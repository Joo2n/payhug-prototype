# 요율 정정 적용 · 가맹점 로스터 16건 통일 — 적용 결과

대상 저장소: `/Users/semi/cursor/payhug-investor-admin`. 작업 트리 수정까지이며 커밋·push 없음.
근거: `rate_fix_map.json`(정정값 117건) · `rate_recalc.md`(재계산 근거) · 로스터 16건 결정(사용자 지시 2단계).

요율 `0.11%`는 C1 미확정 상태 그대로다. 화면의 `예시` 표기는 손대지 않았다. 아래에서 "맞는다"는 **한 표·한 화면 안에서 산식이 아귀가 맞는다**는 뜻이며 정책값 확정이 아니다.

---

## §1 맵 유효성 재확인

`rate_fix_verify.py` 드라이런(원본 미변경, 메모리 치환 후 재검산) 결과.

| 항목 | 결과 |
|---|---|
| 치환 대상 | 86건 (`text` 84 · `formula` 2) / 파일 11개 |
| locator 오류 | **0** |
| 항등식 재검산 오류 | **0** |
| 구값 잔존 | **0** |

| 파일 | 행 | 합계 상환 | 합계 실행 | 합계 수익 | W | Ty(가중) |
|---|---|---|---|---|---|---|
| `invest-profit.html` | 7 | 1,252,175,880 | 1,250,800,000 | 1,375,880 | 11.3 | 3.55% |
| `invest-profit--datepicker.html` | 7 | 1,252,175,880 | 1,250,800,000 | 1,375,880 | 11.3 | 3.55% |
| `invest-profit--monthly.html` | 6 | 32,132,807,250 | 32,097,500,000 | 35,307,250 | 11.3 | 3.54% |

선행 라운드의 결함 수정 14건(H-1·H-2·M급 4건, `index.html` 재작성, `app.html` 신규)이 맵의 locator를 깨뜨리지 않았다. **맵 재생성 불필요** — `rate_fix_map_gen.py`는 실행하지 않았다.

### 비고 — 동시 쓰기 관측

적용 도중 `17:35:00`에 다른 프로세스가 저장소 파일 19개(`acquisition*` · `coocon*` · `contracts*` · `merchants*` · `login` · `password*`)를 일괄 재기록했다. 죽은 링크를 `link-off` 스팬으로 바꾸는 성격의 변경이며, 본 라운드가 만진 숫자·건수·페이지네이션과 겹치지 않는다. 적용 후 §5 대조를 다시 돌려 충돌 0건을 확인했다. `app.html`은 `build_app.py`가 `login.html`에서 로그인 카드를 그대로 실어오는 구조라 재생성분에 그 변경이 함께 들어가 있다.

---

## §2 적용 내역 — 맵 117건의 처리 구분

| 파일 | 맵 건수 | 종류 | 처리 |
|---|---|---|---|
| `invest-profit.html` | 12 | text | 맵 적용. `Ty(투자자산 대비)` 1건은 자산 기준 변경으로 `3.29% → 3.32%` 대체 |
| `invest-profit--datepicker.html` | 12 | text | 동일 (대체 1건) |
| `invest-profit--monthly.html` | 11 | text | 맵 적용. `Ty(투자자산 대비)` `3.23% → 3.26%` 대체 |
| `xls-profit-daily.html` | 9 | text | 맵 적용 |
| `xls-profit-status.html` | 4 | text | 맵 적용. `Ty(투자자산 대비)` `3.29% → 3.32%` 대체 |
| `invest-assets.html` | 4 | text | 로스터 재산출로 흡수 (§3) |
| `invest-assets--page2.html` | 9 | text | 로스터 재산출로 흡수. 맵의 Ty 5건 값은 재산출 결과와 동일 |
| `invest-assets--download.html` | 4 | text | 로스터 재산출로 흡수 |
| `invest-assets--cert-confirm.html` | 4 | text | 로스터 재산출로 흡수 |
| `xls-assets-status.html` | 1 | text | 로스터 재산출로 흡수 |
| `assets/xlsx/일별_투자수익_20260827.xlsx` | 25 | cell | openpyxl로 셀 기입 |
| `assets/xlsx/투자수익_현황_20260827.xlsx` | 4 | cell | 기입. `B8`은 `0.0332`로 대체 |
| `assets/xlsx/투자자산_현황_20260827.xlsx` | 2 | cell | 기입 후 로스터 값으로 재기입 (`C4 11.3` 유지 · `E4 3.57%`) |
| `app.html` | 14 + 2 | text·formula | 직접 편집하지 않고 `build_app.py`의 데이터셋·산식을 고쳐 재생성 |
| **합** | **117** | | |

