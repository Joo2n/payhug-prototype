# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, '/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin')
from decimal import Decimal as D, getcontext
# 기본 정밀도 28 유지 — 원장 platform_duration 의 구성비 합 == 1 검사가 28자리에 맞춰져 있다
from datetime import date, timedelta
import daily_ledger as L

R = L.RECEIVABLES
ASOF = L.ASOF
P0, P1 = date.fromisoformat(L.WEEK[0]), date.fromisoformat(L.WEEK[1])
days = [P0 + timedelta(days=k) for k in range((P1 - P0).days + 1)]
f = lambda n: format(int(n), ',')
pct = lambda x: '%.6f%%' % x

def SA(d):   return sum(r['ai'] for r in R if r['adv'] <= d < r['due'])
def PA1(d):  return sum(r['ai'] for r in R if r['due'] == d)
def cnt_SA(d): return sum(1 for r in R if r['adv'] <= d < r['due'])
def cnt_PA1(d): return sum(1 for r in R if r['due'] == d)

print('== 원장 상수 ==')
print('ASOF %s  WEEK %s ~ %s (%d일)  CASH %s  BOOK %s' % (ASOF, P0, P1, len(days), f(L.CASH), f(L.BOOK)))
print('채권 %s건 · 선정산일 %s ~ %s · 미회수(due > ASOF) %s건 Σai %s' % (f(len(R)), L.ADV_DAYS[0], L.ADV_DAYS[-1], f(len(L.OPEN)), f(L.EXEC)))
print()

print('== 2번: 08-26 하루 — SA(d) vs PA1(d) ==')
d26 = date(2026, 8, 26)
sa26, pa26 = SA(d26), PA1(d26)
print('SA(08-26)  = Σai, adv<=d<due  : %s원  (%s건)' % (f(sa26), f(cnt_SA(d26))))
print('PA1(08-26) = Σai, due==d      : %s원  (%s건)' % (f(pa26), f(cnt_PA1(d26))))
print('SA/PA1 = %.6f  (기간 PD 3.093802 · 전체 D %s 와 견줌)' % (D(sa26)/D(pa26), L.W6))
print('SA(08-27) = %s  (투자자산 화면 Σ A_i · due>ASOF 와 같은가: %s)' % (f(SA(ASOF)), SA(ASOF) == L.EXEC))
print('PA1(08-27) = %s' % f(PA1(ASOF)))
print()

# ── 기간 집계 (원장 facts 와 같은 경로) ──
wk = [r for r in L.LEDGER if L.WEEK[0] <= r['d'] <= L.WEEK[1]]
PA  = sum(r['exec'] for r in wk)
PM  = sum(r['profit'] for r in wk)
WX  = sum(r['wx'] for r in wk)              # Σ A_i × D_i, i∈P  (= PA × PD, 끊지 않은 값)
PD6 = L.r6(D(WX) / D(PA))
PMR6 = L.r6(D(PM) / D(PA) * 100)
PYa6 = L.r6(PMR6 * L.DAYS / PD6)
print('== 기간 P 집계 (08-20~08-26) ==')
print('PA  = %s  PM = %s  Σ(Ai×Di) = %s 원·일  PD = %s  PMR = %s%%  PY_a = %s%%' % (f(PA), f(PM), f(WX), PD6, PMR6, PYa6))
# 정확 적분 스톡
SAsum = sum(SA(t) for t in days)
print('Σ_{t∈P} SA(t) = %s 원·일  (일평균 %s)' % (f(SAsum), f(D(SAsum)/len(days))))
print('PA × PD       = %s 원·일  (일평균 %s)  차이 %s (%.4f%%)' % (f(WX), f(D(WX)/len(days)), f(WX - SAsum), (D(WX)-D(SAsum))/D(SAsum)*100))
for t in days:
    print('   %s  SA(t)=%s  PA1(t)=%s' % (t, f(SA(t)), f(PA1(t))))
print()

# ── EC 두 가지 ──
def ec_series_const():
    return {t: D(L.CASH) for t in days}

def ec_series_backcast():
    # 앵커 EC(08-27 마감) = CASH.  EC(d-1) = EC(d) − Σ_{due=d}(net−ded) + Σ_{adv=d} ai
    ec = {ASOF: D(L.CASH)}
    d = ASOF
    while d > P0:
        inflow  = sum(r['net'] - r['ded'] for r in R if r['due'] == d)
        outflow = sum(r['ai'] for r in R if r['adv'] == d)
        ec[d - timedelta(days=1)] = ec[d] - inflow + outflow
        d -= timedelta(days=1)
    return ec

def five(label, ec):
    PEC = sum(ec[t] for t in days)
    cur_share = D(PA) / (D(PA) + PEC)
    cur5 = L.r6(L.ty_asset(PYa6, D(PA), PEC))
    new_share = D(WX) / (D(WX) + PEC)
    new5 = L.r6(PYa6 * new_share)
    ex_share = D(SAsum) / (D(SAsum) + PEC)
    ex5 = L.r6(PYa6 * ex_share)
    print('-- %s --' % label)
    for t in days: print('   EC(%s) = %s' % (t, f(ec[t])))
    print('   PEC = %s 원·일  (일평균 %s)' % (f(PEC), f(PEC/len(days))))
    print('   현행 ⑤  분모 PA+PEC = %s   비중 PA/(PA+PEC) = %.6f   PY_t = %s%%' % (f(D(PA)+PEC), cur_share, cur5))
    print('   3번 꼴  분모 PA×PD+PEC = %s 원·일   비중 = %.6f   PY_t = %s%%' % (f(D(WX)+PEC), new_share, new5))
    print('   3번 정확 분모 ΣSA(t)+PEC = %s 원·일   비중 = %.6f   PY_t = %s%%' % (f(D(SAsum)+PEC), ex_share, ex5))
    print('   검산 PM×365÷(PA×PD+PEC) = %s%%' % L.r6(D(PM)*100*365/(D(WX)+PEC)))
    print('   현행 = 3번 꼴 이 되는 조건 PD = 1 ; 현행 비중 ÷ 3번 비중 = %.6f' % (cur_share/new_share))

print('== 5번 ==')
five('(a) 순현금 상수 20,000,000', ec_series_const())
ecb = ec_series_backcast()
five('(b) 08-27 마감 20,000,000 앵커 역산', ecb)
