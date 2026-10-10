"""Little Days measurement and decision loop. Standard library; no paid AI calls.
Secrets come only from process environment. Reports stay in ignored work/ and artifacts.
"""
from __future__ import annotations
import argparse, datetime as dt, json, math, os, re, urllib.error, urllib.parse, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
BASE = 'https://supermarlon.github.io/little-days-website/'
EVENTS = ('ld_pageview','ld_explore','ld_contact','ld_resource','ld_download')
AI_HOSTS = ('chatgpt.com','chat.openai.com','perplexity.ai','claude.ai','gemini.google.com','copilot.microsoft.com')

def read_json(path, fallback):
    return json.loads(path.read_text()) if path.exists() else fallback

def request_json(url, body=None, headers=None, method=None):
    data=json.dumps(body).encode() if body is not None else None
    req=urllib.request.Request(url,data=data,headers={'Content-Type':'application/json','User-Agent':'LittleDays-MarketingLoop/1.0',**(headers or {})},method=method)
    with urllib.request.urlopen(req,timeout=30) as response:
        return json.load(response)

def safe_error(error):
    # Never include URLs, response bodies, headers or exception strings containing keys.
    if isinstance(error,urllib.error.HTTPError): return 'provider_http_'+str(error.code)
    if isinstance(error,(ValueError,KeyError,TypeError)): return 'invalid_provider_response'
    return 'provider_unavailable'

def number(value):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<0:
        raise ValueError('invalid count')
    return value

def gsc(now):
    token=os.environ.get('GSC_ACCESS_TOKEN')
    refresh=os.environ.get('GSC_REFRESH_TOKEN')
    if not token and refresh:
        credentials={k:os.environ.get(k) for k in ('GSC_CLIENT_ID','GSC_CLIENT_SECRET')}
        if not all(credentials.values()): return {'status':'missing_credentials','metrics':None}
        payload=urllib.parse.urlencode({'client_id':credentials['GSC_CLIENT_ID'],'client_secret':credentials['GSC_CLIENT_SECRET'],'refresh_token':refresh,'grant_type':'refresh_token'}).encode()
        req=urllib.request.Request('https://oauth2.googleapis.com/token',data=payload)
        with urllib.request.urlopen(req,timeout=30) as response:token=json.load(response)['access_token']
    if not token:return {'status':'missing_credentials','metrics':None}
    end=now.date()-dt.timedelta(days=3); start=end-dt.timedelta(days=27)
    url='https://www.googleapis.com/webmasters/v3/sites/'+urllib.parse.quote(BASE,safe='')+'/searchAnalytics/query'
    response=request_json(url,{'startDate':str(start),'endDate':str(end),'dimensions':[],'type':'web','dataState':'final'}, {'Authorization':'Bearer '+token})
    rows=response.get('rows',[])
    if not rows:return {'status':'no_data','metrics':None,'start':str(start),'end':str(end)}
    if len(rows)!=1:raise ValueError('expected property aggregate')
    row=rows[0]
    metrics={k:number(row[k]) for k in ('clicks','impressions','ctr','position')}
    if metrics['ctr']>1:raise ValueError('invalid ctr')
    return {'status':'connected','metrics':metrics,'start':str(start),'end':str(end),'scope':'property aggregate; no search terms or user identifiers'}