### 자산 기준 변경에 따른 대체값 4건

`Ty(투자자산 대비) = Ty(가중) × 투자실행액 ÷ 투자자산`의 두 인자가 로스터 16건으로 바뀌면서 맵의 산출값이 낡았다.

| 위치 | 맵 값 (8건 기준) | 적용값 (16건 기준) | 산출 |
|---|---|---|---|
| 주간 카드 (`invest-profit` · `--datepicker` · `xls-profit-status` · `투자수익_현황.xlsx`) | 3.29% | **3.32%** | `3.554328 × 1,523,100,000 ÷ 1,628,400,000 = 3.32446` |
| 월별 카드 (`invest-profit--monthly`) | 3.23% | **3.26%** | `3.49 × 1,523,100,000 ÷ 1,628,400,000 = 3.26432` |

### `app.html` 산식 결함 2건

| 위치 | 현행 | 교체 |
|---|---|---|
| `RENDER['invest-profit']` | `tyExec * exec / assetTotal()` | `tyExec * ASSET_ROWS[0].amount / assetTotal()` |
| `sheetData('profit-status')` | `tyE * pexec / total` | `tyE * ASSET_ROWS[0].amount / total` |

분자가 조회 기간 실행금이라 기간 길이에 따라 값이 요동하던 것(주간 3.20% · 월별 12.83%)을 투자실행액 고정으로 바꿨다. 기간 독립성은 §4에서 값으로 확인한다.

---

## §3 로스터 16건 통일

`invest-assets.html` 1페이지 8행 + `invest-assets--page2.html` 2페이지 8행을 한 로스터로 합치고 페이지 크기를 8로 잡았다. 정적 2페이지의 8행이 어느 합계에도 잡히지 않아 비중 합이 118.6%였던 상태가 해소된다.

### 3.1 기준 수치

| 항목 | 종전 (8건) | 통일 후 (16건) |
|---|---|---|
| 투자실행액 | 1,284,500,000 | **1,523,100,000** |
| 순현금 | 105,300,000 | 105,300,000 (불변) |
| 투자자산 | 1,389,800,000 | **1,628,400,000** |
| 투자실행액 비중 | 92.4% | **93.5%** |
| 순현금 비중 | 7.6% | **6.5%** |
| 투자실행액 행 W금융일수 | 11.2 | **11.3** (가중 raw 11.2787) |
| 투자실행액 행 S입금부족율 | 0.42% | 0.42% (가중 raw 0.4220, 불변) |
| 투자실행액 행 Ty수익율 | 3.59% | **3.57%** (가중 raw 3.573231) |

`투자실행액` 행의 W·S·Ty는 투자금액 가중평균이며, 근거는 종전 8건에서 S가 이미 가중평균값과 일치했다는 점이다(`rate_recalc.md` §3.5).

### 3.2 16행 검산

