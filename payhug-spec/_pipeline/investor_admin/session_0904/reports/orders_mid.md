# 지시 이행 중간 판정 — 2026-09-04 22:10 기준

판정 근거는 산출물·저장소·배포 실물을 직접 연 결과입니다. 다른 조의 보고서는 존재 여부만 셉니다. Figma 실물은 이 조 도구 밖이라 `figma_map_investor.json` 의 기록으로만 적습니다.

## 미착수·누락

| 구분 | 항목 | 근거 |
|---|---|---|
| 미착수 | **B 배포** | 전체본 `origin/main`=`1f5c6a4`(8/31 12:08) 뒤로 미푸시 커밋 6건 + 오늘 수정분 미커밋(`git status`: app.html 등 M, xlsx 12건 D). 시연본 미푸시 3건 + 작업 트리 M. Vercel 전체본 `invest-assets.html`: `S입금부족율` 2·`W금융일수` 3·`입금부족률` 0. Vercel 시연본: `invest-sim` 24·`xls-` 32·`S입금부족율` 8·`W금융일수` 16·`Ty수익율` 19·「투자자 어드민」 1 |
| 누락 산출물 | `NEXT_SESSION.md` (E) | `find ~/cursor/payhug ~/cursor/payhug-investor-admin -iname 'NEXT_SESSION*'` 0건 |
| 누락 산출물 | `session_0904/` 커밋 (E) | `git status`: `?? payhug-spec/_pipeline/investor_admin/session_0904/` 미추적. `git log -- session_0904` 0건 |
| 누락 산출물 | `reports/step6_tooltip_report.md` (C) | 없음. `survey/step6_tooltip_map.md` 만 있음 |
| 누락 산출물 | `reports/step7_notation_report.md` (G) · `step7_ty5_report.md` (H) · `step7_sim_hide_report.md` (K) | `find session_0904 -iname 'step7*'` 0건 |
| 누락 산출물 | 교차검증 보고 2건 (J) | 없음. `verify/xv_A·B·C` 는 D 의 ⑤ 검증이지 J 의 배포 후 교차검증이 아님 |
| 누락 산출물 | `reports/orders_final.md` (N) | 없음 (이 파일이 `orders_mid`) |
| 누락 작업 | 로그인 되돌림 (M) | `login.html`·`_fig/login.html` 8/28 22:40 판 그대로, `app.html` 로그인 카드 「투자자 어드민」 2건 |
| 누락 작업 | 시연본 엑셀 미리보기 제거 로직 (L) | `scripts/sync_prototype.py` 에 `xls-` 제거 없음 (`BANNED`·`BANNED_WORDS`·`SIM_BANNED` 상수 어디에도 없음) |
| 누락 작업 | 시연본 변환 실행 (K·L) | scratchpad `proto_dry/` 없음. 시연본 로컬 `index.html` 9/2 01:51 판(`invest-sim` 24·`xls-` 32) |

## 행별 판정

