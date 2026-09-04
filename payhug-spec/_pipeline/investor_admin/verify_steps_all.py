#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""화면 칸별 중간 계산 — 표기 검사.

  A  대시로 채운 칸 0건
       기호·용어·산식 자리에 `—` 하나만 든 칸. 값 자리의 `-` 는 배포 화면이
       실제로 찍는 글자라 (invest-assets.html 순현금 행·합계 행) 여기서 뺀다.
  B  프로젝트 밖에서 뜻이 안 통하는 낱말 0건 — 몫 · 재료 · 낱건
  C  정의 없이 쓰는 세로줄 표기 0건 — `|…|` 건수 · `w | 조건` 조건부
  D  폐기 기호 잔량 — 인용(source) · 화면 라벨은 따로 센다
       정본 dm_0901/symbol_rule_0901.md 「갈아 끼우는 표」 왼쪽 칸
  E  대표 원문 인용이 원문 글자인가 — source 의 [N번 이미지] 뒤 낱말
  F  아래첨자 조판 — 배포 HTML 에 리터럴 `_{` 0건

돌리기 :  python3 verify_steps_all.py
"""
import io
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
REPO = '/Users/semi/cursor/payhug-investor-admin'
SRC = os.path.join(BASE, 'meeting_0901', 'steps_all.json')
MAP = os.path.join(BASE, 'meeting_0901', 'merge', 'screen_map.json')
CEO = os.path.join(BASE, 'ceo_definitions.md')
OUT = os.path.join(BASE, 'verify_steps_all_result.json')

R = []


def chk(sec, name, ok, detail=''):
    R.append(dict(sec=sec, name=name, **{'pass': bool(ok)}, detail=str(detail)))


def rd(p):
    return io.open(p, encoding='utf-8').read()


DASH = ('—', '–', '―', 'ㅡ')
JARGON = ('몫', '재료', '낱건')
# 정본 「갈아 끼우는 표」 왼쪽 칸
DEP = re.compile(r'PSMR|PSA|PSM|PSD|PSC|WAD'
                 r'|SMR_\{|SM_\{|SA_\{|SB_\{|SD_\{|SL_i|SA_i'
                 r'|S입금부족율|w금융일수|ty수익율')
# 배포 화면이 실제로 띄우는 라벨 — 폐기 기호가 아니다
# 라벨 확정 2026-09-04 — 화면·엑셀·증명서 라벨이 `S입금부족율`·`W금융일수`·`Ty수익율` 에서
# `입금부족률`·`가중평균 금융일수`·`(예상 )연환산수익률` 로 바뀌었다(step5 빌더 보고).
# 옛 라벨은 더 이상 화면에 없으므로 D 에서 「화면 라벨」로 봐주지 않는다.
SCREEN_LABEL = ('입금부족률', '가중평균 금융일수', '연환산수익률')

d = json.load(io.open(SRC, encoding='utf-8'))
cells = d['cells']


def walk(fields):
    """(칸 번호, 필드 이름, 글자) 를 훑는다."""
    for i, c in enumerate(cells):
        for k in fields:
            v = c.get(k)
            if isinstance(v, str):
                yield i, k, v
            elif isinstance(v, list):
                for x in v:
                    if isinstance(x, str):
                        yield i, k, x
        for s in c.get('steps') or []:
            for k in ('what', 'detail'):
                if 'steps.' + k in fields and s.get(k):
                    yield i, 'steps.' + k, s[k]


ALL = ('label', 'term', 'symbol', 'formula', 'value', 'xlsx', 'source',
       'hidden', 'steps.what', 'steps.detail')

# ── A. 대시 ──────────────────────────────────────────────────
hit = [(i, k, v) for i, k, v in walk(('symbol', 'term', 'formula'))
       if v.strip() in DASH]
chk('A', '기호·용어·산식 자리 대시 0건', not hit, '%d건 %s' % (len(hit), hit[:5]))
val = [(i, k, v) for i, k, v in walk(('value',)) if v.strip() in DASH + ('-',)]
scr = rd(os.path.join(REPO, 'invest-assets.html')).count('<span class="none">-</span>')
chk('A', '값 자리 `-` = 배포 화면이 찍는 수와 같음', len(val) == scr,
    'JSON %d · invest-assets.html %d' % (len(val), scr))
html_ = rd(os.path.join(REPO, 'steps-all.html'))
for cls in ('sym', 'val'):
    n = len(re.findall(r'<span class="%s">\s*[—–―]\s*</span>' % cls, html_))
    chk('A', '배포 .%s 단독 대시 0건' % cls, n == 0, '%d건' % n)
n = len(re.findall(r'<div class="v[^"]*">\s*[—–―]\s*</div>', html_))
chk('A', '배포 근거·용어 줄 단독 대시 0건', n == 0, '%d건' % n)

# ── B. 낱말 ──────────────────────────────────────────────────
for w in JARGON:
    hit = [(i, k) for i, k, v in walk(ALL) if w in v]
    chk('B', '「%s」 0건' % w, not hit, '%d건 %s' % (len(hit), hit[:5]))
    chk('B', '배포 HTML 「%s」 0건' % w, w not in html_, html_.count(w))

# ── C. 세로줄 ────────────────────────────────────────────────
hit = [(i, k, v) for i, k, v in walk(ALL) if '|' in v]
chk('C', '세로줄 표기 0건', not hit, '%d건 %s' % (len(hit), hit[:5]))

# ── D. 폐기 기호 ─────────────────────────────────────────────
ours, quote, label = [], [], []
for i, k, v in walk(ALL):
    if not DEP.search(v):
        continue
    if k == 'source':
        quote.append((i, k, v))
    elif any(w in v for w in SCREEN_LABEL):
        label.append((i, k, v))
    else:
        ours.append((i, k, v))
chk('D', '우리 서술에 폐기 기호 0건', not ours, '%d건 %s' % (len(ours), ours[:5]))
chk('D', '인용(source) 자리는 남는다', True, '%d건' % len(quote))
chk('D', '화면 라벨 자리는 남는다', True, '%d건' % len(label))

# ── E. 원문 인용 ─────────────────────────────────────────────
ceo = re.sub(r'\s+', '', rd(CEO))
bad = []
for i, c in enumerate(cells):
    s = c.get('source') or ''
    if 'ceo_definitions.md' not in s:
        continue
    for tok in re.findall(r'[A-Za-z]*S?[A-Z]{1,3}D-1i?|S[A-Z]{1,3}i|Ap?i|Dp?i', s):
        if len(tok) < 3:
            continue
        if tok.replace(' ', '') not in ceo:
            bad.append((i, tok))
chk('E', 'source 의 대표 원문 기호가 원문에 그대로 있음', not bad,
    '어긋난 것 %d %s' % (len(bad), bad[:8]))
ours_sub = [(i, k, v) for i, k, v in walk(('source',)) if '_{' in v or '_i' in v]
chk('E', 'source 에 우리 조판(`_{` · `_i`) 0건', not ours_sub,
    '%d건 %s' % (len(ours_sub), ours_sub[:5]))

# ── F. 조판 ──────────────────────────────────────────────────
lit = html_.count('_{')
chk('F', '배포 HTML 리터럴 `_{` 0건', lit == 0, '%d건' % lit)
chk('F', '배포 HTML <sub> 조판', html_.count('<sub>') > 0, '%d건' % html_.count('<sub>'))

# ── 자리 지도도 같은 잣대로 ──────────────────────────────────
m = json.load(io.open(MAP, encoding='utf-8'))
mt = json.dumps(m, ensure_ascii=False)
for w in JARGON:
    chk('G', 'screen_map 「%s」 0건' % w, w not in mt, mt.count(w))
chk('G', 'screen_map 세로줄 표기 0건',
    '| 가맹점ID = i' not in mt and '|대상정산금채권|' not in mt, '')

# ── H. 원장 대조 ─────────────────────────────────────────────
#   서식만 보는 검사는 규칙 이전 경로로 낸 값을 그대로 통과시킨다 — 2026-09-02 교차검증에서
#   ④ 가 3.992465% 로 남아 있는 채 전건 PASS 였다. 기대값을 손으로 적지 않는다.
#   daily_ledger 가 낸 ledger_facts.json 을 읽고, 견줄 「규칙 이전 값」도 같은 원장 식으로 만든다.
#
#   돌리기 :  python3 verify_steps_all.py --selftest
#     규칙 이전 값을 메모리에서 한 건씩 되돌려 넣고 H 가 FAIL 로 도는지 본다. 파일은 안 고친다.
sys.path.insert(0, BASE)
import daily_ledger as dl                                  # noqa: E402
from decimal import Decimal as D, ROUND_HALF_UP            # noqa: E402

F = json.load(io.open(os.path.join(BASE, 'ledger_facts.json'), encoding='utf-8'))
FRAG = rd(os.path.join(BASE, 'steps_all.fragment.html'))
NUM = r'(?<![\d,.])(\d+(?:\.\d+)?)'
AMT = r'(\d{1,3}(?:,\d{3})*)'
# 사다리 한 줄 — 적힌 두 수로 계산하면 적힌 결과가 나와야 한다.
LADDER = ((re.compile(NUM + r'%? × ' + NUM + r'%? = ' + NUM + r'(?![\d,])'), 'mul'),
          (re.compile(NUM + r'%? ÷ ' + NUM + r'%? = ' + NUM + r'(?![\d,])'), 'div'),
          (re.compile(NUM + r'% × ' + AMT + r' ÷ ' + AMT + r' = ' + NUM + r'(?![\d,])'), 'wgt'))


def day_of(c):
    return c['label'].split('—')[-1].strip()


def cell_text(c):
    return ' '.join([c.get('value') or ''] + [s.get('detail') or '' for s in c['steps']]
                    + list(c.get('hidden') or []))


def pick(cells_):
    """④ 두 칸 · ⑤ 한 칸 · ⑥ 일곱 행."""
    # ④ 는 두 자리에 선다 — 수익 현황 카드와 일별 표 합계 행이다(합계 행의 마커는 열 번호 ⑥).
    q4 = [c for c in cells_ if (c.get('symbol') or '').replace('④ = ', '') == 'PMR × 365 ÷ PwD'
          and c.get('table') in ('수익 현황', '일별 투자수익 · 합계')]
    q5 = [c for c in cells_ if c.get('marker') == '⑤' and c.get('table') == '수익 현황']
    d6 = [c for c in cells_ if c.get('table') == '일별 투자수익' and c.get('marker') == '⑥']
    return q4, q5, d6


def ledger_pairs(d6):
    """(규칙대로 낸 값, 규칙 이전 경로로 낸 값) 짝. 둘 다 원장 식으로 만든다.

    규칙 이전 경로 = MR(d-1)·PMR 을 안 끊고 한 번에 낸 것(dm_0901 규칙 1 이전).
    """
    pa, pm = D(F['weekExec']), D(F['weekProfit'])
    o4 = dl.r6(pm / pa * D(100) * D(365) / D(F['weekWRaw']))
    out = [(F['weekTyRaw'], str(o4)),
           # ⑤ 둘째 인자 = Σ( A_i × D_i ) (facts weekAD). [기준 교체 2026-09-04 · step7 ⑤ 산식 교체 ·
           # daily_ledger.ty_asset(ty4, ad, psc)] — 옛 인자 PA(weekExec) 는 PSA 시절 산식이다.
           (F['weekTyAssetRaw'], str(dl.r6(dl.ty_asset(o4, D(F['weekAD']), D(F['weekPsc'])))))]
    for c in d6:
        day = day_of(c)
        ex, pf = D(str(F['tyByDate'][day][2])), D(str(F['tyByDate'][day][3]))
        w6 = D(F['w6ByDate'][day])
        out.append((str(dl.day_ty_raw(int(pf), int(ex), w6)),
                    str(dl.r6(pf / ex * D(100) * D(365) / w6))))
    return out


def hchecks(cells_, sc, mt, html_, frag, sink):
    """원장 대조 여섯 항목. sink(이름, 통과여부, 자세히) 로 결과를 흘린다."""
    q4, q5, d6 = pick(cells_)
    pairs = ledger_pairs(d6)
    new6 = set(n for n, _ in pairs)
    old6 = set(o for _, o in pairs) - new6

    miss = [c['label'] for c in q4 if F['weekTyRaw'] not in cell_text(c)]
    sink('④ 칸이 원장 weekTyRaw 를 그대로 쓴다', not miss and len(q4) == 2,
         '기대 %s · 칸 %d · 어긋난 것 %s' % (F['weekTyRaw'], len(q4), miss))
    miss = [c['label'] for c in q5 if F['weekTyAssetRaw'] not in cell_text(c)]
    sink('⑤ 칸이 원장 weekTyAssetRaw 를 그대로 쓴다', not miss and len(q5) == 1,
         '기대 %s · 칸 %d · 어긋난 것 %s' % (F['weekTyAssetRaw'], len(q5), miss))
    miss = [c['label'] for c in q4 if F['weekMR'] not in cell_text(c)]
    sink('④ 칸의 PMR 이 원장 weekMR 6자리다', not miss,
         '기대 %s · 어긋난 것 %s' % (F['weekMR'], miss))

    bad = []
    for c in d6:
        day, t = day_of(c), cell_text(c)
        w6 = F['w6ByDate'][day]
        want = str(dl.day_ty_raw(F['tyByDate'][day][3], F['tyByDate'][day][2], D(w6)))
        if w6 not in t:
            bad.append((day, 'w6ByDate %s 없음' % w6))
        if want not in t:
            bad.append((day, '⑥ 6자리 %s 없음' % want))
        if F['tyByDate'][day][1] + '%' not in t:
            bad.append((day, '표기 %s%% 없음' % F['tyByDate'][day][1]))
    sink('일별 ⑥ 7행이 원장 w6ByDate·⑥ 6자리와 같다', not bad and len(d6) == 7,
         '행 %d · 어긋난 것 %s' % (len(d6), bad[:6]))

    lost = []
    for v in sorted(old6):
        for nm, txt in (('steps_all.json', sc), ('screen_map.json', mt),
                        ('steps-all.html', html_), ('steps_all.fragment.html', frag)):
            if v in txt:
                lost.append((v, nm, txt.count(v)))
    sink('규칙 이전 경로 값 잔량 0건', not lost,
         '대조한 값 %d · 잔량 %s' % (len(old6), lost[:6]))

    seen, off = 0, []
    for i, c in enumerate(cells_):
        for s in c['steps']:
            t = s.get('detail') or ''
            for rx, op in LADDER:
                for mm in rx.finditer(t):
                    g = [x.replace(',', '') for x in mm.groups()]
                    a, b = D(g[0]), D(g[1])
                    if not b:
                        continue
                    v = a * b if op == 'mul' else a / b if op == 'div' else a * b / D(g[2])
                    res = g[-1]
                    dp = len(res.split('.')[1]) if '.' in res else 0
                    got = v.quantize(D(1).scaleb(-dp), rounding=ROUND_HALF_UP)
                    seen += 1
                    if got != D(res):
                        off.append((i, c['label'], t, '실제 %s' % got))
    sink('사다리가 자기 숫자로 닫힌다', not off and seen > 0,
         '대조한 줄 %d · 안 닫힌 것 %s' % (seen, off[:4]))


SC = json.dumps(d, ensure_ascii=False)
hchecks(cells, SC, mt, html_, FRAG, lambda n, o, de: chk('H', n, o, de))

if '--selftest' in sys.argv:
    def hfail(cells_, sc, mt_, h_, f_):
        out = []
        hchecks(cells_, sc, mt_, h_, f_, lambda n, o, de: out.append(o))
        return sum(1 for o in out if not o)

    base = hfail(cells, SC, mt, html_, FRAG)
    print('판별력 시험 — 규칙 이전 값을 되돌려 넣고 H 가 도는지 본다\n')
    print('  손 안 댄 상태 FAIL %d\n' % base)
    got = missed = 0
    for new, old in ledger_pairs(pick(cells)[2]):
        if new == old:
            continue
        sc2 = SC.replace(new, old)
        n = hfail(json.loads(sc2)['cells'], sc2, mt.replace(new, old),
                  html_.replace(new, old), FRAG.replace(new, old))
        if n > base:
            got += 1
            print('  %-10s → %-10s  잡음 (FAIL %d)' % (new, old, n))
        else:
            missed += 1
            print('  %-10s → %-10s  !! 못 잡음' % (new, old))
    # 사다리만 미는 자리 — 결과 숫자 하나가 앞 두 수와 안 맞게 되는 경우
    sc3 = SC.replace('× 365 = %s%%' % (D(F['weekMR']) * D(365)), '× 365 = 0.124069%')
    n = hfail(json.loads(sc3)['cells'], sc3, mt, html_, FRAG)
    if sc3 != SC and n > base:
        got += 1
        print('  %-10s → %-10s  잡음 (FAIL %d)' % ('연 환산', '0.124069', n))
    else:
        missed += 1
        print('  %-10s → %-10s  !! 못 잡음' % ('연 환산', '0.124069'))
    print('\n판별력 — 심은 것 %d건 · 잡음 %d / 못 잡음 %d' % (got + missed, got, missed))
    sys.exit(1 if missed or base else 0)

io.open(OUT, 'w', encoding='utf-8').write(
    json.dumps(R, ensure_ascii=False, indent=1))
ok = sum(1 for r in R if r['pass'])
for r in R:
    print('  %-3s %-46s %-4s %s'
          % (r['sec'], r['name'], 'PASS' if r['pass'] else 'FAIL', r['detail']))
print('\n%d항목 — PASS %d / FAIL %d' % (len(R), ok, len(R) - ok))
sys.exit(0 if ok == len(R) else 1)
