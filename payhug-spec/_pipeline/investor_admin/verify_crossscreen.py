# -*- coding: utf-8 -*-
"""화면 간 정합 — 정적 HTML · app.html 데이터셋 · xlsx 실파일이 같은 숫자를 말하는지 대조."""
import io, os, re, json, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from roster16_model import ROSTER, SHARES, EXEC, CASH, TOTAL, W_W, S_W, TY_W, EXEC_SHARE, CASH_SHARE, DAILY, MONTHLY, DSUM, AUG_CARD, r1, r2, ty, f
import openpyxl

ROOT = '/Users/semi/cursor/payhug-investor-admin'
def rd(p): return io.open(os.path.join(ROOT, p), encoding='utf-8').read()
def n(t): return int(str(t).replace(',', ''))
strip = lambda h: re.sub(r'<[^>]+>', '', h).strip()

rows_out, fails = [], 0
def chk(name, got, want):
    global fails
    ok = got == want
    if not ok: fails += 1
    rows_out.append((name, ok, got, want))

WANT_MERCH = [(x[0], x[1], x[2], x[3], str(ty(x[2])), str(sh)) for x, sh in zip(ROSTER, SHARES)]

# ── 정적 HTML: 가맹점 표 ──────────────────────────────────────────
TR = re.compile(r'<tr>\s*<td><span class="name">([^<]+)</span></td>\s*'
                r'<td class="num"><span class="strong">([\d,]+)</span></td>\s*'
                r'<td class="num">([\d.]+)일</td>\s*<td class="num">([\d.]+)%</td>\s*'
                r'<td class="num">([\d.]+)%</td>\s*<td class="num">([\d.]+)%</td>\s*</tr>')
def html_merch(p):
    return [(a, n(b), c, d, e, g) for a, b, c, d, e, g in TR.findall(rd(p))]

p1 = html_merch('invest-assets.html')
p2 = html_merch('invest-assets--page2.html')
chk('invest-assets 1p+2p 로스터', p1 + p2, WANT_MERCH)
chk('invest-assets--download 1p',  html_merch('invest-assets--download.html'), WANT_MERCH[:10])
chk('invest-assets--cert-confirm 1p', html_merch('invest-assets--cert-confirm.html'), WANT_MERCH[:10])

# ── 증명서 ────────────────────────────────────────────────────────
CTR = re.compile(r'<tr>\s*<td>([^<]+)</td>\s*<td class="num">([\d,]+)</td>\s*<td class="num">([\d.]+)일</td>\s*'
                 r'<td class="num">([\d.]+)%</td>\s*<td class="num">([\d.]+)%</td>\s*<td class="num">([\d.]+)%</td>\s*</tr>')
cert = rd('certificate.html')
chk('certificate 로스터', [(a, n(b), c, d, e, g) for a, b, c, d, e, g in CTR.findall(cert)], WANT_MERCH)
chk('certificate 대상 건수', re.search(r'대상 가맹점</span><span class="v">(\d+)개', cert).group(1), str(len(ROSTER)))

# ── 엑셀 미리보기 ─────────────────────────────────────────────────
XTR = re.compile(r'<tr><th class="row-head">\d+</th><td>([^<]+)</td><td class="c-num">([\d,]+)</td>'
                 r'<td class="c-num">([\d.]+)</td><td class="c-num">([\d.]+)%</td>'
                 r'<td class="c-num">([\d.]+)%</td><td class="c-num">([\d.]+)%</td>')
chk('xls-assets-merchant 로스터',
    [(a, n(b), c, d, e, g) for a, b, c, d, e, g in XTR.findall(rd('xls-assets-merchant.html'))], WANT_MERCH)

# ── xlsx 실파일 ───────────────────────────────────────────────────
wb = openpyxl.load_workbook(os.path.join(ROOT, 'assets/xlsx/가맹점별투자자산_2026-08-27_2026-08-27.xlsx'))
ws = wb['가맹점별 투자자산']
xls = [(ws['A%d' % r].value, ws['B%d' % r].value,
        ('%.1f' % ws['C%d' % r].value), ('%.2f' % (ws['D%d' % r].value * 100)),
        ('%.2f' % (ws['E%d' % r].value * 100)), ('%.1f' % (ws['F%d' % r].value * 100)))
       for r in range(4, 4 + len(ROSTER))]
chk('가맹점별투자자산.xlsx 로스터', xls, WANT_MERCH)
chk('가맹점별투자자산.xlsx 합계', (ws['B20'].value, round(ws['F20'].value, 4)), (EXEC, 1))

