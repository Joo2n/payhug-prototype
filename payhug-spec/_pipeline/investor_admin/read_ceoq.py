#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""대표님 확인 20문 화면에서 답을 꺼낸다.

사용자가 답을 적고 저장하면 그 답이 페이지 원고에 담겨 새 판으로 게시된다.
Claude 가 그 판을 내려받아 이 스크립트로 답만 뽑는다.

  python3 read_ceoq.py <내려받은.html>            답 있는 것만
  python3 read_ceoq.py <내려받은.html> --all      전건
  python3 read_ceoq.py <내려받은.html> --json     원고 그대로

경로를 안 주면 로컬 산출물(payhug-investor-admin/ceo-questions.html)을 본다.
"""

import io
import json
import os
import re
import sys

DEF = "/Users/semi/cursor/payhug-investor-admin/ceo-questions.html"


def seed_of(path):
    html = io.open(path, encoding="utf-8").read()
    m = re.search(r'id="seed">(.*?)</script>', html, re.S)
    if not m:
        sys.exit("원고 블록을 못 찾았다 — %s" % path)
    return json.loads(m.group(1).replace("<\\/", "</"))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    path = args[0] if args else DEF
    if not os.path.exists(path):
        sys.exit("파일 없음 — %s" % path)

    sd = seed_of(path)
    if "--json" in flags:
        print(json.dumps(sd, ensure_ascii=False, indent=2))
        return

    items = sd["items"]
    got = [i for i in items if (i.get("answer") or "").strip()]
    asked = [i for i in items if i.get("done")]
    print("%s — %s" % (sd["title"], sd["when"]))
    print("답 %d / %d · 물었음 표시 %d\n" % (len(got), len(items), len(asked)))
    if (sd.get("note") or "").strip():
        print("[미팅 메모]\n%s\n" % sd["note"].strip())

    show = items if "--all" in flags else got
    if not show:
        print("적힌 답이 아직 없다.")
        return
    for it in show:
        a = (it.get("answer") or "").strip()
        print("── %s %s%s" % (it["id"], it["topic"], "  (물었음)" if it.get("done") else ""))
        print("   물음: %s" % it["say"][:120])
        print("   답  : %s\n" % (a if a else "(아직 없음)"))


if __name__ == "__main__":
    main()
