# 매출 조회 시트 디스크립션 사실 대조 (AD_SALES 계열 13시트)

- 기준: 시트 작성 2026-07-21(구 코드 3fbc230) vs develop HEAD 9e2741b
- 코드: `/private/tmp/claude-501/-Users-semi-cursor-payhug/d845932c-7f84-4039-9996-117da0987331/scratchpad/fresh-admin`
- Figma: `Tcf69tIciGxmlqCIuRb0iI` 페이지 303:173 — **읽기만 수행, 수정 없음**
- 관련 diff 요지 (매출 조회 범위):
  1. `app/sales/page.tsx` — 사업자번호(businessNumber) 미등록 유저를 목록 수신 시점에 제외 + 검색 3필드 null 가드 (라인 +2 밀림)
  2. `app/sales/[bizNo]/page.tsx` — 라벨 2건 교체(줄수 변화 없음): `차액수수료`→`차액 대상 수수료`(678), `광고비 차감 (배민 우리가게클릭)`→`플랫폼 차감 (광고비·부분환불·정산차액)`(778)
  3. `components/sales/ManualSalesModal.tsx` — form/result 2단계화(등록 완료 요약), 배달 탭 음수 금액=매입취소+환수(CANCEL_CLAWBACK) 확인 단계 신설, 매입 수수료 필수 검증을 handleSubmit 앞단으로 이동
  4. `components/sales/ExcelUploadModal.tsx` — 미리보기에 '구분' 열 추가(매입 타입 제외), 결과 단계를 ManualSalesResultSummary 공용 요약으로 교체, X·배경 닫기 시에도 목록 재조회
  5. 신규: `components/sales/ManualSalesResultSummary.tsx`, `lib/manualSalesResult.ts` (기타 건수·경고·스킵 사유 요약). `services/` 는 변경 없음.
- 공통 SCREEN_STALE: 상세화면을 임베드한 12개 시트(1584 제외 전부) 모두, 임베드 화면 '실제 이체액 구성' 블록에 구 라벨 **"광고비 차감 (배민 우리가게클릭)"** 이 남아 있음 (Noto Sans KR 노드, 시트별 노드ID는 아래 표기). `차액수수료` 라벨은 목업 데이터에서 해당 줄이 미렌더라 임베드 화면에는 없음.

---

## 1584:2 AD_SALES (목록) — 판정: 부분 수정

