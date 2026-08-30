# -*- coding: utf-8 -*-
"""투자자산 정적 낱장·증명서·엑셀 미리보기의 요약 카드·현황표·로스터 표를 모델에서 다시 그린다.

값은 `roster16_model` 하나에서 나온다. 이 파일에는 금액도 비중도 건수도 적혀 있지 않다.

자리는 값이 아니라 구조로 잡는다.

    요약 카드   <div class="summary-label">라벨</div> 다음의 summary-value·summary-sub
    현황표      <thead> 첫 칸이 `자산 구분` 인 표의 <tbody>
    로스터 표   <thead> 첫 칸이 `가맹점` 인 표의 <tbody>
    엑셀 시트   `c-head` 행 다음 줄부터 </tbody> 까지
    계약기록 표 <thead> 첫 칸이 체크박스인 표의 <tbody>
    페이지네이션 pg-size 의 selected 옵션(1쪽 행수) · page-btn active(현재 쪽)
    건수        `<b class="mono">N</b>건` · `다운로드 (N)` · `N건 선택`

옛 값 문자열을 locator 로 쓰면 값이 한 세대 바뀌는 순간 0건 치환이 되고, 0건 치환은
실패로 보이지 않는다. 그래서 기대한 자리를 못 잡으면 AssertionError 로 죽는다.

대상에서 뺀 낱장
    invest-assets--empty.html   요약 카드가 0·현황표·로스터 표가 `조회 결과가 없습니다.` —
                                모델에서 나올 값이 없다.
    contracts--empty.html       0건 상태.

검색 적용 낱장(merchants--filtered.html)은 건수가 로스터 곳수가 아니라 **검색 결과 곳수**다.
화면에 박힌 조건 칩(업종 `음식점업` · 검색어 `곱창`)을 그대로 걸어 로스터에서 다시 추린다.
    contracts.html 의 `3건 선택`  기본 선택 건수이지 로스터 건수가 아니다.
                                (선택 MID 3건은 통합본 build_app.py 의 CT.sel 과 같은 값이다)

실행
    python3 sync_assets_static.py            다시 그려 파일에 쓴다
    python3 sync_assets_static.py --check    쓰지 않고 어긋난 낱장만 보고(어긋나면 종료코드 1)
"""
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from roster16_model import (ROSTER, SHARES, EXEC, CASH, TOTAL, W_W, S_W, TY_W,   # noqa: E402
                            EXEC_SHARE, CASH_SHARE, ty, r2, f,
                            contract_signed, contract_default_sel)
import daily_ledger as LG                                                       # noqa: E402

# 계약기록 표의 기본 선택 3건 — 통합본 build_app.py 의 `var CT_SEL0` 과 같은 원천에서 나온다.
CT_SEL = contract_default_sel()

# 열머리 모집단 툴팁의 건수 — 채권 원장 실측. 낱장에 손으로 적지 않는다.
POP_N_W = len(LG.RECEIVABLES)
POP_N_S = LG.facts()['sampleReceivables']

# 검색 적용 낱장에 박혀 있는 조건 — 화면의 칩·입력값과 같은 값이다.
MC_SECTOR, MC_KEYWORD = '음식점업', '곱창'

ROOT = '/Users/semi/cursor/payhug-investor-admin'

# 엑셀 미리보기 시트 끝에 두는 빈 행 수 — 실물 엑셀이 시트 하단에 남기는 여백과 같다.
SHEET_BLANKS = 4

W_ROW = str(r2(W_W))
S_ROW = str(r2(S_W))
TY_ROW = str(r2(TY_W))
N_ROSTER = len(ROSTER)

# (상호, 투자금액, W금융일수, S입금부족율, Ty수익율, 비중) — 순서까지 원장이 정한다.
CELLS = [(x[0], f(x[1]), x[2], x[3], str(ty(x[2])), str(sh)) for x, sh in zip(ROSTER, SHARES)]


