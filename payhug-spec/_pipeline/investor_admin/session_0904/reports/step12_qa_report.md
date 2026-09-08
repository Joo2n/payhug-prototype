# step12 QA — 투자자 어드민 배포 실물 (2026-09-08)

## 결론

1. 배포 실물 = 로컬. 전체본 `0b6ab0d` · 시연본 `087aa5e` 가 원격 main 과 같고, 배포 HTML 9종(app.html · 낱장 7종 · 시연본 index.html)의 md5 가 로컬 파일과 전부 같습니다.
2. 툴팁 문구 = V1.3 표 4. 낱장 7종 · 전체본 SPA 6상태 · 시연본 4상태에서 실제 마우스 호버로 연 패널 **106개** 전건이 표 4 문구·값 행과 같고, 첨자 `Σ A_i` `PY_a` `PY_t` `Y_r` `A_i` `D_i` 는 전건 `text-transform: none` 이며 캡처 육안으로도 소문자입니다.
3. 옛 문구 0(DOM·가시 텍스트 28화면 × 14낱말) · 값 = 원장 전건(카드 4 · 현황표 · 투자 수익 ④⑤ · 합계 · 툴팁 값 Σ(A_i×D_i) 559,275,516 · PEC 140,000,000 · 주별·월별 재계산까지) · 잘림·겹침·뷰포트 밖 0 · 가로 스크롤 0 · 시연본 「투자 시뮬레이션」 0 · 엑셀 4종 + PDF 실물 도착, 제목행 금칙어 0.
4. 결함 **중 1건**: 가맹점별 엑셀을 내려받은 뒤 「증명서 다운로드」 모달에서 취소 또는 발급을 누르면 `가맹점별투자자산_….xlsx` 가 한 번 더 내려옵니다(재현 2/2, 시연본 동일 코드). 
5. 낮음 6건: 낱장 favicon 404 콘솔 오류 · 「투자실행액」 카드 툴팁이 표 4 빈칸인데 SPA 에만 있고 「투자 실행액」 띄어쓰기 · ④ 값 행 이름 「기간 …」 vs V1.3 「검색대상기간의 …」 · 「연 환산」/「연환산」 혼용 · 낱장 `--empty` 툴팁 0 값 서식이 SPA 와 다름 · 증명서 미리보기 제목 「투자자산 현황」 vs PDF 「투자자산 증명서」.

## 결함 (심각도 순)

