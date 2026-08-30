# -*- coding: utf-8 -*-
"""대표 미팅 2026-08-28 §1 화면 결정(M-1~M-4)을 정적 낱장에 반영한다.

app.html 은 build_app.py 가 만든다. 이 스크립트는 Figma 임포트용 정적 낱장만 손댄다.
쿠콘 2종은 본문 자체가 바뀌어 별도로 처리했다(coocon.html · coocon--confirm.html).

  M-1 정산채권 양수 4종 + 신규 1종
      · `계약서 보기` → `계약서보기`, 여는 자리는 계약서 내용 화면(acquisition--doc.html)
      · 서명하기와 별개 액션. 서명 완료 행에도 같은 액션이 붙는다
  M-2 계약기록 4종
      · 내려받는 것은 전자서명 결과(텍스트). PDF 이미지가 아니다
      · 하나인증서 전자서명이라 페이허그가 서명값을 바꿀 수 없다는 것을 화면에 남긴다
      · 확인필요 2건은 한 줄로만 표기(상세는 meeting_20260828.md)
  M-3 가맹점 3종 — 표 왼쪽 No 열

실물 파일은 build_sigtext.py 가 만든다(전자서명결과_*.txt).
"""
import io
import os
import re

ROOT = '/Users/semi/cursor/payhug-investor-admin'
SIG = '전자서명결과_%s.txt'
SIG_SEL3 = '전자서명결과_선택3건_20260827.txt'
SIG_ALL = '전자서명결과_전체16건_20260827.txt'

MERCH = ['merchants.html', 'merchants--filtered.html', 'merchants--empty.html']
CONTRACTS = ['contracts.html', 'contracts--all.html', 'contracts--downloaded.html', 'contracts--empty.html']
ACQ = ['acquisition.html', 'acquisition--confirm.html', 'acquisition--signing.html', 'acquisition--done.html']

log = []


def R(f):
    return io.open(os.path.join(ROOT, f), encoding='utf-8').read()


def W(f, s):
    io.open(os.path.join(ROOT, f), 'w', encoding='utf-8').write(s)


def note(f, what, n):
    log.append('  %-28s %-30s %s' % (f, what, n))


# ══ M-3 가맹점 — 표 왼쪽 No 열 ═══════════════════════════════════════════
for f in MERCH:
    s = R(f)
    if '<th class="no">No</th>' not in s:
        s, k = re.subn(r'(<thead>\s*<tr>\s*)(<th>가맹점ID</th>)',
                       r'\1<th class="no">No</th>\n              \2', s)
        assert k == 1, f
        note(f, '머리 No 열', k)
        cnt = [0]

        def numcell(m):
            cnt[0] += 1
            return m.group(0) + '\n              <td class="no">%d</td>' % cnt[0]

        s, k = re.subn(r'<tr>\n +<td class="mono">M2026-\d{4}</td>', numcell, s)
        note(f, '순번 값 1..%d' % k, k)
        # 결과 없음 화면의 colspan
        s, k2 = re.subn(r'colspan="7"', 'colspan="8"', s)
        if k2:
            note(f, 'colspan 7→8', k2)
    W(f, s)

# 순번 열은 검색 결과 화면에서도 1부터 다시 센다 — 쪽이 아니라 표시 행의 순서다.
s = R('merchants--filtered.html')
assert s.count('<td class="no">') == s.count('<td class="mono">M2026-'), 'filtered 순번 수 불일치'

# ══ M-2 계약기록 — 전자서명 결과 ══════════════════════════════════════════
NOTICE = """
    <div class="notice notice-green">
      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
      <span>하나인증서 전자서명. 서명값은 인증서 발행기관의 검증 대상이라 페이허그가 바꿔 넣을 수 없다.</span>
    </div>
    <div class="notice notice-amber">
      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01M5 19h14a2 2 0 001.84-2.75L13.74 4a2 2 0 00-3.5 0l-7.1 12.25A2 2 0 004.99 19z"/></svg>
      <span><b>확인필요</b> — 이미지 서명과 전자서명 텍스트의 구분 · 내려받기 파일 형식</span>
    </div>
"""
NOTICE_CSS = ('  .notice-green { background: var(--primary-50); border-color: var(--primary-200); '
              'color: var(--primary-700); }\n')

