# 기호 정리표 산식 표기 통일 — 적용 보고

## 하지 않은 것 · 지시와 다르게 처리한 것

| # | 항목 | 내용 |
|---|---|---|
| 1 | **`calc.검산[2]` 를 지시 문면 `PM × 365 ÷ ( Σ( A_i × D_i ) + PEC ) = 22,986,605 ÷ 696,626,436 = 3.299662%` 로 쓰지 않았습니다** | 그 등식은 성립하지 않습니다. 22,986,605 ÷ 696,626,436 = **3.299703%** 입니다 (Decimal 40자리 재계산). ⑤ 3.299662% 는 ① PMR 을 여섯 자리(0.035003%)로 끊고 ③ → ⑤ 로 간 값이고, PM × 365 를 바로 넣으면 끊기 전 값(0.0350034%)이 들어가 다섯째 자리에서 갈립니다 (`verify_final_terms.py` C2 주석의 dm_0901 규칙 1). 그래서 검산 셋째 줄은 분자를 ③ 에서 되짚은 7,429,796 원으로 두고 분모만 새 표기로 돌린 `PY_t = 7,429,796 ÷ ( ( Σ( A_i × D_i ) + PEC ) ÷ PD )` = 3.299662% 로 두었습니다. `( Σ( A_i × D_i ) + PEC ) ÷ PD` 는 옛 `PA + PEC ÷ PD` 와 같은 값(225,168,410원)이라 D3·D4 계산식은 그대로이고 넷째 줄 「같은 분자를 다른 분모로 나눈 것이다」도 참으로 남습니다. PM × 365 꼴을 쓰려면 값을 3.299703% 로 적고 넷째 줄을 지우며 D3·D4 판정식을 바꿔야 합니다 |
| 2 | 원고 `D`(집계) 항은 산식을 남겼습니다 | 아티팩트 표 2 는 개념 행·집계 행이 나란해 집계 행에 범위만 두었지만, 원고 `vars` 는 항목이 따로 서고 G2(`wD 산식 존재`)·G3·K10 이 그 formula 를 읽습니다. `D = Σ( A_i × D_i ) ÷ Σ A_i      i 는 대상정산금채권 전체 61,760건 · 발생 기준` 으로 표기만 맞췄습니다 |
| 3 | 목록 밖에 손댄 자리 | 아티팩트 `PEC` 행 `PEC = P 안 각 날의 EC 를 더한 값` → `PEC = Σ EC   d ∈ P` (정의 줄 규칙 적용 · 새 기호 없이 EC·d·P 만 씀). 원고 `D`(집계)·`LR`·`Σ A_i + EC` formula 의 괄호 표기 `( Σ A_i × D_i ) ÷ ( Σ A_i )` → `Σ( A_i × D_i ) ÷ Σ A_i` 꼴. 원고 `rules[1].body` 인용 조각, `calc.steps[7]`·`[8]` 라벨의 `PA × PD` → `Σ( A_i × D_i )`. 검사기 B9·C3·H0·I17 제목 문면과 자기시험 J 1건 |
| 4 | 검사기 판정 수 136 → **137** | J 자기시험에 「개념 D 산식에 설명 문장을 넣으면 K0 가 잡는가」 1건이 들었습니다. 통과 **135 / 137**, FAIL `I16` `I17` |
| 5 | `A10` 이 통과로 바뀐 것은 이 조의 변경이 아닙니다 | `daily_ledger.py:181` `TY5_EXPR = 'ty4 * ad / tot'` 와 `ledger_facts.json:54` `weekTyAsset "3.30"` 이 21:52 에 바뀌어 있습니다 (git `M` · 이 조는 손대지 않음 · 확인 필요). 화면 `payhug-investor-admin/invest-profit.html:174` 는 여전히 2.32% · 툴팁 `( PY_a × PA ) ÷ ( PA + PEC )` 라 I16·I17 이 남습니다 |
| 6 | 괄호 안 띄어쓰기 두 벌 | 낱건 행은 기존 `(1 − r)` `max(0, L_i)`, 개념 행은 지시 문면 그대로 `( 1 − r )` `max( 0, L )` 입니다. 세 규칙이 띄어쓰기를 정하지 않아 낱건 행은 그대로 두었습니다 |
| 7 | 검사기 I15 제목의 옛 `3.99%` | 직전 감사 4번 지적. 판정식은 유효하고 이 지시 범위 밖이라 그대로입니다 |

