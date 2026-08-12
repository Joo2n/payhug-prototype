# 화면 조작·코드괴리 감사 — 최종 종합 (2026-08-09, 2라운드/6에이전트)

> **✅ 교정 완료(2026-08-11)**: §1 F1~F5 + §2 M1~M7(확인필요 제외) 전부 반영 — HTML 18파일 42치환 + **피그마 303:173 키노트 59노드**(F1 26+F2 29+잔존1+재구성3) + **네이티브 '모두 동의'→'전체 동의' 10노드**(소스 868/873/878 + 클론 7, 코드 L358 기준). §3은 스펙 아닌 프론트 이슈 → `FRONTEND_FIX_REQUESTS.md`로 이관. §4 잔여 리스크는 미해소(필요 시 Round 3).

진실=프론트 코드(01_admin, 02_merchant + 각 lib/devMockData.ts). 화면=spec/design/(07.21판)·spec/mc_designdoc/(07.28 심화판)·일부 design_fig/design_plus 변형. **피그마 303:173 실물은 약관 클린 확정**(868/873/878=signup 4, contract 6) — 아래 잔존은 주로 HTML 설계문서.

핵심: design/·mc_designdoc/는 두 세대라 조작이 **양방향**. 신판이 고친 것도, 새로 지어낸 것도 있음.

## 1. 지어낸 것 (FABRICATION — 약관과 동류, 최우선)
| # | 파일 | 조작 내용 | 코드 진실 | 잘못된 쪽 | 심각 |
|---|---|---|---|---|---|
| F1 | `mc_designdoc/PH_JO_TERMS.html` (L115-116,120) | 회원가입 약관 5개(**매출채권 양도 동의**·개인정보 제3자 제공 포함) | signup 4개(고유식별 포함, 매출채권양도 코드에 없음, 제3자제공은 contract용) | mc_designdoc | 🔴 |
| F2 | `mc_designdoc/PH_JO_TERMS_ALL.html` | "필수3·선택2"(5) — F1 전파 | 필수3+선택1=4 | mc_designdoc | 🔴 |
| F3 | `design/MC_CONTRACT_DEPOSIT_GATE.html` (L58,78) | "근거 약관 **제8조④**" | 제8조·①②③④ 마커 코드에 전무. 게이트 로직 자체는 실재 | design | 🟠 |
| F4 | `design/MC_CONTRACT_LOCK_INFO.html` (L58,86) | "이용계약 **제7조①** 지정계좌=하나은행" | 제7조는 admin '회수' 조항(지정계좌 무관). 하나은행/081 사실은 실재(bankCodeMap) | design | 🟠 |
| F5 | `mc_designdoc/MC_MYINFO_CONTRACT_TERMS.html` (L110,112) | 제2조가 "**채권매입수수료** 정의" 명시 | 제2조(정의)=선정산만. 채권매입수수료=원장 라벨(MARGIN)일 뿐 약관 정의어 아님 | mc_designdoc | 🟠(확인필요) |

## 2. 코드와 어긋난 라벨/숫자 (스펙에서 다듬기)
| # | 파일 | 표시 | 코드 | 심각 |
|---|---|---|---|---|
| M1 | `mc_designdoc/MC_LANDING.html` | FAQ "10문항" | app/page.tsx = 9문항 | Med |
| M2 | `mc_designdoc/PH_JO_AUTH.html`·`PH_JO_PW.html` | "2/4"·"3/4" 사실단정 | 4번째 점 영구 회색, 실제 3단계(design판은 확인필요 캐비엇) | Med |
| M3 | `mc_designdoc/` BIZ/ID 4종 진행바 | "N/6" | 코드 5칸(design판 정확) | Med |
| M4 | `mc_designdoc/MC_CONTRACT_DEPOSIT_INFO.html` | "4칸" | 코드 5/5 | Low |
| M5 | `AD_MERCHANT_DT_BANKACCT`(design·design_fig·design_plus) | 입출금(비-락) 모달에 "계좌 출금 비밀번호" 필드 + 제목 "입출금 **전용**계좌 등록" | 그 필드는 PRE_PAYMENT(락)에서만 렌더 / 제목 "입출금 계좌 등록"(전용X) | Med |
| M6 | PH_JO_TERMS(_ALL) | 전체동의 "모두 동의" | 실제 버튼 "전체 동의"(signup page.tsx:358) | Low |
| M7 | 기타 | AD_SALES_DT "완료=파랑"(실 인디고)/AD_SIM "저장하지 않고"(실 "DB 저장 없이")/AD_TERMS 허브 "3종"vs필터4/PH_JO_DONE "매출을"(실 "매출를")/PH_LO 직계약·총판 판별필드 과장/MC_DASH_INQUIRY 상태 과다 | 코드 참조 | Low |

## 3. 프론트 코드 자체 문제 (스펙 잘못 아님 — 프론트 레포 수정 사안, 대부분 스펙이 이미 C# 플래그)
- ST_AC_EX·어드민·MC_DASH·MC_LANDING_FAQ: "매일 11:30 단일" 하드코딩 → **확정 하루 2회(11:30·18:00) 중 18:00 누락**(C2). 중상, 대외노출.
- MC_LANDING: 근거없는 "최소 5만원" / 용어드리프트 "정산조정"(실 예상 지급 차액) / "1원 오차 없음"(C4충돌).
- MC_CONTRACT_SIGN_INPUT: 채권매입 수수료율 자유입력(검증X)→계약PDF 직행(C1 실리스크).
- ST_MA: marginFee 필드가 정산=VAT, 매출=수수료본체 의미충돌.
- AD_LOG: 회수 뱃지에 매출대금 스윕+부채회수 혼재.

## 4. 아직 검증 못한 잔여 리스크 (필요 시 Round 3)
1. 임베드 스크린샷 **픽셀 내부**(텍스트 감사만 함).
2. 약관 **본문 조문 문구**(이름/개수/필수만 검증).
3. 알림톡 "15종" 케이스 vs 06 문서 정합.
4. **design/-only 어드민 상세 하위화면 ~24개**(AD_MERCHANT_DT_*, AD_SALES_DT_*, AD_TERMS_* 관리, AD_SETTLE_TRANSFER* 등) — 단일세트라 비대칭검증 안 걸림, 단일세트 조작 잔여 가능.
5. 금액·수식 재계산 정확도.

## ✅ 클린 확정(대표)
피그마 signup 4·contract 6(교차확인)·플랫폼 목록·계약 허브·락계좌 20일·회수 4개념 분리·상태값 enum·알림톡 템플릿 지어냄0·수수료율 사실단정0·로그인/비번/문의/어드민 상품·파트너·시뮬(수수료표는 코드 mock 실재, 화면은 C1 미확정 플래그).
