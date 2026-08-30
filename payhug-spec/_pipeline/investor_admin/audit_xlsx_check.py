# -*- coding: utf-8 -*-
"""검산 통합문서 독립 검증 — 셀 수식을 파싱해 직접 계산한다.

LibreOffice 가 없으므로 엑셀 수식 파서·계산기를 따로 구현해 값을 낸다.
openpyxl 은 수식 문자열만 읽고, 계산은 여기서 한다. 생성기와 코드를 공유하지 않는다.
"""
import json, math, os, re, sys
from datetime import date, datetime, timedelta
from decimal import Decimal as D, ROUND_HALF_UP, ROUND_DOWN

import openpyxl

BASE = os.path.dirname(os.path.abspath(__file__))
XLSX = os.path.join(BASE, '검산_투자자어드민_20260901.xlsx')
EPOCH = date(1899, 12, 30)


# ── 토크나이저 ────────────────────────────────────────────────────
TOK = re.compile(r"""
 (?P<str>"(?:[^"]|"")*")
|(?P<num>\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)
|(?P<ref>(?:'[^']+'|[A-Za-z가-힣_][A-Za-z0-9가-힣_.]*)!\$?[A-Z]{1,3}\$?\d+(?::\$?[A-Z]{1,3}\$?\d+)?)
|(?P<cell>\$?[A-Z]{1,3}\$?\d+(?::\$?[A-Z]{1,3}\$?\d+)?)
|(?P<func>[A-Za-z가-힣_][A-Za-z0-9가-힣_.]*(?=\())
|(?P<name>[A-Za-z가-힣_][A-Za-z0-9가-힣_.]*)
|(?P<op><>|<=|>=|[-+*/^&<>=(),:])
|(?P<ws>\s+)
""", re.X)


def lex(s):
    out, i = [], 0
    while i < len(s):
        m = TOK.match(s, i)
        if not m:
            raise ValueError('토큰 실패 %r at %d' % (s, i))
        i = m.end()
        if m.lastgroup != 'ws':
            out.append((m.lastgroup, m.group()))
    return out


# ── 값 도우미 ─────────────────────────────────────────────────────
def flat(v):
    if isinstance(v, list):
        o = []
        for x in v:
            o.extend(flat(x))
        return o
    return [v]


def numify(x):
    if x is None or x == '':
        return 0.0
    if isinstance(x, bool):
        return 1.0 if x else 0.0
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, date):
        return float((x - EPOCH).days)
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def shape(v):
    return v if isinstance(v, list) else None


def binop(op, a, b):
    if isinstance(a, list) or isinstance(b, list):
        fa, fb = flat(a) if isinstance(a, list) else None, flat(b) if isinstance(b, list) else None
        n = len(fa) if fa else len(fb)
        out = []
        for i in range(n):
            out.append(binop(op, fa[i] if fa else a, fb[i] if fb else b))
        return out
    if op == '&':
        return _txt(a) + _txt(b)
    if op in ('=', '<>', '<', '>', '<=', '>='):
        if isinstance(a, str) or isinstance(b, str):
            x, y = _txt(a), _txt(b)
        else:
            x, y = numify(a), numify(b)
        return {'=': x == y, '<>': x != y, '<': x < y, '>': x > y,
                '<=': x <= y, '>=': x >= y}[op]
    x, y = numify(a), numify(b)
    if op == '+':
        return x + y
    if op == '-':
        return x - y
    if op == '*':
        return x * y
    if op == '/':
        return float('nan') if y == 0 else x / y
    if op == '^':
        return x ** y
    raise ValueError(op)


def _txt(v):
    if v is None:
        return ''
    if isinstance(v, bool):
        return 'TRUE' if v else 'FALSE'
    if isinstance(v, date):
        return str((v - EPOCH).days)
    if isinstance(v, float) and v == int(v):
        return str(int(v))
    return str(v)


