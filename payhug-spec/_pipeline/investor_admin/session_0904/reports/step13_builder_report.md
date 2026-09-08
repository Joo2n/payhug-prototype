# step13 — 투자자 어드민 툴팁 재작성 보고

출력 레포 `/Users/semi/cursor/payhug-investor-admin` HEAD `0b6ab0d` (커밋·push 없음) · 생성기 `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin` · 기준 `session_0904/artifact/투자자어드민 기호정리표_V1.3.html` 표 2 산식 칸

`ledger_facts.json` md5 전후 동일 `1bffe2e62d2caf020b81c8b15a5c56bd`

## 1. 툴팁 최종 innerText (헤드리스 크롬 호버 실측)

### A — `app.html#invest-assets` · 앵커 「투자실행액」 #0
```
Σ Ai
Ai
순지급액i × (1 − r)
r
0.11%
```
### B 카드 — `app.html#invest-assets` · 앵커 「예상 연환산 수익률」 #0
```
Yr = r × 365 ÷ D
r
0.11%
D
3.04일
연환산
일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률
```
### B 현황표 열머리 — `app.html#invest-assets` · 앵커 「예상 연환산 수익률」 #1
```
Yr = r × 365 ÷ D
r
0.11%
D
3.04일
연환산
일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률
```
### B 가맹점별 열머리 — `app.html#invest-assets` · 앵커 「예상 연환산 수익률」 #2
```
Yr = r × 365 ÷ D
r
0.11%
D
3.04일
연환산
일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률
```
### C — `app.html#invest-assets` · 앵커 「가중평균 금융일수」 #0
```
D = Σ( Ai × Di ) ÷ Σ Ai
i
보유 채권 전체 · 61,760건
```
### D — `app.html#invest-assets` · 앵커 「입금부족률」 #0
```
LR = Σ Li ÷ Σ Ai
i
선정산일이 오늘 기준 20일 전 ~ 11일 전 · 3,200건
```
### E — `app.html#invest-profit` · 앵커 「투자실행금액 대비」 #0
```
PYa = PMR × 365 ÷ PD
PMR
0.033992%
PM
61,175원
PA
179,970,919원
PD
3.11일
연환산
일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률
```
### F — `app.html#invest-profit` · 앵커 「투자 자산 대비」 #0
```
PYt = PYa × 채권 비중 + 순현금 수익률 × 순현금 비중
= PM × 365 ÷ ( Σ( Ai × Di ) + PEC )
PYa
3.99%
Σ( Ai × Di )
559,275,516원
PEC
140,000,000원
EC
20,000,000원 × 7일
연환산
일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률
```
### G — `app.html#invest-profit` · 앵커 「투자실행금」 #0
```
PA = Σ Ai
i
정산예정일이 그 날짜인 보유 채권
```
### H — `app.html#invest-profit` · 앵커 「연환산 수익률」 #0
```
PYa = PMR × 365 ÷ PD
i
정산예정일이 그 날짜인 보유 채권
연환산
일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률
```
### B 카드 · 빈 상태 — `invest-assets--empty.html` · 앵커 「예상 연환산 수익률」 #0
```
Yr = r × 365 ÷ D
r
0.11%
D
집계 대상 없음
연환산
일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률
```
### E · 빈 상태 — `invest-profit--empty.html` · 앵커 「투자실행금액 대비」 #0
```
PYa = PMR × 365 ÷ PD
PMR
0.000000%
PM
0원
PA
0원
PD
0.00일
연환산
일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률
```
### F · 빈 상태 — `invest-profit--empty.html` · 앵커 「투자 자산 대비」 #0
```
PYt = PYa × 채권 비중 + 순현금 수익률 × 순현금 비중
= PM × 365 ÷ ( Σ( Ai × Di ) + PEC )
PYa
0.00%
Σ( Ai × Di )
0원
PEC
0원
EC
20,000,000원 × 0일
연환산
일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률
```
### F · 주별 — `invest-profit--weekly.html` · 앵커 「투자 자산 대비」 #0
```
PYt = PYa × 채권 비중 + 순현금 수익률 × 순현금 비중
= PM × 365 ÷ ( Σ( Ai × Di ) + PEC )
PYa
4.62%
Σ( Ai × Di )
1,965,572,846원
PEC
500,000,000원
EC
20,000,000원 × 25일
연환산
일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률
```
### F · 월별 — `invest-profit--monthly.html` · 앵커 「투자 자산 대비」 #0
```
PYt = PYa × 채권 비중 + 순현금 수익률 × 순현금 비중
= PM × 365 ÷ ( Σ( Ai × Di ) + PEC )
PYa
4.57%
Σ( Ai × Di )
14,262,370,838원
PEC
3,600,000,000원
EC
20,000,000원 × 180일
연환산
일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률
```
### F · 시뮬레이션 결과 — `invest-sim--result.html` · 앵커 「투자 자산 대비」 #0
```
PYt = PYa × 채권 비중 + 순현금 수익률 × 순현금 비중
= PM × 365 ÷ ( Σ( Ai × Di ) + PEC )
PYa
4.81%
Σ( Ai × Di )
121,466,240원
PEC
140,000,000원
EC
20,000,000원 × 7일
연환산
일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률
```

낱장 `invest-assets*.html` 에는 「투자실행액」 카드 툴팁(A)이 원래 없고(앵커 0건), 지시대로 두지 않았다. 나머지 8종은 낱장·통합본 글자가 같다(hover_qa_result.json).

## 2. 바꾼 자리 (파일:줄 — 고친 뒤 기준)

| 자리 | 내용 |
|---|---|
| `build_app.py:1294` | 열머리 재료 POP_W · POP_S(C · D 첫 줄·조건 문장) |
| `build_app.py:1296` | popTh() — 첫 줄 p.head · 행 i → 조건 문장 · 건수 |
| `build_app.py:1302` | YR_TIP_HEAD (B 첫 줄) |
| `build_app.py:1304` | yrRows(w) — r · D · 연환산 행 (B) |
| `build_app.py:1309` | yrTh(w) 열머리 (B) |
| `build_app.py:1324` | tyTh() ⑥ 열머리 (H) |
| `build_app.py:1332` | thirdTh() ③ 열머리 (G) |
| `build_app.py:1745` | 투자 자산 카드 「투자실행액」 (A) |
| `build_app.py:1756` | 투자 자산 카드 「예상 연환산 수익률」 (B) |
| `build_app.py:1762` | 현황표 열머리 yrTh(wv) |
| `build_app.py:1791` | 가맹점별 열머리 yrTh(wv) |
| `build_app.py:1966` | pfRender ④ (E) |
| `build_app.py:1975` | pfRender ⑤ (F) |
| `build_app.py:2263` | simTyTip ④ (E · 시뮬레이션 결과) |
| `build_app.py:2272` | simTyTip ⑤ (F · 시뮬레이션 결과) |
| `sync_assets_static.py:181` | POP (C · D) |
| `sync_assets_static.py:185` | pop_th() |
| `sync_assets_static.py:210` | YR_HEAD (B) |
| `sync_assets_static.py:219` | yr_rows(w) |
| `sync_assets_static.py:225` | yr_card_tip(w) |
| `sync_assets_static.py:235` | yr_card(s, w) |
| `sync_assets_static.py:242` | yr_th(w) |
| `sync_assets_static.py:247` | yr_heads(s, w) |
| `sync_assets_static.py:444` | build_assets 호출 |
| `sync_assets_static.py:476` | build_assets_empty 호출 |
| `sync_profit_static.py:161` | YR_ROW |
| `sync_profit_static.py:163` | TIP4 (E) |
| `sync_profit_static.py:172` | TY_TH (H) |
| `sync_profit_static.py:180` | THIRD_TH (G) |
| `sync_profit_static.py:185` | TIP5 (F) |
| `sync_profit_static.py:230` | put_tips — 빈 상태 PMR 0.000000 |
| `sync_profit_static.py:351` | one() — 빈 상태 ④ 0.00 · PD 0.00 |
| `build_sim_static.py:122` | TY_TH (H) |
| `build_sim_static.py:130` | THIRD_TH (G) |
| `build_sim_static.py:265` | ④ (E) |
| `build_sim_static.py:274` | ⑤ (F) |

## 3. 검증기 변경

| 자리 | 내용 |
|---|---|
| `verify_crossscreen.py:130` | CARD_TY — ⑤ 카드 값을 앵커 `투자 자산 대비` 로 잡는다. 옛 규칙은 ⑤ 툴팁 행의 「투자실행금액 대비 연환산 수익률 · 3.99%」 글자에 걸려 2건이 나오던 것 |
| `verify_crossscreen.py:346` | POP_TIP · POP_WANT — 첫 줄(산식, `<sub>` 포함) · 행 `i` · 「조건 문장 · N건」 4-튜플로 대조. 옛 규칙은 「보유 채권 전체」 첫 줄 + 「채권 건수」 행 |
| `verify_crossscreen.py:364` | app.html 열머리 모집단 재료 — `{head, of, n}` 3필드 대조 |
| `verify_proto.js:831` | 기본 기간 PA (④ 툴팁) 기대값 `PA` + 값 (옛: `PA기간 투자실행금 · ` + 값) |
| `verify_proto.js:832` | 기본 기간 PEC (⑤ 툴팁) 기대값 `PEC` + 값 (옛: `PEC검색대상기간의 누적 순현금 · ` + 값) |
| `verify_app.js:888` | 기본 기간 PA (④ 툴팁) 기대값 `PA` + 값 (옛: `PA기간 투자실행금 · ` + 값) |
| `verify_app.js:889` | 기본 기간 PEC (⑤ 툴팁) 기대값 `PEC` + 값 (옛: `PEC기간 순현금 · ` + 값 — 옛 라벨 중에서도 한 단계 더 낡은 문구) |
| `gate_prototype.js:464-471` | 변경 없음 — ⑤ 되짚기는 `.tip-row` 왼쪽 칸 글자(`PEC` · `Σ…`)를 키로 오른쪽 칸 숫자를 읽는다. 왼쪽 칸이 기호뿐인 새 구조에서 그대로 맞는다(dry-run 게이트 통과) |
| `verify_sim.js:632·646·893` | 변경 없음 — ⑥ 열머리 기대 글자 `SF.tyThText` 는 `sim_facts.py:195` 가 `build_app.py` 의 `tyTh()` 리터럴을 그 자리에서 이어 붙여 만든다 |

