/* app.html 항등식 검증 — 정렬·필터·기간·페이지 조작 뒤에도 합계·비중이 재계산되는지 값으로 확인.
   창을 띄우지 않는다(--headless=new). 결과: verify_identity_result.json */
const http = require('http');
const fs   = require('fs');
const path = require('path');
const os   = require('os');
const { spawn } = require('child_process');

const REPO = '/Users/semi/cursor/payhug-investor-admin';
const OUTDIR = '/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin';
/* 검증기가 숫자를 손으로 갖고 있지 않다 — 채권 원장이 내보낸 사실값을 읽어 쓴다.
   daily_ledger.py 의 dump_facts() 산출물. 원장이 바뀌면 기대값도 같이 움직인다. */
const FACTS = JSON.parse(fs.readFileSync(path.join(OUTDIR, 'ledger_facts.json'), 'utf8'));
const PORT = 8700 + (process.pid % 90), DPORT = 9400 + (process.pid % 90);
const DL = fs.mkdtempSync(path.join(os.tmpdir(), 'phdl-'));
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const MIME = {'.html':'text/html; charset=utf-8', '.css':'text/css; charset=utf-8', '.js':'text/javascript',
  '.png':'image/png', '.xlsx':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'};

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
  if(r.exceptionDetails) throw new Error('page eval: ' + JSON.stringify(r.exceptionDetails.exception && r.exceptionDetails.exception.description || r.exceptionDetails.text));
  return r.result.value;
}
const sleep = ms => new Promise(r => setTimeout(r, ms));
/* 화면의 W금융일수가 소수 1자리라 되짚은 Ty 에 남는 잔차.
   Ty = 0.11% x 365 / W 이므로 W 를 0.05 만큼 잘라 낸 오차는 만기가 짧을수록 커진다
   (W 11일대 0.02%p · W 3일대 0.22%p). 상수 하나로는 못 잡아 W 에서 계산한다. */
const tySlack = w => w ? 0.11 * 365 * 0.05 / (w * (w - 0.05)) + 0.006 : 0.03;
/* 비율·일수는 소수 6자리 값으로 계산하고 화면에는 2자리만 보인다(dm_0901 규칙 1 · 확정).
   화면 두 칸으로 되짚으면 W 를 0.005 만큼 잘라 낸 만큼 Ty 가 어긋난다 — 그만큼만 봐 준다. */
const ty2Slack = w => w ? 0.11 * 365 * 0.005 / (w * (w - 0.005)) + 0.005 : 0.04;

