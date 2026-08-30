# 모달 닫힘 동작 전수 조사

조사 시각 2026-08-30 15:0x KST · 읽기 전용 조사 · 프로토타입 소스 무수정

측정 도구 — 헤드리스 Chrome 152.0.7977.65 + CDP `Input.dispatchMouseEvent` / `Input.dispatchKeyEvent`.
뷰포트는 `Emulation.setDeviceMetricsOverride` 로 1440×900 고정(`--window-size` 의 macOS 87px 잠식을 피함).
ESC 는 규약값 `key:"Escape"` · `code:"Escape"` · `keyCode:27` 로 전송.
클릭 지점마다 `document.elementFromPoint` 로 실제로 무엇이 잡히는지 함께 기록.

표기 — **[클릭]** 실제 마우스·키보드 이벤트로 확인 / **[소스]** 코드 판독으로만 확인

---

## 0. 조사 중 원본이 바뀐 사실

`build_app.py` 와 `app.html` 이 조사 도중 다른 조에 의해 수정됨(app.html mtime 2026-08-30 14:53, sha1 `62e8e8d5a31ec5e84deade65bb2489608d83fa7a`).
따라서 이 문서는 **수정 전 상태(배포 3주소)** 와 **수정 후 상태(로컬 정본)** 를 나눠 적는다.

| | 오버레이 `data-act="backdrop"` | 디스패처 | ct-sign 서명란 |
|---|---|---|---|
| git HEAD `build_app.py` | 4개 모달에 부착 (`:962 :984 :1001 :1056`) | `:3005-3007` | `:217` `grid-template-columns: 1fr 1fr` |
| 현재 작업본 `build_app.py` | 전부 제거 (`:961 :983 :1000 :1055`) | `:2962-2963` 주석으로 대체 | `:217` `flex; flex-direction: column` |
| 배포 3주소 | HEAD 판이 그대로 서비스 중 | 〃 | 〃 |

---

## A. 실제 프론트의 모달 닫힘 경로 (근거표)

전부 **[소스]** 판독. 두 레포 모두 dev 서버를 띄우지 않았다 — `.next` 빌드 캐시가 읽기 전용 레포에 생기는 것을 피하기 위함.
단, 이 패턴의 DOM 의미(오버레이 핸들러 + 패널 `stopPropagation`)는 동일 구조를 재현한 페이지에 **[클릭]** 을 쏘아 확인했다(§A-3).

### A-1. payhug-admin-web