| # | 가맹점 | 투자금액 | W | S | Ty | 비중 |
|---|---|---|---|---|---|---|
| 1 | 김성호떡볶이 본점 | 312,400,000 | 10.8 | 0.31% | 3.72% | **20.4%** |
| 2 | 달빛곱창 홍대점 | 268,900,000 | 11.5 | 0.55% | 3.49% | 17.7% |
| 3 | 성호분식 2호점 | 197,300,000 | 12.1 | 0.28% | 3.32% | 13.0% |
| 4 | 바다마루 횟집 | 152,600,000 | 10.2 | 0.47% | 3.94% | 10.0% |
| 5 | 한강커피 잠원점 | 121,800,000 | 11.9 | 0.62% | 3.37% | 8.0% |
| 6 | 김밥나라 | 98,200,000 | 10.5 | 0.19% | 3.82% | 6.4% |
| 7 | 초록치킨 서초점 | 76,100,000 | 12.4 | 0.71% | 3.24% | 5.0% |
| 8 | 골목냉면 | 57,200,000 | 11.0 | 0.38% | 3.65% | 3.8% |
| 9 | 청춘포차 신촌점 | 48,900,000 | 11.3 | 0.44% | 3.55% | 3.2% |
| 10 | 왕십리곱창타운 | 42,300,000 | 10.6 | 0.26% | 3.79% | 2.8% |
| 11 | 소소한밥상 | 37,600,000 | 12.2 | 0.58% | 3.29% | 2.5% |
| 12 | 대박국수 사당점 | 31,400,000 | 11.7 | 0.33% | 3.43% | 2.1% |
| 13 | 정든수산 | 26,800,000 | 10.9 | 0.51% | 3.68% | 1.8% |
| 14 | 착한고기 은평점 | 21,500,000 | 12.6 | 0.67% | 3.19% | 1.4% |
| 15 | 커피한잔 마포점 | 17,200,000 | 11.1 | 0.22% | 3.62% | 1.1% |
| 16 | 우리동네반찬 | 12,900,000 | 10.4 | 0.35% | 3.86% | 0.8% |
| | **합계** | **1,523,100,000** | 11.3 | 0.42% | 3.57% | **100.0%** |

- `Ty = 0.11% × (365 ÷ W)`, 소수 2자리 반올림. 16행 전건 일치
- 금액 합 = 투자실행액 = 현황표 `투자실행액` 행 = 요약 카드
- **반올림 잔차 처리** — 각 행을 소수 1자리로 반올림하면 합이 `100.1%`가 된다. 잔차 `-0.1%p`를 최대 금액 행(1번 김성호떡볶이 본점)에 흡수해 `20.5% → 20.4%`로 적고, 합을 정확히 `100.0%`로 닫았다. 통합본도 같은 규칙을 코드로 넣었다(`ratios()` — 반올림 후 최대 금액 행에 잔차 가산). 이 규칙은 화면 표기 규칙이며 §6의 금액 반올림 규칙(미확정)과 층위가 다르다

### 3.3 파급 동기화

| 대상 | 처리 |
|---|---|
| `invest-assets.html` | 요약 카드 4종 · 현황표 3행 · 가맹점 표 1~8번 · 페이지네이션 2페이지 |
| `invest-assets--page2.html` | 요약 카드 · 현황표 · 가맹점 표 9~16번 · 페이지네이션 |
| `invest-assets--download.html` · `--cert-confirm.html` | 요약 카드 · 현황표 · 가맹점 표 1~8번 · 페이지네이션. `--cert-confirm` 모달 `대상 가맹점 8개 → 16개` |
| `invest-assets--empty.html` | 전 값 0 — 변경 없음 |
| `certificate.html` | 표 16행 · 합계 1,523,100,000 · 비중 합 100.0% · `대상 가맹점 16개` |
| `xls-assets-merchant.html` | 시트 행 4~19 + 합계 20행 + 주석 22행으로 재배치, 주석의 기준 금액 갱신 |
| `xls-assets-status.html` | 투자실행액·순현금·합계 3행 |
| `assets/xlsx/가맹점별_투자자산_20260827.xlsx` | 8행 → 16행(행 삽입 후 서식 승계), 합계 20행, 주석 22행 |
| `assets/xlsx/투자자산_현황_20260827.xlsx` | `B4`·`C4`·`D4`·`E4`·`F4`·`F5`·`B6` |
| `merchants.html` · `--filter-open.html` | 총 8건 → **총 16건**, 페이지네이션 2페이지 |
| `merchants--filtered.html` | 검색어 `곱창`이 `왕십리곱창타운`까지 걸려 1건 → **2건**, 행 1개 추가 |
| `contracts.html` · `--all.html` · `--downloaded.html` | 총 16건, 전체 선택 `16건 선택`·`다운로드 (16)`, 페이지네이션 2페이지 |
| `build_app.py` | `MERCHANTS` 16행 · `CONTRACTS` 16행 · `ASSET_ROWS` 투자실행액 행 · `DAILY` 7행 · `MONTHLY` 6행 · `PAGE_SIZE 8` · `ratios()` 도입 4곳 적용 · 산식 2건 · 시트 행번호 동적화 · 자체 점검 `ratioSum` |
| `app.html` | 위 `build_app.py`로 재생성 |

