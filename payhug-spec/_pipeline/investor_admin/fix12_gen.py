# -*- coding: utf-8 -*-
"""build_app.py 정정 — 배포본 지적 12건 반영.

1  스토리보드 근거 없는 안내·부연 문구 제거      7  조회 필터를 스토리보드 슬라이드7 구성으로
2  용어 안내 섹션 제거(app.html 한정)            8  계약기록 선택 해제 버튼 · 표 아래 각주 제거
3  화면·상태 이동 도크(FAB) 제거                 9  쿠콘 카드 통합
4  수익 산정 기준 카드 = SHOW_FORMULA 스위치     10 제목 아래 한 줄 설명 전 화면 제거
5  페이지네이션 가운데 · 건수 같은 줄 왼쪽       11 서명 대기 목록 전체 선택·선택 해제·행 클릭
6  서명 버튼을 목록 카드 안으로                  12 합계 행 가중평균 표기를 아래 줄로

한 번만 돌린다. 이미 반영된 상태에서 다시 돌리면 치환 건수 검사에서 멈춘다.
"""
import io, os

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build_app.py')
s = io.open(P, encoding='utf-8').read()
done = []


def rep(old, new, tag, n=1):
    global s
    c = s.count(old)
    if c != n:
        raise SystemExit('[%s] %d회 (기대 %d)' % (tag, c, n))
    s = s.replace(old, new)
    done.append('%-34s %d' % (tag, n))


# ══════════════════════════════════════════════════════════════════
# 10 — 제목 아래 한 줄 설명(page-sub) 전 화면 제거
# ══════════════════════════════════════════════════════════════════
for label, sub in [
    ('invest-assets',   '투자자산 현황과 가맹점별 투자 내역.'),
    ('certificate',     '전자서명이 포함된 발급 문서 미리보기.'),
    ('invest-profit',   '기간별 투자 수익 현황 조회 · 수익 산정 기준 안내.'),
    ('merchants',       '투자 대상 가맹점 목록.'),
    ('acquisition',     '정산금채권 양수도 계약서 전자서명.'),
    ('contracts',       '정산금채권 재양도합의서 보관함.'),
    ('coocon',          '관리 현금 거래 내역 조회를 위한 외부 시스템 연결.'),
    ('password',        '로그인 비밀번호 변경.'),
]:
    for indent in ('            ', '          '):
        blk = '\n%s<p class="page-sub">%s</p>' % (indent, sub)
        if blk in s:
            rep(blk, '', 'page-sub/' + label)
            break
    else:
        raise SystemExit('page-sub 미발견: ' + label)

# 엑셀 서식 화면 4종 — 셸에서 부제 슬롯 자체를 없앤다
rep('''def xls_shell(sid, back, backlabel, title, sub):
    return \'\'\'
      <section class="screen" data-screen="%s" data-state="default" hidden>
        <a class="back-link" href="%s.html" data-nav="%s">%s %s</a>
        <div class="page-header">
          <h1 class="page-title">%s<span data-state-mark></span></h1>
          <p class="page-sub">%s</p>
        </div>
        <div class="file-bar" data-mount="filebar"></div>
        <div class="sheet-frame">
          <div class="sheet-tabs" data-mount="sheettabs"></div>
          <div class="sheet-scroll"><table class="sheet" data-mount="sheet"></table></div>
        </div>
        <p class="sheet-caption">화면의 표를 그대로 엑셀 양식으로 내려받은 결과. 서식·열 순서는 화면과 동일.</p>
      </section>\'\'\' % (sid, back, back, sv(D_LEFT), backlabel, title, sub)''',
    '''def xls_shell(sid, back, backlabel, title):
    return \'\'\'
      <section class="screen" data-screen="%s" data-state="default" hidden>
        <a class="back-link" href="%s.html" data-nav="%s">%s %s</a>
        <div class="page-header">
          <h1 class="page-title">%s<span data-state-mark></span></h1>
        </div>
        <div class="file-bar" data-mount="filebar"></div>
        <div class="sheet-frame">
          <div class="sheet-tabs" data-mount="sheettabs"></div>
          <div class="sheet-scroll"><table class="sheet" data-mount="sheet"></table></div>
        </div>
      </section>\'\'\' % (sid, back, back, sv(D_LEFT), backlabel, title)''', 'xls_shell 부제 슬롯 제거')

