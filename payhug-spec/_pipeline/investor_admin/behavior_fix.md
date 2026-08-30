# 투자자 어드민 동작 정정·산식 교정 결과

대상 — `/Users/semi/cursor/payhug-investor-admin` (커밋·push 0건). 기준(진실) — `payhug-admin-web` @ `f79997b` 읽기 전용, 워킹트리 변경 0건.
지시서 — `behavior_parity.md` §5 우선순위, `marker_legend.md` 번호 대응표, `ceo_definitions.md` 대표 정의 원문.

`app.html` 은 `build_app.py` 가 쓴다. 직접 편집하지 않고 생성기를 고쳐 재생성했다. `index.html` 은 `build_index.py`, `archive.html` 은 `build_archive.py`, `assets/xlsx/` 4종은 신설 `build_xlsx.py` 가 쓴다.

건드리지 않은 파일 — `glossary.html`(다른 조 재조판 중) · `capability.html`. `inquiry.html` 은 §7 한 줄만.

---

## §1 P1 4건 — 사용자가 막히거나 값이 틀어지던 것

### P1-1 다운로드 토스트가 사라지지도 닫히지도 않던 것

원본 `Toast.tsx:18, 20-25, 45-51` 은 `duration` 기본 3,000ms 이고, `duration === 0` 이면 자동 소멸 대신 X 닫기 버튼을 렌더한다. **닫을 수단 없는 토스트가 만들어지지 않는 구조**다. 그 구조를 그대로 옮겼다.

| 항목 | 전 | 후 |
|---|---|---|
| 기본 지속시간 | `showToast` 인자 없으면 타이머 자체가 없음(영구) · `showInfo` 2,600ms · 엑셀 3,200ms | 전부 `TOAST_MS = 3000` 단일 기본값 |
| `duration = 0` | 정의 없음 | `t-close` X 버튼 렌더 + `ACT['toast-close']` 로 닫힘 |
| 닫기 버튼 스타일 | 없음 | `Toast.tsx:45-51` 의 `shrink-0 p-0.5` · 타입별 색 대응 |

실측 — 다운로드 후 0.9초에 토스트 표시·닫기 버튼 0개, 3.2초 뒤 소멸. `showToast(..., 0)` 은 3.4초 뒤에도 남아 있고 X 클릭으로 닫힌다 (`verify_toast.js` 2건 PASS).

### P1-2 날짜 입력이 조회 조건을 안 움직이던 것

`change` 위임에 `pf-date` 분기를 넣어 입력값을 `PF.from`/`PF.to` 에 반영한다 (원본 `DateRangeFilter.tsx:116-123` 의 `value`/`onChange` 대응).

실측 — 시작일 `2026-08-25` 입력 → 표 7행 → 3행, 검색 후에도 입력값 유지, 기간 표기 `2026-08-25 ~ 2026-08-27`. 종전에는 입력값이 버려지고 `2026-08-21` 로 되돌아갔다.

### P1-3 역전 범위 무방어

원본 `DateRangeFilter.tsx:79, 116, 122, 128, 138-140` 대로 네 가지를 함께 건다.

- 시작일 `max = 종료일`, 종료일 `min = 시작일` (달력 자체를 상호 제한)
- 역전 시 하단 안내문 `.range-warn` 노출
- 역전 시 `검색` 버튼 `disabled`
- 버튼이 눌려도 `pf-search` 가 조회를 막고 안내 토스트

안내 문구는 원본 `INVALID_RANGE_MESSAGE` 의 낱말을 쓰되 종결을 이 레포 화면 문체(명사형)에 맞췄다 — `시작일은 종료일보다 이후일 수 없음.`

실측 — `max=2026-08-27` · `min=2026-08-21` 부착 확인, 시작일 `2026-09-30` 입력 시 안내문 노출·검색 버튼 비활성.

### P1-4 모달 배경 클릭이 안 닫히던 것