### 3.4 신규 8건의 식별 항목

정적 2페이지에 있던 8건은 가맹점명·투자금액·W·S만 가지고 있어, 통합본의 가맹점 목록·계약기록에 필요한 `가맹점ID · 사업자번호 · 대표자 · 업종 · 종목 · 채권매입업체 · 계약체결일`을 기존 8건의 형식에 맞춰 채웠다(`M2026-0009`~`M2026-0016`). **예시값이며 실데이터가 아니다.** 업종은 기존 8건과 같은 `음식점업`으로 두어 업종 필터의 동작 조건을 바꾸지 않았다.

---

## §4 통합본 재검증

### 4.1 `verify_app.js` — 창 없이(`--headless=new`) 실행

| 묶음 | 항목 | 결과 |
|---|---|---|
| 메뉴 전환 | 7 | 7 PASS |
| 상태 도달 (클릭 시퀀스) | 20 | 20 PASS |
| 엑셀 실제 다운로드 | 4 | 4 PASS |
| 값 변화 (정렬·필터·기간·전체선택·빈 상태) | 5 | 5 PASS |
| 화면·상태 레이아웃 | 34 | 34 PASS |
| **합** | **70** | **70 PASS / 0 FAIL** |
| 죽은 버튼 | | **0** |
| 콘솔 에러 | | **0** |

자체 점검 반환값:

```
merchantSum 1,523,100,000 · assetExecRow 1,523,100,000 · execMatch true
assetTotal 1,628,400,000 · ratioSum 100 · dailyProfitSum 1,375,880
monthlyProfitSum 35,307,250 · contracts 16 · signQueue 3 · screens 14 · states 20
```

**검증기 기대 상수 4건 갱신.** 검사 항목·판정 논리는 그대로 두고, 로스터 결정이 바꾼 데이터 상수만 고쳤다. 고치지 않으면 데이터가 아니라 낡은 기대값 때문에 FAIL이 난다.

| 검사 | 종전 기대 | 갱신 기대 | 사유 |
|---|---|---|---|
| 가맹점별 투자금액 정렬 | 오름차순 첫 행 `골목냉면` | `우리동네반찬` | 로스터 최소 금액 행이 바뀜 |
| 가맹점 검색어 필터 | 1페이지 5행 · 총8건 · `곱창` 1건 | 8행 · 총16건 · 2건 | 페이지 크기 8 · 로스터 16 · `왕십리곱창타운` |
| 계약기록 전체 선택 | `8건 선택` · `(8)` | `16건 선택` · `(16)` | 계약 16건 |
| 데이터 없음 지표 0 치환 | `1,389,800,000` | `1,628,400,000` | 투자자산 총액 |

### 4.2 `verify_identity.js` — 조작 후 항등식 (신규)

정렬·페이지·기간·granularity를 실제로 조작한 뒤 렌더된 DOM 값만 읽어 항등식을 재검산한다. 14건 전건 PASS · 콘솔 에러 0.

