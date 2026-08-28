/* feasibility.html 헤드리스 검증 — 창을 띄우지 않는다(--headless=new).
   1) 콘솔 에러·경고 0  2) 페이지 가로 오버플로 0 (4개 폭)  3) 등급 필터 토글  4) 검색
   5) 복사 텍스트 생성  6) 순서도 SVG 렌더  7) 표는 .scroll 안에 있는가                */
const http = require('http');
const fs   = require('fs');
const path = require('path');
const os   = require('os');
const { spawn } = require('child_process');

const REPO = '/Users/semi/cursor/payhug-investor-admin';
const PORT = 8800 + (process.pid % 90), DPORT = 9500 + (process.pid % 90);
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const MIME = {'.html':'text/html; charset=utf-8', '.css':'text/css; charset=utf-8',
  '.js':'text/javascript', '.png':'image/png', '.svg':'image/svg+xml', '.ico':'image/x-icon'};

const server = http.createServer((req, res) => {
  const url = decodeURIComponent(req.url.split('?')[0]);
  if (url === '/favicon.ico') {   /* 브라우저 기본 요청 — 404 로그를 남기지 않게 빈 응답 */
    res.writeHead(200, {'Content-Type': 'image/x-icon'}); res.end(Buffer.alloc(0)); return;
  }
  const p = path.join(REPO, url);
  fs.readFile(p, (e, b) => {
    if (e) { res.writeHead(404); res.end('nope'); return; }
    res.writeHead(200, {'Content-Type': MIME[path.extname(p)] || 'application/octet-stream'});
    res.end(b);
  });
});