원본 백드롭 37개 중 32개가 배경 클릭으로 닫힌다. **닫히지 않는 5개의 정체**를 확인했다 — `merchants/[id]/page.tsx:2142`(`submitting`) · `partners/page.tsx:446`(`ocrProcessing`) · `MerchantDocumentEditModals.tsx:34`(`analyzing`), 전부 **진행 중 오버레이**다. 즉 원본의 규칙은 "진행 중 오버레이만 예외, 나머지는 닫힌다".

같은 규칙을 적용했다. 백드롭 5개 중 4개에 `data-act="backdrop"` 을 붙이고, 클릭 위임에서 **이벤트 대상이 백드롭 자신일 때만** 닫는다(패널 안쪽 클릭은 새지 않는다 — 원본 `ConfirmDialog.tsx:54-55` 의 백드롭 `onClick` + 패널 `stopPropagation` 대응). `acquisition-signing` 은 전자서명 진행 중 오버레이라 예외로 뒀다.

실측 — `invest-assets/cert-confirm` · `acquisition-list/confirm` · `acquisition-list/done` · `coocon/confirm` 4건 닫힘, `acquisition-list/signing` 유지.

---

## §2 엑셀을 원본과 같게

원본 `lib/excel.ts` 정독 결과를 그대로 적용했다. 생성기는 신설 `build_xlsx.py`(`roster16_model` import → openpyxl 로 4파일 신규 작성).

### 헤더 서식 — `fillSheet` 실측 규격

| 항목 | 전 | 후 (원본 `lib/excel.ts:23-29`) |
|---|---|---|
| 배경 | `F3F4F6` | `FF6366F1` solid |
| 글자 | `374151` bold 10pt | `FFFFFFFF` bold 11pt |
| 정렬 | 좌(숫자열 우) | 가로 center · 세로 middle |
| 행 높이 | 지정 없음 | 24 |

재생성본을 openpyxl 로 다시 열어 4파일 전 헤더 셀에서 위 4항목을 실측 확인했다. 미리보기 화면의 헤더 띠도 같은 인디고로 맞췄다(`assets/sheet.css` `.sheet td.c-head`).

제목 병합행·2행 공백·헤더 3행·thin 테두리·틀고정 `A4`·열 너비·열별 숫자서식은 유지했다. `behavior_parity.md` §4 G-2·G-3 이 인정한 개선분이고, 지시상 개선 15건은 그대로 둔다.

### 파일명 규칙

원본은 `{내용}_{시작일}_{종료일}.xlsx`, 날짜 `YYYY-MM-DD` (`TransferRecordsTab.tsx:318` · `overview/page.tsx:658` · `PreSettlementTab.tsx:394` · `LockAccountDeposits.tsx:219`).

| 전 | 후 |
|---|---|
| `투자자산_현황_20260827.xlsx` | `투자자산현황_2026-08-27_2026-08-27.xlsx` |
| `가맹점별_투자자산_20260827.xlsx` | `가맹점별투자자산_2026-08-27_2026-08-27.xlsx` |
| `투자수익_현황_20260827.xlsx` | `투자수익현황_2026-08-21_2026-08-27.xlsx` |
| `일별_투자수익_20260827.xlsx` | `일별투자수익_2026-08-21_2026-08-27.xlsx` |

투자자산 2종은 기준일 스냅샷이라 시작=종료다. 투자수익 2종은 기본 조회기간(일주일)이다. 구 파일 4개는 삭제했다.

### 워크북 구성 — 단일 시트 4파일 유지

원본 `lib/excel.ts` 는 `downloadExcel`(단일 시트)과 `downloadExcelSheets`(다중 시트)를 함께 내놓고, 실제 사용처가 갈린다 — `이체내역`·`차액정산`은 단일 시트, `정산상세`·`계산서발행자료`·`선정산결과`·`락계좌_입금내역`은 다중 시트다. 다중 시트는 **한 화면의 여러 섹션을 한 번에 내보낼 때** 쓰는 형태다.