rep('''    xls_shell('xls-assets-status',  'invest-assets', '투자 자산',
              '엑셀 산출물 서식 — 투자자산 현황', '투자 자산 &gt; 현황 표를 엑셀로 내려받았을 때의 시트 서식. Figma 임포트용이며 화면 흐름의 진입점이 아님.') +
    xls_shell('xls-assets-merchant', 'invest-assets', '투자 자산',
              '엑셀 산출물 서식 — 가맹점별 투자자산', '투자 자산 &gt; 가맹점별 투자자산 표를 엑셀로 내려받았을 때의 시트 서식. Figma 임포트용이며 화면 흐름의 진입점이 아님.') +
    xls_shell('xls-profit-status',  'invest-profit', '투자 수익',
              '엑셀 산출물 서식 — 투자수익 현황', '투자 수익 &gt; 수익 현황 카드를 엑셀로 내려받았을 때의 시트 서식. Figma 임포트용이며 화면 흐름의 진입점이 아님.') +
    xls_shell('xls-profit-daily',   'invest-profit', '투자 수익',
              '엑셀 산출물 서식 — 일별 투자수익', '투자 수익 &gt; 일별 투자수익 표를 엑셀로 내려받았을 때의 시트 서식. Figma 임포트용이며 화면 흐름의 진입점이 아님.')''',
    '''    xls_shell('xls-assets-status',  'invest-assets', '투자 자산', '엑셀 산출물 서식 — 투자자산 현황') +
    xls_shell('xls-assets-merchant', 'invest-assets', '투자 자산', '엑셀 산출물 서식 — 가맹점별 투자자산') +
    xls_shell('xls-profit-status',  'invest-profit', '투자 수익', '엑셀 산출물 서식 — 투자수익 현황') +
    xls_shell('xls-profit-daily',   'invest-profit', '투자 수익', '엑셀 산출물 서식 — 일별 투자수익')''',
    'xls_shell 호출 4건')

# ══════════════════════════════════════════════════════════════════
# 2·4 — 용어 안내 제거 · 수익 산정 기준 스위치
# ══════════════════════════════════════════════════════════════════
rep("""   .replace('{FORMULA}', '        ' + dedent_block(FORMULA, 4).replace('\\n', '\\n        ')) \\
   .replace('{TERMS}', '        ' + dedent_block(TERMS, 4).replace('\\n', '\\n        '))""",
    """   .replace('{FORMULA}', FORMULA_BLOCK)""", 'FORMULA/TERMS 치환', 2)

rep("""assert TERMS.startswith('    <div class="terms-note">') and 'W금융일수' in TERMS""",
    """assert TERMS.startswith('    <div class="terms-note">') and 'W금융일수' in TERMS
# 용어 안내는 통합본에서 내린다 — 정적 화면(투자 자산 4종)에만 남는다. 스토리보드 슬라이드 3~6 각주 근거.
FORMULA_BLOCK = ('        ' + dedent_block(FORMULA, 4).replace('\\n', '\\n        ')) if SHOW_FORMULA else ''""",
    '용어 안내 블록 분리')

for tag in ('ia', 'pf'):
    pass
rep("""{FORMULA}

{TERMS}
      </section>

      <!-- ═════════ 투자자산 증명서 ═════════ -->""",
    """{FORMULA}
      </section>

      <!-- ═════════ 투자자산 증명서 ═════════ -->""", 'terms-note 제거/invest-assets')

rep("""{FORMULA}

{TERMS}
      </section>

      <!-- ═════════ 가맹점 ═════════ -->""",
    """{FORMULA}
      </section>

      <!-- ═════════ 가맹점 ═════════ -->""", 'terms-note 제거/invest-profit')