let msgId = 0, ws, pending = new Map();
const consoleErrors = [];
function send(method, params) {
  const id = ++msgId;
  ws.send(JSON.stringify({id, method, params: params || {}}));
  return new Promise((res) => pending.set(id, {res}));
}
async function evalJS(expr) {
  const r = await send('Runtime.evaluate',
    {expression: '(function(){' + expr + '})()', returnByValue: true, awaitPromise: true});
  if (r.exceptionDetails) throw new Error('page eval: ' + JSON.stringify(
    (r.exceptionDetails.exception && r.exceptionDetails.exception.description) || r.exceptionDetails.text));
  return r.result.value;
}
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function main() {
  await new Promise(r => server.listen(PORT, r));
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'phfeas-'));
  const chrome = spawn(CHROME, ['--headless=new', '--remote-debugging-port=' + DPORT,
    '--user-data-dir=' + profile, '--no-first-run', '--no-default-browser-check',
    '--disable-gpu', '--window-size=1440,1200', 'about:blank'], {stdio: 'ignore'});

  let targets = null;
  for (let i = 0; i < 60 && !targets; i++) {
    await sleep(300);
    try {
      targets = await new Promise((res, rej) => {
        http.get({host: '127.0.0.1', port: DPORT, path: '/json'}, r => {
          let d = ''; r.on('data', c => d += c); r.on('end', () => res(JSON.parse(d)));
        }).on('error', rej);
      });
    } catch (e) { targets = null; }
  }
  const page = targets.find(t => t.type === 'page');
  ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise(r => ws.addEventListener('open', r));
  ws.addEventListener('message', ev => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { pending.get(m.id).res(m.result); pending.delete(m.id); return; }
    if (m.method === 'Runtime.consoleAPICalled' && (m.params.type === 'error' || m.params.type === 'warning'))
      consoleErrors.push(m.params.type + ': ' + m.params.args.map(a => a.value || a.description || a.type).join(' '));
    if (m.method === 'Runtime.exceptionThrown')
      consoleErrors.push('exception: ' + ((m.params.exceptionDetails.exception &&
        m.params.exceptionDetails.exception.description) || m.params.exceptionDetails.text));
    if (m.method === 'Log.entryAdded' && m.params.entry.level === 'error')
      consoleErrors.push('log: ' + m.params.entry.text + ' ' + (m.params.entry.url || ''));
  });
  await send('Runtime.enable'); await send('Log.enable'); await send('Page.enable');
  await send('Browser.grantPermissions', {origin: 'http://127.0.0.1:' + PORT,
    permissions: ['clipboardReadWrite', 'clipboardSanitizedWrite']});

  await send('Page.navigate', {url: 'http://127.0.0.1:' + PORT + '/feasibility.html'});
  await sleep(1600);

  const R = {overflow: [], counts: null, filter: null, search: null, copy: null, svg: null, tables: null, console: []};

  /* 1) 항목 수·등급 분포 */
  R.counts = await evalJS(
    'var rows=[].slice.call(document.querySelectorAll("tbody[id^=\'tb-\'] tr[data-g]"));' +
    'var by={};rows.forEach(function(r){var g=r.getAttribute("data-g");by[g]=(by[g]||0)+1;});' +
    'var per={};[].forEach.call(document.querySelectorAll("tbody[id^=\'tb-\']"),function(tb){' +
    '  per[tb.id]=tb.querySelectorAll("tr[data-g]").length;});' +
    'return {total:rows.length, by:by, per:per, badge:document.getElementById("cnt").textContent};');

  /* 2) 가로 오버플로 — 4개 폭 */
  for (const [w, h] of [[1440, 1200], [1180, 1000], [900, 1000], [390, 844]]) {
    await send('Emulation.setDeviceMetricsOverride',
      {width: w, height: h, deviceScaleFactor: 1, mobile: w < 500});
    await sleep(450);
    const o = await evalJS(
      'var de=document.documentElement, b=document.body;' +
      'var over=[];' +
      '[].forEach.call(document.body.querySelectorAll("*"),function(el){' +
      '  var r=el.getBoundingClientRect();' +
      '  if(r.width>0 && r.right > de.clientWidth + 1.5){' +
      '    var p=el; var inScroll=false;' +
      '    while(p && p!==document.body){ if(p.classList && p.classList.contains("scroll")){inScroll=true;break;} p=p.parentElement; }' +
      '    if(!inScroll) over.push(el.tagName.toLowerCase()+(el.className&&typeof el.className==="string"?"."+el.className.split(" ")[0]:"")+" right="+Math.round(r.right));' +
      '  }});' +
      'return {docScrollW:de.scrollWidth, clientW:de.clientWidth, bodyScrollW:b.scrollWidth,' +
      ' pageOverflow: de.scrollWidth > de.clientWidth + 1, offenders: over.slice(0,8)};');
    R.overflow.push({width: w, ...o});
  }
  await send('Emulation.setDeviceMetricsOverride', {width: 1440, height: 1200, deviceScaleFactor: 1, mobile: false});
  await sleep(300);

  /* 3) 표가 .scroll 안에 있는가 */
  R.tables = await evalJS(
    'var t=[].slice.call(document.querySelectorAll("table.dt, table.mini"));' +
    'var bad=t.filter(function(x){return !x.closest(".scroll");}).length;' +
    'return {tables:t.length, notInScroll:bad};');

  /* 4) 등급 필터 토글 — A 끄면 A행이 사라지는가 */
  R.filter = await evalJS(
    'function shown(){return document.querySelectorAll("tbody[id^=\'tb-\'] tr[data-g]:not(.hit-off)").length;}' +
    'var before=shown();' +
    'var a=document.querySelector("#chips .chip[data-g=\'A\']"); a.click();' +
    'var afterA=shown();' +
    'var e=document.querySelector("#chips .chip[data-g=\'E\']"); e.click();' +
    'var afterE=shown();' +
    'a.click(); e.click();' +
    'var restored=shown();' +
    'return {before:before, afterOffA:afterA, afterOffAE:afterE, restored:restored,' +
    ' aPressed:a.getAttribute("aria-pressed"), badge:document.getElementById("cnt").textContent};');

  /* 5) 검색 */
  R.search = await evalJS(
    'var q=document.getElementById("q"); q.value="쿠콘";' +
    'q.dispatchEvent(new Event("input"));' +
    'var hit=document.querySelectorAll("tbody[id^=\'tb-\'] tr[data-g]:not(.hit-off)").length;' +
    'q.value="zzz없는말zzz"; q.dispatchEvent(new Event("input"));' +
    'var zero=document.querySelectorAll("tbody[id^=\'tb-\'] tr[data-g]:not(.hit-off)").length;' +
    'var msg=document.getElementById("noHit").classList.contains("on");' +
    'q.value=""; q.dispatchEvent(new Event("input"));' +
    'var back=document.querySelectorAll("tbody[id^=\'tb-\'] tr[data-g]:not(.hit-off)").length;' +
    'return {coocon:hit, none:zero, emptyMsgShown:msg, restored:back};');

  /* 6) 복사 텍스트 생성 (클릭 대신 동일 로직 재현) */
  R.copy = await evalJS(
    'var qbox=document.getElementById("qbox");' +
    'var ids=[].map.call(qbox.querySelectorAll(".qlist .qid"),function(x){return x.textContent.trim();});' +
    'var grps=qbox.querySelectorAll(".qgrp").length;' +
    'var uniq={}; ids.forEach(function(i){uniq[i]=1;});' +
    'return {questions:ids.length, unique:Object.keys(uniq).length, groups:grps, first:ids[0], last:ids[ids.length-1]};');

  /* 7) 순서도 SVG */
  R.svg = await evalJS(
    'var s=document.querySelector(".flow-wrap svg");' +
    'if(!s) return {found:false};' +
    'var r=s.getBoundingClientRect();' +
    'return {found:true, w:Math.round(r.width), h:Math.round(r.height),' +
    ' rects:s.querySelectorAll("rect").length, texts:s.querySelectorAll("text").length,' +
    ' arrows:s.querySelectorAll("path[marker-end]").length};');

  /* 8) 복사 버튼 클릭 — 헤드리스는 문서 포커스가 없어 클립보드 쓰기가 막힌다. 포커스를 강제한 뒤 실제로 써 본다 */
  await send('Emulation.setFocusEmulationEnabled', {enabled: true});
  await send('Page.bringToFront');
  await sleep(200);
  await evalJS('document.getElementById("copyAll").click(); return 1;');
  await sleep(900);
  R.copyClickLabel = await evalJS('return document.getElementById("copyLabel").textContent;');
  R.clipboard = await evalJS(
    'if(!navigator.clipboard || !navigator.clipboard.readText) return {read:false};' +
    'return navigator.clipboard.readText().then(function(t){' +
    '  return {read:true, len:t.length, head:t.split("\\n")[0], hasD01:t.indexOf("D-01")!==-1, hasD32:t.indexOf("D-32")!==-1,' +
    '          lines:t.split("\\n").length};' +
    '})["catch"](function(e){ return {read:false, err:String(e).slice(0,80)}; });');

  R.console = consoleErrors;

  fs.writeFileSync(path.join(__dirname, 'verify_feasibility_result.json'), JSON.stringify(R, null, 2));

  /* ── 판정 ── */
  const fails = [];
  /* 판정 대상 수는 실측을 따른다 — counts.json 이 세는 상태 파일 수와 5-3 표 행 수가 같아야 하고,
     5-2 화면 표는 낱장 화면 + 랜딩 갤러리 1 이다. 검증기에 총계를 손으로 박지 않는다(D-38). */
  const CNT = JSON.parse(fs.readFileSync(path.join(__dirname, 'counts.json'), 'utf8'));
  const wantState = CNT.states;
  const wantScreen = CNT.screens - 1 + 1;                 // 통합본 제외 낱장 + 랜딩 갤러리
  if (R.counts.per['tb-state'] !== wantState)
    fails.push('상태 행 ' + R.counts.per['tb-state'] + ' ≠ 실측 ' + wantState);
  if (R.counts.per['tb-screen'] !== wantScreen)
    fails.push('화면 행 ' + R.counts.per['tb-screen'] + ' ≠ 실측 ' + wantScreen);
  const sum = Object.values(R.counts.per).reduce((a, b) => a + b, 0);
  if (R.counts.total !== sum) fails.push('항목 수 ' + R.counts.total + ' ≠ 구획 합 ' + sum);
  if (R.counts.badge.replace(/\s/g, '') !== sum + '/' + sum + '건')
    fails.push('표시 건수 ' + R.counts.badge + ' ≠ ' + sum);
  const gradeSum = Object.values(R.counts.by).reduce((a, b) => a + b, 0);
  if (gradeSum !== R.counts.total) fails.push('등급 합 ' + gradeSum + ' ≠ ' + R.counts.total);
  if ((R.counts.by.E || 0) !== 0) fails.push('등급 E ' + R.counts.by.E + ' ≠ 0');
  R.overflow.forEach(o => { if (o.pageOverflow) fails.push('가로 오버플로 @' + o.width + 'px — ' + JSON.stringify(o.offenders)); });
  if (R.tables.notInScroll !== 0) fails.push('.scroll 밖 표 ' + R.tables.notInScroll + '건');
  if (R.filter.afterOffA >= R.filter.before) fails.push('A 필터 미작동');
  if (R.filter.restored !== R.filter.before) fails.push('필터 복원 실패');
  if (R.search.none !== 0 || !R.search.emptyMsgShown) fails.push('검색 0건 처리 실패');
  if (R.search.restored !== R.counts.total) fails.push('검색 복원 실패');
  if (R.copy.questions !== 32 || R.copy.unique !== 32) fails.push('개발 문의 ' + R.copy.questions + '건(고유 ' + R.copy.unique + ') ≠ 32');
  if (!R.svg.found || R.svg.rects < 15) fails.push('순서도 SVG 이상');
  if (consoleErrors.length) fails.push('콘솔 ' + consoleErrors.length + '건: ' + consoleErrors.slice(0, 5).join(' | '));

  console.log('── feasibility.html 검증 ──');
  console.log('항목 ' + R.counts.total + '건 · 분포 ' + JSON.stringify(R.counts.by));
  console.log('섹션별 ' + JSON.stringify(R.counts.per));
  R.overflow.forEach(o => console.log('  폭 ' + o.width + 'px → scrollW ' + o.docScrollW + ' / clientW ' + o.clientW +
    ' · 오버플로 ' + (o.pageOverflow ? 'YES ' + JSON.stringify(o.offenders) : '0')));
  console.log('표 ' + R.tables.tables + '개 · .scroll 밖 ' + R.tables.notInScroll);
  console.log('필터 ' + JSON.stringify(R.filter));
  console.log('검색 ' + JSON.stringify(R.search));
  console.log('개발문의 ' + JSON.stringify(R.copy));
  console.log('순서도 ' + JSON.stringify(R.svg));
  console.log("복사 버튼 라벨 → " + R.copyClickLabel + " · 클립보드 " + JSON.stringify(R.clipboard));
  console.log('콘솔 ' + consoleErrors.length + '건' + (consoleErrors.length ? ': ' + consoleErrors.join(' | ') : ''));
  console.log(fails.length ? '\n판정: FAIL\n - ' + fails.join('\n - ') : '\n판정: PASS');

  try { chrome.kill(); } catch (e) {}
  server.close();
  process.exit(fails.length ? 1 : 0);
}

main().catch(e => { console.error('ERR', e); process.exit(2); });
