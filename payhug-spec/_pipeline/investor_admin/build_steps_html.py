#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""화면 칸별 중간 계산 문서 생성기.

meeting_0901/steps_all.json 을 읽어 HTML 한 장으로 편다. 값은 전부 그 JSON 에서
오고 이 스크립트는 배치만 한다 — 숫자를 만들지 않는다.

산출 — _pipeline/investor_admin/steps_all.fragment.html  (아티팩트 게시용 조각)
       payhug-investor-admin/steps-all.html              (완전한 문서)
"""

import html
import importlib.util
import io
import json
import os
import sys

PIPE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(PIPE, "meeting_0901", "steps_all.json")
REPO = "/Users/semi/cursor/payhug-investor-admin"

_spec = importlib.util.spec_from_file_location("bt", os.path.join(PIPE, "build_termsedit.py"))
_bt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_bt)
full = _bt.full

e = lambda s: html.escape("" if s is None else str(s))

SCREEN_NAME = {"invest-assets": "투자 자산", "invest-profit": "투자 수익",
               "invest-assets · invest-profit": "투자 자산 · 투자 수익"}

CSS = """
:root{--bg:#FAF9F7;--surface:#FFFFFF;--sunk:#F4F2ED;--ink:#1B1A17;--mute:#6B6862;
 --faint:#9490879e;--rule:#E5E1D9;--rule-hard:#CFC9BD;--accent:#2C4470;
 --accent-soft:#2C447014;--hide:#8A3143;--hide-soft:#8A314314;--ok:#2F6046;
 --ok-soft:#2F604614;--warn:#9C6212;--warn-soft:#9C621214;
 --shadow:0 1px 2px #1b1a1710,0 8px 22px #1b1a170a;}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
 --bg:#16161A;--surface:#1D1E23;--sunk:#22242A;--ink:#ECEAE5;--mute:#9B978E;
 --faint:#77736b9e;--rule:#2E3038;--rule-hard:#3D4048;--accent:#93AEE0;
 --accent-soft:#93AEE01F;--hide:#E08594;--hide-soft:#E0859420;--ok:#6FBF95;
 --ok-soft:#6FBF9520;--warn:#E0A64A;--warn-soft:#E0A64A20;
 --shadow:0 1px 2px #00000040,0 8px 22px #00000030;}}
:root[data-theme="dark"]{
 --bg:#16161A;--surface:#1D1E23;--sunk:#22242A;--ink:#ECEAE5;--mute:#9B978E;
 --faint:#77736b9e;--rule:#2E3038;--rule-hard:#3D4048;--accent:#93AEE0;
 --accent-soft:#93AEE01F;--hide:#E08594;--hide-soft:#E0859420;--ok:#6FBF95;
 --ok-soft:#6FBF9520;--warn:#E0A64A;--warn-soft:#E0A64A20;
 --shadow:0 1px 2px #00000040,0 8px 22px #00000030;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
 font-family:"Noto Sans KR",-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo",sans-serif;
 font-size:15px;line-height:1.75;-webkit-font-smoothing:antialiased}
code,.m{font-family:"IBM Plex Mono",ui-monospace,monospace}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:4px}

.bar{position:sticky;top:0;z-index:30;display:flex;align-items:center;gap:9px;
 flex-wrap:wrap;padding:9px 20px;border-bottom:1px solid var(--rule);
 background:color-mix(in srgb,var(--bg) 90%,transparent);backdrop-filter:blur(10px)}
.bar h1{margin:0;font-family:"Noto Serif KR",serif;font-size:15px;font-weight:700;white-space:nowrap}
.bar .sp{flex:1}
.bar input,.bar select,.bar button{font:inherit;font-size:12.5px;line-height:1;
 padding:7px 10px;border-radius:7px;border:1px solid var(--rule-hard);
 background:var(--surface);color:var(--ink)}
.bar input{width:150px} .bar button{cursor:pointer}
.bar button:hover{border-color:var(--accent);color:var(--accent)}
.bar .cnt{font-size:12px;color:var(--mute);white-space:nowrap}

