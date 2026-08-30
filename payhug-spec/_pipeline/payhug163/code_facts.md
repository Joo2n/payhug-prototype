# PAYHUG-163 현행 코드 사실관계 — 가맹점 프론트

조사 대상 레포: `/Users/semi/cursor/payhug-merchant-web`
브랜치 `develop` / 커밋 `b2924e12fab38d2b98dd41da9639d32cd02ecc90` (2026-08-08)
경로 표기: 레포 루트 기준 상대경로 + 라인번호. 읽기 전용 조사(수정·커밋 없음).

---

## 1. 변경 대상 문자열 — 파일:라인 전수

### 1-1. 티켓 범위 내

| # | 티켓 항목 | 코드의 실제 문자열 | 위치 | 비고 |
|---|---|---|---|---|
| 1 | `모두 동의` → `전체 동의` | `모두 동의` | `app/signup/page.tsx:358` | 회원가입 1단계 최상단 체크박스. 레포 전체에서 유일 1건 |
| 2 | 락계좌 비밀번호 라벨 | **`계좌 출금 비밀번호 (숫자 4자리)`** | `app/contract/confirm-pre-payment/page.tsx:280`<br>`app/contract/confirm-pre-payment/page.tsx:397` | 티켓의 AS-IS `락계좌 출금 비밀번호 (숫자 4자리)`는 코드에 **없음**. 실제 라벨에 `락계좌` 없음. 동일 문자열 2곳(280=계좌정보 확인 스텝, 397=빠른조회 재점검 스텝) |
| 3 | 락계좌 비밀번호 오류 메시지 | `락계좌 출금 비밀번호 4자리를 입력해주세요.` | `app/contract/confirm-pre-payment/page.tsx:78`<br>`app/contract/confirm-pre-payment/page.tsx:167` | 티켓 AS-IS와 정확히 일치. 2곳(78=1원 인증 요청 전 검증, 167=빠른조회 재점검 전 검증) |
| 4 | 약관 개별 모달 버튼 `확인` → `동의` | `확인` | `components/TermsModal.tsx:51` | **공용 컴포넌트 1곳**. 계약 약관(`app/contract/terms/page.tsx:645`)과 **회원가입 약관(`app/signup/page.tsx:536`)이 동일 컴포넌트를 공유** → 한 줄 수정이 두 화면에 동시 반영 |
| 5 | 출금 전용 계좌 사진 첨부 화면 | `사장님의 선정산 전용 계좌 통장 사진을 첨부해 주세요` | `app/contract/upload-pre-payment/page.tsx:111` | `선정산 전용 계좌` 부분 |
| 5 | 〃 | `하나은행 출금 전용 락계좌` | `app/contract/upload-pre-payment/page.tsx:124` | 인포박스 제목 |
| 5 | 〃 | `…반드시 <strong>출금 전용 락계좌</strong> 통장을 첨부해 주세요.` | `app/contract/upload-pre-payment/page.tsx:128` | 인포박스 본문. `출금 전용 락계좌`가 `<strong>` 태그로 분리돼 있음 |
| 6 | 입금 받을 계좌 사진 첨부 화면 | `…출금 전용 락계좌가 아닌지 확인해 주세요.` | `app/contract/upload-settlement/page.tsx:170` | 인포박스 본문 |
| 7 | `펌뱅킹 출금 전용 계좌` (용어 병기 검토) | **`펌뱅킹 출금전용 계좌`** (띄어쓰기 없음) | `app/contract/apply-pre-payment/page.tsx:73` | 계좌 개설 안내 화면. 티켓 표기와 띄어쓰기 다름 |
| 7 | `출금 전용 계좌 사진을 첨부해 주세요` (용어 병기 검토) | `<span>출금 전용</span> 계좌 사진을 첨부해 주세요` | `app/contract/upload-pre-payment/page.tsx:108` | h1 제목. `출금 전용`이 강조 `<span>`으로 분리돼 **한 문자열이 아님** → 단순 치환 불가, 마크업 재구성 필요 |

### 1-2. 티켓에 명시되지 않았으나 같은 플로우(계약)에 있는 동일 용어 — 병행 검토 대상

