# -*- coding: utf-8 -*-
"""투자 수익 화면 — 기간 필터 재설계 패치.

기간(시작일·종료일)과 집계 단위(일별·주별·월별) 두 축을 분리하고,
집계 단위를 데이트피커의 스냅 단위로 삼는다. 설계 근거는 period_design.md.
build_app.py 의 투자 수익 구간만 건드린다 — 다른 화면 코드는 손대지 않는다.
"""
import io, sys

SRC = '/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/build_app.py'

PATCHES = []


def P(old, new, n=1):
    PATCHES.append((old, new, n))


# ────────────────────────────────────────────────────────────
# 1) 마크업 — 프리셋 줄을 날짜 줄 위로 올리고 6개를 다 심는다(단위별로 보였다 숨었다).
#    토글에 주별을 더한다.
# ────────────────────────────────────────────────────────────
P('''        <div class="search-bar">
          <div class="filter-row">
            <div class="filter-field">
              <label>시작일</label>
              <input type="date" class="input" data-mount="pf-from" data-act="pf-date" data-which="from">
            </div>
            <div class="filter-tilde">~</div>
            <div class="filter-field">
              <label>종료일</label>
              <input type="date" class="input" data-mount="pf-to" data-act="pf-date" data-which="to">
            </div>
            <div class="preset-row">
              <button class="preset-btn" data-act="preset" data-preset="week">일주일</button>
              <button class="preset-btn" data-act="preset" data-preset="month">금월</button>
            </div>
            <button class="btn btn-primary" data-act="pf-search" data-mount="pf-go">검색</button>
            <button class="btn btn-outline" data-act="pf-reset">초기화</button>
          </div>
          <p class="range-warn" data-mount="pf-warn" hidden>시작일은 종료일보다 이후일 수 없음.</p>
          <div class="toggle">
            <button class="toggle-btn" data-act="pf-gran" data-gran="daily">일별</button>
            <button class="toggle-btn" data-act="pf-gran" data-gran="monthly">월별</button>
          </div>
        </div>
''',
  '''        <div class="search-bar">
          <div class="preset-row">
            <button class="preset-btn" data-act="preset" data-preset="week"  data-for="daily">일주일</button>
            <button class="preset-btn" data-act="preset" data-preset="month" data-for="daily">금월</button>
            <button class="preset-btn" data-act="preset" data-preset="w4"    data-for="weekly">4주</button>
            <button class="preset-btn" data-act="preset" data-preset="w12"   data-for="weekly">12주</button>
            <button class="preset-btn" data-act="preset" data-preset="m3"    data-for="monthly">3개월</button>
            <button class="preset-btn" data-act="preset" data-preset="m6"    data-for="monthly">6개월</button>
          </div>
          <div class="filter-row">
            <div class="filter-field">
              <label>시작일</label>
              <input type="date" class="input" data-mount="pf-from" data-act="pf-date" data-which="from">
            </div>
            <div class="filter-tilde">~</div>
            <div class="filter-field">
              <label>종료일</label>
              <input type="date" class="input" data-mount="pf-to" data-act="pf-date" data-which="to">
            </div>
            <button class="btn btn-primary" data-act="pf-search" data-mount="pf-go">검색</button>
            <button class="btn btn-outline" data-act="pf-reset">초기화</button>
          </div>
          <p class="range-warn" data-mount="pf-warn" hidden>시작일은 종료일보다 이후일 수 없음.</p>
          <div class="toggle">
            <button class="toggle-btn" data-act="pf-gran" data-gran="daily">일별</button>
            <button class="toggle-btn" data-act="pf-gran" data-gran="weekly">주별</button>
            <button class="toggle-btn" data-act="pf-gran" data-gran="monthly">월별</button>
          </div>
        </div>
''')

