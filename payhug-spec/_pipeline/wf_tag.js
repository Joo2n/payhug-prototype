export const meta = {
  name: 'payhug-spec-tag',
  description: '기능명세서 197기능에 화면·권한 태그 부여 + 초안3도메인 누락 기능 점검(코드 대조)',
  phases: [{ title: 'Tag', detail: '도메인별: 각 기능에 screen·permission 태그 + 누락 기능 보완' }],
}

const ROOT = '/Users/semi/cursor/payhug/01_payhug-admin-web-main'
const SPEC = '/private/tmp/claude-501/-Users-semi-cursor-payhug/d08c4a93-21cd-4310-99c5-3c1fc6fa88f5/scratchpad/spec_content.json'

// spec_content 도메인 순서와 1:1 정렬(파일·초안여부)
const DOMAINS = [
  { files: ['app/settlement/simulation/page.tsx','app/settlement/policies/page.tsx','app/settlement/policies/PolicyFormModal.tsx','services/settlementService.ts','lib/settlementLabels.ts','lib/platformSettlementConstants.ts','types/settlement.ts'], draft: false },
  { files: ['app/settlement/overview/page.tsx','app/settlement/overview/BatchDetailTab.tsx','app/settlement/overview/PreSettlementTab.tsx','app/settlement/overview/TransferRecordsTab.tsx','app/settlement/overview/VocExportTab.tsx','app/settlement/overview/TaxInvoiceTab.tsx','hooks/useSettlementOverview.ts','hooks/usePurchaseLedger.ts','services/batchService.ts'], draft: false },
  { files: ['app/sales/page.tsx','app/sales/[bizNo]/page.tsx','services/manualSalesService.ts','components/sales/ExcelUploadModal.tsx','components/sales/ManualSalesModal.tsx','hooks/useDashboardData.ts'], draft: true },
  { files: ['app/manage/page.tsx','app/merchants/[id]/page.tsx','services/merchantService.ts','components/MerchantDocumentEditModals.tsx','components/MerchantExternalAccounts.tsx','components/PlatformLockAccountStatus.tsx','components/PlatformLockAccountDetailDialog.tsx','types/merchant.ts'], draft: true },
  { files: ['app/merchants/[id]/page.tsx','app/merchants/[id]/fee-adjustments/page.tsx','app/settlements/[id]/fee-adjustments/page.tsx','components/MerchantCardFees.tsx','components/LockAccountDeposits.tsx','components/MerchantDebtManagement.tsx','components/FeeAdjustmentSummary.tsx','components/MerchantAvgSalesSummary.tsx','components/MerchantInquiries.tsx','components/MerchantMemos.tsx','components/ManualTransferModal.tsx'], draft: true },
  { files: ['app/partners/page.tsx','services/partnerService.ts'], draft: false },
  { files: ['app/terms/page.tsx','services/termsService.ts'], draft: false },
  { files: ['app/inquiries/page.tsx'], draft: false },
  { files: ['app/account-balance/page.tsx'], draft: false },
  { files: ['app/scraping-incidents/page.tsx','services/cooconService.ts'], draft: false },
  { files: ['app/activity-logs/page.tsx','app/log-analysis/page.tsx','services/logAnalysisService.ts'], draft: false },
  { files: ['app/login/page.tsx','components/AdminLayout.tsx','components/TabContext.tsx','services/authService.ts','lib/apiClient.ts','lib/config.ts'], draft: false },
]

