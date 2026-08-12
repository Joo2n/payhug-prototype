# 화면 조작·코드괴리 감사 — Round 1 종합 (2026-08-09)

4팀 병렬(계약·약관 / 정산·수수료 / 어드민 / 알림톡·상태값·캘린더 크로스컷). 진실=프론트 코드(01_admin, 02_merchant + devMockData). 화면=spec/design/*.html, spec/mc_designdoc/*.html.

## 총평
지어낸 콘텐츠는 **약관 잔존 1건 + 없는 조항 인용 2건**이 실질 전부. 나머지는 (a) 라벨/숫자 코드괴리(스펙에서 수정 가능) (b) 프론트 코드가 하드코딩한 미확정값이 화면에 반영(스펙 잘못 아님, 프론트 수정 사안) (c) 주석 vintage/gap.

## A. 잔존 조작 (약관과 동류 — 스펙에서 교정)
| # | 화면/파일 | 내용 | 코드 진실 | 심각도 |
|---|---|---|---|---|
| A1 | `mc_designdoc/PH_JO_TERMS.html` | 회원가입 약관 **5개**(매출채권 양도·개인정보 제3자 제공 포함) 잔존 | signup 4개(서비스이용약관·개인정보 수집 및 이용·고유식별 정보처리·마케팅). `design/PH_JO_TERMS.html`은 이미 교정됨→**mc_designdoc만 누락** | 🔴 High |
| A2 | `design/MC_CONTRACT_DEPOSIT_GATE.html` | "근거 약관 제8조④" 인용 | 코드 약관에 제8조 없음(제1·2조만). 게이트 로직 자체는 실재. mc_designdoc판은 이미 제거됨 | 🟠 Med |
| A3 | `design/MC_CONTRACT_LOCK_INFO.html` | "이용계약 제7조① 지정계좌=하나은행" 인용 | 제7조 없음. 081-only 규칙 자체는 실재(bankCodeMap) | 🟠 Med |

## B. 코드괴리 라벨/숫자 (스펙에서 다듬기)
- B1 `mc_designdoc/` BIZ/ID 진행바 "N/6" vs 코드 5칸 (design판은 정확). Med
- B2 `mc_designdoc/MC_CONTRACT_DEPOSIT_INFO.html` "4칸" vs 코드 5/5. Low
- B3 약관 전체동의 "모두 동의" vs 실제 버튼 "전체 동의"(signup page.tsx:358). Low
- B4 `AD_MERCHANT_DT_BANKACCT` 입출금(비-락) 모달에 "계좌 출금 비밀번호" 필드 표기 → 그 필드는 PRE_PAYMENT(락)에서만 렌더. **자기모순 노트**. Med
- B5 `AD_MERCHANT_DT_BANKACCT` 모달 제목 "입출금 전용계좌 등록" vs 실제 "입출금 계좌 등록"(전용 없음). Low
- B6 `AD_SALES` 승인버튼 과일반화 / `AD_SALES_DT` "완료=파랑"(실제 인디고, 파랑은 바로이체) / `AD_SIM` "저장하지 않고" vs "DB 저장 없이" / `AD_TERMS` 허브 "회원가입 3종" vs 필터 4개. Low
- B7 `ST_MA` `marginFee`가 정산화면=수수료 부가세(VAT), 매출화면=수수료 본체 → 필드 의미 충돌(스펙 미표기). Low-Med(확인필요)

## C. 프론트 코드 이슈(스펙 잘못 아님 — 프론트 문자열 수정 사안, 대부분 스펙이 이미 C# 플래그)
- C-a ST_AC_EX/어드민/MC_DASH: "매일 오전 11:30 단일" 하드코딩 → **확정된 하루 2회(11:30+18:00) 중 18:00 누락** (C2). 중상.
- C-b MC_LANDING_FAQ/MC_LANDING: "365일 매일/D+1/내일 0시 이전 지급" 상호모순 + 근거없는 "최소 5만원" + 용어드리프트 "정산조정"(실제 예상 지급 차액) + "1원 오차 없음"(C4충돌). 대외노출 부정확. 중.
- C-c MC_CONTRACT_SIGN_INPUT: 채권매입 수수료율 자유입력(검증 없음)→계약 PDF 직행 (C1 실제 리스크). 정보.
- C-d AD_LOG: 회수 뱃지에 매출대금 스윕+부채 회수 혼재(개념 분리 필요) — 스펙이 open question으로 정직 노출.

## D. 주석 위생(스펙 hygiene)
- D1 design/ vs mc_designdoc/ 캘린더 주석 vintage 상충(한쪽 구버전 D+1/D+2, 한쪽 하루2회). 세트 정합 필요.
- D2 `mc_designdoc/ST_AC.html` "매일 11:30"에 C2 플래그 누락(형제 화면들은 있음).

## ✅ 클린 확인(대표)
플랫폼 목록·계약 허브 6단계·락계좌 20일 안내·contract 6약관(교정 유지)·어드민 회수 4개념 분리·상태값 enum·알림톡 템플릿(지어냄 0)·수수료율 사실단정 0.

→ Round 2에서 검증/보강 중: 조항 인용 전수 grep, design↔mc_designdoc 비대칭 전수, 피그마 실물 교차확인, 미커버 화면군(문의/마이페이지/에러상태).
