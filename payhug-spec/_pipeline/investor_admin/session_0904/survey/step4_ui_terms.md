# 4단계 — 프론트 화면 옛 표기 잔존 조사

조사 범위 3곳. `node_modules`·`.git` 제외. 파일 수정 0건.

| 범위 | 경로 | 파일 수 |
|---|---|---|
| ① 투자자 어드민 레포 | `/Users/semi/cursor/payhug-investor-admin` (루트 · `assets/` · `scripts/`) | HTML 46 · md 2 · css 2 · py 2 · json 1 |
| ② Figma 용 HTML | `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/_fig/*.html` | 33 |
| ③ 화면 생성기 | `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/build_app.py` | 1 |

정본 대조 기준: `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/final_terms.json` (9/3 20:13) · `alias_table.py`. 이 정본은 이미 `d · D · PD · PY_a · PY_t` 체계이고 하루 갈래(`_{d−1}` · `_d`) 행이 없다.

## 1. 결론

| 판정 | 내용 |
|---|---|
| 화면 라벨·툴팁·엑셀머리글·증명서 | **옛 표기 4종이 남아 있다** — `S입금부족율`(열머리·툴팁 앵커·증명서·엑셀), 툴팁 `PMR × 365 ÷ PwD` + 행 `PwD`, 툴팁 `PY<sub>MR</sub>`, 툴팁 `실적치`. 화면 파일 14벌 + `app.html` + 생성기 4종 |
| 표본 구간 툴팁 | 루트는 `선정산일 d-20 ~ d-11 표본`, `_fig` 는 `선정산일 D-20 ~ D-11 표본`. 둘 다 새 문면(「기준일 d 의 20일 전 ~ 11일 전」)이 아니다. `_fig` 는 8/31 12:33 동기화본이라 루트보다 한 판 오래됐다 |
| 문서 화면 | `steps-all` · `glossary` · `calc` · `terms-edit` · `final-terms` 5벌이 정본보다 오래된 판에서 나왔다. `steps-all`(9/2 03:03)은 9/1 규칙(`wD` · `PwD` · `PY_MR` · `wPY_MR` · `d−1` 하루 갈래) 그대로. `calc` · `terms-edit` · `final-terms`(9/2 23:48)는 대조표 우열이 `D` 로 바뀌었으나 하루 갈래 `_d` 행과 본문 `PwD` · `PY_{MR}` · `wPY_{MR}` 이 남아 있다 |
| 원천 | `build_calc.py` 는 옛 기호를 코드에 직접 들고 있어(L26 · 56-62 · 84-139) 재생성만으로 안 지워진다. `steps-all` 은 데이터 파일 `meeting_0901/steps_all.json` 이, `glossary` 는 원고 `glossary_manuscript.md` 가, `terms-edit` 은 `termsdoc_seed.json` 의 `symbol` 필드(`B_d` · `A_d` · `M_d` · `D_d` · `MR_d` · `Y_d`)가 원천이다 |
| 0건 패턴 | `상환예정일` · `조회일자` · `조회 기준일` · `Y_e` · `PY_MR`(평문) · 「하루 갈래」(문자열) — 범위 ①②③ 모두 0건 |
| 메뉴 | 사이드바 메뉴 라벨(투자 자산 · 투자 수익 · 투자 시뮬레이션 등)에는 옛 기호 없음. 「메뉴」 표시 대상 0건 |
| 손대지 않는 자리 | 대표 원문 인용(`quote` 필드 · `<pre class="calc quote">` · `<q>`)의 `w금융일수 = Σ Ai x Di / Σ Ai` · `D = 현재일자` · `표본집합: 선정산일이 D-20부터 D-11인 …` — sha256 잠금 인용이라 유지. 아래 표에서 「원문 인용 · 유지」로 표시 |

## 2. 화면 — 라벨 · 툴팁 · 엑셀 머리글 · 증명서

바꿀 표기는 지시문의 새 기호·용어에서 도출한다. `S입금부족율` 열머리는 같은 행의 `W금융일수` · `Ty수익율`(지시 grep 밖)과 한 묶음이라 열머리 셋을 함께 결정해야 한다 — §6 참고.

### 2-1. 투자 자산 계열 (원천 `build_app.py` → `sync_assets_static.py` 정적화)

