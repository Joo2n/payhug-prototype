# -*- coding: utf-8 -*-
"""투자 시뮬레이션 정적 낱장 2종 생성 + 낱장 전종 사이드바 8메뉴 동기화.

  invest-sim.html          실행 전 — 기준 변수 · 채권 8행 · 실행 버튼
  invest-sim--result.html  실행 후 — 위에 결과 5블록(투자 요약 · 채권별 산출 · 현황 · 수익 현황 · 일별 투자수익)

값은 build_app.py 의 simBond/simRun 과 같은 산식을 옮겨 계산한다(대표 정의서 [1번]·[2번] 이미지).
사이드바·헤드는 assets/template.html, 시뮬레이션 CSS 는 build_app.py 의 CSS 블록에서 그대로 잘라 쓴다.
"""
import io, os, re, math

REPO = '/Users/semi/cursor/payhug-investor-admin'
HERE = os.path.dirname(os.path.abspath(__file__))

# ── 사이드바 8메뉴 동기화 ─────────────────────────────────────────
TPL = io.open(os.path.join(REPO, 'assets/template.html'), encoding='utf-8').read()
# 스켈레톤은 assets/ 안에 있어 <base href="../"> 로 상대경로 기준을 루트로 되돌린다.
# 루트에 놓이는 화면에는 그 줄이 있으면 안 된다 — 여기서 걷어 낸다.
TPL = re.sub(r'<!-- 이 파일만 assets/.*?-->\n<base href="\.\./">\n', '', TPL, count=1, flags=re.S)
assert '<base' not in TPL
NAV_NEW = re.search(r'( *<a class="nav-item" data-menu="invest-sim".*?</a>\n)', TPL, re.S).group(1)
ANCHOR  = '          <span>투자 수익</span>\n        </a>\n'
SKIP    = {'app.html'}

def sync_sidebars():
    done = []
    for f in sorted(os.listdir(REPO)):
        if not f.endswith('.html') or f in SKIP:
            continue
        p = os.path.join(REPO, f)
        s = io.open(p, encoding='utf-8').read()
        if s.count('class="nav-item"') != 7 or 'data-menu="invest-sim"' in s:
            continue
        assert s.count(ANCHOR) == 1, f
        io.open(p, 'w', encoding='utf-8').write(s.replace(ANCHOR, ANCHOR + NAV_NEW))
        done.append(f)
    return done

# ── 입력 (통합본 SIM 기본값을 그대로 읽는다 — 두 곳에 같은 숫자를 적지 않는다) ──
_SIMSRC = io.open(os.path.join(HERE, 'build_app.py'), encoding='utf-8').read()
_SIMDEF = re.search(r'var SIM_DEFAULT = \{\s*(.*?)\n', _SIMSRC, re.S).group(1)
def _simv(k):
    return float(re.search(k + r':\s*([0-9.]+)', _SIMDEF).group(1))
R_RATE, CASH, UNPAID, OVER = _simv('r'), int(_simv('cash')), _simv('unpaid'), _simv('over')
FROM, TO = '2026-08-21', '2026-08-27'
PLAT = [('card', '카드사', 2), ('bm', '배달의민족', 3), ('cpe', '쿠팡이츠', 5), ('yo', '요기요', 6)]
LABEL = dict((k, l) for k, l, _ in PLAT)
# 채권 8행도 통합본 simSeedRows() 에서 그대로 읽는다 — 두 곳에 같은 행을 적지 않는다.
_SEED = re.search(r'function simSeedRows\(\)\{\s*return \[(.*?)\];', _SIMSRC, re.S).group(1)
ROWS = [(m.group(1), int(m.group(2)), m.group(3), m.group(4)) for m in re.finditer(
    r"\{plat:'(\w+)',\s*amt:(\d+),\s*sd:'([\d-]+)',\s*dd:'([\d-]+)'\}", _SEED)]
assert len(ROWS) == 8, ROWS

