#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""glossary_manuscript.md → payhug-investor-admin/glossary.html

용어 1건 = 카드 1개, 5필드 고정 (용어명 · 변수 · 계산식 · 화면 · 관련 용어).
화면 필드는 정적 화면 캡처 + CSS 좌표 오버레이 + 순수 JS 라이트박스.
좌표는 shot_rects.json 실측값이고 이미지에 굽지 않는다.
"""
import html as H
import json, os, re, sys

PIPE = os.path.dirname(os.path.abspath(__file__))
REPO = '/Users/semi/cursor/payhug-investor-admin'
SRC  = os.path.join(PIPE, 'glossary_manuscript.md')
RECT = os.path.join(PIPE, 'shot_rects.json')
OUT  = os.path.join(REPO, 'glossary.html')

RECTS = {s['file'][:-5]: s for s in json.load(open(RECT, encoding='utf-8'))['screens']}

# 화면 파일명 → 사람이 부르는 화면 이름 (좌측 메뉴 표기 기준)
SCREEN = {
    'invest-assets': '투자 자산',
    'invest-assets--page2': '투자 자산 (2페이지)',
    'invest-assets--cert-confirm': '투자 자산 (증명서 발급 확인)',
    'invest-profit': '투자 수익',
    # D-34(기간 필터 일별·주별·월별 3단)로 주별 낱장 신설 — 캡처 목록과 짝을 맞춘다
    'invest-profit--weekly': '투자 수익 (주별)',
    'invest-profit--monthly': '투자 수익 (월별)',
    'merchants': '가맹점',
    'acquisition': '정산채권 양수',
    'contracts': '계약기록',
    'coocon': '쿠콘 관리 현금',
    'certificate': '가맹점별 투자자산 증명서',
    'xls-profit-status': '투자수익 현황 엑셀',
    'xls-profit-daily': '일별 투자수익 엑셀',
    'xls-assets-status': '투자자산 현황 엑셀',
    'xls-assets-merchant': '가맹점별 투자자산 엑셀',
}
FIELDS = ['term', 'var', 'calc', 'screen', 'rel']

# 캡션 현행화 표 — 캡처가 옛 화면에 묶여 있을 때, 이미지 밖 텍스트인 캡션만
# 현행 화면값으로 맞추는 자리. 치환은 이 표 한 곳에서만 하고
# verify_shotmarks.py 가 같은 표를 불러 앵커 text 에도 똑같이 걸어 대조한다.
#
# 2026-08-31 — 지금은 0건이다. 캡처 5장을 현행 화면으로 다시 찍어(capture_shots.js)
# 앵커 text 자체가 현행값이 됐다. 옛 규칙
#   'Ty수익율 투자실행금액 대비 12.97% 투자자산 대비 10.72%' → '3.99% / 2.24%'
# 은 대상 문자열이 shot_rects.json 에서 사라져 어느 자리에도 걸리지 않는다.
# 규칙을 지운 것이지 검사를 끈 것이 아니다 — cap_text 와 verify_shotmarks 의 짝은 그대로고,
# 캡처가 현행인지는 verify_shots.js 의 B2(원본 HTML sha256)·C1(재현 바이트)이 판정한다.
CAP_FIX = ()


def cap_text(t):
    for a, b in CAP_FIX:
        t = t.replace(a, b)
    return t


# ══════════════════════════════════════════════════════════════════
#  마크다운 → HTML (이 문서가 쓰는 문법만)
# ══════════════════════════════════════════════════════════════════
RAWA = re.compile(r'<a id="([a-zA-Z0-9\-]+)"></a>')

# ── 아래첨자 조판 ──
#  원고는 마크다운 규약 A_i · A_{D-1,i} · SA_{D-1} 로 쓰고, 화면에는 <sub> 로 낸다.
#  하이픈은 빼기표 −(U+2212), 쉼표 뒤에는 가는 공백을 넣는다.
#  대표 원문을 그대로 옮긴 자리는 원고가 평문(AD-1i · SAD-1)이라 이 정규식에 걸리지 않는다.
SUBRE = re.compile(r'(?<![A-Za-z0-9_])(SMR|SB|SA|SM|SD|SL|A|B|M|D)_(?:\{(D-1,i|D-1|p,i)\}|(i))(?![A-Za-z0-9_])')


def subs(t):
    def one(m):
        body = (m.group(2) or m.group(3)).replace('-', '\u2212').replace(',', ',&thinsp;')
        return f'{m.group(1)}<sub>{body}</sub>'
    return SUBRE.sub(one, t)


def flat(t):
    """alt·검색키처럼 태그를 못 넣는 자리 — 아래첨자 표시만 걷어 낸다."""
    return SUBRE.sub(lambda m: m.group(1) + (m.group(2) or m.group(3)).replace(',', ''), t)


# ── 원문 인용 블록 ──
#  라벨이 「원문…:」인 코드펜스는 대표 정의서를 그대로 옮긴 자리다. 아래첨자로 바꾸지 않고,
#  글자가 원문과 어긋나면 여기서 빌드를 세운다.
CEO = open(os.path.join(PIPE, 'ceo_definitions.md'), encoding='utf-8').read()
CEOT = re.sub(r'\s+', '', CEO)
QUOTE_LAB = {'원문이 화면 수정 지시도 함께 달아 두었다.'}
QNOTE = re.compile(r'←.*$')


def is_quote(label):
    l = label.strip()
    return l.startswith('원문') and (l.endswith(':') or l in QUOTE_LAB)


def check_quote(body):
    """인용 블록 각 줄이 원문에 글자 그대로 있는가. 없으면 그 줄을 돌려준다."""
    bad = []
    for ln in body.split('\n'):
        s = QNOTE.sub('', ln)
        for frag in s.split('…'):
            f = re.sub(r'\s+', '', frag)
            if len(f) >= 8 and f not in CEOT:
                bad.append(ln.strip())
                break
    return bad

def inline(t, xref=None, self_id=None):
    keep = []
    def stash(m):
        keep.append(f'<a id="{m.group(1)}"></a>')
        return f'\x00{len(keep)-1}\x00'
    t = RAWA.sub(stash, t)
    t = H.escape(t, quote=False)
    t = re.sub(r'`([^`]+)`', lambda m: '<code>' + m.group(1) + '</code>', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'\[([^\]]+)\]\(#((?:[^()]|\([^()]*\))+)\)',
               lambda m: f'<a class="xref" href="#{xref(m.group(2)) if xref else m.group(2)}">{m.group(1)}</a>', t)
    if xref:                                   # 백틱 용어를 카드 앵커로
        def link(m):
            tid = xref(m.group(1), soft=True)
            if not tid or tid == self_id:
                return m.group(0)
            return f'<a class="xref" href="#{tid}">{m.group(0)}</a>'
        t = re.sub(r'<code>([^<]+)</code>', link, t)
    t = re.sub(r'\x00(\d+)\x00', lambda m: keep[int(m.group(1))], t)
    return subs(t)


def _visible_backticks(out):
    """조판 결과에서 화면에 글자로 뜨는 백틱 자리를 집는다.

    마크다운 백틱이 <code> 로 안 바뀌고 그대로 남으면 화면에 ` 가 찍힌다. 제목·리드처럼
    inline()·blocks() 를 안 태운 자리에서 그렇게 됐다. 태그·스크립트·스타일을 걷은 뒤 센다.
    """
    t = re.sub(r'<(script|style)\b.*?</\1>', ' ', out, flags=re.S | re.I)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = H.unescape(t)
    return [m.group(0).replace('\n', ' ') for m in re.finditer(r'.{0,40}`.{0,40}', t, re.S)]


