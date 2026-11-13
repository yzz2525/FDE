const products = [
  {id:'MLB-4812',name:'Unhas Postiças Nude Francesinha Curta',seller:'Bella Nails Store',price:'R$ 29,90',sales:'4,281',growth:'+64%',rating:'4.8',score:92,tone1:'#ead2d2',tone2:'#c59b9d',style:'短方 · 裸粉法式',margin:'48%',reason:'近 30 天销量增速领先，主流价位供给缺口明显；差评主要集中在胶贴牢固度，可通过升级配件形成差异化。'},
  {id:'MLB-2957',name:'Kit Unhas Almond Degradê Rosa',seller:'Studio Charm BR',price:'R$ 34,50',sales:'3,764',growth:'+51%',rating:'4.7',score:88,tone1:'#efc7d9',tone2:'#a97b9f',style:'杏仁 · 粉色渐变',margin:'44%',reason:'社媒粉色渐变内容播放持续增长，商品评论中“自然感”正向占比较高，适合做内容种草款。'},
  {id:'MLB-8031',name:'Press On Nails Efeito Cat Eye',seller:'Nail Art Pro',price:'R$ 39,90',sales:'2,915',growth:'+47%',rating:'4.9',score:86,tone1:'#9b83b8',tone2:'#47395f',style:'杏仁 · 紫色猫眼',margin:'52%',reason:'猫眼效果搜索热度升高，中高端价格带竞争尚未饱和，具备较好的毛利空间。'},
  {id:'MLB-6184',name:'Unhas Curtas Vermelho Cereja',seller:'Mimo Beauty',price:'R$ 24,90',sales:'2,640',growth:'+39%',rating:'4.6',score:81,tone1:'#d9757b',tone2:'#8e303f',style:'短圆 · 樱桃红',margin:'41%',reason:'红色基础款需求稳定且复购信号较强，适合作为常青款进入基础商品池。'},
  {id:'MLB-7365',name:'Unhas Decoradas Glitter Dourado',seller:'Glow Nails',price:'R$ 42,00',sales:'2,218',growth:'+34%',rating:'4.8',score:79,tone1:'#e8c98f',tone2:'#9a7440',style:'棺材 · 金色亮片',margin:'55%',reason:'节庆场景内容互动高，高端价格带用户对设计感更敏感，可作为小批量节点款。'},
  {id:'MLB-1429',name:'Kit Baby Boomer Natural 24 Peças',seller:'Donna Unhas',price:'R$ 31,90',sales:'1,984',growth:'+28%',rating:'4.7',score:76,tone1:'#f3ddd5',tone2:'#c2a49f',style:'方圆 · Baby Boomer',margin:'46%',reason:'自然风格评价稳定，但同质化较高，需要用尺寸覆盖或包装体验做差异化。'}
];

const concerns = [
  ['胶水牢固度',86,'32%负向'],['尺寸适配',79,'28%负向'],['款式还原度',73,'11%负向'],['持久时间',69,'24%负向'],['自然质感',64,'9%负向'],['安装难度',58,'17%负向'],['卸除伤甲',52,'21%负向'],['重复使用',47,'14%负向'],['包装配件',41,'18%负向'],['配送破损',36,'12%负向']
];

const viewConfig = {
  products:{title:'商品雷达',desc:'追踪巴西市场商品、价格、销量与款式变化。',eyebrow:'PRODUCT RADAR'},
  competitors:{title:'竞品监控',desc:'对比重点卖家的商品结构、定价与增长表现。',eyebrow:'COMPETITOR MONITOR'},
  reviews:{title:'评论洞察',desc:'从葡萄牙语评论中提取情感、共性问题和购买动机。',eyebrow:'VOICE OF CUSTOMER'},
  social:{title:'社媒趋势',desc:'识别内容热度、款式变化和潜在购买信号。',eyebrow:'SOCIAL TREND'},
  'ai-picks':{title:'AI 选品中心',desc:'综合需求、增长、口碑、竞争与毛利输出可解释推荐。',eyebrow:'AI OPPORTUNITY'}
};

const concernList = document.querySelector('#concernList');
concerns.forEach((c,i)=>{
  concernList.insertAdjacentHTML('beforeend',`<div class="concern-item"><span>${String(i+1).padStart(2,'0')}</span><div><div class="concern-name"><b>${c[0]}</b><em>${c[2]}</em></div><div class="concern-bar"><i style="width:${c[1]}%"></i></div></div><strong>${c[1]}</strong></div>`)
});

const productTable = document.querySelector('#productTable');
products.slice(0,5).forEach(renderTableRow);
function renderTableRow(p){
  productTable.insertAdjacentHTML('beforeend',`<tr data-product="${p.id}"><td><div class="product-cell"><i class="nail-thumb" style="--thumb:linear-gradient(145deg,${p.tone1},${p.tone2})"></i><div><b>${p.name}</b><small>${p.seller}</small></div></div></td><td><b>${p.price}</b></td><td>${p.sales}</td><td><span class="growth">${p.growth}</span></td><td>★ ${p.rating}</td><td><span class="score-pill">${p.score}</span></td></tr>`)
}

