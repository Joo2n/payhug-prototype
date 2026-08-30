# -*- coding: utf-8 -*-
"""README.md 생성기 — 개수·화면 목록·상태 목록을 전부 실측에서 뽑는다.

손으로 적은 개수는 화면이 하나 늘 때마다 낡는다(D-38). 파일 수·화면 수·상태 수·메뉴 수는
counts.py 와 저장소 실측이 정하고, 문장은 여기 원고만 갖는다.

  python3 build_readme.py            README.md 를 다시 쓴다
  python3 build_readme.py --check    실측과 어긋나면 종료코드 1
"""
import io, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import counts

REPO = counts.REPO
OUT = os.path.join(REPO, 'README.md')

DEMO = 'https://payhug-investor-demo.vercel.app/'
PROTO = 'https://payhug-investor-prototype.vercel.app/'
GLOSS = 'https://payhug-investor-glossary.vercel.app/'

# 사이드바 메뉴 → 낱장 파일. 라벨은 counts.menu_groups() 실측을 쓰고 여기는 파일만 잇는다.
MENU_FILE = {
    '투자 자산': 'invest-assets', '투자 수익': 'invest-profit', '투자 시뮬레이션': 'invest-sim',
    '가맹점': 'merchants', '정산채권 양수': 'acquisition', '계약기록': 'contracts',
    '쿠콘 관리 현금': 'coocon', '비밀번호 변경': 'password',
}
# 메뉴에 안 걸린 화면
SUB_NAME = {
    'certificate': '투자자산 증명서', 'login': '로그인',
    'xls-assets-status': '엑셀 산출물 서식 — 투자자산 현황',
    'xls-assets-merchant': '엑셀 산출물 서식 — 가맹점별 투자자산',
    'xls-profit-status': '엑셀 산출물 서식 — 투자수익 현황',
    'xls-profit-daily': '엑셀 산출물 서식 — 일별 투자수익',
}
ASSET_NOTE = {
    'base.css': '공용 스타일 (실측 토큰: 사이드바 #1B2537, primary #7FE141 등)',
    'sheet.css': '엑셀 미리보기 전용 (xls-*.html · app.html에서 로드)',
    'template.html': '화면 스켈레톤. 사이드바 메뉴 실측 원본',
    'logo-icon.png': '로고 원본. 화면 렌더는 base.css의 .logo-mark data URI',
}
DOC_NAME = {
    'glossary.html': '용어 해설 — 용어 50건 · 화면 캡처 위치 표시',
    'capability.html': '산출물이 무엇을 말할 수 있나',
    'feasibility.html': '구현 가능성 — 개발 확인 문항',
    'inquiry.html': '대표 확인 요청 — 문항 5건',
    'review.html': '검토 이력',
    'archive.html': '파일 아카이브 — 산출물·파이프라인 전량 목록',
}
# (원 화면, 버튼, 파일 앞머리, Figma 전용 서식 화면)
XLS_BTN = [
    ('투자 자산', '엑셀 다운로드 (현황)', '투자자산현황', 'xls-assets-status.html'),
    ('투자 자산', '엑셀 다운로드 (가맹점별)', '가맹점별투자자산', 'xls-assets-merchant.html'),
    ('투자 수익', '수익 현황 엑셀 다운로드 — 집계 단위 일별·주별·월별', '투자수익현황', 'xls-profit-status.html'),
    ('투자 수익', '표 엑셀 다운로드 — 집계 단위 일별·주별·월별', '별투자수익', 'xls-profit-daily.html'),
]


def tracked():
    # -z · quotepath=false — 한글 파일명이 "..." 로 감싸져 나오면 경로 앞머리 비교가 다 빗나간다
    out = subprocess.run(['git', '-c', 'core.quotepath=false', 'ls-files', '-z'],
                         cwd=REPO, capture_output=True, text=True, check=True)
    return [l for l in out.stdout.split('\0') if l]