| 문자열 | 위치 | 화면 |
|---|---|---|
| `선정산 전용계좌(락계좌)는 하나은행만 등록 가능합니다. 하나은행 계좌를 등록해주세요.` | `app/contract/confirm-pre-payment/page.tsx:73` | 계좌 확인(은행 제한 오류 모달) |
| `락계좌 입금내역을 자동으로 확인하려면 하나은행 빠른조회 서비스 가입이 필요합니다.` | `app/contract/confirm-pre-payment/page.tsx:443` | 빠른조회 가이드 아코디언 본문 |
| `purposeLabel = "선정산 전용 계좌"` (PRE_PAYMENT일 때) | `app/contract/confirm-pre-payment/page.tsx:193` | 계좌 확인 화면 제목·완료 모달 메시지에 주입(240, 208행) |
| `선정산 전용 계좌(락계좌) 통장사진` | `app/contract/page.tsx:180` | 계약 준비 스텝 목록 3번 항목 |
| `출금전용 계좌를 먼저 개설 후, 입출금 계좌를 개설해 주세요` | `app/contract/apply-pre-payment/page.tsx:121` | 계좌 개설 안내 유의사항 |
| `일반 입출금 계좌를 먼저 개설하면 20일 뒤에 출금전용 계좌 개설이 가능해요` | `app/contract/apply-pre-payment/page.tsx:122` | 〃 |
| `선정산금이 입금되는 전용 계좌` | `app/contract/apply-pre-payment/page.tsx:74` | 계좌 종류 안내 카드 부제 |
| `출금만 가능` (배지) | `app/contract/upload-pre-payment/page.tsx:125` | 인포박스 배지 |
| `먼저 선정산 전용계좌 등록을 완료해 주세요.` | `app/contract/upload-settlement/page.tsx:44` | 진입 가드 모달 메시지 |
| `선정산 전용계좌의 하나은행 빠른조회 가입이 완료되어야 …` | `app/contract/upload-settlement/page.tsx:47` | 진입 가드 모달 메시지 |
| `선정산 전용계좌 먼저 등록해주세요` / `선정산 전용계좌로 이동` | `app/contract/upload-settlement/page.tsx:268`, `271` | 진입 가드 모달 제목·버튼 |

### 1-3. 티켓 범위 밖 (계약 플로우가 아닌 화면·주석·서비스 레이어)

| 문자열 | 위치 | 성격 |
|---|---|---|
| `통장사본 (선정산 전용계좌)` / `통장사본 (입출금 전용계좌)` | `app/my-info/contract/page.tsx:29`, `30` | 내 정보 > 계약 정보, 첨부 유형 라벨 상수 |
| `선정산 전용계좌` / `입출금 전용계좌` | `app/my-info/contract/page.tsx:49`, `50` | 내 정보, 계좌 용도(ACCOUNT_PURPOSE) 라벨 상수 |
| `법인 사업자도 전용계좌 개설할 수 있나요?` 외 FAQ 본문 다수(`전용계좌` 총 10회 이상) | `app/page.tsx:380`, `381`, `385`, `389`, `405`, `409` | 랜딩 FAQ |
| `계좌 입금 내역의 입금 계좌는 항상 하나은행(정산 전용 계좌)` | `app/settlement/account/page.tsx:14` | 코드 주석(화면 노출 없음) |
| `락계좌 빠른조회 가입 재점검 …` | `services/contractService.ts:138`, `139` | JSDoc 주석(화면 노출 없음) |
| `… 선정산 전용계좌 준비 여부 확인용.` | `services/contractService.ts:64` | JSDoc 주석 |

> 정산 화면(`app/settlement/**`)에는 `락계좌`·`출금 전용` 표기가 **화면 문구로는 존재하지 않음**. 주석 1건뿐.

### 1-4. 미발견

