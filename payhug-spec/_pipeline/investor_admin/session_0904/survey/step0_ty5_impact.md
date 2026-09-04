# ⑤ 투자자산 대비 ty수익률 — 「일자 축 통일안」 교체 파급 조사

기준: `_pipeline/investor_admin/` (이하 P) · `~/cursor/payhug-investor-admin/` (이하 R) · 읽기 전용 조사 결과.

현행 ⑤ = ④ × PA ÷ (PA + PEC), PA = Σ A_i (정산예정일 ∈ P), PEC = CASH × 조회 일수.
후보 ⑤' = ④ × Σ_d SA_d ÷ Σ_d (SA_d + EC_d), SA_d = d 마감 미회수 채권 A_i 합(잔액), EC_d = d 마감 순현금.

## 0. 원장에서 직접 낸 값 (RECEIVABLES adv·due·ai, 기간 = facts weekFrom~weekTo = 2026-08-20 ~ 08-26)

| 항목 | 값 |
|---|---|
| SA_d 정의 | Σ ai, adv ≤ d 이고 due > d (d 당일 정산예정 채권은 회수된 것으로 봄) |
| SA_d (08-20 → 08-26) | 79,652,915 · 79,187,438 · 80,161,902 · 81,055,996 · 81,673,156 · 81,640,680 · 81,135,846 |
| SA_ASOF(08-27) | 80,000,000 = EXEC (불변식과 일치 — 앵커 검증) |
| Σ SA_d (7일) | 564,507,933 |
| Σ EC_d — 역산(100,000,000 − SA_d) | 135,492,067 → 비중 80.6440% → ⑤' 3.330256 (표기 3.33) |
| Σ EC_d — 상수 20,000,000 | 140,000,000 → 비중 80.1280% → ⑤' 3.308946 (표기 3.31) |
| 현행 | PA 179,916,643 · PEC 140,000,000 → 56.2386% → ⑤ 2.322416 (표기 2.32) |
| 전 구간(179일) | 현행 56.6270% ⑤ 2.592552 → 역산 79.2070% 3.626329 / 상수 79.8401% 3.655318 |
| SA_d 범위(전 구간) | 72,741,770 ~ 85,605,273 |

과제에 적힌 80.6716% / 80.1290% 와 0.03pp 이내 차이. 경계 규약(adv ≤ d · due > d)이나 기간(08-21~27 로 잡으면 80.6936% / 80.1378%)에서 갈리는 것으로 보임 — SA_d 경계 규약 확정 필요(`확인 필요`).

## (가) ⑤ 값 흐름 — `파일:줄 | 무엇 | 교체 시 손볼 것`

### 원장 (단일 원천)

| 파일:줄 | 무엇 | 교체 시 손볼 것 |
|---|---|---|
| P/daily_ledger.py:178 | `TY5_EXPR = 'ty4 * psa / tot'` — ⑤ 식 한 줄 | 식은 그대로 두고 인자 뜻만 바꿀 수 있음(psa→ΣSA_d, psc→ΣEC_d). 이름을 바꾸면 TY5_JS·build_app ty5()·검사기 정규식이 함께 흔들림 |
| P/daily_ledger.py:181-190 | `def ty_asset(ty4, psa, psc)` — 파이썬 ⑤ | docstring·인자 뜻(기간 유량 → 일자 잔액 합) |
| P/daily_ledger.py:210-216 | `TY6_PSC = 0` · `TY6_EXPR = 'ty5(..., third, TY6_PSC)'` — ⑥이 ⑤ 함수를 거침 | ⑤ 인자가 잔액 합이 되면 ⑥에 넣을 셋째 인자 재정의(행 하루의 SA_d·EC_d) |
| P/daily_ledger.py:244 | `TY5_JS` — TY5_EXPR 문자열 파생 | 자동 |
| P/daily_ledger.py:492-493 | `wk_psc = D(CASH) * D(len(wk))` · `wk_ty5 = r6(ty_asset(wk_ty, D(wk_ex), wk_psc))` | ΣSA_d·ΣEC_d 로 교체 (wk_ex 는 ④·툴팁 PA 에 계속 쓰임) |
| P/daily_ledger.py:500-501 | `fu_psc` · `fu_ty5` (전 구간) | 동일 |
| P/daily_ledger.py:538-547 | facts 키 `weekPsc`·`weekTyAsset`·`weekTyAssetRaw`·`fullPsc`·`fullTyAsset`·`fullTyAssetRaw` | 값은 자동. `weekSA`·`weekEC`·`fullSA`·`fullEC`·`saByDate`·`ecByDate` 키 추가 |
| P/ledger_facts.json:53,56 · fullTyAsset 2.59 | 2.32 · 2.322416 | 재생성 |

