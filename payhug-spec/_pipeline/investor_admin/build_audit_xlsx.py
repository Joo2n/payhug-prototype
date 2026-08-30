# -*- coding: utf-8 -*-
"""검산 통합문서 생성기 — 2026-09-01 대표 검산 미팅용.

산출: 검산_투자자어드민_20260901.xlsx

모든 셀은 엑셀 수식이다. 파이썬이 낸 값을 박아 넣는 자리는 셋뿐이다.
  ① 입력 시트의 가정값 (근거 자료에서 읽는다)
  ② 채권 시트의 금융일수 Di — 정산주기.xlsx N6:Q370 (2025년 365일 실측)의 40일 슬라이스
  ③ 화면대조 시트의 화면 값 — rescale_decision.md 표에서 읽는다

근거 자료
  /Users/semi/Downloads/정산주기.xlsx        도수 · 평균만기 · 구성비 · MAU
  rescale_decision.md                        로스터 9건 · 규모 · 화면 값
  ceo_definitions.md                         산식 원문 · 할인율
  platform_duration.py                       미지급률 · 과지급률
  daily_ledger.py                            기준일 · 사업자번호 · 대표자
"""
import json, os, re, sys
from datetime import date, timedelta
from decimal import Decimal as D, ROUND_HALF_UP, ROUND_FLOOR

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule

BASE = os.path.dirname(os.path.abspath(__file__))
CYCLE_XLSX = os.path.expanduser('~/Downloads/정산주기.xlsx')
OUT = os.path.join(BASE, '검산_투자자어드민_20260901.xlsx')
ORDER = ('card', 'bm', 'cpe', 'yo')
LABEL = {'card': '카드사', 'bm': '배달의민족', 'cpe': '쿠팡이츠', 'yo': '요기요'}
WINDOW = 40                       # 선정산일 축 길이(일)


# ══════════════════════════════════════════════════════════════════
# 1. 근거 자료 읽기
# ══════════════════════════════════════════════════════════════════
def read_cycle():
    wb = openpyxl.load_workbook(CYCLE_XLSX, data_only=True)
    ws = wb['정산주기']
    col = {'yo': 'N', 'cpe': 'O', 'bm': 'P', 'card': 'Q'}
    avg_cell = {'yo': 'H16', 'cpe': 'H24', 'bm': 'H32', 'card': 'H40'}
    mix_cell = {'yo': 'I16', 'cpe': 'I24', 'bm': 'I32', 'card': 'I40'}
    freq, avg, mix, raw = {}, {}, {}, {}
    for k, c in col.items():
        vals = [ws['%s%d' % (c, r)].value for r in range(6, 371)]
        assert len(vals) == 365 and all(isinstance(v, int) for v in vals), k
        raw[k] = vals
        f = {}
        for v in vals:
            f[v] = f.get(v, 0) + 1
        freq[k] = dict(sorted(f.items()))
        avg[k] = ws[avg_cell[k]].value
        mix[k] = ws[mix_cell[k]].value
    wsb = wb['비중']
    mau = [('배민', wsb['D4'].value), ('쿠팡이츠', wsb['E4'].value), ('요기요', wsb['F4'].value)]
    return dict(freq=freq, avg=avg, mix=mix, mau=mau, wavg=ws['H41'].value,
                obs_days=365, raw=raw, src_xlsx=os.path.basename(CYCLE_XLSX))


def _md():
    return open(os.path.join(BASE, 'rescale_decision.md'), encoding='utf-8').read()


def read_roster():
    txt = _md()
    rx = re.compile(r'^\|\s*(고액|평범|소액)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|'
                    r'\s*([\d,]+)\s*\|\s*([\d,]+)\s*\|\s*([\d.]+)\s*\|\s*([\d,]+)\s*\|'
                    r'\s*([\d.]+)\s*\|\s*([\d.]+)%\s*\|\s*([\d.]+)%\s*\|\s*([\d.]+)%\s*\|')
    rows = []
    for ln in txt.splitlines():
        m = rx.match(ln.strip())
        if m:
            rows.append(dict(tier=m.group(1), name=m.group(2), biz=m.group(3), item=m.group(4),
                             flow=int(m.group(5).replace(',', '')),
                             daily=int(m.group(6).replace(',', '')), b=m.group(7),
                             invest=int(m.group(8).replace(',', '')), w=m.group(9),
                             s=m.group(10), ty=m.group(11), share=m.group(12)))
    assert len(rows) == 9, len(rows)
    for ln in txt.splitlines():
        m = re.match(r'^\|\s*(M2026-\d{4})\s*\|\s*([^|]+?)\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|'
                     r'\s*(\d{4}-\d{2}-\d{2})\s*\|', ln.strip())
        if m:
            for r in rows:
                if r['name'] == m.group(2):
                    r['mid'], r['contract'] = m.group(1), m.group(4)
    assert all('mid' in r for r in rows)
    return rows


def read_md_pairs(*sections):
    """rescale_decision.md 의 지정 절에서 '항목 | 현행 | 새 값' 3열 표를 걷는다."""
    out, cur = {}, None
    for ln in _md().splitlines():
        s = ln.strip()
        if s.startswith('#'):
            cur = s.lstrip('# ').strip()
        if cur not in sections:
            continue
        m = re.match(r'^\|\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|$', s)
        if m and not m.group(1).startswith('---'):
            out.setdefault(m.group(1), m.group(3).replace('**', '').strip())
    return out


def read_period_table():
    """rescale_decision.md §5-B 조회기간 표 — PSA·PSM·PSC·④·⑤."""
    for ln in _md().splitlines():
        m = re.match(r'^\|\s*기본 일주일 7일\s*\|\s*([\d,]+)\s*\|\s*([\d,]+)\s*\|\s*([\d,]+)\s*\|'
                     r'\s*([\d.]+)%\s*\|\s*\*\*([\d.]+)%\*\*\s*\|', ln.strip())
        if m:
            return dict(psa=int(m.group(1).replace(',', '')),
                        psm=int(m.group(2).replace(',', '')),
                        psc=int(m.group(3).replace(',', '')),
                        p4=float(m.group(4)), p5=float(m.group(5)))
    raise AssertionError('§5-B 표 없음')


def read_rates():
    sys.path.insert(0, BASE)
    import platform_duration as pd
    return {k: (float(pd.UNPAID[k]), float(pd.OVERPAID[k])) for k in ORDER}


def read_meta():
    src = open(os.path.join(BASE, 'daily_ledger.py'), encoding='utf-8').read()
    m = re.search(r'ASOF\s*=\s*date\((\d+),\s*(\d+),\s*(\d+)\)', src)
    asof = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    blk = src.split('BOOKROWS = [', 1)[1].split('\n]', 1)[0]
    meta = {}
    for m in re.finditer(r"\('(M2026-\d{4})',\s*'([^']+)',\s*'([^']+)',\s*'([^']+)'", blk):
        meta[m.group(2).strip()] = (m.group(1), m.group(3), m.group(4))
    return asof, meta


def read_rate_pct():
    txt = open(os.path.join(BASE, 'ceo_definitions.md'), encoding='utf-8').read()
    m = re.search(r'유동화투자자의 할인율 = ([\d.]+)%', txt)
    return float(m.group(1))


def read_definitions():
    txt = open(os.path.join(BASE, 'ceo_definitions.md'), encoding='utf-8').read()
    out, sec = [], ''
    for ln in txt.splitlines():
        s = ln.strip()
        if s.startswith('## '):
            sec = s[3:].strip()
        elif s.startswith('- '):
            out.append((sec, s[2:].strip()))
    return out


# ══════════════════════════════════════════════════════════════════
# 2. 채권 원장 배정 — 엑셀과 같은 산술로 파이썬에서 먼저 푼다
# ══════════════════════════════════════════════════════════════════
def xr(x, n=0):
    return float(D(repr(float(x))).quantize(D(1).scaleb(-n), rounding=ROUND_HALF_UP))


def xrd(x, n=0):
    return float(D(repr(float(x))).quantize(D(1).scaleb(-n), rounding=ROUND_FLOOR))


