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


def feas_rows():
    """구현 가능성 문서의 판정 건수를 그 문서의 표에서 직접 센다.

    산출물 판정 건수는 **엑셀 파일 수가 아니다**. 엑셀 판정은 서식 1벌이 1행이라 4행이고,
    집계 단위 3벌(일별·주별·월별)이나 기간 3벌은 같은 서식을 다른 기간으로 낸 것이라 행이 늘지 않는다.
    파일 수(counts.xlsx)에 묶어 두었더니 파일이 6→8로 늘 때 판정 합계가 실재하지 않는 128로 밀렸다.
    """
    s = io.open(os.path.join(REPO, 'feasibility.html'), encoding='utf-8').read()
    out = {}
    for m in re.finditer(r'<tbody id="tb-(\w+)">(.*?)</tbody>', s, re.S):
        out[m.group(1)] = m.group(2).count('<tr data-g=')
    for k in ('term', 'screen', 'state', 'func', 'out'):
        assert out.get(k), '구현 가능성 문서 tb-%s 판정 행 0건' % k
    return out


def cap_counts():
    """화면별 기능 명세(§3)의 판정 건수를 그 문서의 목록·표에서 직접 센다.

    세는 규칙은 문서가 쓰는 표기 규칙 그대로다.
      행위      = `<li><span class="a-no">` 1건, 판정은 li 끝의 뱃지 1개
      데이터 항목 = 표 `<tr><td class="k">` 1건, 이중 판정 행은 앞에 적힌 것이 그 행의 판정
      화면 블록  = `<div class="scr-head">` 1건. 막대는 엑셀 미리보기를 1건으로 환산한 수를 쓴다
    """
    s = io.open(os.path.join(REPO, 'capability.html'), encoding='utf-8').read()
    sec = s[s.index('<span class="sec-no">03</span>'):s.index('<span class="sec-no">04</span>')]
    K = ('fix', 'hyp', 'chk')

    def tally(items, pick):
        n = dict.fromkeys(K, 0)
        for it in items:
            j = re.findall(r'<span class="j j-(\w+)">', it)
            n[pick(j)] += 1
        return n

    acts = re.findall(r'<li><span class="a-no">\d+</span>(.*?)</li>', sec, re.S)
    rows = re.findall(r'<tr><td class="k">(.*?)</tr>', sec, re.S)
    blocks = re.findall(r'<div class="scr-head">.*?<span class="j j-(\w+)">', sec, re.S)
    a, d = tally(acts, lambda j: j[-1]), tally(rows, lambda j: j[0])
    b = {k: blocks.count(k) for k in K + ('na',)}
    dual = sum(1 for r in rows if len(re.findall(r'<span class="j j-\w+">', r)) > 1)
    return dict(acts=len(acts), rows=len(rows), blocks=len(blocks), a=a, d=d, b=b, dual=dual)


_C = cap_counts()
_F = feas_rows()
# 구현 가능성 문서가 세는 화면 = 낱장 화면 + 랜딩 갤러리 1.
C['feasScreens'] = _F['screen']
C['feasStates'] = _F['state']
C['feasTerms'] = _F['term']
C['feasFuncs'] = _F['func']
C['feasOutputs'] = _F['out']
C['feasTotal'] = sum(_F.values())
# 판정 표와 파일 실측이 갈리면 여기서 멈춘다 — 문서가 화면·상태를 빠뜨린 채 개수만 맞추지 못하게.
assert C['feasScreens'] == C['screenFiles'] + 1, \
    '구현 가능성 화면 판정 %d건 ≠ 낱장 화면 %d + 랜딩 1' % (C['feasScreens'], C['screenFiles'])
assert C['feasStates'] == C['states'], \
    '구현 가능성 상태 판정 %d건 ≠ 상태 낱장 %d' % (C['feasStates'], C['states'])


# 화면별 기능 명세 §3 실측 — KPI·막대·집계표가 전부 이 값을 쓴다
C['capBlocks'] = _C['blocks']
C['capProducts'] = _C['blocks'] - 1 - C['xlsPreview']          # 랜딩 1 · 엑셀 미리보기를 뺀 제품 화면
C['capActs'] = _C['acts']
C['capData'] = _C['rows']
C['capDataDual'] = _C['dual']       # 한 행에 판정이 둘 적힌 항목
for _k, _n in (('Fix', 'fix'), ('Hyp', 'hyp'), ('Chk', 'chk')):
    C['capAct' + _k] = _C['a'][_n]
    C['capData' + _k] = _C['d'][_n]
    C['capBlock' + _k] = _C['b'][_n]
