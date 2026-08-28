#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""용어 원고를 5필드 카드 구조로 재조판한다.

입력  glossary_manuscript.md (구조판 이전 원고)
      symbol_glossary.json   (기호 28건 + 연산자 4건 — 표기 정본)
출력  glossary_manuscript.md (덮어쓰기 — 5필드 카드 구조)

숫자·산식·판정은 한 글자도 바꾸지 않는다. 블록을 잘라 순서와 이름만 바꾼다.
"""
import json, os, re, sys

PIPE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(PIPE, 'glossary_manuscript.md')
SYM  = os.path.join(PIPE, 'symbol_glossary.json')

BLOCKS = ['층위', '한마디로 뭐냐', '어떻게 계산하나', '이 값은 어디서 오나',
          '화면 어디에 보이나', '다른 용어와 어떻게 이어지나', '기획할 때 정해야 할 것']

# ══════════════════════════════════════════════════════════════════
#  카드별 손 지정 — 화면 표기 / 캡처 / 오버레이 앵커
#     shot   assets/shots/<key>.webp
#     anchor shot_rects.json 안 items[].text 와 맞출 문자열
#     kind   direct = 그 자리에 그 값이 뜬다 / indirect = 재료라 그 자리 뒤에 숨는다
#     label  화면 표기가 카드 이름과 다를 때만
# ══════════════════════════════════════════════════════════════════
META = {
 '정산금채권':            dict(shot='invest-assets', anchor='th:가맹점',        kind='indirect'),
 '정산금채권 ID':          dict(shot='merchants',     anchor='th:가맹점ID',      kind='indirect'),
 '플랫폼ID':              dict(shot='invest-assets', anchor='th:가맹점',        kind='indirect'),
 '매출일자':              dict(shot='invest-profit', anchor='th:정산예정일',     kind='indirect'),
 '선정산일':              dict(shot='invest-profit', anchor='th:W금융일수',      kind='indirect'),
 '정산예정일':            dict(shot='invest-profit', anchor='th:정산예정일',     kind='direct', label='정산예정일'),
 '순지급액':              dict(shot='invest-profit', anchor='th:상환액',        kind='indirect'),
 '금융일수':              dict(shot='invest-assets', anchor='th:W금융일수#0',    kind='indirect'),

 '유동화투자자':           dict(shot='merchants',     anchor='th:채권매입업체ID', kind='direct', label='채권매입업체ID'),
 '정산금채권 재양도 합의서': dict(shot='contracts',     anchor='th:재양도합의서',   kind='direct', label='재양도합의서'),
 '효력기간':              dict(shot='contracts',     anchor='th:재양도합의서',   kind='indirect'),
 '대상정산금채권':          dict(shot='invest-assets', anchor='th:가맹점',        kind='indirect'),

 '유동화투자자의 할인율':    dict(shot='invest-assets', anchor='div:0.11%',       kind='direct', label='배분 요율 0.11%'),
 'Ai':                   dict(shot='invest-assets', anchor='td:투자실행액',     kind='indirect'),
 '채권매입수수료':          dict(shot='invest-profit', anchor='th:투자 수익',     kind='indirect'),

 '회수되지 않은 순지급액':   dict(shot='invest-assets', anchor='td:투자실행액',     kind='indirect'),
 '투자 실행액':            dict(shot='invest-assets', anchor='td:투자실행액',     kind='direct', label='투자실행액'),
 '순현금 (투자 자산 · 잔액)': dict(shot='invest-assets', anchor='td:순현금',       kind='direct', label='순현금'),
 '쿠콘 가상계좌':           dict(shot='invest-assets', anchor='th:보관',          kind='direct', label='보관 ㈜쿠콘'),
 'Di':                   dict(shot='invest-assets', anchor='th:W금융일수#0',    kind='indirect'),
 'w금융일수 (투자 자산 · 잔액)': dict(shot='invest-assets', anchor='th:W금융일수#0', kind='direct', label='W금융일수'),
 'ty수익율 (투자 자산 · 잔액)': dict(shot='invest-assets', anchor='th:TY수익율#0',  kind='direct', label='TY수익율'),
 '비중':                  dict(shot='invest-assets', anchor='th:비중#0',        kind='direct'),
 '자산 구분':              dict(shot='invest-assets', anchor='th:자산 구분',      kind='direct'),
 '보관':                  dict(shot='invest-assets', anchor='th:보관',          kind='direct'),
 '투자자산':               dict(shot='invest-assets', anchor='td:합계 (투자자산)', kind='direct', label='합계 (투자자산)'),
 '가맹점별 투자금액':        dict(shot='invest-assets', anchor='th:투자금액 (원)',  kind='direct', label='투자금액 (원)'),
 '기준일자':               dict(shot='invest-assets', anchor='div:기준일 2026-08-27', kind='direct', label='기준일'),

 '미지급금':               dict(shot='invest-profit', anchor='th:상환액',        kind='indirect'),
 '과지급금':               dict(shot='invest-profit', anchor='th:상환액',        kind='indirect'),
 'SLi':                  dict(shot='invest-assets', anchor='th:S입금부족율#0',  kind='indirect'),
 'SAi':                  dict(shot='invest-assets', anchor='th:S입금부족율#0',  kind='indirect'),
 '표본집합':               dict(shot='invest-assets', anchor='h2:수익 산정 기준 (예시)', kind='indirect'),
 'S입금부족율':            dict(shot='invest-assets', anchor='th:S입금부족율#0',  kind='direct'),

 '상환액 (일별 배치 · 하루치)':   dict(shot='invest-profit', anchor='th:상환액',    kind='direct', label='상환액'),
 '투자실행금 (일별 배치 · 하루치)': dict(shot='invest-profit', anchor='th:투자실행금', kind='direct', label='투자실행금'),
 '투자수익 (일별 배치 · 하루치)':  dict(shot='invest-profit', anchor='th:투자 수익',  kind='direct', label='투자 수익'),
 '투자수익율 (일별 배치 · 하루치)': dict(shot='invest-profit', anchor='th:TY수익율',  kind='indirect'),
 'w금융일수 (일별 배치 · 하루치)': dict(shot='invest-profit', anchor='th:W금융일수', kind='direct', label='W금융일수'),
 'ty수익율 (일별 배치 · 하루치)':  dict(shot='invest-profit', anchor='th:TY수익율',  kind='direct', label='TY수익율'),
 '순현금 (일별 배치 · 자정 시점)': dict(shot='coocon',        anchor='h2:쿠콘 We-bank 전자금융서비스', kind='indirect'),

 '투자실행금 (투자 수익 · 기간 합계)': dict(shot='invest-profit', anchor='div:투자실행금#0', kind='direct', label='투자실행금 (현황 카드)'),
 '투자수익 (투자 수익 · 기간 합계)':  dict(shot='invest-profit', anchor='div:투자수익#0',  kind='direct', label='투자수익 (현황 카드)'),
 'PSMR':                        dict(shot='invest-profit', anchor='div:Ty수익율#0', kind='indirect'),
 'PSD':                         dict(shot='invest-profit', anchor='td:합계',      kind='direct', label='W금융일수 (합계 행)'),
 'PSC':                         dict(shot='invest-profit', anchor='div:투자자산 대비', kind='indirect'),
 'ty수익율 › 투자실행금액 대비 (투자 수익 · 기간 합계)':
                                dict(shot='invest-profit', anchor='div:투자실행금액 대비', kind='direct', label='Ty수익율 › 투자실행금액 대비'),
 'ty수익율 › 투자자산 대비 (투자 수익 · 기간 합계)':
                                dict(shot='invest-profit', anchor='div:투자자산 대비', kind='direct', label='Ty수익율 › 투자자산 대비'),
 'ty수익율 (일별 표 · 행 단위)':   dict(shot='invest-profit', anchor='th:TY수익율',  kind='direct', label='TY수익율'),
 '검색대상기간':                  dict(shot='invest-profit', anchor='div:검색대상기간', kind='direct'),
}


# 카드 → 대표 정의 원문 기호. 원문이 그 용어에 붙인 기호만 적는다.
# 원문이 이름만 쓰고 기호를 두지 않은 용어는 None — 지어내지 않는다.
CARD_SYM = {
 '정산금채권 ID': 'i',
 '금융일수': 'Di',
 'Ai': 'Ai',
 'Di': 'Di',
 'w금융일수 (투자 자산 · 잔액)': 'w',
 'ty수익율 (투자 자산 · 잔액)': 'Ty / ty',
 'SLi': 'SLi',
 'SAi': 'SAi',
 '상환액 (일별 배치 · 하루치)': 'SB(D-1)',
 '투자실행금 (일별 배치 · 하루치)': 'SA(D-1)',
 '투자수익 (일별 배치 · 하루치)': 'SM(D-1)',
 '투자수익율 (일별 배치 · 하루치)': 'SMR(D-1)',
 'w금융일수 (일별 배치 · 하루치)': 'SD(D-1)',
 '순현금 (일별 배치 · 자정 시점)': 'EC',
 '투자실행금 (투자 수익 · 기간 합계)': 'PSA',
 '투자수익 (투자 수익 · 기간 합계)': 'PSM',
 'PSMR': 'PSMR',
 'PSD': 'PSD',
 'PSC': 'PSC',
 'ty수익율 › 투자실행금액 대비 (투자 수익 · 기간 합계)': '③④⑤⑥',
 'ty수익율 › 투자자산 대비 (투자 수익 · 기간 합계)': '③④⑤⑥',
 'ty수익율 (일별 표 · 행 단위)': '③④⑤⑥',
}
# 원문 번호가 그 카드에서 어느 번호로 읽히는지 (marker_legend.md 대조)
CARD_CIRCLED = {
 'ty수익율 › 투자실행금액 대비 (투자 수익 · 기간 합계)': '④',
 'ty수익율 › 투자자산 대비 (투자 수익 · 기간 합계)': '⑤',
 'ty수익율 (일별 표 · 행 단위)': '⑥',
}


def sym_id(sym):
    """기호 → 앵커 id. symbol_glossary.md §8-3 권고 규칙."""
    if sym == 'Σ':
        return 'sym-sigma'
    if sym == '③④⑤⑥':
        return 'sym-circled'
    return 'sym-' + re.sub(r'[^A-Za-z0-9]', '', sym)


def split_blocks(txt):
    idx = [(m.start(), m.end(), m.group(1))
           for m in re.finditer(r'^\*\*(.+?)\*\*', txt, re.M) if m.group(1) in BLOCKS]
    out = {}
    for n, (a, b, name) in enumerate(idx):
        end = idx[n + 1][0] if n + 1 < len(idx) else len(txt)
        out[name] = txt[b:end].strip()
    return out


def parse(src):
    s = open(src, encoding='utf-8').read()
    start = s.index('# 1단계 — 채권 한 건이')
    head, body = s[:start], s[start:]

    # 서술 절 — 부록으로 옮길 것들
    def sect(pat, nxt):
        a = head.index(pat)
        b = head.index(nxt, a)
        return head[a:b].rstrip().rstrip('-').rstrip()
    narr = {
        'find':  sect('## 0. 화면에서 본 이름으로 찾기', '## 1. 전체 그림'),
        'map':   sect('## 1. 전체 그림', '## 1-1. 먼저 알아야 할'),
        'hole':  sect('## 1-1. 먼저 알아야 할', '## 2. 읽는 순서'),
        'order': sect('## 2. 읽는 순서', '## 3. 화면에서 거꾸로 찾기'),
        'rev':   sect('## 3. 화면에서 거꾸로 찾기', '## 4. 용어 카드 읽는 법'),
        'howto': head[head.index('## 4. 용어 카드 읽는 법'):].rstrip().rstrip('-').rstrip(),
    }

    stages = []
    for p in re.split(r'\n(?=# )', body):
        m = re.match(r'# (.+)', p)
        if not m:
            continue
        title = m.group(1).strip()
        first = p.find('\n## ')
        if not re.match(r'\d단계', title):
            stages.append({'stage': title, 'lede': '', 'cards': [], 'tail': p})
            continue
        lede = p[m.end():first].strip().strip('-').strip()
        cards = []
        for c in re.split(r'\n(?=## )', p[first:]):
            cm = re.match(r'## (.+)', c)
            if not cm:
                continue
            cards.append({'term': cm.group(1).strip(),
                          'blocks': split_blocks(c[cm.end():])})
        stages.append({'stage': title, 'lede': lede, 'cards': cards, 'tail': ''})
    return narr, stages


def first_sentence(t):
    t = re.sub(r'\s+', ' ', t.strip())
    m = re.match(r'(.{4,120}?[다요]\.)(\s|$)', t)
    return (m.group(1) if m else t[:80]).strip()


def split_chain(t):
    """`재료: X → 결과: Y` 를 둘로 가른다. 못 가르면 통째로 결과 쪽에 둔다."""
    t = t.strip()
    m = re.match(r'재료[:：]\s*(.*?)\s*→\s*결과[:：]\s*(.*)$', t, re.S)
    if m:
        return m.group(1).strip(), m.group(2).strip(), ''
    return '', t, ''


def main():
    narr, stages = parse(SRC)
    G = json.load(open(SYM, encoding='utf-8'))
    SYMS = {x['symbol']: x for x in G['symbols']}
    PAIRS = G.get('confusable_pairs') or []
    for k in CARD_SYM.values():
        assert k in SYMS, f'기호 사전에 없음: {k}'

    def _rel_match(term, r):
        r = r.split(' = ')[0].strip()
        r = re.sub(r'\((?:분자|분모|가중치|분자·분모)\)$', '', r).strip()
        return r == term or term.startswith(r + ' (')

    def related_syms(term):
        """그 용어를 related_terms 에 적어 둔 기호들. 자기 기호는 뺀다."""
        own = CARD_SYM.get(term)
        out = []
        for x in G['symbols']:
            if x['symbol'] == own:
                continue
            if any(_rel_match(term, r) for r in x.get('related_terms') or []):
                out.append(x['symbol'])
        return out

    def pair_note(sym):
        if not sym:
            return ''
        for pr in PAIRS:
            if sym in str(pr.get('pair', '')):
                return f"{pr['pair']} — {pr['why']}"
        return ''

    cards = [c for st in stages for c in st['cards']]
    print(f'카드 {len(cards)}건 / 기호 사전 {len(SYMS)}건')
    missing = [c['term'] for c in cards if c['term'] not in META]
    if missing:
        print('META 누락:', missing, file=sys.stderr); sys.exit(1)
    print(f"기호 붙은 카드 {sum(1 for c in cards if c['term'] in CARD_SYM)}건 / "
          f"기호 없는 카드 {sum(1 for c in cards if c['term'] not in CARD_SYM)}건")

    O = []
    W = O.append
    W('# 투자자 어드민 용어 해설\n')
    W('용어 하나가 카드 하나다. 카드마다 다섯 가지가 같은 자리에 있다 — '
      '**용어명 · 변수 · 계산식 · 어느 화면 어디인지 · 관련 용어**. '
      '목차는 용어 50건 목록이고, 서술은 전부 뒤 부록으로 뺐다.\n')
    W('**근거**\n')
    W('| 무엇 | 어디 |')
    W('|---|---|')
    W('| 용어와 산식 | `_pipeline/investor_admin/ceo_definitions.md` (대표 정의 원문) |')
    W('| 변수 기호 | `_pipeline/investor_admin/symbol_inventory.json` (원문에서 추출) |')
    W('| 화면 구조·라벨 | `스토리보드_Admin_투자자.pptx` (17슬라이드) |')
    W('| 화면 캡처·좌표 | `_pipeline/investor_admin/shot_rects.json` (정적 화면 헤드리스 캡처 실측) |')
    W('| 기존 값의 소재 | `/Users/semi/cursor/payhug-admin-web` (운영 어드민, 읽기 전용) |')
    W('| 정산채권 DB 구조 | `payhug-spec/analysis/figma_policy_db.md` |')
    W('| 기존 정산 용어 | `payhug-spec/02_TERMS_AND_STATUS.md` · `03_SETTLEMENT_LOGIC.md` |\n')
    W('**숫자에 대한 경고**\n')
    W('할인율 `0.11%`는 대표 정의 원문이 **"0.11% 예정"** 으로 적은 값이다. 확정값이 아니다. '
      '이 문서의 모든 요율·금액은 **예시값**이다.\n')
    W('---\n')
    # ── 카드 규격 — 5필드. 기존 §4 에서 살릴 표 둘만 뒤에 붙인다 ──
    ho = narr['howto']
    src_tbl = ho[ho.index('`이 값은 어디서 오나` 다섯 갈래의 뜻'):ho.index('**계산 예시에 쓰는 숫자 한 벌**')].strip()
    ex_tbl  = ho[ho.index('**계산 예시에 쓰는 숫자 한 벌**'):].strip()
    W('## 카드 한 장에 무엇이 들어 있나\n')
    W('용어 하나에 카드 하나다. 카드마다 아래 다섯이 같은 순서로 온다. 하나라도 빠진 카드는 없다.\n')
    W('| # | 필드 | 무엇 |')
    W('|---|---|---|')
    W('| 1 | **용어명** | 화면에서 보는 이름이 먼저다. 대표 정의서 표기가 다르면 `화면 표기`로 병기한다. '
      '같은 이름이 계통별로 갈리면 `(어느 계통 · 어느 집계 단위)`를 붙인다 |')
    W('| 2 | **변수** | 대표 정의 원문이 쓴 기호(`Ai` `SLi` `PSA` 등)와 그 한국어 이름. '
      '기호를 글자 단위로 쪼갠 풀이가 따라붙는다. 원문에 기호가 없는 용어는 `기호 없음` |')
    W('| 3 | **계산식** | 원문 산식을 그대로 적고, 그 안의 기호를 **그 자리에서** 우리말로 푼 뒤, 숫자 한 벌을 넣어 단계별로 계산한다 |')
    W('| 4 | **화면** | 그 용어가 뜨는 화면 캡처. 이미지를 누르면 확대된다. '
      '용어가 있는 자리는 이미지 위에 상자로 표시한다. 화면에 안 뜨는 용어는 그 값이 흘러드는 자리를 표시하고 `재료`로 적는다 |')
    W('| 5 | **관련 용어** | `재료`(이 용어를 만드는 것)와 `쓰이는 곳`(이 용어를 재료로 쓰는 것). 이름을 누르면 그 카드로 간다 |\n')
    W('다섯 아래에 **값의 출처**(기존 어드민이냐 신설이냐)와 **기획할 때 정해야 할 것**이 접혀 있다. 펼쳐서 본다.\n')
    W('카드 순서는 사전순도 중요도순도 아니다. **앞의 것을 알아야 뒤의 것이 이해되는 순서**로 1단계부터 7단계까지 놓았다. '
      '위에서 아래로 읽으면 재료가 결과보다 먼저 나온다.\n')
    W(src_tbl + '\n')
    W(ex_tbl)
    W('\n---\n')
    W('%%TOC%%\n')
    W('---\n')

    for st in stages:
        if not st['cards']:
            continue
        W(f"# {st['stage']}\n")
        if st['lede']:
            W(st['lede'] + '\n')
        W('---\n')
        for c in st['cards']:
            term, b, meta = c['term'], c['blocks'], META[c['term']]
            W(f'## {term}\n')
            head = [f"**층위** {b['층위'].strip()}"]
            if meta.get('label'):
                head.append(f"**화면 표기** `{meta['label']}`")
            W('  ·  '.join(head) + '\n')
            W(b['한마디로 뭐냐'].strip() + '\n')

            W('### 변수\n')
            sk = CARD_SYM.get(term)
            if sk:
                x = SYMS[sk]
                shown = CARD_CIRCLED.get(term, sk)
                name = x['ko_name']
                if term in CARD_CIRCLED:
                    name = f"화면 항목 번호 {shown} — {name}"
                W(f"[`{shown}`](#{sym_id(sk)}) — **{name}**"
                  f"{'  `문서 명명`' if x.get('coined') else '  `원문 명명`'}\n")
                W(f"| | |")
                W(f"|---|---|")
                W(f"| 단위 | {x.get('unit') or '—'} |")
                W(f"| 뜻 | {x['meaning']} |")
                if x.get('formula'):
                    W(f"| 산식 | `{x['formula']}` |")
                W(f"| 글자 유래 | {x.get('letter_origin') or '—'} |")
                if x.get('coined') and x.get('coined_basis'):
                    W(f"| 이름을 붙인 근거 | {x['coined_basis']} |")
                if x.get('aliases'):
                    W(f"| 다르게 쓰는 표기 | {' · '.join('`'+a+'`' for a in x['aliases'])} |")
                W('')
                if x.get('notes'):
                    W(x['notes'] + '\n')
                pn = pair_note(sk)
                if pn:
                    W(f'**헷갈리는 쌍** {pn}\n')
                if term in CARD_CIRCLED:
                    W('**미확정** 원문이 참조한 이미지가 문서에 없어 `③④⑤⑥`이 가리키는 화면 자리는 확정되지 않았다. '
                      f'위 `{shown}` 대응은 `marker_legend.md` 대조 결과다.\n')
            else:
                W('기호 없음 — 대표 정의 원문이 이 용어에 기호를 붙이지 않았다.\n')
            rs = related_syms(term)
            if rs:
                W('**이 용어가 들어가는 기호** '
                  + ' · '.join(f'[`{r}`](#{sym_id(r)})' for r in rs) + '\n')

            W('### 계산식\n')
            W(b['어떻게 계산하나'].strip() + '\n')

            W('### 화면\n')
            W(f"[[shot: {meta['shot']} | anchor: {meta['anchor']} | kind: {meta['kind']}]]\n")
            W(b['화면 어디에 보이나'].strip() + '\n')

            W('### 관련 용어\n')
            src_, dst_, _ = split_chain(b['다른 용어와 어떻게 이어지나'])
            if src_:
                W(f'**재료** {src_}\n')
            W(f'**쓰이는 곳** {dst_}\n')

            W('### 값의 출처 · 정해야 할 것\n')
            W('**이 값은 어디서 오나** ' + b['이 값은 어디서 오나'].strip() + '\n')
            W('**기획할 때 정해야 할 것** ' + b['기획할 때 정해야 할 것'].strip() + '\n')
            W('---\n')

    # ══ 부록 ══
    W('# 부록 A. 기호 사전 — 산식에 나오는 기호 전건\n')
    W('대표 정의 원문 산식에 나오는 기호 28건과 연산자 4건이다. '
      '한국어 이름은 원문이 붙인 것과 이 문서가 붙인 것을 갈라 표시한다 — '
      f"`원문 명명` {sum(1 for x in G['symbols'] if not x.get('coined'))}건 · "
      f"`문서 명명` {sum(1 for x in G['symbols'] if x.get('coined'))}건.\n")
    W('**영문 약자는 전건 근거 없음** — 원문은 기호를 쓰기만 하고 어느 글자가 무엇의 머리글자인지 적은 문장이 하나도 없다. '
      '기호마다 적은 `글자 유래`는 **원문에서 관찰되는 쓰임**이지 머리글자 판정이 아니다.\n')
    for c in G.get('caveats') or []:
        W(f'- {c}')
    W('')
    groups = []
    for x in G['symbols']:
        if x.get('group') not in groups:
            groups.append(x.get('group'))
    for gname in groups:
        W(f"## {gname}\n")
        W('| 기호 | 한국어 이름 | 명명 | 단위 | 뜻 |')
        W('|---|---|---|---|---|')
        for x in G['symbols']:
            if x.get('group') != gname:
                continue
            W(f"| <a id=\"{sym_id(x['symbol'])}\"></a>`{x['symbol']}` | **{x['ko_name']}** "
              f"| {'문서 명명' if x.get('coined') else '원문 명명'} | {x.get('unit') or '—'} | {x['meaning']} |")
        W('')
        for x in G['symbols']:
            if x.get('group') != gname:
                continue
            bits = []
            if x.get('ceo_source'):
                bits.append(f"원문 `{x['ceo_source']}`")
            if x.get('coined') and x.get('coined_basis'):
                bits.append(f"이름 근거 — {x['coined_basis']}")
            if x.get('aliases'):
                bits.append('다르게 쓰는 표기 ' + ' · '.join('`'+a+'`' for a in x['aliases']))
            if bits:
                W(f"**`{x['symbol']}`** " + '  /  '.join(bits) + '\n')
    W('## 연산자\n')
    W('| 표기 | 한국어 | 뜻 | 나오는 자리 |')
    W('|---|---|---|---|')
    for o in G['operators']:
        W(f"| `{o['symbol']}` | {o['ko_name']} | {o['meaning']} | {' · '.join(o.get('used_in') or []) or '—'} |")
    W('')
    W('## 표기 정본\n')
    W(f"정본은 대표 정의 원문이다 — {G['notation_canon'].get('authority') or '`ceo_definitions.md`'}. "
      "원문을 그대로 옮긴 인용 자리는 원문 표기를 건드리지 않는다. 문서가 스스로 서술한 자리만 아래로 맞춘다.\n")
    W('| 항목 | 정본 | 원문 근거 |')
    W('|---|---|---|')
    for r in G['notation_canon']['rules']:
        W(f"| {r['item']} | `{r['canonical']}` | {r['evidence']} |")
    W('')
    W('## 헷갈리기 쉬운 쌍\n')
    W('| 쌍 | 무엇이 다른가 |')
    W('|---|---|')
    for pr in PAIRS:
        W(f"| {pr['pair']} | {pr['why']} |")
    W('')
    W('---\n')

    APX = [('부록 B. 전체 그림 — 원천 데이터에서 화면 숫자까지', narr['map'], '## 1. 전체 그림 — 원천 데이터에서 화면 숫자까지'),
           ('부록 C. 지금은 그림 가운데가 비어 있다', narr['hole'], '## 1-1. 먼저 알아야 할 사실 — 지금은 그림 가운데가 비어 있다'),
           ('부록 D. 화면에서 본 이름으로 찾기', narr['find'], '## 0. 화면에서 본 이름으로 찾기')]
    for title, txt, drop in APX:
        W(f'# {title}\n')
        W(txt.replace(drop, '').lstrip().strip() + '\n')
        W('---\n')
    NEWT = {'8. 이름 대조표 — 회의에서 헷갈리지 않으려면': ('부록 E. 이름 대조표 — 회의에서 헷갈리지 않으려면', 'E'),
            '9. 새로 만들어야 하는 것 — 개발 범위': ('부록 F. 새로 만들어야 하는 것 — 개발 범위', 'F'),
            '10. 물어야 할 것': ('부록 G. 물어야 할 것', 'G')}
    for st in stages:
        if not st['tail']:
            continue
        newt, letter = NEWT[st['stage']]
        t = st['tail'].replace(f"# {st['stage']}", f'# {newt}', 1)
        t = re.sub(r'^## \d+-(\d+)\. ', lambda m: f'## {letter}-{m.group(1)}. ', t, flags=re.M)
        W(t.strip() + '\n')
        W('---\n')

    out = '\n'.join(O)

    # ── 목차 = 용어 50건 목록 ──
    toc = ['## 용어 50건 — 목차\n',
           '용어명을 누르면 그 카드로 간다. `변수`가 비어 있으면 대표 정의 원문에 기호가 없는 용어다.\n',
           '| # | 용어명 | 변수 | 화면 | 한 줄 뜻 |', '|---|---|---|---|---|']
    n = 0
    for st in stages:
        if not st['cards']:
            continue
        toc.append(f"| | **{st['stage']}** | | | |")
        for c in st['cards']:
            n += 1
            term = c['term']
            sy = CARD_CIRCLED.get(term) or CARD_SYM.get(term)
            m = META[term]
            lbl = m.get('label') or term
            toc.append(f"| {n} | [{term}](#{term}) | {'`'+sy+'`' if sy else '—'} "
                       f"| `{m['shot']}.html` › `{lbl}` | {first_sentence(c['blocks']['한마디로 뭐냐'])} |")
    out = out.replace('%%TOC%%', '\n'.join(toc))

    open(SRC, 'w', encoding='utf-8').write(out)
    print(f'원고 재조판 완료 — {len(out.splitlines())}행, 카드 {n}건')


if __name__ == '__main__':
    main()
