# 투자자 어드민 — 결함 수정 + 통합 프로토타입 조립 결과

대상 레포: `/Users/semi/cursor/payhug-investor-admin/` (커밋·push 없음. 파일 수정·생성까지)
기준 자료: `screen_inventory.md`(결함 20건) · `app_spec.json`(화면 14/상태 20/인터랙션 93/다운로드 6) · `app_build_notes.md`(조립 지침) · `request_register.md`(D·R·S·X·G)
작업일: 2026-08-27

## 0. 요약

| 항목 | 결과 |
|---|---|
| 수정·생성 파일 | 레포 14 (신규 1 · 파일명 교체 2 · 수정 11) + 파이프라인 7 |
| H급 결함 3건 | 전건 해소 |
| M급 9건 | 4건 수정 · 5건 통합본에서만 해소하거나 범위 밖 |
| L급 8건 | `logo-icon.png` 존치(보고만) · 나머지는 통합본에서 해소 |
| `app.html` | 화면 14 · 상태 20 · 모달 5 · 조작 핸들러 30 · 140,537 B |
| 헤드리스 검증 | **70항목 PASS / 0 FAIL** · 죽은 버튼 0 · 콘솔 에러 0 |
| 확인 필요 | 4건 (§6). 이 중 2건은 18:01 재빌드에서 처리된 것으로 보인다 (§11) |
| 기준 시점 | §3~§7 수치는 17:07 빌드 기준. 이후 재빌드분은 §11 |

---

## 1. 산출 파일

### 1-1. 레포 (`/Users/semi/cursor/payhug-investor-admin/`)

| 경로 | 구분 | 내용 |
|---|---|---|
| `app.html` | 신규 | 통합 프로토타입. 화면 14 · 상태 20 · 순수 JS 단일 파일. 데이터 모델에서 표·합계·비중을 계산해 그린다 |
| `acquisition.html` | 파일명 교체 | 구 `acquisition--list.html`. 기본(목록·선택 0건) 화면. 상태 마커 제거 |
| `acquisition--confirm.html` | 파일명 교체 | 구 `acquisition.html`. 서명 확인 모달 상태. 상태 마커 `서명 확인` 부여, 서명 대상 정정 |
| `acquisition--done.html` | 수정 | 완료 모달 `확인` → `acquisition.html` |
| `index.html` | 재작성 | 통합본 진입 카드 + 용어·기능 문서 카드 2 + 화면 13종 카드 + 상태 20종 접이식 목록 |
| `README.md` | 재작성 | 화면 14·상태 20·`app.html`·`sheet.css`·`xlsx/` 등재, `logo-icon.png` 미사용 표기 |
| `invest-assets.html` | 수정 | `증명서 다운로드` → 확인 모달 경유 |
| `invest-assets--cert-confirm.html` | 수정 | `발급` → `certificate.html`, `취소` → `invest-assets.html`, 엑셀 링크 복원 |
| `invest-assets--page2.html` | 수정 | 엑셀 링크 2건 복원 |
| `invest-assets--download.html` | 수정 | 엑셀 링크 1건 복원(완료 표시 버튼은 유지) |
| `invest-profit--monthly.html` | 수정 | 엑셀 링크 2건 복원 |
| `invest-profit--datepicker.html` | 수정 | 엑셀 링크 2건 복원 |
| `login.html` | 수정 | `로그인` → `invest-assets.html` |
| `merchants.html` | 수정 | 업종 select 옵션 2 → 5 |

`assets/base.css`·`assets/sheet.css`·`assets/template.html`·`assets/components.html`·`assets/logo-icon.png`·`assets/xlsx/` 미변경. 나머지 상태 파일 미변경.

### 1-2. 파이프라인 (`/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/`)

| 경로 | 내용 |
|---|---|
| `build_app.py` | `app.html` 조립기. 사이드바·산식 카드·용어 안내·쿠콘 본문·로그인 카드를 원본 HTML에서 문자 그대로 인용 |
| `build_index.py` | `index.html` 생성기 |
| `verify_app.js` | 헤드리스 크롬(CDP) 검증기. 창을 띄우지 않는다 |
| `verify_app_result.json` | 검증 원자료 |
| `shots/` | 1440px 뷰포트 캡처 3건 |
| `verify_run.log` | 검증 실행 로그 (17:07 빌드 대상) |
| `probe_current.js` | 재빌드본 최소 점검 스크립트 (§11-1) |
| `app_build_result.md` | 이 문서 |

---

## 2. 결함 수정

### 2-1. H-1 기본/상태 역전 — 파일명·상태 id 변경 내역

| 변경 전 | 변경 후 | 상태 id (`app_spec.json` 기준) |
|---|---|---|
| `acquisition--list.html` (선택 0건) | **`acquisition.html`** | — (기본 화면) |
| `acquisition.html` (2건 선택 + 확인 모달) | **`acquisition--confirm.html`** | `acquisition-confirm` |

파일명 교체로 처리한 근거: 사이드바 32개 파일의 `href="acquisition.html"`·`index.html` 카드·`contracts--empty.html` CTA·`assets/template.html`이 전부 `acquisition.html`을 가리킨다. 이 이름이 기본 화면을 물게 하면 인바운드 링크를 한 곳도 고치지 않고 착지점이 바로잡힌다. 사이드바 nav 블록은 MD5 동일성 유지 대상이므로 href 수정 경로를 택하지 않았다.

