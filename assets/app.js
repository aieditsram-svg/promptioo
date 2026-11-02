(function(){
function el(tag,attrs,...kids){const e=document.createElement(tag);for(const k in(attrs||{})){if(k==='class')e.className=attrs[k];else if(k==='text')e.textContent=attrs[k];else e.setAttribute(k,attrs[k])}kids.flat().forEach(c=>c&&e.append(c));return e}
function parseCSV(t){const rows=[];let row=[],f='',q=false;for(let i=0;i<t.length;i++){const c=t[i];if(q){if(c==='"'){if(t[i+1]==='"'){f+='"';i++}else q=false}else f+=c}else if(c==='"')q=true;else if(c===','){row.push(f);f=''}else if(c==='\n'||c==='\r'){if(c==='\r'&&t[i+1]==='\n')i++;row.push(f);rows.push(row);row=[];f=''}else f+=c}
if(f!==''||row.length){row.push(f);rows.push(row)}return rows}
const CATEGORIES=['Men','Women','Kids','Couples','Others'];
const ALIAS={man:'Men',male:'Men',woman:'Women',female:'Women',kid:'Kids',child:'Kids',children:'Kids',couple:'Couples'};
function normCat(c){const k=(c||'').trim().toLowerCase();const hit=CATEGORIES.find(x=>x.toLowerCase()===k)||ALIAS[k];return hit||'Others'}
const slug=s=>s.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'')||'item';
async function load(){
  const r=await fetch('data/prompts.csv',{cache:'no-cache'});
  if(!r.ok)throw new Error('data/prompts.csv not found');
  const rows=parseCSV((await r.text()).replace(/^\uFEFF/,''));
  const head=rows.shift().map(h=>h.trim().toLowerCase().replace(/[\s-]+/g,'_'));
  const seen={};
  return rows.filter(r=>r.some(c=>c.trim())).map(r=>{
    const o={};head.forEach((h,i)=>o[h]=(r[i]||'').trim());
    let id=o.id||slug(o.title||'item');
    if(seen[id]){seen[id]++;id+='-'+seen[id]}else seen[id]=1;
    return{id,title:o.title||'Untitled',prompt:o.prompt||'',category:normCat(o.category),sub:o.category||'',
      keywords:(o.keywords||'').split(/[|,]/).map(s=>s.trim()).filter(Boolean),
      images:(o.image_urls||o.image_url||o.images||'').split(/[|\s]+/).filter(Boolean)};
  });
}
const catUrl=c=>'category.html?cat='+encodeURIComponent(c);
const kwUrl=k=>'index.html?q='+encodeURIComponent(k);
const viewUrl=i=>'viewer.html?id='+encodeURIComponent(i.id);
function card(i){return el('a',{class:'card',href:viewUrl(i)},el('img',{src:i.images[0]||'',alt:i.title,loading:'lazy'}),el('div',{class:'cap',text:i.title}))}
window.App={CATEGORIES,el,load,catUrl,kwUrl,viewUrl,card};
})();
