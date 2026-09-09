import os, sys, json, html, datetime, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from md2html import convert, esc

ROOT = '/Users/semi/cursor/payhug'
SPEC = os.path.join(ROOT, 'payhug-spec')

DOCS = [
    ('정책서', '00_README.md',            'payhug-spec/00_README.md',            '마스터 문서·부록'),
    ('정책서', '01_SERVICE_OVERVIEW.md',  'payhug-spec/01_SERVICE_OVERVIEW.md',  '서비스 개요'),
    ('정책서', '02_TERMS_AND_STATUS.md',  'payhug-spec/02_TERMS_AND_STATUS.md',  '용어·상태값'),
    ('정책서', '03_SETTLEMENT_LOGIC.md',  'payhug-spec/03_SETTLEMENT_LOGIC.md',  '정산 로직·산식'),
    ('정책서', '04_EXCEPTION_CASES.md',   'payhug-spec/04_EXCEPTION_CASES.md',   '예외 케이스'),
    ('정책서', '05_UI_REQUIREMENTS.md',   'payhug-spec/05_UI_REQUIREMENTS.md',   'UI 요구사항'),
    ('정책서', '06_ADMIN_AND_NOTIFICATION.md','payhug-spec/06_ADMIN_AND_NOTIFICATION.md','어드민·알림톡'),
    ('정책서', '07_OPEN_QUESTIONS.md',    'payhug-spec/07_OPEN_QUESTIONS.md',    '미확정 질문 7-1~7-32'),
    ('부속',   '00_종합.md',              'payhug-spec/analysis/00_종합.md',      '충돌 레지스터 C1~C6'),
    ('부속',   'PROGRESS.md',             'payhug-spec/PROGRESS.md',             '진행 상태'),
    ('판독',   'tickets.md',              'payhug-spec/_pipeline/jira_20260907/tickets.md', 'Jira Product 25건'),
    ('판독',   'figma_policy_EUK.md',     'payhug-spec/_pipeline/jira_20260907/figma_policy_EUK.md', 'Figma 정책 원문 전수'),
    ('판독',   'figma_operation_improvements.md','payhug-spec/_pipeline/jira_20260907/figma_operation_improvements.md','Figma 운영 개선건 16섹션'),
]

def git_date(rel):
    try:
        r = subprocess.run(['git','log','-1','--format=%ad','--date=format:%Y-%m-%d','--', rel],
                           cwd=ROOT, capture_output=True, text=True, timeout=10)
        return r.stdout.strip() or '미커밋'
    except Exception:
        return '?'

items = []
for group, name, rel, desc in DOCS:
    full = os.path.join(ROOT, rel)
    if not os.path.exists(full):
        continue
    raw = open(full, encoding='utf-8').read()
    body = convert(raw)
    st = os.stat(full)
    items.append({
        'group': group, 'name': name, 'rel': rel, 'desc': desc,
        'body': body,
        'lines': raw.count('\n') + 1,
        'kb': round(st.st_size / 1024),
        'mtime': datetime.datetime.fromtimestamp(st.st_mtime).strftime('%Y-%m-%d %H:%M'),
        'gitdate': git_date(rel),
        'plain': raw,
    })

stamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
branch = subprocess.run(['git','branch','--show-current'], cwd=ROOT, capture_output=True, text=True).stdout.strip()
origin = subprocess.run(['git','remote','get-url','origin'], cwd=ROOT, capture_output=True, text=True).stdout.strip()

nav_groups = {}
for idx, it in enumerate(items):
    nav_groups.setdefault(it['group'], []).append((idx, it))

nav = []
for g in ['정책서', '부속', '판독']:
    if g not in nav_groups: continue
    nav.append(f'<div class="navgroup">{g}</div>')
    for idx, it in nav_groups[g]:
        nav.append(
            f'<button class="navitem" data-i="{idx}">'
            f'<span class="nm">{esc(it["name"])}</span>'
            f'<span class="ds">{esc(it["desc"])}</span>'
            f'<span class="mt">{it["lines"]}줄 · {it["kb"]}KB</span>'
            f'</button>')
nav_html = '\n'.join(nav)

secs = []
for idx, it in enumerate(items):
    secs.append(
        f'<section class="doc" id="doc-{idx}" hidden>'
        f'<div class="pathbar">'
        f'<code class="p">{esc(os.path.join(ROOT, it["rel"]))}</code>'
        f'<span class="meta">{it["lines"]}줄 · {it["kb"]}KB · 수정 {it["mtime"]} · 커밋 {it["gitdate"]}</span>'
        f'</div>'
        f'<article class="md">{it["body"]}</article>'
        f'</section>')
secs_html = '\n'.join(secs)

