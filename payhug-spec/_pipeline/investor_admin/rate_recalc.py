# -*- coding: utf-8 -*-
"""
투자자 어드민 요율 배분 재계산 — 검산 스크립트 (읽기 전용, 파일 수정 없음)
채택: r = 0.11% / base = 투자실행금(양수가액) / 원단위 버림(floor)
근거: payhug-spec/analysis/figma_policy_db.md:79 (양수가액 49,446 · 0.11% · 배분액 54)
"""
from decimal import Decimal as D, ROUND_HALF_UP, ROUND_FLOOR

R = D('0.0011')            # 투자자 배분 요율 0.11%
RPCT = D('0.11')           # 퍼센트 표기용
DAYS = D('365')
ASSET_EXEC = 1284500000    # 투자자산 > 투자실행액
ASSET_CASH = 105300000     # 순현금
ASSET_TOTAL = ASSET_EXEC + ASSET_CASH   # 1,389,800,000

def floor0(x):   return int(D(x).quantize(D('1'), rounding=ROUND_FLOOR))
def r2(x):       return D(x).quantize(D('0.01'), rounding=ROUND_HALF_UP)
def r1(x):       return D(x).quantize(D('0.1'),  rounding=ROUND_HALF_UP)
def ty(w):       return r2(RPCT * DAYS / D(str(w)))          # Ty수익율 = 할인율 × 365/W
def profit(exec_): return floor0(D(exec_) * R)               # 배분액 = 양수가액 × 0.11%, 버림
def wavg(rows, k, wk):
    n = sum(D(str(r[k])) * D(str(r[wk])) for r in rows)
    d = sum(D(str(r[wk])) for r in rows)
    return n / d if d else D(0)
def f(n): return format(n, ',')

log = []
def P(s=''): log.append(s); print(s)

# ══ §0 기준 실측 검산 ═══════════════════════════════════════════════
P('== §0 기준 실측 (figma_policy_db.md:79) ==')
for base, label in ((49446, '양수가액'), (49500, '액면금액')):
    raw = D(base) * R
    P('  %s %s x 0.11%% = %s -> floor %d / round %d / ceil %d  (실측 배분액 54)'
      % (label, f(base), raw, floor0(raw),
         int(raw.quantize(D('1'), rounding=ROUND_HALF_UP)), -floor0(-raw)))
P('  -> floor·round 모두 54 성립, ceil 배제. 기준금액 2안 모두 54 -> 이 1건으로는 미판별')
P()

# ══ §1 일별 투자수익 (7행) ══════════════════════════════════════════
DAILY_IN = [
 ('2026-08-21', 182300000, 178900000, 601000, '11.4', '3.55'),
 ('2026-08-22', 175800000, 172600000, 578000, '11.1', '3.61'),
 ('2026-08-23', 168400000, 165300000, 552000, '10.9', '3.58'),
 ('2026-08-24', 191200000, 187700000, 634000, '11.6', '3.52'),
 ('2026-08-25', 186500000, 183100000, 617000, '11.3', '3.57'),
 ('2026-08-26', 179900000, 176600000, 596000, '11.2', '3.59'),
 ('2026-08-27', 190100000, 186600000, 632000, '11.5', '3.54'),
]
P('== §1 일별 투자수익 — 행별 재계산 (기준: 투자실행금 고정) ==')
P('  날짜 | 실행금(고정) | 수익 현행->정정 | 실효율 현행 | 상환액 현행->정정 | W | Ty 현행->정정')
DAILY = []
for d, repay0, exec_, pr0, w, ty0 in DAILY_IN:
    pr = profit(exec_)
    repay = exec_ + pr
    t = ty(w)
    eff = (D(pr0) / D(exec_) * 100).quantize(D('0.0001'))
    P('  %s | %s | %s -> %s | %s%% | %s -> %s | %s | %s%% -> %s%%'
      % (d, f(exec_), f(pr0), f(pr), eff, f(repay0), f(repay), w, ty0, t))
    DAILY.append(dict(d=d, repay=repay, exec=exec_, profit=pr, w=D(w), ty=t,
                      repay0=repay0, profit0=pr0, ty0=D(ty0)))