def base_model(cyc, roster, rates, rate):
    dur = {p: sum(d * n for d, n in cyc['freq'][p].items()) / cyc['obs_days'] for p in ORDER}
    ed2 = {p: sum(d * d * n for d, n in cyc['freq'][p].items()) / cyc['obs_days'] for p in ORDER}
    tot_mau = sum(v for _, v in cyc['mau'])
    dsh = {'bm': cyc['mau'][0][1] / tot_mau, 'cpe': cyc['mau'][1][1] / tot_mau,
           'yo': cyc['mau'][2][1] / tot_mau}
    M = len(roster)
    b = [float(r['b']) for r in roster]
    flow = [r['flow'] for r in roster]
    mix = [[(1 - b[m]) if p == 'card' else b[m] * dsh[p] for p in ORDER] for m in range(M)]
    durm = [sum(mix[m][i] * dur[ORDER[i]] for i in range(4)) for m in range(M)]
    w_flow = sum(flow[m] * durm[m] for m in range(M)) / sum(flow)
    return dict(dur=dur, ed2=ed2, dsh=dsh, mix=mix, durm=durm, w_flow=w_flow, M=M, flow=flow)


def money(mo, exec_target, rate):
    M = mo['M']
    tot = exec_target / ((1 - rate) * mo['w_flow'])
    scale = tot / sum(mo['flow'])
    N = [mo['flow'][m] * scale for m in range(M)]
    net = [[xr(N[m] * mo['mix'][m][i]) for i in range(4)] for m in range(M)]
    ai = [[xr(net[m][i] * (1 - rate)) for i in range(4)] for m in range(M)]
    W = sum(N[m] * mo['durm'][m] for m in range(M)) / sum(N)
    return dict(N=N, net=net, ai=ai, tot=sum(N), W=W, scale=scale)


def _fill(vals, c):
    """문턱 c+1..13 (선정산일 위치 39-c .. 27) 에 미달값(v <= k-1) 배정.

    정산예정일이 축 끝(기준일)까지 고르게 차도록 아직 안 쓴 가장 늦은 정산예정일을 고른다.
    """
    pool = sorted(vals)
    fill, taken = {}, set()
    for k in range(c + 1, 14):
        best = None
        for t in range(len(pool)):
            v = pool[t]
            if v > k - 1:
                continue
            due = WINDOW - k + v
            key = (due in taken, -due)
            if best is None or key < best[0]:
                best = (key, t, due)
        if best is None:
            return None
        fill[k] = pool.pop(best[1])
        taken.add(best[2])
    return fill, pool


def _tail_sums(pool, c):
    """문턱 1..c 에 배정 가능한 c개 값의 합 → 선택 내역.

    오름차순 선택 s_1<=..<=s_c 가 s_j >= j 여야 배정된다.
    같은 조건이 '값 v 이하로 고른 개수 <= v' 다.
    """
    cnt = [0] * 14
    for v in pool:
        cnt[v] += 1
    cur = {(0, 0): []}
    for v in range(1, 14):
        nxt = {}
        for (took, tot), pick in cur.items():
            for k in range(0, min(cnt[v], c - took) + 1):
                t2 = took + k
                if t2 > v:
                    continue
                key = (t2, tot + v * k)
                if key not in nxt:
                    nxt[key] = pick + [(v, k)]
        cur = nxt
    return {tot: pick for (took, tot), pick in cur.items() if took == c}


def _pick(sums, c, u):
    """합이 u 인 선택 → 문턱 k -> 값."""
    if u not in sums:
        return None
    vals = []
    for v, k in sums[u]:
        vals.extend([v] * k)
    vals.sort()
    return {j + 1: vals[j] for j in range(c)}


def _spread(head, tail, rnd, dsum_target, lam=2.0):
    """머리 27건 배치.

    ① 정산예정일 13..39 를 한 건씩 채워 일별 표의 하루 건수를 고르게 한다
    ② 그 구간에 든 채권의 금융일수 합을 27 x 플랫폼 평균만기에 맞춰 PSD 쏠림을 없앤다
    """
    tcnt = [0] * 80
    tsum = 0
    for i in range(13):
        t = 27 + i + tail[i]
        tcnt[t] += 1
        if 13 <= t <= 39:
            tsum += tail[i]

    def score(seq):
        cnt = list(tcnt)
        ds = tsum
        for i, v in enumerate(seq):
            cnt[i + v] += 1
            if 13 <= i + v <= 39:
                ds += v
        c = sum(abs(cnt[t] - 1) for t in range(13, 40))
        c += sum(max(0, cnt[t] - 1) for t in range(1, 13))
        return c + lam * abs(ds - dsum_target), c

    starts = [sorted(head), sorted(head, reverse=True)] + \
             [sorted(head, key=lambda x: rnd.random()) for _ in range(6)]
    best = None
    for seq in starts:
        cur, _c = score(seq)
        for _ in range(1500):
            i, j = rnd.randrange(27), rnd.randrange(27)
            if seq[i] == seq[j]:
                continue
            seq[i], seq[j] = seq[j], seq[i]
            nc, _c2 = score(seq)
            if nc <= cur:
                cur = nc
            else:
                seq[i], seq[j] = seq[j], seq[i]
        if best is None or cur < best[0]:
            best = (cur, list(seq))
        if cur == 0:
            break
    return best


def _realize(vals, c, u, rnd, dsum_target):
    f = _fill(vals, c)
    if f is None:
        return None
    fill, pool = f
    chosen = _pick(_tail_sums(pool, c), c, u)
    if chosen is None:
        return None
    best = None
    for _ in range(12):
        rest = list(pool)
        for v in chosen.values():
            rest.remove(v)
        tail = [(chosen[k] if k <= c else fill[k]) for k in range(13, 0, -1)]
        sc, head = _spread(rest, tail, rnd, dsum_target)
        seq = head + tail
        got = [seq[i] for i in range(WINDOW) if seq[i] >= WINDOW - i]
        if len(seq) != WINDOW or len(got) != c or sum(got) != u:
            continue
        if best is None or sc < best[0]:
            best = (sc, seq)
        if sc == 0:
            break
    return best[1] if best else None


def _hit(w, opts, target, rnd, cap=3000000):
    n = len(w)
    idx = sorted(range(n), key=lambda t: -w[t])
    mn, mx = [0] * (n + 1), [0] * (n + 1)
    for t in range(n - 1, -1, -1):
        j = idx[t]
        mn[t] = mn[t + 1] + w[j] * min(opts[j])
        mx[t] = mx[t + 1] + w[j] * max(opts[j])
    cnt = [0]

    def dfs(t, rem):
        if cnt[0] > cap:
            return None
        cnt[0] += 1
        if t == n:
            return {} if rem == 0 else None
        if rem < mn[t] or rem > mx[t]:
            return None
        j = idx[t]
        mid = (rem - (mn[t + 1] + mx[t + 1]) / 2) / w[j]
        for x in sorted(opts[j], key=lambda v: (abs(v - mid), rnd.random())):
            r = dfs(t + 1, rem - w[j] * x)
            if r is not None:
                r[j] = x
                return r
        return None

    return dfs(0, target)


def assign(cyc, mo, mn, exec_target, seed=20260901):
    import random
    rnd = random.Random(seed)
    raw = cyc['raw']
    pairs = [(m, i) for m in range(mo['M']) for i in range(4)]
    AI = [mn['ai'][m][i] for (m, i) in pairs]
    SAI = sum(AI)
    W = mn['W']

    stot_opts, off_of = [], []
    for (m, i) in pairs:
        seq, dd = raw[ORDER[i]], {}
        for o in range(365):
            dd.setdefault(sum(seq[(o + j) % 365] for j in range(WINDOW)), o)
        stot_opts.append(sorted(dd))
        off_of.append(dd)
    sol1 = _hit(AI, stot_opts, round(WINDOW * W * SAI), rnd)
    assert sol1 is not None, '슬라이스 해 없음'
    offs = {pairs[j]: off_of[j][sol1[j]] for j in range(len(pairs))}
    vals = {k: [raw[ORDER[k[1]]][(offs[k] + j) % 365] for j in range(WINDOW)] for k in pairs}

    SUMS, copts = {}, []
    for (m, i) in pairs:
        a, ok = round(mo['dur'][ORDER[i]]), []
        for c in range(max(1, a - 1), a + 3):
            f = _fill(vals[(m, i)], c)
            if f is None:
                continue
            ss = _tail_sums(f[1], c)
            if ss:
                SUMS[(m, i, c)] = ss
                ok.append(c)
        copts.append(ok)
    sol2 = _hit(AI, copts, exec_target, rnd)
    assert sol2 is not None, '미회수 건수 해 없음'
    cs = [sol2[j] for j in range(len(pairs))]

    A = sum(AI[t] * cs[t] for t in range(len(pairs)))
    wu = (sum(AI[t] * mo['ed2'][ORDER[pairs[t][1]]] for t in range(len(pairs)))
          / sum(AI[t] * mo['dur'][ORDER[pairs[t][1]]] for t in range(len(pairs))))
    uopts = []
    for t, k in enumerate(pairs):
        ss = SUMS[(k[0], k[1], cs[t])]
        nat = cs[t] * mo['ed2'][ORDER[k[1]]] / mo['dur'][ORDER[k[1]]]
        near = sorted(x for x in ss if int(nat) - 3 <= x <= int(nat) + 4)
        uopts.append(near or sorted(ss))
    sol3 = _hit(AI, uopts, round(wu * A), rnd)
    assert sol3 is not None, '미회수 d합 해 없음'

    seqs = {}
    for t, k in enumerate(pairs):
        s = _realize(vals[k], cs[t], sol3[t], rnd,
                     27 * mo['dur'][ORDER[k[1]]])
        assert s is not None, ('배치 실패', k)
        seqs[k] = s
    return seqs


