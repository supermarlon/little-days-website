"""Daily technical observation; no paid services and no invented traffic data."""
import json, subprocess, urllib.request, hashlib, datetime, os
from pathlib import Path
root=Path(__file__).resolve().parents[1]
subprocess.run(['python3', str(root/'scripts/check.py')],check=True)
base='https://supermarlon.github.io/little-days-website/'
results=[]
for path in ('', 'assets/style.css', 'assets/analytics.js', 'assets/social.png', 'sitemap.xml', 'robots.txt', 'impressum.html', 'datenschutz.html'):
    try:
        req=urllib.request.Request(base+path,headers={'User-Agent':'LittleDays-QualityAudit/1.0'})
        with urllib.request.urlopen(req, timeout=20) as response:
            body=response.read(); results.append({'path':path or '/', 'status':response.status, 'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest()})
    except Exception as e: results.append({'path':path or '/', 'error':str(e)})
metrics=json.loads((root/'optimization/data/metrics.json').read_text())
report={'observed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'technical':results,'measurement_connected':{k:metrics.get(k) is not None for k in ('search_console','analytics','geo')},'next_step':'Connect aggregate measurements; evaluate one hypothesis over at least 28 days. Do not interpret missing data as zero.'}
(root/'work').mkdir(exist_ok=True)
(root/'work/daily-report.json').write_text(json.dumps(report,indent=2))
summary='## Little Days daily audit\n\n'+ '\n'.join('- '+str(v) for v in results)+'\n\n'+report['next_step']+'\n'
(root/'work/daily-report.md').write_text(summary)
if os.environ.get('GITHUB_STEP_SUMMARY'):
    with open(os.environ['GITHUB_STEP_SUMMARY'],'a') as f:f.write(summary)
if any('error' in v or v.get('status')!=200 for v in results): raise SystemExit('Live site audit failed')