| # | 심각도 | 화면 | 요소 | 기준(V1.3/원장) | 실제 | 판정 | 근거(파일:줄) |
|---|---|---|---|---|---|---|---|
| 1 | 중 | 전체본 `app.html#invest-assets` · 시연본 동일 | 「증명서 다운로드」 모달의 취소·발급 | 파일은 누른 버튼의 것만 한 번 내려온다 | 순서 A: 가맹점별 엑셀 클릭(+1) → 증명서 다운로드(0) → **취소(+1)** → 증명서 다운로드(0) → **발급(+1)**. 순서 B(엑셀 없이 증명서만): 0. 순서 C(엑셀 → 다른 메뉴 → 복귀 → 보기 변경): 0. 재다운로드마다 「가맹점별투자자산_2026-08-27_2026-08-27.xlsx 내려받기 완료」 토스트가 다시 뜬다 | 불일치 | `app.html:3435` cert-open → `refresh` → `app.html:2134` `toastServed = null` 로 「이미 내려줬다」 표식이 지워짐 → `app.html:3460-3467` modal-close / `app.html:3436` cert-issue → `refresh` → 상태 `download` 복귀 → `app.html:2128-2131` `syncToast` 가 `pullFile` 재호출. 시연본 `index.html:1906·1909·2652-2653·2668` 동일. 고치는 자리: 2134 의 초기화를 `go()` 의 화면 전환(`fresh`) 때만 하거나, 2131 의 재전달 조건을 딥링크 진입(`PEND`·`SEED`)으로 한정 |
| 2 | 낮 | 낱장 7종 | `<head>` | 콘솔 오류 0 | 첫 낱장 로드에서 `Failed to load resource: 404 /favicon.ico` 1건(같은 세션의 이후 페이지는 캐시로 재발 없음). app.html 은 `data:` 아이콘으로 막혀 있음 | 불일치(낱장↔SPA) | `app.html:10` `<link rel="icon" href="data:,">` · `invest-assets.html` 등 7종 `rel="icon"` 0건 · 실제 프론트는 `payhug-admin-web/app/favicon.ico` 존재 |
| 3 | 낮 | 전체본 SPA · 시연본 「투자 자산」 카드 | 「투자실행액」 카드 툴팁 | 표 4 `Σ Ai │ 투자 자산 · 투자실행액 │ (툴팁 빈칸)` · 표 2 용어 「투자실행액」 | 패널 `Σ A_i · 투자 실행액 · A_i = 순지급액_i × (1 − r) 의 합` + `r │ 계약된 할인율 · 0.11%`. 낱장 `invest-assets.html` 에는 이 툴팁이 없음(카드 4 중 툴팁 1개 vs SPA 2개) | 불일치(표 4 빈칸 · 낱장↔SPA · 띄어쓰기) | `app.html:2173-2177` · 시연본 `index.html:1950` · 낱장 `invest-assets.html:120-135` (툴팁은 133 예상 연환산 수익률만). 산식 자체는 V1.3 표 2 `A = 순지급액 × (1 − r)` 와 같음 → 두면 「투자실행액」으로 붙이고 낱장에도 같은 툴팁을 두거나, 표 4 대로 없애거나 한쪽으로 |
| 4 | 낮 | 투자 수익 ④ 툴팁 (낱장·SPA·시연본·시뮬 결과 전부) | 값 행 이름 | V1.3 표 2: PMR 「검색대상기간의 투자수익율」 · PM 「검색대상기간의 투자수익」 · PA 「검색대상기간의 투자실행금」 · PD 「검색대상기간의 가중평균 금융일수」. 같은 화면 ⑤ 의 PEC 행은 「검색대상기간의 누적 순현금」 으로 표 2 그대로 | `PMR │ 기간 투자수익율 · PM ÷ PA = 0.033992%` · `PM │ 기간 투자수익 · 61,175원` · `PA │ 기간 투자실행금 · 179,970,919원` · `PD │ 기간 가중평균 금융일수 · 3.11일` | 불일치(한 화면 안에서 「기간」·「검색대상기간의」 두 표기) | `app.html:2400-2403` · `app.html:2695-2698`(시뮬) · `invest-profit.html:170`. 값은 원장과 같음 |
| 5 | 낮 | 투자 자산 「예상 연환산 수익률」 카드 툴팁 | 마지막 값 행 이름 | 표 4 「연환산」 | 같은 패널 안에 둘째 줄 「연환산」, 마지막 행 「연 환산 │ 13.21%」 | 불일치(표기 혼용) | `app.html:2188` · `invest-assets.html:133` (`<span>연 환산</span>`) |
| 6 | 낮 | 낱장 `invest-profit--empty.html` | ④⑤ 툴팁 0 값 서식 | SPA 빈 상태(직접입력 2026-09-01~09-07)는 `PMR … = 0.000000%` · `PD … 0.00일` · `PY_a … 0.00%` | 낱장은 `0%` · `0일` · `0%` | 불일치(낱장↔SPA) | `invest-profit--empty.html:176·180` vs `app.html:1714` `fx(v,d)=toFixed(d)` · `app.html:2400·2403` |
| 7 | 낮 | 전체본 `#certificate` · 시연본 동일 | 미리보기 문서 제목 | 모달 「문서명 투자자산 증명서」 · 페이지 제목 「가맹점별 투자자산 증명서」 · 내려받은 PDF 1면 제목 「투자자산 증명서」 | 화면 미리보기 본문 제목은 「투 자 자 산 현 황」 | 불일치(미리보기 ≠ PDF 실물) | 캡처 `demo_app_certificate__page.png` · PDF 텍스트 추출(`pypdf`) 1면 「투자자산 증명서 / 가맹점별 투자자산 · 2026-08-27 마감 기준 …」 |

