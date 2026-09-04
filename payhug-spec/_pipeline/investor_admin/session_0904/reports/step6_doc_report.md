# 기호 정리표 확정본 — 적용 보고

## 못 맞춘 것 · 지시와 다르게 처리한 것

| # | 항목 | 내용 |
|---|---|---|
| 1 | **검사기 136/136 유지 실패 — 133/136 · FAIL 3건 (A10 · I16 · I17)** | 세 판정 모두 원고가 아니라 **원장·화면**을 견줍니다. `ledger_facts.json:53` `weekTyAsset "2.32"` 와 `payhug-investor-admin/invest-profit.html:174` 의 ⑤ 2.32%·툴팁 `( PY_a × PA ) ÷ ( PA + PEC )` 가 옛 산식 그대로입니다. 원천은 `daily_ledger.py:181` `TY5_EXPR = 'ty4 * psa / tot'` 한 줄(주석 「새 산식이 오면 이 한 줄만 고친다」)이며, 고치면 `ty_asset()` 에 PD 인자가 필요하고 `ledger_facts.json` → `build_app.py` → 정적 낱장 재생성이 따라옵니다. 이 조 범위 밖이라 손대지 않았고, 세 판정을 느슨하게 만들지도 않았습니다. 원장·화면이 새 산식으로 바뀌면 그대로 통과합니다 |
| 2 | 표식 | **0건**을 택했습니다. 확정본이고 산출물 이력체 금지 규칙에 따라 낱말 단위 「이번에 바뀜」 표식을 두지 않았습니다. `.new{}` CSS 도 넣지 않았습니다. 표 3 「⑤ 분모」 행의 기존·개선 기호만 다른 행과 같은 `sym old`·`sym new` 입니다 |
| 3 | 목록 밖에 손댄 자리 (`final_terms.json`) | ① `rules[1].body` 가 인용하는 ⑤ 산식 조각 `× PA ÷ (PA+PEC)` → `× PA × PD ÷ ( PA × PD + PEC )` — 같은 원고 안 산식 인용이라 맞췄습니다. ② `calc.검산[2]` 문면을 `PY_t = 7,429,796 ÷ ( PA + PEC ÷ PD )` 로 — 4번째 줄 「같은 분자를 다른 분모로 나눈 것이다」(D4 판정) 를 그대로 유지하려고 분모를 원으로 되돌린 꼴입니다 (= 7,429,796 × PD ÷ (PA × PD + PEC) 와 같은 값 3.299662%). ③ `calc.steps[7]` 라벨에 `PA × PD = Σ( A_i × D_i ) = 556,626,436` 을 붙였습니다 |
| 4 | 띄어쓰기 두 벌 | 표 1 의미 칸은 지시 문구 그대로 「연환산 예상 수익률」·「연환산 수익률」, 표 2·3 은 기존 「연환산수익률」입니다. 한 문서 안에 두 표기가 섭니다 |
| 5 | 다른 산출물 미반영 | `final_terms.json` 을 읽는 용어기호정리 워드·HTML(`build_final.py`), `glossary.html`(`build_glossary.py:593` 「유동화투자자의 할인율」), `build_calc.py:109`·`testcase_table.py:221·233·318` 의 옛 ⑤·PA 산식 문자열은 이번 범위 밖이라 그대로입니다 |

## (가) 아티팩트 `ceo_review.html` 고친 줄

백업 `ceo_review.prev3.html`. 줄 번호는 「옛 → 새」.

