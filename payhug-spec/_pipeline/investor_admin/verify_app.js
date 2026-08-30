/* app.html 헤드리스 검증 — 창을 띄우지 않는다(--headless=new).
   1) 사이드바 메뉴 전건 전환  2) 상태 클릭 시퀀스 도달  3) 엑셀 4건 실제 다운로드
   4) 죽은 버튼 전수 스캔  5) 정렬·필터 값 변화  6) 콘솔 에러 0                         */
const http = require('http');
const fs   = require('fs');
const path = require('path');
const os   = require('os');
const { spawn } = require('child_process');

const REPO = '/Users/semi/cursor/payhug-investor-admin';
const OUTDIR = '/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin';
const PORT = 8700 + (process.pid % 90), DPORT = 9400 + (process.pid % 90);
const DL = fs.mkdtempSync(path.join(os.tmpdir(), 'phdl-'));
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const MIME = {'.html':'text/html; charset=utf-8', '.css':'text/css; charset=utf-8', '.js':'text/javascript',
  '.png':'image/png', '.xlsx':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'};

const server = http.createServer((req, res) => {
  const p = path.join(REPO, decodeURIComponent(req.url.split('?')[0]));
  fs.readFile(p, (e, b) => {
    if(e){ res.writeHead(404); res.end('nope'); return; }
    res.writeHead(200, {'Content-Type': MIME[path.extname(p)] || 'application/octet-stream'});
    res.end(b);
  });
});

let msgId = 0, ws, pending = new Map();
const consoleErrors = [];
function send(method, params){
  const id = ++msgId;
  ws.send(JSON.stringify({id, method, params: params || {}}));
  return new Promise((res, rej) => pending.set(id, {res, rej}));
}
async function evalJS(expr){
  const r = await send('Runtime.evaluate', {expression: '(function(){' + expr + '})()', returnByValue: true, awaitPromise: true});
  if(r.exceptionDetails) throw new Error('page eval: ' + JSON.stringify(r.exceptionDetails.exception && r.exceptionDetails.exception.description || r.exceptionDetails.text));
  return r.result.value;
}
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function main(){
  await new Promise(r => server.listen(PORT, r));
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'phprof-'));
  const chrome = spawn(CHROME, ['--headless=new', '--remote-debugging-port=' + DPORT,
    '--user-data-dir=' + profile, '--no-first-run', '--no-default-browser-check',
    '--disable-gpu', '--window-size=1440,1200', 'about:blank'], {stdio:'ignore'});

  let targets = null;
  for(let i = 0; i < 60 && !targets; i++){
    await sleep(300);
    try {
      targets = await new Promise((res, rej) => {
        http.get({host:'127.0.0.1', port:DPORT, path:'/json'}, r => {
          let d = ''; r.on('data', c => d += c); r.on('end', () => res(JSON.parse(d)));
        }).on('error', rej);
      });
    } catch(e){ targets = null; }
  }
  const page = targets.find(t => t.type === 'page');
  ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise(r => ws.addEventListener('open', r));
  ws.addEventListener('message', ev => {
    const m = JSON.parse(ev.data);
    if(m.id && pending.has(m.id)){ pending.get(m.id).res(m.result); pending.delete(m.id); return; }
    if(m.method === 'Runtime.consoleAPICalled' && (m.params.type === 'error' || m.params.type === 'warning'))
      consoleErrors.push(m.params.type + ': ' + m.params.args.map(a => a.value || a.description || a.type).join(' '));
    if(m.method === 'Runtime.exceptionThrown')
      consoleErrors.push('exception: ' + (m.params.exceptionDetails.exception && m.params.exceptionDetails.exception.description || m.params.exceptionDetails.text));
    if(m.method === 'Log.entryAdded' && m.params.entry.level === 'error')
      consoleErrors.push('log: ' + m.params.entry.text + ' ' + (m.params.entry.url || ''));
  });
  await send('Runtime.enable'); await send('Log.enable'); await send('Page.enable');
  await send('Browser.setDownloadBehavior', {behavior:'allow', downloadPath: DL});

  await send('Page.navigate', {url:'http://127.0.0.1:' + PORT + '/app.html'});
  await sleep(1800);

  const R = {menus:[], states:[], downloads:[], dead:[], data:[], selfcheck:null, console:[]};

  /* ── 자체 점검 ── */
  R.selfcheck = await evalJS('return window.__selfcheck();');

  /* ── 1) 사이드바 메뉴 전건 ──
     메뉴 수를 숫자로 박지 않는다. 사이드바에 실제로 걸린 .nav-item 을 세고,
     화면은 MENU_OF 를 뒤집어(메뉴 → 그 메뉴의 첫 화면) 가져온다. 메뉴가 늘면 검사도 저절로 늘어난다. */
  const MENUS = await evalJS(`
    var rev = {}, s;
    for(s in MENU_OF){ if(MENU_OF[s] && !(MENU_OF[s] in rev)) rev[MENU_OF[s]] = s; }
    var out = [];
    Array.prototype.forEach.call(document.querySelectorAll('.sidebar .nav-item[data-menu]'), function(a){
      if(a.getAttribute('target') === '_blank') return;      /* 외부 링크는 아래에서 따로 본다 */
      out.push([a.dataset.menu, rev[a.dataset.menu] || '', a.querySelector('span').textContent.trim()]);
    });
    return out;`);
  R.menuCount = await evalJS("return document.querySelectorAll('.sidebar .nav-item[data-menu]').length;");
  /* 쿠콘 관리 현금 — 메뉴를 누르면 중간 화면 없이 바로 We-bank 로 나간다.
     SPA 화면 전환이 아니므로 링크 자체(주소·새 창)를 본다. */
  const kc = await evalJS(
    'var a=document.querySelector(\'.nav-item[data-menu="kcoon"]\');' +
    'return {href:a.getAttribute("href"), target:a.getAttribute("target"), rel:a.getAttribute("rel"),' +
    ' label:a.textContent.trim()};');
  R.menus.push({menu:'kcoon', screen:'(외부)', label:'쿠콘 관리 현금', ...kc,
    pass: kc.href === 'https://www.we-bank.co.kr/main_00100.act' && kc.target === '_blank'
          && (kc.rel || '').indexOf('noopener') >= 0 && kc.label.indexOf('쿠콘 관리 현금') === 0});
  for(const [menu, screen, label] of MENUS){
    await evalJS('document.querySelector(\'.nav-item[data-menu="' + menu + '"]\').click(); return 1;');
    await sleep(150);
    const r = await evalJS(
      'var s=document.querySelector(\'section.screen[data-screen="' + screen + '"]\');' +
      'var nav=document.querySelector(\'.nav-item[data-menu="' + menu + '"]\');' +
      'var gl=nav.closest(".nav-group").querySelector(".nav-group-label");' +
      'return {active:document.body.dataset.active, visible:!s.hidden, state:s.dataset.state,' +
      ' hash:location.hash, bg:getComputedStyle(nav).backgroundColor, groupLabel:getComputedStyle(gl).color,' +
      ' pageShown:!document.querySelector(".page").hidden};');
    const ch = (r.bg.match(/[\d.]+/g) || []).map(Number);   /* .nav-item 에 transition 이 걸려 있어 알파가 1 미만으로 잡힐 수 있다 */
    const green = ch.length >= 3 && ch[0] === 127 && ch[1] === 225 && ch[2] === 65 && (ch.length < 4 || ch[3] >= 0.9);
    const gl = (r.groupLabel.match(/[\d.]+/g) || []).map(Number);
    const labelOn = gl.length >= 3 && gl[0] === 127 && gl[1] === 225 && gl[2] === 65;
    R.menus.push({menu, screen, label, ...r, green, labelOn,
      pass: r.active === menu && r.visible && r.pageShown && green && labelOn});
  }

  /* ── 2) 상태 전건: 실제 클릭 시퀀스 ── */
  const SEQ = [
    ['invest-assets','page2', [
      ['nav','.nav-item[data-menu="invest-assets"]'],
      ['click','[data-act="ia-page"][data-page="2"]']]],
    ['invest-assets','download', [
      ['nav','.nav-item[data-menu="invest-assets"]'],
      ['click','[data-mount="ia-xls-merchant"]'],
      ['wait', 600]]],
    ['invest-assets','cert-confirm', [
      ['nav','.nav-item[data-menu="invest-assets"]'],
      ['click','[data-act="cert-open"]']]],
    ['invest-assets','empty', [
      ['hash','#invest-assets/empty']]],
    ['invest-profit','weekly', [
      ['nav','.nav-item[data-menu="invest-returns"]'],
      ['click','[data-act="pf-gran"][data-gran="weekly"]'],
      ['click','[data-act="preset"][data-preset="w4"]']]],
    ['invest-profit','monthly', [
      ['nav','.nav-item[data-menu="invest-returns"]'],
      ['click','[data-act="pf-gran"][data-gran="monthly"]'],
      ['click','[data-act="preset"][data-preset="m6"]']]],
    ['invest-profit','empty', [
      ['nav','.nav-item[data-menu="invest-returns"]'],
      ['change','[data-mount="pf-from"]','2026-02-01'],
      ['change','[data-mount="pf-to"]','2026-02-07']]],
    ['merchants','filtered', [
      ['nav','.nav-item[data-menu="merchants"]'],
      ['change','[data-mount="mc-sector"]','음식점업'],
      ['type','[data-mount="mc-kw"]','곱창'],
      ['click','[data-act="mc-search"]']]],
    ['merchants','empty', [
      ['nav','.nav-item[data-menu="merchants"]'],
      ['type','[data-mount="mc-kw"]','라멘'],
      ['click','[data-act="mc-search"]']]],
    ['acquisition-list','doc', [
      ['nav','.nav-item[data-menu="receivables"]'],
      ['click','[data-act="aq-view"][data-i="0"]']]],
    ['acquisition-list','confirm', [
      ['nav','.nav-item[data-menu="receivables"]'],
      ['click','[data-act="aq-chk"][data-i="0"]'],
      ['click','[data-act="aq-chk"][data-i="1"]'],
      ['click','[data-act="aq-sign"]']]],
    ['acquisition-list','signing', [
      ['nav','.nav-item[data-menu="receivables"]'],
      ['click','[data-act="aq-chk"][data-i="0"]'],
      ['click','[data-act="aq-chk"][data-i="1"]'],
      ['click','[data-act="aq-sign"]'],
      ['click','[data-act="aq-sign-go"]']]],
    ['acquisition-list','done', [
      ['nav','.nav-item[data-menu="receivables"]'],
      ['click','[data-act="aq-chk"][data-i="0"]'],
      ['click','[data-act="aq-chk"][data-i="1"]'],
      ['click','[data-act="aq-sign"]'],
      ['click','[data-act="aq-sign-go"]'],
      ['wait', 1800]]],
    ['invest-sim','result', [
      ['nav','.nav-item[data-menu="invest-sim"]'],
      ['click','[data-mount="sim-go"]'],
      ['wait', 500]]],
    ['contracts','all', [
      ['nav','.nav-item[data-menu="contracts"]'],
      ['click','[data-act="ct-all"]']]],
    ['contracts','empty', [
      ['hash','#contracts/empty']]],
    ['password','weak', [
      ['nav','.nav-item[data-menu="password"]'],
      ['type','[data-mount="pw-new"]','12345678']]],
    ['password','error', [
      ['nav','.nav-item[data-menu="password"]'],
      ['type','[data-mount="pw-new"]','payhug!2026'],
      ['type','[data-mount="pw-cfm"]','payhug!2025']]],
    /* 세 칸 다 비어서 열린다(원본과 같다) — 현재 비밀번호까지 쳐 넣어야 제출이 열린다 */
    ['password','done', [
      ['nav','.nav-item[data-menu="password"]'],
      ['type','[data-mount="pw-cur"]','payhug!2025'],
      ['type','[data-mount="pw-new"]','payhug!2026'],
      ['type','[data-mount="pw-cfm"]','payhug!2026'],
      ['click','[data-act="pw-submit"]']]]
  ];
  for(const [screen, state, steps] of SEQ){
    let err = null;
    await evalJS('location.hash="#invest-assets"; return 1;');
    await sleep(60);
    for(const st of steps){
      if(st[0] === 'wait'){ await sleep(st[1]); continue; }
      /* 도크를 뺀 뒤 필터로 닿을 수 없는 빈 상태는 딥링크로 간다 — 딥링크는 Figma 캡처용으로 유지한다. */
      if(st[0] === 'hash'){ await evalJS('location.hash=' + JSON.stringify(st[1]) + '; return 1;'); await sleep(90); continue; }
      try {
        const ok = await evalJS('var e=document.querySelector(' + JSON.stringify(st[1]) + ');' +
          (st[0] === 'type'
            ? 'if(!e) return "missing"; e.value=' + JSON.stringify(st[2]) + '; e.dispatchEvent(new Event("input",{bubbles:true})); return "ok";'
            : st[0] === 'change'
            ? 'if(!e) return "missing"; e.value=' + JSON.stringify(st[2]) + '; e.dispatchEvent(new Event("change",{bubbles:true})); return "ok";'
            : 'if(!e) return "missing"; if(e.disabled) return "disabled"; e.click(); return "ok";'));
        if(ok !== 'ok'){ err = st[1] + ' → ' + ok; break; }
      } catch(e){ err = st[1] + ' → ' + e.message; break; }
      await sleep(60);
    }
    const got = await evalJS('var s=document.querySelector(\'section.screen[data-screen="' + screen + '"]\');' +
      'var modal=document.querySelector("[data-modal]:not([hidden])");' +
      'return {state:s.dataset.state, visible:!s.hidden, hash:location.hash,' +
      ' modal: modal? modal.dataset.modal : null, toast: !document.querySelector("[data-mount=toast]").hidden};');
    R.states.push({screen, state, ...got, err,
      steps: steps.map(s => s[0] === 'wait' ? 'wait ' + s[1] + 'ms' : s[0] + ' ' + s[1] + (s[2] ? ' = ' + s[2] : '')).join(' → '),
      pass: !err && got.visible && got.state === state});
  }

  /* ── 3) 엑셀 8건 — 원본처럼 중간 화면 없이 즉시 파일이 나오는지 실측 ──
     판정 = 실물 파일이 디스크에 떨어지고(바이트 일치) 화면이 미리보기로 넘어가지 않는다.
     투자 수익은 버튼 2개가 집계 단위 3단을 타므로 상태별로 6번을 따로 본다 —
     카드가 4주를 말하는데 일주일 파일이 나가면 여기서 걸린다. */
  const CASES = [
    {key:'assets-status',   screen:'invest-assets', state:'default', file:'투자자산현황_2026-08-27_2026-08-27.xlsx'},
    {key:'assets-merchant', screen:'invest-assets', state:'default', file:'가맹점별투자자산_2026-08-27_2026-08-27.xlsx'},
    {key:'profit-status',   screen:'invest-profit', state:'default', file:'투자수익현황_2026-08-21_2026-08-27.xlsx'},
    {key:'profit-daily',    screen:'invest-profit', state:'default', file:'일별투자수익_2026-08-21_2026-08-27.xlsx'},
    {key:'profit-status',   screen:'invest-profit', state:'weekly',  file:'투자수익현황_2026-08-03_2026-08-30.xlsx'},
    {key:'profit-daily',    screen:'invest-profit', state:'weekly',  file:'주별투자수익_2026-08-03_2026-08-30.xlsx'},
    {key:'profit-status',   screen:'invest-profit', state:'monthly', file:'투자수익현황_2026-03-01_2026-08-31.xlsx'},
    {key:'profit-daily',    screen:'invest-profit', state:'monthly', file:'월별투자수익_2026-03-01_2026-08-31.xlsx'}
  ];
  for(const c of CASES){
    fs.readdirSync(DL).forEach(f => { try{ fs.unlinkSync(path.join(DL, f)); }catch(e){} });
    await evalJS('go(' + JSON.stringify(c.screen) + ', ' + JSON.stringify(c.state) + '); return 1;');
    await sleep(250);
    const click = await evalJS('var b=document.querySelector(\'[data-act="xls-open"][data-xls="' + c.key + '"]\');' +
      'if(!b) return "missing"; b.click(); return "ok";');
    await sleep(120);
    const view = await evalJS('return document.body.dataset.view;');
    let got = null;
    for(let i = 0; i < 25 && !got; i++){
      await sleep(200);
      const f = path.join(DL, c.file);
      if(fs.existsSync(f) && fs.statSync(f).size > 0) got = f;
    }
    await sleep(500);
    const src = path.join(REPO, 'assets/xlsx', c.file);
    const direct = (view === c.screen);
    R.downloads.push({key:c.key + '/' + c.state, expect:c.file, click, viewAfter:view, noPreviewScreen:direct,
      file: got ? path.basename(got) : null,
      bytes: got ? fs.statSync(got).size : 0, srcBytes: fs.statSync(src).size,
      pass: !!got && direct && fs.statSync(got).size === fs.statSync(src).size});
  }

  /* ── 4) 죽은 컨트롤 전수 스캔 ──
     범위 — 태그가 아니라 `클릭 가능해 보이는가`로 뽑는다. div 기반 컨트롤도 들어온다.
     판정 — 클릭 뒤 DOM·표 행 수·모달·토스트·해시·포커스 가운데 하나라도 변해야 산 것으로 본다. */
  const SCAN = await evalJS(`
    function sig(){
      var b=document.body.innerHTML, h=0;
      for(var i=0;i<b.length;i++) h=(h*31 + b.charCodeAt(i))|0;
      var m=document.querySelector('[data-modal]:not([hidden])');
      var t=document.querySelector('[data-mount=toast]');
      var rows=document.querySelectorAll('table.tbl tbody tr').length;
      var els=document.querySelectorAll('*').length;
      var af=document.activeElement;
      return h + '|' + location.hash + '|' + (m?m.dataset.modal:'') + '|' + (t.hidden?0:1) + '|' + t.textContent
           + '|' + b.length + '|' + rows + '|' + els + '|' + (af ? af.tagName + '.' + (af.className||'') : '');
    }
    function isCtl(e){
      var t=e.tagName;
      if(t==='BUTTON' || t==='SELECT') return true;
      if(t==='A' && e.hasAttribute('href')) return true;
      if(t==='INPUT' && (e.type==='checkbox' || e.type==='date')) return true;
      if(e.hasAttribute('data-act') || e.hasAttribute('data-nav') || e.hasAttribute('onclick')) return true;
      var r=e.getAttribute('role');
      if(r==='button' || r==='link' || r==='option' || r==='tab' || r==='menuitem') return true;
      if(e.hasAttribute('tabindex') && e.getAttribute('tabindex')!=='-1') return true;
      if(e.classList.contains('clickable') || e.classList.contains('dd-trigger') || e.classList.contains('dd-opt')) return true;
      try { if(getComputedStyle(e).cursor==='pointer') return true; } catch(err){}
      return false;
    }
    function outermost(e, root){                    /* 버튼 안의 span·svg 를 중복으로 세지 않는다 */
      var p=e.parentElement;
      while(p && p!==root && p!==document.body){ if(isCtl(p)) return false; p=p.parentElement; }
      return true;
    }
    function nativeCtl(e){
      return e.tagName==='BUTTON' || e.tagName==='SELECT' || e.tagName==='INPUT'
             || (e.tagName==='A' && e.hasAttribute('href'));
    }
    function alreadyActive(e){
      if(e.classList.contains('active')) return true;                       /* 프리셋·토글·현재 페이지 */
      if(e.classList.contains('hover') && e.classList.contains('dd-opt')) return true;  /* 선택된 옵션 */
      if(e.dataset.act==='cert-open' && document.querySelector('[data-modal]:not([hidden])')) return true;
      return false;
    }
    var TARGETS=[['invest-assets','default'],['invest-assets','page2'],['invest-assets','empty'],['invest-assets','cert-confirm'],
      ['invest-profit','default'],['invest-profit','weekly'],['invest-profit','monthly'],['invest-profit','empty'],
      ['invest-sim','default'],['invest-sim','result'],
      ['merchants','default'],['merchants','filtered'],['merchants','empty'],
      ['acquisition-list','default'],['acquisition-list','doc'],['acquisition-list','confirm'],['acquisition-list','done'],
      ['contracts','default'],['contracts','all'],['contracts','empty'],
      ['coocon','default'],['password','default'],['password','weak'],['password','done'],
      ['certificate','default'],['xls-assets-status','default'],['xls-assets-merchant','default'],
      ['xls-profit-status','default'],['xls-profit-daily','default'],['index','default'],['login','default']];
    var dead=[], a11y=[], newtab=[], seen={}, scanned=0;
    function vis(e){
      if(e.getClientRects().length===0) return false;
      var cs=getComputedStyle(e);
      return cs.visibility!=='hidden' && cs.display!=='none';
    }
    function collect(scr){
      var root = document.querySelector('section.screen[data-screen="'+scr+'"]');
      var pool = [];
      Array.prototype.push.apply(pool, root.querySelectorAll('*'));
      var mm=document.querySelector('[data-modal]:not([hidden])');
      if(mm) Array.prototype.push.apply(pool, mm.querySelectorAll('*'));
      return pool.filter(function(e){ return isCtl(e) && vis(e) && outermost(e, root); });
    }
    TARGETS.forEach(function(t){
      var scr=t[0], stt=t[1];
      for(var pass=0; pass<400; pass++){
        go(scr, stt);
        var all = collect(scr);
        var pool = all.filter(function(e){
          return e.getAttribute('target')!=='_blank' && !e.disabled
                 && e.getAttribute('aria-disabled')!=='true'   /* 사유를 밝히고 꺼둔 것은 죽은 게 아니다 */
                 && e.tagName!=='SELECT' && !alreadyActive(e)
                 && e.tagName!=='INPUT';
        });
        if(pass === 0){
          all.forEach(function(e){
            var lb=(e.textContent||'').trim().slice(0,24) || e.getAttribute('aria-label') || e.tagName.toLowerCase();
            var k=scr+'/'+stt+' :: '+lb;
            if(e.getAttribute('target')==='_blank' && !seen['NT'+k]){ seen['NT'+k]=1;
              newtab.push({where:scr+'/'+stt, label:lb, href:e.getAttribute('href')||''}); }
            /* 키보드·보조기술로 닿을 수 없는 컨트롤.
               표 행·목록 행은 대상에서 뺀다 — 기준 레포 payhug-admin-web 전수 검색 결과
               tabIndex 0건, role 1건(그것도 <div>)이라 원본 어드민도 행이 키보드 초점 대상이 아니다.
               행에 role="checkbox"·tabindex="0" 을 얹었던 45곳은 임의 생성으로 판정돼 걷어냈다
               (parity_audit_0828.md 판정표 7·8). 행 선택은 행 클릭과 행 안 <input type=checkbox> 가 맡고,
               그 동작은 아래 '행 클릭 선택' 항목에서 따로 확인한다.
               검사 대상은 버튼·링크·입력처럼 원래 초점을 받는 컨트롤로 한정한다. */
            var cls_ = ' ' + (e.className||'').toString() + ' ';
            var isRow = e.tagName==='TR' || cls_.indexOf(' sign-row ')>=0 || cls_.indexOf(' pickable ')>=0;
            if(!isRow && !nativeCtl(e) && !e.hasAttribute('role') && !e.hasAttribute('tabindex') && !seen['A'+k]){
              seen['A'+k]=1;
              a11y.push({where:scr+'/'+stt, label:lb, tag:e.tagName.toLowerCase(),
                         cls:(e.className||'').toString().slice(0,40), act:e.dataset.act||''});
            }
          });
        }
        if(pass>=pool.length) break;
        var el=pool[pass];
        var label=(el.textContent||'').trim().slice(0,24) || el.getAttribute('aria-label') || el.tagName.toLowerCase();
        var key=scr+'/'+stt+' :: '+(el.dataset.act||el.getAttribute('href')||el.dataset.nav||'')+' :: '+label;
        if(seen[key]) continue; seen[key]=1;
        scanned++;
        document.querySelector('[data-mount=toast]').hidden=true;
        var before=sig();
        try{ el.click(); }catch(e){ dead.push({where:scr+'/'+stt, label:label, why:'throw '+e.message}); continue; }
        var after=sig();
        if(before===after) dead.push({where:scr+'/'+stt, label:label, tag:el.tagName.toLowerCase(),
          cls:(el.className||'').toString().slice(0,40), act:el.dataset.act||'', href:el.getAttribute('href')||''});
      }
    });
    go('invest-assets','default');
    return {dead:dead, a11y:a11y, newtab:newtab, scanned:scanned};
  `);
  R.dead = SCAN.dead;
  R.scanned = SCAN.scanned;
  R.a11y = SCAN.a11y;
  R.newtab = SCAN.newtab;

  /* ── 5) 보기 갯수·필터가 실제로 값을 바꾸는지 ── */
  R.data = await evalJS(`
    var out=[];
    function firstCell(sel,col){ var r=document.querySelectorAll(sel+' tbody tr'); return r.length? r[0].children[col].textContent.trim():null; }
    /* 보기 갯수 — 고르는 즉시 표가 다시 그려진다(적용 버튼 없음) */
    function sizePick(key, v){
      var sel=document.querySelector('[data-act=pg-size][data-key='+key+']');
      sel.value=String(v); sel.dispatchEvent(new Event('change',{bubbles:true}));
    }
    function rowsOf(sel){ return document.querySelectorAll(sel+' tbody tr').length; }
    var szOut=[];
    [['invest-assets','ia-merch','[data-mount=ia-merch]'],
     ['merchants','mc-tbl','[data-mount=mc-tbl]'],
     ['contracts','ct-tbl','[data-mount=ct-tbl]']].forEach(function(t){
      go(t[0],'default');
      var opts=Array.prototype.map.call(document.querySelector('[data-act=pg-size][data-key='+t[1]+']').options,
        function(o){ return o.value; });
      var n10=rowsOf(t[2]);
      sizePick(t[1],20); var n20=rowsOf(t[2]);
      var pgs=document.querySelectorAll('section.screen[data-screen='+JSON.stringify(t[0])+'] .page-btn').length;
      sizePick(t[1],50); var n50=rowsOf(t[2]);
      sizePick(t[1],10);
      szOut.push({tbl:t[1], opts:opts, n10:n10, n20:n20, n50:n50, pagesAt20:pgs,
        ok: opts.join(',')==='10,20,50' && n10===10 && n20===16 && n50===16 && pgs===0});
      go(t[0],'default');
    });
    out.push({case:'보기 갯수 10/20/50 — 고르면 즉시 다시 그린다', 표:szOut,
      pass: szOut.every(function(x){ return x.ok; })});

    /* 서명 완료 — 서명한 행이 대기 목록에서 빠지고, 메뉴를 오가도 남는다 */
    go('acquisition-list','default');
    function aqRows(){ return document.querySelectorAll('[data-mount=aq-rows] .sign-row').length; }
    var q0=aqRows();
    document.querySelector('[data-act=aq-chk][data-i="0"]').click();
    document.querySelector('[data-act=aq-sign]').click();
    document.querySelector('[data-act=aq-sign-go]').click();
    /* 1.5초 타이머를 기다리지 않고 같은 전이를 그대로 재현한다 — 선택 비우기까지 포함 */
    for(var i=0;i<AQ.sel.length;i++) if(AQ.sel[i]){ AQ.signed[i]=true; AQ.sel[i]=false; }
    AQ.phase='done'; DIRTY['acquisition-list']=1; refresh('acquisition-list');
    var qSel=document.querySelector('[data-mount=ab-count]').textContent.trim();
    document.querySelector('[data-act=aq-done-ok]').click();
    var q1=aqRows();
    go('merchants'); go('acquisition-list');
    var q2=aqRows(), storageUsed=0;
    try{ storageUsed = localStorage.length + sessionStorage.length; }catch(e){ storageUsed = 0; }
    go('acquisition-list','default');
    var q3=aqRows();
    out.push({case:'서명 완료 — 대기 목록에서 빠지고 메뉴를 오가도 남는다',
      전:q0, 서명후:q1, 메뉴왕복후:q2, 상태리셋후:q3, 저장소항목:storageUsed, 서명직후선택건수:qSel,
      pass: q0===3 && q1===2 && q2===2 && q3===3 && storageUsed===0 && qSel==='0'});

    /* 목록에서 빠진 행이 선택 건수에 남지 않는다 — 서명 완료 상태로 바로 들어와도 같다 */
    go('acquisition-list','done');
    var d0=aqRows(), d1=document.querySelector('[data-mount=ab-count]').textContent.trim();
    var d2=document.querySelector('[data-mount=ab-btn]').disabled;
    out.push({case:'서명 완료 — 선택 건수는 남은 행만 센다', 남은행:d0, 선택건수:d1, 서명하기비활성:d2,
      pass: d0===1 && d1==='0' && d2===true});
    go('acquisition-list','default');

    go('merchants','default');
    var m0=document.querySelectorAll('[data-mount=mc-tbl] tbody tr').length;
    var t0=document.querySelector('[data-mount=mc-page]').textContent.replace(/\\s+/g,'');
    document.querySelector('[data-mount=mc-kw]').value='곱창';
    document.querySelector('[data-act=mc-search]').click();
    var m1=document.querySelectorAll('[data-mount=mc-tbl] tbody tr').length;
    var t1=document.querySelector('[data-mount=mc-page]').textContent.replace(/\\s+/g,'');
    out.push({case:'가맹점 검색어 필터', rowsBefore:m0, rowsAfter:m1, countBefore:t0, countAfter:t1,
      pass: m0===10 && m1===2 && t0.indexOf('총16건')>=0 && t1.indexOf('총2건')>=0});

    go('invest-profit','default');
    function foot(){ var f=document.querySelector('[data-mount=pf-tbl] tfoot tr'); return f? Array.prototype.map.call(f.children,function(c){return c.textContent.trim();}) : null; }
    var w=foot(), wr=document.querySelectorAll('[data-mount=pf-tbl] tbody tr').length;
    /* '어제' 프리셋은 스토리보드 슬라이드7 에 없어 뺐다 — 하루 구간은 날짜를 직접 넣어 만든다. */
    var pfF=document.querySelector('[data-mount=pf-from]'), pfT=document.querySelector('[data-mount=pf-to]');
    pfF.value='2026-08-26'; pfF.dispatchEvent(new Event('change',{bubbles:true}));
    pfT.value='2026-08-26'; pfT.dispatchEvent(new Event('change',{bubbles:true}));
    var y=foot(), yr=document.querySelectorAll('[data-mount=pf-tbl] tbody tr').length;
    /* 하루(08-26)에서 월별로 옮기면 그 하루가 든 달 전체(08-01~08-31)를 덮어 한 행이 된다.
       기간을 지우고 6개월로 되돌리지 않는다 — 그게 종전 결함이었다. */
    document.querySelector('[data-act=pf-gran][data-gran=monthly]').click();
    var mo=foot(), mr=document.querySelectorAll('[data-mount=pf-tbl] tbody tr').length;
    var mFrom=PF.from, mTo=PF.to;
    /* 같은 자리에서 6개월 프리셋을 누르면 여섯 행이 된다 */
    document.querySelector('[data-act=preset][data-preset=m6]').click();
    var m6=foot(), m6r=document.querySelectorAll('[data-mount=pf-tbl] tbody tr').length;
    out.push({case:'기간·granularity 변경 시 합계 재계산', weekRows:wr, weekSum:w&&w[3], ydayRows:yr, ydaySum:y&&y[3],
      monthRows:mr, monthSum:mo&&mo[3], monthRange:mFrom+'~'+mTo, m6Rows:m6r, m6Sum:m6&&m6[3],
      pass: wr===7 && yr===1 && mr===1 && m6r===6
            && mFrom==='2026-08-01' && mTo==='2026-08-31'
            && w[3]!==y[3] && y[3]!==mo[3] && mo[3]!==m6[3]});

    /* 업종 필터 — 네이티브 select 로 고르면 조건이 실제로 적용되는지.
       원본 어드민은 커스텀 드롭다운 0건·전부 <select> 라 대조 대상 컨트롤을 select 로 바꿨다. */
    go('merchants','default');
    var sel=document.querySelector('[data-mount=mc-sector]');
    var ddTag=sel.tagName;
    var ddOpts=Array.prototype.map.call(sel.options,function(e){return e.textContent.trim();});
    var dataSectors=(function(){var s={},o=[];for(var i=0;i<MERCHANTS.length;i++)if(!s[MERCHANTS[i].sector]){s[MERCHANTS[i].sector]=1;o.push(MERCHANTS[i].sector);}return o;})();
    sel.value=dataSectors[0];
    sel.dispatchEvent(new Event('change',{bubbles:true}));
    document.querySelector('[data-act=mc-search]').click();
    var ddChip=(document.querySelector('[data-mount=mc-chips]').textContent||'').replace(/\\s+/g,'');
    var ddCustom=document.querySelectorAll('.dd-trigger, .dd-opt, [role=combobox], [role=listbox]').length;
    out.push({case:'업종 필터 — 네이티브 select·데이터 파생 옵션·조건 적용',
      tag:ddTag, opts:ddOpts, dataSectors:dataSectors, customLeft:ddCustom,
      picked:MC.sector, chips:ddChip,
      pass: ddTag==='SELECT' && ddCustom===0
            && ddOpts.length===dataSectors.length+1 && ddOpts[0]==='전체'
            && dataSectors.every(function(s){return ddOpts.indexOf(s)>0;})
            && ddChip.indexOf('업종:'+MC.sector)>=0});

    /* 날짜 입력이 조회 조건을 움직이는지 — 종전에는 change 를 받는 코드가 없어 친 값이 버려졌다 */
    go('invest-profit','default');
    var d0=document.querySelectorAll('[data-mount=pf-tbl] tbody tr').length;
    var fi=document.querySelector('[data-mount=pf-from]'), ti=document.querySelector('[data-mount=pf-to]');
    fi.value='2026-08-25'; fi.dispatchEvent(new Event('change',{bubbles:true}));
    var d1=document.querySelectorAll('[data-mount=pf-tbl] tbody tr').length;
    document.querySelector('[data-act=pf-search]').click();
    var kept=document.querySelector('[data-mount=pf-from]').value;
    var period=(document.querySelector('[data-mount=pf-stat] .summary-sub.mono').textContent||'').trim();
    out.push({case:'날짜 입력이 조회 조건을 움직인다', rowsBefore:d0, rowsAfter:d1, valueKept:kept, period:period,
      pass: d0===7 && d1===3 && kept==='2026-08-25' && period.indexOf('2026-08-25')===0});

    /* 역전 범위 방어 — 안내문 + 조회 버튼 비활성.
       달력의 min/max 상호 제한은 걸지 않는다. 걸면 지금 기간보다 앞쪽으로 옮기려고
       종료일부터 열었을 때 달력이 통째로 막혀 피커가 죽는다. */
    go('invest-profit','default');
    fi=document.querySelector('[data-mount=pf-from]'); ti=document.querySelector('[data-mount=pf-to]');
    var clamp=[fi.getAttribute('min'),fi.getAttribute('max'),ti.getAttribute('min'),ti.getAttribute('max')];
    fi.value='2026-09-30'; fi.dispatchEvent(new Event('change',{bubbles:true}));
    var warn=document.querySelector('[data-mount=pf-warn]');
    var go1=document.querySelector('[data-act=pf-search]');
    out.push({case:'역전 범위 방어 — 안내문·버튼 비활성 · 달력은 잠그지 않음',
      clamp:clamp, warnShown:!warn.hidden, searchDisabled:!!go1.disabled,
      pass: clamp.every(function(v){return v===null;}) && !warn.hidden && !!go1.disabled});
    go('invest-profit','default');

    /* 검색창 Enter 가 조회를 실행하는지 */
    go('merchants','default');
    var kw=document.querySelector('[data-mount=mc-kw]');
    kw.value='곱창'; kw.dispatchEvent(new Event('input',{bubbles:true}));
    kw.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true}));
    var eRows=document.querySelectorAll('[data-mount=mc-tbl] tbody tr').length;
    out.push({case:'검색창 Enter → 조회 실행', rows:eRows, pass: eRows===2});
    go('merchants','default');

    /* 모달 배경 클릭으로는 닫히지 않는다 (D-40) — 여는 자리는 MODAL_OF 로 역산한다 */
    var bdClose=[], bdKeep=[];
    Object.keys(MODAL_OF).forEach(function(k){
      var t=k.split('/');
      go(t[0],t[1]);
      var bd=document.querySelector('[data-modal]:not([hidden])');
      if(!bd){ bdClose.push(k+':없음'); return; }
      bd.click();
      if(document.querySelector('[data-modal]:not([hidden])')) bdKeep.push(k);
      else bdClose.push(k);
    });
    go('invest-assets','default');
    out.push({case:'모달 배경 클릭으로 닫히지 않는다', closed:bdClose, kept:bdKeep,
      pass: bdClose.length===0 && bdKeep.length===Object.keys(MODAL_OF).length});

    /* 메뉴 그룹 접힘 — 셰브론이 실제로 그룹을 접는지 */
    var gh=document.querySelector('[data-act=nav-group]');
    var g0=gh.closest('.nav-group').classList.contains('collapsed');
    gh.click();
    var g1=gh.closest('.nav-group').classList.contains('collapsed');
    var aria=gh.getAttribute('aria-expanded');
    gh.click();
    out.push({case:'메뉴 그룹 접힘', tag:gh.tagName, before:g0, after:g1, aria:aria,
      pass: gh.tagName==='BUTTON' && g0===false && g1===true && aria==='false'});

    go('contracts','default');
    /* 선택 건수는 목록 아래 왼쪽(쪽번호 줄 왼쪽 칸)에 있다 — 머리에는 총 건수만 남는다 */
    function ctSel(){ var p=document.querySelector('section[data-screen=contracts] .pagination .sel-pill');
                      return p ? p.textContent : null; }
    var c0=ctSel();
    document.querySelector('[data-act=ct-all]').click();
    var c1=ctSel();
    var lab=document.querySelector('[data-mount=ct-dl-label]').textContent;
    out.push({case:'계약기록 전체 선택', before:c0, after:c1, button:lab, pass:c0==='3건 선택' && c1==='16건 선택' && lab.indexOf('(16)')>0});

    /* 신설 버튼 3종 — 계약기록 선택 해제 · 서명 대기 목록 전체 선택/선택 해제 · 행 클릭 선택 */
    document.querySelector('[data-act=ct-clear]').click();
    var c2=ctSel();
    var c2h=document.querySelector('section[data-screen=contracts] .tbl-head-bar .sel-pill')===null;
    var c2d=document.querySelector('[data-act=ct-download]').disabled;
    out.push({case:'계약기록 선택 해제', after:c2, 머리에없음:c2h, downloadDisabled:c2d,
      pass: c2===null && c2h===true && c2d===true});

    /* 내려받기는 선택 건수와 무관하게 잠겨 있다 — 전자서명 결과 파일 형식 미결 (D-39) */
    document.querySelector('[data-act=ct-all]').click();
    var c3d=document.querySelector('[data-act=ct-download]').disabled;
    var c3n=document.querySelectorAll('section[data-screen=contracts] tbody [data-act=ct-doc]:not([disabled])').length;
    var c3a=document.querySelectorAll('section[data-screen=contracts] tbody a[href*="assets/docs"]').length;
    out.push({case:'계약기록 내려받기 잠금', 전체선택시:c3d, 살아있는행버튼:c3n, 문서링크:c3a,
      pass: c3d===true && c3n===0 && c3a===0});
    document.querySelector('[data-act=ct-clear]').click();

    /* 계약기록도 행을 눌러 고른다 — 행 안의 내려받기 버튼은 잠겨 있어 행 토글과 겹치지 않는다 (D-39) */
    var ctr=document.querySelector('section[data-screen=contracts] tbody tr.clickable');
    ctr.click(); var r1=ctSel();
    var ctb=document.querySelector('section[data-screen=contracts] tbody tr.clickable [data-act=ct-doc]');
    ctb.click();
    var r2=ctSel();
    out.push({case:'계약기록 행 클릭 선택 — 행 내려받기 버튼과 상쇄되지 않음', afterRow:r1, afterBtn:r2,
      rowBtnDisabled:!!ctb.disabled,
      role:ctr.getAttribute('role'), tabindex:ctr.getAttribute('tabindex'),
      pass: r1==='1건 선택' && r2==='1건 선택' && ctb.disabled===true
            && ctr.getAttribute('role')===null && ctr.getAttribute('tabindex')===null});
    document.querySelector('[data-act=ct-clear]').click();

    go('acquisition-list','default');
    function aqSel(){ return document.querySelector('[data-mount=ab-count]').textContent.trim(); }
    document.querySelector('[data-act=aq-clear]').click();
    var a0=aqSel(), a0b=document.querySelector('[data-mount=ab-btn]').disabled;
    document.querySelector('[data-act=aq-all]').click();
    var a1=aqSel(), a1b=document.querySelector('[data-mount=ab-btn]').disabled;
    out.push({case:'서명 대기 목록 전체 선택·선택 해제', cleared:a0, clearedBtnDisabled:a0b, all:a1, allBtnDisabled:a1b,
      pass: a0==='0' && a0b===true && a1==='3' && a1b===false});

    document.querySelector('[data-act=aq-clear]').click();
    var r0=aqSel();
    var row=document.querySelector('[data-act=aq-row][data-i="0"]');
    var rTag=!!row, rRole=row?row.getAttribute('role'):null, rTab=row?row.getAttribute('tabindex'):null;
    if(row) row.click();
    var r1v=aqSel(), rAria=document.querySelector('[data-act=aq-row][data-i="0"]').getAttribute('aria-checked');
    /* 체크박스를 눌렀을 때 행 토글과 겹쳐 상쇄되지 않는지 — 한 번 더 눌러 0 으로 돌아가야 한다 */
    document.querySelector('[data-act=aq-chk][data-i="0"]').click();
    var r2v=aqSel();
    out.push({case:'행 클릭 선택 — 체크박스와 상쇄되지 않음', before:r0, afterRowClick:r1v, afterChkClick:r2v,
      role:rRole, tabindex:rTab, aria:rAria,
      pass: rTag && rRole===null && rTab===null && rAria===null && r0==='0' && r1v==='1' && r2v==='0'});
    go('invest-assets','default');

    go('invest-assets','default');
    var s1=document.querySelector('[data-mount=ia-summary]').textContent.replace(/\\s+/g,' ');
    go('invest-assets','empty');
    var s2=document.querySelector('[data-mount=ia-summary]').textContent.replace(/\\s+/g,' ');
    out.push({case:'데이터 없음 상태 지표 0 치환', hasAmount:s1.indexOf('1,628,400,000')>=0, zeroed:s2.indexOf('1,628,400,000')<0,
      pass: s1.indexOf('1,628,400,000')>=0 && s2.indexOf('1,628,400,000')<0});
    go('invest-assets','default');
    return out;
  `);

  /* ── 6) 화면·상태 조합 레이아웃 점검 ── */
  R.layout = await evalJS(`
    var T=[['invest-assets','default'],['invest-assets','page2'],['invest-assets','download'],['invest-assets','cert-confirm'],['invest-assets','empty'],
      ['invest-profit','default'],['invest-profit','weekly'],['invest-profit','monthly'],['invest-profit','empty'],
      ['invest-sim','default'],['invest-sim','result'],
      ['merchants','default'],['merchants','filtered'],['merchants','empty'],
      ['acquisition-list','default'],['acquisition-list','doc'],['acquisition-list','confirm'],['acquisition-list','signing'],['acquisition-list','done'],
      ['contracts','default'],['contracts','all'],['contracts','empty'],
      ['coocon','default'],['password','default'],['password','weak'],['password','error'],['password','done'],
      ['certificate','default'],['xls-assets-status','default'],['xls-assets-merchant','default'],
      ['xls-profit-status','default'],['xls-profit-daily','default'],['index','default'],['login','default']];
    var MOD={'invest-assets/cert-confirm':'invest-assets-cert-confirm','acquisition-list/doc':'acquisition-doc',
      'acquisition-list/confirm':'acquisition-confirm',
      'acquisition-list/signing':'acquisition-signing','acquisition-list/done':'acquisition-done'};
    var out=[];
    T.forEach(function(t){
      go(t[0],t[1]);
      var sec=document.querySelector('section.screen[data-screen="'+t[0]+'"]');
      var h=sec.getBoundingClientRect().height;
      var empties=Array.prototype.filter.call(sec.querySelectorAll('[data-mount]'), function(m){ return m.innerHTML.trim()===''; })
                  .map(function(m){return m.dataset.mount;});
      var vis=Array.prototype.filter.call(document.querySelectorAll('[data-modal]'), function(m){ return !m.hidden; })
              .map(function(m){return m.dataset.modal;});
      var want=MOD[t[0]+'/'+t[1]]||null;
      var bar=document.querySelector('[data-mount=action-bar]');
      var barVis=!!(bar && bar.offsetParent);      /* 카드 안으로 들어가 화면과 함께 보이고 숨는다 */
      out.push({at:t[0]+'/'+t[1], h:Math.round(h), empties:empties, modals:vis, wantModal:want,
        barShown:barVis,
        pass: h>200 && vis.length===(want?1:0) && (!want||vis[0]===want) && barVis===(t[0]==='acquisition-list')});
    });
    go('invest-assets','default');
    return out;
  `);
  /* ── 7) 모달 닫힘 경로 — 닫기 버튼·X 로만 닫힌다 (D-40) ──
     모달 이름을 박지 않는다. 오버레이 요소 `[data-modal]` 를 전수로 훑고,
     그것을 여는 화면·상태는 앱이 들고 있는 MODAL_OF 로 역산한다. 새 모달이 생겨도 저절로 들어온다. */
  R.modals = await evalJS(`
    var OPEN={};
    for(var k in MODAL_OF){ var p=k.split('/'); OPEN[MODAL_OF[k]]=[p[0], p[1]]; }
    function el(name){ return document.querySelector('[data-modal="'+name+'"]'); }
    function shown(name){ var m=el(name); return !!(m && !m.hidden); }
    function esc(node){
      ['keydown','keyup'].forEach(function(t){
        node.dispatchEvent(new KeyboardEvent(t, {key:'Escape', code:'Escape', keyCode:27, bubbles:true, cancelable:true}));
      });
    }
    var out=[];
    Array.prototype.forEach.call(document.querySelectorAll('[data-modal]'), function(m0){
      var name=m0.dataset.modal, o=OPEN[name], rec={modal:name};
      if(!o){ rec.err='여는 화면·상태 없음'; rec.pass=false; out.push(rec); return; }
      rec.at=o[0]+'/'+o[1];

      /* (1) 오버레이 여백 클릭 — 패널 바깥의 실제 좌표를 짚는다 */
      go(o[0],o[1]);
      var m=el(name), panel=m.querySelector('.modal');
      var pr=panel.getBoundingClientRect();
      var hitEl=document.elementFromPoint(Math.max(3, pr.left/2), Math.max(3, pr.top/2));
      rec.overlayHit = hitEl ? (hitEl.className||hitEl.tagName) : null;
      if(hitEl) hitEl.click();
      rec.afterOverlayClick = shown(name);

      /* (2) 패널 안쪽 클릭 — 본문 자체와 본문 안 첫 비컨트롤 요소 */
      go(o[0],o[1]); m=el(name);
      var body=m.querySelector('.modal-body') || m.querySelector('.modal');
      body.click();
      rec.afterBodyClick = shown(name);
      go(o[0],o[1]); m=el(name);
      var inner=Array.prototype.filter.call(m.querySelectorAll('.modal-body *'), function(e){
        return !e.closest('[data-act]') && !e.querySelector('[data-act]')
               && (e.textContent||'').trim().length > 0;
      })[0];
      rec.innerTag = inner ? inner.tagName.toLowerCase() : null;
      if(inner) inner.click();
      rec.afterInnerClick = shown(name);

      /* (3) ESC */
      go(o[0],o[1]); m=el(name);
      esc(document); esc(m); esc(m.querySelector('.modal'));
      rec.afterEsc = shown(name);

      /* (4) 닫히게 하는 컨트롤 전수 — 무엇이 닫는지 실측 */
      go(o[0],o[1]); m=el(name);
      var ctls=Array.prototype.slice.call(m.querySelectorAll('button, a[href], [role=button]'));
      rec.controls = ctls.length;
      rec.live = ctls.filter(function(c){ return !c.disabled; }).length;
      var closers=[];
      for(var i=0;i<ctls.length;i++){
        go(o[0],o[1]);
        var mm=el(name);
        var c=mm.querySelectorAll('button, a[href], [role=button]')[i];
        if(!c || c.disabled) continue;
        if(c.getAttribute('target')==='_blank') continue;   /* 새 창 열기 — 닫기 경로가 아니다 */
        c.click();
        if(!shown(name)) closers.push({
          label:(c.textContent||'').trim().slice(0,12) || c.getAttribute('aria-label') || '',
          tag:c.tagName.toLowerCase(), act:c.dataset.act||'',
          x: c.classList.contains('close'),
          footer: !!c.closest('.modal-footer')});
      }
      rec.closers = closers;

      /* (5) 본문 스크롤·선택이 살아 있는가 — 클릭 무시가 읽기를 막지 않는다 */
      go(o[0],o[1]); m=el(name);
      var ds=m.querySelector('.doc-scroll');
      if(ds){
        var cs=getComputedStyle(ds);
        ds.scrollTop=60;
        rec.scroll={ overflow: ds.scrollHeight>ds.clientHeight, moved: ds.scrollTop>0,
                     select: cs.userSelect!=='none' && cs.webkitUserSelect!=='none',
                     pointer: cs.pointerEvents!=='none' };
        ds.scrollTop=0;
      }

      var noStray = (rec.afterOverlayClick===true && rec.afterBodyClick===true
                     && rec.afterInnerClick===true && rec.afterEsc===true);
      var byButton = closers.every(function(c){ return c.tag==='button' && (c.x || c.footer); });
      var reachable = (rec.live===0) || closers.length>0;    /* 살아 있는 컨트롤이 없으면 진행 오버레이 */
      var readable = !ds || (rec.scroll.select && rec.scroll.pointer && (!rec.scroll.overflow || rec.scroll.moved));
      rec.pass = noStray && byButton && reachable && readable;
      out.push(rec);
    });
    go('invest-assets','default');
    return out;
  `);

  R.console = consoleErrors.slice();
  fs.writeFileSync(path.join(OUTDIR, 'verify_app_result.json'), JSON.stringify(R, null, 1));

  const line = (t, ok) => (ok ? 'PASS ' : 'FAIL ') + t;
  console.log('== 메뉴 ' + R.menus.length + ' ==');   R.menus.forEach(m => console.log(' ', line(m.label + ' → ' + m.screen + ' (' + m.bg + ')', m.pass)));
  console.log('== 상태 ' + R.states.length + ' =='); R.states.forEach(s => console.log(' ', line(s.screen + '/' + s.state + (s.err ? '  ' + s.err : '  got=' + s.state), s.pass)));
  console.log('== 다운로드 ' + R.downloads.length + ' =='); R.downloads.forEach(d => console.log(' ', line(d.key + ' → ' + d.file + ' ' + d.bytes + 'B', d.pass)));
  console.log('== 값 변화 =='); R.data.forEach(d => console.log(' ', line(d.case + ' ' + JSON.stringify(d), d.pass)));
  console.log('== 레이아웃 ' + R.layout.length + '조합 ==');
  R.layout.forEach(l => console.log(' ', line(l.at + ' h=' + l.h + (l.empties.length ? ' 빈마운트=' + l.empties.join(',') : '') + (l.modals.length ? ' 모달=' + l.modals.join(',') : ''), l.pass)));
  console.log('== 사이드바 메뉴 ==', R.menuCount, '건 (SPA', MENUS.length, '· 외부링크', R.menuCount - MENUS.length, ')');
  console.log('== 죽은 컨트롤 ==', R.dead.length, '/ 검사', R.scanned, '건');
  R.dead.slice(0, 40).forEach(d => console.log('  -', JSON.stringify(d)));
  console.log('== 새 창 링크(실물은 verify_links.py) ==', R.newtab.length);
  console.log('== 키보드·보조기술 미도달 컨트롤 (표 행 제외 — 원본 tabIndex 0건) ==', R.a11y.length);
  R.a11y.slice(0, 20).forEach(d => console.log('  -', JSON.stringify(d)));
  console.log('== 콘솔 에러 ==', R.console.length);
  R.console.slice(0, 20).forEach(c => console.log('  -', c));
  console.log('== 모달 닫힘 경로 ' + R.modals.length + ' ==');
  R.modals.forEach(m => console.log(' ', line(m.modal + '  오버레이=' + m.afterOverlayClick + ' 본문=' + m.afterBodyClick +
    ' 내부=' + m.afterInnerClick + ' ESC=' + m.afterEsc +
    ' 닫는것=[' + (m.closers||[]).map(c => c.label + (c.x ? '(X)' : '')).join(', ') + ']' +
    (m.scroll ? ' 스크롤=' + JSON.stringify(m.scroll) : '') + (m.err ? ' ' + m.err : ''), m.pass)));
  console.log('== selfcheck ==', JSON.stringify(R.selfcheck));

  ws.close(); chrome.kill(); server.close();
  process.exit(0);
}
main().catch(e => { console.error('VERIFY ERROR', e); process.exit(1); });
