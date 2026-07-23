export const meta = {
  name: 'payhug-figma-retry',
  description: 'Figma 임포트 실패분 재시도 — 동시 3개·captureId 한도초과 자동 재발급·폴링 24회',
  phases: [{ title: 'Retry', detail: '청크(3)로 순차, 한도 회피' }],
}

const FIGCAP = '/Users/semi/cursor/payhug/payhug-spec/_pipeline/figcap.sh'
const FILEKEY = 'Tcf69tIciGxmlqCIuRb0iI'
const NODEID = '303:173'
const CHUNK = 3

const IMP_SCHEMA = {
  type: 'object', additionalProperties: false, required: ['page_id', 'ok'],
  properties: {
    page_id: { type: 'string' }, ok: { type: 'boolean' },
    node_id: { type: 'string' }, note: { type: 'string' },
  },
}

function impPrompt(pageId) {
  return `너는 화면설계서(심화본) 1장을 Figma로 임포트한다. page_id="${pageId}". 이 페이지는 길다(최대 6500px) — 변환에 오래 걸린다.
로컬 서버 http://localhost:8899 가 심화본을 서빙 중이고 HTML엔 capture.js가 있다.

[절차]
1. 도구 로드: ToolSearch "select:mcp__figma__generate_figma_design".
2. captureId 발급: mcp__figma__generate_figma_design(fileKey="${FILEKEY}", nodeId="${NODEID}"). 응답의 "Capture ID generated: \`...\`" 에서 captureId 추출.
   ★한도 초과("rate limit"/"한도")로 실패하면: Bash \`S=$SECONDS; until [ $((SECONDS-S)) -ge 25 ]; do sleep 1; done; echo wait\` 로 25초 대기 후 재발급. 최대 4회 재시도.
3. 헤드리스 캡처: Bash \`bash ${FIGCAP} ${pageId} <captureId>\` (약 16초). "Killed: 9" 후 "captured ..."면 정상.
4. 폴링(최대 24회): mcp__figma__generate_figma_design(fileKey="${FILEKEY}", captureId="<captureId>"). "added to your existing file"+"node-id=NNNN-N"면 성공→콜론형(1591:2) 기록. pending/processing이면 Bash \`S=$SECONDS; until [ $((SECONDS-S)) -ge 5 ]; do sleep 1; done; echo wait\` 로 5초 대기 후 재호출.
   ★폴링 중 "rate limit"/"한도" 응답이면 위 방식으로 15초 대기 후 같은 captureId로 재호출(재발급 금지).
5. 반환: {page_id:"${pageId}", ok:true/false, node_idःconverted, note}. captureId 재사용/폴링용 재발급 금지. JSON만.`
}

phase('Retry')
let list = args
if (typeof list === 'string') { try { list = JSON.parse(list) } catch (e) { list = [] } }
if (!Array.isArray(list)) list = []
log(`재시도 대상: ${list.length} · 청크 ${CHUNK}`)

function chunks(a, n) { const o = []; for (let i = 0; i < a.length; i += n) o.push(a.slice(i, i + n)); return o }
const groups = chunks(list, CHUNK)
const all = []
for (let ci = 0; ci < groups.length; ci++) {
  const res = await parallel(groups[ci].map(pid => () =>
    agent(impPrompt(pid), { label: `re:${pid}`, phase: 'Retry', schema: IMP_SCHEMA, effort: 'low' })))
  all.push(...res)
  const okc = all.filter(r => r && r.ok && r.node_id).length
  log(`청크 ${ci + 1}/${groups.length} · 누적 성공 ${okc}/${all.length}`)
}

const done = all.filter(r => r && r.ok && r.node_id)
const fail = all.filter(r => !r || !r.ok || !r.node_id)
log(`재시도 완료: 성공 ${done.length} · 실패 ${fail.length}`)
return {
  imported: done.map(r => ({ page_id: r.page_id, node_id: r.node_id })),
  failed: fail.map(f => (f && f.page_id) || '?'),
  map: done.reduce((a, r) => (a[r.page_id] = r.node_id, a), {}),
}