C['capBlockNa'] = _C['b']['na']
# 막대는 엑셀 미리보기 4종을 1건으로 환산해 그린다 — 서식이 같은 화면이라 4칸을 따로 세지 않는다.
C['capBlocksRolled'] = _C['blocks'] - C['xlsPreview'] + 1
C['capBlockHypRolled'] = _C['b']['hyp'] - C['xlsPreview'] + 1
assert C['capBlocks'] == C['screenFiles'] + 1, \
    '화면 블록 %d ≠ 낱장 화면 %d + 랜딩 1' % (C['capBlocks'], C['screenFiles'])


def _widths(ns):
    """막대 폭 — 소수1자리 반올림 후 잔차를 가장 큰 칸이 흡수해 합이 정확히 100.0."""
    t = sum(ns)
    w = [round(n * 1000.0 / t) / 10.0 for n in ns]
    w[ns.index(max(ns))] += round(100.0 - sum(w), 1)
    return ['%.1f' % x for x in w]


for _p, _ws in (('capAct', _widths([_C['a'][k] for k in ('fix', 'hyp', 'chk')])),
                ('capData', _widths([_C['d'][k] for k in ('fix', 'hyp', 'chk')]))):
    for _s, _v in zip(('FixW', 'HypW', 'ChkW'), _ws):
        C[_p + _s] = _v
