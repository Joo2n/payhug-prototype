# -*- coding: utf-8 -*-
"""정적 낱장·증명서·엑셀 미리보기의 숫자를 채권 원장값으로 맞춘다.

가맹점 표는 금액 순서까지 원장에서 나오므로 행을 통째로 다시 쓴다.
그 밖에는 숫자 칸만 손댄다 — 마크업·레이아웃·핸들러는 정규식 바깥이라 건드리지 않는다.
값 원천은 daily_ledger(채권 원장) → roster16_model(묶기) 하나뿐이다.

투자자산 낱장 4종·증명서·투자자산 엑셀 미리보기 2종·가맹점·계약기록 건수는
`sync_assets_static` 이 정본이다. 요약 카드·현황표·로스터 표·시트 행을 라벨과 열머리로
잡아 다시 그린다 — 금액을 locator 로 쓰지 않으므로 값을 먼저 바꿔야 할 순서 의존이 없다.
여기서는 그 정본을 호출만 한다.

실행: python3 apply_duration.py
"""
import io, os, re, sys
from decimal import Decimal as D

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from roster16_model import ROSTER, DAILY, MONTHLY, DSUM, MSUM, r2
import sync_assets_static as SA

ROOT = '/Users/semi/cursor/payhug-investor-admin'
hits = []


def edit(name, fn):
    p = os.path.join(ROOT, name)
    s0 = io.open(p, encoding='utf-8').read()
    s1, n = fn(s0)
    if s1 != s0:
        io.open(p, 'w', encoding='utf-8').write(s1)
    hits.append((name, n, 'changed' if s1 != s0 else 'same'))


def _tbody(s, hit, make):
    """가맹점 행이 든 <tbody> 하나를 통째로 다시 쓴다 — 금액 순서가 원장에서 바뀌므로."""
    n = [0]
    def go(m):
        body = m.group(1)
        if not hit(body):
            return m.group(0)
        n[0] += 1
        return '<tbody>' + make(body) + '</tbody>'
    return re.sub(r'<tbody>(.*?)</tbody>', go, s, flags=re.S), n[0]


# ── 1) 투자자산 낱장·증명서·엑셀 미리보기 — sync_assets_static 이 정본 ──────
#   요약 카드는 summary-label, 현황표·로스터 표는 <thead> 첫 칸, 시트 행은 c-head 행으로
#   자리를 잡는다. 금액을 locator 로 쓰지 않으니 금액을 먼저 바꿔야 W·S·Ty 가 들어가는
#   순서 의존이 없다. 자리를 못 잡으면 AssertionError 로 죽는다 — 0건 치환이 성공으로
#   보이지 않게.
def assets(fn):
    def go(s):
        return fn(s), 1
    return go


# ── 5) 투자수익 표 — 일자·월 행의 W·Ty ─────────────────────────────
def profit_rows(rows):
    want = {x['d']: (str(r2(D(str(x['w'])))), str(x['ty'])) for x in rows}
    def go(s):
        n = [0]
        def f(m):
            w, t = want[m.group('d')]
            n[0] += 1
            return ('%s<td class="num">%s</td>\n              <td class="num">%s%%</td>'
                    % (m.group('head'), w, t))
        pat = re.compile(r'(?P<head><td class="mono">(?P<d>\d{4}-\d\d(?:-\d\d)?)</td>\s*'
                         r'<td class="num">[\d,]+</td>\s*<td class="num">[\d,]+</td>\s*'
                         r'<td class="num"><span class="strong">[\d,]+</span></td>\s*)'
                         r'<td class="num">[\d.]+</td>\s*<td class="num">[\d.]+%</td>')
        return pat.sub(lambda m: f(m) if m.group('d') in want else m.group(0), s), n[0]
    return go


def profit_foot(w, t):
    # 합계 행의 '가중평균' 꼬리표는 낱장마다 W 에만 붙기도 하고 Ty 에도 붙기도 한다. 둘 다 받는다.
    def go(s):
        return re.subn(r'(<td class="num">)[\d.]+(<span class="avg-sub">가중평균</span></td>\s*'
                       r'<td class="num">)[\d.]+%(<span class="avg-sub">가중평균</span>)?(</td>)',
                       lambda m: '%s%s%s%s%%%s%s' % (m.group(1), w, m.group(2), t,
                                                     m.group(3) or '', m.group(4)), s)
    return go


def profit_card(ty4, ty5):
    def go(s):
        n = 0
        s, k = re.subn(r'(<div class="ty-label">투자실행금액 대비</div>\s*'
                       r'<div class="summary-value">)[\d.]+(<span class="unit">%</span>)',
                       lambda m: '%s%s%s' % (m.group(1), ty4, m.group(2)), s)
        n += k
        s, k = re.subn(r'(<div class="ty-label">투자자산 대비</div>\s*'
                       r'<div class="summary-value">)[\d.]+(<span class="unit">%</span>)',
                       lambda m: '%s%s%s' % (m.group(1), ty5, m.group(2)), s)
        n += k
        return s, n
    return go


def chain(*fns):
    def go(s):
        n = 0
        for fn in fns:
            s, k = fn(s)
            n += k
        return s, n
    return go


