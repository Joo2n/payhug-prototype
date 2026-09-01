# -*- coding: utf-8 -*-
"""확정 원고 `final_terms.json` 의 산식·값 전건 재계산 검증기.

대상   payhug-spec/_pipeline/investor_admin/final_terms.json  (vars 29항 · calc 9단계 + 검산 4줄)
원천   daily_ledger.py  →  ledger_facts.json   (값의 단일 원천)
화면   payhug-investor-admin/invest-assets.html · invest-profit.html  (헤드리스 크롬 실렌더)

이 검증기가 보는 것은 이름이 아니라 숫자다. 두 축을 따로 판정한다.
  (축1) 원고에 적힌 값이 원장 원천과 같은가
  (축2) 원고에 적힌 산식대로 계산하면 그 값이 나오는가
둘 중 하나만 맞아도 원고는 닫히지 않는다 — 산식과 값이 다른 것을 가리키고 있다는 뜻이다.

검증기에 원장 숫자를 손으로 적지 않는다. 기대값은 전부 daily_ledger 를 그 자리에서 돌려 받는다.
원고 값만 파일에서 읽는다 — 그것이 검사 대상이기 때문이다.

새는 네 갈래를 막는다.
  · FAIL 이 하나라도 있으면 종료코드 1                       → main() 끝 exit(1 if FAILS else 0)
  · try/except 가 SKIP 으로 삼키지 않는다                     → section() 이 예외를 FAIL 로 기록
  · 판정 없이 값만 출력하는 자리를 두지 않는다                 → 출력은 전부 chk() 를 거친다
  · 대상 0건이면 통과하지 않는다                              → 루프마다 「대상 0건 아님」 판정

실행
  python3 verify_final_terms.py              전건 (화면 렌더 포함 · 판별력 자기시험 포함)
  FT_NOSCREEN=1 python3 verify_final_terms.py   화면 빼고
  FT_MANUSCRIPT=<경로>                        원고 사본으로 돌린다 (판별력 시험이 쓴다)
"""
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import hashlib
from decimal import Decimal as D, ROUND_HALF_UP, getcontext
from datetime import date

getcontext().prec = 60

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

MANUSCRIPT = os.environ.get('FT_MANUSCRIPT') or os.path.join(HERE, 'final_terms.json')
SCREEN_REPO = os.environ.get('FT_SCREEN_REPO') or '/Users/semi/cursor/payhug-investor-admin'
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
CHILD = os.environ.get('FT_CHILD') == '1'
NOSCREEN = os.environ.get('FT_NOSCREEN') == '1' or CHILD

# 화면 뷰포트 — macOS 는 --window-size 높이에서 87px 이 크롬 크롬(툴바 자리)로 빠진다.
VIEW_W, VIEW_H = 1440, 1200
WIN_H = VIEW_H + 87

R = []          # (id, pass, 제목, 실측 문장)


def chk(cid, ok, title, detail=''):
    R.append((cid, bool(ok), title, detail))
    return bool(ok)


def section(name, fn):
    """예외를 SKIP 으로 삼키지 않는다 — 터지면 그 구획이 통째로 FAIL 한 건이 된다."""
    try:
        fn()
    except Exception as e:                                   # noqa: BLE001
        import traceback
        chk(name + '.EXC', False, '%s 구획이 예외로 끊겼다' % name,
            '%s: %s | %s' % (type(e).__name__, e, traceback.format_exc().splitlines()[-3:]))


def q(x, n):
    return D(x).quantize(D('1.' + '0' * n) if n else D('1'), rounding=ROUND_HALF_UP)


def num(s):
    """원고 표기 문자열에서 숫자 하나를 뽑는다. `3.991318%   화면 3.99%` → 3.991318"""
    m = re.search(r'-?[\d,]+\.?\d*', s.replace(' ', ''))
    if not m:
        raise ValueError('숫자를 못 뽑았다: %r' % s)
    return D(m.group(0).replace(',', ''))


def nums(s):
    return [D(x.replace(',', '')) for x in re.findall(r'-?[\d,]+\.?\d*', s)]


# ══════════════════════════════════════════════════════════════════
# 원천 — daily_ledger 를 그 자리에서 돌린다
# ══════════════════════════════════════════════════════════════════
import daily_ledger as L                                     # noqa: E402

FACTS = json.load(io.open(os.path.join(HERE, 'ledger_facts.json'), encoding='utf-8'))
MS_RAW = io.open(MANUSCRIPT, 'rb').read()
MS_MD5 = hashlib.md5(MS_RAW).hexdigest()
MS = json.loads(MS_RAW.decode('utf-8'))

RATE = L.RATE                                                # 0.0011
RPCT = L.RPCT                                                # 0.11
DAYS = L.DAYS                                                # 365
ASOF = L.ASOF

# 정산예정일 축 하루 묶음 — 원장이 일별 표를 만드는 그 집합이다.
DAYROWS = {}
for _r in L.RECEIVABLES:
    if L.FIRST_DUE <= _r['due'] <= ASOF:
        DAYROWS.setdefault(_r['due'], []).append(_r)

WEEK_FROM, WEEK_TO = date(2026, 8, 21), date(2026, 8, 27)    # 원고 calc 이 스스로 적은 조회기간
WEEK_DAYS = [d for d in sorted(DAYROWS) if WEEK_FROM <= d <= WEEK_TO]


def day_A(d):
    return sum(r['ai'] for r in DAYROWS[d])


def day_NET(d):
    return sum(r['net'] for r in DAYROWS[d])


def day_DED(d):
    return sum(r['ded'] for r in DAYROWS[d])


def day_FEE(d):
    """원장의 채권매입수수료 — 하루 Σ순지급액에 요율을 곱하고 내림한다(건별 칸이 없다)."""
    return L.fl(D(day_NET(d)) * RATE)


def day_M(d):
    return day_FEE(d) - day_DED(d)


def day_wD_raw(d):
    return D(sum(r['ai'] * r['di'] for r in DAYROWS[d])) / D(day_A(d))


def day_wD_disp(d):
    return q(day_wD_raw(d), 2)


PA = sum(day_A(d) for d in WEEK_DAYS)
PM = sum(day_M(d) for d in WEEK_DAYS)
PEC = L.CASH * len(WEEK_DAYS)
# PwD 두 길 — 원장·화면은 일자 단위(표기 wD 가중), 원고 산식은 채권 단위다.
PWD_DAY = sum(day_wD_disp(d) * D(day_A(d)) for d in WEEK_DAYS) / D(PA)
PWD_REC = D(sum(r['ai'] * r['di'] for d in WEEK_DAYS for r in DAYROWS[d])) / D(PA)
PWD_DAYRAW = sum(day_wD_raw(d) * D(day_A(d)) for d in WEEK_DAYS) / D(PA)