| 텍스트 노드ID | 현재 문구(요약) | 무엇이 틀렸나 | 제안 문구(전체) | 심각도 | 코드 근거 |
|---|---|---|---|---|---|
| 1584:139 | 오른쪽에 총 N개 가맹점 표시 (캡처 기준 총 14개) | 총 개수의 모집이 바뀜 — 사업자번호 미등록 유저는 수신 시점에 제외되어 집계에 안 들어감 | 오른쪽에 총 N개 가맹점 표시 (사업자번호 등록 가맹점만 집계 · 캡처 기준 총 14개) | M | app/sales/page.tsx:50-53,87 |
| 1584:145 | 검색과 상관없이 전체 가맹점 수 — 검색어를 넣어도 이 숫자는 줄지 않음 (표는 걸러진 목록, 카운트는 전체 목록으로 서로 다름) | '전체 가맹점 수'가 더 이상 전체가 아님 — 미등록 유저 선제외 후의 수 | 검색과 상관없이 목록 전체 수 — 단, 사업자번호 미등록 유저는 조회할 매출이 없어 목록 수신 시점에 이미 빠져 이 숫자에도 안 들어감 · 검색어를 넣어도 이 숫자는 줄지 않음 (표는 걸러진 목록, 카운트는 걸러지기 전 목록) | M | app/sales/page.tsx:50-53,87 |
| 1584:381 | 화면 목록은 가맹점 등록 정보 하나에서만 온다 (매출 데이터가 아님). | 신규 제외 규칙 누락 | 화면 목록은 가맹점 등록 정보 하나에서만 온다 (매출 데이터가 아님). 단 사업자번호 없는 유저는 조회할 매출이 없어 목록에서 제외하고 받는다. [확정] | M | app/sales/page.tsx:50-53 |
| 1584:604 | 주의: 상단의 '총 N개 가맹점'은 검색과 무관하게 전체 수를 그대로 보여준다. … | 위와 동일 — '전체 수' 서술 보정 필요 | 주의: 상단의 '총 N개 가맹점'은 검색과 무관하게 (사업자번호 미등록 제외 후의) 목록 전체 수를 그대로 보여준다. 검색으로 목록이 줄어도 이 숫자는 안 줄어든다. 표 왼쪽 '번호'도 가맹점 고유번호가 아니라 그 순간 화면의 줄 순서일 뿐. | M | app/sales/page.tsx:50-53,87,149 |
| 1584:162 | 가맹점명 · 사업자번호 · 대표자명으로 검색 | 사실은 유지되나 신규 가드 미반영 — 대표자명 등 null 필드 가맹점도 오류 없이 검색됨 | 가맹점명 · 사업자번호 · 대표자명으로 검색 (값이 비어 있는 필드는 빈 문자열로 처리해 오류 없이 동작) | L | app/sales/page.tsx:69-75 |
| 1584:677 | 목록은 가맹점 등록 정보만 불러오고 진입/포커스 복귀 시 재로드 · app/sales/page.tsx:47-66 | 내용에 제외 필터 누락 + 줄번호 밀림 | 목록은 가맹점 등록 정보만 불러오되 사업자번호 미등록 유저는 제외, 진입/포커스 복귀 시 재로드 · app/sales/page.tsx:47-67 (제외 필터 50-53) | M | app/sales/page.tsx:47-67 |
| 1584:695 | 정렬 우선순위… · app/sales/page.tsx:31-38,68-73 | 뒷범위 줄번호 +2 밀림 | 정렬 우선순위: 승인+활성/승인+비활성/미승인, 검색 후 정렬 · app/sales/page.tsx:31-38,70-75 | L | app/sales/page.tsx:70-75 |
| 1584:698 | '승인'과 '활성' … · app/sales/page.tsx:24-33,157-162 | 뒷범위 +2 | '승인'과 '활성' 두 상태를 모두 초록 '승인'으로 라벨·정렬 취급 · app/sales/page.tsx:24-33,159-164 | L | app/sales/page.tsx:159-164 |
| 1584:701 | 미정의 상태는 '대기' 라벨… · app/sales/page.tsx:37,130,166 | 뒤 2개 +2 | 미정의 상태는 '대기' 라벨로 표시되나 정렬은 미승인·승인 버튼 없음 · app/sales/page.tsx:37,132,168 | L | app/sales/page.tsx:132,168 |
| 1584:707 | 행 클릭 사업자번호… · app/sales/page.tsx:135-145,166-179 | +2 | 행 클릭은 사업자번호로 매출상세, 승인 버튼은 내부 번호로 승인화면 · app/sales/page.tsx:137-147,168-181 | L | app/sales/page.tsx:137-147,168-181 |
| 1584:710 | 승인 버튼 '대기'만 노출 · app/sales/page.tsx:166-184 | +2 | 승인 버튼은 '대기'에만 노출, 거절·미정의 상태엔 없음 · app/sales/page.tsx:168-186 | L | app/sales/page.tsx:168-186 |
| 1584:713 | 검색은 가맹점명·사업자번호·대표자명 대상 · app/sales/page.tsx:68-73 | +2, null 가드 추가됨 | 검색은 가맹점명·사업자번호·대표자명 대상 (null 필드 가드 포함) · app/sales/page.tsx:69-75 | L | app/sales/page.tsx:69-75 |
| 1584:716 | 상단 '총 개수'는 검색과 무관한 전체 수… · app/sales/page.tsx:84-86,147 | 내용 보정(위와 동일) + 줄번호 +2 | 상단 '총 개수'는 검색과 무관 — 단 사업자 미등록 제외 후의 목록 수 · '번호'는 화면 줄 순서 · app/sales/page.tsx:86-88,149 | M | app/sales/page.tsx:86-88,149 |

- 임베드 화면: 목록 화면엔 변경 요소 없음 → SCREEN_STALE 아님.

---

## 1598:2 AD_SALES_DT (상세 기본) — 판정: 부분 수정 + SCREEN_STALE

