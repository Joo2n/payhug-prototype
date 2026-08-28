# -*- coding: utf-8 -*-
"""app.html 조립 — 화면·상태 전량을 한 파일에서 조작하는 단일 HTML 애플리케이션.

개별 HTML 34개는 Figma 임포트용 정적 원본으로 보존한다. 이 스크립트는 app.html만 새로 쓴다.
사이드바·산식 카드·용어 안내·쿠콘 본문·로그인 카드는 원본 파일에서 문자 그대로 옮긴다.
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import counts
import daily_ledger
import roster16_model as RM
import contract_text

ROOT = '/Users/semi/cursor/payhug-investor-admin'
OUT  = os.path.join(ROOT, 'app.html')

def R(f):
    return open(os.path.join(ROOT, f), encoding='utf-8').read()

def cut(s, a, b):
    """a 이후부터 b 직전까지."""
    i = s.index(a) + len(a)
    j = s.index(b, i)
    return s[i:j]

def dedent_block(s, n):
    return '\n'.join(l[n:] if l.startswith(' ' * n) else l for l in s.split('\n'))

# ── 원본에서 그대로 옮기는 블록 ────────────────────────────────
_tpl    = R('assets/template.html')
SIDEBAR = _tpl[_tpl.index('<aside class="sidebar">'):_tpl.index('</aside>') + 8]

# 메뉴 그룹 헤더를 <button> 으로 바꾼다 — 원본 AdminLayout.tsx:486 은 <button>, 셰브론(:494)이 그룹을 접는다.
# 정적 화면은 접힘 스크립트가 없어 template.html 원본을 그대로 두고, app.html 에서만 조작 가능하게 만든다.
_gi = [0]
def _grp(m):
    _gi[0] += 1
    return ('<button type="button" class="nav-group-label" data-act="nav-group" aria-expanded="true">'
            + m.group(1) + '</button>')
SIDEBAR = re.sub(r'<div class="nav-group-label">(.*?)</div>', _grp, SIDEBAR, flags=re.S)
assert _gi[0] == 3 and SIDEBAR.count('data-act="nav-group"') == 3, _gi[0]

_ia     = R('invest-assets.html')
FORMULA = cut(_ia, '<!-- 수익 산정 기준 -->\n', '\n\n  </main>').rstrip()

# ── 수익 산정 기준(예시) 카드 노출 스위치 ─────────────────────────
# 요율이 확정되기 전까지만 두는 카드다. 내릴 때는 아래를 False 로 바꾸고
#   python3 build_app.py
# 한 번 돌리면 투자 자산·투자 수익 두 화면에서 카드가 함께 빠진다. 다른 파일은 손대지 않는다.
# 정적 화면 9종에서도 함께 내리려면 fix12_static.py 의 SHOW_FORMULA 도 같이 False 로 둔다.
SHOW_FORMULA = True

_login  = R('login.html')
LOGINCARD = cut(_login, '<div class="login-wrap">\n\n', '\n\n</div>').rstrip()

_coocon = R('coocon.html')
COOCON  = cut(_coocon, '    <div class="link-wrap">', '\n  </main>').rstrip()
COOCON  = '<div class="link-wrap">' + COOCON

assert SIDEBAR.count('nav-item') == 8, SIDEBAR.count('nav-item')

# 쿠콘 관리 현금 — 메뉴를 누르면 중간 화면 없이 바로 We-bank 로 나간다(대표 미팅 2026-08-28 M-4).
# 정적 낱장 34개의 사이드바는 화면마다 같아야 해서 손대지 않는다. 통합본에서만 바깥으로 건다.
WEBANK = 'https://www.we-bank.co.kr/main_00100.act'
_kc = SIDEBAR.count('data-menu="kcoon" href="coocon.html"')
assert _kc == 1, _kc
SIDEBAR = SIDEBAR.replace('data-menu="kcoon" href="coocon.html"',
                          'data-menu="kcoon" href="%s" target="_blank" rel="noopener"' % WEBANK)
assert '0.11%' in FORMULA and '연 12%' in FORMULA and FORMULA.startswith('    <div class="card">')
FORMULA_BLOCK = ('        ' + dedent_block(FORMULA, 4).replace('\n', '\n        ')) if SHOW_FORMULA else ''

assert 'login-card' in LOGINCARD and 'login-note' not in LOGINCARD
assert 'We-bank 바로가기' in COOCON and COOCON.rstrip().endswith('</div>')

# ════════════════════════════════════════════════════════════════
# CSS — 개별 파일 인라인 정의를 한 벌로 정리. base.css·sheet.css는 <link>로 그대로 쓴다.
# ════════════════════════════════════════════════════════════════
CSS = r'''
  /* ── 화면 전환 골격 ───────────────────────────────────────── */
  /* base.css 의 .modal-backdrop·.action-bar·.toast 가 display:flex 로 선언돼 있어
     UA 기본값 [hidden]{display:none} 을 덮는다. 작성자 스타일로 다시 눌러 준다. */
  [hidden] { display: none !important; }
  .screen[hidden], [data-when][hidden], [data-when-not][hidden] { display: none !important; }
  body[data-view="acquisition-list"] .content { padding-bottom: 120px; }

  /* ── 상태 마커 (M-1 단일화: .badge + .state-badge) ────────── */
  .page-title .state-badge {
    vertical-align: middle; position: relative; top: -2px; margin-left: 8px;
    font-size: 12px; line-height: 16px; font-weight: 600;
  }

  /* ── 페이지 헤더 변형 · 기준일 pill (투자 자산 전용) ───────── */
  .page-header.row-between { align-items: flex-start; }
  .base-date {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 6px 12px; background: #fff;
    border: 1px solid var(--gray-200); border-radius: 8px;
    font-size: 14px; line-height: 20px; color: var(--secondary); white-space: nowrap;
  }
  .base-date .mono { color: var(--gray-700); font-weight: 500; }

  /* ── 표 카드 헤더·합계·하단 안내 ──────────────────────────── */
  .tbl-head {
    display: flex; align-items: center; justify-content: space-between; gap: 12px;
    padding: 16px 20px; border-bottom: 1px solid var(--gray-100);
  }
  .tbl-head h2 { font-size: 14px; line-height: 20px; font-weight: 600; color: var(--gray-900); margin: 0; }
  .tbl-head .card-title { margin: 0; }
  .tbl-head .left { display: flex; align-items: center; gap: 16px; }
  .tbl-head .toggle { margin-bottom: 0; }
  .tbl-head .actions { display: flex; align-items: center; gap: 8px; }
  .tbl-head-bar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 16px 20px; border-bottom: 1px solid var(--gray-100);
  }
  .tbl tr.total-row td {
    background: var(--gray-50); border-top: 1px solid var(--gray-100);
    font-weight: 700; color: var(--gray-900);
  }
  .tbl tfoot td { background: var(--gray-50); border-top: 1px solid var(--gray-100); border-bottom: 0; font-weight: 700; color: var(--gray-900); }
  /* 합계 행의 가중평균 표기 — 괄호로 숫자 옆에 붙이면 그 칸만 줄바꿈이 나 행이 어긋난다.
     숫자는 첫 줄에 그대로 두고 아래 줄에 작게 얹어 열 사이 기준선을 맞춘다. */
  .avg-sub { display: block; font-size: 10px; line-height: 12px; font-weight: 400; color: var(--gray-400); font-family: var(--font-sans); }
  .tbl-count { font-size: 12px; color: var(--gray-400); margin-left: 8px; }
  .sel-pill { margin-left: 8px; font-weight: 600; }


  /* ── 체크박스·선택 행 ─────────────────────────────────────── */
  .chk { width: 16px; height: 16px; accent-color: var(--primary); flex-shrink: 0; cursor: pointer; vertical-align: middle; }
  .chk:disabled { cursor: default; opacity: 0.6; }
  .tbl tbody tr.selected td { background: var(--primary-50); }

  /* ── 빈 상태 ──────────────────────────────────────────────
     표는 base.css `.tbl .empty` (= px-5 py-16 text-center text-secondary) 한 줄만 쓴다.
     표가 아닌 목록만 아래 한 줄을 쓴다 — 원본 settlement/overview/BatchDetailTab.tsx:341
     `<div className="p-8 text-center text-gray-400">해당 기간에 정산 내역이 없습니다.</div>` */
  .empty-cell { padding: 64px 20px; text-align: center; color: var(--secondary); }

  /* ── 안내 배너 초록 (L-4) ─────────────────────────────────── */
  .notice-green { background: var(--primary-50); border-color: var(--primary-200); color: var(--primary-700); }

  /* ── 파일 링크 ────────────────────────────────────────────── */
  .file-link { display: inline-flex; align-items: center; gap: 6px; font-weight: 500; color: var(--primary-600); text-decoration: none; cursor: pointer; }
  .file-link:hover { text-decoration: underline; }
  .file-link svg { width: 16px; height: 16px; flex-shrink: 0; }

  /* ── 투자 수익 지표 블록 ──────────────────────────────────── */
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

  /* ── 조건 칩 ──────────────────────────────────────────────── */
  .chip-row { display: flex; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }
  .chip-label { font-size: 12px; line-height: 16px; color: var(--secondary); }
  .chip {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 4px 10px; border-radius: 9999px;
    background: var(--primary-50); border: 1px solid var(--primary-200); color: var(--primary-700);
    font-size: 12px; line-height: 16px; font-weight: 500;
  }
  .chip button { display: flex; background: none; border: 0; padding: 0; color: var(--primary-600); cursor: pointer; }
  .chip svg { width: 12px; height: 12px; }
  .chip-clear { background: none; border: 0; padding: 0; cursor: pointer; font-size: 12px; line-height: 16px; color: var(--gray-500); text-decoration: underline; }

  /* ── 역전 범위 안내문 (DateRangeFilter.tsx:138-140 대응) ──── */
  .range-warn { margin: 8px 0 0; font-size: 12px; line-height: 16px; color: var(--red-500); }

  /* ── 메뉴 그룹 접힘 (AdminLayout.tsx:486, 494) ─────────────── */
  .nav-group-label { background: none; border: 0; width: 100%; text-align: left; cursor: pointer; font-family: inherit; }
  .nav-group-label svg { transition: transform 0.2s cubic-bezier(.4, 0, .2, 1); }
  .nav-group.collapsed .nav-group-label svg { transform: rotate(-90deg); }
  .nav-group.collapsed .nav-item { display: none; }

  /* ── 인라인 스피너 (CommonLoading.tsx:78-95 실측 규격) ─────── */
  @keyframes commonSpinner { to { transform: rotate(360deg); } }
  .spinner-inline {
    display: inline-block; width: 20px; height: 20px; border-radius: 50%;
    border: 2px solid rgba(0,0,0,0.08); border-top-color: #65c826;
    animation: commonSpinner 0.6s linear infinite; vertical-align: -4px;
  }
  .btn .spinner-inline { border-color: rgba(255,255,255,0.35); border-top-color: #fff; margin-right: 6px; }

  /* ── 토스트 닫기 (Toast.tsx:45-51 — duration 0 일 때만 렌더) ─ */
  .toast .t-close { flex-shrink: 0; display: flex; padding: 2px; border: 0; background: none; border-radius: 4px; cursor: pointer; color: var(--green-600); }
  .toast .t-close:hover { color: var(--green-800); }
  .toast-info .t-close { color: var(--primary-600); }
  .toast .t-close svg { width: 16px; height: 16px; }

  /* ── 서명 목록·하단 액션바 ────────────────────────────────── */
  .sign-row { display: flex; align-items: center; gap: 16px; padding: 16px 24px; border-bottom: 1px solid var(--gray-50); }
  .sign-row:last-child { border-bottom: 0; }
  .sign-row.selected { background: var(--primary-50); }
  .sign-row .m-name { font-size: 14px; font-weight: 600; color: var(--gray-900); }
  .sign-row .m-date { font-size: 12px; color: var(--gray-400); margin-top: 2px; }
  .sign-row .m-date .mono { color: var(--gray-500); }
  .sign-row.done .m-name { color: var(--gray-500); }
  .doc-link { font-size: 14px; font-weight: 500; color: var(--primary-600); text-decoration: none; white-space: nowrap; cursor: pointer; }
  .doc-link:hover { text-decoration: underline; }
  /* ── 계약서보기 — 전자계약서로 넘어가기 전에 계약서 내용을 읽는 자리 ─────
     대표 미팅 2026-08-28 M-1. `서명하기`와 별개 액션이며 둘 다 목록 행에 있다. */
  .modal.lg { max-width: 672px; }                          /* max-w-2xl */
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
  /* 서명 버튼 — 스토리보드 15는 목록과 같은 카드 안, 가로 가운데에 둔다(x2.99 w2.36 / 카드 x1.69 w5.59).
     화면 하단 고정 바로 두면 목록이 길 때 뷰포트 밖으로 밀려 보이지 않는다. */
  /* 선택 건수는 목록 아래 왼쪽, 서명 버튼은 그대로 가운데 — 쪽번호 줄과 같은 3열 격자다.
     원본 어드민의 다중선택 액션 바도 건수를 왼쪽에 둔다(PreSettlementTab.tsx:1214·1264). */
  .sign-foot {
    display: grid; grid-template-columns: 1fr auto 1fr; align-items: center;
    padding: 20px 24px 24px; border-top: 1px solid var(--gray-100); background: var(--gray-50);
  }
  .sign-foot .sel-count { justify-self: start; font-size: 13px; color: var(--gray-600); }
  .sign-foot .sel-count b { color: var(--gray-900); }
  .sign-foot .btn { min-width: 240px; justify-content: center; padding: 12px 40px; font-size: 16px; border-radius: 12px; }
  .list-tools { display: flex; align-items: center; gap: 8px; }

  /* ── 인증서 서명 진행 인디케이터 ──────────────────────────── */
  @keyframes ph-spin { to { transform: rotate(360deg); } }
  .spin-wrap { display: flex; flex-direction: column; align-items: center; gap: 12px; padding: 8px 0 4px; }
  .spinner { width: 56px; height: 56px; border-radius: 50%; border: 4px solid var(--gray-100); border-top-color: var(--primary); animation: ph-spin 0.9s linear infinite; }
  .spin-label { font-size: 14px; line-height: 20px; font-weight: 600; color: var(--gray-900); }
  .step-list { border: 1px solid var(--gray-100); background: var(--gray-50); border-radius: 12px; padding: 8px 16px; }
  .step { display: flex; align-items: flex-start; gap: 12px; padding: 10px 0; }
  .step + .step { border-top: 1px solid var(--gray-100); }
  .step-num {
    width: 22px; height: 22px; border-radius: 50%; flex-shrink: 0; margin-top: 1px;
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 700; background: var(--gray-200); color: var(--gray-500);
  }
  .step-num svg { width: 12px; height: 12px; }
  .step.done .step-num { background: var(--emerald-100); color: var(--emerald-700); }
  .step.now .step-num { background: var(--primary); color: #fff; }
  .step-text { font-size: 14px; line-height: 20px; color: var(--gray-400); }
  .step.done .step-text { color: var(--gray-600); }
  .step.now .step-text { color: var(--gray-900); font-weight: 600; }
  .step-note { display: block; font-size: 12px; line-height: 16px; font-weight: 400; color: var(--gray-400); margin-top: 2px; }

  /* ── 모달 부속 ────────────────────────────────────────────── */
  .modal .done-head { text-align: center; }
  .modal .done-icon {
    width: 56px; height: 56px; border-radius: 50%; margin: 0 auto 16px;
    background: var(--emerald-100); color: var(--emerald-600);
    display: flex; align-items: center; justify-content: center;
  }
  .modal .done-icon svg { width: 28px; height: 28px; }
  .modal .done-title { font-size: 18px; line-height: 28px; font-weight: 700; color: var(--gray-900); margin: 0 0 8px; }
  .modal .done-desc { font-size: 14px; line-height: 22px; color: var(--gray-500); margin: 0; }
  .modal .done-list { background: var(--gray-50); border: 1px solid var(--gray-100); border-radius: 12px; padding: 8px 16px; }
  .modal .done-item { display: flex; align-items: center; gap: 8px; padding: 8px 0; }
  .modal .done-item + .done-item { border-top: 1px solid var(--gray-100); }
  .modal .done-item svg { width: 16px; height: 16px; flex-shrink: 0; color: var(--emerald-600); }
  .modal .done-item .n { flex: 1; font-size: 14px; line-height: 20px; font-weight: 600; color: var(--gray-900); }
  .modal .done-item .d { font-size: 12px; line-height: 16px; color: var(--gray-400); }
  .modal-sign-list { background: var(--gray-50); border: 1px solid var(--gray-100); border-radius: 12px; padding: 8px 16px; }
  .modal-sign-list .row-between { padding: 6px 0; }
  .modal-sign-list .row-between + .row-between { border-top: 1px solid var(--gray-100); }
  .modal-sign-list .n { font-size: 14px; font-weight: 600; color: var(--gray-900); }
  .modal-sign-list .d { font-size: 12px; color: var(--gray-400); }
  .cert-desc { font-size: 13px; line-height: 20px; color: var(--gray-600); margin: 0; }
  .cert-info { margin: 0; font-size: 13px; line-height: 20px; }
  .cert-info dt { float: left; clear: left; width: 88px; color: var(--gray-500); padding: 5px 0; }
  .cert-info dd { margin: 0 0 0 88px; color: var(--gray-800); font-weight: 500; padding: 5px 0; }
  .url-box { background: var(--gray-50); border: 1px solid var(--gray-200); border-radius: 12px; padding: 12px 16px; }
  .url-box .k { display: block; font-size: 12px; line-height: 16px; color: var(--secondary); margin-bottom: 4px; }
  .url-box .v { font-size: 13px; line-height: 20px; color: var(--gray-800); word-break: break-all; }

  /* ── 토스트 2행 구성 ──────────────────────────────────────── */
  .toast .t-ico { width: 22px; height: 22px; flex-shrink: 0; margin-top: 1px; }
  .toast .t-main { margin: 0; font-size: 15px; line-height: 22px; font-weight: 700; }
  .toast .t-sub { margin: 2px 0 0; font-size: 13px; line-height: 18px; font-weight: 400; opacity: 0.85; }
  .btn-excel.is-done { background: var(--emerald-700); }
  .btn-excel.is-done:hover { background: var(--emerald-700); }
  .btn-excel.armed { box-shadow: 0 0 0 3px var(--emerald-100), var(--shadow-card); font-weight: 600; }
'''

CSS += r'''
  /* ── 쿠콘 링크 카드 ───────────────────────────────────────── */
  .link-wrap { max-width: 640px; margin: 40px auto 0; }
  .link-card { padding: 48px 40px; text-align: center; }
  .link-icon {
    width: 56px; height: 56px; border-radius: 16px; margin: 0 auto 20px;
    background: var(--primary-50); color: var(--primary-600);
    display: flex; align-items: center; justify-content: center;
  }
  .link-icon svg { width: 26px; height: 26px; }
  .link-title { font-size: 18px; line-height: 28px; font-weight: 700; color: var(--gray-900); margin: 0 0 8px; }
  .link-desc { font-size: 14px; line-height: 22px; color: var(--gray-500); margin: 0 0 24px; }
  .link-foot { font-size: 12px; line-height: 16px; color: var(--gray-400); margin: 16px 0 0; }
  .ref-list { display: flex; flex-direction: column; gap: 10px; }
  .ref-item { display: flex; align-items: center; gap: 10px; font-size: 14px; line-height: 20px; color: var(--gray-700); }
  .ref-item svg { width: 16px; height: 16px; flex-shrink: 0; color: var(--emerald-600); }

  /* ── 비밀번호 변경 폼 ─────────────────────────────────────────
     치수·색·문구 출처 = 실제 프론트
       payhug-merchant-web/components/PasswordInput.tsx
       payhug-merchant-web/app/my-info/change-password/page.tsx
     필드 h62 · r8 · bg #f7faf6 · 테두리 1px
       (오류 #FF383C · 충족 #9FE870 · 포커스 #C9E9B4 · 그 외 투명)
     메시지 칸은 min-height 44px + padding-top 8px 로 늘 잡혀 있다 —
     문구가 붙고 떨어져도 아래 필드가 밀리지 않는다. */
  .pw-card { max-width: 480px; margin: 0 auto; }
  .pw-form { display: flex; flex-direction: column; gap: 12px; }
  .pw-field { display: flex; flex-direction: column; gap: 4px; }
  .pw-field label { font-size: 14.4px; line-height: 20px; color: #434548; }
  .pw-box {
    position: relative; display: flex; align-items: center;
    height: 62px; padding: 0 16px; border-radius: 8px;
    background: #f7faf6; border: 1px solid transparent;
    transition: border-color 150ms ease;
  }
  .pw-box:focus-within { border-color: #C9E9B4; }
  .pw-field.is-ok    .pw-box, .pw-field.is-ok    .pw-box:focus-within { border-color: #9FE870; }
  .pw-field.is-error .pw-box, .pw-field.is-error .pw-box:focus-within { border-color: #FF383C; }
  .pw-box input {
    flex: 1; min-width: 0; padding: 0; border: 0; outline: 0; background: transparent;
    font-family: inherit; font-size: 16px; line-height: 24px; color: #000;
  }
  .pw-box input::placeholder { color: #a0a4b8; }
  .pw-eye {
    flex-shrink: 0; margin-left: 8px; width: 22px; height: 22px; padding: 0;
    border: 0; background: none; cursor: pointer; color: #9296ac;
    display: flex; align-items: center; justify-content: center;
  }
  .pw-eye svg { width: 20px; height: 20px; }
  /* Caps Lock 안내 — 필드 위에 붙는 말풍선 (PasswordInput.tsx:97-110) */
  .pw-caps {
    position: absolute; left: 0; top: -45px; z-index: 10;
    display: flex; align-items: center; gap: 8px;
    padding: 8px 12px; border-radius: 8px; background: #333; color: #fff;
    font-size: 12px; line-height: 16px; white-space: nowrap;
    box-shadow: 0 4px 12px rgba(0,0,0,0.18);
  }
  .pw-caps svg { width: 16px; height: 16px; flex-shrink: 0; }
  .pw-caps::after {
    content: ''; position: absolute; left: 16px; bottom: -4px;
    width: 8px; height: 8px; background: #333; transform: rotate(45deg);
  }
  .pw-msgbox { min-height: 44px; padding-top: 8px; }
  .pw-rules { display: flex; flex-wrap: wrap; gap: 9px 14px; }
  .pw-rules .r { display: flex; align-items: center; gap: 5px; font-size: 12px; line-height: 16px; color: #7E8299; }
  .pw-rules .r.ok { color: #28A745; }
  .pw-rules .r .mark { width: 15px; height: 15px; flex-shrink: 0; display: inline-flex; align-items: center; justify-content: center; }
  .pw-rules .r .mark svg { width: 15px; height: 15px; }
  .pw-rules .r .dot { display: block; width: 5px; height: 5px; border-radius: 50%; background: #C7CAD6; }
  .pw-msg { display: flex; align-items: center; gap: 5px; font-size: 12.5px; line-height: 1.45; }
  .pw-msg.mt { margin-top: 9px; }
  .pw-msg svg { width: 15px; height: 15px; flex-shrink: 0; }
  .pw-msg.t-default { color: #7E8299; font-weight: 400; }
  .pw-msg.t-error   { color: #FF383C; font-weight: 600; }
  .pw-msg.t-success { color: #28A745; font-weight: 600; }
  /* 제출 버튼 — .btn 계열을 쓰지 않는다. base.css 의 .btn:disabled 가 !important 로
     회색을 덮어써서 원본의 연둣빛 비활성색이 나오지 않기 때문이다. */
  .pw-submit {
    width: 100%; margin-top: 12px; padding: 16px 0; border: 0; border-radius: 12px;
    font-family: inherit; font-size: 17.6px; font-weight: 500;
    background: #9fe870; color: #163300; cursor: pointer;
    transition: background-color 150ms ease;
  }
  .pw-submit:hover:not(:disabled) { background: #8cdb5e; }
  .pw-submit:disabled { background: rgba(159,232,112,0.3); color: rgba(22,51,0,0.3); cursor: not-allowed; }

  /* ── 증명서 ───────────────────────────────────────────────── */
  .cert-layout { display: flex; align-items: flex-start; gap: 24px; }
  .cert-main { flex: 1; min-width: 0; }
  .cert-aside { width: 300px; flex-shrink: 0; }
  .doc-card {
    background: #fff; border: 1px solid var(--gray-200); border-radius: 4px;
    box-shadow: var(--shadow-card);
    max-width: 720px; margin: 0 auto; padding: 64px 72px;
    min-height: 1018px; display: flex; flex-direction: column;
  }
  .doc-title {
    text-align: center; font-size: 24px; line-height: 32px; font-weight: 700;
    color: var(--gray-900); letter-spacing: 0.25em; text-indent: 0.25em; margin: 0 0 32px;
  }
  .doc-meta { display: flex; justify-content: flex-end; gap: 24px; font-size: 13px; line-height: 20px; color: var(--gray-600); margin-bottom: 16px; }
  .doc-meta .k { font-weight: 600; color: var(--gray-500); margin-right: 6px; }
  .doc-tbl { width: 100%; border-collapse: collapse; font-size: 13px; line-height: 18px; }
  .doc-tbl th, .doc-tbl td { border: 1px solid var(--gray-200); padding: 8px 12px; color: var(--gray-700); }
  .doc-tbl th { background: var(--gray-50); text-align: center; font-size: 12px; font-weight: 600; color: var(--gray-600); }
  .doc-tbl td.num { text-align: right; font-family: var(--font-mono); font-variant-numeric: tabular-nums; }
  .doc-tbl tfoot td { background: var(--gray-50); font-weight: 700; color: var(--gray-900); }
  /* 서명 블록 — 작성자 오른쪽에 서명값(스토리보드 S6) */
  .doc-sign { margin-top: auto; padding-top: 48px; border-top: 1px solid var(--gray-100); }
  .doc-sign .sign-row2 { display: flex; align-items: baseline; justify-content: center; gap: 20px; margin: 24px 0 16px; flex-wrap: wrap; }
  .doc-sign .author { font-size: 15px; line-height: 22px; font-weight: 600; color: var(--gray-900); margin: 0; }
  .doc-sign .sig-label { font-size: 11px; font-weight: 600; color: var(--gray-500); margin: 0 6px 0 0; }
  .doc-sign .sig-value { font-family: var(--font-mono); font-size: 10px; line-height: 14px; color: var(--gray-400); word-break: break-all; max-width: 320px; margin: 0; }
  .doc-sign .sign-val { display: flex; align-items: baseline; }
  .issue-meta { margin: 0 0 20px; font-size: 12px; line-height: 18px; }
  .issue-meta div { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid var(--gray-100); }
  .issue-meta div:last-child { border-bottom: 0; }
  .issue-meta .k { color: var(--gray-500); }
  .issue-meta .v { color: var(--gray-700); font-weight: 500; }

  /* ── 로그인 (사이드바 없는 독립 화면) ─────────────────────── */
  .login-wrap {
    min-height: 100vh; background: var(--gray-50);
    display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 40px 16px;
  }
  .login-card { width: 100%; max-width: 400px; padding: 36px 32px 28px; }
  .login-logo { display: flex; align-items: center; justify-content: center; gap: 12px; margin-bottom: 8px; }
  .login-logo .logo-mark { display: block; width: 48px; height: 48px; border-radius: 12px; flex-shrink: 0; }
  .login-logo .wordmark { font-size: 22px; line-height: 30px; font-weight: 700; color: var(--gray-900); white-space: nowrap; }
  .login-logo .wordmark em { font-style: normal; color: var(--primary-600); }
  .login-sub { text-align: center; font-size: 13px; line-height: 20px; color: var(--secondary); margin: 0 0 28px; }
  .login-field { margin-bottom: 16px; }
  .login-field label { display: block; font-size: 13px; font-weight: 600; color: var(--gray-700); margin-bottom: 6px; }
  .login-field .input { width: 100%; padding: 11px 16px; border-radius: 12px; background: #fff; border-color: var(--gray-300); }
  .login-submit { width: 100%; padding: 12px 0; border-radius: 12px; margin-top: 8px; }
  .login-links { text-align: center; margin-top: 16px; }
  .login-links a { font-size: 12px; line-height: 16px; color: var(--gray-500); text-decoration: none; cursor: pointer; }
  .login-links a:hover { color: var(--gray-700); text-decoration: underline; }
  .login-links .link-off { font-size: 12px; line-height: 16px; color: var(--gray-300); text-decoration: none; cursor: not-allowed; }

  /* ── 랜딩 갤러리 ──────────────────────────────────────────── */
  .wrap { max-width: 1024px; margin: 0 auto; padding: 56px 32px 64px; }
  .hero { display: flex; align-items: center; gap: 16px; }
  .hero .logo-mark { display: block; width: 48px; height: 48px; border-radius: 12px; flex-shrink: 0; }
  .hero h1 { font-size: 26px; line-height: 34px; font-weight: 700; color: var(--gray-900); margin: 0; }
  .hero h1 em { font-style: normal; color: var(--primary-600); }
  .hero .sub { font-size: 14px; line-height: 20px; color: var(--secondary); margin: 4px 0 0; }
  .hero-date {
    margin-left: auto; align-self: flex-start; font-size: 12px; line-height: 16px; color: var(--gray-400);
    font-family: var(--font-mono); font-variant-numeric: tabular-nums;
    background: #fff; border: 1px solid var(--gray-200); border-radius: 6px; padding: 4px 10px;
  }
  .gallery { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-top: 20px; }
  .shot-card {
    display: block; text-decoration: none; cursor: pointer; text-align: left; width: 100%;
    background: #fff; border-radius: 16px; padding: 20px 24px;
    box-shadow: var(--shadow-card); border: 1px solid var(--gray-100);
    transition: box-shadow 0.15s var(--ease-default), border-color 0.15s var(--ease-default), transform 0.15s var(--ease-default);
  }
  .shot-card:hover { box-shadow: var(--shadow-card-hover); border-color: var(--primary-200); transform: translateY(-2px); }
  .shot-top { display: flex; align-items: center; gap: 12px; }
  .shot-icon {
    width: 36px; height: 36px; border-radius: 10px; flex-shrink: 0;
    background: var(--primary-50); color: var(--primary-600);
    display: flex; align-items: center; justify-content: center;
  }
  .shot-icon svg { width: 18px; height: 18px; }
  .shot-name { font-size: 16px; line-height: 22px; font-weight: 700; color: var(--gray-900); }
  .shot-top .badge.sm { margin-left: auto; flex-shrink: 0; }
  .shot-desc { font-size: 13px; line-height: 19px; color: var(--gray-500); margin: 12px 0 0; }
  .sec-head { display: flex; align-items: baseline; gap: 10px; margin: 36px 0 0; }
  .sec-head h2 { font-size: 16px; line-height: 24px; font-weight: 700; color: var(--gray-900); margin: 0; }
  .sec-head .sec-note { font-size: 12px; line-height: 16px; color: var(--gray-400); }

  /* ── 페이지네이션 — 쪽번호는 가운데, 건수는 같은 줄 왼쪽 ────────
     원본 app/activity-logs/page.tsx:339 · app/sales/[bizNo]/page.tsx:1243 이 justify-center,
     components/LockAccountDeposits.tsx:435 이 같은 줄 맨 왼쪽에 총 건수를 둔다. 둘을 겹쳐 쓴다. */
  .pagination.with-count { display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; }
  .pagination.with-count .pg-count { justify-self: start; font-size: 12px; color: var(--gray-500); }
  .pagination.with-count .pg-nums { display: flex; align-items: center; gap: 4px; justify-self: center; }
  .pg-size { display: inline-flex; align-items: center; gap: 6px; font-size: 12px; color: var(--gray-500); }
  .input.sz { padding: 4px 24px 4px 10px; font-size: 12px; height: 28px; border-radius: 8px; }
  .pagination.with-count .sel-pill { margin-left: 0; }

  /* ── 쿠콘 안내 카드 — 조회 가능 내역을 같은 카드 아래쪽에 잇는다 ── */
  .link-check { width: 100%; margin-top: 24px; padding-top: 20px; border-top: 1px solid var(--gray-100); text-align: left; }
  .link-check .card-title { display: block; margin: 0 0 12px; }

  /* ── 투자 시뮬레이션 ────────────────────────────────────────
     규격은 payhug-admin-web/app/settlement/simulation/page.tsx 의 유틸리티 값을 옮긴 것이다.
     :212 grid-cols-2 gap-4 → 항목이 6개라 3열, :265 flex items-center gap-3 bg-gray-50 rounded-lg px-3 py-2 → .sim-row,
     :299-302 text-xs text-gray-500 pt-1 → .sim-total, :306-312 w-full py-3 rounded-xl font-semibold → .sim-run. */
  .sim-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
  .sim-grid .input { width: 100%; }
  .sim-rows { display: flex; flex-direction: column; gap: 8px; }
  .sim-row { display: flex; align-items: center; gap: 12px; background: var(--gray-50); border-radius: 8px; padding: 8px 12px; }
  .sim-row .input { background: #fff; }
  .sim-head {
    display: flex; align-items: center; gap: 12px; padding: 0 12px 4px;
    font-size: 12px; line-height: 16px; color: var(--secondary);
  }
  .sim-no    { width: 24px; flex-shrink: 0; font-size: 12px; line-height: 16px; color: var(--gray-400); }
  .sim-plat  { width: 112px; flex-shrink: 0; }
  .sim-amt   { width: 160px; flex-shrink: 0; text-align: right; font-family: var(--font-mono); font-variant-numeric: tabular-nums; }
  .sim-unit  { width: 16px; flex-shrink: 0; font-size: 12px; line-height: 16px; color: var(--gray-400); }
  .sim-date  { width: 150px; flex-shrink: 0; }
  .sim-days  { width: 64px; flex-shrink: 0; text-align: right; font-size: 12px; line-height: 16px; color: var(--gray-500); font-variant-numeric: tabular-nums; }
  .sim-del {
    margin-left: auto; background: none; border: 0; padding: 0 4px;
    font-size: 14px; line-height: 20px; color: var(--red-400);
    transition: color 0.15s var(--ease-default);
  }
  .sim-del:hover { color: var(--red-600); }
  .sim-total { font-size: 12px; line-height: 16px; color: var(--gray-500); padding-top: 12px; }
  .sim-run {
    display: block; width: 100%; padding: 12px 20px; border-radius: 12px;
    background: var(--primary); color: #fff; font-size: 14px; line-height: 20px; font-weight: 600;
    margin-bottom: 24px;
  }
  .sim-run:hover:not(:disabled) { background: var(--primary-600); }
  .sim-run:disabled { background: var(--gray-300); color: #fff; cursor: not-allowed; }
  .tbl tr.sim-skip td { color: var(--gray-400); font-style: italic; }
  .tbl tr.sim-skip td .strong, .tbl tr.sim-skip td .name { color: var(--gray-400); font-weight: 400; }
'''

# ════════════════════════════════════════════════════════════════
# SVG (원본 파일에서 그대로 옮긴 path — 신규 아이콘 도입 없음)
# ════════════════════════════════════════════════════════════════
def sv(d, w='2', cls='', style=''):
    c = ' class="%s"' % cls if cls else ''
    st = ' style="%s"' % style if style else ''
    return ('<svg%s%s fill="none" stroke="currentColor" viewBox="0 0 24 24">'
            '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="%s" d="%s"/></svg>' % (c, st, w, d))

D_EXCEL  = 'M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z'
D_DOC    = 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z'
D_CHECKC = 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z'
D_CHECK  = 'M5 13l4 4L19 7'
D_X      = 'M6 18L18 6M6 6l12 12'
D_LEFT   = 'M15 19l-7-7 7-7'
D_RIGHT  = 'M9 5l7 7-7 7'
D_INFO   = 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
D_DL     = 'M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4'
D_GRID   = 'M3 10h18M3 15h18M9 5v14M15 5v14M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z'
D_EXT    = 'M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14'
D_CARD   = 'M3 10h18M7 15h1m4 0h1m-7 4h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z'
D_TREND  = 'M13 7h8m0 0v8m0-8l-8 8-4-4-6 6'
D_USERS  = ('M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857'
            'M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z')
D_CARDS  = 'M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z'
D_COIN   = 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
D_LOCK   = 'M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z'
D_SHIELD = ('M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9'
            'c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z')
D_WARN   = 'M12 9v3m0 3h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z'
D_ERR    = 'M12 9v3m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
D_CHEV   = 'M19 9l-7 7-7-7'

EXCEL_BTN_INNER = sv(D_EXCEL) + '\n            엑셀 다운로드'

# ════════════════════════════════════════════════════════════════
# 화면 셸 — 정적 크롬 + JS 렌더 마운트
# ════════════════════════════════════════════════════════════════
def xls_shell(sid, back, backlabel, title):
    return '''
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
      </section>''' % (sid, back, back, sv(D_LEFT), backlabel, title)


SCREENS_HTML = '''
      <!-- ═════════ 투자 자산 ═════════ -->
      <section class="screen" data-screen="invest-assets" data-state="default" hidden>
        <div class="page-header row-between">
          <div>
            <h1 class="page-title">투자 자산<span data-state-mark></span></h1>
          </div>
          <div class="base-date">기준일 <span class="mono">2026-08-27</span></div>
        </div>

        <div class="summary-grid" data-mount="ia-summary"></div>

        <div class="tbl-wrap mb-6">
          <div class="tbl-head">
            <h2>현황</h2>
            <div class="actions">
              <button class="btn btn-excel" data-act="xls-open" data-xls="assets-status">{EX}</button>
            </div>
          </div>
          <div class="tbl-scroll" data-mount="ia-status-wrap"><table class="tbl" data-mount="ia-status"></table></div>
        </div>

        <div class="tbl-wrap mb-6">
          <div class="tbl-head">
            <h2>가맹점별 투자자산</h2>
            <div class="actions">
              <span data-mount="ia-size"></span>
              <button class="btn btn-excel" data-act="xls-open" data-xls="assets-merchant" data-mount="ia-xls-merchant">{EX}</button>
              <button class="btn btn-outline" data-act="cert-open" data-mount="ia-cert">{CERTICO}
                증명서 다운로드</button>
            </div>
          </div>
          <div data-mount="ia-merch"></div>
          <div data-mount="ia-merch-page"></div>
        </div>

{FORMULA}

      </section>

      <!-- ═════════ 투자자산 증명서 ═════════ -->
      <section class="screen" data-screen="certificate" data-state="default" hidden>
        <a class="back-link" href="invest-assets.html" data-nav="invest-assets">{LEFT} 투자 자산</a>
        <div class="page-header">
          <h1 class="page-title">가맹점별 투자자산 증명서<span data-state-mark></span></h1>
        </div>
        <div class="cert-layout">
          <div class="cert-main">
            <div class="doc-card">
              <h2 class="doc-title">투자자산 현황</h2>
              <div class="doc-meta">
                <span><span class="k">투자자</span>㈜테스트인베스트</span>
                <span><span class="k">작성일자</span><span class="mono">2026-08-27</span></span>
              </div>
              <table class="doc-tbl" data-mount="cert-tbl"></table>
              <div class="doc-sign">
                <div class="sign-row2">
                  <p class="author">작성자: ㈜페이허그</p>
                  <div class="sign-val"><span class="sig-label">서명</span><span class="sig-value">kd568w7sg9apt86ag6ejg8atu73aat8tag8ata6agje8s7</span></div>
                </div>
              </div>
            </div>
          </div>
          <aside class="cert-aside">
            <div class="card">
              <h2 class="card-title">발급 안내</h2>
              <div class="issue-meta">
                <div><span class="k">작성일자</span><span class="v mono">2026-08-27</span></div>
                <div><span class="k">투자자</span><span class="v">㈜테스트인베스트</span></div>
                <div><span class="k">대상 가맹점</span><span class="v" data-mount="cert-count">16개</span></div>
              </div>
              <a class="btn btn-primary" style="width:100%" href="assets/docs/투자자산증명서_20260827.pdf" download="투자자산증명서_20260827.pdf" data-act="cert-pdf">{DLICO}
                PDF 다운로드</a>
            </div>
          </aside>
        </div>
      </section>
'''.replace('{EX}', EXCEL_BTN_INNER) \
   .replace('{CERTICO}', sv(D_DOC, '1.8', 'icon')) \
   .replace('{LEFT}', sv(D_LEFT, '2', '', 'width:14px;height:14px')) \
   .replace('{DLICO}', sv(D_DL, '2', 'icon')) \
   .replace('{FORMULA}', FORMULA_BLOCK)

SCREENS_HTML += '''
      <!-- ═════════ 투자 수익 ═════════ -->
      <section class="screen" data-screen="invest-profit" data-state="default" hidden>
        <div class="page-header">
          <h1 class="page-title">투자 수익<span data-state-mark></span></h1>
        </div>

        <div class="search-bar">
          <div class="preset-row">
            <button class="preset-btn" data-act="preset" data-preset="week"  data-for="daily">일주일</button>
            <button class="preset-btn" data-act="preset" data-preset="month" data-for="daily">금월</button>
            <button class="preset-btn" data-act="preset" data-preset="w4"    data-for="weekly">4주</button>
            <button class="preset-btn" data-act="preset" data-preset="w12"   data-for="weekly">12주</button>
            <button class="preset-btn" data-act="preset" data-preset="m3"    data-for="monthly">3개월</button>
            <button class="preset-btn" data-act="preset" data-preset="m6"    data-for="monthly">6개월</button>
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
          <p class="range-warn" data-mount="pf-warn" hidden>시작일은 종료일보다 이후일 수 없습니다.</p>
          <div class="toggle">
            <button class="toggle-btn" data-act="pf-gran" data-gran="daily">일별</button>
            <button class="toggle-btn" data-act="pf-gran" data-gran="weekly">주별</button>
            <button class="toggle-btn" data-act="pf-gran" data-gran="monthly">월별</button>
          </div>
        </div>

        <div class="card mb-6">
          <div class="card-head">
            <h2 class="card-title">수익 현황</h2>
            <button class="btn btn-excel" data-act="xls-open" data-xls="profit-status" data-mount="pf-xls1">{EX}</button>
          </div>
          <div class="stat-grid" data-mount="pf-stat"></div>
        </div>

        <div class="tbl-wrap mb-6">
          <div class="tbl-head">
            <div class="left">
              <h2 class="card-title" data-mount="pf-tbl-title">일별 투자수익</h2>
            </div>
            <button class="btn btn-excel" data-act="xls-open" data-xls="profit-daily" data-mount="pf-xls2">{EX}</button>
          </div>
          <div data-mount="pf-tbl"></div>
        </div>

{FORMULA}
      </section>

      <!-- ═════════ 투자 시뮬레이션 ═════════ -->
      <!-- 골격은 payhug-admin-web/app/settlement/simulation/page.tsx 를 따른다 —
           :210-248 고정 변수 블록 · :251-303 반복 행 블록 · :299-302 합계 한 줄 ·
           :306-312 폭 전체 실행 버튼 · :321 결과 게이트(실행 전에는 결과가 없다). -->
      <section class="screen" data-screen="invest-sim" data-state="default" hidden>
        <div class="page-header">
          <h1 class="page-title">투자 시뮬레이션<span data-state-mark></span></h1>
        </div>

        <div class="card mb-6">
          <div class="card-head">
            <h2 class="card-title">기준 변수</h2>
          </div>
          <div class="sim-grid">
            <div class="filter-field">
              <label for="sim-r">할인율 (%)</label>
              <input type="number" id="sim-r" class="input" step="0.01" min="0.01" max="5" data-mount="sim-r" data-act="sim-var" data-k="r">
            </div>
            <div class="filter-field">
              <label for="sim-cash">순현금 (원)</label>
              <input type="number" id="sim-cash" class="input" step="100000" min="0" data-mount="sim-cash" data-act="sim-var" data-k="cash">
            </div>
            <div class="filter-field">
              <label for="sim-unpaid">미지급률 (%)</label>
              <input type="number" id="sim-unpaid" class="input" step="0.01" min="0" max="100" data-mount="sim-unpaid" data-act="sim-var" data-k="unpaid">
            </div>
            <div class="filter-field">
              <label for="sim-over">과지급률 (%)</label>
              <input type="number" id="sim-over" class="input" step="0.01" min="0" max="100" data-mount="sim-over" data-act="sim-var" data-k="over">
            </div>
            <div class="filter-field">
              <label for="sim-from">시작일</label>
              <input type="date" id="sim-from" class="input" data-mount="sim-from" data-act="sim-var" data-k="from">
            </div>
            <div class="filter-field">
              <label for="sim-to">종료일</label>
              <input type="date" id="sim-to" class="input" data-mount="sim-to" data-act="sim-var" data-k="to">
            </div>
          </div>
          <p class="range-warn" data-mount="sim-warn" hidden>시작일은 종료일보다 이후일 수 없습니다.</p>
        </div>

        <div class="card mb-6">
          <div class="card-head">
            <h2 class="card-title">정산금채권 입력</h2>
            <button class="btn btn-primary" data-act="sim-add">+ 채권 추가</button>
          </div>
          <div class="sim-head">
            <span class="sim-no"></span><span class="sim-plat">플랫폼</span>
            <span class="sim-amt">순지급액</span><span class="sim-unit"></span>
            <span class="sim-date">선정산일</span><span class="sim-date">정산예정일</span>
            <span class="sim-days">금융일수</span>
          </div>
          <div class="sim-rows" data-mount="sim-rows"></div>
          <div class="sim-total" data-mount="sim-total"></div>
        </div>

        <button class="sim-run" data-act="sim-run" data-mount="sim-go">시뮬레이션 실행</button>

        <div data-mount="sim-out"></div>
      </section>

      <!-- ═════════ 가맹점 ═════════ -->
      <section class="screen" data-screen="merchants" data-state="default" hidden>
        <div class="page-header">
          <h1 class="page-title">가맹점<span data-state-mark></span></h1>
        </div>

        <div class="search-bar">
          <div class="filter-row">
            <div class="filter-field">
              <label>업종</label>
              <select class="input" style="width:140px" data-mount="mc-sector" data-act="mc-sector" aria-label="업종"></select>
            </div>
            <div class="filter-field">
              <label>채권매입업체</label>
              <select class="input" style="width:180px" data-mount="mc-buyer" data-act="mc-buyer">
                <option>전체</option><option>A-001 ㈜페이허그</option>
              </select>
            </div>
            <div class="filter-field" style="flex:1; max-width:360px">
              <label>검색어</label>
              <input type="text" class="input" style="width:100%" data-mount="mc-kw" data-act="mc-kw" placeholder="가맹점ID·가맹점명·사업자번호·대표자명">
            </div>
            <button class="btn btn-primary" data-act="mc-search">검색</button>
            <button class="btn btn-outline" data-act="mc-reset">초기화</button>
          </div>
        </div>

        <div data-mount="mc-chips"></div>

        <div class="tbl-wrap">
          <div class="tbl-head-bar">
            <span class="card-title" style="margin:0">가맹점 목록</span>
            <div class="list-tools"><span data-mount="mc-size"></span></div>
          </div>
          <div data-mount="mc-tbl"></div>
          <div class="pagination with-count" data-mount="mc-page"></div>
        </div>
      </section>

      <!-- ═════════ 정산채권 양수 ═════════ -->
      <section class="screen" data-screen="acquisition-list" data-state="default" hidden>
        <div class="page-header">
          <h1 class="page-title">정산채권 양수<span data-state-mark></span></h1>
        </div>
        <div class="notice notice-green">
          {INFO}
          <span data-mount="aq-notice"></span>
        </div>
        <div class="card" style="padding:0; overflow:hidden">
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
        </div>
      </section>

      <!-- ═════════ 계약기록 ═════════ -->
      <section class="screen" data-screen="contracts" data-state="default" hidden>
        <div class="page-header">
          <h1 class="page-title">계약기록<span data-state-mark></span></h1>
        </div>
        <div class="tbl-wrap">
          <div class="tbl-head-bar">
            <div>
              <span class="card-title" style="margin:0">재양도합의서 목록</span>
              <span class="tbl-count" data-mount="ct-count"></span>
            </div>
            <div class="list-tools">
              <span data-mount="ct-size"></span>
              <button class="btn btn-ghost" data-act="ct-clear" data-mount="ct-clear">선택 해제</button>
              <button class="btn btn-excel" data-act="ct-download" data-mount="ct-dl">{EX2}</button>
            </div>
          </div>
          <div data-mount="ct-tbl"></div>
          <div class="pagination with-count" style="border-top:1px solid var(--gray-100)" data-mount="ct-page"></div>
        </div>
      </section>

      <!-- ═════════ 쿠콘 관리 현금 ═════════ -->
      <section class="screen" data-screen="coocon" data-state="default" hidden>
        <div class="page-header">
          <h1 class="page-title">쿠콘 관리 현금<span data-state-mark></span></h1>
        </div>
{COOCON}
      </section>

      <!-- ═════════ 비밀번호 변경 ═════════
           원본 = payhug-merchant-web/app/my-info/change-password/page.tsx
                  + components/PasswordInput.tsx + lib/passwordPolicy.ts
           라벨·플레이스홀더·안내·오류 문구는 원본 문자열 그대로 둔다.
           제품 UI 문구이므로 문서 문체(개조식)로 고치지 않는다. -->
      <section class="screen" data-screen="password" data-state="default" hidden>
        <div class="page-header">
          <h1 class="page-title">비밀번호 변경<span data-state-mark></span></h1>
        </div>
        <div class="card pw-card">
          <div class="pw-form">
            <!-- 현재 비밀번호 — 원본은 message·checklist 를 넘기지 않아 메시지 칸 자체가 없다 -->
            <div class="pw-field" data-mount="pw-cur-field">
              <label for="pw-cur-input">현재 비밀번호</label>
              <div class="pw-box">
                <div class="pw-caps" data-mount="pw-cur-caps" hidden></div>
                <input id="pw-cur-input" type="password" placeholder="현재 비밀번호를 입력하세요"
                       autocomplete="current-password" data-mount="pw-cur" data-act="pw-input" data-pw="cur">
                <button type="button" class="pw-eye" data-act="pw-eye" data-pw="cur" data-mount="pw-cur-eye"></button>
              </div>
            </div>

            <div class="pw-field" data-mount="pw-new-field">
              <label for="pw-new-input">새 비밀번호</label>
              <div class="pw-box">
                <div class="pw-caps" data-mount="pw-new-caps" hidden></div>
                <input id="pw-new-input" type="password" placeholder="비밀번호 입력" maxlength="16"
                       autocomplete="new-password" data-mount="pw-new" data-act="pw-input" data-pw="new">
                <button type="button" class="pw-eye" data-act="pw-eye" data-pw="new" data-mount="pw-new-eye"></button>
              </div>
              <div class="pw-msgbox" data-mount="pw-new-msgbox"></div>
            </div>

            <div class="pw-field" data-mount="pw-cfm-field">
              <label for="pw-cfm-input">새 비밀번호 확인</label>
              <div class="pw-box">
                <div class="pw-caps" data-mount="pw-cfm-caps" hidden></div>
                <input id="pw-cfm-input" type="password" placeholder="새 비밀번호를 한번 더 입력하세요" maxlength="16"
                       autocomplete="new-password" data-mount="pw-cfm" data-act="pw-input" data-pw="cfm">
                <button type="button" class="pw-eye" data-act="pw-eye" data-pw="cfm" data-mount="pw-cfm-eye"></button>
              </div>
              <div class="pw-msgbox" data-mount="pw-cfm-msgbox"></div>
            </div>

            <button type="button" class="pw-submit" data-act="pw-submit" data-mount="pw-submit">비밀번호 변경하기</button>
          </div>
        </div>
      </section>
'''.replace('{EX}', EXCEL_BTN_INNER) \
   .replace('{EX2}', sv(D_EXCEL) + '\n          <span data-mount="ct-dl-label">선택 문서 다운로드</span>') \
   .replace('{INFO}', sv(D_INFO)) \
   .replace('{WARN}', sv(D_WARN, '2', 'warn-ico')) \
   .replace('{ERRICO}', sv(D_ERR, '2.2')) \
   .replace('{CHECKC}', sv(D_CHECKC)) \
   .replace('{COOCON}', '        ' + dedent_block(COOCON, 0).replace('\n', '\n        ')) \
   .replace('{FORMULA}', FORMULA_BLOCK)

SCREENS_HTML += (
    xls_shell('xls-assets-status',  'invest-assets', '투자 자산', '엑셀 산출물 서식 — 투자자산 현황') +
    xls_shell('xls-assets-merchant', 'invest-assets', '투자 자산', '엑셀 산출물 서식 — 가맹점별 투자자산') +
    xls_shell('xls-profit-status',  'invest-profit', '투자 수익', '엑셀 산출물 서식 — 투자수익 현황') +
    xls_shell('xls-profit-daily',   'invest-profit', '투자 수익', '엑셀 산출물 서식 — 일별 투자수익')
)

# ── 사이드바 없는 독립 화면 ────────────────────────────────────
STANDALONE_HTML = '''
<section class="screen" data-screen="index" data-state="default" hidden>
  <div class="wrap">
    <div class="hero">
      <span class="logo-mark" role="img" aria-label="PayHug"></span>
      <div>
        <h1>PayHug <em>투자자 어드민</em> — 화면 설계(안)</h1>
        <p class="sub">사이드바 메뉴 {MENUS}개 — {MENULIST}. 아래 화면과 상태를 눌러서 오갈 수 있고 엑셀은 실제로 내려받는다.</p>
      </div>
      <span class="hero-date">2026-08-27</span>
    </div>
    <div class="sec-head"><h2>화면</h2><span class="sec-note">메뉴 대응 {MENUS} · 하위 {SUBN} · 상태 {STATES}</span></div>
    <div class="gallery" data-mount="ix-gallery"></div>
  </div>
</section>

<section class="screen" data-screen="login" data-state="default" hidden>
  <div class="login-wrap">
{LOGINCARD}
  </div>
</section>
'''.replace('{LOGINCARD}', LOGINCARD) \
    .replace('{MENUS}', str(counts.C['menus'])) \
    .replace('{MENULIST}', counts.menu_sentence()) \
    .replace('{SUBN}', str(counts.C['screens'] - 1 - counts.C['menus'])) \
    .replace('{STATES}', str(counts.C['states']))

# ── 모달 5종 ───────────────────────────────────────────────────
MODALS_HTML = '''
<div class="modal-backdrop" data-modal="invest-assets-cert-confirm" data-act="backdrop" hidden>
  <div class="modal md">
    <div class="modal-header">
      <h3>투자자산 증명서 발급</h3>
      <button class="close" aria-label="닫기" data-act="modal-close">{X}</button>
    </div>
    <div class="modal-body">
      <p class="cert-desc">기준일 2026-08-27 시점의 가맹점별 투자자산 내역으로 전자문서 발급.</p>
      <dl class="cert-info">
        <dt>문서명</dt><dd>투자자산 증명서</dd>
        <dt>기준일</dt><dd class="mono">2026-08-27</dd>
        <dt>대상</dt><dd data-mount="cf-target">가맹점 16개</dd>
        <dt>작성자</dt><dd>㈜페이허그</dd>
      </dl>
    </div>
    <div class="modal-footer">
      <button class="btn btn-outline" data-act="modal-close">취소</button>
      <button class="btn btn-primary" data-act="cert-issue">발급</button>
    </div>
  </div>
</div>

<div class="modal-backdrop" data-modal="acquisition-confirm" data-act="backdrop" hidden>
  <div class="modal md">
    <div class="modal-header">
      <h3>정산금채권 양수도 계약서 서명</h3>
      <button class="close" aria-label="닫기" data-act="modal-close">{X}</button>
    </div>
    <div class="modal-body">
      <p class="modal-desc" style="margin:0">선택한 <b data-mount="aqc-count">2건</b>의 계약서에 전자서명. 서명 후 취소 불가.</p>
      <div class="modal-sign-list" data-mount="aqc-list"></div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-outline" data-act="modal-close">취소</button>
      <button class="btn btn-primary" data-act="aq-sign-go">서명 진행</button>
    </div>
  </div>
</div>

<div class="modal-backdrop" data-modal="acquisition-doc" data-act="backdrop" hidden>
  <div class="modal lg">
    <div class="modal-header">
      <h3>계약서보기</h3>
      <button class="close" aria-label="닫기" data-act="modal-close">{X}</button>
    </div>
    <div class="modal-body doc-view">
      <p class="doc-meta">가맹점ID <span class="mono" data-mount="aqv-mid"></span> · 계약 생성일 <span class="mono" data-mount="aqv-date"></span>
        <span class="badge" data-mount="aqv-badge"></span></p>
      <div class="doc-scroll">
        {CONTRACT}
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-outline" data-act="modal-close">닫기</button>
      <a class="btn btn-primary" data-act="aq-file" data-mount="aqv-file" href="#" target="_blank" rel="noopener">원문 전체 열기</a>
    </div>
  </div>
</div>

<div class="modal-backdrop" data-modal="acquisition-signing" hidden>
  <div class="modal md">
    <div class="modal-header"><h3>전자서명 진행</h3></div>
    <div class="modal-body">
      <div class="spin-wrap">
        <div class="spinner"></div>
        <span class="spin-label">인증서 서명 진행 중</span>
      </div>
      <div class="step-list">
        <div class="step done">
          <span class="step-num">{CHK}</span>
          <span class="step-text">계약서 생성 완료
            <span class="step-note">양수도 계약서 <span data-mount="aqs-count">2</span>건 생성.</span>
          </span>
        </div>
        <div class="step now">
          <span class="step-num">2</span>
          <span class="step-text">인증서 서명 진행 중
            <span class="step-note">전자서명 진행 중.</span>
          </span>
        </div>
        <div class="step">
          <span class="step-num">3</span>
          <span class="step-text">서명 검증 대기
            <span class="step-note">인증서 발행기관 검증 회신 대기.</span>
          </span>
        </div>
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-primary" disabled>서명 진행 중</button>
    </div>
  </div>
</div>

<div class="modal-backdrop" data-modal="acquisition-done" data-act="backdrop" hidden>
  <div class="modal md">
    <div class="modal-body" style="padding-top:32px">
      <div class="done-head">
        <div class="done-icon">{CHKB}</div>
        <h3 class="done-title">서명 완료</h3>
        <p class="done-desc">정산금채권 양수도 계약 <b data-mount="aqd-count">2건</b> 서명 완료.<br>서명값은 계약기록에 보관.</p>
      </div>
      <div class="done-list" data-mount="aqd-list"></div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-outline" data-act="aq-to-contracts">계약기록 보기</button>
      <button class="btn btn-primary" data-act="aq-done-ok">확인</button>
    </div>
  </div>
</div>

'''.replace('{X}', sv(D_X)).replace('{CHK}', sv(D_CHECK, '3')).replace('{CHKB}', sv(D_CHECK, '2.5')) \
   .replace('{CONTRACT}', contract_text.as_html('        '))

CHROME_HTML = '''
<div class="toast toast-success" role="status" data-mount="toast" hidden></div>

'''

# ════════════════════════════════════════════════════════════════
# JS — 데이터 · 코어
# ════════════════════════════════════════════════════════════════
JS = r'''
'use strict';

/* ═══ 예시 데이터 — 개별 화면 HTML·assets/xlsx 실측값 그대로. 새 값 생성 없음 ═══ */
var BASE_DATE = '2026-08-27';
var INVESTOR  = '㈜테스트인베스트';

var MERCHANTS = [
@@MERCHANTS@@
];
/* 업종 옵션은 원장 데이터에서 뽑는다 — 화면에 없는 업종을 옵션으로 내걸지 않는다.
   운영 어드민에는 업종 필터 자체가 없어(admin app/manage/page.tsx:223-255 · services/merchantService.ts:199-205)
   가져올 코드 목록이 없다. 근거가 있는 값은 원장에 실재하는 업종뿐이다. */
var SECTORS = (function(){
  var out = ['전체'], seen = {}, i;
  for(i = 0; i < MERCHANTS.length; i++){
    var v = MERCHANTS[i].sector;
    if(v && !seen[v]){ seen[v] = 1; out.push(v); }
  }
  return out;
})();

/* 현황 표 — 투자실행액 행의 W·S·Ty는 기록값(합계 행에서는 산정하지 않음) */
var ASSET_ROWS = [
@@ASSETROWS@@
];

/* 일별 투자수익 원장 — 2026-03-01 ~ 08-27 180일. 생성기 daily_ledger.py.
   월별 표는 이 원장을 조회 기간만큼 잘라 달별로 합친 결과다(rollupMonths). 월별 배열을 따로 두지 않는다.
   그래야 같은 조회 기간에서 일별 합계와 월별 합계, 그리고 카드 값이 어긋날 수 없다.
   투자 수익 = floor(순지급액 x 0.11%) · 상환액 = 투자실행금 + 투자 수익 ·
   Ty수익율 = (투자 수익 / 투자실행금 x 100) x 365 / W금융일수.
   수수료 앵커는 순지급액이다(D-31) — 투자 시뮬레이션 simBond 와 같은 앵커라 두 화면의 같은 열이 갈리지 않는다. */
var DAILY = [
@@LEDGER@@
];

var CONTRACTS = [
@@CONTRACTS@@
];

var SIGNQ = [
  {mid:'M2026-0001', name:'김성호떡볶이 본점', created:'2026-08-25'},
  {mid:'M2026-0002', name:'달빛곱창 홍대점',   created:'2026-08-26'},
  {mid:'M2026-0004', name:'바다마루 횟집',     created:'2026-08-27'}
];

/* 파일명 규칙 — 원본 `{내용}_{시작일}_{종료일}.xlsx`, 날짜 YYYY-MM-DD
   (TransferRecordsTab.tsx:318 · overview/page.tsx:658 · PreSettlementTab.tsx:394 · LockAccountDeposits.tsx:219).
   투자자산 2건은 기준일 스냅샷이라 시작=종료, 투자수익 2건은 기본 조회기간(일주일). */
var XLSX = {
  'assets-status':   {file:'투자자산현황_2026-08-27_2026-08-27.xlsx',   size:'@@SZ:투자자산현황_2026-08-27_2026-08-27.xlsx@@', made:'@@MT:투자자산현황_2026-08-27_2026-08-27.xlsx@@', sheet:'투자자산 현황',   screen:'xls-assets-status',   from:'invest-assets'},
  'assets-merchant': {file:'가맹점별투자자산_2026-08-27_2026-08-27.xlsx', size:'@@SZ:가맹점별투자자산_2026-08-27_2026-08-27.xlsx@@', made:'@@MT:가맹점별투자자산_2026-08-27_2026-08-27.xlsx@@', sheet:'가맹점별 투자자산', screen:'xls-assets-merchant', from:'invest-assets'},
  'profit-status':   {file:'투자수익현황_2026-08-21_2026-08-27.xlsx',   size:'@@SZ:투자수익현황_2026-08-21_2026-08-27.xlsx@@', made:'@@MT:투자수익현황_2026-08-21_2026-08-27.xlsx@@', sheet:'투자수익 현황',   screen:'xls-profit-status',   from:'invest-profit'},
  'profit-daily':    {file:'일별투자수익_2026-08-21_2026-08-27.xlsx',   size:'@@SZ:일별투자수익_2026-08-21_2026-08-27.xlsx@@', made:'@@MT:일별투자수익_2026-08-21_2026-08-27.xlsx@@', sheet:'일별 투자수익',   screen:'xls-profit-daily',    from:'invest-profit'},
  /* 주별·월별은 실물 파일만 둔다 — 미리보기 낱장은 일별 것 하나로 충분하다(서식이 같다).
     `수익 현황`도 집계 단위마다 기간이 달라 3벌이다 — 카드가 4주를 말하는데 파일이 일주일이면
     화면과 파일이 다른 기간을 말한다. */
  'profit-weekly':   {file:'주별투자수익_2026-08-03_2026-08-30.xlsx',   size:'@@SZ:주별투자수익_2026-08-03_2026-08-30.xlsx@@', made:'@@MT:주별투자수익_2026-08-03_2026-08-30.xlsx@@', sheet:'주별 투자수익',   screen:null, from:'invest-profit'},
  'profit-monthly':  {file:'월별투자수익_2026-03-01_2026-08-31.xlsx',   size:'@@SZ:월별투자수익_2026-03-01_2026-08-31.xlsx@@', made:'@@MT:월별투자수익_2026-03-01_2026-08-31.xlsx@@', sheet:'월별 투자수익',   screen:null, from:'invest-profit'},
  'profit-status-weekly':  {file:'투자수익현황_2026-08-03_2026-08-30.xlsx', size:'@@SZ:투자수익현황_2026-08-03_2026-08-30.xlsx@@', made:'@@MT:투자수익현황_2026-08-03_2026-08-30.xlsx@@', sheet:'투자수익 현황', screen:null, from:'invest-profit'},
  'profit-status-monthly': {file:'투자수익현황_2026-03-01_2026-08-31.xlsx', size:'@@SZ:투자수익현황_2026-03-01_2026-08-31.xlsx@@', made:'@@MT:투자수익현황_2026-03-01_2026-08-31.xlsx@@', sheet:'투자수익 현황', screen:null, from:'invest-profit'}
};

/* 투자수익 표는 일별·주별·월별 3단이고 엑셀도 3벌이다 — 지금 보고 있는 표를 그대로 내려준다.
   `수익 현황` 카드도 같다. 카드에 적힌 기간과 파일명의 기간이 갈리면 안 된다.
   미리보기 화면(파일바·시트)과 다운로드가 같은 답을 쓰도록 해석은 이 함수 하나에서만 한다. */
var PROFIT_XLS = {daily:'profit-daily', weekly:'profit-weekly', monthly:'profit-monthly'};
var PROFIT_STATUS_XLS = {daily:'profit-status', weekly:'profit-status-weekly', monthly:'profit-status-monthly'};
function xlsKey(k){
  if(k === 'profit-daily')  return PROFIT_XLS[PF.gran] || k;
  if(k === 'profit-status') return PROFIT_STATUS_XLS[PF.gran] || k;
  return k;
}

/* ═══ 화면·상태 레지스터 ═══ */
var MENU_OF = {
  'invest-assets':'invest-assets', 'certificate':'invest-assets',
  'xls-assets-status':'invest-assets', 'xls-assets-merchant':'invest-assets',
  'invest-profit':'invest-returns', 'xls-profit-status':'invest-returns', 'xls-profit-daily':'invest-returns',
  'invest-sim':'invest-sim',
  'merchants':'merchants', 'acquisition-list':'receivables', 'contracts':'contracts',
  'coocon':'kcoon', 'password':'password', 'index':'', 'login':''
};
var STANDALONE = ['index', 'login'];
var STATE_META = {
  'invest-assets': {
    'default':null,
    'page2':        {label:'2페이지',          cls:'badge-gray'},
    'download':     {label:'엑셀 다운로드 완료', cls:'badge-gray'},
    'cert-confirm': {label:'증명서 발급 확인',   cls:'badge-gray'},
    'empty':        {label:'데이터 없음',       cls:'badge-gray'}
  },
  'invest-profit': {
    'default':null,
    'weekly':     {label:'주별',      cls:'badge-gray'},
    'monthly':    {label:'월별',      cls:'badge-gray'},
    'empty':      {label:'결과 없음', cls:'badge-gray'}
  },
  'merchants': {
    'default':null,
    'filtered':    {label:'검색 적용', cls:'badge-gray'},
    'empty':       {label:'결과 없음', cls:'badge-gray'}
  },
  'acquisition-list': {
    'default':null,
    'doc':     {label:'계약서보기', cls:'badge-gray'},
    'confirm': {label:'서명 확인', cls:'badge-gray'},
    'signing': {label:'서명 진행', cls:'badge-gray'},
    'done':    {label:'서명 완료', cls:'badge-gray'}
  },
  'contracts': {
    'default':null,
    'all':        {label:'전체 선택',     cls:'badge-primary'},
    'downloaded': {label:'다운로드 완료', cls:'badge-green'},
    'empty':      {label:'문서 없음',     cls:'badge-gray'}
  },
  'invest-sim': {
    'default':null,
    'result': {label:'실행 결과', cls:'badge-primary'}
  },
  'coocon':   {'default':null},
  'password': {
    'default':null,
    'weak':  {label:'규칙 미충족',   cls:'badge-amber'},
    'error': {label:'확인값 불일치', cls:'badge-red'},
    'done':  {label:'변경 완료',     cls:'badge-green'}
  },
  'certificate':{'default':null}, 'xls-assets-status':{'default':null}, 'xls-assets-merchant':{'default':null},
  'xls-profit-status':{'default':null}, 'xls-profit-daily':{'default':null},
  'index':{'default':null}, 'login':{'default':null}
};
var SCREEN_LABEL = {
  'index':'랜딩 갤러리', 'login':'로그인', 'invest-assets':'투자 자산', 'certificate':'투자자산 증명서',
  'xls-assets-status':'엑셀 산출물 서식 — 투자자산 현황', 'xls-assets-merchant':'엑셀 산출물 서식 — 가맹점별 투자자산',
  'invest-profit':'투자 수익', 'xls-profit-status':'엑셀 산출물 서식 — 투자수익 현황',
  'xls-profit-daily':'엑셀 산출물 서식 — 일별 투자수익', 'invest-sim':'투자 시뮬레이션', 'merchants':'가맹점',
  'acquisition-list':'정산채권 양수', 'contracts':'계약기록', 'coocon':'쿠콘 관리 현금', 'password':'비밀번호 변경'
};
var SCREEN_ORDER = ['index','login','invest-assets','certificate','xls-assets-status','xls-assets-merchant',
  'invest-profit','xls-profit-status','xls-profit-daily','invest-sim','merchants','acquisition-list','contracts','coocon','password'];
var FILE2SCREEN = {
  'index.html':'index', 'login.html':'login', 'invest-assets.html':'invest-assets', 'certificate.html':'certificate',
  'invest-profit.html':'invest-profit', 'invest-sim.html':'invest-sim',
  'merchants.html':'merchants', 'acquisition.html':'acquisition-list',
  'contracts.html':'contracts', 'coocon.html':'coocon', 'password.html':'password',
  'xls-assets-status.html':'xls-assets-status', 'xls-assets-merchant.html':'xls-assets-merchant',
  'xls-profit-status.html':'xls-profit-status', 'xls-profit-daily.html':'xls-profit-daily'
};
var STATEFILE = {
  'invest-assets--page2.html':'invest-assets/page2', 'invest-assets--download.html':'invest-assets/download',
  'invest-assets--cert-confirm.html':'invest-assets/cert-confirm', 'invest-assets--empty.html':'invest-assets/empty',
  'invest-profit--weekly.html':'invest-profit/weekly',
  'invest-profit--monthly.html':'invest-profit/monthly',
  'invest-profit--empty.html':'invest-profit/empty',
  'invest-sim--result.html':'invest-sim/result',
  'merchants--filtered.html':'merchants/filtered', 'merchants--empty.html':'merchants/empty',
  'acquisition--confirm.html':'acquisition-list/confirm', 'acquisition--signing.html':'acquisition-list/signing',
  'acquisition--done.html':'acquisition-list/done', 'acquisition--doc.html':'acquisition-list/doc',
  'contracts--all.html':'contracts/all',
  'contracts--downloaded.html':'contracts/downloaded', 'contracts--empty.html':'contracts/empty',
  'password--weak.html':'password/weak',
  'password--error.html':'password/error', 'password--done.html':'password/done'
};
var MODAL_OF = {
  'invest-assets/cert-confirm':'invest-assets-cert-confirm',
  'acquisition-list/doc':'acquisition-doc',
  'acquisition-list/confirm':'acquisition-confirm',
  'acquisition-list/signing':'acquisition-signing',
  'acquisition-list/done':'acquisition-done'
};

/* ═══ 유틸 ═══ */
function fmt(n){ return Number(n).toLocaleString('ko-KR'); }
function pct(v, d){ return (v===null||v===undefined) ? '-' : Number(v).toFixed(d===undefined?1:d) + '%'; }
function fx(v, d){ return Number(v).toFixed(d); }
function sum(a, k){ var t=0; for(var i=0;i<a.length;i++) t += a[i][k]; return t; }
/* 비중 — 소수 1자리 반올림 후 잔차를 최대 금액 행에 흡수해 합계를 정확히 100.0 으로 닫는다 */
function ratios(a, base){
  var i, out = [], k = 0, t = 0;
  for(i = 0; i < a.length; i++){
    out.push(base ? Math.round(a[i].amount / base * 1000) / 10 : 0);
    t += out[i];
    if(a[i].amount > a[k].amount) k = i;
  }
  if(a.length) out[k] = Math.round((out[k] + (100 - t)) * 10) / 10;
  return out;
}
function wavg(a, k, wk){ var n=0, d=0; for(var i=0;i<a.length;i++){ n += a[i][k]*a[i][wk]; d += a[i][wk]; } return d? n/d : 0; }
function esc(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function Q(sel, root){ return (root||document).querySelector(sel); }
function QA(sel, root){ return Array.prototype.slice.call((root||document).querySelectorAll(sel)); }
function SEC(id){ return Q('section.screen[data-screen="' + id + '"]'); }
function M(name, screen){
  return screen ? Q('[data-mount="' + name + '"]', SEC(screen)) : Q('[data-mount="' + name + '"]');
}
var SVGD = {
  excel:  '$D_EXCEL', doc:'$D_DOC', checkc:'$D_CHECKC', check:'$D_CHECK', x:'$D_X',
  left:   '$D_LEFT', right:'$D_RIGHT', grid:'$D_GRID', ext:'$D_EXT', card:'$D_CARD', trend:'$D_TREND',
  users:  '$D_USERS', cards:'$D_CARDS', coin:'$D_COIN', lock:'$D_LOCK', shield:'$D_SHIELD',
  chev:   '$D_CHEV', dl:'$D_DL', chart:'M9 17V7m4 10V11m4 6v-3M5 21h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v14a2 2 0 002 2z',
  search: 'M21 21l-5.2-5.2m2.2-5.3a7.5 7.5 0 11-15 0 7.5 7.5 0 0115 0z'
};
function svg(key, w, cls, style){
  return '<svg' + (cls?' class="'+cls+'"':'') + (style?' style="'+style+'"':'') +
         ' fill="none" stroke="currentColor" viewBox="0 0 24 24">' +
         '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="' + (w||2) + '" d="' + SVGD[key] + '"/></svg>';
}
'''
_SVGMAP = [('$D_EXCEL', D_EXCEL), ('$D_DOC', D_DOC), ('$D_CHECKC', D_CHECKC), ('$D_CHECK', D_CHECK),
           ('$D_X', D_X), ('$D_LEFT', D_LEFT), ('$D_RIGHT', D_RIGHT), ('$D_GRID', D_GRID),
           ('$D_EXT', D_EXT), ('$D_CARD', D_CARD), ('$D_TREND', D_TREND), ('$D_USERS', D_USERS),
           ('$D_CARDS', D_CARDS), ('$D_COIN', D_COIN), ('$D_LOCK', D_LOCK), ('$D_SHIELD', D_SHIELD),
           ('$D_CHEV', D_CHEV), ('$D_DL', D_DL)]
for _k, _v in sorted(_SVGMAP, key=lambda kv: -len(kv[0])):   # 긴 토큰 우선 — $D_CARD 가 $D_CARDS 를 자르지 않게
    JS = JS.replace(_k, _v)

# ════════════════════════════════════════════════════════════════
# JS — 모델 · 상태 기계
# ════════════════════════════════════════════════════════════════
JS += r'''
/* ═══ 모델 (조작 결과가 여기 쌓이고, 화면은 여기서만 그려진다) ═══ */
var IA = {page:1, downloaded:false, empty:false, cert:false};
var PF = {gran:'daily', from:'2026-08-21', to:'2026-08-27'};
/* ── 두 축 ─────────────────────────────────────────────────────────────
   PF.from · PF.to = 무엇을 조회하느냐.  PF.gran = 표의 한 행이 무엇이냐(하루·한 주·한 달).
   두 축은 서로를 지우지 않는다. 집계 단위를 바꿔도 기간은 남고, 새 단위 경계로 넓혀 스냅될 뿐이다.
   집계 단위가 곧 데이트피커의 스냅 단위다 — 날짜 하나를 고르면 그 날짜가 속한 단위 전체가 잡힌다. */
function dt(s){ var p = s.split('-'); return new Date(+p[0], +p[1] - 1, +p[2]); }
function ds(d){
  var m = d.getMonth() + 1, y = d.getDate();
  return d.getFullYear() + '-' + (m < 10 ? '0' : '') + m + '-' + (y < 10 ? '0' : '') + y;
}
function addDays(s, n){ var d = dt(s); d.setDate(d.getDate() + n); return ds(d); }
/* 주 시작 = 월요일. 일요일은 getDay()===0 이라 6일 뒤로 민다 —
   원본 DateRangeFilter.tsx:35 의 '이번 주' 계산(day === 0 ? 6 : day - 1)과 같은 보정이다. */
function monStart(s){ var w = dt(s).getDay(); return addDays(s, -(w === 0 ? 6 : w - 1)); }
function sunEnd(s){ return addDays(monStart(s), 6); }
function mFirst(s){ return s.slice(0, 7) + '-01'; }
function mLast(s){ var d = dt(mFirst(s)); return ds(new Date(d.getFullYear(), d.getMonth() + 1, 0)); }
function mShift(s, n){ var d = dt(mFirst(s)); return ds(new Date(d.getFullYear(), d.getMonth() + n, 1)); }
/* 스냅 — 시작일은 단위의 처음으로, 종료일은 단위의 끝으로. 일별은 고른 날짜 그대로다. */
function snapFrom(s, g){ return !s ? s : (g === 'weekly' ? monStart(s) : (g === 'monthly' ? mFirst(s) : s)); }
function snapTo(s, g){ return !s ? s : (g === 'weekly' ? sunEnd(s) : (g === 'monthly' ? mLast(s) : s)); }

/* 프리셋 = 기간을 채우는 단축키. 집계 단위마다 묶음이 다르다.
   범위를 그 단위 경계에 맞춰 둬야 눌러 채운 기간이 스냅을 다시 통과해도 그대로다.
   일별 둘(일주일·금월)은 스토리보드 슬라이드7 그대로이고,
   주·달 묶음은 원본 DateRangeFilter.tsx:23-61 의 '최근 3개월' ·
   MerchantAvgSalesSummary.tsx:168-176 의 3~6개월 조회범위와 같은 계열이다. */
var PRESET_RANGE = {
  week:  [addDays(BASE_DATE, -6),               BASE_DATE],
  month: [mFirst(BASE_DATE),                    BASE_DATE],
  w4:    [addDays(monStart(BASE_DATE), -21),    sunEnd(BASE_DATE)],
  w12:   [addDays(monStart(BASE_DATE), -77),    sunEnd(BASE_DATE)],
  m3:    [mShift(BASE_DATE, -2),                mLast(BASE_DATE)],
  m6:    [mShift(BASE_DATE, -5),                mLast(BASE_DATE)]
};
var PRESET_LABEL = {week:'일주일', month:'금월', w4:'4주', w12:'12주', m3:'3개월', m6:'6개월'};
var PRESET_GRAN  = {week:'daily', month:'daily', w4:'weekly', w12:'weekly', m3:'monthly', m6:'monthly'};
var GRAN_LABEL   = {daily:'일별', weekly:'주별', monthly:'월별'};
var GRAN_COL     = {daily:'정산예정일', weekly:'정산예정주', monthly:'정산예정월'};
/* 활성 판정은 현재 날짜값이 프리셋 범위와 같은지로 역산한다 — 따로 담아 두지 않는다.
   그래서 피커를 만져 값이 어긋나면 저절로 풀리고, 단위를 바꿔 묶음이 갈려도
   지금 기간과 일치하는 것 하나만 켜진다. 원본 DateRangeFilter.tsx:74-77 과 같은 방식. */
function activePreset(){
  for(var k in PRESET_RANGE)
    if(PRESET_GRAN[k] === PF.gran && PRESET_RANGE[k][0] === PF.from && PRESET_RANGE[k][1] === PF.to) return k;
  return null;
}
var RATE_PCT = 0.11;                 /* 할인율 — 이 산출물의 고정 입력값(D-21). 요율을 정하는 곳은 이 화면이 아니다 */
var MC = {sector:'전체', buyer:'전체', kw:'', page:1, applied:null};
var AQ = {sel:[false,false,false], signed:[false,false,false], phase:'list', doc:null};
var CT = {sel:{'M2026-0001':1, 'M2026-0004':1, 'M2026-0006':1}, page:1, downloaded:false, empty:false};
/* 비밀번호 — 원본 훅(usePasswordInputValue·usePasswordPolicyField·useConfirmPasswordField)의 상태를 그대로 옮긴다.
   blurred = 새 비밀번호 칸에서 한 번이라도 포커스가 빠졌는가(규칙 오류 문구를 그때부터 보인다)
   spaceNew·spaceCfm = 공백을 눌렀을 때 2200ms 동안만 켜지는 일시 오류
   show* = 각 칸의 표시/숨김 토글 · caps = Caps Lock 말풍선을 띄울 칸 */
var PW = {cur:'12345678', nw:'', cfm:'', blurred:false, done:false,
          spaceNew:false, spaceCfm:false, spaceTimer:{},
          showCur:false, showNew:false, showCfm:false, caps:null};
var CUR = 'invest-assets';
var signTimer = null, toastTimer = null, hashLock = false;
var PAGE_SIZES = [10, 20, 50];
var PAGE_SIZE = 10;                  /* 기본 보기 갯수 */
var PS = {'ia-merch':PAGE_SIZE, 'mc-tbl':PAGE_SIZE, 'ct-tbl':PAGE_SIZE};
function psz(k){ return PS[k] || PAGE_SIZE; }
function presetLabel(){ var k = activePreset(); return k ? PRESET_LABEL[k] : '직접입력'; }

/* 빈 상태 = 표 안 <td colspan> 한 줄. 아이콘 0·버튼 0·일러스트 0.
   원본 app/manage/page.tsx:281-283 · app/sales/page.tsx:121-123 ·
   app/sales/[bizNo]/page.tsx:929 · components/LockAccountDeposits.tsx:425 */
function emptyRow(cols, text){
  return '<tr><td colspan="' + cols + '" class="empty">' + text + '</td></tr>';
}
function emptyTable(head, cols, text){
  return '<div class="tbl-scroll"><table class="tbl"><thead><tr>' + head + '</tr></thead><tbody>' +
         emptyRow(cols, text) + '</tbody></table></div>';
}
/* 표가 아닌 목록 — 원본 BatchDetailTab.tsx:341 의 가운데 정렬 한 줄 */
function emptyLine(text){ return '<div class="empty-cell">' + text + '</div>'; }
/* 쪽번호는 가운데, 총 건수는 같은 줄 맨 왼쪽.
   원본 activity-logs/page.tsx:339 · sales/[bizNo]/page.tsx:1243 = justify-center,
   LockAccountDeposits.tsx:435-437 = 같은 줄 왼쪽 총 건수. 두 패턴을 3열 격자로 겹쳐 쓴다. */
/* 보기 갯수 — 네이티브 select. 고르는 즉시 표를 다시 그린다(적용 버튼 없음).
   원본 어드민은 커스텀 드롭다운이 0건이라 15파일 25곳 전부 <select> 다. */
function sizeSel(key){
  var o = '', i;
  for(i = 0; i < PAGE_SIZES.length; i++)
    o += '<option value="' + PAGE_SIZES[i] + '"' + (psz(key) === PAGE_SIZES[i] ? ' selected' : '') + '>' +
         PAGE_SIZES[i] + '개</option>';
  return '<label class="pg-size">보기<select class="input sz" data-act="pg-size" data-key="' + key +
         '" aria-label="보기 갯수">' + o + '</select></label>';
}
/* 원본은 쪽 이동 컨트롤 전체를 {totalPages > 1 && (…)} 로 가둔다
   (app/sales/[bizNo]/page.tsx:1242 · app/activity-logs/page.tsx:338 · LockAccountDeposits.tsx:432).
   한 쪽에 다 들어오면 비활성 화살표도 쪽번호도 남기지 않는다. */
function pageBar(cur, pages, act, left){
  var inner = '';
  if(pages > 1){
    inner = '<button class="page-arrow" data-act="' + act + '" data-page="' + (cur - 1) + '"' + (cur <= 1 ? ' disabled' : '') + '>' + svg('left') + '</button>';
    for(var p = 1; p <= pages; p++)
      inner += '<button class="page-btn' + (p === cur ? ' active' : '') + '" data-act="' + act + '" data-page="' + p + '">' + p + '</button>';
    inner += '<button class="page-arrow" data-act="' + act + '" data-page="' + (cur + 1) + '"' + (cur >= pages ? ' disabled' : '') + '>' + svg('right') + '</button>';
  }
  if(!left) return inner;
  return '<span class="pg-count">' + left + '</span>' +
         (inner ? '<div class="pg-nums">' + inner + '</div>' : '<span></span>') + '<span></span>';
}

/* ═══ 상태 파생 · 주입 ═══ */
var DERIVE = {
  'invest-assets': function(){
    if(IA.empty) return 'empty';
    if(IA.cert) return 'cert-confirm';
    if(IA.downloaded) return 'download';
    if(IA.page === 2) return 'page2';
    return 'default';
  },
  'invest-profit': function(){
    if(pfRows().length === 0) return 'empty';
    if(PF.gran === 'weekly')  return 'weekly';
    if(PF.gran === 'monthly') return 'monthly';
    return 'default';
  },
  'invest-sim': function(){ return SIM.result ? 'result' : 'default'; },
  'merchants': function(){
    if(MC.applied){ return mcRows().length === 0 ? 'empty' : 'filtered'; }
    return 'default';
  },
  'acquisition-list': function(){
    if(AQ.doc !== null) return 'doc';            /* 계약서보기는 서명 흐름과 겹치지 않는 별개 액션 */
    return AQ.phase === 'list' ? 'default' : AQ.phase;
  },
  'contracts': function(){
    if(CT.empty) return 'empty';
    if(CT.downloaded) return 'downloaded';
    if(ctSelCount() === CONTRACTS.length) return 'all';
    return 'default';
  },
  'password': function(){
    /* 원본은 입력하는 즉시 조건을 따진다 — `한 번 눌러봤는가`로 미루지 않는다. */
    if(PW.done) return 'done';
    if(PW.nw !== '' && !pwIsValid(PW.nw)) return 'weak';
    if(PW.cfm !== '' && !pwCfmMatched()) return 'error';
    return 'default';
  }
};
var SEED = {
  'invest-assets': function(s){ IA.empty = (s === 'empty'); IA.cert = (s === 'cert-confirm'); IA.downloaded = (s === 'download'); IA.page = (s === 'page2') ? 2 : 1; },
  'invest-profit': function(s){
    if(s === 'weekly'){ PF.gran = 'weekly'; PF.from = PRESET_RANGE.w4[0]; PF.to = PRESET_RANGE.w4[1]; }
    else if(s === 'monthly'){ PF.gran = 'monthly'; PF.from = PRESET_RANGE.m6[0]; PF.to = PRESET_RANGE.m6[1]; }
    else if(s === 'empty'){ PF.gran = 'daily'; PF.from = '2026-02-01'; PF.to = '2026-02-07'; }
    else { PF.gran = 'daily'; PF.from = PRESET_RANGE.week[0]; PF.to = PRESET_RANGE.week[1]; }
  },
  'invest-sim': function(s){
    clearSimTimer();
    /* 기본값은 SIM_DEFAULT 한 곳에만 있다 — 여기에 다시 적으면 두 자리가 갈린다 */
    SIM = simSeed();
    if(s === 'result') simRun();
  },
  'merchants': function(s){
    MC.page = 1;
    if(s === 'filtered'){ MC.sector = '음식점업'; MC.kw = '곱창'; MC.buyer = '전체'; MC.applied = {sector:'음식점업', kw:'곱창', buyer:'전체'}; }
    else if(s === 'empty'){ MC.sector = '음식점업'; MC.kw = '라멘'; MC.buyer = '전체'; MC.applied = {sector:'음식점업', kw:'라멘', buyer:'전체'}; }
    else { MC.sector = '전체'; MC.kw = ''; MC.buyer = '전체'; MC.applied = null; }
  },
  'acquisition-list': function(s){
    clearSignTimer();
    AQ.doc = null;
    if(s === 'default'){ AQ.sel = [false, false, false]; AQ.signed = [false, false, false]; AQ.phase = 'list'; }
    else if(s === 'done'){ AQ.sel = [false, false, false]; AQ.signed = [true, true, false]; AQ.phase = 'done'; }
    else if(s === 'doc'){ AQ.sel = [false, false, false]; AQ.signed = [false, false, false]; AQ.phase = 'list'; AQ.doc = 0; }
    else { AQ.sel = [true, true, false]; AQ.signed = [false, false, false]; AQ.phase = s; }
  },
  'contracts': function(s){
    CT.empty = (s === 'empty'); CT.downloaded = (s === 'downloaded'); CT.page = 1;
    if(s === 'all' || s === 'downloaded'){ CT.sel = {}; for(var i = 0; i < CONTRACTS.length; i++) CT.sel[CONTRACTS[i].mid] = 1; }
    else if(s === 'empty'){ CT.sel = {}; }
    else { CT.sel = {'M2026-0001':1, 'M2026-0004':1, 'M2026-0006':1}; }
  },
  'password': function(s){
    pwClearSpaceTimers();
    PW.spaceNew = false; PW.spaceCfm = false; PW.caps = null;
    PW.showCur = false; PW.showNew = false; PW.showCfm = false;
    PW.done = (s === 'done');
    /* 원본은 세 칸 다 비운 채로 열린다. 어느 칸도 미리 채우지 않는다. */
    PW.cur = '';
    if(s === 'weak'){ PW.nw = '12345678'; PW.cfm = ''; PW.blurred = true; }
    else if(s === 'error'){ PW.nw = 'payhug!2026'; PW.cfm = 'payhug!2025'; PW.blurred = true; }
    else { PW.nw = ''; PW.cfm = ''; PW.blurred = false; }
    if(s === 'done') pwShowDoneToast(); else hideToast();
  }
};

/* ═══ 화면 전환 ═══ */
var PEND = {};
/* 조작으로 만들어진 값(서명 결과 등)은 메뉴를 오가도 남는다. 저장소에 쓰지 않으므로
   새로고침하면 처음 상태로 돌아간다. 상태를 콕 집어 부르면(go(id,'default')) 그때는 다시 심는다. */
var DIRTY = {};
function go(screen, state){
  if(!SEC(screen)) screen = 'invest-assets';
  var fresh = (screen !== CUR);
  var st = state || PEND[screen] || ((fresh && !DIRTY[screen]) ? 'default' : null);
  delete PEND[screen];
  clearSignTimer();
  clearSimTimer();
  if(fresh) hideToast();          /* 화면이 바뀌면 이전 화면의 토스트는 내린다 */
  CUR = screen;
  QA('section.screen').forEach(function(s){ s.hidden = (s.dataset.screen !== screen); });
  Q('.page').hidden = (STANDALONE.indexOf(screen) >= 0);
  document.body.dataset.active = MENU_OF[screen] || '';
  document.body.dataset.view = screen;
  if(st && SEED[screen]){ delete DIRTY[screen]; SEED[screen](st); }
  refresh(screen);
  window.scrollTo(0, 0);
}
function refresh(id){
  var sec = SEC(id); if(!sec) return;
  var st = DERIVE[id] ? DERIVE[id]() : 'default';
  sec.dataset.state = st;
  if(RENDER[id]) RENDER[id]();
  QA('[data-when],[data-when-not]', sec).forEach(function(el){
    var ok = true;
    if(el.dataset.when) ok = el.dataset.when.split(/\s+/).indexOf(st) >= 0;
    if(ok && el.dataset.whenNot) ok = el.dataset.whenNot.split(/\s+/).indexOf(st) < 0;
    el.hidden = !ok;
  });
  var mk = Q('[data-state-mark]', sec);
  if(mk){
    var meta = (STATE_META[id] || {})[st];
    mk.innerHTML = meta ? ' <span class="badge ' + meta.cls + ' state-badge">' + meta.label + '</span>' : '';
  }
  var want = MODAL_OF[id + '/' + st] || null;
  QA('[data-modal]').forEach(function(m){ m.hidden = (m.dataset.modal !== want); });
  syncToast(id, st);
  if(id === CUR) setHash(id, st);
}
function setState(id, st){ delete DIRTY[id]; if(SEED[id]) SEED[id](st); refresh(id); }
function setHash(id, st){
  var h = '#' + id + (st && st !== 'default' ? '/' + st : '');
  if(location.hash !== h){ hashLock = true; location.hash = h; setTimeout(function(){ hashLock = false; }, 0); }
}
function readHash(){
  var raw = decodeURIComponent((location.hash || '').replace(/^#/, '')).trim();
  if(!raw) return null;
  if(STATEFILE[raw]) raw = STATEFILE[raw];
  if(FILE2SCREEN[raw]) raw = FILE2SCREEN[raw];
  var p = raw.split('/');
  if(SEC(p[0])) return {screen:p[0], state:p[1] || 'default'};
  for(var s in STATE_META){                       /* app_spec.json 상태 id 별칭 */
    for(var k in STATE_META[s]) if(k !== 'default' && s + '-' + k === raw) return {screen:s, state:k};
  }
  return null;
}
/* ═══ 토스트 ═══ */
/* 원본 Toast.tsx:18, 20-25, 45-51 —
   duration 기본 3000ms, duration===0 이면 자동 소멸 대신 X 닫기 버튼을 렌더한다.
   닫을 수단이 없는 토스트가 만들어지지 않는 구조를 그대로 따른다. */
var TOAST_MS = 3000;
function toastCloseBtn(){
  return '<button type="button" class="t-close" aria-label="닫기" data-act="toast-close">' + svg('x', 2) + '</button>';
}
function toastBody(main, sub){
  return sub ? (svg('checkc', 2, 't-ico') + '<div><p class="t-main">' + main + '</p><p class="t-sub">' + sub + '</p></div>')
             : (svg('checkc', 2, '', 'width:20px;height:20px;flex-shrink:0;margin-top:2px;') + '<span>' + main + '</span>');
}
function armToast(t, ms){
  t.hidden = false;
  if(toastTimer){ clearTimeout(toastTimer); toastTimer = null; }
  if(ms > 0) toastTimer = setTimeout(function(){ t.hidden = true; toastTimer = null; }, ms);
}
function showToast(main, sub, ms){
  if(ms === undefined || ms === null) ms = TOAST_MS;
  var t = M('toast');
  t.className = 'toast toast-success';
  t.innerHTML = toastBody(main, sub) + (ms === 0 ? toastCloseBtn() : '');
  armToast(t, ms);
}
function showInfo(main, ms){
  if(ms === undefined || ms === null) ms = TOAST_MS;
  var t = M('toast');
  t.className = 'toast toast-info';
  t.innerHTML = svg('doc', 1.8, '', 'width:20px;height:20px;flex-shrink:0;margin-top:2px;') + '<span>' + main + '</span>' +
                (ms === 0 ? toastCloseBtn() : '');
  armToast(t, ms);
}
function hideToast(){
  var t = M('toast'); t.hidden = true;
  if(toastTimer){ clearTimeout(toastTimer); toastTimer = null; }
}
/* ── 실물 전달 ────────────────────────────────────────────────────
   화면이 `내려받기 완료`라고 말하면 그 순간 실제 파일이 나가야 한다.
   assets/ 에 실재하는 파일만 건다. 정적 묶음이 없는 조합은 개별 PDF로 내려준다. */
/* 계약기록이 내려주는 것은 전자서명 결과 텍스트다. 실물은 build_sigtext.py 가 만든다. */
var CERT_PDF     = '투자자산증명서_20260827.pdf';
var CONTRACT_TXT  = '정산금채권_재양도_합의서.txt';
var CT_SIG_PREFIX = '전자서명결과_';
var CT_SIG_EXT    = '.txt';
var CT_SIG_ALL   = '전자서명결과_전체16건_20260827.txt';
var CT_SIG_SEL3  = '전자서명결과_선택3건_20260827.txt';
var CT_SEL3     = 'M2026-0001,M2026-0004,M2026-0006';
var toastServed = null;

function pullFile(dir, name, delay){
  setTimeout(function(){
    var a = document.createElement('a');
    a.href = dir + encodeURIComponent(name);
    a.download = name;
    document.body.appendChild(a); a.click(); a.parentNode.removeChild(a);
  }, delay || 0);
}
function ctSelMids(){
  var out = [], i;
  for(i = 0; i < CONTRACTS.length; i++) if(CT.sel[CONTRACTS[i].mid]) out.push(CONTRACTS[i].mid);
  return out;
}
function ctBundle(){
  var mids = ctSelMids(), sig = mids.join(','), f = [], i;
  if(mids.length === CONTRACTS.length && mids.length > 0)
    return {kind:'bundle', files:[CT_SIG_ALL], n:mids.length, sig:sig};
  if(sig === CT_SEL3) return {kind:'bundle', files:[CT_SIG_SEL3], n:mids.length, sig:sig};
  for(i = 0; i < mids.length; i++) f.push(CT_SIG_PREFIX + mids[i] + CT_SIG_EXT);
  return {kind:'each', files:f, n:mids.length, sig:sig};
}
function ctDeliver(b){ for(var i = 0; i < b.files.length; i++) pullFile('assets/docs/', b.files[i], i * 250); }

function syncToast(id, st){
  if(id === 'invest-assets' && st === 'download'){
    var xf = XLSX['assets-merchant'].file, xk = 'invest-assets/download:' + xf;
    if(toastServed !== xk){ pullFile('assets/xlsx/', xf, 0); toastServed = xk; }
    showToast(xf + ' 내려받기 완료'); return;   /* 기본 3,000ms — 원본 Toast.tsx:18 */
  }
  if(id === 'contracts' && st === 'downloaded'){
    var b = ctBundle(), ck = 'contracts/downloaded:' + b.sig;
    if(toastServed !== ck){ ctDeliver(b); toastServed = ck; }
    showToast(b.kind === 'bundle' ? b.files[0] + ' 내려받기 완료'
                                  : '전자서명 결과 ' + b.n + '건 내려받기 완료',
              (b.kind === 'bundle' ? '전자서명 결과 ' + b.n + '건 묶음.' : '개별 파일 ' + b.n + '개.'));
    return;
  }
  toastServed = null;
  if(!toastTimer) M('toast').hidden = true;
}
function clearSignTimer(){ if(signTimer){ clearTimeout(signTimer); signTimer = null; } }
'''

# ════════════════════════════════════════════════════════════════
# JS — 렌더러
# ════════════════════════════════════════════════════════════════
JS += r'''
var RENDER = {};

/* ───────── 투자 자산 ───────── */
function iaExecTotal(){ return sum(MERCHANTS, 'amount'); }
RENDER['invest-assets'] = function(){
  var sec = SEC('invest-assets'), empty = IA.empty;
  var arows = empty ? [] : ASSET_ROWS;
  var mrows = empty ? [] : MERCHANTS;
  var exec = 0, cash = 0, i;
  for(i = 0; i < arows.length; i++){ if(arows[i].name === '순현금') cash += arows[i].amount; else exec += arows[i].amount; }
  var total = exec + cash;
  var aRatio = ratios(arows, total), mRatio = ratios(mrows, exec);
  var rExec = 0, rCash = 0;
  for(i = 0; i < arows.length; i++){ if(arows[i].name === '순현금') rCash += aRatio[i]; else rExec += aRatio[i]; }
  var tyv = arows.length ? arows[0].ty : 0, wv = arows.length ? arows[0].w : null;

  M('ia-summary', 'invest-assets').innerHTML =
    '<div class="summary-card highlight"><div class="summary-label">투자자산</div>' +
      '<div class="summary-value">' + fmt(total) + '<span class="unit">원</span></div>' +
      '<div class="summary-sub">투자실행액 + 순현금</div></div>' +
    '<div class="summary-card"><div class="summary-label">투자실행액</div>' +
      '<div class="summary-value">' + fmt(exec) + '<span class="unit">원</span></div>' +
      '<div class="summary-sub">비중 ' + fx(rExec, 1) + '% · 보관 ㈜페이허그</div></div>' +
    '<div class="summary-card"><div class="summary-label">순현금</div>' +
      '<div class="summary-value">' + fmt(cash) + '<span class="unit">원</span></div>' +
      '<div class="summary-sub">비중 ' + fx(rCash, 1) + '% · 보관 ㈜쿠콘</div></div>' +
    '<div class="summary-card"><div class="summary-label">Ty수익율</div>' +
      '<div class="summary-value">' + fx(tyv, 2) + '<span class="unit">%</span></div>' +
      '<div class="summary-sub">' + (wv === null ? 'W금융일수 집계 대상 없음' : 'W금융일수 ' + fx(wv, 1) + '일 기준') + '</div></div>';

  var h = '<thead><tr><th>자산 구분</th><th class="num">금액 (원)</th><th class="num">W금융일수</th>' +
          '<th class="num">S입금부족율</th><th class="num">Ty수익율</th><th class="num">비중</th><th>보관</th></tr></thead><tbody>';
  if(!arows.length){ h += emptyRow(7, '조회 결과가 없습니다.'); }
  else {
    for(i = 0; i < arows.length; i++){
      var a = arows[i];
      h += '<tr><td><span class="name">' + a.name + '</span></td>' +
           '<td class="num"><span class="strong">' + fmt(a.amount) + '</span></td>' +
           '<td class="num">' + (a.w === null ? '<span class="none">-</span>' : fx(a.w, 1) + '일') + '</td>' +
           '<td class="num">' + (a.s === null ? '<span class="none">-</span>' : pct(a.s, 2)) + '</td>' +
           '<td class="num">' + (a.ty === null ? '<span class="none">-</span>' : pct(a.ty, 2)) + '</td>' +
           '<td class="num">' + fx(aRatio[i], 1) + '%</td><td>' + a.keeper + '</td></tr>';
    }
    h += '<tr class="total-row"><td>합계 (투자자산)</td><td class="num">' + fmt(total) + '</td>' +
         '<td class="num"><span class="none">-</span></td><td class="num"><span class="none">-</span></td>' +
         '<td class="num"><span class="none">-</span></td><td class="num">100.0%</td><td><span class="none">-</span></td></tr>';
  }
  Q('[data-mount="ia-status"]', sec).innerHTML = h + '</tbody>';

  var view = mrows.map(function(r, i){
    var o = {}; for(var k in r) o[k] = r[k];
    o.ratio = mRatio[i]; return o;
  });
  var iaSize = psz('ia-merch');
  var pages = Math.max(1, Math.ceil(view.length / iaSize));
  if(IA.page > pages) IA.page = 1;
  var slice = view.slice((IA.page - 1) * iaSize, IA.page * iaSize);
  var mm = M('ia-merch', 'invest-assets'), mp = M('ia-merch-page', 'invest-assets');
  var IA_HEAD = '<th>가맹점</th><th class="num">투자금액 (원)</th><th class="num">W금융일수</th>' +
                '<th class="num">S입금부족율</th><th class="num">Ty수익율</th><th class="num">비중</th>';
  if(!mrows.length){
    mm.innerHTML = emptyTable(IA_HEAD, 6, '조회 결과가 없습니다.');
    mp.innerHTML = '';
    M('ia-size', 'invest-assets').innerHTML = '';
  } else {
    var t = '<div class="tbl-scroll"><table class="tbl"><thead><tr>' + IA_HEAD + '</tr></thead><tbody>';
    for(i = 0; i < slice.length; i++){
      var m = slice[i];
      t += '<tr><td><span class="name">' + m.name + '</span></td>' +
           '<td class="num"><span class="strong">' + fmt(m.amount) + '</span></td>' +
           '<td class="num">' + fx(m.w, 1) + '일</td><td class="num">' + pct(m.s, 2) + '</td>' +
           '<td class="num">' + pct(m.ty, 2) + '</td><td class="num">' + fx(m.ratio, 1) + '%</td></tr>';
    }
    mm.innerHTML = t + '</tbody></table></div>';
    M('ia-size', 'invest-assets').innerHTML = sizeSel('ia-merch');
    mp.innerHTML = pages > 1 ? '<div class="pagination">' + pageBar(IA.page, pages, 'ia-page') + '</div>' : '';
  }

  var bx = Q('[data-xls="assets-status"]', sec); bx.disabled = empty;
  var xm = M('ia-xls-merchant', 'invest-assets');
  xm.className = 'btn btn-excel' + (IA.downloaded ? ' is-done' : '');
  xm.innerHTML = IA.downloaded ? (svg('checkc') + ' 다운로드 완료') : (svg('excel') + ' 엑셀 다운로드');
  xm.disabled = empty;
  M('ia-cert', 'invest-assets').disabled = empty;
  M('cf-target').textContent = '가맹점 ' + mrows.length + '개';
};

/* ───────── 투자자산 증명서 ───────── */
RENDER['certificate'] = function(){
  var exec = iaExecTotal(), cRatio = ratios(MERCHANTS, exec), i, h =
    '<thead><tr><th>가맹점</th><th>투자금액 (원)</th><th>W금융일수</th><th>S입금부족율</th><th>Ty수익율</th><th>비중</th></tr></thead><tbody>';
  for(i = 0; i < MERCHANTS.length; i++){
    var m = MERCHANTS[i];
    h += '<tr><td>' + m.name + '</td><td class="num">' + fmt(m.amount) + '</td><td class="num">' + fx(m.w, 1) + '일</td>' +
         '<td class="num">' + pct(m.s, 2) + '</td><td class="num">' + pct(m.ty, 2) + '</td>' +
         '<td class="num">' + fx(cRatio[i], 1) + '%</td></tr>';
  }
  h += '</tbody><tfoot><tr><td>합계</td><td class="num">' + fmt(exec) +
       '</td><td class="num">-</td><td class="num">-</td><td class="num">-</td><td class="num">100.0%</td></tr></tfoot>';
  M('cert-tbl', 'certificate').innerHTML = h;
  M('cert-count', 'certificate').textContent = MERCHANTS.length + '개';
};

/* ───────── 투자 수익 ───────── */
/* 조회 기간에 걸친 일자만 자른다 — 일별 표·월별 표·카드·엑셀이 전부 이 한 벌을 본다. */
function pfDays(){
  return DAILY.filter(function(r){ return r.d >= PF.from && r.d <= PF.to; });
}
/* 주별·월별 표 = 잘라 낸 일자를 버킷으로 묶은 것. 버킷이 조회 기간에 일부만 걸리면 걸린 일자만 합친다.
   그래서 같은 조회 기간이면 주별 합계 = 월별 합계 = 일별 합계이고, 카드 값도 셋이 같다.
   대표 정의서의 PSA·PSM 은 '선택 기간 합계'이고, 일별·주별·월별은 그 기간을 어느 크기로
   쪼개 보여주느냐일 뿐이다 — 버킷 하나에 들어가는 계산은 단위가 바뀌어도 같다. */
function rollupBy(days, keyOf, labelOf){
  var out = [], idx = {}, i, g, r, k;
  for(i = 0; i < days.length; i++){
    r = days[i]; k = keyOf(r.d);
    g = idx[k];
    if(!g){ g = idx[k] = {k:k, d:labelOf(r.d), repay:0, exec:0, profit:0, w:0, ty:0, wx:0, days:0}; out.push(g); }
    g.repay += r.repay; g.exec += r.exec; g.profit += r.profit;
    g.wx += r.w * r.exec; g.days += 1;
  }
  for(i = 0; i < out.length; i++){
    g = out[i];
    /* W금융일수는 투자실행금 가중평균이다(단순 합이 아니다).
       Ty수익율은 대표 정의서 그대로 그 가중평균에서 되짚는다 — ty = SMR x 365 / SD,
       SMR = 버킷 투자수익 / 버킷 투자실행금, SD = 버킷 W금융일수.
       일자별 ty 를 다시 가중평균하면 표기 자리에서 W 와 어긋난다(주 버킷에서 실제로 어긋났다).
       반올림하지 않고 담아 두고 표기할 때만 자른다. 그래야 일별·주별·월별 표의 카드 값이 같다. */
    g.w  = g.exec ? g.wx / g.exec : 0;
    g.ty = (g.exec && g.w) ? (g.profit / g.exec * 100) * 365 / g.w : 0;
  }
  out.sort(function(a, b){ return a.k < b.k ? -1 : (a.k > b.k ? 1 : 0); });
  return out;
}
function rollupMonths(days){
  return rollupBy(days, function(d){ return d.slice(0, 7); }, function(d){ return d.slice(0, 7); });
}
/* 주 라벨은 그 주의 월요일 ~ 일요일이다. 조회 기간이 주를 일부만 덮어도 라벨은 주 경계를 쓴다. */
function rollupWeeks(days){
  return rollupBy(days, monStart, function(d){ return monStart(d) + ' ~ ' + sunEnd(d).slice(5); });
}
/* 현황 카드 ④ 와 표 합계 행의 Ty수익율 = PSMR x 365 / PSD (대표 정의서).
   PSMR = 기간 투자수익 / 기간 투자실행금, PSD = 투자실행금 가중평균 W금융일수.
   행마다 나온 ty 를 다시 가중평균하면 같이 적어 둔 W 와 표기 자리에서 어긋난다. */
function tyOfRows(rs){
  var ex = sum(rs, 'exec'), pf = sum(rs, 'profit'), w = rs.length ? wavg(rs, 'w', 'exec') : 0;
  return (ex && w) ? (pf / ex * 100) * 365 / w : 0;
}
function pfRows(){
  var d = pfDays();
  if(PF.gran === 'weekly')  return rollupWeeks(d);
  if(PF.gran === 'monthly') return rollupMonths(d);
  return d;
}
/* 원장이 각 달에 대해 갖고 있는 일수 — 조회 기간이 그 달을 일부만 덮었는지 판정한다. */
var LEDGER_MONTH_DAYS = (function(){
  var m = {}, i, k;
  for(i = 0; i < DAILY.length; i++){ k = DAILY[i].d.slice(0, 7); m[k] = (m[k] || 0) + 1; }
  return m;
})();
function assetTotal(){ return sum(ASSET_ROWS, 'amount'); }
function cashRow(){
  for(var i = 0; i < ASSET_ROWS.length; i++) if(ASSET_ROWS[i].name === '순현금') return ASSET_ROWS[i];
  return null;
}
/* ── 투자자산 대비 Ty수익율 (현황 ⑤) — 대표 정의서 ────────────────
   ⑤ = (④ × PSA) / (PSA + PSC).  PSA = 기간 투자실행금 합, PSC = 기간 동안 EC들의 합.
   EC = 전일자 마감시점 순현금이며 하루에 한 건 쌓인다(유량). 기준일 잔액 1개(스톡)로 나누지 않는다.
   일별 EC 원장이 없어 EC 는 순현금 잔액으로 고정한다 — 실데이터 연결은 확인 대상. */
/* EC 는 하루에 한 건 쌓이는 유량이라 조회 기간에 걸린 일수만큼 센다.
   일별·월별 어느 쪽으로 보든 같은 기간이면 같은 일수라야 하므로 원장 일수 하나로 센다. */
function ecDays(){ return pfDays().length; }
function tyAssetOf(ty4, psa){
  var c = cashRow(), psc = (c ? c.amount : 0) * ecDays();
  return (psa + psc) ? ty4 * psa / (psa + psc) : 0;
}
RENDER['invest-profit'] = function(){
  var sec = SEC('invest-profit'), rows = pfRows();
  /* 프리셋 묶음은 집계 단위를 따라 갈린다 — 그 단위 것만 남기고 나머지는 접는다.
     활성 판정은 activePreset() 이 날짜값으로 역산한다.
     원본 DateRangeFilter.tsx:74-77(판정) · :99(aria-pressed 고지). */
  var ap = activePreset();
  QA('.preset-btn', sec).forEach(function(b){
    var mine = (b.dataset['for'] === PF.gran), on = mine && (b.dataset.preset === ap);
    b.hidden = !mine;
    b.classList.toggle('active', on);
    b.setAttribute('aria-pressed', on ? 'true' : 'false');
  });
  QA('.toggle-btn', sec).forEach(function(b){ b.classList.toggle('active', b.dataset.gran === PF.gran); });
  var fi = M('pf-from', 'invest-profit'), ti = M('pf-to', 'invest-profit');
  fi.value = PF.from; ti.value = PF.to;
  /* 역전 범위 방어 — 안내문 + 조회 버튼 비활성. 원본 DateRangeFilter.tsx:79, 138-140.
     달력의 min/max 상호 제한(원본 :116, :122)은 걸지 않는다. 걸면 지금 기간보다 앞쪽으로
     옮기려고 종료일부터 열었을 때 달력이 통째로 막혀, 피커가 어느 단위에서도 살아 있어야
     한다는 규칙과 어긋난다. 어긋난 범위는 안내문과 비활성 버튼으로 잡는다. */
  var badRange = !!(PF.from && PF.to && PF.from > PF.to);
  M('pf-warn', 'invest-profit').hidden = !badRange;
  M('pf-go', 'invest-profit').disabled = badRange;
  M('pf-tbl-title', 'invest-profit').textContent = GRAN_LABEL[PF.gran] + ' 투자수익';

  var exec = sum(rows, 'exec'), profit = sum(rows, 'profit'), repay = sum(rows, 'repay');
  var wAvg = rows.length ? wavg(rows, 'w', 'exec') : 0;
  var tyExec = tyOfRows(rows);
  var tyAsset = rows.length ? tyAssetOf(tyExec, exec) : 0;
  M('pf-stat', 'invest-profit').innerHTML =
    '<div class="stat"><div class="summary-label">검색대상기간</div>' +
      '<div class="stat-period">' + presetLabel() + '</div>' +
      '<div class="summary-sub mono">' + PF.from + ' ~ ' + PF.to + '</div></div>' +
    '<div class="stat"><div class="summary-label">투자실행금</div>' +
      '<div class="summary-value">' + fmt(exec) + '<span class="unit">원</span></div></div>' +
    '<div class="stat"><div class="summary-label">투자수익</div>' +
      '<div class="summary-value">' + fmt(profit) + '<span class="unit">원</span></div></div>' +
    '<div class="stat"><div class="summary-label">Ty수익율</div><div class="ty-split">' +
      '<div><div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자실행금액 대비</span>' +
        '<span class="tip-panel">PSMR × 365 ÷ PSD' +
          '<span class="tip-row"><span>PSMR</span><span class="tip-green">투자수익 ÷ 투자실행금</span></span>' +
          '<span class="tip-row"><span>PSD</span><span class="tip-green">투자실행금 가중평균 금융일수</span></span>' +
        '</span></span></div>' +
        '<div class="summary-value">' + fx(tyExec, 2) + '<span class="unit">%</span></div></div>' +
      '<div><div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자자산 대비</span>' +
        '<span class="tip-panel">(투자실행금액 대비 × PSA) ÷ (PSA + PSC)' +
          '<span class="tip-row"><span>PSA</span><span class="tip-green">' + fmt(exec) + '원</span></span>' +
          '<span class="tip-row"><span>PSC</span><span class="tip-green">' + fmt((cashRow() ? cashRow().amount : 0) * ecDays()) + '원</span></span>' +
          '<span class="tip-row sum"><span>EC ' + ecDays() + '일 합</span><span>기간 순현금 합계</span></span>' +
        '</span></span></div>' +
        '<div class="summary-value">' + fx(tyAsset, 2) + '<span class="unit">%</span></div></div>' +
    '</div></div>';

  var box = M('pf-tbl', 'invest-profit');
  var PF_HEAD = '<th>' + GRAN_COL[PF.gran] + '</th><th class="num">상환액</th>' +
                '<th class="num">투자실행금</th><th class="num">투자 수익</th>' +
                '<th class="num">W금융일수</th><th class="num">Ty수익율</th>';
  if(!rows.length){
    box.innerHTML = emptyTable(PF_HEAD, 6, '조회 결과가 없습니다.');
  } else {
    var view = rows, i;
    var t = '<div class="tbl-scroll"><table class="tbl"><thead><tr>' + PF_HEAD + '</tr></thead><tbody>';
    for(i = 0; i < view.length; i++){
      var r = view[i];
      t += '<tr><td class="mono">' + r.d + '</td><td class="num">' + fmt(r.repay) + '</td>' +
           '<td class="num">' + fmt(r.exec) + '</td><td class="num"><span class="strong">' + fmt(r.profit) + '</span></td>' +
           '<td class="num">' + fx(r.w, 1) + '</td><td class="num">' + pct(r.ty, 2) + '</td></tr>';
    }
    t += '</tbody><tfoot><tr><td>합계</td><td class="num">' + fmt(repay) + '</td><td class="num">' + fmt(exec) +
         '</td><td class="num">' + fmt(profit) + '</td>' +
         '<td class="num">' + fx(wAvg, 1) + '<span class="avg-sub">가중평균</span></td>' +
         '<td class="num">' + fx(tyExec, 2) + '%<span class="avg-sub">가중평균</span></td></tr></tfoot>';
    t += '</table></div>';
    box.innerHTML = t;
  }
  var x1 = M('pf-xls1', 'invest-profit'), x2 = M('pf-xls2', 'invest-profit');
  x1.disabled = !rows.length; x2.disabled = !rows.length;
  
};

'''

JS += r'''
/* ───────── 투자 시뮬레이션 ─────────
   기존 화면과 완전히 별개다. SIM 은 IA·PF·MC·AQ·CT 와 독립된 상태 객체이고
   simRun() 은 MERCHANTS·ASSET_ROWS·DAILY 를 읽지도 쓰지도 않는다.
   산식 출처 — 대표 정의서 [1번 이미지] Ai·Di·W·Ty·S · [2번 이미지] Mi·Bi·PSA·PSM·PSD·PSMR·PSC.
   앵커는 순지급액이다(채권매입수수료 = 순지급액 x 할인율 · D-31). 일별 원장 daily_ledger.py 도 같은 앵커라
   투자 수익 화면과 이 화면의 같은 열은 같은 산식에서 나온다. */
var SIM_PLAT = [
  {k:'card', label:'카드사',     d:2},
  {k:'bm',   label:'배달의민족', d:3},
  {k:'cpe',  label:'쿠팡이츠',   d:5},
  {k:'yo',   label:'요기요',     d:6}
];
/* 플랫폼별 만기 = round(DURATION) — platform_duration.py:46 실측 2.0 / 3.4 / 4.7 / 6.2.
   채권 한 건의 금융일수는 선정산일과 정산예정일의 날짜 차이라 정수만 나온다. 실측 4.7 일(쿠팡이츠)은
   플랫폼 전체의 금액가중 평균이고, 채권 1건에 그 평균을 그대로 넣을 수는 없어 반올림한 5 를 기본값으로 둔다.
   정산예정일 칸을 직접 고치면 그 행의 만기는 입력한 날짜대로 다시 잡힌다. */
var SIM_DUR = {card:2, bm:3, cpe:5, yo:6};
function simLabel(k){ for(var i = 0; i < SIM_PLAT.length; i++) if(SIM_PLAT[i].k === k) return SIM_PLAT[i].label; return k; }
function simDue(sd, plat){ return sd ? addDays(sd, SIM_DUR[plat] || 0) : sd; }
/* 미회수 4행(1~4)은 30:30:20:20 — 2x0.3 + 3x0.3 + 5x0.2 + 6x0.2 = 3.7 로, W 가 투자 자산 화면의
   3.7 일과 같은 자리에 선다. 만기 4행(5~8)은 40:40:10:10 — PSD 3.1 로 투자 수익 화면 일별 합계와
   같은 자리다. 미회수 합 10억은 그대로라 투자실행액 998,900,000 도 그대로다. */
function simSeedRows(){
  return [
    {plat:'card', amt:300000000, sd:'2026-08-26', dd:'2026-08-28'},
    {plat:'bm',   amt:300000000, sd:'2026-08-26', dd:'2026-08-29'},
    {plat:'cpe',  amt:200000000, sd:'2026-08-26', dd:'2026-08-31'},
    {plat:'yo',   amt:200000000, sd:'2026-08-26', dd:'2026-09-01'},
    {plat:'card', amt:200000000, sd:'2026-08-22', dd:'2026-08-24'},
    {plat:'bm',   amt:200000000, sd:'2026-08-22', dd:'2026-08-25'},
    {plat:'cpe',  amt:50000000,  sd:'2026-08-21', dd:'2026-08-26'},
    {plat:'yo',   amt:50000000,  sd:'2026-08-21', dd:'2026-08-27'}
  ];
}
/* 미지급률·과지급률 기본값은 S입금부족율이 투자 자산 화면의 0.07% 와 같아지는 자리에 둔다 —
   S = (미지급률 - 과지급률) / (1 - 할인율) = 0.07 / 0.9989 = 0.07%. 두 화면이 같은 값을 띄운다. */
var SIM_DEFAULT = {r:0.11, cash:105300000, unpaid:0.08, over:0.01,
                   from:'2026-08-21', to:'2026-08-27'};
function simSeed(){
  var o = {rows:simSeedRows(), result:null, running:false, redraw:true}, k;
  for(k in SIM_DEFAULT) o[k] = SIM_DEFAULT[k];
  return o;
}
var SIM = simSeed();

function simNum(v){ var n = parseFloat(v); return isFinite(n) ? n : 0; }
function simDays(a, b){ return Math.round((dt(b) - dt(a)) / 86400000); }
/* 절사 전에 부동소수 잡음만 걷어낸다 — 0.03 - 0.01 이 0.019999999999999997 로 잡히는 자리.
   산식은 그대로 절사(대표 정의서 원 단위)다. */
function simFloor(x){ return Math.floor(Number(Number(x).toFixed(6))); }
function simAmtTotal(){ var t = 0, i; for(i = 0; i < SIM.rows.length; i++) t += SIM.rows[i].amt; return t; }

/* 채권 1건 — Ai · Di · 채권매입수수료 · 미지급 차감 · 투자수익 Mi · 상환액 Bi */
function simBond(row, r, dedRate){
  var A   = simFloor(row.amt * (1 - r));
  var D   = simDays(row.sd, row.dd);
  var fee = simFloor(row.amt * r);
  var ded = simFloor(Math.max(0, dedRate) * row.amt);
  return {plat:row.plat, amt:row.amt, sd:row.sd, dd:row.dd,
          D:D, A:A, fee:fee, ded:ded, M:fee - ded, B:row.amt - ded};
}

function simRun(){
  var r = SIM.r / 100, ded = (SIM.unpaid - SIM.over) / 100, i;
  var bonds = SIM.rows.map(function(x){ return simBond(x, r, ded); });
  var out = [], mat = [];
  for(i = 0; i < bonds.length; i++){
    var b = bonds[i];
    if(b.dd > SIM.to){ b.kind = '미회수'; out.push(b); }
    else if(b.dd >= SIM.from){ b.kind = '만기'; mat.push(b); }
    else b.kind = '기간 밖';
  }

  /* ── 투자 자산 (회수되지 않은 순지급액) ── */
  var EXEC = sum(out, 'A');
  var W    = EXEC ? out.reduce(function(t, b){ return t + b.A * b.D; }, 0) / EXEC : 0;
  var TY   = W ? SIM.r * 365 / W : 0;
  var S    = (SIM.unpaid - SIM.over) / (1 - r);
  var TOT  = EXEC + SIM.cash;
  var SH   = ratios([{amount:EXEC}, {amount:SIM.cash}], TOT);

  /* ── 투자 수익 (기간 안에 만기가 도래한 채권) ── */
  var PSA  = sum(mat, 'A'), PSM = sum(mat, 'M'), PSB = sum(mat, 'B');
  var PSD  = PSA ? mat.reduce(function(t, b){ return t + b.A * b.D; }, 0) / PSA : 0;
  var PSMR = PSA ? PSM / PSA * 100 : 0;
  var TY4  = PSD ? PSMR * 365 / PSD : 0;
  var ECD  = (SIM.from && SIM.to) ? simDays(SIM.from, SIM.to) + 1 : 0;
  var PSC  = SIM.cash * ECD;
  var TY5  = (PSA + PSC) ? TY4 * PSA / (PSA + PSC) : 0;

  /* ── 일별 ── */
  var day = {}, keys = [];
  mat.forEach(function(b){
    var g = day[b.dd];
    if(!g){ g = day[b.dd] = {d:b.dd, A:0, M:0, B:0, wx:0}; keys.push(b.dd); }
    g.A += b.A; g.M += b.M; g.B += b.B; g.wx += b.A * b.D;
  });
  keys.sort();
  var rows = keys.map(function(k){
    var g = day[k];
    g.W  = g.A ? g.wx / g.A : 0;
    g.TY = (g.A && g.W) ? (g.M / g.A * 100) * 365 / g.W : 0;
    return g;
  });

  SIM.result = {bonds:bonds, out:out, mat:mat, cash:SIM.cash, from:SIM.from, to:SIM.to,
                EXEC:EXEC, W:W, TY:TY, S:S, TOT:TOT, SH:SH,
                PSA:PSA, PSM:PSM, PSB:PSB, PSD:PSD, PSMR:PSMR,
                TY4:TY4, TY5:TY5, ECD:ECD, PSC:PSC, rows:rows};
}

/* 실행 가능 조건 — 어드민 page.tsx:308 과 같은 방식으로, 못 돌릴 입력이면 버튼을 막는다 */
function simCanRun(){
  if(!SIM.rows.length) return false;
  if(!SIM.from || !SIM.to || SIM.from > SIM.to) return false;
  if(!(SIM.r > 0) || SIM.r >= 100) return false;
  for(var i = 0; i < SIM.rows.length; i++){
    var x = SIM.rows[i];
    if(!x.sd || !x.dd || x.sd > x.dd) return false;
  }
  return true;
}

/* ── 그리기 ── */
function simSetVal(name, v){
  var el = M(name, 'invest-sim');
  if(!el || document.activeElement === el) return;   /* 치는 중에는 캐럿을 건드리지 않는다 */
  if(el.value !== String(v)) el.value = v;
}
function simRowHtml(x, i, n){
  var o = '', j;
  for(j = 0; j < SIM_PLAT.length; j++)
    o += '<option value="' + SIM_PLAT[j].k + '"' + (SIM_PLAT[j].k === x.plat ? ' selected' : '') + '>' + SIM_PLAT[j].label + '</option>';
  return '<div class="sim-row" data-row="' + i + '">' +
    '<span class="sim-no">' + (i + 1) + '</span>' +
    '<select class="input sim-plat" data-act="sim-row" data-i="' + i + '" data-f="plat" aria-label="플랫폼">' + o + '</select>' +
    '<input type="number" class="input sim-amt" data-act="sim-row" data-i="' + i + '" data-f="amt" step="1000000" min="0" value="' + x.amt + '" aria-label="순지급액">' +
    '<span class="sim-unit">원</span>' +
    '<input type="date" class="input sim-date" data-act="sim-row" data-i="' + i + '" data-f="sd" value="' + x.sd + '" aria-label="선정산일">' +
    '<input type="date" class="input sim-date" data-act="sim-row" data-i="' + i + '" data-f="dd" value="' + x.dd + '" aria-label="정산예정일">' +
    '<span class="sim-days"></span>' +
    (n > 1 ? '<button type="button" class="sim-del" data-act="sim-del" data-i="' + i + '">삭제</button>' : '') +
    '</div>';
}
function simDrawRows(){
  var h = '', i;
  for(i = 0; i < SIM.rows.length; i++) h += simRowHtml(SIM.rows[i], i, SIM.rows.length);
  M('sim-rows', 'invest-sim').innerHTML = h;
}
/* 값 칸은 그대로 두고 파생 표시만 고친다 — 한 글자 칠 때마다 행을 다시 그리면 포커스가 날아간다 */
function simSyncRows(){
  var els = QA('.sim-row', M('sim-rows', 'invest-sim')), i;
  for(i = 0; i < els.length; i++){
    var x = SIM.rows[i]; if(!x) continue;
    var ok = x.sd && x.dd && x.sd <= x.dd;
    Q('.sim-days', els[i]).textContent = ok ? (simDays(x.sd, x.dd) + '일') : '-';
    var dd = Q('[data-f="dd"]', els[i]);
    if(dd && document.activeElement !== dd && dd.value !== x.dd) dd.value = x.dd;
  }
}
function simTyTip(R){
  return '<div class="stat"><div class="summary-label">Ty수익율</div><div class="ty-split">' +
    '<div><div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자실행금액 대비</span>' +
      '<span class="tip-panel">PSMR × 365 ÷ PSD' +
        '<span class="tip-row"><span>PSMR</span><span class="tip-green">투자수익 ÷ 투자실행금</span></span>' +
        '<span class="tip-row"><span>PSD</span><span class="tip-green">투자실행금 가중평균 금융일수</span></span>' +
      '</span></span></div>' +
      '<div class="summary-value' + (R.TY4 < 0 ? ' neg' : '') + '">' + fx(R.TY4, 2) + '<span class="unit">%</span></div></div>' +
    '<div><div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자자산 대비</span>' +
      '<span class="tip-panel">(투자실행금액 대비 × PSA) ÷ (PSA + PSC)' +
        '<span class="tip-row"><span>PSA</span><span class="tip-green">' + fmt(R.PSA) + '원</span></span>' +
        '<span class="tip-row"><span>PSC</span><span class="tip-green">' + fmt(R.PSC) + '원</span></span>' +
        '<span class="tip-row sum"><span>EC ' + R.ECD + '일 합</span><span>기간 순현금 합계</span></span>' +
      '</span></span></div>' +
      '<div class="summary-value' + (R.TY5 < 0 ? ' neg' : '') + '">' + fx(R.TY5, 2) + '<span class="unit">%</span></div></div>' +
  '</div></div>';
}
function simResultHtml(){
  var R = SIM.result, i, b, h = '';

  /* ① 투자 요약 */
  h += '<div class="summary-grid">' +
    '<div class="summary-card highlight"><div class="summary-label">투자자산</div>' +
      '<div class="summary-value">' + fmt(R.TOT) + '<span class="unit">원</span></div>' +
      '<div class="summary-sub">투자실행액 + 순현금</div></div>' +
    '<div class="summary-card"><div class="summary-label">투자실행액</div>' +
      '<div class="summary-value">' + fmt(R.EXEC) + '<span class="unit">원</span></div>' +
      '<div class="summary-sub">비중 ' + fx(R.SH[0], 1) + '% · 보관 ㈜페이허그</div></div>' +
    '<div class="summary-card"><div class="summary-label">순현금</div>' +
      '<div class="summary-value">' + fmt(R.cash) + '<span class="unit">원</span></div>' +
      '<div class="summary-sub">비중 ' + fx(R.SH[1], 1) + '% · 보관 ㈜쿠콘</div></div>' +
    '<div class="summary-card"><div class="summary-label">Ty수익율</div>' +
      '<div class="summary-value">' + fx(R.TY, 2) + '<span class="unit">%</span></div>' +
      '<div class="summary-sub">W금융일수 ' + fx(R.W, 1) + '일 기준</div></div>' +
  '</div>';

  /* ② 채권별 산출 — 기간 밖 행은 회색 이탤릭으로 두고 집계에서 뺀다 (page.tsx:366-369 · :560) */
  h += '<div class="tbl-wrap mb-6"><div class="tbl-head"><h2>채권별 산출</h2></div>' +
    '<div class="tbl-scroll"><table class="tbl"><thead><tr>' +
    '<th class="num">#</th><th>구분</th><th>플랫폼</th><th class="num">순지급액</th>' +
    '<th class="num">금융일수</th><th class="num">투자실행금</th><th class="num">채권매입수수료</th>' +
    '<th class="num">미지급 차감</th><th class="num">투자수익</th><th class="num">상환액</th>' +
    '</tr></thead><tbody>';
  for(i = 0; i < R.bonds.length; i++){
    b = R.bonds[i];
    h += '<tr' + (b.kind === '기간 밖' ? ' class="sim-skip"' : '') + '>' +
      '<td class="num">' + (i + 1) + '</td><td>' + b.kind + '</td><td>' + simLabel(b.plat) + '</td>' +
      '<td class="num">' + fmt(b.amt) + '</td><td class="num">' + b.D + '</td>' +
      '<td class="num">' + fmt(b.A) + '</td><td class="num">' + fmt(b.fee) + '</td>' +
      '<td class="num">' + fmt(b.ded) + '</td>' +
      '<td class="num"><span class="strong">' + fmt(b.M) + '</span></td>' +
      '<td class="num">' + fmt(b.B) + '</td></tr>';
  }
  h += '</tbody></table></div></div>';

  /* ③ 현황 — 투자 자산 */
  h += '<div class="tbl-wrap mb-6"><div class="tbl-head"><h2>현황</h2></div>' +
    '<div class="tbl-scroll"><table class="tbl"><thead><tr><th>자산 구분</th><th class="num">금액 (원)</th>' +
    '<th class="num">W금융일수</th><th class="num">S입금부족율</th><th class="num">Ty수익율</th>' +
    '<th class="num">비중</th><th>보관</th></tr></thead><tbody>' +
    '<tr><td><span class="name">투자실행액</span></td><td class="num"><span class="strong">' + fmt(R.EXEC) + '</span></td>' +
      '<td class="num">' + fx(R.W, 1) + '일</td><td class="num">' + pct(R.S, 2) + '</td>' +
      '<td class="num">' + pct(R.TY, 2) + '</td><td class="num">' + fx(R.SH[0], 1) + '%</td><td>㈜페이허그</td></tr>' +
    '<tr><td><span class="name">순현금</span></td><td class="num"><span class="strong">' + fmt(R.cash) + '</span></td>' +
      '<td class="num"><span class="none">-</span></td><td class="num"><span class="none">-</span></td>' +
      '<td class="num"><span class="none">-</span></td><td class="num">' + fx(R.SH[1], 1) + '%</td><td>㈜쿠콘</td></tr>' +
    '<tr class="total-row"><td>합계 (투자자산)</td><td class="num">' + fmt(R.TOT) + '</td>' +
      '<td class="num"><span class="none">-</span></td><td class="num"><span class="none">-</span></td>' +
      '<td class="num"><span class="none">-</span></td>' +
      '<td class="num">' + fx(R.SH[0] + R.SH[1], 1) + '%</td><td><span class="none">-</span></td></tr>' +
    '</tbody></table></div></div>';

  /* ④ 수익 현황 — 투자 수익 */
  h += '<div class="card mb-6"><div class="card-head"><h2 class="card-title">수익 현황</h2></div>' +
    '<div class="stat-grid">' +
    '<div class="stat"><div class="summary-label">검색대상기간</div>' +
      '<div class="stat-period">' + R.ECD + '일</div>' +
      '<div class="summary-sub mono">' + R.from + ' ~ ' + R.to + '</div></div>' +
    '<div class="stat"><div class="summary-label">투자실행금</div>' +
      '<div class="summary-value">' + fmt(R.PSA) + '<span class="unit">원</span></div></div>' +
    '<div class="stat"><div class="summary-label">투자수익</div>' +
      '<div class="summary-value' + (R.PSM < 0 ? ' neg' : '') + '">' + fmt(R.PSM) + '<span class="unit">원</span></div></div>' +
    simTyTip(R) +
    '</div></div>';

  /* ⑤ 일별 투자수익 */
  var HEAD = '<th>정산예정일</th><th class="num">상환액</th><th class="num">투자실행금</th>' +
             '<th class="num">투자 수익</th><th class="num">W금융일수</th><th class="num">Ty수익율</th>';
  h += '<div class="tbl-wrap mb-6"><div class="tbl-head"><div class="left">' +
       '<h2 class="card-title">일별 투자수익</h2></div></div>';
  if(!R.rows.length){
    h += emptyTable(HEAD, 6, '조회 결과가 없습니다.');
  } else {
    h += '<div class="tbl-scroll"><table class="tbl"><thead><tr>' + HEAD + '</tr></thead><tbody>';
    for(i = 0; i < R.rows.length; i++){
      var g = R.rows[i];
      h += '<tr><td class="mono">' + g.d + '</td><td class="num">' + fmt(g.B) + '</td>' +
        '<td class="num">' + fmt(g.A) + '</td><td class="num"><span class="strong">' + fmt(g.M) + '</span></td>' +
        '<td class="num">' + fx(g.W, 1) + '</td><td class="num">' + pct(g.TY, 2) + '</td></tr>';
    }
    h += '</tbody><tfoot><tr><td>합계</td><td class="num">' + fmt(R.PSB) + '</td>' +
      '<td class="num">' + fmt(R.PSA) + '</td><td class="num">' + fmt(R.PSM) + '</td>' +
      '<td class="num">' + fx(R.PSD, 1) + '<span class="avg-sub">가중평균</span></td>' +
      '<td class="num">' + fx(R.TY4, 2) + '%<span class="avg-sub">가중평균</span></td></tr></tfoot></table></div>';
  }
  h += '</div>';
  return h;
}

RENDER['invest-sim'] = function(){
  simSetVal('sim-r', SIM.r); simSetVal('sim-cash', SIM.cash);
  simSetVal('sim-unpaid', SIM.unpaid); simSetVal('sim-over', SIM.over);
  simSetVal('sim-from', SIM.from); simSetVal('sim-to', SIM.to);
  if(SIM.redraw){ simDrawRows(); SIM.redraw = false; }
  simSyncRows();
  M('sim-total', 'invest-sim').textContent = '총 ' + SIM.rows.length + '건, 합계 ' + fmt(simAmtTotal()) + '원';
  /* 기간 역전 안내 — 원문 payhug-admin-web/components/DateRangeFilter.tsx:14 · 표시 조건 :79 · 자리 :139 */
  M('sim-warn', 'invest-sim').hidden = !(SIM.from && SIM.to && SIM.from > SIM.to);
  var btn = M('sim-go', 'invest-sim');
  btn.textContent = SIM.running ? '계산 중...' : '시뮬레이션 실행';
  btn.disabled = SIM.running || !simCanRun();
  M('sim-out', 'invest-sim').innerHTML = SIM.result ? simResultHtml() : '';
};

/* ── 조작 ── */
var simTimer = null;
function clearSimTimer(){ if(simTimer){ clearTimeout(simTimer); simTimer = null; } }
function simTakeVar(el){
  var k = el.dataset.k;
  if(k === 'from' || k === 'to') SIM[k] = el.value;
  else SIM[k] = simNum(el.value);
  refresh('invest-sim');
}
function simTakeRow(el){
  var i = parseInt(el.dataset.i, 10), f = el.dataset.f, x = SIM.rows[i];
  if(!x) return;
  if(f === 'amt') x.amt = Math.max(0, simNum(el.value));
  else if(f === 'plat'){ x.plat = el.value; x.dd = simDue(x.sd, x.plat); }
  else x[f] = el.value;
  refresh('invest-sim');
}
'''

JS += r'''
/* ───────── 가맹점 ───────── */
function mcRows(){
  var f = MC.applied; if(!f) return MERCHANTS;
  return MERCHANTS.filter(function(m){
    if(f.sector && f.sector !== '전체' && m.sector !== f.sector) return false;
    if(f.buyer && f.buyer !== '전체' && (m.buyer + ' ' + m.buyerName) !== f.buyer) return false;
    if(f.kw){
      var k = f.kw.toLowerCase();
      var hay = (m.mid + ' ' + m.name + ' ' + m.biz + ' ' + m.ceo + ' ' + m.item).toLowerCase();
      if(hay.indexOf(k) < 0) return false;
    }
    return true;
  });
}
function mcChips(){
  var f = MC.applied; if(!f) return [];
  var out = [];
  if(f.sector && f.sector !== '전체') out.push({k:'sector', t:'업종: ' + f.sector});
  if(f.buyer && f.buyer !== '전체') out.push({k:'buyer', t:'채권매입업체: ' + f.buyer});
  if(f.kw) out.push({k:'kw', t:'검색어: ' + f.kw});
  return out;
}
RENDER['merchants'] = function(){
  var sec = SEC('merchants'), i;
  /* 업종 필터는 네이티브 select — 원본 어드민은 커스텀 드롭다운 0건, 15파일 25곳 전부 <select>. */
  var sel = M('mc-sector', 'merchants');
  if(sel.options.length !== SECTORS.length){
    var opt = '';
    for(i = 0; i < SECTORS.length; i++) opt += '<option value="' + SECTORS[i] + '">' + SECTORS[i] + '</option>';
    sel.innerHTML = opt;
  }
  sel.value = MC.sector;
  M('mc-buyer', 'merchants').value = MC.buyer;
  var kwEl = M('mc-kw', 'merchants');
  if(kwEl !== document.activeElement) kwEl.value = MC.kw;

  var chips = mcChips(), ch = '';
  if(chips.length){
    ch = '<div class="chip-row"><span class="chip-label">적용된 조건</span>';
    for(i = 0; i < chips.length; i++)
      ch += '<span class="chip">' + chips[i].t + ' <button aria-label="조건 해제" data-act="mc-chip-off" data-key="' + chips[i].k + '">' + svg('x', 2.5) + '</button></span>';
    ch += '<button class="chip-clear" data-act="mc-reset">조건 초기화</button></div>';
  }
  M('mc-chips', 'merchants').innerHTML = ch;

  /* 정렬 머리글 없음 — 대표 미팅 2026-08-28 M-3(정렬 필터 삭제). 표는 원장 순서 그대로다. */
  var rows = mcRows();
  var mcSize = psz('mc-tbl');
  var pages = Math.max(1, Math.ceil(rows.length / mcSize));
  if(MC.page > pages) MC.page = 1;
  var slice = rows.slice((MC.page - 1) * mcSize, MC.page * mcSize);
  var t = '<div class="tbl-scroll"><table class="tbl"><thead><tr>' +
    '<th class="no">No</th><th>가맹점ID</th><th>가맹점명</th><th>사업자번호</th>' +
    '<th>대표자</th><th>업종</th><th>종목</th><th>채권매입업체ID</th></tr></thead><tbody>';
  if(!rows.length){
    t += emptyRow(8, '검색 결과가 없습니다.');
  } else {
    for(i = 0; i < slice.length; i++){
      var m = slice[i];
      /* 순번은 쪽이 넘어가도 이어진다 — 계약기록 표와 같은 규칙(ct-tbl). */
      t += '<tr data-mid="' + m.mid + '">' +
           '<td class="no">' + ((MC.page - 1) * mcSize + i + 1) + '</td>' +
           '<td class="mono">' + m.mid + '</td><td><span class="name">' + m.name + '</span></td>' +
           '<td class="mono">' + m.biz + '</td><td>' + m.ceo + '</td><td>' + m.sector + '</td><td>' + m.item + '</td>' +
           '<td><span class="badge sm badge-primary">' + m.buyer + '</span> ' + m.buyerName + '</td></tr>';
    }
  }
  M('mc-tbl', 'merchants').innerHTML = t + '</tbody></table></div>';
  M('mc-size', 'merchants').innerHTML = rows.length ? sizeSel('mc-tbl') : '';
  var mcp = M('mc-page', 'merchants');
  mcp.innerHTML = rows.length ? pageBar(MC.page, pages, 'mc-page',
    '총 <b class="mono">' + rows.length + '</b>건') : '';
  mcp.hidden = !rows.length;
};

/* ───────── 정산채권 양수 ───────── */
function aqCount(){ var n = 0; for(var i = 0; i < AQ.sel.length; i++) if(AQ.sel[i]) n++; return n; }
function aqSignedCount(){ var n = 0; for(var i = 0; i < AQ.signed.length; i++) if(AQ.signed[i]) n++; return n; }
RENDER['acquisition-list'] = function(){
  var i, done = aqSignedCount(), wait = SIGNQ.length - done;
  M('aq-title', 'acquisition-list').textContent = '서명 대기 목록';
  var note;
  if(AQ.phase === 'signing') note = '서명 대기 <b class="mono">' + wait + '건</b> · 선택 <b class="mono">' + aqCount() + '건</b> 서명 처리 중.';
  else if(done) note = '서명 완료 <b class="mono">' + done + '건</b> · 서명 대기 <b class="mono">' + wait + '건</b>.';
  else note = '서명 대기 <b class="mono">' + wait + '건</b>.';
  M('aq-notice', 'acquisition-list').innerHTML = note;

  /* 서명이 끝난 행은 대기 목록에서 빠진다. 결과는 메모리에만 있어 새로고침하면 되돌아온다. */
  var h = '', shown = 0;
  for(i = 0; i < SIGNQ.length; i++){
    if(AQ.signed[i]) continue;
    var s = SIGNQ[i], sel = AQ.sel[i];
    shown++;
    /* 행 어디를 눌러도 선택된다 — 체크박스와 계약서보기는 각자 data-act 를 가져
       closest() 가 먼저 잡으므로 행 토글과 겹쳐 상쇄되지 않는다. */
    h += '<div class="sign-row pickable' + (sel ? ' selected' : '') + '"' +
      ' data-act="aq-row" data-i="' + i + '">' +
      '<input type="checkbox" class="chk" data-act="aq-chk" data-i="' + i + '"' + (sel ? ' checked' : '') + '>' +
      '<div style="flex:1; min-width:0"><div class="m-name">' + s.name + '</div>' +
      '<div class="m-date">계약 생성일 <span class="mono">' + s.created + '</span></div></div>' +
      '<span class="badge badge-amber">서명 대기</span>' +
      /* 계약서보기 — 서명하기와 별개 액션이다(대표 미팅 2026-08-28 M-1) */
      '<a class="doc-link" data-act="aq-view" data-i="' + i + '" href="#">계약서보기</a></div>';
  }
  M('aq-rows', 'acquisition-list').innerHTML = shown ? h : emptyLine('조회 결과가 없습니다.');

  M('ab-count').textContent = aqCount();
  var btn = M('ab-btn');
  btn.disabled = (aqCount() === 0 || AQ.phase !== 'list');
  var openN = 0;
  for(i = 0; i < SIGNQ.length; i++) if(!AQ.signed[i]) openN++;
  btn.disabled = btn.disabled || openN === 0;
  M('aq-all').disabled   = (openN === 0 || aqCount() === openN);
  M('aq-clear').disabled = (aqCount() === 0);

  var list = '';
  for(i = 0; i < SIGNQ.length; i++) if(AQ.sel[i])
    list += '<div class="row-between"><span class="n">' + SIGNQ[i].name + '</span><span class="d mono">' + SIGNQ[i].created + '</span></div>';
  M('aqc-list').innerHTML = list;
  M('aqc-count').textContent = aqCount() + '건';
  M('aqs-count').textContent = aqCount();
  var dl = '';
  for(i = 0; i < SIGNQ.length; i++) if(AQ.signed[i])
    dl += '<div class="done-item">' + svg('check') + '<span class="n">' + SIGNQ[i].name + '</span><span class="d mono">' + SIGNQ[i].created + '</span></div>';
  M('aqd-list').innerHTML = dl;
  M('aqd-count').textContent = done + '건';

  /* 계약서보기 모달 — 어느 행에서 열었는지에 따라 서명 상태·내려받을 파일이 바뀐다 */
  var di = (AQ.doc === null) ? 0 : AQ.doc, ds = SIGNQ[di], dsigned = !!AQ.signed[di];
  M('aqv-mid').textContent  = ds.mid;
  M('aqv-date').textContent = ds.created;
  var bd = M('aqv-badge');
  bd.className = 'badge ' + (dsigned ? 'badge-green' : 'badge-amber');
  bd.textContent = dsigned ? '서명 완료' : '서명 대기';
  var fl = M('aqv-file');
  fl.textContent = dsigned ? '전자서명 결과 열기' : '계약서 원문 열기';
  fl.setAttribute('href', 'assets/docs/' + encodeURIComponent(
    dsigned ? CT_SIG_PREFIX + ds.mid + CT_SIG_EXT : CONTRACT_TXT));
};

/* ───────── 계약기록 ───────── */
function ctSelCount(){ var n = 0; for(var k in CT.sel) if(CT.sel[k]) n++; return n; }
RENDER['contracts'] = function(){
  var rows0 = CT.empty ? [] : CONTRACTS, i;
  var rows = rows0;
  var ctSize = psz('ct-tbl');
  var pages = Math.max(1, Math.ceil(rows.length / ctSize));
  if(CT.page > pages) CT.page = 1;
  var slice = rows.slice((CT.page - 1) * ctSize, CT.page * ctSize);
  var n = ctSelCount();

  M('ct-count', 'contracts').innerHTML = '총 <b class="mono">' + rows.length + '</b>건';
  var dl = M('ct-dl', 'contracts');
  dl.disabled = (n === 0);
  dl.classList.toggle('armed', n > 0 && n === rows.length && rows.length > 0);
  M('ct-dl-label', 'contracts').textContent = '선택 문서 다운로드' + (n ? ' (' + n + ')' : '');
  M('ct-clear', 'contracts').disabled = (n === 0);

  var box = M('ct-tbl', 'contracts');
  var ctp = M('ct-page', 'contracts');
  var allOn = (n === rows.length);
  var CT_HEAD = '<th style="width:48px"><input type="checkbox" class="chk" data-act="ct-all"' + (allOn ? ' checked' : '') + '></th>' +
    '<th class="no">No</th><th>MID</th><th>가맹점</th>' +
    '<th>전자서명 결과</th><th class="center">서명 수단</th>';
  if(!rows.length){
    box.innerHTML = emptyTable(
      '<th style="width:48px"><input type="checkbox" class="chk" disabled></th>' +
      '<th class="no">No</th><th>MID</th><th>가맹점</th>' +
      '<th>전자서명 결과</th><th class="center">서명 수단</th>', 6, '조회 결과가 없습니다.');
    ctp.innerHTML = ''; ctp.hidden = true;
    M('ct-size', 'contracts').innerHTML = '';
    return;
  }
  ctp.hidden = false;
  var t = '<div class="tbl-scroll"><table class="tbl"><thead><tr>' + CT_HEAD + '</tr></thead><tbody>';
  for(i = 0; i < slice.length; i++){
    var c = slice[i], on = !!CT.sel[c.mid];
    /* 순번은 쪽이 넘어가도 이어진다 — 머리에 적은 총 건수와 같은 축이라야 행을 가리킬 수 있다.
       원본 어드민의 순번(sales/page.tsx:143 등)은 쪽나눔이 없는 표라 배열 인덱스 그대로다. */
    t += '<tr class="clickable' + (on ? ' selected' : '') + '" data-act="ct-row" data-mid="' + c.mid + '">' +
      '<td><input type="checkbox" class="chk" data-act="ct-chk" data-mid="' + c.mid + '"' + (on ? ' checked' : '') + '></td>' +
      '<td class="no">' + ((CT.page - 1) * ctSize + i + 1) + '</td>' +
      '<td class="mono">' + c.mid + '</td><td><span class="name">' + c.name + '</span></td>' +
      '<td><a class="file-link" data-act="ct-doc" href="assets/docs/' + encodeURIComponent(CT_SIG_PREFIX + c.mid + CT_SIG_EXT) + '" target="_blank" rel="noopener">' + CT_SIG_PREFIX + c.mid + CT_SIG_EXT + '</a></td>' +
      '<td class="center"><span class="badge badge-green">하나인증서</span></td></tr>';
  }
  box.innerHTML = t + '</tbody></table></div>';
  M('ct-size', 'contracts').innerHTML = sizeSel('ct-tbl');
  ctp.innerHTML = pageBar(CT.page, pages, 'ct-page',
    n ? '<span class="badge badge-green sel-pill">' + n + '건 선택</span>' : ' ');
};

/* ───────── 비밀번호 변경 ─────────
   규칙·문구 = payhug-merchant-web/lib/passwordPolicy.ts
   표시      = payhug-merchant-web/components/PasswordInput.tsx
   흐름      = payhug-merchant-web/app/my-info/change-password/page.tsx
   아래 문자열은 제품이 실제로 띄우는 문구다. 문서 문체로 고치지 않는다. */
var PW_ALLOWED_SPECIAL = '!@#$%^&*()';
var PW_MIN = 8, PW_MAX = 16;
var PW_SPACE_MS = 2200;                       /* usePasswordInputValue.SPACE_ERROR_DURATION */
var PW_MSG = {
  guide:           '영문, 특수문자, 숫자 조합 8자 이상',
  space:           '비밀번호에 공백을 사용할 수 없습니다.',
  disallowed:      '사용 가능한 특수문자: ! @ # $ % ^ & * ( )',
  policy:          '영문, 숫자, 특수문자를 포함한 8~16자로 입력해주세요.',
  success:         '사용 가능한 비밀번호입니다.',
  confirmDefault:  '비밀번호를 한번 더 입력해주세요.',
  confirmMatch:    '비밀번호가 일치합니다.',
  confirmMismatch: '비밀번호가 일치하지 않습니다.'
};
var PW_DONE_MSG = '비밀번호가 성공적으로 변경되었습니다. 다시 로그인해주세요.';
var PW_CAPS_MSG = 'Caps Lock이 켜져 있습니다';

var PW_EYE_ON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">' +
  '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7-10-7-10-7z"/><circle cx="12" cy="12" r="3"/></svg>';
var PW_EYE_OFF = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">' +
  '<path d="M3 3l18 18"/><path d="M10.6 10.6a2 2 0 002.8 2.8"/>' +
  '<path d="M9.4 5.2A9.5 9.5 0 0112 5c5 0 9 4.5 9 7a12 12 0 01-2.2 3.1M6.3 6.3A12.4 12.4 0 003 12c0 2.5 4 7 9 7a9.4 9.4 0 004-.9"/></svg>';
var PW_CHECK = '<svg viewBox="0 0 24 24" fill="none" stroke="#28A745" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">' +
  '<path d="M20 6L9 17l-5-5"/></svg>';
var PW_CAPS_ICO = '<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
  '<path d="M12 2L3 7v10l9 5 9-5V7l-9-5z"/><path d="M12 8v4"/><path d="M12 16h.01"/></svg>';

function pwHasSpace(v){ return /\s/.test(v); }
function pwHasAllowedSpecial(v){
  for(var i = 0; i < v.length; i++) if(PW_ALLOWED_SPECIAL.indexOf(v.charAt(i)) >= 0) return true;
  return false;
}
/* 영문·숫자·공백·허용 특수문자 어디에도 들지 않는 글자가 섞였는가 */
function pwHasDisallowed(v){
  for(var i = 0; i < v.length; i++){
    var c = v.charAt(i);
    if(/[A-Za-z0-9]/.test(c)) continue;
    if(/\s/.test(c)) continue;
    if(PW_ALLOWED_SPECIAL.indexOf(c) < 0) return true;
  }
  return false;
}
/* 저장 기준 — 출력 가능한 ASCII(0x21~0x7E)가 아닌 글자(공백·한글·이모지)는 담지 않고 16자에서 자른다.
   허용되지 않은 ASCII 특수문자는 오류를 보여야 하므로 값에 남긴다. */
function pwSanitize(raw){ return String(raw).replace(/[^\x21-\x7E]/g, '').slice(0, PW_MAX); }
function pwIsValid(v){
  return v.length >= PW_MIN && v.length <= PW_MAX &&
         /[A-Za-z]/.test(v) && /[0-9]/.test(v) && pwHasAllowedSpecial(v) &&
         !pwHasSpace(v) && !pwHasDisallowed(v);
}
/* 오류가 겹쳐도 하나만 말한다 — 공백 > 허용되지 않은 특수문자 > 조건 미충족 */
function pwError(v){
  if(v === '') return '';
  if(pwHasSpace(v)) return PW_MSG.space;
  if(pwHasDisallowed(v)) return PW_MSG.disallowed;
  if(!pwIsValid(v)) return PW_MSG.policy;
  return '';
}
function pwChecklist(v){
  return [
    {t:'8~16자',      ok: v.length >= PW_MIN && v.length <= PW_MAX},
    {t:'영문 포함',    ok: /[A-Za-z]/.test(v)},
    {t:'숫자 포함',    ok: /[0-9]/.test(v)},
    {t:'특수문자 포함', ok: pwHasAllowedSpecial(v) && !pwHasDisallowed(v)}
  ];
}
function pwCfmMatched(){ return PW.cfm !== '' && !pwHasDisallowed(PW.cfm) && PW.cfm === PW.nw; }
function pwCanSubmit(){ return PW.cur !== '' && pwIsValid(PW.nw) && pwCfmMatched(); }

function pwClearSpaceTimers(){
  if(PW.spaceTimer.nw){ clearTimeout(PW.spaceTimer.nw); PW.spaceTimer.nw = null; }
  if(PW.spaceTimer.cfm){ clearTimeout(PW.spaceTimer.cfm); PW.spaceTimer.cfm = null; }
}
/* 공백을 누르면 값에는 안 담기고, 그 사실만 2200ms 동안 문구로 뜬다 */
function pwFlagSpace(k){
  var key = (k === 'new') ? 'nw' : 'cfm';
  if(key === 'nw') PW.spaceNew = true; else PW.spaceCfm = true;
  if(PW.spaceTimer[key]) clearTimeout(PW.spaceTimer[key]);
  PW.spaceTimer[key] = setTimeout(function(){
    if(key === 'nw') PW.spaceNew = false; else PW.spaceCfm = false;
    PW.spaceTimer[key] = null;
    refresh('password');
  }, PW_SPACE_MS);
}
function pwShowDoneToast(){ showToast(PW_DONE_MSG); }

/* 새 비밀번호 칸 — usePasswordPolicyField 의 분기를 그대로 옮긴다 */
function pwNewView(){
  var v = PW.nw, valid = pwIsValid(v), disallowed = pwHasDisallowed(v);
  var out = {checklist:null, msg:null, ok:valid, error:false};
  if(v === '' && !PW.spaceNew)      out.msg = {t:PW_MSG.guide,   c:'default'};
  else if(PW.spaceNew)              out.msg = {t:PW_MSG.space,   c:'error'};
  else if(valid)                    out.msg = {t:PW_MSG.success, c:'success'};
  else {
    out.checklist = pwChecklist(v);
    if(disallowed || PW.blurred)    out.msg = {t:pwError(v),     c:'error'};
  }
  out.error = PW.spaceNew || (disallowed && v !== '') || (PW.blurred && !valid && v !== '');
  return out;
}
/* 확인 칸 — useConfirmPasswordField + getConfirmPasswordMessage. 규칙은 되풀이하지 않고 일치 여부만 말한다 */
function pwCfmView(){
  var v = PW.cfm, matched = pwCfmMatched(), msg;
  if(PW.spaceCfm)             msg = {t:PW_MSG.space,           c:'error'};
  else if(v === '')           msg = {t:PW_MSG.confirmDefault,  c:'default'};
  else if(pwHasDisallowed(v)) msg = {t:PW_MSG.disallowed,      c:'error'};
  else if(v === PW.nw)        msg = {t:PW_MSG.confirmMatch,    c:'success'};
  else                        msg = {t:PW_MSG.confirmMismatch, c:'error'};
  return {msg:msg, ok:matched, error: PW.spaceCfm || (v !== '' && !matched)};
}
function pwRulesHtml(list){
  return '<div class="pw-rules">' + list.map(function(c){
    return '<div class="r' + (c.ok ? ' ok' : '') + '"><span class="mark">' +
           (c.ok ? PW_CHECK : '<span class="dot"></span>') + '</span><span>' + c.t + '</span></div>';
  }).join('') + '</div>';
}
function pwMsgHtml(msg, gap){
  if(!msg) return '';
  return '<div class="pw-msg t-' + msg.c + (gap ? ' mt' : '') + '">' +
         (msg.c === 'success' ? PW_CHECK : '') + '<span>' + msg.t + '</span></div>';
}
RENDER['password'] = function(){
  var val = {cur:PW.cur, 'new':PW.nw, cfm:PW.cfm};
  var vis = {cur:PW.showCur, 'new':PW.showNew, cfm:PW.showCfm};
  ['cur', 'new', 'cfm'].forEach(function(k){
    var inp = M('pw-' + k, 'password');
    if(inp.value !== val[k]) inp.value = val[k];
    inp.type = vis[k] ? 'text' : 'password';
    var eye = M('pw-' + k + '-eye', 'password');
    eye.innerHTML = vis[k] ? PW_EYE_ON : PW_EYE_OFF;
    eye.setAttribute('aria-label', vis[k] ? '비밀번호 숨기기' : '비밀번호 표시');
    var caps = M('pw-' + k + '-caps', 'password');
    caps.innerHTML = PW_CAPS_ICO + '<span>' + PW_CAPS_MSG + '</span>';
    caps.hidden = (PW.caps !== k);
  });
  var nv = pwNewView(), cv = pwCfmView();
  var nf = M('pw-new-field', 'password');
  nf.classList.toggle('is-error', nv.error);
  nf.classList.toggle('is-ok', !nv.error && nv.ok);
  var cf = M('pw-cfm-field', 'password');
  cf.classList.toggle('is-error', cv.error);
  cf.classList.toggle('is-ok', !cv.error && cv.ok);
  M('pw-new-msgbox', 'password').innerHTML =
    (nv.checklist ? pwRulesHtml(nv.checklist) : '') + pwMsgHtml(nv.msg, !!nv.checklist);
  M('pw-cfm-msgbox', 'password').innerHTML = pwMsgHtml(cv.msg, false);
  M('pw-submit', 'password').disabled = !pwCanSubmit();
};

/* 새 비밀번호 칸에서 포커스가 빠진 뒤부터 규칙 오류 문구가 붙는다 (usePasswordPolicyField.handleBlur).
   Caps Lock 말풍선은 어느 칸이든 포커스가 빠지면 내린다 (PasswordInput.handleBlur). */
document.addEventListener('focusout', function(e){
  var t = e.target;
  if(!t || !t.getAttribute) return;
  var m = t.getAttribute('data-mount');
  if(m !== 'pw-cur' && m !== 'pw-new' && m !== 'pw-cfm') return;
  if(m === 'pw-new') PW.blurred = true;
  PW.caps = null;
  refresh('password');
}, true);

/* Caps Lock 감지(PasswordInput.checkCapsLock) + Enter 제출(change-password/page.tsx:104-108) */
document.addEventListener('keydown', function(e){
  var t = e.target;
  if(!t || !t.getAttribute) return;
  var m = t.getAttribute('data-mount');
  if(m !== 'pw-cur' && m !== 'pw-new' && m !== 'pw-cfm') return;
  var on = !!(e.getModifierState && e.getModifierState('CapsLock'));
  var next = on ? t.getAttribute('data-pw') : null;
  var moved = (PW.caps !== next);
  PW.caps = next;
  if(e.key === 'Enter'){
    e.preventDefault();
    if(pwCanSubmit()){ ACT['pw-submit'](t, e); return; }
  }
  if(moved) refresh('password');
}, false);

/* ───────── 엑셀 미리보기 4종 ───────── */
function sheetRow(n, cells, cls){
  var h = '<tr' + (cls ? ' class="' + cls + '"' : '') + '><th class="row-head">' + n + '</th>';
  for(var i = 0; i < cells.length; i++){
    var c = cells[i];
    if(c === null){ h += '<td class="c-empty"></td>'; continue; }
    h += '<td' + (c.c ? ' class="' + c.c + '"' : '') + (c.span ? ' colspan="' + c.span + '"' : '') + '>' + (c.v === undefined ? '' : c.v) + '</td>';
  }
  return h + '</tr>';
}
function sheetData(key){
  var i, rows = [], cols, exec = iaExecTotal(), total = assetTotal();
  var sRatio = ratios(ASSET_ROWS, total), xRatio = ratios(MERCHANTS, exec);
  if(key === 'assets-status'){
    cols = [44, 190, 175, 130, 145, 130, 120, 0];
    rows.push({n:1, c:[{v:'투자자산 현황 — 기준일 ' + BASE_DATE + ' / ' + INVESTOR, c:'c-title', span:7}]});
    rows.push({n:2, c:[null, null, null, null, null, null, null]});
    rows.push({n:3, c:[{v:'자산 구분', c:'c-head'}, {v:'금액 (원)', c:'c-head r'}, {v:'W금융일수', c:'c-head r'},
                       {v:'S입금부족율', c:'c-head r'}, {v:'Ty수익율', c:'c-head r'}, {v:'비중', c:'c-head r'}, {v:'보관', c:'c-head'}]});
    for(i = 0; i < ASSET_ROWS.length; i++){
      var a = ASSET_ROWS[i];
      rows.push({n:4 + i, c:[{v:a.name}, {v:fmt(a.amount), c:'c-num'},
        a.w === null ? {v:''} : {v:fx(a.w, 1), c:'c-num'}, a.s === null ? {v:''} : {v:pct(a.s, 2), c:'c-num'},
        a.ty === null ? {v:''} : {v:pct(a.ty, 2), c:'c-num'},
        {v:fx(sRatio[i], 1) + '%', c:'c-num'}, {v:a.keeper}]});
    }
    rows.push({n:6, cls:'r-total', c:[{v:'합계 (투자자산)'}, {v:fmt(total), c:'c-num'}, {v:''}, {v:''}, {v:''}, {v:'100.0%', c:'c-num'}, {v:''}]});
    rows.push({n:7, c:[null, null, null, null, null, null, null]});
    rows.push({n:8, c:[null, null, null, null, null, null, null]});
    rows.push({n:9, c:[null, null, null, null, null, null, null]});
    rows.push({n:10, c:[null, null, null, null, null, null, null]});
  } else if(key === 'assets-merchant'){
    cols = [44, 210, 175, 130, 145, 130, 120, 0];
    rows.push({n:1, c:[{v:'가맹점별 투자자산 — 기준일 ' + BASE_DATE + ' / ' + INVESTOR, c:'c-title', span:7}]});
    rows.push({n:2, c:[null, null, null, null, null, null, null]});
    rows.push({n:3, c:[{v:'가맹점', c:'c-head'}, {v:'투자금액 (원)', c:'c-head r'}, {v:'W금융일수', c:'c-head r'},
                       {v:'S입금부족율', c:'c-head r'}, {v:'Ty수익율', c:'c-head r'}, {v:'비중', c:'c-head r'}, null]});
    for(i = 0; i < MERCHANTS.length; i++){
      var m = MERCHANTS[i];
      rows.push({n:4 + i, c:[{v:m.name}, {v:fmt(m.amount), c:'c-num'}, {v:fx(m.w, 1), c:'c-num'},
        {v:pct(m.s, 2), c:'c-num'}, {v:pct(m.ty, 2), c:'c-num'}, {v:fx(xRatio[i], 1) + '%', c:'c-num'}, null]});
    }
    var tot = 4 + MERCHANTS.length;
    rows.push({n:tot, cls:'r-total', c:[{v:'합계'}, {v:fmt(exec), c:'c-num'}, {v:''}, {v:''}, {v:''}, {v:'100.0%', c:'c-num'}, null]});
    rows.push({n:tot + 1, c:[null, null, null, null, null, null, null]});
    rows.push({n:tot + 2, c:[null, null, null, null, null, null, null]});
  } else if(key === 'profit-status'){
    cols = [44, 300, 340, 90, 90, 90, 90, 0];
    var rw = pfRows(), pexec = sum(rw, 'exec'), pprofit = sum(rw, 'profit');
    var tyE = tyOfRows(rw);
    var tyA = rw.length ? tyAssetOf(tyE, pexec) : 0;
    rows.push({n:1, c:[{v:'투자수익 현황 — 기준일 ' + BASE_DATE + ' / ' + INVESTOR, c:'c-title', span:2}, null, null, null, null]});
    rows.push({n:2, c:[null, null, null, null, null, null, null]});
    rows.push({n:3, c:[{v:'항목', c:'c-head'}, {v:'값', c:'c-head r'}, null, null, null, null, null]});
    rows.push({n:4, c:[{v:'검색대상기간'}, {v:presetLabel() + ' (' + PF.from + ' ~ ' + PF.to + ')', c:'c-num'}, null, null, null, null, null]});
    rows.push({n:5, c:[{v:'투자실행금'}, {v:fmt(pexec), c:'c-num'}, null, null, null, null, null]});
    rows.push({n:6, c:[{v:'투자수익'}, {v:fmt(pprofit), c:'c-num'}, null, null, null, null, null]});
    rows.push({n:7, c:[{v:'Ty수익율 (투자실행금액 대비)'}, {v:fx(tyE, 2) + '%', c:'c-num'}, null, null, null, null, null]});
    rows.push({n:8, c:[{v:'Ty수익율 (투자자산 대비)'}, {v:fx(tyA, 2) + '%', c:'c-num'}, null, null, null, null, null]});
    rows.push({n:9, c:[null, null, null, null, null, null, null]});
    rows.push({n:10, c:[null, null, null, null, null, null, null]});
    rows.push({n:11, c:[null, null, null, null, null, null, null]});
    rows.push({n:12, c:[null, null, null, null, null, null, null]});
  } else {
    cols = [44, 140, 175, 175, 150, 130, 130, 0];
    var dr = pfRows();
    rows.push({n:1, c:[{v:GRAN_LABEL[PF.gran] + ' 투자수익 — ' + PF.from + ' ~ ' + PF.to + ' / ' + INVESTOR, c:'c-title', span:7}]});
    rows.push({n:2, c:[null, null, null, null, null, null, null]});
    rows.push({n:3, c:[{v:GRAN_COL[PF.gran], c:'c-head'}, {v:'상환액', c:'c-head r'}, {v:'투자실행금', c:'c-head r'},
                       {v:'투자 수익', c:'c-head r'}, {v:'W금융일수', c:'c-head r'}, {v:'Ty수익율', c:'c-head r'}, null]});
    for(i = 0; i < dr.length; i++){
      var d = dr[i];
      rows.push({n:4 + i, c:[{v:d.d}, {v:fmt(d.repay), c:'c-num'}, {v:fmt(d.exec), c:'c-num'},
        {v:fmt(d.profit), c:'c-num'}, {v:fx(d.w, 1), c:'c-num'}, {v:pct(d.ty, 2), c:'c-num'}, null]});
    }
    var nn = 4 + dr.length;
    rows.push({n:nn, cls:'r-total', c:[{v:'합계'}, {v:fmt(sum(dr, 'repay')), c:'c-num'}, {v:fmt(sum(dr, 'exec')), c:'c-num'},
      {v:fmt(sum(dr, 'profit')), c:'c-num'},
      {v:dr.length ? fx(wavg(dr, 'w', 'exec'), 1) : '0.0', c:'c-num'},
      {v:dr.length ? fx(tyOfRows(dr), 2) + '%' : '0.00%', c:'c-num'}, null]});
    rows.push({n:nn + 1, c:[null, null, null, null, null, null, null]});
    rows.push({n:nn + 2, c:[null, null, null, null, null, null, null]});
  }
  return {cols:cols, rows:rows};
}
function renderXls(key){
  var scr = XLSX[key].screen, meta = XLSX[xlsKey(key)], sec = SEC(scr), d = sheetData(key), i;
  M('filebar', scr).innerHTML =
    '<div class="fb-left"><div class="fb-icon">' + svg('grid', 1.8) + '</div><div>' +
      '<div class="fb-name">' + meta.file + '</div>' +
      '<div class="fb-meta"><span>' + meta.size + '</span><span class="dot">·</span>' +
      '<span>생성일시 <span class="mono">' + meta.made + '</span></span><span class="dot">·</span><span>시트 1개</span></div>' +
    '</div></div>' +
    '<a class="btn btn-primary" href="assets/xlsx/' + encodeURIComponent(meta.file) + '" download data-act="xls-get" data-xls="' + key + '">' +
      svg('excel') + ' 엑셀 파일 내려받기</a>';
  M('sheettabs', scr).innerHTML = '<span class="sheet-tab active">' + meta.sheet + '</span>';
  var cg = '<colgroup>';
  for(i = 0; i < d.cols.length; i++) cg += d.cols[i] ? '<col style="width:' + d.cols[i] + 'px">' : '<col>';
  cg += '</colgroup>';
  var head = '<thead><tr class="col-head"><th class="corner"></th><th>A</th><th>B</th><th>C</th><th>D</th><th>E</th><th>F</th><th>G</th></tr></thead>';
  var body = '<tbody>';
  for(i = 0; i < d.rows.length; i++) body += sheetRow(d.rows[i].n, d.rows[i].c, d.rows[i].cls);
  M('sheet', scr).innerHTML = cg + head + body + '</tbody>';
}
RENDER['xls-assets-status']   = function(){ renderXls('assets-status'); };
RENDER['xls-assets-merchant'] = function(){ renderXls('assets-merchant'); };
RENDER['xls-profit-status']   = function(){ renderXls('profit-status'); };
RENDER['xls-profit-daily']    = function(){ renderXls('profit-daily'); };

/* ───────── 랜딩 갤러리 ───────── */
var GALLERY = [
  ['invest-assets','card','badge-primary','투자','현황·가맹점별 투자자산·산식·엑셀/증명서 다운로드'],
  ['certificate','shield','badge-primary','투자','전자문서 미리보기·서명 검증'],
  ['invest-profit','trend','badge-primary','투자','기간 검색·일별/주별/월별 투자수익·산식'],
  ['invest-sim','chart','badge-primary','투자','기준 변수·채권 입력·투자 자산/수익 산출'],
  ['merchants','users','badge-blue','가맹점','목록·업종/채권매입업체 필터·검색'],
  ['acquisition-list','cards','badge-blue','가맹점','계약서보기 · 양수도 계약서 전자서명'],
  ['contracts','doc','badge-blue','가맹점','전자서명 결과 일괄 다운로드'],
  ['coocon','coin','badge-gray','관리','메뉴에서 We-bank 로 바로 이동'],
  ['password','lock','badge-gray','관리','로그인 비밀번호 변경'],
  ['login','lock','badge-gray','인증','사업자번호·휴대전화 로그인'],
  ['xls-assets-status','grid','badge-primary','투자','투자 자산 › 현황 표를 내려받았을 때의 엑셀 서식'],
  ['xls-assets-merchant','grid','badge-primary','투자','투자 자산 › 가맹점별 투자자산 표를 내려받았을 때의 엑셀 서식'],
  ['xls-profit-status','grid','badge-primary','투자','투자 수익 › 수익 현황 표를 내려받았을 때의 엑셀 서식'],
  ['xls-profit-daily','grid','badge-primary','투자','투자 수익 › 일별 투자수익 표를 내려받았을 때의 엑셀 서식']
];
RENDER['index'] = function(){
  var h = '';
  for(var i = 0; i < GALLERY.length; i++){
    var g = GALLERY[i], states = Object.keys(STATE_META[g[0]] || {}).filter(function(k){ return k !== 'default'; });
    h += '<button class="shot-card" data-nav="' + g[0] + '"><div class="shot-top">' +
      '<div class="shot-icon">' + svg(g[1], 1.8) + '</div><div>' +
      '<div class="shot-name">' + SCREEN_LABEL[g[0]] + '</div></div>' +
      '<span class="badge sm ' + g[2] + '">' + g[3] + '</span></div>' +
      '<p class="shot-desc">' + g[4] + (states.length ? ' · 상태 ' + states.length : '') + '</p></button>';
  }
  M('ix-gallery', 'index').innerHTML = h;
};
RENDER['login'] = function(){};
RENDER['coocon'] = function(){};
'''

# ════════════════════════════════════════════════════════════════
# JS — 조작 · 초기화
# ════════════════════════════════════════════════════════════════
JS += r'''
/* pf-date 는 인풋이라 기본 동작(캐럿·타이핑·네이티브 달력)을 막으면 안 된다 */
var KEEP_DEFAULT = ['xls-get', 'cert-pdf', 'aq-chk', 'ct-chk', 'ct-all', 'aq-file', 'ct-doc', 'pf-date'];
var ACT = {};

/* 투자 자산 */
ACT['ia-page'] = function(el){
  var p = parseInt(el.dataset.page, 10);
  if(p < 1) return;
  IA.page = p; IA.downloaded = false; refresh('invest-assets');
};
/* 엑셀 다운로드 — 원본은 버튼을 누르면 중간 화면 없이 파일이 바로 나간다
   (ExcelDownloadButton → downloadExcel → Blob → a[download].click(), lib/excel.ts:38-51).
   내려받는 동안의 라벨 교체는 PreSettlementTab.tsx:483-484 · LockAccountDeposits.tsx:309-310 규격. */
function xlsBusy(el, on){
  if(!el) return;
  if(on){
    if(el.dataset.idle === undefined) el.dataset.idle = el.innerHTML;
    el.disabled = true;
    el.innerHTML = '<span class="spinner-inline"></span>다운로드 중...';
  } else {
    el.disabled = false;
    if(el.dataset.idle !== undefined){ el.innerHTML = el.dataset.idle; delete el.dataset.idle; }
  }
}
ACT['xls-open']  = function(el){
  var k = xlsKey(el.dataset.xls);
  var meta = XLSX[k];
  pullFile('assets/xlsx/', meta.file, 0);
  if(k === 'assets-merchant'){
    IA.downloaded = true;
    toastServed = 'invest-assets/download:' + meta.file;   /* 이 클릭이 이미 파일을 내려줬다 — 재전달 금지 */
  }
  xlsBusy(el, true);
  setTimeout(function(){
    xlsBusy(el, false);
    if(k === 'assets-merchant') refresh('invest-assets');  /* 상태 전환이 syncToast 로 토스트를 낸다 */
    else showToast(meta.file + ' 내려받기 완료');
  }, 350);
};
ACT['cert-open'] = function(){ IA.cert = true; refresh('invest-assets'); };
ACT['cert-issue']= function(){ IA.cert = false; refresh('invest-assets'); go('certificate'); };
ACT['cert-pdf']  = function(){ showToast(CERT_PDF + ' 내려받기 완료'); };
ACT['xls-get']   = function(el){
  var k = xlsKey(el.dataset.xls);
  if(k === 'assets-merchant'){
    PEND['invest-assets'] = 'download';
    toastServed = 'invest-assets/download:' + XLSX[k].file;   /* 이 클릭이 이미 파일을 내려줬다 — 재전달 금지 */
  }
  showToast(XLSX[k].file + ' 내려받기 완료');
};

ACT['toast-close'] = function(){ hideToast(); };

/* 메뉴 그룹 접힘 — 원본 AdminLayout.tsx:486(<button>), :494(셰브론 -rotate-90 duration-200).
   그룹 머리 전체가 누름 대상이다. */
ACT['nav-group'] = function(el){
  var g = el.closest('.nav-group');
  if(!g) return;
  var on = g.classList.toggle('collapsed');
  el.setAttribute('aria-expanded', on ? 'false' : 'true');
};

/* 모달 닫기 (현재 화면 기준) */
ACT['modal-close'] = function(){
  if(CUR === 'invest-assets'){ IA.cert = false; }
  if(CUR === 'acquisition-list'){
    if(AQ.doc !== null){ AQ.doc = null; }        /* 계약서보기만 닫는다 — 서명 흐름은 건드리지 않는다 */
    else { clearSignTimer(); AQ.phase = 'list'; }
  }
  refresh(CUR);
};

/* 투자 수익 */
/* 프리셋은 기간을 채우고 그 자리에서 조회까지 한다 — 검색을 다시 누르게 하지 않는다.
   (원본 DateRangeFilter.tsx:63-67 은 날짜만 채우고 조회는 따로 누르게 하지만,
    이 화면은 프리셋·단위 전환 모두 즉시 반영으로 확정했다.) */
ACT['preset'] = function(el){
  var r = PRESET_RANGE[el.dataset.preset];
  PF.from = r[0]; PF.to = r[1];
  refresh('invest-profit');
};
/* 날짜 칸은 어디를 눌러도 달력이 뜬다 — 숫자 부분(2026. 08. 21.)을 눌러도 마찬가지다.
   원본 어드민은 showPicker() 를 쓰지 않아(레포 0건) 아이콘을 정확히 눌러야 열린다 — 이 산출물만 다르다.
   showPicker() 는 사용자 제스처 안에서만 되고 브라우저에 없을 수도 있어 try 로 감싼다.
   막히면 브라우저 기본 동작(아이콘 클릭·타이핑) 그대로라 잃는 것이 없다.
   키보드 Tab 으로 들어온 포커스에서는 열지 않는다 — 탭 이동마다 달력이 덮이면 키보드 조작이 막힌다. */
ACT['pf-date'] = function(el){
  try { if(el.showPicker) el.showPicker(); } catch(err) {}
};
ACT['pf-search'] = function(){
  if(PF.from > PF.to){ showInfo('시작일은 종료일보다 이후일 수 없습니다.'); return; }   /* 원본 :82-84 alert 대응 */
  refresh('invest-profit');
  showInfo('조회 결과 ' + pfRows().length + '건 · ' + PF.from + ' ~ ' + PF.to);
};
ACT['pf-reset']  = function(){ setState('invest-profit', 'default'); showInfo('검색 조건 초기화'); };
ACT['pf-gran']   = function(el){
  var g = el.dataset.gran;
  if(g === PF.gran){ refresh('invest-profit'); return; }
  PF.gran = g;
  /* 기간은 그대로 둔다 — 새 단위 경계로 넓혀 스냅할 뿐이다. 걸친 단위를 전부 덮는다.
     예) 일별 08-21~08-27 → 주별 08-17~08-30(두 주) · 월별 08-01~08-31(한 달) */
  PF.from = snapFrom(PF.from, g); PF.to = snapTo(PF.to, g);
  refresh('invest-profit');                 /* 검색을 다시 누르게 하지 않는다 */
};
/* 가맹점 */
ACT['mc-search'] = function(){
  MC.kw = M('mc-kw', 'merchants').value.trim();
  MC.buyer = M('mc-buyer', 'merchants').value;
  MC.page = 1;
  MC.applied = (MC.sector === '전체' && !MC.kw && MC.buyer === '전체') ? null
             : {sector:MC.sector, kw:MC.kw, buyer:MC.buyer};
  refresh('merchants');
  showInfo('조회 결과 ' + mcRows().length + '건');
};
ACT['mc-reset'] = function(){ setState('merchants', 'default'); showInfo('검색 조건 초기화'); };
ACT['mc-chip-off'] = function(el){
  var k = el.dataset.key;
  if(k === 'sector') MC.sector = '전체';
  if(k === 'buyer')  MC.buyer = '전체';
  if(k === 'kw')     MC.kw = '';
  MC.applied = (MC.sector === '전체' && !MC.kw && MC.buyer === '전체') ? null
             : {sector:MC.sector, kw:MC.kw, buyer:MC.buyer};
  MC.page = 1;
  refresh('merchants');
};
ACT['mc-page'] = function(el){ var p = parseInt(el.dataset.page, 10); if(p < 1) return; MC.page = p; refresh('merchants'); };

/* 정산채권 양수 */
ACT['aq-chk'] = function(el){
  var i = parseInt(el.dataset.i, 10);
  AQ.sel[i] = el.checked;
  refresh('acquisition-list');
};
ACT['aq-sign'] = function(){ if(aqCount() === 0) return; AQ.phase = 'confirm'; refresh('acquisition-list'); };
ACT['aq-sign-go'] = function(){
  AQ.phase = 'signing'; refresh('acquisition-list');
  clearSignTimer();
  signTimer = setTimeout(function(){
    signTimer = null;
    /* 서명된 행은 대기 목록에서 빠진다 — 선택도 함께 비워야 선택 건수가 없는 행을 세지 않는다 */
    for(var i = 0; i < AQ.sel.length; i++) if(AQ.sel[i]){ AQ.signed[i] = true; AQ.sel[i] = false; }
    AQ.phase = 'done';
    DIRTY['acquisition-list'] = 1;         /* 메뉴를 오가도 서명 결과가 남는다 */
    refresh('acquisition-list');
  }, 1500);
};
ACT['aq-to-contracts'] = function(){
  var mids = [], i;
  for(i = 0; i < SIGNQ.length; i++) if(AQ.signed[i]) mids.push(SIGNQ[i].mid);
  AQ.phase = 'list';
  for(i = 0; i < AQ.sel.length; i++) AQ.sel[i] = false;
  go('contracts', 'default');
  if(mids.length){                        /* 방금 서명한 건이 골라진 채로 열린다 */
    CT.sel = {};
    for(i = 0; i < mids.length; i++) CT.sel[mids[i]] = 1;
    CT.downloaded = false;
    refresh('contracts');
  }
};
ACT['aq-done-ok'] = function(){ AQ.phase = 'list'; for(var i = 0; i < AQ.sel.length; i++) AQ.sel[i] = false; refresh('acquisition-list'); };

/* 계약기록 */
ACT['ct-all'] = function(el){
  CT.sel = {};
  if(el.checked) for(var i = 0; i < CONTRACTS.length; i++) CT.sel[CONTRACTS[i].mid] = 1;
  CT.downloaded = false;
  refresh('contracts');
};
ACT['ct-chk'] = function(el){
  if(el.checked) CT.sel[el.dataset.mid] = 1; else delete CT.sel[el.dataset.mid];
  CT.downloaded = false;
  refresh('contracts');
};
ACT['ct-download'] = function(){
  if(ctSelCount() === 0) return;
  CT.downloaded = true;
  refresh('contracts');
};
ACT['ct-page'] = function(el){ var p = parseInt(el.dataset.page, 10); if(p < 1) return; CT.page = p; refresh('contracts'); };
ACT['ct-row']  = function(el){ var m = el.dataset.mid; CT.sel[m] = !CT.sel[m]; refresh('contracts'); };
ACT['ct-doc']  = function(){};   /* 링크는 기본 동작(새 창)으로 흘린다 — 행 토글과 겹치지 않게 */

/* 비밀번호 */
/* 현재 비밀번호는 원본도 걸러내지 않는다(page.tsx:113 — setCurrentPassword(e.target.value)).
   새 비밀번호 두 칸만 저장 기준을 태운다. */
function readPw(){
  PW.cur = M('pw-cur', 'password').value;
  PW.nw  = pwSanitize(M('pw-new', 'password').value);
  PW.cfm = pwSanitize(M('pw-cfm', 'password').value);
}
ACT['pw-input'] = function(){};
/* 입력 한 번을 값으로 받는 자리 — input 과 compositionend 가 같은 경로를 탄다.
   공백은 값에 담기 전 원본(raw)에서 잡아내고, 담기는 값은 저장 기준을 통과한 것만 남는다. */
function pwTake(el){
  var k = el.dataset.pw, raw = el.value;
  if(k === 'cur'){ PW.cur = raw; }
  else {
    if(/\s/.test(raw)) pwFlagSpace(k);
    if(k === 'new') PW.nw = pwSanitize(raw); else PW.cfm = pwSanitize(raw);
  }
  refresh('password');
}
/* 조합이 끝난 최종 값을 받는다 — 저장 기준이 한글 등 허용되지 않은 글자를 걸러낸다 (PasswordInput.tsx:75-78) */
document.addEventListener('compositionend', function(e){
  var el = e.target && e.target.closest && e.target.closest('[data-act="pw-input"]');
  if(el) pwTake(el);
}, false);
ACT['pw-eye'] = function(el){
  var k = el.dataset.pw;
  if(k === 'cur')      PW.showCur = !PW.showCur;
  else if(k === 'new') PW.showNew = !PW.showNew;
  else                 PW.showCfm = !PW.showCfm;
  refresh('password');
};
ACT['pw-submit'] = function(){
  readPw();
  if(!pwCanSubmit()) return;      /* 원본은 조건이 덜 차면 버튼 자체가 눌리지 않는다 */
  /* 원본은 토스트를 띄우고 세 칸을 비운다. 이어서 1.5초 뒤 로그아웃 후 로그인 화면으로 보낸다 —
     그 자동 이동은 옮기지 않았다(세션이 없는 화면 모음이고, 상태를 붙잡아 두고 봐야 한다). */
  PW.done = true;
  PW.cur = ''; PW.nw = ''; PW.cfm = ''; PW.blurred = false;
  pwClearSpaceTimers(); PW.spaceNew = false; PW.spaceCfm = false; PW.caps = null;
  refresh('password');
  pwShowDoneToast();
};

/* 목록 선택 도구 */
ACT['aq-all']   = function(){ for(var i = 0; i < SIGNQ.length; i++) if(!AQ.signed[i]) AQ.sel[i] = true; refresh('acquisition-list'); };
ACT['aq-clear'] = function(){ for(var i = 0; i < SIGNQ.length; i++) AQ.sel[i] = false; refresh('acquisition-list'); };
ACT['aq-row']   = function(el){ var i = +el.dataset.i; if(AQ.signed[i]) return; AQ.sel[i] = !AQ.sel[i]; refresh('acquisition-list'); };
ACT['aq-view']  = function(el){ AQ.doc = parseInt(el.dataset.i, 10); refresh('acquisition-list'); };
ACT['aq-file']  = function(){};   /* 모달 안 파일 링크는 기본 동작(새 창)으로 흘린다 */
ACT['ct-clear'] = function(){ CT.sel = {}; refresh('contracts'); };

/* 투자 시뮬레이션 */
ACT['sim-add'] = function(){
  var sd = SIM.to ? addDays(SIM.to, -SIM_DUR.card) : SIM.to;
  SIM.rows.push({plat:'card', amt:100000000, sd:sd, dd:SIM.to});
  SIM.redraw = true;
  refresh('invest-sim');
};
ACT['sim-del'] = function(el){
  if(SIM.rows.length <= 1) return;
  SIM.rows.splice(parseInt(el.dataset.i, 10), 1);
  SIM.redraw = true;
  refresh('invest-sim');
};
ACT['sim-run'] = function(){
  if(SIM.running || !simCanRun()) return;
  clearSimTimer();
  SIM.running = true;
  refresh('invest-sim');
  /* 계산은 그 자리에서 끝난다. 300ms 는 진행 상태를 보이기 위한 것 — 어드민 page.tsx:311 이 라벨만 바꾼다 */
  simTimer = setTimeout(function(){
    simTimer = null; SIM.running = false;
    simRun();
    refresh('invest-sim');
  }, 300);
};

/* ═══ 이벤트 바인딩 ═══ */
document.addEventListener('click', function(e){
  var t = e.target;
  if(!t || !t.closest) return;
  var a = t.closest('[data-act]');
  /* 모달 배경 클릭으로 닫기 — 패널 안쪽 클릭은 배경으로 새지 않는다.
     원본 ConfirmDialog.tsx:54-55 (백드롭 onClick + 패널 stopPropagation) 대응.
     진행 중 오버레이(acquisition-signing)만 예외 — 원본도 submitting·ocrProcessing 오버레이는 닫히지 않는다. */
  if(a && a.dataset.act === 'backdrop'){
    if(t !== a) a = t.closest('[data-act]:not([data-act="backdrop"])') || a;
    if(a.dataset.act === 'backdrop'){ e.preventDefault(); ACT['modal-close'](); return; }
  }
  if(a && ACT[a.dataset.act]){
    if(KEEP_DEFAULT.indexOf(a.dataset.act) < 0) e.preventDefault();
    ACT[a.dataset.act](a, e);
    return;
  }
  var n = t.closest('[data-nav]');
  if(n){ e.preventDefault(); go(n.dataset.nav); return; }
  if(t.closest('.sidebar-logo a')){ e.preventDefault(); go('index'); return; }
  if(t.closest('button.logout')){ e.preventDefault(); go('login'); return; }
  var link = t.closest('a[href]');
  if(link){
    var href = link.getAttribute('href');
    /* 새 창 링크는 그대로 나간다 — 쿠콘은 중간 확인 없이 바로 We-bank 로 간다
       (대표 미팅 2026-08-28 M-4). 사이드바 메뉴도 같은 링크다. */
    if(link.getAttribute('target') === '_blank') return;
    if(FILE2SCREEN[href]){ e.preventDefault(); go(FILE2SCREEN[href]); return; }
    if(STATEFILE[href]){ e.preventDefault(); var p = STATEFILE[href].split('/'); go(p[0], p[1]); return; }
    if(href.charAt(0) === '#'){
      e.preventDefault();
      return;
    }
  }
}, false);

/* ═══ 키보드 조작 — div·th 기반 컨트롤도 키로 눌린다 ═══ */
document.addEventListener('keydown', function(e){
  var t = e.target;
  if(!t || !t.closest) return;
  var k = e.key;

  /* 검색창 Enter → 조회 실행 (원본 app/sales/[bizNo]/page.tsx:558) */
  if(t.getAttribute && t.getAttribute('data-mount') === 'mc-kw' && k === 'Enter'){
    e.preventDefault(); ACT['mc-search'](t, e); return;
  }
  if(t.getAttribute && (t.getAttribute('data-mount') === 'pf-from' || t.getAttribute('data-mount') === 'pf-to') && k === 'Enter'){
    e.preventDefault(); ACT['pf-search'](t, e); return;
  }

  /* 로그인 Enter 제출 — 원본 payhug-admin-web/app/login/page.tsx:88-92.
     원본에도 <form> 은 없다. 입력의 keydown 에서 제출 요소를 그대로 누른다. */
  if(t.getAttribute && t.getAttribute('data-login') && k === 'Enter'){
    e.preventDefault();
    var sb = document.querySelector('section[data-screen="login"] .login-submit');
    if(sb) sb.click();
    return;
  }

  /* 표 행에는 tabindex 를 두지 않는다 — 원본 어드민은 레포 전체 tabIndex 0건이라
     행이 키보드 대상이 아니다. 선택은 행 클릭과 행 안 체크박스가 맡는다. */

}, false);

document.addEventListener('change', function(e){
  var el = e.target.closest && e.target.closest('[data-act]');
  if(!el) return;
  /* 날짜 입력이 조회 조건을 움직인다 — 원본 DateRangeFilter.tsx:116-123 의 value/onChange 대응.
     사용자가 직접 친 값도 여기서 받는다. */
  if(el.dataset.act === 'pf-date'){
    /* 고른 날짜는 그 자리에서 집계 단위 경계로 스냅한다 —
       주별이면 그 날짜가 속한 주(월~일), 월별이면 그 달(1일~말일)이 통째로 잡힌다. */
    if(el.dataset.which === 'to') PF.to = snapTo(el.value, PF.gran);
    else PF.from = snapFrom(el.value, PF.gran);
    refresh('invest-profit');
    return;
  }
  if(el.dataset.act === 'sim-var'){ simTakeVar(el); return; }
  if(el.dataset.act === 'sim-row'){ simTakeRow(el); return; }
  if(el.dataset.act === 'pg-size'){
    var k = el.dataset.key;
    PS[k] = parseInt(el.value, 10);
    if(k === 'ia-merch') IA.page = 1;
    if(k === 'mc-tbl')   MC.page = 1;
    if(k === 'ct-tbl')   CT.page = 1;
    refresh(CUR);
    return;
  }
  if(el.dataset.act === 'mc-sector'){
    MC.sector = el.value; MC.page = 1;
    if(MC.applied) MC.applied.sector = MC.sector;
    refresh('merchants');
    return;
  }
  if(el.dataset.act === 'mc-buyer'){
    MC.buyer = el.value;
    if(MC.applied) MC.applied.buyer = MC.buyer;
    refresh('merchants');
  }
});
document.addEventListener('input', function(e){
  var el = e.target.closest && e.target.closest('[data-act]');
  if(!el) return;
  /* 가맹점 검색어 — 타이핑만으로 걸러진다. 원본 app/manage/page.tsx:249-255 는
     onChange 단독 라이브 필터라 버튼도 Enter 도 필요 없다. 버튼은 스토리보드 S14 규정이라 남긴다. */
  if(el.dataset.act === 'mc-kw'){
    if(e.isComposing) return;
    MC.kw = el.value.trim();
    MC.page = 1;
    MC.applied = (MC.sector === '전체' && !MC.kw && MC.buyer === '전체') ? null
               : {sector:MC.sector, kw:MC.kw, buyer:MC.buyer};
    refresh('merchants');
    return;
  }
  if(el.dataset.act === 'sim-var'){ simTakeVar(el); return; }
  if(el.dataset.act === 'sim-row'){ simTakeRow(el); return; }
  if(el.dataset.act === 'pw-input'){
    /* IME(한글 등) 조합 중에는 값을 건드리지 않는다 — 조합이 끝난 뒤 compositionend 에서 최종 값을 한 번에 받는다.
       (PasswordInput.tsx:68-78 — 이벤트마다 isComposing 을 그때그때 보므로 한영전환으로 조합이
       compositionend 없이 취소돼도 입력이 멈추지 않는다.) */
    if(e.isComposing) return;
    pwTake(el);
  }
});
window.addEventListener('hashchange', function(){
  if(hashLock) return;
  var h = readHash();
  if(h) go(h.screen, h.state);
});

/* ═══ 도크 ═══ */

/* ═══ 자체 점검 — 화면 간 숫자 정합 ═══ */
window.__selfcheck = function(){
  var exec = iaExecTotal(), total = assetTotal();
  return {
    merchantSum: exec,
    assetExecRow: ASSET_ROWS[0].amount,
    execMatch: exec === ASSET_ROWS[0].amount,
    assetTotal: total,
    ratioSum: Number(ratios(MERCHANTS, exec).reduce(function(a, r){ return a + r; }, 0).toFixed(1)),
    ledgerDays: DAILY.length,
    ledgerProfitSum: sum(DAILY, 'profit'),
    monthRollupSum: sum(rollupMonths(DAILY), 'profit'),
    rollupMatchesLedger: sum(rollupMonths(DAILY), 'profit') === sum(DAILY, 'profit'),
    contracts: CONTRACTS.length,
    signQueue: SIGNQ.length,
    screens: QA('section.screen').length,
    states: Object.keys(STATE_META).reduce(function(a, k){ return a + Object.keys(STATE_META[k]).length - 1; }, 0)
  };
};

/* ═══ 초기화 ═══ */
(function init(){
  var h = readHash();
  SCREEN_ORDER.forEach(function(s){ if(RENDER[s]) RENDER[s](); });
  go(h ? h.screen : 'invest-assets', h ? h.state : null);
})();
'''

# ════════════════════════════════════════════════════════════════
# 문서 조립
# ════════════════════════════════════════════════════════════════
DOC = '''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=1440">
<title>PayHug Admin — 통합 프로토타입</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="icon" href="data:,">
<link rel="stylesheet" href="assets/base.css">
<link rel="stylesheet" href="assets/sheet.css">
<style>
%s
</style>
</head>
<!--
  통합 프로토타입 — 한 파일에서 화면 @@SCREENS@@ · 상태 @@STATES@@ 전부를 조작한다.
  개별 HTML 34개는 Figma 임포트용 정적 원본으로 별도 보존한다(이 파일이 대체하지 않는다).
  화면은 데이터 모델에서만 그린다. 표·합계·비중은 조작 결과로 계산되며 하드코딩하지 않는다.
  딥링크: #<화면>/<상태>  예) #invest-assets/page2 · #acquisition-list/signing
-->
<body data-active="invest-assets" data-view="invest-assets">
<div class="page">

  <!-- ═══════════ 사이드바 (개별 화면 32개와 동일 마크업) ═══════════ -->
  %s

  <!-- ═══════════ 콘텐츠 영역 ═══════════ -->
  <main class="content">
%s
  </main>

</div>

<!-- ═══════════ 사이드바 없는 독립 화면 ═══════════ -->
%s

<!-- ═══════════ 모달 ═══════════ -->
%s

<!-- ═══════════ 토스트 ═══════════ -->
%s

<script>
%s
</script>
</body>
</html>
''' % (CSS.strip('\n'), SIDEBAR, SCREENS_HTML.strip('\n'), STANDALONE_HTML.strip('\n'),
       MODALS_HTML.strip('\n'), CHROME_HTML.strip('\n'), JS.strip('\n'))

# 로스터·현황·일별 원장은 전부 채권 원장(daily_ledger.py)에서 나온다.
# 화면 코드에 금액·W금융일수·S입금부족율을 손으로 적는 자리를 두지 않는다.
_MER = ',\n'.join(
    "  {mid:'%s', name:'%s', biz:'%s', ceo:'%s', sector:'%s', item:'%s', tier:'%s', "
    "buyer:'A-001', buyerName:'\u321c\ud398\uc774\ud5c8\uadf8', amount:%d, w:%s, s:%s, ty:%s}"
    % (x['mid'], x['name'], x['biz'], x['ceo'], x['sector'], x['item'], x['tierName'],
       x['amount'], x['w'], x['s'], x['ty'])
    for x in RM._M)
_AST = ',\n'.join([
    "  {name:'\ud22c\uc790\uc2e4\ud589\uc561', amount:%d, w:%s, s:%s, ty:%s, "
    "keeper:'\u321c\ud398\uc774\ud5c8\uadf8'}"
    % (RM.EXEC, RM.r1(RM.W_W), RM.r2(RM.S_W), RM.TY_W),
    "  {name:'\uc21c\ud604\uae08',     amount:%d,  w:null,  s:null, ty:null, "
    "keeper:'\u321c\ucfe0\ucf58'}" % RM.CASH])
_CON = ',\n'.join("  {mid:'%s', name:'%s', signed:'%s'}" % (x[4], x[0], x[9]) for x in RM.ROSTER)
for _k, _v in (('@@MERCHANTS@@', _MER), ('@@ASSETROWS@@', _AST), ('@@CONTRACTS@@', _CON),
               ('@@LEDGER@@', daily_ledger.js_array()),
               ('@@SCREENS@@', str(counts.C['screens'])),
               ('@@STATES@@', str(counts.C['states']))):
    assert DOC.count(_k) == 1, _k
    DOC = DOC.replace(_k, _v)

# 엑셀 파일 메타(크기·생성일시)는 assets/xlsx/ 실물에서 산출한다 — 화면에 고정값을 두지 않는다.
import datetime as _dt

def _xmeta(m):
    kind, fname = m.group(1), m.group(2)
    st = os.stat(os.path.join(ROOT, 'assets', 'xlsx', fname))
    if kind == 'SZ':
        return '%.1f KB' % (st.st_size / 1024.0)
    return _dt.datetime.fromtimestamp(st.st_mtime).strftime('%Y-%m-%d %H:%M')

DOC = re.sub(r'@@(SZ|MT):([^@]+)@@', _xmeta, DOC)
assert '@@' not in DOC

open(OUT, 'w', encoding='utf-8').write(DOC)
print('app.html %d bytes / %d lines' % (len(DOC.encode('utf-8')), DOC.count('\n') + 1))
print('screens in doc:', DOC.count('data-screen="') - 1)