PMR = D(PM) / D(PA) * 100                                    # %
TURN_DAY = DAYS / PWD_DAY
PYMR_DAY = PMR * TURN_DAY
SHARE = D(PA) / D(PA + PEC)
WPYMR_DAY = PYMR_DAY * SHARE
PYMR_REC = PMR * DAYS / PWD_REC
WPYMR_REC = PYMR_REC * SHARE

OPEN = [r for r in L.RECEIVABLES if r['due'] > ASOF]
SUM_A_OPEN = sum(r['ai'] for r in OPEN)
WD_ALL = D(sum(r['ai'] * r['di'] for r in L.RECEIVABLES)) / D(sum(r['ai'] for r in L.RECEIVABLES))
WD_OPEN = D(sum(r['ai'] * r['di'] for r in OPEN)) / D(SUM_A_OPEN)
SAMPLE = [r for r in L.RECEIVABLES if L.SAMPLE[0] <= r['adv'] <= L.SAMPLE[1]]
LR = D(sum(r['unpaid'] - r['over'] for r in SAMPLE)) / D(sum(r['ai'] for r in SAMPLE)) * 100

SCREEN = {}


# ══════════════════════════════════════════════════════════════════
# A. 원천 무결 — 재계산이 ledger_facts.json 과 맞는가
# ══════════════════════════════════════════════════════════════════
def sec_A():
    chk('A0', len(WEEK_DAYS) > 0, '조회기간 대상 0건 아님', '%d일' % len(WEEK_DAYS))
    chk('A0b', len(DAYROWS) > 0 and len(L.RECEIVABLES) > 0, '원장 대상 0건 아님',
        '채권 %s건 · 일자 %d개' % (format(len(L.RECEIVABLES), ','), len(DAYROWS)))
    chk('A1', PA == FACTS['weekExec'], 'PA 재계산 = facts.weekExec',
        '%s ↔ %s' % (format(PA, ','), format(FACTS['weekExec'], ',')))
    chk('A2', PM == FACTS['weekProfit'], 'PM 재계산 = facts.weekProfit',
        '%s ↔ %s' % (format(PM, ','), format(FACTS['weekProfit'], ',')))
    chk('A3', PEC == FACTS['weekPsc'], 'PEC 재계산 = facts.weekPsc',
        '%s ↔ %s' % (format(PEC, ','), format(FACTS['weekPsc'], ',')))
    chk('A4', str(q(PWD_DAY, 6)) == FACTS['weekWRaw'], 'PwD(일자단위·표기wD) = facts.weekWRaw',
        '%s ↔ %s' % (q(PWD_DAY, 6), FACTS['weekWRaw']))
    chk('A5', SUM_A_OPEN == FACTS['exec'] == L.BOOK, 'Σ Aᵢ(미회수) = facts.exec = BOOK',
        '%s' % format(SUM_A_OPEN, ','))
    chk('A6', str(q(WD_ALL, 6)) == FACTS['wRaw'], 'wD(대상정산금채권 전체) = facts.wRaw',
        '%s ↔ %s' % (q(WD_ALL, 6), FACTS['wRaw']))
    chk('A7', str(q(LR, 6)) == FACTS['sRaw'], 'LR = facts.sRaw',
        '%s ↔ %s' % (q(LR, 6), FACTS['sRaw']))
    chk('A8', len(FACTS['tyByDate']) == FACTS['ledgerDays'] == len(DAYROWS),
        'tyByDate 행수 = 원장 일자수', '%d' % len(DAYROWS))


# ══════════════════════════════════════════════════════════════════
# B. 계산 예시 9단계 — 원고 값이 원장 원천과 같은가 (축1)
# ══════════════════════════════════════════════════════════════════
def _step(i):
    return MS['calc']['steps'][i]


def sec_B():
    st = MS['calc']['steps']
    chk('B0', len(st) == 9, 'calc 단계 9줄', '%d줄' % len(st))
    chk('B1', num(st[0][1]) == D(PM), 'PM 원고 = 원장',
        '원고 %s ↔ 원장 %s' % (num(st[0][1]), PM))
    chk('B2', num(st[1][1]) == D(PA), 'PA 원고 = 원장',
        '원고 %s ↔ 원장 %s' % (num(st[1][1]), PA))
    chk('B3', num(st[2][1]) == D(PEC), 'PEC 원고 = 원장 (순현금 × 조회일수)',
        '원고 %s ↔ 원장 %s (%s × %d)' % (num(st[2][1]), PEC, format(L.CASH, ','), len(WEEK_DAYS)))
    chk('B4', num(st[3][1]) == q(PWD_DAY, 6), 'PwD 원고 = 원장 일자단위 값',
        '원고 %s ↔ 원장 %s' % (num(st[3][1]), q(PWD_DAY, 6)))
    chk('B5', num(st[4][1]) == q(PMR, 6), '① PMR = PM ÷ PA (6자리)',
        '원고 %s%% ↔ 재계산 %s%%' % (num(st[4][1]), q(PMR, 6)))
    chk('B6', num(st[5][1]) == q(TURN_DAY, 4), '② 365 ÷ PwD (4자리)',
        '원고 %s ↔ 재계산 %s' % (num(st[5][1]), q(TURN_DAY, 4)))
    chk('B7', nums(st[6][1])[0] == q(PYMR_DAY, 6), '③ PYMR (6자리)',
        '원고 %s%% ↔ 재계산 %s%%' % (nums(st[6][1])[0], q(PYMR_DAY, 6)))
    chk('B8', nums(st[6][1])[1] == q(PYMR_DAY, 2), '③ 화면 표기 (2자리)',
        '원고 %s%% ↔ 재계산 %s%%' % (nums(st[6][1])[1], q(PYMR_DAY, 2)))
    chk('B9', num(st[7][1]) == q(SHARE, 6), '④ PA ÷ (PA + PEC) (6자리)',
        '원고 %s ↔ 재계산 %s' % (num(st[7][1]), q(SHARE, 6)))
    chk('B10', nums(st[8][1])[0] == q(WPYMR_DAY, 6), '⑤ wPYMR (6자리)',
        '원고 %s%% ↔ 재계산 %s%%' % (nums(st[8][1])[0], q(WPYMR_DAY, 6)))
    chk('B11', nums(st[8][1])[1] == q(WPYMR_DAY, 2), '⑤ 화면 표기 (2자리)',
        '원고 %s%% ↔ 재계산 %s%%' % (nums(st[8][1])[1], q(WPYMR_DAY, 2)))