async function main(){
  await new Promise(r => server.listen(PORT, r));
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'phprof-'));
  const chrome = spawn(CHROME, ['--headless=new', '--remote-debugging-port=' + DPORT,
    '--user-data-dir=' + profile, '--no-first-run', '--no-default-browser-check',
    '--disable-gpu', '--window-size=1440,1200', 'about:blank'], {stdio:'ignore'});

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
  const page = targets.find(t => t.type === 'page');
  ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise(r => ws.addEventListener('open', r));
  ws.addEventListener('message', ev => {
    const m = JSON.parse(ev.data);
    if(m.id && pending.has(m.id)){ pending.get(m.id).res(m.result); pending.delete(m.id); return; }
    if(m.method === 'Runtime.consoleAPICalled' && (m.params.type === 'error' || m.params.type === 'warning'))
      consoleErrors.push(m.params.type + ': ' + m.params.args.map(a => a.value || a.description || a.type).join(' '));
    if(m.method === 'Runtime.exceptionThrown')
      consoleErrors.push('exception: ' + (m.params.exceptionDetails.exception && m.params.exceptionDetails.exception.description || m.params.exceptionDetails.text));
    if(m.method === 'Log.entryAdded' && m.params.entry.level === 'error')
      consoleErrors.push('log: ' + m.params.entry.text + ' ' + (m.params.entry.url || ''));
  });
  await send('Runtime.enable'); await send('Log.enable'); await send('Page.enable');
  await send('Browser.setDownloadBehavior', {behavior:'allow', downloadPath: DL});

  await send('Page.navigate', {url:'http://127.0.0.1:' + PORT + '/app.html'});
  await sleep(1800);

  const OUT = {cases: [], console: []};
  const push = (name, ok, detail) => OUT.cases.push({case:name, pass:!!ok, detail:detail});

  const PAGE = `
    var EXEC = ${FACTS.exec}, TOTAL = ${FACTS.total}, RATE = 0.0011, RPCT = ${FACTS.rate}, CASH = ${FACTS.cash};
    /* PSC = 기간 동안 EC(전일자 순현금)들의 합. EC 는 하루에 한 건 쌓이므로 기간 일수만큼 센다.
       월별 레코드는 그 달 가운데 조회 기간에 걸친 일수를 센다. */
    function periodRange(){
      var el = document.querySelector('[data-mount=pf-stat] .summary-sub.mono');
      if(!el) return null;
      var m = el.textContent.split('~');
      return m.length === 2 ? [m[0].trim(), m[1].trim()] : null;
    }
    /* 표의 한 행이 덮는 날짜 구간 — 일별 '2026-08-27' · 주별 '2026-08-17 ~ 08-23' · 월별 '2026-08' */
    function bucketSpan(d){
      d = String(d);
      if(d.length === 10) return [d, d];
      if(d.indexOf('~') > 0){
        var p = d.split('~'), a = p[0].trim(), b = p[1].trim();
        return [a, a.slice(0, 4) + '-' + b];
      }
      var y = +d.slice(0, 4), mo = +d.slice(5, 7);
      return [d + '-01', d + '-' + ('0' + new Date(y, mo, 0).getDate()).slice(-2)];
    }
    /* EC 는 하루에 한 건 쌓이는 유량이라 '원장이 실제로 가진 날' 수만큼만 센다.
       집계 단위가 종료일을 주·달 경계까지 넓혀도 원장에 없는 날에는 EC 가 없다 —
       그래서 조회 기간뿐 아니라 원장 구간으로도 자른다. LEDGER_SPAN 은 daily_ledger.py 기준. */
    var LEDGER_SPAN = ${JSON.stringify(FACTS.ledgerSpan)};
    /* 날짜 -> [W, Ty, 투자실행금, 투자수익, 상환액, 채권매입수수료, 부족액 차감] — 원장 사실값 */
    var TYBD = ${JSON.stringify(FACTS.tyByDate)};
    /* 날짜 -> 6자리 W금융일수. 화면에는 2자리만 보인다(dm_0901 규칙 1).
       [기준 교체 2026-09-02] 예전엔 표에 찍힌 2자리 W 를 다시 가중해 ④·⑤ 기대값을 만들고,
       그렇게 생긴 갈림을 tySlack 이 삼켰다 — ⑤ 가 2.25 인데 기대값이 2.24 여도 통과했다.
       기대값은 원장 6자리에서 낸다. 원장이 정본이다(verifiers.md 기대값 원천 표). */
    var W6BD = ${JSON.stringify(FACTS.w6ByDate)};
    /* 날짜 -> Σ( A_i × D_i ) (원·일). ⑤ 의 새 분모 재료 — daily_ledger.facts adByDate.
       [기준 교체 2026-09-04] ⑤ = PM × 365 ÷ ( Σ( A_i × D_i ) + PEC ) 확정안(step7 ⑤ 산식 교체). */
    var ADBD = ${JSON.stringify(FACTS.adByDate)};
    var LEDGER_DATES = Object.keys(TYBD).sort();
    function r6(x){ return Math.round(x * 1e6) / 1e6; }
    /* 표 한 행이 실제로 덮는 날짜 구간 — 라벨의 구간을 조회 기간·원장 구간으로 자른 것 */
    function clipSpan(d){
      var sp = bucketSpan(d), pr = periodRange(), a = sp[0], b = sp[1];
      if(pr){ if(a < pr[0]) a = pr[0]; if(b > pr[1]) b = pr[1]; }
      if(a < LEDGER_SPAN[0]) a = LEDGER_SPAN[0];
      if(b > LEDGER_SPAN[1]) b = LEDGER_SPAN[1];
      return [a, b];
    }
    /* 원장에서 한 구간을 집계한다 — 대표 정의서 PSA·PSM·PSD 그대로.
       W 는 투자실행금(Ai) 가중평균이고 6자리에서 끊는다(dm_0901 규칙 1 · 화면 r6 와 같은 규칙). */
    function ledgerAgg(a, b){
      var ex = 0, pf = 0, rp = 0, fee = 0, ded = 0, wx = 0, ad = 0, nd = 0, i, d, r;
      for(i = 0; i < LEDGER_DATES.length; i++){
        d = LEDGER_DATES[i];
        if(d < a || d > b) continue;
        r = TYBD[d];
        ex += r[2]; pf += r[3]; rp += r[4]; fee += r[5]; ded += r[6];
        wx += Number(W6BD[d]) * r[2]; ad += Number(ADBD[d]); nd += 1;
      }
      return {exec:ex, profit:pf, repay:rp, fee:fee, ded:ded, days:nd, ad:ad, w:ex ? r6(wx / ex) : 0};
    }
    /* 화면 표의 행 라벨을 그대로 받아 그 표가 말해야 할 값을 원장에서 다시 만든다.
       버킷 W 를 6자리로 끊고 그 값을 다시 가중하는 두 단계는 화면 rollupBy·tyOfRows 와 같은 순서다 —
       단계를 한 번으로 줄이면 6번째 자리에서 갈려 표기 한 눈금이 뒤집힐 수 있다. */
    function expectRows(labels){
      var bs = labels.map(function(d){ var sp = clipSpan(d); return ledgerAgg(sp[0], sp[1]); });
      var ex = 0, pf = 0, rp = 0, wx = 0, ad = 0, nd = 0;
      bs.forEach(function(g){ ex += g.exec; pf += g.profit; rp += g.repay; wx += g.w * g.exec; ad += g.ad; nd += g.days; });
      var w = ex ? r6(wx / ex) : 0;
      /* MR(= 투자수익 ÷ 투자실행금 x 100)도 비율이라 6자리에서 끊고 그 값을 다음 계산에 넣는다
         (dm_0901 규칙 1 · 2026-09-02 기획 지시로 MR·PMR 예외 철회 · daily_ledger.facts 와 같은 순서).
         지금 원장 180일·기간 8종 어디서도 표기 2자리를 바꾸지 않지만, 생성기와 같은 단계를 밟아
         나중에 경계에 걸릴 때 검증기가 뒤늦게 갈리지 않게 한다. */
      var ty4 = (ex && w) ? r6(r6(pf / ex * 100) * 365 / w) : 0;
      var psc = CASH * nd;
      /* ⑤ = PM × 365 ÷ ( Σ( A_i × D_i ) + PEC ) = ④ × AD ÷ ( AD + PEC ) — 확정안(step7 ⑤ 산식 교체 ·
         daily_ledger.TY5_EXPR). [기준 교체 2026-09-04] 옛 식 ④ × PSA ÷ (PSA + PSC) 의 PSA 자리가
         AD(= 기간 Σ Ai×Di · adByDate 합)로 바뀌었다. 화면 tyAssetOf 도 r6 를 거쳐 찍을 때만
         2자리로 자르므로 여기서도 r6 뒤 r2 로 같은 순서를 밟는다. */
      var ty5 = (ad + psc) ? r6(ty4 * ad / (ad + psc)) : 0;
      return {buckets:bs, exec:ex, profit:pf, repay:rp, ecDays:nd, psc:psc, ad:ad,
              w:w, w2:r2(w), ty4:ty4, ty42:r2(ty4), ty5:ty5, ty52:r2(ty5),
              /* 행마다 ⑥ = ty5(④행, ③행, TY6_PSC). TY6_PSC 가 0 인 동안 ④ 와 같은 값이다
                 (daily_ledger.TY6_EXPR). 그 0 이 바뀌면 이 줄도 함께 고칠 자리다. */
              rowTy:bs.map(function(g){
                return (g.exec && g.w) ? r2(r6(r6(g.profit / g.exec * 100) * 365 / g.w)) : 0; }),
              rowW:bs.map(function(g){ return r2(g.w); }),
              /* 상환액 − (투자실행금 + 투자수익) 의 정확한 갈림. 원장 세 칸에서 그대로 나온다 —
                 봐 주는 폭이 아니라 기대값이다(예전 REPAY_GAP_DAY 20원/일 자리). */
              rowGap:bs.map(function(g){ return g.repay - (g.exec + g.profit); })};
    }
    function ecDaysOf(rs){
      var pr = periodRange(), n = 0;
      rs.forEach(function(x){
        var sp = bucketSpan(x.d), a = sp[0], b = sp[1];
        if(pr){ if(a < pr[0]) a = pr[0]; if(b > pr[1]) b = pr[1]; }
        if(a < LEDGER_SPAN[0]) a = LEDGER_SPAN[0];
        if(b > LEDGER_SPAN[1]) b = LEDGER_SPAN[1];
        if(a > b) return;
        n += Math.round((Date.parse(b) - Date.parse(a)) / 86400000) + 1;
      });
      return n;
    }
    /* 대표 정의서 — 여러 날을 한 덩이로 볼 때의 Ty수익율 = SMR x 365 / SD.
       화면의 W금융일수는 소수 1자리로 잘려 있어 되짚은 값에 잔차가 남는다. 그만큼만 봐 준다.
       잔차는 0.11% x 365 x 0.05 / w^2 이라 만기가 짧을수록 커진다 — 상수가 아니라 w 의 함수다. */
    function tyFrom(exec, profit, w){ return (exec && w) ? (profit / exec * 100) * 365 / w : 0; }
    function TY_SLACK(w){ return w ? 0.11 * 365 * 0.05 / (w * (w - 0.05)) + 0.006 : 0.03; }
    /* 표기 W(소수 2자리)로 되짚은 Ty 와 6자리 W 로 낸 Ty 의 갈림 (dm_0901 규칙 1) */
    function TY2_SLACK(w){ return w ? 0.11 * 365 * 0.005 / (w * (w - 0.005)) + 0.005 : 0.04; }
    /* 상환액 = 순지급액 − 부족액 한 줄로 낸다(dm_0901 규칙 2 · 확정).
       투자실행금 + 투자 수익으로 쪼개면 Ai 반올림과 채권매입수수료 절사 두 곳에서
       원 단위로 끊겨 하루치가 어긋난다. 하루당 봐 주는 폭이다. */
    var REPAY_GAP_DAY = 20;
    /* ⑤ 기대값 — 행들의 Σ( A_i × D_i ) 합을 분모 재료로 쓴다 (2026-09-04 · 위 expectRows 와 같은 식) */
    function adOfLabels(rs){ var a = 0; rs.forEach(function(x){ var sp = clipSpan(x.d); a += ledgerAgg(sp[0], sp[1]).ad; }); return a; }
    function tyAssetWant(ty4, rs){
      var psc = CASH * ecDaysOf(rs), ad = adOfLabels(rs);
      return (ad + psc) ? r2(ty4 * ad / (ad + psc)) : 0;
    }
    function num(t){ return Number(String(t).replace(/[^0-9.\\-]/g, '')); }
    function cells(tr){ return Array.prototype.map.call(tr.children, function(c){ return c.textContent.trim(); }); }
    function rowsOf(sel){
      var t = document.querySelector(sel + ' tbody'); if(!t) return [];
      return Array.prototype.map.call(t.querySelectorAll('tr'), cells);
    }
    function r2(x){ return Math.round(x * 100) / 100; }
    function r1(x){ return Math.round(x * 10) / 10; }
    function tyOf(w){ return r2(RPCT * 365 / w); }
    function collectAssets(){
      var out = [], seen = {};
      [1, 2].forEach(function(p){
        var b = document.querySelector('[data-act="ia-page"][data-page="' + p + '"]');
        if(b) b.click();
        rowsOf('[data-mount=ia-merch]').forEach(function(c){
          if(seen[c[0]]) return; seen[c[0]] = 1;
          out.push({name:c[0], amount:num(c[1]), w:num(c[2]), s:num(c[3]), ty:num(c[4]), ratio:num(c[5])});
        });
      });
      return out;
    }
  `;

  async function P(expr){ return await evalJS(PAGE + expr); }

  /* ── 1) 투자자산 — 보기 갯수·페이지 조작 후 항등식 ── */
  const SIZES = [10, 20, 50, 10];
  for(let k = 0; k < SIZES.length; k++){
    const key = SIZES[k];
    await evalJS('go("invest-assets","default");' +
      'var s=document.querySelector(\'[data-act=pg-size][data-key=ia-merch]\');' +
      's.value="' + key + '"; s.dispatchEvent(new Event("change",{bubbles:true})); return 1;');
    const r = await P(`
      go('invest-assets', 'default');
      var m = collectAssets();
      var st = rowsOf('[data-mount=ia-status]');
      var card = document.querySelector('[data-mount=ia-summary]').textContent.replace(/\\s+/g, ' ');
      var amt = 0, rat = 0, tyBad = [];
      if(!m.length) return {err:'ia-merch 행 0'};
      m.forEach(function(x){
        amt += x.amount; rat = Math.round((rat + x.ratio) * 10) / 10;
        if(Math.abs(x.ty - tyOf(x.w)) > TY2_SLACK(x.w)) tyBad.push(x.name + ' ' + x.ty + '/' + tyOf(x.w));
      });
      if(st.length < 3) return {err:'ia-status 행 ' + st.length, raw:st, rows:m.length};
      var stExec = num(st[0][1]), stCash = num(st[1][1]), stTot = num(st[2][1]);
      var stRat = Math.round((num(st[0][5]) + num(st[1][5])) * 10) / 10;
      return {rows:m.length, amountSum:amt, ratioSum:rat, tyBad:tyBad,
              stExec:stExec, stCash:stCash, stTotal:stTot, stRatioSum:stRat,
              cardHasExec:card.indexOf(stExec.toLocaleString('en-US')) >= 0,
              cardHasTotal:card.indexOf(stTot.toLocaleString('en-US')) >= 0,
              first:m[0].name, last:m[m.length - 1].name};
    `);
    push('투자자산 항등식 · 보기=' + key + '개',
      r.rows === FACTS.merchants.length && r.amountSum === FACTS.exec && r.ratioSum === 100 && r.tyBad.length === 0 &&
      r.stExec === FACTS.exec && r.stTotal === r.stExec + r.stCash && r.stRatioSum === 100 &&
      r.cardHasExec && r.cardHasTotal, r);
  }

  /* ── 1-b) 비중 = 최대잉여법 ──
     0.1pp 눈금으로 내린 뒤 남는 눈금을 소수부가 큰 행부터 나눠 준다. 합은 정확히 100.0 이고
     어느 행도 정확값에서 한 눈금(0.1pp)을 넘게 밀리지 않는다.
     잔차를 최대 금액 행 하나에 몰면 그 행만 여러 눈금 밀려 SUMPRODUCT 검산에서 드러난다. */
  {
    const r = await P(`
      go('invest-assets', 'default');
      var m = collectAssets(), base = 0, bad = [], sum = 0;
      m.forEach(function(x){ base += x.amount; });
      m.forEach(function(x){
        var exact = x.amount / base * 100;
        sum = Math.round((sum + x.ratio) * 10) / 10;
        if(Math.abs(x.ratio - exact) >= 0.1)
          bad.push(x.name + ' 표기 ' + x.ratio + ' vs 정확 ' + exact.toFixed(4));
      });
      var st = rowsOf('[data-mount=ia-status]');
      return {sum:sum, bad:bad, base:base, rows:m.length,
              top:{name:m[0].name, ratio:m[0].ratio, exact:+(m[0].amount / base * 100).toFixed(4)},
              statusSum:Math.round((num(st[0][5]) + num(st[1][5])) * 10) / 10};`);
    push('비중 최대잉여법 — 합 100.0 · 각 행 잔차 < 0.1pp',
      r.sum === 100 && r.bad.length === 0 && r.statusSum === 100, r);
  }

  /* ── 2) 투자수익 — 기간·granularity 조작 후 항등식 ── */
  /* '어제' 프리셋은 스토리보드 슬라이드7 에 없어 뺐다 — 하루 구간은 날짜를 직접 넣어 만든다. */
  const DAY1 = ['2026-08-26', '2026-08-26'];
  const PERIODS = [['week', 'daily'], ['day1', 'daily'], ['month', 'daily'],
                   ['week', 'weekly'], ['month', 'weekly'],
                   ['week', 'monthly'], ['month', 'monthly']];
  /* 집계 단위 토글은 기간을 지우지 않고 그 단위 경계로 넓혀 스냅한다(period_design.md).
     프리셋으로 기간을 먼저 채우고 토글을 눌러, 스냅된 기간에서 항등식이 서는지 본다. */
  const goPeriod = (preset, gran) =>
    'go("invest-profit","default");' +
    (preset === 'day1'
      ? 'document.querySelector(\'[data-act=pf-gran][data-gran=' + gran + ']\').click();' +
        'var s=document.querySelector(\'section.screen[data-screen=invest-profit]\');' +
        'var f=s.querySelector(\'[data-mount=pf-from]\'), t=s.querySelector(\'[data-mount=pf-to]\');' +
        'f.value="' + DAY1[0] + '"; f.dispatchEvent(new Event("change",{bubbles:true}));' +
        't.value="' + DAY1[1] + '"; t.dispatchEvent(new Event("change",{bubbles:true}));'
      : 'document.querySelector(\'[data-act=preset][data-preset=' + preset + ']\').click();' +
        'document.querySelector(\'[data-act=pf-gran][data-gran=' + gran + ']\').click();') +
    ' return 1;';
  for(const [preset, gran] of PERIODS){
      await evalJS(goPeriod(preset, gran));
    const r = await P(`
      var rs = rowsOf('[data-mount=pf-tbl]').map(function(c){
        return {d:c[0], repay:num(c[1]), exec:num(c[2]), profit:num(c[3]), w:num(c[4]), ty:num(c[5])}; });
      var f = document.querySelector('[data-mount=pf-tbl] tfoot tr');
      var ft = f ? cells(f) : null;
      var st = document.querySelectorAll('[data-mount=pf-stat] .summary-value');
      /* 기대값은 화면에서 되짚지 않고 원장에서 낸다 — 행 라벨만 화면에서 받는다.
         [기준 교체 2026-09-02] 표에 찍힌 2자리 W 를 다시 가중해 기대값을 만들던 자리다. */
      var W = expectRows(rs.map(function(x){ return x.d; }));
      var bad = [], ex = 0, pr = 0, rp = 0;
      rs.forEach(function(x, i){
        var isDay = String(x.d).length === 10;
        /* [기준 교체 2026-08-30] 예전엔 수익을 투자실행금에서 되짚어 봤다
           (수익 = floor(그날 Σ순지급액 x 할인율), 순지급액 = 투자실행금 / (1 - 할인율)).
           대표 정의서 [2번 이미지] MD-1i 로 수수료에서 부족액을 빼게 되면서 되짚기가 성립하지 않는다.
           화면에는 순지급액도 부족액도 열이 없으므로 원장 사실값(TYBD)과 행 단위로 맞춘다 — 더 좁은 검사다.
           아울러 부족액 차감은 음수가 될 수 없으므로 수익은 되짚은 수수료를 넘지 못한다. */
        if(isDay){
          var wantRow = TYBD[x.d];
          if(!wantRow) bad.push(x.d + ' 원장에 없는 날짜');
          else if(wantRow[2] !== x.exec || wantRow[3] !== x.profit || wantRow[4] !== x.repay)
            bad.push(x.d + ' 수익');
          if(x.profit <= 0 || x.profit - x.exec * RATE / (1 - RATE) > 1.5) bad.push(x.d + ' 수익 상한');
        }
        /* 버킷 행도 원장 집계와 완전일치라야 한다 — 금액 세 칸은 정수 합이라 봐 줄 자리가 없다 */
        var g = W.buckets[i];
        if(g.exec !== x.exec || g.profit !== x.profit || g.repay !== x.repay) bad.push(x.d + ' 행 금액');
        /* 상환액 − (투자실행금 + 투자수익) 의 갈림은 원장이 정확히 알려 준다.
           [기준 교체 2026-09-02] 예전엔 REPAY_GAP_DAY 20원/일 로 봐 줬다 — 봐 줄 자리가 아니다. */
        if(x.repay - (x.exec + x.profit) !== W.rowGap[i]) bad.push(x.d + ' 상환액 갈림');
        /* 표기값끼리 맞댄다 — 허용치 없음 */
        if(x.w !== W.rowW[i]) bad.push(x.d + ' W ' + x.w + '/' + W.rowW[i]);
        if(x.ty !== W.rowTy[i]) bad.push(x.d + ' Ty ' + x.ty + '/' + W.rowTy[i]);
        ex += x.exec; pr += x.profit; rp += x.repay;
      });
      return {rows:rs.length, exec:ex, profit:pr, repay:rp, bad:bad,
              footRepay:ft ? num(ft[1]) : null, footExec:ft ? num(ft[2]) : null, footProfit:ft ? num(ft[3]) : null,
              footW:ft ? num(ft[4]) : null, footTy:ft ? num(ft[5]) : null,
              wantExec:W.exec, wantProfit:W.profit, wantRepay:W.repay,
              wantW:W.w2, wantTy:W.ty42, wantTyAsset:W.ty52,
              cardExec:num(st[0].textContent), cardProfit:num(st[1].textContent),
              cardTyExec:num(st[2].textContent), cardTyAsset:num(st[3].textContent),
              ecDays:W.ecDays, psc:W.psc, wRaw:W.w, ty4Raw:W.ty4, ty5Raw:W.ty5};
    `);
    /* 전부 표기값 대조라 허용치가 없다. 금액 세 칸은 정수 합이고 W·④·⑤ 는 원장 6자리에서
       같은 순서로 반올림한 값이라, 한 눈금이라도 밀리면 그대로 FAIL 이다. */
    push('투자수익 항등식 · ' + preset + '/' + gran,
      r.bad.length === 0 && r.footExec === r.exec && r.footProfit === r.profit && r.footRepay === r.repay &&
      r.exec === r.wantExec && r.profit === r.wantProfit && r.repay === r.wantRepay &&
      r.footW === r.wantW && r.footTy === r.wantTy &&
      r.cardExec === r.exec && r.cardProfit === r.profit &&
      r.cardTyExec === r.footTy && r.cardTyAsset === r.wantTyAsset, r);
  }

  /* ── 3) Ty(투자자산 대비) 배율 = AD/(AD+PEC) · AD = Σ( A_i × D_i ) ──
     [기준 교체 2026-09-04] 옛 배율 PSA/(PSA+PSC) → AD/(AD+PEC) (step7 ⑤ 산식 교체 · 기본 기간 0.799031) */
  {
    const vals = [];
    for(const [preset, gran] of PERIODS){
      await evalJS(goPeriod(preset, gran));
      const r = await P(`
        var st = document.querySelectorAll('[data-mount=pf-stat] .summary-value');
        var rs = rowsOf('[data-mount=pf-tbl]').map(function(c){ return {d:c[0], exec:num(c[2])}; });
        var W = expectRows(rs.map(function(x){ return x.d; }));
        return {tyExec:num(st[2].textContent), tyAsset:num(st[3].textContent), exec:num(st[0].textContent),
                ecDays:W.ecDays, psc:W.psc, ad:W.ad, wantFive:W.ty52, wantFour:W.ty42,
                wantK: W.ad ? Math.round(W.ad / (W.ad + W.psc) * 10000) / 10000 : 0};`);
      vals.push({preset, gran, ...r, k: r.tyExec ? Math.round(r.tyAsset / r.tyExec * 10000) / 10000 : 0});
    }
    /* ⑤ 의 배율은 AD/(AD+PEC) (AD = 기간 Σ Ai×Di) 이므로 기간마다 값이 다르다.
       종전 기대식(투자실행액/투자자산 한 값 고정)은 스톡으로 나누던 구식이라 폐기.

       [기준 교체 2026-09-02] 표기 ⑤ ÷ 표기 ④ 로 낸 배율을 상수 0.003 으로 봐 주던 자리다.
       배율은 2자리 표기 둘을 나눈 값이라 그 잔차가 실제로 크다(주간 0.5639 ↔ 정확 0.5625) —
       그래서 이 칸으로는 ⑤ 가 한 눈금 밀린 것을 가릴 수 없다. 판정을 둘로 가른다.
         (가) ⑤·④ 표기값 자체 — 원장 6자리에서 낸 기대값과 완전일치. 허용치 없음
         (나) 배율 — 허용치를 상수로 두지 않고 표기 반올림에서 유도한다.
              ⑤ = r2(④6 x k) · ④ = r2(④6) 이므로 |⑤/④ - k| <= (0.005 + k x 0.005) / ④ 다.
       (나)가 필요한 이유는 배율이 표기 두 칸의 몫이라 원 자리 반올림이 두 번 들어가서다.
       판별력은 (가)가 갖는다. */
    const bad = [];
    vals.forEach(v => {
      if(v.tyAsset !== v.wantFive) bad.push(v.preset + '/' + v.gran + ' ⑤ ' + v.tyAsset + ' (기대 ' + v.wantFive + ')');
      if(v.tyExec !== v.wantFour) bad.push(v.preset + '/' + v.gran + ' ④ ' + v.tyExec + ' (기대 ' + v.wantFour + ')');
      const lim = v.tyExec ? (0.005 + v.wantK * 0.005) / v.tyExec + 1e-9 : 0;
      if(Math.abs(v.k - v.wantK) > lim)
        bad.push(v.preset + '/' + v.gran + ' 배율 ' + v.k + ' (기대 ' + v.wantK + ' · 표기잔차 상한 ' + lim.toFixed(5) + ')');
    });
    /* 배율이 기간마다 달라야 한다 — 한 값으로 굳으면 스톡으로 나누던 옛 식으로 되돌아간 것이다 */
    const ks = [...new Set(vals.map(v => v.wantK))];
    if(ks.length < 2) bad.push('배율이 기간과 무관하게 한 값 ' + ks.join(','));
    push('Ty(투자자산 대비) 배율 = AD/(AD+PEC) — 기간별 대조', bad.length === 0, {bad, vals});
  }

  /* ── 4) 증명서 ── */
  {
    const r = await P(`
      go('certificate', 'default');
      var rs = rowsOf('[data-mount=cert-tbl]').map(function(c){ return {name:c[0], amount:num(c[1]), w:num(c[2]), ty:num(c[4]), ratio:num(c[5])}; });
      var f = document.querySelector('[data-mount=cert-tbl] tfoot tr');
      var ft = cells(f);
      var amt = 0, rat = 0, bad = [];
      rs.forEach(function(x){ amt += x.amount; rat = Math.round((rat + x.ratio) * 10) / 10;
        if(Math.abs(x.ty - tyOf(x.w)) > TY2_SLACK(x.w)) bad.push(x.name); });
      return {rows:rs.length, amountSum:amt, ratioSum:rat, bad:bad,
              footAmount:num(ft[1]), footRatio:num(ft[5]),
              count:document.querySelector('[data-mount=cert-count]').textContent.trim()};`);
    push('증명서 ' + FACTS.merchants.length + '행 · 합계 · 비중',
      r.rows === FACTS.merchants.length && r.amountSum === FACTS.exec && r.ratioSum === 100 && r.bad.length === 0 &&
      r.footAmount === FACTS.exec && r.footRatio === 100 && r.count === FACTS.merchants.length + '개', r);
  }

  /* ── 5) 엑셀 미리보기 ↔ 화면 ── */
  {
    /* 시트 행 자리는 로스터 곳수에서 나온다 — 머리 3줄(제목·공백·열머리) 다음이 본문이고
       그 다음 줄이 합계다. 검증기에 행 번호를 손으로 적지 않는다. */
    const NR = FACTS.merchants.length;
    const r = await P(`
      var NR = ${NR};
      var SH = function(scr){ return 'section[data-screen="' + scr + '"] [data-mount=sheet]'; };
      go('xls-assets-merchant', 'default');
      var all = rowsOf(SH('xls-assets-merchant'));
      var rs = all.slice(3, 3 + NR).map(function(c){ return {n:c[0], name:c[1], amount:num(c[2]), ratio:num(c[6])}; });
      var tot = all[3 + NR];
      go('xls-assets-status', 'default');
      var st = rowsOf(SH('xls-assets-status')).slice(3, 6).map(function(c){ return {name:c[1], amount:num(c[2]), ratio:num(c[6])}; });
      var amt = 0, rat = 0;
      rs.forEach(function(x){ amt += x.amount; rat = Math.round((rat + x.ratio) * 10) / 10; });
      return {rows:rs.length, amountSum:amt, ratioSum:rat, totalRow:{label:tot[1], amount:num(tot[2]), ratio:num(tot[6])},
              status:st};`);
    push('엑셀 미리보기 — 가맹점별·현황',
      r.rows === FACTS.merchants.length && r.amountSum === FACTS.exec && r.ratioSum === 100 &&
      r.totalRow.amount === FACTS.exec && r.totalRow.ratio === 100 &&
      r.status[0].amount === FACTS.exec && r.status[2].amount === FACTS.total &&
      Math.round((r.status[0].ratio + r.status[1].ratio) * 10) / 10 === 100, r);
  }

  /* ── 8) 카드 5값 = 표 합계 — 기간 4종 x (일별 → 월별 → 다시 일별) ──
     조회 기간을 바꾸면 표가 따라가고, 카드는 그 표의 합계와 같아야 한다.
     직접 고른 기간은 집계 단위를 바꿔도 지워지지 않고 그 단위 경계로 넓혀 스냅된다(period_design.md).
     그래서 '월별'과, 그 스냅된 기간을 그대로 물려받은 '일별 복귀'가 같은 기간이고,
     이 둘의 카드 5값은 같아야 한다(월별 표 = 일별 원장의 달별 합).
     네 구간 전부 프리셋이 아닌 직접입력이다 — 프리셋을 보고 있을 때 단위를 바꾸면
     새 단위의 같은 자리 프리셋으로 넘어가므로(기간이 통째로 갈린다) 이 대조의 전제가 성립하지 않는다.
     프리셋 쪽 거동은 verify_period.js 가 따로 본다.
     종료일은 기준일 2026-08-27 에서 끊긴다 — 달 경계(08-31)로 넓히지 않는다. */
  {
    /* [라벨, 프리셋, 일별 기간, 일별 행수, 월별 스냅 기간, 월별 행수, 스냅 기간의 일별 행수] */
    const PRESETS = [
      ['하루',  null, '2026-08-26', '2026-08-26', 1,   '2026-08-01', '2026-08-27', 1, 27],
      ['8일',   null, '2026-08-20', '2026-08-27', 8,   '2026-08-01', '2026-08-27', 1, 27],
      ['26일',  null, '2026-08-02', '2026-08-27', 26,  '2026-08-01', '2026-08-27', 1, 27],
      /* 03-01~08-27 은 월별로 스냅하면 6개월 프리셋 자리라 단위를 되돌릴 때 프리셋 이동이 걸린다 —
         전제(기간 유지)를 지키려고 프리셋과 겹치지 않는 5개월 구간을 쓴다. */
      ['5개월', null, '2026-04-01', '2026-08-27', 149, '2026-04-01', '2026-08-27', 5, 149]
    ];
    const rows = [], bad = [];
    for(const [label, preset, from, to, nDaily, mFrom, mTo, nMonthly, nBack] of PRESETS){
      const STEPS = [['daily', from, to, nDaily], ['monthly', mFrom, mTo, nMonthly], ['daily', mFrom, mTo, nBack]];
      for(let si = 0; si < STEPS.length; si++){
        const [gran, wFrom, wTo, want] = STEPS[si];
        if(si === 0){
          /* 프리셋이 없는 구간은 날짜를 직접 넣고 검색한다 */
          await evalJS('go("invest-profit","default");' +
            (preset ? 'document.querySelector(\'[data-act=preset][data-preset=' + preset + ']\').click();'
                    : 'var s = document.querySelector(\'section.screen[data-screen=invest-profit]\');' +
                      'function put(m, v){ var el = s.querySelector(\'[data-mount=\' + m + \']\'); el.value = v;' +
                      ' el.dispatchEvent(new Event("change", {bubbles:true})); }' +
                      'put("pf-from", "' + from + '"); put("pf-to", "' + to + '");' +
                      's.querySelector(\'[data-act=pf-search]\').click();') +
            'return 1;');
        } else {
          await evalJS('document.querySelector(\'[data-act=pf-gran][data-gran=' + gran + ']\').click(); return 1;');
        }
        const r = await P(`
          var rs = rowsOf('[data-mount=pf-tbl]').map(function(c){
            return {d:c[0], repay:num(c[1]), exec:num(c[2]), profit:num(c[3]), w:num(c[4]), ty:num(c[5])}; });
          var ft = cells(document.querySelector('[data-mount=pf-tbl] tfoot tr'));
          var sv = document.querySelectorAll('[data-mount=pf-stat] .summary-value');
          var ex = 0, pr = 0, rp = 0;
          rs.forEach(function(x){ ex += x.exec; pr += x.profit; rp += x.repay; });
          /* [기준 교체 2026-09-02] 기대값을 원장 6자리에서 낸다. 표기 2자리 W 재가중 폐기 */
          var W = expectRows(rs.map(function(x){ return x.d; }));
          return {rows:rs.length, sumExec:ex, sumProfit:pr, sumRepay:rp,
                  footExec:num(ft[2]), footProfit:num(ft[3]), footRepay:num(ft[1]),
                  footW:num(ft[4]), footTy:num(ft[5]),
                  cardExec:num(sv[0].textContent), cardProfit:num(sv[1].textContent),
                  cardTyExec:num(sv[2].textContent), cardTyAsset:num(sv[3].textContent),
                  cardPeriod:document.querySelector('[data-mount=pf-stat] .summary-sub.mono').textContent.trim(),
                  wantExec:W.exec, wantProfit:W.profit, wantRepay:W.repay,
                  wantW:W.w2, wantTy:W.ty42, wantTyAsset:W.ty52};`);
        const tag = label + '/' + gran + (si === 2 ? '(복귀)' : '');
        rows.push({preset:label, gran, step:si, ...r});
        if(r.rows !== want) bad.push(tag + ' 행수 ' + r.rows + ' (기대 ' + want + ')');
        if(r.cardPeriod !== wFrom + ' ~ ' + wTo) bad.push(tag + ' 기간 ' + r.cardPeriod + ' (기대 ' + wFrom + ' ~ ' + wTo + ')');
        if(r.cardExec !== r.sumExec || r.footExec !== r.sumExec || r.sumExec !== r.wantExec) bad.push(tag + ' 투자실행금');
        if(r.cardProfit !== r.sumProfit || r.footProfit !== r.sumProfit || r.sumProfit !== r.wantProfit) bad.push(tag + ' 투자수익');
        if(r.footRepay !== r.sumRepay || r.sumRepay !== r.wantRepay) bad.push(tag + ' 상환액');
        if(r.footW !== r.wantW) bad.push(tag + ' W ' + r.footW + ' (기대 ' + r.wantW + ')');
        if(r.cardTyExec !== r.footTy || r.footTy !== r.wantTy) bad.push(tag + ' ④ ' + r.footTy + ' (기대 ' + r.wantTy + ')');
        /* [기준 교체 2026-09-02] ⑤ 도 원장 6자리 기대값과 완전일치로 본다.
           예전엔 「달 행 하나로 뭉치면 표기 ④ 로 되짚을 수밖에 없다」며 ty2Slack 으로 봐 주고,
           월별 쪽 기대값은 같은 기간 일별 표에서 빌려 왔다. 원장에서 내면 두 우회가 다 필요 없다. */
        if(r.cardTyAsset !== r.wantTyAsset) bad.push(tag + ' ⑤ ' + r.cardTyAsset + ' (기대 ' + r.wantTyAsset + ')');
      }
      const mCell = rows[rows.length - 2], bCell = rows[rows.length - 1];
      /* 같은 기간이면 집계 단위와 무관하게 카드 5값이 같다 */
      if(mCell.cardExec !== bCell.cardExec || mCell.cardProfit !== bCell.cardProfit ||
         mCell.cardTyExec !== bCell.cardTyExec || mCell.cardTyAsset !== bCell.cardTyAsset ||
         mCell.cardPeriod !== bCell.cardPeriod)
        bad.push(label + ' 같은 기간에서 월별↔일별 카드 불일치');
    }
    push('카드 5값 = 표 합계 · 기간 4종 x 일별→월별→일별 복귀', bad.length === 0, {bad, rows});
  }

  /* ── 6) 항등식 — 채권 원장 하나에서 나온 값들이 서로 어긋나지 않는가 ──

     ① `잔액 = 유량 x 만기` (Little's Law) — 투자실행액 = 하루 평균 투자실행금 x W금융일수,
        허용 오차 2.0%. 2026-08-29 에 한 번 걷어냈다가 2026-08-30 에 되살린 검사다.
        걷어낼 때의 사유는 「W 모집단이 미회수분이라 이 항등식이 성립하지 않는다」였다.
        대표 정의서 원문에서 '회수되지 않은' 한정은 투자 실행액 줄에만 붙어 있고
        대상정산금채권 정의에는 회수 여부 조건이 없다. 대표 실측 엑셀(`정산주기.xlsx` H41)의
        2.7504068548610725 도 365일 발생분 전수 가중평균이다. 그래서 모집단을 발생 기준으로
        되돌렸고(daily_ledger.py), 항등식이 부수 결과로 다시 선다.
        허용 오차를 두는 것은 원장의 일별 표 구간(180일)이 채권 발생 구간(193일)보다 짧아
        하루 평균이 그만큼 흔들리기 때문이다.
     ② 가맹점별 투자금액 합 = 투자실행액
     ③ W금융일수 ⊂ FACTS.wBound (플랫폼별 평균만기 실측 하한·상한) · 채권 한 건 Di ⊂ FACTS.diBound
        경계값은 검증기에 적지 않는다 — platform_duration.py 의 FLOOR/CEIL·DI_MIN/DI_MAX 가
        daily_ledger.facts() 를 거쳐 ledger_facts.json 으로 나온 것을 읽는다.
     ④ Ty수익율 — 잔액 계통(투자실행액 행·가맹점별 행)은 `할인율 x 365 / W금융일수`,
        일별 원장 행은 `(투자수익 / 투자실행금 x 100) x 365 / W금융일수`.
        분자가 다르다 — 잔액 쪽은 순지급액 대비, 일별 쪽은 투자실행금 대비다(simulation_design.md L-4).
        수수료 앵커는 양쪽 모두 순지급액이다(D-31).
     ⑤ S입금부족율 = Σ SLi / Σ SAi — 원장 표본집합(선정산일 D-20 ~ D-11)에서 나온 값과 같은가.
        아울러 부족율이 할인율을 넘으면 투자자 몫 수익을 다 먹고도 원금이 모자란다. */
  {
    /* 범위 가드의 경계 — platform_duration.py 가 내는 값을 원장 사실값으로 받아 쓴다.
       숫자를 여기 적으면 플랫폼 만기 실측이 바뀔 때 검증기가 옛 경계를 지킨다. */
    const WFLOOR = Number(FACTS.wBound[0]), WCEIL = Number(FACTS.wBound[1]);
    const DIFLOOR = Number(FACTS.diBound[0]), DICEIL = Number(FACTS.diBound[1]);
    const WRANGE = '[' + FACTS.wBound.join(', ') + ']', DIRANGE = '[' + FACTS.diBound.join(', ') + ']';
    const r = await P(`
      go('invest-assets', 'default');
      var st = rowsOf('[data-mount=ia-status]');
      var mer = collectAssets();
      var ex = 0, i;
      for(i = 0; i < DAILY.length; i++) ex += DAILY[i].exec;
      var dayAvg = Math.round(ex / DAILY.length);
      var execRow = st[0], w = num(execRow[2]), s = num(execRow[3]), ty = num(execRow[4]);
      var ws = [w].concat(mer.map(function(x){ return x.w; }))
                  .concat(DAILY.map(function(x){ return x.w; }));
      var tyBad = [];
      DAILY.forEach(function(x){
        var want = Math.round((x.profit / x.exec * 100) * 365 / x.w * 100) / 100;
        if(Math.abs(x.ty - want) > TY2_SLACK(x.w)) tyBad.push(x.d + ' ' + x.ty + '!=' + want);
      });
      mer.forEach(function(x){ if(Math.abs(x.ty - tyOf(x.w)) > TY2_SLACK(x.w)) tyBad.push(x.name); });
      if(ty !== tyOf(w)) tyBad.push('투자실행액');
      return {stExec:num(execRow[1]), w:w, s:s, ty:ty, tyOfW:tyOf(w),
              merSum:mer.reduce(function(a, x){ return a + x.amount; }, 0),
              merRows:mer.length, dayAvg:dayAvg, ledgerDays:DAILY.length,
              wMin:Math.min.apply(null, ws), wMax:Math.max.apply(null, ws),
              tyBad:tyBad};`);
    const bad = [];
    if(r.merSum !== r.stExec) bad.push('가맹점 합 ' + r.merSum + ' != 투자실행액 ' + r.stExec);
    if(r.stExec !== FACTS.exec) bad.push('투자실행액 ' + r.stExec + ' != 원장 ' + FACTS.exec);
    if(r.merRows !== FACTS.merchants.length) bad.push('로스터 ' + r.merRows + '건');
    if(r.wMin < WFLOOR || r.wMax > WCEIL) bad.push('W ' + r.wMin + '~' + r.wMax + ' ⊄ ' + WRANGE);
    if(FACTS.diRange[0] < DIFLOOR || FACTS.diRange[1] > DICEIL)
      bad.push('채권 Di ' + FACTS.diRange.join('~') + ' ⊄ ' + DIRANGE);
    if(r.tyBad.length) bad.push('Ty 산식 불일치 (잔액=할인율x365/W · 일별=SMRx365/SD) — ' + r.tyBad.join(','));
    if(String(r.s) !== String(Number(FACTS.s))) bad.push('S ' + r.s + ' != 원장 ' + FACTS.s);
    if(Number(FACTS.sRaw) >= Number(FACTS.rate))
      bad.push('S입금부족율 ' + FACTS.sRaw + '% >= 할인율 ' + FACTS.rate + '%');
    if(r.dayAvg !== FACTS.dayAvg) bad.push('하루 평균 투자실행금 ' + r.dayAvg + ' != 원장 ' + FACTS.dayAvg);
    /* ① 잔액 = 유량 x 만기 — 허용 오차 2.0% */
    const little = r.dayAvg * Number(FACTS.wRaw);
    const littleGap = Math.abs(little - FACTS.exec) / FACTS.exec * 100;
    if(littleGap > 2.0)
      bad.push('잔액=유량x만기 어긋남 ' + littleGap.toFixed(2) + '% (하루평균 ' + r.dayAvg +
               ' x W ' + FACTS.wRaw + ' = ' + Math.round(little) + ' vs 투자실행액 ' + FACTS.exec + ')');
    push('항등식 — 가맹점합 · W범위 · Ty · 부족율',
      bad.length === 0,
      {bad, dayAvg:r.dayAvg, w:r.w, merSum:r.merSum, wMin:r.wMin, wMax:r.wMax,
       diRange:FACTS.diRange, s:r.s, sRaw:FACTS.sRaw, rate:FACTS.rate,
       receivables:FACTS.receivables, openReceivables:FACTS.openReceivables});
  }

  /* ── 대표 DM 2026-08-31 16:45 항등식 검산 ─────────────────────────
     원문 「투자수익률은 할인율 -max(0, 미지급금-과지급금)/투자실행액 이므로 미지급-과지급이 0이면
     할인율이 되므로 같다」. 원장에서 되짚으면 근사식이다 — 채권매입수수료의 앵커가 순지급액인데
     SMR 의 분모는 투자실행액(순지급액 x (1-할인율))이라 두 값이 1/(1-할인율) 배만큼 갈린다.
     어느 쪽이 정본인지는 대표 확인 대상이라 여기서 고르지 않는다. 판정하는 것은 둘 —
       ① `SMR + 부족액/투자실행액` 이 할인율과 같지 않다 (근사식이다)
       ② 그 갈림이 정확히 `할인율 / (1 - 할인율)` 자리다
     원장 값이 없으면 대상 0건으로 통과하는 것을 막으려고 구간별 건수도 함께 본다. */
  {
    const rate = Number(FACTS.rate);                    /* 0.11 (%) */
    const anchored = rate / (1 - rate / 100);           /* 분모가 순지급액일 때의 값 */
    const agg = (from, to) => {
      let ex = 0, pf = 0, ded = 0, n = 0;
      Object.keys(FACTS.tyByDate).forEach(d => {
        if(d < from || d > to) return;
        const v = FACTS.tyByDate[d];
        ex += v[2]; pf += v[3]; ded += v[6]; n++;
      });
      return {ex, pf, ded, n};
    };
    const spans = [['일주일', '2026-08-21', '2026-08-27'],
                   ['전 구간', FACTS.ledgerSpan[0], FACTS.ledgerSpan[1]]];
    const seen = [], bad = [];
    spans.forEach(sp => {
      const label = sp[0], g = agg(sp[1], sp[2]);
      if(!g.n || !g.ex){ bad.push(label + ' — 원장 행 0건. 대상이 없으면 통과시키지 않는다'); return; }
      const smr = g.pf / g.ex * 100;                    /* 투자수익율 PSMR = PSM / PSA */
      const lhs = smr + g.ded / g.ex * 100;             /* SMR + max(0, 미지급-과지급) / 투자실행액 */
      seen.push({span:label, days:g.n, smr:+smr.toFixed(8), lhs:+lhs.toFixed(8),
                 rate:rate, anchored:+anchored.toFixed(8),
                 gapToRate:+(lhs - rate).toFixed(8), gapToAnchored:+(lhs - anchored).toFixed(8)});
      if(Math.abs(lhs - rate) < 1e-5)
        bad.push(label + ' — 할인율과 1e-5%p 안에서 같다. 근사식이라는 판정이 서지 않는다');
      if(Math.abs(lhs - anchored) > 1e-5)
        bad.push(label + ' — 할인율/(1-할인율) 에서 ' + (lhs - anchored).toExponential(2) + '%p 갈린다');
    });
    if(seen.length !== spans.length) bad.push('구간 ' + seen.length + '/' + spans.length + '건만 셌다');
    push('대표 DM 16:45 항등식 — 근사식이고 갈림이 1/(1-할인율) 자리 (정본은 대표 확인 대기)',
      bad.length === 0, {bad, spans:seen});
  }

  OUT.console = consoleErrors.slice();
  fs.writeFileSync(path.join(OUTDIR, 'verify_identity_result.json'), JSON.stringify(OUT, null, 1));
  let fail = 0;
  OUT.cases.forEach(c => { if(!c.pass) fail++; console.log((c.pass ? 'PASS ' : 'FAIL ') + c.case + '  ' + JSON.stringify(c.detail)); });
  console.log('== 항등식 ' + OUT.cases.length + '건 · FAIL ' + fail + ' · 콘솔 에러 ' + OUT.console.length);
  OUT.console.slice(0, 10).forEach(c => console.log('  - ' + c));
  /* 콘솔 에러를 걷어 찍어 놓고 종료코드에는 안 넣던 자리(2026-08-30 이전).
     형제 검증기(verify_rows.js:213 · verify_toast.js:229 · verify_app.js:809)와 같은 방식으로 맞춘다.
     스크립트가 죽어 숫자가 안 그려지면 항등식은 화면에서 읽을 값이 없는데도 통과할 수 있다. */
  ws.close(); chrome.kill(); server.close();
  process.exit(fail || OUT.console.length ? 1 : 0);
}
main().catch(e => { console.error('IDENTITY ERROR', e); process.exit(1); });