| 텍스트 노드ID | 현재 문구(요약) | 무엇이 틀렸나 | 제안 문구(전체) | 심각도 | 코드 근거 |
|---|---|---|---|---|---|
| 1598:360 | 선정산 순지급액 − 당일 카드수수료 차액 − 선정산수수료 ± 차액정산 − 광고비 차감(배민 우리가게클릭) − 현장결제 회수 = 실제 이체액 | 산식 항목 라벨이 바뀌고 범위가 넓어짐 — 광고비 단일이 아니라 플랫폼 차감 계열 | 선정산 순지급액 − 당일 카드수수료 차액 − 선정산수수료 ± 차액정산 − 플랫폼 차감(광고비·부분환불·정산차액) − 현장결제 회수 = 실제 이체액 | H | app/sales/[bizNo]/page.tsx:776-781 |
| 1598:670 | − 광고비 차감(배민 우리가게클릭) − 현장결제 회수 = 실제 이체액 | 동일 라벨 교체 | − 플랫폼 차감(광고비·부분환불·정산차액) − 현장결제 회수 = 실제 이체액 | H | app/sales/[bizNo]/page.tsx:776-781 |
| 1598:318 | 선정산 수수료 : 채권매입+시스템+이체(+차액수수료)로 분해 · 면제면 "면제" 뱃지·취소선 | 4번째 분해 항목 라벨 개칭 | 선정산 수수료 : 채권매입+시스템+이체(+차액 대상 수수료)로 분해 · 면제면 "면제" 뱃지·취소선 | M | app/sales/[bizNo]/page.tsx:673-679 |
| 1598:590 | 업로드 → 미리보기 → 결과 3단계, 미리보기에서 신규/중복/에러 건수 집계 | 3단계는 유지되나 미리보기 '구분' 열·결과 요약 확장이 누락 | 업로드 → 미리보기 → 결과 3단계 · 미리보기에서 신규/중복/에러 건수 집계 + 매입 타입이 아니면(카드 승인·배달) 행별 '구분' 열 노출 · 결과 단계는 전체/성공/중복/실패에 기타(보호·스킵·환수 실패)·경고까지 요약 | M | components/sales/ExcelUploadModal.tsx:204-220,240-249 |
| 1598:554 | 스크래핑에 안 잡힌 매출을 운영자가 직접 넣는 창으로 … 3탭이며 탭마다 입력칸이 다르다. | 등록 후 결과 요약 단계 신설 누락 | 스크래핑에 안 잡힌 매출을 운영자가 직접 넣는 창으로 카드 승인 / 카드 매입 / 배달 플랫폼 3탭이며 탭마다 입력칸이 다르다. 등록 성공 시 바로 닫히지 않고 '등록 완료' 요약(성공/중복/기타·경고)을 거쳐 [확인] 시 목록을 재조회한다. | M | components/sales/ManualSalesModal.tsx:111-138,186-188 |
| 1598:572 | 배달: 플랫폼·수수료·매장명·현장결제 여부 | 배달 탭 음수=취소 확인 단계 신설 누락 | 배달: 플랫폼·수수료·매장명·현장결제 여부 · 음수 금액 입력 시 매입취소+환수(CANCEL_CLAWBACK) 경고 후 [취소로 등록] 확인 단계를 거침 | M | components/sales/ManualSalesModal.tsx:68-85,179-184 |
| 1598:1004 | 단건 등록 3탭과 탭별 입력 필드… · components/sales/ManualSalesModal.tsx:99-103, 137-224 | 줄번호 대폭 밀림 | 단건 등록 3탭과 탭별 입력 필드(카드매입 수수료합계 필수, 배달 현장결제 체크) · components/sales/ManualSalesModal.tsx:140-145, 190-278 (수수료 필수 검증 78-81) | L | components/sales/ManualSalesModal.tsx:78-81,140-145 |
| 1598:1007 | 엑셀 자동 인식·3단계·중복 갱신 · components/sales/ExcelUploadModal.tsx:35, 139-142, 152-208 | 줄번호 밀림 | 엑셀 자동 인식·3단계·중복 갱신 · components/sales/ExcelUploadModal.tsx:43, 61-64, 82-99, 171-238 | L | components/sales/ExcelUploadModal.tsx:43,61-64,82-99 |

- SCREEN_STALE: 임베드 화면 노드 2661:3724 "광고비 차감 (배민 우리가게클릭)" — 구 라벨.
- 유지 확인: 1598:596(중복=기존 갱신), 1598:566(매입 수수료 필수 — 검증 위치만 이동, 규칙 동일), page.tsx 줄 참조들(라벨 교체는 in-place라 줄수 불변).

---

## 1600:2 AD_SALES_DT_PAYOUT — 판정: 현행 OK + SCREEN_STALE
- 디스크립션·코드 근거(page.tsx / usePurchaseLedger.ts) 전부 develop과 일치. 수정 없음.
- SCREEN_STALE: 임베드 화면 노드 2661:4669 구 라벨 "광고비 차감 (배민 우리가게클릭)".

## 1601:2 AD_SALES_DT_CANCEL — 판정: 현행 OK + SCREEN_STALE
- 취소 판정·마스킹·엑셀 처리 서술 및 줄 참조 모두 유효. 수정 없음.
- SCREEN_STALE: 2661:5614 구 라벨.

## 1602:2 AD_SALES_DT_NORMAL — 판정: 현행 OK + SCREEN_STALE
- 서버 재조회·판정 이원화·잔상 서술 및 줄 참조 모두 유효. 수정 없음.
- SCREEN_STALE: 2661:6559 구 라벨.

---

## 1603:2 AD_SALES_DT_BM — 판정: 부분 수정 + SCREEN_STALE