# ══════════════════════════════════════════════════════════════════
# C. 계산 예시 — 원고가 적은 표기값만으로 다음 줄이 재현되는가 (축2)
#    계산 예시는 사람이 따라 계산하라고 놓은 것이다. 적힌 대로 따라가서
#    적힌 답이 안 나오면 그 줄은 예시로서 닫히지 않는다.
# ══════════════════════════════════════════════════════════════════
def sec_C():
    st = MS['calc']['steps']
    p1, p2 = num(st[4][1]) / 100, num(st[5][1])              # ① 표기(%) · ② 표기
    p3 = nums(st[6][1])[0]
    p4 = num(st[7][1])
    p5 = nums(st[8][1])[0]
    pwd = num(st[3][1])
    got2 = q(DAYS / pwd, 4)
    chk('C1', got2 == p2, '② 를 원고 PwD 표기로 재현',
        '365 ÷ %s = %s ↔ 원고 %s' % (pwd, got2, p2))
    got3 = q(p1 * p2 * 100, 6)
    chk('C2', got3 == p3, '③ = ①표기 × ②표기 재현',
        '%s%% × %s = %s%% ↔ 원고 %s%% (차 %s%%p)' % (num(st[4][1]), p2, got3, p3, got3 - p3))
    got5 = q(p3 / 100 * p4 * 100, 6)
    chk('C3', got5 == p5, '⑤ = ③표기 × ④표기 재현',
        '%s%% × %s = %s%% ↔ 원고 %s%% (차 %s%%p)' % (p3, p4, got5, p5, got5 - p5))
    # 원고 PwD 표기를 온전히 따라간 사슬 (①은 풀정밀 · PwD 만 표기)
    ch3 = q(PMR * DAYS / pwd, 6)
    ch5 = q(PMR * DAYS / pwd * SHARE, 6)
    chk('C4', ch3 == p3, '③ 을 원고 PwD 표기 + 풀정밀 ① 로 재현',
        '%s%% ↔ 원고 %s%%' % (ch3, p3))
    chk('C5', ch5 == p5, '⑤ 를 원고 PwD 표기 + 풀정밀 ①④ 로 재현',
        '%s%% ↔ 원고 %s%% (차 %s%%p)' % (ch5, p5, ch5 - p5))


# ══════════════════════════════════════════════════════════════════
# D. 금액으로 되돌린 검산 4줄
# ══════════════════════════════════════════════════════════════════
def sec_D():
    kk = MS['calc']['검산']
    chk('D0', len(kk) == 4, '검산 4줄', '%d줄' % len(kk))
    p2 = num(MS['calc']['steps'][5][1])
    ann_doc = num(kk[0][1])
    got = q(D(PM) * p2, 0)
    chk('D1', got == ann_doc, '연환산 수익금 = PM × ②표기',
        '%s × %s = %s ↔ 원고 %s' % (PM, p2, got, ann_doc))
    g2 = q(ann_doc / D(PA) * 100, 6)
    chk('D2', g2 == num(kk[1][1]), '검산 PYMR = 연환산수익금 ÷ PA',
        '%s ÷ %s = %s%% ↔ 원고 %s%%' % (ann_doc, PA, g2, num(kk[1][1])))
    g3 = q(ann_doc / D(PA + PEC) * 100, 6)
    chk('D3', g3 == num(kk[2][1]), '검산 wPYMR = 연환산수익금 ÷ (PA + PEC)',
        '%s ÷ %s = %s%% ↔ 원고 %s%% (차 %s%%p · 분자를 원 단위로 끊어 6번째 자리가 뒤집힌다)'
        % (ann_doc, PA + PEC, g3, num(kk[2][1]), g3 - num(kk[2][1])))
    # 같은 분자·다른 분모 주장 — 두 길이 같은 값을 내는가 (반올림 없이)
    ann_raw = D(PM) * DAYS / PWD_DAY
    a = ann_raw / D(PA) * 100
    b = ann_raw / D(PA + PEC) * 100
    chk('D4', q(a, 6) == q(PYMR_DAY, 6) and q(b, 6) == q(WPYMR_DAY, 6),
        '검산 4번째 줄 — 같은 분자를 다른 분모로 나눈 것이 맞는가 (풀정밀)',
        'PM×365÷PwD = %s → ÷PA %s%% · ÷(PA+PEC) %s%%' % (q(ann_raw, 4), q(a, 6), q(b, 6)))
    chk('D5', q(ann_raw, 0) == ann_doc, '연환산 수익금 풀정밀 반올림 = 원고 표기',
        '%s → %s ↔ 원고 %s (버린 %s원이 D3 을 뒤집는 크기)'
        % (q(ann_raw, 4), q(ann_raw, 0), ann_doc, q(ann_raw - ann_doc, 4)))


# ══════════════════════════════════════════════════════════════════
# E. 낱개 산식 넷 — 원장 채권 전건으로 성립하는가
# ══════════════════════════════════════════════════════════════════
def formula_of(sym):
    for v in MS['vars']:
        if v['sym'] == sym:
            return v.get('formula')
    return None