| # | 지시 | 상태 | 근거(파일:줄 또는 명령 결과) | 남은 것 |
|---|---|---|---|---|
| A | UI 용어 수정 | **끝** | `_fig/*.html` 31장 옛 표기 8종 0건. `invest-*.html`·`certificate.html`·`xls-*.html` 0건. `app.html` 잔량은 `/* */` 주석(1297·1483·1845·1875·2404~2412·2432~2435·2462~2464·2589·2607행)·JS 변수명 `PwD`(2657~2918행)·「대표 DM」 행(2304행)뿐, 화면 노출 라벨·툴팁 0건. xlsx 14벌×2(admin·_fig) 머리글 = 「가중평균 금융일수 · 입금부족률 · 예상 연환산수익률 · 연환산수익률」, 옛 표기 셀 0. PDF 2벌 텍스트 옛 표기 0 | 범위 밖 문서형 HTML(`glossary.html` `S입금부족율` 38·`W금융일수` 24·`Ty수익율` 24·`PwD` 31, `capability`·`feasibility`·`inquiry`·`calc`·`final-terms`·`terms-edit`·`steps-all`·`archive`·`review`·`ceo-questions`)은 인용 여부 미확인 |
| B | 배포 | **미착수** | 위 「미착수」 행 | 전체본 커밋·push, `sync_prototype.sh` 실행·push, 배포 실물 재확인 |
| C | 툴팁 기호마다 용어명 | **진행 중** | 로컬 10장에서 `PMR→기간 투자수익율`·`PA→기간 투자실행금`·`PEC→기간 순현금`·`EC→순현금`·`PY_a→투자실행금액 대비 연환산수익률` 확인: admin `app.html`(각 2)·`invest-profit.html`·`--weekly`·`--monthly`·`--empty`·`invest-sim--result.html`, `_fig/invest-profit*.html` 4장. 기호만 있고 용어명 없는 tip-row 0건. ⑤ 툴팁 산식 `PM × 365 ÷ ( Σ( A_i × D_i ) + PEC )` (`invest-profit.html:174`). 배포 실물 `invest-profit.html`: `PMR` 용어명 0·`Ty수익율` 2 | `step6_tooltip_report.md` 없음. 「16 HTML」 대비 10장 — 대상 정의 확인 필요. 배포 미반영(B) |
| D | ⑤ 검증 → 워드·HTML 확정본 | **끝** | 검증 3건 `verify/xv_A_blind.md`(판정 표·결론: `PA + PEC` 불성립 → `Σ(A_i × D_i) + PEC`)·`xv_B_adversarial.md`(§5 결론)·`xv_C_numbers.md`(원장 재계산 표). 워드 `~/Downloads/payhug_용어정의서/기호정리표_20260904_2155.docx` 표 1: `PD = Σ( Ai × Di ) ÷ Σ Ai`·`PYt = PM × 365 ÷ ( Σ( Ai × Di ) + PEC )`·`PYa = PMR × 365 ÷ PD`, 아래첨자 run 81·리터럴 `_` 0. HTML 같은 시각본 `<sub>` 81·`_{` 0·PD식 1·PYt식 1. `final_terms.json`(21:53) 3식 같음. `reports/step6_doc_report.md`·`step6_doc_audit.md` 있음 | `final_terms.json` 설명문이 화면 옛 라벨 「W금융일수」·「Ty수익율」을 인용(175·209·250·266행) — 화면 라벨은 바뀌어 어긋남 |
| E | 아티팩트 정리·깃 저장·NEXT_SESSION | **진행 중** | `session_0904/` 21파일(artifact 2·qa 2·reports 6·survey 4·verify 6·ORDERS 1) | `NEXT_SESSION.md` 없음. 커밋 0건(미추적) |
| F | UI·Figma 먼저, 용어정의 다음 | **진행 중** | 산출 순서 step4_ui_terms → step5 builder(UI) → step6 doc 로 UI가 용어정의보다 앞 | Figma 부분 미착수(I·K·L·M 의 삭제 8건 맵상 「페이지에 남아 있음」) |
| G | 표기 통일 | **끝** | 워드 표 1: `D = Σ( Ai × Di ) ÷ Σ Ai`·`A = 순지급액 × ( 1 − r )`·`M = 채권매입수수료 − max( 0, L )`·`B = 순지급액 − max( 0, L )`·`L = 미지급금 − 과지급금`·`MR = M ÷ A`. `PD` 분모 `Σ Ai`. `PYt` Σ 꼴. 표 0 「접두 P = 조회기간」+ 산식 뒤 `i ∈ P` 로 P·Σ 한 규칙. HTML·JSON 같음 | `step7_notation_report.md` 없음 |
| H | ⑤ 산식 교체 (2.32 → 3.30) | **끝** | `daily_ledger.py:181` `TY5_EXPR = 'ty4 * ad / tot'`, `:248` `tot = ad + psc`. `ledger_facts.json:54` `weekTyAsset 3.30`·`:57` `3.299662`. `invest-profit.html:175` `3.30`, `2.32%` 0건(invest-profit 3장·app·_fig). `투자수익현황_2026-08-20_2026-08-26.xlsx` B8 = 0.033 (admin·_fig 둘 다). 배지 「미확정」 4·「대표 확인 대기」 1 (invest-profit 3장·_fig) | `step7_ty5_report.md` 없음. 검산 엑셀(`build_audit_xlsx.py` 21:57 수정) 실물 미확인 |
| I | Figma 는 프로토타입 화면만 | **진행 중** | `prep_fig.py:31~41` IMPORT 24건, `index`·`coocon`·`invest-sim`·`xls-*`·`login` 제외. `figma_map_investor.json` frames 24, retired: coocon `3341:2` 「삭제 대상 · 페이지에 남아 있음」, index `3373:2` 「파일에서 조회되지 않음 · 사용자 삭제」 | Figma 삭제는 확인 불가 · 다른 조 몫. 맵 기록상 `3341:2` 아직 남음. IMPORT 수 24 — 지시문의 「25」와 다름 |
| J | 교차검증 2건 | **대기** | B 선행. 보고 0건 | B 뒤 |
| K | 시뮬 숨김 | **진행 중** | `scripts/sync_prototype.py`(22:07·미커밋) `:31` `SIM_BANNED`, `:82` 메뉴 제거·`:89` section 제거·`:102` CSS·`:112~135` DERIVE/SEED/META/JS 제거. IMPORT·맵 제외(retired `3376:2`·`3378:2` 「페이지에 남아 있음」). 통합본 `app.html` 시뮬 유지 | 변환 미실행(시연본 `index.html` 9/2 판 `invest-sim` 24, Vercel 24). `gate_prototype.js`(9/2) 에 sim 검사 없음. Figma 삭제 확인 불가. `step7_sim_hide_report.md` 없음 |
| L | 엑셀 미리보기 현행화 | **진행 중** | IMPORT·맵 제외(retired `3370:2`·`3372:2`·`3375:2`·`3377:2` 「페이지에 남아 있음」). 통합본·낱장 `xls-*.html` 유지 | `sync_prototype.py` 에 `xls-` 제거 로직 없음. 시연본 로컬·Vercel `xls-` 32. Figma 삭제 확인 불가 |
| M | 로그인 되돌림 | **진행 중** | 실물 `payhug-admin-web/app/login/page.tsx:112` 「관리자 로그인」·`:132` placeholder 「휴대전화번호 또는 사업자번호」·`:186` 「안내:」, 「투자자 어드민」 0. `login.html`(8/28 22:40): 「투자자 어드민」·「사업자등록번호 또는 휴대전화번호」·「비밀번호 찾기」. `_fig/login.html` 같음. `app.html` 로그인 카드 「투자자 어드민」 2·「관리자 로그인」 0. IMPORT·맵 제외(retired `3371:2` 「페이지에 남아 있음」) | UI 되돌림 미착수(3파일). 대조 표 없음. Figma 삭제 확인 불가 |
| N | 추적 에이전트 | **진행 중** | `ORDERS_0904.md`(22:02) 15건. 이 파일 `orders_mid.md` | `orders_final.md` |
| O | 완료 후 한 번에 답 | **대기** | 미완 항목 11건 | 전부 끝난 뒤 |