## (가) 아티팩트 `ceo_review.html` 고친 줄

백업 `ceo_review.prev4.html`. 줄 수 192 그대로.

| 줄 | 옛 | 새 |
|---|---|---|
| 81 | `<td>연환산을 뜻한다</td>` | `<td>연환산을 뜻한다 ( × 365 ÷ 금융일수 )</td>` |
| 108 | `<td class="f">투자실행금으로 가중평균한 금융일수</td>` | `<td class="f">D = Σ( A<sub>i</sub> × D<sub>i</sub> ) ÷ Σ A<sub>i</sub></td>` |
| 109 | `<td>투자실행금</td><td></td>` | `<td>투자실행금</td><td class="f">A = 순지급액 × ( 1 − r )</td>` |
| 110 | `<td>투자수익</td><td></td>` | `<td>투자수익</td><td class="f">M = 채권매입수수료 − max( 0, L )</td>` |
| 111 | `<td>상환액</td><td></td>` | `<td>상환액</td><td class="f">B = 순지급액 − max( 0, L )</td>` |
| 112 | `<td>입금부족액</td><td></td>` | `<td>입금부족액</td><td class="f">L = 미지급금 − 과지급금</td>` |
| 113 | `<td>투자수익율 (Margin)</td><td></td>` | `<td>투자수익율 (Margin)</td><td class="f">MR = M ÷ A</td>` |
| 136 | `D = Σ( A<sub>i</sub> × D<sub>i</sub> ) ÷ Σ A<sub>i</sub><br>i 는 대상정산금채권 전체` | `i 는 대상정산금채권 전체` |
| 152 | `PD = Σ( A<sub>i</sub> × D<sub>i</sub> ) ÷ PA &nbsp; i ∈ P` | `PD = Σ( A<sub>i</sub> × D<sub>i</sub> ) ÷ Σ A<sub>i</sub> &nbsp; i ∈ P` |
| 154 | `PEC = P 안 각 날의 EC 를 더한 값` | `PEC = Σ EC &nbsp; d ∈ P` |
| 160 | `PY<sub>t</sub> = PY<sub>a</sub> × PA × PD ÷ ( PA × PD + PEC )<br>     = PM × 365 ÷ ( PA × PD + PEC )` | `PY<sub>t</sub> = PM × 365 ÷ ( Σ( A<sub>i</sub> × D<sub>i</sub> ) + PEC ) &nbsp; i ∈ P<br>     = PY<sub>a</sub> × Σ( A<sub>i</sub> × D<sub>i</sub> ) ÷ ( Σ( A<sub>i</sub> × D<sub>i</sub> ) + PEC )` |
| 189 | `<span class="sym new">PA × PD + PEC</span> PEC 는 P 안 각 날의 EC 를 더한 값이라 원·일이고, PA 는 채권마다 한 번 더한 값이라 원이다. PA × PD 가 채권이 묶여 있던 원·일` | `<span class="sym new">Σ( A<sub>i</sub> × D<sub>i</sub> ) + PEC</span> PEC 는 P 안 각 날의 EC 를 더한 값이고 Σ( A<sub>i</sub> × D<sub>i</sub> ) 는 P 에 정산된 채권마다 투자실행액 × 금융일수를 더한 값이라 둘 다 금액 × 일수다` |

손대지 않은 것: 채택 11곳 문구 · Σ A<sub>i</sub> 행(129)·D 행(136)의 범위 문구 · 기존 칸 옛 기호(`D` `wD` `PwD` `PY_MR` `wPY_MR` · 표 3 `PA + PEC`) · 값 · `.note` 문단 · 표 3 다른 4행. 낱말 표식 `<span class="new">` 0건, 설명 문단 0건.

