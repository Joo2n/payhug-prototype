# 가맹점 웹(merchant-web) 코드 기반 화면 인벤토리

- 대상: `/private/tmp/claude-501/-Users-semi-cursor-payhug/d845932c-7f84-4039-9996-117da0987331/scratchpad/fresh-merchant` (develop HEAD e083af8, 2026-08-08)
- 목적: Figma 화면설계서 가맹점 시트 92장(PH_*/MC_*/ST_*)과의 커버리지 대조용
- 브랜치 상태: feature/uiux_renewal, uiux_renewal2, settlement-preview, contract-renewal, merchant-validation **전부 develop(HEAD)에 머지됨** → 아래 인벤토리가 최신 상태
- 총계: **라우트 32개** (app/**/page.tsx), 화면 내부 단계·오버레이 약 30개, 모달·드롭다운·툴팁 약 30개

---

## 1. 라우트 트리

```
/                                  랜딩 (계약 전 홈)
/login                             사장님 로그인
/signup                            회원가입 (step 1~3 단일 페이지)
/signup/complete                   회원가입 완료
/find-password                     비밀번호 찾기 (step 1~2)
/dashboard                         대시보드 (계약 전/후 분기)
/notifications                     알림 목록 (빈 상태만 구현)
/my-info                           내 정보 관리 허브
/my-info/contract                  계약 정보 조회
/my-info/accounts                  연동 계정 관리
/my-info/inquiries                 1:1 문의
/my-info/change-password           비밀번호 변경
/contract                          계약 준비 체크리스트 허브 (6단계)
/contract/upload-business          [1] 사업자등록증 업로드
/contract/confirm-business         [1] 사업자 정보 확인·등록
/contract/upload-identity          [2] 신분증 업로드
/contract/confirm-identity         [2] 신분증 정보 확인·등록
/contract/apply-pre-payment        [3] 하나은행 계좌 개설 안내 (QR/My브랜치)
/contract/upload-pre-payment       [3] 선정산 전용(락)계좌 통장 업로드
/contract/confirm-pre-payment      [3] 락계좌 확인 + 1원 인증 + 빠른조회
/contract/upload-settlement        [4] 입금 받을 계좌 통장 업로드
/contract/confirm-settlement       [4] 입금 계좌 확인 + 1원 인증
/contract/register-accounts        [5] 플랫폼(카드/배달앱) 계정 등록
/contract/terms                    [6] 비대면 계약 (약관→미리보기→서명→최종확인)
/settlement                        미리 받는 돈 (일자별 정산 상세)
/settlement/card                   카드사별 상세
/settlement/card/transaction       카드 승인 건별 상세
/settlement/delivery               배달 플랫폼별 상세
/settlement/delivery/order         배달 주문 건별 상세
/settlement/adjustments            예상 지급 차액 내역
/settlement/account                계좌 입금 내역
/settlement/account/excluded       선정산 제외액 내역
```

레이아웃 가드: `app/contract/layout.tsx` = AuthGuard + ApprovedContractGuard(승인된 사업자의 계약 재진입 차단, edit/resign/addBusiness 예외). `app/settlement/layout.tsx` = AuthGuard.
전역: `app/error.tsx`(오류가 발생했습니다 + 다시 시도), `app/loading.tsx`(CommonLoading).

---

## 2. 화면별 해부 (단계 / 모달 / 상태 분기)

### 2.1 랜딩 `/` — app/page.tsx
| 요소 | 내용 |
|---|---|
| 섹션 | Hero(어제 매출 오늘 받기) / 프로세스 3단계 / 선정산 신청 CTA / 매출흐름 분석 / 매출 조회(카드·배민·요기요·쿠팡 4계정, 미리 받을 수 있는 금액 합산) / FAQ 9문항 |
| 모달 | ①선정산 서비스(계약 필요→계약하기) ②로그인이 필요해요(로그인하기) ③이미 계약이 완료되었어요(→대시보드) |
| 숨은 분기 | URL 파라미터 partnerCode/investorCode/salesCode/affiliateCode 저장, DAOU(affiliateCode)+bizNbr 시 제휴 자동로그인→/dashboard |
| 시트 매핑 | MC_LANDING, MC_LANDING_FAQ, MC_LANDING_LOGIN(로그인 필요 모달) |

