# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, '/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin')
import daily_ledger as L
from datetime import date, timedelta
from decimal import Decimal as D

R = L.RECEIVABLES
ASOF = L.ASOF; CASH = L.CASH
P0 = date.fromisoformat(L.WEEK[0]); P1 = date.fromisoformat(L.WEEK[1])
days = [P0 + timedelta(days=k) for k in range((P1-P0).days+1)]
f = lambda n: format(int(n), ',')

print('ASOF', ASOF, 'CASH', f(CASH), 'WEEK', L.WEEK, 'days', len(days))
print('receivables', f(len(R)), 'open@ASOF', f(len(L.OPEN)), 'EXEC', f(L.EXEC))

# ── ④⑤ 현행 (원장 facts 그대로) ──
F = L.facts()
print('\n[현행 facts] weekExec(PA)=%s weekProfit(PM)=%s weekPsc(PEC)=%s weekWRaw(PD)=%s weekTyRaw(PY_a)=%s weekTyAssetRaw(PY_t)=%s'
      % (f(F['weekExec']), f(F['weekProfit']), f(F['weekPsc']), F['weekWRaw'], F['weekTyRaw'], F['weekTyAssetRaw']))
PA = D(F['weekExec']); PM = D(F['weekProfit']); PEC = D(F['weekPsc']); PD = D(F['weekWRaw']); PYa = D(F['weekTyRaw'])
print('현행 비중 PA/(PA+PEC) = %s' % (PA/(PA+PEC)))

# ── 정산예정일 ∈ P 채권의 원·일 Σ(Ai×Di) ──
inP = [r for r in R if P0 <= r['due'] <= P1]
AD_P = sum(r['ai']*r['di'] for r in inP)
print('\nΣ_{i∈P} Ai = %s (건 %s) · Σ_{i∈P} Ai×Di = %s · PA×PD(6자리) = %s'
      % (f(sum(r['ai'] for r in inP)), f(len(inP)), f(AD_P), f(PA*PD)))

# ── 하루(08-26) ──
d = P1
PA_day = sum(r['ai'] for r in R if r['due']==d)
stock_strict = sum(r['ai'] for r in R if r['adv']<=d and r['due']>d)     # adv≤d, due>d
stock_loose  = sum(r['ai'] for r in R if r['due']>d)                      # due>d 만
print('\n[08-26] PA 하루치 = %s' % f(PA_day))
print('  잔액 ΣAi (adv≤d, due>d) = %s' % f(stock_strict))
print('  잔액 ΣAi (due>d 만)     = %s' % f(stock_loose))

# EC 역산 후보들 — 어느 규약이 18,855,391 을 내는지
def adv_sum(a,b): return sum(r['ai'] for r in R if a<=r['adv']<=b)
def net_sum(a,b): return sum(r['net'] for r in R if a<=r['due']<=b)
def rep_sum(a,b): return sum(r['net']-r['ded'] for r in R if a<=r['due']<=b)
cands = {
 'CASH + adv(08-27) - repay(08-27)':        CASH + adv_sum(date(2026,8,27),date(2026,8,27)) - rep_sum(date(2026,8,27),date(2026,8,27)),
 'CASH + adv(08-27) - net(08-27)':          CASH + adv_sum(date(2026,8,27),date(2026,8,27)) - net_sum(date(2026,8,27),date(2026,8,27)),
 'CASH + adv(08-27)':                       CASH + adv_sum(date(2026,8,27),date(2026,8,27)),
 'CASH - repay(08-27)':                     CASH - rep_sum(date(2026,8,27),date(2026,8,27)),
 'CASH + adv(08-27) - repay(08-26)':        CASH + adv_sum(date(2026,8,27),date(2026,8,27)) - rep_sum(date(2026,8,26),date(2026,8,26)),
 '100M - stock_strict':                     100000000 - stock_strict,
 '100M - stock_loose':                      100000000 - stock_loose,
 'CASH + (stock@ASOF - stock_strict)':      CASH + (L.EXEC - stock_strict),
}
print('  EC 역산 후보:')
for k,v in cands.items(): print('    %-40s %s' % (k, f(v)))

