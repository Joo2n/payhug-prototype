/* 용어 문서가 거는 화면 캡처 5장의 「그림 안 내용」을 판정한다.
   대상: payhug-investor-admin/assets/shots/*.webp  ·  거울: payhug-investor-glossary/assets/shots/*.webp

   ■ 왜 만들었나 (2026-08-31)
     배포된 용어 문서의 캡처 5장이 8/29 02:06 자로 굳어 있었다. 그 시절 화면은
     투자 규모 15억 · 가맹점 10곳 · Ty 10.85% · W 3.7일이고, 지금 정본은
     1억 · 8곳 · 13.21% · 3.04일이다. 본문 글자는 정본인데 그림만 옛것이라
     같은 화면이 두 가지 숫자를 말하고 있었다.
     그런데 캡처 파일을 여는 검증기는 verify_shotmarks.py 하나뿐이고, 그것도 마커 자리에
     잉크가 있는지만 본다. gate_glossary.js 는 이미지를 「51개인가」 개수로만 셌다.
     나머지는 전부 텍스트만 본다. 그래서 그림이 통째로 옛것이어도 전건 통과했다.

   ■ 방법 두 갈래를 다 쓴다
     (가) 재현 대조 — 촬영 대상 화면을 기록된 설정(dsf·quality·viewport)으로 다시 찍어
          저장본과 sha256 을 맞춘다. 화면이 바뀌었는데 이미지를 안 찍었으면 여기서 잡힌다.
          같은 입력·같은 설정이면 CDP webp 출력은 바이트까지 같다(2회 독립 실행 대조 확인).
     (나) 봉인 대조 — shot_rects.json 의 capture 블록에 촬영 시점의 이미지 sha256 ·
          원본 HTML sha256 · mtime 이 적혀 있다. 크롬 없이 그 자리에서 어긋남을 잡는다.
          원본 HTML 이 촬영 뒤 한 글자라도 바뀌면 srcSha256 이 갈린다.
     (가)가 본질이고 (나)는 싸다. (나)만 두면 봉인을 다시 찍는 것으로 우회되고,
     (가)만 두면 크롬이 없는 자리에서 검사가 통째로 빠진다. 그래서 둘 다 판정한다.

   ■ 새는 자리를 막는다
     · FAIL 이 1건이라도 있으면 종료코드 1. 곳수만 찍고 끝나는 자리를 두지 않는다.
     · try/catch 로 SKIP 하지 않는다. 예외는 그대로 종료코드 1 로 나간다.
     · 대상이 0건이면 FAIL (A1·A7·D5).
     · 판정기 자신이 어긋남을 실제로 잡는지 매 실행 자기시험한다(D1~D6).

   사용: node verify_shots.js [--repo=<원본>] [--mirror=<거울>]
         SRC_REPO / DST_REPO 환경변수도 같은 자리를 가리킨다. */
const http = require('http');
const fs = require('fs');
const os = require('os');
const path = require('path');
const crypto = require('crypto');
const { spawn, execFileSync } = require('child_process');
const CHROME_DL = require('./chrome_dl');
const PH_DL = CHROME_DL.dir();

const PIPE = __dirname;
const arg = k => (process.argv.find(a => a.startsWith('--' + k + '=')) || '').split('=').slice(1).join('=');
const REPO   = arg('repo')   || process.env.SRC_REPO || '/Users/semi/cursor/payhug-investor-admin';
const MIRROR = arg('mirror') || process.env.DST_REPO || '/Users/semi/cursor/payhug-investor-glossary';
const RECT   = arg('rect')   || path.join(PIPE, 'shot_rects.json');
const CAPJS  = path.join(PIPE, 'capture_shots.js');
const SHOTDIR = path.join(REPO, 'assets', 'shots');
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
/* 포트 대역은 파이프라인 안에서 겹치지 않게 고른다 — 8901·8903 은 verify_links.py 가
   고정으로 쓰고, 8400·8600·8700·8800·8900 과 9100·9300·9400·9500·9700 은 이미 임자가 있다 */
const PORT = 8200 + (process.pid % 90), DPORT = 9200 + (process.pid % 90);

