# 투자자 어드민 전 화면 인터랙션 전수 감사

대조 축 — 기준(진실) `payhug-admin-web`(실 운영 어드민) · 보조 `payhug-merchant-web` ↔ 대상 `payhug-investor-admin`(`app.html` 정본 + 정적 낱장 35종).

본 문서의 대상은 **눌렀을 때·올렸을 때·집중했을 때 무엇이 일어나는가**와 **그 요소가 실제 프론트·스토리보드·대표 정의서에 근거가 있는가** 두 축이다. 색·타이포·간격 축은 `ui_fidelity.md`, 선행 동작 판정은 `behavior_parity.md`(80항목·D-1~D-15) 소관이며 이미 판정된 항목은 재계상하지 않는다.

---

## §0 판독 시각 · 방법 · 경계

| 항목 | 값 |
|---|---|
| 판독 시각 | **2026-08-28 17:40 ~ 18:05 KST** |
| 대상 스냅샷 | 17:40:33 시점 사본 36개 파일을 스크래치패드에 고정, **그 사본만 조작**. 원본은 읽기만 |
| 기준 레포 | `/Users/semi/cursor/payhug-admin-web` · `/Users/semi/cursor/payhug-merchant-web` — 읽기 전용, 워킹트리 변경 0건 |
| 조작 방식 | headless Chrome(`--headless=new`) + CDP `Input.dispatchMouseEvent`·`dispatchKeyEvent`로 **실제 마우스·키보드 발생**. 뷰포트 실측 1440×1600 |
| 다운로드 | CDP `Browser.setDownloadBehavior`로 실물 파일 수령 확인 |
| 콘솔 오류 | 전 화면 순회 결과 **0건** |

### 감사 중 대상 파일이 바뀐 사실

다른 조가 동시 작업 중이라 판독 도중 2개 파일이 갱신됐다. 아래 항목은 **지금 고쳐지는 중일 수 있다.**

| 파일 | 스냅샷(17:40:33) | 판독 종료 시점 라이브 |
|---|---|---|
| `app.html` | `4092f570704e` | `16569cc201f6` |
| `invest-assets.html` | `faddda33e50c` | `869dc367cdb7` |

`merchants*.html` · `contracts*.html` · `login.html` · `coocon*.html` 는 판독 구간 내 변경 0건.

### 중복 배제

다른 조 처리 중으로 지시된 7건 — 계약기록 전자서명 텍스트화 · 가맹점 정렬 머리글·`No`열 · 쿠콘 설명 삭제 · 증명서 고지·서명 배치 · 보기 갯수 드롭다운 · 투자 수익 기간 필터 · 비밀번호 화면 — 은 판정표에서 제외한다. `behavior_parity.md` D-1~D-15, `storyboard_coverage.md` 누락 목록, `fabrication_audit.md` B-14(로그인 계정 발급 안내 문구) 기판정 항목도 제외한다.

### 감사 규모

화면 **14종**(`invest-assets` `certificate` `invest-profit` `merchants` `acquisition-list` `contracts` `coocon` `password` `xls-*` 4종 `index` `login`) · 정적 낱장 **36파일** · 상태 **20여 종** · 판정 항목 **36건**.

판독 뒤 신설된 `invest-sim` 은 이 규모에 들어 있지 않다. 그 화면 단독 대조는 **§6**(판정 항목 20건)이다.

---

## §1 판정표

판정 5단계 — `불일치` · `임의생성` · `누락` · `개선(허용)` · `일치`. 심각도 순.

