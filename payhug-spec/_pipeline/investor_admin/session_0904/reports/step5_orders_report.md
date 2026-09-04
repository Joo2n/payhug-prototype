# 5단계 지시 이행 검사

기준: 지시서 표의 각 행을 산출물(`app.html`·낱장 15종·`_fig/*.html` 33·xlsx 14·증명서 PDF)에서 직접 열어 셈. HEAD(investor-admin `1693bd3` 08-31 · payhug `26a255a` 09-01)는 5단계 직전 상태가 아니라 9/1 이후 라운드가 전부 섞여 있으므로, 5단계 몫은 파일 수정 시각(09-04 18:03~18:19)과 빌더의 18:03/18:10 숫자 스냅샷·`app.before.html`(09-02)로 갈랐습니다.

## 미이행 · 지시 밖 변경

| 구분 | 내용 | 빌더 보고 | 판정 |
|---|---|---|---|
| 미이행 | 지시 표 12행 중 산출물에서 안 된 행 | — | **없음** |
| 지시 밖 변경 | 검증기 5종(`verify_crossscreen.py`·`verify_final_terms.py`·`verify_shortfall.py`·`verify_batch_symbols.py`·`verify_sim.js`)과 `sim_facts.py` 수정. 지시서 원천 목록(생성기 6종·낱장 15종) 밖 | 보고함 | 사실. 18:16~18:19 수정, diff 로 확인 |
| 지시 밖 변경 | `build_app.py` 주석 2줄(`소문자 d 표기는 잠정이다 — 대표 DM 15:15 …`) · `sync_assets_static.py` 같은 주석 2줄 + `PEND_BADGE`·`PEND_ROW` 상수 + 그 위 설명 주석 1줄(`# 대표 재전달 대기 표기 —`) + `pend` 인자 삭제 | 「주석 2곳」·상수·인자 보고. 설명 주석 1줄은 보고에 없음 | 사실. 화면 문자열 아님 |
| 지시 밖 변경 | `verify_batch_symbols_result.json`(18:18) · `verify_shortfall_result.json`(18:19) 재작성 | 보고에 없음 | 검증기 실행 부산물 |
| 범위 밖 미수행 | `verify_sim.js` 미실행 · `sim_facts.json` 8/31 판 잔존(`Ty수익율` 1 · `W금융일수` 12) | 보고함 | 사실. `verify_sim_result.json` 09-02 03:12 그대로 |
| 범위 밖 미수행 | 시연본 `~/cursor/payhug-investor-prototype/index.html` 09-02 판 그대로(`S입금부족율` 8 · `Ty수익율` 19 · `W금융일수` 21). 5단계가 그 레포에 쓴 파일 없음(assets 09-02) | 보고함 | 사실 |

## 확인 1 — 지시 표 각 행의 산출물 이행

### 1-1 `S입금부족율` → `입금부족률`

| 파일 | 새 라벨 | 옛 잔존 | 판정 |
|---|---|---|---|
| `/Users/semi/cursor/payhug-investor-admin/app.html` | 6 | 0(화면) · 주석 1(2598행) | 됨 |
| `invest-assets.html` · `--download` · `--cert-confirm` · `--empty` | 각 2 (열머리 앵커 ×2) | 0 | 됨 |
| `invest-sim--result.html` (현황표 th) | 1 | 0 | 됨 |
| `certificate.html` | 1 | 0 | 됨 |
| `xls-assets-status.html` · `xls-assets-merchant.html` | 각 1 | 0 | 됨 |
| xlsx `투자자산현황_2026-08-27_2026-08-27.xlsx` D3 · `가맹점별투자자산_…` D3 | 각 1 | 0 | 됨 |
| PDF `assets/docs/투자자산증명서_20260827.pdf` | 1 | 0 | 됨 |
| 엑셀 각주 | `build_xlsx.py:271` 문자열은 바뀜. 시트에는 각주가 애초에 없음(`put_note` 가 `return` 만 하는 무동작, 5단계 이전부터. HEAD xlsx 도 `A1:G6`) | — | 해당 자리 없음 |
| `_fig/` 5화면(자산 4 · 시뮬 1) + `certificate` + `xls-assets-*` | 루트 낱장과 동일 건수 | 0 | 됨 |

### 1-2 `W금융일수` → `가중평균 금융일수`

