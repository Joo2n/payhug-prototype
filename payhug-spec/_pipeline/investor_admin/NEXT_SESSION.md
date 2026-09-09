# 투자자 어드민 — 다음 세션 시작점

마지막 세션 2026-09-09. 이 파일과 `session_0904/` 만 읽으면 이어서 할 수 있다. 사용자 지시 목록은 `session_0904/ORDERS_0904.md`, 이행 판정은 `session_0904/reports/orders_mid.md`·`orders_final.md`·`orders_0907.md`. V1.1 명세는 `session_0904/V11_SPEC.md`.

## 지금 상태 한 줄

기호 정리표 **V1.3**(대표님 V1.2 수정안 골격: 첨자 d = 기준일 · EC_d · PEC = Σ EC_d, ⑤ 만 우리 산식, 용어 하나로 보유 채권·연환산 수익률·검색대상기간, 표 4 = 기호·화면·툴팁)이 확정본이고 대표님과의 논의는 종결됐다. 화면(전체본·시연본)·Figma 37프레임·원고·검사기가 V1.3 과 툴팁 규칙(첫 줄 「기호 = 산식」 표 2 그대로 · 둘째 줄부터 「기호 | 값」 · 조건 「i | …」 · 연환산 행 맨 아래)으로 배포돼 있다. 투자자 화면에는 내부 검토 표시(「미확정」 배지·「대표 확인 대기」·「대표 DM」·「항등식」 등)가 0건이고 「수익 산정 기준」 구역(수수료 배분형·조달이자형)은 대표 스토리보드에 없는 것이라 없다. 대표님과의 기호·산식 논의는 2026-09-08 종결(대표님 V1.2 수정안 반영 = V1.3).

**2026-09-09 투자자 공유 정리(시연본만)**: 시연본 `7a369bd` 는 탭 제목 「PayHug 투자자 어드민」, 투자 자산 카드 「투자실행액」「순현금」 아래 「비중 … · 보관 ㈜…」 줄 없음, 현황 표 「비중」「보관」 열 없음, 「투자자산 현황」 엑셀 같은 두 열 없음. 통합본(app.html·낱장·전체본 Vercel)은 그대로다(사용자: 통합본은 나중에 맞출지 결정). 변환은 `scripts/sync_prototype.py` `investor_share()`·`patch_assets_status_xlsx()`, 게이트 검사 7건, Figma 투자 자산 9 프레임은 `prep_fig.py share` 판(신 노드 3860·3861·3862·3866·3865·3863·3864·3868·3867). 보고 `session_0904/reports/step14_figma_share.md`·`step14_qa_share.md`·`step14_figma_inspect.md`·`orders_0909.md`. **같은 날 통합본에도 적용**(사용자 「통합도 고쳐야 하는데」): 생성기 `build_app.py`·`sync_assets_static.py`·`build_sim_static.py`·`build_xlsx.py`·`sim_facts.py` 와 검증기 `verify_sim.js`·`verify_identity.js`·`verify_crossscreen.py` 를 고쳐 재생성, 전체본 **`7493d89`** 배포(카드 아래 줄 0 · 현황 표 열 5 · 시뮬 결과 카드·표 같음 · 엑셀·미리보기 시트 5열). 통합본 탭 제목·첫 화면·툴팁은 그대로. 재생성 순서 **build_xlsx → build_app**. 시연본은 재동기화 `7ba7f26`(변환기 정리 단계는 「원본에 이미 없음」 통과, 배포 게이트 43 PASS — 1차 실행의 5단계 실패는 일시적 네트워크 오류로 재실행 통과). 보고 `step15_builder_share_app.md`·`step15_qa_share_app.md`·`orders_0909b.md`.

