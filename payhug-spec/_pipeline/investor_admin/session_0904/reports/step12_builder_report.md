# step12 적용 보고 — 투자자 어드민 툴팁을 기호정리표 V1.3 에 맞춤

기준 문서 `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/session_0904/artifact/투자자어드민 기호정리표_V1.3.html` (표 2 용어 이름 · 표 4 툴팁 열).
출력 레포 `/Users/semi/cursor/payhug-investor-admin` HEAD `9972f0b`, 시작 시 워킹트리 깨끗함. 커밋·push 없음.
`ledger_facts.json` md5 전후 동일 `1bffe2e62d2caf020b81c8b15a5c56bd`.

## 0. 지시와 다르게 처리한 것 (먼저)

| # | 무엇 | 왜 |
|---|---|---|
| a | `build_app.py` 의 `tyTh()`·`thirdTh()` 바로 위 주석 2개(1316~1318 · 1326~1327)를 `/* ⑥ 열머리 — 투자자어드민 기호정리표 V1.3 표 4 */` · `/* ③ 열머리 — 투자자어드민 기호정리표 V1.3 표 4 */` 한 줄로 바꿈 | 옛 주석에 `(④ ÷ ③)` 원문과 「칸 미지목」 경위가 들어 있고 `<script>` 로 `app.html` 에 그대로 실린다. 지시의 「옛 문구 0건」 검사가 이 주석 때문에 깨져서 최소 범위로 바꿈. 지시 목록의 「주석 2곳」(1917 · 2023)과는 별개 |
| b | `build_sim_static.py` 의 `TY_TH`(123) · `THIRD_TH`(131) 도 2·2b 와 같이 바꿈 | 지시는 3번만 「build_sim_static.py 에도 있으면」 이라 했는데, 같은 파일에 ③·⑥ 열머리 상수가 `build_app.py` 와 같은 마크업으로 있고 `invest-sim--result.html` 일별 표에 실린다. 안 바꾸면 낱장에 「⑥ 의 ③」「칸 미지목」이 남아 0건 검사가 깨지고 `verify_sim.js` 의 「⑥ 열머리 = tyTh()」 판정이 FAIL 난다 |
| c | 검증기 2개 갱신 — `verify_crossscreen.py` 350·366 (`보유 채권 전체 (회수된 것 포함)` → `보유 채권 전체`) · `verify_proto.js` 832 (`PEC기간 순현금 · ` → `PEC검색대상기간의 누적 순현금 · `) | 기대값이 옛 문구라 새 기준에서 FAIL 난다. 시스템 지침(스키마 바뀌면 검증기도 새 기준으로) |
| d | `app.html` 의 엑셀 매니페스트 `made:` 값 14줄이 `2026-09-07 11:36` → `2026-09-07 13:35` 로 바뀜 | 내가 바꾼 것이 아니라 `build_app.py` 가 `@@MT:파일@@` 로 `assets/xlsx/*.xlsx` 의 실제 mtime(`Sep 7 13:35:49`) 을 읽어 넣는 자리다. HEAD 의 `app.html` 이 엑셀 재생성(13:35) 전인 11:36 값으로 굳어 있었다. `app.html` 직접 편집 금지라 되돌리지 않음. 화면에는 엑셀 내려받기 화면의 「생성일시」로 보인다 |

`_fig/` 는 지시대로 `sync` · `freeze` 만 돌렸다. 커밋된 `_fig/*.html` 은 그 뒤 `apply` 단계(capture.js·폰트 링크 주입, value 있는 input → span 치환)까지 거친 상태라, 지금 `git diff _fig` 는 37개 파일 전부에 그 단계의 되돌림이 섞여 보인다. 내용(툴팁 문구)이 바뀐 파일은 §5 의 18개다.

## 1. 바꾼 자리 — `파일:줄` 과 전후 문구

### 생성기 (`/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/`)

| # | 파일:줄 | 전 | 후 |
|---|---|---|---|
| 1 | `build_app.py:1294` `POP_W.of` | `보유 채권 전체 (회수된 것 포함)` | `보유 채권 전체` |
| 1 | `sync_assets_static.py:181` `POP` | `보유 채권 전체 (회수된 것 포함)` | `보유 채권 전체` |
| 2 | `build_app.py:1325~1330` `thirdTh()` | 머리 `⑥ 의 ③` · 행 `번호 \| 상단 현황의 기간 전체 숫자 · 칸 미지목` | 머리 `PA · 투자실행금 · Σ A<sub>i</sub>` · 행 `행 \| 정산예정일이 그 날짜인 보유 채권` |
| 2 | `sync_profit_static.py:178~183` `THIRD_TH` | 같음 | 같음 |
| 2 | `build_sim_static.py:130~135` `THIRD_TH` | 같음 | 같음 (§0-b) |
| 2b | `build_app.py:1317~1323` `tyTh()` | 머리 `(④ ÷ ③) × 365 ÷ ⑤` · 행 `번호 \| 일별 표 열 ③투자실행금 ④투자 수익 ⑤가중평균 금융일수` · 행 `행 \| …` | 머리 `PY<sub>a</sub> · 연환산 수익률 · PMR × 365 ÷ PD` · 행 `연환산 \| 일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률` · 행 `행 \| 정산예정일이 그 날짜인 보유 채권` |
| 2b | `sync_profit_static.py:170~177` `TY_TH` | 같음 | 같음 |
| 2b | `build_sim_static.py:122~129` `TY_TH` | 같음 | 같음 (§0-b) |
| 3 | `build_app.py:1976` (투자 수익 ⑤ 툴팁) | `PEC \| 기간 순현금 · …원` | `PEC \| 검색대상기간의 누적 순현금 · …원` |
| 3 | `build_app.py:2273` `simTyTip()` | 같음 | 같음 |
| 3 | `sync_profit_static.py:188` `TIP5` | 같음 | 같음 |
| 3 | `build_sim_static.py:278` | 같음 | 같음 |
| 4 | `build_app.py:1914` 주석 | `정산예정일이 어제인 대상정산금채권을 마감한 시점의 순현금` | `정산예정일이 어제인 보유 채권을 마감한 시점의 순현금` |
| 4 | `build_app.py:2020` 주석 | `정산예정일이 어제인 대상정산금채권 집합` | `정산예정일이 어제인 보유 채권 집합` |
| §0-a | `build_app.py:1316` 주석 | `/* ⑥ 일별 Ty수익율 열 — 원문 \`(④ ÷ ③) × 365 ÷ ⑤\` 를 … 성립하지 않는다. */` (3줄) | `/* ⑥ 열머리 — 투자자어드민 기호정리표 V1.3 표 4 */` |
| §0-a | `build_app.py:1324` 주석 | `/* ③ 열머리 — 대표는 ③ 을 「상단 현황의 기간 전체 숫자」까지만 … (2026-08-31 회의 00:59:21). */` (2줄) | `/* ③ 열머리 — 투자자어드민 기호정리표 V1.3 표 4 */` |
| §0-c | `verify_crossscreen.py:350` · `:366` | `보유 채권 전체 (회수된 것 포함)` | `보유 채권 전체` |
| §0-c | `verify_proto.js:832` | `'PEC기간 순현금 · '` | `'PEC검색대상기간의 누적 순현금 · '` |

⑥ 툴팁의 「행」 행 문구 `정산예정일이 그 날짜인 보유 채권` 은 옛 ⑥ 툴팁에 있던 것을 그대로 썼고, ③ 툴팁에도 같은 마크업으로 넣었다. 「연환산」 행은 ④ 툴팁의 행과 같은 마크업·클래스(`tip-row` / `tip-green`)다.

### 출력 레포 (`/Users/semi/cursor/payhug-investor-admin/`)

| 파일 | 줄 | 내용 |
|---|---|---|
| `app.html` | 1743 · 1768~1784 · 2349 · 2411 · 2453 · 2706 | 위 생성기 변경이 그대로 실림 (POP_W · tyTh · thirdTh · 주석 2 · PEC 2) |
| `app.html` | 엑셀 매니페스트 14줄 | `made:` mtime (§0-d) |
| `invest-assets.html` | 156 · 218 | W 툴팁 (현황표 · 가맹점별) |
| `invest-assets--cert-confirm.html` | 172 · 234 | 같음 |
| `invest-assets--download.html` | 166 · 228 | 같음 |
| `invest-assets--empty.html` | 157 · 194 | 같음 |
| `invest-profit.html` | 174 · 199 · 202 | ⑤ PEC 행 · ③ 열머리 · ⑥ 열머리 |
| `invest-profit--weekly.html` | 180 · 205 · 208 | 같음 |
| `invest-profit--empty.html` | 180 · 205 · 208 | 같음 |
| `invest-profit--monthly.html` | 180 · 205 · 208 | 같음 |
| `invest-sim--result.html` | 376 · 389 | ⑤ PEC 행 · ③⑥ 열머리(한 줄) |

`README.md` · `assets/shots/*.webp` 는 재생성했으나 바이트 동일 (`git diff --stat` 에 없음).

## 2. `git diff` 전문

### 2-1. 출력 레포 `/Users/semi/cursor/payhug-investor-admin` (`git diff`, 10 파일 · +47 −50)