### 2.2 로그인 `/login`
- 입력: 사업자등록번호 또는 휴대전화번호(숫자만) + 비밀번호(정책 검증, 인라인 오류)
- 상태: 서버 인증 실패 인라인 문구 / 세션 만료 시 상단 토스트("세션이 만료되어 다시 로그인해 주세요", `?reason=expired`) / 로그인 중 전체 로딩 오버레이 / ©주식회사 페이허그 펼침(회사 정보 4줄)
- 이미 로그인 상태로 진입 시 /dashboard 리다이렉트
- 시트 매핑: PH_LO, PH_LO_COMPANY, PH_LO_EXPIRED, PH_LO_LOADING

### 2.3 회원가입 `/signup` (진행 인디케이터 점 4개, step 1~3 + 완료)
| 단계 | 내용 | 모달/토스트 |
|---|---|---|
| step1 약관 동의 | 모두 동의 + 개별 약관(서버 `/terms?type=signup` 동적 로드, 필수/선택) | TermsModal(약관 전문, 하단 확인=동의 처리) |
| step2 본인인증 | 휴대전화번호 입력 → KCB 팝업(safe.ok-name.co.kr) | "이미 가입된 번호예요" 모달(→로그인), 인증 완료 토스트, 실패 alert |
| step3 비밀번호 설정 | 새 비밀번호(정책 체크리스트) + 확인(일치 검증) | 서버 오류 토스트 |
| 완료 `/signup/complete` | {이름}님 환영해요 + 매출 조회하기 버튼(→/dashboard), 헤더에 프로필 체크 표시 | — |
- 시트 매핑: PH_JO_TERMS, PH_JO_TERMS_ALL, PH_JO_TERMS_MODAL, PH_JO_AUTH, PH_JO_AUTH_EXIST, PH_JO_PW, PH_JO_PW_CHECK, PH_JO_PW_TIP_CAPS, PH_JO_DONE

### 2.4 비밀번호 찾기 `/find-password` (점 2개, step 1~2)
- step1 본인인증(KCB 팝업) — "가입되지 않은 번호예요" 모달(→회원가입)
- step2 새 비밀번호 설정 — 완료 시 "변경 완료" 모달(→로그인)
- 시트 매핑: PH_PW_FI, PH_PW_FI_NONE, PH_PW_RE, PH_PW_RE_DONE

### 2.5 대시보드 `/dashboard`
| 요소 | 내용 |
|---|---|
| 사업자 선택 | BusinessSelector 드롭다운(상태 배지: 승인완료/심사반려/계약진행) + "사업자 추가"(→upload-business?addBusiness=true) |
| 계약 현황 카드(ProcessStatusCard) 분기 | ①계약서작성→심사중→입금시작 3단계 진행바 ②REJECTED+계약서 미완료="계약이 반려되었어요"+반려사유+다시 계약하기 ③REJECTED+계약서 완료="서비스가 중지되었어요"+중지사유 ④APPROVED="계약이 완료되었어요"(승인 후 1회만 노출, localStorage) |
| APPROVED 메인 | PreSettlementCard: 오늘 날짜 ∙ 미리 받는 돈(이체 전 0원) / 어제 매출액(집계중) / 계좌 입금 내역보기 버튼 |
| 계약 전 메인 | AmountSummaryCard: "미리 받을 수 있는 금액"+예상 배지 = 원장 기준 예상 선정산 지급액(2026-07-31 변경). placeholder 분기: 조회 중.../매출 연동 전/집계중. 연동 문제 계정 N개 경고 문구. + 매출 조회 아코디언(계정 4종, "계약 승인 전에는 매출 정보가 저장되지 않아요" 안내) |
| 모달 4종 | ①선정산 서비스(계약 필요) ②이미 계약 신청이 완료되었어요 ③승인 대기 중이에요(서류 수정하기→edit 모드) ④계약 재서명이 필요해요(resignRequired 강제 모달, 변경 사유 노출→/contract/terms?resign=true) |
- 시트 매핑: MC_DASH, MC_DASH_DONE, MC_DASH_BIZSEL, MC_DASH_PENDING, MC_DASH_UNAPPROVED, MC_DASH_INQUIRY, MC_DASH_APPLIED, MC_DASH_PROGRESS, MC_DASH_REJECT, MC_DASH_RESIGN