| 조작 | 확인 내용 | 결과 |
|---|---|---|
| 정렬 없음 / 금액↑ / 금액↓ / 가맹점명 / Ty / 비중 (6종) | 2페이지 순회 16행 · 금액 합 1,523,100,000 · 비중 합 100.0 · 행별 `Ty = 0.11%×365÷W` · 현황표 합계 = 실행액+순현금 · 현황 비중 합 100.0 · 요약 카드 = 현황표 | 6 PASS |
| 기간·granularity 5종 (`일주일/일별` · `어제/일별` · `이번달/일별` · `일주일/월별` · `이번달/월별`) | 행별 `수익 = 버림(실행금×0.11%)` · `상환액 = 실행금+수익` · `Ty = 0.11%×365÷W` · tfoot 합계 = 행 합 · tfoot W·Ty = 가중평균 · 요약 카드 = tfoot | 5 PASS |
| 기간 독립성 | `Ty(투자자산 대비) ÷ Ty(실행금 대비)` 배율이 조회 기간 실행금 176,600,000 ~ 32,097,500,000(약 182배)에서도 0.9350~0.9358로 고정. 목표값 `1,523,100,000 ÷ 1,628,400,000 = 0.9353`, 편차는 표시값 소수 2자리 반올림 잔차 | 1 PASS |
| 증명서 | 16행 · 합계 1,523,100,000 · 비중 합 100.0% · 대상 16개 | 1 PASS |
| 엑셀 미리보기 | `가맹점별` 16행·합계·비중 100.0% / `현황` 3행 = 화면 값 | 1 PASS |

기간별 실측:

| 기간·단위 | 행 | 실행금 | 수익 | 상환액 | W | Ty(실행금 대비) | Ty(투자자산 대비) |
|---|---|---|---|---|---|---|---|
| 일주일 · 일별 | 7 | 1,250,800,000 | 1,375,880 | 1,252,175,880 | 11.3 | 3.55% | 3.32% |
| 어제 · 일별 | 1 | 176,600,000 | 194,260 | 176,794,260 | 11.2 | 3.58% | 3.35% |
| 이번달 · 일별 | 7 | 1,250,800,000 | 1,375,880 | 1,252,175,880 | 11.3 | 3.55% | 3.32% |
| 월별 (6개월) | 6 | 32,097,500,000 | 35,307,250 | 32,132,807,250 | 11.3 | 3.54% | 3.31% |

요율 역검산 — 일별 `1,375,880 ÷ 1,250,800,000 = 0.110000%`, 월별 `35,307,250 ÷ 32,097,500,000 = 0.110000%`.

---

## §5 화면 간 정합

`verify_crossscreen.py` — 정적 HTML · `app.html` 데이터셋 · `.xlsx` 실파일을 같은 축으로 대조. **23건 전건 일치, 불일치 0.**

| 축 | 대조 대상 | 결과 |
|---|---|---|
| 가맹점 로스터 16행 (가맹점명·금액·W·S·Ty·비중) | `invest-assets`(1p)+`--page2`(2p) / `--download` / `--cert-confirm` / `certificate` / `xls-assets-merchant` / `가맹점별_투자자산.xlsx` / `app.html MERCHANTS` | 7건 일치 |
| 투자실행액 행 · 순현금 · 합계 | `invest-assets` 계열 / `xls-assets-status` / `투자자산_현황.xlsx` / `app.html ASSET_ROWS` | 3건 일치 |
| 일별 7행 + 합계 | `invest-profit` / `--datepicker` / `xls-profit-daily` / `일별_투자수익.xlsx` / `app.html DAILY` | 5건 일치 |
| 월별 6행 | `invest-profit--monthly` / `app.html MONTHLY` | 2건 일치 |
| 수익 현황 카드 4값 | `xls-profit-status` / `투자수익_현황.xlsx` | 2건 일치 |
| 증명서 대상 건수 · 합계 · 페이지 크기 | `certificate` / `가맹점별_투자자산.xlsx` / `app.html PAGE_SIZE` | 4건 일치 |

