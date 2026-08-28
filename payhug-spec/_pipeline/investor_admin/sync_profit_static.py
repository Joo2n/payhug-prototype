# -*- coding: utf-8 -*-
"""투자 수익 정적 낱장 5종을 통합본(app.html)의 같은 상태에 맞춘다.

검색 카드(프리셋 줄·날짜 줄·집계 단위 토글), 현황 카드 값, 표 제목·열머리·본문·합계,
표 엑셀 링크를 그 상태 그대로 맞춘다.

  invest-profit.html              일별 · 일주일  2026-08-21 ~ 2026-08-27 · 7행
  invest-profit--weekly.html      주별 · 4주     2026-08-03 ~ 2026-08-30 · 4행   (신설)
  invest-profit--monthly.html     월별 · 6개월   2026-03-01 ~ 2026-08-31 · 6행
  invest-profit--empty.html       일별 · 직접입력 2026-02-01 ~ 2026-02-07 · 0행
  invest-profit--datepicker.html  일별 · 일주일  2026-08-21 ~ 2026-08-27 · 7행 (달력 열림)

주별 낱장은 월별 낱장을 본으로 삼아 만든다 — 두 화면이 버킷 표라는 점에서 구조가 같다.
"""
import io, os, re, sys

REPO = '/Users/semi/cursor/payhug-investor-admin/'

TOGGLE = ('      <div class="toggle">\n'
          '        <button class="toggle-btn%s">일별</button>\n'
          '        <button class="toggle-btn%s">주별</button>\n'
          '        <button class="toggle-btn%s">월별</button>\n'
          '      </div>\n')

DATES = ('      <div class="filter-row">\n'
         '        <div class="filter-field">\n'
         '          <label>시작일</label>\n'
         '          <input type="date" class="input%s" value="%s">\n'
         '%s'
         '        </div>\n'
         '        <div class="filter-tilde">~</div>\n'
         '        <div class="filter-field">\n'
         '          <label>종료일</label>\n'
         '          <input type="date" class="input" value="%s">\n'
         '        </div>\n'
         '        <button class="btn btn-primary">검색</button>\n'
         '        <button class="btn btn-outline">초기화</button>\n'
         '      </div>\n')

# 집계 단위별 — (표 제목, 열머리, 표 엑셀 파일, 현황 카드 엑셀 파일)
#   현황 카드도 집계 단위마다 기간이 다르다. 카드가 4주를 말하는데 링크가 일주일 파일이면
#   화면과 파일이 다른 기간을 말한다 — 그래서 두 링크를 따로 맞춘다.
GRAN = {
    'daily':   ('일별 투자수익', '정산예정일', '일별투자수익_2026-08-21_2026-08-27.xlsx',
                '투자수익현황_2026-08-21_2026-08-27.xlsx'),
    'weekly':  ('주별 투자수익', '정산예정주', '주별투자수익_2026-08-03_2026-08-30.xlsx',
                '투자수익현황_2026-08-03_2026-08-30.xlsx'),
    'monthly': ('월별 투자수익', '정산예정월', '월별투자수익_2026-03-01_2026-08-31.xlsx',
                '투자수익현황_2026-03-01_2026-08-31.xlsx'),
}

BLOCK = re.compile(r'    <div class="search-bar">.*?\n    </div>\n', re.S)
POPUP = re.compile(r'(          <div class="datepicker">.*?\n          </div>\n)', re.S)
TBODY = re.compile(r'          <tbody>\n.*?\n          </tfoot>\n', re.S)


def presets(pairs):
    """pairs = [(라벨, 활성여부), ...] — 그 집계 단위의 프리셋만 싣는다."""
    out = '      <div class="preset-row">\n'
    for label, on in pairs:
        out += '        <button class="preset-btn%s">%s</button>\n' % (' active' if on else '', label)
    return out + '      </div>\n'


# 기간 역전 안내 — 통합본과 같은 자리·같은 원문(payhug-admin-web/components/DateRangeFilter.tsx:14)
WARN = '      <p class="range-warn" hidden>시작일은 종료일보다 이후일 수 없습니다.</p>\n'


