# 투자자 어드민 화면 인벤토리 — 통합 프로토타입 `app.html` 제작 기초자료

실측 대상: `/Users/semi/cursor/payhug-investor-admin/` (읽기 전용, 이 조사에서 미변경)
실측 기준 커밋: `5ccfa3f 로고를 base.css data URI + .logo-mark 클래스로 전환 — 바이너리 의존 제거`
실측일: 2026-08-27

---

## 0. 집계 (실측치 · 선행 세션 기술과 대조)

| 항목 | 실측 | 선행 세션 기술 | 판정 |
|---|---|---|---|
| 루트 HTML 파일 | **34개** | "HTML 37개" (작업 지시) | 지시 수치 오류 → 실측 34 채택 |
| `assets/` 내 HTML | 2개 (`template.html`, `components.html`) | — | 34 + 2 = 36 |
| 화면(고유 화면 정체성) | **14개** | "화면 8종 + 랜딩" | 8종은 사이드바 메뉴 대응 본화면만 집계한 값. 랜딩·로그인·증명서·엑셀 미리보기 4종이 누락 |
| 상태 변형 파일 | **20개** | "상태 화면 25개" | 25는 과다 집계. 실측 20 채택 |
| 인터랙션(컨트롤 단위, 중복 행 그룹화) | **93개** | — | §4 |
| 결함 | **H 3 / M 9 / L 8 = 20건** | — | §7 |

**화면 14개 내역**: 사이드바 메뉴 대응 본화면 7 (`invest-assets`, `invest-profit`, `merchants`, `acquisition`, `contracts`, `coocon`, `password`) + 메뉴 비대응 하위화면 1 (`certificate`) + 엑셀 미리보기 4 (`xls-*`) + 인증 1 (`login`) + 랜딩 1 (`index`).

README.md가 말하는 "화면 8종"은 본화면 7 + `certificate` 이고, `login`·`xls-*` 4종은 README 목록에 등재되지 않은 상태.

---

## 1. 화면·상태 전수 인벤토리

파일명 규칙은 `<화면>.html`(기본) / `<화면>--<상태>.html`(상태 변형)로 전 파일에서 일관되게 지켜짐. 예외 1건은 §7 H-1.

메뉴 열은 `<body data-active>` 값 실측(사이드바 활성 메뉴 ID). `—`는 사이드바 없음.

### 1-1. 랜딩·인증 (사이드바 없음)

| 파일 | 화면명(`<title>` / h1) | 구분 | 상태 설명 | 메뉴 | 크기 |
|---|---|---|---|---|---|
| `index.html` | PayHug 투자자 어드민 — 화면 설계(안) / `PayHug 투자자 어드민 — 화면 설계(안)` | 기본 | 화면 갤러리 8카드 | — | 8,860 B / 179줄 |
| `login.html` | PayHug Investor — 로그인 / (h1 없음) | 기본 | 로그인 폼. h1 미사용, `.login-logo` 워드마크가 제목 역할 | — | 3,063 B / 70줄 |

### 1-2. 투자 자산 (`data-active=invest-assets`)

| 파일 | 화면명 | 구분 | 상태 설명 | 메뉴 | 크기 |
|---|---|---|---|---|---|
| `invest-assets.html` | 투자 자산 | 기본 | 요약카드 4 + 현황표 + 가맹점별 표 8행 + 산식 2종 + 용어안내 | 투자 자산 | 18,175 B / 381줄 |
| `invest-assets--page2.html` | 투자 자산 (2페이지) | 상태 | 가맹점별 표 2페이지, 페이지네이션 `2` 활성 | 투자 자산 | 18,467 B / 388줄 |
| `invest-assets--download.html` | 투자 자산 (엑셀 다운로드 완료) | 상태 | 가맹점별 엑셀 버튼 `다운로드 완료`(`.is-done`) + 성공 토스트 | 투자 자산 | 18,950 B / 396줄 |
| `invest-assets--cert-confirm.html` | 투자 자산 (증명서 발급 확인) | 상태 | 증명서 발급 확인 모달 열림 (문서명·기준일·대상·작성자) | 투자 자산 | 20,235 B / 422줄 |
| `invest-assets--empty.html` | 투자 자산 (데이터 없음) | 상태 | 요약값 전부 0, 두 표 모두 빈 상태, 3개 버튼 disabled | 투자 자산 | 14,579 B / 290줄 |
| `certificate.html` | 가맹점별 투자자산 증명서 | 기본(하위화면) | 전자문서 미리보기 + 서명값 + 검증 뱃지 + 발급 안내 사이드 | 투자 자산 | 14,107 B / 291줄 |
| `xls-assets-status.html` | 엑셀 미리보기 — 투자자산 현황 | 기본(하위화면) | 스프레드시트 격자 재현, 시트 1개 `투자자산 현황` | 투자 자산 | 10,299 B / 148줄 |
| `xls-assets-merchant.html` | 엑셀 미리보기 — 가맹점별 투자자산 | 기본(하위화면) | 시트 1개 `가맹점별 투자자산` | 투자 자산 | 11,906 B / 154줄 |

### 1-3. 투자 수익 (`data-active=invest-returns`)