## 항목별 판정

### 0. 배포 = 로컬

| 대상 | 원격 main | 로컬 HEAD | 배포 md5 = 로컬 md5 |
|---|---|---|---|
| Joo2n/payhug-investor-admin | `0b6ab0d592f7…` | 같음 | app.html · invest-assets · invest-assets--empty · invest-profit · invest-profit--monthly · invest-profit--weekly · invest-profit--empty · invest-sim--result 8/8 같음 |
| Joo2n/payhug-investor-prototype | `087aa5e1309c…` | 같음 | index.html 같음 · `assets/base.css` md5 전체본과 같음(`b50a650f…`) |

### 1. 툴팁 문구 = V1.3 표 4 (실제 호버 · 패널 전문)

측정: `Input.dispatchMouseEvent mouseMoved` 를 앵커 중심에 보낸 뒤 `.tip-panel` 의 `display === 'block'` · `el.matches(':hover')` · 패널 `innerText` 를 읽고 클립 캡처. 실제 프론트의 툴팁도 호버 전용(`payhug-admin-web/app/settlement/overview/PreSettlementTab.tsx:1029-1034` onMouseEnter · `app/sales/[bizNo]/page.tsx:1094` `hidden group-hover:block … w-56`) 이라 호버 전용은 일치.

| 화면 · 앵커 | 패널 전문(호버 실측) | 표 4 | 판정 |
|---|---|---|---|
| 투자 자산 · 현황표 열머리 「가중평균 금융일수」 | `보유 채권 전체` / `채권 건수 │ 61,760건` | `보유 채권 전체` | 일치(괄호 없음) |
| 투자 자산 · 가맹점별 열머리 「가중평균 금융일수」 | 위와 같음 | 같음 | 일치 |
| 투자 자산 · 현황표·가맹점별 열머리 「입금부족률」 | `선정산일이 오늘 기준 20일 전 ~ 11일 전인 표본` / `채권 건수 │ 3,200건` | `선정산일이 오늘 기준 20일 전 ~ 11일 전인 표본` | 일치 |
| 투자 자산 · 카드 「예상 연환산 수익률」 | `Y_r · 예상 연환산 수익률 · r × 365 ÷ D` / `연환산 │ 일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률` / `r │ 계약된 할인율 · 0.11%` / `D │ 가중평균 금융일수 · 3.04일` / `연 환산 │ 13.21%` | `연환산 · 일부 기간의 …` | 일치(+ r·D·값 행은 개선(허용) — 산식 입력값을 그 자리에서 보임 · 「연 환산」 표기는 결함 5) |
| 투자 자산 · 현황표·가맹점별 열머리 「예상 연환산 수익률」 | `Y_r · 예상 연환산 수익률 · r × 365 ÷ D` / `연환산 │ …연간 수익률` | 같음 | 일치 |
| 투자 자산 · 카드 「투자실행액」 (SPA·시연본만) | `Σ A_i · 투자 실행액 · A_i = 순지급액_i × (1 − r) 의 합` / `r │ 계약된 할인율 · 0.11%` | 빈칸 | 결함 3 |
| 투자 수익 · ④ 「투자실행금액 대비」 | `PY_a · 투자실행금액 대비 연환산 수익률 · PMR × 365 ÷ PD` / `연환산 │ …연간 수익률` / `PMR │ 기간 투자수익율 · PM ÷ PA = 0.033992%` / `PM │ 기간 투자수익 · 61,175원` / `PA │ 기간 투자실행금 · 179,970,919원` / `PD │ 기간 가중평균 금융일수 · 3.11일` | `연환산 · 위와 같음. PMR · PM · PA · PD 값` | 일치(값 행 이름은 결함 4) |
| 투자 수익 · ⑤ 「투자 자산 대비」 | `PY_t · 투자 자산 대비 연환산 수익률 · PM × 365 ÷ ( Σ( A_i × D_i ) + PEC )` / `연환산 │ …연간 수익률` / `PY_a │ 투자실행금액 대비 연환산 수익률 · 3.99%` / `Σ( A_i × D_i ) │ 559,275,516원` / `PEC │ 검색대상기간의 누적 순현금 · 140,000,000원` / `EC │ 순현금 · 20,000,000원 × 7일` | `연환산 · 위와 같음. PYa · Σ( Ai × Di ) · PEC · EC 값` · PEC = 검색대상기간의 누적 순현금 | 일치 |
| 투자 수익 · 일별 표 열머리 「투자실행금」 | `PA · 투자실행금 · Σ A_i` / `행 │ 정산예정일이 그 날짜인 보유 채권` | 표 4 PA 툴팁 빈칸 · 지시문 기준 문구 | 일치(지시문) |
| 투자 수익 · 일별 표 열머리 「연환산 수익률」 | `PY_a · 연환산 수익률 · PMR × 365 ÷ PD` / `연환산 │ …연간 수익률` / `행 │ 정산예정일이 그 날짜인 보유 채권` | 지시문 기준 문구 | 일치 |
| 주별(4주 08-03~08-27) ④⑤·열머리 2 | 문구 동일 · 값 `PMR 0.038323%` · `PM 248,681원` · `PA 648,903,503원` · `PD 3.03일` · `PY_a 4.62%` · `Σ(A_i×D_i) 1,965,572,846원` · `PEC 500,000,000원` · `EC 20,000,000원 × 25일` | — | 일치 · 값은 원장 재계산과 같음 |
| 월별 SPA(3개월 06-01~08-27) ④⑤·열머리 2 | 값 `PMR 0.038118%` · `PM 875,417원` · `PA 2,296,624,838원` · `PD 3.03일` · `PY_a 4.59%` · `Σ 6,964,794,977원` · `PEC 1,760,000,000원` · `EC × 88일` | — | 일치 · 원장 재계산과 같음 |
| 월별 낱장(6개월 03-01~08-27) ④⑤·열머리 2 | 값 `PMR 0.038026%` · `PM 1,787,417원` · `PA 4,700,503,303원` · `PY_a 4.57%` · `Σ 14,262,370,838원` · `PEC 3,600,000,000원` · `EC × 180일` | 원장 `fullMR 0.038026` · `fullProfit` · `fullExec` · `fullTy 4.57` · `fullAD` · `fullPsc` | 일치 |
| 빈 상태(낱장·SPA) ④⑤·열머리 2 | 문구 동일 · 값 0 (서식 차이는 결함 6) | — | 일치 |
| 시뮬 결과(낱장·SPA 실행) ④⑤·열머리 2 | 문구 동일 · `PM 16,000원` · `PA 39,956,000원` · `PD 3.04일` · `PY_a 4.81%` · `Σ 121,466,240원` · `PEC 140,000,000원` · `EC × 7일` | — | 일치 |
| 시연본 투자 자산 8 · 투자 수익 일별 4 · 주별 4 · 월별 4 | 전체본 SPA 와 글자 단위로 같음 | — | 일치 |

