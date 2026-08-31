/* 투자 시뮬레이션 헤드리스 검증 — 창을 띄우지 않는다(--headless=new).
   실제 입력·클릭으로 몬다. 값을 코드에서 읽어 오는 것이 아니라 화면에 찍힌 글자를 읽는다.

     1) 기본값 실행 — W · Ty · 비중 합 100.0% · 상환액 = PSA + PSM
     2) 입력을 바꾸면 결과가 따라 바뀐다 — 할인율 · 순현금 · 미지급률 · 기간 · 플랫폼
     3) S입금부족율 > 할인율 → 투자수익 음수를 그대로 보인다 (설계 L-3)
     4) 기간 밖 행은 회색 이탤릭 · 집계 제외
     5) 채권 행 추가 · 삭제
     6) 필수 미충족이면 실행 버튼 비활성 · 실행 전에는 결과가 없다
     7) 정적 낱장 2종이 통합본과 같은 값을 싣는다
     8) 콘솔 에러 0

   macOS 함정 — --window-size=1440,H 는 실제 뷰포트 1440x(H-87). 1287 로 줘야 1200 이 잡힌다. */
const http = require('http');
const CHROME_DL = require('./chrome_dl');
const PH_DL = CHROME_DL.dir();
const fs   = require('fs');
const path = require('path');
const os   = require('os');
const { spawn } = require('child_process');

const REPO   = '/Users/semi/cursor/payhug-investor-admin';
const OUTDIR = '/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin';
/* 기대값을 검증기에 손으로 적지 않는다.
   시뮬레이션 쪽 — sim_facts.py 가 build_app.py 의 씨앗 8행(simSeedRows)·기본 변수(SIM_DEFAULT)·
   플랫폼 금융일수(SIM_DUR)를 읽어 산출한 것. 씨앗 한 곳만 고치면 기대값이 따라온다.
   원장 불변식 쪽 — daily_ledger.py 가 내는 ledger_facts.json (verify_identity.js:13 과 같은 원천). */
/* 파일을 읽지 않고 산출기를 그 자리에서 돌려 받는다 — sim_facts.json 이 낡아 있어도
   검증기가 옛 기대값을 지키는 일이 없다. 산출기가 죽으면 검증기도 그대로 죽는다(FAIL). */
const SF    = JSON.parse(require('child_process')
  .execFileSync('python3', [path.join(OUTDIR, 'sim_facts.py'), '--json'],
                {maxBuffer: 1 << 24}).toString('utf8'));
const FACTS = JSON.parse(fs.readFileSync(path.join(OUTDIR, 'ledger_facts.json'), 'utf8'));
const B = SF.base;                       /* 기본값 실행 결과 */
const ROSTER = FACTS.merchants.length;   /* 가맹점 로스터 곳수 = 계약기록 건수 */
const PORT = 8830 + (process.pid % 60), DPORT = 9530 + (process.pid % 60);
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
  return new Promise(res => pending.set(id, {res}));
}
async function evalJS(expr){
  const r = await send('Runtime.evaluate', {expression:'(function(){' + expr + '})()', returnByValue:true});
  if(r.exceptionDetails) throw new Error('page eval: ' + JSON.stringify(
    r.exceptionDetails.exception && r.exceptionDetails.exception.description || r.exceptionDetails.text));
  return r.result.value;
}
const sleep = ms => new Promise(r => setTimeout(r, ms));

const R = {cases: [], console: [], viewport: null};
let failed = 0;
function P(name, pass, detail){
  R.cases.push({name, pass, detail});
  if(!pass) failed++;
  console.log((pass ? '  PASS ' : '  FAIL ') + name + (detail === undefined ? '' : '  ' + JSON.stringify(detail)));
}

/* 화면에 찍힌 글자를 읽어 오는 페이지 쪽 도구 — 검증기는 SIM 객체를 직접 보지 않는다 */
const HELPERS = `
  window.__S = {
    sec: function(){ return document.querySelector('section.screen[data-screen="invest-sim"]'); },
    out: function(){ return document.querySelector('[data-mount="sim-out"]'); },
    tables: function(){ return Array.prototype.slice.call(window.__S.out().querySelectorAll('table')); },
    num: function(t){ var v = String(t).replace(/[^0-9.-]/g, ''); return v === '' ? null : Number(v); },
    cells: function(tr){ return Array.prototype.map.call(tr.children, function(td){ return td.textContent.trim(); }); },
    bondRows: function(){
      var t = window.__S.tables()[0];
      return Array.prototype.map.call(t.querySelectorAll('tbody tr'), function(tr){
        return {cells: window.__S.cells(tr), skip: tr.className.indexOf('sim-skip') >= 0,
                style: getComputedStyle(tr.children[1]).fontStyle}; });
    },
    statusRows: function(){
      var t = window.__S.tables()[1];
      return Array.prototype.map.call(t.querySelectorAll('tbody tr'), function(tr){ return window.__S.cells(tr); });
    },
    dailyRows: function(){
      var t = window.__S.tables()[2];
      return Array.prototype.map.call(t.querySelectorAll('tbody tr'), function(tr){ return window.__S.cells(tr); });
    },
    dailyFoot: function(){
      var t = window.__S.tables()[2], f = t.querySelector('tfoot tr');
      return f ? window.__S.cells(f) : null;
    },
    stat: function(label){
      var g = window.__S.out().querySelectorAll('.stat'), i;
      for(i = 0; i < g.length; i++){
        var l = g[i].querySelector('.summary-label');
        if(l && l.textContent.trim() === label) return g[i].textContent.trim();
      }
      return null;
    },
    card: function(label){
      var g = window.__S.out().querySelectorAll('.summary-card'), i;
      for(i = 0; i < g.length; i++){
        var l = g[i].querySelector('.summary-label');
        if(l && l.textContent.trim() === label)
          return {value: g[i].querySelector('.summary-value').textContent.trim(),
                  sub: (g[i].querySelector('.summary-sub') || {textContent:''}).textContent.trim()};
      }
      return null;
    },
    setVar: function(k, v){
      var el = document.querySelector('[data-act="sim-var"][data-k="' + k + '"]');
      el.focus(); el.value = v;
      el.dispatchEvent(new Event('input', {bubbles:true}));
      el.dispatchEvent(new Event('change', {bubbles:true}));
      el.blur();
      return el.value;
    },
    setRow: function(i, f, v){
      var el = document.querySelector('[data-act="sim-row"][data-i="' + i + '"][data-f="' + f + '"]');
      el.focus(); el.value = v;
      el.dispatchEvent(new Event('input', {bubbles:true}));
      el.dispatchEvent(new Event('change', {bubbles:true}));
      el.blur();
      return el.value;
    },
    rowVal: function(i, f){
      var el = document.querySelector('[data-act="sim-row"][data-i="' + i + '"][data-f="' + f + '"]');
      return el ? el.value : null;
    },
    rowDays: function(i){
      var r = window.__S.sec().querySelectorAll('[data-mount="sim-rows"] .sim-row')[i];
      return r ? r.querySelector('.sim-days').textContent.trim() : null;
    },
    btn: function(){ return document.querySelector('[data-mount="sim-go"]'); },
    varVal: function(k){
      var el = document.querySelector('[data-act="sim-var"][data-k="' + k + '"]')
            || document.querySelector('[data-act="sim-scale"][data-k="' + k + '"]');
      return el ? el.value : null;
    },
    setScale: function(k, v){
      var el = document.querySelector('[data-act="sim-scale"][data-k="' + k + '"]');
      el.focus(); el.value = v;
      el.dispatchEvent(new Event('input', {bubbles:true}));
      el.dispatchEvent(new Event('change', {bubbles:true}));
      el.blur();
      return el.value;
    },
    amts: function(){
      return Array.prototype.map.call(
        document.querySelectorAll('[data-act="sim-row"][data-f="amt"]'), function(e){ return e.value; });
    },
    /* ⑤ Ty 2분할 오른쪽 · ⑥ 일별 표 마지막 열머리 — 표기만 읽는다 */
    ty5Label: function(){
      var g = window.__S.out().querySelectorAll('.ty-split > div');
      return g.length > 1 ? g[1].querySelector('.ty-label').textContent.trim() : null;
    },
    ty5Badge: function(){
      var g = window.__S.out().querySelectorAll('.ty-split > div');
      var b = g.length > 1 ? g[1].querySelector('.ty-label .badge') : null;
      return b ? b.textContent.trim() : null;
    },
    dailyTh: function(){
      var t = window.__S.tables()[2], th = t.querySelectorAll('thead th');
      return th[th.length - 1].textContent.trim();
    },
    dailyThBadge: function(){
      var t = window.__S.tables()[2], th = t.querySelectorAll('thead th'), b = th[th.length - 1].querySelector('.badge');
      return b ? b.textContent.trim() : null;
    },
    snap: function(){
      return {rows: window.__S.sec().querySelectorAll('[data-mount="sim-rows"] .sim-row').length,
              total: document.querySelector('[data-mount="sim-total"]').textContent.trim(),
              btnLabel: window.__S.btn().textContent.trim(),
              btnDisabled: window.__S.btn().disabled,
              warn: !document.querySelector('[data-mount="sim-warn"]').hidden,
              warnText: document.querySelector('[data-mount="sim-warn"]').textContent.trim(),
              state: window.__S.sec().dataset.state,
              badge: (window.__S.sec().querySelector('[data-state-mark]') || {textContent:''}).textContent.trim(),
              outLen: window.__S.out().innerHTML.length};
    }
  };
  return 1;`;

