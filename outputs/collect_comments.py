"""Parse preserved public search/page captures into traceable comments.
Usage: python outputs/collect_comments.py
Captures are fetched with the chat's public web retrieval tool. This script
parses those snapshots; it does not claim live API access or full pagination.
"""
import csv,datetime,hashlib,json,re,sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parent
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
records=[]; covered=set()
def add(url,text,kind,method,published='',score='',locator=''):
    text=re.sub(r'@\w+[.\w]*','[handle]',text).strip()
    text=re.sub(r'【[^】]*】','',text).strip()
    if not text or text=='SHARED URL':return
    uid=hashlib.sha256((url+'|'+text).encode()).hexdigest()[:20]
    records.append(dict(record_id=uid,platform='Reddit',language='pt/other_unverified',record_type=kind,text_original=text,source_url=url,source_locator=locator,retrieved_at=now,published_display=published,score_display=score,collection_method=method))

capture=(ROOT/'public_comment_search_capture.txt').read_text(encoding='utf-8')
for block in capture.split('--------------------------------------------------------------------------------'):
    u=re.search(r'\((https://www\.reddit\.com/[^\s)]+)\)',block)
    if not u:continue
    url=u.group(1)
    # Keep a focused press-on sample; omit the broader gel-injury thread.
    if '/1qqvlnj/' in url:continue
    entries=list(re.finditer(r'^\s*\[([A-Za-z]+ [A-Za-z]+ \d{1,2} \d{4})\] \[([+-]?\d+) votes?\]\s*$',block,re.M))
    if not entries:continue
    covered.add(re.search(r'/comments/([^/]+)',url).group(1))
    for i,e in enumerate(entries):
        end=entries[i+1].start() if i+1<len(entries) else len(block)
        text=block[e.end():end].strip().replace('SHARED URL','').strip()
        add(url,text,'post' if i==0 else 'comment','public_search_snapshot',e.group(1),e.group(2),'entry-'+str(i))

pages=(ROOT/'public_comment_capture.txt').read_text(encoding='utf-8')
for block in pages.split('--------------------------------------------------------------------------------'):
    u=re.search(r'\((https://www\.reddit\.com/[^\s)]+)\)',block)
    if not u:continue
    url=u.group(1); postid=re.search(r'/comments/([^/]+)',url).group(1)
    if postid in covered:continue
    lines=[]
    for m in re.finditer(r'^L(\d+):\s?(.*)$',block,re.M):lines.append((int(m.group(1)),m.group(2)))
    # Visible comments start at the first commenter after sort choices.
    comment_start=next((i for i,(_,s) in enumerate(lines) if s.strip()=='* Perguntas'),None)
    if comment_start is None:continue
    segment=[]; date=''; start=''
    def flush():
        global segment,date,start
        if segment:add(url,'\n'.join(segment),'comment','public_page_snapshot',date,locator=start)
        segment=[];date='';start=''
    for n,s in lines[comment_start+1:]:
        stripped=s.strip()
        if re.fullmatch(r'【\d+†[^】]+】',stripped) and not any(k in stripped for k in ['há ','Image:','Mais respostas']):
            flush();continue
        if 'há ' in stripped and '【' in stripped:
            date=re.sub(r'【\d+†|】|•','',stripped).strip();continue
        if not stripped or stripped=='•' or 'Image:' in stripped or 'Mais respostas' in stripped or 'Top 1% Commenter' in stripped:continue
        if not start:start='L'+str(n)
        segment.append(stripped)
    flush()

records=list({r['record_id']:r for r in records}.values())
topics={
 '胶水与贴合':['cola','adesiv','bolha','colar','ader'],
 '持久与脱落':['dura','durabilidade','solt','cai','cair','semana'],
 '卸除与复用':['remov','tirar','reutil','reaproveit','resíduo','limpar'],
 '尺寸与曲率':['tamanho','curvatura','pequena','polegar','formato','medição'],
 '外观与自然感':['linda','bonita','naturais','realista','design','perfeit'],
 '购买意向与链接':['compr','link','quero','onde'],
 '教程与测评':['dica','resenha','review','passo','swatch','compara'],
 '舒适与使用反应':['doendo','dolor','confort','alerg','vermelh','estraga']}
for r in records:
    t=r['text_original'].lower();r['topic_tags']=';'.join(k for k,v in topics.items() if any(w in t for w in v))
    # Rule labels target experiences in the text, not the user's overall mood.
    pos=any(w in t for w in ['amei','lind','perfeit','gost','bonita']);neg=any(w in t for w in ['não dura','dificuldade','estraga','doendo','dor','pequena','escorre','não consegui'])
    r['sentiment_rule']='mixed' if pos and neg else 'positive' if pos else 'negative' if neg else 'neutral_or_unclassified'
    r['analysis_method']='keyword_rules_needs_review'
fields=list(records[0])
with (ROOT/'public_comments.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(records)
(ROOT/'public_comments.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
comments=[r for r in records if r['record_type']=='comment']
summary={'records':len(records),'comments':len(comments),'posts':len(records)-len(comments),'threads':len({r['source_url'] for r in records}),'topics':{k:sum(k in r['topic_tags'].split(';') for r in comments) for k in topics},'method':'Visible public snapshots, not full comment pagination. Topics and sentiments are rule based.'}
(ROOT/'comment_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(summary,ensure_ascii=False))
template=(ROOT/'comments_template.html').read_text(encoding='utf-8')
(ROOT/'comments_dashboard.html').write_text(template.replace('/*DATA*/',json.dumps(records,ensure_ascii=False).replace('</','<\\/')).replace('/*SUMMARY*/',json.dumps(summary,ensure_ascii=False)),encoding='utf-8')
if (ROOT/'build_unified.py').exists() and (ROOT/'market_expanded.json').exists():
    import runpy
    runpy.run_path(str(ROOT/'build_unified.py'),run_name='__main__')
