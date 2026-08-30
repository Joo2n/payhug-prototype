# -*- coding: utf-8 -*-
"""app.html -> demo/index.html  (시연 전용 단일 진입점)

바깥 문서(용어·문의서·구현가능성·아카이브·순차확인)로 나가는 통로를 전부 끊고,
자산은 복제하지 않고 상위 경로(../assets/)를 참조한다.
"""
import io, os, re, sys

REPO = '/Users/semi/cursor/payhug-investor-admin'
SRC  = os.path.join(REPO, 'app.html')
DST  = os.path.join(REPO, 'demo', 'index.html')

s = io.open(SRC, encoding='utf-8').read()
orig_len = len(s)
log = []

def cut(block, why, expect=1):
    """정확히 expect번 나오는 블록을 지운다."""
    global s
    n = s.count(block)
    assert n == expect, 'cut miss (%d != %d): %s | %r' % (n, expect, why, block[:70])
    s = s.replace(block, '')
    log.append(('cut', why, n))

def sub(a, b, why, expect=1):
    global s
    n = s.count(a)
    assert n == expect, 'sub miss (%d != %d): %s | %r' % (n, expect, why, a[:70])
    s = s.replace(a, b)
    log.append(('sub', why, n))

# ── 1) 자산 참조: 복사 없이 상위 경로로 ───────────────────────────────
#     따옴표 바로 뒤의 assets/ 만 잡는다 ('invest-assets/page2' 같은 문자열은 건드리지 않는다)
s, n_asset = re.subn(r'(?<=["\'])assets/', '../assets/', s)
log.append(('sub', 'assets/ -> ../assets/', n_asset))

# ── 2) 랜딩 갤러리 화면 제거 (뷰·렌더러·CSS·레지스터) ─────────────────
ix_start = s.index('<section class="screen" data-screen="index"')
ix_end   = s.index('</section>', ix_start) + len('</section>\n\n')
cut(s[ix_start:ix_end], 'index 갤러리 <section> 제거')

gal_start = s.index('/* ───────── 랜딩 갤러리 ───────── */')
gal_end   = s.index("RENDER['login']", gal_start)
cut(s[gal_start:gal_end], 'GALLERY 배열 + RENDER[index] 제거')

css_start = s.index('  /* ── 랜딩 갤러리 ─')
css_end   = s.index('  /* ── 통합본 전용 크롬', css_start)
cut(s[css_start:css_end], '랜딩 갤러리 전용 CSS 제거')

sub("'coocon':'kcoon', 'password':'password', 'index':'', 'login':''",
    "'coocon':'kcoon', 'password':'password', 'login':''", "MENU_OF 에서 index 제거")
sub("var STANDALONE = ['index', 'login'];",
    "var STANDALONE = ['login'];", "STANDALONE 에서 index 제거")
sub("  'index':{'default':null}, 'login':{'default':null}",
    "  'login':{'default':null}", "STATE_META 에서 index 제거")
sub("  'index':'랜딩 갤러리', 'login':'로그인',",
    "  'login':'로그인',", "SCREEN_LABEL 에서 index 제거")
sub("var SCREEN_ORDER = ['index','login',",
    "var SCREEN_ORDER = ['login',", "SCREEN_ORDER 에서 index 제거")
sub("  'index.html':'index', 'login.html':'login',",
    "  'login.html':'login',", "FILE2SCREEN 에서 index 제거")
sub("  if(t.closest('.sidebar-logo a')){ e.preventDefault(); go('index'); return; }\n",
    "", "사이드바 로고 -> 랜딩 이동 핸들러 제거")

# ── 3) 내부 이동을 전부 해시 딥링크로 — 형제 .html 파일을 부르지 않는다 ─
sub('''    <div class="sidebar-logo">
      <a href="#">''',
    '''    <div class="sidebar-logo">
      <a href="#invest-assets" data-nav="invest-assets">''',
    '사이드바 로고 -> 홈(투자 자산)')

