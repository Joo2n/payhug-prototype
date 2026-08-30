# -*- coding: utf-8 -*-
"""폐기 — 대체: sync_assets_static.py (투자자산 표·건수) · contract_text.py (계약서 원문)

돌리지 마라. 입력 낱장 `contracts--downloaded.html` 이 없어 첫 줄에서 죽고,
살아 있던 자리도 이제 다른 곳이 그린다.
  · 계약기록 건수 `16건 선택`·`다운로드 (16)` 가 파일 안에 손으로 적혀 있다 —
    로스터가 16건이 아니게 되는 순간 화면과 어긋난다.
  · 투자자산 가맹점별 표·페이지네이션은 sync_assets_static 이 열머리로 자리를 잡아 그린다.

2차 지시(N-1~N-8·계약서 원본 교체)를 정적 낱장에 반영한다.

app.html 은 build_app.py, 엑셀 실물은 build_xlsx.py, 계약서 텍스트는 build_sigtext.py 가 만든다.
이 스크립트는 Figma 임포트용 정적 HTML만 손댄다.

  N-8  0.11% 는 관리자 어드민이 넣어 주는 고정 입력값 — 예시값·미확정 고지 전량 삭제
  N-1~3 읽으라고 붙인 설명 전량 삭제 (계약기록 안내 2줄 · 엑셀 시트 주석 · 산식 캡션)
  N-5  페이지네이션이 있는 표에 보기 갯수 10/20/50 · 1쪽 10행
  N-6~7 계약서보기 본문을 계약서 원문(contract_text.py)으로 교체
"""
import io
import os
import re
import sys

PIPE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PIPE)
raise SystemExit('폐기 — 대체: sync_assets_static.py · contract_text.py')

import contract_text as C            # noqa: E402
from roster16_model import ROSTER, SHARES, ty, r1, f  # noqa: E402

ROOT = '/Users/semi/cursor/payhug-investor-admin'
SIZE = 10
log = []


def R(fn):
    return io.open(os.path.join(ROOT, fn), encoding='utf-8').read()


def W(fn, s):
    io.open(os.path.join(ROOT, fn), 'w', encoding='utf-8').write(s)


def note(fn, what, n):
    log.append('  %-30s %-32s %s' % (fn, what, n))


ALL = [fn for fn in sorted(os.listdir(ROOT)) if fn.endswith('.html')]
OWNED = [fn for fn in ALL if re.match(
    r'(merchants|contracts|acquisition|coocon|invest-assets|invest-profit|xls-|certificate|password|login)', fn)]

# ══ N-8 · N-1~N-3 — 읽으라고 붙인 설명 철거 ═══════════════════════════════
NOTICE_BLOCK = re.compile(
    r'\n *<div class="notice notice-(?:amber|green)">\n(?:[^\n]*\n)*? *<span>(?:<b>확인필요</b>|※ 예시값|하나인증서 전자서명)[^\n]*\n *</div>\n')
CNOTE = re.compile(r'<td class="c-note" colspan="(\d+)">[^<]*</td>')

for fn in OWNED:
    s0 = s = R(fn)
    n = 0
    while True:
        s2 = NOTICE_BLOCK.sub('\n', s, count=1)
        if s2 == s:
            break
        s, n = s2, n + 1
    if n:
        note(fn, '안내 블록 삭제', n)

    # 엑셀 미리보기 시트 — 주석 행은 자리만 남기고 비운다(행 좌표 유지)
    def blank(m):
        k = int(m.group(1))
        return ''.join('<td class="c-empty"></td>' for _ in range(k))
    s, k = CNOTE.subn(blank, s)
    if k:
        note(fn, '시트 주석 행 비움', k)

    s, k = re.subn(r'<p class="doc-notice">[^<]*</p>\n *', '', s)
    if k:
        note(fn, 'doc-notice 삭제', k)
    s, k = re.subn(r'<p class="issue-note">[^<]*</p>\n *', '', s)
    if k:
        note(fn, 'issue-note 삭제', k)
    s, k = re.subn(r'<p class="foot-note">[^<]*</p>\n *', '', s)
    if k:
        note(fn, 'foot-note 삭제', k)
    s, k = re.subn(r'<p class="formula-caption">[^<]*</p>\n *', '', s)
    if k:
        note(fn, '산식 캡션 삭제', k)
    s, k = re.subn(r'<h2 class="card-title">수익 산정 기준 \(예시\)</h2>',
                   '<h2 class="card-title">수익 산정 기준</h2>', s)
    if k:
        note(fn, '산식 카드 제목', k)

    # 쓰이지 않게 된 서식
    for cls in ('doc-notice', 'issue-note', 'foot-note', 'formula-caption'):
        if ('class="%s"' % cls) not in s:
            s, k = re.subn(r'\n *\.%s \{[^\n]*\}' % cls, '', s)
    if s != s0:
        W(fn, s)

