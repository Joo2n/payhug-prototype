export const meta = {
  name: 'payhug-deepdive-wave1',
  description: 'Track B 1차 웨이브 — 핵심 도메인 어드민 12화면 코드 심층추출(로직·정책·데이터출처) 후 적대적 검증',
  phases: [
    { title: 'Extract', detail: '화면별 코드 심층 추출' },
    { title: 'Verify', detail: '코드 재대조 사실검증 + 누락보완' },
  ],
}

const ROOT = '/Users/semi/cursor/payhug/01_payhug-admin-web-main'
const DESIGN = '/Users/semi/cursor/payhug/payhug-spec/spec/design'

const SCREENS = [
  { page_id: 'AD_SALES', name: '매출 조회', focus: '스크래핑 매출을 가맹점별로 조회하는 목록 — 정렬 우선순위(계약승인+정산활성), 상태 문구, 미승인 승인 진입, 매출 링크',
    files: ['app/sales/page.tsx', 'services/manualSalesService.ts', 'hooks/useDashboardData.ts'] },
  { page_id: 'AD_SALES_DT', name: '가맹점 매출 상세', focus: '카드/배달 매출 원천, 실제 이체액 구성 분해, 차액정산·현장결제 회수, 예상/확정 상태, 수기·엑셀 매출, 수수료 툴팁',
    files: ['app/sales/[bizNo]/page.tsx', 'hooks/usePurchaseLedger.ts', 'components/sales/ExcelUploadModal.tsx', 'components/sales/ManualSalesModal.tsx', 'services/manualSalesService.ts'] },
  { page_id: 'AD_MERCHANT', name: '가맹점 관리(목록)', focus: '가맹점 목록·상태 필터·검색·정렬 우선순위, 계약 진척도, 예상정산 배너, 부채 가맹점 등록, 담당자 변경',
    files: ['app/manage/page.tsx', 'services/merchantService.ts', 'types/merchant.ts'] },
  { page_id: 'AD_PRODUCT', name: '정산 상품관리', focus: '정산 상품(정책=일반/다우) 목록·생성·수정·비활성·삭제, 참여자·요율(%/원)·납부/수취 옵션, VAT 별도/포함',
    files: ['app/settlement/policies/page.tsx', 'app/settlement/policies/PolicyFormModal.tsx', 'types/settlement.ts', 'lib/settlementLabels.ts'] },
  { page_id: 'AD_SETTLE', name: '선정산 결과', focus: '정산현황 선정산 결과 탭 — 요약 6카드, 차액 배너, 날짜별 결과 테이블, 가맹점 상세 펼침, 엑셀 4시트, 예상지급',
    files: ['app/settlement/overview/page.tsx', 'app/settlement/overview/PreSettlementTab.tsx', 'hooks/useSettlementOverview.ts', 'services/settlementService.ts'] },
  { page_id: 'AD_SETTLE_PREVIEW', name: '바로이체 미리보기/예상 지급', focus: '주말·스크래핑 장애 시 평균매출 기반 예상 지급(순지급×할인율), 예상/확정 구분, 대상 사유(WEEKEND/장애)',
    files: ['app/settlement/overview/PreSettlementTab.tsx', 'hooks/useSettlementOverview.ts', 'services/settlementService.ts'] },
  { page_id: 'AD_SETTLE_TRANSFER', name: '이체 내역', focus: '이체 KPI·날짜별 목록, 쿠콘 회수 2단계 페어(락계좌→모계좌 스윕), 개별 배분 이체 완료 처리, 수동이체',
    files: ['app/settlement/overview/TransferRecordsTab.tsx', 'app/settlement/overview/page.tsx', 'services/batchService.ts', 'services/settlementService.ts'] },
  { page_id: 'AD_SETTLE_BILL', name: '계산서 발행', focus: '세금/면세계산서 발행 자료, 이해관계자별 합산, 발행 대상 가맹점(승인+사업자번호), 기간 조건',
    files: ['app/settlement/overview/TaxInvoiceTab.tsx', 'app/settlement/overview/page.tsx', 'services/settlementService.ts', 'lib/settlementLabels.ts'] },
  { page_id: 'AD_SETTLE_VOC', name: 'VOC 대응', focus: '가맹점 문의 대응용 정산 상세 엑셀, 데이터 유무 체크, 대상 가맹점·기간 조건',
    files: ['app/settlement/overview/VocExportTab.tsx', 'app/settlement/overview/page.tsx', 'services/settlementService.ts'] },
  { page_id: 'AD_SETTLE_MISSED', name: '미정산 누락 추적', focus: '누락 추적·바로이체/이미지급 처리, 미정산 사유, 정산 재실행',
    files: ['app/settlement/overview/PreSettlementTab.tsx', 'hooks/useSettlementOverview.ts', 'services/settlementService.ts'] },
  { page_id: 'AD_SETTLE_DIFF', name: '차액 정산', focus: '예상↔확정 수수료 차액 정산 대시보드(환급/추가차감), 대기·예정·누적, 매출/차액 이력 연결',
    files: ['app/settlement/overview/page.tsx', 'hooks/useSettlementOverview.ts', 'components/FeeAdjustmentSummary.tsx', 'services/settlementService.ts'] },
  { page_id: 'AD_SCRAPING', name: '스크래핑 장애 이력', focus: '플랫폼(여신협회·배민·요기요·쿠팡) 스크래핑 장애 이력·검증 상태(정상·이상·장애·스킵·검증제외), 쿠콘 검증, 장애 시 이전 검증시각 기준',
    files: ['app/scraping-incidents/page.tsx', 'services/cooconService.ts', 'lib/platformSettlementConstants.ts'] },
]

