# 투자자 어드민 배포 경로 실측 검증

- 대상 로컬 레포: `/Users/semi/cursor/payhug-investor-admin/` (읽기 전용 검증, 파일 수정·커밋·push 없음)
- 대상 라이브: `https://joo2n.github.io/payhug-investor-admin/`
- 원격 상태: `Joo2n/payhug-investor-admin` `main` = `5ccfa3f` — 화면 8 + 랜딩만 배포
- Pages 설정 실측: `status=built`, `build_type=legacy`, `source={branch:main, path:/}`, `public=true`, `https_enforced=true`, `custom_404=false`
- **실측 시각 2026-08-27 16:28 KST**. 이 시각 이후에도 다른 조가 `index.html` 등을 편집 중이므로, 아래 파일 목록·참조 검사는 해당 시점 스냅샷 기준

판정 등급: **치명** = 배포 즉시 깨짐 · **주의** = 동작은 하나 결함 노출 · **정상** = 문제 없음 · **검증 불가** = 사유 명기

---

## §1 라이브 현황

### 1-1 HTTP 상태 (curl 실측)

| 경로 | 상태 | Content-Type | 크기 |
|---|---|---|---|
| `/` · `/index.html` | 200 | text/html; charset=utf-8 | 8,860 |
| `/merchants.html` | 200 | text/html | 11,122 |
| `/contracts.html` | 200 | text/html | 12,136 |
| `/certificate.html` | 200 | text/html | 14,027 |
| `/coocon.html` | 200 | text/html | 9,218 |
| `/acquisition.html` | 200 | text/html | 10,838 |
| `/invest-assets.html` | 200 | text/html | 18,230 |
| `/invest-profit.html` | 200 | text/html | 16,851 |
| `/password.html` | 200 | text/html | 7,140 |
| `/assets/base.css` | 200 | text/css | 88,562 |
| `/assets/logo-icon.png` | 200 | image/png | 43,134 |
| `/login.html` | 404 | — | 미배포(로컬 전용) |
| `/assets/sheet.css` | 404 | — | 미배포(로컬 전용) |

배포된 8장 + 랜딩 전부 200. **정상**

### 1-2 렌더·CSS 적용

헤드리스 크롬(`--headless=new`, 창 미표시, 1440×1000) 9장 전량 스크린샷 성공(51KB~157KB). 캡처본 위치 `<scratchpad>/live/*.png`.

`invest-assets.html` 육안 확인 결과 — 사이드바 `#1B2537` 배경, primary 그린 버튼, Noto Sans KR 한글, 표 우측정렬 숫자 모두 정상 적용. CSS 미적용(FOUC·기본 스타일) 징후 없음. **정상**

### 1-3 하위 리소스 전수 검사

라이브 9페이지에서 `href`·`src` 상대참조를 추출해 라이브 URL로 개별 요청. **비200 응답 0건.** **정상**

### 1-4 로고 `.logo-mark`

라이브 `assets/base.css`에 `data:image/png;base64` 1건 존재, `.logo-mark { … }` 규칙 2건 존재. 스크린샷 좌상단에 PayHug 그린 로고 렌더 확인. **정상**

- 라이브 `base.css` ≡ `HEAD:assets/base.css` (diff 0)
- 로컬 작업본은 `.formula-grid` / `.formula-caption` 3줄 추가분만 앞섬 → 미배포 델타

### 1-5 콘솔 오류

전 HTML에 `<script>`·`fetch`·`XMLHttpRequest`·`@import` **0건**(grep 전수). 따라서 스크립트 기인 콘솔 오류는 구조적으로 발생 불가. 리소스 404도 §1-3에서 0건.

단, 로컬 서버 액세스 로그 실측에서 브라우저가 `/favicon.ico`를 요청함. 라이브 `https://joo2n.github.io/favicon.ico` → **404**. favicon 선언(`rel="icon"`)한 HTML **0개**. → 전 페이지 콘솔에 favicon 404 1건씩 상시 노출. **주의**

### 1-6 부수 관찰 (배포와 무관한 콘텐츠 결함)

`invest-assets.html` 라이브 스탯 타일 라벨이 `ty수익율`(소문자 ty·`수익율`)인 반면 같은 화면 표 헤더는 `TY수익율`. 표기 불일치. 배포 경로 문제가 아니므로 판정 대상 외로 두되, 담당 조 전달 권장.

---

## §2 GitHub Pages 제약 실측

### 2-1 `.xlsx` 다운로드 — **정상(조건부)**

