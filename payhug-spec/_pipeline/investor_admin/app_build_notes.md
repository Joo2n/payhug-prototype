# `app.html` 제작 지침

대상: `/Users/semi/cursor/payhug-investor-admin/app.html` (신규 단일 파일)
근거: `screen_inventory.md` (실측 인벤토리) · `app_spec.json` (기계 판독 사양)

---

## 0. 전제

1. **개별 HTML 34개는 그대로 보존한다.** Figma 네이티브 임포트(`3066:328` 투자자 어드민 페이지)용 원본이므로 `app.html` 제작 과정에서 수정·삭제하지 않는다. `app.html`은 신규 파일 1개 추가로만 성립한다.
2. `assets/base.css`·`assets/sheet.css`도 개별 HTML이 참조 중이므로 **삭제·구조 변경 금지**. 클래스 추가는 파일 하단 신규 섹션에 append 한다.
3. `app.html`의 목적은 화면 간·상태 간 이동을 한 파일 안에서 시연하는 것. 개별 파일은 정적 캡처본, `app.html`은 조작 가능한 프로토타입으로 역할을 나눈다.
4. 데이터·금액·요율·상호는 전부 예시값. 개별 파일의 수치를 그대로 옮기고 새로 만들지 않는다.

---

## 1. 조립 구조

### 1-1. 파일 골격

```
app.html
├ <head>
│  ├ meta viewport = width=1440           (개별 파일과 동일 전제, 결함 L-7)
│  ├ Google Fonts Noto Sans KR 400/500/600/700
│  ├ <link rel="stylesheet" href="assets/base.css">
│  ├ <link rel="stylesheet" href="assets/sheet.css">   ← 엑셀 화면 포함 위해 항상 로드
│  └ <style>  app 전용 + 승격 대상 클래스 (§2)
└ <body data-active="invest-assets">
   ├ <div class="page">
   │   ├ <aside class="sidebar"> …  1회만 (template.html 전문 그대로)
   │   └ <main class="content">
   │        └ <section class="screen" data-screen="…"> × 14
   ├ 모달 컨테이너 (4개)
   ├ 토스트 컨테이너 (2개)
   ├ 하단 액션바 (acquisition 전용)
   └ <script> 화면·상태 전환 로직
```

### 1-2. CSS 인라인 여부

**외부 링크 유지**(인라인 금지). 근거:
- `base.css`가 88.8 KB이고 로고 base64가 57,512자를 차지한다. 인라인 시 `app.html` 자체가 100 KB를 넘어 편집·diff가 어려워진다.
- 개별 파일이 이미 같은 상대 경로로 참조 중이라, `app.html`을 루트에 두면 경로가 그대로 맞는다.
- GitHub Pages 배포 경로도 동일.

`app.html` 전용 `<style>` 블록에는 다음만 둔다.
- 화면·상태 전환용 표시 제어(§3)
- §2의 승격 대상 클래스 (개별 파일 인라인 CSS를 한 벌로 정리한 것)
- `app.html` 전용 크롬(화면 선택 툴바 등)을 추가할 경우 그 스타일

### 1-3. 화면 단위

`app_spec.json`의 `screens[]` 14개를 각각 `<section class="screen" data-screen="<id>">`로 감싼다. `index`(랜딩 갤러리)와 `login`은 사이드바가 없으므로 `.page` 바깥의 별도 컨테이너에 두고, 활성화 시 `.page` 전체를 숨긴다.

- 사이드바 있는 화면 12개: `#invest-assets` `#certificate` `#xls-assets-status` `#xls-assets-merchant` `#invest-profit` `#xls-profit-status` `#xls-profit-daily` `#merchants` `#acquisition-list` `#contracts` `#coocon` `#password`
- 사이드바 없는 화면 2개: `#index` `#login`

---

## 2. 공통화 대상 (개별 파일 인라인 CSS → `app.html` `<style>` 1벌)

개별 파일에 흩어진 인라인 정의를 아래 규격으로 통일한다. `base.css`는 건드리지 않고 `app.html` `<style>`에만 둔다(개별 파일과의 렌더 차이를 만들지 않기 위해, 값은 원본을 그대로 옮긴다).