### 2.6 공통 헤더 — components/Header.tsx
- 비로그인 랜딩: 녹색 헤더(선정산 신청하기/로그인) / 그 외: 흰 헤더
- 알림 드롭다운(더보기→/notifications, 빈 상태) / 프로필 드롭다운(내 정보·1:1 문의·로그아웃) / 로그아웃 확인 모달 / 모바일 햄버거 드로어(대시보드·알림·내 정보·1:1 문의·로그아웃)
- 시트 매핑: MC_COMMON_NOTI_DD, MC_COMMON_PROFILE, MC_COMMON_LOGOUT, MC_COMMON_MENU

### 2.7 알림 `/notifications`
- "안 읽은 알림 0개" + 모두 읽음 버튼(동작 없음) + "받은 알림이 없습니다" 빈 상태만 구현 (목록 미구현)
- 시트 매핑: MC_NOTI — 시트가 알림 목록을 그렸다면 역방향 갭(코드 미구현)

### 2.8 내 정보 `/my-info` 계열
| 라우트 | 내용 | 시트 |
|---|---|---|
| /my-info | 기본 정보(이름·전화) + 4개 진입 카드(계약 정보/연동 계정/1:1 문의/비밀번호 변경) | MC_MYINFO |
| /my-info/contract | 계약 상태 배지(승인완료/심사반려+반려사유/심사중), 복수 사업자 select, 등록 계좌(선정산 전용/입출금 전용+인증완료), 사업자 정보(법인 필드 포함), 신분증 정보(마스킹), 증빙 서류 목록+보기, 전자 계약서+보기, 약관 동의 내역 | MC_MYINFO_CONTRACT |
| ↳ 파일 미리보기 모달 | PDF iframe / 이미지 뷰어 | MC_MYINFO_CONTRACT_PREVIEW |
| ↳ 약관 전문 모달 | termsTitle+content | MC_MYINFO_CONTRACT_TERMS |
| /my-info/accounts | 안내 배너 + 사업자 select + PlatformAccountsManager(4개 플랫폼 저장→매출조회 검증, idle/saving/verifying/verified/failed) | MC_MYINFO_ACCOUNTS, MC_MYINFO_ACCOUNTS_EDIT |
| /my-info/inquiries | InquiryCard(목록, N건 미답변 배지) + InquiryModal(작성: 카테고리 5종/제목/내용) + InquiryPanel(스레드 드로어+답글) | MC_MYINFO_INQUIRY(+_LIST), MC_MYINFO_INQUIRY_NEW(+_ALT), MC_MYINFO_INQUIRY_DT(+_ALT) |
| /my-info/change-password | 현재/새/확인 3필드 + 정책 체크리스트, 성공 시 토스트 후 강제 재로그인 | MC_MYINFO_PW |

