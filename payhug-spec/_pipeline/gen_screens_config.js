// 남은 어드민 화면 전체에 대해 심화 워크플로우용 config(page_id, name, files) 생성.
const fs = require('fs')
const ROOT = '/Users/semi/cursor/payhug/01_payhug-admin-web-main'
const manifest = require('./screen_manifest.json')
const dd = JSON.parse(fs.readFileSync('./deepdive_content.json', 'utf8'))
const done = new Set(dd.screens.map(s => s.page_id))

// prefix → 도메인 공유 파일(핵심 2~3개)
function sharedFor(pid) {
  if (/^AD_SALES/.test(pid)) return ['app/sales/[bizNo]/page.tsx', 'services/manualSalesService.ts', 'hooks/usePurchaseLedger.ts']
  if (/^AD_SIM/.test(pid)) return ['app/settlement/simulation/page.tsx', 'services/settlementService.ts', 'lib/settlementLabels.ts']
  if (/^AD_PRODUCT/.test(pid)) return ['app/settlement/policies/page.tsx', 'app/settlement/policies/PolicyFormModal.tsx', 'types/settlement.ts']
  if (/^AD_SETTLE/.test(pid)) return ['app/settlement/overview/page.tsx', 'services/settlementService.ts', 'hooks/useSettlementOverview.ts', 'lib/settlementLabels.ts']
  if (/^AD_MERCHANT/.test(pid)) return ['app/merchants/[id]/page.tsx', 'services/merchantService.ts', 'types/merchant.ts']
  if (/^AD_PARTNER/.test(pid)) return ['app/partners/page.tsx', 'services/partnerService.ts']
  if (/^AD_TERMS/.test(pid)) return ['app/terms/page.tsx', 'services/termsService.ts']
  if (/^AD_INQUIRY/.test(pid)) return ['app/inquiries/page.tsx']
  if (/^AD_BALANCE/.test(pid)) return ['app/account-balance/page.tsx']
  if (/^AD_SCRAPING/.test(pid)) return ['app/scraping-incidents/page.tsx', 'services/cooconService.ts', 'lib/platformSettlementConstants.ts']
  if (/^AD_(LOG|AI|SCRAPING)/.test(pid)) return ['app/activity-logs/page.tsx', 'app/log-analysis/page.tsx', 'services/logAnalysisService.ts']
  if (/^AD_(LOGIN|HOME)/.test(pid)) return ['app/login/page.tsx', 'components/AdminLayout.tsx', 'services/authService.ts']
  return []
}

const ADMIN_SHARED_EXIST = new Set() // 존재 파일만
function exists(rel) {
  if (ADMIN_SHARED_EXIST.has(rel)) return true
  try { fs.accessSync(ROOT + '/' + rel); ADMIN_SHARED_EXIST.add(rel); return true } catch { return false }
}

const out = []
for (const m of manifest) {
  if (!/^AD_/.test(m.page_id)) continue
  if (done.has(m.page_id)) continue
  const src = (m.src_files || []).filter(f => f && exists(f))
  const shared = sharedFor(m.page_id).filter(f => exists(f))
  const files = Array.from(new Set([...src, ...shared])).slice(0, 6)
  if (files.length === 0) continue // 코드 근거 없는 화면(순수 UI 상태)은 스킵
  out.push({ page_id: m.page_id, name: m.page_name, menu: m.menu, files })
}
fs.writeFileSync('./screens_all_config.json', JSON.stringify(out))
console.log('남은 어드민 심화 대상:', out.length)
// 파일 없어 스킵된 것
const skipped = manifest.filter(m => /^AD_/.test(m.page_id) && !done.has(m.page_id) && out.findIndex(o => o.page_id === m.page_id) < 0)
console.log('스킵(코드파일 없음):', skipped.length, skipped.map(s => s.page_id).slice(0, 30).join(', '))
// 메뉴별 분포
const byMenu = {}
for (const o of out) { const g = o.page_id.replace(/^AD_/, '').split('_')[0]; byMenu[g] = (byMenu[g] || 0) + 1 }
console.log('그룹별:', JSON.stringify(byMenu))