const CONTENT_SCHEMA = {
  type: 'object', additionalProperties: false, required: ['page_id', 'summary', 'sections'],
  properties: {
    page_id: { type: 'string' },
    summary: { type: 'string', description: '이 화면이 정책적으로 무엇인지 1-2문장, 기획자 언어' },
    sections: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false, required: ['heading', 'tag', 'rows'],
        properties: {
          heading: { type: 'string' },
          tag: { type: 'string', enum: ['설정', '연결', '계산', '데이터', '정책'] },
          rows: {
            type: 'array',
            items: {
              type: 'object', additionalProperties: false, required: ['k', 'v', 'status'],
              properties: {
                k: { type: 'string' },
                v: { type: 'string', description: '기획자 언어. <b>강조</b>, 줄바꿈 \\n, 하위설명 "– ". 개발용어(함수/route/DB/상태상수/쿼리) 금지.' },
                status: { type: 'string', enum: ['확정', '가설', '확인필요'] },
              },
            },
          },
        },
      },
    },
    citations: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['claim', 'ref'], properties: { claim: { type: 'string' }, ref: { type: 'string' } } } },
  },
}

function extractPrompt(s) {
  return `너는 PayHug 선정산 서비스의 서비스기획 검토자다. 어드민 화면 "${s.name}"(page_id=${s.page_id})의 화면설계서에 넣을 **심화 내용**을 프론트 코드에서 뽑는다.

초점: ${s.focus}

[정독할 파일]
${s.files.map(f => `${ROOT}/${f}`).join('\n')}
기존 화면설계서(UI 워크스루 이미 있음, 중복 금지): ${DESIGN}/${s.page_id}.html

[임무] 스크린샷만으론 알 수 없는, 기획자가 알아야 할 **로직·정책·설정·연결·데이터 출처**를 코드에서 캐낸다. 해당하는 만큼: 어떤 설정/어디에 연결/어떻게 계산(선정산 수수료 3종→원장→배분→지급액)/어디서 뭘 언제 가져오나(스크래핑·동기화·배치·예상값).

[규칙 엄수]
1. 기획자 언어. 함수·변수·route(/admin/..)·DB·상태상수(ACTIVE 등)·"쿼리" 등 개발용어 금지. 내부 라벨상수(MARGIN/SYSTEM_FEE 등)도 한글로.
2. 6대 개념(미지급금·선정산 제외금액·바로이체·과지급·미회수금·환급) 분리. 어드민 '매출 회수'(락계좌→모계좌 스윕)와 정책 '회수'(과지급)는 다름.
3. 각 항목 확정/가설/확인필요. 서버 전용(최종 산술·스크래핑 스케줄·확정 수수료율C1·지급캘린더C2·예상차액C4)은 확인필요.
4. 사람이 쓴 것처럼. 단락·<b>·"– " 활용. 부호(양/음)·지급완료 여부로 갈리는 지점 명시.
5. citations에 file:line 근거.

sections는 heading별(예 계산로직/설정·연결/데이터출처/정책·주의). 반환은 SCHEMA(JSON)만.`
}

function verifyPrompt(s, draft) {
  return `너는 서비스기획 검토자이자 적대적 완결성 비평가다. 화면 "${s.name}"(${s.page_id}) 심화 초안을 코드와 대조해 최종본으로 만든다.

[초안]
${draft}

[원본 코드 — 다시 읽어 대조]
${s.files.map(f => `${ROOT}/${f}`).join('\n')}

[검증] 1.사실검증(틀리면 코드에 맞게 수정/확인필요로) 2.누락보완(빠진 로직·설정·연결·데이터, 특히 계산 순서·예외분기·데이터 시각 구분) 3.정직성(개발용어·내부상수 제거, 서버 전용값이 확정이면 확인필요로).
[출력] 초안과 동일 SCHEMA로 완성본 전체. 개발용어 0. JSON만.`
}

phase('Extract')
const results = await pipeline(
  SCREENS,
  (s) => agent(extractPrompt(s), { label: `ext:${s.page_id}`, phase: 'Extract', schema: CONTENT_SCHEMA, effort: 'high' }),
  (draft, s) => { if (!draft) return null; return agent(verifyPrompt(s, JSON.stringify(draft)), { label: `ver:${s.page_id}`, phase: 'Verify', schema: CONTENT_SCHEMA, effort: 'high' }) },
)
const final = results.filter(Boolean)
log(`Wave1 심화 완료 ${final.length}/${SCREENS.length}`)
return { screens: final }
