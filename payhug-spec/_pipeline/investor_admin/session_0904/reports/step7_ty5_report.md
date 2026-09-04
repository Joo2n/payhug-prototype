# ⑤ 투자자산 대비 연환산수익률 — 새 산식 적용 보고

새 산식 `⑤ = PM × 365 ÷ ( Σ( A_i × D_i ) + PEC ) = ④ × AD ÷ ( AD + PEC )`, 코드 이름 `ad`.
기본 조회기간(08-20 ~ 08-26) 결과 **AD 556,626,436 · 비중 0.799031 · ⑤ 3.299662 → 3.30%** (④ 4.129577 그대로).

## 하지 않은 것 · 다르게 한 것

| 구분 | 내용 |
|---|---|
| 하지 않음 | 시드·원고 11개, 검사기 10개, `final_terms.json`, `verify_final_terms.py`, `build_symreview.py`, 스크래치패드 `ceo_review.html`, CSS, 사이드바, 대표 원문 인용, ④ 산식, 투자자산 화면 값. 검사기는 돌리지 않았습니다 |
| 하지 않음 | `검산_투자자어드민_20260901_유휴20/25/30.xlsx` 3벌은 9/2 산출물이고 `build_audit_xlsx.py` 가 만들지 않아 옛 식(`입력!C19 = ④ × PA ÷ (PA + PEC)`)이 그대로 남아 있습니다. 어느 생성기가 내는지 `확인 필요` |
| 다르게 함 | ⑥ 의 `TY6_EXPR` 에서 `ty5()` 둘째 인자(옛 `third`=PA)를 그 행의 `Σ(Ai × Di) = ③ × W` 로 바꿨습니다(`third * w`). 지시문의 「셋째 인자를 ad 로」는 PEC 자리(`TY6_PSC`)가 아니라 PA 자리로 읽었습니다. `TY6_PSC` 는 행 하루의 PEC 이고 일별 EC 원장이 없어 0 을 유지합니다. 0 인 동안 ⑥ = ④ 인 성질은 그대로이며 179행 전부 옛 ty 와 일치합니다 |
| 다르게 함 | 「대표 재전달 대기」→「대표 확인 대기」는 ⑤ 툴팁 행에만 적용했습니다. 공용 `PEND_ROW` 를 바꾸면 ③·⑥ 툴팁(둘 다 실제로 대표 재전달 대기)까지 바뀌므로 `PEND5_ROW` 를 따로 두어 ⑤ 툴팁 세 곳(수익 카드·시뮬 카드·낱장)만 씁니다 |
| 추가로 함 | `xls-profit-status.html`(수익 현황 엑셀 미리보기 낱장) 8행 ⑤ 값 `2.32%` → `3.30%`. 지시 목록에 없지만 같은 화면의 xlsx B8 이 3.30% 가 되어 값이 어긋나므로 맞췄습니다. 이 낱장의 값 셀을 쓰는 생성기가 없어(`build_xlsx.py:344` 는 파일바만) 손편집입니다 |
| 추가로 함 | 검산 엑셀 `화면대조` 시트에 `주간 Σ(Ai x Di)`·`전 구간 Σ(Ai x Di)`(facts `weekAD`·`fullAD`) 두 행과 모델 잔차 `조회기간 Σ(Ai x Di)` 한 행. ⑤ 의 새 입력이 facts ↔ 통합문서로 이어지게 한 것으로, 행 번호가 하나씩 밀려 `audit_xlsx_check.py` 가 행 번호를 리터럴로 물고 있으면 갱신 대상입니다 |
| 그대로 둠 | 검산 엑셀 라벨 `⑤ 산식 (미확정 · 대표 재작성 대기)`(입력!B19 · 읽는 법)와 `정의 매핑` 의 「대표 재작성 대기 A-01」 문구. 지시가 툴팁 한 문구로 한정되어 손대지 않았습니다. 사실과는 어긋나므로 다음 조 판단 대상입니다 |
| 그대로 둠 | `calc.html`·`final-terms.html` 에 옛 문면 `( PA + PEC )` 잔존 — `build_calc.py`·`final_terms.json` 산출물이라 범위 밖입니다 |

## (가) 고친 파일

경로는 `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/` 아래입니다.

### daily_ledger.py

