# 툴팁 기호 · 정본 용어명 적용 보고

## 0. 하지 않은 것 · 지도와 다르게 한 것

| 구분 | 항목 | 내용 |
|---|---|---|
| 하지 않음 | `popTh` 2곳 (`build_app.py:1297-1304`) · `sync_assets_static.py` `pop_th` | 지시대로 손대지 않음 (T-01 · T-02 선택분) |
| 하지 않음 | T-03 `i` 행 (지도 §5-3 행 2 「정산예정일이 기준일보다 뒤인 대상정산금채권 · 2,240건」) | 지도에 「선택」이고 지시 요지 표에 없어 넣지 않음. 투자실행액 카드 툴팁은 머리글 + `r` 행만 바꿈 |
| 하지 않음 | 낱장 `invest-assets*.html` 4개의 카드 툴팁 T-03 · T-04 | 별건. 통합본 `app.html` 에만 있는 상태 그대로 |
| 하지 않음 | 검사기 실행 · `verify_proto.js:830-832` 기대값 수정 | 다음 조 몫. 새 문면은 §5 |
| 하지 않음 | `xls-profit-daily.html` · `xls-profit-status.html` | 열지 않음. 툴팁이 없는 파일이라 이번 범위와 겹치지 않음 (§3 · §4 의 diff 는 읽기만) |
| 하지 않음 | CSS · ⑤ 산식 글자 · 값 · 원장 · 원고 | 그대로. `.tip-panel` 은 `white-space: normal` (`assets/base.css:504`) 이라 긴 머리글은 256px 안에서 두 줄로 접힘 |
| 다르게 함 | `app.html` ④ `PMR` 값 | 지도 `fx(r6(profit / exec * 100), 6)` 에 0 나눗셈 보호를 붙여 `fx(exec ? r6(profit / exec * 100) : 0, 6)`. 조회 결과 0행일 때 `NaN%` 대신 `0.000000%` |
| 다르게 함 | `app.html` T-04 `D` 행의 빈 화면 | `wv === null` 이면 `가중평균 금융일수 · 집계 대상 없음`. 같은 카드 부제의 기존 문구(`build_app.py:1768`) 재사용. 지도는 값 있는 경우(`3.04일`)만 적음 |
| 다르게 함 | `app.html` 시뮬 ⑤ `EC` 행의 순현금 | 지도는 `SIM.cash`, 적용은 `R.cash`. `SIM.result` 에 `cash:SIM.cash` 로 들어 있어 같은 값 (`app.html:2675`) |
| 갈림 (지도대로) | 빈 조회 상태의 0 표기 | 낱장 `--empty` 는 지도 §5-1 §5-2 대로 `0%` · `0원` · `0일`. 통합본 `app.html` 은 지도 「실행 시」 열의 `fx(...)` 그대로라 같은 상태에서 `0.000000%` · `0원` · `0.00일` · `0.00%`. 낱장과 통합본이 이 한 상태에서 자릿수가 다름 |

## 1. (가) 고친 자리

행 표기는 `기호 → 오른쪽 칸` 이고, 행 사이는 ` / ` 입니다. 「대표 DM …」 · 「항등식」 · 「부족액 0」 · 「미확정 · 대표 재전달 대기」 행과 배지는 옛·새 모두 같아 표에서 뺐습니다.

### 1-1. 원천 (3파일 13곳)