투자자 어드민은 버튼 1개가 화면의 표 1개에 대응하므로 `downloadExcel` 쪽이 원본 정합이다. 구성은 바꾸지 않았다.

---

## §3 엑셀 다운로드 직행

사용자 지시대로 중간 화면을 없앴다. 원본도 `ExcelDownloadButton` → `downloadExcel` → `Blob` → `a[download].click()` 으로 화면 전환 없이 파일을 내보낸다(`lib/excel.ts:38-51`).

### `app.html`

`ACT['xls-open']` 이 `go(XLSX[k].screen)` 으로 미리보기 화면을 열던 것을 **실물 파일 전달**로 바꿨다. 내려받는 동안 버튼 라벨을 `다운로드 중...` + 인라인 스피너로 교체하고(원본 `PreSettlementTab.tsx:483-484` · `LockAccountDeposits.tsx:309-310` 규격) 끝나면 완료 토스트를 낸다. `가맹점별 투자자산` 버튼은 종전대로 `invest-assets/download` 상태로 전환한다.

### 정적 화면

엑셀 버튼 13건을 `href="xls-*.html"` → `href="assets/xlsx/<파일>" download` 로 교체했다 — `invest-assets` 2 · `--page2` 2 · `--download` 1 · `--cert-confirm` 2 · `invest-profit` 2 · `--datepicker` 2 · `--monthly` 2. `*--empty.html` 의 `disabled` 4건과 `contracts*.html` zip 은 손대지 않았다.

### `xls-*.html` 4종 보존

삭제하지 않았다. **Figma 임포트 전용 산출물 서식**으로 성격을 바꿔 표기했다.

- `index.html`·`archive.html`·`README.md`·`app.html` 갤러리·화면 라벨을 `엑셀 미리보기 —` → `엑셀 산출물 서식 —` 으로 통일
- `figma_import_plan.md` 에 "화면 흐름 진입점이 아니라 엑셀 산출물 서식을 Figma 로 옮기기 위한 프레임" 명시
- `app.html` 안에서는 도크·해시 딥링크로만 도달한다

---

## §4 산식 정정

`marker_legend.md` 로 대표 정의서의 번호가 전부 풀린 뒤의 확정 적용분이다.

### ⑤ 투자자산 대비 ty수익율 — 화면 쪽 오류

```
대표 정의   ⑤ = (④ × PSA) / (PSA + PSC),  PSC = 기간 동안 EC들의 합(유량)
종전 화면   ⑤ = ④ × 투자실행액 / 투자자산       ← 기준일 잔액 1개(스톡)
```

분자는 기간 실적인데 분모 스케일만 시점량이라 기간량과 시점량이 한 비율에 섞여 있었다. 대표 정의는 분모도 기간 합이다.

검산 (Decimal, 일주일 기본 조회):

```
④  = PSMR × 365 ÷ PSD = 0.0011 × 365 ÷ 11.2946 = 3.554328%
PSA = 1,250,800,000                       기간 투자실행금 합
PSC = 105,300,000 × 7일 = 737,100,000     기간 EC 합
⑤  = 3.554328% × 1,250,800,000 ÷ 1,987,900,000 = 2.236407%  → 2.24%
종전 = 3.554328% × 1,523,100,000 ÷ 1,628,400,000 = 3.323300%  → 3.32%
```

| 기간 | 전 | 후 | PSC 근거 |
|---|---|---|---|
| 일주일 `2026-08-21~27` (화면 기본·엑셀) | `3.32%` | **`2.24%`** | EC 7건 = 737,100,000 |
| 이번달 `2026-08-01~27` (정적 월별 화면) | `3.26%` | **`2.24%`** | EC 27건 = 2,843,100,000 |
| 월별 6개월 `2026-03-01~08-27` (통합본 월별) | `3.31%` | **`2.23%`** | EC 180건 = 18,954,000,000 |
| 어제 `2026-08-26` | `3.35%` | **`2.24%`** | EC 1건 = 105,300,000 |