| # | 컴포넌트·화면 | 오버레이 클릭 | 패널 안쪽 클릭 | ESC | X | 취소·닫기 | 근거 |
|---|---|---|---|---|---|---|---|
| 1 | `components/ConfirmDialog.tsx` | 닫힘 | 닫히지 않음 | 없음 | 없음 | `취소`·`확인` | `:54` 오버레이 `onClick={onClose}` / `:55` 패널 `onClick={e=>e.stopPropagation()}` / `:65` 취소 / `:70` 확인 |
| 2 | `components/AttachmentPreviewModal.tsx` | 닫힘 | 닫히지 않음 | 없음 | 있음 | 없음 | `:11` / `:12` / `:22` X |
| 3 | `components/ManualTransferModal.tsx` | 닫힘 | 닫히지 않음 | 없음 | 있음 | `취소`·`닫기` | `:126-128` / `:129-132` / `:141` X / `:268` 취소 / `:300-309` 에러 전용 닫기 |
| 4 | `components/MerchantDocumentEditModals.tsx` OCR 진행 오버레이 | **닫히지 않음** | 닫히지 않음 | 없음 | 없음 | 없음 | `:33-40` `OcrOverlay` — 오버레이에 `onClick` 자체가 없음 |
| 5 | 〃 문서 편집 모달 3종 | 닫힘 | 닫히지 않음 | 없음 | 있음 | `취소` | `:181/:182/:188/:257`, `:370/:371/:377/:443`, `:572/:573/:579/:644` |
| 6 | 〃 신분증 확대 뷰 | 닫힘 | **이미지 클릭도 닫힘** | 없음 | 있음 | 없음 | `:450-451` 오버레이 `onClick`, 패널 없이 `<img>` 직접 배치 → `stopPropagation` 없음. `:453` X |
| 7 | `components/PlatformLockAccountDetailDialog.tsx` | 닫힘 | 닫히지 않음 | 없음 | 있음 | 없음 | `:99` 컨테이너(핸들러 없음) / `:100` 별도 오버레이 `onClick={onClose}` / `:101` 패널은 형제 → `stopPropagation` 불필요 / `:119` X `aria-label="닫기"` |
| 8 | `components/MerchantExternalAccounts.tsx` | 닫힘 | 닫히지 않음 | 없음 | 없음 | 폼 버튼 | `:404-406` 형제 오버레이 구조 |
| 9 | `components/MerchantDebtManagement.tsx` 2종 | 닫힘 | 닫히지 않음 | 없음 | 등록·수정만 있음(`:328`) / 확인 모달은 없음 | 폼 버튼 | `:320-323`, `:387-390` |
| 10 | `components/sales/ExcelUploadModal.tsx` | 닫힘(`handleDismiss`) | 닫히지 않음 | 없음 | 있음 | `닫기` | `:129` / `:131` / `:120-126` 분기 / `:134` X / `:255` 닫기 |
| 11 | `components/sales/ManualSalesModal.tsx` | 닫힘(`handleDismiss`) | 닫히지 않음 | 없음 | 있음 | `닫기` | `:150` / `:152` / `:132-138` / `:156` X / `:304` |
| 12 | `app/settlement/policies/PolicyFormModal.tsx` | 닫힘 | 닫히지 않음 | 없음 | 있음 | `취소` | `:137` / `:138` / `:141` / `:451` |
| 13 | `app/settlement/overview/PreSettlementTab.tsx` 상세 | 닫힘 | 닫히지 않음 | 없음 | 헤더 | — | `:1331` / `:1334` |
| 14 | `app/account-balance/page.tsx` 외부 입금 등록 | 닫힘 | 닫히지 않음 | 없음 | 없음 | 폼 버튼 | `:718` / `:719` |
| 15 | `app/manage/page.tsx` 2종 | 닫힘 | 닫히지 않음 | 없음 | `:376` 1종만 | 폼 버튼 | `:370-373`, `:433-435` |
| 16 | `app/partners/page.tsx` 프로필·회원 2종 | 닫힘 | 닫히지 않음 | 없음 | 있음 | 폼 버튼 | `:251/:252`, `:943/:944` |
| 17 | 〃 사업자등록증 OCR 진행 | **닫히지 않음** | 닫히지 않음 | 없음 | 없음 | 없음 | `:446-450` 오버레이에 핸들러 없음 |
| 18 | `app/merchants/[id]/page.tsx` 7종(반려·재서명·초기화·비번초기화·하드리셋·약관미리보기·백필) | 닫힘 | 닫히지 않음 | 없음 | 대부분 있음 | 폼 버튼 | `:1820/:1821`, `:1862/:1863`, `:1894/:1895`, `:1947/:1948`, `:1985/:1986`, `:2033/:2034`, `:2117/:2118` |
| 19 | 〃 처리 중 로딩 오버레이 | **닫히지 않음** | 닫히지 않음 | 없음 | 없음 | 없음 | `:2142-2145` |
| 20 | `app/terms/page.tsx` 5종 | 닫힘 | 닫히지 않음 | 없음 | 4종 있음 | 폼 버튼 | `:355/:356`, `:399/:400`, `:427/:428`, `:463/:464`, `:487/:488` |