| 텍스트 노드ID | 현재 문구(요약) | 무엇이 틀렸나 | 제안 문구(전체) | 심각도 | 코드 근거 |
|---|---|---|---|---|---|
| 1603:333 | 실제 이체액 구성에 배민 우리가게클릭 광고비 차감 항목이 별도로 붙어 이체액에서 빠진다. | 라벨·범위 변경 — 배민 광고비 단일 항목이 아니라 플랫폼 차감(광고비·부분환불·정산차액)으로 확장 | 실제 이체액 구성에 플랫폼 차감(광고비·부분환불·정산차액) 항목이 별도로 붙어 이체액에서 빠진다. 배민 우리가게클릭 광고비를 포함하되, 화면 라벨 기준으로 부분환불·정산차액까지 아우르는 계열 항목이다 (서버가 각 성분을 어떻게 산입하는지는 확인 필요). | H | app/sales/[bizNo]/page.tsx:776-781 |
| 1603:329 | 광고비 차감 (소제목) | 소제목도 구 라벨 | 플랫폼 차감 (광고비 등) | M | app/sales/[bizNo]/page.tsx:778 |
| 1603:339 | 카드에는 없는 배달(배민) 전용 차감 라인 | '배민 전용' 한정이 라벨에서 사라짐 | 카드에는 없는 배달 플랫폼 전용 차감 라인 (배민 한정 표기는 제거됨) | M | app/sales/[bizNo]/page.tsx:776-781 |
| 1603:393 | 선정산 순지급액 → (당일 카드차액, 익일배치) → 선정산수수료 → 차액정산 → 광고비 차감 → 현장결제 회수 → 실제 이체액. | 순서 항목명 구 라벨 | 선정산 순지급액 → (당일 카드차액, 익일배치) → 선정산수수료 → 차액정산 → 플랫폼 차감 → 현장결제 회수 → 실제 이체액. | M | app/sales/[bizNo]/page.tsx:755-796 |
| 1603:399 | 광고비·현장결제 두 줄이 배달에서 새로 등장 | 항목명 구 라벨 | 플랫폼 차감·현장결제 두 줄이 배달에서 새로 등장 | M | app/sales/[bizNo]/page.tsx:776-796 |
| 1603:493 | 광고비 차감(배민 우리가게클릭) 이체액 구성 라인 · app/sales/[bizNo]/page.tsx:776-781 | 인용 문구가 구 라벨 (줄 참조는 유효) | 플랫폼 차감(광고비·부분환불·정산차액) 이체액 구성 라인 · app/sales/[bizNo]/page.tsx:776-781 | M | app/sales/[bizNo]/page.tsx:778 |
| 1603:502 | 실제 이체액 구성 순서 및 현장결제/광고비 라인 · app/sales/[bizNo]/page.tsx:755-796 | 인용 문구 구 라벨 | 실제 이체액 구성 순서 및 현장결제/플랫폼 차감 라인 · app/sales/[bizNo]/page.tsx:755-796 | L | app/sales/[bizNo]/page.tsx:755-796 |

- SCREEN_STALE: 2661:7504 구 라벨.
- keynote 1603:132("배민 특유의 광고비(우리가게클릭) 차감…" 서술 포함)도 위 1603:333 교정과 같은 취지로 문구 보정 필요 (심각도 M, 동일 근거).

## 1604:2 AD_SALES_DT_ADJUST — 판정: 현행 OK + SCREEN_STALE
- 유형 8종·합계 규칙·펼침 조건·줄 참조 모두 develop과 일치. 수정 없음.
- SCREEN_STALE: 2661:8449 구 라벨.

---

## 1605:2 AD_SALES_DT_ADD_CARD — 판정: 부분 수정 + SCREEN_STALE