우리 레포의 `assets/xlsx/`는 미배포이므로 직접 실측 불가. 동일 조건(GitHub Pages, legacy 빌드)을 만족하는 **타 Pages 사이트의 실제 `.xlsx` 응답**으로 대체 실측.

실측 대상: `https://putianxi.github.io/assets/data/hospital.xlsx`

```
HTTP/2 200
server: GitHub.com
content-type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
accept-ranges: bytes
content-length: 573926
```

본문 매직바이트 `50 4b 03 04`(PK zip), `file` 판정 `Microsoft Excel 2007+`. → **Pages는 `.xlsx`를 정확한 MIME으로, 바이너리 무손상으로 서빙한다.**

보강 근거(같은 계정 Pages):
- `https://joo2n.github.io/payhug-tool/guide/guide-pdf.pdf` → `content-type: application/pdf`, 1,032,965 bytes
- `https://joo2n.github.io/payhug-investor-admin/assets/logo-icon.png` → `content-type: image/png`

로컬 파일 실측: 4개 전부 `Microsoft Excel 2007+`, 5,560~6,161 bytes, 합계 32KB.

| 파일 | 크기 |
|---|---|
| `assets/xlsx/가맹점별_투자자산_20260827.xlsx` | 6,161 |
| `assets/xlsx/일별_투자수익_20260827.xlsx` | 5,934 |
| `assets/xlsx/투자수익_현황_20260827.xlsx` | 5,560 |
| `assets/xlsx/투자자산_현황_20260827.xlsx` | 5,812 |

**미검증 잔여분**: Pages 응답에 `content-disposition` 헤더가 없다. 따라서 저장 파일명은 전적으로 `<a download>` 속성에 의존한다. 현재 HTML은 값 없는 `download`(빈 속성)를 쓰므로 브라우저가 URL 마지막 세그먼트를 파일명으로 채택한다. 동일 출처이므로 `download`는 무시되지 않는다. 다만 **한글 파일명 + 값 없는 `download` 조합의 실제 저장 파일명**은 우리 파일이 배포되기 전에는 재현 불가 → **배포 후 확인 필요**(§4-4 체크리스트 D-3).

### 2-2 대소문자 구분 — **정상**

전 HTML·CSS의 `href`·`src` 참조 문자열을 실제 파일명과 **바이트 단위 대소문자 비교**(Python `os.walk` 인덱스 대조).

- 해석 성공 상대참조: **333건**
- **대소문자 불일치: 0건**
- 대상 파일 부재: 11건 → §2-6에서 별도 판정

macOS 대소문자 미구분 파일시스템에 기댄 참조는 없다.

### 2-3 한글 파일명 — **정상**

| 검사 | 결과 |
|---|---|
| 로컬 4개 파일명 유니코드 정규화 | 전부 **NFC** (NFD 아님) |
| HTML `href` 안의 파일명 정규화 | **NFC** — 실제 파일명과 바이트 동일 |
| HTML 참조 형태 | **원문 한글 그대로**, 퍼센트 인코딩 없음 (예: `href="assets/xlsx/투자자산_현황_20260827.xlsx"`) |

Pages의 한글 경로 서빙 실측(같은 계정, 동일 legacy 빌드):

- `https://joo2n.github.io/payhug-member-hub/회원관리_계약체인_구조서.html` → **200**
- `https://joo2n.github.io/payhug-member-hub/구조서_버전/2026-08-19_v1.html` → **200** (한글 디렉터리 포함)
- 퍼센트 인코딩 형태로 요청해도 **200**

→ 한글 파일명·한글 디렉터리 모두 Pages에서 정상 서빙된다. 브라우저는 raw 한글 `href`를 자동으로 UTF-8 퍼센트 인코딩해 요청하고, Pages는 양쪽 형태를 모두 해석한다.

**남는 위험 1건**: NFC/NFD. macOS에서 만든 파일이 NFD로 커밋되면 Pages(리눅스, 바이트 그대로 매칭)에서 404가 난다. 현재 4개 파일과 HTML 참조가 **모두 NFC로 일치**하므로 안전하나, 향후 파일명 변경 시 재검사 필요. `git config core.precomposeunicode`가 켜져 있으면 자동 NFC 커밋된다.

### 2-4 절대경로 참조 — **정상**

- `href="/…"` · `src="/…"` 형태: **0건**
- 프로토콜 상대(`//host/…`): **0건**
- CSS `url(/…)`: **0건** (`base.css`의 유일한 `url()`은 data URI)

