# -*- coding: utf-8 -*-
"""투자 시뮬레이션 기대값 산출기 — verify_sim.js 가 읽는 sim_facts.json 을 만든다.

왜 있나
    verify_sim.js 는 시뮬레이션 결과를 화면에서 읽어 대조한다. 그 기대값 30여 곳이
    build_app.py 의 씨앗 8행(simSeedRows)과 기본 변수(SIM_DEFAULT)에 맞춰 손으로 계산돼
    검증기 안에 박혀 있었다. 씨앗이 바뀌면 전부 어긋난다 — 검증기가 옛 값을 지키느라
    새 값을 틀렸다고 하는 자리다.

    그래서 기대값을 검증기 밖으로 뺀다. 씨앗은 build_app.py 에서 읽고(build_sim_static.py:39-52
    가 이미 쓰는 정규식 방식 그대로), 산식도 build_sim_static.py 의 run() 을 그대로 부른다.
    씨앗 한 곳만 고치면 이 파일의 산출이 따라 움직이고, 검증기는 그 산출을 읽기만 한다.

    검증기가 스스로 계산하지 않게 하는 것이 요점이다. 검증기 안에서 계산하면 대상과 같은
    실수를 반복해 통과시킨다. 계산은 여기서 하고, 검증기는 화면 글자와 이 파일을 맞대기만 한다.

산식의 출처
    build_sim_static.py 의 bond()/run() — 대표 정의서 [1번] Ai·Di·W·Ty·S,
    [2번] Mi·Bi·PSA·PSM·PSD·PSMR·PSC. build_app.py 의 simBond()/simRun() 과 같은 규칙이고,
    두 구현이 어긋나면 verify_sim.js 의 `낱장 = 통합본` 대조에서 잡힌다.

시나리오
    검증기가 실제로 조작하는 입력 변경을 그대로 이름 붙여 담는다.
      base       기본값 실행
      rate022    할인율 0.11 → 0.22
      cash200m   순현금 → 2억
      unpaid005  미지급률 0.08 → 0.05
      unpaid020  미지급률 0.08 → 0.20 (S > 할인율 → 투자수익 음수)
      to0831     종료일 → 2026-08-31
      from0825   시작일 → 2026-08-25
      amt800m    1행 순지급액 → 8억

    실행:  python3 sim_facts.py     →  sim_facts.json
"""
import io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# build_sim_static 은 씨앗·기본변수를 build_app.py 에서 읽고 산식을 들고 있다.
# import 만으로는 낱장을 쓰지 않는다(main() 가드가 있다).
import build_sim_static as B

# 통합본 SIM_DEFAULT 의 날짜 두 개는 build_sim_static 이 문자열로 따로 들고 있다.
# 같은 값인지 여기서 확인한다 — 두 곳이 갈리면 기대값이 어느 쪽 기간인지 알 수 없다.
_SRC = io.open(os.path.join(HERE, 'build_app.py'), encoding='utf-8').read()
_DEF = re.search(r'var SIM_DEFAULT = \{(.*?)\};', _SRC, re.S).group(1)
_FROM = re.search(r"from:'([\d-]+)'", _DEF).group(1)
_TO   = re.search(r"to:'([\d-]+)'", _DEF).group(1)
assert (_FROM, _TO) == (B.FROM, B.TO), (_FROM, _TO, B.FROM, B.TO)

# 플랫폼 만기도 통합본에서 읽는다 — 새 행 기본값(종료일 - 카드 만기)과 만기 재계산에 쓴다.
_DUR = dict((k, int(v)) for k, v in re.findall(
    r"(\w+):(\d+)", re.search(r'var SIM_DUR = \{(.*?)\};', _SRC).group(1)))
assert set(_DUR) == {'card', 'bm', 'cpe', 'yo'}, _DUR
assert [_DUR[k] for k, _, d in B.PLAT] == [d for _, _, d in B.PLAT], (_DUR, B.PLAT)

_KEYS = ('R_RATE', 'CASH', 'UNPAID', 'OVER', 'FROM', 'TO', 'ROWS')