## (나) 표 2 전 산식 점검

규칙: ① 정의 줄 `이름 = Σ 낱건, 범위` ② 조립 산식은 이름으로만 ③ 한 산식 안 풀면 다 풀고 접으면 다 접기.

| # | 기호 | 산식 (새 판) | 규칙 판정 |
|---|---|---|---|
| 1 | d | (없음) | 상수 · 대상 아님 |
| 2 | r | `0.11% 예정` | 값 · 대상 아님 |
| 3 | D (개념) | `D = Σ( A_i × D_i ) ÷ Σ A_i` | ③ 다 풀기 · **고침** (설명 문장 → 산식) |
| 4 | A (개념) | `A = 순지급액 × ( 1 − r )` | 일반형 · **고침** (빈 칸 → 산식) |
| 5 | M (개념) | `M = 채권매입수수료 − max( 0, L )` | 일반형 · **고침** |
| 6 | B (개념) | `B = 순지급액 − max( 0, L )` | 일반형 · **고침** |
| 7 | L (개념) | `L = 미지급금 − 과지급금` | 일반형 · **고침** |
| 8 | MR (개념) | `MR = M ÷ A` | ② 이름만 · **고침** |
| 9 | D_i | `선정산일로부터 정산예정일까지의 한편 넣기 일수 …` | 기초 항목 정의문 · Σ·이름 없음 · 규칙 밖 · 유지 |
| 10 | A_i | `A_i = 순지급액_i × (1 − r)` | 낱건 정의 · 적합 |
| 11 | L_i | `L_i = 미지급금_i − 과지급금_i` | 적합 |
| 12 | 채권매입수수료_i | `채권매입수수료_i = 순지급액_i × r` | 적합 |
| 13 | M_i | `M_i = 채권매입수수료_i − max(0, L_i)` | 적합 |
| 14 | B_i | `B_i = 순지급액_i − max(0, L_i)` | 적합 |
| 15 | Σ A_i | `Σ A_i ⏎ i 는 정산예정일이 d 보다 뒤인 채권` | ① 정의 줄 · 이름 없는 합 · 적합 · 유지 2곳 |
| 16 | EC | `d 마감시점 쿠콘 가상계좌의 현금 잔액` | 기초 항목 정의문 · 규칙 밖 · 채택 8번 · 유지 |
| 17 | Σ A_i + EC | `Σ A_i + EC ⏎ i 는 정산예정일이 d 보다 뒤인 대상정산금채권` | ① · 적합 · 채택 9번 |
| 18 | D (집계) | `i 는 대상정산금채권 전체` | 개념 행이 산식을 맡고 집계 행은 범위 · **고침** · 범위 문구 유지 |
| 19 | LR | `LR = Σ L_i ÷ Σ A_i ⏎ i 는 선정산일이 d 의 20일 전부터 11일 전까지인 채권` | ①③ 분자·분모 다 풀림 · 적합 |
| 20 | Y_r | `Y_r = r × 365 ÷ D` | ② 이름만 · 적합 |
| 21 | PA | `PA = Σ A_i   i ∈ P` | ① · 적합 · 채택 11번 |
| 22 | PM | `PM = Σ M_i   i ∈ P` | ① · 적합 · 채택 12번 |
| 23 | PB | `PB = Σ B_i   i ∈ P` | ① · 적합 · 채택 12번 |
| 24 | PMR | `PMR = PM ÷ PA` | ② 이름만 · 적합 |
| 25 | PD | `PD = Σ( A_i × D_i ) ÷ Σ A_i   i ∈ P` | ③ · **고침** (분자 Σ · 분모 이름 PA 꼴 제거) |
| 26 | PEC | `PEC = Σ EC   d ∈ P` | ① · **고침** (문장 → 정의 줄 · 목록 밖 3번) |
| 27 | PY_a | `PY_a = PMR × 365 ÷ PD` | ② 이름만 · 적합 |
| 28 | PY_t | `PY_t = PM × 365 ÷ ( Σ( A_i × D_i ) + PEC )   i ∈ P ⏎ = PY_a × Σ( A_i × D_i ) ÷ ( Σ( A_i × D_i ) + PEC )` | 지시 문면 · **고침**. PM·PEC·PY_a 는 이름 있는 합이라 이름, Σ( A_i × D_i ) 는 이름이 없어 Σ |