**2026-09-09 입금부족액 0 판 (대표님 지적 「투자 수익은 투자실행액의 0.11% 여야」)**: 원장 목 규칙의 미지급률·과지급률을 0 으로(`platform_duration.py:140-141`) 두어 투자 수익 = 채권매입수수료(투자실행금의 0.1101%), 상환액 = 순지급액, 입금부족률 0.00%, 시뮬레이션 기본 미지급률·과지급률 0. 기본 검색대상기간 투자수익 **198,184** · PMR 0.110120% · ④ **12.93%** · ⑤ **10.34%** · 08-21 행 28,567. 전체본 **`2db5f01`** · 시연본 **`1af503f`** 배포, Figma 투자 자산 9·투자 수익 9 재교체(신 노드 3877·3876·3875·3879·3878·3880·3883·3882·3881 / 3886·3885·3884·3889·3888·3887·3890·3891·3892). 기호정리표 V1.3 원고의 예시값(PMR 0.033992% · PM 61,175 · ④ 3.99% · ⑤ 3.19% · LR 0.07%)은 옛 값 — `verify_final_terms.py` 원고 대조 14 FAIL 로 남김(V1.4 결정 대기). 보고 `step16_builder_zero_shortfall.md`·`step16_qa_zero.md`·`step16_figma_zero.md`·`step16_figma_inspect.md`·`orders_0909c.md`.
## 확정된 것

