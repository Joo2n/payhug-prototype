/* 용어 해설 카드가 거는 화면 5종 헤드리스 캡처 + 요소 좌표 지도 수집
   - 창을 띄우지 않는다(--headless=new)
   - 이미지: assets/shots/<name>.webp (CDP 로 직접 webp 수신)
   - 좌표: _pipeline/investor_admin/shot_rects.json
   CDP 배선 패턴은 verify_app.js 와 동일(수제 WebSocket + Runtime.evaluate). */
const http = require('http');
const fs   = require('fs');
const path = require('path');
const os   = require('os');
const { spawn, execFileSync } = require('child_process');

const REPO   = '/Users/semi/cursor/payhug-investor-admin';
const SHOTS  = path.join(REPO, 'assets', 'shots');
const OUTDIR = '/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin';
const OUTJSON = path.join(OUTDIR, 'shot_rects.json');
const PORT = 8800 + (process.pid % 90), DPORT = 9500 + (process.pid % 90);
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const BUDGET = 5 * 1024 * 1024;
const VIEW_W = 1440;

/* 촬영 대상 = glossary_manuscript.md 의 [[shot: …]] 가 실제로 부르는 화면만.
   전량 촬영은 하지 않는다 — 아무 문서도 걸지 않는 캡처 10장이 배포에 0.90MB 실려
   나가던 것을 걷어냈다(2026-08-29).

   ■ 마커가 거는 화면은 원고가 정하고, 원고는 바뀐다.
     용어 카드를 여기 없는 화면(예: invest-profit--weekly, certificate, xls-*)에
     걸려면 캡처가 먼저 있어야 한다. 순서:
       1) 이 FILES 에 <화면>.html 을 넣는다
       2) node capture_shots.js  — assets/shots/<화면>.webp + shot_rects.json 재생성
       3) glossary_manuscript.md 에 [[shot: <화면> | anchor: … | kind: …]] 를 쓴다
       4) python3 build_glossary.py && python3 verify_shotmarks.py
     1 을 건너뛰면 build_glossary.py 가 shot_rects.json 에서 KeyError 로 멎는다.
     반대로 원고에서 빠진 화면은 여기서도 빼고 webp 도 지운다 — 안 그러면 다시 되살아난다.
     verify_shotmarks.py 판정 D 가 이 목록과 원고의 어긋남을 잡는다. */
const FILES = [
  'invest-assets.html', 'invest-profit.html',
  'merchants.html', 'contracts.html', 'coocon.html'
];

/* 화질 예산 시도 순서 — quality 를 먼저 깎고, 그래도 넘치면 dsf 를 내린다 */
const ATTEMPTS = [{dsf:2, q:70}, {dsf:2, q:60}, {dsf:2, q:50}, {dsf:1.5, q:50}];

