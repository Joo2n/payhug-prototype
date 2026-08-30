# -*- coding: utf-8 -*-
"""플랫폼별 평균만기(Duration)와 예시 데이터의 플랫폼 구성 — W금융일수의 유일한 출처.

W금융일수는 금융 일반 용어로 `Duration`(가중평균만기)이다. 가중치는 투자액(= 선정산대금)이다.
그러므로 예시 데이터의 W금융일수는 임의로 정할 값이 아니라 **플랫폼 구성비에서 나오는 값**이다.

근거 1 — 플랫폼별 금융일수 도수분포 (조현준 `정산주기.xlsx` N6:Q370, 2025년 365일 실측)
    금융일수 = 락계좌 입금일 - 선정산일, 선정산일 = 결제일 다음날. 2025년 365일 각 일자에서
    잰 값을 (금융일수, 관측 일수) 정수쌍으로 그대로 든다. 평균은 이 도수에서 파생시킨다.

      카드사      Sum(d x n) =   736 / 365 = 2.016438…일   (엑셀 H40)
      배달의민족  Sum(d x n) = 1,223 / 365 = 3.350685…일   (엑셀 H32)
      쿠팡이츠    Sum(d x n) = 1,733 / 365 = 4.747945…일   (엑셀 H24)
      요기요      Sum(d x n) = 2,250 / 365 = 6.164384…일   (엑셀 H16)

    배달앱을 전혀 쓰지 않는 가맹점은 2.0일, 요기요만 쓰는 가맹점은 6.2일.
    현실의 가맹점은 그 사이에 놓인다.
    카드 2.0일은 `analysis/figma_policy_db.md` §1의 정산채권DB 실측(지급예상일 = 거래일 + 2영업일,
    23행 전수 검증)과 같은 규칙을 연평균으로 환산한 값이다.

근거 2 — 플랫폼 구성비 (조현준 `정산주기.xlsx` `비중` D4:H6 · `정산주기` I16·I24·I32·I40)
    카드 0.65 고정, 배달앱 3종은 2025/4 MAU 비중 2,175 : 1,044 : 486 으로 나머지 0.35 를 가른다.

      카드 13/20 = 0.65                배달의 민족  203/988   = 0.205465587044534…
      쿠팡이츠   609/6175 = 0.098623481781377…   요기요      567/12350 = 0.045910931174089…

    이 구성으로 낸 가중평균만기 = 2.750406854861073일 (엑셀 H41). 범위 2.0 ~ 6.2 안에 든다.

근거 2-b — 참고 기록으로만 남기는 Figma 실측 (node 2782:5879 · 하루 1가맹점치)
    `미리 받는 돈 상세` 화면이 하루치 순지급액을 플랫폼별로 쪼갠 값이다
    (`analysis/figma_02_가맹점화면.md` §3-2).

      카드 9사 합계  253,935원      배달의 민족  255,514원
      쿠팡이츠        56,628원      요기요        26,752원
      ─────────────────────────────────────────────────
      합계           592,829원 →  카드 42.83% · 배민 43.10% · 쿠팡이츠 9.55% · 요기요 4.51%

    하루 순지급액 592,829원짜리 1가맹점 1일치라 책 전체 구성비와 층위가 다르다.
    로스터 집계의 근거로는 쓰지 않고 `MEASURED` 로 기록만 남긴다.

근거 3 — 가맹점 한 곳이 실제로 무는 플랫폼 집합
    `01_payhug-admin-web-main/lib/devMockData.ts:5866-5970`
    (`GET admin/merchants/{id}/platform-settlement-account-status`, businessId 101 =
     `김성호떡볶이 본점`) — CARD(KB·신한) + BAEMIN + COUPANG + YOGIYO 4종.
    로스터 1번 가맹점이 카드 2사 + 배달 3사를 무는 구성으로 잡힌 근거다.

확정 / 가설 구분
    `확정`  금융일수 도수분포 · 플랫폼 구성비 (근거 1·2, 대표 실측)
    `가설`  로스터 9건 각각의 배달 의존도 `b` — 업태별로 달리 잡은 예시다. 다만 9건을
            금액으로 가중평균한 구성비가 근거 2의 대표 비중과 정확히 같도록 맞췄다.
"""
from decimal import Decimal as D, ROUND_HALF_UP

# ── 표기 반올림 ──────────────────────────────────────────────────
def r1(x): return D(x).quantize(D('0.1'), rounding=ROUND_HALF_UP)
def r2(x): return D(x).quantize(D('0.01'), rounding=ROUND_HALF_UP)