# ══════════════════════════════════════════════════════════════════
# 3. 서식
# ══════════════════════════════════════════════════════════════════
HEAD = PatternFill('solid', fgColor='1F3864')
SUB = PatternFill('solid', fgColor='D9E2F3')
CHK = PatternFill('solid', fgColor='FFF2CC')
BAD = PatternFill('solid', fgColor='FFC7CE')
GOOD = PatternFill('solid', fgColor='C6EFCE')
THIN = Side(style='thin', color='BFBFBF')
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
FW = Font(color='FFFFFF', bold=True, size=10)
FB = Font(bold=True, size=10)
F_ = Font(size=10)
M0 = '#,##0'
M2 = '#,##0.00'
D6 = '0.000000'
D8 = '0.00000000'
P2 = '0.00'
DT = 'yyyy-mm-dd'


def head(ws, row, labels, start=1, fill=HEAD):
    for i, t in enumerate(labels):
        c = ws.cell(row=row, column=start + i, value=t)
        c.fill = fill
        c.font = FW if fill is HEAD else FB
        c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        c.border = BOX
    ws.row_dimensions[row].height = 30


def put(ws, row, col, value, fmt=None, bold=False, fill=None):
    c = ws.cell(row=row, column=col, value=value)
    c.font = FB if bold else F_
    if fmt:
        c.number_format = fmt
    if fill:
        c.fill = fill
    c.border = BOX
    return c


def widths(ws, spec):
    for col, w in spec.items():
        ws.column_dimensions[col].width = w


