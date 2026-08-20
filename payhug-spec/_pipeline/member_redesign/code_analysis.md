# 어드민 프론트 코드 분석 — 정산상품 참조 인벤토리 · 회원관리 재사용 요소

> 대상 레포: `/Users/semi/cursor/payhug-admin-web` (main, `5f9297e` 2026-07-24). 읽기 전용 분석 — 코드 수정 0건.
> 파일 경로는 레포 루트 기준. v2 §19의 12개 지시를 프론트 관점으로 조사. 서버(백엔드) 내부는 보이지 않으므로 해당 몫은 전부 `서버 확인 필요`로 표기.

## ① 요약

1. 회원관리(`app/partners/page.tsx`)는 목록·등록/수정 모달·프로필 모달·서비스·타입이 모두 갖춰져 있고, `parentUserId`(직속 상위 1명) 필드가 이미 존재한다 — TO-BE 화면의 뼈대로 전부 재사용 가능.
2. 다만 상위 후보 필터가 "활성 + 자기 자신 제외"뿐이라(유형 제한 없음) 유형→직속 상위 규칙은 신규 로직이다 (`app/partners/page.tsx:860~866`).
3. 회원 유형(`userType`)은 PARTNER 단일 값 — 상·하위 파트너 구분은 회원 데이터에 없고, 정산상품 참여자 슬롯(`upperPartnerId`/`lowerPartnerId`)과 계약 서명자 role(`UPPER_PARTNER`/`LOWER_PARTNER`)에서만 발생한다.
4. 수수료율은 100% 정산상품(`fee policy`) 객체 속성이다. 관계(Edge)에 요율을 담을 기존 모델·API는 프론트에 전무 — `MemberContractRelation`형 신설이 전제.
5. 정산상품 참조 화면은 4곳: 상품관리(`/settlement/policies`), 시뮬레이션(`/settlement/simulation`), 가맹점 상세 배정(`/merchants/[id]`), 사이드바 메뉴(`AdminLayout`). API는 `/admin/settlement/policies`(CRUD)·`/admin/settlement/assignments`(배정)·`/admin/settlement/simulate` 3계열.
6. 가맹점 상세의 "정산 실행 활성화"가 배정(assignment) 존재를 전제조건으로 삼는다 — 정산상품 제거 시 이 게이트의 대체 기준(관계 존재?)이 필요 (`app/merchants/[id]/page.tsx:945~953`).
7. 거래유형(txType CARD/DELIVERY)은 배정·시뮬레이션·정산 표시 전반의 축 — 관계 기반 전환 시 "거래유형별 요율 차등"을 관계에 어떻게 담을지가 미결.
8. 추천코드(referralCode)는 가입 URL 생성 전용으로 `parentUserId` 체인과 데이터상 무관하나, 링크의 코드가 가입 가맹점의 계약 파트너 체인 시작점을 정한다는 운영 전제가 주석에 있다 (`app/partners/page.tsx:694~695`).
9. 예외 로직 현황: 비활성 상위 제외 있음 / 순환 방지 없음(자기 자신만 제외) / 다중 상위 구조상 불가(단일 필드) / 상위 변경은 이력 없는 단순 덮어쓰기.
10. 다우(DAOU) 트랙은 정산상품의 `ruleType`으로만 존재(참여자 슬롯 = 상위영업/하위영업) — 정산상품을 없애면 다우 체인을 관계로 어떻게 표현할지가 별도 미결(P4).

## ② 회원관리 재사용 요소 (조사항목 1·3·5)

### 화면·컴포넌트

