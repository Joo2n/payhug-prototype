#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""용어 문서 마커 50건이 캡처 이미지의 '내용이 있는 자리'를 가리키는지 픽셀로 대조.

배경 — 화면이 바뀌면 shot_rects.json 의 앵커는 여전히 풀리는데(부분일치) 좌표만
어긋나 마커가 빈 여백을 가리키는 사고가 난다. verify_glossary5 는 마커가 화면 안에
있는지(inView)와 크기가 0이 아닌지만 본다. 그래서 이 검사를 따로 둔다.

판정 4종
  A. glossary.html 의 data-mark 백분율 → 실제 webp 픽셀 사각형에 잉크가 있는가
  B. 그 사각형이 shot_rects.json 의 앵커 항목 좌표와 일치하는가 (빌더 경유 왜곡 0)
     캡션 텍스트 대조는 build_glossary.CAP_FIX 를 양쪽에 똑같이 건 뒤 완전일치로 본다.
     캡처가 동결된 자리의 캡션만 현행 화면값으로 앞서 있고, 그 차이는 그 표에만 있다.
  C. 캡처 파일이 shot_rects.json 이 기록한 imgW/imgH 와 같은가 (촬영-측정 동기)
  D. 원고가 거는 화면 = capture_shots.js FILES = shot_rects.json = 실물 webp 인가
     (아무도 안 부르는 캡처가 배포에 실리거나, 원고만 앞서 나가 빌더가 멎는 사고)