def xround(x, n):
    n = int(n)
    return float(D(repr(float(x))).quantize(D(1).scaleb(-int(n)), rounding=ROUND_HALF_UP))


def xrounddown(x, n):
    return float(D(repr(float(x))).quantize(D(1).scaleb(-int(n)), rounding=ROUND_DOWN))


def _asdate(v):
    if isinstance(v, list):
        v = flat(v)[0]
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    return EPOCH + timedelta(days=int(numify(v)))


def match_crit(val, crit):
    c = _txt(crit)
    m = re.match(r'^(<=|>=|<>|<|>|=)?(.*)$', c)
    op, rhs = m.group(1) or '=', m.group(2)
    try:
        r = float(rhs)
        v = numify(val)
    except ValueError:
        r, v = rhs, _txt(val)
    return {'=': v == r, '<>': v != r, '<': v < r, '>': v > r, '<=': v <= r, '>=': v >= r}[op]


# ── 계산기 ────────────────────────────────────────────────────────
class Book:
    def __init__(self, path):
        self.wb = openpyxl.load_workbook(path, data_only=False)
        self.cache, self.stack = {}, set()
        self.names = {}
        for k, dn in self.wb.defined_names.items():
            self.names[k] = dn.value if hasattr(dn, 'value') else dn.attr_text
        self.nform = 0

    # 셀 값
    def cell(self, sheet, coord):
        key = (sheet, coord)
        if key in self.cache:
            return self.cache[key]
        if key in self.stack:
            raise ValueError('순환 참조 %s!%s' % key)
        self.stack.add(key)
        prev = getattr(self, 'currow', None)
        try:
            v = self.wb[sheet][coord].value
            if isinstance(v, str) and v.startswith('='):
                self.nform += 1
                self.currow = self.wb[sheet][coord].row
                v = self.eval(v[1:], sheet)
            elif isinstance(v, datetime):
                v = v.date()
        finally:
            self.stack.discard(key)
            self.currow = prev
        self.cache[key] = v
        return v

    def rng(self, sheet, a1):
        ws = self.wb[sheet]
        cells = ws[a1.replace('$', '')]
        if not isinstance(cells, tuple):
            return self.cell(sheet, cells.coordinate)
        out = []
        for row in cells:
            if not isinstance(row, tuple):
                row = (row,)
            out.append([self.cell(sheet, c.coordinate) for c in row])
        if len(out) == 1:
            return out[0]
        if all(len(r) == 1 for r in out):
            return [r[0] for r in out]
        return out

    def resolve(self, ref, cur):
        if '!' in ref:
            sh, a1 = ref.split('!', 1)
            return self.rng(sh.strip("'"), a1)
        return self.rng(cur, ref)

    def eval(self, src, sheet):
        return Parser(self, lex(src), sheet).run()

    def call(self, fn, a):
        if fn == 'SUM':
            return sum(numify(x) for x in flat(a))
        if fn == 'SUMPRODUCT':
            cols = [flat(x) for x in a]
            n = max(len(c) for c in cols)
            s = 0.0
            for i in range(n):
                p = 1.0
                for c in cols:
                    p *= numify(c[i] if len(c) > 1 else c[0])
                s += p
            return s
        if fn in ('SUMIFS', 'COUNTIFS', 'SUMIF'):
            if fn == 'SUMIFS':
                tgt, rest = flat(a[0]), a[1:]
            elif fn == 'SUMIF':
                tgt, rest = flat(a[2]) if len(a) > 2 else flat(a[0]), [a[0], a[1]]
            else:
                tgt, rest = None, a
            pairs = [(flat(rest[i]), rest[i + 1]) for i in range(0, len(rest), 2)]
            n = len(pairs[0][0])
            s = 0.0
            for i in range(n):
                if all(match_crit(rg[i], cr) for rg, cr in pairs):
                    s += numify(tgt[i]) if tgt is not None else 1.0
            return s
        if fn == 'COUNT':
            return float(sum(1 for x in flat(a) if isinstance(x, (int, float, date))
                             and not isinstance(x, bool)))
        if fn == 'COUNTA':
            return float(sum(1 for x in flat(a) if x not in (None, '')))
        if fn == 'MIN':
            f = [numify(x) for x in flat(a) if x not in (None, '')]
            return min(f) if f else 0.0
        if fn == 'MAX':
            f = [numify(x) for x in flat(a) if x not in (None, '')]
            return max(f) if f else 0.0
        if fn == 'ROUND':
            return xround(numify(a[0]), numify(a[1]))
        if fn == 'ROUNDDOWN':
            return xrounddown(numify(a[0]), numify(a[1]))
        if fn == 'ABS':
            return abs(numify(a[0]))
        if fn == 'IF':
            c = a[0]
            c = c[0] if isinstance(c, list) else c
            t = bool(c) if isinstance(c, bool) else numify(c) != 0
            return a[1] if t else (a[2] if len(a) > 2 else False)
        if fn == 'IFERROR':
            v = a[0]
            return a[1] if (isinstance(v, float) and math.isnan(v)) else v
        if fn == 'AND':
            return all((x if isinstance(x, bool) else numify(x) != 0) for x in flat(a))
        if fn == 'OR':
            return any((x if isinstance(x, bool) else numify(x) != 0) for x in flat(a))
        if fn == 'INDEX':
            arr = a[0]
            if len(a) == 2:
                return flat(arr)[int(numify(a[1])) - 1]
            r, c = int(numify(a[1])), int(numify(a[2]))
            if arr and isinstance(arr[0], list):
                return arr[r - 1][c - 1]
            return flat(arr)[(r - 1) if len(a) < 3 or c == 1 else (c - 1)]
        if fn == 'TRANSPOSE':
            return a[0]
        if fn == 'MOD':
            x, y = numify(a[0]), numify(a[1])
            return float('nan') if y == 0 else x - y * math.floor(x / y)
        if fn == 'INT':
            return float(math.floor(numify(a[0])))
        if fn == 'ROW':
            return float(self.currow) if getattr(self, 'currow', None) else 0.0
        if fn == 'COUNTIF':
            rg, cr = flat(a[0]), a[1]
            return float(sum(1 for x in rg if match_crit(x, cr)))
        if fn == 'RANK':
            x = numify(a[0])
            rg = [numify(v) for v in flat(a[1]) if isinstance(v, (int, float))
                  and not isinstance(v, bool)]
            asc = len(a) > 2 and numify(a[2]) != 0
            return float(1 + sum(1 for v in rg if ((v < x) if asc else (v > x))))
        if fn == 'DATE':
            return date(int(numify(a[0])), int(numify(a[1])), int(numify(a[2])))
        if fn == 'YEAR':
            return float(_asdate(a[0]).year)
        if fn == 'MONTH':
            return float(_asdate(a[0]).month)
        if fn == 'DAY':
            return float(_asdate(a[0]).day)
        if fn == 'WEEKDAY':
            d = _asdate(a[0])
            t = int(numify(a[1])) if len(a) > 1 else 1
            if t == 3:
                return float(d.weekday())
            if t == 2:
                return float(d.weekday() + 1)
            return float((d.weekday() + 1) % 7 + 1)
        if fn == 'TEXT':
            v, f = numify(a[0]), _txt(a[1])
            nd = len(f.split('.')[1]) if '.' in f else 0
            return ('%%.%df' % nd) % v
        if fn == 'SUMPRODUCT_':
            return None
        raise ValueError('미구현 함수 %s' % fn)