| 줄 | 옛 | 새 |
|---|---|---|
| 158 | `⑤ = (④ x PSA) / (PSA + PSC)` | `⑤ = PM x 365 / (Σ(Ai x Di) + PEC) = ④ x Σ(Ai x Di) / (Σ(Ai x Di) + PEC)` |
| 168-177 | ⑤ 주석 「대표 정의서 원문 그대로 · 재전달 대기」 | 원문은 수식 오류로 닫힘 · 우리 확정안 · AD = PD 의 분자(행 wx) |
| 179 | `TY5_SOURCE = 'ceo_definitions.md [2번 이미지] · 대표 재전달 대기'` | `'⑤ = PM x 365 / (Σ(Ai x Di) + PEC) · 대표 확인 대기'` |
| 181 | `TY5_EXPR = 'ty4 * psa / tot'` | `TY5_EXPR = 'ty4 * ad / tot'` |
| 184-186 | `def ty_asset(ty4, psa, psc)` · `tot = psa + psc` · docstring PSA | `def ty_asset(ty4, ad, psc)` · `tot = ad + psc` · docstring `④ x AD / (AD + PSC)` |
| 215-217 | ⑥ 주석 | AD 자리 = 행의 Σ(Ai x Di) = ③ x W, PEC 자리 = 행 하루 EC |
| 222 | `TY6_EXPR = 'ty5(…, third, TY6_PSC)'` | `TY6_EXPR = 'ty5(…, third * w, TY6_PSC)'` |
| 248 | `TY5_JS = 'var tot = psa + psc;…'` | `TY5_JS = 'var tot = ad + psc;…'` |
| 426-427 | 일별 행 dict | `ad=g['wx']` 필드 추가 |
| 457-460 | `js_array` `{…, ty:%s}` | `{…, ty:%s, ad:%d}` |
| 479-481 | `month_rollup` 출력 | `ad=int(g['wx'])` 추가 |
| 489-491 | facts 주석 「PEC = 순현금 x 조회 일수」 | AD = 기간 Σ(Ai x Di) 병기 |
| 495 · 500 · 503 | `wk_wraw = r6(D(sum(r['wx']…)))` · `ty_asset(wk_ty, D(wk_ex), wk_psc)` | `wk_ad = sum(r['ad']…)` · `r6(D(wk_ad)/D(wk_ex))` · `ty_asset(wk_ty, D(wk_ad), wk_psc)` |
| 507 · 508 · 511 | 전 구간 동일 | `fu_ad` · `ty_asset(fu_ty, D(fu_ad), fu_psc)` |
| 548 | `weekPsc=…, weekTyAsset=…` | `weekAD=int(wk_ad)` 추가 |
| 555 | `fullPsc=…, fullTyAsset=…` | `fullAD=int(fu_ad)` 추가 |
| 560-562 | — | `monthAD=[[달, ad]]` · `adByDate={날짜: ad}` 추가 |

### build_app.py