def sec_E():
    n = len(L.RECEIVABLES)
    chk('E0', n > 0, '채권 대상 0건 아님', '%s건' % format(n, ','))

    # Aᵢ = 순지급액ᵢ × (1 − r)
    f = formula_of('Aᵢ')
    chk('E1', f is not None and '순지급액' in f and '1 − r' in f.replace('-', '−'),
        'Aᵢ 산식 문언', f)
    bad = [r for r in L.RECEIVABLES if L.ri(D(r['net']) * (D(1) - RATE)) != r['ai']]
    mx = max([abs(L.ri(D(r['net']) * (D(1) - RATE)) - r['ai']) for r in bad] or [0])
    chk('E2', not bad, 'Aᵢ = 순지급액 × (1 − 0.11%) 전건 재현',
        '불일치 %d / %s건 · 최대 %s원' % (len(bad), format(n, ','), mx))

    # Lᵢ = 미지급금ᵢ − 과지급금ᵢ
    chk('E3', formula_of('Lᵢ') is not None, 'Lᵢ 산식 존재', formula_of('Lᵢ'))
    okL = all(r['ded'] == max(0, r['unpaid'] - r['over']) for r in L.RECEIVABLES)
    negL = sum(1 for r in L.RECEIVABLES if r['unpaid'] - r['over'] < 0)
    chk('E4', okL, '원장 차감액 = max(0, Lᵢ) 전건',
        'Lᵢ<0 인 채권 %d건 — 클램프가 실제로 무는 자리 %s' % (negL, '있음' if negL else '0건'))

    # Mᵢ = 채권매입수수료ᵢ − max(0, Lᵢ)
    chk('E5', formula_of('Mᵢ') is not None, 'Mᵢ 산식 존재', formula_of('Mᵢ'))
    has_fee = any('채권매입수수료' in (v.get('formula') or '') or v['term'] == '채권매입수수료'
                  for v in MS['vars'] if v['sym'] not in ('Mᵢ',))
    chk('E6', has_fee, 'vars 29항이 `채권매입수수료ᵢ` 를 정의하는가 — Mᵢ 산식의 재료',
        '정의 0건이면 Mᵢ 를 낱개로 계산할 수 없다 (현재 %s)' % ('있음' if has_fee else '없음'))
    # 낱개 읽기 세 가지 중 원장 M(d-1) 과 맞는 것이 있는가
    d_fl = sum(day_FEE(d) - sum(L.fl(D(r['net']) * RATE) for r in DAYROWS[d]) for d in DAYROWS)
    d_ri = sum(day_FEE(d) - sum(L.ri(D(r['net']) * RATE) for r in DAYROWS[d]) for d in DAYROWS)
    wk_fl = sum(sum(L.fl(D(r['net']) * RATE) for r in DAYROWS[d]) - day_DED(d) for d in WEEK_DAYS)
    wk_ri = sum(sum(L.ri(D(r['net']) * RATE) for r in DAYROWS[d]) - day_DED(d) for d in WEEK_DAYS)
    chk('E7', d_fl == 0 or d_ri == 0,
        '건별 채권매입수수료 합 = 원장 하루 채권매입수수료 (낱개 읽기가 하루층과 닫히는가)',
        '내림읽기 편차 %s원 · 반올림읽기 편차 %s원 (원장은 하루 Σ순지급액에 요율을 곱해 내림한다)'
        % (format(d_fl, ','), format(d_ri, ',')))
    chk('E8', wk_fl == PM and wk_ri == PM,
        '건별 Mᵢ 합 = 원고 PM 61,175 (조회기간)',
        '내림읽기 %s (③ %s%%) · 반올림읽기 %s (③ %s%%) ↔ 원장 %s (③ %s%%)'
        % (format(wk_fl, ','), q(D(wk_fl) / D(PA) * 100 * DAYS / PWD_DAY, 2),
           format(wk_ri, ','), q(D(wk_ri) / D(PA) * 100 * DAYS / PWD_DAY, 2),
           format(PM, ','), q(PYMR_DAY, 2)))

    # Bᵢ = 순지급액ᵢ − max(0, Lᵢ)
    chk('E9', formula_of('Bᵢ') is not None, 'Bᵢ 산식 존재', formula_of('Bᵢ'))
    diffs = [(d, (day_NET(d) - day_DED(d)) - (day_A(d) + day_M(d))) for d in sorted(DAYROWS)]
    off = [x for x in diffs if x[1] != 0]
    chk('E10', not off, 'Σ Bᵢ (정의 그대로) = 원장·화면 상환액 A(d−1) + M(d−1)',
        '어긋난 날 %d / %d · 폭 %s ~ %s원 · 합 %s원'
        % (len(off), len(diffs), min(x[1] for x in diffs), max(x[1] for x in diffs),
           format(sum(x[1] for x in diffs), ',')))


# ══════════════════════════════════════════════════════════════════
# F. 하루치 산식 일곱 — 2026-08-27 · 2026-08-23
# ══════════════════════════════════════════════════════════════════
F_DATES = [date(2026, 8, 27), date(2026, 8, 23)]


def sec_F():
    chk('F0', len(F_DATES) == 2 and all(d in DAYROWS for d in F_DATES),
        '검산 일자 2건이 원장에 있다', ', '.join(L.ymd(d) for d in F_DATES))
    for d in F_DATES:
        k = L.ymd(d)
        tb = FACTS['tyByDate'][k]
        A, M, DEDv, FEEv = day_A(d), day_M(d), day_DED(d), day_FEE(d)
        Bdef = day_NET(d) - DEDv
        Bscr = A + M
        wraw, wdisp = day_wD_raw(d), day_wD_disp(d)
        MR = D(M) / D(A) * 100
        ymr_disp = MR * DAYS / wdisp
        ymr_raw = MR * DAYS / wraw
        chk('F.%s.A' % k, A == tb[2], 'A(d−1) = Σ Aᵢ (i ∈ d−1)',
            '%s ↔ 화면원천 %s' % (format(A, ','), format(tb[2], ',')))
        chk('F.%s.M' % k, M == tb[3], 'M(d−1) = Σ Mᵢ',
            '%s = 수수료 %s − 차감 %s ↔ 화면원천 %s'
            % (format(M, ','), format(FEEv, ','), format(DEDv, ','), format(tb[3], ',')))
        chk('F.%s.B' % k, Bdef == tb[4], 'B(d−1) = Σ Bᵢ (원고 정의 그대로)',
            '정의 %s ↔ 화면원천 %s (화면은 A+M = %s · 차 %s원)'
            % (format(Bdef, ','), format(tb[4], ','), format(Bscr, ','), Bdef - Bscr))
        chk('F.%s.MR' % k, q(MR, 6) == q(D(tb[3]) / D(tb[2]) * 100, 6),
            'MR(d−1) = M(d−1) ÷ A(d−1)', '%s%%' % q(MR, 6))
        chk('F.%s.wD' % k, str(wdisp) == tb[0], 'wD(d−1) = Σ(AᵢDᵢ) ÷ A(d−1)',
            'raw %s · 표기 %s ↔ 화면원천 %s' % (q(wraw, 6), wdisp, tb[0]))
        chk('F.%s.EC' % k, L.CASH * 1 == L.CASH,
            'EC(d−1) = 전일자 자정 잔액 — 원장에 일별 EC 원장이 없어 상수 %s 로 선다' % format(L.CASH, ','),
            '원고도 formula 없음(정의 문장만) · 기간 합 PEC 만 화면에 뜬다')
        chk('F.%s.YMR' % k, str(q(ymr_disp, 2)) == tb[1],
            'YMR(d−1) = MR × 365 ÷ wD(d−1)',
            '표기wD %s%% (표기 %s) · raw wD %s%% (표기 %s) ↔ 화면원천 %s'
            % (q(ymr_disp, 6), q(ymr_disp, 2), q(ymr_raw, 6), q(ymr_raw, 2), tb[1]))
    # 원고 산식은 wD(d−1) 을 raw 로 정의한다. 180일 축에서 표기 2자리가 갈리는가
    flip = []
    for d in sorted(DAYROWS):
        A, M = day_A(d), day_M(d)
        MR = D(M) / D(A) * 100
        if q(MR * DAYS / day_wD_raw(d), 2) != q(MR * DAYS / day_wD_disp(d), 2):
            flip.append(L.ymd(d))
    chk('F.flip', not flip,
        'YMR(d−1) — 원고 산식(raw wD)과 화면(표기 wD)이 표기 2자리에서 같은가',
        '갈리는 날 %d / %d일 · 예 %s' % (len(flip), len(DAYROWS), ', '.join(flip[:5])))