# ── 근거 1 — 금융일수 도수분포 (금융일수, 2025년 관측 일수) ────────
#   채권 한 건의 금융일수는 날짜 차이라 정수다(대표 정의 · 한편넣기).
#   플랫폼 평균만기가 소수인 것은 건별 정수 만기가 섞여 나온 평균이기 때문이다.
#   도수 정수쌍만 들고 분모 365 를 상수로 두어 부동소수 잔차가 생기지 않게 한다.
BUCKET = {
    'card': ((1, 189), (2, 53), (3, 96), (4, 12), (5, 4), (6, 2), (7, 3), (8, 3), (9, 2), (10, 1)),
    'bm':   ((2, 138), (3, 52), (4, 139), (5, 18), (6, 6), (7, 2), (8, 2), (9, 3), (10, 3), (11, 2)),
    'cpe':  ((3, 89), (4, 48), (5, 177), (6, 24), (7, 8), (8, 4), (9, 4), (10, 4), (11, 3), (12, 4)),
    'yo':   ((4, 43), (5, 43), (6, 211), (7, 27), (8, 13), (9, 7), (10, 7), (11, 3), (12, 5), (13, 6)),
}
OBS_DAYS = 365
ORDER    = ('card', 'bm', 'cpe', 'yo')
LABEL    = {'card': '카드사', 'bm': '배달의민족', 'cpe': '쿠팡이츠', 'yo': '요기요'}

# 평균만기는 손으로 적지 않고 도수에서 파생시킨다.
DURATION = dict((k, sum(D(d) * D(n) for d, n in b) / D(OBS_DAYS)) for k, b in BUCKET.items())
DI_MIN = min(d for b in BUCKET.values() for d, _ in b)
DI_MAX = max(d for b in BUCKET.values() for d, _ in b)      # 1 ~ 13일
FLOOR, CEIL = r1(DURATION['card']), r1(DURATION['yo'])      # 현실 범위 2.0 ~ 6.2

for _k, _b in BUCKET.items():
    assert sum(n for _, n in _b) == OBS_DAYS, _k
    assert len(set(d for d, _ in _b)) == len(_b), _k
    assert all(n > 0 for _, n in _b), _k

# ── 근거 2 — 대표 비중 (카드 고정분 + 배달앱 MAU 배분) ─────────────
#   카드 0.65, 나머지 0.35 를 배민:쿠팡이츠:요기요 = 2,175 : 1,044 : 486 (2025/4 MAU) 로 가른다.
#   약분하면 725 : 348 : 162 (합 1,235) 이라 배달 3종 합이 정확히 0.35 가 된다.
CARD_SHARE = D('0.65')
MAU = {'bm': D(725), 'cpe': D(348), 'yo': D(162)}
MAU_SUM = sum(MAU.values())                                  # 1,235
BOOK_MIX = ((CARD_SHARE,) +
            tuple((D(1) - CARD_SHARE) * MAU[k] / MAU_SUM for k in ('bm', 'cpe', 'yo')))


def mix_of(b):
    """배달 의존도 b 하나에서 플랫폼 구성비 4개를 파생시킨다 — 합은 구성상 정확히 1."""
    b = D(str(b))
    assert 0 <= b <= 1, '배달 의존도가 [0, 1] 밖이다: %s' % b
    rest = tuple(b * MAU[k] / MAU_SUM for k in ('bm', 'cpe', 'yo'))
    return (D(1) - sum(rest),) + rest


# ── 근거 2-b — 참고 기록 · 실측 1일치 순지급액 (원) ─────────────────
MEASURED = {'card': 253935, 'bm': 255514, 'cpe': 56628, 'yo': 26752}
MEASURED_SRC = 'Figma 2782:5879 · 미리 받는 돈 상세 (analysis/figma_02_가맹점화면.md §3-2)'

