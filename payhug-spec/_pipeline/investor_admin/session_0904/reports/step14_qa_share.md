# step14 — 시연본(payhug-investor-prototype) 투자자 공유 정리 QA

검사일 2026-09-09 · 대상 https://payhug-investor-prototype.vercel.app/ (Joo2n/payhug-investor-prototype HEAD `7a369bd`) · 비교 기준 직전 배포 판 `19c1440`.

## 하지 않은 것 · 확인 못 한 것

| # | 항목 | 상태 | 사유 |
|---|---|---|---|
| 1 | 엑셀 13종(투자자산 현황 제외) 전부를 배포 URL 에서 실제 클릭으로 내려받기 | 4종만 실클릭(가맹점별 · 투자수익현황 일주일 · 일별투자수익 일주일 · 증명서 PDF). 나머지 9종은 `git diff --stat 19c1440 HEAD -- assets` 로 바이트 무변경만 확인 | 화면에서 닿는 조합이 기간 상태에 묶여 있어 9종은 로컬 레포 대조로 갈음 |
| 2 | 실제 페이허그 프론트(payhug-admin-web) 와의 대조 | 하지 않음 | 이번 라운드 범위는 시연본 변경 4건의 회귀 확인 |
| 3 | 키보드(Tab · Space · Enter) 조작 | 하지 않음 | 변경 4건이 키보드 경로를 건드리지 않음 |
| 4 | 사이드바 「쿠콘 관리 현금」 외부 링크(We-bank) 실클릭 | 하지 않음(href · target=_blank 속성만 확인) | 외부 사이트 |
| 5 | 로그인 화면 「로그인」 버튼 클릭 | 하지 않음(딥링크 `#login` 표시만 확인) | 범위 외 |
| 6 | Vercel 리전별 CDN 캐시 | `icn1` 응답만 확인(`x-vercel-cache: HIT`, `last-modified 2026-09-09 04:46 GMT`, sha256 일치) | 다른 리전은 확인 수단 없음 |

## 대상 · 환경

| 항목 | 값 |
|---|---|
| 로컬 index.html sha256 | `049245d42e95f40b02e753107278171edabe4f93b5d2328ccf0dff7e758a5906` |
| 배포 URL sha256 (`curl -fsSL … \| shasum -a 256`) | `049245d42e95f40b02e753107278171edabe4f93b5d2328ccf0dff7e758a5906` (일치) |
| 브라우저 | Google Chrome 152.0.7977.83 `--headless=new --remote-debugging-port=58373 --window-size=1440,1000` (전용 user-data-dir) |
| 실측 뷰포트 | 1440 × 913 (`--window-size` 1000 − 87), dpr 1 |
| 조작 방식 | CDP `Input.dispatchMouseEvent`(사이드바 · 다운로드 버튼 · 툴팁 호버), `Browser.setDownloadBehavior allow` 로 실물 수신, 상태는 `#<화면>/<상태>` 딥링크 |
| 직전 판 비교 | `19c1440` 의 index.html + assets 를 `python3 -m http.server` 로 서빙해 같은 항목 실측 |
| 콘솔 오류 · 네트워크 실패(배포 페이지) | 0건 (`Runtime.exceptionThrown` · `consoleAPICalled error/warning` · `Network.loadingFailed` · HTTP ≥ 400) |

## 판정표