| 요소 | 근거 (파일:줄) | 현재 상태 | TO-BE 재사용 판단 |
|---|---|---|---|
| 회원 목록 테이블 (11컬럼: ID·이름·아이디/전화·유형·법인·추천코드·상위 회원·상태·사업자등록증·직인·관리) | `app/partners/page.tsx:1298~1435` | `parentUserName` 텍스트 표시 컬럼 보유 (1352~1358) | 재사용. '직속 상위'로 명칭만, '직속 계약 수수료율'·'계약 구조' 컬럼은 신규 |
| 유형 필터 탭 + 검색 | `app/partners/page.tsx:1261~1286` | userType 탭 + 이름/아이디 검색 | 재사용 |
| 등록/수정 모달 `PartnerFormModal` | `app/partners/page.tsx:833~1051` | 이름·아이디/휴대폰·비밀번호·유형·법인·사업자·추천코드·상위 회원·상태(수정 시) | 기본 정보부 전부 재사용. 상위 회원 select(996~1010)를 검색형 + 유형 자동 제한으로 교체, 관계 수수료율 세트·Preview는 신규 |
| 상위 후보 계산 `parentCandidates` | `app/partners/page.tsx:860~866` | `status === "ACTIVE" && id !== editTargetId`만 필터. **유형 제한 없음** — 전체 활성 회원이 후보 | 필터 조건에 유형 규칙 추가 필요(신규 로직) |
| 수정 시 스코프 밖 상위 보존 | `app/partners/page.tsx:867~871` | 기존 상위가 조회 스코프(자기+하위) 밖이면 옵션에 unshift하여 "없음(최상위)" 오표시 방지 | 재사용 (관계 편집에서도 동일 문제 발생) |
| 프로필 모달 `ProfileModal` (사업자정보 + OCR + 직인) | `app/partners/page.tsx:108~454` | 회원의 사업자/법인/개인 프로필. 계약 관계 정보 없음 | 재사용. [직속 계약 관계] 섹션은 신규 |
| 가입 링크 생성기 `SignupLinkGenerator` | `app/partners/page.tsx:688~803` | referralCode 기반 URL 생성 — 파트너/제휴사/영업 3드롭다운 | **폐기** — R4·R5(난수 가입 링크 자동 발급)로 대체. 병행 기간(Q2ⓑ) 중 구 생성기 및 기배포 partnerCode/salesCode URL의 유효성(유지/차단)은 확인 필요 (§⑤-추천코드 참조) |
| 비활성화/삭제 확인 다이얼로그 | `app/partners/page.tsx:1191~1227` | 삭제 안내문에 "정산 상품에 배정된 경우 삭제할 수 없습니다"(1214) | 재사용하되 안내문 문구는 관계 기준으로 대체 대상 |
| 유형 상수 (`USER_TYPE_OPTIONS`/`LABELS`/`BADGE`) | `app/partners/page.tsx:29~62` | INVESTOR·PAYHUG·PARTNER·AFFILIATE·SALES·SALES_ORG·ADMIN 7종 | 재사용. '상위파트너/하위파트너' 값은 없음 |

### 서비스·타입·API

| 요소 | 근거 | 현재 상태 | 재사용 판단 |
|---|---|---|---|
| `PartnerItem` 타입 | `services/partnerService.ts:8~23` | `userType`·`referralCode?`·`parentUserId?`·`parentUserName?` 보유. 요율 필드 없음 | 재사용 + 관계 요율 필드(또는 별도 relation 응답)는 서버 확장 필요 |
| `CreatePartnerPayload`/`UpdatePartnerPayload` | `services/partnerService.ts:25~46` | `parentUserId?: number \| null` 포함, 요율 없음 | 재사용 + 관계 요율 세트 파라미터는 서버 확장 필요 |
| `fetchPartners(userType?)` | `services/partnerService.ts:51~54` | GET `/admin/partners?userType=` — 유형별 조회 지원 | **직속 상위 검색 Select의 데이터 소스로 그대로 사용 가능** |
| `createPartner`/`updatePartner`/`deletePartner`/`deactivatePartner` | `services/partnerService.ts:56~70` | POST/PUT/DELETE/PATCH `/admin/partners` | 재사용 |
| `fetchCreatableTypes` | `services/partnerService.ts:73~75` | GET `/admin/partners/creatable-types` — 서버가 등록 가능 유형을 내려줌 | **유형별 규칙을 서버 주도로 확장할 수 있는 기존 패턴** (상위 유형 규칙도 유사 API로 받을 수 있음 — 서버 확인 필요) |
| 유형별 유저 조회 (참여자 select용) | `app/settlement/policies/page.tsx:227~237`, `services/settlementService.ts:81~83` | GET `/admin/settlement/users?userType=` | 상위 회원 검색의 대체/보조 소스로 재사용 가능 |
| 프로필 API | `app/partners/page.tsx:127, 221, 225` | GET/PUT `/admin/partners/{id}/profile`, POST `/admin/partners/{id}/business-registration` | 재사용 |

