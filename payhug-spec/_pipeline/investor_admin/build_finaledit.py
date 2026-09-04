#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""용어·기호 정리 HTML 편집판 생성기.

원고는 final_terms.json 한 곳에서 온다. 워드·HTML 정본(build_final.py)도 같은
원고를 읽으므로 세 산출물은 같은 말을 한다. 이 생성기는 원고를 읽기만 한다.

산출 — ~/Downloads/payhug_용어정의서/용어기호정리_편집판_YYYYMMDD_HHMM.html
       _pipeline/investor_admin/final-terms-edit.fragment.html

브라우저에서 칸을 고치고 저장하면 자기 원본을 품은 새 HTML 이 내려온다.
그 파일을 read_finaledit.py 가 읽어 원고 꼴로 되돌린다.

되읽기가 깨지지 않게 두 가지를 건다.
  · 아래첨자는 subscript.py 의 정규식을 그대로 JS 로 넘겨 조판하고,
    readField() 가 `_i` · `_{d−1}` 표기로 되돌린다
  · 원고의 백틱은 <code> 로 조판하고 되읽을 때 백틱으로 되돌린다

페이지는 뜨자마자 스스로 왕복 시험을 돌려 어긋난 칸 수를 html[data-rt] 에,
저장이 만들 문서의 지문을 html[data-docsig] 에 적는다. verify_finaledit.py 가
헤드리스 크롬으로 그 두 값을 본다.
"""

import base64
import html
import io
import json
import os
import re
import shutil
import sys
from datetime import datetime

PIPE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PIPE)
import subscript

SEED_PATH = os.path.join(PIPE, "final_terms.json")
FRAG_PATH = os.path.join(PIPE, "final-terms-edit.fragment.html")
OUTDIR = os.path.expanduser("~/Downloads/payhug_용어정의서")
PREV = os.path.join(OUTDIR, "이전판")
STEM = "용어기호정리_편집판"

# 화면에 다는 칸 이름. 그 필드가 무엇인지 그대로 쓴다.
LABELS = {
    "term": "용어 이름",
    "sym": "기호",
    "formula": "산식",
    "plain": "설명",
    "alias": "기존 표기",
}


def js_json(obj):
    # JS 의 JSON.stringify 와 글자까지 같아야 한다. 파이썬 기본 구분자는 ", " · ": "
    # 라 띄어쓰기가 끼고, 그러면 페이지가 만든 문서가 받은 파일과 바이트로 갈린다.
    return json.dumps(obj, ensure_ascii=False,
                      separators=(",", ":")).replace("</", "<\\/")


CSS = r"""
:root{
  --bg:#FAF9F7; --surface:#FFFFFF; --sunk:#F4F2ED;
  --ink:#1B1A17; --mute:#6B6862; --faint:#94908799;
  --rule:#E5E1D9; --rule-hard:#CFC9BD;
  --accent:#2C4470; --accent-soft:#2C447014;
  --wait:#9C6212; --check:#8A3143; --ok:#2F6046;
  --shadow:0 1px 2px #1b1a1710, 0 8px 24px #1b1a170a;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --bg:#16161A; --surface:#1D1E23; --sunk:#22242A;
    --ink:#ECEAE5; --mute:#9B978E; --faint:#77736B99;
    --rule:#2E3038; --rule-hard:#3D4048;
    --accent:#93AEE0; --accent-soft:#93AEE01F;
    --wait:#E0A64A; --check:#E08594; --ok:#6FBF95;
    --shadow:0 1px 2px #00000040, 0 8px 24px #00000030;
  }
}
:root[data-theme="dark"]{
  --bg:#16161A; --surface:#1D1E23; --sunk:#22242A;
  --ink:#ECEAE5; --mute:#9B978E; --faint:#77736B99;
  --rule:#2E3038; --rule-hard:#3D4048;
  --accent:#93AEE0; --accent-soft:#93AEE01F;
  --wait:#E0A64A; --check:#E08594; --ok:#6FBF95;
  --shadow:0 1px 2px #00000040, 0 8px 24px #00000030;
}

*{box-sizing:border-box}
body{margin:0; background:var(--bg); color:var(--ink);
  font-family:"Noto Sans KR",-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo",sans-serif;
  font-size:15px; line-height:1.75; -webkit-font-smoothing:antialiased}
