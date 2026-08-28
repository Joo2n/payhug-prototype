# -*- coding: utf-8 -*-
"""2026-08-28 미팅 결론 16항목 기계 검사. 근거는 meeting_20260828.md · request_register.md."""
import os, re, sys, json

R = '/Users/semi/cursor/payhug-investor-admin'
def rd(n):
    p = os.path.join(R, n)
    return open(p, encoding='utf-8').read() if os.path.exists(p) else ''

APP  = rd('app.html')
IDX  = rd('index.html')
GLO  = rd('glossary.html')
MER  = rd('merchants.html') + rd('merchants--filtered.html') + rd('merchants--empty.html')
COO  = rd('coocon.html') + rd('coocon--confirm.html')
CON  = rd('contracts.html') + rd('contracts--all.html') + rd('contracts--downloaded.html') + rd('contracts--empty.html')
ACQ  = (rd('acquisition.html') + rd('acquisition--confirm.html')
        + rd('acquisition--signing.html') + rd('acquisition--done.html'))
# 검사 범위 = 배포에 실려 나가는 루트 HTML 전량.
# 명단을 손으로 들고 있으면 명단에 없는 낱장이 구멍이 된다 — glossary-legacy 가 그렇게 새어
# 92건의 파일명 노출과 폐기값 32.35% 를 이고 배포되고 있었다. 그래서 디렉터리를 훑는다.
# archive.html 은 파일 추적이 본질이라 파일명 노출 예외(D-20).
ROOT = sorted(f for f in os.listdir(R) if f.endswith('.html'))
DOCS = {n: rd(n) for n in ROOT if n != 'archive.html'}

def txt(h):
    """태그를 걷어낸 화면 노출 텍스트만."""
    h = re.sub(r'<(script|style)\b.*?</\1>', ' ', h, flags=re.S|re.I)
    h = re.sub(r'<[^>]+>', ' ', h)
    return re.sub(r'\s+', ' ', h)

T = {k: txt(v) for k, v in
     dict(APP=APP, IDX=IDX, GLO=GLO, MER=MER, COO=COO, CON=CON, ACQ=ACQ).items()}

C = []   # (번호, 항목, 판정, 실측)
def chk(no, name, ok, detail):
    C.append((no, name, 'PASS' if ok else 'FAIL', detail))

# ── 화면 (D-11~D-14) ────────────────────────────────────────────
n = T['ACQ'].count('계약서보기') + T['APP'].count('계약서보기')
chk(1, '정산채권 양수 — 계약서보기 액션', n > 0, f'{n}건')

n = T['CON'].count('전자서명') + T['APP'].count('전자서명')
chk(2, '계약기록 — 다운로드 결과물이 전자서명', n > 0, f'전자서명 {n}건')

n = (T['CON'] + T['APP']).count('하나인증서')
chk(3, '계약기록 — 하나인증서 전자서명 노출', n > 0, f'{n}건')

bad = [w for w in ('정렬 필터', '정렬필터') if w in T['MER'] or w in T['APP']]
chk(4, '가맹점 — 정렬 필터 삭제', not bad, '잔재 ' + (','.join(bad) or '없음'))

bad = re.findall(r'\d+\s*개씩|페이지당|보기 갯수|보기 개수', T['MER'] + T['APP'])
chk(5, '가맹점 — 표 보기 갯수 삭제', not bad, '잔재 ' + (','.join(set(bad)) or '없음'))

bad = re.findall(r'표시\s*\d+\s*[-–]\s*\d+', T['MER'] + T['APP'])
chk(6, '가맹점 — 표시 N-N 삭제', not bad, '잔재 ' + (','.join(set(bad)) or '없음'))

hasno = bool(re.search(r'<th[^>]*>\s*No\s*</th>', MER + APP, re.I))
chk(7, '가맹점 — No 열 신설', hasno, 'th No ' + ('있음' if hasno else '없음'))

