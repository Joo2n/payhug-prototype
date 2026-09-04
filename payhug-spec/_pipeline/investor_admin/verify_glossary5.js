/* 용어 해설 재조판본 헤드리스 검증 — 창을 띄우지 않는다(--headless=new). */
const http=require('http'), fs=require('fs'), path=require('path'), os=require('os'),
      {spawn}=require('child_process');
const CHROME_DL = require('./chrome_dl');
const PH_DL = CHROME_DL.dir();
const REPO='/Users/semi/cursor/payhug-investor-admin';
const OUT='/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_glossary5_result.json';
const PORT=8760+(process.pid%80), DPORT=9560+(process.pid%80);
const CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const MIME={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript',
  '.png':'image/png','.webp':'image/webp','.json':'application/json'};
const server=http.createServer((q,r)=>{
  const p=path.join(REPO,decodeURIComponent(q.url.split('?')[0].split('#')[0]));
  fs.readFile(p,(e,b)=>{ if(e){r.writeHead(404);r.end('x');return;}
    r.writeHead(200,{'Content-Type':MIME[path.extname(p)]||'application/octet-stream'}); r.end(b); });
});
let id=0, ws, pend=new Map(), errs=[];
function send(m,p){ const i=++id; ws.send(JSON.stringify({id:i,method:m,params:p||{}}));
  return new Promise((res,rej)=>pend.set(i,{res,rej})); }
async function ev(x){ const r=await send('Runtime.evaluate',
  {expression:'(function(){'+x+'})()',returnByValue:true,awaitPromise:true});
  if(r.exceptionDetails) throw new Error('eval: '+JSON.stringify(r.exceptionDetails));
  return r.result.value; }
const sleep=ms=>new Promise(r=>setTimeout(r,ms));

