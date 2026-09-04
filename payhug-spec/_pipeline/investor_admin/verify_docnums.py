# -*- coding: utf-8 -*-
"""문서 낱장의 숫자를 채권 원장(ledger_facts.json)과 맞대는 검사.

왜 별도 파일인가 — verify_0828.py 를 넓히지 않았다.
  1. verify_0828.py 의 chk 번호는 고정 목록이고 다른 조 문서가 그 번호를 인용한다.
     항목을 끼워 넣으면 번호가 밀리거나 파일 경합이 난다.
  2. 여기 필요한 것은 값 4개 대조가 아니라 판정 규칙 한 벌이다 —
     표기값·대조값 가림, 원장 파생량 표, 판별력 시험. 규칙이 한 파일에 모여야 읽힌다.
  3. verify_0828.py 의 검사 범위는 배포 루트 HTML 전량이고, 이 검사는 문서 낱장과
     그 원고(파이프라인)를 함께 본다. 대상 집합이 다르다.

무엇을 보나
  숫자를 손으로 적지 않는다. 기대값은 ledger_facts.json 에서 읽고 파생량은 여기서 계산한다.
  A 고정밀 리터럴 — 소수 4자리 이상 · 백만 이상 콤마 금액
  B 두 자리 표기  — `N.NN%` · `N.NN일`
  둘 다 「원장 값 근처인데 원장 값이 아닌 것」을 잡는다. 근처의 기준은
  비율·일수 상대 0.5%, 금액 절대 2,000원이다.
  C 종전↔바꿈 표의 방향 — 대표 확인 문항 씨앗은 구조가 있어 칸을 갈라 본다.
    「바꿈」 칸의 숫자는 면제 없이 원장 값이어야 하고, 「종전」 칸과 숫자가 같으면 대조가 아니다.

대조값을 오탐으로 잡지 않는 방식
  옛 값이 정당한 자리는 두 조건을 함께 만족한다.
    (1) 같은 창(앞뒤 300자) 안에 대조 표지가 있다 — 종전 · 바꿈 · 갈림 · 두 칸 합 · 되짚 · 옛 · 폐기
    (2) 같은 창 안에 그 값이 견주는 원장 값의 정식 표기가 함께 있다
  (2)가 있어서 표지만 흉내낸 잔존값은 빠져나가지 못한다. 짝이 되는 새 값이 곁에 서야 통과한다.

  python3 verify_docnums.py            검사
  python3 verify_docnums.py --selftest 판별력 시험 — 파일을 고치지 않고 메모리에서만 심는다
    1단 문서에 있는 새 값을 옛 값으로 갈아치운다
    2단 그 값이 없는 문서에는 옛 값을 문서 머리에 끼워 넣는다
    3단 맞는 값을 같은 자리에 끼워 넣고 조용한지 본다 (오탐 시험)
"""
import html as H
import io, json, os, re, sys
from decimal import Decimal as D, ROUND_HALF_UP, getcontext

getcontext().prec = 40
PIPE = os.path.dirname(os.path.abspath(__file__))
REPO = '/Users/semi/cursor/payhug-investor-admin'
FACTS = json.load(io.open(os.path.join(PIPE, 'ledger_facts.json'), encoding='utf-8'))

RATE_TOL = D('0.005')     # 비율·일수 — 상대
AMT_TOL  = D(2000)        # 금액 — 절대(원)
WIN      = 300            # 대조 표지를 찾는 창 반경(문자)
MARKS    = ('종전', '바꿈', '갈림', '두 칸 합', '되짚', '옛 ', '옛값', '폐기')

# ── 대상 ─────────────────────────────────────────────────────────
TARGETS = [
    (REPO, 'glossary.html'),      (PIPE, 'glossary_manuscript.md'),
    (REPO, 'capability.html'),    (PIPE, 'capability_manuscript.md'),
    (REPO, 'feasibility.html'),   (PIPE, 'feasibility.md'),
    (REPO, 'inquiry.html'),       (PIPE, 'ceo_inquiry.md'),
    (REPO, 'review.html'),
    (REPO, 'ceo-questions.html'), (PIPE, 'ceoq_seed.json'),
    (REPO, 'steps-all.html'),     (PIPE, 'steps_all.fragment.html'),
]


def q(x, n):
    return D(x).quantize(D(1).scaleb(-n), rounding=ROUND_HALF_UP)


