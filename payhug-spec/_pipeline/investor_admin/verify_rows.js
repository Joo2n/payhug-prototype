/* 행 호버·순번 열·건수 자리 실측 — 창 없다(--headless=new).
   CDP 로 실제 마우스를 올리고 실제 Tab 키를 눌러 computed style 을 읽는다.
   확대는 transform 이라 흐름을 밀지 않는다 — 표 폭·표 높이·이웃 행 위치·문서 가로폭으로 잰다. */
const http=require('http'),fs=require('fs'),path=require('path'),os=require('os'),{spawn}=require('child_process');
const CHROME_DL = require('./chrome_dl');
const PH_DL = CHROME_DL.dir();
const REPO='/Users/semi/cursor/payhug-investor-admin';
const OUT ='/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_rows_result.json';
const OUTDIR='/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin';
/* 숫자 기대값은 검증기에 손으로 적지 않는다 — daily_ledger.py 가 내는 원장 사실값을 읽는다.
   verify_identity.js:13 · verify_proto.js:14 · verify_period.js:14 와 같은 원천이다. */
const FACTS=JSON.parse(fs.readFileSync(path.join(OUTDIR,'ledger_facts.json'),'utf8'));
const ROSTER=FACTS.merchants.length;   /* 가맹점 로스터 곳수 — 계약기록 건수도 같은 명단이다 */
const PORT=8770+(process.pid%40),DPORT=9470+(process.pid%40);
const CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const MIME={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.png':'image/png','.webp':'image/webp'};
const server=http.createServer((q,r)=>{const p=path.join(REPO,decodeURIComponent(q.url.split('?')[0]));
  fs.readFile(p,(e,b)=>{ if(e){r.writeHead(404);r.end('');return;} r.writeHead(200,{'Content-Type':MIME[path.extname(p)]||'application/octet-stream'});r.end(b);});});
let id=0,ws,pend=new Map(); const cons=[];
function send(m,p){const i=++id;ws.send(JSON.stringify({id:i,method:m,params:p||{}}));return new Promise((res,rej)=>pend.set(i,{res,rej}));}
async function ev(x){const r=await send('Runtime.evaluate',{expression:'(function(){'+x+'})()',returnByValue:true,awaitPromise:true});
  if(r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails));return r.result.value;}
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const mouse=(x,y)=>send('Input.dispatchMouseEvent',{type:'mouseMoved',x:x,y:y,button:'none',buttons:0,clickCount:0});
async function tabKey(){
  await send('Input.dispatchKeyEvent',{type:'rawKeyDown',windowsVirtualKeyCode:9,nativeVirtualKeyCode:9,key:'Tab',code:'Tab'});
  await send('Input.dispatchKeyEvent',{type:'keyUp',windowsVirtualKeyCode:9,nativeVirtualKeyCode:9,key:'Tab',code:'Tab'});
}
const R={hover:[],focus:[],cols:[],counts:[],leftovers:[],console:cons};
function P(a,t,d){ d.t=t; d.pass=!!d.pass; a.push(d); }

const PROBE = (sel, idx) => `
  var all=document.querySelectorAll(${JSON.stringify(sel)}), el=all[${idx}];
  if(!el) return null;
  var cs=getComputedStyle(el), r=el.getBoundingClientRect();
  var sc=el.closest('.tbl-scroll')||el.closest('.card')||el.closest('.tbl-wrap');
  var sib=all[${idx}+1]||all[${idx}-1];
  var box=el.closest('table')||el.parentElement, bb=box.getBoundingClientRect();
  return {bg:cs.backgroundColor, tf:cs.transform, cur:cs.cursor,
          h:Math.round(r.height*100)/100, x:Math.round(r.left+r.width/2), y:Math.round(r.top+r.height/2),
          boxW:Math.round(bb.width*100)/100, boxH:Math.round(bb.height*100)/100,
          sibTop: sib?Math.round(sib.getBoundingClientRect().top*100)/100:null,
          docW: document.documentElement.scrollWidth, winW: window.innerWidth,
          scW: sc?sc.scrollWidth:null, scC: sc?sc.clientWidth:null};
`;

let cur=null;
/* 고정 900ms 대기는 app.html(245KB) 초기화와 경주한다 — 2026-09-04 전종 실행에서 `psz is not defined`
   로 한 번 죽고 재실행에서 통과했다. 앱 전역(go·psz)이 실제로 잡힐 때까지 기다린다(최대 8초). */
