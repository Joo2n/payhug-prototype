/* 시연본 게이트 — 창 없이(--headless=new) 돌리고, 하나라도 걸리면 종료코드 1.
   sync_prototype.sh 가 push 직전에 부른다. 통과해야만 올라간다.

   원본 app.html 의 버튼 구성이 바뀌어도 흔들리지 않게, 화면 이동은 go()·해시로 몬다.
   상태 도달 클릭 시퀀스 같은 깊은 검증은 verify_proto.js 가 따로 본다.

   사용: node gate_prototype.js [--url https://...]        (url 생략 시 로컬 파일 서버)   */
const http = require('http'), fs = require('fs'), path = require('path'), os = require('os');
const { spawn } = require('child_process');

const REPO = process.env.DST_REPO || '/Users/semi/cursor/payhug-investor-prototype';
/* 원본 app.html — 화면·상태 수를 여기서 실측해 시연본과 대조한다(게이트에 고정 숫자를 박지 않는다). */
const SRC_APP = process.env.SRC_APP || '/Users/semi/cursor/payhug-investor-admin/app.html';
const argUrl = (process.argv.find(a => a.startsWith('--url=')) || '').slice(6);
const URL_IN = argUrl || process.env.GATE_URL || '';
const PORT = 8400 + (process.pid % 90), DPORT = 9100 + (process.pid % 90);
const SPORT = 8600 + (process.pid % 90);
const DL = fs.mkdtempSync(path.join(os.tmpdir(), 'gate-'));
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const MIME = {'.html':'text/html; charset=utf-8', '.css':'text/css; charset=utf-8',
  '.png':'image/png', '.pdf':'application/pdf', '.zip':'application/zip',
  '.xlsx':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'};
const ALLOWED_HOSTS = ['www.we-bank.co.kr', 'fonts.googleapis.com', 'fonts.gstatic.com'];
/* 원장 사실값 — 게이트에 숫자를 손으로 적지 않되, 기대값은 원장에서 읽는다.
   daily_ledger.py 의 dump_facts() 산출물(verify_identity.js 와 같은 원천). */
const FACTS = JSON.parse(fs.readFileSync(path.join(__dirname, 'ledger_facts.json'), 'utf8'));
/* 원본에서 시연본이 덜어 내는 화면 — sync_prototype.py 와 같은 목록. 랜딩 갤러리 · 투자 시뮬레이션 · 엑셀 미리보기 4종(통합본 전용) */
const PROTO_DROPPED = ['index', 'invest-sim', 'xls-assets-status', 'xls-assets-merchant', 'xls-profit-status', 'xls-profit-daily'];
/* 시뮬레이션 흔적 — 메뉴·화면·JS·문자열 어느 것이든 시연본 DOM 에 있으면 안 된다 (sync_prototype.py SIM_BANNED 와 같은 목록) */
const SIM_TRACE = /invest-sim|시뮬|simRun|simBond|\bSIM(?:\b|_)|\bsim-/;
/* 엑셀 미리보기 흔적 — 뷰 id·시트 DOM 클래스·시트 JS 함수·파일바 (sync_prototype.py XLS_BANNED 와 같은 목록).
   assets/sheet.css 링크는 남는다 — .back-link 를 증명서 화면이 쓴다 */
const XLS_TRACE = /xls-assets-status|xls-assets-merchant|xls-profit|\bsheet-(?:frame|tabs|scroll|tab)\b|class="sheet"|\b(?:sheetRow|sheetData|sheetName|renderXls)\b|data-mount="(?:filebar|sheettabs|sheet)"|\bfile-bar\b|xls-get|미리보기 화면/;

function serve(root){
  return http.createServer((req, res) => {
    const p = path.join(root, decodeURIComponent(req.url.split('?')[0]));
    fs.readFile(p, (e, b) => {
      if(e){ res.writeHead(404); res.end('nope'); return; }
      res.writeHead(200, {'Content-Type': MIME[path.extname(p)] || 'application/octet-stream'});
      res.end(b);
    });
  });
}
const server = serve(REPO);
const srcServer = serve(path.dirname(SRC_APP));   /* 원본 실측용 */

let msgId = 0, ws, pending = new Map();
const consoleErrors = [];
const fails = [];
function send(m, p){ const id = ++msgId; ws.send(JSON.stringify({id, method:m, params:p||{}}));
  return new Promise(res => pending.set(id, {res})); }
async function ev(x){
  const r = await send('Runtime.evaluate', {expression:'(function(){' + x + '})()', returnByValue:true});
  if(r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails.exception || r.exceptionDetails.text));
  return r.result.value;
}
const sleep = ms => new Promise(r => setTimeout(r, ms));
function check(name, pass, detail){
  console.log((pass ? '  PASS ' : '  FAIL ') + name + (detail === undefined ? '' : '  ' + detail));
  if(!pass) fails.push(name);
}