# ── 자리 잡기 ─────────────────────────────────────────────────────
TABLE = re.compile(r'<table class="(?P<cls>[\w-]+)">.*?</table>', re.S)
HEAD1 = re.compile(r'<thead>\s*<tr>\s*<th[^>]*>([^<]*)</th>', re.S)
TBODY = re.compile(r'(<tbody>)(.*?)(</tbody>)', re.S)


def table_by_head(s, cls, head):
    """<thead> 첫 칸 텍스트로 표 하나를 잡는다 — 표 안의 값이 무엇이든 자리를 잃지 않는다."""
    hits = []
    for m in TABLE.finditer(s):
        if m.group('cls') != cls:
            continue
        h = HEAD1.search(m.group(0))
        if h and h.group(1).strip() == head:
            hits.append(m)
    assert len(hits) == 1, 'table.%s 열머리 `%s` %d건 — 1건이라야 한다' % (cls, head, len(hits))
    return hits[0]


def swap_tbody(s, span, rows):
    """표 하나의 <tbody> 안쪽을 통째로 다시 쓴다. 들여쓰기는 원본 첫 <tr> 에서 읽는다."""
    a, b = span
    blk = s[a:b]
    m = TBODY.search(blk)
    assert m, '<tbody> 없음'
    ind = re.search(r'\n([ \t]*)<tr', m.group(2))
    assert ind, '<tbody> 안에 <tr> 없음'
    ind = ind.group(1)
    body = ''.join('\n' + r for r in rows) + '\n' + ind[:-2]
    blk = blk[:m.start(2)] + body + blk[m.end(2):]
    return s[:a] + blk + s[b:], ind


def tr(ind, cells, cls=''):
    out = '%s<tr%s>\n' % (ind, cls)
    for c in cells:
        out += '%s  %s\n' % (ind, c)
    return out + '%s</tr>' % ind


# ── 1) 요약 카드 4장 ──────────────────────────────────────────────
CARD = re.compile(
    r'(?P<a><div class="summary-label">(?P<label>[^<]+)</div>\s*<div class="summary-value">)'
    r'(?P<val>[^<]*)'
    r'(?P<b><span class="unit">(?P<unit>[^<]*)</span></div>\s*<div class="summary-sub">)'
    r'(?P<sub>[^<]*)'
    r'(?P<c></div>)')


def card_spec():
    """라벨 → (값, 단위, 보조줄). 보조줄이 None 이면 값이 아니라 산식 라벨이라 그대로 둔다."""
    return {
        '투자자산':   (f(TOTAL), '원', None),
        '투자실행액': (f(EXEC),  '원', '비중 %s%% · 보관 ㈜페이허그' % EXEC_SHARE),
        '순현금':     (f(CASH),  '원', '비중 %s%% · 보관 ㈜쿠콘' % CASH_SHARE),
        'Ty수익율':   (TY_ROW,   '%', 'W금융일수 %s일 기준' % W_ROW),
    }


def summary_cards(s):
    spec = card_spec()
    seen = []

    def go(m):
        lb = m.group('label')
        if lb not in spec:
            return m.group(0)
        val, unit, sub = spec[lb]
        assert m.group('unit') == unit, '카드 `%s` 단위 %s ≠ %s' % (lb, m.group('unit'), unit)
        seen.append(lb)
        return m.group('a') + val + m.group('b') + (m.group('sub') if sub is None else sub) + m.group('c')

    s = CARD.sub(go, s)
    assert sorted(seen) == sorted(spec), '요약 카드 %s ≠ %s' % (sorted(seen), sorted(spec))
    return s


# ── 2) 현황표 3행 ─────────────────────────────────────────────────
NONE_CELL = '<td class="num"><span class="none">-</span></td>'