document.addEventListener('click', e=>{
  const nav = e.target.closest('.nav-item[data-view]');
  const targetButton = e.target.closest('[data-view-target]');
  if(nav) switchView(nav.dataset.view);
  if(targetButton) switchView(targetButton.dataset.viewTarget);
  const row = e.target.closest('[data-product]');
  if(row) openProduct(row.dataset.product);
});

function switchView(view){
  document.querySelectorAll('.nav-item[data-view]').forEach(n=>n.classList.toggle('active',n.dataset.view===view));
  document.querySelector('#overviewView').classList.toggle('active',view==='overview');
  document.querySelector('#genericView').classList.toggle('active',view!=='overview');
  const config = view==='overview'?{title:'市场总览'}:viewConfig[view];
  document.querySelector('#pageTitle').textContent=config.title;
  document.querySelector('#breadcrumbCurrent').textContent=config.title;
  if(view!=='overview'){
    document.querySelector('#genericTitle').textContent=config.title;
    document.querySelector('#genericDesc').textContent=config.desc;
    document.querySelector('#viewEyebrow').textContent=config.eyebrow;
    renderGeneric(view);
  }
  document.querySelector('#sidebar').classList.remove('open');
  window.scrollTo({top:0,behavior:'smooth'});
}

function renderGeneric(view){
  const root=document.querySelector('#genericContent');
  if(view==='products'){
    root.innerHTML=`<div class="cards-grid">${products.map(productCard).join('')}</div>`;
  }else if(view==='competitors'){
    root.innerHTML=`<article class="panel"><div class="panel-head"><div><h2>重点竞品排行</h2><p>综合预估销量、上新速度与评分</p></div></div><div class="product-table-wrap"><table class="product-table"><thead><tr><th>卖家</th><th>活跃商品</th><th>30天预估销量</th><th>均价</th><th>好评率</th><th>增长</th></tr></thead><tbody>
    ${[['Bella Nails Store','348','18,420','R$ 31.20','94.8%','+22%'],['Studio Charm BR','275','15,870','R$ 35.60','93.2%','+18%'],['Nail Art Pro','196','12,435','R$ 42.30','96.1%','+31%'],['Mimo Beauty','422','11,965','R$ 26.80','91.5%','+9%'],['Glow Nails','154','8,742','R$ 45.90','94.0%','+17%']].map((r,i)=>`<tr><td><div class="product-cell"><div class="avatar">${i+1}</div><b>${r[0]}</b></div></td><td>${r[1]}</td><td>${r[2]}</td><td>${r[3]}</td><td>★ ${r[4]}</td><td><span class="growth">${r[5]}</span></td></tr>`).join('')}</tbody></table></div></article>`;
  }else if(view==='reviews'){
    root.innerHTML=`<div class="review-layout"><article class="sentiment-card"><h2>整体情感分布</h2><p>8,426 条葡萄牙语评论 · Demo</p><div class="sentiment-ring"><div><strong>72%</strong><span>正向评价</span></div></div><div class="legend" style="justify-content:center"><span><i class="legend-dot" style="background:#43bf94"></i>正向 72%</span><span><i class="legend-dot" style="background:#efb64f"></i>中性 12%</span><span><i class="legend-dot" style="background:#ed7087"></i>负向 16%</span></div></article><article class="sentiment-card"><h2>高频主题</h2><p>颜色代表属性情感倾向</p><div class="topic-cloud" style="margin-top:18px"><span>bonita 漂亮</span><span class="negative-topic">cola fraca 胶水弱</span><span>natural 自然</span><span class="negative-topic">tamanho 尺寸</span><span>fácil 简单</span><span>durabilidade 持久</span><span class="negative-topic">descola 脱落</span><span>preço 价格</span><span>embalagem 包装</span><span>reutilizável 可复用</span></div><div class="opportunity-note" style="margin-top:20px"><span>机会</span><p>升级胶贴并增加尺寸，可覆盖 46% 的高频负向反馈</p></div></article></div>`;
  }else if(view==='social'){
    const social=[['#unhaspostiças','2.8M','+44%','#c9a2b6','#76566f'],['Francesinha fácil','1.9M','+38%','#ead5d2','#b78f8a'],['Cat eye em casa','1.4M','+51%','#9b84b9','#392e4c'],['Unhas para festa','986K','+27%','#d7ba84','#88652e']];
    root.innerHTML=`<div class="social-grid">${social.map((s,i)=>`<article class="social-card" style="--tone1:${s[3]};--tone2:${s[4]}"><div class="fake-nails"><i></i><i></i></div><div class="social-info"><h3>${s[0]}</h3><p>${i%2?'教程内容 · 巴西葡语':'款式展示 · 巴西地区'}</p><div class="social-metrics"><span>▶ ${s[1]}</span><span>♡ ${['184K','127K','96K','72K'][i]}</span><span class="growth">↗ ${s[2]}</span></div></div></article>`).join('')}</div>`;
  }else{
    root.innerHTML=`<div class="ai-list">${products.slice(0,5).map((p,i)=>`<article class="ai-pick" data-product="${p.id}"><div class="ai-rank">${String(i+1).padStart(2,'0')}</div><div class="ai-name"><i class="nail-thumb" style="--thumb:linear-gradient(145deg,${p.tone1},${p.tone2})"></i><div><h3>${p.style}</h3><p>${p.name}</p></div></div><div class="ai-stat"><span>增长</span><b class="growth">${p.growth}</b></div><div class="ai-stat hide-tablet"><span>预计毛利</span><b>${p.margin}</b></div><div class="ai-stat hide-tablet"><span>建议售价</span><b>${p.price}</b></div><div class="ai-score">${p.score}</div><div class="ai-action">查看分析 →</div></article>`).join('')}</div>`;
  }
}