EC 개수 산정 — EC 는 마감 배치가 하루에 한 건 쌓는 값이라 기간 일수만큼 센다. 일별 레코드는 1건, 월별 레코드는 그 달 가운데 조회 기간에 걸친 일수로 센다. **일별 EC 원장이 없어 EC 값 자체는 순현금 잔액 `105,300,000` 예시값으로 고정**했다 — 실데이터 연결은 확인 대상(§8).

반영처 — `app.html` KPI · `app.html` 엑셀 시트 데이터 B8 · `invest-profit.html` · `invest-profit--datepicker.html` · `invest-profit--monthly.html` · `xls-profit-status.html` · `투자수익현황_*.xlsx` B8 · `roster16_model.py`(대조 원천).

각주도 함께 고쳤다. `※ … 투자자산 대비 수익율은 순현금을 포함한 투자자산 총액 기준.` 이 정정된 산식과 어긋나 `※ … 투자자산 대비 수익율의 분모는 기간 투자실행금 합 + 기간 순현금 합(PSC).` 로 교체했다(화면·엑셀 양쪽).

### ⑥ 일별 표 투자실행금액 대비 ty수익율 — 이미 일치

`⑥ = (투자수익 ÷ 투자실행금) × 365 ÷ w금융일수` (행 단위). 일별 7행·월별 6행 전건을 재검산한 결과 현행 값과 오차 0이라 **바꾸지 않았다**.

```
2026-08-21  196,790 ÷ 178,900,000 = 0.110000% ; × 365 ÷ 11.4 = 3.5219% → 3.52%  (표기 3.52)
2026-08-27  205,260 ÷ 186,600,000 = 0.110000% ; × 365 ÷ 11.5 = 3.4913% → 3.49%  (표기 3.49)
```

`verify_identity.js` 가 매 조회마다 전 행을 이 식으로 재계산해 대조한다(7행·6행·1행 5조합 PASS).

### 라벨 `입금일자` → `정산예정일`

대표 지시 명시분. 화면·엑셀 전수 반영.

| 위치 | 후 |
|---|---|
| `app.html` 일별 표 헤더 | `정산예정일` |
| `app.html` 월별 표 헤더 | `정산예정월` (일별의 월 단위 대응 — 파생 적용) |
| `app.html` 엑셀 시트 A3 | `정산예정일` / `정산예정월` |
| `invest-profit.html` · `--datepicker.html` | `정산예정일` |
| `invest-profit--monthly.html` | `정산예정월` |
| `xls-profit-daily.html` A3 | `정산예정일` |
| `일별투자수익_*.xlsx` A3 | `정산예정일` |

PDF 22종에는 `입금일자` 표기가 없어 대상이 아니다. `glossary.html`·`capability.html` 은 스토리보드 원문을 추적하는 문서라 원문 표기를 남겼다(§8).

### 검산 — 흔들지 않은 값

- 가맹점 16행 비중 합 **100.0%** (정렬·페이지 조작 6조합 전건 유지)
- 투자실행액 `1,523,100,000` = 가맹점 16행 합, 투자자산 `1,628,400,000` = 투자실행액 + 순현금
- ④ 값 `3.55%`(일주일) · `3.54%`(월별) 불변
- 일별 수익 합 `1,375,880` · 월별 `35,307,250` 불변
- 요율 C1 미확정이므로 `0.11%` 는 `예시값` 표기 유지

---

## §5 P2·P3 나머지 이탈

