/* 투자 시뮬레이션 헤드리스 검증 — 창을 띄우지 않는다(--headless=new).
   실제 입력·클릭으로 몬다. 값을 코드에서 읽어 오는 것이 아니라 화면에 찍힌 글자를 읽는다.

     1) 기본값 실행 — W 3.7 · Ty 10.85% · 비중 합 100.0% · 상환액 = PSA + PSM
     2) 입력을 바꾸면 결과가 따라 바뀐다 — 할인율 · 순현금 · 미지급률 · 기간 · 플랫폼
     3) S입금부족율 > 할인율 → 투자수익 음수를 그대로 보인다 (설계 L-3)
     4) 기간 밖 행은 회색 이탤릭 · 집계 제외
     5) 채권 행 추가 · 삭제
     6) 필수 미충족이면 실행 버튼 비활성 · 실행 전에는 결과가 없다
     7) 정적 낱장 2종이 통합본과 같은 값을 싣는다
     8) 콘솔 에러 0

   macOS 함정 — --window-size=1440,H 는 실제 뷰포트 1440x(H-87). 1287 로 줘야 1200 이 잡힌다. */
const http = require('http');
const fs   = require('fs');
const path = require('path');
const os   = require('os');
const { spawn } = require('child_process');

const REPO   = '/Users/semi/cursor/payhug-investor-admin';
const OUTDIR = '/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin';
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
    snap: function(){
      return {rows: window.__S.sec().querySelectorAll('[data-mount="sim-rows"] .sim-row').length,
              total: document.querySelector('[data-mount="sim-total"]').textContent.trim(),
              btnLabel: window.__S.btn().textContent.trim(),
              btnDisabled: window.__S.btn().disabled,
              warn: !document.querySelector('[data-mount="sim-warn"]').hidden,
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
    '--user-data-dir=' + profile, '--no-first-run', '--no-default-browser-check',
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
  P('기본 입력 8행 · 합계 한 줄',
    s0.rows === 8 && s0.total === '총 8건, 합계 1,500,000,000원', s0);
  P('실행 버튼 라벨 · 활성', s0.btnLabel === '시뮬레이션 실행' && s0.btnDisabled === false, s0);
  const days0 = await evalJS('var o=[],i; for(i=0;i<8;i++) o.push(window.__S.rowDays(i)); return o;');
  P('금융일수 파생 표시', JSON.stringify(days0) === JSON.stringify(['2일','3일','5일','6일','2일','3일','5일','6일']), days0);

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
  P('현황 · 투자실행액 행', st[0][0] === '투자실행액' && st[0][1] === '998,900,000'
    && st[0][2] === '3.7일' && st[0][3] === '0.07%' && st[0][4] === '10.85%'
    && st[0][5] === '90.5%' && st[0][6] === '㈜페이허그', st[0]);
  P('현황 · 순현금 행', st[1][0] === '순현금' && st[1][1] === '105,300,000'
    && st[1][5] === '9.5%' && st[1][6] === '㈜쿠콘', st[1]);
  P('현황 · 합계 = 투자자산 · 비중 합 100.0%',
    st[2][1] === '1,104,200,000' && st[2][5] === '100.0%', st[2]);
  P('W 3.7 — 투자 자산 화면과 같은 자리', st[0][2] === '3.7일', st[0][2]);
  P('Ty 10.85% — 투자 자산 화면과 같은 자리', st[0][4] === '10.85%', st[0][4]);
  P('요약 카드 4장', base.summary.자산.value === '1,104,200,000원'
    && base.summary.실행.value === '998,900,000원' && base.summary.현금.value === '105,300,000원'
    && base.summary.ty.value === '10.85%' && base.summary.ty.sub === 'W금융일수 3.7일 기준',
    Object.keys(base.summary).map(k => base.summary[k].value));

  const foot = base.foot;
  const n = t => Number(String(t).replace(/[^0-9.-]/g, ''));
  P('검산 상환액 = PSA + PSM (일별 합계행)',
    n(foot[1]) === n(foot[2]) + n(foot[3]) && n(foot[1]) === 499650000, foot);
  P('일별 합계 PSD 3.1 · ④ 4.71%', foot[4].indexOf('3.1') === 0 && foot[5].indexOf('4.71%') === 0, foot);
  P('일별 행 4건 (만기 채권의 서로 다른 정산예정일)',
    base.daily.length === 4 && base.daily[0][0] === '2026-08-24' && base.daily[3][0] === '2026-08-27',
    base.daily.map(r => r[0]));
  P('수익 현황 — 투자실행금 · 투자수익 · 기간',
    base.실행금.indexOf('499,450,000') >= 0 && base.수익.indexOf('200,000') >= 0
    && base.기간.indexOf('7일') >= 0 && base.기간.indexOf('2026-08-21 ~ 2026-08-27') >= 0,
    [base.실행금, base.수익, base.기간]);
  P('Ty 2분할 — ④ 4.71% · ⑤ 1.90%',
    base.tyStat.indexOf('4.71') >= 0 && base.tyStat.indexOf('1.90') >= 0, base.tyStat);
  P('채권별 산출 8행 · 구분 미회수 4 · 만기 4',
    base.bonds.length === 8 && base.bonds.filter(b => b[1] === '미회수').length === 4
    && base.bonds.filter(b => b[1] === '만기').length === 4, base.bonds.map(b => b[1]));
  P('채권 1행 = 설계 검산표',
    JSON.stringify(base.bonds[0]) === JSON.stringify(
      ['1','미회수','카드사','300,000,000','2','299,670,000','330,000','210,000','120,000','299,790,000']),
    base.bonds[0]);

  /* ── 3) 입력을 바꾸면 결과가 바뀐다 ── */
  console.log('\n[3] 입력 변동');
  async function reset(){ await evalJS("go('invest-sim','default'); return 1;"); }

  await reset();
  await evalJS("window.__S.setVar('r', '0.22'); return 1;"); await run();
  const r22 = await evalJS("var s=window.__S.statusRows(); return {ty:s[0][4], exec:s[0][1], S:s[0][3], fee:window.__S.bondRows()[0].cells[6]};");
  P('할인율 0.11 → 0.22 : Ty · 투자실행액 · 수수료가 함께 움직인다',
    r22.ty !== '10.85%' && r22.exec !== '998,900,000' && r22.fee === '660,000', r22);

  await reset();
  await evalJS("window.__S.setVar('cash', '200000000'); return 1;"); await run();
  const c2 = await evalJS("var s=window.__S.statusRows(); return {cash:s[1][1], tot:s[2][1], sh:[s[0][5],s[1][5],s[2][5]], ty5:window.__S.stat('Ty수익율')};");
  P('순현금 1.053억 → 2억 : 순현금 · 투자자산 · 비중 · ⑤ 가 함께 움직인다',
    c2.cash === '200,000,000' && c2.tot === '1,198,900,000'
    && c2.sh[2] === '100.0%' && c2.sh[0] !== '90.5%', c2);

  await reset();
  await evalJS("window.__S.setVar('unpaid', '0.05'); return 1;"); await run();
  const u5 = await evalJS("var s=window.__S.statusRows(); return {S:s[0][3], ded:window.__S.bondRows()[0].cells[7], M:window.__S.bondRows()[0].cells[8], profit:window.__S.stat('투자수익')};");
  P('미지급률 0.08 → 0.05 : S · 차감 · 투자수익이 함께 움직인다',
    u5.S === '0.04%' && u5.ded === '120,000' && u5.M === '210,000' && u5.profit.indexOf('350,000') >= 0, u5);

  await reset();
  await evalJS("window.__S.setVar('to', '2026-08-31'); return 1;"); await run();
  const t31 = await evalJS(`
    var b = window.__S.bondRows();
    return {kinds:b.map(function(x){ return x.cells[1]; }), daily:window.__S.dailyRows().length,
            기간:window.__S.stat('검색대상기간'), exec:window.__S.statusRows()[0][1]};`);
  P('종료일 08-27 → 08-31 : 만기/미회수 경계가 옮겨간다 (09-01 요기요 1건만 미회수로 남는다)',
    t31.kinds.filter(k => k === '만기').length === 7
    && t31.kinds.filter(k => k === '미회수').length === 1 && t31.kinds[3] === '미회수'
    && t31.daily === 7 && t31.기간.indexOf('11일') >= 0 && t31.exec === '199,780,000', t31);

  await reset();
  const plat = await evalJS(`
    var before = {due:window.__S.rowVal(0,'dd'), days:window.__S.rowDays(0)};
    window.__S.setRow(0, 'plat', 'yo');
    return {before:before, after:{due:window.__S.rowVal(0,'dd'), days:window.__S.rowDays(0)}};`);
  P('플랫폼 카드사 → 요기요 : 정산예정일이 선정산일 + 6 으로 다시 채워진다',
    plat.before.due === '2026-08-28' && plat.before.days === '2일'
    && plat.after.due === '2026-09-01' && plat.after.days === '6일', plat);
  const platAll = await evalJS(`
    var out = [], m = {card:'2026-08-28', bm:'2026-08-29', cpe:'2026-08-31', yo:'2026-09-01'};
    ['card','bm','cpe','yo'].forEach(function(k){
      window.__S.setRow(0, 'plat', k);
      out.push({k:k, due:window.__S.rowVal(0,'dd'), days:window.__S.rowDays(0), want:m[k]});
    });
    return out;`);
  P('플랫폼 4종 만기 2·3·5·6',
    platAll.every(x => x.due === x.want) &&
    JSON.stringify(platAll.map(x => x.days)) === JSON.stringify(['2일','3일','5일','6일']), platAll);

  await reset();
  await evalJS("window.__S.setRow(0,'amt','800000000'); return 1;"); await run();
  const amt = await evalJS("return {total:document.querySelector('[data-mount=\"sim-total\"]').textContent.trim(), exec:window.__S.statusRows()[0][1], A:window.__S.bondRows()[0].cells[5]};");
  P('순지급액 3억 → 8억 : 합계 줄 · 투자실행액 · Ai 가 함께 움직인다',
    amt.total === '총 8건, 합계 2,000,000,000원' && amt.A === '799,120,000'
    && amt.exec === '1,498,350,000', amt);

  /* ── 4) 음수 투자수익 (L-3) ── */
  console.log('\n[4] 음수 투자수익');
  await reset();
  await evalJS("window.__S.setVar('unpaid', '0.20'); return 1;"); await run();
  const neg = await evalJS(`
    var b = window.__S.bondRows(), f = window.__S.dailyFoot();
    return {S:window.__S.statusRows()[0][3], M:b[0].cells[8], profit:window.__S.stat('투자수익'),
            foot:f, ty:window.__S.stat('Ty수익율'),
            negCls:!!window.__S.out().querySelector('.summary-value.neg')};`);
  P('S 0.19% > 할인율 0.11% → 채권 투자수익 음수',
    neg.S === '0.19%' && n(neg.M) < 0, {S:neg.S, M:neg.M});
  P('수익 현황 투자수익 음수를 그대로 보인다',
    n(neg.profit.replace('투자수익','')) < 0 && neg.negCls === true, neg.profit);
  P('음수여도 상환액 = PSA + PSM 항등식 유지',
    n(neg.foot[1]) === n(neg.foot[2]) + n(neg.foot[3]), neg.foot);

  /* ── 5) 기간 밖 행 ── */
  console.log('\n[5] 기간 밖');
  await reset();
  await evalJS("window.__S.setVar('from', '2026-08-25'); return 1;"); await run();
  const skip = await evalJS(`
    var b = window.__S.bondRows();
    return {kinds:b.map(function(x){ return x.cells[1]; }),
            skipFlags:b.map(function(x){ return x.skip; }),
            italic:b.filter(function(x){ return x.skip; }).map(function(x){ return x.style; }),
            daily:window.__S.dailyRows().map(function(r){ return r[0]; }),
            PSA:window.__S.stat('투자실행금'), foot:window.__S.dailyFoot()};`);
  P('시작일 08-25 : 08-24 만기 행이 기간 밖으로 빠진다',
    skip.kinds[4] === '기간 밖' && skip.skipFlags[4] === true, skip.kinds);
  P('기간 밖 행은 회색 이탤릭', skip.italic.length > 0 && skip.italic.every(v => v === 'italic'), skip.italic);
  P('기간 밖 행은 일별 표·집계에서 빠진다',
    skip.daily.indexOf('2026-08-24') < 0 && skip.daily.length === 3
    && skip.PSA.indexOf('299,670,000') >= 0, {daily:skip.daily, PSA:skip.PSA});
  P('기간 밖 제외 후에도 상환액 = PSA + PSM',
    n(skip.foot[1]) === n(skip.foot[2]) + n(skip.foot[3]), skip.foot);

  /* ── 6) 행 추가·삭제 ── */
  console.log('\n[6] 행 추가·삭제');
  await reset();
  const add = await evalJS(`
    var before = window.__S.snap();
    document.querySelector('[data-act="sim-add"]').click();
    var after = window.__S.snap();
    var last = 8;
    return {before:before.total, beforeRows:before.rows, after:after.total, afterRows:after.rows,
            newRow:{plat:window.__S.rowVal(last,'plat'), amt:window.__S.rowVal(last,'amt'),
                    sd:window.__S.rowVal(last,'sd'), dd:window.__S.rowVal(last,'dd'),
                    days:window.__S.rowDays(last)}};`);
  P('+ 채권 추가 — 행이 늘고 합계 줄이 따라온다',
    add.beforeRows === 8 && add.afterRows === 9 && add.after === '총 9건, 합계 1,600,000,000원', add);
  P('새 행 기본값 = 카드사 / 100,000,000 / 종료일-2 / 종료일',
    add.newRow.plat === 'card' && add.newRow.amt === '100000000'
    && add.newRow.sd === '2026-08-25' && add.newRow.dd === '2026-08-27' && add.newRow.days === '2일', add.newRow);
  await run();
  const add2 = await evalJS('return {bonds:window.__S.bondRows().length, exec:window.__S.statusRows()[0][1]};');
  P('추가한 행이 결과에 들어온다', add2.bonds === 9, add2);

  const del = await evalJS(`
    var btns = document.querySelectorAll('[data-act="sim-del"]');
    var nBtn = btns.length;
    btns[8].click();
    var a = window.__S.snap();
    return {nBtn:nBtn, rows:a.rows, total:a.total};`);
  P('삭제 — 행이 줄고 합계 줄이 따라온다',
    del.nBtn === 9 && del.rows === 8 && del.total === '총 8건, 합계 1,500,000,000원', del);

  const one = await evalJS(`
    var i;
    for(i = 0; i < 7; i++) document.querySelector('[data-act="sim-del"]').click();
    var s = window.__S.snap();
    return {rows:s.rows, delBtns:document.querySelectorAll('[data-act="sim-del"]').length, total:s.total};`);
  P('1건만 남으면 삭제 버튼이 사라진다 (page.tsx:288 과 같은 조건)',
    one.rows === 1 && one.delBtns === 0, one);

  /* ── 7) 실행 버튼 비활성 ── */
  console.log('\n[7] 필수 미충족');
  await reset();
  const bad1 = await evalJS(`
    window.__S.setVar('from', '2026-09-10');
    var s = window.__S.snap();
    var w = document.querySelector('[data-mount="sim-warn"]');
    return {disabled:s.btnDisabled, warn:s.warn, text:w.textContent.trim()};`);
  P('시작일 > 종료일 → 버튼 비활성 · 안내 한 줄',
    bad1.disabled === true && bad1.warn === true
    && bad1.text === '시작일은 종료일보다 이후일 수 없습니다.', bad1);
  const back = await evalJS("window.__S.setVar('from', '2026-08-21'); return window.__S.snap();");
  P('되돌리면 다시 활성', back.btnDisabled === false && back.warn === false, back);

  await reset();
  const bad2 = await evalJS(`
    window.__S.setRow(0, 'dd', '2026-08-20');
    return {days:window.__S.rowDays(0), disabled:window.__S.snap().btnDisabled};`);
  P('선정산일 > 정산예정일 행 → 금융일수 - · 버튼 비활성',
    bad2.days === '-' && bad2.disabled === true, bad2);

  await reset();
  const bad3 = await evalJS(`
    window.__S.setVar('r', '0');
    var a = window.__S.snap().btnDisabled;
    window.__S.setVar('r', '100');
    var b = window.__S.snap().btnDisabled;
    window.__S.setVar('r', '0.11');
    return {zero:a, hundred:b, back:window.__S.snap().btnDisabled};`);
  P('할인율 0 · 100 → 버튼 비활성', bad3.zero === true && bad3.hundred === true && bad3.back === false, bad3);

  const bad4 = await evalJS(`
    var i;
    for(i = 0; i < 7; i++) document.querySelector('[data-act="sim-del"]').click();
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
  P('시뮬레이션을 굴려도 투자실행액 1,523,100,000 불변', keep.assetExecRow === 1523100000, keep.assetExecRow);
  P('투자자산 1,628,400,000 · 순현금 105,300,000 불변',
    keep.assetTotal === 1628400000 && keep.assetTotal - keep.assetExecRow === 105300000, keep.assetTotal);
  P('비중 합 100.0% · 로스터 16건 불변', keep.ratioSum === 100 && keep.contracts === 16, keep);
  P('SIM 이 원장을 건드리지 않는다', keep.rollupMatchesLedger === true && keep.ledgerDays === 180, keep.ledgerDays);
  R.selfcheck = keep;

  /* ── 10) 정적 낱장 ── */
  console.log('\n[10] 정적 낱장');
  await send('Page.navigate', {url:'http://127.0.0.1:' + PORT + '/invest-sim.html'});
  await sleep(700);
  const leaf1 = await evalJS(`
    return {nav:document.querySelectorAll('.sidebar .nav-item[data-menu]').length,
            active:document.body.dataset.active,
            title:document.querySelector('.page-title').textContent.trim(),
            rows:document.querySelectorAll('.sim-row').length,
            total:document.querySelector('.sim-total').textContent.trim(),
            tables:document.querySelectorAll('.tbl').length,
            btn:document.querySelector('.sim-run').textContent.trim()};`);
  P('invest-sim 낱장 — 8메뉴 · 8행 · 결과 없음',
    leaf1.nav === 8 && leaf1.active === 'invest-sim' && leaf1.rows === 8
    && leaf1.total === '총 8건, 합계 1,500,000,000원' && leaf1.tables === 0
    && leaf1.btn === '시뮬레이션 실행', leaf1);

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
            cards:document.querySelectorAll('.summary-card').length};`);
  const b = R.baseline;
  P('invest-sim--result 낱장 — 배지 · 표 3 · 카드 4',
    leaf2.nav === 8 && leaf2.badge === '실행 결과' && leaf2.tables === 3
    && leaf2.bonds === 8 && leaf2.daily === 4 && leaf2.cards === 4, leaf2);
  P('낱장 현황 표 = 통합본 현황 표',
    JSON.stringify(leaf2.status) === JSON.stringify(b.status), {낱장:leaf2.status[0], 통합본:b.status[0]});
  P('낱장 일별 합계행 = 통합본 합계행',
    JSON.stringify(leaf2.foot) === JSON.stringify(b.foot), {낱장:leaf2.foot, 통합본:b.foot});

  /* ── 11) 콘솔 ── */
  R.console = consoleErrors.filter(c => c.indexOf('/favicon.ico') < 0);
  P('콘솔 에러 0', R.console.length === 0, R.console.slice(0, 5));

  fs.writeFileSync(path.join(OUTDIR, 'verify_sim_result.json'), JSON.stringify(R, null, 1));
  console.log('\n== 뷰포트 ==', JSON.stringify(R.viewport));
  console.log('== 판정 ==', R.cases.length - failed, '/', R.cases.length, failed ? ('FAIL ' + failed) : 'ALL PASS');
  ws.close(); chrome.kill(); server.close();
  process.exit(failed ? 1 : 0);
}
main().catch(e => { console.error('VERIFY ERROR', e); process.exit(1); });
