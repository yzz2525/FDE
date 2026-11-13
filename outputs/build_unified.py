"""Combine existing public datasets into one offline dashboard. No Excel input."""
import json,sys,re
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
root=Path(__file__).resolve().parent
def read(name):return json.loads((root/name).read_text(encoding='utf-8'))
data=read('market_expanded.json');data['comments']=read('public_comments.json');data['comment_summary']=read('comment_summary.json')
data['opportunities']=[
 dict(priority='P1',name='搜索需求与季节性',question='用户正在搜什么？哪些款式有增长或季节窗口？',fields='unhas postiças / unhas autocolantes / press on nails；BR地区；相对热度、相关词、州级分布',access='公开：Google Trends CSV导出',limit='相对指数不等于绝对搜索量；同批次和时间范围比较。本轮未取数。',url='https://support.google.com/trends/answer/4365538?hl=en'),
 dict(priority='P1',name='广告素材与卖点',question='竞品在推什么款式、价格和使用场景？',fields='品牌、素材、文案、落地页、投放起始日（以页面可见为准）',access='公开：Meta广告资料库',limit='普通商业广告通常不能据此取得真实花费、ROAS或销量。本轮未取数。',url='https://www.facebook.com/ads/library/'),
 dict(priority='P1',name='TikTok广告与内容创意',question='哪些素材结构和产品卖点值得测试？',fields='地区、行业、广告素材、文案；可见互动与相对表现指标',access='公开：TikTok Creative Center Top Ads',limit='按可见筛选项选择巴西；精选广告非全量市场，部分详情可能需登录。本轮未取数。',url='https://ads-useast2a.tiktok.com/resources/help/article/how-to-use-the-top-ads-dashboard'),
 dict(priority='P1',name='价格、促销与套装配置',question='消费者到手价如何比较？低价是单套还是批发？',fields='原价、活动价、优惠条件、片数、套数、胶贴/胶水/工具；折算每套价格',access='公开：商品详情与列表快照',limit='已有部分价格/优惠，规格归一和优惠条件待补；不能把24片与100片散片直接比较。',url='https://lista.mercadolivre.com.br/unhas-posticas'),
 dict(priority='P1',name='配送成本与承诺时效',question='销量差距是否由配送和包邮门槛造成？',fields='运费、包邮门槛、本地/跨境、承诺到达日期',access='公开：商品页面，固定巴西邮编询价',limit='必须固定邮编与采集时间；当前未系统采集。',url='https://www.mercadolivre.com.br/'),
 dict(priority='P2',name='竞品上新与供给变化',question='哪种甲型、颜色和设计正在被更多卖家采用？',fields='首次发现时间、商品ID、卖家ID、款式、图片、在售状态、可见销量区间',access='公开：按日/周保存商品快照',limit='首次发现日不等于上架日，缺货不一定等于售罄；当前没有连续快照。',url='https://developers.mercadolivre.com.br/pt_br/itens-e-buscas'),
 dict(priority='P2',name='葡语评论与售前问题',question='用户为什么买、为什么退、还缺少什么功能？',fields='原文、话题、购买意向、尺寸/胶水/持久度/复用；评论时间与可见互动',access='公开：Reddit讨论、电商可见评价与问答',limit='已有102条评论，短视频评论与完整翻页待接；不能推算全市场人群占比。',url='https://www.reddit.com/r/UnhasBrasil/'),
 dict(priority='P2',name='自有商品毛利与库存',question='热门款能否赚钱，是否值得补货？',fields='采购、物流、平台费、广告、退货、净收入、库存、交期；贡献利润',access='授权：自有ERP/店铺导出',limit='外部公开数据不能取得自家实际利润；本轮按要求不导入参考Excel。',url='https://developers.mercadolivre.com.br/pt_br/gerenciamento-de-vendas')
]
data['coverage']=[
 dict(platform='Mercado Livre',available='商品报价、6个商品评价归纳、少量累计销量下限',status='公开索引可用；直采返回页面未解析出商品，需补平台解析/授权接口'),
 dict(platform='Shopee BR',available='商品报价、部分规格/促销和原页评分',status='公开索引可用；动态页面的商品解析待补'),
 dict(platform='Reddit',available='102条可见评论与回复、11条主帖，覆盖12个讨论页',status='公开快照已取得；完整翻页和持续增量待接入'),
 dict(platform='YouTube',available='3条公开视频的元数据索引，评论0条',status='本轮视频页获取失败；评论采集未完成'),
 dict(platform='TikTok',available='2条美国TikTok Shop参考商品内容，巴西评论0条',status='公开内容检索受限；Creative Center广告数据可继续尝试'),
 dict(platform='Instagram',available='评论0条',status='未取得可验证公开评论；广告资料库可用于竞品素材研究'),
 dict(platform='Amazon BR',available='商品记录0条',status='本轮直接请求HTTP 503'),
]
encoded=json.dumps(data,ensure_ascii=False).replace('</','<\\/')
from enrich_channels import enrich
data=enrich(data,read('channel_observations.json'))
if (root/'latest_public_retry.json').exists():
    data['retry_report']=read('latest_public_retry.json')
    latest=read('retry_social_videos.json') if (root/'retry_social_videos.json').exists() else []
    # A new snapshot updates the existing URL; never count it as another video.
    social_by_url={r['source_url']:r for r in data['social']}
    for r in latest:social_by_url[r['source_url']]=r
    data['social']=list(social_by_url.values())
    data['tiktok_status']['checked_date']='2026-11-07'
    data['tiktok_status']['result']='已通过本机代理验证巴西BR出口；TikTok话题页HTTP200，但本轮返回HTML不含已解析视频/评论。Creative Center重定向TikTok One Creative Suite。'
    for c in data['coverage']:
        if c['platform']=='TikTok':c['status']=data['tiktok_status']['result']
        elif c['platform']=='Instagram':c['status']='巴西代理重试HTTP200；本轮HTML未解析出帖子/评论。'
        elif c['platform']=='YouTube':
            c['available']=str(sum(r['platform']=='YouTube' and r['content_type']=='video' for r in data['social']))+'条公开视频元数据，评论0条'
            c['status']='巴西代理重试解析7条视频元数据（含已有URL更新）；完整评论未取得。'
