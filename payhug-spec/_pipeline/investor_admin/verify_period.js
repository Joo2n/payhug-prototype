/* 투자 수익 — 기간·집계 단위 조작 검증. 창 없다(--headless=new).
   기간(시작일·종료일)과 집계 단위(일별·주별·월별) 두 축이 서로를 지우지 않는지,
   집계 단위가 데이트피커의 스냅 단위로 실제로 동작하는지, 어느 단위에서도 피커가 살아 있는지를
   실제 클릭·change 이벤트로 확인하고, 매 단계마다 표 행 수와 합계를 읽어 대조한다.
   판정 기준은 period_design.md.
   macOS 헤드리스는 --window-size=1440,H 가 실제 뷰포트 1440×(H-87) 로 잡히는 경우가 있어 87 을 더해 둔다.
   실제로 잡힌 뷰포트는 결과 맨 아래 '뷰포트' 줄에 그대로 적는다. */
const http = require('http'), fs = require('fs'), path = require('path'), os = require('os'), { spawn } = require('child_process');
const REPO  = '/Users/semi/cursor/payhug-investor-admin';
const OUT   = '/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_period_result.json';
const PORT  = 8890 + (process.pid % 40), DPORT = 9590 + (process.pid % 40);
/* 기대값은 채권 원장이 내보낸 사실값에서 읽는다 — 검증기에 숫자를 손으로 적지 않는다. */
const FACTS = JSON.parse(fs.readFileSync(
  '/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/ledger_facts.json', 'utf8'));
const WEEK_EXEC = FACTS.weekExec.toLocaleString('en-US');
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const VIEW_H = 1200, WIN_H = VIEW_H + 87;
const MIME = {'.html':'text/html; charset=utf-8', '.css':'text/css; charset=utf-8', '.png':'image/png', '.webp':'image/webp'};
const server = http.createServer((q, r) => {
  const p = path.join(REPO, decodeURIComponent(q.url.split('?')[0]));
  fs.readFile(p, (e, b) => { if(e){ r.writeHead(404); r.end(''); return; }
    r.writeHead(200, {'Content-Type': MIME[path.extname(p)] || 'application/octet-stream'}); r.end(b); });
});
let id = 0, ws, pend = new Map(); const cons = [];
function send(m, p){ const i = ++id; ws.send(JSON.stringify({id:i, method:m, params:p||{}}));
  return new Promise((res, rej) => pend.set(i, {res, rej})); }
async function ev(x){
  const r = await send('Runtime.evaluate', {expression:'(function(){' + x + '})()', returnByValue:true, awaitPromise:true});
  if(r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails));
  return r.result.value;
}
const sleep = ms => new Promise(r => setTimeout(r, ms));

const BASE = '2026-08-27';        /* 기준일 — 프리셋 종료일은 여섯 묶음 전부 이 날짜다 */
const R = {snap:[], link:[], alive:[], reset:[], invariant:[], picker:[], console:cons};
function P(a, t, d){ d.t = t; d.pass = !!d.pass; a.push(d); }

/* 화면에서 실제로 보이는 것만 읽는다 — 모델 값이 아니라 인풋·버튼·표에 찍힌 것 */
const SNAP = `
  var sec = document.querySelector('section[data-screen="invest-profit"]');
  var fi = sec.querySelector('[data-mount="pf-from"]'), ti = sec.querySelector('[data-mount="pf-to"]');
  function shown(b){ return !b.hidden; }
  var pr = [].filter.call(sec.querySelectorAll('.preset-btn'), shown)
              .map(function(b){ return b.textContent.trim() + (b.classList.contains('active') ? '*' : ''); });
  var tg = [].map.call(sec.querySelectorAll('.toggle-btn'), function(b){
              return b.textContent.trim() + (b.classList.contains('active') ? '*' : ''); });
  var body = sec.querySelectorAll('[data-mount="pf-tbl"] tbody tr');
  var foot = sec.querySelector('[data-mount="pf-tbl"] tfoot tr');
  var head = sec.querySelector('[data-mount="pf-tbl"] th');
  var stat = sec.querySelectorAll('[data-mount="pf-stat"] .summary-value');
  return {
    from: fi.value, to: ti.value,
    clamp: [fi.getAttribute('min'), fi.getAttribute('max'), ti.getAttribute('min'), ti.getAttribute('max')],
    alive: !fi.disabled && !fi.readOnly && !ti.disabled && !ti.readOnly
           && fi.getClientRects().length > 0 && ti.getClientRects().length > 0,
    presets: pr, gran: tg,
    label: (sec.querySelector('[data-mount="pf-stat"] .stat-period') || {}).textContent,
    period: (sec.querySelector('[data-mount="pf-stat"] .summary-sub') || {}).textContent,
    title: sec.querySelector('[data-mount="pf-tbl-title"]').textContent,
    col: head ? head.textContent.trim() : null,
    rows: body.length,
    first: body.length ? body[0].children[0].textContent.trim() : null,
    last:  body.length ? body[body.length - 1].children[0].textContent.trim() : null,
    exec:  foot ? foot.children[2].textContent.trim() : null,
    profit: foot ? foot.children[3].textContent.trim() : null,
    cardExec: stat.length ? stat[0].textContent.replace('원', '').trim() : null,
    state: sec.dataset.state,
    secShown: sec.getClientRects().length > 0,
    warn: !sec.querySelector('[data-mount="pf-warn"]').hidden,
    goDisabled: !!sec.querySelector('[data-mount="pf-go"]').disabled
  };`;