| 파일:줄 (새) | 옛 | 새 |
|---|---|---|
| `build_app.py:1747-1748` T-03 투자실행액 카드 | 머리글 `순지급액 × (1 − 할인율)` / `할인율 → ' + fx(RATE_PCT, 2) + '%` | 머리글 `Σ A<sub>i</sub> · 투자 실행액 · A<sub>i</sub> = 순지급액<sub>i</sub> × (1 − r) 의 합` / `r → 계약된 할인율 · ' + fx(RATE_PCT, 2) + '%` |
| `build_app.py:1759-1762` T-04 예상 연환산수익률 카드 | 머리글 `할인율 × 365 ÷ 가중평균 금융일수` / `연 환산 → ' + fx(tyv, 2) + '%` | 머리글 `Y<sub>r</sub> · 예상 연환산수익률 · r × 365 ÷ D` / `r → 계약된 할인율 · ' + fx(RATE_PCT, 2) + '%` / `D → 가중평균 금융일수 · ' + (wv === null ? '집계 대상 없음' : fx(wv, 2) + '일') + '` / `연 환산 → ' + fx(tyv, 2) + '%` (그대로) |
| `build_app.py:1973-1977` T-05 ④ `pfRender` | 머리글 `PMR × 365 ÷ PD` / `PMR → 투자수익 ÷ 투자실행금` / `PD → 기간 가중평균 금융일수` | 머리글 `PY<sub>a</sub> · 투자실행금액 대비 연환산수익률 (관찰된 값) · PMR × 365 ÷ PD` / `PMR → 기간 투자수익율 · PM ÷ PA = ' + fx(exec ? r6(profit / exec * 100) : 0, 6) + '%` / `PM → 기간 투자수익 · ' + fmt(profit) + '원` / `PA → 기간 투자실행금 · ' + fmt(exec) + '원` / `PD → 기간 가중평균 금융일수 · ' + fx(wAvg, 2) + '일` |
| `build_app.py:1984-1988` T-06 ⑤ `pfRender` | 머리글 `( PY<sub>a</sub> × PA ) ÷ ( PA + PEC )` / `PA → ' + fmt(exec) + '원` / `PEC → ' + fmt((cashRow() ? cashRow().amount : 0) * ecDays()) + '원` / (합) `EC ' + ecDays() + '일 합 → 기간 순현금 합계` | 머리글 `PY<sub>t</sub> · 투자자산 대비 연환산수익률 (관찰된 값) · ( PY<sub>a</sub> × PA ) ÷ ( PA + PEC )` / `PY<sub>a</sub> → 투자실행금액 대비 연환산수익률 (관찰된 값) · ' + fx(tyExec, 2) + '%` / `PA → 기간 투자실행금 · ' + fmt(exec) + '원` / `PEC → 기간 순현금 · ' + fmt((cashRow() ? cashRow().amount : 0) * ecDays()) + '원` / (합) `EC → 순현금 · ' + fmt(cashRow() ? cashRow().amount : 0) + '원 × ' + ecDays() + '일` |
| `build_app.py:2271-2275` T-09 ④ `simTyTip` | T-05 와 같은 옛 문면 | 머리글 같음 / `PMR → 기간 투자수익율 · PM ÷ PA = ' + fx(R.PMR, 6) + '%` / `PM → 기간 투자수익 · ' + fmt(R.PM) + '원` / `PA → 기간 투자실행금 · ' + fmt(R.PA) + '원` / `PD → 기간 가중평균 금융일수 · ' + fx(R.PwD, 2) + '일` |
| `build_app.py:2282-2286` T-10 ⑤ `simTyTip` | T-06 와 같은 꼴 (`R.PA` · `R.PEC` · `R.ECD`) | 머리글 같음 / `PY<sub>a</sub> → 투자실행금액 대비 연환산수익률 (관찰된 값) · ' + fx(R.TY4, 2) + '%` / `PA → 기간 투자실행금 · ' + fmt(R.PA) + '원` / `PEC → 기간 순현금 · ' + fmt(R.PEC) + '원` / (합) `EC → 순현금 · ' + fmt(R.cash) + '원 × ' + R.ECD + '일` |
| `sync_profit_static.py:163-175` `TIP4` | 고정 문자열, `% (_R, _R / (1 − _R / 100.0))` 로 부족액 값만 채움 | `%(pmr)s` · `%(pm)s` · `%(pa)s` · `%(pd)s` · `%(r)s` · `%(pmr0)s` 자리의 사전 서식. 머리글·행은 T-05 새 문면. `TIP4_FIX = dict(r='%.2f' % _R, pmr0='%.6f' % (_R / (1 − _R / 100.0)))` |
| `sync_profit_static.py:195-202` `TIP5` | `%s원` · `%s원` · `EC %d일 합 → 기간 순현금 합계` | `%(ty4)s` · `%(pa)s` · `%(pec)s` · `%(ec)s` · `%(ecd)d` 자리의 사전 서식. 머리글·행은 T-06 새 문면 |
| `sync_profit_static.py:226-229` `put_tips` | `put_tips(s, psa, ec_days)` | `put_tips(s, psa, psm, ty4, pd, ec_days)` · `pmr = RM.r6(D(psm) / D(psa) * D(100)) if psa else 0` |
| `sync_profit_static.py:344-347` `one()` | `put_tips(s, VIEW[gran][4], ec_days(frm, to))` · 빈 낱장 `put_tips(s, 0, ec_days(frm, to))` | `v = VIEW[gran]; put_tips(s, v[4], v[5], v[6], v[3][3], ec_days(frm, to))` · 빈 낱장 `put_tips(s, 0, 0, 0, 0, ec_days(frm, to))`. `v[3][3]` 은 표 합계 행의 가중평균 금융일수 문자열 |
| `build_sim_static.py:276-280` T-09 ④ | 머리글 `PMR × 365 ÷ PD` / `PMR → 투자수익 ÷ 투자실행금` / `PD → 기간 가중평균 금융일수` | 머리글 T-05 새 문면 / `PMR → 기간 투자수익율 · PM ÷ PA = %s%%` / `PM → 기간 투자수익 · %s원` / `PA → 기간 투자실행금 · %s원` / `PD → 기간 가중평균 금융일수 · %s일` |
| `build_sim_static.py:285-289` T-10 ⑤ | 머리글 `( PY<sub>a</sub> × PA ) ÷ ( PA + PEC )` / `PA → %s원` / `PEC → %s원` / `EC %d일 합 → 기간 순현금 합계` | 머리글 T-06 새 문면 / `PY<sub>a</sub> → 투자실행금액 대비 연환산수익률 (관찰된 값) · %s%%` / `PA → 기간 투자실행금 · %s원` / `PEC → 기간 순현금 · %s원` / `EC → 순현금 · %s원 × %d일` |
| `build_sim_static.py:294-295` 서식 값 | `(fx(R['TY4'], 2), fmt(R['PSA']), fmt(R['PSC']), R['ECD'], fx(R['TY5'], 2))` | `(fx(R['PSMR'], 6), fmt(R['PSM']), fmt(R['PSA']), fx(R['PSD'], 2), fx(R['TY4'], 2), fx(R['TY4'], 2), fmt(R['PSA']), fmt(R['PSC']), fmt(CASH), R['ECD'], fx(R['TY5'], 2))` |