def posthog(now):
    key=os.environ.get('POSTHOG_READ_KEY')
    if not key:return {'status':'missing_credentials','metrics':None}
    config=read_json(ROOT/'optimization/settings.json',{})
    project=str(config.get('posthog_project_id','300977'))
    if not re.fullmatch(r'\d+',project):raise ValueError('invalid project')
    end=now.date(); start=end-dt.timedelta(days=28)
    # Both project and website scope are fixed; only allowlisted counts are retrieved.
    event_list=','.join("'"+x+"'" for x in EVENTS)
    query=f"SELECT event, count() FROM events WHERE timestamp >= toDateTime('{start}') AND timestamp < toDateTime('{end}') AND properties.site = 'little-days-marketing' AND event IN ({event_list}) GROUP BY event"
    response=request_json(f'https://eu.posthog.com/api/projects/{project}/query/',{'query':{'kind':'HogQLQuery','query':query}},{'Authorization':'Bearer '+key})
    rows=response.get('results')
    if not isinstance(rows,list):raise ValueError('missing results')
    counts={e:0 for e in EVENTS}
    for row in rows:
        if not isinstance(row,list) or len(row)!=2 or row[0] not in counts:raise ValueError('unexpected row')
        counts[row[0]]=number(row[1])
    return {'status':'connected','metrics':counts,'start':str(start),'end':str(end),'scope':'consenting traffic only; event counts, not unique people or sessions'}

def validate_geo(raw, now):
    samples=raw.get('samples',[])
    if not isinstance(samples,list):raise ValueError('samples must be a list')
    clean=[]
    for sample in samples:
        if sample.get('surface') not in ('consumer_search','consumer_chat','tracker_consumer_search'):
            raise ValueError('API probes cannot be consumer ranking samples')
        engine=sample.get('engine');prompt_id=sample.get('prompt_id')
        if engine not in ('ChatGPT','Claude','Gemini','Perplexity','Copilot'):raise ValueError('unknown engine')
        if prompt_id not in ('discovery','tracking','brand'):raise ValueError('unknown prompt')
        date=dt.date.fromisoformat(sample['date'])
        if date>now.date():raise ValueError('future observation')
        if not isinstance(sample.get('mentioned'),bool) or not isinstance(sample.get('cited'),bool):raise ValueError('binary observation required')
        clean.append({k:sample[k] for k in ('date','engine','prompt_id','surface','mentioned','cited')})
    recent=[s for s in clean if (now.date()-dt.date.fromisoformat(s['date'])).days<=28]
    if not recent:return {'status':'no_data' if not clean else 'stale','metrics':None}
    # Descriptive rate of this specific prompt panel; never call it a market share or ranking.
    return {'status':'connected','metrics':{'samples':len(recent),'mentions':sum(s['mentioned'] for s in recent),'citations':sum(s['cited'] for s in recent)},'scope':'observed prompt panel only; not representative of overall rankings'}

def browser_snapshot(source_name, now):
    """Optional local fallback from a actually read provider UI; never committed."""
    raw=read_json(ROOT/'work/provider-snapshots.json',{})
    entry=raw.get(source_name)
    if not entry:return None
    stamp=dt.datetime.fromisoformat(entry['observed_at'])
    if stamp.tzinfo is None or stamp>now or (now-stamp).total_seconds()>86400:
        return {'status':'stale','metrics':None}
    if entry.get('status')=='processing':return {'status':'processing','metrics':None,'scope':'provider UI; no data available yet'}
    expected=('clicks','impressions','ctr','position') if source_name=='search_console' else EVENTS
    metrics={k:number(entry['metrics'][k]) for k in expected}
    if source_name=='search_console' and metrics['ctr']>1:raise ValueError('invalid ctr')
    start=dt.date.fromisoformat(entry['start']);end=dt.date.fromisoformat(entry['end'])
    if end>now.date() or end<start:raise ValueError('invalid dates')
    return {'status':'connected','metrics':metrics,'start':str(start),'end':str(end),'scope':'actual provider UI snapshot; no raw queries, people or sessions'}

def collect(now, geo_file):
    sources={}
    for name,func in (('search_console',gsc),('analytics',posthog)):
        try:
            sources[name]=func(now)
            if sources[name]['status']=='missing_credentials':
                sources[name]=browser_snapshot(name,now) or sources[name]
        except Exception as e:sources[name]={'status':'error','error':safe_error(e),'metrics':None}
    try:sources['geo']=validate_geo(read_json(geo_file,{'samples':[]}),now)
    except Exception as e:sources['geo']={'status':'error','error':safe_error(e),'metrics':None}
    return {'observed_at':now.isoformat(),'sources':sources}