### 파생 모델·화면 생성기

| 파일:줄 | 무엇 | 교체 시 손볼 것 |
|---|---|---|
| P/roster16_model.py:140-142 | `ty_asset(ty4, psa, ec_days)` 껍질 — `CASH × ec_days` | 날짜 집합을 받아 ΣSA_d·ΣEC_d 를 넘기는 껍질로 |
| P/roster16_model.py:151-153 | `agg()` — `psc=CASH*ec_days, tyAsset=…` | 동일 (DSUM·MSUM) |
| P/roster16_model.py:157-158 | `AUG_CARD tyAsset(…, EC_MONTH_AUG)` | 동일 |
| P/build_app.py:1318 | `function ty5(ty4, psa, psc){ @@TY5JS@@ }` | 자동 |
| P/build_app.py:1319 | `var TY6_PSC = @@TY6PSC@@` | ⑥ 인자와 짝 |
| P/build_app.py:1932-1935 | `tyAssetOf(ty4, psa)` — `psc = cashRow().amount * ecDays()` | 화면 DAILY(정산예정일 축)에 잔액이 없음 → 행마다 `sa`·`ec` 를 실어 Σ 로 냄. `ecDays()` 폐기 |
| P/build_app.py:1982-1987 | 툴팁 행 PA · PEC · `EC n일 합` | ΣSA_d · ΣEC_d 행으로 |
| P/build_app.py:2118-2120 | simRun `PEC = SIM.cash * ECD` · `TY5 = ty5(TY4, PA, PEC)` | 시뮬 채권 `sd`·`dd`·`A`(simBond :2085-2093)로 SA_d 산출 함수 추가 |
| P/build_app.py:2277-2284 | 시뮬 결과 카드 툴팁 `R.PEC` | 동일 |
| P/build_app.py:2866-2875 | xls-profit-status 미리보기 `tyA = tyAssetOf(…)` | 함수 따라 자동 |
| P/build_app.py:3482-3490 | `@@LEDGER@@`(js_array) · `@@TY5JS@@` · `@@TY6PSC@@` 치환 | js_array(daily_ledger.py:449-457)에 `sa`·`ec` 필드 추가 |
| P/build_sim_static.py:99-100 | `PSC = CASH * ECD` · `TY5 = LG.ty_asset(TY4, PSA, float(PSC))` | SA_d 산출 추가 (float 경로) |
| P/build_sim_static.py:282-291 | 시뮬 낱장 툴팁 PA/PEC/EC n일 | 동일 |
| P/sim_facts.py:139 | `'ty5': fx(R['TY5'], 2)` | 자동 |
| P/sync_profit_static.py:129-130 | `_wkasset = RM.ty_asset(…, len(LEDGER 구간))` | 인자 교체 |
| P/sync_profit_static.py:133-139 | VIEW — DSUM/MSUM `tyAsset` | 자동 |
| P/sync_profit_static.py:192-197, 222-223 | `TIP5`(PA/PEC/EC n일 합) · `put_tips(psa, ec_days)` → `RM.CASH * ec_days` | 툴팁 재작성 |

### 엑셀

| 파일:줄 | 무엇 | 교체 시 손볼 것 |
|---|---|---|
| P/build_xlsx.py:306-307 | 투자수익현황 시트 B8 = `pct(ty5)` — **값 셀** (수식 아님) | 값이라 시트에 날짜별 열 불필요. 값은 :328 `ty_asset(tot['ty'], tot['exec'], _ec_days(frm, to))` 인자만 교체 |
| P/build_xlsx.py:311-313 | `_ec_days()` — 구간 원장 일수 | 폐기 또는 날짜 집합 반환으로 |
| P/build_audit_xlsx.py:1086 | 검산 엑셀 일별!J = `=순현금` (EC 상수 27칸) | **수식 통합문서**. EC_d 열 유지(상수) 또는 `=총투자자산-SA_d` 역산 스위치 |
| P/build_audit_xlsx.py:1103-1105 | ECN 주석 「PEC 는 순현금 x 조회 일수」 | 문구 |
| P/build_audit_xlsx.py:1158-1159 | 기간집계 `PEC 순현금 합 = SUMIFS(일별!J, 조회기간)` | `ΣSA_d`·`ΣEC_d` 행 추가. 일별 시트에 SA_d 열 신설: `=SUMIFS(채권!J, 채권!F,"<="&A_r, 채권!G,">"&A_r)` (채권 F=선정산일 · G=정산예정일 · J=Ai, :1050-1061) |
| P/build_audit_xlsx.py:1165, 1214 | 기간집계 ⑤ 행 = `=입력!C19` | 참조 유지 |
| P/build_audit_xlsx.py:1907-1914 | 입력!C19 F5 = `ROUND(④×PA/(PA+PEC),6)` — 통합문서 유일한 ⑤ 계산 칸 | 새 식으로 (④ × ΣSA ÷ (ΣSA + ΣEC)) |
| P/build_audit_xlsx.py:1682-1698 | 화면대조 `주간 PEC = 순현금 × 주간 일수` · 전 구간 PEC | facts 새 키로 |
| P/build_audit_xlsx.py:1767-1771 | 조회기간 ⑤ · PEC | 동일 |
| P/build_audit_xlsx.py:1871-1875, 2096-2101 | 정의 매핑 · 기호 사전 `wPYMR = PYMR x PA / (PA + PEC)` | 문구 |
| P/build_audit_xlsx.py:64-68 | facts 키 매핑 `주간 PEC: weekPsc` 등 | 키 추가 |
| P/roster16_apply.py:30-33, 263 · P/apply_duration.py:93,153-191 | 정적 낱장·xlsx B8 을 DSUM tyAsset 으로 패치하던 구식 스크립트 | 현행 파이프라인 밖 — 손대지 않음 |