# ══════════════════════════════════════════════════════════════════
# 7 — 조회 필터를 스토리보드 슬라이드7 구성으로
#     [시작일] ~ [종료일] [일주일][금월] [검색][초기화]  /  아래 줄에 [일별][월별]
#     '어제' 는 슬라이드7에 없다 — 뺀다.
# ══════════════════════════════════════════════════════════════════
rep("""        <div class="search-bar">
          <div class="preset-row">
            <button class="preset-btn" data-act="preset" data-preset="yesterday">어제</button>
            <button class="preset-btn" data-act="preset" data-preset="week">일주일</button>
            <button class="preset-btn" data-act="preset" data-preset="month">이번달</button>
          </div>
          <div class="filter-row">
            <div class="filter-field">
              <label>시작일</label>
              <input type="date" class="input" data-mount="pf-from" data-act="pf-date" data-which="from">
            </div>
            <div class="filter-tilde">~</div>
            <div class="filter-field">
              <label>종료일</label>
              <input type="date" class="input" data-mount="pf-to" data-act="pf-date" data-which="to">
            </div>
            <button class="btn btn-primary" data-act="pf-search" data-mount="pf-go">검색</button>
            <button class="btn btn-outline" data-act="pf-reset">초기화</button>
          </div>
          <p class="range-warn" data-mount="pf-warn" hidden>시작일은 종료일보다 이후일 수 없음.</p>
        </div>""",
    """        <div class="search-bar">
          <div class="filter-row">
            <div class="filter-field">
              <label>시작일</label>
              <input type="date" class="input" data-mount="pf-from" data-act="pf-date" data-which="from">
            </div>
            <div class="filter-tilde">~</div>
            <div class="filter-field">
              <label>종료일</label>
              <input type="date" class="input" data-mount="pf-to" data-act="pf-date" data-which="to">
            </div>
            <div class="preset-row">
              <button class="preset-btn" data-act="preset" data-preset="week">일주일</button>
              <button class="preset-btn" data-act="preset" data-preset="month">금월</button>
            </div>
            <button class="btn btn-primary" data-act="pf-search" data-mount="pf-go">검색</button>
            <button class="btn btn-outline" data-act="pf-reset">초기화</button>
          </div>
          <p class="range-warn" data-mount="pf-warn" hidden>시작일은 종료일보다 이후일 수 없음.</p>
          <div class="toggle">
            <button class="toggle-btn" data-act="pf-gran" data-gran="daily">일별</button>
            <button class="toggle-btn" data-act="pf-gran" data-gran="monthly">월별</button>
          </div>
        </div>""", '검색 영역 재배치')

rep("""            <div class="left">
              <h2 class="card-title" data-mount="pf-tbl-title">일별 투자수익</h2>
              <div class="toggle">
                <button class="toggle-btn" data-act="pf-gran" data-gran="daily">일별</button>
                <button class="toggle-btn" data-act="pf-gran" data-gran="monthly">월별</button>
              </div>
            </div>""",
    """            <div class="left">
              <h2 class="card-title" data-mount="pf-tbl-title">일별 투자수익</h2>
            </div>""", '일별·월별 토글 이동')

rep("""var PRESET_LABEL = {yesterday:'어제', week:'일주일', month:'이번달'};""",
    """var PRESET_LABEL = {week:'일주일', month:'금월'};""", 'PRESET_LABEL')

rep("""var PRESET_RANGE = {
  yesterday: ['2026-08-26', '2026-08-26'],
  week:      ['2026-08-21', '2026-08-27'],
  month:     ['2026-08-01', '2026-08-27']
};""",
    """/* 프리셋은 스토리보드 슬라이드7 그대로 둘이다 — 일주일·금월.
   원본 DateRangeFilter.tsx:23-61 은 7종(오늘·어제·이번 주·지난 주·이번 달·지난 달·최근 3개월)이지만
   이 화면의 진실은 스토리보드다. '어제'는 슬라이드7에 없어 싣지 않는다. */
var PRESET_RANGE = {
  week:  ['2026-08-21', '2026-08-27'],
  month: ['2026-08-01', '2026-08-27']
};""", 'PRESET_RANGE')

