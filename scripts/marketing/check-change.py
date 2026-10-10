"""Daily agent change boundary. Infrastructure setup is performed separately by the owner task."""
import argparse,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--base',default='origin/main');args=p.parse_args()
r=subprocess.run(['git','diff','--name-only',args.base,'--'],cwd=ROOT,check=True,text=True,capture_output=True)
files=r.stdout.splitlines()
allow={'optimization/experiments.json','optimization/distribution/opportunities.json','optimization/distribution/drafts.md','optimization/distribution/research.md'}
for name in files:
 if name in allow or name.startswith('optimization/distribution/drafts/'):continue
 if re.fullmatch(r'site/(index|ressourcen|baby-tagebuch|betreuungsuebergabe|presse)\.html',name):continue
 raise SystemExit('Daily agent change outside allowed scope: '+name)
patch=subprocess.run(['git','diff',args.base,'--','site/'],cwd=ROOT,check=True,text=True,capture_output=True).stdout
for forbidden in ('google-site-verification','phc_','data-consent','statistics-status','application/ld+json','marlon@supermarlon.de'):
 if any(forbidden in line for line in patch.splitlines() if line.startswith(('+','-')) and not line.startswith(('+++','---'))):
  raise SystemExit('Protected markup changed; use a focused patch that preserves: '+forbidden)
# Whole-line HTML replacement can make unrelated protected changes appear. Format content before daily edits.
print('Daily scope guard passed; factual review is still required.')