| 대상 | 통일 방침 | 원본 |
|---|---|---|
| 상태 마커 | `.state-badge` 계통(`.badge` + 색 조합)으로 단일화. `.state-flag`는 `.badge.badge-gray.state-badge`로 치환 | 결함 M-1 |
| 빈 상태 | `.empty-state > .empty-ico / .empty-title / .empty-desc` 로 단일화. `es-*` 계열 폐기 | 결함 M-3 |
| 알림 배너 초록 | `.notice-green` 1회 정의 | 결함 L-4 |
| 체크박스·선택 행 | `.chk`, `.selected` 1회 정의 | 결함 L-3 |
| 표 헤더/푸터 | `.tbl-head`(제목+우측 액션), `.tbl-head-bar`, `.tbl-foot-note`, `.total-row` 1회 정의 | 결함 L-3 |
| 카운트 표기 | `.tbl-count` + `.badge.sel-pill` 로 단일화. 인라인 style span 폐기 | 결함 L-6 |
| 기준일 pill | `.base-date` 1회 정의 | — |
| 수익 지표 | `.card-head` `.stat-grid` `.stat` `.ty-split` `.ty-label` `.avg-note` 1회 정의 | — |
| 조건 칩 | `.chip-row` `.chip` `.chip-label` `.chip-clear` 1회 정의 | — |
| 달력 | `.datepicker` `.dp-*` 1회 정의 | — |
| 커스텀 드롭다운 | `.dd` `.dd-trigger` `.dd-menu` `.dd-opt` 1회 정의 | — |
| 서명 화면 | `.sign-row` `.action-bar` `.sel-count` `.doc-link` `.spin-*` `.step-*` `.done-*` 1회 정의 | — |
| 모달 안내문 | `.modal-guide` 1회 정의 | 결함 L-3 |
| 뒤로가기 | `sheet.css`의 `.back-link` 사용. 인라인 재정의 금지 | 결함 L-3 |
| 증명서 | `.cert-layout` `.cert-main` `.cert-aside` `.doc-*` `.issue-*` `.sig-*` `.cert-desc` `.cert-info` 1회 정의 | — |
| 로그인·비밀번호 | `.login-*` `.pw-*` `.done-card` `.rule-list` `.err-msg` `.has-error` `.input-wrap` 1회 정의 | — |
| 쿠콘 | `.link-*` `.ref-*` `.url-box` 1회 정의 | — |
| 랜딩 | `.wrap` `.hero` `.gallery` `.shot-*` `.foot-note` 1회 정의 | — |

사이드바는 `template.html`의 `<aside class="sidebar">` 블록을 **문자 그대로** 옮긴다. 32개 파일에서 MD5 완전 일치가 확인됐으므로 임의 재작성 금지.

---

## 3. 화면 전환 방식

### 3-1. 화면 전환

`data-screen` 속성 + CSS 표시 제어. 프레임워크·번들러 없이 vanilla JS.

```js
function showScreen(id) {
  document.querySelectorAll('[data-screen]').forEach(el =>
    el.hidden = (el.dataset.screen !== id));
  document.body.dataset.active = MENU_OF[id] || '';   // 사이드바 활성 메뉴 동기화
  resetStates(id);                                     // 화면 진입 시 상태 초기화
  location.hash = id;                                  // 딥링크
}
```

- **사이드바 활성 표시는 `base.css`의 기존 기전을 그대로 쓴다.** `body[data-active]` 값만 갈아끼우면 CSS가 처리한다. `.nav-item.active` 클래스를 별도로 토글하지 말 것(이중 기전이 되어 어긋난다).
- `MENU_OF` 매핑은 `app_spec.json`의 `screens[].menu`를 그대로 옮긴다. `certificate`·`xls-assets-*`는 `invest-assets`, `xls-profit-*`는 `invest-returns`.
- `index`·`login`은 `menu: null` → `data-active=""` → 활성 메뉴 없음 + `.page` 숨김.
- `location.hash` 딥링크를 두면 개별 상태 검토·캡처가 쉬워진다. `#acquisition-signing` 같은 상태 id도 받도록 한다.

### 3-2. 상태 전환

