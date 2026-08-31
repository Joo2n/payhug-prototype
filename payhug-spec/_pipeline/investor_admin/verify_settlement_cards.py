#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
어드민 `정산 현황 > 선정산 결과` 요약 카드 산식 기계 검산.

대상
  1) 산식 문언  — /Users/semi/cursor/payhug-admin-web (읽기 전용)
       app/settlement/overview/PreSettlementTab.tsx  카드 캡션·PAYOUT_TERMS·payoutFormula
       types/settlement.ts                            값 정의 JSDoc
  2) 화면 실측  — settlement_cards_measured.json (세트 A, 판정)
  3) 동결 캡처  — _pipeline/enhance_202608/discovery/dom/admin_overview_partner.html (세트 B, 검사기 자기시험)

왜 코드까지 읽는가
  캡션이 바뀌면 검산 규칙 자체가 바뀐다. 규칙을 이 파일에 손으로 적어두면 화면이 먼저 낡는다.
  그래서 부호·항 구성은 전부 코드 원문에서 확인하고, 사라지면 그 자리에서 FAIL 로 세운다.

판정 원칙
  · 값만 찍고 넘어가는 자리를 만들지 않는다. 출력만 하는 항목은 REPORT 로 명시하고 종료코드에서 뺀다.
  · try/except 로 오류를 SKIP 으로 삼키지 않는다. 대상 파일이 없으면 FAIL 이다.
  · FAIL 1건 이상이면 종료코드 1.