```diff
diff --git a/app.html b/app.html
index fe9bbb4..0bb3b2b 100644
--- a/app.html
+++ b/app.html
@@ -1587,22 +1587,22 @@ var SIGNQ = [
    두 조합(일별 일주일·금월)이 한 파일을 가리켜, 화면은 27행 금월인데 파일은 일주일치가 된다.
    `profit-status`·`profit-daily` 는 미리보기 화면을 가리키는 자리이고 파일을 갖지 않는다. */
 var XLSX = {
-  'assets-status':   {file:'투자자산현황_2026-08-27_2026-08-27.xlsx',   size:'5.6 KB', made:'2026-09-07 11:36', sheet:'투자자산 현황',   screen:'xls-assets-status',   from:'invest-assets'},
-  'assets-merchant': {file:'가맹점별투자자산_2026-08-27_2026-08-27.xlsx', size:'6.0 KB', made:'2026-09-07 11:36', sheet:'가맹점별 투자자산', screen:'xls-assets-merchant', from:'invest-assets'},
+  'assets-status':   {file:'투자자산현황_2026-08-27_2026-08-27.xlsx',   size:'5.6 KB', made:'2026-09-07 13:35', sheet:'투자자산 현황',   screen:'xls-assets-status',   from:'invest-assets'},
+  'assets-merchant': {file:'가맹점별투자자산_2026-08-27_2026-08-27.xlsx', size:'6.0 KB', made:'2026-09-07 13:35', sheet:'가맹점별 투자자산', screen:'xls-assets-merchant', from:'invest-assets'},
   'profit-status':   {screen:'xls-profit-status', from:'invest-profit'},
   'profit-daily':    {screen:'xls-profit-daily',  from:'invest-profit'},
-  'profit-daily@daily:2026-08-21:2026-08-27': {file:'일별투자수익_2026-08-21_2026-08-27.xlsx', size:'5.7 KB', made:'2026-09-07 11:36', sheet:'일별 투자수익', screen:null, from:'invest-profit'},
-  'profit-status@daily:2026-08-21:2026-08-27': {file:'투자수익현황_2026-08-21_2026-08-27.xlsx', size:'5.3 KB', made:'2026-09-07 11:36', sheet:'투자수익 현황', screen:null, from:'invest-profit'},
-  'profit-daily@daily:2026-08-01:2026-08-27': {file:'일별투자수익_2026-08-01_2026-08-27.xlsx', size:'6.6 KB', made:'2026-09-07 11:36', sheet:'일별 투자수익', screen:null, from:'invest-profit'},
-  'profit-status@daily:2026-08-01:2026-08-27': {file:'투자수익현황_2026-08-01_2026-08-27.xlsx', size:'5.3 KB', made:'2026-09-07 11:36', sheet:'투자수익 현황', screen:null, from:'invest-profit'},
-  'profit-daily@weekly:2026-08-03:2026-08-27': {file:'주별투자수익_2026-08-03_2026-08-27.xlsx', size:'5.6 KB', made:'2026-09-07 11:36', sheet:'주별 투자수익', screen:null, from:'invest-profit'},
-  'profit-status@weekly:2026-08-03:2026-08-27': {file:'투자수익현황_2026-08-03_2026-08-27.xlsx', size:'5.3 KB', made:'2026-09-07 11:36', sheet:'투자수익 현황', screen:null, from:'invest-profit'},
-  'profit-daily@weekly:2026-06-08:2026-08-27': {file:'주별투자수익_2026-06-08_2026-08-27.xlsx', size:'6.0 KB', made:'2026-09-07 11:36', sheet:'주별 투자수익', screen:null, from:'invest-profit'},
-  'profit-status@weekly:2026-06-08:2026-08-27': {file:'투자수익현황_2026-06-08_2026-08-27.xlsx', size:'5.3 KB', made:'2026-09-07 11:36', sheet:'투자수익 현황', screen:null, from:'invest-profit'},
-  'profit-daily@monthly:2026-06-01:2026-08-27': {file:'월별투자수익_2026-06-01_2026-08-27.xlsx', size:'5.6 KB', made:'2026-09-07 11:36', sheet:'월별 투자수익', screen:null, from:'invest-profit'},
-  'profit-status@monthly:2026-06-01:2026-08-27': {file:'투자수익현황_2026-06-01_2026-08-27.xlsx', size:'5.3 KB', made:'2026-09-07 11:36', sheet:'투자수익 현황', screen:null, from:'invest-profit'},
-  'profit-daily@monthly:2026-03-01:2026-08-27': {file:'월별투자수익_2026-03-01_2026-08-27.xlsx', size:'5.7 KB', made:'2026-09-07 11:36', sheet:'월별 투자수익', screen:null, from:'invest-profit'},
-  'profit-status@monthly:2026-03-01:2026-08-27': {file:'투자수익현황_2026-03-01_2026-08-27.xlsx', size:'5.3 KB', made:'2026-09-07 11:36', sheet:'투자수익 현황', screen:null, from:'invest-profit'}
+  'profit-daily@daily:2026-08-21:2026-08-27': {file:'일별투자수익_2026-08-21_2026-08-27.xlsx', size:'5.7 KB', made:'2026-09-07 13:35', sheet:'일별 투자수익', screen:null, from:'invest-profit'},
+  'profit-status@daily:2026-08-21:2026-08-27': {file:'투자수익현황_2026-08-21_2026-08-27.xlsx', size:'5.3 KB', made:'2026-09-07 13:35', sheet:'투자수익 현황', screen:null, from:'invest-profit'},
+  'profit-daily@daily:2026-08-01:2026-08-27': {file:'일별투자수익_2026-08-01_2026-08-27.xlsx', size:'6.6 KB', made:'2026-09-07 13:35', sheet:'일별 투자수익', screen:null, from:'invest-profit'},
+  'profit-status@daily:2026-08-01:2026-08-27': {file:'투자수익현황_2026-08-01_2026-08-27.xlsx', size:'5.3 KB', made:'2026-09-07 13:35', sheet:'투자수익 현황', screen:null, from:'invest-profit'},
+  'profit-daily@weekly:2026-08-03:2026-08-27': {file:'주별투자수익_2026-08-03_2026-08-27.xlsx', size:'5.6 KB', made:'2026-09-07 13:35', sheet:'주별 투자수익', screen:null, from:'invest-profit'},
+  'profit-status@weekly:2026-08-03:2026-08-27': {file:'투자수익현황_2026-08-03_2026-08-27.xlsx', size:'5.3 KB', made:'2026-09-07 13:35', sheet:'투자수익 현황', screen:null, from:'invest-profit'},
+  'profit-daily@weekly:2026-06-08:2026-08-27': {file:'주별투자수익_2026-06-08_2026-08-27.xlsx', size:'6.0 KB', made:'2026-09-07 13:35', sheet:'주별 투자수익', screen:null, from:'invest-profit'},
+  'profit-status@weekly:2026-06-08:2026-08-27': {file:'투자수익현황_2026-06-08_2026-08-27.xlsx', size:'5.3 KB', made:'2026-09-07 13:35', sheet:'투자수익 현황', screen:null, from:'invest-profit'},
+  'profit-daily@monthly:2026-06-01:2026-08-27': {file:'월별투자수익_2026-06-01_2026-08-27.xlsx', size:'5.6 KB', made:'2026-09-07 13:35', sheet:'월별 투자수익', screen:null, from:'invest-profit'},
+  'profit-status@monthly:2026-06-01:2026-08-27': {file:'투자수익현황_2026-06-01_2026-08-27.xlsx', size:'5.3 KB', made:'2026-09-07 13:35', sheet:'투자수익 현황', screen:null, from:'invest-profit'},
+  'profit-daily@monthly:2026-03-01:2026-08-27': {file:'월별투자수익_2026-03-01_2026-08-27.xlsx', size:'5.7 KB', made:'2026-09-07 13:35', sheet:'월별 투자수익', screen:null, from:'invest-profit'},
+  'profit-status@monthly:2026-03-01:2026-08-27': {file:'투자수익현황_2026-03-01_2026-08-27.xlsx', size:'5.3 KB', made:'2026-09-07 13:35', sheet:'투자수익 현황', screen:null, from:'invest-profit'}
 };
 
 /* 지금 보고 있는 기간·집계 단위의 파일을 고른다. 프리셋 밖 기간(직접입력)에는 실물이 없어 null 이다 —
@@ -1740,7 +1740,7 @@ function wavg(a, k, wk){ var n=0, d=0; for(var i=0;i<a.length;i++){ n += a[i][k]
    옆 칸 금액(미회수 Σ A<sub>i</sub>)까지 셋이 각자 다른 집합에서 나오므로, 행을 금액으로 가중평균해도
    현황표의 두 칸과 맞아떨어지지 않는다. 그 모집단을 열머리 툴팁이 그대로 적는다.
    건수는 채권 원장 실측이다(daily_ledger.py) — 화면에 손으로 적지 않는다. */
-var POP_W = {of:'보유 채권 전체 (회수된 것 포함)', n:'61,760건'};
+var POP_W = {of:'보유 채권 전체', n:'61,760건'};
 var POP_S = {of:'선정산일이 오늘 기준 20일 전 ~ 11일 전인 표본', n:'3,200건'};
 function popTh(label, p){
   return '<th class="num"><span class="tooltip wide"><span class="tip-anchor">' + label + '</span>' +
@@ -1765,22 +1765,19 @@ var TY6_PSC = 0;   /* ⑥ 이 ⑤ 를 거칠 때 넣는 PEC — 일별 EC 원장
 function ty6(profit, execu, w){ var third = ty3(execu);
   if(!(third && w)) return 0;
   return ty5(r6(profit / third * 100) * 365 / w, third * w, TY6_PSC); }
-/* ⑥ 일별 Ty수익율 열 — 원문 `(④ ÷ ③) × 365 ÷ ⑤` 를 일별 표의 열 번호로 읽은 것이다.
-   현황 카드 번호(④ 투자실행금액 대비 · ⑤ 투자자산 대비)를 그대로 넣으면
-   `수익률 ÷ 금액 × 365 ÷ 수익률` 이 되어 성립하지 않는다. */
+/* ⑥ 열머리 — 투자자어드민 기호정리표 V1.3 표 4 */
 function tyTh(){
   return '<th class="num"><span class="tooltip wide"><span class="tip-anchor">연환산 수익률</span>' +
-         '<span class="tip-panel">(④ ÷ ③) × 365 ÷ ⑤' +
-           '<span class="tip-row"><span>번호</span><span class="tip-green">일별 표 열 ③투자실행금 ④투자 수익 ⑤가중평균 금융일수</span></span>' +
+         '<span class="tip-panel">PY<sub>a</sub> · 연환산 수익률 · PMR × 365 ÷ PD' +
+           '<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span>' +
            '<span class="tip-row"><span>행</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span>' +
          '</span></span></th>';
 }
-/* ③ 열머리 — 대표는 ③ 을 「상단 현황의 기간 전체 숫자」까지만 좁혔고 어느 칸인지는 지목하지 않았다
-   (2026-08-31 회의 00:59:21). */
+/* ③ 열머리 — 투자자어드민 기호정리표 V1.3 표 4 */
 function thirdTh(){
   return '<th class="num"><span class="tooltip wide"><span class="tip-anchor">투자실행금</span>' +
-         '<span class="tip-panel">⑥ 의 ③' +
-           '<span class="tip-row"><span>번호</span><span class="tip-green">상단 현황의 기간 전체 숫자 · 칸 미지목</span></span>' +
+         '<span class="tip-panel">PA · 투자실행금 · Σ A<sub>i</sub>' +
+           '<span class="tip-row"><span>행</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span>' +
          '</span></span></th>';
 }
 function esc(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
@@ -2349,7 +2346,7 @@ function cashRow(){
    산식은 ty5() 한 곳에 있다(생성기 daily_ledger.ty_asset). 여기는 AD·PEC 를 만들어 넘기기만 한다.
    AD = 기간 Σ(A_i x D_i) — 행마다 실린 ad 의 합(PwD 의 분자), PEC = 기간 동안 EC들의 합.
    ty5() 의 매개변수 이름 ad·psc 는 daily_ledger.TY5_EXPR 한 줄에 묶여 있어 그대로 둔다.
-   EC = 정산예정일이 어제인 대상정산금채권을 마감한 시점의 순현금이며 하루에 한 건 쌓인다(유량).
+   EC = 정산예정일이 어제인 보유 채권을 마감한 시점의 순현금이며 하루에 한 건 쌓인다(유량).
    기준일 잔액 1개(스톡)로 나누지 않는다.
    일별 EC 원장이 없어 EC 는 순현금 잔액으로 고정한다 — 실데이터 연결은 확인 대상. */
 /* EC 는 하루에 한 건 쌓이는 유량이라 조회 기간에 걸린 일수만큼 센다.
@@ -2411,7 +2408,7 @@ RENDER['invest-profit'] = function(){
           '<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span>' +
           '<span class="tip-row"><span>PY<sub>a</sub></span><span class="tip-green">투자실행금액 대비 연환산 수익률 · ' + fx(tyExec, 2) + '%</span></span>' +
           '<span class="tip-row"><span>Σ( A<sub>i</sub> × D<sub>i</sub> )</span><span class="tip-green">' + fmt(adOfRows(rows)) + '원</span></span>' +
-          '<span class="tip-row"><span>PEC</span><span class="tip-green">기간 순현금 · ' + fmt((cashRow() ? cashRow().amount : 0) * ecDays()) + '원</span></span>' +
+          '<span class="tip-row"><span>PEC</span><span class="tip-green">검색대상기간의 누적 순현금 · ' + fmt((cashRow() ? cashRow().amount : 0) * ecDays()) + '원</span></span>' +
           '<span class="tip-row sum"><span>EC</span><span>순현금 · ' + fmt(cashRow() ? cashRow().amount : 0) + '원 × ' + ecDays() + '일</span></span>' +
         '</span></span></div>' +
         '<div class="summary-value">' + fx(tyAsset, 2) + '<span class="unit">%</span></div></div>' +
@@ -2453,7 +2450,7 @@ RENDER['invest-profit'] = function(){
    기존 화면과 완전히 별개다. SIM 은 IA·PF·MC·AQ·CT 와 독립된 상태 객체이고
    simRun() 은 MERCHANTS·ASSET_ROWS·DAILY 를 읽지도 쓰지도 않는다.
    산식 출처 — 대표 정의서 [1번 이미지] A<sub>i</sub>·D<sub>i</sub>·w·ty·S · [2번 이미지] M<sub>d−1,&thinsp;i</sub>·B<sub>d−1,&thinsp;i</sub>·PSA·PSM·PSD·PSMR·PSC.
-   대문자 D 는 금융일수, 소문자 d 는 오늘 날짜다. d−1 은 어제 날짜가 아니라 정산예정일이 어제인 대상정산금채권 집합을 가리킨다.
+   대문자 D 는 금융일수, 소문자 d 는 오늘 날짜다. d−1 은 어제 날짜가 아니라 정산예정일이 어제인 보유 채권 집합을 가리킨다.
    앵커는 순지급액이다(채권매입수수료 = 순지급액 x 할인율 · D-31). 일별 원장 daily_ledger.py 도 같은 앵커라
    투자 수익 화면과 이 화면의 같은 열은 같은 산식에서 나온다. */
 var SIM_PLAT = [
@@ -2706,7 +2703,7 @@ function simTyTip(R){
         '<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span>' +
         '<span class="tip-row"><span>PY<sub>a</sub></span><span class="tip-green">투자실행금액 대비 연환산 수익률 · ' + fx(R.TY4, 2) + '%</span></span>' +
         '<span class="tip-row"><span>Σ( A<sub>i</sub> × D<sub>i</sub> )</span><span class="tip-green">' + fmt(R.AD) + '원</span></span>' +
-        '<span class="tip-row"><span>PEC</span><span class="tip-green">기간 순현금 · ' + fmt(R.PEC) + '원</span></span>' +
+        '<span class="tip-row"><span>PEC</span><span class="tip-green">검색대상기간의 누적 순현금 · ' + fmt(R.PEC) + '원</span></span>' +
         '<span class="tip-row sum"><span>EC</span><span>순현금 · ' + fmt(R.cash) + '원 × ' + R.ECD + '일</span></span>' +
       '</span></span></div>' +
       '<div class="summary-value' + (R.TY5 < 0 ? ' neg' : '') + '">' + fx(R.TY5, 2) + '<span class="unit">%</span></div></div>' +
diff --git a/invest-assets--cert-confirm.html b/invest-assets--cert-confirm.html
index 03544ed..f2f0be3 100644
--- a/invest-assets--cert-confirm.html
+++ b/invest-assets--cert-confirm.html
@@ -169,7 +169,7 @@
             <tr>
               <th>자산 구분</th>
               <th class="num">금액 (원)</th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">가중평균 금융일수</span><span class="tip-panel">보유 채권 전체 (회수된 것 포함)<span class="tip-row"><span>채권 건수</span><span class="tip-green">61,760건</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">가중평균 금융일수</span><span class="tip-panel">보유 채권 전체<span class="tip-row"><span>채권 건수</span><span class="tip-green">61,760건</span></span></span></span></th>
               <th class="num"><span class="tooltip wide"><span class="tip-anchor">입금부족률</span><span class="tip-panel">선정산일이 오늘 기준 20일 전 ~ 11일 전인 표본<span class="tip-row"><span>채권 건수</span><span class="tip-green">3,200건</span></span></span></span></th>
               <th class="num"><span class="tooltip wide"><span class="tip-anchor">예상 연환산 수익률</span><span class="tip-panel">Y<sub>r</sub> · 예상 연환산 수익률 · r × 365 ÷ D<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></th>
               <th class="num">비중</th>
@@ -231,7 +231,7 @@
             <tr>
               <th>가맹점</th>
               <th class="num">투자실행액 (원)</th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">가중평균 금융일수</span><span class="tip-panel">보유 채권 전체 (회수된 것 포함)<span class="tip-row"><span>채권 건수</span><span class="tip-green">61,760건</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">가중평균 금융일수</span><span class="tip-panel">보유 채권 전체<span class="tip-row"><span>채권 건수</span><span class="tip-green">61,760건</span></span></span></span></th>
               <th class="num"><span class="tooltip wide"><span class="tip-anchor">입금부족률</span><span class="tip-panel">선정산일이 오늘 기준 20일 전 ~ 11일 전인 표본<span class="tip-row"><span>채권 건수</span><span class="tip-green">3,200건</span></span></span></span></th>
               <th class="num"><span class="tooltip wide"><span class="tip-anchor">예상 연환산 수익률</span><span class="tip-panel">Y<sub>r</sub> · 예상 연환산 수익률 · r × 365 ÷ D<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></th>
               <th class="num">비중</th>
diff --git a/invest-assets--download.html b/invest-assets--download.html
index 9815a3c..b68b167 100644
--- a/invest-assets--download.html
+++ b/invest-assets--download.html
@@ -163,7 +163,7 @@
             <tr>
               <th>자산 구분</th>
               <th class="num">금액 (원)</th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">가중평균 금융일수</span><span class="tip-panel">보유 채권 전체 (회수된 것 포함)<span class="tip-row"><span>채권 건수</span><span class="tip-green">61,760건</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">가중평균 금융일수</span><span class="tip-panel">보유 채권 전체<span class="tip-row"><span>채권 건수</span><span class="tip-green">61,760건</span></span></span></span></th>
               <th class="num"><span class="tooltip wide"><span class="tip-anchor">입금부족률</span><span class="tip-panel">선정산일이 오늘 기준 20일 전 ~ 11일 전인 표본<span class="tip-row"><span>채권 건수</span><span class="tip-green">3,200건</span></span></span></span></th>
               <th class="num"><span class="tooltip wide"><span class="tip-anchor">예상 연환산 수익률</span><span class="tip-panel">Y<sub>r</sub> · 예상 연환산 수익률 · r × 365 ÷ D<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></th>
               <th class="num">비중</th>
@@ -225,7 +225,7 @@
             <tr>
               <th>가맹점</th>
               <th class="num">투자실행액 (원)</th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">가중평균 금융일수</span><span class="tip-panel">보유 채권 전체 (회수된 것 포함)<span class="tip-row"><span>채권 건수</span><span class="tip-green">61,760건</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">가중평균 금융일수</span><span class="tip-panel">보유 채권 전체<span class="tip-row"><span>채권 건수</span><span class="tip-green">61,760건</span></span></span></span></th>
               <th class="num"><span class="tooltip wide"><span class="tip-anchor">입금부족률</span><span class="tip-panel">선정산일이 오늘 기준 20일 전 ~ 11일 전인 표본<span class="tip-row"><span>채권 건수</span><span class="tip-green">3,200건</span></span></span></span></th>
               <th class="num"><span class="tooltip wide"><span class="tip-anchor">예상 연환산 수익률</span><span class="tip-panel">Y<sub>r</sub> · 예상 연환산 수익률 · r × 365 ÷ D<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></th>
               <th class="num">비중</th>
diff --git a/invest-assets--empty.html b/invest-assets--empty.html
index 2845f84..478193e 100644
--- a/invest-assets--empty.html
+++ b/invest-assets--empty.html
@@ -154,7 +154,7 @@
             <tr>
               <th>자산 구분</th>
               <th class="num">금액 (원)</th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">가중평균 금융일수</span><span class="tip-panel">보유 채권 전체 (회수된 것 포함)<span class="tip-row"><span>채권 건수</span><span class="tip-green">61,760건</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">가중평균 금융일수</span><span class="tip-panel">보유 채권 전체<span class="tip-row"><span>채권 건수</span><span class="tip-green">61,760건</span></span></span></span></th>
               <th class="num"><span class="tooltip wide"><span class="tip-anchor">입금부족률</span><span class="tip-panel">선정산일이 오늘 기준 20일 전 ~ 11일 전인 표본<span class="tip-row"><span>채권 건수</span><span class="tip-green">3,200건</span></span></span></span></th>
               <th class="num"><span class="tooltip wide"><span class="tip-anchor">예상 연환산 수익률</span><span class="tip-panel">Y<sub>r</sub> · 예상 연환산 수익률 · r × 365 ÷ D<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></th>
               <th class="num">비중</th>
@@ -191,7 +191,7 @@
             <tr>
               <th>가맹점</th>
               <th class="num">투자실행액 (원)</th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">가중평균 금융일수</span><span class="tip-panel">보유 채권 전체 (회수된 것 포함)<span class="tip-row"><span>채권 건수</span><span class="tip-green">61,760건</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">가중평균 금융일수</span><span class="tip-panel">보유 채권 전체<span class="tip-row"><span>채권 건수</span><span class="tip-green">61,760건</span></span></span></span></th>
               <th class="num"><span class="tooltip wide"><span class="tip-anchor">입금부족률</span><span class="tip-panel">선정산일이 오늘 기준 20일 전 ~ 11일 전인 표본<span class="tip-row"><span>채권 건수</span><span class="tip-green">3,200건</span></span></span></span></th>
               <th class="num"><span class="tooltip wide"><span class="tip-anchor">예상 연환산 수익률</span><span class="tip-panel">Y<sub>r</sub> · 예상 연환산 수익률 · r × 365 ÷ D<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></th>
               <th class="num">비중</th>
diff --git a/invest-assets.html b/invest-assets.html
index b32ac85..a775221 100644
--- a/invest-assets.html
+++ b/invest-assets.html
@@ -153,7 +153,7 @@
             <tr>
               <th>자산 구분</th>
               <th class="num">금액 (원)</th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">가중평균 금융일수</span><span class="tip-panel">보유 채권 전체 (회수된 것 포함)<span class="tip-row"><span>채권 건수</span><span class="tip-green">61,760건</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">가중평균 금융일수</span><span class="tip-panel">보유 채권 전체<span class="tip-row"><span>채권 건수</span><span class="tip-green">61,760건</span></span></span></span></th>
               <th class="num"><span class="tooltip wide"><span class="tip-anchor">입금부족률</span><span class="tip-panel">선정산일이 오늘 기준 20일 전 ~ 11일 전인 표본<span class="tip-row"><span>채권 건수</span><span class="tip-green">3,200건</span></span></span></span></th>
               <th class="num"><span class="tooltip wide"><span class="tip-anchor">예상 연환산 수익률</span><span class="tip-panel">Y<sub>r</sub> · 예상 연환산 수익률 · r × 365 ÷ D<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></th>
               <th class="num">비중</th>
@@ -215,7 +215,7 @@
             <tr>
               <th>가맹점</th>
               <th class="num">투자실행액 (원)</th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">가중평균 금융일수</span><span class="tip-panel">보유 채권 전체 (회수된 것 포함)<span class="tip-row"><span>채권 건수</span><span class="tip-green">61,760건</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">가중평균 금융일수</span><span class="tip-panel">보유 채권 전체<span class="tip-row"><span>채권 건수</span><span class="tip-green">61,760건</span></span></span></span></th>
               <th class="num"><span class="tooltip wide"><span class="tip-anchor">입금부족률</span><span class="tip-panel">선정산일이 오늘 기준 20일 전 ~ 11일 전인 표본<span class="tip-row"><span>채권 건수</span><span class="tip-green">3,200건</span></span></span></span></th>
               <th class="num"><span class="tooltip wide"><span class="tip-anchor">예상 연환산 수익률</span><span class="tip-panel">Y<sub>r</sub> · 예상 연환산 수익률 · r × 365 ÷ D<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></th>
               <th class="num">비중</th>
diff --git a/invest-profit--empty.html b/invest-profit--empty.html
index 8470bfb..92b92fe 100644
--- a/invest-profit--empty.html
+++ b/invest-profit--empty.html
@@ -177,7 +177,7 @@
               <div class="summary-value">0.00<span class="unit">%</span></div>
             </div>
             <div>
-              <div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자 자산 대비</span><span class="tip-panel">PY<sub>t</sub> · 투자 자산 대비 연환산 수익률 · PM × 365 ÷ ( Σ( A<sub>i</sub> × D<sub>i</sub> ) + PEC )<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span><span class="tip-row"><span>PY<sub>a</sub></span><span class="tip-green">투자실행금액 대비 연환산 수익률 · 0%</span></span><span class="tip-row"><span>Σ( A<sub>i</sub> × D<sub>i</sub> )</span><span class="tip-green">0원</span></span><span class="tip-row"><span>PEC</span><span class="tip-green">기간 순현금 · 0원</span></span><span class="tip-row sum"><span>EC</span><span>순현금 · 20,000,000원 × 0일</span></span></span></span></div>
+              <div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자 자산 대비</span><span class="tip-panel">PY<sub>t</sub> · 투자 자산 대비 연환산 수익률 · PM × 365 ÷ ( Σ( A<sub>i</sub> × D<sub>i</sub> ) + PEC )<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span><span class="tip-row"><span>PY<sub>a</sub></span><span class="tip-green">투자실행금액 대비 연환산 수익률 · 0%</span></span><span class="tip-row"><span>Σ( A<sub>i</sub> × D<sub>i</sub> )</span><span class="tip-green">0원</span></span><span class="tip-row"><span>PEC</span><span class="tip-green">검색대상기간의 누적 순현금 · 0원</span></span><span class="tip-row sum"><span>EC</span><span>순현금 · 20,000,000원 × 0일</span></span></span></span></div>
               <div class="summary-value">0.00<span class="unit">%</span></div>
             </div>
           </div>
@@ -202,10 +202,10 @@
             <tr>
               <th>정산예정일</th>
               <th class="num">상환액</th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">투자실행금</span><span class="tip-panel">⑥ 의 ③<span class="tip-row"><span>번호</span><span class="tip-green">상단 현황의 기간 전체 숫자 · 칸 미지목</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">투자실행금</span><span class="tip-panel">PA · 투자실행금 · Σ A<sub>i</sub><span class="tip-row"><span>행</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span></span></span></th>
               <th class="num">투자 수익</th>
               <th class="num">가중평균 금융일수</th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">연환산 수익률</span><span class="tip-panel">(④ ÷ ③) × 365 ÷ ⑤<span class="tip-row"><span>번호</span><span class="tip-green">일별 표 열 ③투자실행금 ④투자 수익 ⑤가중평균 금융일수</span></span><span class="tip-row"><span>행</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">연환산 수익률</span><span class="tip-panel">PY<sub>a</sub> · 연환산 수익률 · PMR × 365 ÷ PD<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span><span class="tip-row"><span>행</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span></span></span></th>
             </tr>
           </thead>
           <tbody>
diff --git a/invest-profit--monthly.html b/invest-profit--monthly.html
index 489ab2f..7531ac6 100644
--- a/invest-profit--monthly.html
+++ b/invest-profit--monthly.html
@@ -177,7 +177,7 @@
               <div class="summary-value">4.57<span class="unit">%</span></div>
             </div>
             <div>
-              <div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자 자산 대비</span><span class="tip-panel">PY<sub>t</sub> · 투자 자산 대비 연환산 수익률 · PM × 365 ÷ ( Σ( A<sub>i</sub> × D<sub>i</sub> ) + PEC )<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span><span class="tip-row"><span>PY<sub>a</sub></span><span class="tip-green">투자실행금액 대비 연환산 수익률 · 4.57%</span></span><span class="tip-row"><span>Σ( A<sub>i</sub> × D<sub>i</sub> )</span><span class="tip-green">14,262,370,838원</span></span><span class="tip-row"><span>PEC</span><span class="tip-green">기간 순현금 · 3,600,000,000원</span></span><span class="tip-row sum"><span>EC</span><span>순현금 · 20,000,000원 × 180일</span></span></span></span></div>
+              <div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자 자산 대비</span><span class="tip-panel">PY<sub>t</sub> · 투자 자산 대비 연환산 수익률 · PM × 365 ÷ ( Σ( A<sub>i</sub> × D<sub>i</sub> ) + PEC )<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span><span class="tip-row"><span>PY<sub>a</sub></span><span class="tip-green">투자실행금액 대비 연환산 수익률 · 4.57%</span></span><span class="tip-row"><span>Σ( A<sub>i</sub> × D<sub>i</sub> )</span><span class="tip-green">14,262,370,838원</span></span><span class="tip-row"><span>PEC</span><span class="tip-green">검색대상기간의 누적 순현금 · 3,600,000,000원</span></span><span class="tip-row sum"><span>EC</span><span>순현금 · 20,000,000원 × 180일</span></span></span></span></div>
               <div class="summary-value">3.65<span class="unit">%</span></div>
             </div>
           </div>
@@ -202,10 +202,10 @@
             <tr>
               <th>정산예정월</th>
               <th class="num">상환액</th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">투자실행금</span><span class="tip-panel">⑥ 의 ③<span class="tip-row"><span>번호</span><span class="tip-green">상단 현황의 기간 전체 숫자 · 칸 미지목</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">투자실행금</span><span class="tip-panel">PA · 투자실행금 · Σ A<sub>i</sub><span class="tip-row"><span>행</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span></span></span></th>
               <th class="num">투자 수익</th>
               <th class="num">가중평균 금융일수</th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">연환산 수익률</span><span class="tip-panel">(④ ÷ ③) × 365 ÷ ⑤<span class="tip-row"><span>번호</span><span class="tip-green">일별 표 열 ③투자실행금 ④투자 수익 ⑤가중평균 금융일수</span></span><span class="tip-row"><span>행</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">연환산 수익률</span><span class="tip-panel">PY<sub>a</sub> · 연환산 수익률 · PMR × 365 ÷ PD<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span><span class="tip-row"><span>행</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span></span></span></th>
             </tr>
           </thead>
           <tbody>
diff --git a/invest-profit--weekly.html b/invest-profit--weekly.html
index 125c288..8e1e35a 100644
--- a/invest-profit--weekly.html
+++ b/invest-profit--weekly.html
@@ -177,7 +177,7 @@
               <div class="summary-value">4.62<span class="unit">%</span></div>
             </div>
             <div>
-              <div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자 자산 대비</span><span class="tip-panel">PY<sub>t</sub> · 투자 자산 대비 연환산 수익률 · PM × 365 ÷ ( Σ( A<sub>i</sub> × D<sub>i</sub> ) + PEC )<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span><span class="tip-row"><span>PY<sub>a</sub></span><span class="tip-green">투자실행금액 대비 연환산 수익률 · 4.62%</span></span><span class="tip-row"><span>Σ( A<sub>i</sub> × D<sub>i</sub> )</span><span class="tip-green">1,965,572,846원</span></span><span class="tip-row"><span>PEC</span><span class="tip-green">기간 순현금 · 500,000,000원</span></span><span class="tip-row sum"><span>EC</span><span>순현금 · 20,000,000원 × 25일</span></span></span></span></div>
+              <div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자 자산 대비</span><span class="tip-panel">PY<sub>t</sub> · 투자 자산 대비 연환산 수익률 · PM × 365 ÷ ( Σ( A<sub>i</sub> × D<sub>i</sub> ) + PEC )<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span><span class="tip-row"><span>PY<sub>a</sub></span><span class="tip-green">투자실행금액 대비 연환산 수익률 · 4.62%</span></span><span class="tip-row"><span>Σ( A<sub>i</sub> × D<sub>i</sub> )</span><span class="tip-green">1,965,572,846원</span></span><span class="tip-row"><span>PEC</span><span class="tip-green">검색대상기간의 누적 순현금 · 500,000,000원</span></span><span class="tip-row sum"><span>EC</span><span>순현금 · 20,000,000원 × 25일</span></span></span></span></div>
               <div class="summary-value">3.68<span class="unit">%</span></div>
             </div>
           </div>
@@ -202,10 +202,10 @@
             <tr>
               <th>정산예정주</th>
               <th class="num">상환액</th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">투자실행금</span><span class="tip-panel">⑥ 의 ③<span class="tip-row"><span>번호</span><span class="tip-green">상단 현황의 기간 전체 숫자 · 칸 미지목</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">투자실행금</span><span class="tip-panel">PA · 투자실행금 · Σ A<sub>i</sub><span class="tip-row"><span>행</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span></span></span></th>
               <th class="num">투자 수익</th>
               <th class="num">가중평균 금융일수</th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">연환산 수익률</span><span class="tip-panel">(④ ÷ ③) × 365 ÷ ⑤<span class="tip-row"><span>번호</span><span class="tip-green">일별 표 열 ③투자실행금 ④투자 수익 ⑤가중평균 금융일수</span></span><span class="tip-row"><span>행</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">연환산 수익률</span><span class="tip-panel">PY<sub>a</sub> · 연환산 수익률 · PMR × 365 ÷ PD<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span><span class="tip-row"><span>행</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span></span></span></th>
             </tr>
           </thead>
           <tbody>
diff --git a/invest-profit.html b/invest-profit.html
index 84d914b..33ab59a 100644
--- a/invest-profit.html
+++ b/invest-profit.html
@@ -171,7 +171,7 @@
               <div class="summary-value">3.99<span class="unit">%</span></div>
             </div>
             <div>
-              <div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자 자산 대비</span><span class="tip-panel">PY<sub>t</sub> · 투자 자산 대비 연환산 수익률 · PM × 365 ÷ ( Σ( A<sub>i</sub> × D<sub>i</sub> ) + PEC )<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span><span class="tip-row"><span>PY<sub>a</sub></span><span class="tip-green">투자실행금액 대비 연환산 수익률 · 3.99%</span></span><span class="tip-row"><span>Σ( A<sub>i</sub> × D<sub>i</sub> )</span><span class="tip-green">559,275,516원</span></span><span class="tip-row"><span>PEC</span><span class="tip-green">기간 순현금 · 140,000,000원</span></span><span class="tip-row sum"><span>EC</span><span>순현금 · 20,000,000원 × 7일</span></span></span></span></div>
+              <div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자 자산 대비</span><span class="tip-panel">PY<sub>t</sub> · 투자 자산 대비 연환산 수익률 · PM × 365 ÷ ( Σ( A<sub>i</sub> × D<sub>i</sub> ) + PEC )<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span><span class="tip-row"><span>PY<sub>a</sub></span><span class="tip-green">투자실행금액 대비 연환산 수익률 · 3.99%</span></span><span class="tip-row"><span>Σ( A<sub>i</sub> × D<sub>i</sub> )</span><span class="tip-green">559,275,516원</span></span><span class="tip-row"><span>PEC</span><span class="tip-green">검색대상기간의 누적 순현금 · 140,000,000원</span></span><span class="tip-row sum"><span>EC</span><span>순현금 · 20,000,000원 × 7일</span></span></span></span></div>
               <div class="summary-value">3.19<span class="unit">%</span></div>
             </div>
           </div>
@@ -196,10 +196,10 @@
             <tr>
               <th>정산예정일</th>
               <th class="num">상환액</th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">투자실행금</span><span class="tip-panel">⑥ 의 ③<span class="tip-row"><span>번호</span><span class="tip-green">상단 현황의 기간 전체 숫자 · 칸 미지목</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">투자실행금</span><span class="tip-panel">PA · 투자실행금 · Σ A<sub>i</sub><span class="tip-row"><span>행</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span></span></span></th>
               <th class="num">투자 수익</th>
               <th class="num">가중평균 금융일수</th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">연환산 수익률</span><span class="tip-panel">(④ ÷ ③) × 365 ÷ ⑤<span class="tip-row"><span>번호</span><span class="tip-green">일별 표 열 ③투자실행금 ④투자 수익 ⑤가중평균 금융일수</span></span><span class="tip-row"><span>행</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">연환산 수익률</span><span class="tip-panel">PY<sub>a</sub> · 연환산 수익률 · PMR × 365 ÷ PD<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span><span class="tip-row"><span>행</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span></span></span></th>
             </tr>
           </thead>
           <tbody>
diff --git a/invest-sim--result.html b/invest-sim--result.html
index d29a66c..e8f166d 100644
--- a/invest-sim--result.html
+++ b/invest-sim--result.html
@@ -373,7 +373,7 @@
               <div class="summary-value">4.81<span class="unit">%</span></div>
             </div>
             <div>
-              <div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자 자산 대비</span><span class="tip-panel">PY<sub>t</sub> · 투자 자산 대비 연환산 수익률 · PM × 365 ÷ ( Σ( A<sub>i</sub> × D<sub>i</sub> ) + PEC )<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span><span class="tip-row"><span>PY<sub>a</sub></span><span class="tip-green">투자실행금액 대비 연환산 수익률 · 4.81%</span></span><span class="tip-row"><span>Σ( A<sub>i</sub> × D<sub>i</sub> )</span><span class="tip-green">121,466,240원</span></span><span class="tip-row"><span>PEC</span><span class="tip-green">기간 순현금 · 140,000,000원</span></span><span class="tip-row sum"><span>EC</span><span>순현금 · 20,000,000원 × 7일</span></span></span></span></div>
+              <div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자 자산 대비</span><span class="tip-panel">PY<sub>t</sub> · 투자 자산 대비 연환산 수익률 · PM × 365 ÷ ( Σ( A<sub>i</sub> × D<sub>i</sub> ) + PEC )<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span><span class="tip-row"><span>PY<sub>a</sub></span><span class="tip-green">투자실행금액 대비 연환산 수익률 · 4.81%</span></span><span class="tip-row"><span>Σ( A<sub>i</sub> × D<sub>i</sub> )</span><span class="tip-green">121,466,240원</span></span><span class="tip-row"><span>PEC</span><span class="tip-green">검색대상기간의 누적 순현금 · 140,000,000원</span></span><span class="tip-row sum"><span>EC</span><span>순현금 · 20,000,000원 × 7일</span></span></span></span></div>
               <div class="summary-value">2.23<span class="unit">%</span></div>
             </div>
           </div>
@@ -386,7 +386,7 @@
       <div class="tbl-scroll">
         <table class="tbl">
           <thead>
-            <tr><th>정산예정일</th><th class="num">상환액</th><th class="num"><span class="tooltip wide"><span class="tip-anchor">투자실행금</span><span class="tip-panel">⑥ 의 ③<span class="tip-row"><span>번호</span><span class="tip-green">상단 현황의 기간 전체 숫자 · 칸 미지목</span></span></span></span></th><th class="num">투자 수익</th><th class="num">가중평균 금융일수</th><th class="num"><span class="tooltip wide"><span class="tip-anchor">연환산 수익률</span><span class="tip-panel">(④ ÷ ③) × 365 ÷ ⑤<span class="tip-row"><span>번호</span><span class="tip-green">일별 표 열 ③투자실행금 ④투자 수익 ⑤가중평균 금융일수</span></span><span class="tip-row"><span>행</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span></span></span></th></tr>
+            <tr><th>정산예정일</th><th class="num">상환액</th><th class="num"><span class="tooltip wide"><span class="tip-anchor">투자실행금</span><span class="tip-panel">PA · 투자실행금 · Σ A<sub>i</sub><span class="tip-row"><span>행</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span></span></span></th><th class="num">투자 수익</th><th class="num">가중평균 금융일수</th><th class="num"><span class="tooltip wide"><span class="tip-anchor">연환산 수익률</span><span class="tip-panel">PY<sub>a</sub> · 연환산 수익률 · PMR × 365 ÷ PD<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span><span class="tip-row"><span>행</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span></span></span></th></tr>
           </thead>
           <tbody>
             <tr><td class="mono">2026-08-24</td><td class="num">15,189,360</td><td class="num">15,183,280</td><td class="num"><span class="strong">6,080</span></td><td class="num">2.00</td><td class="num">7.31%</td></tr>
```