# ── 산식 ──────────────────────────────────────────────────────────
import datetime
def _d(s): return datetime.date(int(s[:4]), int(s[5:7]), int(s[8:10]))
def days(a, b): return (_d(b) - _d(a)).days
def flr(x): return int(math.floor(round(x, 6)))
def fmt(n): return '{:,}'.format(int(n))
def fx(v, d): return ('%.' + str(d) + 'f') % v
def pct(v, d): return fx(v, d) + '%'

def ratios(vals, base):
    out, tot, k = [], 0.0, 0
    for i, v in enumerate(vals):
        out.append(math.floor(v / base * 1000 + 0.5) / 10 if base else 0)
        tot += out[i]
        if v > vals[k]: k = i
    if vals: out[k] = math.floor((out[k] + (100 - tot)) * 10 + 0.5) / 10
    return out

def bond(plat, amt, sd, dd, r, ded):
    return {'plat': plat, 'amt': amt, 'sd': sd, 'dd': dd, 'D': days(sd, dd),
            'A': flr(amt * (1 - r)), 'fee': flr(amt * r), 'ded': flr(max(0, ded) * amt),
            'M': flr(amt * r) - flr(max(0, ded) * amt), 'B': amt - flr(max(0, ded) * amt)}

def run():
    r, ded = R_RATE / 100.0, (UNPAID - OVER) / 100.0
    bonds = [bond(p, a, s, d, r, ded) for p, a, s, d in ROWS]
    out, mat = [], []
    for b in bonds:
        if b['dd'] > TO:      b['kind'] = '미회수'; out.append(b)
        elif b['dd'] >= FROM: b['kind'] = '만기';   mat.append(b)
        else:                 b['kind'] = '기간 밖'
    EXEC = sum(b['A'] for b in out)
    W    = (sum(b['A'] * b['D'] for b in out) / float(EXEC)) if EXEC else 0
    TY   = (R_RATE * 365 / W) if W else 0
    S    = (UNPAID - OVER) / (1 - r)
    TOT  = EXEC + CASH
    SH   = ratios([EXEC, CASH], TOT)
    PSA  = sum(b['A'] for b in mat); PSM = sum(b['M'] for b in mat); PSB = sum(b['B'] for b in mat)
    PSD  = (sum(b['A'] * b['D'] for b in mat) / float(PSA)) if PSA else 0
    PSMR = (PSM / float(PSA) * 100) if PSA else 0
    TY4  = (PSMR * 365 / PSD) if PSD else 0
    ECD  = days(FROM, TO) + 1
    PSC  = CASH * ECD
    TY5  = (TY4 * PSA / float(PSA + PSC)) if (PSA + PSC) else 0
    day, keys = {}, []
    for b in mat:
        g = day.get(b['dd'])
        if not g:
            g = day[b['dd']] = {'d': b['dd'], 'A': 0, 'M': 0, 'B': 0, 'wx': 0}
            keys.append(b['dd'])
        g['A'] += b['A']; g['M'] += b['M']; g['B'] += b['B']; g['wx'] += b['A'] * b['D']
    keys.sort()
    drows = []
    for k in keys:
        g = day[k]
        g['W'] = (g['wx'] / float(g['A'])) if g['A'] else 0
        g['TY'] = ((g['M'] / float(g['A']) * 100) * 365 / g['W']) if (g['A'] and g['W']) else 0
        drows.append(g)
    return dict(bonds=bonds, EXEC=EXEC, W=W, TY=TY, S=S, TOT=TOT, SH=SH, PSA=PSA, PSM=PSM,
                PSB=PSB, PSD=PSD, PSMR=PSMR, TY4=TY4, TY5=TY5, ECD=ECD, PSC=PSC, rows=drows)

# ── 마크업 ────────────────────────────────────────────────────────
def field(fid, label, kind, value, extra=''):
    return ('        <div class="filter-field">\n'
            '          <label for="%s">%s</label>\n'
            '          <input type="%s" id="%s" class="input"%s value="%s">\n'
            '        </div>\n' % (fid, label, kind, fid, extra, value))

