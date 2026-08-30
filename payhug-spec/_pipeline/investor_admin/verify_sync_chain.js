#!/usr/bin/env node
/* 동기화 사슬 검사기 — 정본(payhug-investor-admin) 대 배포 3주소
 *
 *   payhug-investor-admin (정본)
 *     ├ app.html      ──sync_prototype.py──▶ payhug-investor-prototype ──▶ prototype.vercel.app
 *     ├ glossary.html ──sync_glossary.py───▶ payhug-investor-glossary  ──▶ glossary.vercel.app
 *     └ 전체          ──git push──────────▶ payhug-investor-demo.vercel.app
 *
 * A 응답   익명 HTTP 코드·바이트·Vercel 차단 여부
 * B 표식   렌더 후 본문에서 있어야 할 것 / 없어야 할 것
 * C 정본   로컬 app.html·glossary.html 을 같은 방법으로 재보고 배포본과 대조
 * D 실조작 사이드바 8메뉴 · 쿠콘 외부링크 · 보기 갯수 select · 기간 3단 pf-gran
 *
 * 표식·숫자는 아래 상수만 고치면 된다.
 *
 *   node verify_sync_chain.js                 3주소 + 정본 전부
 *   node verify_sync_chain.js --only=gloss    한 주소만 (proto|gloss|demo)
 *   node verify_sync_chain.js --rounds=12 --gap=90    수렴할 때까지 되돌기
 *   node verify_sync_chain.js --out=result.json
 *
 * 종료코드 0=전건 통과, 1=어긋남 남음.
 */
'use strict';
const http = require('http'), fs = require('fs'), path = require('path'), os = require('os');
const { spawn } = require('child_process');

/* ══════════════ 상수 — 여기만 고친다 ══════════════ */

const URLS = {
  proto: 'https://payhug-investor-prototype.vercel.app/',
  gloss: 'https://payhug-investor-glossary.vercel.app/',
  demo:  'https://payhug-investor-demo.vercel.app/'
};
/* 통합본은 랜딩 갤러리라 실제 화면은 하위 경로에 있다 */
const DEMO_APP   = 'https://payhug-investor-demo.vercel.app/app.html';
const DEMO_GLOSS = 'https://payhug-investor-demo.vercel.app/glossary.html';

const ADMIN = process.env.ADMIN_REPO || '/Users/semi/cursor/payhug-investor-admin';
const OUTDIR = '/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin';
/* 숫자 기대값은 검증기에 손으로 적지 않는다 — daily_ledger.py 가 내는 원장 사실값을 읽는다.
   verify_identity.js:13 · verify_proto.js:14 · verify_period.js:14 와 같은 원천이다. */
const FACTS = JSON.parse(fs.readFileSync(path.join(OUTDIR, 'ledger_facts.json'), 'utf8'));
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 ' +
           '(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36';

/* 시연·통합 화면(app.html 계열) — 전 화면·전 상태를 순회해 모은 본문에서 본다 */
const W_DAYS = FACTS.weekW;       /* W금융일수 계열 — 기본 조회기간(일주일) 합계 행 */
const APP_MUST     = ['주별', '12주', '계약서보기', '하나인증서', W_DAYS, '10개'];
const APP_MUST_NOT = ['예시값', '표시 1-', '확인필요', '용어 안내', 'coocon--confirm'];

/* 쿠콘 화면 — 아이콘 + 버튼 하나뿐이어야 한다 */
const COOCON_MUST     = ['We-bank 바로가기'];
const COOCON_MUST_NOT = ['전자금융서비스에서 조회', '조회 가능한 내역', '기관코드', 'OTP'];

/* 용어 해설 */
const GLOSS_MUST     = ['가중평균만기', 'Duration', '케이뱅크', '목차'];
const GLOSS_MUST_NOT = ['카드 한 장', '값의 출처', '용어 50건', '관리자 어드민'];
/* 용어판에서 href·action 안에 나오면 안 되는 형제 문서 (본문 <code> 표기는 내용이라 허용 — sync_glossary.py 와 같은 규칙) */
const GLOSS_BANNED_HREF = ['app.html', 'capability.html', 'feasibility.html', 'inquiry.html',
                           'archive.html', 'review.html', 'glossary-legacy.html'];

/* 숫자 불변식 — 렌더된 본문에 그대로 있어야 한다.
   투자실행액·순현금·투자자산은 원장 사실값에서 읽는다. 비중 합 100.0% 는 원장과 무관한
   항등식이라 그대로 둔다(ratios() 가 최대 항에 잔차를 몰아 항상 100.0 이 된다). */
const NUMS = [FACTS.exec, FACTS.cash, FACTS.total].map(v => Number(v).toLocaleString('en-US'))
             .concat(['100.0%']);