const S = () => ev(SNAP);
const click = sel => ev(`var e = document.querySelector('section[data-screen="invest-profit"] ' + ${JSON.stringify(sel)});
  if(!e) throw new Error('없음 ' + ${JSON.stringify(sel)}); e.click(); return 1;`);
const setDate = (which, v) => ev(`
  var e = document.querySelector('section[data-screen="invest-profit"] [data-mount="pf-' + ${JSON.stringify(which)} + '"]');
  e.value = ${JSON.stringify(v)}; e.dispatchEvent(new Event('change', {bubbles:true})); return 1;`);
const gran = g => click('.toggle-btn[data-gran="' + g + '"]');
const preset = k => click('.preset-btn[data-preset="' + k + '"]');
const home = () => ev(`go('invest-profit', 'default'); return 1;`);
/* 진짜 마우스 클릭 — CDP 로 쏘면 사용자 제스처로 인정돼 showPicker() 가 실제로 통과한다 */
async function realClick(x, y){
  await send('Input.dispatchMouseEvent', {type:'mousePressed',  x:x, y:y, button:'left', buttons:1, clickCount:1});
  await send('Input.dispatchMouseEvent', {type:'mouseReleased', x:x, y:y, button:'left', buttons:0, clickCount:1});
}
/* showPicker 호출을 세어 둔다 — 네이티브 달력은 화면에서 읽을 수 없으니 호출 자체를 잰다 */
const armPicker = () => ev(`
  window.__pick = [];
  if(!HTMLInputElement.prototype.__wrapped){
    var orig = HTMLInputElement.prototype.showPicker;
    HTMLInputElement.prototype.showPicker = function(){
      window.__pick.push(this.getAttribute('data-mount'));
      if(orig) try { return orig.call(this); } catch(e){}
    };
    HTMLInputElement.prototype.__wrapped = true;
  }
  return 1;`);
const pickedList = () => ev('return window.__pick || [];');
const fieldBox = which => ev(`
  var e = document.querySelector('section[data-screen="invest-profit"] [data-mount="pf-' + ${JSON.stringify(which)} + '"]');
  var r = e.getBoundingClientRect();
  return {left:Math.round(r.left), top:Math.round(r.top), w:Math.round(r.width), h:Math.round(r.height)};`);

