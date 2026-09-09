# step16 — 원장 입금부족액 0 적용 (L_i = 0) · 화면·낱장·엑셀·사실값·검증기 재생성

2026-09-09. 통합본 레포 `/Users/semi/cursor/payhug-investor-admin` (HEAD `d9af5a7`, 커밋 안 함) · 파이프라인 `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin`.

## 1. 지시 밖에서 바꾼 것 · 못 한 것

| 구분 | 무엇 | 어디 | 왜 |
|---|---|---|---|
| 바꿈 (지시 밖) | 검증기 F 절 `MR` 을 여섯 자리에서 끊고 곱함 | `verify_final_terms.py:426-427` · `:452` | 원장 규칙(`daily_ledger.py:210-211` TY6_EXPR 주석 · dm_0901 규칙 1)은 MR 을 6자리로 끊는데 검증기는 안 끊어 2026-04-16 · 07-02 두 날이 표기 한 눈금 어긋남(F.rule FAIL). 옛 값에서는 우연히 180일 전건 일치 |
| 바꿈 (지시 밖) | 합계 행 ty 되짚기를 PSMR 6자리 × 365 ÷ 원장 `weekWRaw` 로 | `verify_batch_symbols.py:703-708` | 표기 두 자리 W(3.11)로 되짚으면 12.92, 화면·원장은 12.93. 옛 값(3.99)에서는 두 길이 같은 표기 |
| 바꿈 (지시 밖) | 엑셀 미리보기 낱장 두 장의 표 값 | `xls-profit-status.html:136-139` · `xls-profit-daily.html:135-142` | 이 두 낱장은 생성기가 없음(`step6_xlsprev_report.md:9`). 실물 xlsx(`투자수익현황_2026-08-21_2026-08-27.xlsx` · `일별투자수익_…`)를 openpyxl 로 읽어 칸 단위로 치환(스크래치 스크립트). `verify_crossscreen.py` 「xls-profit-daily 7행」「xls-profit-status 카드」 FAIL 2건이 이걸로 해소 |
| 못 함 (결정 필요) | 투자 시뮬레이션 기본값 미지급률 0.08 · 과지급률 0.01 | `build_app.py:2052-2056` `SIM_DEFAULT` · `app.html:2485-2486` 주석 「투자 자산 화면의 0.07% 와 같아지는 자리」 · `invest-sim--result.html:342` | 지시 「다른 상수는 건드리지 않는다」. 그 결과 `#invest-sim/result` 현황표 입금부족률 **0.07%** · 기간 내 투자수익 16,000(수수료 44,000 − 차감 28,000)이 투자 자산 화면 0.00% 와 갈림. `grep -c "0.07%" app.html` = 2 는 이 주석 두 줄 |
| 못 함 (지시) | `platform_duration.py:126-139` 주석(「③ 방향 — 미지급이 과지급보다 크다」 등) | 같은 파일 | 지시 범위가 `:140-141` · `:143` 이라 그대로. 값 0 과 설명이 어긋남 |
| 못 함 (지시) | 기호정리표 V1.3 원고 예시값(PM 61,175 · PMR 0.033992% · ④ 3.99% · ⑤ 3.19%) | `final_terms.json` · `session_0904/artifact/ceo_review.html` | 원고 갱신은 사용자 결정(V1.4). `verify_final_terms.py` FAIL 14 (§4) |
| 못 함 (범위 밖) | 시연본 재동기화 · `gate_prototype.js` · `prep_fig.py` · Figma | `sync_prototype.sh` | 지시 목록에 없음. `verify_proto.js` FAIL 8 · `verify_shortfall.py` 3 · `verify_batch_symbols.py` 3 은 전부 시연본(`payhug-investor-prototype` `7ba7f26`)의 옛 값 |
| 못 함 (범위 밖) | 문서 페이지·용어 해설의 옛 값 | `glossary.html` 0.07% 6 · 61,175 7 · 3.99% 10 · 3.19% 2 / `calc.html` 1·1·1·0 / `steps-all.html` 1·1·1·0 / `terms-edit.html` 1·1·1·0 / `final-terms.html` 0·1·1·0 / `capability.html` 1·0·2·2 / `feasibility.html` 0·0·1·1 / `inquiry.html` 0·0·2·4 | `capture_shots.js`·`build_glossary.py`·문서 페이지 생성기는 돌리지 않음(F·G 범위). `verify_batch_symbols.py` 「삼각 대조」 3건이 여기서 남 |
| 못 함 (재설계 필요) | `verify_shortfall.py` 판별력 검사 15건 · `verify_batch_symbols.py` 요율 행태 시험 3건 | `verify_shortfall.py:626-650` · `:730-760` · `verify_batch_symbols.py:1188-1200` | 부족액이 0 이면 방식1 = 방식2 = 가맹평균 = 0 이라 「서로 다르다」류 검사가 판별할 값이 없고, 요율을 뒤집어도 0 ↔ 0 이라 클램프가 발동하지 않음. 합성 요율로 시험하도록 바꾸는 것은 검사 설계 변경이라 손대지 않음 |
| 못 함 (지시) | `/Users/semi/cursor/payhug/CLAUDE.md` 「S입금부족율 0.07%」 문장 | | 사용자가 확인 |
| 확인 | `README.md` 는 `build_readme.py` 로 다시 만들었으나 내용 변화 없음 | | git diff 에 없음 |