const ROSTER_ROWS = FACTS.merchants.length;   /* 가맹점 로스터 건수 — 현재 corpus 판정에서 참조하지 않는다 */

/* 정본 대비 시연본이 의도적으로 덜어 내는 화면 — 이 둘만 빠져도 정상 */
const PROTO_DROPPED = ['index'];

/* 시연본 selfcheck 대조에서 뺄 항목 — 의도적 축소로 반드시 달라진다 */
const SELFCHECK_SKIP = ['screens', 'states'];
/* 시연본에 남아도 되는 자기 참조 링크 (사이드바 로고 → 자기 자신) */
const SELF_LINK_OK = ['index.html'];

/* 사이드바 메뉴 수는 박지 않는다 — 정본 app.html 을 계측해 채운다(canonApp.navMenus).
   정본을 재지 못했을 때만 아래 기본값을 쓴다. */
let SIDEBAR_MENUS = 8;
const PERIOD_GRAN = 3;       /* 기간 3단 토글 */

/* ══════════════ 도구 ══════════════ */

const sleep = ms => new Promise(r => setTimeout(r, ms));
const arg = k => { const a = process.argv.find(x => x.startsWith('--' + k + '=')); return a ? a.slice(k.length + 3) : ''; };
const has = k => process.argv.indexOf('--' + k) >= 0;

function log(s) { console.log(s); }
function mark(pass) { return pass ? 'PASS' : 'FAIL'; }

/* A — 익명 HTTP. Vercel 봇 차단(x-vercel-mitigated: challenge)을 200 과 구분한다. */
async function probeHttp(url) {
  const t0 = Date.now();
  try {
    const r = await fetch(url, { headers: { 'user-agent': UA, accept: 'text/html' }, redirect: 'follow' });
    const body = await r.text();
    const mit = r.headers.get('x-vercel-mitigated') || '';
    const title = (body.match(/<title[^>]*>([\s\S]*?)<\/title>/i) || [, ''])[1].trim();
    return {
      url, status: r.status, bytes: Buffer.byteLength(body), ms: Date.now() - t0,
      mitigated: mit, challenge: mit === 'challenge' || /Vercel Security Checkpoint/i.test(title),
      title, age: r.headers.get('age') || '', cache: r.headers.get('x-vercel-cache') || '',
      md5: require('crypto').createHash('md5').update(body).digest('hex')
    };
  } catch (e) {
    return { url, status: 0, bytes: 0, ms: Date.now() - t0, error: String(e && e.message || e), challenge: false };
  }
}

/* 로컬 정적 서버 — 정본을 같은 방법으로 재기 위해 */
const MIME = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
  '.png': 'image/png', '.webp': 'image/webp', '.svg': 'image/svg+xml', '.pdf': 'application/pdf', '.zip': 'application/zip',
  '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' };
function serve(root) {
  return http.createServer((req, res) => {
    const p = path.join(root, decodeURIComponent(req.url.split('?')[0]));
    fs.readFile(p, (e, b) => {
      if (e) { res.writeHead(404); res.end('404'); return; }
      res.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' });
      res.end(b);
    });
  });
}