# ── 7일 잔액 합 · 비중 ──
def stock(dd): return sum(r['ai'] for r in R if r['adv']<=dd and r['due']>dd)
def stock2(dd): return sum(r['ai'] for r in R if r['due']>dd)
S_strict = sum(stock(dd) for dd in days)
S_loose  = sum(stock2(dd) for dd in days)
print('\n[7일] Σ_d 잔액(adv≤d,due>d) = %s · Σ_d 잔액(due>d) = %s · Σ_{i∈P}AiDi = %s' % (f(S_strict), f(S_loose), f(AD_P)))
print('  Σ_d 잔액 / PA = %s (PD %s)' % (D(S_strict)/PA, PD))
print('  비중 EC 상수 20M: 잔액합/(잔액합+PEC) = %s' % (D(S_strict)/(D(S_strict)+PEC)))
# EC 역산 = CASH + (EXEC - stock_d)  (총자산 흐름 보존 가정)  및 후보 1
for name, ecf in [('EC=CASH+(EXEC-stock_d)', lambda dd: CASH + (L.EXEC - stock(dd))),
                  ('EC=CASH+adv(d+1..ASOF)-repay(d+1..ASOF)', lambda dd: CASH + adv_sum(dd+timedelta(1),ASOF) - rep_sum(dd+timedelta(1),ASOF)),
                  ('EC=CASH+adv(d+1..ASOF)-net(d+1..ASOF)', lambda dd: CASH + adv_sum(dd+timedelta(1),ASOF) - net_sum(dd+timedelta(1),ASOF))]:
    ecs = [ecf(dd) for dd in days]
    tot = sum(stock(dd)+e for dd,e in zip(days,ecs))
    print('  비중 %s: %s · EC(08-26)=%s · Σ_d EC=%s · 투자자산(08-26)=%s'
          % (name, D(S_strict)/D(tot), f(ecs[-1]), f(sum(ecs)), f(stock(P1)+ecs[-1])))

# ── 결론 3 vs 기존 기호만 쓰는 대안 ──
share_AD = (PA*PD)/(PA*PD+PEC)
share_AD_exact = D(AD_P)/(D(AD_P)+PEC)
print('\n[대안] PA×PD/(PA×PD+PEC) = %s · Σ AiDi 정확값 사용 = %s' % (share_AD, share_AD_exact))
print('  ⑤ 현행            = PY_a × PA/(PA+PEC)          = %s' % (PYa*PA/(PA+PEC)))
print('  ⑤ 결론3(EC상수)   = PY_a × 잔액합/(잔액합+PEC)  = %s' % (PYa*D(S_strict)/(D(S_strict)+PEC)))
print('  ⑤ 대안(PA×PD)     = PY_a × PA·PD/(PA·PD+PEC)    = %s' % (PYa*share_AD))
print('  ⑤ 대안 = PM×365/(ΣAiDi+PEC)                     = %s' % (PM*365/(D(AD_P)+PEC)*100))
print('  ⑤ 직접 = PM×365/Σ_d(잔액_d+EC_d) (EC상수)        = %s' % (PM*365/(D(S_strict)+PEC)*100))
print('  ④ 검산 PM×365/ΣAiDi                             = %s (facts %s)' % (PM*365/D(AD_P)*100, PYa))

# ── 08-26 하루 P=1 로 본 비중 ──
print('\n[P=1일 08-26] 현행 PA_day/(PA_day+EC) = %s · 잔액/(잔액+EC) = %s · PA_day×PD_day 근사'
      % (D(PA_day)/(D(PA_day)+D(CASH)), D(stock_strict)/(D(stock_strict)+D(CASH))))
row = [x for x in L.LEDGER if x['d']=='2026-08-26'][0]
print('  원장 행 08-26: exec %s profit %s w6 %s wx %s' % (f(row['exec']), f(row['profit']), row['w6'], f(row['wx'])))
print('  wx/(wx+EC) = %s' % (D(row['wx'])/(D(row['wx'])+D(CASH))))

# ── 창 경계 효과: Σ_{i∈P}AiDi 와 Σ_d 잔액_d 의 차이 분해 ──
# 잔액합에는 P 밖(뒤)에 정산되는 채권의 P 안 일수가 들어가고, AiDi 합에는 P 앞의 일수가 들어간다
before = sum(r['ai']*max(0,(P0 - r['adv']).days) for r in inP)   # P 시작 전 일수
after  = sum(r['ai']*max(0,(min(r['due'],ASOF+timedelta(30)) - P1 - timedelta(1)).days + 0) for r in R if r['adv']<=P1 and r['due']>P1)
print('\n[경계] i∈P 채권의 P 이전 원·일 = %s' % f(before))
print('  Σ_{i∈P}AiDi − Σ_d잔액 = %s' % f(AD_P - S_strict))