| # | 이탈 | 조치 |
|---|---|---|
| P3-3 | 검색창 Enter 무반응 | keydown 위임에 `mc-kw` Enter → `mc-search`, 날짜 입력 Enter → `pf-search` (원본 `sales/[bizNo]/page.tsx:558`). 실측 `곱창` + Enter → 2행 |
| P3-1 | 전이 가속곡선 생략 → `ease` | `--ease-default: cubic-bezier(0.4, 0, 0.2, 1)` 토큰 1개를 `:root` 에 두고 `assets/base.css` 8선언·`app.html` 1선언·`assets/sheet.css` 1선언·`certificate.html` 1선언·`index.html` 3선언 일괄 참조 |
| P3-2 | 토스트 2,600 / 3,200ms | `TOAST_MS = 3000` 단일화 (§1 P1-1) |
| P2-5 | 그룹 헤더가 `<div>`, 셰브론 눌러도 무반응 | `SIDEBAR` 의 `nav-group-label` 3개를 `<button type="button">` 으로 바꾸고 `ACT['nav-group']` 이 `.nav-group.collapsed` 를 토글, 셰브론 `-90°` `0.2s`, `aria-expanded` 고지 (원본 `AdminLayout.tsx:486, 494`). 정적 화면의 `assets/template.html` 은 접힘 스크립트가 없어 원본대로 뒀다 |
| D-9·D-10 | 다운로드 중·로딩 상태 부재 | 엑셀 버튼에 원본 규격 인라인 스피너(20px · 2px · `#65c826` · `commonSpinner 0.6s linear`, `CommonLoading.tsx:78-95`) + `다운로드 중...` 라벨 교체 적용. 페이지 전환 로딩은 §8 |
| P4-3 | `.tooltip` CSS 사용처 0 | 투자 수익 KPI 의 `투자실행금액 대비`·`투자자산 대비` 두 라벨에 다크 툴팁을 붙여 ④·⑤ 산식과 PSA·PSC 실값을 보인다. 원본이 툴팁을 쓰는 목적(금액 산식 설명, `overview/page.tsx:386`)과 같다 |
| P2-4 | 네이티브 date 위 커스텀 달력 중첩 | 커스텀 달력 전면 제거 (§6) |
| P3-4 | 프리셋 활성 판정이 클릭 플래그 | 현재 `PF.from`/`PF.to` 가 프리셋 범위와 같은지로 판정하도록 바꾸고 `aria-pressed` 부착 (원본 `DateRangeFilter.tsx:74-77, 99`). 기간 라벨(`일주일`·`이번달`·`직접입력`)도 같은 판정에서 파생 |

`behavior_parity.md` §4 의 **개선 15건은 그대로 뒀다** — 완료 토스트·열별 숫자서식·제목행/틀고정·비활성 화살표 hover 억제·열 헤더 정렬·정렬 표식·체크박스 브랜드 색·빈 상태 4화면·표시 구간 고지·조건 칩·`role="status"`·모달 X 버튼·초기화 안내 토스트.
단 G-11(커스텀 드롭다운 ARIA·키보드)은 §6 결론에 따라 컨트롤 자체가 사라져 함께 없어졌다.

---

## §6 필터 네이티브 통일 · 화면 폐기

### 업종 필터

원본 어드민은 커스텀 드롭다운 **0건**(15파일 25곳 전부 `<select>`, `role=listbox`/`combobox` 0, 드롭다운 라이브러리 0)이다. `app.html` 의 커스텀 `div.dd` 를 `merchants.html:105` 와 동일한 `<select class="input" style="width:140px">` 로 바꿨다.

함께 사라진 것 — `.dd`·`.dd-trigger`·`.dd-menu`·`.dd-opt` CSS 전량, `ACT['dd-toggle']`·`ACT['dd-pick']`, 드롭다운 키보드 처리기, 바깥 클릭 닫기, `MC.dd`·`DD_FOCUS` 상태.
실측 — `app.html` 잔존 `.dd-trigger`/`.dd-opt`/`[role=combobox]`/`[role=listbox]` **0개**. 옵션은 종전대로 원장 데이터에서 파생한다(`전체` + 실재 업종).

