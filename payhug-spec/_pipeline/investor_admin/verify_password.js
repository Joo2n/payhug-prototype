/* 비밀번호 변경 화면 실조작 대조 — 실제 프론트(payhug-merchant-web)와 같은 문구·같은 시점에
   같은 표시가 나오는지 헤드리스로 눌러 보고 DOM 글자를 그대로 읽어 맞춰 본다.
   기대 문자열은 외우지 않는다. lib/passwordPolicy.ts 에서 뽑아 쓴다.
   결과: verify_password_result.json                                              */
const http = require('http');
const CHROME_DL = require('./chrome_dl');
const PH_DL = CHROME_DL.dir();
const fs   = require('fs');
const path = require('path');
const os   = require('os');
const { spawn } = require('child_process');

const REPO  = '/Users/semi/cursor/payhug-investor-admin';
const FRONT = '/Users/semi/cursor/payhug-merchant-web';
const OUTDIR = '/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin';
const PORT = 8700 + (process.pid % 90), DPORT = 9400 + (process.pid % 90);
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const MIME = {'.html':'text/html; charset=utf-8', '.css':'text/css; charset=utf-8', '.js':'text/javascript',
  '.png':'image/png', '.svg':'image/svg+xml', '.pdf':'application/pdf'};

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
  if(r.exceptionDetails) throw new Error('page eval: ' + JSON.stringify(
    (r.exceptionDetails.exception && r.exceptionDetails.exception.description) || r.exceptionDetails.text));
  return r.result.value;
}
const sleep = ms => new Promise(r => setTimeout(r, ms));

