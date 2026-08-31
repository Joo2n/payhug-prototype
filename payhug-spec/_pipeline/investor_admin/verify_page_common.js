/* 용어정의서 편집판을 실제 브라우저에서 돌려 본다.
 *
 * 파이썬 쪽 verify_termsedit.py 는 생성기의 재생산만 대조한다. 페이지 안에서
 * 자기 원본을 꺼내는 길이 끊겨도 그 검사는 통과한다. 실제로 그렇게 한 번 샜다 —
 * #src 가 JSON 문자열이라 따옴표째 atob 에 넘어가 저장이 통째로 막혔는데
 * 검사는 전건 통과했다.
 *
 * 여기서는 페이지가 만든 문서를 바이트로 견주고, 그 문서를 다시 띄워 2세대가
 * 서는지까지 본다.
 *
 * CDP 배선은 verify_app.js 와 같은 패턴이다. FAIL 이 하나라도 있으면 exit 1.
 * 대상이 0건이어도 FAIL 이다. */
const http = require('http');
const fs = require('fs');
const os = require('os');
const path = require('path');
const crypto = require('crypto');
const { spawn } = require('child_process');
const DL = require('./chrome_dl');

const REPO = '/Users/semi/cursor/payhug-investor-admin';
const PAGE = process.env.CEOQ ? 'ceo-questions.html' : 'terms-edit.html';
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const HPORT = +(process.env.HP||8216), DPORT = +(process.env.DP||9216);

const R = [];
const chk = (id, name, got, want) => {
  const pass = JSON.stringify(got) === JSON.stringify(want);
  R.push({ pass, id, name, got, want });
  return pass;
};
const sha = s => crypto.createHash('sha256').update(s, 'utf8').digest('hex').slice(0, 12);