## 2. 고친 파일과 자리

| 파일 | 줄 | 내용 |
|---|---|---|
| `platform_duration.py` | 140 | `UNPAID = {'card': D('0'), 'bm': D('0'), 'cpe': D('0'), 'yo': D('0')}` |
| `platform_duration.py` | 141 | `OVERPAID = {'card': D('0'), 'bm': D('0'), 'cpe': D('0'), 'yo': D('0')}` |
| `platform_duration.py` | 143 | `assert 0 <= OVERPAID[_k] <= UNPAID[_k], _k` |
| `platform_duration.py` | 192 | 출력문 그대로(`미지급 0%  과지급 0%  순 0%` 로 찍힘) |
| `daily_ledger.py` | — | 손대지 않음. `M = 채권매입수수료 − max(0, 미지급 − 과지급)` · `B = 순지급액 − max(0, …)` 그대로라 부족액 0 이 결과에 따라옴 |
| `verify_final_terms.py` | 426-427 · 452 | F 절 `q(MR, 6)` |
| `verify_batch_symbols.py` | 703-708 | 합계 행 되짚기 PSMR 6자리 · PSD = `facts['weekWRaw']` · 화면 합계 W 두 자리가 그 표기인지 assert |
| `xls-profit-status.html` (통합본 레포) | 136-139 | 투자수익 198,184 · ④ 12.93% · ⑤ 10.34% |
| `xls-profit-daily.html` (통합본 레포) | 135-142 | 7행 + 합계 행, 실물 xlsx 값 |

## 3. 전후 값

### 3-1. 기본 검색대상기간 2026-08-21 ~ 08-27 (`ledger_facts.json`)

| 항목 | 전 | 후 | 비고 |
|---|---|---|---|
| 투자실행금 PA | 179,970,919 | **179,970,919** | 같음 |
| 투자수익 PM | 61,175 | **198,184** | = 채권매입수수료 합 |
| 상환액 PB | 180,032,111 | **180,169,120** | = 순지급액 합 = PA + PM 에서 원 단위 절사 차 17원 |
| PMR = PM ÷ PA | 0.033992% | **0.110120%** | 기대 0.11 ÷ (1 − 0.0011) = 0.110121%. 차 1e-6 은 수수료 원 단위 절사 |
| PD | 3.11 (3.107588) | **3.11 (3.107588)** | 같음 |
| ④ PY_a | 3.99% (3.992511) | **12.93%** (12.934083) | |
| Σ(A_i × D_i) | 559,275,516 | **559,275,516** | 같음 |
| PEC | 140,000,000 | **140,000,000** | 같음 |
| ⑤ PY_t | 3.19% (3.193182) | **10.34%** (10.344586) | |
| 부족액 차감 합 | 137,009 (수수료의 69.13%) | **0** | |

