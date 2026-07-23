// figma_map_shallow.json에서 AD_ 접두 117개(심화 전 얕은 프레임)만 삭제하는 use_figma 코드 생성.
// MC_/PH_/ST_(가맹점·예시)는 절대 포함하지 않음. 새 심화 노드(figma_map_deep)와도 겹치지 않음.
const fs = require('fs')
const DIR = '/Users/semi/cursor/payhug/payhug-spec/_pipeline'
const shallow = JSON.parse(fs.readFileSync(DIR + '/figma_map_shallow.json', 'utf8'))
const deep = JSON.parse(fs.readFileSync(DIR + '/figma_map_deep.json', 'utf8'))

// 삭제 대상 = AD_ 접두 & 얕은 노드. 안전: 새 심화 노드값과 동일하면 제외.
const deepVals = new Set(Object.values(deep))
const targets = []
for (const [pid, node] of Object.entries(shallow)) {
  if (!pid.startsWith('AD_')) continue
  if (deepVals.has(node)) continue // 혹시라도 겹치면 스킵(안전)
  targets.push(node)
}
console.log('삭제 대상(AD_ 얕은 프레임):', targets.length)

const code = `
const IDS = ${JSON.stringify(targets)};
const page = figma.root.children.find(p=>p.id==="303:173");
await figma.setCurrentPageAsync(page);
let removed=0, absent=0;
for(const id of IDS){
  try{ const n=await figma.getNodeByIdAsync(id); if(n){ n.remove(); removed++; } else absent++; }
  catch(e){ absent++; }
}
"removed "+removed+", absent "+absent+" of "+IDS.length;
`.trim()

fs.writeFileSync(DIR + '/delete_shallow_code.js', code)
console.log('delete_shallow_code.js 생성 · 길이', code.length)
