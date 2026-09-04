# 교차검증 A — 배포 실물 · 지시 이행 · Figma 맵 · 기호정리표

2026-09-04 22:54~23:08 KST. 다른 조의 보고서는 열지 않았고 산출물·배포 실물·git·docx 만 봤습니다. 이 셸의 `grep` 은 ugrep 이라 한글 문맥 검색은 python 으로 했습니다.

## 불일치·미이행

| # | 항목 | 확인한 사실 | 판정 | 고칠 것 |
|---|---|---|---|---|
| 1 | **E 깃 저장** | payhug 레포에서 `session_0904/` 와 `NEXT_SESSION.md` 가 `??`(untracked). 마지막 커밋 `26a255a` 2026-09-01 22:03. `investor_admin/` 아래 수정 파일 40개 이상도 미커밋 | **미이행(진행 중)** | `payhug-spec/_pipeline/investor_admin/session_0904`·`NEXT_SESSION.md`·수정 생성기 전부 커밋 |
| 2 | **N orders_final.md** | `session_0904/reports/orders_mid.md` 만 있음(22:11). `orders_final.md` 없음 | **진행 중** | 최종 판정 산출 |
| 3 | **H ⑤ 옛 산식 잔존 — `calc.html`** | 전체본 배포에 포함(200, 42,338 B). `wPY_MR = PY_MR × PA ÷ (PA + PEC)` 등 `PY<sub>MR` 8곳. 파일 시각 09-02 23:48, 이번 세션 미갱신 | **부분** | `build_calc.py` 로 재생성(⑤ = `PM × 365 ÷ ( Σ( A_i × D_i ) + PEC )`, 기호 `PY_a`/`PY_t`) 또는 배포 명단에서 제외 |
| 4 | **시연본 `xls-` 7건** (판정 기준 문면은 0건) | 실체는 다운로드 버튼 `data-act="xls-open"` 4개(`data-xls`·`data-mount="ia-xls-merchant"`·`pf-xls1`·`pf-xls2`)와 핸들러 `ACT['xls-open']` → `pullFile('assets/xlsx/', meta.file)`. 미리보기 격자(`class="sheet`·`sheetRow`·`xlsPreview`) 0건. `<link href="assets/sheet.css">` 는 남아 있고 그 파일의 클래스 중 `.back-link` 1곳만 쓰임 | **이행(실체 기준)** · 기준 문구는 「미리보기 뷰 0건」으로 읽어야 맞음 | 없음. `sheet.css` 정리는 선택 |
| 5 | **「대표 DM 16:45」 행 문구 변경** | `app.html` 2곳·시연본 1곳의 값이 `실적치 · SMR 계통` → `관찰된 값 · PMR 계통`. 원문(`dm_0831/dm_20260831_raw.md` 16:45:02)은 「위는 예상치 아래는 실제 결과치… smr」이라 행 값은 직접 인용이 아니라 요약. 「대표 DM」 행 4개는 그대로 있음 | **확인 필요** — 「대표 DM 행 손대지 않기」 문면에는 걸리고, 지시 A 의 옛 표기 `실적치` 교체에는 부합 | 사용자 판단. 원문 직접 인용으로 되돌리려면 「예상치 ↔ 실제 결과치(smr)」 |
| 6 | **`figma_map_investor.json` 메타** | `source_commit` = `1693bd3` + 「워킹트리 미커밋」. 실제로는 그 워킹트리가 `b4f41b3` 로 커밋됨(교체 9화면 diff +147/−147 = 맵 기재와 일치) | **부분** (내용 일치, 메타 낡음) | `source_commit`·`head_at_completion` 을 `b4f41b3` 으로 |
| 7 | **F 작업 순서** | 판정 근거가 「보고 순서」인데 O(최종 보고)가 아직 없음. 파일 시각: 화면 18:09~21:58 → 기호정리표 docx 21:55 → invest-profit 21:58 → login 22:14 → figma_map 22:24 | **대기** | O 의 보고 순서로 판정 |
| 8 | **감사 중 재생성** | `prep_fig.py`·`_fig/*.html` 이 22:56 에 다시 써짐(감사 시작 뒤). 재확인 결과 IMPORT 24·`_fig` 24 파일 동일, 금지 5종 0 | 참고 | 없음 |

