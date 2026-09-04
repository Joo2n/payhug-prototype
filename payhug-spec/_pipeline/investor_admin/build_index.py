# -*- coding: utf-8 -*-
"""index.html 재생성 — 통합 프로토타입 진입 + 화면 전량 등재. 화면·상태 수는 MAIN·SUB 실측으로 찍는다."""
import io, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import counts
import daily_ledger as L
ROOT = '/Users/semi/cursor/payhug-investor-admin'

ICON = {
 'credit':'M3 10h18M7 15h1m4 0h1m-7 4h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z',
 'shield':'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z',
 'trend':'M13 7h8m0 0v8m0-8l-8 8-4-4-6 6',
 'coin':'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
 'users':'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z',
 'cards':'M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z',
 'doc':'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
 'lock':'M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z',
 'grid':'M3 10h18M3 15h18M9 5v14M15 5v14M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z',
 'ext':'M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14',
 'calc':'M15.75 15.75V18m-7.5-6.75h.008v.008H8.25v-.008zm0 2.25h.008v.008H8.25V13.5zm0 2.25h.008v.008H8.25v-.008zm0 2.25h.008v.008H8.25V18zm2.498-6.75h.007v.008h-.007v-.008zm0 2.25h.007v.008h-.007V13.5zm0 2.25h.007v.008h-.007v-.008zm0 2.25h.007v.008h-.007V18zm2.504-6.75h.008v.008h-.008v-.008zm0 2.25h.008v.008h-.008V13.5zm3.75-6.75A2.25 2.25 0 0119.5 4.5h-15A2.25 2.25 0 002.25 6.75v10.5A2.25 2.25 0 004.5 19.5h15a2.25 2.25 0 002.25-2.25V6.75z',
}

def svg(key, cls=''):
    c = ' class="%s"' % cls if cls else ''
    return ('<svg%s fill="none" stroke="currentColor" viewBox="0 0 24 24">'
            '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="%s"/></svg>' % (c, ICON[key]))

# (파일, 화면명, 아이콘, 그룹뱃지클래스, 그룹라벨, 설명, [(상태라벨, 파일), ...])
MAIN = [
 ('invest-assets.html','투자 자산','credit','badge-primary','투자','현황·가맹점별 투자자산·산식·엑셀/증명서 다운로드',
  [('엑셀 다운로드 완료','invest-assets--download.html'),
   ('증명서 발급 확인','invest-assets--cert-confirm.html'),('데이터 없음','invest-assets--empty.html')]),
 ('certificate.html','투자자산 증명서','shield','badge-primary','투자','전자문서 미리보기·서명 검증',[]),
 ('invest-profit.html','투자 수익','trend','badge-primary','투자','기간 검색·일별/주별/월별 투자수익·산식',
  [('주별','invest-profit--weekly.html'),
   ('월별','invest-profit--monthly.html'),
   ('결과 없음','invest-profit--empty.html')]),
 ('invest-sim.html','투자 시뮬레이션','calc','badge-primary','투자','기준 변수·채권 입력·투자 자산/수익 산출',
  [('실행 결과','invest-sim--result.html')]),
 ('coocon.html','쿠콘 관리 현금','coin','badge-gray','관리','메뉴에서 We-bank 로 바로 이동',[]),
 ('merchants.html','가맹점','users','badge-blue','가맹점','목록·필터 검색',
  [('검색 적용','merchants--filtered.html'),('결과 없음','merchants--empty.html')]),
 ('acquisition.html','정산채권 양수','cards','badge-blue','가맹점','계약서보기 · 양수도 계약서 전자서명',
  [('계약서보기','acquisition--doc.html'),('서명 확인','acquisition--confirm.html'),
   ('서명 진행','acquisition--signing.html'),('서명 완료','acquisition--done.html')]),
 ('contracts.html','계약기록','doc','badge-blue','가맹점','전자서명 결과 목록 · 서명 수단',
  [('전체 선택','contracts--all.html'),('문서 없음','contracts--empty.html')]),
 ('password.html','비밀번호 변경','lock','badge-gray','관리','로그인 비밀번호 변경',
  [('규칙 미충족','password--weak.html'),('확인값 불일치','password--error.html'),
   ('변경 완료','password--done.html')]),
]
SUB = [
 ('login.html','로그인','lock','badge-gray','인증','사업자번호·휴대전화 로그인 폼',[]),
 ('xls-assets-status.html','엑셀 산출물 서식 — 투자자산 현황','grid','badge-gray','Figma 전용','투자 자산 &gt; 현황 표를 내려받았을 때의 엑셀 서식',[]),
 ('xls-assets-merchant.html','엑셀 산출물 서식 — 가맹점별 투자자산','grid','badge-gray','Figma 전용','투자 자산 &gt; 가맹점별 투자자산 표를 내려받았을 때의 엑셀 서식',[]),
 ('xls-profit-status.html','엑셀 산출물 서식 — 투자수익 현황','grid','badge-gray','Figma 전용','투자 수익 &gt; 수익 현황 표를 내려받았을 때의 엑셀 서식',[]),
 ('xls-profit-daily.html','엑셀 산출물 서식 — 일별 투자수익','grid','badge-gray','Figma 전용','투자 수익 &gt; 일별 투자수익 표를 내려받았을 때의 엑셀 서식',[]),
]