# ══════════════════════════════════════════════════════════════════
# 5 — 페이지네이션: 쪽번호 가운데 · 건수 같은 줄 왼쪽
# ══════════════════════════════════════════════════════════════════
rep("""function pageBar(cur, pages, act, left){
  var h = left ? left : '';
  var inner = '<button class="page-arrow" data-act="' + act + '" data-page="' + (cur - 1) + '"' + (cur <= 1 ? ' disabled' : '') + '>' + svg('left') + '</button>';
  for(var p = 1; p <= pages; p++)
    inner += '<button class="page-btn' + (p === cur ? ' active' : '') + '" data-act="' + act + '" data-page="' + p + '">' + p + '</button>';
  inner += '<button class="page-arrow" data-act="' + act + '" data-page="' + (cur + 1) + '"' + (cur >= pages ? ' disabled' : '') + '>' + svg('right') + '</button>';
  return left ? (h + '<div style="display:flex; align-items:center; gap:4px">' + inner + '</div>') : inner;
}""",
    """/* 쪽번호는 가운데, 총 건수는 같은 줄 맨 왼쪽.
   원본 activity-logs/page.tsx:339 · sales/[bizNo]/page.tsx:1243 = justify-center,
   LockAccountDeposits.tsx:435-437 = 같은 줄 왼쪽 총 건수. 두 패턴을 3열 격자로 겹쳐 쓴다. */
function pageBar(cur, pages, act, left){
  var inner = '<button class="page-arrow" data-act="' + act + '" data-page="' + (cur - 1) + '"' + (cur <= 1 ? ' disabled' : '') + '>' + svg('left') + '</button>';
  for(var p = 1; p <= pages; p++)
    inner += '<button class="page-btn' + (p === cur ? ' active' : '') + '" data-act="' + act + '" data-page="' + p + '">' + p + '</button>';
  inner += '<button class="page-arrow" data-act="' + act + '" data-page="' + (cur + 1) + '"' + (cur >= pages ? ' disabled' : '') + '>' + svg('right') + '</button>';
  if(!left) return inner;
  return '<span class="pg-count">' + left + '</span><div class="pg-nums">' + inner + '</div><span></span>';
}""", 'pageBar 3열')

rep("""          <div class="pagination" style="justify-content:space-between" data-mount="mc-page"></div>""",
    """          <div class="pagination with-count" data-mount="mc-page"></div>""", 'mc-page 격자')

rep("""  M('mc-page', 'merchants').innerHTML = pageBar(MC.page, pages, 'mc-page',
    '<span style="font-size:12px; color:var(--gray-500)">총 <b class="mono">' + rows.length + '</b>건'
    + rangeLabel(MC.page, pages, rows.length) + '</span>');""",
    """  M('mc-page', 'merchants').innerHTML = pageBar(MC.page, pages, 'mc-page',
    '총 <b class="mono">' + rows.length + '</b>건' + rangeLabel(MC.page, pages, rows.length));""", 'mc-page 렌더')

# ══════════════════════════════════════════════════════════════════
# 1·5·8 — 표 아래 각주 제거
# ══════════════════════════════════════════════════════════════════
rep("""          <div class="tbl-foot-note">가맹점 상세 화면은 이번 설계(안) 범위 밖. 행 클릭 목적지 없음.</div>\n""",
    '', 'tbl-foot-note/merchants')
rep("""          <div class="tbl-foot-note">다운로드 시 선택한 각 가맹점의 재양도합의서 파일이 제공됨. 서명 검증 회신전문은 형식·전달 경로 미정의 — 확인 대상.</div>\n""",
    '', 'tbl-foot-note/contracts')