| # | 항목 | 기대 | 실측 | 판정 |
|---|---|---|---|---|
| 1 | A. index.html diff 범위 (`19c1440` → 로컬) | 1~4 + 머리 주석 + XLSX 레지스터 `size` 뿐 | 6 hunk · +10/−11 줄. 아래 「diff 요약」 전건이 그 범위 안. 그 밖의 diff 0 | PASS |
| 2 | A. 레포 내 index.html 밖 변경 | 투자자산 현황 xlsx 1건 | `README.md`(+7줄, 갱신 표) · `assets/xlsx/투자자산현황_….xlsx`(5727 → 5658 B) 2건. 다른 xlsx 12종 · PDF · txt · css 무변경 | PASS |
| 3 | B. 배포본 = 로컬 | sha256 일치 | 일치 | PASS |
| 4 | B. `document.title` | 「PayHug 투자자 어드민」 | 「PayHug 투자자 어드민」(26개 화면·상태 전부). 직전 판 「PayHug Admin — 통합 프로토타입」 | PASS |
| 5 | B. 투자 자산 `.summary-card .summary-sub` | 2건: 「투자실행액 + 순현금」 「가중평균 금융일수 3.04일 기준」 | 정확히 그 2건. 직전 판은 4건(「비중 80.0% · 보관 ㈜페이허그」 「비중 20.0% · 보관 ㈜쿠콘」 포함) | PASS |
| 6 | B. 현황 표 `[data-mount="ia-status"] thead th` | 5열: 자산 구분 · 금액 (원) · 가중평균 금융일수 · 입금부족률 · 예상 연환산 수익률 | 5열 동일. 직전 판 7열(+비중 · 보관) | PASS |
| 7 | B. 현황 표 tbody 행 | 투자실행액 80,000,000 · 3.04일 · 0.07% · 13.21% / 순현금 20,000,000 · - · - · - / 합계 (투자자산) 100,000,000 · - · - · - | 동일(3행 · 각 5셀, 합계 행 `total-row`) | PASS |
| 8 | B. 빈 상태 `#invest-assets/empty` | 열 5 · 빈 행 colspan 5 · 「조회 결과가 없습니다.」 | thead 5열, tbody 1행 1셀 `colspan="5"` 「조회 결과가 없습니다.」. 배지 「데이터 없음」, 카드 0원 · 0.00% · 「가중평균 금융일수 집계 대상 없음」, 버튼 3개(엑셀 ×2 · 증명서) 전부 disabled | PASS |
| 9 | B. 가맹점별 표 `[data-mount="ia-merch"] thead th` | 「비중」 열 그대로 | 6열(가맹점 · 투자실행액 (원) · 가중평균 금융일수 · 입금부족률 · 예상 연환산 수익률 · 비중). 8행 값 직전 판과 완전 동일 | PASS |
| 10 | B. 투자 자산 툴팁 `.tip-panel` 문구 | 직전 판과 동일 | 8곳(카드 2 · 현황 표 열머리 3 · 가맹점별 표 열머리 3) 앵커·패널 텍스트 직전 판과 전부 동일. 투자실행액 카드 = `Σ Ai / Ai 순지급액i × (1 − r) / r 0.11%` | PASS |
| 11 | B. 툴팁이 실제로 뜨는가 | 호버 시 표시 | 투자실행액 카드 앵커 위로 마우스 이동 → `.tip-panel` display block · 256 × 86 px. 마우스 이탈 → display none | PASS |
| 12 | B. 투자 수익 툴팁 4곳 | 직전 판과 동일 | 투자실행금액 대비 · 투자 자산 대비 · 투자실행금 열머리 · 연환산 수익률 열머리 — 앵커·패널 텍스트 직전 판과 동일 | PASS |
| 13 | B. 사이드바 메뉴 | 7개 · 라벨 변경 0 | 투자 자산 · 투자 수익 · 가맹점 · 정산채권 양수 · 계약기록 · 쿠콘 관리 현금(외부, `target=_blank`) · 비밀번호 변경. 직전 판과 동일 | PASS |
| 14 | B. 전 화면 금칙어 | 「보관 ㈜」「통합 프로토타입」「미확정」「대상정산금채권」「시뮬레이션」 0건 | `SCREEN_ORDER` 9화면 × 상태 = 26개 상태 전부 `document.body.innerText` 에서 5종 모두 0건 | PASS |
| 15 | B. 딥링크 도달 | 26개 상태 전부 해당 화면·상태로 | 26/26 `body.dataset.view` · `section.dataset.state` 일치. 모달 상태(cert-confirm · doc · confirm · signing · done) 모달 표시 확인 | PASS |
| 16 | B. 전 화면 innerText 직전 판 대조 | 투자 자산 화면 외 변화 0 | 26개 중 22개 바이트 동일. 차이 4개(invest-assets default · download · cert-confirm · empty)는 삭제된 「비중 … · 보관 ㈜…」 2줄과 표 「비중」「보관」 열뿐 | PASS |
| 17 | C. 「엑셀 다운로드」(현황) 실클릭 | 실물 xlsx · 머리 5열 · ㈜ 0 · 5658 B | `Browser.downloadWillBegin` → `completed`. 파일 `투자자산현황_2026-08-27_2026-08-27.xlsx` 5658 B, sha256 = 로컬 assets. 머리 행 A3~E3 = 자산 구분 · 금액 (원) · 가중평균 금융일수 · 입금부족률 · 예상 연환산 수익률. 전 파트 문자열에서 ㈜페이허그 0 · ㈜쿠콘 0 · 비중 0 · 보관 0(㈜ 는 A1 제목의 ㈜테스트인베스트 1건만). 토스트 「투자자산현황_….xlsx 내려받기 완료」 | PASS |
| 18 | C. 「엑셀 다운로드」(가맹점별) 실클릭 | 직전 판과 바이트 동일 | 6109 B, sha256 `cfc8a8ee…` = 로컬 = `git show 19c1440:…`. 클릭 후 해시 `#invest-assets/download`, 버튼 「다운로드 완료」(`is-done`), 배지 「엑셀 다운로드 완료」, 토스트 3.5초 뒤 hidden | PASS |
| 19 | C. 다른 다운로드 동작 | 실물 수신 | 투자수익현황(5466 B) · 일별투자수익(5873 B) · 증명서 PDF(245,291 B) 실클릭 수신, 셋 다 sha256 = 로컬 = `19c1440` | PASS |
| 20 | C. 엑셀 13종 무변경 | 바이트 동일 | `git diff --stat 19c1440 HEAD -- assets` 결과 투자자산 현황 1건만. 가맹점별 xlsx 「비중」 열(F3) 유지 | PASS |
| 21 | D. 스크린샷 3장 1440 폭 | 저장 | `01_invest-assets_default.png` 1440×1071 · `02_invest-assets_empty.png` 1440×913 · `03_invest-profit_default.png` 1440×1037 | PASS |