| 파일 | 새 라벨 | 옛 잔존 | 판정 |
|---|---|---|---|
| `app.html` | 16 | 0(화면) · 주석 11줄 · 인용 1(2300행 「대표 DM 16:27」, 유지 대상) | 됨 |
| 자산 낱장 4종 (카드 부제 `가중평균 금융일수 3.04일 기준` + 열머리 ×2) | 각 3 | 0 | 됨 |
| 수익 낱장 4종 (툴팁 `기간 가중평균 금융일수` + 일별 th + `⑤가중평균 금융일수`) | 각 3 | 0 | 됨 |
| `invest-sim--result.html` | 5 | 0 | 됨 |
| `certificate.html` · `xls-assets-*` · `xls-profit-daily.html` | 각 1 | 0 | 됨 |
| xlsx 14종 (자산 2 C3 · 일별/주별/월별 6 E3) | 각 1 | 0 | 됨 |
| PDF | 1(`가중평균 금/융일수` 로 줄바꿈 추출) | 0 | 됨 |
| `_fig/` | 루트와 동일 | 0 | 됨 |

### 1-3 `Ty수익율` 투자 자산 계통 → `예상 연환산수익률`

| 파일 | 새 라벨 | 옛 잔존 | 판정 |
|---|---|---|---|
| `app.html` (투자자산 카드 앵커 · 자산 구분 표 · 가맹점별 표 · 증명서 th · 시뮬 현황표 등) | 8 | 0(화면) | 됨 |
| 자산 낱장 4종 (카드 라벨 + 자산 구분 th + 가맹점별 th) | 각 3 | 0 | 됨 |
| `invest-sim--result.html` (요약 카드 + 현황표 th) | 2 | 0 | 됨 |
| `certificate.html` · `xls-assets-status` · `xls-assets-merchant` | 각 1 | 0 | 됨 |
| xlsx 자산 2종 E3 | 각 1 | 0 | 됨 |
| PDF | 1(`예상 연환산/수익률` 줄바꿈) | 0 | 됨 |

### 1-4 `Ty수익율` 투자 수익 계통 → `연환산수익률`

| 파일 | 새 라벨(「예상」 제외) | 옛 잔존 | 판정 |
|---|---|---|---|
| `app.html` (④⑤ 카드 · ⑥ 열머리 · 엑셀 미리보기 7·8행) | 6 | 0(화면) | 됨 |
| 수익 낱장 4종 (④⑤ 카드 앵커 · 일별 th) | 각 2 | 0 | 됨 |
| `invest-sim--result.html` (수익 현황 카드 · 일별 th) | 2 | 0 | 됨 |
| `xls-profit-status.html` 7·8행 `연환산수익률 (투자실행금액 대비)` / `(투자자산 대비)` | 2 | 0 | 됨 · 부제 유지 |
| `xls-profit-daily.html` 머리글 | 1 | 0 | 됨 |
| xlsx `투자수익현황_*` 6종 A7/A8 · 일별/주별/월별 6종 F3 | 각 2 / 각 1 | 0 | 됨 · 부제 유지 |

### 1-5 툴팁 문면 4건 (`÷ PD` · `PD = 기간 가중평균 금융일수` · `관찰된 값 · PMR 계통` · `PY<sub>a</sub>`)

| 파일 | 자리 | 판정 |
|---|---|---|
| `app.html` 2509·2511·2514·2518 (투자 수익) · 2802·2804·2807·2811 (시뮬) | `PMR × 365 ÷ PD` / `<span>PD</span><span>기간 가중평균 금융일수</span>` / `관찰된 값 · PMR 계통` / `( PY<sub>a</sub> × PA ) ÷ ( PA + PEC )` | 됨 (각 2) |
| 수익 낱장 4종 L170~174(본판 기준) · `invest-sim--result.html` L372~376 | 위와 동일 4건 | 됨 (각 1) |
| 잔존 `PwD`·`실적치`·`PY<sub>MR` | `app.html` 주석·변수명(`var PwD`, `R.PwD`)만 6줄 · 낱장 0 · `_fig` 0 | 됨 |

### 1-6 표본 문구 `선정산일 d-20 ~ d-11 표본` → `선정산일이 기준일 20일 전 ~ 11일 전인 표본`

| 파일 | 새 문구 | `d-20`/`D-20` 잔존 | 판정 |
|---|---|---|---|
| `app.html:1850` `POP_S.of` | 1 | 0 | 됨 |
| 자산 낱장 4종 (열머리 툴팁 ×2) | 각 2 | 0 | 됨 |
| `_fig/invest-assets*.html` 4종 | 각 2 | 0 | 됨 |
| 시뮬 현황표 | HEAD 시점부터 툴팁 없는 평문 `<th>` — 대상 자리 없음 | 0 | 해당 없음 |

### 1-7 입금부족률 열의 「표기 d · 미확정」 행 + `미확정` 배지 제거 / ⑤⑥ 배지·행 유지