| 텍스트 노드ID | 현재 문구(요약) | 무엇이 틀렸나 | 제안 문구(전체) | 심각도 | 코드 근거 |
|---|---|---|---|---|---|
| 1605:172 | 등록 성공 시 모달 닫고 목록 자동 재조회 · 실패 시 서버 메시지 노출 | 성공 동작 변경 — 즉시 닫지 않고 결과 요약 단계를 거침, 닫기 경로 어디로든 재조회 | 등록 성공 시 모달이 바로 닫히지 않고 '등록 완료' 결과 요약(성공/중복/기타·경고)으로 전환 · [확인]은 물론 X·배경 클릭으로 닫아도 목록 자동 재조회 · 실패 시 서버 메시지 노출(폼 유지) | H | components/sales/ManualSalesModal.tsx:111-138,283-290 |
| 1605:443 (+449) | 등록 성공 시 모달 닫고 상세 목록을 첫 페이지부터 다시 조회 | 동일 — 결과 요약 경유로 변경 | 등록 성공 시 '등록 완료' 결과 요약을 먼저 표시하고, [확인]/닫기 시 상세 목록을 첫 페이지부터 다시 조회 (방금 넣은 승인 건이 목록·요약에 반영) [확정] | H | components/sales/ManualSalesModal.tsx:111-138; app/sales/[bizNo]/page.tsx:1270-1271 |
| 1605:387 | 승인취소(음수) 건을 이 창으로 넣을 때의 처리 규칙은 이 화면에 명시 없음 [확인필요] | 부분 해소 — 배달 탭엔 음수=취소 확인 단계가 생겼고, 카드 승인 탭은 여전히 확인 단계 없음(코드 주석상 별도 PR 예정), 서버는 이미 취소 건이면 스킵 응답 | 배달 탭은 음수 금액=매입취소+환수(CANCEL_CLAWBACK) 확인 단계가 신설됐으나, 카드 승인 탭은 여전히 확인 없이 그대로 전송(코드 주석: 같은 패턴이나 별도 PR 영역) · 서버가 이미 승인취소된 건이면 '되돌림 방지'로 원장 미반영(applied=false·skipReason=ALREADY_CANCELLED) 응답 — 카드 음수 입력의 최종 정책은 여전히 확인필요 | M | components/sales/ManualSalesModal.tsx:68-70; lib/manualSalesResult.ts:120-137 |
| 1605:166 | [취소] 닫기 · [등록] 저장(진행 중 "등록 중...") | 결과 단계 버튼 누락 | [취소] 닫기 · [등록] 저장(진행 중 "등록 중...") · 결과 단계에선 [확인]만 노출 | M | components/sales/ManualSalesModal.tsx:283-311 |
| 1605:120 | 현재 카드 승인 탭 활성 · 탭 전환 시 폼 리셋 | 결과 단계 탭 숨김 누락 | 현재 카드 승인 탭 활성 · 탭 전환 시 폼 리셋 · 결과 단계에선 탭 줄 숨김 | L | components/sales/ManualSalesModal.tsx:162-170 |
| 1605:87 | 공통 3개 탭 … 배경 클릭 또는 X로 닫힘 | 결과 단계에서의 닫기 부수효과 누락 | 공통 3개 탭(카드 승인 / 카드 매입 / 배달 플랫폼) · 탭 바꾸면 입력값 초기화 · 배경 클릭 또는 X로 닫힘(결과 단계에선 닫아도 목록 재조회) | L | components/sales/ManualSalesModal.tsx:132-138 |
| 1605:511 | 성공 시 목록 첫 페이지 재조회, 실패 시 메시지 표시 · components/sales/ManualSalesModal.tsx:83-96 | 내용·줄번호 모두 구버전 | 성공 시 결과 요약 단계로 전환, 결과 닫힘 시 onSuccess로 목록 재조회, 실패 시 메시지 표시 · components/sales/ManualSalesModal.tsx:111-138 | M | components/sales/ManualSalesModal.tsx:111-138 |
| 1605:484 | 탭 정의와 기본 CARD_APPROVAL… · ManualSalesModal.tsx:17,26,99-103 | 줄번호 밀림 | 탭 정의와 기본 CARD_APPROVAL, 3개 탭 라벨 · components/sales/ManualSalesModal.tsx:22,32,140-145 | L | components/sales/ManualSalesModal.tsx:22,32,140-145 |
| 1605:487 | 탭 변경 시 폼 초기화 · 47-55 | 줄번호 | 탭 변경 시 폼 초기화 · components/sales/ManualSalesModal.tsx:55-66 | L | components/sales/ManualSalesModal.tsx:55-66 |
| 1605:490 | 카드사 고정 10개·기본 신한 · 6-9,33,159-161 | 줄번호 | 카드사 고정 10개 목록·기본값 신한 · components/sales/ManualSalesModal.tsx:11-14,41,211-217 | L | components/sales/ManualSalesModal.tsx:11-14,41,211-217 |
| 1605:493 | 결제수단 신용/체크 · 34,164-169 | 줄번호 | 결제수단 신용/체크, 기본 신용 · components/sales/ManualSalesModal.tsx:42,219-226 | L | components/sales/ManualSalesModal.tsx:42,219-226 |
| 1605:496 | salesSource=CARD dataType=APPROVAL… · 66-67 | 줄번호 (payload 조립이 doRegister로 이동) | 카드 승인 탭 전송값 salesSource=CARD dataType=APPROVAL, merNo 빈값 제외 · components/sales/ManualSalesModal.tsx:94-95 | L | components/sales/ManualSalesModal.tsx:94-95 |
| 1605:499 | 필수 3개 검증 문구 · 59-62 | 줄번호 | 필수 3개 검증 문구 · components/sales/ManualSalesModal.tsx:73-77 | L | components/sales/ManualSalesModal.tsx:73-77 |
| 1605:502 | 카드 매입 탭만 수수료 필수… · 68-73,173-192 | 줄번호 (검증이 handleSubmit 앞단으로 이동, 규칙은 동일) | 카드 매입 탭만 수수료 필수(공통 필수 통과 후 검사), 승인 탭엔 수수료칸 없음 · components/sales/ManualSalesModal.tsx:78-81,228-248 | L | components/sales/ManualSalesModal.tsx:78-81,228-248 |
| 1605:505 | 매출금액 숫자 입력칸 · 149-152 | 줄번호 | 매출금액 숫자 입력칸(수정 시 취소 확인 상태 자동 해제) · components/sales/ManualSalesModal.tsx:204-208 | L | components/sales/ManualSalesModal.tsx:204-208 |

- SCREEN_STALE: 2661:9456 (모달 뒤 상세화면의 구 라벨).
- 유지 확인: 필수 3개·카드사 10종·결제수단·merNo 빈값 제외·keynote '수수료를 안 받는다' — 모두 유효.

---

## 1673:2 AD_SALES_DT_ADD_PURCHASE — 판정: 부분 수정 + SCREEN_STALE