# ── 원장에서 읽는 값 + 원장으로 계산하는 파생량 ─────────────────
def quantities():
    F = FACTS
    pa, pec, pm = D(F['weekExec']), D(F['weekPsc']), D(F['weekProfit'])
    # AD = 기간 Σ( A_i × D_i ). ⑤ 의 새 분모 재료 (step7 ⑤ 산식 교체 2026-09-04 · daily_ledger.facts weekAD)
    ad = D(F['weekAD'])
    pwd = D(F['weekWRaw'])
    # PMR 을 6자리에서 끊고 그 값을 다음 계산에 넣는다(dm_0901 규칙 1).
    # 원장이 weekMR · weekTyRaw · weekTyAssetRaw 로 이미 낸 값을 그대로 쓴다.
    pmr = D(F['weekMR']) / 100
    turns = D(365) / pwd
    q4 = D(F['weekTyRaw'])
    # [기준 교체 2026-09-04] ⑤ 비중 = AD ÷ (AD + PEC). 옛 PA ÷ (PA + PEC) 은 PSA 시절 산식이라
    # 그 값(0.562460)이 문서에 남아 있으면 위반으로 잡힌다.
    ratio = ad / (ad + pec)
    Q = {}

    def add(key, val, kind):
        Q[key] = (D(val), kind)

    for k in ('exec', 'cash', 'total', 'weekExec', 'weekProfit', 'weekRepay',
              'weekPsc', 'weekAD', 'dayAvg', 'fullExec', 'fullProfit', 'fullPsc', 'fullAD'):
        add(k, F[k], 'amt')
    for k in ('wRaw', 'w', 'weekWRaw', 'weekW', 'fullW'):
        add(k, F[k], 'rate')
    for k in ('ty', 'weekTy', 'weekTyAsset', 'sRaw', 's', 'rate',
              'fullTy', 'fullTyAsset', 'weekMR', 'weekTyRaw', 'weekTyAssetRaw',
              'fullMR', 'fullTyRaw', 'fullTyAssetRaw'):
        add(k, F[k], 'rate')

    add('AD+PEC', ad + pec, 'amt')
    add('PMR%', pmr * 100, 'rate')
    add('365/PwD', turns, 'rate')
    add('4', q4, 'rate')
    add('AD비중', ratio, 'rate')
    add('5', D(F['weekTyAssetRaw']), 'rate')
    add('5(평균순현금)', q4 * pa / (pa + D(F['cash'])), 'rate')
    add('5(잔액)', q4 * D(F['exec']) / D(F['total']), 'rate')
    # 할인율의 원식 — 분모가 순지급액일 때. 근사 0.11% 와 다른 값이라 못에 함께 둔다
    add('할인율/(1−할인율)', D(F['rate']) / (1 - D(F['rate']) / 100), 'rate')
    add('ty@PwD', D(F['rate']) * turns, 'rate')
    add('ty@w', D(F['rate']) * D(365) / D(F['wRaw']), 'rate')
    return Q


QTY = quantities()


# ── 정식 표기 못 (문서에 나와도 되는 숫자 전량) ─────────────────
def canon(val, kind):
    """한 값의 정식 표기 집합.

    7자리를 함께 두는 이유 — 6자리 규칙(dm_0901/rounding_rule_0901.md 규칙 1)의 대상은
    `wD` `PwD` `MR(d-1)` `PMR` `PY_{MR}` `wPY_{MR}` `Y_r` `LR` 과 가중치 `A_i ÷ ΣA_i` 다.
    `Σ(Ai×Di) ÷ (Σ(Ai×Di) + PEC)` 은 그 목록에 없어 끊지 않고, calc.html 이 이 값을 7자리로 적는다.
    같은 값의 7자리 표기를 못에서 빼 두면 옳은 자리가 위반으로 잡힌다.
    """
    out = set()
    if kind == 'amt':
        n = int(val)
        out |= {str(n), format(n, ',')}
    else:
        for d in (1, 2, 3, 4, 6, 7):
            s = str(q(val, d))
            out.add(s)
            out.add(s.rstrip('0').rstrip('.') if '.' in s else s)
    return {x for x in out if x}


CANON = {k: canon(v, t) for k, (v, t) in QTY.items()}