async function goto(url){
  if(cur===url) return;
  await send('Page.navigate',{url:url});
  for(let i=0;i<80;i++){
    await sleep(100);
    let ok=false;
    try{ ok=await ev("return typeof go==='function' && typeof psz==='function' && !!document.querySelector('section.screen');"); }catch(e){ ok=false; }
    if(ok) break;
  }
  await sleep(300); cur=url;
}

async function probeRow(label, url, sel, idx){
  await goto(url);
  await mouse(5,5); await sleep(200);
  const pre = await ev(PROBE(sel, idx));
  if(!pre){ P(R.hover, label, {pass:false, err:'행 없음 '+sel+'['+idx+']'}); return; }
  await mouse(pre.x, pre.y); await sleep(320);
  const post = await ev(PROBE(sel, idx));
  await mouse(5,5); await sleep(320);
  const off = await ev(PROBE(sel, idx));
  const grew    = post.tf !== 'none' && post.tf !== pre.tf && post.h > pre.h;
  const bgMoved = post.bg !== pre.bg;
  const pointer = post.cur === 'pointer';
  const stable  = post.boxW===pre.boxW && post.boxH===pre.boxH && post.sibTop===pre.sibTop && post.docW===pre.docW;
  const back    = off.tf===pre.tf && off.bg===pre.bg;
  const noScr   = (post.scW===null) || (post.scW <= post.scC);
  const noDoc   = post.docW <= post.winW;
  P(R.hover, label, {pass: grew&&bgMoved&&pointer&&stable&&back&&noScr&&noDoc,
    확대:post.tf, 배경:pre.bg+' → '+post.bg, 커서:post.cur,
    표폭:pre.boxW+' → '+post.boxW, 표높이:pre.boxH+' → '+post.boxH,
    이웃행top:pre.sibTop+' → '+post.sibTop, 행사각형:pre.h+' → '+post.h,
    가로스크롤:post.scW+'/'+post.scC, 문서폭:post.docW+'/'+post.winW, 떼면복귀:back});
}

/* 원본 어드민은 레포 전체 tabIndex 0건 — 표 행·목록 행이 키보드 초점 대상이 아니다.
   행에 tabindex 를 얹지 않았는지, Tab 을 아무리 눌러도 행이 잡히지 않는지 확인한다.
   선택 수단은 행 클릭과 행 안 <input type=checkbox> 다. */
async function probeNoTabStop(label, url, sel, live){
  await send('Page.navigate',{url:url}); await sleep(1000); cur=url;
  const attrs = await ev(`
    var rows=document.querySelectorAll(${JSON.stringify(sel)});
    var tab=0, role=0, aria=0;
    for(var i=0;i<rows.length;i++){
      if(rows[i].hasAttribute('tabindex')) tab++;
      if(rows[i].hasAttribute('role')) role++;
      if(rows[i].hasAttribute('aria-checked')) aria++;
    }
    return {n:rows.length, tab:tab, role:role, aria:aria};
  `);
  let caught=null;
  for(let i=0;i<90;i++){
    await tabKey();
    if(await ev(`var a=document.activeElement; return !!(a&&a.matches&&a.matches(${JSON.stringify(sel)}));`)){ caught=i+1; break; }
  }
  /* 행 클릭으로는 여전히 선택된다 — 스크립트가 없는 정적 낱장은 대상이 아니다 */
  const picked = !live ? {changed:null} : await ev(`
    var r=document.querySelector(${JSON.stringify(sel)});
    if(!r) return null;
    var before=r.className;
    r.click();
    var after=document.querySelector(${JSON.stringify(sel)}).className;
    return {before:before, after:after, changed:before!==after};
  `);
  P(R.focus, label, {pass: attrs.n>0 && attrs.tab===0 && attrs.role===0 && attrs.aria===0 &&
                           caught===null && (!live || (!!picked && picked.changed)),
                     행수:attrs.n, tabindex달린행:attrs.tab, role달린행:attrs.role,
                     ariaChecked달린행:attrs.aria, Tab으로잡힌횟수:caught,
                     행클릭선택:picked&&picked.changed});
}