def status_rows(ind):
    return [
        tr(ind, ['<td><span class="name">투자실행액</span></td>',
                 '<td class="num"><span class="strong">%s</span></td>' % f(EXEC),
                 '<td class="num">%s일</td>' % W_ROW,
                 '<td class="num">%s%%</td>' % S_ROW,
                 '<td class="num">%s%%</td>' % TY_ROW,
                 '<td class="num">%s%%</td>' % EXEC_SHARE,
                 '<td>㈜페이허그</td>']),
        tr(ind, ['<td><span class="name">순현금</span></td>',
                 '<td class="num"><span class="strong">%s</span></td>' % f(CASH),
                 NONE_CELL, NONE_CELL, NONE_CELL,
                 '<td class="num">%s%%</td>' % CASH_SHARE,
                 '<td>㈜쿠콘</td>']),
        tr(ind, ['<td>합계 (투자자산)</td>',
                 '<td class="num">%s</td>' % f(TOTAL),
                 NONE_CELL, NONE_CELL, NONE_CELL,
                 '<td class="num">%s%%</td>' % (EXEC_SHARE + CASH_SHARE),
                 '<td><span class="none">-</span></td>'], cls=' class="total-row"'),
    ]


def status_table(s):
    m = table_by_head(s, 'tbl', '자산 구분')
    ind = re.search(r'\n([ \t]*)<tr', TBODY.search(m.group(0)).group(2)).group(1)
    return swap_tbody(s, (m.start(), m.end()), status_rows(ind))[0]

# ── 2-1) 열머리 모집단 툴팁 ───────────────────────────────────────
#   W금융일수·S입금부족율·옆 칸 금액이 각자 다른 집합에서 나온다. 행을 금액으로 가중평균해도
#   현황표의 두 칸과 맞아떨어지지 않는 자리라, 열머리가 자기 모집단을 스스로 말한다.
#   마크업은 통합본 build_app.py 의 popTh() 와 같다.
POP = (('W금융일수', '대상정산금채권 전체 (발생 기준)', POP_N_W),
       ('S입금부족율', '선정산일 D-20 ~ D-11 표본', POP_N_S))


def pop_th(label, of, n):
    return ('<th class="num"><span class="tooltip wide"><span class="tip-anchor">%s</span>'
            '<span class="tip-panel">%s'
            '<span class="tip-row"><span>채권 건수</span><span class="tip-green">%s건</span></span>'
            '</span></span></th>' % (label, of, f(n)))


def pop_heads(s):
    """현황표·가맹점별 표의 두 열머리를 툴팁 붙은 것으로. 이미 붙어 있으면 통째로 갈아 끼운다."""
    for label, of, n in POP:
        pat = re.compile(
            r'<th class="num">(?:%s|<span class="tooltip wide"><span class="tip-anchor">%s</span>'
            r'.*?</span></span>)</th>' % (re.escape(label), re.escape(label)), re.S)
        s, k = pat.subn(lambda _m: pop_th(label, of, n), s)
        assert k == 2, '열머리 `%s` %d건 — 현황표·가맹점별 표 2건이라야 한다' % (label, k)
    return s



# ── 3) 로스터 표 (가맹점별 투자자산) ──────────────────────────────
def roster_rows(ind, sl):
    return [tr(ind, ['<td><span class="name">%s</span></td>' % c[0],
                     '<td class="num"><span class="strong">%s</span></td>' % c[1],
                     '<td class="num">%s일</td>' % c[2],
                     '<td class="num">%s%%</td>' % c[3],
                     '<td class="num">%s%%</td>' % c[4],
                     '<td class="num">%s%%</td>' % c[5]]) for c in sl]


def cert_rows(ind):
    return [tr(ind, ['<td>%s</td>' % c[0],
                     '<td class="num">%s</td>' % c[1],
                     '<td class="num">%s일</td>' % c[2],
                     '<td class="num">%s%%</td>' % c[3],
                     '<td class="num">%s%%</td>' % c[4],
                     '<td class="num">%s%%</td>' % c[5]]) for c in CELLS]