상태는 **별도 섹션을 복제하지 않고**, 해당 화면 섹션 안에서 데이터 속성 하나로 갈아끼운다. 상태 파일 20개를 20개 섹션으로 옮기면 표 데이터가 20벌로 중복돼 유지가 불가능해진다.

```html
<section class="screen" data-screen="invest-assets" data-state="default">
```

```js
function setState(screen, state) {
  const sec = document.querySelector(`[data-screen="${screen}"]`);
  sec.dataset.state = state;
  renderStateMarker(sec, STATE_META[state]);   // h1 안 .state-badge 삽입/제거
}
```

CSS는 `[data-state]` 선택자로 분기한다.

```css
[data-screen="invest-assets"][data-state="empty"] .tbl-scroll  { display: none; }
[data-screen="invest-assets"][data-state="empty"] .empty-state { display: block; }
[data-screen="invest-assets"]:not([data-state="page2"]) .page-2-rows { display: none; }
```

**상태별 조립 방침**

| 상태 유형 | 해당 상태 | 구현 |
|---|---|---|
| 모달 열림 | `invest-assets-cert-confirm`, `acquisition-confirm`, `acquisition-signing`, `acquisition-done`, `coocon-confirm` | 모달 마크업 5벌을 `.page` 바깥에 미리 두고 `hidden` 토글. `.modal-backdrop`은 `base.css` 그대로 |
| 토스트 | `invest-assets-download`, `contracts-downloaded` | 토스트 2벌 미리 배치 + 표시 토글. 자동 소멸 타이머는 두지 않는다(검토용이라 계속 보여야 함) |
| 빈 상태 | `invest-assets-empty`, `invest-profit-empty`, `merchants-empty`, `contracts-empty` | 표 `.tbl-scroll` 숨김 + `.empty-state` 노출 + 지표값 0 치환 + 버튼 `disabled` |
| 데이터 교체 | `invest-assets-page2`, `invest-profit-monthly`, `merchants-filtered` | 두 벌의 `<tbody>`를 미리 두고 토글. JS로 행을 생성하지 않는다(캡처 재현성 확보) |
| 팝오버 | `invest-profit-datepicker`, `merchants-filter-open` | 팝오버 마크업을 해당 필드 안에 두고 토글. 달력 셀은 클릭 무반응(표기 전용) |
| 선택 상태 | `contracts-all`, `acquisition-confirm` | 체크박스 `checked` 일괄 토글 + `tr.selected`/`.sign-row.selected` 클래스 + 카운트 텍스트 갱신 |
| 폼 검증 | `password-weak`, `password-error`, `password-done` | `.pw-field.has-error` 토글 + 오류 문구·규칙 리스트 노출 + 버튼 `disabled`. `done`은 폼 전체를 `.done-card`로 교체 |

### 3-3. 결함 반영 사항 (조립 시 정정)

| 결함 | app.html 처리 |
|---|---|
| **H-1** | 사이드바 `정산채권 양수` → `acquisition-list`(선택 0건)를 기본으로. 확인 모달은 `data-state="confirm"` 상태로 종속 |
| **H-2** | 서명 대상을 **1행 김성호떡볶이 본점 + 2행 달빛곱창 홍대점**으로 통일. 확인 모달의 목록도 이 2건으로 표기 |
| **H-3** | 상태 20개 전건을 UI에서 도달 가능하게 한다. 추가로 화면 상단에 상태 전환 툴바(현재 화면의 상태 목록 버튼)를 두면 검토자가 클릭 한 번으로 순회 가능 |
| **M-2** | 엑셀 버튼은 상태와 무관하게 항상 `xls-*` 화면으로 이동. `empty` 상태에서만 `disabled` |
| **M-5** | `증명서 다운로드` → 확인 모달 → `[발급]` → `certificate` 순서로 연결 |
| **M-6** | `PDF 다운로드`·`로그인`·`확인`·`발급`에 동작 부여. `로그인` → `invest-assets`, `확인` → 모달 닫고 `acquisition-list` 복귀, `PDF 다운로드` → 토스트 표시 |
| **M-7** | 업종 select 옵션을 5개(전체·음식점업·도소매업·서비스업·기타)로 통일 |
| **L-2** | 사이드바 `로그아웃` → `login` 화면 |
| **L-5** | `href="#"` 자리표시자는 `<a href="#" onclick="return false">` 또는 `role="link" tabindex="0"`로 두어 페이지 점프를 막는다 |