전부 상대경로이므로 `/payhug-investor-admin/` 하위 경로에서 정상 해석된다. 실측 보강: 로컬 HTTP 서버에 `/payhug-investor-admin/` 하위 경로를 재현하고 헤드리스 크롬으로 진입 → 서버 액세스 로그가 `/payhug-investor-admin/assets/base.css` 200, `/payhug-investor-admin/assets/sheet.css` 200으로 기록됨.

### 2-5 `.nojekyll` — **불필요(단, 권장)**

| 검사 | 결과 |
|---|---|
| `.nojekyll` 존재 | **없음** |
| Pages 빌드 방식 | `build_type: legacy` → **Jekyll이 실제로 돈다** |
| `_` 로 시작하는 파일·디렉터리 | **0건** |
| `.`·`#` 시작, `~` 종료 파일 | **0건** (`.git` 제외) |
| Liquid 구문 `{{ }}` / `{% %}` | **0건** |
| `.md` 앞머리(YAML front matter) | `README.md`·`DESIGN_REF.md` 둘 다 **없음** |

Jekyll의 기본 제외 규칙(`_`·`.`·`#` 시작, `~` 종료)에 걸리는 파일이 하나도 없고 Liquid 충돌도 없다. `.md`는 front matter가 없어 변환 대상이 아니며, 실측상 라이브 `README.md`가 `content-type: text/markdown`으로 원문 그대로 서빙된다.

같은 계정·같은 legacy 빌드의 `payhug-member-hub`가 `.nojekyll` 없이 한글 파일명을 정상 서빙하는 선례도 확인됨.

**판정**: 현재 파일 구성에서는 `.nojekyll`이 없어도 깨지지 않는다. 다만 빌드 시간 단축과 향후 `_`로 시작하는 파일 추가 시의 사고 예방 목적으로 추가를 권장한다(비용 0, 부작용 없음).

### 2-6 존재하지 않는 대상 참조 — **치명 2건 + 주의 1건**

§2-2 검사에서 나온 "대상 부재" 11건의 내역.

| 참조 대상 | 참조원 | 판정 |
|---|---|---|
| `glossary.html` | `index.html:141` | **치명** — 로컬·원격 어디에도 없고 `README.md`에도 미언급. push 시 랜딩에서 404 |
| `capability.html` | `index.html:148` | **치명** — 동상. 랜딩 "기능 명세" 카드가 404 |
| `app.html` | `index.html:131` | **주의** — 다른 조가 제작 중. 완성 전 push하면 랜딩 최상단 진입 카드가 404 |
| `assets/base.css`, `acquisition.html`, `contracts.html`, `coocon.html`, `invest-assets.html`, `invest-profit.html`, `merchants.html`, `password.html` (8건) | `assets/template.html` | **주의** — 스캐폴딩 파일이 루트 기준 경로를 쓰는데 자신은 `assets/` 안에 있어 `assets/assets/base.css`·`assets/merchants.html`로 해석됨. 이미 라이브에 배포되어 있고, 열면 스타일 없는 깨진 페이지가 나온다 |

`assets/components.html`의 `href="base.css"`는 같은 디렉터리 기준이라 **정상 해석**된다(`assets/base.css`).

`index.html`의 `login.html` 참조와 `password--done.html`의 `login.html` 참조는 로컬에 파일이 있으므로 push 시 해소된다.

### 2-7 외부 리소스 — **주의**

전 HTML·CSS에서 발견된 외부 호스트는 **3종뿐**.

| 호스트 | 횟수 | 성격 | 판정 |
|---|---|---|---|
| `https://fonts.googleapis.com` | 74 | 스타일시트 + preconnect | 정상 (Pages에서 로드됨, 스크린샷 한글 렌더 확인) |
| `https://fonts.gstatic.com` | 36 | preconnect (폰트 파일 원본) | 정상 |
| `https://www.we-bank.co.kr` | 4 | `<a target="_blank" rel="noopener">` 외부 이동 링크 + 화면 표기 텍스트 | 리소스 아님, 렌더 영향 없음 |

- Google Fonts 외 외부 **리소스** 참조 없음. CDN 스크립트·외부 이미지·아이콘 폰트 전무(아이콘은 인라인 SVG).
- **주의 사유**: 폰트가 유일한 외부 의존이라, 사내망 차단이나 Google Fonts 장애 시 한글 폰트가 시스템 폴백으로 떨어진다. `font-family` 폴백 스택이 지정돼 있는지 담당 조 확인 권장.
- `we-bank.co.kr`은 쿠콘 화면의 의도된 외부 이동이며 `rel="noopener"` 처리됨.

### 2-8 부수 실측

