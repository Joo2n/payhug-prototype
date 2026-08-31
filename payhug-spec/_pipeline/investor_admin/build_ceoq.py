#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""대표님 확인 20문 — 답을 적어 저장하면 같은 주소가 새 판이 되는 화면.

앞판은 답을 브라우저에만 담아서 Claude 가 가져올 수 없었다. 이 판은 답을
페이지 원고에 담아 새 판으로 게시하므로, Claude 가 그 주소를 읽어 답을 그대로
집어 온다.

자기 원본을 base64 로 품고 있다가 저장할 때 원고만 갈아 끼우는 방식은
build_termsedit.py 와 같다. 껍데기 씌우기와 JSON 직렬화도 그 파일 것을 그대로
쓴다 — 두 벌을 만들면 어긋난다.

산출
  _pipeline/investor_admin/ceoq.fragment.html   아티팩트 게시용 조각
  payhug-investor-admin/ceo-questions.html      완전한 문서
"""

import base64
import importlib.util
import json
import os
import sys
from datetime import date

PIPE = os.path.dirname(os.path.abspath(__file__))
SEED = os.path.join(PIPE, "ceoq_seed.json")
REPO = "/Users/semi/cursor/payhug-investor-admin"
OUTDIR = os.path.expanduser("~/Downloads/payhug_용어정의서")

_spec = importlib.util.spec_from_file_location("bt", os.path.join(PIPE, "build_termsedit.py"))
_bt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_bt)
full, js_json = _bt.full, _bt.js_json


CSS = r"""
:root{
  --bg:#FAF9F7; --surface:#FFFFFF; --sunk:#F4F2ED;
  --ink:#1B1A17; --mute:#6B6862; --faint:#9490879e;
  --rule:#E5E1D9; --rule-hard:#CFC9BD;
  --accent:#2C4470; --accent-soft:#2C447014;
  --stop:#8A3143; --stop-soft:#8A314314;
  --ask:#9C6212; --ask-soft:#9C621214;
  --ok:#2F6046;
  --shadow:0 1px 2px #1b1a1710, 0 10px 26px #1b1a170a;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#16161A; --surface:#1D1E23; --sunk:#22242A;
  --ink:#ECEAE5; --mute:#9B978E; --faint:#77736b9e;
  --rule:#2E3038; --rule-hard:#3D4048;
  --accent:#93AEE0; --accent-soft:#93AEE01F;
  --stop:#E08594; --stop-soft:#E0859420;
  --ask:#E0A64A; --ask-soft:#E0A64A20;
  --ok:#6FBF95;
  --shadow:0 1px 2px #00000040, 0 10px 26px #00000030;
}}
:root[data-theme="dark"]{
  --bg:#16161A; --surface:#1D1E23; --sunk:#22242A;
  --ink:#ECEAE5; --mute:#9B978E; --faint:#77736b9e;
  --rule:#2E3038; --rule-hard:#3D4048;
  --accent:#93AEE0; --accent-soft:#93AEE01F;
  --stop:#E08594; --stop-soft:#E0859420;
  --ask:#E0A64A; --ask-soft:#E0A64A20;
  --ok:#6FBF95;
  --shadow:0 1px 2px #00000040, 0 10px 26px #00000030;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:"Noto Sans KR",-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo",sans-serif;
  font-size:15px;line-height:1.75;-webkit-font-smoothing:antialiased}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:4px}

.bar{position:sticky;top:0;z-index:30;display:flex;align-items:center;gap:10px;
  flex-wrap:wrap;padding:10px 20px;border-bottom:1px solid var(--rule);
  background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:blur(10px)}
.bar h1{margin:0;font-family:"Noto Serif KR",serif;font-size:16px;font-weight:700;white-space:nowrap}
.bar .sp{flex:1}
.btn{font:inherit;font-size:13px;line-height:1;cursor:pointer;padding:8px 12px;
  border-radius:7px;border:1px solid var(--rule-hard);background:var(--surface);color:var(--ink)}
.btn:hover{border-color:var(--accent);color:var(--accent)}
.btn.pri{background:var(--accent);border-color:var(--accent);color:var(--bg);font-weight:600}
.btn.pri:hover{filter:brightness(1.12);color:var(--bg)}
.btn[disabled]{opacity:.45;cursor:default}
.st{font-size:12px;color:var(--mute);white-space:nowrap}
.st.on{color:var(--ask)} .st.ok{color:var(--ok)} .st.bad{color:var(--stop)}