| 파일 | 화면명 | 구분 | 상태 설명 | 메뉴 | 크기 |
|---|---|---|---|---|---|
| `invest-profit.html` | 투자 수익 | 기본 | 프리셋 `일주일` 활성, 현황 4지표, 일별 표 7행+합계, 산식 2종 | 투자 수익 | 16,743 B / 348줄 |
| `invest-profit--monthly.html` | 투자 수익 (월별) | 상태 | 토글 `월별` 활성, 프리셋 `이번달`, 표 헤더 `입금월`, 월 6행 | 투자 수익 | 16,740 B / 346줄 |
| `invest-profit--datepicker.html` | 투자 수익 (기간 선택) | 상태 | 시작일 인풋 포커스 + 달력 팝오버(2026년 8월, 21~27 범위 선택) | 투자 수익 | 22,314 B / 451줄 |
| `invest-profit--empty.html` | 투자 수익 (결과 없음) | 상태 | 기간 2026-07-01~07-07, 지표 전부 0, 표 빈 상태, 엑셀 disabled | 투자 수익 | 14,933 B / 288줄 |
| `xls-profit-status.html` | 엑셀 미리보기 — 투자수익 현황 | 기본(하위화면) | 시트 1개 `투자수익 현황` | 투자 수익 | 10,968 B / 150줄 |
| `xls-profit-daily.html` | 엑셀 미리보기 — 일별 투자수익 | 기본(하위화면) | 시트 1개 `일별 투자수익` | 투자 수익 | 11,788 B / 153줄 |

### 1-4. 가맹점 (`data-active=merchants`)

| 파일 | 화면명 | 구분 | 상태 설명 | 메뉴 | 크기 |
|---|---|---|---|---|---|
| `merchants.html` | 가맹점 | 기본 | 필터 3종(업종 select·채권매입업체 select·검색어) + 목록 8행 | 가맹점 | 11,220 B / 223줄 |
| `merchants--filter-open.html` | 가맹점 · 필터 열림 | 상태 | 업종 필드가 네이티브 select → 커스텀 `.dd` 드롭다운으로 교체·열림. 목록은 미필터 8행 | 가맹점 | 13,672 B / 269줄 |
| `merchants--filtered.html` | 가맹점 · 검색 적용 | 상태 | 업종=음식점업 + 검색어=곱창, 적용조건 칩 2개, 결과 1행 | 가맹점 | 10,468 B / 193줄 |
| `merchants--empty.html` | 가맹점 · 결과 없음 | 상태 | 검색어=라멘, 칩 2개, 결과 0행 + 빈 상태 블록 | 가맹점 | 11,300 B / 206줄 |

### 1-5. 정산채권 양수 (`data-active=receivables`)

| 파일 | 화면명 | 구분 | 상태 설명 | 메뉴 | 크기 |
|---|---|---|---|---|---|
| `acquisition--list.html` | 정산채권 양수 · 선택 없음 | 상태(실질 기본) | 서명대기 3건 전부 미선택, 하단 액션바 `선택 0건` + `서명하기` disabled | 정산채권 양수 | 9,753 B / 176줄 |
| `acquisition.html` | 정산채권 양수 | 기본(실질 상태) | 1·3행 선택(`선택 2건`) + **서명 확인 모달이 열린 채로 배포**. 상태 마커 없음 | 정산채권 양수 | 10,936 B / 198줄 |
| `acquisition--signing.html` | 정산채권 양수 · 서명 진행 | 상태 | 1·2행 선택, 하나은행 인증서 서명 모달(스피너 + 3단계 진행) | 정산채권 양수 | 13,163 B / 244줄 |
| `acquisition--done.html` | 정산채권 양수 · 서명 완료 | 상태 | 1·2행 `서명 완료` 뱃지 + 체크박스 disabled, 완료 모달(계약기록 보기·확인) | 정산채권 양수 | 12,574 B / 226줄 |

### 1-6. 계약기록 (`data-active=contracts`)

| 파일 | 화면명 | 구분 | 상태 설명 | 메뉴 | 크기 |
|---|---|---|---|---|---|
| `contracts.html` | 계약기록 | 기본 | 8건 중 3건 선택, 다운로드 버튼 활성(카운트 미표기) | 계약기록 | 12,234 B / 221줄 |
| `contracts--all.html` | 계약기록 · 전체 선택 | 상태 | 헤더 체크박스 checked, 8건 전건 선택, 버튼 `선택 문서 다운로드 (8)` + `.armed` 강조 | 계약기록 | 12,888 B / 228줄 |
| `contracts--downloaded.html` | 계약기록 · 다운로드 완료 | 상태 | 전건 선택 유지 + 2행 구성 성공 토스트 | 계약기록 | 13,469 B / 238줄 |
| `contracts--empty.html` | 계약기록 · 문서 없음 | 상태 | 총 0건, 표 제거·빈 상태 블록, 버튼 disabled, `정산채권 양수로 이동` CTA | 계약기록 | 9,119 B / 154줄 |

### 1-7. 쿠콘 관리 현금 (`data-active=kcoon`)

| 파일 | 화면명 | 구분 | 상태 설명 | 메뉴 | 크기 |
|---|---|---|---|---|---|
| `coocon.html` | 쿠콘 관리 현금 | 기본 | We-bank 외부 연결 안내 카드 + 조회 가능 내역 3항목 | 쿠콘 관리 현금 | 9,218 B / 153줄 |
| `coocon--confirm.html` | 쿠콘 관리 현금 · 이동 확인 | 상태 | 본문 동일 + 외부 이동 확인 모달(이동 주소 표기) | 쿠콘 관리 현금 | 11,217 B / 190줄 |

### 1-8. 비밀번호 변경 (`data-active=password`)