| 항목 | 결과 | 판정 |
|---|---|---|
| Pages 404 페이지 | `custom_404: false` — 없는 경로는 GitHub 기본 404 | 주의(브랜딩 없음, 기능상 무해) |
| 캐시 헤더 | `cache-control: max-age=600`, `etag` 있음 | 배포 후 검증 시 캐시 우회 필요(§4-4) |
| `assets/logo-icon.png` | 43,134 bytes, 참조하는 HTML **0개**(`README.md`도 "미사용" 명기) | 주의 — 미사용 자산이 배포됨 |
| 배포 총량 | 레포 1.6MB (xlsx 4종 합 32KB) | 정상 (Pages 한도 1GB / 파일당 100MB 대비 무시 가능) |

---

## §3 통합본 `app.html` 배포 적합성 — 위험 목록

`app.html`은 실측 시각 기준 **미생성**이므로 파일 자체 검증은 불가. 아래는 Pages 환경에서 이 설계가 깨질 수 있는 지점의 사전 목록이며, 각 항목에 실측으로 확정한 사실을 근거로 붙인다.

### R-1 해시 라우팅 — 성립 (실측)

**결론: 성립한다.** URL 프래그먼트는 서버로 전송되지 않으므로 Pages는 `/payhug-investor-admin/app.html` 하나만 서빙하면 된다. 하위 경로라는 사실이 해시 라우팅에 영향을 주지 않는다.

실측: `/payhug-investor-admin/app.html#invest-assets/empty`로 헤드리스 진입 → 서버 로그에 `GET /payhug-investor-admin/app.html 200` 단 1건, 해시는 미전송.

**단, 다음으로 바뀌면 즉시 깨진다.**
- History API(`pushState`)로 `/payhug-investor-admin/invest-assets/empty` 같은 경로형 URL을 쓰면, 새로고침·직접 진입 시 Pages가 해당 파일을 찾지 못해 404. Pages에는 SPA 리라이트 기능이 없다(정적 서버). → **해시 방식을 유지할 것.**
- 경로형이 필요하면 Pages에서는 `404.html`을 SPA 폴백으로 두는 우회밖에 없고, 현재 `custom_404: false`이므로 별도 작업 대상.

### R-2 상대경로 CSS·xlsx 해석 — 성립 (실측)

**결론: 성립한다.** 상대 URL은 프래그먼트를 제외한 문서 URL 기준으로 해석된다.

실측: `/payhug-investor-admin/app.html#invest-assets/empty`에서 `href="assets/base.css"`·`href="assets/sheet.css"`가 각각 `GET /payhug-investor-admin/assets/base.css 200`, `GET /payhug-investor-admin/assets/sheet.css 200`으로 해석됨.

**깨질 수 있는 조건:**
- `<base href="/">`를 넣으면 전 상대참조가 `joo2n.github.io` 루트로 튀어 전멸한다. → **`<base>` 태그 금지.**
- 해시에 `../`나 `/`가 포함되는 라우트 문법(`#/invest-assets/empty` 등)을 쓰더라도 상대 URL 해석에는 영향 없으나, 자바스크립트에서 `location.href + 'assets/…'` 같은 문자열 연결로 경로를 만들면 해시가 섞여 잘못된 URL이 된다. → 경로 조립은 문자열 연결 대신 상대 URL 그대로 쓰거나 `new URL(p, location.pathname)` 사용.
- xlsx 링크가 자바스크립트로 동적 생성될 경우 한글 파일명을 그대로 넣어도 무방하나(§2-3), `encodeURIComponent`를 **경로 전체**에 걸면 `/`까지 인코딩돼 404가 된다. → 세그먼트 단위로만 인코딩하거나 인코딩하지 않을 것.

### R-3 직접 링크 진입 시 초기 상태 복원 — 미검증 위험

`app.html#invest-assets/empty`로 **직접 진입**하는 경로에서 흔히 깨지는 지점.

- 초기화 로직이 `hashchange` 이벤트에만 걸려 있으면, 최초 로드는 `hashchange`를 발생시키지 않으므로 기본 화면이 뜬다. → 로드 시점에 `location.hash`를 1회 읽어 라우팅하는 코드 필요.
- 인라인 `<script>`가 `<head>`에 있고 DOM 조작을 하면 대상 노드가 아직 없어 실패한다. → `defer` 또는 `</body>` 직전 배치.
- 해시가 한글 상태명을 담으면 브라우저가 퍼센트 인코딩한다. `location.hash`는 **인코딩된 문자열**을 돌려주므로 `decodeURIComponent` 없이 문자열 비교하면 매칭 실패. → 라우트 키는 ASCII(`invest-assets/empty`)로 고정하는 편이 안전.
- 존재하지 않는 해시(`#nope`)로 진입했을 때의 폴백 정의 필요. 정의가 없으면 빈 화면.
- 뒤로가기/앞으로가기 시 `hashchange`로 상태가 되돌아가는지. 모달 상태를 해시에 넣었다면 뒤로가기가 모달만 닫아야 한다.