### 3-4. 하지 말 것

- `<iframe>`으로 개별 파일 34개를 끌어오는 방식. 사이드바가 34벌 중복 렌더되고 활성 메뉴 동기화가 불가능하며, Figma 임포트와도 무관해진다.
- 상태별 섹션 복제(20개 섹션). 표 데이터가 중복돼 수치 정정 시 20곳을 고쳐야 한다.
- `base.css` 수정. 개별 파일 34개의 렌더가 동시에 바뀐다.
- 표 행의 JS 동적 생성. 정적 마크업으로 두어야 Figma 캡처·임포트가 가능하다.
- 새 아이콘·새 색·새 컴포넌트 도입. `DESIGN_REF.md` 실측값 밖의 값은 쓰지 않는다.

---

## 4. 주의점

1. **사이드바 활성 기전이 `base.css`에 하드코딩** — 메뉴 ID 7개(`invest-assets` `invest-returns` `merchants` `receivables` `contracts` `kcoon` `password`)가 `base.css:146~165` 셀렉터에 나열돼 있다. `app.html`에서 새 메뉴 ID를 만들면 활성 표시가 동작하지 않는다.
2. **`sheet.css`는 로컬 토큰 스코프** — 스프레드시트 격자 회색이 `.sheet-frame` 스코프 안에서만 정의된다. 엑셀 화면 마크업을 `.sheet-frame` 밖으로 꺼내면 격자가 사라진다.
3. **`.logo-mark`는 data URI** — 이미지 파일 참조가 아니므로 `assets/logo-icon.png` 없이도 렌더된다. `app.html`에서도 `<span class="logo-mark">`만 두면 된다(`<img>` 금지).
4. **`acquisition` 화면은 `main`에 `padding-bottom:120px`** — 하단 고정 액션바에 콘텐츠가 가리지 않게 하는 값. 화면 전환 시 다른 화면에 이 패딩이 남지 않도록 `[data-screen="acquisition-list"] .content` 스코프로 건다.
5. **모달·액션바는 `.page` 형제** — `base.css`의 `.modal-backdrop`이 `position:fixed`이므로 위치 자체는 어디 두든 같지만, `.content`의 `margin-left:240px` 영향을 받지 않도록 `.page` 바깥에 둔다. 개별 파일도 그렇게 되어 있다.
6. **`certificate`·`xls-*` 화면의 뒤로가기** — 사이드바 활성 메뉴는 각각 `invest-assets`/`invest-returns`로 유지된다. 화면 전환 시 `data-active`가 상위 메뉴를 가리키게 매핑을 정확히 옮길 것.
7. **`invest-assets` 헤더 변형** — 이 화면만 `.page-header.row-between` + `.base-date`. 다른 화면에 이 변형이 새지 않도록 스코프를 건다.
8. **산식 카드·용어 안내 블록은 `invest-assets`·`invest-profit` 두 화면에서 완전 동일** — 한 벌을 만들어 두 섹션에 복사하되, 값이 갈리지 않게 한 곳에서 관리한다.
9. **수치는 개별 파일 실측값 그대로** — 기준일 `2026-08-27`, 투자자산 `1,389,800,000`, 배분 요율 `0.11%`, 조달 이자율 `연 12%` 등. 새 값을 만들지 않는다. 요율은 `analysis/00_종합.md` C1 미확정 사안이므로 "예시" 표기(`.formula-caption`)를 반드시 유지한다.
10. **엑셀 파일 4개 실물 링크** — `assets/xlsx/*.xlsx` 상대 경로. `app.html`을 루트에 두면 그대로 동작한다.

---

## 5. 검증 체크리스트

### 5-1. 구조

- [ ] `app.html`이 루트에 있고, 기존 34개 HTML·`assets/` 전건 미변경 (`git status`로 확인)
- [ ] `assets/base.css`·`assets/sheet.css` diff 0
- [ ] 외부 CSS 링크 2개 + Google Fonts만 사용, 그 외 외부 의존 없음
- [ ] `<section data-screen>` 14개 존재, id가 `app_spec.json`의 `screens[].id`와 1:1