### 날짜 필터

네이티브 `input[type=date]` 단독으로 되돌렸다(원본 `DateRangeFilter.tsx:116-123`). `.datepicker`·`.dp-*` CSS 전량, `datepickerHTML()`, `ACT['dp-open']`·`dp-move`·`dp-pick`, `PF.dp`·`PF.dpMonth`·`PF.pick` 을 제거했다.

### 폐기 화면

| 화면 | 처리 |
|---|---|
| `merchants--filter-open.html` | **파일 삭제**. 커스텀 드롭다운 열림 상태만을 위해 존재하던 화면이라 존치 근거가 사라졌다 |
| `invest-profit--datepicker.html` | **폐기 대상 — 파일만 남김.** 같은 이유로 설계 대상이 아니나, `glossary.html`(접촉 금지)이 링크를 걸고 있어 지우면 링크가 깨진다 |

두 화면 모두 통합본 상태 레지스터·`index.html`·`archive.html` 설명·`figma_import_plan.md` 임포트 대상에서 제외했다. `archive.html` 은 디스크를 스캔하므로 `invest-profit--datepicker.html` 행은 남되 설명이 `폐기 대상 — …` 으로 나온다.
레포 전역 `merchants--filter-open` 참조 **0건**. 브라우저 기본 팝업(네이티브 select·네이티브 달력)은 화면설계 대상이 아니므로 대체 상태를 새로 만들지 않았다.

**모수 변동** — 통합본 상태 20 → **18**, `index.html` 상태 20 → 18, Figma 임포트 33프레임 → **31프레임**.

---

## §7 재검증

전 검증기 창 없이(`--headless=new`) 실행.

| 검증기 | 결과 | 기준 대비 |
|---|---|---|
| `verify_app.js` | **72 PASS / 0 FAIL** · 죽은 컨트롤 **0** / 검사 134건 · 키보드 미도달 **0** · 콘솔 **0** | 71 → 72 (모수 변동, 아래) |
| `verify_identity.js` | **항등식 14 PASS / 0 FAIL** · 비중 합 **100.0%** · 콘솔 0 | 14 유지 |
| `verify_crossscreen.py` | **23건 · 불일치 0** | 23 유지 |
| `verify_links.py` | **79건 · FAIL 0** · 전건 200 · 바이트 일치 | 링크 모수 증가 |
| `verify_toast.js` | **16건 · FAIL 0** · 실물 동반 · 콘솔 0 | 10 → 16 |

### 모수가 바뀐 자리

- **`verify_app.js` 71 → 72** — 상태 20 → 18(폐기 2건)로 −2, 레이아웃 34조합 → 32로 −2, 값 변화 6 → 11로 +5. 새로 넣은 5건은 P1·P2·P3 정정분을 직접 겨눈다: `날짜 입력이 조회 조건을 움직인다` · `역전 범위 방어 — 상호 제한·안내문·버튼 비활성` · `검색창 Enter → 조회 실행` · `모달 배경 클릭 닫기 — 진행 오버레이만 예외` · `메뉴 그룹 접힘`.
- **죽은 컨트롤 스캔 모수 144 → 134** — 폐기 상태 2개가 빠졌고, 네이티브 `input[type=date]` 를 클릭 스캔 대상에서 제외했다. 브라우저 기본 달력은 DOM 에 흔적을 남기지 않아 `클릭 뒤 변화` 로는 산 것/죽은 것을 가릴 수 없다. 대신 값 변화(`change`)가 조회 조건을 움직이는지를 값 변화 절에서 직접 본다.
- **`verify_toast.js` 10 → 16** — 엑셀 직행 4건(`xls-open`)과 토스트 소멸·닫기 2건을 추가했다.
- **`verify_links.py`** — 엑셀 파일명 4건 교체, 화면 1개 삭제. 아울러 `HREF` 정규식에 단어 경계를 넣어 `data-src=` 를 `src=` 로 오인해 잡던 오탐 5건을 없앴다(`glossary.html` 이 도입한 속성이며, 링크 결함이 아니었다).

