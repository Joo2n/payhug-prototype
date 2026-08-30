# 용어 박스 통일 · 목록 행 신호 · 순번 열 — 반영 결과

대상 `/Users/semi/cursor/payhug-investor-admin` · 시연본 `/Users/semi/cursor/payhug-investor-prototype`
근거 원본 `스토리보드_Admin_투자자.pptx`(17슬라이드) · 운영 어드민 `/Users/semi/cursor/payhug-admin-web`
생성 경로 — `fix_rows.py`(정적 낱장 11) → `build_app.py`(app.html 재생성) → `sync_prototype.sh`(시연본)

---

## 1 — 용어 박스 4줄 복원

### 무엇을 어디에

| 자리 | 처리 | 근거 |
|---|---|---|
| `app.html` 투자 자산 (수익 산정 기준 카드 아래) | **넣음** | 스토리보드 S3·S4·S5·S6 각주 4줄 |
| `app.html` 투자 수익 | 넣지 않음 | S7·S8·S9 에 각주 없음 |
| `app.html` 증명서 | 넣지 않음 | 같음 |
| `invest-assets*.html` 정적 5종 | 종전대로 유지 | 이미 있던 자리 |
| `invest-profit*.html` 정적 4종 | 종전대로 없음 | S7~S9 에 각주 없음 |

통합본 안 `terms-note` 는 투자 자산 한 곳뿐이다(실측 1개).

### 문구 — 스토리보드 원문 그대로

```
금융일수      양수일로부터 지급예정일까지의 한편 넣기 일수
W금융일수     취소 등이 없다는 가정하에, 보유한 정산채권들의 투자금액을 가중한 금융일수 평균
S입금부족율   20일 전일자부터 11일 전일자까지인 기간의 거래금액을 샘플로 한 '입금부족액/선정산금액'
Ty수익율      할인율 × (365 / w금융일수)
```

`금융일수` 의 시점·종점 낱말은 대표 정의(`ceo_definitions.md:43` = `선정산일로부터 정산예정일(=전일자)까지`)와 다르다.
화면 문구는 스토리보드 각주 쪽이고, 이 어긋남은 `value_lineage.md:309` 에 이미 등재돼 있다 — 손대지 않았다.

### 어떻게 같게 유지되는가

`build_app.py:42` 가 `invest-assets.html` 에서 블록을 문자 그대로 떠 온다.

```python
TERMS = cut(_ia, '<!-- 용어 안내 -->\n', '\n\n  </main>').rstrip()
TERMS_BLOCK = '        ' + dedent_block(TERMS, 4).replace('\n', '\n        ')
```

정적 화면을 고치면 통합본이 따라온다. 두 갈래로 다시 갈릴 자리가 없다.

### 되살리지 않은 것

투자 수익 화면(통합본·정적 4종)의 같은 블록은 그대로 없다. `fix12_static.py:162` 의 `invest-profit` 분기도 그대로 둔다.
지난 라운드에서 내린 부연설명 26종·`page-sub`·화면 이동 도크도 되살아나지 않았다(§3 잔존 검사).

---

## 2 — 정적본 대조

| 파일 | 블록 수 | 정규화 해시 | 원문 바이트 |
|---|---|---|---|
| `invest-assets.html` | 1 | `0626eeb0d28d` | 365 |
| `invest-assets--page2.html` | 1 | `0626eeb0d28d` | 365 |
| `invest-assets--download.html` | 1 | `0626eeb0d28d` | 365 |
| `invest-assets--cert-confirm.html` | 1 | `0626eeb0d28d` | 365 |
| `invest-assets--empty.html` | 1 | `0626eeb0d28d` | 365 |
| `app.html` | 1 | `0626eeb0d28d` | 397 |

여섯 자리의 정규화 해시가 같다. `app.html` 이 32바이트 큰 것은 들여쓰기 4칸 × 8줄뿐이고,
줄 단위 diff 는 앞 공백 외에 0건이다.