부수 사실
- **ESC 핸들러가 레포 전체에 0건.** `grep -rn "Escape\|keydown" app/ components/ hooks/` 결과 6건 전부 `Enter` 처리(`app/sales/[bizNo]/page.tsx:558`, `app/inquiries/page.tsx:415`, `app/log-analysis/page.tsx:252`, `app/login/page.tsx:131·152`, `components/MerchantMemos.tsx:182`).
- **배경 스크롤 잠금 0건.** `document.body.style.overflow` 조작 없음. `document.body` 등장 5곳은 전부 포털(`PlatformLockAccountDetailDialog.tsx:224`, `MerchantCardFees.tsx:196`, `MerchantExternalAccounts.tsx:680`) 또는 다운로드 앵커(`AttachmentPreviewModal.tsx:66·68`).
- **`role="dialog"`·`aria-modal` 0건.** 포커스 트랩 구현도 0건.
- 공통 Modal 컴포넌트가 없다. 20종이 전부 손으로 같은 구조를 반복한다.

### A-2. payhug-merchant-web

| # | 컴포넌트 | 오버레이 클릭 | 패널 안쪽 클릭 | ESC | X | 버튼 | 근거 |
|---|---|---|---|---|---|---|---|
| 1 | `components/CommonModal.tsx` | 닫힘 | 닫히지 않음 | 없음 | 없음 | `취소`·`확인` | `:39` / `:40` / `:64` / `:71` |
| 2 | `components/TermsModal.tsx` | 닫힘 | 닫히지 않음 | 없음 | 있음 | 동의 | `:27` / `:28` / `:31` / 본문 스크롤 `:42` |
| 3 | `components/dashboard/InquiryModal.tsx` | 닫힘 | 닫히지 않음 | 없음 | 있음 | 취소·등록 | `:31` / `:32` / `:36` / `:82` / `:89` |
| 4 | `components/Header.tsx` 로그아웃 확인 | 닫힘 | 닫히지 않음 | 없음 | 있음 | 예·아니오 | `:268` 컨테이너 / `:269` 형제 오버레이 `onClick` / `:270` 패널 / `:273` X |
| 5 | `app/my-info/contract/page.tsx` 첨부·약관 미리보기 2종 | 닫힘 | 닫히지 않음 | 없음 | 있음 | — | `:206-208/:210-212`, `:240-242/:244-246` |
| 6 | `components/SignatureCreator.tsx` 서명 그리기 | **닫히지 않음** | 닫히지 않음 | 없음 | 없음 | 버튼만 | `:85` 오버레이에 `onClick` 없음 |
| 7 | `components/ContractDirectSign.tsx` / `ContractSignView.tsx` / `SignatureOnPdf.tsx` / `ContractSignInput.tsx` 전면 서명 화면 | **닫히지 않음** | 닫히지 않음 | 없음 | 헤더 버튼 | 버튼만 | `:222`, `:119`, `:121`, `:128` |
| 8 | 업로드·로그인 진행 오버레이 | **닫히지 않음** | 닫히지 않음 | 없음 | 없음 | 없음 | `app/contract/upload-*/page.tsx:190·208·248·258`, `app/login/page.tsx:186`, `app/contract/terms/page.tsx:754` |

merchant-web 도 ESC 0건 · 스크롤 잠금 0건.

### A-3. 패턴의 DOM 의미 확인 **[클릭]**

`ConfirmDialog.tsx:54-55` 와 동일 구조(오버레이 `click`→close, 패널 `click`→`stopPropagation`)를 재현한 페이지에 실제 마우스 이벤트를 쏜 결과.

| 클릭 지점 | 결과 |
|---|---|
| 오버레이 (60, 60) | CLOSED |
| 패널 본문 텍스트 중앙 | OPEN 유지 |
| 패널 빈 여백(패딩) | OPEN 유지 |

즉 **실제 프론트의 규칙은 "오버레이 클릭 = 닫힘, 패널 안쪽 클릭 = 유지, ESC = 없음"** 이다. 진행 중 오버레이만 오버레이 클릭도 막는다.

---

## B. 우리 산출물 모달 × 닫힘 경로 격자

