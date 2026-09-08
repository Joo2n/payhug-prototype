# 교차 검사 A — 2026-09-08 라운드 (V1.3 확정 → 툴팁 정렬 → 「기호 = 산식」 규칙 → 배포 → Figma)

검사 시각 2026-09-08 · 검사자 감시자 A · 파일 수정 0건 · 산출물 직접 개봉(git diff · md5 · 헤드리스 크롬 CDP 실측 · 검사기 재실행)

## 결론

1. 변경 범위는 지시 안이다. `9972f0b..d7ce377` 11파일(app.html · 낱장 9 · base.css)이고, 툴팁·base.css 1줄·JS 주석 외의 변경은 **app.html 엑셀 매니페스트 `made:` 14줄(11:36→13:35) 1건**뿐이다. 생성기가 xlsx 실제 mtime 을 읽어 넣는 자리이고 step12 보고서 §0-d 에 밝혀져 있다. README.md 는 diff 에 없다(보고서도 「재생성 결과 동일」).
2. 툴팁 8종 첫 줄은 V1.3 표 2 산식 칸과 첨자까지 글자 단위로 같다(정적 파일 grep + 헤드리스 렌더 실측 양쪽). 둘째 줄 규칙은 **「투자실행액」 카드 1종이 부분** — `A_i | 순지급액_i × (1 − r)` 는 오른쪽이 값이 아니라 산식이고, 표 2 조건 행 `i | 정산예정일이 d 보다 뒤인 채권` 이 없다.
3. V1.3 워드·HTML 은 15:18:40 이후 바뀌지 않았다(Downloads ↔ artifact md5 동일). 표 4 툴팁 열은 화면과 7자리 어긋난다 — 결함이 아니라 문서 후속 갱신 대상.
4. 검사기 `verify_final_terms.py` 302 PASS · 0 FAIL · 종료 0. 배포 3곳 md5 = 커밋(d7ce377 · 19c1440 · 3ddc511) 전건 일치, origin/main 도 같은 SHA. Figma 맵 source_commit d7ce377 · 프레임 37 · 금지어 0 · 이전 두 판 36노드 retired 기록.
5. 조 보고서 7건 모두 존재하며 생성 시각(17:12 → 18:32)이 작업 순서와 맞는다. 콘솔 오류 0(낱장 favicon 404 는 네트워크). 부수 피해 없음. 기존 결함 1건(증명서 모달 취소·발급 시 엑셀 재다운로드)은 이 라운드 변경 밖이다.

## 항목별 판정

| # | 확인 항목 | 판정 | 근거 |
|---|---|---|---|
| 1 | 변경 범위 | **이행** (지시 밖 변경 1건 있음, 아래 표) | `git -C payhug-investor-admin diff 9972f0b..d7ce377 --stat` → 11파일 111+/110−. README.md 없음(`git log -- README.md` 마지막 6d58374). 툴팁·base.css·주석 제외 변경 줄 = XLSX `made:` 14줄만 (app.html:1590~1591 · 1594~1605) |
| 2 | 툴팁 = V1.3 표 2 (8종) | **부분** — 7종 이행 · 「투자실행액」 카드 부분 | 헤드리스 실측(`xa_cdp_result.json`): D `D = Σ( A_i × D_i ) ÷ Σ A_i` · LR `LR = Σ L_i ÷ Σ A_i` · Y_r `Y_r = r × 365 ÷ D` · PA `PA = Σ A_i` · PY_a `PY_a = PMR × 365 ÷ PD` · PY_t `PY_t = PY_a × 채권 비중 + 순현금 수익률 × 순현금 비중 ⏎ = PM × 365 ÷ ( Σ( A_i × D_i ) + PEC )` · 투자실행액 `Σ A_i`. V1.3 표 2 파싱 결과와 글자 일치. `th` 안 패널 computed `text-transform: none` 전건. 연환산 행 맨 아래 전건. 위반: app.html:2180~2182 `A_i | 순지급액_i × (1 − r)` (오른쪽 산식) · 조건 행 `i` 없음 |
| 3 | 문서 무변경 | **이행** | `투자자어드민 기호정리표_V1.3.docx` md5 `0642eed4…` · `.html` md5 `766527ef…` Downloads ↔ `session_0904/artifact/` 동일, mtime 둘 다 `2026-09-08 15:18:40`. artifact git 마지막 커밋 40a2517(15:30) |
| 4 | 원고·검사기 | **이행** | `python3 verify_final_terms.py` → 판정 302 · PASS 302 · FAIL 0 · exit 0. `final_terms.json` vars 27건 중 D·LR·Y_r·Σ A_i·A_i·PA·PY_a·PY_t 의 term·formula = 표 2 (커밋 697e588) |
| 5 | 배포 = 커밋 | **이행** | demo app.html `e18f5d53…` · invest-profit.html `4d35e2b4…` · invest-assets.html `e400e776…` · base.css `b50a650f…` = `git show d7ce377:`. prototype `/` `5033ff77…` = `19c1440:index.html`. glossary `/` `3ae96f05…` = `3ddc511:index.html`. 세 레포 모두 `main...origin/main` 워킹트리 0 |
| 6 | Figma 맵 | **이행** | `figma_map_investor.json`(커밋 5eb3507) source_commit `d7ce377` · prev `0b6ab0d` · frames 37 · verification.forbidden_texts 26종 전 0 · `deleted_0908`(9972f0b 판 18) · `deleted_0908b`(0b6ab0d 판 18) 36노드 전부 `retired` 에 replaced_by 와 함께 있음. `_fig/` 37파일 워킹트리 0, 툴팁 줄 출력 레포와 동일 |
| 7 | 교차 검증·QA·검수 보고서 | **이행** | step12_builder 17:12:09 · step12_terms 17:22:27 · step12_figma 17:39:45 · step12_qa 17:50:56 · step13_builder 18:02:21 · step13_qa 18:22:55 · step13_figma 18:32:11 (전부 2026-09-08). QA 산출 `session_0904/qa/screen_ab_0908/` 33장 · `figma_0908b/` 10장 |
| 8 | 생성기 ↔ 산출물 | **이행** (소멸위험 없음) | `build_app.py`(1294·1295·1302·1324·1332·1966·1975·2263·2272) · `build_sim_static.py`(123·131·265·274) · `sync_profit_static.py` 에 새 툴팁 문구 있음, 옛 문구 0. payhug 레포 커밋 697e588 · 59526ff. base.css 는 출력 레포가 원천(prep_fig 가 복사) |
| 9 | 부수 피해 | **없음** | 헤드리스 CDP: app.html#invest-assets 툴팁 8 · #invest-profit 4 · 낱장 3종 정상, `Runtime.exceptionThrown` 0, 콘솔 error 0(낱장 첫 로드 favicon 404 만). diff 에 모달·메뉴·표·값 코드 변경 없음 |