| # | 화면 | 요소 | 실제 프론트 | 우리 | 판정 | 근거 |
|---|---|---|---|---|---|---|
| 1 | merchants·contracts·invest-profit·invest-assets 빈 상태 | 빈 상태 마크업 구조 | 표 안 `<tr><td colSpan={N} class="px-5 py-16 text-center text-secondary">텍스트</td></tr>` 한 줄. 아이콘 0·버튼 0·일러스트 0 | 표 밖 `<div class="empty-state">` + SVG 아이콘 원형 배지 + 제목 + 행동 버튼 | **임의생성** | 기준 `app/manage/page.tsx:281-283` · `app/sales/page.tsx:121-123` · `app/inquiries/page.tsx:274-277` / 우리 `merchants--empty.html:180-185` · `contracts--empty.html:152-157` · `invest-profit--empty.html:204-206` |
| 2 | merchants 빈 상태 | 빈 상태 안 행동 버튼 | 없음. 빈 상태는 텍스트 전용 | `조건 초기화` 버튼 | **임의생성** | `merchants--empty.html:185` |
| 3 | contracts 빈 상태 | 빈 상태 안 이동 링크 | 없음 | `정산채권 양수로 이동` 링크 | **임의생성** | `contracts--empty.html:157` |
| 4 | merchants 빈 상태 | 0건일 때 페이지네이션 | `{totalPages > 1 && (…)}` — 0건·1페이지면 렌더 자체를 안 함 | 0건인데 페이지 버튼 `1` + 화살표 2개(비활성) 잔존 | **불일치** | 기준 `app/sales/[bizNo]/page.tsx:1241` / 우리 `merchants--empty.html:195` |
| 5 | contracts 빈 상태 | 0건일 때 보기 갯수 셀렉트 | 페이지네이션 블록 자체가 조건부라 0건이면 부재 | 0건인데 `보기 10/20/50` 셀렉트 표시 | **불일치** | `contracts--empty.html:144` |
| 6 | invest-assets | 전건이 1페이지에 들어올 때 페이지네이션 | 상동 — `totalPages > 1` 조건 | 보기 `50개` 선택 시 16행 전건 표시되는데 페이지 버튼 `1` + 화살표 2개 잔존 | **불일치** | 조작 실측(50개 선택 → 2번째 표 16행, 페이지 버튼 유지) |
| 7 | contracts·acquisition-list | 표 행 ARIA | `role=` 레포 전체 1건(그것도 `<div>`), `tabIndex` **0건**, `aria-*` 2건뿐 | `<tr role="checkbox" tabindex="0" aria-checked>` 45곳 | **임의생성** | 기준 전수 grep 결과(0건) / 우리 `contracts.html:151,159` · `app.html:2228,2310` |
| 8 | contracts·acquisition-list | `role="checkbox"` 적용 위치 | 해당 없음 | `<tr>`에 `checkbox` 롤 부여 — 행 시맨틱이 소거되어 스크린리더가 표의 행으로 읽지 않음. 규약상 `role="row"` + `aria-selected`가 맞음 | **불일치** | `contracts.html:151` |
| 9 | coocon | 상태 2종 파일 | 해당 없음 | `coocon.html` 과 `coocon--confirm.html` **바이트 동일**(sha256 `1ee946b5449e`). 상태 변형을 주장하나 같은 파일 | **불일치** | 스냅샷 해시 대조 |
| 10 | login | 비밀번호 칸 Enter | Enter로 제출(`onKeyDown` Enter, 폼 유효 시) | 제출 요소가 `<a href>` 이고 `<form>` 부재 — Enter 무반응, 로그인 불가 | **누락** | 기준 `app/login/page.tsx:90` / 우리 `login.html:61`(조작 실측: Enter 후 `/login.html` 유지) |
| 11 | login | `비밀번호 찾기` 링크 | 해당(스토리보드 S2 규정 요소) | 부재. 8/27 판독 시점에는 `login.html:62`에 존재했고 현재 소실 | **누락** | 스토리보드 S2 / `storyboard_coverage.md:245` ↔ 현행 `login.html:53-61` |
| 12 | 전 표 빈 상태 | 빈 상태 문구 | `검색 결과가 없습니다.` · `조회 결과가 없습니다.` · `해당 기간에 …이 없습니다.` | `검색 결과 없음` · `조회된 투자수익 없음` · `조회된 자산 구분 없음` — 실제 원문을 명사형으로 개작 | **불일치** | 기준 `app/manage/page.tsx:282` 외 35종 / 우리 `merchants--empty.html:184` · `invest-profit--empty.html:206`. **G-1 문체 게이트와 정면 충돌 — §3 참조** |
| 13 | invest-profit | 역전 범위 경고 문구 | `시작일은 종료일보다 이후일 수 없습니다.` | `시작일은 종료일보다 이후일 수 없음.` | **불일치** | 기준 `components/DateRangeFilter.tsx:14` / 우리 `app.html:675,2728` |
| 14 | merchants·contracts·invest-profit | 빈 상태 아이콘 클래스명 | 해당 없음 | 같은 요소에 화면마다 다른 이름 — `empty-icon` / `empty-ico` / `es-icon` | **불일치** | `merchants--empty.html:37` · `contracts--empty.html:32` · `invest-profit--empty.html:37` |
| 15 | merchants | 검색 입력 반응 방식 | 4개 목록 화면 전부 `onChange` 라이브 필터 — 버튼·Enter 불필요 | 타이핑만으로는 안 걸러지고 Enter 또는 `검색` 필요 | **불일치** | 기준 `app/manage/page.tsx:249-255`(핸들러 `onChange` 단독) / 우리 조작 실측(타이핑 직후 10행 유지 → Enter 후 1행). 단 스토리보드 S14가 `검색` 버튼을 규정 |
| 16 | 전 화면 | 화면 부제 `<p>` | 모든 최상위 화면에 `<h1>` 아래 한 문장 부제 필수(`text-secondary text-sm mt-1`) | 전량 부재 | **누락** | 기준 `app/manage/page.tsx:192` 외 11종. **D-23(화면 설명 0건) 확정과 충돌 — §3 참조** |
| 17 | 전 표 | 로딩 상태 | `로딩 중...` / `CommonLoading` | 없음 | 기판정 | `behavior_parity.md` D-10 — 재계상 제외 |
| 18 | merchants | 업종 필터 | 실제 어드민에 업종 필터 **부재**(업종은 상세 화면 읽기 전용 필드 1곳) | 네이티브 `<select>` 로 존재하며 정상 동작 | **일치** | 스토리보드 S14 `필터 업종 ∨ 채권매입업체 ∨` 명시(`storyboard_coverage.md:80`). 출처 A 충족 |
| 19 | merchants | 업종 필터 동작 | — | `음식점업` 선택 후 10행 유지 = **정상**. 데이터 16건이 전건 `음식점업`이라 걸러도 전건 통과 | **일치** | 조작 실측(1·2페이지 업종 열 전건 `음식점업`) |
| 20 | invest-profit | 기간 프리셋 라벨 | `오늘`·`어제`·`이번 주`·`지난 주`·`이번 달`·`지난 달`·`최근 3개월` 7종 | `일주일`·`금월` 2종 | **일치** | 스토리보드 S7 `프리셋 일주일 금월` 명시(`storyboard_coverage.md:54`). 출처 A 충족 |
| 21 | merchants·invest-profit | 조회 버튼 라벨 | **레포 전체에 `검색` 버튼 0건** — 항상 `조회` | `검색` | **일치** | 스토리보드 S7·S14 `버튼 검색 초기화` 명시(`:54`,`:80`). 출처 A 충족 |
| 22 | 전 모달 | Esc 닫기 | **없음** — 레포 전체 `Escape` 키 핸들러 0건 | 없음 | **일치** | 기준 `components/ConfirmDialog.tsx` 전문 / 우리 조작 실측(Esc 후 `state=confirm` 유지) |
| 23 | 전 모달 | 배경 클릭 닫기 | 있음(`onClick={onClose}` on backdrop + 패널 `stopPropagation`) | 있음 | **일치** | 기준 `components/ConfirmDialog.tsx:54-55` / 우리 조작 실측 |
| 24 | 전 모달 | `role="dialog"`·`aria-modal`·포커스 트랩 | 전부 없음 | 전부 없음 | **일치** | 기준 전수 grep / 우리 `.modal-backdrop` 속성 실측 |
| 25 | 전 모달 | 닫기 X 접근명 | `aria-label="닫기"` | `aria-label="닫기"` | **일치** | 기준 `components/PlatformLockAccountDetailDialog.tsx:121` / 우리 실측 |
| 26 | 전 화면 | 토스트 위치·색·소멸 | `fixed top-6 left-1/2 -translate-x-1/2` 상단 중앙, 3000ms 자동 소멸, 기본 duration에선 닫기 버튼 **미렌더**, success `bg-green-100 text-green-800` | 상단 중앙(centerX 721/1440), top 24px, 배경 `#dcfce7`, 글자 `#016630`, 닫기 버튼 없음, 3~4초 사이 소멸 | **일치** | 기준 `components/Toast.tsx:20-45` / 우리 실측 |
| 27 | 전 화면 | 토스트 `role` | `role`·`aria-live` 없음 | `role="status"` | **개선(허용)** | 우리 실측 |
| 28 | 전 표 | 페이지 화살표 접근명 | 아이콘 전용 chevron, `aria-label` 없음 | 아이콘 전용, `aria-label` 없음 | **일치** | 기준 `app/sales/[bizNo]/page.tsx:1241-1263` / 우리 실측 |
| 29 | 전 필터 | 드롭다운 구현 방식 | 전부 네이티브 `<select>` — 커스텀 드롭다운 0건 | 전부 네이티브 `<select>` | **일치** | 기준 34개 `<select>` 전수 / 우리 `merchants.html:107,111` |
| 30 | invest-profit | 날짜 입력 `min`/`max` | `max={dateTo}` · `min={dateFrom}` | 동일(`min=2026-08-21`/`max=2026-08-27` 실측) | **일치** | 기준 `components/DateRangeFilter.tsx:116,122` |
| 31 | invest-profit | 역전 범위 시 조회 버튼 | `disabled={isInvalidRange}` | `disabled=true` 실측 | **일치** | 기준 `components/DateRangeFilter.tsx:128` |
| 32 | invest-profit | 프리셋 `aria-pressed` | 있음 | 있음 | **일치** | 기준 `components/DateRangeFilter.tsx:99` |
| 33 | 전 표 | 엑셀 버튼 0건 시 비활성 | 대상 0건이면 `disabled` | 빈 상태 4화면 전부 `disabled=true` | **일치** | 기준 `ExcelDownloadButton.tsx` 호출부 6곳 / 우리 실측 |
| 34 | 전 화면 | 다운로드 실물 | Blob → `a[download]` | 링크 대상 파일 **전건 실존**, 실제 수령 확인(xlsx 1건·txt 3건) | **일치** | `assets/` 전수 존재 검증 + CDP 수령 |
| 35 | contracts·acquisition-list | 행 키보드 토글 | 행이 키보드 대상 아님 | Space·Enter 양쪽 토글, 토글 후 포커스 복귀, `aria-checked` 갱신 | **개선(허용)** | `app.html:2905-2921` / 조작 실측 |
| 36 | contracts | 클릭 가능 행 hover·포커스 | 클릭 행 `hover:bg-primary-50/30 transition-colors cursor-pointer` | hover `#f5fcee` α0.30 · `cursor:pointer` · `transition background-color .15s` · 포커스 `outline 2px #65c826` | **일치** | 기준 `app/manage/page.tsx:291` / 우리 실측. 포커스 링은 실제엔 없는 추가분 |