# ── 근거 4 — 플랫폼별 미지급·과지급 발생률 (순지급액 대비) ─────────
#   S입금부족율의 재료다. 대표 정의서는 산식만 주었고 값은 예시로 우리가 넣는다.
#     SLi = 미지급액 - 과지급액 ,  SAi = 순지급액 x (1 - 할인율)
#
#   크기를 잡은 근거
#     ① 상한 — 부족율이 할인율(0.11%)을 넘으면 그 채권은 투자자 몫 수익을 다 먹고도
#        원금이 모자란다. 선정산 재원(순자산)이 그만큼 깎이므로 지속 불가능한 구조다.
#        그래서 전체 가중 부족율은 할인율 아래에 둔다.
#     ② 플랫폼별 차이 — 카드 매입분은 승인취소·환불 조정만 생겨 극소다
#        (`payhug-spec/04_EXCEPTIONS.md` 취소·환불 계열). 배달앱은 프로모션 정산 차감·
#        주문취소·정산보류가 겹쳐 카드보다 한 자릿수 크다.
#     ③ 방향 — 미지급(줘야 하는데 못 준 것)이 과지급(더 나간 것)보다 크다.
#        과지급은 취소분 회수 지연에서만 생겨 미지급의 1/3 안쪽이다.
#   6대 개념 구분 — 여기서 쓰는 미지급금·과지급금은 서로 다른 계정이며 합치지 않는다.
UNPAID = {'card': D('0.00025'), 'bm': D('0.00140'), 'cpe': D('0.00210'), 'yo': D('0.00300')}
OVERPAID = {'card': D('0.00010'), 'bm': D('0.00045'), 'cpe': D('0.00055'), 'yo': D('0.00075')}
for _k in ORDER:
    assert 0 <= OVERPAID[_k] < UNPAID[_k], _k


def duration(mix):
    """플랫폼 구성비 → 가중평균만기(Duration). mix = (카드, 배민, 쿠팡이츠, 요기요), 합 1."""
    m = [D(str(v)) for v in mix]
    assert sum(m) == 1, '구성비 합이 1이 아니다: %s' % (mix,)
    assert all(v >= 0 for v in m), '음수 구성비: %s' % (mix,)
    return sum(v * DURATION[k] for v, k in zip(m, ORDER))


def w_of(mix):
    """화면 표기용 W금융일수 — 소수 2자리."""
    w = r2(duration(mix))
    assert FLOOR <= w <= CEIL, 'W금융일수가 현실 범위(2.0~6.2) 밖이다: %s' % w
    return w


def measured_mix():
    t = D(sum(MEASURED.values()))
    return tuple(D(MEASURED[k]) / t for k in ORDER)


MEASURED_W = duration(measured_mix())          # 참고값 — 데이터로 쓰지 않는다


if __name__ == '__main__':
    t = sum(MEASURED.values())
    print('실측 1일치 순지급액 합계 %s원' % format(t, ','))
    for k in ORDER:
        print('  %-10s %10s원  %6s%%  평균만기 %s일'
              % (LABEL[k], format(MEASURED[k], ','),
                 (D(MEASURED[k]) / D(t) * 100).quantize(D('0.01')), DURATION[k]))
    print('실측 구성의 가중평균만기 = %s일 → 표기 %s일 (참고 기록 · 데이터로 쓰지 않는다)'
          % (MEASURED_W.quantize(D('0.000001')), r2(MEASURED_W)))
    print('현실 범위 %s ~ %s일 (배달앱 미사용 ~ 요기요 전용)' % (FLOOR, CEIL))
    print('금융일수 도수 — 채권 한 건의 금융일수는 %d ~ %d일 · 관측 %d일' % (DI_MIN, DI_MAX, OBS_DAYS))
    for k in ORDER:
        print('  %-10s %s  →  합 %s / %d = %s일'
              % (LABEL[k], ' '.join('%d일x%d' % (d, n) for d, n in BUCKET[k]),
                 sum(d * n for d, n in BUCKET[k]), OBS_DAYS,
                 DURATION[k].quantize(D('0.000000000000001'))))
    print('대표 비중 — %s' % ' · '.join('%s %s' % (LABEL[k], v.quantize(D('0.0000000000000001')))
                                        for k, v in zip(ORDER, BOOK_MIX)))
    print('대표 비중의 가중평균 금융일수 = %s일 → 표기 %s일'
          % (sum(v * DURATION[k] for v, k in zip(BOOK_MIX, ORDER)).quantize(D('0.0000000000000001')),
             r2(sum(v * DURATION[k] for v, k in zip(BOOK_MIX, ORDER)))))
    print('미지급·과지급 발생률 (순지급액 대비)')
    for k in ORDER:
        print('  %-10s 미지급 %s%%  과지급 %s%%  순 %s%%'
              % (LABEL[k], UNPAID[k] * 100, OVERPAID[k] * 100, (UNPAID[k] - OVERPAID[k]) * 100))