# 문체 · 다운로드 완료 토스트 문구
for fn in OWNED:
    s = R(fn)
    s0 = s
    s = s.replace('기준일 2026-08-27 시점의 가맹점별 투자자산 내역으로 전자문서를 발급합니다.',
                  '기준일 2026-08-27 시점의 가맹점별 투자자산 내역으로 전자문서 발급.')
    s = s.replace('<p class="t-main">재양도합의서_전체16건_20260827.zip 내려받기 완료</p>',
                  '<p class="t-main">전자서명결과_전체16건_20260827.txt 내려받기 완료</p>')
    s = s.replace('<p class="t-sub">재양도합의서 16건 묶음.</p>',
                  '<p class="t-sub">전자서명 결과 16건 묶음.</p>')
    if s != s0:
        W(fn, s)
        note(fn, '문구 교정', 1)

# ══ N-5 — 1쪽 10행 · 보기 갯수 드롭다운 ══════════════════════════════════
HEADBAR_CSS = ('  .tbl-head-bar { display: flex; align-items: center; justify-content: space-between; '
               'padding: 16px 24px; border-bottom: 1px solid var(--gray-100); }\n'
               '  .list-tools { display: flex; align-items: center; gap: 8px; }\n')
SIZE_CSS = ('  .pg-size { display: inline-flex; align-items: center; gap: 6px; font-size: 12px; color: var(--gray-500); }\n'
            '  .input.sz { padding: 4px 24px 4px 10px; font-size: 12px; height: 28px; border-radius: 8px; }\n')
PAGE_CSS = ('  .pagination.with-count { display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; }\n'
            '  .pagination.with-count .pg-count { justify-self: start; font-size: 12px; color: var(--gray-500); }\n'
            '  .pagination.with-count .pg-nums { display: flex; align-items: center; gap: 4px; justify-self: center; }\n')


def size_sel():
    o = ''.join('<option value="%d"%s>%d개</option>' % (v, ' selected' if v == SIZE else '', v)
                for v in (10, 20, 50))
    return ('<label class="pg-size">보기<select class="input sz" aria-label="보기 갯수">%s</select></label>' % o)


def put_size(s):
    """표 오른쪽 위 도구줄에 보기 갯수를 둔다. 도구줄이 없으면 만든다."""
    if 'class="pg-size"' in s:
        return s
    if '<div class="list-tools">' in s:
        return s.replace('<div class="list-tools">',
                         '<div class="list-tools">\n          ' + size_sel(), 1)
    if '<div class="actions">' in s:
        return s.replace('<div class="actions">',
                         '<div class="actions">\n          ' + size_sel(), 1)
    # 가맹점 목록 — 도구줄이 없어 새로 만든다(통합본과 같은 구성)
    return s.replace('    <div class="tbl-wrap">\n      <div class="tbl-scroll">',
                     '    <div class="tbl-wrap">\n'
                     '      <div class="tbl-head-bar">\n'
                     '        <span class="card-title" style="margin:0">가맹점 목록</span>\n'
                     '        <div class="list-tools">' + size_sel() + '</div>\n'
                     '      </div>\n'
                     '      <div class="tbl-scroll">', 1)


ARROW_L = ('<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" '
           'stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>')
ARROW_R = ('<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" '
           'stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>')