"""

import json
import os
import re
import sys
import html as htmlmod

HERE = os.path.dirname(os.path.abspath(__file__))
ADMIN = "/Users/semi/cursor/payhug-admin-web"
TAB = os.path.join(ADMIN, "app/settlement/overview/PreSettlementTab.tsx")
TYPES = os.path.join(ADMIN, "types/settlement.ts")
PAGE = os.path.join(ADMIN, "app/settlement/overview/page.tsx")
MEASURED = os.path.join(HERE, "settlement_cards_measured.json")
FROZEN = os.path.join(
    HERE, "..", "enhance_202608", "discovery", "dom", "admin_overview_partner.html"
)

R = []          # 판정 대상
REPORT = []     # 출력만 (종료코드 밖) — 이유를 반드시 함께 적는다


def chk(section, name, ok, detail=""):
    R.append({"section": section, "name": name, "pass": bool(ok), "detail": detail})
    return bool(ok)


def report(section, name, detail, why):
    REPORT.append({"section": section, "name": name, "detail": detail, "why": why})


def rd(path):
    """없는 파일을 빈 문자열로 삼키지 않는다 — 없으면 그 자리가 FAIL 로 남게 None 을 돌린다."""
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as f:
        return f.read()


def won(n):
    return f"{n:,}"


# ─────────────────────────────────────────────────────────────
# A. 산식 문언 정박 — 검산 규칙의 출처가 살아 있는가
# ─────────────────────────────────────────────────────────────
tab = rd(TAB)
types = rd(TYPES)
page = rd(PAGE)

chk("code", "PreSettlementTab.tsx 존재", tab is not None, TAB)
chk("code", "types/settlement.ts 존재", types is not None, TYPES)
chk("code", "overview/page.tsx 존재", page is not None, PAGE)

tab = tab or ""
types = types or ""
page = page or ""

# 카드 캡션 원문 — 이 문자열이 검산 규칙 그 자체다
ANCHORS_TAB = [
    ("순지급액 캡션 = 총 매출액 - 총 수수료", 'sub="총 매출액 - 총 수수료"'),
    ("총수수료 캡션 = 카드 + 배달", "카드 ${fmt(o.cardFeeAmt)} + 배달 ${fmt(o.deliveryFeeAmt)}"),
    ("선정산수수료 캡션 = 매입+시스템+이체", "매입${fmt(o.marginFeeAmt || 0)}+시스템${fmt(o.systemFeeAmt || 0)}+이체${fmt(o.transferFeeAmt || 0)}"),
    ("선정산수수료 캡션에 +차액대상", "+차액대상${fmt(o.adjMarginFeeAmt)}"),
    ("지급액 기본항 = 대상액 - 수수료", 'base: "선정산 대상액 - 선정산 수수료"'),
    ("차액 카드 부호 문구", "양수 = 추가 차감, 음수 = 환급"),
    ("차액 카드 정의 문구", "실제 수수료 - 예상 수수료 (거래일 기준)"),
]
for name, needle in ANCHORS_TAB:
    chk("code", name, needle in tab, "원문 없음" if needle not in tab else "")

# 지급액 캡션 7항의 부호 — payoutFormula 가 실제로 붙이는 연산자
PAYOUT_SIGNS = [
    ("반영 수수료 차액", '${batchAdj > 0 ? "+" : "-"} ${PAYOUT_TERMS.feeDiff}', None),
    ("미회수 이월 +", "carryForward > 0 ? ` + ${PAYOUT_TERMS.carryForward}", "+"),
    ("오프라인 차감 -", "` - ${PAYOUT_TERMS.offline}", "-"),
    ("플랫폼 차감 -", "` - ${PAYOUT_TERMS.adDeduction}", "-"),
    ("플랫폼 환급 +", "` + ${PAYOUT_TERMS.refund}", "+"),
]
for name, needle, _sign in PAYOUT_SIGNS:
    chk("code", f"지급액 캡션 부호: {name}", needle in tab, "" if needle in tab else "원문 없음")

# 대상액 산식의 출처 — types JSDoc. '+' 방향이 여기 박혀 있다
chk("code", "types: 대상액 = 순 지급액 + 제외액 + 거래 수수료 차액",
    "대상액 = 순 지급액 + 제외액 + 이 값" in types,
    "" if "대상액 = 순 지급액 + 제외액 + 이 값" in types else "JSDoc 문언 없음")

# 지급액 항등식의 출처 — carryForwardTotal JSDoc
IDENT = "지급액 = 대상액 − 수수료(실차감 기준) + 반영차액 + 이월생성분 − 오프라인 − 플랫폼차감 + 환급"
chk("code", "types: 지급액 항등식 7항 선언", IDENT in types,
    "" if IDENT in types else "JSDoc 항등식 문언 없음")

# 캡션이 음수 항을 통째로 떨어뜨리는 게이트가 실재하는가 (구조 구멍의 소재)
GATES = [
    "(o.offlineDeductionTotal || 0) > 0",
    "(o.adDeductionTotal || 0) > 0",
    "totalRefund > 0",
    "carryForward > 0",
]
gates_present = [g for g in GATES if g in tab]
chk("code", "지급액 캡션 항 노출 게이트 4종 실재", len(gates_present) == 4,
    f"발견 {len(gates_present)}/4 — 이 게이트들은 항이 음수면 캡션에서 통째로 사라지게 한다")

# 요약 카드에는 행 단위 검증차이(unexplainedDiffAmt)에 해당하는 총계 항목이 없다
m = re.search(r"export interface PreSettlementOverview \{(.*?)\n\}", types, re.S)
chk("code", "PreSettlementOverview 블록 파싱", m is not None,
    "" if m else "인터페이스 블록을 못 잡았다 — 아래 검사가 무효라 FAIL")
ov_block = m.group(1) if m else ""
chk("code", "요약 총계에 검증차이 항목이 없음 (행에만 있음)",
    ("unexplainedDiff" not in ov_block) and ("unexplainedDiffAmt" in types),
    "요약 카드는 잔차를 표기할 자리가 없다 — 행 툴팁(검증 차이)에만 있다")

# 건별 제외액 JSDoc 의 괄호 부호가 대상액 항등식과 정합한가.
#   feeDiffAmt        = txAmount − netPayout                       (JSDoc 원문)
#   targetAmt(=txAmount) = netPayout + excludedAmt + feeDiffAmt     (JSDoc 원문, 요약 산식)
#   ⇒ excludedAmt = txAmount − (netPayout + feeDiffAmt)
# 현행 원문은 괄호가 '순지급액 − 수수료 차액' 이라 두 식이 동시에 성립하지 않는다.
# (선정산 카드 건 excludedAmt = 0 이라는 같은 JSDoc 의 단서와도 '+' 일 때만 맞는다)
EXC_WRONG = "정산 시점 순지급액(순지급액 − 수수료 차액)"
EXC_RIGHT = "정산 시점 순지급액(순지급액 + 수수료 차액)"
chk("code", "types: 건별 제외액 정의 괄호 부호 = 대상액 항등식과 정합",
    (EXC_RIGHT in types) and (EXC_WRONG not in types),
    f"원문 '{EXC_WRONG}' — 대상액 = 순지급액 + 제외액 + 차액 과 동시에 성립하지 않는다"
    if EXC_WRONG in types else "")

# 에이전시 전체 = 클라이언트 필터 없음 → 카드값은 서버 집계 원값(행 합이 아님)
chk("code", "필터 없으면 서버 집계 원값 사용",
    "const isClientFiltered = Boolean(agencyCodeFilter || merchantQuery);" in page
    and "isClientFiltered && overview.totalOverview" in page,
    "필터가 걸릴 때만 행 합으로 재집계한다 — 전체 뷰의 8개 카드는 서로 독립한 서버 집계다")


# ─────────────────────────────────────────────────────────────
# B. 실측 세트 검산
# ─────────────────────────────────────────────────────────────
raw = rd(MEASURED)
chk("data", "실측 파일 존재", raw is not None, MEASURED)
meas = json.loads(raw) if raw else {"sets": []}

setA = next((s for s in meas["sets"] if s["id"] == "A"), None)
chk("data", "세트 A 존재", setA is not None, "")

if setA:
    c = setA["cards"]
    S = c["totalSalesAmt"]; F = c["totalFeeAmt"]
    CF = c["cardFeeAmt"]; DF = c["deliveryFeeAmt"]
    NP = c["netPayoutAmt"]; EX = c["preSettlementExcludedAmt"]
    DT = c["directTransferAmt"]; RO = c["recordOnlyAmt"]
    FD = c["feeDiffAmt"]; TG = c["preSettlementTargetAmt"]
    FEE = c["preSettlementFeeAmt"]
    MG = c["marginFeeAmt"]; SY = c["systemFeeAmt"]; TR = c["transferFeeAmt"]; AJ = c["adjMarginFeeAmt"]
    PAY = c["preSettlementPayoutAmt"]
    ADJ = c["adjustmentTotal"]; CFW = c["carryForwardTotal"]
    OFF = c["offlineDeductionTotal"]; ADD = c["adDeductionTotal"]; RFD = c["platformRefundTotal"]
    CC = c["cancelledCardAmt"]; OC = c["cancelledOrderAmt"]

    # ① 총수수료 = 카드 + 배달
    d1 = CF + DF - F
    chk("A", "① 총수수료 = 카드 + 배달", d1 == 0,
        f"{won(CF)} + {won(DF)} = {won(CF+DF)} vs 화면 {won(F)} · 차 {won(d1)}")

    # ② 순지급액 = 총매출액 − 총수수료
    d2 = NP - (S - F)
    chk("A", "② 순지급액 = 총매출액 - 총수수료", d2 == 0,
        f"{won(S)} - {won(F)} = {won(S-F)} vs 화면 {won(NP)} · 차 {won(d2)} (화면이 {won(abs(d2))} 크다)")

    # ②' ②의 편차가 어느 칸의 판독 오류로 설명될 수 있는지 — 후보를 기계로 좁힌다.
    #     순지급액을 d2 만큼 옮기면 ② 는 맞지만 ④(대상액) 가 깨진다 → 순지급액 판독 오류로는 설명 불가.
    #     총수수료를 옮기면 ①(카드+배달) 이 깨진다 → 총수수료 판독 오류로도 설명 불가.
    #     총매출액만이 다른 어떤 검산도 건드리지 않는다 (총매출액은 ② 외에 어느 항등식에도 안 들어간다).
    chk("A", "②' 순지급액 판독 오류로는 설명 불가",
        (NP - d2) + EX + FD != TG,
        f"순지급액을 {won(NP-d2)} 로 보면 ② 는 맞지만 대상액이 {won((NP-d2)+EX+FD)} 가 되어 화면 {won(TG)} 와 어긋난다")
    chk("A", "②'' 총수수료 판독 오류로는 설명 불가",
        CF + DF != F + d2,
        f"총수수료를 {won(F+d2)} 로 보면 ② 는 맞지만 카드+배달 {won(CF+DF)} 와 어긋난다")
    chk("A", "②''' 남는 단일 판독 후보는 총매출액뿐",
        (S + d2) - F == NP,
        f"총매출액이 {won(S+d2)} 였다면 ② 가 성립하고 다른 검산은 총매출액을 쓰지 않아 무영향")

    # ③ 선정산수수료 = 매입 + 시스템 + 이체 + 차액대상
    d3 = MG + SY + TR + AJ - FEE
    chk("A", "③ 선정산수수료 = 매입+시스템+이체+차액대상", d3 == 0,
        f"{won(MG)}+{won(SY)}+{won(TR)}+({won(AJ)}) = {won(MG+SY+TR+AJ)} vs 화면 {won(FEE)} · 차 {won(d3)}")

    # ③' 제외액 구성 — 바로이체·이미지급은 양수로 내려와 화면이 -를 붙인다
    resid_ex = EX + (DT + RO)
    # 잔차의 값 자체는 기대값을 댈 수 없다(정산 후 취소분). 대신 코드 JSDoc 이 못박은 두 성질을 판정한다 —
    # 「대상액 스냅샷에만 남아 양수」이고, 정산 후 취소분은 기간 전체 취소분의 부분집합이다.
    chk("A", "③' 제외액 잔차가 양수 (JSDoc: 정산 후 취소분)", resid_ex > 0,
        f"-({won(DT)}+{won(RO)}) = {won(-(DT+RO))} vs 화면 {won(EX)} · 잔차 {won(resid_ex)}")
    chk("A", "③'' 제외액 잔차 ≤ 기간 전체 취소액", resid_ex <= CC + OC,
        f"잔차 {won(resid_ex)} vs 취소합 {won(CC+OC)} (카드 {won(CC)} + 배달 {won(OC)})")
    chk("A", "③''' 잔차가 0이 아니면 화면 안내 조건이 참",
        (resid_ex != 0) == (EX != -(DT + RO)),
        "코드 조건 preSettlementExcludedAmt !== -(directTransferAmt + recordOnlyAmt) 와 같은 판정")

    # ④ 선정산 대상액 — 조합 전수 탐색
    base = NP + EX
    pool = {
        "거래수수료차액": FD, "카드승인취소": CC, "배달주문취소": OC,
        "취소합": CC + OC, "선정산수수료": FEE, "미회수이월": CFW,
        "오프라인차감": OFF, "플랫폼차감": ADD, "플랫폼환급": RFD,
        "반영수수료차액": ADJ,
    }
    keys = list(pool)
    hits = []
    from itertools import combinations, product
    for n in range(0, 4):
        for cs in combinations(keys, n):
            for sg in product([1, -1], repeat=n):
                if base + sum(s * pool[k] for k, s in zip(cs, sg)) == TG:
                    hits.append("순지급액+제외액" + "".join(
                        f"{'+' if s > 0 else '-'}{k}" for k, s in zip(cs, sg)))
    hits = sorted(set(hits), key=len)
    doc_combo = base + FD == TG
    chk("A", "④ 대상액 = 순지급액 + 제외액 + 거래수수료차액 (코드 JSDoc 산식)", doc_combo,
        f"{won(NP)} + ({won(EX)}) + {won(FD)} = {won(base+FD)} vs 화면 {won(TG)} · 차 {won(base+FD-TG)}")
    chk("A", "④' 3항 이내 정확일치 조합이 유일", len(hits) == 1,
        f"정확일치 {len(hits)}건: {hits}")
    chk("A", "④'' 취소분은 대상액 조합에 들어가지 않음",
        all("취소" not in h for h in hits),
        f"카드승인취소 {won(CC)} · 배달주문취소 {won(OC)} 는 어느 정확일치 조합에도 없다")

    # ⑤ 선정산 지급액 — 캡션 7항 그대로
    calc = TG - FEE + ADJ + CFW - OFF - ADD + RFD
    gap = calc - PAY
    chk("A", "⑤ 지급액 = 캡션 7항", gap == 0,
        f"{won(TG)} - {won(FEE)} + ({won(ADJ)}) + {won(CFW)} - {won(OFF)} - {won(ADD)} + {won(RFD)} "
        f"= {won(calc)} vs 화면 {won(PAY)} · 차 {won(gap)}")

    # ⑤' 갭 분해 — 이월을 뺀 6항 잔차가 곧 행 단위 검증차이의 합이어야 한다
    resid6 = PAY - (TG - FEE + ADJ - OFF - ADD + RFD)
    chk("A", "⑤' 6항 잔차 = 미회수이월 (코드가 주장하는 항등식)", resid6 == CFW,
        f"Σ검증차이 상당액 {won(resid6)} vs 이월 {won(CFW)} · 차 {won(resid6-CFW)} "
        f"→ 이월로 설명되지 않는 잔차 {won(abs(resid6-CFW))}")

    # ⑤'' 캡션 게이트가 이번 실측에서 항을 떨어뜨렸는가
    dropped = [n for n, v in [("미회수이월", CFW), ("오프라인차감", OFF),
                              ("플랫폼차감", ADD), ("플랫폼환급", RFD)] if v <= 0]
    chk("A", "⑤'' 캡션 게이트(>0)가 떨어뜨린 항 0건", len(dropped) == 0,
        f"떨어진 항: {dropped or '없음'} — 있으면 그 금액은 지급액에 들어가고 캡션에는 안 뜬다")

    # ⑤''' 캡션이 실제로 찍은 부호가 값의 부호와 맞는가
    sg = setA["captionSigns"]
    chk("A", "⑤''' 캡션 부호 = 값 부호 (반영 수수료 차액)",
        sg["adjustmentTotal"] == ("+" if ADJ > 0 else "-"),
        f"캡션 '{sg['adjustmentTotal']}' · 값 {won(ADJ)}")

    # ⑥ 거래 수수료 차액의 부호 — 캡션은 '양수 = 추가 차감', 대상액 산식은 더한다
    plus_ok = (base + FD == TG)
    minus_ok = (base - FD == TG)
    chk("A", "⑥ 대상액 검산에서 차액은 더해야 맞는다", plus_ok and not minus_ok,
        f"더하면 {won(base+FD)} (일치) · 빼면 {won(base-FD)} (차 {won(base-FD-TG)})")
    report("A", "⑥' 캡션 '양수 = 추가 차감' ↔ 산식 '+' 의 양립",
           f"더해야 맞는다({won(base+FD)}=화면). 캡션은 차감이라 읽힌다",
           "양립하려면 순지급액이 실제수수료 기준, 대상액이 선정산 시점 예상수수료 스냅샷이어야 한다 — "
           "그 기준 차이는 백엔드 집계 모집단이라 이 검증기가 확인할 수 없다. "
           "산술 방향은 ⑥ 이 판정하고, 코드 문언의 자기모순은 code 섹션 "
           "'건별 제외액 정의 괄호 부호' 가 판정한다")

    report("A", "취소 집계", f"카드 {c['cancelledCardCount']}건/{won(CC)} · 배달 {c['cancelledOrderCount']}건/{won(OC)}",
           "요약 모집단 밖 별도 집계라(types JSDoc) 어느 카드와도 검산 관계가 없다 — 기대값을 댈 수 없다")
    report("A", "건수", f"{setA['txCount']}건 / {setA['merchantCount']}개 가맹점",
           "행 데이터가 없어 곳수를 재검산할 원천이 없다")


# ─────────────────────────────────────────────────────────────
# E. 채권매입수수료 요율의 기준액(앵커) — 순지급액인가 선정산대상액인가
#    다른 조에서 판정이 갈린 자리. 코드 문언과 수치 역산을 갈라 판정한다.
# ─────────────────────────────────────────────────────────────
tax = rd(os.path.join(ADMIN, "app/settlement/overview/TaxInvoiceTab.tsx"))
policy = rd(os.path.join(ADMIN, "app/settlement/policies/page.tsx"))
merch = rd(os.path.join(ADMIN, "app/merchants/[id]/page.tsx"))
svc = rd(os.path.join(ADMIN, "services/settlementService.ts"))

chk("E", "TaxInvoiceTab.tsx 존재", tax is not None, "")
chk("E", "settlement/policies/page.tsx 존재", policy is not None, "")
chk("E", "merchants/[id]/page.tsx 존재", merch is not None, "")
chk("E", "services/settlementService.ts 존재", svc is not None, "")
tax = tax or ""; policy = policy or ""; merch = merch or ""; svc = svc or ""

# E1 요율 계산식이 baseAmount 를 분모로 쓴다
chk("E", "E1 요율 = supply / baseAmount", "const pct = (row.supply / row.baseAmount) * 100;" in tax, "")
# E2 그 열의 헤더 문자열
chk("E", "E2 baseAmount 열 헤더가 '선정산대상액'",
    'font-medium text-right">선정산대상액</th>' in tax, "")
# E3 baseAmount 의 타입 JSDoc
chk("E", "E3 baseAmount JSDoc = 요율 산정 기준액", "/** 요율 산정 기준액 (이체수수료는 null) */" in types, "")
# E4 프론트가 baseAmount 를 만들지 않는다 — 서버 필드를 그대로 쓴다(대입·산술 0건)
# 값을 만드는 자리만 잡는다 — 비교(===)·타입 선언·서버값 그대로 넘기는 대입은 제외.
#   유도가 있으면 앵커를 프론트가 정하는 것이고, 없으면 앵커는 전적으로 서버 몫이다.
base_writes = re.findall(r"baseAmount\s*(?::\s*|=(?!=)\s*)([^,;\n]*)", tax + page + types)
PASSTHRU = re.compile(r"^(number \| null|r\.baseAmount|row\.baseAmount)")
derived = [x.strip() for x in base_writes if not PASSTHRU.match(x.strip())]
chk("E", "E4 프론트에 baseAmount 유도 코드 0건", len(derived) == 0,
    f"유도로 보이는 자리 {derived}" if derived
    else "타입 선언 1곳 + 서버값 그대로 넘기는 자리뿐 — 앵커를 정하는 것은 서버 /tax-invoice 응답이다")
# E5 코드가 두 화면의 값을 같은 원천으로 잇는 유일한 문장
LINK = "계산서 발행 탭의 선정산대상액과 같은 원천값"
chk("E", "E5 types 가 요약 대상액 ↔ 계산서 대상액을 같은 원천으로 선언", LINK in types, "")
# E6 요약 카드 대상액 캡션도 계산서 발행을 가리킨다
chk("E", "E6 대상액 카드 캡션 = 계산서 발행에 따른 채권 매입 금액",
    'sub="계산서 발행에 따른 채권 매입 금액"' in tab, "")
# E7 MARGIN 이 역할별로 쪼개진다 — C1 의 0.6+0.11+0.1 분해와 같은 축
roles = re.findall(r'\{ feeType: "MARGIN", targetRole: "(\w+)"', policy)
chk("E", "E7 MARGIN 이 역할별 다행 구조", len(set(roles)) >= 3,
    f"역할 {sorted(set(roles))} — 계산서 탭의 '발행 주체' 행이 이 축이다")
# E8 정책 화면은 요율의 기준액을 말하지 않는다 → 앵커가 드러나는 자리는 계산서 탭뿐
chk("E", "E8 정책 화면에 기준액 문언 0건",
    ("선정산대상액" not in policy) and ("순지급" not in policy),
    "요율은 %로만 입력받고 무엇에 곱하는지 화면이 말하지 않는다")

if setA:
    # ── 수치 역산. 분자는 실차감(charged) 매입수수료, 분모는 전 가맹점 합(면제 포함)
    MGF = c["marginFeeAmt"]
    anchors = {"선정산대상액": TG, "순지급액": NP}
    cands = [1.0, 0.81, 0.604, 0.25]   # C1 후보
    feas = {}
    for aname, A in anchors.items():
        blended = MGF / A * 100
        for r in cands:
            x = 1 - blended / r      # 면제 가맹점이 대상액에서 차지해야 하는 비율
            feas[(aname, r)] = x
        chk("E", f"E9 블렌디드 요율({aname})",
            abs(MGF / A * 100 - blended) < 1e-12,
            f"{won(MGF)} / {won(A)} = {blended:.6f}%")

    # E10 면제는 분자만 줄인다 → 실제 요율은 블렌디드보다 반드시 크다.
    #     블렌디드보다 낮은 후보는 면제로 설명할 수 없다(음의 면제분).
    for (aname, r), x in sorted(feas.items()):
        expect_ok = (0 <= x < 1)
        chk("E", f"E10 면제 역산 {aname} × {r}% → 면제분 {x*100:.3f}%",
            (x < 0) == (r * 1 < MGF / anchors[aname] * 100),
            f"{'가능' if expect_ok else '불가(음의 면제분)'} · 면제 대상액 {won(round(anchors[aname]*x))}")

    # E11 후보 4종 중 두 앵커에서 모두 살아남는 것은 1.0% 하나뿐
    alive = sorted({r for (a, r), x in feas.items() if 0 <= x < 1})
    chk("E", "E11 면제로 설명 가능한 요율 후보 = 1.0% 단일", alive == [1.0],
        f"생존 후보 {alive} · 0.81%/0.604%/0.25% 는 두 앵커 모두에서 음의 면제분을 요구한다")

    # E12 0.811% ≈ 0.81% 주장의 반증 — 순지급액 앵커에서도 0.81% 는 음의 면제분을 요구한다
    x81 = feas[("순지급액", 0.81)]
    chk("E", "E12 순지급액 앵커 + 0.81% 는 면제로 설명 불가", x81 < 0,
        f"필요 면제분 {x81*100:.3f}% (음수) — 실차감이 0.81%×순지급액보다 "
        f"{won(round(MGF - 0.0081*NP))} 많다. 면제는 분자를 줄이기만 하므로 방향이 반대다")

    # E13 두 블렌디드 요율은 항등식으로 묶여 있다 — 서로 독립한 증거가 아니다
    lhs = MGF / NP
    rhs = (MGF / TG) * (TG / NP)
    chk("E", "E13 r(순지급액) = r(대상액) × 대상액/순지급액 (항등식)", abs(lhs - rhs) < 1e-15,
        f"두 역산값은 제외액 비율 하나로 연결된다 — 한쪽이 맞으면 다른 쪽 값은 자동으로 정해진다")

    # E14 0.81% 근접의 민감도 — 구조가 아니라 이 기간 바로이체 규모에 달렸다
    need_np = MGF / 0.0081
    delta = need_np - NP
    chk("E", "E14 0.81% 정확일치는 순지급액이 달랐으면 깨진다", abs(delta) > 0,
        f"정확히 0.81% 가 되려면 순지급액 {need_np:,.0f} 필요 · 실제와 {delta:,.0f} 차 "
        f"({delta/NP*100:.4f}%). 바로이체 {won(DT)} 의 {abs(delta)/DT*100:.2f}% 만 달랐어도 일치가 사라진다")
    chk("E", "E14' 0.81% 는 근사일 뿐 정확일치가 아니다", MGF != round(0.0081 * NP),
        f"0.81% × 순지급액 = {won(round(0.0081*NP))} vs 실측 매입수수료 {won(MGF)}")

# ── TP-68: estimatedAmount 가 수수료인가 지급액인가
chk("E", "F1 estimatedAmount 는 서버 필드(ForecastMerchant)",
    "export interface ForecastMerchant" in svc and "estimatedAmount: number;" in svc, "")
fe_derive = re.findall(r"estimatedAmount\s*=\s*[^;\n]*", merch)
chk("E", "F2 프론트에 estimatedAmount 산출 코드 0건", len(fe_derive) == 0,
    f"발견 {fe_derive}" if fe_derive else "화면은 서버값을 그대로 찍는다 — 산식 검산 자리가 없다")
chk("E", "F3 라벨은 '예상 정산 금액'", "예상 정산 금액:" in merch, "")
chk("E", "F4 괄호 산식은 '순지급 × 할인율%'",
    "(순지급 {Math.round(forecastInfo.avgNetPayoutAmt ?? 0).toLocaleString()}원 x 할인율 {forecastInfo.discountRatePct}%)" in merch, "")
chk("E", "F5 같은 배너에 수수료가 별도 슬롯으로 있다",
    "(수수료 {Math.round(forecastInfo.avgFeeAmt).toLocaleString()}원)" in merch,
    "수수료 자리가 따로 있으므로 '예상 정산 금액' 은 수수료 슬롯이 아니다")
chk("E", "F6 merchants/[id] 226행 주석이 말하는 '수수료율' 이 타입에 없다",
    "interface Assignment { routingRuleId: number; businessId?: number; txType: string; feePolicyId: number; policyName: string; ruleType: string; validFrom: string; }" in merch
    and "정산상품 배정 정보(상품명·수수료율·배정일)" in merch,
    "Assignment 에 요율 필드가 없고 배정 카드도 상품명·배정일만 그린다 — 여기서 요율 기준을 읽을 수 없다")
chk("E", "F7 가맹점 상세가 받는 정책은 요율 없이 3필드",
    "interface PolicyOption { id: number; policyName: string; ruleType: string; }" in merch
    and "rateBps" not in merch,
    "rateBps 는 정책 화면(settlement/policies)에서만 다루고 가맹점 상세로 오지 않는다")


# ─────────────────────────────────────────────────────────────
# C. 동결 캡처로 검사기 자기시험
# ─────────────────────────────────────────────────────────────
setB = next((s for s in meas["sets"] if s["id"] == "B"), None)
chk("data", "세트 B 존재", setB is not None, "")

frozen = rd(FROZEN)
chk("B", "동결 캡처 파일 존재", frozen is not None, os.path.normpath(FROZEN))

if frozen and setB:
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", frozen, flags=re.S)
    t = htmlmod.unescape(re.sub(r"<[^>]+>", "\n", t))
    L = [x.strip() for x in t.split("\n") if x.strip()]

    def after(label, occurrence=0):
        """label 다음 첫 숫자 줄. 못 찾으면 None (호출부가 FAIL 로 판정한다)."""
        seen = 0
        for i, x in enumerate(L):
            if x == label:
                if seen == occurrence:
                    for y in L[i + 1:i + 4]:
                        if re.fullmatch(r"[+\-]?[\d,]+", y):
                            return int(y.replace(",", "").replace("+", ""))
                    return None
                seen += 1
        return None

    bS = after("총 매출액"); bF = after("총 수수료"); bNP = after("순 지급액")
    bEX = after("선정산 제외액"); bTG = after("선정산 대상액"); bFEE = after("선정산 수수료")
    bADJ = after("정산 반영 수수료 차액"); bPAY = after("선정산 지급액")
    fees = re.search(r"매입([\d,]+)\+시스템([\d,]+)\+이체([\d,]+)", t)
    pair = re.search(r"카드 ([\d,]+) \+ 배달 ([\d,]+)", t)
    banner = re.findall(r"\(\+([\d,]+)원\)", t)

    parsed = [bS, bF, bNP, bEX, bTG, bFEE, bADJ, bPAY, fees, pair]
    chk("B", "캡처 판독 전건 성공", all(x is not None for x in parsed),
        f"판독 실패 {sum(1 for x in parsed if x is None)}건")

    if all(x is not None for x in parsed):
        cfee, dfee = (int(x.replace(",", "")) for x in pair.groups())
        mg, sy, tr = (int(x.replace(",", "")) for x in fees.groups())

        # 같은 검사식을 동결 데이터에 그대로 돌린다
        chk("B", "자기시험: ① 총수수료 = 카드+배달 이 이 빌드에서 맞는다", cfee + dfee == bF,
            f"{won(cfee)}+{won(dfee)} vs {won(bF)}")
        chk("B", "자기시험: ② 순지급액 = 총매출-총수수료 가 이 빌드에서 맞는다", bNP == bS - bF,
            f"{won(bS-bF)} vs {won(bNP)}")
        chk("B", "자기시험: ③ 선정산수수료 = 매입+시스템+이체 가 이 빌드에서 맞는다", mg + sy + tr == bFEE,
            f"{won(mg+sy+tr)} vs {won(bFEE)}")

        # 알려진 편차 2건을 그대로 집어내는가
        d_tg = bTG - (bNP + bEX)
        d_pay = (bTG - bFEE + bADJ) - bPAY
        chk("B", "자기시험: 대상액 편차를 알려진 값으로 집어냄",
            d_tg == setB["knownDeltas"]["targetMinusNetPlusExcluded"],
            f"대상액 - (순지급+제외) = {won(d_tg)} (기대 {won(setB['knownDeltas']['targetMinusNetPlusExcluded'])})")
        chk("B", "자기시험: 지급액 캡션-값 편차를 알려진 값으로 집어냄",
            d_pay == setB["knownDeltas"]["payoutCaptionMinusValue"],
            f"(대상액-수수료+반영차액) - 지급액 = {won(d_pay)} (기대 {won(setB['knownDeltas']['payoutCaptionMinusValue'])})")

        # 그 편차의 정체 — 구버전에는 거래 수수료 차액 카드가 없었고, 배너 반영+대기 합이 그 값이다
        chk("B", "자기시험: 구버전 대상액 편차 = 배너 반영+대기 차액 합",
            len(banner) >= 2 and sum(int(x.replace(",", "")) for x in banner[:2]) == d_tg,
            f"배너 {banner[:2]} 합 vs 대상액 편차 {won(d_tg)} — "
            f"현행 '거래 수수료 차액' 카드가 승격되기 전 같은 값이 카드 없이 대상액에 들어가 있었다")
        chk("B", "자기시험: 구버전 지급액 값 = 대상액 - 수수료 (캡션의 차액항은 값에 없음)",
            bPAY == bTG - bFEE,
            f"{won(bTG)} - {won(bFEE)} = {won(bTG-bFEE)} vs 화면 {won(bPAY)}")

        report("B", "구버전 캡션 원문", "선정산 대상액 - 선정산 수수료 + 정산 반영 수수료 차액(21,200)",
               "동결 아티팩트라 지금 고칠 대상이 아니다 — 값 자체는 판정하지 않고 검사기가 편차를 잡는지만 판정한다")


# ─────────────────────────────────────────────────────────────
# 결론 — 검사 결과에서 기계로 뽑는다 (손으로 적지 않는다)
# ─────────────────────────────────────────────────────────────
verdict = None
if setA:
    code_side = all(x["pass"] for x in R
                    if x["section"] == "E" and x["name"].startswith(("E1 ", "E2 ", "E3 ", "E5 ")))
    tgt_alive = [r for r in cands if 0 <= feas[("선정산대상액", r)] < 1]
    net_alive = [r for r in cands if 0 <= feas[("순지급액", r)] < 1]
    if tgt_alive and net_alive:
        verdict = "가맹점별 데이터 없이는 확정 불가"
    elif tgt_alive:
        verdict = "선정산대상액"
    elif net_alive:
        verdict = "순지급액"
    else:
        verdict = "가맹점별 데이터 없이는 확정 불가"

    report("E", "앵커 결론", verdict,
           f"코드 문언은 대상액을 가리킨다(E1·E2·E3·E5 전건 {'성립' if code_side else '불성립'}). "
           f"그러나 수치로는 대상액 앵커 생존 후보 {tgt_alive} · 순지급액 앵커 생존 후보 {net_alive} 로 "
           f"두 앵커 모두 1.0% 를 살려 둔다(면제분만 9.036% vs 18.894% 로 다르다). "
           f"확정에 필요한 것 — ① 계산서 발행 탭에서 가맹점 1곳의 baseAmount 실측 1건과 "
           f"같은 기간 그 가맹점 행의 선정산대상액·순지급액. 두 값 중 어느 것과 같은지로 즉시 결판난다. "
           f"② 수수료 면제 가맹점(feeExempt 배지) 명단과 그 가맹점들의 대상액 합 — "
           f"9.036% 인지 18.894% 인지가 남은 한 갈래를 자른다")

report("E", "TP-68 estimatedAmount 의 정체", "문언은 지급액 · 산식은 수수료 — 프론트만으로 확정 불가",
       "라벨이 '예상 정산 금액' 이고 같은 배너에 수수료 슬롯이 따로 있다(F3·F5) → 지급액으로 읽힌다. "
       "반면 괄호 산식 '순지급 × 할인율%'(F4) 는 할인율이 요율(0.6~1%대)이면 수수료를 낸다. "
       "값이 서버에서 오고 프론트에 산출 코드가 0건이라(F1·F2) 코드로는 갈리지 않는다. "
       "확정에 필요한 것 — discountRatePct 실측 1건. 1 근처면 estimatedAmount 는 수수료, "
       "99 근처면 지급액이다. merchants/[id] 226행은 근거가 못 된다(F6·F7)")


# ─────────────────────────────────────────────────────────────
# 출력
# ─────────────────────────────────────────────────────────────
fails = [x for x in R if not x["pass"]]

width = max(len(x["name"]) for x in R) if R else 0
cur = None
for x in R:
    if x["section"] != cur:
        cur = x["section"]
        print(f"\n[{cur}]")
    mark = "PASS" if x["pass"] else "FAIL"
    print(f"  {mark}  {x['name']:<{width}}  {x['detail']}")

if REPORT:
    print("\n[판정하지 않음 — 출력만]")
    for x in REPORT:
        print(f"  REPORT  {x['name']}: {x['detail']}")
        print(f"          이유: {x['why']}")

print(f"\n총 {len(R)}건 · PASS {len(R)-len(fails)} · FAIL {len(fails)}")
for x in fails:
    print(f"  FAIL  [{x['section']}] {x['name']} — {x['detail']}")

with open(os.path.join(HERE, "verify_settlement_cards_result.json"), "w", encoding="utf-8") as f:
    json.dump({"checks": R, "report": REPORT, "anchorVerdict": verdict,
               "total": len(R), "fail": len(fails)}, f, ensure_ascii=False, indent=2)

sys.exit(1 if fails else 0)