`app_spec.json` 대조:
- `screens[].id = "acquisition-list"` 유지. `screens[].file` 만 `acquisition--list.html` → `acquisition.html` 로 실측 변경
- `states[].id = "acquisition-confirm"` 유지. 대응 파일 `acquisition--confirm.html` 신설 — 다른 상태 파일과 `<화면>--<상태>.html` 규칙 일치
- `app.html` 내부: `data-screen="acquisition-list"`, `data-state="confirm"`, 딥링크 `#acquisition-list/confirm`. 별칭으로 `#acquisition-confirm`(spec 상태 id)과 `#acquisition.html`도 받는다

부수 정정: 신규 `acquisition.html`에서 h1 상태 마커(`선택 없음`)와 미사용 `.state-flag` 정의 제거. 신규 `acquisition--confirm.html`에 `.state-flag` 정의와 마커 `서명 확인` 부여.

### 2-2. H-2 서명 대상 불연속 — 김성호떡볶이 본점 + 달빛곱창 홍대점으로 통일

정정 방향 근거:

| 근거 | 내용 |
|---|---|
| 등장 빈도 | 1행+2행(김성호·달빛곱창) 조합 = `acquisition--signing.html`·`acquisition--done.html` 2개 파일. 1행+3행(김성호·바다마루) 조합 = 확인 모달 1개 파일 |
| 편집량 | 확인 모달 1곳(선택 행 1개 + 모달 목록 1행) 대 완료 흐름 2파일(선택 행 2개 + 뱃지 2개 + 체크박스 2개 + 완료 목록 2행 + 날짜 2개) |
| 지침 | `app_build_notes.md` §3-3 H-2 가 1행+2행 통일을 명시 |
| 잔여 대기 표기 | `acquisition--done.html` 안내 배너 `서명 완료 2건 · 대기 잔여 1건` 이 1·2행 서명 전제와만 맞는다 |

검산: 서명 대기 3건, 선택 2건, 서명 완료 2건 + 잔여 1건 = 3건. 계약 생성일 2026-08-25(김성호)·2026-08-26(달빛곱창)이 확인 모달·완료 모달·목록 행에서 동일. 이 흐름에는 금액 항목이 없어 금액 검산 대상 없음.

`app.html`에서는 확인 모달·진행 모달·완료 모달의 대상 목록·건수를 모두 목록의 실제 선택값에서 생성한다. 선택을 바꾸면 세 모달이 함께 따라가므로 같은 유형의 불연속이 구조적으로 생기지 않는다.

### 2-3. H-3 상태 20개 인바운드 0 — `index.html` 재작성

- 최상단에 통합 프로토타입 진입 카드(`app.html`). 사이드바 배경색 카드로 갤러리와 구분
- 그 아래 용어 사전(`glossary.html`) · 기능 명세(`capability.html`) 링크 카드 2종. 파일 생성은 다른 조 담당이므로 링크만 배치
- 기존 8장 갤러리 유지 + 각 카드 하단에 `<details>` 접이식 상태 목록. 카드 8장에 상태 20종 전건 수용
- 하위 화면 섹션 신설: `login.html` + `xls-*.html` 4종

지시문의 "`xls-*` 3종"은 실측과 어긋난다. `xls-assets-status` · `xls-assets-merchant` · `xls-profit-status` · `xls-profit-daily` 4종이 모두 존재하며 각각 `assets/xlsx/` 파일과 1:1로 연결되어 있다(§5 참조). 4종 전건 등재.

### 2-4. M급 처리

| 결함 | 처리 | 판단 |
|---|---|---|
| M-1 상태 마커 이원화 | 개별 파일 미수정 / `app.html`에서 `.badge + .state-badge` 단일화 | 개별 파일 20개의 마커를 바꾸면 Figma 임포트 원본의 렌더가 함께 바뀐다. 통합본에서만 단일화 |
| M-2 상태 파일 엑셀·발급 링크 소실 | **수정** — 5개 파일 9건 `<button>` → `<a href>` 복원 + `발급` → `certificate.html` | `<a class="btn">`와 `<button class="btn">`은 `base.css` 상 렌더가 같아 시각 변화 0. 막다른 길만 사라진다. `disabled`(empty 2파일)·`is-done`(download 1건)은 의도된 표기이므로 제외 |
| M-3 빈 상태 마크업 3종 | 개별 파일 미수정 / `app.html`에서 `.empty-ico·.empty-title·.empty-desc` 단일화 | M-1과 같은 이유 |
| M-4 필터 컨트롤 이원화 | 개별 파일 미수정 / `app.html`에서 커스텀 `.dd` 로 단일화 | 정적 캡처에서 네이티브 select 의 열린 상태를 표현할 방법이 없어 `--filter-open`만 `.dd`인 것은 의도된 구성. 결함으로 보지 않음 |
| M-5 증명서 확인 모달 우회 | **수정** — `invest-assets.html` 링크를 `invest-assets--cert-confirm.html`로 | 1줄. 플로우가 화면 링크로 성립하지 않는 상태였다 |
| M-6 목적지 없는 CTA 4건 | **3건 수정** — `login` 로그인 → `invest-assets.html`, `acquisition--done` 확인 → `acquisition.html`, cert-confirm 발급 → `certificate.html`. `certificate`의 `PDF 다운로드`는 미수정 | PDF는 대응 파일·상태가 없다. 없는 목적지를 만들면 산출물이 늘어난다. `app.html`에서는 토스트로 응답 |
| M-7 업종 옵션 세트 불일치 | **수정** — `merchants.html` 2 → 5 | 1줄. 같은 컨트롤이 화면마다 다른 목록을 보이는 것은 검토자에게 오독을 준다 |
| M-8 `components.html` 미갱신 | 미수정 | 컴포넌트 갤러리 9종 신규 등재는 별건 분량. 이번 범위 밖 |
| M-9 `README.md` 미반영 | **수정** — 전면 재작성 | 파일명이 바뀌었으므로 방치 시 문서가 실제와 어긋난다 |