## diff 요약 — `git show 19c1440:index.html` → 로컬 `index.html` (바뀐 줄 전부)

| hunk | 로컬 줄 | 직전 판 | 로컬 | 대응 |
|---|---|---|---|---|
| 1 | 6 | `<title>PayHug Admin — 통합 프로토타입</title>` | `<title>PayHug 투자자 어드민</title>` | 변경 1 |
| 2 | 378 | 주석 「시연 전용 배포본 — 통합 프로토타입 한 파일뿐이다.」 | 「시연 전용 배포본 — 한 파일뿐이다.」 | 머리 주석 |
| 2 | 382 | (없음) | 주석 「투자자 공유 정리 — 탭 제목 · 투자 자산 카드 아래 비중·보관 줄 · 현황 표 비중·보관 열 · 같은 엑셀 두 열은 이 배포본에 없다.」 | 머리 주석 |
| 3 | 1392 | `'assets-status': {… size:'5.6 KB' …}` | `size:'5.5 KB'` | XLSX 레지스터(화면 미노출 — `.size` `.made` 참조 0건) |
| 4 | 1959~1963 | 투자실행액 카드 `'<div class="summary-sub">비중 ' + fx(rExec, 1) + '% · 보관 ㈜페이허그</div></div>'` / 순현금 카드 `… fx(rCash, 1) … ㈜쿠콘 …` | 두 곳 모두 `'</div>' +` | 변경 2 |
| 5 | 1971~1972 | `'<th class="num">비중</th><th>보관</th></tr></thead><tbody>'` / `emptyRow(7, …)` | `'</tr></thead><tbody>'` / `emptyRow(5, …)` | 변경 3 (열머리 · 빈 행) |
| 6 | 1981~1985 | 행 `'<td class="num">' + fx(aRatio[i], 1) + '%</td><td>' + a.keeper + '</td></tr>'` / 합계 행 `… <td class="num">100.0%</td><td><span class="none">-</span></td></tr>'` | `'</tr>'` / `'<td class="num"><span class="none">-</span></td></tr>'` | 변경 3 (행 · 합계 행) |

그 밖의 diff 0. README.md 는 「갱신」 표 1행과 상단 설명 1줄이 늘었고, `assets/xlsx/투자자산현황_2026-08-27_2026-08-27.xlsx` 는 `sheet1.xml` 2871 → 2459 B(F·G 열 삭제, `dimension A1:G6 → A1:E6`, 제목 병합 `A1:E1`), `core.xml` modified `2026-09-09T04:44:26Z`. 나머지 파트 동일.

## 관찰 — 결함 아님, 잔존 기록