| 항목 | 값 | 근거 |
|---|---|---|
| `d` (V1.3) | 표 1 첨자 규칙 「하나의 일 (d = 기준일, d−1 = 기준일의 전일, d−2 = 기준일의 전전일)」. 첨자는 잔액 `EC_d` 에만, 채권은 조건 문장(「정산예정일이 d 보다 뒤인 채권」·「정산예정일이 기준일(d) 보다 뒤인 보유 채권」). 기준일 = 마감이 끝난 날이라 오늘 보면 어제. 투자자 화면에 d 표시 없음. LR 표본 「선정산일이 오늘(d 의 다음 날) 기준 20일 전부터 11일 전까지」. PEC = Σ EC_d, d ∈ P | V1.3 표 1·표 2 · `final_terms.json` · (V1.1 의 d = 오늘 안은 폐기, `session_0904/V11_SPEC.md` 는 이력) |
| 원장 시점 | `ASOF` 08-27 = **어제(마감 스냅샷 날)**. 오늘은 08-28 이고 화면에 없다. `LAST_DUE = ASOF`, 일별 표에 08-27 행, 기본 조회기간 **08-21~08-27**, 입금부족률 표본 08-08~08-17 | `daily_ledger.py:62-71` · `ledger_facts.json` |
| ⑤ 투자 자산 대비 연환산 수익률 | `PY_t = PY_a × 채권 비중 + 0 × 순현금 비중 = PM × 365 ÷ ( Σ( A_i × D_i ) + PEC )`, i 는 정산예정일이 P 안인 채권. 채권 비중 = Σ(A_i×D_i) ÷ (Σ(A_i×D_i)+PEC). 기호표 ⑤ 칸에 전개 전문(순현금 수익률 0 항·PMR·PD 대입·약분) | 교차검증 `session_0904/verify/xv_*.md` · 잔액 하루씩 7일 합 564,855,018 ≈ Σ(A_i×D_i) 559,275,516 (경계 채권 1%) |
| 기본 조회기간 값 (입금부족액 0 판) | 투자실행금 179,970,919 · 투자수익 **198,184** · 상환액 180,169,120 · PD 3.11 · PMR 0.110120% · ④ **12.93%** · Σ(A_i×D_i) 559,275,516 · PEC 140,000,000 · ⑤ **10.34%** · LR 0.00% | `ledger_facts.json` `weekExec`·`weekProfit`·`weekTy`·`weekAD`·`weekPsc`·`weekTyAsset` |
| 표기 규칙 셋 | 정의 줄은 `이름 = Σ 낱건, 범위` · 조립 산식은 이름으로만 · 한 산식 안에서 풀기/접기 혼용 금지 | `session_0904/reports/step7_notation_report.md` |
| 낱말 | 「비중」으로 통일(가중치 낱말 안 씀). 띄어쓰기 「보유 채권」「연환산 수익률」「예상 연환산 수익률」「투자 자산 대비」, 「투자실행금액 대비」는 붙임. 「투자실행액」(투자 자산)·「투자실행금」(투자 수익)은 화면 라벨 그대로 | V1.3 본문 · `final_terms.json` · `verify_final_terms.py` S7 |
| 용어 하나로 (V1.3) | 내부/외부 용어를 나누지 않음(대표님 9/8 판단). 대상정산금채권 → 보유 채권 · ty수익률 → 연환산 수익률 · 조회기간·조회대상기간 → 검색대상기간 · 조회시점의 투자자산 → 투자자산. 표 4 는 「기호 · 화면 · 툴팁」 15행 | 대표님 V1.2 수정안(`session_0904/artifact/…_V1.2_대표님수정안.docx`) · 표 4 AS-IS/TO-BE https://claude.ai/code/artifact/95990a7c-d41d-411d-90bb-78ee155f790a · `final_terms.json` `screen_terms` |
| 대표님 워드 변경 판정 (최종) | 채택: 첨자 d 규칙 · 상수 d 행 삭제 · `EC_d`·`PEC = Σ EC_d` · 「d 일 마감시점」·「기준일(d) 보다 뒤」 · 용어 하나로. 비채택: ⑤ `PM ÷ (PA + PEC)`(365 없음, 비중 재료 PA) → `PY_t = PY_a × 채권 비중 … = PM × 365 ÷ ( Σ( A_i × D_i ) + PEC )` 유지 | 대표님 V1.0 추적본(첨자 d)·V1.2 수정안(용어 통일) · 메모리 `feedback_confirmed_doc_is_baseline.md` |
| 화면 라벨·툴팁 (규칙) | 툴팁 첫 줄은 「기호 = 산식」(표 2 산식 칸 그대로, 이름 없음), 조립 산식은 이름으로(⑤ 는 `PY_t = PY_a × 채권 비중 + 순현금 수익률 × 순현금 비중` 다음 줄 `= PM × 365 ÷ ( Σ( A_i × D_i ) + PEC )`), Σ 는 정의 줄에만, 둘째 줄부터 「기호 \| 값」, 조건 「i \| 조건 · 건수」, 「연환산 \| 일부 기간의 …」 행 맨 아래. 8곳: 투자실행액 카드 `Σ A_i` · 예상 연환산 수익률 `Y_r = r × 365 ÷ D` · 가중평균 금융일수 `D = Σ( A_i × D_i ) ÷ Σ A_i` + `i \| 보유 채권 전체 · 61,760건` · 입금부족률 `LR = Σ L_i ÷ Σ A_i` + `i \| 선정산일이 오늘 기준 20일 전 ~ 11일 전 · 3,200건` · ④ `PY_a = PMR × 365 ÷ PD` · ⑤ 위 · 열머리 투자실행금 `PA = Σ A_i` + `i \| 정산예정일이 그 날짜인 보유 채권` · 열머리 연환산 수익률 `PY_a = PMR × 365 ÷ PD`. 열머리 안 패널은 대문자 변환 해제(`base.css`). 검토 표시 0건 · 「수익 산정 기준」 구역 없음 · 「기준일」 알약 없음 | `build_app.py` `YR_TIP_HEAD`·`yrTh`·`popTh`·`tyTh`·`thirdTh` · `sync_assets_static.py`·`sync_profit_static.py`·`build_sim_static.py` · `session_0904/reports/step13_builder_report.md`·`step13_qa_report.md` · 전후 비교 https://claude.ai/code/artifact/2783782a-a759-4e3b-b022-60173f4db89b |
| 시연본 범위 | 사이드바 7메뉴 · 화면 9 · 상태 17. 시뮬레이션·엑셀 미리보기·화면 갤러리는 통합본 전용 | `scripts/sync_prototype.py` `drop_sim()`·`drop_xls_preview()` · `gate_prototype.js` |
| 투자자 공유 정리 (2026-09-09, 시연본 → 통합본) | 탭 제목 「PayHug 투자자 어드민」 · 투자 자산 카드 아래 비중·보관 줄 0 · 현황 표 비중·보관 열 0(열 5, 빈 행 colspan 5) · 「투자자산 현황」 엑셀 두 열 0(5658 B, 레지스터 size 5.5 KB). 가맹점별 표 「비중」 열은 그대로. 통합본 원본도 같은 정리(`7493d89`), 탭 제목만 시연본 변환 때 바꿈 | `build_app.py`·`sync_assets_static.py`·`build_sim_static.py`·`build_xlsx.py` · `scripts/sync_prototype.py` `investor_share()`·`patch_assets_status_xlsx()` · `gate_prototype.js` 「투자자 공유 정리」 7검사 · `prep_fig.py share` · 시연본 `7a369bd` |
| Figma 3066:328 | 직계 **37프레임** = 화면 24 + 상태 13. 원천 커밋 `d7ce377`(투자 자산 9 는 이 판 + `prep_fig.py share` 투자자 공유 정리 = 시연본 모습 · 투자 수익 9 는 이 판 · 나머지 19 는 `e019d5a` 판이나 화면 내용 같음). 툴팁 열린 상태 프레임 8장은 패널을 최상위 마지막 자식 + ABSOLUTE 로 올린 후처리가 있음. 37프레임 텍스트 전수에서 검토 표시·수익 산정 기준·투자 시뮬레이션·기준일·W금융일수 0건. 쿠콘·시뮬 2·엑셀 서식 4·로그인 은 만들지 않는다 | `figma_map_investor.json` `frames` 37 · `source_commit` · `verification` · `session_0904/reports/step10_figma_report.md`·`step11_figma_report.md` · 캡처 `session_0904/qa/figma_0907/`·`figma_0907b/` |
| 로그인 | 기존 어드민 프론트 `app/login/page.tsx` 그대로 | `reports/step7_login_report.md` |

