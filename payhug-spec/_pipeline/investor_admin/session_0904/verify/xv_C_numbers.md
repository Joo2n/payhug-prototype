# xv_C 독립 계산 — 원장 `daily_ledger.py` 기준 (P = 2026-08-20 ~ 08-26, ASOF 08-27, CASH 20,000,000)

## 산출 표 (스크립트 출력 원문)

```
== facts ==
weekTyRaw = 4.129577
weekTyAssetRaw = 2.322416
weekExec = 179916643
weekProfit = 62977
weekPsc = 140000000
ASOF = 2026-08-27  CASH = 20000000  WEEK = ('2026-08-20', '2026-08-26')  n_receivables = 61760

== 표1 날짜별 08-20~08-27 ==
| d | SA(d) | PA1(d) | OUT(d) | IN(d) | EC(d) | SA+EC |
|---|---:|---:|---:|---:|---:|---:|
| 2026-08-20 | 79,652,915 | 26,467,707 | 25,978,279 | 26,478,274 | 20,285,893 | 99,938,808 |
| 2026-08-21 | 79,187,438 | 25,941,773 | 25,476,296 | 25,951,644 | 20,761,241 | 99,948,679 |
| 2026-08-22 | 80,161,902 | 25,366,208 | 26,340,672 | 25,375,330 | 19,795,899 | 99,957,801 |
| 2026-08-23 | 81,055,996 | 25,179,655 | 26,073,749 | 25,188,289 | 18,910,439 | 99,966,435 |
| 2026-08-24 | 81,673,156 | 25,273,193 | 25,890,353 | 25,281,449 | 18,301,535 | 99,974,691 |
| 2026-08-25 | 81,640,680 | 25,593,903 | 25,561,427 | 25,602,105 | 18,342,213 | 99,982,893 |
| 2026-08-26 | 81,135,846 | 26,094,204 | 25,589,370 | 26,102,548 | 18,855,391 | 99,991,237 |
| 2026-08-27 | 80,000,000 | 26,521,983 | 25,386,137 | 26,530,746 | 20,000,000 | 100,000,000 |

== 표2 검산 ==
SA(08-27) = 80,000,000  ; == 80,000,000 ? True
facts weekExec = 179,916,643 ; Σ PA1(P) = 179,916,643 ; == ? True

== 표3 7일 합 ==
Σ PA1 = 179,916,643
Σ SA = 564,507,933
Σ EC(역산) = 135,252,611
7×CASH = 140,000,000
Σ(ai×di) = 556,626,436

== 표4 비중과 ⑤ ==
④ weekTyRaw = 4.129577
| 안 | 식 | 비중(6자리) | ⑤ 6자리 = q6(④×비중) | ⑤ 2자리 |
|---|---|---:|---:|---:|
| (가) | ΣPA1 ÷ (ΣPA1 + 7×CASH) | 0.562386 | 2.322416 | 2.32 |
| (나) | ΣPA1 ÷ (ΣPA1 + ΣEC역산) | 0.570857 | 2.357399 | 2.36 |
| (다) | ΣSA ÷ (ΣSA + 7×CASH) | 0.801280 | 3.308946 | 3.31 |
| (라) | ΣSA ÷ (ΣSA + ΣEC역산) | 0.806716 | 3.331395 | 3.33 |
| (마) | Σ(ai×di) ÷ (Σ(ai×di) + 7×CASH) | 0.799031 | 3.299662 | 3.30 |
(가) ⑤ 6자리 2.322416 vs facts weekTyAssetRaw 2.322416 : == ? True

== 표5 기간 길이별 (가)·(라), 끝날 08-26 고정 ==
| n일 | 시작일 | ΣPA1 | n×CASH | ΣSA | ΣEC | (가) | (라) | ⑤(가) | ⑤(라) |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2026-08-26 | 26,094,204 | 20,000,000 | 81,135,846 | 18,855,391 | 0.566106 | 0.811430 | 2.34 | 3.35 |
| 7 | 2026-08-20 | 179,916,643 | 140,000,000 | 564,507,933 | 135,252,611 | 0.562386 | 0.806716 | 2.32 | 3.33 |
| 26 | 2026-08-01 | 676,190,218 | 520,000,000 | 2,051,649,164 | 545,036,198 | 0.565287 | 0.790103 | 2.33 | 3.26 |
| 90 | 2026-05-29 | 2,350,750,321 | 1,800,000,000 | 7,127,905,908 | 1,831,281,590 | 0.566343 | 0.795597 | 2.34 | 3.29 |
| 179 | 2026-03-01 | 4,673,981,320 | 3,580,000,000 | 14,178,044,091 | 3,562,207,670 | 0.566270 | 0.799202 | 2.34 | 3.30 |

== 표6 경계 규약 민감도 (7일, (라)) ==
| 규약 | ΣSA | ΣEC | (라) 6자리 | ⑤ 2자리 | 기준(라) 대비 차 |
|---|---:|---:|---:|---:|---:|
| adv ≤ d, due > d (기준) | 564,507,933 | 135,252,611 | 0.806716 | 3.33 | +0.000000 |
| adv < d, due > d | 383,597,787 | 135,252,611 | 0.739323 | 3.05 | -0.067393 |
| adv ≤ d, due ≥ d | 744,424,576 | 135,252,611 | 0.846247 | 3.49 | +0.039532 |
```

## 스크립트 원문 (`xv_C_calc.py`)

```python
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

```