# ══════════════════════════════════════════════════════════════════
# 4. 통합문서 조립
# ══════════════════════════════════════════════════════════════════
def build():
    cyc = read_cycle()
    roster = read_roster()
    rates = read_rates()
    rate_pct = read_rate_pct()
    rate = rate_pct / 100
    asof, meta = read_meta()
    md = read_md_pairs('9-A. 불변식', '9-B. 원장이 다시 내는 값')
    per = read_period_table()
    defs = read_definitions()

    exec_target = int(md['투자실행액'].replace(',', ''))
    cash = int(md['순현금'].replace(',', ''))
    _n = len(roster)
    avg_daily = int(re.search(r'\|\s*\**%d\**\s*\|\s*\**([\d,]+)\**\s*\|' % _n,
                              _md()).group(1).replace(',', ''))

    mo = base_model(cyc, roster, rates, rate)
    mn = money(mo, exec_target, rate)
    seqs = assign(cyc, mo, mn, exec_target)

    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    NAME = {}

    def name(key, sheet, ref):
        NAME[key] = "'%s'!%s" % (sheet, ref) if ' ' in sheet else '%s!%s' % (sheet, ref)
        wb.defined_names.add(DefinedName(key, attr_text=NAME[key]))

    # ── 입력 ────────────────────────────────────────────────────
    ws = wb.create_sheet('입력')
    widths(ws, {'A': 16, 'B': 26, 'C': 20, 'D': 8, 'E': 46, 'F': 12, 'G': 14,
                'H': 14, 'I': 18})
    head(ws, 1, ['구분', '항목', '값', '단위', '출처'])
    rows = [
        ('요율', '유동화투자자의 할인율', rate, '비율', 'ceo_definitions.md [1번 이미지]'),
        ('요율', '할인율(%)', '=C2*100', '%', 'C2 x 100'),
        ('요율', '연일수', 365, '일', 'ceo_definitions.md ty수익율'),
        ('규모', '투자실행액 목표', exec_target, '원', 'rescale_decision.md 9-A'),
        ('규모', '순현금', cash, '원', 'rescale_decision.md 9-A'),
        ('규모', '가맹점 평균 하루 선정산액', avg_daily, '원', 'rescale_decision.md 4-A'),
        ('기간', '기준일 D', asof, '날짜', 'daily_ledger.py ASOF'),
        ('기간', '선정산일 축 시작', '=C8-%d' % (WINDOW - 1), '날짜', '축 %d일' % WINDOW),
        ('기간', '일별 표 시작', asof - timedelta(days=26), '날짜', '전량 커버 구간 시작'),
        ('기간', '일별 표 종료', '=C8', '날짜', '기준일'),
        ('기간', '조회기간 시작', '=C8-6', '날짜', 'ceo_definitions.md default 일주일'),
        ('기간', '조회기간 종료', '=C8', '날짜', '기준일'),
        ('기간', 'S표본 시작', '=C8-20', '날짜', 'ceo_definitions.md 표본집합 D-20'),
        ('기간', 'S표본 종료', '=C8-11', '날짜', 'ceo_definitions.md 표본집합 D-11'),
    ]
    fmts = [D8, P2, M0, M0, M0, M0, DT, DT, DT, DT, DT, DT, DT, DT]
    keys = ['할인율', '할인율퍼센트', '연일수', '투자실행액목표', '순현금', '가맹점평균',
            '기준일', '축시작', '일별시작', '일별종료', '조회시작', '조회종료',
            '표본시작', '표본종료']
    for i, (g, lab, val, unit, src) in enumerate(rows):
        r = 2 + i
        put(ws, r, 1, g)
        put(ws, r, 2, lab, bold=True)
        put(ws, r, 3, val, fmts[i], fill=CHK)
        put(ws, r, 4, unit)
        put(ws, r, 5, src)
        name(keys[i], '입력', '$C$%d' % r)

    head(ws, 17, ['스위치', '선택', '선택지', '산출 위치'], fill=SUB)
    sw = [('① W금융일수 모집단', '대상정산금채권 전체',
           '대상정산금채권 전체 / 만기 도래분만 / 미회수 잔량만', '기간집계 B21'),
          ('② W 표기 자릿수', 2, '1 / 2', '기간집계 B22'),
          ('③ 가맹점 수', len(roster), '1 ~ %d' % len(roster), '가맹점 G열'),
          ('④ 산출 방향', 'A', 'A 자산에서 출발 / B 가맹점에서 출발', '가맹점 P열')]
    swkeys = ['SW_모집단', 'SW_자릿수', 'SW_가맹점수', 'SW_방향']
    for i, (lab, val, opt, where) in enumerate(sw):
        r = 18 + i
        put(ws, r, 1, lab, bold=True)
        put(ws, r, 2, val, fill=CHK)
        put(ws, r, 3, opt)
        put(ws, r, 4, where)
        name(swkeys[i], '입력', '$B$%d' % r)
    for rng, opts in [('B18', '"대상정산금채권 전체,만기 도래분만,미회수 잔량만"'),
                      ('B19', '"1,2"'),
                      ('B20', '"%s"' % ','.join(str(x) for x in range(1, len(roster) + 1))),
                      ('B21', '"A,B"')]:
        dv = DataValidation(type='list', formula1=opts, allow_blank=False)
        ws.add_data_validation(dv)
        dv.add(ws[rng])

    head(ws, 23, ['코드', '플랫폼', '구성비', '미지급률', '과지급률', '출처'], fill=SUB)
    for i, p in enumerate(ORDER):
        r = 24 + i
        put(ws, r, 1, p)
        put(ws, r, 2, LABEL[p], bold=True)
        put(ws, r, 3, cyc['mix'][p], D8, fill=CHK)
        put(ws, r, 4, rates[p][0], D6, fill=CHK)
        put(ws, r, 5, rates[p][1], D6, fill=CHK)
        put(ws, r, 6, '%s 정산주기 I열 · platform_duration.py' % cyc['src_xlsx'])
    put(ws, 28, 2, '합계', bold=True)
    put(ws, 28, 3, '=SUM(C24:C27)', D8, bold=True, fill=CHK)
    name('플랫폼코드범위', '입력', '$A$24:$A$27')
    name('플랫폼명범위', '입력', '$B$24:$B$27')
    name('구성비범위', '입력', '$C$24:$C$27')
    name('미지급률범위', '입력', '$D$24:$D$27')
    name('과지급률범위', '입력', '$E$24:$E$27')

    head(ws, 30, ['배달앱', 'MAU', '배달 3사 내부 배분', '출처'], fill=SUB)
    for i, (nm, v) in enumerate(cyc['mau']):
        r = 31 + i
        put(ws, r, 1, nm, bold=True)
        put(ws, r, 2, v, M0, fill=CHK)
        put(ws, r, 3, '=B%d/$B$34' % r, D8)
        put(ws, r, 4, '%s 비중 D4:F4' % cyc['src_xlsx'])
    put(ws, 34, 1, '계', bold=True)
    put(ws, 34, 2, '=SUM(B31:B33)', M0, bold=True)
    put(ws, 34, 3, '=SUM(C31:C33)', D8, bold=True)
    name('배달배분범위', '입력', '$C$31:$C$33')

    head(ws, 36, ['순번', '사업자ID', '상호', '업종', '품목', '계약일', 'flow 상수',
                  '배달 의존도 b', '하루 선정산액(방향 B)'], fill=SUB)
    for i, r0 in enumerate(roster):
        r = 37 + i
        put(ws, r, 1, i + 1)
        put(ws, r, 2, r0['mid'])
        put(ws, r, 3, r0['name'], bold=True)
        put(ws, r, 4, r0['biz'])
        put(ws, r, 5, r0['item'])
        put(ws, r, 6, date(*[int(x) for x in r0['contract'].split('-')]), DT)
        put(ws, r, 7, r0['flow'], M0, fill=CHK)
        put(ws, r, 8, float(r0['b']), D8, fill=CHK)
        put(ws, r, 9, r0['daily'], M0, fill=CHK)
    R9 = 36 + len(roster)
    put(ws, R9 + 1, 3, '합계', bold=True)
    put(ws, R9 + 1, 7, '=SUM(G37:G%d)' % R9, M0, bold=True)
    put(ws, R9 + 1, 9, '=SUM(I37:I%d)' % R9, M0, bold=True)
    name('순번범위', '입력', '$A$37:$A$%d' % R9)
    name('상호범위', '입력', '$C$37:$C$%d' % R9)
    name('flow범위', '입력', '$G$37:$G$%d' % R9)
    name('b범위', '입력', '$H$37:$H$%d' % R9)
    name('하루입력범위', '입력', '$I$37:$I$%d' % R9)

    # ── 플랫폼 ──────────────────────────────────────────────────
    ws = wb.create_sheet('플랫폼')
    widths(ws, dict({'A': 8, 'B': 14}, **{get_column_letter(3 + i): 6 for i in range(13)}))
    widths(ws, {'P': 12, 'Q': 14, 'R': 15})
    head(ws, 1, ['코드', '플랫폼'] + list(range(1, 14)) + ['도수 합', 'Σ(d x 도수)',
                                                          'Σ(d² x 도수)'])
    for i, p in enumerate(ORDER):
        r = 2 + i
        put(ws, r, 1, p)
        put(ws, r, 2, LABEL[p], bold=True)
        for d in range(1, 14):
            put(ws, r, 2 + d, cyc['freq'][p].get(d, 0), M0, fill=CHK)
        put(ws, r, 16, '=SUM(C%d:O%d)' % (r, r), M0, bold=True)
        put(ws, r, 17, '=SUMPRODUCT($C$1:$O$1,C%d:O%d)' % (r, r), M0)
        put(ws, r, 18, '=SUMPRODUCT($C$1:$O$1,$C$1:$O$1,C%d:O%d)' % (r, r), M0)
    put(ws, 6, 2, '합계', bold=True)
    put(ws, 6, 16, '=SUM(P2:P5)', M0, bold=True)

    head(ws, 8, ['코드', '플랫폼', '구성비', '평균 만기 E[d]', 'E[d²]', 'E[d²]/E[d]',
                 '미지급률', '과지급률', '미지급-과지급', '대표 엑셀 평균', '차'], fill=SUB)
    for i, p in enumerate(ORDER):
        r, s = 9 + i, 2 + i
        put(ws, r, 1, p)
        put(ws, r, 2, LABEL[p], bold=True)
        put(ws, r, 3, '=INDEX(구성비범위,%d)' % (i + 1), D8)
        put(ws, r, 4, '=Q%d/P%d' % (s, s), D8)
        put(ws, r, 5, '=R%d/P%d' % (s, s), D8)
        put(ws, r, 6, '=E%d/D%d' % (r, r), D6)
        put(ws, r, 7, '=INDEX(미지급률범위,%d)' % (i + 1), D6)
        put(ws, r, 8, '=INDEX(과지급률범위,%d)' % (i + 1), D6)
        put(ws, r, 9, '=G%d-H%d' % (r, r), D6)
        put(ws, r, 10, cyc['avg'][p], D8)
        put(ws, r, 11, '=D%d-J%d' % (r, r), '0.00E+00', fill=CHK)
    put(ws, 13, 2, '가중', bold=True)
    put(ws, 13, 3, '=SUM(C9:C12)', D8, bold=True)
    put(ws, 13, 4, '=SUMPRODUCT(C9:C12,D9:D12)', D8, bold=True)
    put(ws, 13, 5, '=SUMPRODUCT(C9:C12,E9:E12)', D8, bold=True)
    put(ws, 13, 6, '=E13/D13', D6, bold=True)
    name('만기범위', '플랫폼', '$D$9:$D$12')
    name('Ed2범위', '플랫폼', '$E$9:$E$12')

    head(ws, 15, ['항목', '값', '산식'], fill=SUB)
    pf = [('구성비 합', '=SUM(구성비범위)', 'SUM(구성비)', D8),
          ('W금융일수 (구성비 x 만기)', '=SUMPRODUCT(구성비범위,만기범위)',
           'Σ 구성비 x 평균만기', D8),
          ('대표 엑셀 가중평균 H41', cyc['wavg'], '%s 정산주기 H41' % cyc['src_xlsx'], D8),
          ('차', '=B17-B18', 'B17 - B18', '0.00E+00'),
          ('가중 E[d²]', '=SUMPRODUCT(구성비범위,Ed2범위)', 'Σ 구성비 x E[d²]', D8),
          ('미회수 이론 W', '=B20/B17', '가중 E[d²] / W', D6),
          ('Ty수익율(%) — 구성비 W 기준', '=할인율퍼센트*연일수/ROUND(B17,SW_자릿수)',
           '할인율 x 365 / 표기 W', P2)]
    for i, (lab, val, f, fmt) in enumerate(pf):
        r = 16 + i
        put(ws, r, 1, lab, bold=True)
        put(ws, r, 2, val, fmt, fill=CHK)
        put(ws, r, 3, f)
    widths(ws, {'A': 30, 'B': 22, 'C': 34})

    # ── 가맹점 ──────────────────────────────────────────────────
    ws = wb.create_sheet('가맹점')
    cols = ['순번', '사업자ID', '상호', '업종', '품목', '계약일', '사용', 'flow 상수',
            '배달 의존도 b', '카드', '배민', '쿠팡이츠', '요기요', '구성비 합',
            '가맹점 만기', '하루 선정산액', '하루 Ai', '투자금액', '비중', '표기 W',
            '가중 미지급률', '가중 과지급률', 'S입금부족율(%)', 'Ty수익율(%)', '구간',
            '결정안 하루 선정산액', '차', '결정안 투자금액', '차']
    head(ws, 1, cols)
    n = len(roster)
    last = 2 + n                      # 가맹점 합계 행
    RATE_ROW = last + 5              # 산출 블록의 '배율 (방향 A)' 행
    for i, r0 in enumerate(roster):
        r, src = 2 + i, 37 + i
        put(ws, r, 1, '=입력!A%d' % src)
        put(ws, r, 2, '=입력!B%d' % src)
        put(ws, r, 3, '=입력!C%d' % src, bold=True)
        put(ws, r, 4, '=입력!D%d' % src)
        put(ws, r, 5, '=입력!E%d' % src)
        put(ws, r, 6, '=입력!F%d' % src, DT)
        put(ws, r, 7, '=IF(A%d<=SW_가맹점수,1,0)' % r)
        put(ws, r, 8, '=입력!G%d' % src, M0)
        put(ws, r, 9, '=입력!H%d' % src, D8)
        put(ws, r, 10, '=G{0}*(1-I{0})'.format(r), D6)
        for j in range(3):
            put(ws, r, 11 + j, '=G{0}*I{0}*INDEX(배달배분범위,{1})'.format(r, j + 1), D6)
        put(ws, r, 14, '=SUM(J%d:M%d)' % (r, r), D6)
        put(ws, r, 15, '=' + '+'.join('%s%d*INDEX(만기범위,%d)' % (get_column_letter(10 + j), r,
                                                                 j + 1) for j in range(4)), D6)
        put(ws, r, 16,
            '=IF(SW_방향="A",G{0}*H{0}*$B${2},G{0}*입력!I{1})'.format(r, src, RATE_ROW), M0)
        put(ws, r, 17, '=P%d*(1-할인율)' % r, M0)
        put(ws, r, 18, '=P{0}*(1-할인율)*O{0}'.format(r), M0)
        put(ws, r, 19, '=IF($R$%d=0,0,R%d/$R$%d)' % (last, r, last), '0.0%')
        put(ws, r, 20, '=IF(G%d=0,"",ROUND(O%d,SW_자릿수))' % (r, r))
        put(ws, r, 21, '=' + '+'.join('%s%d*INDEX(미지급률범위,%d)' % (get_column_letter(10 + j),
                                                                     r, j + 1)
                                      for j in range(4)), D8)
        put(ws, r, 22, '=' + '+'.join('%s%d*INDEX(과지급률범위,%d)' % (get_column_letter(10 + j),
                                                                     r, j + 1)
                                      for j in range(4)), D8)
        put(ws, r, 23, '=IF(G%d=0,"",(U%d-V%d)/(1-할인율)*100)' % (r, r, r), P2)
        put(ws, r, 24, '=IF(G%d=0,"",할인율퍼센트*연일수/T%d)' % (r, r), P2)
        put(ws, r, 25, '=IF(G%d=0,"",IF(P%d>=5000000,"고액",IF(P%d>=2000000,"평범","소액")))'
            % (r, r, r))
        put(ws, r, 26, r0['daily'], M0)
        put(ws, r, 27, '=P%d-Z%d' % (r, r), M0, fill=CHK)
        put(ws, r, 28, r0['invest'], M0)
        put(ws, r, 29, '=R%d-AB%d' % (r, r), M0, fill=CHK)
    for col, f in [(7, 'SUM'), (8, 'SUM'), (16, 'SUM'), (17, 'SUM'), (18, 'SUM'), (19, 'SUM')]:
        L = get_column_letter(col)
        put(ws, last, col, '=%s(%s2:%s%d)' % (f, L, L, last - 1),
            '0.0%' if col == 19 else M0, bold=True)
    put(ws, last, 3, '합계', bold=True)
    put(ws, last, 15, '=IF(P%d=0,0,SUMPRODUCT(P2:P%d,O2:O%d)/P%d)' % (last, last - 1, last - 1,
                                                                      last), D8, bold=True)
    put(ws, last, 20, '=ROUND(O%d,SW_자릿수)' % last, bold=True)

    b0 = last + 2
    head(ws, b0, ['항목', '값', '산식'], fill=SUB)
    gf = 'SUMPRODUCT(G2:G%d,H2:H%d)' % (last - 1, last - 1)
    gfd = 'SUMPRODUCT(G2:G%d,H2:H%d,O2:O%d)' % (last - 1, last - 1, last - 1)
    blk = [('flow 가중 만기 W_flow', '=IF(%s=0,0,%s/%s)' % (gf, gfd, gf),
            'Σ(사용 x flow x 만기) / Σ(사용 x flow)', D8),
           ('하루 선정산액 합계 (방향 A)', '=IF(B%d=0,0,투자실행액목표/((1-할인율)*B%d))'
            % (b0 + 1, b0 + 1), '투자실행액 / (1-r) / W_flow', M2),
           ('배율 (방향 A)', '=IF(%s=0,0,B%d/%s)' % (gf, b0 + 2, gf),
            '하루 선정산액 합계 / Σ(사용 x flow)', D8),
           ('하루 선정산액 합계 (적용)', '=P%d' % last, 'Σ 하루 선정산액', M2),
           ('금액가중 W금융일수', '=O%d' % last, 'Σ(하루선정산액 x 만기) / Σ 하루선정산액', D8),
           ('투자실행액 (모집단 산식)', '=B%d*(1-할인율)*B%d' % (b0 + 4, b0 + 5),
            '합계 x (1-r) x W', M2),
           ('가맹점 수 (적용)', '=SUM(G2:G%d)' % (last - 1), 'Σ 사용', M0),
           ('가맹점 수 (방향 A 산출)', '=IF(가맹점평균=0,0,B%d/가맹점평균)' % (b0 + 4),
            '하루 선정산액 합계 / 가맹점 평균', '0.0000'),
           ('곳당 평균 하루 선정산액', '=IF(B%d=0,0,B%d/B%d)' % (b0 + 7, b0 + 4, b0 + 7),
            '합계 / 가맹점 수', M2),
           ('순현금', '=순현금', '입력', M0),
           ('투자자산', '=B%d+B%d' % (b0 + 6, b0 + 10), '투자실행액 + 순현금', M2),
           ('투자실행액 비중', '=B%d/B%d' % (b0 + 6, b0 + 11), '투자실행액 / 투자자산', '0.0%'),
           ('순현금 비중', '=B%d/B%d' % (b0 + 10, b0 + 11), '순현금 / 투자자산', '0.0%')]
    for i, (lab, val, f, fmt) in enumerate(blk):
        r = b0 + 1 + i
        put(ws, r, 1, lab, bold=True)
        put(ws, r, 2, val, fmt, fill=CHK)
        put(ws, r, 3, f)
    MB = {lab: b0 + 1 + i for i, (lab, *_ ) in enumerate(blk)}

    c0 = b0 + len(blk) + 2
    head(ws, c0, ['플랫폼', '로스터 금액가중 구성비', '대표 구성비', '차'], fill=SUB)
    for i in range(4):
        r, L = c0 + 1 + i, get_column_letter(10 + i)
        put(ws, r, 1, LABEL[ORDER[i]], bold=True)
        put(ws, r, 2, '=IF($P$%d=0,0,SUMPRODUCT($P$2:$P$%d,%s2:%s%d)/$P$%d)'
            % (last, last - 1, L, L, last - 1, last), D8)
        put(ws, r, 3, '=INDEX(구성비범위,%d)' % (i + 1), D8)
        put(ws, r, 4, '=B%d-C%d' % (r, r), '0.00E+00', fill=CHK)
    widths(ws, {'A': 20, 'B': 22, 'C': 20, 'D': 12, 'E': 10, 'F': 12, 'G': 7, 'H': 12,
                'I': 12, 'J': 10, 'K': 10, 'L': 10, 'M': 10, 'N': 10, 'O': 12, 'P': 15,
                'Q': 14, 'R': 14, 'S': 9, 'T': 9, 'U': 12, 'V': 12, 'W': 12, 'X': 12,
                'Y': 8, 'Z': 18, 'AA': 10, 'AB': 16, 'AC': 10})

    # ── 채권 ────────────────────────────────────────────────────
    ws = wb.create_sheet('채권')
    ch = ['번호', '가맹점', '플랫폼', '가맹점#', '플랫폼#', '선정산일', '정산예정일',
          '금융일수 Di', '순지급액', 'Ai', '채권매입수수료', '미지급액', '과지급액',
          '차감액', '투자수익 Mi', '상환액 Bi', '미회수', '만기 도래', 'Ai x Di',
          'S표본', '조회기간']
    head(ws, 1, ch)
    recs = []
    for j in range(WINDOW):
        for m in range(n):
            for i in range(4):
                recs.append((j, m, i, seqs[(m, i)][j]))
    r = 1
    for (j, m, i, d) in recs:
        r += 1
        put(ws, r, 1, r - 1)
        put(ws, r, 2, '=INDEX(상호범위,D%d)' % r)
        put(ws, r, 3, '=INDEX(플랫폼명범위,E%d)' % r)
        put(ws, r, 4, m + 1)
        put(ws, r, 5, i + 1)
        put(ws, r, 6, '=축시작+%d' % j, DT)
        put(ws, r, 7, '=F%d+H%d' % (r, r), DT)
        put(ws, r, 8, d)
        put(ws, r, 9, '=ROUND(INDEX(가맹점!$P$2:$P$%d,D%d)*INDEX(가맹점!$J$2:$M$%d,D%d,E%d),0)'
            % (last - 1, r, last - 1, r, r), M0)
        put(ws, r, 10, '=ROUND(I%d*(1-할인율),0)' % r, M0)
        put(ws, r, 11, '=ROUNDDOWN(I%d*할인율,0)' % r, M0)
        put(ws, r, 12, '=ROUND(I%d*INDEX(미지급률범위,E%d),0)' % (r, r), M0)
        put(ws, r, 13, '=ROUND(I%d*INDEX(과지급률범위,E%d),0)' % (r, r), M0)
        put(ws, r, 14, '=MAX(0,L%d-M%d)' % (r, r), M0)
        put(ws, r, 15, '=K%d-N%d' % (r, r), M0)
        put(ws, r, 16, '=I%d-N%d' % (r, r), M0)
        put(ws, r, 17, '=IF(G%d>기준일,1,0)' % r)
        put(ws, r, 18, '=IF(G%d<=기준일,1,0)' % r)
        put(ws, r, 19, '=J%d*H%d' % (r, r), M0)
        put(ws, r, 20, '=IF(AND(F%d>=표본시작,F%d<=표본종료),1,0)' % (r, r))
        put(ws, r, 21, '=IF(AND(G%d>=조회시작,G%d<=조회종료),1,0)' % (r, r))
    NROW = r
    ws.freeze_panes = 'A2'
    ws.auto_filter.ref = 'A1:U%d' % NROW
    widths(ws, {'A': 7, 'B': 18, 'C': 12, 'D': 8, 'E': 8, 'F': 12, 'G': 12, 'H': 10,
                'I': 12, 'J': 12, 'K': 14, 'L': 11, 'M': 11, 'N': 11, 'O': 12, 'P': 12,
                'Q': 8, 'R': 9, 'S': 14, 'T': 8, 'U': 9})
    RNG = {c: '채권!$%s$2:$%s$%d' % (c, c, NROW) for c in
           'FGHIJKLMNOPQRSTU'}

    # ── 일별 ────────────────────────────────────────────────────
    ws = wb.create_sheet('일별')
    head(ws, 1, ['정산예정일', '건수', 'SBD-1 상환액', 'SAD-1 투자실행금', 'SMD-1 투자수익',
                 'SMD-1 투자수익(차감 제외)', 'SMRD-1 투자수익율', 'SDD-1 W금융일수',
                 'ty수익율(%)', 'EC 순현금', 'Σ(Ai x Di)'])
    NDAY = 27
    for k in range(NDAY):
        r = 2 + k
        put(ws, r, 1, '=일별시작+%d' % k, DT)
        put(ws, r, 2, '=COUNTIFS(%s,$A%d)' % (RNG['G'], r), M0)
        put(ws, r, 3, '=SUMIFS(%s,%s,$A%d)' % (RNG['P'], RNG['G'], r), M0)
        put(ws, r, 4, '=SUMIFS(%s,%s,$A%d)' % (RNG['J'], RNG['G'], r), M0)
        put(ws, r, 5, '=SUMIFS(%s,%s,$A%d)' % (RNG['O'], RNG['G'], r), M0)
        put(ws, r, 6, '=SUMIFS(%s,%s,$A%d)' % (RNG['K'], RNG['G'], r), M0)
        put(ws, r, 7, '=IF(D%d=0,0,E%d/D%d)' % (r, r, r), D8)
        put(ws, r, 8, '=IF(D%d=0,0,K%d/D%d)' % (r, r, r), D6)
        put(ws, r, 9, '=IF(H%d=0,0,G%d*연일수/H%d*100)' % (r, r, r), P2)
        put(ws, r, 10, '=순현금', M0)
        put(ws, r, 11, '=SUMIFS(%s,%s,$A%d)' % (RNG['S'], RNG['G'], r), M0)
    DL = 1 + NDAY
    put(ws, DL + 1, 1, '합계', bold=True)
    for col in (2, 3, 4, 5, 6, 10, 11):
        L = get_column_letter(col)
        put(ws, DL + 1, col, '=SUM(%s2:%s%d)' % (L, L, DL), M0, bold=True)
    ws.freeze_panes = 'A2'
    widths(ws, {'A': 13, 'B': 8, 'C': 16, 'D': 17, 'E': 15, 'F': 20, 'G': 16, 'H': 16,
                'I': 12, 'J': 14, 'K': 16})
    DRG = {c: "일별!$%s$2:$%s$%d" % (c, c, DL) for c in 'ABCDEFGHIJK'}

    # ── 기간집계 ────────────────────────────────────────────────
    ws = wb.create_sheet('기간집계')
    head(ws, 1, ['항목', '값', '산식', '출처'])
    crit = '%s,">="&조회시작,%s,"<="&조회종료' % (DRG['A'], DRG['A'])
    per_rows = [
        ('조회기간 시작', '=조회시작', '입력', DT, ''),
        ('조회기간 종료', '=조회종료', '입력', DT, ''),
        ('조회 일수', '=조회종료-조회시작+1', '종료 - 시작 + 1', M0, ''),
        ('PSA 투자실행금', '=SUMIFS(%s,%s)' % (DRG['D'], crit), 'Σ SAD-1', M0,
         'ceo_definitions.md [2번] 투자 실행금(PSA)'),
        ('PSM 투자수익 (정의 · 차감 반영)', '=SUMIFS(%s,%s)' % (DRG['E'], crit),
         'Σ SMD-1 = Σ(수수료 - max(0,미지급-과지급))', M0,
         'ceo_definitions.md [2번] MD-1i'),
        ('PSM 투자수익 (차감 제외)', '=SUMIFS(%s,%s)' % (DRG['F'], crit), 'Σ 채권매입수수료',
         M0, '현행 daily_ledger.py:298'),
        ('② 상환액', '=SUMIFS(%s,%s)' % (DRG['C'], crit), 'Σ SBD-1', M0,
         'ceo_definitions.md [2번] 이미지의 ②'),
        ('Σ(Ai x Di)', '=SUMIFS(%s,%s)' % (DRG['K'], crit), 'Σ 일별 Σ(Ai x Di)', M0, ''),
        ('PSMR (정의)', '=IF(B5=0,0,B6/B5)', 'PSM / PSA', D8,
         'ceo_definitions.md [2번] PSMR'),
        ('PSMR (차감 제외)', '=IF(B5=0,0,B7/B5)', 'PSM(차감 제외) / PSA', D8, ''),
        ('PSD', '=IF(B5=0,0,B9/B5)', 'Σ(Api x Dpi) / PSA', D6,
         'ceo_definitions.md [2번] PSD'),
        ('④ 투자실행금액 대비 ty수익율 (정의)', '=IF(B12=0,0,B10*연일수/B12*100)',
         'PSMR x 365 / PSD', P2, 'ceo_definitions.md [2번] 이미지의 ④'),
        ('④ (차감 제외)', '=IF(B12=0,0,B11*연일수/B12*100)', 'PSMR(차감 제외) x 365 / PSD',
         P2, ''),
        ('PSC 순현금 합', '=SUMIFS(%s,%s)' % (DRG['J'], crit), 'Σ EC', M0,
         'ceo_definitions.md [2번] PSC'),
        ('⑤ 투자자산 대비 ty수익율 (정의)', '=IF(B5+B15=0,0,B13*B5/(B5+B15))',
         '④ x PSA / (PSA + PSC)', P2, 'ceo_definitions.md [2번] 이미지의 ⑤'),
        ('⑤ (차감 제외)', '=IF(B5+B15=0,0,B14*B5/(B5+B15))', '④(차감 제외) x PSA / (PSA+PSC)',
         P2, ''),
    ]
    for i, (lab, val, f, fmt, src) in enumerate(per_rows):
        r = 2 + i
        put(ws, r, 1, lab, bold=True)
        put(ws, r, 2, val, fmt, fill=CHK)
        put(ws, r, 3, f)
        put(ws, r, 4, src)
    b1 = 2 + len(per_rows) + 1
    head(ws, b1, ['항목', '값', '산식', '출처'], fill=SUB)
    bal = [
        ('대상정산금채권 Σ Ai', '=SUM(%s)' % RNG['J'], 'Σ Ai (선정산일 축 전량)', M0, ''),
        ('대상정산금채권 Σ(Ai x Di)', '=SUM(%s)' % RNG['S'], 'Σ Ai x Di', M0, ''),
        ('W금융일수 — 대상정산금채권 전체', '=B%d/B%d' % (b1 + 2, b1 + 1),
         'Σ(Ai x Di) / Σ Ai', D8, 'ceo_definitions.md [1번] w금융일수'),
        ('만기 도래분 Σ Ai', '=SUMPRODUCT(%s,%s)' % (RNG['J'], RNG['R']), 'Σ Ai x 도래', M0, ''),
        ('만기 도래분 Σ(Ai x Di)', '=SUMPRODUCT(%s,%s)' % (RNG['S'], RNG['R']), '', M0, ''),
        ('W금융일수 — 만기 도래분만', '=IF(B%d=0,0,B%d/B%d)' % (b1 + 4, b1 + 5, b1 + 4),
         '', D8, ''),
        ('미회수 Σ Ai', '=SUMPRODUCT(%s,%s)' % (RNG['J'], RNG['Q']), 'Σ Ai x 미회수', M0,
         'ceo_definitions.md [1번] 투자 실행액'),
        ('미회수 Σ(Ai x Di)', '=SUMPRODUCT(%s,%s)' % (RNG['S'], RNG['Q']), '', M0, ''),
        ('W금융일수 — 미회수 잔량만', '=IF(B%d=0,0,B%d/B%d)' % (b1 + 7, b1 + 8, b1 + 7),
         '', D8, ''),
        ('W금융일수 raw (스위치 ① 적용)',
         '=IF(SW_모집단="미회수 잔량만",B%d,IF(SW_모집단="만기 도래분만",B%d,B%d))'
         % (b1 + 9, b1 + 6, b1 + 3), '스위치 ①', D8, ''),
        ('W금융일수 표기 (스위치 ② 적용)', '=ROUND(B%d,SW_자릿수)' % (b1 + 10), '스위치 ②',
         'General', ''),
        ('Ty수익율(%)', '=할인율퍼센트*연일수/B%d' % (b1 + 11), '할인율 x 365 / 표기 W', P2,
         'ceo_definitions.md [1번] ty수익율'),
        ('투자실행액', '=B%d' % (b1 + 7), '미회수 Σ Ai', M0, ''),
        ('순현금', '=순현금', '입력', M0, 'ceo_definitions.md [1번] 순현금'),
        ('투자자산', '=B%d+B%d' % (b1 + 13, b1 + 14), '투자실행액 + 순현금', M0, ''),
        ('투자실행액 비중', '=B%d/B%d' % (b1 + 13, b1 + 15), '', '0.0%', ''),
        ('순현금 비중', '=B%d/B%d' % (b1 + 14, b1 + 15), '', '0.0%', ''),
        ('S표본 Σ(미지급-과지급)', '=SUMPRODUCT(%s-%s,%s)' % (RNG['L'], RNG['M'], RNG['T']),
         'Σ SLi', M0, 'ceo_definitions.md [1번] SLi'),
        ('S표본 Σ Ai', '=SUMPRODUCT(%s,%s)' % (RNG['J'], RNG['T']), 'Σ SAi', M0, ''),
        ('S입금부족율(%)', '=IF(B%d=0,0,B%d/B%d*100)' % (b1 + 19, b1 + 18, b1 + 19),
         'Σ SLi / Σ SAi', P2, 'ceo_definitions.md [1번] S입금부족율'),
        ('미회수 건수', '=SUM(%s)' % RNG['Q'], '', M0, ''),
        ('채권 건수', '=COUNT(%s)' % RNG['H'], '', M0, ''),
    ]
    for i, (lab, val, f, fmt, src) in enumerate(bal):
        r = b1 + 1 + i
        put(ws, r, 1, lab, bold=True)
        put(ws, r, 2, val, fmt, fill=CHK)
        put(ws, r, 3, f)
        put(ws, r, 4, src)
    AGG = {lab: b1 + 1 + i for i, (lab, *_) in enumerate(bal)}
    PER = {lab: 2 + i for i, (lab, *_) in enumerate(per_rows)}
    widths(ws, {'A': 36, 'B': 22, 'C': 40, 'D': 40})

    # ── 화면대조 ────────────────────────────────────────────────
    ws = wb.create_sheet('화면대조')
    head(ws, 1, ['구분', '항목', '엑셀 값', '산출 경로', '화면 값', '차이', '판정', '출처'])

    def A(k):
        return '기간집계!B%d' % AGG[k]

    def P(k):
        return '기간집계!B%d' % PER[k]

    def G(k):
        return '가맹점!B%d' % MB[k]

    def num(s):
        return float(re.sub(r'[^\d.\-]', '', str(s)))

    cmp_rows = [
        ('항등식', '좌변 — 투자실행액 (채권 미회수 Σ Ai)', '=' + A('미회수 Σ Ai'),
         '기간집계 B%d' % AGG['미회수 Σ Ai'], '=' + G('투자실행액 (모집단 산식)'),
         '우변 — 하루 선정산액 합계 x (1-r) x W', M0, 0.5),
        ('잔액', '투자실행액', '=' + A('투자실행액'), '기간집계 B%d' % AGG['투자실행액'],
         num(md['투자실행액']), 'rescale_decision.md 9-A', M0, 0.5),
        ('잔액', '순현금', '=' + A('순현금'), '기간집계 B%d' % AGG['순현금'],
         num(md['순현금']), 'rescale_decision.md 9-A', M0, 0.5),
        ('잔액', '투자자산', '=' + A('투자자산'), '기간집계 B%d' % AGG['투자자산'],
         num(md['투자자산']), 'rescale_decision.md 9-A', M0, 0.5),
        ('잔액', '투자실행액 비중(%)', '=' + A('투자실행액 비중') + '*100',
         '기간집계 B%d' % AGG['투자실행액 비중'], num(md['투자실행액 비중']),
         'rescale_decision.md 9-A', P2, 0.005),
        ('잔액', '순현금 비중(%)', '=' + A('순현금 비중') + '*100',
         '기간집계 B%d' % AGG['순현금 비중'], num(md['순현금 비중']),
         'rescale_decision.md 9-A', P2, 0.005),
        ('잔액', 'W금융일수 (표기)', '=' + A('W금융일수 표기 (스위치 ② 적용)'),
         '기간집계 B%d' % AGG['W금융일수 표기 (스위치 ② 적용)'], num(md['W금융일수']),
         'rescale_decision.md 9-A', '0.00', 0.0005),
        ('잔액', 'W금융일수 (raw)', '=' + A('W금융일수 raw (스위치 ① 적용)'),
         '기간집계 B%d' % AGG['W금융일수 raw (스위치 ① 적용)'], cyc['wavg'],
         '%s 정산주기 H41' % cyc['src_xlsx'], D8, 0.000001),
        ('잔액', 'Ty수익율(%)', '=' + A('Ty수익율(%)'), '기간집계 B%d' % AGG['Ty수익율(%)'],
         num(md['Ty수익율']), 'rescale_decision.md 9-A', P2, 0.005),
        ('잔액', 'S입금부족율(%)', '=ROUND(' + A('S입금부족율(%)') + ',2)',
         '기간집계 B%d' % AGG['S입금부족율(%)'], num(md['S입금부족율']),
         'rescale_decision.md 9-A', P2, 0.0005),
        ('잔액', '로스터 건수', '=' + G('가맹점 수 (적용)'),
         '가맹점 B%d' % MB['가맹점 수 (적용)'], num(md['로스터 건수']),
         'rescale_decision.md 9-A', M0, 0.5),
        ('유량', '하루 평균 투자실행금', '=' + G('하루 선정산액 합계 (적용)') + '*(1-할인율)',
         '가맹점 B%d x (1-r)' % MB['하루 선정산액 합계 (적용)'],
         num(md['하루 평균 투자실행금']), 'rescale_decision.md 9-B', M0, 0.5),
        ('유량', '하루 순지급액', '=' + G('하루 선정산액 합계 (적용)'),
         '가맹점 B%d' % MB['하루 선정산액 합계 (적용)'], num(md['하루 순지급액']),
         'rescale_decision.md 9-B', M0, 0.5),
        ('유량', '채권 Di 범위 최소', '=MIN(%s)' % RNG['H'], '채권 H열', 1,
         'rescale_decision.md 9-B', M0, 0.5),
        ('유량', '채권 Di 범위 최대', '=MAX(%s)' % RNG['H'], '채권 H열', 13,
         'rescale_decision.md 9-B', M0, 0.5),
        ('유량', 'PSA (조회기간)', '=' + P('PSA 투자실행금'),
         '기간집계 B%d' % PER['PSA 투자실행금'], per['psa'], 'rescale_decision.md 5-B', M0, 0.5),
        ('유량', 'PSM (차감 제외)', '=' + P('PSM 투자수익 (차감 제외)'),
         '기간집계 B%d' % PER['PSM 투자수익 (차감 제외)'], per['psm'],
         'rescale_decision.md 5-B', M0, 0.5),
        ('유량', 'PSM (정의 · 차감 반영)', '=' + P('PSM 투자수익 (정의 · 차감 반영)'),
         '기간집계 B%d' % PER['PSM 투자수익 (정의 · 차감 반영)'], per['psm'],
         'rescale_decision.md 5-B', M0, 0.5),
        ('유량', 'PSD', '=' + P('PSD'), '기간집계 B%d' % PER['PSD'], cyc['wavg'],
         '%s 정산주기 H41' % cyc['src_xlsx'], D6, 0.000001),
        ('유량', 'PSC', '=' + P('PSC 순현금 합'), '기간집계 B%d' % PER['PSC 순현금 합'],
         per['psc'], 'rescale_decision.md 5-B', M0, 0.5),
        ('유량', '④ (차감 제외)', '=' + P('④ (차감 제외)'), '기간집계 B%d' % PER['④ (차감 제외)'],
         per['p4'], 'rescale_decision.md 5-B', P2, 0.005),
        ('유량', '④ (정의 · 차감 반영)', '=' + P('④ 투자실행금액 대비 ty수익율 (정의)'),
         '기간집계 B%d' % PER['④ 투자실행금액 대비 ty수익율 (정의)'], per['p4'],
         'rescale_decision.md 5-B', P2, 0.005),
        ('유량', '⑤ (차감 제외)', '=' + P('⑤ (차감 제외)'), '기간집계 B%d' % PER['⑤ (차감 제외)'],
         per['p5'], 'rescale_decision.md 5-B', P2, 0.005),
        ('유량', '⑤ (정의 · 차감 반영)', '=' + P('⑤ 투자자산 대비 ty수익율 (정의)'),
         '기간집계 B%d' % PER['⑤ 투자자산 대비 ty수익율 (정의)'], per['p5'],
         'rescale_decision.md 5-B', P2, 0.005),
    ]
    r = 1
    for (g, lab, val, path, scr, src, fmt, tol) in cmp_rows:
        r += 1
        put(ws, r, 1, g)
        put(ws, r, 2, lab, bold=True)
        put(ws, r, 3, val, fmt, fill=CHK)
        put(ws, r, 4, path)
        put(ws, r, 5, scr, fmt)
        put(ws, r, 6, '=IFERROR(C%d-E%d,"")' % (r, r), fmt)
        put(ws, r, 7, '=IFERROR(IF(ABS(F%d)<=%s,"일치","차이"),"")' % (r, repr(tol)))
        put(ws, r, 8, src)
    # 가맹점별 9행
    r += 1
    head(ws, r, ['구분', '항목', '엑셀 값', '산출 경로', '화면 값', '차이', '판정', '출처'],
         fill=SUB)
    for i, r0 in enumerate(roster):
        for key, col, scr, fmt, tol in [('투자금액', 'R', r0['invest'], M0, 2.5),
                                        ('W', 'T', float(r0['w']), '0.00', 0.0005),
                                        ('Ty수익율(%)', 'X', float(r0['ty']), P2, 0.005),
                                        ('비중(%)', 'S', float(r0['share']), P2, 0.1)]:
            r += 1
            put(ws, r, 1, '가맹점')
            put(ws, r, 2, '%s — %s' % (r0['name'], key), bold=True)
            put(ws, r, 3, '=가맹점!%s%d%s' % (col, 2 + i, '*100' if key == '비중(%)' else ''),
                fmt, fill=CHK)
            put(ws, r, 4, '가맹점!%s%d' % (col, 2 + i))
            put(ws, r, 5, scr, fmt)
            put(ws, r, 6, '=IFERROR(C%d-E%d,"")' % (r, r), fmt)
            put(ws, r, 7, '=IFERROR(IF(ABS(F%d)<=%s,"일치","차이"),"")' % (r, repr(tol)))
            put(ws, r, 8, 'rescale_decision.md 4-D')
    LASTC = r
    ws.conditional_formatting.add('G2:G%d' % LASTC,
                                  CellIsRule(operator='equal', formula=['"차이"'], fill=BAD))
    ws.conditional_formatting.add('G2:G%d' % LASTC,
                                  CellIsRule(operator='equal', formula=['"일치"'], fill=GOOD))
    ws.freeze_panes = 'A2'
    widths(ws, {'A': 9, 'B': 34, 'C': 20, 'D': 26, 'E': 20, 'F': 16, 'G': 8, 'H': 34})

    # ── 산식 ────────────────────────────────────────────────────
    ws = wb.create_sheet('산식')
    head(ws, 1, ['출처 절', '대표 정의서 원문', '이 통합문서의 셀'])
    MAPS = [
        ('투자 실행액', '기간집계 B%d · 화면대조 3행' % AGG['투자실행액']),
        ('유동화투자자의 할인율', '입력 C2 · C3'),
        ('순현금', '입력 C6 · 기간집계 B%d' % AGG['순현금']),
        ('w금융일수 =', '기간집계 B%d' % AGG['W금융일수 — 대상정산금채권 전체']),
        ('Ai =', '채권 J열'),
        ('Di =', '채권 H열'),
        ('대상정산금채권:', '채권 시트 전 행 (선정산일 축 %d일)' % WINDOW),
        ('각 정산금채권의 ID', '채권 D·E·F열'),
        ('플랫폼ID', '입력 A24:A27'),
        ('D = 현재일자', '입력 C8'),
        ('비중', '기간집계 B%d · B%d' % (AGG['투자실행액 비중'], AGG['순현금 비중'])),
        ('매일 자정일 지나면', '일별 시트 전 행'),
        ('상기 배치작업이 완료된 후', '기간집계 2~%d행' % (1 + len(per_rows))),
        ('금융일수 =', '채권 H열 (정산주기.xlsx N6:Q370 실측)'),
        ('S입금부족율', '기간집계 B%d' % AGG['S입금부족율(%)']),
        ('SLi =', '채권 L열 - M열'),
        ('표본집합:', '채권 T열 · 입력 C14:C15'),
        ('SAi =', '채권 J열'),
        ('ty수익율 =', '기간집계 B%d' % AGG['Ty수익율(%)']),
        ('투자 실행액의 비중', '기간집계 B%d' % AGG['투자실행액 비중']),
        ('순현금의 비중', '기간집계 B%d' % AGG['순현금 비중']),
        ('전일자(D-1) 대상정산금채권의 상환액', '일별 C열'),
        ('Σ BD-1i', '채권 P열 = 순지급액 - 차감액'),
        ('전일자(D-1) 대상정산금채권의 투자실행금', '일별 D열'),
        ('Σ AD-1i', '채권 J열'),
        ('전일자(D-1) 대상정산금채권의 투자수익(SMD-1)', '일별 E열'),
        ('MD-1i =', '채권 O열 = 채권매입수수료 - 차감액'),
        ('전일자(D-1) 대상정산금채권의 투자수익율', '일별 G열'),
        ('전일자(D-1) 대상정산금채권의 w금융일수', '일별 H열'),
        ('AD-1i =', '채권 J열'),
        ('DD-1i =', '채권 H열'),
        ('전일자(D-1) 대상정산금채권의 ty수익율', '일별 I열'),
        ('전일자(D-1) 순현금 (EC)', '일별 J열'),
        ('투자 실행금(PSA)', '기간집계 B%d' % PER['PSA 투자실행금']),
        ('투자수익(PSM)', '기간집계 B%d · B%d'
         % (PER['PSM 투자수익 (정의 · 차감 반영)'], PER['PSM 투자수익 (차감 제외)'])),
        ('투자실행금액 대비 ty수익율(이미지의 ④)', '기간집계 B%d · B%d'
         % (PER['④ 투자실행금액 대비 ty수익율 (정의)'], PER['④ (차감 제외)'])),
        ('PSMR =', '기간집계 B%d · B%d' % (PER['PSMR (정의)'], PER['PSMR (차감 제외)'])),
        ('PSD =', '기간집계 B%d' % PER['PSD']),
        ('Api :', '채권 J열 x U열'),
        ('Dpi:', '채권 H열'),
        ('투자자산 대비 ty수익율 (이미지의 ⑤)', '기간집계 B%d · B%d'
         % (PER['⑤ 투자자산 대비 ty수익율 (정의)'], PER['⑤ (차감 제외)'])),
        ('PSC =', '기간집계 B%d' % PER['PSC 순현금 합']),
        ('상환액 (이미지의 ②)', '기간집계 B%d · 일별 C열' % PER['② 상환액']),
    ]
    r = 1
    for sec, line in defs:
        r += 1
        put(ws, r, 1, sec)
        put(ws, r, 2, line)
        cell = ''
        for key, ref in MAPS:
            if line.startswith(key):
                cell = ref
                break
        put(ws, r, 3, cell, fill=CHK if cell else None)
        ws.cell(row=r, column=2).alignment = Alignment(wrap_text=True, vertical='top')
    widths(ws, {'A': 16, 'B': 86, 'C': 40})
    ws.freeze_panes = 'A2'

    wb.save(OUT)
    return dict(out=OUT, nrec=NROW - 1, nday=NDAY, last=last, ncmp=LASTC - 1,
                exec_target=exec_target, cash=cash, avg_daily=avg_daily)


if __name__ == '__main__':
    info = build()
    print(json.dumps(info, ensure_ascii=False, indent=1))
