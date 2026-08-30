# -*- coding: utf-8 -*-
"""프레임 판정표 → 실행 op 목록(figma_ops_0828.json).

fig_heights.json 이 갱신될 때마다 다시 돌린다. 판정 근거는 figma_plan_0828.md §2.
쓰기는 하지 않는다. 임포트 담당이 이 JSON 을 읽어 순서대로 실행한다.
"""
import json, os

BASE = os.path.dirname(os.path.abspath(__file__))
MAP = json.load(open(os.path.join(BASE, 'figma_map_investor.json')))
H = json.load(open(os.path.join(BASE, 'fig_heights.json')))

# 판정: replace 교체 · keep 그대로 · hold 보류 · retire 폐기 · new 신규
VERDICT = {n: 'replace' for n in [
    'invest-assets', 'invest-assets--page2', 'invest-assets--download',
    'invest-assets--cert-confirm', 'invest-assets--empty', 'certificate',
    'invest-profit', 'invest-profit--monthly', 'invest-profit--empty',
    'coocon', 'merchants', 'merchants--filtered', 'merchants--empty',
    'acquisition', 'acquisition--confirm', 'acquisition--signing', 'acquisition--done',
    'contracts', 'contracts--all', 'contracts--empty',
    'password', 'password--weak', 'password--error', 'password--done',
    'index', 'login',
    'xls-assets-status', 'xls-assets-merchant', 'xls-profit-status', 'xls-profit-daily',
]}
# 동결 b0717bf — 사이드바 8메뉴화(D-35)와 숫자 전면 교체(D-31)가 전 프레임에 걸린다.
# 폐기 프레임은 VERDICT 가 아니라 매핑표 retired 가 갖는다 — 원본 파일이 없어 대응표에서도 빠지기 때문이다.
HOLD_REASON = {}
NEW = [
    {'file': 'invest-profit--weekly', 'frame_name': '03-c 투자 수익 — 주별', 'x': 3200, 'y': 7839,
     'note': '04-a 폐기로 비는 자리. 투자 수익 계열 행에 붙는다'},
    {'file': 'acquisition--doc', 'frame_name': '06-d 정산채권 양수 — 계약서 내용', 'x': 4800, 'y': 13065,
     'note': '양수 계열 행의 빈 슬롯'},
    {'file': 'invest-sim', 'frame_name': '15 투자 시뮬레이션', 'x': 1600, 'y': 23517,
     'note': '신규 메뉴. 기존 01~14 번호를 건드리지 않으려고 끝번으로 붙인다'},
    {'file': 'invest-sim--result', 'frame_name': '15-a 투자 시뮬레이션 — 실행 결과', 'x': 3200, 'y': 23517,
     'note': '상동'},
]
HOLD_NEW = []
ORPHANS = [
    ('3189:14605', '01 투자 자산', -6797, -4575, 1269),
    ('3189:15019', '02 투자자산 증명서', -6797, -2392, 1306),
    ('3189:15380', '03 투자 수익', -6797, -55, 1257),
    ('3189:15742', '03-a 투자 수익 — 월별', -6797, 1966, 1212),
    ('3189:16095', '05-a 가맹점 — 검색 적용', -6797, 3631, 533),
    ('3189:16281', '06-a 정산채권 양수 — 서명 확인', -6797, 4649, 656),
    ('3189:16460', '07-a 계약기록 — 전체 선택', -6797, 5632, 690),
    ('3189:16726', '08-a 비밀번호 변경 — 규칙 미충족', -6797, 6589, 585),
]

by_file = {f['file'][:-5]: f for f in MAP['frames']}
ops = {'file_key': MAP['file_key'], 'page_node_id': MAP['page_node_id'],
       'capture': {'server': 'http://localhost:8903 (루트 = _fig)',
                   'script': 'figcap_ia.sh <file> <captureId> <vh> [delay]',
                   'viewport_correction_px': 87, 'figmadelay_default': 2500},
       'replace': [], 'keep': [], 'hold': [], 'retire': [], 'new': [], 'hold_new': [],
       'delete_orphans': []}

for name, v in sorted(VERDICT.items()):
    fr = by_file.get(name)
    if fr is None:
        raise SystemExit('매핑표에 없음: %s' % name)
    rec = {'file': name, 'frame_name': fr['frame_name'], 'old_node_id': fr['node_id'],
           'x': fr['x'], 'y': fr['y'], 'old_h': fr['h']}
    if v in ('replace', 'keep', 'hold'):
        if name not in H:
            raise SystemExit('높이 미측정: %s — prep_fig.py heights 먼저' % name)
        rec['vh'] = H[name]['vh']
        rec['delta'] = H[name]['vh'] - fr['h']
    if v == 'hold':
        rec['reason'] = HOLD_REASON.get(name, '')
    ops[v].append(rec)

for n in NEW:
    n = dict(n); n['vh'] = H[n['file']]['vh']; ops['new'].append(n)
# 원본 파일이 폐기된 프레임 — Figma 에서 지운다. `delete_node_id` 가 아직 안 지운 것이다.
for r in MAP['retired']:
    nid = r.get('delete_node_id') or r.get('deleted_node_id')
    ops['retire'].append({'file': r['file'], 'frame_name': r['frame_name'], 'old_node_id': nid,
                          'done': 'deleted_node_id' in r, 'reason': r['reason']})
for n in HOLD_NEW:
    ops['hold_new'].append(dict(n))
for nid, nm, x, y, h in ORPHANS:
    ops['delete_orphans'].append({'node_id': nid, 'frame_name': nm, 'x': x, 'y': y, 'h': h})

json.dump(ops, open(os.path.join(BASE, 'figma_ops_0828.json'), 'w'), ensure_ascii=False, indent=1)

print('교체 %d · 그대로 %d · 보류 %d · 폐기 %d · 신규 %d · 보류신규 %d · 잔여삭제 %d'
      % (len(ops['replace']), len(ops['keep']), len(ops['hold']), len(ops['retire']),
         len(ops['new']), len(ops['hold_new']), len(ops['delete_orphans'])))
print('현행 프레임 대조: %d = 교체+그대로+보류 %d'
      % (len(MAP['frames']), len(ops['replace']) + len(ops['keep']) + len(ops['hold'])))
print()
print('%-32s %-34s %-12s %6s %6s' % ('file', 'frame', 'old node', 'vh', '증감'))
for r in ops['replace']:
    print('%-32s %-34s %-12s %6d %+6d' % (r['file'], r['frame_name'], r['old_node_id'], r['vh'], r['delta']))
for r in ops['new']:
    print('%-32s %-34s %-12s %6d %6s' % (r['file'], r['frame_name'], '—', r['vh'], 'NEW'))
print('\n[보류]')
for r in ops['hold']:
    print('  %-30s %-34s %s' % (r['file'], r['frame_name'], r['reason']))
for r in ops['hold_new']:
    print('  %-30s %-34s %s' % (r['file'], r['frame_name'], r['reason']))
print('\n[폐기] ' + ', '.join('%s %s%s' % (r['old_node_id'], r['frame_name'],
      '' if r['done'] else ' (삭제 대기)') for r in ops['retire']))
print('[그대로] ' + ', '.join('%s %s' % (r['old_node_id'], r['frame_name']) for r in ops['keep']))