# ══════════════════════════════════════════════════════════════════
# G. 미회수 잔량 — Σ Aᵢ · wD · Yr · LR
#    원고 scopes 는 범위 표시가 없는 기호를 「미회수 잔량」으로 읽으라고 적었다.
#    그 읽기대로 계산해서 화면값이 나오는지 본다.
# ══════════════════════════════════════════════════════════════════
def sec_G():
    sc = dict((s['mark'], s) for s in MS['scopes'])
    chk('G0', '없음' in sc and '미회수' in sc['없음']['name'],
        'scopes — 범위 표시 없는 기호의 읽기', '%s · %s' % (sc['없음']['name'], sc['없음']['def']))
    chk('G1', SUM_A_OPEN == L.BOOK, 'Σ Aᵢ (미회수) = 화면 투자실행액',
        '%s · 미회수 %s건' % (format(SUM_A_OPEN, ','), format(len(OPEN), ',')))

    v = dict((x['sym'], x) for x in MS['vars'])
    chk('G2', 'wD' in v and v['wD']['formula'], 'wD 산식 존재', v['wD']['formula'])
    wtxt = (v['wD']['formula'] or '') + ' ' + (v['wD'].get('plain') or '')
    chk('G3', ('전체' in wtxt) or ('발생 기준' in wtxt),
        'wD 항이 모집단을 「대상정산금채권 전체 (발생 기준)」로 적는가 — 화면 열머리 툴팁이 대는 문언',
        '원고 wD 항 전문: %s' % wtxt.strip())
    chk('G4', str(q(WD_OPEN, 6)) == FACTS['wRaw'],
        'wD — 원고 범위 규약(미회수)대로 계산한 값이 화면 wD 인가',
        '미회수 %s (표기 %s) ↔ 화면 %s (표기 %s) · 차 %s일'
        % (q(WD_OPEN, 6), q(WD_OPEN, 2), FACTS['wRaw'], FACTS['w'], q(WD_OPEN - WD_ALL, 6)))
    chk('G5', str(q(WD_ALL, 6)) == FACTS['wRaw'],
        'wD — 원장·화면 모집단(대상정산금채권 전체)으로 계산한 값이 화면 wD 인가',
        '%s ↔ %s' % (q(WD_ALL, 6), FACTS['wRaw']))

    yr_open = RPCT * DAYS / q(WD_OPEN, 2)
    yr_disp = RPCT * DAYS / q(WD_ALL, 2)
    yr_raw = RPCT * DAYS / q(WD_ALL, 6)
    chk('G6', str(q(yr_open, 2)) == FACTS['ty'],
        'Yr — 원고 범위 규약(미회수 wD)대로 계산한 값이 화면 Ty 인가',
        '%s%% ↔ 화면 %s%%' % (q(yr_open, 2), FACTS['ty']))
    chk('G7', str(q(yr_disp, 2)) == FACTS['ty'] and str(q(yr_raw, 2)) == FACTS['ty'],
        'Yr — 전체 모집단 wD 로 계산하면 화면 Ty 가 나오는가',
        '표기wD %s%% · rawwD %s%% ↔ 화면 %s%%' % (q(yr_disp, 6), q(yr_raw, 6), FACTS['ty']))
    # Yr 분모 판별 — 원장이 raw 를 쓰는지 표기를 쓰는지
    chk('G8', str(L.TY_BOOK) == str(q(yr_disp, 2)) and q(yr_disp, 6) != q(yr_raw, 6),
        'Yr 분모 판별 — 원장은 표기 wD 를 쓴다 (두 기준이 6자리에서 갈려 판별력이 있다)',
        '표기 %s → %s%% · raw %s → %s%% · 차 %s%%p · 원장 TY %s'
        % (FACTS['w'], q(yr_disp, 6), FACTS['wRaw'], q(yr_raw, 6),
           q(yr_raw - yr_disp, 6), L.TY_BOOK))

    chk('G9', 'LR' in v and 'd−20' in v['LR']['formula'].replace('-', '−'),
        'LR 산식이 표본 구간을 달고 있는가', v['LR']['formula'])
    chk('G10', str(q(LR, 6)) == FACTS['sRaw'] and str(q(LR, 2)) == FACTS['s'],
        'LR = Σ Lᵢ ÷ Σ Aᵢ (표본 d−20 ~ d−11)',
        '%s%% (표기 %s%%) ↔ 화면 %s%% / %s%% · 표본 %s건 %s ~ %s'
        % (q(LR, 6), q(LR, 2), FACTS['sRaw'], FACTS['s'], format(len(SAMPLE), ','),
           L.ymd(L.SAMPLE[0]), L.ymd(L.SAMPLE[1])))
    chk('G11', len(SAMPLE) == FACTS['sampleReceivables'] and len(SAMPLE) > 0,
        'LR 표본 대상 0건 아님', '%s건' % format(len(SAMPLE), ','))


# ══════════════════════════════════════════════════════════════════
# H. 특히 볼 것 — PwD 두 길 · 상환액 두 길
# ══════════════════════════════════════════════════════════════════
def sec_H():
    v = dict((x['sym'], x) for x in MS['vars'])
    f = v['PwD']['formula']
    chk('H0', 'Aᵢ' in f and 'Dᵢ' in f, 'PwD 산식이 채권 단위 Σ(AᵢDᵢ) ÷ PA 로 적혀 있다', f)
    chk('H1', PWD_REC == PWD_DAYRAW,
        'PwD — 채권 단위와 「일자 단위 × raw wD」는 같은 값이다 (갈림의 원인은 집계 단위가 아니다)',
        '채권 %s ↔ 일자·raw %s' % (q(PWD_REC, 12), q(PWD_DAYRAW, 12)))
    chk('H2', PWD_REC == PWD_DAY,
        'PwD — 원고 산식(채권 단위)과 원장·화면 값(일자 단위 × 표기 wD)이 같은가',
        '원고산식 %s ↔ 원장값 %s · 차 %s일 (원인은 wD(d−1) 을 소수 2자리로 끊는 것)'
        % (q(PWD_REC, 6), q(PWD_DAY, 6), q(PWD_DAY - PWD_REC, 6)))
    chk('H3', q(PYMR_REC, 2) == q(PYMR_DAY, 2),
        'PwD 두 길이 ③ 화면 표기 2자리를 뒤집는가',
        '원고산식 %s%% → %s%% · 원장 %s%% → %s%%'
        % (q(PYMR_REC, 6), q(PYMR_REC, 2), q(PYMR_DAY, 6), q(PYMR_DAY, 2)))
    chk('H4', q(WPYMR_REC, 2) == q(WPYMR_DAY, 2),
        'PwD 두 길이 ⑤ 화면 표기 2자리를 뒤집는가',
        '원고산식 %s%% → %s%% · 원장·화면 %s%% → %s%%'
        % (q(WPYMR_REC, 6), q(WPYMR_REC, 2), q(WPYMR_DAY, 6), q(WPYMR_DAY, 2)))

    diffs = [(day_NET(d) - day_DED(d)) - (day_A(d) + day_M(d)) for d in sorted(DAYROWS)]
    chk('H5', all(x == 0 for x in diffs),
        '상환액 두 길 — Σ(순지급액 − max(0,Lᵢ)) 과 A(d−1) + M(d−1) 이 같은가',
        '어긋난 날 %d / %d · 하루 %s ~ %s원 · 180일 합 %s원'
        % (sum(1 for x in diffs if x), len(diffs), min(diffs), max(diffs),
           format(sum(diffs), ',')))
    wk = sum((day_NET(d) - day_DED(d)) - (day_A(d) + day_M(d)) for d in WEEK_DAYS)
    chk('H6', wk == 0, '상환액 두 길 — 조회기간 7일 합이 같은가',
        '정의 %s ↔ 화면 %s · 차 %s원'
        % (format(sum(day_NET(d) - day_DED(d) for d in WEEK_DAYS), ','),
           format(sum(day_A(d) + day_M(d) for d in WEEK_DAYS), ','), wk))
    chk('H7', all(FACTS['tyByDate'][L.ymd(d)][4] == day_A(d) + day_M(d) for d in DAYROWS),
        '화면이 쓰는 갈래는 A(d−1) + M(d−1) 이다 (180일 전건)',
        '화면원천 tyByDate 상환액 = 투자실행금 + 투자수익')

    # 원고가 검사 도중 바뀌면 판정이 두 판을 섞는다 — 같은 판을 봤는지 못 박는다.
    chk('H8', hashlib.md5(io.open(MANUSCRIPT, 'rb').read()).hexdigest() == MS_MD5,
        '원고가 검사 도중 바뀌지 않았다 (md5)', MS_MD5)