def witness(key):
    """대조값을 눈감아 줄 때 곁에 서 있어야 하는 표기 — 화면 2자리와 계산 6자리만 센다.

    3자리 같은 중간 표기를 witness 로 두면 옛 값 자신이 witness 가 된다
    (`3.108` 은 `3.108481` 안에 들어 있다). 짝이 되는 새 값만 witness 가 되게 좁힌다."""
    v, kind = QTY[key]
    if kind == 'amt':
        return {str(int(v)), format(int(v), ',')}
    return {str(q(v, 2)), str(q(v, 6)), str(q(v, 6)).rstrip('0').rstrip('.')}


def standalone(tok, text):
    """숫자 토큰이 다른 숫자의 일부가 아니라 홀로 서 있는가."""
    return re.search(r'(?<![\d.,])' + re.escape(tok) + r'(?![\d.])', text) is not None


def pool():
    """원장 어딘가에 실제로 있는 숫자 전량 — 오탐 방지용 허용 못."""
    P = set()
    for k, (v, t) in QTY.items():
        P |= CANON[k]
    F = FACTS
    for row in F['tyByDate'].values():
        for x in row:
            P |= canon(D(str(x)), 'amt' if isinstance(x, int) else 'rate')
    for row in F['monthTy']:
        for x in row[1:]:
            P |= canon(D(x), 'rate')
    for _, v in F['monthExec']:
        P |= canon(D(v), 'amt')
    for m in F['merchants']:
        P |= canon(D(m[1]), 'amt') | canon(D(m[6]), 'amt')
        for x in m[2:5]:
            P |= canon(D(x), 'rate')
    for k in ('wRange', 'wBound'):
        for x in F[k]:
            P |= canon(D(x), 'rate')
    for k in ('receivables', 'openReceivables', 'sampleReceivables', 'ledgerDays'):
        P |= canon(D(F[k]), 'amt')
    P |= ledger_w6()
    P |= ledger_mr6()
    P |= roster6()
    return P


def roster6():
    """가맹점 8곳의 6자리 값 — 표기 W·S 뒤에 서는 계산값과 그 입력.

    `ledger_facts.json` 의 `merchants` 는 표기 2자리만 싣는다. 칸별 중간 계산 문서는
    그 곳의 6자리 `w6`·`s6` 과 배달 의존도 `b`·플랫폼 구성비 `mix` 를 그대로 적는다.
    못에 없으면 김성호떡볶이 본점의 `3.020016` 처럼 옳은 값이 주간·전구간 W 근처라
    위반으로 잡힌다. 원장 모듈에서 직접 읽는다.
    """
    out = set()
    prec = getcontext().prec
    try:
        # 원장 모듈은 기본 정밀도(28)에서 구성비 합 1 을 검사한다 — ledger_w6 과 같은 이유다.
        getcontext().prec = 28
        sys.path.insert(0, PIPE)
        import daily_ledger as dl
        for x in dl.MERCHANTS:
            for k in ('w6', 's6', 'wraw', 'sraw', 'b'):
                if x.get(k) is not None:
                    out |= canon(D(str(x[k])), 'rate')
            for v in x.get('mix') or ():
                out |= canon(D(str(v)), 'rate')
    except Exception as e:
        print('!! 가맹점 6자리 값을 못 읽었다:', e, file=sys.stderr)
    finally:
        getcontext().prec = prec
    return out


def ledger_mr6():
    """일별 6자리 투자수익율 MR(d-1) — `tyByDate` 의 투자수익 ÷ 투자실행금.

    dm_0901/rounding_rule_0901.md 규칙 1 로 MR(d-1) 도 백분율 표기 기준 6자리에서
    끊고 그 값을 다음 계산에 넣는다. 계산 예시가 그 6자리 값을 그대로 적으므로
    못에 없으면 정상 예시가 위반으로 잡힌다. 원장이 이 열을 따로 싣지 않아
    `tyByDate` 의 투자실행금·투자수익 두 칸에서 같은 규칙으로 낸다.
    """
    out = set()
    for row in FACTS.get('tyByDate', {}).values():
        execu, profit = D(str(row[2])), D(str(row[3]))
        if execu:
            out |= canon(q(profit / execu * 100, 6), 'rate')
    return out


