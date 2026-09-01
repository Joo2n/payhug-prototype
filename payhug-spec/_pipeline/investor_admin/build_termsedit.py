#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""용어정의서 HTML 편집판 생성기.

원고는 termsdoc_seed.json 한 곳에서 온다. 워드판(build_termsdoc.py)도 같은
원고를 읽으므로 두 산출물은 같은 말을 한다.

산출 — payhug-investor-admin/terms-edit.html
       ~/Downloads/payhug_용어정의서/용어정의서_편집판_YYYYMMDD.html

읽는 사람이 그 자리에서 고치고 저장하면 같은 주소가 새 판이 된다.
저장은 claude.use("artifact").publish(html) 로 하고, 페이지는 자기 원본을
base64 로 품고 있다가 원고만 갈아 끼워 새 문서를 만든다. 그래서 저장을
거듭해도 뼈대가 닳지 않는다.

화면 캡처는 assets/shots/*.webp 를 data URI 로 박아 넣는다. 아티팩트는
바깥 주소에서 그림을 못 받아 오기 때문이다.
"""

import base64
import json
import os
import re
import sys
from datetime import date

PIPE = os.path.dirname(os.path.abspath(__file__))
SEED = os.path.join(PIPE, "termsdoc_seed.json")
REPO = "/Users/semi/cursor/payhug-investor-admin"
SHOTDIR = os.path.join(REPO, "assets", "shots")
OUTDIR = os.path.expanduser("~/Downloads/payhug_용어정의서")
LIVE = "https://payhug-investor-demo.vercel.app"


# ══════════════════════════════════════════════════════════════════
#  원고 다듬기
# ══════════════════════════════════════════════════════════════════

def shots_payload():
    """캡처를 data URI 로. 없으면 빈 사전."""
    out = {}
    if not os.path.isdir(SHOTDIR):
        return out
    for f in sorted(os.listdir(SHOTDIR)):
        ext = os.path.splitext(f)[1].lower()
        mime = {".webp": "image/webp", ".png": "image/png",
                ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}.get(ext)
        if not mime:
            continue
        with open(os.path.join(SHOTDIR, f), "rb") as fh:
            out[f] = "data:%s;base64,%s" % (
                mime, base64.b64encode(fh.read()).decode("ascii"))
    return out


def with_links(seed):
    """화면 파일명으로 실물 주소를 뽑아 붙인다.

    파일명은 screen_file 에 따로 담겨 있다. 화면에 뜨는 screen 문구에는 파일명을
    두지 않는다 — 배포 화면에 .html 이름을 노출하지 않는 규칙(verify_0828 20번)이다.
    """
    for it in seed.get("items", []):
        f = it.get("screen_file")
        it["href"] = ("%s/%s" % (LIVE, f)) if f else None
    return seed


def js_json(obj):
    # JS 의 JSON.stringify 와 글자까지 같아야 한다. 파이썬 기본 구분자는 ", " · ": "
    # 라 띄어쓰기가 끼고, 그러면 페이지가 만든 문서가 받은 파일과 바이트로 갈린다.
    return json.dumps(obj, ensure_ascii=False,
                      separators=(",", ":")).replace("</", "<\\/")


# ══════════════════════════════════════════════════════════════════
#  겉모습
# ══════════════════════════════════════════════════════════════════

CSS = r"""
:root{
  --bg:#FAF9F7; --surface:#FFFFFF; --sunk:#F4F2ED;
  --ink:#1B1A17; --mute:#6B6862; --faint:#94908799;
  --rule:#E5E1D9; --rule-hard:#CFC9BD;
  --accent:#2C4470; --accent-soft:#2C447014;
  --wait:#9C6212; --wait-soft:#9C621218;
  --check:#8A3143; --check-soft:#8A314318;
  --ok:#2F6046;
  --shadow:0 1px 2px #1b1a1710, 0 8px 24px #1b1a170a;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --bg:#16161A; --surface:#1D1E23; --sunk:#22242A;
    --ink:#ECEAE5; --mute:#9B978E; --faint:#77736B99;
    --rule:#2E3038; --rule-hard:#3D4048;
    --accent:#93AEE0; --accent-soft:#93AEE01F;
    --wait:#E0A64A; --wait-soft:#E0A64A22;
    --check:#E08594; --check-soft:#E0859422;
    --ok:#6FBF95;
    --shadow:0 1px 2px #00000040, 0 8px 24px #00000030;
  }
}
:root[data-theme="dark"]{
  --bg:#16161A; --surface:#1D1E23; --sunk:#22242A;
  --ink:#ECEAE5; --mute:#9B978E; --faint:#77736B99;
  --rule:#2E3038; --rule-hard:#3D4048;
  --accent:#93AEE0; --accent-soft:#93AEE01F;
  --wait:#E0A64A; --wait-soft:#E0A64A22;
  --check:#E08594; --check-soft:#E0859422;
  --ok:#6FBF95;
  --shadow:0 1px 2px #00000040, 0 8px 24px #00000030;
}

*{box-sizing:border-box}
body{
  margin:0; background:var(--bg); color:var(--ink);
  font-family:"Noto Sans KR",-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo",sans-serif;
  font-size:15px; line-height:1.75; -webkit-font-smoothing:antialiased;
}
a{color:var(--accent)}
:focus-visible{outline:2px solid var(--accent); outline-offset:2px; border-radius:3px}

/* ── 상단 막대 ───────────────────────────────────── */
.bar{
  position:sticky; top:0; z-index:40; display:flex; align-items:center;
  gap:10px; flex-wrap:wrap; padding:10px 20px;
  background:color-mix(in srgb, var(--bg) 88%, transparent);
  backdrop-filter:saturate(1.6) blur(10px);
  border-bottom:1px solid var(--rule);
}
.bar h1{
  margin:0; font-family:"Noto Serif KR",serif; font-size:16px;
  font-weight:700; letter-spacing:-.01em; white-space:nowrap;
}
.bar .sp{flex:1}
.btn{
  font:inherit; font-size:13px; line-height:1; cursor:pointer;
  padding:8px 12px; border-radius:7px; border:1px solid var(--rule-hard);
  background:var(--surface); color:var(--ink);
}
.btn:hover{border-color:var(--accent); color:var(--accent)}
.btn.pri{background:var(--accent); border-color:var(--accent); color:var(--bg); font-weight:600}
.btn.pri:hover{filter:brightness(1.12); color:var(--bg)}
.btn[disabled]{opacity:.45; cursor:default}
.btn[disabled]:hover{border-color:var(--rule-hard); color:var(--ink)}
.bar input[type=search]{
  font:inherit; font-size:13px; padding:7px 11px; width:180px;
  border-radius:7px; border:1px solid var(--rule-hard);
  background:var(--surface); color:var(--ink);
}
.state{font-size:12px; color:var(--mute); white-space:nowrap}
.state.on{color:var(--wait)}
.state.ok{color:var(--ok)}
.state.bad{color:var(--check)}

