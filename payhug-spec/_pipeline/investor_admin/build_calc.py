#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""각 계산식이 나오는 화면 — 변수 정의 → 산식 → 대입 → 결과.

값은 ledger_facts.json 한 곳에서 온다. 이 스크립트는 배치만 한다.
산출 _pipeline/investor_admin/calc.fragment.html · payhug-investor-admin/calc.html
"""
import html, importlib.util, io, json, os
from decimal import Decimal as D, getcontext
getcontext().prec = 30
PIPE = os.path.dirname(os.path.abspath(__file__))
REPO = "/Users/semi/cursor/payhug-investor-admin"
e = lambda s: html.escape("" if s is None else str(s))
f = json.load(io.open(os.path.join(PIPE, "ledger_facts.json"), encoding="utf-8"))
t = f["tyByDate"]
DS = sorted(k for k in t if "2026-08-21" <= k <= "2026-08-27")
PA = sum(D(t[k][2]) for k in DS); PM = sum(D(t[k][3]) for k in DS)
PwD = sum(D(t[k][2]) * D(t[k][0]) for k in DS) / PA
PEC = D(f["weekPsc"]); EC = D(f["cash"]); EX = D(f["exec"])
r = D("0.0011"); wD = D(str(f["wRaw"]))
n = lambda x, p=0: ("{:,.%df}" % p).format(x)

# id, 갈래, 이름, 기호, 정의(변수), 대입, 결과, 설명
F = [
 ("f1","채권 한 건","i번째 채권의 투자 실행액","Aᵢ","Aᵢ = 순지급액ᵢ × (1 − r)",
  ["r = 0.0011", "순지급액ᵢ 는 매출에서 플랫폼 수수료를 뺀 금액"],
  "채권마다 다름", "투자자가 그 채권을 산 금액. 할인율만큼 깎아서 산다."),
 ("f2","채권 한 건","i번째 채권의 입금부족액","Lᵢ","Lᵢ = 미지급금ᵢ − 과지급금ᵢ", [],
  "채권마다 다름", "덜 들어온 쪽에서 더 들어온 쪽을 뺀다. 더 들어왔으면 음수가 된다."),
 ("f3","채권 한 건","i번째 채권의 투자수익","Mᵢ","Mᵢ = 채권매입수수료ᵢ − max(0, Lᵢ)", [],
  "채권마다 다름", "수수료에서 덜 들어온 만큼을 뺀다. max(0, …) 은 더 들어왔다고 수수료를 부풀리지 않게 막는 바닥이다."),
 ("f4","채권 한 건","i번째 채권의 상환액","Bᵢ","Bᵢ = 순지급액ᵢ − max(0, Lᵢ)", [],
  "채권마다 다름", "그 채권에서 실제로 돌아온 금액."),

 ("g1","투자 자산 화면","투자 실행액","Σ Aᵢ","Σ Aᵢ   (i 는 정산예정일이 아직 안 온 채권)",
  ["미회수 2,240건"], n(EX) + "원", "지금 채권으로 들고 있는 돈. 정산예정일이 온 것은 빠진다."),
 ("g2","투자 자산 화면","가중평균 금융일수","wD","wD = Σ (Aᵢ × Dᵢ) ÷ Σ Aᵢ",
  ["가중치 wᵢ = Aᵢ ÷ Σ Aᵢ  (합이 1)", "곧  wD = Σ wᵢ Dᵢ"],
  str(f["wRaw"]) + "일  (표기 " + str(f["w"]) + ")",
  "투자한 돈이 평균 며칠 묶여 있는지. 가중치가 건수가 아니라 금액이라 큰 채권의 날짜가 더 세게 반영된다."),
 ("g3","투자 자산 화면","예상 연회전수익률","Yr","Yr = r × 365 ÷ wD",
  ["365 ÷ %s = %s 번   ← 1년에 몇 번 굴리나" % (f["wRaw"], n(365/wD, 4)),
   "0.11%% × %s = %s%%" % (n(365/wD, 4), n(r*365/wD*100, 4))],
  str(f["ty"]) + "%", "분자에 실제로 번 수익률 대신 약속한 할인율을 넣어 재는 값이다."),
 ("g4","투자 자산 화면","입금부족률","LR","LR = Σ Lᵢ ÷ Σ Aᵢ   (i 는 선정산일이 d−20 ~ d−11 인 채권)",
  ["기준일 2026-08-27 → 표본 08-07 ~ 08-16"],
  str(f["sRaw"]) + "%  (표기 " + str(f["s"]) + "%)",
  "약속보다 덜 들어온 비율. 선정산일이 d−20 ~ d−11 인 열흘치 채권을 표본으로 잰다."),
 ("g5","투자 자산 화면","투자자산","Σ Aᵢ + EC","Σ Aᵢ + EC",
  ["%s + %s" % (n(EX), n(EC))], n(EX+EC) + "원",
  "채권과 현금을 합친 것. 화면 「합계」 행이다."),
 ("g6","투자 자산 화면","비중","—","투자실행액 ÷ 투자자산   ·   순현금 ÷ 투자자산",
  ["%s ÷ %s = %s%%" % (n(EX), n(EX+EC), n(EX/(EX+EC)*100,1)),
   "%s ÷ %s = %s%%" % (n(EC), n(EX+EC), n(EC/(EX+EC)*100,1))],
  "80.0% / 20.0%", "굴린 돈 중 채권으로 나간 몫과 놀고 있는 몫."),
]
d0 = "2026-08-27"; row = t[d0]
A1, M1, B1, wD1, y1 = D(row[2]), D(row[3]), D(row[4]), D(row[0]), row[1]
F += [
 ("h1","투자 수익 화면 · 일별 표  ·  " + d0, "투자실행금","A(d-1)","A(d-1) = Σ Aᵢ   (i ∈ d−1)",
  ["정산예정일이 그 날인 채권들을 모은다"], n(A1)+"원", "그 날 정산예정일이 온 채권들의 투자 실행액 합."),
 ("h2","투자 수익 화면 · 일별 표  ·  " + d0, "투자수익","M(d-1)","M(d-1) = Σ Mᵢ   (i ∈ d−1)",
  ["채권매입수수료 29,206 − 부족액 차감 20,445"], n(M1)+"원", "그 날 벌어들인 금액."),
 ("h3","투자 수익 화면 · 일별 표  ·  " + d0, "상환액","B(d-1)","B(d-1) = Σ Bᵢ   (i ∈ d−1)",
  ["순지급액 26,551,190 − 부족액 차감 20,445"], n(B1)+"원", "그 날 실제로 돌아온 금액."),
 ("h4","투자 수익 화면 · 일별 표  ·  " + d0, "투자수익율","MR(d-1)","MR(d-1) = M(d-1) ÷ A(d-1)",
  ["%s ÷ %s" % (n(M1), n(A1))], n(M1/A1*100, 6)+"%",
  "비율이라 더할 수 없다. 분자와 분모를 각각 더한 뒤 나눈다."),
 ("h5","투자 수익 화면 · 일별 표  ·  " + d0, "가중평균 금융일수","wD(d-1)","wD(d-1) = Σ (Aᵢ × Dᵢ) ÷ A(d-1)   (i ∈ d−1)",
  [], str(row[0])+"일", "그 하루 몫만 놓고 잰 것."),
 ("h6","투자 수익 화면 · 일별 표  ·  " + d0, "일별 연회전수익률","YMR(d-1)","YMR(d-1) = MR(d-1) × 365 ÷ wD(d-1)",
  ["%s%% × 365 ÷ %s" % (n(M1/A1*100, 6), row[0]),
   "= %s%%" % n(M1/A1*365/wD1*100, 6)], str(y1)+"%",
  "그 하루의 실적치. 분자가 약속한 할인율이 아니라 실제로 번 수익률이다."),
]
PMR = PM/PA; PYMR = PMR*365/PwD; share = PA/(PA+PEC)
F += [
 ("p1","투자 수익 화면 · 기간 현황  ·  08-21 ~ 08-27","투자실행금","PA","PA = Σ A(d-1)   (기간 안 레코드 전부)",
  ["7일치를 더한다"], n(PA)+"원", None),
 ("p2","투자 수익 화면 · 기간 현황  ·  08-21 ~ 08-27","투자수익","PM","PM = Σ M(d-1)", [], n(PM)+"원", None),
 ("p3","투자 수익 화면 · 기간 현황  ·  08-21 ~ 08-27","투자수익율","PMR","PMR = PM ÷ PA",
  ["%s ÷ %s" % (n(PM), n(PA))], n(PMR*100, 6)+"%",
  "행별 수익율을 평균 내지 않는다. 재료를 다시 모아 한 번에 낸다."),
 ("p4","투자 수익 화면 · 기간 현황  ·  08-21 ~ 08-27","가중평균 금융일수","PwD","PwD = Σ (Aᵢ × Dᵢ) ÷ PA   (i ∈ P)",
  [], n(PwD, 6)+"일", None),
 ("p5","투자 수익 화면 · 기간 현황  ·  08-21 ~ 08-27","순현금","PEC","PEC = Σ EC(d-1)",
  ["%s × 7일" % n(EC)], n(PEC)+"원",
  "날마다의 잔액을 기간만큼 더한다. 7일을 고르면 순현금이 7번 들어간다."),
 ("p6","투자 수익 화면 · 기간 현황  ·  08-21 ~ 08-27","투자실행금액 대비 연회전수익률","PYMR","PYMR = PMR × 365 ÷ PwD",
  ["365 ÷ %s = %s 번" % (n(PwD,6), n(365/PwD,4)),
   "%s%% × %s = %s%%" % (n(PMR*100,6), n(365/PwD,4), n(PYMR*100,6))],
  n(PYMR*100,6)+"%   화면 3.99%", "채권으로 나간 돈만 놓고 잰 수익률."),
 ("p7","투자 수익 화면 · 기간 현황  ·  08-21 ~ 08-27","투자자산 대비 연회전수익률","wPYMR","wPYMR = PYMR × PA ÷ (PA + PEC)",
  ["가중치 w = PA ÷ (PA + PEC) = %s ÷ %s = %s" % (n(PA), n(PA+PEC), n(share,6)),
   "%s%% × %s = %s%%" % (n(PYMR*100,6), n(share,6), n(PYMR*share*100,6))],
  n(PYMR*share*100,6)+"%   화면 2.24%",
  "놀고 있는 현금까지 분모에 넣어 다시 잰 것. 굴린 돈 중 %s%% 만 일하므로 그만큼 깎인다." % n(share*100,2)),
]

CHAIN = [
 ("연환산 수익금으로 되돌리면", [
   "PM × (365 ÷ PwD) = %s × %s = %s원" % (n(PM), n(365/PwD,4), n(PM*365/PwD)),
   "PYMR  = %s ÷ PA        = %s%%" % (n(PM*365/PwD), n(PM*365/PwD/PA*100,6)),
   "wPYMR = %s ÷ (PA+PEC) = %s%%" % (n(PM*365/PwD), n(PM*365/PwD/(PA+PEC)*100,6)),
   "→ 같은 분자를 다른 분모로 나눈 것이다"]),
 ("행별 수익율을 평균 내면 틀린다", [
   "일별 7개 단순평균 = %s%%" % n(sum(D(t[k][1]) for k in DS)/len(DS), 6),
   "원장이 내는 값     = %s%%" % n(PYMR*100, 6),
   "→ 비율은 평균 낼 수 없다"]),
]

CSS = open(os.path.join(PIPE, "build_final.py")).read().split('CSS = """')[1].split('"""')[0]
CSS += """
.fx-def{margin:9px 0 0;padding:11px 14px;background:var(--sunk);border-radius:8px;
 font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:13px;line-height:1.75;
 white-space:pre-wrap;overflow-x:auto;border-left:3px solid var(--accent)}