| 줄 | 옛 | 새 |
|---|---|---|
| 1305-1308 | 주석 「대표 재전달 대기 — ⑤ 는 수식 새로 작성해 전달」 | ③·⑥ 은 대표 재전달 대기, ⑤ 는 우리 확정안 · 대표 확인 대기 |
| 1311 | — | `var PEND5_ROW = '…<span>미확정</span><span>대표 확인 대기</span>…'` |
| 1315 | 주석 「대표가 ⑤ 를 새로 주면」 | 「⑤ 산식은 daily_ledger.ty_asset 한 곳만 고치면」 |
| 1317 | `function ty5(ty4, psa, psc)` | `function ty5(ty4, ad, psc)` |
| 1318 | 주석 `PSC` | `PEC` |
| 1864 · 1866-1868 | `rollupBy` 버킷 `{…, wx:0, days:0}` · `g.wx += r.wx` | `ad:0` 추가 · `g.ad += r.ad` |
| 1923-1926 | 주석 「PEC 를 만들어 넘기기만 · psa·psc」 | 「AD·PEC 를 만들어 넘기기만 · AD = 행 ad 의 합 · ad·psc」 |
| 1934-1937 | `function tyAssetOf(ty4, psa){ … ty5(ty4, psa, psc) }` | `function adOfRows(rs){ return sum(rs,'ad'); }` · `tyAssetOf(ty4, rs){ … ty5(ty4, adOfRows(rs), psc) }` |
| 1966 | `tyAssetOf(tyExec, exec)` | `tyAssetOf(tyExec, rows)` |
| 1988 | 툴팁 머리 `( PY_a × PA ) ÷ ( PA + PEC )` | `PM × 365 ÷ ( Σ( A<sub>i</sub> × D<sub>i</sub> ) + PEC )` |
| 1990 | 행 `PA | 기간 투자실행금 · 값원` | 행 `Σ( A<sub>i</sub> × D<sub>i</sub> ) | 값원` (`fmt(adOfRows(rows))`) |
| 1993 | `PEND_ROW` | `PEND5_ROW` |
| 2121-2122 | `PwD = PA ? mat.reduce(A×D)/PA : 0` | `var AD = mat.reduce(A×D)` · `PwD = PA ? AD / PA : 0` |
| 2127 | `TY5 = ty5(TY4, PA, PEC)` | `TY5 = ty5(TY4, AD, PEC)` |
| 2146 | `SIM.result` | `AD:AD` 추가 |
| 2287 · 2289 · 2292 | 시뮬 결과 카드 ⑤ 툴팁 (머리 · `PA` 행 · `PEND_ROW`) | 수익 카드와 같은 새 머리 · `Σ( A_i × D_i )` 행 `fmt(R.AD)` · `PEND5_ROW` |
| 2877 | 엑셀 미리보기 `tyAssetOf(tyE, pexec)` | `tyAssetOf(tyE, rw)` |

### build_sim_static.py

| 줄 | 옛 | 새 |
|---|---|---|
| 95-96 | `PSD = (sum(A×D) / PSA)` | `AD = sum(A×D)` · `PSD = AD / PSA` |
| 101 | `TY5 = LG.ty_asset(TY4, PSA, float(PSC))` | `TY5 = LG.ty_asset(TY4, float(AD), float(PSC))` |
| 117 | `run()` 결과 | `AD=AD` 추가 |
| 121-126 | 주석 · `PEND_ROW` 만 | 주석 갱신 · `PEND5_ROW` 추가 |
| 288 · 290 · 293 · 298 | 툴팁 머리 · `PA` 행(`fmt(R['PSA'])`) · `PEND_ROW` | 새 머리 · `Σ( A_i × D_i )` 행(`fmt(R['AD'])`) · `PEND5_ROW` |

### sync_profit_static.py

| 줄 | 옛 | 새 |
|---|---|---|
| 129 | `RM.ty_asset(_wtot['ty'], _wtot['exec'], …)` | `RM.ty_asset(_wtot['ty'], _wtot['wx'], …)` |
| 131-140 | `VIEW` 튜플 8칸 | 9칸 — `ad`(`DSUM['ad']` · `int(_wtot['wx'])` · `MSUM['ad']`) |
| 176-181 | 주석 · `PEND_ROW` 만 | 주석 갱신 · `PEND5_ROW` 추가 |
| 198 · 200 · 203 | `TIP5` 머리 · `PA` 행 `%(pa)s` · `PEND_ROW` | 새 머리 · `Σ( A_i × D_i )` 행 `%(ad)s원` · `PEND5_ROW` |
| 228 · 231 | `put_tips(s, psa, psm, ty4, pd, ec_days)` · `pa=f(psa)` | `put_tips(s, psa, psm, ty4, pd, ad, ec_days)` · `ad=f(ad)` |
| 242 | `put_card` 언패킹 8칸 | 9칸(`_ad`) |
| 347 · 349 | `put_tips(…, v[3][3], ec_days())` · `put_tips(s,0,0,0,0, ec_days())` | `…, v[8], ec_days()` · `…,0,0,0,0,0, ec_days()` |

### roster16_model.py