wb = openpyxl.load_workbook(os.path.join(ROOT, 'assets/xlsx/투자자산현황_2026-08-27_2026-08-27.xlsx'))
ws = wb['투자자산 현황']
chk('투자자산현황.xlsx 투자실행액 행',
    (ws['B4'].value, '%.1f' % ws['C4'].value, '%.2f' % (ws['D4'].value * 100),
     '%.2f' % (ws['E4'].value * 100), '%.1f' % (ws['F4'].value * 100)),
    (EXEC, str(r1(W_W)), str(r2(S_W)), str(r2(TY_W)), str(EXEC_SHARE)))
chk('투자자산현황.xlsx 순현금·합계',
    (ws['B5'].value, '%.1f' % (ws['F5'].value * 100), ws['B6'].value),
    (CASH, str(CASH_SHARE), TOTAL))

wb = openpyxl.load_workbook(os.path.join(ROOT, 'assets/xlsx/일별투자수익_2026-08-21_2026-08-27.xlsx'))
ws = wb['일별 투자수익']
chk('일별투자수익.xlsx 7행',
    [(ws['A%d' % r].value, ws['B%d' % r].value, ws['C%d' % r].value, ws['D%d' % r].value,
      '%.1f' % ws['E%d' % r].value, '%.2f' % (ws['F%d' % r].value * 100)) for r in range(4, 11)],
    [(x['d'], x['repay'], x['exec'], x['profit'], x['w'], str(x['ty'])) for x in DAILY])
chk('일별투자수익.xlsx 합계',
    (ws['B11'].value, ws['C11'].value, ws['D11'].value, '%.1f' % ws['E11'].value, '%.2f' % (ws['F11'].value * 100)),
    (DSUM['repay'], DSUM['exec'], DSUM['profit'], str(DSUM['w']), str(DSUM['ty'])))

wb = openpyxl.load_workbook(os.path.join(ROOT, 'assets/xlsx/투자수익현황_2026-08-21_2026-08-27.xlsx'))
ws = wb['투자수익 현황']
chk('투자수익현황.xlsx 카드',
    (ws['B5'].value, ws['B6'].value, '%.2f' % (ws['B7'].value * 100), '%.2f' % (ws['B8'].value * 100)),
    (DSUM['exec'], DSUM['profit'], str(DSUM['ty']), str(DSUM['tyAsset'])))

# ── 정적 투자수익 화면 ────────────────────────────────────────────
PR = re.compile(r'<td class="mono">(\d{4}-\d\d(?:-\d\d)?)</td>\s*<td class="num">([\d,]+)</td>\s*'
                r'<td class="num">([\d,]+)</td>\s*<td class="num"><span class="strong">([\d,]+)</span></td>\s*'
                r'<td class="num">([\d.]+)</td>\s*<td class="num">([\d.]+)%</td>')
def html_profit(p):
    return [(a, n(b), n(c), n(d), e, g) for a, b, c, d, e, g in PR.findall(rd(p))]
want_daily = [(x['d'], x['repay'], x['exec'], x['profit'], x['w'], str(x['ty'])) for x in DAILY]
want_mon   = [(x['d'], x['repay'], x['exec'], x['profit'], x['w'], str(x['ty'])) for x in MONTHLY]
chk('invest-profit 일별 7행', html_profit('invest-profit.html'), want_daily)
chk('invest-profit--monthly 월별 6행', html_profit('invest-profit--monthly.html'), want_mon)

# ── 주별·월별 낱장 ↔ 주별·월별 엑셀 실물 ─────────────────────────
#   버킷 라벨(2026-08-17 ~ 08-23 · 2026-08)을 받는 별도 정규식으로 낱장 표를 읽고,
#   같은 자리 엑셀과 값을 맞대 본다. 화면과 파일이 갈라지면 여기서 걸린다.
BR = re.compile(r'<td class="mono">([\d\-~ ]+)</td>\s*<td class="num">([\d,]+)</td>\s*'
                r'<td class="num">([\d,]+)</td>\s*<td class="num"><span class="strong">([\d,]+)</span></td>\s*'
                r'<td class="num">([\d.]+)</td>\s*<td class="num">([\d.]+)%</td>')
def html_bucket(p):
    return [(a.strip(), n(b), n(c), n(d), e, g) for a, b, c, d, e, g in BR.findall(rd(p))]

def xls_bucket(fn, sheet, nrows):
    w = openpyxl.load_workbook(os.path.join(ROOT, 'assets/xlsx/' + fn))[sheet]
    return [(str(w['A%d' % r].value), w['B%d' % r].value, w['C%d' % r].value, w['D%d' % r].value,
             '%.1f' % w['E%d' % r].value, '%.2f' % (w['F%d' % r].value * 100))
            for r in range(4, 4 + nrows)]

chk('invest-profit--weekly 낱장 = 주별투자수익.xlsx 4행',
    html_bucket('invest-profit--weekly.html'),
    xls_bucket('주별투자수익_2026-08-03_2026-08-30.xlsx', '주별 투자수익', 4))
