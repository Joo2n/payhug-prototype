export const meta = {
  name: 'payhug-figma-import-deep',
  description: '심화본(design_fig) 화면설계서 HTML을 헤드리스 캡처로 Figma(303:173)에 임포트',
  phases: [{ title: 'Import', detail: '화면별: captureId 발급→헤드리스 캡처→폴링→node id' }],
}

const FIGCAP = '/Users/semi/cursor/payhug/payhug-spec/_pipeline/figcap.sh'
const FILEKEY = 'Tcf69tIciGxmlqCIuRb0iI'
const NODEID = '303:173'

const IMP_SCHEMA = {
  type: 'object', additionalProperties: false, required: ['page_id', 'ok'],
  properties: {
    page_id: { type: 'string' },
    ok: { type: 'boolean' },
    node_id: { type: 'string', description: '성공 시 Figma node-id 콜론형(예 1584:2). 실패면 빈문자' },
    note: { type: 'string' },
  },
}

function impPrompt(pageId) {
  return `너는 화면설계서(심화본) 1장을 Figma로 임포트한다. page_id="${pageId}".
로컬 서버(http://localhost:8899)가 심화본을 서빙 중이고 HTML엔 capture.js가 심어져 있다. 이 심화 페이지는 길다(3000~6500px) — 변환에 시간이 더 걸릴 수 있으니 폴링을 넉넉히 하라.

[절차 — 순서대로]
1. Figma 도구 로드: ToolSearch로 "select:mcp__figma__generate_figma_design" 실행.
2. captureId 발급: mcp__figma__generate_figma_design 를 fileKey="${FILEKEY}", nodeId="${NODEID}" 로 호출(captureId 없이). 응답의 "Capture ID generated: \`...\`" 에서 captureId 추출.
3. 헤드리스 캡처: Bash로 \`bash ${FIGCAP} ${pageId} <captureId>\` 실행(약 16초, 이 안에서 로드→전송). "Killed: 9" 로그가 나와도 "captured ..." 가 출력되면 정상이다.
4. 폴링: mcp__figma__generate_figma_design 를 fileKey="${FILEKEY}", captureId="<captureId>" 로 호출. 응답에 "added to your existing file" 과 "node-id=NNNN-N" 가 나오면 성공 → node-id를 콜론형(1584:2)으로 변환해 기록. 아직 pending/processing 이면 아래 명령으로 5초 대기 후 다시 호출(최대 14회):
   Bash로 \`S=$SECONDS; until [ $((SECONDS-S)) -ge 5 ]; do sleep 1; done; echo wait\` 실행.
5. 결과 반환: {page_id:"${pageId}", ok:true/false, node_id:"...", note:"..."}.

주의: captureId는 1회용. 재발급/재사용 금지(폴링은 같은 captureId로). 14회까지 안되면 ok:false, note에 마지막 상태 기록.
반환은 SCHEMA(JSON)만.`
}

phase('Import')
let list = args
if (typeof list === 'string') { try { list = JSON.parse(list) } catch (e) { list = [] } }
if (!Array.isArray(list)) list = []
log(`Figma 심화 임포트 대상: ${list.length}`)

const results = await parallel(list.map(pid => () =>
  agent(impPrompt(pid), { label: `fig:${pid}`, phase: 'Import', schema: IMP_SCHEMA, effort: 'low' })))

const done = results.filter(r => r && r.ok && r.node_id)
const fail = results.filter(r => !r || !r.ok || !r.node_id)
log(`임포트 완료: ${done.length}/${list.length} · 실패 ${fail.length}`)
return {
  imported: done.map(r => ({ page_id: r.page_id, node_id: r.node_id })),
  failed: fail.map(f => (f && f.page_id) || '?'),
  map: done.reduce((a, r) => (a[r.page_id] = r.node_id, a), {}),
}