| 파일 | 화면명 | 구분 | 상태 설명 | 메뉴 | 크기 |
|---|---|---|---|---|---|
| `password.html` | 비밀번호 변경 | 기본 | 3필드 폼 + 규칙 힌트 + `변경하기` 활성 | 비밀번호 변경 | 7,298 B / 127줄 |
| `password--weak.html` | 비밀번호 변경 · 규칙 미충족 | 상태 | 새 비밀번호 필드 오류 + 규칙 체크리스트 4항목(ok 2 / ng 2), 버튼 disabled | 비밀번호 변경 | 10,146 B / 160줄 |
| `password--error.html` | 비밀번호 변경 · 확인값 불일치 | 상태 | 확인 필드 오류(`payhug!2026` vs `payhug!2025`), 버튼 disabled | 비밀번호 변경 | 8,833 B / 144줄 |
| `password--done.html` | 비밀번호 변경 · 변경 완료 | 상태 | 폼 제거·완료 카드 + `로그인 화면으로` → `login.html` | 비밀번호 변경 | 8,509 B / 142줄 |

---

## 2. 공통 구조 실측

### 2-1. 사이드바

- **전 32개 사이드바 보유 파일에서 `<nav class="sidebar-nav">` 블록이 공백 정규화 후 MD5 완전 일치**(`aa16331105`). 메뉴 항목·순서·아이콘 SVG path·href 어긋남 0건.
- 사이드바 미보유: `index.html`, `login.html` 2개(의도된 구성).
- 로고 블록·프로필 블록도 32개 전건 동일. 프로필 표기는 `㈜테스트인베스트 님` + `.type-badge 투자자` + `로그아웃` 버튼.

**메뉴 구조 (그룹 3 / 항목 7, 순서 고정)**

| # | 그룹(`data-group`) | 그룹 라벨 | 항목(`data-menu`) | 라벨 | href | 아이콘(SVG 형태) |
|---|---|---|---|---|---|---|
| 1 | `invest` | 투자 | `invest-assets` | 투자 자산 | `invest-assets.html` | 신용카드 |
| 2 | `invest` | 투자 | `invest-returns` | 투자 수익 | `invest-profit.html` | 우상향 화살표 |
| 3 | `merchant` | 가맹점 | `merchants` | 가맹점 | `merchants.html` | 인물 그룹 |
| 4 | `merchant` | 가맹점 | `receivables` | 정산채권 양수 | `acquisition.html` | 카드 2겹 |
| 5 | `merchant` | 가맹점 | `contracts` | 계약기록 | `contracts.html` | 문서 |
| 6 | `manage` | 관리 | `kcoon` | 쿠콘 관리 현금 | `coocon.html` | 원화/달러 원형 + `.ext` 외부링크 아이콘 |
| 7 | `manage` | 관리 | `password` | 비밀번호 변경 | `password.html` | 자물쇠 |

**활성 표시 방식** — JS 없음. `<body data-active="<메뉴ID>">` 속성과 `base.css:146~165`의 정적 셀렉터 매칭으로 처리.

```
body[data-active="invest-assets"] .nav-item[data-menu="invest-assets"], … { background: var(--primary); color: #fff; }
body[data-active="invest-assets"] .nav-group[data-group="invest"] .nav-group-label, … { color: var(--primary-400); }
```

즉 활성 항목 = `#7FE141` 배경 + 흰 텍스트, 활성 그룹 라벨 = `#7FE141` 텍스트. 메뉴 ID 7개가 `base.css`에 하드코딩되어 있으므로 메뉴 추가 시 CSS 동반 수정 필요.

### 2-2. 헤더·페이지 타이틀·브레드크럼

- **브레드크럼 컴포넌트 없음.** 계층 표현은 두 가지 관례로 대체:
  - `.back-link` (뒤로가기 링크): `certificate.html`, `xls-*` 4종. 화살표 + 상위 화면명.
  - `.page-sub` 문구에 경로 표기: `xls-*`는 `투자 자산 &gt; 가맹점별 투자자산 표를 …` 형식.
- 페이지 헤더 표준: `.page-header > h1.page-title (24/32, 700, gray-900) + p.page-sub (14/20, --secondary)`, 하단 여백 24px.
- `invest-assets` 계열만 `.page-header.row-between` 변형 — 우측에 `.base-date` 기준일 pill 배치.
- 상태 마커는 `h1.page-title` 안에 인라인 span으로 삽입. **두 계통이 병존**(§7 M-1).

### 2-3. `assets/base.css` 클래스 체계 (88,843 B / 221 rule / 클래스 142개)

`app.html`에서 그대로 재사용 가능한 목록. 괄호는 변형 클래스.

| 계열 | 클래스 |
|---|---|
| 레이아웃 | `.page` `.content` `.page-header` `.page-title` `.page-sub` `.row-between` `.mb-4` |
| 사이드바 | `.sidebar` `.sidebar-logo` `.wordmark` `.logo-mark` `.sidebar-nav` `.nav-group` `.nav-group-label` `.nav-item`(`.active`, `.ext`) `.sidebar-profile` `.avatar` `.info` `.name` `.type-badge` `.logout` |
| 카드 | `.card` `.card-title` `.summary-grid`(`.cols-3` `.cols-5` `.cols-6`) `.summary-card`(`.highlight` `.amber`) `.summary-label` `.summary-value` `.summary-sub` `.unit` `.pos` `.neg` |
| 테이블 | `.tbl-wrap` `.tbl-scroll` `.tbl`(`.wide`) `.num` `.center` `.clickable` `.name` `.sub-id` `.strong` `.none` `.mono` `.total` |
| 뱃지 | `.badge`(`.sm`) + `.badge-primary` `.badge-green` `.badge-gray` `.badge-amber` `.badge-blue` `.badge-violet` `.badge-red` |
| 버튼 | `.btn` + `.btn-primary` `.btn-outline` `.btn-excel` `.btn-danger` `.btn-gray` `.btn-cancel` `.btn-confirm`, `.icon` `.icon-lg` |
| 검색·필터 | `.search-bar` `.preset-row` `.preset-btn`(`.active`) `.filter-row` `.filter-field` `.filter-tilde` `.input` `.search-input-wrap` `.search-input` |
| 토글·탭·페이징 | `.toggle` `.toggle-btn`(`.active`) `.filter-tabs` `.filter-tab`(`.active`, `.count`) `.pagination` `.page-btn`(`.active`) `.page-arrow` |
| 산식 | `.formula-grid` `.formula-card`(`.ok` `.warn`) `.formula-head` `.formula-row` `.formula-term`(`.strong` `.emerald` `.red` `.teal` `.muted`) `.t-label` `.t-value` `.t-sub` `.formula-op` `.formula-caption` |
| 툴팁 | `.tooltip`(`.wide`) `.tip-anchor`(`.red` `.amber`) `.tip-panel` `.tip-row`(`.sum`) `.tip-green` |
| 토스트 | `.toast` + `.toast-success` `.toast-error` `.toast-info` |
| 모달 | `.modal-backdrop`(`.blur`) `.modal`(`.md`) `.modal-simple` `.modal-icon`(`.danger` `.warning` `.info`) `.modal-title` `.modal-desc` `.modal-actions` `.modal-header` `.modal-body` `.modal-footer` `.close` |
| 안내 | `.notice`(`.notice-red` `.notice-amber` `.notice-violet`) `.terms-note` `.tn-title` |
| 유틸 | `.text-muted` `.text-red` `.empty` `.count` `.active` |