### R-4 단일 파일 규모

화면 14 + 상태 20을 한 파일에 담으면 수백 KB 규모가 된다. Pages 파일당 한도 100MB·사이트 1GB이므로 **한도 문제는 없다**. 다만 `cache-control: max-age=600`(실측)이라 갱신 후 10분간 브라우저 캐시에 옛 버전이 남을 수 있다. 시연 직전 배포 시 캐시 우회 필요(§4-4).

### R-5 엑셀 실제 내려받기

`<a download>`는 **동일 출처에서만** 존중된다. `app.html`과 `assets/xlsx/`는 같은 출처이므로 동작한다. Pages는 `content-disposition`을 주지 않으므로(§2-1) 저장 파일명은 `download` 속성값이 결정한다.

- 값 없는 `download`: URL 마지막 세그먼트 = 한글 파일명. → **배포 후 실제 저장명 확인 필요.**
- 값 있는 `download="투자자산_현황_20260827.xlsx"`: 명시값이 우선하며 브라우저가 파일시스템 금지문자만 치환. 파일명을 확정하고 싶다면 이쪽이 안전.
- `Blob` + `URL.createObjectURL`로 만들어 내려받는 방식이면 Pages 제약과 무관하게 동작한다.

### R-6 Jekyll 상호작용

`app.html`에 인라인 스크립트가 들어가면서 `{{ }}` 또는 `{% %}` 문자열(템플릿 리터럴, 정규식, 객체 리터럴 중괄호 연속)이 생기면 legacy Jekyll 빌드가 Liquid로 해석해 **빌드 실패 또는 내용 삭제**를 일으킨다. 현재 레포에는 0건이지만 통합본은 유일하게 스크립트를 가진 파일이 되므로 위험이 새로 생긴다.

→ **`app.html` 추가와 동시에 `.nojekyll`을 함께 커밋하는 것이 안전하다.** (§2-5의 "권장"이 여기서 "필요"로 올라간다.)

### R-7 참조 무결성

랜딩 `index.html`이 이미 `app.html`·`glossary.html`·`capability.html`을 링크한다(§2-6). 통합본만 만들고 나머지 2개를 만들지 않으면 랜딩에 404 카드 2개가 남는다.

---

## §4 배포 실행 계획

### 4-1 커밋 대상 집계 (실측 시각 기준)

`git status --porcelain` = **38건** (신규 27 · 수정 11). 신규 HTML 25, 수정 HTML 9.

| 구분 | 내역 |
|---|---|
| 신규 상태 화면 20 | `acquisition--{confirm,signing,done}` · `contracts--{all,downloaded,empty}` · `coocon--confirm` · `invest-assets--{page2,download,cert-confirm,empty}` · `invest-profit--{monthly,datepicker,empty}` · `merchants--{filter-open,filtered,empty}` · `password--{weak,error,done}` |
| 신규 화면 1 | `login.html` |
| 신규 엑셀 미리보기 4 | `xls-assets-status` · `xls-assets-merchant` · `xls-profit-status` · `xls-profit-daily` |
| 신규 자산 5 | `assets/sheet.css` · `assets/xlsx/` 4개 |
| 수정 9 | `index.html` · `README.md` · `assets/base.css` · `assets/template.html` · 기존 화면 7(`acquisition` `certificate` `contracts` `invest-assets` `invest-profit` `merchants` `password`) |
| 미생성(선행 필요) | `app.html` · `glossary.html` · `capability.html` |

### 4-2 커밋 단위 제안 — 4분할

한 덩어리로 묶으면 38건이 단일 커밋이 되어 되돌리기 단위가 사라진다. 성격이 다른 4묶음으로 나누기를 제안한다. **순서가 중요하다** — 랜딩(`index.html`)은 아직 없는 파일 3개를 링크하므로 마지막에 둔다.

**커밋 1 — 엑셀 미리보기·다운로드 자산**
```
git add assets/sheet.css assets/xlsx xls-assets-status.html xls-assets-merchant.html \
        xls-profit-status.html xls-profit-daily.html
```
> 엑셀 미리보기 화면 4종 + 내려받기 대상 xlsx 4종 — 시트 전용 스타일 sheet.css 분리

