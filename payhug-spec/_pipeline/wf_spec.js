export const meta = {
  name: 'payhug-admin-func-spec',
  description: '어드민 프론트 전체를 12개 도메인으로 나눠 기능+정책 로직+데이터 흐름을 기획자 언어로 심층 추출 후 적대적 검증(프론트 한도, 서버 전용은 확인필요)',
  phases: [
    { title: 'Extract', detail: '도메인별 프론트 코드에서 기능·로직·정책·데이터 추출' },
    { title: 'Verify', detail: '코드 재대조 사실검증 + 누락보완 + 확인필요 정직표기' },
  ],
}

const ROOT = '/Users/semi/cursor/payhug/01_payhug-admin-web-main'

const DOMAINS = [
  { key: 'settlement_calc', label: '정산 — 선정산 계산·수수료 정책·정산상품',
    focus: '선정산이 어떻게 계산되는가(수수료 3종→원장→이해관계자 배분→지급액), 정산상품(정책=일반/다우)에 담기는 설정(참여자·요율·납부/수취), 정산 시뮬레이터',
    files: ['app/settlement/simulation/page.tsx','app/settlement/policies/page.tsx','app/settlement/policies/PolicyFormModal.tsx','services/settlementService.ts','lib/settlementLabels.ts','lib/platformSettlementConstants.ts','types/settlement.ts'] },
  { key: 'settlement_ops', label: '정산 — 정산현황·배치마감·배분원장·이체·예상지급·VOC·세금계산서',
    focus: '정산 데이터 파이프라인(동기화→정산처리→배치마감), 배치별 배분 원장, 이체 기록·수동이체 표시, 예상 지급(주말·장애 시 평균매출 기반), VOC 엑셀, 세금계산서 발행',
    files: ['app/settlement/overview/page.tsx','app/settlement/overview/BatchDetailTab.tsx','app/settlement/overview/PreSettlementTab.tsx','app/settlement/overview/TransferRecordsTab.tsx','app/settlement/overview/VocExportTab.tsx','app/settlement/overview/TaxInvoiceTab.tsx','hooks/useSettlementOverview.ts','hooks/usePurchaseLedger.ts','services/batchService.ts','services/settlementService.ts'] },
  { key: 'sales', label: '매출 — 매출 조회·카드/배달 상세·수기매출·엑셀업로드',
    focus: '스크래핑 매출 조회, 가맹점별 매출 상세(카드/배달 원천), 수기 매출 입력·수정, 엑셀 업로드, 매출 데이터 출처·구분(예상/확정)',
    files: ['app/sales/page.tsx','app/sales/[bizNo]/page.tsx','services/manualSalesService.ts','components/sales/ExcelUploadModal.tsx','components/sales/ManualSalesModal.tsx','hooks/useDashboardData.ts'] },
  { key: 'merchant_core', label: '가맹점 — 목록·상세·승인/반려/이관·계약·플랫폼계정·증빙서류',
    focus: '가맹점 목록·상태 필터, 상세 종합, 승인/반려/이관 흐름과 조건, 소개파트너·담당·투자자, 플랫폼 계정(락계좌 연결), 증빙 서류·계좌 등록(통장사본·쿠콘·하나은행 빠른조회), 계약서·서명·약관',
    files: ['app/manage/page.tsx','app/merchants/[id]/page.tsx','services/merchantService.ts','components/MerchantDocumentEditModals.tsx','components/MerchantExternalAccounts.tsx','components/PlatformLockAccountStatus.tsx','components/PlatformLockAccountDetailDialog.tsx','types/merchant.ts'] },
  { key: 'merchant_fee', label: '가맹점 — 카드수수료·차액정산·락계좌입금·이관부채·평균매출·수동이체·문의/메모',
    focus: '카드사별 수수료율 설정·선정산 포함, 예상↔확정 차액 정산(환급/추가차감), 락계좌 입금내역·모계좌 스윕, 이관 부채=회수 모드, 요일별 평균매출(예상 산출근거), 수동 이체, 가맹점 문의·내부 메모',
    files: ['app/merchants/[id]/page.tsx','app/merchants/[id]/fee-adjustments/page.tsx','app/settlements/[id]/fee-adjustments/page.tsx','components/MerchantCardFees.tsx','components/LockAccountDeposits.tsx','components/MerchantDebtManagement.tsx','components/FeeAdjustmentSummary.tsx','components/MerchantAvgSalesSummary.tsx','components/MerchantInquiries.tsx','components/MerchantMemos.tsx','components/ManualTransferModal.tsx'] },
  { key: 'partners', label: '파트너 — 제휴사·영업조직·투자자·대리점·관리자·페이허그',
    focus: '파트너 유형별 관리, 등록·수정·비활성·삭제, 파트너 체인·수수료 수취 관계, 투자자 매칭, 대리점 코드, 계정 권한',
    files: ['app/partners/page.tsx','services/partnerService.ts'] },
  { key: 'terms', label: '약관 — 버전·유형·컨텍스트·마케팅·계약 약관',
    focus: '약관 유형·버전 관리, 신규/개정·고정, 컨텍스트별 노출, 마케팅 동의, 계약 약관, 미리보기',
    files: ['app/terms/page.tsx','services/termsService.ts'] },
  { key: 'inquiries', label: '1:1 문의 — 정산/계정/기술 분류·상태 처리',
    focus: '문의 목록·필터, 분류(정산·결제·계정·기술·일반), 상태(대기·처리중·답변완료·종료), 답변, 미답변 집계',
    files: ['app/inquiries/page.tsx'] },
  { key: 'balance', label: '모계좌 — 잔액·입금·락계좌 스윕 회수',
    focus: '페이허그 모계좌 잔액·입금 내역, 락계좌→모계좌 스윕(어드민 매출 회수)과 정책상 과지급 회수의 구분',
    files: ['app/account-balance/page.tsx'] },
  { key: 'scraping', label: '스크래핑 — 장애 이력·쿠콘 락계좌 검증',
    focus: '스크래핑 장애 이력 조회, 플랫폼(여신협회·배민·요기요·쿠팡) 검증 상태(정상·이상·장애·스킵·검증제외), 쿠콘 락계좌 검증·빠른조회',
    files: ['app/scraping-incidents/page.tsx','services/cooconService.ts'] },
  { key: 'logs_ai', label: '로그·AI — 활동 로그·AI 로그 분석·모니터링',
    focus: '어드민 활동 로그, AI 기반 로그 분석·모니터링·질의응답(AI 어시스턴트), 요약 지표',
    files: ['app/activity-logs/page.tsx','app/log-analysis/page.tsx','services/logAnalysisService.ts'] },
  { key: 'auth_common', label: '인증·공통 — 로그인·권한·탭 시스템·레이아웃',
    focus: '로그인·인증, 권한 구분(관리자/페이허그/파트너 조회전용)이 기능 노출에 미치는 영향, 멀티탭 워크스페이스, 공통 레이아웃·토스트',
    files: ['app/login/page.tsx','components/AdminLayout.tsx','components/TabContext.tsx','services/authService.ts','lib/apiClient.ts','lib/config.ts'] },
]