chk('invest-profit--monthly 낱장 = 월별투자수익.xlsx 6행',
    html_bucket('invest-profit--monthly.html'),
    xls_bucket('월별투자수익_2026-03-01_2026-08-31.xlsx', '월별 투자수익', 6))

# ── 주별·월별 낱장의 `수익 현황` 카드 ↔ 같은 기간 현황 엑셀 ───────
#   카드가 4주를 말하는데 링크·파일이 일주일이면 여기서 걸린다.
CARD_NUM = re.compile(r'<div class="summary-label">(?:투자실행금|투자수익)</div>\s*'
                      r'<div class="summary-value">([\d,]+)<span class="unit">원</span>')
CARD_TY = re.compile(r'(?:투자실행금액|투자자산) 대비.*?<div class="summary-value">([\d.]+)'
                     r'<span class="unit">%</span>', re.S)
CARD_PERIOD = re.compile(r'<div class="summary-sub mono">([^<]+)</div>')

def html_status(p):
    s_ = rd(p)
    ex, pf = [n(x) for x in CARD_NUM.findall(s_)]
    t4, t5 = CARD_TY.findall(s_)
    return (CARD_PERIOD.search(s_).group(1), ex, pf, t4, t5)

def xls_status(fn):
    w = openpyxl.load_workbook(os.path.join(ROOT, 'assets/xlsx/' + fn))['투자수익 현황']
    period = w['B4'].value.split('(')[1].rstrip(')')
    return (period, w['B5'].value, w['B6'].value,
            '%.2f' % (w['B7'].value * 100), '%.2f' % (w['B8'].value * 100))

for _f, _x in (('invest-profit.html',            '투자수익현황_2026-08-21_2026-08-27.xlsx'),
               ('invest-profit--weekly.html',    '투자수익현황_2026-08-03_2026-08-30.xlsx'),
               ('invest-profit--monthly.html',   '투자수익현황_2026-03-01_2026-08-31.xlsx')):
    chk('%s 현황 카드 = %s' % (_f.replace('.html', ''), _x), html_status(_f), xls_status(_x))
    _href = 'assets/xlsx/' + _x
    chk('%s 현황 카드 링크' % _f.replace('.html', ''), _href in rd(_f), True)

XPR = re.compile(r'<td class="c-num">([\d,]+)</td><td class="c-num">([\d,]+)</td><td class="c-num">([\d,]+)</td>'
                 r'<td class="c-num">([\d.]+)</td><td class="c-num">([\d.]+)%</td>')
chk('xls-profit-daily 7행',
    [(n(a), n(b), n(c), d, e) for a, b, c, d, e in XPR.findall(rd('xls-profit-daily.html'))][:7],
    [(x['repay'], x['exec'], x['profit'], x['w'], str(x['ty'])) for x in DAILY])

sp = rd('xls-profit-status.html')
chk('xls-profit-status 카드',
    (n(re.search(r'투자실행금</td><td class="c-num">([\d,]+)', sp).group(1)),
     n(re.search(r'>투자수익</td><td class="c-num">([\d,]+)', sp).group(1)),
     re.search(r'투자실행금액 대비\)</td><td class="c-num">([\d.]+)%', sp).group(1),
     re.search(r'투자자산 대비\)</td><td class="c-num">([\d.]+)%', sp).group(1)),
    (DSUM['exec'], DSUM['profit'], str(DSUM['ty']), str(DSUM['tyAsset'])))

# ── app.html 데이터셋 ────────────────────────────────────────────
app = rd('app.html')
def jsarr(name):
    a = app.index('var %s = [' % name); b = app.index('];', a)
    return app[a:b]
mm = re.findall(r"name:'([^']+)'.*?amount:(\d+), w:([\d.]+), s:([\d.]+), ty:([\d.]+)", jsarr('MERCHANTS'))
chk('app.html MERCHANTS',
    [(a, int(b), ('%.1f' % float(c)), ('%.2f' % float(d)), ('%.2f' % float(e))) for a, b, c, d, e in mm],
    [(x[0], x[1], x[2], x[3], str(ty(x[2]))) for x in ROSTER])
ar = re.search(r"\{name:'투자실행액', amount:(\d+), w:([\d.]+),\s+s:([\d.]+), ty:([\d.]+)", app)
chk('app.html ASSET_ROWS 투자실행액',
    (int(ar.group(1)), '%.1f' % float(ar.group(2)), '%.2f' % float(ar.group(3)), '%.2f' % float(ar.group(4))),
    (EXEC, str(r1(W_W)), str(r2(S_W)), str(r2(TY_W))))