async function main(){
  await new Promise(r => server.listen(PORT, r));
  await new Promise(r => srcServer.listen(SPORT, r));
  const TARGET = URL_IN || ('http://127.0.0.1:' + PORT + '/index.html');
  console.log('게이트 대상:', TARGET);
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'gp-'));
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
  ws = new WebSocket(targets.find(t => t.type === 'page').webSocketDebuggerUrl);
  await new Promise(r => ws.addEventListener('open', r));
  ws.addEventListener('message', e => {
    const m = JSON.parse(e.data);
    if(m.id && pending.has(m.id)){ pending.get(m.id).res(m.result); pending.delete(m.id); return; }
    if(m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error')
      consoleErrors.push(m.params.args.map(a => a.value || a.description || a.type).join(' '));
    if(m.method === 'Runtime.exceptionThrown')
      consoleErrors.push(String(m.params.exceptionDetails.exception && m.params.exceptionDetails.exception.description || m.params.exceptionDetails.text));
    if(m.method === 'Log.entryAdded' && m.params.entry.level === 'error')
      consoleErrors.push(m.params.entry.text + ' ' + (m.params.entry.url || ''));
  });
  await send('Runtime.enable'); await send('Log.enable'); await send('Page.enable');
  await send('Browser.setDownloadBehavior', {behavior:'allow', downloadPath: DL});

  /* 0) 원본 app.html 실측 — 시연본과 대조할 기준을 게이트가 들고 있지 않고 원본에서 읽는다.
        화면·상태는 계속 늘어난다(D-14 로 invest-profit/weekly 신설). 고정 숫자를 두면 늘 때마다 게이트가 깨진다. */
  let SRCREG = null;
  if(fs.existsSync(SRC_APP)){
    await send('Page.navigate', {url:'http://127.0.0.1:' + SPORT + '/' + encodeURIComponent(path.basename(SRC_APP))});
    await sleep(2200);
    try {
      SRCREG = await ev('var c=window.__selfcheck();' +
        'var per={}; Object.keys(STATE_META).forEach(function(k){ per[k]=Object.keys(STATE_META[k]).length-1; });' +
        'var nav=[].map.call(document.querySelectorAll(".sidebar .nav-item[data-menu]"), function(a){ return a.dataset.menu; });' +
        'var xls=Object.keys(XLSX).filter(function(k){ return !!XLSX[k].file; }).map(function(k){ return XLSX[k].file; });' +
        'return {screens:c.screens, states:c.states, order:SCREEN_ORDER.slice(), per:per, nav:nav, xls:xls};');
    } catch(e){ SRCREG = null; }
  }
  consoleErrors.length = 0;   /* 원본 페이지에서 난 것은 이 게이트 대상이 아니다 — verify_app.js 가 본다 */
  check('원본 app.html 실측', SRCREG !== null,
        SRCREG ? SRCREG.screens + '화면 · 상태 ' + SRCREG.states : SRC_APP + ' 를 읽지 못했다 (SRC_APP 로 지정)');

  await send('Page.navigate', {url: TARGET});
  await sleep(2200);

  /* 1) 화면·상태 전건이 그려지는가 (이동은 go() 로 — 버튼 구성 변화에 흔들리지 않는다) */
  const walk = await ev(`
    var out={screens:[], bad:[], states:0};
    SCREEN_ORDER.forEach(function(sc){
      var meta=STATE_META[sc]||{'default':null};
      Object.keys(meta).forEach(function(st){
        go(sc, st);
        var sec=document.querySelector('section.screen[data-screen="'+sc+'"]');
        var h=sec?sec.getBoundingClientRect().height:0;
        if(st!=='default') out.states++;
        if(!sec || sec.hidden || sec.dataset.state!==st || h<200)
          out.bad.push(sc+'/'+st+' hidden='+(sec?sec.hidden:'없음')+' state='+(sec?sec.dataset.state:'-')+' h='+Math.round(h));
      });
      out.screens.push(sc);
    });
    go('invest-assets','default');
    return out;
  `);
  check('화면 전건 렌더 (' + walk.screens.length + '화면 · 상태 ' + walk.states + ')',
        walk.bad.length === 0, walk.bad.slice(0, 5).join(' | '));

  /* 2) 사이드바 메뉴 전건 — 쿠콘 1개를 뺀 나머지는 클릭 전환, 쿠콘은 외부 링크.
        D-14: 쿠콘 관리 현금은 중간 화면 없이 바로 We-bank 로 나간다.
        app.html 의 .nav-item[data-menu=kcoon] 은 <a href="https://www.we-bank.co.kr/…" target="_blank" rel="noopener">.
        SPA 전환을 기대하면 영원히 FAIL 이고, 클릭하면 새 탭이 열려 게이트가 흔들린다 — 주소가 걸린 외부 링크인지를 본다.
        통합본 검증기 verify_app.js 도 같은 기준이다. 실측 전건을 그대로 본다(검사를 뺀 것이 아니다). */
  const KCOON_HOST = 'www.we-bank.co.kr';
  /* 메뉴 수를 숫자로 박지 않는다 — 사이드바에 실제로 걸린 .nav-item 을 세고,
     외부 링크(target=_blank)만 덜어 낸 나머지를 SPA 전환 대상으로 본다. 메뉴가 늘면 검사도 저절로 늘어난다. */
  const NAV = await ev(`
    return Array.prototype.map.call(document.querySelectorAll('.sidebar .nav-item[data-menu]'), function(a){
      return {m:a.dataset.menu, ext:a.getAttribute('target')==='_blank'}; });`);
  const SPA_MENUS = NAV.filter(x => !x.ext).map(x => x.m);
  const menu = await ev(`
    var bad=[];
    ${JSON.stringify(SPA_MENUS)}.forEach(function(m){
      var n=document.querySelector('.nav-item[data-menu="'+m+'"]');
      if(!n){ bad.push(m+' 없음'); return; }
      n.click();
      if(document.body.dataset.active!==m) bad.push(m+' -> active='+document.body.dataset.active);
      if(document.querySelector('.page').hidden) bad.push(m+' 사이드바 숨김');
    });
    var k=document.querySelector('.nav-item[data-menu="kcoon"]');
    if(!k) bad.push('kcoon 없음');
    else {
      var h=k.getAttribute('href')||'', u=null;
      try{ u=new URL(h); }catch(e){}
      if(!u || u.protocol!=='https:' || u.host!==${JSON.stringify(KCOON_HOST)}) bad.push('kcoon href='+h);
      if(k.getAttribute('target')!=='_blank') bad.push('kcoon target='+k.getAttribute('target'));
      if((k.getAttribute('rel')||'').indexOf('noopener')<0) bad.push('kcoon rel='+k.getAttribute('rel'));
      if(!/쿠콘/.test(k.textContent)) bad.push('kcoon 라벨='+k.textContent.trim());
    }
    go('invest-assets','default');
    return bad;
  `);
  check('사이드바 메뉴 ' + NAV.length + ' (SPA ' + SPA_MENUS.length + ' 전환 · 쿠콘 1 외부링크)',
        menu.length === 0 && NAV.length === SPA_MENUS.length + 1, menu.join(' | '));

  /* 3) 로고 — 자기 자신의 메인 화면으로만 */
  const logo = await ev(`
    go('contracts','default');
    var a=document.querySelector('.sidebar-logo a');
    if(!a) return {err:'로고 없음'};
    a.click();
    return {href:a.getAttribute('href'), view:document.body.dataset.view, host:location.host};
  `);
  check('로고 -> 자기 자신 메인', logo.view === 'invest-assets' && (logo.href === 'index.html' || logo.href === '#invest-assets'),
        JSON.stringify(logo));

  /* 3b) 투자 시뮬레이션 — 통합본 전용. 시연본에는 메뉴·화면·레지스터·JS·문자열 어느 것도 없다.
        사이드바는 원본 실측에서 invest-sim 하나를 뺀 목록과 순서까지 같아야 한다(곳수를 박지 않는다). */
  const sim = await ev(`
    var bad=[];
    if(document.querySelector('.sidebar .nav-item[data-menu="invest-sim"]')) bad.push('메뉴 있음');
    if(document.querySelector('section.screen[data-screen="invest-sim"]')) bad.push('화면 있음');
    if(SCREEN_ORDER.indexOf('invest-sim')>=0) bad.push('SCREEN_ORDER');
    if('invest-sim' in STATE_META) bad.push('STATE_META');
    if('invest-sim' in MENU_OF) bad.push('MENU_OF');
    if(Object.keys(FILE2SCREEN).concat(Object.keys(STATEFILE)).some(function(k){ return k.indexOf('invest-sim')===0; })) bad.push('FILE2SCREEN·STATEFILE');
    if(typeof simRun!=='undefined' || typeof SIM!=='undefined' || typeof clearSimTimer!=='undefined') bad.push('시뮬 JS 정의 있음');
    var m=document.documentElement.outerHTML.match(new RegExp(${JSON.stringify(SIM_TRACE.source)}));
    if(m) bad.push('문자열 '+m[0]);
    return bad;
  `);
  const navWant = SRCREG ? SRCREG.nav.filter(m => m !== 'invest-sim') : null;
  const navGot = NAV.map(x => x.m);
  if(navWant && JSON.stringify(navGot) !== JSON.stringify(navWant))
    sim.push('사이드바 ' + JSON.stringify(navGot) + ' ≠ 원본 - invest-sim ' + JSON.stringify(navWant));
  check('투자 시뮬레이션 없음 (메뉴 ' + navGot.length + (navWant ? ' = 원본 ' + SRCREG.nav.length + ' - 1' : '') + ')',
        sim.length === 0, sim.join(' | '));

  /* 그 해시로 들어오면 투자 자산 기본 화면 — 첫 진입(init)과 화면 안 이동(hashchange) 둘 다 */
  await send('Page.navigate', {url:'about:blank'}); await sleep(200);
  await send('Page.navigate', {url: TARGET + '#invest-sim/result'}); await sleep(1800);
  const simHash = await ev(`
    var sec=document.querySelector('section.screen:not([hidden])');
    var a={load:{view:document.body.dataset.view, state:sec?sec.dataset.state:'-', hash:location.hash}};
    go('contracts','default');
    return a;`);
  await ev(`location.hash='#invest-sim'; return 1;`); await sleep(300);
  simHash.change = await ev(`return {view:document.body.dataset.view, hash:location.hash};`);
  check('invest-sim 해시 진입 -> 투자 자산 (첫 진입 · 화면 안 이동)',
        simHash.load.view === 'invest-assets' && simHash.load.state === 'default' && simHash.load.hash === '#invest-assets' &&
        simHash.change.view === 'invest-assets' && simHash.change.hash === '#invest-assets',
        JSON.stringify(simHash));

  /* 3c) 엑셀 미리보기 4종 — 통합본 전용. 시연본에는 뷰·레지스터·시트 JS·파일바·문자열 어느 것도 없다.
        「엑셀 다운로드」 버튼은 중간 화면 없이 실물 xlsx 를 a[download] 로 바로 내려준다(원본 lib/excel.ts:38-51 규격). */
  const XLS_VIEWS = PROTO_DROPPED.filter(x => /^xls-/.test(x));
  await send('Page.navigate', {url: TARGET}); await sleep(1800);
  const xp = await ev(`
    var bad=[], V=${JSON.stringify(XLS_VIEWS)};
    if(document.querySelector('section.screen[data-screen^="xls-"]')) bad.push('화면 있음');
    if(document.querySelector('.sheet-frame, .sheet-tabs, table.sheet, .file-bar, [data-mount="filebar"], [data-mount="sheettabs"], [data-mount="sheet"]')) bad.push('시트·파일바 DOM 있음');
    V.forEach(function(v){
      if(SCREEN_ORDER.indexOf(v)>=0) bad.push('SCREEN_ORDER '+v);
      if(v in STATE_META) bad.push('STATE_META '+v);
      if(v in MENU_OF) bad.push('MENU_OF '+v);
      if(v in SCREEN_LABEL) bad.push('SCREEN_LABEL '+v);
      if(v in RENDER) bad.push('RENDER '+v);
    });
    if(Object.keys(FILE2SCREEN).concat(Object.keys(STATEFILE)).some(function(k){ return k.indexOf('xls-')===0; })) bad.push('FILE2SCREEN·STATEFILE');
    if(typeof renderXls!=='undefined' || typeof sheetData!=='undefined' || typeof sheetRow!=='undefined' || typeof sheetName!=='undefined') bad.push('시트 JS 정의 있음');
    if(ACT['xls-get']) bad.push("ACT['xls-get']");
    if(KEEP_DEFAULT.indexOf('xls-get')>=0) bad.push('KEEP_DEFAULT xls-get');
    Object.keys(XLSX).forEach(function(k){
      if(!XLSX[k].file) bad.push('XLSX '+k+' 파일 없음');
      if(String(XLSX[k].screen||'').indexOf('xls-')===0) bad.push('XLSX '+k+' screen');
    });
    var m=document.documentElement.outerHTML.match(new RegExp(${JSON.stringify(XLS_TRACE.source)}));
    if(m) bad.push('문자열 '+m[0]);
    return bad;
  `);
  check('엑셀 미리보기 없음 (뷰 ' + XLS_VIEWS.length + '종 · 레지스터 · 시트 JS · 파일바 · 문자열)', xp.length === 0, xp.join(' | '));

  /* 다운로드 버튼 — 레지스터의 파일 목록은 원본과 같고 전건이 시연본 자산에 있으며, 4개 버튼 모두 기본 상태에서 파일에 닿는다.
     실제 수신·바이트 일치는 5) 가 본다. */
  const dl = await ev(`
    var files=Object.keys(XLSX).map(function(k){ return XLSX[k].file; });
    var direct=String(pullFile).indexOf('a.download')>=0 && String(ACT['xls-open']).indexOf("'assets/xlsx/'")>=0;
    var btns=[].map.call(document.querySelectorAll('[data-act="xls-open"]'), function(b){ return b.dataset.xls; });
    go('invest-profit','default');
    var res=btns.map(function(x){ var k=xlsKey(x); return {btn:x, key:k, file:k?XLSX[k].file:null}; });
    go('invest-assets','default');
    return {files:files, direct:direct, btns:res};
  `);
  const dlBad = [];
  const dlMissing = dl.files.filter(f => !fs.existsSync(path.join(REPO, 'assets/xlsx', f)));
  const dlWant = SRCREG ? SRCREG.xls : null;
  if(!dl.direct) dlBad.push('pullFile·xls-open 이 a[download]·assets/xlsx/ 를 쓰지 않음');
  if(dlMissing.length) dlBad.push('시연본 자산에 없음 ' + dlMissing.join(','));
  if(dlWant && JSON.stringify(dl.files) !== JSON.stringify(dlWant)) dlBad.push('레지스터 파일 목록 ≠ 원본 (' + dl.files.length + '/' + dlWant.length + ')');
  dl.btns.forEach(b => { if(!b.file) dlBad.push('버튼 ' + b.btn + ' 기본 상태에서 파일 없음'); });
  check('엑셀 다운로드 = 실물 xlsx 직행 (레지스터 ' + dl.files.length + '건' + (dlWant ? ' = 원본 ' + dlWant.length : '') +
        ' · 자산 실재 · 버튼 ' + dl.btns.length + ')', dlBad.length === 0, dlBad.join(' | '));

  /* 그 해시로 들어오면 투자 자산 기본 화면 — 첫 진입 4종 · 화면 안 이동 1종 */
  const xh = {load:{}, change:null};
  for(const v of XLS_VIEWS){
    await send('Page.navigate', {url:'about:blank'}); await sleep(200);
    await send('Page.navigate', {url: TARGET + '#' + v}); await sleep(1600);
    xh.load[v] = await ev(`var sec=document.querySelector('section.screen:not([hidden])');
      return {view:document.body.dataset.view, state:sec?sec.dataset.state:'-', hash:location.hash};`);
  }
  await ev(`go('invest-profit','default'); return 1;`);
  await ev(`location.hash='#' + ${JSON.stringify(XLS_VIEWS[0] || 'xls-assets-status')}; return 1;`); await sleep(300);
  xh.change = await ev(`return {view:document.body.dataset.view, hash:location.hash};`);
  const xhBad = Object.keys(xh.load)
    .filter(v => !(xh.load[v].view === 'invest-assets' && xh.load[v].state === 'default' && xh.load[v].hash === '#invest-assets'))
    .concat(xh.change.view === 'invest-assets' && xh.change.hash === '#invest-assets' ? [] : ['화면 안 이동']);
  check('xls-* 해시 진입 -> 투자 자산 (첫 진입 ' + XLS_VIEWS.length + '종 · 화면 안 이동)', xhBad.length === 0,
        xhBad.length ? xhBad.join(' | ') + ' ' + JSON.stringify(xh) : '');

  /* 4) 바깥으로 나가는 통로 — 화면·상태 전 조합의 클릭 가능 요소 전수 */
  const esc = await ev(`
    var BAD=/glossary|capability|feasibility|inquiry|archive|review/i;
    var here=location.pathname, self=here.replace(/[^/]*$/,'')+'index.html';
    var out={offsite:[], sibling:[], banned:[], hash:0, asset:0, total:0}, seen={};
    function scan(where){
      Array.prototype.forEach.call(document.querySelectorAll('a[href],area[href],form[action]'), function(e){
        if(e.getClientRects().length===0) return;
        var h=e.getAttribute('href')||e.getAttribute('action')||'';
        var k=where+'::'+h; if(seen[k]) return; seen[k]=1;
        out.total++;
        if(BAD.test(h)) out.banned.push(where+' '+h);
        if(h.charAt(0)==='#'){ out.hash++; return; }
        var u; try{ u=new URL(h, location.href); }catch(err){ out.sibling.push(where+' '+h); return; }
        if(u.origin!==location.origin){ out.offsite.push(u.host); return; }
        if(u.pathname.indexOf('/assets/')>=0){ out.asset++; return; }
        if(u.pathname!==here && u.pathname!==self) out.sibling.push(where+' '+h+' -> '+u.pathname);
      });
    }
    SCREEN_ORDER.forEach(function(sc){
      var meta=STATE_META[sc]||{'default':null};
      Object.keys(meta).forEach(function(st){ go(sc,st); scan(sc+'/'+st); });
    });
    var d=document.querySelector('[data-act=dock-toggle]');
    if(d){ go('invest-assets','default'); d.click(); scan('dock/open'); d.click(); }
    go('invest-assets','default');
    out.offsite=out.offsite.filter(function(v,i,a){return a.indexOf(v)===i;});
    return out;
  `);
  const badHosts = esc.offsite.filter(h => ALLOWED_HOSTS.indexOf(h) < 0);
  check('형제 문서 링크 0', esc.sibling.length === 0, esc.sibling.slice(0, 4).join(' | '));
  check('금칙 문자열 링크 0', esc.banned.length === 0, esc.banned.slice(0, 4).join(' | '));
  check('허용 밖 외부 호스트 0', badHosts.length === 0, badHosts.join(','));
  console.log('       (링크 총 ' + esc.total + ' — 해시 ' + esc.hash + ' · 자산 ' + esc.asset +
              ' · 허용 외부 ' + esc.offsite.join(',') + ')');

  /* 5) 엑셀 레지스터 전건 실물 수신 — 바이트 일치.
        어느 버튼이 어느 파일을 주는지는 게이트가 알지 않는다. 하드코딩하면 또 낡는다:
        D-14 로 주별·월별이 생겼는데 전용 버튼(data-xls=profit-weekly/monthly)이 없다 —
        일별 버튼 하나가 PF.gran 에 따라 갈린다(app.html: var PROFIT_XLS, ACT['xls-open']).
        그래서 pullFile 을 잠시 가로채 화면·상태를 돌며 "이 버튼이 무슨 파일을 부르는가"를 앱에게 물어 경로를 찾고,
        찾은 경로로 진짜 클릭해 받는다. XLSX 에 항목이 늘어도 경로는 저절로 따라온다. */
  /* file 이 없는 자리는 도달 경로를 따질 대상이 아니다 */
  const meta = (await ev('return Object.keys(XLSX).map(function(k){ return {key:k, file:XLSX[k].file}; });'))
                 .filter(m => !!m.file);
  const norm = x => x.normalize('NFC');
  /* 조합 = 화면·상태 + (투자 수익은) 그 화면의 프리셋 칩까지.
     투자 수익 엑셀은 프리셋마다 파일이 갈리므로 상태만 돌면 절반이 도달 경로 없음으로 남는다.
     프리셋 목록도 화면이 스스로 갖고 있는 것을 받아 쓴다 — 게이트에 기간을 적지 않는다. */
  const combos = await ev(`
    var out=[];
    SCREEN_ORDER.forEach(function(s){
      var m=STATE_META[s]||{'default':null};
      Object.keys(m).forEach(function(t){
        go(s,t);
        var sec=document.querySelector('section.screen[data-screen="'+s+'"]');
        var n=sec?sec.querySelectorAll('[data-act="xls-open"]').length:0;
        if(!n) return;
        var pres=[].map.call(sec.querySelectorAll('.preset-btn'), function(b){ return b.dataset.preset; });
        if(pres.length) pres.forEach(function(p){ out.push([s,t,n,p]); });
        else out.push([s,t,n,null]);
      });
    });
    go('invest-assets','default');
    return out;
  `);
  await ev('window.__pull=[]; if(!window.__pullOrig){ window.__pullOrig=pullFile;' +
           ' pullFile=function(d,n){ window.__pull.push(n); }; } return 1;');
  const route = {};                       /* 파일명 -> {s:화면, t:상태, p:프리셋, i:버튼 순번} */
  /* 화면을 세우고 프리셋 칩을 누르는 것을 한 틱에 몰지 않는다 — 해시 갱신이 겹치면 마지막 해시가
     상태를 다시 심어, 방금 누른 프리셋이 아니라 그 상태의 씨앗 기간이 잡힌다. */
  for(const [s, t, n, p] of combos){
    for(let i = 0; i < n; i++){
      await ev(`go(${JSON.stringify(s)},${JSON.stringify(t)}); return 1;`);
      await sleep(120);
      if(p){
        await ev(`var b=document.querySelector('section.screen[data-screen="'+${JSON.stringify(s)}+
                  '"] .preset-btn[data-preset="'+${JSON.stringify(p)}+'"]');
                  if(b){ var g=document.querySelector('[data-act=pf-gran][data-gran="'+PRESET_GRAN[${JSON.stringify(p)}]+'"]');
                         if(g) g.click(); }
                  return 1;`);
        await sleep(120);
        await ev(`var b=document.querySelector('section.screen[data-screen="'+${JSON.stringify(s)}+
                  '"] .preset-btn[data-preset="'+${JSON.stringify(p)}+'"]');
                  if(b) b.click(); return 1;`);
        await sleep(120);
      }
      const pulled = await ev(`
        var b=document.querySelector('section.screen[data-screen="'+${JSON.stringify(s)}+'"]')
              .querySelectorAll('[data-act="xls-open"]')[${i}];
        if(!b || b.disabled) return [];
        window.__pull=[]; b.click(); return window.__pull.slice();`);
      await sleep(400);                   /* xlsBusy 가 350ms 동안 버튼을 잠근다 */
      pulled.forEach(f => { if(!route[f]) route[f] = {s:s, t:t, p:p, i:i}; });
    }
  }
  const noRoute = meta.filter(m => !route[m.file]).map(m => m.key + ' 도달 경로 없음');
  const stray = Object.keys(route).filter(f => !meta.some(m => m.file === f)).map(f => '레지스터 밖 ' + f);
  check('엑셀 도달 경로 (레지스터 ' + meta.length + '종 ↔ 화면 버튼)',
        noRoute.length === 0 && stray.length === 0, noRoute.concat(stray).join(' | '));

  for(const m of meta){
    const r = route[m.file];
    const src = path.join(REPO, 'assets/xlsx', m.file);
    const want = fs.existsSync(src) ? fs.statSync(src).size : -1;
    if(!r){ check('엑셀 ' + m.key, false, '도달 경로 없음 / 원본 ' + want + 'B'); continue; }
    fs.readdirSync(DL).forEach(f => { try{ fs.unlinkSync(path.join(DL, f)); }catch(e){} });
    await send('Page.navigate', {url: TARGET}); await sleep(1600);
    await send('Browser.setDownloadBehavior', {behavior:'allow', downloadPath: DL});
    await ev(`go(${JSON.stringify(r.s)},${JSON.stringify(r.t)}); return 1;`);
    await sleep(120);
    if(r.p){
      await ev(`var g=document.querySelector('[data-act=pf-gran][data-gran="'+PRESET_GRAN[${JSON.stringify(r.p)}]+'"]');
                if(g) g.click(); return 1;`);
      await sleep(120);
      await ev(`var b=document.querySelector('.preset-btn[data-preset="'+${JSON.stringify(r.p)}+'"]');
                if(b) b.click(); return 1;`);
      await sleep(120);
    }
    const clicked = await ev(`
      var b=document.querySelector('section.screen[data-screen="'+${JSON.stringify(r.s)}+'"]')
            .querySelectorAll('[data-act="xls-open"]')[${r.i}];
      if(!b) return '없음'; b.click(); return 'ok';`);
    let got = null;
    for(let i = 0; i < 30 && !got; i++){
      await sleep(200);
      const hit = fs.readdirSync(DL).find(f => !f.endsWith('.crdownload') && norm(f).replace(/ \(\d+\)/, '') === norm(m.file));
      if(hit && fs.statSync(path.join(DL, hit)).size > 0) got = path.join(DL, hit);
    }
    check('엑셀 ' + m.key, clicked === 'ok' && !!got && fs.statSync(got).size === want,
          (got ? fs.statSync(got).size : 0) + 'B / 원본 ' + want + 'B  <- ' + r.s + '/' + r.t +
          (r.p ? '/' + r.p : '') + ' #' + r.i);
  }

  /* 6) 콘솔 · 가로 오버플로 · 숫자 */
  await send('Page.navigate', {url: TARGET}); await sleep(1800);
  const of = await ev(`
    var bad=[];
    SCREEN_ORDER.forEach(function(sc){
      go(sc,'default');
      if(document.documentElement.scrollWidth > document.documentElement.clientWidth + 1)
        bad.push(sc+' '+document.documentElement.scrollWidth+'>'+document.documentElement.clientWidth);
    });
    go('invest-assets','default'); return bad;
  `);
  check('가로 오버플로 0', of.length === 0, of.join(' | '));
  const sc = await ev('return window.__selfcheck();');
  check('비중 합 100.0%', sc.ratioSum === 100, String(sc.ratioSum));
  check('투자실행금 화면 간 일치', sc.execMatch === true, String(sc.assetExecRow));
  check('일별 원장 = 월별 롤업', sc.rollupMatchesLedger === true, sc.ledgerProfitSum + ' / ' + sc.monthRollupSum);
  /* 투자자산 대비 Ty수익율 — 게이트에 절대값을 **손으로** 박지 않는다. 원장에서 읽는다.
     2026-08-28 버킷 Ty 산식 정정으로 이 값이 2.24% -> 8.15% 로 움직였다
     (app.html tyAssetOf: PEC 를 기준일 잔액 1개(스톡)가 아니라 EC 일수만큼 쌓이는 유량으로 센다).
     숫자를 박아 두면 재산출 때마다 게이트가 깨지고, 그때 숫자만 갈아 끼우면 근거 없는 추인이 된다.

     [기준 교체 2026-09-02] 그래서 「화면이 스스로 내놓은 값끼리 맞는지」만 봤는데,
     되짚기의 재료가 표기 2자리 ④ 라 되짚은 값이 애초에 정확하지 않다(주간 want 2.244 ↔ 화면 2.25).
     그 갈림을 0.02 허용치가 삼켜, ⑤ 가 2.24 로 되돌아가도 게이트가 통과했다.
     기대값을 원장(ledger_facts.json)에서 읽어 표기값끼리 완전일치로 본다 — 기본 기간이 일주일이라
     weekTy(④) · weekTyAsset(⑤) 자리다. 원장이 다시 찍히면 기대값도 함께 움직여 추인이 생기지 않는다.
     되짚기 자체는 남긴다 — 툴팁 Σ(Ai×Di)·PEC 가 카드와 다른 기간을 말하는 것을 그 자리가 잡는다.
     기간 7종의 절대값은 verify_identity.js 가 따로 본다(대표 정의서 ⑤). */
  const ty = await ev(`
    go('invest-profit','default');
    var sec=document.querySelector('section.screen[data-screen="invest-profit"]');
    var box=sec.querySelector('.ty-split');
    if(!box) return {err:'ty-split 없음'};
    if(box.children.length!==2) return {err:'ty 칸 '+box.children.length+'개'};
    function num(t){ return Number(String(t).replace(/[^0-9.\\-]/g,'')); }
    var c0=box.children[0], c1=box.children[1], got={};
    Array.prototype.forEach.call(c1.querySelectorAll('.tip-row'), function(r){
      got[r.children[0].textContent.trim()] = num(r.children[1].textContent);
    });
    var four=num(c0.querySelector('.summary-value').textContent);
    var five=num(c1.querySelector('.summary-value').textContent);
    go('invest-assets','default');
    var adKey=Object.keys(got).filter(function(k){ return k.indexOf('Σ')===0; })[0];
    return {four:four, five:five, ad:got[adKey], psc:got['PEC'],
            label:c1.textContent.indexOf('투자자산 대비')>=0};
  `);
  const tyK = (ty && ty.ad + ty.psc) ? ty.ad / (ty.ad + ty.psc) : NaN;
  const tyWant = ty.four * tyK;
  /* 되짚기 허용치는 상수가 아니라 표기 반올림에서 유도한다 —
     ⑤ = r2(④6 x k) · ④ = r2(④6) 이므로 |⑤ - ④ x k| <= 0.005 x (1 + k) 다.
     이 자리에 허용치가 남는 이유는 재료인 ④ 가 이미 2자리로 잘려 있어서다(원 자리 반올림 2회).
     판별력은 바로 아래 원장 대조가 갖는다 — 그쪽에는 허용치가 없다. */
  const tyLim = 0.005 * (1 + (isNaN(tyK) ? 1 : tyK)) + 1e-9;
  check('연환산수익률 ⑤ = ④ x Σ(Ai×Di)/(Σ(Ai×Di)+PEC) — 툴팁 표기값으로 되짚기',
        !ty.err && ty.label === true && ty.four > 0 && ty.five > 0 && ty.five <= ty.four &&
        Math.abs(ty.five - tyWant) <= tyLim,
        JSON.stringify(ty) + ' want=' + (isNaN(tyWant) ? 'NaN' : tyWant.toFixed(3)) +
        ' lim=' + tyLim.toFixed(5));
  /* 원장 대조 — 기본 기간(일주일)의 ④·⑤ 표기값과 완전일치. 허용치 없음 */
  check('연환산수익률 ④ ⑤ = 원장 weekTy · weekTyAsset (기본 기간 일주일)',
        !ty.err && ty.four === Number(FACTS.weekTy) && ty.five === Number(FACTS.weekTyAsset),
        '④ ' + ty.four + '/' + FACTS.weekTy + ' · ⑤ ' + ty.five + '/' + FACTS.weekTyAsset);
  /* 툴팁 Σ(Ai×Di)·PEC 도 원장 기대값과 맞대 본다 — 카드와 툴팁이 다른 기간을 말하면 여기서 걸린다 */
  check('연환산수익률 툴팁 Σ(Ai×Di) · PEC = 원장 weekAD · weekPsc',
        ty.ad === FACTS.weekAD && ty.psc === FACTS.weekPsc,
        'Σ(Ai×Di) ' + ty.ad + '/' + FACTS.weekAD + ' · PEC ' + ty.psc + '/' + FACTS.weekPsc);
  check('콘솔 에러 0', consoleErrors.length === 0, consoleErrors.slice(0, 3).join(' | '));

  /* 화면·상태 수 — 고정 숫자를 박지 않는다.
     시연본이 원본에서 빼는 것은 PROTO_DROPPED 의 화면과 그 화면에 달린 상태뿐이다(sync_prototype.py).
     기준은 "원본 실측 - 그 목록" 이라 상태가 늘어도(D-14 invest-profit/weekly) 저절로 따라간다.
     덤으로 DOM 섹션 수 ↔ SCREEN_ORDER ↔ STATE_META 가 서로 어긋나지 않는지도 같이 본다. */
  const reg = await ev('return {order:SCREEN_ORDER.slice(), meta:Object.keys(STATE_META)};');
  const regBad = [];
  if(sc.screens !== reg.order.length) regBad.push('DOM 섹션 ' + sc.screens + ' ≠ SCREEN_ORDER ' + reg.order.length);
  if(reg.meta.length !== reg.order.length) regBad.push('STATE_META ' + reg.meta.length + ' ≠ SCREEN_ORDER ' + reg.order.length);
  if(sc.states !== walk.states) regBad.push('STATE_META 상태 ' + sc.states + ' ≠ 렌더 확인 ' + walk.states);
  let dropWant = PROTO_DROPPED, dropStates = 0;
  if(SRCREG){
    dropWant = SRCREG.order.filter(x => PROTO_DROPPED.indexOf(x) >= 0);   /* 원본 순서로 — 빠진 화면 목록과 그대로 맞댄다 */
    dropStates = dropWant.reduce((a, x) => a + (SRCREG.per[x] || 0), 0);
    const dropped = SRCREG.order.filter(x => reg.order.indexOf(x) < 0);
    if(JSON.stringify(dropped) !== JSON.stringify(dropWant))
      regBad.push('원본에서 빠진 화면 ' + JSON.stringify(dropped) + ' ≠ ' + JSON.stringify(dropWant));
    if(sc.screens !== SRCREG.screens - dropWant.length)
      regBad.push('화면 ' + sc.screens + ' ≠ 원본 ' + SRCREG.screens + ' - ' + dropWant.length);
    if(sc.states !== SRCREG.states - dropStates)
      regBad.push('상태 ' + sc.states + ' ≠ 원본 ' + SRCREG.states + ' - ' + dropStates);
  }
  check('화면·상태 = 원본 - ' + dropWant.join('·') + ' (' + sc.screens + '화면 · 상태 ' + sc.states + ')',
        regBad.length === 0, regBad.join(' | '));

  console.log(fails.length ? '\n게이트 실패 ' + fails.length + '건: ' + fails.join(', ')
                           : '\n게이트 통과 — 바깥으로 나가는 통로 0건.');
  ws.close(); chrome.kill(); server.close(); srcServer.close();
  process.exit(fails.length ? 1 : 0);
}
main().catch(e => { console.error('GATE ERROR', e); process.exit(1); });
