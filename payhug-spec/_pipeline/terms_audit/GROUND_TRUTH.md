# 약관(terms) 로직 진실 원천 — 프론트 코드 기준

출처(진실): `payhug-merchant-web/` (실행 레포, 사본 `payhug/02_payhug-merchant-web-main/`)
- 약관은 **백엔드 API에서 동적 로드** — 프론트 하드코딩 아님:
  - signup: `app/signup/page.tsx:88` → `fetch("/terms?type=signup")`
  - contract: `app/contract/terms/page.tsx:79` → `fetch("/terms?type=contract")`
  - service: `services/contractService.ts:151` → `GET /terms?type=${type}`
- **약관명·내용·필수여부는 서버/DB 값** → 백엔드 없으면 알 수 없음. 디자인이 임의로 지어내면 안 됨.
- dev 목킹(=서버 미러, 사실상 유일한 확정 소스): `payhug/02_payhug-merchant-web-main/lib/devMockData.ts`

## A. SIGNUP 약관 (`/terms?type=signup`) — 4개 (devMockData L179–223)
| id | code | name | 필수/선택 |
|----|------|------|-----------|
| 1 | SERVICE_AGREEMENT | 서비스 이용약관 | **필수** |
| 2 | PRIVACY_COLLECTION | 개인정보 수집 및 이용 | **필수** |
| 3 | UNIQUE_IDENTIFIER | 고유식별 정보처리 | **필수** |
| 4 | MARKETING | 마케팅 활용 및 정보 수신 | 선택 |

## B. CONTRACT 약관 (`/terms?type=contract`) — 6개, **전부 필수** (devMockData L225–291)
| id | code | name | 필수/선택 |
|----|------|------|-----------|
| 11 | PRE_SETTLEMENT_SERVICE_AGREEMENT | 선정산 서비스 계약 약관 | **필수** |
| 12 | THIRD_PARTY_PROVISION_CONTRACT | 개인정보 제3자 제공 동의(계약) | **필수** |
| 13 | AUTO_DEBIT_AGREEMENT | 출금이체 동의 및 해지 통지 안내 | **필수** |
| 14 | SERVICE_FEE_DEBIT | 서비스 이용수수료 출금 동의 | **필수** |
| 15 | CREDIT_INFO_PROVISION | 개인(신용)정보 제공 동의 | **필수** |
| 16 | UNIQUE_ID_PROVISION | 고유식별정보 제공 동의 | **필수** |

> 각 term은 `title`, `content`(전문), `version`, `effective_date` 보유. 전문 텍스트 존재함.

## C. 인터랙션 로직 (코드 기준)

### SIGNUP (`app/signup/page.tsx`)
- **모두 동의** 있음 (`handleAllAgree`, L131) — 최상단, 클릭 시 전체 체크/해제.
- 각 행: `[체크박스] (필수/선택) {name} 동의` + 우측 `>` 꺾쇠.
- **체크박스/행 클릭 → 직접 토글**(`handleIndividualAgree`) — 전문 안 봐도 체크 가능.
- **`>` 꺾쇠 → 전문 모달**(`setSelectedTerm` → 공용 TermDetail 모달, title+content) → 모달 "확인"(`handleConfirmTerm`) 누르면 **자동 체크+닫힘**. X(onClose)는 체크 없이 닫힘.
- 라벨 접미 **"동의"** 포함: `(필수) 서비스 이용약관 동의`.
- 필수 전부 체크 시 다음 진행 활성(`isRequiredAgree`).

### CONTRACT (`app/contract/terms/page.tsx`)
- **모두 동의 없음** — 개별 토글만(`handleIndividualAgree`, L256).
- 각 행: `[체크박스] (필수/선택) {name}` + 우측 `>` 꺾쇠. (**"동의" 접미 없음**, 이름만)
- **체크박스/행 클릭 → 직접 토글**. **`>` 꺾쇠 → 전문 모달**(`setSelectedTerm` L467) → "확인"(`handleConfirmTerm` L260)이 체크+닫힘.
- 6개 전부 필수라 **6개 모두 체크해야** "다음 단계 진행하기" 활성(`isRequiredAgree`, L265).
- `>` 꺾쇠 아이콘 = `M9 18L15 12L9 6`(SVG), 색 `#7e8299`.

## D. 이미 확인된 오류 예시 (Figma 1836 = MC_CONTRACT_TERMS_AGREE, 손으로 그린 화면)
현재 표시(잘못): (필수)선정산 서비스 이용약관 / (필수)개인정보 수집·이용 동의 / (필수)매출채권 양도 동의 / (선택)개인정보 제3자 제공 동의 / (선택)마케팅 정보 수신 동의
- "매출채권 양도 동의" = **존재하지 않는 약관(지어냄)**
- "개인정보 수집·이용", "마케팅 수신" = **signup 약관을 contract에 잘못 삽입**
- "개인정보 제3자 제공" = 실제는 **필수**인데 선택으로 오표기, 이름도 "(계약)" 누락
- 개수 5개(3필수+2선택) — 실제 contract는 **6개 전부 필수**
- 전체동의는 현재 contract 앱엔 없음(디자인의 "신규 추가" 제안은 별도 확인필요 항목으로 유지 가능)
