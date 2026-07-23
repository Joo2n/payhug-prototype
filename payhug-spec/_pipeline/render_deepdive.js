// 워크플로우 심화 결과(deepdive_content.json) + 기존 화면설계서 HTML → 심화 섹션이 붙은 자체완결 HTML.
// 캡처 이미지는 base64로 임베드하여 어디서든 렌더되게 함. capture.js(외부) 제거.
// 사용: node render_deepdive.js
const fs = require('fs')

const CONTENT = '/private/tmp/claude-501/-Users-semi-cursor-payhug/d08c4a93-21cd-4310-99c5-3c1fc6fa88f5/scratchpad/deepdive_content.json'
const DESIGN = '/Users/semi/cursor/payhug/payhug-spec/spec/design'
const OUTDIR = '/Users/semi/cursor/payhug/payhug-spec/spec/design_plus'
if (!fs.existsSync(OUTDIR)) fs.mkdirSync(OUTDIR, { recursive: true })

const TAGCLASS = { '설정': 'set', '연결': 'lnk', '계산': 'calc', '데이터': 'data', '정책': 'pol' }

function esc(s) { return String(s == null ? '' : s) } // v는 의도된 <b> 포함 → 이스케이프 안 함(에이전트 신뢰)

// v 렌더: \n 줄바꿈, "– "/"- " 로 시작하면 들여쓴 하위설명
function renderV(v) {
  const lines = String(v || '').split('\n')
  return lines.map(ln => {
    const t = ln.replace(/\s+$/, '')
    if (/^\s*[–-]\s+/.test(t)) return `<span class="di">${esc(t.replace(/^\s*[–-]\s+/, ''))}</span>`
    if (t === '') return ''
    return `<span class="dl">${esc(t)}</span>`
  }).join('')
}

function pill(status) {
  const cls = status === '확정' ? 'ok' : status === '가설' ? 'hy' : 'ck'
  return `<span class="pill pill-${cls}">${status}</span>`
}

function deepHtml(screen) {
  const secs = (screen.sections || []).map(sec => {
    const tc = TAGCLASS[sec.tag] || 'set'
    const rows = (sec.rows || []).map(r => `
        <div class="drow">
          <div class="dk">${esc(r.k)}</div>
          <div class="dv">${renderV(r.v)}${pill(r.status)}</div>
        </div>`).join('')
    return `
    <div class="dsec dsec-${tc}">
      <div class="dsec-h"><span class="dtag dtag-${tc}">${esc(sec.tag)}</span>${esc(sec.heading)}</div>
      <div class="dsec-body">${rows}
      </div>
    </div>`
  }).join('')

  const cites = (screen.citations || []).slice(0, 24).map(c =>
    `<span class="cite"><b>${esc(c.claim)}</b> · <code>${esc(c.ref)}</code></span>`).join('')

  return `
  <div class="deep">
    <div class="deep-band">정책 · 계산 로직 · 데이터 출처 <span class="dsub">코드 기반 심화 · 확정 / 가설 / 확인필요 표기</span></div>
    ${screen.summary ? `<div class="deep-sum">${esc(screen.summary)}</div>` : ''}
    <div class="deep-col">${secs}
    </div>
    ${cites ? `<div class="deep-cite"><div class="cite-h">코드 근거</div>${cites}</div>` : ''}
  </div>`
}

