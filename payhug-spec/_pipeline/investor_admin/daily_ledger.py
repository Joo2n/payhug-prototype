# -*- coding: utf-8 -*-
"""채권 원장 — 투자자 어드민 숫자의 단일 원천.

대표 정의서가 주는 입력은 채권 목록 하나뿐이다.

    채권 한 건 = (가맹점, 순지급액, 선정산일, 정산예정일)
      Ai = 순지급액 x (1 - 할인율 0.11%)
      Di = 정산예정일 - 선정산일            (한편넣기 · 정수 · 1~13일)

    미회수 채권 = 정산예정일 > 기준일.
    투자실행액       = 미회수 Sum Ai
    가맹점별 투자금액 = 그 가맹점 미회수 채권의 Sum Ai
    w금융일수        = 대상정산금채권 Sum (Ai x Di) / Sum Ai
    ty수익율         = 할인율 x 365 / w금융일수
    하루 투자실행금   = 정산예정일이 그날인 채권의 Sum Ai   (유량 계통)

    투자수익(채권매입수수료)은 순지급액이 앵커다 — D-31 확정. 여기서 부족액을 뺀다.
      M(d-1)i = 채권매입수수료 - max(0, 미지급금 - 과지급금)
      B(d-1)i = 순지급액       - max(0, 미지급금 - 과지급금)
      하루 투자수익  = Sum M(d-1)i,   하루 상환액 = Sum B(d-1)i
      d-1 은 어제 날짜가 아니라 `정산예정일이 어제인 대상정산금채권 집합` 이다.
      하루 ty수익율  = (투자수익 / 투자실행금 x 100) x 365 / w금융일수
    투자실행금 x 할인율로 잡으면 앵커가 (1 - 할인율)배만큼 작아져 투자 시뮬레이션과 갈린다.
    S입금부족율      = Sum SLi / Sum SAi   (표본 = 선정산일 d-20 ~ d-11)
      SLi = 미지급액 - 과지급액 ,  SAi = 순지급액 x (1 - 할인율)

이 파일이 손으로 적는 것은 아래 셋뿐이다. 나머지는 전부 위 산식으로 나온다.

    ① 규모   BOOK = 80,000,000  (투자실행액 · 불변식)
    ② 구성비 가맹점 8건의 일일 선정산 규모와 배달 의존도 b (BOOKROWS)
    ③ 패턴   요일·주차에 따른 규모 계수와 배달 의존도 틸트 (날짜에서 결정 · 무작위 아님)

w금융일수의 모집단 — 대상정산금채권 전체
    대표 정의서에서 '회수되지 않은' 이라는 한정은 투자 실행액 줄에만 붙어 있다.
    w금융일수의 재료인 대상정산금채권은 '선정산일자가 합의서 효력기간에 해당하는 정산금채권'
    이라 회수 여부 조건이 없다. 대표가 낸 `정산주기.xlsx` H41 의 값도 2025년 365일
    발생분 전수의 가중평균이다. 그래서 발생 기준으로 센다.
    가맹점별 W 도 같다. 옆 칸 투자금액(미회수 Sum Ai)은 하루 선정산액 x (1 - 할인율) x 그
    가맹점의 w금융일수라 W 와 같은 금융일수를 쓴다 — 두 칸이 어긋나지 않는다.

가맹점 규모 구간 — 기준은 일일 선정산 규모다. 대표 밴드 100만~1,000만을 3등분한 경계다.
    고액  일 500만원 이상       2건   배달 의존도 높은 상위 2곳
    평범  일 200만 ~ 500만원    4건
    소액  일 200만원 미만       2건   매장 중심 업태 → 카드 비중 높고 부족율 낮음
    구성비 원천이 금액 실측(카드 42.83%)이라 규모가중 배달 의존도가 0.5717 이다. 매장 중심
    업태(일식·카페)를 상위 규모에 놓으면 그 평균을 맞출 수 없어, 배달 의존 업태가 상위에 온다.
"""
import io, json, math, os, sys
from datetime import date, timedelta
from decimal import Decimal as D, ROUND_HALF_UP, ROUND_FLOOR, localcontext

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from platform_duration import (DURATION, ORDER, LABEL, FLOOR, CEIL, BUCKET, OBS_DAYS,
                               DI_MIN, DI_MAX, UNPAID, OVERPAID, BOOK_MIX,
                               duration, mix_of, w_of)

# ══ 상수 ① 규모 · 요율 · 기간 ═══════════════════════════════════
RATE = D('0.0011')                 # 유동화투자자의 할인율
RPCT = D('0.11')
DAYS = D('365')
BOOK = 80000000                    # 투자실행액 — 규모 기준(불변식)
CASH = 20000000                    # 순현금 — 쿠콘 가상계좌 현금잔액. 채권과 무관한 별개 스톡이라
                                   #          원장이 만들지 않고 그대로 받는 입력이다(불변식).