# ── 시나리오 = 검증기가 화면에 넣는 입력 그 자체 ───────────────────
#   var  기준 변수 칸(data-act=sim-var, data-k) 에 넣는 값
#   row  채권 입력 한 행(data-act=sim-row, data-i·data-f) 에 넣는 값
#   기대값도 같은 표에서 계산한다 — 검증기가 넣는 값과 기대값이 갈릴 자리를 없앤다.
SCENARIOS = {
    'rate022':   {'var': 'r',      'value': '0.22'},
    'cash200m':  {'var': 'cash',   'value': '200000000'},
    'unpaid005': {'var': 'unpaid', 'value': '0.05'},
    'unpaid020': {'var': 'unpaid', 'value': '0.20'},
    'to0831':    {'var': 'to',     'value': '2026-08-31'},
    'from0825':  {'var': 'from',   'value': '2026-08-25'},
    'amt800m':   {'row': 0, 'field': 'amt', 'value': '800000000'},
}
# 화면 입력 이름 → build_sim_static 전역 이름·형변환
_VARMAP = {'r': ('R_RATE', float), 'cash': ('CASH', int), 'unpaid': ('UNPAID', float),
           'over': ('OVER', float), 'from': ('FROM', str), 'to': ('TO', str)}


def _override(sc, rows):
    """시나리오 한 줄 → run() 에 넣을 전역 덮어쓰기."""
    if 'var' in sc:
        k, cast = _VARMAP[sc['var']]
        return {k: cast(sc['value'])}
    i, f = sc['row'], sc['field']
    r = list(rows[i])
    r[{'plat': 0, 'amt': 1, 'sd': 2, 'dd': 3}[f]] = int(sc['value']) if f == 'amt' else sc['value']
    return {'ROWS': rows[:i] + [tuple(r)] + rows[i + 1:]}


def scenario(**over):
    """build_sim_static 의 전역을 잠깐 갈아 끼우고 그 파일의 run() 을 그대로 부른다.

    산식을 여기에 다시 적지 않는다 — 적으면 구현이 셋이 되고, 셋이 어긋날 자리가 생긴다."""
    save = dict((k, getattr(B, k)) for k in _KEYS)
    try:
        for k, v in over.items():
            assert k in _KEYS, k
            setattr(B, k, v)
        return B.run()
    finally:
        for k, v in save.items():
            setattr(B, k, v)


def snap(R, cash):
    """화면에 찍히는 글자 그대로. 검증기는 이 문자열과 DOM 텍스트를 맞대기만 한다."""
    f, fx, pct = B.fmt, B.fx, B.pct
    bonds = R['bonds']
    b0 = bonds[0]
    return {
        # ── 현황 표 3행 ──
        'exec':      f(R['EXEC']),
        'w':         fx(R['W'], 2) + '일',
        's':         pct(R['S'], 2),
        'ty':        pct(R['TY'], 2),
        'share0':    fx(R['SH'][0], 1) + '%',
        'cash':      f(cash),
        'share1':    fx(R['SH'][1], 1) + '%',
        'total':     f(R['TOT']),
        'shareSum':  fx(R['SH'][0] + R['SH'][1], 1) + '%',
        # ── 요약 카드 4장 ──
        'cardTotal': f(R['TOT']) + '원',
        'cardExec':  f(R['EXEC']) + '원',
        'cardCash':  f(cash) + '원',
        'cardTy':    fx(R['TY'], 2) + '%',
        'cardTySub': 'W금융일수 ' + fx(R['W'], 2) + '일 기준',
        # ── 수익 현황 · 일별 합계 ──
        'psa':       f(R['PSA']),
        'psm':       f(R['PSM']),
        'psb':       R['PSB'],
        'psbText':   f(R['PSB']),
        'psd':       fx(R['PSD'], 2),
        'ty4':       fx(R['TY4'], 2),
        'ty4pct':    pct(R['TY4'], 2),
        'ty5':       fx(R['TY5'], 2),
        'ecd':       str(R['ECD']) + '일',
        # ── 일별 표 ──
        'dailyDates': [g['d'] for g in R['rows']],
        # ── 채권별 산출 ──
        'bondKinds': [b['kind'] for b in bonds],
        'bond0': ['1', b0['kind'], B.LABEL[b0['plat']], f(b0['amt']), str(b0['D']),
                  f(b0['A']), f(b0['fee']), f(b0['ded']), f(b0['M']), f(b0['B'])],
        'bond0A':   f(b0['A']),
        'bond0fee': f(b0['fee']),
        'bond0ded': f(b0['ded']),
        'bond0M':   f(b0['M']),
    }


def rows_total(rows):
    return '총 %d건, 합계 %s원' % (len(rows), B.fmt(sum(a for _, a, _, _ in rows)))