def card(f, name, icon, bcls, blabel, desc, states):
    o = []
    o.append('    <div class="shot-card">')
    o.append('      <a class="shot-link" href="%s">' % f)
    o.append('        <div class="shot-top">')
    o.append('          <div class="shot-icon">%s</div>' % svg(icon))
    o.append('          <div class="shot-id">')
    o.append('            <div class="shot-name">%s</div>' % name)
    o.append('          </div>')
    o.append('          <span class="badge sm %s">%s</span>' % (bcls, blabel))
    o.append('        </div>')
    o.append('        <p class="shot-desc">%s</p>' % desc)
    o.append('      </a>')
    if states:
        o.append('      <details class="state-fold">')
        o.append('        <summary>상태 %d개</summary>' % len(states))
        o.append('        <ul class="state-list">')
        for lab, sf in states:
            o.append('          <li><a href="%s"><span class="s-name">%s</span></a></li>' % (sf, lab))
        o.append('        </ul>')
        o.append('      </details>')
    o.append('    </div>')
    return '\n'.join(o)

HEAD = '''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PayHug 투자자 어드민 — 화면 설계(안)</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/base.css">
<style>
  /* 랜딩 갤러리 전용 — 색상은 base.css 변수만 사용 */
  .wrap { max-width: 1024px; margin: 0 auto; padding: 56px 32px 64px; }
  .hero { display: flex; align-items: center; gap: 16px; }
  .hero img, .hero .logo-mark { display: block; width: 48px; height: 48px; border-radius: 12px; flex-shrink: 0; }
  .hero h1 { font-size: 26px; line-height: 34px; font-weight: 700; color: var(--gray-900); margin: 0; }
  .hero h1 em { font-style: normal; color: var(--primary-600); }
  .hero .sub { font-size: 14px; line-height: 20px; color: var(--secondary); margin: 4px 0 0; }
  .hero-date {
    margin-left: auto; align-self: flex-start;
    font-size: 12px; line-height: 16px; color: var(--gray-400);
    font-family: var(--font-mono); font-variant-numeric: tabular-nums;
    background: #fff; border: 1px solid var(--gray-200); border-radius: 6px; padding: 4px 10px;
  }

  /* 통합 프로토타입 진입 카드 */
  a.app-card {
    display: flex; align-items: center; gap: 20px; text-decoration: none;
    margin-top: 32px; padding: 28px 32px; border-radius: 20px;
    background: var(--sidebar-bg); color: #fff;
    box-shadow: var(--shadow-card);
    transition: box-shadow 0.15s var(--ease-default), transform 0.15s var(--ease-default);
  }
  a.app-card:hover { box-shadow: var(--shadow-card-hover); transform: translateY(-2px); }
  .app-card .app-icon {
    width: 56px; height: 56px; border-radius: 16px; flex-shrink: 0;
    background: rgba(127,225,65,0.16); color: var(--primary);
    display: flex; align-items: center; justify-content: center;
  }
  .app-card .app-icon svg { width: 26px; height: 26px; }
  .app-card .app-name { font-size: 20px; line-height: 28px; font-weight: 700; }
  .app-card .app-name em { font-style: normal; color: var(--primary); }
  .app-card .app-desc { font-size: 13px; line-height: 20px; color: rgba(255,255,255,0.72); margin: 6px 0 0; }
  .app-card .app-go {
    margin-left: auto; flex-shrink: 0;
    background: var(--primary); color: var(--gray-900);
    font-size: 14px; line-height: 20px; font-weight: 700;
    padding: 10px 20px; border-radius: 10px; white-space: nowrap;
  }

  /* 문서 링크 카드 */
  .doc-row { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-top: 16px; }
  @media (min-width: 760px) { .doc-row { grid-template-columns: repeat(3, 1fr); } }
  @media (min-width: 1000px) { .doc-row { grid-template-columns: repeat(4, 1fr); } }
  a.doc-card {
    display: flex; align-items: center; gap: 12px; text-decoration: none;
    background: #fff; border: 1px solid var(--gray-100); border-radius: 16px;
    padding: 16px 20px; box-shadow: var(--shadow-card);
    transition: box-shadow 0.15s var(--ease-default), border-color 0.15s var(--ease-default), transform 0.15s var(--ease-default);
  }
  a.doc-card:hover { box-shadow: var(--shadow-card-hover); border-color: var(--primary-200); transform: translateY(-2px); }
  .doc-card .doc-icon {
    width: 36px; height: 36px; border-radius: 10px; flex-shrink: 0;
    background: var(--gray-100); color: var(--gray-500);
    display: flex; align-items: center; justify-content: center;
  }
  .doc-card .doc-icon svg { width: 18px; height: 18px; }
  .doc-card .d-name { font-size: 15px; line-height: 22px; font-weight: 700; color: var(--gray-900); }
.doc-card .d-desc { font-size: 12px; line-height: 16px; color: var(--gray-400); margin-top: 1px; }

  /* 섹션 제목 */
  .sec-head { display: flex; align-items: baseline; gap: 10px; margin: 40px 0 0; }
  .sec-head h2 { font-size: 16px; line-height: 24px; font-weight: 700; color: var(--gray-900); margin: 0; }
  .sec-head .sec-note { font-size: 12px; line-height: 16px; color: var(--gray-400); }

  /* 화면 카드 */
  .gallery { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-top: 16px; align-items: start; }
  .shot-card {
    background: #fff; border-radius: 16px;
    box-shadow: var(--shadow-card); border: 1px solid var(--gray-100);
    transition: box-shadow 0.15s var(--ease-default), border-color 0.15s var(--ease-default);
    overflow: hidden;
  }
  .shot-card:hover { box-shadow: var(--shadow-card-hover); border-color: var(--primary-200); }
  a.shot-link { display: block; text-decoration: none; padding: 20px 24px; }
  .shot-top { display: flex; align-items: center; gap: 12px; }
  .shot-icon {
    width: 36px; height: 36px; border-radius: 10px; flex-shrink: 0;
    background: var(--primary-50); color: var(--primary-600);
    display: flex; align-items: center; justify-content: center;
  }
  .shot-icon svg { width: 18px; height: 18px; }
  .shot-id { min-width: 0; }
  .shot-name { font-size: 16px; line-height: 22px; font-weight: 700; color: var(--gray-900); }
  .shot-top .badge.sm { margin-left: auto; flex-shrink: 0; }
  .shot-desc { font-size: 13px; line-height: 19px; color: var(--gray-500); margin: 12px 0 0; }

  /* 상태 접기 목록 */
  .state-fold { border-top: 1px solid var(--gray-100); background: var(--gray-50); }
  .state-fold > summary {
    list-style: none; cursor: pointer;
    padding: 10px 24px; font-size: 12px; line-height: 16px; font-weight: 600; color: var(--gray-500);
  }
  .state-fold > summary::-webkit-details-marker { display: none; }
  .state-fold > summary::before { content: "▸ "; color: var(--gray-400); }
  .state-fold[open] > summary::before { content: "▾ "; }
  .state-fold > summary:hover { color: var(--gray-700); }
  .state-list { list-style: none; margin: 0; padding: 0 12px 12px; }
  .state-list a {
    display: flex; align-items: baseline; gap: 8px; text-decoration: none;
    padding: 7px 12px; border-radius: 8px;
  }
  .state-list a:hover { background: #fff; }
  .state-list .s-name { font-size: 13px; line-height: 18px; font-weight: 500; color: var(--gray-700); }

</style>
</head>
<body>
<div class="wrap">

  <div class="hero">
    <span class="logo-mark" role="img" aria-label="PayHug"></span>
    <div>
      <h1>PayHug <em>투자자 어드민</em> — 화면 설계(안)</h1>
      <p class="sub">투자자용 어드민 UI 기획 · 기존 어드민 디자인시스템 기준</p>
    </div>
    <span class="hero-date">@@ASOF@@</span>
  </div>
'''

