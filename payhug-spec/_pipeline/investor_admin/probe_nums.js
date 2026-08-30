/* 화면 전 조합에서 0.11* / 2.24 / 비중합 을 훑어 실제 표기 문자열을 확인한다 */
const http=require('http'),fs=require('fs'),path=require('path'),os=require('os'),{spawn}=require('child_process');
const REPO=process.env.PROTO_REPO||'/Users/semi/cursor/payhug-investor-prototype';
const PORT=8900+(process.pid%90),DPORT=9600+(process.pid%90);
const CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const MIME={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.png':'image/png'};
const server=http.createServer((q,r)=>{const p=path.join(REPO,decodeURIComponent(q.url.split('?')[0]));
  fs.readFile(p,(e,b)=>{ if(e){r.writeHead(404);r.end('');return;} r.writeHead(200,{'Content-Type':MIME[path.extname(p)]||'application/octet-stream'});r.end(b);});});
let id=0,ws,pend=new Map();
function send(m,p){const i=++id;ws.send(JSON.stringify({id:i,method:m,params:p||{}}));return new Promise((res,rej)=>pend.set(i,{res,rej}));}
async function ev(x){const r=await send('Runtime.evaluate',{expression:'(function(){'+x+'})()',returnByValue:true});
  if(r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails));return r.result.value;}
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  await new Promise(r=>server.listen(PORT,r));
  const prof=fs.mkdtempSync(path.join(os.tmpdir(),'pn-'));
  const ch=spawn(CHROME,['--headless=new','--remote-debugging-port='+DPORT,'--user-data-dir='+prof,'--no-first-run','--disable-gpu','--window-size=1440,1200','about:blank'],{stdio:'ignore'});
  let t=null;for(let i=0;i<60&&!t;i++){await sleep(300);try{t=await new Promise((res,rej)=>{http.get({host:'127.0.0.1',port:DPORT,path:'/json'},r=>{let d='';r.on('data',c=>d+=c);r.on('end',()=>res(JSON.parse(d)));}).on('error',rej);});}catch(e){t=null;}}
  const pg=t.find(x=>x.type==='page');ws=new WebSocket(pg.webSocketDebuggerUrl);
  await new Promise(r=>ws.addEventListener('open',r));
  ws.addEventListener('message',e=>{const m=JSON.parse(e.data);if(m.id&&pend.has(m.id)){pend.get(m.id).res(m.result);pend.delete(m.id);}});
  await send('Runtime.enable');
  await send('Page.navigate',{url:process.env.PROTO_URL||('http://127.0.0.1:'+PORT+'/index.html')});
  await sleep(1800);
  const out=await ev(`
    var T=[['invest-assets','default'],['invest-profit','default'],['invest-profit','monthly'],
      ['certificate','default'],['xls-profit-daily','default'],['xls-profit-status','default'],
      ['xls-assets-status','default'],['xls-assets-merchant','default']];
    var res={};
    T.forEach(function(t){
      go(t[0],t[1]);
      var s=document.querySelector('section.screen[data-screen="'+t[0]+'"]').textContent;
      var r={};
      (s.match(/0\\.1[0-9]+ *%?/g)||[]).forEach(function(x){ r[x.trim()]=(r[x.trim()]||0)+1; });
      (s.match(/2\\.2[0-9]+ *%?/g)||[]).forEach(function(x){ r[x.trim()]=(r[x.trim()]||0)+1; });
      res[t[0]+'/'+t[1]]=r;
    });
    go('invest-assets','default');
    return res;
  `);
  console.log(JSON.stringify(out,null,1));
  ws.close();ch.kill();server.close();process.exit(0);
})().catch(e=>{console.error(e);process.exit(1);});