for f in CONTRACTS:
    s = R(f)
    # 표 머리 — 문서 열과 서명 수단 열
    s, k = re.subn(r'<th>재양도합의서</th>', '<th>전자서명 결과</th>', s)
    if k:
        note(f, '열 이름 → 전자서명 결과', k)
    s, k = re.subn(r'<th class="center">검증</th>', '<th class="center">서명 수단</th>', s)
    if k:
        note(f, '열 이름 → 서명 수단', k)
    # 행 파일 링크 — 전자서명 결과 텍스트
    s, k = re.subn(r'href="assets/docs/재양도합의서_(M2026-\d{4})\.pdf"([^>]*)>재양도합의서_M2026-\d{4}\.pdf</a>',
                   lambda m: 'href="assets/docs/%s"%s>%s</a>' % (SIG % m.group(1), m.group(2), SIG % m.group(1)), s)
    if k:
        note(f, '행 링크 → 전자서명 결과 txt', k)
    s, k = re.subn(r'<span class="badge badge-gray">확인 대상</span>',
                   '<span class="badge badge-green">하나인증서</span>', s)
    if k:
        note(f, '서명 수단 하나인증서', k)
    # 선택 문서 다운로드 — 묶음도 텍스트
    s, k = re.subn(r'href="assets/docs/재양도합의서_선택3건_20260827\.zip"', 'href="assets/docs/%s"' % SIG_SEL3, s)
    k += re.subn(r'href="assets/docs/재양도합의서_전체16건_20260827\.zip"', 'href="assets/docs/%s"' % SIG_ALL, s)[1]
    s = re.sub(r'href="assets/docs/재양도합의서_전체16건_20260827\.zip"', 'href="assets/docs/%s"' % SIG_ALL, s)
    if k:
        note(f, '묶음 다운로드 → 텍스트', k)
    # 화면 머리 안내 2줄
    if 'notice-green' not in s:
        anchor = '    <!-- 재양도합의서 목록 -->' if '<!-- 재양도합의서 목록 -->' in s else '    <div class="tbl-wrap">'
        s = s.replace(anchor, NOTICE.strip('\n') + '\n\n' + anchor, 1)
        if '.notice-green {' not in s:
            s = s.replace('</style>', NOTICE_CSS + '</style>', 1)
        note(f, '하나인증서·확인필요 안내', 2)
    W(f, s)

# ══ M-1 정산채권 양수 — 계약서보기 ═════════════════════════════════════════
for f in ACQ:
    s = R(f)
    s, k = re.subn(r'<a class="doc-link" href="assets/docs/계약서_서명대기_M2026-\d{4}\.pdf" target="_blank" rel="noopener">계약서 보기</a>',
                   '<a class="doc-link" href="acquisition--doc.html">계약서보기</a>', s)
    s, k2 = re.subn(r'<a class="doc-link" href="contracts\.html">계약서 보기</a>',
                    '<a class="doc-link" href="acquisition--doc.html">계약서보기</a>', s)
    s, k3 = re.subn(r'<a class="doc-link"([^>]*)>계약서 보기</a>',
                    r'<a class="doc-link"\1>계약서보기</a>', s)
    note(f, '계약서보기', k + k2 + k3)
    # 서명 확인 모달 문체 — G-1
    s = s.replace('전자서명합니다. 서명 후에는 취소할 수 없습니다.', '전자서명. 서명 후 취소 불가.')
    s = s.replace('서명값은 계약기록에 보관됩니다.', '서명값은 계약기록에 보관.')
    W(f, s)

