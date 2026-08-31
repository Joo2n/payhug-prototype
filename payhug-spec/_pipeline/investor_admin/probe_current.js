/* 현재 app.html(타 조 재빌드본) 대상 최소 점검 — 상태 20 해시 도달 + 콘솔 에러 */
const http=require('http'), fs=require('fs'), path=require('path'), os=require('os'), {spawn}=require('child_process');
const CHROME_DL = require('./chrome_dl');
const PH_DL = CHROME_DL.dir();
const REPO='/Users/semi/cursor/payhug-investor-admin';
const PORT=8600+(process.pid%90), DPORT=9600+(process.pid%90);
const MIME={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8'};
const srv=http.createServer((q,s)=>{const p=path.join(REPO,decodeURIComponent(q.url.split('?')[0]));
  fs.readFile(p,(e,b)=>{if(e){s.writeHead(404);s.end();return;}s.writeHead(200,{'Content-Type':MIME[path.extname(p)]||'application/octet-stream'});s.end(b);});});
let id=0,ws,pend=new Map(),errs=[];
const send=(m,p)=>{const i=++id;ws.send(JSON.stringify({id:i,method:m,params:p||{}}));return new Promise(r=>pend.set(i,r));};
const ev=async e=>{const r=await send('Runtime.evaluate',{expression:'(function(){'+e+'})()',returnByValue:true});
  if(r.exceptionDetails) return 'ERR '+JSON.stringify(r.exceptionDetails.exception?.description||r.exceptionDetails.text);
  return r.result.value;};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  await new Promise(r=>srv.listen(PORT,r));
  const prof=fs.mkdtempSync(path.join(os.tmpdir(),'phprobe-'));
  const ch=spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    ['--headless=new','--remote-debugging-port='+DPORT,CHROME_DL.args(PH_DL, prof)[0],'--no-first-run','--disable-gpu','--window-size=1440,1200','about:blank'],{stdio:'ignore'});
  let t=null;for(let i=0;i<60&&!t;i++){await sleep(300);
    try{t=await new Promise((res,rej)=>http.get({host:'127.0.0.1',port:DPORT,path:'/json'},r=>{let d='';r.on('data',c=>d+=c);r.on('end',()=>res(JSON.parse(d)))}).on('error',rej));}catch(e){t=null;}}
  const pg=t.find(x=>x.type==='page');
  ws=new WebSocket(pg.webSocketDebuggerUrl);await new Promise(r=>ws.addEventListener('open',r));
  ws.addEventListener('message',m=>{const o=JSON.parse(m.data);
    if(o.id&&pend.has(o.id)){pend.get(o.id)(o.result);pend.delete(o.id);return;}
    if(o.method==='Runtime.exceptionThrown')errs.push('exception: '+(o.params.exceptionDetails.exception?.description||o.params.exceptionDetails.text));
    if(o.method==='Log.entryAdded'&&o.params.entry.level==='error')errs.push('log: '+o.params.entry.text);
    if(o.method==='Runtime.consoleAPICalled'&&o.params.type==='error')errs.push('console: '+o.params.args.map(a=>a.value||a.description).join(' '));});
  await send('Runtime.enable');await send('Log.enable');await send('Page.enable');
  await send('Page.navigate',{url:'http://127.0.0.1:'+PORT+'/app.html'});await sleep(1800);

  const S=[['invest-assets','page2'],['invest-assets','download'],['invest-assets','cert-confirm'],['invest-assets','empty'],
   ['invest-profit','monthly'],['invest-profit','empty'],
   ['merchants','filter-open'],['merchants','filtered'],['merchants','empty'],
   ['acquisition-list','confirm'],['acquisition-list','signing'],['acquisition-list','done'],
   ['contracts','all'],['contracts','downloaded'],['contracts','empty'],['coocon','confirm'],
   ['password','weak'],['password','error'],['password','done']];
  let ok=0,bad=[];
  for(const [sc,st] of S){
    await ev('location.hash="#'+sc+'/'+st+'"; return 1;'); await sleep(120);
    const r=await ev('var s=document.querySelector(\'section.screen[data-screen="'+sc+'"]\');'+
      'return {v:!s.hidden, st:s.dataset.state, h:Math.round(s.getBoundingClientRect().height)};');
    if(r&&r.v&&r.st===st&&r.h>200) ok++; else bad.push(sc+'/'+st+' → '+JSON.stringify(r));
  }
  const sc=await ev('return window.__selfcheck? JSON.stringify(window.__selfcheck()) : "no selfcheck";');
  console.log('상태 도달: '+ok+'/20'); bad.forEach(b=>console.log('  FAIL',b));
  console.log('콘솔 에러: '+errs.filter(e=>!/favicon/.test(e)).length);
  errs.filter(e=>!/favicon/.test(e)).slice(0,10).forEach(e=>console.log('  -',e));
  console.log('selfcheck: '+sc);
  ws.close();ch.kill();srv.close();process.exit(0);
})().catch(e=>{console.error('PROBE ERROR',e.message);process.exit(1);});