### 2.9 계약 플로우 `/contract/**` (진행바 5~6칸)
| 라우트/상태 | 내용 | 모달·오버레이 | 시트 |
|---|---|---|---|
| /contract 허브 | 6단계 체크리스트(사업자등록증/신분증/락계좌 통장/입금 계좌 통장/플랫폼 계정/비대면 계약), 완료 항목 체크 표시, "준비 완료"→미완료 첫 단계로 라우팅 | 승인 대기 중 모달(서류 수정하기→edit) | MC_CONTRACT, MC_CONTRACT_PENDING |
| ↳ edit 모드(`?edit=true` 또는 PENDING) | "등록된 서류를 수정할 수 있어요", 각 단계 클릭 진입, 대시보드로 이동 버튼 | — | MC_CONTRACT_EDIT |
| upload-business | 사업자 유형 라디오(개인/법인), 사진 최대 3장, OCR 분석 | 분석 중 오버레이 / 오류 모달 / **"사업자 유형 확인" 자동 교정 모달**(번호로 개인↔법인 자동 전환) | MC_CONTRACT_BIZ_UPLOAD(_CORP) |
| confirm-business | OCR 결과 8필드(법인 시 +4: 법인등록번호·본점소재지·대표유형·사업자등록일), 국세청 검증→등록 2단계 버튼 상태 | OCR 힌트 배너(10초) / 등록 완료 모달 / 검증·등록 실패 모달 | MC_CONTRACT_BIZ_INFO(_CORP) |
| upload-identity | 주민등록증/운전면허증 1장, OCR, 주민번호 뒷자리 마스킹(fail-closed) | 분석 중 오버레이 / 오류 모달 | MC_CONTRACT_ID_UPLOAD |
| confirm-identity | 신분증 종류(읽기전용)+성명+주민등록번호+발급일자 | OCR 힌트 / 등록 완료 모달 | MC_CONTRACT_ID_INFO(_DRIVER) |
| apply-pre-payment | 하나은행 My브랜치 QR(PC)/바로가기 버튼(모바일), 두 계좌 개설 안내(펌뱅킹 출금전용+자유입출금), 개설 순서 주의 3줄 | — | MC_CONTRACT_LOCK_APPLY |
| upload-pre-payment | 락계좌 통장 사진, "출금 전용 락계좌" 안내 배너 | 분석 중 / 오류 모달 | MC_CONTRACT_LOCK_UPLOAD |
| confirm-pre-payment (VerifyStep 4단계) | **info**: 계좌주·은행·계좌번호 + 출금 비밀번호 4자리 + FastInquiryGuide 아코디언 → **verify**: 1원 인증번호 3자리 → **fast_inquiry**: 빠른조회 미가입 시 별도 카드(안내 메시지+가입 방법 5단계+비밀번호 재입력+다시 확인) → **done** | 등록 완료 모달 / 오류 모달(하나은행 전용 검증 등) / OCR 힌트 | MC_CONTRACT_LOCK_INFO, LOCK_VERIFY, LOCK_FASTINQ, LOCK_FASTGUIDE |
| upload-settlement | 입금 계좌 통장 사진, "자유 입출금 계좌" 안내 배너, **진입 가드**(락계좌 미등록/빠른조회 미가입 시 차단 모달→apply-pre-payment) | 게이트 모달 / 분석 중 / 오류 모달 | MC_CONTRACT_DEPOSIT_UPLOAD, MC_CONTRACT_DEPOSIT_GATE |
| confirm-settlement (info/verify/done) | 계좌 3필드 → 1원 인증번호 | 등록 완료 모달 / 오류 모달 / OCR 힌트 | MC_CONTRACT_DEPOSIT_INFO, DEPOSIT_VERIFY |
| register-accounts | PlatformAccountsEditor(카드·배민·쿠팡·요기요 저장+검증, 1개 이상 verified 시 다음) | — | MC_CONTRACT_PLATFORM |
| terms (FlowStep 4단계) | **terms**: 계약 약관 개별 동의(`/terms?type=contract`, 모두동의 버튼 없음) → **preview**: 전체화면 계약서 이미지 미리보기(페이지 번호, 확대/축소 토글) → **input**: ContractSignInput(서명 캔버스+다시 그리기+채권매입 수수료율 % 입력) → **confirm**: 최종 계약서(서명·수수료 반영) → 저장 | TermsModal / 계약 동의 완료 모달(→대시보드) / **매출 연동 게이트 모달**("매출 연동을 먼저 완료해주세요"→register-accounts) / 로딩 오버레이 3종(생성·서명 반영·저장) | MC_CONTRACT_SIGN(_ALLAGREE), SIGN_TERMSMODAL, SIGN_PREVIEW(_ZOOM), SIGN_INPUT, SIGN_CONFIRM, SIGN_DONE |
- resign 흐름: /contract/terms?resign=true (대시보드 강제 모달에서 진입, 게이트 미적용)