a{color:var(--accent)}
:focus-visible{outline:2px solid var(--accent); outline-offset:2px; border-radius:3px}
code{font-family:"IBM Plex Mono",ui-monospace,monospace; font-size:.92em;
     background:var(--sunk); padding:0 3px; border-radius:3px}

.bar{position:sticky; top:0; z-index:40; display:flex; align-items:center; gap:10px;
  flex-wrap:wrap; padding:10px 20px;
  background:color-mix(in srgb, var(--bg) 88%, transparent);
  backdrop-filter:saturate(1.6) blur(10px); border-bottom:1px solid var(--rule)}
.bar h1{margin:0; font-family:"Noto Serif KR",serif; font-size:16px; font-weight:700;
  letter-spacing:-.01em; white-space:nowrap}
.bar .sp{flex:1}
.btn{font:inherit; font-size:13px; line-height:1; cursor:pointer; padding:8px 12px;
  border-radius:7px; border:1px solid var(--rule-hard); background:var(--surface); color:var(--ink)}
.btn:hover{border-color:var(--accent); color:var(--accent)}
.btn.pri{background:var(--accent); border-color:var(--accent); color:var(--bg); font-weight:600}
.btn.pri:hover{filter:brightness(1.12); color:var(--bg)}
.btn[disabled]{opacity:.45; cursor:default}
.btn[disabled]:hover{border-color:var(--rule-hard); color:var(--ink)}
.bar input[type=search]{font:inherit; font-size:13px; padding:7px 11px; width:180px;
  border-radius:7px; border:1px solid var(--rule-hard); background:var(--surface); color:var(--ink)}
.state{font-size:12px; color:var(--mute); white-space:nowrap}
.state.on{color:var(--wait)}
.state.ok{color:var(--ok)}
.state.bad{color:var(--check)}

.wrap{display:grid; grid-template-columns:236px minmax(0,1fr); gap:34px;
  max-width:1160px; margin:0 auto; padding:26px 20px 120px}
@media(max-width:900px){.wrap{grid-template-columns:1fr; gap:18px}
  .toc{position:static; max-height:none}}
.toc{position:sticky; top:66px; align-self:start; max-height:calc(100vh - 92px);
  overflow:auto; font-size:12.5px; line-height:1.55}
.toc .grp{margin:14px 0 6px; font-weight:700; font-size:11px; letter-spacing:.09em; color:var(--mute)}
.toc a{display:flex; gap:7px; padding:3px 6px; border-radius:5px; color:var(--mute);
  text-decoration:none}
.toc a:hover{background:var(--accent-soft); color:var(--accent)}
.toc a .n{font-variant-numeric:tabular-nums; opacity:.65; min-width:1.6em}

.head{border-bottom:1px solid var(--rule); padding-bottom:18px}
.head h2{margin:0 0 4px; font-family:"Noto Serif KR",serif; font-size:29px; font-weight:700;
  letter-spacing:-.02em}
.head .sub{color:var(--mute); font-size:13.5px; margin:0}
.head .asof{color:var(--mute); font-size:12.5px; margin:4px 0 0;
  font-variant-numeric:tabular-nums}

h2.sep{margin:34px 0 10px; padding-top:22px; border-top:2px solid var(--rule-hard);
  font-family:"Noto Serif KR",serif; font-size:20px; font-weight:700}
h2.sep span{font-family:"Noto Sans KR",sans-serif; font-size:12px; font-weight:400;
  color:var(--mute); margin-left:9px}

.scroll{overflow-x:auto; border:1px solid var(--rule); border-radius:9px;
  background:var(--surface); box-shadow:var(--shadow); margin:12px 0}
table{width:100%; border-collapse:collapse; font-size:13.5px}
th,td{padding:9px 12px; text-align:left; border-bottom:1px solid var(--rule); vertical-align:top}
th{background:var(--sunk); font-size:11.5px; letter-spacing:.04em; color:var(--mute);
  font-weight:700; white-space:nowrap}
tr:last-child td{border-bottom:0}
td.n{font-family:"IBM Plex Mono",ui-monospace,monospace; white-space:nowrap; color:var(--accent)}

.rule{background:var(--surface); border:1px solid var(--rule); border-radius:10px;
  padding:12px 15px; margin:9px 0; box-shadow:var(--shadow)}
.rule .num{font-variant-numeric:tabular-nums; font-size:12px; font-weight:700;
  color:var(--mute); margin-right:6px}