### 집계

| 판정 | 건수 |
|---|---|
| 임의생성 | 4 |
| 불일치 | 7 |
| 누락 | 3 |
| 개선(허용) | 2 |
| 일치 | 19 |
| 기판정 재계상 제외 | 1 |
| **합계** | **36** |

---

## §2 상위 10건 — 무엇을 어떻게 고칠 것인가

### 1. 빈 상태를 표 안 텍스트 한 줄로 되돌린다 (판정표 1·2·3)

현재 `<table>` **밖**에 `<div class="empty-state">` 를 두고 아이콘 배지·제목·행동 버튼을 쌓는다. 실제 어드민은 예외 없이 표 **안** `<tbody>` 의 한 행이다.

교체 형태 — 표 열 수만큼 `colspan` 을 채운 행 하나로:

```html
<tbody>
  <tr><td colspan="8" class="empty-cell">검색 결과가 없습니다.</td></tr>
</tbody>
```

`.empty-cell` 은 실제 어드민 `px-5 py-16 text-center text-secondary` 환산값(상하 패딩 64px·가운데 정렬·`--gray-500` 계열)만 갖는다. 삭제 대상 — SVG 아이콘 배지 3종(`empty-icon`·`empty-ico`·`es-icon`), `조건 초기화` 버튼(`merchants--empty.html:185`), `정산채권 양수로 이동` 링크(`contracts--empty.html:157`), `.empty-state` 관련 CSS 블록 전량. 적용처는 `merchants--empty` · `contracts--empty` · `invest-profit--empty` · `invest-assets--empty` 4개 낱장과 `app.html` 의 `emptyState()` 생성 함수.