o = [HEAD]
o.append('''
  <a class="app-card" href="app.html">
    <div class="app-icon">%s</div>
    <div>
      <div class="app-name"><em>통합</em> 프로토타입</div>
      <p class="app-desc">사이드바 메뉴 %d개 &mdash; %s</p>
    </div>
    <span class="app-go">열기</span>
  </a>

  <div class="doc-row">
    <a class="doc-card" href="glossary.html">
      <div class="doc-icon">%s</div>
      <div>
        <div class="d-name">용어 해설</div>
        <div class="d-desc">화면과 엑셀에 쓰인 계산식 용어 50건</div>
      </div>
    </a>
    <a class="doc-card" href="terms-edit.html">
      <div class="doc-icon">%s</div>
      <div>
        <div class="d-name">용어 정의서 편집판</div>
        <div class="d-desc">대표 정의 45항 &mdash; 그 자리에서 고쳐 저장</div>
      </div>
    </a>
    <a class="doc-card" href="final-terms.html">
      <div class="doc-icon">%s</div>
      <div>
        <div class="d-name">용어·기호 정리</div>
        <div class="d-desc">기존 표기 &rarr; 바뀐 기호</div>
      </div>
    </a>
    <a class="doc-card" href="calc.html">
      <div class="doc-icon">%s</div>
      <div>
        <div class="d-name">계산식 하나씩</div>
        <div class="d-desc">변수 정의 &rarr; 산식 &rarr; 대입 &rarr; 결과</div>
      </div>
    </a>
    <a class="doc-card" href="steps-all.html">
      <div class="doc-icon">%s</div>
      <div>
        <div class="d-name">화면 칸별 중간 계산</div>
        <div class="d-desc">투자 자산 · 투자 수익 두 화면의 값</div>
      </div>
    </a>
    <a class="doc-card" href="capability.html">
      <div class="doc-icon">%s</div>
      <div>
        <div class="d-name">기능·데이터 명세</div>
        <div class="d-desc">투자자에게 노출되는 기능과 데이터 범위</div>
      </div>
    </a>
    <a class="doc-card" href="feasibility.html">
      <div class="doc-icon">%s</div>
      <div>
        <div class="d-name">구현 가능성</div>
        <div class="d-desc">화면·데이터 항목별로 지금 만들 수 있는 범위</div>
      </div>
    </a>
    <a class="doc-card" href="inquiry.html">
      <div class="doc-icon">%s</div>
      <div>
        <div class="d-name">대표 확인 요청</div>
        <div class="d-desc">확인 문항 5건과 개발·백엔드 부록</div>
      </div>
    </a>
    <a class="doc-card" href="ceo-questions.html">
      <div class="doc-icon">%s</div>
      <div>
        <div class="d-name">대표님 확인 문항</div>
        <div class="d-desc">미팅 확인 문항 &mdash; 답을 적어 저장</div>
      </div>
    </a>
    <a class="doc-card" href="review.html">
      <div class="doc-icon">%s</div>
      <div>
        <div class="d-name">순차 확인</div>
        <div class="d-desc">무엇을 어느 순서로 볼지 한 단계씩</div>
      </div>
    </a>
    <a class="doc-card" href="archive.html">
      <div class="doc-icon">%s</div>
      <div>
        <div class="d-name">작업물 아카이브</div>
        <div class="d-desc">산출물 전체 목록 — 경로·설명·수정 시각</div>
      </div>
    </a>
  </div>
''' % (svg('ext'), counts.C['menus'], counts.menu_sentence().replace(' · ', ' &middot; '),
       svg('doc'), svg('calc'), svg('doc'), svg('calc'), svg('grid'),
       svg('shield'), svg('trend'), svg('cards'), svg('users'), svg('lock'),
       svg('grid')))