### 2-5. L급

- **L-1 `assets/logo-icon.png` (43,134 B)** — 참조 0건 고아 자산. 지시대로 삭제하지 않고 그대로 두었다. `README.md` 구조 트리에 `미사용. 로고는 base.css의 .logo-mark data URI로 렌더` 표기
- L-2·L-3·L-5·L-6·L-7·L-8 개별 파일 미수정. `app.html`에서만 해소(로그아웃 → 로그인 화면, 인라인 CSS 1벌 정리, 자리표시자 링크 토스트 응답, 카운트 표기 `.tbl-count`+`.sel-pill` 단일화)

---

## 3. `app.html` 구조

### 3-1. 집계

| 항목 | 수 |
|---|---|
| 화면 (`section.screen[data-screen]`) | 14 |
| 상태 (`data-state`) | 20 |
| 사이드바 메뉴 | 7 |
| 모달 | 5 |
| 실제 파일 다운로드 | 4 (`assets/xlsx/*.xlsx`) |
| 외부 링크 | 1 (We-bank, `target="_blank" rel="noopener"`) |
| 조작 핸들러 (`ACT[...]`) | 30 |
| 파일 크기 | 140,299 B / 2,353 줄 |

### 3-2. 골격

```
app.html
├ <head>  viewport 1440 · Noto Sans KR · base.css · sheet.css · <style>(통합본 전용)
└ <body data-active="<메뉴ID>" data-view="<화면ID>">
   ├ .page
   │  ├ aside.sidebar               ← assets/template.html 전문 그대로 (nav 블록 MD5 = 개별 32개 파일과 동일)
   │  └ main.content
   │      └ section.screen[data-screen] × 12
   ├ section.screen[data-screen] × 2   (index · login — 사이드바 없음, .page 를 숨긴다)
   ├ .modal-backdrop[data-modal] × 5
   ├ .action-bar (정산채권 양수 전용)
   ├ .toast (1행·2행 두 형태를 한 요소가 담당)
   ├ .dock (통합본 전용 크롬 — 화면 선택 + 상태 버튼)
   └ <script>  데이터 · 모델 · 파생 · 렌더러 · 조작
```

`body`의 화면 표시 속성은 `data-view`다. `data-screen`을 쓰면 `section[data-screen]`과 셀렉터가 충돌해 `[data-screen="x"] [data-act]`가 다른 섹션의 요소를 잡는다(조립 중 실제로 발생, `xls-get` 오결합).

### 3-3. 데이터 주도 방식

숫자를 마크업에 박지 않는다. 데이터셋 6종에서 계산해 그린다.

| 데이터셋 | 행 | 출처 |
|---|---|---|
| `MERCHANTS` | 8 | `invest-assets.html` 가맹점별 표 · `merchants.html` 목록 · `certificate.html` 문서 표 · `assets/xlsx/가맹점별_투자자산_20260827.xlsx` |
| `ASSET_ROWS` | 2 | `invest-assets.html` 현황 표 · `assets/xlsx/투자자산_현황_20260827.xlsx` |
| `DAILY` | 7 | `invest-profit.html` 일별 표 · `assets/xlsx/일별_투자수익_20260827.xlsx` |
| `MONTHLY` | 6 | `invest-profit--monthly.html` 월별 표 |
| `CONTRACTS` | 8 | `contracts.html` |
| `SIGNQ` | 3 | `acquisition.html` 서명 대기 목록 |

계산 항목: 요약 카드 4종 · 현황 표 합계와 비중 · 가맹점별 비중 · 일별/월별 tfoot 합계와 가중평균 · 수익 현황 4지표 · 증명서 표 합계 · 엑셀 미리보기 시트 4종 · 목록 건수 · 선택 건수.

정렬은 `th[data-sort]` 클릭으로 4개 표(가맹점별 투자자산 · 일별/월별 투자수익 · 가맹점 목록 · 계약기록)에서 동작한다. 필터·기간·페이지 변경 시 합계가 그 결과로 다시 계산된다.

### 3-4. 상태 파생

상태를 직접 세팅하지 않고 모델에서 파생한다. 조작 → 모델 변경 → 상태 재계산 → 렌더 순서.

| 화면 | 모델 | 파생 규칙 |
|---|---|---|
| `invest-assets` | `IA{page, downloaded, empty, cert}` | empty > cert-confirm > download > page2 > default |
| `invest-profit` | `PF{gran, from, to, preset, dp, dpMonth, pick}` | dp → datepicker / 결과 0건 → empty / gran=monthly → monthly / else default |
| `merchants` | `MC{sector, buyer, kw, dd, page, applied}` | dd → filter-open / applied && 0건 → empty / applied → filtered / else default |
| `acquisition-list` | `AQ{sel[3], signed[3], phase}` | phase 그대로 |
| `contracts` | `CT{sel, page, downloaded, empty}` | empty > downloaded > 전건 선택 → all > default |
| `coocon` | `CO{modal}` | modal → confirm |
| `password` | `PW{cur, nw, cfm, touched, done}` | done / 규칙 미충족 → weak / 확인값 불일치 → error / default |