ASOF      = date(2026, 8, 27)      # 기준일 d (오늘 날짜). 금융일수 D 와 다른 글자다
FIRST_DUE = date(2026, 3, 1)       # 일별 표 첫 행(정산예정일)
FIRST_ADV = FIRST_DUE - timedelta(days=DI_MAX)     # 첫 행을 채우는 가장 이른 선정산일
SAMPLE    = (ASOF - timedelta(days=20), ASOF - timedelta(days=11))   # S 표본집합 구간 d-20 ~ d-11

TIER_NAME = {'H': '고액', 'M': '평범', 'L': '소액'}
TIER_CUT  = (5000000, 2000000)     # 고액 / 평범 경계 — 일일 선정산 규모

# ══ 상수 ② 가맹점 8건 구성비 ═══════════════════════════════════
#   flow  일일 선정산 규모(원) — 구간을 가르는 기준값이자 채권 발생량의 가중치.
#         원장은 이 값을 상대 가중치로만 쓰고, 미회수 합이 BOOK 이 되도록 배율을 되푼다.
#         8건 합 26,300,000 은 BOOK / (1 - 할인율) / W = 26,348,172 자리다.
#   b     배달 의존도 — 플랫폼 구성비를 여기 하나에서 파생시킨다(platform_duration.mix_of).
#         카드 = 1 - b, 배달 3사는 b 를 금액 실측 255,514 : 56,628 : 26,752 으로 가른다.
#         가맹점별로 배달 3사 내부 배분을 다르게 잡을 실측 근거가 없어 실측 비를 그대로 쓴다.
#         7곳은 업태로 정한 예시값(`가설`)이고, 김성호떡볶이 본점 한 곳은 규모가중 평균이
#         금액 실측 B_BAR = 338,894 / 592,829 이 되는 자리에서 역산했다.
#           b1 = (26,300,000 x B_BAR - 11,446,000) / 6,400,000 = 1,063,695,733 / 1,897,052,800
#         분모에 89 x 6,661 이 남아 유한소수가 아니다. 20자리에서 끊는다 — 잔차가 b 로 1e-20,
#         W금융일수로 2e-21 이라 표기 소수 2자리는 물론 raw 6자리에도 닿지 않는다.
#         7곳의 값은 0.02 눈금 위에서 골랐다. 채권 61,760건의 Ai 를 원 단위로 반올림하면
#         W금융일수에 1e-7 자리 잔차가 남는데, 실측 3.0396073972 가 raw 표기(소수 6자리)
#         경계에서 1.03e-7 아래라 잔차 방향에 따라 3.039608 로 넘어간다. 이 조합의 잔차는
#         +1.9e-9 이라 원장이 낸 raw W 가 실측과 소수 6자리까지 같다.
#   s     열은 없다 — S입금부족율은 채권의 미지급액·과지급액에서 계산된다.
#
#   (mid, 상호, 사업자번호, 대표자, 업종, 품목, 계약일, 구간, 일일 선정산 규모, 배달 의존도)
BOOKROWS = [
 ('M2026-0001', '김성호떡볶이 본점', '123-45-67890', '김성호', '음식점업', '분식', '2026-01-05',
  'H', 6400000, '0.56070960860973400424'),
 ('M2026-0002', '달빛곱창 홍대점',   '234-56-78901', '이달빛', '음식점업', '곱창', '2026-01-09',
  'M', 2500000, '0.46'),
 ('M2026-0004', '바다마루 횟집',     '456-78-90123', '조해민', '음식점업', '일식', '2026-01-16',
  'L', 1900000, '0.30'),
 ('M2026-0009', '청춘포차 신촌점',   '901-23-45678', '오지훈', '음식점업', '포차', '2026-01-22',
  'M', 2100000, '0.38'),
 ('M2026-0005', '한강커피 잠원점',   '567-89-01234', '정한강', '음식점업', '카페', '2026-02-02',
  'L', 1600000, '0.28'),
 ('M2026-0008', '골목냉면',          '890-12-34567', '백미순', '음식점업', '냉면', '2026-02-06',
  'M', 3000000, '0.60'),
 ('M2026-0006', '김밥나라',          '678-90-12345', '김나라', '음식점업', '김밥', '2026-02-10',
  'M', 3600000, '0.70'),
 ('M2026-0007', '초록치킨 서초점',   '789-01-23456', '최초록', '음식점업', '치킨', '2026-02-13',
  'H', 5200000, '0.80'),
]