def facts():
    """저장소 실측 — 배포에 실려 나가는 파일을 갈래별로 센다."""
    fs = tracked()
    root_html = sorted(f for f in fs if f.endswith('.html') and '/' not in f)
    docs = [f for f in root_html if f in counts.DOCS and f != 'index.html']
    states = [f for f in root_html if '--' in f]
    screens = [f for f in root_html if f not in counts.DOCS and '--' not in f and f != 'app.html']
    assert len(screens) + 1 == counts.C['screens'], (len(screens), counts.C['screens'])
    assert len(states) == counts.C['states'], (len(states), counts.C['states'])
    d = lambda p: [f for f in fs if f.startswith(p)]
    # 캡처는 용어 카드가 거는 화면만 둔다(부르는 문서가 없던 10장은 2026-08-29 에 걷어냈다).
    # 몇 장을 부르는지는 배포 HTML 을 훑어 센다 — 손으로 적으면 마커가 옮겨갈 때마다 낡는다.
    shots = [os.path.basename(f) for f in d('assets/shots/')]
    html_all = ''.join(io.open(os.path.join(REPO, f), encoding='utf-8').read() for f in root_html)
    # 확장자 나열도 실측이다. 손으로 적으면 없는 형식(ZIP)이 안내에 남는다.
    ext = lambda p: sorted({os.path.splitext(f)[1][1:].upper() for f in d(p)} - {''})
    return dict(
        docExt=ext('assets/docs/'),
        dlExt=sorted(set(ext('assets/docs/')) | set(ext('assets/xlsx/'))),
        assetCommonNames=sorted(os.path.basename(f) for f in d('assets/') if f.count('/') == 1),
        shotsUsed=len([x for x in shots if x in html_all]),
        appStates=counts.app_states(),
        all=len(fs), rootHtml=len(root_html), rootDoc=len([f for f in fs if f.endswith('.md')]),
        docs=docs, states=states, screens=screens,
        assetCommon=len([f for f in d('assets/') if f.count('/') == 1]),
        assetDocs=len(d('assets/docs/')), assetXlsx=len(d('assets/xlsx/')),
        assetShots=len(d('assets/shots/')), scripts=len(d('scripts/')),
        wf=len(d('.github/')),
        xlsx=sorted(os.path.basename(f) for f in d('assets/xlsx/')))


def states_of(stem, F):
    return [f[len(stem) + 2:-5] for f in F['states'] if f.startswith(stem + '--')]


