# -*- coding: utf-8 -*-
"""투자자 어드민 Figma 임포트용 스테이징 사본 전처리.

  sync     레포 → _fig 동기화 + CSS 패치(모노 폰트 교체 · 시트 말줄임 제거)
  measure  _fig 렌더 → value 필드 기하 측정 → fig_meas.json
  apply    capture.js 주입 + 폰트 링크 주입 + value 보유 input → 텍스트 노드 치환
  verify   스테이징 사본이 캡처 준비 상태인지 확인
  fontgate --font-mono 가 Roboto Mono 로 해석되는지 실측 (캡처 배치 직전 필수)
  heights  프레임 높이 산출 → fig_heights.json (캡처 직전 필수)
  all      sync → measure → apply

원본 레포는 읽기만 한다. 쓰기는 _fig/ 안에서만 일어난다.

모노 폰트 — 레포 원본 스택은 Chrome에서 Menlo로 해석되는데 Figma에 Menlo가 없어
캡처 노드가 hasMissingFont 상태가 되고(텍스트 속성 쓰기 전면 차단) 대체 폰트 폭이
Chrome 실측 폭을 넘겨 숫자 셀이 말줄임된다. 스테이징에서만 Figma 내장 구글폰트
'Roboto Mono'로 갈아 Chrome·Figma가 같은 패밀리를 쓰게 한다.
advance 0.6em vs Menlo 0.6021em — 14px 13자리에서 0.4px 차로 열 폭 영향 없음.
"""
import json, re, os, sys, shutil, subprocess, time, urllib.parse

SRC = '/Users/semi/cursor/payhug-investor-admin'
BASE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(BASE, '_fig')
MEAS_PATH = os.path.join(BASE, 'fig_meas.json')
PORT = 8903

# 임포트 대상 35화면. invest-profit--datepicker 는 093a07b 에서 폐기(커스텀 달력 팝오버가 실물에 없음).
IMPORT = [
    'invest-assets', 'certificate', 'invest-profit', 'coocon', 'merchants',
    'acquisition', 'acquisition--doc', 'contracts', 'password',
    'invest-assets--download', 'invest-assets--cert-confirm',
    'invest-assets--empty', 'invest-profit--monthly', 'invest-profit--empty',
    'merchants--filtered', 'merchants--empty',
    'acquisition--confirm', 'acquisition--signing', 'acquisition--done',
    'contracts--all', 'contracts--empty',
    'password--weak', 'password--error', 'password--done',
    'invest-profit--weekly', 'invest-sim', 'invest-sim--result',
    'index', 'login',
    'xls-assets-status', 'xls-assets-merchant', 'xls-profit-status', 'xls-profit-daily',
]
HOLD = []

ASSET_DIRS = ['docs', 'xlsx', 'shots']
ASSET_FILES = ['base.css', 'sheet.css', 'logo-icon.png', 'template.html']

CAP = '<script src="https://mcp.figma.com/mcp/html-to-design/capture.js" async></script>'
FONTLINK = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;500;700&display=block" rel="stylesheet">'
)
MONO = "'Roboto Mono', ui-monospace, Menlo, monospace"
CAL = ('<svg viewBox="0 0 24 24" fill="none" stroke="#1a1a1a" stroke-width="1.9" '
       'style="width:15px;height:15px;flex:none;margin-right:1px">'
       '<rect x="3" y="5" width="18" height="16" rx="2"/>'
       '<path d="M3 10.5h18M8 3v4M16 3v4" stroke-linecap="round"/></svg>')

ATTR = re.compile(r'(\w[\w:-]*)\s*=\s*"([^"]*)"')
INPUT = re.compile(r'<input\b[^>]*\bvalue="[^"]*"[^>]*>')


def files():
    return [n + '.html' for n in IMPORT]