주별·월별 표의 「행 │ 정산예정일이 그 날짜인 보유 채권」 은 행 단위가 주·월인데 「그 날짜」 로 읽힙니다. 표 4 에 행 툴팁 정의가 없어 판정은 두지 않고 확인 필요로 남깁니다(`app.html:1773·1780` · 시연본 `index.html:1556·1563`).

### 2. 첨자 소문자

| 측정 | 결과 |
|---|---|
| `getComputedStyle(.tip-panel).textTransform` | 106 패널 전건 `none` (`assets/base.css:509` `.tooltip .tip-panel { text-transform: none }` 가 `base.css:247` `th … uppercase` 를 덮음) |
| `getComputedStyle(sub).textTransform` | `sub` 전건 `none` |
| 캡처 육안 | `Y_r` · `PY_a` · `PY_t` · `Σ A_i` · `A_i × D_i` · `순지급액_i` 모두 소문자 아래첨자 (`demo_app_invest-profit__투자_자산_대비_stat_9.png` 등) |
| 대문자 `Σ A_I` `PY_A` `Y_R` | 0건 |

### 3. 옛 문구 0

DOM 텍스트(script·style·noscript·template 제외 TreeWalker) · 가시 텍스트(`body.innerText`) 28 화면·상태 × 14 낱말 = **0건**. 엑셀 4종 전체 셀 · PDF 2면 추출 텍스트에도 0건. 「검색대상기간」 은 V1.3 용어라 대상에 넣지 않았습니다.

