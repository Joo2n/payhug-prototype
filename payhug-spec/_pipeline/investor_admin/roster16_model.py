# -*- coding: utf-8 -*-
"""로스터·현황·일별·월별 — 전부 채권 원장(daily_ledger.py)에서 파생.

이 파일에는 금액도 W금융일수도 S입금부족율도 적혀 있지 않다. 원장이 만든 채권을 묶기만 한다.
로스터 곳수도 여기서 정하지 않는다 — 원장의 BOOKROWS 길이가 그대로 온다.

    가맹점별 투자금액 = 그 가맹점의 미회수 Sum Ai
    W금융일수        = 대상정산금채권 Sum (Ai x Di) / Sum Ai   (발생 기준 · 소수 2자리 표기)
    S입금부족율      = Sum SLi / Sum SAi   (표본 = 선정산일 D-20 ~ D-11)
    ty수익율         = 할인율 x 365 / W금융일수
    비중            = 각 금액 / 투자실행액 (소수1자리 · 최대잉여법으로 잔차 배분 · 합 100.0)

일별·월별 투자수익은 순지급액 앵커다(D-31) — 채권매입수수료 = 순지급액 x 할인율. 거기서
부족액 max(0, 미지급금 - 과지급금)을 뺀 것이 MD-1i 다(대표 정의서 [2번 이미지]).
행 ty수익율 = (투자수익 / 투자실행금 x 100) x 365 / W금융일수. 원장이 이미 그렇게 낸 값을 묶기만 한다.

순현금(CASH)만 원장 밖의 입력이다 — 쿠콘 가상계좌 현금잔액이라 채권과 무관한 별개 스톡이다.
"""
import os, sys
from decimal import Decimal as D, ROUND_HALF_UP, ROUND_FLOOR

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from platform_duration import DURATION, ORDER, LABEL, FLOOR, CEIL, duration, w_of, MEASURED_W
import daily_ledger as L
from daily_ledger import (BOOK, CASH, TIER_NAME, TIER_CUT, SAMPLE, ASOF, r1, r2, fl, ty_of,
                          RECEIVABLES, OPEN, MERCHANTS as _M, W_RAW, W_BOOK, TY_BOOK, S_RAW,
                          DAY_AVG, LEDGER, month_rollup, shortfall, wavg)

R    = D('0.0011')
RPCT = D('0.11')
DAYS = D('365')

def ty(w):  return ty_of(w)
def f(n):   return format(n, ',')

# 종전 소비자가 그대로 쓰던 이름들 — 원장에서 되짚어 채운다.
MIX = {x['mid']: x['mix'] for x in _M}
TIERS = {x['mid']: x['tier'] for x in _M}

# ── 가맹점 로스터 (금액 내림차순 · 기본 보기 10건 안이라 1페이지) ────
#   (상호, 투자금액, W금융일수, S입금부족율, MID, 사업자번호, 대표자, 업종, 품목, 계약일)
ROSTER = [(x['name'], x['amount'], str(x['w']), str(x['s']), x['mid'], x['biz'], x['ceo'],
           x['sector'], x['item'], x['signed']) for x in _M]

EXEC  = sum(x[1] for x in ROSTER)          # 투자실행액 = 미회수 Σ Ai
TOTAL = EXEC + CASH                        # 투자자산
assert EXEC == BOOK

def ratios(amounts, base):
    """소수1자리 표기 — 최대잉여법. 합이 정확히 100.0 이고 어느 행도 한 눈금(0.1pp)을 넘게 밀리지 않는다.

    잔차를 최대 금액 행 하나에 몰면 그 행만 눈금 여러 개만큼 밀린다(8행 로스터에서 눈금 5개).
    0.1pp 단위로 내림한 뒤 남는 눈금을 소수부가 큰 행부터 하나씩 나눠 준다.
    통합본 build_app.py 의 ratios() 와 같은 규칙이다 — 화면과 엑셀이 다른 비중을 말하지 않는다.
    """
    n = len(amounts)
    if not n or not base:
        return [r1(D(0))] * n
    unit, frac = [], []
    for i, a in enumerate(amounts):
        raw = D(a) * 1000 / D(base)
        fl = int(raw.to_integral_value(rounding=ROUND_FLOOR))
        unit.append(fl)
        frac.append((raw - fl, D(a), -i))          # 동률이면 금액 큰 행, 그다음 앞 행
    rest = 1000 - sum(unit)
    order = sorted(range(n), key=lambda i: frac[i], reverse=True)
    for i in order[:max(0, rest)]:
        unit[i] += 1
    return [r1(D(u) / D(10)) for u in unit]