# ── 4) 페이지네이션 — 1쪽 행수·현재 쪽을 마크업에서 읽는다 ────────
PGSIZE = re.compile(r'<option value="(\d+)" selected>')
PGACT = re.compile(r'<button class="page-btn active">(\d+)</button>')
BTNRUN = re.compile(r'(?:[ \t]*<button class="page-btn(?: active)?">\d+</button>\n)+')
ARROW = re.compile(r'<button class="page-arrow"( disabled)?>')


def page_size(s):
    got = PGSIZE.findall(s)
    assert len(got) == 1, 'pg-size selected %d건 — 1건이라야 한다' % len(got)
    return int(got[0])


def page_now(s):
    got = PGACT.findall(s)
    assert len(got) == 1, 'page-btn active %d건 — 1건이라야 한다' % len(got)
    return int(got[0])


def paginate(s, page, pages):
    """쪽 버튼 묶음과 좌·우 화살표를 총 쪽수에 맞춘다. 총 쪽수는 로스터 건수에서 나온다."""
    assert 1 <= page <= pages, '현재 쪽 %d — 총 %d쪽' % (page, pages)
    m = BTNRUN.search(s)
    assert m, 'page-btn 묶음 없음'
    ind = re.match(r'[ \t]*', m.group(0)).group(0)
    btns = ''.join('%s<button class="page-btn%s">%d</button>\n'
                   % (ind, ' active' if i == page else '', i) for i in range(1, pages + 1))
    s = s[:m.start()] + btns + s[m.end():]
    arrows = ARROW.findall(s)
    assert len(arrows) == 2, 'page-arrow %d개 — 2개라야 한다' % len(arrows)
    want = [page > 1, page < pages]
    n = [0]

    def go(mm):
        i = n[0]
        n[0] += 1
        return '<button class="page-arrow"%s>' % ('' if want[i] else ' disabled')

    return ARROW.sub(go, s)


# ── 5) 엑셀 미리보기 시트 ─────────────────────────────────────────
def sheet(s, make):
    """`c-head` 행 다음 줄부터 </tbody> 까지를 다시 쓴다. 행 번호는 c-head 행에서 이어 붙인다."""
    m = TABLE.search(s)
    assert m and m.group('cls') == 'sheet', '<table class="sheet"> 없음'
    t = TBODY.search(m.group(0))
    assert t, '시트 <tbody> 없음'
    body = t.group(2)
    lines = [x for x in body.split('\n') if x.strip()]
    hi = [i for i, x in enumerate(lines) if 'c-head' in x]
    assert len(hi) == 1, 'c-head 행 %d건 — 1건이라야 한다' % len(hi)
    hi = hi[0]
    ind = re.match(r'[ \t]*', lines[hi]).group(0)
    no = int(re.search(r'row-head">(\d+)</th>', lines[hi]).group(1))
    ncols = lines[hi].count('<td')
    rows = lines[:hi + 1] + make(no + 1, ind, ncols)
    new = '\n' + '\n'.join(rows) + '\n' + ind[:-2]
    blk = m.group(0)[:t.start(2)] + new + m.group(0)[t.end(2):]
    return s[:m.start()] + blk + s[m.end():]


def blank_row(no, ind, ncols):
    return '%s<tr><th class="row-head">%d</th>%s</tr>' % (ind, no, '<td class="c-empty"></td>' * ncols)