화면을 옮기면 대상 화면 모델이 기본으로 되돌아간다(개별 HTML = 새 페이지 로드와 같은 전제). 예외는 `PEND` 예약 1건 — 가맹점별 엑셀을 실제로 내려받은 뒤 `투자 자산`으로 돌아오면 `download` 상태로 착지한다.

### 3-5. 딥링크

`#<화면>/<상태>` 형식. `#invest-assets/page2` · `#acquisition-list/signing` · `#password/done`.
별칭 수용: `app_spec.json` 상태 id(`#invest-assets-page2`) · 개별 파일명(`#acquisition--signing.html`).

---

## 4. 화면 간 숫자 정합 교차 검산

`window.__selfcheck()` 로 상시 확인 가능.

| 항목 | 값 | 대조 |
|---|---|---|
| 가맹점 8개 투자금액 합 | 1,284,500,000 | 현황 표 `투자실행액` 행과 일치 |
| 투자자산 합계 | 1,389,800,000 | 투자실행액 1,284,500,000 + 순현금 105,300,000 |
| 가맹점별 비중 합 | 100.0% | 8행 각 비중을 소수 1자리로 반올림한 합 |
| 일별 투자수익 합 | 4,210,000 | 수익 현황 카드 `투자수익` |
| 월별 투자수익 합 | 108,510,000 | 월별 표 tfoot |
| 계약기록 | 8건 | `contracts` 목록 |
| 서명 대기 | 3건 | `acquisition` 안내 배너 |

### 4-1. 정적 파일 대비 의도된 표기 차이

계산으로 바꾸면서 정적 파일과 값이 갈리는 곳. 예시값 자체는 새로 만들지 않았고, 원 파일의 행 데이터에서 유도한 결과다.

| 위치 | 정적 파일 | 통합본 | 사유 |
|---|---|---|---|
| 수익 현황 `투자실행금` | 1,284,500,000 | 1,250,800,000 | 기간 내 행의 투자실행금 합. `--empty`가 0을 표시하므로 기간 종속 값이 맞다. 정적 파일은 전체 투자실행액을 쓴다 |
| 수익 현황 `Ty수익율(투자실행금액 대비)` | 3.58% | 3.56% | 투자금액 가중평균. 산정 규칙은 `일별_투자수익_20260827.xlsx` A13 주석 "투자금액 가중평균(단순평균 아님)" |
| 수익 현황 `Ty수익율(투자자산 대비)` | 3.31% | 3.21% | 위 값 × (기간 투자실행금 ÷ 투자자산 1,389,800,000) |
| 일별 표 tfoot `Ty수익율` | 3.58% | 3.56% | 위와 동일 규칙 |
| 일별 표 tfoot 라벨 | `(평균)` | `(가중평균)` | xlsx 주석과 일치시킨 표기 |
| 일별 표 tfoot `W금융일수` | 11.3 | 11.3 | 일치 |
| 월별 표 tfoot 전 항목 | — | — | 일치 (합계 32,698,000,000 / 32,097,500,000 / 108,510,000, W 11.3, Ty 3.55%) |
| 현황 표 `투자실행액` 행 W·S·Ty | 11.2 / 0.42% / 3.59% | 동일 | 합계 행에서 산정하지 않는 기록값이므로 데이터로 보유 |
| 가맹점별 표 페이지 | 8행 1페이지 + 별도 8행 2페이지 | 8행 2페이지(5+3) | §6-1 참조 |
| 계약기록 카운트 표기 | 인라인 span `총 8건 · 선택 3건` | `.tbl-count` + `.badge.sel-pill` | L-6 단일화 |
| 계약기록 다운로드 버튼 | 기본 화면은 건수 미표기 | 선택 N>0 이면 `(N)` 표기, 전건 선택 시 `.armed` | L-6 연장 |
| 상태 마커 7건 | `.state-flag` 회색 pill | `.badge.badge-gray.state-badge` | M-1 단일화. 색 계열은 회색 유지 |
| 빈 상태 | `es-*` / `empty-icon` / `empty-ico` 3종 | `.empty-ico·.empty-title·.empty-desc` 1종 | M-3 단일화 |
| 가맹점 업종 컨트롤 | 기본은 select, 열림 상태만 `.dd` | 전 상태 `.dd` | M-4 단일화. 클릭으로 열림 상태를 재현하려면 커스텀 드롭다운이 필요 |
| 월별 전환 시 기간 | 프리셋 `이번달`(08-01~08-27) + 6개월 표 | 2026-03-01 ~ 2026-08-27 + 6개월 표 | 정적 파일은 기간 라벨과 표 범위가 어긋난다. 통합본은 표·현황 카드가 같은 기간을 가리키게 맞춘다 |

---

## 5. `assets/xlsx/` ↔ 결과 화면 대응 실측

지시받은 X-1(엑셀 결과 화면 4종 중 3종만 존재)은 **실측과 어긋난다.** 4종 전건 존재하고, 각 화면의 시트 내용이 실제 xlsx 파일 내용과 일치한다.

| 엑셀 파일 | 크기 | 결과 화면 | 시트명 | 시트 내용 대조 |
|---|---|---|---|---|
| `투자자산_현황_20260827.xlsx` | 5,812 B | `xls-assets-status.html` | 투자자산 현황 | A1 제목 · A3 머리행 7열 · A4~A6 데이터 3행 · A8 주석 — 화면과 일치 |
| `가맹점별_투자자산_20260827.xlsx` | 6,161 B | `xls-assets-merchant.html` | 가맹점별 투자자산 | A1 제목 · A3 머리행 6열 · A4~A12 데이터 9행 · A14 주석 — 화면과 일치 |
| `투자수익_현황_20260827.xlsx` | 5,560 B | `xls-profit-status.html` | 투자수익 현황 | A1 제목 · A3 머리행 2열 · A4~A8 항목 5행 · A10 주석 — 화면과 일치 |
| `일별_투자수익_20260827.xlsx` | 5,934 B | `xls-profit-daily.html` | 일별 투자수익 | A1 제목 · A3 머리행 6열 · A4~A11 데이터 8행 · A13 주석 — 화면과 일치 |