def search_bar(pre, frm, to, gran, focus='', popup=''):
    act = lambda g: ' active' if g == gran else ''
    return ('    <div class="search-bar">\n'
            + presets(pre)
            + DATES % (focus, frm, popup, to)
            + WARN
            + TOGGLE % (act('daily'), act('weekly'), act('monthly'))
            + '    </div>\n')


def table_block(rows, foot):
    out = '          <tbody>\n'
    for d, repay, ex, pf, w, ty in rows:
        out += ('            <tr>\n'
                '              <td class="mono">%s</td>\n'
                '              <td class="num">%s</td>\n'
                '              <td class="num">%s</td>\n'
                '              <td class="num"><span class="strong">%s</span></td>\n'
                '              <td class="num">%s</td>\n'
                '              <td class="num">%s</td>\n'
                '            </tr>\n' % (d, repay, ex, pf, w, ty))
    out += ('          </tbody>\n'
            '          <tfoot>\n'
            '            <tr>\n'
            '              <td>합계</td>\n'
            '              <td class="num">%s</td>\n'
            '              <td class="num">%s</td>\n'
            '              <td class="num">%s</td>\n'
            '              <td class="num">%s<span class="avg-sub">가중평균</span></td>\n'
            '              <td class="num">%s<span class="avg-sub">가중평균</span></td>\n'
            '            </tr>\n'
            '          </tfoot>\n' % foot)
    return out


DAILY_PRE = lambda week_on: [('일주일', week_on), ('금월', False)]

# ── 표 본문·현황 카드 — 전부 채권 원장에서 나온다 ────────────────
#   일별 = 원장 그대로, 주별·월별 = 원장을 주·달로 묶은 것(build_xlsx.rollup = 화면 rollupBy).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from decimal import Decimal as D                                  # noqa: E402
import roster16_model as RM                                       # noqa: E402
import build_xlsx as BX                                           # noqa: E402

WEEK_RANGE = ('2026-08-03', '2026-08-30')
_wk = BX.rollup(WEEK_RANGE[0], WEEK_RANGE[1], BX._mon_start,
                lambda d: BX._mon_start(d) + ' ~ ' + BX._sun_end(d)[5:])
_wtot = BX.bucket(_wk, '합계')


def _fmt(rows):
    return [(r['d'], f(r['repay']), f(r['exec']), f(r['profit']),
             str(RM.r1(D(str(r['w'])))), str(RM.r2(D(str(r['ty'])))) + '%') for r in rows]


def _foot(sm):
    return (f(sm['repay']), f(sm['exec']), f(sm['profit']),
            str(RM.r1(D(str(sm['w'])))), str(RM.r2(D(str(sm['ty'])))) + '%')


f = lambda n: format(n, ',')
_wkasset = RM.ty_asset(_wtot['ty'], _wtot['exec'],
                       len([r for r in RM.LEDGER if WEEK_RANGE[0] <= r['d'] <= WEEK_RANGE[1]]))

# 화면별 (검색대상기간 라벨, 구간, 표 행, 표 합계, 카드 투자실행금·투자수익·④·⑤)
VIEW = {
    'daily':   ('일주일', '2026-08-21 ~ 2026-08-27', _fmt(RM.DAILY), _foot(RM.DSUM),
                RM.DSUM['exec'], RM.DSUM['profit'], RM.DSUM['ty'], RM.DSUM['tyAsset']),
    'weekly':  ('4주', '%s ~ %s' % WEEK_RANGE, _fmt(_wk), _foot(_wtot),
                _wtot['exec'], _wtot['profit'], RM.r2(_wtot['ty']), _wkasset),
    'monthly': ('6개월', '2026-03-01 ~ 2026-08-31', _fmt(RM.MONTHLY), _foot(RM.MSUM),
                RM.MSUM['exec'], RM.MSUM['profit'], RM.MSUM['ty'], RM.MSUM['tyAsset']),
}