### B-0. 배포 주소 실측

| 주소 | HTTP | 내용 |
|---|---|---|
| `https://payhug-investor-admin.vercel.app/` | **404 `DEPLOYMENT_NOT_FOUND`** | 존재하지 않음. 하위 경로 5종(`index.html`·`app.html`·`capability.html`·`feasibility.html`·`archive.html`) 전부 404 |
| `https://payhug-investor-prototype.vercel.app/` | 200 (210,315 B) | `app.html` 시연본 1장 |
| `https://payhug-investor-glossary.vercel.app/` | 200 (379,834 B) | 용어 해설 1장 |
| `https://payhug-investor-demo.vercel.app/` | 200 | 저장소 전량. `app.html` 213,601 B + 낱장 34종 |

세 번째 주소의 정확한 이름은 `payhug-investor-demo` 다 — `README.md:9-11`.
배포 3주소는 전부 **수정 전** 판이다(`demo/app.html` 에 `data-act="backdrop"` 5줄 중 4줄 잔존, `ct-sign` 은 `grid 1fr 1fr`).

### B-1. 배포본 = 수정 전 **[클릭 전수]**

대상 `https://payhug-investor-prototype.vercel.app/` (동일 결과를 `demo/app.html` 의 `계약서보기` 로 재확인).
표의 값은 그 조작 뒤 모달이 어떻게 됐는지의 **관측 결과**다.

| 모달 | 여는 경로 | 오버레이 | 본문 텍스트 | 본문 빈 여백 | 헤더 빈 공간 | 스크롤 영역 안 | ESC | X | 닫기·취소 |
|---|---|---|---|---|---|---|---|---|---|
| `invest-assets-cert-confirm` 증명서 발급 확인 | 투자 자산 → `증명서 발급` | **닫힘** | **닫힘** | **닫힘** | **닫힘** | (없음) | 무반응 | 닫힘 | 닫힘 |
| `acquisition-doc` **계약서보기** | 정산채권 양수 → 행의 `계약서보기` | **닫힘** | **닫힘** | **닫힘** | **닫힘** | **닫힘** | 무반응 | 닫힘 | 닫힘 |
| `acquisition-confirm` 서명 확인 | 정산채권 양수 → `전체 선택` → `서명하기` | **닫힘** | **닫힘** | **닫힘** | **닫힘** | (없음) | 무반응 | 닫힘 | 닫힘 |
| `acquisition-signing` 서명 진행 | 〃 → `서명 진행` | 유지 | (본문 p 없음) | 유지 | 유지 | (없음) | 무반응 | X 없음 | 닫기 버튼 없음 |
| `acquisition-done` 서명 완료 | 〃 → 진행 완료 대기 | **닫힘** | **닫힘** | **닫힘** | (헤더 없음) | (없음) | 무반응 | X 없음 | `확인`·`계약기록 보기` 로 닫힘 |

클릭 지점의 `elementFromPoint` 기록 — 본문 텍스트 지점에서 잡힌 요소는 `P.cert-desc` / `SPAN.mono` / `P.modal-desc` / `P.done-desc`, 빈 여백은 `DIV.modal-body`, 헤더는 `DIV.modal-header`, 스크롤 영역은 `.doc-scroll` 안의 `P`. 전부 `closest('[data-act]')` 가 배경을 물어 온다.

**원인** — `build_app.py:3005-3007`(git HEAD 기준)

```js
var a = t.closest('[data-act]');
if(a && a.dataset.act === 'backdrop'){
  if(t !== a) a = t.closest('[data-act]:not([data-act="backdrop"])') || a;
  if(a.dataset.act === 'backdrop'){ e.preventDefault(); ACT['modal-close'](); return; }
}
```