# ══════════════════════════════════════════════════════════════════
# 8 — 계약기록: 선택 해제 버튼을 다운로드 버튼 왼쪽에
# ══════════════════════════════════════════════════════════════════
rep("""            <button class="btn btn-excel" data-act="ct-download" data-mount="ct-dl">{EX2}</button>""",
    """            <div class="list-tools">
              <button class="btn btn-ghost" data-act="ct-clear" data-mount="ct-clear">선택 해제</button>
              <button class="btn btn-excel" data-act="ct-download" data-mount="ct-dl">{EX2}</button>
            </div>""", 'ct 선택 해제 버튼')

rep("""  M('ct-dl-label', 'contracts').textContent = '선택 문서 다운로드' + (n ? ' (' + n + ')' : '');""",
    """  M('ct-dl-label', 'contracts').textContent = '선택 문서 다운로드' + (n ? ' (' + n + ')' : '');
  M('ct-clear', 'contracts').disabled = (n === 0);""", 'ct-clear 상태')

# ══════════════════════════════════════════════════════════════════
# 6·11 — 정산채권 양수: 목록 도구 · 카드 안 서명 버튼 · 행 클릭 선택
# ══════════════════════════════════════════════════════════════════
rep("""        <div class="card" style="padding:0; overflow:hidden">
          <div style="padding:16px 24px; border-bottom:1px solid var(--gray-100)">
            <span class="card-title" style="margin:0" data-mount="aq-title">서명 대기 목록</span>
          </div>
          <div data-mount="aq-rows"></div>
        </div>""",
    """        <div class="card" style="padding:0; overflow:hidden">
          <div class="tbl-head-bar">
            <span class="card-title" style="margin:0" data-mount="aq-title">서명 대기 목록</span>
            <div class="list-tools">
              <button class="btn btn-ghost" data-act="aq-all" data-mount="aq-all">전체 선택</button>
              <button class="btn btn-ghost" data-act="aq-clear" data-mount="aq-clear">선택 해제</button>
            </div>
          </div>
          <div data-mount="aq-rows"></div>
          <div class="sign-foot" data-mount="action-bar">
            <span class="sel-count">선택 <b class="mono" data-mount="ab-count">0</b>건</span>
            <button class="btn btn-primary" data-act="aq-sign" data-mount="ab-btn" disabled>서명하기</button>
          </div>
        </div>""", '서명 버튼 카드 내 배치')

rep("""    h += '<div class="sign-row' + (sg ? ' done' : (sel ? ' selected' : '')) + '">' +
      '<input type="checkbox" class="chk" data-act="aq-chk" data-i="' + i + '"' + ((sel || sg) ? ' checked' : '') + (sg ? ' disabled' : '') + '>' +""",
    """    /* 행 어디를 눌러도 선택된다 — 체크박스 자체와 계약서 링크는 각자 data-act 를 가져
       closest() 가 먼저 잡으므로 행 토글과 겹쳐 상쇄되지 않는다. */
    h += '<div class="sign-row' + (sg ? ' done' : (sel ? ' selected' : '')) + '"' +
      (sg ? '' : ' data-act="aq-row" data-i="' + i + '" role="checkbox" tabindex="0" aria-checked="' + (sel ? 'true' : 'false') + '"') + '>' +
      '<input type="checkbox" class="chk" data-act="aq-chk" data-i="' + i + '"' + ((sel || sg) ? ' checked' : '') + (sg ? ' disabled' : '') + '>' +""",
    'sign-row 행 클릭')

rep("""      (sg ? '<a class="doc-link" href="contracts.html" data-nav="contracts">계약서 보기</a>'
          : '<a class="doc-link" href="assets/docs/계약서_서명대기_' + s.mid + '.pdf" target="_blank" rel="noopener">계약서 보기</a>') + '</div>';""",
    """      (sg ? '<a class="doc-link" href="contracts.html" data-nav="contracts">계약서 보기</a>'
          : '<a class="doc-link" data-act="aq-doc" href="assets/docs/계약서_서명대기_' + s.mid + '.pdf" target="_blank" rel="noopener">계약서 보기</a>') + '</div>';""",
    'aq-doc 링크 표식')

