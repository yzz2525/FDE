"""Public page collector and reproducible dashboard. Python 3.10+, no dependencies.
Run: python crawl_market.py --crawl (network) or --report-only (saved evidence).
"""
import argparse, concurrent.futures, csv, datetime, hashlib, html, json, re
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urlparse
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parent
class StructuredHTML(HTMLParser):
    def __init__(self):
        super().__init__(); self.capture=False; self.parts=[]; self.blocks=[]; self.text=[]
    def handle_starttag(self, tag, attrs):
        if tag=='script' and dict(attrs).get('type')=='application/ld+json':
            self.capture=True; self.parts=[]
    def handle_data(self, data):
        if self.capture: self.parts.append(data)
        else: self.text.append(data)
    def handle_endtag(self, tag):
        if tag=='script' and self.capture:
            self.capture=False
            try: self.blocks.append(json.loads(''.join(self.parts)))
            except ValueError: pass

def walk(obj):
    if isinstance(obj,dict):
        yield obj
        for v in obj.values(): yield from walk(v)
    elif isinstance(obj,list):
        for v in obj: yield from walk(v)

def read_csv(name):
    p=ROOT/name
    if not p.exists(): return []
    with p.open(encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f))

def number(v):
    try: return float(str(v).strip())
    except (ValueError,TypeError): return None

def collect(url):
    stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
    record={'url':url,'attempted_at':stamp,'status':'error','products':0}
    found=[]
    try:
        req=Request(url,headers={'User-Agent':'NailTrendResearchDemo/0.1','Accept-Language':'pt-BR,pt;q=0.9'})
        with urlopen(req,timeout=12) as response:
            raw=response.read(4_000_000).decode('utf-8','replace')
        cache=ROOT/'crawl_raw'; cache.mkdir(exist_ok=True)
        (cache/(hashlib.sha256(url.encode()).hexdigest()[:16]+'.html')).write_text(raw,encoding='utf-8')
        doc=StructuredHTML(); doc.feed(raw)
        for node in walk(doc.blocks):
            kinds=node.get('@type',[])
            if isinstance(kinds,str): kinds=[kinds]
            if 'Product' not in kinds: continue
            offers=node.get('offers',{})
            if isinstance(offers,list): offers=offers[0] if offers else {}
            rating=node.get('aggregateRating',{})
            if number(offers.get('price',offers.get('lowPrice'))) is None: continue
            found.append({'platform':platform(url),'title':node.get('name',''),'price_brl':offers.get('price',offers.get('lowPrice')),'rating':rating.get('ratingValue',''),'source_url':node.get('url',url),'evidence_method':'direct_jsonld','snapshot_at':stamp})
        record.update(status='ok' if found else 'no_structured_products',products=len(found))
    except HTTPError as e: record.update(status='http_error',error=str(e.code))
    except Exception as e: record.update(error=type(e).__name__+': '+str(e)[:160])
    return found,record

def platform(url):
    host=urlparse(url).netloc
    return next((v for k,v in [('mercadolivre','Mercado Livre'),('shopee','Shopee BR'),('amazon','Amazon BR'),('tiktok','TikTok'),('instagram','Instagram'),('youtube','YouTube')] if k in host),host)

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--crawl',action='store_true'); parser.add_argument('--report-only',action='store_true'); args=parser.parse_args()
    rows=[]
    for filename in ['marketplace_products_sample.csv','additional_products.csv']:
        for r in read_csv(filename):
            r.update(evidence_method='search_index_sample',snapshot_at='',retrieved_date='2026-11-06')
            rows.append(r)
    for r in read_csv('mercadolivre_review_summary_sample.csv'):
        rows.append({'platform':'Mercado Livre','title':r['title'],'price_brl':r['price_brl'],'rating':r['rating'],'source_url':r['source_url'],'evidence_method':'search_index_detail','sold_signal':r['sold_signal'],'review_count':r['review_count'],'snapshot_at':''})
    log=[]
    if args.crawl:
        urls=sorted({r['source_url'] for r in rows})+['https://www.amazon.com.br/s?k=unhas+posticas','https://www.tiktok.com/tag/unhasposticas','https://www.instagram.com/explore/tags/unhasposticas/']
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            for found,status in pool.map(collect,urls):
                rows.extend(found); log.append(status); print(status['status'],status['url'],flush=True)
        (ROOT/'crawl_log.json').write_text(json.dumps(log,ensure_ascii=False,indent=2),encoding='utf-8')
    elif (ROOT/'crawl_log.json').exists(): log=json.loads((ROOT/'crawl_log.json').read_text(encoding='utf-8'))
    unique={}
    for r in rows:
        r['price_brl']=number(r.get('price_brl')); r['rating']=number(r.get('rating'))
        if not r['title'].strip() or r['price_brl'] is None: continue
        key=(r['platform'],re.sub(r'\W+','',r['title'].casefold()),r['price_brl'])
        unique[key]=r
    rows=list(unique.values())
    fields=sorted(set().union(*(r.keys() for r in rows)))
    with (ROOT/'market_expanded.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields); writer.writeheader(); writer.writerows(rows)
    payload={'products':rows,'reviews':read_csv('mercadolivre_review_summary_sample.csv'),'social':read_csv('social_content_sample.csv'),'log':log}
    (ROOT/'market_expanded.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    template=(ROOT/'dashboard_template.html').read_text(encoding='utf-8')
    page=template.replace('/*DATA*/',json.dumps(payload,ensure_ascii=False).replace('</','<\\/'))
    if (ROOT/'comments_dashboard.html').exists():
        page=page.replace('<main>','<main><p><a href="comments_dashboard.html">查看真实社媒评论与主题分析 →</a></p>',1)
    (ROOT/'market_dashboard.html').write_text(page,encoding='utf-8')
    print(json.dumps({'products':len(rows),'attempts':len(log),'dashboard':str(ROOT/'market_dashboard.html')},ensure_ascii=False))
    if (ROOT/'build_unified.py').exists() and (ROOT/'public_comments.json').exists():
        import runpy
        runpy.run_path(str(ROOT/'build_unified.py'),run_name='__main__')

if __name__=='__main__': main()
