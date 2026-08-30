# -*- coding: utf-8 -*-
"""
정정값 맵 생성기 — payhug-investor-admin 은 읽기만 하고, 산출물은 rate_fix_map.json 1건.
locator 는 대상 파일에서 정확히 1회만 일치하는지 전건 검증한다.
"""
import json, os, io
from decimal import Decimal as D, ROUND_HALF_UP, ROUND_FLOOR

ROOT = '/Users/semi/cursor/payhug-investor-admin'
OUT  = '/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/rate_fix_map.json'
R, RP, DAYS = D('0.0011'), D('0.11'), D('365')
A_EXEC, A_CASH = 1284500000, 105300000
A_TOT = A_EXEC + A_CASH

def fl(x):  return int(D(x).quantize(D('1'), rounding=ROUND_FLOOR))
def r2(x):  return D(x).quantize(D('0.01'), rounding=ROUND_HALF_UP)
def r1(x):  return D(x).quantize(D('0.1'),  rounding=ROUND_HALF_UP)
def ty(w):  return r2(RP * DAYS / D(str(w)))
def pf(e):  return fl(D(e) * R)
def f(n):   return format(n, ',')
def wavg(rows, k, wk):
    n = sum(D(str(r[k]))*D(str(r[wk])) for r in rows); d = sum(D(str(r[wk])) for r in rows)
    return n/d if d else D(0)

CACHE = {}
def src(fn):
    if fn not in CACHE: CACHE[fn] = io.open(os.path.join(ROOT, fn), encoding='utf-8').read()
    return CACHE[fn]

FIX, ERR = [], []
def fix(fn, loc, cur, cor, basis, kind='text'):
    if kind == 'text':
        n = src(fn).count(loc)
        if n != 1: ERR.append('%s : locator 일치 %d회 -> %r' % (fn, n, loc[:90]))
        if loc == cor: ERR.append('%s : locator == corrected -> %r' % (fn, loc[:90]))
    FIX.append(dict(file=fn, kind=kind, locator=loc, current=cur, corrected=cor, basis=basis))

B_PROFIT = '투자 수익 = 투자실행금(양수가액) × 0.11% 버림. figma_policy_db.md:79 (49,446×0.11%=54.3906→54)'
B_REPAY  = '상환액 = 투자실행금 + 투자 수익. 정산채권DB 금액체인(양수가액+분배액=입금액), figma_policy_db.md:77~80'
B_TY     = 'Ty수익율 = 할인율 0.11% × (365 ÷ W금융일수). 스토리보드_Admin_투자자 슬라이드3~9 정의문'
B_WAVG   = '합계행 = 투자금액 가중평균 (화면 주석 "투자금액 가중평균(단순평균 아님)" · app.html wavg())'
B_CARD   = '요약 카드 = 표 합계와 동일 (app.html RENDER[invest-profit] sum(rows,...))'
B_TYA    = 'Ty(투자자산 대비) = Ty(가중) × 투자실행액 1,284,500,000 ÷ 투자자산 1,389,800,000 (무수익 순현금 가중)'

# ── 데이터 ───────────────────────────────────────────────────────────
DAILY_IN = [('2026-08-21',182300000,178900000,601000,'11.4','3.55'),
            ('2026-08-22',175800000,172600000,578000,'11.1','3.61'),
            ('2026-08-23',168400000,165300000,552000,'10.9','3.58'),
            ('2026-08-24',191200000,187700000,634000,'11.6','3.52'),
            ('2026-08-25',186500000,183100000,617000,'11.3','3.57'),
            ('2026-08-26',179900000,176600000,596000,'11.2','3.59'),
            ('2026-08-27',190100000,186600000,632000,'11.5','3.54')]
MON_IN   = [('2026-03',5124600000,5031200000,16980000,'11.4','3.51'),
            ('2026-04',5387900000,5289400000,17920000,'11.2','3.56'),
            ('2026-05',5642300000,5538700000,18730000,'11.0','3.62'),
            ('2026-06',5478100000,5376500000,18140000,'11.6','3.48'),
            ('2026-07',5861400000,5752800000,19480000,'11.3','3.60'),
            ('2026-08',5203700000,5108900000,17260000,'11.5','3.55')]