.wrap{max-width:880px;margin:0 auto;padding:26px 20px 110px}
header h1{margin:0 0 4px;font-family:"Noto Serif KR",serif;font-size:31px;
  font-weight:700;letter-spacing:-.02em;text-wrap:balance}
header .when{color:var(--mute);font-size:13.5px;margin:0 0 18px}
.tally{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:1px;
  background:var(--rule);border:1px solid var(--rule);border-radius:10px;overflow:hidden}
.tally div{background:var(--surface);padding:12px 14px}
.tally dt{font-size:11px;letter-spacing:.06em;color:var(--mute);margin:0 0 3px}
.tally dd{margin:0;font-size:19px;font-weight:700;font-variant-numeric:tabular-nums}
.tally dd small{font-size:12px;font-weight:400;color:var(--mute);margin-left:3px}
.tally .s dd{color:var(--stop)} .tally .d dd{color:var(--ok)}
.memo{margin-top:14px}
.memo label{display:block;font-size:11px;letter-spacing:.06em;color:var(--mute);margin-bottom:4px}

h2.grp{margin:36px 0 2px;padding-top:20px;border-top:2px solid var(--rule-hard);
  font-family:"Noto Serif KR",serif;font-size:21px;font-weight:700}
p.why{margin:2px 0 12px;color:var(--mute);font-size:13.5px}

.q{background:var(--surface);border:1px solid var(--rule);border-radius:11px;
  margin:12px 0;box-shadow:var(--shadow);overflow:hidden;scroll-margin-top:64px}
.q.stop{border-left:4px solid var(--stop)}
.q.ask{border-left:4px solid var(--ask)}
.q.done{opacity:.62}
.q .hd{display:flex;align-items:center;gap:9px;flex-wrap:wrap;padding:13px 16px 0}
.q .id{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:12px;font-weight:600;
  color:var(--accent);background:var(--accent-soft);padding:2px 8px;border-radius:5px}
.tag{font-size:10.5px;font-weight:700;letter-spacing:.06em;padding:3px 8px;
  border-radius:20px;border:1px solid currentColor}
.tag.stop{color:var(--stop);background:var(--stop-soft)}
.tag.ask{color:var(--ask);background:var(--ask-soft)}
.q .topic{font-size:13px;color:var(--mute)}
.q .chk{margin-left:auto;display:flex;align-items:center;gap:5px;font-size:11.5px;
  color:var(--mute);cursor:pointer;user-select:none}
.q .chk input{accent-color:var(--accent);width:15px;height:15px;cursor:pointer}
.say{margin:9px 16px 0;padding:12px 15px;background:var(--sunk);
  border-left:3px solid var(--rule-hard);border-radius:0 8px 8px 0;
  font-family:"Noto Serif KR",serif;font-size:15px;line-height:1.75}
.body{padding:11px 16px 15px}
.rows{display:grid;grid-template-columns:64px minmax(0,1fr);gap:1px;background:var(--rule);
  border:1px solid var(--rule);border-radius:8px;overflow:hidden;margin-bottom:11px}
.rows .k{background:var(--sunk);padding:8px 11px;font-size:11.5px;font-weight:700;color:var(--mute)}
.rows .v{background:var(--surface);padding:8px 12px;font-size:13.5px;min-width:0}
label.al{display:block;font-size:11px;letter-spacing:.06em;color:var(--mute);margin-bottom:4px}
textarea{width:100%;min-height:56px;resize:vertical;font:inherit;font-size:13.5px;
  padding:9px 11px;border-radius:8px;border:1px dashed var(--rule-hard);
  background:var(--bg);color:var(--ink);line-height:1.6}
textarea:focus{outline:none;border-style:solid;border-color:var(--accent)}
textarea::placeholder{color:var(--faint)}
textarea.filled{border-style:solid;border-color:var(--ok)}

@media print{.bar{display:none}.q{break-inside:avoid;box-shadow:none}
  textarea{border-style:solid;min-height:46px}}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