async function main(){
  await new Promise(r => server.listen(PORT, r));
  const prof = fs.mkdtempSync(path.join(os.tmpdir(), 'vp-'));
  const ch = spawn(CHROME, ['--headless=new', '--remote-debugging-port=' + DPORT, '--user-data-dir=' + prof,
    '--no-first-run', '--disable-gpu', '--window-size=1440,' + WIN_H, 'about:blank'], {stdio:'ignore'});
  let t = null;
  for(let i = 0; i < 60 && !t; i++){
    await sleep(300);
    try { t = await new Promise((res, rej) => { http.get({host:'127.0.0.1', port:DPORT, path:'/json'},
      r => { let d = ''; r.on('data', c => d += c); r.on('end', () => res(JSON.parse(d))); }).on('error', rej); }); }
    catch(e){ t = null; }
  }
  const pg = t.find(x => x.type === 'page'); ws = new WebSocket(pg.webSocketDebuggerUrl);
  await new Promise(r => ws.addEventListener('open', r));
  ws.addEventListener('message', e => { const m = JSON.parse(e.data);
    if(m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error') cons.push(JSON.stringify(m.params.args.map(a => a.value || a.description)));
    if(m.method === 'Runtime.exceptionThrown'){
      var f = ((m.params.exceptionDetails.stackTrace || {}).callFrames || [])[0] || {};
      cons.push(m.params.exceptionDetails.text + ' @ ' + (f.functionName || '?') + ' line ' + ((f.lineNumber || 0) + 1));
    }
    if(m.id && pend.has(m.id)){ pend.get(m.id).res(m.result); pend.delete(m.id); } });
  await send('Runtime.enable'); await send('Page.enable');
  await send('Page.navigate', {url:'http://127.0.0.1:' + PORT + '/app.html#invest-profit/default'});
  await sleep(1200);
  const vp = await ev('return [window.innerWidth, window.innerHeight];');
  await home();                       /* 화면을 세우고 시작한다 */

  /* ══ 1) 초기 상태 · 불변식 ══ */
  let a = await S();
  P(R.invariant, '초기 = 일별 + 일주일 프리셋 · ' + FACTS.weekDays + '행 · 투자실행금 ' + WEEK_EXEC,
    {pass: a.gran[0] === '일별*' && a.presets.join('·') === '일주일*·금월' && a.rows === FACTS.weekDays
           && a.exec === WEEK_EXEC && a.cardExec === WEEK_EXEC
           && a.from === '2026-08-21' && a.to === '2026-08-27',
     기간:a.from + '~' + a.to, 프리셋:a.presets, 단위:a.gran, 행:a.rows, 합계:a.exec, 카드:a.cardExec, 라벨:a.label});
  P(R.invariant, '투자 수익 화면이 실제로 그려진다', {pass: a.secShown, 표시:a.secShown});

  /* ══ 2) 프리셋 = 기간을 채우고 그 자리에서 조회 ══ */
  await preset('month'); let b = await S();
  P(R.link, '일별 금월 프리셋 → 기간 채움 · 즉시 조회 · 그 버튼만 활성',
    {pass: b.from === '2026-08-01' && b.to === '2026-08-27' && b.rows === 27
           && b.presets.join('·') === '일주일·금월*' && b.label === '금월'
           && b.exec !== a.exec && b.exec === b.cardExec,
     기간:b.from + '~' + b.to, 행:a.rows + ' → ' + b.rows, 합계:a.exec + ' → ' + b.exec, 프리셋:b.presets});

  await preset('week'); let c = await S();
  P(R.link, '일별 일주일 프리셋 → ' + FACTS.weekDays + '행 · ' + WEEK_EXEC + ' 복귀',
    {pass: c.from === '2026-08-21' && c.to === '2026-08-27' && c.rows === FACTS.weekDays && c.exec === WEEK_EXEC,
     기간:c.from + '~' + c.to, 행:c.rows, 합계:c.exec});

  /* ══ 3) 피커를 만지면 프리셋이 풀리고 그 자리에서 조회된다 ══ */
  await setDate('from', '2026-08-24'); let d = await S();
  P(R.link, '피커 변경 → 프리셋 활성 해제 · 조회됨',
    {pass: d.from === '2026-08-24' && d.presets.join('·') === '일주일·금월' && d.label === '직접입력'
           && d.rows === 4 && d.exec !== c.exec,
     기간:d.from + '~' + d.to, 프리셋:d.presets, 라벨:d.label, 행:c.rows + ' → ' + d.rows, 합계:c.exec + ' → ' + d.exec});

  /* ══ 4) 스냅 — 집계 단위가 곧 피커의 단위 ══
     프리셋을 보고 있을 때 단위를 바꾸면 새 단위의 같은 자리 프리셋으로 넘어간다(짧은 쪽 ↔ 짧은 쪽).
     탭을 눌렀다고 직접입력으로 떨어지지 않고, 종료일이 기준일보다 뒤로 나가지도 않는다. */
  await home(); await gran('weekly');
  let w = await S();
  P(R.snap, '일별 일주일 → 주별 전환 시 4주 프리셋 08-03~08-27 (종료일이 기준일에서 끊긴다)',
    {pass: w.from === '2026-08-03' && w.to === BASE && w.gran[1] === '주별*'
           && w.rows === 4 && w.title === '주별 투자수익' && w.col === '정산예정주'
           && w.presets.join('·') === '4주*·12주' && w.label === '4주',
     기간:w.from + '~' + w.to, 행:w.rows, 표제목:w.title, 열:w.col, 첫행:w.first, 끝행:w.last,
     프리셋:w.presets, 합계:w.exec});
  P(R.snap, '주 라벨 = 월요일 ~ 일요일 · 기준일에서 끊긴 마지막 주는 기준일까지',
    {pass: w.first === '2026-08-03 ~ 08-09' && w.last === '2026-08-24 ~ 08-27',
     첫행:w.first, 끝행:w.last});

  await setDate('to', '2026-08-25'); let w2 = await S();
  P(R.snap, '주별 종료일에 2026-08-25(화) → 그 주 일요일(08-30)이 아니라 기준일 08-27 로 스냅',
    {pass: w2.to === BASE, 넣은값:'2026-08-25', 결과:w2.to, 기간:w2.from + '~' + w2.to, 행:w2.rows});
  await setDate('from', '2026-08-25'); let w3 = await S();
  P(R.snap, '주별 시작일에 2026-08-25(화) → 그 주 월요일 2026-08-24 로 스냅 · 한 주 1행',
    {pass: w3.from === '2026-08-24' && w3.rows === 1 && w3.last === '2026-08-24 ~ 08-27',
     넣은값:'2026-08-25', 결과:w3.from, 기간:w3.from + '~' + w3.to, 행:w3.rows, 끝행:w3.last, 합계:w3.exec});

  await home(); await gran('monthly'); let m = await S();
  P(R.snap, '일별 일주일 → 월별 전환 시 3개월 프리셋 06-01~08-27 · 3행',
    {pass: m.from === '2026-06-01' && m.to === BASE && m.rows === 3
           && m.title === '월별 투자수익' && m.col === '정산예정월' && m.first === '2026-06'
           && m.presets.join('·') === '3개월*·6개월',
     기간:m.from + '~' + m.to, 행:m.rows, 첫행:m.first, 표제목:m.title, 열:m.col,
     프리셋:m.presets, 합계:m.exec});
  await setDate('from', '2026-08-14'); let m2 = await S();
  P(R.snap, '월별 시작일에 2026-08-14 → 그 달 1일 2026-08-01 로 스냅',
    {pass: m2.from === '2026-08-01', 넣은값:'2026-08-14', 결과:m2.from, 기간:m2.from + '~' + m2.to, 행:m2.rows});
  await setDate('from', '2026-06-14'); let m3 = await S();
  P(R.snap, '월별 시작일에 2026-06-14 → 2026-06-01 · 3행 (06·07·08)',
    {pass: m3.from === '2026-06-01' && m3.rows === 3 && m3.first === '2026-06' && m3.last === '2026-08',
     기간:m3.from + '~' + m3.to, 행:m3.rows, 첫행:m3.first, 끝행:m3.last, 합계:m3.exec});

  /* ══ 5) 프리셋을 보고 있으면 단위를 바꿔도 프리셋 자리가 이어진다 ══
     금월은 일별 묶음의 긴 쪽이라 월별에서는 6개월, 주별에서는 12주가 켜진다.
     되돌아오면 처음 그 프리셋으로 돌아온다 — 08-31 같은 기준일 뒤 날짜가 남지 않는다. */
  await home(); await preset('month'); const dm = await S();
  await gran('monthly'); const mm = await S();
  await gran('daily');   const back = await S();
  P(R.link, '금월 → 월별 전환 시 같은 자리(긴 쪽) 프리셋 6개월 03-01~08-27',
    {pass: mm.from === '2026-03-01' && mm.to === BASE && mm.rows === FACTS.monthExec.length
           && mm.label === '6개월' && mm.presets.join('·') === '3개월·6개월*',
     일별:dm.from + '~' + dm.to + ' ' + dm.rows + '행 ' + dm.exec,
     월별:mm.from + '~' + mm.to + ' ' + mm.rows + '행 ' + mm.exec, 프리셋:mm.presets});
  P(R.link, '월별 → 일별 복귀 시 금월 프리셋으로 되돌아온다(08-31 이 남지 않는다)',
    {pass: back.from === '2026-08-01' && back.to === BASE && back.rows === 27
           && back.exec === dm.exec && back.label === '금월',
     기간:back.from + '~' + back.to, 행:back.rows, 합계:back.exec, 라벨:back.label});

  /* 직접 고른 기간은 단위를 바꿔도 지워지지 않는다 — 두 축이 서로를 지우지 않는 자리.
     2026-06-01 은 월요일이자 그 달 1일이라 세 단위의 스냅을 모두 통과해 기간이 그대로 남는다. */
  await home();
  await setDate('from', '2026-06-01'); await setDate('to', BASE);
  const gcd = await S();
  await gran('weekly');  const gcw = await S();
  await gran('monthly'); const gcm = await S();
  P(R.link, '직접 고른 06-01~08-27 은 단위를 바꿔도 그대로 · 합계가 셋 다 같다',
    {pass: gcd.exec === gcw.exec && gcw.exec === gcm.exec
           && gcd.from === '2026-06-01' && gcw.from === '2026-06-01' && gcm.from === '2026-06-01'
           && gcd.to === BASE && gcw.to === BASE && gcm.to === BASE
           && gcd.label === '직접입력' && gcw.label === '직접입력' && gcm.label === '3개월'
           && gcm.rows === 3,
     일별:gcd.from + '~' + gcd.to + ' ' + gcd.rows + '행 ' + gcd.exec,
     주별:gcw.from + '~' + gcw.to + ' ' + gcw.rows + '행 ' + gcw.exec,
     월별:gcm.from + '~' + gcm.to + ' ' + gcm.rows + '행 ' + gcm.exec});

  /* 6개월 프리셋은 원장 전체를 덮는다 */
  await home(); await gran('monthly'); await preset('m6'); const g6m = await S();
  P(R.link, '6개월 프리셋 = 원장 전체 ' + FACTS.monthExec.length + '행',
    {pass: g6m.rows === FACTS.monthExec.length
           && g6m.exec === FACTS.monthExec.reduce((a, x) => a + x[1], 0).toLocaleString('en-US'),
     월별:g6m.rows + '행 ' + g6m.exec});

  /* ══ 6) 프리셋 묶음이 단위를 따라 갈린다 ══ */
  await home(); const pd = await S();
  await gran('weekly');  const pw = await S();
  await gran('monthly'); const pm = await S();
  P(R.link, '프리셋 묶음 — 일별 일주일·금월 / 주별 4주·12주 / 월별 3개월·6개월',
    {pass: pd.presets.join('·') === '일주일*·금월' && pw.presets.join('·') === '4주*·12주'
           && pm.presets.join('·') === '3개월*·6개월',
     일별:pd.presets, 주별:pw.presets, 월별:pm.presets});
  await home(); await gran('weekly'); await preset('w4'); const pw4 = await S();
  P(R.link, '주별 4주 프리셋 → 08-03~08-27 · 4행 · 그 버튼만 활성',
    {pass: pw4.from === '2026-08-03' && pw4.to === BASE && pw4.rows === 4
           && pw4.presets.join('·') === '4주*·12주' && pw4.label === '4주',
     기간:pw4.from + '~' + pw4.to, 행:pw4.rows, 프리셋:pw4.presets, 합계:pw4.exec});
  await preset('w12'); const pw12 = await S();
  P(R.link, '주별 12주 프리셋 → 06-08~08-27 · 12행',
    {pass: pw12.from === '2026-06-08' && pw12.to === BASE && pw12.rows === 12
           && pw12.presets.join('·') === '4주·12주*',
     기간:pw12.from + '~' + pw12.to, 행:pw12.rows, 합계:pw12.exec});
  await home(); await gran('monthly'); await preset('m3'); const pm3 = await S();
  P(R.link, '월별 3개월 프리셋 → 06-01~08-27 · 3행',
    {pass: pm3.from === '2026-06-01' && pm3.to === BASE && pm3.rows === 3
           && pm3.presets.join('·') === '3개월*·6개월',
     기간:pm3.from + '~' + pm3.to, 행:pm3.rows, 합계:pm3.exec});
  /* 직접 고른 기간에서 단위를 바꾸면 새 묶음 중 일치하는 것이 없어 직접입력으로 남는다 */
  await home(); await setDate('from', '2026-08-10'); await gran('weekly'); const keep = await S();
  P(R.link, '직접 고른 기간에서 단위를 바꾸면 기간 유지 · 일치하는 프리셋이 없으면 직접입력',
    {pass: keep.from === '2026-08-10' && keep.to === BASE
           && keep.presets.join('·') === '4주·12주' && keep.label === '직접입력',
     기간:keep.from + '~' + keep.to, 프리셋:keep.presets, 라벨:keep.label});

  /* ══ 7) 어느 단위에서도 피커가 살아 있다 — 이번 결함의 핵심 ══ */
  for(const g of ['daily', 'weekly', 'monthly']){
    await home(); await gran(g);
    const before = await S();
    await setDate('from', '2026-05-14');
    const after = await S();
    const want = g === 'daily' ? '2026-05-14' : (g === 'weekly' ? '2026-05-11' : '2026-05-01');
    P(R.alive, GRAN_LABEL(g) + ' — 피커 살아 있음(잠금 0) · 값이 바뀌고 표가 다시 그려진다',
      {pass: after.alive && after.clamp.every(v => v === null) && after.from === want
             && after.rows !== before.rows && after.exec !== before.exec,
       잠금:after.clamp, 살아있음:after.alive, 넣은값:'2026-05-14', 결과:after.from,
       행:before.rows + ' → ' + after.rows, 합계:before.exec + ' → ' + after.exec});
  }
  /* 역전 범위는 달력을 잠그는 대신 안내문 + 조회 버튼 비활성으로 막는다 */
  await home(); await setDate('from', '2026-09-30'); const bad = await S();
  P(R.alive, '역전 범위 — 안내문 표시 · 검색 버튼 비활성 · 달력은 그대로 열림',
    {pass: bad.warn && bad.goDisabled && bad.alive && bad.clamp.every(v => v === null),
     안내문:bad.warn, 검색비활성:bad.goDisabled, 잠금:bad.clamp});

  /* ══ 7-2) 날짜 칸은 어디를 눌러도 달력이 뜬다 ══ */
  /* 숫자 부분(칸 왼쪽)을 진짜 마우스로 눌러 showPicker 가 나가는지 본다.
     네이티브 달력 아이콘은 칸 오른쪽 끝에 있으므로 왼쪽 20px 은 확실히 숫자 자리다. */
  await home(); await armPicker();
  for(const which of ['from', 'to']){
    const b = await fieldBox(which);
    await realClick(b.left + 20, b.top + Math.round(b.h / 2));
    await sleep(200);
    const got = await pickedList();
    const after = await S();
    P(R.picker, 'pf-' + which + ' 숫자 자리를 눌러도 달력 호출이 나간다',
      {pass: got.indexOf('pf-' + which) >= 0 && after.alive,
       누른자리:'왼쪽 20px (아이콘 아님)', 칸너비:b.w, showPicker호출:got, 피커살아있음:after.alive});
    await ev('window.__pick = []; return 1;');
  }
  const wired = await ev(`
    var sec = document.querySelector('section[data-screen="invest-profit"]');
    return {act: [].map.call(sec.querySelectorAll('[data-act="pf-date"]'), function(e){ return e.dataset.which; }),
            hasAct: typeof ACT['pf-date'] === 'function',
            keepDefault: KEEP_DEFAULT.indexOf('pf-date') >= 0};`);
  P(R.picker, '두 칸 모두 배선 · 기본 동작 유지(preventDefault 제외)',
    {pass: wired.act.join(',') === 'from,to' && wired.hasAct && wired.keepDefault,
     배선:wired.act, 핸들러:wired.hasAct, 기본동작유지:wired.keepDefault});

  /* ══ 7-3) 사용자 지적 — 시작일만 만진 뒤 프리셋을 누르면 둘 다 덮어쓴다 ══ */
  await home(); const p0 = await S();
  await setDate('from', '2026-08-24'); const p1 = await S();
  P(R.link, '시작일만 바꾸면 종료일은 그대로 남고 표가 다시 그려진다',
    {pass: p1.from === '2026-08-24' && p1.to === p0.to && p1.rows === 4 && p1.exec !== p0.exec,
     기간:p0.from + '~' + p0.to + ' → ' + p1.from + '~' + p1.to,
     행:p0.rows + ' → ' + p1.rows, 합계:p0.exec + ' → ' + p1.exec});
  await preset('week'); const p2 = await S();
  P(R.link, '그 뒤 일주일 프리셋 → 시작·종료를 둘 다 덮어쓴다(종료일만 남지 않는다)',
    {pass: p2.from === '2026-08-21' && p2.to === '2026-08-27' && p2.rows === 7
           && p2.exec === WEEK_EXEC && p2.presets.join('·') === '일주일*·금월',
     기간:p1.from + '~' + p1.to + ' → ' + p2.from + '~' + p2.to,
     행:p1.rows + ' → ' + p2.rows, 합계:p1.exec + ' → ' + p2.exec, 프리셋:p2.presets});
  await setDate('to', '2026-08-24'); await preset('month'); const p3 = await S();
  P(R.link, '종료일만 만진 뒤 금월 프리셋 → 역시 둘 다 덮어쓴다',
    {pass: p3.from === '2026-08-01' && p3.to === '2026-08-27' && p3.rows === 27 && p3.label === '금월',
     기간:p3.from + '~' + p3.to, 행:p3.rows, 합계:p3.exec, 라벨:p3.label});

  /* ══ 8) 초기화 ══ */
  await home(); await gran('monthly'); await preset('m3');
  await ev(`document.querySelector('section[data-screen="invest-profit"] [data-act="pf-reset"]').click(); return 1;`);
  const rs = await S();
  P(R.reset, '초기화 → 일별 + 일주일 프리셋 + 08-21~08-27 · ' + FACTS.weekDays + '행 · ' + WEEK_EXEC,
    {pass: rs.gran[0] === '일별*' && rs.presets.join('·') === '일주일*·금월'
           && rs.from === '2026-08-21' && rs.to === '2026-08-27' && rs.rows === 7
           && rs.exec === WEEK_EXEC && rs.state === 'default',
     단위:rs.gran, 프리셋:rs.presets, 기간:rs.from + '~' + rs.to, 행:rs.rows, 합계:rs.exec, 상태:rs.state});

  /* ══ 9) 정적 낱장 4종이 같은 상태를 그리는가 ══ */
  const D3 = '일별*·주별·월별', W3 = '일별·주별*·월별', M3 = '일별·주별·월별*';
  /* 엑셀 2건 = [현황 카드, 표]. 카드가 4주를 말하는데 링크가 일주일 파일이면 여기서 걸린다.
     결과 없음 낱장은 두 버튼이 모두 disabled 라 링크가 없다. */
  const XW = ['assets/xlsx/투자수익현황_2026-08-21_2026-08-27.xlsx', 'assets/xlsx/일별투자수익_2026-08-21_2026-08-27.xlsx'];
  const STATIC = [
    ['invest-profit.html',             '일주일*·금월', D3, '2026-08-21', '2026-08-27', 7, '일별 투자수익', '정산예정일', XW],
    ['invest-profit--weekly.html',     '4주*·12주',    W3, '2026-08-03', BASE, 4, '주별 투자수익', '정산예정주',
     ['assets/xlsx/투자수익현황_2026-08-03_2026-08-27.xlsx', 'assets/xlsx/주별투자수익_2026-08-03_2026-08-27.xlsx']],
    ['invest-profit--monthly.html',    '3개월·6개월*', M3, '2026-03-01', BASE, 6, '월별 투자수익', '정산예정월',
     ['assets/xlsx/투자수익현황_2026-03-01_2026-08-27.xlsx', 'assets/xlsx/월별투자수익_2026-03-01_2026-08-27.xlsx']],
    ['invest-profit--empty.html',      '일주일·금월',  D3, '2026-02-01', '2026-02-07', 0, '일별 투자수익', '정산예정일', []]
  ];
  for(const [f, pre, gr, frm, to, rows, title, col, xls] of STATIC){
    await send('Page.navigate', {url:'http://127.0.0.1:' + PORT + '/' + f}); await sleep(600);
    const st = await ev(`
      var main = document.querySelector('main.content');
      var ins = main.querySelectorAll('.filter-row input[type=date]');
      var order = [].map.call(main.querySelectorAll('.search-bar > div'), function(d){ return d.className; });
      return {presets: [].map.call(main.querySelectorAll('.preset-btn'), function(b){
                return b.textContent.trim() + (b.classList.contains('active') ? '*' : ''); }).join('·'),
              gran: [].map.call(main.querySelectorAll('.toggle-btn'), function(b){
                return b.textContent.trim() + (b.classList.contains('active') ? '*' : ''); }),
              from: ins[0] ? ins[0].value : null, to: ins[1] ? ins[1].value : null,
              /* 낱장 빈 상태는 자리표시 행 한 줄(td.empty)로 그린다 — 데이터 행만 센다 */
              rows: [].filter.call(main.querySelectorAll('.tbl tbody tr'),
                                   function(tr){ return !tr.querySelector('td.empty'); }).length,
              placeholder: !!main.querySelector('.tbl tbody td.empty'),
              title: (main.querySelectorAll('.card-title')[1] || {}).textContent,
              col: main.querySelector('.tbl th') ? main.querySelector('.tbl th').textContent.trim() : null,
              xls: [].map.call(main.querySelectorAll('a[download]'), function(a){ return a.getAttribute('href'); }),
              order: order};`);
    P(R.reset, '정적 ' + f + ' — 통합본 같은 상태와 일치',
      {pass: st.presets === pre && st.gran.length === 3 && st.gran.join('·') === gr
             && st.from === frm && st.to === to && st.rows === rows
             && st.title === title && st.col === col
             && st.xls.join('|') === xls.join('|')
             && st.order[0] === 'preset-row' && st.order[1] === 'filter-row',
       프리셋:st.presets, 단위:st.gran, 기간:st.from + '~' + st.to, 행:st.rows,
       자리표시행:st.placeholder, 표제목:st.title, 열:st.col, 엑셀:st.xls, 줄순서:st.order});
  }

  /* ══ 9-2) 엑셀 미리보기 화면이 지금 보고 있는 집계 단위의 파일을 말하는가 ══
     파일바 이름 · 내려받기 링크 · 시트 머리글 · 검색대상기간 줄이 한 기간을 말해야 한다. */
  await send('Page.navigate', {url:'http://127.0.0.1:' + PORT + '/app.html'}); await sleep(1200);
  const PREV = [
    ['daily',   'default', '투자수익현황_2026-08-21_2026-08-27.xlsx', '일별투자수익_2026-08-21_2026-08-27.xlsx',
     '일주일 (2026-08-21 ~ 2026-08-27)', '일별 투자수익'],
    ['weekly',  'weekly',  '투자수익현황_2026-08-03_2026-08-27.xlsx', '주별투자수익_2026-08-03_2026-08-27.xlsx',
     '4주 (2026-08-03 ~ 2026-08-27)', '주별 투자수익'],
    ['monthly', 'monthly', '투자수익현황_2026-03-01_2026-08-27.xlsx', '월별투자수익_2026-03-01_2026-08-27.xlsx',
     '6개월 (2026-03-01 ~ 2026-08-27)', '월별 투자수익']
  ];
  for(const [g, state, fs_, fd, period, dtitle] of PREV){
    const pv = await ev(`
      go('invest-profit', ${JSON.stringify(state)});
      function read(scr){
        go(scr, 'default');
        var sec = document.querySelector('section.screen[data-screen="' + scr + '"]');
        var rows = sec.querySelectorAll('tbody tr');
        return {name: sec.querySelector('.fb-name').textContent,
                href: decodeURIComponent(sec.querySelector('a[download]').getAttribute('href')),
                title: sec.querySelector('.c-title').textContent,
                r4: rows[3] ? rows[3].textContent : ''};
      }
      return {gran: PF.gran, status: read('xls-profit-status'), daily: read('xls-profit-daily')};`);
    P(R.link, '엑셀 미리보기 ' + GRAN_LABEL(g) + ' — 파일바·링크·시트가 한 기간을 말한다',
      {pass: pv.gran === g
             && pv.status.name === fs_ && pv.status.href === 'assets/xlsx/' + fs_
             && pv.status.r4.indexOf(period) >= 0
             && pv.daily.name === fd && pv.daily.href === 'assets/xlsx/' + fd
             && pv.daily.title.indexOf(dtitle) === 0,
       단위:pv.gran, 현황:pv.status.name, 현황링크:pv.status.href, 검색대상기간:pv.status.r4,
       표:pv.daily.name, 표제목:pv.daily.title});
  }

  /* ══ 9-3) 프리셋 밖 기간 — 실물이 없으므로 잠근다 ══
     프리셋 6조합에만 실물 파일이 있다. 직접입력 기간에서 버튼이 살아 있으면 화면이 없는 파일을 말하게 된다.
     잠금 규격은 원본 어드민 그대로 disabled 속성 + 회색 + cursor:not-allowed 다. */
  {
    const off = await ev(`
      go('invest-profit','default');
      var sec = document.querySelector('section[data-screen="invest-profit"]');
      var ti = sec.querySelector('[data-mount="pf-to"]');
      ti.value = '2026-08-25'; ti.dispatchEvent(new Event('change', {bubbles:true}));
      var x1 = sec.querySelector('[data-mount="pf-xls1"]'), x2 = sec.querySelector('[data-mount="pf-xls2"]');
      var cs = getComputedStyle(x1);
      function prev(scr){
        go(scr, 'default');
        var p = document.querySelector('section.screen[data-screen="' + scr + '"]');
        var b = p.querySelector('.file-bar .btn');
        return {name: p.querySelector('.fb-name').textContent,
                off: p.querySelector('.file-bar').classList.contains('is-off'),
                tag: b.tagName, disabled: !!b.disabled,
                links: p.querySelectorAll('.file-bar a[download]').length,
                tab: p.querySelector('.sheet-tab').textContent};
      }
      return {label:(sec.querySelector('.stat-period') || {}).textContent,
              keys:[xlsKey('profit-status'), xlsKey('profit-daily')],
              lock:[!!x1.disabled, !!x2.disabled], cursor:cs.cursor,
              status:prev('xls-profit-status'), daily:prev('xls-profit-daily')};`);
    P(R.link, '직접입력 기간 — 엑셀 두 버튼 잠금 · 미리보기 파일바 회색 · 내려받기 링크 0',
      {pass: off.label === '직접입력' && off.keys[0] === null && off.keys[1] === null
             && off.lock[0] && off.lock[1] && off.cursor === 'not-allowed'
             && off.status.off && off.daily.off
             && off.status.name === '-' && off.daily.name === '-'
             && off.status.tag === 'BUTTON' && off.daily.tag === 'BUTTON'
             && off.status.disabled && off.daily.disabled
             && off.status.links === 0 && off.daily.links === 0
             && off.daily.tab === '일별 투자수익',
       라벨:off.label, 열쇠:off.keys, 잠금:off.lock, cursor:off.cursor,
       현황파일바:off.status, 표파일바:off.daily});
  }

  /* ══ 출력 ══ */
  const lines = [];
  const dump = (n, arr) => { lines.push('== ' + n + ' =='); arr.forEach(x =>
    lines.push('  ' + (x.pass ? 'PASS ' : 'FAIL ') + x.t + '  ' + JSON.stringify(x))); };
  dump('불변식', R.invariant); dump('스냅', R.snap); dump('두 축 연동', R.link);
  dump('피커 생존', R.alive); dump('달력 열림', R.picker); dump('초기화·정적 대조', R.reset);
  const all = R.invariant.concat(R.snap, R.link, R.alive, R.picker, R.reset);
  const fail = all.filter(x => !x.pass);
  /* 뷰포트를 재 놓고 판정에 안 넣던 자리(2026-08-30 이전).
     이 파일 17행이 스스로 VIEW_H = 1200 · WIN_H = VIEW_H + 87 로 macOS 함정 보정을 선언한다 —
     보정이 풀리면 실제 뷰포트가 1113 이 되고, 기간 피커·달력의 높이 판정이 조용히 다른 조건에서 돈다.
     기준은 이 파일이 이미 적어 둔 값이다. 새로 정하지 않는다. */
  R.viewport = {want: [1440, VIEW_H], got: vp,
                pass: vp[0] === 1440 && vp[1] === VIEW_H};
  lines.push('== 뷰포트 == ' + (R.viewport.pass ? 'PASS ' : 'FAIL ') + vp.join('x') +
             ' (창 1440x' + WIN_H + ' · 기대 1440x' + VIEW_H + ')');
  lines.push('== 콘솔 에러 == ' + cons.length); cons.slice(0, 10).forEach(c => lines.push('  - ' + c));
  lines.push('== 합계 == ' + all.length + '건 · PASS ' + (all.length - fail.length) + ' · FAIL ' + fail.length);
  console.log(lines.join('\n'));
  fs.writeFileSync(OUT, JSON.stringify(R, null, 1));
  /* 콘솔 에러·뷰포트를 종료코드에 넣는다 — 형제 검증기(verify_rows.js:213 · verify_toast.js:229)와 같은 방식. */
  ws.close(); ch.kill(); server.close();
  process.exit(fail.length || cons.length || !R.viewport.pass ? 1 : 0);
}
function GRAN_LABEL(g){ return g === 'daily' ? '일별' : (g === 'weekly' ? '주별' : '월별'); }
main().catch(e => { console.error('VERIFY ERROR', e); process.exit(1); });
