# -*- coding: utf-8 -*-
"""verify_0828.py 음성 시험 — 막았다는 구멍에 위반을 심고 실제로 FAIL 이 나는지 본다.

양성 시험(위반이 없을 때 PASS)만으로는 검사 범위를 늘렸는지 알 수 없다. 실제로
`<script>` 안 문자열·`assets/*.html`·PDF 본문·명단 밖 낱장에 위반을 심으면 종전 검증기는
전부 통과했다. 여기서 심는 16가지가 하나라도 통과하면 그 구멍은 아직 열려 있다.

    python3 verify_0828_negative.py     심고 → 판정 → 되돌린다 (저장소는 원상복구)

되돌리기는 finally 로 돈다. 중간에 죽으면 `git -C payhug-investor-admin status` 로 확인한다.
"""
import io, os, re, shutil, subprocess, sys, tempfile, json

R = '/Users/semi/cursor/payhug-investor-admin'
P = '/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin'

def run():
    subprocess.run([sys.executable, 'verify_0828.py'], cwd=P, capture_output=True)
    d = json.load(open(os.path.join(P, 'verify_0828_result.json'), encoding='utf-8'))
    return {x['no']: x['r'] for x in d}, {x['no']: x['d'] for x in d}

CASES = []

def case(name, want, apply, undo):
    CASES.append((name, want, apply, undo))

# ── 1. <script> 안 문자열 ────────────────────────────────────────
APP = os.path.join(R, 'app.html')
def inject_app(payload):
    s = io.open(APP, encoding='utf-8').read()
    i = s.index('<script>')
    j = s.index('\n', i)
    return s[:j+1] + payload + '\n' + s[j+1:]

def mk_app(name, payload, want):
    bak = {}
    def ap():
        bak['s'] = io.open(APP, encoding='utf-8').read()
        new = inject_app(payload)
        io.open(APP, 'w', encoding='utf-8').write(new)
    def un():
        io.open(APP, 'w', encoding='utf-8').write(bak['s'])
    case(name, want, ap, un)

mk_app('script 문자열 — 존댓말', "const _t = '저장이 완료되었습니다.';", [22, 26])
mk_app('script 문자열 — .html 파일명 노출',
       "const _t = '자세한 것은 zzstray.html 화면을 보라';", [20, 21])
mk_app('script 문자열 — 자기설명 리터럴', "const _t = '이 카드의 값의 출처를 적었다';", [16])
mk_app('script 템플릿 리터럴 — 자기설명 종결',
       "const _t = `<p>여기에 한자리에 모은 것이다</p>`;", [16])

# ── 2. <dd>·<div> 안 값의 출처 ─────────────────────────────────
CAP = os.path.join(R, 'capability.html')
def mk_tag(name, tag, payload, want):
    bak = {}
    def ap():
        bak['s'] = io.open(CAP, encoding='utf-8').read()
        new = bak['s'].replace('</body>', f'<{tag}>{payload}</{tag}></body>', 1)
        io.open(CAP, 'w', encoding='utf-8').write(new)
    def un():
        io.open(CAP, 'w', encoding='utf-8').write(bak['s'])
    case(name, want, ap, un)

mk_tag('<dd> 안 값의 출처', 'dd', '값의 출처 — 어디서 왔나', [16])
mk_tag('<div> 안 값의 출처', 'div', '값의 출처 — 어디서 왔나', [16])
mk_tag('<td> 안 자기설명 종결', 'td', '아래를 한자리에 모은 것이다', [16])

# ── 3. 명단 밖 낱장 ─────────────────────────────────────────────
STRAY = os.path.join(R, 'zz-stray.html')
def ap_stray():
    io.open(STRAY, 'w', encoding='utf-8').write('<!doctype html><html><body>x</body></html>')
def un_stray():
    os.path.exists(STRAY) and os.remove(STRAY)
case('명단 밖 낱장 zz-stray.html', [28], ap_stray, un_stray)

STRAY2 = os.path.join(R, 'merchants--zzstray.html')
def ap_stray2():
    io.open(STRAY2, 'w', encoding='utf-8').write('<!doctype html><html><body>x</body></html>')
def un_stray2():
    os.path.exists(STRAY2) and os.remove(STRAY2)
case('랜딩 미등재 상태 낱장 merchants--zzstray.html', [28], ap_stray2, un_stray2)

# ── 4. assets/ 안 HTML ─────────────────────────────────────────
TPL = os.path.join(R, 'assets', 'template.html')
def mk_tpl(name, payload, want):
    bak = {}
    def ap():
        bak['s'] = io.open(TPL, encoding='utf-8').read()
        new = bak['s'].replace('</body>', payload + '</body>', 1)
        io.open(TPL, 'w', encoding='utf-8').write(new)
    def un():
        io.open(TPL, 'w', encoding='utf-8').write(bak['s'])
    case(name, want, ap, un)

mk_tpl('assets HTML — 존댓말', '<p>처리에 실패했습니다.</p>', [22])
mk_tpl('assets HTML — .html 파일명 노출', '<p>zzstray.html 을 열어라</p>', [20])
mk_tpl('assets HTML — 문서 사용법 안내', '<p>아래 스니펫을 복사해 사용</p>', [16])
mk_tpl('assets HTML — 이모지', '<p>완료 ✅</p>', [23])

# ── 5. PDF 본문 ────────────────────────────────────────────────
PDFSRC = os.path.join(P, 'build_docs.py')
PDF = os.path.join(R, 'assets', 'docs', '투자자산증명서_20260827.pdf')
def mk_pdf(name, payload, want):
    bak = {}
    def ap():
        bak['py'] = io.open(PDFSRC, encoding='utf-8').read()
        bak['pdf'] = open(PDF, 'rb').read()
        new = bak['py'].replace('<h2>서명 및 검증</h2>',
                                '<p>' + payload + '</p><h2>서명 및 검증</h2>', 1)
        io.open(PDFSRC, 'w', encoding='utf-8').write(new)
        subprocess.run([sys.executable, 'build_docs.py'], cwd=P, capture_output=True)
    def un():
        io.open(PDFSRC, 'w', encoding='utf-8').write(bak['py'])
        open(PDF, 'wb').write(bak['pdf'])
    case(name, want, ap, un)

mk_pdf('PDF 본문 — 파일명 노출', '자세한 것은 glossary.html 참조.', [29])
mk_pdf('PDF 본문 — 예시값 고지', 'W금융일수는 예시값이다.', [29])
mk_pdf('PDF 본문 — 존댓말', '본 문서는 견본입니다.', [29])

# ── 실행 ────────────────────────────────────────────────────────
base, _ = run()
print('기준선 FAIL:', [n for n, r in base.items() if r == 'FAIL'] or '없음')
ok = True
for name, want, ap, un in CASES:
    try:
        ap()
        got, det = run()
        fail = sorted(n for n, r in got.items() if r == 'FAIL')
    finally:
        un()
    caught = [n for n in want if n in fail]
    mark = 'OK  ' if len(caught) == len(want) else 'MISS'
    if mark == 'MISS':
        ok = False
    print(f'{mark}  {name:<38} 기대 {want} · 실측 FAIL {fail}')
after, _ = run()
print('복원 후 FAIL:', [n for n, r in after.items() if r == 'FAIL'] or '없음')
sys.exit(0 if ok else 1)
