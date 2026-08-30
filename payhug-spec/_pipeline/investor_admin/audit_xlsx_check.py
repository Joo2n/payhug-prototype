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
        try:
            v = self.wb[sheet][coord].value
            if isinstance(v, str) and v.startswith('='):
                self.nform += 1
                v = self.eval(v[1:], sheet)
            elif isinstance(v, datetime):
                v = v.date()
        finally:
            self.stack.discard(key)
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
def main():
    bk = Book(XLSX)
    wb = bk.wb
    rep = {'파일': XLSX, '시트': {}, '이름정의': len(bk.names)}
    nf = nv = 0
    for ws in wb.worksheets:
        f = v = 0
        for row in ws.iter_rows():
            for c in row:
                if c.value is None:
                    continue
                if isinstance(c.value, str) and c.value.startswith('='):
                    f += 1
                else:
                    v += 1
        nf += f
        nv += v
        rep['시트'][ws.title] = {'행': ws.max_row, '열': ws.max_column, '수식셀': f, '값셀': v}
    rep['수식셀 합계'] = nf
    rep['값셀 합계'] = nv

    # 전 시트 수식 평가
    err = []
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.startswith('='):
                    try:
                        bk.cell(ws.title, c.coordinate)
                    except Exception as e:
                        err.append('%s!%s  %s  → %s' % (ws.title, c.coordinate, c.value, e))
    rep['평가 실패'] = err[:12]
    rep['평가 실패 수'] = len(err)

    # 화면대조
    ws = wb['화면대조']
    diffs, bad = [], 0
    for r in range(2, ws.max_row + 1):
        lab = ws.cell(r, 2).value
        if not lab or (isinstance(lab, str) and lab.startswith('=')):
            continue
        if ws.cell(r, 1).value == '구분':
            continue
        try:
            xv = bk.cell('화면대조', 'C%d' % r)
            sv = bk.cell('화면대조', 'E%d' % r)
            df = bk.cell('화면대조', 'F%d' % r)
            jd = bk.cell('화면대조', 'G%d' % r)
        except Exception as e:
            diffs.append([lab, 'ERR', str(e)])
            continue
        if jd != '일치':
            bad += 1
        diffs.append([ws.cell(r, 1).value, lab, xv, sv, df, jd])
    rep['화면대조 행'] = len(diffs)
    rep['화면대조 차이'] = bad
    rep['화면대조'] = diffs

    # 주요 값
    key = {}
    for sh, addr, lab in [('플랫폼', 'B17', 'W(구성비x만기)'), ('플랫폼', 'B19', '대표 H41 차'),
                          ('플랫폼', 'B21', '미회수 이론 W')]:
        key[lab] = bk.cell(sh, addr)
    ws = wb['기간집계']
    for r in range(2, ws.max_row + 1):
        lab = ws.cell(r, 1).value
        if lab and not str(lab).startswith('='):
            key[str(lab)] = bk.cell('기간집계', 'B%d' % r)
    ws = wb['가맹점']
    for r in range(12, ws.max_row + 1):
        lab = ws.cell(r, 1).value
        if lab and lab != '항목' and lab != '플랫폼':
            key['가맹점/' + str(lab)] = bk.cell('가맹점', 'B%d' % r)
    rep['주요값'] = key

    # 항등식
    lhs = bk.cell('화면대조', 'C2')
    rhs = bk.cell('화면대조', 'E2')
    rep['항등식'] = {'좌변': lhs, '우변': rhs, '차': lhs - rhs}
    print(json.dumps(rep, ensure_ascii=False, indent=1, default=str))
    return rep


def switch_test():
    """스위치 4개를 바꿔 넣고 화면 값이 따라 움직이는지 본다."""
    cases = [
        ('기본', {}),
        ('① 만기 도래분만', {'B18': '만기 도래분만'}),
        ('① 미회수 잔량만', {'B18': '미회수 잔량만'}),
        ('② 표기 1자리', {'B19': 1}),
        ('③ 가맹점 8곳', {'B20': 8}),
        ('③ 가맹점 5곳', {'B20': 5}),
        ('④ 방향 B', {'B21': 'B'}),
        ('④ 방향 B + 8곳', {'B21': 'B', 'B20': 8}),
    ]
    hdr = ['W raw', 'W 표기', 'Ty(%)', '투자실행액', '투자자산', '실행액비중(%)',
           '가맹점수', '하루선정산액합계', 'S(%)', '항등식 차']
    print('%-18s' % '' + ''.join('%16s' % h for h in hdr))
    out = []
    for name, ov in cases:
        bk = Book(XLSX)
        for k, v in ov.items():
            bk.wb['입력'][k] = v
        g = lambda a: bk.cell('기간집계', a)
        row = [g('B29'), g('B30'), g('B31'), g('B32'), g('B34'), g('B35') * 100,
               bk.cell('가맹점', 'B20'), bk.cell('가맹점', 'B17'), g('B39'),
               bk.cell('화면대조', 'C2') - bk.cell('화면대조', 'E2')]
        out.append((name, row))
        print('%-18s' % name + ''.join(
            '%18s' % (('%.6f' % x) if isinstance(x, float) and abs(x) < 1000
                      else ('{:,.1f}'.format(x) if isinstance(x, float) else x))
            for x in row))
    return out


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'switch':
        switch_test()
    else:
        main()
