# 프론트 코드 수정요청 목록 (감사 파생 — 스펙에서 못 고치는 것)

2026-08-11 감사 2라운드에서 확인된 **프론트 레포 자체의 문제**. 화면설계서·피그마는 교정 완료('AUDIT_FINAL.md' 참조), 아래는 실제 코드 문자열/데이터 수정이 필요해 개발 협의 대상.

## 🔴 우선 (대외 노출 · 확정 정책과 충돌)
1. **[C2] "매일 오전 11:30" 단일 컷오프 하드코딩** — 확정된 하루 2회(11:30·18:00) 미반영, 18:00 배치 누락 안내.
   - `02_payhug-merchant-web-main/app/settlement/account/excluded/page.tsx:15` (EXCLUDED_BANNER)
   - `01_payhug-admin-web-main/app/merchants/[id]/page.tsx` "매일 오전 11:30 자동 실행"
   - `02.../components/dashboard/PreSettlementCard.tsx:19-24` (JSDoc T+1·11:30 — 주석)
2. **[C2+C4] 랜딩 FAQ** (`02.../app/page.tsx:380-412`): "365일 매일" / "다음 날부터(D+1)" / "내일 오전 12시 이전 지급" 상호 모순 + 근거 없는 "최소 5만원" + 용어 드리프트 "정산조정"(실 라벨=예상 지급 차액) + "1원의 오차도 발생하지 않습니다"(C4 미확정과 충돌).

## 🟠 중요 (정합성 리스크)
3. **[C1] 계약 수수료율 자유입력** (`02.../components/ContractSignInput.tsx:195`): 채권매입 수수료율이 검증·기본값·범위 없이 free-text → 계약 PDF 직행. C1 미확정 지뢰가 계약서로 그대로 유입되는 구조.
4. **[C1/C5] `marginFee` 필드 의미 충돌**: 정산 상세(`app/settlement/page.tsx:377`)에선 "수수료 부가세(VAT)"(본체 수수료는 비노출), 매출 도메인(`services/salesService.ts:112`, `components/SalesCalendarCard.tsx:353`)에선 채권매입 수수료 **본체**. 같은 필드명이 두 의미 — 정리 필요.
5. **[약관 체계 불일치] admin mock 데이터의 '매출채권 양도 동의서'**: 어드민 가맹점 서류/동의서 목록에 '매출채권 양도 동의서' 문서행이 존재해 다수 어드민 화면에 노출(추출 네이티브 화면들에서 확인). 실제 약관 체계(signup 4·contract 6)에 이 약관은 없음 → mock 데이터 정리 or 실재 약관으로 교체 확인.

## 🟡 다듬기 (라벨·표시 로직)
6. **회원가입 진행 점 4개 중 4번째 영구 비활성** (`app/signup/page.tsx:323-326`): 실제 3단계인데 점 4개 렌더 → 3개로 정리 or 4단계 복원.
7. **계약 진행바**: confirm-settlement(4단계)가 5/5로 렌더(`app/contract/confirm-settlement/page.tsx:177-181`) — 단계 표시 로직 정리. 허브 6단계 vs 스텝 페이지 5칸 분모 불일치도 동일 계열.
8. **명칭 혼재**: 성공 모달 "정산 계좌" vs 라벨 "입금 받을 계좌"(DEPOSIT_VERIFY) / admin "입출금 계좌 등록"(모달)·"입출금 전용계좌"(배지)·"입금 계좌"(서류 단계) 3종 병존.
9. **오타**: 가입 완료 안내 "매장 매출를 조회" (`app/signup/complete/page.tsx:84`).
10. **[C5/C6] AD_LOG 회수 뱃지**: 매출대금 스윕(COLLECTION)과 부채 회수(DEBT_RECOVERY)가 같은 '회수' 뱃지에 혼재 — 개념 분리 표기.

## 참고 — Figma 추출 화면 구버전 라벨 (Figma는 교정 완료)
- 추출 네이티브 868/873/878의 전체동의 라벨이 "모두 동의"였음 → 코드(`signup/page.tsx:358`)는 "전체 동의". Figma 소스·클론 10개 노드 교정 완료(2026-08-11). 향후 재추출 시 최신 빌드 기준으로 뜰 것.