/* CDP 최소 클라이언트 */
class Cdp {
  constructor() { this.id = 0; this.pending = new Map(); this.consoleErrors = []; }
  async launch(port) {
    this.profile = fs.mkdtempSync(path.join(os.tmpdir(), 'vsc-'));
    this.dl = fs.mkdtempSync(path.join(os.tmpdir(), 'vsc-dl-'));
    /* macOS 함정 — --window-size=1440,H 는 실제 뷰포트 1440×(H-87). 1287 로 1440×1200 을 얻는다. */
    this.proc = spawn(CHROME, ['--headless=new', '--remote-debugging-port=' + port,
      '--user-data-dir=' + this.profile, '--no-first-run', '--no-default-browser-check',
      '--disable-gpu', '--window-size=1440,1287', '--user-agent=' + UA, 'about:blank'], { stdio: 'ignore' });
    let targets = null;
    for (let i = 0; i < 80 && !targets; i++) {
      await sleep(300);
      try {
        targets = await new Promise((res, rej) => {
          http.get({ host: '127.0.0.1', port, path: '/json' }, r => {
            let d = ''; r.on('data', c => d += c); r.on('end', () => res(JSON.parse(d)));
          }).on('error', rej);
        });
      } catch (e) { targets = null; }
    }
    if (!targets) throw new Error('Chrome 이 안 떴다');
    this.ws = new WebSocket(targets.find(t => t.type === 'page').webSocketDebuggerUrl);
    await new Promise(r => this.ws.addEventListener('open', r));
    this.ws.addEventListener('message', e => {
      const m = JSON.parse(e.data);
      if (m.id && this.pending.has(m.id)) { this.pending.get(m.id).res(m.result); this.pending.delete(m.id); return; }
      if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error')
        this.consoleErrors.push(m.params.args.map(a => a.value || a.description || a.type).join(' '));
      if (m.method === 'Runtime.exceptionThrown')
        this.consoleErrors.push(String((m.params.exceptionDetails.exception || {}).description || m.params.exceptionDetails.text));
    });
    await this.send('Runtime.enable'); await this.send('Page.enable'); await this.send('Log.enable');
    await this.send('Browser.setDownloadBehavior', { behavior: 'allow', downloadPath: this.dl });
  }
  send(m, p) { const id = ++this.id; this.ws.send(JSON.stringify({ id, method: m, params: p || {} })); return new Promise(res => this.pending.set(id, { res })); }
  async ev(x) {
    const r = await this.send('Runtime.evaluate', { expression: '(function(){' + x + '})()', returnByValue: true, awaitPromise: true });
    if (r && r.exceptionDetails) return { __err: JSON.stringify((r.exceptionDetails.exception || {}).description || r.exceptionDetails.text) };
    return r && r.result ? r.result.value : null;
  }
  async goto(url, wait) { this.consoleErrors.length = 0; await this.send('Page.navigate', { url }); await sleep(wait || 2600); }
  /* 실제 마우스 이벤트 — DOM 클릭이 아니라 CDP 입력 */
  async clickAt(x, y) {
    for (const type of ['mousePressed', 'mouseReleased'])
      await this.send('Input.dispatchMouseEvent', { type, x, y, button: 'left', clickCount: 1, buttons: type === 'mousePressed' ? 1 : 0 });
    await sleep(320);
  }
  async clickSel(sel, nth) {
    const box = await this.ev(`var e=document.querySelectorAll(${JSON.stringify(sel)})[${nth || 0}];if(!e)return null;
      e.scrollIntoView({block:'center'});var r=e.getBoundingClientRect();
      return (r.width>0&&r.height>0)?{x:r.left+r.width/2,y:r.top+r.height/2}:null;`);
    if (!box || box.__err) return false;
    await this.clickAt(box.x, box.y);
    return true;
  }
  kill() { try { this.proc.kill(); } catch (e) {} }
}

/* ══════════════ B·C·D — 화면 계측 ══════════════ */

/* app.html 계열: 전 화면·전 상태를 돌며 본문을 모으고, 실조작 4종을 친다. */
const APP_PROBE = `
  if(typeof SCREEN_ORDER === 'undefined') return {kind:'not-app', title:document.title, text:document.body.innerText.slice(0,400)};
  var out = {kind:'app', title:document.title, screens:SCREEN_ORDER.slice(), states:{}, corpus:'', bad:[]};
  try { out.selfcheck = window.__selfcheck ? window.__selfcheck() : null; } catch(e){ out.selfcheck = {err:String(e)}; }
  SCREEN_ORDER.forEach(function(sc){
    var meta = (typeof STATE_META !== 'undefined' && STATE_META[sc]) || {'default':null};
    out.states[sc] = Object.keys(meta);
    Object.keys(meta).forEach(function(st){
      try { go(sc, st); } catch(e){ out.bad.push(sc+'/'+st+' go() '+e); return; }
      var sec = document.querySelector('section.screen[data-screen="'+sc+'"]');
      var h = sec ? sec.getBoundingClientRect().height : 0;
      if(!sec || sec.hidden || sec.dataset.state !== st || h < 200)
        out.bad.push(sc+'/'+st+' hidden='+(sec?sec.hidden:'없음')+' state='+(sec?sec.dataset.state:'-')+' h='+Math.round(h));
      out.corpus += '\\n<<'+sc+'/'+st+'>>\\n' + (sec ? (sec.innerText + ' ' + sec.textContent.replace(/\\s+/g,' ')) : '');
    });
  });
  out.corpusLen = out.corpus.length;
  out.navMenus = document.querySelectorAll('.sidebar .nav-item[data-menu]').length;
  out.navList = Array.prototype.map.call(document.querySelectorAll('.sidebar .nav-item[data-menu]'), function(a){ return a.dataset.menu; });
  /* 쿠콘 화면 — 아이콘 + 링크 하나뿐인지 */
  go('coocon','default');
  var cs = document.querySelector('section.screen[data-screen="coocon"]');
  out.cooconText = cs ? cs.innerText : '';
  out.cooconLinks = cs ? Array.prototype.map.call(cs.querySelectorAll('a[href]'), function(a){ return a.getAttribute('href'); }) : [];
  out.cooconBtns = cs ? cs.querySelectorAll('a.btn, button').length : -1;
  out.cooconIcons = cs ? cs.querySelectorAll('svg').length : -1;
  /* 보기 갯수 select */
  go('merchants','default');
  var sels = document.querySelectorAll('select[data-act="pg-size"]');
  out.sizeSelectors = sels.length;
  out.sizeOptions = sels.length ? Array.prototype.map.call(sels[0].options, function(o){ return o.textContent; }) : [];
  /* 기간 3단 */
  go('invest-profit','default');
  var g = document.querySelectorAll('[data-act="pf-gran"]');
  out.granCount = g.length;
  out.granLabels = Array.prototype.map.call(g, function(e){ return (e.textContent||'').trim(); });
  /* 외부로 나가는 링크 전수 */
  out.extLinks = Array.prototype.filter.call(document.querySelectorAll('a[href]'), function(a){
    return /^https?:/i.test(a.getAttribute('href'));
  }).map(function(a){ return a.getAttribute('href'); });
  /* 형제 문서 상대링크가 남았는가 (시연본에서는 0 이어야 한다) */
  out.siblingLinks = Array.prototype.filter.call(document.querySelectorAll('a[href],form[action]'), function(e){
    var v = e.getAttribute('href') || e.getAttribute('action') || '';
    return /\\.html(\\?|#|$)/i.test(v);
  }).map(function(e){ return (e.getAttribute('href') || e.getAttribute('action')) + (e.dataset.nav ? ' [data-nav=' + e.dataset.nav + ']' : ''); });
  go('invest-assets','default');
  return out;
`;

