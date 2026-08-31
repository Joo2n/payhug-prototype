/* W금융일수 가중 기준 혼용 차단 — 창을 띄우지 않는다(--headless=new).

   무엇을 막는가
     확정 · 화면 값   워드 · 금액(Ai) 가중   카드 42.83%   W 3.039607일   Ty 13.21%
     참고값           엑셀 · MAU(이용자 수)   카드 65.00%   W 2.750407일   Ty 14.60%

   근거 — 대표 워드 `용어 정의.docx` 4~6번 문단 `w금융일수 = Σ Ai × Di / Σ Ai`,
          `Ai = 순지급액 × (1 − 할인율)`. 2026-08-31 사용자 결정. 레지스터 `TP-87` `확정`.

   MAU 값을 지우는 것이 아니다. 참고값으로 살아 있어야 한다(검사 다).
   막을 것은 참고값이 화면·원장·계산 자리에 계산값으로 새어 들어가는 것이다(검사 나).

   (가) 원장이 실제로 금액 가중인가
        BOOK_MIX 가 MEASURED 금액비에서 나오는가 · ledger_facts.wRaw 가 그 구성비 × 만기의
        가중평균과 소수 6자리까지 같은가 · 원장 채권 Σ Ai 를 플랫폼으로 가른 구성비가
        MEASURED 금액비와 표기 자리까지 같은가
   (나) 배포본·문서에 MAU 값이 계산값 자리에 있는가
        금지값이 나오는 자리마다 같은 문단·표 안에 `참고`·`시장 평균`·`MAU` 중 하나가
        함께 있는가. 없으면 FAIL — 갈라 적지 않은 자리다
       `~/Downloads/payhug_정산주기_정리/정산주기_정리_*.xlsx` 도 같은 규칙으로 본다 —
       MAU 비중이 실물로 담긴 파일이라 갈라 적지 않으면 화면 값과 정면으로 어긋나 보인다
   (다) 참고값이 사라지지 않았는가
        platform_duration 에 MAU_MIX·MAU_W 가 남아 있는가 · TP-87 이 확정인가 ·
        「0.35 와 카드 65% 가 매출액 기준인가」 확인 문항이 살아 있는가

   음성 시험 (2026-08-31 실시 · 심은 뒤 md5 로 원본 복원 확인) — 3건 전건 FAIL 로 잡힘
     ① `capability_manuscript.md` 에 단서 없는 `카드 비중 65%` 한 줄 → (나) 파이프라인 원고 FAIL
     ② `platform_duration.BOOK_MIX` 를 MAU 값으로 → 그 파일 자신의 `assert r2(MEASURED_W)==3.04`
        가 먼저 걸려 프로브가 죽는다. 그 assert 까지 2.75 로 풀면 (가1)·(가2)·(가3) 이 FAIL
     ③ `MAU_MIX` 삭제 → `MAU_W` 가 그것을 참조해 프로브가 죽는다. 둘을 같이 지우면
        (가2)·(다1)·(다2) 가 FAIL
   페이지 판독기가 죽는 경우는 상시 자기시험으로 본다 — 아래 `__phw_selftest`.
*/
const http = require('http'), fs = require('fs'), path = require('path'), os = require('os'),
      { spawn, spawnSync } = require('child_process');
const CHROME_DL = require('./chrome_dl');
const PH_DL = CHROME_DL.dir();

const PIPE  = '/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin';
const OUT   = path.join(PIPE, 'verify_weighting_result.json');
/* 포트는 고르지 않고 커널에서 받는다 — pid 로 자리를 잡으면 앞 회차의 크롬이 아직 물고 있을 때
   접속에 실패해 검사와 무관한 이유로 종료코드 1 이 난다(실측 1회). */
let PORT = 0;
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

/* 배포 3주소의 로컬 원본. verify_deployed.py 가 익명 수신으로 보는 그 세 곳이다. */
const REPOS = [
  { key: 'demo',  name: '전체(demo)',      dir: '/Users/semi/cursor/payhug-investor-admin',     entry: 'app.html',   walk: true  },
  { key: 'proto', name: '시연(prototype)', dir: '/Users/semi/cursor/payhug-investor-prototype', entry: 'index.html', walk: true  },
  { key: 'gloss', name: '용어(glossary)',  dir: '/Users/semi/cursor/payhug-investor-glossary',  entry: 'index.html', walk: false },
];

/* 금지값 — 대표 엑셀 MAU 비중과 거기서 나온 값. 사용자가 지정한 네 가지에
   자릿수 변형(65.0000% · 14.6%)을 더했다. 넓히는 방향이라 검사가 느슨해지지 않는다.
   `2.75` 단독은 넣지 않는다 — 두 자리 표기라 다른 값과 부딪힌다. 경계는 `2.7504` 다. */
