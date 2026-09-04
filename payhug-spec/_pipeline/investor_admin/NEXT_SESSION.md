# 투자자 어드민 — 다음 세션 시작점

마지막 세션 2026-09-04. 이 파일과 `session_0904/` 만 읽으면 이어서 할 수 있다. 사용자 지시 목록은 `session_0904/ORDERS_0904.md`, 이행 판정은 `session_0904/reports/orders_mid.md`·`orders_final.md`.

## 지금 상태 한 줄

기호 체계·⑤ 산식·화면 라벨·툴팁·Figma·시연본이 한 판으로 맞춰져 배포됐고, 기호 정리표 확정본(워드·HTML·아티팩트)이 기획팀 보고용으로 나와 있다. 대표님 승인이 남은 자리는 ⑤ 산식 하나다.

## 확정된 것

| 항목 | 값 | 근거 |
|---|---|---|
| ⑤ 투자자산 대비 연환산수익률 | `PY_t = PM × 365 ÷ ( Σ( A_i × D_i ) + PEC )`, i 는 정산예정일이 P 안인 대상정산금채권 | 교차검증 3건 `session_0904/verify/xv_*.md`. 대표 원문 54행의 `PSA` 를 `Σ( A_i × D_i )` 로 |
| 기본 조회기간 08-20~08-26 값 | Σ( A_i × D_i ) 556,626,436 · 비중 0.799031 · ⑤ 3.299662 → **3.30%** (옛 2.32%) | `ledger_facts.json` `weekAD`·`weekTyAssetRaw` |
| 표기 규칙 셋 | 정의 줄은 `이름 = Σ 낱건, 범위` · 조립 산식은 이름으로만 · 한 산식 안에서 풀기/접기 혼용 금지 | `session_0904/reports/step7_notation_report.md` |
| 화면 라벨 | 입금부족률 · 가중평균 금융일수 · 예상 연환산수익률(투자 자산) · 연환산수익률(투자 수익) | `reports/step5_builder_report.md` |
| 툴팁 | ④⑤ 툴팁의 기호마다 용어명·값. ⑤ 툴팁 「미확정 · 대표 확인 대기」 배지 유지 | `reports/step6_tooltip_report.md`·`step7_ty5_report.md` |
| 시연본 범위 | 사이드바 7메뉴 · 화면 9 · 상태 17. 시뮬레이션·엑셀 미리보기·화면 갤러리는 통합본 전용 | `scripts/sync_prototype.py` `drop_sim()`·`drop_xls_preview()` · `gate_prototype.js` |
| Figma 3066:328 | 직계 24프레임. 쿠콘·시뮬 2·엑셀 서식 4·로그인 은 만들지 않는다. **24프레임 사이드바에서 「투자 시뮬레이션」 항목 삭제** (스테이징은 `prep_fig.py` `patch_nav()`) | `figma_map_investor.json` `frames`·`retired`·`verification` · `prep_fig.py` IMPORT 24 · `session_0904/qa/figma_nav/` 24장 |
| 로그인 | 기존 어드민 프론트 `app/login/page.tsx` 그대로 | `reports/step7_login_report.md` |
| 대표님 수정 13곳 | 채택 11 · 유지 2 (7번 Σ A_i 「조회대상기간 누계」는 PA 의 뜻 · 10번 D 「표본」은 확인) | `survey/step1_apply_map.md` |

## 산출물 위치

| 무엇 | 경로 |
|---|---|
| 기호 정리표 확정본 **「투자자어드민 기호정리표_V1.0」** | `~/Downloads/payhug_용어정의서/1차 최종/투자자어드민 기호정리표_V1.0.docx` · `.html` (= 20260904_2155 판. 레포 사본 `session_0904/artifact/`. 다음 판은 V1.1·V2.0. 이전판은 `이전판/`) |
| 아티팩트 원본 (워드·HTML 생성기 입력) | `session_0904/artifact/ceo_review.html` · 게시 https://claude.ai/code/artifact/f0f651d2-7579-4cee-bf7e-0d7a582d48fd |
| 대표 수정 검토 아티팩트 | `session_0904/artifact/ceo_edit_review.html` · https://claude.ai/code/artifact/4e9ff1f7-3b60-48d1-9911-3cb06eaeac94 |
| 원고 | `final_terms.json` (⑤·PD·개념 6행 새 산식) · 검사기 `verify_final_terms.py` 137건 |
| 원장 | `daily_ledger.py` `TY5_EXPR = 'ty4 * ad / tot'` · `ledger_facts.json` |
| 배포 | 전체본 https://payhug-investor-demo.vercel.app/ (`Joo2n/payhug-investor-admin` main `b4f41b3`) · 시연본 https://payhug-investor-prototype.vercel.app/ (`Joo2n/payhug-investor-prototype` main `75bc47b`). 배포 실물 교차검증 `session_0904/reports/xcheck_A.md`·`xcheck_B.md` |
| 세션 보고서 | `session_0904/reports/` (빌더·검사기·QA·지시 이행·문서 검토) · 조사 `session_0904/survey/` · 검증 `session_0904/verify/` · 캡처 `session_0904/qa/` |

## 남은 작업 (우선순위)