def add_days(d, n):
    return B._d(d).__class__.fromordinal(B._d(d).toordinal() + n).isoformat()


def facts():
    rows = list(B.ROWS)
    base = scenario()
    # `+ 채권 추가` 기본값 — build_app.py ACT['sim-add'] 와 같은 규칙(종료일 - 카드 만기 ~ 종료일)
    add_sd = add_days(B.TO, -_DUR['card'])
    add_rows = rows + [('card', 100000000, add_sd, B.TO)]
    out = {
        'seedSource': 'build_app.py simSeedRows() · SIM_DEFAULT · SIM_DUR',
        'defaults': {'rate': B.R_RATE, 'cash': B.CASH, 'unpaid': B.UNPAID, 'over': B.OVER,
                     'from': B.FROM, 'to': B.TO},
        'scenarios': SCENARIOS,
        'platDur': _DUR,
        'seedRows': len(rows),
        'seedTotalText': rows_total(rows),
        'seedDays': [str(B.days(sd, dd)) + '일' for _, _, sd, dd in rows],
        # 1행 선정산일 기준으로 플랫폼을 갈아 끼웠을 때 다시 채워지는 정산예정일·금융일수
        'row0Sd': rows[0][2],
        'platDue': dict((k, add_days(rows[0][2], _DUR[k])) for k in _DUR),
        'platDays': [str(_DUR[k]) + '일' for k, _, _ in B.PLAT],
        'addRow': {'plat': 'card', 'amt': '100000000', 'sd': add_sd, 'dd': B.TO,
                   'days': str(_DUR['card']) + '일', 'totalText': rows_total(add_rows),
                   'rows': len(add_rows)},
        'period': B.FROM + ' ~ ' + B.TO,
        # 실행 버튼을 막아야 하는 입력 — 기대값이 아니라 조작값이지만 씨앗 기간에 매여 있어
        # 여기서 낸다. badFrom 은 종료일보다 뒤, badDue 는 1행 선정산일보다 앞이어야 한다.
        'badFrom': add_days(B.TO, 14),
        'badDue':  add_days(rows[0][2], -6),
        'base': snap(base, B.CASH),
    }
    for name, sc in SCENARIOS.items():
        ov = _override(sc, rows)
        out[name] = snap(scenario(**ov), ov.get('CASH', B.CASH))
        out[name]['rowsTotalText'] = rows_total(ov.get('ROWS', rows))
        out[name]['period'] = ov.get('FROM', B.FROM) + ' ~ ' + ov.get('TO', B.TO)
    return out


def dump(path=None):
    path = path or os.path.join(HERE, 'sim_facts.json')
    io.open(path, 'w', encoding='utf-8').write(
        json.dumps(facts(), ensure_ascii=False, indent=1))
    return path


if __name__ == '__main__':
    # --json  기대값을 표준출력으로만 낸다. verify_sim.js 가 이 모드로 불러 매번 새로 받는다 —
    #         파일이 낡아 옛 기대값을 지키는 자리를 만들지 않는다.
    if '--json' in sys.argv:
        out = json.dumps(facts(), ensure_ascii=False)
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout.buffer.write(out.encode('utf-8'))
        else:
            sys.stdout.write(out)
        sys.exit(0)
    F = facts()
    b = F['base']
    print('씨앗 %d행 · %s' % (F['seedRows'], F['seedTotalText']))
    print('기본값 실행 — 투자실행액 %s · W %s · S %s · Ty %s · 비중 %s / %s (합 %s)'
          % (b['exec'], b['w'], b['s'], b['ty'], b['share0'], b['share1'], b['shareSum']))
    print('           투자자산 %s · PSA %s · PSM %s · PSB %s · PSD %s · ④ %s · ⑤ %s'
          % (b['total'], b['psa'], b['psm'], b['psbText'], b['psd'], b['ty4'], b['ty5']))
    print('           채권 구분 %s' % ' '.join(b['bondKinds']))
    print('           1행 %s' % ' / '.join(b['bond0']))
    for k in ('rate022', 'cash200m', 'unpaid005', 'unpaid020', 'to0831', 'from0825', 'amt800m'):
        s = F[k]
        print('  %-10s 실행 %15s  S %6s  Ty %7s  PSM %12s  구분 %s'
              % (k, s['exec'], s['s'], s['ty'], s['psm'], ''.join(x[0] for x in s['bondKinds'])))
    print('기대값 → %s' % dump())
