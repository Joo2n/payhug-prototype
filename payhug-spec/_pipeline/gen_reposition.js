// figma_map.json + screen_manifest.json → use_figma용 재배치 JS(reposition_code.js)
// 구조: 메뉴별 섹션(라벨 붙임) → 섹션 안에서 화면 패밀리(base+variant) 단위로 줄바꿈 → 좌→우 그리드.
const fs = require('fs')
const DIR = '/private/tmp/claude-501/-Users-semi-cursor-payhug/d08c4a93-21cd-4310-99c5-3c1fc6fa88f5/scratchpad'
const map = JSON.parse(fs.readFileSync(DIR + '/figma_map.json', 'utf8'))
const man = JSON.parse(fs.readFileSync(DIR + '/screen_manifest.json', 'utf8'))

function menuCode(m) { return (String(m).match(/^[AM]-\d+/) || [String(m)])[0] }

// 메뉴 순서(매니페스트 등장순 유지)
const menuOrder = []
for (const s of man) { const c = menuCode(s.menu); if (!menuOrder.includes(c)) menuOrder.push(c) }
const menuLabel = {}
for (const s of man) { const c = menuCode(s.menu); if (!menuLabel[c]) menuLabel[c] = s.menu }

// node_id 있는 화면만, 메뉴별로 수집
const byMenu = {}
for (const s of man) {
  if (!map[s.page_id]) continue
  const c = menuCode(s.menu)
  ;(byMenu[c] = byMenu[c] || []).push(s)
}

// 각 메뉴 안: 패밀리(base_id)별로 묶고, 패밀리 순서=패밀리 내 최소 node, 패밀리 내 base 먼저→variant(node순)
function nodeNum(s) { return parseInt(s.node) || 0 }
const ORDER = [] // [node_id, menuCode, page_id, famStart(0/1)]
for (const c of menuOrder) {
  const scr = byMenu[c] || []
  const fams = {}
  for (const s of scr) (fams[s.base_id] = fams[s.base_id] || []).push(s)
  const famIds = Object.keys(fams).sort((a, b) => Math.min(...fams[a].map(nodeNum)) - Math.min(...fams[b].map(nodeNum)))
  for (const fid of famIds) {
    const list = fams[fid].sort((a, b) => (a.kind === 'base' ? 0 : 1) - (b.kind === 'base' ? 0 : 1) || nodeNum(a) - nodeNum(b))
    list.forEach((s, i) => ORDER.push([map[s.page_id], c, s.page_id, i === 0 ? 1 : 0]))
  }
}

const LABELS = menuOrder.filter(c => byMenu[c]).map(c => [c, menuLabel[c]])

const code = `
const ORDER = ${JSON.stringify(ORDER)};
const LABELS = ${JSON.stringify(LABELS)};
const X0=-1281, Y0=6200, COLW=2060, COLS=8, ROWGAP=240, SECGAP=760, LABELDROP=300;
const page = figma.root.children.find(p=>p.id==="303:173");
await figma.setCurrentPageAsync(page);
await figma.loadFontAsync({family:"Inter",style:"Bold"});
for(const t of page.children.filter(n=>n.type==="TEXT" && Math.round(n.fontSize)===140)) t.remove();
const nodes=[]; for(const [id] of ORDER){ try{nodes.push(await figma.getNodeByIdAsync(id));}catch(e){nodes.push(null);} }
let y=Y0, col=0, rowMaxH=0, curMenu=null, placed=0, missing=0;
const labelY={};
for(let i=0;i<ORDER.length;i++){
  const [id,menu,pid,famStart]=ORDER[i];
  const n=nodes[i]; if(!n){missing++; continue;}
  if(menu!==curMenu){                                   // 새 메뉴 = 섹션
    if(curMenu!==null) y += rowMaxH + SECGAP;
    labelY[menu]=y; y += LABELDROP;                     // 라벨 자리 확보
    col=0; rowMaxH=0; curMenu=menu;
  } else if(famStart || col>=COLS){                      // 패밀리 시작 or 줄넘침 → 새 줄
    y += rowMaxH + ROWGAP; col=0; rowMaxH=0;
  }
  n.x = X0 + col*COLW; n.y = y;
  rowMaxH = Math.max(rowMaxH, n.height||1300); col++; placed++;
}
// 메뉴 섹션 라벨 텍스트 생성
let labels=0;
for(const [c,name] of LABELS){
  if(labelY[c]===undefined) continue;
  const t=figma.createText(); t.fontName={family:"Inter",style:"Bold"}; t.fontSize=140;
  t.characters=name; t.x=X0; t.y=labelY[c]; t.fills=[{type:"SOLID",color:{r:0.29,g:0.28,b:0.84}}];
  labels++;
}
"placed "+placed+", missing "+missing+", labels "+labels+" of "+ORDER.length;
`.trim()

fs.writeFileSync(DIR + '/reposition_code.js', code)
console.log('reposition_code.js 생성:', ORDER.length, '프레임 ·', LABELS.length, '메뉴 라벨')
console.log('use_figma code 길이:', code.length, '자')