**렌더 텍스트 대조** — 통합본 투자 자산 상태 5종(`default` `page2` `download` `cert-confirm` `empty`)과
정적 5종, 합 10건의 `textContent` 가 공백 정규화 후 전부 같다(불일치 0).
상태 변형에서도 같은 규칙이 선다 — 다섯 상태 모두 `terms-note` 1개, 보임, 같은 문구.
`invest-profit/default` `invest-profit/monthly` `certificate/default` 에는 없다.

---

## 3 — 목록 행 신호 · 순번 열 · 건수 자리

### A. 행 호버 — 원본 값 + 미세 확대

운영 어드민 조사 결과(파일:라인 인용은 `payhug-admin-web` 기준):

| 항목 | 원본에 있는가 | 값 |
|---|---|---|
| 클릭 가능 행 배경 | 있음 | `hover:bg-primary-50/30` = `rgba(244,253,240,0.3)` — `sales/page.tsx:130` · `inquiries/page.tsx:286` · `manage/page.tsx:291` |
| 전이 | 있음 | `transition-colors` = `150ms cubic-bezier(0.4,0,0.2,1)`. `duration-*`·`ease-*` 명시는 `<tr>` 에 0건 |
| 커서 | 있음 | `cursor-pointer` — `onClick` 이 붙은 행에만. 예외 없음 |
| `transform` · `scale` | **없음 (0건)** | 레포의 `transform` 은 토글 노브·chevron 회전·툴팁 위치뿐 |
| 선택된 행 배경 | **없음** | 다중선택 표 `PreSettlementTab.tsx:1276` 도 체크 상태를 행 배경에 안 쓴다 |
| `focus-visible` | **없음 (0건)** | `<tr>` 에 `tabIndex`·`onKeyDown` 도 0건. 포커스 표시는 input 계열의 `focus:ring-2 focus:ring-primary-500`(`PolicyFormModal.tsx:84`) |

→ 배경·전이·커서는 원본 값 그대로 두고, 원본에 없는 확대만 얹었다.

```css
.tbl tbody tr.clickable, .sign-row.pickable {
  transform-origin: center right;
  transition: background-color .15s var(--ease-default), transform .15s var(--ease-default);
}
… :hover, … :focus-visible { transform: scale(1.005); position: relative; z-index: 1; }
… :focus-visible { outline: 2px solid var(--primary-500); outline-offset: -2px; }
```

`assets/base.css` 한 곳에 있어 통합본·정적 낱장이 같은 규칙을 쓴다.

**확대가 레이아웃을 흔들지 않는 이유** — 축을 오른쪽 모서리에 두면 늘어난 폭이 전부 시작 쪽으로 간다.
가로 스크롤 상자는 시작 쪽 넘침을 스크롤 영역에 넣지 않아 스크롤바가 생기지 않는다.
실측: 표 폭 `1134 → 1134`, 표 높이 `438 → 438`, 이웃 행 top 불변, 문서 폭 `1440/1440`,
`scrollWidth/clientWidth` = `1134/1134`. 마우스를 떼면 배경·확대가 전부 원래대로 돌아온다.

서명이 끝난 행(`.sign-row.done`)에는 `pickable` 을 붙이지 않는다 — 고를 수 없는 행이라 신호도 없다(커서 `auto`).

**계약기록에 행 클릭 선택 신설** — 종전에는 체크박스로만 닿았다. 행에 `data-act="ct-row"` ·
`role="checkbox"` · `tabindex="0"` 을 주고 Space·Enter 도 받는다. 체크박스와 문서 링크는 각자
`data-act` 를 가져 `closest()` 가 먼저 잡으므로 행 토글과 겹치지 않는다.

### B. 정산채권 양수 — 선택 건수 위치

