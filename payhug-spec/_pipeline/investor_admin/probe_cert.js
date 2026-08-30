const http=require('http'),fs=require('fs'),path=require('path'),os=require('os'),{spawn}=require('child_process');
const REPO='/Users/semi/cursor/payhug-investor-prototype';
const PORT=8990+(process.pid%9),DPORT=9690+(process.pid%9);
const DL=fs.mkdtempSync(path.join(os.tmpdir(),'cert-'));
const CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const MIME={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.pdf':'application/pdf'};
const server=http.createServer((q,r)=>{const p=path.join(REPO,decodeURIComponent(q.url.split('?')[0]));
  fs.readFile(p,(e,b)=>{if(e){console.log('404',q.url);r.writeHead(404);r.end('');return;}
  r.writeHead(200,{'Content-Type':MIME[path.extname(p)]||'application/octet-stream'});r.end(b);});});
let id=0,ws,pend=new Map();
function send(m,p){const i=++id;ws.send(JSON.stringify({id:i,method:m,params:p||{}}));return new Promise(res=>pend.set(i,{res}));}
async function ev(x){const r=await send('Runtime.evaluate',{expression:'(function(){'+x+'})()',returnByValue:true});
  if(r.exceptionDetails)throw new Error(JSON.stringify(r.exceptionDetails));return r.result.value;}
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  await new Promise(r=>server.listen(PORT,r));
  const prof=fs.mkdtempSync(path.join(os.tmpdir(),'cp-'));
  const ch=spawn(CHROME,['--headless=new','--remote-debugging-port='+DPORT,'--user-data-dir='+prof,'--no-first-run','--disable-gpu','about:blank'],{stdio:'ignore'});
  let t=null;for(let i=0;i<60&&!t;i++){await sleep(300);try{t=await new Promise((res,rej)=>{http.get({host:'127.0.0.1',port:DPORT,path:'/json'},r=>{let d='';r.on('data',c=>d+=c);r.on('end',()=>res(JSON.parse(d)));}).on('error',rej);});}catch(e){t=null;}}
  ws=new WebSocket(t.find(x=>x.type==='page').webSocketDebuggerUrl);
  await new Promise(r=>ws.addEventListener('open',r));
  ws.addEventListener('message',e=>{const m=JSON.parse(e.data);if(m.id&&pend.has(m.id)){pend.get(m.id).res(m.result);pend.delete(m.id);}
    else if(m.method&&m.method.indexOf('Browser.download')===0) console.log('EVT',m.method,JSON.stringify(m.params));});
  await send('Runtime.enable');
  await send('Browser.setDownloadBehavior',{behavior:'allow',downloadPath:DL,eventsEnabled:true});
  await send('Page.navigate',{url:'http://127.0.0.1:'+PORT+'/index.html'});
  await sleep(1500);
  console.log('href =', await ev('go("certificate","default"); var a=document.querySelector(\'[data-act="cert-pdf"]\'); return {href:a.getAttribute("href"), abs:a.href, dl:a.getAttribute("download"), rects:a.getClientRects().length};'));
  await ev('document.querySelector(\'[data-act="cert-pdf"]\').click(); return 1;');
  await sleep(3000);
  console.log('DL dir:', fs.readdirSync(DL).map(f=>f+' '+fs.statSync(path.join(DL,f)).size));
  ws.close();ch.kill();server.close();process.exit(0);
})().catch(e=>{console.error(e);process.exit(1);});