**커밋 2 — 상태 화면 20 + 로그인**
```
git add login.html *--*.html
```
> 화면 상태 20종 + 로그인 화면 — `<화면>--<상태>.html` 명명 규칙 적용

**커밋 3 — 기존 화면 정정 + 공용 스타일**
```
git add acquisition.html certificate.html contracts.html invest-assets.html \
        invest-profit.html merchants.html password.html assets/base.css assets/template.html
```
> 기본 화면 7종 상태 정정 및 산식 카드 2열 그리드 토큰 추가 — acquisition 기본 상태를 목록으로 환원

**커밋 4 — 통합 프로토타입·랜딩·문서 (선행 조건 충족 후)**
```
git add app.html glossary.html capability.html index.html README.md .nojekyll
```
> 통합 프로토타입 app.html 및 랜딩 전량 등재 구조 — 해시 딥링크 라우팅, 용어 사전·기능 명세 동반

**커밋 4의 선행 조건 3가지**
1. `app.html` 완성
2. `glossary.html`·`capability.html` 생성 — 또는 `index.html`에서 해당 카드 2개 제거
3. `.nojekyll` 추가 (R-6 — `app.html` 인라인 스크립트의 Liquid 오인 차단)

**대안(단일 커밋)**: 세 파일이 모두 완성될 때까지 기다렸다가 38+건을 한 번에 올리는 방식. 되돌리기 단위가 사라지고 랜딩·화면·자산 문제가 섞여 원인 분리가 어려워지므로 **비권장**. 커밋 1~3은 랜딩과 무관하게 지금 올려도 라이브가 깨지지 않는다(현재 라이브 `index.html`은 이들을 링크하지 않으므로 노출되지 않을 뿐 무해).

### 4-3 push 후 Pages 빌드 확인 방법과 대기 시간

**대기 시간(실측 근거)**

| 레포 | 빌드 소요 |
|---|---|
| `payhug-investor-admin` (직전 빌드 `5ccfa3f`) | **40,996 ms** (06:22:25 생성 → 06:23:05 완료) |
| `payhug-support` 최근 5회 | 39,326 / 32,285 / 82,071 / 41,411 / 32,683 ms |

→ **통상 30초~90초.** 파일이 34개 늘어나므로 상한 쪽(60~90초)을 잡을 것. 2분을 넘기면 실패를 의심한다.

**확인 방법 (읽기 전용 조회만)**
```bash
# 최근 빌드 상태·소요 — status 가 built 이면 완료, errored 면 실패
gh api repos/Joo2n/payhug-investor-admin/pages/builds/latest \
  --jq '{status, created_at, updated_at, duration, commit: .commit[0:7], error: .error.message}'

# 폴링 (약 2분 상한)
for i in $(seq 1 12); do
  gh api repos/Joo2n/payhug-investor-admin/pages/builds/latest --jq '.status + " " + .commit[0:7]'
  sleep 10
done
```
- 판정 기준: `status == "built"` **이면서** `commit`이 방금 push한 SHA와 일치해야 완료다. 직전 빌드가 그대로 `built`로 남아 있는 것을 완료로 오독하지 말 것.
- `status == "errored"`면 `.error.message`에 Jekyll 오류가 담긴다.
- 실패 시 GitHub이 커밋 작성자에게 빌드 실패 메일을 보낸다.
- **주의**: `gh api ... -X POST .../pages/builds`(빌드 강제 트리거)는 쓰기 호출이므로 이번 작업 범위 밖.

### 4-4 배포 후 검증 체크리스트

CDN·브라우저 캐시가 `max-age=600`(실측)이므로 **모든 검증 요청에 캐시 우회를 건다**.

```bash
BASE=https://joo2n.github.io/payhug-investor-admin
CB="?_=$(date +%s)"          # 캐시 버스터
```

**D-1 · 전 HTML 200 확인 (35개)**
```bash
cd /Users/semi/cursor/payhug-investor-admin
for f in *.html; do
  c=$(curl -s -o /dev/null -w '%{http_code}' -H 'Cache-Control: no-cache' "$BASE/$f$CB")
  [ "$c" = 200 ] || echo "FAIL $f -> $c"
done
```
기대: 출력 없음. 특히 `login.html`·`app.html`·`glossary.html`·`capability.html`·`xls-*.html` 4종.

**D-2 · 신규 자산 200 + MIME 확인**
```bash
curl -sI "$BASE/assets/sheet.css$CB"  | grep -i content-type   # → text/css
for x in assets/xlsx/*.xlsx; do
  curl -sI "$BASE/$x" | grep -iE 'HTTP/|content-type|content-length'
done
```
기대: 200 · `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` · 로컬과 동일한 바이트 수(5,560 / 5,812 / 5,934 / 6,161).

