// ~/cursor/payhug-member-redesign/index.html → proto_fig/index.html (capture.js 주입본)
const fs = require('fs'), path = require('path')
const SRC = '/Users/semi/cursor/payhug-member-redesign/v2.html'
const OUT = '/Users/semi/cursor/payhug/payhug-spec/_pipeline/member_redesign/proto_fig'
const TAG = '<script src="https://mcp.figma.com/mcp/html-to-design/capture.js" async></script>'
if (!fs.existsSync(OUT)) fs.mkdirSync(OUT, { recursive: true })
let h = fs.readFileSync(SRC, 'utf8')
if (!h.includes('html-to-design/capture.js')) {
  if (/<\/body>/i.test(h)) h = h.replace(/<\/body>/i, TAG + '</body>')
  else h += TAG
}
fs.writeFileSync(path.join(OUT, 'index.html'), h)
console.log('proto_fig/index.html 생성 (' + Math.round(h.length/1024) + 'KB)')