### 2-2. 생성기·검증기 `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin` (`git diff`, 6 파일)

```diff
diff --git a/payhug-spec/_pipeline/investor_admin/build_app.py b/payhug-spec/_pipeline/investor_admin/build_app.py
index 6380ac2..4f5cd00 100644
--- a/payhug-spec/_pipeline/investor_admin/build_app.py
+++ b/payhug-spec/_pipeline/investor_admin/build_app.py
@@ -1291,7 +1291,7 @@ function wavg(a, k, wk){ var n=0, d=0; for(var i=0;i<a.length;i++){ n += a[i][k]
    옆 칸 금액(미회수 Σ A<sub>i</sub>)까지 셋이 각자 다른 집합에서 나오므로, 행을 금액으로 가중평균해도
    현황표의 두 칸과 맞아떨어지지 않는다. 그 모집단을 열머리 툴팁이 그대로 적는다.
    건수는 채권 원장 실측이다(daily_ledger.py) — 화면에 손으로 적지 않는다. */
-var POP_W = {of:'보유 채권 전체 (회수된 것 포함)', n:'@@POPW@@'};
+var POP_W = {of:'보유 채권 전체', n:'@@POPW@@'};
 var POP_S = {of:'선정산일이 오늘 기준 20일 전 ~ 11일 전인 표본', n:'@@POPS@@'};
 function popTh(label, p){
   return '<th class="num"><span class="tooltip wide"><span class="tip-anchor">' + label + '</span>' +
@@ -1313,22 +1313,19 @@ function ty3(execu){ @@TY3JS@@ }
 function ty5(ty4, ad, psc){ @@TY5JS@@ }
 var TY6_PSC = @@TY6PSC@@;   /* ⑥ 이 ⑤ 를 거칠 때 넣는 PEC — 일별 EC 원장이 없어 0 이다 */
 function ty6(profit, execu, w){ @@TY6JS@@ }
-/* ⑥ 일별 Ty수익율 열 — 원문 `(④ ÷ ③) × 365 ÷ ⑤` 를 일별 표의 열 번호로 읽은 것이다.
-   현황 카드 번호(④ 투자실행금액 대비 · ⑤ 투자자산 대비)를 그대로 넣으면
-   `수익률 ÷ 금액 × 365 ÷ 수익률` 이 되어 성립하지 않는다. */
+/* ⑥ 열머리 — 투자자어드민 기호정리표 V1.3 표 4 */
 function tyTh(){
   return '<th class="num"><span class="tooltip wide"><span class="tip-anchor">연환산 수익률</span>' +
-         '<span class="tip-panel">(④ ÷ ③) × 365 ÷ ⑤' +
-           '<span class="tip-row"><span>번호</span><span class="tip-green">일별 표 열 ③투자실행금 ④투자 수익 ⑤가중평균 금융일수</span></span>' +
+         '<span class="tip-panel">PY<sub>a</sub> · 연환산 수익률 · PMR × 365 ÷ PD' +
+           '<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span>' +
            '<span class="tip-row"><span>행</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span>' +
          '</span></span></th>';
 }
-/* ③ 열머리 — 대표는 ③ 을 「상단 현황의 기간 전체 숫자」까지만 좁혔고 어느 칸인지는 지목하지 않았다
-   (2026-08-31 회의 00:59:21). */
+/* ③ 열머리 — 투자자어드민 기호정리표 V1.3 표 4 */
 function thirdTh(){
   return '<th class="num"><span class="tooltip wide"><span class="tip-anchor">투자실행금</span>' +
-         '<span class="tip-panel">⑥ 의 ③' +
-           '<span class="tip-row"><span>번호</span><span class="tip-green">상단 현황의 기간 전체 숫자 · 칸 미지목</span></span>' +
+         '<span class="tip-panel">PA · 투자실행금 · Σ A<sub>i</sub>' +
+           '<span class="tip-row"><span>행</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span>' +
          '</span></span></th>';
 }
 function esc(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
@@ -1914,7 +1911,7 @@ function cashRow(){
    산식은 ty5() 한 곳에 있다(생성기 daily_ledger.ty_asset). 여기는 AD·PEC 를 만들어 넘기기만 한다.
    AD = 기간 Σ(A_i x D_i) — 행마다 실린 ad 의 합(PwD 의 분자), PEC = 기간 동안 EC들의 합.
    ty5() 의 매개변수 이름 ad·psc 는 daily_ledger.TY5_EXPR 한 줄에 묶여 있어 그대로 둔다.
-   EC = 정산예정일이 어제인 대상정산금채권을 마감한 시점의 순현금이며 하루에 한 건 쌓인다(유량).
+   EC = 정산예정일이 어제인 보유 채권을 마감한 시점의 순현금이며 하루에 한 건 쌓인다(유량).
    기준일 잔액 1개(스톡)로 나누지 않는다.
    일별 EC 원장이 없어 EC 는 순현금 잔액으로 고정한다 — 실데이터 연결은 확인 대상. */
 /* EC 는 하루에 한 건 쌓이는 유량이라 조회 기간에 걸린 일수만큼 센다.
@@ -1976,7 +1973,7 @@ RENDER['invest-profit'] = function(){
           '<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span>' +
           '<span class="tip-row"><span>PY<sub>a</sub></span><span class="tip-green">투자실행금액 대비 연환산 수익률 · ' + fx(tyExec, 2) + '%</span></span>' +
           '<span class="tip-row"><span>Σ( A<sub>i</sub> × D<sub>i</sub> )</span><span class="tip-green">' + fmt(adOfRows(rows)) + '원</span></span>' +
-          '<span class="tip-row"><span>PEC</span><span class="tip-green">기간 순현금 · ' + fmt((cashRow() ? cashRow().amount : 0) * ecDays()) + '원</span></span>' +
+          '<span class="tip-row"><span>PEC</span><span class="tip-green">검색대상기간의 누적 순현금 · ' + fmt((cashRow() ? cashRow().amount : 0) * ecDays()) + '원</span></span>' +
           '<span class="tip-row sum"><span>EC</span><span>순현금 · ' + fmt(cashRow() ? cashRow().amount : 0) + '원 × ' + ecDays() + '일</span></span>' +
         '</span></span></div>' +
         '<div class="summary-value">' + fx(tyAsset, 2) + '<span class="unit">%</span></div></div>' +
@@ -2020,7 +2017,7 @@ JS += r'''
    기존 화면과 완전히 별개다. SIM 은 IA·PF·MC·AQ·CT 와 독립된 상태 객체이고
    simRun() 은 MERCHANTS·ASSET_ROWS·DAILY 를 읽지도 쓰지도 않는다.
    산식 출처 — 대표 정의서 [1번 이미지] A<sub>i</sub>·D<sub>i</sub>·w·ty·S · [2번 이미지] M<sub>d−1,&thinsp;i</sub>·B<sub>d−1,&thinsp;i</sub>·PSA·PSM·PSD·PSMR·PSC.
-   대문자 D 는 금융일수, 소문자 d 는 오늘 날짜다. d−1 은 어제 날짜가 아니라 정산예정일이 어제인 대상정산금채권 집합을 가리킨다.
+   대문자 D 는 금융일수, 소문자 d 는 오늘 날짜다. d−1 은 어제 날짜가 아니라 정산예정일이 어제인 보유 채권 집합을 가리킨다.
    앵커는 순지급액이다(채권매입수수료 = 순지급액 x 할인율 · D-31). 일별 원장 daily_ledger.py 도 같은 앵커라
    투자 수익 화면과 이 화면의 같은 열은 같은 산식에서 나온다. */
 var SIM_PLAT = [
@@ -2273,7 +2270,7 @@ function simTyTip(R){
         '<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span>' +
         '<span class="tip-row"><span>PY<sub>a</sub></span><span class="tip-green">투자실행금액 대비 연환산 수익률 · ' + fx(R.TY4, 2) + '%</span></span>' +
         '<span class="tip-row"><span>Σ( A<sub>i</sub> × D<sub>i</sub> )</span><span class="tip-green">' + fmt(R.AD) + '원</span></span>' +
-        '<span class="tip-row"><span>PEC</span><span class="tip-green">기간 순현금 · ' + fmt(R.PEC) + '원</span></span>' +
+        '<span class="tip-row"><span>PEC</span><span class="tip-green">검색대상기간의 누적 순현금 · ' + fmt(R.PEC) + '원</span></span>' +
         '<span class="tip-row sum"><span>EC</span><span>순현금 · ' + fmt(R.cash) + '원 × ' + R.ECD + '일</span></span>' +
       '</span></span></div>' +
       '<div class="summary-value' + (R.TY5 < 0 ? ' neg' : '') + '">' + fx(R.TY5, 2) + '<span class="unit">%</span></div></div>' +
diff --git a/payhug-spec/_pipeline/investor_admin/build_sim_static.py b/payhug-spec/_pipeline/investor_admin/build_sim_static.py
index 387f12f..a0d5dc3 100644
--- a/payhug-spec/_pipeline/investor_admin/build_sim_static.py
+++ b/payhug-spec/_pipeline/investor_admin/build_sim_static.py
@@ -120,17 +120,17 @@ def run():
 
 # ⑥ 열머리 — 통합본 build_app.py 의 tyTh() 와 같은 마크업이다.
 TY_TH = ('<th class="num"><span class="tooltip wide"><span class="tip-anchor">연환산 수익률</span>'
-         '<span class="tip-panel">(④ ÷ ③) × 365 ÷ ⑤'
-         '<span class="tip-row"><span>번호</span><span class="tip-green">'
-         '일별 표 열 ③투자실행금 ④투자 수익 ⑤가중평균 금융일수</span></span>'
+         '<span class="tip-panel">PY<sub>a</sub> · 연환산 수익률 · PMR × 365 ÷ PD'
+         '<span class="tip-row"><span>연환산</span><span class="tip-green">'
+         '일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span>'
          '<span class="tip-row"><span>행</span><span class="tip-green">'
          '정산예정일이 그 날짜인 보유 채권</span></span>'
          '</span></span></th>')
 # ③ 열머리 — 통합본 build_app.py 의 thirdTh() 와 같은 마크업이다.
 THIRD_TH = ('<th class="num"><span class="tooltip wide"><span class="tip-anchor">투자실행금</span>'
-            '<span class="tip-panel">⑥ 의 ③'
-            '<span class="tip-row"><span>번호</span><span class="tip-green">'
-            '상단 현황의 기간 전체 숫자 · 칸 미지목</span></span>'
+            '<span class="tip-panel">PA · 투자실행금 · Σ A<sub>i</sub>'
+            '<span class="tip-row"><span>행</span><span class="tip-green">'
+            '정산예정일이 그 날짜인 보유 채권</span></span>'
             '</span></span></th>')
 
 def field(fid, label, kind, value, extra=''):
@@ -275,7 +275,7 @@ def result_block(R):
            '<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span>'
            '<span class="tip-row"><span>PY<sub>a</sub></span><span class="tip-green">투자실행금액 대비 연환산 수익률 · %s%%</span></span>'
            '<span class="tip-row"><span>Σ( A<sub>i</sub> × D<sub>i</sub> )</span><span class="tip-green">%s원</span></span>'
-           '<span class="tip-row"><span>PEC</span><span class="tip-green">기간 순현금 · %s원</span></span>'
+           '<span class="tip-row"><span>PEC</span><span class="tip-green">검색대상기간의 누적 순현금 · %s원</span></span>'
            '<span class="tip-row sum"><span>EC</span><span>순현금 · %s원 × %d일</span></span>'
            '</span></span></div>\n'
            '              <div class="summary-value">%s<span class="unit">%%</span></div>\n            </div>\n'
diff --git a/payhug-spec/_pipeline/investor_admin/sync_assets_static.py b/payhug-spec/_pipeline/investor_admin/sync_assets_static.py
index 975c4b4..8c18ecb 100644
--- a/payhug-spec/_pipeline/investor_admin/sync_assets_static.py
+++ b/payhug-spec/_pipeline/investor_admin/sync_assets_static.py
@@ -178,7 +178,7 @@ def status_table(s):
 #   W금융일수·S입금부족율·옆 칸 금액이 각자 다른 집합에서 나온다. 행을 금액으로 가중평균해도
 #   현황표의 두 칸과 맞아떨어지지 않는 자리라, 열머리가 자기 모집단을 스스로 말한다.
 #   마크업은 통합본 build_app.py 의 popTh() 와 같다.
-POP = (('가중평균 금융일수', '보유 채권 전체 (회수된 것 포함)', POP_N_W),
+POP = (('가중평균 금융일수', '보유 채권 전체', POP_N_W),
        ('입금부족률', '선정산일이 오늘 기준 20일 전 ~ 11일 전인 표본', POP_N_S))
 
 
diff --git a/payhug-spec/_pipeline/investor_admin/sync_profit_static.py b/payhug-spec/_pipeline/investor_admin/sync_profit_static.py
index 035f630..9bac65b 100644
--- a/payhug-spec/_pipeline/investor_admin/sync_profit_static.py
+++ b/payhug-spec/_pipeline/investor_admin/sync_profit_static.py
@@ -168,24 +168,24 @@ TIP4 = ('<div class="ty-label"><span class="tooltip wide"><span class="tip-ancho
         '</span></span></div>')
 # ⑥ 열머리 — 통합본 build_app.py 의 tyTh() 와 같은 마크업이다.
 TY_TH = ('<th class="num"><span class="tooltip wide"><span class="tip-anchor">연환산 수익률</span>'
-         '<span class="tip-panel">(④ ÷ ③) × 365 ÷ ⑤'
-         '<span class="tip-row"><span>번호</span><span class="tip-green">'
-         '일별 표 열 ③투자실행금 ④투자 수익 ⑤가중평균 금융일수</span></span>'
+         '<span class="tip-panel">PY<sub>a</sub> · 연환산 수익률 · PMR × 365 ÷ PD'
+         '<span class="tip-row"><span>연환산</span><span class="tip-green">'
+         '일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span>'
          '<span class="tip-row"><span>행</span><span class="tip-green">'
          '정산예정일이 그 날짜인 보유 채권</span></span>'
          '</span></span></th>')
 # ③ 열머리 — 통합본 build_app.py 의 thirdTh() 와 같은 마크업이다.
 THIRD_TH = ('<th class="num"><span class="tooltip wide"><span class="tip-anchor">투자실행금</span>'
-            '<span class="tip-panel">⑥ 의 ③'
-            '<span class="tip-row"><span>번호</span><span class="tip-green">'
-            '상단 현황의 기간 전체 숫자 · 칸 미지목</span></span>'
+            '<span class="tip-panel">PA · 투자실행금 · Σ A<sub>i</sub>'
+            '<span class="tip-row"><span>행</span><span class="tip-green">'
+            '정산예정일이 그 날짜인 보유 채권</span></span>'
             '</span></span></th>')
 TIP5 = ('<div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자 자산 대비</span>'
         '<span class="tip-panel">PY<sub>t</sub> · 투자 자산 대비 연환산 수익률 · PM × 365 ÷ ( Σ( A<sub>i</sub> × D<sub>i</sub> ) + PEC )'
         '<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span>'
         '<span class="tip-row"><span>PY<sub>a</sub></span><span class="tip-green">투자실행금액 대비 연환산 수익률 · %(ty4)s%%</span></span>'
         '<span class="tip-row"><span>Σ( A<sub>i</sub> × D<sub>i</sub> )</span><span class="tip-green">%(ad)s원</span></span>'
-        '<span class="tip-row"><span>PEC</span><span class="tip-green">기간 순현금 · %(pec)s원</span></span>'
+        '<span class="tip-row"><span>PEC</span><span class="tip-green">검색대상기간의 누적 순현금 · %(pec)s원</span></span>'
         '<span class="tip-row sum"><span>EC</span><span>순현금 · %(ec)s원 × %(ecd)d일</span></span>'
         '</span></span></div>')
 
diff --git a/payhug-spec/_pipeline/investor_admin/verify_crossscreen.py b/payhug-spec/_pipeline/investor_admin/verify_crossscreen.py
index b308f4b..6251a20 100644
--- a/payhug-spec/_pipeline/investor_admin/verify_crossscreen.py
+++ b/payhug-spec/_pipeline/investor_admin/verify_crossscreen.py
@@ -347,7 +347,7 @@ POP_TIP = re.compile(r'<span class="tip-anchor">(가중평균 금융일수|입
                      r'<span class="tip-panel">([^<]+)'
                      r'<span class="tip-row"><span>채권 건수</span>'
                      r'<span class="tip-green">([\d,]+)건</span>')
-POP_WANT = [('가중평균 금융일수', '보유 채권 전체 (회수된 것 포함)', POP_W_N),
+POP_WANT = [('가중평균 금융일수', '보유 채권 전체', POP_W_N),
             ('입금부족률', '선정산일이 오늘 기준 20일 전 ~ 11일 전인 표본', POP_S_N)]
 # 기준일 d 는 확정이라 열머리 두 곳 어디에도 `미확정` 배지가 없다.
 PEND_TH = re.compile(r'<span class="tip-anchor">(가중평균 금융일수|입금부족률)</span>.*?'
@@ -363,7 +363,7 @@ for _p in ('invest-assets.html', 'invest-assets--download.html',
 _app = rd('app.html')
 chk('app.html 열머리 모집단 재료',
     re.findall(r"var (POP_[WS]) = \{of:'([^']+)',\s*n:'([\d,]+)건'(, pend:1)?\}", _app),
-    [('POP_W', '보유 채권 전체 (회수된 것 포함)', POP_W_N, ''),
+    [('POP_W', '보유 채권 전체', POP_W_N, ''),
      ('POP_S', '선정산일이 오늘 기준 20일 전 ~ 11일 전인 표본', POP_S_N, '')])
 chk('app.html 두 표가 같은 popTh 를 쓴다', _app.count("popTh('가중평균 금융일수', POP_W)"), 2)
 chk('app.html 두 표가 같은 popTh 를 쓴다 (S)', _app.count("popTh('입금부족률', POP_S)"), 2)
diff --git a/payhug-spec/_pipeline/investor_admin/verify_proto.js b/payhug-spec/_pipeline/investor_admin/verify_proto.js
index 9a135a2..7ab2815 100644
--- a/payhug-spec/_pipeline/investor_admin/verify_proto.js
+++ b/payhug-spec/_pipeline/investor_admin/verify_proto.js
@@ -829,7 +829,7 @@ async function main(){
        Σ( Ai × Di ) 행이 됐다. PA 행은 ④ 툴팁에 「기간 투자실행금」으로 남는다.
        <sub> 는 textContent 에서 글자로 붙는다 — Σ( A<sub>i</sub> × D<sub>i</sub> ) → 'Σ( Ai × Di )'. */
     add('기본 기간 PA (④ 툴팁)', 'PA기간 투자실행금 · ' + F.psa + '원', tip.filter(function(x){ return x.indexOf('PA')===0; })[0] || '없음');
-    add('기본 기간 PEC (⑤ 툴팁)', 'PEC기간 순현금 · ' + F.psc + '원', tip.filter(function(x){ return x.indexOf('PEC')===0; })[0] || '없음');
+    add('기본 기간 PEC (⑤ 툴팁)', 'PEC검색대상기간의 누적 순현금 · ' + F.psc + '원', tip.filter(function(x){ return x.indexOf('PEC')===0; })[0] || '없음');
     add('기본 기간 Σ( Ai × Di ) (⑤ 툴팁)', 'Σ( Ai × Di )' + F.ad + '원', tip.filter(function(x){ return x.indexOf('Σ( Ai × Di )')===0; })[0] || '없음');
     var ft = Array.prototype.map.call(SECQ('invest-profit','.tbl tfoot td'), function(td){ return td.textContent.replace('가중평균','').trim(); });
     add('일별 표 합계 W',  F.weekW,          ft[4] || '없음');
```