# ══ 상수 ③ 날짜에서 결정되는 패턴 (무작위 아님) ═══════════════════
#   SIZE  그날 선정산 규모의 증감. 주말 주문분이 몰리는 요일과 카드 매입분이 몰리는 요일이
#         갈려 하루치가 평균에서 ±7% 안쪽으로 흔들린다.
#   TILT  그날 채권 묶음의 배달 의존도 틸트. + 면 그날 b 가 그만큼 커진다(b x (1 + t)).
#         주기를 7일이 아닌 13·29일로 잡은 것은, 금융일수 1~13일이 섞이면 7일 주기가 상쇄돼
#         정산예정일 기준 묶음에서 금융일수 차이가 드러나지 않기 때문이다.
#         진폭의 상한은 b x (1 + t) <= 1 이다. 로스터 최대 b 는 초록치킨 서초점 0.80,
#         틸트 최대는 0.216237 이라 0.80 x 1.216237 = 0.973 — 구성비가 [0, 1] 안에 남는다.
#         구성비 원천이 MAU(카드 65%)에서 금액 실측(카드 42.83%)으로 바뀌며 규모가중 b 가
#         0.35 에서 0.5717 로 올랐지만, 상한에 닿지 않아 진폭은 그대로 둔다.
#   위상(_PH)은 고정 예시값이다. 규모가중 평균 0 정규화(DAYTILT)를 거치므로 위상을 바꿔도
#   전체 W금융일수는 흔들리지 않고, 달별·일자별 W가 어느 자리에서 흔들리는지만 달라진다.
SIZE_WD = {0: 0.021, 1: 0.006, 2: -0.004, 3: -0.028, 4: -0.033, 5: 0.017, 6: 0.021}
SIZE_A, SIZE_P, SIZE_PH = 0.030, 11.0, 6
TILT = ((0.120, 13.0, 10),      # 주 단위 배달 쏠림
        (0.057, 29.0, 0),       # 달 단위 정산주기 밀림
        (0.044, 101.0, 20))     # 계절 흐름 — 달별 W금융일수 차이를 만든다

UNIT = D(1)


def r1(x):  return D(x).quantize(D('0.1'), rounding=ROUND_HALF_UP)
def r2(x):  return D(x).quantize(D('0.01'), rounding=ROUND_HALF_UP)
def fl(x):  return int(D(x).quantize(D('1'), rounding=ROUND_FLOOR))
def ri(x):  return int(D(x).quantize(D('1'), rounding=ROUND_HALF_UP))
def ty_of(w): return r2(RPCT * DAYS / D(str(w)))
def ymd(d): return d.strftime('%Y-%m-%d')


# ══ ③④⑤⑥ 단일 원천 — 대표 정의서 [2번 이미지] 번호 ═══════════════
#     ④ = PSMR x 365 / PSD
#     ⑤ = (④ x PSA) / (PSA + PSC)
#     ⑥ = (④ ÷ ③) x 365 ÷ ⑤
#   화면(build_app.py) · 시뮬 낱장(build_sim_static.py) · 수익 낱장(roster16_model.ty_asset)
#   · 내려받는 엑셀(build_xlsx.py) 이 전부 아래 함수를 거쳐 값을 받는다.
#   자바스크립트 쪽은 같은 식을 TY3_JS · TY5_JS · TY6_JS 로 내려보내 생성기가 심는다 —
#   파이썬과 화면이 두 벌로 갈리지 않는다.
#   숫자형을 고정하지 않는다 — 원장은 Decimal, 시뮬 낱장은 float 로 같은 함수를 쓴다.

TY_PENDING = '미확정'          # 화면 배지에 쓰는 낱말. 새 문구를 짓지 않는다.

# ── ⑤ 투자자산 대비 Ty수익율 ──────────────────────────────────────
#   미확정 · 대표 재전달 대기. 2026-08-31 회의에서 ⑤ 는 「수식 오류, 새로 작성해 전달」로 닫혔다
#   (meeting_0831/ceo_definitions_20260831.txt). 아래 식은 대표 정의서 [2번 이미지] 원문 그대로다 —
#     「투자자산 대비 ty수익율 (이미지의 ⑤) = (이미지의 ④ x PSA) / (PSA + PSC)」
#   새 수식이 오면 고칠 자리는 ty_asset() 본문 한 줄과 그 짝인 TY5_JS 한 줄뿐이다.
TY5_STATUS = TY_PENDING
TY5_SOURCE = 'ceo_definitions.md [2번 이미지] · 대표 재전달 대기'


def ty_asset(ty4, psa, psc):
    """⑤ = (④ x PSA) / (PSA + PSC).  PSA = 기간 투자실행금 합, PSC = 기간 EC 합."""
    tot = psa + psc
    if not tot:
        return 0
    # Decimal 은 기본 28자리에서 끊긴다. 중간 곱을 넉넉히 잡아 PSC 가 0 일 때
    # ④ 가 마지막 자리를 잃지 않고 그대로 나오게 한다(float 는 이 설정과 무관).
    with localcontext() as ctx:
        ctx.prec = 60
        return ty4 * psa / tot


