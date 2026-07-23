// PayHug 화면설계서 HTML 조립기 — _pilot_매출조회.html 구조를 그대로 재현.
// 입력: 화면 스펙 객체(메타 + memo + rows + markers). 출력: 완성 HTML 문자열.
// 에이전트는 memo/rows의 note에 아래 허용 클래스만 쓴다:
//   .grp(소제목 볼드) .i(–들여쓰기 불릿) .b(블록줄) <b>(핵심 볼드) .red(빨강 이슈) .sb(서브번호 알약) <br>
// 마커: mk(원, label 숫자/서브), sub(작은 알약), dim(영역선). 좌표는 % 문자열 or 숫자(%).

const STYLE = `*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Apple SD Gothic Neo','Malgun Gothic',sans-serif;color:#222}
.frame{position:relative;width:1920px;min-height:1280px;background:#fff;border:1px solid #222}
.meta{display:flex;border-bottom:1px solid #222}
.metabar{flex:1}
.mrow{display:flex;border-bottom:1px solid #cfcfd4;height:46px}
.mrow:last-child{border-bottom:none}
.lbl{background:#E5E5EA;border-right:1px solid #cfcfd4;display:flex;align-items:center;padding:0 14px;font-size:14px;font-weight:700;white-space:nowrap}
.val{border-right:1px solid #cfcfd4;display:flex;align-items:center;padding:0 14px;font-size:14px}
.logo{width:150px;display:flex;align-items:center;justify-content:center;border-left:1px solid #222;font-weight:800;font-size:22px;letter-spacing:-.5px}
.logo b{color:#111}.logo i{color:#2ac06d;font-style:normal}
.body{display:flex;min-height:calc(1280px - 93px)}
.left{width:1360px;border-right:1px solid #222;padding:26px 30px;position:relative}
.mock{position:relative;width:1250px;margin:0 auto}
.mock.mob{width:440px}
.mock img{width:100%;display:block;border:1px solid #ececf0;border-radius:6px;box-shadow:0 1px 4px rgba(0,0,0,.06)}
.mock.mob img{border-radius:16px}
.mk{position:absolute;width:17px;height:17px;border-radius:50%;background:#4b47d6;color:#fff;font-size:10.5px;font-weight:800;display:flex;align-items:center;justify-content:center;box-shadow:0 1px 2px rgba(0,0,0,.22);z-index:7;transform:translate(-50%,-50%)}
.sub{position:absolute;height:16px;padding:0 5px;border-radius:8px;background:#4b47d6;color:#fff;font-size:9.5px;font-weight:800;display:flex;align-items:center;justify-content:center;z-index:6;transform:translate(-50%,-50%);white-space:nowrap;box-shadow:0 1px 2px rgba(0,0,0,.2)}
.dim{position:absolute;width:0;border-left:1.5px solid #7b6cf0;z-index:4}
.dim::before,.dim::after{content:"";position:absolute;left:-4px;width:9px;border-top:1.5px solid #7b6cf0}
.dim::before{top:0}.dim::after{bottom:-1.5px}
.right{width:560px;overflow:visible}
.kn-h{background:#E5E5EA;padding:9px 16px;font-size:14px;font-weight:700;border-bottom:1px solid #cfcfd4}
.kn-memo{padding:10px 16px;font-size:13px;color:#333;border-bottom:1px solid #eee;line-height:1.8}
.kn-memo .g{color:#3538cd;font-weight:800}
.kn-memo b{color:#1a1f2b;font-weight:700}
.kn-memo .b{display:block}.kn-memo .i{display:block;padding-left:14px;color:#5C5D62}
.kn-memo .red{color:#FF383C}
.kn-tbl{width:100%;border-collapse:collapse;font-size:13px}
.kn-tbl th{background:#f4f4f6;text-align:left;padding:7px 10px;font-weight:700;font-size:12px;border-bottom:1px solid #d7d7dc}
.kn-tbl td{padding:11px 10px 13px;vertical-align:top;border-bottom:1px solid #eef0f2}
.kn-no{width:28px;font-weight:800;color:#4b47d6}
.kn-nm{width:78px;font-weight:700;color:#1a1f2b}
.kn-note{line-height:1.85}
.kn-note b{font-weight:700;color:#1a1f2b}
.kn-note .b{display:block;margin-top:1px}
.kn-note .i{display:block;padding-left:16px;color:#55565b;position:relative}
.kn-note .i:before{content:"–";position:absolute;left:4px;color:#b0b2b8}
.kn-note .red{color:#FF383C}
.kn-note .sb{color:#fff;background:#4b47d6;border-radius:8px;padding:0 6px;font-size:10.5px;font-weight:800;margin-right:3px}
.kn-note .grp{display:block;margin-top:9px;font-weight:700;color:#1a1f2b}`