### 2. 페이지네이션·보기 갯수를 `totalPages > 1` 로 가둔다 (판정표 4·5·6)

`emptyState` 이거나 `Math.ceil(rows/size) <= 1` 이면 페이지네이션 블록과 보기 갯수 셀렉트를 **렌더하지 않는다**. 실제 어드민은 `{totalPages > 1 && (…)}` 로 블록 전체를 조건부로 둔다(`app/sales/[bizNo]/page.tsx:1241`).

`app.html` 의 `pageBar()` 진입부에 `if(total <= 1) return '';` 를 두고, `psz()`/`sizeSel()` 도 같은 조건을 탄다. 정적 낱장은 `merchants--empty.html:195` 페이지 블록과 `contracts--empty.html:144` 보기 셀렉트를 지운다. 지금은 0건인 표 아래 비활성 화살표 2개와 `1` 버튼이 남아 조작할 것이 있는 것처럼 보인다.

### 3. `<tr>` 의 `role="checkbox"` 를 걷어낸다 (판정표 7·8)

`<tr>` 에 `checkbox` 롤을 주면 그 요소는 표의 행이 아니라 체크박스로 노출되어 행·열 관계가 통째로 사라진다. 실제 어드민은 `role`·`tabIndex` 를 아예 쓰지 않는다(레포 전체 `tabIndex` 0건).

