# step15 QA — 통합본 배포본(7493d89) 투자자 공유 정리 실측 (2026-09-09)

대상 `https://payhug-investor-demo.vercel.app/` · 로컬 `/Users/semi/cursor/payhug-investor-admin` main HEAD `7493d89` · 직전 판 `d7ce377`.
실측 도구는 헤드리스 Chrome 152.0.7977.83 + CDP(포트 9333 · 전용 프로필 · `Emulation.setDeviceMetricsOverride` 1440×900 · 클릭은 `Input.dispatchMouseEvent`). 원시 측정값은 `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/qa_share_app_0909/result.json`.

## 하지 않은 것 · 확인 못 한 것

| 구분 | 내용 | 까닭 |
|---|---|---|
| 하지 않음 | 시연본(배포 루트 `index.html`) 실측 | 지시 범위가 통합본 `app.html`·낱장·엑셀입니다 |
| 하지 않음 | 나머지 화면(`index`·`login`·`certificate`·`invest-profit`·`merchants`·`acquisition-list`·`contracts`·`coocon`·`password`·엑셀 미리보기 3종)의 값 단위 직전 판 대조 | 「보관 ㈜」 0건·툴팁 문구만 실측했습니다. 값이 그대로라는 판정은 `app.html` diff 가 그 화면들의 코드에 닿지 않은 것(아래 diff 요약)을 근거로 합니다 |
| 하지 않음 | 시뮬레이션 결과 「수익 현황」 띠(7일 · 39,956,000 · 16,000 · 4.81% · 2.23%)의 직전 판 값 대조 | 카드·표 3개만 기계 대조했습니다. 띠 값은 `simRun()` 에서 `SH` 한 줄만 빠진 diff(`app.html:2531`·`2558`)를 근거로 그대로라고 봅니다 (추정) |
| 확인 못 함 | 직전 판 렌더링 대조는 `git show d7ce377:app.html` 을 로컬 서버에 단독으로 올려 했으므로 `assets/base.css`·`sheet.css` 가 404 였습니다 | 툴팁은 `.tip-panel` innerHTML(DOM) 로 비교해 CSS 유무와 무관합니다. 직전 판의 `innerText` 는 CSS 없이 툴팁 본문이 섞여 값 비교에 쓰지 않았습니다 |
| 스크린샷 | 1장째(투자 자산 기본)에 다운로드 실클릭 직후 토스트 「투자자산현황_….xlsx 내려받기 완료」가 찍혀 있습니다 | 토스트 3,000ms 안에 촬영했습니다. 화면 요소 판정에는 영향이 없습니다 |

## 판정표