`data-act="backdrop"` 가 **오버레이 div 자체**에 붙어 있고, 모달 패널은 그 자식이다.
패널 안쪽 아무 데나 누르면 `closest('[data-act]')` 가 조상으로 올라가 배경을 집는다.
2행의 재탐색은 `[data-act]:not([data-act="backdrop"])` 를 찾지만 패널 안에 `data-act` 를 가진 조상이 없으므로 `null` → `|| a` 로 다시 배경이 되고, 3행에서 닫힌다.
주석은 "패널 안쪽 클릭은 배경으로 새지 않는다"고 적혀 있으나 실제 코드가 그 반대로 동작한다.

### B-2. 로컬 정본 = 수정 후 **[클릭 전수]**

대상 `file:///Users/semi/cursor/payhug-investor-admin/app.html` (sha1 `62e8e8d5…`, mtime 14:53).

| 모달 | 오버레이 | 본문 텍스트 | 본문 빈 여백 | 헤더 빈 공간 | 스크롤 영역 안 | ESC | X | 닫기·취소 |
|---|---|---|---|---|---|---|---|---|
| `invest-assets-cert-confirm` | 유지 | 유지 | 유지 | 유지 | (없음) | 무반응 | 닫힘 | 닫힘 |
| `acquisition-doc` | 유지 | 유지 | 유지 | 유지 | 유지 | 무반응 | 닫힘 | 닫힘 |
| `acquisition-confirm` | 유지 | 유지 | 유지 | 유지 | (없음) | 무반응 | 닫힘 | 닫힘 |
| `acquisition-signing` | 유지 | — | 유지 | 유지 | (없음) | 무반응 | X 없음 | 닫기 버튼 없음 |
| `acquisition-done` | 유지 | 유지 | 유지 | (헤더 없음) | (없음) | 무반응 | X 없음 | `확인`·`계약기록 보기` 로 닫힘 |

`elementFromPoint` 가 잡는 요소는 같으나 `act` 가 전부 `null` 로 바뀌었다.

### B-3. 낱장 정적 HTML 5종 **[클릭]**

`https://payhug-investor-demo.vercel.app/<파일>` 실측. 스크립트 0개짜리 정적 페이지다.

| 파일 | 오버레이 | ESC | X | 푸터 버튼 |
|---|---|---|---|---|
| `acquisition--doc.html` | 무반응 | 무반응 | `<a href="acquisition.html">` → **목록으로 이동** | `닫기`→`acquisition.html`, `계약서 원문 열기`→`assets/docs/정산금채권_재양도_합의서.txt` |
| `acquisition--confirm.html` | 무반응 | 무반응 | `<button class="close">` — **핸들러도 href 도 없음. 죽은 버튼** | `취소`→`acquisition.html`, `서명 진행`→`acquisition--signing.html` |
| `acquisition--done.html` | 무반응 | 무반응 | X 없음 | `계약기록 보기`→`contracts.html`, `확인`→`acquisition.html` |
| `acquisition--signing.html` | 무반응 | 무반응 | X 없음 | `서명 진행 중`(비활성 표시) |
| `invest-assets--cert-confirm.html` | 무반응 | 무반응 | `<button class="close">` — **죽은 버튼** | `취소`→`invest-assets.html`, `발급`→`certificate.html` |

### B-4. 용어 해설 라이트박스 **[클릭]**

`https://payhug-investor-glossary.vercel.app/`, 여는 경로 = 본문 캡처 크롭(`.crop`, 50개) 클릭. 로컬 `glossary.html:2937-2998` 과 동일 코드.

| 조작 | 결과 |
|---|---|
| 오버레이(`.lb` 안 `.lb-in` 밖) | 닫힘 |
| 이미지(내부) 클릭 | **유지** |
| 상단바 빈 공간 클릭 | **유지** |
| ESC | 닫힘 |
| `닫기 (Esc)` 버튼 | 닫힘 |