두 갈래 중 하나를 택한다.

- **실제 어드민에 맞춘다(권장)** — `role`·`tabindex`·`aria-checked` 를 전부 제거하고 선택은 행 안 `<input type="checkbox">` 가 담당. 키보드 조작은 그 체크박스가 기본 제공.
- **접근성 추가분을 유지한다** — 롤을 `role="row"` + `aria-selected` 로 바꾸고 `tabindex` 는 행이 아니라 행 안 체크박스에 둔다.

적용처 45곳 — `contracts.html:151,159` 외 8행, `contracts--all/--downloaded`, `acquisition*.html` 4종, `app.html:2228,2310` 생성 문자열. Space·Enter 토글 자체는 정상 동작하므로(판정표 35) 핸들러 로직은 그대로 두고 속성만 교체한다.

### 4. `coocon--confirm.html` 을 실제 상태로 만들거나 폐기한다 (판정표 9)

`coocon.html` 과 바이트 단위로 같은 파일이다(sha256 `1ee946b5449e`). 상태 목록에는 2종으로 잡혀 있으나 열어 보면 구분이 없다. D-14가 쿠콘 설명 전량 삭제와 메뉴 클릭 즉시 이동을 확정했으므로, 확인 단계 자체가 사라졌다면 `coocon--confirm.html` 을 지우고 상태 목록·`index.html`·`archive.html` 에서 항목을 뺀다. 확인 단계를 남긴다면 We-bank 이동 직전 확인 모달이 열린 상태를 실제로 그린다.

### 5. 로그인 Enter 제출을 살린다 (판정표 10)

제출 요소가 `<a class="btn btn-primary login-submit" href="invest-assets.html">` 이고 `<form>` 이 없다. 비밀번호 칸에서 Enter를 눌러도 아무 일도 일어나지 않는다(실측: `/login.html` 유지). 실제 어드민은 Enter로 제출한다(`app/login/page.tsx:90`).

`<a>` 를 `<button type="submit">` 으로 바꾸고 두 입력을 `<form>` 으로 감싸 `submit` 에서 이동시키거나, 최소한 두 입력의 `keydown` 에서 Enter를 받아 같은 이동을 수행한다. `app.html` 의 `login` 화면도 동일.

### 6. `비밀번호 찾기` 링크를 복구한다 (판정표 11)

스토리보드 S2 규정 요소이며 8/27 판독 시점 `login.html:62` 에 존재했다. 현행 파일에는 `로그인` 앵커 하나뿐이다(`login.html:53-61`). 삭제 근거가 레지스터에 없으므로 복구 대상. 이동 대상 화면이 없다면 실제 가맹점 프론트 `app/find-password/page.tsx` 대응 위치로 두거나, 링크만 두고 비활성 처리 대신 담당자 안내 경로를 잡는다.

### 7. 빈 상태·검증 문구의 원문 채택 여부를 결정한다 (판정표 12·13)

실제 프론트에 **글자 그대로 존재하는 문자열**을 명사형으로 개작한 상태다.

| 실제 프론트 원문 | 현행 | 위치 |
|---|---|---|
| `검색 결과가 없습니다.` | `검색 결과 없음` | `merchants--empty.html:184` |
| `조회 결과가 없습니다.` | `조회된 투자수익 없음` | `invest-profit--empty.html:206` |
| `시작일은 종료일보다 이후일 수 없습니다.` | `시작일은 종료일보다 이후일 수 없음.` | `app.html:675,2728` |

G-1(`습니다` 종결 0건)과 감사 지시 10번(실제 프론트에서 그대로 가져온 문구는 예외)이 충돌한다. **어느 쪽을 우선할지 결정 대기.** 원문 채택으로 정하면 위 3종과 나머지 빈 상태 문구를 실제 어드민 문자열로 교체하고 G-1에 예외 조항을 붙인다. 현행 유지로 정하면 레지스터에 "화면 문구는 G-1 우선, 실제 원문과 의도적 상이" 를 명문화해 재지적을 막는다. 이 항목은 화면 전반에 걸쳐 있어 개별 수정 전에 방침부터 정하는 편이 싸다.