| 텍스트 노드ID | 현재 문구(요약) | 무엇이 틀렸나 | 제안 문구(전체) | 심각도 | 코드 근거 |
|---|---|---|---|---|---|
| 1673:154 | [취소] · [등록] (진행 중 "등록 중...") → 성공 시 목록 재조회 | 성공 동작 변경 — 결과 요약 경유 | [취소] · [등록](진행 중 "등록 중...") → 성공 시 '등록 완료' 결과 요약으로 전환 · [확인]/X/배경 닫기 시 목록 재조회 | H | components/sales/ManualSalesModal.tsx:111-138,283-290 |
| 1673:324 | 단건 등록 전용 저장 경로로 1건 전송. 성공 응답이면 모달 닫고 목록 새로고침, 실패면 서버 메시지 그대로 노출. | 동일 — 결과 요약 경유 누락 | 단건 등록 전용 저장 경로로 1건 전송. 성공 응답이면 '등록 완료' 결과 요약(성공/중복/기타·경고)을 먼저 보여주고, 닫을 때 목록을 새로고침. 실패면 서버 메시지를 그대로 노출(폼 유지). [확정] | M | components/sales/ManualSalesModal.tsx:111-138; services/manualSalesService.ts:4-13 |
| 1673:415 | 실제 수수료 미입력 시 저장 차단 · …ManualSalesModal.tsx:69 | 줄번호 (검증 위치 이동) | 카드 매입 탭에서 실제 수수료 미입력 시 저장 차단 · 01_payhug-admin-web-main/components/sales/ManualSalesModal.tsx:78-80 | L | components/sales/ManualSalesModal.tsx:78-80 |
| 1673:418 | 매입일자·지급예정일 선택 입력… · …:174-192 | 줄번호 | 매입일자·지급예정일은 선택 입력, 실제 수수료는 필수 payload · 01_payhug-admin-web-main/components/sales/ManualSalesModal.tsx:96-100,228-248 | L | components/sales/ManualSalesModal.tsx:96-100,228-248 |
| 1673:421 | 금액 라벨이 매입 탭에서 '매입금액' · …:149 | 줄번호 | 금액 라벨이 매입 탭에서 '매입금액'으로 바뀜 · 01_payhug-admin-web-main/components/sales/ManualSalesModal.tsx:205 | L | components/sales/ManualSalesModal.tsx:205 |
| 1673:424 | 카드사 10종·결제수단 · …:6-9,155-171 | 줄번호 | 카드사 10종·결제수단 신용/체크 공통 노출 · 01_payhug-admin-web-main/components/sales/ManualSalesModal.tsx:11-14,211-226 | L | components/sales/ManualSalesModal.tsx:11-14,211-226 |
| 1673:427 | 저장 유형 매입(PURCHASE)·merNo 선택 전송 · …:68-73 | 줄번호 | 저장 유형 매입(PURCHASE)·merNo 선택 전송 · 01_payhug-admin-web-main/components/sales/ManualSalesModal.tsx:96-100 | L | components/sales/ManualSalesModal.tsx:96-100 |
| 1673:430 | 공통 필수 검증 후 성공 시 닫고 새로고침 · …:57-97 | 내용 일부(닫고 새로고침)·줄번호 | 공통 필수→수수료 검증 후 성공 시 결과 요약 단계, 결과 닫힘 시 새로고침 · 01_payhug-admin-web-main/components/sales/ManualSalesModal.tsx:72-138 | M | components/sales/ManualSalesModal.tsx:72-138 |

- SCREEN_STALE: 2661:63820 구 라벨.
- 유지 확인: 검증 순서(① 공통 필수 → ② 수수료)는 이동 후에도 동일 — 1673:299~315 수정 불요. 차액 연결·6대 개념 경계 서술 유효.

---

## 1675:2 AD_SALES_DT_ADD_DELIVERY — 판정: 부분 수정 + SCREEN_STALE

| 텍스트 노드ID | 현재 문구(요약) | 무엇이 틀렸나 | 제안 문구(전체) | 심각도 | 코드 근거 |
|---|---|---|---|---|---|
| 1675:146 | 필수 3개(주문번호·거래일자·매출금액) 미입력 시 "필수 항목을 모두 입력해주세요." | 신규 핵심 기능 누락 — 배달 탭 음수 금액=취소 확인 단계 | 필수 3개(주문번호·거래일자·매출금액) 미입력 시 "필수 항목을 모두 입력해주세요." · 매출금액이 음수면 즉시 등록되지 않고 앰버 경고("음수 금액은 매입취소로 처리되며, 정산 완료 건은 환수(CANCEL_CLAWBACK)가 생성됩니다. 되돌리기 어려운 작업입니다.")가 뜨고 [돌아가기]/[취소로 등록]으로 한 번 더 확인 | H | components/sales/ManualSalesModal.tsx:68-85,179-184,291-301 |
| 1675:157 | [취소] · [등록] → 성공 시 목록 재조회 | 버튼 구성·성공 동작 변경 | [취소] · [등록] → 음수 확인 상태에선 [돌아가기] / [취소로 등록](앰버) · 성공 시 '등록 완료' 결과 요약으로 전환, [확인]/닫기 시 목록 재조회 | H | components/sales/ManualSalesModal.tsx:283-311,111-138 |
| 1675:452 | 성공 응답이면 모달을 닫고 상위 원장 목록을 재조회. 실패면 서버 메시지를 모달 상단에 표시. | 결과 요약 경유 + 이미 취소 건 스킵 표시 누락 | 성공 응답이면 '등록 완료' 결과 요약을 먼저 표시 — 이미 매입취소된 건이면 "이미 매입취소 (되돌림 방지)"로 원장 미반영을 알림 — 닫을 때 상위 원장 목록을 재조회. 실패면 서버 메시지를 모달 상단에 표시. [확정] | H | components/sales/ManualSalesModal.tsx:111-138; lib/manualSalesResult.ts:120-137 |
| 1675:167 | keynote: … 이 탭에만 있는 '현장결제(만나서결제)' 체크가 핵심 분기점으로 … | 두 번째 분기(음수=취소 신호) 누락 | (기존 문장 유지 후 추가) 또 하나의 분기는 금액 부호다 — 배달 단건은 '구분' 선택이 없어 음수 금액이 유일한 취소 신호이며, 음수 등록은 매입취소+환수(CANCEL_CLAWBACK) 생성으로 이어져 등록 전 확인 단계를 거친다. 등록 성공 시엔 결과 요약을 거쳐 목록을 재조회한다. | M | components/sales/ManualSalesModal.tsx:68-70,82-85 |
| 1675:404 (+410) | 탭 공통으로 주문번호·거래일자·매출금액 3개만 필수 … 이 3개만 채우면 등록된다. | 음수 예외 누락 | 탭 공통으로 주문번호·거래일자·매출금액 3개만 필수. 하나라도 비면 '필수 항목을 모두 입력해주세요' 안내. 단 매출금액이 음수면 3개를 채워도 취소 확인 단계를 한 번 더 거치며, 금액을 고치면 확인 상태가 자동 해제된다. [확정] | M | components/sales/ManualSalesModal.tsx:72-85,204-208 |