def xls_status_make(no, ind, ncols):
    out = ['%s<tr><th class="row-head">%d</th><td>투자실행액</td><td class="c-num">%s</td>'
           '<td class="c-num">%s</td><td class="c-num">%s%%</td><td class="c-num">%s%%</td>'
           '<td class="c-num">%s%%</td><td>㈜페이허그</td></tr>'
           % (ind, no, f(EXEC), W_ROW, S_ROW, TY_ROW, EXEC_SHARE),
           '%s<tr><th class="row-head">%d</th><td>순현금</td><td class="c-num">%s</td>'
           '<td></td><td></td><td></td><td class="c-num">%s%%</td><td>㈜쿠콘</td></tr>'
           % (ind, no + 1, f(CASH), CASH_SHARE),
           '%s<tr class="r-total"><th class="row-head">%d</th><td>합계 (투자자산)</td>'
           '<td class="c-num">%s</td><td></td><td></td><td></td><td class="c-num">%s%%</td>'
           '<td></td></tr>' % (ind, no + 2, f(TOTAL), EXEC_SHARE + CASH_SHARE)]
    return out + [blank_row(no + 3 + i, ind, ncols) for i in range(SHEET_BLANKS)]


def xls_merchant_make(no, ind, ncols):
    out = []
    for i, c in enumerate(CELLS):
        out.append('%s<tr><th class="row-head">%d</th><td>%s</td><td class="c-num">%s</td>'
                   '<td class="c-num">%s</td><td class="c-num">%s%%</td><td class="c-num">%s%%</td>'
                   '<td class="c-num">%s%%</td><td class="c-empty"></td></tr>'
                   % ((ind, no + i) + c))
    t = no + len(CELLS)
    out.append('%s<tr class="r-total"><th class="row-head">%d</th><td>합계</td>'
               '<td class="c-num">%s</td><td></td><td></td><td></td><td class="c-num">%s%%</td>'
               '<td class="c-empty"></td></tr>' % (ind, t, f(EXEC), EXEC_SHARE + CASH_SHARE))
    return out + [blank_row(t + 1 + i, ind, ncols) for i in range(SHEET_BLANKS)]


# ── 6) 건수 ───────────────────────────────────────────────────────
def sub1(s, pat, rep, what):
    s, n = re.subn(pat, rep, s)
    assert n == 1, '%s %d건 — 1건이라야 한다' % (what, n)
    return s


def total_count(s):
    return sub1(s, r'(<b class="mono">)\d+(</b>건)', r'\g<1>%d\g<2>' % N_ROSTER, '총 N건')