dex = sum(r['exec'] for r in DAILY); dpr = sum(r['profit'] for r in DAILY); drp = sum(r['repay'] for r in DAILY)
dW = wavg(DAILY, 'w', 'exec'); dTy = wavg(DAILY, 'ty', 'exec')
P('  합계 상환액 1,274,200,000 -> %s' % f(drp))
P('  합계 실행금 1,250,800,000 -> %s (불변)' % f(dex))
P('  합계 수익   4,210,000 -> %s' % f(dpr))
P('  합계 W(가중) 11.3 -> %s   [raw %s]' % (r1(dW), dW.quantize(D('0.0001'))))
P('  합계 Ty(가중) 3.58%% -> %s%%  [raw %s]' % (r2(dTy), dTy.quantize(D('0.000001'))))
P('  검산: 합계수익/합계실행금 = %s%%' % (D(dpr)/D(dex)*100).quantize(D('0.000001')))
P()

# ══ §2 주간 수익 현황 카드 ══════════════════════════════════════════
P('== §2 수익 현황 카드 (일주일 2026-08-21~27) ==')
tyE = r2(dTy)
tyA_new = r2(dTy * D(ASSET_EXEC) / D(ASSET_TOTAL))
tyA_appbug = r2(dTy * D(dex) / D(ASSET_TOTAL))
P('  투자실행금 1,284,500,000 -> %s   (표 합계와 일치시킴)' % f(dex))
P('  투자수익   4,210,000 -> %s' % f(dpr))
P('  Ty 실행금대비 3.58%% -> %s%%' % tyE)
P('  Ty 자산대비  3.31%% -> %s%%   [= Ty(가중) x 투자실행액 1,284,500,000 / 투자자산 1,389,800,000]' % tyA_new)
P('  (참고) app.html 현행 산식 tyExec x 기간실행금/투자자산 = %s%% — 기간 의존 결함' % tyA_appbug)
P()

# ══ §3 월별 투자수익 (6행) ══════════════════════════════════════════
MON_IN = [
 ('2026-03', 5124600000, 5031200000, 16980000, '11.4', '3.51'),
 ('2026-04', 5387900000, 5289400000, 17920000, '11.2', '3.56'),
 ('2026-05', 5642300000, 5538700000, 18730000, '11.0', '3.62'),
 ('2026-06', 5478100000, 5376500000, 18140000, '11.6', '3.48'),
 ('2026-07', 5861400000, 5752800000, 19480000, '11.3', '3.60'),
 ('2026-08', 5203700000, 5108900000, 17260000, '11.5', '3.55'),
]
P('== §3 월별 투자수익 — 행별 재계산 ==')
MON = []
for d, repay0, exec_, pr0, w, ty0 in MON_IN:
    pr = profit(exec_); repay = exec_ + pr; t = ty(w)
    eff = (D(pr0)/D(exec_)*100).quantize(D('0.0001'))
    P('  %s | %s | %s -> %s | %s%% | %s -> %s | %s | %s%% -> %s%%'
      % (d, f(exec_), f(pr0), f(pr), eff, f(repay0), f(repay), w, ty0, t))
    MON.append(dict(d=d, repay=repay, exec=exec_, profit=pr, w=D(w), ty=t))
mex=sum(r['exec'] for r in MON); mpr=sum(r['profit'] for r in MON); mrp=sum(r['repay'] for r in MON)
mW=wavg(MON,'w','exec'); mTy=wavg(MON,'ty','exec')
P('  합계 상환액 32,698,000,000 -> %s' % f(mrp))
P('  합계 실행금 32,097,500,000 -> %s' % f(mex))
P('  합계 수익   108,510,000 -> %s' % f(mpr))
P('  합계 W(가중) 11.3 -> %s  [raw %s]' % (r1(mW), mW.quantize(D('0.0001'))))
P('  합계 Ty(가중) 3.55%% -> %s%%  [raw %s]' % (r2(mTy), mTy.quantize(D('0.000001'))))
aug = MON[-1]
P('  -- 월별 화면 카드(이번달=2026-08 1건) --')
P('     투자실행금 1,284,500,000 -> %s' % f(aug['exec']))
P('     투자수익   17,260,000 -> %s' % f(aug['profit']))
P('     Ty 실행금대비 3.55%% -> %s%%' % aug['ty'])
P('     Ty 자산대비  3.28%% -> %s%%' % r2(aug['ty']*D(ASSET_EXEC)/D(ASSET_TOTAL)))
P()