const GLOSS_PROBE = `
  var out = {kind:'gloss', title:document.title};
  /* innerText 는 접힌·숨은 절을 빼먹는다 — 표식은 textContent(전문)로 본다 */
  out.text = document.body.textContent.replace(/\s+/g,' ');
  out.visible = document.body.innerText;
  out.textLen = out.visible.length;
  out.cards = document.querySelectorAll('[data-k]').length;
  out.hrefs = Array.prototype.map.call(document.querySelectorAll('a[href],form[action]'), function(e){
    return e.getAttribute('href') || e.getAttribute('action'); });
  out.badHref = out.hrefs.filter(function(h){ return h && /\\.html(\\?|#|$)/i.test(h); });
  out.extHref = out.hrefs.filter(function(h){ return h && /^https?:/i.test(h); });
  out.toc = document.querySelectorAll('.toc a, nav a[href^="#"]').length;
  return out;
`;

function scan(text, must, mustNot) {
  const found = {}, leaked = {};
  must.forEach(m => { found[m] = (text.split(m).length - 1); });
  mustNot.forEach(m => { leaked[m] = (text.split(m).length - 1); });
  const missing = must.filter(m => found[m] === 0);
  const present = mustNot.filter(m => leaked[m] > 0);
  return { found, leaked, missing, present, ok: missing.length === 0 && present.length === 0 };
}

/* ══════════════ 라운드 ══════════════ */