bad = [w for w in ('전자금융서비스에서 조회', '기관코드', 'OTP', '조회 가능한 내역',
                   '펌뱅킹 제휴거래내역조회') if w in T['COO']]
chk(8, '쿠콘 — 설명 전량 삭제', not bad, '잔재 ' + (','.join(bad) or '없음'))

direct = ('webank' in APP.lower() or 'we-bank' in APP.lower())
modal  = '이동 확인' in T['APP'] or 'coocon--confirm' in APP
chk(9, '쿠콘 — 메뉴에서 바로 이동(확인 모달 경유 안 함)', direct and not modal,
    f'외부링크 {"있음" if direct else "없음"} / 확인모달 {"남음" if modal else "없음"}')

# ── 용어 해설 본문 (D-16~D-18c) ─────────────────────────────────
def gl(*ws):
    return all(w in T['GLO'] for w in ws)
chk(10, '할인율 — 내부 (채권매입)수수료율 / 외부 할인율',
    gl('수수료율') and '할인율' in T['GLO'], '')
chk(11, 'ID — 카드 신설 없이 설명 한 줄',
    GLO.count('<article class="term"') == 50 and '식별값' in T['GLO'],
    f'카드 {GLO.count(chr(60)+"article class=" + chr(34) + "term" + chr(34))}건')
chk(12, '정산금채권 — 플랫폼이 정산예정일에 주기로 한 돈',
    gl('플랫폼', '정산예정일'), '')
chk(13, '정산금채권 단위 — 일자 · 가맹점 · 플랫폼', '단위' in T['GLO'], '')
chk(14, '대상정산금채권 — 가맹점당 투자자 1명 / 투자자 1:N',
    bool(re.search(r'1\s*:\s*N', T['GLO'])) and '가맹점 다수' in T['GLO'], '')
chk(15, '순현금 — 쿠콘 명의 케이뱅크 계좌', '케이뱅크' in T['GLO'], '')

# ── 문서 형식 (D-19·D-20 / F-1~F-7) ────────────────────────────
bad = [w for w in ('카드 한 장', '값의 출처', '이 값은 어디서 오나') if w in T['GLO']]
chk(16, '문서 사용법 안내 삭제', not bad, '잔재 ' + (','.join(bad) or '없음'))
chk(17, '목차 제목 = 목차', '용어 50건' not in T['GLO'] and '목차' in T['GLO'], '')
chk(18, '목차 표 화면 열 삭제', '.html ›' not in T['GLO'], '')
chk(19, '값의 출처 접힘 블록 삭제', 'details class="more"' not in GLO, '')

# 파일명 노출 — archive는 예외(D-20)
# 근거 인용(`파일:라인`)과 산출물 경로 표는 G-2·G-7이 요구하는 것이라 예외
ALLOW = {'capability.html': 3, 'feasibility.html': 3}   # 근거 인용 · 산출물 경로 표
leak = {}
for nm, h in DOCS.items():
    k = len(re.findall(r'[A-Za-z][A-Za-z0-9_\-]*\.html', txt(h)))
    if k > ALLOW.get(nm, 0): leak[nm] = k
chk(20, '.html 파일명 화면 노출 0건 (근거 인용 예외)', not leak,
    ', '.join(f'{k} {v}' for k, v in leak.items()) or f'예외 {sum(ALLOW.values())}건 외 없음')

appleak = re.findall(r'[A-Za-z][A-Za-z0-9_\-]*\.html', T['APP'])
chk(21, '통합본 갤러리 슬러그·파일명 노출 0건', not appleak,
    f'{len(appleak)}건 ' + (','.join(sorted(set(appleak))[:5]) if appleak else ''))