def blocks(md, xref=None, self_id=None):
    """문단·목록·표·코드펜스·인용만 다룬다."""
    o, i, L = [], 0, md.split('\n')
    IN = lambda s: inline(s, xref, self_id)
    while i < len(L):
        ln = L[i]
        if not ln.strip():
            i += 1; continue
        if ln.startswith('```'):
            j = i + 1
            while j < len(L) and not L[j].startswith('```'):
                j += 1
            body = '\n'.join(L[i+1:j])
            lab = next((L[k] for k in range(i - 1, -1, -1) if L[k].strip()), '')
            if is_quote(lab):
                bad = check_quote(body)
                if bad:
                    raise SystemExit('!! 원문 인용 블록이 원문과 다르다 %d줄\n   %s'
                                     % (len(bad), '\n   '.join(bad[:3])))
                o.append('<pre class="calc quote">' + H.escape(body) + '</pre>')
            else:
                o.append('<pre class="calc">' + subs(H.escape(body)) + '</pre>')
            i = j + 1; continue
        if ln.startswith('|'):
            j = i
            while j < len(L) and L[j].startswith('|'):
                j += 1
            rows = [r for r in L[i:j]]
            cells = lambda r: [c.strip() for c in r.strip().strip('|').split('|')]
            head = cells(rows[0])
            body = rows[2:] if len(rows) > 1 and set(rows[1].replace('|', '').strip()) <= set('-: ') else rows[1:]
            th = ''.join(f'<th>{IN(c)}</th>' for c in head)
            tr = ''
            for r in body:
                cs = cells(r)
                tr += '<tr>' + ''.join(f'<td>{IN(c)}</td>' for c in cs) + '</tr>'
            blank = all(not c for c in head)
            o.append('<div class="t-card"><div class="t-scroll"><table class="tbl">'
                     + ('' if blank else f'<thead><tr>{th}</tr></thead>')
                     + f'<tbody>{tr}</tbody></table></div></div>')
            i = j; continue
        if re.match(r'^[-*] ', ln):
            j = i
            while j < len(L) and re.match(r'^[-*] ', L[j]):
                j += 1
            o.append('<ul>' + ''.join(f'<li>{IN(x[2:])}</li>' for x in L[i:j]) + '</ul>')
            i = j; continue
        if re.match(r'^\d+\. ', ln):
            j = i
            while j < len(L) and re.match(r'^\d+\. ', L[j]):
                j += 1
            o.append('<ol>' + ''.join(f'<li>{IN(re.sub(chr(94)+chr(92)+"d+. ", "", x))}</li>' for x in L[i:j]) + '</ol>')
            i = j; continue
        if ln.startswith('> '):
            o.append(f'<blockquote>{IN(ln[2:])}</blockquote>'); i += 1; continue
        if ln.strip() == '---':
            i += 1; continue
        if ln.startswith('### '):
            o.append(f'<h4 class="mini-h">{IN(ln[4:])}</h4>'); i += 1; continue
        if ln.startswith('## '):
            o.append(f'<h3 class="blk-title">{IN(ln[3:])}</h3>'); i += 1; continue
        j = i
        while j < len(L) and L[j].strip() and not L[j].startswith(('|', '```', '- ', '> ', '#')) \
                and not re.match(r'^\d+\. ', L[j]) and L[j].strip() != '---':
            j += 1
        o.append('<p>' + IN(' '.join(x.strip() for x in L[i:j])) + '</p>')
        i = j
    return '\n'.join(o)


