#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""편집판 HTML 을 원고 꼴로 되읽는다.

대상   ~/Downloads/payhug_용어정의서/용어기호정리_편집판_*.html  (build_finaledit.py 가 낸 것)
       또는 그 페이지에서 저장해 내려받은 HTML
견줌   final_terms.json

원고에 쓰지 않는다. 차이 목록만 낸다. 기획자가 그 목록을 보고 「반영해」 하면
그때 원고에 쓴다.

  python3 read_finaledit.py                     최신 편집판을 찾아 차이만 낸다
  python3 read_finaledit.py <파일.html>         파일을 지정
  python3 read_finaledit.py --out <경로.json>   되읽은 원고를 딴 파일로 뽑는다
  python3 read_finaledit.py --all               고친 것이 없어도 전건을 훑는다

되읽은 문장은 기획자 것이라 손대지 않는다. 다만 두 가지를 알려만 준다.
  · 금지어  dm_0901/banned_words.md
  · 숫자    ledger_facts.json 에 없는 숫자가 고친 칸에 남았는가
"""

import base64
import io
import json
import os
import re
import sys

PIPE = os.path.dirname(os.path.abspath(__file__))
SEED_PATH = os.path.join(PIPE, "final_terms.json")
FACTS_PATH = os.path.join(PIPE, "ledger_facts.json")
BANNED_PATH = os.path.join(PIPE, "dm_0901", "banned_words.md")
OUTDIR = os.path.expanduser("~/Downloads/payhug_용어정의서")
DOWNLOADS = os.path.expanduser("~/Downloads")
STEM = "용어기호정리_편집판"

# 견주는 칸. 기획자가 고칠 수 있게 열어 둔 것과 같다.
VAR_FIELDS = ("term", "sym", "formula", "plain", "alias")
DOC_FIELDS = ("title", "basis")


# ══════════════════════════════════════════════════════════════════
#  편집판에서 원고를 꺼낸다
# ══════════════════════════════════════════════════════════════════

def find_latest(stem=STEM):
    """최신 편집판을 찾는다. 내려받기가 최상위에 떨어질 수도 있어 두 곳을 본다."""
    cand = []
    for d in (OUTDIR, DOWNLOADS):
        if not os.path.isdir(d):
            continue
        for f in os.listdir(d):
            if f.startswith(stem) and f.endswith(".html"):
                p = os.path.join(d, f)
                cand.append((os.path.getmtime(p), p))
    return max(cand)[1] if cand else None


def unpack(doc):
    """페이지가 품고 있는 원고를 꺼낸다."""
    m = re.search(r'id="seed">(.*?)</script>', doc, re.S)
    if not m:
        return None
    return json.loads(m.group(1).replace("<\\/", "</"))


def unpack_src(doc):
    """페이지가 품고 있는 자기 원본. 뼈대가 닳았는지 볼 때 쓴다."""
    m = re.search(r'id="src">"([A-Za-z0-9+/=]+)"</script>', doc)
    return base64.b64decode(m.group(1)).decode("utf-8") if m else None


# ══════════════════════════════════════════════════════════════════
#  알려만 주는 검사 둘
# ══════════════════════════════════════════════════════════════════

def banned_words(path=BANNED_PATH):
    """금지어 목록을 문서에서 읽는다. 검증기 안에 두 번째 목록을 두지 않는다.

    첫 칸의 백틱 토큰만 쓴다. `~자리` 처럼 물결로 시작하는 것과 한 글자 로마자는
    글자 하나로 온 문서를 때리므로 뺀다. 「미확정」은 금지어가 아니다 — 문서가
    그렇게 갈라 적었다.
    """
    if not os.path.exists(path):
        return []
    out, seen, on = [], set(), False
    for line in io.open(path, encoding="utf-8"):
        if line.startswith("## "):
            on = "쓰지 않는 말" in line
            continue
        if not on or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or cells[0].startswith("---"):
            continue
        for tok in re.findall(r"`([^`]+)`", cells[0]):
            tok = tok.strip()
            if not tok or tok.startswith("~") or re.match(r"^[A-Za-z]{1,2}$", tok):
                continue
            if tok in seen or tok == "미확정":
                continue
            seen.add(tok)
            out.append(tok)
    return out


NUMRE = re.compile(r"\d{1,3}(?:,\d{3})+|\d+\.\d+")


def fact_strings(path=FACTS_PATH):
    """원장 원천의 숫자를 화면에 쓰는 꼴로 모은다."""
    if not os.path.exists(path):
        return set()
    out = set()

    def add(v):
        if isinstance(v, bool):
            return
        if isinstance(v, (int, float)):
            out.add("{:,}".format(v))
            out.add(str(v))
            if isinstance(v, int):
                out.add("{:,}".format(v))
        elif isinstance(v, str):
            out.add(v)
            for m in NUMRE.finditer(v):
                out.add(m.group(0))
        elif isinstance(v, dict):
            for x in v.values():
                add(x)
        elif isinstance(v, list):
            for x in v:
                add(x)

    add(json.load(io.open(path, encoding="utf-8")))
    return out


def scan_numbers(text, facts):
    """원장에 없는 숫자를 집는다. 고친 칸만 훑으므로 잡음이 적다."""
    return [m.group(0) for m in NUMRE.finditer(text or "") if m.group(0) not in facts]


# ══════════════════════════════════════════════════════════════════
#  차이 목록
# ══════════════════════════════════════════════════════════════════

def norm(v):
    return "" if v is None else str(v)


def diff(old, new, fields=VAR_FIELDS, prep=None):
    """[(번호, 용어, 칸, 전, 후), …]. prep 는 견주기 전에 옛 값을 다듬는 함수."""
    prep = prep or (lambda s: s)
    out = []
    for k in DOC_FIELDS:
        a, b = prep(norm(old.get(k))), norm(new.get(k))
        if a != b:
            out.append((0, "머리", k, a, b))

    ov, nv = old.get("vars", []), new.get("vars", [])
    n = max(len(ov), len(nv))
    for i in range(n):
        o = ov[i] if i < len(ov) else None
        x = nv[i] if i < len(nv) else None
        if o is None:
            out.append((i + 1, norm(x.get("term")), "항 추가", "", norm(x.get("term"))))
            continue
        if x is None:
            out.append((i + 1, norm(o.get("term")), "항 삭제", norm(o.get("term")), ""))
            continue
        for f in fields:
            a, b = prep(norm(o.get(f))), norm(x.get(f))
            if a != b:
                out.append((i + 1, norm(x.get("term")) or norm(o.get("term")), f, a, b))
    return out


def diff_side(old, new, key, label, subs, prep=None):
    """규칙·범위처럼 vars 밖에 있는 문단."""
    prep = prep or (lambda s: s)
    out = []
    oa, na = old.get(key, []), new.get(key, [])
    for i in range(max(len(oa), len(na))):
        o = oa[i] if i < len(oa) else {}
        x = na[i] if i < len(na) else {}
        for f in subs:
            a, b = prep(norm(o.get(f))), norm(x.get(f))
            if a != b:
                out.append((i + 1, label, f, a, b))
    return out


def show(rows, facts, banned, title):
    if not rows:
        print("%s — 고친 것 없음" % title)
        return 0
    print("%s — %d곳" % (title, len(rows)))
    for no, term, field, a, b in rows:
        print()
        print("[%02d] %s  %s" % (no, term, field))
        print("  전  %s" % (a if a else "(비어 있음)"))
        print("  후  %s" % (b if b else "(비어 있음)"))
        hits = [w for w in banned if w in b]
        if hits:
            print("       금지어  %s" % " · ".join(hits))
        nums = scan_numbers(b, facts)
        if nums:
            print("       원장에 없는 숫자  %s" % " · ".join(sorted(set(nums))))
    return len(rows)


def verifier_risk(rows):
    """기호·산식을 고쳤으면 verify_final_terms.py 가 깨질 수 있다. 그 자리를 세운다."""
    return [r for r in rows if r[2] in ("sym", "formula", "항 추가", "항 삭제")]


# ══════════════════════════════════════════════════════════════════

def main():
    args = [a for a in sys.argv[1:]]
    out_path = None
    if "--out" in args:
        i = args.index("--out")
        out_path = args[i + 1]
        del args[i:i + 2]
    show_all = "--all" in args
    args = [a for a in args if not a.startswith("--")]

    src = args[0] if args else find_latest()
    if not src or not os.path.exists(src):
        sys.exit("편집판을 못 찾음 — %s 아래 %s_*.html" % (OUTDIR, STEM))

    doc = io.open(src, encoding="utf-8").read()
    new = unpack(doc)
    if new is None:
        sys.exit("이 파일에서 원고를 못 꺼냄 — %s" % src)
    old = json.load(io.open(SEED_PATH, encoding="utf-8"))

    print("편집판  %s" % src)
    print("원고    %s" % SEED_PATH)
    print("용어    원고 %d항 → 편집판 %d항"
          % (len(old.get("vars", [])), len(new.get("vars", []))))
    raw = unpack_src(doc)
    print("뼈대    %s" % ("원본 살아 있음" if raw and "%%SRC%%" in raw else "원본 회수 실패"))
    print()

    facts = fact_strings()
    banned = banned_words()

    rows = diff(old, new)
    rows += diff_side(old, new, "rules", "규칙", ("head", "body"))
    rows += diff_side(old, new, "scopes", "범위", ("name", "def"))
    n = show(rows, facts, banned, "차이")

    risk = verifier_risk(rows)
    if risk:
        print()
        print("verify_final_terms.py 가 볼 자리 %d곳" % len(risk))
        for no, term, field, a, b in risk:
            print("  [%02d] %s  %s" % (no, term, field))
        print("  검증기 기준을 이 값으로 옮길지 정해 주면 그때 고친다.")

    if show_all:
        print()
        print("전건 훑기 — 금지어·원장에 없는 숫자")
        for i, v in enumerate(new.get("vars", []), 1):
            for f in VAR_FIELDS:
                t = norm(v.get(f))
                hits = [w for w in banned if w in t]
                nums = scan_numbers(t, facts)
                if hits or nums:
                    print("  [%02d] %s  %s  %s" % (i, norm(v.get("term")), f,
                                                   " · ".join(hits + nums)))

    if out_path:
        io.open(out_path, "w", encoding="utf-8").write(
            json.dumps(new, ensure_ascii=False, indent=1) + "\n")
        print()
        print("되읽은 원고  %s" % out_path)

    return n


if __name__ == "__main__":
    main()