### 수수료율을 관계로 옮길 기존 모델 유무 (조사항목 5)

- 회원 간 관계는 `parentUserId` 단일 스칼라가 전부 (`services/partnerService.ts:17`) — 요율·적용기간·상태를 담을 자리가 없다.
- 기간(effective) 필드를 가진 프론트 모델은 약관(`services/termsService.ts:39~40` `effectiveFrom/To`)과 가맹점-상품 배정(`types/settlement.ts:26` `Assignment.validFrom`)뿐. 둘 다 회원 간 관계가 아니다.
- `contract`·`relation`류 회원 간 모델 검색 결과 없음 → 프론트 기준 **v2 §12의 `MemberContractRelation` 신설이 전제**. 서버에 유사 테이블이 있는지는 서버 확인 필요.

## ③ 정산상품(fee policy) 참조 인벤토리 (조사항목 4)

### 화면

| 화면 | 근거 | 참조 내용 |
|---|---|---|
| 정산 상품관리 `/settlement/policies` | `app/settlement/policies/page.tsx:149~655` | 상품 목록·생성·수정·비활성화·삭제. 참여자 칩(405~446)·옵션 칩(448~485)·요율 표(591~628) 렌더 |
| 상품 폼 모달 `PolicyFormModal` | `app/settlement/policies/PolicyFormModal.tsx:119~469` | ruleType(일반/다우) 선택(184~198), 참여자 select 7슬롯(211~264), 납부 옵션(277~308), 수취 옵션(318~370), 요율 표(373~440: %·원, VAT 별도/포함) |
| 정산 시뮬레이션 `/settlement/simulation` | `app/settlement/simulation/page.tsx:75~99, 142~143, 209~247, 375` | 카드/배달 정책 select 2개, simulate 요청에 `cardPolicyId`/`deliveryPolicyId`, 결과에 `policyName(ruleType)` 표시 |
| 가맹점 상세 `/merchants/[id]` — 정산 상품 배정 | `app/merchants/[id]/page.tsx:75, 121~122, 204~210, 271~283, 1704~1753` | 배정 목록(routing rule: txType 배지·ruleType 배지·policyName·validFrom), 배정 폼(txType + 상품 select), POST `/admin/settlement/assignments` |
| 가맹점 상세 — 정산 실행 토글 게이트 | `app/merchants/[id]/page.tsx:945~953, 1642~1650, 2196~2215` | `assignments.length === 0`이면 활성화 차단 + "정산 상품 배정 필요" 다이얼로그·문구 |
| 사이드바 메뉴 | `components/AdminLayout.tsx:74~75` | 정산 그룹 "정산 상품관리" 항목. 참여자용 메뉴(156~200)에는 이 항목 없음(관리자 전용) |
| 회원 삭제 다이얼로그 문구 | `app/partners/page.tsx:1214` | "정산 상품에 배정된 경우 삭제할 수 없습니다" — 회원↔상품 참조 제약의 프론트 흔적 |

### API (프론트에서 호출하는 엔드포인트)

| 엔드포인트 | 근거 | 용도 |
|---|---|---|
| GET `/admin/settlement/policies` | `app/settlement/policies/page.tsx:166`, `app/settlement/simulation/page.tsx:89`, `app/merchants/[id]/page.tsx:205`, `services/settlementService.ts:9~10` | 목록 (3개 화면 공용) |
| GET/POST/PUT `/admin/settlement/policies(/{id})` | `app/settlement/policies/page.tsx:380~388`, `services/settlementService.ts:13~22` | 단건·생성·수정 |
| PATCH `/admin/settlement/policies/{id}/deactivate` | `app/settlement/policies/page.tsx:194` | 비활성화 ("배정된 가맹점 이력은 유지" 문구 189) |
| DELETE `/admin/settlement/policies/{id}` | `app/settlement/policies/page.tsx:215`, `services/settlementService.ts:25~26` | 완전 삭제 ("배정된 가맹점이 있으면 삭제할 수 없습니다" 문구 210) |
| GET `/admin/settlement/assignments/business/{businessId}` | `app/merchants/[id]/page.tsx:204` | 가맹점의 배정(routing rule) 목록 |
| POST `/admin/settlement/assignments` | `app/merchants/[id]/page.tsx:274~277` | 배정: `{merchantId, businessId, feePolicyId, txType}` |
| POST `/admin/settlement/simulate` | `app/settlement/simulation/page.tsx:144~148` | `cardPolicyId`/`deliveryPolicyId`로 원장·배분 시뮬레이션 |
| GET `/admin/settlement/users?userType=` | `app/settlement/policies/page.tsx:229` | 상품 참여자 후보 조회 |