판정 완화 없음. verify_crossscreen.py 는 옛 규칙이 ⑤ 툴팁 행 글자에 우연히 걸려 2건을 얻던 자리를 앵커 기준으로 바꿔 더 좁게 본다.

## 4. 검사 결과

| 검사 | 결과 |
|---|---|
| `python3 sync_assets_static.py --check` | 어긋난 낱장 0 / 11 |
| `python3 verify_crossscreen.py` | 60 PASS · FAIL 3 — 셋 다 `glossary.html` 용어 해설 duration 허용 블록 검사로, HEAD `0b6ab0d` 를 stash 로 되돌려도 같은 3건이 FAIL (이번 변경과 무관, 7절) |
| `node verify_sim.js` | 92 / 92 ALL PASS (⑥ 열머리 = tyTh() 글자 대조 포함) |
| `node verify_app.js` | 판정 123건 · PASS 123 · FAIL 0 · 콘솔 에러 0 · 죽은 컨트롤 0 |
| `bash sync_prototype.sh --dry-run` | 변환 + `gate_prototype.js` 통과 — 「⑤ = ④ x Σ(Ai×Di)/(Σ(Ai×Di)+PEC) 툴팁 표기값 되짚기」 · 「툴팁 Σ(Ai×Di) · PEC = 원장 weekAD · weekPsc」 PASS, push 안 함 |
| `node verify_proto.js` | 판정 118건 · PASS 118 · FAIL 0 |
| `node capture_shots.js` · `node verify_shots.js` | 5/5 · 콘솔 에러 0 · 판정 64건 FAIL 0. webp 5장은 바이트 동일(툴팁은 호버 전용이라 그림에 실리지 않음) → `assets/shots/*.webp` 는 diff 에 없음 |
| `python3 build_readme.py` | 재생성 결과 동일 → `README.md` diff 없음 |
| 옛 문구 0건 스캔 | 「·  투자 실행액」「의 합」「투자실행금액 대비 연환산 수익률 ·」「기간 순현금」「검색대상기간의 누적 순현금」「계약된 할인율」「기간 투자수익」「기간 투자실행금」「기간 가중평균」「채권 건수」「인 표본」「연 환산」「<span>행</span>」 — app.html·낱장 툴팁 0건. app.html JS 주석(2319 · 2350줄)의 「기간 투자수익 / 기간 투자실행금」「ad 의 합」은 화면 글자가 아니라 두었다 |
| 헤드리스 호버 QA `step13_qa/hover_qa.js` | 47 / 47 PASS — 첫 줄(산식·가운뎃점 0)·행 2칸·왼쪽 기호만·오른쪽 값만·연환산 행 맨 아래·⑤ 첫 줄 두 줄·`tip-row`/`tip-green`/`tip-row sum` 클래스·패널 폭 256px·`<sub>` 글자 i/r/a/t 9.17px `vertical-align: sub`·④ 툴팁 PA·PM = 같은 화면 카드 값·⑤ 툴팁 PYa = ④ 표기값 |

### 호버 QA 47건

| 판정 | 화면 | 앵커 | 패널 폭 | 크롭 |
|---|---|---|---|---|
| PASS | `invest-assets.html` | 예상 연환산 수익률 #0 | 256px | assets-B-card-yield.png |
| PASS | `invest-assets.html` | 예상 연환산 수익률 #1 | 256px | assets-B-th-yield-status.png |
| PASS | `invest-assets.html` | 예상 연환산 수익률 #2 | 256px | assets-B-th-yield-merchant.png |
| PASS | `invest-assets.html` | 가중평균 금융일수 #0 | 256px | assets-C-th-wavg-status.png |
| PASS | `invest-assets.html` | 가중평균 금융일수 #1 | 256px | assets-C-th-wavg-merchant.png |
| PASS | `invest-assets.html` | 입금부족률 #0 | 256px | assets-D-th-shortfall-status.png |
| PASS | `invest-assets.html` | 입금부족률 #1 | 256px | assets-D-th-shortfall-merchant.png |
| PASS | `invest-assets--empty.html` | 예상 연환산 수익률 #0 | 256px | assets-empty-B-card-yield.png |
| PASS | `invest-assets--empty.html` | 예상 연환산 수익률 #1 | 256px | assets-empty-B-th-yield-status.png |
| PASS | `invest-profit.html` | 투자실행금액 대비 #0 | 256px | profit-E-py-exec.png |
| PASS | `invest-profit.html` | 투자 자산 대비 #0 | 256px | profit-F-py-asset.png |
| PASS | `invest-profit.html` | 투자실행금 #0 | 256px | profit-G-th-exec.png |
| PASS | `invest-profit.html` | 연환산 수익률 #0 | 256px | profit-H-th-yield.png |
| PASS | `invest-profit--weekly.html` | 투자실행금액 대비 #0 | 256px | profit-weekly-E-py-exec.png |
| PASS | `invest-profit--weekly.html` | 투자 자산 대비 #0 | 256px | profit-weekly-F-py-asset.png |
| PASS | `invest-profit--weekly.html` | 투자실행금 #0 | 256px | profit-weekly-G-th-exec.png |
| PASS | `invest-profit--weekly.html` | 연환산 수익률 #0 | 256px | profit-weekly-H-th-yield.png |
| PASS | `invest-profit--monthly.html` | 투자실행금액 대비 #0 | 256px | profit-monthly-E-py-exec.png |
| PASS | `invest-profit--monthly.html` | 투자 자산 대비 #0 | 256px | profit-monthly-F-py-asset.png |
| PASS | `invest-profit--monthly.html` | 투자실행금 #0 | 256px | profit-monthly-G-th-exec.png |
| PASS | `invest-profit--monthly.html` | 연환산 수익률 #0 | 256px | profit-monthly-H-th-yield.png |
| PASS | `invest-profit--empty.html` | 투자실행금액 대비 #0 | 256px | profit-empty-E-py-exec.png |
| PASS | `invest-profit--empty.html` | 투자 자산 대비 #0 | 256px | profit-empty-F-py-asset.png |
| PASS | `invest-sim--result.html` | 투자실행금액 대비 #0 | 256px | sim-result-E-py-exec.png |
| PASS | `invest-sim--result.html` | 투자 자산 대비 #0 | 256px | sim-result-F-py-asset.png |
| PASS | `invest-sim--result.html` | 투자실행금 #0 | 256px | sim-result-G-th-exec.png |
| PASS | `invest-sim--result.html` | 연환산 수익률 #0 | 256px | sim-result-H-th-yield.png |
| PASS | `app.html#invest-assets` | 투자실행액 #0 | 256px | app-assets-A-card-exec.png |
| PASS | `app.html#invest-assets` | 예상 연환산 수익률 #0 | 256px | app-assets-B-card-yield.png |
| PASS | `app.html#invest-assets` | 예상 연환산 수익률 #1 | 256px | app-assets-B-th-yield-status.png |
| PASS | `app.html#invest-assets` | 예상 연환산 수익률 #2 | 256px | app-assets-B-th-yield-merchant.png |
| PASS | `app.html#invest-assets` | 가중평균 금융일수 #0 | 256px | app-assets-C-th-wavg-status.png |
| PASS | `app.html#invest-assets` | 가중평균 금융일수 #1 | 256px | app-assets-C-th-wavg-merchant.png |
| PASS | `app.html#invest-assets` | 입금부족률 #0 | 256px | app-assets-D-th-shortfall-status.png |
| PASS | `app.html#invest-assets` | 입금부족률 #1 | 256px | app-assets-D-th-shortfall-merchant.png |
| PASS | `app.html#invest-assets/empty` | 예상 연환산 수익률 #0 | 256px | app-assets-empty-B-card-yield.png |
| PASS | `app.html#invest-assets/empty` | 예상 연환산 수익률 #1 | 256px | app-assets-empty-B-th-yield-status.png |
| PASS | `app.html#invest-profit` | 투자실행금액 대비 #0 | 256px | app-profit-E-py-exec.png |
| PASS | `app.html#invest-profit` | 투자 자산 대비 #0 | 256px | app-profit-F-py-asset.png |
| PASS | `app.html#invest-profit` | 투자실행금 #0 | 256px | app-profit-G-th-exec.png |
| PASS | `app.html#invest-profit` | 연환산 수익률 #0 | 256px | app-profit-H-th-yield.png |
| PASS | `app.html#invest-profit/empty` | 투자실행금액 대비 #0 | 256px | app-profit-empty-E-py-exec.png |
| PASS | `app.html#invest-profit/empty` | 투자 자산 대비 #0 | 256px | app-profit-empty-F-py-asset.png |
| PASS | `app.html#invest-sim/result` | 투자실행금액 대비 #0 | 256px | app-sim-result-E-py-exec.png |
| PASS | `app.html#invest-sim/result` | 투자 자산 대비 #0 | 256px | app-sim-result-F-py-asset.png |
| PASS | `app.html#invest-sim/result` | 투자실행금 #0 | 256px | app-sim-result-G-th-exec.png |
| PASS | `app.html#invest-sim/result` | 연환산 수익률 #0 | 256px | app-sim-result-H-th-yield.png |

크롭 PNG: `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/step13_qa/*.png` (첨자 소문자 확인: `app-assets-A-card-exec.png` · `app-profit-F-py-asset.png` · `assets-C-th-wavg-status.png`)

## 5. git diff (출력 레포)

```
 app.html                         | 85 +++++++++++++++++++++-------------------
 invest-assets--cert-confirm.html | 14 +++----
 invest-assets--download.html     | 14 +++----
 invest-assets--empty.html        | 14 +++----
 invest-assets.html               | 14 +++----
 invest-profit--empty.html        |  8 ++--
 invest-profit--monthly.html      |  8 ++--
 invest-profit--weekly.html       |  8 ++--
 invest-profit.html               |  8 ++--
 invest-sim--result.html          |  6 +--
 10 files changed, 91 insertions(+), 88 deletions(-)
```

변경 줄 전부가 `tip-anchor` … `tip-panel` 안쪽이다(비툴팁 줄 0). 전문:

```diff
diff --git a/app.html b/app.html
index 0bb3b2b..23583d6 100644
--- a/app.html
+++ b/app.html
@@ -1740,19 +1740,24 @@ function wavg(a, k, wk){ var n=0, d=0; for(var i=0;i<a.length;i++){ n += a[i][k]
    옆 칸 금액(미회수 Σ A<sub>i</sub>)까지 셋이 각자 다른 집합에서 나오므로, 행을 금액으로 가중평균해도
    현황표의 두 칸과 맞아떨어지지 않는다. 그 모집단을 열머리 툴팁이 그대로 적는다.
    건수는 채권 원장 실측이다(daily_ledger.py) — 화면에 손으로 적지 않는다. */
-var POP_W = {of:'보유 채권 전체', n:'61,760건'};
-var POP_S = {of:'선정산일이 오늘 기준 20일 전 ~ 11일 전인 표본', n:'3,200건'};
+var POP_W = {head:'D = Σ( A<sub>i</sub> × D<sub>i</sub> ) ÷ Σ A<sub>i</sub>', of:'보유 채권 전체', n:'61,760건'};
+var POP_S = {head:'LR = Σ L<sub>i</sub> ÷ Σ A<sub>i</sub>', of:'선정산일이 오늘 기준 20일 전 ~ 11일 전', n:'3,200건'};
 function popTh(label, p){
   return '<th class="num"><span class="tooltip wide"><span class="tip-anchor">' + label + '</span>' +
-         '<span class="tip-panel">' + p.of +
-           '<span class="tip-row"><span>채권 건수</span><span class="tip-green">' + p.n + '</span></span>' +
+         '<span class="tip-panel">' + p.head +
+           '<span class="tip-row"><span>i</span><span class="tip-green">' + p.of + ' · ' + p.n + '</span></span>' +
          '</span></span></th>';
 }
-var YR_TIP_HEAD = 'Y<sub>r</sub> · 예상 연환산 수익률 · r × 365 ÷ D';
+var YR_TIP_HEAD = 'Y<sub>r</sub> = r × 365 ÷ D';
 var YR_TIP_ROW  = '<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span>';
-function yrTh(){
+function yrRows(w){
+  return '<span class="tip-row"><span>r</span><span class="tip-green">' + fx(RATE_PCT, 2) + '%</span></span>' +
+         '<span class="tip-row"><span>D</span><span class="tip-green">' + (w === null ? '집계 대상 없음' : fx(w, 2) + '일') + '</span></span>' +
+         YR_TIP_ROW;
+}
+function yrTh(w){
   return '<th class="num"><span class="tooltip wide"><span class="tip-anchor">예상 연환산 수익률</span>' +
-         '<span class="tip-panel">' + YR_TIP_HEAD + YR_TIP_ROW + '</span></span></th>';
+         '<span class="tip-panel">' + YR_TIP_HEAD + yrRows(w) + '</span></span></th>';
 }
 /* ── ③ ⑤ ⑥ 단일 원천 ────────────────────────────────────────────
    산식은 생성기 daily_ledger.py 의 ty_third · ty_asset · ty_row 한 벌에서 온다
@@ -1768,16 +1773,16 @@ function ty6(profit, execu, w){ var third = ty3(execu);
 /* ⑥ 열머리 — 투자자어드민 기호정리표 V1.3 표 4 */
 function tyTh(){
   return '<th class="num"><span class="tooltip wide"><span class="tip-anchor">연환산 수익률</span>' +
-         '<span class="tip-panel">PY<sub>a</sub> · 연환산 수익률 · PMR × 365 ÷ PD' +
+         '<span class="tip-panel">PY<sub>a</sub> = PMR × 365 ÷ PD' +
+           '<span class="tip-row"><span>i</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span>' +
            '<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span>' +
-           '<span class="tip-row"><span>행</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span>' +
          '</span></span></th>';
 }
 /* ③ 열머리 — 투자자어드민 기호정리표 V1.3 표 4 */
 function thirdTh(){
   return '<th class="num"><span class="tooltip wide"><span class="tip-anchor">투자실행금</span>' +
-         '<span class="tip-panel">PA · 투자실행금 · Σ A<sub>i</sub>' +
-           '<span class="tip-row"><span>행</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span>' +
+         '<span class="tip-panel">PA = Σ A<sub>i</sub>' +
+           '<span class="tip-row"><span>i</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span>' +
          '</span></span></th>';
 }
 function esc(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
@@ -2172,8 +2177,9 @@ RENDER['invest-assets'] = function(){
       '<div class="summary-sub">투자실행액 + 순현금</div></div>' +
     '<div class="summary-card"><div class="summary-label">' +
       '<span class="tooltip wide"><span class="tip-anchor">투자실행액</span>' +
-        '<span class="tip-panel">Σ A<sub>i</sub> · 투자 실행액 · A<sub>i</sub> = 순지급액<sub>i</sub> × (1 − r) 의 합' +
-          '<span class="tip-row"><span>r</span><span class="tip-green">계약된 할인율 · ' + fx(RATE_PCT, 2) + '%</span></span>' +
+        '<span class="tip-panel">Σ A<sub>i</sub>' +
+          '<span class="tip-row"><span>A<sub>i</sub></span><span class="tip-green">순지급액<sub>i</sub> × (1 − r)</span></span>' +
+          '<span class="tip-row"><span>r</span><span class="tip-green">' + fx(RATE_PCT, 2) + '%</span></span>' +
         '</span></span></div>' +
       '<div class="summary-value">' + fmt(exec) + '<span class="unit">원</span></div>' +
       '<div class="summary-sub">비중 ' + fx(rExec, 1) + '% · 보관 ㈜페이허그</div></div>' +
@@ -2182,16 +2188,13 @@ RENDER['invest-assets'] = function(){
       '<div class="summary-sub">비중 ' + fx(rCash, 1) + '% · 보관 ㈜쿠콘</div></div>' +
     '<div class="summary-card"><div class="summary-label">' +
       '<span class="tooltip wide"><span class="tip-anchor">예상 연환산 수익률</span>' +
-        '<span class="tip-panel">' + YR_TIP_HEAD + YR_TIP_ROW +
-          '<span class="tip-row"><span>r</span><span class="tip-green">계약된 할인율 · ' + fx(RATE_PCT, 2) + '%</span></span>' +
-          '<span class="tip-row"><span>D</span><span class="tip-green">가중평균 금융일수 · ' + (wv === null ? '집계 대상 없음' : fx(wv, 2) + '일') + '</span></span>' +
-          '<span class="tip-row"><span>연 환산</span><span class="tip-green">' + fx(tyv, 2) + '%</span></span>' +
+        '<span class="tip-panel">' + YR_TIP_HEAD + yrRows(wv) +
         '</span></span></div>' +
       '<div class="summary-value">' + fx(tyv, 2) + '<span class="unit">%</span></div>' +
       '<div class="summary-sub">' + (wv === null ? '가중평균 금융일수 집계 대상 없음' : '가중평균 금융일수 ' + fx(wv, 2) + '일 기준') + '</div></div>';
 
   var h = '<thead><tr><th>자산 구분</th><th class="num">금액 (원)</th>' + popTh('가중평균 금융일수', POP_W) +
-          popTh('입금부족률', POP_S) + yrTh() +
+          popTh('입금부족률', POP_S) + yrTh(wv) +
           '<th class="num">비중</th><th>보관</th></tr></thead><tbody>';
   if(!arows.length){ h += emptyRow(7, '조회 결과가 없습니다.'); }
   else {
@@ -2220,7 +2223,7 @@ RENDER['invest-assets'] = function(){
   var slice = view.slice((IA.page - 1) * iaSize, IA.page * iaSize);
   var mm = M('ia-merch', 'invest-assets'), mp = M('ia-merch-page', 'invest-assets');
   var IA_HEAD = '<th>가맹점</th><th class="num">투자실행액 (원)</th>' + popTh('가중평균 금융일수', POP_W) +
-                popTh('입금부족률', POP_S) + yrTh() +
+                popTh('입금부족률', POP_S) + yrTh(wv) +
                 '<th class="num">비중</th>';
   if(!mrows.length){
     mm.innerHTML = emptyTable(IA_HEAD, 6, '조회 결과가 없습니다.');
@@ -2395,21 +2398,21 @@ RENDER['invest-profit'] = function(){
       '<div class="summary-value">' + fmt(profit) + '<span class="unit">원</span></div></div>' +
     '<div class="stat"><div class="summary-label">연환산 수익률</div><div class="ty-split">' +
       '<div><div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자실행금액 대비</span>' +
-        '<span class="tip-panel">PY<sub>a</sub> · 투자실행금액 대비 연환산 수익률 · PMR × 365 ÷ PD' +
-          '<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span>' +
-          '<span class="tip-row"><span>PMR</span><span class="tip-green">기간 투자수익율 · PM ÷ PA = ' + fx(exec ? r6(profit / exec * 100) : 0, 6) + '%</span></span>' +
-          '<span class="tip-row"><span>PM</span><span class="tip-green">기간 투자수익 · ' + fmt(profit) + '원</span></span>' +
-          '<span class="tip-row"><span>PA</span><span class="tip-green">기간 투자실행금 · ' + fmt(exec) + '원</span></span>' +
-          '<span class="tip-row"><span>PD</span><span class="tip-green">기간 가중평균 금융일수 · ' + fx(wAvg, 2) + '일</span></span>' +
+        '<span class="tip-panel">PY<sub>a</sub> = PMR × 365 ÷ PD' +
+          '<span class="tip-row"><span>PMR</span><span class="tip-green">' + fx(exec ? r6(profit / exec * 100) : 0, 6) + '%</span></span>' +
+          '<span class="tip-row"><span>PM</span><span class="tip-green">' + fmt(profit) + '원</span></span>' +
+          '<span class="tip-row"><span>PA</span><span class="tip-green">' + fmt(exec) + '원</span></span>' +
+          '<span class="tip-row"><span>PD</span><span class="tip-green">' + fx(wAvg, 2) + '일</span></span>' +
+          YR_TIP_ROW +
         '</span></span></div>' +
         '<div class="summary-value">' + fx(tyExec, 2) + '<span class="unit">%</span></div></div>' +
       '<div><div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자 자산 대비</span>' +
-        '<span class="tip-panel">PY<sub>t</sub> · 투자 자산 대비 연환산 수익률 · PM × 365 ÷ ( Σ( A<sub>i</sub> × D<sub>i</sub> ) + PEC )' +
-          '<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span>' +
-          '<span class="tip-row"><span>PY<sub>a</sub></span><span class="tip-green">투자실행금액 대비 연환산 수익률 · ' + fx(tyExec, 2) + '%</span></span>' +
+        '<span class="tip-panel">PY<sub>t</sub> = PY<sub>a</sub> × 채권 비중 + 순현금 수익률 × 순현금 비중<br>= PM × 365 ÷ ( Σ( A<sub>i</sub> × D<sub>i</sub> ) + PEC )' +
+          '<span class="tip-row"><span>PY<sub>a</sub></span><span class="tip-green">' + fx(tyExec, 2) + '%</span></span>' +
           '<span class="tip-row"><span>Σ( A<sub>i</sub> × D<sub>i</sub> )</span><span class="tip-green">' + fmt(adOfRows(rows)) + '원</span></span>' +
-          '<span class="tip-row"><span>PEC</span><span class="tip-green">검색대상기간의 누적 순현금 · ' + fmt((cashRow() ? cashRow().amount : 0) * ecDays()) + '원</span></span>' +
-          '<span class="tip-row sum"><span>EC</span><span>순현금 · ' + fmt(cashRow() ? cashRow().amount : 0) + '원 × ' + ecDays() + '일</span></span>' +
+          '<span class="tip-row"><span>PEC</span><span class="tip-green">' + fmt((cashRow() ? cashRow().amount : 0) * ecDays()) + '원</span></span>' +
+          '<span class="tip-row sum"><span>EC</span><span>' + fmt(cashRow() ? cashRow().amount : 0) + '원 × ' + ecDays() + '일</span></span>' +
+          YR_TIP_ROW +
         '</span></span></div>' +
         '<div class="summary-value">' + fx(tyAsset, 2) + '<span class="unit">%</span></div></div>' +
     '</div></div>';
@@ -2690,21 +2693,21 @@ function simSyncRows(){
 function simTyTip(R){
   return '<div class="stat"><div class="summary-label">연환산 수익률</div><div class="ty-split">' +
     '<div><div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자실행금액 대비</span>' +
-      '<span class="tip-panel">PY<sub>a</sub> · 투자실행금액 대비 연환산 수익률 · PMR × 365 ÷ PD' +
-        '<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span>' +
-        '<span class="tip-row"><span>PMR</span><span class="tip-green">기간 투자수익율 · PM ÷ PA = ' + fx(R.PMR, 6) + '%</span></span>' +
-        '<span class="tip-row"><span>PM</span><span class="tip-green">기간 투자수익 · ' + fmt(R.PM) + '원</span></span>' +
-        '<span class="tip-row"><span>PA</span><span class="tip-green">기간 투자실행금 · ' + fmt(R.PA) + '원</span></span>' +
-        '<span class="tip-row"><span>PD</span><span class="tip-green">기간 가중평균 금융일수 · ' + fx(R.PwD, 2) + '일</span></span>' +
+      '<span class="tip-panel">PY<sub>a</sub> = PMR × 365 ÷ PD' +
+        '<span class="tip-row"><span>PMR</span><span class="tip-green">' + fx(R.PMR, 6) + '%</span></span>' +
+        '<span class="tip-row"><span>PM</span><span class="tip-green">' + fmt(R.PM) + '원</span></span>' +
+        '<span class="tip-row"><span>PA</span><span class="tip-green">' + fmt(R.PA) + '원</span></span>' +
+        '<span class="tip-row"><span>PD</span><span class="tip-green">' + fx(R.PwD, 2) + '일</span></span>' +
+        YR_TIP_ROW +
       '</span></span></div>' +
       '<div class="summary-value' + (R.TY4 < 0 ? ' neg' : '') + '">' + fx(R.TY4, 2) + '<span class="unit">%</span></div></div>' +
     '<div><div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자 자산 대비</span>' +
-      '<span class="tip-panel">PY<sub>t</sub> · 투자 자산 대비 연환산 수익률 · PM × 365 ÷ ( Σ( A<sub>i</sub> × D<sub>i</sub> ) + PEC )' +
-        '<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span>' +
-        '<span class="tip-row"><span>PY<sub>a</sub></span><span class="tip-green">투자실행금액 대비 연환산 수익률 · ' + fx(R.TY4, 2) + '%</span></span>' +
+      '<span class="tip-panel">PY<sub>t</sub> = PY<sub>a</sub> × 채권 비중 + 순현금 수익률 × 순현금 비중<br>= PM × 365 ÷ ( Σ( A<sub>i</sub> × D<sub>i</sub> ) + PEC )' +
+        '<span class="tip-row"><span>PY<sub>a</sub></span><span class="tip-green">' + fx(R.TY4, 2) + '%</span></span>' +
         '<span class="tip-row"><span>Σ( A<sub>i</sub> × D<sub>i</sub> )</span><span class="tip-green">' + fmt(R.AD) + '원</span></span>' +
-        '<span class="tip-row"><span>PEC</span><span class="tip-green">검색대상기간의 누적 순현금 · ' + fmt(R.PEC) + '원</span></span>' +
-        '<span class="tip-row sum"><span>EC</span><span>순현금 · ' + fmt(R.cash) + '원 × ' + R.ECD + '일</span></span>' +
+        '<span class="tip-row"><span>PEC</span><span class="tip-green">' + fmt(R.PEC) + '원</span></span>' +
+        '<span class="tip-row sum"><span>EC</span><span>' + fmt(R.cash) + '원 × ' + R.ECD + '일</span></span>' +
+        YR_TIP_ROW +
       '</span></span></div>' +
       '<div class="summary-value' + (R.TY5 < 0 ? ' neg' : '') + '">' + fx(R.TY5, 2) + '<span class="unit">%</span></div></div>' +
   '</div></div>';
diff --git a/invest-assets--cert-confirm.html b/invest-assets--cert-confirm.html
index f2f0be3..0cc4d3d 100644
--- a/invest-assets--cert-confirm.html
+++ b/invest-assets--cert-confirm.html
@@ -146,7 +146,7 @@
         <div class="summary-sub">비중 20.0% · 보관 ㈜쿠콘</div>
       </div>
       <div class="summary-card">
-        <div class="summary-label"><span class="tooltip wide"><span class="tip-anchor">예상 연환산 수익률</span><span class="tip-panel">Y<sub>r</sub> · 예상 연환산 수익률 · r × 365 ÷ D<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span><span class="tip-row"><span>r</span><span class="tip-green">계약된 할인율 · 0.11%</span></span><span class="tip-row"><span>D</span><span class="tip-green">가중평균 금융일수 · 3.04일</span></span><span class="tip-row"><span>연 환산</span><span class="tip-green">13.21%</span></span></span></span></div>
+        <div class="summary-label"><span class="tooltip wide"><span class="tip-anchor">예상 연환산 수익률</span><span class="tip-panel">Y<sub>r</sub> = r × 365 ÷ D<span class="tip-row"><span>r</span><span class="tip-green">0.11%</span></span><span class="tip-row"><span>D</span><span class="tip-green">3.04일</span></span><span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></div>
         <div class="summary-value">13.21<span class="unit">%</span></div>
         <div class="summary-sub">가중평균 금융일수 3.04일 기준</div>
       </div>
@@ -169,9 +169,9 @@
             <tr>
               <th>자산 구분</th>
               <th class="num">금액 (원)</th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">가중평균 금융일수</span><span class="tip-panel">보유 채권 전체<span class="tip-row"><span>채권 건수</span><span class="tip-green">61,760건</span></span></span></span></th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">입금부족률</span><span class="tip-panel">선정산일이 오늘 기준 20일 전 ~ 11일 전인 표본<span class="tip-row"><span>채권 건수</span><span class="tip-green">3,200건</span></span></span></span></th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">예상 연환산 수익률</span><span class="tip-panel">Y<sub>r</sub> · 예상 연환산 수익률 · r × 365 ÷ D<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">가중평균 금융일수</span><span class="tip-panel">D = Σ( A<sub>i</sub> × D<sub>i</sub> ) ÷ Σ A<sub>i</sub><span class="tip-row"><span>i</span><span class="tip-green">보유 채권 전체 · 61,760건</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">입금부족률</span><span class="tip-panel">LR = Σ L<sub>i</sub> ÷ Σ A<sub>i</sub><span class="tip-row"><span>i</span><span class="tip-green">선정산일이 오늘 기준 20일 전 ~ 11일 전 · 3,200건</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">예상 연환산 수익률</span><span class="tip-panel">Y<sub>r</sub> = r × 365 ÷ D<span class="tip-row"><span>r</span><span class="tip-green">0.11%</span></span><span class="tip-row"><span>D</span><span class="tip-green">3.04일</span></span><span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></th>
               <th class="num">비중</th>
               <th>보관</th>
             </tr>
@@ -231,9 +231,9 @@
             <tr>
               <th>가맹점</th>
               <th class="num">투자실행액 (원)</th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">가중평균 금융일수</span><span class="tip-panel">보유 채권 전체<span class="tip-row"><span>채권 건수</span><span class="tip-green">61,760건</span></span></span></span></th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">입금부족률</span><span class="tip-panel">선정산일이 오늘 기준 20일 전 ~ 11일 전인 표본<span class="tip-row"><span>채권 건수</span><span class="tip-green">3,200건</span></span></span></span></th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">예상 연환산 수익률</span><span class="tip-panel">Y<sub>r</sub> · 예상 연환산 수익률 · r × 365 ÷ D<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">가중평균 금융일수</span><span class="tip-panel">D = Σ( A<sub>i</sub> × D<sub>i</sub> ) ÷ Σ A<sub>i</sub><span class="tip-row"><span>i</span><span class="tip-green">보유 채권 전체 · 61,760건</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">입금부족률</span><span class="tip-panel">LR = Σ L<sub>i</sub> ÷ Σ A<sub>i</sub><span class="tip-row"><span>i</span><span class="tip-green">선정산일이 오늘 기준 20일 전 ~ 11일 전 · 3,200건</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">예상 연환산 수익률</span><span class="tip-panel">Y<sub>r</sub> = r × 365 ÷ D<span class="tip-row"><span>r</span><span class="tip-green">0.11%</span></span><span class="tip-row"><span>D</span><span class="tip-green">3.04일</span></span><span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></th>
               <th class="num">비중</th>
             </tr>
           </thead>
diff --git a/invest-assets--download.html b/invest-assets--download.html
index b68b167..0aab794 100644
--- a/invest-assets--download.html
+++ b/invest-assets--download.html
@@ -140,7 +140,7 @@
         <div class="summary-sub">비중 20.0% · 보관 ㈜쿠콘</div>
       </div>
       <div class="summary-card">
-        <div class="summary-label"><span class="tooltip wide"><span class="tip-anchor">예상 연환산 수익률</span><span class="tip-panel">Y<sub>r</sub> · 예상 연환산 수익률 · r × 365 ÷ D<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span><span class="tip-row"><span>r</span><span class="tip-green">계약된 할인율 · 0.11%</span></span><span class="tip-row"><span>D</span><span class="tip-green">가중평균 금융일수 · 3.04일</span></span><span class="tip-row"><span>연 환산</span><span class="tip-green">13.21%</span></span></span></span></div>
+        <div class="summary-label"><span class="tooltip wide"><span class="tip-anchor">예상 연환산 수익률</span><span class="tip-panel">Y<sub>r</sub> = r × 365 ÷ D<span class="tip-row"><span>r</span><span class="tip-green">0.11%</span></span><span class="tip-row"><span>D</span><span class="tip-green">3.04일</span></span><span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></div>
         <div class="summary-value">13.21<span class="unit">%</span></div>
         <div class="summary-sub">가중평균 금융일수 3.04일 기준</div>
       </div>
@@ -163,9 +163,9 @@
             <tr>
               <th>자산 구분</th>
               <th class="num">금액 (원)</th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">가중평균 금융일수</span><span class="tip-panel">보유 채권 전체<span class="tip-row"><span>채권 건수</span><span class="tip-green">61,760건</span></span></span></span></th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">입금부족률</span><span class="tip-panel">선정산일이 오늘 기준 20일 전 ~ 11일 전인 표본<span class="tip-row"><span>채권 건수</span><span class="tip-green">3,200건</span></span></span></span></th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">예상 연환산 수익률</span><span class="tip-panel">Y<sub>r</sub> · 예상 연환산 수익률 · r × 365 ÷ D<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">가중평균 금융일수</span><span class="tip-panel">D = Σ( A<sub>i</sub> × D<sub>i</sub> ) ÷ Σ A<sub>i</sub><span class="tip-row"><span>i</span><span class="tip-green">보유 채권 전체 · 61,760건</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">입금부족률</span><span class="tip-panel">LR = Σ L<sub>i</sub> ÷ Σ A<sub>i</sub><span class="tip-row"><span>i</span><span class="tip-green">선정산일이 오늘 기준 20일 전 ~ 11일 전 · 3,200건</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">예상 연환산 수익률</span><span class="tip-panel">Y<sub>r</sub> = r × 365 ÷ D<span class="tip-row"><span>r</span><span class="tip-green">0.11%</span></span><span class="tip-row"><span>D</span><span class="tip-green">3.04일</span></span><span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></th>
               <th class="num">비중</th>
               <th>보관</th>
             </tr>
@@ -225,9 +225,9 @@
             <tr>
               <th>가맹점</th>
               <th class="num">투자실행액 (원)</th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">가중평균 금융일수</span><span class="tip-panel">보유 채권 전체<span class="tip-row"><span>채권 건수</span><span class="tip-green">61,760건</span></span></span></span></th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">입금부족률</span><span class="tip-panel">선정산일이 오늘 기준 20일 전 ~ 11일 전인 표본<span class="tip-row"><span>채권 건수</span><span class="tip-green">3,200건</span></span></span></span></th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">예상 연환산 수익률</span><span class="tip-panel">Y<sub>r</sub> · 예상 연환산 수익률 · r × 365 ÷ D<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">가중평균 금융일수</span><span class="tip-panel">D = Σ( A<sub>i</sub> × D<sub>i</sub> ) ÷ Σ A<sub>i</sub><span class="tip-row"><span>i</span><span class="tip-green">보유 채권 전체 · 61,760건</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">입금부족률</span><span class="tip-panel">LR = Σ L<sub>i</sub> ÷ Σ A<sub>i</sub><span class="tip-row"><span>i</span><span class="tip-green">선정산일이 오늘 기준 20일 전 ~ 11일 전 · 3,200건</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">예상 연환산 수익률</span><span class="tip-panel">Y<sub>r</sub> = r × 365 ÷ D<span class="tip-row"><span>r</span><span class="tip-green">0.11%</span></span><span class="tip-row"><span>D</span><span class="tip-green">3.04일</span></span><span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></th>
               <th class="num">비중</th>
             </tr>
           </thead>
diff --git a/invest-assets--empty.html b/invest-assets--empty.html
index 478193e..17e338e 100644
--- a/invest-assets--empty.html
+++ b/invest-assets--empty.html
@@ -131,7 +131,7 @@
         <div class="summary-sub">비중 0.0% · 보관 ㈜쿠콘</div>
       </div>
       <div class="summary-card">
-        <div class="summary-label"><span class="tooltip wide"><span class="tip-anchor">예상 연환산 수익률</span><span class="tip-panel">Y<sub>r</sub> · 예상 연환산 수익률 · r × 365 ÷ D<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span><span class="tip-row"><span>r</span><span class="tip-green">계약된 할인율 · 0.11%</span></span><span class="tip-row"><span>D</span><span class="tip-green">가중평균 금융일수 · 집계 대상 없음</span></span><span class="tip-row"><span>연 환산</span><span class="tip-green">0.00%</span></span></span></span></div>
+        <div class="summary-label"><span class="tooltip wide"><span class="tip-anchor">예상 연환산 수익률</span><span class="tip-panel">Y<sub>r</sub> = r × 365 ÷ D<span class="tip-row"><span>r</span><span class="tip-green">0.11%</span></span><span class="tip-row"><span>D</span><span class="tip-green">집계 대상 없음</span></span><span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></div>
         <div class="summary-value">0.00<span class="unit">%</span></div>
         <div class="summary-sub">가중평균 금융일수 집계 대상 없음</div>
       </div>
@@ -154,9 +154,9 @@
             <tr>
               <th>자산 구분</th>
               <th class="num">금액 (원)</th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">가중평균 금융일수</span><span class="tip-panel">보유 채권 전체<span class="tip-row"><span>채권 건수</span><span class="tip-green">61,760건</span></span></span></span></th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">입금부족률</span><span class="tip-panel">선정산일이 오늘 기준 20일 전 ~ 11일 전인 표본<span class="tip-row"><span>채권 건수</span><span class="tip-green">3,200건</span></span></span></span></th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">예상 연환산 수익률</span><span class="tip-panel">Y<sub>r</sub> · 예상 연환산 수익률 · r × 365 ÷ D<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">가중평균 금융일수</span><span class="tip-panel">D = Σ( A<sub>i</sub> × D<sub>i</sub> ) ÷ Σ A<sub>i</sub><span class="tip-row"><span>i</span><span class="tip-green">보유 채권 전체 · 61,760건</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">입금부족률</span><span class="tip-panel">LR = Σ L<sub>i</sub> ÷ Σ A<sub>i</sub><span class="tip-row"><span>i</span><span class="tip-green">선정산일이 오늘 기준 20일 전 ~ 11일 전 · 3,200건</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">예상 연환산 수익률</span><span class="tip-panel">Y<sub>r</sub> = r × 365 ÷ D<span class="tip-row"><span>r</span><span class="tip-green">0.11%</span></span><span class="tip-row"><span>D</span><span class="tip-green">집계 대상 없음</span></span><span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></th>
               <th class="num">비중</th>
               <th>보관</th>
             </tr>
@@ -191,9 +191,9 @@
             <tr>
               <th>가맹점</th>
               <th class="num">투자실행액 (원)</th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">가중평균 금융일수</span><span class="tip-panel">보유 채권 전체<span class="tip-row"><span>채권 건수</span><span class="tip-green">61,760건</span></span></span></span></th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">입금부족률</span><span class="tip-panel">선정산일이 오늘 기준 20일 전 ~ 11일 전인 표본<span class="tip-row"><span>채권 건수</span><span class="tip-green">3,200건</span></span></span></span></th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">예상 연환산 수익률</span><span class="tip-panel">Y<sub>r</sub> · 예상 연환산 수익률 · r × 365 ÷ D<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">가중평균 금융일수</span><span class="tip-panel">D = Σ( A<sub>i</sub> × D<sub>i</sub> ) ÷ Σ A<sub>i</sub><span class="tip-row"><span>i</span><span class="tip-green">보유 채권 전체 · 61,760건</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">입금부족률</span><span class="tip-panel">LR = Σ L<sub>i</sub> ÷ Σ A<sub>i</sub><span class="tip-row"><span>i</span><span class="tip-green">선정산일이 오늘 기준 20일 전 ~ 11일 전 · 3,200건</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">예상 연환산 수익률</span><span class="tip-panel">Y<sub>r</sub> = r × 365 ÷ D<span class="tip-row"><span>r</span><span class="tip-green">0.11%</span></span><span class="tip-row"><span>D</span><span class="tip-green">집계 대상 없음</span></span><span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></th>
               <th class="num">비중</th>
             </tr>
           </thead>
diff --git a/invest-assets.html b/invest-assets.html
index a775221..7149565 100644
--- a/invest-assets.html
+++ b/invest-assets.html
@@ -130,7 +130,7 @@
         <div class="summary-sub">비중 20.0% · 보관 ㈜쿠콘</div>
       </div>
       <div class="summary-card">
-        <div class="summary-label"><span class="tooltip wide"><span class="tip-anchor">예상 연환산 수익률</span><span class="tip-panel">Y<sub>r</sub> · 예상 연환산 수익률 · r × 365 ÷ D<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span><span class="tip-row"><span>r</span><span class="tip-green">계약된 할인율 · 0.11%</span></span><span class="tip-row"><span>D</span><span class="tip-green">가중평균 금융일수 · 3.04일</span></span><span class="tip-row"><span>연 환산</span><span class="tip-green">13.21%</span></span></span></span></div>
+        <div class="summary-label"><span class="tooltip wide"><span class="tip-anchor">예상 연환산 수익률</span><span class="tip-panel">Y<sub>r</sub> = r × 365 ÷ D<span class="tip-row"><span>r</span><span class="tip-green">0.11%</span></span><span class="tip-row"><span>D</span><span class="tip-green">3.04일</span></span><span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></div>
         <div class="summary-value">13.21<span class="unit">%</span></div>
         <div class="summary-sub">가중평균 금융일수 3.04일 기준</div>
       </div>
@@ -153,9 +153,9 @@
             <tr>
               <th>자산 구분</th>
               <th class="num">금액 (원)</th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">가중평균 금융일수</span><span class="tip-panel">보유 채권 전체<span class="tip-row"><span>채권 건수</span><span class="tip-green">61,760건</span></span></span></span></th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">입금부족률</span><span class="tip-panel">선정산일이 오늘 기준 20일 전 ~ 11일 전인 표본<span class="tip-row"><span>채권 건수</span><span class="tip-green">3,200건</span></span></span></span></th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">예상 연환산 수익률</span><span class="tip-panel">Y<sub>r</sub> · 예상 연환산 수익률 · r × 365 ÷ D<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">가중평균 금융일수</span><span class="tip-panel">D = Σ( A<sub>i</sub> × D<sub>i</sub> ) ÷ Σ A<sub>i</sub><span class="tip-row"><span>i</span><span class="tip-green">보유 채권 전체 · 61,760건</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">입금부족률</span><span class="tip-panel">LR = Σ L<sub>i</sub> ÷ Σ A<sub>i</sub><span class="tip-row"><span>i</span><span class="tip-green">선정산일이 오늘 기준 20일 전 ~ 11일 전 · 3,200건</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">예상 연환산 수익률</span><span class="tip-panel">Y<sub>r</sub> = r × 365 ÷ D<span class="tip-row"><span>r</span><span class="tip-green">0.11%</span></span><span class="tip-row"><span>D</span><span class="tip-green">3.04일</span></span><span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></th>
               <th class="num">비중</th>
               <th>보관</th>
             </tr>
@@ -215,9 +215,9 @@
             <tr>
               <th>가맹점</th>
               <th class="num">투자실행액 (원)</th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">가중평균 금융일수</span><span class="tip-panel">보유 채권 전체<span class="tip-row"><span>채권 건수</span><span class="tip-green">61,760건</span></span></span></span></th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">입금부족률</span><span class="tip-panel">선정산일이 오늘 기준 20일 전 ~ 11일 전인 표본<span class="tip-row"><span>채권 건수</span><span class="tip-green">3,200건</span></span></span></span></th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">예상 연환산 수익률</span><span class="tip-panel">Y<sub>r</sub> · 예상 연환산 수익률 · r × 365 ÷ D<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">가중평균 금융일수</span><span class="tip-panel">D = Σ( A<sub>i</sub> × D<sub>i</sub> ) ÷ Σ A<sub>i</sub><span class="tip-row"><span>i</span><span class="tip-green">보유 채권 전체 · 61,760건</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">입금부족률</span><span class="tip-panel">LR = Σ L<sub>i</sub> ÷ Σ A<sub>i</sub><span class="tip-row"><span>i</span><span class="tip-green">선정산일이 오늘 기준 20일 전 ~ 11일 전 · 3,200건</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">예상 연환산 수익률</span><span class="tip-panel">Y<sub>r</sub> = r × 365 ÷ D<span class="tip-row"><span>r</span><span class="tip-green">0.11%</span></span><span class="tip-row"><span>D</span><span class="tip-green">3.04일</span></span><span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></th>
               <th class="num">비중</th>
             </tr>
           </thead>
diff --git a/invest-profit--empty.html b/invest-profit--empty.html
index 92b92fe..767dfb1 100644
--- a/invest-profit--empty.html
+++ b/invest-profit--empty.html
@@ -173,11 +173,11 @@
           <div class="summary-label">연환산 수익률</div>
           <div class="ty-split">
             <div>
-              <div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자실행금액 대비</span><span class="tip-panel">PY<sub>a</sub> · 투자실행금액 대비 연환산 수익률 · PMR × 365 ÷ PD<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span><span class="tip-row"><span>PMR</span><span class="tip-green">기간 투자수익율 · PM ÷ PA = 0%</span></span><span class="tip-row"><span>PM</span><span class="tip-green">기간 투자수익 · 0원</span></span><span class="tip-row"><span>PA</span><span class="tip-green">기간 투자실행금 · 0원</span></span><span class="tip-row"><span>PD</span><span class="tip-green">기간 가중평균 금융일수 · 0일</span></span></span></span></div>
+              <div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자실행금액 대비</span><span class="tip-panel">PY<sub>a</sub> = PMR × 365 ÷ PD<span class="tip-row"><span>PMR</span><span class="tip-green">0.000000%</span></span><span class="tip-row"><span>PM</span><span class="tip-green">0원</span></span><span class="tip-row"><span>PA</span><span class="tip-green">0원</span></span><span class="tip-row"><span>PD</span><span class="tip-green">0.00일</span></span><span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></div>
               <div class="summary-value">0.00<span class="unit">%</span></div>
             </div>
             <div>
-              <div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자 자산 대비</span><span class="tip-panel">PY<sub>t</sub> · 투자 자산 대비 연환산 수익률 · PM × 365 ÷ ( Σ( A<sub>i</sub> × D<sub>i</sub> ) + PEC )<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span><span class="tip-row"><span>PY<sub>a</sub></span><span class="tip-green">투자실행금액 대비 연환산 수익률 · 0%</span></span><span class="tip-row"><span>Σ( A<sub>i</sub> × D<sub>i</sub> )</span><span class="tip-green">0원</span></span><span class="tip-row"><span>PEC</span><span class="tip-green">검색대상기간의 누적 순현금 · 0원</span></span><span class="tip-row sum"><span>EC</span><span>순현금 · 20,000,000원 × 0일</span></span></span></span></div>
+              <div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자 자산 대비</span><span class="tip-panel">PY<sub>t</sub> = PY<sub>a</sub> × 채권 비중 + 순현금 수익률 × 순현금 비중<br>= PM × 365 ÷ ( Σ( A<sub>i</sub> × D<sub>i</sub> ) + PEC )<span class="tip-row"><span>PY<sub>a</sub></span><span class="tip-green">0.00%</span></span><span class="tip-row"><span>Σ( A<sub>i</sub> × D<sub>i</sub> )</span><span class="tip-green">0원</span></span><span class="tip-row"><span>PEC</span><span class="tip-green">0원</span></span><span class="tip-row sum"><span>EC</span><span>20,000,000원 × 0일</span></span><span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></div>
               <div class="summary-value">0.00<span class="unit">%</span></div>
             </div>
           </div>
@@ -202,10 +202,10 @@
             <tr>
               <th>정산예정일</th>
               <th class="num">상환액</th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">투자실행금</span><span class="tip-panel">PA · 투자실행금 · Σ A<sub>i</sub><span class="tip-row"><span>행</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">투자실행금</span><span class="tip-panel">PA = Σ A<sub>i</sub><span class="tip-row"><span>i</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span></span></span></th>
               <th class="num">투자 수익</th>
               <th class="num">가중평균 금융일수</th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">연환산 수익률</span><span class="tip-panel">PY<sub>a</sub> · 연환산 수익률 · PMR × 365 ÷ PD<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span><span class="tip-row"><span>행</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">연환산 수익률</span><span class="tip-panel">PY<sub>a</sub> = PMR × 365 ÷ PD<span class="tip-row"><span>i</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span><span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></th>
             </tr>
           </thead>
           <tbody>
diff --git a/invest-profit--monthly.html b/invest-profit--monthly.html
index 7531ac6..83819bc 100644
--- a/invest-profit--monthly.html
+++ b/invest-profit--monthly.html
@@ -173,11 +173,11 @@
           <div class="summary-label">연환산 수익률</div>
           <div class="ty-split">
             <div>
-              <div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자실행금액 대비</span><span class="tip-panel">PY<sub>a</sub> · 투자실행금액 대비 연환산 수익률 · PMR × 365 ÷ PD<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span><span class="tip-row"><span>PMR</span><span class="tip-green">기간 투자수익율 · PM ÷ PA = 0.038026%</span></span><span class="tip-row"><span>PM</span><span class="tip-green">기간 투자수익 · 1,787,417원</span></span><span class="tip-row"><span>PA</span><span class="tip-green">기간 투자실행금 · 4,700,503,303원</span></span><span class="tip-row"><span>PD</span><span class="tip-green">기간 가중평균 금융일수 · 3.03일</span></span></span></span></div>
+              <div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자실행금액 대비</span><span class="tip-panel">PY<sub>a</sub> = PMR × 365 ÷ PD<span class="tip-row"><span>PMR</span><span class="tip-green">0.038026%</span></span><span class="tip-row"><span>PM</span><span class="tip-green">1,787,417원</span></span><span class="tip-row"><span>PA</span><span class="tip-green">4,700,503,303원</span></span><span class="tip-row"><span>PD</span><span class="tip-green">3.03일</span></span><span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></div>
               <div class="summary-value">4.57<span class="unit">%</span></div>
             </div>
             <div>
-              <div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자 자산 대비</span><span class="tip-panel">PY<sub>t</sub> · 투자 자산 대비 연환산 수익률 · PM × 365 ÷ ( Σ( A<sub>i</sub> × D<sub>i</sub> ) + PEC )<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span><span class="tip-row"><span>PY<sub>a</sub></span><span class="tip-green">투자실행금액 대비 연환산 수익률 · 4.57%</span></span><span class="tip-row"><span>Σ( A<sub>i</sub> × D<sub>i</sub> )</span><span class="tip-green">14,262,370,838원</span></span><span class="tip-row"><span>PEC</span><span class="tip-green">검색대상기간의 누적 순현금 · 3,600,000,000원</span></span><span class="tip-row sum"><span>EC</span><span>순현금 · 20,000,000원 × 180일</span></span></span></span></div>
+              <div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자 자산 대비</span><span class="tip-panel">PY<sub>t</sub> = PY<sub>a</sub> × 채권 비중 + 순현금 수익률 × 순현금 비중<br>= PM × 365 ÷ ( Σ( A<sub>i</sub> × D<sub>i</sub> ) + PEC )<span class="tip-row"><span>PY<sub>a</sub></span><span class="tip-green">4.57%</span></span><span class="tip-row"><span>Σ( A<sub>i</sub> × D<sub>i</sub> )</span><span class="tip-green">14,262,370,838원</span></span><span class="tip-row"><span>PEC</span><span class="tip-green">3,600,000,000원</span></span><span class="tip-row sum"><span>EC</span><span>20,000,000원 × 180일</span></span><span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></div>
               <div class="summary-value">3.65<span class="unit">%</span></div>
             </div>
           </div>
@@ -202,10 +202,10 @@
             <tr>
               <th>정산예정월</th>
               <th class="num">상환액</th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">투자실행금</span><span class="tip-panel">PA · 투자실행금 · Σ A<sub>i</sub><span class="tip-row"><span>행</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">투자실행금</span><span class="tip-panel">PA = Σ A<sub>i</sub><span class="tip-row"><span>i</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span></span></span></th>
               <th class="num">투자 수익</th>
               <th class="num">가중평균 금융일수</th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">연환산 수익률</span><span class="tip-panel">PY<sub>a</sub> · 연환산 수익률 · PMR × 365 ÷ PD<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span><span class="tip-row"><span>행</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">연환산 수익률</span><span class="tip-panel">PY<sub>a</sub> = PMR × 365 ÷ PD<span class="tip-row"><span>i</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span><span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></th>
             </tr>
           </thead>
           <tbody>
diff --git a/invest-profit--weekly.html b/invest-profit--weekly.html
index 8e1e35a..18fd582 100644
--- a/invest-profit--weekly.html
+++ b/invest-profit--weekly.html
@@ -173,11 +173,11 @@
           <div class="summary-label">연환산 수익률</div>
           <div class="ty-split">
             <div>
-              <div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자실행금액 대비</span><span class="tip-panel">PY<sub>a</sub> · 투자실행금액 대비 연환산 수익률 · PMR × 365 ÷ PD<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span><span class="tip-row"><span>PMR</span><span class="tip-green">기간 투자수익율 · PM ÷ PA = 0.038323%</span></span><span class="tip-row"><span>PM</span><span class="tip-green">기간 투자수익 · 248,681원</span></span><span class="tip-row"><span>PA</span><span class="tip-green">기간 투자실행금 · 648,903,503원</span></span><span class="tip-row"><span>PD</span><span class="tip-green">기간 가중평균 금융일수 · 3.03일</span></span></span></span></div>
+              <div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자실행금액 대비</span><span class="tip-panel">PY<sub>a</sub> = PMR × 365 ÷ PD<span class="tip-row"><span>PMR</span><span class="tip-green">0.038323%</span></span><span class="tip-row"><span>PM</span><span class="tip-green">248,681원</span></span><span class="tip-row"><span>PA</span><span class="tip-green">648,903,503원</span></span><span class="tip-row"><span>PD</span><span class="tip-green">3.03일</span></span><span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></div>
               <div class="summary-value">4.62<span class="unit">%</span></div>
             </div>
             <div>
-              <div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자 자산 대비</span><span class="tip-panel">PY<sub>t</sub> · 투자 자산 대비 연환산 수익률 · PM × 365 ÷ ( Σ( A<sub>i</sub> × D<sub>i</sub> ) + PEC )<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span><span class="tip-row"><span>PY<sub>a</sub></span><span class="tip-green">투자실행금액 대비 연환산 수익률 · 4.62%</span></span><span class="tip-row"><span>Σ( A<sub>i</sub> × D<sub>i</sub> )</span><span class="tip-green">1,965,572,846원</span></span><span class="tip-row"><span>PEC</span><span class="tip-green">검색대상기간의 누적 순현금 · 500,000,000원</span></span><span class="tip-row sum"><span>EC</span><span>순현금 · 20,000,000원 × 25일</span></span></span></span></div>
+              <div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자 자산 대비</span><span class="tip-panel">PY<sub>t</sub> = PY<sub>a</sub> × 채권 비중 + 순현금 수익률 × 순현금 비중<br>= PM × 365 ÷ ( Σ( A<sub>i</sub> × D<sub>i</sub> ) + PEC )<span class="tip-row"><span>PY<sub>a</sub></span><span class="tip-green">4.62%</span></span><span class="tip-row"><span>Σ( A<sub>i</sub> × D<sub>i</sub> )</span><span class="tip-green">1,965,572,846원</span></span><span class="tip-row"><span>PEC</span><span class="tip-green">500,000,000원</span></span><span class="tip-row sum"><span>EC</span><span>20,000,000원 × 25일</span></span><span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></div>
               <div class="summary-value">3.68<span class="unit">%</span></div>
             </div>
           </div>
@@ -202,10 +202,10 @@
             <tr>
               <th>정산예정주</th>
               <th class="num">상환액</th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">투자실행금</span><span class="tip-panel">PA · 투자실행금 · Σ A<sub>i</sub><span class="tip-row"><span>행</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">투자실행금</span><span class="tip-panel">PA = Σ A<sub>i</sub><span class="tip-row"><span>i</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span></span></span></th>
               <th class="num">투자 수익</th>
               <th class="num">가중평균 금융일수</th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">연환산 수익률</span><span class="tip-panel">PY<sub>a</sub> · 연환산 수익률 · PMR × 365 ÷ PD<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span><span class="tip-row"><span>행</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">연환산 수익률</span><span class="tip-panel">PY<sub>a</sub> = PMR × 365 ÷ PD<span class="tip-row"><span>i</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span><span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></th>
             </tr>
           </thead>
           <tbody>
diff --git a/invest-profit.html b/invest-profit.html
index 33ab59a..8fa1a24 100644
--- a/invest-profit.html
+++ b/invest-profit.html
@@ -167,11 +167,11 @@
           <div class="summary-label">연환산 수익률</div>
           <div class="ty-split">
             <div>
-              <div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자실행금액 대비</span><span class="tip-panel">PY<sub>a</sub> · 투자실행금액 대비 연환산 수익률 · PMR × 365 ÷ PD<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span><span class="tip-row"><span>PMR</span><span class="tip-green">기간 투자수익율 · PM ÷ PA = 0.033992%</span></span><span class="tip-row"><span>PM</span><span class="tip-green">기간 투자수익 · 61,175원</span></span><span class="tip-row"><span>PA</span><span class="tip-green">기간 투자실행금 · 179,970,919원</span></span><span class="tip-row"><span>PD</span><span class="tip-green">기간 가중평균 금융일수 · 3.11일</span></span></span></span></div>
+              <div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자실행금액 대비</span><span class="tip-panel">PY<sub>a</sub> = PMR × 365 ÷ PD<span class="tip-row"><span>PMR</span><span class="tip-green">0.033992%</span></span><span class="tip-row"><span>PM</span><span class="tip-green">61,175원</span></span><span class="tip-row"><span>PA</span><span class="tip-green">179,970,919원</span></span><span class="tip-row"><span>PD</span><span class="tip-green">3.11일</span></span><span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></div>
               <div class="summary-value">3.99<span class="unit">%</span></div>
             </div>
             <div>
-              <div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자 자산 대비</span><span class="tip-panel">PY<sub>t</sub> · 투자 자산 대비 연환산 수익률 · PM × 365 ÷ ( Σ( A<sub>i</sub> × D<sub>i</sub> ) + PEC )<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span><span class="tip-row"><span>PY<sub>a</sub></span><span class="tip-green">투자실행금액 대비 연환산 수익률 · 3.99%</span></span><span class="tip-row"><span>Σ( A<sub>i</sub> × D<sub>i</sub> )</span><span class="tip-green">559,275,516원</span></span><span class="tip-row"><span>PEC</span><span class="tip-green">검색대상기간의 누적 순현금 · 140,000,000원</span></span><span class="tip-row sum"><span>EC</span><span>순현금 · 20,000,000원 × 7일</span></span></span></span></div>
+              <div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자 자산 대비</span><span class="tip-panel">PY<sub>t</sub> = PY<sub>a</sub> × 채권 비중 + 순현금 수익률 × 순현금 비중<br>= PM × 365 ÷ ( Σ( A<sub>i</sub> × D<sub>i</sub> ) + PEC )<span class="tip-row"><span>PY<sub>a</sub></span><span class="tip-green">3.99%</span></span><span class="tip-row"><span>Σ( A<sub>i</sub> × D<sub>i</sub> )</span><span class="tip-green">559,275,516원</span></span><span class="tip-row"><span>PEC</span><span class="tip-green">140,000,000원</span></span><span class="tip-row sum"><span>EC</span><span>20,000,000원 × 7일</span></span><span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></div>
               <div class="summary-value">3.19<span class="unit">%</span></div>
             </div>
           </div>
@@ -196,10 +196,10 @@
             <tr>
               <th>정산예정일</th>
               <th class="num">상환액</th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">투자실행금</span><span class="tip-panel">PA · 투자실행금 · Σ A<sub>i</sub><span class="tip-row"><span>행</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">투자실행금</span><span class="tip-panel">PA = Σ A<sub>i</sub><span class="tip-row"><span>i</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span></span></span></th>
               <th class="num">투자 수익</th>
               <th class="num">가중평균 금융일수</th>
-              <th class="num"><span class="tooltip wide"><span class="tip-anchor">연환산 수익률</span><span class="tip-panel">PY<sub>a</sub> · 연환산 수익률 · PMR × 365 ÷ PD<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span><span class="tip-row"><span>행</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span></span></span></th>
+              <th class="num"><span class="tooltip wide"><span class="tip-anchor">연환산 수익률</span><span class="tip-panel">PY<sub>a</sub> = PMR × 365 ÷ PD<span class="tip-row"><span>i</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span><span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></th>
             </tr>
           </thead>
           <tbody>
diff --git a/invest-sim--result.html b/invest-sim--result.html
index e8f166d..40b17b0 100644
--- a/invest-sim--result.html
+++ b/invest-sim--result.html
@@ -369,11 +369,11 @@
           <div class="summary-label">연환산 수익률</div>
           <div class="ty-split">
             <div>
-              <div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자실행금액 대비</span><span class="tip-panel">PY<sub>a</sub> · 투자실행금액 대비 연환산 수익률 · PMR × 365 ÷ PD<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span><span class="tip-row"><span>PMR</span><span class="tip-green">기간 투자수익율 · PM ÷ PA = 0.040044%</span></span><span class="tip-row"><span>PM</span><span class="tip-green">기간 투자수익 · 16,000원</span></span><span class="tip-row"><span>PA</span><span class="tip-green">기간 투자실행금 · 39,956,000원</span></span><span class="tip-row"><span>PD</span><span class="tip-green">기간 가중평균 금융일수 · 3.04일</span></span></span></span></div>
+              <div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자실행금액 대비</span><span class="tip-panel">PY<sub>a</sub> = PMR × 365 ÷ PD<span class="tip-row"><span>PMR</span><span class="tip-green">0.040044%</span></span><span class="tip-row"><span>PM</span><span class="tip-green">16,000원</span></span><span class="tip-row"><span>PA</span><span class="tip-green">39,956,000원</span></span><span class="tip-row"><span>PD</span><span class="tip-green">3.04일</span></span><span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></div>
               <div class="summary-value">4.81<span class="unit">%</span></div>
             </div>
             <div>
-              <div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자 자산 대비</span><span class="tip-panel">PY<sub>t</sub> · 투자 자산 대비 연환산 수익률 · PM × 365 ÷ ( Σ( A<sub>i</sub> × D<sub>i</sub> ) + PEC )<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span><span class="tip-row"><span>PY<sub>a</sub></span><span class="tip-green">투자실행금액 대비 연환산 수익률 · 4.81%</span></span><span class="tip-row"><span>Σ( A<sub>i</sub> × D<sub>i</sub> )</span><span class="tip-green">121,466,240원</span></span><span class="tip-row"><span>PEC</span><span class="tip-green">검색대상기간의 누적 순현금 · 140,000,000원</span></span><span class="tip-row sum"><span>EC</span><span>순현금 · 20,000,000원 × 7일</span></span></span></span></div>
+              <div class="ty-label"><span class="tooltip wide"><span class="tip-anchor">투자 자산 대비</span><span class="tip-panel">PY<sub>t</sub> = PY<sub>a</sub> × 채권 비중 + 순현금 수익률 × 순현금 비중<br>= PM × 365 ÷ ( Σ( A<sub>i</sub> × D<sub>i</sub> ) + PEC )<span class="tip-row"><span>PY<sub>a</sub></span><span class="tip-green">4.81%</span></span><span class="tip-row"><span>Σ( A<sub>i</sub> × D<sub>i</sub> )</span><span class="tip-green">121,466,240원</span></span><span class="tip-row"><span>PEC</span><span class="tip-green">140,000,000원</span></span><span class="tip-row sum"><span>EC</span><span>20,000,000원 × 7일</span></span><span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></div>
               <div class="summary-value">2.23<span class="unit">%</span></div>
             </div>
           </div>
@@ -386,7 +386,7 @@
       <div class="tbl-scroll">
         <table class="tbl">
           <thead>
-            <tr><th>정산예정일</th><th class="num">상환액</th><th class="num"><span class="tooltip wide"><span class="tip-anchor">투자실행금</span><span class="tip-panel">PA · 투자실행금 · Σ A<sub>i</sub><span class="tip-row"><span>행</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span></span></span></th><th class="num">투자 수익</th><th class="num">가중평균 금융일수</th><th class="num"><span class="tooltip wide"><span class="tip-anchor">연환산 수익률</span><span class="tip-panel">PY<sub>a</sub> · 연환산 수익률 · PMR × 365 ÷ PD<span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span><span class="tip-row"><span>행</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span></span></span></th></tr>
+            <tr><th>정산예정일</th><th class="num">상환액</th><th class="num"><span class="tooltip wide"><span class="tip-anchor">투자실행금</span><span class="tip-panel">PA = Σ A<sub>i</sub><span class="tip-row"><span>i</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span></span></span></th><th class="num">투자 수익</th><th class="num">가중평균 금융일수</th><th class="num"><span class="tooltip wide"><span class="tip-anchor">연환산 수익률</span><span class="tip-panel">PY<sub>a</sub> = PMR × 365 ÷ PD<span class="tip-row"><span>i</span><span class="tip-green">정산예정일이 그 날짜인 보유 채권</span></span><span class="tip-row"><span>연환산</span><span class="tip-green">일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률</span></span></span></span></th></tr>
           </thead>
           <tbody>
             <tr><td class="mono">2026-08-24</td><td class="num">15,189,360</td><td class="num">15,183,280</td><td class="num"><span class="strong">6,080</span></td><td class="num">2.00</td><td class="num">7.31%</td></tr>
```