"""
import io, json, os, re, sys, html as H
from PIL import Image

PIPE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PIPE)
# 캡션은 이미지 밖 텍스트라 현행 화면값으로 맞춘다(좌표·앵커 text 는 동결).
# 빌더가 쓰는 치환표를 그대로 불러 앵커 text 에도 똑같이 걸고 대조한다 —
# 양쪽에 같은 변환을 걸 뿐이라 대조는 그대로 완전일치다.
from build_glossary import cap_text
REPO = '/Users/semi/cursor/payhug-investor-admin'
GLOSS = os.path.join(REPO, 'glossary.html')
RECT = os.path.join(PIPE, 'shot_rects.json')
MANU = os.path.join(PIPE, 'glossary_manuscript.md')
CAPJS = os.path.join(PIPE, 'capture_shots.js')
SHOTDIR = os.path.join(REPO, 'assets', 'shots')

INK_MIN = 0.004      # 사각형 안 비배경 픽셀 최소 비율 — 글자 한 줄이면 1% 넘는다
PAD = 5              # build_glossary.shot_html 이 앵커에 주는 여백(문서 px)

RECTS = {s['file'][:-5]: s for s in json.load(open(RECT, encoding='utf-8'))['screens']}
doc = open(GLOSS, encoding='utf-8').read()

marks = re.findall(
    r'data-shot="([^"]*)"\s+data-yc="[^"]*"\s+data-mark="([^"]*)"\s+data-kind="([^"]*)"'
    r'\s+data-lab="[^"]*"\s+data-cap="([^"]*)"', doc)

fail, out = 0, []
if len(marks) != 50:
    print(f'FAIL 마커 수 {len(marks)} != 50')
    sys.exit(1)

# ── D. 원고 · 촬영 목록 · 좌표 · 실물 4자 일치
manu = set(re.findall(r'\[\[shot:\s*([^|]+?)\s*\|', io.open(MANU, encoding='utf-8').read()))
capjs = io.open(CAPJS, encoding='utf-8').read()
files = set(re.findall(r"'([A-Za-z0-9._-]+)\.html'",
                       re.search(r'const FILES = \[(.*?)\];', capjs, re.S).group(1)))
rects = set(RECTS)
disk = {f[:-5] for f in os.listdir(SHOTDIR) if f.endswith('.webp')}
for lab, a, b in (('원고 ≠ capture_shots.js FILES', manu, files),
                  ('capture_shots.js FILES ≠ shot_rects.json', files, rects),
                  ('shot_rects.json ≠ assets/shots 실물', rects, disk)):
    if a != b:
        print(f'FAIL {lab}: 앞에만 {sorted(a - b)} · 뒤에만 {sorted(b - a)}')
        fail += 1
orphan = sorted(disk - manu)
if orphan:
    print(f'FAIL 아무 원고도 부르지 않는 캡처 {len(orphan)}장: {orphan}')
    fail += 1

# ── C. 촬영-측정 동기
for name, sc in RECTS.items():
    p = os.path.join(REPO, sc['shot'])
    if not os.path.exists(p):
        print(f'FAIL 캡처 없음 {sc["shot"]}'); fail += 1; continue
    with Image.open(p) as im:
        if (im.width, im.height) != (sc['imgW'], sc['imgH']):
            print(f'FAIL 촬영·측정 불일치 {name}: 파일 {im.width}x{im.height} != json {sc["imgW"]}x{sc["imgH"]}')
            fail += 1

cache = {}
def load(shot):
    if shot not in cache:
        cache[shot] = Image.open(os.path.join(REPO, shot)).convert('L')
    return cache[shot]

for src, mk, kind, cap in marks:
    shot = os.path.basename(src)[:-5]
    sc = RECTS[shot]
    im = load(src)
    L, T, W, Hh = [float(x) for x in mk.split(',')]
    x0 = int(L / 100 * im.width);  y0 = int(T / 100 * im.height)
    x1 = int((L + W) / 100 * im.width); y1 = int((T + Hh) / 100 * im.height)
    x1 = min(max(x1, x0 + 1), im.width); y1 = min(max(y1, y0 + 1), im.height)
    crop = im.crop((x0, y0, x1, y1))
    px = list(crop.getdata())
    ink = sum(1 for v in px if v < 235) / max(1, len(px))

    # ── B. 빌더 왜곡 0 — data-mark 을 문서 좌표로 되돌려 앵커 항목과 맞춰 본다
    dx = L / 100 * sc['docW'] + PAD
    dy = T / 100 * sc['docH'] + PAD
    capt = H.unescape(cap).split(' · ', 1)[-1].rstrip('…')
    # 같은 좌표에 겹친 항목이 여럿이다(감싸는 div + 안쪽 라벨). 크기까지 맞춰 고른다.
    near = [it for it in sc['items']
            if abs(it['x'] - dx) < 1.2 and abs(it['y'] - dy) < 1.2]
    dw = W / 100 * sc['docW'] - PAD * 2
    dh = Hh / 100 * sc['docH'] - PAD * 2
    hit = None
    for it in near:
        if abs(it['w'] - dw) < 1.5 and abs(it['h'] - dh) < 1.5:
            hit = it; break

    bad = []
    if ink < INK_MIN:
        bad.append(f'잉크 {ink*100:.2f}% < {INK_MIN*100:.1f}%')
    if hit is None:
        bad.append(f'앵커 좌표 역산 불일치(후보 {len(near)}건)')
    elif capt and not cap_text(hit['text']).startswith(capt[:20]):
        bad.append(f'캡션≠앵커 텍스트({cap_text(hit["text"])[:20]!r})')
    if bad:
        fail += 1
        print(f'FAIL {shot} [{mk}] {H.unescape(cap)[:44]} <- ' + ', '.join(bad))
    out.append({'shot': shot, 'kind': kind, 'mark': mk, 'ink': round(ink, 4),
                'cap': H.unescape(cap), 'ok': not bad})

json.dump({'marks': out, 'fail': fail}, open(os.path.join(PIPE, 'verify_shotmarks_result.json'), 'w'),
          ensure_ascii=False, indent=1)
print(f'== 마커 픽셀 대조 {len(marks)}건 · 촬영 {len(RECTS)}장 · FAIL {fail} ==')
print('  원고 {}종 = FILES {}종 = 좌표 {}종 = 실물 {}종 · 고아 캡처 {}장'.format(
    len(manu), len(files), len(rects), len(disk), len(disk - manu)))
print('  잉크 최소 {:.2f}% · 최대 {:.2f}%'.format(min(o["ink"] for o in out) * 100,
                                                  max(o["ink"] for o in out) * 100))
sys.exit(1 if fail else 0)