### 4. 값 = 원장 `ledger_facts.json`

| 자리 | 화면 실측 | 원장 | 판정 |
|---|---|---|---|
| 카드 투자자산 · 투자실행액 · 순현금 | 100,000,000 · 80,000,000 · 20,000,000 | `total` `exec` `cash` | 일치 |
| 카드·현황표 예상 연환산 · D · 입금부족률 | 13.21% · 3.04일 · 0.07% | `ty` `w` `s` | 일치 |
| 투자 수익 08-21~08-27 ④ · ⑤ | 3.99% · 3.19% | `weekTy` `weekTyAsset` | 일치 |
| 합계 투자실행금 · 투자 수익 · 상환액 · PD | 179,970,919 · 61,175 · 180,032,111 · 3.11 | `weekExec` `weekProfit` `weekRepay` `weekW` | 일치 |
| ⑤ 툴팁 Σ(A_i×D_i) · PEC · PMR | 559,275,516 · 140,000,000 · 0.033992% | `weekAD` `weekPsc` `weekMR` | 일치 |
| 주별 4주 · 월별 3개월 · 월별 6개월 | 위 표 1 | `adByDate` `tyByDate` `monthExec` `monthAD` `full*` 합산 재계산 | 일치 |
| 엑셀 4종 셀 값 | 합계 80,000,000 / 179,970,919 / 61,175 / 0.0399·0.0319 | 위와 같음 | 일치 |

### 5. 잘림·겹침·콘솔·가로 스크롤·시연본 시뮬

| 검사 | 결과 |
|---|---|
| 툴팁 패널 뷰포트 밖 · overflow 조상에 잘림 · 다른 요소에 덮임(`elementFromPoint` 5점) | 106 패널 0건 |
| `documentElement.scrollWidth > clientWidth` · overflow-x auto/scroll 내부 요소 | 28 화면 0건 (뷰포트 1440×1000 · DPR 2 · `Emulation.setDeviceMetricsOverride` 로 고정) |
| 콘솔 error/warning · 예외 | favicon 404 1건(결함 2) 외 0건 |
| 시연본 「투자 시뮬레이션」 | DOM 텍스트 · 가시 텍스트 · `section[data-screen=invest-sim]` · 사이드바 전부 0. 사이드바 7 메뉴 실제 클릭 전건 도달(투자 자산 · 투자 수익 · 가맹점 · 정산채권 양수 · 계약기록 · 쿠콘 관리 현금 = we-bank 새 탭 열림 확인 · 비밀번호 변경) |

### 6. 다운로드 실물

`Browser.setDownloadBehavior allow` + `downloadWillBegin/Progress` 이벤트로 도착을 확인하고 파일을 열어 읽었습니다.

