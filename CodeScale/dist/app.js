const seed = [
  {id:1,name:'售后知识库问答',department:'客户成功部',date:'2026-11-05',acceptanceRule:'答案引用有效来源，关键字段无事实错误',acceptanceOwner:'客服主管',evidence:'complete',baselineCost:2280,baselineQualified:140,baselineMinutes:9.5,aiCost:420,humanCost:690,reworkCost:120,integrationCost:160,opsCost:90,total:180,qualified:162,handovers:18,minutes:3.2},
  {id:2,name:'商品标题批量生成',department:'电商运营部',date:'2026-11-03',acceptanceRule:'标题符合平台规则且无需二次改写',acceptanceOwner:'运营负责人',evidence:'complete',baselineCost:2460,baselineQualified:178,baselineMinutes:8.2,aiCost:310,humanCost:880,reworkCost:460,integrationCost:210,opsCost:80,total:240,qualified:196,handovers:34,minutes:4.8},
  {id:3,name:'竞品周报分析',department:'战略市场部',date:'2026-10-30',acceptanceRule:'覆盖指定竞品并提供可追溯数据来源',acceptanceOwner:'市场总监',evidence:'partial',baselineCost:2850,baselineQualified:31,baselineMinutes:42,aiCost:680,humanCost:1680,reworkCost:760,integrationCost:320,opsCost:120,total:42,qualified:28,handovers:12,minutes:28},
  {id:4,name:'销售线索初筛',department:'销售部',date:'2026-10-26',acceptanceRule:'线索字段完整且分级与人工复核一致',acceptanceOwner:'销售运营',evidence:'complete',baselineCost:2140,baselineQualified:108,baselineMinutes:11,aiCost:520,humanCost:740,reworkCost:190,integrationCost:140,opsCost:80,total:150,qualified:126,handovers:21,minutes:5.5},
  {id:5,name:'发票信息识别',department:'财务部',date:'2026-10-19',acceptanceRule:'金额、税号、日期三项字段全部正确',acceptanceOwner:'财务复核员',evidence:'complete',baselineCost:1860,baselineQualified:258,baselineMinutes:4.8,aiCost:260,humanCost:510,reworkCost:370,integrationCost:190,opsCost:70,total:320,qualified:274,handovers:28,minutes:2.1},
  {id:6,name:'合同条款提取',department:'法务部',date:'2026-10-12',acceptanceRule:'指定条款完整提取且不存在实质性遗漏',acceptanceOwner:'法务经理',evidence:'claim',baselineCost:2050,baselineQualified:61,baselineMinutes:18,aiCost:560,humanCost:1120,reworkCost:540,integrationCost:180,opsCost:100,total:76,qualified:58,handovers:20,minutes:13.5}
];