**`base.css` 미수록 = 개별 파일 인라인 정의**(재사용 시 승격 후보, §7 M-3/M-4/L-3):
`.state-flag` · `.state-badge` · `.empty-state` 계열 · `.chk` · `.selected` · `.notice-green` · `.sign-row` · `.action-bar` · `.sel-count` · `.doc-link` · `.file-link` · `.tbl-head` · `.tbl-head-bar` · `.tbl-foot-note` · `.total-row` · `.base-date` · `.card-head` · `.stat-grid` · `.stat` · `.ty-split` · `.ty-label` · `.avg-note` · `.chip-row` 계열 · `.dd` 계열 · `.datepicker`/`.dp-*` · `.login-*` · `.pw-*` · `.done-*` · `.link-*` · `.cert-*` · `.doc-*` · `.spin-*`/`.step-*` · `.url-box` · `index.html`의 `.hero`/`.gallery`/`.shot-*`.

### 2-4. `assets/sheet.css` (5,516 B, 클래스 25개)

엑셀 미리보기 전용. `xls-*` 4개 파일만 `base.css` 뒤에 추가 로드.
`.back-link` `.file-bar` `.fb-left` `.fb-icon` `.fb-name` `.fb-meta` `.dot` `.sheet-frame` `.sheet-tabs` `.sheet-tab`(`.active`) `.sheet-scroll` `.sheet` `.col-head` `.corner` `.row-head` `.c-title` `.c-head` `.c-num` `.c-note` `.c-empty` `.r` `.r-total` `.sheet-caption`.
스프레드시트 격자 회색은 전역 오염 방지를 위해 `.sheet-frame` 스코프 로컬 토큰으로 정의(파일 상단 주석 명시).

### 2-5. `assets/template.html` · `assets/components.html`

| 파일 | 용도 | 상태 |
|---|---|---|
| `template.html` (6,270 B) | 신규 화면 스켈레톤. 루트에 `<화면명>.html`로 복사해 시작. 상단 주석에 사용법·메뉴 ID 7종 명시. 사이드바 전문 + 빈 `.page-header` + `<!-- CONTENT -->` 슬롯 | 현행 화면과 사이드바 동일. 유효 |
| `components.html` (16,783 B) | 컴포넌트 갤러리. `base.css`만 로드, 사이드바 없음. 12개 섹션(지표카드·뱃지·버튼·검색필터·키워드검색·토글/탭·테이블·산식·툴팁·토스트·모달·안내)에 마크업 견본 + 클래스 사용법을 h2에 서술 | 투자자 화면 신설 컴포넌트 미등재(§7 M-8) |

`components.html`의 데모 전용 클래스 `.demo-section` `.demo-inline-modal` `.demo-inline-toast` `.demo-tip-open`은 실화면 복사 금지 대상(파일 내 주석 명시).

---

## 3. 엑셀 다운로드 ↔ `assets/xlsx/` 대응

버튼 → 미리보기 화면 → 실제 파일까지 3단 연결. 파일 4개 전건 존재 확인, 미리보기 화면에 표기된 크기도 실제 바이트와 일치.

| 원 화면 | 버튼 위치 | 미리보기 화면 | xlsx 파일 | 실제 크기 | 화면 표기 |
|---|---|---|---|---|---|
| `invest-assets.html` | `현황` 카드 헤드 | `xls-assets-status.html` | `assets/xlsx/투자자산_현황_20260827.xlsx` | 5,812 B | 5.7 KB · 시트 1개 |
| `invest-assets.html` | `가맹점별 투자자산` 카드 헤드 | `xls-assets-merchant.html` | `assets/xlsx/가맹점별_투자자산_20260827.xlsx` | 6,161 B | 6.0 KB · 시트 1개 |
| `invest-profit.html` | `수익 현황` 카드 헤드 | `xls-profit-status.html` | `assets/xlsx/투자수익_현황_20260827.xlsx` | 5,560 B | 5.4 KB · 시트 1개 |
| `invest-profit.html` | `일별 투자수익` 카드 헤드 | `xls-profit-daily.html` | `assets/xlsx/일별_투자수익_20260827.xlsx` | 5,934 B | 5.8 KB · 시트 1개 |