def build(rows_in):
    out = []
    for d, rp0, ex, p0, w, t0 in rows_in:
        p = pf(ex); out.append(dict(d=d, repay0=rp0, exec=ex, profit0=p0, w=w, ty0=t0,
                                    profit=p, repay=ex+p, ty=ty(w)))
    return out
DAILY, MON = build(DAILY_IN), build(MON_IN)
def tot(rs):
    return dict(repay=sum(r['repay'] for r in rs), exec=sum(r['exec'] for r in rs),
                profit=sum(r['profit'] for r in rs),
                w=r1(wavg(rs,'w','exec')), ty=r2(wavg(rs,'ty','exec')))
DT, MT = tot(DAILY), tot(MON)

# ── 1. 화면 표 (일별 3파일 / 월별 1파일) ────────────────────────────
ROW = ('              <td class="mono">%s</td>\n'
       '              <td class="num">%s</td>\n'
       '              <td class="num">%s</td>\n'
       '              <td class="num"><span class="strong">%s</span></td>\n'
       '              <td class="num">%s</td>\n'
       '              <td class="num">%s%%</td>')
for fn, rs in (('invest-profit.html', DAILY),
               ('invest-profit--monthly.html', MON)):
    for r in rs:
        fix(fn, ROW % (r['d'], f(r['repay0']), f(r['exec']), f(r['profit0']), r['w'], r['ty0']),
                '상환액 %s · 투자 수익 %s · Ty %s%%' % (f(r['repay0']), f(r['profit0']), r['ty0']),
                ROW % (r['d'], f(r['repay']), f(r['exec']), f(r['profit']), r['w'], r['ty']),
                '%s / %s / %s' % (B_REPAY, B_PROFIT, B_TY))

FOOT = ('              <td>합계</td>\n'
        '              <td class="num">%s</td>\n'
        '              <td class="num">%s</td>\n'
        '              <td class="num">%s</td>\n'
        '              <td class="num">%s<span class="avg-note">(평균)</span></td>\n'
        '              <td class="num">%s%%%s</td>')
for fn, T, tail in (('invest-profit.html', DT, ''),
                    ('invest-profit--monthly.html', MT, '<span class="avg-note">(평균)</span>')):
    o = ('1,274,200,000','1,250,800,000','4,210,000','11.3','3.58') if T is DT \
        else ('32,698,000,000','32,097,500,000','108,510,000','11.3','3.55')
    fix(fn, FOOT % (o[0], o[1], o[2], o[3], o[4], tail),
            '합계 상환액 %s · 수익 %s · Ty %s%%' % (o[0], o[2], o[4]),
            FOOT % (f(T['repay']), f(T['exec']), f(T['profit']), T['w'], T['ty'], tail),
            '%s / %s' % (B_WAVG, B_PROFIT))

# ── 2. 수익 현황 카드 ────────────────────────────────────────────────
CV  = '<div class="summary-value">%s<span class="unit">원</span></div>'
CP  = '>%s<span class="unit">%%</span></div>'
for fn, T in (('invest-profit.html', DT),):
    fix(fn, CV % '1,284,500,000', '1,284,500,000', CV % f(DT['exec']),
        B_CARD + ' — 표 합계 1,250,800,000 과 불일치(투자자산 투자실행액을 잘못 옮겨 적음)')
    fix(fn, CV % '4,210,000', '4,210,000', CV % f(DT['profit']), B_CARD + ' / ' + B_PROFIT)
    fix(fn, CP % '3.58', '3.58%', CP % r2(wavg(DAILY,'ty','exec')), B_WAVG + ' / ' + B_TY)
    fix(fn, CP % '3.31', '3.31%', CP % r2(wavg(DAILY,'ty','exec')*D(A_EXEC)/D(A_TOT)), B_TYA)
aug = MON[-1]
fix('invest-profit--monthly.html', CV % '1,284,500,000', '1,284,500,000', CV % f(aug['exec']),
    B_CARD + ' — 이번달 필터 결과는 2026-08 1건, 실행금 5,108,900,000')