고친 것 10칸 · 적합 14칸 · 규칙 밖(기초 항목 정의문·값·상수) 4칸.

## (다) 원고 `final_terms.json` 고친 키 (17)

| 키 | 옛 | 새 |
|---|---|---|
| `vars` D(개념).formula | `null` | `D = Σ( A_i × D_i ) ÷ Σ A_i` |
| `vars` A(개념).formula | `null` | `A = 순지급액 × ( 1 − r )` |
| `vars` M(개념).formula | `null` | `M = 채권매입수수료 − max( 0, L )` |
| `vars` B(개념).formula | `null` | `B = 순지급액 − max( 0, L )` |
| `vars` L(개념).formula | `null` | `L = 미지급금 − 과지급금` |
| `vars` MR(개념).formula | `null` | `MR = M ÷ A` |
| `vars` D(개념).plain | `… 것이 `D_i` 로, 정산예정일이 전일자인 채권들의 가중평균이 `PD` 로, 정산예정일이 선택한 기간에 …` | `… 것이 `D_i` 로, 정산예정일이 선택한 기간에 …` (`PD` 1회) |
| `vars` D(집계).formula | `D = ( Σ A_i × D_i ) ÷ ( Σ A_i )      i 는 대상정산금채권 전체 61,760건 · 발생 기준` | `D = Σ( A_i × D_i ) ÷ Σ A_i      i 는 대상정산금채권 전체 61,760건 · 발생 기준` |
| `vars` Σ A_i + EC.formula | `( Σ A_i ) + EC      i 는 회수되지 않은 대상정산금채권` | `Σ A_i + EC      i 는 회수되지 않은 대상정산금채권` |
| `vars` LR.formula | `LR = ( Σ L_i ) ÷ ( Σ A_i )      i 는 …` | `LR = Σ L_i ÷ Σ A_i      i 는 …` |
| `vars` PD.formula | `PD = ( Σ A_i × D_i ) ÷ PA      i 는 정산예정일이 선택한 기간에 해당하는 채권` | `PD = Σ( A_i × D_i ) ÷ Σ A_i      i ∈ P` |
| `vars` PEC.formula | `PEC = P 안 각 날의 EC 를 더한 값` | `PEC = Σ EC      d ∈ P` |
| `vars` PY_t.formula | `PY_t = PY_a × PA × PD ÷ ( PA × PD + PEC ) = PM × 365 ÷ ( PA × PD + PEC )` | `PY_t = PM × 365 ÷ ( Σ( A_i × D_i ) + PEC ) = PY_a × Σ( A_i × D_i ) ÷ ( Σ( A_i × D_i ) + PEC )      i ∈ P` (한 줄 · `build_final.py:111` 이 한 문단으로 조판) |
| `rules[1].body` 인용 | `` `× PA × PD ÷ ( PA × PD + PEC )` `` | `` `× Σ( A_i × D_i ) ÷ ( Σ( A_i × D_i ) + PEC )` `` |
| `calc.steps[7]` 라벨 | `④ 투자실행금 비중 = PA × PD ÷ (PA × PD + PEC)   PA × PD = Σ( A_i × D_i ) = 556,626,436` | `④ 투자실행금 비중 = Σ( A_i × D_i ) ÷ ( Σ( A_i × D_i ) + PEC )   Σ( A_i × D_i ) = 556,626,436` |
| `calc.steps[8]` 라벨 | `⑤ PY_t = ③ × PA × PD ÷ (PA × PD + PEC)` | `⑤ PY_t = ③ × Σ( A_i × D_i ) ÷ ( Σ( A_i × D_i ) + PEC )` |
| `calc.검산[2]` 문면 | `PY_t = 7,429,796 ÷ ( PA + PEC ÷ PD )` | `PY_t = 7,429,796 ÷ ( ( Σ( A_i × D_i ) + PEC ) ÷ PD )` (값 3.299662% 그대로 · 위 1번) |