/* ── 판짜기 ───────────────────────────────────── */
.wrap{display:grid; grid-template-columns:236px minmax(0,1fr); gap:34px;
      max-width:1160px; margin:0 auto; padding:26px 20px 120px}
@media(max-width:900px){.wrap{grid-template-columns:1fr; gap:18px}
  .toc{position:static; max-height:none}}

.toc{position:sticky; top:66px; align-self:start; max-height:calc(100vh - 92px);
     overflow:auto; font-size:12.5px; line-height:1.55}
.toc .grp{margin:14px 0 6px; font-weight:700; font-size:11px; letter-spacing:.09em;
          color:var(--mute); text-transform:uppercase}
.toc a{display:flex; gap:7px; padding:3px 6px; border-radius:5px;
       color:var(--mute); text-decoration:none}
.toc a:hover{background:var(--accent-soft); color:var(--accent)}
.toc a .n{font-variant-numeric:tabular-nums; opacity:.65; min-width:1.5em}
.toc a.wait{color:var(--wait)} .toc a.check{color:var(--check)}

/* ── 머리 ───────────────────────────────────── */
.head{border-bottom:1px solid var(--rule); padding-bottom:20px; margin-bottom:8px}
.head h2{margin:0 0 6px; font-family:"Noto Serif KR",serif; font-size:30px;
         font-weight:700; letter-spacing:-.02em; text-wrap:balance}
.head .sub{color:var(--mute); font-size:13.5px; margin:0 0 16px}
.facts{display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
       gap:1px; background:var(--rule); border:1px solid var(--rule); border-radius:9px;
       overflow:hidden}
.facts div{background:var(--surface); padding:11px 13px}
.facts dt{font-size:11px; letter-spacing:.06em; color:var(--mute); margin:0 0 3px}
.facts dd{margin:0; font-size:14px; font-weight:600; font-variant-numeric:tabular-nums}

.pend{margin:22px 0 6px; border:1px solid var(--wait); border-radius:9px;
      background:var(--wait-soft); padding:13px 15px}
.pend h3{margin:0 0 8px; font-size:13px; letter-spacing:.04em; color:var(--wait)}
.pend ul{margin:0; padding-left:17px}
.pend li{font-size:13.5px; margin:3px 0}
.pend b{font-weight:600}

.pf{margin:10px 0 0; padding:10px 12px; border-radius:7px; background:var(--surface);
    border:1px solid var(--wait)}
.pf .lb{font-size:11px; letter-spacing:.05em; color:var(--wait); font-weight:700}
.pf .fx{margin-top:5px; font-family:"IBM Plex Mono",ui-monospace,monospace;
        font-size:13px; padding:5px 7px; border-radius:5px; background:var(--sunk)}
.pf .fx:focus{outline:2px solid var(--accent); outline-offset:1px}
.pf .to{margin-top:6px; font-size:12.5px; color:var(--mute)}
.mark{font-size:11px; font-weight:700; letter-spacing:.04em; color:var(--wait);
      margin-left:8px; white-space:nowrap}

/* ── 항목 ───────────────────────────────────── */
.card{background:var(--surface); border:1px solid var(--rule); border-radius:11px;
      margin:16px 0; box-shadow:var(--shadow); scroll-margin-top:72px}
.card.hide{display:none}
.card > .top{display:flex; align-items:baseline; gap:10px; flex-wrap:wrap;
             padding:14px 17px 0}
.card .no{font-variant-numeric:tabular-nums; font-size:12px; font-weight:700;
          color:var(--mute); letter-spacing:.04em}
.card h3{margin:0; font-family:"Noto Serif KR",serif; font-size:19px; font-weight:700;
         letter-spacing:-.01em}