NAV = [('invest-assets', 'invest-assets.html', 'invest-assets'),
       ('invest-returns', 'invest-profit.html', 'invest-profit'),
       ('merchants',     'merchants.html',     'merchants'),
       ('receivables',   'acquisition.html',   'acquisition-list'),
       ('contracts',     'contracts.html',     'contracts'),
       ('kcoon',         'coocon.html',        'coocon'),
       ('password',      'password.html',      'password')]
for menu, href, screen in NAV:
    sub('<a class="nav-item" data-menu="%s" href="%s">' % (menu, href),
        '<a class="nav-item" data-menu="%s" data-nav="%s" href="#%s">' % (menu, screen, screen),
        '사이드바 메뉴 %s' % menu)

sub('<a class="back-link" href="invest-assets.html" data-nav="invest-assets">',
    '<a class="back-link" href="#invest-assets" data-nav="invest-assets">',
    '뒤로가기 -> 투자 자산', expect=3)
sub('<a class="back-link" href="invest-profit.html" data-nav="invest-profit">',
    '<a class="back-link" href="#invest-profit" data-nav="invest-profit">',
    '뒤로가기 -> 투자 수익', expect=2)
sub('<a class="btn btn-primary login-submit" href="invest-assets.html">',
    '<a class="btn btn-primary login-submit" href="#invest-assets" data-nav="invest-assets">',
    '로그인 버튼')
sub('href="contracts.html" data-nav="contracts"',
    'href="#contracts" data-nav="contracts"',
    '서명 완료 모달 -> 계약기록')

# ── 4) 머리말 ────────────────────────────────────────────────────────
sub('''<!--
  통합 프로토타입 — 화면 14 · 상태 18을 한 파일에서 조작한다.
  개별 HTML 34개는 Figma 임포트용 정적 원본으로 별도 보존한다(이 파일이 대체하지 않는다).
  화면은 데이터 모델에서만 그린다. 표·합계·비중은 조작 결과로 계산되며 하드코딩하지 않는다.
  딥링크: #<화면>/<상태>  예) #invest-assets/page2 · #acquisition-list/signing
-->''',
    '''<!--
  시연 전용 배포본 — 통합 프로토타입 한 파일만 연다. 화면 13 · 상태 18.
  자산(css·xlsx·pdf·zip)은 복제하지 않고 저장소 루트의 ../assets/ 를 참조한다.
  바깥 문서로 나가는 통로 없음. 외부 링크는 쿠콘 We-bank 1건뿐이며 이는 화면 기능이다.
  화면은 데이터 모델에서만 그린다. 표·합계·비중은 조작 결과로 계산되며 하드코딩하지 않는다.
  딥링크: #<화면>/<상태>  예) #invest-assets/page2 · #acquisition-list/signing
-->''',
    '머리말 교체')

s = re.sub(r'\n{3,}', '\n\n', s)

if not os.path.isdir(os.path.dirname(DST)):
    os.makedirs(os.path.dirname(DST))
io.open(DST, 'w', encoding='utf-8').write(s)

for kind, why, n in log:
    print('%-4s %-44s x%d' % (kind, why, n))
print('--- %d bytes -> %d bytes' % (orig_len, len(s)))

# ── 잔존 검사 ────────────────────────────────────────────────────────
BAD = ['glossary', 'capability', 'feasibility', 'inquiry', 'archive', 'review',
       'index.html', "'index'", '"index"', '랜딩', '갤러리', '용어 정리', '문의서', '구현 가능']
fail = 0
for b in BAD:
    hits = [(i + 1, ln.strip()[:110]) for i, ln in enumerate(s.split('\n')) if b in ln]
    print('%-14s %d' % (b, len(hits)))
    for h in hits:
        print('    L%d  %s' % h); fail += 1

sib = re.findall(r'href="(?!#|https?:|data:|\.\./)([^"]+)"', s)
print('형제 파일 상대링크 %d건: %s' % (len(sib), sib[:10]))
fail += len(sib)
sys.exit(1 if fail else 0)
