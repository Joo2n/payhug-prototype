/* payhug-investor-prototype/index.html(독립 시연 저장소) 헤드리스 검증 — 창을 띄우지 않는다(--headless=new).
   1) 사이드바 메뉴 전건 전환  2) 상태 클릭 시퀀스 도달  3) 엑셀 4건 실제 다운로드
   4) 죽은 버튼 전수 스캔  5) 정렬·필터 값 변화  6) 콘솔 에러 0                         */
const http = require('http');
const fs   = require('fs');
const path = require('path');
const os   = require('os');
const { spawn } = require('child_process');

const REPO = process.env.PROTO_REPO || '/Users/semi/cursor/payhug-investor-prototype';
const OUTDIR = '/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin';
/* 숫자 기대값은 검증기에 손으로 적지 않는다 — daily_ledger.py 가 내는 원장 사실값을 읽는다.
   verify_identity.js:13 · verify_period.js:14 와 같은 원천이다. */
const FACTS = JSON.parse(fs.readFileSync(path.join(OUTDIR, 'ledger_facts.json'), 'utf8'));
const ROSTER = FACTS.merchants.length;                    /* 가맹점 로스터 곳수 — 계약기록 건수도 같은 명단이다 */
/* 가맹점 검색 예시어 `곱창` 에 걸리는 곳수 — 검증기에 적지 않고 원장 명단에서 센다.
   로스터가 바뀌면 걸리는 곳수도 같이 바뀐다. */