search_index = json.dumps([{'i': i, 'n': it['name'], 't': it['plain']} for i, it in enumerate(items)], ensure_ascii=False)

CSS = """
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,'Apple SD Gothic Neo','Pretendard',sans-serif;
color:#1a1d21;background:#fff;-webkit-font-smoothing:antialiased}
#wrap{display:flex;min-height:100vh}
#side{width:290px;flex:0 0 290px;border-right:1px solid #e6e8eb;background:#fafbfc;
position:sticky;top:0;height:100vh;overflow-y:auto;padding:18px 0 40px}
#side h1{font-size:15px;margin:0 16px 4px;letter-spacing:-.2px}
#side .sub{font-size:11px;color:#8b9199;margin:0 16px 14px;line-height:1.5}
#side .sub code{font-size:10px;background:#eef0f2;padding:1px 4px;border-radius:3px}
#q{width:calc(100% - 32px);margin:0 16px 12px;padding:7px 10px;border:1px solid #d8dce0;
border-radius:7px;font-size:12.5px;font-family:inherit;background:#fff}
#q:focus{outline:none;border-color:#7FE141;box-shadow:0 0 0 3px rgba(127,225,65,.15)}
.navgroup{font-size:10.5px;font-weight:700;color:#9aa1a9;letter-spacing:.6px;margin:14px 16px 5px;text-transform:uppercase}
.navitem{display:block;width:calc(100% - 16px);margin:0 8px 1px;padding:8px 10px;border:0;background:none;
text-align:left;cursor:pointer;border-radius:7px;font-family:inherit;line-height:1.35}
.navitem:hover{background:#eef1f4}
.navitem.on{background:#1B2537}
.navitem.on .nm{color:#fff}.navitem.on .ds,.navitem.on .mt{color:#9fb0c9}
.navitem .nm{display:block;font-size:12.5px;font-weight:600;color:#2b3038}
.navitem .ds{display:block;font-size:11px;color:#7a828b;margin-top:1px}
.navitem .mt{display:block;font-size:10px;color:#a4abb3;margin-top:2px;font-variant-numeric:tabular-nums}
#main{flex:1;min-width:0;padding:26px 40px 100px;max-width:1080px}
.pathbar{display:flex;flex-wrap:wrap;gap:8px;align-items:baseline;justify-content:space-between;
padding:9px 13px;background:#f4f6f8;border:1px solid #e6e8eb;border-radius:8px;margin-bottom:22px}
.pathbar .p{font-size:11.5px;color:#3d5a80;word-break:break-all;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.pathbar .meta{font-size:11px;color:#8b9199;white-space:nowrap;font-variant-numeric:tabular-nums}
.md{font-size:14px;line-height:1.75;color:#22262b}
.md h1{font-size:23px;margin:0 0 18px;padding-bottom:10px;border-bottom:2px solid #1B2537;letter-spacing:-.4px}
.md h2{font-size:18px;margin:34px 0 12px;padding-top:14px;border-top:1px solid #eceef0;letter-spacing:-.3px}
.md h3{font-size:15.5px;margin:24px 0 9px;color:#2b3038}
.md h4{font-size:14px;margin:18px 0 7px;color:#4a5058}
.md h5,.md h6{font-size:13px;margin:14px 0 6px;color:#5a6068}
.md p{margin:9px 0}
.md ul,.md ol{margin:9px 0;padding-left:22px}
.md li{margin:3px 0}
.md code{background:#f0f2f4;padding:1.5px 5px;border-radius:4px;font-size:12.5px;
font-family:ui-monospace,SFMono-Regular,Menlo,monospace;color:#b0384a}
.md pre.code{background:#1B2537;color:#e6edf3;padding:13px 15px;border-radius:8px;overflow-x:auto;font-size:12.5px;line-height:1.6}
.md pre.code code{background:none;color:inherit;padding:0;font-size:12.5px}
.md blockquote{margin:11px 0;padding:9px 15px;border-left:3px solid #7FE141;background:#f7fdf3;color:#2f3a2a;font-size:13.5px}
.md hr{border:0;border-top:1px solid #e6e8eb;margin:26px 0}
.tw{overflow-x:auto;margin:13px 0;border:1px solid #e2e5e8;border-radius:8px}
.md table{border-collapse:collapse;width:100%;font-size:12.8px;background:#fff}
.md th{background:#f4f6f8;text-align:left;padding:8px 11px;font-weight:700;
border-bottom:1px solid #e2e5e8;white-space:nowrap;color:#3a4048}
.md td{padding:7px 11px;border-bottom:1px solid #f0f2f4;vertical-align:top;line-height:1.6}
.md tbody tr:last-child td{border-bottom:0}
.md tbody tr:hover{background:#fafbfc}
.md strong{font-weight:700;color:#111}
.md a{color:#2f6fd0}
mark{background:#ffe98a;padding:0 2px;border-radius:2px}
#hits{margin:0 8px 6px;font-size:11px;color:#7a828b}
#hits .hit{display:block;width:100%;text-align:left;border:0;background:none;padding:4px 8px;
border-radius:6px;cursor:pointer;font-family:inherit;font-size:11.5px;color:#3d5a80}
#hits .hit:hover{background:#eef1f4}
@media (max-width:900px){#wrap{flex-direction:column}#side{width:100%;height:auto;position:static;flex:none}#main{padding:20px}}
"""