def evaluate(experiment, observation, now):
    if experiment.get('status')!='running':return {'id':experiment['id'],'decision':'not_running'}
    if not experiment.get('started_at') or not experiment.get('baseline'):
        return {'id':experiment['id'],'decision':'blocked_missing_baseline'}
    started=dt.date.fromisoformat(experiment['started_at'])
    if (now.date()-started).days<max(28,experiment.get('minimum_window_days',28)):
        return {'id':experiment['id'],'decision':'observe'}
    source=observation['sources']['analytics']
    if source['status']!='connected':return {'id':experiment['id'],'decision':'blocked_missing_measurement'}
    current=source['metrics']; baseline=experiment['baseline']
    views=number(current.get('ld_pageview',0)); old_views=number(baseline.get('ld_pageview',0))
    if min(views,old_views)<100:return {'id':experiment['id'],'decision':'insufficient_sample'}
    contacts=number(current.get('ld_contact',0)); old_contacts=number(baseline.get('ld_contact',0))
    if min(contacts,old_contacts)<10:return {'id':experiment['id'],'decision':'insufficient_sample'}
    # Rolling aggregates are observational. Never auto-declare causal improvement or auto-revert.
    return {'id':experiment['id'],'decision':'review_due','baseline_contact_events_per_pageview':old_contacts/old_views,'current_contact_events_per_pageview':contacts/views,'limitation':'Consent-selected event ratio; pre/post comparison is not causal and can include repeat clicks.'}

def plan(observation, experiments, now):
    sources=observation['sources']; decisions=[evaluate(e,observation,now) for e in experiments['experiments']]
    blockers=[name+': '+s['status'] for name,s in sources.items() if s['status']!='connected']
    running=[e for e in experiments['experiments'] if e.get('status')=='running']
    if any(s['status']=='error' for s in sources.values()):action='repair_measurement'
    elif blockers:action='establish_baseline'
    elif running:action='evaluate_existing_experiment' if any(d['decision']=='review_due' for d in decisions) else 'observe_existing_experiment'
    else:action='propose_one_experiment'
    return {'next_action':action,'blockers':blockers,'experiment_decisions':decisions,'automatic_external_posts':False,'website_change_limit':1,'observed_at':now.isoformat()}

def run(output, geo_file, now=None):
    now=now or dt.datetime.now(dt.timezone.utc)
    output.mkdir(parents=True,exist_ok=True)
    observation=collect(now,geo_file)
    experiments=read_json(ROOT/'optimization/experiments.json',{'experiments':[]})
    decision=plan(observation,experiments,now)
    history=read_json(output/'history.json',[])
    # Idempotent per UTC observation date; reruns replace, not inflate evidence.
    day=now.date().isoformat()
    history=[v for v in history if v['observed_at'][:10]!=day]
    history.append(observation); history=history[-90:]
    for name,value in (('observation.json',observation),('decision.json',decision),('history.json',history)):
        (output/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
    report='# Little Days · Marketing Loop\n\nStand: '+day+' (UTC)\n\n'
    report+='| Messquelle | Tatsächlicher Status |\n|---|---|\n'
    report+=''.join('| '+name+' | '+s['status']+' |\n' for name,s in observation['sources'].items())
    report+='\nNächster Schritt: **'+decision['next_action']+'**\n\n'
    report+='Fehlende Daten sind keine Nullwerte. Kein Experiment wird ohne Baseline zum Gewinner erklärt.\n\n'
    report+='Website: höchstens eine begründete Änderung. Externe Posts und Outreach: nur vorbereitete Entwürfe, keine automatische Aussendung.\n'
    (output/'report.md').write_text(report)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'],'a') as file:file.write(report)
    print('Loop report saved. Next action:',decision['next_action'])
    if any(s['status']=='error' for s in observation['sources'].values()):raise SystemExit(1)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ROOT/'work/marketing');parser.add_argument('--geo-file',type=Path,default=ROOT/'work/geo-observations.json');args=parser.parse_args();run(args.output,args.geo_file)
