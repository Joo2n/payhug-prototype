// 생성 Workflow 산출(specs) + 매니페스트(메타바) → 파일럿 포맷 HTML 208장 조립.
// 사용: node assemble_run.js <gen_journal.jsonl 경로>
const fs = require('fs')
const { assemble } = require('./assemble_design.js')

const GENJOURNAL = process.argv[2]
if (!GENJOURNAL || !fs.existsSync(GENJOURNAL)) { console.error('gen journal 경로 필요'); process.exit(1) }
const MANIFEST = '/private/tmp/claude-501/-Users-semi-cursor-payhug/d08c4a93-21cd-4310-99c5-3c1fc6fa88f5/scratchpad/screen_manifest.json'
const OUTDIR = '/Users/semi/cursor/payhug/payhug-spec/spec/design'
if (!fs.existsSync(OUTDIR)) fs.mkdirSync(OUTDIR, { recursive: true })

const manifest = JSON.parse(fs.readFileSync(MANIFEST, 'utf8'))
const metaByNode = {}
for (const m of manifest) metaByNode[m.node] = m

// 개발용어 targeted 치환(누출 정정). 정상용어(쿼리=AI기능, "API 오류"=장애유형)는 건드리지 않음.
const SANI = [
  [/isAdmin\(ADMIN([·\/])PAYHUG\)/g, '관리자(ADMIN$1PAYHUG)'],
  [/canEdit\s*=\s*isAdmin/g, '수정 권한 = 관리자'],
  [/isAdmin\s*한정/g, '관리자 한정'],
  [/isAdmin·/g, '관리자·'],
  [/isAdmin/g, '관리자'],
  [/원본 순번·DB id 아님/g, '원본 순번 아님(내부 id 아님)'],
  [/DB 정보만 존재/g, '정보만 존재'],
  [/DB 저장 없이/g, '저장하지 않고'],
  [/DB 저장 없음/g, '저장하지 않음'],
  [/DB 미저장/g, '저장 안 함'],
  [/DB에서 동적/g, '서버에서 동적'],
  [/DB 동적 로드/g, '서버에서 동적 로드'],
  [/별도 API\(hours=24\)/g, '별도 경로(최근 24시간)'],
  [/transferAmount/g, '실제 이체액'],
  [/\bbizNo\b/g, '사업자번호'],
  [/\bdate를 URL/g, '날짜를 주소(URL)'],
  // merchant/공통 누출
  [/\b(POST|GET|PUT|PATCH|DELETE)\s+\/[^\s"<)]+/g, '서버에 요청'],
  [/\s*\(\/[A-Za-z][\w\/?=&%-]*\)/g, ''],            // (/route?x=y) 괄호 경로 제거
  [/\bflowStep\b[\s=]*[^\s;<.]*/g, ''],
  [/ACTIVE 연동/g, '연동 완료'],
  [/ACTIVE 계정/g, '연동된 계정'],
  [/ACTIVE·?/g, '활성'],
  [/\s\/[a-z][a-z0-9-]+(?:\/[a-z0-9?=&_-]+)+/gi, ''],   // 인라인 소문자 route 경로 제거([대문자PageID]는 보존)
  [/수정\(edit\)·재서명\(resign\)/g, '수정·재서명'],
  [/\(edit\)/g, ''], [/\(resign\)/g, ''], [/\(verify\)/g, ''],
  [/archive_02 §1\.1/g, '계약 약관 정책'],
  [/=archive_\d+[^\s;]*/g, ''],
]
function sani(s) { if (s == null) return s; let x = String(s); for (const [re, to] of SANI) x = x.replace(re, to); return x }

// 정밀 마커 오버라이드(node → markers): 있으면 그걸로 대체(정규화 생략, 이미 검증된 좌표).
const OVR = '/private/tmp/claude-501/-Users-semi-cursor-payhug/d08c4a93-21cd-4310-99c5-3c1fc6fa88f5/scratchpad/marker_overrides.json'
let overrides = {}
try { overrides = JSON.parse(fs.readFileSync(OVR, 'utf8')) } catch {}

// 마커 정규화: 번호 원(mk)이 자기 영역선(dim)에서 너무 바깥으로 뜬 것을 → 라인에 붙여 안쪽으로.
// 규칙: mk 바로 앞의 dim을 짝으로 보고, mk가 그 라인 근처(열)일 때만 left를 라인 위(dl)로 스냅. 세로(top)·우측 포인트마커는 유지.
function num(s) { const v = parseFloat(String(s == null ? '' : s)); return isNaN(v) ? null : v }
function normalizeMarkers(markers) {
  if (!Array.isArray(markers)) return markers
  let lastDim = null
  return markers.map(m => {
    if (m.kind === 'dim') { lastDim = m; return m }
    if (m.kind === 'mk' && lastDim) {
      const ml = num(m.left), dl = num(lastDim.left)
      // 같은 왼쪽 열(라인 기준 -6% ~ +3%)에 있는 원만 스냅 = 우측 포인트마커(hover 등)는 제외
      if (ml != null && dl != null && ml >= dl - 6 && ml <= dl + 3) {
        return { ...m, left: dl + '%' } // 라인 위로(콘텐츠 경계). 세로 유지
      }
    }
    return m
  })
}

// gen journal: 각 result 라인의 result.screens 안에 {node,page_id,memo,rows,markers}
const specByNode = {}
for (const l of fs.readFileSync(GENJOURNAL, 'utf8').trim().split('\n')) {
  let o; try { o = JSON.parse(l) } catch { continue }
  if (o.type !== 'result') continue
  const sc = (o.result && o.result.screens) || (o.value && o.value.screens) || []
  for (const s of sc) if (s && s.node) specByNode[s.node] = s // 후행(verify) 결과가 덮어씀 = 최종본
}

let ok = 0, miss = []
for (const m of manifest) {
  const spec = specByNode[m.node]
  if (!spec) { miss.push(m.node + '/' + m.page_id); continue }
  const full = {
    page: m.page_name, page_id: m.page_id, system: m.system, date: '2026.07.21',
    writer: '이서준', flow: m.flow, note: m.note || '-',
    capture: '../' + m.capture, // spec/design/*.html 기준 상대경로
    alt: m.page_name,
    note: sani(m.note || '-'),
    memo: (spec.memo || []).map(x => ({ html: sani(x.html || x) })),
    rows: (spec.rows || []).map(r => ({ no: r.no, name: r.name, note_html: sani(r.note_html) })),
    markers: overrides[m.node] ? overrides[m.node] : normalizeMarkers(spec.markers || []),
  }
  fs.writeFileSync(OUTDIR + '/' + m.page_id + '.html', assemble(full))
  ok++
}
console.log('조립 완료:', ok, '/', manifest.length, 'HTML →', OUTDIR)
if (miss.length) console.log('스펙 누락(재생성 필요):', miss.length, miss.slice(0, 40).join(', '))