### 5-2. 화면 전환

- [ ] 사이드바 7개 메뉴 클릭 시 각 기본 화면 표시 + 해당 메뉴가 `#7FE141` 배경 + 소속 그룹 라벨이 `#7FE141`
- [ ] `정산채권 양수` 클릭 시 **모달 없는 목록 화면**(선택 0건)이 뜬다 (H-1 정정 확인)
- [ ] `certificate`·`xls-assets-*` 진입 시 사이드바 활성 = `투자 자산`
- [ ] `xls-profit-*` 진입 시 사이드바 활성 = `투자 수익`
- [ ] `index`·`login` 진입 시 사이드바가 보이지 않음
- [ ] `location.hash`로 14개 화면 + 20개 상태 전건 직접 진입 가능

### 5-3. 상태 전환 (20개 전건)

- [ ] `invest-assets`: page2 / download(토스트) / cert-confirm(모달) / empty
- [ ] `invest-profit`: monthly(토글+프리셋 동시) / datepicker(팝오버) / empty
- [ ] `merchants`: filter-open(드롭다운) / filtered(칩 2 + 1행) / empty(칩 2 + 빈 상태)
- [ ] `acquisition`: list(0건) → confirm(모달) → signing(스피너 3단계) → done(완료 모달)
- [ ] `contracts`: all(전건 선택 + `(8)` 라벨) / downloaded(2행 토스트) / empty(CTA)
- [ ] `coocon`: confirm(외부 이동 모달, 주소 표기)
- [ ] `password`: weak(규칙 4항목 ok2/ng2) / error(확인값 불일치) / done(완료 카드)
- [ ] 각 상태에서 `h1` 옆 상태 마커가 단일 규격(`.badge.state-badge`)으로 표시

### 5-4. 인터랙션 (93개)

- [ ] `app_spec.json`의 `interactions[]` 중 `target`이 `null`이 아닌 항목 전건이 실제로 이동
- [ ] `target: null` 항목은 클릭해도 페이지 점프·hash 변경이 일어나지 않음
- [ ] 엑셀 다운로드 4개 → 각 `xls-*` 화면 → `assets/xlsx/*.xlsx` 실제 다운로드 (§3 대응표와 파일명 일치)
- [ ] 서명 플로우에서 선택 대상 가맹점이 3단계 내내 **김성호떡볶이 본점 + 달빛곱창 홍대점**으로 유지 (H-2 정정 확인)
- [ ] 증명서 플로우: `증명서 다운로드` → 확인 모달 → `발급` → `certificate` (M-5 정정 확인)
- [ ] 모달 4종의 `닫기`·`취소`가 각각 원 화면으로 복귀
- [ ] `로그아웃` → `login`
- [ ] `password-done`의 `로그인 화면으로` → `login`
- [ ] `contracts-empty`의 `정산채권 양수로 이동` → `acquisition-list`
- [ ] `coocon` 외부 링크 2개가 `target="_blank" rel="noopener"` 유지

### 5-5. 시각 대조

- [ ] 1440px 뷰포트에서 14개 화면 + 20개 상태를 개별 HTML 원본과 나란히 놓고 픽셀 차이 확인. 사이드바 240px / 콘텐츠 padding 32px / 카드 radius 16px / 활성 메뉴 `#7FE141`
- [ ] 로고가 34개 원본과 동일하게 렌더 (data URI)
- [ ] 상태 마커 통일로 인해 원본과 색이 달라지는 7개 화면(`.state-flag` → `.badge`)은 의도된 차이로 기록
- [ ] 콘솔 에러 0건 (JS 예외·404 리소스)

### 5-6. 산출물 정합

- [ ] `README.md` 갱신: 화면 14 / 상태 20 / `app.html` 추가 / `sheet.css`·`xlsx/` 등재 / `login.html`·`xls-*` 등재 (결함 M-9)
- [ ] `assets/components.html`에 신설 컴포넌트 9종 등재 여부 판단 (결함 M-8)
- [ ] `assets/logo-icon.png` 처리 결정 — 삭제 또는 README에서 미사용 표기 (결함 L-1)
