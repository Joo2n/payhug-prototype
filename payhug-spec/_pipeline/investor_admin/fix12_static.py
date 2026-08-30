# -*- coding: utf-8 -*-
"""정적 화면 34종 정정 — 배포본 지적 12건을 통합본과 같은 기준으로 반영.

app.html 은 build_app.py 가 만든다. 이 스크립트는 그 재료가 되는
invest-assets.html · coocon.html · login.html 을 포함해 정적 화면만 손댄다.
따라서 이 스크립트를 먼저 돌리고 build_app.py 를 돌린다.

SHOW_FORMULA = False 로 두고 돌리면 정적 화면 9종에서도 수익 산정 기준 카드가 빠진다.
"""
import io, os, re, sys

ROOT = '/Users/semi/cursor/payhug-investor-admin'
SHOW_FORMULA = True

SCREENS = [
    'acquisition.html', 'acquisition--confirm.html', 'acquisition--signing.html', 'acquisition--done.html',
    'certificate.html', 'contracts.html', 'contracts--all.html', 'contracts--downloaded.html', 'contracts--empty.html',
    'coocon.html', 'coocon--confirm.html',
    'invest-assets.html', 'invest-assets--page2.html', 'invest-assets--download.html',
    'invest-assets--cert-confirm.html', 'invest-assets--empty.html',
    'invest-profit.html', 'invest-profit--monthly.html', 'invest-profit--empty.html',
    'login.html', 'merchants.html', 'merchants--filtered.html', 'merchants--empty.html',
    'password.html', 'password--weak.html', 'password--error.html', 'password--done.html',
    'xls-assets-status.html', 'xls-assets-merchant.html', 'xls-profit-status.html', 'xls-profit-daily.html',
]

log = []
def note(f, tag, n):
    if n:
        log.append('%-32s %-30s %d' % (f, tag, n))

# ── 전 화면 공통: 줄 단위로 지우는 것 ────────────────────────────
LINE_KILL = [
    ('page-sub',        re.compile(r'^[ \t]*<p class="page-sub">.*?</p>[ \t]*\n', re.M)),
    ('tbl-foot-note',   re.compile(r'^[ \t]*<div class="tbl-foot-note">.*?</div>[ \t]*\n', re.M)),
    ('tbl-note',        re.compile(r'^[ \t]*<p class="tbl-note">.*?</p>[ \t]*\n', re.M)),
    ('sheet-caption',   re.compile(r'^[ \t]*<p class="sheet-caption">.*?</p>[ \t]*\n', re.M)),
    ('empty-desc',      re.compile(r'^[ \t]*<p class="empty-desc">.*?</p>[ \t]*\n', re.M)),
    ('es-sub',          re.compile(r'^[ \t]*<p class="es-sub">.*?</p>[ \t]*\n', re.M)),
    ('login-links',     re.compile(r'^[ \t]*<div class="login-links">.*?</div>[ \t]*\n', re.M)),
    ('c-note/산식',      re.compile(r'^[ \t]*<p class="c-note">※ (?!예시값).*?</p>[ \t]*\n', re.M)),
    ('css/tbl-note',    re.compile(r'^[ \t]*\.tbl-note \{.*?\}[ \t]*\n', re.M)),
    ('css/tbl-foot',    re.compile(r'^[ \t]*\.tbl-foot-note \{[^}]*\}[ \t]*\n', re.M | re.S)),
]

