"""Retest public channels through the machine's current network, preserving runs."""
import concurrent.futures,datetime,hashlib,json,re,sys,argparse
from pathlib import Path
from urllib.request import Request,urlopen,install_opener,build_opener,ProxyHandler
from urllib.error import HTTPError
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parent
STAMP=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
RUN=ROOT/'public_retry_runs'/STAMP
TARGETS=[
 ('Mercado Livre','https://lista.mercadolivre.com.br/unhas-posticas'),
 ('Mercado Livre API','https://api.mercadolibre.com/sites/MLB/search?q=unhas%20posticas&limit=10'),
 ('Shopee BR','https://shopee.com.br/search?keyword=unhas%20posti%C3%A7as'),
 ('Amazon BR','https://www.amazon.com.br/s?k=unhas+posticas'),
 ('TikTok','https://www.tiktok.com/tag/unhasposticas'),
 ('TikTok Creative Center','https://ads.tiktok.com/business/creativecenter/pc/en'),
 ('Instagram','https://www.instagram.com/explore/tags/unhasposticas/'),
 ('YouTube','https://www.youtube.com/results?search_query=unhas+posticas+brasil')]
def probe(target):
    channel,url=target
    rec={'platform':channel,'url':url,'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'request_error','new_products':0,'new_comments':0}
    try:
        req=Request(url,headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36','Accept-Language':'pt-BR,pt;q=0.9'})
        with urlopen(req,timeout=18) as res:
            raw=res.read(6_000_000).decode('utf-8','replace')
            rec.update(http_status=res.status,final_url=res.url)
        name=hashlib.sha256(url.encode()).hexdigest()[:16]+'.html'
        (RUN/name).write_text(raw,encoding='utf-8')
        rec['raw_file']=str(RUN/name)
        title=re.search('<title[^>]*>(.*?)</title>',raw,re.S|re.I)
        rec['page_title']=re.sub(r'\s+',' ',title.group(1)).strip() if title else ''
        rec['html_bytes']=len(raw.encode())
        rec['product_schema_markers']=len(re.findall(r'"@type"\s*:\s*"Product"',raw))
        rec['video_schema_markers']=len(re.findall(r'"@type"\s*:\s*"VideoObject"',raw))
        final=rec['final_url'].lower()
        if any(s in final for s in ['verify/traffic','captcha','challenge']):rec['status']='traffic_verification'
        elif any(s in final for s in ['/login','/signin','/accounts/login','/gz/account-verification']):rec['status']='login_required'
        elif 'captcha' in rec['page_title'].lower() or 'robot check' in rec['page_title'].lower():rec['status']='challenge_page'
        else:rec['status']='html_received_needs_platform_parser'
    except HTTPError as e:rec.update(http_status=e.code,status='http_error',error=str(e))
    except Exception as e:rec['error']=type(e).__name__+': '+str(e)[:180]
    print(json.dumps({k:v for k,v in rec.items() if k in ['platform','status','http_status','final_url','page_title','error']},ensure_ascii=False),flush=True)
    return rec
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--proxy',default='');args=parser.parse_args()
    if args.proxy:
        install_opener(build_opener(ProxyHandler({'http':args.proxy,'https':args.proxy})))
    RUN.mkdir(parents=True,exist_ok=False)
    network={'country_code':None,'country':None,'verified':False}
    # Store country only, never the user's public IP.
    try:
        with urlopen('https://www.cloudflare.com/cdn-cgi/trace',timeout=12) as res: trace=res.read().decode()
        loc=re.search(r'^loc=([A-Z]+)$',trace,re.M)
        network.update(country_code=loc.group(1) if loc else None,verified=bool(loc),route='explicit_local_proxy' if args.proxy else 'system_default')
    except Exception as e:network['error']=type(e).__name__
    print('NETWORK_COUNTRY '+json.dumps(network,ensure_ascii=False),flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool: records=list(pool.map(probe,TARGETS))
    report={'run_id':STAMP,'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'network':network,'records':records,'browser_evidence':[{'platform':'Shopee BR','status':'traffic_verification','observed_final_path':'shopee.com.br/verify/traffic/error','method':'local Edge browser observed URL'}],'new_products':0,'new_comments':0,'note':'HTTP200 or HTML received is not proof of data extraction. No CAPTCHA solved or session credentials exported.'}
    (RUN/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'latest_public_retry.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('SAVED '+str(RUN/'report.json'),flush=True)
if __name__=='__main__':main()