# ══════════════════════════════════════════════════════════════════
# I. 화면 대조 — 헤드리스 크롬으로 실제 띄우고 렌더된 글자를 읽는다
# ══════════════════════════════════════════════════════════════════
NODE_JS = r'''
const http=require('http'),fs=require('fs'),os=require('os'),path=require('path'),{spawn}=require('child_process');
const CHROME=process.env.FT_CHROME, BASE=process.env.FT_BASE, DPORT=+process.env.FT_DPORT;
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let id=0, ws, pend=new Map(), errs=[];
function send(m,p){const i=++id;ws.send(JSON.stringify({id:i,method:m,params:p||{}}));
  return new Promise((res,rej)=>pend.set(i,{res,rej}));}
async function ev(x){const r=await send('Runtime.evaluate',
  {expression:'(function(){'+x+'})()',returnByValue:true,awaitPromise:true});
  if(r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails));return r.result.value;}
const EXTRACT=`
  var vis=function(e){ if(!e) return false; var r=e.getBoundingClientRect();
    return r.width>0 && r.height>0 && getComputedStyle(e).visibility!=='hidden'; };
  var txt=function(e){ return e ? (e.innerText||'').replace(/\\s+/g,' ').trim() : null; };
  var cards=[].map.call(document.querySelectorAll('.summary-card,.stat'),function(c){
    return {label:txt(c.querySelector('.summary-label')),
            value:txt(c.querySelector('.summary-value')),
            sub:txt(c.querySelector('.summary-sub')),
            vis:vis(c.querySelector('.summary-value')||c)};});
  var tables=[].map.call(document.querySelectorAll('table.tbl'),function(t){
    return {head:[].map.call(t.querySelectorAll('thead th'),function(h){
              var a=h.querySelector('.tip-anchor'); return txt(a||h);}),
            body:[].map.call(t.querySelectorAll('tbody tr'),function(r){
              return [].map.call(r.children,function(c){return txt(c);});}),
            foot:[].map.call(t.querySelectorAll('tfoot tr'),function(r){
              return [].map.call(r.children,function(c){return txt(c);});}),
            vis:vis(t)};});
  var split=[].map.call(document.querySelectorAll('.ty-split > div'),function(d){
    return {label:txt(d.querySelector('.tip-anchor')), value:txt(d.querySelector('.summary-value')),
            vis:vis(d.querySelector('.summary-value'))};});
  return {w:innerWidth,h:innerHeight,cards:cards,tables:tables,split:split,
          title:document.title};`;
(async()=>{
  const prof=fs.mkdtempSync(path.join(os.tmpdir(),'ft-'));
  const ch=spawn(CHROME,['--headless=new','--remote-debugging-port='+DPORT,
    '--user-data-dir='+prof,'--no-first-run','--no-default-browser-check','--disable-gpu',
    '--window-size=1440,'+process.env.FT_WINH,'about:blank'],{stdio:'ignore'});
  let t=null;
  for(let i=0;i<80&&!t;i++){ await sleep(250);
    try{ t=await new Promise((res,rej)=>{http.get({host:'127.0.0.1',port:DPORT,path:'/json'},
      r=>{let d='';r.on('data',c=>d+=c);r.on('end',()=>res(JSON.parse(d)));}).on('error',rej);});}
    catch(e){t=null;} }
  if(!t) { console.log(JSON.stringify({error:'chrome 붙지 않음'})); process.exit(0); }
  ws=new WebSocket(t.find(x=>x.type==='page').webSocketDebuggerUrl);
  await new Promise(r=>ws.addEventListener('open',r));
  ws.addEventListener('message',e=>{const m=JSON.parse(e.data);
    if(m.id&&pend.has(m.id)){const {res,rej}=pend.get(m.id);pend.delete(m.id);
      m.error?rej(new Error(JSON.stringify(m.error))):res(m.result);}
    else if(m.method==='Runtime.exceptionThrown') errs.push('exception '+JSON.stringify(m.params).slice(0,300));
    else if(m.method==='Runtime.consoleAPICalled'&&m.params.type==='error')
      errs.push('console '+JSON.stringify(m.params.args).slice(0,300));});
  await send('Page.enable'); await send('Runtime.enable');
  const out={pages:{},errs:errs};
  for(const p of ['invest-assets.html','invest-profit.html']){
    await send('Page.navigate',{url:BASE+'/'+p}); await sleep(900);
    out.pages[p]=await ev(EXTRACT);
  }
  // 실제 조작 — 투자자산 대비 툴팁을 hover 해서 PSA·PSC 가 화면에 뜨는지 본다
  await send('Page.navigate',{url:BASE+'/invest-profit.html'}); await sleep(900);
  const box=await ev(`var a=[].filter.call(document.querySelectorAll('.tip-anchor'),
      function(x){return x.textContent.indexOf('투자자산 대비')>=0;})[0];
    if(!a) return null; var r=a.getBoundingClientRect();
    return {x:r.left+r.width/2,y:r.top+r.height/2};`);
  if(box){
    await send('Input.dispatchMouseEvent',{type:'mouseMoved',x:box.x,y:box.y});
    await sleep(500);
    out.hover=await ev(`var a=[].filter.call(document.querySelectorAll('.tip-anchor'),
        function(x){return x.textContent.indexOf('투자자산 대비')>=0;})[0];
      var p=a.parentNode.querySelector('.tip-panel'); var r=p.getBoundingClientRect();
      return {text:(p.innerText||p.textContent).replace(/\\s+/g,' ').trim(),
              w:r.width,h:r.height,opacity:getComputedStyle(p).opacity,
              vis:getComputedStyle(p).visibility};`);
  } else out.hover=null;
  out.errs=errs;
  console.log(JSON.stringify(out));
  ws.close(); ch.kill(); process.exit(0);
})().catch(e=>{console.log(JSON.stringify({error:String(e)}));process.exit(0);});
'''