/* ── 기대 문구는 실제 프론트 소스에서 뽑는다 ── */
const policySrc = fs.readFileSync(path.join(FRONT, 'lib/passwordPolicy.ts'), 'utf8');
function pick(key){
  const m = policySrc.match(new RegExp(key + ':\\s*"((?:[^"\\\\]|\\\\.)*)"'));
  if(!m) throw new Error('passwordPolicy.ts 에서 ' + key + ' 를 못 찾음');
  return m[1];
}
const EXP = {
  guide: pick('guide'), space: pick('space'), disallowed: pick('disallowed'),
  policy: pick('policy'), success: pick('success'),
  confirmDefault: pick('confirmDefault'), confirmMatch: pick('confirmMatch'),
  confirmMismatch: pick('confirmMismatch')
};
const pageSrc = fs.readFileSync(path.join(FRONT, 'app/my-info/change-password/page.tsx'), 'utf8');
EXP.doneToast = (pageSrc.match(/showToast\("([^"]+)"\)/) || [])[1];
EXP.submitLabel = (pageSrc.match(/isLoading \? "[^"]*" : "([^"]+)"/) || [])[1];
const inputSrc = fs.readFileSync(path.join(FRONT, 'components/PasswordInput.tsx'), 'utf8');
EXP.caps = (inputSrc.match(/<span>(Caps Lock[^<]+)<\/span>/) || [])[1];
EXP.placeholders = {
  cur: (pageSrc.match(/label="현재 비밀번호"\s*\n\s*placeholder="([^"]+)"/) || [])[1],
  nw:  (pageSrc.match(/label="새 비밀번호"\s*\n\s*placeholder="([^"]+)"/) || [])[1],
  cfm: (pageSrc.match(/label="새 비밀번호 확인"\s*\n\s*placeholder="([^"]+)"/) || [])[1]
};
/* 체크리스트 4개 라벨도 소스에서 */
EXP.checklist = (policySrc.match(/label:\s*"([^"]+)"/g) || []).map(s => s.match(/"([^"]+)"/)[1]);

/* ── 화면에서 읽어 오는 것들 ── */
const PROBE = `
  var q = function(m){ return document.querySelector('[data-mount="' + m + '"]'); };
  var msg = function(box){
    var e = q(box) && q(box).querySelector('.pw-msg');
    return e ? {text: e.textContent.trim(), type: (e.className.match(/t-(\\w+)/) || [])[1],
                icon: !!e.querySelector('svg')} : null;
  };
  var rules = function(){
    var box = q('pw-new-msgbox'); if(!box) return null;
    var rs = box.querySelectorAll('.pw-rules .r'); if(!rs.length) return null;
    return Array.prototype.map.call(rs, function(r){
      return {label: r.lastElementChild.textContent.trim(),
              met: r.classList.contains('ok'), mark: r.querySelector('.mark svg') ? 'check' : 'dot',
              color: getComputedStyle(r).color};
    });
  };
  var border = function(f){
    var e = q(f); if(!e) return null;
    return {cls: e.className.replace('pw-field','').trim(),
            color: getComputedStyle(e.querySelector('.pw-box')).borderTopColor};
  };
  var toast = document.querySelector('[data-mount="toast"]');
  var sub = q('pw-submit');
  return {
    state: document.querySelector('section.screen[data-screen="password"]').dataset.state,
    values: {cur: q('pw-cur').value, nw: q('pw-new').value, cfm: q('pw-cfm').value},
    types:  {cur: q('pw-cur').type, nw: q('pw-new').type, cfm: q('pw-cfm').type},
    placeholders: {cur: q('pw-cur').placeholder, nw: q('pw-new').placeholder, cfm: q('pw-cfm').placeholder},
    labels: Array.prototype.map.call(document.querySelectorAll('[data-screen="password"] .pw-field label'),
              function(l){ return l.textContent.trim(); }),
    newMsg: msg('pw-new-msgbox'), cfmMsg: msg('pw-cfm-msgbox'), rules: rules(),
    newField: border('pw-new-field'), cfmField: border('pw-cfm-field'),
    submit: {label: sub.textContent.trim(), disabled: sub.disabled,
             bg: getComputedStyle(sub).backgroundColor},
    eyeLabels: {cur: q('pw-cur-eye').getAttribute('aria-label'), nw: q('pw-new-eye').getAttribute('aria-label'),
                cfm: q('pw-cfm-eye').getAttribute('aria-label')},
    caps: {shown: !q('pw-new-caps').hidden, text: q('pw-new-caps').textContent.trim()},
    toast: {shown: !toast.hidden, text: toast.textContent.trim()}
  };
`;
/* 테두리는 150ms 전환이 걸려 있다 — 끝난 뒤 읽어야 목표색이 나온다 */
const probe = async () => { await sleep(220); return evalJS(PROBE); };

async function focusField(m){
  await evalJS('document.querySelector(\'[data-mount="' + m + '"]\').focus(); return 1;');
  await sleep(40);
}
async function clearField(m){
  /* 값만 지우면 input 이벤트가 안 나므로 전체 선택 후 지운다 */
  await focusField(m);
  await evalJS('var e=document.querySelector(\'[data-mount="' + m + '"]\'); e.select(); return 1;');
  await send('Input.dispatchKeyEvent', {type:'keyDown', windowsVirtualKeyCode:8, nativeVirtualKeyCode:8, key:'Backspace', code:'Backspace'});
  await send('Input.dispatchKeyEvent', {type:'keyUp',   windowsVirtualKeyCode:8, nativeVirtualKeyCode:8, key:'Backspace', code:'Backspace'});
  await sleep(50);
}
async function typeInto(m, text){
  await focusField(m);
  await send('Input.insertText', {text});
  await sleep(60);
}
async function pressSpace(){
  await send('Input.dispatchKeyEvent', {type:'keyDown', key:' ', code:'Space', windowsVirtualKeyCode:32, nativeVirtualKeyCode:32, text:' ', unmodifiedText:' '});
  await send('Input.dispatchKeyEvent', {type:'char',    key:' ', text:' ', unmodifiedText:' '});
  await send('Input.dispatchKeyEvent', {type:'keyUp',   key:' ', code:'Space', windowsVirtualKeyCode:32, nativeVirtualKeyCode:32});
  await sleep(80);
}
async function pressKey(key, code, vk, mods){
  await send('Input.dispatchKeyEvent', {type:'keyDown', key, code, windowsVirtualKeyCode:vk, nativeVirtualKeyCode:vk, modifiers: mods || 0});
  await send('Input.dispatchKeyEvent', {type:'keyUp',   key, code, windowsVirtualKeyCode:vk, nativeVirtualKeyCode:vk, modifiers: mods || 0});
  await sleep(80);
}
async function blurAll(){
  await evalJS('if(document.activeElement && document.activeElement.blur) document.activeElement.blur(); return 1;');
  await sleep(60);
}
async function resetScreen(){
  await evalJS('go("password","default"); return 1;');
  await sleep(120);
}

const R = {expected: EXP, steps: [], checks: [], console: []};
function check(id, pass, want, got){ R.checks.push({id, pass, want, got}); }

async function main(){
  await new Promise(r => server.listen(PORT, r));
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'phpw-'));
  const chrome = spawn(CHROME, ['--headless=new', '--remote-debugging-port=' + DPORT,
    CHROME_DL.args(PH_DL, profile)[0] /* '--user-data-dir=' + profile */, '--no-first-run', '--no-default-browser-check',
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
  const WebSocketImpl = global.WebSocket;
  const page = targets.find(t => t.type === 'page');
  ws = new WebSocketImpl(page.webSocketDebuggerUrl);
  await new Promise(r => ws.addEventListener('open', r));
  ws.addEventListener('message', ev => {
    const m = JSON.parse(ev.data);
    if(m.id && pending.has(m.id)){ pending.get(m.id).res(m.result); pending.delete(m.id); return; }
    if(m.method === 'Runtime.consoleAPICalled' && (m.params.type === 'error' || m.params.type === 'warning'))
      consoleErrors.push(m.params.type + ': ' + m.params.args.map(a => a.value || a.description || a.type).join(' '));
    if(m.method === 'Runtime.exceptionThrown')
      consoleErrors.push('exception: ' + ((m.params.exceptionDetails.exception && m.params.exceptionDetails.exception.description) || m.params.exceptionDetails.text));
  });
  await send('Runtime.enable'); await send('Page.enable');
  await send('Page.navigate', {url:'http://127.0.0.1:' + PORT + '/app.html#password'});
  await sleep(1600);

  const log = async (id, note) => { const p = await probe(); R.steps.push({id, note: note || '', ...p}); return p; };

  /* ── 1) 처음 열었을 때 ── */
  await resetScreen();
  let s = await log('1. 처음 연 화면');
  check('처음 — 새 비밀번호 안내 문구', s.newMsg && s.newMsg.text === EXP.guide, EXP.guide, s.newMsg && s.newMsg.text);
  check('처음 — 안내 문구는 회색(default)', s.newMsg && s.newMsg.type === 'default', 'default', s.newMsg && s.newMsg.type);
  check('처음 — 확인 칸 안내 문구', s.cfmMsg && s.cfmMsg.text === EXP.confirmDefault, EXP.confirmDefault, s.cfmMsg && s.cfmMsg.text);
  check('처음 — 체크리스트 없음', s.rules === null, null, s.rules);
  check('처음 — 세 칸 다 비어 있다', s.values.cur === '' && s.values.nw === '' && s.values.cfm === '',
        '빈 값 3개', s.values);
  check('처음 — 제출 잠김', s.submit.disabled === true, true, s.submit.disabled);
  check('제출 버튼 글자', s.submit.label === EXP.submitLabel, EXP.submitLabel, s.submit.label);
  check('라벨 3개', JSON.stringify(s.labels) === JSON.stringify(['현재 비밀번호','새 비밀번호','새 비밀번호 확인']),
        ['현재 비밀번호','새 비밀번호','새 비밀번호 확인'], s.labels);
  check('플레이스홀더 — 현재', s.placeholders.cur === EXP.placeholders.cur, EXP.placeholders.cur, s.placeholders.cur);
  check('플레이스홀더 — 새', s.placeholders.nw === EXP.placeholders.nw, EXP.placeholders.nw, s.placeholders.nw);
  check('플레이스홀더 — 확인', s.placeholders.cfm === EXP.placeholders.cfm, EXP.placeholders.cfm, s.placeholders.cfm);
  check('처음 — 세 칸 모두 가려짐', s.types.cur === 'password' && s.types.nw === 'password' && s.types.cfm === 'password',
        'password×3', s.types);
  check('눈 버튼 aria-label(가려진 상태)', s.eyeLabels.nw === '비밀번호 표시', '비밀번호 표시', s.eyeLabels.nw);

  /* ── 2) 짧은 비번을 넣는 순간 (blur 전) ── */
  await typeInto('pw-new', 'abc');
  s = await log('2. "abc" 입력 (아직 포커스 안 뺌)');
  check('입력 즉시 체크리스트 등장', !!s.rules, '4항목', s.rules && s.rules.length);
  check('체크리스트 라벨 = 원본', JSON.stringify((s.rules||[]).map(r=>r.label)) === JSON.stringify(EXP.checklist),
        EXP.checklist, (s.rules||[]).map(r=>r.label));
  check('"abc" — 영문만 충족', JSON.stringify((s.rules||[]).map(r=>r.met)) === JSON.stringify([false,true,false,false]),
        [false,true,false,false], (s.rules||[]).map(r=>r.met));
  check('미충족 항목은 점(dot) 표시', (s.rules||[]).filter(r=>!r.met).every(r=>r.mark==='dot'), 'dot', (s.rules||[]).map(r=>r.mark));
  check('충족 항목은 체크 아이콘', (s.rules||[]).filter(r=>r.met).every(r=>r.mark==='check'), 'check', (s.rules||[]).map(r=>r.mark));
  check('blur 전에는 규칙 오류 문구 없음', s.newMsg === null, null, s.newMsg && s.newMsg.text);
  check('blur 전에는 빨간 테두리 아님', s.newField.cls.indexOf('is-error') < 0, '(테두리 평상)', s.newField);

  /* ── 3) 포커스를 빼면 그때 규칙 오류 문구 ── */
  await blurAll();
  s = await log('3. 포커스 빼기(blur)');
  check('blur 후 규칙 오류 문구', s.newMsg && s.newMsg.text === EXP.policy, EXP.policy, s.newMsg && s.newMsg.text);
  check('blur 후 빨간 테두리', s.newField.cls.indexOf('is-error') >= 0 && s.newField.color === 'rgb(255, 56, 60)',
        'is-error / rgb(255, 56, 60)', s.newField);
  check('오류 문구는 빨강', s.newMsg && s.newMsg.type === 'error', 'error', s.newMsg && s.newMsg.type);
  check('오류 문구와 체크리스트가 함께 보인다', !!s.rules && !!s.newMsg, '둘 다', {rules: !!s.rules, msg: !!s.newMsg});

  /* ── 4) 규칙을 하나씩 채워 나간다 ── */
  await typeInto('pw-new', '1');
  s = await log('4a. "abc1"');
  check('숫자 채우면 숫자 항목 켜짐', JSON.stringify((s.rules||[]).map(r=>r.met)) === JSON.stringify([false,true,true,false]),
        [false,true,true,false], (s.rules||[]).map(r=>r.met));
  await typeInto('pw-new', '2345');
  s = await log('4b. "abc12345" (8자)');
  check('8자 되면 길이 항목 켜짐', JSON.stringify((s.rules||[]).map(r=>r.met)) === JSON.stringify([true,true,true,false]),
        [true,true,true,false], (s.rules||[]).map(r=>r.met));
  check('특수문자 남아 아직 미충족 문구', s.newMsg && s.newMsg.text === EXP.policy, EXP.policy, s.newMsg && s.newMsg.text);
  await typeInto('pw-new', '!');
  s = await log('4c. "abc12345!" (전부 충족)');
  check('전부 충족 → 체크리스트 사라짐', s.rules === null, null, s.rules);
  check('전부 충족 문구', s.newMsg && s.newMsg.text === EXP.success, EXP.success, s.newMsg && s.newMsg.text);
  check('전부 충족 문구는 초록 + 체크아이콘', s.newMsg && s.newMsg.type === 'success' && s.newMsg.icon,
        'success + icon', s.newMsg);
  check('전부 충족 → 연둣빛 테두리', s.newField.cls.indexOf('is-ok') >= 0 && s.newField.color === 'rgb(159, 232, 112)',
        'is-ok / rgb(159, 232, 112)', s.newField);
  check('확인 칸 비어 제출은 아직 잠김', s.submit.disabled === true, true, s.submit.disabled);

  /* ── 5) 허용되지 않은 특수문자 ── */
  await resetScreen();
  await typeInto('pw-new', 'abc12345~');
  s = await log('5. "abc12345~" (허용 밖 특수문자, blur 안 함)');
  check('허용 밖 문자는 blur 없이 즉시 문구', s.newMsg && s.newMsg.text === EXP.disallowed, EXP.disallowed, s.newMsg && s.newMsg.text);
  check('허용 밖 문자 — 값에는 남는다', s.values.nw === 'abc12345~', 'abc12345~', s.values.nw);
  check('허용 밖 문자 — 특수문자 항목 미충족', (s.rules||[])[3] && (s.rules||[])[3].met === false, false, (s.rules||[])[3]);

  /* ── 6) 공백 ── */
  await resetScreen();
  await typeInto('pw-new', 'abc123');
  await focusField('pw-new'); await pressSpace();
  s = await log('6a. 스페이스 누른 직후');
  check('공백 문구', s.newMsg && s.newMsg.text === EXP.space, EXP.space, s.newMsg && s.newMsg.text);
  check('공백은 값에 담기지 않는다', s.values.nw === 'abc123', 'abc123', s.values.nw);
  check('공백일 때 체크리스트는 감춘다', s.rules === null, null, s.rules);
  await sleep(2400);
  s = await log('6b. 2.4초 뒤 (2200ms 경과)');
  check('공백 문구는 2200ms 뒤 사라진다', !s.newMsg || s.newMsg.text !== EXP.space, '사라짐', s.newMsg && s.newMsg.text);

  /* ── 7) 한글·이모지·17자 ── */
  await resetScreen();
  await typeInto('pw-new', '가나다');
  s = await log('7a. 한글 입력');
  check('한글은 담기지 않는다', s.values.nw === '', '', s.values.nw);
  await typeInto('pw-new', 'abcdefgh12345678!');   /* 17자 */
  s = await log('7b. 17자 입력');
  check('16자에서 잘린다', s.values.nw.length === 16, 16, s.values.nw.length);

  /* ── 7c) IME 조합 — 조합 중에는 값을 건드리지 않고, 끝난 뒤 저장 기준이 한글을 걸러낸다 ── */
  await resetScreen();
  await focusField('pw-new');
  await send('Input.imeSetComposition', {text:'\uAC01', selectionStart:1, selectionEnd:1});
  await sleep(120);
  const mid = await evalJS('return {dom: document.querySelector(\'[data-mount="pw-new"]\').value, model: PW.nw};');
  R.steps.push({id:'7c. 한글 조합 중', note:'Input.imeSetComposition', ime: mid,
                values:{cur:'',nw:mid.model,cfm:''}, newMsg:null, cfmMsg:null, rules:null,
                submit:{disabled:true}, state:'-', toast:{shown:false}});
  check('조합 중에는 모델 값을 건드리지 않는다', mid.model === '', '', mid.model);
  check('조합 중 글자는 칸에 그대로 남는다(중간에 지워지지 않는다)', mid.dom !== '', '조합 글자 유지', mid.dom);
  await send('Input.insertText', {text:'\uAC01'});   /* 조합 확정 → compositionend */
  await sleep(150);
  s = await log('7d. 한글 조합 확정');
  check('조합 확정 후 한글은 걸러진다', s.values.nw === '', '', s.values.nw);

  /* ── 8) 확인값 ── */
  await resetScreen();
  await typeInto('pw-cur', 'payhug!2025');
  await typeInto('pw-new', 'payhug!2026');
  await typeInto('pw-cfm', 'payhug!2025');
  s = await log('8a. 확인값 불일치');
  check('불일치 문구', s.cfmMsg && s.cfmMsg.text === EXP.confirmMismatch, EXP.confirmMismatch, s.cfmMsg && s.cfmMsg.text);
  check('불일치 — 확인 칸 빨간 테두리', s.cfmField.cls.indexOf('is-error') >= 0 && s.cfmField.color === 'rgb(255, 56, 60)',
        'is-error / rgb(255, 56, 60)', s.cfmField);
  check('불일치 — 화면 상태 error', s.state === 'error', 'error', s.state);
  check('불일치 — 제출 잠김', s.submit.disabled === true, true, s.submit.disabled);
  check('확인 칸은 규칙을 되풀이하지 않는다', s.cfmMsg && s.cfmMsg.text !== EXP.policy, '규칙 문구 아님', s.cfmMsg && s.cfmMsg.text);

  await clearField('pw-cfm');
  await typeInto('pw-cfm', 'payhug!2026');
  s = await log('8b. 확인값 일치');
  check('일치 문구', s.cfmMsg && s.cfmMsg.text === EXP.confirmMatch, EXP.confirmMatch, s.cfmMsg && s.cfmMsg.text);
  check('일치 — 초록 + 체크아이콘', s.cfmMsg && s.cfmMsg.type === 'success' && s.cfmMsg.icon, 'success + icon', s.cfmMsg);
  check('일치 — 연둣빛 테두리', s.cfmField.cls.indexOf('is-ok') >= 0, 'is-ok', s.cfmField.cls);
  check('세 칸 다 차면 제출 열림', s.submit.disabled === false, false, s.submit.disabled);

  /* ── 9) 현재 비밀번호가 비면 제출은 잠긴다 ── */
  await clearField('pw-cur');
  s = await log('9. 현재 비밀번호를 비움');
  check('현재 비밀번호 비면 제출 잠김', s.submit.disabled === true, true, s.submit.disabled);
  check('현재 비밀번호 칸엔 메시지 칸이 없다',
        await evalJS('return !document.querySelector(\'[data-mount="pw-cur-field"] .pw-msgbox\');'), true, undefined);

  /* ── 10) 눈 버튼 ── */
  await resetScreen();
  await evalJS('document.querySelector(\'[data-mount="pw-new-eye"]\').click(); return 1;');
  await sleep(80);
  s = await log('10. 새 비밀번호 눈 버튼 누름');
  check('눈 버튼 → 글자 보임', s.types.nw === 'text', 'text', s.types.nw);
  check('눈 버튼 aria-label 바뀜', s.eyeLabels.nw === '비밀번호 숨기기', '비밀번호 숨기기', s.eyeLabels.nw);
  check('다른 칸은 그대로 가려짐', s.types.cfm === 'password' && s.types.cur === 'password', 'password', s.types);
  await evalJS('document.querySelector(\'[data-mount="pw-new-eye"]\').click(); return 1;');
  await sleep(80);

  /* ── 11) Caps Lock ── */
  await resetScreen();
  await focusField('pw-new');
  /* CDP Input.dispatchKeyEvent 의 modifiers 에는 CapsLock 비트가 없다.
     getModifierState('CapsLock') 이 참인 keydown 을 만들어 그대로 흘려 넣는다. */
  await evalJS("var t=document.querySelector('[data-mount=\\'pw-new\\']');" +
    "var e=new KeyboardEvent('keydown',{key:'a',code:'KeyA',bubbles:true,cancelable:true});" +
    "Object.defineProperty(e,'getModifierState',{value:function(k){return k==='CapsLock';}});" +
    "t.dispatchEvent(e); return 1;");
  await sleep(80);
  s = await log('11. Caps Lock 켠 채 입력(CapsLock=on keydown)');
  check('Caps Lock 말풍선', s.caps.shown === true, true, s.caps.shown);
  check('Caps Lock 문구', s.caps.text === EXP.caps, EXP.caps, s.caps.text);
  await blurAll();
  s = await log('11b. 포커스 빼면 말풍선 내림');
  check('blur 시 말풍선 사라짐', s.caps.shown === false, false, s.caps.shown);

  /* ── 12) 제출 → 완료 ── */
  await resetScreen();
  await typeInto('pw-cur', 'payhug!2025');
  await typeInto('pw-new', 'payhug!2026');
  await typeInto('pw-cfm', 'payhug!2026');
  await evalJS('document.querySelector(\'[data-act="pw-submit"]\').click(); return 1;');
  await sleep(150);
  s = await log('12. 제출');
  check('완료 토스트 문구', s.toast.shown && s.toast.text === EXP.doneToast, EXP.doneToast, s.toast.text);
  check('완료 후 세 칸 비움', s.values.cur === '' && s.values.nw === '' && s.values.cfm === '', '빈 값 3개', s.values);
  check('완료 후 화면 상태 done', s.state === 'done', 'done', s.state);
  check('완료 후 제출 다시 잠김', s.submit.disabled === true, true, s.submit.disabled);
  check('완료 화면에 별도 완료 카드는 없다',
        await evalJS('return !document.querySelector(\'[data-screen="password"] .done-card\');'), true, undefined);

  /* ── 13) Enter 제출 ── */
  await resetScreen();
  await typeInto('pw-cur', 'payhug!2025');
  await typeInto('pw-new', 'payhug!2026');
  await typeInto('pw-cfm', 'payhug!2026');
  await focusField('pw-cfm');
  await pressKey('Enter', 'Enter', 13);
  s = await log('13. Enter 로 제출');
  check('Enter 로도 제출된다', s.state === 'done' && s.toast.shown, 'done + 토스트', {state:s.state, toast:s.toast.shown});

  /* ── 14) 정적 낱장 4종에도 같은 문구가 박혀 있는지 ── */
  R.static = {};
  for(const [f, want] of [['password.html', [EXP.guide, EXP.confirmDefault, EXP.submitLabel]],
                          ['password--weak.html', [EXP.policy, ...EXP.checklist]],
                          ['password--error.html', [EXP.confirmMismatch, EXP.success]],
                          ['password--done.html', [EXP.doneToast]]]){
    const src = fs.readFileSync(path.join(REPO, f), 'utf8');
    R.static[f] = want.map(w => ({text: w, found: src.indexOf(w) >= 0}));
    check('정적 ' + f, R.static[f].every(x => x.found), want, R.static[f].filter(x=>!x.found).map(x=>x.text));
  }

  /* ── 15) 지어낸 문구가 남아 있지 않은지 ── */
  const appSrc = fs.readFileSync(path.join(REPO, 'app.html'), 'utf8');
  /* 기본 낱장은 세 칸이 비어 있어야 한다 — 미리 채운 값은 우리가 지어낸 것이다 */
  for(const f of ['password.html', 'password--done.html']){
    const src = fs.readFileSync(path.join(REPO, f), 'utf8');
    check('정적 ' + f + ' 미리 채운 값 없음', src.indexOf('value="12345678"') < 0, '없음', '남아 있음');
  }
  const GHOSTS = ['비밀번호 규칙 미충족', '새 비밀번호가 일치하지 않음', '영문·숫자·특수문자 포함 8자 이상',
                  "{t:'8자 이상'", '>비밀번호 변경 완료<', '새 비밀번호로 변경 완료', '>로그인 화면으로<',
                  '>변경하기<', 'class="rule-list"', 'class="done-card"', 'pwRulesOk', 'PW.touched'];
  R.ghosts = GHOSTS.map(g => ({text:g, stillIn: appSrc.indexOf(g) >= 0}));
  check('지어낸 문구 전부 제거', R.ghosts.every(g => !g.stillIn), '0건', R.ghosts.filter(g=>g.stillIn).map(g=>g.text));

  R.console = consoleErrors;
  check('콘솔 오류 0', consoleErrors.length === 0, 0, consoleErrors.length);

  R.summary = {total: R.checks.length, pass: R.checks.filter(c=>c.pass).length,
               fail: R.checks.filter(c=>!c.pass).map(c=>c.id)};
  fs.writeFileSync(path.join(OUTDIR, 'verify_password_result.json'), JSON.stringify(R, null, 2));
  console.log('PASS ' + R.summary.pass + '/' + R.summary.total);
  if(R.summary.fail.length) console.log('FAIL:\n  - ' + R.summary.fail.join('\n  - '));

  try{ ws.close(); }catch(e){}
  chrome.kill(); server.close();
  process.exit(R.summary.fail.length ? 1 : 0);
}
main().catch(e => { console.error(e); process.exit(2); });