| # | 항목 | 기대 | 실측 | 판정 |
|---|---|---|---|---|
| 1 | 배포본 = 로컬 | md5 동일 | `app.html` · 낱장 5 · `xls-assets-status.html` · `투자자산현황_….xlsx` 8개 전부 원격 md5 = 로컬 md5 (`app.html` 0d4813ea… 235,191 B · xlsx c88b9a2f… 5,603 B) | PASS |
| 2 | `app.html` 탭 제목 | 「PayHug Admin — 통합 프로토타입」 | `document.title` = `PayHug Admin — 통합 프로토타입` | PASS |
| 3 | `#invest-assets` 요약 카드 4장 | 「투자자산」 아래 「투자실행액 + 순현금」 · 「투자실행액」「순현금」 아래 줄 없음 · 「예상 연환산 수익률」 아래 「가중평균 금융일수 3.04일 기준」 | `summary-sub` = [`투자실행액 + 순현금`, null, null, `가중평균 금융일수 3.04일 기준`] · 값 100,000,000 / 80,000,000 / 20,000,000 / 13.21% | PASS |
| 4 | 같은 카드 — `/download` · `/cert-confirm` · `/empty` | 위와 같음 (`/empty` 는 「가중평균 금융일수 집계 대상 없음」) | 세 상태 모두 [`투자실행액 + 순현금`, null, null, …] · `/empty` 는 0원 · 0.00% · `가중평균 금융일수 집계 대상 없음` | PASS |
| 5 | 투자 자산 현황 표 | 열머리 5 · 행 3 × 5칸 · 값 80,000,000 · 3.04일 · 0.07% · 13.21% / 20,000,000 / 100,000,000 | th = [자산 구분, 금액 (원), 가중평균 금융일수, 입금부족률, 예상 연환산 수익률] · 행 [투자실행액 80,000,000 3.04일 0.07% 13.21%] [순현금 20,000,000 - - -] [합계 (투자자산) 100,000,000 - - -] 각 5칸 | PASS |
| 6 | 현황 표 빈 상태 | `colspan=5` | `/empty` 행 1개 · `colspan="5"` 「조회 결과가 없습니다.」 | PASS |
| 7 | 가맹점별 표 「비중」 열 | 그대로 | th 6 = […, 예상 연환산 수익률, 비중] · 행 6칸(24.2% · 22.6% · 14.8% · 11.6% …) · 빈 상태 `colspan="6"` | PASS |
| 8 | `#invest-sim/result` 카드 | 「투자실행액」「순현금」 아래 줄 없음 · 값 직전 판과 동일 | [`투자실행액 + 순현금`, null, null, `가중평균 금융일수 3.04일 기준`] · 99,912,000 / 79,912,000 / 20,000,000 / 13.21% — 직전 판 카드 값과 동일(직전 판 sub 는 「비중 80.0% · 보관 ㈜페이허그」「비중 20.0% · 보관 ㈜쿠콘」) | PASS |
| 9 | `#invest-sim/result` 현황 표 | 열 5 · 값 동일 | th 5 · [투자실행액 79,912,000 3.04일 0.07% 13.21%] [순현금 20,000,000 - - -] [합계 99,912,000 - - -] · 채권별 산출 표(10열 8행) 직전 판과 셀 단위 동일 | PASS |
| 10 | 전 화면 「보관 ㈜」 | 0건 | `SCREEN_ORDER` 15 화면 + 4 상태(`/download` `/cert-confirm` `/empty` `sim/result`) 전부 화면 innerText 0 · `body.innerText` 0. 「㈜쿠콘」 도 0 | PASS |
| 11 | 툴팁 8곳 문구 | 직전 판과 동일 · 「투자실행액」 카드 툴팁 포함 | `#invest-assets` `.tip-panel` 8개(카드 2 + 현황 표 th 3 + 가맹점별 th 3) innerHTML 이 `d7ce377` 렌더링과 전부 일치. 「투자실행액」 = `Σ A<sub>i</sub>` / `A<sub>i</sub> → 순지급액<sub>i</sub> × (1 − r)` / `r → 0.11%`. 4 상태 모두 8개 동일 · `invest-profit` 4개 · `sim/result` 4개 동일 | PASS |
| 12 | 사이드바 8 메뉴 라벨 | 그대로 | 투자 자산 · 투자 수익 · 투자 시뮬레이션 · 가맹점 · 정산채권 양수 · 계약기록 · 쿠콘 관리 현금 · 비밀번호 변경 | PASS |
| 13 | 첫 화면 「화면 설계(안)」 · 「㈜테스트인베스트」 | 그대로 | `index` 섹션 첫 줄 「PayHug 투자자 어드민 — 화면 설계(안)」 · 사이드바 하단·엑셀 A1 「㈜테스트인베스트」 | PASS |
| 14 | 엑셀 미리보기 `#xls-assets-status` | 파일바 5.5 KB · 시트 머리 5열 · F·G 빈 셀 | 파일바 「5.5 KB · 생성일시 2026-09-09 14:18 · 시트 1개」 · 1행 제목 `colspan=5` + `c-empty` 2 · 3행 [자산 구분 · 금액 (원) · 가중평균 금융일수 · 입금부족률 · 예상 연환산 수익률] + `c-empty` 2 · 4~6행 5칸 + `c-empty` 2 | PASS |
| 15 | 「엑셀 다운로드」 실클릭 | 실물 xlsx · 5,603 B | 버튼 (1329, 261) 마우스 클릭 → 라벨 「다운로드 중...」 → `Browser.downloadWillBegin` `assets/xlsx/투자자산현황_2026-08-27_2026-08-27.xlsx` → `completed` 5,603 B → 라벨 「엑셀 다운로드」 복귀 · 토스트 「투자자산현황_2026-08-27_2026-08-27.xlsx 내려받기 완료」 · 상태 `invest-assets/default` 유지. 받은 파일 md5 = 로컬 | PASS |
| 16 | 받은 xlsx 내용 | 머리 5열 · ㈜ 0 | `sheet1.xml`: A1 「투자자산 현황 — 2026-08-27 / ㈜테스트인베스트」(`mergeCell A1:E1`) · 3행 A~E 머리 5개 · 4행 80000000 · 3.04 · 0.0007 · 0.1321 · 5행 20000000 · 6행 100000000 · `dimension A1:E6` · 열 폭 5개. 「㈜」는 A1 의 ㈜테스트인베스트 1건뿐, 쿠콘·페이허그·비중·보관 0 | PASS |
| 17 | 낱장 `invest-assets.html` · `--download` · `--cert-confirm` · `--empty` | 카드 sub 없음 · 표 5열 · 보관 0 | 4 파일 모두 sub [`투자실행액 + 순현금`, null, null, …] · th 5 · 행 5칸(`--empty` `colspan="5"`) · 가맹점별 th 6(비중 유지) · 「보관 ㈜」 0 · 탭 제목 「PayHug Admin — 투자 자산 (…)」 | PASS |
| 18 | 낱장 `invest-sim--result.html` | 카드 sub 없음 · 현황 표 5열 · 값 동일 | sub [`투자실행액 + 순현금`, null, null, `가중평균 금융일수 3.04일 기준`] · 현황 표 th 5 · 3행 5칸 · 79,912,000 / 20,000,000 / 99,912,000 · 툴팁 4 = 통합본 `sim/result` 4 | PASS |
| 19 | 낱장 `xls-assets-status.html` | 시트 머리 5열 · 파일바 | 파일바 「5.5 KB · 생성일시 2026-09-09 14:18 · 시트 1개」 · 1행 `colspan=5` + 빈 2 · 3행 머리 5 + 빈 2 · 4~6행 5칸 + 빈 2 · 「보관 ㈜」 0 | PASS |
| 20 | 엑셀 등록부 `size:` | 실물 크기와 일치 | 14 항목 전부 `%.1f KB` 가 실물과 일치 (투자자산현황 5.5 KB = 5,603 B) | PASS |
| 21 | 나머지 엑셀 13종 | 값 그대로 (−1 B 는 문서 속성) | 13 파일 `sheet1.xml`·`styles.xml`·`workbook.xml` md5 직전 판과 동일. 차이는 `docProps/core.xml` created·modified `2026-09-07T04:35:49Z → 2026-09-09T05:18:25Z` 뿐 · 각 −1 B | PASS |