### 타입·상수

| 항목 | 근거 | 내용 |
|---|---|---|
| `Policy`/`PolicyRate` | `types/settlement.ts:1~18`, `app/settlement/policies/page.tsx:14~39` | `rates[]`(feeType MARGIN/SYSTEM_FEE/TRANSFER_FEE × targetRole × rateBps × vatType), `participants{}`, `options{}` |
| `Assignment` | `types/settlement.ts:20~27`, `app/merchants/[id]/page.tsx:75` | `routingRuleId`·`txType`·`feePolicyId`·`policyName`·`ruleType`·`validFrom` |
| `RateRow`/`CreateForm` | `app/settlement/policies/PolicyFormModal.tsx:13~41` | 요율 세트 전량: rateDisplay(%·원)·vatType(SEPARATE/INCLUDED)·systemFeePayer/transferFeePayer(""=가맹점, UPPER/LOWER)·수취 토글 6종 |
| 기본 요율 템플릿 | `app/settlement/policies/page.tsx:107~125` | GENERAL 9행 / DAOU 5행 (targetRole 조합) |
| targetRole 라벨 | `app/settlement/policies/page.tsx:41~49`, `PolicyFormModal.tsx:43~51`, `app/settlement/overview/page.tsx:171~177` | UPPER=상위파트너, LOWER=하위파트너, SALES=영업조직, UPPER_SALES/LOWER_SALES=상위/하위영업 |
| `policyRate` 필드 | `types/settlement.ts:240`, `hooks/usePurchaseLedger.ts:113` | 선정산 응답 타입에 선언만 있고 화면 표시 소비처는 검색되지 않음 |
| 서비스 함수 | `services/settlementService.ts:9~26` | fetchPolicies/fetchPolicy/createPolicy/updatePolicy/deactivatePolicy |

### 정산상품과 무관한 수수료 축 (혼동 주의)

- 카드사별 수수료: `components/MerchantCardFees.tsx:5, 69` (`fetchCardFees` — merchantService) — 카드사 실수수료율, 정책과 별개.
- 차액 정산(예상↔실제 수수료): `app/merchants/[id]/fee-adjustments/page.tsx:11~26`, `app/settlements/[id]/fee-adjustments/page.tsx` — feePolicy 참조 0건(grep 결과 없음).
- 수수료 면제: `types/settlement.ts:240` 부근 `feeExempt`. 
- 가맹점 레포(`/Users/semi/cursor/payhug-merchant-web`)에는 feePolicy·정산상품·policyName 참조가 0건 — 가맹점 화면은 이번 제거의 직접 영향권 밖.

## ④ 정산상품 제거 시 영향 분류 (조사항목 6)

### (a) 화면만 바꾸면 되는 것 (프론트 단독 작업)

| 항목 | 근거 |
|---|---|
| 사이드바 "정산 상품관리" 메뉴 제거 | `components/AdminLayout.tsx:74~75` (참여자 메뉴엔 원래 없음) |
| `/settlement/policies` 라우트·`PolicyFormModal` 삭제 | `app/settlement/policies/` 디렉토리 전체 |
| 회원 목록에 직속 상위/요율/계약구조 컬럼 표시 | `app/partners/page.tsx:1298~1435` 확장 |
| 등록/수정 모달의 계약 관계 섹션 UI (검색 select·요율 입력·Preview 프레임) | `app/partners/page.tsx:833~1051` 확장 |
| 회원 삭제 다이얼로그 문구의 "정산 상품" 표현 교체 | `app/partners/page.tsx:1214` |

### (b) 백엔드 API 신설·전환이 전제인 것 (서버 확인 필요)