.card .sym{font-family:"IBM Plex Mono",ui-monospace,monospace; font-size:12.5px;
           color:var(--accent); background:var(--accent-soft);
           padding:2px 7px; border-radius:5px}
.pill{font-size:11px; font-weight:700; letter-spacing:.05em; padding:3px 8px;
      border-radius:20px; border:1px solid currentColor; cursor:pointer;
      background:none; font-family:inherit; line-height:1.5}
.pill.s확정{color:var(--mute)}
.pill.s대기{color:var(--wait); background:var(--wait-soft)}
.pill.s확인필요{color:var(--check); background:var(--check-soft)}
.card .ops{margin-left:auto; display:flex; gap:3px; opacity:0; transition:opacity .12s}
.card:hover .ops, .card:focus-within .ops{opacity:1}
.ops button{font:inherit; font-size:11px; line-height:1; cursor:pointer; padding:5px 7px;
            border:1px solid var(--rule); border-radius:5px;
            background:var(--surface); color:var(--mute)}
.ops button:hover{color:var(--accent); border-color:var(--accent)}
.ops button.del:hover{color:var(--check); border-color:var(--check)}

blockquote.q{margin:11px 17px 0; padding:11px 14px; background:var(--sunk);
             border-left:3px solid var(--rule-hard); border-radius:0 7px 7px 0;
             font-family:"Noto Serif KR",serif; font-size:14px; line-height:1.7;
             color:var(--ink)}
blockquote.q .tag{display:block; font-family:"Noto Sans KR",sans-serif; font-size:10.5px;
                  letter-spacing:.08em; color:var(--mute); margin-bottom:5px}

.body{padding:4px 17px 16px}
.plain{margin:12px 0 0; font-size:15px; line-height:1.85}
.rows{margin:13px 0 0; display:grid; grid-template-columns:76px minmax(0,1fr);
      gap:1px; background:var(--rule); border:1px solid var(--rule);
      border-radius:8px; overflow:hidden}
.rows .k{background:var(--sunk); padding:8px 11px; font-size:11.5px; font-weight:700;
         color:var(--mute); letter-spacing:.03em; display:flex; align-items:center;
         justify-content:space-between; gap:4px}
.rows .k button{font:inherit; font-size:12px; line-height:1; border:0; background:none;
                cursor:pointer; color:var(--faint); padding:0 2px; flex:none}
.rows .k [contenteditable]{flex:1; min-width:0}
.rows .k button:hover{color:var(--check)}
.rows .v{background:var(--surface); padding:8px 12px; font-size:13.5px; min-width:0;
         overflow-x:auto}
.rows .v.mono{font-family:"IBM Plex Mono",ui-monospace,monospace; font-size:12.5px;
              white-space:pre-wrap; word-break:break-word}
.rows .v.num{font-variant-numeric:tabular-nums}

[contenteditable]{border-radius:5px; transition:background .12s, box-shadow .12s}
[contenteditable]:hover{background:var(--accent-soft)}
[contenteditable]:focus{outline:none; background:var(--accent-soft);
                        box-shadow:inset 0 0 0 1px var(--accent)}
[contenteditable]:empty::before{content:attr(data-ph); color:var(--faint)}

.addrow{margin-top:8px; display:flex; gap:6px; align-items:center; flex-wrap:wrap}
.addrow .ah{font-size:11px; letter-spacing:.06em; color:var(--mute); margin-right:2px}
.addrow button{font:inherit; font-size:11.5px; cursor:pointer; padding:5px 9px;
               border:1px dashed var(--rule-hard); border-radius:6px;
               background:none; color:var(--mute)}
.addrow button:hover{color:var(--accent); border-color:var(--accent)}

.shots{margin-top:13px; display:flex; gap:10px; flex-wrap:wrap; align-items:flex-start}
.shots figure{margin:0; width:210px}
.shots img{width:100%; display:block; border:1px solid var(--rule-hard);
           border-radius:7px; cursor:zoom-in; background:var(--sunk)}
.shots figcaption{font-size:11px; color:var(--mute); margin-top:4px}
.golink{display:inline-flex; align-items:center; gap:5px; font-size:12px;
        text-decoration:none; padding:5px 9px; border:1px solid var(--rule-hard);
        border-radius:6px; color:var(--accent)}
.golink:hover{border-color:var(--accent)}

.sep{margin:34px 0 4px; padding-top:22px; border-top:2px solid var(--rule-hard);
     font-family:"Noto Serif KR",serif; font-size:21px; font-weight:700}
.sep span{font-family:"Noto Sans KR",sans-serif; font-size:12px; font-weight:400;
          color:var(--mute); margin-left:9px}
.newitem{margin:16px 0; text-align:center}