rep("""  M('ab-count').textContent = aqCount();
  var btn = M('ab-btn');
  btn.disabled = (aqCount() === 0 || AQ.phase !== 'list');""",
    """  M('ab-count').textContent = aqCount();
  var btn = M('ab-btn');
  btn.disabled = (aqCount() === 0 || AQ.phase !== 'list');
  var openN = 0;
  for(i = 0; i < SIGNQ.length; i++) if(!AQ.signed[i]) openN++;
  M('aq-all').disabled   = (openN === 0 || aqCount() === openN);
  M('aq-clear').disabled = (aqCount() === 0);""", 'aq 도구 상태')

rep("""/* 도크 */
ACT['dock-toggle'] = function(){ var p = M('dock-panel'); p.hidden = !p.hidden; };
ACT['dock-state']  = function(el){ setState(CUR, el.dataset.state); };""",
    """/* 목록 선택 도구 */
ACT['aq-all']   = function(){ for(var i = 0; i < SIGNQ.length; i++) if(!AQ.signed[i]) AQ.sel[i] = true; refresh('acquisition-list'); };
ACT['aq-clear'] = function(){ for(var i = 0; i < SIGNQ.length; i++) AQ.sel[i] = false; refresh('acquisition-list'); };
ACT['aq-row']   = function(el){ var i = +el.dataset.i; if(AQ.signed[i]) return; AQ.sel[i] = !AQ.sel[i]; refresh('acquisition-list'); };
ACT['aq-doc']   = function(){};   /* 링크는 기본 동작(새 창)으로 흘린다 — 행 토글과 겹치지 않게 */
ACT['ct-clear'] = function(){ CT.sel = {}; refresh('contracts'); };""", '도크 핸들러 → 목록 도구')

rep("""var KEEP_DEFAULT = ['xls-get', 'cert-pdf', 'aq-chk', 'ct-chk', 'ct-all'];""",
    """var KEEP_DEFAULT = ['xls-get', 'cert-pdf', 'aq-chk', 'ct-chk', 'ct-all', 'aq-doc'];""", 'KEEP_DEFAULT')

rep("""  var head = t.closest('th[data-act="sort"]');""",
    """  /* 선택 행은 키보드로도 토글된다 — role=checkbox 에 Space·Enter */
  var row = t.closest('[data-act="aq-row"]');
  if(row && (k === 'Enter' || k === ' ' || k === 'Spacebar')){
    e.preventDefault();
    var ri = row.dataset.i;
    ACT['aq-row'](row, e);
    var back = document.querySelector('[data-act="aq-row"][data-i="' + ri + '"]');
    if(back) back.focus();
    return;
  }

  var head = t.closest('th[data-act="sort"]');""", '행 키보드 토글')

# ══════════════════════════════════════════════════════════════════
# 3 — 도크(FAB) 제거
# ══════════════════════════════════════════════════════════════════
rep("""<div class="dock">
  <button class="dock-toggle" data-act="dock-toggle"><span class="dot"></span><span data-mount="dock-label">화면 · 상태</span></button>
  <div class="dock-panel" data-mount="dock-panel" hidden>
    <h3>화면</h3>
    <select class="input" data-mount="dock-screen" data-act="dock-screen"></select>
    <h3>상태</h3>
    <div class="dock-states" data-mount="dock-states"></div>
    <p class="dock-hint">해시 딥링크 <code>#화면/상태</code> · 예 <code>#invest-assets/page2</code></p>
  </div>
</div>
""", '', '도크 마크업')

rep("""<div class="action-bar" data-mount="action-bar" hidden>
  <span class="sel-count">선택 <b class="mono" data-mount="ab-count">0</b>건</span>
  <button class="btn btn-primary" style="padding:12px 40px; font-size:16px; border-radius:12px" data-act="aq-sign" data-mount="ab-btn" disabled>서명하기</button>
</div>

""", '', '하단 고정 액션바 제거')

rep("""  M('action-bar').hidden = (id !== 'acquisition-list');
  if(id === CUR){ setHash(id, st); updateDock(id, st); }""",
    """  if(id === CUR) setHash(id, st);""", 'refresh 도크 호출 제거')