.sub{margin:9px 0 0;padding:0;list-style:none}
.sub li{padding:5px 0 5px 22px;position:relative;font-family:"IBM Plex Mono",ui-monospace,monospace;
 font-size:12.5px;color:var(--mute);line-height:1.65}
.sub li::before{content:"↓";position:absolute;left:4px;color:var(--accent);font-family:inherit}
.res{margin:10px 0 0;padding:9px 13px;border-radius:8px;background:var(--accent-soft);
 font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:13.5px;font-weight:600;color:var(--accent)}
.grp{margin:34px 0 4px;padding-top:20px;border-top:2px solid var(--rule-hard);
 font-family:"Noto Serif KR",serif;font-size:19px;font-weight:700}
"""

def build():
    o = ['<title>계산식 하나씩</title>',
      '<style>@import url("https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=Noto+Serif+KR:wght@400;700&family=IBM+Plex+Mono:wght@400;500&display=swap");',
      CSS, "</style>", '<div class="wrap">',
      '<h1>계산식 하나씩</h1>',
      '<p class="meta">변수 정의 → 산식 → 대입 → 결과 · 기준일 2026-08-27 · 조회기간 2026-08-21 ~ 08-27</p>']
    seen = set()
    for fid, grp, name, sym, define, subs, res, note in F:
        if grp not in seen:
            seen.add(grp); o.append('<h2 class="grp">%s</h2>' % e(grp))
        o.append('<div class="v"><div class="hd"><span class="t">%s</span><span class="s">%s</span></div>'
                 % (e(name), e(sym)))
        o.append('<div class="fx-def">%s</div>' % e(define))
        if subs:
            o.append("<ul class='sub'>" + "".join("<li>%s</li>" % e(s) for s in subs) + "</ul>")
        o.append('<div class="res">= %s</div>' % e(res))
        if note: o.append('<p class="p">%s</p>' % e(note))
        o.append("</div>")
    o.append('<h2 class="grp">이어 보기</h2>')
    for head, lines in CHAIN:
        o.append('<div class="v"><div class="hd"><span class="t">%s</span></div>' % e(head))
        o.append('<div class="fx-def">%s</div></div>' % e("\n".join(lines)))
    o.append("</div>")
    return "".join(o)

frag = build()
spec = importlib.util.spec_from_file_location("bt", os.path.join(PIPE,"build_termsedit.py"))
bt = importlib.util.module_from_spec(spec); spec.loader.exec_module(bt)
fp = os.path.join(PIPE,"calc.fragment.html"); hp = os.path.join(REPO,"calc.html")
io.open(fp,"w",encoding="utf-8").write(frag)
io.open(hp,"w",encoding="utf-8").write(bt.full(frag))
for p in (fp,hp): print("%s  %.0fKB" % (p, os.path.getsize(p)/1024))
print("  산식 %d개" % len(F))
