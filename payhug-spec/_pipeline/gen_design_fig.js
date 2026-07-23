// design_plus/*.html(자체완결 심화본) → design_fig/*.html(Figma 전송용, capture.js 재주입).
// design_fig는 gitignore(재생성 파생물). Figma 재임포트 전 이 스크립트로 생성.
// 사용: node gen_design_fig.js
const fs = require('fs'), path = require('path')
const SPEC = '/Users/semi/cursor/payhug/payhug-spec/spec'
const SRC = SPEC + '/design_plus', OUT = SPEC + '/design_fig'
const TAG = '<script src="https://mcp.figma.com/mcp/html-to-design/capture.js" async></script>'
if (!fs.existsSync(OUT)) fs.mkdirSync(OUT, { recursive: true })
let n = 0
for (const f of fs.readdirSync(SRC).filter(x => x.endsWith('.html'))) {
  let h = fs.readFileSync(path.join(SRC, f), 'utf8')
  if (!h.includes('html-to-design/capture.js')) h = h.replace(/<\/body>\s*<\/html>\s*$/i, TAG + '</body></html>')
  fs.writeFileSync(path.join(OUT, f), h); n++
}
console.log('design_fig 재생성:', n, '개 →', OUT)
