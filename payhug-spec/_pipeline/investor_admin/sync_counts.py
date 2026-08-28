# -*- coding: utf-8 -*-
"""손으로 쓰는 문서의 개수 표기를 counts.py 실측으로 덮는다.

생성기가 있는 산출물(index.html · app.html · archive.html)은 counts.py 를 직접 import 해
쓰므로 여기 대상이 아니다. 생성기 없이 손으로 유지하는 문서만 여기서 맞춘다.

    python3 sync_counts.py            덮어쓰기 + 결과 출력
    python3 sync_counts.py --check    맞는지만 본다 (틀리면 종료코드 1)

대상 문구는 앵커를 통째로 적어 둔다. 문서 표현이 바뀌면 여기서 걸리고, 그때 앵커를 고친다.
"""
import io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import counts

REPO = '/Users/semi/cursor/payhug-investor-admin'
C = dict(counts.C)
# 구현 가능성 문서가 세는 화면 = 낱장 화면 + 랜딩 갤러리 1. 용어 50 · 기능 35 는 판정 건수라
# 실측 대상이 아니지만, 합계는 실측이 움직이면 같이 움직여야 하므로 여기서 더한다.
C['feasScreens'] = C['screenFiles'] + 1
C['feasTotal'] = 50 + C['feasScreens'] + C['states'] + 35 + C['xlsx']

#  (파일, 정규식, 실측을 끼운 치환문)  — 정규식은 반드시 1건만 잡혀야 한다
RULES = [
 (REPO + '/review.html',
  r'const CNT = \{menus:\d+, screens:\d+, states:\d+, xlsx:\d+\};',
  'const CNT = {{menus:{menus}, screens:{screens}, states:{states}, xlsx:{xlsx}}};'),

 (REPO + '/capability.html',
  r'<td>엑셀 \d+종 \+ 투자자산 증명서\(전자서명값 표시\)',
  '<td>엑셀 {xlsx}종 + 투자자산 증명서(전자서명값 표시)'),
 (REPO + '/capability.html',
  r'<div class="expo-item">엑셀 산출물 \d+종</div>',
  '<div class="expo-item">엑셀 산출물 {xlsx}종</div>'),
 (REPO + '/capability.html',
  r'<div class="gi-what">산출물 \d+종의 존재는',
  '<div class="gi-what">산출물 {xlsx}종의 존재는'),
 (REPO + '/capability.html',
  r'<code>Ty수익율</code>, 엑셀 \d+종, 증명서 본문이',
  '<code>Ty수익율</code>, 엑셀 {xlsx}종, 증명서 본문이'),
 (REPO + '/capability.html',
  r'화면 블록 막대는 엑셀 미리보기 \d+종을',
  '화면 블록 막대는 엑셀 미리보기 {xlsPreview}종을'),

 (REPO + '/feasibility.html',
  r'<div class="note-band">엑셀 \d+종의 <code>※</code>',
  '<div class="note-band">엑셀 {xlsx}종의 <code>※</code>'),
 (REPO + '/feasibility.html',
  r'<span class="qtx">엑셀 \d+종을 서버에서 생성합니까',
  '<span class="qtx">엑셀 {xlsx}종을 서버에서 생성합니까'),
 (REPO + '/feasibility.html',
  r'<td class="k">엑셀 파일을 내려받는다 \(미리보기 \d+종\)</td>',
  '<td class="k">엑셀 파일을 내려받는다 (미리보기 {xlsPreview}종)</td>'),

 (HERE + '/capability_manuscript.md',
  r'\| 엑셀 \d+종 \+ 투자자산 증명서',
  '| 엑셀 {xlsx}종 + 투자자산 증명서'),
 (HERE + '/capability_manuscript.md',
  r'\| 엑셀 산출물 \d+종 \|',
  '| 엑셀 산출물 {xlsx}종 |'),
 (HERE + '/capability_manuscript.md',
  r'\| 산출물 \d+종의 존재는',
  '| 산출물 {xlsx}종의 존재는'),
 (HERE + '/capability_manuscript.md',
  r'`Ty수익율`, 엑셀 \d+종, 증명서 본문이',
  '`Ty수익율`, 엑셀 {xlsx}종, 증명서 본문이'),
 (HERE + '/capability_manuscript.md',
  r'엑셀 미리보기 \d+종을 1건으로 계산',
  '엑셀 미리보기 {xlsPreview}종을 1건으로 계산'),

 (HERE + '/feasibility.md',
  r'엑셀 \d+종의 `※` 주석',
  '엑셀 {xlsx}종의 `※` 주석'),
 (HERE + '/feasibility.md',
  r'엑셀 \d+종을 서버에서 생성합니까',
  '엑셀 {xlsx}종을 서버에서 생성합니까'),
 (HERE + '/feasibility.md',
  r'\| 엑셀 파일을 내려받는다\(미리보기 \d+종\)',
  '| 엑셀 파일을 내려받는다(미리보기 {xlsPreview}종)'),

 (HERE + '/glossary_manuscript.md',
  r'\| `가맹점별 투자자산 증명서` · 엑셀 \d+종 \|',
  '| `가맹점별 투자자산 증명서` · 엑셀 {xlsx}종 |'),

 # 산출물 묶음 개수 — 낱장 화면 + 상태 + assets 공용 부품
 (REPO + '/capability.html',
  r'화면 설계\(안\) \d+개 HTML\(화면 \d+ \+ 상태 변형 \d+ \+ 공용 부품 \d+\)',
  '화면 설계(안) {kitHtml}개 HTML(화면 {screenFiles} + 상태 변형 {states} + 공용 부품 {assetParts})'),
 (HERE + '/capability_manuscript.md',
  r'\| HTML 파일 \| \d+ \(화면 \d+ \+ 상태 변형 \d+ \+ 공용 부품 \d+\) \|',
  '| HTML 파일 | {kitHtml} (화면 {screenFiles} + 상태 변형 {states} + 공용 부품 {assetParts}) |'),
 (HERE + '/capability_manuscript.md',
  r'\| 상태 변형 \| \d+ \(레포 상태 파일 \d+ 중',
  '| 상태 변형 | {states} (레포 상태 파일 {statesAll} 중'),

 # 구현 가능성 판정 대상 — 화면(낱장 + 랜딩) · 상태 · 합계
 (REPO + '/feasibility.html',
  r'용어 50 · 화면 \d+ · 상태 \d+ · 기능 35 · 산출물 \d+ — 총 \d+건',
  '용어 50 · 화면 {feasScreens} · 상태 {states} · 기능 35 · 산출물 {xlsx} — 총 {feasTotal}건'),
 (HERE + '/feasibility.md',
  r'판정 대상 \*\*\d+건\*\* — 용어 50 · 화면 \d+ · 상태 \d+ · 기능 35 · 산출물 \d+\.',
  '판정 대상 **{feasTotal}건** — 용어 50 · 화면 {feasScreens} · 상태 {states} · 기능 35 · 산출물 {xlsx}.'),
 (HERE + '/feasibility.md',
  r'\| 등급 \| 뜻 \| 용어 50 \| 화면 \d+ \| 상태 \d+ \| 기능 35 \| 산출물 \d+ \| \*\*합계 \d+\*\* \|',
  '| 등급 | 뜻 | 용어 50 | 화면 {feasScreens} | 상태 {states} | 기능 35 | 산출물 {xlsx} | **합계 {feasTotal}** |'),
 (HERE + '/feasibility.md',
  r'## 6\. 화면 \d+ \+ 상태 \d+ 판정',
  '## 6. 화면 {feasScreens} + 상태 {states} 판정'),
 (HERE + '/feasibility.md', r'### 6-1\. 화면 \d+', '### 6-1. 화면 {feasScreens}'),
 (HERE + '/feasibility.md', r'### 6-2\. 상태 \d+', '### 6-2. 상태 {states}'),
 (REPO + '/feasibility.html',
  r'<h2>판정 전량 \d+건</h2>', '<h2>판정 전량 {feasTotal}건</h2>'),
 (REPO + '/feasibility.html',
  r'<div class="tb-count" id="cnt"><b>\d+</b> / \d+건</div>',
  '<div class="tb-count" id="cnt"><b>{feasTotal}</b> / {feasTotal}건</div>'),
 (REPO + '/feasibility.html',
  r'<div class="sub-head">5-2\. 화면 <span class="cnt">\d+건</span></div>',
  '<div class="sub-head">5-2. 화면 <span class="cnt">{feasScreens}건</span></div>'),
 (REPO + '/feasibility.html',
  r'<div class="sub-head">5-3\. 상태 변형 <span class="cnt">\d+건 · 실측 파일 기준</span></div>',
  '<div class="sub-head">5-3. 상태 변형 <span class="cnt">{states}건 · 실측 파일 기준</span></div>'),
 (REPO + '/feasibility.html',
  r'<div class="bar-name">전체<span class="bn-sub">\d+건</span></div>',
  '<div class="bar-name">전체<span class="bn-sub">{feasTotal}건</span></div>'),
 (REPO + '/feasibility.html',
  r'<div class="bar-name">화면<span class="bn-sub">\d+건</span></div>',
  '<div class="bar-name">화면<span class="bn-sub">{feasScreens}건</span></div>'),
 (REPO + '/feasibility.html',
  r'<div class="bar-name">상태<span class="bn-sub">\d+건</span></div>',
  '<div class="bar-name">상태<span class="bn-sub">{states}건</span></div>'),
]