### 2.10 선정산(정산) `/settlement/**`
| 라우트 | 내용 | 툴팁/모달 | 시트 |
|---|---|---|---|
| /settlement | "미리 받는 돈" 일자 네비(전일/익일 화살표, 내역 반영 시간/전), 어제 매출액(집계중 분기), **카드 섹션: 카드사 9사 고정 행(0원 포함 상시 노출)**, **배달앱 3사 고정 행**, 페이허그 섹션(예상 지급 차액 행 상시 노출·0원 시 disabled/밑줄 제거, 수수료 부가세(VAT), 전산 수수료(면제 분기), 시스템 이용료), **추가 선정산(18:00) 지급분 (+N,NNN원) 파란 병기(AdditionalAmount)** | 예상 지급 차액 ? 툴팁 | ST_MA, ST_MA_TIP_DIFF |
| /settlement/card | 카드사명 헤더, 일자 네비, 어제 매출액/차감액(카드 수수료+페이허그 수수료[면제])/미리 받는 돈, 승인 건 목록+더 불러오기 | — | ST_MA_CARD |
| /settlement/card/transaction | 승인 건 상세: 승인번호·결제수단·어제 매출액·차감액(카드/페이허그 수수료)·미리 받는 돈 | — | ST_MA_CARD_DT |
| /settlement/delivery | 플랫폼명 헤더, 어제 매출액 → **환급액 그룹(+N원, 0원 시 미노출) + {플랫폼} 환급액 하위 행** → 차감액({플랫폼} 차감액 + 광고비(0원 시 미노출) + 페이허그 수수료) → 미리 받는 돈. 주문 목록(만나서 결제 건 = 흐린 음수 표기)+더 불러오기 | 광고비 ? 툴팁(배민/쿠팡이츠/기타 3분기 문구) | ST_MA_DELIV, ST_MA_DELIV_TIP |
| /settlement/delivery/order | 주문 상세: 주문번호·결제수단·어제 매출액(만나서 결제=괄호)·차감액(음수 그대로)·미리 받는 돈 + 하단 고정 안내(만나서 결제 제외 / 배민원 배달팁 제외[BM만]) | — | ST_MA_DELIV_DT |
| /settlement/adjustments | 예상 지급 차액 합산(±부호)+반영일, 안내 배너, 건별 목록(승인/주문번호) | 금액 툴팁: 일반 건=예상/실제 수수료·차액 3줄, **현장결제 지연 회수 건=예정차감일/실제차감일(회수 예정)** | ST_DIFF, ST_DIFF_TIP_NORMAL, ST_DIFF_TIP_MEET_DONE, ST_DIFF_TIP_MEET_PLAN |
| /settlement/account | 하나은행 로고+계좌번호, 입금 내역(날짜 그룹, 배지: 정산 완료류[초록]/선정산 제외[파랑→클릭 시 상세]) | — | ST_AC |
| /settlement/account/excluded | 선정산 제외액 총액+입금일, 안내 배너(11:30 이후 수집분 제외), 건별 목록 | 금액 툴팁(매출액/카드 수수료/선정산 제외액 월 표기 3줄) | ST_AC_EX, ST_AC_EX_TIP |
- 공통 상태: 로딩(CommonLoading) / 파라미터·데이터 없음("정보를 불러올 수 없어요"+메인으로 가기) / 빈 목록("주문 내역이 없어요" 등) / 더 불러오기 페이지네이션

### 2.11 미사용(레거시) 컴포넌트 — 시트 대조 대상 아님
어느 페이지에서도 import되지 않음: `components/ContractDirectSign.tsx`, `ContractSignView.tsx`, `SignatureCreator.tsx`, `SignatureOnPdf.tsx`, `SignaturePad.tsx`, `SalesCalendarCard.tsx`(+`components/sales/LedgerTable.tsx`) — 구 계약/매출 캘린더 플로우 잔재.

