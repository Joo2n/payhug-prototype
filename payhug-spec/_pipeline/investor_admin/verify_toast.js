/* 토스트 대조 — app.html 이 `완료`라고 말할 때 실제로 파일이 나가는지 값으로 확인한다.
   창을 띄우지 않는다(--headless=new). 결과: verify_toast_result.json                    */
const http = require('http');
const fs   = require('fs');
const path = require('path');
const os   = require('os');
const { spawn } = require('child_process');

const REPO = '/Users/semi/cursor/payhug-investor-admin';
const OUTDIR = '/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin';
const PORT = 8600 + (process.pid % 90), DPORT = 9300 + (process.pid % 90);
const DL = fs.mkdtempSync(path.join(os.tmpdir(), 'phtoast-'));
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const MIME = {'.html':'text/html; charset=utf-8', '.css':'text/css; charset=utf-8', '.js':'text/javascript',
  '.png':'image/png', '.pdf':'application/pdf', '.zip':'application/zip',
  '.xlsx':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'};

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
const clearDL = () => fs.readdirSync(DL).forEach(f => { try{ fs.unlinkSync(path.join(DL, f)); }catch(e){} });
/* 계약기록 1쪽 행수 — 로스터 곳수와 보기 갯수 기본값(10) 중 작은 쪽. 검증기에 적지 않는다. */
const FACTS = JSON.parse(fs.readFileSync(path.join(__dirname, 'ledger_facts.json'), 'utf8'));
/* 계약기록에서 문서 버튼이 붙는 행 = 서명이 끝난 계약. 서명 대기 큐에 남은 가맹점은 문서가 없다.
   곳수는 화면이 세는 수를 받아 쓴다(아래 evalJS) — 여기 적어 두면 큐가 바뀔 때 낡는다. */
let CT_ROWS = 0;
/* 내려받기 폴더에 떨어진 것 중 `우리 자산`만 센다.
   헤드리스 크롬이 자기 부속 파일(downloads.html 등)을 같은 폴더에 쓸 때가 있어 그것까지 세면 판정이 흐려진다. */
const ASSETS = new Set(['assets/docs', 'assets/xlsx']
  .flatMap(d => fs.readdirSync(path.join(REPO, d)).map(f => f.normalize('NFC'))));
const assetLanded = () => fs.readdirSync(DL)
  .filter(f => !f.endsWith('.crdownload'))
  .filter(f => ASSETS.has(f.normalize('NFC').replace(/ \(\d+\)(?=\.[^.]+$)/, '')));

/* 토스트가 이름을 대는 파일이 assets 아래 실물로 있고, 받은 바이트가 그 크기와 같아야 한다 */
function landed(names){
  const out = [];
  for(const n of names){
    const got = path.join(DL, n);
    const src = ['assets/docs', 'assets/xlsx'].map(d => path.join(REPO, d, n)).find(fs.existsSync);
    out.push({name:n, saved: fs.existsSync(got), bytes: fs.existsSync(got) ? fs.statSync(got).size : 0,
              srcBytes: src ? fs.statSync(src).size : 0,
              ok: !!src && fs.existsSync(got) && fs.statSync(got).size === fs.statSync(src).size});
  }
  return out;
}

async function main(){
  await new Promise(r => server.listen(PORT, r));
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'phtprof-'));
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
  });
  await send('Runtime.enable'); await send('Page.enable');
  await send('Browser.setDownloadBehavior', {behavior:'allow', downloadPath: DL});
  await send('Page.navigate', {url:'http://127.0.0.1:' + PORT + '/app.html'});
  await sleep(1800);

  const R = {claims:[], cases:[], console:[]};

  /* ── 1) `완료`를 말하는 토스트 문구 전수 수집 ── */
  const src = fs.readFileSync(path.join(REPO, 'app.html'), 'utf8');
  R.claims = (src.match(/showToast\([^;]*?\)/g) || []).filter(s => /완료/.test(s));

  /* ── 2) 각 경로가 실제로 파일을 내보내는지 ── */
  const CASES = [
    {id:'xls-get assets-status',   act:'location.hash="#xls-assets-status"; return 1;',
     click:'[data-act="xls-get"][data-xls="assets-status"]',   want:['투자자산현황_2026-08-27_2026-08-27.xlsx']},
    {id:'xls-get assets-merchant', act:'location.hash="#xls-assets-merchant"; return 1;',
     click:'[data-act="xls-get"][data-xls="assets-merchant"]', want:['가맹점별투자자산_2026-08-27_2026-08-27.xlsx']},
    {id:'xls-get profit-status',   act:['go("invest-profit","default"); return 1;', 'location.hash="#xls-profit-status"; return 1;'],
     click:'[data-act="xls-get"][data-xls="profit-status"]',   want:['투자수익현황_2026-08-21_2026-08-27.xlsx']},
    {id:'xls-get profit-daily',    act:['go("invest-profit","default"); return 1;', 'location.hash="#xls-profit-daily"; return 1;'],
     click:'[data-act="xls-get"][data-xls="profit-daily"]',    want:['일별투자수익_2026-08-21_2026-08-27.xlsx']},
    /* 화면 버튼 → 중간 화면 없이 즉시 파일 (원본 ExcelDownloadButton 경로 대응) */
    {id:'xls-open 투자자산 현황 직행',   act:'go("invest-assets","default"); return 1;',
     click:'[data-act="xls-open"][data-xls="assets-status"]',   want:['투자자산현황_2026-08-27_2026-08-27.xlsx']},
    {id:'xls-open 가맹점별 투자자산 직행', act:'go("invest-assets","default"); return 1;',
     click:'[data-act="xls-open"][data-xls="assets-merchant"]', want:['가맹점별투자자산_2026-08-27_2026-08-27.xlsx']},
    {id:'cert-pdf 증명서 PDF',      act:'location.hash="#certificate"; return 1;',
     click:'[data-act="cert-pdf"]', want:['투자자산증명서_20260827.pdf']},
    {id:'상태 진입 #invest-assets/download', act:'location.hash="#contracts"; return 1;',
     hash:'#invest-assets/download', want:['가맹점별투자자산_2026-08-27_2026-08-27.xlsx']}
  ];

  /* 투자 수익은 프리셋 조합마다 자기 파일이다 — 화면이 가진 프리셋 표를 그대로 돌면서
     `지금 화면이 말하는 파일명`이 그 프리셋의 시작일·종료일을 달고 있는지, 그 실물이 나오는지 본다.
     기간을 검증기에 손으로 적으면 프리셋이 하나 늘 때마다 낡는다. */
  const PRESETS = await evalJS(`
    var out = [];
    for(var k in PRESET_RANGE)
      out.push({k:k, gran:PRESET_GRAN[k], label:PRESET_LABEL[k],
                from:PRESET_RANGE[k][0], to:PRESET_RANGE[k][1]});
    return out;`);
  /* 사람이 누르는 순서 그대로 한 번에 하나씩 누른다 — 화면을 세우고, 탭을 누르고, 칩을 누른다.
     한 틱에 몰아 누르면 해시 갱신이 겹쳐 마지막 해시가 상태를 다시 심는다(조작이 아니라 주소 복원). */
  const steps = pr => ['go("invest-profit","default"); return 1;',
                       `document.querySelector('[data-act=pf-gran][data-gran=${pr.gran}]').click(); return 1;`,
                       `document.querySelector('[data-act=preset][data-preset=${pr.k}]').click(); return 1;`];
  for(const pr of PRESETS){
    const act = steps(pr);
    for(const [key, kind] of [['profit-status', '수익 현황'], ['profit-daily', '투자수익 표']]){
      for(const one of act){ await evalJS(one); await sleep(120); }
      const want = await evalJS(`var k = xlsKey(${JSON.stringify(key)}); return k ? XLSX[k].file : null;`);
      const tail = '_' + pr.from + '_' + pr.to + '.xlsx';
      CASES.push({id:'xls-open ' + pr.label + ' ' + kind, act,
                  click:'[data-act="xls-open"][data-xls="' + key + '"]',
                  want:[want], periodOk: !!want && want.indexOf(tail) > 0});
    }
  }

  for(const c of CASES){
    clearDL();
    for(const one of [].concat(c.act)){ await evalJS(one); await sleep(120); }
    await sleep(300);
    let toast = null;
    if(c.hash){
      await evalJS('location.hash=' + JSON.stringify(c.hash) + '; return 1;');
    } else {
      const r = await evalJS('var e=document.querySelector(' + JSON.stringify(c.click) + ');' +
        'if(!e) return "missing"; e.click(); return "ok";');
      if(r !== 'ok'){ R.cases.push({id:c.id, err:r, pass:false}); continue; }
    }
    await sleep(1400);
    toast = await evalJS('var t=document.querySelector("[data-mount=toast]");' +
      'return {hidden:t.hidden, text:(t.textContent||"").replace(/\\s+/g," ").trim()};');
    const files = landed(c.want);
    const claimsDone = /완료/.test(toast.text);
    R.cases.push({id:c.id, toast:toast.text, toastShown:!toast.hidden, claimsDone,
      기간일치:c.periodOk === undefined ? '해당없음' : c.periodOk,
      files, pass: !toast.hidden && claimsDone && files.every(f => f.ok)
                   && (c.periodOk === undefined || c.periodOk)});
  }

  /* ── 2-b) 잠긴 내려받기 — 버튼이 disabled 이고 토스트도 파일도 나오지 않는다 (D-39)
        전자서명 결과 파일 형식이 미결이라(meeting_20260828.md 확인필요 ②) 실물이 없다.
        실물이 없는 자리에서 `완료` 토스트가 뜨면 그것이 곧 거짓말이므로 여기서 막는다. */
  {
    clearDL();
    await evalJS('go("contracts","default"); hideToast(); return 1;');
    await sleep(250);
    CT_ROWS = await evalJS('return Math.min(psz("ct-tbl"), ctSignedCount(CONTRACTS));');
    const lock = await evalJS(`
      var sec=document.querySelector('section.screen[data-screen=contracts]');
      var bulk=sec.querySelector('[data-act="ct-download"]');
      var rows=sec.querySelectorAll('tbody tr.clickable [data-act="ct-doc"]');
      var live=[].filter.call(rows, function(b){ return !b.disabled; }).length;
      bulk.click();
      [].forEach.call(rows, function(b){ b.click(); });
      return {bulkDisabled: !!bulk.disabled, rowBtns: rows.length, rowLive: live,
              docAnchors: sec.querySelectorAll('tbody a[href*="assets/docs"]').length};
    `);
    await sleep(1200);
    const t1 = await evalJS('var t=document.querySelector("[data-mount=toast]"); return {hidden:t.hidden, text:(t.textContent||"").trim()};');
    const f1 = assetLanded();
    R.cases.push({id:'계약기록 내려받기 잠금 — 토스트 0 · 파일 0', bulkDisabled:lock.bulkDisabled,
      rowBtns:lock.rowBtns, rowLive:lock.rowLive, docAnchors:lock.docAnchors, toast:t1.text, saved:f1,
      pass: lock.bulkDisabled === true && lock.rowBtns === CT_ROWS && lock.rowLive === 0
            && lock.docAnchors === 0 && t1.hidden === true && f1.length === 0});

    /* 사라진 상태로 딥링크해도 완료를 말하지 않는다 — 주소를 붙여 넣고 새로 여는 경로 그대로 본다 */
    clearDL();
    await send('Page.navigate', {url:'http://127.0.0.1:' + PORT + '/app.html#contracts/downloaded'});
    await sleep(1800);
    await send('Browser.setDownloadBehavior', {behavior:'allow', downloadPath: DL});
    await sleep(600);
    const t2 = await evalJS('var t=document.querySelector("[data-mount=toast]"); return {hidden:t.hidden, text:(t.textContent||"").trim(), view:document.body.dataset.view};');
    const f2 = assetLanded();
    R.cases.push({id:'#contracts/downloaded 딥링크 — 완료 주장 없음', toast:t2.text, view:t2.view, saved:f2,
      pass: t2.hidden === true && t2.view === 'contracts' && f2.length === 0});
  }

  /* ── 3) 소멸·닫기 — 원본 Toast.tsx:18(기본 3000ms) · :45-51(duration 0 이면 X 버튼) ── */
  {
    clearDL();
    await evalJS('go("invest-assets","default"); return 1;'); await sleep(200);
    await evalJS('document.querySelector(\'[data-act="xls-open"][data-xls="assets-status"]\').click(); return 1;');
    await sleep(900);
    const shown = await evalJS('var t=document.querySelector("[data-mount=toast]"); return {hidden:t.hidden, close:t.querySelectorAll(".t-close").length};');
    await sleep(3200);
    const gone = await evalJS('return document.querySelector("[data-mount=toast]").hidden;');
    R.cases.push({id:'토스트 자동 소멸 3,000ms', shown:!shown.hidden, closeBtn:shown.close, goneAfter:gone,
      pass: !shown.hidden && shown.close === 0 && gone === true});

    await evalJS('showToast("영구 토스트 점검", null, 0); return 1;'); await sleep(200);
    const perm = await evalJS('var t=document.querySelector("[data-mount=toast]"); return {hidden:t.hidden, close:t.querySelectorAll(".t-close").length};');
    await sleep(3400);
    const still = await evalJS('return document.querySelector("[data-mount=toast]").hidden;');
    await evalJS('var b=document.querySelector("[data-mount=toast] .t-close"); if(b) b.click(); return 1;'); await sleep(150);
    const closed = await evalJS('return document.querySelector("[data-mount=toast]").hidden;');
    R.cases.push({id:'duration 0 → X 닫기 버튼', closeBtn:perm.close, stillAfter3s:!still, closedByX:closed,
      pass: perm.close === 1 && still === false && closed === true});
  }

  R.console = consoleErrors.slice();
  fs.writeFileSync(path.join(OUTDIR, 'verify_toast_result.json'), JSON.stringify(R, null, 1));

  /* ── `완료` 주장 문구 판정 ──
     1) 이 수집은 2026-08-30 이전까지 곳수만 찍고 통과·실패를 가르지 않았다.
     근거 = request_register.md D-39 「실물 없는 `내려받기 완료` 토스트 금지」.
     판정식 — 완료를 말하는 토스트는 무엇을 내려줬는지(파일명 표현식)를 반드시 함께 말해야 한다.
     `showToast('내려받기 완료')` 처럼 인자 전체가 문자열 리터럴이면 대조할 실물이 없는 주장이라
     아래 2) 의 바이트 대조로 확인할 방법 자체가 없다. 그것이 D-39 가 막은 자리다.
     곳수(현재 4개)는 못 박지 않는다 — 내려받기 경로가 늘면 같이 늘 값이다.
     다만 0 이면 토스트 배선이 끊겼거나 수집 정규식이 낡은 것이므로 그것만 본다. */
  const bareClaims = R.claims.filter(c => {
    const arg = c.replace(/^showToast\(/, '').split(/,(?![^(]*\))/)[0].trim().replace(/\)$/, '');
    return /^(['"]).*\1$/.test(arg);                       /* 인자 전체가 문자열 리터럴 = 파일명을 안 댄다 */
  });
  const claimFails = [];
  if(R.claims.length === 0) claimFails.push('`완료` 토스트 0개 — 배선이 끊겼거나 수집 정규식이 낡았다');
  if(bareClaims.length) claimFails.push('파일명을 대지 않는 완료 주장 ' + bareClaims.length + '개 (D-39): ' + bareClaims.join(' | '));
  R.cases.push({id:'`완료` 토스트는 전건 파일명을 댄다 (D-39)', 주장수:R.claims.length,
    파일명없음:bareClaims, pass: claimFails.length === 0});

  console.log('== `완료` 주장 문구 ' + R.claims.length + '개 ==');
  R.claims.forEach(c => console.log('  ' + c.replace(/\s+/g, ' ')));
  claimFails.forEach(f => console.log('  FAIL ' + f));
  console.log('== 실물 대조 ' + R.cases.length + '건 ==');
  R.cases.forEach(c => console.log('  ' + (c.pass ? 'PASS ' : 'FAIL ') + c.id + '  ' +
    JSON.stringify({toast:c.toast, files:(c.files || []).map(f => f.name + ':' + f.bytes + '/' + f.srcBytes), err:c.err})));
  const fail = R.cases.filter(c => !c.pass).length;
  console.log('== FAIL ' + fail + ' · 콘솔 에러 ' + R.console.length + ' ==');
  R.console.slice(0, 10).forEach(c => console.log('  - ' + c));

  ws.close(); chrome.kill(); server.close();
  process.exit(fail || R.console.length ? 1 : 0);
}
main().catch(e => { console.error('VERIFY ERROR', e); process.exit(1); });