`계약기록`의 `선택 문서 다운로드`는 xlsx가 아니라 PDF 묶음 개념이며 대응 파일·미리보기 화면 없음(상태 `contracts--downloaded`의 토스트로만 표현).

---

## 4. 인터랙션 목록 및 상태 전이 매핑

기호: **→** 대응 상태/화면 존재 · **✗** 상태 없음(대응 파일 부재) · `#` 앵커 자리표시자.

### 4-1. 공통 사이드바 (32개 화면 전건 동일, 9개 컨트롤)

| 컨트롤 | 유형 | 이동 | 비고 |
|---|---|---|---|
| 로고 `PayHug Investor` | link | ✗ (`href="#"`) | 대시보드 미정의 |
| 투자 자산 | nav | → `invest-assets.html` | |
| 투자 수익 | nav | → `invest-profit.html` | |
| 가맹점 | nav | → `merchants.html` | |
| 정산채권 양수 | nav | → `acquisition.html` | 목적지가 모달 열린 상태 (H-1) |
| 계약기록 | nav | → `contracts.html` | |
| 쿠콘 관리 현금 | nav | → `coocon.html` | `.ext` 아이콘 표기(실제 이동은 내부 화면) |
| 비밀번호 변경 | nav | → `password.html` | |
| 로그아웃 | button | ✗ | `login.html` 존재하나 미연결 (L-2) |

### 4-2. `index.html` — 8개

`shot-card` ×8 → `invest-assets` / `certificate` / `invest-profit` / `coocon` / `merchants` / `acquisition` / `contracts` / `password`.
`login.html`·`xls-*` 4종·상태 20종은 갤러리 미등재(H-3).

### 4-3. `login.html` — 4개

| 컨트롤 | 유형 | 이동 |
|---|---|---|
| 사업자등록번호 또는 휴대전화번호 | text input | — |
| 비밀번호 | password input | — |
| 로그인 | button | ✗ (성공 후 진입 화면 미지정) |
| 비밀번호 찾기 | link | ✗ (`#`) |

### 4-4. `invest-assets` 계열 — 기본 6 + 상태 6

| 화면 | 컨트롤 | 유형 | 이동 |
|---|---|---|---|
| `invest-assets` | 엑셀 다운로드(현황) | link.btn-excel | → `xls-assets-status.html` |
| `invest-assets` | 엑셀 다운로드(가맹점별) | link.btn-excel | → `xls-assets-merchant.html` / 완료상태 → `invest-assets--download.html` |
| `invest-assets` | 증명서 다운로드 | link.btn-outline | → `certificate.html` / 확인단계 → `invest-assets--cert-confirm.html` |
| `invest-assets` | 페이지네이션 `1` · `‹` · `›` | button ×3 | → `invest-assets--page2.html` |
| `--page2` | 페이지네이션 `1` `2`(active) `‹`(활성) `›`(disabled) | button ×4 | → `invest-assets.html` (1페이지 복귀) |
| `--page2` / `--download` / `--cert-confirm` | 엑셀 다운로드 ×2 | button (링크 아님) | ✗ (M-2) |
| `--download` | 엑셀 버튼 `다운로드 완료`(`.is-done`) | button | ✗ (완료 표시 전용) |
| `--cert-confirm` | 모달 닫기 `close` | button | → `invest-assets.html` |
| `--cert-confirm` | 취소 | button.btn-outline | → `invest-assets.html` |
| `--cert-confirm` | 발급 | button.btn-primary | ✗ (`certificate.html` 이 대응 결과이나 미연결, M-2) |
| `--empty` | 엑셀 ×2 · 증명서 ×1 | button disabled ×3 | — |

### 4-5. `certificate.html` — 2개

| 컨트롤 | 유형 | 이동 |
|---|---|---|
| `투자 자산` 뒤로가기 | link.back-link | → `invest-assets.html` |
| PDF 다운로드 | button.btn-primary | ✗ (다운로드 완료 상태 미정의, M-6) |

### 4-6. `invest-profit` 계열 — 기본 11 + 상태 파생

| 화면 | 컨트롤 | 유형 | 이동 |
|---|---|---|---|
| `invest-profit` | 프리셋 `어제` | button.preset-btn | ✗ |
| `invest-profit` | 프리셋 `일주일`(active) | button.preset-btn | 현재 상태 |
| `invest-profit` | 프리셋 `이번달` | button.preset-btn | → `invest-profit--monthly.html` (프리셋·기간 동시 전환) |
| `invest-profit` | 시작일 / 종료일 | date input ×2 | → `invest-profit--datepicker.html` |
| `invest-profit` | 검색 | button.btn-primary | 결과 0건 → `invest-profit--empty.html` |
| `invest-profit` | 초기화 | button.btn-outline | → `invest-profit.html` |
| `invest-profit` | 엑셀 다운로드(수익 현황) | link.btn-excel | → `xls-profit-status.html` |
| `invest-profit` | 엑셀 다운로드(일별) | link.btn-excel | → `xls-profit-daily.html` |
| `invest-profit` | 토글 `일별`(active) / `월별` | button.toggle-btn ×2 | → `invest-profit--monthly.html` |
| `--datepicker` | 이전 달 / 다음 달 | button.dp-nav ×2 | ✗ |
| `--datepicker` | 날짜 셀 1~31 (+ blank 6) | button.dp-cell ×37 | ✗ (범위 21~27 고정 표기) |
| `--monthly` / `--datepicker` | 엑셀 ×2 | button (링크 아님) | ✗ (M-2) |
| `--empty` | 엑셀 ×2 | button disabled ×2 | — |

### 4-7. `merchants` 계열 — 기본 8 + 상태 파생

