# 지시 이행 최종 판정 — 2026-09-04 23:05 기준

판정 근거는 저장소·배포 실물·산출물 파일을 직접 연 결과입니다. 다른 조의 보고서는 존재 여부만 셉니다. Figma 실물은 이 조의 도구 밖이라 `figma_map_investor.json`·`prep_fig.py`·QA 캡처로 적습니다. `orders_mid.md`(22:11) 는 그때 남았던 것의 목록으로만 참고했습니다.

## 미착수·누락

없음.

## 확인 필요 (지시 밖이지만 판정 중 드러난 것)

| 항목 | 내용 | 근거 |
|---|---|---|
| 워드·HTML 파일 위치 | `기호정리표_20260904_2155.docx/html` 이 22:59 에 `~/Downloads/payhug_용어정의서/1차 최종/투자자어드민 기호정리표_V1.0.docx/.html` 로 옮겨져 있음 (크기 40,288 / 13,594 · mtime 21:55 그대로). `NEXT_SESSION.md`·`ORDERS_0904.md` 가 적은 경로는 옛 이름 | `ls ~/Downloads/payhug_용어정의서/` · `1차 최종/` 폴더 22:59 생성 |
| `final_terms.json` 설명문 | `plain` 175·209·250·266행이 화면 라벨을 「W금융일수」·「Ty수익율」로 인용. 화면 라벨은 「가중평균 금융일수」·「연환산수익률」 | `final_terms.json:175,209,250,266` · `invest-assets.html` 옛 표기 0 |
| 시연본 `coocon` 화면 | `index.html:815` `data-screen="coocon"` 링크 카드(We-bank 바로가기)가 남아 있음. 지시 I 는 Figma 대상이라 판정에 넣지 않음 | `git -C ~/cursor/payhug-investor-prototype show HEAD:index.html` |

## 행별 판정