fix('invest-profit--monthly.html', CV % '17,260,000', '17,260,000', CV % f(aug['profit']), B_CARD + ' / ' + B_PROFIT)
fix('invest-profit--monthly.html', CP % '3.55', '3.55%', CP % aug['ty'], B_TY)
fix('invest-profit--monthly.html', CP % '3.28', '3.28%', CP % r2(aug['ty']*D(A_EXEC)/D(A_TOT)), B_TYA)

# ── 3. 엑셀 미리보기 화면 ───────────────────────────────────────────
XR = ('<tr><th class="row-head">%d</th><td class="mono">%s</td><td class="c-num">%s</td>'
      '<td class="c-num">%s</td><td class="c-num">%s</td><td class="c-num">%s</td>'
      '<td class="c-num">%s%%</td><td class="c-empty"></td></tr>')
for i, r in enumerate(DAILY):
    fix('xls-profit-daily.html', XR % (4+i, r['d'], f(r['repay0']), f(r['exec']), f(r['profit0']), r['w'], r['ty0']),
        '상환액 %s · 수익 %s · Ty %s%%' % (f(r['repay0']), f(r['profit0']), r['ty0']),
        XR % (4+i, r['d'], f(r['repay']), f(r['exec']), f(r['profit']), r['w'], r['ty']),
        '%s / %s / %s' % (B_REPAY, B_PROFIT, B_TY))
XT = ('<tr class="r-total"><th class="row-head">11</th><td>합계</td><td class="c-num">%s</td>'
      '<td class="c-num">%s</td><td class="c-num">%s</td><td class="c-num">%s</td>'
      '<td class="c-num">%s%%</td><td class="c-empty"></td></tr>')
fix('xls-profit-daily.html', XT % ('1,274,200,000','1,250,800,000','4,210,000','11.3','3.58'),
    '합계 상환액 1,274,200,000 · 수익 4,210,000 · Ty 3.58%',
    XT % (f(DT['repay']), f(DT['exec']), f(DT['profit']), DT['w'], DT['ty']), B_WAVG)
fix('xls-profit-daily.html', '가중평균(단순평균 아님) — 11.3일 / 3.58%.', '11.3일 / 3.58%',
    '가중평균(단순평균 아님) — %s일 / %s%%.' % (DT['w'], DT['ty']), B_WAVG)

XS = '<tr><th class="row-head">%d</th><td>%s</td><td class="c-num">%s</td>'
for n, lab, cur, cor, b in ((5,'투자실행금','1,284,500,000',f(DT['exec']),B_CARD),
                            (6,'투자수익','4,210,000',f(DT['profit']),B_PROFIT),
                            (7,'Ty수익율 (투자실행금액 대비)','3.58%',str(DT['ty'])+'%',B_WAVG),
                            (8,'Ty수익율 (투자자산 대비)','3.31%',
                               str(r2(wavg(DAILY,'ty','exec')*D(A_EXEC)/D(A_TOT)))+'%',B_TYA)):
    fix('xls-profit-status.html', XS % (n, lab, cur), cur, XS % (n, lab, cor), b)

# ── 4. 투자자산 — 투자실행액 행의 W·Ty (가중평균 규칙) ──────────────
MER = [('김성호떡볶이 본점',312400000,'10.8','0.31'), ('달빛곱창 홍대점',268900000,'11.5','0.55'),
       ('성호분식 2호점',197300000,'12.1','0.28'),   ('바다마루 횟집',152600000,'10.2','0.47'),
       ('한강커피 잠원점',121800000,'11.9','0.62'),  ('김밥나라',98200000,'10.5','0.19'),
       ('초록치킨 서초점',76100000,'12.4','0.71'),   ('골목냉면',57200000,'11.0','0.38')]
M = [dict(amount=a, w=w, s=s, ty=ty(w)) for _, a, w, s in MER]
mW, mTy = r1(wavg(M,'w','amount')), r2(wavg(M,'ty','amount'))
B_AW = ('투자실행액 행 = 가맹점 8행의 투자금액 가중평균. 같은 행 S입금부족율 0.42%가 이미 '
        '가중평균값(0.4217)과 일치해 규칙이 입증됨. 가중 W = 11.2600 → 11.3')
