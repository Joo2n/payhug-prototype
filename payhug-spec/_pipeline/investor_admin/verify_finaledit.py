#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""용어·기호 정리를 고치는 두 길 검사 — HTML 편집판과 워드.

기획자가 고친 말이 그대로 원고로 돌아와야 대표에게 나가는 문서가 기획자 말이 된다.
그 길이 한 군데라도 끊기면 고친 것이 날아가므로 여기서 본다.

  (축1) 편집판이 자기 원본을 품고 세대를 넘겨도 뼈대가 닳지 않는가   build_finaledit.py
  (축2) 조판한 칸을 되읽으면 원고 문자열이 글자까지 돌아오는가        브라우저 실측 + 파이썬 대조
  (축3) 워드에서 되읽은 것이 원고와 같은가                            read_wordedit.py
  (축4) 고친 것을 read_*.py 가 그 자리만 집어내는가                   판별력 자기시험

FAIL 이 하나라도 있으면 종료코드 1. 대상이 0건이어도 FAIL 이다.

  python3 verify_finaledit.py               전건
  FE_NOSCREEN=1 python3 verify_finaledit.py    브라우저 실측 빼고
"""

import base64
import html as htmlmod
import io
import json
import os
import re
import subprocess
import sys
import tempfile
from html.parser import HTMLParser

PIPE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PIPE)

import build_finaledit as be
import read_finaledit as rf
import read_wordedit as rw
import subscript

SEED_PATH = os.path.join(PIPE, "final_terms.json")
FRAG_PATH = be.FRAG_PATH
OUTDIR = be.OUTDIR
PREV = be.PREV
STEM = be.STEM
DOWNLOADS = os.path.expanduser("~/Downloads")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
NOSCREEN = os.environ.get("FE_NOSCREEN") == "1"

R = []


def chk(name, got, want, note=""):
    ok = (got == want)
    R.append((ok, name, got, want, note))
    return ok


def chk_true(name, cond, note=""):
    R.append((bool(cond), name, "예" if cond else "아니오", "예", note))
    return bool(cond)


def load(p):
    return io.open(p, encoding="utf-8").read()


# ══════════════════════════════════════════════════════════════════
#  페이지가 하는 조판·되읽기를 파이썬으로 그대로 흉내 낸다
# ══════════════════════════════════════════════════════════════════

def esc(s):
    return (str("" if s is None else s)
            .replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def codify(s):
    return re.sub(r"`([^`]*)`", r"<code>\1</code>", s)


def fmt(s):
    """build_finaledit 의 fmt() 와 같은 절차 — 이스케이프 · 아래첨자 · 백틱."""
    return codify(subscript.subs(esc(s)))


class Back(HTMLParser):
    """조판된 조각을 원고 표기로 되돌린다. 페이지의 readField() 와 같은 규칙."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.sub = None

    def handle_starttag(self, tag, attrs):
        if tag == "sub":
            self.sub = []
        elif tag == "code":
            self.out.append("`")
        elif tag == "br":
            self.out.append("\n")

    def handle_startendtag(self, tag, attrs):
        if tag == "br":
            self.out.append("\n")

    def handle_endtag(self, tag):
        if tag == "sub" and self.sub is not None:
            b = "".join(self.sub).replace(" ", "")
            self.out.append("_" + b if b in ("i", "r") else "_{" + b + "}")
            self.sub = None
        elif tag == "code":
            self.out.append("`")

    def handle_data(self, d):
        (self.sub if self.sub is not None else self.out).append(d)


def unfmt(s):
    p = Back()
    p.feed(s)
    p.close()
    return "".join(p.out)


def fnv(s):
    """페이지의 fnv() 와 같은 값. JS 는 UTF-16 낱자를 센다."""
    b = s.encode("utf-16-le")
    h = 0x811C9DC5
    for i in range(0, len(b), 2):
        h ^= b[i] | (b[i + 1] << 8)
        h = (h + ((h << 1) + (h << 4) + (h << 7) + (h << 8) + (h << 24))) & 0xFFFFFFFF
    return "%08x" % h


def utf16len(s):
    return len(s.encode("utf-16-le")) // 2


# ══════════════════════════════════════════════════════════════════
#  편집판 되감기
# ══════════════════════════════════════════════════════════════════

def unpack(doc):
    m = re.search(r'id="src">"([A-Za-z0-9+/=]+)"</script>', doc)
    raw = base64.b64decode(m.group(1)).decode("utf-8") if m else None
    s = re.search(r'id="seed">(.*?)</script>', doc, re.S)
    seed = json.loads(s.group(1).replace("<\\/", "</")) if s else None
    return raw, seed