# ══════════════════════════════════════════════════════════════════
#  화면 캡처 + 좌표 오버레이
# ══════════════════════════════════════════════════════════════════
def find_rect(shot, spec):
    """`tag:text#n` → 문서 좌표 사각형."""
    sc = RECTS[shot]
    tag = None
    m = re.match(r'([a-z0-9]+):(.*)$', spec)
    if m:
        tag, spec = m.group(1), m.group(2)
    nth = 0
    m = re.match(r'(.*)#(\d+)$', spec)
    if m:
        spec, nth = m.group(1), int(m.group(2))
    cand = [it for it in sc['items'] if (tag is None or it['tag'] == tag)]
    low = spec.lower()
    exact = [it for it in cand if it['text'].strip().lower() == low]
    part  = [it for it in cand if low in it['text'].lower()]
    hits = exact or part
    if not hits:
        raise SystemExit(f'!! 앵커 못 찾음: {shot} / {tag}:{spec}')
    return hits[min(nth, len(hits) - 1)], sc


def shot_html(shot, spec, kind, term):
    it, sc = find_rect(shot, spec)
    W, Hh = sc['docW'], sc['docH']
    pad = 5
    x = max(0, it['x'] - pad); y = max(0, it['y'] - pad)
    w = min(W - x, it['w'] + pad * 2); h = min(Hh - y, it['h'] + pad * 2)
    L_, T_ = x / W * 100, y / Hh * 100
    Wp, Hp = w / W * 100, h / Hh * 100
    yc = (y + h / 2) / Hh
    src = f"assets/shots/{shot}.webp"
    name = SCREEN.get(shot, shot)
    lab = '이 자리' if kind == 'direct' else '재료 — 이 자리 뒤에 숨는다'
    ctext = cap_text(it['text'])
    cap = f"{name} · {ctext[:40] or it['tag']}"
    alt = f"{name} 화면 캡처 — {flat(term)} 이 표시되는 자리"
    mk = (f'<span class="mark {kind}" style="left:{L_:.3f}%;top:{T_:.3f}%;'
          f'width:{Wp:.3f}%;height:{Hp:.3f}%"><i>{H.escape(lab)}</i></span>')
    img = (f'<img src="{src}" alt="{H.escape(alt)}" loading="lazy" decoding="async" '
           f'width="{sc["imgW"]}" height="{sc["imgH"]}">')
    return f'''<figure class="shot">
<button class="crop" type="button" data-shot="{src}" data-yc="{yc:.5f}"
  data-mark="{L_:.3f},{T_:.3f},{Wp:.3f},{Hp:.3f}" data-kind="{kind}" data-lab="{H.escape(lab)}"
  data-cap="{H.escape(cap)}" aria-label="{H.escape(alt)} — 눌러서 확대">
  <span class="pan" data-yc="{yc:.5f}" style="transform:translateY(calc(130px - {yc*100:.3f}%))">{img}{mk}</span>
  <span class="zoom">확대</span>
</button>
<figcaption><b>{H.escape(name)}</b> · {H.escape(ctext[:56] or it['tag'])}
<span class="kd {kind}">{'화면에 뜬다' if kind == 'direct' else '화면에 안 뜬다 — 재료'}</span></figcaption>
</figure>'''


# ══════════════════════════════════════════════════════════════════
#  원고 파싱
# ══════════════════════════════════════════════════════════════════
def parse():
    s = open(SRC, encoding='utf-8').read()
    doc = {'title': re.match(r'# (.+)', s).group(1).strip()}
    parts = re.split(r'\n(?=# )', s)
    doc['front'] = parts[0][parts[0].index('\n'):].strip()
    doc['stages'], doc['apx'] = [], []
    for p in parts[1:]:
        t = re.match(r'# (.+)', p).group(1).strip()
        body = p[p.index('\n'):]
        if re.match(r'\d단계', t):
            first = body.find('\n## ')
            cards = []
            for c in re.split(r'\n(?=## )', body[first:] if first >= 0 else ''):
                cm = re.match(r'## (.+)', c)
                if not cm:
                    continue
                cards.append((cm.group(1).strip(), c[cm.end():]))
            doc['stages'].append({'t': t, 'lede': body[:first].strip(' \n-') if first >= 0 else '',
                                  'cards': cards})
        else:
            doc['apx'].append({'t': t, 'body': body.strip(' \n-')})
    return doc