| 줄 | 옛 | 새 |
|---|---|---|
| 133-135 | 주석 `⑤ = (④ x PSA) / (PSA + PSC)` | `⑤ = PM x 365 / (Σ(Ai x Di) + PEC) = ④ x AD / (AD + PSC)` |
| 140-142 | `ty_asset(ty4, psa, ec_days)` → `L.ty_asset(…, D(psa), …)` | `ty_asset(ty4, ad, ec_days)` → `L.ty_asset(…, D(ad), …)` |
| 150-154 | `agg()` — `wv = r6(D(sum wx)/D(ex))` · `tyAsset=ty_asset(tv, ex, ec_days)` | `ad = sum(wx)` · `wv = r6(D(ad)/D(ex))` · 반환에 `ad=ad` · `tyAsset=ty_asset(tv, ad, ec_days)` |
| 159 | `AUG_CARD tyAsset=ty_asset(AUG['ty6'], AUG['exec'], …)` | `ty_asset(AUG['ty6'], AUG['wx'], …)` |

### build_xlsx.py

| 줄 | 옛 | 새 |
|---|---|---|
| 306-307 | 주석 `⑤ wPYMR = (④ PYMR × PA) / (PA + PEC)` | `⑤ PY_t = PM × 365 / (Σ(Ai x Di) + PEC) = ④ × AD / (AD + PEC)` · AD 는 표 wx 합 |
| 329 | `ty_asset(tot['ty'], tot['exec'], _ec_days(frm, to))` | `ty_asset(tot['ty'], tot['wx'], _ec_days(frm, to))` (`_ec_days` 는 PEC 용으로 유지) |

### build_audit_xlsx.py

| 줄 | 옛 | 새 |
|---|---|---|
| 65 · 69 | facts 키 매핑 | `'주간 Σ(Ai x Di)': 'weekAD'` · `'전 구간 Σ(Ai x Di)': 'fullAD'` 추가 |
| 677-683 | 입력!C19 주석 「지금 들어 있는 것은 대표 정의서 원문 산식」 · 출처 셀 `ceo_definitions.md [2번] 이미지의 ⑤ — … 대표 재작성 대기 (A-01)` | 주석 「우리 확정안 ⑤ = PM x 365 / (Σ(Ai x Di) + PEC)」 · 출처 셀 `⑤ = PM x 365 / (Σ(Ai x Di) + PEC) · daily_ledger.TY5_EXPR — … 대표 확인 대기 (A-01)` |
| 1516 · 1528 | 화면대조 `sv_rows` | `주간 Σ(Ai x Di)` · `전 구간 Σ(Ai x Di)` 행 추가 |
| 1776-1777 | 모델 잔차 `res_rows` | `조회기간 Σ(Ai x Di)` = 기간집계 B9 ↔ 화면대조 주간 Σ 행 추가 |
| 1912-1920 | `F5 = IF(B5+B15=0,0,ROUND(B13*B5/(B5+B15),6))` (B5 = PA) | `F5 = IF(B9+B15=0,0,ROUND(B13*B9/(B9+B15),6))` (B9 = Σ(Ai x Di)) · 주석 갱신 |
| 2106-2107 | 기호 사전 `wPYMR … = PYMR x PA / (PA + PEC)` | `= PM x 365 / (Σ(Ai x Di) + PEC) = PYMR x Σ(Ai x Di) / (Σ(Ai x Di) + PEC)` |

기간집계 `Σ(Ai x Di)` 행(B9 = `SUMIFS(일별!K, 조회기간)`)과 일별 시트 K열 `Σ(Ai x Di)` 는 이미 있어 신설하지 않았습니다.

### 손편집 낱장 `/Users/semi/cursor/payhug-investor-admin/`

| 파일:줄 | 옛 | 새 |
|---|---|---|
| invest-profit.html:174-175 | 툴팁 머리 `( PY_a × PA ) ÷ ( PA + PEC )` · `PA 179,916,643원` 행 · `대표 재전달 대기` · 값 `2.32` | `PM × 365 ÷ ( Σ( A_i × D_i ) + PEC )` · `Σ( A_i × D_i ) 556,626,436원` · `대표 확인 대기` · `3.30` |
| invest-profit--weekly.html:180-181 | `PA 622,381,520원` · `2.63` | `Σ 1,883,200,800원` · `3.71` |
| invest-profit--monthly.html:180-181 | `PA 4,673,981,320원` · `2.59` | `Σ 14,179,998,792원` · `3.66` |
| invest-profit--empty.html:180-181 | `PA 0원` · `0.00` | `Σ 0원` · `0.00` |
| invest-sim--result.html:376-377 | `PA 37,558,640원` · `1.08` | `Σ 107,082,080원` · `2.22` |
| xls-profit-status.html:139 | `2.32%` | `3.30%` |