def vars_block():
    h  = '    <div class="card mb-6">\n      <div class="card-head">\n        <h2 class="card-title">기준 변수</h2>\n      </div>\n'
    h += '      <div class="sim-grid">\n'
    h += field('sim-r', '할인율 (%)', 'number', R_RATE, ' step="0.01" min="0.01" max="5"')
    h += field('sim-cash', '순현금 (원)', 'number', CASH, ' step="100000" min="0"')
    h += field('sim-unpaid', '미지급률 (%)', 'number', UNPAID, ' step="0.01" min="0" max="100"')
    h += field('sim-over', '과지급률 (%)', 'number', OVER, ' step="0.01" min="0" max="100"')
    h += field('sim-from', '시작일', 'date', FROM)
    h += field('sim-to', '종료일', 'date', TO)
    h += '      </div>\n'
    # 기간 역전 안내 — 통합본과 같은 자리·같은 원문(payhug-admin-web/components/DateRangeFilter.tsx:14)
    h += ('      <p class="range-warn" hidden>'
          '시작일은 종료일보다 이후일 수 없습니다.</p>\n')
    h += '    </div>\n\n'
    return h

def rows_block(bonds):
    h  = '    <div class="card mb-6">\n      <div class="card-head">\n'
    h += '        <h2 class="card-title">정산금채권 입력</h2>\n'
    h += '        <button class="btn btn-primary">+ 채권 추가</button>\n      </div>\n'
    h += ('      <div class="sim-head">\n'
          '        <span class="sim-no"></span><span class="sim-plat">플랫폼</span>\n'
          '        <span class="sim-amt">순지급액</span><span class="sim-unit"></span>\n'
          '        <span class="sim-date">선정산일</span><span class="sim-date">정산예정일</span>\n'
          '        <span class="sim-days">금융일수</span>\n'
          '      </div>\n')
    h += '      <div class="sim-rows">\n'
    for i, b in enumerate(bonds):
        opts = ''.join('<option value="%s"%s>%s</option>' % (k, ' selected' if k == b['plat'] else '', l)
                       for k, l, _ in PLAT)
        h += ('        <div class="sim-row">\n'
              '          <span class="sim-no">%d</span>\n'
              '          <select class="input sim-plat" aria-label="플랫폼">%s</select>\n'
              '          <input type="number" class="input sim-amt" step="1000000" min="0" value="%d" aria-label="순지급액">\n'
              '          <span class="sim-unit">원</span>\n'
              '          <input type="date" class="input sim-date" value="%s" aria-label="선정산일">\n'
              '          <input type="date" class="input sim-date" value="%s" aria-label="정산예정일">\n'
              '          <span class="sim-days">%d일</span>\n'
              '          <button type="button" class="sim-del">삭제</button>\n'
              '        </div>\n' % (i + 1, opts, b['amt'], b['sd'], b['dd'], b['D']))
    h += '      </div>\n'
    h += '      <div class="sim-total">총 %d건, 합계 %s원</div>\n' % (len(bonds), fmt(sum(b['amt'] for b in bonds)))
    h += '    </div>\n\n'
    return h