# ── ③ ⑥ 의 분모 ─────────────────────────────────────────────────
#   대표는 00:59:21 에 ③ 을 「저 위에 있는 현황에 있는 거 … 그 기간 전체에 대한 숫자」까지만
#   좁혔다. 현황의 **어느 칸**인지는 지목되지 않았다 — 읽기 미확정(U-03 · F-23 · TP-66).
#   화면은 일별 표 열 `투자실행금` 으로 읽고 있고, 그 읽기를 여기 한 곳에 모은다.
TY3_STATUS = TY_PENDING
TY3_SOURCE = '대표 2026-08-31 회의 00:59:21 「상단 현황의 기간 전체 숫자」 · 칸 미지목'


def ty_third(execu):
    """③ — ⑥ 의 분모. 일별 표 열 `투자실행금` 으로 읽는다(미확정)."""
    return execu


# ── ⑥ 행 Ty수익율 ────────────────────────────────────────────────
#   행 하나 = 정산예정일이 그 날짜인 대상정산금채권 집합이다. 「그날」이 아니라 그 집합이다.
#   ③·④·⑤ 를 일별 표 세 열(③투자실행금 ④투자 수익 ⑤W금융일수)로 읽는다 — 읽기 미확정.
#   나온 값은 ⑤ 함수 ty_asset() 을 거친다. 일별 EC 원장이 없어 TY6_PSC 가 0 이고,
#   0 인 동안 ⑥ 은 ④ 와 같은 값이다. ty_asset() 을 고치면 ⑥ 이 따라 움직인다.
TY6_PSC = 0


def ty_row(profit, execu, w, days=None, psc=None):
    """⑥ = (④ ÷ ③) x 365 ÷ ⑤ — 한 행."""
    third = ty_third(execu)
    if not (third and w):
        return 0
    four = (profit / third * 100) * (DAYS if days is None else days) / w
    return ty_asset(four, third, TY6_PSC if psc is None else psc)


def day_ty_raw(profit, execu, w):
    """일별 행 ty수익율 — 통합본 rollupBy·엑셀 bucket 과 같은 규칙(⑥)."""
    return ty_row(D(profit), D(execu), D(str(w)))
def day_ty(profit, execu, w): return r2(day_ty_raw(profit, execu, w))


# ── 화면(자바스크립트)이 심는 같은 식 ─────────────────────────────
#   build_app.py 가 @@TY3JS@@ · @@TY5JS@@ · @@TY6JS@@ 로 받아 app.html 에 그대로 넣는다.
TY3_JS = 'return execu;'
TY5_JS = 'var tot = psa + psc;\n  return tot ? ty4 * psa / tot : 0;'
TY6_JS = ('var third = ty3(execu);\n'
          '  if(!(third && w)) return 0;\n'
          '  return ty5((profit / third * 100) * 365 / w, third, TY6_PSC);')


def _size(k, wd):
    return D(str(1.0 + SIZE_WD[wd] + SIZE_A * math.sin(2 * math.pi * (k + SIZE_PH) / SIZE_P)))


def _tilt(k):
    return sum(a * math.sin(2 * math.pi * (k + ph) / p) for a, p, ph in TILT)


# 선정산일 축 — 첫 행(정산예정일 2026-03-01)을 채우려면 금융일수 최대치만큼 앞서 시작한다.
ADV_DAYS = [FIRST_ADV + timedelta(days=i) for i in range((ASOF - FIRST_ADV).days + 1)]

_size_raw = [_size(i, d.weekday()) for i, d in enumerate(ADV_DAYS)]
_zs = sum(_size_raw) / len(_size_raw)
SIZE = [x / _zs for x in _size_raw]                       # 평균 정확히 1

_tilt_raw = [_tilt(i) for i in range(len(ADV_DAYS))]
_zt = sum(D(str(t)) * s for t, s in zip(_tilt_raw, SIZE)) / sum(SIZE)
DAYTILT = [D(str(t)) - _zt for t in _tilt_raw]               # 규모가중 평균 정확히 0
#   → 규모가중 평균이 0이므로 가맹점별·전체 w금융일수가 틸트에 흔들리지 않는다.
#     하루치 묶음만 틸트만큼 금융일수가 길거나 짧아진다.


def tilted(b, t):
    """그날의 배달 의존도 = b x (1 + t). 구성비는 거기서 파생된다.
    구성비가 b 에 대해 1차식이고 t 의 규모가중 평균이 0 이라, 책 전체 구성비는 흔들리지 않는다."""
    return mix_of(D(str(b)) * (D(1) + t))


