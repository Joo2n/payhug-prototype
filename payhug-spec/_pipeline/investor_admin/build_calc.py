#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""각 계산식이 나오는 화면 — 변수 정의 → 산식 → 대입 → 결과.

값은 ledger_facts.json 한 곳에서 온다. 이 스크립트는 배치만 한다.
산출 _pipeline/investor_admin/calc.fragment.html · payhug-investor-admin/calc.html
"""
import html, importlib.util, io, json, os, sys
from decimal import Decimal as D, getcontext, ROUND_HALF_UP
getcontext().prec = 30
PIPE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PIPE)
import alias_table, testcase_table
import daily_ledger as L
from subscript import subs as sub_
REPO = "/Users/semi/cursor/payhug-investor-admin"
e = lambda s: sub_(html.escape("" if s is None else str(s)))
f = json.load(io.open(os.path.join(PIPE, "ledger_facts.json"), encoding="utf-8"))
t = f["tyByDate"]
DS = sorted(k for k in t if f["weekFrom"] <= k <= f["weekTo"])
PA = D(f["weekExec"]); PM = D(f["weekProfit"])
# 비율·일수는 소수 여섯째 자리까지 남긴 값을 다음 계산에 넣는다(dm_0901 규칙 1).
# PwD 는 원장이 낸 여섯 자리 값을 그대로 읽는다 — 여기서 다시 만들지 않는다.
PwD = D(f["weekWRaw"])
PEC = D(f["weekPsc"]); EC = D(f["cash"]); EX = D(f["exec"])
r = D("0.0011"); wD = D(str(f["wRaw"]))
n = lambda x, p=0: ("{:,.%df}" % p).format(x)
# 비율·일수는 소수 일곱째 자리에서 반올림해 여섯째 자리까지 남긴다 — daily_ledger.r6 와 같은 규칙.
q6 = lambda x: D(x).quantize(D("0.000001"), rounding=ROUND_HALF_UP)
LROW = dict((x["d"], x) for x in L.LEDGER)

# 낱건 대입값 — 테스트 케이스 1번 채권 (골목냉면 M2026-0008 · 카드사 · 정산예정일 2026-08-21)
TC1 = testcase_table.facts()["rec"][0]
TCM = testcase_table.facts()["tc"]["meta"]
TCH = "%s(%s) · %s · 정산예정일 %s · 순지급액 %s원" % (
    TCM["가맹점"], TCM["가맹점ID"], TC1["플랫폼"], TC1["정산예정일"], n(D(TC1["순지급액"])))

# id, 갈래, 이름, 기호, 정의(변수), 대입, 결과, 설명
F = [
 ("f1","채권 한 건","i번째 채권의 투자 실행액","A_i","A_i = 순지급액_i × (1 − r)",
  ["r = 0.0011", "순지급액_i 는 매출에서 플랫폼 수수료를 뺀 금액",
   "%s → 반올림( %s × 0.9989 )" % (TCH, n(D(TC1["순지급액"])))],
  n(D(TC1["Ai"]))+"원", "투자자가 그 채권을 산 금액. 할인율만큼 깎아서 산다."),
 ("f2","채권 한 건","i번째 채권의 입금부족액","L_i","L_i = 미지급금_i − 과지급금_i",
  ["%s → %s − %s" % (TCH, n(D(TC1["미지급금"])), n(D(TC1["과지급금"])))],
  n(D(TC1["Li"]))+"원", "덜 들어온 쪽에서 더 들어온 쪽을 뺀다. 더 들어왔으면 음수가 된다."),
 ("f3","채권 한 건","i번째 채권의 투자수익","M_i","M_i = 채권매입수수료_i − max(0, L_i)",
  ["%s → %s − %s" % (TCH, n(D(TC1["채권매입수수료"])), n(D(TC1["차감액"])))],
  n(D(TC1["Mi"]))+"원", "수수료에서 덜 들어온 만큼을 뺀다. max(0, …) 은 더 들어왔다고 수수료를 부풀리지 않게 막는 바닥이다."),
 ("f4","채권 한 건","i번째 채권의 상환액","B_i","B_i = 순지급액_i − max(0, L_i)",
  ["%s → %s − %s" % (TCH, n(D(TC1["순지급액"])), n(D(TC1["차감액"])))],
  n(D(TC1["Bi"]))+"원", "그 채권에서 실제로 돌아온 금액."),

 ("g1","투자 자산 화면","투자 실행액","Σ A_i","( Σ A_i )      i 는 정산예정일이 아직 안 온 채권",
  ["미회수 2,240건"], n(EX) + "원", "지금 채권으로 들고 있는 돈. 정산예정일이 온 것은 빠진다."),
 ("g2","투자 자산 화면","가중평균 금융일수","wD","wD = ( Σ A_i × D_i ) ÷ ( Σ A_i )      i 는 대상정산금채권 전체 61,760건 · 발생 기준",
  ["가중치 w_i = A_i ÷ ( Σ A_i )  (합이 1)", "곧  wD = Σ w_i D_i"],
  str(f["wRaw"]) + "일  (표기 " + str(f["w"]) + ")",
  "투자한 돈이 평균 며칠 묶여 있는지. 가중치가 건수가 아니라 금액이라 큰 채권의 날짜가 더 세게 반영된다. 옆 칸 투자 실행액은 미회수만 세지만 이 값은 발생한 채권 전체를 센다."),
 ("g3","투자 자산 화면","예상 연환산수익률","Y_r","Y_r = r × 365 ÷ wD   (분모는 소수 여섯째 자리까지 남긴 값)",
  ["365 ÷ %s = %s 번   ← 1년에 몇 번 굴리나" % (f["wRaw"], n(365/wD, 4)),
   "0.11%% × %s = %s%%" % (n(365/wD, 4), n(r*365/wD*100, 4))],
  str(f["ty"]) + "%", "분자에 실제로 번 수익률 대신 약속한 할인율을 넣어 재는 값이다."),
 ("g4","투자 자산 화면","입금부족률","LR","LR = ( Σ L_i ) ÷ ( Σ A_i )      i 는 선정산일이 d−20 ~ d−11 인 채권",
  ["기준일 %s → 표본 %s ~ %s" % (f["asof"], f["sampleSpan"][0][5:], f["sampleSpan"][1][5:])],
  str(f["sRaw"]) + "%  (표기 " + str(f["s"]) + "%)",
  "약속보다 덜 들어온 비율. 선정산일이 d−20 ~ d−11 인 열흘치 채권을 표본으로 잰다."),
 ("g5","투자 자산 화면","투자자산","Σ A_i + EC","( Σ A_i ) + EC",
  ["%s + %s" % (n(EX), n(EC))], n(EX+EC) + "원",
  "채권과 현금을 합친 것. 화면 「합계」 행이다."),
 ("g6","투자 자산 화면","비중","—","투자실행액 ÷ 투자자산   ·   순현금 ÷ 투자자산",
  ["%s ÷ %s = %s%%" % (n(EX), n(EX+EC), n(EX/(EX+EC)*100,1)),
   "%s ÷ %s = %s%%" % (n(EC), n(EX+EC), n(EC/(EX+EC)*100,1))],
  "80.0% / 20.0%", "굴린 돈 중 채권으로 나간 몫과 놀고 있는 몫."),
]
d0 = f["lastDue"]; row = t[d0]; lg = LROW[d0]   # 일별 표 마지막 행(기준일 전날)
A1, M1, B1, y1 = D(row[2]), D(row[3]), D(row[4]), row[1]
wD1 = D(lg["w6"])                      # 계산에 쓰는 여섯 자리 값
# MR 도 비율이라 백분율 소수 여섯째 자리에서 끊고 그 값을 다음 계산에 넣는다
# (dm_0901 규칙 1 · daily_ledger.TY6_EXPR 과 같은 꼴).
MR1 = q6(M1 / A1 * D(100)); Y1 = q6(MR1 * D(365) / wD1)
NET1 = D(lg["repay"] + lg["ded"]); DED1 = D(lg["ded"]); FEE1 = D(lg["fee"])
F += [
 ("h1","투자 수익 화면 · 일별 표  ·  " + d0, "투자실행금","A_{d−1}","A_{d−1} = ( Σ A_i )      i ∈ d−1",
  ["정산예정일이 그 날인 채권들을 모은다"], n(A1)+"원", "그 날 정산예정일이 온 채권들의 투자 실행액 합."),
 ("h2","투자 수익 화면 · 일별 표  ·  " + d0, "투자수익","M_{d−1}","M_{d−1} = ( Σ M_i )      i ∈ d−1",
  ["채권매입수수료 %s − 부족액 차감 %s" % (n(FEE1), n(DED1))], n(M1)+"원", "그 날 벌어들인 금액."),
 ("h3","투자 수익 화면 · 일별 표  ·  " + d0, "상환액","B_{d−1}",
  "B_{d−1} = ( Σ 순지급액_i ) − ( Σ max(0, L_i) )      i ∈ d−1",
  ["순지급액 %s − 부족액 차감 %s" % (n(NET1), n(DED1))], n(B1)+"원",
  "그 날 실제로 돌아온 금액. A_{d−1} + M_{d−1} 로 나눠 더하면 원 단위로 두 번 끊겨 이레에 17원 어긋난다."),
 ("h4","투자 수익 화면 · 일별 표  ·  " + d0, "투자수익율","MR_{d−1}","MR_{d−1} = M_{d−1} ÷ A_{d−1}",
  ["%s ÷ %s" % (n(M1), n(A1))], n(MR1, 6)+"%",
  "비율이라 더할 수 없다. 분자와 분모를 각각 더한 뒤 나눈다."),
 ("h5","투자 수익 화면 · 일별 표  ·  " + d0, "가중평균 금융일수","wD_{d−1}","wD_{d−1} = ( Σ A_i × D_i ) ÷ A_{d−1}      i ∈ d−1",
  [], "%s일  (표기 %s)" % (wD1, row[0]), "그 하루 몫만 놓고 잰 것."),
 ("h6","투자 수익 화면 · 일별 표  ·  " + d0, "일별 연환산수익률","Y_{MR,d−1}","Y_{MR,d−1} = MR_{d−1} × 365 ÷ wD_{d−1}   (분자·분모 모두 소수 여섯째 자리까지 남긴 값)",
  ["%s%% × 365 ÷ %s" % (n(MR1, 6), wD1),
   "= %s%%" % n(Y1, 6)], str(y1)+"%",
  "그 하루의 실적치. 분자가 약속한 할인율이 아니라 실제로 번 수익률이다."),
]
# PMR 은 백분율 소수 여섯째 자리에서 끊는다 — 비율(0.00033992…)로 끊으면 한 자리가 밀린다
# (dm_0901 규칙 1 · daily_ledger.TY6_EXPR · month_rollup 과 같은 꼴).
PMR = q6(PM / PA * D(100))            # 백분율 6자리
PYMR = q6(PMR * D(365) / PwD)         # ④ 백분율 6자리
share = PA / (PA + PEC)
WPYMR = q6(PYMR * share)              # ⑤ 백분율 6자리
F += [
 ("p1","투자 수익 화면 · 기간 현황  ·  08-21 ~ 08-27","투자실행금","PA","PA = ( Σ A_{d−1} )      기간 안 레코드 전부",
  ["7일치를 더한다"], n(PA)+"원", None),
 ("p2","투자 수익 화면 · 기간 현황  ·  08-21 ~ 08-27","투자수익","PM","PM = ( Σ M_{d−1} )", [], n(PM)+"원", None),
 ("p3","투자 수익 화면 · 기간 현황  ·  08-21 ~ 08-27","투자수익율","PMR","PMR = PM ÷ PA",
  ["%s ÷ %s" % (n(PM), n(PA))], n(PMR, 6)+"%",
  "행별 수익율을 평균 내지 않는다. 채권을 다시 모아 한 번에 낸다."),
 ("p4","투자 수익 화면 · 기간 현황  ·  08-21 ~ 08-27","가중평균 금융일수","PwD","PwD = ( Σ A_i × D_i ) ÷ PA      i 는 정산예정일이 기간 안에 든 채권",
  [], str(PwD)+"일", None),
 ("p5","투자 수익 화면 · 기간 현황  ·  08-21 ~ 08-27","순현금","PEC","PEC = ( Σ EC_{d−1} )",
  ["%s × 7일" % n(EC)], n(PEC)+"원",
  "날마다의 잔액을 기간만큼 더한다. 7일을 고르면 순현금이 7번 들어간다."),
 ("p6","투자 수익 화면 · 기간 현황  ·  08-21 ~ 08-27","투자실행금액 대비 연환산수익률","PY_{MR}","PY_{MR} = PM ÷ PA × 365 ÷ PwD",
  ["1년에 몇 번 굴리나 = 365 ÷ %s = %s 번" % (PwD, q6(365/PwD)),
   "%s%% × 365 ÷ %s" % (n(PMR, 6), PwD)],
  "%s%%   화면 %s%%" % (n(PYMR, 6), f["weekTy"]), "채권으로 나간 돈만 놓고 잰 수익률."),
 ("p7","투자 수익 화면 · 기간 현황  ·  08-21 ~ 08-27","투자자산 대비 연환산수익률","wPY_{MR}","wPY_{MR} = PY_{MR} × PA ÷ (PA + PEC)",
  ["가중치 w = PA ÷ (PA + PEC) = %s ÷ %s = %s"
    % (n(PA), n(PA+PEC), D(share).quantize(D("0.0000001"), rounding=ROUND_HALF_UP)),
   "%s%% × %s ÷ %s" % (n(PYMR, 6), n(PA), n(PA+PEC))],
  "%s%%   화면 %s%%" % (n(WPYMR, 6), f["weekTyAsset"]),
  "놀고 있는 현금까지 분모에 넣어 다시 잰 것. 굴린 돈 중 %s%% 만 일하므로 그만큼 깎인다." % n(share*100,2)),
]

# 연환산 수익금은 ④ 에서 되짚는다 — PM 을 그대로 늘리면 PMR 을 6자리로 끊기 전 값이라
# ④ ⑤ 와 여섯째 자리에서 갈린다(3.992464% vs 3.992511%).
ANN = D(round(PYMR * PA / D(100)))
CHAIN = [
 ("연환산 수익금으로 되돌리면", [
   "PY_{MR} × PA ÷ 100 = %s%% × %s ÷ 100 = %s원" % (n(PYMR, 6), n(PA), n(ANN)),
   "PY_{MR}  = %s ÷ PA        = %s%%" % (n(ANN), q6(ANN/PA*100)),
   "wPY_{MR} = %s ÷ (PA+PEC) = %s%%" % (n(ANN), q6(ANN/(PA+PEC)*100)),
   "→ 같은 분자를 다른 분모로 나눈 것이다"]),
 ("행별 수익율을 평균 내면 틀린다", [
   "일별 7개 단순평균 = %s%%" % n(sum(D(t[k][1]) for k in DS)/len(DS), 6),
   "원장이 내는 값     = %s%%" % n(PYMR, 6),
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

def alias_html():
    """기존 표기 → 바뀐 기호 대조표. 표만 낸다."""
    o = ["<div class='scroll'><table><thead><tr>"]
    o += ["<th>%s</th>" % e(h) for h in alias_table.HEAD]
    o.append("</tr></thead><tbody>")
    for old, new, name in alias_table.rows():
        o.append("<tr><td class='n'>%s</td><td class='n'>%s</td><td>%s</td></tr>"
                 % (e(old), e(new), e(name)))
    o.append("</tbody></table></div>")
    return "".join(o)


def build():
    o = ['<title>계산식 하나씩</title>',
      '<style>@import url("https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=Noto+Serif+KR:wght@400;700&family=IBM+Plex+Mono:wght@400;500&display=swap");',
      CSS, "</style>", '<div class="wrap">',
      '<h1>계산식 하나씩</h1>',
      '<p class="meta">변수 정의 → 산식 → 대입 → 결과 · 기준일 %s · 조회기간 %s ~ %s</p>'
     % (f["asof"], f["weekFrom"], f["weekTo"][5:])]
    o.append('<h2 class="grp">%s</h2>' % e(alias_table.TITLE))
    o.append(alias_html())
    seen = set()
    for fid, grp, name, sym, define, bullets, res, note in F:
        if grp not in seen:
            seen.add(grp); o.append('<h2 class="grp">%s</h2>' % e(grp))
        o.append('<div class="v"><div class="hd"><span class="t">%s</span><span class="s">%s</span></div>'
                 % (e(name), e(sym)))
        o.append('<div class="fx-def">%s</div>' % e(define))
        if bullets:
            o.append("<ul class='sub'>" + "".join("<li>%s</li>" % e(s) for s in bullets) + "</ul>")
        o.append('<div class="res">= %s</div>' % e(res))
        if note: o.append('<p class="p">%s</p>' % e(note))
        o.append("</div>")
    o.append('<h2 class="grp">%s</h2>' % e(testcase_table.TITLE))
    for sec in testcase_table.sections():
        o.append('<h3>%d) %s</h3>' % (sec["no"], e(sec["title"])))
        for tb in sec["tables"]:
            o.append("<div class='scroll'><table><thead><tr>")
            o += ["<th>%s</th>" % e(h) for h in tb["head"]]
            o.append("</tr></thead><tbody>")
            for rr in tb["rows"]:
                o.append("<tr>" + "".join(
                    "<td%s>%s</td>" % (" class='n'" if i in tb["mono"] else "", e(c))
                    for i, c in enumerate(rr)) + "</tr>")
            o.append("</tbody></table></div>")
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
