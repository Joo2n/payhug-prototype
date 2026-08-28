# -*- coding: utf-8 -*-
"""app_spec.json `_meta.counts` 를 실측으로 덮는다.

사양 파일에 개수를 손으로 적으면 화면·상태가 늘거나 줄어도 그대로 남는다.
화면·상태·상호작용·결함은 사양 자신의 배열을 세고, 파일 수는 저장소를 센다(D-38).

    python3 sync_app_spec.py            덮어쓰기 + 결과 출력
    python3 sync_app_spec.py --check    맞는지만 본다 (틀리면 종료코드 1)
"""
import io, json, os, subprocess, sys
from collections import OrderedDict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import counts

SPEC = os.path.join(HERE, 'app_spec.json')
REPO = counts.REPO


def measured(spec):
    """사양 배열 + 저장소 파일에서 센다."""
    root = [f for f in sorted(os.listdir(REPO)) if f.endswith('.html')]
    assets = [f for f in sorted(os.listdir(os.path.join(REPO, 'assets'))) if f.endswith('.html')]
    sev = Counter(d['severity'] for d in spec['defects'])
    c = OrderedDict()
    c['htmlFilesRoot'] = len(root)
    c['htmlFilesAssets'] = len(assets)
    c['screens'] = len(spec['screens'])
    c['states'] = sum(len(s.get('states', [])) for s in spec['screens'])
    c['interactions'] = len(spec['interactions'])
    c['defects'] = OrderedDict((k, sev[k]) for k in ('H', 'M', 'L'))
    return c


def note(spec):
    """앞머리 낱장 수만 실측으로 갈아 끼운다 — 뒤 문장은 원문 그대로 둔다."""
    n = counts.C['screenFiles'] + counts.C['states']
    tail = spec['_meta']['note'].split('는 Figma 임포트용 원본', 1)[1]
    return '개별 HTML %d개는 Figma 임포트용 원본%s' % (n, tail)


def head_commit():
    r = subprocess.run(['git', '-C', REPO, 'rev-parse', '--short', 'HEAD'],
                       capture_output=True, text=True)
    return r.stdout.strip() or None


def build():
    spec = json.load(io.open(SPEC, encoding='utf-8'), object_pairs_hook=OrderedDict)
    spec['_meta']['counts'] = measured(spec)
    spec['_meta']['note'] = note(spec)
    hc = head_commit()
    if hc:
        spec['_meta']['sourceCommit'] = hc
    return json.dumps(spec, ensure_ascii=False, indent=1) + '\n'


if __name__ == '__main__':
    chk = '--check' in sys.argv
    new = build()
    cur = io.open(SPEC, encoding='utf-8').read()
    c = json.loads(new)['_meta']['counts']
    print('app_spec _meta — 화면 %d · 상태 %d · 상호작용 %d · 루트 HTML %d · 결함 %s'
          % (c['screens'], c['states'], c['interactions'], c['htmlFilesRoot'],
             '·'.join('%s%d' % (k, v) for k, v in c['defects'].items())))
    if cur == new:
        print('실측 일치')
        sys.exit(0)
    if chk:
        print('  ! app_spec.json — 실측과 다르다 (sync_app_spec.py 로 다시 쓴다)')
        sys.exit(1)
    io.open(SPEC, 'w', encoding='utf-8').write(new)
    print('  app_spec.json 실측으로 재기록')