const MIME = {'.html':'text/html; charset=utf-8', '.css':'text/css; charset=utf-8', '.js':'text/javascript',
  '.png':'image/png', '.webp':'image/webp', '.svg':'image/svg+xml', '.pdf':'application/pdf',
  '.xlsx':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'};

const R = [];                       /* 판정 전수 — 종료코드는 여기서만 나온다 */
function chk(name, pass, detail){
  R.push({name, pass: pass === true, detail: detail === undefined ? '' : String(detail)});
  console.log((pass === true ? '  PASS ' : '  FAIL ') + name + (detail === undefined || detail === '' ? '' : '  ' + detail));
}
const sha = b => crypto.createHash('sha256').update(b).digest('hex');
const sleep = ms => new Promise(r => setTimeout(r, ms));

/* ══════════ 판정기 본체 — 자기시험이 이 함수들을 그대로 다시 부른다 ══════════ */

/* 명부 4자 일치. 어느 한 집합이 비면 그 자체로 실패다(0건 통과 방지). */
function judgeRoster(files, rectNames, sealNames, diskNames, mirrorNames){
  const out = [];
  const eq = (a, b) => a.length === b.length && a.every((x, i) => x === b[i]);
  const S = s => [...s].sort();
  out.push({name: 'A1 촬영 대상 0건 아님', pass: files.length > 0, detail: files.length + '종'});
  out.push({name: 'A2 봉인 files 0건 아님', pass: sealNames.length > 0, detail: sealNames.length + '건'});
  out.push({name: 'A3 shot_rects.screens = FILES', pass: eq(S(rectNames), S(files)),
            detail: S(rectNames).join(',')});
  out.push({name: 'A4 봉인 files = FILES', pass: eq(S(sealNames), S(files)), detail: S(sealNames).join(',')});
  out.push({name: 'A5 assets/shots 실물 = FILES', pass: eq(S(diskNames), S(files)), detail: S(diskNames).join(',')});
  out.push({name: 'A6 거울 저장소 실물 = FILES', pass: eq(S(mirrorNames), S(files)), detail: S(mirrorNames).join(',')});
  return out;
}

/* 화면 한 장의 봉인 대조. 이미지·원본 HTML·촬영 순서 세 축. */
function judgeSeal(name, seal, imgBuf, srcBuf, imgMtime, srcMtime, mirrorBuf){
  const out = [];
  const iSha = sha(imgBuf), sSha = sha(srcBuf);
  out.push({name: 'B1 ' + name + ' 이미지 sha256 = 봉인', pass: iSha === seal.imgSha256,
            detail: iSha.slice(0, 12) + ' vs ' + String(seal.imgSha256).slice(0, 12)});
  out.push({name: 'B2 ' + name + ' 원본 HTML sha256 = 봉인', pass: sSha === seal.srcSha256,
            detail: sSha.slice(0, 12) + ' vs ' + String(seal.srcSha256).slice(0, 12)
                    + (sSha === seal.srcSha256 ? '' : ' — 화면이 촬영 뒤 바뀌었다. capture_shots.js 를 다시 돌린다')});
  out.push({name: 'B3 ' + name + ' 이미지가 화면보다 나중', pass: imgMtime >= srcMtime,
            detail: new Date(imgMtime).toISOString() + ' >= ' + new Date(srcMtime).toISOString()});
  out.push({name: 'B4 ' + name + ' 거울 이미지 = 원본 이미지', pass: sha(mirrorBuf) === iSha,
            detail: sha(mirrorBuf).slice(0, 12) + ' vs ' + iSha.slice(0, 12)});
  return out;
}

/* 재현 대조 한 장. 지금 화면을 다시 찍은 바이트가 저장본과 같은가. */
function judgeRepro(name, storedSha, freshBuf, docNow, docSaved){
  const f = sha(freshBuf);
  return [
    {name: 'C1 ' + name + ' 재현 바이트 = 저장본', pass: f === storedSha,
     detail: f.slice(0, 12) + ' vs ' + String(storedSha).slice(0, 12)},
    {name: 'C2 ' + name + ' 문서 크기 = 봉인 시점', pass: docNow.w === docSaved.w && docNow.h === docSaved.h,
     detail: docNow.w + 'x' + docNow.h + ' vs ' + docSaved.w + 'x' + docSaved.h}
  ];
}

/* ══════════ 크롬 배선 ══════════ */
let msgId = 0, ws, pending = new Map(), consoleErrors = [];
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

const server = http.createServer((req, res) => {
  const p = path.join(REPO, decodeURIComponent(req.url.split('?')[0]));
  fs.readFile(p, (e, b) => {
    if(e){ res.writeHead(404); res.end('nope'); return; }
    res.writeHead(200, {'Content-Type': MIME[path.extname(p)] || 'application/octet-stream'});
    res.end(b);
  });
});

async function main(){
  console.log('원본 ' + REPO);
  console.log('거울 ' + MIRROR);

  /* ── 재료 ─────────────────────────────────────────────── */
  const capjs = fs.readFileSync(CAPJS, 'utf8');
  const mFiles = /const FILES = \[(.*?)\];/s.exec(capjs);
  if(!mFiles) throw new Error('capture_shots.js 의 FILES 목록을 못 읽는다');
  const FILES = [...mFiles[1].matchAll(/'([A-Za-z0-9._-]+\.html)'/g)].map(m => m[1]);

  const rect = JSON.parse(fs.readFileSync(RECT, 'utf8'));
  const CAP = rect.capture;
  const rectByFile = Object.fromEntries((rect.screens || []).map(s => [s.file, s]));

  /* A7 — 봉인 블록 자체가 있는가. 없으면 (가)의 재현 설정을 댈 수 없고
     (나)는 비교 상대가 없어 「대상 0건」으로 통째로 새어 나간다. */
  console.log('\n── A. 명부·봉인 ──');
  chk('A7 shot_rects.json 에 capture 봉인 블록 존재',
      !!(CAP && CAP.files && CAP.dsf && CAP.quality && CAP.viewW),
      CAP ? ('dsf=' + CAP.dsf + ' q=' + CAP.quality + ' view=' + CAP.viewW + ' ' + (CAP.chrome || '')) : '없음');
  if(!(CAP && CAP.files)) throw new Error('봉인 블록이 없다 — node capture_shots.js 를 먼저 돌린다');

  const diskNames = fs.readdirSync(SHOTDIR).filter(f => f.endsWith('.webp')).map(f => f.replace(/\.webp$/, '.html'));
  const mirrorDir = path.join(MIRROR, 'assets', 'shots');
  const mirrorNames = fs.existsSync(mirrorDir)
    ? fs.readdirSync(mirrorDir).filter(f => f.endsWith('.webp')).map(f => f.replace(/\.webp$/, '.html'))
    : [];
  chk('A0 거울 저장소 캡처 폴더 존재', fs.existsSync(mirrorDir), mirrorDir);
  for(const j of judgeRoster(FILES, Object.keys(rectByFile), Object.keys(CAP.files), diskNames, mirrorNames))
    chk(j.name, j.pass, j.detail);
  for(const f of FILES)
    chk('A8 ' + f + ' 원본 화면 실재', fs.existsSync(path.join(REPO, f)), path.join(REPO, f));

  /* ── B. 봉인 대조 (크롬 없음) ─────────────────────────── */
  console.log('\n── B. 봉인 대조 ──');
  const stored = {};
  for(const f of FILES){
    const seal = CAP.files[f];
    if(!seal){ chk('B0 ' + f + ' 봉인 항목 존재', false, '없음'); continue; }
    const imgP = path.join(REPO, seal.shot), srcP = path.join(REPO, f);
    const mirP = path.join(mirrorDir, path.basename(seal.shot));
    const imgBuf = fs.readFileSync(imgP), srcBuf = fs.readFileSync(srcP);
    const mirBuf = fs.existsSync(mirP) ? fs.readFileSync(mirP) : Buffer.alloc(0);
    stored[f] = {seal, imgBuf, imgSha: sha(imgBuf)};
    for(const j of judgeSeal(f, seal, imgBuf, srcBuf,
                             Math.floor(fs.statSync(imgP).mtimeMs), Math.floor(fs.statSync(srcP).mtimeMs), mirBuf))
      chk(j.name, j.pass, j.detail);
  }

  /* ── C. 재현 대조 (헤드리스 크롬으로 다시 찍는다) ─────── */
  console.log('\n── C. 재현 대조 ──');
  await new Promise(r => server.listen(PORT, r));
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'phvs-'));
  const chrome = spawn(CHROME, ['--headless=new', '--remote-debugging-port=' + DPORT,
    CHROME_DL.args(PH_DL, profile)[0], '--no-first-run', '--no-default-browser-check',
    '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1',
    '--window-size=' + CAP.viewW + ',' + CAP.viewH, 'about:blank'], {stdio: 'ignore'});

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
  if(!targets) throw new Error('크롬이 뜨지 않는다');
  ws = new WebSocket(targets.find(t => t.type === 'page').webSocketDebuggerUrl);
  await new Promise(r => ws.addEventListener('open', r));
  ws.addEventListener('message', ev => {
    const m = JSON.parse(ev.data);
    if(m.id && pending.has(m.id)){ pending.get(m.id).res(m.result); pending.delete(m.id); return; }
    if(m.method === 'Runtime.consoleAPICalled' && (m.params.type === 'error' || m.params.type === 'warning'))
      consoleErrors.push(m.params.type + ': ' + m.params.args.map(a => a.value || a.description || a.type).join(' '));
    if(m.method === 'Runtime.exceptionThrown')
      consoleErrors.push('exception: ' + (m.params.exceptionDetails.exception && m.params.exceptionDetails.exception.description || m.params.exceptionDetails.text));
    if(m.method === 'Log.entryAdded' && m.params.entry.level === 'error' && !/favicon\.ico/.test(m.params.entry.url || ''))
      consoleErrors.push('log: ' + m.params.entry.text + ' ' + (m.params.entry.url || ''));
  });
  await send('Runtime.enable'); await send('Log.enable'); await send('Page.enable');
  await send('Emulation.setDeviceMetricsOverride', {width: CAP.viewW, height: CAP.viewH, deviceScaleFactor: CAP.dsf, mobile: false});
  await send('Emulation.setDefaultBackgroundColorOverride', {color: {r:255, g:255, b:255, a:1}});

  const fresh = {};
  for(const f of FILES){
    await send('Page.navigate', {url: 'http://127.0.0.1:' + PORT + '/' + f});
    for(let i = 0; i < 60; i++){
      await sleep(120);
      let st = '';
      try { st = await evalJS('return document.readyState;'); } catch(e){ st = ''; }
      if(st === 'complete') break;
    }
    try { await evalJS('return document.fonts.ready.then(function(){return 1;});'); } catch(e){}
    await sleep(800);
    const D = await evalJS('var de=document.documentElement, bd=document.body;' +
      'return {w: Math.max(de.scrollWidth, bd?bd.scrollWidth:0, de.clientWidth),' +
      ' h: Math.max(de.scrollHeight, bd?bd.scrollHeight:0, de.clientHeight)};');
    const docW = Math.max(D.w, CAP.viewW), docH = D.h;
    const shot = await send('Page.captureScreenshot', {
      format: 'webp', quality: CAP.quality, captureBeyondViewport: true, fromSurface: true,
      clip: {x: 0, y: 0, width: docW, height: docH, scale: 1}
    });
    fresh[f] = Buffer.from(shot.data, 'base64');
    const rc = rectByFile[f] || {};
    for(const j of judgeRepro(f, (stored[f] || {}).imgSha, fresh[f], {w: docW, h: docH}, {w: rc.docW, h: rc.docH}))
      chk(j.name, j.pass, j.detail + (j.pass ? '' : '  ' + pixDiff(f, fresh[f])));
  }
  chk('C3 재현 촬영 중 콘솔 에러 0', consoleErrors.length === 0, consoleErrors.slice(0, 3).join(' | '));

  /* ── D. 자기시험 — 판정기가 어긋남을 실제로 잡는가 ────── */
  console.log('\n── D. 판별력 자기시험 ──');
  /* 자기시험은 실물이 성한지와 무관해야 한다. 실물 파일을 기준선으로 쓰면
     그 파일이 이미 어긋난 날(= 이 검사가 가장 필요한 날) 자기시험이 같이 무너져
     「검사기가 고장 났다」로 읽힌다. 그래서 봉인을 그 자리에서 지어 기준선을 만든다. */
  const probe = FILES[0], pv = stored[probe];
  const bImg = pv.imgBuf, bSrc = fs.readFileSync(path.join(REPO, probe));
  const T = 1700000000000;
  const fake = {shot: 'x', imgSha256: sha(bImg), srcSha256: sha(bSrc), imgMtime: T, srcMtime: T - 1000};
  const d0 = judgeSeal(probe, fake, bImg, bSrc, fake.imgMtime, fake.srcMtime, bImg);
  chk('D0 자기시험 기준선 4건 전건 통과', d0.every(x => x.pass === true),
      d0.filter(x => !x.pass).map(x => x.name).join(', '));

  const bad = Buffer.from(bImg); bad[bad.length - 1] ^= 0xFF;               /* 1바이트만 흔든다 */
  const d1 = judgeSeal(probe, fake, bad, bSrc, fake.imgMtime, fake.srcMtime, bad);
  chk('D1 이미지 1바이트 변조를 B1 이 잡는다', d1[0].pass === false && d1[1].pass === true);

  const srcBad = Buffer.concat([bSrc, Buffer.from('<!--x-->')]);
  const d2 = judgeSeal(probe, fake, bImg, srcBad, fake.imgMtime, fake.srcMtime, bImg);
  chk('D2 화면 1글자 변경을 B2 가 잡는다', d2[1].pass === false && d2[0].pass === true);

  const d3 = judgeSeal(probe, fake, bImg, bSrc, fake.srcMtime - 1, fake.srcMtime, bImg);
  chk('D3 화면이 이미지보다 새로우면 B3 이 잡는다', d3[2].pass === false && d3[0].pass === true);

  const d4 = judgeSeal(probe, fake, bImg, bSrc, fake.imgMtime, fake.srcMtime, Buffer.alloc(0));
  chk('D4 거울이 비면 B4 가 잡는다', d4[3].pass === false && d4[0].pass === true);

  const cut = FILES.slice(0, -1);
  const d5 = judgeRoster(FILES, Object.keys(rectByFile), Object.keys(CAP.files), cut, mirrorNames);
  chk('D5 실물 한 장이 빠지면 A5 가 잡는다', d5[4].pass === false);
  const d5b = judgeRoster([], [], [], [], []);
  chk('D5b 대상 0건이면 A1·A2 가 잡는다', d5b[0].pass === false && d5b[1].pass === false);

  const other = FILES.find(f => f !== probe && fresh[f] && sha(fresh[f]) !== pv.imgSha);
  const d6 = judgeRepro(probe, pv.imgSha, fresh[other], {w:1, h:1}, {w:1, h:1});
  chk('D6 다른 화면 그림을 C1 이 잡는다', d6[0].pass === false, probe + ' <- ' + other);

  /* ── 마무리 ───────────────────────────────────────────── */
  const fails = R.filter(r => !r.pass);
  chk('E1 판정 건수가 화면 수에 비례', R.length >= FILES.length * 5, R.length + '건 / 화면 ' + FILES.length + '종');

  console.log('\n══════ 판정 ══════');
  console.log('판정 ' + R.length + '건  ·  FAIL ' + R.filter(r => !r.pass).length + '건');
  for(const f of R.filter(r => !r.pass)) console.log('  FAIL ' + f.name + '  ' + f.detail);

  try{ ws.close(); }catch(e){}
  try{ chrome.kill('SIGKILL'); }catch(e){}
  try{ server.close(); }catch(e){}
  await sleep(300);
  try{ fs.rmSync(profile, {recursive:true, force:true, maxRetries:5, retryDelay:200}); }catch(e){}
  CHROME_DL.clean(PH_DL);
  process.exit(R.filter(r => !r.pass).length ? 1 : 0);
}