PYa · PEC · EC 행과 ④ 툴팁의 `PA` 행은 그대로입니다.

## (나) 재생성 결과

| 순서 | 생성기 | 결과 |
|---|---|---|
| 1 | `daily_ledger.py` | `ledger_facts.json` — `weekAD 556626436` · `weekTyAssetRaw 3.299662` · `weekTyAsset 3.30` · `fullAD 14179998792` · `fullTyAssetRaw 3.655420` · `monthAD` 6달 · `adByDate` 179일. ④ `weekTyRaw 4.129577` 그대로 |
| 2 | `build_app.py` | `app.html` 242,137 bytes · 3,929 lines · 16 screens. AssertionError 없음 |
| 3 | `sync_assets_static.py` | 자산 낱장 전부 `same` |
| 4 | `sync_profit_static.py` | 4장 기록 — 카드 ↔ 표 기간 일치 |
| 5 | `build_sim_static.py` | `invest-sim.html` / `invest-sim--result.html` 기록 |
| 6 | `build_xlsx.py` | 14벌 · 미리보기 낱장 4장 파일바 동기화 |
| 7 | `build_audit_xlsx.py` | `검산_투자자어드민_20260901.xlsx` 254,167 bytes |
| 8 | `build_docs.py` | 증명서 PDF 1건 |
| 9 | `prep_fig.py sync` | 31화면 동기화 |

손편집 낱장 5장(`invest-profit.html` · `--weekly` · `--monthly` · `--empty` · `invest-sim--result.html`)은 `sync_profit_static.py`·`build_sim_static.py` 출력과 **바이트 일치**(`cmp`).

`app.html` 의 DAILY·ty5·r6·sum 을 node 로 실행해 낸 값 = 원장 값 (JS ↔ Python 6자리 일치):

| 프리셋 | 기간 | 일수 | AD | ④ raw | ⑤ raw |
|---|---|---|---|---|---|
| 일주일 | 08-20 ~ 08-26 | 7 | 556,626,436 | 4.129577 | **3.299662** |
| 금월 | 08-01 ~ 08-26 | 26 | 2,045,807,158 | 4.647234 | 3.705401 |
| 4주 | 08-03 ~ 08-26 | 24 | 1,883,200,800 | 4.650140 | 3.705630 |
| 12주 | 06-08 ~ 08-26 | 80 | 6,330,869,262 | 4.581017 | 3.656827 |
| 3개월 | 06-01 ~ 08-26 | 87 | 6,882,422,931 | 4.596199 | 3.668689 |
| 6개월 | 03-01 ~ 08-26 | 179 | 14,179,998,792 | 4.578297 | 3.655420 |

⑥ 행 ty(`ty6` → `ty5(…, third * w, 0)`) 179행 전부 옛 값과 일치.

## (다) ⑤ 값 — 자리별

| 자리 | 옛 | 새 |
|---|---|---|
| `app.html` 수익 카드 · 일주일(기본) | 2.32 | **3.30** |
| `app.html` 수익 카드 · 금월 / 4주 | 2.63 / 2.63 | 3.71 / 3.71 |
| `app.html` 수익 카드 · 12주 / 3개월 / 6개월 | 2.59 / 2.59 / 2.59 | 3.66 / 3.67 / 3.66 |
| `app.html` 엑셀 미리보기 `profit-status` 8행 | 2.32% | 3.30% (같은 `tyAssetOf`) |
| `app.html` 시뮬 결과 카드(기본 입력) | 1.08 | 2.22 |
| `invest-profit.html` | 2.32 | 3.30 |
| `invest-profit--weekly.html` (4주) | 2.63 | 3.71 |
| `invest-profit--monthly.html` (6개월) | 2.59 | 3.66 |
| `invest-profit--empty.html` | 0.00 | 0.00 |
| `invest-sim--result.html` | 1.08 | 2.22 |
| `xls-profit-status.html` 8행 | 2.32% | 3.30% |
| `투자수익현황_2026-08-20_2026-08-26.xlsx` B8 | 0.0232 | 0.0330 |
| `투자수익현황_2026-08-01_2026-08-26.xlsx` · `_08-03_08-26` B8 | 0.0263 | 0.0371 |
| `투자수익현황_2026-06-08_2026-08-26.xlsx` · `_03-01_08-26` B8 | 0.0259 | 0.0366 |
| `투자수익현황_2026-06-01_2026-08-26.xlsx` B8 | 0.0259 | 0.0367 |
| `검산_투자자어드민_20260901.xlsx` 입력!C19 | `=IF(기간집계!B5+기간집계!B15=0,0,ROUND(기간집계!B13*기간집계!B5/(기간집계!B5+기간집계!B15),6))` | `=IF(기간집계!B9+기간집계!B15=0,0,ROUND(기간집계!B13*기간집계!B9/(기간집계!B9+기간집계!B15),6))` |
| 검산 xlsx 화면대조 `주간 ⑤(%)` / `전 구간 ⑤(%)` (facts 원본) | 2.32 / 2.59 | 3.30 / 3.66 |
| `ledger_facts.json` `weekTyAsset` / `fullTyAsset` | 2.32 / 2.59 | 3.30 / 3.66 |
| `_fig/` 스테이징 사본 5장 + `xls-profit-status.html` + xlsx 6벌 | 옛 값 | 위와 동일 |