같은 디렉터리에서 `shot_rects.json` · `verify_sim_result.json` 도 바뀌었다 — `capture_shots.js` · `verify_sim.js` 가 쓰는 결과 파일이다.

## 3. 검사 결과

| 검사 | 결과 |
|---|---|
| `python3 build_app.py` | `app.html 237703 bytes / 3822 lines · screens in doc: 16` |
| `sync_assets_static.py` · `sync_profit_static.py` · `build_sim_static.py` | 낱장 갱신. sim `W 3.04 · Ty 13.21% · 비중합 100.0 · 상환액=PSA+PSM True` |
| `prep_fig.py sync` · `freeze` | 24화면 동기화 + 상태 프레임 낱장 13개 |
| `node capture_shots.js` | 5장 0.38MB / 5MB, 콘솔 에러 0, 실패 0 |
| `node verify_shots.js` | 판정 64건 FAIL 0 |
| `python3 build_readme.py` | 파일 76 · 루트 HTML 45 · 화면 14 · 상태 18 · 메뉴 8 (내용 동일) |
| `python3 sync_assets_static.py --check` | 어긋난 낱장 0 / 11 |
| `sync_profit_static.py --check` | 그런 옵션이 없다(파일에 `--check` 처리 없음). 대신 본 실행이 「카드 ↔ 표 기간 일치」 4건을 찍는다 |
| `python3 verify_crossscreen.py` | 전건 PASS (열머리 모집단 툴팁 4낱장×2 · app.html 재료 · 배지 없음) |
| `node verify_sim.js` | 92 / 92 ALL PASS — 낱장 ⑥ 열머리 = `tyTh()` 판정에 새 문구 `PYa · 연환산 수익률 · PMR × 365 ÷ PD연환산…행정산예정일이 그 날짜인 보유 채권` |
| `bash sync_prototype.sh --dry-run` | 게이트 통과, 바깥 통로 0건, push 안 함. ⑤ 툴팁 PEC 140,000,000 = 원장 weekPsc |
| `ledger_facts.json` md5 | 전 `1bffe2e62d2caf020b81c8b15a5c56bd` = 후 |
| `git -C /Users/semi/cursor/payhug-investor-admin diff --stat` | `app.html` · `invest-assets*.html` 4 · `invest-profit*.html` 4 · `invest-sim--result.html` = 10 파일뿐 |
| 옛 문구 0건 (「회수된 것 포함」「칸 미지목」「⑥ 의 ③」「(④ ÷ ③)」「기간 순현금」「대상정산금채권」) | `app.html` 0 · 낱장 9개 0 · dry-run 게이트(verify_proto) 통과 |