.rule b{font-size:15px}
.rule .bd{display:block; color:var(--mute); font-size:13.5px; line-height:1.7; margin-top:4px}

.card{background:var(--surface); border:1px solid var(--rule); border-radius:11px;
  margin:14px 0; box-shadow:var(--shadow); scroll-margin-top:72px; padding:13px 16px 14px}
.card.hide{display:none}
.card .hd{display:flex; align-items:flex-end; gap:14px; flex-wrap:wrap}
.card .no{font-variant-numeric:tabular-nums; font-size:12px; font-weight:700;
  color:var(--mute); letter-spacing:.04em; padding-bottom:3px}
.fld{display:flex; flex-direction:column; gap:1px; min-width:0}
.fld .lb{font-size:10.5px; letter-spacing:.06em; color:var(--mute)}
.fld .t{font-family:"Noto Serif KR",serif; font-size:18px; font-weight:700; letter-spacing:-.01em}
.fld .s{font-family:"IBM Plex Mono",ui-monospace,monospace; font-size:13px; color:var(--accent);
  background:var(--accent-soft); padding:2px 8px; border-radius:5px}
.card .ops{margin-left:auto; display:flex; gap:3px; opacity:0; transition:opacity .12s}
.card:hover .ops, .card:focus-within .ops{opacity:1}
.ops button{font:inherit; font-size:11px; line-height:1; cursor:pointer; padding:5px 7px;
  border:1px solid var(--rule); border-radius:5px; background:var(--surface); color:var(--mute)}
.ops button:hover{color:var(--accent); border-color:var(--accent)}
.ops button.del:hover{color:var(--check); border-color:var(--check)}

.rows{margin:11px 0 0; display:grid; grid-template-columns:82px minmax(0,1fr); gap:1px;
  background:var(--rule); border:1px solid var(--rule); border-radius:8px; overflow:hidden}
.rows .k{background:var(--sunk); padding:8px 10px; font-size:11.5px; font-weight:700;
  color:var(--mute); letter-spacing:.03em; display:flex; align-items:flex-start;
  justify-content:space-between; gap:4px}
.rows .k button{font:inherit; font-size:12px; line-height:1; border:0; background:none;
  cursor:pointer; color:var(--faint); padding:0 2px; flex:none}
.rows .k button:hover{color:var(--check)}
.rows .v{background:var(--surface); padding:8px 12px; font-size:13.5px; min-width:0; overflow-x:auto}
.rows .v.mono{font-family:"IBM Plex Mono",ui-monospace,monospace; font-size:12.5px;
  white-space:pre-wrap; word-break:break-word}

[contenteditable]{border-radius:5px; transition:background .12s, box-shadow .12s}
[contenteditable]:hover{background:var(--accent-soft)}
[contenteditable]:focus{outline:none; background:var(--accent-soft);
  box-shadow:inset 0 0 0 1px var(--accent)}
[contenteditable]:empty::before{content:attr(data-ph); color:var(--faint)}

.addrow{margin-top:8px; display:flex; gap:6px; align-items:center; flex-wrap:wrap}
.addrow .ah{font-size:11px; letter-spacing:.06em; color:var(--mute); margin-right:2px}
.addrow button{font:inherit; font-size:11.5px; cursor:pointer; padding:5px 9px;
  border:1px dashed var(--rule-hard); border-radius:6px; background:none; color:var(--mute)}
.addrow button:hover{color:var(--accent); border-color:var(--accent)}
.newitem{margin:16px 0; text-align:center}

@media print{.bar,.toc,.ops,.addrow,.newitem{display:none!important}
  .wrap{grid-template-columns:1fr; padding:0}
  .card{break-inside:avoid; box-shadow:none}}