| 파일 | 「표기 d」 | `미확정` HEAD→WT | 판정 |
|---|---|---|---|
| `app.html` | HEAD 1(1665행 `p.pend ? …표기 d…`) → 0 | 10 → 8 (빠진 2 = 「표기 d」 행 + 그 열 `PEND_ROW`) | 됨 |
| 자산 낱장 4종 | 2 → 0 | 6 → 0 (열 2 × 행·PEND_ROW·배지 3) | 됨 |
| 수익 낱장 4종 | 0 | 7 → 7 (⑤ 카드 배지+행 · ⑥ th 배지+행 · ③ th 배지+행) | 됨 · 유지 |
| `invest-sim--result.html` | 0 | 7 → 7 | 됨 · 유지 |
| `_fig/` | 0 | 자산 0 · 수익 7 · 시뮬 7 | 됨 |

### 1-8 투자자산 카드 툴팁 첫 줄 · 「대표 DM 16:27」 행 유지

| 파일 | 확인 | 판정 |
|---|---|---|
| `app.html:2297` | `할인율 × 365 ÷ 가중평균 금융일수` | 됨 |
| `app.html:2300` | `대표 DM 16:27 · 365 ÷ W금융일수 = 1년 회전수` 그대로 | 됨 · 유지 |
| 자산 낱장 4종 | 카드에 툴팁 자체가 없음(HEAD 시점부터 라벨·값·부제만) | 해당 없음 |

### 1-9 `일별 표 열 … ⑤W금융일수` → `⑤가중평균 금융일수`

| 파일 | 건수 | 판정 |
|---|---|---|
| `app.html` | 1 | 됨 |
| 수익 낱장 4종 · `invest-sim--result.html` · `_fig` 동일 5종 | 각 1 | 됨 |

## 확인 2 — 「손대지 말 것」

| 항목 | 확인 방법 | 결과 | 판정 |
|---|---|---|---|
| 사이드바 메뉴 라벨 | `app.html`·`invest-assets`·`invest-profit`·`invest-sim--result`·`certificate` 의 nav 라벨 15개 HEAD 대 WT 비교 | 5개 파일 전부 동일 | 지켜짐 |
| 원문 인용 | `대표 DM 16:27` 1→1 · `16:45` 3→3 · `16:19` 1→1 (`app.html`), 수익·시뮬 낱장 `16:45` 1→1. 줄어든 「대표 DM」 1건은 삭제 주석 안의 `15:15`(HEAD 1658행 `/* …`) | 툴팁 인용 행 전부 유지 | 지켜짐 |
| 문서 화면 10종 | 09-04 수정 시각 목록에 `glossary`·`steps-all`·`calc`·`terms-edit`·`final-terms`·`capability`·`inquiry`·`feasibility`·`ceo-questions`·`review` 없음 (`git status` 의 M/A 는 9/1~9/3 라운드 것) | 5단계 변경 0 | 지켜짐 |
| 숫자 불변 | 빌더 18:03/18:10 `.nums` 스냅샷 재대조: 낱장 11종 차이 0 · `app.html` 6개(`15` `15` `0831` `0831.` `4` `1` — 삭제 주석·`pend:1` 안) · `xls-*` 4종 각 3쌍(파일바 생성일시 `09-03 20:02`→`09-04 18:10`). xlsx 값 셀(B4 80000000 · C4 3.04 · D4 0.0007 · E4 0.1321 등) HEAD 와 동일 | 화면 값 변화 0 | 지켜짐 |
| CSS | `assets/base.css`·`assets/sheet.css` `git status` 미표시. `_fig/assets/sheet.css` 는 mtime 18:10 이나 `git diff` 0(`prep_fig.py` 08-30 판의 상시 ellipsis 패치) | 변경 0 | 지켜짐 |
| 코드 변수명·주석 | 변수 `PwD`·`PY_MR` 등 그대로. 주석은 2곳(+설명 1줄) 삭제 — 위 「지시 밖 변경」 | 삭제만 있음 | 빌더 보고대로 |
| 산식·값 | 위 숫자 불변 항목과 같음 | — | 지켜짐 |

## 확인 3 — 「미확정」 배지

| 파일 | 입금부족률 열 배지 | ⑤ 카드 배지·행 | ⑥ 열머리 배지·행 | 판정 |
|---|---|---|---|---|
| `app.html` | 제거(`popTh` 의 `pend` 분기 없음, `PEND_BADGE`·`PEND_ROW` 는 ⑤⑥용으로 남음) | 유지 | 유지 | 됨 |
| 자산 낱장 4종 | 0 | — | — | 됨 |
| 수익 낱장 4종 | — | L174/180 `대표 재전달 대기` 행 + `badge-amber` | L199·202/205·208 | 됨 |
| `invest-sim--result.html` | 현황표 th 배지 없음(HEAD 도 없음) | L376 | L389 ×2 | 됨 |
| `_fig/invest-assets*` 4 · `_fig/invest-profit*` 4 · `_fig/invest-sim--result` | 0 | 7 | 7 | 됨 |