`서명하기` 버튼 위 가운데에 있던 `선택 N건` 을 목록 아래 **왼쪽**으로 옮겼다.
`.sign-foot` 을 `1fr auto 1fr` 3열 격자로 바꿔 건수는 왼쪽 칸, 버튼은 가운데 칸이다 —
버튼은 스토리보드 S15(카드 안 가로 가운데) 자리를 지킨다. 쪽번호 줄이 쓰는 격자와 같은 구조다.
근거: 원본의 다중선택 액션 바도 건수가 왼쪽, 버튼이 오른쪽이다(`PreSettlementTab.tsx:1214·1264`).

### C. 계약기록 — 표시 제거 · No 열 · 선택 칩 이동

| 항목 | 결정 | 근거 |
|---|---|---|
| 머리 `표시 1–8` | 제거 | 범위 문자열이 원본 어드민 전체에 0건 |
| 머리 `총 16건` | 유지 | 지시 |
| `No` 열 위치 | 체크박스 → `No` → `MID` … | 원본 순번 열은 늘 1번째지만 체크박스 열과 같이 쓰는 표가 없다. 체크박스는 행 선택 컨트롤, 순번은 데이터라 컨트롤을 앞에 둔다 |
| `No` 번호 규칙 | **쪽이 넘어가도 이어짐** (1–8 · 9–16) | 원본 순번은 `index + 1`(`sales/page.tsx:143` · `inquiries/page.tsx:289` · `manage/page.tsx:294`)인데 그 세 표는 쪽나눔이 없어 표시 중인 전체가 곧 한 쪽이다. 쪽나눔이 있는 표의 등가물은 이어지는 번호다. 쪽마다 1부터면 머리의 `총 16건` 과 축이 어긋나 번호로 행을 가리킬 수 없다 |
| `No` 열 서식 | 48px · 12px · `gray-400` · 왼쪽 | 원본 `w-12 … text-gray-400 text-xs`, 헤더 `text-left` |
| 선택 칩 `3건 선택` | 머리 → 쪽번호 줄 왼쪽 칸 | B 와 같은 규칙(선택 건수는 목록 아래 왼쪽) |
| `선택 해제` · `선택 문서 다운로드` | 자리 유지 | 지시 |

머리 라벨은 지시대로 `No` 다. 원본 어드민의 라벨은 `번호`(`sales/page.tsx:107`) 하나와
`#`(`inquiries/page.tsx:257` · `manage/page.tsx:265`) 둘이며 `No` 는 0건이다 — §5 에 올린다.

### D. 같은 규칙을 다른 표에도

| 표 | 처리 | 근거 |
|---|---|---|
| 가맹점 | `표시 a–b` 제거. `총 N건` 은 쪽번호 줄 왼쪽 그대로 | 범위 표기는 원본 0건. 한 규칙으로 맞춘다 |
| 계약기록 | `표시 a–b` 제거 | 같음 |
| 투자 자산 `가맹점별 투자자산` | **손대지 않음** | 열 구성이 스토리보드 S3 표2 로 고정(`가맹점 · 투자금액 · W금융일수 · S입금부족율 · ty수익율 · 비중`)이고, 엑셀·증명서와 열이 1:1로 맞물려 `verify_crossscreen` 23건이 그 위에 선다 |
| 일별·월별 투자수익 | **손대지 않음** | 같음 (S7 표2) |

`rangeLabel()` 함수는 폐기했다. 레포 HTML 39개(용어 문서 제외)에 `표시 a–b` · `rangeLabel` 잔존 0.

**가맹점 표의 `No` 열은 손대지 않고 §5 로 올린다** — 근거가 갈린다.

---

## 4 — 검증

전부 창 없이(`--headless=new`) 돌렸다.

