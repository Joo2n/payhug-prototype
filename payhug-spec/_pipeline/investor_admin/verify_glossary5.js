/* 용어 해설 재조판본 헤드리스 검증 — 창을 띄우지 않는다(--headless=new). */
const http=require('http'), fs=require('fs'), path=require('path'), os=require('os'),
      {spawn}=require('child_process');
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
const ch=spawn(CHROME,['--headless=new','--remote-debugging-port='+DPORT,'--user-data-dir='+prof,
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

R.lightbox = await ev(`
  var b=document.querySelector('.crop'); b.click();
  var lb=document.getElementById('lb');
  var on=lb.classList.contains('on');
  var img=document.getElementById('lb-img').getAttribute('src');
  var mk=document.getElementById('lb-mark').style.left;
  document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape'}));
  var closed=!lb.classList.contains('on');
  b.click(); var on2=lb.classList.contains('on');
  document.body.click(); var closed2=!lb.classList.contains('on');
  return {opens:on, src:img, markLeft:mk, escCloses:closed, reopens:on2, backdropCloses:closed2};`);

R.search = await ev(`
  var q=document.getElementById('q');
  q.value='PSD'; q.dispatchEvent(new Event('input'));
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
try{ch.kill('SIGKILL');}catch(e){} server.close(); fs.rmSync(prof,{recursive:true,force:true});
process.exit(0);
})().catch(e=>{ console.error('FAIL',e); process.exit(1); });