def pagebar(ind, left, page, pages, extra_style=''):
    L = [ind + '<div class="pagination with-count"%s>' % extra_style,
         ind + '  <span class="pg-count">%s</span>' % left,
         ind + '  <div class="pg-nums">',
         ind + '    <button class="page-arrow"%s>' % ('' if page > 1 else ' disabled'),
         ind + '      ' + ARROW_L,
         ind + '    </button>']
    for p in range(1, pages + 1):
        L.append(ind + '    <button class="page-btn%s">%d</button>' % (' active' if p == page else '', p))
    L += [ind + '    <button class="page-arrow"%s>' % ('' if page < pages else ' disabled'),
          ind + '      ' + ARROW_R,
          ind + '    </button>',
          ind + '  </div>',
          ind + '  <span></span>',
          ind + '</div>']
    return '\n'.join(L)


PAGES = 2
def rows_for(page):
    return ROSTER[:SIZE] if page == 1 else ROSTER[SIZE:]


def swap_tbody(s, body, nth=1):
    """nth 번째 <tbody> 안을 갈아 끼운다. 투자 자산 화면은 현황 표가 먼저라 2번째가 가맹점별 표다."""
    i = -1
    for _ in range(nth):
        i = s.index('<tbody>', i + 1)
    i += len('<tbody>')
    j = s.index('</tbody>', i)
    return s[:i] + '\n' + body + '\n          ' + s[j:]


def swap_pagination(s, left, page, ind, extra_style=''):
    m = re.search(r'( *)<div class="pagination(?: with-count)?"[^>]*>\n.*?\n\1</div>', s, re.S)
    assert m, 'pagination 없음'
    return s[:m.start()] + pagebar(m.group(1), left, page, PAGES, extra_style) + s[m.end():]


def ensure_css(s, block):
    if '.pagination.with-count {' not in s:
        s = s.replace('</style>', PAGE_CSS + '</style>', 1)
    if '.pg-size {' not in s:
        s = s.replace('</style>', block + '</style>', 1)
    if '.tbl-head-bar {' not in s and 'class="tbl-head-bar"' in s:
        s = s.replace('</style>', HEADBAR_CSS + '</style>', 1)
    return s


# ── 가맹점 ───────────────────────────────────────────────────────────────
def mc_rows(rows, start):
    out = []
    for i, r in enumerate(rows):
        name, _amt, _w, _s, mid, biz, ceo, sector, item, _sg = r
        out.append(
            '            <tr>\n'
            '              <td class="no">%d</td>\n'
            '              <td class="mono">%s</td>\n'
            '              <td><span class="name">%s</span></td>\n'
            '              <td class="mono">%s</td>\n'
            '              <td>%s</td>\n'
            '              <td>%s</td>\n'
            '              <td>%s</td>\n'
            '              <td><span class="badge sm badge-primary">A-001</span> ㈜페이허그</td>\n'
            '            </tr>' % (start + i, mid, name, biz, ceo, sector, item))
    return '\n'.join(out)


s = R('merchants.html')
s = swap_tbody(s, mc_rows(rows_for(1), 1))
s = swap_pagination(s, '총 <b class="mono">16</b>건', 1, '      ')
s = put_size(s)
s = ensure_css(s, SIZE_CSS)
W('merchants.html', s)
note('merchants.html', '1쪽 %d행 · 보기 갯수' % SIZE, SIZE)

for fn in ('merchants--filtered.html', 'merchants--empty.html'):
    s = R(fn)
    if 'pagination' in s:
        m = re.search(r'( *)<div class="pagination(?: with-count)?"[^>]*>\n.*?\n\1</div>', s, re.S)
        if m and 'pg-size-wrap' not in s:
            left = re.search(r'<span class="pg-count">(.*?)</span>', m.group(0), re.S)
            L = [m.group(1) + '<div class="pagination with-count">',
                 m.group(1) + '  <span class="pg-count">%s</span>' % (left.group(1) if left else ''),
                 m.group(1) + '  <div class="pg-nums">',
                 m.group(1) + '    <button class="page-arrow" disabled>', m.group(1) + '      ' + ARROW_L,
                 m.group(1) + '    </button>',
                 m.group(1) + '    <button class="page-btn active">1</button>',
                 m.group(1) + '    <button class="page-arrow" disabled>', m.group(1) + '      ' + ARROW_R,
                 m.group(1) + '    </button>', m.group(1) + '  </div>',
                 m.group(1) + '  ' + size_sel(), m.group(1) + '</div>']
            s = s[:m.start()] + '\n'.join(L) + s[m.end():]
            s = put_size(s)
            s = ensure_css(s, SIZE_CSS)
            note(fn, '보기 갯수', 1)
    W(fn, s)