/* FAIL 한 자리에 붙는 진단 — 몇 픽셀이 어긋났는지. 판정은 위에서 이미 끝났다 */
function pixDiff(name, freshBuf){
  try {
    const a = path.join(os.tmpdir(), 'phvs-a-' + process.pid + '.webp');
    fs.writeFileSync(a, freshBuf);
    const b = path.join(REPO, 'assets', 'shots', name.replace(/\.html$/, '.webp'));
    const o = execFileSync('python3', ['-c',
      'import sys\nfrom PIL import Image, ImageChops\n' +
      'x=Image.open(sys.argv[1]).convert("RGB"); y=Image.open(sys.argv[2]).convert("RGB")\n' +
      'if x.size!=y.size: print("크기 %s vs %s"%(x.size,y.size)); sys.exit()\n' +
      'd=ImageChops.difference(x,y); n=sum(1 for p in d.getdata() if p!=(0,0,0))\n' +
      'print("어긋난 픽셀 %d / %d (%.3f%%)"%(n, x.size[0]*x.size[1], 100.0*n/(x.size[0]*x.size[1])))',
      a, b], {encoding: 'utf8'}).trim();
    fs.rmSync(a, {force: true});
    return o;
  } catch(e){ return '(픽셀 진단 실패: ' + e.message.split('\n')[0] + ')'; }
}

main().catch(e => {
  console.error('\nERR ' + (e && e.stack || e));
  try{ ws && ws.close(); }catch(_){}
  CHROME_DL.clean(PH_DL);
  process.exit(1);      /* 예외를 SKIP 으로 삼키지 않는다 */
});
