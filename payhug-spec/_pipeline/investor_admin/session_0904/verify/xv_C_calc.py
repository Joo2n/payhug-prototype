import sys, datetime as dt
from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict
sys.path.insert(0, '/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin')
import daily_ledger as L

D = dt.date
R = L.RECEIVABLES
ASOF = L.ASOF
CASH = L.CASH
F = L.facts()
P0, P1 = D(2026, 8, 20), D(2026, 8, 26)

def q6(x): return Decimal(x).quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)
def q2(x): return Decimal(x).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
def q4(x): return Decimal(x).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)

print('== facts ==')
for k in ['weekTyRaw', 'weekTyAssetRaw', 'weekExec', 'weekProfit', 'weekPsc']:
    print(f'{k} = {F[k]}')
print(f'ASOF = {ASOF}  CASH = {CASH}  WEEK = {L.WEEK}  n_receivables = {len(R)}')

# 날짜별 집계 (전 기간)
adv_min = min(r['adv'] for r in R)
due_max = max(r['due'] for r in R)
days_all = [adv_min + dt.timedelta(i) for i in range((due_max - adv_min).days + 1)]

PA1 = defaultdict(int); OUT = defaultdict(int); IN = defaultdict(int); AIDI = defaultdict(int)
for r in R:
    PA1[r['due']] += r['ai']
    OUT[r['adv']] += r['ai']
    IN[r['due']] += r['net'] - r['ded']
    AIDI[r['due']] += r['ai'] * r['di']

def SA(d, adv_strict=False, due_incl=False):
    s = 0
    for r in R:
        a = (r['adv'] < d) if adv_strict else (r['adv'] <= d)
        b = (r['due'] >= d) if due_incl else (r['due'] > d)
        if a and b: s += r['ai']
    return s

# EC 역산: EC(ASOF)=CASH, EC(d-1) = EC(d) - IN(d) + OUT(d)
EC = {ASOF: CASH}
d = ASOF
while d > adv_min:
    EC[d - dt.timedelta(1)] = EC[d] - IN[d] + OUT[d]
    d -= dt.timedelta(1)

print('\n== 표1 날짜별 08-20~08-27 ==')
print('| d | SA(d) | PA1(d) | OUT(d) | IN(d) | EC(d) | SA+EC |')
print('|---|---:|---:|---:|---:|---:|---:|')
SAc = {}
for i in range(8):
    d = P0 + dt.timedelta(i)
    SAc[d] = SA(d)
    print(f'| {d} | {SAc[d]:,} | {PA1[d]:,} | {OUT[d]:,} | {IN[d]:,} | {EC[d]:,} | {SAc[d]+EC[d]:,} |')

print('\n== 표2 검산 ==')
sa27 = SAc[ASOF]
sumPA1 = sum(PA1[P0 + dt.timedelta(i)] for i in range(7))
print(f'SA(08-27) = {sa27:,}  ; == 80,000,000 ? {sa27 == 80_000_000}')
print(f'facts weekExec = {F["weekExec"]:,} ; Σ PA1(P) = {sumPA1:,} ; == ? {F["weekExec"] == sumPA1}')

print('\n== 표3 7일 합 ==')
sumSA = sum(SAc[P0 + dt.timedelta(i)] for i in range(7))
sumEC = sum(EC[P0 + dt.timedelta(i)] for i in range(7))
sumAIDI = sum(AIDI[P0 + dt.timedelta(i)] for i in range(7))
c7 = 7 * CASH
print(f'Σ PA1 = {sumPA1:,}')
print(f'Σ SA = {sumSA:,}')
print(f'Σ EC(역산) = {sumEC:,}')
print(f'7×CASH = {c7:,}')
print(f'Σ(ai×di) = {sumAIDI:,}')

print('\n== 표4 비중과 ⑤ ==')
ty4 = Decimal(F['weekTyRaw'])
def ratio(n, dnm): return Decimal(n) / Decimal(n + dnm)
rows = [
    ('가', 'ΣPA1 ÷ (ΣPA1 + 7×CASH)', ratio(sumPA1, c7)),
    ('나', 'ΣPA1 ÷ (ΣPA1 + ΣEC역산)', ratio(sumPA1, sumEC)),
    ('다', 'ΣSA ÷ (ΣSA + 7×CASH)', ratio(sumSA, c7)),
    ('라', 'ΣSA ÷ (ΣSA + ΣEC역산)', ratio(sumSA, sumEC)),
    ('마', 'Σ(ai×di) ÷ (Σ(ai×di) + 7×CASH)', ratio(sumAIDI, c7)),
]
print(f'④ weekTyRaw = {ty4}')
print('| 안 | 식 | 비중(6자리) | ⑤ 6자리 = q6(④×비중) | ⑤ 2자리 |')
print('|---|---|---:|---:|---:|')
for k, f, rt in rows:
    v6 = q6(ty4 * rt)
    print(f'| ({k}) | {f} | {q6(rt)} | {v6} | {q2(v6)} |')
v6ga = q6(ty4 * ratio(sumPA1, c7))
print(f'(가) ⑤ 6자리 {v6ga} vs facts weekTyAssetRaw {F["weekTyAssetRaw"]} : == ? {str(v6ga) == F["weekTyAssetRaw"]}')

print('\n== 표5 기간 길이별 (가)·(라), 끝날 08-26 고정 ==')
print('| n일 | 시작일 | ΣPA1 | n×CASH | ΣSA | ΣEC | (가) | (라) | ⑤(가) | ⑤(라) |')
print('|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|')
SA_cache = dict(SAc)
for n in [1, 7, 26, 90, 179]:
    start = P1 - dt.timedelta(n - 1)
    days = [start + dt.timedelta(i) for i in range(n)]
    for d in days:
        if d not in SA_cache: SA_cache[d] = SA(d)
    sPA1 = sum(PA1[d] for d in days)
    sSA = sum(SA_cache[d] for d in days)
    sEC = sum(EC[d] for d in days)
    ga = ratio(sPA1, n * CASH); ra = ratio(sSA, sEC)
    print(f'| {n} | {start} | {sPA1:,} | {n*CASH:,} | {sSA:,} | {sEC:,} | {q6(ga)} | {q6(ra)} | {q2(q6(ty4*ga))} | {q2(q6(ty4*ra))} |')

print('\n== 표6 경계 규약 민감도 (7일, (라)) ==')
print('| 규약 | ΣSA | ΣEC | (라) 6자리 | ⑤ 2자리 | 기준(라) 대비 차 |')
print('|---|---:|---:|---:|---:|---:|')
base = ratio(sumSA, sumEC)
variants = [
    ('adv ≤ d, due > d (기준)', False, False),
    ('adv < d, due > d', True, False),
    ('adv ≤ d, due ≥ d', False, True),
]
for name, a, b in variants:
    s = sum(SA(P0 + dt.timedelta(i), a, b) for i in range(7))
    rt = ratio(s, sumEC)
    print(f'| {name} | {s:,} | {sumEC:,} | {q6(rt)} | {q2(q6(ty4*rt))} | {q6(rt - base):+} |')