| # | 지시 | 상태 | 근거 | 남은 것 |
|---|---|---|---|---|
| A | UI 용어 수정 | **끝** | 화면 HTML 12장(`invest-*`·`certificate`·`login`·`contracts`·`merchants`·`index`·`coocon`) 옛 표기 7종 0. `app.html` 잔량은 `/* */` 주석(1320·1506·1868·1898·2433~2456·2485·2630행)과 「대표 DM 16:27」 인용(2327행)뿐, 노출 라벨 0. `_fig/*.html` 24장 0. xlsx 14벌×2(admin·`_fig`) 옛 표기 셀 0 · 머리글 「가중평균 금융일수 · 입금부족률 · 예상 연환산수익률 · 연환산수익률」. PDF 2벌 텍스트 옛 표기 0 · 「입금부족률」1 · 「연환산수익률」1. Vercel 전체본 `invest-assets.html` 「입금부족률」2 · 「가중평균 금융일수」3 · 옛 표기 0 | 문서형 HTML(`glossary`·`calc`·`capability` 등 12장)은 범위 밖 · 미판정. `app.html:1074` 통합본 제목 「투자자 어드민」은 로그인 카드가 아니라 손대지 않은 자리 |
| B | 배포 | **끝** | 전체본 `origin/main` = `b4f41b3` (22:49:43) · ahead/behind 0/0 · 작업 트리 clean. 시연본 `origin/main` = `75bc47b` (22:51:25) · 0/0 · clean. Vercel 전체본 `invest-assets`·`invest-profit`·`app`·`login`·`certificate` 5장 로컬과 `cmp` 바이트 동일 (`invest-profit.html` 「3.30」1 · 「PMR」4). Vercel 시연본 `/` = HEAD `index.html` 바이트 동일 (191,943B) | 없음 |
| C | 툴팁 기호마다 용어명·산식 | **끝** | tip-row 전수 검사(18파일): 기호만 있고 용어명 없는 행 0. 용어명 붙은 행 `app.html` 10 · `invest-profit` 4장 각 5 · `invest-sim--result` 5 · `_fig/invest-profit` 4장 각 5. 카드 툴팁 2건 `app.html` `Σ A<sub>i</sub> · 투자 실행액`·`Y<sub>r</sub> · 예상 연환산수익률 · r × 365 ÷ D` 각 2. ⑤ 머리글 `PY<sub>t</sub> · 투자자산 대비 연환산수익률` 2. `invest-profit.html:174` 산식 `PM × 365 ÷ ( Σ( A_i × D_i ) + PEC )`. Vercel 전체본 = 로컬 바이트 동일. `reports/step6_tooltip_report.md` (22:12) 있음 | 없음 |
| D | ⑤ 검증 → 워드·HTML 확정본 | **끝** | 검증 3건 `verify/xv_A_blind.md`·`xv_B_adversarial.md`·`xv_C_numbers.md` + 계산기 `.py` 3. 워드 `1차 최종/투자자어드민 기호정리표_V1.0.docx`(21:55 판) 표 1 `PYt = PM × 365 ÷ ( Σ( Ai × Di ) + PEC )`·`PD = Σ( Ai × Di ) ÷ Σ Ai`·`PYa = PMR × 365 ÷ PD`, 아래첨자 run 81 · 리터럴 `_{` 0 · 옛 라벨 0. HTML `<sub>` 81 · `_{` 0 · 옛 라벨 0. `final_terms.json:273` 같은 식. `reports/step6_doc_report.md`·`step6_doc_audit.md`·`step7_doc_audit.md` 있음 | `final_terms.json` 설명문의 옛 화면 라벨 인용 (위 확인 필요 표) |
| E | 아티팩트 정리·깃 저장·NEXT_SESSION | **진행 중 · 커밋 전** | `session_0904/` 33파일 (ORDERS 1 · artifact 4 · qa 3 + figma 9 · reports 14 · survey 4 · verify 6). `NEXT_SESSION.md` (22:32 · 7,493B) 있음 — 산출물 위치·남은 작업 표. `artifact/ceo_review.html` (22:12) `Σ( A_i × D_i )` 3. payhug 레포 `git status`: `?? NEXT_SESSION.md` · `?? session_0904/` 미추적 · 커밋 0 | payhug 레포 커밋 (이 판정 뒤 예정) |
| F | UI·Figma 먼저, 용어정의 다음 | **끝** | 파일 시각: UI 라벨 `step5_*` 21:43 → 워드 21:55 → 툴팁 22:12 → 로그인 22:14 → Figma 22:26. UI 가 용어정의보다 앞. Figma 삭제 대상 8건은 착수 시점 이미 없었고(`figma_map` `deleted_at`), 로그인 프레임은 M 지시 뒤 삭제 | 없음 |
| G | 표기 통일 | **끝** | 워드 표 1: `D = Σ( Ai × Di ) ÷ Σ Ai`·`A = 순지급액 × ( 1 − r )`·`M = 채권매입수수료 − max( 0, L )`·`B = 순지급액 − max( 0, L )`·`L = 미지급금 − 과지급금`·`MR = M ÷ A`. `PD` 분모 `Σ Ai`. `PYt` Σ 꼴 + `= PYa × Σ( Ai × Di ) ÷ ( Σ( Ai × Di ) + PEC )`. 표 0 「접두 P | 조회기간」 + 산식 뒤 `i ∈ P` (HTML 5곳). 표 2 전환표 `PA + PEC → Σ( Ai × Di ) + PEC`. `reports/step7_notation_report.md` (22:12) 있음 | 없음 |
| H | ⑤ 산식 교체 (2.32 → 3.30) | **끝** | `daily_ledger.py:181` `TY5_EXPR = 'ty4 * ad / tot'` · `:186` `tot = ad + psc` · `:248` `TY5_JS`. `ledger_facts.json:54` `3.30` · `:57` `3.299662`. `invest-profit.html` 「3.30」1 · 배지 「미확정」4 · 「대표 확인 대기」1 · `app.html:1886` `PEND5_ROW`. 리터럴 `2.32%` 0 (`app`·`invest-profit` 4장·`_fig` 4장·시연본). xlsx `투자수익현황_2026-08-20_2026-08-26` B8 = 0.033 (admin·`_fig`). 검산 엑셀 `검산_투자자어드민_20260901.xlsx`(21:58) 입력 C19 `=ROUND(기간집계!B13*기간집계!B9/(기간집계!B9+기간집계!B15),6)` (④ × Σ(Ai×Di) ÷ (Σ(Ai×Di)+PEC)) · 화면대조 E32 = 3.3 · 산식 시트 B43 옛 식은 「[2번 이미지]」 대표 원문 인용. `reports/step7_ty5_report.md` (22:12) 있음 | 없음 |
| I | Figma 는 프로토타입 화면만 | **끝 (도구 내 산출물 기준)** | `prep_fig.py:31~41` IMPORT 24 — `index`·`coocon`·`invest-sim`·`xls-*`·`login` 없음. `figma_map_investor.json` `frames` 24 = IMPORT 24 = `_fig/*.html` 24. `retired` 중 이번 대상 9건 전부 `status: 삭제 완료` — `coocon 3341:2`·`index 3373:2`·`invest-sim 3376:2`·`3378:2`·`xls 3370:2`·`3372:2`·`3375:2`·`3377:2` 「착수 시점 조회되지 않음」, `login 3371:2` 「이 라운드에서 삭제」. `qa/figma/3403~3412.png` 9장. `reports/step7_figma_report.md` (22:26) 있음 | Figma 실물 재확인은 J 교차검증 몫 |
| J | 교차검증 2건 | **진행 중 · 보고서 도착 전** | `reports/` 14파일 중 `xcheck_A.md`·`xcheck_B.md` 0건. 선행 조건 B 는 끝 | 보고 2건 도착 |
| K | 시뮬 숨김 | **끝** | `scripts/sync_prototype.py:32` `SIM_BANNED` · `:84` `drop_sim()`. `gate_prototype.js`(22:29) `:28` `PROTO_DROPPED` · `:30` `SIM_TRACE` · `:194~196` 메뉴·화면·`SCREEN_ORDER` 검사. 시연본 HEAD `index.html` `invest-sim` 0 · 「시뮬레이션」 0 · 사이드바 `nav-item` 7 (`invest-assets`·`invest-returns`·`merchants`·`receivables`·`contracts`·`kcoon`·`password`). 통합본 `app.html` `data-screen="invest-sim"` 1 · 메뉴 1 유지. Figma `3376:2`·`3378:2` 맵 「삭제 완료」. `reports/step7_sim_hide_report.md` (22:21) 있음 | 없음 |
| L | 엑셀 미리보기 현행화 | **끝** | `sync_prototype.py:35` `XLS_BANNED` · `:185` `drop_xls_preview()`. `gate_prototype.js:33` `XLS_TRACE`. 시연본 HEAD `index.html` `data-screen="xls-*"` 0 (화면 9: `login`·`invest-assets`·`certificate`·`invest-profit`·`merchants`·`acquisition-list`·`contracts`·`coocon`·`password`). `xls-` 잔량 7 = 다운로드 버튼 `data-act="xls-open"` 4 · mount id 1 · `ACT['xls-open']` 핸들러 2 (`pullFile` → 실물 xlsx). 「미리보기」 0. 시연본 `assets/xlsx/` 실물 14벌. 통합본 `app.html` `xls-*` 화면 4 유지. Figma 4건 맵 「삭제 완료」 | 없음 |
| M | 로그인 되돌림 | **끝** | `login.html`(22:14) `PayHug <em>Admin</em>` · 「관리자 로그인」 · 아이디 placeholder 「휴대전화번호 또는 사업자번호」 · 「안내: 이 페이지는 관리자 전용입니다.」 · 「투자자 어드민」 0 · 「비밀번호 찾기」 0 = 실물 `page.tsx:110·112·132·186`. `app.html` 로그인 카드 1093·1100·1115행 같음. 시연본 `index.html` 896·903·918행 같음. `_fig/login.html` 없음. Figma `3371:2` 맵 「이 라운드에서 삭제」. 대조 표 `reports/step7_login_report.md` (가). Vercel `login.html` = 로컬 바이트 동일 | 없음 |
| N | 추적 에이전트 | **끝** | `ORDERS_0904.md` 15건 · `reports/orders_mid.md` (22:11) · 이 파일 | 없음 |
| O | 완료 후 한 번에 답 | **대기** | J 보고 2건 도착 전 · E 커밋 전 | J·E 뒤 |

