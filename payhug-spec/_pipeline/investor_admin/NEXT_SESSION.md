# 투자자 어드민 — 다음 세션 시작점

마지막 세션 2026-09-07. 이 파일과 `session_0904/` 만 읽으면 이어서 할 수 있다. 사용자 지시 목록은 `session_0904/ORDERS_0904.md`, 이행 판정은 `session_0904/reports/orders_mid.md`·`orders_final.md`·`orders_0907.md`. V1.1 명세는 `session_0904/V11_SPEC.md`.

## 지금 상태 한 줄

기호 정리표 **V1.1**(d = 오늘, 산식 조건은 d 표기)이 워드·HTML·아티팩트로 나와 있고, 화면(전체본·시연본)·Figma 37프레임·용어 해설 미러가 같은 판으로 배포돼 있다. 투자자 화면에는 내부 검토 표시(「미확정」 배지·「대표 확인 대기」·「대표 DM」·「항등식」 등)가 0건이고 「수익 산정 기준」 구역(수수료 배분형·조달이자형)은 대표 스토리보드에 없는 것이라 없다. 대표님 승인이 남은 자리는 ⑤ 산식 하나이며 승인 상태는 화면이 아니라 이 문서에서만 추적한다.

## 확정된 것

| 항목 | 값 | 근거 |
|---|---|---|
| `d` | 오늘(화면을 보는 날). 첨자 아님. 산식에는 조건 문장으로만: 「선정산일이 d 전날 이전이고 정산예정일이 d 이후」「d 전날 마감 잔액」「P 는 d 전날까지」「선정산일이 d 의 20일 전부터 11일 전까지」. 투자자 화면에 표시하지 않음 | `session_0904/V11_SPEC.md` · `final_terms.json` vars.d · 점검 `session_0904/verify/xv_d_A.md`·`xv_d_B.md`·`xv_v11_A.md`·`xv_v11_B.md` |
| 원장 시점 | `ASOF` 08-27 = **어제(마감 스냅샷 날)**. 오늘은 08-28 이고 화면에 없다. `LAST_DUE = ASOF`, 일별 표에 08-27 행, 기본 조회기간 **08-21~08-27**, 입금부족률 표본 08-08~08-17 | `daily_ledger.py:62-71` · `ledger_facts.json` |
| ⑤ 투자 자산 대비 연환산 수익률 | `PY_t = PY_a × 채권 비중 + 0 × 순현금 비중 = PM × 365 ÷ ( Σ( A_i × D_i ) + PEC )`, i 는 정산예정일이 P 안인 채권. 채권 비중 = Σ(A_i×D_i) ÷ (Σ(A_i×D_i)+PEC). 기호표 ⑤ 칸에 전개 전문(순현금 수익률 0 항·PMR·PD 대입·약분) | 교차검증 `session_0904/verify/xv_*.md` · 잔액 하루씩 7일 합 564,855,018 ≈ Σ(A_i×D_i) 559,275,516 (경계 채권 1%) |
| 기본 조회기간 값 | 투자실행금 179,970,919 · 투자수익 61,175 · PD 3.11 · ④ **3.99%** · Σ(A_i×D_i) 559,275,516 · PEC 140,000,000 · ⑤ **3.19%** | `ledger_facts.json` `weekExec`·`weekProfit`·`weekTy`·`weekAD`·`weekPsc`·`weekTyAsset` |
| 표기 규칙 셋 | 정의 줄은 `이름 = Σ 낱건, 범위` · 조립 산식은 이름으로만 · 한 산식 안에서 풀기/접기 혼용 금지 | `session_0904/reports/step7_notation_report.md` |
| 낱말 | 「비중」으로 통일(가중치 낱말 안 씀). 띄어쓰기 「보유 채권」「연환산 수익률」「예상 연환산 수익률」「투자 자산 대비」, 「투자실행금액 대비」는 붙임 | 기호표 표 4 · `verify_final_terms.py` S6·S7 |
| 내부 용어 ↔ 투자자 화면 (표 4) | 대상정산금채권 → 보유 채권 · ty수익률 → 연환산 수익률(툴팁 「일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률」) · 오늘(d) → 표시하지 않음 · 조회기간(P) → 검색대상기간 | 대표님 DM 9/7 합의 · `final_terms.json` `screen_terms` |
| 대표님 워드 변경 판정 | 채택: 보유 채권 · 연환산 수익률 툴팁 · 내부/화면 분리. 비채택: 첨자 d 규칙 · 상수 d 행 삭제 · `EC_d`·`Σ EC_d` · ⑤ `PM ÷ (PA + PEC)` 되돌림 | `/Users/semi/Downloads/투자자어드민 기호정리표_V1.0.docx`(변경 추적본) · 메모리 `feedback_confirmed_doc_is_baseline.md` |
| 화면 라벨·툴팁 | 투자 자산: 「기준일」 알약 없음 · 열머리 가중평균 금융일수(툴팁 「보유 채권 전체 (회수된 것 포함)」)·입금부족률(툴팁 「선정산일이 오늘 기준 20일 전 ~ 11일 전」)·예상 연환산 수익률(툴팁 Y_r 머리 + 「연환산」 행, 카드·현황표·가맹점별). 투자 수익: ④ 투자실행금액 대비 · ⑤ 투자 자산 대비, 툴팁 기호마다 용어명·값·「연환산」 행. **검토 표시 0건**(「미확정」「대표 확인 대기」「대표 재전달」「대표 DM」「(관찰된 값)」「항등식」「부족액 0」「일 환산」) · 「수익 산정 기준」 구역 없음(`build_app.py` `SHOW_FORMULA = False`, 낱장은 `sync_*_static.py` `drop_formula()`) | `build_app.py` `YR_TIP_HEAD`·`YR_TIP_ROW`·`yrTh()`·`tyTh`·`thirdTh` · `sync_assets_static.py`·`sync_profit_static.py` · 빌더 `session_0904/reports/step11_builder_report.md` · QA `step10_qa_report.md`·`step11_qa_report.md` · 메모리 `feedback_no_internal_marks_in_investor_ui.md` |
| 시연본 범위 | 사이드바 7메뉴 · 화면 9 · 상태 17. 시뮬레이션·엑셀 미리보기·화면 갤러리는 통합본 전용 | `scripts/sync_prototype.py` `drop_sim()`·`drop_xls_preview()` · `gate_prototype.js` |
| Figma 3066:328 | 직계 **37프레임** = 화면 24 + 상태 13. 원천 커밋 `9972f0b`(투자 자산 9·투자 수익 9 는 이 판, 나머지 19 는 `e019d5a` 판이나 화면 내용 같음). 37프레임 텍스트 전수에서 검토 표시·수익 산정 기준·투자 시뮬레이션·기준일·W금융일수 0건. 쿠콘·시뮬 2·엑셀 서식 4·로그인 은 만들지 않는다 | `figma_map_investor.json` `frames` 37 · `source_commit` · `verification` · `session_0904/reports/step10_figma_report.md`·`step11_figma_report.md` · 캡처 `session_0904/qa/figma_0907/`·`figma_0907b/` |
| 로그인 | 기존 어드민 프론트 `app/login/page.tsx` 그대로 | `reports/step7_login_report.md` |

