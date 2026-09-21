from pathlib import Path
from urllib.request import Request, urlopen
import json, re, shutil, time
ROOT=Path(__file__).resolve().parent
RESOURCES=[]
for p in sorted((ROOT/'bootstrap-resources').glob('*.txt')):
    for line in p.read_text().splitlines():
        if line.strip(): RESOURCES.append(tuple(line.split('\t',1)))
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/153 Safari/537.36'

def download(url,target):
    path=ROOT/target; path.parent.mkdir(parents=True,exist_ok=True); last=None
    for n in range(4):
        try:
            headers={'User-Agent':UA,'Accept':'*/*'}
            if n % 2 == 0: headers['Referer']='https://www.tandjungsarihotel.com/'
            req=Request(url,headers=headers)
            with urlopen(req,timeout=90) as r: data=r.read()
            if not data and path.suffix.lower()!='.bin': raise RuntimeError('empty response')
            path.write_bytes(data); print('downloaded',target,len(data)); return
        except Exception as e:
            last=e; print('retry',n+1,url,e); time.sleep(2+n*2)
    raise RuntimeError(f'failed {url}: {last}')

seen=set()
for url,rel in RESOURCES:
    if rel not in seen: seen.add(rel); download(url,rel)
url_map={u:'/'+r.replace('\\','/') for u,r in RESOURCES}
index=ROOT/'index.html'; html=index.read_text('utf-8',errors='ignore')
for url,rel in sorted(RESOURCES,key=lambda x:len(x[0]),reverse=True):
    if url=='https://www.tandjungsarihotel.com/': continue
    local='/'+rel.replace('\\','/'); html=html.replace(url,local).replace(url.replace('&','&amp;'),local.replace('&','&amp;'))
html=re.sub(r'\s*<link[^>]+href=["\']https://www\.googletagmanager\.com/gtm\.js[^>]*>','',html,flags=re.I)
csp='<meta http-equiv="Content-Security-Policy" content="default-src \'self\' data: blob:; script-src \'self\' \'unsafe-inline\'; style-src \'self\' \'unsafe-inline\'; img-src \'self\' data: blob:; media-src \'self\' data: blob:; font-src \'self\' data:; connect-src \'self\'; frame-src \'self\'; object-src \'none\'; worker-src \'self\' blob:; base-uri \'self\'; form-action \'self\'">'
if 'Content-Security-Policy' not in html: html=html.replace('<head>','<head>'+csp,1)
def kill_href(m):
    q,u=m.group(1),m.group(2); return f'href={q}#{q} data-external-disabled={q}true{q} data-original-href={q}{u}{q}'
html=re.sub(r'href=(["\'])(https?://[^"\']+)\1',kill_href,html,flags=re.I)
if '/__sitecloner/runtime.js' not in html: html=html.replace('</head>','<script src="/__sitecloner/runtime.js"></script></head>',1)
index.write_text(html,'utf-8')
site=ROOT/'__sitecloner'; site.mkdir(exist_ok=True)
site.joinpath('runtime.js').write_text('const M='+json.dumps(url_map,separators=(',',':'))+';\n'+(ROOT/'bootstrap-runtime.template.js').read_text())
site.joinpath('blank.js').write_text('/* external scripts disabled */\n')
site.joinpath('blocked.json').write_text('{"offline":true,"externalNetwork":false}\n')
site.joinpath('placeholder.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1" viewBox="0 0 1 1"></svg>\n')
fallback='/__external__/vold-independent.s3.ap-southeast-1.amazonaws.com/our-story/0172d8b4-b73d-4b7a-bac1-7a848c8e04a6/raw/lobby-editwebp.webp'
for p in (ROOT/'_nuxt').glob('*.js'):
    s=p.read_text('utf-8',errors='ignore').replace('https://www.googletagmanager.com/gtm.js','/__sitecloner/blank.js').replace('https://picsum.photos/600/300',fallback); p.write_text(s)
icon=ROOT/'web-app-manifest-192x192.png'
if icon.exists(): shutil.copyfile(icon,ROOT/'favicon-96x96.png'); shutil.copyfile(icon,ROOT/'apple-touch-icon.png')
(ROOT/'vercel.json').write_text(json.dumps({'cleanUrls':True,'trailingSlash':False,'headers':[{'source':'/(.*)','headers':[{'key':'X-Content-Type-Options','value':'nosniff'},{'key':'Referrer-Policy','value':'no-referrer'},{'key':'X-Frame-Options','value':'SAMEORIGIN'}]}]},indent=2)+'\n')
(ROOT/'.gitignore').write_text('.DS_Store\nThumbs.db\n.vercel\n')
(ROOT/'.vercelignore').write_text('.github\nbootstrap_localize.py\nbootstrap-runtime.template.js\nbootstrap-resources\n')
(ROOT/'README.md').write_text('# Tandjung Sari localized build\n\nSelf contained static capture. All captured assets, fonts, app chunks, media, API responses and the linked hotel book are served from this repository. Automatic external requests and outbound HTTP navigation are disabled.\n')
remote=re.findall(r'<(?:script|img|source|video|audio|iframe|link)[^>]+(?:src|href)=["\']https?://',index.read_text(errors='ignore'),flags=re.I)
if remote: raise RuntimeError(f'remote automatic resources remain: {len(remote)}')
print('localized build complete')