값 칸은 전부 그대로입니다. `indent=2` 왕복이 원문과 바이트 단위로 같아(사전 확인) 다른 자리는 변하지 않았습니다. `Y`(개념) formula 는 `null` 그대로 — 지시가 「개념 6행」이고 표 1 접두 행이 `× 365 ÷ 금융일수` 를 맡습니다.

## (라) 검사기 `verify_final_terms.py`

| 항목 | 결과 |
|---|---|
| 전체 실행 (화면 렌더 + 자기시험) | **137건 · PASS 135 · FAIL 2** — `I16` `I17` |
| 화면 없이 (`FT_NOSCREEN=1`) | 99 / 99 |
| 자기시험 J | 8 / 8 통과 · J3 원고 md5 무변조 |
| 판정 완화 | 0건 |

판정별 반응

| 판정 | 옛 기준 | 새 기준 · 반응 |
|---|---|---|
| K0 | 개념 항목에 산식이 없다 | 접두 `Y` 를 뺀 개념 6항 전건에 `기호 = …` 꼴 산식이 있고, 우변 낱말이 원고 실재 기호 ∪ {순지급액·미지급금·과지급금·채권매입수수료·max·Σ·0·1·365} 뿐이며, 범위 조건(`i 는`·`∈`·`n건`·`d−1`·공백 3칸 이상)이 없고, 첨자는 `Σ` 가 있을 때만 선다. `Y` 에 산식이 있으면 FAIL. 실측 `7항 — D … · Y (없음)` PASS. 자기시험 `D = 투자실행금으로 가중평균한 금융일수` 를 넣으면 「재료 아닌 낱말 투자실행금으로, 가중평균한, 금융일수」로 FAIL (J.개념.D산식설명 PASS) |
| K1 | 그대로 | PASS — formula 와 무관 |
| K2 | 그대로 | PASS — D 개념 plain 이 `D_i` `PD` `D` 를 여전히 댄다 |
| K3 | 그대로 | PASS |
| D3 | `ann ÷ (PA + PEC × PA ÷ SAD)` | 계산식 그대로 (= `ann ÷ ( ( Σ( A_i × D_i ) + PEC ) ÷ PD )`) · 제목만 새 문면. 실측 `7429796 ÷ 225168410 = 3.299662% ↔ 원고 3.299662%` PASS |
| D4 | `'같은 분자' in 검산[3]` + 두 값 일치 | 그대로 · 실측 문면만 `÷( ( Σ( A_i × D_i ) + PEC ) ÷ PD )`. PASS |
| H0 | `'A_i × D_i' in f` | `'Σ( A_i × D_i ) ÷ Σ A_i' in f` 로 조임 · PASS |
| B9 · C3 · I17 | 제목 `PA × PD ÷ (PA × PD + PEC)` | 제목 `Σ( A_i × D_i ) ÷ ( Σ( A_i × D_i ) + PEC )` · 판정식 그대로 |
| G9 · G2 · G3 · K10 | 그대로 | PASS — LR·D(집계) formula 의 범위 문구·건수 유지 |

FAIL 2건 실측

| 판정 | 실측 | 원인 |
|---|---|---|
| I16 | `2.32% ↔ 3.30` | 화면 `invest-profit.html:174` ⑤ 가 옛 산식 값 |
| I17 | `화면 2.32% ↔ 원고산식 3.30 (두 자리로 끊으면 3.30)` | 같음 |

`A10` 은 `4.129577% → 4.13% ↔ 4.13%  ·  3.299662% → 3.30% ↔ 3.30%` PASS (원장 변경은 위 5번 · 이 조 아님).

## (마) 산출 파일