구값 전수 스캔 — `1,284,500,000` · `1,389,800,000` · `4,210,000` · `601,000` · `1,274,200,000` · `108,510,000` · `32,698,000,000` · `17,260,000` · `92.4%` · `11.2일` · `3.59%` 를 저장소 전 HTML에서 검색해 **0건**.

---

## §6 미확정 잔여 — 임의로 해소하지 않은 것

| # | 항목 | 상태 |
|---|---|---|
| 1 | 수수료율 자체 (C1) | `0.11%`는 어드민 등록 관찰값이며 정책 확정값이 아니다. 최소 5개 버전 병존(`analysis/00_종합.md` C1). 화면의 `예시` 표기 유지 |
| 2 | 기준금액 정의 | `figma_policy_fee.md:121` — 지급예정액 / 매출액 / 원본 결제 대금 3갈래 상충. 실측 1건(양수가액 49,446 · 액면 49,500)이 양쪽 다 배분액 54를 내 판별 불가. `확인 필요` 유지 |
| 3 | 금액 반올림 규칙 | `버림` 채택 + `확인필요`. 판별 실측 없음. 이번 대상 전 행의 실행금이 100,000원의 배수라 버림·반올림 어느 쪽이든 산출값 동일 |
| 4 | `0.11%`와 연 12%의 관계 | `figma_policy_fee.md:363` — 동시 발생인지 택일인지 `확인 필요`. 이번 적용은 `수수료 배분형`(0.11%)만 건드렸고 `조달이자형` 카드는 손대지 않았다 |
| 5 | 한편 넣기 셈법 | 편면산입/양편산입 미확정. `glossary.html` 검산 C가 같은 데이터에서 Ty 12.6789% vs 9.636%로 3.0429%p 벌어짐을 보인다. W금융일수가 확정되지 않으면 Ty도 확정되지 않는다 |
| 6 | `Ty(투자실행금액 대비)` / `Ty(투자자산 대비)` 산식 | 스토리보드에 라벨만 있고 산식이 없다. 적용한 `Ty(가중) × 투자실행액 ÷ 투자자산`은 정적 화면 현행값에서 역산해 복원한 `가설` |
| 7 | 합계행 주석 문구 | 정적 파일 `(평균)` vs 통합본 `(가중평균)`. `invest-profit.html` 합계 Ty에는 주석이 없고 `--monthly`에는 있다. 숫자가 아니라 문구라 이번 라운드에서 통일하지 않았다 |
| 8 | 요약 카드 부제 `W금융일수 11.3일 기준` | 카드 Ty 3.57%는 가중평균이고 11.3에서 역산하면 3.55%다(Jensen 격차 0.02%p). `기준`이 유도 관계를 시사해 재문구가 필요하나 문구 결정 사안이라 남긴다 |
| 9 | `상환액` 앵커 | 투자실행금 고정·상환액 유도로 적용. 반대 앵커(상환액 고정·실행금 역산)를 택하면 투자자산 화면과의 교차 참조가 깨진다 |
| 10 | 예시 데이터 개연성 | 일평균 실행금 약 178,690,000 × W 11.29일 ≈ 2,018,000,000이 잔액이어야 하나 투자실행액은 1,523,100,000(약 1.32배 차). 로스터 16건 통일로 차이가 1.57배에서 줄었으나 해소는 아니다. 요율과 무관한 데이터 생성 문제 |
| 11 | 신규 8건 식별 항목 | §3.4 — 예시값 채움. 실데이터 아님 |

`rate_fix_map.json`의 `unresolved` 3건 가운데 `U1`(로스터 8/16 결정)은 사용자 결정으로 해소했고, `U2`(데이터 개연성)·`U3`(문구)는 위 10·7·8로 그대로 남긴다.

---

## 산출물