def build():
    F = facts()
    C = counts.C
    menus = [m for _, ms in C['menuGroups'] for m in ms]
    n_menu_screen = len(menus)
    n_sub = len(F['screens']) - n_menu_screen
    o = []
    W = o.append

    W('# PayHug 투자자 어드민 — 화면 설계(안)')
    W('')
    W('투자자용 어드민 UI 기획 목업. 실제 운영 어드민(payhug-admin-web)의 디자인시스템을 실측해 동일한 UI 문법으로 제작.')
    W('')
    W('## 공개 주소')
    W('')
    W('| 주소 | 내용 |')
    W('|---|---|')
    W('| %s | 저장소 전량. 통합 프로토타입·낱장·설명 문서·내려받기 실물이 모두 이 주소에서 열린다 |' % DEMO)
    W('| %s | 시연본. `app.html` 한 판만, 바깥으로 나가는 통로 없음 |' % PROTO)
    W('| %s | 용어 해설 단독본 |' % GLOSS)
    W('')
    W('전체본은 `main` 에 올라간 %d개 파일을 그대로 서비스한다. 한글 이름을 쓰는 %s 도 같은 주소에서 바로 열린다.'
      % (F['all'] - F['wf'], '·'.join(F['dlExt'])))
    W('')
    W('| 구획 | 수 | 내역 |')
    W('|---|---|---|')
    W('| 루트 HTML | %d | 통합 프로토타입 1 · 기본 화면 %d · 상태 %d · 랜딩 1 · 설명 문서 %d |'
      % (F['rootHtml'], len(F['screens']), len(F['states']), len(F['docs'])))
    W('| 루트 문서 | %d | `README.md` `DESIGN_REF.md` |' % F['rootDoc'])
    W('| `assets/` 공용 | %d | %s |'
      % (F['assetCommon'], ' '.join('`%s`' % n for n in F['assetCommonNames'])))
    W('| 내려받기 실물 | %d | `assets/docs/` %d · `assets/xlsx/` %d |'
      % (F['assetDocs'] + F['assetXlsx'], F['assetDocs'], F['assetXlsx']))
    W('| 화면 캡처 | %d | `assets/shots/` — 용어 해설 카드가 거는 화면 촬영본 %d장 |'
      % (F['assetShots'], F['shotsUsed']))
    W('| 동기화 스크립트 | %d | `scripts/` — 시연본·용어 단독본 변환기 |' % F['scripts'])
    W('')
    W('## 진입점')
    W('')
    W('| 파일 | 용도 |')
    W('|---|---|')
    W('| `index.html` | 랜딩. 통합 프로토타입 진입 + 화면·상태 전량 목록 |')
    W('| `app.html` | 통합 프로토타입. 화면 %d · 상태 %d 를 한 파일에서 조작. 메뉴 전환·엑셀 실제 내려받기·모달·검색·페이지네이션 동작. `#화면/상태` 해시 딥링크 |'
      % (len(F['screens']), F['appStates']))
    W('')
    W('개별 HTML은 Figma 네이티브 임포트용 정적 원본(1파일 = 1프레임)이고, `app.html`은 조작 가능한 프로토타입이다. 두 산출물은 역할이 다르며 서로를 대체하지 않는다.')
    W('')
    W('## 화면 목록')
    W('')
    W('### 사이드바 메뉴 대응 %d' % n_menu_screen)
    W('')
    W('| 파일 | 그룹 | 화면 | 상태 파일 |')
    W('|---|---|---|---|')
    for g, ms in C['menuGroups']:
        for m in ms:
            stem = MENU_FILE[m]
            st = states_of(stem, F)
            W('| `%s.html` | %s | %s | %s |'
              % (stem, g, m, ' '.join('`--%s`' % s for s in st) or '—'))
    W('')
    W('### 하위 화면 %d' % n_sub)
    W('')
    W('| 파일 | 화면 | 상태 파일 |')
    W('|---|---|---|')
    for stem in sorted(SUB_NAME):
        if stem + '.html' not in F['screens']:
            continue
        st = states_of(stem, F)
        W('| `%s.html` | %s | %s |'
          % (stem, SUB_NAME[stem], ' '.join('`--%s`' % s for s in st) or '—'))
    W('')
    W('상태 파일 이름 규칙은 `<화면>--<상태>.html`. `<화면>.html`은 항상 기본 상태다.')
    W('')
    W('`xls-*.html` %d종은 Figma 임포트 전용 서식이다. 화면 흐름의 진입점이 아니며, 엑셀 버튼은 미리보기를 거치지 않고 파일을 바로 내려준다.'
      % C['xlsPreview'])
    W('')
    W('상태 낱장 %d종은 전량이 랜딩·아카이브·구현 가능성 판정에 등재되고, 통합본이 태우는 상태 %d종과 같다. 배포에 실려 주소로 열리는 낱장을 목록 밖에 두지 않는다.'
      % (len(F['states']), F['appStates']))
    W('')
    W('### 설명 문서 %d' % len(F['docs']))
    W('')
    W('| 파일 | 내용 |')
    W('|---|---|')
    for f in F['docs']:
        W('| `%s` | %s |' % (f, DOC_NAME[f]))
    W('')
    W('## 구조')
    W('')
    W('```')
    W('├── index.html            # 랜딩 (통합본 진입 + 전량 목록)')
    W('├── app.html              # 통합 프로토타입')
    W('├── *.html                # 기본 화면 %d + 상태 %d + 설명 문서 %d'
      % (len(F['screens']), len(F['states']), len(F['docs'])))
    W('├── scripts/              # 시연본·용어 단독본 변환기')
    W('└── assets/')
    for nm in F['assetCommonNames']:
        W('    ├── %-18s# %s' % (nm, ASSET_NOTE.get(nm, '공용 자산')))
    W('    ├── docs/             # 내려받기 실물 %d (%s)'
      % (F['assetDocs'], ' · '.join(F['docExt'])))
    W('    ├── xlsx/             # 내려받기 실물 %d (XLSX)' % F['assetXlsx'])
    W('    └── shots/            # 화면 캡처 %d — 용어 해설이 거는 화면만 (부르는 것 %d)'
      % (F['assetShots'], F['shotsUsed']))
    W('```')
    W('')
    W('## 엑셀 다운로드 대응')
    W('')
    W('버튼을 누르면 중간 화면 없이 파일이 바로 내려온다 (원본 `ExcelDownloadButton` → `downloadExcel` 경로와 같다).')
    W('파일명은 원본 규칙 `{내용}_{시작일}_{종료일}.xlsx` · 날짜 `YYYY-MM-DD` 를 따른다. 투자자산 2종은 기준일 스냅샷이라 시작=종료다.')
    W('')
    W('| 원 화면 | 버튼 | 파일 | Figma 전용 서식 화면 |')
    W('|---|---|---|---|')
    for scr, btn, stem, fig in XLS_BTN:
        hit = [x for x in F['xlsx'] if stem in x]
        assert hit, '엑셀 실물 없음 — ' + stem
        W('| %s | %s | %s | `%s` |'
          % (scr, btn, ' · '.join('`assets/xlsx/%s`' % h for h in hit), fig))
    W('')
    _docs = os.listdir(os.path.join(REPO, 'assets/docs'))
    W('계약기록의 `선택 문서 다운로드`와 행별 문서 다운로드는 비활성이다 — 전자서명 결과물 파일 형식이 미결이라 실물을 만들지 않는다(`request_register.md` D-39). `assets/docs` 에는 `계약서보기`가 여는 계약서 원문 텍스트와 투자자산 증명서 PDF %d건만 둔다.'
      % len([f for f in _docs if f.endswith('.pdf')]))
    W('')
    W('## 참고')
    W('')
    W('- 표기 금액·요율·상호는 전부 예시. 화면에는 `예시`·`미확정` 류 고지를 두지 않는다(`request_register.md` D-22 · D-23).')
    W('- 투자 수익 화면은 일별 원장 하나만 갖고, 주별·월별 표는 그 원장을 주·달로 합쳐 만든다. 카드 5값(검색대상기간·투자실행금·투자수익·Ty수익율 2종)은 언제나 그 표의 합계와 같고, 같은 조회 기간이면 어느 집계 단위로 보든 값이 같다.')
    W('- 사이드바 메뉴 %d종: %s.' % (C['menus'], ' / '.join(menus)))
    W('- 사이드바는 투자자 메뉴만 둔다. 어드민 실메뉴를 병기하지 않는다 — 기존 어드민 사이드바 안의 한 뷰이되 겉모습은 투자자 메뉴만 두는 결정(`request_register.md` D-3 · D-35).')
    W('- 개수 서술은 실측 추종이다. 이 문서는 `_pipeline/investor_admin/build_readme.py` 가 `counts.py` 실측으로 생성한다(D-38).')
    W('- Figma: 서준 작업 공간 `[투자자 어드민]` 페이지(3066:328)에 동일 화면 네이티브 임포트.')
    W('')
    return '\n'.join(o)


if __name__ == '__main__':
    md = build()
    if '--check' in sys.argv:
        cur = io.open(OUT, encoding='utf-8').read()
        if cur != md:
            print('README.md 가 실측과 다르다 — build_readme.py 로 다시 쓴다')
            sys.exit(1)
        print('README.md 실측 일치')
    else:
        io.open(OUT, 'w', encoding='utf-8').write(md)
        F = facts()
        print('README.md 재생성 — 파일 %d · 루트 HTML %d · 화면 %d · 상태 %d · 메뉴 %d'
              % (F['all'], F['rootHtml'], len(F['screens']), len(F['states']), counts.C['menus']))