def render_screens():
    import http.server
    import socketserver
    import functools
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=SCREEN_REPO)
    handler.log_message = lambda *a, **k: None
    srv = socketserver.TCPServer(('127.0.0.1', 0), handler)
    srv.allow_reuse_address = True
    port = srv.server_address[1]
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    env = dict(os.environ)
    env.update(FT_CHROME=CHROME, FT_BASE='http://127.0.0.1:%d' % port,
               FT_DPORT=str(9700 + os.getpid() % 90), FT_WINH=str(WIN_H))
    p = subprocess.run(['node', '-e', NODE_JS], capture_output=True, text=True, env=env, timeout=240)
    srv.shutdown()
    line = [x for x in p.stdout.splitlines() if x.startswith('{')]
    if not line:
        raise RuntimeError('node 출력 없음: %s / %s' % (p.stdout[-400:], p.stderr[-600:]))
    return json.loads(line[-1])


def only(s):
    return re.sub(r'[^\d.,\-]', '', s or '').replace(',', '')


def sec_I():
    out = render_screens()
    SCREEN.update(out)
    chk('I0', not out.get('error'), '헤드리스 크롬 기동', out.get('error') or 'OK')
    if out.get('error'):
        return
    pa = out['pages']['invest-assets.html']
    pp = out['pages']['invest-profit.html']
    chk('I1', pa['w'] == VIEW_W and pa['h'] == VIEW_H,
        '뷰포트 %d×%d (macOS 87px 보정)' % (VIEW_W, VIEW_H), '%d×%d' % (pa['w'], pa['h']))
    chk('I2', not out.get('errs'), '콘솔 에러 0건', str(out.get('errs'))[:300])

    # ── 투자 자산 화면
    ca = dict((c['label'], c) for c in pa['cards'] if c['label'])
    chk('I3', len(ca) >= 4, '투자 자산 요약 카드 대상 0건 아님', '%d장' % len(ca))
    chk('I4', only(ca['투자실행액']['value']) == str(SUM_A_OPEN),
        '화면 투자실행액 = Σ Aᵢ(미회수)', '%s ↔ %s' % (ca['투자실행액']['value'], SUM_A_OPEN))
    chk('I5', only(ca['순현금']['value']) == str(L.CASH),
        '화면 순현금 = EC', '%s ↔ %s' % (ca['순현금']['value'], L.CASH))
    chk('I6', only(ca['투자자산']['value']) == str(SUM_A_OPEN + L.CASH),
        '화면 투자자산 = Σ Aᵢ + EC', ca['투자자산']['value'])
    chk('I7', only(ca['Ty수익율']['value']) == FACTS['ty'],
        '화면 Ty수익율 = Yr', '%s ↔ %s' % (ca['Ty수익율']['value'], FACTS['ty']))
    chk('I8', FACTS['w'] in (ca['Ty수익율']['sub'] or ''),
        '화면 Ty 부제가 표기 wD 를 댄다 (Yr 분모가 표기 갈래임을 화면이 스스로 적는다)',
        ca['Ty수익율']['sub'])
    hdr = pa['tables'][0]['head']
    chk('I9', any('W금융일수' in h for h in hdr),
        '투자 자산 현황표에 W금융일수 열이 있다', str(hdr))
    row0 = pa['tables'][0]['body'][0]
    chk('I10', only(row0[2]) == FACTS['w'] and only(row0[4]) == FACTS['ty'],
        '현황표 투자실행액 행 W·Ty = 원장', str(row0))
    chk('I11', only(row0[3]) == FACTS['s'], '현황표 S입금부족율 = LR 표기', row0[3])

    # ── 투자 수익 화면
    cp = dict((c['label'], c) for c in pp['cards'] if c['label'])
    chk('I12', len(cp) >= 4, '투자 수익 카드 대상 0건 아님', '%d장' % len(cp))
    chk('I13', only(cp['투자실행금']['value']) == str(PA),
        '화면 투자실행금 = 원고 PA', '%s ↔ %s' % (cp['투자실행금']['value'], PA))
    chk('I14', only(cp['투자수익']['value']) == str(PM),
        '화면 투자수익 = 원고 PM', '%s ↔ %s' % (cp['투자수익']['value'], PM))
    sp = dict((s['label'], s) for s in pp['split'])
    st = MS['calc']['steps']
    chk('I15', only(sp['투자실행금액 대비']['value']) == str(nums(st[6][1])[1]),
        '화면 ③ = 원고 「화면 3.99%」', '%s ↔ %s' % (sp['투자실행금액 대비']['value'], nums(st[6][1])[1]))
    chk('I16', only(sp['투자자산 대비']['value']) == str(nums(st[8][1])[1]),
        '화면 ⑤ = 원고 「화면 2.24%」', '%s ↔ %s' % (sp['투자자산 대비']['value'], nums(st[8][1])[1]))
    chk('I17', only(sp['투자자산 대비']['value']) == str(q(WPYMR_REC, 2)),
        '화면 ⑤ = 원고 PwD 산식(채권 단위)으로 계산한 값',
        '화면 %s ↔ 원고산식 %s (원장 %s)'
        % (sp['투자자산 대비']['value'], q(WPYMR_REC, 2), q(WPYMR_DAY, 2)))

    tb = [t for t in pp['tables'] if t['body'] and len(t['body'][0]) == 6]
    chk('I18', tb and len(tb[0]['body']) == len(WEEK_DAYS),
        '일별 투자수익 표 %d행 대상 0건 아님' % len(WEEK_DAYS),
        '%d행' % (len(tb[0]['body']) if tb else 0))
    body = tb[0]['body']
    bad_b, bad_y, bad_yraw = [], [], []
    for r in body:
        d = date(*map(int, r[0].split('-')))
        if only(r[1]) != str(day_A(d) + day_M(d)):
            bad_b.append((r[0], r[1]))
        MR = D(day_M(d)) / D(day_A(d)) * 100
        if only(r[5]) != str(q(MR * DAYS / day_wD_disp(d), 2)):
            bad_y.append((r[0], r[5]))
        if only(r[5]) != str(q(MR * DAYS / day_wD_raw(d), 2)):
            bad_yraw.append((r[0], r[5], str(q(MR * DAYS / day_wD_raw(d), 2))))
    chk('I19', not bad_b, '일별 표 상환액 = A(d−1) + M(d−1) 전행', str(bad_b))
    chk('I20', not bad_y, '일별 표 Ty수익율 = 표기 wD 갈래 전행', str(bad_y))
    chk('I21', not bad_yraw,
        '일별 표 Ty수익율 = 원고 산식(raw wD) 전행',
        '어긋난 행 %d / %d — %s' % (len(bad_yraw), len(body),
                                 '; '.join('%s 화면 %s ↔ 원고산식 %s' % x for x in bad_yraw)))
    foot = tb[0]['foot'][0]
    chk('I22', only(foot[2]) == str(PA) and only(foot[3]) == str(PM),
        '일별 표 합계행 = PA · PM', str(foot))
    chk('I23', only(foot[1]) == str(PA + PM),
        '일별 표 합계 상환액 = PA + PM (화면 갈래)',
        '%s ↔ %s (원고 정의 Σ Bᵢ 는 %s)'
        % (foot[1], PA + PM,
           format(sum(day_NET(d) - day_DED(d) for d in WEEK_DAYS), ',')))
    chk('I24', only(foot[4]) == str(q(PWD_DAY, 2)),
        '일별 표 합계 W금융일수 = PwD 표기', '%s ↔ %s' % (foot[4], q(PWD_DAY, 2)))

    h = out.get('hover')
    chk('I25', h and h['w'] > 0 and h['h'] > 0 and h['vis'] != 'hidden',
        'hover — 투자자산 대비 툴팁이 실제로 열린다', str(h)[:160] if h else 'None')
    chk('I26', h and format(PA, ',') in h['text'] and format(PEC, ',') in h['text'],
        'hover 툴팁이 PSA = PA · PSC = PEC 를 그대로 댄다',
        (h or {}).get('text', '')[:220])