@media (prefers-reduced-motion:reduce){*{transition:none!important; animation:none!important}}
"""


JS_HEAD = r"""
(function(){
"use strict";

var SEED = JSON.parse(document.getElementById("seed").textContent);
var SRC = null;
var dirty = false;
var pub = null;
var dl = null;

var $ = function(s,r){return (r||document).querySelector(s)};
var esc = function(s){return String(s==null?"":s)
  .replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")};

/* 아래첨자 조판 — subscript.py 의 정규식을 그대로 넘겨 받는다.
   두 벌로 적으면 규칙이 바뀔 때 어긋나므로 생성기가 한 곳에서 찍어 준다. */
var SUBRE = new RegExp(%%SUBRE%%, "g");
var subs = function(s){
  return String(s==null?"":s).replace(SUBRE, function(m, base, br, one){
    var body = (br==null?one:br).replace(/-/g,"−").replace(/,/g,",\u2009");
    return base + "<sub>" + body + "</sub>";
  });
};
/* 원고의 백틱은 <code> 로 조판한다. 짝이 맞는 것만 바꾸고 홀로 남은 것은 글자로 둔다. */
var codify = function(s){ return s.replace(/`([^`]*)`/g, "<code>$1</code>") };
var fmt = function(s){ return codify(subs(esc(s))) };

/* 고쳐 쓰는 칸을 되읽는다. 조판된 아래첨자는 원고 표기 `_i` · `_{d−1}` 로,
   <code> 는 백틱으로 되돌린다. 이 되돌림이 없으면 한 글자만 고쳐도 표기가 날아간다. */
function readField(el){
  var out = "";
  (function walk(node){
    for (var n = node.firstChild; n; n = n.nextSibling){
      if (n.nodeType === 3){ out += n.nodeValue; continue }
      if (n.nodeType !== 1) continue;
      if (n.tagName === "SUB"){
        var b = n.textContent.replace(/\u2009/g, "");
        out += (b === "i" || b === "r") ? "_" + b : "_{" + b + "}";
        continue;
      }
      if (n.tagName === "CODE"){ out += "`"; walk(n); out += "`"; continue }
      if (n.tagName === "BR"){ out += "\n"; continue }
      if (n.tagName === "DIV" || n.tagName === "P"){
        if (out && out.slice(-1) !== "\n") out += "\n";
        walk(n); continue;
      }
      walk(n);
    }
  })(el);
  return out;
}

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
  var fill = function(s){ return s.split(TK("SEED")).join(jsonFor(SEED)) };
  var b = new TextEncoder().encode(SRC), raw = "", CH = 0x8000;
  for (var i=0;i<b.length;i+=CH) raw += String.fromCharCode.apply(null, b.subarray(i,i+CH));
  return wrapFull(fill(before) + btoa(raw) + fill(after));
}

/* 조각에 껍데기를 씌운다. 생성기의 full() 과 같은 절차다. */
function wrapFull(frag){
  var m = /^\s*<title>([\s\S]*?)<\/title>\s*/.exec(frag);
  var title = m ? m[1] : "용어 기호 정리";
  var body = m ? frag.slice(m[0].length) : frag;
  return '<!doctype html>\n<html lang="ko">\n<head>\n'
       + '<meta charset="utf-8">\n'
       + '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
       + '<title>' + title + '</title>\n</head>\n<body>\n'
       + body + '\n</body>\n</html>\n';
}

/* ── 칸 하나를 SEED 에서 집고 놓는다 ───────────── */
var LB = %%LABELS%%;
var ROWF = ["formula","plain","alias"];

function locate(el){
  var d = el.dataset;
  if (d.g) return {get:function(){return SEED[d.g]},
                   set:function(t){SEED[d.g]=t}};
  if (d.r) return {get:function(){return SEED.rules[+d.j][d.r]},
                   set:function(t){SEED.rules[+d.j][d.r]=t}};
  if (d.s) return {get:function(){return SEED.scopes[+d.j][d.s]},
                   set:function(t){SEED.scopes[+d.j][d.s]=t}};
  if (d.f){
    var c = el.closest(".card"); if (!c) return null;
    var i = +c.dataset.i;
    return {get:function(){return SEED.vars[i][d.f]},
            set:function(t){SEED.vars[i][d.f]=t}};
  }
  return null;
}

/* ── 그리기 ───────────────────────────────── */
function aliasHTML(){
  var rs = SEED.vars.filter(function(v){ return v.alias });
  var h = '<div class="scroll"><table><thead><tr><th>기존 표기</th><th>바뀐 기호</th>'
        + '<th>용어 이름</th></tr></thead><tbody>';
  rs.forEach(function(v){
    h += '<tr><td class="n">'+fmt(v.alias)+'</td><td class="n">'+fmt(v.sym)
       + '</td><td>'+esc(v.term)+'</td></tr>';
  });
  return h + '</tbody></table></div>';
}

function cardHTML(v, i){
  var h = '<article class="card" id="v'+i+'" data-i="'+i+'"><div class="hd">';
  h += '<span class="no">'+String(i+1).padStart(2,"0")+'</span>';
  h += '<span class="fld"><span class="lb">'+LB.term+'</span>'
     + '<span class="t" contenteditable data-f="term" data-ph="'+LB.term+'">'
     + fmt(v.term)+'</span></span>';
  h += '<span class="fld"><span class="lb">'+LB.sym+'</span>'
     + '<span class="s" contenteditable data-f="sym" data-ph="'+LB.sym+'">'
     + fmt(v.sym)+'</span></span>';
  h += '<span class="ops">'
     + '<button data-act="up" title="위로">↑</button>'
     + '<button data-act="down" title="아래로">↓</button>'
     + '<button data-act="add" title="아래에 항목 추가">＋</button>'
     + '<button data-act="del" class="del" title="항목 삭제">✕</button>'
     + '</span></div>';

  var rows = "";
  ROWF.forEach(function(f){
    if (v[f] == null || v[f] === "") return;
    rows += '<div class="k">'+LB[f]
          + '<button data-act="rmf" data-f="'+f+'" title="이 줄 지우기">×</button></div>'
          + '<div class="v'+(f === "plain" ? "" : " mono")+'" contenteditable data-f="'+f+'">'
          + fmt(v[f])+'</div>';
  });
  if (rows) h += '<div class="rows">'+rows+'</div>';

  var miss = ROWF.filter(function(f){ return v[f] == null || v[f] === "" });
  if (miss.length){
    h += '<div class="addrow"><span class="ah">줄 추가</span>';
    miss.forEach(function(f){
      h += '<button data-act="addf" data-f="'+f+'">'+LB[f]+'</button>' });
    h += '</div>';
  }
  return h + '</article>';
}

function render(){
  var h = '<div class="head">';
  h += '<h2 contenteditable data-g="title" data-ph="제목">'+esc(SEED.title)+'</h2>';
  h += '<p class="sub" contenteditable data-g="basis" data-ph="근거">'+esc(SEED.basis)+'</p>';
  h += '<p class="asof">'+esc(SEED.asof)+'</p></div>';

  h += '<h2 class="sep">기존 표기 → 바뀐 기호<span>'
     + SEED.vars.filter(function(v){return v.alias}).length+'줄</span></h2>';
  h += '<div id="ali">'+aliasHTML()+'</div>';

  h += '<h2 class="sep">이름 짓는 규칙<span>'+SEED.rules.length+'개</span></h2>';
  SEED.rules.forEach(function(r, j){
    h += '<div class="rule"><span class="num">'+esc(r.n)+'</span>'
       + '<b contenteditable data-r="head" data-j="'+j+'" data-ph="규칙">'+fmt(r.head)+'</b>'
       + '<span class="bd" contenteditable data-r="body" data-j="'+j+'" data-ph="'+LB.plain+'">'
       + fmt(r.body)+'</span></div>';
  });

  h += '<h2 class="sep">범위<span>'+SEED.scopes.length+'개</span></h2>';
  h += '<div class="scroll"><table><thead><tr><th>표시</th><th>이름</th><th>'+LB.plain
     + '</th></tr></thead><tbody>';
  SEED.scopes.forEach(function(s, j){
    h += '<tr><td class="n">'+fmt(s.mark)+'</td>'
       + '<td contenteditable data-s="name" data-j="'+j+'" data-ph="이름">'+fmt(s.name)+'</td>'
       + '<td contenteditable data-s="def" data-j="'+j+'" data-ph="'+LB.plain+'">'
       + fmt(s["def"])+'</td></tr>';
  });
  h += '</tbody></table></div>';

  h += '<h2 class="sep">용어와 기호<span>'+SEED.vars.length+'항</span></h2>';
  SEED.vars.forEach(function(v, i){ h += cardHTML(v, i) });
  h += '<div class="newitem"><button class="btn" data-act="addend">＋ 맨 끝에 항목 추가</button></div>';

  $("#doc").innerHTML = h;
  toc();
  filter();
  selfcheck();
}

function toc(){
  var h = '<div class="grp">용어와 기호</div>';
  SEED.vars.forEach(function(v, i){
    h += '<a href="#v'+i+'"><span class="n">'+String(i+1).padStart(2,"0")
       + '</span><span>'+fmt(v.term)+'</span></a>';
  });
  $("#toc").innerHTML = h;
}

function filter(){
  var q = ($("#q").value || "").trim().toLowerCase();
  var n = 0;
  SEED.vars.forEach(function(v, i){
    var el = document.querySelector('.card[data-i="'+i+'"]');
    if (!el) return;
    var hay = [v.term, v.sym, v.formula, v.plain, v.alias].join(" ").toLowerCase();
    var show = !q || hay.indexOf(q) >= 0;
    el.classList.toggle("hide", !show);
    if (show) n++;
  });
  $("#cnt").textContent = n + " / " + SEED.vars.length + "항";
}

/* ── 왕복 시험 ───────────────────────────────
   조판된 칸을 그 자리에서 되읽어 원고 문자열과 견준다. 어긋난 칸 수를
   html[data-rt] 에 적는다. 저장이 만들 문서의 지문은 html[data-docsig] 에 적는다. */
function roundtrip(){
  var bad = [];
  var els = document.querySelectorAll("#doc [contenteditable]");
  for (var i=0;i<els.length;i++){
    var loc = locate(els[i]); if (!loc) continue;
    var want = loc.get(); want = (want == null ? "" : String(want));
    var got = readField(els[i]);
    if (got !== want) bad.push([els[i].dataset.f || els[i].dataset.g
                                || els[i].dataset.r || els[i].dataset.s, want, got]);
  }
  return bad;
}
function fnv(s){
  var h = 0x811c9dc5;
  for (var i=0;i<s.length;i++){
    h ^= s.charCodeAt(i);
    h = (h + ((h<<1) + (h<<4) + (h<<7) + (h<<8) + (h<<24))) >>> 0;
  }
  return ("0000000" + h.toString(16)).slice(-8);
}
function selfcheck(){
  var bad = roundtrip();
  document.documentElement.dataset.rt = String(bad.length);
  window.__rtbad = bad;
  var doc = renderDoc();
  document.documentElement.dataset.docsig = doc ? (fnv(doc) + ":" + doc.length) : "none";
}

/* ── 고치기 ───────────────────────────────── */
function say(t, cls){ var s = $("#st"); s.textContent = t; s.className = "state "+(cls||"") }
function mark(){
  if (!dirty){ dirty = true; $("#save").disabled = false }
  say("고친 것 있음", "on");
}

document.addEventListener("input", function(e){
  var el = e.target;
  if (!el.isContentEditable) return;
  var loc = locate(el); if (!loc) return;
  loc.set(readField(el));
  if (el.dataset.f === "alias" || el.dataset.f === "sym" || el.dataset.f === "term"){
    var a = $("#ali"); if (a) a.innerHTML = aliasHTML();
  }
  mark();
});

document.addEventListener("paste", function(e){
  if (!e.target.isContentEditable) return;
  e.preventDefault();
  document.execCommand("insertText", false,
    (e.clipboardData || window.clipboardData).getData("text/plain"));
});

function idx(el){ var c = el.closest(".card"); return c ? +c.dataset.i : -1 }

document.addEventListener("click", function(e){
  var b = e.target.closest("[data-act]");
  if (!b) return;
  var act = b.dataset.act, i = idx(b), a = SEED.vars;

  if (act === "up" || act === "down"){
    var j = act === "up" ? i-1 : i+1;
    if (j < 0 || j >= a.length) return;
    var t = a[i]; a[i] = a[j]; a[j] = t;
    mark(); render();
    var el = document.querySelector('.card[data-i="'+j+'"]');
    if (el) el.scrollIntoView({block:"center"});
    return;
  }
  if (act === "del"){
    if (!confirm("“"+(a[i].term || "이 항목")+"” 삭제")) return;
    a.splice(i,1); mark(); render(); return;
  }
  if (act === "add" || act === "addend"){
    var at = act === "add" ? i+1 : a.length;
    a.splice(at, 0, {term:"", sym:"", alias:null, kind:(a[i]||a[a.length-1]||{}).kind || "",
                     formula:null, plain:""});
    mark(); render();
    var ne = document.querySelector('.card[data-i="'+at+'"] [data-f="term"]');
    if (ne){ ne.scrollIntoView({block:"center"}); ne.focus() }
    return;
  }
  if (act === "addf"){
    a[i][b.dataset.f] = ""; mark(); render();
    var fe = document.querySelector('.card[data-i="'+i+'"] [data-f="'+b.dataset.f+'"]');
    if (fe){ fe.scrollIntoView({block:"center"}); fe.focus() }
    return;
  }
  if (act === "rmf"){ a[i][b.dataset.f] = null; mark(); render(); return }
});

/* ── 저장 ───────────────────────────────── */
$("#q").addEventListener("input", filter);

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
        say("저장 실패 · "+(c || "까닭 모름"), "bad");
      }
    }
  }
  if (dl){
    try {
      await dl.save({filename:"용어기호정리_편집판.html", data:doc});
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

window.__renderDoc = renderDoc;
window.__roundtrip = roundtrip;
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
  <input type="search" id="q" placeholder="용어·기호·산식 찾기" aria-label="찾기">
  <span class="state" id="cnt"></span>
  <span class="state" id="st"></span>
  <button class="btn pri" id="save">저장</button>
</header>

<div class="wrap">
  <nav class="toc" id="toc" aria-label="목차"></nav>
  <main id="doc"></main>
</div>

<script type="application/json" id="seed">%%SEED%%</script>
<script type="application/json" id="src">"%%SRC%%"</script>
<script>%%JS%%</script>
"""


def full(frag):
    """조각에 껍데기를 씌운다. 페이지 안 JS 의 wrapFull() 과 같은 절차다."""
    m = re.match(r"\s*<title>(.*?)</title>\s*", frag, re.S)
    title = m.group(1) if m else "용어 기호 정리"
    body = frag[m.end():] if m else frag
    return ("<!doctype html>\n<html lang=\"ko\">\n<head>\n"
            "<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
            "<title>" + title + "</title>\n</head>\n<body>\n"
            + body + "\n</body>\n</html>\n")


def js_source():
    """JS 안의 자리 두 곳을 채운다 — 아래첨자 정규식과 칸 이름."""
    return (JS_HEAD
            .replace("%%SUBRE%%", json.dumps(subscript.SUBRE.pattern))
            .replace("%%LABELS%%", js_json(LABELS)))


def build(seed):
    raw = (TEMPLATE
           .replace("%%CSS%%", CSS)
           .replace("%%JS%%", js_source())
           .replace("%%TITLE%%", html.escape(seed.get("title", "용어 기호 정리"))))

    cut = raw.index("%%SRC%%")
    before, after = raw[:cut], raw[cut + len("%%SRC%%"):]
    fill = lambda s: s.replace("%%SEED%%", js_json(seed))
    b64 = base64.b64encode(raw.encode("utf-8")).decode("ascii")
    return fill(before) + b64 + fill(after)


def rotate(outdir, stem):
    """최상위에 최신 한 벌만 둔다. 앞 판은 같은 폴더 이전판/ 으로 옮긴다."""
    moved = []
    if not os.path.isdir(outdir):
        return moved
    for f in sorted(os.listdir(outdir)):
        if f.startswith(stem + "_") and f.endswith(".html"):
            os.makedirs(PREV, exist_ok=True)
            dst = os.path.join(PREV, f)
            if os.path.exists(dst):
                os.remove(dst)
            shutil.move(os.path.join(outdir, f), dst)
            moved.append(f)
    return moved


def main():
    if not os.path.exists(SEED_PATH):
        sys.exit("원고 없음 — %s" % SEED_PATH)
    seed = json.load(io.open(SEED_PATH, encoding="utf-8"))

    frag = build(seed)
    page = full(frag)

    os.makedirs(OUTDIR, exist_ok=True)
    moved = rotate(OUTDIR, STEM)
    stamp = os.environ.get("FINALEDIT_STAMP") or datetime.now().strftime("%Y%m%d_%H%M")
    out = os.path.join(OUTDIR, "%s_%s.html" % (STEM, stamp))
    io.open(out, "w", encoding="utf-8").write(page)
    io.open(FRAG_PATH, "w", encoding="utf-8").write(frag)

    for p in (out, FRAG_PATH):
        print("%s  %.0fKB" % (p, os.path.getsize(p) / 1024))
    print("  용어 %d항 · 규칙 %d · 범위 %d · 기존 표기 %d줄"
          % (len(seed["vars"]), len(seed["rules"]), len(seed["scopes"]),
             sum(1 for v in seed["vars"] if v.get("alias"))))
    if moved:
        print("  이전판으로 옮김 %d개 — %s" % (len(moved), ", ".join(moved)))


if __name__ == "__main__":
    main()