# Ty 두 칸의 ty-label 은 put_tips 가 툴팁 마크업으로 채운다. 라벨 안쪽을 고정 문자열로 잡으면
# 한 번 채워진 화면에서는 카드가 통째로 안 잡히고 re.sub 가 조용히 0건을 돌려준다 —
# 주별 낱장이 월별 값을 그대로 이고 있던 원인이다. 라벨 안쪽은 문구만 보고 건너뛴다.
CARD = re.compile(
    r'(<div class="summary-label">검색대상기간</div>\s*<div style="[^"]*">)[^<]*(</div>\s*'
    r'<div class="summary-sub mono">)[^<]*(</div>.*?'
    r'<div class="summary-label">투자실행금</div>\s*<div class="summary-value">)[\d,]*('
    r'<span class="unit">원</span></div>.*?'
    r'<div class="summary-label">투자수익</div>\s*<div class="summary-value">)[\d,]*('
    r'<span class="unit">원</span></div>.*?'
    r'투자실행금액 대비.*?<div class="summary-value">)[\d.]*('
    r'<span class="unit">%</span>.*?'
    r'투자자산 대비.*?<div class="summary-value">)[\d.]*('
    r'<span class="unit">%</span>)', re.S)


# Ty수익율 두 칸의 산식 툴팁 — 통합본 build_app.py pfRender 와 같은 마크업.
# ty-label 안쪽을 통째로 갈아 끼우므로 여러 번 돌려도 겹쳐 붙지 않는다.
TY_LABEL = re.compile(r'<div class="ty-label">.*?</div>', re.S)
TIP4 = ('<div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자실행금액 대비</span>'
        '<span class="tip-panel">PSMR × 365 ÷ PSD'
        '<span class="tip-row"><span>PSMR</span><span class="tip-green">투자수익 ÷ 투자실행금</span></span>'
        '<span class="tip-row"><span>PSD</span><span class="tip-green">투자실행금 가중평균 금융일수</span></span>'
        '</span></span></div>')
TIP5 = ('<div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자자산 대비</span>'
        '<span class="tip-panel">(투자실행금액 대비 × PSA) ÷ (PSA + PSC)'
        '<span class="tip-row"><span>PSA</span><span class="tip-green">%s원</span></span>'
        '<span class="tip-row"><span>PSC</span><span class="tip-green">%s원</span></span>'
        '<span class="tip-row sum"><span>EC %d일 합</span><span>기간 순현금 합계</span></span>'
        '</span></span></div>')


def put_tips(s, psa, ec_days):
    tips = [TIP4, TIP5 % (f(psa), f(RM.CASH * ec_days), ec_days)]
    n = [0]
    def take(_m):
        i = n[0]; n[0] += 1
        return tips[i] if i < len(tips) else _m.group(0)
    out = TY_LABEL.sub(take, s)
    assert n[0] == 2, 'ty-label %d건 — 2건이라야 한다' % n[0]
    return out


def put_card(s, v):
    lbl, sub, _rows, _foot_, ex, pf, ty4, ty5 = v
    out, n = CARD.subn(lambda m: (m.group(1) + lbl + m.group(2) + sub + m.group(3) + f(ex)
                                  + m.group(4) + f(pf) + m.group(5) + str(ty4) + m.group(6)
                                  + str(ty5) + m.group(7)), s, count=1)
    assert n == 1, '현황 카드를 못 잡았다 — 카드가 표와 다른 기간을 이고 남는다'
    return out


PLAN = [
    ('invest-profit.html',             DAILY_PRE(True),  '2026-08-21', '2026-08-27', 'daily'),
    ('invest-profit--empty.html',      DAILY_PRE(False), '2026-02-01', '2026-02-07', 'daily'),
    ('invest-profit--datepicker.html', DAILY_PRE(True),  '2026-08-21', '2026-08-27', 'daily'),
    ('invest-profit--monthly.html',    [('3개월', False), ('6개월', True)],
                                                         '2026-03-01', '2026-08-31', 'monthly'),
    ('invest-profit--weekly.html',     [('4주', True), ('12주', False)],
                                                         '2026-08-03', '2026-08-30', 'weekly'),
]