def result_block(R):
    h  = '    <div class="summary-grid">\n'
    h += ('      <div class="summary-card highlight">\n        <div class="summary-label">투자자산</div>\n'
          '        <div class="summary-value">%s<span class="unit">원</span></div>\n'
          '        <div class="summary-sub">투자실행액 + 순현금</div>\n      </div>\n' % fmt(R['TOT']))
    h += ('      <div class="summary-card">\n        <div class="summary-label">투자실행액</div>\n'
          '        <div class="summary-value">%s<span class="unit">원</span></div>\n'
          '        <div class="summary-sub">비중 %s%% · 보관 ㈜페이허그</div>\n      </div>\n'
          % (fmt(R['EXEC']), fx(R['SH'][0], 1)))
    h += ('      <div class="summary-card">\n        <div class="summary-label">순현금</div>\n'
          '        <div class="summary-value">%s<span class="unit">원</span></div>\n'
          '        <div class="summary-sub">비중 %s%% · 보관 ㈜쿠콘</div>\n      </div>\n'
          % (fmt(CASH), fx(R['SH'][1], 1)))
    h += ('      <div class="summary-card">\n        <div class="summary-label">Ty수익율</div>\n'
          '        <div class="summary-value">%s<span class="unit">%%</span></div>\n'
          '        <div class="summary-sub">W금융일수 %s일 기준</div>\n      </div>\n'
          % (fx(R['TY'], 2), fx(R['W'], 2)))
    h += '    </div>\n\n'

    h += ('    <div class="tbl-wrap mb-6">\n      <div class="tbl-head"><h2>채권별 산출</h2></div>\n'
          '      <div class="tbl-scroll">\n        <table class="tbl">\n          <thead>\n'
          '            <tr><th class="num">#</th><th>구분</th><th>플랫폼</th><th class="num">순지급액</th>'
          '<th class="num">금융일수</th><th class="num">투자실행금</th><th class="num">채권매입수수료</th>'
          '<th class="num">미지급 차감</th><th class="num">투자수익</th><th class="num">상환액</th></tr>\n'
          '          </thead>\n          <tbody>\n')
    for i, b in enumerate(R['bonds']):
        cls = ' class="sim-skip"' if b['kind'] == '기간 밖' else ''
        h += ('            <tr%s><td class="num">%d</td><td>%s</td><td>%s</td><td class="num">%s</td>'
              '<td class="num">%d</td><td class="num">%s</td><td class="num">%s</td><td class="num">%s</td>'
              '<td class="num"><span class="strong">%s</span></td><td class="num">%s</td></tr>\n'
              % (cls, i + 1, b['kind'], LABEL[b['plat']], fmt(b['amt']), b['D'],
                 fmt(b['A']), fmt(b['fee']), fmt(b['ded']), fmt(b['M']), fmt(b['B'])))
    h += '          </tbody>\n        </table>\n      </div>\n    </div>\n\n'

    h += ('    <div class="tbl-wrap mb-6">\n      <div class="tbl-head"><h2>현황</h2></div>\n'
          '      <div class="tbl-scroll">\n        <table class="tbl">\n          <thead>\n'
          '            <tr><th>자산 구분</th><th class="num">금액 (원)</th><th class="num">W금융일수</th>'
          '<th class="num">S입금부족율</th><th class="num">Ty수익율</th><th class="num">비중</th><th>보관</th></tr>\n'
          '          </thead>\n          <tbody>\n')
    h += ('            <tr><td><span class="name">투자실행액</span></td><td class="num"><span class="strong">%s</span></td>'
          '<td class="num">%s일</td><td class="num">%s</td><td class="num">%s</td><td class="num">%s%%</td>'
          '<td>㈜페이허그</td></tr>\n'
          % (fmt(R['EXEC']), fx(R['W'], 2), pct(R['S'], 2), pct(R['TY'], 2), fx(R['SH'][0], 1)))
    h += ('            <tr><td><span class="name">순현금</span></td><td class="num"><span class="strong">%s</span></td>'
          '<td class="num"><span class="none">-</span></td><td class="num"><span class="none">-</span></td>'
          '<td class="num"><span class="none">-</span></td><td class="num">%s%%</td><td>㈜쿠콘</td></tr>\n'
          % (fmt(CASH), fx(R['SH'][1], 1)))
    h += ('            <tr class="total-row"><td>합계 (투자자산)</td><td class="num">%s</td>'
          '<td class="num"><span class="none">-</span></td><td class="num"><span class="none">-</span></td>'
          '<td class="num"><span class="none">-</span></td><td class="num">%s%%</td>'
          '<td><span class="none">-</span></td></tr>\n'
          % (fmt(R['TOT']), fx(R['SH'][0] + R['SH'][1], 1)))
    h += '          </tbody>\n        </table>\n      </div>\n    </div>\n\n'

    h += ('    <div class="card mb-6">\n      <div class="card-head"><h2 class="card-title">수익 현황</h2></div>\n'
          '      <div class="stat-grid">\n'
          '        <div class="stat">\n          <div class="summary-label">검색대상기간</div>\n'
          '          <div class="stat-period">%d일</div>\n'
          '          <div class="summary-sub mono">%s ~ %s</div>\n        </div>\n'
          '        <div class="stat">\n          <div class="summary-label">투자실행금</div>\n'
          '          <div class="summary-value">%s<span class="unit">원</span></div>\n        </div>\n'
          '        <div class="stat">\n          <div class="summary-label">투자수익</div>\n'
          '          <div class="summary-value">%s<span class="unit">원</span></div>\n        </div>\n'
          % (R['ECD'], FROM, TO, fmt(R['PSA']), fmt(R['PSM'])))
    h += ('        <div class="stat">\n          <div class="summary-label">Ty수익율</div>\n'
          '          <div class="ty-split">\n'
          '            <div>\n              <div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자실행금액 대비</span>'
          '<span class="tip-panel">PSMR × 365 ÷ PSD'
          '<span class="tip-row"><span>PSMR</span><span class="tip-green">투자수익 ÷ 투자실행금</span></span>'
          '<span class="tip-row"><span>PSD</span><span class="tip-green">투자실행금 가중평균 금융일수</span></span>'
          '</span></span></div>\n'
          '              <div class="summary-value">%s<span class="unit">%%</span></div>\n            </div>\n'
          '            <div>\n              <div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자자산 대비</span>'
          '<span class="tip-panel">(투자실행금액 대비 × PSA) ÷ (PSA + PSC)'
          '<span class="tip-row"><span>PSA</span><span class="tip-green">%s원</span></span>'
          '<span class="tip-row"><span>PSC</span><span class="tip-green">%s원</span></span>'
          '<span class="tip-row sum"><span>EC %d일 합</span><span>기간 순현금 합계</span></span>'
          '</span></span></div>\n'
          '              <div class="summary-value">%s<span class="unit">%%</span></div>\n            </div>\n'
          '          </div>\n        </div>\n      </div>\n    </div>\n\n'
          % (fx(R['TY4'], 2), fmt(R['PSA']), fmt(R['PSC']), R['ECD'], fx(R['TY5'], 2)))

    h += ('    <div class="tbl-wrap mb-6">\n'
          '      <div class="tbl-head"><div class="left"><h2 class="card-title">일별 투자수익</h2></div></div>\n'
          '      <div class="tbl-scroll">\n        <table class="tbl">\n          <thead>\n'
          '            <tr><th>정산예정일</th><th class="num">상환액</th><th class="num">투자실행금</th>'
          '<th class="num">투자 수익</th><th class="num">W금융일수</th><th class="num">Ty수익율</th></tr>\n'
          '          </thead>\n          <tbody>\n')
    for g in R['rows']:
        h += ('            <tr><td class="mono">%s</td><td class="num">%s</td><td class="num">%s</td>'
              '<td class="num"><span class="strong">%s</span></td><td class="num">%s</td>'
              '<td class="num">%s</td></tr>\n'
              % (g['d'], fmt(g['B']), fmt(g['A']), fmt(g['M']), fx(g['W'], 2), pct(g['TY'], 2)))
    h += ('          </tbody>\n          <tfoot>\n'
          '            <tr><td>합계</td><td class="num">%s</td><td class="num">%s</td><td class="num">%s</td>'
          '<td class="num">%s<span class="avg-sub">가중평균</span></td>'
          '<td class="num">%s%%<span class="avg-sub">가중평균</span></td></tr>\n'
          '          </tfoot>\n        </table>\n      </div>\n    </div>\n'
          % (fmt(R['PSB']), fmt(R['PSA']), fmt(R['PSM']), fx(R['PSD'], 2), fx(R['TY4'], 2)))
    return h