### 헤드리스 크롬 호버 — `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/step12_qa/`

스크립트 `hover_qa.js`(CDP · `Input.dispatchMouseEvent` 로 앵커 중앙에 마우스 이동 → `.tooltip:hover .tip-panel` 표시 → 패널 문구 읽기 → 앵커+패널 영역 캡처). 결과 `hover_qa_result.json`, 캡처 `<tag>.png`(툴팁 부분) · `<tag>--full.png`(뷰포트).

| tag | 페이지 | 앵커 | 표시 | 읽힌 문구(textContent) |
|---|---|---|---|---|
| assets-w-status | invest-assets.html | 가중평균 금융일수 (현황표) | hover=true visible | `보유 채권 전체 / 채권 건수 61,760건` |
| assets-w-merchant | invest-assets.html | 가중평균 금융일수 (가맹점별) | 〃 | 〃 |
| profit-th-exec | invest-profit.html | 투자실행금 | 〃 | `PA · 투자실행금 · Σ Ai / 행 정산예정일이 그 날짜인 보유 채권` |
| profit-th-yield | invest-profit.html | 연환산 수익률 | 〃 | `PYa · 연환산 수익률 · PMR × 365 ÷ PD / 연환산 일부 기간의 … 연간 수익률 / 행 정산예정일이 그 날짜인 보유 채권` |
| profit-py-asset | invest-profit.html | 투자 자산 대비 | 〃 | `… PEC 검색대상기간의 누적 순현금 · 140,000,000원 / EC 순현금 · 20,000,000원 × 7일` |
| app-assets-w-status / -merchant | app.html#invest-assets | 가중평균 금융일수 ×2 | 〃 | `보유 채권 전체 / 채권 건수 61,760건` |
| app-profit-th-exec | app.html#invest-profit | 투자실행금 | 〃 | 위와 같음 |
| app-profit-th-yield | app.html#invest-profit | 연환산 수익률 | 〃 | 위와 같음 |
| app-profit-py-asset | app.html#invest-profit | 투자 자산 대비 | 〃 | 위와 같음 |