const MIME = {'.html':'text/html; charset=utf-8', '.css':'text/css; charset=utf-8', '.js':'text/javascript',
  '.png':'image/png', '.webp':'image/webp', '.svg':'image/svg+xml', '.pdf':'application/pdf',
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
let consoleErrors = [];
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

/* ══════════ 페이지 안에서 도는 좌표 수집기 ══════════ */
function COLLECT(){
  var KEY_CARD = /(card|stat|summary|kpi|metric|tile)/i;
  var KEY_NOTE = /(foot|note|hint|caption|notice)/i;
  var out = [], seen = new Map();
  var HTMLNS = 'http://www.w3.org/1999/xhtml';

  function clsList(el){
    var c = el.getAttribute && el.getAttribute('class');
    if(!c || typeof c !== 'string') return [];
    return c.trim().split(/\s+/).filter(function(x){ return x && /^[A-Za-z_][A-Za-z0-9_-]*$/.test(x); });
  }
  function seg(el){
    var s = el.tagName.toLowerCase();
    var cls = clsList(el).slice(0, 3);
    if(cls.length) s += '.' + cls.join('.');
    var p = el.parentElement;
    if(p){
      var same = [], k;
      for(k = 0; k < p.children.length; k++) if(p.children[k].tagName === el.tagName) same.push(p.children[k]);
      if(same.length > 1) s += ':nth-of-type(' + (same.indexOf(el) + 1) + ')';
    }
    return s;
  }
  function count(sel){ try { return document.querySelectorAll(sel).length; } catch(e){ return 0; } }
  function uniq(el, noTable){
    var id = el.getAttribute('id');
    if(id && /^[A-Za-z_][A-Za-z0-9_-]*$/.test(id) && count('#' + id) === 1) return '#' + id;
    var parts = [], node = el, guard = 0, sel = '', hit = '';
    while(node && node.nodeType === 1 && node.tagName !== 'BODY' && guard++ < 24){
      parts.unshift(seg(node));
      sel = parts.join(' > ');
      if(count(sel) === 1){ hit = sel; break; }
      node = node.parentElement;
    }
    if(!hit) return 'body > ' + parts.join(' > ');
    /* 표 안 요소는 사람이 알아보게 소속 table 로 앞을 묶는다 */
    if(!noTable && /^(tr|td|th|tbody|thead|tfoot)[.:>\s]/.test(hit + ' ')){
      var tbl = el.closest && el.closest('table');
      if(tbl && tbl !== el){
        var comb = uniq(tbl, true) + ' ' + hit;
        if(count(comb) === 1) return comb;
      }
    }
    return hit;
  }
  function txt(el){
    var t = (el.innerText && el.innerText.length) ? el.innerText : (el.textContent || '');
    t = String(t).replace(/\s+/g, ' ').trim();
    return t.length > 80 ? t.slice(0, 79) + '…' : t;
  }
  function r1(v){ return Math.round(v * 10) / 10; }
  /* overflow:auto/scroll/hidden 컨테이너에 가려 캡처 이미지에 안 나오는 요소를 가려낸다
     (.tbl-scroll / .sheet-scroll 이 가로 스크롤이라 넓은 표의 오른쪽 열이 잘린다) */
  function clippedBy(el, r){
    var n = el.parentElement, cs, cr, vx1 = -1e9, vy1 = -1e9, vx2 = 1e9, vy2 = 1e9, guard = 0;
    while(n && n.nodeType === 1 && guard++ < 30){
      cs = getComputedStyle(n);
      if(/(auto|scroll|hidden)/.test(cs.overflowX)){
        cr = n.getBoundingClientRect();
        vx1 = Math.max(vx1, cr.left); vx2 = Math.min(vx2, cr.left + n.clientWidth + 1);
      }
      if(/(auto|scroll|hidden)/.test(cs.overflowY)){
        cr = n.getBoundingClientRect();
        vy1 = Math.max(vy1, cr.top); vy2 = Math.min(vy2, cr.top + n.clientHeight + 1);
      }
      n = n.parentElement;
    }
    var iw = Math.min(r.right, vx2) - Math.max(r.left, vx1);
    var ih = Math.min(r.bottom, vy2) - Math.max(r.top, vy1);
    if(iw < 0) iw = 0;
    if(ih < 0) ih = 0;
    var area = r.width * r.height;
    return area > 0 ? ((iw * ih) / area) < 0.6 : false;
  }
  function add(el, kind){
    if(!el || el.nodeType !== 1 || seen.has(el)) return;
    if(el.namespaceURI !== HTMLNS) return;
    var r = el.getBoundingClientRect();
    var w = r1(r.width), h = r1(r.height);
    if(!(w > 0 && h > 0)) return;
    var tx = txt(el);
    if(!tx) return;                       /* 빈 칸(.c-empty 등)은 용어 오버레이 대상이 아니다 */
    var it = {sel: uniq(el), text: tx, tag: el.tagName.toLowerCase(), kind: kind,
      x: r1(r.left + window.scrollX), y: r1(r.top + window.scrollY), w: w, h: h};
    if(clippedBy(el, r)) it.clipped = true;
    seen.set(el, it); out.push(it);
  }
  function leaves(root){
    var res = [], all = root.querySelectorAll('*'), i, j, e, kids, hasTextKid;
    for(i = 0; i < all.length; i++){
      e = all[i];
      if(e.namespaceURI !== HTMLNS) continue;
      if(!clsList(e).length) continue;
      if(!(e.textContent || '').replace(/\s+/g, '').length) continue;
      kids = e.children; hasTextKid = false;
      for(j = 0; j < kids.length; j++){
        if((kids[j].textContent || '').replace(/\s+/g, '').length){ hasTextKid = true; break; }
      }
      if(hasTextKid) continue;
      res.push(e);
    }
    return res;
  }
  function each(sel, kind){
    var ns = document.querySelectorAll(sel), i;
    for(i = 0; i < ns.length; i++) add(ns[i], kind);
  }

  /* 1) 좌측 메뉴 */
  each('a[class*="nav"], button[class*="nav"], .nav-group-label', 'nav');
  /* 2) 페이지 헤더 제목·기준일 */
  each('.page-header h1, .page-header h2, .page-title, .base-date, .page-header .mono, .back-link', 'header');
  /* 3) 표 머리글 */
  each('th', 'th');
  /* 4) 표 각 행의 첫 열 td */
  var trs = document.querySelectorAll('tr'), i, k2, tds;
  for(i = 0; i < trs.length; i++){
    tds = trs[i].querySelectorAll(':scope > td');
    /* 첫 칸이 체크박스·여백이면 글자가 있는 첫 칸이 행 이름 역할을 한다 */
    for(k2 = 0; k2 < tds.length; k2++){
      if((tds[k2].textContent || '').replace(/\s+/g, '').length){ add(tds[k2], 'row-head'); break; }
    }
  }
  /* 5) 카드·요약·현황류 + 그 안의 라벨·값 */
  var cands = document.querySelectorAll('[class]'), j, el, lv, k;
  for(j = 0; j < cands.length; j++){
    el = cands[j];
    if(el.namespaceURI !== HTMLNS) continue;
    if(!KEY_CARD.test(clsList(el).join(' '))) continue;
    add(el, 'card');
    lv = leaves(el);
    if(lv.length <= 12) for(k = 0; k < lv.length; k++) add(lv[k], 'card-text');
  }
  /* 6) label */
  each('label', 'label');
  /* 7) 각주·안내문 */
  for(j = 0; j < cands.length; j++){
    el = cands[j];
    if(el.namespaceURI !== HTMLNS) continue;
    if(!KEY_NOTE.test(clsList(el).join(' '))) continue;
    add(el, 'note');
    lv = leaves(el);
    if(lv.length <= 12) for(k = 0; k < lv.length; k++) add(lv[k], 'note-text');
  }

  /* 실제로 넘치는 스크롤 컨테이너 목록 — 캡처에서 잘린 영역의 근거 */
  var scrollers = [], allc = document.querySelectorAll('*'), cs2, rr;
  for(j = 0; j < allc.length; j++){
    el = allc[j];
    if(el.namespaceURI !== HTMLNS) continue;
    cs2 = getComputedStyle(el);
    if(!/(auto|scroll)/.test(cs2.overflowX) && !/(auto|scroll)/.test(cs2.overflowY)) continue;
    if(el.scrollWidth <= el.clientWidth + 1 && el.scrollHeight <= el.clientHeight + 1) continue;
    rr = el.getBoundingClientRect();
    scrollers.push({sel: uniq(el), clientW: el.clientWidth, scrollW: el.scrollWidth,
      clientH: el.clientHeight, scrollH: el.scrollHeight,
      x: r1(rr.left + window.scrollX), y: r1(rr.top + window.scrollY)});
  }

  var de = document.documentElement, bd = document.body;
  return {
    scrollers: scrollers,
    docW: Math.max(de.scrollWidth, bd ? bd.scrollWidth : 0, de.clientWidth),
    docH: Math.max(de.scrollHeight, bd ? bd.scrollHeight : 0, de.clientHeight),
    fontOK: (document.fonts && document.fonts.check) ? !!document.fonts.check('16px "Noto Sans KR"') : null,
    items: out
  };
}

/* ══════════ webp 실측 크기: sips 우선, 실패 시 헤더 파싱 ══════════ */
function webpSizeHeader(buf){
  if(buf.length < 30 || buf.toString('ascii', 0, 4) !== 'RIFF' || buf.toString('ascii', 8, 12) !== 'WEBP') return null;
  const fourcc = buf.toString('ascii', 12, 16);
  if(fourcc === 'VP8X') return {w: (buf.readUIntLE(24, 3) & 0xFFFFFF) + 1, h: (buf.readUIntLE(27, 3) & 0xFFFFFF) + 1};
  if(fourcc === 'VP8 ') return {w: buf.readUInt16LE(26) & 0x3FFF, h: buf.readUInt16LE(28) & 0x3FFF};
  if(fourcc === 'VP8L'){
    const b = buf.readUInt32LE(21);
    return {w: (b & 0x3FFF) + 1, h: ((b >> 14) & 0x3FFF) + 1};
  }
  return null;
}
function imgSize(file){
  try {
    const o = execFileSync('sips', ['-g', 'pixelWidth', '-g', 'pixelHeight', file], {encoding: 'utf8'});
    const w = /pixelWidth:\s*(\d+)/.exec(o), h = /pixelHeight:\s*(\d+)/.exec(o);
    if(w && h) return {w: +w[1], h: +h[1], via: 'sips'};
  } catch(e){}
  const hd = webpSizeHeader(fs.readFileSync(file));
  if(hd) return {w: hd.w, h: hd.h, via: 'header'};
  return {w: null, h: null, via: 'fail'};
}

async function runPass(dsf, quality){
  const screens = [];
  await send('Emulation.setDeviceMetricsOverride', {width: VIEW_W, height: 1200, deviceScaleFactor: dsf, mobile: false});
  await send('Emulation.setDefaultBackgroundColorOverride', {color: {r:255, g:255, b:255, a:1}});

  for(const f of FILES){
    const before = consoleErrors.length;
    await send('Page.navigate', {url: 'http://127.0.0.1:' + PORT + '/' + f});
    for(let i = 0; i < 60; i++){
      await sleep(120);
      let st = '';
      try { st = await evalJS('return document.readyState;'); } catch(e){ st = ''; }
      if(st === 'complete') break;
    }
    /* 웹폰트(Noto Sans KR)는 외부 CDN — fonts.ready 대기 후 여유 800ms */
    try { await evalJS('return document.fonts.ready.then(function(){return 1;});'); } catch(e){}
    await sleep(800);

    const R = await evalJS('return (' + COLLECT.toString() + ')();');
    const docW = Math.max(R.docW, VIEW_W), docH = R.docH;

    const shot = await send('Page.captureScreenshot', {
      format: 'webp', quality: quality, captureBeyondViewport: true, fromSurface: true,
      clip: {x: 0, y: 0, width: docW, height: docH, scale: 1}
    });
    const name = f.replace(/\.html$/, '') + '.webp';
    const dest = path.join(SHOTS, name);
    fs.writeFileSync(dest, Buffer.from(shot.data, 'base64'));
    const sz = imgSize(dest);

    screens.push({
      file: f, shot: 'assets/shots/' + name,
      docW: docW, docH: docH, imgW: sz.w, imgH: sz.h,
      bytes: fs.statSync(dest).size, sizeVia: sz.via, fontOK: R.fontOK, scrollers: R.scrollers,
      clipped: R.items.filter(function(i){ return i.clipped; }).length,
      consoleErrors: consoleErrors.slice(before),
      items: R.items
    });
    process.stdout.write('  ' + f.padEnd(34) + ' doc ' + docW + 'x' + docH +
      '  img ' + sz.w + 'x' + sz.h + '  ' + (fs.statSync(dest).size/1024).toFixed(0) + 'KB  items ' + R.items.length + '\n');
  }
  return screens;
}

async function main(){
  fs.mkdirSync(SHOTS, {recursive: true});
  await new Promise(r => server.listen(PORT, r));
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'phcap-'));
  const chrome = spawn(CHROME, ['--headless=new', '--remote-debugging-port=' + DPORT,
    '--user-data-dir=' + profile, '--no-first-run', '--no-default-browser-check',
    '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1',
    '--window-size=' + VIEW_W + ',1200', 'about:blank'], {stdio: 'ignore'});

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
    if(m.method === 'Log.entryAdded' && m.params.entry.level === 'error'
        && !/favicon\.ico/.test(m.params.entry.url || ''))   /* 로컬 정적서버가 안 주는 파비콘 404는 화면 결함이 아니다 */
      consoleErrors.push('log: ' + m.params.entry.text + ' ' + (m.params.entry.url || ''));
  });
  await send('Runtime.enable'); await send('Log.enable'); await send('Page.enable');

  let screens = null, used = null;
  for(const a of ATTEMPTS){
    console.log('\n[pass] deviceScaleFactor=' + a.dsf + ' quality=' + a.q);
    consoleErrors = [];
    screens = await runPass(a.dsf, a.q);
    used = a;
    const total = screens.reduce((s, x) => s + x.bytes, 0);
    console.log('  총합 ' + (total/1048576).toFixed(2) + 'MB / 예산 5.00MB');
    if(total <= BUDGET) break;
    console.log('  예산 초과 -> 다음 설정으로 재촬영');
  }

  fs.writeFileSync(OUTJSON, JSON.stringify({screens: screens.map(s => ({
    file: s.file, shot: s.shot, docW: s.docW, docH: s.docH, imgW: s.imgW, imgH: s.imgH,
    scrollers: s.scrollers, items: s.items
  }))}, null, 1));

  /* ══════════ 자체 검증 ══════════ */
  console.log('\n══════ 검증 ══════');
  console.log('deviceScaleFactor=' + used.dsf + '  quality=' + used.q);
  let total = 0, fail = 0;
  for(const s of screens){
    total += s.bytes;
    const bad = [];
    if(!fs.existsSync(path.join(REPO, s.shot))) bad.push('파일없음');
    if(!s.items.length) bad.push('항목0');
    if(s.docH < 500) bad.push('docH<500');
    if(!s.imgW || !s.imgH) bad.push('이미지크기측정실패');
    if(s.consoleErrors.length) bad.push('콘솔' + s.consoleErrors.length);
    if(s.fontOK === false) bad.push('폰트미로드');
    if(bad.length) fail++;
    console.log((bad.length ? 'FAIL ' : 'ok   ') + s.file.padEnd(34) +
      String(s.bytes).padStart(8) + 'B  doc ' + s.docW + 'x' + s.docH +
      '  img ' + s.imgW + 'x' + s.imgH + '  items ' + String(s.items.length).padStart(4) +
      '  clip ' + String(s.clipped).padStart(3) +
      '  (' + s.sizeVia + ')' + (bad.length ? '  <- ' + bad.join(',') : ''));
    for(const e of s.consoleErrors) console.log('       console: ' + e);
  }
  /* 목표 장수는 FILES.length — 원고가 거는 화면이 늘고 줄면 같이 움직인다. 숫자를 박지 않는다 */
  console.log('\n장수 ' + screens.length + '/' + FILES.length + '   총합 ' + total + 'B (' + (total/1048576).toFixed(2) + 'MB) / 5.00MB 예산  ' +
    (total <= BUDGET ? 'OK' : '초과'));
  console.log('콘솔 에러 총 ' + screens.reduce((s,x)=>s+x.consoleErrors.length,0) + '건');
  console.log('실패 화면 ' + fail + '건');
  console.log('JSON: ' + OUTJSON);

  ws.close(); chrome.kill(); server.close();
  process.exit(0);
}
main().catch(e => { console.error('ERR', e); try{ ws && ws.close(); }catch(_){} process.exit(1); });