const storeKey = 'codescale.tasks.v2';
let tasks = JSON.parse(localStorage.getItem(storeKey) || 'null') || seed;
const $ = selector => document.querySelector(selector);
const $$ = selector => [...document.querySelectorAll(selector)];
const esc = value => String(value ?? '').replace(/[&<>'"]/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));
const money = value => '¥' + Number(value || 0).toLocaleString('zh-CN', {maximumFractionDigits:2});
const pct = value => `${Math.round(Number(value || 0) * 100)}%`;
const pp = value => `${value >= 0 ? '+' : ''}${(value * 100).toFixed(1)} 个百分点`;
const clamp = (min, value, max) => Math.min(max, Math.max(min, value));
const localDate = () => new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0,10);
const currentCost = task => ['aiCost','humanCost','reworkCost','integrationCost','opsCost'].reduce((sum,key) => sum + (+task[key] || 0), 0);
const fullCost = task => currentCost(task) / (+task.qualified || 1);
const baselineFullCost = task => (+task.baselineCost || 0) / (+task.baselineQualified || 1);
const success = task => (+task.qualified || 0) / (+task.total || 1);
const baselineSuccess = task => (+task.baselineQualified || 0) / (+task.total || 1);
const handover = task => (+task.handovers || 0) / (+task.total || 1);
const costDelta = task => (fullCost(task) - baselineFullCost(task)) / (baselineFullCost(task) || 1);
const status = task => costDelta(task) <= -.12 && success(task) >= baselineSuccess(task) ? 'improved' : costDelta(task) <= .03 && success(task) >= baselineSuccess(task) - .03 ? 'review' : 'risk';
const statusText = {improved:'已验证改善',review:'待复核',risk:'未达基线'};
const evidenceText = {complete:'证据完整',partial:'部分证据',claim:'仅业务口径'};

function totals(){
  const sum = key => tasks.reduce((total, task) => total + (+task[key] || 0), 0);
  const cost = tasks.reduce((total, task) => total + currentCost(task), 0);
  const baselineCost = sum('baselineCost');
  return {
    ai:sum('aiCost'), human:sum('humanCost'), rework:sum('reworkCost'), integration:sum('integrationCost'), ops:sum('opsCost'),
    cost, baselineCost, savings:baselineCost - cost, total:sum('total'), qualified:sum('qualified'), baselineQualified:sum('baselineQualified'), handovers:sum('handovers'),
    timeSaved:tasks.reduce((total, task) => total + Math.max(0, (+task.baselineMinutes || 0) - (+task.minutes || 0)) * (+task.total || 0), 0)
  };
}

function dataQuality(){
  if(!tasks.length) return 0;
  const fields = ['name','department','date','acceptanceRule','acceptanceOwner','baselineCost','baselineQualified','baselineMinutes','total','qualified','minutes','evidence'];
  const fieldScore = tasks.reduce((sum, task) => sum + fields.filter(field => task[field] !== '' && task[field] !== null && task[field] !== undefined).length / fields.length, 0) / tasks.length;
  const evidenceScore = tasks.reduce((sum, task) => sum + ({complete:1, partial:.65, claim:.3}[task.evidence] || 0), 0) / tasks.length;
  return Math.round((fieldScore * .65 + evidenceScore * .35) * 100);
}

function save(){ localStorage.setItem(storeKey, JSON.stringify(tasks)); renderAll(); }
function toast(message){ const element=$('#toast'); element.textContent=message; element.classList.add('show'); setTimeout(()=>element.classList.remove('show'),2200); }

function renderQuality(){
  const quality = dataQuality();
  $('#dataQuality').textContent = `${quality}%`;
  $('#qualityBar').style.width = `${quality}%`;
  $('#qualityLabel').textContent = quality >= 85 ? '可信' : quality >= 65 ? '可用' : '待补充';
  const incomplete = tasks.filter(task => task.evidence !== 'complete').length;
  $('#qualityHint').textContent = incomplete ? `${incomplete} 项任务仍需补充原始验收或抽样证据。` : '所有任务均登记了基线、验收规则与完整证据。';
}

function renderMetrics(){
  const total = totals();
  const cpq = total.cost / (total.qualified || 1);
  const baselineCpq = total.baselineCost / (total.baselineQualified || 1);
  const metrics = [
    ['当前总投入', money(total.cost), 'AI、人工、返工、集成与运维', 'var(--green)'],
    ['合格成果全成本', money(cpq), `基线 ${money(baselineCpq)} / 个`, 'var(--lime)'],
    ['已验证成本变化', money(total.savings), total.savings >= 0 ? '相对基线节省' : '相对基线增加', total.savings >= 0 ? 'var(--blue)' : 'var(--red)'],
    ['累计节省工时', `${Math.round(total.timeSaved).toLocaleString('zh-CN')} 分钟`, '按同任务量与平均时长计算', 'var(--orange)']
  ];
  $('#metricGrid').innerHTML = metrics.map(metric => `<article class="metric-card" style="--accent:${metric[3]}"><span>${metric[0]}</span><strong>${metric[1]}</strong><small>${metric[2]}</small></article>`).join('');
}

function renderChart(){
  const items = [...tasks].sort((a,b) => b.date.localeCompare(a.date)).slice(0,6).reverse();
  if(!items.length){ $('#costChart').innerHTML=''; $('#chartYLabels').innerHTML=''; return; }
  const values = items.flatMap(task => [baselineFullCost(task), fullCost(task)]);
  const max = Math.max(10, Math.ceil(Math.max(...values) / 10) * 10);
  const h = 190, baseY = 198, groupWidth = 720 / items.length, barWidth = Math.min(28, groupWidth * .22);
  $('#chartYLabels').innerHTML = [max, max*.67, max*.33, 0].map(value => `<span>${money(value)}</span>`).join('');
  const grid = [0,.33,.67,1].map(ratio => `<line x1="0" y1="${8 + h*ratio}" x2="720" y2="${8 + h*ratio}" stroke="#e4e5df"/>`).join('');
  const bars = items.map((task,index) => {
    const center = groupWidth * index + groupWidth/2;
    const before = baselineFullCost(task), after = fullCost(task);
    const beforeHeight = before/max*h, afterHeight = after/max*h;
    const label = task.name.length > 7 ? `${task.name.slice(0,7)}…` : task.name;
    return `<rect x="${center-barWidth-2}" y="${baseY-beforeHeight}" width="${barWidth}" height="${beforeHeight}" rx="3" fill="#c8cec8"/><rect x="${center+2}" y="${baseY-afterHeight}" width="${barWidth}" height="${afterHeight}" rx="3" fill="#235c42"/><text x="${center}" y="224" text-anchor="middle" font-size="9" fill="#8a958e">${esc(label)}</text>`;
  }).join('');
  $('#costChart').innerHTML = `${grid}${bars}`;
}

function renderMix(){
  const total = totals();
  const parts = [['AI 费用',total.ai,'#235c42'],['人工处理',total.human,'#b8d96a'],['返工成本',total.rework,'#e8834d'],['集成摊销',total.integration,'#648aa0'],['运维成本',total.ops,'#cbd2cb']];
  const ratios = parts.map(part => total.cost ? part[1]/total.cost*100 : 0);
  let at = 0;
  $('#donut').style.background = `conic-gradient(${parts.map((part,index) => { const start=at; at+=ratios[index]; return `${part[2]} ${start}% ${at}%`; }).join(',')})`;
  $('#donutTotal').textContent = money(total.cost);
  $('#mixList').innerHTML = parts.map((part,index) => `<div class="mix-item"><i style="--c:${part[2]}"></i><span>${part[0]}</span><strong>${Math.round(ratios[index])}%</strong></div>`).join('');
}

function deltaMarkup(task){
  const delta = costDelta(task);
  return `<span class="delta ${delta <= 0 ? 'good' : 'bad'}">${delta > 0 ? '+' : ''}${Math.round(delta*100)}%</span>`;
}

function overviewRow(task){
  const state = status(task);
  return `<tr><td class="task-name"><strong>${esc(task.name)}</strong><small>${esc(task.date)}</small></td><td>${esc(task.department)}</td><td>${money(baselineFullCost(task))}</td><td><strong>${money(fullCost(task))}</strong></td><td>${deltaMarkup(task)}</td><td><span class="pill ${state}">${statusText[state]}</span></td></tr>`;
}

function taskRow(task){
  const state = status(task), successChange = success(task) - baselineSuccess(task);
  return `<tr><td class="task-name"><strong>${esc(task.name)}</strong><small>${esc(task.department)} · ${esc(task.acceptanceOwner)}</small></td><td>${esc(task.acceptanceRule)}<span class="cell-note">${esc(task.date)}</span></td><td>${money(baselineFullCost(task))}<span class="cell-note">${task.baselineQualified} 个合格成果</span></td><td><strong>${money(fullCost(task))}</strong><span class="cell-note">${task.qualified}/${task.total} 通过</span></td><td><span class="delta ${successChange >= 0 ? 'good' : 'bad'}">${pp(successChange)}</span></td><td><span class="evidence ${esc(task.evidence)}">${evidenceText[task.evidence] || '未登记'}</span></td><td><span class="pill ${state}">${statusText[state]}</span></td><td><button class="delete-btn" data-delete="${task.id}" aria-label="删除 ${esc(task.name)}">删除</button></td></tr>`;
}

function renderTables(){
  const sorted = [...tasks].sort((a,b) => b.date.localeCompare(a.date));
  $('#overviewTable').innerHTML = sorted.slice(0,5).map(overviewRow).join('');
  const query = ($('#searchInput')?.value || '').trim().toLowerCase();
  const filter = $('#statusFilter')?.value || 'all';
  const filtered = sorted.filter(task => (!query || `${task.name}${task.department}${task.acceptanceOwner}`.toLowerCase().includes(query)) && (filter === 'all' || status(task) === filter));
  $('#taskTable').innerHTML = filtered.map(taskRow).join('');
  $('#emptyState').hidden = !!filtered.length;
  $$('[data-delete]').forEach(button => button.onclick = () => {
    if(confirm('删除这条任务记录？该操作只影响当前浏览器中的演示数据。')){
      tasks = tasks.filter(task => String(task.id) !== button.dataset.delete);
      save(); toast('任务记录已删除');
    }
  });
}

function recommendations(){
  const list = [];
  const belowBaseline = [...tasks].filter(task => status(task)==='risk').sort((a,b) => costDelta(b)-costDelta(a))[0];
  if(belowBaseline){
    const gap = currentCost(belowBaseline) - (+belowBaseline.baselineCost || 0);
    list.push({title:`重新限定「${belowBaseline.name}」的交付范围`,body:`当前成果成本 ${money(fullCost(belowBaseline))}，基线为 ${money(baselineFullCost(belowBaseline))}；成功率变化 ${pp(success(belowBaseline)-baselineSuccess(belowBaseline))}。先检查验收规则、任务拆分和失败样本。`,impact:`总成本差额 ${money(gap)}`});
  }
  const highRework = [...tasks].sort((a,b) => (b.reworkCost/currentCost(b))-(a.reworkCost/currentCost(a)))[0];
  if(highRework && +highRework.reworkCost > 0){
    list.push({title:`复盘「${highRework.name}」的返工样本`,body:`返工成本占当前总成本的 ${pct(highRework.reworkCost/currentCost(highRework))}。建议给失败样本标注原因，再决定优化 Prompt、知识库、工作流或人工审核节点。`,impact:`返工成本 ${money(highRework.reworkCost)}`});
  }
  const incomplete = tasks.filter(task => task.evidence !== 'complete');
  if(incomplete.length){
    list.push({title:'补齐验收证据后再对外宣称收益',body:`${incomplete.length} 项任务仍是部分证据或业务口径。应保存抽样记录、验收人、观察周期和原始结果，避免把宣传数字当成已验证成效。`,impact:`可信度 ${dataQuality()}%`});
  }
  if(list.length < 3){
    const highHandover = [...tasks].sort((a,b) => handover(b)-handover(a))[0];
    if(highHandover) list.push({title:`为「${highHandover.name}」设置分级接管`,body:`当前人工接管率 ${pct(handover(highHandover))}。可按置信度和风险等级分流，优先减少无效人工复核。`,impact:`接管 ${highHandover.handovers} 次`});
  }
  return list.slice(0,3);
}

function renderDiagnosis(){
  const total = totals();
  const baselineSuccessRate = total.baselineQualified/(total.total||1), currentSuccessRate = total.qualified/(total.total||1);
  const costImprovement = total.savings/(total.baselineCost||1);
  const score = clamp(0, Math.round(60 + costImprovement*60 + (currentSuccessRate-baselineSuccessRate)*100 - (total.handovers/(total.total||1))*10), 100);
  const recs = recommendations();
  $('#diagnosisSummary').innerHTML = `<div class="score-card"><span>基线对比得分</span><strong>${score}<small>/100</small></strong><p>依据成本变化、成功率变化和人工接管率计算。</p></div><div class="score-card light"><span>未达基线任务</span><strong>${tasks.filter(task=>status(task)==='risk').length} 项</strong><p>当前成本或合格率尚未达到同口径基线。</p></div><div class="score-card light"><span>已验证成本变化</span><strong>${money(total.savings)}</strong><p>仅使用已登记的改造前后总成本计算。</p></div>`;
  $('#recommendationList').innerHTML = recs.map((rec,index) => `<article class="recommendation"><div class="rec-num">0${index+1}</div><div><h3>${esc(rec.title)}</h3><p>${esc(rec.body)}</p></div><div class="impact"><span>当前证据</span><strong>${esc(rec.impact)}</strong></div></article>`).join('');
}

function formatDate(value){ return new Intl.DateTimeFormat('zh-CN',{year:'numeric',month:'long',day:'numeric'}).format(new Date(`${value}T00:00:00`)); }

function renderReport(){
  const total = totals();
  const cpq = total.cost/(total.qualified||1), baselineCpq = total.baselineCost/(total.baselineQualified||1);
  const baselineRate = total.baselineQualified/(total.total||1), currentRate = total.qualified/(total.total||1);
  const sorted = [...tasks].sort((a,b)=>a.date.localeCompare(b.date));
  const start = sorted[0]?.date, end = sorted.at(-1)?.date;
  $('#reportDate').textContent = start && end ? `报告周期：${formatDate(start)}—${formatDate(end)} · 演示企业` : '尚无任务数据';
  $('#reportKpis').innerHTML = [['当前总投入',money(total.cost)],['已验证成本变化',money(total.savings)],['成果成本变化',`${Math.round((cpq/(baselineCpq||1)-1)*100)}%`],['成功率变化',pp(currentRate-baselineRate)]].map(item => `<div class="report-kpi"><span>${item[0]}</span><strong>${item[1]}</strong></div>`).join('');
  $('#reportNarrative').textContent = `本期记录 ${tasks.length} 类 AI 业务任务，共产生 ${total.qualified} 个合格成果。当前总投入 ${money(total.cost)}，相对同口径基线${total.savings >= 0 ? '减少' : '增加'} ${money(Math.abs(total.savings))}；每个合格成果成本由 ${money(baselineCpq)} 变为 ${money(cpq)}。其中 ${tasks.filter(task=>task.evidence==='complete').length} 项具有完整基线与验收证据，其余结论应在补证后再用于对外披露。`;
  $('#reportEvidenceTable').innerHTML = [...tasks].sort((a,b)=>costDelta(a)-costDelta(b)).map(task => `<tr><td>${esc(task.name)}</td><td>${money(baselineFullCost(task))}</td><td>${money(fullCost(task))}</td><td>${deltaMarkup(task)}</td><td>${pp(success(task)-baselineSuccess(task))}</td></tr>`).join('');
  $('#reportActions').innerHTML = recommendations().map((rec,index) => `<div class="report-action"><strong>0${index+1} · ${esc(rec.title)}</strong><span>${esc(rec.body)}</span></div>`).join('');
}

function renderFinding(){
  if(!tasks.length){ $('#heroFinding').textContent='先记录第一个 AI 业务任务'; $('#heroSub').textContent='定义基线、验收标准和真实成本后再做判断。'; return; }
  const best = [...tasks].sort((a,b)=>costDelta(a)-costDelta(b))[0];
  $('#heroFinding').textContent = `${best.name}的改善幅度最明确`;
  $('#heroSub').textContent = `合格成果成本较基线${costDelta(best)<=0?'下降':'上升'} ${Math.abs(Math.round(costDelta(best)*100))}%，证据状态：${evidenceText[best.evidence]}。`;
}

function renderAll(){ renderQuality(); renderMetrics(); renderChart(); renderMix(); renderTables(); renderDiagnosis(); renderReport(); renderFinding(); }
function switchView(name){
  $$('.view').forEach(view => view.classList.remove('active'));
  $(`#${name}View`).classList.add('active');
  $$('.nav-item').forEach(item => item.classList.toggle('active', item.dataset.view===name));
  $('#currentView').textContent = {overview:'项目总览',tasks:'任务台账',diagnosis:'效能诊断',reports:'价值报告'}[name];
  $('#sidebar').classList.remove('open'); window.scrollTo({top:0,behavior:'smooth'});
}

$$('.nav-item').forEach(item => item.onclick=()=>switchView(item.dataset.view));
$$('[data-go]').forEach(item => item.onclick=()=>switchView(item.dataset.go));
$('#menuBtn').onclick=()=>$('#sidebar').classList.toggle('open');
const modal=$('#modal');
function openModal(){ modal.hidden=false; document.body.style.overflow='hidden'; calcPreview(); $('#taskForm [name=name]').focus(); }
function closeModal(){ modal.hidden=true; document.body.style.overflow=''; }
$('#openModal').onclick=$('#openModal2').onclick=openModal;
$('#closeModal').onclick=$('#cancelModal').onclick=closeModal;
modal.onclick=event=>{if(event.target===modal)closeModal()};
document.onkeydown=event=>{if(event.key==='Escape')closeModal()};

function calcPreview(){
  const form = new FormData($('#taskForm'));
  const cost = ['aiCost','humanCost','reworkCost','integrationCost','opsCost'].reduce((sum,key)=>sum+(+form.get(key)||0),0);
  const qualified = +form.get('qualified') || 1, baselineCost=+form.get('baselineCost')||0, baselineQualified=+form.get('baselineQualified')||1;
  const current = cost/qualified, baseline=baselineCost/baselineQualified, delta=(current/(baseline||1)-1)*100;
  $('#formulaResult').textContent = `${money(baseline)} → ${money(current)} / 个（${delta>0?'+':''}${Math.round(delta)}%）`;
}
$$('#taskForm input').forEach(input=>input.addEventListener('input',calcPreview));

$('#taskForm').onsubmit = event => {
  event.preventDefault();
  const record = Object.fromEntries(new FormData(event.target));
  ['baselineCost','baselineQualified','baselineMinutes','aiCost','humanCost','reworkCost','integrationCost','opsCost','total','qualified','handovers','minutes'].forEach(key=>record[key]=+record[key]);
  if(record.qualified>record.total || record.baselineQualified>record.total){ toast('改造前后合格成果数都不能大于任务总数'); return; }
  if(record.handovers>record.total){ toast('人工接管数不能大于任务总数'); return; }
  record.id=Date.now(); tasks.push(record); save(); closeModal(); event.target.reset(); event.target.date.value=localDate(); calcPreview(); toast('任务已记录，并完成基线对比'); switchView('tasks');
};

$('#searchInput').oninput=renderTables;
$('#statusFilter').onchange=renderTables;
$('#refreshDiagnosis').onclick=()=>{renderDiagnosis();toast('已按当前基线和验收数据重新计算')};
$('#printReport').onclick=()=>window.print();
$('#exportCsv').onclick=()=>{
  const heads=['任务','部门','日期','验收标准','验收负责人','证据状态','基线总成本','基线合格成果','基线平均时长','AI费用','人工成本','返工成本','集成摊销','运维成本','总任务','当前合格成果','人工接管','当前平均时长','基线成果成本','当前成果成本'];
  const rows=tasks.map(task=>[task.name,task.department,task.date,task.acceptanceRule,task.acceptanceOwner,evidenceText[task.evidence],task.baselineCost,task.baselineQualified,task.baselineMinutes,task.aiCost,task.humanCost,task.reworkCost,task.integrationCost,task.opsCost,task.total,task.qualified,task.handovers,task.minutes,baselineFullCost(task).toFixed(2),fullCost(task).toFixed(2)]);
  const csv='\ufeff'+[heads,...rows].map(row=>row.map(value=>`"${String(value).replaceAll('"','""')}"`).join(',')).join('\n');
  const link=document.createElement('a'); link.href=URL.createObjectURL(new Blob([csv],{type:'text/csv'})); link.download='CodeScale-价值验收台账.csv'; link.click(); URL.revokeObjectURL(link.href); toast('CSV 已导出');
};

$('#taskForm [name=date]').value=localDate();
renderAll();