10 / 10 PASS. 옛 문구·「번호」 행 0건.

## 4. 발견했으나 고치지 않은 것

| # | 어디 | 무엇 |
|---|---|---|
| 1 | `/Users/semi/cursor/payhug-investor-admin/assets/base.css:247` `.tbl th { text-transform: uppercase }` | 표 열머리 안에 있는 툴팁은 `<sub>` 도 대문자로 그려진다. 새 ③·⑥ 툴팁이 화면에 `PA · 투자실행금 · Σ A<sub>I</sub>` · `PY<sub>A</sub> · 연환산 …` 로 보인다(캡처 `profit-th-exec.png` · `profit-th-yield.png`). 기존 「예상 연환산 수익률」 열머리의 `Y<sub>r</sub>` 도 같은 규칙 아래 있다. 카드 안 ④⑤ 툴팁(div)은 `PY<sub>a</sub>` 소문자 그대로. CSS 는 지시 밖 |
| 2 | `/Users/semi/cursor/payhug-investor-admin/app.html` 엑셀 매니페스트 | §0-d. HEAD 의 `made:` 가 실제 xlsx mtime 과 어긋나 있었다 |
| 3 | `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/_fig/` 커밋본 | `apply` 단계까지 거친 상태로 커밋돼 있다. `sync`+`freeze` 만 돌리면 37파일 전부 capture.js·폰트 링크·input 치환이 빠진 형태가 된다 |
| 4 | 문서 페이지(지시상 불변) 안의 옛 낱말 | `steps-all.html` 대상정산금채권 126 · (④ ÷ ③) 14 · 기간 순현금 3 · 칸 미지목 2 · ⑥ 의 ③ 2 / `glossary.html` 대상정산금채권 93 / `terms-edit.html` 41 · 기간 순현금 2 · (④ ÷ ③) 1 / `final-terms.html` 34 · 기간 순현금 2 / `inquiry.html` 4 / `calc.html` 3 · 기간 순현금 1 / `feasibility.html` 1 / `capability.html` 기간 순현금 2 / `ceo-questions.html` (④ ÷ ③) 1 |
| 5 | `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_sim.js:76` 주석 | `대상정산금채권` — 검증기 안 주석, 화면에 안 실림 |
| 6 | `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/roster16_model.py:8·108` · `build_audit_xlsx.py` 여러 곳 · `verify_shortfall.py` · `restructure_glossary.py:40` | `대상정산금채권` — 원장 모델·감사 엑셀·용어집 생성기. 엑셀·문서는 지시상 불변 |
| 7 | `build_glossary.py` | 지시대로 돌리지 않음(기존 앵커 문제). `glossary.html` 은 HEAD 그대로 |