- SCREEN_STALE: 2661:65774 구 라벨.
- 비고: 이 시트에는 '코드 근거' 섹션이 원래 없음(추가 여지). 광고비 payload(1675:280 adCampaign 미노출) 서술은 develop에서도 동일(입력칸 없음·빈값 전송) — 유지.

---

## 1676:2 AD_SALES_DT_EXCEL — 판정: 부분 수정 + SCREEN_STALE

| 텍스트 노드ID | 현재 문구(요약) | 무엇이 틀렸나 | 제안 문구(전체) | 심각도 | 코드 근거 |
|---|---|---|---|---|---|
| 1676:146 | 타입 · 신규 · 중복 · 에러 건수 카드 + 행별 표(행/상태/주문·승인번호/거래일자/금액/카드사·플랫폼) | 미리보기 표에 '구분' 열 신설 누락 | 타입 · 신규 · 중복 · 에러 건수 카드 + 행별 표(행/상태/구분/주문·승인번호/거래일자/금액/카드사·플랫폼) · '구분' 열은 매입(PURCHASE) 타입이 아닐 때만 노출 — 행의 구분값 또는 승인상태, 없으면 '-' | H | components/sales/ExcelUploadModal.tsx:204-206,218-220 |
| 1676:167 | "업로드 완료" + 성공/중복/실패 건수 · [확인] 누르면 목록 재조회 | 결과 단계 전면 개편 누락 | 결과 요약: 상황별 제목("업로드 완료" / "업로드 완료 (일부 실패)" / "업로드 완료 (확인 필요)") + 전체 N건 + 성공/중복/실패 + 기타 건수(취소 참조 행 반영·선정산 완료 건 보호·이미 승인취소/매입취소 되돌림 방지·미처리 취소·환수(CANCEL_CLAWBACK) 생성 실패) + 서버 경고 목록 · [확인]은 물론 X·배경 클릭으로 닫아도 목록 재조회 | H | components/sales/ExcelUploadModal.tsx:115-126,240-249; components/sales/ManualSalesResultSummary.tsx:26-56; lib/manualSalesResult.ts:52-96 |
| 1676:446 (+452) | 3단계 결과에서 성공 · 중복 · 실패 건수를 서버 확정값으로 다시 표시 / 미리보기의 예상 집계와 별개로, 실제 반영 결과를 재확인 | 기타·경고·중복 주석 확장 누락 | 3단계 결과에서 전체·성공·중복·실패에 더해 기타(선정산 완료 건 보호=수정 안 함 · 이미 취소 건 되돌림 방지 · 취소 참조 행 반영 · 미처리 취소 · 환수 생성 실패)와 서버 경고를 서버 확정값으로 표시. 중복은 '기존 원장을 갱신한 건수'로 성공 건수와 겹칠 수 있다는 주석이 붙는다. 미리보기의 예상 집계와 별개로 실제 반영 결과를 재확인. [확정] | M | components/sales/ManualSalesResultSummary.tsx:60-70; lib/manualSalesResult.ts:52-96 |
| 1676:188 | keynote: … (3) 파싱과 저장이 별도 단계로 분리돼 … 서버 전용이라 확인필요. | 결과 집계 세분화 누락 | (기존 문장 유지 후 추가) 저장 결과는 성공/중복/실패 3종을 넘어 선정산 완료 건 보호, 이미 취소 건 스킵, 취소 참조 행, 미처리 취소, 환수(CANCEL_CLAWBACK) 생성 실패까지 세분 집계·경고로 돌려주며, 프런트는 이를 공용 결과 요약으로 표시한다. | M | lib/manualSalesResult.ts:6-19,52-96 |
| 1676:544 | 결과 화면 성공/중복/실패 건수 표시 · components/sales/ExcelUploadModal.tsx:213-224 | 내용·위치 모두 구버전 — 공용 컴포넌트로 교체됨 | 결과 화면은 공용 요약 컴포넌트로 표시 · components/sales/ExcelUploadModal.tsx:240-249 + components/sales/ManualSalesResultSummary.tsx + lib/manualSalesResult.ts | M | components/sales/ExcelUploadModal.tsx:240-249 |
| 1676:517 | 확장자 .xls/.xlsx만 허용 · …:44-48 | 줄번호 | 확장자 .xls/.xlsx만 허용, 그 외 차단 안내 · components/sales/ExcelUploadModal.tsx:51-56 | L | components/sales/ExcelUploadModal.tsx:51-56 |
| 1676:520 | 자동 인식 안내 · …:139-143 | 줄번호 | 카드 승인내역/매입내역·배달 단건등록 양식 자동 인식 안내 · components/sales/ExcelUploadModal.tsx:160-166 | L | components/sales/ExcelUploadModal.tsx:160-166 |
| 1676:523 | 서버가 dataType 판정·타입 표시 · …:53-56,154-161 | 줄번호 | 서버가 dataType(APPROVAL/PURCHASE/배달)을 판정해 반환·타입 표시 · components/sales/ExcelUploadModal.tsx:61-64,174-183 | L | components/sales/ExcelUploadModal.tsx:61-64,174-183 |
| 1676:526 | 행별 신규/중복/에러 판정·에러행 강조 · …:13-15,191,97-105 | 줄번호 | 행별 신규/중복/에러 상태 판정 및 에러행 강조 · components/sales/ExcelUploadModal.tsx:19-31,105-113,215 | L | components/sales/ExcelUploadModal.tsx:19-31,105-113,215 |
| 1676:529 | 상단 4칸 집계 · …:152-175 | 줄번호 | 상단 타입·신규·중복·에러 4칸 집계 · components/sales/ExcelUploadModal.tsx:172-197 | L | components/sales/ExcelUploadModal.tsx:172-197 |
| 1676:532 | 중복 업데이트 경고 · …:204-208 | 줄번호 | 중복 건 기존 데이터 업데이트 경고 · components/sales/ExcelUploadModal.tsx:231-235 | L | components/sales/ExcelUploadModal.tsx:231-235 |
| 1676:535 | 저장 버튼 라벨·비활성 · …:240-243 | 줄번호 | 저장 버튼 라벨=신규+중복 건수, 둘 다 0이면 비활성 · components/sales/ExcelUploadModal.tsx:265-267 | L | components/sales/ExcelUploadModal.tsx:265-267 |
| 1676:538 | 업로드=파싱, 저장 별도 confirm · …:52-58,74-89 | 줄번호 | 업로드=파싱(preview), 저장은 별도 confirm 단계 · components/sales/ExcelUploadModal.tsx:58-70,82-99 | L | components/sales/ExcelUploadModal.tsx:58-70,82-99 |
| 1676:547 | 저장 시 사업자번호·타입·행 전달 · …:79-83 | 줄번호 | 저장 시 사업자번호·타입·행 전달 · components/sales/ExcelUploadModal.tsx:85-91 | L | components/sales/ExcelUploadModal.tsx:85-91 |