# ---------------------------------------------------------------- sync
def patch_css():
    """모노 폰트 교체 + 시트 셀 말줄임 제거. 둘 다 멱등."""
    out = []
    p = os.path.join(FIG, 'assets', 'base.css')
    s = open(p, encoding='utf-8').read()
    new, n = re.subn(r'(--font-mono:\s*)[^;]+;', r'\g<1>' + MONO + ';', s, count=1)
    if n != 1:
        raise SystemExit('base.css 의 --font-mono 선언을 찾지 못했다 — 원본 구조 확인 필요')
    open(p, 'w', encoding='utf-8').write(new)
    out.append('base.css --font-mono → %s' % MONO)

    # 시트 셀 말줄임 — 캡처가 textTruncation=ENDING 으로 옮겨 숫자가 잘린다.
    # .tbl / .fb-name 등 base.css 쪽 말줄임은 실제 디자인 의도라 건드리지 않는다.
    p = os.path.join(FIG, 'assets', 'sheet.css')
    s = open(p, encoding='utf-8').read()
    new, n = re.subn(r'\s*text-overflow:\s*ellipsis;', '', s)
    open(p, 'w', encoding='utf-8').write(new)
    out.append('sheet.css text-overflow:ellipsis %d곳 제거' % n)
    return out


def sync():
    if not os.path.isdir(SRC):
        raise SystemExit('원본 레포 없음: %s' % SRC)
    head = subprocess.run(['git', '-C', SRC, 'rev-parse', '--short', 'HEAD'],
                          capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(['git', '-C', SRC, 'status', '--porcelain'],
                           capture_output=True, text=True).stdout.strip()
    os.makedirs(FIG, exist_ok=True)
    for f in os.listdir(FIG):
        q = os.path.join(FIG, f)
        shutil.rmtree(q) if os.path.isdir(q) else os.remove(q)
    for f in files():
        src = os.path.join(SRC, f)
        if not os.path.exists(src):
            raise SystemExit('원본에 없음: %s' % f)
        shutil.copy2(src, os.path.join(FIG, f))
    os.makedirs(os.path.join(FIG, 'assets'), exist_ok=True)
    for f in ASSET_FILES:
        q = os.path.join(SRC, 'assets', f)
        if os.path.exists(q):
            shutil.copy2(q, os.path.join(FIG, 'assets', f))
    for d in ASSET_DIRS:
        q = os.path.join(SRC, 'assets', d)
        if os.path.isdir(q):
            shutil.copytree(q, os.path.join(FIG, 'assets', d))
    print('동기화 %d화면 · 원본 HEAD %s%s' % (len(files()), head, ' (워킹트리 변경분 포함)' if dirty else ''))
    for line in patch_css():
        print('  패치 ' + line)
    if HOLD:
        print('  보류 제외: ' + ', '.join(HOLD))
    return head


# ---------------------------------------------------------------- measure
PROBE = """<!doctype html><meta charset="utf-8"><body style="margin:0">
<script>
const files=%s;let i=0;
function done(){new Image().src='/MEASDONE.gif?t='+Date.now();}
function next(){
 if(i>=files.length){setTimeout(done,300);return;}
 const f=files[i++];
 const fr=document.createElement('iframe');
 fr.style.cssText='width:1440px;height:1800px;border:0;position:absolute;left:-9999px';
 fr.src=f+'.html';
 fr.onload=function(){
  let payload='ERR';
  try{const d=fr.contentDocument;
   const ins=[...d.querySelectorAll('input[value]')].map(function(el){
    const r=el.getBoundingClientRect();
    return Math.round(r.width*100)/100+','+Math.round(r.height*100)/100;});
   payload=ins.join('|');
  }catch(e){}
  new Image().src='/MEAS_'+encodeURIComponent(f)+'_'+encodeURIComponent(payload)+'_x.gif?t='+Date.now();
  fr.remove();setTimeout(next,120);
 };
 fr.onerror=function(){fr.remove();setTimeout(next,120);};
 document.body.appendChild(fr);
}
setTimeout(next,900);
</script></body>"""


def measure():
    probe = os.path.join(FIG, '_measprobe.html')
    open(probe, 'w', encoding='utf-8').write(PROBE % json.dumps(IMPORT))
    log = os.path.join(FIG, '_meas.log')
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(PORT)], cwd=FIG,
                           stdout=open(log, 'w'), stderr=subprocess.STDOUT)
    prof = '/tmp/_prepfig_meas'
    shutil.rmtree(prof, ignore_errors=True)
    time.sleep(1.5)
    ch = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    br = subprocess.Popen([ch, '--headless=new', '--disable-gpu', '--no-first-run',
                           '--no-default-browser-check', '--hide-scrollbars', '--lang=ko-KR',
                           '--user-data-dir=' + prof, '--window-size=1440,1800',
                           'http://localhost:%d/_measprobe.html' % PORT],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t0 = time.time()
    while time.time() - t0 < 120:
        time.sleep(2)
        if 'MEASDONE' in open(log, encoding='utf-8', errors='ignore').read():
            break
    br.kill(); srv.kill(); time.sleep(0.5)
    raw = open(log, encoding='utf-8', errors='ignore').read()
    shutil.rmtree(prof, ignore_errors=True)
    os.remove(probe)

    meas = {}
    for name, payload in re.findall(r'MEAS_([^_\s]+)_(\S*?)_x\.gif', raw):
        name = urllib.parse.unquote(name); payload = urllib.parse.unquote(payload)
        if payload == 'ERR':
            raise SystemExit('측정 실패: %s' % name)
        ins = []
        if payload:
            for pair in payload.split('|'):
                w, h = pair.split(',')
                ins.append({'w': float(w), 'h': float(h)})
        meas[name + '.html'] = {'ins': ins}
    os.remove(log)
    missing = [f for f in files() if f not in meas]
    if missing:
        raise SystemExit('미측정 화면: %s' % ', '.join(missing))
    json.dump(meas, open(MEAS_PATH, 'w'), ensure_ascii=False, indent=1)
    tot = sum(len(v['ins']) for v in meas.values())
    sc = sum(1 for v in meas.values() if v['ins'])
    print('측정 %d필드 / %d화면 (전체 %d화면) → %s' % (tot, sc, len(meas), MEAS_PATH))
    for f in files():
        n = len(meas[f]['ins'])
        if n:
            print('  %-34s %d' % (f, n))
    return meas


# ---------------------------------------------------------------- apply
def disp_date(v):
    y, m, d = v.split('-')
    return '%s. %s. %s.' % (y, m, d)


def apply():
    meas = json.load(open(MEAS_PATH))
    log = []
    for f in files():
        p = os.path.join(FIG, f)
        s = open(p, encoding='utf-8').read()

        # A. 폰트 링크 — 대체 렌더 방지. display=block 이라 로드 전 렌더를 막는다.
        if 'family=Roboto+Mono' not in s:
            s = s.replace('</head>', '  ' + FONTLINK + '\n</head>', 1)
        # B. capture.js
        if 'html-to-design/capture.js' not in s:
            s = s.replace('</head>', '  ' + CAP + '\n</head>', 1)

        # C. value 필드 → 동일 스타일 텍스트 노드
        geo = meas.get(f, {}).get('ins', [])
        if geo:
            idx = [0]

            def sub(m):
                tag = m.group(0)
                a = dict(ATTR.findall(tag))
                g = geo[idx[0]]; idx[0] += 1
                val = a.get('value', '')
                t = a.get('type', 'text')
                if t == 'date':
                    inner = '<span>%s</span>%s' % (disp_date(val), CAL)
                    extra = 'justify-content:space-between;gap:8px;'
                elif t == 'password':
                    inner = '&bull;' * len(val)
                    extra = ''
                else:
                    inner = val
                    extra = ''
                st = (a.get('style', '') or '').rstrip(';')
                if st:
                    st += ';'
                st += ('display:inline-flex;align-items:center;box-sizing:border-box;'
                       'width:%gpx;height:%gpx;white-space:nowrap;overflow:hidden;%s' % (g['w'], g['h'], extra))
                out = '<span class="%s" style="%s" data-fig-input="%s">%s</span>' % (a.get('class', ''), st, t, inner)
                log.append((f, t, val, '%gx%g' % (g['w'], g['h'])))
                return out

            s = INPUT.sub(sub, s)
            if idx[0] != len(geo):
                raise SystemExit('%s 필드 수 불일치 %d != %d — measure 재실행 필요' % (f, idx[0], len(geo)))
        open(p, 'w', encoding='utf-8').write(s)

    print('치환 %d필드 / %d화면 · 폰트 링크·capture.js %d화면 주입'
          % (len(log), len(set(x[0] for x in log)), len(files())))
    for r in log:
        print('  ' + ' | '.join(r))


# ---------------------------------------------------------------- verify
def verify():
    """스테이징 사본이 캡처 준비 상태인지 확인."""
    ok = True
    bad = [f for f in files() if 'family=Roboto+Mono' not in open(os.path.join(FIG, f), encoding='utf-8').read()]
    print('폰트 링크 누락 %d건 %s' % (len(bad), bad or ''))
    ok &= not bad
    bad = [f for f in files() if 'html-to-design/capture.js' not in open(os.path.join(FIG, f), encoding='utf-8').read()]
    print('capture.js 누락 %d건 %s' % (len(bad), bad or ''))
    ok &= not bad
    s = open(os.path.join(FIG, 'assets', 'base.css'), encoding='utf-8').read()
    m = re.search(r'--font-mono:\s*([^;]+);', s)
    print('base.css --font-mono = %s' % (m.group(1) if m else '없음'))
    ok &= bool(m) and 'Roboto Mono' in m.group(1)
    s = open(os.path.join(FIG, 'assets', 'sheet.css'), encoding='utf-8').read()
    n = len(re.findall(r'text-overflow:\s*ellipsis', s))
    print('sheet.css 잔여 말줄임 %d건' % n)
    ok &= n == 0
    left = [f for f in files() if INPUT.search(open(os.path.join(FIG, f), encoding='utf-8').read())]
    print('미치환 value input %d건 %s' % (len(left), left or ''))
    ok &= not left
    print('판정: %s' % ('통과' if ok else '미통과'))
    return ok


# ---------------------------------------------------------------- 게이트·측정
def _probe(page_html, token, wait=60, vh=1800):
    """_fig 를 8903 에 띄우고 헤드리스로 열어 비컨을 회수한다."""
    probe = os.path.join(FIG, '_p.html')
    open(probe, 'w', encoding='utf-8').write(page_html)
    log = os.path.join(FIG, '_p.log')
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(PORT)], cwd=FIG,
                           stdout=open(log, 'w'), stderr=subprocess.STDOUT)
    prof = '/tmp/_prepfig_probe'
    shutil.rmtree(prof, ignore_errors=True)
    time.sleep(1.5)
    ch = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    br = subprocess.Popen([ch, '--headless=new', '--disable-gpu', '--no-first-run',
                           '--no-default-browser-check', '--hide-scrollbars', '--lang=ko-KR',
                           '--user-data-dir=' + prof, '--window-size=1440,%d' % vh,
                           'http://localhost:%d/_p.html' % PORT],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t0 = time.time()
    while time.time() - t0 < wait:
        time.sleep(2)
        if token in open(log, encoding='utf-8', errors='ignore').read():
            break
    br.kill(); srv.kill(); time.sleep(0.5)
    raw = open(log, encoding='utf-8', errors='ignore').read()
    shutil.rmtree(prof, ignore_errors=True)
    os.remove(probe); os.remove(log)
    return raw


FONTPROBE = """<!doctype html><meta charset="utf-8">""" + FONTLINK + """
<link rel="stylesheet" href="assets/base.css">
<body><span id="t" style="font-family:var(--font-mono);font-size:14px">%s</span>
<span id="r" style="font-family:'Roboto Mono';font-size:14px">%s</span>
<script>
function W(id){var r=document.createRange();r.selectNodeContents(document.getElementById(id));
 return Math.round(r.getBoundingClientRect().width*100)/100;}
function go(t){new Image().src='/GATE-'+t+'-check'+document.fonts.check('14px \"Roboto Mono\"')+
 '-stack'+W('t')+'-roboto'+W('r')+'-x.gif?q='+Date.now();}
setTimeout(function(){go('d1200')},1200);
document.fonts.ready.then(function(){go('ready')});
</script></body>""" % ('0' * 50, '0' * 50)


def fontgate():
    """캡처 배치 직전 게이트. --font-mono 가 Roboto Mono 로 해석되는지 실측.
    50자 기준 Roboto Mono 420.08 / Menlo 421.44 로 갈린다."""
    raw = _probe(FONTPROBE, 'GATE-', wait=45, vh=800)
    hits = re.findall(r'GATE-(\w+)-check(\w+)-stack([\d.]+)-roboto([\d.]+)-x', raw)
    if not hits:
        print('게이트 실패 — 비컨 회수 0건. CDN 도달 또는 헤드리스 실행 확인 필요')
        return False
    ok = True
    for tag, chk, stack, robo in hits:
        good = chk == 'true' and abs(float(stack) - float(robo)) < 0.5
        print('  %-6s fonts.check=%s  stack=%s  robotomono=%s  %s'
              % (tag, chk, stack, robo, '일치' if good else '불일치'))
        ok &= good
    print('폰트 게이트: %s' % ('통과' if ok else '미통과 — 캡처 금지'))
    return ok


HEIGHTPROBE = """<!doctype html><meta charset="utf-8"><body style="margin:0">
<script>
const files=%s;let i=0;
function next(){
 if(i>=files.length){setTimeout(function(){new Image().src='/HDONE.gif?q='+Date.now()},300);return;}
 const f=files[i++];
 const fr=document.createElement('iframe');
 fr.style.cssText='width:1440px;height:200px;border:0;position:absolute;left:-9999px';
 fr.src=f+'.html';
 fr.onload=function(){
  let h=0,sb=0;
  try{const d=fr.contentDocument;
   h=Math.max(d.documentElement.scrollHeight,d.body.scrollHeight);
   const s=d.querySelector('.sidebar');
   if(s){const keep=s.style.height;s.style.height='auto';sb=s.scrollHeight;s.style.height=keep;}
  }catch(e){h=-1;}
  new Image().src='/H_'+encodeURIComponent(f)+'_'+h+'_'+sb+'_x.gif?q='+Date.now();
  fr.remove();setTimeout(next,100);
 };
 fr.onerror=function(){fr.remove();setTimeout(next,100);};
 document.body.appendChild(fr);
}
setTimeout(next,900);
</script></body>"""

HEIGHTS_PATH = os.path.join(BASE, 'fig_heights.json')


def heights():
    """캡처 직전 프레임 높이 산출. 프레임 높이 = max(문서 높이, 사이드바 높이).
    사이드바는 position:fixed · height:100% 라 문서 높이에 안 잡히고 뷰포트를 그대로
    따라간다. 측정 때만 height:auto 로 풀어 고유 콘텐츠 높이를 읽는다(≈533).
    사이드바가 없는 login·index 는 이 바닥이 붙지 않는다."""
    raw = _probe(HEIGHTPROBE % json.dumps(IMPORT), 'HDONE', wait=120)
    out = {}
    for name, h, sb in re.findall(r'H_([^_\s]+)_(-?\d+)_(\d+)_x', raw):
        name = urllib.parse.unquote(name)
        h, sb = int(h), int(sb)
        if h < 0:
            raise SystemExit('높이 측정 실패: %s' % name)
        out[name] = {'content': h, 'sidebar': sb, 'vh': max(h, sb)}
    missing = [n for n in IMPORT if n not in out]
    if missing:
        raise SystemExit('미측정: %s' % ', '.join(missing))
    json.dump(out, open(HEIGHTS_PATH, 'w'), ensure_ascii=False, indent=1)
    print('높이 측정 %d화면 → %s' % (len(out), HEIGHTS_PATH))
    for n in IMPORT:
        v = out[n]
        print('  %-32s vh=%-6d (문서 %d · 사이드바 %d)' % (n, v['vh'], v['content'], v['sidebar']))
    return out


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if cmd == 'sync':
        sync()
    elif cmd == 'measure':
        measure()
    elif cmd == 'apply':
        apply()
    elif cmd == 'verify':
        sys.exit(0 if verify() else 1)
    elif cmd == 'fontgate':
        sys.exit(0 if fontgate() else 1)
    elif cmd == 'heights':
        heights()
    elif cmd == 'all':
        sync(); measure(); apply(); print(); verify()
    else:
        raise SystemExit(__doc__)