.wrap{max-width:940px;margin:0 auto;padding:28px 20px 110px}
h2.head{margin:0 0 5px;font-family:"Noto Serif KR",serif;font-size:29px;font-weight:700;
 letter-spacing:-.02em}
.meta{color:var(--mute);font-size:13px;margin:0 0 20px}
.tally{display:grid;grid-template-columns:repeat(auto-fit,minmax(128px,1fr));gap:1px;
 background:var(--rule);border:1px solid var(--rule);border-radius:10px;overflow:hidden}
.tally div{background:var(--surface);padding:12px 14px}
.tally dt{font-size:11px;letter-spacing:.05em;color:var(--mute);margin:0 0 3px}
.tally dd{margin:0;font-size:20px;font-weight:700;font-variant-numeric:tabular-nums}
.tally dd small{font-size:12px;font-weight:400;color:var(--mute);margin-left:3px}
.tally .h dd{color:var(--hide)}

h3.grp{margin:34px 0 4px;padding-top:20px;border-top:2px solid var(--rule-hard);
 font-family:"Noto Serif KR",serif;font-size:19px;font-weight:700}
h3.grp .t{font-family:"Noto Sans KR",sans-serif;font-size:12px;font-weight:400;
 color:var(--mute);margin-left:8px}

details.cell{background:var(--surface);border:1px solid var(--rule);border-radius:10px;
 margin:8px 0;box-shadow:var(--shadow);overflow:hidden}
details.cell[hidden]{display:none}
details.cell>summary{list-style:none;cursor:pointer;padding:11px 15px;
 display:grid;grid-template-columns:minmax(0,1fr) auto;gap:6px 12px;align-items:baseline}
details.cell>summary::-webkit-details-marker{display:none}
details.cell>summary:hover{background:var(--accent-soft)}
.lbl{font-weight:700;font-size:14.5px}
.sym{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:12px;
 color:var(--accent);background:var(--accent-soft);padding:1px 6px;border-radius:4px;
 margin-left:7px}
.val{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:13px;font-weight:600;
 font-variant-numeric:tabular-nums;color:var(--accent);text-align:right;white-space:nowrap}
.sub{grid-column:1/-1;font-size:11.5px;color:var(--mute);display:flex;gap:9px;flex-wrap:wrap}
.sub b{font-weight:700;color:var(--hide)}
.tag{font-size:10px;font-weight:700;letter-spacing:.05em;padding:2px 7px;border-radius:20px;
 border:1px solid currentColor}
.tag.nox{color:var(--hide);background:var(--hide-soft)}
.tag.rn{color:var(--warn);background:var(--warn-soft)}

.bd{padding:0 15px 14px;border-top:1px solid var(--rule)}
.fx{margin:11px 0 0;padding:10px 13px;background:var(--sunk);border-radius:8px;
 font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:12.5px;line-height:1.7;
 white-space:pre-wrap;overflow-x:auto}
ol.steps{margin:11px 0 0;padding:0;list-style:none}
ol.steps li{position:relative;padding:6px 0 6px 30px;border-top:1px dashed var(--rule);
 font-size:13.5px;line-height:1.65}
ol.steps li:first-child{border-top:0}
ol.steps li::before{content:attr(data-n);position:absolute;left:0;top:8px;width:19px;height:19px;
 border-radius:5px;background:var(--hide-soft);color:var(--hide);font-size:11px;font-weight:700;
 display:flex;align-items:center;justify-content:center}
ol.steps li.on::before{background:var(--ok-soft);color:var(--ok)}
ol.steps .d{display:block;font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:12px;
 color:var(--mute);margin-top:1px;word-break:break-word}
.foot{margin:11px 0 0;display:grid;grid-template-columns:62px minmax(0,1fr);gap:1px;
 background:var(--rule);border:1px solid var(--rule);border-radius:8px;overflow:hidden}
.foot .k{background:var(--sunk);padding:7px 10px;font-size:11px;font-weight:700;color:var(--mute)}
.foot .v{background:var(--surface);padding:7px 11px;font-size:12.5px;min-width:0;
 word-break:break-word}