| 검증기 | 기준 | 실측 |
|---|---|---|
| `verify_app.js` | 75 PASS / 0 FAIL · 죽은 컨트롤 0 · 콘솔 0 | **76 PASS / 0 FAIL** · 죽은 컨트롤 0 / 검사 161 · 콘솔 0 |
| `verify_identity.js` | 15 PASS · 비중 100.0% · ⑤ 2.24% | 15건 · FAIL 0 · `ratioSum 100` · `cardTyAsset 2.24` |
| `verify_crossscreen.py` | 23건 일치 | 23건 · 불일치 0 |
| `verify_links.py` | 200 · 바이트 일치 | 86건 전건 200 · 바이트 일치 |
| `verify_toast.js` | FAIL 0 | 16건 · FAIL 0 · 콘솔 0 |
| `verify_rows.js` (신설) | — | **39 PASS / 0 FAIL** |

`verify_app` 이 75 → 76 인 것은 계약기록 행 클릭 선택 1건이 새로 붙어서다. 검사 대상 컨트롤도 145 → 161.
`verify_links` 가 80 → 86 인 것은 계약기록 문서 링크가 새로 잡혀서다.
`verify_app.js` 의 계약기록 선택 건수 판정은 옮긴 자리(쪽번호 줄 왼쪽)를 읽도록 고쳤다.

### verify_rows.js 내역 (39건)

| 묶음 | 건수 | 잰 것 |
|---|---|---|
| 행 호버 | 22 | 통합본·정적본 두 목록 **전 행**(계약기록 8+8 · 서명대기 3+3) + 서명 완료 행 1. CDP 로 실제 마우스를 올려 배경·`transform`·커서를 읽고, 표 폭·표 높이·이웃 행 top·문서 가로폭·`scrollWidth/clientWidth` 가 그대로인지, 떼면 되돌아오는지 |
| 키보드 포커스 | 4 | 실제 Tab 키로 도달(11~18회). `:focus-visible` 매칭 · `solid 2px rgb(101,200,38)` · `matrix(1.005…)` · `tabindex=0` |
| 순번 열 | 5 | 머리 `No` · 열 순서 `체크박스 · No · MID · 가맹점 · 재양도합의서 · 검증` · 1쪽 `1–8` · 2쪽 `9–16` · 순번↔MID 1:1 · 정적본 `1–8` |
| 건수 자리 | 6 | 계약기록 칩이 쪽번호 줄 왼쪽(왼쪽에서 20px) · 머리에 없음 · 머리 = `총 16건`(표시 없음) · 행 클릭 시 `3건 → 2건` · 서명대기 건수 왼쪽(24px)이며 버튼 위가 아님 · 버튼은 가운데 · `선택 0건 → 선택 1건` |
| 잔존 | 1 | `표시 a–b` · `rangeLabel` 0건 (HTML 39개, 용어 문서 제외) |

산출 `verify_rows_result.json`.

### 되살아나지 않았는지

| 검사 | 결과 |
|---|---|
| 용어 박스 — 통합본·정적본 양쪽에 있고 문자 단위로 같은가 | 6파일 정규화 해시 동일 · 렌더 텍스트 10건 불일치 0 |
| `page-sub` | 0건 |
| 화면·상태 이동 도크(`dock` 계열) | 0건 |
| 지난 라운드 부연설명 26종 | 화면 0건. `inquiry.html` 개발 부록의 `비밀번호 변경 후 기존 세션 …` 1건은 지난 라운드가 부록으로 옮긴 것이라 그대로 |
| 숫자 | 비중 합 `100.0%` · ⑤ `2.24%` · 합계 `1,250,800,000` / `1,375,880` · 총 `16건` — 전부 종전 그대로 |

---

## 5 — 미해소 · 판단이 갈린 것