SHARES = ratios([x[1] for x in ROSTER], EXEC)

# ── 서명 대기 큐 — 정산채권 양수 화면이 세우는 3건 ──────────────────
#   계약기록도 같은 목록을 본다. 한 화면이 `서명 대기`라고 하는 가맹점을 다른 화면이
#   `하나인증서로 서명 완료`로 보이면 같은 예시 데이터가 두 말을 하게 된다.
#   (가맹점ID, 계약 생성일) — 상호는 로스터에서 온다.
SIGN_PENDING = (('M2026-0001', '2026-08-25'),
                ('M2026-0002', '2026-08-26'),
                ('M2026-0004', '2026-08-27'))
SIGN_PENDING_MIDS = tuple(m for m, _ in SIGN_PENDING)
NAME_OF = {x['mid']: x['name'] for x in _M}


def sign_queue():
    """(가맹점ID, 상호, 계약 생성일) — 화면 SIGNQ 그대로."""
    return [(mid, NAME_OF[mid], made) for mid, made in SIGN_PENDING]


def contract_signed(mid):
    """계약기록에서 이미 서명이 끝난 계약인가 — 서명 대기 큐에 없으면 끝난 것이다."""
    return mid not in SIGN_PENDING_MIDS


def contract_default_sel(n=3):
    """계약기록 기본 선택 — 서명이 끝난 계약 중 표 순서로 앞 n건."""
    return tuple(x[4] for x in ROSTER if contract_signed(x[4]))[:n]

def wavg_pairs(vals, wts):
    return sum(D(str(v)) * D(w) for v, w in zip(vals, wts)) / D(sum(wts))

AMTS = [x[1] for x in ROSTER]
# 투자실행액 행의 W·S 는 개별 행을 다시 평균 낸 값이 아니라 원장에서 한 번에 낸 값이다.
#   W = 대상정산금채권 Sum(Ai x Di) / Sum Ai   ·   S = 표본집합 Sum SLi / Sum SAi
# 두 값의 모집단이 서로 다르다 — W 는 발생분 전체, S 는 선정산일 D-20~D-11 표본이다.
W_W  = W_RAW
S_W  = S_RAW
# ty = 할인율 x 365 / W. 화면에 뜨는 W(소수2자리)에서 낸 값이라 보는 사람이 화면 두 칸으로
# 되짚을 수 있다. 가맹점별 행도 같은 규칙이다(ty_of(x['w'])).
TY_W = TY_BOOK
TY_W_ROWAVG = wavg_pairs([ty(x[2]) for x in ROSTER], AMTS)   # 참고값 — 화면에는 쓰지 않는다

EXEC_SHARE = r1(D(EXEC) / D(TOTAL) * 100)
CASH_SHARE = r1(D(CASH) / D(TOTAL) * 100)

# ── 일별·월별 투자수익 — 원장 롤업 그대로 ─────────────────────────
WEEK = ('2026-08-21', '2026-08-27')        # 기본 조회 기간(일주일)
#   w 는 화면 표기 그대로 문자열로 담는다 — 정적 낱장·엑셀·통합본이 같은 자리를 대조한다.
def _srow(r):
    x = dict(r); x['w'] = str(x['w']); return x
DAILY   = [_srow(r) for r in LEDGER if WEEK[0] <= r['d'] <= WEEK[1]]
MONTHLY = [_srow(r) for r in month_rollup(LEDGER)]
DAILY_W = [(r['d'], r['exec'], str(r['w'])) for r in DAILY]
MON_W   = [(r['d'], r['exec'], str(r['w'])) for r in MONTHLY]

# ── 투자자산 대비 ty수익율(현황 ⑤) — 대표 정의서 기준 ──────────────
# ⑤ = (④ x PSA) / (PSA + PSC).  PSA = 기간 투자실행금 합(유량),
# PSC = 기간 동안 EC(전일자 순현금)들의 합(유량). EC 예시값은 순현금 잔액 CASH 로 고정한다.
EC_DAILY_WEEK = len(DAILY)
EC_MONTHLY_ALL = len(LEDGER)
EC_MONTH_AUG = sum(1 for r in LEDGER if r['d'].startswith('2026-08'))

def ty_asset(ty4, psa, ec_days):
    """⑤ 산식은 daily_ledger.ty_asset 한 곳에 있다 — 여기는 EC 일수를 PSC 로 바꿔 넘기는 껍질이다."""
    return r2(L.ty_asset(D(str(ty4)), D(psa), D(CASH) * D(ec_days)))