# ────────────────────────────────────────────────────────────
# 2) 모델 — 두 축 · 스냅 · 프리셋 묶음
# ────────────────────────────────────────────────────────────
P("""var PF = {gran:'daily', from:'2026-08-21', to:'2026-08-27'};
""",
  """var PF = {gran:'daily', from:'2026-08-21', to:'2026-08-27'};
/* ── 두 축 ─────────────────────────────────────────────────────────────
   PF.from · PF.to = 무엇을 조회하느냐.  PF.gran = 표의 한 행이 무엇이냐(하루·한 주·한 달).
   두 축은 서로를 지우지 않는다. 집계 단위를 바꿔도 기간은 남고, 새 단위 경계로 넓혀 스냅될 뿐이다.
   집계 단위가 곧 데이트피커의 스냅 단위다 — 날짜 하나를 고르면 그 날짜가 속한 단위 전체가 잡힌다. */
function dt(s){ var p = s.split('-'); return new Date(+p[0], +p[1] - 1, +p[2]); }
function ds(d){
  var m = d.getMonth() + 1, y = d.getDate();
  return d.getFullYear() + '-' + (m < 10 ? '0' : '') + m + '-' + (y < 10 ? '0' : '') + y;
}
function addDays(s, n){ var d = dt(s); d.setDate(d.getDate() + n); return ds(d); }
/* 주 시작 = 월요일. 일요일은 getDay()===0 이라 6일 뒤로 민다 —
   원본 DateRangeFilter.tsx:35 의 '이번 주' 계산(day === 0 ? 6 : day - 1)과 같은 보정이다. */
function monStart(s){ var w = dt(s).getDay(); return addDays(s, -(w === 0 ? 6 : w - 1)); }
function sunEnd(s){ return addDays(monStart(s), 6); }
function mFirst(s){ return s.slice(0, 7) + '-01'; }
function mLast(s){ var d = dt(mFirst(s)); return ds(new Date(d.getFullYear(), d.getMonth() + 1, 0)); }
function mShift(s, n){ var d = dt(mFirst(s)); return ds(new Date(d.getFullYear(), d.getMonth() + n, 1)); }
/* 스냅 — 시작일은 단위의 처음으로, 종료일은 단위의 끝으로. 일별은 고른 날짜 그대로다. */
function snapFrom(s, g){ return !s ? s : (g === 'weekly' ? monStart(s) : (g === 'monthly' ? mFirst(s) : s)); }
function snapTo(s, g){ return !s ? s : (g === 'weekly' ? sunEnd(s) : (g === 'monthly' ? mLast(s) : s)); }

/* 프리셋 = 기간을 채우는 단축키. 집계 단위마다 묶음이 다르다.
   범위를 그 단위 경계에 맞춰 둬야 눌러 채운 기간이 스냅을 다시 통과해도 그대로다.
   일별 둘(일주일·금월)은 스토리보드 슬라이드7 그대로이고,
   주·달 묶음은 원본 DateRangeFilter.tsx:23-61 의 '최근 3개월' ·
   MerchantAvgSalesSummary.tsx:168-176 의 3~6개월 조회범위와 같은 계열이다. */
var PRESET_RANGE = {
  week:  [addDays(BASE_DATE, -6),               BASE_DATE],
  month: [mFirst(BASE_DATE),                    BASE_DATE],
  w4:    [addDays(monStart(BASE_DATE), -21),    sunEnd(BASE_DATE)],
  w12:   [addDays(monStart(BASE_DATE), -77),    sunEnd(BASE_DATE)],
  m3:    [mShift(BASE_DATE, -2),                mLast(BASE_DATE)],
  m6:    [mShift(BASE_DATE, -5),                mLast(BASE_DATE)]
};
var PRESET_LABEL = {week:'일주일', month:'금월', w4:'4주', w12:'12주', m3:'3개월', m6:'6개월'};
var PRESET_GRAN  = {week:'daily', month:'daily', w4:'weekly', w12:'weekly', m3:'monthly', m6:'monthly'};
var GRAN_LABEL   = {daily:'일별', weekly:'주별', monthly:'월별'};
var GRAN_COL     = {daily:'정산예정일', weekly:'정산예정주', monthly:'정산예정월'};
/* 활성 판정은 현재 날짜값이 프리셋 범위와 같은지로 역산한다 — 따로 담아 두지 않는다.
   그래서 피커를 만져 값이 어긋나면 저절로 풀리고, 단위를 바꿔 묶음이 갈려도
   지금 기간과 일치하는 것 하나만 켜진다. 원본 DateRangeFilter.tsx:74-77 과 같은 방식. */
function activePreset(){
  for(var k in PRESET_RANGE)
    if(PRESET_GRAN[k] === PF.gran && PRESET_RANGE[k][0] === PF.from && PRESET_RANGE[k][1] === PF.to) return k;
  return null;
}
""")

P("""var PRESET_LABEL = {week:'일주일', month:'금월'};
function presetLabel(){
  for(var k in PRESET_RANGE) if(PRESET_RANGE[k][0] === PF.from && PRESET_RANGE[k][1] === PF.to) return PRESET_LABEL[k];
  return '직접입력';
}
""",
  """function presetLabel(){ var k = activePreset(); return k ? PRESET_LABEL[k] : '직접입력'; }
""")

