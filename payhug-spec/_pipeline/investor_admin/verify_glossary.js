/* glossary.html 헤드리스 검증 — 창을 띄우지 않는다(--headless=new).
   보는 것: 앵커 도달 · 가로 넘침 · 관련 용어 링크 이름 = 카드 제목 · 기호 검색 · 목차.
   카드 5필드·캡처 마커·라이트박스·구버전 링크는 verify_glossary5.js 가 본다.
   5필드 재조판(2026-08-28)으로 층위 필터 칩(.fchip)·h4 제목·hitCount 가 사라져 그 기준을 걷어냈다. */
const http = require('http'); const fs = require('fs'); const path = require('path');
const CHROME_DL = require('./chrome_dl');
const PH_DL = CHROME_DL.dir();
const os = require('os'); const { spawn } = require('child_process');
const REPO = '/Users/semi/cursor/payhug-investor-admin';
const PORT = 8790, DPORT = 9490;
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const MIME = {'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript','.png':'image/png'};
const server = http.createServer((req,res)=>{ const p=path.join(REPO, decodeURIComponent(req.url.split('?')[0]));
  fs.readFile(p,(e,b)=>{ if(e){res.writeHead(404);res.end('nope');return;}
    res.writeHead(200,{'Content-Type':MIME[path.extname(p)]||'application/octet-stream'}); res.end(b); }); });
let msgId=0, ws, pending=new Map(); const consoleErrors=[];
function send(m,p){ const id=++msgId; ws.send(JSON.stringify({id,method:m,params:p||{}}));
  return new Promise((res,rej)=>pending.set(id,{res,rej})); }
async function evalJS(e){ const r=await send('Runtime.evaluate',{expression:'(function(){'+e+'})()',returnByValue:true,awaitPromise:true});
  if(r.exceptionDetails) throw new Error('eval: '+JSON.stringify(r.exceptionDetails)); return r.result.value; }
const sleep=ms=>new Promise(r=>setTimeout(r,ms));