### 1-2. 낱장 (5파일 10툴팁)

옛 줄 번호는 지도 (가) 표와 같고, 새 줄 번호도 같습니다(툴팁이 한 줄 안에서 길어졌을 뿐 줄 수는 그대로).

| 파일:줄 | 옛 | 새 |
|---|---|---|
| `invest-profit.html:170` ④ | 머리글 `PMR × 365 ÷ PD` / `PMR → 투자수익 ÷ 투자실행금` / `PD → 기간 가중평균 금융일수` | 머리글 `PY_a · 투자실행금액 대비 연환산수익률 (관찰된 값) · PMR × 365 ÷ PD` / `PMR → 기간 투자수익율 · PM ÷ PA = 0.035003%` / `PM → 기간 투자수익 · 62,977원` / `PA → 기간 투자실행금 · 179,916,643원` / `PD → 기간 가중평균 금융일수 · 3.09일` |
| `invest-profit.html:174` ⑤ | 머리글 `( PY_a × PA ) ÷ ( PA + PEC )` / `PA → 179,916,643원` / `PEC → 140,000,000원` / `EC 7일 합 → 기간 순현금 합계` | 머리글 `PY_t · 투자자산 대비 연환산수익률 (관찰된 값) · ( PY_a × PA ) ÷ ( PA + PEC )` / `PY_a → 투자실행금액 대비 연환산수익률 (관찰된 값) · 4.13%` / `PA → 기간 투자실행금 · 179,916,643원` / `PEC → 기간 순현금 · 140,000,000원` / `EC → 순현금 · 20,000,000원 × 7일` |
| `invest-profit--weekly.html:176` ④ | 위와 같은 옛 문면 | `PMR → … = 0.038549%` / `PM → … 239,920원` / `PA → … 622,381,520원` / `PD → … 3.03일` |
| `invest-profit--weekly.html:180` ⑤ | `PA → 622,381,520원` / `PEC → 480,000,000원` / `EC 24일 합 → 기간 순현금 합계` | `PY_a → … 4.65%` / `PA → … 622,381,520원` / `PEC → … 480,000,000원` / `EC → 순현금 · 20,000,000원 × 24일` |
| `invest-profit--monthly.html:176` ④ | 위와 같은 옛 문면 | `PMR → … = 0.038054%` / `PM → … 1,778,656원` / `PA → … 4,673,981,320원` / `PD → … 3.03일` |
| `invest-profit--monthly.html:180` ⑤ | `PA → 4,673,981,320원` / `PEC → 3,580,000,000원` / `EC 179일 합 → …` | `PY_a → … 4.58%` / `PA → … 4,673,981,320원` / `PEC → … 3,580,000,000원` / `EC → 순현금 · 20,000,000원 × 179일` |
| `invest-profit--empty.html:176` ④ | 위와 같은 옛 문면 | `PMR → … = 0%` / `PM → … 0원` / `PA → … 0원` / `PD → … 0일` |
| `invest-profit--empty.html:180` ⑤ | `PA → 0원` / `PEC → 0원` / `EC 0일 합 → …` | `PY_a → … 0%` / `PA → … 0원` / `PEC → … 0원` / `EC → 순현금 · 20,000,000원 × 0일` |
| `invest-sim--result.html:372` ④ | 위와 같은 옛 문면 | `PMR → … = 0.040044%` / `PM → … 15,040원` / `PA → … 37,558,640원` / `PD → … 2.85일` |
| `invest-sim--result.html:376` ⑤ | `PA → 37,558,640원` / `PEC → 140,000,000원` / `EC 7일 합 → …` | `PY_a → … 5.13%` / `PA → … 37,558,640원` / `PEC → … 140,000,000원` / `EC → 순현금 · 20,000,000원 × 7일` |