### 3-2. 투자 자산 카드 · 현황표

| 항목 | 전 | 후 |
|---|---|---|
| 투자자산 | 100,000,000 | **100,000,000** |
| 투자실행액 | 80,000,000 | **80,000,000** |
| 순현금 | 20,000,000 | **20,000,000** |
| 가중평균 금융일수 | 3.04일 (3.039607) | **3.04일** (3.039607) |
| 입금부족률 LR | 0.07% (0.074328) | **0.00%** (0.000000) |
| 예상 연환산 수익률 | 13.21% | **13.21%** |
| 가맹점별 표 입금부족률 8행 | 0.07 · 0.10 · 0.09 · 0.08 · 0.06 · 0.05 · 0.05 · 0.04 | **전부 0.00%** (투자실행액·W·예상 연환산·비중은 같음) |

### 3-3. 일별 표 08-21 행

| 항목 | 전 | 후 |
|---|---|---|
| 상환액 | 25,951,644 | **25,970,340** |
| 투자실행금 | 25,941,773 | **25,941,773** |
| 투자 수익 | 9,871 | **28,567** = 25,970,340 − 25,941,773 = 채권매입수수료 28,567 |
| 가중평균 금융일수 | 3.06 | **3.06** |
| 연환산 수익률 | 4.54% | **13.15%** |
| 부족액 차감 | 18,696 | **0** |

### 3-4. 그 밖의 원장 사실값

| 항목 | 전 | 후 |
|---|---|---|
| 전 구간(03-01~08-27) 투자수익 | 1,787,417 | **5,176,160** (= 수수료 합) |
| 전 구간 ④ / ⑤ | 4.57% / 3.65% | **13.25% / 10.58%** |
| 월별 ④ 3~8월 | 4.49 · 4.83 · 4.38 · 4.38 · 4.76 · 4.62 | **13.20 · 13.37 · 13.16 · 13.14 · 13.35 · 13.27** |
| 월별 W | 3.05 · 3.01 · 3.05 · 3.06 · 3.01 · 3.03 | 같음 |
| 채권 61,760건 · 미회수 2,240건 · 표본 3,200건 · dayAvg 26,113,907 | | 같음 |
| `sim_facts.json` | | 변화 없음(시뮬은 자기 입력값으로 계산) |

## 4. 재생성 · 검증 결과

### 4-1. 생성기

| 순서 | 명령 | 결과 |
|---|---|---|
| 1 | `python3 daily_ledger.py` | `ledger_facts.json` 갱신. S입금부족율 0.00% · 채권매입수수료 5,176,160 · 차감 0 · 투자수익 5,176,160 |
| 2 | `python3 build_xlsx.py` | 14개 xlsx 재생성 · 낱장 4장 파일바 동기화 |
| 3 | `python3 build_app.py` | `app.html` 235,465 B / 3,813줄 |
| 4 | `sync_assets_static.py` · `sync_profit_static.py` · `build_sim_static.py` | 투자 자산 낱장 3 + 증명서 · 투자 수익 낱장 4 · 시뮬 낱장 2 |
| 5 | `build_audit_xlsx.py` · `build_docs.py` | `검산_투자자어드민_20260901.xlsx` · `투자자산증명서_20260827.pdf` 245,257 B. 실패 없음 |
| 6 | `sim_facts.py` · `build_readme.py` | `sim_facts.json` 값 같음 · README 내용 같음 |