(async()=>{
await new Promise(r=>server.listen(PORT,r));
const prof=fs.mkdtempSync(path.join(os.tmpdir(),'gl5-'));
const ch=spawn(CHROME,['--headless=new','--remote-debugging-port='+DPORT,CHROME_DL.args(PH_DL, prof)[0],
  '--no-first-run','--no-default-browser-check','--disable-gpu','--hide-scrollbars',
  '--window-size=1440,1287','about:blank'],{stdio:'ignore'});
let t=null; for(let i=0;i<60&&!t;i++){ await sleep(300);
  try{ t=await new Promise((res,rej)=>{ http.get({host:'127.0.0.1',port:DPORT,path:'/json'},
    r=>{let d='';r.on('data',c=>d+=c);r.on('end',()=>res(JSON.parse(d)));}).on('error',rej); }); }catch(e){t=null;} }
ws=new WebSocket(t.find(x=>x.type==='page').webSocketDebuggerUrl);
await new Promise(r=>ws.addEventListener('open',r));
ws.addEventListener('message',e=>{ const m=JSON.parse(e.data);
  if(m.id&&pend.has(m.id)){pend.get(m.id).res(m.result);pend.delete(m.id);return;}
  if(m.method==='Runtime.consoleAPICalled'&&m.params.type==='error') errs.push('console: '+m.params.args.map(a=>a.value||a.description).join(' '));
  if(m.method==='Runtime.exceptionThrown') errs.push('exception: '+JSON.stringify(m.params.exceptionDetails.text));
  if(m.method==='Log.entryAdded'&&m.params.entry.level==='error'&&!/favicon/.test(m.params.entry.url||'')) errs.push('log: '+m.params.entry.text+' '+(m.params.entry.url||''));
});
await send('Runtime.enable'); await send('Log.enable'); await send('Page.enable');
const R={};
await send('Page.navigate',{url:`http://127.0.0.1:${PORT}/glossary.html`});
await sleep(2500);
await ev("document.querySelectorAll('img[loading=lazy]').forEach(i=>i.loading='eager'); return 1;");
await ev("window.scrollTo(0,document.body.scrollHeight); return 1;"); await sleep(1800);
await ev("window.scrollTo(0,0); return 1;"); await sleep(900);

R.cards = await ev(`
  var c=[].slice.call(document.querySelectorAll('article.term'));
  var need=['term','var','calc','screen','rel'];
  var bad=c.filter(function(x){return need.some(function(f){return !x.querySelector('[data-field="'+f+'"]');});})
           .map(function(x){return x.id;});
  return {n:c.length, missing:bad, ids:c.map(function(x){return x.id;})};`);

R.images = await ev(`
  var im=[].slice.call(document.querySelectorAll('.crop img'));
  return {n:im.length, broken:im.filter(function(i){return !i.complete||i.naturalWidth===0;})
    .map(function(i){return i.getAttribute('src');})};`);

R.anchors = await ev(`
  var a=[].slice.call(document.querySelectorAll('a[href^="#"]'));
  var dead=[];
  a.forEach(function(x){ var h=x.getAttribute('href').slice(1);
    if(!h) return; if(!document.getElementById(h)) dead.push(h); });
  return {n:a.length, dead:Array.from(new Set(dead))};`);

R.marks = await ev(`
  var out=[]; document.querySelectorAll('.crop').forEach(function(c){
    var m=c.querySelector('.mark'), pan=c.querySelector('.pan');
    var cr=c.getBoundingClientRect(), mr=m.getBoundingClientRect();
    out.push({shot:c.dataset.shot.replace(/.*\\//,''), inView: mr.top<cr.bottom && mr.bottom>cr.top,
      declared:c.dataset.mark, w:+ (mr.width).toFixed(1), h:+(mr.height).toFixed(1),
      panH:pan.offsetHeight, ty:pan.style.transform});
  });
  return {n:out.length, offscreen:out.filter(function(o){return !o.inView;}).length,
    zero:out.filter(function(o){return o.w<2||o.h<2;}).length, sample:out.slice(0,3)};`);

/* 기대값을 검증기가 들고 있지 않는다 — 누른 크롭이 선언한 좌표(declaredLeft)와 그 크롭이
   가리키는 캡처(declaredSrc)를 화면에서 같이 읽어 와 아래 판정에서 라이트박스와 맞춰 본다. */
R.lightbox = await ev(`
  var b=document.querySelector('.crop'); b.click();
  var lb=document.getElementById('lb');
  var on=lb.classList.contains('on');
  var img=document.getElementById('lb-img').getAttribute('src');
  var mk=document.getElementById('lb-mark').style.left;
  var closeBtn=document.getElementById('lb-close');
  document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape'}));
  var closed=!lb.classList.contains('on');
  b.click(); var on2=lb.classList.contains('on');
  document.body.click(); var closed2=!lb.classList.contains('on');
  return {opens:on, src:img, markLeft:mk, escCloses:closed, reopens:on2, backdropCloses:closed2,
          closeLabel: closeBtn ? closeBtn.textContent.trim() : null,
          declaredSrc: b.dataset.shot, declaredLeft: b.dataset.mark.split(',')[0] + '%'};`);

R.search = await ev(`
  var q=document.getElementById('q');
  q.value='PwD'; q.dispatchEvent(new Event('input'));
  var a=document.querySelectorAll('article.term:not(.hidden)').length;
  q.value=''; q.dispatchEvent(new Event('input'));
  var b=document.querySelectorAll('article.term:not(.hidden)').length;
  return {filtered:a, restored:b};`);

R.overflow={};
for(const w of [1440,1280,1024,768]){
  await send('Emulation.setDeviceMetricsOverride',{width:w,height:1000,deviceScaleFactor:1,mobile:false});
  await sleep(700);
  R.overflow[w]=await ev(`
    var d=document.documentElement;
    var wide=[].slice.call(document.querySelectorAll('.main *')).filter(function(e){
      var r=e.getBoundingClientRect(); return r.right>d.clientWidth+1.5;})
      .slice(0,4).map(function(e){return e.className||e.tagName;});
    return {scrollW:d.scrollWidth, clientW:d.clientWidth, over:d.scrollWidth>d.clientWidth+1, wide:wide};`);
}
await send('Emulation.clearDeviceMetricsOverride');

/* 구버전은 대표 정의(만기 2.0~6.2일)와 뿌리부터 어긋나는 동결 스냅샷이다. 링크만 떼도 주소를
   직접 치면 열리므로 배포에서 파일 자체를 뺐다. 파일이 되살아나거나 링크가 붙으면 여기서 걸린다.
   archive.html 은 파일 추적이 본질이라 전 파일을 싣는다(D-20 예외) — 링크가 아니라 이름만 본다. */
R.legacyInRepo = fs.existsSync(path.join(REPO, 'glossary-legacy.html'));
R.legacyUnlinked = fs.readdirSync(REPO)
  .filter(f => f.endsWith('.html') && f !== 'archive.html')
  .filter(f => /(?:href|src)="[^"]*glossary-legacy\.html/.test(fs.readFileSync(path.join(REPO, f), 'utf8')));
R.legacy = {inRepo: R.legacyInRepo};

R.console = errs;
fs.writeFileSync(OUT, JSON.stringify(R,null,1));
console.log(JSON.stringify({cards:R.cards.n, missingFields:R.cards.missing.length,
  images:R.images.n, broken:R.images.broken.length, anchors:R.anchors.n, deadAnchors:R.anchors.dead,
  marks:R.marks, lightbox:R.lightbox, search:R.search,
  overflow:Object.fromEntries(Object.entries(R.overflow).map(([k,v])=>[k,v.over?('OVER '+v.scrollW+'>'+v.clientW+' '+JSON.stringify(v.wide)):'ok'])),
  legacyInRepo:R.legacyInRepo, legacyStillLinked:R.legacyUnlinked,
  legacyVerdict:(R.legacyInRepo||R.legacyUnlinked.length)?'FAIL':'배포에서 빠짐 · 링크 0건',
  consoleErrors:errs.length},null,1));

/* ── 판정 ──
   2026-08-30 이전까지 이 파일은 process.exit(0) 무조건이었다. 자기 출력에 legacyVerdict:'FAIL'
   을 찍으면서도 종료코드에 넣지 않았고, marks.offscreen · lightbox · overflow 는 이 파일도
   gate_glossary.js 도 판정하지 않았다(게이트는 카드·필드·이미지·앵커·콘솔만 본다).
   기준은 새로 발명하지 않는다 — 이 파일이 이미 재고 있는 값의 "결함이면 무엇인가"만 적는다.
   곳수(카드 50 · 앵커 734 · 마커 50)는 박지 않는다. 내용이 늘면 같이 늘 값이다. */
const fails = [];
if(R.cards.n === 0) fails.push('용어 카드 0건 — 검사 대상이 사라졌다');
if(R.cards.missing.length) fails.push('5필드 빠진 카드 ' + R.cards.missing.length + '건: ' + R.cards.missing.slice(0,5).join(', '));
if(R.images.n === 0) fails.push('.crop 이미지 0건');
if(R.images.broken.length) fails.push('깨진 이미지 ' + R.images.broken.length + '건: ' + R.images.broken.slice(0,4).join(', '));
if(R.anchors.n === 0) fails.push('앵커 0건');
if(R.anchors.dead.length) fails.push('죽은 앵커 ' + JSON.stringify(R.anchors.dead.slice(0,6)));
/* 마커가 크롭 밖(offscreen)이면 캡처의 엉뚱한 자리를 가리키는 것이고, 크기 0이면 아예 안 보인다.
   픽셀 대조는 verify_shotmarks.py 가 따로 하지만 그쪽은 glossary.html 을 브라우저로 띄우지 않는다. */
if(R.marks.n === 0) fails.push('마커 0건');
if(R.marks.offscreen) fails.push('크롭 밖 마커 ' + R.marks.offscreen + '건');
if(R.marks.zero) fails.push('크기 0 마커 ' + R.marks.zero + '건');
/* 라이트박스 — 열림·재열림은 기능 자체다. ESC 닫힘은 화면이 스스로 약속한 것이다:
   glossary.html 의 닫기 버튼 라벨이 「닫기 (Esc)」다. 라벨이 바뀌면 이 판정도 같이 풀린다.
   src·markLeft 는 누른 크롭이 선언한 값과 맞는지로 본다(검증기가 값을 들고 있지 않다).
   backdropCloses 는 화면이 약속한 적 없는 동작이라 판정하지 않는다 — 아래에서 보고만 한다. */
const LB = R.lightbox;
if(!LB.opens) fails.push('라이트박스가 열리지 않는다');
if(!LB.reopens) fails.push('라이트박스가 다시 열리지 않는다');
if(LB.src !== LB.declaredSrc) fails.push('라이트박스 이미지 ' + LB.src + ' ≠ 크롭 선언 ' + LB.declaredSrc);
if(LB.markLeft !== LB.declaredLeft) fails.push('라이트박스 마커 ' + LB.markLeft + ' ≠ 크롭 선언 ' + LB.declaredLeft);
if(/Esc/i.test(LB.closeLabel || '') && !LB.escCloses)
  fails.push('닫기 버튼이 「' + LB.closeLabel + '」 라고 적어 두고 ESC 로 안 닫힌다');
if(!LB.closeLabel) fails.push('라이트박스 닫기 버튼(#lb-close) 이 없다');
/* 검색 — 좁혀야 좁힌 것이고, 지우면 전건이 돌아와야 한다. 걸리는 곳수는 판정하지 않는다. */
if(!(R.search.filtered > 0)) fails.push('검색 PwD 0건 — 검색이 죽었거나 그 기호가 사라졌다');
if(!(R.search.filtered < R.search.restored)) fails.push('검색이 좁히지 않는다 ' + R.search.filtered + '/' + R.search.restored);
if(R.search.restored !== R.cards.n) fails.push('검색 지운 뒤 ' + R.search.restored + ' ≠ 카드 ' + R.cards.n);
Object.keys(R.overflow).forEach(w => { const o = R.overflow[w];
  if(o.over) fails.push('가로 넘침 @' + w + 'px — ' + o.scrollW + '>' + o.clientW + ' ' + JSON.stringify(o.wide)); });
/* 위 112-114행 주석이 근거 — 구버전은 뿌리부터 어긋난 동결본이라 배포에서 파일을 뺐다.
   그 판정을 이미 문자열로 찍고 있었는데 종료코드에 안 넣던 자리다. */
if(R.legacyInRepo) fails.push('구버전 glossary-legacy.html 이 배포 레포에 되살아났다');
if(R.legacyUnlinked.length) fails.push('구버전 링크 잔존: ' + R.legacyUnlinked.join(', '));
if(errs.length) fails.push('콘솔 에러 ' + errs.length + '건: ' + errs.slice(0,3).join(' | '));

console.log('-- 판정하지 않고 보고만 -- 배경 클릭 닫힘=' + LB.backdropCloses +
            ' (화면이 약속한 동작이 아니라 기준을 댈 수 없다)');
console.log(fails.length ? '판정: FAIL ' + fails.length + '건\n - ' + fails.join('\n - ') : '판정: PASS');
try{ch.kill('SIGKILL');}catch(e){} server.close(); fs.rmSync(prof,{recursive:true,force:true});
process.exit(fails.length ? 1 : 0);
})().catch(e=>{ console.error('FAIL',e); process.exit(1); });