JS = """
const IDX = __INDEX__;
const nav = document.querySelectorAll('.navitem');
const docs = document.querySelectorAll('.doc');
function show(i){
  docs.forEach(d=>d.hidden=true);
  nav.forEach(n=>n.classList.remove('on'));
  const d=document.getElementById('doc-'+i); if(d) d.hidden=false;
  const n=document.querySelector('.navitem[data-i="'+i+'"]'); if(n) n.classList.add('on');
  window.scrollTo(0,0);
  try{ localStorage.setItem('ph_doc', i); }catch(e){}
  if(history.replaceState) history.replaceState(null,'','#doc-'+i);
}
nav.forEach(n=>n.addEventListener('click',()=>show(n.dataset.i)));
let start=0;
const hm=(location.hash||'').match(/^#doc-(\d+)$/);
if(hm && document.getElementById('doc-'+hm[1])){ start=hm[1]; }
else { try{ const s=localStorage.getItem('ph_doc'); if(s!==null && document.getElementById('doc-'+s)) start=s; }catch(e){} }
show(start);
window.addEventListener('hashchange',()=>{
  const m=(location.hash||'').match(/^#doc-(\d+)$/);
  if(m && document.getElementById('doc-'+m[1])) show(m[1]);
});

const q=document.getElementById('q'), hits=document.getElementById('hits');
function clearMarks(){
  document.querySelectorAll('mark').forEach(m=>{
    const t=document.createTextNode(m.textContent); m.parentNode.replaceChild(t,m);
  });
}
function markIn(root, term){
  const rx=new RegExp(term.replace(/[.*+?^${}()|[\\]\\\\]/g,'\\\\$&'),'gi');
  const walk=document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  const targets=[]; let node;
  while(node=walk.nextNode()){ if(node.nodeValue.match(rx)) targets.push(node); }
  targets.forEach(t=>{
    const span=document.createElement('span');
    span.innerHTML=t.nodeValue.replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]))
      .replace(rx,m=>'<mark>'+m+'</mark>');
    t.parentNode.replaceChild(span,t);
  });
}
q.addEventListener('input',()=>{
  const term=q.value.trim();
  clearMarks(); hits.innerHTML='';
  if(term.length<2) return;
  const rx=new RegExp(term.replace(/[.*+?^${}()|[\\]\\\\]/g,'\\\\$&'),'gi');
  const rows=IDX.map(d=>({i:d.i,n:d.n,c:(d.t.match(rx)||[]).length})).filter(r=>r.c>0)
    .sort((a,b)=>b.c-a.c);
  if(!rows.length){ hits.textContent='결과 없음'; return; }
  rows.forEach(r=>{
    const b=document.createElement('button');
    b.className='hit'; b.textContent=r.n+' · '+r.c+'건';
    b.onclick=()=>{ show(r.i); setTimeout(()=>{
      const d=document.getElementById('doc-'+r.i); markIn(d, term);
      const m=d.querySelector('mark'); if(m) m.scrollIntoView({block:'center'});
    },0); };
    hits.appendChild(b);
  });
});
"""

out = f"""<title>PayHug 정책서</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>{CSS}</style>
<div id="wrap">
<aside id="side">
  <h1>PayHug 정책서</h1>
  <p class="sub">{esc(ROOT)}<br><code>{esc(origin)}</code><br>브랜치 {esc(branch)} · {stamp} 기준</p>
  <input id="q" placeholder="전체 문서 검색 (2자 이상)" autocomplete="off">
  <div id="hits"></div>
  {nav_html}
</aside>
<main id="main">
{secs_html}
</main>
</div>
<script>{JS.replace('__INDEX__', search_index)}</script>
"""

dst = sys.argv[1]
open(dst, 'w', encoding='utf-8').write(out)
print('생성:', dst)
print('문서:', len(items), '개 ·', round(len(out)/1024), 'KB')
for it in items:
    print(f"  {it['group']:4} {it['name']:36} {it['lines']:>5}줄  {it['kb']:>4}KB  커밋 {it['gitdate']}")