# ══ §4 가맹점별 투자자산 (8행) ══════════════════════════════════════
MER_IN = [
 ('김성호떡볶이 본점', 312400000, '10.8', '0.31', '3.72', '24.3'),
 ('달빛곱창 홍대점',   268900000, '11.5', '0.55', '3.49', '20.9'),
 ('성호분식 2호점',    197300000, '12.1', '0.28', '3.32', '15.4'),
 ('바다마루 횟집',     152600000, '10.2', '0.47', '3.94', '11.9'),
 ('한강커피 잠원점',   121800000, '11.9', '0.62', '3.37', '9.5'),
 ('김밥나라',          98200000,  '10.5', '0.19', '3.82', '7.6'),
 ('초록치킨 서초점',   76100000,  '12.4', '0.71', '3.24', '5.9'),
 ('골목냉면',          57200000,  '11.0', '0.38', '3.65', '4.5'),
]
P('== §4 가맹점별 투자자산 — Ty·비중 검산 ==')
MER=[]
for n, amt, w, s, ty0, sh0 in MER_IN:
    t=ty(w); sh=r1(D(amt)/D(ASSET_EXEC)*100)
    P('  %-16s %s | W %s | Ty %s%% -> %s%% %s | 비중 %s%% -> %s%% %s'
      % (n, f(amt), w, ty0, t, 'OK' if D(ty0)==t else '<<FIX', sh0, sh, 'OK' if D(sh0)==sh else '<<FIX'))
    MER.append(dict(n=n, amount=amt, w=D(w), s=D(s), ty=t))
msum=sum(r['amount'] for r in MER)
mwW=wavg(MER,'w','amount'); mwS=wavg(MER,'s','amount'); mwTy=wavg(MER,'ty','amount')
P('  합계 투자금액 %s  (투자실행액 %s 와 %s)' % (f(msum), f(ASSET_EXEC), '일치' if msum==ASSET_EXEC else '불일치'))
P('  가중 W  = %s -> %s   (현황표 투자실행액 행 현행 11.2)' % (mwW.quantize(D('0.0001')), r1(mwW)))
P('  가중 S  = %s -> %s%%  (현행 0.42%% — 일치 => 가중평균이 채택 규칙임을 입증)' % (mwS.quantize(D('0.0001')), r2(mwS)))
P('  가중 Ty = %s -> %s%%  (현행 3.59%%)' % (mwTy.quantize(D('0.000001')), r2(mwTy)))
P('  참고: 0.11%% x 365 / %s = %s%%  (가중 W에서 역산 — 가중Ty와 %s 차이, Jensen 격차)'
  % (r1(mwW), ty(r1(mwW)), abs(r2(mwTy)-ty(r1(mwW)))))
P()
P('== §5 투자자산 현황표 ==')
P('  투자실행액 %s | 비중 %s%% | W 11.2 -> %s | S 0.42%% -> %s%% | Ty 3.59%% -> %s%%'
  % (f(ASSET_EXEC), r1(D(ASSET_EXEC)/D(ASSET_TOTAL)*100), r1(mwW), r2(mwS), r2(mwTy)))
P('  순현금     %s | 비중 %s%%' % (f(ASSET_CASH), r1(D(ASSET_CASH)/D(ASSET_TOTAL)*100)))
P('  합계       %s | 100.0%%' % f(ASSET_TOTAL))
P()

# ══ §6 page2 유령 가맹점 ════════════════════════════════════════════
P2 = [('청춘포차 신촌점',48900000,'11.3','0.44','3.51','3.8'),
      ('왕십리곱창타운',42300000,'10.6','0.26','3.78','3.3'),
      ('소소한밥상',37600000,'12.2','0.58','3.29','2.9'),
      ('대박국수 사당점',31400000,'11.7','0.33','3.42','2.4'),
      ('정든수산',26800000,'10.9','0.51','3.68','2.1'),
      ('착한고기 은평점',21500000,'12.6','0.67','3.21','1.7'),
      ('커피한잔 마포점',17200000,'11.1','0.22','3.74','1.3'),
      ('우리동네반찬',12900000,'10.4','0.35','3.86','1.0')]
P('== §6 invest-assets--page2.html (정적 전용 8행) ==')
tot2=sum(r[1] for r in P2)
for n,amt,w,s,ty0,sh0 in P2:
    t=ty(w)
    P('  %-14s %s | W %s | Ty %s%% -> %s%% %s | 비중(현행 %s%%, 기준 1,284,500,000)'
      % (n,f(amt),w,ty0,t,'OK' if D(ty0)==t else '<<FIX',sh0))
P('  page2 합계 %s. page1 8행이 이미 1,284,500,000(=100%%)을 소진 -> 비중 총합 %s%%'
  % (f(tot2), r1(D(ASSET_EXEC+tot2)/D(ASSET_EXEC)*100)))
P('  app.html 은 PAGE_SIZE=5·가맹점 8건 -> page2 = 6~8번 가맹점. 정적 page2 의 8건은 어디에도 없음.')
open('/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/rate_recalc.log','w',encoding='utf-8').write('\n'.join(log))
