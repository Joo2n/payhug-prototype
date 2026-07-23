export const meta = {
  name: 'payhug-figma-import',
  description: 'PayHug 화면설계서 HTML을 헤드리스 캡처로 Figma(303:173 파일)에 임포트',
  phases: [{ title: 'Import', detail: '화면별: captureId 발급→헤드리스 캡처→폴링→node id' }],
}

const MANIFEST = '/private/tmp/claude-501/-Users-semi-cursor-payhug/d08c4a93-21cd-4310-99c5-3c1fc6fa88f5/scratchpad/screen_manifest.json'
const FIGCAP = '/private/tmp/claude-501/-Users-semi-cursor-payhug/d08c4a93-21cd-4310-99c5-3c1fc6fa88f5/scratchpad/figcap.sh'
const FILEKEY = 'Tcf69tIciGxmlqCIuRb0iI'
const NODEID = '303:173'

// 필터: 특정 메뉴 접두만(테스트). 빈 문자열이면 전체.
const ONLY_MENU_PREFIX = ''
// ONLY_PAGES 지정 시 그 page_id만(누락 재임포트). 비어있으면 무시.
const ONLY_PAGES = ["AD_MERCHANT_DT","AD_PARTNER_DELETE","AD_PARTNER_PROFILE","AD_SETTLE_BILL","AD_SETTLE_DETAIL","AD_SETTLE_MISSED","AD_SETTLE_VOC","AD_SALES","AD_SIM","AD_TERMS","AD_TERMS_SIGNUP","AD_LOG","AD_AI","AD_AI_ANSWER","AD_SCRAPING"]
// 이미 임포트되어 건너뛸 page_id
const SKIP = []

const BOOT_SCHEMA = {
  type: 'object', additionalProperties: false, required: ['screens'],
  properties: {
    screens: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['page_id', 'menu'],
      properties: { page_id: { type: 'string' }, menu: { type: 'string' } } } },
  },
}

const IMP_SCHEMA = {
  type: 'object', additionalProperties: false, required: ['page_id', 'ok'],
  properties: {
    page_id: { type: 'string' },
    ok: { type: 'boolean' },
    node_id: { type: 'string', description: '성공 시 Figma node-id(예 1143:2). 실패면 빈문자' },
    note: { type: 'string' },
  },
}

function impPrompt(pageId) {
  return `너는 화면설계서 1장을 Figma로 임포트한다. page_id="${pageId}".

로컬 서버(http://localhost:8899)가 이미 화면설계서를 서빙 중이고, HTML엔 capture.js가 심어져 있다.

[절차 — 순서대로]
1. Figma 도구 로드: ToolSearch로 "select:mcp__figma__generate_figma_design" 실행.
2. captureId 발급: mcp__figma__generate_figma_design 를 fileKey="${FILEKEY}", nodeId="${NODEID}" 로 호출(captureId 없이). 응답의 "Capture ID generated: \`...\`" 에서 captureId를 추출.
3. 헤드리스 캡처 실행: Bash로 \`bash ${FIGCAP} ${pageId} <captureId>\` 실행(약 16초 소요, 이 안에서 페이지 로드→전송).
4. 폴링: mcp__figma__generate_figma_design 를 fileKey="${FILEKEY}", captureId="<captureId>" 로 호출. 응답에 "added to your existing file" 과 "node-id=NNNN-N" 가 나오면 성공 → node-id를 콜론형(1143:2)으로 변환해 기록. 아직 pending/processing 이면 Bash로 \`sleep 5\` 대신 5초 대기 후 다시 호출(최대 8회). 8회까지 안되면 실패.
5. 결과 반환: {page_id:"${pageId}", ok:true/false, node_id:"...", note:"..."}.

주의: captureId는 1회용. 절대 재사용/재폴링용 새 발급 금지(폴링은 같은 captureId로). Bash sleep는 짧게(5초) 반복 허용.
반환은 SCHEMA(JSON)만.`
}

phase('Import')

const boot = await agent(
  `Read JSON ${MANIFEST} (array). Return {screens:[{page_id, menu}]} for every element.`,
  { label: 'boot:list', phase: 'Import', schema: BOOT_SCHEMA, effort: 'low' })

let list = (boot && boot.screens) || []
if (ONLY_PAGES.length) list = list.filter(s => ONLY_PAGES.includes(s.page_id))
else if (ONLY_MENU_PREFIX) list = list.filter(s => String(s.menu).startsWith(ONLY_MENU_PREFIX))
list = list.filter(s => !SKIP.includes(s.page_id))
log(`Figma 임포트 대상: ${list.length} (${ONLY_PAGES.length ? 'ONLY_PAGES' : (ONLY_MENU_PREFIX || 'ALL')})`)

const results = await parallel(list.map(s => () =>
  agent(impPrompt(s.page_id), { label: `fig:${s.page_id}`, phase: 'Import', schema: IMP_SCHEMA, effort: 'medium' })))

const done = results.filter(r => r && r.ok)
const fail = results.filter(r => !r || !r.ok)
log(`임포트 완료: ${done.length}/${list.length} · 실패 ${fail.length}`)
return { imported: done, failed: fail.map(f => f && f.page_id), map: done.reduce((a, r) => (a[r.page_id] = r.node_id, a), {}) }