| 항목 | 프론트 근거 | 필요한 서버 몫 |
|---|---|---|
| 관계(Edge) 요율 세트 저장·조회 | `parentUserId`뿐, 요율 자리 없음 (`services/partnerService.ts:17, 33, 44`) | `MemberContractRelation`형 CRUD API 신설 |
| 유형→직속 상위 유형 규칙 | 프론트 필터는 활성+자기제외뿐 (`app/partners/page.tsx:860~866`) | 규칙의 서버 검증 + (선택) `creatable-types`류 규칙 조회 API (`services/partnerService.ts:73~75` 패턴) |
| 전체 체인 조회 (Preview·계약 구조 View) | 체인 조회 API 부재 — 프론트에 재귀 조회 로직 없음 | parent 재귀 조회 API 신설 |
| 가맹점 배정의 대체 (`feePolicyId` → 관계 참조) | POST `/admin/settlement/assignments` body에 `feePolicyId` 필수 (`app/merchants/[id]/page.tsx:276`) | 배정 API의 참조 대상 전환 또는 폐지 — **정산 계산의 rate source 전환과 동시 진행 필수** |
| 정산 실행 활성화 게이트의 대체 기준 | `assignments.length === 0`이면 차단 (`app/merchants/[id]/page.tsx:945~953`) | "적용 계약 체인 존재"로 판정 기준 전환 |
| 시뮬레이션 입력 전환 | `cardPolicyId`/`deliveryPolicyId` (`app/settlement/simulation/page.tsx:142~143`) | simulate API가 관계/가맹점 기준으로 계산하도록 전환 |
| 정산 계산 자체의 rate source | 프론트는 결과만 표시 (`app/settlement/overview/*`) — 계산은 전부 서버 | 서버 확인 필요 (v2 §16: 정산상품이 원장·계산의 정책 소스인지 확인이 최우선) |
| 투자자·페이허그 MARGIN 배분의 행선지 | 상품 rates에 INVESTOR/PAYHUG 행 존재 (`app/settlement/policies/page.tsx:108~109, 120~121`) — 체인 Edge에 자리 없음 | 서버 확인 필요 (P2) |

### (c) 마이그레이션이 필요한 데이터 (프론트에서 보이는 범위)

| 데이터 | 프론트 근거 | 판단 |
|---|---|---|
| 기존 정산상품(participants+rates+options) → 관계 요율 세트 | `types/settlement.ts:9~18` | 상품 1건 = 체인 1개 분량의 요율 묶음. Edge별 분해 이행안은 서버 확인 필요 |
| 기존 가맹점 배정(routing rule: txType별 feePolicyId, validFrom) | `types/settlement.ts:20~27` | 가맹점→담당 체인 매핑으로 전환할 대상. txType 차등을 관계에 어떻게 담을지 미결 |
| 기존 `parentUserId` 값 | `services/partnerService.ts:17` | 관계 테이블 초기 적재의 소스로 사용 가능 (요율은 상품에서 가져와야 함) |
| 과거 정산 이력의 표시 (payout/ledger의 role: UPPER/LOWER/…) | `app/settlement/overview/page.tsx:171~177`, `BatchDetailTab.tsx:534, 778` | 과거 데이터는 상품 기준 role로 남음 — 표시 라벨은 유지 가능하나 신규 데이터의 role 체계는 서버 확인 필요 |

## ⑤ 예외·특이사항 (조사항목 2·7·8·9·10)

### 파트너 상·하위 구분 (조사항목 2)

- 회원 `userType`은 `PARTNER` 단일 값 (`app/partners/page.tsx:32`). 회원 데이터·목록·모달 어디에도 상/하위 속성 없음.
- 상·하위 구분이 존재하는 곳은 두 군데뿐:
  - 정산상품 참여자 슬롯: `upperPartnerId`/`lowerPartnerId` 모두 `userType="PARTNER"` 풀에서 선택 (`app/settlement/policies/PolicyFormModal.tsx:227~240`) — 즉 상품 안에서의 **배치 위치**가 구분의 전부.
  - 계약 서명자 role: `UPPER_PARTNER`/`LOWER_PARTNER`/`PARTNER_LEVEL_0~2` (`app/merchants/[id]/page.tsx:1560~1567`) — 서버가 내려주는 서명 현황 표시용.