증명서 PDF 본문 대조(PyMuPDF, HEAD 판 ↔ 새 판): 바뀐 줄 16 = 가맹점 8행의 입금부족률 `0.0x%` → `0.00%` 뿐. 투자자산·투자실행액·순현금·W·예상 연환산은 같음.

### 4-2. 검증기 (최소 실행 8종)

| 검사기 | PASS | FAIL | FAIL 내역 |
|---|---|---|---|
| `node verify_app.js` | 123 | 0 | 콘솔 에러 0 · 죽은 컨트롤 0 |
| `node verify_proto.js` | 110 | 8 | 전부 시연본(`payhug-investor-prototype`)의 옛 값 — 기본 기간 ④⑤ · 일별 합계·7행 · 월별 ④⑤·합계·6행. 시연본 재동기화는 범위 밖 |
| `node verify_sim.js` | 93 | 0 | |
| `node verify_identity.js` | 18 | 0 | `sRaw 0.000000 < 할인율 0.11` 가드 통과 |
| `python3 verify_crossscreen.py` | 62 | 3 | 용어 해설 duration 블록 3건 — 기존(NEXT_SESSION G). 1차 실행의 xls 미리보기 2건은 낱장 치환 뒤 해소 |
| `python3 verify_final_terms.py` | 288 | 14 | **V1.3 원고 대조 14** (아래 4-3). F.rule 1건은 검증기 수정으로 해소 |
| `python3 verify_0828.py` | 32 | 0 | |
| `node verify_weighting.js` | 28 | 0 | |

### 4-3. V1.3 원고 대조 FAIL (고치지 않음 · 사용자 결정 V1.4)

| 검사 | 원고 | 재계산 |
|---|---|---|
| B1 PM | 61,175 | 198,184 |
| B5 PMR | 0.033992% | 0.110120% |
| B7 · B8 ③ PY_a | 3.992511% · 3.99% | 12.934083% · 12.93% |
| B10 · B11 ⑤ PY_t | 3.193182% · 3.19% | 10.344586% · 10.34% |
| C4 · C5 ③⑤ 재현 | 3.992511% · 3.193182% | 12.934083% · 10.344586% |
| K11 · K12 수익율 두 층 설명 문장 | 0.033992% · 3.992511% · 3.99% | 0.110120% · 12.934083% · 12.93% |
| I15 · I16 화면 ③⑤ = 원고 | 3.99 · 3.19 | 12.93% · 10.34% |
| J.calc.③ · J2 | 판별력 시험 파생(B7 이 이미 FAIL 이라 새 FAIL 로 잡히지 않음) | |

### 4-4. 추가로 돌린 검사기 (최소 목록 밖 · 부족액 영향)

| 검사기 | PASS | FAIL | FAIL 분류 |
|---|---|---|---|
| `python3 verify_shortfall.py` | 61 | 21 | 판별력(0 이라 방식1 = 방식2) 15 · 시연본 3 · 툴팁 문언 3(기존 — 결과 JSON 9/7 이후 V1.3 툴팁 규칙으로 문구가 바뀜, `POP_S_TEXT` 「…인 표본」 ≠ 화면 「… · 3,200건」) |
| `python3 verify_batch_symbols.py` | 120 | 9 | 시연본 3 · 삼각 대조 3(시연본·원고·배포 glossary 옛 값) · 요율 행태 시험 3(요율 0). `[app] 합계 행 ty` 1건은 검증기 수정으로 해소 |

돌리지 않음: `gate_prototype.js`(시연본·배포 URL 대상) · `capture_shots.js` · `build_glossary.py` · `prep_fig.py` · `sync_prototype.sh`.

## 5. 헤드리스 DOM 실측 (`app.html`, 스크래치 `probe_dom.js` → `dom_probe.json`)