## 산출물 위치

| 무엇 | 경로 |
|---|---|
| **최종본 묶음 (V1.3 · 2026-09-09)** | `~/Downloads/payhug_용어정의서/최종/` — `목록_V1.3_20260909.md` · `01_기호정리표` · `02_시연본_V1.3_20260909_7ba7f26` · `03_통합본_V1.3_20260909_d9af5a7` · `04_엑셀_V1.3_20260909` · `05_증명서_V1.3_20260909` · `06_Figma_V1.3_20260909` · `07_검증보고_20260909`. 다음 판은 새 폴더(`최종_V1.4_…`) |
| 기호 정리표 **「투자자어드민 기호정리표_V1.3」** (확정) | `~/Downloads/payhug_용어정의서/투자자어드민 기호정리표_V1.3.docx` · `.html` (레포 사본 `session_0904/artifact/`, 대표님 수정안 사본 `…_V1.2_대표님수정안.docx`). V1.0 은 `1차 최종/`, V1.1·V1.2 는 폐기된 중간판. 다음 판은 V1.4·V2.0 |
| 전후 비교 (화면 툴팁 8곳 · Figma 8프레임) | https://claude.ai/code/artifact/2783782a-a759-4e3b-b022-60173f4db89b · `~/Downloads/payhug_용어정의서/V1.3_반영_전후비교_20260908.html` · 표 4 AS-IS/TO-BE https://claude.ai/code/artifact/95990a7c-d41d-411d-90bb-78ee155f790a |
| 아티팩트 원본 (워드·HTML 생성기 입력) | 스크래치패드 `ceo_review.html` → 레포 사본 `session_0904/artifact/ceo_review.html` · 게시 https://claude.ai/code/artifact/f0f651d2-7579-4cee-bf7e-0d7a582d48fd (「V1.1 d 표기」 판) |
| 대표 수정 검토 아티팩트 | `session_0904/artifact/ceo_edit_review.html` · https://claude.ai/code/artifact/4e9ff1f7-3b60-48d1-9911-3cb06eaeac94 |
| 원고 | `final_terms.json`(V1.3 표 1~4 글자 그대로) · 검사기 `verify_final_terms.py` **302건 전건 통과** (T 절 = V1.3 워드·HTML 실물 대조 135, S 절 = 옛 표기 0, J 절 = 판별력 26) · `build_symreview.py` 원고 경로 `session_0904/artifact/ceo_review.html` |
| 원장 | `daily_ledger.py` (`ASOF` 어제 · `TY5_EXPR = 'ty4 * ad / tot'`) · `ledger_facts.json` |
| 배포 | 전체본 https://payhug-investor-demo.vercel.app/ (`Joo2n/payhug-investor-admin` main `2db5f01`) · 시연본 https://payhug-investor-prototype.vercel.app/ (`Joo2n/payhug-investor-prototype` main `7ba7f26(투자자 공유 정리 판, 원본 7493d89 재동기화)`) · 용어 해설 https://payhug-investor-glossary.vercel.app/ (`Joo2n/payhug-investor-glossary` main `3ddc511`). GitHub Actions 「배포 동기화 검사」는 **수동 실행 전용**(`workflow_dispatch`) — push 마다 돌면 로컬 동기화 전 8분 재시도 끝에 실패 메일이 나가서 뺐다. push 뒤 `sync_prototype.sh`·`sync_glossary.sh` 가 대상 레포·배포면을 스스로 확인한다 |
| 대표님 슬랙 초안 | `~/Downloads/payhug_용어정의서/대표님_슬랙_V1.3_20260908.txt` (대표님과는 이미 종결, 참고용) |
| 세션 보고서 | `session_0904/reports/` (step5~step13 · xcheck_A/B · xcheck_0908_A/B · orders_mid/final/0907/0907b/0908 · audit_0907_decisions) · 조사 `session_0904/survey/` · 검증 `session_0904/verify/` · 캡처 `session_0904/qa/` (figma_nav 24 · figma_states 13 · figma_0907 22 · figma_0907b 5 · figma_0908b 10 · screen_ab_0908) |
| 지라 PAYHUG-229 9/4 기록 (붙여넣기용) | `~/Downloads/payhug_용어정의서/PAYHUG-229_진행상황_20260904.html` · 사본 `session_0904/reports/` |