| 경로 | 내용 |
|---|---|
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/rate_apply_result.md` | 본 문서 |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/roster16_model.py` | 로스터 16건 모델 — 요율·가중평균·비중 잔차 흡수를 한 곳에서 산출 |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/roster16_apply.py` | 정적 HTML·xlsx 적용기 (맵 적용 + 로스터 재산출) |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/roster16_apply.log` | 적용 로그 |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/patch_build_app.py` | `build_app.py` 데이터셋·산식 패치기 |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_identity.js` | 통합본 항등식 검증기 — 정렬·기간·페이지 조작 후 재검산 (헤드리스) |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_identity_result.json` | 항등식 검증 원문 결과 |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_crossscreen.py` | 화면 간 정합 대조기 (정적 HTML ↔ `app.html` ↔ `.xlsx`) |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_app.js` | 기존 통합본 검증기 — 기대 상수 4건 갱신 |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_run.log` | `verify_app.js` 실행 로그 (70 PASS / 0 FAIL) |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/build_app.py` | 통합본 생성기 — 데이터셋 16행·페이지 크기 8·`ratios()`·산식 2건 |

### 저장소 수정 파일 (커밋·push 없음)

| 경로 | 내용 |
|---|---|
| `/Users/semi/cursor/payhug-investor-admin/invest-assets.html` | 요약 카드·현황표·가맹점 표 1~8·페이지네이션 |
| `/Users/semi/cursor/payhug-investor-admin/invest-assets--page2.html` | 요약 카드·현황표·가맹점 표 9~16·페이지네이션 |
| `/Users/semi/cursor/payhug-investor-admin/invest-assets--download.html` | 요약 카드·현황표·가맹점 표 1~8·페이지네이션 |
| `/Users/semi/cursor/payhug-investor-admin/invest-assets--cert-confirm.html` | 위 + 모달 대상 16개 |
| `/Users/semi/cursor/payhug-investor-admin/certificate.html` | 표 16행·합계·대상 건수 |
| `/Users/semi/cursor/payhug-investor-admin/invest-profit.html` | 일별 7행·합계·요약 카드 |
| `/Users/semi/cursor/payhug-investor-admin/invest-profit--datepicker.html` | 동일 |
| `/Users/semi/cursor/payhug-investor-admin/invest-profit--monthly.html` | 월별 6행·합계·요약 카드 |
| `/Users/semi/cursor/payhug-investor-admin/xls-assets-status.html` | 시트 3행 |
| `/Users/semi/cursor/payhug-investor-admin/xls-assets-merchant.html` | 시트 16행·합계·주석 |
| `/Users/semi/cursor/payhug-investor-admin/xls-profit-daily.html` | 시트 7행·합계·주석 |
| `/Users/semi/cursor/payhug-investor-admin/xls-profit-status.html` | 시트 카드 4행 |
| `/Users/semi/cursor/payhug-investor-admin/merchants.html` · `merchants--filter-open.html` | 총 16건·페이지네이션 |
| `/Users/semi/cursor/payhug-investor-admin/merchants--filtered.html` | 검색 결과 2건 |
| `/Users/semi/cursor/payhug-investor-admin/contracts.html` · `contracts--all.html` · `contracts--downloaded.html` | 총 16건·선택 16건·페이지네이션 |
| `/Users/semi/cursor/payhug-investor-admin/app.html` | `build_app.py` 재생성 |
| `/Users/semi/cursor/payhug-investor-admin/assets/xlsx/가맹점별_투자자산_20260827.xlsx` | 16행·합계·주석 |
| `/Users/semi/cursor/payhug-investor-admin/assets/xlsx/투자자산_현황_20260827.xlsx` | 투자실행액·순현금·합계 |
| `/Users/semi/cursor/payhug-investor-admin/assets/xlsx/일별_투자수익_20260827.xlsx` | 7행·합계·주석 |
| `/Users/semi/cursor/payhug-investor-admin/assets/xlsx/투자수익_현황_20260827.xlsx` | 카드 4값 |

손대지 않은 것 — `glossary.html`(자체 예시 데이터셋이 0.11%와 전건 정합) · `invest-assets--empty.html` · `invest-profit--empty.html`(전 값 0) · `index.html` · `capability.html` · `README.md`.