def regen(raw, seed):
    """페이지의 renderDoc() 과 같은 절차로 문서를 다시 만든다."""
    cut = raw.index("%%SRC%%")
    before, after = raw[:cut], raw[cut + 7:]
    f = lambda s: s.replace("%%SEED%%", be.js_json(seed))
    frag = f(before) + base64.b64encode(raw.encode("utf-8")).decode("ascii") + f(after)
    return be.full(frag)


def visible_text(dom):
    """dump-dom 결과에서 눈에 보이는 글자만 남긴다. 원고 JSON 은 script 안이라 뺀다."""
    t = re.sub(r"<script\b[^>]*>.*?</script>", " ", dom, flags=re.S | re.I)
    t = re.sub(r"<style\b[^>]*>.*?</style>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<sub\b[^>]*>(.*?)</sub>", r"_{\1}", t, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    return htmlmod.unescape(t)


def dump_dom(path):
    p = subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
         "--no-first-run", "--disable-extensions", "--virtual-time-budget=8000",
         "--dump-dom", "file://" + path],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=120)
    return p.stdout.decode("utf-8", "replace")


# ══════════════════════════════════════════════════════════════════

def main():
    seed = json.load(io.open(SEED_PATH, encoding="utf-8"))
    banned = rf.banned_words()

    # ── 1. 생성기 · 세대를 넘겨도 뼈대가 닳지 않는가 ─────────
    frag = be.build(seed)
    page = be.full(frag)
    raw1, s1 = unpack(page)
    chk_true("생성기 · 원본 회수", raw1 is not None)
    chk("생성기 · 회수한 원본의 토큰 2종",
        (raw1 or "").count("%%SEED%%") + (raw1 or "").count("%%SRC%%"), 2)
    chk_true("생성기 · 재생산이 원본과 같음", raw1 and regen(raw1, s1) == page)

    s2 = json.loads(json.dumps(seed))
    s2["vars"][2]["plain"] = "기획자가 고친 문장이다."
    s2["vars"].append({"term": "새 용어", "sym": "Z", "alias": None,
                       "kind": "집계", "formula": None, "plain": "새로 넣은 설명이다."})
    g2 = regen(raw1, s2)
    raw2, sd2 = unpack(g2)
    chk_true("2세대 · 뼈대가 닳지 않음", raw2 == raw1)
    chk("2세대 · 항 수", len(sd2["vars"]), len(seed["vars"]) + 1)
    chk("2세대 · 고친 문장 살아 있음", sd2["vars"][2]["plain"], "기획자가 고친 문장이다.")

    s3 = json.loads(json.dumps(sd2))
    del s3["vars"][1]
    raw3, sd3 = unpack(regen(raw2, s3))
    chk_true("3세대 · 뼈대가 닳지 않음", raw3 == raw1)
    chk("3세대 · 삭제 반영", len(sd3["vars"]), len(seed["vars"]))

    chk("생성기 · JS·CSS 에 토큰 글자 잔재",
        len(re.findall(r"%%[A-Z]+%%", be.js_source() + be.CSS)), 0)
    body_seed = re.search(r'id="seed">(.*?)</script>', page, re.S).group(1)
    chk_true("원고의 </script> 가 문서를 깨지 않음", "</script>" not in body_seed)

    # ── 2. 왕복 시험 · 조판한 칸을 되읽으면 글자까지 같은가 ───
    fields = []
    for k in ("title", "basis"):
        fields.append(("머리", k, seed.get(k)))
    for i, v in enumerate(seed["vars"], 1):
        for f in rf.VAR_FIELDS:
            if v.get(f):
                fields.append(("%02d %s" % (i, v["term"]), f, v[f]))
    for i, r0 in enumerate(seed["rules"], 1):
        for f in ("head", "body"):
            fields.append(("규칙%d" % i, f, r0.get(f)))
    for i, sc in enumerate(seed["scopes"], 1):
        for f in ("name", "def"):
            fields.append(("범위%d" % i, f, sc.get(f)))
    chk_true("왕복 시험 · 대상 0건 아님", len(fields) > 100, "%d칸" % len(fields))
    bad = [(w, f) for w, f, t in fields if unfmt(fmt(t)) != t]
    chk("왕복 시험 · 조판했다 되읽어 어긋난 칸", len(bad), 0, str(bad[:4]))

    # 판별력 — 되읽기가 아무 글자나 통과시키지 않는지 스스로 시험한다
    chk_true("왕복 시험 · 판별력",
             unfmt(fmt("A_i 와 `wD` 다")) == "A_i 와 `wD` 다"
             and unfmt("A<sub>i</sub>") != "A_j"
             and unfmt(fmt("Y_{MR,d−1}")) == "Y_{MR,d−1}")

    # 원고 표기가 조판을 못 견디는 자리 — 아래첨자 안 붙임표는 되돌아오지 않는다
    hyph = [(w, f) for w, f, t in fields
            for m in [subscript.SUBRE.finditer(t or "")]
            if any("-" in (x.group(2) or x.group(3) or "") for x in m)]
    chk("왕복 시험 · 아래첨자 안에 붙임표를 쓴 칸", len(hyph), 0, str(hyph[:4]))

    # ── 3. 화면에 나가는 말 ─────────────────────────────
    chk("칸 이름", sorted(be.LABELS.values()),
        sorted(["용어 이름", "기호", "산식", "설명", "기존 표기"]))
    chk("원고 · 금지어",
        sorted({w for w, f, t in fields for x in banned if x in (t or "")}), [])
    chk("원고 · 값 없는 칸을 채운 표시",
        [(w, f) for w, f, t in fields if (t or "").strip() in ("—", "-", "N/A")], [])
    chk("원고의 「미확정」이 편집판에 그대로 실림",
        sum((t or "").count("미확정") for w, f, t in fields),
        sum(fmt(t or "").count("미확정") for w, f, t in fields))

    # ── 4. 산출 파일 자리 ───────────────────────────────
    made = sorted(f for f in os.listdir(OUTDIR)
                  if f.startswith(STEM + "_") and f.endswith(".html")) \
        if os.path.isdir(OUTDIR) else []
    chk("산출 · 최상위에 편집판 한 벌", len(made), 1, str(made))
    chk_true("산출 · 파일명이 한글과 날짜·시각",
             bool(made) and bool(re.match(r"^%s_\d{8}_\d{4}\.html$" % STEM, made[0])),
             made[0] if made else "")
    chk_true("산출 · 조각 파일 있음", os.path.exists(FRAG_PATH))
    # 기획자가 편집판에서 저장한 파일은 날짜·시각이 없는 이름으로 내려받기 최상위에
    # 떨어진다. 그것은 기획자 것이라 세지 않고, 생성기가 낸 것만 본다.
    stray = [f for f in os.listdir(DOWNLOADS)
             if re.match(r"^%s_\d{8}_\d{4}\.html$" % STEM, f)]
    chk("산출 · 생성기가 내려받기 최상위에 떨군 것", stray, [])
    old = sorted(f for f in os.listdir(PREV)
                 if re.match(r"^%s_\d{8}_\d{4}\.html$" % STEM, f)) \
        if os.path.isdir(PREV) else []
    chk_true("산출 · 앞 판은 이전판/ 아래에만", all(f not in made for f in old),
             "%d개" % len(old))

    built = os.path.join(OUTDIR, made[0]) if made else None
    if built:
        rawB, seedB = unpack(load(built))
        chk_true("산출 · 원본 회수", rawB is not None)
        chk_true("산출 · 재생산이 파일과 같음", rawB and regen(rawB, seedB) == load(built))
        chk("산출 · 항 수", len(seedB["vars"]), len(seed["vars"]))
        chk_true("산출 · 원고와 같은 판", seedB == seed,
                 "다르면 build_finaledit.py 를 다시 돌린다")
        chk("산출 · 바깥에서 받아 오는 자원",
            [u for u in re.findall(r'(?:src|href)="(https?://[^"]+)"', load(built))
             if "fonts.googleapis.com" not in u and "fonts.gstatic.com" not in u], [])
        chk_true("산출 · 저장 통로 선언", 'claude.use("artifact")' in load(built))
    else:
        chk_true("산출 파일 있음", False, OUTDIR)

    # ── 5. 되읽기 두 길 · 판별력 자기시험 ────────────────
    edited = json.loads(json.dumps(seed))
    edited["vars"][2]["plain"] = "기획자 말로 다시 쓴 설명이다. 확인필요"
    edited["vars"][17]["term"] = "남은 현금"
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "%s_20260101_0000.html" % STEM)
        io.open(p, "w", encoding="utf-8").write(be.full(be.build(edited)))
        _, back = unpack(load(p))
        rows = rf.diff(seed, back)
        chk("되읽기 · 고친 자리만 집음", sorted((r[0], r[2]) for r in rows),
            [(3, "plain"), (18, "term")])
        chk("되읽기 · 금지어를 집음",
            [w for w in banned if w in rows[0][4] or w in rows[-1][4]], ["확인필요"])
        chk("되읽기 · 고치지 않았을 때 차이 0", len(rf.diff(seed, seed)), 0)

    # ── 6. 워드 ─────────────────────────────────────────
    dp = rw.find_latest()
    if not dp:
        chk_true("워드 · 파일 있음", False, "%s 아래 용어기호정리_YYYYMMDD.docx" % OUTDIR)
    else:
        wd = rw.read_docx(dp)
        chk("워드 · 5절 항 수", len(wd["vars"]), len(seed["vars"]), os.path.basename(dp))
        chk("워드 · 기존 표기 줄 수", sum(1 for v in wd["vars"] if v.get("alias")),
            sum(1 for v in seed["vars"] if v.get("alias")))
        chk("워드 · 규칙 수", len(wd["rules"]), len(seed["rules"]))
        chk("워드 · 범위 수", len(wd["scopes"]), len(seed["scopes"]))
        chk_true("워드 · 원고보다 뒤에 만든 판",
                 os.path.getmtime(dp) >= os.path.getmtime(SEED_PATH),
                 "원고가 더 새것이면 build_final.py 를 다시 돌려야 한다")
        wrows = rw.diff_rows(seed, wd) if hasattr(rw, "diff_rows") else (
            rf.diff(seed, wd, prep=rw.bare)
            + rf.diff_side(seed, wd, "rules", "규칙", ("head", "body"), prep=rw.bare)
            + rf.diff_side(seed, wd, "scopes", "범위", ("name", "def"), prep=rw.bare))
        chk("워드 · 백틱 뺀 원고와 어긋난 칸", len(wrows), 0,
            str([(r[0], r[2]) for r in wrows[:4]]))
        chk_true("워드 · 백틱은 되읽어도 돌아오지 않는다",
                 any("`" in (v.get("plain") or "") for v in seed["vars"])
                 and not any("`" in (v.get("plain") or "") for v in wd["vars"]),
                 "build_final.py 가 워드에 넣을 때 뗀다")

    # ── 7. 브라우저 실측 ────────────────────────────────
    if NOSCREEN:
        print("  (FE_NOSCREEN=1 · 브라우저 실측 뺌)")
    elif not built:
        chk_true("브라우저 · 볼 파일 있음", False)
    elif not os.path.exists(CHROME):
        chk_true("브라우저 · 크롬 있음", False, CHROME)
    else:
        dom = dump_dom(built)
        m = re.search(r'data-rt="(\d+)"', dom)
        chk("브라우저 · 되읽어 어긋난 칸", int(m.group(1)) if m else None, 0)
        sg = re.search(r'data-docsig="([0-9a-f]+):(\d+)"', dom)
        # 페이지가 품은 원고로 견준다. 원고가 페이지보다 새것일 때 지문만 어긋나는 것을
        # 막는다 — 판이 다른 것은 「산출 · 원고와 같은 판」이 따로 본다.
        want = be.full(be.build(unpack(load(built))[1]))
        chk("브라우저 · 저장이 만들 문서의 지문",
            (sg.group(1), int(sg.group(2))) if sg else None,
            (fnv(want), utf16len(want)))
        vis = visible_text(dom)
        chk("브라우저 · 화면에 뜬 금지어", sorted({w for w in banned if w in vis}), [])
        chk("브라우저 · 칸 이름이 다 떴는가",
            sorted({v for v in be.LABELS.values() if v in vis}),
            sorted(be.LABELS.values()))
        chk("브라우저 · 값 없는 칸을 채운 표시",
            len(re.findall(r">\s*[—–]\s*<", dom)), 0)
        cards = len(re.findall(r'<article class="card[^"]*" id="v\d+"', dom))
        chk("브라우저 · 그려진 용어 카드", cards, len(seed["vars"]))
        chk("브라우저 · .html 파일 이름이 화면에 뜸",
            sorted(set(re.findall(r"[0-9A-Za-z_\-]+\.html", vis))), [])

    # ── 판정 ────────────────────────────────────────────
    fail = [r for r in R if not r[0]]
    w = max(len(r[1]) for r in R)
    for ok, name, got, want_, note in R:
        line = "  %s  %-*s  %s" % ("PASS" if ok else "FAIL", w, name, got)
        if not ok:
            line += "   ← 기대 %s" % (want_,)
        if note:
            line += "   %s" % note
        print(line)
    print("\n판정 %d건 · FAIL %d건" % (len(R), len(fail)))
    if not R:
        print("대상 0건 — 검사한 것이 없다")
        sys.exit(1)
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