const TAG_SCHEMA = {
  type: 'object', additionalProperties: false, required: ['idx', 'tags'],
  properties: {
    idx: { type: 'number' },
    tags: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false, required: ['name', 'screen', 'permission'],
        properties: {
          name: { type: 'string', description: '기존 기능명 그대로(매칭용)' },
          screen: { type: 'string', description: '이 기능이 속한 어드민 화면명(짧게). 예: 가맹점 상세, 정산 시뮬레이션, 매출 조회, 정산 상품 관리' },
          permission: { type: 'string', enum: ['관리자 전용', '관리자·페이허그', '파트너 조회', '공통'] },
        },
      },
    },
    extra_features: {
      type: 'array', description: '초안 도메인에서 코드엔 있는데 목록에 빠진 중요 기능(있을 때만, 보통 0~5개)',
      items: {
        type: 'object', additionalProperties: false, required: ['name', 'what', 'status', 'screen', 'permission'],
        properties: {
          name: { type: 'string' }, what: { type: 'string' }, logic: { type: 'string' },
          settings: { type: 'string' }, data: { type: 'string' }, notes: { type: 'string' },
          status: { type: 'string', enum: ['확정', '가설', '확인필요'] },
          screen: { type: 'string' }, permission: { type: 'string', enum: ['관리자 전용', '관리자·페이허그', '파트너 조회', '공통'] },
        },
      },
    },
  },
}

// 스크립트에서 파일 읽기 불가 → boot 에이전트가 spec_content를 읽어 도메인별 feature 이름을 넘김
const BOOT_SCHEMA = {
  type: 'object', additionalProperties: false, required: ['domains'],
  properties: { domains: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['idx', 'label', 'names'],
    properties: { idx: { type: 'number' }, label: { type: 'string' }, names: { type: 'array', items: { type: 'string' } } } } } },
}

phase('Tag')
const boot = await agent(
  `Read JSON ${SPEC}. It has {domains:[{key,label,features:[{name,...}]}]}. Return {domains:[{idx, label, names:[each feature.name]}]} where idx is the array index (0-based).`,
  { label: 'boot', phase: 'Tag', schema: BOOT_SCHEMA, effort: 'low' })

const bl = (boot && boot.domains) || []

function tagPrompt(d, files, isDraft, names) {
  return `너는 PayHug 어드민 기능명세서에 화면·권한 태그를 붙인다. 도메인="${d.label}" (idx=${d.idx}).

[코드 정독]
${files.map(f => `${ROOT}/${f}`).join('\n')}

[이 도메인의 기존 기능 목록 (이름 그대로 매칭)]
${names.map((n, i) => `${i + 1}. ${n}`).join('\n')}

[임무]
각 기능에 대해:
- **screen**: 그 기능이 실제로 나타나는 어드민 화면명(짧게, 예: "가맹점 상세", "정산 시뮬레이션", "매출 조회", "정산 상품 관리", "1:1 문의", "약관 관리"). 코드의 라우트/화면 구조로 판단.
- **permission**: 누가 쓰나 — '관리자 전용'(관리자만) / '관리자·페이허그'(내부 둘 다 편집) / '파트너 조회'(파트너도 조회 가능) / '공통'(로그인 전체). 코드의 권한 분기로 판단, 불명확하면 '관리자·페이허그'.
tags 배열에 {name(기존 이름 그대로), screen, permission}로 반환.
${isDraft ? `\n[추가·이 도메인은 검증 미완] 코드엔 있는데 위 목록에 **빠진 중요 기능**이 있으면 extra_features에 담아라(무엇을 what·로직 logic·상태 status·screen·permission 포함, 기획자 언어, 개발용어 금지). 없으면 빈 배열. 과하게 쪼개지 말고 의미있는 기능만.` : '\nextra_features는 빈 배열.'}

반환은 SCHEMA(JSON)만. idx=${d.idx}.`
}

const results = await parallel(bl.map(d => () => {
  const cfg = DOMAINS[d.idx] || { files: [], draft: false }
  return agent(tagPrompt(d, cfg.files, cfg.draft, d.names),
    { label: `tag:${d.idx}:${d.label.slice(0, 12)}`, phase: 'Tag', schema: TAG_SCHEMA, effort: cfg.draft ? 'high' : 'medium' })
}))

const ok = results.filter(Boolean)
const nTags = ok.reduce((a, r) => a + (r.tags || []).length, 0)
const nExtra = ok.reduce((a, r) => a + (r.extra_features || []).length, 0)
log(`태깅 완료 ${ok.length}/${bl.length} · 태그 ${nTags} · 누락보완 ${nExtra}`)
return { results: ok }