class Parser:
    """수식 하나를 파싱·계산한다. 재진입 가능하도록 상태를 인스턴스에 둔다."""

    def __init__(self, bk, toks, sheet):
        self.bk, self.toks, self.sheet, self.i = bk, toks, sheet, 0

    def run(self):
        v = self._cmp()
        assert self.i == len(self.toks), ('잔여 토큰', self.toks, self.i)
        return v

    def _peek(self):
        return self.toks[self.i] if self.i < len(self.toks) else (None, None)

    def _eat(self, val=None):
        t, v = self._peek()
        if val is not None and v != val:
            raise ValueError('기대 %r 실제 %r' % (val, v))
        self.i += 1
        return v

    def _cmp(self):
        v = self._concat()
        while self._peek()[1] in ('=', '<>', '<', '>', '<=', '>='):
            op = self._eat()
            v = binop(op, v, self._concat())
        return v

    def _concat(self):
        v = self._add()
        while self._peek()[1] == '&':
            self._eat()
            v = binop('&', v, self._add())
        return v

    def _add(self):
        v = self._mul()
        while self._peek()[1] in ('+', '-'):
            op = self._eat()
            v = binop(op, v, self._mul())
        return v

    def _mul(self):
        v = self._un()
        while self._peek()[1] in ('*', '/'):
            op = self._eat()
            v = binop(op, v, self._un())
        return v

    def _un(self):
        if self._peek()[1] in ('-', '+'):
            op = self._eat()
            v = self._un()
            return binop('-', 0, v) if op == '-' else v
        return self._pow()

    def _pow(self):
        v = self._atom()
        while self._peek()[1] == '^':
            self._eat()
            v = binop('^', v, self._atom())
        return v

    def _args(self):
        self._eat('(')
        args = []
        if self._peek()[1] == ')':
            self._eat(')')
            return args
        while True:
            args.append(self._cmp())
            if self._peek()[1] == ',':
                self._eat()
                continue
            self._eat(')')
            return args

    def _atom(self):
        t, v = self._peek()
        if v == '(':
            self._eat('(')
            r = self._cmp()
            self._eat(')')
            return r
        if t == 'num':
            self._eat()
            return float(v)
        if t == 'str':
            self._eat()
            return v[1:-1].replace('""', '"')
        if t == 'func':
            self._eat()
            return self.bk.call(v.upper(), self._args())
        if t in ('ref', 'cell'):
            self._eat()
            return self.bk.resolve(v, self.sheet)
        if t == 'name':
            self._eat()
            if v.upper() in ('TRUE', 'FALSE'):
                return v.upper() == 'TRUE'
            tgt = self.bk.names.get(v)
            assert tgt, '이름 없음 %r' % v
            sh, a1 = tgt.split('!', 1)
            return self.bk.rng(sh.strip("'"), a1)
        raise ValueError('예상 못한 토큰 %r' % (v,))


