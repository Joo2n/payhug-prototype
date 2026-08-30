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
    {id:'xls-get profit-status',   act:'location.hash="#xls-profit-status"; return 1;',
     click:'[data-act="xls-get"][data-xls="profit-status"]',   want:['투자수익현황_2026-08-21_2026-08-27.xlsx']},
    {id:'xls-get profit-daily',    act:'location.hash="#xls-profit-daily"; return 1;',
     click:'[data-act="xls-get"][data-xls="profit-daily"]',    want:['일별투자수익_2026-08-21_2026-08-27.xlsx']},
    /* 화면 버튼 → 중간 화면 없이 즉시 파일 (원본 ExcelDownloadButton 경로 대응) */
    {id:'xls-open 투자자산 현황 직행',   act:'go("invest-assets","default"); return 1;',
     click:'[data-act="xls-open"][data-xls="assets-status"]',   want:['투자자산현황_2026-08-27_2026-08-27.xlsx']},
    {id:'xls-open 가맹점별 투자자산 직행', act:'go("invest-assets","default"); return 1;',
     click:'[data-act="xls-open"][data-xls="assets-merchant"]', want:['가맹점별투자자산_2026-08-27_2026-08-27.xlsx']},
    /* 현황 카드도 집계 단위마다 기간이 갈린다 — 카드가 4주를 말하면 4주 파일이 나가야 한다 */
    {id:'xls-open 투자수익 현황 직행',   act:'go("invest-profit","default"); return 1;',
     click:'[data-act="xls-open"][data-xls="profit-status"]',   want:['투자수익현황_2026-08-21_2026-08-27.xlsx']},
    {id:'xls-open 주별 수익 현황 직행',  act:'go("invest-profit","weekly"); return 1;',
     click:'[data-act="xls-open"][data-xls="profit-status"]',   want:['투자수익현황_2026-08-03_2026-08-30.xlsx']},
    {id:'xls-open 월별 수익 현황 직행',  act:'go("invest-profit","monthly"); return 1;',
     click:'[data-act="xls-open"][data-xls="profit-status"]',   want:['투자수익현황_2026-03-01_2026-08-31.xlsx']},
    /* 표가 일별·주별·월별 3단이라 같은 버튼이 지금 보고 있는 표의 파일을 내려준다 */
    {id:'xls-open 일별 투자수익 직행',   act:'go("invest-profit","default"); return 1;',
     click:'[data-act="xls-open"][data-xls="profit-daily"]',    want:['일별투자수익_2026-08-21_2026-08-27.xlsx']},
    {id:'xls-open 주별 투자수익 직행',   act:'go("invest-profit","weekly"); return 1;',
     click:'[data-act="xls-open"][data-xls="profit-daily"]',    want:['주별투자수익_2026-08-03_2026-08-30.xlsx']},
    {id:'xls-open 월별 투자수익 직행',   act:'go("invest-profit","monthly"); return 1;',
     click:'[data-act="xls-open"][data-xls="profit-daily"]',    want:['월별투자수익_2026-03-01_2026-08-31.xlsx']},
    {id:'cert-pdf 증명서 PDF',      act:'location.hash="#certificate"; return 1;',
     click:'[data-act="cert-pdf"]', want:['투자자산증명서_20260827.pdf']},
    {id:'상태 진입 #invest-assets/download', act:'location.hash="#contracts"; return 1;',
     hash:'#invest-assets/download', want:['가맹점별투자자산_2026-08-27_2026-08-27.xlsx']}
  ];

  for(const c of CASES){
    clearDL();
    await evalJS(c.act); await sleep(300);
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
      files, pass: !toast.hidden && claimsDone && files.every(f => f.ok)});
  }

  /* ── 2-b) 잠긴 내려받기 — 버튼이 disabled 이고 토스트도 파일도 나오지 않는다 (D-39)
        전자서명 결과 파일 형식이 미결이라(meeting_20260828.md 확인필요 ②) 실물이 없다.
        실물이 없는 자리에서 `완료` 토스트가 뜨면 그것이 곧 거짓말이므로 여기서 막는다. */
  {
    clearDL();
    await evalJS('go("contracts","default"); document.querySelector("[data-mount=toast]").hidden=true; return 1;');
    await sleep(250);
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
      pass: lock.bulkDisabled === true && lock.rowBtns === 10 && lock.rowLive === 0
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

  console.log('== `완료` 주장 문구 ' + R.claims.length + '개 ==');
  R.claims.forEach(c => console.log('  ' + c.replace(/\s+/g, ' ')));
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