### 문서 생성기·시드 (숫자·산식이 손으로 적힌 자리)

| 파일:줄 | 무엇 | 교체 시 손볼 것 |
|---|---|---|
| P/build_calc.py:25, 106, 117-119, 124-129, 139 | `PEC = weekPsc` · `share = PA/(PA+PEC)` · p5(PEC = EC×7일) · p7(wPY_MR) · CHAIN | p5·p7·CHAIN 재작성. 날짜별 SA_d·EC_d 표를 대입 단계로 |
| P/testcase_table.py:232-233, 317-319 | `PEC = ( Σ EC_d )` · `PY_t = PY_a × PA ÷ (PA + PEC)` · 현황 카드 ⑤ 행 `PEC %s원`(weekPsc) | 산식 문자열·키 |
| P/termsfacts.py:83, 87 | 토큰 `weekPsc`·`weekTyAsset` | `weekSA`·`weekEC` 토큰 추가 |
| P/termsdoc_seed.json:634 | EC 항 `our_value`/`screen` `{{weekPsc}}` | 문장 |
| P/termsdoc_seed.json:762-770 | 42항 PY_t (quote 는 대표 원문이라 손대지 않음 · plain·note) | plain·note |
| P/termsdoc_seed.json:776-785 | 43항 PSC `formula: PEC = ( Σ EC )` · `our_value {{weekPsc}}` | 문장 |
| P/termsdoc_seed.json:817-835 | `pending_formula.formula: ⑤ = (④ × PA) ÷ (PA + PEC)` (basis_formula 와 같은 동안 「미확정」 배지, build_termsdoc.py:235-246) | formula 한 줄 → 배지 상태도 바뀜 |
| P/final_terms.json:254-258 | var PEC formula/plain | 재작성 |
| P/final_terms.json:269-275 | var PY_t `PY_t = PY_a × PA ÷ (PA + PEC)` | 재작성 |
| P/final_terms.json:290, 310-311, 314-315, 328-329 | calc.steps `PEC 140,000,000` · `④ 비중 0.562386` · `⑤ 2.322416% 화면 2.32%` · 검산 `PY_t = 7,429,796 ÷ (PA+PEC)` | 손으로 적힌 값 — 전량 |
| P/dm_0901/symbol_rule_0901.md:79, 81, 113, 128 | 정본 기호표 `PEC = Σ EC(d-1)` · `wPY_{MR} = PY_{MR} × PA ÷ (PA + PEC)` | 정본 재작성 |
| P/meeting_0901/testcase.json:55, 57 | 산식 문자열 | 재작성 |
| P/meeting_0901/testcase.json:1482, 1657-1658, 2118-2122 | `PEC null` · `PEC 140,000,000 · wPYMR 2.24%` · 현황 카드 ⑤ 2.24% | 산식 + 값 (2.24 는 9/2 규칙 전 값) |
| P/meeting_0901/steps_all.json:4073-4128, 4150-4160 | ⑤ 칸(2.25% · ④ 3.992511% · 비중 0.5624602) · PEC 칸 | build_steps_html 이 그대로 폄 — 재작성 (값도 이미 원장 2.32 와 어긋남) |
| P/symbol_glossary.json:926-948, 1265-1270 | PSC/PEC 항 · `wPY_{MR} = PY_{MR} x PA / (PA + PEC)` | 재작성 |
| P/glossary_manuscript.md | PEC 37곳 · `PA + PEC` 10곳 · 2.25% 5곳 · :3016 비율 0.562460 | 원고 손질 |
| P/ceo_inquiry.md · P/feasibility.md · P/capability_manuscript.md · P/ceoq_seed.json:182-194,425-429 | 2.25% · `PA + PEC` · ⑤ 문항 | 문구 |
| P/verifiers.md · P/value_lineage.md · P/meeting_0901/merge/formulas.json:1015-1045 · screen_map.json · xlsx_map.json | 참고·기록 문서 | 기록 문서라 필수 아님 |

