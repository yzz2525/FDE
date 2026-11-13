"""Extract public video metadata from captured YouTube HTML without credentials."""
import json,re,sys,datetime
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parent
report=json.loads((ROOT/'latest_public_retry.json').read_text(encoding='utf-8'))
def walk(v):
    if isinstance(v,dict):
        yield v
        for x in v.values():yield from walk(x)
    elif isinstance(v,list):
        for x in v:yield from walk(x)
def text(v):
    if not isinstance(v,dict):return ''
    return v.get('simpleText','') or ''.join(r.get('text','') for r in v.get('runs',[]))
def count(display):
    m=re.search(r'[\d.,]+',display)
    if not m:return ''
    n=m.group(0)
    # Full counts only: don't turn rounded K/M displays into precise totals.
    if re.search(r'\d\s*(K|M|mil|mi|thousand|million)\b',display,re.I):return ''
    return int(re.sub(r'\D','',n))
videos=[]
for r in report['records']:
    if r['platform']!='YouTube' or not r.get('raw_file'):continue
    raw=Path(r['raw_file']).read_text(encoding='utf-8')
    start=re.search(r'(?:var\s+)?ytInitialData\s*=\s*',raw)
    if not start:continue
    try:data=json.JSONDecoder().raw_decode(raw[start.end():])[0]
    except ValueError:continue
    for node in walk(data):
        item=node.get('videoRenderer')
        if not item or not item.get('videoId'):continue
        title=text(item.get('title',{}))
        view_display=text(item.get('viewCountText',{}))
        videos.append({'observed_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).date().isoformat(),'platform':'YouTube','content_type':'video','title_or_excerpt':title,'author':text(item.get('ownerText',{})),'published_date':text(item.get('publishedTimeText',{})),'views':count(view_display),'views_display':view_display,'likes':'','followers':'','topic_tags':'unhas postiças;Brazil query;needs language review','source_url':'https://www.youtube.com/watch?v='+item['videoId'],'data_status':'public_page_brazil_query','region_evidence':'来自巴西穿戴甲关键词搜索，创作者和观众地区未核验','duration_display':text(item.get('lengthText',{})),'retrieved_at':report['checked_at'],'collection_method':'direct_public_html_vpn_br'})
videos=list({v['source_url']:v for v in videos}.values())
report['new_social_videos']=len(videos)
(ROOT/'latest_public_retry.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'retry_social_videos.json').write_text(json.dumps(videos,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'videos':len(videos),'examples':[{k:v[k] for k in ['title_or_excerpt','views_display','source_url']} for v in videos[:4]]},ensure_ascii=False))