# ── 화면 전용 보조 스타일 — 시뮬레이션 규격은 build_app.py CSS 블록에서 그대로 잘라 온다 ──
def sim_css():
    src = io.open(os.path.join(HERE, 'build_app.py'), encoding='utf-8').read()
    i = src.index('  /* ── 투자 시뮬레이션 ─')
    j = src.index("'''", i)
    return src[i:j].rstrip() + '\n'

BASE_CSS = """  /* 화면 전용 보조 스타일 — 색상은 base.css 변수만 사용 */
  .card-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 20px; }
  .card-head .card-title { margin: 0; }
  .stat-grid { display: grid; grid-template-columns: 1.1fr 1.15fr 1fr 1.7fr; }
  .stat-grid > .stat { padding: 0 24px; min-width: 0; }
  .stat-grid > .stat:first-child { padding-left: 0; }
  .stat-grid > .stat + .stat { border-left: 1px solid var(--gray-100); }
  .stat .ty-split { display: flex; }
  .stat .ty-split > div + div { border-left: 1px solid var(--gray-100); padding-left: 20px; margin-left: 20px; }
  .stat .ty-label { font-size: 11px; line-height: 15px; color: var(--secondary); margin-bottom: 2px; white-space: nowrap; }
  .stat .stat-period { font-size: 16px; line-height: 28px; font-weight: 700; color: var(--gray-900); }
  .tbl-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 16px 20px; border-bottom: 1px solid var(--gray-100); }
  .tbl-head h2 { font-size: 14px; line-height: 20px; font-weight: 600; color: var(--gray-900); margin: 0; }
  .tbl-head .left { display: flex; align-items: center; gap: 16px; }
  .tbl-head .card-title { margin: 0; }
  .tbl tr.total-row td { background: var(--gray-50); border-top: 1px solid var(--gray-100); font-weight: 700; color: var(--gray-900); }
  .tbl tfoot td { background: var(--gray-50); border-top: 1px solid var(--gray-100); border-bottom: 0; font-weight: 700; color: var(--gray-900); }
  .avg-sub { display: block; font-size: 10px; line-height: 12px; font-weight: 400; color: var(--gray-400); font-family: var(--font-sans); }
  .range-warn { margin: 8px 0 0; font-size: 12px; line-height: 16px; color: var(--red-500); }
"""