이 라이트박스만 유일하게 제대로 짜여 있다 — `glossary.html:2994` 의 `!e.target.closest('.lb-in')` 가 안쪽을 걸러 낸다.
`role="dialog"`·`aria-modal="true"` 도 이것만 있다(`:2937`). 열면 `#lb-real` 로 포커스가 들어가고 닫으면 원래 버튼으로 되돌아간다(`:2978`, `:2982`).

---

## C. 부수 확인

| 항목 | 수정 전(배포) | 수정 후(로컬) | 실제 프론트 | 확인 방법 |
|---|---|---|---|---|
| 모달 열린 동안 배경 스크롤 | **스크롤됨** (뷰포트 1440×520, 휠 −500 → `window.scrollY` 0→135) | **스크롤됨** (동일) | 잠금 코드 0건 → 동일하게 스크롤됨 | **[클릭]** `Input.dispatchMouseEvent type:mouseWheel` |
| `body` overflow | `hidden auto`(원래 스타일) — 모달이 건드리지 않음 | 동일 | — | **[클릭]** `getComputedStyle` |
| `계약서보기` 본문 스크롤 | **동작** `.doc-scroll` `scrollTop` 0→400, 모달 유지. `scrollHeight` 1157 / `clientHeight` 466 | **동작** 0→400, `scrollHeight` 1383 로 증가(서명란 1열화 때문) | `TermsModal.tsx:42` 등 동일 구조 | **[클릭]** 휠 |
| 본문 텍스트 드래그 선택 | **드래그 중엔 선택됨**(57자) → **마우스업 순간 모달이 닫히고 선택이 사라짐**(선택 길이 0) | **정상** — 릴리스 후에도 선택 유지, 모달 열린 채 | 패널 `stopPropagation` 이라 정상 | **[클릭]** press→move→release 3단 분리 측정 |
| 안→밖 드래그 후 릴리스 | 닫힘 | 유지 | React 도 `click` 이 공통 조상(오버레이)에서 나므로 닫힘 | **[클릭]** |
| 모달 위에서 사이드바 메뉴 클릭 | 배경이 가로채 모달만 닫힘, 화면 전환 없음 | 모달 유지, 화면 전환 없음 | 오버레이가 가림 → 동일 | **[클릭]** + `elementFromPoint`=`DIV.modal-backdrop` |
| 포커스 트랩(Tab) | **없음.** Tab 10회 중 앞 6회가 배경 목록의 체크박스·`계약서보기` 링크로 감 | **없음**(동일) | 트랩 구현 0건 → 동일 | **[클릭]** `Tab` 키 10회 + `document.activeElement` 추적 |
| 열 때 포커스 이동 | 없음. `document.activeElement` = `BODY` | 없음 | 없음 | **[클릭]** |
| `role="dialog"`·`aria-modal` | 없음(`null`) | 없음 | 없음 | **[클릭]** |
| ESC | 전 모달 무반응 | 전 모달 무반응 | 전 모달 무반응(핸들러 0건) | **[클릭]** `key:"Escape"`, `keyCode:27` |

Tab 순서 실측(수정 전·후 동일, `계약서보기` 기준)
`OUT INPUT.chk` → `OUT A.doc-link` → `OUT INPUT.chk` → `OUT A.doc-link` → `OUT INPUT.chk` → `OUT A.doc-link` → `IN BUTTON.close` → `IN DIV.doc-scroll` → `IN BUTTON 닫기` → `IN A 계약서 원문 열기`

---

## D. 계약서보기 모달 서명란

`양도인 | 양수인` / `재양수인 | 유동화기관` 2열 격자를 만드는 코드는 **두 파일로 나뉜다.**