## 6. `_fig` 변경 파일

`prep_fig.py sync` · `freeze` 뒤 git 기준. 툴팁 글자가 바뀐 파일(Figma 교체 대상) 18:

- `payhug-spec/_pipeline/investor_admin/_fig/invest-assets--cert-confirm.html`
- `payhug-spec/_pipeline/investor_admin/_fig/invest-assets--download.html`
- `payhug-spec/_pipeline/investor_admin/_fig/invest-assets--empty.html`
- `payhug-spec/_pipeline/investor_admin/_fig/invest-assets--nav-collapsed.html`
- `payhug-spec/_pipeline/investor_admin/_fig/invest-assets--tip-exec.html`
- `payhug-spec/_pipeline/investor_admin/_fig/invest-assets--tip-shortfall.html`
- `payhug-spec/_pipeline/investor_admin/_fig/invest-assets--tip-wavg.html`
- `payhug-spec/_pipeline/investor_admin/_fig/invest-assets--tip-yield.html`
- `payhug-spec/_pipeline/investor_admin/_fig/invest-assets.html`
- `payhug-spec/_pipeline/investor_admin/_fig/invest-profit--empty.html`
- `payhug-spec/_pipeline/investor_admin/_fig/invest-profit--monthly.html`
- `payhug-spec/_pipeline/investor_admin/_fig/invest-profit--range-error.html`
- `payhug-spec/_pipeline/investor_admin/_fig/invest-profit--tip-exec.html`
- `payhug-spec/_pipeline/investor_admin/_fig/invest-profit--tip-py-asset.html`
- `payhug-spec/_pipeline/investor_admin/_fig/invest-profit--tip-py-exec.html`
- `payhug-spec/_pipeline/investor_admin/_fig/invest-profit--tip-yield.html`
- `payhug-spec/_pipeline/investor_admin/_fig/invest-profit--weekly.html`
- `payhug-spec/_pipeline/investor_admin/_fig/invest-profit.html`