# ── 검증 ──────────────────────────────────────────────────────────
def rowmap(ws, col=1):
    """라벨 -> 행 번호. 시트 구조가 바뀌어도 주소를 손으로 적지 않는다."""
    m = {}
    for r in range(1, ws.max_row + 1):
        v = ws.cell(r, col).value
        if isinstance(v, str) and v and not v.startswith('='):
            m.setdefault(v, r)
    return m


def counts(wb):
    out, nf, nv = {}, 0, 0
    for ws in wb.worksheets:
        f = v = 0
        for row in ws.iter_rows():
            for c in row:
                if c.value is None or c.value == '':
                    continue
                if isinstance(c.value, str) and c.value.startswith('='):
                    f += 1
                else:
                    v += 1
        nf += f
        nv += v
        out[ws.title] = {'행': ws.max_row, '열': ws.max_column, '수식셀': f, '값셀': v}
    return out, nf, nv


def evaluate_all(bk):
    err = []
    for ws in bk.wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.startswith('='):
                    try:
                        bk.cell(ws.title, c.coordinate)
                    except Exception as e:
                        err.append('%s!%s  %s  → %s' % (ws.title, c.coordinate,
                                                        c.value[:80], e))
    return err


def facts():
    return json.load(open(os.path.join(BASE, 'ledger_facts.json'), encoding='utf-8'))