let msgId = 0, ws = null, waiting = new Map();
function send(method, params) {
  const id = ++msgId;
  ws.send(JSON.stringify({ id, method, params }));
  return new Promise((res, rej) => waiting.set(id, { res, rej }));
}
async function evalJS(expr) {
  const r = await send('Runtime.evaluate', {
    expression: '(function(){' + expr + '})()', returnByValue: true, awaitPromise: true });
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.text + ' ' +
    (r.exceptionDetails.exception && r.exceptionDetails.exception.description || ''));
  return r.result.value;
}
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function main() {
  const file = path.join(REPO, PAGE);
  if (!fs.existsSync(file)) { chk('A0', '산출물 있음', false, true); return; }
  const served = fs.readFileSync(file, 'utf8');

  // 2세대 문서를 담을 자리. 저장소를 더럽히지 않게 임시 파일로 두고 끝나면 지운다.
  const gen2 = path.join(REPO, (process.env.CEOQ ? '.ceoq-gen2.html' : '.termsedit-gen2.html'));
  const srv = http.createServer((rq, rs) => {
    const name = decodeURIComponent(rq.url.split('?')[0]).replace(/^\//, '') || PAGE;
    const f = path.join(REPO, name);
    if (!f.startsWith(REPO) || !fs.existsSync(f)) { rs.writeHead(404); rs.end(); return; }
    rs.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    rs.end(fs.readFileSync(f));
  }).listen(HPORT);

  const dl = DL.dir();
  const chrome = spawn(CHROME, DL.args(dl).concat([
    '--headless=new', '--remote-debugging-port=' + DPORT,
    '--disable-gpu', '--no-first-run', '--window-size=1440,1200', 'about:blank']));
  const errs = [];
  try {
    let tgt = null;
    for (let i = 0; i < 60 && !tgt; i++) {
      await sleep(250);
      try {
        tgt = await new Promise((res, rej) => http.get(
          { host: '127.0.0.1', port: DPORT, path: '/json/list' },
          r => { let b = ''; r.on('data', d => b += d); r.on('end', () => {
            /* 확장 프로그램 배경 페이지가 먼저 잡힌다. 진짜 탭만 고른다. */
            const all = JSON.parse(b);
            res(all.find(t => t.type === 'page' && !/^chrome-extension:/.test(t.url || '')) || null);
          }); })
          .on('error', rej));
      } catch (e) { tgt = null; }
    }
    if (!tgt) throw new Error('크롬이 안 붙는다');

    ws = new WebSocket(tgt.webSocketDebuggerUrl);
    await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
    ws.onmessage = ev => {
      const m = JSON.parse(ev.data);
      if (m.id && waiting.has(m.id)) {
        const w = waiting.get(m.id); waiting.delete(m.id);
        m.error ? w.rej(new Error(m.error.message)) : w.res(m.result);
      } else if (m.method === 'Runtime.exceptionThrown') {
        errs.push(m.params.exceptionDetails.text);
      } else if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error') {
        errs.push((m.params.args || []).map(a => a.value || a.description).join(' '));
      }
    };
    await send('Runtime.enable', {});
    await send('Page.enable', {});

    // ── 1세대 ────────────────────────────────────────────────
    await send('Page.navigate', { url: `http://127.0.0.1:${HPORT}/${PAGE}` });
    await sleep(3000);
    const probe = await evalJS('return {t:document.title, url:location.href, ' +
      'body:document.body?document.body.children.length:-1, st:!!document.getElementById("st")}');
    if (!probe.st) { console.error('진입 실패:', JSON.stringify(probe)); }

    chk('A1', '자기 원본을 꺼냄 (상태줄에 실패 문구 없음)',
        await evalJS('return (document.getElementById("st").textContent||"").indexOf("원본을 못 읽었습니다") < 0'), true);
    const SEL = process.env.CEOQ ? '.q' : '.card', N = +(process.env.N||45);
    chk('A2', '항목 카드 수', await evalJS('return document.querySelectorAll("'+SEL+'").length'), N);
    if (!process.env.CEOQ) chk('A3', '목차 항목 수', await evalJS('return document.querySelectorAll("#toc a").length'), N);
    chk('A4', '대조용 갈고리 노출', await evalJS('return typeof window.__renderDoc'), 'function');
    if (!process.env.CEOQ) chk('A5', '원문 인용 블록 수', await evalJS('return document.querySelectorAll("blockquote.q").length'), N);
    chk('A6', '고칠 수 있는 자리가 있음',
        await evalJS('return document.querySelectorAll("[contenteditable],textarea").length > 10'), true);
    if (!process.env.CEOQ) chk('A7', '캡처가 실제로 뜸',
        await evalJS('return Array.prototype.every.call(document.querySelectorAll(".shots img"), function(i){return i.naturalWidth>0}) && document.querySelectorAll(".shots img").length > 0'), true);

    const made = await evalJS('return window.__renderDoc()');
    chk('B1', '페이지가 만든 문서 = 받은 파일 (바이트)', sha(made || ''), sha(served));
    chk('B2', '만든 문서가 doctype 으로 시작',
        (made || '').slice(0, 15).toLowerCase(), '<!doctype html>');
    chk('B3', '만든 문서에 원본이 다시 들겨 있음',
        /id="src">"[A-Za-z0-9+/=]+"/.test(made || ''), true);

    // ── 2세대 — 고친 뒤 만든 문서를 다시 띄운다 ──────────────
    const MUT = process.env.CEOQ
      ? 'window.__seed.items[0].answer = "2세대 시험 답"; return window.__renderDoc();'
      : 'window.__seed.items[0].plain = "2세대 시험 문구";' +
        'window.__seed.items.push({no:46,image:2,term:"2세대 항목",quote:"",plain:"덧붙임",status:"확인필요"});' +
        'return window.__renderDoc();';
    const gen2doc = await evalJS(MUT);
    chk('C0', '2세대 문서를 만들어 냄', typeof gen2doc === 'string' && gen2doc.length > 1000, true);
    fs.writeFileSync(gen2, gen2doc || '', 'utf8');
    await send('Page.navigate', { url: `http://127.0.0.1:${HPORT}/${process.env.CEOQ ? '.ceoq-gen2.html' : '.termsedit-gen2.html'}` });
    await sleep(2500);

    chk('C1', '2세대도 자기 원본을 꺼냄',
        await evalJS('return (document.getElementById("st").textContent||"").indexOf("원본을 못 읽었습니다") < 0'), true);
    chk('C2', '2세대 카드 수', await evalJS('return document.querySelectorAll("'+SEL+'").length'), process.env.CEOQ ? N : N+1);
    chk('C3', '2세대에 고친 것이 살아 있음',
        await evalJS(process.env.CEOQ
          ? 'return document.querySelector("[data-ans]").value'
          : 'return document.querySelector(".card .plain").textContent'),
        process.env.CEOQ ? '2세대 시험 답' : '2세대 시험 문구');
    chk('C4', '2세대에서 만든 문서도 doctype 으로 시작',
        (await evalJS('return window.__renderDoc()') || '').slice(0, 15).toLowerCase(), '<!doctype html>');
    chk('C5', '2세대 뼈대가 1세대와 같음',
        await evalJS('return JSON.parse(document.getElementById("src").textContent)') ===
        (served.match(/id="src">"([A-Za-z0-9+/=]+)"/) || [])[1], true);

    chk('D1', '콘솔 오류', errs.length, 0);
  } finally {
    try { ws && ws.close(); } catch (e) {}
    chrome.kill();
    srv.close();
    try { fs.unlinkSync(gen2); } catch (e) {}
    DL.clean(dl);
  }
}

main().then(() => {
  const w = Math.max(...R.map(r => r.name.length));
  R.forEach(r => console.log('  %s  %s  %s%s', r.pass ? 'PASS' : 'FAIL', r.id,
    r.name.padEnd(w), r.pass ? '' : '   ← ' + JSON.stringify(r.got) + ' / 기대 ' + JSON.stringify(r.want)));
  const bad = R.filter(r => !r.pass).length;
  console.log('\n판정 %d건 · FAIL %d건', R.length, bad);
  if (!R.length) { console.log('대상 0건 — 검사한 것이 없다'); process.exit(1); }
  process.exit(bad ? 1 : 0);
}).catch(e => {
  R.forEach(r => console.log('  %s  %s  %s', r.pass ? 'PASS' : 'FAIL', r.id, r.name));
  console.error('터짐:', e.message);
  process.exit(1);
});