# ── 낱장별 재생성 ─────────────────────────────────────────────────
def build_assets(s):
    s = summary_cards(s)
    s = pop_heads(s)
    s = status_table(s)
    size = page_size(s)
    page = page_now(s)
    pages = -(-N_ROSTER // size)
    sl = CELLS[(page - 1) * size: page * size]
    assert sl, '%d쪽에 실을 행이 없다 — 로스터 %d건 · 1쪽 %d행' % (page, N_ROSTER, size)
    m = table_by_head(s, 'tbl', '가맹점')
    ind = re.search(r'\n([ \t]*)<tr', TBODY.search(m.group(0)).group(2)).group(1)
    s = swap_tbody(s, (m.start(), m.end()), roster_rows(ind, sl))[0]
    return paginate(s, page, pages)


def build_certificate(s):
    m = table_by_head(s, 'doc-tbl', '가맹점')
    ind = re.search(r'\n([ \t]*)<tr', TBODY.search(m.group(0)).group(2)).group(1)
    s = swap_tbody(s, (m.start(), m.end()), cert_rows(ind))[0]
    # 합계는 <tfoot> — 첫 칸 `합계` 로 자리를 잡는다.
    s = sub1(s, r'(<td>합계</td>\s*<td class="num">)[\d,]*(</td>)',
             lambda mm: mm.group(1) + f(EXEC) + mm.group(2), '증명서 합계 금액')
    s = sub1(s, r'(<td>합계</td>(?:\s*<td[^>]*>[^<]*</td>){4}\s*<td class="num">)[\d.]*(%</td>)',
             lambda mm: mm.group(1) + str(EXEC_SHARE + CASH_SHARE) + mm.group(2), '증명서 합계 비중')
    return sub1(s, r'(<span class="k">대상 가맹점</span><span class="v">)\d+(개</span>)',
                r'\g<1>%d\g<2>' % N_ROSTER, '대상 가맹점 N개')


def build_merchants(s):
    s = total_count(s)
    return paginate(s, page_now(s), -(-N_ROSTER // page_size(s)))


XLS_SVG = ('<svg fill="none" stroke="currentColor" viewBox="0 0 24 24">'
           '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" '
           'd="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293'
           'l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>')


def contract_rows(ind, all_sel):
    """계약기록 표 본문 — 순서·MID·상호를 원장 로스터에서 그대로 가져온다.

    전자서명 결과는 정산채권 양수의 서명 대기 큐(roster16_model.SIGN_PENDING)에서 갈린다.
    큐에 남아 있는 가맹점은 아직 서명 전이라 문서가 없다 — 두 화면이 같은 가맹점을 두고
    한쪽은 `서명 대기`, 다른 쪽은 `하나인증서로 서명 완료`라고 말하지 않게 한다.
    """
    out = []
    for i, x in enumerate(ROSTER):
        mid, name = x[4], x[0]
        sg = contract_signed(mid)
        on = sg and (all_sel or mid in CT_SEL)
        chk = ' checked' if on else ('' if sg else ' disabled')
        result = ('<td><button type="button" class="btn btn-excel" disabled>%s 문서 다운로드</button></td>' % XLS_SVG
                  if sg else '<td><span class="badge badge-amber">서명 대기</span></td>')
        means = ('<td class="center"><span class="badge badge-green">하나인증서</span></td>' if sg
                 else '<td class="center"><span class="none">-</span></td>')
        out.append(tr(ind, ['<td><input type="checkbox" class="chk"%s></td>' % chk,
                            '<td class="no">%d</td>' % (i + 1),
                            '<td class="mono">%s</td>' % mid,
                            '<td><span class="name">%s</span></td>' % name,
                            result, means],
                       cls=(' class="clickable selected"' if on else
                            (' class="clickable"' if sg else ''))))
    return out


def n_signed():
    """계약기록에서 고를 수 있는 행 수 = 서명이 끝난 계약 수."""
    return sum(1 for x in ROSTER if contract_signed(x[4]))


def contract_table(s, all_sel):
    # 계약기록 표의 첫 칸은 체크박스라 열머리 텍스트가 없다. 두 번째·세 번째 열머리로 잡는다.
    hits = [m for m in TABLE.finditer(s)
            if m.group('cls') == 'tbl' and '<th class="no">No</th>' in m.group(0)
            and '<th>MID</th>' in m.group(0)]
    assert len(hits) == 1, '계약기록 표 %d건 — 1건이라야 한다' % len(hits)
    m = hits[0]
    ind = re.search(r'\n([ \t]*)<tr', TBODY.search(m.group(0)).group(2)).group(1)
    return swap_tbody(s, (m.start(), m.end()), contract_rows(ind, all_sel))[0]


def build_contracts(s):
    s = total_count(s)
    s = contract_table(s, False)
    return paginate(s, page_now(s), -(-N_ROSTER // page_size(s)))


def build_contracts_all(s):
    n = n_signed()                       # `전체 선택`은 고를 수 있는 행 전부다
    s = total_count(s)
    s = contract_table(s, True)
    s = paginate(s, page_now(s), -(-N_ROSTER // page_size(s)))
    s = sub1(s, r'(선택 문서 다운로드 \()\d+(\))', r'\g<1>%d\g<2>' % n, '다운로드 (N)')
    return sub1(s, r'(<span class="badge badge-green sel-pill">)\d+(건 선택</span>)',
                r'\g<1>%d\g<2>' % n, 'N건 선택')


MC_ROW = ('%s<tr>\n%s  <td class="no">%d</td>\n%s  <td class="mono">%s</td>\n'
          '%s  <td><span class="name">%s</span></td>\n%s  <td class="mono">%s</td>\n'
          '%s  <td>%s</td>\n%s  <td>%s</td>\n%s  <td>%s</td>\n'
          '%s  <td><span class="badge sm badge-primary">A-001</span> \u321c\ud398\uc774\ud5c8\uadf8</td>\n%s</tr>')


def mc_hit(x):
    """가맹점 검색 — 통합본 RENDER['merchants'] 와 같은 규칙(업종 + 키워드 부분일치)."""
    kw = MC_KEYWORD
    return x[7] == MC_SECTOR and any(kw in str(v) for v in (x[4], x[0], x[5], x[6]))


def build_merchants_filtered(s):
    hits = [x for x in ROSTER if mc_hit(x)]
    assert hits, '검색 조건 `%s`/`%s` 에 걸리는 가맹점이 0곳이다' % (MC_SECTOR, MC_KEYWORD)
    m = table_by_head(s, 'tbl', 'No')
    ind = re.search(r'\n([ \t]*)<tr', TBODY.search(m.group(0)).group(2)).group(1)
    rows = []
    for i, x in enumerate(hits):
        rows.append(MC_ROW % (ind, ind, i + 1, ind, x[4], ind, x[0], ind, x[5],
                              ind, x[6], ind, x[7], ind, x[8], ind, ind))
    s = swap_tbody(s, (m.start(), m.end()), rows)[0]
    return sub1(s, r'(총 <b class="mono">)\d+(</b>건)', r'\g<1>%d\g<2>' % len(hits), '검색 결과 N건')


PLAN = [
    ('invest-assets.html',              build_assets),
    ('invest-assets--download.html',    build_assets),
    ('invest-assets--cert-confirm.html', build_assets),
    # 빈 상태 낱장은 표에 행이 없어 본문을 다시 그릴 것이 없다 — 열머리만 같은 자리에 둔다.
    ('invest-assets--empty.html',       pop_heads),
    ('certificate.html',                build_certificate),
    ('xls-assets-status.html',          lambda s: sheet(s, xls_status_make)),
    ('xls-assets-merchant.html',        lambda s: sheet(s, xls_merchant_make)),
    ('merchants.html',                  build_merchants),
    ('merchants--filtered.html',        build_merchants_filtered),
    ('contracts.html',                  build_contracts),
    ('contracts--all.html',             build_contracts_all),
]


def run(check=False):
    bad = 0
    for name, fn in PLAN:
        p = os.path.join(ROOT, name)
        s0 = io.open(p, encoding='utf-8').read()
        s1 = fn(s0)
        same = s1 == s0
        if check:
            if not same:
                bad += 1
                a, b = s0.split('\n'), s1.split('\n')
                d = [i for i in range(max(len(a), len(b)))
                     if (a[i] if i < len(a) else None) != (b[i] if i < len(b) else None)]
                print('  %-34s DIFF %d줄  첫 줄 %d' % (name, len(d), d[0] + 1 if d else 0))
                for i in d[:3]:
                    print('      낱장 %s' % (a[i].strip() if i < len(a) else '(없음)'))
                    print('      모델 %s' % (b[i].strip() if i < len(b) else '(없음)'))
            else:
                print('  %-34s OK' % name)
            continue
        if not same:
            io.open(p, 'w', encoding='utf-8').write(s1)
        print('  %-34s %s' % (name, 'changed' if not same else 'same'))
    if check:
        print('== 어긋난 낱장 %d / %d ==' % (bad, len(PLAN)))
        return 1 if bad else 0
    return 0


if __name__ == '__main__':
    print('로스터 %d건 · 투자실행액 %s · 순현금 %s · 투자자산 %s · W %s일 · S %s%% · Ty %s%%'
          % (N_ROSTER, f(EXEC), f(CASH), f(TOTAL), W_ROW, S_ROW, TY_ROW))
    sys.exit(run('--check' in sys.argv))
