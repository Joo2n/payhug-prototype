#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""배포된 3주소를 익명으로 받아 표식을 센다. 200 만 보고 완료라고 하지 않는다.

배경 — 사용자가 "쿠콘 화면이 구버전으로 뜬다"고 잡아냈다. 원본은 D-14 로 이미 아이콘+버튼만
남았는데 배포본이 옛 설명 문단을 그대로 서비스하고 있었다. 로컬 게이트는 로컬 파일을 보므로
이 구멍을 못 잡는다. 그래서 실제 URL 에서 받은 바이트로만 판정한다.

  시연(prototype) · 전체(demo)  — 있어야: 주별 계약서보기 하나인증서 12주 W금융일수(원장 사실값)
                                  없어야: 예시값 / 표시 1- / 확인필요 / 용어 안내
  용어(glossary)                — 있어야: w금융일수 케이뱅크
                                  없어야: 카드 한 장 / 값의 출처 / 용어 50건 / 관리자 어드민

전체본 루트는 화면 갤러리 랜딩이라 지표값(하나인증서·12주·W금융일수)이 랜딩에 없다.
랜딩에 값을 심는 것은 근거 없는 생성(D-8)이므로 전체본은 콘텐츠 화면에서 센다.

무엇을 세는가 — 화면 문구만 센다(오탐 교정)
  받은 바이트를 그대로 세면 소스 주석 안의 낱말이 화면 문구로 오판된다. 실제로 배포본
  app.html 의 JS 주석 한 줄 때문에 `예시값` 이 1건으로 잡혀 FAIL 이 났다. D-22 가 지운
  것은 "`예시값`·`미확정`·`확정값이 아니다` 류 **화면 고지**"(request_register.md:152)이지
  코드 주석이 아니다. 주석 낱말은 화면에 안 뜨므로 D-22 대상이 아니다.

  그래서 세기 전에 이 순서로 걷어낸다 — HTML 주석 <!-- --> · <style> 블록 · <script> 안의
  JS 주석(// , /* */) · HTML 태그. 태그는 통째로 버리지 않고 alt·title·aria-label·placeholder
  값은 살린다(보조기술에 읽히는 화면 문구다). JS 문자열·템플릿 리터럴·정규식 리터럴은
  건드리지 않는다 — 화면은 JS 가 그리므로 그 안의 문구가 곧 화면 문구다.
  검사 범위를 좁히는 것이 아니라 주석만 뺀다. 금칙어가 JS 문자열에 있으면 그대로 걸린다.

  주석은 따로 센다(§주석) — 화면 문구 판정과 섞지 않는다. D-22 는 화면 고지만 지웠으므로
  주석 잔존은 FAIL 로 세지 않고 건수만 남긴다.
"""
import html as _html
import io, json, os, re, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
# 숫자 기대값은 검증기에 손으로 적지 않는다 — daily_ledger.py 가 내는 원장 사실값을 읽는다.
FACTS = json.load(io.open(os.path.join(HERE, 'ledger_facts.json'), encoding='utf-8'))
W_DAYS = FACTS['weekW']        # W금융일수 계열 — 기본 조회기간(일주일) 합계 행

DEMO  = 'https://payhug-investor-demo.vercel.app'
PROTO = 'https://payhug-investor-prototype.vercel.app'
GLOSS = 'https://payhug-investor-glossary.vercel.app'

NEED_APP = ['주별', '계약서보기', '하나인증서', '12주', W_DAYS]
BAN_APP  = ['예시값', '표시 1-', '확인필요', '용어 안내']
NEED_GL  = ['w금융일수', '케이뱅크']
BAN_GL   = ['카드 한 장', '값의 출처', '용어 50건', '관리자 어드민']
# D-14 로 쿠콘 화면에서 사라져야 하는 옛 설명 — 배포본에 한 건이라도 남으면 구버전이다
COOCON_OLD = ['쿠콘 We-bank 전자금융서비스', 'We-bank에서 조회 가능한 내역', '전자금융서비스']

TARGETS = [
    # (이름, URL, 있어야, 없어야)  — 전체본은 루트(갤러리) + 콘텐츠 화면을 합쳐서 센다
    ('시연 루트',        PROTO + '/',                           NEED_APP, BAN_APP),
    ('전체 루트(갤러리)', DEMO + '/',                            [],       BAN_APP),
    ('전체 통합본',      DEMO + '/app.html',                     NEED_APP, BAN_APP),
    ('전체 계약기록',    DEMO + '/contracts.html',               ['하나인증서'], BAN_APP),
    ('전체 주별',        DEMO + '/invest-profit--weekly.html',   ['주별', '12주'], BAN_APP),
    ('용어 루트',        GLOSS + '/',                            NEED_GL,  BAN_GL),
]

# ── 화면 문구만 남기는 걷어내기 ────────────────────────────────────
_SCRIPT = re.compile(r'<script\b[^>]*>(.*?)</script\s*>', re.I | re.S)
_STYLE  = re.compile(r'<style\b[^>]*>.*?</style\s*>',     re.I | re.S)
_HTMLC  = re.compile(r'<!--.*?-->', re.S)
_TAG    = re.compile(r'<[^<>]*>', re.S)
# 태그를 버릴 때도 살려야 하는 문구 담는 속성 — 보조기술이 읽는다
_ATTR   = re.compile(r'\b(?:alt|title|aria-label|placeholder|aria-description)\s*=\s*'
                     r'("([^"]*)"|\'([^\']*)\')', re.I)
# 정규식 리터럴이 올 수 있는 자리의 직전 문자 — 나눗셈 기호와 가르는 통상 규칙
_RE_PREV = set('(,=:[!&|?{};+-*%~^<>')


def _walk_js(js, keep_comments):
    """JS 를 훑어 주석만 버리거나(keep_comments=False) 주석만 모은다(True).

    문자열·템플릿 리터럴·정규식 리터럴은 주석으로 오인하지 않는다.
    `https://` 의 `//` 를 줄 주석으로 잘라 먹지 않게 하려는 것이다.
    """
    out, cmts, i, n, prev = [], [], 0, len(js), ''
    while i < n:
        c = js[i]
        if c in '"\'`':                                  # 문자열·템플릿 리터럴 — 화면 문구다
            q = c
            out.append(c); i += 1
            while i < n:
                if js[i] == '\\':
                    out.append(js[i:i + 2]); i += 2; continue
                out.append(js[i])
                if js[i] == q:
                    i += 1; break
                i += 1
            prev = q
            continue
        if c == '/' and i + 1 < n:
            if js[i + 1] == '/':                         # 줄 주석
                j = js.find('\n', i)
                j = n if j < 0 else j
                cmts.append(js[i:j]); i = j; continue
            if js[i + 1] == '*':                         # 블록 주석
                j = js.find('*/', i + 2)
                j = n if j < 0 else j + 2
                cmts.append(js[i:j]); i = j; continue
            if prev in _RE_PREV or prev == '':            # 정규식 리터럴
                out.append(c); i += 1
                while i < n:
                    if js[i] == '\\':
                        out.append(js[i:i + 2]); i += 2; continue
                    out.append(js[i])
                    if js[i] == '/':
                        i += 1; break
                    if js[i] == '\n':
                        break
                    i += 1
                prev = '/'
                continue
        out.append(c)
        if not c.isspace():
            prev = c
        i += 1
    return '\n'.join(cmts) if keep_comments else ''.join(out)


def screen_text(raw_html):
    """화면에 실제로 뜨는 문구만 남긴다 — 주석·스타일·태그를 걷는다."""
    s = _HTMLC.sub(' ', raw_html)
    s = _STYLE.sub(' ', s)
    s = _SCRIPT.sub(lambda m: ' ' + _walk_js(m.group(1), False) + ' ', s)
    # 태그는 버리되 문구를 담은 속성값은 남긴다
    s = _TAG.sub(lambda m: ' ' + ' '.join(g[1] or g[2] for g in _ATTR.findall(m.group(0))) + ' ', s)
    return _html.unescape(s)


def comment_text(raw_html):
    """주석 본문만 모은다 — 화면 밖이라 D-22 판정에 넣지 않는다."""
    got = list(_HTMLC.findall(raw_html))
    got += [m.group(0) for m in re.finditer(r'/\*.*?\*/', ' '.join(_STYLE.findall(raw_html)) or '', re.S)]
    for js in _SCRIPT.findall(raw_html):
        got.append(_walk_js(js, True))
    return '\n'.join(got)


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'payhug-deploy-check'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, r.read()


fail, notes, rows = 0, 0, []
for name, url, need, ban in TARGETS:
    try:
        code, raw = get(url)
    except Exception as e:                     # noqa: BLE001
        print(f'FAIL {name} {url} <- {e}')
        fail += 1
        rows.append({'name': name, 'url': url, 'code': None, 'bytes': 0})
        continue
    s = raw.decode('utf-8', 'replace')
    scr = screen_text(s)                       # 화면 문구
    cmt = comment_text(s)                      # 주석(화면 밖)
    miss = [m for m in need if scr.count(m) == 0]
    hit  = [m for m in ban if scr.count(m) > 0]
    bad  = []
    if code != 200:
        bad.append(f'코드 {code}')
    if miss:
        bad.append('없다: ' + ', '.join(miss))
    if hit:
        bad.append('남았다: ' + ', '.join(f'{m}x{scr.count(m)}' for m in hit))
    if bad:
        fail += 1
    print(('FAIL ' if bad else 'PASS ') + f'{name:<16} {code} {len(raw):>7}B  ' +
          ' · '.join(f'{m}={scr.count(m)}' for m in (need or ban)) +
          ('  <- ' + ' / '.join(bad) if bad else ''))
    rows.append({'name': name, 'url': url, 'code': code, 'bytes': len(raw),
                 'need': {m: scr.count(m) for m in need}, 'ban': {m: scr.count(m) for m in ban},
                 'rawBan': {m: s.count(m) for m in ban},
                 'commentBan': {m: cmt.count(m) for m in ban}})

# 쿠콘 구버전 잔재 — 시연·전체 양쪽. 옛 설명이 화면에 뜨는지를 본다(주석은 제외).
for name, url in [('시연 쿠콘', PROTO + '/'), ('전체 쿠콘', DEMO + '/coocon.html')]:
    code, raw = get(url)
    s = raw.decode('utf-8', 'replace')
    scr = screen_text(s)
    left = [m for m in COOCON_OLD if m in scr]
    btn = scr.count('We-bank 바로가기')
    ok = not left and btn >= 1
    if not ok:
        fail += 1
    print(('PASS ' if ok else 'FAIL ') + f'{name:<16} {code} 옛 설명 {len(left)}건 · 바로가기 버튼 {btn}개' +
          ('  <- ' + ', '.join(left) if left else ''))
    rows.append({'name': name, 'url': url, 'code': code, 'coocon_old': left, 'btn': btn})

# ── 주석(화면 밖) — 화면 문구 판정과 섞지 않는다 ──────────────────────
# D-22 가 지운 것은 화면 고지다. 주석에 남은 낱말은 화면에 안 뜨므로 FAIL 로 세지 않는다.
# 다만 0 이 아니면 찍어 둔다 — 화면 고지를 주석으로 옮겨 검사를 피하는 일을 눈에 보이게 한다.
print('-- 주석(화면 밖) · D-22 판정 제외 --')
for r in rows:
    cb = r.get('commentBan') or {}
    left = {m: c for m, c in cb.items() if c}
    if left:
        notes += sum(left.values())
        print(f'NOTE {r["name"]:<16} 주석에 ' + ', '.join(f'{m}x{c}' for m, c in left.items()))
if not notes:
    print('NOTE 주석 잔존 0건')

json.dump({'rows': rows, 'fail': fail, 'commentNotes': notes},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'verify_deployed_result.json'), 'w'),
          ensure_ascii=False, indent=1)
print(f'== 배포 실측 {len(rows)}건 · FAIL {fail} · 주석 참고 {notes}건 ==')
sys.exit(1 if fail else 0)
