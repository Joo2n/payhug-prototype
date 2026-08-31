/* 용어판 게이트 — 창 없이(--headless=new) 돌리고, 하나라도 걸리면 종료코드 1.
   sync_glossary.sh 가 push 직전에 부른다. 통과해야만 올라간다.

   바깥 링크는 문자열·DOM 양쪽으로 본다. 본문의 <code>invest-assets.html</code> 같은
   화면 이름 표기는 링크가 아니므로 href·action 속성 안만 검사 대상이다.

   사용: node gate_glossary.js [--url=https://...]      (url 생략 시 로컬 파일 서버)   */
const http = require('http'), fs = require('fs'), path = require('path'), os = require('os');
const crypto = require('crypto');
const CHROME_DL = require('./chrome_dl');
const PH_DL = CHROME_DL.dir();
const { spawn, spawnSync } = require('child_process');

const REPO = process.env.DST_REPO || '/Users/semi/cursor/payhug-investor-glossary';
const argUrl = (process.argv.find(a => a.startsWith('--url=')) || '').slice(6);
const URL_IN = argUrl || process.env.GATE_URL || '';
const PORT = 8600 + (process.pid % 90), DPORT = 9300 + (process.pid % 90);
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const MIME = {'.html':'text/html; charset=utf-8', '.css':'text/css; charset=utf-8',
  '.js':'text/javascript', '.png':'image/png', '.webp':'image/webp', '.json':'application/json'};

const TITLE = '용어 해설 — 투자자 어드민';
const CARDS = 50, FIELDS = ['term', 'var', 'calc', 'screen', 'rel'];
const BANNED_FILES = ['app.html', 'capability.html', 'feasibility.html', 'inquiry.html',
                      'archive.html', 'review.html', 'glossary-legacy.html'];
const HREF_OK = /^(#|assets\/|https:\/\/fonts\.googleapis\.com|https:\/\/fonts\.gstatic\.com)/;

const server = http.createServer((req, res) => {
  const p = path.join(REPO, decodeURIComponent(req.url.split('?')[0].split('#')[0]));
  fs.readFile(p, (e, b) => {
    if(e){ res.writeHead(404); res.end('nope'); return; }
    res.writeHead(200, {'Content-Type': MIME[path.extname(p)] || 'application/octet-stream'});
    res.end(b);
  });
});

let msgId = 0, ws, pending = new Map();
const consoleErrors = [], fails = [];
function send(m, p){ const id = ++msgId; ws.send(JSON.stringify({id, method:m, params:p||{}}));
  return new Promise(res => pending.set(id, {res})); }
async function ev(x){
  const r = await send('Runtime.evaluate', {expression:'(function(){' + x + '})()', returnByValue:true});
  if(r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails.exception || r.exceptionDetails.text));
  return r.result.value;
}
/* 프로미스를 돌려주는 페이지 코드용 — 이미지 바이트를 받아 해시할 때 쓴다 */
async function evA(x){
  const r = await send('Runtime.evaluate', {expression:'(function(){' + x + '})()', returnByValue:true, awaitPromise:true});
  if(r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails.exception || r.exceptionDetails.text));
  return r.result.value;
}
const sleep = ms => new Promise(r => setTimeout(r, ms));
function check(name, pass, detail){
  console.log((pass ? '  PASS ' : '  FAIL ') + name + (detail === undefined || detail === '' ? '' : '  ' + detail));
  if(!pass) fails.push(name);
}