| # | 줄 | 옛 | 새 |
|---|---|---|---|
| 6 | 80 뒤 → 81–82 (신설) | 없음 | `<tr><td>접두 <span class="sym">Y</span></td><td>연환산을 뜻한다</td>` / `<td><span class="sym">Y<sub>r</sub></span> <span class="sym">PY<sub>a</sub></span> <span class="sym">PY<sub>t</sub></span></td></tr>` |
| 1 | 86 → 88 | `예상 연환산수익률을 나타낼 때 쓴다` | `예상 수익률을 나타낼 때 쓴다. Y<sub>r</sub> 는 연환산 예상 수익률 (Y 가 연환산을 뜻하므로)` |
| 2 | 88 → 90 | `투자실행금 기준 연환산수익률을 나타낼 때 쓴다` | `투자실행금 기준 관찰된 값을 나타낼 때 쓴다. PY<sub>a</sub> 는 조회기간에서 관찰된 투자실행금 기준 연환산 수익률 (P 는 조회기간)` |
| 3 | 90 → 92 | `투자자산 기준 연환산수익률을 나타낼 때 쓴다` | `투자자산 기준 관찰된 값을 나타낼 때 쓴다. PY<sub>t</sub> 는 조회기간에서 관찰된 투자자산 기준 연환산 수익률` |
| 4 | 102 → 104 | `유동화투자자의 할인율` | `계약된 할인율` |
| 5 | 110 → 112 | `입금부족` | `입금부족액` |
| 6 | 112 (삭제) | `<tr><td></td><td><span class="sym">Y</span></td><td></td><td>연환산수익률</td><td></td></tr>` | 없음 |
| 8 | 130 → 131 | `d 시점 쿠콘 가상계좌의 현금 잔액` | `d 마감시점 쿠콘 가상계좌의 현금 잔액` |
| 9 | 132 → 133 | `Σ A<sub>i</sub> + EC<br>i 는 정산예정일이 d 보다 뒤인 채권` | `Σ A<sub>i</sub> + EC<br>i 는 정산예정일이 d 보다 뒤인 대상정산금채권` |
| 11 | 142 → 143 | `PA = Σ A<sub>i</sub><br>i 는 정산예정일이 P 안에 든 채권` | `PA = Σ A<sub>i</sub> &nbsp; i ∈ P` |
| 12 | 144·146 | 변경 0건 (`PM = Σ M<sub>i</sub> &nbsp; i ∈ P` · `PB = Σ B<sub>i</sub> &nbsp; i ∈ P`) | 그대로 |
| ⑤ | 159 → 160 | `PY<sub>t</sub> = PY<sub>a</sub> × PA ÷ (PA + PEC)` | `PY<sub>t</sub> = PY<sub>a</sub> × PA × PD ÷ ( PA × PD + PEC )<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;= PM × 365 ÷ ( PA × PD + PEC )` (기존 칸 `wPY<sub>MR</sub>` 그대로) |
| 13 | 183 → 184 | `연환산수익률 기호 변경` | `관찰된 연환산수익률 기호 변경` |
| ⑤ | 185 뒤 → 187–189 (신설) | 없음 | `<tr><td>⑤ 분모</td>` / `<td><span class="sym old">PA + PEC</span></td>` / `<td><span class="sym new">PA × PD + PEC</span> PEC 는 P 안 각 날의 EC 를 더한 값이라 원·일이고, PA 는 채권마다 한 번 더한 값이라 원이다. PA × PD 가 채권이 묶여 있던 원·일</td></tr>` |

7번(Σ A<sub>i</sub> 「조회대상기간 중 누계」)·10번(D 「표본에 속하는」)·128줄(Σ A<sub>i</sub> 행 「채권」)·137줄(LR)·153줄(PEC) 은 손대지 않았습니다. 파일 188줄 → 192줄.

## (나) `final_terms.json` 고친 키

| 키 | 옛 | 새 |
|---|---|---|
| `vars[1].term` (r) | 유동화투자자의 할인율 | 계약된 할인율 |
| `vars[6].term` (L) | 입금부족 | 입금부족액 |
| `vars[8].term` (Y · 개념 · 삭제 안 함) | 연환산수익률 | 연환산 |
| `vars[8].plain` | 수익률을 1년으로 늘려 잰 값이다. 산식에는 할인율로 잰 예상치가 `Y_r` 로, 정산예정일이 조회기간에 든 채권들의 것이 `PY_a` 로, 그 값의 분모에 순현금을 더한 것이 `PY_t` 로 나온다. | 값이 아니라 수익률을 1년으로 늘려 잰다는 표시다. P 처럼 기호 앞에 선다. 할인율로 잰 예상치가 `Y_r` 로, 조회기간에서 관찰된 투자실행금 기준 값이 `PY_a` 로, 투자자산 기준 값이 `PY_t` 로 나온다. |
| `vars[17].plain` (EC) 첫 문장 | 채권으로 나가지 않고 쿠콘 가상계좌에 남아 있는 현금이다. | 기준일 마감시점에 채권으로 나가지 않고 쿠콘 가상계좌에 남아 있는 현금이다. (20,000,000 · 140,000,000 · `PEC` 유지) |
| `vars[21].formula` (PA) | `PA = ( Σ PA )      기간 안 레코드 전부` | `PA = Σ A_i      i ∈ P` |
| `vars[22].formula` (PB) | `PB = ( Σ PB )` | `PB = Σ B_i      i ∈ P` |
| `vars[23].formula` (PM) | `PM = ( Σ PM )` | `PM = Σ M_i      i ∈ P` |
| `vars[28].formula` (PY_t) | `PY_t = PY_a × PA ÷ (PA + PEC)` | `PY_t = PY_a × PA × PD ÷ ( PA × PD + PEC ) = PM × 365 ÷ ( PA × PD + PEC )` (한 줄 — 생성기가 formula 를 한 문단으로 조판) |
| `rules[1].body` 인용 조각 | `` `PY_t` 은 `× PA ÷ (PA+PEC)` 가 있다 `` | `` `PY_t` 은 `× PA × PD ÷ ( PA × PD + PEC )` 가 있다 `` |
| `calc.steps[7]` | `④ 투자실행금 비중 = PA ÷ (PA + PEC)` · `0.562386` | `④ 투자실행금 비중 = PA × PD ÷ (PA × PD + PEC)   PA × PD = Σ( A_i × D_i ) = 556,626,436` · `0.799031` |
| `calc.steps[8]` | `⑤ PY_t = ③ × PA ÷ (PA + PEC)` · `2.322416%   화면 2.32%` | `⑤ PY_t = ③ × PA × PD ÷ (PA × PD + PEC)` · `3.299662%   화면 3.30%` |
| `calc.검산[2]` | `PY_t = 7,429,796 ÷ (PA + PEC)` · `2.322416%` | `PY_t = 7,429,796 ÷ ( PA + PEC ÷ PD )` · `3.299662%` |