for fn in ('invest-assets.html','invest-assets--page2.html','invest-assets--download.html','invest-assets--cert-confirm.html'):
    fix(fn, '<td class="num">11.2일</td>', '11.2일', '<td class="num">%s일</td>' % mW, B_AW)
    fix(fn, '<td class="num">3.59%</td>', '3.59%', '<td class="num">%s%%</td>' % mTy, B_AW + ' / ' + B_WAVG)
    fix(fn, '<div class="summary-value">3.59<span class="unit">%</span></div>', '3.59%',
            '<div class="summary-value">%s<span class="unit">%%</span></div>' % mTy, B_WAVG)
    fix(fn, '<div class="summary-sub">W금융일수 11.2일 기준</div>', 'W금융일수 11.2일 기준',
            '<div class="summary-sub">W금융일수 %s일 기준</div>' % mW, B_AW)
fix('xls-assets-status.html',
    '<td class="c-num">11.2</td><td class="c-num">0.42%</td><td class="c-num">3.59%</td>',
    'W 11.2 · Ty 3.59%',
    '<td class="c-num">%s</td><td class="c-num">0.42%%</td><td class="c-num">%s%%</td>' % (mW, mTy),
    B_AW + ' / ' + B_WAVG)

# ── 5. page2 유령 가맹점 Ty ─────────────────────────────────────────
P2 = [('청춘포차 신촌점',48900000,'11.3','0.44','3.51'), ('왕십리곱창타운',42300000,'10.6','0.26','3.78'),
      ('소소한밥상',37600000,'12.2','0.58','3.29'),      ('대박국수 사당점',31400000,'11.7','0.33','3.42'),
      ('정든수산',26800000,'10.9','0.51','3.68'),        ('착한고기 은평점',21500000,'12.6','0.67','3.21'),
      ('커피한잔 마포점',17200000,'11.1','0.22','3.74'), ('우리동네반찬',12900000,'10.4','0.35','3.86')]
P2ROW = ('              <td><span class="name">%s</span></td>\n'
         '              <td class="num"><span class="strong">%s</span></td>\n'
         '              <td class="num">%s일</td>\n'
         '              <td class="num">%s%%</td>\n'
         '              <td class="num">%s%%</td>')
for n, a, w, s, t0 in P2:
    t = ty(w)
    if str(t) == t0: continue
    fix('invest-assets--page2.html', P2ROW % (n, f(a), w, s, t0), 'Ty %s%%' % t0,
        P2ROW % (n, f(a), w, s, t), B_TY)

# ── 6. app.html (데이터 배열 · 산식) ────────────────────────────────
fix('app.html', "{name:'투자실행액', amount:1284500000, w:11.2,  s:0.42, ty:3.59, keeper:'㈜페이허그'},",
    'w:11.2 · ty:3.59', "{name:'투자실행액', amount:1284500000, w:%s,  s:0.42, ty:%s, keeper:'㈜페이허그'}," % (mW, mTy), B_AW)
AR = "  {d:'%s', repay:%d, exec:%d, profit:%d, w:%s, ty:%s}"
for rs in (DAILY, MON):
    for r in rs:
        fix('app.html', AR % (r['d'], r['repay0'], r['exec'], r['profit0'], r['w'], r['ty0']),
            'repay:%d · profit:%d · ty:%s' % (r['repay0'], r['profit0'], r['ty0']),
            AR % (r['d'], r['repay'], r['exec'], r['profit'], r['w'], r['ty']),
            '%s / %s / %s' % (B_REPAY, B_PROFIT, B_TY))
fix('app.html', 'var tyAsset = (rows.length && assetTotal()) ? tyExec * exec / assetTotal() : 0;',
    'tyExec * exec / assetTotal()',
    'var tyAsset = (rows.length && assetTotal()) ? tyExec * ASSET_ROWS[0].amount / assetTotal() : 0;',
    B_TYA + ' — 현행은 조회기간 실행금을 분자로 써 기간에 따라 값이 요동(주간 3.20% · 월별 12.83%)', 'formula')
