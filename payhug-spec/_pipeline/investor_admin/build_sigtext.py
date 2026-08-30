#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""계약서 원문 텍스트 — 화면이 여는 실물.

산출 — payhug-investor-admin/assets/docs/
  정산금채권_재양도_합의서.txt        `계약서보기`의 원문 열기 대상

전자서명 결과 파일(전자서명결과_*.txt)은 만들지 않는다.
원문 해시·서명값을 우리가 지어냈고, 결과물 파일 형식이 미결이라(meeting_20260828.md 확인필요 ②)
계약기록의 내려받기를 비활성으로 잠갔다(D-39). 형식이 정해지면 그때 실물 생성기를 다시 붙인다.

계약서 원문은 contract_text.py 한 곳에서 온다. 원본이 바뀌면 그 파일만 갈아 끼운다.
"""

import io
import os
import sys

PIPE = os.path.dirname(os.path.abspath(__file__))
REPO = '/Users/semi/cursor/payhug-investor-admin'
OUT = os.path.join(REPO, 'assets', 'docs')
sys.path.insert(0, PIPE)
import contract_text as C          # noqa: E402

CONTRACT_FILE = '정산금채권_재양도_합의서.txt'
STALE_PREFIX = '전자서명결과_'


def main():
    if not os.path.isdir(OUT):
        os.makedirs(OUT)

    io.open(os.path.join(OUT, CONTRACT_FILE), 'w', encoding='utf-8').write(C.as_text())
    print('%-38s %8d B' % (CONTRACT_FILE, os.path.getsize(os.path.join(OUT, CONTRACT_FILE))))

    # 되살아나지 않게 — 예전 산출물이 남아 있으면 거둔다
    gone = 0
    for f in sorted(os.listdir(OUT)):
        if f.startswith(STALE_PREFIX):
            os.remove(os.path.join(OUT, f))
            gone += 1
    if gone:
        print('구 산출물 %d건 제거 (%s*)' % (gone, STALE_PREFIX))
    print('산출 1건 → %s' % OUT)


if __name__ == '__main__':
    main()