### 8. 빈 상태 아이콘 클래스명을 하나로 통일한다 (판정표 14)

같은 자리의 같은 요소가 화면마다 `empty-icon`(`merchants--empty.html:37`) · `empty-ico`(`contracts--empty.html:32`) · `es-icon`(`invest-profit--empty.html:37`) 세 이름을 쓴다. 상위 1번대로 아이콘 자체를 걷어내면 함께 소멸하므로 **1번과 묶어 처리**한다. 아이콘을 남기는 결정이 나올 경우에만 `empty-icon` 으로 통일하고 `assets/base.css` 로 올린다.

### 9. 가맹점 검색을 라이브 필터로 바꿀지 결정한다 (판정표 15)

실제 어드민 목록 4종은 전부 `onChange` 즉시 필터라 버튼이 필요 없다(`app/manage/page.tsx:249-255`). 현행은 타이핑만으로는 걸러지지 않고 Enter 또는 `검색` 을 눌러야 한다(실측: 타이핑 직후 10행 → Enter 후 1행).

다만 스토리보드 S14가 `검색` `초기화` 버튼을 명시하므로 버튼 제거는 근거와 충돌한다. **버튼을 유지한 채 입력 `onChange` 에도 필터를 걸면** 양쪽을 만족한다. `초기화` 는 그대로 둔다.

### 10. 화면 부제 부재를 레지스터에 명문화한다 (판정표 16)

실제 어드민은 예외 없이 `<h1>` 아래 한 문장 부제를 둔다(`app/manage/page.tsx:192` `가맹점 승인, 수수료 정책 설정 및 관리를 수행합니다.` 외 11종). 현행은 D-23(화면에 읽으라고 붙인 설명 0건) 확정에 따라 전량 없앤 상태다.

D-23은 사용자 확정이므로 **화면을 되돌리지 않는다.** 대신 "실제 어드민에는 화면당 부제 1문장이 있으나 D-23에 따라 의도적으로 제외" 를 `request_register.md` 에 적어, 실제 프론트 대조 때 누락으로 재분류되지 않게 한다.

---

## §3 결정 대기 2건

| 건 | 충돌 축 | 선택지 |
|---|---|---|
| 화면 문구 문체 | G-1(`습니다` 0건) ↔ 감사 지시 10번(실제 원문 예외) | (a) 실제 원문 채택 + G-1 예외 조항 / (b) 현행 명사형 유지 + 레지스터 명문화 |
| 화면 부제 | 실제 어드민 필수 요소 ↔ D-23(화면 설명 0건) | D-23 우선 확정 상태. 레지스터 명문화만 필요 |

---

## §4 DOM만 보면 결함으로 보이나 실제로는 정상인 것

선행 세션에서 업종 필터를 죽었다고 오판한 전례가 있어, 이번 판독에서 결함으로 보였다가 **조작 결과 정상으로 확인된 것**을 따로 남긴다.

| 현상 | 결함으로 보이는 이유 | 실제 |
|---|---|---|
| 업종 필터가 걸러도 10행 그대로 | 필터가 안 먹는 것처럼 보임 | **정상.** 데이터 16건이 전건 `음식점업` 이라 걸러도 전건 통과. 1·2페이지 업종 열 전수 확인 |
| 업종·채권매입업체 셀렉트 옵션이 `전체` 외 1개뿐 | 옵션 생성이 깨진 것처럼 보임 | **정상.** 예시 데이터의 실제 고유값이 각 1종. 옵션은 데이터에서 파생 |
| Esc로 모달이 안 닫힘 | 접근성 결함으로 보임 | **실제 어드민과 동일.** 기준 레포 전체에 `Escape` 핸들러 0건. 배경 클릭 닫기만 존재하고 그것은 우리도 동일 |
| 모달에 `role="dialog"`·`aria-modal`·포커스 트랩 없음 | 접근성 결함으로 보임 | **실제 어드민과 동일.** 기준도 전부 부재 |
| 토스트에 닫기 버튼 없음 | 닫을 수단이 없는 것처럼 보임 | **실제 어드민과 동일.** 기준은 `duration === 0` 일 때만 X를 렌더하고 기본 3초에선 렌더하지 않음(`Toast.tsx:45`) |
| 페이지 화살표에 접근명 없음 | 접근성 결함으로 보임 | **실제 어드민과 동일.** 기준도 아이콘 전용 chevron에 `aria-label` 없음 |
| `검색` 버튼 라벨 (실제 어드민은 항상 `조회`) | 임의 라벨로 보임 | **스토리보드 S7·S14 명시 요소.** 출처 A 충족. 다만 실제 어드민에 `검색` 버튼이 0건인 사실은 별도 인지 필요 |
| 프리셋 `일주일`·`금월` (실제는 7종 다른 라벨) | 임의 생성으로 보임 | **스토리보드 S7 명시 요소**(`storyboard_coverage.md:54`). 출처 A 충족 |
| 선택된 행에 배경색이 없어 보임 | `tr.selected` 의 `backgroundColor` 가 투명 | **정상.** 배경은 `tr` 이 아니라 `td` 에 적용(`contracts.html:14` `.tbl tbody tr.selected td { background: var(--primary-50); }`) |
| `role="checkbox"` 행에서 Space 무반응 | 키보드 조작 결함으로 보임 | **판독자 측 오류였다.** CDP에 `key:"Space"` 를 보낸 탓이며 규약값 `key:" "` 로 다시 보내면 정상 토글. 핸들러는 `k === ' ' \|\| k === 'Spacebar'` 를 정확히 본다(`app.html:2906`). Space·Enter 양쪽 동작 확인 |