async function main(){
  /* ── A. 문자열 검사 — 브라우저를 띄우기 전에 파일 그대로 본다 ────────── */
  const file = path.join(REPO, 'index.html');
  if(!fs.existsSync(file)){ console.error('게이트 대상 없음:', file); process.exit(1); }
  const raw = fs.readFileSync(file, 'utf8');
  const attrs = (raw.match(/(?:href|action)="([^"]*)"/g) || []).map(a => a.replace(/^[a-z]+="/, '').slice(0, -1));
  const outside = attrs.filter(h => !HREF_OK.test(h));
  check('[문자열] 바깥 href/action 0', outside.length === 0, outside.slice(0, 6).join(' | '));
  const banned = BANNED_FILES.filter(f => attrs.some(h => h.indexOf(f) >= 0));
  check('[문자열] 형제 문서 href 0', banned.length === 0, banned.join(', '));
  const host = [...new Set((raw.match(/(?:href|src|action)="https?:\/\/[^/"]+/g) || [])
    .map(h => h.replace(/.*https?:\/\//, '')))].filter(h => h !== 'fonts.googleapis.com' && h !== 'fonts.gstatic.com');
  check('[문자열] 허용 밖 외부 호스트 0', host.length === 0, host.join(','));
  const t = /<title>([^<]*)<\/title>/.exec(raw);
  check('[문자열] <title> = ' + TITLE, !!t && t[1] === TITLE, t ? t[1] : '없음');
  check('[문자열] tb-alt 잔존 0', raw.indexOf('tb-alt') < 0);
  const shots = [...new Set((raw.match(/assets\/shots\/[A-Za-z0-9._%-]+\.webp/g) || []))];
  const missing = shots.filter(s => !fs.existsSync(path.join(REPO, s)));
  check('[문자열] 캡처 참조 실물 존재 (' + shots.length + '종)', shots.length > 0 && missing.length === 0, missing.join(', '));

  /* ── 캡처 내용 판정 (2026-08-31 신설) ─────────────────────────────────
     여기까지는 「몇 장인가 · 파일이 있는가」만 봤다. 그래서 15억·10곳 시절 그림이
     1억·8곳 본문 옆에 붙어 있어도 게이트를 통과했다. 개수 검사는 위에 그대로 두고,
     그림 안 내용을 보는 판정을 더한다.
       S1 — 배포본 webp 바이트가 shot_rects.json 촬영 봉인의 sha256 과 같은가
       S2 — verify_shots.js 전건(재현 대조 포함) 통과인가
       S3 — 화면이 실제로 물고 있는 이미지 바이트가 그 봉인과 같은가 (DOM 단계) */
  const shaHex = b => crypto.createHash('sha256').update(b).digest('hex');
  const RECT = path.join(__dirname, 'shot_rects.json');
  let SEAL = {};
  try {
    const cap = JSON.parse(fs.readFileSync(RECT, 'utf8')).capture;
    for(const k of Object.keys((cap && cap.files) || {}))
      SEAL[path.basename(cap.files[k].shot)] = cap.files[k].imgSha256;
  } catch(e){ SEAL = {}; }
  check('[캡처] shot_rects.json 촬영 봉인 존재', Object.keys(SEAL).length > 0,
        Object.keys(SEAL).length + '종');
  const sealBad = shots.map(s => path.basename(s)).filter(n =>
    !SEAL[n] || !fs.existsSync(path.join(REPO, 'assets/shots', n)) ||
    shaHex(fs.readFileSync(path.join(REPO, 'assets/shots', n))) !== SEAL[n]);
  check('[캡처] 배포본 webp = 촬영 봉인 sha256 (' + shots.length + '종)',
        shots.length > 0 && sealBad.length === 0, sealBad.join(', '));

  const vs = spawnSync('node', [path.join(__dirname, 'verify_shots.js')],
                       {encoding: 'utf8', env: Object.assign({}, process.env, {DST_REPO: REPO})});
  const vsTail = String(vs.stdout || '').split('\n').filter(l => /FAIL|판정 /.test(l)).slice(-4).join(' | ');
  check('[캡처] verify_shots.js 전건 통과', vs.status === 0, 'exit ' + vs.status + '  ' + vsTail);
  /* D-20 — 산출물 표면에 .html 영어 파일명 노출 금지. 화면 이름으로 부른다 */
  const codeNames = (raw.match(/<code>[A-Za-z0-9._-]+\.html<\/code>/g) || []).length;
  check('[문자열] 화면 파일명 노출 0건 (D-20)', codeNames === 0, codeNames + '건');

  /* ── B. DOM 검사 — 창 없이 실제로 띄운다 ──────────────────────────── */
  await new Promise(r => server.listen(PORT, r));
  const TARGET = URL_IN || ('http://127.0.0.1:' + PORT + '/index.html');
  console.log('게이트 대상:', TARGET);
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'gg-'));
  const chrome = spawn(CHROME, ['--headless=new', '--remote-debugging-port=' + DPORT,
    CHROME_DL.args(PH_DL, profile)[0] /* '--user-data-dir=' + profile */, '--no-first-run', '--no-default-browser-check',
    '--disable-gpu', '--hide-scrollbars', '--window-size=1440,1287', 'about:blank'], {stdio:'ignore'});

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
  ws = new WebSocket(targets.find(x => x.type === 'page').webSocketDebuggerUrl);
  await new Promise(r => ws.addEventListener('open', r));
  ws.addEventListener('message', e => {
    const m = JSON.parse(e.data);
    if(m.id && pending.has(m.id)){ pending.get(m.id).res(m.result); pending.delete(m.id); return; }
    if(m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error')
      consoleErrors.push('console: ' + m.params.args.map(a => a.value || a.description || a.type).join(' '));
    if(m.method === 'Runtime.exceptionThrown')
      consoleErrors.push('exception: ' + String((m.params.exceptionDetails.exception || {}).description || m.params.exceptionDetails.text));
    if(m.method === 'Log.entryAdded' && m.params.entry.level === 'error' && !/favicon/.test(m.params.entry.url || ''))
      consoleErrors.push('log: ' + m.params.entry.text + ' ' + (m.params.entry.url || ''));
  });
  await send('Runtime.enable'); await send('Log.enable'); await send('Page.enable'); await send('Network.enable');

  const codes = new Map();
  ws.addEventListener('message', e => {
    const m = JSON.parse(e.data);
    if(m.method === 'Network.responseReceived') codes.set(m.params.response.url, m.params.response.status);
  });

  await send('Page.navigate', {url: TARGET});
  await sleep(2500);
  await ev("document.querySelectorAll('img[loading=lazy]').forEach(function(i){i.loading='eager';}); return 1;");
  await ev("window.scrollTo(0,document.body.scrollHeight); return 1;"); await sleep(1800);
  await ev("window.scrollTo(0,0); return 1;"); await sleep(900);

  check('index.html 200', (codes.get(TARGET) || codes.get(TARGET + '/')) === 200, String(codes.get(TARGET)));

  const cards = await ev(`
    var c=[].slice.call(document.querySelectorAll('article.term'));
    var need=${JSON.stringify(FIELDS)};
    var bad=c.filter(function(x){return need.some(function(f){return !x.querySelector('[data-field="'+f+'"]');});})
             .map(function(x){return x.id;});
    return {n:c.length, missing:bad};`);
  check('용어 카드 ' + CARDS + '건', cards.n === CARDS, cards.n + '건');
  check('카드마다 data-field 5종', cards.missing.length === 0, cards.missing.slice(0, 5).join(', '));

  const images = await ev(`
    var im=[].slice.call(document.querySelectorAll('img')).filter(function(i){return i.getAttribute('src');});
    return {n:im.length, broken:im.filter(function(i){return !i.complete||i.naturalWidth===0;})
      .map(function(i){return i.getAttribute('src');})};`);
  check('이미지 전건 로드 (' + images.n + '개)', images.n >= CARDS && images.broken.length === 0,
        images.broken.slice(0, 4).join(', '));

  /* S3 — 화면이 실제로 물고 있는 그림의 바이트를 받아 촬영 봉인과 맞춘다.
     파일이 제자리에 있어도 페이지가 다른 것을 부르면 여기서 갈린다.
     --url 로 배포본을 볼 때도 같은 판정이 돈다(그때는 서버가 준 실물 바이트다). */
  const live = await evA(`
    var s=[].slice.call(document.querySelectorAll('img[src*="assets/shots/"],[data-shot]'))
      .map(function(e){return e.getAttribute('src')||e.getAttribute('data-shot');})
      .filter(function(v){return v && v.indexOf('assets/shots/')>=0;});
    s=s.filter(function(v,i,a){return a.indexOf(v)===i;});
    return Promise.all(s.map(function(u){
      return fetch(u).then(function(r){return r.arrayBuffer();})
        .then(function(b){return crypto.subtle.digest('SHA-256', b);})
        .then(function(h){ return {u:u, sha:Array.prototype.map.call(new Uint8Array(h),
          function(x){return ('0'+x.toString(16)).slice(-2);}).join('')}; })
        .catch(function(e){ return {u:u, sha:'ERR:'+e}; });
    }));`);
  const liveBad = live.filter(x => SEAL[x.u.split('/').pop()] !== x.sha)
                      .map(x => x.u.split('/').pop() + ' ' + String(x.sha).slice(0, 12));
  check('[캡처] 화면이 부른 이미지 바이트 = 촬영 봉인 (' + live.length + '종)',
        live.length > 0 && liveBad.length === 0, liveBad.join(', '));

  const anchors = await ev(`
    var a=[].slice.call(document.querySelectorAll('a[href^="#"]'));
    var dead=[];
    a.forEach(function(x){ var h=x.getAttribute('href').slice(1); if(!h) return;
      if(!document.getElementById(h)) dead.push(h); });
    return {n:a.length, dead:Array.from(new Set(dead))};`);
  check('페이지 안 앵커 전건 도달 (' + anchors.n + '개)', anchors.dead.length === 0, anchors.dead.slice(0, 6).join(', '));

  const esc = await ev(`
    var out={outside:[], offsite:[], total:0};
    [].slice.call(document.querySelectorAll('a[href],area[href],form[action],link[href]')).forEach(function(e){
      var h=e.getAttribute('href')||e.getAttribute('action')||'';
      out.total++;
      if(/^(#|assets\\/|https:\\/\\/fonts\\.googleapis\\.com|https:\\/\\/fonts\\.gstatic\\.com)/.test(h)) return;
      var u; try{ u=new URL(h, location.href); }catch(err){ out.outside.push(h); return; }
      if(u.origin!==location.origin){ out.offsite.push(u.host); return; }
      out.outside.push(h+' -> '+u.pathname);
    });
    out.offsite=out.offsite.filter(function(v,i,a){return a.indexOf(v)===i;});
    return out;`);
  check('[DOM] 바깥 링크 0', esc.outside.length === 0, esc.outside.slice(0, 6).join(' | '));
  check('[DOM] 허용 밖 외부 호스트 0', esc.offsite.length === 0, esc.offsite.join(','));
  console.log('       (링크·자산 참조 총 ' + esc.total + '건 — 전부 해시·assets·Google Fonts)');

  const dtitle = await ev("return {t:document.title, alt:!!document.querySelector('.tb-alt')};");
  check('[DOM] <title> = ' + TITLE, dtitle.t === TITLE, dtitle.t);
  check('[DOM] .tb-alt 요소 0', dtitle.alt === false);

  check('콘솔 에러 0', consoleErrors.length === 0, consoleErrors.slice(0, 3).join(' | '));

  console.log(fails.length ? '\n게이트 실패 ' + fails.length + '건: ' + fails.join(', ')
                           : '\n게이트 통과 — 바깥으로 나가는 통로 0건.');
  try{ ws.close(); }catch(e){}
  try{ chrome.kill('SIGKILL'); }catch(e){}
  try{ server.close(); }catch(e){}
  await sleep(300);
  try{ fs.rmSync(profile, {recursive:true, force:true, maxRetries:5, retryDelay:200}); }catch(e){}
  process.exit(fails.length ? 1 : 0);
}
main().catch(e => { console.error('GATE ERROR', e); process.exit(1); });