손편집한 낱장 5개와 생성기가 다시 쓴 낱장 5개는 바이트 단위로 같습니다(§2 뒤 `diff -q` 5건 모두 동일).

## 2. (나) 재생성 결과

| 순서 | 스크립트 | 종료코드 | 마지막 줄 |
|---|---|---|---|
| 1 | `python3 build_app.py` | 0 | `screens in doc: 16` (앞줄 `app.html 239226 bytes / 3924 lines`) |
| 2 | `python3 sync_profit_static.py` | 0 | `invest-profit--weekly.html 행 4 · 카드 4주 2026-08-03 ~ 2026-08-26 · 합계 622,381,520` (카드 ↔ 표 기간 일치 4건 통과) |
| 3 | `python3 build_sim_static.py` | 0 | `W 3.13 · Ty 12.84% · 비중합 100.0 · 상환액=PSA+PSM True` |
| 4 | `python3 prep_fig.py sync` | 0 | `패치 sheet.css text-overflow:ellipsis 2곳 제거` (앞줄 `동기화 33화면 · 원본 HEAD 1693bd3 (워킹트리 변경분 포함)`) |

AssertionError 0건. `sync_profit_static.py` 의 `TY_LABEL` 치환은 `<div class="ty-label">.*?</div>` 를 잡아 머리글 문자열에 기대지 않으므로 정규식 수정이 필요 없었습니다.