# ── 게이트 ─────────────────────────────────────────────────────
# G-1 예외는 레지스터 「G-1 예외 — 제품 UI 원문」에 등재된 문구에만 준다.
# 종전 기준은 `appstyle <= 8` 이라 출처 없는 존댓말이 7건까지 통과했다 — 임계값을 없애고 등재분만 뺀다.
# 등재분이 화면에서 사라지면 레지스터가 낡은 것이므로 그것도 FAIL 이다.
UI_ORIG = [
    # (문구, 출처) — 출처를 `파일:라인`으로 못 대면 예외가 아니라 임의 생성이다
    ('영문, 특수문자, 숫자 조합 8자 이상',            'payhug-merchant-web/lib/passwordPolicy.ts:12-19'),
    ('비밀번호에 공백을 사용할 수 없습니다.',          'payhug-merchant-web/lib/passwordPolicy.ts:12-19'),
    # `&` 뒤는 화면에서 &amp; 로 이스케이프되기도 해 앞부분만 본다 — 원문은 `... ! @ # $ % ^ & * ( )`
    ('사용 가능한 특수문자: ! @ # $ % ^ ',            'payhug-merchant-web/lib/passwordPolicy.ts:12-19'),
    ('영문, 숫자, 특수문자를 포함한 8~16자로 입력해주세요.', 'payhug-merchant-web/lib/passwordPolicy.ts:12-19'),
    ('사용 가능한 비밀번호입니다.',                    'payhug-merchant-web/lib/passwordPolicy.ts:12-19'),
    ('비밀번호를 한번 더 입력해주세요.',               'payhug-merchant-web/lib/passwordPolicy.ts:12-19'),
    ('비밀번호가 일치합니다.',                        'payhug-merchant-web/lib/passwordPolicy.ts:12-19'),
    ('비밀번호가 일치하지 않습니다.',                  'payhug-merchant-web/lib/passwordPolicy.ts:12-19'),
    ('비밀번호가 성공적으로 변경되었습니다. 다시 로그인해주세요.',
     'payhug-merchant-web/app/my-info/change-password/page.tsx:54'),
    ('Caps Lock이 켜져 있습니다',
     'payhug-merchant-web/components/PasswordInput.tsx:107'),
    ('시작일은 종료일보다 이후일 수 없습니다.',
     'payhug-admin-web/components/DateRangeFilter.tsx:14 INVALID_RANGE_MESSAGE'),
    ('조회 결과가 없습니다.',
     'payhug-admin-web/app/sales/[bizNo]/page.tsx:929'),
    ('검색 결과가 없습니다.',
     'payhug-admin-web/app/sales/page.tsx:122'),
]

def _ui_strip(t):
    for _s, _ in UI_ORIG:
        t = t.replace(_s, ' ')
    return t


g1 = {}
for nm, h in DOCS.items():
    t = txt(h)
    if nm == 'inquiry.html':      # 대표께 복사해 보내는 편지 본문(pre.src, display:none)은 존댓말 유지
        t = txt(re.sub(r'<pre[^>]*>.*?</pre>', ' ', h, flags=re.S))
    if nm == 'feasibility.html':  # 개발팀에 던지는 질문 문항은 의문형 유지
        t = re.sub(r'[^ ]*습니까', ' ', t)
    if nm == 'capability.html':   # <code> 안은 인용이다 — 제품 UI 원문·경로·API 이름이지 우리 문장이 아니다
        t = txt(re.sub(r'<code>.*?</code>', ' ', h, flags=re.S))
    t = _ui_strip(t)              # 레지스터에 등재된 제품 UI 원문만 뺀다
    k = len(re.findall(r'(입니다|습니다)[.\s]', t)) + \
        len(re.findall(r'(요청하신|지시에 따라|말씀하신)', t))
    if k: g1[nm] = k
chk(22, f'G-1 문체 — 루트 HTML {len(DOCS)}장', not g1,
    ', '.join(f'{k} {v}' for k, v in g1.items()) or '위반 0')

# 편지 예외의 근거 — pre.src 가 화면에 안 뜬다는 것. 뜨게 되면 예외가 아니다.
_inq = rd('inquiry.html')
_hid = 'pre.src{display:none}' in _inq.replace(' ', '')
chk(27, '편지 본문 예외 근거 — pre.src 화면 비노출', _hid and _inq.count('<pre class="src"') > 0,
    f'pre.src {_inq.count(chr(60) + "pre class=" + chr(34) + "src" + chr(34))}블록 · '
    + ('display:none' if _hid else '화면에 뜬다'))

