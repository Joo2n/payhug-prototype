# -*- coding: utf-8 -*-
"""산출물 개수 실측 — 메뉴·화면·상태·엑셀.

문서에 개수를 손으로 적으면 화면이 하나 늘 때마다 낡는다(메뉴 7→8·화면 14→15·
상태 18→20·엑셀 4→6 이 실제로 그렇게 어긋났다). 세는 곳을 여기 하나로 모으고,
생성기는 import 해 쓰고 손으로 쓰는 문서는 sync_counts.py 가 여기 값으로 덮는다.

    python3 counts.py            실측값 출력 + counts.json 갱신
"""
import io, json, os, re

REPO = '/Users/semi/cursor/payhug-investor-admin'
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'counts.json')

# 랜딩·통합본에 등재하지 않는 낱장 — 커스텀 달력 열림 상태 전용이라 네이티브 input[type=date]
# 단독 통일로 폐기됐다. 파일만 남아 있어(용어 해설이 캡처를 참조) 화면 수에서 뺀다.
RETIRED = {'invest-profit--datepicker.html'}

# 화면이 아닌 문서 낱장
DOCS = {'index.html', 'glossary.html', 'capability.html',
        'feasibility.html', 'inquiry.html', 'review.html', 'archive.html'}


def _tpl():
    return io.open(os.path.join(REPO, 'assets/template.html'), encoding='utf-8').read()


def menu_groups():
    """사이드바 = (그룹명, [메뉴 라벨...]) — 스켈레톤 assets/template.html 실측."""
    out = []
    for blk in re.findall(r'<div class="nav-group".*?(?=<div class="nav-group"|</nav>)', _tpl(), re.S):
        g = re.search(r'<div class="nav-group-label">\s*<span>([^<]+)</span>', blk)
        items = re.findall(r'<a class="nav-item"[^>]*>.*?<span>([^<]+)</span>', blk, re.S)
        if g and items:
            out.append((g.group(1).strip(), [i.strip() for i in items]))
    return out


def _root_html():
    return [f for f in sorted(os.listdir(REPO)) if f.endswith('.html')]


def screen_files():
    """기본 화면 = 통합본 + 문서·상태·폐기분을 뺀 낱장."""
    return ['app.html'] + [f for f in _root_html()
                           if f not in DOCS and f != 'app.html' and '--' not in f]


def state_files():
    return [f for f in _root_html() if '--' in f and f not in RETIRED]


def counts():
    g = menu_groups()
    xd = os.path.join(REPO, 'assets', 'xlsx')
    ad = os.path.join(REPO, 'assets')
    c = dict(
        menus=sum(len(m) for _, m in g),
        menuGroups=[[k, v] for k, v in g],
        screens=len(screen_files()),
        states=len(state_files()),
        statesAll=len([f for f in _root_html() if '--' in f]),
        xlsx=len([f for f in os.listdir(xd) if f.endswith('.xlsx')]),
        xlsPreview=len([f for f in _root_html() if f.startswith('xls-')]),
        assetParts=len([f for f in os.listdir(ad) if f.endswith('.html')]))
    # 파생값 — 문서가 자주 쓰는 조합. 문서마다 손으로 더하지 않게 여기서 한 번만 만든다.
    c['screenFiles'] = c['screens'] - 1                       # 통합본을 뺀 낱장 화면
    c['kitHtml'] = c['screenFiles'] + c['states'] + c['assetParts']
    return c


C = counts()


def menu_sentence():
    """랜딩 카피의 메뉴 나열 — 그룹(메뉴 · 메뉴) / 그룹(...) 형식."""
    return ' / '.join('%s(%s)' % (k, ' · '.join(v)) for k, v in C['menuGroups'])


def dump(path=OUT):
    io.open(path, 'w', encoding='utf-8').write(json.dumps(C, ensure_ascii=False, indent=1))
    return path


if __name__ == '__main__':
    print('메뉴 %d · 화면 %d · 상태 %d · 엑셀 %d · 엑셀 미리보기 %d'
          % (C['menus'], C['screens'], C['states'], C['xlsx'], C['xlsPreview']))
    print('  ' + menu_sentence())
    print('  화면 ' + ', '.join(screen_files()))
    print('  사실값 → %s' % dump())