## 산출물 위치

| 무엇 | 경로 |
|---|---|
| 기호 정리표 **「투자자어드민 기호정리표_V1.1」** | `~/Downloads/payhug_용어정의서/투자자어드민 기호정리표_V1.1.docx` · `.html` (레포 사본 `session_0904/artifact/`). V1.0 은 `~/Downloads/payhug_용어정의서/1차 최종/`. 다음 판은 V1.2·V2.0 |
| 아티팩트 원본 (워드·HTML 생성기 입력) | 스크래치패드 `ceo_review.html` → 레포 사본 `session_0904/artifact/ceo_review.html` · 게시 https://claude.ai/code/artifact/f0f651d2-7579-4cee-bf7e-0d7a582d48fd (「V1.1 d 표기」 판) |
| 대표 수정 검토 아티팩트 | `session_0904/artifact/ceo_edit_review.html` · https://claude.ai/code/artifact/4e9ff1f7-3b60-48d1-9911-3cb06eaeac94 |
| 원고 | `final_terms.json` · 검사기 `verify_final_terms.py` **151건 전건 통과** (S 절 = V1.1 조건·띄어쓰기·옛 표기 0, J 절 = 판별력 시험) |
| 원장 | `daily_ledger.py` (`ASOF` 어제 · `TY5_EXPR = 'ty4 * ad / tot'`) · `ledger_facts.json` |
| 배포 | 전체본 https://payhug-investor-demo.vercel.app/ (`Joo2n/payhug-investor-admin` main `9972f0b`) · 시연본 https://payhug-investor-prototype.vercel.app/ (`Joo2n/payhug-investor-prototype` main `4535135`) · 용어 해설 https://payhug-investor-glossary.vercel.app/ (`Joo2n/payhug-investor-glossary` main `da8703d`). GitHub Actions 「배포 동기화 검사」는 **수동 실행 전용**(`workflow_dispatch`) — push 마다 돌면 로컬 동기화 전 8분 재시도 끝에 실패 메일이 나가서 뺐다. push 뒤 `sync_prototype.sh`·`sync_glossary.sh` 가 대상 레포·배포면을 스스로 확인한다 |
| 대표님 슬랙 초안 (V1.1 기호만) | `~/Downloads/payhug_용어정의서/대표님_슬랙_V1.1_20260907.txt` |
| 세션 보고서 | `session_0904/reports/` (step5~step11 · xcheck_A/B · orders_mid/final/0907/0907b) · 조사 `session_0904/survey/` · 검증 `session_0904/verify/` · 캡처 `session_0904/qa/` (figma_nav 24 · figma_states 13 · figma_0907 22 · figma_0907b 5) |
| 지라 PAYHUG-229 9/4 기록 (붙여넣기용) | `~/Downloads/payhug_용어정의서/PAYHUG-229_진행상황_20260904.html` · 사본 `session_0904/reports/` |