---

## 3. 7월 이후 변경 (git log --since=2026-07-01, develop)

| 시기 | 커밋/티켓 | 변경 화면 | 내용 |
|---|---|---|---|
| 8/5~8/8 | PAYHUG-152·158·164 (fe0ac58, 8c63048, c44d574, a0f9d80, cf1e6cc) | /settlement, /settlement/delivery | ①선정산 광고비 부호·툴팁 정리 ②환급액 그룹+{플랫폼} 환급액 행 신설, `+` 접두사, 0원 미노출 ③0원 행 상시 노출 + 0원 시 disabled(밑줄·포커스 제거) ④흡수 항목(만나서결제·광고비)에 환급 가산 추가 |
| 8/4 | 74ad31f | /settlement/delivery | 쿠팡이츠 광고비 툴팁 배민과 동일 구조 통일(실체는 정산차액, CS 참고) |
| 7/31~8/4 | PAYHUG-153 (8553ca6), 9a2fdf9 (feature/settlement-preview) | /dashboard | 계약 전 "미리 받을 수 있는 금액" = 총매출 → 원장 기준 예상 선정산 지급액, 예상 배지·집계중/매출 연동 전 placeholder, 설명 문구 조정 |
| 7/22 | PAYHUG-128 (f66360c) | /settlement | (정산 화면 수수료 관련) |
| 7/13~7/16 | PAYHUG-72·79 (f441ed1, e77afd4, fde1091, 2fd0962) — feature/merchant-validation | /login, /signup, /find-password, /my-info/change-password, /settlement, /settlement/adjustments | 비밀번호 정책 필드(체크리스트·CapsLock 팁), 로그인 식별자 검증, 인라인 오류 |
| 7/10 | PAYHUG-73 (ec1b097) | Header, InquirySection | 헤더·문의 섹션 수정 |
| 7월 초 | 6ca9f34, d4f97e3, bc04fc3, 02a88ee, 613939e — feature/contract-renewal 후속 | /contract/terms, /contract/layout, /login, /dashboard | 계약 프로세스 변경(투자자 없음, 배달/카드 수수료 분리), ApprovedContractGuard 추가, 계약서 원복 |
| 7월 말 | fa66030 | proxy.ts | 담당자 배정 우선순위(화면 아님) |

---

## 4. 커버리지 대조 — gap 후보

