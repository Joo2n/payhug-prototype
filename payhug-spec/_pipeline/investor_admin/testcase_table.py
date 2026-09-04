#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""테스트 케이스 절 — 계산에 넣는 값 → 채권 1건 → 하루 합계 → 조회기간 합계 → 화면 표시값 대조.

값은 meeting_0901/testcase.json 에서 오고, 화면에 뜨는 값은 ledger_facts.json
에서 온다. 이 파일은 숫자를 손으로 적지 않는다.

비율·일수는 소수 일곱째 자리에서 반올림해 여섯째 자리까지 남기고 그 값을 다음
계산에 넣는다. 금액은 원 아래를 남기지 않고 한 줄로 낸다 —
dm_0901/rounding_rule_0901.md · 기호 정본 dm_0901/symbol_rule_0901.md
"""
import io
import json
import os
import re
from decimal import Decimal as D, ROUND_HALF_UP, getcontext

getcontext().prec = 60

PIPE = os.path.dirname(os.path.abspath(__file__))
TC = os.path.join(PIPE, 'meeting_0901', 'testcase.json')
FACTS = os.path.join(PIPE, 'ledger_facts.json')

TITLE = '테스트 케이스 — 골목냉면 카드사 채권 70건'


def _r6(x):
    return D(x).quantize(D('0.000001'), rounding=ROUND_HALF_UP)


def _r2(x):
    return D(x).quantize(D('0.01'), rounding=ROUND_HALF_UP)


def _n(x, p=0):
    return ('{:,.%df}' % p).format(D(x))


def _load():
    tc = json.load(io.open(TC, encoding='utf-8'))
    fx = json.load(io.open(FACTS, encoding='utf-8'))
    return tc, fx


def _rate(tc, key):
    """플랫폼 미지급률·과지급률 — testcase.json 산식 문장에서 읽는다."""
    m = re.search(r'([0-9.]+)%', tc['산식'][key])
    return (D(m.group(1)) / 100).normalize()


def _days(tc):
    """일별 7행 — 상환액은 원문 정의(순지급액 − max(0, L_i))로 낸다."""
    out = []
    for r in tc['daily']:
        m = r['재료']
        A, ded, net = D(r['A']), D(m['Σ차감']), D(m['Σ순지급액'])
        fee = D(m['Σ채권매입수수료'])
        M = fee - ded
        B = net - ded
        w6 = _r6(D(m['Σ(A_{i}×D_{i})']) / A)
        mr = M / A * 100
        ymr = _r6(mr * 365 / w6)
        out.append(dict(d=r['정산예정일'], n=r['건수'], A=A, M=M, B=B, net=net,
                        fee=fee, ded=ded, ax=D(m['Σ(A_{i}×D_{i})']),
                        unpaid=D(m['Σ미지급금']), over=D(m['Σ과지급금']),
                        w6=w6, mr=_r6(mr), ymr=ymr,
                        fee_each=D(m['Σ 건별 채권매입수수료'])))
    return out


def facts():
    """절이 쓰는 값 전부를 한 번에 낸다 — 검증기도 이 함수를 읽는다."""
    tc, fx = _load()
    dd = _days(tc)
    PA = sum(x['A'] for x in dd)
    PM = sum(x['M'] for x in dd)
    PB = sum(x['B'] for x in dd)
    NET = sum(x['net'] for x in dd)
    DED = sum(x['ded'] for x in dd)
    AX = sum(x['ax'] for x in dd)
    AW = sum(x['w6'] * x['A'] for x in dd)
    PD = _r6(AW / PA)
    PMR = PM / PA * 100
    PY = _r6(PMR * 365 / PD)
    rec = tc['receivables']
    return dict(tc=tc, fx=fx, days=dd, PA=PA, PM=PM, PB=PB, NET=NET, DED=DED,
                AX=AX, AW=AW, PD=PD, PMR=_r6(PMR), PY=PY, rec=rec,
                recA=D(sum(r['Ai'] for r in rec)),
                recNET=D(sum(r['순지급액'] for r in rec)),
                recDED=D(sum(r['차감액'] for r in rec)),
                recAX=D(sum(r['Ai×Di'] for r in rec)),
                recFEE=D(sum(r['채권매입수수료'] for r in rec)),
                dayFEE=sum(x['fee'] for x in dd))


# ══════════════════════════════════════════════════════════════════
#  절 조립 — [{'no', 'title', 'tables':[{'head','rows','w','mono'}]}]
# ══════════════════════════════════════════════════════════════════

HEAD_CALC = ['기호', '산식', '결과']
HEAD_IN = ['항목', '값']
HEAD_CHECK = ['대조', '값']


def sections():
    f = facts()
    tc, fx, dd = f['tc'], f['fx'], f['days']
    mt = tc['meta']
    r1 = f['rec'][0]
    d1 = dd[0]
    r = D(str(mt['할인율']))
    ur = _rate(tc, '미지급금_{i}')
    orr = _rate(tc, '과지급금_{i}')
    span = mt['기간']
    S = []

    # ── 1. 계산에 넣는 값 ────────────────────────────────────────
    kv = [
        ('가맹점', '%s (%s)' % (mt['가맹점'], mt['가맹점ID'])),
        ('사업자번호 · 대표자', '%s · %s' % (mt['사업자번호'], mt['대표자'])),
        ('업종·품목', mt['업종·품목']),
        ('규모', mt['구간']),
        ('플랫폼', '카드사'),
        ('채권', '카드사 70건 · 이 가맹점 이 기간 전건은 280건'),
        ('순지급액_i 70건 합', _n(f['recNET']) + '원'),
        ('조회기간', '%s · %s' % (span, mt['기간의 뜻'])),
        ('기준일 d', mt['기준일']),
        ('할인율 r', mt['할인율 표기']),
        ('순현금 EC', _n(mt['순현금 EC']) + '원'),
    ]
    rows5 = [[str(x['no']), x['선정산일'], x['정산예정일'], '%d일' % x['Di'],
              _n(x['순지급액']) + '원'] for x in f['rec'][:5]]
    S.append(dict(no=1, title='계산에 넣는 값', tables=[
        dict(head=list(HEAD_IN), rows=kv, w=[4.2, 12.0], mono=(1,)),
        dict(head=['번호 (70건 중 1~5)', '선정산일', '정산예정일', 'D_i', '순지급액_i'],
             rows=rows5, w=[3.4, 3.0, 3.0, 1.8, 3.4], mono=(0, 1, 2, 3, 4)),
    ]))

    # ── 2. 채권 1건 계산 ─────────────────────────────────────────
    given = [
        ('선정산일', r1['선정산일']),
        ('정산예정일', r1['정산예정일']),
        ('순지급액_i', _n(r1['순지급액']) + '원'),
    ]
    rows = [
        ['D_i', 'D_i = 정산예정일 − 선정산일 = %s − %s (한편넣기)'
         % (r1['정산예정일'], r1['선정산일']), '%d일' % r1['Di']],
        ['A_i', 'A_i = 순지급액_i × (1 − r) = %s × (1 − %s)'
         % (_n(r1['순지급액']), r), _n(r1['Ai']) + '원'],
        ['채권매입수수료_i',
         '채권매입수수료_i = 절사( 순지급액_i × r ) = 절사( %s × %s )'
         % (_n(r1['순지급액']), r), _n(r1['채권매입수수료']) + '원'],
        ['미지급금_i',
         '미지급금_i = 반올림( 순지급액_i × 미지급률 ) = 반올림( %s × %s )'
         % (_n(r1['순지급액']), ur), _n(r1['미지급금']) + '원'],
        ['과지급금_i',
         '과지급금_i = 반올림( 순지급액_i × 과지급률 ) = 반올림( %s × %s )'
         % (_n(r1['순지급액']), orr), _n(r1['과지급금']) + '원'],
        ['L_i', 'L_i = 미지급금_i − 과지급금_i = %s − %s'
         % (_n(r1['미지급금']), _n(r1['과지급금'])), _n(r1['Li']) + '원'],
        ['max(0, L_i)', 'max(0, L_i) = max(0, %s)' % _n(r1['Li']),
         _n(r1['차감액']) + '원'],
        ['M_i', 'M_i = 채권매입수수료_i − max(0, L_i) = %s − %s'
         % (_n(r1['채권매입수수료']), _n(r1['차감액'])), _n(r1['Mi']) + '원'],
        ['B_i', 'B_i = 순지급액_i − max(0, L_i) = %s − %s'
         % (_n(r1['순지급액']), _n(r1['차감액'])), _n(r1['Bi']) + '원'],
        ['A_i × D_i', 'A_i × D_i = %s × %d' % (_n(r1['Ai']), r1['Di']),
         _n(r1['Ai×Di'])],
    ]
    S.append(dict(no=2, title='채권 1건 계산 — 1번 채권', tables=[
        dict(head=list(HEAD_IN), rows=given, w=[4.2, 12.0], mono=(1,)),
        dict(head=list(HEAD_CALC), rows=rows, w=[3.2, 9.4, 3.6], mono=(0, 1, 2)),
    ]))

    # ── 3. 하루 합계 ─────────────────────────────────────────────
    sums = [
        ('건수', '%d건' % d1['n']),
        ('( Σ 순지급액_i )', _n(d1['net']) + '원'),
        ('( Σ A_i )', _n(d1['A']) + '원'),
        ('( Σ 미지급금_i )', _n(d1['unpaid']) + '원'),
        ('( Σ 과지급금_i )', _n(d1['over']) + '원'),
        ('( Σ max(0, L_i) )', _n(d1['ded']) + '원'),
        ('( Σ A_i × D_i )', _n(d1['ax'])),
    ]
    rows = [
        ['A_d', 'A_d = ( Σ A_i )      i ∈ d', _n(d1['A']) + '원'],
        ['채권매입수수료_d',
         '채권매입수수료_d = 절사( ( Σ 순지급액_i ) × r ) = 절사( %s × %s )'
         % (_n(d1['net']), r), _n(d1['fee']) + '원'],
        ['M_d',
         'M_d = 채권매입수수료_d − ( Σ max(0, L_i) ) = %s − %s'
         % (_n(d1['fee']), _n(d1['ded'])), _n(d1['M']) + '원'],
        ['B_d',
         'B_d = ( Σ 순지급액_i ) − ( Σ max(0, L_i) ) = %s − %s'
         % (_n(d1['net']), _n(d1['ded'])), _n(d1['B']) + '원'],
        ['MR_d', 'MR_d = M_d ÷ A_d = %s ÷ %s'
         % (_n(d1['M']), _n(d1['A'])), '%s%%' % d1['mr']],
        ['D_d',
         'D_d = ( Σ A_i × D_i ) ÷ A_d = %s ÷ %s'
         % (_n(d1['ax']), _n(d1['A'])),
         '%s일   화면 %s' % (d1['w6'], _r2(d1['w6']))],
        ['Y_d',
         'Y_d = MR_d × 365 ÷ D_d = %s%% × 365 ÷ %s'
         % (d1['mr'], d1['w6']),
         '%s%%   화면 %s%%' % (d1['ymr'], _r2(d1['ymr']))],
    ]
    seven = [[x['d'], '%d건' % x['n'], _n(x['A']), _n(x['M']), _n(x['B']),
              str(x['w6']), '%s%%' % x['ymr']] for x in dd]
    S.append(dict(no=3, title='하루 합계 — 정산예정일 %s · %d건' % (d1['d'], d1['n']),
                  tables=[
        dict(head=list(HEAD_IN), rows=sums, w=[4.6, 11.6], mono=(0, 1)),
        dict(head=list(HEAD_CALC), rows=rows, w=[3.4, 9.2, 3.6], mono=(0, 1, 2)),
        dict(head=['정산예정일', '건수', 'A_d', 'M_d', 'B_d',
                   'D_d', 'Y_d'], rows=seven,
             w=[2.6, 1.4, 2.4, 1.6, 2.4, 2.2, 2.4], mono=(0, 1, 2, 3, 4, 5, 6)),
    ]))

    # ── 4. 조회기간 합계 ─────────────────────────────────────────
    nocash = '낼 수 없다. EC 는 투자자 한 명 앞으로 있는 잔액이라 가맹점·플랫폼으로 나뉘지 않는다.'
    rows = [
        ['PA', 'PA = ( Σ A_d )      조회기간 안 레코드 전부', _n(f['PA']) + '원'],
        ['PM', 'PM = ( Σ M_d )', _n(f['PM']) + '원'],
        ['PB', 'PB = ( Σ B_d )', _n(f['PB']) + '원'],
        ['PMR', 'PMR = PM ÷ PA = %s ÷ %s' % (_n(f['PM']), _n(f['PA'])),
         '%s%%' % f['PMR']],
        ['PD', 'PD = ( Σ A_i × D_i ) ÷ PA = %s ÷ %s'
         % (_n(f['AW'], 6), _n(f['PA'])),
         '%s일   화면 %s' % (f['PD'], _r2(f['PD']))],
        ['PY_a', 'PY_a = PMR × 365 ÷ PD = %s%% × 365 ÷ %s'
         % (f['PMR'], f['PD']),
         '%s%%   화면 %s%%' % (f['PY'], _r2(f['PY']))],
        ['PEC', 'PEC = ( Σ EC_d )', nocash],
        ['PY_t', 'PY_t = PY_a × PA ÷ (PA + PEC)', '낼 수 없다. PEC 가 없다.'],
    ]
    check = [
        ['채권 70건의 A_i 합 = PA',
         '%s = %s' % (_n(f['recA']), _n(f['PA']))],
        ['채권 70건의 순지급액_i 합 = 하루 값 7일 합',
         '%s = %s' % (_n(f['recNET']), _n(f['NET']))],
        ['채권 70건의 max(0, L_i) 합 = 하루 값 7일 합',
         '%s = %s' % (_n(f['recDED']), _n(f['DED']))],
        ['채권 70건의 A_i × D_i 합 = 하루 값 7일 합',
         '%s = %s' % (_n(f['recAX']), _n(f['AX']))],
        ['채권 70건으로 낸 PD = 하루 값으로 낸 PD',
         '%s = %s' % (_r6(f['recAX'] / f['recA']), f['PD'])],
        ['( Σ 순지급액_i ) − ( Σ max(0, L_i) ) = PB',
         '%s − %s = %s' % (_n(f['NET']), _n(f['DED']), _n(f['PB']))],
        ['( Σ 채권매입수수료_d ) − 채권 70건의 채권매입수수료_i 합',
         '%s − %s = %s원 · 하루치는 ( Σ 순지급액_i ) 에 절사를 한 번 건다'
         % (_n(f['dayFEE']), _n(f['recFEE']), _n(f['dayFEE'] - f['recFEE']))],
    ]
    S.append(dict(no=4, title='조회기간 합계 — %s' % span, tables=[
        dict(head=list(HEAD_CALC), rows=rows, w=[2.6, 7.4, 6.2], mono=(0, 1, 2)),
        dict(head=list(HEAD_CHECK), rows=check, w=[8.0, 8.2], mono=(0, 1)),
    ]))

    # ── 5. 화면 표시값 대조 ──────────────────────────────────────────
    S.append(dict(no=5, title='화면 표시값 대조', tables=[
        dict(head=['메뉴', '표 · 항목', '날짜', '화면 표시값', '산식',
                   '채권 70건 값', '견줄 수 있나'],
             rows=screen_rows(), w=[1.8, 3.0, 2.3, 2.3, 4.4, 2.6, 4.0],
             mono=(3, 4, 5)),
    ]))
    return S


def screen_rows():
    """화면 반영처 45줄 — 화면 표시값은 ledger_facts, 70건 값은 테스트 케이스."""
    f = facts()
    fx, dd = f['fx'], f['days']
    tb = fx['tyByDate']
    P, T = '투자 수익', '일별 투자수익'
    NOSUM = '카드사 70건만 놓고 낸 값이라 화면 표시값에 더해지지 않는다.'
    NOCASH = '순현금 EC 는 투자자 한 명 앞으로 있는 잔액이라 가맹점·플랫폼으로 나뉘지 않는다.'
    out = []

    def part(a, b):
        """값 칸과 까닭 칸을 갈라 낸다 — 한 칸에 대시로 붙이지 않는다."""
        return [_n(a) + '원', '화면 표시값의 %s%%' % _r6(D(a) / D(b) * 100)]

    for x in dd:
        r = tb[x['d']]
        out.append([P, T + ' · 상환액', x['d'], _n(r[4]) + '원',
                    'B_d = ( Σ 순지급액_i ) − ( Σ max(0, L_i) )',
                    *part(x['B'], r[4])])
    for x in dd:
        r = tb[x['d']]
        out.append([P, T + ' · 투자실행금', x['d'], _n(r[2]) + '원',
                    'A_d = ( Σ A_i )      i ∈ d',
                    *part(x['A'], r[2])])
    for x in dd:
        r = tb[x['d']]
        out.append([P, T + ' · 투자 수익', x['d'], _n(r[3]) + '원',
                    'M_d = 채권매입수수료_d − ( Σ max(0, L_i) )',
                    *part(x['M'], r[3])])
    for x in dd:
        r = tb[x['d']]
        out.append([P, T + ' · W금융일수', x['d'], '%s일' % r[0],
                    'D_d = ( Σ A_i × D_i ) ÷ A_d',
                    '%s일' % _r2(x['w6']), NOSUM])
    for x in dd:
        r = tb[x['d']]
        out.append([P, T + ' · Ty수익율', x['d'], '%s%%' % r[1],
                    'Y_d = MR_d × 365 ÷ D_d',
                    '%s%%' % _r2(x['ymr']), NOSUM])

    span = f['tc']['meta']['기간']
    out.append([P, '일별 투자수익 합계 행 · 상환액', span, _n(fx['weekRepay']) + '원',
                'PB = ( Σ B_d )', *part(f['PB'], fx['weekRepay'])])
    out.append([P, '현황 카드 · 투자실행금', span, _n(fx['weekExec']) + '원',
                'PA = ( Σ A_d )', *part(f['PA'], fx['weekExec'])])
    out.append([P, '현황 카드 · 투자수익', span, _n(fx['weekProfit']) + '원',
                'PM = ( Σ M_d )', *part(f['PM'], fx['weekProfit'])])
    out.append([P, '현황 카드 · Ty수익율 · 투자실행금액 대비', span, '%s%%' % fx['weekTy'],
                'PY_a = PMR × 365 ÷ PD   ·   PD %s일' % fx['weekWRaw'],
                '%s%%' % _r2(f['PY']), NOSUM])
    out.append([P, '현황 카드 · Ty수익율 · 투자자산 대비', span, '%s%%' % fx['weekTyAsset'],
                'PY_t = PY_a × PA ÷ (PA + PEC)   ·   PEC %s원' % _n(fx['weekPsc']),
                '낼 수 없다', NOCASH])

    m = [x for x in fx['merchants'] if x[0] == f['tc']['meta']['가맹점']][0]
    asof = '기준일 ' + f['tc']['meta']['기준일']
    A, W, S, TY = m[1], m[2], m[3], m[4]
    out.append(['투자 자산', '가맹점별 투자자산 · 투자실행액', asof, _n(A) + '원',
                '( Σ A_i )      i 는 정산예정일이 기준일 뒤인 미회수분',
                '겹치지 않는다',
                '화면은 정산예정일이 아직 오지 않은 채권을 세고, 이 70건은 '
                '정산예정일이 %s 로 이미 지났다.' % span])
    out.append(['투자 자산', '가맹점별 투자자산 · W금융일수', asof, '%s일' % W,
                'D = ( Σ A_i × D_i ) ÷ ( Σ A_i )      i 는 대상정산금채권 전체 · 발생 기준',
                '세는 채권이 다르다',
                '화면은 이 가맹점 채권 전건(전 플랫폼 · 발생 기준)이고 '
                '이 70건은 카드사 이레치다.'])
    out.append(['투자 자산', '가맹점별 투자자산 · S입금부족율', asof, '%s%%' % S,
                'LR = ( Σ L_i ) ÷ ( Σ A_i )      i 는 선정산일이 기준일 20일 전부터 11일 전까지인 채권',
                '세는 기간이 다르다',
                '화면은 선정산일 %s ~ %s 인 표본이고 이 70건은 정산예정일 %s 이다.'
                % (fx['sampleSpan'][0], fx['sampleSpan'][1], span)])
    out.append(['투자 자산', '가맹점별 투자자산 · Ty수익율', asof, '%s%%' % TY,
                'Y_r = r × 365 ÷ D   ·   D %s일' % W,
                '%s%% × 365 ÷ %s = %s%%' % (fx['rate'], W, TY),
                '화면 두 칸으로 그대로 되짚어진다.'])
    out.append(['투자 자산', '가맹점별 투자자산 · 비중', asof,
                '%s%%' % (D(A) / D(fx['exec']) * D(100)).quantize(
                    D('0.1'), rounding=ROUND_HALF_UP),
                '가맹점 행 투자실행액 ÷ 투자실행액 %s원' % _n(fx['exec']),
                '나오지 않는다', '분모가 8곳 전체 투자실행액이다.'])
    return out


if __name__ == '__main__':
    for s in sections():
        print('%d. %s' % (s['no'], s['title']))
        for t in s['tables']:
            print('   %-8s %d행' % ('표', len(t['rows'])), t['head'])
    print('화면 반영처 %d줄' % len(screen_rows()))