## 남은 작업 (우선순위)

| # | 할 일 | 어디 | 비고 |
|---|---|---|---|
| 1 | **⑤ 대표님 승인** — 화면에는 배지가 없으므로 승인 여부는 여기서만 추적. 승인이 다르게 나면 `daily_ledger.py` `TY5_EXPR` 과 기호표 ⑤ 칸을 함께 고친다 | 슬랙 초안 `~/Downloads/payhug_용어정의서/대표님_슬랙_V1.1_20260907.txt` | |
| 2 | 대표님께 보낼 것 — V1.1 워드 · ⑤ 산식(PD 가 Σ D_i 가 아닌 이유는 `PA × PD = Σ( A_i × D_i )` 항등식으로) · 7번(Σ A_i 누계)·10번(D 표본) | `session_0904/artifact/ceo_edit_review.html` · 슬랙 초안은 V1.1 기호(PA·PD·PEC·PY_a·PY_t)로만 | 값은 `survey/step0_ty5_impact.md` |
| 3 | 통합본 전용 문서 페이지 8종에 남은 검토 표시·「조달이자형」 — capability 46 · inquiry 14 · glossary 113 · steps-all 101 · terms-edit 51 · feasibility 14 · ceo-questions 8 · archive 3 (건수는 `step11_builder_report.md` §6 · `orders_0907b.md`). 시연본에는 없음. **용어 해설 단독 배포 https://payhug-investor-glossary.vercel.app/ 는 glossary 와 같은 내용이 공개 상태**이고 통합본 `index.html` 이 8종에 링크한다 — 원고 재작성 전까지 내릴지(Vercel 프로젝트 일시정지) 사용자 결정 | 각 원고(`capability_manuscript.md`·`ceo_inquiry.md`·`glossary_manuscript.md`·`steps_all.json`·`termsdoc_seed.json`) → 생성기 | 7·8번과 함께 |
| 4 | 증명서 화면 — 「작성일자 2026-08-27」이 마감일(어제)과 같음. 발급 버튼을 오늘 누른 문서의 작성일자가 어제인 셈. 미리보기에 「마감 기준」이 없고 PDF 머리에만 있음 | `certificate.html:153·258` · `app.html` 증명서 · `build_docs.py:179` | 「작성일자」를 「기준(마감)」으로 바꿀지, 값을 오늘로 할지 결정 필요. QA `step10_qa_report.md` (마) ①② |
| 5 | 순현금 시점 — 대표 원문 12행 「조회시점 현재」 vs 45행 「전일자 마감」. V1.1 은 어제 마감 | `ceo_definitions.md` 읽기만 | 대표 확인 |
| 6 | 용어 해설 `glossary.html` — `build_glossary.py` 가 원고 앵커에서 멎음(31개 중 안 잡히는 것 8 + 「수익 산정 기준」 제거로 사라진 `invest-assets / div:0.11%`·`h2:수익 산정 기준` 2). 9/7 띄어쓰기 3건 미반영. `verify_shotmarks.py` FAIL 45 · `verify_crossscreen.py` 불일치 3 · `verify_docnums.py` 24 는 전부 이 문서 페이지 대상 | `glossary_manuscript.md` 앵커 재지정 → `build_glossary.py` → `verify_shotmarks.py` → `sync_glossary.sh` | 3·7번과 함께 |
| 7 | 문서 화면 5종 재작성 (옛 체계 `wD`·`PwD`·`PY_MR`·하루 갈래) | `glossary.html`·`steps-all.html`·`calc.html`·`terms-edit.html`·`final-terms.html` ← `build_calc.py`·`steps_all.json`·`glossary_manuscript.md`·`termsdoc_seed.json` | 잔존 `survey/step4_ui_terms.md` §4 |
| 8 | 시드·원고 11개에 ⑤ 산식 동기화 | `termsdoc_seed.json` · `dm_0901/symbol_rule_0901.md` · `meeting_0901/testcase.json` · `meeting_0901/steps_all.json` · `symbol_glossary.json` · `glossary_manuscript.md` · `ceo_inquiry.md` · `feasibility.md` · `capability_manuscript.md` · `ceoq_seed.json` | 자리 목록 `survey/step0_ty5_impact.md` (가) |
| 9 | 용어기호정리 워드·HTML 재생성 (`final_terms.json` 을 읽는 다른 문서, 09-02 판에 멈춤) | `build_final.py` — `meeting_0901/testcase.json` 옛 기간 고정 | 8번과 함께 |
| 10 | `build_symreview.py` 가 읽는 원고 경로를 스크래치패드에서 `session_0904/artifact/ceo_review.html` 로 | `build_symreview.py:29–31` | 스크래치패드는 세션이 끝나면 사라진다 |
| 11 | `build_archive.py --check` 실패 — 설명 공란 6건 (`NEXT_SESSION.md` · `freeze_app.js` · `figma_map_investor.json.bak_0904`·`.bak_0904b` · `gate_prototype.js.bak_0904` · `prep_fig.py.bak_0904`). `.bak` 4건은 지우고 둘은 설명을 넣어 `archive.html` 재생성 | `build_archive.py` | 전 파일 행이 바뀌므로 따로 |
| 12 | 검사기 FAIL 정리 — 기간 이동 잔재(`verify_period.js`·`verify_docnums.py`·`verify_links.py`) · 시뮬 종료일 ASOF ↔ 정적 낱장 WEEK (`sim_facts.py:52`) | `session_0904/reports/step7_verifier_report.md` (다) | |
| 13 | 순현금 EC 상수(2천만) 대 날짜별 합 | `daily_ledger.py:62 CASH` | 날짜별 역산 표 `survey/step0_ty5_impact.md` |
| 14 | 통합본 `app.html` 날짜 입력 역전 시 카드가 0원/0.00% 로 감(실물은 직전 결과 유지) · `min/max` 속성 없음 · 파일바 「생성일시」에 빌드 시각 노출 | `app.html:3851-3862` · `:686·691` · `:1709~` | QA `step10_qa_report.md` (마) ④⑤⑥ |
| 15 | 툴팁 ④ 「항등식」「부족액 0」 라벨 꺾임 · 「대표 DM 16:45」 행 요약이 「관찰된 값 · PMR 계통」으로 바뀐 것 되돌릴지 | `build_app.py` ④ 툴팁 · `sync_profit_static.py` `TIP4` · `assets/base.css` `.tip-row` | `session_0904/reports/xcheck_A.md` 4번 |