/* ── 확대 ───────────────────────────────────── */
.lb{position:fixed; inset:0; z-index:90; background:#0B0B0Dee; display:none}
.lb.on{display:block}
.lb .stage{position:absolute; inset:0; overflow:hidden; cursor:grab}
.lb .stage.drag{cursor:grabbing}
.lb img{position:absolute; top:0; left:0; transform-origin:0 0;
        image-rendering:-webkit-optimize-contrast; user-select:none;
        -webkit-user-drag:none}
.lb .hud{position:absolute; top:0; left:0; right:0; display:flex; gap:8px;
         align-items:center; padding:12px 16px; color:#EFEDE8; font-size:12.5px}
.lb .hud .sp{flex:1}
.lb .hud button{font:inherit; font-size:12.5px; line-height:1; cursor:pointer;
                padding:7px 11px; border-radius:6px; border:1px solid #FFFFFF33;
                background:#FFFFFF14; color:#EFEDE8}
.lb .hud button:hover{background:#FFFFFF26}
.lb .hud .zm{font-variant-numeric:tabular-nums; min-width:52px; text-align:center}

@media print{
  .bar,.toc,.ops,.addrow,.newitem,.golink{display:none!important}
  .wrap{grid-template-columns:1fr; padding:0}
  .card{break-inside:avoid; box-shadow:none}
}
@media (prefers-reduced-motion:reduce){*{transition:none!important; animation:none!important}}
"""


JS = r"""
(function(){
"use strict";

var SEED = JSON.parse(document.getElementById("seed").textContent);
var SHOTS = JSON.parse(document.getElementById("shots").textContent);
var SRC = null;
var dirty = false;
var pub = null;
var dl = null;

var $ = function(s,r){return (r||document).querySelector(s)};
var esc = function(s){return String(s==null?"":s)
  .replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")};

/* ── 자기 원본 ───────────────────────────────── */
function b64dec(s){
  var bin = atob(s), b = new Uint8Array(bin.length);
  for (var i=0;i<bin.length;i++) b[i] = bin.charCodeAt(i);
  return new TextDecoder().decode(b);
}
/* #src 는 JSON 문자열 하나다. 따옴표째 atob 에 넘기면 그 자리에서 깨진다. */
try { SRC = b64dec(JSON.parse(document.getElementById("src").textContent)); }
catch(e){ SRC = null; }

function jsonFor(o){ return JSON.stringify(o).split("</").join("<\\/"); }

var TK = function(n){ return "%"+"%" + n + "%"+"%" };

function renderDoc(){
  if (!SRC) return null;
  var cut = SRC.indexOf(TK("SRC"));
  if (cut < 0) return null;
  var before = SRC.slice(0, cut), after = SRC.slice(cut + TK("SRC").length);
  var fill = function(s){
    return s.split(TK("SEED")).join(jsonFor(SEED))
            .split(TK("SHOTS")).join(jsonFor(SHOTS));
  };
  var b = new TextEncoder().encode(SRC), raw = "", CH = 0x8000;
  for (var i=0;i<b.length;i+=CH) raw += String.fromCharCode.apply(null, b.subarray(i,i+CH));
  return wrapFull(fill(before) + btoa(raw) + fill(after));
}

/* 조각에 껍데기를 씌운다. 생성기의 full() 과 같은 절차다.
   조각 맨 앞의 <title> 은 머리로 옮긴다 — 본문에 남으면 글자로 찍힌다. */
function wrapFull(frag){
  var m = /^\s*<title>([\s\S]*?)<\/title>\s*/.exec(frag);
  var title = m ? m[1] : "용어 정의서";
  var body = m ? frag.slice(m[0].length) : frag;
  return '<!doctype html>\n<html lang="ko">\n<head>\n'
       + '<meta charset="utf-8">\n'
       + '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
       + '<title>' + title + '</title>\n</head>\n<body>\n'
       + body + '\n</body>\n</html>\n';
}

/* ── 그리기 ───────────────────────────────── */
var FIELDS = [
  ["formula","산식","mono"],
  ["symbol","기호","mono"],
  ["our_value","우리 값","num"],
  ["screen","화면",""],
  ["note","비고",""]
];

/* 대기 중인 산식은 원고 한 곳(pending_formula)에서만 온다.
   42항(⑤)은 그 블록을, 45항(⑥)은 그 블록의 depends 를 가리킨다. */
function pfmark(b){
  /* 대체 여부는 따로 적어 두지 않고 두 문자열을 견줘 낸다.
     그래야 대표 산식이 왔을 때 formula 한 줄만 고쳐도 표시가 맞는다. */
  return b.formula === b.basis_formula ? b.status : "";
}

function pf(it){
  var b = SEED.pending_formula;
  if (!b || !it.formula_ref) return null;
  var src = it.no === b.no ? b
          : (b.depends||[]).filter(function(x){ return x.no === it.no })[0];
  if (!src) return null;
  return {formula:src.formula, our_value:src.our_value, status:pfmark(b)};
}

function cardHTML(it, idx){
  var st = it.status || "확정";
  var h = '<article class="card" id="t'+it.no+'" data-i="'+idx+'">';

  h += '<div class="top"><span class="no">'+String(it.no).padStart(2,"0")+'</span>';
  h += '<h3 contenteditable data-f="term" data-ph="용어">'+esc(it.term)+'</h3>';
  if (it.symbol) h += '<span class="sym">'+esc(it.symbol)+'</span>';
  h += '<button class="pill s'+st+'" data-act="st" title="상태 바꾸기">'+st+'</button>';
  h += '<span class="ops">'
     + '<button data-act="up" title="위로">↑</button>'
     + '<button data-act="down" title="아래로">↓</button>'
     + '<button data-act="add" title="아래에 항목 추가">＋</button>'
     + '<button data-act="del" class="del" title="항목 삭제">✕</button>'
     + '</span></div>';

  if (it.quote)
    h += '<blockquote class="q"><span class="tag">대표 원문 · 고칠 수 없음</span>'
       + esc(it.quote) + '</blockquote>';

  h += '<div class="body">';
  h += '<p class="plain" contenteditable data-f="plain" data-ph="풀이를 쓰세요">'
     + esc(it.plain) + '</p>';

  var rows = "", p = pf(it);
  FIELDS.forEach(function(f){
    if (p && (f[0] === "formula" || f[0] === "our_value")){
      var pv = f[0] === "formula" ? p.formula : p.our_value;
      if (pv == null || pv === "") return;
      rows += '<div class="k">'+f[1]+'</div>'
            + '<div class="v '+f[2]+'">'+esc(pv)
            + (p.status ? '<span class="mark">'+esc(p.status)+'</span>' : '')
            + '</div>';
      return;
    }
    if (it[f[0]] == null || it[f[0]] === "") return;
    rows += '<div class="k">'+f[1]+'<button data-act="rmf" data-f="'+f[0]+'" title="이 줄 지우기">×</button></div>'
          + '<div class="v '+f[2]+'" contenteditable data-f="'+f[0]+'">'+esc(it[f[0]])+'</div>';
  });
  (it.extra||[]).forEach(function(x,j){
    rows += '<div class="k"><span contenteditable data-f="xk" data-j="'+j+'" '
          + 'data-ph="이름">'+esc(x.k)+'</span>'
          + '<button data-act="rmx" data-j="'+j+'" title="이 줄 지우기">×</button></div>'
          + '<div class="v" contenteditable data-f="xv" data-j="'+j+'">'+esc(x.v)+'</div>';
  });
  if (rows) h += '<div class="rows">'+rows+'</div>';

  var miss = FIELDS.filter(function(f){
    if (p && (f[0] === "formula" || f[0] === "our_value")) return false;
    return it[f[0]] == null || it[f[0]] === "";
  });
  h += '<div class="addrow"><span class="ah">줄 추가</span>';
  miss.forEach(function(f){ h += '<button data-act="addf" data-f="'+f[0]+'">'+f[1]+'</button>' });
  h += '<button data-act="addx">이름을 직접</button></div>';

  var sh = it.shot && SHOTS[it.shot];
  if (sh || it.href){
    h += '<div class="shots">';
    if (sh) h += '<figure><img src="'+SHOTS[it.shot]+'" alt="'+esc(it.term)+' 화면" '
               + 'data-act="zoom" data-shot="'+esc(it.shot)+'">'
               + '<figcaption>'+esc(it.shot)+' · 눌러서 확대</figcaption></figure>';
    if (it.href) h += '<a class="golink" href="'+esc(it.href)+'" target="_blank" '
                    + 'rel="noopener">실제 화면 열기 ↗</a>';
    h += '</div>';
  }

  return h + '</div></article>';
}

function render(){
  var items = SEED.items;
  var h = "";

  h += '<div class="head"><h2 contenteditable data-g="title">'+esc(SEED.title)+'</h2>';
  h += '<p class="sub" contenteditable data-g="basis">'+esc(SEED.basis)+'</p>';
  var sc = SEED.scale || {};
  h += '<dl class="facts">'
     + '<div><dt>기준일</dt><dd>'+esc(SEED.asof)+'</dd></div>'
     + '<div><dt>투자실행액</dt><dd>'+(sc["투자실행액"]||0).toLocaleString()+'원</dd></div>'
     + '<div><dt>순현금</dt><dd>'+(sc["순현금"]||0).toLocaleString()+'원</dd></div>'
     + '<div><dt>가맹점</dt><dd>'+(sc["가맹점수"]||0)+'곳</dd></div>'
     + '<div><dt>할인율</dt><dd>'+((sc["할인율"]||0)*100)+'%</dd></div>'
     + '<div><dt>항목</dt><dd>'+items.length+'항</dd></div></dl></div>';

  if ((SEED.pending||[]).length){
    h += '<div class="pend"><h3>미결</h3><ul>';
    SEED.pending.forEach(function(p,i){
      h += '<li><b contenteditable data-p="item" data-j="'+i+'">'+esc(p.item)+'</b> · '
         + '<span contenteditable data-p="who" data-j="'+i+'">'+esc(p.who)+'</span> — '
         + '<span contenteditable data-p="what" data-j="'+i+'">'+esc(p.what)+'</span></li>';
    });
    h += '</ul>';
    var b = SEED.pending_formula;
    if (b){
      var to = [b.no].concat((b.depends||[]).map(function(x){ return x.no }));
      h += '<div class="pf"><div class="lb">'+esc(b.ref)+' '+esc(b.term)
         + (pfmark(b) ? ' · '+esc(pfmark(b)) : '')+'</div>'
         + '<div class="fx" contenteditable data-pf="formula">'+esc(b.formula)+'</div>'
         + '<div class="to">'+to.map(function(n){ return n+"항" }).join(" · ")
         + ' · ' + esc((b.depends||[]).map(function(x){
             return x.ref+" = "+x.formula }).join(" · ")) + '</div></div>';
    }
    h += '</div>';
  }

  var seen = {};
  items.forEach(function(it, i){
    var g = it.image || 1;
    if (!seen[g]){
      seen[g] = 1;
      var n = items.filter(function(x){return (x.image||1)===g}).length;
      h += '<h2 class="sep">['+g+'번 이미지]<span>'+n+'항</span></h2>';
    }
    h += cardHTML(it, i);
  });
  h += '<div class="newitem"><button class="btn" data-act="addend">＋ 맨 끝에 항목 추가</button></div>';

  $("#doc").innerHTML = h;
  toc();
  filter();
}

function toc(){
  var h = "", seen = {};
  SEED.items.forEach(function(it){
    var g = it.image || 1;
    if (!seen[g]){ seen[g]=1; h += '<div class="grp">'+g+'번 이미지</div>' }
    var cls = it.status === "대기" ? "wait" : it.status === "확인필요" ? "check" : "";
    h += '<a href="#t'+it.no+'" class="'+cls+'"><span class="n">'
       + String(it.no).padStart(2,"0")+'</span><span>'+esc(it.term)+'</span></a>';
  });
  $("#toc").innerHTML = h;
}

/* ── 고르기 ───────────────────────────────── */
function filter(){
  var q = ($("#q").value || "").trim().toLowerCase();
  var only = $("#only").value;
  var n = 0;
  SEED.items.forEach(function(it, i){
    var el = document.querySelector('.card[data-i="'+i+'"]');
    if (!el) return;
    var okQ = !q || (it.term+" "+it.quote+" "+it.plain+" "+(it.formula||"")+" "+
                     (it.note||"")+" "+(it.symbol||"")).toLowerCase().indexOf(q) >= 0;
    var okS = only === "all" || it.status === only;
    var show = okQ && okS;
    el.classList.toggle("hide", !show);
    if (show) n++;
  });
  $("#cnt").textContent = n + " / " + SEED.items.length + "항";
}

/* ── 고치기 ───────────────────────────────── */
function mark(){
  if (dirty) return;
  dirty = true;
  say("고친 것 있음", "on");
  $("#save").disabled = false;
}

function idx(el){ var c = el.closest(".card"); return c ? +c.dataset.i : -1 }

document.addEventListener("input", function(e){
  var el = e.target;
  if (!el.isContentEditable) return;
  var t = el.textContent;
  if (el.dataset.g){ SEED[el.dataset.g] = t; mark(); return }
  if (el.dataset.p){ SEED.pending[+el.dataset.j][el.dataset.p] = t; mark(); return }
  if (el.dataset.pf){ SEED.pending_formula[el.dataset.pf] = t; mark(); return }
  var i = idx(el); if (i < 0) return;
  var f = el.dataset.f;
  if (f === "xk") SEED.items[i].extra[+el.dataset.j].k = t;
  else if (f === "xv") SEED.items[i].extra[+el.dataset.j].v = t;
  else if (f) SEED.items[i][f] = t;
  mark();
});

document.addEventListener("paste", function(e){
  if (!e.target.isContentEditable) return;
  e.preventDefault();
  document.execCommand("insertText", false,
    (e.clipboardData || window.clipboardData).getData("text/plain"));
});

var STATES = ["확정","대기","확인필요"];

function renumber(){ SEED.items.forEach(function(it,i){ it.no = i+1 }) }

document.addEventListener("click", function(e){
  var b = e.target.closest("[data-act]");
  if (!b) return;
  var act = b.dataset.act, i = idx(b);

  if (act === "zoom"){ zoom(b.dataset.shot); return }

  if (act === "st"){
    var it = SEED.items[i];
    it.status = STATES[(STATES.indexOf(it.status||"확정")+1) % 3];
    b.textContent = it.status;
    b.className = "pill s"+it.status;
    toc(); mark(); return;
  }
  if (act === "up" || act === "down"){
    var j = act === "up" ? i-1 : i+1;
    if (j < 0 || j >= SEED.items.length) return;
    var a = SEED.items;
    var g = a[i].image; a[i].image = a[j].image; a[j].image = g;
    var t = a[i]; a[i] = a[j]; a[j] = t;
    renumber(); mark(); render();
    var el = document.querySelector('.card[data-i="'+j+'"]');
    if (el) el.scrollIntoView({block:"center"});
    return;
  }
  if (act === "del"){
    if (!confirm("“"+(SEED.items[i].term||"이 항목")+"” 삭제")) return;
    SEED.items.splice(i,1); renumber(); mark(); render(); return;
  }
  if (act === "add" || act === "addend"){
    var at = act === "add" ? i+1 : SEED.items.length;
    var img = act === "add" ? (SEED.items[i].image||1)
                            : ((SEED.items[SEED.items.length-1]||{}).image||1);
    SEED.items.splice(at, 0, {no:0, image:img, term:"", quote:"", plain:"",
                              status:"확인필요", extra:[]});
    renumber(); mark(); render();
    var nel = document.querySelector('.card[data-i="'+at+'"] h3');
    if (nel){ nel.scrollIntoView({block:"center"}); nel.focus() }
    return;
  }
  if (act === "addf"){ SEED.items[i][b.dataset.f] = ""; mark(); render();
    var fe = document.querySelector('.card[data-i="'+i+'"] [data-f="'+b.dataset.f+'"]');
    if (fe){ fe.scrollIntoView({block:"center"}); fe.focus() } return }
  if (act === "rmf"){ delete SEED.items[i][b.dataset.f]; mark(); render(); return }
  if (act === "rmx"){
    var ex = SEED.items[i].extra || [];
    ex.splice(+b.dataset.j, 1);
    if (!ex.length) delete SEED.items[i].extra;
    mark(); render(); return;
  }
  if (act === "addx"){
    var it2 = SEED.items[i];
    it2.extra = it2.extra || [];
    it2.extra.push({k:"", v:""});
    mark(); render();
    var xe = document.querySelector('.card[data-i="'+i+'"] [data-f="xk"][data-j="'
                                    +(it2.extra.length-1)+'"]');
    if (xe){ xe.scrollIntoView({block:"center"}); xe.focus() }
    return;
  }
});

/* ── 확대 ───────────────────────────────── */
var lb = {k:1, x:0, y:0, w:0, h:0, on:false};

function zoom(name){
  var src = SHOTS[name]; if (!src) return;
  var im = $("#lbimg");
  im.onload = function(){
    lb.w = im.naturalWidth; lb.h = im.naturalHeight;
    fit(); 
  };
  im.src = src;
  $("#lbname").textContent = name;
  $("#lb").classList.add("on");
  lb.on = true;
}
function apply(){
  var im = $("#lbimg");
  im.style.transform = "translate("+lb.x+"px,"+lb.y+"px) scale("+lb.k+")";
  $("#lbzm").textContent = Math.round(lb.k*100)+"%";
}
function fit(){
  var st = $("#lbstage");
  var k = Math.min((st.clientWidth-56)/lb.w, (st.clientHeight-104)/lb.h, 1);
  lb.k = k; lb.x = (st.clientWidth - lb.w*k)/2; lb.y = (st.clientHeight - lb.h*k)/2 + 18;
  apply();
}
function scale(k, cx, cy){
  var st = $("#lbstage");
  cx = cx == null ? st.clientWidth/2 : cx;
  cy = cy == null ? st.clientHeight/2 : cy;
  var nk = Math.min(8, Math.max(.08, k));
  lb.x = cx - (cx - lb.x) * (nk/lb.k);
  lb.y = cy - (cy - lb.y) * (nk/lb.k);
  lb.k = nk; apply();
}
function close(){ $("#lb").classList.remove("on"); lb.on = false; $("#lbimg").src = "" }

$("#lbfit").onclick = fit;
$("#lb1").onclick = function(){ scale(1) };
$("#lbin").onclick = function(){ scale(lb.k*1.35) };
$("#lbout").onclick = function(){ scale(lb.k/1.35) };
$("#lbx").onclick = close;
$("#lb").addEventListener("click", function(e){ if (e.target.id === "lbstage") close() });
$("#lbstage").addEventListener("wheel", function(e){
  e.preventDefault();
  var r = e.currentTarget.getBoundingClientRect();
  scale(lb.k * (e.deltaY < 0 ? 1.12 : 1/1.12), e.clientX-r.left, e.clientY-r.top);
}, {passive:false});
(function(){
  var st = $("#lbstage"), down = false, px = 0, py = 0;
  st.addEventListener("pointerdown", function(e){
    down = true; px = e.clientX; py = e.clientY;
    st.classList.add("drag"); st.setPointerCapture(e.pointerId);
  });
  st.addEventListener("pointermove", function(e){
    if (!down) return;
    lb.x += e.clientX - px; lb.y += e.clientY - py;
    px = e.clientX; py = e.clientY; apply();
  });
  st.addEventListener("pointerup", function(){ down = false; st.classList.remove("drag") });
  st.addEventListener("pointercancel", function(){ down = false; st.classList.remove("drag") });
})();
window.addEventListener("keydown", function(e){
  if (!lb.on) return;
  if (e.key === "Escape") close();
  else if (e.key === "+" || e.key === "=") scale(lb.k*1.35);
  else if (e.key === "-") scale(lb.k/1.35);
  else if (e.key === "0") fit();
});

/* ── 저장 ───────────────────────────────── */
function say(t, cls){ var s = $("#st"); s.textContent = t; s.className = "state "+(cls||"") }

$("#q").addEventListener("input", filter);
$("#only").addEventListener("change", filter);

$("#save").addEventListener("click", async function(){
  var doc = renderDoc();
  if (!doc){ say("원본 회수 실패 · 저장 불가", "bad"); return }
  $("#save").disabled = true;
  say("저장하는 중", "on");
  if (pub){
    try {
      await pub.publish(doc);
      dirty = false; say("저장됨", "ok");
      return;
    } catch(err){
      var c = err && err.code;
      if (c === "conflict"){ say("다른 판이 먼저 저장됨 · 최신 판으로 다시 엶", "on"); return }
      if (c === "not_writer" || c === "not_granted" || c === "not_declared"){
        pub = null; say("읽기 전용 · 이 주소에는 저장 불가", "bad");
      } else {
        say("저장 실패 · "+(c||"까닭 모름"), "bad");
      }
    }
  }
  if (dl){
    try {
      await dl.save({filename:"용어정의서_편집판.html", data:doc});
      dirty = false; say("파일로 내려받음", "ok");
      return;
    } catch(e2){ say("내려받기 취소됨", "bad") }
  } else {
    say("이 사본에서는 저장 불가", "bad");
  }
  $("#save").disabled = false;
});

window.addEventListener("beforeunload", function(e){
  if (dirty){ e.preventDefault(); e.returnValue = "" }
});

/* 검증기가 페이지가 실제로 만드는 문서를 바이트로 대조한다.
   파이썬 쪽 재생산만 보면 페이지 안에서 깨진 것을 못 잡는다. */
window.__renderDoc = renderDoc;
window.__seed = SEED;

render();
say(SRC ? "" : "원본 회수 실패 · 저장 불가", SRC ? "" : "bad");
$("#save").disabled = true;

if (window.claude && window.claude.use){
  claude.use("artifact").then(function(a){
    pub = a;
    if (a) say(dirty ? "고친 것 있음" : "저장 가능", dirty ? "on" : "");
  }).catch(function(){});
  claude.use("downloads").then(function(d){ dl = d }).catch(function(){});
}
})();
"""


TEMPLATE = """<title>%%TITLE%%</title>
<style>@import url("https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=Noto+Serif+KR:wght@400;700&family=IBM+Plex+Mono:wght@400;500&display=swap");
%%CSS%%</style>

<header class="bar">
  <h1>%%TITLE%%</h1>
  <span class="sp"></span>
  <input type="search" id="q" placeholder="용어·산식 찾기" aria-label="찾기">
  <select id="only" class="btn" aria-label="상태로 고르기">
    <option value="all">전체</option>
    <option value="확정">확정</option>
    <option value="대기">대기</option>
    <option value="확인필요">확인필요</option>
  </select>
  <span class="state" id="cnt"></span>
  <span class="state" id="st"></span>
  <button class="btn pri" id="save">저장</button>
</header>

<div class="wrap">
  <nav class="toc" id="toc" aria-label="목차"></nav>
  <main id="doc"></main>
</div>

<div class="lb" id="lb" role="dialog" aria-label="화면 확대">
  <div class="stage" id="lbstage"><img id="lbimg" alt=""></div>
  <div class="hud">
    <span id="lbname"></span>
    <span class="sp"></span>
    <button id="lbout" aria-label="축소">−</button>
    <span class="zm" id="lbzm">100%</span>
    <button id="lbin" aria-label="확대">＋</button>
    <button id="lbfit">맞춤</button>
    <button id="lb1">100%</button>
    <button id="lbx">닫기 (Esc)</button>
  </div>
</div>

<script type="application/json" id="seed">%%SEED%%</script>
<script type="application/json" id="shots">%%SHOTS%%</script>
<script type="application/json" id="src">"%%SRC%%"</script>
<script>%%JS%%</script>
"""


# 조각에 씌우는 껍데기. 파이썬과 페이지 안 JS 가 같은 절차를 쓴다.
# 조각 맨 앞의 <title> 은 머리로 옮긴다 — 본문에 남으면 글자로 찍힌다.
def full(frag):
    m = re.match(r"\s*<title>(.*?)</title>\s*", frag, re.S)
    title = m.group(1) if m else "용어 정의서"
    body = frag[m.end():] if m else frag
    return ("<!doctype html>\n<html lang=\"ko\">\n<head>\n"
            "<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
            "<title>" + title + "</title>\n</head>\n<body>\n"
            + body + "\n</body>\n</html>\n")


# ══════════════════════════════════════════════════════════════════
#  조립 — 자기 원본을 품는 방식
# ══════════════════════════════════════════════════════════════════

def build(seed, shots):
    raw = (TEMPLATE
           .replace("%%CSS%%", CSS)
           .replace("%%JS%%", JS)
           .replace("%%TITLE%%", seed.get("title", "용어 정의서")))

    cut = raw.index("%%SRC%%")
    before, after = raw[:cut], raw[cut + len("%%SRC%%"):]

    def fill(s):
        return (s.replace("%%SEED%%", js_json(seed))
                 .replace("%%SHOTS%%", js_json(shots)))

    b64 = base64.b64encode(raw.encode("utf-8")).decode("ascii")
    return fill(before) + b64 + fill(after)


def main():
    if not os.path.exists(SEED):
        sys.exit("원고 없음 — %s" % SEED)
    with open(SEED, encoding="utf-8") as f:
        seed = with_links(json.load(f))

    shots = shots_payload()
    doc = build(seed, shots)

    stamp = os.environ.get("TERMSDOC_STAMP") or date.today().strftime("%Y%m%d")
    os.makedirs(OUTDIR, exist_ok=True)
    page = full(doc)
    targets = [os.path.join(REPO, "terms-edit.html"),
               os.path.join(OUTDIR, "용어정의서_편집판_%s.html" % stamp)]
    for t in targets:
        with open(t, "w", encoding="utf-8") as f:
            f.write(page)
    # 아티팩트로 올릴 때 쓰는 조각. 게시가 껍데기를 한 겹 씌우므로 조각을 준다.
    frag = os.path.join(PIPE, "terms-edit.fragment.html")
    with open(frag, "w", encoding="utf-8") as f:
        f.write(doc)
    targets.append(frag)

    used = sorted({i.get("shot") for i in seed["items"] if i.get("shot")})
    miss = [s for s in used if s not in shots]
    for t in targets:
        print("%s  %.0fKB" % (t, os.path.getsize(t) / 1024))
    print("  항목 %d · 캡처 %d장 박음 (원고가 부르는 %d장%s)"
          % (len(seed["items"]), len(shots), len(used),
             "" if not miss else " · 없는 것 " + ", ".join(miss)))


if __name__ == "__main__":
    main()