## 남은 작업 (2026-09-09 시점)

| # | 할 일 | 어디 | 상태 |
|---|---|---|---|
| A | 기호정리표 V1.3 표 4 「툴팁」 열 후속 갱신 — 화면 툴팁이 「기호 = 산식」 규칙으로 바뀌어 표 4 툴팁 문장(「보유 채권 전체」「연환산 · …」「선정산일이 …」)은 이제 둘째 줄 이하의 행 문구. 규칙 한 줄을 표 4 위에 적고 열을 「둘째 줄 이하」로 재정의할지 사용자 결정 | `ceo_review.html` 표 4 → `build_symreview.py` → V1.4 | 결정 필요 |
| B | 가맹점별 엑셀을 내려받은 뒤 「증명서 다운로드」 모달에서 취소·발급을 누르면 엑셀이 한 번 더 내려옴 (전체본·시연본, 재현 2/2) | `app.html:3438` cert-open → `2139` `toastServed = null` → `2133-2137` `syncToast` 가 `pullFile` 재호출. 2139 초기화를 화면 전환 때만 하거나 재전달을 딥링크 진입으로 한정 | 고칠 것 (기존 결함) |
| C | 투자실행액·순현금 카드 툴팁 — 제안서의 두 줄(`i | 정산예정일이 d 보다 뒤인 채권 · 2,240건`, `EC_d = 20,000,000원`)은 사용자가 요청한 적 없는 내 제안이라 취소(9/9 사용자 확인). 확정 문서 표 4 에는 두 카드 툴팁이 없고 「d 는 표시하지 않음」. 지금 화면은 투자실행액 카드 툴팁 `Σ A_i / A_i \| 순지급액_i × (1 − r) / r \| 0.11%` 가 남아 있고 순현금은 없음 | `build_app.py:1745` · `sync_assets_static.py` | 사용자 결정 대기: 확정 문서대로 투자실행액 툴팁을 없앨지 / 그대로 둘지 (9/9 「툴팁은 지시 없어 그대로」) |
| D | ⑤·입금부족률 툴팁 첫 줄이 256px 안에서 「순현금 / 비중」「3,200 / 건」 으로 단어 중간 줄바꿈 | `app.html` ⑤ 첫 줄 `<br>` 을 「+」 앞으로, 건수에 `&nbsp;` | 개선 여지 |
| D2 | 빈 상태 낱장 `invest-profit--empty.html` ④⑤ 툴팁 0 값 자리수를 `0%`→`0.000000%`·`0일`→`0.00일` 로 통합본과 맞춤(빌더 판단, 지시 밖) · 전후 비교의 Figma 01-h·01-g·03-f 3장은 교체 전 캡처 없음 | `sync_profit_static.py:230·351` | 고지용 |
| E | 낱장 7종 favicon 404 · 증명서 미리보기 제목 「투자자산 현황」 ≠ PDF 「투자자산 증명서」 · 주별·월별 열머리 툴팁 「그 날짜인」(행 단위가 주·월) | `certificate.html:164` · `app.html:1777·1785` | 낮음 |
| F | 통합본 전용 문서 페이지 8종·용어 해설 단독 배포(공개 URL)의 옛 체계·검토 표시 잔존, `build_glossary.py` 앵커 8+2 소실 | `glossary_manuscript.md` 등 원고 → 생성기 | 결정 필요 (내릴지 / 재작성) |
| G | `verify_crossscreen.py` FAIL 3(glossary duration 블록) · `verify_shotmarks.py` FAIL 45 · `verify_docnums.py` 24 — 전부 문서 페이지 대상 기존 FAIL | | F 와 함께 |
| H | `build_archive.py --check` 설명 공란 6건(.bak 4 · NEXT_SESSION.md · freeze_app.js) · `archive.html` 재생성 | | 정리 |
| I | 순현금 시점(대표 원문 12행 「조회시점 현재」 vs V1.3 EC_d 「d 일 마감시점」) · 증명서 「작성일자 2026-08-27」 의미 · 시드·원고 11개 ⑤ 동기화 · `build_final.py` 옛 기간 | | 기존 항목 |
| J | 표 2 Σ A_i 「정산예정일이 d 보다 뒤인 채권」 vs 투자자산 「기준일(d) 보다 뒤인 보유 채권」 두 문장 · 산문의 EC(첨자 없음) vs 기호 EC_d | V1.3 본문 | 확인 필요 (원고 조 지적) |
| K | 통합본 날짜 입력 역전 시 카드가 0원/0.00% 로 감(실물은 직전 결과 유지) · 키보드 입력 시 빈 값 · `min/max` 없음 · 파일바 「생성일시」 빌드 시각 노출 | `app.html` `change`→`refresh()` · `:686·691` · `:1709~` | 낮음 |
| L | 기간 이동 잔재 FAIL(`verify_period.js`·`verify_docnums.py`·`verify_links.py`) · 시뮬 종료일 ASOF ↔ 낱장 WEEK(`sim_facts.py:52`) · 순현금 EC 상수(2천만) 대 날짜별 합(`daily_ledger.py:62`) | | 기존 항목 |
| M | 「d」 관련 옛 명세 `session_0904/V11_SPEC.md`·`verify/xv_d_*.md`·`xv_v11_*.md` 는 V1.1 이력이라 V1.3 과 다름 — 읽을 때 주의 | | 참고 |
| N | 통합본 투자자 공유 정리 — 적용 완료(`7493d89`). 남은 것: 용어 해설 원고 `glossary_manuscript.md:1092·1096·1129·1434·1501` 의 「보관 ㈜쿠콘」·`anchor: th:보관`(캡처 재촬영 전 정리 필요, F 와 함께) · 문서 페이지·`assets/shots` 캡처는 정리 전 화면 | `glossary_manuscript.md` · `capture_shots.js` | F·G 와 함께 |
| O | 사용자가 후보로 본 나머지 — 투자자명 「㈜테스트인베스트」(사이드바·증명서·엑셀 제목, 바꿀 이름 필요) · 전체본 첫 화면 「화면 설계(안)」 문구 · 시뮬레이션 표 열머리 내부 용어(순지급액·채권매입수수료·미지급 차감) | `app.html:1155·527·581·598` · `:944` · `:2737` | 사용자 결정 |
| P | `gate_prototype.js` 배포 URL 게이트가 페이지 로드 전에 `go()` 를 부르면 `go is not defined` 로 중단(9/9 1회, 재실행 통과). `ev` 앞에 `SCREEN_ORDER`·`go` 정의 대기(폴링)를 넣을 것 | `gate_prototype.js:215` | 낮음 |
| Q | 전체본 배포의 용어 해설 `glossary.html`(「보관 ㈜」 5곳)·`terms-edit.html`(1곳)·`assets/shots/invest-assets.webp` 캡처는 정리 전 화면. 첫 화면 doc-card 로 닿음. F·G(문서 페이지 8종) 와 함께 원고 정리 → 재촬영 | `glossary_manuscript.md:1092·1096·1129·1434·1501` · `capture_shots.js` | F·G 와 함께 |
| R | **기호정리표 V1.3 원고 예시값 갱신(V1.4)** — 본문 plain 의 PMR 0.033992% · 3.992511% · 3.99% · ⑤ 3.19% · PM 61,175 등이 입금부족액 0 판과 다름. `verify_final_terms.py` 원고 대조 14 FAIL. 대표님과 종결된 정의는 그대로이고 예시 숫자만 | `session_0904/artifact/ceo_review.html` · `final_terms.json` · `build_symreview.py` | 사용자 결정 |
| S | 일별 표에 「채권매입수수료」「입금부족액」 열(또는 툴팁)과 입금 대사 전 날짜 「집계 중」 표시 — 9/9 사용자 질문(입금부족액이 날짜별로 갱신되는가)에 대한 답. 대표 스토리보드 밖 열이라 대표님 확인 필요 | `build_app.py` 일별 표 · `daily_ledger.py` | 사용자 결정 |
| T | (해당 없음) 「CLAUDE.md 의 S입금부족율 0.07% 문장」은 빌더 보고의 오류 — 두 CLAUDE.md 에 그런 문장 없음(지시 추적 0909c 확인) | | — |

