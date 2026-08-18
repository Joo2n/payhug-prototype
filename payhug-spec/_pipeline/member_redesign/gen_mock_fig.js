// mockups/*.html → mockups_fig/*.html (capture.js 주입본, Figma 전송용)
const fs = require('fs'), path = require('path')
const BASE = '/Users/semi/cursor/payhug/payhug-spec/_pipeline/member_redesign'
const SRC = BASE + '/mockups', OUT = BASE + '/mockups_fig'
const TAG = '<script src="https://mcp.figma.com/mcp/html-to-design/capture.js" async></script>'
if (!fs.existsSync(OUT)) fs.mkdirSync(OUT, { recursive: true })
let n = 0
for (const f of fs.readdirSync(SRC).filter(x => x.endsWith('.html'))) {
  let h = fs.readFileSync(path.join(SRC, f), 'utf8')
  if (!h.includes('html-to-design/capture.js')) {
    if (/<\/body>/i.test(h)) h = h.replace(/<\/body>/i, TAG + '</body>')
    else h += TAG
  }
  fs.writeFileSync(path.join(OUT, f), h); n++
}
console.log('mockups_fig 생성:', n, '개')