`_fig/` 동기화 결과: `invest-profit.html` · `--weekly` · `--monthly` · `--empty` · `invest-sim--result.html` 각각 `PY<sub>t</sub> · 투자자산 대비` 머리글 1건. `app.html` 은 `prep_fig.py` 의 IMPORT 목록에 없어 `_fig/` 에 없습니다.

## 3. (다) 툴팁 기호별 용어명 유무 — 산출 16파일

`tip-panel` 을 span 깊이로 잘라 텍스트를 뽑은 결과입니다. `O` = 기호 옆에 정본 용어명 있음 · `-` = 그 툴팁에 그 기호 없음. `X`(기호는 있는데 용어명 없음)는 0건입니다.

| 파일 | 툴팁 | PMR | PY_a | PA | PEC | EC | PY_t | PD | PM |
|---|---|---|---|---|---|---|---|---|---|
| `app.html` | 투자실행액 카드 (T-03) | - | - | - | - | - | - | - | - |
| `app.html` | 예상 연환산수익률 카드 (T-04) | - | - | - | - | - | - | - | - |
| `app.html` | ④ 투자실행금액 대비 (T-05) | O | O | O | - | - | - | O | O |
| `app.html` | ⑤ 투자자산 대비 (T-06) | - | O | O | O | O | O | - | - |
| `app.html` | 시뮬 ④ (T-09) | O | O | O | - | - | - | O | O |
| `app.html` | 시뮬 ⑤ (T-10) | - | O | O | O | O | O | - | - |
| `invest-profit.html` | ④ | O | O | O | - | - | - | O | O |
| `invest-profit.html` | ⑤ | - | O | O | O | O | O | - | - |
| `invest-profit--weekly.html` | ④ | O | O | O | - | - | - | O | O |
| `invest-profit--weekly.html` | ⑤ | - | O | O | O | O | O | - | - |
| `invest-profit--monthly.html` | ④ | O | O | O | - | - | - | O | O |
| `invest-profit--monthly.html` | ⑤ | - | O | O | O | O | O | - | - |
| `invest-profit--empty.html` | ④ | O | O | O | - | - | - | O | O |
| `invest-profit--empty.html` | ⑤ | - | O | O | O | O | O | - | - |
| `invest-sim--result.html` | ④ | O | O | O | - | - | - | O | O |
| `invest-sim--result.html` | ⑤ | - | O | O | O | O | O | - | - |
| `invest-sim.html` | 툴팁 없음 | | | | | | | | |
| `invest-assets.html` · `--download` · `--cert-confirm` · `--empty` | 열머리 T-01 · T-02 만 (기호 없음, 그대로) | | | | | | | | |
| `certificate.html` | 툴팁 없음 | | | | | | | | |
| `xls-assets-merchant.html` · `xls-assets-status.html` · `xls-profit-daily.html` · `xls-profit-status.html` | 툴팁 없음 | | | | | | | | |

T-03 · T-04 의 기호 `Σ A_i` · `A_i` · `r` · `Y_r` · `D` 는 위 다섯 기호 밖이라 표 열에 없고, 머리글 `Σ A_i · 투자 실행액` · `Y_r · 예상 연환산수익률`, 행 `r → 계약된 할인율` · `D → 가중평균 금융일수` 로 용어명이 붙어 있습니다.

옛 문자열 잔존 검사: `투자수익 ÷ 투자실행금` · `일 합</span>` · `기간 순현금 합계` · `순지급액 × (1 − 할인율)` · `할인율 × 365 ÷ 가중평균 금융일수` — 산출 16파일 · `_fig/` 6파일 · 생성기 3파일 모두 **0건**.

## 4. (라) 툴팁 밖 라벨·숫자 diff

작업 전 사본(`scratchpad/step6/before/`)과 산출본에서 `tip-panel` 블록을 통째로 뺀 뒤 줄 단위로 비교한 결과입니다.