_bw = _widths([C['capBlockHypRolled'], C['capBlockChk'], C['capBlockNa']])
C['capBlockHypW'], C['capBlockChkW'], C['capBlockNaW'] = _bw

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

 # 화면별 기능 명세 §3 — KPI·막대·집계표는 문서 자신을 세서 채운다
 (REPO + '/capability.html',
  r'을 화면 블록 \d+개로 묶어 대조한 결과\.',
  '을 화면 블록 {capBlocks}개로 묶어 대조한 결과.'),
 (REPO + '/capability.html',
  r'화면 \d+개 = 제품 화면 \d+ \+ 랜딩 1 \+ 엑셀 산출물 미리보기 \d+\.',
  '화면 {capBlocks}개 = 제품 화면 {capProducts} + 랜딩 1 + 엑셀 산출물 미리보기 {xlsPreview}.'),
 (REPO + '/capability.html',
  r'<div class="kpi-label">화면 블록</div>\s*<div class="kpi-value">\d+<span class="u">개</span>',
  '<div class="kpi-label">화면 블록</div>\n        '
  '<div class="kpi-value">{capBlocks}<span class="u">개</span>'),
 (REPO + '/capability.html',
  r'<div class="kpi-label">투자자 행위</div>\s*<div class="kpi-value">\d+<span class="u">건</span>',
  '<div class="kpi-label">투자자 행위</div>\n        '
  '<div class="kpi-value">{capActs}<span class="u">건</span>'),
 (REPO + '/capability.html',
  r'<div class="kpi-label">데이터 항목</div>\s*<div class="kpi-value">\d+<span class="u">항목</span>',
  '<div class="kpi-label">데이터 항목</div>\n        '
  '<div class="kpi-value">{capData}<span class="u">항목</span>'),
 (REPO + '/capability.html',
  r'<div class="bar-name">투자자 행위<span class="bn-sub">\d+건</span></div>\s*<div class="bar">\s*'
  r'<div class="seg seg-fix" style="width:[\d.]+%"><span>확정 \d+</span></div>\s*'
  r'<div class="seg seg-hyp" style="width:[\d.]+%"><span>가설 \d+</span></div>\s*'
  r'<div class="seg seg-chk" style="width:[\d.]+%"><span>확인필요 \d+</span></div>',
  '<div class="bar-name">투자자 행위<span class="bn-sub">{capActs}건</span></div>\n'
  '          <div class="bar">\n'
  '            <div class="seg seg-fix" style="width:{capActFixW}%"><span>확정 {capActFix}</span></div>\n'
  '            <div class="seg seg-hyp" style="width:{capActHypW}%"><span>가설 {capActHyp}</span></div>\n'
  '            <div class="seg seg-chk" style="width:{capActChkW}%"><span>확인필요 {capActChk}</span></div>'),
 (REPO + '/capability.html',
  r'<div class="bar-name">데이터 항목<span class="bn-sub">\d+항목</span></div>\s*<div class="bar">\s*'
  r'<div class="seg seg-fix" style="width:[\d.]+%"><span>확정 \d+</span></div>\s*'
  r'<div class="seg seg-hyp" style="width:[\d.]+%"><span>가설 \d+</span></div>\s*'
  r'<div class="seg seg-chk" style="width:[\d.]+%"><span>확인필요 \d+</span></div>',
  '<div class="bar-name">데이터 항목<span class="bn-sub">{capData}항목</span></div>\n'
  '          <div class="bar">\n'
  '            <div class="seg seg-fix" style="width:{capDataFixW}%"><span>확정 {capDataFix}</span></div>\n'
  '            <div class="seg seg-hyp" style="width:{capDataHypW}%"><span>가설 {capDataHyp}</span></div>\n'
  '            <div class="seg seg-chk" style="width:{capDataChkW}%"><span>확인필요 {capDataChk}</span></div>'),
 (REPO + '/capability.html',
  r'<div class="bar-name">화면 블록<span class="bn-sub">\d+건 환산</span></div>\s*<div class="bar">\s*'
  r'<div class="seg seg-hyp" style="width:[\d.]+%"><span>가설 \d+</span></div>\s*'
  r'<div class="seg seg-chk" style="width:[\d.]+%"><span>확인필요 \d+</span></div>\s*'
  r'<div class="seg seg-na" style="width:[\d.]+%"><span>\d+</span></div>',
  '<div class="bar-name">화면 블록<span class="bn-sub">{capBlocksRolled}건 환산</span></div>\n'
  '          <div class="bar">\n'
  '            <div class="seg seg-hyp" style="width:{capBlockHypW}%"><span>가설 {capBlockHypRolled}</span></div>\n'
  '            <div class="seg seg-chk" style="width:{capBlockChkW}%"><span>확인필요 {capBlockChk}</span></div>\n'
  '            <div class="seg seg-na" style="width:{capBlockNaW}%"><span>{capBlockNa}</span></div>'),
 (REPO + '/capability.html',
  r'화면 블록 막대는 엑셀 미리보기 \d+종을 1건으로 환산한 \d+건 기준\. '
  r'확정 판정을 받은 화면 블록은 \d+건',
  '화면 블록 막대는 엑셀 미리보기 {xlsPreview}종을 1건으로 환산한 {capBlocksRolled}건 기준. '
  '확정 판정을 받은 화면 블록은 {capBlockFix}건'),
 (REPO + '/capability.html',
  r'데이터 항목 <span class="j j-fix">확정</span> \d+건 가운데 \d+건은',
  '데이터 항목 <span class="j j-fix">확정</span> {capDataFix}건 가운데 {capDataDual}건은'),

 (HERE + '/capability_manuscript.md',
  r'\| 화면 블록 \| \d+ \(제품 화면 \d+ · 랜딩 1 · 엑셀 미리보기 \d+\) \|',
  '| 화면 블록 | {capBlocks} (제품 화면 {capProducts} · 랜딩 1 · 엑셀 미리보기 {xlsPreview}) |'),
 (HERE + '/capability_manuscript.md',
  r'\| 투자자 행위 \| \d+ \|', '| 투자자 행위 | {capActs} |'),
 (HERE + '/capability_manuscript.md',
  r'\| 행위 판정 — `확정` \| \d+ \|', '| 행위 판정 — `확정` | {capActFix} |'),
 (HERE + '/capability_manuscript.md',
  r'\| 행위 판정 — `가설` \| \d+ \|', '| 행위 판정 — `가설` | {capActHyp} |'),
 (HERE + '/capability_manuscript.md',
  r'\| 행위 판정 — `확인필요` \| \d+ \|', '| 행위 판정 — `확인필요` | {capActChk} |'),
 (HERE + '/capability_manuscript.md',
  r'\| 데이터 항목 \| \d+ \|', '| 데이터 항목 | {capData} |'),
 (HERE + '/capability_manuscript.md',
  r'\| 데이터 항목 판정 — `확정` \| \d+ \|', '| 데이터 항목 판정 — `확정` | {capDataFix} |'),
 (HERE + '/capability_manuscript.md',
  r'\| 데이터 항목 판정 — `가설` \| \d+ \|', '| 데이터 항목 판정 — `가설` | {capDataHyp} |'),
 (HERE + '/capability_manuscript.md',
  r'\| 데이터 항목 판정 — `확인필요` \| \d+ \|', '| 데이터 항목 판정 — `확인필요` | {capDataChk} |'),
 (HERE + '/capability_manuscript.md',
  r'데이터 항목의 `확정` \d+건 가운데 \d+건은',
  '데이터 항목의 `확정` {capDataFix}건 가운데 {capDataDual}건은'),
 (HERE + '/capability_manuscript.md',
  r'화면 블록 단위 판정은 `확정` \d+ · `가설` \d+\(', '화면 블록 단위 판정은 `확정` {capBlockFix} · `가설` {capBlockHypRolled}('),

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
  r'용어 \d+ · 화면 \d+ · 상태 \d+ · 기능 \d+ · 산출물 \d+ — 총 \d+건',
  '용어 {feasTerms} · 화면 {feasScreens} · 상태 {feasStates} · 기능 {feasFuncs} · 산출물 {feasOutputs} — 총 {feasTotal}건'),
 (HERE + '/feasibility.md',
  r'판정 대상 \*\*\d+건\*\* — 용어 \d+ · 화면 \d+ · 상태 \d+ · 기능 \d+ · 산출물 \d+\.',
  '판정 대상 **{feasTotal}건** — 용어 {feasTerms} · 화면 {feasScreens} · 상태 {feasStates} · 기능 {feasFuncs} · 산출물 {feasOutputs}.'),
 (HERE + '/feasibility.md',
  r'\| 등급 \| 뜻 \| 용어 \d+ \| 화면 \d+ \| 상태 \d+ \| 기능 \d+ \| 산출물 \d+ \| \*\*합계 \d+\*\* \|',
  '| 등급 | 뜻 | 용어 {feasTerms} | 화면 {feasScreens} | 상태 {feasStates} | 기능 {feasFuncs} | 산출물 {feasOutputs} | **합계 {feasTotal}** |'),
 (HERE + '/feasibility.md',
  r'## 6\. 화면 \d+ \+ 상태 \d+ 판정',
  '## 6. 화면 {feasScreens} + 상태 {feasStates} 판정'),
 (HERE + '/feasibility.md', r'### 6-1\. 화면 \d+', '### 6-1. 화면 {feasScreens}'),
 (HERE + '/feasibility.md', r'### 6-2\. 상태 \d+', '### 6-2. 상태 {feasStates}'),
 (HERE + '/feasibility.md', r'## 5\. 용어 \d+건 판정', '## 5. 용어 {feasTerms}건 판정'),
 (HERE + '/feasibility.md', r'## 7\. 기능 \d+건 판정', '## 7. 기능 {feasFuncs}건 판정'),
 (HERE + '/feasibility.md',
  r'## 8\. 산출물 \d+건 판정 — 실제로 발급되나',
  '## 8. 산출물 {feasOutputs}건 판정 — 실제로 발급되나'),
 (REPO + '/feasibility.html',
  r'<div class="sub-head">5-5\. 산출물 — 실제로 발급되나 <span class="cnt">\d+건</span></div>',
  '<div class="sub-head">5-5. 산출물 — 실제로 발급되나 <span class="cnt">{feasOutputs}건</span></div>'),
 (REPO + '/feasibility.html',
  r'<div class="bar-name">산출물<span class="bn-sub">\d+건</span></div>',
  '<div class="bar-name">산출물<span class="bn-sub">{feasOutputs}건</span></div>'),
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
  '<div class="sub-head">5-3. 상태 변형 <span class="cnt">{feasStates}건 · 실측 파일 기준</span></div>'),
 (REPO + '/feasibility.html',
  r'<div class="bar-name">전체<span class="bn-sub">\d+건</span></div>',
  '<div class="bar-name">전체<span class="bn-sub">{feasTotal}건</span></div>'),
 (REPO + '/feasibility.html',
  r'<div class="bar-name">화면<span class="bn-sub">\d+건</span></div>',
  '<div class="bar-name">화면<span class="bn-sub">{feasScreens}건</span></div>'),
 (REPO + '/feasibility.html',
  r'<div class="bar-name">상태<span class="bn-sub">\d+건</span></div>',
  '<div class="bar-name">상태<span class="bn-sub">{feasStates}건</span></div>'),
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