## 다음 라운드 (컴팩트 뒤 이어서) — 사용자 확인 필요 항목부터

| # | 할 일 | 어디 | 상태 |
|---|---|---|---|
| A | 기호표 V1.1 에 **내부/외부 용어 규칙 행 + 병기** — 표 1 에 「내부 용어 · 이 표는 내부 용어(대상정산금채권·ty수익률)로 쓴다. 투자자 화면 용어는 표 4」 행, 표 2 첨자 i·Σ A_i + EC·D 세 자리에 「대상정산금채권(보유 채권)」 병기. 문구 확인 후 `ceo_review.html` → `build_symreview.py` → 워드·HTML·아티팩트 재발행, `verify_final_terms.py` 기대값 갱신 | 스크래치패드 `ceo_review.html`(사본 `session_0904/artifact/`) | 문구 확인 대기 |
| B | 표 4 툴팁 열 ↔ 화면 툴팁 정합 — 「계약된 할인율 기준 예상치」는 화면에 없음, 「보유 채권 전체 (회수된 것 포함)」의 「회수된 것 포함」은 어시스턴트 문구. 어느 쪽으로 맞출지 | 표 4 · `build_app.py` `POP_W`·`YR_TIP_HEAD` | 확인 필요 |
| C | 투자 수익 일별 표 「투자실행금」 열머리 툴팁에 회의 메모(「칸 미지목」·「⑥ 의 ③」 번호 체계) 노출 — QA 최상위 결함. 번호 체계를 V1.1 기호(P=1일의 PA·PM·PD·PY_a)로 바꾸거나 툴팁을 뺀다 → 재생성·배포·Figma 03-h(`3720:2`) 교체 | `build_app.py` `thirdTh`·`tyTh` · `sync_profit_static.py` `THIRD_TH`·`TY_TH` · `step11_qa_report.md` 결함 1 | 결정 필요 |
| D | 시연본·통합본 h1 옆 상태 배지 15종(「주별」「검색 적용」「규칙 미충족」 등) — 실제 프론트에 없음. 뺄지 | `build_app.py` state-badge · `step11_qa_report.md` 결함 5 | 결정 필요 |
| E | 날짜 칸 키보드 입력이 `""` 로 떨어져 180일 전체 조회됨(실제 프론트는 입력값 유지) · 숫자 부분 클릭 시 달력 | `app.html` `change`→`refresh()` · `step11_qa_report.md` 결함 2·3 | 고칠 것 |
| F | 증명서 제목 3종 불일치(h1·문서·PDF)와 PDF 에만 「견본 · 계약 효력 없음」 띠 | `certificate.html:155,164` · `build_docs.py:169-171` | 확인 필요 |
| G | 사용자 결정 15개 대 V1.1·화면 감사 결과 반영 | `scratchpad/audit_0907_decisions.md`(감사 조 진행 중이었음. 없으면 다시 돌린다) | 대기 |
| H | 문서 페이지 8종·용어 해설 단독 배포 잔존(위 3·6번) | | 결정 필요 |
| I | 표 1 「관찰된 값」 낱말 유지 여부 | 표 1 첨자 a·t | 확인 필요 |
| J | **EC 정의에서 날짜 제거** — 표 2 EC 「d 전날 마감시점 …」 → 「그날 마감시점 쿠콘 가상계좌의 현금 잔액」(날짜는 쓰는 자리의 조건이 정함), 투자자산 `Σ A_i + EC` 행에 「EC 는 d 전날의 값」, PEC 「P 안 각 날의 EC 를 더한 값」 그대로. 사용자 지적(9/7): EC 에 d 전날을 박으면 일별 행·PEC 의 「그날 EC」가 성립하지 않음. A 와 함께 워드·HTML·아티팩트 재발행, `verify_final_terms.py` S5 의 EC plain 기대값 갱신, 슬랙 초안 EC 문장 한 줄 수정 | `ceo_review.html` EC 행·투자자산 행 · `final_terms.json` vars.EC · `verify_final_terms.py:1032` | 진행 확인 대기 |