바뀌지 않은 값(확인): ④ 4.13 / 4.65 / 4.58 · ④ 툴팁 `PA 179,916,643원` · `PM 62,977원` · `PD 3.09일` · 투자자산 화면 100,000,000 / 80,000,000 / 20,000,000 / W 3.04 / S 0.07 / Ty 13.21 (`invest-assets.html` · `투자자산현황_*.xlsx` 4~6행 · `app.html` ASSET_ROWS). 나머지 xlsx 8벌(가맹점별·일별·주별·월별·투자자산현황)은 ⑤ 칸이 없어 값 변화 없음.

## (라) 옛 문면 잔존 grep

대상: `/Users/semi/cursor/payhug-investor-admin/*.html` · `_fig/*.html` · 검산 xlsx 전 셀 · 생성기 7개. 패턴 `( PA + PEC )` · `PA ÷ (` · `PA / (PA` · `ty4 * psa`.

| 파일 | 건수 | 비고 |
|---|---|---|
| `app.html` · 낱장 5장 · `xls-profit-status.html` · `_fig/` 동일 7장 | **0** | |
| 검산 `검산_투자자어드민_20260901.xlsx` 전 시트 | **0** | 새 문면 2셀(읽는 법 D73 · 입력 E19) |
| 생성기 7개(`daily_ledger` · `build_app` · `build_sim_static` · `sync_profit_static` · `roster16_model` · `build_xlsx` · `build_audit_xlsx`) | **0** | |
| `calc.html` · `final-terms.html` | 잔존 | `build_calc.py` · `final_terms.json` 산출물 — 범위 밖 |
| `검산_…_유휴20/25/30.xlsx` | 잔존(입력!C19 옛 식) | 9/2 산출물 · 생성기 미상 `확인 필요` |
| 문서 화면(`glossary.html` · `steps-all.html` · `capability.html` · `inquiry.html` 등)의 `2.25%` · `0.562460` | 잔존 | 시드·원고 산출물 — 범위 밖(지도 「이미 어긋난 자리」) |

## (마) 검사기 갱신 안내

새 키·이름: facts `weekAD` · `fullAD` · `monthAD` · `adByDate`, 원장 행 `ad`(= `wx`), JS `DAILY[i].ad` · `adOfRows(rs)` · `tyAssetOf(ty4, rows)` · `SIM.result.AD` · `PEND5_ROW`, 파이썬 `ty_asset(ty4, ad, psc)` · `TY5_EXPR = 'ty4 * ad / tot'` · `TY5_JS = 'var tot = ad + psc; …'` · `TY6_EXPR = 'ty5(…, third * w, TY6_PSC)'`, 툴팁 ⑤ 머리 `PM × 365 ÷ ( Σ( A<sub>i</sub> × D<sub>i</sub> ) + PEC )` · 행 `Σ( A<sub>i</sub> × D<sub>i</sub> ) | 값원` · 미확정 행 `대표 확인 대기`. ⑤ 툴팁에 `PA` 행 없음.