async function main(){
  await new Promise(r=>server.listen(PORT,r));
  const profile=fs.mkdtempSync(path.join(os.tmpdir(),'phg-'));
  const chrome=spawn(CHROME,['--headless=new','--remote-debugging-port='+DPORT,CHROME_DL.args(PH_DL, profile)[0] /* '--user-data-dir='+profile */,
    '--no-first-run','--no-default-browser-check','--disable-gpu','--window-size=1440,1200','about:blank'],{stdio:'ignore'});
  let targets=null;
  for(let i=0;i<60&&!targets;i++){ await sleep(300);
    try{ targets=await new Promise((res,rej)=>{ http.get({host:'127.0.0.1',port:DPORT,path:'/json'},r=>{
      let d='';r.on('data',c=>d+=c);r.on('end',()=>res(JSON.parse(d)));}).on('error',rej); }); }catch(e){ targets=null; } }
  const page=targets.find(t=>t.type==='page');
  ws=new WebSocket(page.webSocketDebuggerUrl);
  await new Promise(r=>ws.addEventListener('open',r));
  ws.addEventListener('message',ev=>{ const m=JSON.parse(ev.data);
    if(m.id&&pending.has(m.id)){pending.get(m.id).res(m.result);pending.delete(m.id);return;}
    if(m.method==='Runtime.consoleAPICalled'&&(m.params.type==='error'||m.params.type==='warning'))
      consoleErrors.push(m.params.type+': '+m.params.args.map(a=>a.value||a.description||a.type).join(' '));
    if(m.method==='Runtime.exceptionThrown') consoleErrors.push('exception: '+JSON.stringify(m.params.exceptionDetails.text));
    if(m.method==='Log.entryAdded'&&m.params.entry.level==='error') consoleErrors.push('log: '+m.params.entry.text+' '+(m.params.entry.url||'')); });
  await send('Runtime.enable'); await send('Log.enable'); await send('Page.enable');
  await send('Page.navigate',{url:'http://127.0.0.1:'+PORT+'/glossary.html'});
  await sleep(1500);

  const R={};
  R.anchors = await evalJS(`
    var bad=[], seen=0;
    [].slice.call(document.querySelectorAll('a[href^="#"]')).forEach(function(a){
      var id=a.getAttribute('href').slice(1); if(!id) return; seen++;
      if(!document.getElementById(id)) bad.push(a.getAttribute('href')+' :: '+a.textContent.trim().slice(0,30));
    });
    return {total:seen, bad:bad};`);

  R.overflow = {};
  for (const w of [1440, 1280, 1024, 768]) {
    await send('Emulation.setDeviceMetricsOverride',{width:w,height:900,deviceScaleFactor:1,mobile:false});
    await sleep(250);
    R.overflow[w] = await evalJS(`
      var de=document.documentElement, over=[];
      if(de.scrollWidth > de.clientWidth){
        [].slice.call(document.querySelectorAll('body *')).forEach(function(el){
          var r=el.getBoundingClientRect();
          if(r.width>0 && r.right > de.clientWidth+1) over.push(el.tagName+'.'+(el.className||'').toString().slice(0,40)+' right='+Math.round(r.right));
        });
      }
      return {scrollW:de.scrollWidth, clientW:de.clientWidth, over:over.slice(0,8)};`);
  }
  await send('Emulation.clearDeviceMetricsOverride');
  await sleep(200);

  /* 본문 링크는 카드 제목으로도, 별칭·기호로도 건다(build_glossary.py ALIAS).
     그래서 글자가 제목과 달라도 결함이 아니다. 결함은 '가리키는 카드가 없다' 하나뿐이다.
     별칭으로 걸린 것은 세어서 남긴다 — 갑자기 0이 되면 링크 배선이 끊긴 것이다. */
  R.names = await evalJS(`
    var bad=[], alias=0, exact=0;
    [].slice.call(document.querySelectorAll('a.xref[href^="#t"]')).forEach(function(a){
      var t=document.getElementById(a.getAttribute('href').slice(1));
      if(!t) { bad.push('missing '+a.getAttribute('href')); return; }
      var h3=t.querySelector('h3[data-field="term"]');
      if(!h3) { bad.push('no title '+a.getAttribute('href')); return; }
      if(a.textContent.trim()===h3.textContent.trim()) exact++; else alias++;
    });
    return {bad:bad, exact:exact, alias:alias};`);

  /* 층위는 카드 머리의 칩 글자로만 남아 있다(필터 UI 없음) */
  R.layers = await evalJS(`
    var c=[].slice.call(document.querySelectorAll('.term .chip.lv'));
    var s=c.filter(function(x){ return x.textContent.trim()==='화면 용어'; }).length;
    return {screen:s, calc:c.length-s, total:document.querySelectorAll('.term').length};`);

  /* 기호 검색 */
  R.search = {};
  for (const q of ['PSA','SB','SMR','W금융일수','ty수익율','④','순현금']) {
    R.search[q] = await evalJS(`var i=document.getElementById('q'); i.value=${JSON.stringify(q)};
      i.dispatchEvent(new Event('input')); return document.querySelectorAll('.term:not(.hidden)').length;`);
  }
  await evalJS(`var i=document.getElementById('q'); i.value=''; i.dispatchEvent(new Event('input')); return 1;`);

  R.toc = await evalJS(`
    var a=[].slice.call(document.querySelectorAll('.toc a[data-t]'));
    var dead=a.filter(function(x){ return !document.getElementById(x.getAttribute('href').slice(1)); })
              .map(function(x){ return x.getAttribute('href'); });
    return {entries:a.length, dead:dead, first:a.length?a[0].getAttribute('href'):null,
            stages:document.querySelectorAll('.stage-sec').length,
            appendix:document.querySelectorAll('section.sec[id^=apx]').length};`);

  R.console = consoleErrors.filter(function(c){ return c.indexOf('/favicon.ico') < 0; });
  console.log(JSON.stringify(R,null,1));

  /* ── 판정 ──
     2026-08-30 이전까지 이 파일은 위 6종을 재기만 하고 process.exit(0) 으로 끝냈다.
     화면에 값이 찍히니 검사되는 줄 알았지만 어느 값도 통과·실패를 가르지 않았다.
     기준을 새로 발명하지 않는다 — 이 파일 머리말이 스스로 적은 검사 대상
     (앵커 도달 · 가로 넘침 · 본문 링크 대상 · 기호 검색 · 목차)을 그대로 판정식으로 옮긴다.
     곳수(카드 50 · 앵커 734 · exact 354)는 박지 않는다. 카드가 늘면 같이 늘어야 하는 값이라
     못 박으면 그것이 다음 세대의 낡은 기준이 된다. */
  const fails = [];
  if(R.anchors.bad.length) fails.push('죽은 앵커 ' + R.anchors.bad.length + '건: ' + R.anchors.bad.slice(0,4).join(' | '));
  if(R.anchors.total === 0) fails.push('앵커 0건 — 검사 대상이 사라졌다(셀렉터 노후)');
  Object.keys(R.overflow).forEach(function(w){
    const o = R.overflow[w];
    if(o.scrollW > o.clientW) fails.push('가로 넘침 @' + w + 'px — ' + o.scrollW + '>' + o.clientW + ' ' + JSON.stringify(o.over.slice(0,3)));
  });
  if(R.names.bad.length) fails.push('본문 링크가 가리키는 카드 없음 ' + R.names.bad.length + '건: ' + R.names.bad.slice(0,4).join(' | '));
  /* 위 69-71행 주석의 기준 그대로 — 별칭으로 걸린 것이 갑자기 0 이면 링크 배선이 끊긴 것이다.
     몇 건이어야 하는지는 정해 두지 않는다. 0 인지만 본다. */
  if(R.names.exact + R.names.alias === 0) fails.push('본문 xref 0건 — 링크 배선이 끊겼다');
  /* 층위 칩은 카드마다 하나다(build_glossary.py). screen+calc 는 칩 곳수이므로
     이것이 카드 수와 어긋나면 칩이 빠졌거나 겹쳐 붙은 것이다. */
  if(R.layers.screen + R.layers.calc !== R.layers.total)
    fails.push('층위 칩 ' + (R.layers.screen + R.layers.calc) + ' ≠ 카드 ' + R.layers.total);
  /* 기호 검색 — 여기 적힌 기호는 용어판에 실린 것들이다. 0건이면 그 기호가 사라졌거나 검색이 죽었다.
     걸리는 카드 수는 판정하지 않는다(내용이 늘면 같이 는다). */
  Object.keys(R.search).forEach(function(q){ if(R.search[q] === 0) fails.push('기호 검색 0건 — ' + q); });
  if(R.toc.dead.length) fails.push('목차 죽은 항목 ' + JSON.stringify(R.toc.dead));
  if(R.toc.entries === 0) fails.push('목차 0건');
  if(R.console.length) fails.push('콘솔 에러 ' + R.console.length + '건: ' + R.console.slice(0,3).join(' | '));

  console.log(fails.length ? '판정: FAIL ' + fails.length + '건\n - ' + fails.join('\n - ') : '판정: PASS');
  try{ chrome.kill(); }catch(e){}
  server.close(); process.exit(fails.length ? 1 : 0);
}
main().catch(e=>{ console.error('ERR', e); process.exit(1); });