- `락계좌 출금 비밀번호 (숫자 4자리)` — 코드에 없음. 실제 라벨은 `계좌 출금 비밀번호 (숫자 4자리)`(§1-1 #2).
- `펌뱅킹 출금 전용 계좌`(띄어쓰기 포함) — 코드는 `펌뱅킹 출금전용 계좌`.
- `출금 전용 계좌 사진을 첨부해 주세요`(단일 문자열) — 마크업 분리로 단일 문자열 부존재.
- `전체 동의`·`전체동의`·`일괄 동의` — 레포 전체 0건. 즉 신규 문구.
- 상환전용 / 상환 전용 — 레포 전체 0건.

---

## 2. 약관 동의 화면 구조

### 2-1. 계약 약관 동의 — `app/contract/terms/page.tsx` (717행)

| 항목 | 사실 |
|---|---|
| 약관 목록 출처 | **서버 API**. `fetch(getSpringApiUrl("/terms?type=contract"))` — 79행. 배열·상수·i18n 등 **프론트 하드코딩 없음** |
| 타입 | `Term { id, code, name, title, content, is_required, is_active, version, effective_date }` — `components/TermsModal.tsx:3-13`에서 export |
| 상태 관리 | 폼 라이브러리 없음. 순수 `useState`.<br>`terms: Term[]` (29행), `agreements: Record<number, boolean>` (30행), `selectedTerm: Term \| null` (31행) |
| 초기값 | 목록 수신 즉시 전 항목 `false`로 초기화 — 83~85행 |
| 개별 토글 | `handleIndividualAgree(id)` — 256~258행. 체크박스/행 클릭 시 즉시 토글(전문 열람 강제 없음) — 448행 |
| 전문 모달 열기 | 우측 `>` 꺾쇠 버튼 `setSelectedTerm(term)` — 464~468행 |
| 모달 컴포넌트 | `components/TermsModal.tsx` (57행). 렌더 위치 `app/contract/terms/page.tsx:645-649` |
| 모달 확인 동작 | `handleConfirmTerm(id)` — 260~263행. **해당 약관 체크 + 모달 닫기**(`setSelectedTerm(null)`) |
| 모달 X 닫기 | `onClose` → 체크 없이 닫힘 (`TermsModal.tsx:29`) |
| "다음 단계 진행하기" 버튼 | 480~490행. 활성 조건 `isRequiredAgree && !isSubmitting`.<br>`isRequiredAgree` = 265~267행: `terms.length > 0 && terms.filter(is_required).every(agreements[id])` |
| 라벨 형식 | `({필수\|선택}) {term.name}` — 460~462행. **접미 "동의" 없음** |
| 전체 동의 체크박스 | **없음** (개별 토글만 존재) |
| 클릭 시 동작 | `handleNextStep` — 270~325행. 약관 동의 자체를 저장하지 않고, 계약 참여자 조회 후 FastAPI `/signature/generate-contract`로 계약서 미리보기 생성 |

### 2-2. 회원가입 약관 동의 — `app/signup/page.tsx` (555행, step 1)

| 항목 | 사실 |
|---|---|
| 약관 목록 출처 | 서버 API `fetch(getSpringApiUrl("/terms?type=signup"))` — 88행. 하드코딩 없음 |
| 상태 관리 | `terms` (21행), `agreements: Record<number, boolean>` (22행), **`allAgree: boolean`** (23행), `selectedTerm` (24행). 모두 `useState` |
| 전체 동의 ↔ 개별 연동 | 양방향.<br>· `handleAllAgree()` — 131~139행: `allAgree` 반전 후 **전 항목을 동일 값으로 일괄 설정**(선택 약관 포함)<br>· `handleIndividualAgree(id)` — 141~148행: 개별 토글 후 `terms.every(next[id])`로 `allAgree` 재계산<br>· `handleConfirmTerm(id)` — 150~158행: 모달 확인 시 체크 + `allAgree` 재계산 |
| 전체 동의 UI | 346~359행. 체크박스 28×28, 라벨 `모두 동의`(358행, `font-bold`). 개별 항목보다 위, 별도 구분선 없음 |
| 개별 항목 라벨 | `({필수\|선택}) {term.name} 동의` — 375~377행. **접미 "동의" 있음**(계약 화면과 상이) |
| 다음 버튼 | 394~404행. 활성 조건 `isRequiredAgree`(160~162행, 필수 항목 전부 체크). 클릭 시 `setStep(2)`만 수행 — **API 호출 없음** |
| 모달 | 동일 `components/TermsModal.tsx` (536~540행) |

### 2-3. 계약 약관 6개 표시명·순서

프론트 레포(`payhug-merchant-web`)에는 약관 목록이 없다 — 이름·순서·필수여부 전부 **서버(Spring `/terms?type=contract`) 응답 순서**를 그대로 `terms.map()`으로 렌더한다(`app/contract/terms/page.tsx:446`).

코드로 확인 가능한 유일한 목록은 과거 스냅샷 사본의 dev 목킹 데이터 `/Users/semi/cursor/payhug/02_payhug-merchant-web-main/lib/devMockData.ts:225-292` (현행 `payhug-merchant-web/develop`에는 `lib/devMockData.ts` 파일 자체가 없음):

| 순서 | id | code | name(=표시명) | 필수 |
|---|---|---|---|---|
| 1 | 11 | `PRE_SETTLEMENT_SERVICE_AGREEMENT` | 선정산 서비스 계약 약관 | 필수 |
| 2 | 12 | `THIRD_PARTY_PROVISION_CONTRACT` | 개인정보 제3자 제공 동의(계약) | 필수 |
| 3 | 13 | `AUTO_DEBIT_AGREEMENT` | 출금이체 동의 및 해지 통지 안내 | 필수 |
| 4 | 14 | `SERVICE_FEE_DEBIT` | 서비스 이용수수료 출금 동의 | 필수 |
| 5 | 15 | `CREDIT_INFO_PROVISION` | 개인(신용)정보 제공 동의 | 필수 |
| 6 | 16 | `UNIQUE_ID_PROVISION` | 고유식별정보 제공 동의 | 필수 |

6개 전부 `is_required: true` → 6개 모두 체크해야 "다음 단계 진행하기" 활성.
(참고) 회원가입 약관은 4개: `서비스 이용약관`(필수) / `개인정보 수집 및 이용`(필수) / `고유식별 정보처리`(필수) / `마케팅 활용 및 정보 수신`(선택) — `devMockData.ts:179-223`.

> 주의: 위 목록은 목킹 값이다. 운영 DB의 실제 표시명·순서와 일치하는지는 백엔드 확인 필요(§5 확인 필요 항목).

### 2-4. 동의 상태 저장 시점 — 로컬 상태

- **계약**: `agreements`는 컴포넌트 `useState`. 화면 진입 때마다 목록을 다시 받아 **전부 `false`로 초기화**(83~85행). 서버로는 마지막 단계 `handleContractSave`(363~401행)에서 `POST /contracts` 바디의 `agreedTermsIds`로 **한 번에** 전송(369~372행). 그 전 단계에서 동의 상태를 저장·조회하는 API 호출 없음.
- **회원가입**: 동일. `POST /auth/signup` 바디의 `agreements` 배열로 최종 전송(260행). step 1→2 이동은 로컬 `setStep(2)`뿐.
- **저장된 동의 조회**: 계약 완료 이후에만 존재. `GET /merchants/my-detail?businessId=`(`services/myContractService.ts:5-12`) → `ContractAgreement { termsId, termsTitle, termsContent, agreedAt, ipAddress }`(`types/myContract.ts:79-86`)를 내 정보 화면에서 표시(`app/my-info/contract/page.tsx:470`, `480`).
- `sessionStorage`/`localStorage`에 동의 상태를 담는 코드 없음(회원가입의 sessionStorage 사용은 partnerCode 등 귀속 코드 전용, 74~82·263~268행).

**판단 근거**: 티켓의 "이탈 시 동의된 항목만 체크 유지"는 현행 코드로는 **구현되어 있지 않다**. 새로고침·이탈 시 전체 초기화된다. 구현하려면 (a) 로컬 저장(sessionStorage/localStorage) 또는 (b) 중간 저장 API 신설 중 택일이 필요하며, 현재는 어느 쪽도 없다.

---

## 3. 전체 동의 순차 모달 구현 시 손댈 파일 후보

| 파일 | 손댈 내용 | 난이도 |
|---|---|---|
| `app/contract/terms/page.tsx` | ① `allAgree` state 신설 ② 목록 상단에 전체 동의 행 추가(마크업은 `app/signup/page.tsx:346-359` 재사용 가능) ③ 순차 모달 커서 state(예: `modalQueueIndex`) ④ `handleConfirmTerm`을 "체크 후 닫기"(260~263행)에서 "체크 후 **다음 약관 모달 열기**"로 분기 ⑤ 중도 이탈 시 지금까지 동의분만 유지 | 중 — 상태 하나가 아니라 "큐 진행 + 개별 열람" 두 진입 경로를 한 모달이 겸해야 함 |
| `components/TermsModal.tsx` | ① 버튼 라벨 `확인`→`동의`(51행) ② 순차 모드용 props 추가(진행도 `n/6`, 마지막 항목에서 라벨·동작 분기) | 중 — **회원가입과 공유 컴포넌트**. 라벨 변경이 회원가입 모달에도 그대로 적용됨. 순차 모드를 넣을 경우 옵셔널 props로 기존 호출부(회원가입) 무영향 보장 필요 |
| `app/signup/page.tsx` | `모두 동의`→`전체 동의`(358행) 문구만. 순차 모달을 회원가입에도 적용한다면 `handleAllAgree`(131~139행)·`handleConfirmTerm`(150~158행) 동시 개편 | 하 (문구만) / 중 (순차 적용 시) |
| `app/contract/confirm-pre-payment/page.tsx` | 라벨 2곳(280·397), 오류 메시지 2곳(78·167). 필요 시 73·443·193행 동반 정정 | 하 — 문자열 치환 |
| `app/contract/upload-pre-payment/page.tsx` | 108(제목, `<span>` 분리로 마크업 조정 필요)·111·124·128행 | 하~중 — 108행만 마크업 재구성 |
| `app/contract/upload-settlement/page.tsx` | 170행. 진입 가드 문구(44·47·268·271)는 정책 판단 후 | 하 |
| `app/contract/apply-pre-payment/page.tsx` | 73·74·121·122행 (용어 병기 검토 결과에 따라) | 하 |
| `app/contract/page.tsx` | 180행 스텝 제목 | 하 |

**소견**
- 문자열 교체(1~7번)는 전부 단일 파일 지역 수정으로, 마크업이 분리된 `upload-pre-payment/page.tsx:108`·`:128` 두 곳만 태그 경계를 고려하면 된다. 리스크 낮음.
- `TermsModal`의 `확인`→`동의`는 **회원가입 약관 모달까지 함께 바뀐다**. 계약에만 적용할지, 회원가입도 함께 `동의`로 통일할지 기획 결정이 선행돼야 하며, 계약만 바꾸려면 props 분기(예: `confirmLabel`)가 필요하다.
- 전체 동의 순차 모달의 실질적 난점은 UI가 아니라 상태 설계다: 현재 `handleConfirmTerm`은 "체크+닫기" 한 가지 동작만 하고, 모달은 `selectedTerm` 단일 값으로만 제어된다. 순차 진행을 넣으면 (a) 큐 진행 중 X로 닫았을 때 지금까지 동의분 유지, (b) 개별 꺾쇠 열람은 종전대로 단건 처리, 두 경로를 구분해야 한다. 순차 큐 인덱스 state 추가와 `handleConfirmTerm` 분기로 처리 가능한 수준.
- 약관 표시명·순서·개수는 프론트가 결정하지 않는다. "6개" 전제는 서버 `/terms?type=contract` 응답에 의존하므로, 순차 모달의 진행도 표기(`n/6`)는 하드코딩하지 말고 `terms.length` 기준으로 계산해야 한다.

---

## 4. 확인 필요

- 운영 DB 기준 계약 약관 6개의 실제 표시명·정렬 순서 (프론트에 근거 없음. §2-3 표는 dev 목킹 값)
- `TermsModal` 확인 버튼 라벨 변경 범위 — 계약 전용 / 회원가입 포함 통일
- 티켓 AS-IS와 코드 실제 문자열의 불일치 3건(§1-4) 처리 방향 — 티켓 표기를 코드 기준으로 정정할지
- "이탈 시 동의 항목 유지"의 저장 매체 — 로컬 저장 vs 중간 저장 API 신설 (현행 코드에 어느 쪽도 없음)
- `펌뱅킹 출금전용 계좌`(은행 상품명)를 서비스 용어로 바꿀지, 병기할지