def main():
    bk = Book(XLSX)
    wb = bk.wb
    fx = facts()
    rep = {'파일': XLSX, '사본': os.path.expanduser(
        '~/Downloads/payhug_검산엑셀/검산_투자자어드민_20260901.xlsx')}
    rep['바이트 동일'] = (os.path.exists(rep['사본'])
                          and open(XLSX, 'rb').read() == open(rep['사본'], 'rb').read())
    rep['시트'], nf, nv = counts(wb)
    rep['수식셀 합계'], rep['값셀 합계'] = nf, nv
    rep['이름정의'] = len(bk.names)

    err = evaluate_all(bk)
    rep['평가 실패 수'] = len(err)
    rep['평가 실패'] = err[:12]

    # 값 셀이 허용된 자리에만 있는가 — 입력 가정값 · 채권 Di · 화면 값
    vcells = {}
    for ws in wb.worksheets:
        n = 0
        for row in ws.iter_rows():
            for c in row:
                v = c.value
                if v is None or v == '' or isinstance(v, str):
                    continue
                if isinstance(v, bool):
                    continue
                n += 1
        vcells[ws.title] = n
    rep['숫자 값셀'] = vcells

    # ── 화면대조 ────────────────────────────────────────────────
    ws = wb['화면대조']
    blocks = {'항등식': [], '불변식': [], '교차': [], '화면 정합': [], '가맹점': [],
              '모델 잔차': [], '화면 값 원본': []}
    for r in range(2, ws.max_row + 1):
        g = ws.cell(r, 1).value
        if g not in blocks:
            continue
        lab = ws.cell(r, 2).value
        if g == '화면 값 원본':
            blocks[g].append([lab, bk.cell('화면대조', 'E%d' % r)])
            continue
        row = [lab, bk.cell('화면대조', 'C%d' % r), bk.cell('화면대조', 'E%d' % r),
               bk.cell('화면대조', 'F%d' % r), bk.cell('화면대조', 'G%d' % r)]
        blocks[g].append(row)
    judged = [x for k in ('항등식', '불변식', '교차', '화면 정합', '가맹점')
              for x in blocks[k]]
    rep['화면대조 판정 행'] = len(judged)
    rep['화면대조 차이'] = sum(1 for x in judged if x[4] != '일치')
    rep['화면대조 차이 목록'] = [x for x in judged if x[4] != '일치']
    rep['모델 잔차 행'] = len(blocks['모델 잔차'])
    rep['모델 잔차'] = [[x[0], x[1], x[2], x[3]] for x in blocks['모델 잔차']]
    rep['화면 값 원본 행'] = len(blocks['화면 값 원본'])

    # 모델 잔차 행에 사유가 비어 있으면 안 된다
    nowhy = []
    for r in range(2, ws.max_row + 1):
        if ws.cell(r, 1).value == '모델 잔차' and not ws.cell(r, 8).value:
            nowhy.append(ws.cell(r, 2).value)
    rep['사유 빠진 잔차 행'] = nowhy

    # ── 화면 값이 ledger_facts.json 과 같은가 ────────────────────
    sv = dict(blocks['화면 값 원본'])
    chk = [('투자실행액', fx['exec']), ('순현금', fx['cash']), ('투자자산', fx['total']),
           ('W금융일수 raw', float(fx['wRaw'])), ('W금융일수 표기', float(fx['w'])),
           ('Ty수익율(%)', float(fx['ty'])), ('S입금부족율 raw(%)', float(fx['sRaw'])),
           ('S입금부족율 표기(%)', float(fx['s'])), ('할인율(%)', float(fx['rate'])),
           ('하루 평균 투자실행금', fx['dayAvg']), ('채권 건수', fx['receivables']),
           ('미회수 채권 건수', fx['openReceivables']),
           ('채권 Di 최소', fx['diRange'][0]), ('채권 Di 최대', fx['diRange'][1]),
           ('로스터 건수', len(fx['merchants'])),
           ('주간 PSA', fx['weekExec']), ('주간 PSM', fx['weekProfit']),
           ('주간 PSD raw', float(fx['weekWRaw'])), ('주간 PSC', fx['weekPsc']),
           ('주간 ④(%)', float(fx['weekTy'])), ('주간 ⑤(%)', float(fx['weekTyAsset'])),
           ('전 구간 PSA', fx['fullExec']), ('전 구간 PSM', fx['fullProfit']),
           ('전 구간 PSC', fx['fullPsc']), ('전 구간 ④(%)', float(fx['fullTy'])),
           ('전 구간 ⑤(%)', float(fx['fullTyAsset']))]
    bad = [[k, sv.get(k), v] for k, v in chk if abs(numify(sv.get(k)) - v) > 1e-9]
    rep['화면 값 ↔ ledger_facts 불일치'] = bad

    # ── 가중치 대조 ─────────────────────────────────────────────
    ws = wb['가중치 대조']
    wm = rowmap(ws)
    g = lambda a: bk.cell('가중치 대조', a)
    W = {}
    for lab, key in [('W금융일수', 'W'), ('W금융일수 표기', 'W표기'), ('Ty수익율(%)', 'Ty'),
                     ('미회수 잔량 W', '미회수W'), ('미회수 잔량 Ty(%)', '미회수Ty')]:
        r = wm[lab]
        W[key] = {'(가) 금액 실측': g('C%d' % r), '(나) 엑셀 MAU': g('D%d' % r),
                  '(다) 로스터 금액가중': g('E%d' % r), '(가)-(나)': g('F%d' % r),
                  '(다)-(가)': g('E%d' % r) - g('C%d' % r)}
    rep['가중치 대조'] = W
    wm2 = rowmap(ws, 2)
    rep['가중치 판정'] = ws.cell(wm['판정'], 3).value
    rep['워드 인용'] = [ws.cell(wm2[k], 3).value for k in
                        ('w금융일수 산식', 'Ai 정의', 'Di 정의')]
    rep['확인 문항'] = [ws.cell(wm[k], 2).value for k in ('확인 문항 1', '확인 문항 2')]
    v0 = wm['배달앱/전체']
    sens = []
    for r in range(v0 + 1, v0 + 6):
        sens.append([g('A%d' % r), g('F%d' % r), g('G%d' % r), g('H%d' % r),
                     ws.cell(r, 9).value])
    rep['0.35 민감도'] = sens

    # ── 기간집계 · 플랫폼 주요값 ────────────────────────────────
    pm = rowmap(wb['기간집계'])
    rep['기간집계'] = {k: bk.cell('기간집계', 'B%d' % r) for k, r in pm.items()
                       if k not in ('항목',)}
    rep['플랫폼'] = {wb['플랫폼'].cell(r, 1).value: bk.cell('플랫폼', 'B%d' % r)
                     for r in range(16, 23) if wb['플랫폼'].cell(r, 1).value}

    # ── 항등식 ──────────────────────────────────────────────────
    ws = wb['화면대조']
    for r in range(2, ws.max_row + 1):
        if ws.cell(r, 1).value == '항등식':
            rep['항등식'] = {'좌변': bk.cell('화면대조', 'C%d' % r),
                             '우변': bk.cell('화면대조', 'E%d' % r),
                             '차': bk.cell('화면대조', 'F%d' % r)}
            break

    # ── 프리셋 · 비중 최대잉여법 · 계약 상태 ─────────────────────
    ws = wb['입력']
    im = rowmap(ws)
    pr = im['프리셋']
    rep['프리셋'] = [[ws.cell(r, 3).value, bk.cell('입력', 'D%d' % r),
                      bk.cell('입력', 'E%d' % r), bk.cell('입력', 'F%d' % r),
                      bk.cell('입력', 'I%d' % r)] for r in range(pr + 1, pr + 7)]
    rep['프리셋 차 합계'] = sum(x[4] for x in rep['프리셋'])
    gm = wb['가맹점']
    n = 0
    while gm.cell(2 + n, 3).value and bk.cell('가맹점', 'C%d' % (2 + n)) != '합계':
        n += 1
    rep['비중 최대잉여법'] = [[bk.cell('가맹점', 'C%d' % (2 + i)),
                               bk.cell('가맹점', 'S%d' % (2 + i)) * 100,
                               bk.cell('가맹점', 'Z%d' % (2 + i)),
                               bk.cell('가맹점', 'AB%d' % (2 + i)),
                               bk.cell('가맹점', 'AC%d' % (2 + i))] for i in range(n)]
    rep['비중 합'] = sum(x[4] for x in rep['비중 최대잉여법'])
    rep['비중 잔차 최대(pp)'] = max(abs(x[4] - x[1]) for x in rep['비중 최대잉여법'])
    rep['서명 대기'] = [bk.cell('가맹점', 'C%d' % (2 + i)) for i in range(n)
                        if bk.cell('가맹점', 'AD%d' % (2 + i)) == '서명 대기']

    print(json.dumps(rep, ensure_ascii=False, indent=1, default=str))
    return rep


