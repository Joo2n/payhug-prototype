#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""기존 표기 → 바뀐 기호 대조표.

원천은 final_terms.json 의 vars[].alias 한 곳이다. 워드·HTML 생성기가 모두
여기서 읽으므로 표가 여러 벌로 갈리지 않는다.

근거 — dm_0901/symbol_rule_0901.md 「갈아 끼우는 표」 · symbol_glossary.json aliases
"""
import io
import json
import os
import re

PIPE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(PIPE, 'final_terms.json')

HEAD = ('기존 표기', '바뀐 기호', '용어 이름')
TITLE = '기존 표기 → 바뀐 기호'


def rows(path=None):
    """[(기존 표기, 바뀐 기호, 용어 이름), …] — final_terms.json 순서 그대로."""
    d = json.load(io.open(path or SRC, encoding='utf-8'))
    return [(v['alias'], v['sym'], v['term']) for v in d['vars'] if v.get('alias')]


# ── 같은 용어의 범위별 기호 ────────────────────────────────────────
# 표를 손으로 적지 않는다. final_terms.json 의 vars[].sym 을 그 자리에서 갈라
# 세운다. 기호가 늘거나 이름이 바뀌면 표가 따라 바뀐다.
#
# 열머리 「ID가 i인 대상정산금채권」 은 대표 원문 14행 그대로다. 뒤 두 칸은
# 4절 범위 표의 표시(d · P)와 이름을 그대로 단다. BRANCH_COLS 는 화면에
# 안 나오는 내부 키라 그대로 둔다.

BRANCH_HEAD = ('용어', 'ID가 i인 대상정산금채권', '하루 d', '기간 P', '그 밖')
BRANCH_TITLE = '같은 용어의 범위별 기호'
BRANCH_COLS = ('낱건', '하루', '기간', '그 밖')


def split(sym):
    """기호 하나를 (개념 글자, 갈래) 로 가른다. 규칙은 dm_0901 기호 정본과 같다.

      Σ 로 시작   i 를 다 모은 값이라 갈래는 「그 밖」
      _i          낱건
      d−1         하루
      앞머리 P    기간
      나머지      그 밖

    앞머리 `w` 는 가중 표시라 개념 글자가 아니고, 꼬리 `_{MR}` · `_r` 도 뗀다.
    `+` 가 든 합성 기호와 한글 기호는 행으로 세우지 않는다.
    """
    s = sym.strip()
    if '+' in s:
        return None
    agg = s.startswith('Σ')
    s = s.lstrip('Σ').strip()
    m = re.search(r'_\{([^}]*)\}$', s)
    tail, body = (m.group(1), s[:m.start()]) if m else ('', s)
    one = re.search(r'_([A-Za-z])$', body)
    if one:
        tail, body = tail or one.group(1), body[:one.start()]
    body = body.lstrip('w')
    period = body.startswith('P')
    if period:
        body = body[1:].lstrip('w')
    if agg:
        scope = '그 밖'
    elif tail == 'i':
        scope = '낱건'
    elif tail == 'd' or 'd−1' in tail:
        scope = '하루'
    elif period:
        scope = '기간'
    else:
        scope = '그 밖'
    if not re.match(r'^[A-Z]+$', body):
        return None
    return body, scope


def branch_rows(path=None):
    """[(개념, 낱건, 하루, 기간, 그 밖), …] — 값이 없는 칸은 빈 문자열."""
    d = json.load(io.open(path or SRC, encoding='utf-8'))
    order, cell, name, hour = [], {}, {}, {}
    for v in d['vars']:
        if v['kind'] == '상수':
            continue
        got = split(v['sym'])
        if not got:
            continue
        key, scope = got
        if key not in cell:
            order.append(key)
            cell[key] = dict((c, []) for c in BRANCH_COLS)
        if v['kind'] == '개념':
            name[key] = v['term']
            continue
        if scope != '그 밖' and cell[key][scope]:
            scope = '그 밖'                       # 칸이 이미 찼으면 「그 밖」 으로 민다
        tag = v['sym'] + (' (%s)' % v['note'] if v.get('note') else '')
        cell[key][scope].append(tag)
        if scope == '하루':
            hour[key] = v['term']
    # 비율 기호는 갈래 변형이 없으면 제 재료 행의 「그 밖」 으로 든다 — LR 은 L 행에
    for key in list(order):
        c = cell[key]
        if (key.endswith('R') and key[:-1] in cell
                and not c['낱건'] and not c['하루'] and not c['기간']):
            cell[key[:-1]]['그 밖'] += c['그 밖']
            order.remove(key)
            del cell[key]
    out = []
    for key in order:
        label = name.get(key) or (hour.get(key, '').replace('하루 ', '', 1))
        out.append(tuple(['%s  %s' % (key, label)]
                         + [' · '.join(cell[key][c]) for c in BRANCH_COLS]))
    return out