배포 실물·라벨·⑤ 값·로그인·Figma 맵·기호정리표 본문에는 불일치가 없습니다.

## 1. Vercel 배포 실물

### 1-1. 전체본 `payhug-investor-demo.vercel.app` (main `b4f41b3`)

1회차(22:54)에 6개 파일 모두 200. 재시도 없음. 로컬 레포 워킹트리는 클린, `HEAD` = `origin/main` = `b4f41b3`.

| 파일 | HTTP | 바이트 | sha256 로컬 = 배포 |
|---|---|---|---|
| invest-assets.html | 200 | 20,046 | 같음 `0fc6cb74…` |
| invest-profit.html | 200 | 19,700 | 같음 `0465d0f0…` |
| certificate.html | 200 | 14,764 | 같음 `70440696…` |
| login.html | 200 | 6,156 | 같음 `a93010f8…` |
| app.html | 200 | 245,015 | 같음 `0b80f5ee…` |
| index.html | 200 | 27,310 | 같음 `5b123f27…` |

라벨 건수 (`<q>`·`calc quote`·「대표 DM」 행 제외해도 수치 동일):

| 파일 | 입금부족률 | 가중평균 금융일수 | 예상 연환산수익률 | 연환산수익률* | S입금부족율 | W금융일수 | Ty수익율 | PwD |
|---|---|---|---|---|---|---|---|---|
| invest-assets.html | 2 | 3 | 3 | 3 | 0 | 0 | 0 | 0 |
| invest-profit.html | 0 | 3 | 0 | 5 | 0 | 0 | 0 | 0 |
| certificate.html | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 0 |
| login.html | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| app.html | 6 | 16 | 9 | 21 | 2 | 7 | 5 | 16 |

\* `연환산수익률` 은 `예상 연환산수익률` 을 포함한 건수. `app.html` 의 옛 표기는 전부 `<script>` 안 `/* */` 주석·JS 식별자(`var PwD`)이고, 사용자에게 보이는 텍스트에는 0건입니다. `W금융일수` 1건은 「대표 DM 16:27」 행(`365 ÷ W금융일수 = 1년 회전수`)입니다. `PY_MR`·`실적치`·`d-20 ~ d-11` 은 5개 파일 모두 0.

`invest-profit.html` ⑤·④:

| 확인 항목 | 실물 |
|---|---|
| ⑤ 값 | L175 `<div class="summary-value">3.30<span class="unit">%</span></div>` (문자열 `3.30%` 는 마크업 때문에 0건, 값은 3.30). `2.32%` 0건 |
| ⑤ 툴팁 머리글 | L174 `PY<sub>t</sub> · 투자자산 대비 연환산수익률 (관찰된 값) · PM × 365 ÷ ( Σ( A<sub>i</sub> × D<sub>i</sub> ) + PEC )` |
| ⑤ 툴팁 행 | `PY_a 투자실행금액 대비 연환산수익률 (관찰된 값) · 4.13%` / `Σ( A_i × D_i ) 556,626,436원` / `PEC 기간 순현금 · 140,000,000원` / `EC 순현금 · 20,000,000원 × 7일` / `미확정 대표 확인 대기` |
| ④ 툴팁 행 | `PMR 기간 투자수익율 · PM ÷ PA = 0.035003%` / `PM 기간 투자수익 · 62,977원` / `PA 기간 투자실행금 · 179,916,643원` / `PD 기간 가중평균 금융일수 · 3.09일` |
| 검산 | 62,977 × 365 ÷ (556,626,436 + 140,000,000) = 3.2997% → 3.30. `ledger_facts.json` `weekTyAssetRaw` 3.299662 와 같음 |
| 배지 | `미확정` 7 · `대표 확인 대기` 1 |

행 문자열은 `<span>PEC</span><span class="tip-green">기간 순현금 · …</span>` 꼴이라 태그를 벗기면 지시 문구와 같습니다.

`login.html`:

| 문구 | 배포 login.html | 실물 `payhug-admin-web/app/login/page.tsx` |
|---|---|---|
| 관리자 로그인 | 1 | L112 |
| 이 페이지는 관리자 전용입니다 | 1 (`안내: 이 페이지는 관리자 전용입니다.`) | L186 |
| placeholder | `휴대전화번호 또는 사업자번호` · `비밀번호` | L132 · L153 |
| 투자자 어드민 | 0 | 없음 |
| 비밀번호 찾기 | 0 | 없음 |

### 1-2. 시연본 `payhug-investor-prototype.vercel.app` (main `75bc47b`)

| 항목 | 실물 |
|---|---|
| index.html | 200, 191,943 B, sha256 `178f3c1e…` = 로컬 클론 `~/cursor/payhug-investor-prototype/index.html`(클린 트리, HEAD = origin/main = `75bc47b` 22:51) |
| 사이드바 `data-menu` 7 | `invest-assets` 투자 자산 · `invest-returns` 투자 수익 · `merchants` 가맹점 · `receivables` 정산채권 양수 · `contracts` 계약기록 · `kcoon` 쿠콘 관리 현금 · `password` 비밀번호 변경 |
| 금지어 | `invest-sim` 0 · `시뮬` 0 · `미리보기` 0 · `sheetRow` 0 · `화면 갤러리` 0 · `glossary` 0 · **`xls-` 7** (위 불일치 #4 — 다운로드 버튼·핸들러) |
| 새 라벨 | 입금부족률 3 · 가중평균 금융일수 9 · 예상 연환산수익률 5 · 연환산수익률 10 |
| 옛 라벨 | S입금부족율 1 · W금융일수 7 · Ty수익율 5 · PwD 7 — 전부 `<script>` 주석·식별자, 1건은 「대표 DM 16:27」 행. 보이는 텍스트 0 |
| ⑤ | 정적 문자열에는 없음(JS 계산). 로컬 클론 파일을 Chrome 헤드리스로 `#invest-profit` 렌더 → `투자자산 대비 … => 3.30%`, `투자실행금액 대비 => 4.13%`, `미확정` 7, `대표 확인 대기` 1, `Σ( A` 2, `기간 순현금` 1 |
| 로그인 카드 | `관리자 로그인` 1 · `이 페이지는 관리자 전용입니다` 1 · `투자자 어드민` 0 · `비밀번호 찾기` 0 |
| 화면 | `data-screen` 9: invest-assets · certificate · invest-profit · merchants · acquisition-list · contracts · coocon · password · login |

xlsx 표본 3건 (`assets/xlsx/…`, `XLSX` 맵 → `pullFile`):

| 파일 | HTTP | 바이트 | sha256 = 어드민 레포 assets | 머리글 |
|---|---|---|---|---|
| 투자자산현황_2026-08-27_2026-08-27.xlsx | 200 | 5,737 | 같음 | 자산 구분 · 금액 (원) · **가중평균 금융일수** · **입금부족률** · **예상 연환산수익률** · 비중 · 보관 |
| 투자수익현황_2026-08-20_2026-08-26.xlsx | 200 | 5,471 | 같음 | 항목/값 … `연환산수익률 (투자실행금액 대비)` 0.0413 · `연환산수익률 (투자자산 대비)` **0.033** (서식 `0.00%`) |
| 일별투자수익_2026-08-20_2026-08-26.xlsx | 200 | 5,876 | 같음 | 정산예정일 · 상환액 · 투자실행금 · 투자 수익 · **가중평균 금융일수** · **연환산수익률** |

어드민 레포 `assets/xlsx` 14개 전부 옛 라벨 0. `assets/docs/투자자산증명서_20260827.pdf` 본문에 `가중평균 금융일수`·`입금부족률`·`예상 연환산수익률`(줄바꿈 분리), 옛 표기 0. 두 배포 모두 200 (244,871 B).

## 2. 사용자 지시 A~O

| # | 지시 | 확인한 것 | 상태 |
|---|---|---|---|
| A | UI 용어 수정 | 9화면·xls 4·sim 2·xlsx 14·pdf·`_fig/` 24 에 옛 표기 0(주석·JS 식별자 제외). `PY_MR`·`실적치`·`d-20 ~ d-11` 은 통합본 문서 페이지(`calc.html`·`final-terms.html`·`glossary.html`·`terms-edit.html`·`steps-all.html`)에 남음 — 화면 라벨·툴팁·엑셀·증명서 범위 밖 | **끝** (문서 페이지는 #3 참고) |
| B | 배포 | 전체본 = `b4f41b3` 바이트 동일 6/6, 시연본 = `75bc47b` 바이트 동일. `scripts/sync_prototype.py` 22:22 · `gate_prototype.js` 22:29 · `sync_prototype.sh` 08-28 | **끝** |
| C | 툴팁 기호마다 용어명·산식 | ④⑤ 툴팁이 있는 파일 = `기간 순현금` 보유 화면: invest-profit 4종 각 1 + app.html 2 + invest-sim--result 1 → ⑤ 6 + ④ 6 = 12. 카드 툴팁(`계약된 할인율 · 0.11%`) 시연본 2. 기호 `PMR`·`PM`·`PA`·`PD`·`PY_a`·`PEC`·`EC` 에 용어명·값 | **끝** |
| D | ⑤ 검증 후 워드·HTML 확정본 | `기호정리표_20260904_2155.docx/.html` 존재, 셀 텍스트 43행 완전 일치. `verify/xv_A·B·C` 3건 존재. `final_terms.json`(21:53) `Σ( A_i × D_i ) + PEC` 6곳 | **끝** |
| E | 정리·깃 저장·넥스트세션 md | `session_0904/{artifact,qa,reports,survey,verify}` · `investor_admin/NEXT_SESSION.md`(22:32) 존재. **payhug 레포 미커밋**(#1) | **진행 중** |
| F | UI·Figma 먼저, 용어정의 다음 | 보고 순서로 판정하는 지시. 시각은 #7 | **대기** |
| G | 표기 통일 | docx: `PD = Σ( A_i × D_i ) ÷ Σ A_i  i ∈ P` · 개념행 D·MR·A·M·B·L 산식 · `PA = Σ A_i  i ∈ P`·`PM`·`PB`·`PD`·`PEC` 같은 규칙 · `PY_t` Σ( A_i × D_i ) 꼴 · `PA × PD` 0 | **끝** |
| H | ⑤ 산식 교체 2.32→3.30 | 화면 3.30(정적·렌더 둘 다) · xlsx 0.033 · `ledger_facts.json` `weekTyAsset` 3.30 · 검산 엑셀 `입력 C19 = ROUND(B13×B9/(B9+B15),6)` = PY_a × Σ(A×D) ÷ (Σ(A×D)+PEC), `읽는 법 R73` 에 새 산식 · 배지 「미확정」·「대표 확인 대기」. **`calc.html` 옛 산식 잔존**(#3). 검산 엑셀 라벨은 `wPYMR`·`PwD`·`W금융일수` 21·`S입금부족율` 26 옛 기호(산식은 새 것) | **부분** |
| I | Figma 프로토타입 화면만, index·coocon 금지 | `prep_fig.py` IMPORT 24 에 index·coocon 없음. 맵 `not_imported` 에 둘 다 있음, `retired` 에 `3373:2`(갤러리)·`3341:2`(쿠콘) 「삭제 완료」. Figma 실물은 도구 밖 | **끝(맵 기준)** |
| J | 교차검증 2건 | 이 보고가 그중 1건 | **진행 중** |
| K | 시뮬레이션 시연본·Figma 숨김, 통합본 유지 | 시연본 `invest-sim` 0·메뉴 7. 통합본 `app.html` `data-menu="invest-sim"` 유지, `invest-sim` 29. 맵 `3376:2`·`3378:2` retired | **끝** |
| L | 엑셀 미리보기 제거, 다운로드 유지 | 시연본 미리보기 격자 0, 다운로드 버튼 4 → 실물 xlsx 200. 통합본 `xls-*` 4뷰 각 10건 유지. 맵 `3370:2`·`3372:2`·`3375:2`·`3377:2` retired | **끝** (#4) |
| M | 로그인 실물로 되돌림, Figma 프레임 삭제 | `1693bd3` login.html: 「투자자 어드민」·「비밀번호 찾기」·placeholder 「'-' 없이 숫자만 입력」. HEAD: page.tsx L112/132/153/186 과 같음. 통합본 로그인 카드도 같음(`투자자 어드민` 1건은 통합본 표제 `<h1>PayHug 투자자 어드민 — 화면 설계(안)`). 맵 `3371:2` retired 「이 라운드에서 삭제」 | **끝(맵 기준)** |
| N | 추적 에이전트 | `ORDERS_0904.md`·`orders_mid.md` 있음, `orders_final.md` 없음 | **진행 중** |
| O | 최종 보고 | 없음 | **대기** |

### 손대지 않는 것

| 항목 | 확인한 것 | 판정 |
|---|---|---|
| 사이드바 라벨 | `git diff 1693bd3 -- app.html \| grep nav-item` 출력 0줄. 라벨 목록 diff 없음 | 유지 |
| 대표 원문 인용 | `<q>`·`calc quote`·`quote` 는 1693bd3·HEAD 모두 0. 「대표 DM」 행: app.html 6→5 — 줄어든 1건은 `/* 소문자 d 표기는 잠정이다 — 대표 DM 15:15 … */` JS 주석(내부 메모, 인용 행 아님). 행 4개 유지, 그중 「16:45」 2곳 값 문구 변경(#5) | 유지 · #5 확인 필요 |
| 통합본 시뮬·엑셀 미리보기 | `app.html` `invest-sim` 29 · `xls-assets-status` 등 각 10 · `sheetRow` 2 · `미리보기` 4 · `data-menu` 8(invest-sim 포함) | 유지 |
| payhug-io 금지 | 두 레포 remote 모두 `github.com/Joo2n/…` | 준수 |

## 3. Figma 맵 (`figma_map_investor.json` 22:24 · 실물은 도구 밖)

| 항목 | 확인한 것 |
|---|---|
| 파일·페이지 | `Tcf69tIciGxmlqCIuRb0iI` · `3066:328` 「[투자자 어드민] 제안서 첨부용」 |
| `frames` 24 | 노드 `3405:2`(01 투자 자산) `3403:2`(02 증명서) `3404:2`(03 투자 수익) `3340:2` `3345:2` `3344:2` `3351:2` `3409:2` `3407:2` `3408:2` `3410:2` `3412:2` `3411:2` `3355:2` `3356:2` `3357:2` `3361:2` `3360:2` `3362:2` `3363:2` `3365:2` `3366:2` `3367:2` `3368:2`. 중복 이름·노드 0. 폭 전부 1440. x ∈ {0, 1600, 3200, 4800} · y ∈ {0, 2613, 5226, 7839, 10452, 13065, 15678, 18291} |
| `prep_fig.py` IMPORT 24 | `frames` 24 와 **집합 동일**(차집합 양쪽 ∅). 22:56 재작성 뒤 재확인도 동일 |
| `not_imported` 16 | app · archive · capability · **coocon** · feasibility · glossary · **index** · inquiry · **invest-sim--result** · **invest-sim** · **login** · review · **xls-assets-merchant** · **xls-assets-status** · **xls-profit-daily** · **xls-profit-status** — 요구 9종 전부 포함 |
| `retired` | **13건** 전부 `status` 「삭제 완료」. 이 세션 대상 9건: coocon `3341:2` · index `3373:2` · invest-sim `3376:2` · `3378:2` · xls `3370:2` `3372:2` `3375:2` `3377:2` · login `3371:2`. 앞 8건은 `deleted_at` 「착수 시점 get_metadata 에서 이미 조회되지 않음 · 이 라운드 삭제 실행 없음」, login 만 「이 라운드에서 삭제」. 나머지 4건(coocon--confirm·datepicker·page2·downloaded)은 이전 회차. 지시문의 「retired 8」과 건수가 다름 — `deleted_orphans` 가 8건(`3189:14605` 외 7) |
| `verification` | frames_on_page 24 · forbidden_names 0(패턴 갤러리·쿠콘 관리 현금·시뮬레이션·엑셀 산출물·로그인) · old_labels_in_replaced_9 0 · invest_profit_5 「3.30% (3404:2)」 — 맵의 자기 기술이며 실물 대조는 **도구 밖** |
| `source_commit` | `1693bd3` + 워킹트리 → 실제 `b4f41b3` (#6) |
| `_fig/` 스테이징 | 24 파일, index·coocon·login·invest-sim·xls 0. 라벨 다중집합이 레포 `invest-profit.html` 과 동일 |

## 4. 기호정리표 `~/Downloads/payhug_용어정의서/기호정리표_20260904_2155.docx`

| 항목 | 확인한 것 | 판정 |
|---|---|---|
| 표 | **3개**, 행 **8 / 29 / 6** (표 1 이름 짓는 규칙 · 표 2 전체 기호 · 표 3 기호 변경내역). 본문 단락: 「일별 표의 한 행은 P 가 1일인 경우다. 주별은 7일, 월별은 그 달의 일수다.」 | 이행 |
| PD 분모 | `PD = Σ( A_i × D_i ) ÷ Σ A_i   i ∈ P` — `i` 는 실제 아래첨자 런. 개념행 `D = Σ( A_i × D_i ) ÷ Σ A_i`. `PA` 분모 표기 0 | 이행 |
| PY_t | `PY_t = PM × 365 ÷ ( Σ( A_i × D_i ) + PEC )   i ∈ P` + 둘째 줄 `= PY_a × Σ( A_i × D_i ) ÷ ( Σ( A_i × D_i ) + PEC )`. `PA × PD` 0 | 이행 |
| 개념 행 산식 | `A = 순지급액 × ( 1 − r )` · `L = 미지급금 − 과지급금` · `M = 채권매입수수료 − max( 0, L )` · `B = 순지급액 − max( 0, L )` · `MR = M ÷ A` · `D = Σ( A_i × D_i ) ÷ Σ A_i` | 이행 |
| 접두 Y | `연환산을 뜻한다 ( × 365 ÷ 금융일수 )` | 이행 |
| 대표 채택 11곳 | 첨자 r 「예상 수익률을 나타낼 때 쓴다」 · a/t 「관찰된 값」 2 · r 행 「계약된 할인율」 · L·L_i 「입금부족액」 2 · EC 「d 마감시점 쿠콘 가상계좌의 현금 잔액」 · Σ A_i + EC 「i 는 정산예정일이 d 보다 뒤인 대상정산금채권」 · PA `i ∈ P`(5곳) · 표 3 「관찰된 연환산수익률 기호 변경」 | 이행 |
| 유지 2곳 | 「조회대상기간 중 누계」 0 · 「표본에 속하는」 0 | 이행 |
| 금지어 | 상환예정일 0 · 조회일자 0 · 신설 0 · 추가했습니다 0 · 기존에는 0 · 종전에는 0 · 이번에 0 | 이행 |
| HTML 쌍둥이 | `기호정리표_20260904_2155.html` 표 3 · 43행, 셀 텍스트 diff **0** | 이행 |
| 아티팩트 | `claude.ai/code/artifact/f0f651d2…` 는 200 이지만 껍데기 HTML(15,295 B, 본문은 스크립트 로드) → **도구 밖**. 로컬 원본 `session_0904/artifact/ceo_review.html` 과 43행 diff **0** | 대체 확인 |
| 참고 | 표 2 `D_i` 행 「선정산일로부터 정산예정일까지의 **한편 넣기** 일수 / 08-24 선정산 · 08-26 정산예정이면 2」 — docx·html·ceo_review 세 벌이 같아 원고 문구. 낱말 「한편 넣기」는 확인 필요 | 확인 필요 |

## 판정

배포 실물(전체본 `b4f41b3`·시연본 `75bc47b`)·화면 라벨·⑤ 3.30·툴팁 용어명·로그인 실물화·Figma 맵·기호정리표는 지시대로이고, 남은 것은 **E 의 payhug 레포 커밋 미이행, N·O 미완, `calc.html` 옛 ⑤ 산식 잔존, 「대표 DM 16:45」 행 문구 변경(사용자 판단), 맵 `source_commit` 메타 갱신** 다섯입니다.
