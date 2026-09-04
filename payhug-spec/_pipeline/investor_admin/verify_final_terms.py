# -*- coding: utf-8 -*-
"""확정 원고 `final_terms.json` 의 산식·값 전건 재계산 검증기.

대상   payhug-spec/_pipeline/investor_admin/final_terms.json  (vars 30항 · calc 9단계 + 검산 4줄)
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
    if L.FIRST_DUE <= _r['due'] <= L.LAST_DUE:
        DAYROWS.setdefault(_r['due'], []).append(_r)

_wf, _wt = L.facts()['weekFrom'], L.facts()['weekTo']        # 원장 파생 — 손으로 적지 않는다
WEEK_FROM = date(*map(int, _wf.split('-')))
WEEK_TO   = date(*map(int, _wt.split('-')))
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


def day_wD_6(d):
    """계산에 쓰는 값 — 소수 일곱째에서 반올림해 여섯째까지 (dm_0901 규칙 1)."""
    return q(day_wD_raw(d), 6)


def day_wD_disp(d):
    return q(day_wD_raw(d), 2)


def day_B(d):
    """상환액 — 대표 정의서 [2번 이미지] 「순지급액 - max(0, 미지급금-과지급금)」의 합."""
    return day_NET(d) - day_DED(d)


def day_BAM(d):
    """나눠 더하는 길 — 원 단위로 두 번 끊긴다 (dm_0901 규칙 2가 물리는 자리)."""
    return day_A(d) + day_M(d)


PA = sum(day_A(d) for d in WEEK_DAYS)
PM = sum(day_M(d) for d in WEEK_DAYS)
PB = sum(day_B(d) for d in WEEK_DAYS)
PEC = L.CASH * len(WEEK_DAYS)
# ⑤ 분모 — Σ( A_i × D_i ) + PEC. Σ( A_i × D_i ) 는 채권이 묶여 있던 원·일 (채권 단위·끊는 자리 없음).
SAD = sum(r['ai'] * r['di'] for d in WEEK_DAYS for r in DAYROWS[d])
# PwD 세 길 — 원장·화면·원고는 여섯 자리 wD(d−1) 가중(= 채권 단위와 같은 값),
# 2자리로 끊어 가중하면 갈린다.
PWD_DAY = q(sum(day_wD_6(d) * D(day_A(d)) for d in WEEK_DAYS) / D(PA), 6)
PWD_REC = q(D(sum(r['ai'] * r['di'] for d in WEEK_DAYS for r in DAYROWS[d])) / D(PA), 6)
PWD_DAYRAW = sum(day_wD_raw(d) * D(day_A(d)) for d in WEEK_DAYS) / D(PA)
PWD_2DP = sum(day_wD_disp(d) * D(day_A(d)) for d in WEEK_DAYS) / D(PA)

# PMR 도 6자리에서 끊고 그 값을 다음 계산에 넣는다 — 2026-09-02 기획 지시로
# MR·PMR 예외를 철회했다. 원장 daily_ledger.facts() 의 wk_ty 와 같은 단계다.
PMR = q(D(PM) / D(PA) * 100, 6)                              # %
TURN_DAY = q(DAYS / PWD_DAY, 6)
PYMR_DAY = q(PMR * DAYS / PWD_DAY, 6)
SHARE = q(D(SAD) / D(SAD + PEC), 6)
WPYMR_DAY = q(PYMR_DAY * D(SAD) / D(SAD + PEC), 6)
PYMR_2DP = q(PMR * DAYS / PWD_2DP, 6)
WPYMR_2DP = q(PYMR_2DP * D(SAD) / D(SAD + PEC), 6)
PYMR_REC = q(PMR * DAYS / PWD_REC, 6)
WPYMR_REC = q(PYMR_REC * D(SAD) / D(SAD + PEC), 6)

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
    chk('A4', str(PWD_DAY) == FACTS['weekWRaw'],
        'PwD(일자단위 · 여섯 자리 wD 가중) = facts.weekWRaw',
        '%s ↔ %s (2자리로 끊어 가중하면 %s)' % (PWD_DAY, FACTS['weekWRaw'], q(PWD_2DP, 6)))
    chk('A5', SUM_A_OPEN == FACTS['exec'] == L.BOOK, 'Σ A_i(미회수) = facts.exec = BOOK',
        '%s' % format(SUM_A_OPEN, ','))
    chk('A6', str(q(WD_ALL, 6)) == FACTS['wRaw'], 'wD(대상정산금채권 전체) = facts.wRaw',
        '%s ↔ %s' % (q(WD_ALL, 6), FACTS['wRaw']))
    chk('A7', str(q(LR, 6)) == FACTS['sRaw'], 'LR = facts.sRaw',
        '%s ↔ %s' % (q(LR, 6), FACTS['sRaw']))
    chk('A8', len(FACTS['tyByDate']) == FACTS['ledgerDays'] == len(DAYROWS),
        'tyByDate 행수 = 원장 일자수', '%d' % len(DAYROWS))
    chk('A9', PB == FACTS['weekRepay'], 'PB 재계산 = facts.weekRepay (원문 정의 한 줄로)',
        '%s ↔ %s (A+M 로 나눠 더하면 %s · 차 %s원)'
        % (format(PB, ','), format(FACTS['weekRepay'], ','),
           format(sum(day_BAM(d) for d in WEEK_DAYS), ','),
           PB - sum(day_BAM(d) for d in WEEK_DAYS)))
    chk('A10', str(q(PYMR_DAY, 2)) == FACTS['weekTy']
        and str(q(WPYMR_DAY, 2)) == FACTS['weekTyAsset'],
        'PY_a · PY_t 재계산 표기 = facts.weekTy · weekTyAsset',
        '%s%% → %s%% ↔ %s%%  ·  %s%% → %s%% ↔ %s%%'
        % (PYMR_DAY, q(PYMR_DAY, 2), FACTS['weekTy'],
           WPYMR_DAY, q(WPYMR_DAY, 2), FACTS['weekTyAsset']))


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
    chk('B4', num(st[3][1]) == PWD_DAY, 'PwD 원고 = 원장 값 (여섯 자리)',
        '원고 %s ↔ 원장 %s' % (num(st[3][1]), PWD_DAY))
    chk('B5', num(st[4][1]) == q(PMR, 6), '① PMR = PM ÷ PA (6자리)',
        '원고 %s%% ↔ 재계산 %s%%' % (num(st[4][1]), q(PMR, 6)))
    chk('B6', num(st[5][1]) == TURN_DAY, '② 365 ÷ PwD (6자리)',
        '원고 %s ↔ 재계산 %s' % (num(st[5][1]), TURN_DAY))
    chk('B7', nums(st[6][1])[0] == PYMR_DAY, '③ PY_MR (6자리)',
        '원고 %s%% ↔ 재계산 %s%%' % (nums(st[6][1])[0], PYMR_DAY))
    chk('B8', nums(st[6][1])[1] == q(PYMR_DAY, 2), '③ 화면 표기 (2자리)',
        '원고 %s%% ↔ 재계산 %s%%' % (nums(st[6][1])[1], q(PYMR_DAY, 2)))
    chk('B9', num(st[7][1]) == SHARE, '④ Σ( A_i × D_i ) ÷ ( Σ( A_i × D_i ) + PEC ) (6자리)',
        '원고 %s ↔ 재계산 %s' % (num(st[7][1]), SHARE))
    chk('B10', nums(st[8][1])[0] == WPYMR_DAY, '⑤ PY_t (6자리)',
        '원고 %s%% ↔ 재계산 %s%%' % (nums(st[8][1])[0], WPYMR_DAY))
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
    got2 = q(DAYS / pwd, 6)
    chk('C1', got2 == p2, '② 를 원고 PwD 표기로 재현 (6자리)',
        '365 ÷ %s = %s ↔ 원고 %s' % (pwd, got2, p2))
    # ③ 은 ① × ② 로 간다 — PMR 을 6자리로 끊고 그 값을 다음 계산에 넣는다(dm_0901 규칙 1).
    # 한 줄로 되짚으면 끊는 단계가 빠져 여섯째 자리가 갈린다.
    got3 = q(p1 * p2 * 100, 6)
    chk('C2', got3 == p3, '③ = ① × ② 로 재현 (6자리로 끊어 가는 길)',
        '%s%% × %s = %s%% ↔ 원고 %s%% (한 줄로 되짚으면 %s%%)'
        % (p1, p2, got3, p3, q(D(PM) / D(PA) * 100 * DAYS / pwd, 6)))
    got5 = q(p3 * D(SAD) / D(SAD + PEC), 6)
    alt5 = q(p3 * D(PA) * pwd / (D(PA) * pwd + PEC), 6)
    chk('C3', got5 == p5, '⑤ = ③표기 × Σ( A_i × D_i ) ÷ ( Σ( A_i × D_i ) + PEC ) 재현',
        '%s%% × %s ÷ %s = %s%% ↔ 원고 %s%% (④표기로 끊어 가면 %s%% · PA × PD표기 %s 로 가면 %s%%)'
        % (p3, format(SAD, ','), format(SAD + PEC, ','), got5, p5, q(p3 / 100 * p4 * 100, 6),
           q(D(PA) * pwd, 2), alt5))
    # 원고 PwD 표기를 온전히 따라간 사슬 (①은 풀정밀 · PwD 만 표기)
    ch3 = q(PMR * DAYS / pwd, 6)
    ch5 = q(q(PMR * DAYS / pwd, 6) * D(SAD) / D(SAD + PEC), 6)
    chk('C4', ch3 == p3, '③ 을 원고 PwD 표기 + 6자리 ① 로 재현',
        '%s%% ↔ 원고 %s%%' % (ch3, p3))
    chk('C5', ch5 == p5, '⑤ 를 원고 PwD 표기 + 6자리 ①④ 로 재현',
        '%s%% ↔ 원고 %s%% (차 %s%%p)' % (ch5, p5, ch5 - p5))


# ══════════════════════════════════════════════════════════════════
# D. 금액으로 되돌린 검산 4줄
# ══════════════════════════════════════════════════════════════════
def sec_D():
    kk = MS['calc']['검산']
    chk('D0', len(kk) == 4, '검산 4줄', '%d줄' % len(kk))
    p2 = num(MS['calc']['steps'][5][1])
    p3 = nums(MS['calc']['steps'][6][1])[0]
    p5 = nums(MS['calc']['steps'][8][1])[0]
    ann_doc = num(kk[0][1])
    # ③ 에서 되짚는다 — PM × ② 로 내면 PMR 을 6자리로 끊기 전 값이 들어가 ③ 과 갈린다.
    got = q(p3 * D(PA) / 100, 0)
    chk('D1', got == ann_doc, '연환산 수익금 = ③ × PA ÷ 100',
        '%s%% × %s ÷ 100 = %s ↔ 원고 %s' % (p3, PA, got, ann_doc))
    g2 = q(ann_doc / D(PA) * 100, 6)
    chk('D2', g2 == num(kk[1][1]), '검산 PYMR = 연환산수익금 ÷ PA',
        '%s ÷ %s = %s%% ↔ 원고 %s%%' % (ann_doc, PA, g2, num(kk[1][1])))
    # ⑤ = ann × PD ÷ ( Σ( A_i × D_i ) + PEC ) = ann ÷ ( ( Σ( A_i × D_i ) + PEC ) ÷ PD ).
    # PD 는 SAD ÷ PA 그대로(끊지 않는다). 분자 ann 은 ③ 에서 되짚은 원 단위 값이라
    # PM × 365 를 바로 넣으면 ① 을 여섯 자리로 끊은 만큼 ⑤ 와 갈린다 (3.299703% ↔ 3.299662%).
    den_t = D(PA) + D(PEC) * D(PA) / D(SAD)
    g3 = q(ann_doc / den_t * 100, 6)
    chk('D3', g3 == num(kk[2][1]), '검산 PY_t = 연환산수익금 ÷ ( ( Σ( A_i × D_i ) + PEC ) ÷ PD )',
        '%s ÷ %s = %s%% ↔ 원고 %s%% (차 %s%%p · 분자를 원 단위로 끊어 6번째 자리가 뒤집힐 수 있다)'
        % (ann_doc, q(den_t, 0), g3, num(kk[2][1]), g3 - num(kk[2][1])))
    # 같은 분자·다른 분모 주장 — 두 길이 같은 값을 내는가 (반올림 없이)
    ann_raw = D(PM) * DAYS / PWD_DAY
    a = ann_raw / D(PA) * 100
    b = q(q(a, 6) * D(SAD) / D(SAD + PEC), 6)
    # ③ 에서 되짚었으므로 검산 세 줄이 ③⑤ 와 정확히 맞물린다.
    d2 = q(D(ann_doc) / D(PA) * 100, 6)
    d3 = q(D(ann_doc) / den_t * 100, 6)
    chk('D4', d2 == p3 and d3 == p5 and '같은 분자' in kk[3][0],
        '검산 4번째 줄 — 같은 분자를 다른 분모로 나눈 것이 맞는가',
        '÷PA %s%% ↔ ③ %s%% · ÷( ( Σ( A_i × D_i ) + PEC ) ÷ PD ) %s%% ↔ ⑤ %s%%' % (d2, p3, d3, p5))
    chk('D5', q(p3 * D(PA) / 100, 4).quantize(D(1), rounding=ROUND_HALF_UP) == ann_doc,
        '연환산 수익금 반올림 = 원고 표기',
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

    # A_i = 순지급액_i × (1 − r)
    f = formula_of('A_i')
    chk('E1', f is not None and '순지급액' in f and '1 − r' in f.replace('-', '−'),
        'A_i 산식 문언', f)
    bad = [r for r in L.RECEIVABLES if L.ri(D(r['net']) * (D(1) - RATE)) != r['ai']]
    mx = max([abs(L.ri(D(r['net']) * (D(1) - RATE)) - r['ai']) for r in bad] or [0])
    chk('E2', not bad, 'A_i = 순지급액 × (1 − 0.11%) 전건 재현',
        '불일치 %d / %s건 · 최대 %s원' % (len(bad), format(n, ','), mx))

    # L_i = 미지급금_i − 과지급금_i
    chk('E3', formula_of('L_i') is not None, 'L_i 산식 존재', formula_of('L_i'))
    okL = all(r['ded'] == max(0, r['unpaid'] - r['over']) for r in L.RECEIVABLES)
    negL = sum(1 for r in L.RECEIVABLES if r['unpaid'] - r['over'] < 0)
    chk('E4', okL, '원장 차감액 = max(0, L_i) 전건',
        'L_i<0 인 채권 %d건 — 클램프가 실제로 무는 자리 %s' % (negL, '있음' if negL else '0건'))

    # M_i = 채권매입수수료_i − max(0, L_i)
    chk('E5', formula_of('M_i') is not None, 'M_i 산식 존재', formula_of('M_i'))
    has_fee = any('채권매입수수료' in (v.get('formula') or '') or v['term'] == '채권매입수수료'
                  for v in MS['vars'] if v['sym'] not in ('M_i',))
    chk('E6', has_fee, 'vars 30항이 `채권매입수수료_i` 를 정의하는가 — M_i 산식의 재료',
        '정의 0건이면 M_i 를 낱개로 계산할 수 없다 (현재 %s)' % ('있음' if has_fee else '없음'))
    # 낱개 읽기 세 가지 중 원장 M(d-1) 과 맞는 것이 있는가
    d_fl = sum(day_FEE(d) - sum(L.fl(D(r['net']) * RATE) for r in DAYROWS[d]) for d in DAYROWS)
    d_ri = sum(day_FEE(d) - sum(L.ri(D(r['net']) * RATE) for r in DAYROWS[d]) for d in DAYROWS)
    wk_fl = sum(sum(L.fl(D(r['net']) * RATE) for r in DAYROWS[d]) - day_DED(d) for d in WEEK_DAYS)
    wk_ri = sum(sum(L.ri(D(r['net']) * RATE) for r in DAYROWS[d]) - day_DED(d) for d in WEEK_DAYS)
    chk('E7', d_fl != 0 and d_ri != 0,
        '채권매입수수료는 하루치에서 한 번만 끊는다 — 건별로 끊은 합과 갈리는 것이 규칙대로다',
        '내림읽기 편차 %s원 · 반올림읽기 편차 %s원 (원장은 하루 Σ순지급액에 요율을 곱해 내림한다 · dm_0901 규칙 2)'
        % (format(d_fl, ','), format(d_ri, ',')))
    chk('E8', wk_fl != PM and wk_ri != PM,
        '건별 M_i 합은 원고 PM 과 갈린다 — 끊는 곳이 하루치 한 곳이기 때문이다',
        '내림읽기 %s (③ %s%%) · 반올림읽기 %s (③ %s%%) ↔ 원장 %s (③ %s%%)'
        % (format(wk_fl, ','), q(D(wk_fl) / D(PA) * 100 * DAYS / PWD_DAY, 2),
           format(wk_ri, ','), q(D(wk_ri) / D(PA) * 100 * DAYS / PWD_DAY, 2),
           format(PM, ','), q(PYMR_DAY, 2)))

    # B_i = 순지급액_i − max(0, L_i)
    chk('E9', formula_of('B_i') is not None, 'B_i 산식 존재', formula_of('B_i'))
    diffs = [(d, day_B(d) - day_BAM(d)) for d in sorted(DAYROWS)]
    off = [x for x in diffs if x[1] != 0]
    bad = [d for d in sorted(DAYROWS) if FACTS['tyByDate'][L.ymd(d)][4] != day_B(d)]
    chk('E10', not bad,
        '원장·화면 상환액 = Σ B_i (대표 원문 정의 그대로) 180일 전건',
        '어긋난 날 %d / %d · A+M 로 나눠 더한 길과는 %d일에서 %s ~ %s원 갈린다 (180일 합 %s원)'
        % (len(bad), len(diffs), len(off),
           min(x[1] for x in diffs), max(x[1] for x in diffs),
           format(sum(x[1] for x in diffs), ',')))


# ══════════════════════════════════════════════════════════════════
# F. 하루치 산식 일곱 — 2026-08-27 · 2026-08-23
# ══════════════════════════════════════════════════════════════════
F_DATES = [L.LAST_DUE, date(2026, 8, 23)]    # 표 마지막 행과 그 앞 어느 하루


def sec_F():
    chk('F0', len(F_DATES) == 2 and all(d in DAYROWS for d in F_DATES),
        '검산 일자 2건이 원장에 있다', ', '.join(L.ymd(d) for d in F_DATES))
    for d in F_DATES:
        k = L.ymd(d)
        tb = FACTS['tyByDate'][k]
        A, M, DEDv, FEEv = day_A(d), day_M(d), day_DED(d), day_FEE(d)
        Bdef = day_B(d)
        Bscr = day_BAM(d)
        wraw, w6, wdisp = day_wD_raw(d), day_wD_6(d), day_wD_disp(d)
        MR = D(M) / D(A) * 100
        ymr6 = q(MR * DAYS / w6, 6)
        ymr_disp = MR * DAYS / wdisp
        chk('F.%s.A' % k, A == tb[2], 'A(d−1) = Σ A_i (i ∈ d−1)',
            '%s ↔ 화면원천 %s' % (format(A, ','), format(tb[2], ',')))
        chk('F.%s.M' % k, M == tb[3], 'M(d−1) = Σ M_i',
            '%s = 수수료 %s − 차감 %s ↔ 화면원천 %s'
            % (format(M, ','), format(FEEv, ','), format(DEDv, ','), format(tb[3], ',')))
        chk('F.%s.B' % k, Bdef == tb[4], 'B(d−1) = Σ B_i (원고 정의 그대로)',
            '정의 %s ↔ 화면원천 %s (화면은 A+M = %s · 차 %s원)'
            % (format(Bdef, ','), format(tb[4], ','), format(Bscr, ','), Bdef - Bscr))
        chk('F.%s.MR' % k, q(MR, 6) == q(D(tb[3]) / D(tb[2]) * 100, 6),
            'MR(d−1) = M(d−1) ÷ A(d−1)', '%s%%' % q(MR, 6))
        chk('F.%s.wD' % k, str(w6) == str(q(wraw, 6)) and str(wdisp) == tb[0],
            'wD(d−1) = Σ(A_iD_i) ÷ A(d−1) — 여섯 자리로 남기고 화면은 두 자리',
            '여섯 자리 %s · 화면 %s ↔ 화면원천 %s' % (w6, wdisp, tb[0]))
        chk('F.%s.EC' % k, L.CASH * 1 == L.CASH,
            'EC(d−1) = 전일자 자정 잔액 — 원장에 일별 EC 원장이 없어 상수 %s 로 선다' % format(L.CASH, ','),
            '원고도 formula 없음(정의 문장만) · 기간 합 PEC 만 화면에 뜬다')
        chk('F.%s.YMR' % k, str(q(ymr6, 2)) == tb[1],
            'Y(MR,d−1) = MR × 365 ÷ wD(d−1) — 분모는 여섯 자리 값',
            '여섯자리wD %s%% (표기 %s) · 두자리wD %s%% (표기 %s) ↔ 화면원천 %s'
            % (ymr6, q(ymr6, 2), q(ymr_disp, 6), q(ymr_disp, 2), tb[1]))
    # 여섯 자리 값을 넣는 길이 화면 전건과 맞는가. 두 자리로 끊으면 몇 날이 뒤집히는가
    bad, flip = [], []
    for d in sorted(DAYROWS):
        A, M = day_A(d), day_M(d)
        MR = D(M) / D(A) * 100
        got = q(q(MR * DAYS / day_wD_6(d), 6), 2)
        if str(got) != FACTS['tyByDate'][L.ymd(d)][1]:
            bad.append(L.ymd(d))
        if got != q(MR * DAYS / day_wD_disp(d), 2):
            flip.append(L.ymd(d))
    chk('F.rule', not bad,
        'Y(MR,d−1) — 여섯 자리 wD(d−1) 로 낸 값이 화면 전건과 같은가',
        '어긋난 날 %d / %d일 · 예 %s' % (len(bad), len(DAYROWS), ', '.join(bad[:5]) or '없음'))
    chk('F.flip', len(flip) > 0,
        'Y(MR,d−1) — 두 자리로 끊어 넣으면 화면 표기가 뒤집힌다 (규칙에 판별력이 있는가)',
        '뒤집히는 날 %d / %d일 · 예 %s' % (len(flip), len(DAYROWS), ', '.join(flip[:5])))


# ══════════════════════════════════════════════════════════════════
# G. 미회수 잔량 — Σ A_i · wD · Yr · LR
#    원고 scopes 는 범위 표시가 없는 기호를 「미회수 잔량」으로 읽으라고 적었다.
#    그 읽기대로 계산해서 화면값이 나오는지 본다.
# ══════════════════════════════════════════════════════════════════
def sec_G():
    sc = dict((s['mark'], s) for s in MS['scopes'])
    chk('G0', '없음' in sc and '미회수' in sc['없음']['name'],
        'scopes — 범위 표시 없는 기호의 읽기', '%s · %s' % (sc['없음']['name'], sc['없음']['def']))
    chk('G1', SUM_A_OPEN == L.BOOK, 'Σ A_i (미회수) = 화면 투자실행액',
        '%s · 미회수 %s건' % (format(SUM_A_OPEN, ','), format(len(OPEN), ',')))

    v = dict((x['sym'], x) for x in MS['vars'])
    chk('G2', 'D' in v and v['D']['formula'], 'wD 산식 존재', v['D']['formula'])
    wtxt = (v['D']['formula'] or '') + ' ' + (v['D'].get('plain') or '')
    chk('G3', ('전체' in wtxt) or ('발생 기준' in wtxt),
        'wD 항이 모집단을 「대상정산금채권 전체 (발생 기준)」로 적는가 — 화면 열머리 툴팁이 대는 문언',
        '원고 wD 항 전문: %s' % wtxt.strip())
    chk('G4', str(q(WD_OPEN, 6)) != FACTS['wRaw'],
        'wD — 미회수만 세면 화면 wD 가 안 나온다 (원고 scopes 가 칸마다 모집단이 다르다고 적은 근거)',
        '미회수 %s (표기 %s) ↔ 화면 %s (표기 %s) · 차 %s일'
        % (q(WD_OPEN, 6), q(WD_OPEN, 2), FACTS['wRaw'], FACTS['w'], q(WD_OPEN - WD_ALL, 6)))
    chk('G5', str(q(WD_ALL, 6)) == FACTS['wRaw'],
        'wD — 원장·화면 모집단(대상정산금채권 전체)으로 계산한 값이 화면 wD 인가',
        '%s ↔ %s' % (q(WD_ALL, 6), FACTS['wRaw']))

    yr_open = RPCT * DAYS / q(WD_OPEN, 2)
    yr_disp = RPCT * DAYS / q(WD_ALL, 2)
    yr_6 = RPCT * DAYS / q(WD_ALL, 6)
    yr_raw = yr_6
    chk('G6', str(q(yr_open, 2)) != FACTS['ty'],
        'Y_r — 미회수 wD 로 내면 화면 Ty 가 안 나온다 (모집단이 갈리는 것이 화면에 실제로 보인다)',
        '%s%% ↔ 화면 %s%%' % (q(yr_open, 2), FACTS['ty']))
    chk('G7', str(q(yr_disp, 2)) == FACTS['ty'] and str(q(yr_raw, 2)) == FACTS['ty'],
        'Yr — 전체 모집단 wD 로 계산하면 화면 Ty 가 나오는가',
        '표기wD %s%% · rawwD %s%% ↔ 화면 %s%%' % (q(yr_disp, 6), q(yr_raw, 6), FACTS['ty']))
    # Yr 분모 판별 — 원장이 raw 를 쓰는지 표기를 쓰는지
    chk('G8', str(L.TY_BOOK) == str(q(yr_6, 2)) and q(yr_disp, 6) != q(yr_6, 6),
        'Y_r 분모 판별 — 원장은 여섯 자리 wD 를 쓴다 (두 기준이 6자리에서 갈려 판별력이 있다)',
        '두자리 %s → %s%% · 여섯자리 %s → %s%% · 차 %s%%p · 원장 TY %s'
        % (FACTS['w'], q(yr_disp, 6), FACTS['wRaw'], q(yr_6, 6),
           q(yr_6 - yr_disp, 6), L.TY_BOOK))

    _lrf = v.get('LR', {}).get('formula', '')
    chk('G9', '20일 전' in _lrf and '11일 전' in _lrf,
        'LR 산식이 표본 구간을 달고 있는가', _lrf)
    chk('G10', str(q(LR, 6)) == FACTS['sRaw'] and str(q(LR, 2)) == FACTS['s'],
        'LR = Σ L_i ÷ Σ A_i (표본 d−20 ~ d−11)',
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
    f = v['PD']['formula']
    # 기획자가 채권 경로로 정했다(2026-09-02). 대표 정의서 [2번] 「PSD = (Σ Api x Dpi) / PSA」
    # 와 같은 길이고 중간에 끊는 자리가 없다.
    chk('H0', 'Σ( A_i × D_i ) ÷ Σ A_i' in f and 'd−1' not in f,
        'PwD 산식이 채권 단위 Σ( A_i × D_i ) ÷ Σ A_i 로 적혀 있다', f)
    chk('H1', PWD_REC == PWD_DAY,
        'PwD — 채권 단위와 「일자 단위 × 여섯 자리 wD」는 같은 값이다',
        '채권 %s ↔ 일자·여섯자리 %s (반올림 전 %s)'
        % (PWD_REC, PWD_DAY, q(PWD_DAYRAW, 12)))
    chk('H2', str(PWD_DAY) == FACTS['weekWRaw'],
        'PwD — 원고 산식대로 낸 값이 원장·화면 값인가',
        '원고산식 %s ↔ 원장값 %s · 두 자리로 끊어 가중하면 %s (차 %s일)'
        % (PWD_DAY, FACTS['weekWRaw'], q(PWD_2DP, 6), q(PWD_2DP - PWD_DAY, 6)))
    chk('H3', q(PYMR_2DP, 2) == q(PYMR_DAY, 2),
        'wD(d−1) 을 두 자리로 끊어도 ③ 화면 표기는 안 뒤집힌다',
        '두자리 %s%% → %s%% · 정본 %s%% → %s%%'
        % (PYMR_2DP, q(PYMR_2DP, 2), PYMR_DAY, q(PYMR_DAY, 2)))
    # 두 경로가 갈리는지 본다. 표기 두 자리까지 뒤집히는지는 조회기간에 달렸다.
    chk('H4', WPYMR_2DP != WPYMR_DAY,
        'D 를 두 자리로 끊으면 ⑤ 가 정본과 갈린다 (6자리 규칙이 무는 자리)',
        '두자리 %s%% → %s%% · 정본 %s%% → %s%%'
        % (WPYMR_2DP, q(WPYMR_2DP, 2), WPYMR_DAY, q(WPYMR_DAY, 2)))

    diffs = [day_B(d) - day_BAM(d) for d in sorted(DAYROWS)]
    chk('H5', all(FACTS['tyByDate'][L.ymd(d)][4] == day_B(d) for d in DAYROWS),
        '상환액 — 원장·화면이 쓰는 갈래가 ( Σ 순지급액_i ) − ( Σ max(0, L_i) ) 인가 (180일 전건)',
        'A(d−1) + M(d−1) 로 나눠 더한 길과 %d / %d일에서 갈린다 · 하루 %s ~ %s원 · 180일 합 %s원'
        % (sum(1 for x in diffs if x), len(diffs), min(diffs), max(diffs),
           format(sum(diffs), ',')))
    wk = sum(day_B(d) - day_BAM(d) for d in WEEK_DAYS)
    chk('H6', PB == FACTS['weekRepay'] and wk > 0,
        '상환액 — 조회기간 합이 원장과 같고 A+M 갈래와 갈리는가',
        '원문정의 %s ↔ 원장 %s · A+M %s · 차 %s원'
        % (format(PB, ','), format(FACTS['weekRepay'], ','),
           format(sum(day_BAM(d) for d in WEEK_DAYS), ','), wk))
    chk('H7', not any(FACTS['tyByDate'][L.ymd(d)][4] == day_BAM(d)
                      and day_B(d) != day_BAM(d) for d in DAYROWS),
        '화면이 A(d−1) + M(d−1) 갈래를 쓰는 날이 하나도 없다 (180일 전건)',
        '화면원천 tyByDate 상환액 = ( Σ 순지급액_i ) − ( Σ max(0, L_i) )')

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
        '화면 투자실행액 = Σ A_i(미회수)', '%s ↔ %s' % (ca['투자실행액']['value'], SUM_A_OPEN))
    chk('I5', only(ca['순현금']['value']) == str(L.CASH),
        '화면 순현금 = EC', '%s ↔ %s' % (ca['순현금']['value'], L.CASH))
    chk('I6', only(ca['투자자산']['value']) == str(SUM_A_OPEN + L.CASH),
        '화면 투자자산 = Σ A_i + EC', ca['투자자산']['value'])
    chk('I7', only(ca['예상 연환산수익률']['value']) == FACTS['ty'],
        '화면 예상 연환산수익률 = Yr', '%s ↔ %s' % (ca['예상 연환산수익률']['value'], FACTS['ty']))
    chk('I8', FACTS['w'] in (ca['예상 연환산수익률']['sub'] or ''),
        '화면 Ty 부제가 표기 wD 를 댄다 (Yr 분모가 표기 갈래임을 화면이 스스로 적는다)',
        ca['예상 연환산수익률']['sub'])
    hdr = pa['tables'][0]['head']
    chk('I9', any('가중평균 금융일수' in h for h in hdr),
        '투자 자산 현황표에 가중평균 금융일수 열이 있다', str(hdr))
    row0 = pa['tables'][0]['body'][0]
    chk('I10', only(row0[2]) == FACTS['w'] and only(row0[4]) == FACTS['ty'],
        '현황표 투자실행액 행 W·Ty = 원장', str(row0))
    chk('I11', only(row0[3]) == FACTS['s'], '현황표 입금부족률 = LR 표기', row0[3])

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
        '화면 ⑤ = 원고 계산 예시의 화면 표기',
        '%s ↔ %s' % (sp['투자자산 대비']['value'], nums(st[8][1])[1]))
    chk('I17', only(sp['투자자산 대비']['value']) == str(q(WPYMR_DAY, 2)),
        '화면 ⑤ = 원고 산식 PY_a × Σ( A_i × D_i ) ÷ ( Σ( A_i × D_i ) + PEC ) 로 계산한 값',
        '화면 %s ↔ 원고산식 %s (두 자리로 끊으면 %s)'
        % (sp['투자자산 대비']['value'], q(WPYMR_DAY, 2), q(WPYMR_2DP, 2)))

    tb = [t for t in pp['tables'] if t['body'] and len(t['body'][0]) == 6]
    chk('I18', tb and len(tb[0]['body']) == len(WEEK_DAYS),
        '일별 투자수익 표 %d행 대상 0건 아님' % len(WEEK_DAYS),
        '%d행' % (len(tb[0]['body']) if tb else 0))
    body = tb[0]['body']
    bad_b, bad_y, bad_yraw = [], [], []
    for r in body:
        d = date(*map(int, r[0].split('-')))
        if only(r[1]) != str(day_B(d)):
            bad_b.append((r[0], r[1], str(day_B(d))))
        MR = D(day_M(d)) / D(day_A(d)) * 100
        if only(r[5]) != str(q(q(MR * DAYS / day_wD_6(d), 6), 2)):
            bad_y.append((r[0], r[5]))
        if only(r[4]) != str(day_wD_disp(d)):
            bad_yraw.append((r[0], r[4], str(day_wD_disp(d))))
    chk('I19', not bad_b,
        '일별 표 상환액 = ( Σ 순지급액_i ) − ( Σ max(0, L_i) ) 전행', str(bad_b))
    chk('I20', not bad_y, '일별 표 연환산수익률 = 여섯 자리 wD 갈래 전행', str(bad_y))
    chk('I21', not bad_yraw,
        '일별 표 가중평균 금융일수 = 여섯 자리 wD 의 두 자리 표기 전행',
        '어긋난 행 %d / %d — %s' % (len(bad_yraw), len(body),
                                 '; '.join('%s 화면 %s ↔ 원장 %s' % x for x in bad_yraw)))
    foot = tb[0]['foot'][0]
    chk('I22', only(foot[2]) == str(PA) and only(foot[3]) == str(PM),
        '일별 표 합계행 = PA · PM', str(foot))
    chk('I23', only(foot[1]) == str(PB),
        '일별 표 합계 상환액 = PB (원문 정의 한 줄로)',
        '%s ↔ %s (A + M 로 나눠 더하면 %s)'
        % (foot[1], PB, format(sum(day_BAM(d) for d in WEEK_DAYS), ',')))
    chk('I24', only(foot[4]) == str(q(PWD_DAY, 2)),
        '일별 표 합계 가중평균 금융일수 = PwD 표기', '%s ↔ %s' % (foot[4], q(PWD_DAY, 2)))

    h = out.get('hover')
    chk('I25', h and h['w'] > 0 and h['h'] > 0 and h['vis'] != 'hidden',
        'hover — 투자자산 대비 툴팁이 실제로 열린다', str(h)[:160] if h else 'None')
    # [기준 교체 2026-09-04] ⑤ 툴팁이 PA 대신 Σ( A_i × D_i ) 를 댄다 (step7 ⑤ 산식 교체 ·
    # build_app.py pfRender ⑤ 행 `Σ( A_i × D_i ) | 값원`). PA 행은 ④ 툴팁으로 옮겨 갔다.
    chk('I26', h and format(SAD, ',') in h['text'] and format(PEC, ',') in h['text'],
        'hover 툴팁이 Σ( A_i × D_i ) · PEC 를 그대로 댄다',
        (h or {}).get('text', '')[:220])


# ══════════════════════════════════════════════════════════════════
# K. 개념 갈래 · 갈래 표 · 겹치는 이름
#    개념 항목은 갈래 기호에서 뒤집어 세운 것이라 스스로 값을 갖지 않는다.
#    그래서 값이 아니라 짜임을 본다 — 세운 글자가 실제로 갈라지는가,
#    갈래 표가 vars 전건을 덮는가, 겹침 문장이 대는 숫자가 원장과 같은가.
# ══════════════════════════════════════════════════════════════════
import alias_table as AT                                     # noqa: E402

CONC_KINDS = ('상수', '개념')


def _var(sym, kind=None):
    """기호로 원고 항을 찾는다. D 처럼 개념·집계 두 항이 같은 글자면 kind 로 가른다."""
    for v in MS['vars']:
        if v['sym'] == sym and (kind is None or v['kind'] == kind):
            return v
    return {}


def _plain(sym, kind=None):
    return _var(sym, kind).get('plain') or ''


def sec_K():
    V = MS['vars']
    conc = [v for v in V if v['kind'] == '개념']
    body = [v for v in V if v['kind'] not in CONC_KINDS]
    bare = set(v['sym'] for v in body)
    keys = {}
    for v in body:
        got = AT.split(v['sym'])
        if got:
            keys.setdefault(got[0], {}).setdefault(got[1], []).append(v['sym'])
    # 개념 항목 산식 — 첨자·범위를 뗀 일반형 (A = 순지급액 × ( 1 − r )). 재료는 원고에 실재하는
    # 기호와 기초 항목뿐이라 설명 문장이 들어오면 재료 아닌 낱말로 잡힌다. 첨자는 Σ 안에서만 선다.
    # 접두 Y(연환산) 는 값이 아니라 산식을 두지 않는다.
    GEN_BASE = {'순지급액', '미지급금', '과지급금', '채권매입수수료', 'max', 'Σ', '0', '1', '365'}
    allsym = set(x['sym'] for x in V)
    badf = []
    for v in conc:
        f = v.get('formula')
        if v['sym'] == 'Y':
            if f:
                badf.append('Y → 접두에 산식 %r' % f)
            continue
        if not f:
            badf.append('%s → 산식 없음' % v['sym'])
            continue
        if not f.startswith(v['sym'] + ' = '):
            badf.append('%s → 「%s = 」로 시작하지 않음 %r' % (v['sym'], v['sym'], f))
            continue
        rhs = f[len(v['sym']) + 3:]
        if re.search(r'i 는|∈|\d건|d−1|\s{3,}', rhs):
            badf.append('%s → 범위 조건이 붙음 %r' % (v['sym'], rhs))
        toks = [t for t in re.split(r'[\s()×÷−+,]+', rhs) if t]
        alien = [t for t in toks if t not in allsym and t not in GEN_BASE]
        if alien:
            badf.append('%s → 재료 아닌 낱말 %s' % (v['sym'], ', '.join(alien)))
        if '_' in rhs and 'Σ' not in rhs:
            badf.append('%s → Σ 없이 첨자 %r' % (v['sym'], rhs))
    chk('K0', len(conc) > 0 and not badf,
        '개념 항목 대상 0건 아님 · 개념 항목 산식이 첨자·범위 없는 일반형이고 재료가 실재 기호뿐이다 (접두 Y 는 산식 없음)',
        '; '.join(badf) or '%d항 — %s' % (len(conc), ' · '.join(
            '%s %s' % (v['sym'], v.get('formula') or '(없음)') for v in conc)))

    need = sorted(k for k in keys if k not in bare)
    have = sorted(v['sym'] for v in conc)
    chk('K1', need and set(need) <= set(have),
        '홀로 서지 않는 갈래 글자가 전건 개념 항목에 있다',
        '갈래 글자 %s · 홀로 서는 것 %s · 개념 항목 %s'
        % (', '.join(sorted(keys)), ', '.join(sorted(set(keys) & bare)) or '없음',
           ', '.join(have) or '없음'))

    miss = []
    for v in conc:
        cited = set(re.findall(r'`([^`]+)`', v.get('plain') or ''))
        own = set(sum(keys.get(v['sym'], {}).values(), []))
        if own - cited:
            miss.append('%s → %s' % (v['sym'], ', '.join(sorted(own - cited))))
        if not own:
            miss.append('%s → 갈래 기호 0건' % v['sym'])
    chk('K2', not miss, '개념 항목이 자기 갈래 기호를 빠짐없이 댄다', '; '.join(miss) or '전건 댄다')

    ghost = []
    for v in conc:
        for c in re.findall(r'`([^`]+)`', v.get('plain') or ''):
            if c not in set(x['sym'] for x in V):
                ghost.append('%s → %s' % (v['sym'], c))
    chk('K3', not ghost, '개념 항목이 대는 기호가 vars 에 실재한다', '; '.join(ghost) or '전건 실재')

    rows = AT.branch_rows(MANUSCRIPT)
    fold = sorted(k for k in keys if k.endswith('R') and k[:-1] in keys
                  and set(keys[k]) == {'그 밖'})
    chk('K4', len(rows) == len(keys) - len(fold) and rows,
        '갈래 표 대상 0건 아님 · 행 수 = 갈래 글자 수 − 재료 행으로 든 비율 기호',
        '%d행 — %s · 재료 행으로 든 것 %s'
        % (len(rows), ' · '.join(r[0].split()[0] for r in rows), ', '.join(fold) or '없음'))
    shown = set()
    for r in rows:
        for c in r[1:]:
            shown |= set(re.findall(r'[^ ·()]+(?:_\{[^}]*\}|_[ir])?', c.replace('Σ ', 'Σ')))
    out = []
    for v in body:
        t = v['sym'].replace('Σ ', 'Σ')
        if AT.split(v['sym']) and t not in shown:
            out.append(v['sym'])
    chk('K5', not out, '갈래 표가 갈래 기호 전건을 덮는다 (합성·한글 기호는 세우지 않는다)',
        '빠진 기호 %s' % (', '.join(out) or '없음'))
    dash = [r[0] for r in rows for c in r[1:] if c.strip() in ('—', '-', 'N/A')]
    chk('K6', not dash, '갈래 표 빈 칸을 대시로 채우지 않았다', '대시 칸 %s' % (', '.join(dash) or '0건'))

    # ── 겹침 (가) 투자실행액 두 값
    a1, a2 = format(SUM_A_OPEN, ','), format(PA, ',')
    t1, t2 = _plain('Σ A_i'), _plain('PA')
    chk('K7', a1 in t1 and a2 in t1 and '`PA`' in t1 and a2 in t2 and a1 in t2 and '`Σ A_i`' in t2,
        '투자실행액 두 값 — 두 항이 서로를 가리키고 금액이 원장과 같다',
        'Σ A_i %s (미회수 %s건) ↔ PA %s (조회기간 만기)'
        % (a1, format(len(OPEN), ','), a2))
    chk('K8', '투자실행액' in t1 and '투자실행금' in t1 and '투자실행금' in t2 and '투자실행액' in t2,
        '투자실행액 두 값 — 화면 이름 두 벌을 두 항이 다 적는다',
        '투자 자산 화면 「투자실행액」 · 투자 수익 화면 「투자실행금」')

    # ── 겹침 (나) W금융일수 두 값
    w1, w2 = _plain('D', kind='집계'), _plain('PD')
    chk('K9', FACTS['w'] in w1 and FACTS['weekW'] in w1 and '`PD`' in w1
        and FACTS['weekW'] in w2 and FACTS['w'] in w2 and '`D`' in w2,
        'W금융일수 두 값 — 두 항이 서로를 가리키고 일수가 원장과 같다',
        'wD %s일 (발생 전체 %s건) ↔ PwD %s일 (조회기간 만기)'
        % (FACTS['w'], format(FACTS['receivables'], ','), FACTS['weekW']))
    chk('K10', format(FACTS['receivables'], ',') in (_var('D', kind='집계').get('formula') or ''),
        'wD 산식이 모집단 건수를 원장과 같이 적는다',
        '%s ↔ 원장 %s건' % (_var('D', kind='집계').get('formula'), format(FACTS['receivables'], ',')))

    # ── 겹침 (다) 수익율 두 층
    m1, m2 = _plain('PMR'), _plain('PY_a')
    pmr6, py6 = str(q(PMR, 6)), str(PYMR_DAY)
    chk('K11', pmr6 in m1 and py6 in m1 and '`PY_a`' in m1
        and pmr6 in m2 and py6 in m2 and '`PMR`' in m2,
        '수익율 두 층 — 기간 비율과 연환산이 서로를 가리키고 값이 재계산과 같다',
        'PMR %s%% ↔ PY_{MR} %s%% (%s배)' % (pmr6, py6, q(PYMR_DAY / q(PMR, 6), 0)))
    y1 = _plain('Y_r')
    chk('K12', FACTS['ty'] in y1 and FACTS['weekTy'] in y1 and '`PY_a`' in y1
        and FACTS['weekTy'] in m2 and FACTS['ty'] in m2 and '`Y_r`' in m2,
        'Ty수익율 라벨 두 층 — 예상과 실적이 서로를 가리키고 표기가 원장과 같다',
        'Y_r %s%% (할인율 분자) ↔ PY_{MR} %s%% (실적 분자)' % (FACTS['ty'], FACTS['weekTy']))

    # ── 순현금 한 시점 ↔ 기간 합
    ec = _plain('EC')
    chk('K13', format(L.CASH, ',') in ec and format(PEC, ',') in ec and '`PEC`' in ec,
        '순현금 — 한 시점 잔액과 기간 합을 같은 항에서 가른다',
        'EC %s원 × %d일 = PEC %s원' % (format(L.CASH, ','), len(WEEK_DAYS), format(PEC, ',')))

    # ── 「비중」 두 분모
    tot = _plain('Σ A_i + EC')
    s1 = str(q(D(SUM_A_OPEN) / D(SUM_A_OPEN + L.CASH) * 100, 1))
    s2 = str(q(D(L.CASH) / D(SUM_A_OPEN + L.CASH) * 100, 1))
    chk('K14', s1 in tot and s2 in tot and '비중' in tot and '비중' in _plain('D', kind='집계'),
        '「비중」 — 화면 열과 wD 가중치가 같은 낱말이라는 것을 두 항이 적는다',
        '현황표 %s%% · %s%% (분모 투자자산) ↔ wD 가중치 A_i ÷ Σ A_i' % (s1, s2))


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
            6, [m['calc']['steps'][6][0], '3.992466%   화면 3.99%']), 'B7'),
        ('검산.연환산', lambda m: m['calc']['검산'].__setitem__(
            0, [m['calc']['검산'][0][0], '7,185,276원']), 'D1'),
        ('vars.A_i',   lambda m: [v for v in m['vars'] if v['sym'] == 'A_i'][0].__setitem__(
            'formula', 'A_i = 순지급액_i × (1 + r)'), 'E1'),
        ('vars.LR',   lambda m: [v for v in m['vars'] if v['sym'] == 'LR'][0].__setitem__(
            'formula', 'LR = ( Σ L_i ) ÷ ( Σ A_i )'), 'G9'),
        ('개념.Y삭제', lambda m: m['vars'].remove(
            [v for v in m['vars'] if v['sym'] == 'Y'][0]), 'K1'),
        ('개념.D산식설명', lambda m: [v for v in m['vars'] if v['sym'] == 'D' and v['kind'] == '개념'][0].__setitem__(
            'formula', 'D = 투자실행금으로 가중평균한 금융일수'), 'K0'),
        ('겹침.투자실행액', lambda m: [v for v in m['vars'] if v['sym'] == 'PA'][0].__setitem__(
            'plain', _plain('PA').replace('80,000,000', '80,000,001')), 'K7'),
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
    section('K', sec_K)
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
            print('  실패 목록 — %s' % ', '.join(x[0] for x in fails))
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