# ── 계약서보기 화면 — 목록에서 연 계약서 내용 ────────────────────────────
DOC_CSS = """  /* 계약서보기 — 전자계약서로 넘어가기 전에 계약서 내용을 읽는 자리 */
  .modal.lg { max-width: 672px; }
  .doc-view { gap: 12px; }
  .doc-view .doc-kind { font-size: 15px; font-weight: 700; color: var(--gray-900); }
  .doc-view .doc-head { display: flex; align-items: center; gap: 8px; }
  .doc-view .doc-meta { margin: 0; font-size: 13px; line-height: 20px; color: var(--gray-500); }
  .doc-scroll { max-height: 46vh; overflow-y: auto; border: 1px solid var(--gray-200); border-radius: 12px; padding: 16px 18px; background: var(--gray-50); }
  .doc-scroll h4 { margin: 16px 0 4px; font-size: 13px; font-weight: 700; color: var(--gray-900); }
  .doc-scroll h4:first-child { margin-top: 0; }
  .doc-scroll p { margin: 0; font-size: 13px; line-height: 20px; color: var(--gray-700); }
  .doc-scroll .party { width: 100%; border-collapse: collapse; font-size: 12px; }
  .doc-scroll .party th, .doc-scroll .party td { border-bottom: 1px solid var(--gray-200); padding: 6px 8px; text-align: left; }
  .doc-scroll .party th { color: var(--secondary); font-weight: 600; width: 88px; }
  .doc-scroll .party td { color: var(--gray-800); }
  .doc-scroll .src { margin-top: 4px; font-size: 11px; line-height: 16px; color: var(--gray-400); }
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
        <div class="doc-head">
          <span class="doc-kind">정산금채권 재양도 합의서</span>
          <span class="badge badge-amber">서명 대기</span>
        </div>
        <p class="doc-meta">김성호떡볶이 본점 · 가맹점ID <span class="mono">M2026-0001</span> · 계약 생성일 <span class="mono">2026-08-25</span></p>
        <div class="doc-scroll">
          <h4>당사자</h4>
          <table class="party">
            <tbody>
              <tr><th>양도인</th><td>김성호떡볶이 본점 (대표자 김성호 · 사업자등록번호 123-45-67890)</td></tr>
              <tr><th>양수인</th><td>㈜페이허그</td></tr>
              <tr><th>재양수인</th><td>㈜테스트인베스트 (유동화기관 · 투자자 어드민 로그인 주체)</td></tr>
            </tbody>
          </table>
          <p class="src">직계약 3자본 기준. 총판 4자본은 양수인이 채권매입업체, 재양수인이 페이허그다 &mdash; analysis/archive_02_계약약관.md &sect;2.4</p>
          <h4>제1조 (합의의 목적)</h4>
          <p>제1부 양수도 계약에 따라 양수인이 양수하는 양도자산을, 양수와 동시에 재양수인에게 재양도하는 데 대하여 전 당사자가 합의한다.</p>
          <h4>제2조 (동시 이행)</h4>
          <p>양수인은 양도인으로부터의 양수와 동시에 양도자산을 재양수인에게 양도한다.</p>
          <h4>제3조 (이중양도 금지)</h4>
          <p>양도인은 전 당사자의 서면 동의 없이 양도자산을 제3자에게 재양도하거나 담보로 제공할 수 없다.</p>
          <h4>제4조 (전자서명)</h4>
          <p>재양수인은 하나인증서 전자서명으로 본 합의서에 서명한다. 서명값과 인증서 발행기관의 서명 검증 회신전문은 계약기록에 보관한다.</p>
          <p class="src">근거 &mdash; 재양도 합의서(가맹점직계약본) 제3조 1&middot;2항 &middot; 11_계약서/4_정산금채권 재양도 합의서_가맹점직계약.docx &middot; 서명 수단은 대표 미팅 2026-08-28 결정</p>
          <h4>수수료</h4>
          <p>채권매입수수료율은 원 계약서도 가맹점별 기입 공란이다. 여기에 어느 값도 넣지 않는다 &mdash; analysis/00_종합.md C1</p>
        </div>
      </div>
      <div class="modal-footer">
        <a class="btn btn-outline" href="acquisition.html">닫기</a>
        <a class="btn btn-primary" href="assets/docs/계약서_서명대기_M2026-0001.pdf" target="_blank" rel="noopener">원문 전체 열기</a>
      </div>
    </div>
  </div>
"""

doc = R('acquisition.html')
doc = doc.replace('<title>PayHug Admin — 정산채권 양수</title>',
                  '<title>PayHug Admin — 정산채권 양수 · 계약서보기</title>', 1)
doc = doc.replace('<h1 class="page-title">정산채권 양수</h1>',
                  '<h1 class="page-title">정산채권 양수 <span class="state-flag">계약서보기</span></h1>', 1)
doc = doc.replace('</style>', DOC_CSS + '</style>', 1)
doc = doc.replace('\n</div>\n</body>', '\n' + DOC_MODAL.rstrip('\n') + '\n\n</div>\n</body>', 1)
assert 'modal lg' in doc and 'state-flag' in doc
W('acquisition--doc.html', doc)
note('acquisition--doc.html', '신규 — 계약서 내용 화면', 1)

print('정적 낱장 반영')
print('\n'.join(log))