| # | 내용 | 상태 |
|---|---|---|
| 1 | **순번 열 머리 라벨** — 지시는 `No`, 원본 어드민은 `번호` 1곳 · `#` 2곳이고 `No` 는 0건이다. 지시대로 `No` 로 넣었다 | 라벨을 원본 쪽으로 맞출지 결정 필요 |
| 2 | **가맹점 표의 순번 열** — 원본의 같은 성격 화면(`manage/page.tsx:265` 가맹점 관리)에는 `#` 열이 있지만, 스토리보드 S14 는 7열을 `가맹점ID`부터로 규정하고 순번이 없다. 근거가 정면으로 갈려 손대지 않았다 | 결정 필요 |
| 3 | **총 건수 자리** — 계약기록은 카드 머리, 가맹점은 쪽번호 줄 왼쪽이다. 지시가 계약기록 `총 16건` 을 그 자리에 두라고 못 박아 그대로 뒀다. 원본 어드민도 자리가 갈린다(카드 머리 `sales/[bizNo]/page.tsx:880` vs 쪽번호 줄 왼쪽 `LockAccountDeposits.tsx:436`) | 한 자리로 통일할지 결정 필요 |
| 4 | **일별 할인율 표기 자릿수** — 원장 값 `0.110000%` 가 화면·엑셀에 `0.11%` / `0.11` 로 나온다. 화면 `app.html:519·680`, 엑셀 4종 시트 값 모두 `0.11`. **표시 자릿수 차이일 뿐 값은 같다.** 이번 범위 밖이라 손대지 않았다 | 표기 자리수 결정 필요 |
| 5 | **시연본 자동 동기화 워크플로** — `.github/workflows/sync-prototype.yml` 이 시크릿 `PROTOTYPE_SYNC_TOKEN` 미등록으로 첫 단계에서 계속 실패한다(run 33146586434 · 33147487042). 수동 `sync_prototype.sh` 로 대신하고 있다. 시크릿 등록은 저장소 설정 변경이라 손대지 않았다 | 사용자 조치 필요 |
| 6 | **레포 비공개 전환 중 배포 차단** — 두 레포가 private 이던 동안 Vercel 배포가 `BLOCKED` 로 떨어졌다(§6) | 해소됨 — 공개로 되돌림 |

### Figma 재임포트 대상 (쓰기는 하지 않았다)

`Tcf69tIciGxmlqCIuRb0iI` 페이지 `3066:328`. 이번에 그림이 바뀐 프레임 9개.

| 프레임 | 파일 | node |
|---|---|---|
| 05 가맹점 | `merchants.html` | `3124:2` |
| 06 정산채권 양수 | `acquisition.html` | `3118:2` |
| 06-a 정산채권 양수 — 서명 확인 | `acquisition--confirm.html` | `3132:2` |
| 06-b 정산채권 양수 — 서명 진행 | `acquisition--signing.html` | `3135:2` |
| 06-c 정산채권 양수 — 서명 완료 | `acquisition--done.html` | `3138:2` |
| 07 계약기록 | `contracts.html` | `3127:2` |
| 07-a 계약기록 — 전체 선택 | `contracts--all.html` | `3141:2` |
| 07-b 계약기록 — 다운로드 완료 | `contracts--downloaded.html` | `3144:2` |
| 07-c 계약기록 — 문서 없음 | `contracts--empty.html` | `3140:2` |

`merchants--filtered.html` · `merchants--empty.html` 은 범위 표기가 원래 없어 그림이 그대로다.
`invest-assets*` 5종도 용어 박스가 이미 있던 자리라 그대로다. 호버·포커스는 정지 화면에 안 잡힌다.

---

## 6 — 양쪽 배포 실측

| 항목 | 값 |
|---|---|
| `payhug-investor-admin` HEAD | `efe85b4272e830c6c1425b00ac30268cba1d67a0` (= `origin/main`) |
| `payhug-investor-prototype` HEAD | `c222a839fa1670a55b05606ae698c9fd1358691b` |
| 용어 박스 커밋 | `3dfcbfe` |