def card_parts(raw):
    """카드 본문을 머리·리드·5필드로 가른다."""
    idx = [(m.start(), m.end(), m.group(1)) for m in re.finditer(r'^### (.+)$', raw, re.M)]
    head = raw[:idx[0][0]] if idx else raw
    out = {}
    for n, (a, b, name) in enumerate(idx):
        end = idx[n + 1][0] if n + 1 < len(idx) else len(raw)
        out[name] = raw[b:end].strip()
    lines = head.strip().split('\n')
    meta = ''
    if lines and lines[0].startswith('**층위**'):
        meta, lines = lines[0], lines[1:]
    lede = '\n'.join(lines).strip()
    return meta, lede, out


CSS = r'''
body { background: var(--gray-50); }
.topbar { position: sticky; top: 0; z-index: 40; background: rgba(249,250,251,0.94);
  backdrop-filter: blur(8px); border-bottom: 1px solid var(--gray-200); }
.topbar-in { max-width: 1280px; margin: 0 auto; padding: 10px 32px; display: flex;
  align-items: center; gap: 16px; flex-wrap: wrap; }
.tb-brand { display: flex; align-items: center; gap: 10px; flex-shrink: 0; }
.tb-brand .logo-mark { width: 28px; height: 28px; border-radius: 7px; }
.tb-name { font-size: 14px; line-height: 20px; font-weight: 700; color: var(--gray-900); white-space: nowrap; }
.tb-name em { font-style: normal; color: var(--primary-600); }
.tb-search { position: relative; flex: 1; min-width: 200px; max-width: 400px; }
.tb-search input { width: 100%; height: 36px; padding: 0 12px; border: 1px solid var(--gray-200);
  border-radius: 10px; background: #fff; font-size: 13px; color: var(--gray-900); }
.tb-search input:focus { border-color: var(--primary); box-shadow: 0 0 0 2px rgba(127,225,65,0.2); outline: none; }
.tb-count { font-size: 12px; color: var(--gray-400); font-family: var(--font-mono); white-space: nowrap; }
.tb-count b { color: var(--primary-700); }
.tb-alt { margin-left: auto; display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.tb-alt a { font-size: 12px; font-weight: 600; color: var(--gray-500); text-decoration: none;
  border: 1px solid var(--gray-200); background: #fff; border-radius: 8px; padding: 5px 10px; }
.tb-alt a:hover { border-color: var(--primary); color: var(--primary-700); }

.doc { max-width: 1280px; margin: 0 auto; padding: 0 32px 120px; display: grid;
  grid-template-columns: 250px minmax(0,1fr); gap: 40px; align-items: start; }
.toc { position: sticky; top: 68px; padding-top: 24px; max-height: calc(100vh - 84px); overflow-y: auto; }
.toc-h { font-size: 11px; font-weight: 700; color: var(--gray-400); letter-spacing: .05em;
  text-transform: uppercase; margin: 14px 0 6px 10px; }
.toc a { display: block; padding: 5px 10px; border-left: 2px solid transparent; font-size: 12.5px;
  line-height: 18px; color: var(--gray-500); text-decoration: none; border-radius: 0 6px 6px 0; }
.toc a:hover { background: var(--gray-100); color: var(--gray-800); }
.toc a.cur { background: var(--primary-50); border-left-color: var(--primary); color: var(--primary-700); font-weight: 700; }
.toc a .sy { font-family: var(--font-mono); font-size: 11px; color: var(--gray-400); margin-left: 4px; }
.main { min-width: 0; padding-top: 24px; }

.doc-head h1 { font-size: 30px; line-height: 40px; font-weight: 700; color: var(--gray-900); margin: 0; letter-spacing: -.01em; }
.doc-head .lede { font-size: 15px; line-height: 26px; color: var(--gray-600); margin: 12px 0 0; max-width: 62em; }
.sec { margin-top: 56px; scroll-margin-top: 72px; }
.sec > h2 { font-size: 22px; line-height: 30px; font-weight: 700; color: var(--gray-900); margin: 0; letter-spacing: -.01em; }
.sec > .sec-lede { font-size: 14px; line-height: 24px; color: var(--gray-600); margin: 10px 0 0; max-width: 60em; }
.sec > .sec-lede > *:first-child { margin-top: 0; }
.sec > .sec-lede p { font-size: 14px; line-height: 24px; color: var(--gray-600); margin: 12px 0 0; }
h3.blk-title { font-size: 16px; line-height: 25px; font-weight: 700; color: var(--gray-900); margin: 32px 0 0; }
h4.mini-h { font-size: 14px; line-height: 22px; font-weight: 700; color: var(--gray-800); margin: 22px 0 0; }
p { font-size: 14px; line-height: 25px; color: var(--gray-700); margin: 12px 0 0; max-width: 62em; }
ul, ol { font-size: 14px; line-height: 25px; color: var(--gray-700); margin: 10px 0 0; padding-left: 20px; max-width: 62em; }
li { margin: 4px 0; }
li::marker { color: var(--gray-400); }
b, strong { font-weight: 700; color: var(--gray-900); }
blockquote { margin: 14px 0 0; padding: 10px 16px; border-left: 3px solid var(--gray-300);
  background: var(--gray-100); border-radius: 0 8px 8px 0; font-size: 13px; line-height: 22px; color: var(--gray-700); }
code { font-family: var(--font-mono); font-size: .88em; background: var(--gray-100); color: var(--gray-800);
  border-radius: 4px; padding: 1px 5px; overflow-wrap: anywhere; }
a.xref { color: var(--primary-700); text-decoration: none; border-bottom: 1px solid var(--primary-200); font-weight: 600; }
a.xref:hover { background: var(--primary-50); border-bottom-color: var(--primary); }
a.xref code { background: var(--primary-50); color: var(--primary-800); }
pre.calc { font-family: var(--font-mono); font-size: 12.5px; line-height: 21px; background: var(--gray-900);
  color: #e8f6dd; border-radius: 12px; padding: 16px 18px; margin: 14px 0 0; overflow-x: auto; }
pre.calc.quote { border-left: 4px solid var(--brand-500, #7bc043); }
.t-card { background: #fff; border: 1px solid var(--gray-100); border-radius: 14px;
  box-shadow: var(--shadow-card); overflow: hidden; margin-top: 14px; }
.t-scroll { overflow-x: auto; }
table.tbl { width: 100%; border-collapse: collapse; }
table.tbl th, table.tbl td { text-align: left; padding: 9px 14px; border-bottom: 1px solid var(--gray-100);
  font-size: 13px; line-height: 21px; vertical-align: top; }
table.tbl th { background: var(--gray-50); font-weight: 700; color: var(--gray-800); white-space: nowrap; }
table.tbl tr:last-child td { border-bottom: 0; }
table.tbl td:first-child { color: var(--gray-900); }

/* ── 용어 카드 ── */
.term { background: #fff; border: 1px solid var(--gray-200); border-radius: 18px; padding: 24px 26px 20px;
  margin-top: 22px; scroll-margin-top: 72px; box-shadow: var(--shadow-card); }
.term-head { display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap; }
.term-no { font-family: var(--font-mono); font-size: 12px; font-weight: 700; color: var(--primary-600); }
.term-head h3 { font-size: 20px; line-height: 29px; font-weight: 700; color: var(--gray-900); margin: 0; letter-spacing: -.01em; }
.chip { display: inline-block; border-radius: 9999px; padding: 2px 9px; font-size: 11px; line-height: 17px; font-weight: 700; white-space: nowrap; }
.chip.screenlab { background: var(--emerald-50); color: var(--emerald-700); border: 1px solid var(--emerald-200); font-family: var(--font-mono); }
.chip.lv { background: var(--gray-100); color: var(--gray-600); }
.chip.lv.ui { background: var(--primary-50); color: var(--primary-800); }
.term > .lede-line { font-size: 14.5px; line-height: 25px; color: var(--gray-700); margin: 12px 0 0; }
.fld { margin-top: 22px; padding-top: 18px; border-top: 1px dashed var(--gray-200); }
.fld > .fh { display: flex; align-items: center; gap: 8px; font-size: 11px; font-weight: 700;
  letter-spacing: .06em; color: var(--gray-400); text-transform: uppercase; }
.fld > .fh .n { width: 17px; height: 17px; border-radius: 50%; background: var(--gray-200); color: var(--gray-600);
  font-size: 10px; line-height: 17px; text-align: center; letter-spacing: 0; }
.fld > .fh .ko { color: var(--gray-700); font-size: 12px; letter-spacing: 0; }
.fld p:first-of-type { margin-top: 10px; }

/* ── 화면 캡처 · 오버레이 ── */
.shot { margin: 12px 0 0; }
.crop { display: block; position: relative; width: 100%; height: 260px; overflow: hidden;
  border: 1px solid var(--gray-200); border-radius: 12px; background: var(--gray-100);
  padding: 0; cursor: zoom-in; }
.crop .pan { position: absolute; left: 0; top: 0; width: 100%; display: block; }
.crop img { display: block; width: 100%; height: auto; }
.crop .zoom { position: absolute; right: 10px; bottom: 10px; background: rgba(17,24,39,.82); color: #fff;
  font-size: 11px; font-weight: 700; border-radius: 7px; padding: 4px 9px; }
.crop:hover .zoom { background: var(--primary-700); }
.crop:focus-visible { outline: 2px solid var(--primary); outline-offset: 2px; }
.mark { position: absolute; border-radius: 5px; box-shadow: 0 0 0 9999px rgba(17,24,39,.30); }
.mark.direct { border: 2px solid var(--primary); background: rgba(127,225,65,.16); }
.mark.indirect { border: 2px dashed var(--amber-500, #f59e0b); background: rgba(245,158,11,.14); }
.mark i { position: absolute; left: 0; top: -21px; font-style: normal; font-size: 10.5px; font-weight: 700;
  line-height: 17px; padding: 0 6px; border-radius: 5px; white-space: nowrap; }
.mark.direct i { background: var(--primary); color: #10240a; }
.mark.indirect i { background: var(--amber-500, #f59e0b); color: #2b1a00; }
.shot figcaption { font-size: 11.5px; line-height: 18px; color: var(--gray-500); margin-top: 7px;
  display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.kd { border-radius: 9999px; padding: 1px 8px; font-size: 10.5px; font-weight: 700; }
.kd.direct { background: var(--primary-50); color: var(--primary-800); }
.kd.indirect { background: var(--amber-50, #fffbeb); color: var(--amber-800, #92400e); }

/* ── 라이트박스 ── */
.lb { position: fixed; inset: 0; z-index: 90; background: rgba(9,12,18,.86); display: none;
  padding: 26px; overflow: auto; }
.lb.on { display: block; }
.lb-in { position: relative; margin: 0 auto; width: max-content; max-width: 100%; }
.lb-wrap { position: relative; display: block; }
.lb-wrap img { display: block; max-width: 100%; height: auto; border-radius: 10px; background: #fff; }
.lb.real .lb-in { width: auto; }
.lb.real .lb-wrap img { max-width: none; width: var(--nw); }
.lb-bar { position: sticky; top: 0; display: flex; gap: 10px; align-items: center; margin-bottom: 12px;
  color: #fff; font-size: 12.5px; flex-wrap: wrap; }
.lb-bar .cap { font-family: var(--font-mono); opacity: .85; }
.lb-bar button { background: rgba(255,255,255,.12); color: #fff; border: 1px solid rgba(255,255,255,.25);
  border-radius: 8px; padding: 5px 11px; font-size: 12px; font-weight: 700; cursor: pointer; }
.lb-bar button:hover { background: rgba(255,255,255,.24); }
.lb-bar .sp { margin-left: auto; }

.hidden { display: none !important; }
.nores { font-size: 14px; color: var(--gray-500); margin-top: 20px; }

@media (max-width: 1100px) {
  .doc { grid-template-columns: 1fr; gap: 0; }
  .toc { position: static; max-height: none; padding-top: 18px; }
  .toc-list { display: flex; flex-wrap: wrap; gap: 4px; }
  .toc-list a { border-left: 0; border: 1px solid var(--gray-200); background: #fff; border-radius: 8px; }
}
@media (max-width: 720px) {
  .doc, .topbar-in { padding-left: 18px; padding-right: 18px; }
  .term { padding: 20px 18px 16px; }
  .crop { height: 210px; }
}
'''

