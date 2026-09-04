#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""용어정의서 두 산출물 검사 — HTML 편집판과 워드판.

편집판은 자기 원본을 base64 로 품고 있다가 저장할 때 원고만 갈아 끼운다.
그 되돌아오는 길이 한 군데라도 끊기면 사용자가 고친 내용이 날아가므로,
세대를 넘겨 가며 뼈대가 닳지 않는지 여기서 본다.

FAIL 이 하나라도 있으면 exit 1. 대상이 0건이어도 FAIL 이다.
"""

import base64
import io
import json
import os
import re
import sys
import importlib.util

PIPE = os.path.dirname(os.path.abspath(__file__))
SEED = os.path.join(PIPE, "termsdoc_seed.json")
GLOS = os.path.join(PIPE, "symbol_glossary.json")
CEO = os.path.join(PIPE, "ceo_definitions.md")
RULE = os.path.join(PIPE, "dm_0831", "symbol_rule_0831.md")
BUILT = "/Users/semi/cursor/payhug-investor-admin/terms-edit.html"

BAN = ("만기", "가중평균만기", "Duration")

# 인용 자리 — 대표 원문·DM 을 글자 그대로 옮긴 칸이라 기호를 갈지 않는다.
# 「…」로 감싼 대목도 같다. 기호 검사는 이 밖만 본다.
QUOTE_KEYS = ("quote", "ceo_source", "aliases", "evidence", "drift", "not_used")

rows = []


def chk(name, got, want, note=""):
    ok = (got == want)
    rows.append((ok, name, got, want, note))
    return ok


def chk_true(name, cond, note=""):
    rows.append((bool(cond), name, "예" if cond else "아니오", "예", note))
    return bool(cond)


def load(path):
    return io.open(path, encoding="utf-8").read()


def old_notation():
    """기호 규칙 문서의 갈아 끼우는 표에서 「지금」 칸의 옛 표기를 읽는다.

    기대값을 검증기가 따로 들고 있으면 규칙이 바뀔 때 둘이 어긋난다.
    「그대로」로 적힌 행과 낱글자 D 한 자짜리는 뺀다 — 대문자 D 자체는 살아 있는 기호다.
    """
    if not os.path.exists(RULE):
        return []
    out, seen = [], set()
    for line in load(RULE).splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 2 or "그대로" in cells[1]:
            continue
        for tok in re.findall(r"`([^`]+)`", cells[0]):
            for t in re.split(r"\s*~\s*", tok):
                t = t.strip()
                if len(t) > 1 and t not in seen:
                    seen.add(t)
                    out.append(t)
    return out


def rule_letters():
    """규칙 문서의 낱글자 표에서 등재돼야 할 글자를 읽는다."""
    if not os.path.exists(RULE):
        return set()
    out, on = set(), False
    for line in load(RULE).splitlines():
        if line.startswith("## "):
            on = "낱글자" in line
            continue
        if on and line.startswith("|"):
            c = [x.strip() for x in line.strip().strip("|").split("|")]
            m = re.match(r"^`(.+)`$", c[0]) if c else None
            if m:
                out.add(m.group(1))
    return out


def scan(obj, tokens):
    """인용 자리를 뺀 곳에 옛 표기가 남았는지 훑는다."""
    bad = []

    def strip_quotes(s):
        return re.sub(r"「[^」]*」", "", s)

    def walk(o, path):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in QUOTE_KEYS or k == "drift_sites":
                    continue
                walk(v, path + "." + str(k))
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, "%s[%d]" % (path, i))
        elif isinstance(o, str):
            body = strip_quotes(o)
            for t in tokens:
                if re.search(r"(?<![A-Za-z])" + re.escape(t), body):
                    bad.append((path, o[:60], t))
    walk(obj, "")
    return bad


def unpack(doc):
    """문서에서 품고 있는 원본·원고·캡처를 꺼낸다."""
    m = re.search(r'id="src">"([A-Za-z0-9+/=]+)"</script>', doc)
    raw = base64.b64decode(m.group(1)).decode("utf-8") if m else None
    s = re.search(r'id="seed">(.*?)</script>', doc, re.S)
    sh = re.search(r'id="shots">(.*?)</script>', doc, re.S)
    seed = json.loads(s.group(1).replace("<\\/", "</")) if s else None
    shots = json.loads(sh.group(1).replace("<\\/", "</")) if sh else None
    return raw, seed, shots


def regen(raw, seed, shots, jsjson, full):
    """페이지의 renderDoc() 과 같은 절차로 문서를 다시 만든다."""
    cut = raw.index("%%SRC%%")
    before, after = raw[:cut], raw[cut + 7:]
    f = lambda s: (s.replace("%%SEED%%", jsjson(seed))
                    .replace("%%SHOTS%%", jsjson(shots)))
    frag = f(before) + base64.b64encode(raw.encode("utf-8")).decode("ascii") + f(after)
    # 페이지의 renderDoc() 도 마지막에 껍데기를 씌운다. 여기서도 같은 절차를 거쳐야
    # 재생산 대조가 실제 산출물과 맞는다.
    return full(frag)


def main():
    spec = importlib.util.spec_from_file_location(
        "bt", os.path.join(PIPE, "build_termsedit.py"))
    bt = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bt)

    # ── 1. 생성기 자체 — 꾸민 원고로 3세대까지 ──────────────
    seed = {"title": "시험", "basis": "시험", "asof": "2026-08-27", "meeting": "",
            "scale": {"투자실행액": 80000000, "순현금": 20000000,
                      "가맹점수": 8, "할인율": 0.0011},
            "pending": [{"item": "⑤", "who": "대표", "what": "수식"}],
            "items": [{"no": 1, "image": 1, "term": "가", "quote": "</script> & <b>",
                       "plain": "풀이", "formula": "Σ Ai", "status": "확정",
                       "shot": "x.webp"},
                      {"no": 2, "image": 2, "term": "나", "quote": "둘",
                       "plain": "풀이2", "status": "대기"}]}
    shots = {"x.webp": "data:image/webp;base64,AAAA"}
    g1 = bt.build(seed, shots)

    raw1, s1, h1 = unpack(g1)
    chk_true("생성기 · 원본 회수", raw1 is not None)
    chk("생성기 · 회수한 원본의 토큰 3종", 
        (raw1 or "").count("%%SEED%%") + (raw1 or "").count("%%SHOTS%%")
        + (raw1 or "").count("%%SRC%%"), 3)
    # build() 는 조각을 낸다. 재생산은 마지막에 껍데기를 씌우므로 조각에 껍데기를
    # 씌운 것과 견준다.
    chk_true("생성기 · 재생산이 원본과 같음",
             raw1 and regen(raw1, s1, h1, bt.js_json, bt.full) == bt.full(g1))

    s2 = json.loads(json.dumps(seed))
    s2["items"][0]["plain"] = "고친 풀이"
    s2["items"].append({"no": 3, "image": 2, "term": "다", "quote": "",
                        "plain": "덧붙임", "status": "미확정"})
    g2 = regen(raw1, s2, h1, bt.js_json, bt.full)
    raw2, sd2, h2 = unpack(g2)
    chk_true("2세대 · 뼈대가 닳지 않음", raw2 == raw1)
    chk("2세대 · 항목 수", len(sd2["items"]), 3)
    chk("2세대 · 고친 풀이 살아 있음", sd2["items"][0]["plain"], "고친 풀이")

    s3 = json.loads(json.dumps(sd2))
    del s3["items"][1]
    g3 = regen(raw2, s3, h2, bt.js_json, bt.full)
    raw3, sd3, _ = unpack(g3)
    chk_true("3세대 · 뼈대가 닳지 않음", raw3 == raw1)
    chk("3세대 · 삭제 반영", len(sd3["items"]), 2)

    body_seed = re.search(r'id="seed">(.*?)</script>', g1, re.S).group(1)
    chk_true("인용문의 </script> 가 문서를 깨지 않음",
             "</script>" not in body_seed and "<\\/script>" in body_seed)
    chk("JS·CSS 에 토큰 글자 잔재",
        len(re.findall(r"%%[A-Z]+%%", bt.JS + bt.CSS)), 0)

    # ── 2. 테마 ──────────────────────────────────────────
    css = bt.CSS
    base = set(re.findall(r"(--[a-z-]+)\s*:", css.split("@media")[0]))
    tail = css[css.index("@media"):]
    only_dark = {v for blk in re.findall(r"\{([^{}]*)\}", tail)
                 for v in re.findall(r"(--[a-z-]+)\s*:", blk) if v not in base}
    chk("색을 어두운 테마에서만 정의한 자리", len(only_dark), 0,
        ", ".join(sorted(only_dark)))
    chk_true("body 에 바탕색을 직접 칠함",
             bool(re.search(r"body\{[^}]*background:var\(--bg\)", css)))
    chk_true("밝은 테마 선택이 어두운 OS 를 이김",
             ':root:not([data-theme="light"])' in css)
    chk_true("어두운 테마 선택이 밝은 OS 를 이김",
             ':root[data-theme="dark"]' in css)

    # ── 3. 원고 ──────────────────────────────────────────
    if not os.path.exists(SEED):
        chk_true("원고 파일 있음", False, SEED)
    else:
        sd = json.loads(load(SEED))
        items = sd.get("items", [])
        chk("원고 · 항목 수", len(items), 45)
        # 항수는 대표 원문의 불릿을 그 자리에서 세어 기준으로 삼는다.
        # 검증기 안에 두 번째 기준표를 두면 원문이 바뀔 때 서로 어긋난다.
        cur, want = None, {1: 0, 2: 0}
        for line in (load(CEO).splitlines() if os.path.exists(CEO) else []):
            if "[1번 이미지]" in line:
                cur = 1
            elif "[2번 이미지]" in line:
                cur = 2
            elif cur and line.startswith("- "):
                want[cur] += 1
        chk("원고 · [1번 이미지]", sum(1 for i in items if i.get("image") == 1), want[1])
        chk("원고 · [2번 이미지]", sum(1 for i in items if i.get("image") == 2), want[2])
        chk("원고 · 항수 합이 원문 불릿과 같음", len(items), want[1] + want[2])
        chk("원고 · 번호가 1..N 연속",
            [i.get("no") for i in items], list(range(1, len(items) + 1)))
        chk("원고 · 풀이가 빈 항", sum(1 for i in items if not (i.get("plain") or "").strip()), 0)
        chk("원고 · 인용이 빈 항", sum(1 for i in items if not (i.get("quote") or "").strip()), 0)
        chk("원고 · 모르는 상태값",
            sorted({i.get("status") for i in items} - {"확정", "대기", "미확정"}), [])

        if os.path.exists(CEO):
            ceo = re.sub(r"\s+", " ", load(CEO))
            bad = [i["no"] for i in items
                   if re.sub(r"\s+", " ", i.get("quote", "")).strip() not in ceo]
            chk("원고 · 인용이 대표 원문에 그대로 있음 (어긋난 항)", bad, [])
        else:
            chk_true("대표 원문 파일 있음", False, CEO)

        blob = json.dumps(sd, ensure_ascii=False)
        for w in BAN:
            chk("원고 · 금지어 「%s」" % w, blob.count(w), 0)

        # ── 3-2. 기호 규칙 ───────────────────────────────
        # 기대값은 dm_0831/symbol_rule_0831.md 의 갈아 끼우는 표에서 읽는다.
        # 검증기 안에 두 번째 기준표를 두면 규칙이 바뀔 때 서로 어긋난다.
        gone = old_notation()
        chk_true("기호 규칙 · 갈아 끼우는 표를 읽음", len(gone) >= 5,
                 "옛 표기 %d개 %s" % (len(gone), gone[:4]))
        badS = scan(sd, gone)
        chk("원고 · 옛 대문자 D 날짜 표기 (인용 밖)", len(badS), 0,
            str([(p, t) for p, _, t in badS[:4]]))
        if os.path.exists(GLOS):
            sg = json.loads(load(GLOS))
            badG = scan(sg, gone)
            chk("기호 사전 · 옛 대문자 D 날짜 표기 (인용 밖)", len(badG), 0,
                str([(p, t) for p, _, t in badG[:4]]))
            chk("기호 사전 · 등재 수와 symbol_count 가 같음",
                sg.get("symbol_count"), len(sg.get("symbols", [])))
            letters = {s["symbol"] for s in sg.get("symbols", [])}
            chk("기호 사전 · 규칙이 세운 낱글자 중 미등재",
                sorted(rule_letters() - letters), [])
        else:
            chk_true("기호 사전 파일 있음", False, GLOS)

        # ── 3-3. ⑤ 산식 자리 ────────────────────────────
        pf = sd.get("pending_formula") or {}
        chk_true("⑤ · pending_formula 블록 있음", bool(pf.get("formula")))
        f5 = pf.get("formula", "")
        # ⑤ 산식이 원고 어디에도 하드코딩돼 있지 않아야 한 곳만 고치면 끝난다.
        loose = [i.get("no") for i in items if f5 and f5 in json.dumps(
            {k: v for k, v in i.items()}, ensure_ascii=False)]
        chk("⑤ · pending_formula 밖에 박힌 산식", loose, [])
        chk("⑤ · 산식을 들고 있는 항 (formula 키 직접)",
            [i.get("no") for i in items
             if i.get("formula_ref") and i.get("formula")], [])
        ref5 = [i.get("no") for i in items if i.get("formula_ref")]
        chk("⑤ · 블록을 가리키는 항", sorted(ref5),
            sorted([pf.get("no")] + [d.get("no") for d in pf.get("depends", [])]))
        chk("⑥ · ⑤ 를 가져다 씀",
            sorted({d.get("uses") for d in pf.get("depends", [])}), ["⑤"])
        chk_true("⑥ · 산식에 ⑤ 가 들어 있음",
                 all("⑤" in (d.get("formula") or "") for d in pf.get("depends", [])))
        chk("⑤ · 대체 전이라 대기 표시가 붙음",
            pf.get("status") if pf.get("formula") == pf.get("basis_formula") else None,
            "미확정")

    # ── 4. 산출물 ────────────────────────────────────────
    if not os.path.exists(BUILT):
        chk_true("편집판 산출물 있음", False, BUILT)
    else:
        doc = load(BUILT)
        rawB, seedB, shotsB = unpack(doc)
        chk_true("산출물 · 원본 회수", rawB is not None)
        chk_true("산출물 · 재생산이 파일과 같음",
                 rawB and regen(rawB, seedB, shotsB, bt.js_json, bt.full) == doc)
        chk("산출물 · 항목 수", len(seedB.get("items", [])), 45)
        want = sorted({i.get("shot") for i in seedB.get("items", []) if i.get("shot")})
        chk("산출물 · 원고가 부르는 캡처 중 안 박힌 것",
            [s for s in want if s not in (shotsB or {})], [])
        chk_true("산출물 · 캡처가 data URI 로 박힘",
                 all(v.startswith("data:image/") for v in (shotsB or {}).values())
                 and len(shotsB or {}) > 0)
        chk("산출물 · 바깥에서 받아 오는 자원",
            len([u for u in re.findall(r'(?:src|href)="(https?://[^"]+)"', doc)
                 if "fonts.googleapis.com" not in u and "fonts.gstatic.com" not in u
                 and "payhug-investor-demo.vercel.app" not in u]), 0)
        for w in BAN:
            chk("산출물 · 금지어 「%s」" % w, doc.count(w), 0)
        chk_true("산출물 · 저장 통로 선언", 'claude.use("artifact")' in doc)

    # ── 판정 ─────────────────────────────────────────────
    fail = [r for r in rows if not r[0]]
    w = max(len(r[1]) for r in rows)
    for ok, name, got, want_, note in rows:
        line = "  %s  %-*s  %s" % ("PASS" if ok else "FAIL", w, name, got)
        if not ok:
            line += "   ← 기대 %s" % (want_,)
        if note:
            line += "   %s" % note
        print(line)
    print("\n판정 %d건 · FAIL %d건" % (len(rows), len(fail)))
    if not rows:
        print("대상 0건 — 검사한 것이 없다")
        sys.exit(1)
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