function pct(v) { return typeof v === 'number' ? v + '%' : String(v) }

// spec: {
//   page, page_id, system, date, writer, flow, note, capture, alt,
//   memo: [ {html} ]  // kn-memo 안에 들어갈 줄들(html 문자열, 허용 클래스)
//   rows: [ {no, name, note_html} ]
//   markers: [ {kind:'dim'|'mk'|'sub', label?, left, top, height?} ]
// }
function assemble(spec) {
  const meta1 = `
      <div class="mrow">
        <div class="lbl" style="width:64px">Page</div><div class="val" style="width:260px">${esc(spec.page)}</div>
        <div class="lbl" style="width:74px">Page ID</div><div class="val" style="width:150px">${esc(spec.page_id)}</div>
        <div class="lbl" style="width:70px">System</div><div class="val" style="width:96px">${esc(spec.system || 'pc')}</div>
        <div class="lbl" style="width:52px">Date</div><div class="val" style="width:110px">${esc(spec.date || '2026.07.21')}</div>
        <div class="lbl" style="width:62px">Writer</div><div class="val" style="flex:1">${esc(spec.writer || '이서준')}</div>
      </div>
      <div class="mrow">
        <div class="lbl" style="width:64px">Flow</div><div class="val" style="width:544px">${esc(spec.flow)}</div>
        <div class="lbl" style="width:52px">Note</div><div class="val" style="flex:1">${esc(spec.note || '-')}</div>
      </div>`

  const markers = (spec.markers || []).map(m => {
    if (m.kind === 'dim') return `        <div class="dim" style="left:${pct(m.left)};top:${pct(m.top)};height:${pct(m.height)}"></div>`
    if (m.kind === 'sub') return `        <div class="sub" style="left:${pct(m.left)};top:${pct(m.top)}">${esc(m.label)}</div>`
    return `        <div class="mk" style="left:${pct(m.left)};top:${pct(m.top)}">${esc(m.label)}</div>`
  }).join('\n')

  const memo = (spec.memo && spec.memo.length)
    ? `      <div class="kn-memo">\n${spec.memo.map(x => '        ' + (x.html || x)).join('\n')}\n      </div>\n`
    : ''

  const rows = (spec.rows || []).map(r => `          <tr><td class="kn-no">${esc(r.no)}</td><td class="kn-nm">${r.name}</td><td class="kn-note">
${r.note_html}
          </td></tr>`).join('\n')

  const isMobile = /mobile/i.test(String(spec.system || ''))
  return `<!doctype html><html lang="ko"><head><meta charset="utf-8">
<style>
${STYLE}
</style><script src="https://mcp.figma.com/mcp/html-to-design/capture.js" async></script></head><body>
<div class="frame">
  <div class="meta">
    <div class="metabar">${meta1}
    </div>
    <div class="logo"><b>Pay</b><i>hug</i></div>
  </div>
  <div class="body">
    <div class="left">
      <div class="mock${isMobile ? ' mob' : ''}">
        <img src="${esc(spec.capture)}" alt="${esc(spec.alt || spec.page)}">
${markers}
      </div>
    </div>
    <div class="right">
      <div class="kn-h">key note</div>
${memo}      <table class="kn-tbl">
        <thead><tr><th class="kn-no">No</th><th class="kn-nm">이름</th><th>설명</th></tr></thead>
        <tbody>
${rows}
        </tbody>
      </table>
    </div>
  </div>
</div>
</body></html>`
}

function esc(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

module.exports = { assemble }