| 화면 | 컨트롤 | 유형 | 이동 |
|---|---|---|---|
| `merchants` | 업종 | select (option 2: 전체·음식점업) | → `merchants--filter-open.html` |
| `merchants` | 채권매입업체 | select (option 2) | ✗ |
| `merchants` | 검색어 | text input | ✗ |
| `merchants` | 검색 | button.btn-primary | → `merchants--filtered.html` / 0건 → `merchants--empty.html` |
| `merchants` | 초기화 | button.btn-outline | → `merchants.html` |
| `merchants` | 목록 행 `tr.clickable` ×8 | row click | ✗ (가맹점 상세 화면 미정의) |
| `merchants` | 페이지네이션 `‹` `1` `›` | button ×3 | ✗ (1페이지 고정) |
| `--filter-open` | `.dd-trigger` | div click | 열림 상태 |
| `--filter-open` | `.dd-opt` ×5 (전체·음식점업(hover)·도소매업·서비스업·기타) | div click | → `merchants--filtered.html` |
| `--filtered` / `--empty` | 조건 칩 해제 ×2 | button[aria-label=조건 해제] | ✗ |
| `--filtered` / `--empty` | 조건 초기화 `.chip-clear` | button | → `merchants.html` |
| `--empty` | 빈 상태 `조건 초기화` | button.btn-outline | → `merchants.html` |

### 4-8. `acquisition` 계열 — 서명 플로우

| 화면 | 컨트롤 | 유형 | 이동 |
|---|---|---|---|
| `--list` | 체크박스 ×3 | checkbox | → `acquisition.html` (2건 선택 상태) |
| `--list` | 계약서 보기 ×3 | link | ✗ (`#`) |
| `--list` | 서명하기 (disabled) | button | — |
| `acquisition` | 서명하기 (활성) | button | 확인 모달 열림 = 현재 화면 자체 |
| `acquisition` | 모달 닫기 `close` | button | → `acquisition--list.html` |
| `acquisition` | 취소 | button.btn-outline | → `acquisition--list.html` |
| `acquisition` | 서명 진행 | button.btn-primary | → `acquisition--signing.html` |
| `--signing` | 서명 진행 중 (disabled) | button | → `acquisition--done.html` (자동 전이) |
| `--done` | 계약기록 보기 | link.btn-outline | → `contracts.html` |
| `--done` | 확인 | button.btn-primary | ✗ (`acquisition--list.html` 복귀가 자연스러우나 미연결) |
| `--done` | 계약서 보기 ×2(서명완료 행) | link | → `contracts.html` |
| `--done` | 계약서 보기 ×1(대기 행) | link | ✗ (`#`) |

### 4-9. `contracts` 계열

| 화면 | 컨트롤 | 유형 | 이동 |
|---|---|---|---|
| `contracts` | 전체선택 체크박스(thead) | checkbox | → `contracts--all.html` |
| `contracts` | 행 체크박스 ×8 (3건 checked) | checkbox | → `contracts--all.html` |
| `contracts` | 선택 문서 다운로드 | button.btn-excel | → `contracts--downloaded.html` |
| `contracts` | 재양도합의서 PDF 링크 ×8 | link | ✗ (`#`) |
| `contracts` | 페이지네이션 `‹` `1` `›` | button ×3 | ✗ |
| `--all` | 선택 문서 다운로드 (8) `.armed` | button | → `contracts--downloaded.html` |
| `--empty` | 선택 문서 다운로드 (disabled) | button | — |
| `--empty` | 정산채권 양수로 이동 | link.btn-outline | → `acquisition.html` |

### 4-10. `coocon` 계열

| 화면 | 컨트롤 | 유형 | 이동 |
|---|---|---|---|
| `coocon` | We-bank 바로가기 | link.btn-primary `target=_blank` | 외부 `https://www.we-bank.co.kr/main_00100.act` / 확인단계 → `coocon--confirm.html` |
| `--confirm` | 모달 닫기 `close` | button | → `coocon.html` |
| `--confirm` | 취소 | button.btn-outline | → `coocon.html` |
| `--confirm` | 이동 | link.btn-primary `target=_blank` | 외부 We-bank |

### 4-11. `password` 계열

| 화면 | 컨트롤 | 유형 | 이동 |
|---|---|---|---|
| `password` | 현재/새/새 확인 비밀번호 | password input ×3 | 규칙 위반 → `password--weak.html`, 확인값 불일치 → `password--error.html` |
| `password` | 변경하기 | button.btn-primary | → `password--done.html` |
| `--weak` / `--error` | 변경하기 (disabled) | button | — |
| `--done` | 로그인 화면으로 | link.btn-primary | → `login.html` |

### 4-12. `xls-*` 4종 (각 3개)

| 컨트롤 | 유형 | 이동 |
|---|---|---|
| 뒤로가기 (`투자 자산` / `투자 수익`) | link.back-link | → `invest-assets.html` / `invest-profit.html` |
| 엑셀 파일 내려받기 | link `download` | → `assets/xlsx/*.xlsx` (§3 표) |
| 시트 탭 ×1 (active) | tab | 단일 시트 |

---

## 5. 증명서 플로우 확정

```
invest-assets.html
  └ [증명서 다운로드] 클릭
      └ invest-assets--cert-confirm.html   (발급 확인 모달: 문서명·기준일 2026-08-27·대상 가맹점 8개·작성자 ㈜페이허그)
          ├ [취소] / [닫기] → invest-assets.html
          └ [발급]          → certificate.html   ※ 모달의 [발급] 버튼에 href 없음 — 코드상 미연결
                              certificate.html
                                ├ [PDF 다운로드] → 상태 없음
                                └ [투자 자산]    → invest-assets.html
```