# 배포 명단 무결 — 루트 HTML 이 전부 counts 가 아는 갈래(문서·화면·상태)에 든다.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import counts as _cnt
_known = set(_cnt.DOCS) | set(_cnt.screen_files()) | set(_cnt.state_files())
_stray = [f for f in ROOT if f not in _known]
chk(28, '배포 루트 HTML 전량이 실측 명단에 든다', not _stray, '명단 밖 ' + (', '.join(_stray) or '없음'))

pw = len(re.findall(r'PW_(MSG|DONE_MSG|CAPS_MSG)', APP))   # 비밀번호 메시지는 <script> 안이라 화면 텍스트에 안 잡힌다
_app = T['APP']
_union = ''.join(DOCS.values())        # 등재 문구는 낱장에만 있는 것도 있다 — 배포 전량에서 센다
seen_orig = {}
for _s, _src in UI_ORIG:
    # 통합본은 표를 스크립트에서 그린다 — txt() 가 <script> 를 걷어내므로 원문에서도 센다
    seen_orig[_s] = _app.count(_s) + _union.count(_s)
    _app = _app.replace(_s, ' ')
appstyle = len(re.findall(r'(입니다|습니다)[.\s<]', _app))
stale = [f'{s_}(등재만 남고 화면에 0건)' for s_, n_ in seen_orig.items() if n_ == 0]
chk(26, 'G-1 문체 — 통합본 (등재된 제품 UI 원문만 예외)', appstyle == 0 and not stale,
    f'등재 외 {appstyle}건 / 예외 등재 {len(UI_ORIG)}종 실측 {sum(seen_orig.values())}건'
    + (' / 낡은 예외 ' + ', '.join(stale) if stale else '')
    + f' / 비밀번호 메시지 상수 참조 {pw}건')

emo = sum(len(re.findall(r'[\U0001F300-\U0001FAFF✅❌⭐✨]', txt(h)))
          for h in DOCS.values())
chk(23, 'G-1 이모지 0건', emo == 0, f'{emo}건')

# 정적 화면 = 서식된 값 / 통합본 = 원시 시드값(합계·행합은 런타임 계산)
# 기대값은 채권 원장이 내보낸 사실값에서 읽는다 — 검증기에 숫자를 손으로 적지 않는다.
import json as _json
FACTS = _json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        'ledger_facts.json'), encoding='utf-8'))
_c = lambda n: format(n, ',')
STATIC = {_c(FACTS['exec']):  ('invest-assets.html', '투자실행액'),
          _c(FACTS['cash']):  ('invest-assets.html', '순현금'),
          _c(FACTS['total']): ('invest-assets.html', '투자자산'),
          _c(FACTS['weekExec']): ('invest-profit.html', '일별 투자실행금 합')}
miss = [v for k, (f, v) in STATIC.items() if k not in rd(f)]
chk(24, '숫자 불변식 — 정적 화면', not miss, '누락 ' + (','.join(miss) or '없음'))
seed = [s_ for s_ in (str(FACTS['exec']), str(FACTS['cash'])) if s_ not in APP]
chk(25, '숫자 불변식 — 통합본 시드값', not seed, '누락 ' + (','.join(seed) or '없음'))

# ── 출력 ───────────────────────────────────────────────────────
w = max(len(x[1]) for x in C)
for no, name, ok, d in C:
    print(f'{no:2d}. {name:<{w}}  {ok}  {d}')
f = [x for x in C if x[2] == 'FAIL']
print(f'\n{len(C)}항목 — PASS {len(C)-len(f)} / FAIL {len(f)}')
json.dump([{'no': n, 'name': m, 'r': r, 'd': d} for n, m, r, d in C],
          open('verify_0828_result.json', 'w'), ensure_ascii=False, indent=1)
sys.exit(1 if f else 0)