**D-3 · xlsx 실제 내려받기 (수동, §2-1 미검증분 해소)**

`https://joo2n.github.io/payhug-investor-admin/xls-assets-merchant.html`을 브라우저로 열고 `엑셀 다운로드` 클릭.
- [ ] 파일이 실제로 저장되는가 (새 탭에서 열리지 않고)
- [ ] 저장된 파일명이 `가맹점별_투자자산_20260827.xlsx` 그대로인가 (한글 깨짐·`download` 누락 없음)
- [ ] Excel/Numbers에서 정상 열리는가 (바이트 손상 없음)
- 나머지 3종도 동일 확인

**D-4 · 깨진 링크 전수 재검사**
```bash
for f in *.html; do
  curl -s "$BASE/$f$CB" | grep -oE '(href|src)="[^"#h][^"]*"' | sed -E 's/^(href|src)="//;s/"$//' \
  | sort -u | while read -r r; do
      c=$(curl -s -o /dev/null -w '%{http_code}' "$BASE/$r")
      [ "$c" = 200 ] || echo "BROKEN $f -> $r [$c]"
    done
done
```
기대: `assets/template.html` 기인 항목 외 출력 없음(§2-6 미수정 시 8건 잔존).

**D-5 · 렌더 확인 (헤드리스, 창 미표시)**
```bash
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
for p in index app login xls-assets-status invest-assets--empty merchants--filter-open; do
  "$CH" --headless=new --disable-gpu --hide-scrollbars --virtual-time-budget=6000 \
        --window-size=1440,1000 --screenshot="$p.png" "$BASE/$p.html"
done
```
기대: 전부 생성, 사이드바 `#1B2537`·그린 primary·한글 폰트 적용. `--user-data-dir`은 이 맥에서 헤드리스를 행(hang)시키므로 붙이지 말 것(실측).

**D-6 · 통합본 딥링크 (app.html 배포 시)**

브라우저 주소창에 직접 입력해 진입:
- [ ] `$BASE/app.html#invest-assets/empty` → 빈 상태 화면으로 복원되는가 (기본 화면이 뜨면 R-3 결함)
- [ ] `$BASE/app.html#merchants/filter-open` → 필터 열린 상태
- [ ] 진입 후 새로고침(F5) → 같은 상태 유지
- [ ] 사이드바로 3화면 이동 후 뒤로가기 3회 → 역순 복귀
- [ ] `$BASE/app.html#존재하지않는키` → 폴백 화면(빈 화면 아님)
- [ ] app.html에서 엑셀 다운로드 실동작

**D-7 · Jekyll 부작용**
```bash
curl -s "$BASE/app.html$CB" | grep -c '{{\|{%'   # 0이어야 함
curl -s "$BASE/app.html$CB" | wc -c              # 로컬 파일 크기와 일치해야 함
```
`.nojekyll`을 넣지 않고 push했다면 이 항목이 특히 중요하다.

**D-8 · 문서**
- [ ] `$BASE/README.md` 200, 갱신 내용 반영
- [ ] 랜딩(`$BASE/`) 카드 개수 = 실제 파일 수와 일치, 404 카드 없음

---

## §5 `README.md` 갱신 필요 항목

현행 `README.md`는 **이미 다른 조가 대폭 개정한 미커밋 상태**(+74줄)이며 `app.html`·상태 20종·엑셀 대응표까지 반영돼 있다. 아래는 그 개정본을 실측 결과와 대조해 남은 불일치를 항목화한 것이다. (지시대로 직접 수정하지 않음.)

### 5-1 사실관계 불일치 — 수정 필요

**A. 집계 수치 내부 모순 (7행 vs 50행)**
- 7행: `화면 14 · 상태 20 · 인터랙션 93 · 루트 HTML 35(통합본 app.html 포함)`
- 50행(구조 블록): `*.html  # 기본 화면 13 + 상태 20`
- 실측: 루트 HTML **34개** + 미생성 `app.html` = 35 ✓ / 상태(`--`) 파일 **20개** ✓ / 상태 아닌 화면 파일 14개(= `index` 1 + 기본 8 + `login` 1 + `xls-*` 4)
- → "화면 14"에 `index.html`(랜딩)이 포함된 반면 "기본 화면 13"에는 빠져 있다. **둘 중 하나의 기준으로 통일**할 것. 랜딩을 화면으로 세지 않는 편이 자연스러우므로 `화면 13 + 랜딩 1` 표기 권장.
- "인터랙션 93"의 산출 근거가 문서 어디에도 없다. 근거를 붙이거나 수치를 내릴 것.