# 낱장별 상태 이름 — 문서 제목 · 제목줄 뱃지가 같은 값을 쓴다
BADGE = {'invest-profit.html': '', 'invest-profit--empty.html': '결과 없음',
         'invest-profit--datepicker.html': '기간 선택',
         'invest-profit--monthly.html': '월별', 'invest-profit--weekly.html': '주별'}


def ec_days(frm, to):
    """EC 합에 들어가는 날수 = 조회 기간에 원장이 갖고 있는 일자 수(통합본 ecDays 와 같다)."""
    return len([r for r in RM.LEDGER if frm <= r['d'] <= to])


def make_weekly():
    """월별 낱장을 본으로 주별 낱장을 만든다 — 검색 카드·제목은 뒤이어 one() 이 맞춘다."""
    s = io.open(REPO + 'invest-profit--monthly.html', encoding='utf-8').read()
    s = put_card(s, VIEW['weekly'])
    s = TBODY.sub(lambda m: table_block(VIEW['weekly'][2], VIEW['weekly'][3]), s, count=1)
    io.open(REPO + 'invest-profit--weekly.html', 'w', encoding='utf-8').write(s)


def put_title(s, name):
    """문서 제목 · 제목줄 뱃지를 그 낱장 상태로. 본을 뜬 화면의 이름이 남지 않게 한다."""
    b = BADGE[name]
    s = re.sub(r'<title>PayHug Admin — 투자 수익[^<]*</title>',
               '<title>PayHug Admin — 투자 수익%s</title>' % (' (%s)' % b if b else ''), s, count=1)
    s = re.sub(r'(<h1 class="page-title">투자 수익)(?: <span class="badge badge-gray state-badge">'
               r'[^<]*</span>)?(</h1>)',
               r'\g<1>%s\g<2>' % (' <span class="badge badge-gray state-badge">%s</span>' % b if b else ''),
               s, count=1)
    return s


PERIOD = re.compile(r'<div class="summary-sub mono">([^<]*)</div>')
DATEIN = re.compile(r'<input type="date" class="input[^"]*" value="([\d-]+)"')
FOOTV  = re.compile(r'<tfoot>.*?</tfoot>', re.S)
CARDV  = re.compile(r'<div class="summary-label">(?:투자실행금|투자수익)</div>\s*'
                    r'<div class="summary-value">([\d,]*)<span class="unit">원</span>')


def assert_period(name, frm, to, gran):
    """카드와 표가 같은 기간을 말하는지 낱장에서 직접 읽어 대조한다.

    D-36·D-37 — 화면 숫자는 원장 한 벌에서 나오고, 한 화면 안에서 카드와 표가 어긋나면 안 된다.
    주별 낱장이 월별 카드(6개월·88,449,097,042)를 이고 표는 4주 합계를 보이던 일을 여기서 막는다.
    """
    s = io.open(REPO + name, encoding='utf-8').read()
    lbl, sub, rows, foot = VIEW[gran][0], VIEW[gran][1], VIEW[gran][2], VIEW[gran][3]
    empty = name == 'invest-profit--empty.html'

    got = DATEIN.findall(s)
    assert got == [frm, to], '%s 조회 입력 %s ≠ %s~%s' % (name, got, frm, to)

    per = PERIOD.findall(s)
    assert len(per) == 1, '%s 검색대상기간 %d건' % (name, len(per))
    want = '%s ~ %s' % (frm, to) if empty else sub
    assert per[0] == want, '%s 카드 기간 %s ≠ 조회 %s' % (name, per[0], want)

    body = re.search(r'<tbody>(.*?)</tbody>', s, re.S).group(1)
    n = body.count('<tr>')
    if empty:
        assert n == 1 and '조회 결과가 없습니다.' in body, '%s 빈 상태 행 %d건' % (name, n)
        assert CARDV.findall(s) == ['0', '0'], '%s 빈 상태인데 카드에 값이 있다' % name
        return '행 0 · 카드 %s' % per[0]
    assert n == len(rows), '%s 표 행 %d ≠ %d' % (name, n, len(rows))

    xl = re.findall(r'href="assets/xlsx/([^"]+)" download', s)
    assert xl == [GRAN[gran][3], GRAN[gran][2]], \
        '%s 엑셀 링크 %s ≠ %s' % (name, xl, [GRAN[gran][3], GRAN[gran][2]])

    ft = FOOTV.search(s).group(0)
    fnums = re.findall(r'<td class="num">([\d,.%]+)', ft)
    assert fnums[:3] == list(foot[:3]), '%s 표 합계 %s ≠ %s' % (name, fnums[:3], list(foot[:3]))
    cv = CARDV.findall(s)
    assert cv == [foot[1], foot[2]], '%s 카드 값 %s ≠ 표 합계 %s' % (name, cv, [foot[1], foot[2]])
    assert lbl in s, '%s 검색대상기간 라벨 %s 없음' % (name, lbl)
    return '행 %d · 카드 %s %s · 합계 %s' % (n, lbl, per[0], foot[1])