# ────────────────────────────────────────────────────────────
# 3) 집계 — 일별 원장 하나를 주·달로 묶는다. 원장을 두 벌 만들지 않는다.
# ────────────────────────────────────────────────────────────
P("""/* 월별 표 = 잘라 낸 일자를 달별로 합친 것. 한 달이 조회 기간에 일부만 걸리면 걸린 일자만 합친다.
   그래서 같은 조회 기간이면 월별 합계 = 일별 합계이고, 카드 값도 둘이 같다. */
function rollupMonths(days){
  var out = [], idx = {}, i, g, r;
  for(i = 0; i < days.length; i++){
    r = days[i];
    g = idx[r.d.slice(0, 7)];
    if(!g){ g = idx[r.d.slice(0, 7)] = {d:r.d.slice(0, 7), repay:0, exec:0, profit:0, w:0, ty:0, wx:0, tx:0, days:0}; out.push(g); }
    g.repay += r.repay; g.exec += r.exec; g.profit += r.profit;
    g.wx += r.w * r.exec; g.tx += r.ty * r.exec; g.days += 1;
  }
  for(i = 0; i < out.length; i++){
    g = out[i];
    /* 합계 행과 같은 규칙 — W금융일수·Ty수익율은 투자실행금 가중평균이다.
       반올림하지 않고 담아 두고 표기할 때만 자른다. 그래야 일별 표와 월별 표의 카드 값이 같다. */
    g.w  = g.exec ? g.wx / g.exec : 0;
    g.ty = g.exec ? g.tx / g.exec : 0;
  }
  out.sort(function(a, b){ return a.d < b.d ? -1 : (a.d > b.d ? 1 : 0); });
  return out;
}
function pfRows(){
  var d = pfDays();
  return PF.gran === 'daily' ? d : rollupMonths(d);
}
""",
  """/* 주별·월별 표 = 잘라 낸 일자를 버킷으로 묶은 것. 버킷이 조회 기간에 일부만 걸리면 걸린 일자만 합친다.
   그래서 같은 조회 기간이면 주별 합계 = 월별 합계 = 일별 합계이고, 카드 값도 셋이 같다.
   대표 정의서의 PSA·PSM 은 '선택 기간 합계'이고, 일별·주별·월별은 그 기간을 어느 크기로
   쪼개 보여주느냐일 뿐이다 — 버킷 하나에 들어가는 계산은 단위가 바뀌어도 같다. */
function rollupBy(days, keyOf, labelOf){
  var out = [], idx = {}, i, g, r, k;
  for(i = 0; i < days.length; i++){
    r = days[i]; k = keyOf(r.d);
    g = idx[k];
    if(!g){ g = idx[k] = {k:k, d:labelOf(r.d), repay:0, exec:0, profit:0, w:0, ty:0, wx:0, tx:0, days:0}; out.push(g); }
    g.repay += r.repay; g.exec += r.exec; g.profit += r.profit;
    g.wx += r.w * r.exec; g.tx += r.ty * r.exec; g.days += 1;
  }
  for(i = 0; i < out.length; i++){
    g = out[i];
    /* 합계 행과 같은 규칙 — W금융일수·Ty수익율은 투자실행금 가중평균이다(단순 합이 아니다).
       반올림하지 않고 담아 두고 표기할 때만 자른다. 그래야 일별·주별·월별 표의 카드 값이 같다. */
    g.w  = g.exec ? g.wx / g.exec : 0;
    g.ty = g.exec ? g.tx / g.exec : 0;
  }
  out.sort(function(a, b){ return a.k < b.k ? -1 : (a.k > b.k ? 1 : 0); });
  return out;
}
function rollupMonths(days){
  return rollupBy(days, function(d){ return d.slice(0, 7); }, function(d){ return d.slice(0, 7); });
}
/* 주 라벨은 그 주의 월요일 ~ 일요일이다. 조회 기간이 주를 일부만 덮어도 라벨은 주 경계를 쓴다. */
function rollupWeeks(days){
  return rollupBy(days, monStart, function(d){ return monStart(d) + ' ~ ' + sunEnd(d).slice(5); });
}
function pfRows(){
  var d = pfDays();
  if(PF.gran === 'weekly')  return rollupWeeks(d);
  if(PF.gran === 'monthly') return rollupMonths(d);
  return d;
}
""")