async function run(){ await evalJS('window.__S.btn().click(); return 1;'); await sleep(420); }
async function snap(){ return evalJS('return window.__S.snap();'); }

async function main(){
  await new Promise(r => server.listen(PORT, r));
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'vsim-'));
  const chrome = spawn(CHROME, ['--headless=new', '--remote-debugging-port=' + DPORT,
    CHROME_DL.args(PH_DL, profile)[0] /* '--user-data-dir=' + profile */, '--no-first-run', '--no-default-browser-check',
    '--disable-gpu', '--window-size=1440,1287', 'about:blank'], {stdio:'ignore'});

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
      consoleErrors.push('exception: ' + (m.params.exceptionDetails.exception &&
        m.params.exceptionDetails.exception.description || m.params.exceptionDetails.text));
    if(m.method === 'Log.entryAdded' && m.params.entry.level === 'error')
      consoleErrors.push('log: ' + m.params.entry.text + ' ' + (m.params.entry.url || ''));
  });
  await send('Runtime.enable'); await send('Log.enable'); await send('Page.enable');
  await send('Page.navigate', {url:'http://127.0.0.1:' + PORT + '/app.html'});
  await sleep(1800);
  R.viewport = await evalJS('return {w:innerWidth, h:innerHeight};');
  /* 재 놓고 판정에 안 넣던 자리(2026-08-30 이전). 기준은 이 파일 13행이 스스로 적어 둔 것이다 —
     「--window-size=1440,H 는 실제 뷰포트 1440x(H-87). 1287 로 줘야 1200 이 잡힌다」.
     보정이 풀리면 실제 폭·높이가 달라져 아래 레이아웃·표 판정이 조용히 다른 조건에서 돈다. */
  P('뷰포트 1440x1200 (창 1440x1287 · macOS 87px 보정)',
    R.viewport.w === 1440 && R.viewport.h === 1200, R.viewport);
  await evalJS(HELPERS);

  /* ── 0) 메뉴 ── */
  console.log('\n[0] 사이드바');
  const nav = await evalJS(`
    var a = Array.prototype.map.call(document.querySelectorAll('.sidebar .nav-item[data-menu]'), function(n){
      return {menu:n.dataset.menu, label:n.querySelector('span').textContent.trim(), href:n.getAttribute('href')};
    });
    var g = document.querySelectorAll('.sidebar .nav-group').length;
    return {list:a, groups:g};`);
  const labels = nav.list.map(x => x.label);
  P('메뉴 8건 · 그룹 3', nav.list.length === 8 && nav.groups === 3, {n:nav.list.length, groups:nav.groups});
  P('투자 시뮬레이션이 투자 수익 바로 아래',
    labels[1] === '투자 수익' && labels[2] === '투자 시뮬레이션' && nav.list[2].menu === 'invest-sim', labels);
  P('기존 7개 라벨 불변',
    JSON.stringify(labels.filter((_, i) => i !== 2)) ===
    JSON.stringify(['투자 자산','투자 수익','가맹점','정산채권 양수','계약기록','쿠콘 관리 현금','비밀번호 변경']),
    labels);

  await evalJS(`document.querySelector('.nav-item[data-menu="invest-sim"]').click(); return 1;`);
  await sleep(250);   /* .nav-item 에 background-color transition 이 걸려 있어 바로 읽으면 중간값이 잡힌다 */
  const menuGo = await evalJS(`
    var s = window.__S.sec();
    return {active:document.body.dataset.active, visible:!s.hidden, hash:location.hash,
            bg:getComputedStyle(document.querySelector('.nav-item[data-menu="invest-sim"]')).backgroundColor,
            groupLabel:getComputedStyle(document.querySelector('.nav-item[data-menu="invest-sim"]')
                        .closest('.nav-group').querySelector('.nav-group-label')).color};`);
  const ch = (menuGo.bg.match(/[\d.]+/g) || []).map(Number);
  const gl = (menuGo.groupLabel.match(/[\d.]+/g) || []).map(Number);
  P('메뉴 클릭 → 화면 전환 · 활성 표시 (메뉴 초록 · 그룹 라벨 초록)',
    menuGo.active === 'invest-sim' && menuGo.visible && menuGo.hash === '#invest-sim'
    && ch[0] === 127 && ch[1] === 225 && ch[2] === 65
    && gl[0] === 127 && gl[1] === 225 && gl[2] === 65, menuGo);

  /* ── 1) 실행 전 ── */
  console.log('\n[1] 실행 전');
  await evalJS("go('invest-sim','default'); return 1;");
  const s0 = await snap();
  P('결과 게이트 — 실행 전에는 결과가 없다', s0.outLen === 0 && s0.state === 'default' && s0.badge === '', s0);
  P('기본 입력 ' + SF.seedRows + '행 · 합계 한 줄',
    s0.rows === SF.seedRows && s0.total === SF.seedTotalText, s0);
  P('실행 버튼 라벨 · 활성', s0.btnLabel === '시뮬레이션 실행' && s0.btnDisabled === false, s0);
  const days0 = await evalJS('var o=[],i; for(i=0;i<' + SF.seedRows + ';i++) o.push(window.__S.rowDays(i)); return o;');
  P('금융일수 파생 표시', JSON.stringify(days0) === JSON.stringify(SF.seedDays), days0);

  /* ── 2) 기본값 실행 ── */
  console.log('\n[2] 기본값 실행');
  const mid = await evalJS('window.__S.btn().click(); return window.__S.snap();');
  P('실행 중 라벨 · 비활성', mid.btnLabel === '계산 중...' && mid.btnDisabled === true, mid);
  await sleep(500);
  const s1 = await snap();
  P('실행 후 상태 배지', s1.state === 'result' && s1.badge === '실행 결과' && s1.outLen > 2000, s1);

  const base = await evalJS(`
    var st = window.__S.statusRows(), ft = window.__S.dailyFoot();
    return {status:st, foot:ft,
      summary:{자산:window.__S.card('투자자산'), 실행:window.__S.card('투자실행액'),
               현금:window.__S.card('순현금'), ty:window.__S.card('Ty수익율')},
      bonds:window.__S.bondRows().map(function(b){ return b.cells; }),
      daily:window.__S.dailyRows(),
      실행금:window.__S.stat('투자실행금'), 수익:window.__S.stat('투자수익'),
      기간:window.__S.stat('검색대상기간'),
      tyStat:window.__S.stat('Ty수익율')};`);
  R.baseline = base;
  const st = base.status;
  P('현황 · 투자실행액 행', st[0][0] === '투자실행액' && st[0][1] === B.exec
    && st[0][2] === B.w && st[0][3] === B.s && st[0][4] === B.ty
    && st[0][5] === B.share0 && st[0][6] === '㈜페이허그', st[0]);
  P('현황 · 순현금 행', st[1][0] === '순현금' && st[1][1] === B.cash
    && st[1][5] === B.share1 && st[1][6] === '㈜쿠콘', st[1]);
  P('현황 · 합계 = 투자자산 · 비중 합 ' + B.shareSum,
    st[2][1] === B.total && st[2][5] === B.shareSum, st[2]);
  P('W ' + B.w + ' — 투자 자산 화면과 같은 자리', st[0][2] === B.w, st[0][2]);
  P('Ty ' + B.ty + ' — 투자 자산 화면과 같은 자리', st[0][4] === B.ty, st[0][4]);
  P('요약 카드 4장', base.summary.자산.value === B.cardTotal
    && base.summary.실행.value === B.cardExec && base.summary.현금.value === B.cardCash
    && base.summary.ty.value === B.cardTy && base.summary.ty.sub === B.cardTySub,
    Object.keys(base.summary).map(k => base.summary[k].value));

  const foot = base.foot;
  const n = t => Number(String(t).replace(/[^0-9.-]/g, ''));
  P('검산 상환액 = PSA + PSM (일별 합계행)',
    n(foot[1]) === n(foot[2]) + n(foot[3]) && n(foot[1]) === B.psb, foot);
  P('일별 합계 PSD ' + B.psd + ' · ④ ' + B.ty4pct,
    foot[4].indexOf(B.psd) === 0 && foot[5].indexOf(B.ty4pct) === 0, foot);
  P('일별 행 ' + B.dailyDates.length + '건 (기간 내 채권의 서로 다른 정산예정일)',
    JSON.stringify(base.daily.map(r => r[0])) === JSON.stringify(B.dailyDates),
    base.daily.map(r => r[0]));
  P('수익 현황 — 투자실행금 · 투자수익 · 기간',
    base.실행금.indexOf(B.psa) >= 0 && base.수익.indexOf(B.psm) >= 0
    && base.기간.indexOf(B.ecd) >= 0 && base.기간.indexOf(SF.period) >= 0,
    [base.실행금, base.수익, base.기간]);
  P('Ty 2분할 — ④ ' + B.ty4 + '% · ⑤ ' + B.ty5 + '%',
    base.tyStat.indexOf(B.ty4) >= 0 && base.tyStat.indexOf(B.ty5) >= 0, base.tyStat);
  P('채권별 산출 ' + B.bondKinds.length + '행 · 구분 '
    + B.bondKinds.filter(k => k === '미회수').length + ' 미회수 · '
    + B.bondKinds.filter(k => k === '기간 내').length + ' 기간 내',
    JSON.stringify(base.bonds.map(b => b[1])) === JSON.stringify(B.bondKinds), base.bonds.map(b => b[1]));
  P('채권 1행 = 설계 검산표',
    JSON.stringify(base.bonds[0]) === JSON.stringify(B.bond0), base.bonds[0]);

  /* ── 3) 입력을 바꾸면 결과가 바뀐다 ── */
  console.log('\n[3] 입력 변동');
  async function reset(){ await evalJS("go('invest-sim','default'); return 1;"); }
  /* 시나리오 입력도 산출기(sim_facts.py SCENARIOS)에서 받는다 — 검증기가 넣는 값과
     기대값이 갈릴 자리를 없앤다. 기준 변수 칸이면 setVar, 채권 행 칸이면 setRow 다. */
  async function apply(k){
    const sc = SF.scenarios[k];
    return sc.var !== undefined
      ? evalJS("window.__S.setVar('" + sc.var + "', '" + sc.value + "'); return 1;")
      : evalJS("window.__S.setRow(" + sc.row + ", '" + sc.field + "', '" + sc.value + "'); return 1;");
  }

  await reset();
  await apply('rate022'); await run();
  const r22 = await evalJS("var s=window.__S.statusRows(); return {ty:s[0][4], exec:s[0][1], S:s[0][3], fee:window.__S.bondRows()[0].cells[6]};");
  P('할인율 ' + SF.defaults.rate + ' → ' + SF.scenarios.rate022.value + ' : Ty · 투자실행액 · 수수료가 함께 움직인다',
    r22.ty !== B.ty && r22.exec !== B.exec
    && r22.ty === SF.rate022.ty && r22.exec === SF.rate022.exec
    && r22.fee === SF.rate022.bond0fee, r22);

  await reset();
  await apply('cash200m'); await run();
  const c2 = await evalJS("var s=window.__S.statusRows(); return {cash:s[1][1], tot:s[2][1], sh:[s[0][5],s[1][5],s[2][5]], ty5:window.__S.stat('Ty수익율')};");
  P('순현금 ' + B.cash + ' → ' + SF.cash200m.cash + ' : 순현금 · 투자자산 · 비중 · ⑤ 가 함께 움직인다',
    c2.cash === SF.cash200m.cash && c2.tot === SF.cash200m.total
    && c2.sh[2] === SF.cash200m.shareSum
    && c2.sh[0] === SF.cash200m.share0 && c2.sh[0] !== B.share0, c2);

  await reset();
  await apply('unpaid005'); await run();
  const u5 = await evalJS("var s=window.__S.statusRows(); return {S:s[0][3], ded:window.__S.bondRows()[0].cells[7], M:window.__S.bondRows()[0].cells[8], profit:window.__S.stat('투자수익')};");
  P('미지급률 ' + SF.defaults.unpaid + ' → ' + SF.scenarios.unpaid005.value + ' : S · 차감 · 투자수익이 함께 움직인다',
    u5.S === SF.unpaid005.s && u5.ded === SF.unpaid005.bond0ded && u5.M === SF.unpaid005.bond0M
    && u5.profit.indexOf(SF.unpaid005.psm) >= 0 && u5.S !== B.s, u5);

  await reset();
  await apply('to0831'); await run();
  const t31 = await evalJS(`
    var b = window.__S.bondRows();
    return {kinds:b.map(function(x){ return x.cells[1]; }), daily:window.__S.dailyRows().length,
            기간:window.__S.stat('검색대상기간'), exec:window.__S.statusRows()[0][1]};`);
  P('종료일 ' + SF.defaults.to + ' → ' + SF.scenarios.to0831.value + ' : 기간 내/미회수 경계가 옮겨간다',
    JSON.stringify(t31.kinds) === JSON.stringify(SF.to0831.bondKinds)
    && t31.daily === SF.to0831.dailyDates.length
    && t31.기간.indexOf(SF.to0831.ecd) >= 0 && t31.exec === SF.to0831.exec, t31);

  await reset();
  const plat = await evalJS(`
    var before = {due:window.__S.rowVal(0,'dd'), days:window.__S.rowDays(0)};
    window.__S.setRow(0, 'plat', 'yo');
    return {before:before, after:{due:window.__S.rowVal(0,'dd'), days:window.__S.rowDays(0)}};`);
  P('플랫폼 카드사 → 요기요 : 정산예정일이 선정산일 + ' + SF.platDur.yo + ' 으로 다시 채워진다',
    plat.before.due === SF.platDue.card && plat.before.days === SF.platDur.card + '일'
    && plat.after.due === SF.platDue.yo && plat.after.days === SF.platDur.yo + '일', plat);
  const platAll = await evalJS(`
    var out = [], m = ${JSON.stringify(SF.platDue)};
    ['card','bm','cpe','yo'].forEach(function(k){
      window.__S.setRow(0, 'plat', k);
      out.push({k:k, due:window.__S.rowVal(0,'dd'), days:window.__S.rowDays(0), want:m[k]});
    });
    return out;`);
  P('플랫폼 4종 금융일수 ' + SF.platDays.map(d => parseInt(d, 10)).join('·'),
    platAll.every(x => x.due === x.want) &&
    JSON.stringify(platAll.map(x => x.days)) === JSON.stringify(SF.platDays), platAll);

  await reset();
  await apply('amt800m'); await run();
  const amt = await evalJS("return {total:document.querySelector('[data-mount=\"sim-total\"]').textContent.trim(), exec:window.__S.statusRows()[0][1], A:window.__S.bondRows()[0].cells[5]};");
  P('순지급액 ' + B.bond0[3] + ' → ' + SF.amt800m.bond0[3] + ' : 합계 줄 · 투자실행액 · Ai 가 함께 움직인다',
    amt.total === SF.amt800m.rowsTotalText && amt.A === SF.amt800m.bond0A
    && amt.exec === SF.amt800m.exec, amt);

  /* ── 4) 음수 투자수익 (L-3) ── */
  console.log('\n[4] 음수 투자수익');
  await reset();
  await apply('unpaid020'); await run();
  const neg = await evalJS(`
    var b = window.__S.bondRows(), f = window.__S.dailyFoot();
    return {S:window.__S.statusRows()[0][3], M:b[0].cells[8], profit:window.__S.stat('투자수익'),
            foot:f, ty:window.__S.stat('Ty수익율'),
            negCls:!!window.__S.out().querySelector('.summary-value.neg')};`);
  P('S ' + SF.unpaid020.s + ' > 할인율 ' + SF.defaults.rate + '% → 채권 투자수익 음수',
    neg.S === SF.unpaid020.s && neg.M === SF.unpaid020.bond0M && n(neg.M) < 0, {S:neg.S, M:neg.M});
  P('수익 현황 투자수익 음수를 그대로 보인다',
    neg.profit.indexOf(SF.unpaid020.psm) >= 0
    && n(neg.profit.replace('투자수익','')) < 0 && neg.negCls === true, neg.profit);
  P('음수여도 상환액 = PSA + PSM 항등식 유지',
    n(neg.foot[1]) === n(neg.foot[2]) + n(neg.foot[3]), neg.foot);

  /* ── 5) 기간 밖 행 ── */
  console.log('\n[5] 기간 밖');
  await reset();
  await apply('from0825'); await run();
  const skip = await evalJS(`
    var b = window.__S.bondRows();
    return {kinds:b.map(function(x){ return x.cells[1]; }),
            skipFlags:b.map(function(x){ return x.skip; }),
            italic:b.filter(function(x){ return x.skip; }).map(function(x){ return x.style; }),
            daily:window.__S.dailyRows().map(function(r){ return r[0]; }),
            PSA:window.__S.stat('투자실행금'), foot:window.__S.dailyFoot()};`);
  P('시작일 ' + SF.scenarios.from0825.value + ' : ' + B.dailyDates[0] + ' 기간 내 행이 기간 밖으로 빠진다',
    JSON.stringify(skip.kinds) === JSON.stringify(SF.from0825.bondKinds)
    && skip.skipFlags[SF.from0825.bondKinds.indexOf('기간 밖')] === true, skip.kinds);
  P('기간 밖 행은 회색 이탤릭', skip.italic.length > 0 && skip.italic.every(v => v === 'italic'), skip.italic);
  P('기간 밖 행은 일별 표·집계에서 빠진다',
    JSON.stringify(skip.daily) === JSON.stringify(SF.from0825.dailyDates)
    && skip.PSA.indexOf(SF.from0825.psa) >= 0, {daily:skip.daily, PSA:skip.PSA});
  P('기간 밖 제외 후에도 상환액 = PSA + PSM',
    n(skip.foot[1]) === n(skip.foot[2]) + n(skip.foot[3]), skip.foot);

  /* ── 6) 행 추가·삭제 ── */
  console.log('\n[6] 행 추가·삭제');
  await reset();
  const add = await evalJS(`
    var before = window.__S.snap();
    document.querySelector('[data-act="sim-add"]').click();
    var after = window.__S.snap();
    var last = ${SF.seedRows};
    return {before:before.total, beforeRows:before.rows, after:after.total, afterRows:after.rows,
            newRow:{plat:window.__S.rowVal(last,'plat'), amt:window.__S.rowVal(last,'amt'),
                    sd:window.__S.rowVal(last,'sd'), dd:window.__S.rowVal(last,'dd'),
                    days:window.__S.rowDays(last)}};`);
  P('+ 채권 추가 — 행이 늘고 합계 줄이 따라온다',
    add.beforeRows === SF.seedRows && add.afterRows === SF.addRow.rows
    && add.after === SF.addRow.totalText, add);
  P('새 행 기본값 = 카드사 / ' + SF.addRow.amt + ' / 종료일-' + SF.platDur.card + ' / 종료일',
    add.newRow.plat === SF.addRow.plat && add.newRow.amt === SF.addRow.amt
    && add.newRow.sd === SF.addRow.sd && add.newRow.dd === SF.addRow.dd
    && add.newRow.days === SF.addRow.days, add.newRow);
  await run();
  const add2 = await evalJS('return {bonds:window.__S.bondRows().length, exec:window.__S.statusRows()[0][1]};');
  P('추가한 행이 결과에 들어온다', add2.bonds === 9, add2);

  const del = await evalJS(`
    var btns = document.querySelectorAll('[data-act="sim-del"]');
    var nBtn = btns.length;
    btns[${SF.seedRows}].click();
    var a = window.__S.snap();
    return {nBtn:nBtn, rows:a.rows, total:a.total};`);
  P('삭제 — 행이 줄고 합계 줄이 따라온다',
    del.nBtn === SF.addRow.rows && del.rows === SF.seedRows && del.total === SF.seedTotalText, del);

  const one = await evalJS(`
    var i;
    for(i = 0; i < ${SF.seedRows - 1}; i++) document.querySelector('[data-act="sim-del"]').click();
    var s = window.__S.snap();
    return {rows:s.rows, delBtns:document.querySelectorAll('[data-act="sim-del"]').length, total:s.total};`);
  P('1건만 남으면 삭제 버튼이 사라진다 (page.tsx:288 과 같은 조건)',
    one.rows === 1 && one.delBtns === 0, one);

  /* ── 7) 실행 버튼 비활성 ── */
  console.log('\n[7] 필수 미충족');
  await reset();
  const bad1 = await evalJS(`
    window.__S.setVar('from', '${SF.badFrom}');
    var s = window.__S.snap();
    var w = document.querySelector('[data-mount="sim-warn"]');
    return {disabled:s.btnDisabled, warn:s.warn, text:w.textContent.trim()};`);
  P('시작일 > 종료일 → 버튼 비활성 · 안내 한 줄',
    bad1.disabled === true && bad1.warn === true
    && bad1.text === '시작일은 종료일보다 이후일 수 없습니다.', bad1);
  const back = await evalJS("window.__S.setVar('from', '" + SF.defaults.from + "'); return window.__S.snap();");
  P('되돌리면 다시 활성', back.btnDisabled === false && back.warn === false, back);

  await reset();
  const bad2 = await evalJS(`
    window.__S.setRow(0, 'dd', '${SF.badDue}');
    return {days:window.__S.rowDays(0), disabled:window.__S.snap().btnDisabled};`);
  P('선정산일 > 정산예정일 행 → 금융일수 - · 버튼 비활성',
    bad2.days === '-' && bad2.disabled === true, bad2);

  await reset();
  const bad3 = await evalJS(`
    window.__S.setVar('r', '0');
    var a = window.__S.snap().btnDisabled;
    window.__S.setVar('r', '100');
    var b = window.__S.snap().btnDisabled;
    window.__S.setVar('r', '${SF.defaults.rate}');
    return {zero:a, hundred:b, back:window.__S.snap().btnDisabled};`);
  P('할인율 0 · 100 → 버튼 비활성', bad3.zero === true && bad3.hundred === true && bad3.back === false, bad3);

  const bad4 = await evalJS(`
    var i;
    for(i = 0; i < ${SF.seedRows - 1}; i++) document.querySelector('[data-act="sim-del"]').click();
    var one = window.__S.snap().btnDisabled;
    window.__S.setRow(0, 'sd', '');
    return {one:one, emptyDate:window.__S.snap().btnDisabled};`);
  P('선정산일 비우면 버튼 비활성', bad4.one === false && bad4.emptyDate === true, bad4);

  /* ── 8) 상태 낱장 도달 ── */
  console.log('\n[8] 상태·해시');
  const hash = await evalJS(`
    go('invest-sim','result');
    var a = window.__S.snap(), h = location.hash;
    location.hash = '#invest-sim';
    return {result:{state:a.state, badge:a.badge, outLen:a.outLen, hash:h}};`);
  P('go(invest-sim, result) — 결과 상태로 바로 선다',
    hash.result.state === 'result' && hash.result.badge === '실행 결과'
    && hash.result.outLen > 2000 && hash.result.hash === '#invest-sim/result', hash.result);

  const file = await evalJS(`
    var a = document.createElement('a'); a.href = 'invest-sim--result.html'; a.textContent = 'x';
    document.body.appendChild(a); a.click(); a.remove();
    return {hash:location.hash, state:window.__S.sec().dataset.state};`);
  P('낱장 파일명 링크 → 같은 상태로 붙는다',
    file.state === 'result' && file.hash === '#invest-sim/result', file);

  /* ── 9) 다른 화면 불변식 ── */
  console.log('\n[9] 기존 화면 불변식');
  const inv = await evalJS(`
    go('invest-sim','default');
    window.__S.setVar('cash','1'); window.__S.setVar('r','3');
    window.__S.setRow(0,'amt','1');
    window.__S.btn().click();
    return 1;`);
  await sleep(500);
  const keep = await evalJS('return window.__selfcheck();');
  P('시뮬레이션을 굴려도 투자실행액 ' + FACTS.exec.toLocaleString('en-US') + ' 불변',
    keep.assetExecRow === FACTS.exec, keep.assetExecRow);
  P('투자자산 ' + FACTS.total.toLocaleString('en-US') + ' · 순현금 '
    + FACTS.cash.toLocaleString('en-US') + ' 불변',
    keep.assetTotal === FACTS.total && keep.assetTotal - keep.assetExecRow === FACTS.cash, keep.assetTotal);
  P('비중 합 100.0% · 로스터 ' + ROSTER + '건 불변',
    keep.ratioSum === 100 && keep.contracts === ROSTER, keep);
  P('SIM 이 원장을 건드리지 않는다',
    keep.rollupMatchesLedger === true && keep.ledgerDays === FACTS.ledgerDays, keep.ledgerDays);
  R.selfcheck = keep;


  /* ── 10) 대표 재전달 대기 표기 (⑤ · ⑥) ── */
  console.log('\n[10] 대표 재전달 대기 표기');
  await evalJS("go('invest-sim','result'); return 1;");
  const pend = await evalJS(`
    return {ty5:window.__S.ty5Label(), ty5Badge:window.__S.ty5Badge(),
            th:window.__S.dailyTh(), thBadge:window.__S.dailyThBadge()};`);
  P('⑤ 투자자산 대비 — 값은 두고 ' + SF.pendBadge + ' 배지',
    pend.ty5Badge === SF.pendBadge && pend.ty5.indexOf(SF.pendRow) >= 0, pend.ty5);
  P('⑥ 일별 Ty수익율 열머리 — 배지 + 어느 읽기인지 툴팁',
    pend.thBadge === SF.pendBadge && pend.th === SF.tyThText, pend.th);
  const pendPf = await evalJS(`
    go('invest-profit','default');
    var sec = document.querySelector('section.screen[data-screen="invest-profit"]');
    var g = sec.querySelectorAll('.ty-split > div');
    var th = sec.querySelectorAll('.tbl thead th');
    return {ty5:g[1].querySelector('.ty-label').textContent.trim(),
            ty5Badge:(g[1].querySelector('.ty-label .badge')||{textContent:''}).textContent.trim(),
            th:th[th.length-1].textContent.trim(),
            values:Array.prototype.map.call(sec.querySelectorAll('.ty-split .summary-value'),
                     function(e){ return e.textContent.trim(); })};`);
  P('투자 수익 화면도 같은 표기 — ⑤ 배지 · ⑥ 열머리',
    pendPf.ty5Badge === SF.pendBadge && pendPf.ty5.indexOf(SF.pendRow) >= 0
    && pendPf.th === SF.tyThText, {ty5:pendPf.ty5Badge, th:pendPf.th});
  P('표기를 붙여도 ⑤ 값 자체는 그대로 뜬다',
    pendPf.values.length === 2 && /^\d+\.\d\d%$/.test(pendPf.values[1]), pendPf.values);

  /* ── 11) 실행 게이트 — 각 칸의 min/max 를 실제로 본다 ── */
  console.log('\n[11] 실행 게이트');
  async function seed(){ await evalJS("go('invest-sim','result'); return 1;"); }
  for(const b of SF.bounds){
    await seed();
    const g = await evalJS(`
      var before = window.__S.snap().outLen;
      window.__S.setVar('${b.k}', '${b.probe}');
      var a = window.__S.snap();
      window.__S.btn().click();
      var after = window.__S.snap();
      return {before:before, disabled:a.btnDisabled, warn:a.warn, text:a.warnText,
              outLen:a.outLen, afterClick:after.outLen};`);
    P(b.label + ' ' + b.probe + ' (' + (b.max === null ? '≥ ' + b.min : b.min + ' ~ ' + b.max) + ') → 버튼 비활성 · 까닭 한 줄 · 묵은 결과 없음',
      g.before > 2000 && g.disabled === true && g.warn === true && g.text === b.msg
      && g.outLen === 0 && g.afterClick === 0, g);
  }
  await seed();
  const gAmt = await evalJS(`
    var before = window.__S.snap().outLen;
    window.__S.setRow(0, 'amt', '-1');
    var a = window.__S.snap();
    return {before:before, disabled:a.btnDisabled, text:a.warnText, outLen:a.outLen};`);
  P('순지급액 -1 → 버튼 비활성 · 까닭 한 줄 · 묵은 결과 없음',
    gAmt.before > 2000 && gAmt.disabled === true && gAmt.text === SF.amtMsg && gAmt.outLen === 0, gAmt);
  await seed();
  const gRange = await evalJS(`
    var before = window.__S.snap().outLen;
    window.__S.setVar('from', '${SF.badFrom}');
    var a = window.__S.snap();
    window.__S.setVar('from', '${SF.defaults.from}');
    var b = window.__S.snap();
    return {before:before, disabled:a.btnDisabled, text:a.warnText, outLen:a.outLen,
            backDisabled:b.btnDisabled, backWarn:b.warn};`);
  P('기간 역전 → 묵은 결과도 함께 내린다 · 되돌리면 다시 활성',
    gRange.before > 2000 && gRange.disabled === true && gRange.text === SF.rangeMsg
    && gRange.outLen === 0 && gRange.backDisabled === false && gRange.backWarn === false, gRange);

  /* ── 12) 입력이 화면을 벗어나도 남는다 ── */
  console.log('\n[12] 입력 유지');
  await evalJS("go('invest-sim','default'); return 1;");
  await evalJS("window.__S.setVar('cash', '30000000'); return 1;");
  await run();
  const keepIn = await evalJS(`
    var before = {cash:window.__S.varVal('cash'), state:window.__S.snap().state, outLen:window.__S.snap().outLen};
    document.querySelector('.nav-item[data-menu="merchants"]').click();
    document.querySelector('.nav-item[data-menu="invest-sim"]').click();
    var a = window.__S.snap();
    return {before:before, cash:window.__S.varVal('cash'), state:a.state, outLen:a.outLen};`);
  P('순현금 30,000,000 · 실행 결과가 메뉴를 오가도 남는다',
    keepIn.before.cash === '30000000' && keepIn.before.outLen > 2000
    && keepIn.cash === '30000000' && keepIn.state === 'result' && keepIn.outLen > 2000, keepIn);
  const deep = await evalJS(`
    location.hash = '#invest-assets';
    location.hash = '#invest-sim';
    go('invest-sim','default');
    return {cash:window.__S.varVal('cash'), state:window.__S.snap().state, outLen:window.__S.snap().outLen};`);
  P('상태를 콕 집어 부르면(딥링크) 그때는 씨앗을 다시 심는다',
    deep.cash === String(SF.defaults.cash) && deep.state === 'default' && deep.outLen === 0, deep);

  /* ── 13) 투자자산 규모 · 유휴자금 비율 ── */
  console.log('\n[13] 투자자산 규모 · 유휴자금 비율');
  await evalJS("go('invest-sim','default'); return 1;");
  const seedScale = await evalJS("return {asset:window.__S.varVal('asset'), idle:window.__S.varVal('idle')};");
  P('두 칸은 지금 상태에서 되읽은 값으로 선다 (투자자산 = 미회수 투자실행금 + 순현금)',
    seedScale.asset === SF.seedAsset && seedScale.idle === SF.seedIdle, seedScale);
  for(const p of SF.scaleIdle){
    const w = SF.scale[p];
    await evalJS("go('invest-sim','default'); return 1;");
    await evalJS(`window.__S.setScale('asset', '${SF.scaleAsset}'); window.__S.setScale('idle', '${p}'); return 1;`);
    const got = await evalJS(`
      return {asset:window.__S.varVal('asset'), idle:window.__S.varVal('idle'),
              cash:window.__S.varVal('cash'), amts:window.__S.amts()};`);
    await run();
    const st2 = await evalJS("return {status:window.__S.statusRows(), tot:window.__S.snap()};");
    P('투자자산 ' + SF.scaleAsset + ' · 유휴 ' + p + '% → 투자실행액 ' + w.exec + ' (반올림 어긋남 0)',
      got.cash === w.cashField && got.asset === SF.scaleAsset && got.idle === String(p)
      && JSON.stringify(got.amts) === JSON.stringify(w.amts)
      && st2.status[0][1] === w.exec && st2.status[1][1] === w.cash
      && st2.status[2][1] === w.total && st2.status[2][5] === w.shareSum
      && st2.status[0][5] === w.share0 && st2.status[1][5] === w.share1,
      {cash:got.cash, exec:st2.status[0][1], total:st2.status[2][1], 비중:st2.status[2][5]});
    /* 규칙 — 같은 값을 다시 넣어도 결과가 그대로다(멱등). 어느 칸을 마지막에 만졌든 값이 튀지 않는다. */
    const again = await evalJS(`
      window.__S.setScale('idle', '${p}');
      var a = {asset:window.__S.varVal('asset'), idle:window.__S.varVal('idle'),
               cash:window.__S.varVal('cash'), amts:window.__S.amts()};
      window.__S.setScale('asset', '${SF.scaleAsset}');
      var b = {asset:window.__S.varVal('asset'), idle:window.__S.varVal('idle'),
               cash:window.__S.varVal('cash'), amts:window.__S.amts()};
      return {a:a, b:b};`);
    P('유휴 ' + p + '% — 두 칸을 다시 만져도 값이 튀지 않는다(멱등)',
      JSON.stringify(again.a) === JSON.stringify(got) && JSON.stringify(again.b) === JSON.stringify(got),
      again);
  }
  /* 반대 방향 — 순현금을 직접 만지면 두 칸이 되읽힌다 */
  await evalJS("go('invest-sim','default'); return 1;");
  const rev = await evalJS(`
    var b0 = {asset:window.__S.varVal('asset'), idle:window.__S.varVal('idle')};
    window.__S.setVar('cash', '30000000');
    return {before:b0, asset:window.__S.varVal('asset'), idle:window.__S.varVal('idle'),
            amts:window.__S.amts()};`);
  P('순현금을 직접 만지면 두 칸이 되읽힌다 — 행 금액은 건드리지 않는다',
    rev.asset === String(Number(SF.seedAsset) - SF.defaults.cash + 30000000)
    && rev.idle !== rev.before.idle
    && JSON.stringify(rev.amts) === JSON.stringify(SF.seedAmts), rev);

  /* ── 15) ⑤ 단일 원천 · ⑥ 배선 ────────────────────────────────
     대표가 ⑤ 산식을 새로 주면 daily_ledger.ty_asset 한 곳만 고치면 되어야 한다.
     문자열 대조만으로는 배선이 끊긴 것을 못 잡으므로, 화면에서 ⑤ 함수를 인공 값으로 갈아 끼워
     ⑥ 이 따라 움직이는지 행동으로 본다. ③ 도 같은 방식으로 본다. */
  console.log('\n[15] ⑤ 단일 원천 · ⑥ 배선');
  {
    const SRC = fs.readFileSync(path.join(REPO, 'app.html'), 'utf8');
    const cnt = re => (SRC.match(re) || []).length;
    const bodyOf = name => {
      const m = SRC.match(new RegExp('function ' + name + '\\([^)]*\\)\\{([\\s\\S]*?)\\n?\\}'));
      return m ? m[1] : '';
    };
    const w = {
      ty3def: cnt(/function ty3\(/g), ty5def: cnt(/function ty5\(/g), ty6def: cnt(/function ty6\(/g),
      /* ⑤ 산식이 코드에 한 곳에서만 정의된다 — 옛 하드코딩이 남으면 여기서 잡힌다 */
      ty5body: cnt(/ty4 \* psa \/ tot/g),
      hard5: cnt(/TY4 \* PSA \/ \(PSA \+ PSC\)/g) + cnt(/ty4 \* psa \/ \(psa \+ psc\)/g)
             + cnt(/psa \+ psc\) \? ty4/g),
      /* ⑥ 도 마찬가지 — 행 ty 를 직접 계산하던 두 자리가 ty6() 로 모였다 */
      hard6: cnt(/\* 100\) \* 365 \/ g\.[wW]/g),
      ty6call: cnt(/= ty6\(/g),
      ty6usesTy5: bodyOf('ty6').indexOf('ty5(') >= 0,
      ty6usesTy3: bodyOf('ty6').indexOf('ty3(') >= 0,
      tyAssetUsesTy5: bodyOf('tyAssetOf').indexOf('ty5(') >= 0,
      simRunUsesTy5: cnt(/var TY5  = ty5\(/g)
    };
    P('[문자열] ⑤ 정의 1곳 · 하드코딩 0건 · ⑥ 계산 자리 2곳이 모두 ty6()',
      w.ty3def === 1 && w.ty5def === 1 && w.ty6def === 1 && w.ty5body === 1
      && w.hard5 === 0 && w.hard6 === 0 && w.ty6call === 2
      && w.ty6usesTy5 && w.ty6usesTy3 && w.tyAssetUsesTy5 && w.simRunUsesTy5 === 1, w);

    /* 행동 판정 — ty5 를 갈아 끼우고 ⑤·⑥ 이 함께 움직이는지 본다 */
    const CAP = `
      var sp = window.__S.out().querySelectorAll('.ty-split > div');
      var six = window.__S.dailyRows().map(function(r){ return r[r.length - 1]; });
      return {ty4: sp[0].querySelector('.summary-value').textContent.trim(),
              ty5: sp[1].querySelector('.summary-value').textContent.trim(),
              six: six, exec: window.__S.statusRows()[0][1]};`;
    await evalJS("go('invest-sim','default'); return 1;");
    await run();
    const b0 = await evalJS(CAP);
    const n = t => Number(String(t).replace(/[^0-9.-]/g, ''));

    await evalJS("window.__ty5_orig = ty5; window.ty5 = function(a, b, c){ return 7.77; }; return 1;");
    await run();
    const sw = await evalJS(CAP);
    await evalJS("window.ty5 = window.__ty5_orig; return 1;");
    await run();
    const rb = await evalJS(CAP);
    const badB = [];
    if(!b0.six.length) badB.push('일별 행 0건 — 대상이 없으면 통과시키지 않는다');
    if(n(sw.ty5) !== 7.77) badB.push('⑤ 가 인공 값을 안 따라왔다 ' + sw.ty5);
    if(sw.six.some(v => n(v) !== 7.77)) badB.push('⑥ 가 안 따라왔다 ' + JSON.stringify(sw.six));
    if(sw.ty4 !== b0.ty4) badB.push('④ 가 흔들렸다 ' + b0.ty4 + ' -> ' + sw.ty4);
    if(JSON.stringify(rb) !== JSON.stringify(b0)) badB.push('되돌려도 원래 값이 아니다');
    P('[행동] ⑤ 함수를 인공 값으로 갈면 ⑤·⑥ 이 함께 움직이고 되돌리면 복귀',
      badB.length === 0, {bad:badB, base:b0.six.slice(0, 3), swapped:sw.six.slice(0, 3),
                          ty5:{base:b0.ty5, swapped:sw.ty5, back:rb.ty5}});

    await evalJS("window.__ty3_orig = ty3; window.ty3 = function(e){ return e * 2; }; return 1;");
    await run();
    const s3 = await evalJS(CAP);
    await evalJS("window.ty3 = window.__ty3_orig; return 1;");
    await run();
    const r3 = await evalJS(CAP);
    const bad3 = [];
    if(!s3.six.length) bad3.push('일별 행 0건');
    s3.six.forEach((v, i) => {
      if(Math.abs(n(v) - n(b0.six[i]) / 2) > 0.011)
        bad3.push(b0.six[i] + ' -> ' + v + ' (기대 ' + (n(b0.six[i]) / 2).toFixed(2) + ')');
    });
    if(JSON.stringify(r3) !== JSON.stringify(b0)) bad3.push('되돌려도 원래 값이 아니다');
    P('[행동] ③ 함수를 2배로 갈면 ⑥ 이 절반으로 움직이고 되돌리면 복귀',
      bad3.length === 0, {bad:bad3, base:b0.six.slice(0, 3), swapped:s3.six.slice(0, 3)});
  }

  /* ── 14) 정적 낱장 ── */
  console.log('\n[14] 정적 낱장');
  await send('Page.navigate', {url:'http://127.0.0.1:' + PORT + '/invest-sim.html'});
  await sleep(700);
  const leaf1 = await evalJS(`
    return {nav:document.querySelectorAll('.sidebar .nav-item[data-menu]').length,
            active:document.body.dataset.active,
            title:document.querySelector('.page-title').textContent.trim(),
            rows:document.querySelectorAll('.sim-row').length,
            total:document.querySelector('.sim-total').textContent.trim(),
            tables:document.querySelectorAll('.tbl').length,
            fields:Array.prototype.map.call(document.querySelectorAll('.sim-grid .filter-field label'),
                     function(e){ return e.textContent.trim(); }),
            asset:document.querySelector('#sim-asset').value,
            idle:document.querySelector('#sim-idle').value,
            btn:document.querySelector('.sim-run').textContent.trim()};`);
  P('invest-sim 낱장 — 8메뉴 · ' + SF.seedRows + '행 · 결과 없음',
    leaf1.nav === 8 && leaf1.active === 'invest-sim' && leaf1.rows === SF.seedRows
    && leaf1.total === SF.seedTotalText && leaf1.tables === 0
    && leaf1.btn === '시뮬레이션 실행', leaf1);
  P('낱장 기준 변수 8칸 — 투자자산 규모 · 유휴자금 비율이 통합본과 같은 값',
    leaf1.fields.length === 8 && leaf1.fields[0] === '투자자산 규모 (원)'
    && leaf1.fields[1] === '유휴자금 비율 (%)'
    && leaf1.asset === SF.seedAsset && leaf1.idle === SF.seedIdle, leaf1.fields);

  await send('Page.navigate', {url:'http://127.0.0.1:' + PORT + '/invest-sim--result.html'});
  await sleep(700);
  const leaf2 = await evalJS(`
    var t = document.querySelectorAll('.tbl');
    function cells(tr){ return Array.prototype.map.call(tr.children, function(td){ return td.textContent.trim(); }); }
    return {nav:document.querySelectorAll('.sidebar .nav-item[data-menu]').length,
            badge:(document.querySelector('.state-badge')||{textContent:''}).textContent.trim(),
            tables:t.length,
            status:Array.prototype.map.call(t[1].querySelectorAll('tbody tr'), cells),
            foot:cells(t[2].querySelector('tfoot tr')),
            bonds:t[0].querySelectorAll('tbody tr').length,
            daily:t[2].querySelectorAll('tbody tr').length,
            cards:document.querySelectorAll('.summary-card').length,
            ty5:document.querySelectorAll('.ty-split > div')[1].querySelector('.ty-label').textContent.trim(),
            ty5Badge:(document.querySelectorAll('.ty-split > div')[1].querySelector('.ty-label .badge')
                      || {textContent:''}).textContent.trim(),
            dailyTh:(function(){ var th = t[2].querySelectorAll('thead th'); return th[th.length-1].textContent.trim(); })()};`);
  const b = R.baseline;
  P('invest-sim--result 낱장 — 배지 · 표 3 · 카드 4',
    leaf2.nav === 8 && leaf2.badge === '실행 결과' && leaf2.tables === 3
    && leaf2.bonds === SF.seedRows && leaf2.daily === B.dailyDates.length
    && leaf2.cards === 4, leaf2);
  P('낱장 현황 표 = 통합본 현황 표',
    JSON.stringify(leaf2.status) === JSON.stringify(b.status), {낱장:leaf2.status[0], 통합본:b.status[0]});
  P('낱장 일별 합계행 = 통합본 합계행',
    JSON.stringify(leaf2.foot) === JSON.stringify(b.foot), {낱장:leaf2.foot, 통합본:b.foot});
  P('낱장도 ⑤ · ⑥ 에 같은 대표 재전달 대기 표기',
    leaf2.ty5Badge === SF.pendBadge && leaf2.ty5.indexOf(SF.pendRow) >= 0
    && leaf2.dailyTh === SF.tyThText, {ty5:leaf2.ty5Badge, th:leaf2.dailyTh});

  /* ── 15) 콘솔 ── */
  R.console = consoleErrors.filter(c => c.indexOf('/favicon.ico') < 0);
  P('콘솔 에러 0', R.console.length === 0, R.console.slice(0, 5));

  fs.writeFileSync(path.join(OUTDIR, 'verify_sim_result.json'), JSON.stringify(R, null, 1));
  console.log('\n== 뷰포트 ==', JSON.stringify(R.viewport));
  console.log('== 판정 ==', R.cases.length - failed, '/', R.cases.length, failed ? ('FAIL ' + failed) : 'ALL PASS');
  ws.close(); chrome.kill(); server.close();
  process.exit(failed ? 1 : 0);
}
main().catch(e => { console.error('VERIFY ERROR', e); process.exit(1); });
