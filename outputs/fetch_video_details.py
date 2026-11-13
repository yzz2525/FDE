"""Fetch HTML for already-discovered public videos through the verified local proxy."""
import concurrent.futures,json,re,sys,hashlib
from pathlib import Path
from urllib.request import Request,urlopen,install_opener,build_opener,ProxyHandler
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parent
report=json.loads((ROOT/'latest_public_retry.json').read_text(encoding='utf-8'))
videos=json.loads((ROOT/'retry_social_videos.json').read_text(encoding='utf-8'))
install_opener(build_opener(ProxyHandler({'http':'http://127.0.0.1:10808','https':'http://127.0.0.1:10808'})))
folder=ROOT/'public_retry_runs'/report['run_id']/'video_details';folder.mkdir(exist_ok=True)
def walk(v):
    if isinstance(v,dict):
        yield v
        for x in v.values():yield from walk(x)
    elif isinstance(v,list):
        for x in v:yield from walk(x)
def text(v):return v.get('simpleText','') or ''.join(r.get('text','') for r in v.get('runs',[])) if isinstance(v,dict) else ''
def fetch(v):
    record={'url':v['source_url'],'status':'failed','comments':0}
    try:
        req=Request(v['source_url'],headers={'User-Agent':'Mozilla/5.0','Accept-Language':'pt-BR,pt;q=0.9'})
        with urlopen(req,timeout=12) as res:raw=res.read(6_000_000).decode('utf-8','replace')
        (folder/(hashlib.sha256(v['source_url'].encode()).hexdigest()[:16]+'.html')).write_text(raw,encoding='utf-8')
        records=[]
        for name in ['ytInitialData','ytInitialPlayerResponse']:
            m=re.search(r'(?:var\s+)?'+name+r'\s*=\s*',raw)
            if not m:continue
            try: data=json.JSONDecoder().raw_decode(raw[m.end():])[0]
            except ValueError:continue
            for node in walk(data):
                if 'videoDetails' in node:
                    detail=node['videoDetails'];v['views']=detail.get('viewCount',v.get('views',''));v['duration_seconds']=detail.get('lengthSeconds','')
                if 'playerMicroformatRenderer' in node:
                    v['published_date']=node['playerMicroformatRenderer'].get('publishDate',v['published_date'])
                if 'commentRenderer' in node:
                    c=node['commentRenderer'];body=text(c.get('contentText',{}))
                    if body:records.append({'platform':'YouTube','record_type':'comment','text_original':body,'source_url':v['source_url'],'collection_method':'direct_public_html_vpn_br'})
        record.update(status='html_parsed',comments=len(records))
        v['detail_fetch_status']='html_parsed_comments_'+str(len(records))
        return v,record,records
    except Exception as e:record['error']=type(e).__name__+': '+str(e)[:130];return v,record,[]
logs=[];found=[];updated=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    for v,l,c in pool.map(fetch,videos):updated.append(v);logs.append(l);found.extend(c);print(json.dumps(l,ensure_ascii=False),flush=True)
(ROOT/'retry_social_videos.json').write_text(json.dumps(updated,ensure_ascii=False,indent=2),encoding='utf-8')
(folder/'comment_records.json').write_text(json.dumps(found,ensure_ascii=False,indent=2),encoding='utf-8')
report['video_detail_attempts']=logs;report['new_comments']=len(found)
(ROOT/'latest_public_retry.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'public_retry_runs'/report['run_id']/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('DETAILS '+str(len(logs))+' COMMENTS '+str(len(found)),flush=True)