encoded=json.dumps(data,ensure_ascii=False).replace('</','<\\/')
page=(root/'unified_template.html').read_text(encoding='utf-8').replace('/*DATA*/',encoded)
analysis_template=(root/'analysis_template.html').read_text(encoding='utf-8')
analysis_markup=re.search(r'<main>(.*?)</main>',analysis_template,re.S).group(1)
analysis_markup=re.sub(r'id="([^"]+)"',r'id="analysis-\1"',analysis_markup)
analysis_markup=analysis_markup.replace('href="market_dashboard.html#sources"','href="#sources"').replace('href="market_dashboard.html"','href="#market"')
for section in ['pricing','pain','actions']:
    analysis_markup=analysis_markup.replace('href="#'+section+'"','href="#analysis-'+section+'"')
analysis_markup=analysis_markup.replace('<footer>','<footer hidden>')
analysis_markup='<div id="analysis" class="analysis-panel"><h2>分析与选品建议</h2>'+analysis_markup+'</div>'
analysis_script=re.search(r'<script>(.*?)</script>',analysis_template,re.S).group(1)
analysis_script=analysis_script.replace('const D=/*DATA*/;','').replace('document.getElementById(id)',"document.getElementById('analysis-'+id)")
page=page.replace('<section id="next">',analysis_markup+'<section id="next">',1)
page=page.replace('</html>','<script>(()=>{'+analysis_script+'})();</script></html>')
extension=(root/'channel_extension.html').read_text(encoding='utf-8')
extension_markup,extension_script=extension.split('<script>',1)
page=page.replace('<section id="comments">',extension_markup+'<section id="comments">',1)
page=page.replace('</html>','<script>'+extension_script+'</html>')
page=page.replace("r.data_status==='non_brazil_reference'?'美国参考':'公开索引语境样本'", "r.collection_method==='direct_public_html_vpn_br'?'本次公开HTML直采':r.data_status==='non_brazil_reference'?'美国参考':'公开索引语境样本'")
if data.get('retry_report'):
    page=page.replace('3条YouTube元数据',str(sum(r['platform']=='YouTube' and r['content_type']=='video' for r in data['social']))+'条YouTube元数据')
(root/'market_dashboard.html').write_text(page,encoding='utf-8')
(root/'unified_public_data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
# Preserve the already-open URL while making it show the same complete page.
(root/'analysis_dashboard.html').write_text(page,encoding='utf-8')
print(json.dumps({'products':len(data['products']),'comments':data['comment_summary']['comments'],'reviews':len(data['reviews']),'opportunities':len(data['opportunities']),'dashboard':str(root/'market_dashboard.html')},ensure_ascii=False))