| URL | 응답 | 크기 | 로컬과 |
|---|---|---|---|
| `https://payhug-investor-demo.vercel.app/` | 200 | 24,490B | — |
| `https://payhug-investor-demo.vercel.app/app.html` | 200 | 163,673B | **바이트 일치** |
| `https://payhug-investor-prototype.vercel.app/` | 200 | 158,433B | **바이트 일치** |

배포본 `app.html` 안: `terms-note` 1 · `class="no">No` 1 · `ct-row` 5 · `pickable` 1 · `표시 <b` 0 — 로컬과 같다.
정적 화면도 sha256 일치: `contracts.html` `db4047a6…` · `acquisition.html` `71915e52…` · `assets/base.css` `c4a49c5e…`.

`sync_prototype.sh` 는 5단계 전부 통과했다 — 통로 검사(금칙 0 · 형제링크 0 · 허용 외부 2호스트) →
로컬 게이트 17 PASS → push `f4a3d52..c222a83` → 배포 반영 2회차 확인 → **배포 URL 게이트 17 PASS**.

### 시연본 전건 404 재확인

| 파일 | 응답 |
|---|---|
| `glossary.html` | 404 |
| `glossary-legacy.html` | 404 |
| `capability.html` | 404 |
| `feasibility.html` | 404 |
| `inquiry.html` | 404 |
| `archive.html` | 404 |
| `review.html` | 404 |
| `app.html` | 404 |
| `contracts.html` · `acquisition.html` · `invest-assets.html` (정적 낱장 표본) | 404 |

시연본은 `index.html` 과 화면이 부르는 자산만 갖는다. 다른 조가 이번에 새로 만든 `glossary-legacy.html` 도 넘어가지 않았다.

### 레포 비공개 전환 — 배포에 문제가 있었다

두 레포가 private 이던 동안 **Vercel 배포가 `BLOCKED` 로 떨어졌다.**

| 배포 | 커밋 | 저장소 가시성 | 상태 |
|---|---|---|---|
| `dpl_AKSuPfMv…` (demo) | `3dfcbfe` | `private` | **BLOCKED** |
| `dpl_DbjErTD3…` (prototype) | `f4a3d52` | `private` | **BLOCKED** |
| 그 이전 전량 | — | `public` | READY |

`errorLink` = `vercel.com/docs/deployments/troubleshoot-project-collaboration#account-configuration`.
팀 `joons-projects-9eb5ca31` 은 `hobby` 요금제다. 배포 보호(비밀번호·SSO·신뢰 IP)는 셋 다 꺼져 있어 원인이 아니다.
그동안 시연본 짧은 주소는 `x-vercel-mitigated: challenge` 로 403 을 냈고(프로젝트 자체 주소는 200),
`sync_prototype.sh` 의 배포 반영 확인이 10분 타임아웃으로 끊겼다.

**push 자체는 문제가 없었다** — `gh` 토큰에 `repo` 범위가 있어 private 에도 그대로 올라갔다.

레포가 공개로 되돌아온 뒤(`d03335b 프로덕션 배포 재개 — 레포 공개 전환 후`) 두 배포 다 정상이고,
현재 두 레포 모두 `PUBLIC` 이다. **비공개로 다시 돌리려면 Vercel 요금제를 올려야 배포가 산다.**

### 커밋 이력에 생긴 겹침

이번 라운드 두 번째 묶음(행 신호·순번 열·건수 자리)은 **다른 조의 커밋 `efe85b4` 에 함께 담겼다.**
용어 문서를 재조판하던 조가 같은 저장소에서 `git add -A` 로 전량 스테이징한 뒤 커밋해,
내 작업 파일 12개가 그 커밋에 섞였다. 내용은 전부 들어갔고 `origin/main` 에 올라가 있으나,
그 커밋 메시지는 이 작업을 설명하지 않는다. 이미 push 된 커밋이라 다시 쓰지 않았다.
첫 번째 묶음(용어 박스)은 `3dfcbfe` 로 온전히 남아 있다.
