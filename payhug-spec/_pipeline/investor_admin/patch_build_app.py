# -*- coding: utf-8 -*-
"""build_app.py 데이터셋·산식 갱신 — 로스터 16건 · 페이지 크기 8 · 0.11% 요율 · Ty(투자자산 대비) 기준 교체."""
import io, os, sys, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from roster16_model import ROSTER, EXEC, DAILY, MONTHLY, W_W, S_W, TY_W, r1, r2, ty

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build_app.py')
s = io.open(P, encoding='utf-8').read()
n0 = len(s)
hits = []
def rep(old, new, tag):
    global s
    if s.count(old) != 1: raise SystemExit('%s: %d회' % (tag, s.count(old)))
    s = s.replace(old, new, 1); hits.append(tag)

# ── 1) MERCHANTS 16행 ────────────────────────────────────────────
mer = []
for n, a, w, sv, mid, biz, ceo, sector, item, _sg in ROSTER:
    mer.append("  {mid:'%s', name:'%s', biz:'%s', ceo:'%s', sector:'%s', item:'%s', "
               "buyer:'A-001', buyerName:'㈜페이허그', amount:%d, w:%s, s:%s, ty:%s}"
               % (mid, n, biz, ceo, sector, item, a, w, sv, ty(w)))
a = s.index('var MERCHANTS = ['); b = s.index('];', a) + 2
s = s[:a] + 'var MERCHANTS = [\n' + ',\n'.join(mer) + '\n];' + s[b:]
hits.append('MERCHANTS 16행')

# ── 2) ASSET_ROWS — 투자실행액 행 ────────────────────────────────
rep("{name:'투자실행액', amount:1284500000, w:11.2,  s:0.42, ty:3.59, keeper:'㈜페이허그'},",
    "{name:'투자실행액', amount:%d, w:%s,  s:%s, ty:%s, keeper:'㈜페이허그'}," % (EXEC, r1(W_W), r2(S_W), r2(TY_W)),
    'ASSET_ROWS 투자실행액')

# ── 3) DAILY · MONTHLY 요율 재계산 ───────────────────────────────
for src, rows in (('DAILY', DAILY), ('MONTHLY', MONTHLY)):
    body = ',\n'.join("  {d:'%s', repay:%d, exec:%d, profit:%d, w:%s, ty:%s}"
                      % (r['d'], r['repay'], r['exec'], r['profit'], r['w'], r['ty']) for r in rows)
    a = s.index('var %s = [' % src); b = s.index('];', a) + 2
    s = s[:a] + 'var %s = [\n' % src + body + '\n];' + s[b:]
    hits.append('%s %d행' % (src, len(rows)))

# ── 4) CONTRACTS 16행 ────────────────────────────────────────────
ct = ',\n'.join("  {mid:'%s', name:'%s', signed:'%s'}" % (x[4], x[0], x[9]) for x in ROSTER)
a = s.index('var CONTRACTS = ['); b = s.index('];', a) + 2
s = s[:a] + 'var CONTRACTS = [\n' + ct + '\n];' + s[b:]
hits.append('CONTRACTS 16행')

# ── 5) 페이지 크기 ───────────────────────────────────────────────
rep('var PAGE_SIZE = 5;', 'var PAGE_SIZE = 8;', 'PAGE_SIZE 8')

# ── 6) 비중 산출기 — 반올림 잔차를 최대 금액 행에 흡수 ───────────
rep("function wavg(a, k, wk){",
    "/* 비중 — 소수 1자리 반올림 후 잔차를 최대 금액 행에 흡수해 합계를 정확히 100.0 으로 닫는다 */\n"
    "function ratios(a, base){\n"
    "  var i, out = [], k = 0, t = 0;\n"
    "  for(i = 0; i < a.length; i++){\n"
    "    out.push(base ? Math.round(a[i].amount / base * 1000) / 10 : 0);\n"
    "    t += out[i];\n"
    "    if(a[i].amount > a[k].amount) k = i;\n"
    "  }\n"
    "  if(a.length) out[k] = Math.round((out[k] + (100 - t)) * 10) / 10;\n"
    "  return out;\n"
    "}\n"
    "function wavg(a, k, wk){", 'ratios() 도입')

# ── 7) 투자자산 현황·가맹점 표에 ratios 적용 ─────────────────────
rep("  var tyv = arows.length ? arows[0].ty : 0, wv = arows.length ? arows[0].w : null;",
    "  var tyv = arows.length ? arows[0].ty : 0, wv = arows.length ? arows[0].w : null;\n"
    "  var aRatio = ratios(arows, total), mRatio = ratios(mrows, exec);", 'ratios 계산')