rep("""<!-- ═══════════ 하단 액션바 · 토스트 · 이동 도크 ═══════════ -->""",
    """<!-- ═══════════ 토스트 ═══════════ -->""", '크롬 주석')

rep("""function updateDock(id, st){
  var sel = M('dock-screen');
  if(!sel.options.length){
    sel.innerHTML = SCREEN_ORDER.map(function(s){ return '<option value="' + s + '">' + SCREEN_LABEL[s] + '</option>'; }).join('');
  }
  sel.value = id;
  var meta = STATE_META[id] || {'default':null};
  var keys = Object.keys(meta);
  M('dock-states').innerHTML = keys.map(function(k){
    return '<button data-act="dock-state" data-state="' + k + '"' + (k === st ? ' class="on"' : '') + '>' +
           (k === 'default' ? '기본' : meta[k].label) + '</button>';
  }).join('');
  M('dock-label').textContent = SCREEN_LABEL[id] + (meta[st] ? ' · ' + meta[st].label : '');
}
""", '', 'updateDock 함수 제거')

rep("""  var h = readHash();
  updateDock('invest-assets', 'default');
""", """  var h = readHash();
""", 'updateDock 초기화 호출 제거')

rep("""  if(el.dataset.act === 'dock-screen') go(el.value);\n""", '', 'dock-screen 변경 핸들러')

# ══════════════════════════════════════════════════════════════════
# 12 — 합계 행 가중평균 표기를 숫자 아래 줄로
# ══════════════════════════════════════════════════════════════════
rep("""         '<td class="num">' + fx(wAvg, 1) + '<span class="avg-note">(가중평균)</span></td>' +
         '<td class="num">' + fx(tyExec, 2) + '%<span class="avg-note">(가중평균)</span></td></tr></tfoot>';""",
    """         '<td class="num">' + fx(wAvg, 1) + '<span class="avg-sub">가중평균</span></td>' +
         '<td class="num">' + fx(tyExec, 2) + '%<span class="avg-sub">가중평균</span></td></tr></tfoot>';""",
    '합계 가중평균 표기')

# 1·12 — 표 아래 부연 문단 제거
rep("""    /* 한 달을 일부만 덮은 행은 몇 일치인지 표 아래에 적는다 — 한 달 전체로 오해할 여지를 없앤다. */
    var part = [];
    if(!daily) for(i = 0; i < rows.length; i++)
      if(rows[i].days < LEDGER_MONTH_DAYS[rows[i].d]) part.push(rows[i].d + ' ' + rows[i].days + '일');
    t += '</table></div><p class="tbl-note">' +
         (daily ? '※ 조회 기간에 걸친 일자만 담는다. 합계 행의 W금융일수·Ty수익율은 투자실행금 가중평균(단순평균 아님).'
                : '※ 월 행은 그 달 가운데 조회 기간에 걸친 일자만 합친 값이다.' +
                  (part.length ? ' 일부만 걸친 달 — ' + part.join(' · ') + '.' : '') +
                  ' 월 행·합계 행의 W금융일수·Ty수익율은 투자실행금 가중평균(단순평균 아님).') +
         '</p>';
    box.innerHTML = t;""",
    """    t += '</table></div>';
    box.innerHTML = t;""", 'tbl-note 제거')

# ══════════════════════════════════════════════════════════════════
# 1 — 빈 상태 부연 · 확인 대상 꼬리 문장 제거
# ══════════════════════════════════════════════════════════════════
rep("""function emptyState(icon, title, desc, cta){
  return '<div class="empty-state"><div class="empty-ico">' + svg(icon, 1.6) + '</div>' +
         '<p class="empty-title">' + title + '</p><p class="empty-desc">' + desc + '</p>' + (cta || '') + '</div>';
}""",
    """function emptyState(icon, title, cta){
  return '<div class="empty-state"><div class="empty-ico">' + svg(icon, 1.6) + '</div>' +
         '<p class="empty-title">' + title + '</p>' + (cta || '') + '</div>';
}""", 'emptyState 부연 제거')