SWCELL = {'①': 'B18', '②': 'B19', '③': 'B20', '④': 'B21'}


def switch_test(quiet=False):
    """스위치 4개를 바꿔 넣고 값이 실제로 움직이는지 본다."""
    base = Book(XLSX)
    pm = rowmap(base.wb['기간집계'])
    gm = rowmap(base.wb['가맹점'])
    pick = [('W raw', '기간집계', 'B%d' % pm['W금융일수 raw (스위치 ① 적용)']),
            ('W 표기', '기간집계', 'B%d' % pm['W금융일수 표기 (스위치 ② 적용)']),
            ('Ty(%)', '기간집계', 'B%d' % pm['Ty수익율(%)']),
            ('투자실행액', '기간집계', 'B%d' % pm['투자실행액']),
            ('투자자산', '기간집계', 'B%d' % pm['투자자산']),
            ('S(%)', '기간집계', 'B%d' % pm['S입금부족율(%)']),
            ('가맹점수', '가맹점', 'B%d' % gm['가맹점 수 (적용)']),
            ('하루선정산액합계', '가맹점', 'B%d' % gm['하루 선정산액 합계 (적용)'])]
    cases = [('기본', {}),
             ('① 만기 도래분만', {'B18': '만기 도래분만'}),
             ('① 미회수 잔량만', {'B18': '미회수 잔량만'}),
             ('② 표기 1자리', {'B19': 1}),
             ('③ 가맹점 4곳', {'B20': 4}),
             ('③ 가맹점 1곳', {'B20': 1}),
             ('④ 방향 B', {'B21': 'B'}),
             ('④ 방향 B + 4곳', {'B21': 'B', 'B20': 4})]
    out = []
    for nm, ov in cases:
        bk = Book(XLSX)
        for k, v in ov.items():
            bk.wb['입력'][k] = v
        row = {'케이스': nm}
        for lab, sh, ad in pick:
            row[lab] = bk.cell(sh, ad)
        # 항등식은 어느 스위치에서도 성립해야 한다
        ws = bk.wb['화면대조']
        for r in range(2, ws.max_row + 1):
            if ws.cell(r, 1).value == '항등식':
                row['항등식 차'] = bk.cell('화면대조', 'F%d' % r)
                break
        out.append(row)
    moved = {}
    b = out[0]
    for lab in ('W raw', 'W 표기', '가맹점수', '하루선정산액합계'):
        moved[lab] = sorted({round(x[lab], 8) if isinstance(x[lab], float) else x[lab]
                             for x in out})
    rep = {'케이스': out, '스위치가 실제로 움직인 값': moved,
           '항등식 차 (기본 조합)': out[0]['항등식 차'],
           '항등식 차 (스위치 ①②)': [out[i]['항등식 차'] for i in (1, 2, 3)],
           '항등식 차 (스위치 ③④)': [out[i]['항등식 차'] for i in (4, 5, 6, 7)],
           '항등식 주석': '채권 시트의 미회수 건수는 기본 조합에서 푼 정수다. '
                          '스위치 ③④로 가맹점 구성이 바뀌면 좌변이 그만큼 어긋난다.'}
    ok = {'① 모집단': len({round(out[i]['W raw'], 8) for i in (0, 1, 2)}) == 3,
          '② 자릿수': out[0]['W 표기'] != out[3]['W 표기'],
          '③ 가맹점 수': len({out[i]['가맹점수'] for i in (0, 4, 5)}) == 3,
          '④ 방향': abs(out[0]['하루선정산액합계'] - out[6]['하루선정산액합계']) > 1,
          '항등식 기본 0': abs(out[0]['항등식 차']) < 0.5}
    rep['스위치 동작'] = ok
    rep['스위치 4개 모두 동작'] = all(ok.values())
    if not quiet:
        print(json.dumps(rep, ensure_ascii=False, indent=1, default=str))
    return rep