툴팁과 무관하게 바뀐 파일 19 — 커밋된 `_fig` 판에는 `mcp.figma.com/…/capture.js` 스크립트와 `data-fig-input` 스팬(캡처 단계 패치)이 들어 있었고 `sync` 가 원본 낱장으로 되돌린 것. 이번 작업의 산출이 아니다:

- `payhug-spec/_pipeline/investor_admin/_fig/acquisition--after-sign.html`
- `payhug-spec/_pipeline/investor_admin/_fig/acquisition--confirm.html`
- `payhug-spec/_pipeline/investor_admin/_fig/acquisition--doc.html`
- `payhug-spec/_pipeline/investor_admin/_fig/acquisition--done.html`
- `payhug-spec/_pipeline/investor_admin/_fig/acquisition--selected.html`
- `payhug-spec/_pipeline/investor_admin/_fig/acquisition--signing.html`
- `payhug-spec/_pipeline/investor_admin/_fig/acquisition.html`
- `payhug-spec/_pipeline/investor_admin/_fig/certificate.html`
- `payhug-spec/_pipeline/investor_admin/_fig/contracts--all.html`
- `payhug-spec/_pipeline/investor_admin/_fig/contracts--empty.html`
- `payhug-spec/_pipeline/investor_admin/_fig/contracts.html`
- `payhug-spec/_pipeline/investor_admin/_fig/merchants--empty.html`
- `payhug-spec/_pipeline/investor_admin/_fig/merchants--filtered.html`
- `payhug-spec/_pipeline/investor_admin/_fig/merchants.html`
- `payhug-spec/_pipeline/investor_admin/_fig/password--done.html`
- `payhug-spec/_pipeline/investor_admin/_fig/password--error.html`
- `payhug-spec/_pipeline/investor_admin/_fig/password--valid.html`
- `payhug-spec/_pipeline/investor_admin/_fig/password--weak.html`
- `payhug-spec/_pipeline/investor_admin/_fig/password.html`