### 4.1 코드에는 있으나 대응 시트가 없어 보이는 것 (정방향 gap)
| # | 코드 요소 | 파일 | 판정 |
|---|---|---|---|
| G1 | 계약서 단계 진입 시 **매출 연동 게이트 모달** "매출 연동을 먼저 완료해주세요" | app/contract/terms/page.tsx | gap 후보 — DEPOSIT_GATE(입금계좌 게이트)와 별개 모달, 대응 시트 없음 |
| G2 | 사업자등록증 업로드의 **"사업자 유형 확인" 자동 교정 모달** (개인↔법인 자동 전환 안내) | app/contract/upload-business/page.tsx | gap 후보 — BIZ_UPLOAD_CORP는 라디오 선택 상태만 커버 추정 |
| G3 | **환급액 그룹 행**(+N원, {플랫폼} 환급액 하위 행) — 2026-08-05 신설 | app/settlement/delivery/page.tsx | gap 후보 — ST_MA_DELIV 시트가 8/5 이전 제작이면 미반영. 확인 필요 |
| G4 | 정산 메인 **0원 행 상시 노출 + 0원 disabled**(카드 9사·배달 3사 고정 목록) — PAYHUG-164, 8월 | app/settlement/page.tsx | 확인 필요 — ST_MA 시트의 행 구성·0원 처리와 대조 |
| G5 | **추가 선정산(18:00) 지급분 (+N,NNN원) 파란 병기**(AdditionalAmount, 하루 2회 지급) | app/settlement/page.tsx | 확인 필요 — 정책서엔 하루 2회 반영됐으나 ST_MA 시트 표기 여부 미확인 |
| G6 | 계약 전 대시보드 카드: **예상 배지 + placeholder 3분기(조회 중/매출 연동 전/집계중) + 연동 문제 계정 N개 경고** — 7/31 변경 | app/dashboard/page.tsx | gap 후보 — MC_DASH 시트가 총매출 기준 구버전이면 미반영 (VOC C4 직결) |
| G7 | 대시보드 **"서비스가 중지되었어요"** 상태(REJECTED+계약서 완료, 중지 사유 박스) | app/dashboard/page.tsx | 확인 필요 — MC_DASH_REJECT가 반려만 그렸는지 중지까지 그렸는지 |
| G8 | 랜딩의 **"이미 계약이 완료되었어요" 모달** | app/page.tsx | 확인 필요 — MC_DASH_APPLIED(대시보드 변형)와 문구 다름 |
| G9 | confirm 4개 화면 공통 **OCR 자동 입력 힌트 배너**(10초 자동 소멸) | confirm-business/identity/pre-payment/settlement | 확인 필요 — 시트에 포함됐을 수도 있음 |
| G10 | contract/terms **로딩 오버레이 3종**(계약서 생성/서명 반영/저장 중) + login/upload 계열 분석 중 오버레이 | app/contract/terms 외 | 확인 필요 — 로딩 상태는 통상 시트 생략, 화면설계 의미는 낮음 |
| G11 | settlement 계열 공통 **오류 상태**("정보를 불러올 수 없어요"+메인으로 가기) / **빈 목록 상태** / **더 불러오기 버튼** | app/settlement/** | 확인 필요 |
| G12 | delivery/order 하단 고정 안내(만나서 결제 제외 / 배민원 배달팁 제외) | app/settlement/delivery/order/page.tsx | 확인 필요 — ST_MA_DELIV_DT 포함 여부 |
| G13 | 전역 **error.tsx**(오류가 발생했습니다) | app/error.tsx | gap 후보 — 대응 시트 없음 (우선순위 낮음) |
| G14 | confirm-pre-payment의 **락계좌 출금 비밀번호 4자리 입력 필드**(빠른조회용) | app/contract/confirm-pre-payment/page.tsx | 확인 필요 — LOCK_INFO 시트에 필드 포함 여부 |
| G15 | 비밀번호 정책 **체크리스트 UI**(PAYHUG-72/79, 7월) — signup/find-password/change-password 공통 | components/PasswordInput.tsx | 확인 필요 — PH_JO_PW_CHECK/PW_TIP_CAPS가 7월 변경분 기준인지 |

### 4.2 시트에는 있으나 코드와 안 맞는 것 (역방향, 참고)
| # | 시트 | 내용 |
|---|---|---|
| R1 | MC_CONTRACT_TERMS_AGREE (1836:2, 이미지 없음) | MC_CONTRACT_SIGN과 중복되는 구버전 시트로 추정. 정리 대상 확인 필요 |
| R2 | MC_MYINFO_INQUIRY_LIST / _NEW_ALT / _DT_ALT | 동일 코드 화면의 대안(ALT) 변형 — 코드 1:다 매핑 |
| R3 | MC_NOTI | 코드는 빈 상태만 구현(목록·모두 읽음 미구현). 시트가 목록을 그렸다면 코드 측 미구현 |
| R4 | MC_CONTRACT_SIGN_ALLAGREE | 계약 약관 단계에 "모두 동의" 버튼 없음(개별 체크만, signup과 다름). 시트가 모두동의 UI를 그렸다면 코드와 불일치 |

### 4.3 시트 ↔ 코드 매핑 총괄
- 92장 중 코드 대응 확인: 88장 (MC_CONTRACT_TERMS_AGREE 중복 1, ALT 변형 3 포함 시 92장 전부 코드 화면에 귀속 가능)
- 코드 화면·상태 중 시트 미확인: 위 G1~G15 (gap 확정 4~5건, 나머지 '확인 필요')