| 파일:줄 | 현재 표기 | 바꿀 표기 | 종류 |
|---|---|---|---|
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/build_app.py:1300` | `POP_S = {of:'선정산일 d-20 ~ d-11 표본'…}` | `선정산일이 기준일 d 의 20일 전 ~ 11일 전 표본` | 툴팁 (원천) |
| `…/build_app.py:1772` · `:1801` | `popTh('S입금부족율', POP_S)` | `popTh('입금부족률', …)` — 기호 병기 시 `LR` | 라벨 (원천) |
| `…/build_app.py:1836` | `<th>W금융일수</th><th>S입금부족율</th><th>Ty수익율</th>` (가맹점별 표) | `S입금부족율` → `입금부족률` | 라벨 (원천) |
| `…/build_app.py:2328` | `<th class="num">W금융일수</th><th class="num">S입금부족율</th><th class="num">Ty수익율</th>` (시뮬레이션 현황표) | `S입금부족율` → `입금부족률` | 라벨 (원천) |
| `…/build_app.py:2835` · `:2853` | `{v:'S입금부족율', c:'c-head r'}` (엑셀 미리보기 머리글) | `입금부족률` | 엑셀머리글 (원천) |
| `…/sync_assets_static.py:187` | `('S입금부족율', '선정산일 d-20 ~ d-11 표본', POP_N_S, 1)` | 위와 같음 | 툴팁·라벨 (정적화 원천) |
| `/Users/semi/cursor/payhug-investor-admin/app.html:1852` | `선정산일 d-20 ~ d-11 표본` | → 산출 | 툴팁 |
| `…/app.html:2310` · `:2339` · `:2374` · `:2601` · `:2864` · `:3369` · `:3387` | `S입금부족율` | → 산출 | 라벨·엑셀머리글 |
| `/Users/semi/cursor/payhug-investor-admin/invest-assets.html:168` · `:230` | 툴팁 앵커 `S입금부족율` + 패널 `선정산일 d-20 ~ d-11 표본` | → 산출 | 라벨·툴팁 |
| `…/invest-assets--download.html:178` · `:240` | 같음 | → 산출 | 라벨·툴팁 |
| `…/invest-assets--cert-confirm.html:184` · `:246` | 같음 | → 산출 | 라벨·툴팁 |
| `…/invest-assets--empty.html:169` · `:206` | 같음 | → 산출 | 라벨·툴팁 |
| `/Users/semi/cursor/payhug-investor-admin/certificate.html:175` | `<th>S입금부족율</th>` | `입금부족률` | 증명서 (정적 파일 자체가 원천) |
| `…/build_docs.py:213` | `<th class="n">S입금부족율</th>` (증명서 PDF 표) | `입금부족률` | 증명서 PDF (원천) |
| `…/build_xlsx.py:261` · `:280` | `put_header(… 'W금융일수', 'S입금부족율', 'Ty수익율' …)` | `S입금부족율` → `입금부족률` | 엑셀머리글 (xlsx 원천) |
| `…/build_xlsx.py:271` | 주석행 `W금융일수·S입금부족율·Ty수익율은 투자실행액에만 산정.` | 같은 치환 | 엑셀 각주 (원천) |
| `/Users/semi/cursor/payhug-investor-admin/xls-assets-status.html:134` | `<td class="c-head r">S입금부족율</td>` | → 산출 | 엑셀머리글 |
| `…/xls-assets-merchant.html:134` | 같음 | → 산출 | 엑셀머리글 |

### 2-2. 투자 수익 · 시뮬레이션 계열 (원천 `build_app.py` → `sync_profit_static.py` · `build_sim_static.py`)

| 파일:줄 | 현재 표기 | 바꿀 표기 | 종류 |
|---|---|---|---|
| `…/build_app.py:1974` · `:2269` | 툴팁 패널 `PMR × 365 ÷ PwD` | `PMR × 365 ÷ PD` | 툴팁 (원천) |
| `…/build_app.py:1976` · `:2271` | 툴팁 행 `PwD` = `투자실행금 가중평균 금융일수` | `PD` = `조회기간 가중평균 금융일수` | 툴팁 (원천) |
| `…/build_app.py:1979` · `:2274` | 툴팁 행 `실적치 · PMR 계통` | `관찰된 값 · PMR 계통` | 툴팁 (원천) |
| `…/build_app.py:1983` · `:2278` | 툴팁 패널 `( PY<sub>MR</sub> × PA ) ÷ ( PA + PEC )` | `( PY<sub>a</sub> × PA ) ÷ ( PA + PEC )` | 툴팁 (원천) |
| `…/build_app.py:2372` | `fx(R.PwD, 2) + '<span class="avg-sub">가중평균</span>'` | 변수명은 내부값이라 무관. 부제 `가중평균` 은 유지 | 라벨 (참고) |
| `…/sync_profit_static.py:164` · `:166` · `:171` · `:193` | 위 4건과 같은 문자열 | 같은 치환 | 툴팁 (정적화 원천) |
| `…/build_sim_static.py:144` · `:276` · `:278` · `:283` | 위 4건과 같은 문자열 | 같은 치환 | 툴팁 (정적화 원천) |
| `…/build_sim_static.py:246` | `<th class="num">S입금부족율</th>` | `입금부족률` | 라벨 (정적화 원천) |
| `/Users/semi/cursor/payhug-investor-admin/app.html:2512-2521` · `:2805-2814` | 툴팁 4건 | → 산출 | 툴팁 |
| `…/invest-profit.html:170` · `:174` | `PMR × 365 ÷ PwD` · `PwD` 행 · `실적치` · `PY<sub>MR</sub>` | → 산출 | 툴팁 |
| `…/invest-profit--weekly.html:176` · `:180` | 같음 | → 산출 | 툴팁 |
| `…/invest-profit--monthly.html:176` · `:180` | 같음 | → 산출 | 툴팁 |
| `…/invest-profit--empty.html:176` · `:180` | 같음 | → 산출 | 툴팁 |
| `…/invest-sim--result.html:341` | `<th>S입금부족율</th>` | → 산출 | 라벨 |
| `…/invest-sim--result.html:372` · `:376` | 툴팁 4건 | → 산출 | 툴팁 |

### 2-3. `build_app.py` · `app.html` 주석 (화면에 안 보임 · 일관성용)

| 파일:줄 | 현재 표기 | 바꿀 표기 | 종류 |
|---|---|---|---|
| `…/build_app.py:1121` | `Ty수익율 = (투자 수익 / 투자실행금 x 100) x 365 / W금융일수.` | `PY_a = PMR × 365 ÷ PD` | 주석 |
| `…/build_app.py:1129` · `:1131` · `:1865` · `:1892-1895` · `:3483` | `PwD` (7건) | `PD` | 주석 |
| `…/build_app.py:1293` · `:2065` · `:3445` | `S입금부족율` | `입금부족률 LR` | 주석 |
| `…/build_app.py:2029` | `M<sub>d−1,&thinsp;i</sub>·B<sub>d−1,&thinsp;i</sub>·PSA·PSM·PSD·PSMR·PSC` | `M_i · B_i · PA · PM · PD · PMR · PEC` | 주석 |
| `…/build_app.py:2030` | `소문자 d 는 오늘 날짜다. d−1 은 … 정산예정일이 어제인 대상정산금채권 집합` | `d 는 기준일. 일별 표 한 행은 P 가 1일인 경우` | 주석 |
| `…/build_app.py:2084` | `투자수익 M<sub>d−1, i</sub> · 상환액 B<sub>d−1, i</sub>` | `M_i · B_i` | 주석 |
| `…/build_app.py:176` · `:1091` · `:1296` · `:2039-2052`(7건) | `실측` (치수·도수분포 측정 의미) | 해당 없음 — 수익률의 「관찰된」 과 다른 뜻 | 주석 |
| `/Users/semi/cursor/payhug-investor-admin/app.html:1297` · `:1483` · `:1485` · `:1845` · `:2403` · `:2430-2433` · `:2565-2566` · `:2620` · `:2908` | 위 주석의 산출 | → 산출 | 주석 |

## 3. Figma 용 HTML — `_fig/` (원천 = 레포 루트 → `prep_fig.py sync`)

`prep_fig.py:22` 가 `/Users/semi/cursor/payhug-investor-admin` 을 읽어 `_fig/` 에 복사한다. 8/31 12:33 동기화본이라 툴팁 표본 구간이 대문자 `D-20 ~ D-11` 로 남아 루트(`d-20 ~ d-11`)와도 다르다. 루트를 고친 뒤 sync 를 다시 돌리면 아래 전건이 따라온다.

| 파일:줄 | 현재 표기 | 바꿀 표기 | 종류 |
|---|---|---|---|
| `…/_fig/invest-assets.html:171` · `:232` | `S입금부족율` + `선정산일 D-20 ~ D-11 표본` | `입금부족률` + `선정산일이 기준일 d 의 20일 전 ~ 11일 전 표본` | 라벨·툴팁 |
| `…/_fig/invest-assets--download.html:181` · `:242` | 같음 | 같음 | 라벨·툴팁 |
| `…/_fig/invest-assets--cert-confirm.html:187` · `:248` | 같음 | 같음 | 라벨·툴팁 |
| `…/_fig/invest-assets--empty.html:171` · `:208` | 같음 | 같음 | 라벨·툴팁 |
| `…/_fig/certificate.html:177` | `<th>S입금부족율</th>` | `입금부족률` | 증명서 |
| `…/_fig/invest-profit.html:172` · `:176` | `PMR × 365 ÷ PwD` · `PwD` 행 · `실적치` · `PY<sub>MR</sub>` | `PD` · `조회기간 가중평균 금융일수` · `관찰된 값` · `PY<sub>a</sub>` | 툴팁 |
| `…/_fig/invest-profit--weekly.html:178` · `:182` | 같음 | 같음 | 툴팁 |
| `…/_fig/invest-profit--monthly.html:178` · `:182` | 같음 | 같음 | 툴팁 |
| `…/_fig/invest-profit--empty.html:178` · `:182` | 같음 | 같음 | 툴팁 |
| `…/_fig/invest-sim--result.html:335` | `<th>S입금부족율</th>` | `입금부족률` | 라벨 |
| `…/_fig/invest-sim--result.html:366` · `:370` | 툴팁 4건 | 같음 | 툴팁 |
| `…/_fig/xls-assets-status.html:136` | `S입금부족율` | `입금부족률` | 엑셀머리글 |
| `…/_fig/xls-assets-merchant.html:136` | `S입금부족율` | `입금부족률` | 엑셀머리글 |
| `…/_fig/password.html:12` · `--done:12` · `--weak:12` · `--error:12` | `실측` (CSS 치수 주석) | 해당 없음 | 주석 |
| `…/_fig/assets/base.css` (21) | `실측` (디자인 토큰 주석) | 해당 없음 | 주석 |

`_fig/xls-profit-daily.html` · `xls-profit-status.html` 은 지시 grep 패턴 0건. 열머리 `W금융일수` · `Ty수익율` 만 있다(§6).

## 4. 문서 화면

### 4-1. `steps-all.html` — 본문이 114번 한 줄 (543 토큰)

원천: `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/meeting_0901/steps_all.json` (9/2 03:03) → `build_steps_html.py` → `steps_all.fragment.html` → 레포. 9/1 규칙 그대로라 정본과 체계가 다르다.

| 파일:줄 (원천) | 현재 표기 | 바꿀 표기 | 종류 |
|---|---|---|---|
| `steps_all.json:34` · `:57` · `:1045` · `:1082` → `steps-all.html:114` 대조표 첫 행 · 요약 카드 | `D → d 현재일자` · `기준일 d = 현재일자` | `기준일` | 문서 |
| `steps_all.json:253-3549`(28줄) → 대조표 행 · 카드 라벨 | `w금융일수 → wD` · `W금융일수 — 투자실행액 행 wD = …` | `w금융일수 → D` · 라벨 `가중평균 금융일수 D` | 문서 |
| `steps_all.json:254-6131`(26줄) | `wD` (26) | `D` | 문서 |
| `steps_all.json:4019-6389`(12줄) | `PSD → PwD` · `④ = PMR × 365 ÷ PwD` · `(PM ÷ PA) × 365 ÷ PwD` | `PD` | 문서 |
| `steps-all.html:114` 대조표 끝 2행 | `④ → PY<sub>MR</sub>` · `⑤ → wPY<sub>MR</sub>` | `PY_a` · `PY_t` | 문서 |
| `steps_all.json:311-3226`(34줄) | `S입금부족율 → LR` · 카드 라벨 `S입금부족율 — 투자실행액 행` | 대조표 좌열은 유지 · 카드 라벨은 `입금부족률 LR` | 문서 |
| `steps_all.json:319` · `:1010` · `:1016` | `선정산일이 d−20 ~ d−11 인 대상정산금채권` | `선정산일이 기준일 d 의 20일 전 ~ 11일 전인 대상정산금채권` | 문서 |
| `steps_all.json:1052` | `대표 정의서는 표본 구간을 D-20부터 D-11 로 적었다` | 원문 인용 · 유지 | 문서 |
| `steps-all.html:114` 대조표 「하루」 5행 | `SB_{D−1} → B_{d−1}` · `SA_{D−1} → A_{d−1}` · `SM_{D−1} → M_{d−1}` · `SD_{D−1} → wD_{d−1}` · `전일자(D−1) … → Y_{MR,d−1}` | 정본 대조표(`alias_table.rows()`)에 없는 행 — 삭제 | 문서 |
| `steps_all.json:3921-6212` (`A_{d−1}` 12 · `M_{d−1}` 10 · `B_{d−1}` 8 · `R_{d−1}` 21 · `A_{d−1,i}` 49 · `D_{d−1,i}` 21 · `M_{d−1,i}` 8 · `B_{d−1,i}` 7 · `(d-1)` 63 · `<sub>d−1</sub>` 70) | 일별 표 카드의 하루 갈래 기호 `A<sub>d−1</sub> = Σ A<sub>d−1,i</sub>` 등 | 낱건은 `A_i` · `M_i` · `B_i` · `D_i`(범위 첨자 없이 조건 문장), 하루 합계는 P 가 1일인 `PA` · `PM` · `PB` · `PMR` · `PD` · `PY_a` — 정본 규칙 3 「범위는 P 로만」. 표기 형태는 확인 필요 | 문서 |
| `steps_all.json:4362-6072`(7줄) | 라벨 `전일자(D−1) 대상정산금채권의 …` | `정산예정일이 그 날인 대상정산금채권의 …` | 문서 |
| `build_steps_html.py:164` | 주석 `평문 괄호 표기(Ai · wD(d-1))` | `Ai · PD` | 주석 |

### 4-2. `glossary.html` (424 토큰) — 원천 `glossary_manuscript.md` (9/2 03:10) → `build_glossary.py`

기호 사전 절 전체가 9/1 이전 체계(`D = 현재일자` · `SB_{d−1}` · `PwD` · 용어 카드 이름 `w금융일수 (투자 자산 · 잔액)`)다. 원고 줄은 대표 건만 적는다.

| 파일:줄 (원천) | 현재 표기 | 바꿀 표기 | 종류 |
|---|---|---|---|
| `glossary_manuscript.md:28` · `:30` · `:75` · `:95` … (75줄, 90건) → `glossary.html:232-2957` (116건) | 용어 카드 이름 `w금융일수 (투자 자산 · 잔액)` · `w금융일수 (일별 배치 · 하루치)` · 본문 `w금융일수` | `가중평균 금융일수 D` · 하루치 카드는 P 범위로 합침(확인 필요) | 문서 |
| `build_glossary.py:594` · `:598` | `ALIAS` 표 `'w금융일수': 'w금융일수 (투자 자산 · 잔액)'` · `'w금융일수 SD': 'w금융일수 (일별 배치 · 하루치)'` | 카드 이름 바뀌면 함께 | 주석(코드 표) |
| `glossary_manuscript.md:43` · `:88` · `:89` · `:310` … (39줄, 44건) → `glossary.html:275-2959` (49건) | 용어 카드 `S입금부족율` · 본문 | `입금부족률 LR` | 문서 |
| `glossary_manuscript.md:102` · `:840` · `:1234` … (30줄, 38건) → `glossary.html:333-2943` (41건) | `PwD` · `PwD (기간 집계)` | `PD` | 문서 |
| `glossary_manuscript.md:1932` · `:1956` · `:3199` → `glossary.html:1800` · `:1823` · `:2768` | `D = 현재일자` (1800 · 2768 은 `<pre class="calc quote">` 원문 인용) | 1823 xref 만 `기준일`; 인용 2건 유지 | 문서 |
| `glossary_manuscript.md:1931` · `:3308` → `glossary.html:1799` · `:2805` | `표본집합: 선정산일이 D-20부터 D-11인 …` (원문 인용 · 대표 대화 인용) | 원문 인용 · 유지 | 문서 |
| `glossary_manuscript.md:310` · `:1595` · `:1938-1944` · `:3192` · `:3297` · `:3327` · `:3646` → `glossary.html:541` · `:1535` 등 | `선정산일이 d-20 ~ d-11 사이인 채권` | `선정산일이 기준일 d 의 20일 전 ~ 11일 전인 채권` | 문서 |
| `glossary_manuscript.md:91-95` · `:2045-2049` · `:3246-3250` 등 (`B_{d-1}` 10 · `A_{d-1}` 28 · `M_{d-1}` 12 · `R_{d-1}` 12 · `D_{d-1}` 15 · `_{d-1,i}` 50 · `(D-1)` 26) → `glossary.html:281-2413` (`<sub>d−1</sub>` 82 · `<sub>d−1,i</sub>` 50 · `d-1` 53) | 용어 카드 `상환액 (일별 배치 · 하루치) SB<sub>d−1</sub>` · 기호 사전 `B_{d−1,i}` · `A_{d−1,i}` · `D_{d−1,i}` · `M_{d−1,i}` | 낱건 `B_i` · `A_i` · `D_i` · `M_i`, 하루 합계는 P 범위. 기호 사전 절 재서술 필요(확인 필요) | 문서 |
| `glossary_manuscript.md:2462` · `:2464` · `:3603-3604` → `glossary.html:2204` · `:2205` | `유량식은 실적, 잔액식은 계획` · `아래(유량식)가 실적치` | `관찰된 값` | 문서 |
| `glossary_manuscript.md:1243` → `glossary.html:1266` | `2025년 실적으로 재 놓은 값` | `2025년 관찰된 값` | 문서 |
| `glossary_manuscript.md:26` · `:28` → `glossary.html:372` | `w금융일수 실측(카드사 2.0일 · …)` | `관찰된 플랫폼별 금융일수` (확인 필요) | 문서 |
| `glossary_manuscript.md:10` · `:398-409` · `:623` … (16줄) → `glossary.html:367` · `:371` · `:616-623` … | `실측` (캡처 치수 · DB 액면 · 배포 검증 의미, 16건) | 해당 없음 | 문서 |

### 4-3. `calc.html` (58 토큰) — 원천 `build_calc.py` (9/3 16:31, 코드에 직접 기재) → `calc.fragment.html`

| 파일:줄 (원천) | 현재 표기 | 바꿀 표기 | 종류 |
|---|---|---|---|
| `build_calc.py:26` · `:56-62` → `calc.html:67` | 변수 `wD` · 카드 `가중평균 금융일수 wD = ( Σ A_i × D_i ) ÷ ( Σ A_i )` · `Y_r = r × 365 ÷ wD` · `곧 wD = Σ w_i D_i` | `D` | 문서 |
| `build_calc.py:23-24` · `:105` · `:115-116` · `:120-122` → `calc.html:67` | `PwD` 카드 · `PY_{MR} = PM ÷ PA × 365 ÷ PwD` | `PD` | 문서 |
| `build_calc.py:120` · `:124` · `:137-139` → `calc.html:67-69` | `PY_{MR}` · `wPY_{MR}` · 검산 `wPY_{MR} = 7,185,359 ÷ (PA+PEC)` | `PY_a` · `PY_t` | 문서 |
| `build_calc.py:64` · `:67` → `calc.html:67` | `i 는 선정산일이 d−20 ~ d−11 인 채권` · `선정산일이 d−20 ~ d−11 인 열흘치 채권` | `선정산일이 기준일 d 의 20일 전 ~ 11일 전인 채권` | 문서 |
| `build_calc.py:84-100` → `calc.html:67` (`<sub>d−1</sub>` 20 · `d−1` 8) | 일별 표 카드 `A_{d−1}` · `M_{d−1}` · `B_{d−1}` · `MR_{d−1}` · `wD_{d−1}` · `Y_{MR,d−1}` · `i ∈ d−1` | 하루 갈래 기호 없음 — P 가 1일인 `PA` · `PM` · `PB` · `PMR` · `PD` · `PY_a` (확인 필요) | 문서 |
| `build_calc.py:109` · `:111` · `:117` → `calc.html:67` | `PA = ( Σ A_{d−1} )` · `PM = ( Σ M_{d−1} )` · `PEC = ( Σ EC_{d−1} )` | `PA = Σ A_i (i ∈ P)` · `PM = Σ M_i (i ∈ P)` · `PEC = 조회기간 각 날 EC 의 합` | 문서 |
| `build_calc.py:100` → `calc.html:67` | `그 하루의 실적치.` | `그 하루의 관찰된 값.` | 문서 |
| `calc.html:67` 대조표 (원천 = 9/2 판 `final_terms.json`) | `SB<sub>D−1</sub> → B<sub>d</sub>` · `SA → A_d` · `SM → M_d` · `전일자(D−1) … ty수익율 → Y_d` (`<sub>D−1</sub>` 5) | 현재 `alias_table.rows()` 에 없는 행 — 재생성 시 사라짐 | 문서 |
| `calc.html:67` 대조표 좌열 `w금융일수 → D` · `S입금부족율 → LR` | 옛 표기 열 | 유지 (대조표 좌열이 제 자리) | 문서 |
| `calc.html:67` 대입표 `투자 자산 · 가맹점별 투자자산 · S입금부족율` · `일별 투자수익 · W금융일수` | 화면 열머리 인용 | 화면 열머리 결정에 따라감(§6) | 문서 |

### 4-4. `terms-edit.html` (53 토큰) — 원천 `termsdoc_seed.json` (9/2 23:45) → `build_termsedit.py`

| 파일:줄 (원천) | 현재 표기 | 바꿀 표기 | 종류 |
|---|---|---|---|
| `termsdoc_seed.json:456-462` · `:486-492` · `:516-522` · `:560-566` · `:546-552` · `:623` · `:793-800` · `:854` (`symbol` · `formula` 필드 `B_d` · `A_d` · `M_d` · `D_d` · `MR_d` · `Y_d`, 30건) → `terms-edit.html:272` | 하루 갈래 `_d` 첨자 (9/1 규칙에도 정본에도 없는 표기) | 낱건 `B_i` · `A_i` · `M_i` · `D_i` + 조건 문장, 합계는 P 범위 (확인 필요) | 문서 |
| `termsdoc_seed.json:439` · `:454` · `:469` … (13줄) `quote` 필드 `전일자(D-1) 대상정산금채권의 …(SBD-1)` | 대표 원문 인용 | 원문 인용 · 유지 | 문서 |
| `termsdoc_seed.json:201-202` · `:379` · `:557-558` · `:726` `quote` `w금융일수 = Σ Ai x Di / Σ Ai` · `term: 전일자 대상정산금채권의 w금융일수 (SDD-1)` | 원문 인용 (`quote`) · 용어 이름 (`term`) | `quote` 유지 · `term` 은 `가중평균 금융일수` (확인 필요 — term 도 원문 제목이면 유지) | 문서 |
| `termsdoc_seed.json:238` · `:350` → `terms-edit.html:272` | `quote: D = 현재일자` · note `단독 D 는 현재일자` | quote 유지 · note 는 `기준일` | 문서 |
| `termsdoc_seed.json:59` · `:313` · `:340-351` → `terms-edit.html:272` | `d-20 ~ d-11 고정` · 열머리 인용 `S입금부족율 · 선정산일 d-20 ~ d-11 표본` | `기준일 d 의 20일 전 ~ 11일 전` | 문서 |
| `termsdoc_seed.json:336` `quote: 표본집합: 선정산일이 D-20부터 D-11인 …` | 원문 인용 | 유지 | 문서 |
| `termsdoc_seed.json:385` · `:616` · `:621` → `terms-edit.html:272` | `실적치다 (3차 미팅 확정)` · `실적치라 부족액이 이미 반영` | `관찰된 값` | 문서 |
| `termsdoc_seed.json:208` · `:283` → `terms-edit.html:272` | `금액 실측 카드 42.83%` · `2025년 365일 실측` | `관찰된 금액 구성비` · `2025년 365일 관찰값` (확인 필요) | 문서 |
| `termsdoc_seed.json:48` · `:57` · `:306-311` · `:340` → `terms-edit.html:272` | `term: S입금부족율` · 열머리 인용 | `입금부족률` (quote 는 유지) | 문서 |
| `terms-edit.html:252` 대조표 | `SB<sub>D−1</sub> → B<sub>d</sub>` 등 5행 · `w금융일수 → D` · `S입금부족율 → LR` | 하루 5행은 재생성 시 사라짐 · 좌열 옛 표기는 유지 | 문서 |
| `build_termsedit.py:350` → `terms-edit.html:292` | `SUBRE = /(…)(wPY|SMR|PY|wD|MR|SA|SB|SD|SL|SM|…)_/` 첨자 조판 정규식 | 새 기호(`PY_a` · `PY_t` · `Y_r` · `D_i`)가 걸리도록 목록 정리. 화면 문자열 아님 | 주석(코드) |
| `build_termsedit.py:359` → `terms-edit.html:301` | 주석 `원고 표기 _i · _{d−1}` | `_i` 만 | 주석 |
| `terms-edit.html:273` | `wD` (base64 이미지 데이터 안 우연 일치, 121건) | 오탐 — 해당 없음 | — |

### 4-5. `final-terms.html` (9 토큰) — 원천 `final_terms.json` + `alias_table.py` → `build_final.py`

| 파일:줄 | 현재 표기 | 바꿀 표기 | 종류 |
|---|---|---|---|
| `final-terms.html:55` 대조표 | `SB<sub>D−1</sub> → B<sub>d</sub>` · `SA → A_d` · `SM → M_d` · `전일자(D−1) … → Y_d` (`<sub>D−1</sub>` 5) | 현재 `alias_table.rows()` 13행에 없음 — 재생성 시 사라짐 | 문서 |
| `final-terms.html:55` 범위표 | `A_i · A<sub>d</sub> · PA` 등 「하루 d」 열 | 현재 `branch_rows()` 는 하루 열이 빈 칸 — 재생성 시 사라짐 | 문서 |
| `final-terms.html:55` 본문 | `정산예정일이 전일자인 채권들의 실적치다.` | `관찰된 값` | 문서 |
| `final-terms.html:55` 대조표 좌열 | `w금융일수 → D` · `S입금부족율 → LR` | 유지 | 문서 |
| `final-terms.html:55` 본문 인용 | `투자 자산 화면의 「W금융일수」 3.04일` · `「Ty수익율」 13.21%` | 화면 열머리 결정에 따라감(§6) | 문서 |

### 4-6. `feasibility.html` · `capability.html` · `inquiry.html` · `ceo-questions.html` · `archive.html`

| 파일:줄 (원천 → 산출) | 현재 표기 | 바꿀 표기 | 종류 |
|---|---|---|---|
| `feasibility.md:252` → `feasibility.html:738` | `선정산일 D-20 ~ D-11 구간 필터` | `선정산일이 기준일 d 의 20일 전 ~ 11일 전` | 문서 |
| `feasibility.md:260` → `feasibility.html:741` | `정산예정일이 D-1인 채권 합` | `정산예정일이 조회기간 P 에 드는 채권 합` | 문서 |
| `feasibility.md:105-106` · `:183-184` · `:235-236` · `:263` · `:280` → `feasibility.html:472` · `:671` · `:673` · `:726-727` · `:744` · `:754` | `w금융일수` (8) | `가중평균 금융일수 D` | 문서 |
| `feasibility.md:105` · `:253` · `:292` → `feasibility.html:475` · `:739` · `:770` | `S입금부족율` (3) | `입금부족률 LR` | 문서 |
| `feasibility.html:771` · `:777` · `:844` · `:830-878` · `:932` · `:955` | `D-19 D-20 D-21` · `D-11 D-24` (개발 확인 문항 번호) | 오탐 — 문항 ID | — |
| `feasibility.md:40` · `:61` → `feasibility.html:375` · `:790` | `실측` (파일 기준 집계 의미) | 해당 없음 | 문서 |
| `capability_manuscript.md:41-757` (10줄) → `capability.html:388` · `:513` · `:523` · `:680` · `:1098` · `:1131` · `:1207` · `:1416` · `:1500` | `S입금부족율` (10) | `입금부족률 LR` | 문서 |
| `capability_manuscript.md:134-728` (7줄) → `capability.html:524` · `:634` · `:647` · `:1208` · `:1278` · `:1327` · `:1379` · `:1465` | `w금융일수` (8) · `할인율 × (365 / w금융일수)` | `가중평균 금융일수 D` · `r × 365 ÷ D` | 문서 |
| `capability_manuscript.md:531` → `capability.html:1117` | `가맹점 영업 실적` | 오탐 — 영업실적 의미 | — |
| `capability_manuscript.md:257` · `:499` · `:706` → `capability.html:337` · `:710` | `실측` (플랫폼 만기 측정) | `관찰된 플랫폼별 금융일수` (확인 필요) | 문서 |
| `ceo_inquiry.md:29` → `inquiry.html:126` | `<q>… w금융일수(SDD-1), ty수익율 …</q>` | 원문 인용 · 유지 | 문서 |
| `ceo_inquiry.md:87` · `:103` → `inquiry.html:254` · `:279` · `:376` · `:427` · `:440` | `w금융일수` | `가중평균 금융일수 D` | 문서 |
| `ceo_inquiry.md:87` · `:104` → `inquiry.html:254` · `:280` · `:427` · `:441` | `S입금부족율` · `표본집합(선정산일 D-20 ~ D-11)` | `입금부족률 LR` · `선정산일이 기준일 d 의 20일 전 ~ 11일 전` | 문서 |
| `ceo_inquiry.md:25` · `:28` → `inquiry.html:117` · `:121` · `:371` · `:373` | `같은 실적을 분모만 바꿔 읽으면` | `같은 관찰된 값을` | 문서 |
| `inquiry.html:313` · `:180` | `D-11`(문항 ID) · `이전 결정 D-1`(결정 ID) | 오탐 | — |
| `ceo_inquiry.md:85` · `:139` → `inquiry.html:248` · `:326` · `:426` · `:429` · `:482` | `실측` (화면 대조 의미) | 해당 없음 | 문서 |
| `ceoq_seed.json:270` · `:274` → `ceo-questions.html:125` | `SD(d-1)처럼 날짜 쪽에 소문자` · `d-1 = 정산예정일이 어제인 채권 집합` | 대표에게 묻는 문항 문면 — 정본 규칙 3(P 로만)에 맞춰 재서술 (확인 필요) | 문서 |
| `ceoq_seed.json:308` → `ceo-questions.html:125` | `S입금부족률 표본을 … 선정산일이 d-20부터 d-11이다` | `입금부족률 LR … 기준일 d 의 20일 전부터 11일 전` | 문서 |
| `ceoq_seed.json:425` · `:429` → `ceo-questions.html:125` | `PwD 3.108481` · `PwD 3.107588` | `PD` | 문서 |
| `ceoq_seed.json:22` · `:117` · `:227` · `:407` → `ceo-questions.html:125` | `실측` (샘플 조사 · 배포본 집계 의미) | 해당 없음 | 문서 |
| `build_archive.py:14-202` (26) → `archive.html:37-265` | `실측` (배포 검증 · 디자인 토큰 의미) · `Ty수익율`(37 · 246 파일 설명) | 해당 없음 · 파일 설명은 §6 | 문서 |

## 5. 레포 안내 · CSS · 기타

| 파일:줄 | 현재 표기 | 바꿀 표기 | 종류 |
|---|---|---|---|
| `/Users/semi/cursor/payhug-investor-admin/README.md:3` · `:89` · `:92` · `:118` (원천 `build_readme.py:2-247`) | `실측` (디자인 측정 의미) | 해당 없음 | 문서 |
| `…/DESIGN_REF.md:1` · `:3` · `:75` · `:228` | `실측` (디자인 측정 의미) | 해당 없음 | 문서 |
| `…/assets/base.css:3-601` (21) | `실측` (토큰 주석) | 해당 없음 | 주석 |
| `…/assets/base.css:116` | `wD` (base64 폰트 데이터) | 오탐 | — |
| `…/password.html:12` · `--done` · `--weak` · `--error` | `실측` (CSS 주석) | 해당 없음 | 주석 |
| `…/verify_0828_result.json:156` | `실측 67건` | 해당 없음 | — |
| `…/.claude/worktrees/nostalgic-lichterman-0e321d/` (detached HEAD `dcdc634` 8/28) | 옛 작업본 전체 — `glossary` 110 · `feasibility` 23 · `capability` 17 · `inquiry` 17 · `app` 12 등 | 조사 범위 밖 옛 체크아웃. 정리 여부 결정 필요 | — |

## 6. 지시 grep 밖 — 함께 결정해야 하는 자리

| 항목 | 어디 | 건수 | 왜 같이 보나 |
|---|---|---|---|
| 열머리 `W금융일수` · `Ty수익율` | 투자 자산 현황표 · 가맹점별 표 · 증명서 · 엑셀 4종 · 시뮬레이션 · 일별 표 · 요약 카드 `Ty수익율` 라벨 · 부제 `W금융일수 3.04일 기준` · 툴팁 `⑤W금융일수` | 레포 화면 파일 `W금융일수` 44 · `Ty수익율` 62 (문서 제외), `_fig` 32 · `build_app.py` 41 | `S입금부족율` 과 같은 행에 있는 스토리보드 열머리. 하나만 `입금부족률` 로 바꾸면 행이 두 체계로 갈린다. 용어 정본은 「가중평균 금융일수」·「예상 연환산수익률 Y_r」·「관찰된 연환산수익률 PY_a」 |
| 표본 툴팁 소문자 `d-20 ~ d-11` | 루트 `invest-assets*` 4벌 · `app.html:1852` · `build_app.py:1300` · `sync_assets_static.py:187` | 10 | 지시 grep 은 대문자 `D-20` 만. 소문자도 새 문면(「기준일 d 의 20일 전 ~ 11일 전」)이 아니라 같이 적었다 |
| `sync_assets_static.py:184-185` · `:196` | 주석 `소문자 d 표기는 잠정` · 툴팁 행 `표기 d · 미확정` + `미확정` 배지 | 1 | `d` 가 확정됐으면 툴팁의 「표기 d 미확정」 행과 배지가 근거를 잃는다 |
| `ty수익율` 소문자 | `glossary.html` 144 · `steps-all` 113 · `terms-edit` 24 · `feasibility` 8 · `inquiry` 10 · `calc` 4 · `final-terms` 4 · `capability` 4 | 311 | 대조표 좌열(`ty수익율 → Y_r`)과 원문 인용은 유지, 본문 서술은 `예상 연환산수익률 Y_r` |

## 7. 파일별 건수

오탐(base64 안 `wD` · CSS 색상 토큰 · 문항 ID) 제외. `실측` 은 「관찰된」 대상(수익률·비율 의미)만 센다.

### 7-1. `/Users/semi/cursor/payhug-investor-admin`

| 파일 | 건수 | 주 토큰 | 원천 |
|---|---|---|---|
| `steps-all.html` | 543 | `d-1` 계열 344 · `w금융일수` 104 · `S입금부족` 35 · `wD` 28 · `PwD` 13 · `현재일자` 8 · `<sub>D−1</sub>` 5 · `MR` 첨자 2 · `wPY` 1 | `meeting_0901/steps_all.json` |
| `glossary.html` | 424 | `w금융일수` 117 · `d-1` 계열 185 · `S입금부족` 49 · `PwD` 41 · `실측` 19(관찰 의미 1 · 치수 의미 18) · `실적` 6 · `현재일자` 3 · `D-20/11` 4(인용) | `glossary_manuscript.md` |
| `calc.html` | 58 | `<sub>d−1</sub>` 20 · `d−1` 8 · `MR` 첨자 8 · `wD` 7 · `<sub>D−1</sub>` 5 · `PwD` 3 · `wPY` 3 · `S입금부족` 2 · `실적` 1 | `build_calc.py` |
| `terms-edit.html` | 43 | `w금융일수` 10 · `S입금부족` 8 · `d-1/d−1` 10 · `<sub>D−1</sub>` 5 · `실적` 3 · `실측` 2 · `현재일자` 2 · `D-20/11` 2(인용) · `wPY` 1 · `_d` 첨자 30(별도) | `termsdoc_seed.json` |
| `app.html` | 43 | `PwD` 17 · `S입금부족` 8 · `실측`(주석) 8 · `d−1` 5 · `실적` 2 · `MR` 첨자 2 · `d-11` 1 | `build_app.py` |
| `feasibility.html` | 15 | `w금융일수` 8 · `S입금부족` 3 · `D-20/11` 2 · `D-1` 1 · `실측` 2(치수) | `feasibility.md` |
| `inquiry.html` | 19 | `w금융일수` 6 · `실적` 4 · `S입금부족` 4 · `D-20/11` 4 · `실측` 5(치수 · 제외) | `ceo_inquiry.md` |
| `capability.html` | 21 | `S입금부족` 10 · `w금융일수` 8 · `실측` 3 · `실적` 1(오탐) | `capability_manuscript.md` |
| `ceo-questions.html` | 6 | `d-1` 3 · `PwD` 2 · `S입금부족` 1 (`실측` 4 는 조사 의미) | `ceoq_seed.json` |
| `final-terms.html` | 9 | `<sub>D−1</sub>` 5 · `S입금부족` 2 · `w금융일수` 1 · `실적` 1 | `final_terms.json` (구판) |
| `invest-assets.html` · `--download` · `--cert-confirm` · `--empty` | 각 4 | `S입금부족` 2 · `d-11` 2 | `build_app.py` → `sync_assets_static.py` |
| `invest-profit.html` · `--weekly` · `--monthly` · `--empty` | 각 4 | `PwD` 2 · `실적` 1 · `MR` 첨자 1 | `build_app.py` → `sync_profit_static.py` |
| `invest-sim--result.html` | 5 | `PwD` 2 · `S입금부족` 1 · `실적` 1 · `MR` 첨자 1 | `build_sim_static.py` |
| `certificate.html` | 1 | `S입금부족` | 파일 자체 (`build_docs.py:213` 은 PDF) |
| `xls-assets-status.html` · `xls-assets-merchant.html` | 각 1 | `S입금부족` | `build_xlsx.py` |
| `archive.html` · `README.md` · `DESIGN_REF.md` · `base.css` · `password*.html` | 0 (관찰된 대상) | `실측` 은 전부 디자인·검증 의미 | — |
| `index.html` · `login.html` · `merchants*` · `contracts*` · `acquisition*` · `coocon*` · `review.html` · `invest-sim.html` · `xls-profit-*` · `assets/template.html` · `assets/docs/*.txt` · `scripts/*.py` | 0 | — | — |
| **합계 (관찰 대상)** | **1,221** | — | — |

### 7-2. `_fig/`

| 파일 | 건수 |
|---|---|
| `invest-assets.html` · `--download` · `--cert-confirm` · `--empty` | 각 6 (`S입금부족` 2 · `D-20` 2 · `D-11` 2) |
| `invest-profit.html` · `--weekly` · `--monthly` · `--empty` | 각 4 (`PwD` 2 · `실적` 1 · `MR` 첨자 1) |
| `invest-sim--result.html` | 5 |
| `certificate.html` · `xls-assets-status.html` · `xls-assets-merchant.html` | 각 1 |
| `password*.html` 4 · `assets/base.css` | `실측` 치수 의미 · 제외 |
| **합계** | **48** |

### 7-3. 생성기

| 파일 | 화면 문자열 | 주석 |
|---|---|---|
| `build_app.py` | 15줄 (L1300 · 1772 · 1801 · 1836 · 1974 · 1976 · 1979 · 1983 · 2269 · 2271 · 2274 · 2278 · 2328 · 2835 · 2853) | 20 |
| `sync_assets_static.py` | 1 (L187) | 4 (L65 · 178 · 184-185 · 196) |
| `sync_profit_static.py` | 4 (L164 · 166 · 171 · 193) | 0 |
| `build_sim_static.py` | 5 (L144 · 246 · 276 · 278 · 283) | 0 |
| `build_xlsx.py` | 3 (L261 · 271 · 280) | 2 (L138 · 306) |
| `build_docs.py` | 1 (L213) | 0 |
| `build_calc.py` | 64 (L26 · 56-64 · 84-100 · 109-139 — 변수명·카드 문자열 혼재) | 1 (L23) |
| `build_glossary.py` | 5 (L594-600 ALIAS 표) | 3 (L70 · 640) |
| `build_termsedit.py` | 0 | 3 (L350 · 359) |
| `build_steps_html.py` | 0 | 1 (L164) |
| `build_final.py` | 0 | 1 (L42) |