# ── 계약기록 ─────────────────────────────────────────────────────────────
SEL_DEFAULT = {'M2026-0001', 'M2026-0004', 'M2026-0006'}


def ct_rows(rows, start, allsel):
    out = []
    for i, r in enumerate(rows):
        name, mid = r[0], r[4]
        on = allsel or mid in SEL_DEFAULT
        out.append(
            '            <tr class="clickable%s" role="checkbox" tabindex="0" aria-checked="%s">\n'
            '              <td><input type="checkbox" class="chk"%s></td>\n'
            '              <td class="no">%d</td>\n'
            '              <td class="mono">%s</td>\n'
            '              <td><span class="name">%s</span></td>\n'
            '              <td><a class="file-link" href="assets/docs/전자서명결과_%s.txt" target="_blank" rel="noopener">전자서명결과_%s.txt</a></td>\n'
            '              <td class="center"><span class="badge badge-green">하나인증서</span></td>\n'
            '            </tr>' % (' selected' if on else '', 'true' if on else 'false',
                                   ' checked' if on else '', start + i, mid, name, mid, mid))
    return '\n'.join(out)


for fn, allsel, pill in (('contracts.html', False, '3건 선택'),
                         ('contracts--all.html', True, '16건 선택'),
                         ('contracts--downloaded.html', True, '16건 선택')):
    s = R(fn)
    s = swap_tbody(s, ct_rows(rows_for(1), 1, allsel))
    s = swap_pagination(s, '<span class="badge badge-green sel-pill">%s</span>' % pill, 1,
                        '      ', ' style="border-top:1px solid var(--gray-100)"')
    s = put_size(s)
    s = ensure_css(s, SIZE_CSS)
    W(fn, s)
    note(fn, '1쪽 %d행 · 보기 갯수' % SIZE, SIZE)

s = R('contracts--empty.html')
s = put_size(s)
s = ensure_css(s, SIZE_CSS)
W('contracts--empty.html', s)

# ── 투자 자산 가맹점별 표 ────────────────────────────────────────────────
def ia_rows(rows, shares):
    out = []
    for r, sh in zip(rows, shares):
        name, amt, w, sv = r[0], r[1], r[2], r[3]
        out.append(
            '            <tr>\n'
            '              <td><span class="name">%s</span></td>\n'
            '              <td class="num"><span class="strong">%s</span></td>\n'
            '              <td class="num">%s일</td>\n'
            '              <td class="num">%s%%</td>\n'
            '              <td class="num">%s%%</td>\n'
            '              <td class="num">%s%%</td>\n'
            '            </tr>' % (name, f(amt), w, sv, ty(w), sh))
    return '\n'.join(out)


IA1 = ia_rows(ROSTER[:SIZE], SHARES[:SIZE])
IA2 = ia_rows(ROSTER[SIZE:], SHARES[SIZE:])
for fn, page in (('invest-assets.html', 1), ('invest-assets--download.html', 1),
                 ('invest-assets--cert-confirm.html', 1), ('invest-assets--page2.html', 2)):
    s = R(fn)
    s = swap_tbody(s, IA1 if page == 1 else IA2, nth=2)
    s = swap_pagination(s, ' ', page, '      ')
    s = put_size(s)
    s = ensure_css(s, SIZE_CSS)
    W(fn, s)
    note(fn, '%d쪽 %d행 · 보기 갯수' % (page, SIZE if page == 1 else 16 - SIZE), SIZE if page == 1 else 16 - SIZE)

