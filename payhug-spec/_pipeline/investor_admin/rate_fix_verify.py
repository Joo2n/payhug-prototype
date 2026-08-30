# -*- coding: utf-8 -*-
"""폐기 — 맵 locator 가 옛 값이라 0건 매칭. 실행하면 74건 전건 locator 오류 뒤 예외로 죽는다.

정정값 맵 드라이런 — 원본은 건드리지 않고 메모리에서만 치환·재검산.

폐기일 2026-08-30. rate_fix_map.json 의 locator 는 할인율 정정 라운드(2026-08-29) 당시의
낱장 HTML 문자열이다. 그 뒤 D-31(수수료 앵커 = 순지급액)로 원장이 재생성되고 낱장이 다시
찍히면서 locator 74건이 전부 대상 파일에서 사라졌다. 아래 OLD 배열의 잔존 구값 목록도 같은
시점의 값이라 지금 화면과 대조 대상이 아니다.

역할을 대신하는 것 — 할인율·수익·상환액·W·Ty 의 행 단위 재검산은 verify_crossscreen.py
(정적 HTML · app.html 데이터셋 · xlsx 실파일 3중 대조)와 verify_identity.js(항등식)가 덮는다.
검사 공백 없음. 실행 명부(verifiers.md)에서도 뺀다.
"""
import json, io, os, re
from decimal import Decimal as D, ROUND_HALF_UP, ROUND_FLOOR
ROOT='/Users/semi/cursor/payhug-investor-admin'
M=json.load(io.open('/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/rate_fix_map.json',encoding='utf-8'))
def fl(x): return int(D(x).quantize(D('1'),rounding=ROUND_FLOOR))
def r2(x): return D(x).quantize(D('0.01'),rounding=ROUND_HALF_UP)
def r1(x): return D(x).quantize(D('0.1'),rounding=ROUND_HALF_UP)
def n(s): return int(s.replace(',',''))
bad=[]
buf={}
for x in M['fixes']:
    if x['kind']=='cell': continue
    f=x['file']
    if f not in buf: buf[f]=io.open(os.path.join(ROOT,f),encoding='utf-8').read()
    if buf[f].count(x['locator'])!=1: bad.append('%s locator %d회'%(f,buf[f].count(x['locator'])))
    buf[f]=buf[f].replace(x['locator'],x['corrected'],1)
print('치환 %d건 / 대상 파일 %d개 / locator 오류 %d'%(sum(1 for x in M['fixes'] if x['kind']!='cell'),len(buf),len(bad)))

ROW=re.compile(r'<td class="mono">(\d{4}-\d\d(?:-\d\d)?)</td>\s*<td class="num">([\d,]+)</td>\s*'
               r'<td class="num">([\d,]+)</td>\s*<td class="num"><span class="strong">([\d,]+)</span></td>\s*'
               r'<td class="num">([\d.]+)</td>\s*<td class="num">([\d.]+)%</td>')
FOOT=re.compile(r'<td>합계</td>\s*<td class="num">([\d,]+)</td>\s*<td class="num">([\d,]+)</td>\s*'
                r'<td class="num">([\d,]+)</td>\s*<td class="num">([\d.]+)<span class="avg-note">')
err=[]
for f in ('invest-profit.html','invest-profit--monthly.html'):
    rows=ROW.findall(buf[f]); assert rows, f
    er=ep=rp=0; wn=tn=D(0)
    for d,rep,ex,pr,w,t in rows:
        rep,ex,pr=n(rep),n(ex),n(pr)
        if pr!=fl(D(ex)*D('0.0011')): err.append('%s %s 수익 %d'%(f,d,pr))
        if rep!=ex+pr: err.append('%s %s 상환액 %d'%(f,d,rep))
        exp=r2(D('0.11')*365/D(w))
        if D(t)!=exp: err.append('%s %s Ty %s != %s'%(f,d,t,exp))
        er+=rep; ep+=ex; rp+=pr; wn+=D(w)*ex; tn+=D(t)*ex
    ft=FOOT.search(buf[f]).groups()
    if n(ft[0])!=er: err.append('%s 합계 상환액 %s != %d'%(f,ft[0],er))
    if n(ft[1])!=ep: err.append('%s 합계 실행금 %s != %d'%(f,ft[1],ep))
    if n(ft[2])!=rp: err.append('%s 합계 수익 %s != %d'%(f,ft[2],rp))
    if D(ft[3])!=r1(wn/ep): err.append('%s 합계 W %s != %s'%(f,ft[3],r1(wn/ep)))
    print('  %-32s 행 %d · 합계 상환 %s / 실행 %s / 수익 %s / W %s / Ty(가중) %s%%'
          %(f,len(rows),format(er,','),format(ep,','),format(rp,','),ft[3],r2(tn/ep)))
# 잔존 구값 스캔
OLD=['601,000','578,000','552,000','634,000','617,000','596,000','632,000','4,210,000',
     '1,274,200,000','16,980,000','17,920,000','18,730,000','18,140,000','19,480,000','17,260,000',
     '108,510,000','32,698,000,000','11.2일','3.59%','182,300,000','5,124,600,000']
for f,s in buf.items():
    hit=[o for o in OLD if o in s]
    if hit: err.append('%s 구값 잔존 %s'%(f,hit))
print('재검산 오류: %d'%len(err))
for e in err: print('  !!',e)