`invest-assets.html`의 `증명서 다운로드` 버튼은 확인 모달을 건너뛰고 `certificate.html`로 직접 연결되어 있음. 확인 모달 경유가 정본이면 링크 대상을 `invest-assets--cert-confirm.html`로 바꿔야 함(M-5).

## 6. 서명 플로우 확정

```
acquisition--list.html          선택 0건 · [서명하기] disabled
  └ 체크박스 2건 선택
      └ acquisition.html        선택 2건(1행 김성호떡볶이 · 3행 바다마루) + 서명 확인 모달 열림
          ├ [취소]/[닫기]       → acquisition--list.html
          └ [서명 진행]
              └ acquisition--signing.html   선택 2건(1행 김성호떡볶이 · 2행 달빛곱창) ← 대상 불일치(H-2)
                   하나은행 인증서 서명 모달: 스피너 + 3단계(완료/진행중/대기)
                   └ 자동 전이
                       └ acquisition--done.html   1·2행 서명 완료 뱃지 + 체크박스 disabled
                            완료 모달: 2건 목록(김성호떡볶이·달빛곱창)
                            ├ [계약기록 보기] → contracts.html
                            └ [확인]          → 상태 없음
```

서명 완료 후 계약기록 연결: `acquisition--done.html`의 완료 행 `계약서 보기`도 `contracts.html`로 향함. 역방향으로 `contracts--empty.html`이 `정산채권 양수로 이동` CTA로 `acquisition.html`을 가리켜 두 화면이 상호 참조.

---

## 7. 결함 목록

### High

**H-1. `acquisition.html`의 기본/상태 역전 — `acquisition.html:130,150` (선택 행), `acquisition.html:90~115` (모달 블록), `template.html:36`·`index.html`(shot-card)·전 32화면 사이드바의 `href="acquisition.html"`**
파일명 규칙상 `<화면>.html`은 기본 상태여야 하나, `acquisition.html`은 2건 선택 + 서명 확인 모달이 열린 상태로 배포됨. 상태 마커(`.state-flag`/`.state-badge`)도 없어 기본 화면으로 오인됨. 실제 기본 상태는 `acquisition--list.html`(선택 0건)에 있음. 사이드바 `정산채권 양수` 메뉴와 랜딩 카드가 모두 모달 열린 화면으로 착지. `app.html`에서는 `acquisition--list`를 기본으로, 확인 모달을 상태로 뒤집어 조립할 것.

**H-2. 서명 플로우 대상 가맹점 불연속 — `acquisition.html:130,150` vs `acquisition--signing.html:164,173` vs `acquisition--done.html:155,164`**
확인 모달은 `김성호떡볶이 본점`(1행) + `바다마루 횟집`(3행)을 선택 대상으로 명시하나, 이어지는 `--signing`은 1행 + `달빛곱창 홍대점`(2행)을, `--done`도 1·2행을 서명 완료 처리. 데모 워크스루에서 선택 대상이 도중에 바뀜. `app.html`은 1·2행 기준으로 통일하거나 확인 모달을 1·2행으로 정정할 것.

**H-3. 상태 파일 20개 전건 인바운드 링크 0 — 20개 상태 파일 전체**
본문 영역 링크 그래프 실측 결과, 20개 상태 파일 어느 것도 다른 화면에서 링크되지 않음. `index.html` 갤러리는 8개 기본 화면만 등재하고 `login.html`·`xls-*` 4종·상태 20종을 누락. 결과적으로 파일을 직접 열지 않으면 도달 불가. `login.html`의 유일한 인바운드는 `password--done.html`.

### Medium

**M-1. 상태 마커 클래스 이원화 — 20개 상태 파일**
- `.state-flag` 계통 7개: `acquisition--list:121`, `acquisition--signing:148`, `acquisition--done:139`, `coocon--confirm:122`, `merchants--empty:125`, `merchants--filter-open:124`, `merchants--filtered:115` — 회색 pill 고정, 색 구분 없음.
- `.badge .state-badge` 계통 13개: `contracts--*` 3, `invest-assets--*` 4, `invest-profit--*` 3, `password--*` 3 — `badge-gray/green/amber/red/primary`로 의미 색 구분.
동일 목적 컴포넌트가 두 벌. 추가로 `.state-badge`의 CSS 정의도 두 형태(`invest-*` 계열은 `.page-title .state-badge`, `contracts`/`password` 계열은 `.state-badge`)로 갈림. 어느 쪽도 `base.css` 미수록.

**M-2. 상태 파일에서 엑셀·발급 버튼의 링크 소실 — `invest-assets--page2:79,138` · `invest-assets--download:82` · `invest-assets--cert-confirm:88,144` · `invest-assets--empty:89,121` · `invest-profit--monthly:70,114` · `invest-profit--datepicker:166,…` · `invest-profit--empty:80,124`**
기본 화면은 `<a class="btn btn-excel" href="xls-*.html">`이나, 상태 파일 7개에서 전부 `<button class="btn btn-excel">`로 치환되어 목적지가 사라짐. `invest-assets--cert-confirm`의 `[발급]` 버튼도 `certificate.html` 미연결. 상태 화면에서 진입하면 프로토타입이 막다른 길이 됨.

**M-3. 빈 상태 마크업 3종 병존 — `invest-assets--empty:38~45` · `invest-profit--empty:34~42` · `merchants--empty`(빈 상태 블록) · `contracts--empty:33~42`**
같은 `.empty-state` 아래 하위 클래스가 제각각: `es-icon/es-title/es-sub`(invest 계열 2개), `empty-icon/empty-title/empty-desc`(merchants), `empty-ico/empty-title/empty-desc`(contracts). `base.css` 미수록이라 파일마다 재정의. `merchants--empty`만 CTA 버튼(`조건 초기화`)을 포함.