**B. 없는 파일 2개가 문서에서 누락 — 랜딩과 불일치**
- `index.html`이 `glossary.html`(용어 사전)·`capability.html`(기능 명세)을 링크하는데 `README.md`는 **둘 다 미언급**.
- → 두 파일을 만들 계획이면 "하위 화면" 표와 "구조" 블록에 등재. 만들지 않을 계획이면 `index.html`의 카드 2개를 제거하고 README는 현행 유지.

**C. 미존재 파일을 확정 서술**
- 13~14행·49행이 `app.html`을 이미 존재하는 산출물처럼 서술하나 실측상 **미생성**.
- → `app.html` 완성 커밋과 **동시에** README를 올릴 것. README만 먼저 push하면 문서가 라이브 사실과 어긋난다.

**D. 구조 블록에 누락된 항목**
- `DESIGN_REF.md`가 레포에 존재하고 라이브에도 배포돼 있으나 구조 블록에 없음.
- `.nojekyll`을 추가한다면 구조 블록에 함께 등재.
- → 구조 블록에 두 줄 추가.

**E. `logo-icon.png` 처리 방침**
- 56행은 "미사용. 로고는 base.css의 .logo-mark data URI로 렌더"로 **정확히** 기술돼 있다(실측: 참조 HTML 0개).
- → 사실 서술은 맞으나, 43KB 미사용 자산을 계속 배포할지 판단이 필요하다. 삭제하면 이 줄도 함께 정리.

### 5-2 규율 대조 — 유지

**F. 변경 이력 (77~81행)**
- 프로젝트 규율(push마다 README에 날짜·변경내용 기록)에 부합. **유지.**
- 이번 push 시 새 항목 1줄 추가 필요. 커밋을 4분할하더라도 README 변경 이력은 배포 단위로 1줄이면 충분하다.
- 초안:
  > `- 2026-08-27 — 상태 화면 20종·로그인·엑셀 미리보기 4종 추가. 엑셀 내려받기 대상 xlsx 4종과 시트 전용 sheet.css 동반. 통합 프로토타입 app.html 및 해시 딥링크 라우팅 도입.`
- 변경 이력 외 본문은 현재 상태 서술체로 작성돼 있어 규율(변경이력체 금지)에 맞다. **유지.**

**G. 배포 제약 안내 부재 — 추가 권장**
- 실측으로 확정된 배포 관련 사실이 README에 없다. "참고" 절에 아래 3줄 추가 권장.
  - 한글 파일명은 **NFC**로 유지할 것 (NFD로 커밋되면 Pages에서 404)
  - 경로는 **전부 상대경로**로 유지할 것 (`/`로 시작하면 Pages 하위 경로에서 깨짐, `<base>` 태그 금지)
  - `app.html` 등 스크립트 포함 파일은 `{{ }}`·`{% %}` 문자열을 피하거나 `.nojekyll`을 유지할 것 (legacy Jekyll 빌드)

### 5-3 사실 확인 완료 — 수정 불필요

| 항목 | 실측 결과 |
|---|---|
| 5행 라이브 URL | 200 ✓ |
| 24~31행 화면·상태 매핑 8행 | 실제 파일과 전건 일치 ✓ |
| 37~41행 하위 화면 5개 | 파일 존재 ✓ |
| 43행 명명 규칙 `<화면>--<상태>.html` | 20개 전부 준수 ✓ |
| 62~67행 엑셀 대응표 4행 | HTML의 `href`와 실제 xlsx 파일명 전건 일치 ✓ |
| 52행 토큰 표기 (`#1B2537`, `#7FE141`) | `base.css` 실측 일치 ✓ |
| 74행 사이드바 메뉴 7종 | 화면 실측 일치 ✓ |

---

## 판정 요약

| 등급 | 건수 | 내역 |
|---|---|---|
| **치명** | 2 | `index.html` → `glossary.html` · `capability.html` (미존재, README에도 없음) |
| **주의** | 6 | `index.html` → `app.html`(미완성) / `assets/template.html` 깨진 참조 8건 / favicon 전 페이지 404 / Google Fonts 단일 외부 의존 / `logo-icon.png` 미사용 배포 / `custom_404` 없음 |
| **검증 불가** | 3 | 한글 xlsx `<a download>` 실제 저장 파일명(배포 후) · `app.html` 자체(파일 미생성) · 이번 push의 Pages 빌드 소요(과거 이력으로 대체 추정) |
