#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""아래첨자 조판 한 곳.

원고는 마크다운 규약으로 쓴다.

    A_i · D_i · 순지급액_i          낱개
    A_d · D_d · MR_d                하루
    A_{d,i} · D_{p,i}               하루·기간 안의 낱개
    Y_r · Y_d · PY_a · PY_t

화면은 <sub>, 워드는 subscript run 으로 낸다. 하이픈은 빼기표 −(U+2212),
쉼표 뒤에는 가는 공백. 평문(엑셀 열머리·코드·검색키)은 괄호 표기로 돌린다.

기호 정본 — dm_0901/symbol_rule_0901.md
build_glossary.py 의 SUBRE·subs() 와 같은 규칙이고, 기호 범위만 정본에 맞춰 넓혔다.
"""
import re

# 아래첨자를 다는 기호 — 정본 「기호 전건」과 「갈아 끼우는 표」에 있는 것만 둔다.
BASES = (
    # 정본
    'wPY', 'PY', 'Y', 'wD', 'MR', 'EC', 'A', 'B', 'D', 'L', 'M', 'w',
    # 옛 표기 — 정본 「갈아 끼우는 표」 왼쪽 칸
    'SMR', 'SA', 'SB', 'SD', 'SL', 'SM',
)

_LATIN = '|'.join(sorted(BASES, key=len, reverse=True))

# 한글 이름도 낱개에 i 가 붙는다 — 순지급액_i · 미지급금_i · 채권매입수수료_i
SUBRE = re.compile(
    r'(?<![0-9A-Za-z_])(%s|[가-힣]{2,12})_(?:\{([^{}]{1,24})\}|([iradt]))(?![0-9A-Za-z_])'
    % _LATIN)


def _body(m):
    return m.group(2) if m.group(2) is not None else m.group(3)


def subs(t):
    """이미 이스케이프된 HTML 조각에 <sub> 를 넣는다."""
    def one(m):
        b = _body(m).replace('-', '−').replace(',', ',&thinsp;')
        return '%s<sub>%s</sub>' % (m.group(1), b)
    return SUBRE.sub(one, t)


def flat(t):
    """평문 — 태그를 못 넣는 자리(검색키·alt·엑셀 열머리). 괄호 표기로 돌린다."""
    def one(m):
        b = _body(m)
        if m.group(3) is not None:
            return m.group(1) + b
        return '%s(%s)' % (m.group(1), b.replace('−', '-'))
    return SUBRE.sub(one, t)


def runs(t):
    """워드용 — [(글자, 아래첨자인가), …] 로 쪼갠다."""
    out, i = [], 0
    for m in SUBRE.finditer(t):
        if m.start() > i:
            out.append((t[i:m.start()], False))
        out.append((m.group(1), False))
        out.append((_body(m).replace('-', '−').replace(',', ', '), True))
        i = m.end()
    if i < len(t):
        out.append((t[i:], False))
    return out or [(t, False)]


def count(t):
    """조판 대상이 몇 자리인가."""
    return len(SUBRE.findall(t))