async function round(n) {
  const R = { round: n, at: new Date().toISOString(), http: {}, checks: [], fails: [] };
  const only = arg('only');
  const want = k => !only || only === k;
  const add = (name, pass, detail) => {
    R.checks.push({ name, pass, detail });
    if (!pass) R.fails.push(name + (detail ? ' — ' + detail : ''));
    log('  ' + mark(pass) + '  ' + name + (detail === undefined ? '' : '  ' + detail));
  };

  /* ── A ─────────────────────────────── */
  log('\n[A] 익명 응답');
  for (const k of Object.keys(URLS)) {
    if (!want(k)) continue;
    const p = await probeHttp(URLS[k] + '?vsc=' + Date.now());
    R.http[k] = p;
    add('A ' + k + ' 익명 200',
      p.status === 200 && !p.challenge,
      'code=' + p.status + ' bytes=' + p.bytes + (p.challenge ? ' ★Vercel 검문소(' + p.mitigated + ')' : '') +
      (p.age ? ' age=' + p.age + 's' : '') + (p.cache ? ' cache=' + p.cache : ''));
  }
  if (want('demo')) {
    for (const [nm, u] of [['demo/app.html', DEMO_APP], ['demo/glossary.html', DEMO_GLOSS]]) {
      const p = await probeHttp(u);
      R.http[nm] = p;
      add('A ' + nm, p.status === 200 && !p.challenge, 'code=' + p.status + ' bytes=' + p.bytes);
    }
  }

  /* ── 브라우저 ───────────────────────── */
  const cdp = new Cdp();
  const port = 9200 + (process.pid % 90);
  await cdp.launch(port);
  const srv = serve(ADMIN);
  const sport = 8700 + (process.pid % 90);
  await new Promise(r => srv.listen(sport, r));
  const LOCAL = 'http://127.0.0.1:' + sport + '/';

  try {
    /* ── C 기준선: 정본 계측 ───────────── */
    log('\n[C] 정본 계측 (' + ADMIN + ')');
    await cdp.goto(LOCAL + 'app.html', 3200);
    const canonApp = await cdp.ev(APP_PROBE);
    add('C 정본 app.html 계측', !!(canonApp && canonApp.kind === 'app'),
      canonApp && canonApp.kind === 'app'
        ? canonApp.screens.length + '화면 · 상태합 ' + Object.keys(canonApp.states).reduce((a, k) => a + canonApp.states[k].length, 0) +
          ' · 본문 ' + canonApp.corpusLen + '자'
        : JSON.stringify(canonApp).slice(0, 200));
    await cdp.goto(LOCAL + 'glossary.html', 3000);
    const canonGloss = await cdp.ev(GLOSS_PROBE);
    add('C 정본 glossary.html 계측', !!(canonGloss && canonGloss.cards > 0),
      canonGloss ? '카드 ' + canonGloss.cards + ' · 본문 ' + canonGloss.textLen + '자' : 'null');
    if (canonApp && canonApp.navMenus > 0) SIDEBAR_MENUS = canonApp.navMenus;   /* 실측이 기준 */
    R.canon = { app: canonApp && { screens: canonApp.screens, states: canonApp.states, selfcheck: canonApp.selfcheck, corpusLen: canonApp.corpusLen, nav: canonApp.navMenus, gran: canonApp.granCount },
                gloss: canonGloss && { cards: canonGloss.cards, textLen: canonGloss.textLen, title: canonGloss.title } };
    /* 정본 자체 표식 — 여기서 빠지면 배포 탓이 아니다 */
    if (canonApp && canonApp.corpus) {
      const s = scan(canonApp.corpus, APP_MUST, APP_MUST_NOT);
      add('C 정본 app 표식', s.ok, '없음=' + JSON.stringify(s.missing) + ' 새어나옴=' + JSON.stringify(s.present));
      R.canonAppScan = s;
      const sn = NUMS.filter(x => canonApp.corpus.indexOf(x) < 0);
      add('C 정본 숫자 불변식', sn.length === 0, sn.length ? '없음=' + JSON.stringify(sn) : NUMS.join(' · '));
    }
    if (canonGloss && canonGloss.text) {
      const s = scan(canonGloss.text, GLOSS_MUST, GLOSS_MUST_NOT);
      add('C 정본 용어 표식', s.ok, '없음=' + JSON.stringify(s.missing) + ' 새어나옴=' + JSON.stringify(s.present));
      R.canonGlossScan = s;
    }

    /* ── 시연 배포본 ───────────────────── */
    if (want('proto')) {
      log('\n[B·D] 시연 배포본');
      await cdp.goto(URLS.proto + '?vsc=' + Date.now(), 4200);
      const d = await cdp.ev(APP_PROBE);
      R.proto = d;
      if (!d || d.kind !== 'app') {
        add('B 시연 앱 로드', false, '앱이 아니다 — title=' + (d && d.title) + ' / ' + String(d && d.text).slice(0, 90));
      } else {
        const s = scan(d.corpus, APP_MUST, APP_MUST_NOT);
        add('B 시연 표식', s.ok, '없음=' + JSON.stringify(s.missing) + ' 새어나옴=' + JSON.stringify(s.present));
        const cs = scan(d.cooconText, COOCON_MUST, COOCON_MUST_NOT);
        add('B 시연 쿠콘 화면', cs.ok && d.cooconLinks.length === 1 && /we-bank/i.test(d.cooconLinks[0] || ''),
          '링크=' + JSON.stringify(d.cooconLinks) + ' 없음=' + JSON.stringify(cs.missing) + ' 새어나옴=' + JSON.stringify(cs.present));
        const nm = NUMS.filter(x => d.corpus.indexOf(x) < 0);
        add('B 시연 숫자 불변식', nm.length === 0, nm.length ? '없음=' + JSON.stringify(nm) : 'OK');
        /* C — 정본 대조 */
        if (canonApp && canonApp.kind === 'app') {
          const expect = canonApp.screens.filter(x => PROTO_DROPPED.indexOf(x) < 0);
          const missScreen = expect.filter(x => d.screens.indexOf(x) < 0);
          const extra = d.screens.filter(x => canonApp.screens.indexOf(x) < 0);
          add('C 시연 화면 구성', missScreen.length === 0 && extra.length === 0,
            '정본 ' + canonApp.screens.length + ' → 시연 ' + d.screens.length +
            ' (의도적 제거 ' + JSON.stringify(PROTO_DROPPED) + ')' +
            (missScreen.length ? ' 빠짐=' + JSON.stringify(missScreen) : '') + (extra.length ? ' 초과=' + JSON.stringify(extra) : ''));
          const stDiff = Object.keys(canonApp.states).filter(k => PROTO_DROPPED.indexOf(k) < 0)
            .filter(k => JSON.stringify(canonApp.states[k]) !== JSON.stringify(d.states[k]));
          add('C 시연 상태 구성', stDiff.length === 0, stDiff.length ? '다름=' + JSON.stringify(stDiff) : '전건 일치');
          /* selfcheck 의 screens·states 는 의도적 축소(PROTO_DROPPED)로 달라진다 —
             그 둘은 위의 '화면 구성'·'상태 구성' 검사가 따로 본다. 숫자 불변식만 여기서 맞춘다. */
          const cf = canonApp.selfcheck || {}, df = d.selfcheck || {};
          const numDiff = Object.keys(cf).filter(k => SELFCHECK_SKIP.indexOf(k) < 0)
            .filter(k => JSON.stringify(cf[k]) !== JSON.stringify(df[k]));
          add('C 시연 selfcheck 일치', numDiff.length === 0,
            numDiff.length ? numDiff.map(k => k + ': 정본 ' + JSON.stringify(cf[k]) + ' ≠ 시연 ' + JSON.stringify(df[k])).join(' / ')
                           : Object.keys(df).filter(k => SELFCHECK_SKIP.indexOf(k) < 0).map(k => k + '=' + JSON.stringify(df[k])).join(' '));
        }
        add('D 사이드바 메뉴 ' + SIDEBAR_MENUS + '개', d.navMenus === SIDEBAR_MENUS, d.navMenus + '개 ' + JSON.stringify(d.navList));
        add('D 기간 ' + PERIOD_GRAN + '단 토글', d.granCount === PERIOD_GRAN, d.granCount + '개 ' + JSON.stringify(d.granLabels));
        add('D 보기 갯수 select', d.sizeSelectors > 0 && d.sizeOptions.indexOf('10개') >= 0,
          'select ' + d.sizeSelectors + '개 ' + JSON.stringify(d.sizeOptions));
        /* 사이드바 로고의 index.html 은 자기 자신을 가리킨다(data-nav 로 JS 가 가로챈다) —
           sync_prototype.py 가 남기기로 한 것이라 형제 문서 유출이 아니다. */
        const sib = d.siblingLinks.filter(h => !SELF_LINK_OK.some(x => String(h).indexOf(x) >= 0));
        add('D 형제 문서 링크 0건', sib.length === 0,
          JSON.stringify(sib.slice(0, 6)) + (d.siblingLinks.length ? ' (자기참조 허용 ' + JSON.stringify(d.siblingLinks) + ')' : ''));
        /* 외부 링크는 고정 개수가 아니라 정본과 같은 집합이어야 한다.
           정본 app.html 은 사이드바 쿠콘 메뉴와 쿠콘 화면 버튼 둘 다 We-bank 로 나간다(=2건). */
        const extOf = o => (o.extLinks || []).filter(h => !/fonts\.(googleapis|gstatic)/.test(h)).sort();
        const cExt = canonApp && canonApp.kind === 'app' ? extOf(canonApp) : null;
        const dExt = extOf(d);
        add('D 외부 링크 = 정본', !cExt || JSON.stringify(cExt) === JSON.stringify(dExt),
          '정본 ' + JSON.stringify(cExt) + ' ↔ 시연 ' + JSON.stringify(dExt));
        add('D 외부 링크는 We-bank 뿐', dExt.every(h => /we-bank\.co\.kr/i.test(h)), JSON.stringify(dExt));
        /* 실제 마우스 조작 */
        /* 옛 판정 `navMoved >= SIDEBAR_MENUS - 1` 은 "한 개는 안 움직여도 봐준다" 는 곳수 예외였다.
           그 한 개의 정체는 쿠콘(`target="_blank"` 외부 링크 — 화면을 안 바꾸는 것이 맞다)인데,
           예외가 곳수로만 걸려 있어 SPA 메뉴 하나가 진짜로 죽어도 7/8 로 통과했다(2026-08-30 실측 확인).
           예외를 없애지 않고 구멍만 막는다 — 안 움직여도 되는 자리를 곳수가 아니라 속성으로 정한다.
           화면을 안 바꿔도 되는 것은 (1) 새 창으로 나가는 외부 링크 (2) 누르기 전에 이미 그 화면인 것. */
        const navBefore = await cdp.ev("return document.body.dataset.view||document.body.dataset.active;");
        const navStuck = [];
        for (let i = 0; i < SIDEBAR_MENUS; i++) {
          const meta = await cdp.ev(`var e=document.querySelectorAll('.sidebar .nav-item[data-menu]')[${i}];
            return e ? {menu:e.dataset.menu, blank:e.getAttribute('target')==='_blank'} : null;`);
          if (!meta) { navStuck.push('#' + i + ' 메뉴 없음'); continue; }
          if (meta.blank) continue;              /* 새 창으로 나가는 외부 링크는 화면을 안 바꾸는 것이 맞다 */
          /* 누르기 전에 반드시 다른 화면에 세워 둔다 — 사이드바가 아니라 주소(해시)로 옮긴다.
             이미 그 메뉴에 서 있는 상태로 누르면 죽은 메뉴도 active 가 이미 맞아 통과한다.
             옛 판정 `navMoved >= SIDEBAR_MENUS - 1` 과 그 뒤 `i === 0` 자리 예외가 다 이 구멍이었다. */
          const park = meta.menu === 'password' ? 'invest-assets' : 'password';
          await cdp.ev("location.hash=" + JSON.stringify('#' + park) + "; return 1;");
          await sleep(400);
          const before = await cdp.ev("return document.body.dataset.active||'';");
          if (before === meta.menu) { navStuck.push(meta.menu + ' — 대기 화면(' + park + ')으로 못 옮김'); continue; }
          await cdp.clickSel('.sidebar .nav-item[data-menu]', i);
          /* 「화면이 바뀌었나」가 아니라 「그 메뉴로 갔나」를 본다.
             app.html 이 스스로 body.dataset.active = MENU_OF[screen] 를 쓴다 — 앱이 선언한 계약이다. */
          const active = await cdp.ev("return document.body.dataset.active||'';");
          if (active !== meta.menu) navStuck.push(meta.menu + ' (' + before + ' → active=' + active + ')');
        }
        add('D 사이드바 실클릭 전환 — 안 움직인 SPA 메뉴 0', navStuck.length === 0,
          navStuck.length ? JSON.stringify(navStuck) : SIDEBAR_MENUS + '개 전건 반응 (시작 ' + navBefore + ' · 외부 링크는 제외)');
        await cdp.ev("go('invest-profit','default');");
        const granRes = await cdp.ev(`var g=document.querySelectorAll('[data-act="pf-gran"]');var o=[];
          for(var i=0;i<g.length;i++){g[i].click();o.push({v:g[i].dataset.gran||g[i].textContent.trim(),
            on:g[i].getAttribute('aria-pressed')||g[i].className});}return o;`);
        add('D 기간 토글 실클릭', Array.isArray(granRes) && granRes.length === PERIOD_GRAN, JSON.stringify(granRes));
        add('D 콘솔 오류 0건', cdp.consoleErrors.length === 0, JSON.stringify(cdp.consoleErrors.slice(0, 3)));
      }
    }

    /* ── 용어 배포본 ───────────────────── */
    if (want('gloss')) {
      log('\n[B·C] 용어 배포본');
      await cdp.goto(URLS.gloss + '?vsc=' + Date.now(), 3600);
      const g = await cdp.ev(GLOSS_PROBE);
      R.gloss = g && { title: g.title, cards: g.cards, textLen: g.textLen, badHref: g.badHref, extHref: g.extHref, toc: g.toc };
      if (!g || !g.text) add('B 용어 로드', false, JSON.stringify(g).slice(0, 200));
      else {
        const s = scan(g.text, GLOSS_MUST, GLOSS_MUST_NOT);
        add('B 용어 표식', s.ok, '없음=' + JSON.stringify(s.missing) + ' 새어나옴=' + JSON.stringify(s.present));
        add('B 용어 href .html 0건', g.badHref.length === 0, JSON.stringify(g.badHref.slice(0, 6)));
        if (canonGloss) {
          add('C 용어 카드 수 정본 일치', g.cards === canonGloss.cards, '정본 ' + canonGloss.cards + ' ↔ 배포 ' + g.cards);
          const drift = Math.abs(g.textLen - canonGloss.textLen);
          add('C 용어 본문 길이 근사', drift <= Math.max(200, canonGloss.textLen * 0.01),
            '정본 ' + canonGloss.textLen + ' ↔ 배포 ' + g.textLen + ' (차 ' + drift + ')');
        }
      }
    }

    /* ── 통합 배포본 ───────────────────── */
    if (want('demo')) {
      log('\n[B·C] 통합 배포본');
      await cdp.goto(DEMO_APP + '?vsc=' + Date.now(), 4200);
      const d = await cdp.ev(APP_PROBE);
      R.demoApp = d && { kind: d.kind, screens: d.screens, corpusLen: d.corpusLen, selfcheck: d.selfcheck, nav: d.navMenus, gran: d.granCount, sizeOptions: d.sizeOptions };
      if (!d || d.kind !== 'app') add('B 통합 app 로드', false, JSON.stringify(d).slice(0, 200));
      else {
        const s = scan(d.corpus, APP_MUST, APP_MUST_NOT);
        add('B 통합 표식', s.ok, '없음=' + JSON.stringify(s.missing) + ' 새어나옴=' + JSON.stringify(s.present));
        const cs = scan(d.cooconText, COOCON_MUST, COOCON_MUST_NOT);
        add('B 통합 쿠콘 화면', cs.ok, '링크=' + JSON.stringify(d.cooconLinks) + ' 새어나옴=' + JSON.stringify(cs.present));
        const nm = NUMS.filter(x => d.corpus.indexOf(x) < 0);
        add('B 통합 숫자 불변식', nm.length === 0, nm.length ? '없음=' + JSON.stringify(nm) : 'OK');
        if (canonApp && canonApp.kind === 'app') {
          const cf = canonApp.selfcheck || {}, df = d.selfcheck || {};
          const numDiff = Object.keys(cf).filter(k => JSON.stringify(cf[k]) !== JSON.stringify(df[k]));
          add('C 통합 selfcheck = 정본', numDiff.length === 0,
            numDiff.length ? numDiff.map(k => k + ': 정본 ' + JSON.stringify(cf[k]) + ' ≠ 배포 ' + JSON.stringify(df[k])).join(' / ') : 'OK');
          const scDiff = canonApp.screens.filter(x => d.screens.indexOf(x) < 0);
          add('C 통합 화면 전건', scDiff.length === 0, '정본 ' + canonApp.screens.length + ' ↔ 배포 ' + d.screens.length + (scDiff.length ? ' 빠짐=' + JSON.stringify(scDiff) : ''));
        }
        add('D 통합 사이드바 ' + SIDEBAR_MENUS + '개', d.navMenus === SIDEBAR_MENUS, String(d.navMenus));
        add('D 통합 기간 ' + PERIOD_GRAN + '단', d.granCount === PERIOD_GRAN, JSON.stringify(d.granLabels));
      }
      await cdp.goto(DEMO_GLOSS + '?vsc=' + Date.now(), 3600);
      const g = await cdp.ev(GLOSS_PROBE);
      R.demoGloss = g && { title: g.title, cards: g.cards, textLen: g.textLen };
      if (g && g.text && canonGloss) {
        const s = scan(g.text, GLOSS_MUST, GLOSS_MUST_NOT);
        add('B 통합 용어 표식', s.ok, '없음=' + JSON.stringify(s.missing) + ' 새어나옴=' + JSON.stringify(s.present));
        add('C 통합 용어 카드 = 정본', g.cards === canonGloss.cards, '정본 ' + canonGloss.cards + ' ↔ 배포 ' + g.cards);
      }
    }
  } finally {
    cdp.kill(); srv.close();
  }

  R.pass = R.fails.length === 0;
  log('\n라운드 ' + n + ' — ' + (R.pass ? '전건 통과' : R.fails.length + '건 어긋남'));
  R.fails.forEach(f => log('    · ' + f));
  return R;
}

(async () => {
  const rounds = parseInt(arg('rounds') || '1', 10);
  const gap = parseInt(arg('gap') || '90', 10) * 1000;
  const out = arg('out') || path.join(__dirname, 'verify_sync_chain_result.json');
  const all = [];
  for (let i = 1; i <= rounds; i++) {
    log('\n════════ 라운드 ' + i + '/' + rounds + '  ' + new Date().toISOString() + ' ════════');
    let r;
    try { r = await round(i); }
    catch (e) { r = { round: i, pass: false, fails: ['검사기 예외: ' + String(e && e.stack || e)] }; log('  검사기 예외 ' + e); }
    all.push(r);
    fs.writeFileSync(out, JSON.stringify({ finishedAt: new Date().toISOString(), rounds: all }, null, 1));
    if (r.pass) { log('\n▶ 수렴 — 라운드 ' + i + '에서 전건 통과'); break; }
    if (i < rounds) { log('\n… ' + (gap / 1000) + '초 대기'); await sleep(gap); }
  }
  const last = all[all.length - 1];
  log('\n결과 파일: ' + out);
  log(last.pass ? '동기화 됐다' : '동기화 안 됐다 — ' + last.fails.length + '건');
  process.exit(last.pass ? 0 : 1);
})();