def jsrows(name):
    return [(a, int(b), int(c), int(d), ('%.1f' % float(e)), ('%.2f' % float(g)))
            for a, b, c, d, e, g in re.findall(r"\{d:'([\d-]+)', repay:(\d+), exec:(\d+), profit:(\d+), w:([\d.]+), ty:([\d.]+)\}", jsarr(name))]
# app.html 은 일별 원장 한 벌만 갖고, 월별 표는 그 원장을 달별로 합쳐 만든다.
# 대조 1 — 원장 가운데 기본 조회 기간(일주일) 구간이 정적 화면·xlsx 와 같은 7행인가.
# 대조 2 — 원장을 달별로 합친 값이 월별 정적 화면의 6행과 같은가(합계·가중평균 모두).
LEDGER = jsrows('DAILY')
chk('app.html 일별 원장 · 기본 기간 7행',
    [r for r in LEDGER if '2026-08-21' <= r[0] <= '2026-08-27'], want_daily)

def month_rollup(rows):
    """통합본 build_app.py 의 rollupBy 와 같은 규칙으로 달별로 묶는다.

    W금융일수는 투자실행금 가중평균, Ty수익율은 그 가중평균에서 되짚는다(PSMR x 365 / PSD).
    일자별 Ty 를 다시 가중평균하면 1/w 의 볼록성 때문에 달 행에 적힌 W 로 되짚을 수 없다.
    만기가 3일대로 짧아지면 그 격차가 0.05%p 까지 벌어져 화면과 대조가 갈린다.
    """
    from decimal import Decimal as _D
    agg, order = {}, []
    for d, repay, ex, pr, w, t in rows:
        k = d[:7]
        if k not in agg:
            agg[k] = dict(repay=0, ex=0, pr=0, wx=_D(0)); order.append(k)
        g = agg[k]
        g['repay'] += repay; g['ex'] += ex; g['pr'] += pr
        g['wx'] += _D(w) * _D(ex)
    out = []
    for k in order:
        g = agg[k]
        wv = g['wx'] / _D(g['ex'])
        tv = (_D(g['pr']) / _D(g['ex']) * _D(100)) * _D(365) / wv
        out.append((k, g['repay'], g['ex'], g['pr'], str(r1(wv)), str(r2(tv))))
    return out
chk('app.html 일별 원장 월 롤업 = 월별 6행', month_rollup(LEDGER), want_mon)
chk('app.html PAGE_SIZE', re.search(r'var PAGE_SIZE = (\d+);', app).group(1), '10')

# ── W금융일수 현실 범위 — 조현준 슬랙 2026-08-28 실측 2.0 ~ 6.2일 ──
from platform_duration import FLOOR, CEIL
from decimal import Decimal as _DD
def in_range(vals):
    return sorted({str(v) for v in vals if not (_DD(str(FLOOR)) <= _DD(str(v)) <= _DD(str(CEIL)))})
chk('로스터 16건 W금융일수 ⊂ [%s, %s]' % (FLOOR, CEIL), in_range(x[2] for x in ROSTER), [])
chk('일별 원장 180일 W금융일수 ⊂ [%s, %s]' % (FLOOR, CEIL), in_range(r[4] for r in LEDGER), [])
chk('낱장 가맹점 표 W금융일수 ⊂ [%s, %s]' % (FLOOR, CEIL), in_range(x[2] for x in p1 + p2), [])
chk('투자실행액 행 W금융일수 ⊂ [%s, %s]' % (FLOOR, CEIL), in_range([r1(W_W)]), [])

# ── Duration(가중평균만기) 등재 — 용어 문서에만, 화면에는 쓰지 않는다 ──
gl = rd('glossary.html')
chk('용어 해설 · Duration 카드 3종', gl.count('금융 일반 용어로는'), 3)
chk('용어 해설 · 가중평균만기 표기', ('Duration' in gl) and ('가중평균만기' in gl), True)
chk('용어 해설 · 플랫폼별 평균만기 실측 4건',
    all(v in gl for v in ('2.0일', '3.4일', '4.7일', '6.2일')), True)
chk('용어 해설 · 출처 병기', '조현준 슬랙 2026-08-28' in gl, True)
screens = [rd(x) for x in ('app.html', 'invest-assets.html', 'invest-assets--page2.html',
                           'invest-profit.html', 'invest-profit--weekly.html',
                           'invest-profit--monthly.html', 'certificate.html')]
chk('화면에는 Duration 설명문 없음 (D-23)',
    sorted({w for w in ('Duration', '가중평균만기', '평균만기') for t in screens if w in t}), [])

print('== 화면 간 정합 %d건 · 불일치 %d ==' % (len(rows_out), fails))
for name, ok, got, want in rows_out:
    print(('  PASS ' if ok else '  FAIL ') + name)
    if not ok:
        print('        got :', got)
        print('        want:', want)
sys.exit(1 if fails else 0)