function productCard(p,i){return `<article class="product-card" data-product="${p.id}"><div class="product-visual" style="--tone1:${p.tone1};--tone2:${p.tone2}"><span class="rank-badge">TOP ${i+1}</span></div><div class="product-card-body"><h3>${p.style}</h3><p>${p.name}</p><div class="card-stats"><div><span>价格</span><b>${p.price}</b></div><div><span>增速</span><b class="growth">${p.growth}</b></div><div><span>机会分</span><b>${p.score}</b></div></div></div></article>`}

function openProduct(id){
  const p=products.find(x=>x.id===id); if(!p)return;
  document.querySelector('#drawerContent').innerHTML=`<span class="eyebrow">AI PRODUCT ANALYSIS</span><h2>${p.style}</h2><p>${p.name} · ${p.seller}</p><div class="drawer-hero" style="--tone1:${p.tone1};--tone2:${p.tone2}"></div><div class="drawer-score"><div><span>机会分</span><b>${p.score}/100</b></div><div><span>30天增长</span><b class="growth">${p.growth}</b></div><div><span>预计毛利</span><b>${p.margin}</b></div></div><div class="drawer-reason"><strong>✦ AI 推荐逻辑</strong><br>${p.reason}</div><div class="drawer-actions"><button class="secondary-btn" onclick="showToast('已加入观察','将在每日同步后更新数据')">加入观察</button><button class="primary-btn" onclick="showToast('测试计划已创建','建议首批 500 套，目标售价 ${p.price}')">生成测试计划</button></div>`;
  document.querySelector('#productDrawer').classList.add('open');
}

document.querySelectorAll('.date-switch button').forEach(btn=>btn.addEventListener('click',()=>{
  document.querySelectorAll('.date-switch button').forEach(b=>b.classList.remove('active'));btn.classList.add('active');showToast(`已切换至 ${btn.dataset.days} 天`,`图表已按新的时间范围更新`)
}));
document.querySelector('#mobileMenu').onclick=()=>document.querySelector('#sidebar').classList.toggle('open');
document.querySelector('#dataSourceBtn').onclick=()=>document.querySelector('#dataModal').classList.add('open');
document.querySelectorAll('[data-close-modal]').forEach(x=>x.onclick=()=>document.querySelector('#dataModal').classList.remove('open'));
document.querySelectorAll('[data-close-drawer]').forEach(x=>x.onclick=()=>document.querySelector('#productDrawer').classList.remove('open'));
document.querySelector('#dataModal').addEventListener('click',e=>{if(e.target.id==='dataModal')e.currentTarget.classList.remove('open')});
document.querySelector('#productDrawer').addEventListener('click',e=>{if(e.target.id==='productDrawer')e.currentTarget.classList.remove('open')});
document.querySelector('#importBtn').onclick=()=>document.querySelector('#csvInput').click();
document.querySelector('#csvInput').onchange=e=>{if(e.target.files[0])showToast('数据导入完成',`${e.target.files[0].name} 已进入待校验队列`)};
document.querySelector('#exportBtn').onclick=()=>{
  const rows=['商品,卖家,价格,30天预估销量,增长,评分,机会分',...products.map(p=>`"${p.name}","${p.seller}","${p.price}",${p.sales},${p.growth},${p.rating},${p.score}`)];
  const blob=new Blob(['\ufeff'+rows.join('\n')],{type:'text/csv;charset=utf-8'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='NailTrend-BR-demo-report.csv';a.click();URL.revokeObjectURL(a.href);showToast('报告已导出','CSV 文件已生成并下载');
};

document.querySelector('#searchInput').addEventListener('input',e=>{
  if(!document.querySelector('.cards-grid'))return;
  const q=e.target.value.toLowerCase();document.querySelectorAll('.product-card').forEach((card,i)=>card.style.display=(products[i].name+' '+products[i].seller+' '+products[i].style).toLowerCase().includes(q)?'':'none');
});

let toastTimer;window.showToast=function(title,text){
  const toast=document.querySelector('#toast');document.querySelector('#toastTitle').textContent=title;document.querySelector('#toastText').textContent=text;toast.classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>toast.classList.remove('show'),2800)
};
