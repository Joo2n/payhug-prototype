#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""대표 정의 원문 인용 무결성 — 아래첨자·낱말 교체가 인용 자리를 건드렸는지 본다.

  A  ceo_definitions.md 무결 (읽기 전용 파일이 바뀌지 않았는가)
  B  인용 자리에 담긴 문자열이 전부 원문의 부분문자열인가
       원고 코드펜스(라벨이 「원문」) · 기호 사전 md 의 「대표 정의서 원문」 칸
       symbol_glossary.json 의 ceo_source · 배포 glossary.html 의 「원문:」 블록
  C  원문 43항이 산출물 어딘가에 그대로 남아 있는가 (인용이 소리 없이 사라지지 않았는가)
  D  아래첨자 규약이 지켜졌는가
       마크다운 원고·기호 사전 = A_i · A_{D-1,i} · SA_{D-1}
       배포 HTML          = A<sub>i</sub> · A<sub>D−1,&thinsp;i</sub>
       괄호 표기 A(D-1)i 는 0건
  E  「만기」·차용 표준용어(Duration·가중평균만기) 잔존 0건인가
       조어 근거에서 「만기」로 지목한 자리만 예외
  F  원문 인용 블록이 조판에서 갈라져 있고 그 안에 아래첨자가 없는가

돌리기 :  python3 verify_ceo_quotes.py
"""
import hashlib
import html as H
import io
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
REPO = '/Users/semi/cursor/payhug-investor-admin'
R = []


def chk(sec, name, ok, detail=''):
    R.append(dict(sec=sec, name=name, **{'pass': bool(ok)}, detail=str(detail)))


def rd(p):
    return io.open(p, encoding='utf-8').read()


def norm(t):
    return re.sub(r'\s+', ' ', t).strip()


def tight(t):
    """공백을 전부 걷는다. 원문의 겹공백('투자실행금( SAD-1)')을 인용이 정리해 옮긴 자리가 있어
       공백까지 맞추면 실제 낱말이 바뀌지 않았는데도 어긋난 것으로 잡힌다."""
    return re.sub(r'\s+', '', t)


CEO = rd(os.path.join(BASE, 'ceo_definitions.md'))
CEON = norm(CEO)
BULLETS = [norm(re.sub(r'^-\s*', '', l)) for l in CEO.split('\n') if l.strip().startswith('-')]
#  C(누락 대조)는 산식이 담긴 12자 이상 항만 센다. B(인용 무결)는 「D = 현재일자」 같은
#  짧은 항도 인용에 섞여 오므로 5자 이상 전부를 걷어 내는 데 쓴다.
ITEMS = [i for i in BULLETS if len(i) >= 12]

# ══════════════════════════════════════════════════════════════════
# A. 원문 파일 무결
# ══════════════════════════════════════════════════════════════════
sha = hashlib.sha256(CEO.encode()).hexdigest()
LOCK = os.path.join(BASE, 'ceo_definitions.sha256')
if os.path.exists(LOCK):
    want = rd(LOCK).split()[0]
    chk('A', 'ceo_definitions.md 해시 일치 (읽기 전용)', sha == want,
        '기록 %s / 지금 %s' % (want[:16], sha[:16]))
else:
    io.open(LOCK, 'w', encoding='utf-8').write(sha + '  ceo_definitions.md\n')
    chk('A', 'ceo_definitions.md 해시 기록 생성', True, sha[:16])
chk('A', '원문 항목 43건 판독', len(ITEMS) == 43, '%d건' % len(ITEMS))


# ══════════════════════════════════════════════════════════════════
# B. 인용 자리 → 원문 부분문자열
# ══════════════════════════════════════════════════════════════════
QUOTE_LAB = {'원문이 화면 수정 지시도 함께 달아 두었다.'}


def md_quote_fences(path):
    """라벨이 「원문…:」인 코드펜스 본문."""
    L = rd(path).split('\n')
    out, i = [], 0
    while i < len(L):
        if L[i].startswith('```'):
            prev = [x for x in L[max(0, i - 3):i] if x.strip()]
            lab = prev[-1] if prev else ''
            j = i + 1
            while j < len(L) and not L[j].startswith('```'):
                j += 1
            if lab.startswith('원문') and (lab.rstrip().endswith(':') or lab in QUOTE_LAB):
                out.append((path, i + 1, '\n'.join(L[i + 1:j])))
            i = j + 1
        else:
            i += 1
    return out


def md_quote_cells(path):
    """「대표 정의서 원문」 행 · 「원문 정의문」 열의 백틱 칸."""
    out = []
    for n, l in enumerate(rd(path).split('\n')):
        if not l.lstrip().startswith('|'):
            continue
        cells = [c.strip() for c in l.strip().strip('|').split('|')]
        if cells and cells[0] in ('대표 정의서 원문', '대표님 정의 원문'):
            for c in cells[1:]:
                for m in re.finditer(r'`([^`]+)`', c):
                    out.append((path, n + 1, m.group(1)))
    return out


SRC = []
SRC += md_quote_fences(os.path.join(BASE, 'glossary_manuscript.md'))
SRC += md_quote_cells(os.path.join(BASE, 'symbol_glossary.md'))
sg = json.loads(rd(os.path.join(BASE, 'symbol_glossary.json')))
for s in sg['symbols'] + sg['operators']:
    if s.get('ceo_source'):
        SRC.append(('symbol_glossary.json', s['symbol'], s['ceo_source']))

TITEMS = sorted({tight(i) for i in BULLETS if len(tight(i)) >= 5}, key=len, reverse=True)
CEOT = tight(CEO)
NOTE = re.compile(r'←\d+번이미지|…')


def uncovered(txt):
    """인용에서 원문 항을 걷어 내고 남는 글자. 남으면 원문에 없는 글자를 넣은 것이다."""
    b = tight(txt)
    for it in TITEMS:
        b = b.replace(it, '')
    b = NOTE.sub('', b)
    return b


def ok_quote(txt):
    if not uncovered(txt):              # 원문 항을 통째로 옮긴 인용
        return True
    if tight(txt) in CEOT:              # 항 중간을 잘라 온 인용
        return True
    # 「…」로 가운데를 줄인 인용 — 조각이 전부 원문에 있으면 된다
    frag = [tight(p) for p in re.split(r'…', txt) if len(tight(p)) >= 8]
    return bool(frag) and all(p in CEOT for p in frag)


bad = []
for where, ln, txt in SRC:
    if ok_quote(txt):
        continue
    bad.append((os.path.basename(str(where)), ln, uncovered(txt)[:60]))
chk('B', '인용 자리 %d곳이 전부 원문 부분문자열' % len(SRC), not bad,
    '어긋난 곳 %d %s' % (len(bad), bad[:4]))


# ══════════════════════════════════════════════════════════════════
# C. 원문 43항이 산출물에 그대로 남아 있는가
# ══════════════════════════════════════════════════════════════════
GH = rd(os.path.join(REPO, 'glossary.html'))
GHT = norm(H.unescape(re.sub(r'<[^>]+>', ' ', re.sub(r'<(script|style)\b.*?</\1>', ' ',
                                                     GH, flags=re.S | re.I))))
POOL = {
    'glossary_manuscript.md': norm(rd(os.path.join(BASE, 'glossary_manuscript.md'))),
    'symbol_glossary.md': norm(rd(os.path.join(BASE, 'symbol_glossary.md'))),
    'symbol_glossary.json': norm(rd(os.path.join(BASE, 'symbol_glossary.json'))),
    'glossary.html(배포)': GHT,
}
#   배치 절차문 1항만은 어느 산출물도 통째로 옮기지 않고 풀어 쓴다(원고 「원문이 정한 절차는
#   이렇다」 블록). 인용 자리가 아니므로 이 항은 빼고 센다.
PARAPHRASED = '매일 자정일 지나면, 배치 작업으로, 유동화투자자별로'
POOLT = {k: tight(v) for k, v in POOL.items()}
missing = [i[:60] for i in ITEMS
           if not i.startswith(PARAPHRASED)
           and not any(tight(i) in v for v in POOLT.values())]
chk('C', '원문 43항 전건이 산출물 어딘가에 그대로 남아 있음 (풀어 쓴 배치 절차문 1항 제외)',
    not missing, '못 찾은 항 %d %s' % (len(missing), missing[:3]))
for k, v in POOLT.items():
    n = sum(1 for i in ITEMS if tight(i) in v)
    chk('C', '[%s] 원문 항 인용 0건 아님' % k, n > 0, '%d항' % n)


# ══════════════════════════════════════════════════════════════════
# D. 아래첨자 규약
# ══════════════════════════════════════════════════════════════════
#  2026-08-31 기호 규칙 — 아래첨자의 전일자는 소문자 d 다(A_{d-1,i} · SA_{d-1}).
#  옛 대문자 표기(A_{D-1,i})도 같이 잡는다. 원고는 소문자로 갈아 끼웠고, 기호 사전 쪽은
#  다른 조가 손대는 중이라 두 표기가 한동안 같이 있는다. 잔존 검사는 두 표기 다 잡아야 샌 자리가 보인다.
MD_SUB = re.compile(r'(?<![A-Za-z0-9_])(?:SMR|SB|SA|SM|SD|SL|A|B|M|D)_(?:\{(?:[Dd]-1,i|[Dd]-1|p,i)\}|i)'
                    r'(?![A-Za-z0-9_])')
PAREN = re.compile(r'S?[ABMD]\([Dd]-1\)i?')
DRIFTROW = re.compile(r'^\|\s*`(?:glossary\.html|glossary_manuscript\.md)`\s*\|\s*\d+\s*\|')


#   인용 자리는 괄호 표기 검사에서 뺀다. 대표가 스스로 괄호 꼴로 적은 자리가 있어서다 —
#   DM 2026-08-31 15:37 「투자 수익 : M(D-1)i = 채권매입수수료 − max(0, 미지급금 − 과지급금)」,
#   15:15 「금융일수 D 말고 다른 용어 써야 함 → PSD, SD(d-1) 등등 나와서」.
#   이 검사가 막는 것은 「우리 표기가 괄호 꼴로 되돌아갔는가」이지 대표가 쓴 글자가 아니다.
QUOTE_FIELDS = ('ceo_source', 'meeting_source')


def no_drift(f, t):
    """표기 흔들림 기록(§5-1 · notation_canon.drift_sites)은 곱셈기호 흔들림의 실측 기록이라
       아래첨자 교체 대상이 아니다. 인용 자리와 함께 괄호 표기 검사에서 뺀다."""
    if f.endswith('.json'):
        d = json.loads(t)
        d.pop('notation_canon', None)
        for s in d.get('symbols', []) + d.get('operators', []):
            s.pop('aliases', None)              # aliases 는 이전 표기를 남겨 두는 자리다
            for q in QUOTE_FIELDS:              # 대표 원문·DM 을 글자 그대로 옮긴 자리다
                s.pop(q, None)
        return json.dumps(d, ensure_ascii=False)
    return '\n'.join(l for l in t.split('\n') if not DRIFTROW.match(l.lstrip()))


for f in ('glossary_manuscript.md', 'symbol_glossary.md', 'symbol_glossary.json',
          'restructure_glossary.py'):
    t = rd(os.path.join(BASE, f))
    chk('D', '[%s] 아래첨자 마크다운 표기 0건 아님' % f, len(MD_SUB.findall(t)) > 0,
        '%d건' % len(MD_SUB.findall(t)))
    t2 = no_drift(f, t)
    chk('D', '[%s] 괄호 표기 X(D-1)i 0건 (표기 흔들림 기록·aliases 제외)' % f, not PAREN.search(t2),
        '%d건 %s' % (len(PAREN.findall(t2)), sorted(set(PAREN.findall(t2)))[:4]))

HTML_SUB = re.compile(r'<sub>(?:[Dd]−1,&thinsp;i|[Dd]−1|p,&thinsp;i|i)</sub>')
chk('D', '배포 glossary.html 아래첨자 <sub> 0건 아님', len(HTML_SUB.findall(GH)) > 0,
    '%d건' % len(HTML_SUB.findall(GH)))
chk('D', '배포 glossary.html 에 마크다운 밑줄 표기 잔존 0건', not MD_SUB.search(GH),
    str(sorted(set(MD_SUB.findall(GH)))[:5]))
chk('D', '배포 glossary.html 괄호 표기 X(D-1)i 0건', not PAREN.search(GH),
    '%d건' % len(PAREN.findall(GH)))
chk('D', '<sub> 안 하이픈이 빼기표 U+2212',
    '<sub>D-1' not in GH and '<sub>d-1' not in GH, '평문 하이픈 잔존')

#  2026-08-31 기호 규칙 — 우리 표기의 전일자 첨자는 소문자 d 다(D 는 금융일수로 비워 뒀다).
#  옛 대문자 표기로 되돌아가면 여기서 걸린다. 기호 사전(symbol_glossary.*)은 다른 조가
#  옮기는 중이라 이 검사에 넣지 않는다 — 대상은 원고와 그 원고로 낸 배포 HTML 뿐이다.
OLD_SUB_MD = re.compile(r'(?<![A-Za-z0-9_])(?:SMR|SB|SA|SM|SD|SL|A|B|M|D)_\{D-1(?:,i)?\}')
GM = rd(os.path.join(BASE, 'glossary_manuscript.md'))
chk('D', '[glossary_manuscript.md] 옛 대문자 첨자 _{D-1} 0건',
    not OLD_SUB_MD.search(GM), '%d건 %s' % (len(OLD_SUB_MD.findall(GM)),
                                            sorted(set(OLD_SUB_MD.findall(GM)))[:4]))
chk('D', '[glossary_manuscript.md] 새 소문자 첨자 _{d-1} 0건 아님',
    GM.count('_{d-1}') + GM.count('_{d-1,i}') > 0,
    '%d건' % (GM.count('_{d-1}') + GM.count('_{d-1,i}')))
chk('D', '배포 glossary.html 옛 대문자 첨자 <sub>D−1 0건',
    '<sub>D\u2212' not in GH, '%d건' % GH.count('<sub>D\u2212'))
chk('D', '배포 glossary.html 새 소문자 첨자 <sub>d−1 0건 아님',
    GH.count('<sub>d\u2212') > 0, '%d건' % GH.count('<sub>d\u2212'))
#  표본 구간도 같은 규칙이다 — 우리 서술은 소문자, 대표 DM·원문 인용은 대문자 그대로 둔다.
chk('D', '[glossary_manuscript.md] 표본 구간 서술이 소문자 d-20 ~ d-11',
    '선정산일이 d-20 ~ d-11' in GM and 'd-20   = 2026-08-07' in GM,
    '소문자 서술 누락')
chk('D', '배포 glossary.html 표본 구간 서술이 소문자 d-20 ~ d-11',
    '선정산일이 d-20 ~ d-11' in GHT, '소문자 서술 누락')

#  파이프라인에 둔 낱장은 배포본의 거울이다(생성기는 build_glossary.py 하나뿐).
chk('D', '_pipeline/investor_admin/glossary.html = 배포본 거울',
    rd(os.path.join(BASE, 'glossary.html')) == GH, '%d B' % len(GH))

# 원문 평문 표기는 인용 자리에 그대로 살아 있어야 한다
RAW = re.compile(r'(?<![A-Za-z0-9_])(?:(?:SMR|SB|SA|SM|SD)D-1|[ABMD]D-1i)(?![A-Za-z0-9_])')
chk('D', '배포 glossary.html 에 원문 평문 표기(AD-1i·SAD-1 …) 살아 있음',
    len(RAW.findall(GHT)) > 0, '%d건' % len(RAW.findall(GHT)))


# ══════════════════════════════════════════════════════════════════
# E. 「만기」·duration — 정본 표기 자리에는 0건, 각주 한 자리에서만
# ══════════════════════════════════════════════════════════════════
#   2026-08-31 재판정. 앞 판은 이 낱말들을 전 산출물에서 0건으로 막았고 사유는 「근거 없는 조어」였다.
#   그 사유는 무효다 — 대표가 직접 썼다(DM 2026-08-31 16:41:24 · 3차 미팅 00:43:33·00:44:30).
#   정본 표기는 `w금융일수` 하나로 그대로 두고, 출처를 밝힌 각주 딱 한 자리에서만 허용한다.
#   허용 자리가 늘지 않도록 각주 전문을 글자 그대로 못 박고 곳수를 1로 고정한다.
#     · 같은 각주가 둘이면 count 가 2 → FAIL
#     · 다른 문장으로 자리를 더 만들면 각주를 걷어 낸 나머지에 낱말이 남아 → FAIL
#   각주가 놓인 자리는 원고와 그 원고로 낸 배포 HTML 둘뿐이다. 기호 사전 쪽은 여전히 0건이다.
DUR_NOTE = (
    '공식 용어는 duration, 대표 표현은 가중평균 만기일 — 대표 DM 2026-08-31 16:41:24 '
    '「w금융일수 = 공식 용어로 duration, 우리는 가중 평균 만기일(weight) 가중평균금융일수」 · '
    '3차 미팅 00:43:33 「엄밀히는 공식 영어는 듀레이션」 · 00:44:30 '
    '「가중 평균 만기해서 웨이티드의 W 를 붙인 것」. 가중평균 만기일은 매콜리 듀레이션의 정의 그대로이고, '
    '금리 민감도를 재는 수정 듀레이션과는 다르다. 정본 표기는 w금융일수 하나이고 '
    '화면·표·머리글에는 이 이름만 쓴다.')
NOTE_SITES = ('glossary_manuscript.md', 'glossary.html(배포)')
MENTION = '「만기」'
for name, t in [('glossary_manuscript.md', rd(os.path.join(BASE, 'glossary_manuscript.md'))),
                ('symbol_glossary.md', rd(os.path.join(BASE, 'symbol_glossary.md'))),
                ('symbol_glossary.json', rd(os.path.join(BASE, 'symbol_glossary.json'))),
                ('restructure_glossary.py', rd(os.path.join(BASE, 'restructure_glossary.py'))),
                ('glossary.html(배포)', GHT)]:
    if name in NOTE_SITES:
        chk('E', '[%s] duration 각주가 정확히 1자리' % name, t.count(DUR_NOTE) == 1,
            '%d자리' % t.count(DUR_NOTE))
        body = t.replace(DUR_NOTE, '', 1)       # 각주 한 자리만 걷는다
        lab = '각주 밖'
    else:
        body = t
        lab = ''
    tot = body.count('만기')
    men = body.count(MENTION)
    chk('E', '[%s] %s「만기」 = 조어 근거의 지목뿐' % (name, lab), tot == men,
        '전체 %d · 지목 %d · 그 밖 %d' % (tot, men, tot - men))
    for w in ('Duration', 'duration', '가중평균만기', '평균만기'):
        chk('E', '[%s] %s대출·표준용어 차용 %s 0건' % (name, lab, w), w not in body,
            '%d건' % body.count(w))
#   각주 안 곳수까지 못 박는다 — 각주를 부풀려 낱말을 더 넣어도 걸린다
chk('E', '배포 glossary.html 「만기」 총 곳수 = 각주 안 곳수',
    GHT.count('만기') == DUR_NOTE.count('만기'),
    '전체 %d · 각주 %d' % (GHT.count('만기'), DUR_NOTE.count('만기')))
chk('E', '배포 glossary.html duration 총 곳수 = 각주 안 곳수',
    GHT.lower().count('duration') == DUR_NOTE.lower().count('duration'),
    '전체 %d · 각주 %d' % (GHT.lower().count('duration'), DUR_NOTE.lower().count('duration')))
chk('E', '각주에 출처(DM 시각·회의 시각) 병기',
    all(s in DUR_NOTE for s in ('대표 DM 2026-08-31 16:41:24', '3차 미팅 00:43:33', '00:44:30')),
    '출처 누락')
chk('E', '정본 표기 w금융일수가 각주 밖에서 살아 있음',
    GHT.replace(DUR_NOTE, '', 1).count('w금융일수') > 0,
    '%d건' % GHT.replace(DUR_NOTE, '', 1).count('w금융일수'))
CT = sg.get('coined_terms', [])
chk('E', '조어 모집단 용어가 사전에 근거와 함께 등재됨',
    len(CT) >= 1 and all(c.get('coined') and c.get('coined_basis') and c.get('not_used')
                         for c in CT),
    str([c.get('term') for c in CT]))
FORMS = [f for c in CT for f in [c.get('term')] + list(c.get('short_forms') or [])]
chk('E', '조어가 원고·기호 사전에서 쓰이고 있음',
    all(any(f in v for v in POOL.values()) for f in FORMS), str(FORMS))


# ══════════════════════════════════════════════════════════════════
# F. 인용 블록이 조판에서 갈라져 있는가
# ══════════════════════════════════════════════════════════════════
QB = re.findall(r'<pre class="calc quote">(.*?)</pre>', GH, re.S)
NB = re.findall(r'<pre class="calc">(.*?)</pre>', GH, re.S)
chk('F', '인용 블록이 서술 블록과 다른 클래스로 나옴', len(QB) > 0 and len(NB) > 0,
    '인용 %d · 서술 %d' % (len(QB), len(NB)))
chk('F', '인용 블록 안 아래첨자 조판 0건',
    sum(b.count('<sub>') for b in QB) == 0 and not any(MD_SUB.search(b) for b in QB),
    '<sub> %d' % sum(b.count('<sub>') for b in QB))
qbad = []
for b in QB:
    for ln in H.unescape(b).split('\n'):
        s = re.sub(r'←.*$', '', ln)
        for frag in s.split('…'):
            f = tight(frag)
            if len(f) >= 8 and f not in CEOT:
                qbad.append(ln.strip()[:60])
                break
chk('F', '인용 블록 %d개의 산식 문자열이 원문과 글자 그대로 같음' % len(QB), not qbad,
    '어긋난 줄 %d %s' % (len(qbad), qbad[:3]))

# ══════════════════════════════════════════════════════════════════
fail = [r for r in R if not r['pass']]
for r in R:
    print('  %-4s %-58s %s  %s' % (r['sec'], r['name'][:58],
                                   'PASS' if r['pass'] else 'FAIL', r['detail'][:70]))
print('\n%d항목 — PASS %d / FAIL %d' % (len(R), len(R) - len(fail), len(fail)))
json.dump(dict(total=len(R), fail=len(fail), cases=R),
          io.open(os.path.join(BASE, 'verify_ceo_quotes_result.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
sys.exit(1 if fail else 0)