---

## §6 투자 시뮬레이션 — 2차 판독 (화면 신설분)

`§0` 판독(17:40~18:05)이 끝난 뒤 20:49에 신설된 화면이라 1차 대조를 거치지 않았다. G-10에 따라 이 화면만 따로 본다.

| 항목 | 값 |
|---|---|
| 판독 시각 | **2026-08-28 21:5x KST** |
| 기준 | `/Users/semi/cursor/payhug-admin-web/app/settlement/simulation/page.tsx` (592행) — 읽기 전용 |
| 대상 | `payhug-investor-admin/app.html` `invest-sim` · 낱장 `invest-sim.html` · `invest-sim--result.html` |
| 조작 방식 | headless Chrome + CDP `Input.dispatchMouseEvent`·`dispatchKeyEvent`. 사이드바 진입 → 행 추가 → 행 삭제 → 실행 → 미지급률 타이핑 → 재실행까지 전부 실제 입력 |
| 콘솔 오류 | 0건 |

### §6-1 판정표 — 15건

| # | 요소 | 실제 프론트 | 우리 | 판정 | 근거 |
|---|---|---|---|---|---|
| 1 | 페이지 제목 | `<h1 class="text-2xl font-bold">정산 시뮬레이션</h1>` (`page.tsx:202`) | `.page-title` `투자 시뮬레이션` | 일치 | 같은 자리·같은 위계 |
| 2 | 제목 아래 부제 | `<p class="text-sm text-gray-500">거래 건을 입력하면 …` (`:203-206`) | 없음 | 개선(허용) | D-23 화면 설명 0건 |
| 3 | 입력 카드 | `bg-white rounded-xl border border-gray-200 p-5` + `h2 text-sm font-semibold` (`:210-212`) | `.card` + `.card-title` `기준 변수` | 일치 | 같은 껍데기 |
| 4 | 입력 그리드 | `grid grid-cols-1 md:grid-cols-2 gap-4` (`:212`) | `.sim-grid` 3열 gap 16px | 개선(허용) | 항목이 2개가 아니라 6개다. gap 값은 같다 |
| 5 | 행 목록 카드 머리 | `거래 입력` + 우상단 `+ 거래 추가` (`:252-259`) | `정산금채권 입력` + 우상단 `+ 채권 추가` | 일치 | 배치·동작 동일. 낱말만 이 화면의 단위 |
| 6 | 행 레이아웃 | `flex items-center gap-3 bg-gray-50 rounded-lg px-3 py-2` (`:265`) | `.sim-row` 같은 값 | 일치 | `build_app.py:489-491` 주석에 대응 행 기록 |
| 7 | 행 순번 | `<span class="text-xs text-gray-400 w-6">{idx+1}</span>` (`:268`) | `.sim-no` 12px · `--gray-400` · 24px | 일치 | |
| 8 | 유형 select | `border rounded-lg px-2 py-1.5 text-sm w-28` (`:270-278`) | `.sim-plat` 112px 네이티브 select | 일치 | 네이티브 select 유지 |
| 9 | 금액 input | `type=number` · `w-40 text-right` (`:279-287`) | `.sim-amt` 160px 우정렬 · `type=number` | 일치 | |
| 10 | 단위 `원` | `<span class="text-xs text-gray-400">원</span>` (`:288`) | `.sim-unit` | 일치 | |
| 11 | 행 삭제 | `transactions.length > 1` 일 때만 · `ml-auto` · `text-red-400 hover:text-red-600` (`:289-296`) | `.sim-del` 같은 조건·같은 정렬·같은 색 | 일치 | 실조작 확인 — 9행에서 삭제하면 8행, 1행만 남으면 버튼 0개 |
| 12 | 합계 줄 | `총 {n}건, 합계 {fmt}` · `text-xs text-gray-500 pt-1` (`:299-302`) | `.sim-total` 같은 문자열 · 같은 값 | 일치 | 실조작 확인 — `총 9건, 합계 1,600,000,000원` 까지 따라옴 |
| 13 | 실행 버튼 | `w-full py-3 rounded-xl font-semibold` · `disabled:bg-gray-300 disabled:cursor-not-allowed` (`:306-312`) | `.sim-run` 같은 값 | 일치 | 색만 이 산출물 primary |
| 14 | 실행 중 라벨 | `{loading ? "계산 중..." : "시뮬레이션 실행"}` (`:313`) | 같은 두 문자열 | 일치 | 원문 그대로 |
| 15 | 결과 요약 카드 | `SummaryCard label/value/sub/highlight` 4장 (`:330-352`) | `.summary-card` 4장 · 첫 장 `highlight` | 일치 | 실조작 확인 — 카드 4장 |

