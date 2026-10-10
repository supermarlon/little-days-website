"""Notify participating engines only after a successful deployment of changed pages."""
import argparse,json,re,subprocess,sys,urllib.error,urllib.request,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CONFIG=json.loads((ROOT/'optimization/settings.json').read_text())
BASE=CONFIG['site_url']
def changed_urls(before=None):
 urls=[v.text for v in ET.parse(ROOT/'site/sitemap.xml').findall('.//{*}loc')]
 if before and re.fullmatch(r'[a-f0-9]{40}',before) and before!='0'*40:
  proc=subprocess.run(['git','diff','--name-only',before,'HEAD','--','site/'],cwd=ROOT,capture_output=True,text=True,check=True)
  files=proc.stdout.splitlines();paths={'site/index.html':BASE}
  paths.update({'site/'+url[len(BASE):]:url for url in urls if url!=BASE})
  # Global CSS/analytics changes do not require notifying engines about unchanged text.
  urls=[paths[file] for file in files if file in paths]
 if not all(url.startswith(BASE) for url in urls):raise ValueError('Off-site URL in sitemap')
 return urls[:20]
def submit(urls):
 if not urls:print('IndexNow: no changed indexable pages.');return
 key_file=CONFIG['indexnow_key_file'];key=(ROOT/'site'/key_file).read_text().strip()
 with urllib.request.urlopen(BASE+key_file,timeout=20) as response:
  if response.read().decode().strip()!=key:raise ValueError('Live ownership proof does not match')
 body={'host':'supermarlon.github.io','key':key,'keyLocation':BASE+key_file,'urlList':urls}
 req=urllib.request.Request('https://api.indexnow.org/indexnow',data=json.dumps(body).encode(),headers={'Content-Type':'application/json; charset=utf-8'},method='POST')
 try:
  with urllib.request.urlopen(req,timeout=30) as response:code=response.status
 except urllib.error.HTTPError as error:
  print('IndexNow: submission failed with HTTP',error.code);sys.exit(1)
 print('IndexNow:',code,'—',len(urls),'URLs received; indexing is not confirmed.')
 if code not in (200,202):raise SystemExit(1)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--before');p.add_argument('--dry-run',action='store_true');a=p.parse_args();urls=changed_urls(a.before)
 if a.dry_run:print(json.dumps({'urlList':urls},indent=2))
 else:submit(urls)