## 재개 명령

```bash
cd /Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin
python3 daily_ledger.py            # 원장 → ledger_facts.json
python3 build_app.py               # 통합본 app.html
python3 sync_assets_static.py && python3 sync_profit_static.py && python3 build_sim_static.py
python3 build_xlsx.py && python3 build_audit_xlsx.py && python3 build_docs.py
python3 prep_fig.py sync && python3 prep_fig.py freeze   # Figma 용 사본 (화면 24 + 상태 13)
python3 verify_final_terms.py      # 원고 검사기 151건
node capture_shots.js && python3 build_glossary.py && python3 verify_shotmarks.py && node verify_shots.js   # 화면이 바뀌면 용어 해설 캡처 재촬영
bash sync_prototype.sh --dry-run   # 시연본 변환·게이트 (push 없이)
bash sync_prototype.sh             # 시연본 push (Joo2n/payhug-investor-prototype)
bash sync_glossary.sh              # 용어 해설 push (Joo2n/payhug-investor-glossary)
```

기호 정리표 워드·HTML: `python3 build_symreview.py` (원고 경로는 10번 참고).
Figma 재임포트: `bash run_import_0828.sh preflight` → `serve` → `generate_figma_design` 청크 3 → 검수 → 구 노드 삭제 (`session_0904/reports/step10_figma_report.md`).

## 손대지 않는 것

- 사이드바 메뉴 **라벨** · 대표 원문 인용 · `ceo_definitions.md`(sha256 잠금)
- `payhug-admin-web`·`payhug-merchant-web` 읽기만 · `/Users/semi/Desktop/01_PayHug/` 읽기만
- `payhug-io` 조직 저장소 push 금지 (세 저장소 모두 `Joo2n`)
- MAU 참고값(카드 65%·2.7504일·14.60%) 지우지도 계산에 쓰지도 않음
- 미확정 3대(C1 수수료율·C2 지급 캘린더·C4 예상 지급 차액) 확정으로 올리지 않음 · 6대 개념 합치지 않음
- `roster16_apply.py` 실행 금지 (두 번 돌리면 엑셀 행 겹침)
- 확정본 V1.x 가 기준. 대표 원문·대표 워드로 확정본을 뒤집지 않는다 (채택/비채택만 판정)
