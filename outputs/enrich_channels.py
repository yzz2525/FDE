"""Enrich unified data with public channel observations and title dimensions."""
import re,hashlib
def enrich(data,observations):
    rows=data['products']
    for r in rows:
        if r['platform']=='Shopee BR' and r['title'] in observations['shopee_existing']:
            r.update(observations['shopee_existing'][r['title']])
    existing={(r['platform'],r['title'],r['source_url']) for r in rows}
    for r in observations['products']:
        key=(r['platform'],r['title'],r['source_url'])
        if key not in existing:
            rows.append(dict(r,evidence_method='public_search_snapshot',retrieved_date=observations['retrieved_date']))
            existing.add(key)
    for r in rows:
        title=r['title'].lower()
        r['record_id']=hashlib.sha256((r['platform']+'|'+r['title']+'|'+r['source_url']).encode()).hexdigest()[:16]
        if not r.get('brand'):
            r['brand']=next((brand for pattern,brand in [('impress|kiss','KISS / imPRESS'),('sabrina sato','Sabrina Sato'),('macrilan','Macrilan'),('santa clara','Santa Clara'),('koasis','Koasis'),('honey ?girl','Honey Girl'),('one ?love','One Love'),('nitesco','Nitesco'),('gluroo','Gluroo'),('dafu','Dafu')] if re.search(pattern,title)),None)
        r['shape_tags']=';'.join(label for pattern,label in [('quadrad','方形'),('am[eê]nd|almond|amendo','杏仁'),('bailarina|ballerina|coffin','芭蕾/棺材'),('oval','椭圆'),('stiletto','尖形'),('redonda','圆形')] if re.search(pattern,title))
        r['color_tags']=';'.join(label for pattern,label in [('nude','裸色'),('rosa|ros[eé]|pink','粉色'),('branc','白色'),('pret|black','黑色'),('azul|ocean','蓝色'),('vermelh|red','红色'),('dourad|gold','金色'),('magenta','洋红'),('green','绿色')] if re.search(pattern,title))
        r['length_tags']=';'.join(label for pattern,label in [('curt','短款'),('m[eé]di','中款'),('long','长款')] if re.search(pattern,title))
        r['style_dimensions']=';'.join(label for pattern,label in [('frances|french','法式'),('glitter','亮片'),('flor','花卉'),('cat.eye|olho.de.gato|magnetic','猫眼/磁效'),('gel','Gel关键词'),('3d','3D装饰'),('degrad','渐变'),('matte|fosca','哑光')] if re.search(pattern,title))
        match=re.search(r'\b(\d+)\s*(?:unidades|unid\b|un\b|pe[çc]as|pcs|pçs)',title)
        r['pieces_title']=int(match.group(1)) if match else None
        r['dimension_method']='标题关键词提取，非图片识别；可能缺失或多选'
    data['tiktok_status']=observations['tiktok_status']
    data['channel_update_date']=observations['retrieved_date']
    for c in data['coverage']:
        if c['platform']=='Shopee BR':
            c['available']=f"虾皮 {sum(r['platform']=='Shopee BR' for r in rows)}条报价；品牌/甲型/颜色等标题维度；部分店铺月售标签"
        if c['platform']=='TikTok':
            c['status']=observations['tiktok_status']['result']
    return data