- 결론: v2 §3의 "파트너 선택 시 계약 위치(상위/하위) 판별" 자동화 근거는 프론트에 없음 → 등록 시 별도 선택 단계 필요(스펙 m3 (B)안) 또는 서버 판별 로직 확인 필요.

### 추천코드/URL과 체인 (조사항목 7)

- `SignupLinkGenerator`는 활성+코드 보유 회원을 파트너/제휴사/영업으로 나눠 `?partnerCode=&affiliateCode=&salesCode=` URL을 만든다 (`app/partners/page.tsx:696~722`). `parentUserId`는 전혀 참조하지 않음 — **데이터상 체인과 무관**.
- 단, 주석에 "상위 조직 코드로 링크를 만들면 파트너 체인이 상위부터 시작되어 본인이 계약(및 수수료 배분)에서 빠진다"고 명시 (`app/partners/page.tsx:694~695`) — 가입 시 어떤 코드로 들어오느냐가 그 가맹점의 계약 체인 구성에 영향을 준다는 운영 전제. 관계 기반 전환 후 이 연결(코드→체인 시작점)의 규칙화 필요.
- 가맹점 상세의 소개 파트너 지정도 referralCode를 표시용으로만 사용 (`app/merchants/[id]/page.tsx:826~828`), DAOU/제휴 채널 가맹점은 지정 차단 (`815~816`).

### 거래유형(txType) 분기 (조사항목 8)

- 배정: 카드/배달 각각 별도 routing rule로 배정 — `assignTxType` state + 배정 폼 select (`app/merchants/[id]/page.tsx:121, 1734~1737`), 배정 목록 배지 (`1713~1715`).
- 계산 입력: 시뮬레이션이 카드/배달 정책을 따로 받음 (`app/settlement/simulation/page.tsx:77~78, 142~143`).
- 표시: 선정산 현황의 카드/배달 분리 집계 (`types/settlement.ts:187~199` cardSalesAmt/deliverySalesAmt/cardFeeAmt/deliveryFeeAmt), 계산서 발행 구분 (`app/settlement/overview/TaxInvoiceTab.tsx:98, 211`), 원장 그룹 (`BatchDetailTab.tsx:690`).
- 결론: 관계(Edge) 1건 = 요율 세트 1개 모델이면 카드/배달 차등을 담을 수 없음 → Edge에 txType 차원을 추가할지, 가맹점 축에 남길지 결정 필요 (스펙 P3와 동일).

### 예외 관련 기존 로직 (조사항목 9)

| 케이스 | 현재 프론트 상태 | 근거 |
|---|---|---|
| 비활성 상위 | 상위 후보에서 제외됨 (`status === "ACTIVE"` 필터). 가입 링크 생성도 활성만 | `app/partners/page.tsx:860~861, 696` |
| 순환 방지 | 자기 자신 제외뿐 — A→B→A 등 다단계 순환 검증 없음. 서버 차단 여부는 서버 확인 필요 | `app/partners/page.tsx:861` |
| 다중 상위 | 단일 `parentUserId` 필드라 구조상 불가 (UI도 단일 select) | `services/partnerService.ts:17`, `app/partners/page.tsx:996~1008` |
| 상위 변경 | PUT `/admin/partners/{id}`로 즉시 덮어쓰기. 이력·적용일 개념 없음 | `app/partners/page.tsx:1152~1166` |
| 스코프 밖 상위 | 수정 시 기존 상위가 후보 목록에 없으면 "(현재 상위)" 라벨로 강제 추가해 오전송 방지 | `app/partners/page.tsx:867~871` |
| skip-level | 유형 제한 자체가 없으므로 현재는 모든 조합이 허용되는 상태(제한 로직 부재) | `app/partners/page.tsx:860~866` |
| 회원 삭제 제약 | "정산 상품에 배정된 경우 삭제할 수 없습니다" — 서버 제약의 프론트 안내 | `app/partners/page.tsx:1214` |

### 다우(DAOU) 트랙 노출 지점 (조사항목 10)