| 구분 | 경로 |
|---|---|
| 아티팩트 (갱신) | `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/ceo_review.html` |
| 아티팩트 백업 | `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/ceo_review.prev4.html` |
| 원고 | `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/final_terms.json` |
| 검사기 | `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_final_terms.py` |
| 워드 (신규) | `/Users/semi/Downloads/payhug_용어정의서/기호정리표_20260904_2155.docx` (39KB) |
| HTML (신규) | `/Users/semi/Downloads/payhug_용어정의서/기호정리표_20260904_2155.html` (13KB) |
| 이전판 이동 | `/Users/semi/Downloads/payhug_용어정의서/이전판/기호정리표_20260904_2126.docx` · `/Users/semi/Downloads/payhug_용어정의서/이전판/기호정리표_20260904_2126.html` |
| 편집 스크립트 | `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/step7/edit_artifact_json.py` · `edit_verifier.py` |
| 편집 전 사본 | `…/scratchpad/step7/final_terms.before.json` · `verify_final_terms.before.py` |
| 검사기 출력 | `…/scratchpad/step7/verify_full.txt` · `verify_noscreen.txt` |
| 보고서 | `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/step7_notation_report.md` |

생성기 `build_symreview.py` 는 손대지 않았습니다 (`SYMREVIEW_STAMP=20260904_2155` · 블록 h1 1 · h2 3 · table 3 · note 1). HTML 산출의 `<div class="wrap">` 이하는 아티팩트와 바이트 단위로 같습니다 (8,030자).

## (바) 워드 확인 (python-docx)

| 항목 | 실측 |
|---|---|
| 표 수 | 3 · 표 1 8행×3열 · 표 2 29행×5열 · 표 3 6행×3열 (직전 판과 같음) |
| 표 1 접두 Y 행 | `접두 Y │ 연환산을 뜻한다 ( × 365 ÷ 금융일수 ) │ Y_r PY_a PY_t` |
| 표 2 개념 D 행 산식 | `D = Σ( A_i × D_i ) ÷ Σ A_i` (첨자 run) |
| 표 2 개념 A·M·B·L·MR 산식 | `A = 순지급액 × ( 1 − r )` · `M = 채권매입수수료 − max( 0, L )` · `B = 순지급액 − max( 0, L )` · `L = 미지급금 − 과지급금` · `MR = M ÷ A` |
| 표 2 투자 자산 D 행 산식 | `i 는 대상정산금채권 전체` |
| 표 2 PD 행 | `PD = Σ( A_i × D_i ) ÷ Σ A_i   i ∈ P` |
| 표 2 PEC 행 | `PEC = Σ EC   d ∈ P` |
| 표 2 PY_t 행 | 1줄 `PY_t = PM × 365 ÷ ( Σ( A_i × D_i ) + PEC )   i ∈ P` ⏎ 2줄 `     = PY_a × Σ( A_i × D_i ) ÷ ( Σ( A_i × D_i ) + PEC )` (줄바꿈 run · 공백 5자 · 첨자 run) · 기존 칸 `wPY_MR` |
| 표 3 ⑤ 분모 행 | `⑤ 분모 │ PA + PEC │ Σ( A_i × D_i ) + PEC PEC 는 P 안 각 날의 EC 를 더한 값이고 Σ( A_i × D_i ) 는 P 에 정산된 채권마다 투자실행액 × 금융일수를 더한 값이라 둘 다 금액 × 일수다` |
| 옛 문면 잔존 | `PA × PD` 0 · `투자실행금으로 가중평균한` 0 · `PA + PEC ÷ PD` 0 · `× PA ÷ (PA + PEC)` 0 · `÷ PA` 1 (`PMR = PM ÷ PA` · 조립 산식 · 적합) |
| 금지 낱말 | 신설·추가·기존에는·종전·이번에·신규·대시(—) 전부 0 |
| run 색 | 파랑 2C4470 **23** (개선 기호 · 표 3 `Σ( A_i × D_i ) + PEC` 포함) · 빨강 A63D2F 33 (기존 기호) · 회색 6E6A63 11 · 첨자 run 81 |