## 로그인 대조 (M)

| 자리 | 실물 `page.tsx` | `login.html` · `_fig/login.html` | `app.html` 로그인 카드 |
|---|---|---|---|
| 제목 | 「관리자 로그인」(`:112`) | 「PayHug Admin」+「투자자 어드민」 | 「PayHug Admin」+「투자자 어드민」 |
| 아이디 placeholder | 「휴대전화번호 또는 사업자번호」(`:132`) | 「사업자등록번호 또는 휴대전화번호」 | 「사업자등록번호 또는 휴대전화번호」 |
| 하단 | 「안내:」(`:186`) | 「비밀번호 찾기」 | 「비밀번호 찾기」 |

## 배포 실물 (B)

| URL | 상태 | 확인 값 |
|---|---|---|
| `https://payhug-investor-demo.vercel.app/invest-assets.html` | 200 | `S입금부족율` 2 · `W금융일수` 3 · `입금부족률` 0 |
| `https://payhug-investor-demo.vercel.app/invest-profit.html` | 200 | `PMR` 용어명 0 · `Ty수익율` 2 · `3.30` 0 |
| `https://payhug-investor-prototype.vercel.app/` | 200 | `invest-sim` 24 · `xls-` 32 · `S입금부족율` 8 · `W금융일수` 16 · `Ty수익율` 19 · 「투자자 어드민」 1 |

끝 4 · 진행 중 8 · 대기 2 · 미착수 1