# ── 전 화면 공통: 문자열 치환 ────────────────────────────────────
SWAP = [
    # 12 — 합계 행 가중평균은 괄호를 떼고 숫자 아래 줄로
    ('<span class="avg-note">(가중평균)</span>', '<span class="avg-sub">가중평균</span>'),
    ('<span class="avg-note">(평균)</span>',     '<span class="avg-sub">가중평균</span>'),
    ('.tbl tfoot td .avg-note { font-size: 11px; font-weight: 400; color: var(--gray-400); margin-left: 4px; font-family: var(--font-sans); }',
     '.avg-sub { display: block; font-size: 10px; line-height: 12px; font-weight: 400; color: var(--gray-400); font-family: var(--font-sans); }'),
    ('.tbl tbody td .avg-note { font-size: 11px; font-weight: 400; color: var(--gray-400); margin-left: 4px; font-family: var(--font-sans); }', ''),
    # 1 — '확인 대상' 꼬리 문장
    ('표기 금액·상호·서명값은 전부 예시이며 실제 발급 기록이 아니다. 전자문서에 ㈜페이허그 인증서 서명값을 표시함. 인증서 발행기관 검증 회신전문은 형식·전달 경로 미정의 — 확인 대상.',
     '※ 예시값 — 표기 금액·상호·서명값은 전부 예시이며 실제 발급 기록이 아니다.'),
    ('기준일 2026-08-27 시점의 가맹점별 투자자산 내역으로 전자문서를 발급함. 발급 문서에 ㈜페이허그 인증서 서명값을 표시함. 인증서 발행기관 검증 회신전문은 확인 대상.',
     '기준일 2026-08-27 시점의 가맹점별 투자자산 내역으로 전자문서를 발급합니다.'),
    ('선택한 <b>2건</b>의 계약서에 전자서명함. 서명 수단은 확인 대상. 서명 후 취소 불가.',
     '선택한 <b>2건</b>의 계약서에 전자서명합니다. 서명 후에는 취소할 수 없습니다.'),
    ('<span class="step-note">전자서명 진행 중. 서명 수단 확인 대상.</span>',
     '<span class="step-note">전자서명 진행 중.</span>'),
    ('정산금채권 양수도 계약 <b class="mono">2건</b> 서명 완료.<br>서명값은 계약기록에 보관됨. 인증서 발행기관 검증 회신전문의 형식·보관 경로는 확인 대상.',
     '정산금채권 양수도 계약 <b class="mono">2건</b> 서명 완료.<br>서명값은 계약기록에 보관됩니다.'),
    ('<p class="done-desc">새 비밀번호로 변경 완료. 기존 세션 처리는 확인 대상.</p>',
     '<p class="done-desc">새 비밀번호로 변경 완료.</p>'),
    ('재양도합의서 16건 묶음. 서명 검증 회신전문 미포함 — 형식·전달 경로 확인 대상.',
     '재양도합의서 16건 묶음.'),
    # 7 — 프리셋 라벨
    ('<button class="preset-btn active">이번달</button>', '<button class="preset-btn">금월</button>'),
    ('<button class="preset-btn">이번달</button>',        '<button class="preset-btn">금월</button>'),
    # 5 — 페이지네이션 가운데 정렬 + 건수 왼쪽
    ('<div class="pagination" style="justify-content:space-between">', '<div class="pagination with-count">'),
]

PW_NOTE = re.compile(r'^[ \t]*<p class="pw-note">.*?</p>[ \t]*\n', re.M)

# ── CSS 보강 — 새 클래스는 각 화면의 인라인 <style> 에 넣는다 ─────
CSS_ADD = {
    'pagination': '''  .pagination.with-count { display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; }
  .pagination.with-count .pg-count { justify-self: start; font-size: 12px; color: var(--gray-500); }
  .pagination.with-count .pg-nums { display: flex; align-items: center; gap: 4px; justify-self: center; }
''',
    'avg': '''  .avg-sub { display: block; font-size: 10px; line-height: 12px; font-weight: 400; color: var(--gray-400); font-family: var(--font-sans); }
''',
    'sign': '''  .sign-foot { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 20px 24px 24px; border-top: 1px solid var(--gray-100); background: var(--gray-50); }
  .sign-foot .sel-count { font-size: 13px; color: var(--gray-600); }
  .sign-foot .sel-count b { color: var(--gray-900); }
  .sign-foot .btn { min-width: 240px; justify-content: center; padding: 12px 40px; font-size: 16px; border-radius: 12px; }
  .list-tools { display: flex; align-items: center; gap: 8px; }
  .tbl-head-bar { display: flex; align-items: center; justify-content: space-between; padding: 16px 24px; border-bottom: 1px solid var(--gray-100); }
''',
    'link': '''  .link-check { width: 100%; margin-top: 24px; padding-top: 20px; border-top: 1px solid var(--gray-100); text-align: left; }
  .link-check .card-title { display: block; margin: 0 0 12px; }
''',
}

def add_css(s, key):
    block = CSS_ADD[key]
    first = block.strip().split('\n')[0].split('{')[0].strip()
    if first in s:
        return s, 0
    return s.replace('</style>', block + '</style>', 1), 1