| 파일 | 전체본 | 시연본 | 바이트 | 제목행 | 금칙어 |
|---|---|---|---|---|---|
| 투자자산현황_2026-08-27_2026-08-27.xlsx | 도착 | 도착 | 5,727 | 「투자자산 현황 — 2026-08-27 / ㈜테스트인베스트」 | 0 |
| 가맹점별투자자산_2026-08-27_2026-08-27.xlsx | 도착 | 도착 | 6,109 | 「가맹점별 투자자산 — 2026-08-27 / ㈜테스트인베스트」 | 0 |
| 투자수익현황_2026-08-21_2026-08-27.xlsx | 도착 | 도착 | 5,466 | 「투자수익 현황 — 2026-08-27 / ㈜테스트인베스트」 · 항목 「검색대상기간」 | 0 |
| 일별투자수익_2026-08-21_2026-08-27.xlsx | 도착 | 도착 | 5,873 | 「일별 투자수익 — 2026-08-21 ~ 2026-08-27 / ㈜테스트인베스트」 | 0 |
| 투자자산증명서_20260827.pdf | 도착 | 도착 | 245,291 · `%PDF-1.4` · 2면 | 「투자자산 증명서」 | 0 |

토스트는 전건 파일명 + 「내려받기 완료」 로 떴습니다. 빈 상태(직접입력 기간)에서는 투자 수익 엑셀 2 버튼이 `disabled` 로 잠겨 눌리지 않았습니다.

## DOM 만 보면 결함이나 실제로는 정상