JS = r'''
(function(){
  /* 크롭 위치 — 표시 좌표를 컨테이너 안에 가둔다 */
  function place(){
    document.querySelectorAll('.crop').forEach(function(c){
      var pan = c.querySelector('.pan'); if(!pan) return;
      var ph = pan.offsetHeight, ch = c.clientHeight;
      if(!ph) return;
      var want = ch/2 - parseFloat(pan.dataset.yc) * ph;
      var min = Math.min(0, ch - ph);
      pan.style.transform = 'translateY(' + Math.max(min, Math.min(0, want)).toFixed(1) + 'px)';
    });
  }
  window.addEventListener('load', place);
  window.addEventListener('resize', place);
  document.addEventListener('DOMContentLoaded', function(){ setTimeout(place, 60); });

  /* 라이트박스 */
  var lb = document.getElementById('lb'), img = document.getElementById('lb-img'),
      mk = document.getElementById('lb-mark'), cap = document.getElementById('lb-cap'),
      real = document.getElementById('lb-real'), last = null;
  function open(btn){
    var m = btn.dataset.mark.split(',');
    img.src = btn.dataset.shot;
    img.alt = btn.getAttribute('aria-label') || '';
    mk.className = 'mark ' + btn.dataset.kind;
    mk.style.left = m[0] + '%'; mk.style.top = m[1] + '%';
    mk.style.width = m[2] + '%'; mk.style.height = m[3] + '%';
    mk.innerHTML = '<i></i>'; mk.firstChild.textContent = btn.dataset.lab;
    cap.textContent = btn.dataset.cap;
    lb.classList.remove('real'); real.textContent = '실제 크기';
    lb.classList.add('on'); document.body.style.overflow = 'hidden';
    last = btn; real.focus();
  }
  function close(){
    lb.classList.remove('on'); lb.classList.remove('real');
    document.body.style.overflow = ''; if(last) last.focus(); last = null;
  }
  document.addEventListener('click', function(e){
    var b = e.target.closest('.crop');
    if(b){ e.preventDefault(); open(b); return; }
    if(e.target.closest('#lb-close')){ close(); return; }
    if(e.target.closest('#lb-real')){
      var on = lb.classList.toggle('real');
      lb.style.setProperty('--nw', (img.naturalWidth/2) + 'px');
      real.textContent = on ? '화면에 맞추기' : '실제 크기';
      return;
    }
    if(lb.classList.contains('on') && !e.target.closest('.lb-in')) close();
  });
  document.addEventListener('keydown', function(e){
    if(e.key === 'Escape' && lb.classList.contains('on')) close();
  });

  /* 검색 — 카드와 목차를 함께 거른다 */
  var q = document.getElementById('q'), cnt = document.getElementById('cnt'),
      cards = [].slice.call(document.querySelectorAll('.term')),
      links = [].slice.call(document.querySelectorAll('.toc-list a[data-t]')),
      none = document.getElementById('nores');
  function filt(){
    var v = (q.value || '').trim().toLowerCase(), n = 0;
    cards.forEach(function(c){
      var hit = !v || c.dataset.k.indexOf(v) >= 0;
      c.classList.toggle('hidden', !hit); if(hit) n++;
    });
    links.forEach(function(a){
      a.classList.toggle('hidden', !!v && a.dataset.k.indexOf(v) < 0);
    });
    document.querySelectorAll('.stage-sec').forEach(function(s){
      s.classList.toggle('hidden', !s.querySelector('.term:not(.hidden)'));
    });
    if(cnt) cnt.textContent = v ? (n + '건') : '';
    none.classList.toggle('hidden', n > 0);
  }
  if(q){ q.addEventListener('input', filt); }

  /* 현재 위치 표시 */
  var obs = new IntersectionObserver(function(es){
    es.forEach(function(e){
      if(!e.isIntersecting) return;
      var a = document.querySelector('.toc-list a[href="#' + e.target.id + '"]');
      if(!a) return;
      document.querySelectorAll('.toc-list a.cur').forEach(function(x){ x.classList.remove('cur'); });
      a.classList.add('cur');
    });
  }, {rootMargin: '-72px 0px -70% 0px'});
  cards.forEach(function(c){ obs.observe(c); });
})();
'''