def ledger_w6():
    """일별 6자리 W금융일수 — `ledger_facts.json` 의 `w6ByDate`.

    Q23(6자리 규칙)로 계산 예시가 6자리 일별 W를 쓴다. 그 값들이 주간 W 근처라
    못에 없으면 정상 표가 통째로 위반으로 잡힌다.
    원장이 아직 이 열을 안 실으면 원장 모듈에서 직접 읽는다.
    """
    out = set()
    if FACTS.get('w6ByDate'):
        for v in FACTS['w6ByDate'].values():
            out |= canon(D(str(v)), 'rate')
        return out
    prec = getcontext().prec
    try:
        # 원장 모듈은 기본 정밀도(28)에서 구성비 합 1 을 검사한다.
        # 이 검사기가 올려 둔 40 을 그대로 들고 들어가면 그 검사가 깨진다 — 되돌려 놓고 부른다.
        getcontext().prec = 28
        sys.path.insert(0, PIPE)
        import daily_ledger as dl
        for r in dl.LEDGER:
            out |= canon(r['w6'], 'rate')
    except Exception as e:
        print('!! 일별 6자리 W 를 못 읽었다:', e, file=sys.stderr)
    finally:
        getcontext().prec = prec
    return out


POOL = pool()

STRIP = re.compile(r'<[^>]+>')
NUM_HI = re.compile(r'(?<![\d.])\d{1,3}(?:,\d{3})*\.\d{4,}')
NUM_AMT = re.compile(r'(?<![\d.,])\d{1,3}(?:,\d{3}){2,}(?![\d,])')
NUM_D2 = re.compile(r'(?<![\d.])\d{1,4}\.\d{2}(?=\s*(?:%|일))')


def near(tok):
    """토큰이 어느 원장량 근처인지 — (키, 값, 종류) 목록."""
    raw = tok.replace(',', '')
    try:
        v = D(raw)
    except Exception:
        return []
    hit = []
    for k, (val, kind) in QTY.items():
        if kind == 'amt':
            if val > 0 and abs(v - val) <= AMT_TOL:
                hit.append((k, val, kind))
        else:
            if val > 0 and abs(v - val) / val <= RATE_TOL:
                hit.append((k, val, kind))
    return hit


def excused(text, at, keys):
    """대조값 자리인가 — 표지 + 견주는 원장 값의 정식 표기가 같은 창에 함께 있어야 한다."""
    w = text[max(0, at - WIN): at + WIN]
    if not any(m in w for m in MARKS):
        return None
    for k in keys:
        for c in witness(k):
            if len(c) >= 3 and standalone(c, w):
                return k
    return None


def scan(name, text):
    """한 문서에서 (위반, 대조값으로 넘긴 것, 검사한 토큰 수)."""
    t = STRIP.sub(' ', text) if name.endswith('.html') else text
    bad, kept, seen = [], [], 0
    for rx, tag in ((NUM_HI, '고정밀'), (NUM_AMT, '금액'), (NUM_D2, '두자리')):
        for m in rx.finditer(t):
            tok = m.group(0)
            hits = near(tok)
            if not hits:
                continue
            seen += 1
            if tok in POOL or tok.replace(',', '') in POOL:
                continue
            keys = [k for k, _, _ in hits]
            ex = excused(t, m.start(), keys)
            ctx = re.sub(r'\s+', ' ', t[max(0, m.start() - 60): m.start() + 60]).strip()
            rec = {'tok': tok, 'kind': tag, 'near': keys,
                   'want': sorted(CANON[keys[0]])[:4], 'ctx': ctx}
            if ex:
                rec['대조'] = ex
                kept.append(rec)
            else:
                bad.append(rec)
    return bad, kept, seen


SEED_RX = re.compile(r'<script type="application/json" id="seed">(.*?)</script>', re.S)


def seed_of(name, text):
    """대표 확인 문항 씨앗을 돌려준다 — 원본 JSON 이든 화면에 박힌 것이든."""
    if name.endswith('.json'):
        try:
            return json.loads(text)
        except Exception:
            return None
    m = SEED_RX.search(text)
    if not m:
        return None
    try:
        return json.loads(H.unescape(m.group(1)))
    except Exception:
        return None