const SPEC_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['key', 'label', 'intro', 'features'],
  properties: {
    key: { type: 'string' },
    label: { type: 'string' },
    intro: { type: 'string', description: '도메인 개요 2-3문장(기획자 언어)' },
    features: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        required: ['name', 'what', 'status'],
        properties: {
          name: { type: 'string', description: '기능명(짧게)' },
          what: { type: 'string', description: '무엇을 하는 기능인가 1-2문장' },
          logic: { type: 'string', description: '핵심 로직·계산·조건 분기. <b>강조, 줄바꿈 \\n, 하위설명 "– ". 개발용어 금지.' },
          settings: { type: 'string', description: '관련 설정·연결(선택)' },
          data: { type: 'string', description: '데이터 출처·흐름·시각 구분(선택)' },
          notes: { type: 'string', description: '정책·주의·미확정(C1 수수료율/C2 지급캘린더/C4 예상차액 등). 서버 전용이면 명시.' },
          status: { type: 'string', enum: ['확정', '가설', '확인필요'] },
        },
      },
    },
    citations: {
      type: 'array',
      items: { type: 'object', additionalProperties: false, required: ['claim', 'ref'],
        properties: { claim: { type: 'string' }, ref: { type: 'string' } } },
    },
  },
}

function extractPrompt(d) {
  const files = d.files.map(f => `${ROOT}/${f}`).join('\n')
  return `너는 PayHug 선정산 서비스의 서비스기획 검토자다. 어드민 프론트 기능명세서의 "${d.label}" 도메인을 코드에서 작성한다.

이 도메인 초점: ${d.focus}

[정독할 파일]
${files}

[임무]
이 도메인의 **모든 기능**을 빠짐없이 뽑아, 기획자가 알아야 할 로직·정책·설정·연결·데이터 출처를 정리하라. 기능 하나하나를 features 배열에 담아라(무엇을 하나 what, 핵심 로직 logic, 설정·연결 settings, 데이터 출처 data, 정책·주의 notes).

[작성 규칙 — 엄수]
1. **기획자 언어**. 함수명·변수명·route(/admin/...)·DB·상태상수(ACTIVE 등)·"쿼리" 등 개발용어 금지. 서비스 용어로 풀어써라.
2. 6대 개념(미지급금·선정산 제외금액·바로이체·과지급·미회수금·환급)을 섞지 마라. 어드민 "매출 회수"(락계좌→모계좌 스윕)와 정책 "회수"(과지급 회수)는 다른 개념.
3. 각 기능에 **확정/가설/확인필요** 표기. 코드가 명확하면 확정.
4. **서버(백엔드)에서만 확정되는 것은 프론트에 없다** → 반드시 확인필요로 표기: (a)특정 금액의 최종 산술·반올림·부호처리, (b)스크래핑 정확한 스케줄 시각, (c)수수료율 실제 확정값(C1), (d)지급 캘린더 D+N(C2), (e)'예상 지급 차액' 정의(C4). 화면이 "표시만" 하는 값은 서버 계산임을 밝혀라.
5. 값 부호(양수/음수)·지급완료 여부로 처리가 갈리는 지점, 권한(관리자/파트너 조회전용)에 따른 노출 차이를 명시.
6. 핵심 주장마다 citations에 file:line 근거.

가능한 한 상세하고 완전하게. 반환은 SCHEMA(JSON)만.`
}