rep("           '<td class=\"num\">' + fx(total ? a.amount / total * 100 : 0, 1) + '%</td><td>' + a.keeper + '</td></tr>';",
    "           '<td class=\"num\">' + fx(aRatio[i], 1) + '%</td><td>' + a.keeper + '</td></tr>';", '현황 비중')
rep("  var rExec = total ? exec / total * 100 : 0, rCash = total ? cash / total * 100 : 0;",
    "  var rExec = 0, rCash = 0;\n"
    "  for(i = 0; i < arows.length; i++){}\n", '요약 비중 자리')
rep("  var view = mrows.map(function(r){\n"
    "    var o = {}; for(var k in r) o[k] = r[k];\n"
    "    o.ratio = exec ? r.amount / exec * 100 : 0; return o;\n"
    "  });",
    "  var view = mrows.map(function(r, i){\n"
    "    var o = {}; for(var k in r) o[k] = r[k];\n"
    "    o.ratio = mRatio[i]; return o;\n"
    "  });", '가맹점 비중')

# ── 8) 증명서 비중 ───────────────────────────────────────────────
rep("  var exec = iaExecTotal(), i, h =",
    "  var exec = iaExecTotal(), cRatio = ratios(MERCHANTS, exec), i, h =", '증명서 ratios')
rep("         '<td class=\"num\">' + fx(m.amount / exec * 100, 1) + '%</td></tr>';",
    "         '<td class=\"num\">' + fx(cRatio[i], 1) + '%</td></tr>';", '증명서 비중')

# ── 9) Ty(투자자산 대비) — 분자를 투자실행액으로 고정 ────────────
rep('var tyAsset = (rows.length && assetTotal()) ? tyExec * exec / assetTotal() : 0;',
    'var tyAsset = (rows.length && assetTotal()) ? tyExec * ASSET_ROWS[0].amount / assetTotal() : 0;', 'tyAsset 산식')
rep('var tyA = (rw.length && total) ? tyE * pexec / total : 0;',
    'var tyA = (rw.length && total) ? tyE * ASSET_ROWS[0].amount / total : 0;', 'tyA 산식')

# ── 10) 엑셀 시트 — 비중·행번호 ──────────────────────────────────
rep("  var i, rows = [], cols, exec = iaExecTotal(), total = assetTotal();",
    "  var i, rows = [], cols, exec = iaExecTotal(), total = assetTotal();\n"
    "  var sRatio = ratios(ASSET_ROWS, total), xRatio = ratios(MERCHANTS, exec);", '시트 ratios')
rep("        {v:fx(a.amount / total * 100, 1) + '%', c:'c-num'}, {v:a.keeper}]});",
    "        {v:fx(sRatio[i], 1) + '%', c:'c-num'}, {v:a.keeper}]});", '시트 현황 비중')
rep("{v:pct(m.ty, 2), c:'c-num'}, {v:fx(m.amount / exec * 100, 1) + '%', c:'c-num'}, null]});",
    "{v:pct(m.ty, 2), c:'c-num'}, {v:fx(xRatio[i], 1) + '%', c:'c-num'}, null]});", '시트 가맹점 비중')
rep("    rows.push({n:12, cls:'r-total', c:[{v:'합계'}, {v:fmt(exec), c:'c-num'}, {v:''}, {v:''}, {v:''}, {v:'100.0%', c:'c-num'}, null]});\n"
    "    rows.push({n:13, c:[null, null, null, null, null, null, null]});\n"
    "    rows.push({n:14, c:[{v:'※ 비중은 투자실행액 합계(' + fmt(exec) + '원) 대비 각 가맹점 투자실행액의 구성비.', c:'c-note', span:7}]});",
    "    var tot = 4 + MERCHANTS.length;\n"
    "    rows.push({n:tot, cls:'r-total', c:[{v:'합계'}, {v:fmt(exec), c:'c-num'}, {v:''}, {v:''}, {v:''}, {v:'100.0%', c:'c-num'}, null]});\n"
    "    rows.push({n:tot + 1, c:[null, null, null, null, null, null, null]});\n"
    "    rows.push({n:tot + 2, c:[{v:'※ 비중은 투자실행액 합계(' + fmt(exec) + '원) 대비 각 가맹점 투자실행액의 구성비.', c:'c-note', span:7}]});",
    '시트 합계 행번호')

# ── 11) 자체 점검 ────────────────────────────────────────────────
rep("    ratioSum: Number(MERCHANTS.reduce(function(a, m){ return a + Number((m.amount / exec * 100).toFixed(1)); }, 0).toFixed(1)),",
    "    ratioSum: Number(ratios(MERCHANTS, exec).reduce(function(a, r){ return a + r; }, 0).toFixed(1)),",
    'selfcheck ratioSum')

io.open(P, 'w', encoding='utf-8').write(s)
print('build_app.py %d → %d bytes' % (n0, len(s)))
for h in hits: print('  ·', h)