## 기대 밖에서 본 것 (판정 항목 아님 · 이번 커밋이 만든 것 아님)

| # | 내용 | 근거 | 성격 |
|---|---|---|---|
| N1 | 낱장 `invest-assets*.html` 4 파일은 「투자실행액」 카드에 툴팁이 없어 툴팁이 7개입니다. 통합본은 8개 | `invest-assets.html:123` · `--download.html:133` · `--cert-confirm.html:139` · `--empty.html:124` 가 `<div class="summary-label">투자실행액</div>` 로 평문. 통합본은 `app.html:2177` `tip-anchor`. `d7ce377` 낱장도 7개 | 통합본↔낱장 불일치 (기존). 낱장 생성기 `sync_assets_static.py` 의 카드 규격에 「투자실행액」 툴팁이 없는 것으로 추정 (확인 필요) |
| N2 | `#invest-assets/download` 해시로 들어오면 「가맹점별투자자산_….xlsx」 가 자동으로 내려옵니다 | `app.html:2133-2137` `syncToast` → `pullFile`. 실측 `Browser.downloadWillBegin` 이 `app:invest-assets/download` 단계에서 1건 | 설계대로 (직전 판과 동일). URL 공유 시 파일이 바로 내려오는 점은 알고 있어야 합니다 |
| N3 | `scripts/sync_prototype.py` 머리 주석 「투자자 공유 정리 (시연본에만 · 통합본 app.html 은 그대로)」와 `investor_share()` docstring 은 `3978be3` 시점 문장이라 `7493d89`(통합본 자체 정리) 와 어긋납니다 | `scripts/sync_prototype.py:17` · `:255`. 함수 자체는 앵커 0건을 「원본 정리 판」으로 받아 통과시킵니다(`:271-272` · `:289-291` · `:319`) | 시연본 변환기 주석 (지시 범위 밖) |

## diff 요약 (`d7ce377..7493d89`)

`git diff --stat` 25 파일 · +183 −100.