function verifyPrompt(d, draft) {
  const files = d.files.map(f => `${ROOT}/${f}`).join('\n')
  return `너는 서비스기획 검토자이자 적대적 완결성 비평가다. "${d.label}" 도메인 기능명세 초안을 코드와 대조해 최종본으로 만든다.

[초안 JSON]
${draft}

[원본 코드 — 다시 읽어 대조]
${files}

[검증]
1. 사실검증 — 각 기능·로직이 코드와 일치하는가? 틀리거나 추정된 것은 코드에 맞게 고치거나 확인필요로 내려라.
2. 누락보완 — 이 도메인 코드에 있는데 초안이 빠뜨린 기능/로직/설정/연결/데이터가 있는가? 추가하라. 특히 조건 분기·권한별 노출·예외(주말/장애/법인/기록용/회수전용/면제)·데이터 시각 구분.
3. 정직성 — 개발용어 잔재 제거. 서버 전용값(최종 산술·스크래핑 시각·확정 수수료율·지급 캘린더·예상차액)이 확정으로 표기됐으면 확인필요로 내려라.

[출력] 초안과 동일 SCHEMA로, 수정·보완 반영된 **완성본 전체**. 개발용어 0. JSON만.`
}

phase('Extract')
const results = await pipeline(
  DOMAINS,
  (d) => agent(extractPrompt(d), { label: `ext:${d.key}`, phase: 'Extract', schema: SPEC_SCHEMA, effort: 'high' }),
  (draft, d) => {
    if (!draft) return null
    return agent(verifyPrompt(d, JSON.stringify(draft)), { label: `ver:${d.key}`, phase: 'Verify', schema: SPEC_SCHEMA, effort: 'high' })
  },
)
const final = results.filter(Boolean)
const featCount = final.reduce((a, d) => a + (d.features || []).length, 0)
log(`도메인 완료 ${final.length}/${DOMAINS.length} · 기능 ${featCount}개`)
return { domains: final }