# ── 6) 엑셀 미리보기 · 투자수익 ────────────────────────────────────
#   미리보기 낱장은 실물 엑셀과 같은 값을 보여야 한다 — 행 전체를 원장값으로 다시 쓴다.
def _xrow(no, d, r, cls=''):
    return ('<tr%s><th class="row-head">%s</th><td%s>%s</td><td class="c-num">%s</td>'
            '<td class="c-num">%s</td><td class="c-num">%s</td><td class="c-num">%s</td>'
            '<td class="c-num">%s%%</td><td class="c-empty"></td></tr>'
            % (cls, no, ' class="mono"' if len(d) == 10 else '', d,
               format(r['repay'], ','), format(r['exec'], ','), format(r['profit'], ','),
               r2(D(str(r['w']))), r2(D(str(r['ty'])))))


def xls_profit_daily(s):
    n = [0]
    seq = list(DAILY)
    def f(m):
        if n[0] >= len(seq):
            return m.group(0)
        r = seq[n[0]]; n[0] += 1
        return _xrow(m.group('no'), r['d'], r)
    pat = re.compile(r'<tr><th class="row-head">(?P<no>\d+)</th><td class="mono">[\d-]+</td>'
                     r'<td class="c-num">[\d,]+</td><td class="c-num">[\d,]+</td>'
                     r'<td class="c-num">[\d,]+</td><td class="c-num">[\d.]+</td>'
                     r'<td class="c-num">[\d.]+%</td><td class="c-empty"></td></tr>')
    s = pat.sub(f, s)
    tot = dict(repay=DSUM['repay'], exec=DSUM['exec'], profit=DSUM['profit'],
               w=DSUM['w'], ty=DSUM['ty'])
    s, k = re.subn(r'<tr class="r-total"><th class="row-head">(\d+)</th><td>합계</td>'
                   r'<td class="c-num">[\d,]+</td><td class="c-num">[\d,]+</td>'
                   r'<td class="c-num">[\d,]+</td><td class="c-num">[\d.]+</td>'
                   r'<td class="c-num">[\d.]+%</td><td class="c-empty"></td></tr>',
                   lambda m: _xrow(m.group(1), '합계', tot, ' class="r-total"'), s)
    return s, n[0] + k


def xls_profit_status(s):
    n = 0
    for lbl, val in (('투자실행금', format(DSUM['exec'], ',')),
                     ('투자수익', format(DSUM['profit'], ','))):
        s, k = re.subn(r'(<td>%s</td><td class="c-num">)[\d,]+' % lbl,
                       lambda m: m.group(1) + val, s); n += k
    s, k = re.subn(r'(투자실행금액 대비\)</td><td class="c-num">)[\d.]+%',
                   lambda m: '%s%s%%' % (m.group(1), DSUM['ty']), s); n += k
    s, k = re.subn(r'(투자자산 대비\)</td><td class="c-num">)[\d.]+%',
                   lambda m: '%s%s%%' % (m.group(1), DSUM['tyAsset']), s); n += k
    return s, n


# ── 7) 가맹점 관리 표 — 원장 순서(투자금액 내림차순) 그대로 ────────
#   통합본 RENDER['merchants'] 가 원장 순서로 그린다. 정적 낱장도 같은 순서라야 한다.
MC_ROW = ('%s<tr>\n%s  <td class="no">%d</td>\n%s  <td class="mono">%s</td>\n'
          '%s  <td><span class="name">%s</span></td>\n%s  <td class="mono">%s</td>\n'
          '%s  <td>%s</td>\n%s  <td>%s</td>\n%s  <td>%s</td>\n'
          '%s  <td><span class="badge sm badge-primary">A-001</span> \u321c\ud398\uc774\ud5c8\uadf8</td>\n%s</tr>')


def mc_rows(s):
    def hit(b):
        return '<td class="no">' in b and '<span class="name">' in b and 'M2026-' in b
    def make(b):
        ind = re.search(r'\n(\s*)<tr>', b).group(1)
        cnt = b.count('<tr>')
        out = ''
        for i, x in enumerate(ROSTER[:cnt]):
            out += '\n' + MC_ROW % (ind, ind, i + 1, ind, x[4], ind, x[0], ind, x[5],
                                    ind, x[6], ind, x[7], ind, x[8], ind, ind)
        return out + '\n' + ind[:-2]
    return _tbody(s, hit, make)


if __name__ == '__main__':
    # 정본이 다루지 않는 자리 — 가맹점 관리 표 본문(MID·사업자번호·대표자·업종·품목)
    EXTRA = {'merchants.html': mc_rows}
    for name, fn in SA.PLAN:
        more = EXTRA.get(name)
        edit(name, chain(assets(fn), more) if more else assets(fn))

    day = chain(profit_rows(DAILY), profit_foot(DSUM['w'], DSUM['ty']),
                profit_card(DSUM['ty'], DSUM['tyAsset']))
    edit('invest-profit.html', day)
    mon = chain(profit_rows(MONTHLY), profit_foot(MSUM['w'], MSUM['ty']),
                profit_card(MSUM['ty'], MSUM['tyAsset']))
    edit('invest-profit--monthly.html', mon)
    edit('xls-profit-daily.html', xls_profit_daily)
    edit('xls-profit-status.html', xls_profit_status)

    for name, n, st in hits:
        print('  %-34s %3d칸  %s' % (name, n, st))
