from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any, Dict, List


def generate_channel_library_report(
    path: Path,
    generated_at: str,
    input_config: Dict[str, Any],
    candidates: List[Dict[str, Any]],
    summary: Dict[str, Any],
) -> None:
    """Generate the single Chinese channel library dashboard."""
    path.parent.mkdir(parents=True, exist_ok=True)
    product = html.escape(str(input_config.get("product_name") or "产品"))
    template = r'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>__PRODUCT__ 渠道库</title>
<style>
:root{--bg:#f6f7f9;--card:#fff;--text:#182230;--muted:#667085;--line:#e4e7ec;--blue:#2563eb;--blue2:#eff6ff;--green:#067647;--green2:#ecfdf3;--shadow:0 10px 28px rgba(16,24,40,.06);--radius:14px}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font-family:ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif}a{color:var(--blue);text-decoration:none}a:hover{text-decoration:underline}.page{max-width:1480px;margin:0 auto;padding:24px}.hero{display:grid;grid-template-columns:minmax(0,1.4fr) minmax(320px,.6fr);gap:16px}.card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow)}.hero-main{padding:26px}.kicker{color:var(--blue);font-size:13px;font-weight:800}.hero h1{margin:8px 0 10px;font-size:34px;line-height:1.15}.subtitle{color:var(--muted);line-height:1.7}.meta{padding:20px;display:grid;gap:12px}.meta-row{display:flex;justify-content:space-between;gap:12px;padding-bottom:10px;border-bottom:1px solid var(--line)}.meta-row:last-child{border-bottom:0}.meta-label{color:var(--muted)}.meta-value{font-weight:800;text-align:right}.stats{display:grid;grid-template-columns:repeat(4,minmax(150px,1fr));gap:12px;margin:18px 0}.stat{padding:16px}.stat-value{font-size:28px;font-weight:900}.stat-label{font-size:13px;color:var(--muted);margin-top:4px}.section{margin-top:18px}.section-head{display:flex;align-items:end;justify-content:space-between;gap:12px;padding:18px 18px 0}.section-title{font-size:20px;font-weight:900}.section-note{font-size:13px;color:var(--muted);margin-top:4px}.chips{display:flex;flex-wrap:wrap;gap:8px}.chip{display:inline-flex;align-items:center;gap:4px;padding:6px 10px;border-radius:999px;background:var(--blue2);color:#1d4ed8;font-size:12px;font-weight:800}.chip.ok{background:var(--green2);color:var(--green)}.toolbar{display:grid;grid-template-columns:1.7fr minmax(150px,.55fr) minmax(150px,.55fr) minmax(150px,.55fr) 100px;gap:10px;padding:16px}input,select,button{width:100%;border:1px solid var(--line);border-radius:10px;background:#fff;color:var(--text);padding:10px 12px;font:inherit}button{background:var(--blue);border-color:var(--blue);color:#fff;font-weight:800;cursor:pointer}.toggles{display:flex;flex-wrap:wrap;gap:14px;padding:0 16px 16px;color:var(--muted);font-size:13px}.toggles label{display:flex;align-items:center;gap:8px}.toggles input{width:auto}.score{display:inline-flex;width:max-content;min-width:54px;justify-content:center;padding:5px 10px;border-radius:999px;background:var(--blue2);color:var(--blue);font-weight:900}.small{font-size:12px;color:var(--muted);line-height:1.55}.table-wrap{overflow:auto;border-top:1px solid var(--line)}table{width:100%;border-collapse:collapse;min-width:1240px;font-size:13px}th{position:sticky;top:0;background:#f9fafb;z-index:1;text-align:left;color:#475467;border-bottom:1px solid var(--line);padding:11px}td{border-bottom:1px solid var(--line);padding:11px;vertical-align:top}tr.data-row{cursor:pointer}tr.data-row:hover{background:#f8fbff}.name-cell{font-weight:900;min-width:220px}.detail-row td{background:#fbfdff;padding:0}.detail{display:grid;grid-template-columns:420px minmax(0,1fr);gap:14px;padding:16px}.box{background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px}.box h4{margin:0 0 10px}.bars{display:grid;gap:9px}.bar-row{display:grid;grid-template-columns:138px 1fr 48px;align-items:center;gap:9px}.bar{height:8px;border-radius:999px;background:#e5e7eb;overflow:hidden}.bar span{display:block;height:100%;background:var(--blue)}.empty{padding:26px;text-align:center;color:var(--muted)}.footer{margin-top:18px;color:var(--muted);font-size:12px;line-height:1.7}@media(max-width:1180px){.hero{grid-template-columns:1fr}.stats{grid-template-columns:repeat(2,1fr)}.toolbar{grid-template-columns:1fr 1fr}.detail{grid-template-columns:1fr}}@media(max-width:720px){.page{padding:14px}.stats{grid-template-columns:1fr 1fr}.toolbar{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="page">
<section class="hero">
  <div class="card hero-main">
    <div class="kicker">渠道发现总看板</div>
    <h1>__PRODUCT__ 渠道库</h1>
    <div class="subtitle">这是唯一需要查看的渠道汇总页。每次新抓取的数据会先保存到对应 campaign 的 data 目录，再合并、查重并刷新到这个总看板。请在联系前人工确认渠道匹配度、公开联系方式、赞助页和备注。</div>
  </div>
  <div class="card meta">
    <div class="meta-row"><span class="meta-label">更新时间</span><span class="meta-value">__GENERATED__</span></div>
    <div class="meta-row"><span class="meta-label">最新 Run</span><span class="meta-value" id="latestRun"></span></div>
    <div class="meta-row"><span class="meta-label">数据源</span><span class="meta-value">data/master-candidates.json</span></div>
  </div>
</section>
<section class="stats" id="stats"></section>
<section class="section card">
  <div class="section-head"><div><div class="section-title">渠道合集</div><div class="section-note">这里展示多次抓取后的去重合集。点击任意行可以展开评分细节和来源信息。</div></div></div>
  <div class="toolbar">
    <input id="q" placeholder="搜索名称、主题、受众、关键词、备注..." />
    <select id="type"><option value="">全部类型</option></select>
    <select id="sort"><option value="score_desc">分数从高到低</option><option value="seen_desc">出现次数从多到少</option><option value="name_asc">名称 A-Z</option></select>
    <select id="source"><option value="">全部来源</option></select>
    <button id="reset">重置</button>
  </div>
  <div class="toggles"><label><input id="contactOnly" type="checkbox" /> 只看有联系方式</label><label><input id="sponsorOnly" type="checkbox" /> 只看有赞助/媒体页</label><label><input id="hideCompetitors" type="checkbox" checked /> 隐藏竞品/参考站标记</label></div>
  <div class="table-wrap"><table><thead><tr><th>排名</th><th>渠道</th><th>类型</th><th>主题/最近内容</th><th>订阅/粉丝</th><th>分数</th><th>来源</th><th>联系方式</th><th>赞助页</th><th>建议合作方式</th></tr></thead><tbody id="tbody"></tbody></table></div>
</section>
<section class="section card"><div style="padding:18px"><div class="section-title">评分规则</div><div class="chips" style="margin-top:12px"><span class="chip">受众匹配 30</span><span class="chip">内容相关 20</span><span class="chip">活跃度 15</span><span class="chip">赞助准备度 10</span><span class="chip">可联系性 10</span><span class="chip">影响力 10</span><span class="chip">长期搜索价值 5</span></div><div class="footer">缺失字段显示为 Unknown。工具不会猜测邮箱、价格、订阅数、受众结构或私密信息，也不会自动联系任何渠道。</div></div></section>
</div>
<script>
const DATA=__CHANNEL_DATA__;
const SUMMARY=__SUMMARY_DATA__;
const weights={audience_match:30,content_fit:20,activity:15,sponsorship_readiness:10,contactability:10,authority_reach:10,long_term_search_value:5};
const scoreLabels={audience_match:'受众匹配',content_fit:'内容相关',activity:'活跃度',sponsorship_readiness:'赞助准备度',contactability:'可联系性',authority_reach:'影响力/覆盖',long_term_search_value:'长期搜索价值'};
let expanded=null;
function val(x){return x===undefined||x===null||x===''?'Unknown':x}
function known(x){return !(x===undefined||x===null||x===''||x==='Unknown')}
function esc(s){return String(val(s)).replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]))}
function link(url,text){return known(url)?`<a href="${esc(url)}" target="_blank" rel="noopener">${esc(text||url)}</a>`:'Unknown'}
function cn(s){return String(val(s))
.replaceAll('matches AI agent / LLM workflow topics','匹配 AI Agent / LLM 工作流主题')
.replaceAll('matches developer and data API audience','匹配开发者和数据 API 受众')
.replaceAll('matches SEO and search data use cases','匹配 SEO 和搜索数据场景')
.replaceAll('has a public contact path','有公开联系路径')
.replaceAll('has sponsorship or media kit signal','有赞助或 media kit 信号')
.replaceAll('has partial relevance but needs manual validation','有一定相关性，需要人工确认')
.replaceAll('Sponsored technical tutorial or newsletter placement featuring','赞助技术教程或 Newsletter 露出，介绍') }
function isCompetitor(c){return String(c.notes||'').includes('competitor/reference')||String(c.notes||'').includes('竞品/参考站')||String(c.review_notes||'').includes('competitor/reference')||String(c.review_notes||'').includes('竞品/参考站')}
function contactHtml(c){if(known(c.contact_email))return esc(c.contact_email);if(known(c.contact_page))return link(c.contact_page,'联系页/主页');if(known(c.sponsor_page))return link(c.sponsor_page,'赞助/合作页');if(known(c.media_kit_url))return link(c.media_kit_url,'Media Kit');return link(c.url,'渠道主页')}
function hasContact(c){return known(c.contact_email)||known(c.contact_page)||known(c.sponsor_page)||known(c.media_kit_url)||known(c.url)}
function renderStats(){const total=DATA.length,contact=DATA.filter(hasContact).length,sponsor=DATA.filter(x=>known(x.sponsor_page)||known(x.media_kit_url)).length,seen=DATA.filter(x=>(Number(x.seen_count)||0)>1).length;const rows=[['渠道总数',total],['有联系方式',contact],['有赞助页/媒体包',sponsor],['重复出现渠道',seen]];document.getElementById('stats').innerHTML=rows.map(([a,b])=>`<div class="card stat"><div class="stat-value">${esc(b)}</div><div class="stat-label">${esc(a)}</div></div>`).join('');document.getElementById('latestRun').textContent=SUMMARY.latest_run_id||'Unknown'}
function renderOptions(){const types=[...new Set(DATA.map(x=>x.channel_type||x.platform||'Unknown'))].sort();document.getElementById('type').innerHTML='<option value="">全部类型</option>'+types.map(x=>`<option>${esc(x)}</option>`).join('');const sources=[...new Set(DATA.flatMap(x=>String(x.source_provider||'Unknown').split(',').map(s=>s.trim()).filter(Boolean)))].sort();document.getElementById('source').innerHTML='<option value="">全部来源</option>'+sources.map(x=>`<option>${esc(x)}</option>`).join('')}
function filtered(){const q=document.getElementById('q').value.toLowerCase(),type=document.getElementById('type').value,source=document.getElementById('source').value,contactOnly=document.getElementById('contactOnly').checked,sponsorOnly=document.getElementById('sponsorOnly').checked,hideCompetitors=document.getElementById('hideCompetitors').checked,sort=document.getElementById('sort').value;let rows=DATA.filter(c=>{const text=[c.name,c.topic,c.audience,c.score_reason,c.recommended_collaboration,c.notes,c.source_keyword,c.source_provider,c.contact_email,c.contact_page,c.sponsor_page,c.media_kit_url,c.url].join(' ').toLowerCase();if(q&&!text.includes(q))return false;if(type&&(c.channel_type||c.platform)!==type)return false;if(source&&!String(c.source_provider||'').split(',').map(s=>s.trim()).includes(source))return false;if(contactOnly&&!hasContact(c))return false;if(sponsorOnly&&!(known(c.sponsor_page)||known(c.media_kit_url)))return false;if(hideCompetitors&&isCompetitor(c))return false;return true});if(sort==='seen_desc')rows.sort((a,b)=>(Number(b.seen_count)||0)-(Number(a.seen_count)||0)||(Number(b.fit_score)||0)-(Number(a.fit_score)||0));else if(sort==='name_asc')rows.sort((a,b)=>String(a.name||'').localeCompare(String(b.name||'')));else rows.sort((a,b)=>(Number(b.fit_score)||0)-(Number(a.fit_score)||0));return rows}
function renderTable(){const rows=filtered(),body=document.getElementById('tbody');if(!rows.length){body.innerHTML='<tr><td colspan="10"><div class="empty">当前筛选条件下没有渠道。</div></td></tr>';return}body.innerHTML=rows.map((c,i)=>{const key=String(c.dedupe_key||c.rank||i);return `<tr class="data-row" onclick="toggle('${esc(key)}')"><td>${esc(c.rank||i+1)}</td><td class="name-cell">${link(c.url,c.name)}<div class="small">${esc(c.platform)} · ${esc(c.domain)}</div></td><td>${esc(c.channel_type)}</td><td>${esc(c.topic)}</td><td>${esc(c.subscribers_or_followers)}</td><td><span class="score">${esc(c.fit_score)}</span></td><td>${esc(c.source_provider)}<div class="small">出现 ${esc(c.seen_count||1)} 次</div></td><td>${contactHtml(c)}</td><td>${known(c.sponsor_page)?link(c.sponsor_page,'赞助页'):link(c.media_kit_url,'Media Kit')}</td><td>${esc(cn(c.recommended_collaboration))}</td></tr>${expanded===key?detail(c):''}`}).join('')}
function detail(c){const b=c.score_breakdown||{},bars=Object.keys(weights).map(k=>{const v=Number(b[k]||0),pct=Math.max(0,Math.min(100,v/weights[k]*100));return `<div class="bar-row"><div class="small">${scoreLabels[k]}</div><div class="bar"><span style="width:${pct}%"></span></div><div class="small">${v}/${weights[k]}</div></div>`}).join('');const missing=(c.missing_fields||[]).length?c.missing_fields.map(x=>`<span class="chip">${esc(x)}</span>`).join(''):'<span class="chip ok">无</span>';return `<tr class="detail-row"><td colspan="10"><div class="detail"><div class="box"><h4>评分明细</h4><div class="bars">${bars}</div></div><div class="box"><h4>渠道信息</h4><p><b>评分原因：</b>${esc(cn(c.score_reason))}</p><p><b>建议动作：</b>${esc(cn(c.recommended_collaboration))}</p><p><b>联系方式：</b>${contactHtml(c)}</p><p><b>来源：</b>${esc(c.source_provider)} · ${link(c.source_url,'来源链接')} · ${esc(c.source_keyword)}</p><p><b>最近活跃：</b>${esc(c.recent_activity)}</p><p><b>缺失信息：</b></p><div class="chips">${missing}</div><p class="small"><b>备注：</b>${esc(cn(c.notes||'Unknown'))}</p></div></div></td></tr>`}
function toggle(key){expanded=expanded===String(key)?null:String(key);renderTable()}
['q','type','source','sort','contactOnly','sponsorOnly','hideCompetitors'].forEach(id=>document.getElementById(id).addEventListener('input',renderTable));document.getElementById('reset').addEventListener('click',()=>{['q','type','source'].forEach(id=>document.getElementById(id).value='');document.getElementById('sort').value='score_desc';document.getElementById('contactOnly').checked=false;document.getElementById('sponsorOnly').checked=false;document.getElementById('hideCompetitors').checked=true;expanded=null;renderTable()});
renderStats();renderOptions();renderTable();
</script>
</body>
</html>'''
    html_doc = (
        template
        .replace("__PRODUCT__", product)
        .replace("__GENERATED__", html.escape(generated_at))
        .replace("__CHANNEL_DATA__", json.dumps(candidates, ensure_ascii=False).replace("</", "<\\/"))
        .replace("__SUMMARY_DATA__", json.dumps(summary, ensure_ascii=False).replace("</", "<\\/"))
    )
    path.write_text(html_doc, encoding="utf-8")