### 산출물 (재생성으로 따라옴)

| 파일:줄 | 무엇 |
|---|---|
| R/app.html:1318, 2460-2470, 2501, 2520, 2813, 3401, 3409 | ty5·tyAssetOf·카드·툴팁·xls 미리보기 |
| R/invest-profit.html:174-175 (2.32) · invest-profit--weekly.html:181 (2.63) · invest-profit--monthly.html:181 (2.59) · invest-profit--empty.html:180 · invest-sim--result.html:376-377 (1.08) | 정적 낱장 카드 |
| R/xls-profit-status.html:139 | 2.25% — 이미 원장 2.32 와 어긋남. 값을 쓰는 현행 생성기 없음(build_xlsx.py:344 는 파일바만) → `확인 필요` |
| R/calc.html · steps-all.html · final-terms.html · terms-edit.html · glossary.html(2.25% 다수·:2633 0.562460) · capability.html:1303 · inquiry.html:117-132 · feasibility.html:753 · ceo-questions.html · review.html:130 | 문서 화면 |
| R/assets/xlsx/투자수익현황_*.xlsx 6종 B8 | 값 셀 |
| P/검산_투자자어드민_20260901.xlsx | 수식 통합문서 |
| P/_fig/invest-profit*.html 4종 · _fig/invest-sim--result.html:370 · _fig/xls-profit-status.html:141 | Figma 스테이징 사본(prep_fig sync) |
| P/calc.fragment.html · steps_all.fragment.html · final_terms.fragment.html · final-terms-edit.fragment.html · terms-edit.fragment.html | 조각 |

## (나) 새로 필요한 입력

| 항목 | 원장에 있는가 | 어디에 무엇으로 |
|---|---|---|
| SA_d (d 마감 미회수 A_i 합) | 없음. `LEDGER` 는 정산예정일 축 유량(exec·profit·repay·wx)만 실음 | `daily_ledger.py` `_daily()`(:396-425) 옆에 `sa_of(d) = Σ ai (adv ≤ d, due > d)` 를 두고 LEDGER 행에 `sa` 키로 실음. 경계 규약(adv ≤ · due >)을 한 줄로 못 박음. 검증: `sa_of(ASOF) == EXEC == BOOK` |
| EC_d (d 마감 순현금) | 없음. `CASH` 상수 하나(:56) | 선택지 두 개 — (a) `CASH` 상수, (b) `TOTAL − SA_d` 역산(총자산 100,000,000 고정, 08-27 앵커에서 SA=80,000,000·EC=20,000,000 으로 닫힘). 모드 상수 `EC_MODE` 한 줄 + LEDGER 행 `ec` 키 |
| `facts()` 키 | `weekPsc`·`fullPsc` 만 | `weekSA`·`weekEC`·`fullSA`·`fullEC`·`saByDate`·`ecByDate`(6자리 아닌 원 단위). `weekPsc`·`fullPsc` 는 유지(툴팁 PEC 를 계속 보일지 결정) |
| 화면 JS 데이터 | `DAILY` 배열(js_array :449-457)에 sa·ec 없음 | js_array 에 `sa:%d, ec:%d` 추가 → `tyAssetOf` 가 `sum(rows,'sa')`·`sum(rows,'ec')` 로 냄. 주별·월별 롤업(rollupWeeks·rollupMonths)에도 sa·ec 합산 필드 필요 |
| 시뮬레이션 | 채권 행 `sd`·`dd`·`A` 만 | `simRun`(build_app.py:2095-2140)·`build_sim_static.run`(:80-116)에 날짜별 SA_d 함수. EC_d 는 `SIM.cash` 상수 |
| 검산 엑셀 | 채권 시트 F(선정산일)·G(정산예정일)·J(Ai) 있음 | 일별 시트 SA_d 열 `SUMIFS(채권!J, 채권!F,"<="&A, 채권!G,">"&A)` · EC_d 열(J 유지 또는 `총투자자산−SA`) · 기간집계 ΣSA·ΣEC 행 · 입력!C19 새 식 |
| 문서 토큰 | termsfacts 에 `weekPsc` 뿐 | `weekSA`·`weekEC`·`weekShare`(비중) 토큰 |