값 근거 (원장 재계산): Σ(A_i × D_i) **556,626,436** 원·일 · PEC 140,000,000 · 비중 556,626,436 ÷ 696,626,436 = **0.799031** · ⑤ = 4.129577% × 556,626,436 ÷ 696,626,436 = **3.299662%** → 3.30%. ④ 표기 0.799031 로 끊어 가면 3.299660%, PA × PD(3.093802) 표기로 가면 556,626,469.95 원·일 → 3.299662% 로 같습니다. 검산 7,429,796 ÷ (PA + PEC ÷ PD) = 7,429,796 ÷ 225,168,408 = 3.299662%.

`vars[18]`(Σ A_i + EC) 는 「대상정산금채권」이 이미 있어 그대로. json 은 `indent=2` 왕복이 원문과 동일해 다른 자리는 바이트 단위로 같습니다.

## (다) 검사기 `verify_final_terms.py`

| 항목 | 결과 |
|---|---|
| 판정 | **133 / 136** · FAIL `A10` `I16` `I17` (위 1번) |
| 자기시험 J | 7 / 7 통과 · J3 원고 md5 무변조 |
| 판정 완화 | 0건 |

고친 자리

| 자리 | 옛 | 새 |
|---|---|---|
| 정의 (`PEC` 아래) | 없음 | `SAD = Σ A_i × D_i` (조회기간 채권 단위 · 끊는 자리 없음) |
| `SHARE` · `WPYMR_DAY` · `WPYMR_2DP` · `WPYMR_REC` | `× PA ÷ (PA + PEC)` | `× SAD ÷ (SAD + PEC)` |
| A10 제목 | `PY_MR · wPY_MR 재계산 표기 = …` | `PY_a · PY_t 재계산 표기 = …` (판정식 그대로) |
| B9 · B10 제목 | `④ PA ÷ (PA + PEC)` · `⑤ wPY_MR` | `④ PA × PD ÷ (PA × PD + PEC)` · `⑤ PY_t` |
| C3 | `③표기 × PA ÷ (PA + PEC)` | `③표기 × SAD ÷ (SAD + PEC)` · 부가 표시에 PA × PD 표기 경로 값 |
| C5 | 같은 분모 교체 | `× SAD ÷ (SAD + PEC)` |
| D3 · D4 | `ann ÷ (PA + PEC)` | `ann ÷ (PA + PEC × PA ÷ SAD)` = ann ÷ (PA + PEC ÷ PD) · 제목 `검산 PY_t = 연환산수익금 ÷ (PA + PEC ÷ PD)` |
| I17 제목 | `원고 PwD 산식(여섯 자리)으로 계산한 값` | `원고 산식 PY_a × PA × PD ÷ (PA × PD + PEC) 로 계산한 값` (판정식 그대로) |

FAIL 3건 실측

| 판정 | 실측 |
|---|---|
| A10 | `4.129577% → 4.13% ↔ 4.13%  ·  3.299662% → 3.30% ↔ 2.32%` |
| I16 | `2.32% ↔ 3.30` |
| I17 | `화면 2.32% ↔ 원고산식 3.30 (두 자리로 끊으면 3.30)` |

## (라) 산출 파일