const DEEP_CSS = `
.deep{border-top:2px solid #222;background:#fbfbfd}
.deep-band{background:#4b47d6;color:#fff;padding:11px 30px;font-size:16px;font-weight:800;letter-spacing:-.3px}
.deep-band .dsub{font-size:12px;font-weight:600;opacity:.85;margin-left:10px}
.deep-sum{padding:14px 30px 4px;font-size:14px;color:#33343a;line-height:1.7}
.deep-col{padding:16px 30px 8px;display:flex;flex-direction:column;gap:14px}
.dsec{border:1px solid #e4e4ea;border-radius:10px;background:#fff;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.04)}
.dsec-h{display:flex;align-items:center;gap:9px;padding:11px 16px;font-size:15px;font-weight:800;color:#1a1f2b;border-bottom:1px solid #eee}
.dtag{font-size:11px;font-weight:800;color:#fff;border-radius:6px;padding:2px 8px}
.dsec-set .dsec-h{background:#f4f4fb}.dtag-set{background:#4b47d6}
.dsec-lnk .dsec-h{background:#eefaf7}.dtag-lnk{background:#0e9f8e}
.dsec-calc .dsec-h{background:#f6f0fd}.dtag-calc{background:#7c3aed}
.dsec-data .dsec-h{background:#eef6fd}.dtag-data{background:#2b7fd4}
.dsec-pol .dsec-h{background:#fdf3ee}.dtag-pol{background:#e0762a}
.dsec-body{padding:4px 0}
.drow{display:flex;gap:0;padding:11px 16px;border-bottom:1px solid #f2f2f5;align-items:flex-start}
.drow:last-child{border-bottom:none}
.dk{width:190px;flex-shrink:0;font-size:13.5px;font-weight:800;color:#3a3b42;padding-right:14px;line-height:1.55}
.dv{flex:1;font-size:13.5px;color:#2c2d33;line-height:1.72}
.dv b{color:#111;font-weight:800}
.dv .dl{display:block}
.dv .di{display:block;padding-left:15px;position:relative;color:#54555c}
.dv .di:before{content:"–";position:absolute;left:2px;color:#b0b2b8}
.pill{display:inline-block;margin-left:7px;font-size:10.5px;font-weight:800;border-radius:6px;padding:1px 7px;vertical-align:middle;white-space:nowrap}
.pill-ok{background:#e5f6ec;color:#1f9d55}
.pill-hy{background:#fdf3e0;color:#c07d15}
.pill-ck{background:#fde8e8;color:#d83a3a}
.deep-cite{padding:12px 30px 26px}
.cite-h{font-size:12px;font-weight:800;color:#8a8b92;margin-bottom:7px}
.deep-cite .cite{display:inline-block;font-size:11px;color:#55565c;background:#f1f1f4;border-radius:6px;padding:3px 9px;margin:0 6px 6px 0}
.deep-cite .cite b{color:#3a3b42;font-weight:700}
.deep-cite code{font-family:ui-monospace,Menlo,monospace;color:#7c3aed;font-size:10.5px}
`

function embedCapture(html) {
  // ../captures/XXX.png → data URI
  return html.replace(/src="(\.\.\/captures\/([0-9_]+\.png))"/g, (m, rel, fn) => {
    const p = DESIGN + '/../captures/' + fn
    try {
      const b64 = fs.readFileSync(p).toString('base64')
      return `src="data:image/png;base64,${b64}"`
    } catch { return m }
  })
}

const content = JSON.parse(fs.readFileSync(CONTENT, 'utf8'))
const byId = {}
for (const s of (content.screens || content)) byId[s.page_id] = s

let done = []
for (const pageId of Object.keys(byId)) {
  const src = DESIGN + '/' + pageId + '.html'
  if (!fs.existsSync(src)) { console.error('원본 없음:', pageId); continue }
  let html = fs.readFileSync(src, 'utf8')

  // 1) capture.js(외부 스크립트) 제거 → 자체완결
  html = html.replace(/<script src="https:\/\/mcp\.figma\.com[^"]*"[^>]*><\/script>/g, '')
  // 2) 캡처 base64 임베드
  html = embedCapture(html)
  // 3) 심화 CSS 주입
  html = html.replace('</style>', DEEP_CSS + '\n</style>')
  // 4) .frame 닫기 직전에 심화 섹션 삽입 (body 다음)
  const deep = deepHtml(byId[pageId])
  // 마지막 </div>\n</body> 앞의 frame close 를 찾아 삽입: 구조상 body div 다음 frame close.
  // '  </div>\n</div>\n</body>' 패턴(=body close, frame close) 사이에 삽입
  const idx = html.lastIndexOf('</div>\n</body>')
  if (idx === -1) { console.error('삽입점 못찾음:', pageId); continue }
  // frame close(</div>) 바로 앞에 deep 삽입
  html = html.slice(0, idx) + deep + '\n' + html.slice(idx)

  const out = OUTDIR + '/' + pageId + '.html'
  fs.writeFileSync(out, html)
  done.push(pageId)
}
console.log('심화 HTML 생성:', done.length, '→', OUTDIR)
console.log(done.join(', '))