const BAN = /(?<![\d.])65(?:\.0+)?\s*%|(?<![\d.])2\.7504|(?<![\d.])14\.60?0*\s*%/g;
/* 갈라 적었다고 인정하는 표식 — 사용자가 지정한 세 낱말 그대로 */
const MARK = ['참고', '시장 평균', 'MAU'];
const hasMark = t => MARK.some(k => String(t).indexOf(k) >= 0);

const R = { pass: [], fail: [], report: {} };
function chk(name, ok, detail) {
  (ok ? R.pass : R.fail).push(detail ? name + ' — ' + detail : name);
}

/* ══ 문단·표 가르기 ═══════════════════════════════════════════════
   md·평문 — 공백줄 하나가 문단 경계다. 표는 공백줄이 없어 통째로 한 단위가 된다.
   ``` 울타리 안은 공백줄이 있어도 가르지 않는다(계산식 한 덩어리다). */
function blocks(text) {
  const lines = String(text).split('\n');
  const out = []; let cur = [], start = 1, fence = false;
  for (let i = 0; i < lines.length; i++) {
    const ln = lines[i];
    if (/^\s*```/.test(ln)) { fence = !fence; if (!cur.length) start = i + 1; cur.push(ln); continue; }
    if (!fence && !ln.trim()) { if (cur.length) out.push({ line: start, text: cur.join('\n') }); cur = []; continue; }
    if (!cur.length) start = i + 1;
    cur.push(ln);
  }
  if (cur.length) out.push({ line: start, text: cur.join('\n') });
  return out;
}

/* html — 표 안이면 표가 한 단위, 아니면 가장 가까운 블록 요소가 한 단위 */
const BT = ['table', 'p', 'li', 'td', 'th', 'tr', 'section', 'article', 'figure',
            'blockquote', 'pre', 'div', 'dd', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'];
function htmlCtx(src, idx) {
  const re = /<(\/?)([a-zA-Z][\w-]*)([^>]*)>/g; let m; const stack = [];
  while ((m = re.exec(src)) && m.index < idx) {
    const closing = m[1] === '/', tag = m[2].toLowerCase(), self = /\/\s*$/.test(m[3]);
    if (BT.indexOf(tag) < 0) continue;
    if (closing) { for (let i = stack.length - 1; i >= 0; i--) if (stack[i].tag === tag) { stack.length = i; break; } }
    else if (!self) stack.push({ tag, start: m.index });
  }
  let pick = null;
  for (const s of stack) if (s.tag === 'table') { pick = s; break; }   // 표가 있으면 표가 단위
  if (!pick) pick = stack.length ? stack[stack.length - 1] : null;
  if (!pick) return src.slice(Math.max(0, idx - 500), idx + 500);
  const re2 = new RegExp('</?' + pick.tag + '\\b', 'gi'); re2.lastIndex = pick.start + 1;
  let d = 1, e = src.length, mm;
  while ((mm = re2.exec(src))) { if (mm[0][1] === '/') { if (--d === 0) { e = mm.index; break; } } else d++; }
  return src.slice(pick.start, e);
}

function scanText(label, text, kind) {
  const bad = [];
  if (kind === 'html') {
    BAN.lastIndex = 0; let m;
    while ((m = BAN.exec(text))) {
      const ctx = htmlCtx(text, m.index);
      if (!hasMark(ctx)) bad.push({ where: label, hit: m[0], at: m.index,
        sample: text.slice(Math.max(0, m.index - 60), m.index + 60).replace(/\s+/g, ' ') });
    }
  } else {
    for (const b of blocks(text)) {
      BAN.lastIndex = 0;
      if (!BAN.test(b.text) || hasMark(b.text)) continue;
      BAN.lastIndex = 0;
      bad.push({ where: label + ':' + b.line, hit: (BAN.exec(b.text) || [''])[0],
        sample: b.text.replace(/\s+/g, ' ').slice(0, 140) });
    }
  }
  return bad;
}

/* ══ 파이썬 프로브 — 모델 사실값·원고 명단·PDF 본문·레지스터 ═════════
   숫자를 검증기에 손으로 적지 않는다. platform_duration·daily_ledger·ledger_facts 가 낸다. */
const PROBE = String.raw`# -*- coding: utf-8 -*-
import io, json, os, re, sys
sys.path.insert(0, ${JSON.stringify(PIPE)})
os.chdir(${JSON.stringify(PIPE)})
from decimal import Decimal as D
import platform_duration as P
import daily_ledger as L

o = {}
q6 = lambda x: str(D(x).quantize(D('0.000001')))
pc = lambda x: str((D(x) * 100).quantize(D('0.01')))

o['order']       = list(P.ORDER)
o['measured']    = dict((k, P.MEASURED[k]) for k in P.ORDER)
o['measuredSum'] = str(P.MEASURED_SUM)
o['measuredMix'] = [str(v) for v in P.measured_mix()]
o['bookMix']     = [str(v) for v in P.BOOK_MIX]
o['measuredPct'] = dict((k, pc(D(P.MEASURED[k]) / P.MEASURED_SUM)) for k in P.ORDER)
o['bookPct']     = dict((k, pc(v)) for k, v in zip(P.ORDER, P.BOOK_MIX))
o['duration']    = dict((k, str(P.DURATION[k])) for k in P.ORDER)
o['measuredW6']  = q6(P.MEASURED_W)
o['hasMauMix']   = hasattr(P, 'MAU_MIX')
o['hasMauW']     = hasattr(P, 'MAU_W')
o['mauMix']      = [str(v) for v in getattr(P, 'MAU_MIX', [])]
o['mauPct']      = [pc(v) for v in getattr(P, 'MAU_MIX', [])]
o['mauW6']       = q6(getattr(P, 'MAU_W', 0)) if hasattr(P, 'MAU_W') else None
o['mauW2']       = str(P.r2(P.MAU_W)) if hasattr(P, 'MAU_W') else None

# 원장 채권 Σ Ai 를 플랫폼으로 가른 구성비 (발생 기준 전건)
tot = {}
for r in L.RECEIVABLES:
    tot[r['plat']] = tot.get(r['plat'], 0) + r['ai']
s = sum(tot.values())
o['ledgerAi']  = dict((k, tot.get(k, 0)) for k in P.ORDER)
o['ledgerPct'] = dict((k, pc(D(tot.get(k, 0)) / D(s))) for k in P.ORDER)
o['ledgerW6']  = q6(L.W_RAW)

o['facts'] = json.load(io.open(os.path.join(${JSON.stringify(PIPE)}, 'ledger_facts.json'), encoding='utf-8'))
del o['facts']['tyByDate']

# 파이프라인 원고 — 목록을 검증기가 들고 있지 않고 build_archive.py 의 DESC 에서 읽는다.
#   DESC 가 '원고' · '브리핑' 이라 부르는 .md 가 문서로 나가는 원고다. 새 원고가 늘면 저절로 따라온다.
#   '결정안'·작업 기록은 화면·원장으로 흘러가는 자리가 아니라 범위 밖이고, 대신
#   rescale_decision.md 는 머리말 표식을 따로 판정한다(아래 supersede).
arc = io.open(os.path.join(${JSON.stringify(PIPE)}, 'build_archive.py'), encoding='utf-8').read()
desc = dict(re.findall(r'"([\w.\-]+\.md)"\s*:\s*"([^"]*)"', arc))
o['desc'] = desc
o['manuscripts'] = sorted(f for f, d in desc.items()
                          if ('원고' in d or '브리핑' in d)
                          and os.path.exists(os.path.join(${JSON.stringify(PIPE)}, f)))
o['mdAll'] = sorted(f for f in os.listdir(${JSON.stringify(PIPE)}) if f.endswith('.md'))
o['mdNoDesc'] = [f for f in o['mdAll'] if f not in desc]
o['manuscriptText'] = dict((f, io.open(os.path.join(${JSON.stringify(PIPE)}, f), encoding='utf-8').read())
                           for f in o['manuscripts'])
o['supersede'] = io.open(os.path.join(${JSON.stringify(PIPE)}, 'rescale_decision.md'),
                         encoding='utf-8').read()[:1400]

# 산출 문서 — assets/docs 의 실물. PDF 본문은 PyMuPDF 로 뽑는다.
o['docs'] = {}
o['pdfErr'] = None
DOC = '/Users/semi/cursor/payhug-investor-admin/assets/docs'
for f in sorted(os.listdir(DOC)):
    p = os.path.join(DOC, f)
    if f.endswith('.pdf'):
        try:
            import fitz
            d = fitz.open(p)
            o['docs'][f] = '\n\n'.join(pg.get_text() for pg in d)
        except Exception as e:
            o['pdfErr'] = '%s: %s' % (f, e)
    elif f.endswith(('.txt', '.md', '.csv')):
        o['docs'][f] = io.open(p, encoding='utf-8', errors='replace').read()

# 레지스터 TP-87
reg = io.open('/Users/semi/cursor/payhug/payhug-spec/analysis/terms_policy_register.md',
              encoding='utf-8').read()
m = re.search(r'^### (TP-87\b[^\n]*)\n(.*?)(?=\n### |\Z)', reg, re.S | re.M)
o['tp87'] = {'found': bool(m), 'title': m.group(1) if m else None, 'body': m.group(2) if m else None}
if m:
    st = re.search(r'\|\s*상태\s*\|\s*([^|\n]+?)\s*\|', m.group(2))
    o['tp87']['status'] = st.group(1) if st else None

# 확인 문항 — 대표가 「매출액 기준」이라고 답하면 65% 로 되돌린다. 그 문항이 살아 있어야 한다.
axl = io.open(os.path.join(${JSON.stringify(PIPE)}, 'build_audit_xlsx.py'), encoding='utf-8').read()
o['inquiryAlive'] = ('0.35' in axl and '카드 65%' in axl
                     and '매출액 기준인가' in axl)

# 정산주기_정리 워크북 — MAU(이용자 수) 비중이 실물로 담긴 파일. 판정 대상이다.
#   이 파일만 보면 W 2.7504068548610725 · Ty 14.60% 가 화면의 3.04 · 13.21 과 어긋나 보인다.
#   MAU 값은 지우지 않는다. 그 자리에 갈라적기 표식이 붙어 있는지만 본다.
import glob
BANC = re.compile(r'(?<![\d.])65(?:\.0+)?\s*%|(?<![\d.])2\.7504|(?<![\d.])14\.60?0*\s*%')
o['cycle'] = {'path': None, 'cells': 0, 'hits': [], 'markText': '', 'err': None}
try:
    import openpyxl as _ox
    _cg = sorted(glob.glob(os.environ.get(
        'CYCLE_GLOB',
        os.path.expanduser('~/Downloads/payhug_정산주기_정리/정산주기_정리_*.xlsx'))))
    if not _cg:
        o['cycle']['err'] = '파일 없음'
    else:
        cp = _cg[-1]
        o['cycle']['path'] = cp
        cwb = _ox.load_workbook(cp)
        for cws in cwb.worksheets:
            for crow in cws.iter_rows():
                for cc in crow:
                    if cc.value is None:
                        continue
                    o['cycle']['cells'] += 1
                    if not BANC.search(str(cc.value)):
                        continue
                    near = ' '.join(str(x.value) for rr in
                                    cws.iter_rows(min_row=max(1, cc.row - 4),
                                                  max_row=cc.row + 4)
                                    for x in rr if x.value is not None)
                    o['cycle']['hits'].append(
                        {'sheet': cws.title, 'cell': cc.coordinate,
                         'value': str(cc.value)[:60],
                         'marked': any(k in near for k in ('참고', '시장 평균', 'MAU'))})
        cwv = cwb['가중평균']
        o['cycle']['markText'] = ' '.join(
            str(cwv.cell(r, c).value) for r in range(1, cwv.max_row + 1)
            for c in range(1, cwv.max_column + 1) if cwv.cell(r, c).value)
except Exception as e:
    o['cycle']['err'] = str(e)

# 판정하지 않고 보고만 — 검산 엑셀 실물(수정 금지 대상이라 판정해도 고칠 수 없다)
o['xlsx'] = []
try:
    import openpyxl
    XP = os.path.join(${JSON.stringify(PIPE)}, '검산_투자자어드민_20260901.xlsx')
    wb = openpyxl.load_workbook(XP)
    BANX = re.compile(r'(?<![\d.])65(?:\.0+)?\s*%|(?<![\d.])2\.7504|(?<![\d.])14\.60?0*\s*%')
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if c.value is None:
                    continue
                if BANX.search(str(c.value)):
                    near = ' '.join(str(x.value) for r2_ in
                                    ws.iter_rows(min_row=max(1, c.row - 4), max_row=c.row + 4)
                                    for x in r2_ if x.value is not None)
                    o['xlsx'].append({'sheet': ws.title, 'cell': c.coordinate,
                                      'value': str(c.value)[:100],
                                      'marked': any(k in near for k in ('참고', '시장 평균', 'MAU'))})
except Exception as e:
    o['xlsx'] = [{'sheet': '(읽기 실패)', 'cell': '-', 'value': str(e), 'marked': False}]

sys.stdout.write(json.dumps(o, ensure_ascii=False))
`;

const probeFile = path.join(os.tmpdir(), 'phw-probe-' + process.pid + '.py');
fs.writeFileSync(probeFile, PROBE);
const pr = spawnSync('python3', [probeFile], { encoding: 'utf-8', maxBuffer: 1 << 28 });
fs.unlinkSync(probeFile);
if (pr.status !== 0) { console.error('FAIL 파이썬 프로브\n' + (pr.stderr || '').slice(-3000)); process.exit(1); }
const P = JSON.parse(pr.stdout);

/* ══ (가) 원장이 실제로 금액 가중인가 ═══════════════════════════ */
const F = P.facts;
chk('(가1) BOOK_MIX = MEASURED 금액비',
    JSON.stringify(P.bookMix) === JSON.stringify(P.measuredMix),
    'BOOK_MIX ' + P.bookMix.join(' / ') + '  MEASURED ' + P.measuredMix.join(' / '));
chk('(가2) BOOK_MIX ≠ MAU_MIX (두 기준이 섞이지 않았다)',
    P.hasMauMix && JSON.stringify(P.bookMix) !== JSON.stringify(P.mauMix),
    '카드 BOOK ' + P.bookPct.card + '% · MAU ' + (P.mauPct[0] || '-') + '%');
chk('(가3) ledger_facts.wRaw = Σ(BOOK_MIX × 만기), 소수 6자리',
    F.wRaw === P.measuredW6 && P.ledgerW6 === P.measuredW6,
    'wRaw ' + F.wRaw + ' · 원장 실측 ' + P.ledgerW6 + ' · 구성비×만기 ' + P.measuredW6);
{
  const got = P.order.map(k => P.ledgerPct[k]).join(' / ');
  const want = P.order.map(k => P.measuredPct[k]).join(' / ');
  chk('(가4) 원장 채권 Σ Ai 플랫폼 구성비 = MEASURED 금액비 (표기 자리)',
      got === want, got + '  vs  ' + want);
}
chk('(가5) 화면 표기 W·Ty 가 MAU 값이 아니다',
    F.w !== P.mauW2 && F.ty !== '14.60',
    'W ' + F.w + ' · Ty ' + F.ty + '  (MAU 였다면 ' + P.mauW2 + ' · 14.60)');

/* ══ (다) 참고값이 사라지지 않았는가 ═══════════════════════════ */
chk('(다1) platform_duration.MAU_MIX 잔존', P.hasMauMix,
    P.hasMauMix ? 'card ' + P.mauPct[0] + '% · ' + P.mauPct.slice(1).join(' / ') + '%' : '없다');
chk('(다2) platform_duration.MAU_W 잔존 · 2.750407', P.hasMauW && P.mauW6 === '2.750407',
    String(P.mauW6));
chk('(다3) 레지스터 TP-87 확정',
    P.tp87.found && P.tp87.status === '확정', (P.tp87.title || '없음') + ' / ' + P.tp87.status);
chk('(다4) TP-87 이 금액 가중과 MAU 참고값 두 사실을 다 적는다',
    !!P.tp87.body && /Σ\s*Ai|Ai\s*[x×]\s*Di/.test(P.tp87.body) && P.tp87.body.indexOf('MAU') >= 0
      && P.tp87.body.indexOf('참고') >= 0);
chk('(다5) 「0.35·카드 65% 가 매출액 기준인가」 확인 문항 잔존', P.inquiryAlive,
    'build_audit_xlsx.py 확인 문항 2');
{
  const C = P.cycle, mt = C.markText || '';
  chk('(다7) 정산주기_정리 워크북 판독', !C.err && !!C.path, C.err || C.path);
  chk('(다7) 정산주기_정리 검사 대상 0건 아님', C.cells > 0, C.cells + '셀');
  chk('(다7) 정산주기_정리 MAU 값 자리 0건 아님 — 참고값이 지워지지 않았다',
      C.hits.length > 0, C.hits.map(h => h.sheet + '!' + h.cell).join(', '));
  chk('(다7) 정산주기_정리 `가중평균` 시트 갈라적기 한 줄',
      hasMark(mt) && mt.indexOf('금액') >= 0 && mt.indexOf(F.w) >= 0
        && mt.indexOf(F.ty) >= 0,
      '표식 ' + hasMark(mt) + ' · 금액 ' + (mt.indexOf('금액') >= 0) +
      ' · W ' + F.w + ' ' + (mt.indexOf(F.w) >= 0) +
      ' · Ty ' + F.ty + ' ' + (mt.indexOf(F.ty) >= 0));
  chk('(나) 정산주기_정리 워크북 — 갈라 적지 않은 자리 0건 (' + C.hits.length + '곳 검사)',
      C.hits.every(h => h.marked),
      C.hits.filter(h => !h.marked).map(h => h.sheet + '!' + h.cell + ' 「' + h.value + '」')
        .join(' | '));
}

chk('(다6) rescale_decision.md 머리말이 폐기·참고값을 갈라 적는다',
    P.supersede.indexOf('폐기') >= 0 && P.supersede.indexOf('TP-87') >= 0
      && hasMark(P.supersede) && P.supersede.indexOf('42.83') >= 0
      && P.supersede.indexOf('3.039607') >= 0,
    '이 표식이 있어야 결정안 본문이 (나) 판정 범위 밖으로 빠진다');

/* ══ (나) 배포본·문서 — 정적 갈래 (원고 · 산출 문서 · 저장소 원천) ══ */
const hits = { render: [], repo: [], manuscript: [], doc: [] };
const counted = { render: 0, repo: 0, manuscript: 0, doc: 0 };

for (const f of P.manuscripts) {
  counted.manuscript++;
  hits.manuscript.push(...scanText(f, P.manuscriptText[f], 'text'));
}
for (const f of Object.keys(P.docs)) {
  counted.doc++;
  hits.doc.push(...scanText('assets/docs/' + f, P.docs[f], 'text'));
}

const TEXT_EXT = ['.html', '.css', '.js', '.md', '.txt', '.json', '.csv', '.svg'];
function repoTextFiles(dir) {
  const out = [];
  (function walk(d, rel) {
    for (const e of fs.readdirSync(d, { withFileTypes: true })) {
      if (e.name === '.git' || e.name === 'node_modules' || e.name === '.claude') continue;
      const p = path.join(d, e.name), r = rel ? rel + '/' + e.name : e.name;
      if (e.isDirectory()) { walk(p, r); continue; }
      if (TEXT_EXT.indexOf(path.extname(e.name).toLowerCase()) >= 0) out.push({ abs: p, rel: r });
    }
  })(dir, '');
  return out;
}
for (const rep of REPOS) {
  for (const f of repoTextFiles(rep.dir)) {
    counted.repo++;
    const src = fs.readFileSync(f.abs, 'utf-8');
    hits.repo.push(...scanText(rep.key + '/' + f.rel, src,
      /\.(html|svg)$/i.test(f.rel) ? 'html' : 'text'));
  }
}

/* ══ (나) 배포본 — 렌더된 텍스트 ═══════════════════════════════ */
const server = http.createServer((q, r) => {
  const u = decodeURIComponent(q.url.split('?')[0].split('#')[0]);
  const m = /^\/(demo|proto|gloss)(\/.*)?$/.exec(u);
  if (!m) { r.writeHead(404); r.end('x'); return; }
  const rep = REPOS.find(x => x.key === m[1]);
  const p = path.join(rep.dir, m[2] || '/');
  fs.readFile(p, (e, b) => {
    if (e) { r.writeHead(404); r.end('x'); return; }
    const MIME = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8',
      '.js': 'text/javascript', '.png': 'image/png', '.webp': 'image/webp',
      '.json': 'application/json', '.svg': 'image/svg+xml' };
    r.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' });
    r.end(b);
  });
});

let id = 0, ws, pend = new Map();
function send(m, p) {
  const i = ++id; ws.send(JSON.stringify({ id: i, method: m, params: p || {} }));
  return new Promise((res, rej) => pend.set(i, { res, rej }));
}
async function ev(x) {
  const r = await send('Runtime.evaluate',
    { expression: '(function(){' + x + '})()', returnByValue: true, awaitPromise: true });
  if (r.exceptionDetails) throw new Error('eval: ' + JSON.stringify(r.exceptionDetails));
  return r.result.value;
}
const sleep = ms => new Promise(r => setTimeout(r, ms));

/* 페이지 안에서 도는 판독기 — 텍스트 노드마다 금지값을 찾고, 그 노드를 감싸는
   가장 가까운 표·문단의 화면 텍스트에 표식이 있는지 본다. 없으면 걸린다. */
const PAGE_SCAN = String.raw`
  var PAT = /(?<![\d.])65(?:\.0+)?\s*%|(?<![\d.])2\.7504|(?<![\d.])14\.60?0*\s*%/g;
  var MARK = ['참고', '시장 평균', 'MAU'];
  var SEL = 'table,p,li,td,th,dd,dt,blockquote,figure,pre,section,article,h1,h2,h3,h4,h5,h6';
  var out = [], w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null), n;
  while ((n = w.nextNode())) {
    var t = n.nodeValue; if (!t) continue;
    PAT.lastIndex = 0; var m = PAT.exec(t); if (!m) continue;
    var el = n.parentElement; if (!el) continue;
    var ctx = el.closest('table') || el.closest(SEL) || el;
    var ct = ctx.innerText || ctx.textContent || '';
    var ok = MARK.some(function (k) { return ct.indexOf(k) >= 0; });
    if (!ok) out.push({ hit: m[0], sample: t.trim().slice(0, 120),
                        ctx: ctx.tagName + (ctx.id ? '#' + ctx.id : '') });
  }
  return out;
`;

(async () => {
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  PORT = server.address().port;
  const prof = fs.mkdtempSync(path.join(os.tmpdir(), 'phw-'));
  const ch = spawn(CHROME, ['--headless=new', '--remote-debugging-port=0',
    CHROME_DL.args(PH_DL, prof)[0], '--no-first-run', '--no-default-browser-check',
    '--disable-gpu', '--hide-scrollbars', '--window-size=1440,1287', 'about:blank'],
    { stdio: 'ignore' });
  /* 크롬이 실제로 문 연 포트는 프로필의 DevToolsActivePort 첫 줄에 적힌다 */
  const dpFile = path.join(prof, 'DevToolsActivePort');
  let DPORT = 0;
  for (let i = 0; i < 80 && !DPORT; i++) {
    await sleep(250);
    try { DPORT = parseInt(fs.readFileSync(dpFile, 'utf-8').split('\n')[0], 10) || 0; } catch (e) { DPORT = 0; }
  }
  let t = null;
  for (let i = 0; i < 60 && !t && DPORT; i++) {
    await sleep(250);
    try {
      t = await new Promise((res, rej) => {
        http.get({ host: '127.0.0.1', port: DPORT, path: '/json' },
          r => { let d = ''; r.on('data', c => d += c); r.on('end', () => res(JSON.parse(d))); }).on('error', rej);
      });
    } catch (e) { t = null; }
  }
  if (!t) { console.error('FAIL 크롬에 붙지 못했다 (DevToolsActivePort=' + DPORT + ')'); process.exit(1); }
  ws = new WebSocket(t.find(x => x.type === 'page').webSocketDebuggerUrl);
  await new Promise(r => ws.addEventListener('open', r));
  ws.addEventListener('message', e => {
    const m = JSON.parse(e.data);
    if (m.id && pend.has(m.id)) { pend.get(m.id).res(m.result); pend.delete(m.id); }
  });
  await send('Runtime.enable'); await send('Page.enable');

  const screens = [];
  for (const rep of REPOS) {
    for (const f of fs.readdirSync(rep.dir)) if (/\.html$/i.test(f)) screens.push({ rep, url: f });
    const ad = path.join(rep.dir, 'assets');
    if (fs.existsSync(ad))
      for (const f of fs.readdirSync(ad)) if (/\.html$/i.test(f)) screens.push({ rep, url: 'assets/' + f });
  }

  for (const s of screens) {
    await send('Page.navigate', { url: 'http://127.0.0.1:' + PORT + '/' + s.rep.key + '/' + encodeURIComponent(s.url) });
    await sleep(s.url === s.rep.entry ? 1600 : 500);
    let got = [];
    try { got = await ev(PAGE_SCAN); } catch (e) { got = [{ hit: '(판독 실패)', sample: String(e).slice(0, 120), ctx: '-' }]; }
    counted.render++;
    got.forEach(g => hits.render.push({ where: s.rep.key + '/' + s.url, ...g }));

    /* 통합본·시연본은 화면 하나가 아니다 — 등록된 화면 × 상태를 전부 돌며 다시 읽는다.
       상태 목록을 검증기가 들고 있지 않고 화면의 SCREEN_ORDER·STATE_META 에서 읽는다. */
    if (s.rep.walk && s.url === s.rep.entry) {
      const walked = await ev(`
        if (typeof SCREEN_ORDER === 'undefined' || typeof go !== 'function') return null;
        var res = [], seen = 0, skipped = [];
        SCREEN_ORDER.forEach(function (sc) {
          var meta = (typeof STATE_META !== 'undefined' && STATE_META[sc]) || { 'default': null };
          Object.keys(meta).forEach(function (st) {
            try { go(sc, st); } catch (e) { skipped.push(sc + '/' + st); return; }
            seen++;
            var found = (function () { ${PAGE_SCAN} })();
            found.forEach(function (f) { f.state = sc + '/' + st; res.push(f); });
          });
        });
        go(SCREEN_ORDER[0], 'default');
        return { states: res, n: seen, screens: SCREEN_ORDER.length, skipped: skipped };`);
      if (!walked) { chk('(나0) ' + s.rep.name + ' 화면·상태 목록 판독', false, 'SCREEN_ORDER·go 를 못 읽었다'); }
      else {
        counted.render += walked.n;
        R.report[s.rep.key + 'Walk'] = { screens: walked.screens, statesScanned: walked.n,
                                         skipped: walked.skipped };
        /* 상태를 세우다 튕긴 자리는 그 상태를 못 본 것이다 — 조용히 넘기지 않는다 */
        chk('(나0) ' + s.rep.name + ' 화면 × 상태 전건 도달 (' + walked.n + '건)',
            walked.skipped.length === 0, walked.skipped.slice(0, 5).join(', '));
        walked.states.forEach(g => hits.render.push({ where: s.rep.key + '/' + g.state, ...g }));
      }
    }
  }

  /* 페이지 판독기 자기시험 — 셀렉터가 낡거나 정규식이 죽으면 「걸린 자리 0건」이 저절로 나온다.
     지금 열려 있는 화면에 위반 한 줄과 갈라 적은 한 줄을 붙였다 떼며, 앞은 잡고 뒤는 안 잡는지 본다.
     디스크는 건드리지 않는다(붙였다 바로 떼는 DOM 노드다). */
  const self = await ev(`
    var d = document.createElement('div');
    d.id = '__phw_selftest';
    d.innerHTML = '<p>카드 비중 65%</p>' +
                  '<table><tr><td>대표 엑셀 시장 평균 참고값 카드 65%</td></tr></table>';
    document.body.appendChild(d);
    var got = (function () { ${PAGE_SCAN} })();
    d.remove();
    return { caught: got.length, left: document.getElementById('__phw_selftest') ? 1 : 0 };`);
  chk('(나0) 페이지 판독기 자기시험 — 갈라 적지 않은 1건만 잡는다',
      self && self.caught === 1 && self.left === 0, JSON.stringify(self));

  /* 검사 대상이 0건이면 아무것도 안 보고 통과한다 — 네 갈래 각각 0건인지부터 본다
     (verify_links.py 의 「검사 대상 링크 0건 아님」과 같은 갈래). */
  chk('(나0) 검사 대상 0건 아님 — 렌더', counted.render > 0, counted.render + '화면·상태');
  chk('(나0) 검사 대상 0건 아님 — 저장소 원천', counted.repo > 0, counted.repo + '파일');
  chk('(나0) 검사 대상 0건 아님 — 원고', counted.manuscript > 0,
      counted.manuscript + '건: ' + P.manuscripts.join(', '));
  chk('(나0) 검사 대상 0건 아님 — 산출 문서', counted.doc > 0,
      counted.doc + '건: ' + Object.keys(P.docs).join(', '));

  const NAME = { render: '배포 3주소 렌더된 텍스트', repo: '배포 3주소 원천 텍스트',
                 manuscript: '파이프라인 원고', doc: '산출 문서' };
  for (const k of ['render', 'repo', 'manuscript', 'doc']) {
    chk('(나) ' + NAME[k] + ' — 갈라 적지 않은 자리 0건 (' + counted[k] + '곳 검사)',
        hits[k].length === 0,
        hits[k].slice(0, 6).map(h => h.where + ' 「' + h.hit + '」 ' +
          (h.sample || '').slice(0, 70)).join(' | '));
  }

  R.report.counted = counted;
  R.report.hits = hits;
  R.report.manuscripts = P.manuscripts;
  R.report.mdOutOfScope = P.mdAll.filter(f => P.manuscripts.indexOf(f) < 0);
  R.report.mdNoDesc = P.mdNoDesc;
  R.report.xlsx = P.xlsx;
  R.report.cycleXlsx = P.cycle;
  R.report.pdfErr = P.pdfErr;
  R.report.model = { bookPct: P.bookPct, mauPct: P.mauPct, wRaw: F.wRaw, w: F.w, ty: F.ty,
                     mauW: P.mauW6, ledgerPct: P.ledgerPct };

  /* PDF 본문을 못 읽었으면 검사 못 한 것이다 — 조용히 넘기지 않는다(verify_0828.py 와 같은 기준) */
  chk('(나) 산출 문서 PDF 본문 판독', !P.pdfErr, P.pdfErr || 'PyMuPDF 로 전건 판독');

  console.log('== W금융일수 가중 기준 ==');
  console.log('  확정 · 화면 값  금액(Ai) 가중  카드 ' + P.bookPct.card + '%  W ' + F.wRaw + '  Ty ' + F.ty + '%');
  console.log('  참고값          MAU 이용자 수  카드 ' + P.mauPct[0] + '%  W ' + P.mauW6 + '  Ty 14.60%');
  console.log('  검사 대상 — 렌더 ' + counted.render + ' · 저장소 원천 ' + counted.repo +
              ' · 원고 ' + counted.manuscript + ' · 산출 문서 ' + counted.doc +
              ' · 정산주기_정리 ' + P.cycle.cells + '셀');
  P.cycle.hits.forEach(h => console.log('    정산주기_정리 ' +
              (h.marked ? '표식 있음 ' : '표식 없음 ') + h.sheet + '!' + h.cell +
              '  ' + h.value));
  console.log('-- 판정하지 않고 보고만 --');
  console.log('  범위 밖 .md ' + R.report.mdOutOfScope.length + '건 — build_archive.py DESC 가 ' +
              '`원고`·`브리핑` 으로 부르지 않는 작업 기록. 화면·원장으로 흘러가는 자리가 아니다');
  console.log('  DESC 없는 .md ' + P.mdNoDesc.length + '건: ' + (P.mdNoDesc.join(', ') || '없음'));
  console.log('  검산 엑셀 금지값 ' + P.xlsx.length + '건 — 수정 금지 대상(지시)이라 판정해도 고칠 수 없다. ' +
              'audit_xlsx_check.py 소관');
  P.xlsx.forEach(x => console.log('    ' + (x.marked ? '표식 있음 ' : '표식 없음 ') +
              x.sheet + '!' + x.cell + '  ' + x.value));

  console.log('== 판정 ' + (R.pass.length + R.fail.length) + '건 · FAIL ' + R.fail.length + ' ==');
  R.pass.forEach(x => console.log('  PASS ' + x));
  R.fail.forEach(x => console.log('  FAIL ' + x));
  for (const k of ['render', 'repo', 'manuscript', 'doc'])
    hits[k].forEach(h => console.log('    걸린 자리 [' + NAME[k] + '] ' + h.where +
      ' 「' + h.hit + '」 ' + (h.sample || '').slice(0, 110)));

  fs.writeFileSync(OUT, JSON.stringify(R, null, 1));
  try { ch.kill('SIGKILL'); } catch (e) {}
  server.close();
  /* 프로필 정리는 판정이 아니다 — 크롬이 아직 파일을 쥐고 있으면 ENOTEMPTY 가 나서
     FAIL 0 인데 종료코드 1 이 된다(실측). 정리 실패로 검사 결과를 뒤집지 않는다. */
  await sleep(300);
  try { fs.rmSync(prof, { recursive: true, force: true }); } catch (e) {}
  process.exit(R.fail.length ? 1 : 0);
})().catch(e => { console.error('FAIL', e); process.exit(1); });