**판정 논리는 유지했다.** 바꾼 것은 기대 상수와 대조 대상 컨트롤이다.

- `verify_identity.js` 의 `wantTyAsset` 을 대표 정의 ⑤ 로 재계산하도록 교체. 종전 `Ty(투자자산 대비) 기간 독립 — 배율 = 투자실행액/투자자산` 케이스는 **구식(스톡) 산식을 기대값으로 박아 둔 것**이라 `Ty(투자자산 대비) 배율 = PSA/(PSA+PSC) — 기간별 대조` 로 바꿨다. 대표 정의에서 ⑤ 의 배율은 기간마다 달라지므로 기간별로 각각 대조한다(최대 편차 0.0018, 표기 반올림 잔차 범위).
- `verify_app.js` 의 업종 필터 케이스를 커스텀 combobox 대조에서 네이티브 `<select>` 대조로 교체하고, 커스텀 컨트롤 잔존 0건을 함께 본다.

### 엑셀 다운로드 직행 — 4건 전건 실측

버튼을 누른 뒤 `body[data-view]` 가 원 화면에 그대로 머무는지(미리보기 화면으로 넘어가지 않는지)와 실물 파일이 디스크에 떨어지는지를 함께 본다.

| 버튼 | 클릭 후 화면 | 중간 화면 | 내려온 파일 | 바이트 |
|---|---|---|---|---|
| 투자자산 현황 | `invest-assets` | 없음 | `투자자산현황_2026-08-27_2026-08-27.xlsx` | 5,824 / 원본 5,824 |
| 가맹점별 투자자산 | `invest-assets` | 없음 | `가맹점별투자자산_2026-08-27_2026-08-27.xlsx` | 6,615 / 원본 6,615 |
| 투자수익 현황 | `invest-profit` | 없음 | `투자수익현황_2026-08-21_2026-08-27.xlsx` | 5,586 / 원본 5,586 |
| 일별 투자수익 | `invest-profit` | 없음 | `일별투자수익_2026-08-21_2026-08-27.xlsx` | 5,958 / 원본 5,958 |

정적 화면 13건은 헤드리스 DOM 덤프로 `href="assets/xlsx/…xlsx"` + `download` 부착을 전건 확인했다.

---

## §8 미해소