fix('app.html', 'var tyA = (rw.length && total) ? tyE * pexec / total : 0;', 'tyE * pexec / total',
    'var tyA = (rw.length && total) ? tyE * ASSET_ROWS[0].amount / total : 0;',
    B_TYA + ' — 엑셀 미리보기 쪽 동일 결함', 'formula')

# ── 7. xlsx 셀 ──────────────────────────────────────────────────────
def cell(fn, sheet, addr, cur, cor, b):
    FIX.append(dict(file='assets/xlsx/'+fn, kind='cell', locator='%s!%s' % (sheet, addr),
                    current=cur, corrected=cor, basis=b))
S='일별 투자수익'
for i, r in enumerate(DAILY):
    n = 4+i
    cell('일별_투자수익_20260827.xlsx', S, 'B%d'%n, r['repay0'], r['repay'], B_REPAY)
    cell('일별_투자수익_20260827.xlsx', S, 'D%d'%n, r['profit0'], r['profit'], B_PROFIT)
    cell('일별_투자수익_20260827.xlsx', S, 'F%d'%n, float(D(r['ty0'])/100), float(r['ty']/100), B_TY)
cell('일별_투자수익_20260827.xlsx', S, 'B11', 1274200000, DT['repay'], B_WAVG)
cell('일별_투자수익_20260827.xlsx', S, 'D11', 4210000, DT['profit'], B_PROFIT)
cell('일별_투자수익_20260827.xlsx', S, 'F11', 0.0358, float(DT['ty']/100), B_WAVG)
cell('일별_투자수익_20260827.xlsx', S, 'A13',
     '※ 합계행의 W금융일수·Ty수익율은 투자금액 가중평균(단순평균 아님) — 11.3일 / 3.58%.',
     '※ 합계행의 W금융일수·Ty수익율은 투자금액 가중평균(단순평균 아님) — %s일 / %s%%.' % (DT['w'], DT['ty']), B_WAVG)
S2='투자수익 현황'
cell('투자수익_현황_20260827.xlsx', S2, 'B5', 1284500000, DT['exec'], B_CARD)
cell('투자수익_현황_20260827.xlsx', S2, 'B6', 4210000, DT['profit'], B_PROFIT)
cell('투자수익_현황_20260827.xlsx', S2, 'B7', 0.0358, float(DT['ty']/100), B_WAVG)
cell('투자수익_현황_20260827.xlsx', S2, 'B8', 0.0331,
     float(r2(wavg(DAILY,'ty','exec')*D(A_EXEC)/D(A_TOT))/100), B_TYA)
cell('투자자산_현황_20260827.xlsx', '투자자산 현황', 'C4', 11.2, float(mW), B_AW)
cell('투자자산_현황_20260827.xlsx', '투자자산 현황', 'E4', 0.0359, float(mTy/100), B_AW)