| 화면 | 실측 |
|---|---|
| `#invest-assets` 카드 4 | 투자자산 100,000,000원 · 투자실행액 80,000,000원 · 순현금 20,000,000원 · 예상 연환산 수익률 13.21% (부제 「가중평균 금융일수 3.04일 기준」) |
| `#invest-assets` 현황표 | 열 5 · 투자실행액 80,000,000 / 3.04일 / **0.00%** / 13.21% · 순현금 20,000,000 / - / - / - · 합계 (투자자산) 100,000,000 |
| `#invest-assets` 가맹점별 표 | 8행 입금부족률 전부 **0.00%** · 비중 24.2 · 22.6 · 14.8 · 11.6 · 8.8 · 7.0 · 6.0 · 5.0 (합 100.0) |
| `#invest-profit` 카드 | 검색대상기간 179,970,919원 (2026-08-21 ~ 2026-08-27) · 198,184원 · **12.93%** · **10.34%** |
| `#invest-profit` 일별 표 7행 | 08-21 25,970,340 / 25,941,773 / 28,567 / 3.06 / 13.15% · 08-22 25,394,136 / 25,366,208 / 27,933 / 3.10 / 12.97% · 08-23 25,207,385 / 25,179,655 / 27,728 / 3.12 / 12.90% · 08-24 25,301,031 / 25,273,193 / 27,831 / 3.12 / 12.87% · 08-25 25,622,093 / 25,593,903 / 28,184 / 3.13 / 12.86% · 08-26 26,122,944 / 26,094,204 / 28,735 / 3.12 / 12.86% · 08-27 26,551,191 / 26,521,983 / 29,206 / 3.11 / 12.94% |
| `#invest-profit` 합계 행 | 180,169,120 / 179,970,919 / 198,184 / 3.11 / 12.93% |
| `#invest-sim/result` | 입력 r 0.11 · 순현금 20,000,000 · 미지급률 0.08 · 과지급률 0.01 · 08-21~08-27. 카드 99,912,000원 · 79,912,000원 · 20,000,000원 · 13.21% · 39,956,000원 · 16,000원 · 4.81% · 2.23%. 현황표 투자실행액 79,912,000 / 3.04일 / **0.07%** / 13.21% (시뮬 기본값 그대로 — §1) |

옛 값 잔존 검색(통합본 레포): `0.07%` — `app.html` 2(시뮬 기본값 주석) · `invest-sim--result.html` 1 · 나머지 투자 자산·수익·엑셀 미리보기·증명서 낱장 0. `61,175`·`3.99%`·`3.19%`·`0.033992`·`180,032,111` — app.html·투자 수익 낱장·엑셀 미리보기 0. 「보관 ㈜」·「keeper」 0.

## 6. diff 요약

| 레포 | 파일 수 | 목록 |
|---|---|---|
| `/Users/semi/cursor/payhug-investor-admin` | 27 (+337 / −337) | `app.html` · `assets/docs/투자자산증명서_20260827.pdf` · `assets/xlsx/*.xlsx` 14 · `certificate.html` · `invest-assets.html` · `invest-assets--cert-confirm.html` · `invest-assets--download.html` · `invest-profit.html` · `invest-profit--weekly.html` · `invest-profit--monthly.html` · `xls-assets-status.html` · `xls-assets-merchant.html` · `xls-profit-status.html` · `xls-profit-daily.html` |
| `/Users/semi/cursor/payhug` (파이프라인) | 11 | `platform_duration.py` · `ledger_facts.json` · `verify_final_terms.py` · `verify_batch_symbols.py` · `검산_투자자어드민_20260901.xlsx` · 결과 JSON 6 (`verify_app` · `verify_proto` · `verify_sim` · `verify_identity` · `verify_shortfall` · `verify_batch_symbols`) |

커밋·push 는 하지 않았습니다. 임시 파일은 `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/builder_zero_0909/` (전 사실값 `ledger_facts_before.json` · `sim_facts_before.json` · 증명서 HEAD 판 `cert_before.pdf` · DOM 실측 `dom_probe.json` · 검사기 로그).