## 확인 4 — 빌더가 밝힌 「하지 않은 것·다르게 한 것」 4건과 지시 밖 변경

| 빌더 항목 | 근거 | 판정 |
|---|---|---|
| `verify_sim.js` 미실행 | `verify_sim_result.json` 09-02 03:12 그대로 · `sim_facts.json` 08-31 21:01 그대로 | 사실 |
| 시연본 미재생성 | `payhug-investor-prototype/index.html` 09-02 01:51 · 옛 라벨 48건 · 그 레포 assets 09-02 | 사실 |
| 주석 2곳 삭제 | `build_app.py` diff 에서 `/* 소문자 d 표기는 잠정이다 …` 2줄 · `(p.pend ? PEND_BADGE : '')` 삭제. `sync_assets_static.py` diff 에서 같은 주석 2줄 + `# 대표 재전달 대기 표기 —` 1줄 + `PEND_BADGE`·`PEND_ROW` + `pend` 인자 삭제 | 사실 · 설명 주석 1줄은 보고 누락 |
| 검증기 2종 기간 종속 수정 | `verify_crossscreen.py`: xlsx 파일명 하드코딩 3곳 → `BX.PRESETS`·`BX.profit_file`·`BX.status_file` 파생. `sim_facts.py`: `_DEF.replace('@@WKFROM@@', …).replace('@@ASOF@@', …)` 1줄 + `cardTySub` + assert 문구 | 사실 (`amtOdd` 등 나머지 diff 는 09-02 교차검증 라운드 것) |
| 지시 밖 변경 더 있나 | payhug 레포 09-04 수정 파일 = 생성기 6 + 검증기 5 + `sim_facts.py` + 결과 json 2. investor-admin 09-04 수정 파일 = `app.html` + 낱장 15 + xlsx 14 + PDF 1. `README.md`·`index.html`·`archive.html`·`assets/shots/*.webp`·문서 화면 10종은 09-04 아님 | 결과 json 2건 외 없음 |
| 「투자금액 (원)→투자실행액 (원)」이 diff 에 보임 | 9/1 13:47 사용자 지시(「투자실행액으로 투자금액도 통일해」). `app.before.html`(09-02) 에 이미 `투자실행액 (원)` 3 · `투자금액` 0 | 이전 라운드 것 · 5단계 변경 아님 |

## 확인 5 — 빌더 건수(생성기 69 · 낱장 91 · 검증기 34)

| 묶음 | 빌더 | `git diff` `+`줄의 새 라벨 출현 | 비고 |
|---|---|---|---|
| 생성기 6종 | 69 | 86 (`build_app` 43 · `sync_assets` 5 · `sync_profit` 9 · `build_sim` 13 · `build_xlsx` 13 · `build_docs` 3) | 빌더는 「수정 자리」 단위(예: `build_docs` th 3칸 = 1건), 검사는 「출현」 단위. HEAD 기준 diff 라 이전 라운드 치환도 섞임 |
| 낱장 15종 | 91 | 98 (자산 4×10 · 수익 4×8 · 시뮬 13 · 증명서 3 · xls 3+3+2+2) | 자산·수익·증명서·xls 는 빌더 수와 일치, 시뮬 결과 11 대 13 |
| 검증기 6종 | 34 | 48 | 단위·라운드 혼재로 정확 대조 불가 |

판정: **단위가 달라 정확 대조 불가** · 파일별 규모는 빌더 표와 어긋나지 않음. 빌더 보고 안에서 `verify_final_terms.py` 항목이 한 표는 7건(I7·I8·I9·I11·I20·I21·I24), 다른 표는 6건(I8 없음)으로 서로 다름.

## 판정

**전건 이행.** 지시 표 12행 모두 산출물(app · 낱장 15 · `_fig` 33 · xlsx 14 · PDF)에서 확인. 「손대지 말 것」 7항목 전부 지켜짐. 지시 밖 변경은 빌더가 밝힌 검증기 6종·주석·상수 삭제 외에 검증 결과 json 2건(실행 부산물)뿐이며, 화면 문자열·숫자·CSS·메뉴·문서 화면에는 없음.

### 안 된 것

- 없음. (범위 밖으로 남은 것: `verify_sim.js` 미실행 · `sim_facts.json` 8/31 판 · 시연본 미재생성 — 빌더가 밝힘, 지시 목록 밖)