| 무엇 | 위치 | 내용 |
|---|---|---|
| 서명 당사자 4인과 각 필드 문자열 | `_pipeline/investor_admin/contract_text.py:43-48` `SIGN` | `“양도인”`·`“양수인”`·`“재양수인”`·`“유동화기관”` 4개 튜플, 각각 `상 호 :` `주 소 :` `대표이사 : (인)` |
| `<div class="ct-sign">` + `.ct-party` 마크업 생성 | `_pipeline/investor_admin/contract_text.py:105-111` `as_html()` | `SIGN` 을 순서대로 돌며 `.ct-party` 를 4개 뱉음. **격자가 아니라 평평한 4형제** |
| 2열 격자로 만드는 CSS | **`_pipeline/investor_admin/build_app.py:217`** | git HEAD `.doc-scroll .ct-sign { display: grid; grid-template-columns: 1fr 1fr; gap: 20px 24px; margin-top: 8px; }` |
| 산출된 HTML | `app.html:151`(수정 전) → 현재 `app.html:152` / `acquisition--doc.html:43` | 배포본에도 동일 |
| 삽입 지점 | `build_app.py:1009` `<div class="doc-scroll">` · `build_app.py:1073` `.replace('{CONTRACT}', contract_text.as_html('        '))` | 통합 프로토타입·낱장 둘 다 이 한 곳에서 나옴 |

`build_app.py` 밖에도 `contract_text.py` 를 쓰는 곳이 있다 — `build_sigtext.py:23·33` 이 `as_text()` 로 `assets/docs/정산금채권_재양도_합의서.txt` 를 찍는다. 텍스트본은 1열이라 격자와 무관하다.

현재 작업본에서는 `build_app.py:217` 이 `display: flex; flex-direction: column; gap: 20px;` 로 이미 바뀌었고, `app.html:152` 와 `acquisition--doc.html:43` 에 반영돼 있다. 배포본은 아직 2열이다.

---

## 고쳐야 할 모달

우선순위 순. 1~2는 로컬 작업본에서 이미 손이 들어갔으므로 **배포 반영이 남은 일**이다.

### 1. 배포 3주소의 `data-act="backdrop"` 판이 아직 서비스 중 (심각)

- 대상 — `payhug-investor-prototype.vercel.app`, `payhug-investor-demo.vercel.app/app.html`
- 영향 모달 4종 — `invest-assets-cert-confirm` · `acquisition-doc` · `acquisition-confirm` · `acquisition-done`
- 증상 — 본문 텍스트·빈 여백·헤더·스크롤 영역 어디를 눌러도 닫힘. 계약서 본문을 드래그해 읽으려 하면 손을 떼는 순간 모달이 사라지고 선택이 날아감
- 조치 — 현재 작업본의 `build_app.py` 로 `app.html` 재생성 후 `scripts/sync_prototype.py` 를 돌려 두 배포를 갱신. 그 뒤 §B-1 표를 다시 찍어 전 칸이 `유지` 인지 확인

### 2. `acquisition-confirm` · `invest-assets-cert-confirm` 낱장의 죽은 X 버튼 (중간)

- 대상 — `acquisition--confirm.html`, `invest-assets--cert-confirm.html`
- 증상 — 헤더 X 가 `<button class="close">` 인데 스크립트도 `href` 도 없어 아무 일도 일어나지 않음. 같은 세트의 `acquisition--doc.html` 은 `<a class="close" href="acquisition.html">` 로 정상 동작
- 조치 — `build_app.py` 의 낱장 생성부에서 이 둘의 X 를 `<a href="acquisition.html">` · `<a href="invest-assets.html">`(각 푸터 `취소` 와 같은 목적지)로 맞춤. 낱장 5종의 X 유무·동작을 한 규칙으로 통일

### 3. `acquisition-done` 에 X 도 `닫기` 도 없음 (낮음, 판단 필요)

- 오버레이 닫힘을 없앤 뒤 남는 닫힘 경로는 `확인`·`계약기록 보기` 두 버튼뿐이다. 둘 다 실제로 닫힌다 **[클릭]** 
- 실제 프론트 대조 — `ConfirmDialog.tsx:63-74` 도 X 없이 버튼만 둔다. 완료 알림 성격이면 현행 유지가 원본과 맞다
- 다만 `acquisition-confirm`(X 있음) 과 `acquisition-done`(X 없음) 이 같은 흐름 안에서 갈리므로, 흐름 단위로 X 정책을 하나로 정할 것

