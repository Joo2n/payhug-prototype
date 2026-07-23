// 기능명세 결과(spec_content.json) → 법조항식 계층(도메인→화면→기능) 단일 HTML.
// 좌측 계층 네비(도메인·화면 클릭 이동) + 경로 브레드크럼 + 번호체계 + 검색/필터/FAB.
const fs = require('fs')
const CONTENT = '/private/tmp/claude-501/-Users-semi-cursor-payhug/d08c4a93-21cd-4310-99c5-3c1fc6fa88f5/scratchpad/spec_content.json'
const OUT = '/Users/semi/cursor/payhug/payhug-spec/spec/기능명세서_어드민.html'

function esc(s) { return String(s == null ? '' : s) }
function attr(s) { return String(s == null ? '' : s).replace(/"/g, '&quot;') }
function renderV(v) {
  if (!v) return ''
  return String(v).split('\n').map(ln => {
    const t = ln.replace(/\s+$/, '')
    if (t === '') return ''
    if (/^\s*[–-]\s+/.test(t)) return `<span class="i">${esc(t.replace(/^\s*[–-]\s+/, ''))}</span>`
    return `<span class="l">${esc(t)}</span>`
  }).join('')
}
function pill(s) { const c = s === '확정' ? 'ok' : s === '가설' ? 'hy' : 'ck'; return `<span class="pill pill-${c}">${s}</span>` }
function permBadge(p) { if (!p) return ''; const c = p === '관리자 전용' ? 'a' : p === '관리자·페이허그' ? 'ap' : p === '파트너 조회' ? 'pt' : 'co'; return `<span class="pbadge pb-${c}">${esc(p)}</span>` }
function sub(label, v) { if (!v || !String(v).trim()) return ''; return `<div class="sc"><span class="scl">${label}</span><div class="scv">${renderV(v)}</div></div>` }
function plain(v) { return String(v || '').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim() }

const data = JSON.parse(fs.readFileSync(CONTENT, 'utf8'))
const domains = (data.domains || data).filter(Boolean)

// 통계
let totFeat = 0, cnt = { '확정': 0, '가설': 0, '확인필요': 0 }
const perms = new Set(), allScreens = new Set()
for (const d of domains) for (const f of (d.features || [])) { totFeat++; cnt[f.status] = (cnt[f.status] || 0) + 1; if (f.permission) perms.add(f.permission); if (f.screen) allScreens.add(f.screen) }
const PERM_ORDER = ['관리자 전용', '관리자·페이허그', '파트너 조회', '공통']
const permList = PERM_ORDER.filter(p => perms.has(p))
const screenList = Array.from(allScreens).sort()

// 도메인 짧은 라벨(브레드크럼용): "정산 — ..." → "정산 ..."의 앞부분
function shortDom(label) { return String(label).split('—')[0].trim() }

// 도메인 내 화면별 그룹핑(등장 순서 보존)
function groupByScreen(feats) {
  const order = [], map = {}
  for (const f of feats) {
    const sc = f.screen || '기타'
    if (!map[sc]) { map[sc] = []; order.push(sc) }
    map[sc].push(f)
  }
  return order.map(sc => ({ screen: sc, feats: map[sc] }))
}

// 본문 + 네비 생성
let navHtml = '', bodyHtml = ''
domains.forEach((d, di) => {
  const dn = di + 1
  const groups = groupByScreen(d.features || [])
  const dShort = shortDom(d.label)
  // 네비: 도메인 + 화면 하위
  navHtml += `<div class="nav-dom"><a href="#d${dn}" class="nav-d"><span class="nav-n">${dn}</span>${esc(d.label)}<span class="nav-c">${(d.features || []).length}</span></a>` +
    `<div class="nav-scrs">` + groups.map((g, si) => `<a href="#d${dn}-${si + 1}" class="nav-s">${dn}.${si + 1} ${esc(g.screen)}<span class="nav-sc">${g.feats.length}</span></a>`).join('') + `</div></div>`

  // 본문: 장
  bodyHtml += `<section id="d${dn}" class="chap" data-menu="${attr(d.label)}">
    <div class="chap-h"><span class="chap-n">${dn}</span><h2>${esc(d.label)}</h2><span class="chap-cnt">${(d.features || []).length}개 기능 · ${groups.length}개 화면</span></div>
    ${d.intro ? `<p class="chap-intro">${esc(d.intro)}</p>` : ''}`
  // 절(화면)
  groups.forEach((g, si) => {
    const sn = `${dn}.${si + 1}`
    bodyHtml += `<section id="d${dn}-${si + 1}" class="scr" data-screen="${attr(g.screen)}"><div class="scr-h"><span class="scr-n">${sn}</span><h3>${esc(g.screen)}</h3><span class="scr-cnt">${g.feats.length}개</span></div>`
    // 조(기능)
    g.feats.forEach((f, fi) => {
      const fn = `${sn}.${fi + 1}`
      const text = [f.name, f.what, f.logic, f.settings, f.data, f.notes, g.screen, f.permission].map(plain).join(' ').toLowerCase()
      bodyHtml += `<article class="feat" data-menu="${attr(d.label)}" data-screen="${attr(g.screen)}" data-perm="${attr(f.permission || '공통')}" data-text="${attr(text)}">
        <div class="feat-crumb">${esc(dShort)} <span class="sep">›</span> ${esc(g.screen)}</div>
        <div class="feat-h"><span class="feat-n">${fn}</span><span class="feat-nm">${esc(f.name)}</span>${pill(f.status)}${permBadge(f.permission)}</div>
        ${f.what ? `<div class="feat-what">${renderV(f.what)}</div>` : ''}
        ${sub('로직·계산', f.logic)}${sub('설정·연결', f.settings)}${sub('데이터 출처', f.data)}${sub('정책·주의', f.notes)}
      </article>`
    })
    bodyHtml += `</section>`
  })
  // 도메인 코드근거
  const cites = (d.citations || []).slice(0, 40).map(c => `<span class="cite"><b>${esc(c.claim)}</b> <code>${esc(c.ref)}</code></span>`).join('')
  if (cites) bodyHtml += `<details class="cites"><summary>${dn}장 코드 근거 ${(d.citations || []).length}건</summary><div class="cites-body">${cites}</div></details>`
  bodyHtml += `</section>`
})

const permChips = `<button class="chip chip-on" data-perm="__all">전체 권한</button>` + permList.map(p => `<button class="chip" data-perm="${attr(p)}">${esc(p)}</button>`).join('')
const screenOpts = `<option value="__all">화면 전체 (${screenList.length})</option>` + screenList.map(s => `<option value="${attr(s)}">${esc(s)}</option>`).join('')

const html = `<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>PayHug 어드민 프론트 기능명세서</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#f7f7f9;--card:#fff;--ink:#1b1c21;--sub:#5c5d64;--line:#e7e8ec;--pri:#4b47d6;--pri2:#7c3aed}
body{font-family:'Apple SD Gothic Neo','Malgun Gothic',-apple-system,sans-serif;color:var(--ink);background:var(--bg);line-height:1.62}
.wrap{display:flex;max-width:1560px;margin:0 auto;align-items:flex-start}
/* 좌측 계층 네비 */
.side{position:sticky;top:0;height:100vh;width:340px;flex-shrink:0;background:#14151a;color:#e9eaf0;overflow-y:auto;padding:20px 0}
.side-h{padding:0 20px 14px;border-bottom:1px solid #2a2b33;margin-bottom:8px}
.side-h .logo{font-size:19px;font-weight:800;letter-spacing:-.4px}
.side-h .logo i{color:#2ac06d;font-style:normal}
.side-h .st{font-size:12px;color:#9a9ba5;margin-top:5px}
.side-h .meta{font-size:11px;color:#77787f;margin-top:7px}
.nav-dom{border-bottom:1px solid #202127}
.nav-d{display:flex;align-items:center;gap:8px;padding:9px 20px;font-size:13px;font-weight:700;color:#dcdde5;text-decoration:none}
.nav-d:hover{background:#1f2027;color:#fff}
.nav-d.on{background:#1f2027;color:#fff}
.nav-d .nav-n{font-size:11px;font-weight:800;color:var(--pri);min-width:15px}
.nav-d .nav-c{margin-left:auto;font-size:10px;background:#2a2b33;color:#a9aab3;border-radius:9px;padding:1px 7px}
.nav-scrs{display:none;padding:2px 0 6px}
.nav-dom.open .nav-scrs{display:block}
.nav-s{display:flex;align-items:center;gap:6px;padding:5px 20px 5px 43px;font-size:12px;color:#9fa0aa;text-decoration:none}
.nav-s:hover{color:#fff;background:#191a20}
.nav-s.on{color:#fff}
.nav-s .nav-sc{margin-left:auto;font-size:9.5px;color:#6b6c75}
.legend{padding:12px 20px 4px;border-top:1px solid #2a2b33;margin-top:8px}
.legend .lt{font-size:11px;color:#77787f;margin-bottom:7px}
.legend .lg{display:flex;align-items:center;gap:7px;font-size:11.5px;color:#c7c8d2;margin-bottom:5px}
.legend .dot{width:9px;height:9px;border-radius:3px}
/* 본문 */
.main{flex:1;min-width:0;padding:34px 44px 120px}
.doc-h h1{font-size:28px;font-weight:800;letter-spacing:-.6px}
.doc-h .sub{color:var(--sub);font-size:14px;margin-top:8px;line-height:1.7;max-width:900px}
.stat{display:flex;gap:9px;margin:18px 0 18px;flex-wrap:wrap}
.stat .s{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 16px;min-width:96px}
.stat .s .n{font-size:20px;font-weight:800;color:var(--pri)}
.stat .s .lb{font-size:11.5px;color:var(--sub);margin-top:1px}
.stat .s.ok .n{color:#1f9d55}.stat .s.hy .n{color:#c07d15}.stat .s.ck .n{color:#d83a3a}
/* 컨트롤바 */
.ctrl{position:sticky;top:0;z-index:20;background:rgba(247,247,249,.95);backdrop-filter:blur(6px);padding:10px 0 12px;margin-bottom:6px;border-bottom:1px solid var(--line)}
.searchbox{display:flex;align-items:center;gap:8px;background:#fff;border:1.5px solid var(--line);border-radius:11px;padding:9px 13px}
.searchbox:focus-within{border-color:var(--pri)}
.searchbox svg{width:17px;height:17px;fill:#9a9ba5;flex-shrink:0}
.searchbox input{border:none;outline:none;font-size:14.5px;flex:1;background:transparent;color:var(--ink)}
.searchbox .clr{cursor:pointer;color:#b0b2b8;font-size:18px;padding:0 4px;display:none}
.filters{display:flex;gap:12px;align-items:center;margin-top:10px;flex-wrap:wrap}
.chips{display:flex;gap:6px;flex-wrap:wrap}
.chip{font-size:12px;font-weight:700;border:1px solid var(--line);background:#fff;color:#54555c;border-radius:15px;padding:4px 11px;cursor:pointer}
.chip-on{background:var(--pri);color:#fff;border-color:var(--pri)}
.fsel{font-size:12px;font-weight:700;border:1px solid var(--line);background:#fff;color:#54555c;border-radius:8px;padding:5px 9px;cursor:pointer;max-width:240px}
.rescount{font-size:12px;color:var(--sub);margin-left:auto}
/* 장(도메인) */
.chap{margin-bottom:20px;scroll-margin-top:110px}
.chap.hide{display:none}
.chap-h{display:flex;align-items:baseline;gap:11px;padding-bottom:9px;border-bottom:2.5px solid var(--ink);margin-bottom:4px}
.chap-n{font-size:19px;font-weight:800;color:var(--pri);font-variant-numeric:tabular-nums}
.chap-h h2{font-size:20px;font-weight:800;letter-spacing:-.4px}
.chap-cnt{margin-left:auto;font-size:11.5px;color:var(--sub)}
.chap-intro{color:var(--sub);font-size:13.5px;margin:11px 0 14px;line-height:1.72;max-width:940px}
/* 절(화면) */
.scr{margin:0 0 8px;scroll-margin-top:110px}
.scr.hide{display:none}
.scr-h{display:flex;align-items:baseline;gap:9px;position:sticky;top:78px;background:var(--bg);padding:12px 0 7px;z-index:5;border-bottom:1px solid #dcdde3}
.scr-n{font-size:14px;font-weight:800;color:var(--pri2);font-variant-numeric:tabular-nums}
.scr-h h3{font-size:16.5px;font-weight:800;color:#232429}
.scr-cnt{margin-left:auto;font-size:11px;color:#9a9ba5}
/* 조(기능) — 법조항식 들여쓰기 */
.feat{padding:13px 0 13px 18px;border-left:2px solid #ececeF;margin-left:4px}
.feat:hover{border-left-color:#c7c6f0}
.feat.hide{display:none}
.feat-crumb{font-size:11px;color:#a3a4ac;margin-bottom:3px}
.feat-crumb .sep{color:#c7c8ce}
.feat-h{display:flex;align-items:baseline;gap:8px;margin-bottom:5px;flex-wrap:wrap}
.feat-n{font-size:13px;font-weight:800;color:#8688d8;font-variant-numeric:tabular-nums;min-width:36px}
.feat-nm{font-size:15.5px;font-weight:800;color:var(--ink)}
.feat-what{font-size:13.5px;color:#33343a;line-height:1.68;margin:0 0 7px 44px}
.sc{display:flex;gap:0;margin:0 0 3px 44px;padding:5px 0}
.scl{width:88px;flex-shrink:0;font-size:11.5px;font-weight:800;color:#9698a0;padding-top:1px}
.sc:nth-child(odd) .scl{}
.scv{flex:1;font-size:13px;color:#2f3036;line-height:1.68}
.scv .l{display:block}
.scv .i{display:block;padding-left:14px;position:relative;color:#55565c}
.scv .i:before{content:"–";position:absolute;left:1px;color:#b6b7bd}
.scv b{color:#0f0f12;font-weight:800}
.pill{font-size:10.5px;font-weight:800;border-radius:5px;padding:1px 7px;white-space:nowrap}
.pill-ok{background:#e5f6ec;color:#1f9d55}.pill-hy{background:#fdf3e0;color:#c07d15}.pill-ck{background:#fde8e8;color:#d83a3a}
.pbadge{font-size:10px;font-weight:800;border-radius:5px;padding:1px 6px;white-space:nowrap}
.pb-a{background:#efeafe;color:#6b46e0}.pb-ap{background:#e9eefe;color:#3a5bd0}.pb-pt{background:#e6f6f2;color:#0e9f8e}.pb-co{background:#eef0f2;color:#6b6c75}
.cites{margin:6px 0 0 4px}
.cites summary{font-size:11.5px;color:#8a8b92;cursor:pointer;font-weight:700}
.cites-body{padding-top:8px}
.cites .cite{display:inline-block;font-size:10.5px;color:#55565c;background:#eef0f2;border-radius:5px;padding:2px 8px;margin:0 5px 5px 0}
.cites .cite b{color:#3a3b42;font-weight:700}
.cites code{font-family:ui-monospace,Menlo,monospace;color:var(--pri2);font-size:10px}
.nomatch{display:none;text-align:center;color:var(--sub);font-size:15px;padding:60px 0}
.nomatch.show{display:block}
.fab{position:fixed;right:26px;bottom:26px;z-index:40;width:54px;height:54px;border-radius:50%;background:var(--pri);border:none;box-shadow:0 6px 18px rgba(75,71,214,.42);cursor:pointer;display:flex;align-items:center;justify-content:center}
.fab svg{width:23px;height:23px;fill:#fff}
.fab:active{transform:scale(.94)}
@media(max-width:900px){.side{display:none}.main{padding:20px 15px 90px}.scr-h{top:70px}}
</style></head><body>
<div class="wrap">
  <aside class="side">
    <div class="side-h">
      <div class="logo">Pay<i>hug</i> 기능명세서</div>
      <div class="st">어드민 프론트 · 코드 기반</div>
      <div class="meta">${domains.length}개 도메인 · ${screenList.length}개 화면 · ${totFeat}개 기능</div>
    </div>
    <nav id="nav">${navHtml}</nav>
    <div class="legend">
      <div class="lt">표기</div>
      <div class="lg"><span class="dot" style="background:#1f9d55"></span>확정 — 코드 근거 명확</div>
      <div class="lg"><span class="dot" style="background:#c07d15"></span>가설 — 정황상 추정</div>
      <div class="lg"><span class="dot" style="background:#d83a3a"></span>확인필요 — 서버/정책 확정 필요</div>
    </div>
  </aside>
  <main class="main">
    <div class="doc-h">
      <h1>PayHug 어드민 프론트 기능명세서</h1>
      <div class="sub">어드민 프론트 코드를 <b>도메인(장) → 화면(절) → 기능(조)</b> 계층으로 정리한 명세서입니다. 각 기능은 <b>확정 / 가설 / 확인필요</b>로 구분하며, 서버(백엔드)에서만 확정되는 값은 <b>확인필요</b>로 남겼습니다. 좌측에서 도메인·화면을 눌러 이동하고, 검색·권한/화면 필터로 좁힐 수 있습니다.</div>
    </div>
    <div class="stat">
      <div class="s"><div class="n">${domains.length}</div><div class="lb">도메인</div></div>
      <div class="s"><div class="n">${screenList.length}</div><div class="lb">화면</div></div>
      <div class="s"><div class="n">${totFeat}</div><div class="lb">기능</div></div>
      <div class="s ok"><div class="n">${cnt['확정']}</div><div class="lb">확정</div></div>
      <div class="s hy"><div class="n">${cnt['가설']}</div><div class="lb">가설</div></div>
      <div class="s ck"><div class="n">${cnt['확인필요']}</div><div class="lb">확인필요</div></div>
    </div>
    <div class="ctrl">
      <div class="searchbox">
        <svg viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27a6.5 6.5 0 1 0-.7.7l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0A4.5 4.5 0 1 1 14 9.5 4.5 4.5 0 0 1 9.5 14z"/></svg>
        <input id="q" type="text" placeholder="기능·로직·화면·정책 검색 (예: 락계좌, 차액, 예상지급, 승인)">
        <span class="clr" id="clr">&times;</span>
      </div>
      <div class="filters">
        <div class="chips" id="permChips">${permChips}</div>
        <select class="fsel" id="screenSel">${screenOpts}</select>
        <span class="rescount" id="rescount">${totFeat}개 기능</span>
      </div>
    </div>
    ${bodyHtml}
    <div class="nomatch" id="nomatch">검색·필터 결과가 없습니다.</div>
  </main>
</div>
<button class="fab" id="fab" title="검색"><svg viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27a6.5 6.5 0 1 0-.7.7l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0A4.5 4.5 0 1 1 14 9.5 4.5 4.5 0 0 1 9.5 14z"/></svg></button>
<script>
(function(){
  var q=document.getElementById('q'), clr=document.getElementById('clr'), screenSel=document.getElementById('screenSel'),
      rescount=document.getElementById('rescount'), nomatch=document.getElementById('nomatch'), fab=document.getElementById('fab');
  var feats=[].slice.call(document.querySelectorAll('.feat'));
  var chaps=[].slice.call(document.querySelectorAll('.chap'));
  var scrs=[].slice.call(document.querySelectorAll('.scr'));
  var chips=[].slice.call(document.querySelectorAll('#permChips .chip'));
  var doms=[].slice.call(document.querySelectorAll('.nav-dom'));
  var perm='__all';
  function apply(){
    var term=(q.value||'').trim().toLowerCase(), scr=screenSel.value;
    clr.style.display=term?'block':'none';
    var vis=0;
    feats.forEach(function(f){
      var ok=true;
      if(term && f.getAttribute('data-text').indexOf(term)<0) ok=false;
      if(ok && perm!=='__all' && f.getAttribute('data-perm')!==perm) ok=false;
      if(ok && scr!=='__all' && f.getAttribute('data-screen')!==scr) ok=false;
      f.classList.toggle('hide',!ok); if(ok)vis++;
    });
    scrs.forEach(function(s){ s.classList.toggle('hide', s.querySelectorAll('.feat:not(.hide)').length===0); });
    chaps.forEach(function(c){ c.classList.toggle('hide', c.querySelectorAll('.feat:not(.hide)').length===0); });
    rescount.textContent=vis+'개 기능';
    nomatch.classList.toggle('show',vis===0);
  }
  q.addEventListener('input',apply);
  clr.addEventListener('click',function(){q.value='';q.focus();apply();});
  screenSel.addEventListener('change',apply);
  chips.forEach(function(c){c.addEventListener('click',function(){chips.forEach(function(x){x.classList.remove('chip-on')});c.classList.add('chip-on');perm=c.getAttribute('data-perm');apply();});});
  fab.addEventListener('click',function(){window.scrollTo({top:0,behavior:'smooth'});setTimeout(function(){q.focus()},300);});
  // 네비: 도메인 클릭 시 화면 하위 펼침(아코디언), 현재 위치 하이라이트
  doms.forEach(function(dm){ var d=dm.querySelector('.nav-d'); d.addEventListener('click',function(){ doms.forEach(function(x){if(x!==dm)x.classList.remove('open')}); dm.classList.toggle('open'); }); });
  var navD=[].slice.call(document.querySelectorAll('.nav-d'));
  var navS=[].slice.call(document.querySelectorAll('.nav-s'));
  window.addEventListener('scroll',function(){
    var y=window.scrollY+130, curC=-1, curS=-1;
    chaps.forEach(function(c,i){ if(!c.classList.contains('hide') && c.offsetTop<=y) curC=i; });
    scrs.forEach(function(s,i){ if(!s.classList.contains('hide') && s.offsetTop<=y) curS=i; });
    navD.forEach(function(n,i){n.classList.toggle('on', navD[curC] && n.getAttribute('href')===navD[curC].getAttribute('href'));});
    // 현재 장의 화면 하위 펼침
    doms.forEach(function(dm,i){ if(navD[curC] && dm.querySelector('.nav-d')===navD[curC]) dm.classList.add('open'); });
    navS.forEach(function(n,i){n.classList.toggle('on', navS[curS] && n.getAttribute('href')===navS[curS].getAttribute('href'));});
  },{passive:true});
  if(doms[0])doms[0].classList.add('open');
})();
</script>
</body></html>`

fs.writeFileSync(OUT, html)
const nScreens = domains.reduce((a, d) => a + groupByScreen(d.features || []).length, 0)
console.log('기능명세서(법조항식) 생성 →', OUT)
console.log('도메인', domains.length, '· 화면(절)', nScreens, '· 기능', totFeat)