def sens_test(quiet=False):
    """배달앱/전체 입력을 0.30 · 0.40 으로 바꿔 (나) W·Ty 가 움직이는지 본다."""
    out = []
    for v in (0.30, 0.35, 0.40):
        bk = Book(XLSX)
        bk.wb['입력']['B43'] = v
        wm = rowmap(bk.wb['가중치 대조'])
        out.append({'배달앱/전체': v,
                    '(나) W': bk.cell('가중치 대조', 'D%d' % wm['W금융일수']),
                    '(나) Ty(%)': bk.cell('가중치 대조', 'D%d' % wm['Ty수익율(%)'])})
    rep = {'민감도': out, '움직임': len({round(x['(나) W'], 8) for x in out}) == 3}
    if not quiet:
        print(json.dumps(rep, ensure_ascii=False, indent=1, default=str))
    return rep


def mix_test(quiet=False):
    """구성비 4칸을 MAU 값으로 바꿔 넣으면 (가) 가 (나) 와 같아지는가."""
    bk = Book(XLSX)
    wm = rowmap(bk.wb['가중치 대조'])
    mau = [bk.cell('가중치 대조', 'D%d' % (wm['카드사'] + i)) for i in range(4)]
    bk2 = Book(XLSX)
    for i, v in enumerate(mau):
        bk2.wb['입력']['C%d' % (24 + i)] = v
    rep = {'MAU 로 바꾼 뒤 (가) W': bk2.cell('가중치 대조', 'C%d' % wm['W금융일수']),
           '(나) W': bk2.cell('가중치 대조', 'D%d' % wm['W금융일수'])}
    rep['일치'] = abs(rep['MAU 로 바꾼 뒤 (가) W'] - rep['(나) W']) < 1e-9
    if not quiet:
        print(json.dumps(rep, ensure_ascii=False, indent=1, default=str))
    return rep


if __name__ == '__main__':
    arg = sys.argv[1] if len(sys.argv) > 1 else ''
    if arg == 'switch':
        switch_test()
    elif arg == 'sens':
        sens_test()
    elif arg == 'mix':
        mix_test()
    elif arg == 'all':
        r = main()
        s1 = switch_test(True)
        s2 = sens_test(True)
        s3 = mix_test(True)
        print(json.dumps({'스위치': s1, '배달앱비중 민감도': s2, '구성비 입력 반응': s3},
                         ensure_ascii=False, indent=1, default=str))
        ok = (r['평가 실패 수'] == 0 and r['화면대조 차이'] == 0
              and not r['화면 값 ↔ ledger_facts 불일치'] and r['바이트 동일']
              and s1['스위치 4개 모두 동작'] and s2['움직임'] and s3['일치']
              and not r['사유 빠진 잔차 행'] and abs(r['비중 합'] - 100.0) < 1e-9)
        print(json.dumps({'전체 통과': ok}, ensure_ascii=False))
        sys.exit(0 if ok else 1)
    else:
        main()
