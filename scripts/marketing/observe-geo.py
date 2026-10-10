"""Record an actually observed consumer prompt sample. No automated rankings invented."""
import argparse, datetime as dt, json, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from loop import ROOT, validate_geo
p=argparse.ArgumentParser();p.add_argument('--engine',required=True,choices=['ChatGPT','Claude','Gemini','Perplexity','Copilot']);p.add_argument('--prompt-id',required=True,choices=['discovery','tracking','brand']);p.add_argument('--surface',required=True,choices=['consumer_search','consumer_chat','tracker_consumer_search']);p.add_argument('--date',default=dt.date.today().isoformat());p.add_argument('--mentioned',required=True,choices=['yes','no']);p.add_argument('--cited',required=True,choices=['yes','no']);p.add_argument('--file',type=Path,default=ROOT/'work/geo-observations.json');a=p.parse_args()
data=json.loads(a.file.read_text()) if a.file.exists() else {'samples':[]}
data['samples'].append({'date':a.date,'engine':a.engine,'prompt_id':a.prompt_id,'surface':a.surface,'mentioned':a.mentioned=='yes','cited':a.cited=='yes'})
validate_geo(data,dt.datetime.now(dt.timezone.utc));a.file.parent.mkdir(parents=True,exist_ok=True);a.file.write_text(json.dumps(data,indent=2)+'\n')
print('Recorded actual observation. This is a panel sample, not an overall ranking.')