rep("""    mm.innerHTML = emptyState('chart', '조회된 투자자산 없음', '선정산 채권 양수 후 자산이 집계됨.');""",
    """    mm.innerHTML = emptyState('chart', '조회된 투자자산 없음');""", 'empty/invest-assets')
rep("""    box.innerHTML = emptyState('chart', '조회된 투자수익 없음', '선택한 기간에 상환된 정산채권이 없음.');""",
    """    box.innerHTML = emptyState('chart', '조회된 투자수익 없음');""", 'empty/invest-profit')
rep("""        emptyState('search', '검색 결과 없음', '다른 조건으로 다시 조회.',""",
    """        emptyState('search', '검색 결과 없음',""", 'empty/merchants')
rep("""    box.innerHTML = emptyState('doc', '보관된 계약문서 없음', '정산채권 양수 후 재양도합의서가 보관됨.',""",
    """    box.innerHTML = emptyState('doc', '보관된 계약문서 없음',""", 'empty/contracts')

rep("""              <p class="issue-note">표기 금액·상호·서명값은 전부 예시이며 실제 발급 기록이 아니다. 전자문서에 ㈜페이허그 인증서 서명값을 표시함. 인증서 발행기관 검증 회신전문은 형식·전달 경로 미정의 — 확인 대상.</p>""",
    """              <p class="issue-note">※ 예시값 — 표기 금액·상호·서명값은 전부 예시이며 실제 발급 기록이 아니다.</p>""",
    'issue-note 예시 고지만')
rep("""        <p class="pw-note" data-when-not="done">비밀번호 변경 후 기존 세션 처리는 확인 대상.</p>\n""",
    '', 'pw-note 제거')
rep("""          <p class="done-desc">새 비밀번호로 변경 완료. 기존 세션 처리는 확인 대상.</p>""",
    """          <p class="done-desc">새 비밀번호로 변경 완료.</p>""", 'password done-desc')
rep("""      <p class="cert-desc">기준일 2026-08-27 시점의 가맹점별 투자자산 내역으로 전자문서를 발급함. 발급 문서에 ㈜페이허그 인증서 서명값을 표시함. 인증서 발행기관 검증 회신전문은 확인 대상.</p>""",
    """      <p class="cert-desc">기준일 2026-08-27 시점의 가맹점별 투자자산 내역으로 전자문서를 발급합니다.</p>""",
    'cert-desc 축약')
rep("""      <p class="modal-desc" style="margin:0">선택한 <b data-mount="aqc-count">2건</b>의 계약서에 전자서명함. 서명 수단은 확인 대상. 서명 후 취소 불가.</p>""",
    """      <p class="modal-desc" style="margin:0">선택한 <b data-mount="aqc-count">2건</b>의 계약서에 전자서명합니다. 서명 후에는 취소할 수 없습니다.</p>""",
    'aq 확인 모달')
rep("""            <span class="step-note">전자서명 진행 중. 서명 수단 확인 대상.</span>""",
    """            <span class="step-note">전자서명 진행 중.</span>""", 'step-note 서명')
rep("""        <p class="done-desc">정산금채권 양수도 계약 <b data-mount="aqd-count">2건</b> 서명 완료.<br>서명값은 계약기록에 보관됨. 인증서 발행기관 검증 회신전문의 형식·보관 경로는 확인 대상.</p>""",
    """        <p class="done-desc">정산금채권 양수도 계약 <b data-mount="aqd-count">2건</b> 서명 완료.<br>서명값은 계약기록에 보관됩니다.</p>""",
    'aq 완료 모달')

# 로그인 — '이번 설계(안) 범위 밖' 툴팁이 달린 목적지 없는 링크를 뺀다
rep("""      if(t.closest('.login-links')) showInfo('비밀번호 재발급은 페이허그 담당자에게 문의.');\n""",
    '', 'login-links 핸들러 제거')

io.open(P, 'w', encoding='utf-8').write(s)
print('\n'.join(done))
print('-- %d건 치환' % len(done))