def agg(rs, ec_days):
    # 합계 행의 Ty = PSMR x 365 / PSD (대표 정의서). PSD 는 반올림 전 가중평균을 쓴다.
    # 통합본 build_app.py 의 tyOfRows·rollupBy 와 같은 규칙이라 화면과 파일이 갈리지 않는다.
    ex = sum(r['exec'] for r in rs); pr = sum(r['profit'] for r in rs); rp = sum(r['repay'] for r in rs)
    wv = wavg_pairs([r['w'] for r in rs], [r['exec'] for r in rs])
    tv = (D(pr) / D(ex) * D(100)) * DAYS / wv
    return dict(exec=ex, profit=pr, repay=rp, w=r2(wv), wraw=wv, ty=r2(tv), tyraw=tv,
                ecDays=ec_days, psc=CASH * ec_days, tyAsset=ty_asset(tv, ex, ec_days))

DSUM, MSUM = agg(DAILY, EC_DAILY_WEEK), agg(MONTHLY, EC_MONTHLY_ALL)
AUG = MONTHLY[-1]
AUG_CARD = dict(exec=AUG['exec'], profit=AUG['profit'], ty=AUG['ty'], ecDays=EC_MONTH_AUG,
                tyAsset=ty_asset(AUG['ty'], AUG['exec'], EC_MONTH_AUG))

# ── 규모 구간 요약 ────────────────────────────────────────────────
def tier_table():
    out = []
    for t in ('H', 'M', 'L'):
        g = [x for x in _M if x['tier'] == t]
        out.append(dict(tier=t, name=TIER_NAME[t], n=len(g),
                        flowLo=min(x['dayflow'] for x in g), flowHi=max(x['dayflow'] for x in g),
                        amtLo=min(x['amount'] for x in g), amtHi=max(x['amount'] for x in g),
                        amt=sum(x['amount'] for x in g),
                        wLo=min(x['w'] for x in g), wHi=max(x['w'] for x in g),
                        sLo=min(x['s'] for x in g), sHi=max(x['s'] for x in g)))
    return out

if __name__ == '__main__':
    print('로스터 %d건 · 투자실행액 %s · 순현금 %s · 투자자산 %s' % (len(ROSTER), f(EXEC), f(CASH), f(TOTAL)))
    print('비중 합계 %s (최대잉여법 · 잔차를 한 행에 몰지 않는다)' % sum(SHARES))
    for (n, a, w, s, mid, *_), sh in zip(ROSTER, SHARES):
        print('  %s %-14s %15s  W %s  S %s%%  Ty %s%%  비중 %s%%'
              % (TIER_NAME[TIERS[mid]], n, f(a), w, s, ty(w), sh))
    print('투자실행액 행 — W %s (raw %s) · S %s%% (raw %s) · Ty %s%% · 비중 %s%%'
          % (r2(W_W), W_W.quantize(D('0.000001')), r2(S_W), S_W.quantize(D('0.000001')),
             r2(TY_W), EXEC_SHARE))
    print('순현금 비중 %s%% · 합계 %s%%' % (CASH_SHARE, EXEC_SHARE + CASH_SHARE))
    print()
    print('구간   건수  일 선정산 규모              투자금액                 W        S')
    for t in tier_table():
        print('  %s  %2d건  %13s ~ %13s  %13s ~ %13s  %s~%s  %s~%s%%'
              % (t['name'], t['n'], f(t['flowLo']), f(t['flowHi']), f(t['amtLo']), f(t['amtHi']),
                 t['wLo'], t['wHi'], t['sLo'], t['sHi']))
    print()
    for lbl, rs, sm in (('일별', DAILY, DSUM), ('월별', MONTHLY, MSUM)):
        print('== %s ==' % lbl)
        for r in rs:
            print('  %s  실행 %15s  수익 %12s  상환 %16s  W %s  Ty %s%%'
                  % (r['d'], f(r['exec']), f(r['profit']), f(r['repay']), r['w'], r['ty']))
        print('  합계 실행 %s · 수익 %s · 상환 %s · W %s · Ty %s%% · Ty(자산대비) %s%%'
              % (f(sm['exec']), f(sm['profit']), f(sm['repay']), sm['w'], sm['ty'], sm['tyAsset']))
        print('  역검산 수익/실행 = %s%%' % (D(sm['profit']) / D(sm['exec']) * 100).quantize(D('0.000001')))
    print('월별 카드(2026-08) 실행 %s · 수익 %s · Ty %s%% · Ty(자산대비) %s%%'
          % (f(AUG_CARD['exec']), f(AUG_CARD['profit']), AUG_CARD['ty'], AUG_CARD['tyAsset']))