async function main(){
  await new Promise(r=>server.listen(PORT,r));
  const prof=fs.mkdtempSync(path.join(os.tmpdir(),'vr-'));
  const ch=spawn(CHROME,['--headless=new','--remote-debugging-port='+DPORT,CHROME_DL.args(PH_DL, prof)[0],'--no-first-run','--disable-gpu','--window-size=1440,1200','about:blank'],{stdio:'ignore'});
  let t=null;for(let i=0;i<60&&!t;i++){await sleep(300);try{t=await new Promise((res,rej)=>{http.get({host:'127.0.0.1',port:DPORT,path:'/json'},r=>{let d='';r.on('data',c=>d+=c);r.on('end',()=>res(JSON.parse(d)));}).on('error',rej);});}catch(e){t=null;}}
  const pg=t.find(x=>x.type==='page'); ws=new WebSocket(pg.webSocketDebuggerUrl);
  await new Promise(r=>ws.addEventListener('open',r));
  ws.addEventListener('message',e=>{const m=JSON.parse(e.data);
    if(m.method==='Runtime.consoleAPICalled'&&m.params.type==='error') cons.push(JSON.stringify(m.params.args.map(a=>a.value||a.description)));
    if(m.method==='Runtime.exceptionThrown') cons.push(m.params.exceptionDetails.text);
    if(m.id&&pend.has(m.id)){pend.get(m.id).res(m.result);pend.delete(m.id);}});
  await send('Runtime.enable'); await send('Page.enable');
  const U = p => 'http://127.0.0.1:'+PORT+'/'+p;

  /* ── 호버 — 두 목록 전 행, 통합본·정적본 양쪽 ──
     계약기록에서 고를 수 있는 행은 서명이 끝난 계약뿐이다(서명 대기 큐에 남은 가맹점은 문서가 없다).
     1쪽 행수는 그 수와 보기 갯수 기본값 중 작은 쪽이다 — 검증기에 적지 않고 화면이 세는 수를 받는다. */
  await goto(U('app.html#contracts/default'));
  const CT_ROWS = await ev(`return Math.min(psz('ct-tbl'), ctSignedCount(CONTRACTS));`);
  const CT_LOCK = await ev(`return document.querySelectorAll(
    'section[data-screen="contracts"] tbody input.chk[disabled]').length;`);
  P(R.cols, '계약기록 — 고를 수 있는 행 ' + CT_ROWS + ' · 잠긴 행 ' + CT_LOCK + ' = 총 ' + ROSTER,
    {pass: CT_ROWS > 0 && CT_ROWS + CT_LOCK === ROSTER, 고를수있는행:CT_ROWS, 잠긴행:CT_LOCK, 총:ROSTER});
  for(let i=0;i<CT_ROWS;i++) await probeRow('통합본 계약기록 '+(i+1)+'행', U('app.html#contracts/default'),
    'section[data-screen="contracts"] tbody tr.clickable', i);
  for(let j=0;j<3;j++) await probeRow('통합본 서명대기 '+(j+1)+'행', U('app.html#acquisition-list/default'),
    'section[data-screen="acquisition-list"] .sign-row.pickable', j);
  for(let i=0;i<CT_ROWS;i++) await probeRow('정적 계약기록 '+(i+1)+'행', U('contracts.html'), 'tbody tr.clickable', i);
  await goto(U('contracts.html'));
  const ctStatic = await ev(`return {clickable:document.querySelectorAll('tbody tr.clickable').length,
                                     locked:document.querySelectorAll('tbody input.chk[disabled]').length};`);
  P(R.cols, '정적 계약기록도 같은 갈림 — 고를 수 있는 행 ' + CT_ROWS,
    {pass: ctStatic.clickable === CT_ROWS && ctStatic.locked === CT_LOCK, 낱장:ctStatic,
     통합본:{clickable:CT_ROWS, locked:CT_LOCK}});
  for(let j=0;j<3;j++) await probeRow('정적 서명대기 '+(j+1)+'행', U('acquisition.html'), '.sign-row.pickable', j);
  /* 서명이 끝난 행은 대기 목록에서 빠진다 — 남는 행은 전부 고를 수 있다 */
  await goto(U('acquisition--done.html'));
  const done = await ev(`var rows=document.querySelectorAll('.sign-row');
    return {n:rows.length, done:document.querySelectorAll('.sign-row.done').length,
            pick:document.querySelectorAll('.sign-row.pickable').length};`);
  P(R.hover,'서명 완료 행은 목록에서 빠진다',{pass:done.n===1&&done.done===0&&done.pick===1,
    남은행:done.n,서명완료행:done.done,고를수있는행:done.pick});

  /* ── 포커스 ── */
  await probeNoTabStop('통합본 계약기록 행 — 키보드 초점 대상 아님·행 클릭 선택 유지', U('app.html#contracts/default'), 'section[data-screen="contracts"] tbody tr.clickable', true);
  await probeNoTabStop('통합본 서명대기 행 — 키보드 초점 대상 아님·행 클릭 선택 유지', U('app.html#acquisition-list/default'), 'section[data-screen="acquisition-list"] .sign-row.pickable', true);
  await probeNoTabStop('정적 계약기록 행 — 키보드 초점 대상 아님·행 클릭 선택 유지', U('contracts.html'), 'tbody tr.clickable');
  await probeNoTabStop('정적 서명대기 행 — 키보드 초점 대상 아님·행 클릭 선택 유지', U('acquisition.html'), '.sign-row.pickable');
  cur=null;

  /* ── 순번 열 ── */
  await goto(U('app.html#contracts/default'));
  const p1 = await ev(`
    function nos(){ return [].map.call(document.querySelectorAll('section[data-screen="contracts"] tbody td.no'),function(d){return d.textContent;}); }
    function mids(){ return [].map.call(document.querySelectorAll('section[data-screen="contracts"] tbody td.mono'),function(d){return d.textContent;}); }
    var head=document.querySelector('section[data-screen="contracts"] thead th.no');
    var ths=document.querySelectorAll('section[data-screen="contracts"] thead th');
    var r={label:head&&head.textContent, 열순서:[].map.call(ths,function(h){return h.querySelector('input')?'체크박스':h.textContent.trim();}),
           page1:nos(), mid1:mids(),
           pageBtns:document.querySelectorAll('section[data-screen="contracts"] [data-act="ct-page"]').length};
    return r;
  `);
  /* [기준 교체 2026-08-30] 예전 이 자리는 2쪽 버튼을 눌러 순번 11–16 을 보았다.
     로스터가 9건이 되면서 기본 보기 10건 안에 다 들어가 2쪽 자체가 없다(보기 갯수 10/20/50 어디서도).
     쪽 버튼이 0개인 것을 판정으로 세우고, 순번 축은 1쪽 전건 1:1 로 본다.
     건수는 검증기에 적지 않는다 — 원장 사실값 FACTS.merchants 길이를 쓴다. */
  const NROW = FACTS.merchants.length;
  const want1 = Array.from({length:NROW}, function(_, i){ return String(i + 1); }).join(',');
  P(R.cols,'순번 열 머리 No · 체크박스 열이 앞',{pass:p1.label==='No'&&p1.열순서[0]==='체크박스'&&p1.열순서[1]==='No',열순서:p1.열순서});
  P(R.cols,'1쪽 순번 1–'+NROW,{pass:p1.page1.join(',')===want1,값:p1.page1.join(','),기대:want1});
  P(R.cols,'로스터가 기본 보기 안 — 쪽 버튼 0개',{pass:p1.pageBtns===0,값:p1.pageBtns});
  P(R.cols,'순번이 행 순서와 1:1',{pass:p1.page1.every(function(v,i){return +v===i+1;})&&p1.mid1.length===NROW,
    행:p1.page1.map(function(v,i){return v+':'+p1.mid1[i];})});
  await goto(U('contracts.html'));
  const st = await ev(`return {head:(document.querySelector('thead th.no')||{}).textContent,
    vals:[].map.call(document.querySelectorAll('tbody td.no'),function(d){return d.textContent;}).join(',')};`);
  P(R.cols,'정적 계약기록 순번 1–'+NROW,{pass:st.head==='No'&&st.vals===want1,머리:st.head,값:st.vals});

  /* ── 건수 자리 ── */
  await goto(U('app.html#contracts/default'));
  const cnt = await ev(`
    var sec=document.querySelector('section[data-screen="contracts"]');
    function read(){ var p=sec.querySelector('.pagination .sel-pill'), pg=sec.querySelector('.pagination').getBoundingClientRect();
      return {text:p?p.textContent:null, left:p?Math.round(p.getBoundingClientRect().left-pg.left):null,
              inHead:!!sec.querySelector('.tbl-head-bar .sel-pill'),
              head:sec.querySelector('.tbl-head-bar').textContent.replace(/\\s+/g,' ').trim()}; }
    var a=read(); sec.querySelector('tbody tr.clickable').click();
    return new Promise(function(res){ setTimeout(function(){ res({a:a,b:read()}); },350); });
  `);
  P(R.counts,'계약기록 선택 건수 = 목록 아래 왼쪽',{pass:cnt.a.text==='3건 선택'&&cnt.a.left<40&&!cnt.a.inHead,
    표기:cnt.a.text,왼쪽px:cnt.a.left,머리에남음:cnt.a.inHead});
  P(R.counts,'행을 누르면 선택 개수가 바뀐다',{pass:cnt.b.text==='2건 선택',전:cnt.a.text,후:cnt.b.text});
  P(R.counts,'계약기록 머리 = 총 '+ROSTER+'건 · 표시 없음',
    {pass:new RegExp('총 '+ROSTER+'건').test(cnt.a.head)&&!/표시/.test(cnt.a.head),머리:cnt.a.head});
  await goto(U('app.html#acquisition-list/default'));
  const aq = await ev(`
    var sec=document.querySelector('section[data-screen="acquisition-list"]');
    var f=sec.querySelector('.sign-foot'), c=f.querySelector('.sel-count'), b=f.querySelector('.btn');
    var fr=f.getBoundingClientRect(), cr=c.getBoundingClientRect(), br=b.getBoundingClientRect();
    var before=c.textContent.replace(/\\s+/g,' ').trim();
    sec.querySelector('.sign-row.pickable').click();
    return new Promise(function(res){ setTimeout(function(){ res({전:before, 후:c.textContent.replace(/\\s+/g,' ').trim(),
      왼쪽px:Math.round(cr.left-fr.left), 버튼가운데:Math.abs((br.left+br.width/2)-(fr.left+fr.width/2))<2,
      버튼위:cr.bottom<=br.top}); },350); });
  `);
  P(R.counts,'서명대기 선택 건수 = 목록 아래 왼쪽',{pass:aq.왼쪽px<40&&!aq.버튼위,왼쪽px:aq.왼쪽px,버튼위:aq.버튼위});
  P(R.counts,'서명 버튼은 그대로 가운데',{pass:aq.버튼가운데,가운데:aq.버튼가운데});
  P(R.counts,'선택 개수 갱신',{pass:aq.전==='선택 0건'&&aq.후==='선택 1건',전:aq.전,후:aq.후});

  /* ── 잔존 ── */
  const files=fs.readdirSync(REPO).filter(f=>/\.html$/.test(f)&&!/^glossary/.test(f));
  const bad=[];
  files.forEach(f=>{ const s=fs.readFileSync(path.join(REPO,f),'utf8');
    if(/표시 <b/.test(s)) bad.push(f+' 표시a–b');
    if(/rangeLabel/.test(s)) bad.push(f+' rangeLabel'); });
  P(R.leftovers,'표시 a–b · rangeLabel 잔존 0 (glossary 제외)',{pass:bad.length===0,검사파일:files.length,걸린것:bad});

  const lines=[];
  const dump=(n,a)=>{ lines.push('== '+n+' =='); a.forEach(x=>lines.push('  '+(x.pass?'PASS ':'FAIL ')+x.t+'  '+JSON.stringify(x))); };
  dump('행 호버',R.hover); dump('행 키보드 초점 없음',R.focus); dump('순번 열',R.cols); dump('건수 자리',R.counts); dump('잔존',R.leftovers);
  const all=R.hover.concat(R.focus,R.cols,R.counts,R.leftovers);
  const fail=all.filter(x=>!x.pass);
  lines.push('== 콘솔 에러 == '+cons.length); cons.slice(0,10).forEach(c=>lines.push('  - '+c));
  lines.push('== 합계 == '+all.length+'건 · PASS '+(all.length-fail.length)+' · FAIL '+fail.length);
  console.log(lines.join('\n'));
  fs.writeFileSync(OUT, JSON.stringify(R,null,1));
  ws.close(); ch.kill(); server.close(); process.exit(fail.length||cons.length?1:0);
}
main().catch(e=>{console.error('VERIFY ERROR',e);process.exit(1);});