**M-4. 동일 필터 컨트롤의 구현 이원화 — `merchants:22~24`(select) vs `merchants--filter-open:…`(`.dd` div 구조)**
업종 필터가 기본·`--filtered`·`--empty`에서는 네이티브 `<select>`, `--filter-open`에서만 커스텀 `.dd/.dd-trigger/.dd-menu/.dd-opt` div 구조. 통합 시 한쪽으로 정리 필요.

**M-5. 증명서 확인 모달 우회 — `invest-assets.html:149`**
`증명서 다운로드`가 `certificate.html`로 직행. 확인 모달 상태(`invest-assets--cert-confirm.html`)를 거치지 않아 §5 플로우가 화면 링크로는 성립하지 않음.

**M-6. 목적지 없는 주요 CTA 4건**
`certificate.html`의 `PDF 다운로드`, `login.html`의 `로그인`, `acquisition--done.html`의 `확인`, `invest-assets--cert-confirm.html`의 `발급`. 모두 결과 상태 파일 부재.

**M-7. 옵션 세트 불일치 — `merchants.html:22`(업종 select) vs `merchants--filtered`·`merchants--empty`(동 select)**
기본 화면의 업종 select는 `전체`·`음식점업` 2개만, 상태 파일은 `전체`·`음식점업`·`도소매업`·`서비스업`·`기타` 5개. `--filter-open`의 `.dd-menu`도 5개. 기본 화면만 결손.

**M-8. `assets/components.html` 갱신 누락**
투자자 화면 신설 컴포넌트가 갤러리에 미등재: 빈 상태, 조건 칩(`.chip-row`), 달력 팝오버(`.datepicker`), 서명 행(`.sign-row`)·하단 액션바(`.action-bar`), 엑셀 시트(`.sheet-*`), 로그인 폼(`.login-*`), 비밀번호 폼(`.pw-*`), 상태 마커, 커스텀 드롭다운(`.dd`). 사이드바 섹션도 없음(사이드바 견본은 `template.html` 전용).

**M-9. `README.md` 현행 미반영**
"화면 8종 + 랜딩" · 화면 목록 9행 · 구조 트리에 `sheet.css`·`xlsx/` 누락 · `logo-icon.png`를 여전히 사용 자산으로 표기 · 상태 파일 20개와 `login.html`·`xls-*` 4종 미등재. 변경 이력도 최초 제작 1건에서 멈춤(로고 data URI 전환 커밋 미반영).

### Low

**L-1. 로고 자산 고아화 — `assets/logo-icon.png` (43,134 B)**
`.logo-mark` data URI 전환(커밋 `5ccfa3f`) 이후 34개 HTML 전건에서 `logo-icon.png` 참조 0건. `base.css`에 base64 57,512자로 내장되어 정상 렌더. 파일 자체는 미사용 잔존. **로고 렌더 실패 사례는 34개 파일 전건에서 없음** — `.logo-mark` 적용 누락 0건 확인(`index.html`·`login.html`은 2회 사용, 나머지 32개는 사이드바 1회).

**L-2. 사이드바 로그아웃·로고 링크 미연결 — 32개 파일 전건**
`로그아웃` 버튼에 목적지 없음(`login.html` 존재). 로고 `<a href="#">`도 목적지 없음.

**L-3. 인라인 CSS 중복 정의**
`.state-badge` 5회, `.state-flag` 7회, `.notice-green` 4회(acquisition 4파일), `.empty-state` 4회, `.modal-guide` 2회(`coocon--confirm`, `acquisition--signing`), `.back-link` 2회(`certificate.html` 인라인 + `sheet.css`), `.tbl-head` 6회, `.chk`·`.selected` 각 7회. 통합 시 전부 `base.css` 승격 대상.

**L-4. `notice` 색 변형 결손 — `base.css`**
`.notice-red`·`.notice-amber`·`.notice-violet`만 정의. acquisition 4파일이 쓰는 `.notice-green`은 미정의이므로 각 파일 인라인.

**L-5. 앵커 자리표시자 `href="#"` 다수**
`contracts` 계열 PDF 링크 8개 ×3파일, `acquisition` 계열 `계약서 보기` 3개 ×3파일, `login.html` 비밀번호 찾기 1개, 사이드바 로고 32개.

**L-6. 카운트 표기 방식 불일치 — `contracts.html:46` vs `contracts--all.html:52~53`**
기본 화면은 인라인 style span으로 `총 8건 · 선택 3건`, 상태 파일은 `.tbl-count` + `.badge.sel-pill`로 `총 8건` + `8건 선택`. 같은 위치·같은 정보의 표현이 두 벌.

**L-7. 뷰포트 고정**
34개 전건 `<meta name="viewport" content="width=1440">`. 반응형 없음(1440 목업 전제). `app.html`도 동일 전제를 유지할지 명시 필요.

**L-8. `login.html`에 h1 없음**
34개 중 유일하게 `<h1>` 미사용. 문서 구조 관점 접근성 결손이며, 인벤토리 자동 수집 시 화면명 누락 원인.

### 결함 없음이 확인된 항목

- 사이드바 메뉴 어긋남: **0건** (32개 파일 nav 블록 MD5 완전 일치)
- 정의되지 않은 CSS 클래스 사용: **0건** (전 파일 사용 클래스가 `base.css`/`sheet.css`/자체 인라인 중 하나에 정의)
- 깨진 내부 링크(존재하지 않는 `.html` 참조): **0건**
- `assets/xlsx/` 참조 파일 부재: **0건** (4개 전건 존재, 표기 크기도 실제와 일치)
- 로고 렌더 실패: **0건**