`app.html`에서 네 화면 전건 도달 가능(원 화면의 엑셀 버튼 → 결과 화면 → 실제 파일). 신규 화면 제작 대상 없음.

월별 표에는 대응 엑셀 파일이 없다. 월별 전환 상태에서 엑셀 버튼을 누르면 `월별 표에 대응하는 엑셀 파일 없음. 일별 표 기준 파일만 제공.` 안내가 뜬다(비활성 사유 안내).

---

## 6. 조사 중 확인된 사항 — 정책 판단 대상

값을 임의로 맞추지 않았다. 화면의 기존 예시값을 그대로 옮기고 사실만 기록한다.

### 6-1. 가맹점별 투자자산 2페이지 데이터가 나머지 화면과 정합하지 않는다

- `invest-assets.html` 1페이지 8행: 투자금액 합 1,284,500,000 · 비중 합 100.0%
- `invest-assets--page2.html` 2페이지 8행(청춘포차 신촌점 등): 투자금액 합 238,600,000 · 비중 합 18.5%
- 두 페이지를 합치면 비중이 118.5%가 되고, 투자실행액이 1,523,100,000이 되어 현황 표·요약 카드·증명서·엑셀 4종의 1,284,500,000과 어긋난다
- `certificate.html`·`invest-assets--cert-confirm.html`은 대상 가맹점을 `8개`로 표기하는데, 2페이지가 존재하면 16개가 된다

통합본 처리: 8행 데이터셋 1벌만 두고 페이지 크기를 5로 잡아 2페이지(5+3)를 만들었다. `invest-assets-page2` 상태의 정체성(2페이지 표시)은 유지되고, 다른 화면의 값과 어긋나지 않는다. 2페이지 8개 상호는 통합본에서 사용하지 않는다. 정본이 16개 가맹점이라면 투자실행액·비중·증명서 대상 수를 함께 재산정해야 한다. **확인 필요**

### 6-2. 수익 산정 기준 카드 2종이 같은 화면의 표를 재현하지 못한다

`invest-assets.html`·`invest-profit.html`의 산식 카드(구조 변경 없이 그대로 이관, D-1 확정 사항)와 표 값의 관계.

| 모델 | 화면 산식 | 화면 표 값으로 계산 | 표의 투자수익 | 배율 |
|---|---|---|---|---|
| 수수료 배분형 | 선정산 거래액 × 0.11% | 1,274,200,000 × 0.11% = 1,401,620 | 4,210,000 | **3.00배** |
| 조달이자형 | 투자실행금 × 연 12% × 사용일수 ÷ 365 | 1,250,800,000 × 12% × 11.3 ÷ 365 = 4,646,808 | 4,210,000 | 1.10배 |

- 배분형 역산 요율 = 4,210,000 ÷ 1,274,200,000 = **0.3304%** (화면 표기 0.11%의 3.00배)
- 조달이자형 역산 사용일수 = 4,210,000 × 365 ÷ (1,250,800,000 × 12%) = **10.238일** (W금융일수 11.3일과 근사하나 불일치)
- 대입한 `선정산 거래액`은 화면에 그 이름의 항목이 없어 일별 표 `상환액` 합계를 대용했다. 항목 대응 자체가 미정의

요율은 `analysis/00_종합.md` C1 미확정 사안이다. 통합본은 화면의 `(예시)` 표기와 `.formula-caption`을 그대로 유지하고 값을 손대지 않았다. **확인 필요**

### 6-3. 산식 카드 라벨이 레지스터 D-1 표기와 다르다

- `request_register.md` D-1: `매출 배분형(0.11%)` · `대출 이자형(연 12%)`, 라벨 예 `채권매입 배분` vs `조달이자`
- 화면 실제: `수수료 배분형` · `조달이자형`

2모델 병기라는 구조는 충족한다. 라벨 문구만 갈린다. 지시대로 화면 구조를 건드리지 않았다. **확인 필요**

### 6-4. 일별 합계 Ty수익율이 행 값으로 재현되지 않는다

`일별_투자수익_20260827.xlsx` A13 주석은 합계행 W금융일수·Ty수익율을 투자금액 가중평균으로 정의한다.
- W금융일수 가중평균 = 11.2946 → 11.3 (파일 표기와 일치)
- Ty수익율 가중평균 = 3.5648 → 3.56 (파일 표기 3.58%와 0.02%p 차이). 단순평균도 3.57로 3.58이 나오지 않는다

예시 데이터 작성 시점의 반올림 흔적으로 보인다. 통합본은 주석에 적힌 규칙(가중평균)을 따른다. **확인 필요**

---

## 7. 헤드리스 검증

실행: `node /Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_app.js`
방식: 로컬 정적 서버 + Chrome `--headless=new` + CDP. 창을 띄우지 않는다. 원자료 `verify_app_result.json`, 로그 `verify_run.log`.
집계: **70항목 PASS / 0 FAIL** (메뉴 7 · 상태 20 · 다운로드 4 · 값 변화 5 · 레이아웃 34) · 죽은 버튼 0 · 콘솔 에러 0.