## 보고서와 실제가 다른 곳

| 자리 | 보고 | 실제 |
|---|---|---|
| 상위 요약 「README.md 실측 수치 변경」 | 바뀐 파일에 README.md 포함 | diff 에 없음. step12·13 builder 보고서 자체는 「재생성 결과 동일 → diff 없음」 이라 조 보고와 산출물은 일치 |
| 상위 요약 「base.css `text-transform:none`」 | 1속성 | base.css:509 `.tooltip .tip-panel { text-transform: none; letter-spacing: 0; }` — letter-spacing 도 같이 들어감 |

## 지시 밖 변경

| # | 파일:줄 | 무엇 | 출처·보고 여부 | 판정 |
|---|---|---|---|---|
| 1 | app.html:1590~1591 · 1594~1605 (14줄) | 엑셀 매니페스트 `made:'2026-09-07 11:36'` → `'2026-09-07 13:35'`. 화면 「엑셀 내려받기」 목록의 생성일시로 보인다 | `build_app.py` 가 `assets/xlsx/*.xlsx` mtime(13:35:49)을 읽어 넣는 자리. 9972f0b 의 app.html 이 xlsx 재생성 전 값으로 굳어 있던 것이 재빌드로 맞춰짐. step12 builder §0-d 에 명시 | 지시 밖이나 생성기 부수효과 · 값이 실물과 맞게 됨. 되돌릴 필요 없음 |
| 2 | invest-profit--empty.html 툴팁 | `PMR 0%`→`0.000000%` · `PD 0일`→`0.00일` · `PY_a 0%`→`0.00%` | `sync_profit_static.py` 빈 상태 호출 서식 통일(59526ff). step13 builder 「다르게 한 것」 에 명시. 값 0 그대로 | 툴팁 안 서식 정렬. 문제 없음 |
| 3 | app.html:1773 · 1781 | JS 주석 2개(⑥·③ 열머리 경위)를 「투자자어드민 기호정리표 V1.3 표 4」 한 줄로 교체 | step12 builder §0-a. 옛 주석이 `<script>` 로 실려 「옛 문구 0건」 검사에 걸림 | 화면 비노출. 문제 없음 |
| 4 | 투자 자산 「예상 연환산 수익률」 카드 툴팁 | 값 행 「연 환산 | 13.21%」 삭제 | 규칙 적용(연환산 행 맨 아래 = 설명 행). 카드 본문 13.21% 는 그대로 | 툴팁 범위 내 |

그 외 값·라벨·메뉴·레이아웃 변경 0건.

## 둘째 줄 규칙 — 판정 보류 (규칙 문구 해석)