# ────────────────────────────────────────────────────────────
# 4) 렌더 — 프리셋 묶음 교체 · 피커는 어느 단위에서도 살려 둔다
# ────────────────────────────────────────────────────────────
P("""  /* 프리셋 활성 판정은 현재 날짜값이 프리셋 범위와 같은지로 본다 — 수동 입력으로 맞춰도 되살아난다.
     원본 DateRangeFilter.tsx:74-77(판정) · :99(aria-pressed 고지). */
  QA('.preset-btn', sec).forEach(function(b){
    var r = PRESET_RANGE[b.dataset.preset], on = !!(r && r[0] === PF.from && r[1] === PF.to);
    b.classList.toggle('active', on);
    b.setAttribute('aria-pressed', on ? 'true' : 'false');
  });
  QA('.toggle-btn', sec).forEach(function(b){ b.classList.toggle('active', b.dataset.gran === PF.gran); });
  var fi = M('pf-from', 'invest-profit'), ti = M('pf-to', 'invest-profit');
  fi.value = PF.from; ti.value = PF.to;
  /* 역전 범위 방어 — 달력 자체를 상호 제한하고, 어긋나면 안내문 + 조회 버튼 비활성.
     원본 DateRangeFilter.tsx:79, 116, 122, 128, 138-140 */
  fi.max = PF.to || ''; ti.min = PF.from || '';
  var badRange = !!(PF.from && PF.to && PF.from > PF.to);
  M('pf-warn', 'invest-profit').hidden = !badRange;
  M('pf-go', 'invest-profit').disabled = badRange;
  M('pf-tbl-title', 'invest-profit').textContent = daily ? '일별 투자수익' : '월별 투자수익';
""",
  """  /* 프리셋 묶음은 집계 단위를 따라 갈린다 — 그 단위 것만 남기고 나머지는 접는다.
     활성 판정은 activePreset() 이 날짜값으로 역산한다.
     원본 DateRangeFilter.tsx:74-77(판정) · :99(aria-pressed 고지). */
  var ap = activePreset();
  QA('.preset-btn', sec).forEach(function(b){
    var mine = (b.dataset['for'] === PF.gran), on = mine && (b.dataset.preset === ap);
    b.hidden = !mine;
    b.classList.toggle('active', on);
    b.setAttribute('aria-pressed', on ? 'true' : 'false');
  });
  QA('.toggle-btn', sec).forEach(function(b){ b.classList.toggle('active', b.dataset.gran === PF.gran); });
  var fi = M('pf-from', 'invest-profit'), ti = M('pf-to', 'invest-profit');
  fi.value = PF.from; ti.value = PF.to;
  /* 역전 범위 방어 — 안내문 + 조회 버튼 비활성. 원본 DateRangeFilter.tsx:79, 138-140.
     달력의 min/max 상호 제한(원본 :116, :122)은 걸지 않는다. 걸면 지금 기간보다 앞쪽으로
     옮기려고 종료일부터 열었을 때 달력이 통째로 막혀, 피커가 어느 단위에서도 살아 있어야
     한다는 규칙과 어긋난다. 어긋난 범위는 안내문과 비활성 버튼으로 잡는다. */
  var badRange = !!(PF.from && PF.to && PF.from > PF.to);
  M('pf-warn', 'invest-profit').hidden = !badRange;
  M('pf-go', 'invest-profit').disabled = badRange;
  M('pf-tbl-title', 'invest-profit').textContent = GRAN_LABEL[PF.gran] + ' 투자수익';
""")

# daily 지역변수는 3분기가 되면서 쓸 곳이 없어졌다 — GRAN_LABEL·GRAN_COL 이 대신한다.
P("""  var sec = SEC('invest-profit'), rows = pfRows(), daily = (PF.gran === 'daily');
""",
  """  var sec = SEC('invest-profit'), rows = pfRows();
""")

P("""      '<th>' + (daily ? '정산예정일' : '정산예정월') + '</th><th class="num">상환액</th>' +
""",
  """      '<th>' + GRAN_COL[PF.gran] + '</th><th class="num">상환액</th>' +
""")

# ────────────────────────────────────────────────────────────
# 5) 상태 심기 — 월별 상태는 6개월 프리셋 자리에 놓는다
# ────────────────────────────────────────────────────────────
P("""    if(s === 'monthly'){ PF.gran = 'monthly'; PF.from = '2026-03-01'; PF.to = '2026-08-27'; }
    else if(s === 'empty'){ PF.gran = 'daily'; PF.from = '2026-02-01'; PF.to = '2026-02-07'; }
    else { PF.gran = 'daily'; PF.from = '2026-08-21'; PF.to = '2026-08-27'; }
""",
  """    if(s === 'monthly'){ PF.gran = 'monthly'; PF.from = PRESET_RANGE.m6[0]; PF.to = PRESET_RANGE.m6[1]; }
    else if(s === 'empty'){ PF.gran = 'daily'; PF.from = '2026-02-01'; PF.to = '2026-02-07'; }
    else { PF.gran = 'daily'; PF.from = PRESET_RANGE.week[0]; PF.to = PRESET_RANGE.week[1]; }
""")