| 화면 · 요소 | DOM 상태 | 실제 | 판정 근거 |
|---|---|---|---|
| SPA·시연본 투자 자산·투자 수익 툴팁 | 정적 HTML 에 `.tip-panel` 0건 (`grep` 무응답) | JS 렌더(`app.html:1745-1782` `popTh`·`yrTh`·`tyTh`·`thirdTh`, `2169-2190` 카드, `2388-2412` ④⑤, `2690-2707` 시뮬)라 호버 시 106 패널 전건 열림 | 실제 호버 실측 |
| 툴팁 첫 줄 `Y<sub>r</sub>` 이 `th … text-transform: uppercase` 안에 있음 | 부모 규칙만 보면 대문자 | `.tooltip .tip-panel { text-transform: none }` (`base.css:509`) 가 덮어 소문자 | `getComputedStyle` 전건 `none` + 캡처 |
| 시연본 사이드바 `.nav-item.active` 0건 | 활성 클래스 없음 | `body[data-active]` 로 칠함 — 클릭한 메뉴 배경 `rgb(127,225,65)` 전건 | 클릭 후 계산된 배경색 |
| 시연본 「쿠콘 관리 현금」 클릭 뒤 hash 가 이전 화면(#contracts) 그대로 | 전환 실패로 보임 | `target=_blank` 외부 링크 — we-bank 새 탭이 열림(`Target.getTargets` 로 확인) | 실제 클릭 |
| 계약기록 「선택 문서 다운로드 (3)」 · 행 「문서 다운로드」 가 3건 선택 상태에서도 `disabled` | 죽은 버튼 | D-39 로 일부러 잠금(전자서명 결과 파일 형식 미결) — `app.html:3016`, `README.md:110`, `request_register.md:314`. 시연본 README 의 「재양도합의서 묶음은 실물 파일이 그대로 내려온다」 문장은 이와 어긋남(확인 필요) | 문서 근거 |
| 투자 수익 빈 상태에서 엑셀 버튼 2개 `disabled` | 눌리지 않음 | 실물 없는 기간을 말하지 않는 규칙(D-39 · `app.html:1609` `xlsKey` null) | 의도 |
| 낱장 월별이 6개월(03-01~), SPA 월별 토글이 3개월(06-01~) | 값이 다름 | 프리셋이 다를 뿐 각각 원장과 같음(`fullTy 4.57` · 재계산 4.59) | 원장 재계산 |
| 낱장 첫 페이지 콘솔 404 가 두 번째 페이지부터 안 보임 | 간헐 오류처럼 보임 | 크롬이 favicon 404 를 세션에 캐시 — 낱장 7종 전부 `rel="icon"` 이 없어 새 세션 첫 로드마다 남 | 결함 2 로 올림 |
| `Page.captureScreenshot` clip 을 뷰포트 좌표로 주면 스크롤한 툴팁 캡처가 어긋남(1차 실행) | 패널이 잘린 듯 보임 | clip 은 문서 좌표 — `scrollX/Y` 를 더해 재캡처하니 전건 온전 | 판독기 오류 |

## 근거 판본과 작업 중 감지한 로컬 변경

- 모든 `파일:줄` 은 배포본과 같은 커밋 `0b6ab0d`(`git show 0b6ab0d:app.html`) · 시연본 `087aa5e` 기준입니다. 보고 시점에 배포 app.html md5 = HEAD md5(`103368a0…`) 를 다시 확인했습니다.
- 이 QA 가 도는 동안 로컬 `/Users/semi/cursor/payhug-investor-admin` 의 `app.html` 과 낱장 9종(`invest-assets*.html` · `invest-profit*.html` · `invest-sim--result.html`)에 **미커밋 수정**이 생겼습니다(이 QA 는 파일을 고치지 않았고, 쓰기는 scratchpad 안에서만 했습니다). 예: `yrTh()` → `yrTh(w)`, 열머리 툴팁 행 이름 `행` → `i`. 수정본은 배포되지 않았으므로 판정 대상이 아니며, 다음 배포 뒤 같은 검사를 다시 돌려야 합니다. `assets/base.css` · `README.md` · 시연본 `index.html` 은 HEAD 와 같습니다.

## 방법

- 헤드리스 크롬 `--headless=new` + CDP(수제 WebSocket) · `--window-size=1440,1087` 뒤 `Emulation.setDeviceMetricsOverride` 1440×1000 DPR 2 (`innerWidth/innerHeight` 1440×1000 확인).
- 호버·클릭은 `Input.dispatchMouseEvent`(mouseMoved · mousePressed/Released). 사이드바·토글·엑셀·증명서·발급·취소 전부 실제 좌표 클릭. 시뮬 실행 버튼도 실제 클릭.
- SPA 빈 상태만 `input[type=date]` 값을 JS 로 넣고 `change` 를 쏜 뒤 「검색」 은 실제 클릭.
- 다운로드는 `Browser.setDownloadBehavior allow`. xlsx 는 `openpyxl` 로, PDF 는 `pypdf` 로 열어 읽음.
- 스크립트 `scratchpad/qa_live.js` · 결과 `scratchpad/step12_result.json` · 화면별 가시 텍스트 `scratchpad/step12_txt/*.txt` · 내려받은 실물 `scratchpad/step12_dl/`.

## 캡처

`/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/step12_qa_live/` 113장. 이름 규칙 `<화면>__<앵커>_<자리 card|th|stat>_<번호>.png`(툴팁 1장씩 78장) · `<화면>__page.png`(화면 28장) · 흐름 7장.

| 화면 키 | 뜻 |
|---|---|
| `demo_invest-assets` `demo_invest-assets--empty` `demo_invest-profit` `demo_invest-profit--weekly` `demo_invest-profit--monthly` `demo_invest-profit--empty` `demo_invest-sim--result` | 전체본 낱장 7 |
| `demo_app_invest-assets` `demo_app_certificate` `demo_app_invest-profit` `demo_app_invest-profit--weekly` `--monthly` `--empty` `demo_app_invest-sim` `demo_app_invest-sim--result` | 전체본 app.html 흐름 |
| `demo_app_invest-assets__after_xls_status` `__after_xls_merchant` `__cert_modal` · `demo_app_certificate__after_pdf` · `demo_app_invest-profit__after_xls` | 다운로드·토스트 순간 |
| `proto_home` `proto_invest-assets` `proto_invest-returns` `proto_invest-returns--weekly` `--monthly` `proto_merchants` `proto_receivables` `proto_contracts` `proto_kcoon` `proto_password` `proto_downloads__cert_confirm` | 시연본 7 메뉴 + 흐름 |