def pair_scan(name, text):
    """종전↔바꿈 표의 방향 검사.

    창 기반 대조값 면제는 「종전」 칸과 「바꿈」 칸을 갈라 보지 못한다 — 둘이 붙어 있어서다.
    문항 씨앗은 구조가 있으니 칸을 직접 갈라 본다.
      · 「바꿈」 칸의 숫자는 면제 없이 원장 값이어야 한다
      · 「종전」 칸과 「바꿈」 칸의 숫자가 같으면 대조가 성립하지 않는다
    """
    seed = seed_of(name, text)
    if seed is None:
        return []
    out = []
    numrx = re.compile(r'(?<![\d.])\d{1,3}(?:,\d{3})*(?:\.\d+)?')
    for it in seed.get('items', []):
        rows = it.get('rows') or []
        labs = [r[0] for r in rows if isinstance(r, list) and r]
        if '바꿈' not in labs:
            continue
        for r in rows:
            if not (isinstance(r, list) and len(r) > 1) or r[0] != '바꿈':
                continue
            for rx in (NUM_HI, NUM_AMT, NUM_D2):
                for m in rx.finditer(r[1]):
                    tok = m.group(0)
                    hits = near(tok)
                    if hits and tok not in POOL and tok.replace(',', '') not in POOL:
                        out.append({'tok': tok, 'kind': '바꿈칸',
                                    'near': [k for k, _, _ in hits],
                                    'want': sorted(witness(hits[0][0])),
                                    'ctx': f"{it.get('id')} 「바꿈」 {r[1]}"})
        old = ' '.join(r[1] for r in rows if isinstance(r, list) and len(r) > 1 and r[0] == '종전')
        new = ' '.join(r[1] for r in rows if isinstance(r, list) and len(r) > 1 and r[0] == '바꿈')
        if old and new and set(numrx.findall(old)) == set(numrx.findall(new)):
            out.append({'tok': '', 'kind': '대조없음', 'near': [], 'want': [],
                        'ctx': f"{it.get('id')} 「종전」과 「바꿈」의 숫자가 같다"})
    return out


def read(base, name):
    p = os.path.join(base, name)
    return io.open(p, encoding='utf-8').read() if os.path.exists(p) else None


def run():
    rows, tot_bad, tot_kept, tot_seen = [], 0, 0, 0
    for base, name in TARGETS:
        s = read(base, name)
        if s is None:
            rows.append({'file': name, 'r': 'FAIL', 'why': '파일 없음'})
            tot_bad += 1
            continue
        bad, kept, seen = scan(name, s)
        bad = bad + pair_scan(name, s)
        tot_bad += len(bad); tot_kept += len(kept); tot_seen += seen
        rows.append({'file': name, 'r': 'FAIL' if bad else 'PASS',
                     'checked': seen, 'bad': bad, 'kept': len(kept),
                     'keptList': kept})
    return rows, tot_bad, tot_kept, tot_seen


# ── 판별력 시험 ─────────────────────────────────────────────────
SEED = [('3.107588', '3.108481'), ('117.454437', '117.4207'),
        ('3.992511', '3.992465'), ('2.245629', '2.245603'),
        ('2.25%', '2.24%'), ('180,032,111', '180,032,094')]


def plant(name, text, new, old):
    """옛 값을 한 곳에만 심고 (심은 글자, 사유) 를 돌려준다.

    두 자리를 피한다.
      · 태그 안 — HTML 은 찾기용 속성(`data-q`)에 본문과 같은 글자를 한 벌 더 담는다.
        `scan` 이 태그를 걷어내고 보므로 거기 심으면 검사에 닿지 않아 시험이 헛돈다.
      · 되짚기 대조 창 — 설계상 면제 자리다. 거기밖에 자리가 없으면 심지 않고 그렇게 적는다.
    """
    html_ = name.endswith('.html')
    spots = []
    if html_:
        for m in re.finditer(re.escape(new), text):
            head = text[:m.start()]
            if head.rfind('<') <= head.rfind('>'):        # 태그 밖이다
                spots.append((m.start(), m.end()))
    else:
        i = text.find(new)
        if i >= 0:
            spots.append((i, i + len(new)))
    if not spots:
        return None, '대상없음'
    keys = [k for k, _, _ in near(old)]
    for a, b in spots:
        hurt = text[:a] + old + text[b:]
        t = STRIP.sub(' ', hurt) if html_ else hurt
        at = len(STRIP.sub(' ', text[:a])) if html_ else a
        if excused(t, at, keys) is None:
            return hurt, ''
    return None, '대조자리'