.foot .v.x{color:var(--hide);font-weight:600}
@media print{.bar{display:none}details.cell{break-inside:avoid;box-shadow:none}
 details.cell>summary{cursor:default}}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
"""


def cell_html(c, idx):
    steps = c.get("steps") or []
    nsh = sum(1 for s in steps if not s.get("visible"))
    nox = not c.get("xlsx")
    blob = " ".join(str(c.get(k) or "") for k in
                    ("label", "term", "symbol", "formula", "value", "xlsx", "source")) \
        + " " + " ".join((s.get("what") or "") + " " + (s.get("detail") or "") for s in steps)

    o = ['<details class="cell" data-i="%d" data-screen="%s" data-table="%s" '
         'data-nox="%d" data-q="%s">' % (idx, e(c.get("screen")), e(c.get("table")),
                                         1 if nox else 0, e(blob.lower()))]
    o.append("<summary>")
    o.append('<span><span class="lbl">%s</span>' % e(c.get("label")))
    if c.get("marker"):
        o.append('<span class="sym">%s</span>' % e(c["marker"]))
    if c.get("symbol"):
        o.append('<span class="sym">%s</span>' % e(c["symbol"]))
    o.append("</span>")
    o.append('<span class="val">%s</span>' % e(c.get("value")))
    o.append('<span class="sub"><span>단계 %d · 화면 밖 <b>%d</b></span>' % (len(steps), nsh))
    if nox:
        o.append('<span class="tag nox">엑셀 자리 없음</span>')
    if c.get("rename_pending"):
        o.append('<span class="tag rn">개명 대기</span>')
    o.append("</span></summary>")

    o.append('<div class="bd">')
    if c.get("formula"):
        o.append('<div class="fx">%s</div>' % e(c["formula"]))
    if steps:
        o.append("<ol class='steps'>")
        for s in steps:
            cls = " class='on'" if s.get("visible") else ""
            o.append("<li%s data-n='%s'>%s" % (cls, e(s.get("n")), e(s.get("what"))))
            if s.get("detail"):
                o.append('<span class="d">%s</span>' % e(s["detail"]))
            o.append("</li>")
        o.append("</ol>")
    rows = []
    if c.get("term"):
        rows.append(("용어", e(c["term"]), ""))
    if c.get("hidden"):
        rows.append(("화면 밖", " · ".join(e(h) for h in c["hidden"]), ""))
    rows.append(("엑셀", e(c["xlsx"]) if c.get("xlsx") else "자리 없음",
                 "" if c.get("xlsx") else " x"))
    if c.get("source"):
        rows.append(("근거", e(c["source"]), ""))
    o.append('<div class="foot">')
    for k, v, kls in rows:
        o.append('<div class="k">%s</div><div class="v%s">%s</div>' % (k, kls, v))
    o.append("</div></div></details>")
    return "".join(o)


def build(d):
    cells, cnt, meta = d["cells"], d["counts"], d["meta"]
    o = ['<title>화면 칸별 중간 계산</title>',
         '<style>@import url("https://fonts.googleapis.com/css2?family=Noto+Sans+KR:'
         'wght@400;500;700&family=Noto+Serif+KR:wght@400;700&family=IBM+Plex+Mono:'
         'wght@400;500&display=swap");', CSS, "</style>"]

    tables = []
    for c in cells:
        key = (c.get("screen"), c.get("table"))
        if key not in tables:
            tables.append(key)

    o.append('<div class="bar"><h1>화면 칸별 중간 계산</h1>')
    o.append('<input type="search" id="q" placeholder="칸·산식 찾기" aria-label="찾기">')
    o.append('<select id="f" aria-label="표로 고르기"><option value="">전체 표</option>')
    for s, t in tables:
        o.append('<option value="%s|%s">%s · %s</option>' % (e(s), e(t), e(SCREEN_NAME.get(s, s)), e(t)))
    o.append("</select>")
    o.append('<label style="font-size:12.5px;color:var(--mute);display:flex;gap:5px;'
             'align-items:center;white-space:nowrap">'
             '<input type="checkbox" id="nox" style="width:auto"> 엑셀 자리 없는 것만</label>')
    o.append('<span class="sp"></span><span class="cnt" id="cnt"></span>')
    o.append('<button id="all">모두 펼치기</button></div>')

    o.append('<div class="wrap"><h2 class="head">화면 칸별 중간 계산</h2>')
    o.append('<p class="meta">투자 자산 · 투자 수익 두 화면의 값이 뜨는 칸 전건 · '
             '기준일 %s · 조회기간 %s</p>' % (e(meta.get("기준일")), e(meta.get("조회기간"))))
    o.append('<dl class="tally">'
             '<div><dt>칸</dt><dd>%d</dd></div>'
             '<div><dt>계산 단계</dt><dd>%d</dd></div>'
             '<div class="h"><dt>화면에 안 뜨는 단계</dt><dd>%d<small> / %d</small></dd></div>'
             '<div class="h"><dt>엑셀 자리 없는 칸</dt><dd>%d</dd></div>'
             '<div><dt>개명 대기 칸</dt><dd>%d</dd></div></dl>'
             % (cnt["칸"], cnt["단계"], cnt["화면에_안뜨는_단계"], cnt["단계"],
                cnt["엑셀자리_없는_칸"], cnt["개명대기_칸"]))

    idx = 0
    for s, t in tables:
        grp = [c for c in cells if c.get("screen") == s and c.get("table") == t]
        nsh = sum(1 for c in grp for st in (c.get("steps") or []) if not st.get("visible"))
        o.append('<h3 class="grp">%s · %s<span class="t">칸 %d · 화면 밖 단계 %d</span></h3>'
                 % (e(SCREEN_NAME.get(s, s)), e(t), len(grp), nsh))
        for c in grp:
            o.append(cell_html(c, idx))
            idx += 1
    o.append("</div>")

    o.append("""<script>