# ══ N-6·N-7 — 계약서보기 화면을 계약서 원문으로 ═══════════════════════════
DOC_CSS = """  .modal.lg { max-width: 672px; }
  .doc-view { gap: 12px; }
  .doc-view .doc-meta { margin: 0; font-size: 13px; line-height: 20px; color: var(--gray-500); }
  .doc-scroll { max-height: 52vh; overflow-y: auto; border: 1px solid var(--gray-200); border-radius: 12px; padding: 18px 20px; background: var(--gray-50); }
  .doc-scroll .ct-title { margin: 0 0 12px; font-size: 15px; font-weight: 700; color: var(--gray-900); text-align: center; }
  .doc-scroll .ct-pre { margin: 0 0 16px; }
  .doc-scroll h5 { margin: 16px 0 4px; font-size: 13px; font-weight: 700; color: var(--gray-900); }
  .doc-scroll p { margin: 0 0 4px; font-size: 13px; line-height: 20px; color: var(--gray-700); }
  .doc-scroll .ct-date { margin: 20px 0 16px; text-align: center; }
  .doc-scroll .ct-sign { display: grid; grid-template-columns: 1fr 1fr; gap: 20px 24px; margin-top: 8px; }
  .doc-scroll .ct-party { flex: 1; display: flex; flex-direction: column; gap: 6px; font-size: 12px; color: var(--gray-700); }
  .doc-scroll .ct-party .r { font-weight: 700; color: var(--gray-900); }
  .doc-scroll .ct-party .f { border-bottom: 1px solid var(--gray-300); padding-bottom: 3px; }
  .state-flag {
    display: inline-block; margin-left: 10px; vertical-align: middle;
    padding: 4px 10px; border-radius: 9999px;
    background: var(--gray-100); color: var(--gray-500);
    font-size: 12px; line-height: 16px; font-weight: 500;
  }
"""

DOC_MODAL = """
  <!-- 계약서보기 (열린 상태) -->
  <div class="modal-backdrop">
    <div class="modal lg">
      <div class="modal-header">
        <h3>계약서보기</h3>
        <a class="close" href="acquisition.html"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg></a>
      </div>
      <div class="modal-body doc-view">
        <p class="doc-meta">가맹점ID <span class="mono">M2026-0001</span> · 계약 생성일 <span class="mono">2026-08-25</span>
          <span class="badge badge-amber">서명 대기</span></p>
        <div class="doc-scroll">
          {CONTRACT}
        </div>
      </div>
      <div class="modal-footer">
        <a class="btn btn-outline" href="acquisition.html">닫기</a>
        <a class="btn btn-primary" href="assets/docs/정산금채권_재양도_합의서.txt" target="_blank" rel="noopener">계약서 원문 열기</a>
      </div>
    </div>
  </div>
""".replace('{CONTRACT}', C.as_html('          '))

doc = R('acquisition.html')
doc = doc.replace('<title>PayHug Admin — 정산채권 양수</title>',
                  '<title>PayHug Admin — 정산채권 양수 · 계약서보기</title>', 1)
doc = doc.replace('<h1 class="page-title">정산채권 양수</h1>',
                  '<h1 class="page-title">정산채권 양수 <span class="state-flag">계약서보기</span></h1>', 1)
doc = doc.replace('</style>', DOC_CSS + '</style>', 1)
doc = doc.replace('\n</div>\n</body>', '\n' + DOC_MODAL.rstrip('\n') + '\n\n</div>\n</body>', 1)
assert "ct-title" in doc and "제7조" in doc
W('acquisition--doc.html', doc)
note('acquisition--doc.html', '계약서 원문으로 재작성', 1)


# ══ 정산채권 양수 — 통합본과 같은 안내 문구·서명 완료 목록 ══════════════════
NOTE_OLD = '서명 대기 중인 정산금채권 양수도 계약 <b class="mono">3건</b>. 계약서 내용 확인 후 서명 진행.'
for fn in ('acquisition.html', 'acquisition--doc.html', 'acquisition--confirm.html'):
    s = R(fn)
    if NOTE_OLD in s:
        s = s.replace(NOTE_OLD, '서명 대기 <b class="mono">3건</b>.', 1)
        W(fn, s)
        note(fn, '안내 = 건수만', 1)

s = R('acquisition--signing.html')
a = '서명 대기 중인 정산금채권 양수도 계약 <b class="mono">3건</b>. 선택 <b class="mono">2건</b> 서명 처리 중.'
if a in s:
    s = s.replace(a, '서명 대기 <b class="mono">3건</b> · 선택 <b class="mono">2건</b> 서명 처리 중.', 1)
    W('acquisition--signing.html', s)
    note('acquisition--signing.html', '안내 = 건수만', 1)