| # | 위치 | 내용 | 영향 | 구분 |
|---|---|---|---|---|
| O1 | xlsx `xl/worksheets/sheet1.xml` `<cols>` | 열 너비 정의가 7개(min 1~7) 그대로. openpyxl `delete_cols` 가 `column_dimensions` 를 옮기지 않음(`sync_prototype.py:323`) | 내용 없는 F·G 열의 너비만 지정. 표시 내용 · 머리 · 값 무관 | 확정 |
| O2 | `index.html:984-985`, `1945-1947` | 데이터 `keeper:'㈜페이허그'` `keeper:'㈜쿠콘'` 와 `aRatio · rExec · rCash` 계산이 남아 있음 | 화면 미노출(26 상태 innerText 0건). view-source 에만 보임 | 확정 |
| O3 | 가맹점(9) · 증명서(1) · 증명서 발급 확인 모달(1) | 「㈜페이허그」 표시 | 채권매입업체 ID 「A-001 ㈜페이허그」 · 증명서 발급자. 직전 판과 innerText 동일. 이번 정리 대상(「보관 ㈜」)이 아님 | 확정 |
| O4 | XLSX 레지스터 `made:'2026-09-07 13:35'` | 파일 `core.xml` modified 는 09-09 | 시연본에서 `.made` 를 읽는 코드 0건 → 노출 없음 | 확정 |

## DOM만 보면 결함이나 실제로는 정상

| # | DOM 에서 보이는 것 | 실제 |
|---|---|---|
| 1 | 카드 라벨 `textContent` 가 「투자실행액Σ AiAi순지급액i × (1 − r)r0.11%」 처럼 툴팁 문구와 붙어 나옴 | `.tip-panel` 은 display none 이고 호버 때만 block(판정표 11 실측). 화면엔 「투자실행액」만 보임(스크린샷 01) |
| 2 | 투자 자산 화면 `.tooltip` 이 요청서의 4곳이 아니라 8곳 | 현황 표 열머리 3 + 가맹점별 표 열머리 3 + 카드 2. 같은 `popTh` `yrTh` 로 두 표에 붙는 구조(`index.html:1529-1545`). 직전 판도 8곳 · 문구 동일 |
| 3 | 빈 상태(`#invest-assets/empty`) innerText 끝에 「가맹점별투자자산_….xlsx 내려받기 완료」 토스트 | 스캔이 `download` 상태를 거친 지 3초 안에 같은 화면의 `empty` 로 옮긴 잔상. 화면이 바뀔 때만 토스트를 내리고(`go()` `if(fresh) hideToast()`), 같은 화면 안 전환은 3,000 ms 자동 소멸(원본 Toast.tsx:18 규격). 실측 3.5초 뒤 `hidden=true`. 사용자 동선(빈 상태는 씨앗 상태)에서 재현되지 않음 |
| 4 | 현황 표 열머리 「가중평균 금융일수」「입금부족률」「예상 연환산 수익률」 밑줄 | 툴팁 앵커 스타일(`.tip-anchor`). 정렬 버튼이 아님. 직전 판과 동일 |
| 5 | 직전 판을 `file://` 로 열면 `#invest-assets/download` 부터 페이지가 「ERR_FILE_NOT_FOUND」로 바뀜 | `download` 상태가 `<a download>` 를 클릭하는데 `file://` 에 assets 가 없어 크롬이 다운로드 대신 오류 페이지로 이동. `http.server` 로 assets 와 함께 서빙하면 26 상태 전부 정상. 판독 환경 함정이며 배포본 문제 아님 |
| 6 | `curl -sI` 응답 `x-vercel-cache: HIT` | 캐시 응답이지만 본문 sha256 이 로컬 HEAD 와 일치(판정표 3). 구 캐시 아님 |

## 산출 파일

| 파일 | 내용 |
|---|---|
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/session_0904/qa/share_0909/01_invest-assets_default.png` | 투자 자산 기본, 1440×1071 |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/session_0904/qa/share_0909/02_invest-assets_empty.png` | 투자 자산 빈 상태, 1440×913 |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/session_0904/qa/share_0909/03_invest-profit_default.png` | 투자 수익 기본, 1440×1037 |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/session_0904/reports/step14_qa_share.md` | 이 보고서 |

총평: PASS 21 · FAIL 0 — 시연본 변경은 지시한 4건(+주석 · 레지스터 size)에 한정되고, 배포본은 로컬과 동일하며 다운로드 실물과 나머지 화면은 직전 판과 같습니다.