## 5. `_fig/*.html` 중 내용이 바뀐 파일 (Figma 교체 대상, 18개)

`/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/_fig/` 기준. 판정은 `git diff` 에서 `apply` 단계 되돌림(폰트 링크 · capture.js · input→span)을 뺀 나머지 줄이 있는지로 했다.

| 파일 | 바뀐 것 |
|---|---|
| `invest-assets.html` · `invest-assets--cert-confirm.html` · `invest-assets--download.html` · `invest-assets--empty.html` · `invest-assets--nav-collapsed.html` · `invest-assets--tip-exec.html` · `invest-assets--tip-shortfall.html` · `invest-assets--tip-yield.html` | W 열머리 툴팁 문구 (현황표 · 가맹점별, 패널 닫힘) |
| `invest-assets--tip-wavg.html` | W 열머리 툴팁 문구 — **패널 열린 상태(`id="fig-tip"`)** 라 캡처에 문구가 그대로 보인다 |
| `invest-profit.html` · `invest-profit--weekly.html` · `invest-profit--monthly.html` · `invest-profit--empty.html` · `invest-profit--tip-py-exec.html` | ③·⑥ 열머리 툴팁 + ⑤ PEC 행 (패널 닫힘) |
| `invest-profit--range-error.html` | ⑥ 열머리 툴팁 + ⑤ PEC 행 (표 없음·③ 없음) |
| `invest-profit--tip-exec.html` | ③ 열머리 툴팁 **열림** — 캡처에 `PA · 투자실행금 · Σ Ai / 행 …` 보임 |
| `invest-profit--tip-yield.html` | ⑥ 열머리 툴팁 **열림** — 캡처에 `PYa · 연환산 수익률 · PMR × 365 ÷ PD / 연환산 … / 행 …` 보임 |
| `invest-profit--tip-py-asset.html` | ⑤ 툴팁 **열림** — 캡처에 `PEC 검색대상기간의 누적 순현금 · 140,000,000원` 보임 |

`merchants--empty.html` · `merchants--filtered.html` 의 diff 1줄은 `apply` 단계의 검색어 input 치환 되돌림이고 내용 변화가 아니다. 나머지 17개(acquisition·contracts·certificate·merchants·password)는 `apply` 되돌림만 있다.