## (다) 기대값을 박아 둔 검사기

⑤ 값 2.32·2.322416·0.562386 을 리터럴로 박은 검사기는 **0건**. 전부 `ledger_facts.json` 을 읽거나 산식을 다시 계산함. 산식을 자기 안에 갖고 있어 교체 시 함께 고쳐야 하는 것이 아래.

| 파일:줄 | 무엇 | 손볼 것 |
|---|---|---|
| P/verify_final_terms.py:162, 175-180 | `PEC = L.CASH * len(WEEK_DAYS)` · `SHARE`·`WPYMR_DAY/2DP/REC = … × PA ÷ (PA + PEC)` | 재계산 식 교체 |
| P/verify_final_terms.py:203(A3), 222-226(A10), 243-244(B3), 255(B9), 284-291(C3·C5), 314-327(D3·D4), 715-721(I16·I17), 758-759(I26), 883-885(K13) | PEC = facts.weekPsc · ⑤ 재현 · 원고 PEC/비중 · 검산 ÷(PA+PEC) · hover 툴팁 PA·PEC · EC×일수=PEC 문장 | 12개 판정 |
| P/verify_identity.js:92-93, 158-161 | `psc = CASH * nd` · `ty5 = r6(ty4 * ex / (ex + psc))` 자체 계산 | 식 교체 (PAGE 문자열 안) |
| P/verify_identity.js:196-199 | `tyAssetWant(ty4, psa, rs)` — `CASH * ecDaysOf(rs)` | 식 교체 |
| P/verify_identity.js:356-392 | 「배율 = PSA/(PSA+PSC) 기간별 대조」 · `wantK = exec/(exec+psc)` · 배율이 기간마다 달라야 함 | 배율 정의 교체 |
| P/gate_prototype.js:330-378 | 툴팁 PA·PEC 로 ⑤ 되짚기 · `five === weekTyAsset` · `psa/psc === weekExec/weekPsc` | 툴팁 항목명·키 교체 |
| P/verify_proto.js:808-810, 829-832, 861, 883 | `psc: weekPsc` · `'PEC'+psc+'원'` 툴팁 문자열 · ⑤ facts 대조 | 툴팁 문자열만 |
| P/verify_docnums.py:66-94 | `ratio = pa/(pa+pec)` · `PA비중` · `5(평균순현금)` · `5(잔액)` 정식 표기 못 | 못 재정의 (문서 숫자 검사가 이 못으로 판정) |
| P/verify_steps_all.py:193, 213-215 | `dl.ty_asset(o4, pa, D(F['weekPsc']))` · ⑤ 칸 = weekTyAssetRaw | 인자 교체 |
| P/verify_app.js:866-877 | `ty5body: /ty4 \* psa \/ tot/` 1건 요구 · `hard5` 정규식 | TY5_EXPR 문자열이 바뀌면 정규식 교체 |
| P/verify_sim.js:768-785 | 동일 + `simRunUsesTy5` | 동일 |
| P/audit_xlsx_check.py:541-545, 592, 963-1016 | facts 대조(주간 PEC·⑤) · ⑤ 표식 · 「PA·PEC 를 함께 문 수식 셀 하나뿐」 · `'PA + PEC'` 문자열 검사 | 셀 이름·문자열 교체 |
| P/verify_crossscreen.py:86, 162-163 | xlsx B8 · xls-profit-status.html ⑤ ↔ DSUM tyAsset | 자동 따라옴. 다만 :83 파일명 `_2026-08-21_2026-08-27` 이 자산 `_08-20_08-26` 과 어긋남 → `확인 필요` |

## 이미 원장과 어긋난 자리 (교체와 무관하게 남아 있는 것)

| 자리 | 값 | 원장 |
|---|---|---|
| R/xls-profit-status.html:139 · _fig 동일 | 2.25% | 2.32 |
| R/capability.html:1303 · glossary.html(5곳) · inquiry.html(4곳) | 2.25% | 2.32 |
| P/meeting_0901/steps_all.json:4073-4128 · testcase.json:1657 · formulas.json | 2.25% / 2.24% · 비중 0.562460 | 2.32 · 0.562386 |

## 교체 작업량 추정: 파일 21개(원장·생성기 10 + 시드·원고 11), 검사기 10개 (산출물 재생성 약 40개 별도)