| 검사기:줄 | 옛 기대 | 새 기대 |
|---|---|---|
| `verify_app.js:868-870` · `verify_sim.js:769-771` | `ty5body: /ty4 \* psa \/ tot/` 1건 · `hard5` 정규식 `psa \+ psc` | `/ty4 \* ad \/ tot/` 1건 · `hard5` 는 `ad \+ psc\) \? ty4` 꼴로 |
| `verify_identity.js:158-161` | `psc = CASH * nd` · `ty5 = r6(ty4 * ex / (ex + psc))` | `ad = Σ rows.ad` · `ty5 = r6(ty4 * ad / (ad + psc))` |
| `verify_identity.js:196-198` | `tyAssetWant(ty4, psa, rs)` = `r2(ty4 * psa / (psa + psc))` | `r2(ty4 * sum(rs,'ad') / (sum(rs,'ad') + psc))` |
| `verify_identity.js:356-392` | 배율 `PSA/(PSA+PSC)` 기간별 대조 · `wantK = exec/(exec+psc)` | 배율 `AD/(AD+PEC)` · `wantK = ad/(ad+psc)` (기본 기간 0.799031) |
| `gate_prototype.js:356-378` | 툴팁 `PA`·`PEC` 로 ⑤ 되짚기 · `psa === weekExec` | 툴팁 `Σ( Ai × Di )`·`PEC` 행 → `ad === FACTS.weekAD` · `five = r2(four × ad/(ad+psc))` |
| `verify_proto.js:809 · 831` | `psa: weekExec` · `'PA' + psa + '원'` 툴팁 행 존재 | ⑤ 툴팁에 `PA` 행 없음 → `'Σ( Ai × Di )' + weekAD + '원'` 로(텍스트는 `Σ( Ai × Di )` 로 렌더) |
| `verify_docnums.py:66-94 · 113` | `ratio = pa/(pa+pec)` · `PA+PEC` 못 · 「PA ÷ (PA + PEC)」 | `ratio = ad/(ad+pec)` (`weekAD`) · 못 이름 `AD+PEC` |
| `verify_steps_all.py:196` | `dl.ty_asset(o4, pa, D(F['weekPsc']))` | `dl.ty_asset(o4, D(F['weekAD']), D(F['weekPsc']))` |
| `audit_xlsx_check.py:541-545` | facts 대조 항목(주간 PEC …) | `주간 Σ(Ai x Di)`=`weekAD` · `전 구간 Σ(Ai x Di)`=`fullAD` 추가, 화면대조 행 번호 +1/+2/+3 밀림(주간 Σ 30행 · 전 구간 Σ 41행 · 모델 잔차 조회기간 Σ 175행) |
| `audit_xlsx_check.py:965-1016` | 「PA·PEC 를 함께 문 수식 셀 하나뿐」(`기간집계!B5`+`B15`) · `'PA + PEC'` 문자열 0건 | 「Σ(Ai x Di)·PEC 를 함께 문 수식 셀 하나뿐」(`기간집계!B9`+`B15`) · 문자열 검사는 그대로(0건 유지) |
| `verify_crossscreen.py:257` | `_DL.TY5_SOURCE` 문구 대조 시 `'ceo_definitions.md [2번 이미지] · 대표 재전달 대기'` | `'⑤ = PM x 365 / (Σ(Ai x Di) + PEC) · 대표 확인 대기'` (배지 낱말 `미확정`은 그대로) |
| `verify_crossscreen.py:86 · 162-163` | xlsx B8 · `xls-profit-status.html` ⑤ ↔ `DSUM['tyAsset']` | 자동 따라옴 (3.30) |
| `verify_final_terms.py:162-180 · 203 · 222-226 · 243-244 · 255 · 284-291 · 314-327 · 715-721 · 758-759 · 883-885` (지도 인용 · 열지 않음) | `PEC = CASH × len(WEEK_DAYS)` · `… × PA ÷ (PA + PEC)` · hover 툴팁 `PA`·`PEC` | 다른 조 담당 — 위 새 키·문면으로 |

PEND_ROW 건수를 세는 검사기가 있으면 ③·⑥ 은 `대표 재전달 대기` 그대로, ⑤ 만 `대표 확인 대기` 로 나뉜 것을 반영해야 합니다.