def selftest():
    print('판별력 시험 — 옛 값을 메모리에서 한 건씩 심고 잡히는지 본다\n')
    ok = miss = na = ctx = 0
    for base, name in TARGETS:
        s = read(base, name)
        if s is None:
            continue
        base_bad = len(scan(name, s)[0]) + len(pair_scan(name, s))
        for new, old in SEED:
            hurt, why = plant(name, s, new, old)
            if hurt is None:
                if why == '대조자리':
                    ctx += 1
                else:
                    na += 1
                print(f'  {name:26s} {new:>11s} → {old:<11s}  {why}')
                continue
            n = len(scan(name, hurt)[0]) + len(pair_scan(name, hurt))
            if n > base_bad:
                ok += 1
                print(f'  {name:26s} {new:>11s} → {old:<11s}  잡음')
            else:
                miss += 1
                print(f'  {name:26s} {new:>11s} → {old:<11s}  !! 못 잡음')
    print(f'\n1단 · 제자리 갈아치우기 — 심은 것 {ok+miss}건 · 잡음 {ok} / 못 잡음 {miss} · '
          f'대상없음 {na} · 대조자리뿐 {ctx}')

    # 2단 — 문서에 그 값이 없어 1단을 못 돌린 자리까지 메운다. 옛 값을 문장으로 끼워 넣는다.
    print('\n2단 — 옛 값을 문장으로 끼워 넣고 잡히는지 본다\n')
    ok2 = miss2 = 0
    for base, name in TARGETS:
        s = read(base, name)
        if s is None:
            continue
        b0 = len(scan(name, s)[0]) + len(pair_scan(name, s))
        for new, old in SEED:
            # 대조 표 곁에 붙으면 면제 창에 걸려 시험이 무뎌진다 — 문서 머리에 넣는다
            hurt = '기준 기간 값 ' + old + '\n' + s
            n = len(scan(name, hurt)[0]) + len(pair_scan(name, hurt))
            if n > b0:
                ok2 += 1
            else:
                miss2 += 1
                print(f'  {name:26s} {old:<11s}  !! 못 잡음')
    print(f'2단 · 끼워 넣기 — 심은 것 {ok2+miss2}건 · 잡음 {ok2} / 못 잡음 {miss2}')

    # 3단 — 맞는 값을 같은 자리에 끼워 넣었을 때 잡으면 오탐이다.
    print('\n3단 — 맞는 값을 끼워 넣고 조용한지 본다\n')
    ok3 = bad3 = 0
    for base, name in TARGETS:
        s = read(base, name)
        if s is None:
            continue
        b0 = len(scan(name, s)[0]) + len(pair_scan(name, s))
        for new, old in SEED:
            heal = '기준 기간 값 ' + new + '\n' + s
            n = len(scan(name, heal)[0]) + len(pair_scan(name, heal))
            if n > b0:
                bad3 += 1
                print(f'  {name:26s} {new:<11s}  !! 오탐')
            else:
                ok3 += 1
    print(f'3단 · 맞는 값 — 심은 것 {ok3+bad3}건 · 조용함 {ok3} / 오탐 {bad3}')

    print(f'\n판별력 — 잡아야 할 {ok+miss+ok2+miss2}건 중 {ok+ok2} 잡음 · '
          f'조용해야 할 {ok3+bad3}건 중 {bad3} 오탐')
    return miss + miss2 + bad3


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        sys.exit(1 if selftest() else 0)
    rows, nb, nk, ns = run()
    w = max(len(r['file']) for r in rows)
    for r in rows:
        if r['r'] == 'FAIL' and 'bad' not in r:
            print(f"{r['file']:<{w}}  FAIL  {r['why']}")
            continue
        print(f"{r['file']:<{w}}  {r['r']}  대조 토큰 {r['checked']:3d} · "
              f"대조값 {r['kept']:2d} · 위반 {len(r['bad'])}")
        for b in r['bad']:
            print(f"    !! {b['tok']}  ({b['kind']} · {'/'.join(b['near'])} 근처) "
                  f"기대 {b['want']}\n       … {b['ctx']} …")
    print(f"\n{len(rows)}문서 — 대조 토큰 {ns} · 대조값 통과 {nk} · 위반 {nb}")
    json.dump({'files': rows, 'checked': ns, 'kept': nk, 'bad': nb,
               'qty': {k: str(v) for k, (v, _) in QTY.items()}},
              io.open(os.path.join(PIPE, 'verify_docnums_result.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    sys.exit(1 if nb else 0)