## 7. 발견했으나 고치지 않은 것 · 지시와 다르게 한 것

| 항목 | 내용 |
|---|---|
| 빈 상태 낱장 ④⑤ 값 표기 (다르게 한 것) | `invest-profit--empty.html` 툴팁이 옛 판부터 `PMR 0%` · `PD 0일` · `PYa 0%` 로 나와 같은 카드의 `0.00%` 와 달랐다(통합본 빈 상태는 `0.000000%` · `0.00일` · `0.00%`). `sync_profit_static.py` 빈 상태 호출에서 0 을 통합본과 같은 자리수로 넣어 맞췄다(2절 마지막 두 줄). 값 자체는 0 그대로 |
| `verify_crossscreen.py` 용어 해설 FAIL 3건 | `glossary.html` duration 허용 블록 검사(「duration 허용 블록 = 1곳」 got 0 · 「허용 블록 밖 만기」 got [만기] · 「허용 블록 밖 duration」 got 2). HEAD 에서도 같은 결과. 범위 밖이라 두었다 |
| 낱장 「투자실행액」 카드 툴팁 | 낱장 4장에 앵커가 없다(통합본에만 있음). 지시대로 추가하지 않았다 |
| `app.html` JS 주석의 옛 낱말 | 2319줄 「PMR = 기간 투자수익 / 기간 투자실행금」, 2350줄 「ad 의 합」 — 코드 주석이라 화면에 나오지 않아 두었다 |
| `shot_rects.json` | `capture_shots.js` 가 `capturedAt` · mtime · srcSha256 를 다시 찍어 diff 가 생겼다(그림 바이트 동일) |
| 시연본 레포 `payhug-investor-prototype` | `sync_prototype.sh --dry-run` 이 `index.html` 을 다시 써서 워킹트리에 `M index.html` 이 남아 있다(커밋·push 안 함) |
| 툴팁 EC 행 클래스 | `tip-row sum`(위 구분선) 을 지시대로 그대로 두어, ⑤ 툴팁은 EC 행 아래 연환산 행이 구분선 밑에 놓인다(`app-profit-F-py-asset.png`) |
| `capture_shots.js` 실행 시점 | 빈 상태 낱장 0 자리수 수정 전에 찍었다. 그 뒤 바뀐 파일은 `invest-profit--empty.html` 뿐이고 5장 촬영 대상(`invest-assets` · `invest-profit` · `merchants` · `contracts` · `coocon`)이 아니며 `app.html` 은 그대로라 다시 찍지 않았다 |