| # | 항목 | 상태 |
|---|---|---|
| U-1 | **EC 일별 원장 부재** | ⑤ 의 `PSC` 는 EC 를 하루 한 건으로 세되 값은 순현금 잔액 `105,300,000` 예시값으로 고정했다. 실제로는 날마다 달라진다. 일별 EC 계열이 붙어야 ⑤ 가 실값이 된다 — **확인 대상** |
| U-2 | **정의서 안 PSC 표현 충돌** | 배치 항목은 `평균순현금` 을 산출한다고 적었는데 `PSC` 는 `EC들의 합` 으로 정의돼 있다. 합으로 보면 737,100,000, 평균으로 보면 105,300,000 이고 결과가 1%p 넘게 벌어진다. 이번 정정은 **원문의 `합`** 을 채택했다. `inquiry.html` Q-3 에 이미 문항이 서 있다 |
| U-3 | **수수료율 C1 미확정** | 0.11% 를 `예시값` 표기로 유지. 확정 전까지 투자수익·상환액·투자실행금 세 열이 확정값이 아니다 |
| U-4 | **`glossary.html`·`capability.html` 미반영** | 두 문서는 스토리보드 원문(`입금일자`)과 종전 산식 해석(`투자자산 대비 = 투자실행금액 대비 × 투자실행액 비중`)을 추적한다. `glossary.html` 은 다른 조 재조판 중이라 접촉 금지, `capability.html` 은 원문 추적 문서라 이번 라운드에서 손대지 않았다. **대표 정의 확정분과 어긋난 서술이 남아 있어 후속 동기화 필요** |
| U-5 | **`invest-profit--datepicker.html` 잔존** | 폐기 대상으로 판정했으나 `glossary.html` 링크 때문에 파일만 남겼다. `glossary.html` 재조판이 끝나면 링크와 함께 삭제할 것 |
| U-6 | **사이드바 240↔72 접힘(P4-2)** | 원본에 있으나 재현본에 없다. 투자자 어드민은 메뉴 7개뿐이고 접기 컨트롤을 둘 자리가 설계에 없어 이번 라운드에서 넣지 않았다. 그룹 접힘(P2-5)만 구현했다 — **판단 기록** |
| U-7 | **페이지 전환 로딩(D-10 후단)** | 원본 `app/loading.tsx` → `CommonLoading` 마스코트는 라우트 전환에 붙는다. 단일 HTML 프로토타입에는 라우트 전환이 없어 물리적으로 붙일 자리가 없다. 엑셀 다운로드 중 표시만 원본 규격으로 넣었다 — **판단 기록** |
| U-8 | **엑셀 파일명 기간이 고정** | `app.html` 은 정적 xlsx 를 내려준다. 조회 기간을 바꿔도 파일명·내용은 기본 기간(일주일) 그대로다. 실제 구현에서는 `dateFrom`/`dateTo` 로 조립된다 |
| U-9 | **`review.html` 진행바 전이** | `transition:width .25s` 는 원본에 대응 요소가 없어 가속곡선 통일 대상에서 뺐다 |

---

## 산출·수정 파일

### 생성기 (`_pipeline/investor_admin/`)

| 절대경로 | 성격 |
|---|---|
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/build_app.py` | 통합본 생성기 — P1 4건·엑셀 직행·⑤ 산식·라벨·네이티브 select·달력 제거·그룹 접힘·툴팁 |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/build_xlsx.py` | **신규** — 엑셀 4종 생성기 (원본 헤더 서식·파일명 규칙) |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/build_index.py` | 랜딩 생성기 — 폐기 상태 2건 제외, `xls-*` Figma 전용 표기, 전이 곡선 |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/build_archive.py` | 아카이브 생성기 — `xls-*`·폐기 대상 설명 |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/roster16_model.py` | 값 원천 — `tyAsset` 을 대표 정의 ⑤ 로 교체 |

### 검증기

| 절대경로 | 갱신 |
|---|---|
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_app.js` | 상태 시퀀스·스캔/레이아웃 대상·엑셀 직행 실측·업종 select 대조·P1 케이스 5건 |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_identity.js` | ⑤ 기대식 교체·배율 기간별 대조 |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_crossscreen.py` | xlsx 경로 4건 |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_links.py` | `data-src=` 오탐 제거 |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_toast.js` | 파일명 4건·직행 4건·소멸/닫기 2건 |

### 산출물 (`payhug-investor-admin/`)

`app.html` · `index.html` · `archive.html` · `README.md` · `assets/base.css` · `assets/sheet.css` · `certificate.html` ·
`invest-assets.html` · `invest-assets--page2.html` · `invest-assets--download.html` · `invest-assets--cert-confirm.html` ·
`invest-profit.html` · `invest-profit--datepicker.html` · `invest-profit--monthly.html` ·
`xls-assets-status.html` · `xls-assets-merchant.html` · `xls-profit-status.html` · `xls-profit-daily.html` ·
`inquiry.html`(§7 한 줄) · `assets/xlsx/` 4종 교체 ·
**삭제** `merchants--filter-open.html`

### 문서

`/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/figma_import_plan.md` — 임포트 제외 2프레임 표기
`/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/behavior_fix.md` — 이 문서