def one(name, pre, frm, to, gran):
    p = REPO + name
    s = io.open(p, encoding='utf-8').read()
    m = BLOCK.search(s)
    if not m:
        sys.exit('검색 카드 못 찾음 — ' + name)
    old = m.group(0)
    pop = POPUP.search(old)
    new = search_bar(pre, frm, to, gran,
                     focus=' is-focused' if pop else '',
                     popup=pop.group(1) if pop else '')
    s = s[:m.start()] + new + s[m.end():]

    if name != 'invest-profit--empty.html':
        s = put_card(s, VIEW[gran])
        s = TBODY.sub(lambda m: table_block(VIEW[gran][2], VIEW[gran][3]), s, count=1)
        s = put_tips(s, VIEW[gran][4], ec_days(frm, to))
    else:
        s = put_tips(s, 0, ec_days(frm, to))

    # 표 제목·열머리·엑셀 링크 — 그 집계 단위 것으로
    title, col, xls, xls_status = GRAN[gran]
    s = re.sub(r'(<!-- )[가-힣]*\s*투자수익 카드 -->', r'\g<1>%s 카드 -->' % title, s)
    s = re.sub(r'(<h2 class="card-title">)[가-힣]+ 투자수익(</h2>)', r'\g<1>%s\g<2>' % title, s)
    s = re.sub(r'(<th>)정산예정[일주월](</th>)', r'\g<1>%s\g<2>' % col, s)
    s = re.sub(r'(href="assets/xlsx/)(?:일별|주별|월별)투자수익_[^"]+(" download)', r'\g<1>%s\g<2>' % xls, s)
    # 결과 없음 낱장은 두 버튼이 모두 disabled 라 링크가 없다 — 있을 때만 맞춘다.
    n = len(re.findall(r'href="assets/xlsx/투자수익현황_[^"]+" download', s))
    assert n == (0 if name == 'invest-profit--empty.html' else 1), \
        '%s 현황 카드 엑셀 링크 %d건' % (name, n)
    s = re.sub(r'(href="assets/xlsx/)투자수익현황_[^"]+(" download)', r'\g<1>%s\g<2>' % xls_status, s)
    s = put_title(s, name)

    io.open(p, 'w', encoding='utf-8').write(s)
    print('%-34s 프리셋 %-12s %s ~ %s · %-7s · %s + %s%s'
          % (name, '·'.join(l + ('*' if o else '') for l, o in pre), frm, to, gran, xls, xls_status,
             ' · 달력 유지' if pop else ''))


if __name__ == '__main__':
    for a in PLAN:
        if a[0] == 'invest-profit--weekly.html':
            make_weekly()
        one(*a)
    print('-- 카드 ↔ 표 기간 일치 --')
    for name, _pre, frm, to, gran in PLAN:
        print('  %-34s %s' % (name, assert_period(name, frm, to, gran)))