| 위치 | 근거 | 내용 |
|---|---|---|
| 상품 목록·폼 | `app/settlement/policies/page.tsx:533~539`, `PolicyFormModal.tsx:172~200` | ruleType 일반/다우 배지·토글 (수정 시 변경 불가) |
| 다우 참여자 슬롯 | `PolicyFormModal.tsx:250~264` | 상위영업/하위영업 = SALES+AFFILIATE 풀에서 선택 |
| 다우 요율 템플릿 | `app/settlement/policies/page.tsx:119~125` | MARGIN(투자자·페이허그·상위영업·하위영업)+TRANSFER_FEE — SYSTEM_FEE 행 없음 |
| 납부자 라벨 분기 | `app/settlement/policies/page.tsx:101~104` | 다우면 UPPER/LOWER를 상위영업/하위영업으로 읽음 |
| 가맹점 배정 | `app/merchants/[id]/page.tsx:1716~1718, 1743` | 배정 카드·상품 select에 일반/다우 배지 |
| 시뮬레이션 | `app/settlement/simulation/page.tsx:224, 241, 375` | 정책 옵션·결과에 `[ruleType]` 표기 |
| 정산 현황 role 라벨 | `app/settlement/overview/page.tsx:174` | UPPER_SALES/LOWER_SALES = 상위영업/하위영업 |
| DAOU 채널 가맹점 | `app/merchants/[id]/page.tsx:815~816, 672` | `signupSource === "DAOU"`·`agencyCode`면 소개 파트너 지정 차단, agencyCode 뱃지 |

- 결론: 다우는 회원 체인이 아니라 **상품 ruleType + 가맹점 signupSource/agencyCode 축**으로 돌아간다. 정산상품 제거 시 다우 트랙의 체인 표현(영업↔영업 Edge? 별도 트랙?)이 통째로 미결(P4).

## ⑥ 화면설계 시 '확인 필요' 표기 항목

1. **파트너 상·하위 판별**: 회원 데이터에 구분 없음 — 등록 시 '계약 위치' 선택 단계 신설 여부, 기존 상품 참여자 배치에서 역산 가능한지 (서버 확인 필요, P5).
2. **투자자·페이허그 MARGIN 배분의 자리**: 체인 Edge에 없음 — 별도 전역 설정? 최상위 Edge? (P2, `app/settlement/policies/page.tsx:108~109` 근거).
3. **거래유형(카드/배달)별 요율 차등**: 현행은 txType별 별도 배정 — 관계 모델에서의 표현 방식 (P3, `app/merchants/[id]/page.tsx:1734~1737` 근거).
4. **다우 트랙의 체인 표현**: ruleType 축 소멸 시 상위영업/하위영업 관계·수수료의 행선지 (P4).
5. **정산 계산 rate source 전환·기존 상품 데이터 마이그레이션**: 계산은 전부 서버 — 상품이 원장·계산의 정책 소스인지부터 서버 확인 필요 (P6, v2 §16).
6. **상위파트너(최상위) 등록 시 페이허그와의 계약율 필요 여부**: 현행 상품엔 PAYHUG 요율 행이 있으나 관계 모델에선 최상위가 Edge를 갖지 않음 (스펙 m3 (A)).
7. **관계 변경 이력 정책**: 현행은 덮어쓰기(이력 없음) — 종료 처리+신규 이력 생성(effective_from/to) 채택 여부 (`app/partners/page.tsx:1152~1166` 근거).
8. **순환·skip-level·다중 상위의 서버 검증**: 프론트에 로직 없음 — 서버 차단 규칙 신설 여부.
9. **정산 실행 활성화 게이트의 대체 기준**: 배정 존재 → 계약 체인 존재로 전환 시 판정 주체 (`app/merchants/[id]/page.tsx:945~953`).
10. **추천코드→체인 시작점 규칙**: 가입 링크 코드가 계약 체인 구성에 주는 영향의 명문화 (`app/partners/page.tsx:694~695`).
11. **비활성 상위의 기존 하위 처리**: 현행은 신규 선택 제외만 — 이미 연결된 하위의 관계·정산 지속 여부 (서버 확인 필요).
12. **`policyRate` 응답 필드의 거취**: 선정산 응답 타입에 선언만 있고 표시 소비처 없음 (`types/settlement.ts:240`) — 관계 전환 시 의미 재정의 또는 폐기 (서버 확인 필요).
