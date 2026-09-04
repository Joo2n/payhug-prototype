/* 통합본 app.html 상태 동결 — 헤드리스 크롬(--headless=new) + CDP. 창을 띄우지 않는다.
   prep_fig.py freeze 가 부른다.
     인자   : <원본 레포 경로>   (정적 서빙만 — 읽기 전용)
     stdin  : JSON [{name, screen, state, js, label}]
     stdout : JSON {name: {html, view, state, toastHidden}}
   상태를 go()·상태 변수·ACT[] 로 만든 뒤 DOM 을 낱장 HTML 로 직렬화한다.
   직렬화 전에 value·checked·selected 를 속성으로 옮긴다 — 이 셋은 속성에 반영되지 않는
   상태값이라 outerHTML 에 실리지 않는다. 스크립트·숨은 section·숨은 모달은 뺀다 —
   스크립트는 부팅 때 해시(#figmacapture=…)를 화면 id 로 읽어 기본 화면으로 되돌리므로
   캡처 해시와 충돌한다. CDP 배선은 verify_app.js 와 같다. */
const http = require('http');
const fs   = require('fs');
const path = require('path');
const os   = require('os');
const { spawn } = require('child_process');

const REPO = process.argv[2];
const SPEC = JSON.parse(fs.readFileSync(0, 'utf8'));
const PORT = 8800 + (process.pid % 90), DPORT = 9500 + (process.pid % 90);
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const MIME = {'.html':'text/html; charset=utf-8', '.css':'text/css; charset=utf-8', '.js':'text/javascript',
  '.png':'image/png', '.txt':'text/plain; charset=utf-8'};

const server = http.createServer((req, res) => {
  const p = path.join(REPO, decodeURIComponent(req.url.split('?')[0].split('#')[0]));
  fs.readFile(p, (e, b) => {
    if(e){ res.writeHead(404); res.end('nope'); return; }
    res.writeHead(200, {'Content-Type': MIME[path.extname(p)] || 'application/octet-stream'});
    res.end(b);
  });
});

let msgId = 0, ws, pending = new Map();
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

const SERIALIZE = `
  var label = LABEL;
  Array.prototype.forEach.call(document.querySelectorAll('input'), function(el){
    var t = el.type;
    if(t === 'checkbox' || t === 'radio'){ if(el.checked) el.setAttribute('checked', ''); else el.removeAttribute('checked'); }
    else if(t !== 'button' && t !== 'submit'){ if(el.value !== '') el.setAttribute('value', el.value); else el.removeAttribute('value'); }
  });
  Array.prototype.forEach.call(document.querySelectorAll('select'), function(s){
    Array.prototype.forEach.call(s.options, function(o){ if(o.selected) o.setAttribute('selected', ''); else o.removeAttribute('selected'); });
  });
  var c = document.documentElement.cloneNode(true);
  Array.prototype.forEach.call(c.querySelectorAll('script, section.screen[hidden], .modal-backdrop[hidden]'), function(e){ e.remove(); });
  var t = c.querySelector('title'); if(t) t.textContent = 'PayHug Admin \\u2014 ' + label;
  var sec = document.querySelector('section.screen:not([hidden])');
  var toast = document.querySelector('[data-mount="toast"]');
  return {html: '<!doctype html>\\n' + c.outerHTML, view: document.body.dataset.view,
          state: sec ? sec.dataset.state : null, toastHidden: toast ? !!toast.hidden : true,
          visibleModals: document.querySelectorAll('.modal-backdrop:not([hidden])').length};
`;

async function main(){
  await new Promise(r => server.listen(PORT, r));
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'phfreeze-'));
  const chrome = spawn(CHROME, ['--headless=new', '--remote-debugging-port=' + DPORT,
    '--user-data-dir=' + profile, '--no-first-run', '--no-default-browser-check',
    '--disable-gpu', '--hide-scrollbars', '--lang=ko-KR', '--window-size=1440,1800', 'about:blank'], {stdio:'ignore'});
  const out = {};
  try {
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
    if(!targets) throw new Error('CDP 연결 실패');
    const page = targets.find(t => t.type === 'page');
    ws = new WebSocket(page.webSocketDebuggerUrl);
    await new Promise(r => ws.addEventListener('open', r));
    ws.addEventListener('message', ev => {
      const m = JSON.parse(ev.data);
      if(m.id && pending.has(m.id)){ pending.get(m.id).res(m.result); pending.delete(m.id); }
    });
    await send('Runtime.enable'); await send('Page.enable');
    await send('Page.navigate', {url:'http://127.0.0.1:' + PORT + '/app.html'});
    let ready = false;
    for(let i = 0; i < 50 && !ready; i++){
      await sleep(300);
      try { ready = await evalJS("return typeof go === 'function' && !!document.body.dataset.view;"); } catch(e){ ready = false; }
    }
    if(!ready) throw new Error('app.html 부팅 대기 초과');
    await evalJS('return document.fonts.ready.then(function(){ return 1; });');
    await sleep(400);

    for(const s of SPEC){
      await evalJS('go(' + JSON.stringify(s.screen) + ', ' + JSON.stringify(s.state) + '); return 1;');
      await sleep(120);
      if(s.js) await evalJS(s.js + ' return 1;');
      await sleep(350);
      out[s.name] = await evalJS(SERIALIZE.replace('LABEL', JSON.stringify(s.label || s.screen)));
    }
  } finally {
    try { ws && ws.close(); } catch(e){}
    try { chrome.kill('SIGKILL'); } catch(e){}
    server.close();
    await sleep(300);
    try { fs.rmSync(profile, {recursive:true, force:true}); } catch(e){}
  }
  process.stdout.write(JSON.stringify(out));
}
main().catch(e => { process.stderr.write(String(e && e.stack || e) + '\n'); process.exit(1); });