# ══ 채권 생성 ═══════════════════════════════════════════════════
#   한 칸 = (가맹점, 플랫폼, 금융일수 버킷, 선정산일) → 채권 한 건.
#   대표 정의서의 채권 ID(가맹점ID & 플랫폼ID & 매출일자)와 같은 잘림이다.
def _cells():
    out = []
    for i, d in enumerate(ADV_DAYS):
        size, t = SIZE[i], DAYTILT[i]
        for m in BOOKROWS:
            mid, flow, b = m[0], D(m[8]), m[9]
            tm = tilted(b, t)
            for p, share in zip(ORDER, tm):
                for di, n in BUCKET[p]:
                    out.append((mid, p, di, d, d + timedelta(days=di),
                                flow * size * share * D(n) / D(OBS_DAYS)))
    return out


CELLS = _cells()
OPEN_CELLS = [c for c in CELLS if c[4] > ASOF]


def _open_sum(scale):
    return sum(ri(c[5] * scale) for c in OPEN_CELLS)


def _solve_scale():
    """미회수 Σ Ai 가 정확히 BOOK 이 되는 배율. 단조 계단함수라 이분탐색으로 잡는다."""
    lo = D(BOOK) / sum(c[5] for c in OPEN_CELLS)
    hi = lo * D('1.0001'); lo = lo * D('0.9999')
    for _ in range(200):
        mid = (lo + hi) / 2
        v = _open_sum(mid)
        if v == BOOK:
            return mid
        if v < BOOK:
            lo = mid
        else:
            hi = mid
    return None


SCALE = _solve_scale()
assert SCALE is not None, '미회수 Σ Ai 를 BOOK 에 정확히 맞추는 배율을 못 찾았다'


def _build():
    rows = []
    for mid, p, di, adv, due, unit in CELLS:
        ai = ri(unit * SCALE)                    # Ai = 순지급액 x (1 - 할인율)
        if ai <= 0:
            continue
        net = ri(D(ai) / (D(1) - RATE))          # 순지급액
        up, ov = ri(D(net) * UNPAID[p]), ri(D(net) * OVERPAID[p])
        rows.append(dict(mid=mid, plat=p, di=di, adv=adv, due=due, ai=ai, net=net,
                         unpaid=up, over=ov, ded=max(0, up - ov)))
    return rows


RECEIVABLES = _build()
OPEN = [r for r in RECEIVABLES if r['due'] > ASOF]
EXEC = sum(r['ai'] for r in OPEN)
assert EXEC == BOOK, '미회수 Σ Ai %s != %s' % (EXEC, BOOK)
assert all(DI_MIN <= r['di'] <= DI_MAX for r in RECEIVABLES)


def wavg(rows):
    a = sum(r['ai'] for r in rows)
    return (sum(D(r['ai']) * r['di'] for r in rows) / D(a)) if a else D(0)


W_RAW = wavg(RECEIVABLES)                        # w금융일수 — 대상정산금채권 전체 (발생 기준)
W_BOOK = r2(W_RAW)
# ty수익율은 화면 표기 W(소수 2자리)에서 낸다. 40.15 / 3.04 = 13.21 이라 화면 두 칸(W·할인율)
# 으로 정확히 되짚어진다. 가맹점별 행도 같은 규칙이다(ty_of(x['w'])).
TY_BOOK = ty_of(W_BOOK)
assert FLOOR <= W_RAW <= CEIL, 'w금융일수가 현실 범위 밖이다: %s' % W_RAW

# ── 가맹점별 ────────────────────────────────────────────────────
_SAMPLE = [r for r in RECEIVABLES if SAMPLE[0] <= r['adv'] <= SAMPLE[1]]


def shortfall(rows):
    """S입금부족율 = Σ SLi / Σ SAi — 표본집합 채권에서만 센다."""
    sa = sum(r['ai'] for r in rows)
    sl = sum(r['unpaid'] - r['over'] for r in rows)
    return (D(sl) / D(sa) * 100) if sa else D(0)