### 7-1. 사이드바 메뉴 7개 전환

각 항목 클릭 후 `body[data-active]` · 대상 섹션 표시 · 활성 메뉴 배경 `#7FE141` · 소속 그룹 라벨 색을 확인.

| 메뉴 | 도착 화면 | 판정 |
|---|---|---|
| 투자 자산 | `invest-assets` | PASS |
| 투자 수익 | `invest-profit` | PASS |
| 가맹점 | `merchants` | PASS |
| 정산채권 양수 | `acquisition-list` (모달 없는 목록, 선택 0건) | PASS |
| 계약기록 | `contracts` | PASS |
| 쿠콘 관리 현금 | `coocon` | PASS |
| 비밀번호 변경 | `password` | PASS |

### 7-2. 상태 20개 — 실제 클릭 시퀀스 도달

전건 PASS. 시퀀스는 마우스 조작만으로 구성했다(도크 경유 2건 명시).

| # | 상태 | 클릭 시퀀스 |
|---|---|---|
| 1 | `invest-assets/page2` | 사이드바 `투자 자산` → 페이지네이션 `2` |
| 2 | `invest-assets/download` | `투자 자산` → 가맹점별 `엑셀 다운로드` → `엑셀 파일 내려받기` → 뒤로가기 `투자 자산` |
| 3 | `invest-assets/cert-confirm` | `투자 자산` → `증명서 다운로드` |
| 4 | `invest-assets/empty` | `투자 자산` → 도크 `화면 · 상태` → `데이터 없음` |
| 5 | `invest-profit/monthly` | `투자 수익` → 토글 `월별` |
| 6 | `invest-profit/datepicker` | `투자 수익` → 시작일 입력칸 |
| 7 | `invest-profit/empty` | `투자 수익` → 시작일 → 달력 `이전 달` → `1일` → `7일` (2026-07-01~07-07, 결과 0건) |
| 8 | `merchants/filter-open` | `가맹점` → 업종 드롭다운 |
| 9 | `merchants/filtered` | `가맹점` → 업종 드롭다운 → `음식점업` → 검색어 `곱창` → `검색` (1건) |
| 10 | `merchants/empty` | `가맹점` → 검색어 `라멘` → `검색` (0건) |
| 11 | `acquisition-list/confirm` | `정산채권 양수` → 1행 체크 → 2행 체크 → `서명하기` |
| 12 | `acquisition-list/signing` | 위 + `서명 진행` |
| 13 | `acquisition-list/done` | 위 + 자동 전이(1.5초) |
| 14 | `contracts/all` | `계약기록` → 헤더 전체선택 체크박스 |
| 15 | `contracts/downloaded` | 위 + `선택 문서 다운로드 (8)` |
| 16 | `contracts/empty` | `계약기록` → 도크 `문서 없음` |
| 17 | `coocon/confirm` | `쿠콘 관리 현금` → `We-bank 바로가기` |
| 18 | `password/weak` | `비밀번호 변경` → 새 비밀번호 `12345678` 입력 |
| 19 | `password/error` | `비밀번호 변경` → 새 `payhug!2026` / 확인 `payhug!2025` |
| 20 | `password/done` | `비밀번호 변경` → 새·확인 `payhug!2026` → `변경하기` |

4·16번은 화면 안에 필터가 없어 도크(통합본 전용 크롬)를 경유한다. 나머지 18건은 화면 내부 컨트롤만으로 도달한다.

### 7-3. 엑셀 실제 다운로드 4건

버튼 → 결과 화면 → 실제 파일 3단 연결. 내려받은 바이트가 원본과 일치.

| 원 화면 버튼 | 결과 화면 | 내려받은 파일 | 바이트 | 판정 |
|---|---|---|---|---|
| 투자 자산 · 현황 엑셀 | `xls-assets-status` | `투자자산_현황_20260827.xlsx` | 5,812 | PASS |
| 투자 자산 · 가맹점별 엑셀 | `xls-assets-merchant` | `가맹점별_투자자산_20260827.xlsx` | 6,161 | PASS |
| 투자 수익 · 수익 현황 엑셀 | `xls-profit-status` | `투자수익_현황_20260827.xlsx` | 5,560 | PASS |
| 투자 수익 · 일별 엑셀 | `xls-profit-daily` | `일별_투자수익_20260827.xlsx` | 5,934 | PASS |

`downloads` 6건 중 나머지 2건(증명서 PDF · 재양도합의서 묶음)은 대응 파일이 없다. 각각 토스트로 응답한다.

### 7-4. 조작이 값을 실제로 바꾸는지

| 검사 | 결과 | 판정 |
|---|---|---|
| 가맹점별 투자금액 열 정렬 | 오름차순 첫 행 `골목냉면` / 내림차순 첫 행 `김성호떡볶이 본점` | PASS |
| 가맹점 검색어 필터 | 행 5 → 1, 카운트 `총 8건` → `총 1건` | PASS |
| 기간·일별/월별 전환 시 합계 재계산 | 일주일 7행 합계 4,210,000 → 어제 1행 596,000 → 월별 6행 108,510,000 | PASS |
| 계약기록 전체 선택 | `3건 선택` → `8건 선택`, 버튼 `선택 문서 다운로드 (8)` | PASS |
| 데이터 없음 상태 지표 0 치환 | 1,389,800,000 표기 사라짐 | PASS |

### 7-5. 죽은 버튼 전수 스캔

30개 화면·상태 조합에서 보이는 클릭 가능 요소를 전수 열거해 하나씩 클릭하고, 클릭 전후 DOM·해시·모달·토스트를 비교.