- SCREEN_STALE: 2661:66785 (모달 뒤 상세화면 구 라벨). 임베드된 모달 자체는 1단계(업로드) 화면이라 이번 변경(2·3단계)과 충돌 없음.
- 유지 확인: 3단계 골격, .xls/.xlsx 검사, 타입 자동 판정, 중복=갱신 방침, 저장 버튼 활성 조건, services/manualSalesService.ts 참조 — 모두 유효. 1676:158의 경고문 인용이 "(ON CONFLICT 처리)"를 생략한 것은 구코드 시점부터의 축약이라 diff 어긋남 아님.

---

## 1672:2 AD_SALES_DT_CARD — 판정: 현행 OK + SCREEN_STALE
- 카드사 2뎁스 필터 서술·줄 참조 모두 develop과 일치. 수정 없음.
- SCREEN_STALE: 2661:61641 구 라벨.

## 1674:2 AD_SALES_DT_OLD — 판정: 현행 OK + SCREEN_STALE
- 정렬 토글 서술(1674:102~125) develop과 일치. 수정 없음.
- SCREEN_STALE: 2661:64829 구 라벨.
- 비고(디프 무관, 기존 이슈): 심화 섹션이 placeholder 상태 — 1674:135 "test", 1674:143 "h", 1674:148 "a", 1674:152 "b". 별도 보완 필요.

---

## 집계

| 판정 | 시트 |
|---|---|
| 부분 수정 | 1584 AD_SALES · 1598 AD_SALES_DT · 1603 BM · 1605 ADD_CARD · 1673 ADD_PURCHASE · 1675 ADD_DELIVERY · 1676 EXCEL (7개) |
| 현행 OK | 1600 PAYOUT · 1601 CANCEL · 1602 NORMAL · 1604 ADJUST · 1672 CARD · 1674 OLD (6개, 단 1674 심화 placeholder) |
| SCREEN_STALE | 1584 제외 12개 시트 전부 (임베드 화면의 "광고비 차감 (배민 우리가게클릭)" 구 라벨) |

수정 필요 텍스트 노드: **총 57개** (H 9 · M 21 · L 27)