(function(){
 "use strict";
 var all = Array.prototype.slice.call(document.querySelectorAll("details.cell"));
 var q = document.getElementById("q"), f = document.getElementById("f"),
     nox = document.getElementById("nox"), cnt = document.getElementById("cnt"),
     btn = document.getElementById("all");
 function apply(){
   var t = (q.value||"").trim().toLowerCase(), key = f.value, only = nox.checked, n = 0;
   all.forEach(function(el){
     var ok = (!t || el.dataset.q.indexOf(t) >= 0)
           && (!key || key === el.dataset.screen + "|" + el.dataset.table)
           && (!only || el.dataset.nox === "1");
     el.hidden = !ok; if (ok) n++;
   });
   document.querySelectorAll("h3.grp").forEach(function(h){
     var sib = h.nextElementSibling, any = false;
     while (sib && sib.tagName === "DETAILS"){ if (!sib.hidden) any = true; sib = sib.nextElementSibling; }
     h.hidden = !any;
   });
   cnt.textContent = n + " / " + all.length + "칸";
 }
 q.addEventListener("input", apply); f.addEventListener("change", apply);
 nox.addEventListener("change", apply);
 btn.addEventListener("click", function(){
   var open = all.some(function(el){ return !el.hidden && el.open });
   all.forEach(function(el){ if (!el.hidden) el.open = !open });
   btn.textContent = open ? "모두 펼치기" : "모두 접기";
 });
 apply();
})();
</script>""")
    return "".join(o)


def main():
    if not os.path.exists(SRC):
        sys.exit("원고 없음 — %s" % SRC)
    d = json.load(io.open(SRC, encoding="utf-8"))
    frag = build(d)
    out = [(os.path.join(PIPE, "steps_all.fragment.html"), frag),
           (os.path.join(REPO, "steps-all.html"), full(frag))]
    for p, body in out:
        io.open(p, "w", encoding="utf-8").write(body)
        print("%s  %.0fKB" % (p, os.path.getsize(p) / 1024))
    print("  칸 %d · 단계 %d · 화면 밖 %d"
          % (d["counts"]["칸"], d["counts"]["단계"], d["counts"]["화면에_안뜨는_단계"]))


if __name__ == "__main__":
    main()