const MC_KW = '곱창';
const MC_HITS = FACTS.merchants.filter(m => String(m[0]).indexOf(MC_KW) >= 0).length;
const TOTAL_TXT = FACTS.total.toLocaleString('en-US');    /* 투자자산 = 투자실행액 + 순현금 */
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

  const TARGET = process.env.PROTO_URL || ('http://127.0.0.1:' + PORT + '/index.html');
  await send('Page.navigate', {url: TARGET});
  await sleep(1800);

  const R = {menus:[], states:[], downloads:[], dead:[], data:[], selfcheck:null, console:[]};

  /* ── 자체 점검 ── */
  R.selfcheck = await evalJS('return window.__selfcheck();');

  /* ── 1) 사이드바 메뉴 전건 ──
     메뉴 수를 숫자로 박지 않는다. 사이드바에 실제로 걸린 .nav-item 을 세고,
     화면은 MENU_OF 를 뒤집어(메뉴 → 그 메뉴의 첫 화면) 가져온다. 메뉴가 늘면 검사도 저절로 늘어난다.
     쿠콘 관리 현금은 SPA 전환이 아니라 We-bank 외부 링크다(D-14) — 링크 자체를 따로 본다. */
  const kc = await evalJS(
    'var a=document.querySelector(\'.nav-item[data-menu="kcoon"]\');' +
    'return a ? {href:a.getAttribute("href"), target:a.getAttribute("target"), rel:a.getAttribute("rel"),' +
    ' label:a.textContent.trim()} : null;');
  /* `if(kc)` 로 감싸 두면 메뉴가 통째로 사라졌을 때 검사가 그냥 건너뛰어져 통과한다(2026-08-30 수정).
     없으면 없다고 실패로 남긴다 — 형제 verify_app.js 는 감싸지 않아 예외로 죽는다. */
  R.menus.push({menu:'kcoon', screen:'(외부)', label:'쿠콘 관리 현금', ...(kc || {없음:true}),
    pass: !!kc && /we-bank\.co\.kr/.test(kc.href || '') && kc.target === '_blank'
          && (kc.rel || '').indexOf('noopener') >= 0 && kc.label.indexOf('쿠콘 관리 현금') === 0});
  const MENUS = await evalJS(`
    var rev = {}, s;
    for(s in MENU_OF){ if(MENU_OF[s] && !(MENU_OF[s] in rev)) rev[MENU_OF[s]] = s; }
    var out = [];
    Array.prototype.forEach.call(document.querySelectorAll('.sidebar .nav-item[data-menu]'), function(a){
      if(a.getAttribute('target') === '_blank') return;
      out.push([a.dataset.menu, rev[a.dataset.menu] || '', a.querySelector('span').textContent.trim()]);
    });
    return out;`);
  /* 사이드바에서 메뉴가 통째로 사라지면 MENUS 가 같이 줄어 아래 for 문이 덜 돌 뿐 아무것도 실패하지 않는다.
     기준은 검증기가 정하지 않는다 — 앱이 스스로 선언한 MENU_OF 의 서로 다른 메뉴 값이
     사이드바에 하나씩 있어야 한다. 곳수를 박지 않는다(verify_app.js 와 같은 판정). */
  const menuDecl = await evalJS(
    "var v={}; Object.keys(MENU_OF).forEach(function(k){ if(MENU_OF[k]) v[MENU_OF[k]]=1; });" +
    "var dom=[].map.call(document.querySelectorAll('.sidebar .nav-item[data-menu]'), function(e){ return e.dataset.menu; });" +
    "return {want:Object.keys(v).sort(), got:dom.slice().sort(), dup:dom.length!==new Set(dom).size};");
  R.menus.push({menu:'(사이드바 구성)', screen:'-', label:'선언된 메뉴 전건이 사이드바에 하나씩',
    선언:menuDecl.want, 그려진것:menuDecl.got,
    pass: JSON.stringify(menuDecl.want) === JSON.stringify(menuDecl.got) && !menuDecl.dup});
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

  /* ── 2) 상태 전건: 실제 클릭 시퀀스 ──
     쿠콘은 여기 없다. D-14 로 SPA 전이가 사라져 링크 검사로 뒤집었다 — 아래 2-b. */
  const SEQ = [
    ['invest-assets','download', [
      ['nav','.nav-item[data-menu="invest-assets"]'],
      ['click','[data-mount="ia-xls-merchant"]'],
      ['wait', 600]]],
    ['invest-assets','cert-confirm', [
      ['nav','.nav-item[data-menu="invest-assets"]'],
      ['click','[data-act="cert-open"]']]],
    ['invest-assets','empty', [
      ['hash','#invest-assets/empty']]],
    ['invest-profit','monthly', [
      ['nav','.nav-item[data-menu="invest-returns"]'],
      ['click','[data-act="pf-gran"][data-gran="monthly"]']]],
    ['invest-profit','empty', [
      ['nav','.nav-item[data-menu="invest-returns"]'],
      ['change','[data-mount="pf-from"]','2026-02-01'],
      ['change','[data-mount="pf-to"]','2026-02-07']]],
    ['invest-sim','result', [
      ['nav','.nav-item[data-menu="invest-sim"]'],
      ['click','[data-mount="sim-go"]'],
      ['wait', 500]]],
    ['merchants','filtered', [
      ['nav','.nav-item[data-menu="merchants"]'],
      ['change','[data-mount="mc-sector"]','음식점업'],
      ['type','[data-mount="mc-kw"]','곱창'],
      ['click','[data-act="mc-search"]']]],
    ['merchants','empty', [
      ['nav','.nav-item[data-menu="merchants"]'],
      ['type','[data-mount="mc-kw"]','라멘'],
      ['click','[data-act="mc-search"]']]],
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
    /* 세 칸 다 비어서 열린다(원본과 같다) — 현재 비밀번호까지 쳐 넣어야 제출이 열린다.
       pwCanSubmit() = PW.cur !== '' && pwIsValid(PW.nw) && pwCfmMatched().
       verify_password.js:317-320 이 "현재 비밀번호 비면 제출 잠김"을 이미 못 박고 있고
       verify_app.js:199-205 도 pw-cur 를 먼저 친다. 여기만 그 칸이 빠져 있었다. */
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
      if(st[0] === 'hash'){ await evalJS('location.hash=' + JSON.stringify(st[1]) + '; return 1;'); await sleep(160); continue; }
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
    /* 기대(want)를 got 이 덮어써 FAIL 줄이 "기대=실측"으로 보이던 것을 분리한다. 판정 기준은 그대로. */
    R.states.push({screen, want: state, ...got, err,
      steps: steps.map(s => s[0] === 'wait' ? 'wait ' + s[1] + 'ms' : s[0] + ' ' + s[1] + (s[2] ? ' = ' + s[2] : '')).join(' → '),
      pass: !err && got.visible && got.state === state});
  }

  /* ── 2-b) 쿠콘 = 외부 링크 (옛 coocon/confirm 자리) ──
     D-14 「쿠콘 관리 현금 = 설명 전량 삭제. 메뉴 클릭 시 바로 쿠콘 이동」으로 중간 확인 화면이 사라졌다.
     coocon/confirm 상태도, coocon--confirm.html 도 그때 없어졌다. SPA 전이를 기대하면 영원히 FAIL 이고,
     target=_blank 를 그냥 누르면 새 탭이 열려 검증기가 흔들린다 — 그래서 전이가 아니라 나가는 링크를 본다.
     같은 기준: verify_app.js:88-104 · gate_prototype.js:129-159.
     검사를 뺀 것이 아니다. 아래 6가지를 전부 만족해야 PASS 다.
       ① 앱이 선언한 coocon 상태(STATE_META)가 default 하나뿐 ② coocon-confirm 모달이 문서에 없음
       ③ 사이드바 kcoon 이 https we-bank 절대주소 + _blank + noopener
       ④ 쿠콘 화면 안 We-bank 버튼도 같은 외부 링크
       ⑤ 실제로 눌러도(기본동작만 막고) SPA 화면·해시가 전혀 움직이지 않음
       ⑥ 쿠콘 화면이 default 그대로 */
  {
    const cc = await evalJS(`
      go('invest-assets','default');
      var st  = (typeof STATE_META !== 'undefined' && STATE_META['coocon']) ? Object.keys(STATE_META['coocon']) : null;
      var nav = document.querySelector('.nav-item[data-menu="kcoon"]');
      go('coocon','default');
      var btn = document.querySelector('section.screen[data-screen="coocon"] a.btn-primary[target="_blank"]');
      var sec = document.querySelector('section.screen[data-screen="coocon"]');
      var stateBefore = sec.dataset.state;
      go('invest-assets','default');
      var before = {active:document.body.dataset.active, view:document.body.dataset.view, hash:location.hash};
      /* 기본 동작(새 탭)만 막고 실제로 누른다 — 캡처 단계라 앱의 위임 핸들러보다 먼저 걸린다.
         DOM 만 읽지 않는다: 눌러도 SPA 가 움직이지 않는다는 것을 실측한다. */
      var block = function(e){ e.preventDefault(); };
      document.addEventListener('click', block, true);
      nav.click();
      document.removeEventListener('click', block, true);
      var after = {active:document.body.dataset.active, view:document.body.dataset.view, hash:location.hash};
      go('invest-assets','default');
      var abs = function(a){
        if(!a) return null;
        var h = a.getAttribute('href') || '', u = null;
        try{ u = new URL(h); }catch(e){}
        return {href:h, ok: !!u && u.protocol === 'https:' && u.host === 'www.we-bank.co.kr',
                target:a.getAttribute('target'), rel:a.getAttribute('rel') || ''};
      };
      return {states:st, modal:!!document.querySelector('[data-modal="coocon-confirm"]'),
              nav:abs(nav), btn:abs(btn), stateBefore:stateBefore, before:before, after:after};
    `);
    const linkOK = l => !!l && l.ok && l.target === '_blank' && l.rel.indexOf('noopener') >= 0;
    const noMove = JSON.stringify(cc.before) === JSON.stringify(cc.after);
    R.states.push({screen:'coocon', want:'(외부링크·D-14)', state:'(외부링크·D-14)', visible:true,
      declaredStates: cc.states, modal: cc.modal, nav: cc.nav, btn: cc.btn,
      before: cc.before, after: cc.after,
      steps: 'STATE_META.coocon 확인 → 링크 속성 확인 → kcoon 클릭(기본동작 차단) → SPA 무변동 확인',
      err: null,
      pass: JSON.stringify(cc.states) === JSON.stringify(['default']) && cc.modal === false
            && linkOK(cc.nav) && linkOK(cc.btn) && noMove && cc.stateBefore === 'default'});
  }

  /* ── 3) 엑셀 — 원본처럼 중간 화면 없이 즉시 파일이 나오는지 실측 ──
     판정 = 실물 파일이 디스크에 떨어지고(바이트 일치) 화면이 미리보기로 넘어가지 않는다.
     조합은 시연본이 스스로 갖고 있는 프리셋 표에서 가져온다 — 기간을 검증기에 손으로 적지 않는다.
     파일명이 그 프리셋의 시작일·종료일을 달고 있는지도 함께 본다.
     화면은 27행 금월인데 파일은 일주일치가 나가던 자리가 여기서 걸린다. */
  const PRESETS = await evalJS(`
    var out = [];
    for(var k in PRESET_RANGE)
      out.push({k:k, gran:PRESET_GRAN[k], label:PRESET_LABEL[k],
                from:PRESET_RANGE[k][0], to:PRESET_RANGE[k][1]});
    return out;`);
  const CASES = [
    {key:'assets-status',   screen:'invest-assets', state:'default', file:'투자자산현황_2026-08-27_2026-08-27.xlsx'},
    {key:'assets-merchant', screen:'invest-assets', state:'default', file:'가맹점별투자자산_2026-08-27_2026-08-27.xlsx'}
  ];
  for(const p of PRESETS)
    for(const key of ['profit-status', 'profit-daily'])
      CASES.push({key, screen:'invest-profit', state:'default', preset:p});
  for(const c of CASES){
    fs.readdirSync(DL).forEach(f => { try{ fs.unlinkSync(path.join(DL, f)); }catch(e){} });
    /* 한 번에 하나씩 누른다 — 한 틱에 몰면 해시 갱신이 겹쳐 마지막 해시가 상태를 다시 심는다 */
    await evalJS('go(' + JSON.stringify(c.screen) + ', ' + JSON.stringify(c.state) + '); return 1;');
    await sleep(150);
    if(c.preset){
      await evalJS(`document.querySelector('[data-act=pf-gran][data-gran=${c.preset.gran}]').click(); return 1;`);
      await sleep(150);
      await evalJS(`document.querySelector('[data-act=preset][data-preset=${c.preset.k}]').click(); return 1;`);
      await sleep(150);
      const got = await evalJS(`var k = xlsKey(${JSON.stringify(c.key)});
        return {from:PF.from, to:PF.to, gran:PF.gran, file:k ? XLSX[k].file : null};`);
      c.file = got.file;
      c.periodOk = !!got.file && got.from === c.preset.from && got.to === c.preset.to
                   && got.gran === c.preset.gran
                   && got.file.indexOf('_' + c.preset.from + '_' + c.preset.to + '.xlsx') > 0;
    } else {
      c.periodOk = true;
    }
    await sleep(150);
    const click = c.file ? await evalJS('var b=document.querySelector(\'[data-act="xls-open"][data-xls="' + c.key + '"]\');' +
      'if(!b) return "missing"; b.click(); return "ok";') : '파일 없음';
    await sleep(120);
    const view = await evalJS('return document.body.dataset.view;');
    let got = null;
    for(let i = 0; i < 25 && !got && c.file; i++){
      await sleep(200);
      const f = path.join(DL, c.file);
      if(fs.existsSync(f) && fs.statSync(f).size > 0) got = f;
    }
    await sleep(500);
    const src = c.file ? path.join(REPO, 'assets/xlsx', c.file) : null;
    const direct = (view === c.screen);
    R.downloads.push({key:c.key + '/' + (c.preset ? c.preset.label : c.state), expect:c.file,
      기간:c.preset ? c.preset.from + '~' + c.preset.to : '기준일', 기간일치:c.periodOk,
      click, viewAfter:view, noPreviewScreen:direct,
      file: got ? path.basename(got) : null,
      bytes: got ? fs.statSync(got).size : 0,
      srcBytes: src && fs.existsSync(src) ? fs.statSync(src).size : -1,
      pass: !!got && direct && c.periodOk && fs.statSync(got).size === fs.statSync(src).size});
  }

  /* 프리셋 밖 기간(직접입력)에는 실물이 없다 — 버튼이 잠기고 토스트도 나오지 않는다(D-39) */
  {
    fs.readdirSync(DL).forEach(f => { try{ fs.unlinkSync(path.join(DL, f)); }catch(e){} });
    const off = await evalJS(`
      go('invest-profit','default');
      var sec = document.querySelector('section[data-screen="invest-profit"]');
      var t = document.querySelector('[data-mount=toast]');
      var ti = sec.querySelector('[data-mount=pf-to]');
      ti.value = '2026-08-25'; ti.dispatchEvent(new Event('change',{bubbles:true}));
      hideToast();
      var x1 = sec.querySelector('[data-mount=pf-xls1]'), x2 = sec.querySelector('[data-mount=pf-xls2]');
      var st = {label:(sec.querySelector('.stat-period')||{}).textContent,
                keys:[xlsKey('profit-status'), xlsKey('profit-daily')],
                lock:[!!x1.disabled, !!x2.disabled], cursor:getComputedStyle(x1).cursor};
      x1.click(); x2.click();
      st.toastHidden = t.hidden;
      return st;`);
    await sleep(600);
    const dropped = fs.readdirSync(DL).filter(f => f.endsWith('.xlsx'));
    R.downloads.push({key:'profit/직접입력 — 실물 없는 기간', expect:'없음',
      라벨:off.label, 열쇠:off.keys, 잠금:off.lock, cursor:off.cursor,
      토스트숨김:off.toastHidden, 떨어진파일:dropped,
      pass: off.label === '직접입력' && off.keys[0] === null && off.keys[1] === null
            && off.lock[0] && off.lock[1] && off.cursor === 'not-allowed'
            && off.toastHidden && dropped.length === 0});
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
    var TARGETS=[['invest-assets','default'],['invest-assets','empty'],['invest-assets','cert-confirm'],
      ['invest-profit','default'],['invest-profit','monthly'],['invest-profit','empty'],
      ['invest-sim','default'],['invest-sim','result'],
      ['merchants','default'],['merchants','filtered'],['merchants','empty'],
      ['acquisition-list','default'],['acquisition-list','confirm'],['acquisition-list','done'],
      ['contracts','default'],['contracts','all'],['contracts','empty'],
      ['coocon','default'],['password','default'],['password','weak'],['password','done'],
      ['certificate','default'],['xls-assets-status','default'],['xls-assets-merchant','default'],
      ['xls-profit-status','default'],['xls-profit-daily','default'],['login','default']];
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
      var ab=document.querySelector('[data-mount=action-bar]');
      if(ab && !ab.hidden) Array.prototype.push.apply(pool, ab.querySelectorAll('*'));
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
            /* 키보드·보조기술로 닿을 수 없는 컨트롤 */
            if(!nativeCtl(e) && !e.hasAttribute('role') && !e.hasAttribute('tabindex') && !seen['A'+k]){
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

  /* ── 5) 정렬·필터가 실제로 값을 바꾸는지 ── */
  try { R.data = await evalJS(`
    var out=[];
    function firstCell(sel,col){ var r=document.querySelectorAll(sel+' tbody tr'); return r.length? r[0].children[col].textContent.trim():null; }
    /* D-28 「열 정렬 머리글 전량 철거」 — 실제 어드민(payhug-admin-web)에 열 정렬이 0건이라 우리가 넣은 것은 임의 생성이었다.
       옛 기준은 [data-act=sort] 를 눌러 오름/내림을 봤고, 컨트롤이 사라진 뒤로 셀렉터가 null 이라
       이 블록 전체가 예외로 떨어져 SKIP 으로 가려져 있었다. 기대값만 새 동작으로 뒤집는다.
       ① 정렬 머리글·정렬 아이콘이 정말 0건 ② 그 자리를 대신한 보기 갯수(D-25·D-29)가 즉시 다시 그린다.
       verify_app.js:387-411 과 같은 기준. */
    var sortLeft=document.querySelectorAll('[data-act=sort], th[data-key][role=button], .sort-icon').length;
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
        ok: opts.join(',')==='10,20,50' && n10===Math.min(10,${ROSTER}) && n20===${ROSTER} && n50===${ROSTER} && pgs===0});
      go(t[0],'default');
    });
    go('invest-assets','default');
    out.push({case:'열 정렬 머리글 0건(D-28) · 보기 갯수 10/20/50 이 즉시 다시 그린다(D-25·D-29)',
      sortLeft:sortLeft, 표:szOut,
      pass: sortLeft===0 && szOut.every(function(x){ return x.ok; })});

    go('merchants','default');
    var m0=document.querySelectorAll('[data-mount=mc-tbl] tbody tr').length;
    var t0=document.querySelector('[data-mount=mc-page]').textContent.replace(/\\s+/g,'');
    document.querySelector('[data-mount=mc-kw]').value='곱창';
    document.querySelector('[data-act=mc-search]').click();
    var m1=document.querySelectorAll('[data-mount=mc-tbl] tbody tr').length;
    var t1=document.querySelector('[data-mount=mc-page]').textContent.replace(/\\s+/g,'');
    /* D-29 로 보기 갯수 드롭다운(10/20/50·기본 10)이 생기면서 첫 페이지가 8행 → 10행이 됐다. */
    out.push({case:'가맹점 검색어 필터', rowsBefore:m0, rowsAfter:m1, countBefore:t0, countAfter:t1,
      pass: m0===Math.min(10,${ROSTER}) && m1===${MC_HITS} && t0.indexOf('총${ROSTER}건')>=0 && t1.indexOf('총${MC_HITS}건')>=0});

    /* D-34 「기간 필터 = 집계 단위가 곧 스냅 단위. 일별·주별·월별 3단」으로 프리셋이 갈렸다.
       옛 기준의 data-preset=yesterday 는 그 개편 때 없어졌고, 셀렉터가 null 이라 이 블록 전체가
       예외로 떨어져 SKIP 으로 가려져 있었다. 현행 프리셋(일별 = 일주일·금월)으로 기대값만 옮긴다.
       설계 정본 period_design.md · 전건 검사는 verify_period.js:141-160. */
    go('invest-profit','default');
    function foot(){ var f=document.querySelector('[data-mount=pf-tbl] tfoot tr'); return f? Array.prototype.map.call(f.children,function(c){return c.textContent.trim();}) : null; }
    var w=foot(), wr=document.querySelectorAll('[data-mount=pf-tbl] tbody tr').length;
    document.querySelector('[data-act=preset][data-preset=month]').click();
    var y=foot(), yr=document.querySelectorAll('[data-mount=pf-tbl] tbody tr').length;
    /* 프리셋을 보고 있을 때 단위를 바꾸면 새 단위의 같은 자리 프리셋으로 넘어간다 —
       금월은 일별 묶음의 긴 쪽이라 월별에서는 6개월이 켜지고 기간이 통째로 갈린다.
       기간을 유지한 채 단위만 보려면 직접 고른 기간이어야 한다(아래 두 번째 묶음). */
    document.querySelector('[data-act=pf-gran][data-gran=monthly]').click();
    var mo=foot(), mr=document.querySelectorAll('[data-mount=pf-tbl] tbody tr').length;
    var moLabel=(document.querySelector('[data-mount=pf-stat] .stat-period')||{}).textContent;
    /* 2026-06-01 은 월요일이자 그 달 1일이라 세 단위의 스냅을 모두 통과한다 */
    go('invest-profit','default');
    var s2=document.querySelector('section.screen[data-screen=invest-profit]');
    function put2(m,v){ var el=s2.querySelector('[data-mount='+m+']'); el.value=v; el.dispatchEvent(new Event('change',{bubbles:true})); }
    put2('pf-from','2026-06-01'); put2('pf-to','2026-08-27');
    var kd=foot(), kdr=document.querySelectorAll('[data-mount=pf-tbl] tbody tr').length;
    document.querySelector('[data-act=pf-gran][data-gran=monthly]').click();
    var km=foot(), kmr=document.querySelectorAll('[data-mount=pf-tbl] tbody tr').length;
    out.push({case:'기간·집계 단위 변경 시 합계 재계산', weekRows:wr, weekFoot:w, monthPresetRows:yr, monthPresetFoot:y,
      monthlyRows:mr, monthlyFoot:mo, monthlyLabel:moLabel,
      keepRows:[kdr, kmr], keepFoot:[kd && kd[3], km && km[3]],
      pass: wr===7 && yr===27 && mr===6 && moLabel==='6개월' && w[3]!==y[3] && y[3]!==mo[3]
            && kdr===88 && kmr===3 && kd[3]===km[3]});

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

    /* 역전 범위 방어 — 달력을 min/max 로 잠그던 방식이 폐기됐다. 어느 단위에서도 피커는 살아 있어야 하고
       (D-34 · verify_period.js:244-256), 역전은 안내문 + 조회 버튼 비활성으로 막는다(verify_period.js:257-261).
       느슨해진 것이 아니라 반대다 — 잠금이 하나라도 남아 있으면 FAIL 이다. */
    go('invest-profit','default');
    fi=document.querySelector('[data-mount=pf-from]'); ti=document.querySelector('[data-mount=pf-to]');
    var clamp=[fi.getAttribute('min'), fi.getAttribute('max'), ti.getAttribute('min'), ti.getAttribute('max')];
    fi.value='2026-09-30'; fi.dispatchEvent(new Event('change',{bubbles:true}));
    var warn=document.querySelector('[data-mount=pf-warn]');
    var go1=document.querySelector('[data-act=pf-search]');
    var alive=!fi.disabled && !fi.readOnly && !ti.disabled && !ti.readOnly;
    out.push({case:'역전 범위 방어 — 달력 잠금 0 · 안내문 · 버튼 비활성',
      clamp:clamp, pickerAlive:alive, warnShown:!warn.hidden, searchDisabled:!!go1.disabled,
      pass: clamp.every(function(v){ return v===null; }) && alive && !warn.hidden && !!go1.disabled});
    go('invest-profit','default');

    /* 검색창 Enter 가 조회를 실행하는지 */
    go('merchants','default');
    var kw=document.querySelector('[data-mount=mc-kw]');
    kw.value='곱창'; kw.dispatchEvent(new Event('input',{bubbles:true}));
    kw.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true}));
    var eRows=document.querySelectorAll('[data-mount=mc-tbl] tbody tr').length;
    out.push({case:'검색창 Enter → 조회 실행', rows:eRows, pass: eRows===${MC_HITS}});
    go('merchants','default');

    /* 모달 배경 클릭으로는 닫히지 않는다 (D-40)
       근거 = request_register.md D-40 「모달은 닫기 버튼·X 로만 닫힌다. 오버레이(배경) 클릭·모달 안쪽
       클릭·ESC 로는 닫히지 않는다」 (사용자 지시 "무조건 닫기나 x눌러야 닫히게 해").
       옛 기대 「배경 클릭 = 닫힘, 진행 오버레이만 예외」 는 D-40 이전 동작이라 기대값을 뒤집는다.
       대상 모달은 손으로 적지 않고 앱이 들고 있는 MODAL_OF 로 역산한다 — verify_app.js:540 과 같은 방식.
       (옛 코드는 3건을 손으로 박아 doc·signing 두 모달을 보지 않았다. MODAL_OF 로 5건 전수가 된다.)
       닫는 경로가 실제로 살아 있는지는 아래 11) 모달 닫힘 경로가 본다 — 안 닫히는 것만 보고 끝내면
       모달이 영영 안 닫혀도 통과한다. */
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
    /* 진행 오버레이는 D-40 이전에도 닫히면 안 됐다 — 같은 자리에서 한 번 더 못 박는다 */
    go('acquisition-list','signing');
    var sg=document.querySelector('[data-modal]:not([hidden])');
    if(sg) sg.click();
    var sgStill=!!document.querySelector('[data-modal="acquisition-signing"]:not([hidden])');
    go('invest-assets','default');
    out.push({case:'모달 배경 클릭으로 닫히지 않는다 (D-40)', closed:bdClose, kept:bdKeep, signingKept:sgStill,
      pass: bdClose.length===0 && bdKeep.length===Object.keys(MODAL_OF).length && sgStill===true});

    /* 메뉴 그룹 접힘 — 셰브론이 실제로 그룹을 접는지 */
    var gh=document.querySelector('[data-act=nav-group]');
    var g0=gh.closest('.nav-group').classList.contains('collapsed');
    gh.click();
    var g1=gh.closest('.nav-group').classList.contains('collapsed');
    var aria=gh.getAttribute('aria-expanded');
    gh.click();
    out.push({case:'메뉴 그룹 접힘', tag:gh.tagName, before:g0, after:g1, aria:aria,
      pass: gh.tagName==='BUTTON' && g0===false && g1===true && aria==='false'});

    /* 선택 건수를 알리던 [data-mount=ct-sel] 칩은 사라지고 다운로드 버튼 라벨 '선택 문서 다운로드 (N)' 과
       표 머리 체크박스 data-act=ct-all 로 바뀌었다. 세는 대상만 옮긴다 — 기본 3건 → 전체 선택 = 로스터 곳수. */
    go('contracts','default');
    function ctLab(){ return document.querySelector('[data-mount=ct-dl-label]').textContent.trim(); }
    var c0=ctLab(), cnt0=document.querySelector('[data-mount=ct-count]').textContent.replace(/\\s+/g,'');
    var head=document.querySelector('[data-act=ct-all]');
    var checked0=head.checked;
    head.click();
    var c1=ctLab(), checked1=document.querySelector('[data-act=ct-all]').checked;
    /* 고를 수 있는 행 = 서명이 끝난 계약. 서명 대기 큐에 남은 가맹점은 문서가 없어 체크박스가 잠긴다.
       기대값을 검증기에 적지 않는다 — 화면이 세는 수를 그대로 받는다. */
    var ctWant=ctSignedCount(CONTRACTS);
    var ctLocked=document.querySelectorAll('section[data-screen=contracts] tbody input.chk[disabled]').length;
    out.push({case:'계약기록 전체 선택 — 서명 완료 행만', before:c0, after:c1, count:cnt0,
      headChecked:[checked0, checked1], 고를수있는행:ctWant, 잠긴체크박스:ctLocked, 총행:CONTRACTS.length,
      pass: c0==='선택 문서 다운로드 (3)' && c1==='선택 문서 다운로드 ('+ctWant+')'
            && cnt0==='총${ROSTER}건' && checked0===false && checked1===true
            && ctLocked===CONTRACTS.length-ctWant});

    go('invest-assets','default');
    var s1=document.querySelector('[data-mount=ia-summary]').textContent.replace(/\\s+/g,' ');
    go('invest-assets','empty');
    var s2=document.querySelector('[data-mount=ia-summary]').textContent.replace(/\\s+/g,' ');
    out.push({case:'데이터 없음 상태 지표 0 치환', hasAmount:s1.indexOf('${TOTAL_TXT}')>=0, zeroed:s2.indexOf('${TOTAL_TXT}')<0,
      pass: s1.indexOf('${TOTAL_TXT}')>=0 && s2.indexOf('${TOTAL_TXT}')<0});
    go('invest-assets','default');
    return out;
  `); } catch(e){ R.data = [{case:'보기 갯수·필터 대조 — 셀렉터가 깨졌다', err:String(e.message).slice(0,200), pass:false}]; }

  /* ── 6) 화면·상태 조합 레이아웃 점검 ── */
  try { R.layout = await evalJS(`
    var T=[['invest-assets','default'],['invest-assets','download'],['invest-assets','cert-confirm'],['invest-assets','empty'],
      ['invest-profit','default'],['invest-profit','monthly'],['invest-profit','empty'],
      ['invest-sim','default'],['invest-sim','result'],
      ['merchants','default'],['merchants','filtered'],['merchants','empty'],
      ['acquisition-list','default'],['acquisition-list','confirm'],['acquisition-list','signing'],['acquisition-list','done'],
      ['contracts','default'],['contracts','all'],['contracts','empty'],
      ['coocon','default'],['password','default'],['password','weak'],['password','error'],['password','done'],
      ['certificate','default'],['xls-assets-status','default'],['xls-assets-merchant','default'],
      ['xls-profit-status','default'],['xls-profit-daily','default'],['login','default']];
    /* D-14 로 coocon/confirm 화면·coocon-confirm 모달이 없어졌다. 쿠콘은 2-b 에서 외부 링크로 본다. */
    var MOD={'invest-assets/cert-confirm':'invest-assets-cert-confirm','acquisition-list/confirm':'acquisition-confirm',
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
      /* 서명 액션바는 개편으로 고정 푸터에서 정산채권 양수 화면 안으로 들어왔다.
         hidden 속성이 아니라 실제로 눈에 보이는지로 본다 — 두 구성 모두에서 맞다. */
      var bar=document.querySelector('[data-mount=action-bar]');
      var barShown=!!(bar && !bar.hidden && bar.getClientRects().length>0);
      out.push({at:t[0]+'/'+t[1], h:Math.round(h), empties:empties, modals:vis, wantModal:want,
        barShown:barShown,
        pass: h>200 && vis.length===(want?1:0) && (!want||vis[0]===want) && barShown===(t[0]==='acquisition-list')});
    });
    go('invest-assets','default');
    return out;
  `); } catch(e){ R.layout = [{at:'레이아웃 조합 — 원본 화면 개편으로 셀렉터 불일치', err:String(e.message).slice(0,200), pass:false}]; }

  /* ── 7) 바깥으로 나가는 통로 전수 스캔 ──
     클릭 가능한 요소를 화면·상태 전 조합에서 훑어 문서 밖으로 나갈 수 있는 것을 모은다. */
  R.escape = await evalJS(`
    var TARGETS=[['invest-assets','default'],['invest-assets','download'],['invest-assets','cert-confirm'],['invest-assets','empty'],
      ['invest-profit','default'],['invest-profit','monthly'],['invest-profit','empty'],
      ['invest-sim','default'],['invest-sim','result'],
      ['merchants','default'],['merchants','filtered'],['merchants','empty'],
      ['acquisition-list','default'],['acquisition-list','confirm'],['acquisition-list','signing'],['acquisition-list','done'],
      ['contracts','default'],['contracts','all'],['contracts','empty'],
      ['coocon','default'],['password','default'],['password','weak'],['password','error'],['password','done'],
      ['certificate','default'],['xls-assets-status','default'],['xls-assets-merchant','default'],
      ['xls-profit-status','default'],['xls-profit-daily','default'],['login','default']];
    var BAD=/glossary|capability|feasibility|inquiry|archive|review/i;
    var here=location.pathname;
    var out={offsite:[], sibling:[], banned:[], asset:[], hash:0, total:0, docText:[]};
    var seen={};
    function scan(where){
      Array.prototype.forEach.call(document.querySelectorAll('a[href], area[href], form[action]'), function(e){
        if(e.getClientRects().length===0) return;
        var h=e.getAttribute('href')||e.getAttribute('action')||'';
        var k=where+' :: '+h; if(seen[k]) return; seen[k]=1;
        out.total++;
        if(BAD.test(h)) out.banned.push({where:where, href:h});
        if(h.charAt(0)==='#'){ out.hash++; return; }
        var u;
        try{ u=new URL(h, location.href); }catch(err){ out.sibling.push({where:where, href:h, why:'unparsable'}); return; }
        if(u.origin!==location.origin){ out.offsite.push({where:where, href:h, label:(e.textContent||'').trim().slice(0,20), target:e.getAttribute('target')||''}); return; }
        if(u.pathname.indexOf('/assets/')>=0){ out.asset.push({where:where, path:u.pathname}); return; }
        if(u.pathname!==here && h!=='index.html') out.sibling.push({where:where, href:h, resolved:u.pathname});
      });
      /* 화면에 적힌 문구 자체에 바깥 문서 이름이 남아 있는지 */
      var txt=document.body.innerText||'';
      ['용어 정리','문의서','구현 가능성','아카이브','순차 확인','화면 설계(안)'].forEach(function(w){
        if(txt.indexOf(w)>=0 && out.docText.indexOf(where+' :: '+w)<0) out.docText.push(where+' :: '+w);
      });
    }
    TARGETS.forEach(function(t){ go(t[0],t[1]); scan(t[0]+'/'+t[1]); });
    /* 도크를 연 상태도 훑는다 */
    go('invest-assets','default');
    var dk=document.querySelector('[data-act=dock-toggle]');
    if(dk){ dk.click(); scan('dock/open'); dk.click(); }
    var ds=document.querySelector('[data-mount=dock-screen]');
    out.dockOptions = ds ? Array.prototype.map.call(ds.options,function(o){return o.value;}) : '도크 없음';
    go('invest-assets','default');
    return out;
  `);

  /* ── 8) 가로 오버플로 ── */
  R.overflow = await evalJS(`
    var T=[['invest-assets','default'],['invest-assets','empty'],
      ['invest-profit','default'],['invest-profit','monthly'],['invest-sim','default'],['invest-sim','result'],
      ['merchants','default'],['merchants','filtered'],
      ['acquisition-list','default'],['acquisition-list','confirm'],['contracts','default'],['contracts','all'],
      ['coocon','default'],['password','default'],['certificate','default'],
      ['xls-assets-status','default'],['xls-assets-merchant','default'],['xls-profit-status','default'],['xls-profit-daily','default'],
      ['login','default']];
    var out=[];
    T.forEach(function(t){
      go(t[0],t[1]);
      out.push({at:t[0]+'/'+t[1], sw:document.documentElement.scrollWidth, cw:document.documentElement.clientWidth,
                pass: document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1});
    });
    go('invest-assets','default');
    return out;
  `);

  /* ── 9) 숫자 불변 — 화면에 뜨는 Ty수익율·W금융일수가 원장 사실값과 같은가 ──
     [기준 노후 교체] 예전 이 자리는 found224(2.24%) · found110000(0.110000) 두 상수를
     넣어 두고 출력만 했다 — PASS/FAIL 판정에 쓰지 않았고, 둘 다 현행 화면에 없다.
       · 2.24% 는 옛 원장(PSA 1,250,800,000 · ④ 3.55%) 시절의 ⑤ 다. D-31 로 산식 앵커가
         순지급액으로 통일되면서 원장이 재생성됐고 ⑤ 는 기본 기간 10.72% 가 됐다.
       · 0.110000 은 일별 표에 할인율을 소수 6자리로 적던 시절 표기다. 화면·엑셀 모두 0.11% 로 그린다.
     검사를 없애지 않고 기대값만 현행으로 바꾼다. 리터럴로 박지 않는다 — ledger_facts.json 을 읽어 대조한다.
     대상 화면은 옛 검사가 훑던 다섯(ia · pf · pfm · xd · xs)을 그대로 덮고 xls-profit-status 를 더한다. */
  R.numbers = await evalJS(`
    var F = ${JSON.stringify({
      ty: FACTS.ty, w: FACTS.w, tyByDate: FACTS.tyByDate,
      weekTy: FACTS.weekTy, weekTyAsset: FACTS.weekTyAsset, weekW: FACTS.weekW,
      psa: Number(FACTS.weekExec).toLocaleString('en-US'), psc: Number(FACTS.weekPsc).toLocaleString('en-US'),
      fullTy: FACTS.fullTy, fullTyAsset: FACTS.fullTyAsset, fullW: FACTS.fullW, monthTy: FACTS.monthTy
    })};
    var out = [];
    function add(name, want, got){ out.push({name:name, want:want, got:got, pass: want === got}); }
    function cells(tr){ return Array.prototype.map.call(tr.cells, function(td){ return td.textContent.trim(); }); }
    function SECQ(scr, sel){ return document.querySelector('section.screen[data-screen="'+scr+'"]').querySelectorAll(sel); }

    /* (1) 투자 자산 — 카드 Ty · 자산표 투자실행액 행 */
    go('invest-assets','default');
    var iaCards = SECQ('invest-assets','.summary-value');
    add('투자자산 카드 Ty', F.ty + '%', iaCards[3] ? iaCards[3].textContent.trim() : '없음');
    var iaRow = cells(SECQ('invest-assets','.tbl tbody tr')[0]);
    add('자산표 투자실행액 W', F.w + '일', iaRow[2]);
    add('자산표 투자실행액 Ty', F.ty + '%', iaRow[4]);

    /* (2) 투자 수익 기본(일주일·일별) — 카드 ④·⑤ · PSA·PSC · 합계 행 · 행별 W↔Ty */
    go('invest-profit','default');
    var tv = SECQ('invest-profit','.ty-split .summary-value');
    add('기본 기간 ④ 투자실행금액 대비', F.weekTy + '%',      tv[0] ? tv[0].textContent.trim() : '없음');
    add('기본 기간 ⑤ 투자자산 대비',   F.weekTyAsset + '%', tv[1] ? tv[1].textContent.trim() : '없음');
    var tip = Array.prototype.map.call(SECQ('invest-profit','.ty-split .tip-row'), function(e){ return e.textContent.trim(); });
    add('기본 기간 PSA', 'PSA' + F.psa + '원', tip.filter(function(x){ return x.indexOf('PSA')===0; })[0] || '없음');
    add('기본 기간 PSC', 'PSC' + F.psc + '원', tip.filter(function(x){ return x.indexOf('PSC')===0; })[0] || '없음');
    var ft = Array.prototype.map.call(SECQ('invest-profit','.tbl tfoot td'), function(td){ return td.textContent.replace('가중평균','').trim(); });
    add('일별 표 합계 W',  F.weekW,          ft[4] || '없음');
    add('일별 표 합계 Ty', F.weekTy + '%',   ft[5] || '없음');
    /* [기준 교체 2026-08-30] 예전엔 W 하나에 Ty 하나(tyByW)로 접어 대조했다.
       대표 정의서 [2번 이미지] MD-1i 의 부족액 차감이 들어가면서 Ty 가 W 만의 함수가 아니게 됐다.
       날짜로 잡은 원장 사실값(tyByDate = 날짜 → [W, Ty])과 행 단위로 맞춘다 — 더 좁은 검사다. */
    function pairCheck(label, rows){
      var bad = [];
      rows.forEach(function(c){
        var want = F.tyByDate[c.d];
        if(!want) bad.push(c.d + ' 원장에 없는 날짜');
        else if(want[0] !== c.w || want[1] + '%' !== c.ty)
          bad.push(c.d + ' W' + c.w + '/' + c.ty + ' (원장 W' + want[0] + '/' + want[1] + '%)');
      });
      out.push({name:label + ' 날짜↔W↔Ty ' + rows.length + '행', want:'전건 원장 일치',
                got: bad.length ? bad.join(' / ') : '어긋남 0',
                pass: rows.length > 0 && bad.length === 0});
    }
    var pfRows = Array.prototype.map.call(SECQ('invest-profit','.tbl tbody tr'), function(tr){
      var c = cells(tr); return {d:c[0], w:c[4], ty:c[5]};
    });
    pairCheck('일별 표', pfRows);

    /* (3) 투자 수익 월별(6개월 = 원장 전구간) — 달 행은 달 안에서 다시 가중평균한 W 라
       일별 행과 짝이 안 맞는다. month_rollup 값(monthTy)과 대조한다. */
    go('invest-profit','monthly');
    var mv = SECQ('invest-profit','.ty-split .summary-value');
    add('월별 ④ 투자실행금액 대비', F.fullTy + '%',      mv[0] ? mv[0].textContent.trim() : '없음');
    add('월별 ⑤ 투자자산 대비',   F.fullTyAsset + '%', mv[1] ? mv[1].textContent.trim() : '없음');
    var mft = Array.prototype.map.call(SECQ('invest-profit','.tbl tfoot td'), function(td){ return td.textContent.replace('가중평균','').trim(); });
    add('월별 표 합계 W',  F.fullW,        mft[4] || '없음');
    add('월별 표 합계 Ty', F.fullTy + '%', mft[5] || '없음');
    var mrows = Array.prototype.map.call(SECQ('invest-profit','.tbl tbody tr'), function(tr){
      var c = cells(tr); return c[0] + '|' + c[4] + '|' + c[5];
    });
    add('월별 표 ' + F.monthTy.length + '행 W·Ty',
        F.monthTy.map(function(m){ return m[0] + '|' + m[1] + '|' + m[2] + '%'; }).join(' , '), mrows.join(' , '));

    /* (4) 엑셀 서식 미리보기 — 기간은 수익 화면 상태를 따른다. 기본(일주일)로 되돌리고 본다. */
    go('invest-profit','default');
    go('xls-profit-daily','default');
    var xdRows = Array.prototype.map.call(SECQ('xls-profit-daily','table tr'), cells)
      .filter(function(c){ return /^\\d{4}-\\d{2}-\\d{2}$/.test(c[1] || ''); })
      .map(function(c){ return {d:c[1], w:c[5], ty:c[6]}; });
    pairCheck('엑셀 일별투자수익', xdRows);

    go('xls-profit-status','default');
    var xps = {};
    Array.prototype.map.call(SECQ('xls-profit-status','table tr'), cells).forEach(function(c){ if(c[1]) xps[c[1]] = c[2]; });
    add('엑셀 투자수익현황 ④', F.weekTy + '%',      xps['Ty수익율 (투자실행금액 대비)'] || '없음');
    add('엑셀 투자수익현황 ⑤', F.weekTyAsset + '%', xps['Ty수익율 (투자자산 대비)'] || '없음');

    go('xls-assets-status','default');
    var xasExec = Array.prototype.map.call(SECQ('xls-assets-status','table tr'), cells)
      .filter(function(c){ return c[1] === '투자실행액'; })[0] || [];
    add('엑셀 투자자산현황 W',  F.w,        xasExec[3] || '없음');
    add('엑셀 투자자산현황 Ty', F.ty + '%', xasExec[5] || '없음');

    /* (5) 비중 합 — 예전에도 값만 찍고 판정은 안 했다. 같이 판정에 올린다. */
    var sumRatio = window.__selfcheck().ratioSum;
    out.push({name:'가맹점별 비중 합', want:'100', got:String(sumRatio), pass: sumRatio === 100});

    go('invest-assets','default');
    return {items: out, ratioSum: sumRatio, fail: out.filter(function(o){ return !o.pass; }).length};
  `);

  /* ── 10) 문서 실물 수신 (D-39 로 계약기록 내려받기 잠금) ── */
  {
    /* D-39 「계약서 다운로드 차단 — 전자서명 형식이 정해질 때까지 비활성」으로
       전자서명 결과 텍스트가 사라졌다. 남는 실물 내려받기는 증명서 PDF 한 건이다.
       계약기록 쪽은 아래 잠금 검사에서 "버튼이 꺼져 있고 아무 파일도 나가지 않는가"로 본다. */
    const DOCS = [
      ['증명서 PDF', '투자자산증명서_20260827.pdf', 'go("certificate","default"); document.querySelector(\'[data-act="cert-pdf"]\').click(); return 1;']
    ];
    R.docs = [];
    for(const [label, name, script] of DOCS){
      fs.readdirSync(DL).forEach(f => { try{ fs.unlinkSync(path.join(DL, f)); }catch(e){} });
      /* 한 번 띄운 탭에서 자동 다운로드를 여러 번 하면 Chrome 이 두 번째부터 막는다.
         앞선 검사에서 이미 여러 건을 받았으므로 문서 1건마다 페이지를 새로 연다. */
      await send('Page.navigate', {url: TARGET});
      await sleep(1500);
      await send('Browser.setDownloadBehavior', {behavior:'allow', downloadPath: DL});
      await evalJS(script);
      /* macOS 파일명 정규화(NFC/NFD) 차이를 피해 디렉터리를 훑어 맞춘다 */
      const norm = x => x.normalize('NFC');
      let got = null;
      for(let i = 0; i < 30 && !got; i++){
        await sleep(200);
        /* 앞선 죽은-컨트롤 스캔이 같은 파일을 이미 한 번 받아서 Chrome 이 " (1)" 을 붙일 수 있다 */
        const base = norm(name).replace(/\.[^.]+$/, ''), ext = path.extname(name);
        const hit = fs.readdirSync(DL).find(f => !f.endsWith('.crdownload') &&
          path.extname(f) === ext && norm(f).replace(/ \(\d+\)$/, '').replace(/\.[^.]+$/, '') === base);
        if(hit && fs.statSync(path.join(DL, hit)).size > 0) got = path.join(DL, hit);
      }
      const src = path.join(REPO, 'assets/docs', name);
      const srcBytes = fs.existsSync(src) ? fs.statSync(src).size : -1;
      R.docs.push({label, name, saved: got ? path.basename(got) : null, bytes: got ? fs.statSync(got).size : 0, srcBytes,
                   pass: !!got && fs.statSync(got).size === srcBytes});
      await evalJS('go("invest-assets","default"); return 1;');
    }
  }

  /* ── 11) 모달 닫힘 경로 — 닫기 버튼·X 로만 닫힌다 (D-40) ──
     근거 = request_register.md D-40. 5-9) 는 `배경으로는 안 닫힌다`만 보므로, 닫는 경로가 죽어
     모달이 영영 안 닫혀도 통과한다. 여기서 X·푸터 버튼이 실제로 닫는지를 실측해 그 구멍을 막는다.
     판정 로직은 verify_app.js §7 과 같은 것을 쓴다 — 원본과 시연본을 같은 잣대로 본다.
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
  fs.writeFileSync(path.join(OUTDIR, 'verify_proto_result.json'), JSON.stringify(R, null, 1));

  const line = (t, ok) => (ok ? 'PASS ' : 'FAIL ') + t;
  console.log('== 메뉴 ' + R.menus.length + ' ==');   R.menus.forEach(m => console.log(' ', line(m.label + ' → ' + m.screen + ' (' + m.bg + ')', m.pass)));
  console.log('== 상태 ' + R.states.length + ' =='); R.states.forEach(s => console.log(' ', line(s.screen + '/' + s.want + (s.err ? '  ' + s.err : '  got=' + s.state), s.pass)));
  console.log('== 다운로드 ' + R.downloads.length + ' =='); R.downloads.forEach(d => console.log(' ', line(d.key + ' → ' + d.file + ' ' + d.bytes + 'B', d.pass)));
  console.log('== 값 변화 =='); R.data.forEach(d => console.log(' ', d.pass===null ? 'SKIP ' + d.case + ' ' + (d.err||'') : line(d.case + ' ' + JSON.stringify(d), d.pass)));
  console.log('== 레이아웃 ' + (R.layout ? R.layout.length : 0) + '조합 ==');
  R.layout.forEach(l => console.log(' ', l.pass===null ? 'SKIP ' + l.at + ' ' + (l.err||'') : line(l.at + ' h=' + l.h + (l.empties.length ? ' 빈마운트=' + l.empties.join(',') : '') + (l.modals.length ? ' 모달=' + l.modals.join(',') : ''), l.pass)));
  console.log('== 죽은 컨트롤 ==', R.dead.length, '/ 검사', R.scanned, '건');
  R.dead.slice(0, 40).forEach(d => console.log('  -', JSON.stringify(d)));
  console.log('== 새 창 링크(실물은 verify_links.py) ==', R.newtab.length);
  console.log('== 키보드·보조기술 미도달 컨트롤 ==', R.a11y.length);
  R.a11y.slice(0, 20).forEach(d => console.log('  -', JSON.stringify(d)));
  console.log('== 콘솔 에러 ==', R.console.length);
  R.console.slice(0, 20).forEach(c => console.log('  -', c));
  /* ── 바깥 통로 판정 ──
     2026-08-30 이전까지 이 블록은 위 7) 에서 전 화면·상태를 훑어 값을 만들고 찍기만 했다.
     `pass` 를 붙이지 않아 종료코드 walker 에 안 잡혔고, 시연본에서 형제 문서 링크가 되살아나도
     verify_proto.js 는 곳수만 찍고 통과했다.
     기준은 새로 정하지 않는다 — 같은 값을 이미 판정하는 형제 게이트
     `gate_prototype.js:206-209`(형제 문서 0 · 금칙 문자열 0 · 허용 밖 외부 호스트 0)를 그대로 쓴다.
     ALLOWED_HOSTS 도 gate_prototype.js:23 과 같은 목록이다. */
  {
    const ALLOWED_HOSTS = ['www.we-bank.co.kr', 'fonts.googleapis.com', 'fonts.gstatic.com'];
    const hostOf = h => { try { return new URL(h.href, 'https://x/').host; } catch(e){ return h.href; } };
    const badHosts = R.escape.offsite.map(hostOf).filter(h => ALLOWED_HOSTS.indexOf(h) < 0);
    R.escapeGuard = [
      {at:'형제 문서 링크 0', pass: R.escape.sibling.length === 0, 곳: R.escape.sibling.slice(0, 4)},
      {at:'금칙 문자열 링크 0', pass: R.escape.banned.length === 0, 곳: R.escape.banned.slice(0, 4)},
      {at:'허용 밖 외부 호스트 0 (허용 ' + ALLOWED_HOSTS.join(',') + ')',
       pass: badHosts.length === 0, 곳: Array.from(new Set(badHosts))},
      /* 위 7) 의 주석이 근거 — 「화면에 적힌 문구 자체에 바깥 문서 이름이 남아 있는지」.
         링크를 떼도 문구가 남으면 시연본이 없는 문서를 가리키게 된다. banned(주소)의 문구 짝이다. */
      {at:'화면 문구에 바깥 문서 이름 0', pass: R.escape.docText.length === 0, 곳: R.escape.docText.slice(0, 6)},
      /* 스캔이 아무것도 못 잡으면(셀렉터 노후·go() 실패) 위 넷이 전부 0 이 되어 저절로 통과한다.
         그 구멍만 막는다 — 곳수는 판정하지 않고 0 인지만 본다. */
      {at:'링크 스캔 대상 0건 아님', pass: R.escape.total > 0, 곳: R.escape.total}
    ];
  }

  console.log('== 바깥으로 나가는 통로 ==');
  console.log('  타 오리진', R.escape.offsite.length, JSON.stringify(R.escape.offsite));
  console.log('  형제 문서', R.escape.sibling.length, JSON.stringify(R.escape.sibling));
  console.log('  금칙 문자열 링크', R.escape.banned.length, JSON.stringify(R.escape.banned));
  console.log('  자산 링크', R.escape.asset.length, '해시 링크', R.escape.hash, '전체', R.escape.total);
  console.log('  화면 문구 잔존', R.escape.docText.length, JSON.stringify(R.escape.docText));
  R.escapeGuard.forEach(g => console.log(' ', line(g.at + '  ' + JSON.stringify(g.곳), g.pass)));
  /* 판정하지 않고 보고만 — 도크가 지금 없다(「도크 없음」). 몇 개여야 하는지 근거를 댈 수 없다. */
  console.log('  도크 화면 목록(보고만)', JSON.stringify(R.escape.dockOptions));
  console.log('== 가로 오버플로 ==', R.overflow.filter(o => !o.pass).length, JSON.stringify(R.overflow.filter(o => !o.pass)));
  console.log('== 숫자 불변 (기대값 출처 ledger_facts.json) ' + R.numbers.items.length + '건 · FAIL ' + R.numbers.fail + ' ==');
  R.numbers.items.forEach(n => console.log(' ', line(n.name + '  want=' + n.want + '  got=' + n.got, n.pass)));
  console.log('== PDF·전자서명 텍스트 실물 ==');
  R.docs.forEach(d => console.log('  ', (d.pass?'PASS ':'FAIL ') + d.label + ' ' + (d.saved||d.name) + ' ' + d.bytes + 'B / src ' + d.srcBytes + 'B'));
  /* 닫는 컨트롤이 0인 모달은 진행 오버레이 하나뿐이다.
     근거 = request_register.md D-40 「대상 모달 5종 — 증명서 발급 확인 · 서명 확인 · 계약서보기 ·
     서명 진행 · 서명 완료. `서명 진행`은 원래도 닫기 컨트롤이 없는 진행 오버레이다」.
     위 11) 의 reachable 은 `살아 있는 컨트롤이 없으면 진행 오버레이` 로 봐주므로, 어느 모달의 버튼이
     전부 꺼지면 영영 안 닫히는데도 그 예외에 걸려 통과한다. 그 구멍을 곳수로 막는다.
     모달 이름은 적지 않고 닫는 컨트롤 0건인 모달의 곳수만 센다 — 새 모달이 생겨도 판정에 들어온다. */
  {
    const noCloser = R.modals.filter(m => (m.closers || []).length === 0);
    R.modalGuard = {name: '닫는 컨트롤 없는 모달 = 진행 오버레이 1건',
      곳: noCloser.map(m => m.modal + '(controls=' + m.controls + ' live=' + m.live + ')'),
      pass: noCloser.length === 1 && noCloser[0].live === 0 && noCloser[0].controls > 0};
  }

  console.log('== 모달 닫힘 경로 ' + R.modals.length + ' ==');
  R.modals.forEach(m => console.log(' ', line(m.modal + '  오버레이=' + m.afterOverlayClick + ' 본문=' + m.afterBodyClick +
    ' 내부=' + m.afterInnerClick + ' ESC=' + m.afterEsc +
    ' 닫는것=[' + (m.closers||[]).map(c => c.label + (c.x ? '(X)' : '')).join(', ') + ']' +
    (m.scroll ? ' 스크롤=' + JSON.stringify(m.scroll) : '') + (m.err ? ' ' + m.err : ''), m.pass)));
  console.log(' ', line(R.modalGuard.name + '  ' + JSON.stringify(R.modalGuard.곳), R.modalGuard.pass));
  console.log('== selfcheck ==', JSON.stringify(R.selfcheck));

  /* ── 종료코드 ── FAIL 이 하나라도 있으면 1 로 끝난다.
     형제 검증기(verify_rows.js:213 · verify_toast.js:229 · verify_period.js:405)와 같은 방식이다.
     화면에 FAIL 을 찍고도 exit=0 으로 끝나, 종료코드로 판정하는 실행기·CI 가 실패를 못 보던 것을 막는다.
     섹션 이름을 손으로 적지 않고 R 안에서 `pass` 를 가진 항목을 전수로 훑는다 —
     검사를 새로 넣어도 저절로 종료코드에 들어온다. 판정 누락이 생길 자리가 없다.
     pass!==true 는 전부 실패로 센다 — try/catch 가 낸 pass:null(SKIP)도 실패다.
     콘솔 에러·죽은 컨트롤은 pass 필드가 없어 따로 더한다. */
  const graded = [];
  (function walk(node, at){
    if(Array.isArray(node)){ node.forEach((v, i) => walk(v, at + '[' + i + ']')); return; }
    if(node && typeof node === 'object'){
      if(Object.prototype.hasOwnProperty.call(node, 'pass')) graded.push({at: at, pass: node.pass, item: node});
      Object.keys(node).forEach(k => { if(k !== 'pass') walk(node[k], at + '.' + k); });
    }
  })(R, 'R');
  const failed = graded.filter(g => g.pass !== true);
  console.log('== 합계 == 판정 ' + graded.length + '건 · PASS ' + (graded.length - failed.length) +
    ' · FAIL ' + failed.length + ' · 콘솔 에러 ' + R.console.length + ' · 죽은 컨트롤 ' + R.dead.length);
  failed.forEach(g => console.log('  FAIL ' + g.at + '  ' + JSON.stringify(g.item).slice(0, 300)));

  ws.close(); chrome.kill(); server.close();
  process.exit(failed.length || R.console.length || R.dead.length ? 1 : 0);
}
main().catch(e => { console.error('VERIFY ERROR', e); process.exit(1); });