| 파일 | 바뀐 줄 | 내용 |
|---|---|---|
| `invest-profit.html` · `--weekly` · `--monthly` · `--empty` | 0 | |
| `invest-sim.html` · `invest-sim--result.html` | 0 | |
| `invest-assets.html` · `--download` · `--cert-confirm` · `--empty` | 0 | |
| `certificate.html` | 0 | |
| `xls-assets-merchant.html` · `xls-assets-status.html` · `xls-profit-daily.html` · `xls-profit-status.html` | 0 | |
| `app.html` | 28 (14쌍) | 전부 엑셀 목록의 `made:` 값. `2026-09-03 20:02` → `2026-09-04 18:10`. `build_app.py` 가 `@@MT:파일명@@` 자리에 `assets/xlsx/*.xlsx` 의 수정 시각을 읽어 넣는데, 그 파일들이 오늘 18:10 에 다시 만들어져 있어 재생성 때 따라 바뀐 값입니다. 화면 라벨 · 카드 값 · 표 숫자는 0건 |

## 5. (마) `verify_proto.js:830-832` 가 볼 새 문면

검사기는 `.ty-split .tip-row` 의 `textContent.trim()` 을 모아 `indexOf('PA')===0` · `indexOf('PEC')===0` 인 첫 항목을 `'PA' + F.psa + '원'` · `'PEC' + F.psc + '원'` 과 등호 비교합니다. 두 칸이 붙어 나오므로 새 텍스트는 아래와 같습니다.

| 검사 항목 | 옛 기대값 | 새 문면 (기본 기간 2026-08-20 ~ 08-26) | 비고 |
|---|---|---|---|
| 기본 기간 PA | `PA179,916,643원` | `PA기간 투자실행금 · 179,916,643원` | ④ 에도 `PA` 행이 생겨 DOM 순서상 ④ 것이 먼저 잡히지만 ⑤ 것과 글자가 같음 |
| 기본 기간 PEC | `PEC140,000,000원` | `PEC기간 순현금 · 140,000,000원` | ⑤ 에만 있음 |
| (참고) `EC` 행 | `EC 7일 합기간 순현금 합계` | `EC순현금 · 20,000,000원 × 7일` | 검사 대상 아님 |
| (참고) `PMR` 행 | `PMR투자수익 ÷ 투자실행금` | `PMR기간 투자수익율 · PM ÷ PA = 0.035003%` | `indexOf('PA')` 검사에 걸리지 않음 |
| (참고) `PY_a` 행 | 없음 | `PYa투자실행금액 대비 연환산수익률 (관찰된 값) · 4.13%` | `<sub>` 가 textContent 에서 `a` 로 붙음 |

기대값을 `'PA기간 투자실행금 · ' + F.psa + '원'` · `'PEC기간 순현금 · ' + F.psc + '원'` 으로 맞추면 통과합니다.

## 6. 파일 목록

| 구분 | 경로 |
|---|---|
| 원천 | `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/build_app.py` |
| 원천 | `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/sync_profit_static.py` |
| 원천 | `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/build_sim_static.py` |
| 산출 | `/Users/semi/cursor/payhug-investor-admin/app.html` |
| 산출 | `/Users/semi/cursor/payhug-investor-admin/invest-profit.html` |
| 산출 | `/Users/semi/cursor/payhug-investor-admin/invest-profit--weekly.html` |
| 산출 | `/Users/semi/cursor/payhug-investor-admin/invest-profit--monthly.html` |
| 산출 | `/Users/semi/cursor/payhug-investor-admin/invest-profit--empty.html` |
| 산출 | `/Users/semi/cursor/payhug-investor-admin/invest-sim--result.html` |
| 산출 (재생성으로 다시 쓰임, 내용 같음) | `/Users/semi/cursor/payhug-investor-admin/invest-sim.html` |
| 동기화 | `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/_fig/` 33화면 |
| 작업 사본 · 검사 스크립트 | `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/step6/` (`before/` 16파일 · `hand/` 5파일 · `edit_static.py` · `edit_gen.py` · `check.py` · `log_*.txt`) |