DOC = dict(
  rate=0.0011,
  rate_label='0.11% (투자자 배분 요율, VAT 면제)',
  base='투자실행금 = 정산채권DB 수익권자(투자자) 양수가액. figma_policy_db.md:79 실측 1건(49,446 × 0.11% → 배분액 54) 채택',
  base_caveat='figma_policy_fee.md:121 의 지급예정액 / 매출액 / 원본 결제 대금 3갈래 상충은 미해소. 실측 1건은 양수가액 49,446 과 액면금액 49,500 을 판별하지 못한다(양쪽 다 54)',
  rounding='floor',
  rounding_label='원 단위 버림 — 확인필요',
  rounding_caveat=('실측 1건(54.3906→54)은 버림·반올림을 판별하지 못하고 올림만 배제한다. '
                   'figma_policy_fee.md:15,380,422 / 03_SETTLEMENT §4 / figma_03_어드민.md:312 모두 규칙 미정의. '
                   'payhug-admin-web 은 배분액을 백엔드 API 로 받아 프론트에 산식이 없음. '
                   'Figma 3336:116-117 "공급가액 소수점 절사" 표현을 근거로 버림 채택'),
  identities=[ '투자 수익 = 버림(투자실행금 × 0.0011)',
               '상환액 = 투자실행금 + 투자 수익',
               'Ty수익율 = 0.11% × (365 ÷ W금융일수), 소수 2자리 반올림',
               '합계행 W·Ty = 투자금액 가중평균 (행 Ty 재유도 아님 — Jensen 격차 허용)',
               '수익 현황 카드 = 표 합계와 동일',
               'Ty(투자자산 대비) = Ty(가중) × 투자실행액 ÷ 투자자산' ],
  how_to_apply=('locator 는 해당 파일에서 정확히 1회만 나타나는 문맥 문자열이며, kind="text" 인 항목은 '
                'locator 문자열 전체를 corrected 문자열로 치환한다. current 는 검토용 요약값. '
                'kind="cell" 은 xlsx 의 "시트명!셀주소" 이며 corrected 를 셀 값으로 넣는다. '
                'kind="formula" 는 app.html 의 산식 라인 교체.'),
  scope_note='요율은 C1 미확정 유지. 화면의 "예시" 표기는 그대로 둔다. 정정은 표 안 산식 정합 회복이지 정책값 확정이 아니다.',
  unresolved=[
    dict(id='U1', file='invest-assets--page2.html',
         issue='정적 2페이지의 가맹점 8건(청춘포차 신촌점 외)이 다른 어떤 근거에도 없다. 1페이지 8건이 이미 투자실행액 1,284,500,000 = 비중 100.0% 를 소진하는데 2페이지도 같은 분모로 비중을 계산해 두어 합계가 118.6% 가 된다. app.html 은 MERCHANTS 8건 · PAGE_SIZE 5 라 2페이지가 6~8번 가맹점이며 구성 자체가 다르다.',
         blocked_on='가맹점 로스터를 8건으로 볼지 16건으로 볼지 결정. 16건이면 투자실행액 1,523,100,000 · 투자자산 1,628,400,000 으로 바뀌고 비중·W·S·Ty·투자자산대비수익율 전건 재산출 대상.',
         note='요율 배분과 무관한 데이터 설계 결정이라 값을 산출하지 않는다. 요율과 무관하게 성립하는 Ty 5건만 fixes 에 포함.'),
    dict(id='U2', file='invest-profit.html · invest-assets.html',
         issue='일평균 투자실행금 약 178,690,000 × W금융일수 11.29일 = 약 2,018,000,000 이 잔액이어야 하나 투자실행액은 1,284,500,000 (약 1.57배 차).',
         blocked_on='예시 데이터 생성 규칙 자체의 개연성 문제.',
         note='요율과 무관. 이번 라운드에서 손대지 않음.'),
    dict(id='U3', file='invest-profit.html · invest-assets.html (문구)',
         issue='합계행 주석이 정적 파일은 "(평균)", app.html 은 "(가중평균)". invest-profit.html 합계 Ty 에는 주석이 없고 --monthly 에는 있음. invest-assets 카드 부제 "W금융일수 11.3일 기준" 은 유도 관계를 시사하나 카드 Ty 3.58% 는 가중평균이라 11.3 에서 역산한 3.55% 와 0.03%p 어긋난다(Jensen 격차).',
         blocked_on='문구 결정.',
         note='숫자가 아니라 문구라 fixes 에서 제외.')],
  no_change=['certificate.html','invest-assets--empty.html','invest-profit--empty.html','glossary.html',
             'merchants*.html','acquisition*.html','contracts*.html','coocon*.html','index.html',
             'xls-assets-merchant.html','assets/xlsx/가맹점별_투자자산_20260827.xlsx'],
  fixes=FIX)
io.open(OUT,'w',encoding='utf-8').write(json.dumps(DOC, ensure_ascii=False, indent=2, default=str))
print('fixes: %d (text %d / cell %d / formula %d)' % (len(FIX),
      sum(1 for x in FIX if x['kind']=='text'), sum(1 for x in FIX if x['kind']=='cell'),
      sum(1 for x in FIX if x['kind']=='formula')))
files = sorted(set(x['file'] for x in FIX)); print('files: %d' % len(files))
for x in files: print('  -', x, sum(1 for y in FIX if y['file']==x))
print('locator 검증 오류: %d' % len(ERR))
for e in ERR: print('  !!', e)
