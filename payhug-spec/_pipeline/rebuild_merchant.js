// 베이스 design/AD_MERCHANT_DT.html 의 마커(6→15)·키노트(6→15행)를 전체높이 캡처 기준으로 교체.
const fs = require('fs')
const BASE = '/Users/semi/cursor/payhug/payhug-spec/spec/design/AD_MERCHANT_DT.html'
const MC = require('./mc_markers.json')

let html = fs.readFileSync(BASE, 'utf8')

// 1) 마커 블록 재생성 (L: dim 12/mk 11.2, R: dim 70.3/mk 69.6)
const mkHtml = MC.markers.map(m => {
  const dl = m.col === 'R' ? 70.3 : 12
  const ml = m.col === 'R' ? 69.6 : 11.2
  return `        <div class="dim" style="left:${dl}%;top:${m.dim_top}%;height:${m.dim_h}%"></div>\n        <div class="mk" style="left:${ml}%;top:${m.mk_top}%">${m.no}</div>`
}).join('\n')

// img 태그 다음부터 mock 닫힘(</div>) 전까지 = 기존 마커들 → 교체
html = html.replace(
  /(<img src="\.\.\/captures\/1033_2\.png"[^>]*>\n)([\s\S]*?)(\n\s*<\/div>\n\s*<\/div>\n\s*<div class="right">)/,
  (_, img, _old, tail) => img + mkHtml + tail
)

// 2) 키노트 tbody 재생성 (15행) + C1/C2 red 플래그 되살림
const RED = {
  9: ' <span class="red">※ \'매일 오전 11:30 자동 실행\'은 화면 고정 문구 — 실제 지급 캘린더(D+N) 근거 미확정(C2).</span>',
  10: ' <span class="red">※ 표시 요율(표준 채권매입 1.0%·배달 0.604%·시스템 0.11% 등)은 서버 표시값 — 수수료율 근거 미확정(C1).</span>',
}
const rows = MC.keynote.map(k => {
  const note = (k.note || '') + (RED[k.no] || '')
  return `          <tr><td class="kn-no">${k.no}</td><td class="kn-nm">${k.name}</td><td class="kn-note">\n${note}\n          </td></tr>`
}).join('\n')

html = html.replace(/(<tbody>\n)([\s\S]*?)(\n\s*<\/tbody>)/, (_, a, _old, c) => a + rows + c)

// 3) Note 개발어 정리
html = html.replace('상세 기본. canEdit=관리자(ADMIN/PAYHUG)', '가맹점 종합 상세 · 관리자만 편집, 파트너 조회 전용')

// 4) 화면 성격 memo: 잘림 관련 오래된 red 문구 정리(개업일 포맷은 유지) — 데이터 라인만 최신화
html = html.replace(
  '<span class="b red">개업일 "2021.-0.5-" 깨짐 = 목업 openDate 포맷 오류 · 우측 정산 상품/"매일 11:30" 문구의 수수료율·지급일 근거 미확정(C1·C2)</span>',
  '<span class="b red">전체 높이 캡처 — 15개 섹션 전부 표시 · 수수료율·"매일 11:30" 지급일 근거 미확정(C1·C2), 개업일 "2021.-0.5-"는 목업 포맷 오류</span>'
)

fs.writeFileSync(BASE, html)
// 검증
const nMk = (html.match(/class="mk"/g) || []).length
const nRow = (html.match(/class="kn-no">/g) || []).length - 1 // thead 헤더 제외
console.log('마커', nMk, '· 키노트행', nRow, '· img', /captures\/1033_2/.test(html) ? 'ok' : 'MISSING')