"""


JS = r"""
(function(){
"use strict";
var SEED = JSON.parse(document.getElementById("seed").textContent);
var SRC = null, dirty = false, pub = null;
var $ = function(s){return document.querySelector(s)};
var esc = function(s){return String(s==null?"":s)
  .replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")};

function b64dec(s){
  var bin = atob(s), b = new Uint8Array(bin.length);
  for (var i=0;i<bin.length;i++) b[i] = bin.charCodeAt(i);
  return new TextDecoder().decode(b);
}
/* #src 는 JSON 문자열 하나다. 따옴표째 넘기면 그 자리에서 깨진다. */
try { SRC = b64dec(JSON.parse(document.getElementById("src").textContent)); }
catch(e){ SRC = null; }

var TK = function(n){ return "%"+"%" + n + "%"+"%" };

function wrapFull(frag){
  var m = /^\s*<title>([\s\S]*?)<\/title>\s*/.exec(frag);
  var t = m ? m[1] : "확인 문항";
  var body = m ? frag.slice(m[0].length) : frag;
  return '<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n'
       + '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
       + '<title>' + t + '</title>\n</head>\n<body>\n' + body + '\n</body>\n</html>\n';
}
function renderDoc(){
  if (!SRC) return null;
  var cut = SRC.indexOf(TK("SRC"));
  if (cut < 0) return null;
  var before = SRC.slice(0, cut), after = SRC.slice(cut + TK("SRC").length);
  var fill = function(s){ return s.split(TK("SEED")).join(
    JSON.stringify(SEED).split("</").join("<\\/")) };
  var b = new TextEncoder().encode(SRC), raw = "", CH = 0x8000;
  for (var i=0;i<b.length;i+=CH) raw += String.fromCharCode.apply(null, b.subarray(i,i+CH));
  return wrapFull(fill(before) + btoa(raw) + fill(after));
}

function render(){
  var h = '<header><h1>' + esc(SEED.title) + '</h1>'
        + '<p class="when">' + esc(SEED.when) + ' · ' + esc(SEED.basis) + '</p>';
  var st = SEED.items.filter(function(x){return x.prio==="stop"}).length;
  var dn = SEED.items.filter(function(x){return (x.answer||"").trim()}).length;
  h += '<dl class="tally">'
     + '<div class="s"><dt>먼저 답 없으면 못 감</dt><dd>'+st+'<small>문</small></dd></div>'
     + '<div><dt>확인만 받으면 됨</dt><dd>'+(SEED.items.length-st)+'<small>문</small></dd></div>'
     + '<div class="d"><dt>답 받음</dt><dd id="dn">'+dn+'<small> / '+SEED.items.length+'</small></dd></div>'
     + '<div><dt>묶음</dt><dd>5<small>덩어리</small></dd></div></dl>';
  h += '<div class="memo"><label>미팅 메모</label>'
     + '<textarea data-memo placeholder="회의 중 남길 것">'+esc(SEED.note)+'</textarea></div>';
  h += '</header>';

  var seen = {};
  SEED.items.forEach(function(it, i){
    if (!seen[it.grp]){
      seen[it.grp] = 1;
      h += '<h2 class="grp">'+esc(it.grp_name)+'</h2><p class="why">'+esc(it.grp_why)+'</p>';
    }
    var filled = (it.answer||"").trim() ? " done" : "";
    h += '<article class="q '+it.prio+(it.done?" done":"")+'" id="'+it.id+'" data-i="'+i+'">'
       + '<div class="hd"><span class="id">'+esc(it.id)+'</span>'
       + '<span class="tag '+it.prio+'">'+(it.prio==="stop"?"먼저 답 필요":"확인")+'</span>'
       + '<span class="topic">'+esc(it.topic)+'</span>'
       + '<label class="chk"><input type="checkbox" data-done'+(it.done?" checked":"")+'>물었음</label>'
       + '</div><p class="say">'+esc(it.say)+'</p><div class="body">';
    if (it.rows && it.rows.length){
      h += '<div class="rows">';
      it.rows.forEach(function(r){
        h += '<div class="k">'+esc(r[0])+'</div><div class="v">'+esc(r[1])+'</div>';
      });
      h += '</div>';
    }
    h += '<label class="al">대표님 답</label>'
       + '<textarea data-ans class="'+((it.answer||"").trim()?"filled":"")
       + '" placeholder="여기에 적고 저장을 누르면 Claude 가 그대로 읽어 갑니다">'
       + esc(it.answer) + '</textarea></div></article>';
  });
  $("#doc").innerHTML = h;
}

function mark(){ if (dirty) return; dirty = true; say("적은 것 있음","on"); $("#save").disabled = !pub; }
function say(t, c){ var s = $("#st"); s.textContent = t; s.className = "st " + (c||""); }

document.addEventListener("input", function(e){
  var t = e.target;
  if (t.hasAttribute && t.hasAttribute("data-memo")){ SEED.note = t.value; mark(); return }
  if (t.hasAttribute && t.hasAttribute("data-ans")){
    var c = t.closest(".q");
    SEED.items[+c.dataset.i].answer = t.value;
    t.classList.toggle("filled", !!t.value.trim());
    var n = SEED.items.filter(function(x){return (x.answer||"").trim()}).length;
    var d = document.getElementById("dn");
    if (d) d.innerHTML = n + '<small> / ' + SEED.items.length + '</small>';
    mark();
  }
});
document.addEventListener("change", function(e){
  if (!e.target.hasAttribute || !e.target.hasAttribute("data-done")) return;
  var c = e.target.closest(".q");
  SEED.items[+c.dataset.i].done = e.target.checked;
  c.classList.toggle("done", e.target.checked);
  mark();
});
document.addEventListener("paste", function(e){
  if (e.target.tagName !== "TEXTAREA") return;
  e.preventDefault();
  document.execCommand("insertText", false,
    (e.clipboardData || window.clipboardData).getData("text/plain"));
});

$("#save").addEventListener("click", async function(){
  var doc = renderDoc();
  if (!doc){ say("원본 회수 실패 · 저장 불가","bad"); return }
  if (!pub){ say("이 사본에서는 저장 불가","bad"); return }
  $("#save").disabled = true;
  say("저장하는 중","on");
  try {
    await pub.publish(doc);
    dirty = false; say("저장됨 · Claude 가 읽어 갈 수 있음","ok");
  } catch(err){
    var c = err && err.code;
    if (c === "conflict"){ say("다른 판이 먼저 저장됨 · 최신 판으로 다시 엶","on"); return }
    if (c === "not_writer" || c === "not_granted" || c === "not_declared"){
      pub = null; say("읽기 전용 · 이 주소에는 저장 불가","bad");
    } else { say("저장 실패 · "+(c||"까닭 모름"),"bad") }
    $("#save").disabled = false;
  }
});
window.addEventListener("beforeunload", function(e){ if (dirty){ e.preventDefault(); e.returnValue = "" } });

window.__renderDoc = renderDoc;
window.__seed = SEED;

render();
$("#save").disabled = true;
say(SRC ? "" : "원본 회수 실패 · 저장 불가", SRC ? "" : "bad");
if (window.claude && window.claude.use){
  claude.use("artifact").then(function(a){
    pub = a;
    if (a) { $("#save").disabled = !dirty; say(dirty ? "적은 것 있음" : "저장 가능", dirty ? "on" : ""); }
    else say("이 사본에서는 저장 불가","bad");
  }).catch(function(){});
}
})();
"""


TEMPLATE = """<title>%%TITLE%%</title>
<style>@import url("https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=Noto+Serif+KR:wght@400;700&family=IBM+Plex+Mono:wght@400;500&display=swap");
%%CSS%%</style>

<div class="bar">
  <h1>%%TITLE%%</h1>
  <span class="sp"></span>
  <span class="st" id="st"></span>
  <button class="btn pri" id="save">저장</button>
</div>

<div class="wrap"><main id="doc"></main></div>

<script type="application/json" id="seed">%%SEED%%</script>
<script type="application/json" id="src">"%%SRC%%"</script>
<script>%%JS%%</script>
"""


def build(seed):
    raw = (TEMPLATE.replace("%%CSS%%", CSS).replace("%%JS%%", JS)
           .replace("%%TITLE%%", seed.get("title", "확인 문항")))
    cut = raw.index("%%SRC%%")
    before, after = raw[:cut], raw[cut + len("%%SRC%%"):]
    fill = lambda s: s.replace("%%SEED%%", js_json(seed))
    return fill(before) + base64.b64encode(raw.encode("utf-8")).decode("ascii") + fill(after)


def main():
    if not os.path.exists(SEED):
        sys.exit("원고 없음 — %s" % SEED)
    with open(SEED, encoding="utf-8") as f:
        seed = json.load(f)
    frag = build(seed)
    page = full(frag)
    os.makedirs(OUTDIR, exist_ok=True)
    stamp = os.environ.get("TERMSDOC_STAMP") or date.today().strftime("%Y%m%d")
    out = [(os.path.join(PIPE, "ceoq.fragment.html"), frag),
           (os.path.join(REPO, "ceo-questions.html"), page),
           (os.path.join(OUTDIR, "대표님확인20문_%s.html" % stamp), page)]
    for p, body in out:
        with open(p, "w", encoding="utf-8") as f:
            f.write(body)
        print("%s  %.0fKB" % (p, os.path.getsize(p) / 1024))
    print("  문항 %d · 답 적힌 것 %d"
          % (len(seed["items"]), sum(1 for i in seed["items"] if (i.get("answer") or "").strip())))


if __name__ == "__main__":
    main()