## 재개 명령

```bash
cd /Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin
python3 daily_ledger.py            # 원장 → ledger_facts.json
python3 build_xlsx.py              # 엑셀 — build_app 보다 먼저(등록부가 파일 크기·생성일시를 읽음)
python3 build_app.py               # 통합본 app.html
python3 sync_assets_static.py && python3 sync_profit_static.py && python3 build_sim_static.py
python3 build_audit_xlsx.py && python3 build_docs.py
python3 prep_fig.py sync && python3 prep_fig.py freeze   # Figma 용 사본 (화면 24 + 상태 13)
python3 verify_final_terms.py      # 원고 검사기 151건
node capture_shots.js && python3 build_glossary.py && python3 verify_shotmarks.py && node verify_shots.js   # 화면이 바뀌면 용어 해설 캡처 재촬영
bash sync_prototype.sh --dry-run   # 시연본 변환·게이트 (push 없이)
bash sync_prototype.sh             # 시연본 push (Joo2n/payhug-investor-prototype)
bash sync_glossary.sh              # 용어 해설 push (Joo2n/payhug-investor-glossary)
```

기호 정리표 워드·HTML: `python3 build_symreview.py` (원고 경로는 10번 참고).
Figma 재임포트: `bash run_import_0828.sh preflight` → `serve` → `generate_figma_design` 청크 3 → 검수 → 구 노드 삭제 (`session_0904/reports/step10_figma_report.md`).

**순서 주의**: `build_xlsx.py` 를 `build_app.py` 보다 먼저 돌린다. `build_app.py` 가 엑셀 파일의 크기·생성일시를 읽어 `app.html` 등록부에 박는다.

## 손대지 않는 것

- 사이드바 메뉴 **라벨** · 대표 원문 인용 · `ceo_definitions.md`(sha256 잠금)
- `payhug-admin-web`·`payhug-merchant-web` 읽기만 · `/Users/semi/Desktop/01_PayHug/` 읽기만
- `payhug-io` 조직 저장소 push 금지 (세 저장소 모두 `Joo2n`)
- MAU 참고값(카드 65%·2.7504일·14.60%) 지우지도 계산에 쓰지도 않음
- 미확정 3대(C1 수수료율·C2 지급 캘린더·C4 예상 지급 차액) 확정으로 올리지 않음 · 6대 개념 합치지 않음
- `roster16_apply.py` 실행 금지 (두 번 돌리면 엑셀 행 겹침)
- 확정본 V1.x 가 기준. 대표 원문·대표 워드로 확정본을 뒤집지 않는다 (채택/비채택만 판정)
