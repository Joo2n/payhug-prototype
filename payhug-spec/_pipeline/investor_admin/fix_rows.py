# -*- coding: utf-8 -*-
"""정적 화면에 행 호버·순번 열·건수 자리를 통합본과 같은 규칙으로 맞춘다.

app.html 은 build_app.py 가 만든다. 이 스크립트는 Figma 임포트용 정적 낱장 11개만 손댄다.
  · 정산채권 양수 4종 — 고를 수 있는 행에 pickable, 선택 건수를 카드 아래 왼쪽으로
  · 계약기록 4종 — 머리에 총 건수만, 순번 열 신설, 행에 clickable, 선택 건수를 쪽번호 줄 왼쪽으로
  · 가맹점 3종 — 범위 표기(표시 a–b) 제거

행 호버·포커스와 순번 열 서식은 assets/base.css 한 곳에 있다(정적·통합본 공용).
"""
import io, os, re

ROOT = '/Users/semi/cursor/payhug-investor-admin'
def R(f): return io.open(os.path.join(ROOT, f), encoding='utf-8').read()
def W(f, s): io.open(os.path.join(ROOT, f), 'w', encoding='utf-8').write(s)

log = []
def note(f, what, n): log.append('  %-30s %-24s %d' % (f, what, n))

SIGN_FOOT_OLD = ('.sign-foot { display: flex; flex-direction: column; align-items: center; gap: 10px; '
                 'padding: 20px 24px 24px; border-top: 1px solid var(--gray-100); background: var(--gray-50); }\n'
                 '  .sign-foot .sel-count { font-size: 13px; color: var(--gray-600); }')
SIGN_FOOT_NEW = ('/* 선택 건수는 목록 아래 왼쪽, 서명 버튼은 가운데 — 쪽번호 줄과 같은 3열 격자다.\n'
                 '     원본 어드민의 다중선택 액션 바도 건수를 왼쪽에 둔다(PreSettlementTab.tsx:1214·1264). */\n'
                 '  .sign-foot { display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; '
                 'padding: 20px 24px 24px; border-top: 1px solid var(--gray-100); background: var(--gray-50); }\n'
                 '  .sign-foot .sel-count { justify-self: start; font-size: 13px; color: var(--gray-600); }')

PAGE_CSS = ('  .pagination.with-count { display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; }\n'
            '  .pagination.with-count .pg-count { justify-self: start; font-size: 12px; color: var(--gray-500); }\n'
            '  .pagination.with-count .pg-nums { display: flex; align-items: center; gap: 4px; justify-self: center; }\n'
            '  .pagination.with-count .sel-pill { margin-left: 0; }\n')

# ── 1) 정산채권 양수 4종 ────────────────────────────────────────────────
for f in ['acquisition.html', 'acquisition--confirm.html', 'acquisition--signing.html', 'acquisition--done.html']:
    s = R(f)
    assert SIGN_FOOT_OLD in s, f
    s = s.replace(SIGN_FOOT_OLD, SIGN_FOOT_NEW); note(f, '선택 건수 왼쪽 격자', 1)
    # 서명이 끝난 행(done)은 고를 수 없어 pickable 을 붙이지 않는다.
    s, n = re.subn(r'<div class="sign-row((?: selected)?)" role="checkbox"',
                   lambda m: '<div class="sign-row pickable%s" role="checkbox"' % m.group(1), s)
    assert n, f
    note(f, '행 pickable', n)
    W(f, s)

# ── 2) 계약기록 4종 ─────────────────────────────────────────────────────
PAGE_RE = re.compile(r'( *)<div class="pagination" style="border-top:1px solid var\(--gray-100\)">\n'
                     r'(.*?)\n\1</div>', re.S)
for f in ['contracts.html', 'contracts--all.html', 'contracts--downloaded.html', 'contracts--empty.html']:
    s = R(f)
    # 선택 건수 — 자리를 옮기기 전에 표기 값을 떠 둔다
    m = (re.search(r'선택 <b class="mono">(\d+)</b>건', s) or re.search(r'sel-pill">(\d+)건 선택', s))
    pill = m.group(1) if m else None

    # 머리 건수 — 총 N건만 남긴다
    n = 0
    for pat in (r'(총 <b class="mono">\d+</b>건) · 표시 <b class="mono">[0-9]+–[0-9]+</b> · 선택 <b class="mono">\d+</b>건',
                r'(총 <b class="mono">\d+</b>건) · 표시 <b class="mono">[0-9]+–[0-9]+</b>',
                r'(총 <b class="mono">\d+</b>건) · 선택 <b class="mono">\d+</b>건'):
        s, k = re.subn(pat, r'\1', s); n += k
    assert n == 1, (f, n)
    note(f, '머리 = 총 건수만', n)
    s, k = re.subn(r'\n *<span class="badge badge-green sel-pill">\d+건 선택</span>', '', s)
    if k: note(f, '선택 뱃지 머리에서 뗌', k)

    if '<tbody>' in s:
        # 순번 열 — 머리와 값
        s, k = re.subn(r'(<th style="width:48px"><input type="checkbox" class="chk"[^>]*></th>)',
                       r'\1\n              <th class="no">No</th>', s)
        assert k == 1, (f, k)
        cnt = [0]
        def numcell(mm):
            cnt[0] += 1
            return mm.group(0) + '\n              <td class="no">%d</td>' % cnt[0]
        s, k = re.subn(r'<td><input type="checkbox" class="chk"[^>]*></td>', numcell, s)
        note(f, '순번 열 1..%d' % k, k)
        # 행에 clickable — 누를 수 있다는 표시
        s, a = re.subn(r'<tr class="selected">',
                       '<tr class="clickable selected" role="checkbox" tabindex="0" aria-checked="true">', s)
        s, b = re.subn(r'<tr>\n( +)<td><input type="checkbox" class="chk">',
                       lambda mm: ('<tr class="clickable" role="checkbox" tabindex="0" aria-checked="false">\n'
                                   + mm.group(1) + '<td><input type="checkbox" class="chk">'), s)
        note(f, '행 clickable', a + b)
        # 쪽번호 줄 — 왼쪽 선택 건수 · 가운데 쪽번호
        def pagebar(mm):
            ind, body = mm.group(1), mm.group(2)
            body = '\n'.join(('  ' + l) if l.strip() else l for l in body.split('\n'))
            left = ('<span class="badge badge-green sel-pill">%s건 선택</span>' % pill) if pill else ''
            return (ind + '<div class="pagination with-count" style="border-top:1px solid var(--gray-100)">\n'
                    + ind + '  <span class="pg-count">' + left + '</span>\n'
                    + ind + '  <div class="pg-nums">\n' + body + '\n'
                    + ind + '  </div>\n'
                    + ind + '  <span></span>\n'
                    + ind + '</div>')
        s, k = PAGE_RE.subn(pagebar, s)
        assert k == 1, (f, k)
        note(f, '쪽번호 줄 3열', k)
        assert '.pagination.with-count' not in s
        s = s.replace('</style>', PAGE_CSS + '</style>', 1)
    W(f, s)

# ── 3) 가맹점 3종 — 범위 표기 제거 ───────────────────────────────────────
for f in ['merchants.html', 'merchants--filtered.html', 'merchants--empty.html']:
    s = R(f)
    s, k = re.subn(r'(총 <b class="mono">\d+</b>건) · 표시 <b class="mono">[0-9]+–[0-9]+</b>', r'\1', s)
    note(f, '범위 표기 제거', k)
    W(f, s)

print('정적 화면 반영')
print('\n'.join(log))