# ══════════════════════════════════════════════════════════════════
def run():
    for f in SCREENS:
        p = os.path.join(ROOT, f)
        s0 = io.open(p, encoding='utf-8').read()
        s = s0

        for tag, rx in LINE_KILL:
            s, n = rx.subn('', s)
            note(f, tag, n)

        # pw-note 는 password 화면에만 — 문구 자체가 '확인 대상' 각주다
        s, n = PW_NOTE.subn('', s); note(f, 'pw-note', n)

        for a, b in SWAP:
            if a in s:
                note(f, 'swap:' + a[:22], s.count(a))
                s = s.replace(a, b)

        if 'avg-sub' in s:
            s, n = add_css(s, 'avg'); note(f, 'css/avg-sub', n)
        if 'pagination with-count' in s:
            s, n = add_css(s, 'pagination'); note(f, 'css/pagination', n)

        # ── 7 조회 필터 — 날짜 → 프리셋 → 검색·초기화 한 줄, 아래 일별·월별
        if f.startswith('invest-profit'):
            s, n = re.subn(
                r'[ \t]*<div class="preset-row">\n(?:[ \t]*<button class="preset-btn[^\n]*\n)+[ \t]*</div>\n',
                '', s, count=1)
            note(f, '프리셋 행 분리 제거', n)
            # 어제 프리셋은 스토리보드 슬라이드7 에 없다 — 통째로 뺀다
            s, n = re.subn(r'[ \t]*<button class="preset-btn[^>]*>어제</button>\n', '', s)
            note(f, '어제 프리셋 제거', n)
            s, n = re.subn(
                r'[ \t]*(<button class="btn btn-primary">검색</button>)',
                '        <div class="preset-row">\n'
                '          <button class="preset-btn">일주일</button>\n'
                '          <button class="preset-btn">금월</button>\n'
                '        </div>\n'
                '        \\1', s, count=1)
            note(f, '프리셋 삽입', n)
            # 일별·월별 토글을 표 머리에서 검색 카드 아래로 — 스토리보드 슬라이드7 y3.62
            m = re.search(r'[ \t]*<div class="toggle">\n(?:[ \t]*<button class="toggle-btn[^\n]*\n)+[ \t]*</div>\n', s)
            if m:
                tog = m.group(0)
                s = s[:m.start()] + s[m.end():]
                tog = ('      <div class="toggle">\n'
                       + ''.join('        ' + l.strip() + '\n'
                                 for l in tog.strip().split('\n')[1:-1])
                       + '      </div>\n')
                i = s.find('    <div class="search-bar">')
                j = s.find('\n    </div>\n', i) if i >= 0 else -1
                if j > 0:
                    s = s[:j + 1] + tog + s[j + 1:]
                    note(f, '일별·월별 토글 이동', 1)
            # 투자 수익 화면에는 스토리보드 각주(용어 안내)가 없다
            s, n = re.subn(r'\n[ \t]*<!-- 용어 안내 -->\n[ \t]*<div class="terms-note">.*?\n[ \t]*</div>\n',
                           '', s, count=1, flags=re.S)
            note(f, '용어 안내 제거', n)

        # ── 6·11 정산채권 양수 — 목록 도구 · 카드 안 서명 버튼
        if f.startswith('acquisition'):
            s, n = add_css(s, 'sign'); note(f, 'css/sign-foot', n)
            s, n = re.subn(
                r'[ \t]*<div style="padding:16px 24px; border-bottom:1px solid var\(--gray-100\)">\n'
                r'[ \t]*<span class="card-title" style="margin:0">(서명 대기 목록|양수도 계약 목록)</span>\n'
                r'[ \t]*</div>\n',
                '      <div class="tbl-head-bar">\n'
                '        <span class="card-title" style="margin:0">\\1</span>\n'
                '        <div class="list-tools">\n'
                '          <button class="btn btn-ghost">전체 선택</button>\n'
                '          <button class="btn btn-ghost" disabled>선택 해제</button>\n'
                '        </div>\n'
                '      </div>\n', s, count=1)
            note(f, '목록 도구 신설', n)
            m = re.search(r'\n[ \t]*<!-- 하단 고정 액션 영역 -->\n[ \t]*<div class="action-bar">\n'
                          r'([ \t]*<span class="sel-count">.*?</span>\n)'
                          r'([ \t]*<button class="btn btn-primary"[^\n]*\n)'
                          r'[ \t]*</div>\n', s, re.S)
            if m:
                sel = m.group(1).strip()
                btn = re.sub(r' style="[^"]*"', '', m.group(2).strip())
                s = s[:m.start()] + '\n' + s[m.end():]
                foot = ('      <div class="sign-foot">\n'
                        '        ' + sel + '\n'
                        '        ' + btn + '\n'
                        '      </div>\n')
                s, n = re.subn(r'(\n[ \t]*</div>\n\n[ \t]*</main>)', '\n' + foot.rstrip('\n') + r'\1', s, count=1)
                note(f, '서명 버튼 카드 안으로', n)
            s = re.sub(r'[ \t]*\.action-bar \{[^}]*\}\n', '', s)
            s = re.sub(r'[ \t]*\.action-bar \.sel-count[^\n]*\n', '', s)
            # 행 클릭으로도 선택된다는 것을 마크업으로 드러낸다(정적 화면엔 스크립트가 없다)
            s = s.replace('<div class="sign-row">', '<div class="sign-row" role="checkbox" tabindex="0" aria-checked="false">')
            s = s.replace('<div class="sign-row selected">', '<div class="sign-row selected" role="checkbox" tabindex="0" aria-checked="true">')

        # ── 8 계약기록 — 선택 해제 버튼
        if f.startswith('contracts'):
            s, n = add_css(s, 'sign'); note(f, 'css/list-tools', n)
            i = s.find('      <div class="tbl-head-bar">')
            j = s.find('\n      </div>\n', i) if i >= 0 else -1
            blk = s[i:j] if j > 0 else ''
            k = max(blk.rfind('\n        <a class="btn btn-excel'),
                    blk.rfind('\n        <button class="btn btn-excel'))
            if k > 0:
                ctrl = re.sub(r'^(?=.)', '  ', blk[k:], flags=re.M)
                s = (s[:i] + blk[:k]
                     + '\n        <div class="list-tools">'
                     + '\n          <button class="btn btn-ghost" disabled>선택 해제</button>'
                     + ctrl + '\n        </div>' + s[j:])
                note(f, '선택 해제 버튼', 1)

        # ── 9 쿠콘 — 안내 문단 이어 쓰기 · 조회 가능 내역을 같은 카드로
        if f.startswith('coocon'):
            s, n = add_css(s, 'link'); note(f, 'css/link-check', n)
            s, n = re.subn(
                r'[ \t]*<p class="link-desc">\n.*?</p>\n',
                '        <p class="link-desc">\n'
                '          관리 현금의 입금·송금·펌뱅킹 거래 내역은 쿠콘 We-bank 전자금융서비스에서 조회하며, 별도 발급된 사용자 ID·비밀번호·기관코드·OTP로 로그인합니다.\n'
                '          아래 바로가기는 새 창으로 열리고, 계정 발급과 OTP 초기화는 페이허그 담당자가 처리합니다.\n'
                '        </p>\n', s, count=1, flags=re.S)
            note(f, '안내 문단 이어 쓰기', n)
            s, n = re.subn(r'[ \t]*<p class="link-foot">.*?</p>\n', '', s)
            note(f, 'link-foot 흡수', n)
            m = re.search(r'\n[ \t]*<!-- 참고 카드 -->\n[ \t]*<div class="card" style="margin-top:16px">\n'
                          r'[ \t]*<h3 class="card-title">We-bank에서 조회 가능한 내역</h3>\n'
                          r'([ \t]*<div class="ref-list">.*?\n[ \t]*</div>)\n[ \t]*</div>\n', s, re.S)
            if m:
                reflist = m.group(1)
                s = s[:m.start()] + '\n' + s[m.end():]
                block = ('        <div class="link-check">\n'
                         '          <h3 class="card-title">We-bank에서 조회 가능한 내역</h3>\n'
                         + reflist + '\n'
                         '        </div>\n')
                i = s.find('      <div class="card link-card">')
                j = s.find('\n      </div>\n', i) if i >= 0 else -1
                if j > 0:
                    s = s[:j + 1] + block + s[j + 1:]
                    note(f, '조회 가능 내역 카드 합침', 1)

        # ── 4 수익 산정 기준 카드 스위치
        if not SHOW_FORMULA:
            s, n = re.subn(r'\n[ \t]*<!-- (?:수익 )?산식 안내 카드 -->\n.*?\n[ \t]*</div>\n(?=\n)', '\n', s, count=1, flags=re.S)
            s2, n2 = re.subn(r'\n[ \t]*<!-- 수익 산정 기준 -->\n.*?<p class="formula-caption">.*?</p>\n[ \t]*</div>\n', '\n', s, count=1, flags=re.S)
            s = s2; note(f, '수익 산정 기준 카드 내림', n + n2)

        if s != s0:
            io.open(p, 'w', encoding='utf-8').write(s)

    print('\n'.join(log))
    print('-- %d건' % len(log))


if __name__ == '__main__':
    run()