# ────────────────────────────────────────────────────────────
# 6) 조작 — 프리셋은 채우고 바로 조회, 단위 전환은 기간을 넓혀 스냅만
# ────────────────────────────────────────────────────────────
P("""/* 투자 수익 */
/* 프리셋은 스토리보드 슬라이드7 그대로 둘이다 — 일주일·금월.
   원본 DateRangeFilter.tsx:23-61 은 7종(오늘·어제·이번 주·지난 주·이번 달·지난 달·최근 3개월)이지만
   이 화면의 진실은 스토리보드다. '어제'는 슬라이드7에 없어 싣지 않는다. */
var PRESET_RANGE = {
  week:  ['2026-08-21', '2026-08-27'],
  month: ['2026-08-01', '2026-08-27']
};
ACT['preset'] = function(el){
  var r = PRESET_RANGE[el.dataset.preset];
  PF.from = r[0]; PF.to = r[1];
  refresh('invest-profit');
};
""",
  """/* 투자 수익 */
/* 프리셋은 기간을 채우고 그 자리에서 조회까지 한다 — 검색을 다시 누르게 하지 않는다.
   (원본 DateRangeFilter.tsx:63-67 은 날짜만 채우고 조회는 따로 누르게 하지만,
    이 화면은 프리셋·단위 전환 모두 즉시 반영으로 확정했다.) */
ACT['preset'] = function(el){
  var r = PRESET_RANGE[el.dataset.preset];
  PF.from = r[0]; PF.to = r[1];
  refresh('invest-profit');
};
""")

P("""ACT['pf-gran']   = function(el){
  var g = el.dataset.gran;
  if(g === PF.gran){ refresh('invest-profit'); return; }
  if(g === 'monthly'){ PF.gran = 'monthly'; PF.from = '2026-03-01'; PF.to = '2026-08-27'; }
  else { PF.gran = 'daily'; PF.from = '2026-08-21'; PF.to = '2026-08-27'; }
  refresh('invest-profit');
};
""",
  """ACT['pf-gran']   = function(el){
  var g = el.dataset.gran;
  if(g === PF.gran){ refresh('invest-profit'); return; }
  PF.gran = g;
  /* 기간은 그대로 둔다 — 새 단위 경계로 넓혀 스냅할 뿐이다. 걸친 단위를 전부 덮는다.
     예) 일별 08-21~08-27 → 주별 08-17~08-30(두 주) · 월별 08-01~08-31(한 달) */
  PF.from = snapFrom(PF.from, g); PF.to = snapTo(PF.to, g);
  refresh('invest-profit');                 /* 검색을 다시 누르게 하지 않는다 */
};
""")

P("""  if(el.dataset.act === 'pf-date'){
    if(el.dataset.which === 'to') PF.to = el.value; else PF.from = el.value;
    refresh('invest-profit');
    return;
  }
""",
  """  if(el.dataset.act === 'pf-date'){
    /* 고른 날짜는 그 자리에서 집계 단위 경계로 스냅한다 —
       주별이면 그 날짜가 속한 주(월~일), 월별이면 그 달(1일~말일)이 통째로 잡힌다. */
    if(el.dataset.which === 'to') PF.to = snapTo(el.value, PF.gran);
    else PF.from = snapFrom(el.value, PF.gran);
    refresh('invest-profit');
    return;
  }
""")

# ────────────────────────────────────────────────────────────
# 7) 엑셀 — 일별 표 기준 파일만 있다
# ────────────────────────────────────────────────────────────
P("""  if(k === 'profit-daily' && PF.gran === 'monthly'){
    showInfo('월별 표에 대응하는 엑셀 파일 없음. 일별 표 기준 파일만 제공.');
    return;
  }
""",
  """  if(k === 'profit-daily' && PF.gran !== 'daily'){
    showInfo(GRAN_LABEL[PF.gran] + ' 표에 대응하는 엑셀 파일 없음. 일별 표 기준 파일만 제공.');
    return;
  }
""")


def main():
    s = io.open(SRC, encoding='utf-8').read()
    for old, new, n in PATCHES:
        c = s.count(old)
        if c != n:
            sys.stderr.write('패치 불일치 %d회(기대 %d) — %r\n' % (c, n, old[:90]))
            sys.exit(1)
        s = s.replace(old, new)
    io.open(SRC, 'w', encoding='utf-8').write(s)
    print('build_app.py 패치 %d건 적용' % len(PATCHES))


if __name__ == '__main__':
    main()