# ══════════════════════════════════════════════════════════════════
# J. 판별력 자기시험 — 원고 사본을 틀리게 만들면 종료코드 1 이 나는가
# ══════════════════════════════════════════════════════════════════
def run_child(path):
    env = dict(os.environ)
    env.update(FT_CHILD='1', FT_NOSCREEN='1', FT_MANUSCRIPT=path)
    p = subprocess.run([sys.executable, os.path.abspath(__file__), '--json'],
                       capture_output=True, text=True, env=env, timeout=900)
    line = [x for x in p.stdout.splitlines() if x.startswith('{"rc"')]
    if not line:
        raise RuntimeError('자식 출력 없음: %s' % (p.stdout[-500:] + p.stderr[-500:]))
    return p.returncode, json.loads(line[-1])


def sec_J():
    real = MS_RAW
    md5_before = MS_MD5
    tmp = tempfile.mkdtemp(prefix='ft-self-')
    clean = os.path.join(tmp, 'clean.json')
    io.open(clean, 'wb').write(real)
    rc0, r0 = run_child(clean)
    base_fail = set(r0['fails'])
    chk('J1', rc0 == r0['rc'] and r0['n'] > 0,
        '자기시험 — 무변조 사본에서 판정 건수 0 아님',
        '판정 %d건 · FAIL %d건 · 종료코드 %d' % (r0['n'], len(base_fail), rc0))

    cases = [
        ('calc.PA',   lambda m: m['calc']['steps'].__setitem__(
            1, [m['calc']['steps'][1][0], '179,970,918원']), 'B2'),
        ('calc.③',    lambda m: m['calc']['steps'].__setitem__(
            6, [m['calc']['steps'][6][0], '3.991319%   화면 3.99%']), 'B7'),
        ('검산.연환산', lambda m: m['calc']['검산'].__setitem__(
            0, [m['calc']['검산'][0][0], '7,183,212원']), 'D1'),
        ('vars.Aᵢ',   lambda m: [v for v in m['vars'] if v['sym'] == 'Aᵢ'][0].__setitem__(
            'formula', 'Aᵢ = 순지급액ᵢ × (1 + r)'), 'E1'),
        ('vars.LR',   lambda m: [v for v in m['vars'] if v['sym'] == 'LR'][0].__setitem__(
            'formula', 'LR = Σ Lᵢ ÷ Σ Aᵢ'), 'G9'),
    ]
    caught = 0
    for name, mut, expect in cases:
        m = json.loads(real.decode('utf-8'))
        mut(m)
        p = os.path.join(tmp, 'mut_%s.json' % re.sub(r'\W', '_', name))
        io.open(p, 'w', encoding='utf-8').write(json.dumps(m, ensure_ascii=False))
        rc, r = run_child(p)
        new = set(r['fails']) - base_fail
        ok = rc == 1 and expect in new
        caught += 1 if ok else 0
        chk('J.%s' % name, ok, '판별력 — %s 를 한 자리 틀리면 %s 가 FAIL 로 잡히는가' % (name, expect),
            '종료코드 %d · 새로 난 FAIL %s' % (rc, sorted(new) or '없음'))
    chk('J2', caught == len(cases), '판별력 시험 전건 통과',
        '%d / %d' % (caught, len(cases)))
    md5_after = hashlib.md5(io.open(MANUSCRIPT, 'rb').read()).hexdigest()
    chk('J3', md5_before == md5_after, '실물 원고 무변조 (md5)',
        '%s ↔ %s' % (md5_before, md5_after))


# ══════════════════════════════════════════════════════════════════
def main():
    section('A', sec_A)
    section('B', sec_B)
    section('C', sec_C)
    section('D', sec_D)
    section('E', sec_E)
    section('F', sec_F)
    section('G', sec_G)
    section('H', sec_H)
    if not NOSCREEN:
        section('I', sec_I)
    if not CHILD and not NOSCREEN:
        section('J', sec_J)

    fails = [x for x in R if not x[1]]
    if '--json' not in sys.argv:
        print('원고 %s' % MANUSCRIPT)
        print('원장 채권 %s건 · 일자 %d일 · 기준일 %s'
              % (format(len(L.RECEIVABLES), ','), len(DAYROWS), L.ymd(ASOF)))
        print('')
        for cid, ok, title, detail in R:
            print('%s %-11s %s' % ('PASS' if ok else 'FAIL', cid, title))
            if detail:
                print('%18s%s' % ('', detail))
        print('')
        print('판정 %d건 · PASS %d · FAIL %d' % (len(R), len(R) - len(fails), len(fails)))
        if fails:
            print('FAIL 목록 — %s' % ', '.join(x[0] for x in fails))
    # 대상 0건이면 통과시키지 않는다
    if not R:
        print('판정 0건 — 검사가 돌지 않았다')
        sys.exit(1)
    rc = 1 if fails else 0
    if '--json' in sys.argv:
        print(json.dumps({'rc': rc, 'n': len(R), 'fails': [x[0] for x in fails]},
                         ensure_ascii=False))
    sys.exit(rc)


if __name__ == '__main__':
    main()