### 4. ESC 미지원 (개선 후보, 원본 대조상 결함 아님)

- 우리 5종 전부 무반응. 실제 프론트도 두 레포 통틀어 ESC 핸들러 0건이므로 **원본과 일치**
- 넣는다면 원본에 없는 동작을 추가하는 것이므로 별건으로 결정할 것. 넣을 경우 `acquisition-signing`(진행 중)은 제외해야 원본 규칙과 어긋나지 않음

### 5. 배경 스크롤 잠금 없음 (개선 후보, 원본 대조상 결함 아님)

- 모달이 떠 있어도 뒤 페이지가 휠로 움직인다 **[클릭 확인]** 
- 실제 프론트도 잠금 코드 0건이라 **일치**. 고칠 경우 원본과 달라지는 쪽이므로 별건 결정

---

## DOM만 보면 결함이나 실제로는 정상

| 항목 | DOM·소스만 보면 | 실제로 눌러 보면 |
|---|---|---|
| `acquisition-signing` 에 닫기 버튼·X·오버레이 핸들러가 하나도 없음 | 닫을 방법이 없는 모달로 보임 | 서명 진행 인디케이터다. 타이머가 끝나면 `acquisition-done` 으로 자동 전환된다. 실제 프론트도 진행 중 오버레이는 같은 방식이다 — `MerchantDocumentEditModals.tsx:33-40`, `partners/page.tsx:446-450`, `merchants/[id]/page.tsx:2142-2145`. **의도된 동작** |
| `acquisition-done` 푸터에 `data-act="modal-close"` 가 없음 | 닫기 경로 없음으로 오판하기 쉬움 | `확인`(`aq-done-ok`)·`계약기록 보기`(`aq-to-contracts`) 둘 다 실제로 닫힌다. 액션 이름만 다르다 |
| `.modal-body` 의 `scrollHeight === clientHeight` (552 = 552) | `계약서보기` 본문에 스크롤이 없다고 판정하기 쉬움 | 스크롤러는 `.modal-body` 가 아니라 그 안의 `.doc-scroll`(`max-height: 52vh; overflow-y:auto`)이다. 실측 `scrollHeight` 1157 / `clientHeight` 466, 휠로 0→400 이동 확인 |
| 수정 후 판에서 오버레이 클릭이 무반응 | 오버레이가 죽은 것처럼 보임 | 요구사항이 그것이다. 오버레이는 여전히 배경 클릭을 가로채 뒤 화면 조작을 막는다 — 모달 위에서 사이드바 메뉴 좌표를 눌러도 `elementFromPoint` 가 `DIV.modal-backdrop` 을 반환하고 화면이 바뀌지 않는다 |
| 낱장 `acquisition--doc.html` 의 X 를 눌렀더니 `.modal-backdrop` 이 사라짐 | 정상 닫힘으로 오판했었음 | 닫힌 게 아니라 `acquisition.html` 로 **페이지 이동**했다. X 가 `<a href>` 다. 정적 낱장은 원래 이동으로 상태를 표현한다 |
| 용어 해설 라이트박스에 `!e.target.closest('.lb-in')` 라는 한 줄뿐 | 우리 프로토타입과 같은 방식으로 보여 같은 결함을 의심 | `.lb-in` 이 패널 전체를 감싸고 있어 안쪽 클릭이 전부 걸러진다. 이미지 클릭·상단바 빈 공간 클릭 모두 **유지** 확인. ESC·닫기 버튼·배경 클릭 3경로 정상, 배경 스크롤도 `body.style.overflow='hidden'` 으로 잠긴다 |
| `payhug-investor-admin.vercel.app` 404 | 배포가 내려간 것으로 보임 | 그 이름의 배포가 애초에 없다. `README.md:9` 기준 세 번째 주소는 `payhug-investor-demo.vercel.app` 다 |