| 구분 | 경로 |
|---|---|
| 아티팩트 (갱신) | `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/ceo_review.html` |
| 아티팩트 백업 | `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/ceo_review.prev3.html` |
| 원고 | `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/final_terms.json` |
| 검사기 | `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_final_terms.py` |
| 워드 (신규) | `/Users/semi/Downloads/payhug_용어정의서/기호정리표_20260904_2126.docx` (40KB) |
| HTML (신규) | `/Users/semi/Downloads/payhug_용어정의서/기호정리표_20260904_2126.html` (13KB) |
| 이전판 이동 | `/Users/semi/Downloads/payhug_용어정의서/이전판/기호정리표_20260903_2329.docx` · `/Users/semi/Downloads/payhug_용어정의서/이전판/기호정리표_20260903_2329.html` |
| 보고서 | `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/step6_doc_report.md` |

생성기 `build_symreview.py` 는 손대지 않았습니다 (`SYMREVIEW_STAMP=20260904_2126` 로 실행 · 블록 h1 1 · h2 3 · table 3 · note 1). HTML 산출은 아티팩트 `<div class="wrap">` 이하와 본문이 같습니다 (끝 빈 줄 하나만 차이).

## (마) 워드 내용 확인 (python-docx)

| 항목 | 실측 |
|---|---|
| 표 수 | **3** |
| 표 1 이름 짓는 규칙 | 8행 (머리 1 + 본문 7: 접두 P · 접두 Y · 아래첨자 · 첨자 i · r · a · t) · 3열 |
| 표 2 전체 기호 | 29행 (머리 1 + 본문 28 · Y 단독 행 없음) · 5열 |
| 표 3 기호 변경내역 | 6행 (머리 1 + 본문 5: w 삭제 · d−1 제거 · d 재정의 · 관찰된 연환산수익률 기호 변경 · ⑤ 분모) · 3열 |

채택 문구 (표 · 본문 행 · 열)

| # | 문구 | 자리 |
|---|---|---|
| 1 | 예상 수익률을 나타낼 때 쓴다. Y<sub>r</sub> 는 연환산 예상 수익률 (Y 가 연환산을 뜻하므로) | 표1 5행 의미 |
| 2 | 투자실행금 기준 관찰된 값을 나타낼 때 쓴다. PY<sub>a</sub> 는 조회기간에서 관찰된 투자실행금 기준 연환산 수익률 (P 는 조회기간) | 표1 6행 의미 |
| 3 | 투자자산 기준 관찰된 값을 나타낼 때 쓴다. PY<sub>t</sub> 는 조회기간에서 관찰된 투자자산 기준 연환산 수익률 | 표1 7행 의미 |
| 4 | 계약된 할인율 | 표2 2행 용어 이름 |
| 5 | L · 입금부족액 | 표2 7행 |
| 6 | 접두 Y · 연환산을 뜻한다 · Y<sub>r</sub> PY<sub>a</sub> PY<sub>t</sub> | 표1 2행 · 표2 Y 단독 행 0건 |
| 8 | d 마감시점 쿠콘 가상계좌의 현금 잔액 | 표2 16행 산식 |
| 9 | Σ A<sub>i</sub> + EC ⏎ i 는 정산예정일이 d 보다 뒤인 대상정산금채권 | 표2 17행 산식 |
| 11 | PA = Σ A<sub>i</sub> ␣ i ∈ P | 표2 21행 산식 |
| 12 | PM = Σ M<sub>i</sub> ␣ i ∈ P · PB = Σ B<sub>i</sub> ␣ i ∈ P | 표2 22·23행 (변경 0건) |
| 13 | 관찰된 연환산수익률 기호 변경 | 표3 4행 변경점 |
| ⑤ 산식 1줄 | PY<sub>t</sub> = PY<sub>a</sub> × PA × PD ÷ ( PA × PD + PEC ) | 표2 28행 산식 |
| ⑤ 산식 2줄 | ⏎ ␣␣␣␣␣= PM × 365 ÷ ( PA × PD + PEC ) | 표2 28행 산식 (줄바꿈 + 아래첨자 run 확인) |
| ⑤ 기존 칸 | wPY<sub>MR</sub> | 표2 28행 기존 |
| 표3 ⑤ 분모 | PA + PEC → PA × PD + PEC · PEC 는 P 안 각 날의 EC 를 더한 값이라 원·일이고, PA 는 채권마다 한 번 더한 값이라 원이다. PA × PD 가 채권이 묶여 있던 원·일 | 표3 5행 |

옛 문구 잔존 0건: 「유동화투자자의 할인율」 「d 시점 쿠콘」 「PA ÷ (PA + PEC)」 「예상 연환산수익률을 나타낼」 「i 는 정산예정일이 P 안에 든 채권」.

run 색: 파랑 2C4470 **19** (개선 기호 · 「PA × PD + PEC」 포함) · 빨강 A63D2F **33** (기존 기호 · 「PA + PEC」 포함) · 회색 6E6A63 11 · 낱말 표식 `class="new"` 0건.