def run(check=False):
    bad, hit = [], 0
    for path, pat, tmpl in RULES:
        s = io.open(path, encoding='utf-8').read()
        m = re.findall(pat, s)
        if len(m) != 1:
            bad.append('%s — 앵커 %d건: %s' % (os.path.basename(path), len(m), pat))
            continue
        want = tmpl.format(**C)
        if m[0] == want:
            continue
        hit += 1
        if check:
            bad.append('%s — %r → %r' % (os.path.basename(path), m[0], want))
        else:
            io.open(path, 'w', encoding='utf-8').write(re.sub(pat, want.replace('\\', '\\\\'), s))
            print('  %-26s %s' % (os.path.basename(path), want))
    return bad, hit


def readme(check):
    """README.md 는 앵커 치환이 아니라 통째 생성이다 — build_readme.py 를 그대로 태운다."""
    import build_readme
    md = build_readme.build()
    cur = io.open(build_readme.OUT, encoding='utf-8').read()
    if cur == md:
        return []
    if check:
        return ['README.md — 실측과 다르다 (build_readme.py 로 다시 쓴다)']
    io.open(build_readme.OUT, 'w', encoding='utf-8').write(md)
    print('  %-26s 실측으로 재생성' % 'README.md')
    return []


if __name__ == '__main__':
    chk = '--check' in sys.argv
    bad, hit = run(chk)
    bad += readme(chk)
    print('메뉴 %d · 화면 %d · 상태 %d · 엑셀 %d · 엑셀 미리보기 %d'
          % (C['menus'], C['screens'], C['states'], C['xlsx'], C['xlsPreview']))
    print('%s %d건 / 규칙 %d건' % ('불일치' if chk else '갱신', hit, len(RULES)))
    for b in bad:
        print('  ! ' + b)
    sys.exit(1 if bad else 0)