| 자리 | 화면 | 읽기 A | 읽기 B |
|---|---|---|---|
| PY_t 툴팁 값 행 `Σ( A_i × D_i ) | 559,275,516원` (app.html:2412 · 2707 · invest-profit.html · invest-sim--result.html) | 행 라벨에 Σ | 「정의 줄에만 Σ」 위반 | V1.3 표 4 PY_t 툴팁 열이 「PY_a · Σ( A_i × D_i ) · PEC · EC 값」 을 명시 → 확정본 기준 적합 |
| EC 행 `EC | 20,000,000원 × 7일` (`tip-row sum` 구분선 위) | 오른쪽이 값 × 일수 | 값 아님 | PEC 의 산출 근거 표시, 표 4 「EC 값」 |

확정본이 기준이라는 원칙(feedback_confirmed_doc_is_baseline)에 따르면 읽기 B. 최종 결정은 규칙 원문을 낸 쪽이 한다.

## 문서 후속 갱신 필요 (V1.3 표 4 툴팁 열 ↔ 화면)

| 기호 | 표 4 툴팁 열 | 화면 툴팁(d7ce377) | 갱신 방향 |
|---|---|---|---|
| Σ A_i 투자실행액 | 빈칸 | `Σ A_i` / `A_i | 순지급액_i × (1 − r)` / `r | 0.11%` (통합본·시연본만, 낱장 4장 없음) | 표 4 에 툴팁 유무·내용 결정 후 기재. 화면은 조건 행 `i` 추가 여부 결정 |
| D | 「보유 채권 전체」 | `D = Σ( A_i × D_i ) ÷ Σ A_i` / `i | 보유 채권 전체 · 61,760건` | 첫 줄 산식 + 건수 반영 |
| LR | 「선정산일이 오늘 기준 20일 전 ~ 11일 전인 표본」 | `LR = Σ L_i ÷ Σ A_i` / `i | 선정산일이 오늘 기준 20일 전 ~ 11일 전 · 3,200건` | 「인 표본」 삭제 · 건수 반영 |
| Y_r | 「연환산 · 일부 기간의 …」 | `Y_r = r × 365 ÷ D` / `r | 0.11%` / `D | 3.04일` / `연환산 | …` | 첫 줄 산식 + r·D 값 행 |
| PY_a | 「연환산 · 위와 같음. PMR · PM · PA · PD 값」 | 첫 줄 `PY_a = PMR × 365 ÷ PD` + 값 행 4 + 연환산 맨 아래 | 첫 줄 산식 · 연환산 행 위치 |
| PY_t | 「연환산 · 위와 같음. PY_a · Σ( A_i × D_i ) · PEC · EC 값」 | 첫 줄 2행(조립 산식 ⏎ 전개) + 값 행 4 + 연환산 맨 아래 | 첫 줄 2행 구조 |
| PA · PY_a (일별 표 열머리) | 표 4 에 열머리 툴팁 정의 없음 | `PA = Σ A_i` / `i | 정산예정일이 그 날짜인 보유 채권` · `PY_a = PMR × 365 ÷ PD` / 같은 조건 행 / 연환산 | 열머리 툴팁 행 추가. 주별·월별 표에서 「그 날짜」 문구 적정성 확인 |
| 용어 해설(glossary.html · payhug-investor-glossary 3ddc511) | — | 「대상정산금채권」 93 · 「미확정」 36 · V1.3 용어(보유 채권·PY_a) 0. 마지막 재생성 b4f41b3(9/4) | 지시상 불변(step12 builder §4-7). V1.3 용어로 재생성할지 결정 필요 |

## 기존 결함 · 참고

| 항목 | 내용 |
|---|---|
| 증명서 모달 취소·발급 시 가맹점별 엑셀 재다운로드 | step12·13 QA 「중」 1건, 재현 2/2. 이 라운드 diff 에 모달 코드 없음 → 9972f0b 이전부터 있는 결함 |
| `verify_crossscreen.py` FAIL 3 | 전부 glossary.html duration 허용 블록 검사. 9972f0b 에서도 같음(step13 builder §7) |
| 전후 비교 HTML | `~/Downloads/payhug_용어정의서/V1.3_반영_전후비교_20260908.html` = `session_0904/artifact/v13_before_after.html` (18:36:26, md5 `18dce922…`). 사용자 「다시 보여주고」 에 대응하는 산출물로 보임. artifact 사본은 git 미추적(`??`) |
| 미추적 파일 | `session_0904/reports/step12_*·step13_*` 7건 · `qa/screen_ab_0908/` · `qa/figma_0908b/` · `artifact/v13_before_after.html` — payhug 레포에 커밋되지 않음 |

## 검사 방법

- `git diff 9972f0b..d7ce377` 전문 → `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/xa_diff_full.patch`
- V1.3 HTML 표 1~4 파싱(정규식, `<sub>`→`_{}`), 화면 툴팁은 정적 grep + 헤드리스 크롬 CDP(`xa_cdp.js`, 로컬 http 8771 · 디버그 9771, 결과 `xa_cdp_result.json`)
- 배포 실물 curl → `xa_deploy/` md5 ↔ `git show <sha>:<file> | md5`
- 검사기 `python3 verify_final_terms.py` 직접 실행
