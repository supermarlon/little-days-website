"""Dependency-free release checks for local links, semantic HTML and SEO consistency."""
import json, re, sys
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
BASE = 'https://supermarlon.github.io/little-days-website/'
class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.ids=set(); self.links=[]; self.h1=0; self.ld=[]; self.capture=False; self.buffer=''; self.meta={}; self.canonical=None; self.images=[]
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if 'id' in a:
            assert a['id'] not in self.ids, 'Duplicate ID'
            self.ids.add(a['id'])
        if tag=='h1': self.h1+=1
        for key in ('href','src'):
            if key in a: self.links.append(a[key])
        if tag=='meta': self.meta[a.get('name',a.get('property',''))]=a.get('content','')
        if tag=='link' and a.get('rel')=='canonical': self.canonical=a['href']
        if tag=='img': self.images.append(a)
        if tag=='script' and a.get('type')=='application/ld+json': self.capture=True; self.buffer=''
    def handle_data(self,text):
        if self.capture: self.buffer+=text
    def handle_endtag(self,tag):
        if tag=='script' and self.capture: self.ld.append(json.loads(self.buffer)); self.capture=False
pages={f.name:Page(f.read_text()) for f in SITE.glob('*.html')}
for name,p in pages.items():
    assert p.h1==1, name+': expected one h1'
    assert p.meta.get('viewport'), name+': missing viewport'
    assert all('alt' in a for a in p.images), name+': missing alt'
    for link in p.links:
        u=urlsplit(link)
        if u.scheme or u.netloc: continue
        path=unquote(u.path) or name
        if path in ('.','./'): path='index.html'
        target=SITE/path
        assert target.is_file(), name+': broken link '+link
        if u.fragment and target.suffix=='.html':
            assert u.fragment in pages[target.name].ids, name+': missing anchor '+link
p=pages['index.html']
assert p.canonical==BASE
assert p.meta['og:url']==BASE
assert p.meta['og:image']==BASE+'assets/social.png'
assert (SITE/'assets/social.png').is_file(), 'Missing social image'
assert p.meta.get('description') and p.meta.get('twitter:card')
assert p.ld[0]['@graph'][0]['url']==BASE
html=(SITE/'index.html').read_text()
for q in p.ld[0]['@graph'][1]['mainEntity']:
    assert q['name'] in html and q['acceptedAnswer']['text'] in html, 'FAQ drift'
sitemap_urls=[v.text for v in ET.parse(SITE/'sitemap.xml').findall('.//{*}loc')]
assert sitemap_urls[0]==BASE
for url in sitemap_urls:
    assert url.startswith(BASE), 'Off-site sitemap entry'
    page=pages[url[len(BASE):] or 'index.html']
    assert page.canonical==url and 'noindex' not in page.meta.get('robots',''), 'Sitemap/canonical mismatch'
assert 'Sitemap: '+BASE+'sitemap.xml' in (SITE/'robots.txt').read_text()
assert sum(f.stat().st_size for f in SITE.rglob('*') if f.is_file()) < 400_000, 'Page payload budget'
print('PASS: local links, anchors, metadata, structured FAQ, sitemap and payload budget')