**반응 없는 요소 0건.**

제외 기준(죽은 버튼이 아닌 것):
- 이미 활성인 컨트롤(`.active` 프리셋·토글·현재 페이지 번호, 선택된 드롭다운 옵션) — 같은 값을 다시 고르는 조작
- `target="_blank"` 외부 링크 1건(We-bank) — 새 창 이동이라 스캔 대상 밖. `href`·`rel="noopener"` 표기로 확인
- 텍스트·비밀번호 입력칸 — 클릭이 아니라 입력에 반응. 7-2의 18·19·20번에서 확인
- 단일 시트 탭 — `<span>`이며 버튼이 아니다

목적지가 없던 컨트롤에 부여한 응답:

| 컨트롤 | 응답 |
|---|---|
| 가맹점 목록 행 | `가맹점 상세 화면은 이번 설계 범위 밖. 대상 <MID>` 안내 |
| 계약기록 PDF 링크 | `재양도합의서 원문 파일은 이번 설계 범위 밖. 대상 <MID>` 안내 |
| 서명 대기 행 `계약서 보기` | `계약서 원문 미리보기는 이번 설계 범위 밖. 대상 <상호>` 안내 |
| 증명서 `PDF 다운로드` | `투자자산 증명서 PDF 내려받기 완료` 토스트 |
| 로그인 `비밀번호 찾기` | `비밀번호 재발급은 페이허그 담당자에게 문의.` 안내 |
| 사이드바 로고 | 랜딩 갤러리(`index`) |
| 사이드바 `로그아웃` | 로그인 화면 |
| 검색 / 초기화 | 결과 건수 안내 · 조건 초기화 안내 |
| 월별 상태의 일별 엑셀 버튼 | `월별 표에 대응하는 엑셀 파일 없음. 일별 표 기준 파일만 제공.` (비활성 사유) |

### 7-6. 콘솔

에러 0건. 조립 중 잡은 2건은 수정 완료.
- SVG `path` 파싱 오류 16건 — 조립기 토큰 치환에서 `$D_CARD`가 `$D_CARDS`를 잘라 경로가 깨졌다. 치환 순서를 긴 토큰 우선으로 교정
- `favicon.ico` 404 — `<link rel="icon" href="data:,">` 로 요청 제거

### 7-7. 자체 점검(`window.__selfcheck()`)

```
merchantSum 1284500000 · assetExecRow 1284500000 · execMatch true
assetTotal 1389800000 · ratioSum 100 · dailyProfitSum 4210000
monthlyProfitSum 108510000 · contracts 8 · signQueue 3 · screens 14 · states 20
```

### 7-8. 화면·상태 34조합 레이아웃 점검

각 조합에 진입해 섹션 렌더 높이 · 열린 모달 · 하단 액션바 표시 조건을 확인. **34조합 전건 PASS.**

- 렌더 높이 최소 372px(`password/done`) ~ 최대 1,400px(`invest-profit/default`). 빈 화면 0건
- 모달은 해당 상태에서만 1개 노출. 나머지 조합에서 노출 0건
- 하단 액션바는 `acquisition-list` 4개 상태에서만 노출

### 7-9. 시각 확인

`shots/` 에 1440px 뷰포트 캡처 3건 보관 — `01_invest-assets.png`(요약·현황·가맹점별·정렬 마커·페이지네이션·산식 2모델) · `02_acq-confirm.png`(H-2 정정: 확인 모달 대상 = 김성호떡볶이 본점 2026-08-25 + 달빛곱창 홍대점 2026-08-26, 액션바 `선택 2건`) · `03_xls-merchant.png`(엑셀 미리보기 격자·합계 1,284,500,000·비중 100.0%, 사이드바 활성 = 투자 자산). 캡처로 잡은 결함 1건은 수정 완료.

- `base.css`의 `.modal-backdrop`·`.action-bar`·`.toast`가 `display:flex` 로 선언돼 있어 UA 기본값 `[hidden]{display:none}` 을 덮었다. 모달 5종과 하단 액션바가 모든 화면에 겹쳐 표시되던 상태. 통합본 `<style>` 최상단에 `[hidden]{display:none !important}` 를 두어 해소. `base.css`는 건드리지 않았다
- 이 결함은 속성 기준 검사(`[data-modal]:not([hidden])`)를 통과하기 때문에 7-2 상태 검증만으로는 잡히지 않았다. 캡처 대조가 필요한 유형

---

## 8. 조립 규율 준수

| 항목 | 상태 |
|---|---|
| 개별 HTML 보존 | 34개 유지(파일명 교체 2건 포함). `app.html` 1개 추가 |
| `assets/base.css`·`assets/sheet.css` | diff 0. `<link>`로 참조, 인라인 복제 없음 |
| `assets/template.html`·`components.html`·`logo-icon.png`·`xlsx/` | 미변경 |
| 외부 스크립트·CDN·프레임워크 | 0. 순수 JS |
| 사이드바 nav 블록 | `assets/template.html` 전문 그대로. 공백 정규화 MD5가 개별 32개 파일 및 `app.html`에서 동일(`490b3b061d`) |
| `<iframe>` 사용 | 0 |
| 상태별 섹션 복제 | 0. `data-state` + 모델 파생 |
| 새 아이콘·새 색 | 0. SVG path·색 토큰 전부 원본 인용 |
| 요율·산식 숫자 | 미변경. `0.11%`·`연 12%`·`(예시)` 표기와 `.formula-caption` 유지 |
| 커밋·push | 없음 |
| `payhug-admin-web`·`payhug-merchant-web` | 미접근 |