## 로그인 대조 (M)

| 자리 | 실물 `page.tsx` | `login.html` | `app.html` 로그인 카드 | 시연본 `index.html` |
|---|---|---|---|---|
| 제목 | `PayHug Admin` (`:110`) | `PayHug <em>Admin</em>` | 같음 (`:1092`) | 같음 |
| 부제 | 「관리자 로그인」(`:112`) | 「관리자 로그인」 | 「관리자 로그인」(`:1093`) | 「관리자 로그인」(`:896`) |
| 아이디 placeholder | 「휴대전화번호 또는 사업자번호」(`:132`) | 같음 | 같음 (`:1100`) | 같음 (`:903`) |
| 하단 | 「안내: 이 페이지는 관리자 전용입니다.」(`:186`) | 같음 | 같음 (`:1115`) | 같음 (`:918`) |
| 「투자자 어드민」·「비밀번호 찾기」 | 없음 | 0 · 0 | 0 · 0 | 0 · 0 |

## 배포 실물 (B)

| URL | 상태 | 확인 값 |
|---|---|---|
| `https://payhug-investor-demo.vercel.app/invest-assets.html` | 200 | 로컬 `b4f41b3` 과 바이트 동일 · 「입금부족률」2 · 「가중평균 금융일수」3 · 옛 표기 0 |
| `https://payhug-investor-demo.vercel.app/invest-profit.html` | 200 | 바이트 동일 · 「3.30」1 · 「PMR」4 · 「기간 투자수익율」1 · 「Ty수익율」0 |
| `https://payhug-investor-demo.vercel.app/app.html` · `login.html` · `certificate.html` | 200 | 바이트 동일 |
| `https://payhug-investor-prototype.vercel.app/` | 200 | HEAD `75bc47b` `index.html` 과 바이트 동일 (191,943B) · `invest-sim` 0 · `xls-*` 화면 0 · 메뉴 7 · 「투자자 어드민」 0 · 「관리자 로그인」 1 |

끝 12 · 진행 중 2 · 대기 1 · 미착수 0