def page(title, badge, body):
    head = TPL[:TPL.index('</head>')]
    head = head.replace('PayHug Admin — 화면명', 'PayHug Admin — ' + title)
    head = head.replace('<link rel="stylesheet" href="assets/base.css">',
                        '<link rel="stylesheet" href="assets/base.css">\n<style>\n'
                        + BASE_CSS + sim_css() + '</style>')
    shell = TPL[TPL.index('<body '):TPL.index('  <!-- ═══════════ 콘텐츠 영역 ═══════════ -->')]
    shell = shell.replace('<body data-active="invest-assets">', '<body data-active="invest-sim">')
    shell = shell.replace('<a href="#">', '<a href="index.html">')
    mark = ('<span class="badge badge-primary state-badge">%s</span>' % badge) if badge else ''
    return (head + '</head>\n' + shell
            + '  <!-- ═══════════ 콘텐츠 영역 ═══════════ -->\n  <main class="content">\n'
            + '    <div class="page-header">\n      <h1 class="page-title">투자 시뮬레이션'
            + (' ' + mark if mark else '') + '</h1>\n    </div>\n\n'
            + body + '\n  </main>\n\n</div>\n</body>\n</html>\n')


def main():
    moved = sync_sidebars()
    R = run()
    form = vars_block() + rows_block(R['bonds'])
    btn_off = '    <button class="sim-run">시뮬레이션 실행</button>\n'
    io.open(os.path.join(REPO, 'invest-sim.html'), 'w', encoding='utf-8').write(
        page('투자 시뮬레이션', '', form + btn_off))
    io.open(os.path.join(REPO, 'invest-sim--result.html'), 'w', encoding='utf-8').write(
        page('투자 시뮬레이션 · 실행 결과', '실행 결과', form + btn_off + '\n' + result_block(R)))
    print('사이드바 8메뉴 동기화:', len(moved), '건')
    print('invest-sim.html / invest-sim--result.html 기록')
    print('W %s · Ty %s · 비중합 %s · 상환액=PSA+PSM %s'
          % (fx(R['W'], 2), pct(R['TY'], 2), fx(R['SH'][0] + R['SH'][1], 1),
             R['PSB'] == R['PSA'] + R['PSM']))

if __name__ == '__main__':
    main()