| # | 할 일 | 어디 | 비고 |
|---|---|---|---|
| 1 | **대표님 승인 후** ⑤ 「미확정」 배지·「대표 확인 대기」 행 제거 | `daily_ledger.py` `TY5_STATUS`·`PEND5_ROW`(`build_app.py`) → 재생성 | 승인 전에는 손대지 않는다 |
| 2 | 대표님께 되물을 것 셋 — 7번(Σ A_i 누계)·10번(D 표본: 전체 13.21% / LR 표본 13.05% / P 안 12.98%)·⑤ 새 산식 | `session_0904/artifact/ceo_edit_review.html` | 값은 `survey/step0_ty5_impact.md` |
| 3 | 시드·원고 11개에 ⑤ 새 산식 동기화 | `termsdoc_seed.json` · `dm_0901/symbol_rule_0901.md` · `meeting_0901/testcase.json` · `meeting_0901/steps_all.json` · `symbol_glossary.json` · `glossary_manuscript.md` · `ceo_inquiry.md` · `feasibility.md` · `capability_manuscript.md` · `ceoq_seed.json` | 자리 목록 `survey/step0_ty5_impact.md` (가) |
| 4 | 문서 화면 5종 재작성 (옛 체계 `wD`·`PwD`·`PY_MR`·하루 갈래) | `glossary.html`·`steps-all.html`·`calc.html`·`terms-edit.html`·`final-terms.html` ← `build_calc.py`(코드에 옛 기호)·`steps_all.json`·`glossary_manuscript.md`·`termsdoc_seed.json` | 잔존 1,221건 `survey/step4_ui_terms.md` §4 |
| 5 | 용어기호정리 워드·HTML 재생성 (`final_terms.json` 을 읽는 다른 문서, 09-02 판에 멈춤) | `build_final.py` — `meeting_0901/testcase.json` 이 옛 기간(08-21~08-27) 고정이라 막힘. 3번과 함께 | |
| 6 | 검사기 FAIL 정리 — 기간 08-21→08-20 이동 잔재(`verify_period.js` 26 · `verify_docnums.py` 76 · `verify_links.py` `archive.html` 옛 xlsx 이름 12) · 시뮬 종료일 ASOF 08-27 ↔ 정적 낱장 WEEK 08-26 (`sim_facts.py:52`) | `session_0904/reports/step7_verifier_report.md` 분류 (다) | |
| 7 | `build_symreview.py` 가 읽는 원고 경로를 스크래치패드에서 `session_0904/artifact/ceo_review.html` 로 | `build_symreview.py:29–31` | 스크래치패드는 세션이 끝나면 사라진다 |
| 8 | 순현금 EC 상수(2천만) 대 날짜별 합 — 원문 45·55행은 날짜별 | `daily_ledger.py:62 CASH` | 날짜별 역산 표 `survey/step0_ty5_impact.md` |
| 9 | `archive.html` 재생성 (`login.html` 행 옛 크기·시각) | `build_archive.py` | 전 파일 행이 바뀌므로 따로 |
| 10 | 시뮬레이션 화면(통합본 전용)의 ⑤ 툴팁·값은 이미 새 산식. 시뮬 종료일 결정은 6번과 함께 | | |
| 11 | **Figma 상호작용 프레임 추가** — 메뉴·드롭다운·토글을 눌렀을 때 상태 (사용자 요청 2026-09-04). 후보·캡처 방법은 `session_0904/survey/step8_interaction_map.md` | `_fig/` 상태 주입 → `run_import_0828.sh` | 실물 프론트에 없는 상호작용은 만들지 않는다 |
| 12 | 통합본 `app.html` 의 `BASE_DATE`(08-26) 와 기준일(08-27) 갈림 — `#xls-profit-status` 직접 진입 시 기간 라벨·다운로드 잠김 | `build_app.py:1285·1940` | QA `session_0904/reports/` 참고. 통합본 전용 |
| 13 | 툴팁 ④ 「항등식」「부족액 0」 라벨이 낱자로 꺾임 (앞 라운드부터) | `assets/base.css` `.tip-row` 첫 span 규칙은 넣었음. 문안 길이 조정 | 가독 |

## 재개 명령

```bash
cd /Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin
python3 daily_ledger.py            # 원장 → ledger_facts.json
python3 build_app.py               # 통합본 app.html
python3 sync_assets_static.py && python3 sync_profit_static.py && python3 build_sim_static.py
python3 build_xlsx.py && python3 build_audit_xlsx.py && python3 build_docs.py
python3 prep_fig.py sync           # Figma 용 사본 (IMPORT 24)
python3 verify_final_terms.py      # 원고 검사기
bash sync_prototype.sh --dry-run   # 시연본 변환·게이트 (push 없이)
bash sync_prototype.sh             # 시연본 push (Joo2n/payhug-investor-prototype)
```

기호 정리표 워드·HTML: `python3 build_symreview.py` (원고 경로는 7번 참고).
Figma 재임포트: `bash run_import_0828.sh preflight` → `serve` → `generate_figma_design` 청크 3 → 검수 → 구 노드 삭제 (`figma_reimport2.md` §1·§2·§5, `session_0904/reports/step7_figma_report.md`).

## 손대지 않는 것

- 사이드바 메뉴 **라벨** · 대표 원문 인용 · `ceo_definitions.md`(sha256 잠금)
- `payhug-admin-web`·`payhug-merchant-web` 읽기만 · `/Users/semi/Desktop/01_PayHug/` 읽기만
- `payhug-io` 조직 저장소 push 금지 (세 저장소 모두 `Joo2n`)
- MAU 참고값(카드 65%·2.7504일·14.60%) 지우지도 계산에 쓰지도 않음
- 미확정 3대(C1 수수료율·C2 지급 캘린더·C4 예상 지급 차액) 확정으로 올리지 않음 · 6대 개념 합치지 않음
- `roster16_apply.py` 실행 금지 (두 번 돌리면 엑셀 행 겹침)