# 화면·상태 수는 MAIN 실측으로 찍는다. 박아 두면 D-34(주별 신설)처럼 화면이 늘 때마다 낡는다.
o.append('''
  <div class="sec-head">
    <h2>화면</h2>
    <span class="sec-note">기본 화면 %d · 상태 %d</span>
  </div>
  <div class="gallery">
''' % (len(MAIN), sum(len(c[6]) for c in MAIN)))
o.append('\n'.join(card(*c) for c in MAIN))
o.append('''
  </div>

  <div class="sec-head">
    <h2>하위 화면</h2>
    <span class="sec-note">인증 %d · 엑셀 산출물 서식 %d</span>
  </div>
  <div class="gallery">
''' % (sum(1 for c in SUB if not c[0].startswith('xls-')),
       sum(1 for c in SUB if c[0].startswith('xls-'))))
o.append('\n'.join(card(*c) for c in SUB))
o.append('''
  </div>


</div>
</body>
</html>
''')

# 기준일 — 원천은 daily_ledger.ASOF 한 줄이다.
_DOC = ''.join(o).replace('@@ASOF@@', L.ASOF_S)
assert '@@ASOF' not in _DOC, '기준일 토큰 잔여'
open(os.path.join(ROOT,'index.html'),'w',encoding='utf-8').write(_DOC)
n_states = sum(len(c[6]) for c in MAIN+SUB)
assert (len(MAIN)+len(SUB)+1, n_states) == (counts.C['screens'], counts.C['states']), \
    '화면·상태 실측이 갈린다 — 등재 %s/%s vs 파일 %s/%s' % (
        len(MAIN)+len(SUB)+1, n_states, counts.C['screens'], counts.C['states'])
counts.dump()
print('index.html 재생성 — 화면 %d · 상태 %d' % (len(MAIN)+len(SUB)+1, n_states))