`app_spec.json`은 H-1 정정에 맞춰 `screens[acquisition-list].file` 과 `states[acquisition-confirm].file`·`marker` 를 실측값으로 갱신했다. 화면 14 · 상태 20 · 인터랙션 93 집계는 그대로다.

---

## 9. 남은 항목

| 항목 | 상태 |
|---|---|
| `glossary.html` · `capability.html` | `index.html`에 링크 카드 배치 완료. 파일 생성은 다른 조 담당 |
| M-8 `components.html` 신설 컴포넌트 9종 등재 | 미처리 |
| 개별 상태 파일의 마커·빈 상태·필터 컨트롤 단일화 | 미처리(통합본에서만 단일화). Figma 임포트 원본의 렌더를 바꾸지 않기 위함 |
| `certificate.html`의 `PDF 다운로드` 결과 화면 | 미정의. D-2(성공 경로만)에 따라 신규 화면 제작 없음 |
| §6 확인 필요 4건 | 정책 판단 대기 |

## 10. 다른 조 산출물 연결

작업 중 같은 레포에 다음 파일이 추가되어 `index.html`에 링크 카드로 등재했다.

| 파일 | 제목 | 상태 |
|---|---|---|
| `glossary.html` | PayHug 투자자 어드민 — 계산식 용어 정의 | 존재. 링크 연결 |
| `capability.html` | PayHug 투자자 어드민 — 기능·데이터 명세 | 존재. 링크 연결 |
| `archive.html` | 투자자 어드민 — 작업물 아카이브 | 존재. 링크 연결 |

이 3개 파일의 내용은 이 작업 범위 밖이며 열람만 했다.

### 10-1. 요율 재계산 적용 시 주의

같은 파이프라인에 `rate_recalc.md` · `rate_fix_map.json`(요율 0.11% 기준 재계산, 적용 대기)이 있다. 그 조의 실측은 §6-2와 같은 방향이다 — `투자 수익` 열이 투자실행금 대비 0.3339~0.3387%로 0.11%의 3.04~3.08배.

적용 시 순서:

1. 개별 HTML의 값을 고친다
2. `build_app.py` 안의 데이터셋 상수(`MERCHANTS` · `ASSET_ROWS` · `DAILY` · `MONTHLY`)를 같은 값으로 고친다
3. `python3 build_app.py` 로 `app.html`을 다시 만든다
4. `node verify_app.js` 로 재검증한다

`app.html`은 마크업이 아니라 데이터셋에서 숫자를 만들므로, 개별 HTML만 고치면 통합본이 옛 값을 유지한다.

---

## 11. 후속 변경 — 이 문서 기준 시점 이후 (2026-08-27 18:01)

이 문서의 §3~§7 수치는 **17:07 빌드** 기준이다. 이후 다른 조가 `build_app.py`의 데이터셋과 개별 HTML을 갱신하고 `app.html`을 재빌드했다(18:01). 재빌드본 실측:

| 항목 | 17:07 빌드 (이 문서 기준) | 18:01 재빌드본 |
|---|---|---|
| 가맹점 행 수 | 8 | **16** |
| 가맹점 투자금액 합 = 투자실행액 | 1,284,500,000 | **1,523,100,000** |
| 투자자산 합계 | 1,389,800,000 | **1,628,400,000** |
| 일별 투자수익 합 | 4,210,000 | **1,375,880** |
| 월별 투자수익 합 | 108,510,000 | **35,307,250** |
| 계약기록 행 수 | 8 | **16** |
| 비중 합 | 100.0% | 100.0% |

§6에 `확인 필요`로 올린 2건이 이 재빌드로 처리된 것으로 보인다.

- **§6-1**(2페이지 8행이 나머지 화면과 불일치) — 16행 전건 채택 방향. 투자실행액·투자자산·계약기록이 그에 맞춰 재산정됨
- **§6-2**(배분형 산식이 표를 재현 못 함, 3.00배) — 일별 투자수익 합 1,375,880 = 투자실행금 1,250,800,000 × 0.11%. `rate_fix_map.json` 적용 결과로 보인다

§4·§4-1·§6-1·§6-2·§7-7의 수치는 재빌드본과 어긋나므로 그대로 인용하지 말 것.

### 11-1. 재빌드본 최소 점검

`probe_current.js` 로 18:01 재빌드본을 확인한 결과다. 이 문서 작성자의 조립 결과가 아니라 재빌드본의 현재 상태다.

| 항목 | 결과 |
|---|---|
| 상태 20개 해시 도달 | 20/20 |
| 콘솔 에러 | 0 |
| 화면 수 · 상태 수 | 14 · 20 |
| 비중 합 | 100.0% |

§2의 결함 수정분도 재빌드본에 남아 있다.

| 확인 항목 | 재빌드본 실측 |
|---|---|
| H-1 `acquisition.html` = 기본 | 상태 마커 0 · 선택 행 0 · 모달 0 |
| H-2 확인 모달 대상 | 김성호떡볶이 본점 2026-08-25 + 달빛곱창 홍대점 2026-08-26 |
| `[hidden]{display:none !important}` | 존재 |
| `body` 화면 속성 = `data-view` | 존재 (`data-screen` 0건) |
| 요율 표기 `0.11%` · `연 12%` | 유지 |

값 재계산을 추가로 적용할 때는 §10-1의 순서(개별 HTML → `build_app.py` 데이터셋 → 재빌드 → 재검증)를 따를 것.