### §6-2 실제에 있는데 우리에게 없는 것 — 2건

| 요소 | 실제 | 우리 | 판정 |
|---|---|---|---|
| 정책 선택 select 2개 (카드/배달) | `page.tsx:213-247`. 정산정책 목록을 불러 고른다 | 없음 | **해당 없음.** 정산정책은 관리자 어드민이 정하고 투자자 어드민은 읽어 쓰기만 한다(D-21·D-32). 고를 대상이 없다 |
| 실패 배너 | `bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700` (`:316-320`). 네트워크·서버 오류 표시 | 없음 | **해당 없음.** 계산이 브라우저 안에서 끝나 실패 경로가 없다(D-2 성공 경로만). 입력이 어긋나면 배너 대신 `DateRangeFilter.tsx:14` 원문 한 줄과 버튼 비활성으로 막는다 |

### §6-3 우리에게 있는데 실제에 없는 것 — 3건

| 요소 | 우리 | 근거 | 판정 |
|---|---|---|---|
| 행의 선정산일·정산예정일 날짜 칸 | `.sim-date` 2개 | 대표 정의서 `Di = 정산예정일 − 선정산일` (출처 C) | 근거 있음 |
| 행 끝 금융일수 표시 | `.sim-days` | 같은 정의. 날짜 두 칸에서 파생되는 값이라 입력이 아니라 표시다 | 근거 있음 |
| 행 열 머리줄 | `.sim-head` | 실제는 열이 3개(유형·금액·단위)라 머리가 필요 없다. 우리는 7개라 없으면 어느 칸이 무엇인지 못 읽는다 | 개선(허용) |

### §6-4 실조작 결과

| 조작 | 결과 |
|---|---|
| 사이드바 `투자 시뮬레이션` 클릭 | `data-view=invest-sim` · `#invest-sim` |
| `+ 채권 추가` 클릭 | 8행 → 9행 · 합계 `1,500,000,000` → `1,600,000,000` |
| 마지막 행 `삭제` 클릭 | 9행 → 8행 · 합계 복귀 · 삭제 버튼 8개 |
| `시뮬레이션 실행` 클릭 | 상태 `result` · 배지 `실행 결과` · 표 3개 · 카드 4장 · 현황 `투자실행액 998,900,000 / 3.7일 / 0.07% / 10.85% / 90.5%` |
| 미지급률 칸에 `0.05` 타이핑 후 재실행 | `S 0.07% → 0.04%` · 일별 합계 `투자수익 200,000 → 350,000` · `Ty 4.71% → 8.25%` |
| `투자 자산` 으로 복귀 | 불변식 유지 — 투자실행액 1,523,100,000 · 투자자산 1,628,400,000 · 비중 합 100.0% · 로스터 16건 · 원장 180일 |

---

## §5 규율 준수

`payhug-admin-web` · `payhug-merchant-web` 읽기 전용 — 워킹트리 변경 0건, 커밋·푸시 0건. `payhug-investor-admin` 읽기 전용 — HTML·CSS·자산 수정 0건. 모든 조작은 스크래치패드 고정 사본 대상. 산출물은 본 문서 1개.