# 서명 완료 화면 — 서명한 행은 목록에서 빠진다(통합본과 같은 규칙).
# 목록·사이드바·서식이 어긋나지 않게 acquisition.html 을 바탕으로 다시 만든다.
DONE_MODAL = """
  <!-- 서명 완료 모달 -->
  <div class="modal-backdrop">
    <div class="modal md">
      <div class="modal-body" style="padding-top:32px">
        <div class="done-head">
          <div class="done-icon">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg>
          </div>
          <h3 class="done-title">서명 완료</h3>
          <p class="done-desc">정산금채권 양수도 계약 <b class="mono">2건</b> 서명 완료.<br>서명값은 계약기록에 보관.</p>
        </div>

        <div class="done-list">
          <div class="done-item">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
            <span class="n">김성호떡볶이 본점</span>
            <span class="d mono">2026-08-25</span>
          </div>
          <div class="done-item">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
            <span class="n">달빛곱창 홍대점</span>
            <span class="d mono">2026-08-26</span>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <a class="btn btn-outline" href="contracts.html">계약기록 보기</a>
        <a class="btn btn-primary" href="acquisition.html">확인</a>
      </div>
    </div>
  </div>
"""
DONE_CSS = """  .state-flag {
    display: inline-block; margin-left: 10px; vertical-align: middle;
    padding: 4px 10px; border-radius: 9999px;
    background: var(--gray-100); color: var(--gray-500);
    font-size: 12px; line-height: 16px; font-weight: 500;
  }
  .done-head { text-align: center; }
  .done-icon {
    width: 56px; height: 56px; border-radius: 50%; margin: 0 auto 16px;
    background: var(--primary-50); color: var(--primary-600);
    display: flex; align-items: center; justify-content: center;
  }
  .done-icon svg { width: 28px; height: 28px; }
  .done-title { font-size: 18px; line-height: 28px; font-weight: 700; color: var(--gray-900); margin: 0 0 6px; }
  .done-desc { font-size: 14px; line-height: 20px; color: var(--gray-500); margin: 0; }
  .done-list { display: flex; flex-direction: column; gap: 8px; margin-top: 20px; }
  .done-item {
    display: flex; align-items: center; gap: 10px;
    background: var(--primary-50); border-radius: 10px; padding: 10px 14px;
  }
  .done-item svg { width: 16px; height: 16px; color: var(--primary-600); flex-shrink: 0; }
  .done-item .n { flex: 1; font-size: 14px; font-weight: 600; color: var(--gray-900); }
  .done-item .d { font-size: 12px; color: var(--gray-400); }
"""

done = R('acquisition.html')
done = done.replace('<title>PayHug Admin — 정산채권 양수</title>',
                    '<title>PayHug Admin — 정산채권 양수 · 서명 완료</title>', 1)
done = done.replace('<h1 class="page-title">정산채권 양수</h1>',
                    '<h1 class="page-title">정산채권 양수 <span class="state-flag">서명 완료</span></h1>', 1)
done = done.replace('서명 대기 <b class="mono">3건</b>.',
                    '서명 완료 <b class="mono">2건</b> · 서명 대기 <b class="mono">1건</b>.', 1)
# 서명이 끝난 두 행 제거 — 남는 건 바다마루 횟집 한 줄
for nm in ('김성호떡볶이 본점', '달빛곱창 홍대점'):
    m = re.search(r'\n( *)<div class="sign-row[^"]*"[^>]*>\n.*?' + nm + r'.*?\n\1</div>\n', done, re.S)
    assert m, nm
    done = done[:m.start()] + '\n' + done[m.end():]
done = done.replace('</style>', DONE_CSS + '</style>', 1)
done = done.replace('\n</div>\n</body>', '\n' + DONE_MODAL.rstrip('\n') + '\n\n</div>\n</body>', 1)
assert done.count('class="sign-row') == 1 and '계약서보기' in done
W('acquisition--done.html', done)
note('acquisition--done.html', '서명 완료 = 남은 1건만', 1)

print('정적 낱장 2차 반영')
print('\n'.join(log))
