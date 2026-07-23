export const meta = {
  name: 'payhug-deepdive-all',
  description: '남은 어드민 화면 전체(102) 심화 — 베이스 8=추출+검증 2패스, 변형 94=상태·모달 특수로직 1패스',
  phases: [{ title: 'Extract', detail: '화면별 코드 심층추출' }, { title: 'Verify', detail: '베이스만 검증' }],
}

const ROOT = '/Users/semi/cursor/payhug/01_payhug-admin-web-main'
const DESIGN = '/Users/semi/cursor/payhug/payhug-spec/spec/design'
const CFG = '/private/tmp/claude-501/-Users-semi-cursor-payhug/d08c4a93-21cd-4310-99c5-3c1fc6fa88f5/scratchpad/screens_all_config.json'

const CONTENT_SCHEMA = {
  type: 'object', additionalProperties: false, required: ['page_id', 'summary', 'sections'],
  properties: {
    page_id: { type: 'string' },
    summary: { type: 'string' },
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
              properties: { k: { type: 'string' }, v: { type: 'string' }, status: { type: 'string', enum: ['확정', '가설', '확인필요'] } },
            },
          },
        },
      },
    },
    citations: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['claim', 'ref'], properties: { claim: { type: 'string' }, ref: { type: 'string' } } } },
  },
}

const BOOT_SCHEMA = {
  type: 'object', additionalProperties: false, required: ['screens'],
  properties: { screens: { type: 'array', items: {
    type: 'object', additionalProperties: false, required: ['page_id', 'name', 'kind', 'files'],
    properties: { page_id: { type: 'string' }, name: { type: 'string' }, menu: { type: 'string' }, kind: { type: 'string' }, note: { type: 'string' }, files: { type: 'array', items: { type: 'string' } } } } } },
}

const RULES = `[규칙 엄수]
1. 기획자 언어. 함수·변수·route(/admin/..)·DB·상태상수(ACTIVE 등)·"쿼리"·내부라벨상수(MARGIN/SYSTEM_FEE 등) 개발용어 금지 — 전부 한글로.
2. 6대 개념(미지급금·선정산 제외금액·바로이체·과지급·미회수금·환급) 분리. 어드민 '매출 회수'(락계좌→모계좌 스윕)와 정책 '회수'(과지급)는 다름.
3. 각 항목 확정/가설/확인필요. 서버 전용(최종 산술·스크래핑 스케줄·확정 수수료율C1·지급캘린더C2·예상차액C4)은 확인필요.
4. 사람이 쓴 것처럼. v는 <b>강조·줄바꿈 \\n·하위설명 "– " 활용, 간결하게.
5. citations에 file:line 근거. tag는 설정/연결/계산/데이터/정책 중 하나.`

function extractPrompt(s) {
  const isVar = s.kind !== 'base'
  const files = (s.files || []).map(f => `${ROOT}/${f}`).join('\n')
  return `너는 PayHug 서비스기획 검토자다. 어드민 화면 "${s.name}"(page_id=${s.page_id}${s.note ? ', 성격: ' + s.note : ''})의 심화 내용을 코드에서 뽑는다.
${isVar ? `\n[중요] 이 화면은 상위 화면의 **세부 상태/모달/변형**이다. 베이스 화면의 일반 로직 반복은 피하고, **이 상태·모달에 특수한 것**(이 화면에서만의 입력 필드·조건 분기·경고 문구·처리 규칙·계산)에 집중하라. 특수 내용이 적으면 섹션을 적게(2~3개) 만들어도 된다.` : ''}
[정독할 파일]
${files}
기존 화면설계서(UI 워크스루 있음, 중복 금지): ${DESIGN}/${s.page_id}.html

스크린샷만으론 알 수 없는 로직·정책·설정·연결·데이터 출처를 캐낸다(설정/연결/계산/데이터/정책).
${RULES}
반환은 SCHEMA(JSON)만. page_id="${s.page_id}".`
}

function verifyPrompt(s, draft) {
  return `너는 서비스기획 검토자이자 적대적 완결성 비평가다. 화면 "${s.name}"(${s.page_id}) 심화 초안을 코드와 대조해 최종본으로 만든다.
[초안]
${draft}
[원본 코드]
${(s.files || []).map(f => `${ROOT}/${f}`).join('\n')}
[검증] 1.사실검증(틀리면 수정/확인필요로) 2.누락보완 3.개발용어·내부상수 제거, 서버전용값이 확정이면 확인필요로.
[출력] 초안과 동일 SCHEMA로 완성본. 개발용어 0. JSON만.`
}

phase('Extract')
const boot = await agent(`Read JSON array at ${CFG}. Return {screens:[{page_id,name,menu,kind,note,files}]} for every element, files preserved.`,
  { label: 'boot', phase: 'Extract', schema: BOOT_SCHEMA, effort: 'low' })
let SCREENS = (boot && boot.screens) || []
log(`전체 심화 대상: ${SCREENS.length} (base ${SCREENS.filter(s => s.kind === 'base').length} / variant ${SCREENS.filter(s => s.kind !== 'base').length})`)

const results = await pipeline(
  SCREENS,
  (s) => agent(extractPrompt(s), { label: `ext:${s.page_id}`, phase: 'Extract', schema: CONTENT_SCHEMA, effort: s.kind === 'base' ? 'high' : 'medium' }),
  (draft, s) => {
    if (!draft) return null
    if (s.kind === 'base') return agent(verifyPrompt(s, JSON.stringify(draft)), { label: `ver:${s.page_id}`, phase: 'Verify', schema: CONTENT_SCHEMA, effort: 'high' })
    return draft
  },
)
const final = results.filter(Boolean)
log(`전체 심화 완료 ${final.length}/${SCREENS.length}`)
return { screens: final }