MERCHANTS = []
for m in BOOKROWS:
    mid = m[0]
    mine = [r for r in RECEIVABLES if r['mid'] == mid]
    myopen = [r for r in mine if r['due'] > ASOF]      # 투자금액의 모집단(미회수)
    MERCHANTS.append(dict(
        mid=mid, name=m[1], biz=m[2], ceo=m[3], sector=m[4], item=m[5], signed=m[6],
        tier=m[7], tierName=TIER_NAME[m[7]], flow=m[8], b=m[9],
        mix=tuple(str(v.quantize(D('0.000001'))) for v in mix_of(m[9])),
        amount=sum(r['ai'] for r in myopen),
        wraw=wavg(mine), w=r2(wavg(mine)),
        sraw=shortfall([r for r in _SAMPLE if r['mid'] == mid]),
        dayflow=sum(r['ai'] for r in mine) // len(ADV_DAYS)))
MERCHANTS.sort(key=lambda x: -x['amount'])
for x in MERCHANTS:
    x['ty'] = ty_of(x['w'])
    x['s'] = r2(x['sraw'])
assert sum(x['amount'] for x in MERCHANTS) == BOOK
assert len(MERCHANTS) == len(BOOKROWS)

# 구간은 일일 선정산 규모가 가른다 — 원장에서 나온 규모가 경계를 넘지 않는지 본다.
for x in MERCHANTS:
    lo, hi = {'H': (TIER_CUT[0], None), 'M': (TIER_CUT[1], TIER_CUT[0]),
              'L': (None, TIER_CUT[1])}[x['tier']]
    assert (lo is None or x['dayflow'] >= lo) and (hi is None or x['dayflow'] < hi), \
        '%s 구간 %s · 일 선정산 규모 %s 가 경계 밖이다' % (x['name'], TIER_NAME[x['tier']], x['dayflow'])

S_RAW = shortfall(_SAMPLE)

# ── 일별 원장 (정산예정일 축) ───────────────────────────────────
def _daily():
    agg = {}
    for r in RECEIVABLES:
        if not (FIRST_DUE <= r['due'] <= ASOF):
            continue
        g = agg.setdefault(r['due'], dict(ai=0, net=0, wx=0, ded=0))
        g['ai'] += r['ai']; g['net'] += r['net']; g['wx'] += r['ai'] * r['di']
        g['ded'] += r['ded']
    out = []
    for d in sorted(agg):
        g = agg[d]
        w = r2(D(g['wx']) / D(g['ai']))
        fee = fl(D(g['net']) * RATE)        # 채권매입수수료 = 순지급액 x 할인율 (D-31 앵커)
        # M(d-1)i = 채권매입수수료 - max(0, 미지급금 - 과지급금)  (대표 정의서 [2번 이미지])
        # B(d-1)i = 순지급액       - max(0, 미지급금 - 과지급금)  = Ai + M(d-1)i
        # 한 행 = 정산예정일이 그 날짜인 대상정산금채권 집합이다.
        p = fee - g['ded']
        out.append(dict(d=ymd(d), repay=g['ai'] + p, exec=g['ai'], profit=p, w=w,
                        fee=fee, ded=g['ded'], ty=day_ty(p, g['ai'], w)))
    return out


LEDGER = _daily()
assert LEDGER[0]['d'] == ymd(FIRST_DUE) and LEDGER[-1]['d'] == ymd(ASOF)
assert all(FLOOR <= r['w'] <= CEIL for r in LEDGER)

DAY_AVG = ri(D(sum(r['exec'] for r in LEDGER)) / D(len(LEDGER)))   # 하루 평균 투자실행금(유량)

# 표기 W금융일수로 되짚은 ty 가 반올림 경계에 정확히 걸리면 파이썬(ROUND_HALF_UP)과
# 화면 자바스크립트(Math.round·2진 부동소수)가 다른 값을 낸다. 예시 데이터가 그 자리에
# 앉지 않게 막는다 — W 4.4일이 실제로 걸렸다(40.15/4.4 = 9.125).
def _ty_safe(w):
    return (D(str(ty_of(w))) - RPCT * DAYS / D(str(w))).copy_abs() != D('0.005')


for _w in sorted({W_BOOK} | {x['w'] for x in MERCHANTS}):
    assert _ty_safe(_w), 'ty 반올림 경계에 걸린 W금융일수: %s' % _w

for _r in LEDGER:
    _raw = day_ty_raw(_r['profit'], _r['exec'], _r['w'])
    assert (D(str(_r['ty'])) - _raw).copy_abs() != D('0.005'), \
        'ty 반올림 경계에 걸린 일자: %s (W %s)' % (_r['d'], _r['w'])


def js_array(indent='  '):
    out = []
    for r in LEDGER:
        out.append("%s{d:'%s', repay:%d, exec:%d, profit:%d, w:%s, ty:%s}" %
                   (indent, r['d'], r['repay'], r['exec'], r['profit'],
                    format(r['w'], 'f'), format(r['ty'], 'f')))
    return ',\n'.join(out)


def month_rollup(rows):
    agg = {}
    for r in rows:
        k = r['d'][:7]
        g = agg.setdefault(k, dict(d=k, repay=0, exec=0, profit=0, wx=D(0), n=0))
        g['repay'] += r['repay']; g['exec'] += r['exec']; g['profit'] += r['profit']
        g['wx'] += r['w'] * D(r['exec']); g['n'] += 1
    out = []
    for k in sorted(agg):
        g = agg[k]
        raw = g['wx'] / D(g['exec'])
        # 달 행은 집계 행이다. ty = PSMR x 365 / PSD 를 반올림 전 가중평균에서 되짚는다 —
        # 통합본 build_app.py 의 rollupBy·엑셀 build_xlsx.bucket 과 같은 규칙이다.
        ty = r2((D(g['profit']) / D(g['exec']) * D(100)) * DAYS / raw)
        out.append(dict(d=k, repay=g['repay'], exec=g['exec'], profit=g['profit'],
                        w=r2(raw), wraw=raw, ty=ty, n=g['n']))
    return out


def facts():
    """검증기가 읽는 원장 사실값 — 검증기에 숫자를 손으로 적지 않게 한다."""
    wk = [r for r in LEDGER if '2026-08-21' <= r['d'] <= '2026-08-27']
    # 기본 조회 기간(일주일) 집계 — 수익 화면 카드 4/5 와 표 합계 행이 여기서 나온다.
    #   4 투자실행금액 대비 Ty = PSMR x 365 / PSD  (PSD = 투자실행금 가중평균 W, 반올림 전)
    #   5 투자자산   대비 Ty = ty_asset() — PSC = 순현금 x 조회 일수(유량). 산식은 그 함수 한 곳이다
    # build_app.py 의 tyOfRows()·tyAssetOf() 와 같은 규칙이다. 검증기가 이 값을 손으로 적지 않게 한다.
    wk_ex = sum(r['exec'] for r in wk)
    wk_pf = sum(r['profit'] for r in wk)
    wk_wraw = sum(r['w'] * D(r['exec']) for r in wk) / D(wk_ex)
    wk_ty = (D(wk_pf) / D(wk_ex) * D(100)) * DAYS / wk_wraw
    wk_psc = D(CASH) * D(len(wk))
    wk_ty5 = ty_asset(wk_ty, D(wk_ex), wk_psc)
    # 월별 화면(기본 6개월 = 원장 전 구간)의 같은 집계. 일별 표와 달리 달 행의 W 는 달 안에서
    # 다시 가중평균한 값이라 일별 행과 짝이 맞지 않는다 — 달 행은 month_rollup 값으로 대조한다.
    fu_ex = sum(r['exec'] for r in LEDGER)
    fu_pf = sum(r['profit'] for r in LEDGER)
    fu_wraw = sum(r['w'] * D(r['exec']) for r in LEDGER) / D(fu_ex)
    fu_ty = (D(fu_pf) / D(fu_ex) * D(100)) * DAYS / fu_wraw
    fu_psc = D(CASH) * D(len(LEDGER))
    fu_ty5 = ty_asset(fu_ty, D(fu_ex), fu_psc)
    # 일별 표의 날짜 -> [W금융일수, Ty수익율, 투자실행금, 투자수익, 상환액, 채권매입수수료, 부족액 차감].
    #   W 하나에 Ty 하나로 접을 수 없다 — 투자수익에서 부족액(max(0, 미지급-과지급))을 빼면
    #   Ty 가 W 만의 함수가 아니게 된다(대표 정의서 [2번 이미지] M(d-1)i). 날짜로 잡는다.
    #   같은 이유로 수익을 순지급액에서 되짚을 수도 없다. 원장이 낸 값을 그대로 실어 검증기가
    #   행 단위로 맞춰 보게 한다.
    ty_by_date = dict((r['d'], [str(r['w']), str(r['ty']), r['exec'], r['profit'],
                                r['repay'], r['fee'], r['ded']]) for r in LEDGER)
    for r in LEDGER:
        assert r['ty'] == day_ty(r['profit'], r['exec'], r['w']), r['d']
    return dict(
        exec=EXEC, cash=CASH, total=EXEC + CASH,
        wRaw=str(W_RAW.quantize(D('0.000001'))), w=str(W_BOOK), ty=str(TY_BOOK),
        sRaw=str(S_RAW.quantize(D('0.000001'))), s=str(r2(S_RAW)),
        rate=str(RPCT), dayAvg=DAY_AVG, ledgerDays=len(LEDGER),
        ledgerSpan=[LEDGER[0]['d'], LEDGER[-1]['d']],
        receivables=len(RECEIVABLES), openReceivables=len(OPEN),
        # W 와 S 는 같은 행에 나란히 서지만 모집단이 다르다 — 화면 툴팁이 이 두 값을 그대로 읽는다.
        #   W = 대상정산금채권 전체(발생 기준)  ·  S = 선정산일 d-20 ~ d-11 표본
        sampleReceivables=len(_SAMPLE), sampleSpan=[ymd(SAMPLE[0]), ymd(SAMPLE[1])],
        diRange=[min(r['di'] for r in RECEIVABLES), max(r['di'] for r in RECEIVABLES)],
        wRange=[str(min(r['w'] for r in LEDGER)), str(max(r['w'] for r in LEDGER))],
        # 범위 가드의 상·하한 — 원장이 실제로 낸 값(diRange·wRange)이 아니라 허용 경계다.
        # 출처는 platform_duration.py 하나뿐이다(FLOOR/CEIL = 플랫폼별 w금융일수 실측 2.0~6.2일,
        # DI_MIN/DI_MAX = 그 평균을 쪼갠 정수 금융일수 버킷 2~7일). 검증기가 이 숫자를 손으로 적지 않게 한다.
        wBound=[str(FLOOR), str(CEIL)], diBound=[DI_MIN, DI_MAX],
        weekExec=sum(r['exec'] for r in wk), weekProfit=sum(r['profit'] for r in wk),
        weekRepay=sum(r['repay'] for r in wk), weekDays=len(wk),
        weekW=str(r2(wk_wraw)), weekWRaw=str(wk_wraw.quantize(D('0.000001'))),
        weekTy=str(r2(wk_ty)), weekPsc=int(wk_psc), weekTyAsset=str(r2(wk_ty5)),
        tyByDate=ty_by_date,
        fullExec=fu_ex, fullProfit=fu_pf, fullW=str(r2(fu_wraw)),
        fullTy=str(r2(fu_ty)), fullPsc=int(fu_psc), fullTyAsset=str(r2(fu_ty5)),
        monthTy=[[g['d'], str(g['w']), str(g['ty'])] for g in month_rollup(LEDGER)],
        monthExec=[[g['d'], g['exec']] for g in month_rollup(LEDGER)],
        merchants=[[x['name'], x['amount'], str(x['w']), str(x['s']), str(x['ty']), x['tierName'],
                    x['flow']] for x in MERCHANTS])


def dump_facts(path=None):
    import json
    path = path or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ledger_facts.json')
    with io.open(path, 'w', encoding='utf-8') as fp:
        fp.write(json.dumps(facts(), ensure_ascii=False, indent=1))
    return path


if __name__ == '__main__':
    f = lambda n: format(n, ',')
    print('채권 %s건 · 선정산일 %s ~ %s · 기준일 %s'
          % (f(len(RECEIVABLES)), ymd(ADV_DAYS[0]), ymd(ADV_DAYS[-1]), ymd(ASOF)))
    print('미회수 %s건 · 투자실행액 %s · w금융일수 %s(raw %s) · ty %s%%'
          % (f(len(OPEN)), f(EXEC), W_BOOK, W_RAW.quantize(D('0.000001')), TY_BOOK))
    print('S입금부족율 %s%% (raw %s · 표본 %s ~ %s · %s건)'
          % (r2(S_RAW), S_RAW.quantize(D('0.000001')), ymd(SAMPLE[0]), ymd(SAMPLE[1]), f(len(_SAMPLE))))
    print()
    print('구간   상호            일 선정산규모      투자금액        W    S       Ty      비중')
    for x in MERCHANTS:
        print('  %s  %-14s %13s %15s  %s  %s%%  %s%%  %s%%'
              % (x['tierName'], x['name'], f(x['dayflow']), f(x['amount']), x['w'], x['s'], x['ty'],
                 r1(D(x['amount']) / D(EXEC) * 100)))
    print()
    for g in month_rollup(LEDGER):
        print('  %s  %2d일  실행 %15s  수익 %11s  상환 %16s  W %s  Ty %s%%'
              % (g['d'], g['n'], f(g['exec']), f(g['profit']), f(g['repay']), g['w'], g['ty']))
    print('  합계 실행 %s · 하루 평균 %s' % (f(sum(r['exec'] for r in LEDGER)), f(DAY_AVG)))
    print('  모집단 대조 — 전체 %s건 W %s / 미회수 %s건 W %s (화면은 전체 기준)'
          % (f(len(RECEIVABLES)), W_RAW.quantize(D('0.0001')),
             f(len(OPEN)), wavg(OPEN).quantize(D('0.0001'))))
    print('  채권매입수수료 %s · 부족액 차감 %s (%s%%) · 투자수익 %s'
          % (f(sum(r['fee'] for r in LEDGER)), f(sum(r['ded'] for r in LEDGER)),
             (D(sum(r['ded'] for r in LEDGER)) / D(sum(r['fee'] for r in LEDGER)) * 100).quantize(D('0.01')),
             f(sum(r['profit'] for r in LEDGER))))
    wk = [r for r in LEDGER if '2026-08-21' <= r['d'] <= '2026-08-27']
    print('  기본 일주일 실행 %s · 수익 %s · %d건'
          % (f(sum(x['exec'] for x in wk)), f(sum(x['profit'] for x in wk)), len(wk)))
    print('  일자 투자실행금 %s ~ %s · W %s ~ %s'
          % (f(min(r['exec'] for r in LEDGER)), f(max(r['exec'] for r in LEDGER)),
             min(r['w'] for r in LEDGER), max(r['w'] for r in LEDGER)))
    print('  사실값 → %s' % dump_facts())