| 파일 | 바뀐 줄 | 지시 1~4 안인가 |
|---|---|---|
| `app.html` | `ASSET_ROWS` `keeper` 필드 제거(1181-1182) · `XLSX` 등록부 `made:` 14건 `2026-09-07 13:35 → 2026-09-09 14:18`, `assets-status` `size:` `5.6 KB → 5.5 KB`(1590-1605) · `RENDER['invest-assets']` `aRatio`·`rExec`·`rCash` 제거, 카드 2장 `summary-sub` 제거, 현황 표 th·행·합계 5칸, `emptyRow(5, …)`(2169-2207) · `simRun()` `SH` 제거(2531·2558) · `simResultHtml()` 카드 2장 sub 제거, 현황 표 5칸(2717-2757) · `sheetData('assets-status')` `sRatio` 제거, 제목 `span:5`, 머리·행·합계 5칸 + `null` 2(3243-3258) | 예 (1·2·3·4 + 등록부) |
| `invest-assets.html` · `--download` · `--cert-confirm` | 카드 `summary-sub` 2줄 · th 2 · 행 3 × td 2 제거 | 예 (1·2) |
| `invest-assets--empty.html` | 카드 `summary-sub` 2줄 · th 2 제거 · `colspan 7 → 5` | 예 (1·2) |
| `invest-sim--result.html` | 카드 `summary-sub` 2줄 · 현황 표 th 2 · 행 3 × td 2 제거 | 예 (3) |
| `xls-assets-status.html` | 파일바 `5.6 KB → 5.5 KB` · 생성일시 · 시트 1행 `colspan 7 → 5` + 빈 셀 2 · 3~6행 F·G 를 `c-empty` 로 | 예 (4 + 파일바) |
| `xls-assets-merchant.html` · `xls-profit-daily.html` · `xls-profit-status.html` | 파일바 생성일시 1줄씩 | 예 (파일바 생성일시) |
| `assets/xlsx/*.xlsx` 14 | 13종 −1 B(문서 속성 시각) · 투자자산현황 5,727 → 5,603 B(열 5) | 예 (4 + 재저장) |
| `scripts/sync_prototype.py` | +135: 머리 주석 · `NEW_HEAD` 문구 · `investor_share()` · `patch_assets_status_xlsx()` · `transform()` 5b 단계 · `gate()` 잔존 검사 5어(`보관 ㈜` `<th>보관</th>` `a.keeper` `통합 프로토타입` `emptyRow(7,`) · `main()` 엑셀 사본·size 갱신 | **아니오** — `3978be3` 「시연본 변환기」 커밋분. 통합본 산출물에는 닿지 않습니다 (N3) |

지시 1~4·등록부·파일바 밖의 diff 는 `scripts/sync_prototype.py` 1건입니다.

## 결함 재현 절차

FAIL 0건이라 재현 절차는 없습니다. N1 확인 절차만 둡니다.

| 단계 | 조작 | 관찰 |
|---|---|---|
| 1 | `https://payhug-investor-demo.vercel.app/app.html#invest-assets` 열기 | 「투자실행액」 카드 라벨에 점선 밑줄, 호버 시 `Σ A_i …` 툴팁 |
| 2 | `https://payhug-investor-demo.vercel.app/invest-assets.html` 열기 | 같은 카드 라벨이 평문, 호버해도 툴팁 없음 (`.tip-panel` 7개) |

## DOM만 보면 결함이나 실제로는 정상

| 관찰 | 실제 |
|---|---|
| 엑셀 미리보기 시트 3~6행에 F·G 빈 셀(`c-empty`)이 남아 7칸 | `renderXls()` 가 A~G 격자를 고정으로 그리고 2열짜리 「투자수익 현황」 시트도 같은 격자를 씁니다. 데이터·머리는 A~E 5열이고 실물 xlsx 는 `dimension A1:E6` 입니다 |
| `.tip-panel` 8개가 DOM 에 항상 있음 | CSS 로 숨겨 두고 호버에만 보입니다. 직전 판을 CSS 없이 띄우면 `th` innerText 에 툴팁 본문이 섞이는데, 이는 측정 환경(404) 탓이고 배포본은 `assets/base.css` 가 정상 로드됩니다 |
| 「㈜페이허그」 문자열이 `certificate` 1 · `merchants` 9 · `cert-confirm` 모달 1 에 남음 | 증명서 작성자(`app.html:587`·`1005`) · 양수인 「A-001 ㈜페이허그」(`:750`·`MERCHANTS.buyerName`). 「보관 ㈜」 표기가 아니며 직전 판과 같습니다 |
| `app.html` 에 「보관」 1건 잔존(`:1134`) | 「서명값은 계약기록에 보관.」 — 정산채권 양수 완료 문구. 현황 표 「보관」 열과 무관합니다 |
| `#invest-assets/download` 진입만으로 파일이 내려옴 | `syncToast` 의 상태 진입 전달(N2). 버튼 클릭이 이미 내려줬으면 `toastServed` 로 재전달을 막습니다 |
| 「엑셀 다운로드」 클릭 뒤 화면 상태가 `download` 로 안 바뀜 | `download` 상태는 「가맹점별 투자자산」 버튼(`data-xls="assets-merchant"`) 전용입니다(`app.html:3416-3419`). 현황 표 버튼은 토스트만 냅니다 |

## 산출물

| 경로 | 내용 |
|---|---|
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/session_0904/qa/share_app_0909/01_invest-assets_default.png` | `app.html#invest-assets` 1440×1071 (다운로드 토스트 포함) |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/session_0904/qa/share_app_0909/02_invest-sim_result.png` | `app.html#invest-sim/result` 1440×2613 |

## 총평

**PASS 21 · FAIL 0** — 통합본·낱장·엑셀 모두 지시 1~5 대로이고, 지시 밖 diff 는 시연본 변환기 1건(N3), 기존 편차는 낱장 「투자실행액」 카드 툴팁 부재 1건(N1)입니다.