HEAD = '''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/base.css">
<style>%(css)s</style>
</head>
<body>
<div class="topbar"><div class="topbar-in">
  <div class="tb-brand"><img class="logo-mark" src="assets/logo-icon.png" alt="">
    <span class="tb-name">투자자 어드민 <em>용어 해설</em></span></div>
  <div class="tb-search"><input id="q" type="search" placeholder="용어·기호·화면 이름으로 찾기"
    aria-label="용어 찾기" autocomplete="off"></div>
  <span class="tb-count" id="cnt"></span>
  <div class="tb-alt">%(alt)s</div>
</div></div>
<div class="doc">
'''

FOOT = '''</div>
<div class="lb" id="lb" role="dialog" aria-modal="true" aria-label="화면 캡처 확대">
  <div class="lb-in">
    <div class="lb-bar"><span class="cap" id="lb-cap"></span>
      <span class="sp"></span>
      <button type="button" id="lb-real">실제 크기</button>
      <button type="button" id="lb-close">닫기 (Esc)</button></div>
    <span class="lb-wrap"><img id="lb-img" src="" alt=""><span class="mark" id="lb-mark"></span></span>
  </div>
</div>
<script>%(js)s</script>
</body>
</html>
'''


def main():
    doc = parse()
    ids, order = {}, []
    for st in doc['stages']:
        for term, _ in st['cards']:
            n = len(order) + 1
            ids[term] = f't{n:02d}'
            order.append(term)
    assert len(order) == 50, f'카드 {len(order)}건'

    ALIAS = {
        '투자실행액': '투자 실행액', '순현금': '순현금 (투자 자산 · 잔액)',
        '할인율': '유동화투자자의 할인율', '투자자 요율': '유동화투자자의 할인율',
        'w금융일수': 'w금융일수 (투자 자산 · 잔액)', 'W금융일수': 'w금융일수 (투자 자산 · 잔액)',
        'ty수익율': 'ty수익율 (투자 자산 · 잔액)', 'Ty수익율': 'ty수익율 (투자 자산 · 잔액)',
        'ty수익율(잔액식)': 'ty수익율 (투자 자산 · 잔액)',
        'ty수익율(일별)': 'ty수익율 (일별 배치 · 하루치)',
        'w금융일수 SD': 'w금융일수 (일별 배치 · 하루치)',
        '상환액 SB': '상환액 (일별 배치 · 하루치)', '상환액': '상환액 (일별 배치 · 하루치)',
        '투자실행금 SA': '투자실행금 (일별 배치 · 하루치)', '투자실행금': '투자실행금 (일별 배치 · 하루치)',
        '투자수익 SM': '투자수익 (일별 배치 · 하루치)', '투자수익': '투자수익 (일별 배치 · 하루치)',
        '투자수익율 SMR': '투자수익율 (일별 배치 · 하루치)', '투자수익율': '투자수익율 (일별 배치 · 하루치)',
        'PSA': '투자실행금 (투자 수익 · 기간 합계)', 'PSM': '투자수익 (투자 수익 · 기간 합계)',
        '순현금 EC': '순현금 (일별 배치 · 자정 시점)', 'EC': '순현금 (일별 배치 · 자정 시점)',
        '채권매입업체': '유동화투자자', '재양도합의서': '정산금채권 재양도 합의서',
        '④': 'ty수익율 › 투자실행금액 대비 (투자 수익 · 기간 합계)',
        '⑤': 'ty수익율 › 투자자산 대비 (투자 수익 · 기간 합계)',
        '⑥': 'ty수익율 (일별 표 · 행 단위)',
    }
    SYMIDS = set(re.findall(r'<a id="(sym-[A-Za-z0-9]+)"></a>', open(SRC, encoding='utf-8').read()))

    def xref(key, soft=False):
        k = key.strip()
        if k in ids:
            return ids[k]
        if k in ALIAS and ALIAS[k] in ids:
            return ids[ALIAS[k]]
        if k in SYMIDS or k.startswith('sym-'):
            return k
        return None if soft else k

    O = [HEAD % {'title': doc['title'], 'css': CSS,
                 # 상단 우측 통로는 전체 목록 하나뿐이다. 구버전 판은 금융일수 10~13일·ty 3.57% 로
                 # 짜여 대표 정의(금융일수 2.0~6.2일)와 뿌리부터 어긋나고 생성기도 없어,
                 # 링크가 아니라 파일 자체가 배포에서 빠져 있다(보관처는 파이프라인).
                 'alt': '<a href="index.html">전체 목록</a>'}]
    W = O.append

    # ── 좌측 목차 = 용어 50건 ──
    W('<nav class="toc" aria-label="용어 목차"><div class="toc-list">')
    W('<div class="toc-h">목차</div>')
    for st in doc['stages']:
        W(f'<div class="toc-h">{H.escape(st["t"].split(" — ")[0])}</div>')
        for term, raw in st['cards']:
            _, _, f = card_parts(raw)
            sy = ''
            m = re.match(r'\[`([^`]+)`\]', (f.get('변수') or '').strip())
            if m:
                sy = f'<span class="sy">{subs(H.escape(m.group(1)))}</span>'
            key = (term + ' ' + flat(term) + ' ' + (f.get('변수') or '')[:80]).lower()
            W(f'<a href="#{ids[term]}" data-t="1" data-k="{H.escape(key, quote=True)}">'
              f'{subs(H.escape(term))}{sy}</a>')
    W('<div class="toc-h">부록</div>')
    for i, a in enumerate(doc['apx']):
        W(f'<a href="#apx{i}">{H.escape(a["t"])}</a>')
    W('</div></nav>')

    W('<main class="main">')
    W(f'<div class="doc-head"><h1>{H.escape(doc["title"])}</h1></div>')
    W(blocks(doc['front'], xref))

    for si, st in enumerate(doc['stages']):
        # 제목에도 백틱 코드 표기가 온다 — inline() 을 태워야 글자로 새지 않는다.
        W(f'<section class="sec stage-sec" id="s{si}"><h2>{inline(st["t"])}</h2>')
        if st['lede']:
            # 리드는 한 문단이 아니다 — 코드펜스·표·목록이 섞여 온다. blocks() 로 통째로 조판한다.
            W(f'<div class="sec-lede">{blocks(st["lede"], xref)}</div>')
        for term, raw in st['cards']:
            tid = ids[term]
            meta, lede, f = card_parts(raw)
            lv = re.search(r'\*\*층위\*\*\s*`([^`]+)`', meta)
            lab = re.search(r'\*\*화면 표기\*\*\s*`([^`]+)`', meta)
            no = int(tid[1:])
            key = ' '.join([term, flat(term), lede[:120], (f.get('변수') or '')[:160],
                            (f.get('화면') or '')[:120]]).lower()
            W(f'<article class="term" id="{tid}" data-k="{H.escape(key, quote=True)}">')
            W('<div class="term-head">'
              f'<span class="term-no">{no:02d}</span>'
              f'<h3 data-field="term">{subs(H.escape(term))}</h3>'
              + (f'<span class="chip screenlab">화면 표기 {H.escape(lab.group(1))}</span>' if lab else '')
              + (f'<span class="chip lv{" ui" if lv and lv.group(1) == "화면 용어" else ""}">'
                 f'{H.escape(lv.group(1))}</span>' if lv else '')
              + '</div>')
            if lede:
                ll = lede.split('\n')
                W(f'<p class="lede-line">{inline(ll[0], xref, tid)}</p>')
                rest = '\n'.join(ll[1:]).strip()
                if rest:
                    W(blocks(rest, xref, tid))

            def fld(n, name, ko, body, fid):
                W(f'<div class="fld" data-field="{fid}">'
                  f'<div class="fh"><span class="n">{n}</span>{name}<span class="ko">{ko}</span></div>')
                W(body)
                W('</div>')

            fld(2, '변수', '대표 정의 원문 기호', blocks(f.get('변수', ''), xref, tid), 'var')
            fld(3, '계산식', '원문 산식 · 기호 풀이 · 숫자 예시', blocks(f.get('계산식', ''), xref, tid), 'calc')
            sc = f.get('화면', '')
            m = re.search(r'\[\[shot:\s*([^|]+)\|\s*anchor:\s*([^|]+)\|\s*kind:\s*([^\]]+)\]\]', sc)
            assert m, f'{term} — 화면 지시 없음'
            fig = shot_html(m.group(1).strip(), m.group(2).strip(), m.group(3).strip(), term)
            rest = blocks(sc[:m.start()] + sc[m.end():], xref, tid)
            fld(4, '화면', '눌러서 확대', fig + rest, 'screen')
            fld(5, '관련 용어', '재료 · 쓰이는 곳', blocks(f.get('관련 용어', ''), xref, tid), 'rel')

            W('</article>')
        W('</section>')
    W('<p class="nores hidden" id="nores">찾는 용어가 없다. 다른 낱말로 다시 찾아본다.</p>')

    for i, a in enumerate(doc['apx']):
        W(f'<section class="sec" id="apx{i}"><h2>{H.escape(a["t"])}</h2>')
        W(blocks(a['body'], xref))
        W('</section>')
    W('</main>')
    O.append(FOOT % {'js': JS})

    out = '\n'.join(O)
    ticks = _visible_backticks(out)
    if ticks:
        raise SystemExit('!! 백틱이 화면 글자로 샌다 %d건 — 인라인 파서가 못 잡은 자리다\n   %s'
                         % (len(ticks), '\n   '.join(ticks[:5])))
    open(OUT, 'w', encoding='utf-8').write(out)
    nf = {k: out.count(f'data-field="{k}"') for k in FIELDS}
    print(f'생성 {OUT}  {len(out.encode()):,}B')
    print('카드', out.count('<article class="term"'), '/ 필드', nf)
    print('이미지 참조', len(re.findall(r'assets/shots/', out)))


if __name__ == '__main__':
    main()
