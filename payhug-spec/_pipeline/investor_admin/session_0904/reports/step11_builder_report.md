# step11 적용 보고 — 내부 검토 표시 제거 · 「수익 산정 기준」 구역 제거

생성기 `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin` · 출력 레포 `/Users/semi/cursor/payhug-investor-admin`. 커밋·push 없음.

## 1. 뺀 문구 — 화면별 · 생성기 자리

| 화면 | 뺀 것 | 생성기 (현재 줄) |
|---|---|---|
| 투자 자산 카드 「투자실행액」 툴팁 (통합본·낱장 4벌·_fig) | 「대표 DM 16:19 \| 가맹점 매입 1% 차감」 행 · 「미확정 \| 선정산 실행액은 이보다 작다」 행 | `build_app.py:1742-1746` (RENDER['invest-assets']) · 낱장은 원본 마크업에 없음 |
| 투자 자산 카드 「예상 연환산 수익률」 툴팁 (통합본·낱장 4벌) | 「일 환산 \| 미확정」 · 「대표 DM 16:27 \| 365 ÷ W금융일수 = 1년 회전수」 · 「대표 DM 16:45 \| 예상치 · 할인율 계통」 행 | `build_app.py:1752-1758` · `sync_assets_static.py:219-227` `yr_card_tip()` |
| 투자 수익 ④ 「투자실행금액 대비」 툴팁 (통합본·낱장 4벌·시뮬 2벌) | 머리 괄호 「(관찰된 값)」 · 「항등식 \| 할인율 − max(0, 미지급금 − 과지급금) ÷ 투자실행액」 · 「부족액 0 \| 할인율 0.11% ↔ PMR … · 미확정」 · 「대표 DM 16:45 \| 관찰된 값 · PMR 계통」 행 | `build_app.py:1966-1971` (pfRender) · `build_app.py:2263-2268` (simTyTip) · `sync_profit_static.py:161-169` `TIP4` (`TIP4_FIX`·`_R` 삭제) · `build_sim_static.py:265-270` (`TY4_DM` 삭제) |
| 투자 수익 ⑤ 「투자 자산 대비」 툴팁 + 카드 배지 (통합본·낱장 4벌·시뮬 2벌) | 「미확정」 배지 · 「미확정 \| 대표 확인 대기」 행 · 머리·PY_a 행의 「(관찰된 값)」 | `build_app.py:1975-1983` · `build_app.py:2272-2280` · `sync_profit_static.py:183-191` `TIP5` · `build_sim_static.py:274-282` |
| 일별·주별·월별 표 열머리 「투자실행금」(③) 배지·툴팁 (통합본·낱장 4벌·시뮬 결과) | 「미확정」 배지 · 「미확정 \| 대표 재전달 대기」 행 | `build_app.py:1328-1333` `thirdTh()` · `sync_profit_static.py:178-182` `THIRD_TH` · `build_sim_static.py:130-134` |
| 일별·주별·월별 표 열머리 「연환산 수익률」(⑥) 배지·툴팁 (통합본·낱장 4벌·시뮬 결과) | 「미확정」 배지 · 「미확정 \| 대표 재전달 대기」 행 | `build_app.py:1319-1326` `tyTh()` · `sync_profit_static.py:170-177` `TY_TH` · `build_sim_static.py:122-128` |
| 배지·행 상수 자체 | `PEND_BADGE` · `PEND_ROW` · `PEND5_ROW` 정의와 주석 | `build_app.py`(옛 1311-1317 삭제) · `sync_profit_static.py`(옛 177-182 삭제) · `build_sim_static.py`(옛 121-126 삭제) |
| `daily_ledger.py` 상태 상수 | `TY_PENDING` · `TY5_STATUS` · `TY5_SOURCE` · `TY3_STATUS` · `TY3_SOURCE` 삭제. 산식 `TY5_EXPR`(:176) · `TY3_EXPR`(:195) 그대로 | `daily_ledger.py:166-195` |
| `app.html` `<script>` 주석 | 「W금융일수」 6곳 → 화면 라벨 「가중평균 금융일수」(입금부족률 1곳 포함) | `build_app.py:1118 · 1126 · 1290 · 1861 · 1863 · 1884` |

남긴 것(확인): `Y_r · 예상 연환산 수익률 · r × 365 ÷ D` 머리 · 「연환산 \| 일부 기간의 …」 · r · D · 「연 환산 \| 13.21%」 행, `PY_a`/`PY_t` 머리(괄호만 뺌), PMR·PM·PA·PD·PY_a·Σ( A_i × D_i )·PEC·EC 행, 「보유 채권 전체 (회수된 것 포함)」·「선정산일이 오늘 기준 20일 전 ~ 11일 전인 표본」·채권 건수 행, ③ 「번호 \| 상단 현황의 기간 전체 숫자 · 칸 미지목」, ⑥ 「번호 …」·「행 \| 정산예정일이 그 날짜인 보유 채권」. 화면 라벨·메뉴 라벨·값 전부 그대로.

## 2. 「수익 산정 기준」 구역

| 대상 | 처리 |
|---|---|
| 통합본 `app.html` 투자 자산 · 투자 수익 | `build_app.py:49 SHOW_FORMULA = False`. `FORMULA = cut(...) if SHOW_FORMULA else ''`(:50), assert 도 `if SHOW_FORMULA`(:68-69). 템플릿 `{FORMULA}` 줄은 `.replace('\n{FORMULA}', …)`(:645 · :923)로 빈 줄 없이 빠진다 — `</div>` 다음 바로 `</section>` |
| 낱장 invest-assets 4벌 (`invest-assets.html` · `--download` · `--cert-confirm` · `--empty`) | 낱장은 파일 자체가 원본이고 `sync_assets_static.py` 가 제자리 수정한다. `FORMULA_CARD`(:250) · `drop_formula()`(:255)를 `build_assets`(:439) · `build_assets_empty`(:472)에 넣어 카드(`<!-- 수익 산정 기준 -->` 주석 + `<div class="card">` … `</main>` 앞)를 걷어낸다. `--check` 도 같은 함수를 거친다 |
| 낱장 invest-profit 4벌 (`invest-profit.html` · `--empty` · `--monthly` · `--weekly`) | `sync_profit_static.py` 가 제자리 수정. `drop_formula()`(:198)를 `one()`(:340)에 넣음. 주별은 월별을 본으로 뜨므로 함께 빠진다. 주석 변형 `<!-- 산식 안내 카드 -->` 도 같은 정규식이 잡는다 |
| 시뮬 2벌 | 원래 구역이 없다 (`build_sim_static.py` 가 처음부터 생성) |
| `fix12_static.py` | `SHOW_FORMULA = False`(:13). 한 번 쓰는 정정 스크립트라 재생성 순서에 없고, 그 정규식은 `formula-caption` 이 있는 옛 카드만 잡아 지금 낱장엔 효력이 없다 — 낱장 제거는 위 두 sync 스크립트가 맡는다 |
| `</main>` 앞 조판 | 낱장 8벌 전부 `    </div>\n\n  </main>` (원래 카드 앞 빈 줄 하나가 그대로 `</main>` 앞으로 옴). 헤드리스 DOM: `main` 마지막 자식 = 가맹점별 표 / 일별 표, `.formula-grid` 0 |

## 3. 검사 결과

| 검사 | 결과 |
|---|---|
| `python3 sync_assets_static.py --check` | 어긋난 낱장 0 / 11 |
| `sync_profit_static.py --check` | 없음(--check 모드 없음). 본 실행에서 카드↔표 기간 일치 4벌 통과 |
| `python3 verify_final_terms.py` | **151건 · PASS 151 · FAIL 0** |
| `python3 verify_crossscreen.py` | 63건 · 불일치 3 — 셋 다 `glossary.html`(duration 허용 블록 · 대출 어휘 「만기」 · duration 2곳). `glossary.html` 은 손대지 않았고 이번에 재생성되지 않아(아래 build_glossary) **이전과 같은 상태의 기존 FAIL** |
| `bash sync_prototype.sh --dry-run` (게이트 `gate_prototype.js`) | 게이트 통과 · 바깥 통로 0건 · push 안 함. 게이트는 미확정 문구를 기대하지 않아 뒤집을 것 없음 |
| `node verify_shots.js` | 64건 · FAIL 2 — `B4 invest-assets.html · invest-profit.html 거울 이미지 = 원본 이미지`. 거울은 `payhug-investor-glossary` 레포(sync_glossary.sh 가 push 까지 하므로 돌리지 않음). 원본 캡처는 새로 찍혔고 거울이 옛것 |
| `node verify_sim.js` | **92 / 92 ALL PASS** (뒤집은 뒤) |
| `node verify_app.js` · `verify_proto.js` · `verify_identity.js` | 123/123 · 118/118 · 18/18 |
| `node verify_weighting.js` · `verify_toast.js` · `verify_period.js` · `verify_rows.js` · `verify_sync_chain.js` | 28/28 · FAIL 0 · 40/40 · 35/35 · 동기화 됐다 |
| `python3 verify_batch_symbols.py` · `verify_shortfall.py` | FAIL 0 · 통과 |
| `python3 verify_docnums.py` | 위반 24 — HEAD 결과도 `bad: 24`, 변동 없음(문서 페이지 대상) |
| `node capture_shots.js` | 5/5 · 콘솔 에러 0 |
| `python3 build_glossary.py` | **실패(기존)** — `!! 앵커 못 찾음: invest-profit / th:W금융일수`. `NEXT_SESSION.md:48` 에 이미 적힌 미해결 항목. 옛 `shot_rects.json` 으로도 같은 앵커가 안 잡힌다(원고 31개 앵커 중 8개가 전부터 미해결). 추가로 카드 제거로 `invest-assets / div:0.11%` · `h2:수익 산정 기준` 2개가 새로 안 잡힘. `glossary.html` 은 재생성되지 않아 손대지 않은 상태 그대로 |
| `python3 verify_shotmarks.py` | FAIL 45 (HEAD 결과 FAIL 40) — `glossary.html` 의 마커 좌표가 옛 캡처(invest-profit docH 1314) 기준이고 새 캡처는 docH 1200. build_glossary 가 서야 풀린다(위 항목의 결과) |
| 헤드리스 크롬 QA (`step11_qa/qa_tips.js`) | **40 / 40 PASS** — `app.html#invest-assets`·`#invest-profit`·낱장 2벌: 툴팁 4곳(예상 연환산 수익률·가중평균 금융일수·④·⑤) hover 로 뜸(display·높이 실측), 남긴 행 전부 있음, 카드 4종·④⑤ 값 통합본=낱장=원장, 배지 0, 검토 문구 0, 콘솔 오류 0. 캡처 6장 `step11_qa/01~06_*.png` |

### 뒤집은 검사

| 검사 | 줄 | 전 | 후 |
|---|---|---|---|
| `verify_sim.js` [10] | :621-633 | ⑤ 배지 = `SF.pendBadge` · 「대표 확인 대기」 행 있음 · ⑥ 열머리 배지 있음이라야 PASS | 배지 `null` · 툴팁에 「미확정·대기·대표 DM·관찰된 값·항등식·부족액 0·일 환산」 0건 · ⑥ 열머리 = `tyTh()` 글자 (`NO_MARK`) |
| `verify_sim.js` 투자 수익 화면 | :644-646 | 같은 표기 있어야 PASS | 배지 `''` · 검토 문구 0 |
| `verify_sim.js` 낱장 invest-sim--result | :891-893 | 「⑤ 확인 대기 · ⑥ 재전달 대기 같은 표기」 | 「⑤ 배지 없음 · 검토 문구 없음 · ⑥ 열머리 = tyTh()」 |
| `sim_facts.py` | :191-199 · :290-291 | `PEND_BADGE`·`PEND_ROW`·`PEND5_ROW` 를 build_app.py 에서 뽑아 `pendBadge`·`pendRow`·`pend5Row` 로 냄, `PEND_ROW_TEXT in TY_TH_TEXT` assert | 세 키 삭제, `tyThText` 만 냄, assert 는 `badge`·「미확정」·「대기」 없음 |
| `verify_crossscreen.py` | 옛 :255-264 · :387-389 | `daily_ledger.TY5_STATUS` 등을 「미확정에 걸린 자리」로 출력 | 블록 삭제 |

### 잔존 0 확인 (12어: 미확정·대표 확인 대기·대표 재전달·대표 DM·관찰된 값·항등식·부족액 0·일 환산·수익 산정 기준·수수료 배분형·조달이자형·W금융일수)

| 대상 | 결과 |
|---|---|
| `app.html` (본문·`<!-- -->`·`<script>` 주석 포함) | 0 |
| `invest-assets*.html` 4벌 · `invest-profit*.html` 4벌 · `invest-sim*.html` 2벌 | 0 |
| 시연본 dry-run 결과 `/Users/semi/cursor/payhug-investor-prototype/index.html` | 0 |
| `assets/xlsx/*.xlsx` 14벌 (openpyxl 전 셀) | 0 · HEAD 대비 셀 값 차이 0 |
| `assets/docs/투자자산증명서_20260827.pdf` (pypdf 본문) | 0 · HEAD 본문과 같음 |
| `_fig/*.html` 37벌 | 0 |
| 그 밖 낱장 | `calc.html` W금융일수 8 · `final-terms.html` W금융일수 11 (문서 페이지, 대상 밖) 외 0 |

## 4. 원장·값

| 항목 | 값 |
|---|---|
| `ledger_facts.json` md5 시작 | `1bffe2e62d2caf020b81c8b15a5c56bd` |
| `ledger_facts.json` md5 끝 (daily_ledger.py 재실행 후) | `1bffe2e62d2caf020b81c8b15a5c56bd` — 같음 |
| 카드 4종 (투자 자산) | 투자자산 100,000,000원 · 투자실행액 80,000,000원 · 순현금 20,000,000원 · 예상 연환산 수익률 13.21% (가중평균 금융일수 3.04일) |
| ④ 투자실행금액 대비 · ⑤ 투자 자산 대비 (기본 일주일) | 3.99% · 3.19% |
| 통합본 = 낱장 | 카드 4종·④⑤ 헤드리스 대조 일치 |

## 5. 바뀐 파일

`git -C /Users/semi/cursor/payhug-investor-admin status --short` — `app.html` · `invest-assets.html` · `invest-assets--download.html` · `invest-assets--cert-confirm.html` · `invest-assets--empty.html` · `invest-profit.html` · `invest-profit--empty.html` · `invest-profit--monthly.html` · `invest-profit--weekly.html` · `invest-sim--result.html` · `xls-assets-status.html` · `xls-assets-merchant.html` · `xls-profit-status.html` · `xls-profit-daily.html`(생성 시각 줄) · `assets/xlsx/*.xlsx` 14벌(재생성, 셀 값 동일) · `assets/docs/투자자산증명서_20260827.pdf`(재생성, 본문 동일) · `assets/shots/invest-assets.webp` · `assets/shots/invest-profit.webp` · `README.md` 는 내용 동일(재생성) · `.github/workflows/sync-prototype.yml` 은 작업 전부터 M.

`git -C /Users/semi/cursor/payhug diff --name-only -- payhug-spec/_pipeline/investor_admin/_fig` — html 37벌 전부 이름이 뜬다. 내용이 바뀐 **Figma 재임포트 대상 18벌**:
`invest-assets` · `invest-assets--download` · `invest-assets--cert-confirm` · `invest-assets--empty` · `invest-assets--nav-collapsed` · `invest-assets--tip-exec` · `invest-assets--tip-shortfall` · `invest-assets--tip-wavg` · `invest-assets--tip-yield` · `invest-profit` · `invest-profit--empty` · `invest-profit--monthly` · `invest-profit--weekly` · `invest-profit--range-error` · `invest-profit--tip-exec` · `invest-profit--tip-py-exec` · `invest-profit--tip-py-asset` · `invest-profit--tip-yield`.
나머지 19벌(acquisition 7 · contracts 3 · merchants 3 · password 5 · certificate)은 화면 내용 차이가 아니라 커밋본이 `prep_fig.py apply` 상태(capture.js 주입·input→span)였고 이번엔 `sync`·`freeze` 까지만 돌려 원본 상태로 돌아간 차이다.

생성기 쪽 변경: `build_app.py` · `sync_assets_static.py` · `sync_profit_static.py` · `build_sim_static.py` · `daily_ledger.py` · `sim_facts.py` · `sim_facts.json` · `verify_sim.js` · `verify_crossscreen.py` · `fix12_static.py` · `shot_rects.json` · `검산_투자자어드민_20260901.xlsx`(재생성) · `verify_*_result.json`.

## 6. 문서 페이지 8종 잔존 (손대지 않음)

| 파일 | 합계 | 내역 |
|---|---|---|
| `capability.html` | 46 | 미확정 22 · 수익 산정 기준 7 · 수수료 배분형 1 · 조달이자형 1 · W금융일수 15 |
| `inquiry.html` | 14 | 수익 산정 기준 2 · 수수료 배분형 2 · 조달이자형 6 · W금융일수 4 |
| `glossary.html` | 113 | 미확정 36 · 대표 재전달 2 · 대표 DM 25 · 일 환산 4 · 수익 산정 기준 10 · 수수료 배분형 2 · 조달이자형 4 · W금융일수 30 |
| `steps-all.html` | 101 | 미확정 19 · 대표 DM 27 · 수익 산정 기준 6 · 조달이자형 2 · W금융일수 47 |
| `terms-edit.html` | 51 | 미확정 12 · 대표 재전달 1 · 대표 DM 22 · 항등식 4 · 일 환산 4 · 수익 산정 기준 1 · 수수료 배분형 1 · W금융일수 6 |
| `feasibility.html` | 14 | 미확정 10 · W금융일수 4 |
| `ceo-questions.html` | 8 | 미확정 3 · 항등식 1 · 일 환산 3 · W금융일수 1 |
| `archive.html` | 3 | 미확정 1 · 항등식 2 |

## 7. 하지 않은 것

- `glossary.html` 재생성 — `build_glossary.py` 가 원고 앵커 `th:W금융일수`(옛 라벨)에서 멎는다. 작업 전부터 같은 자리에서 멎던 기존 미해결(`NEXT_SESSION.md:48`). 원고 `glossary_manuscript.md` 는 문서 페이지라 손대지 않았다. 카드 제거로 원고 앵커 `invest-assets / div:0.11%` · `h2:수익 산정 기준` 2개도 더 이상 화면에 없다 — 원고를 고칠 때 함께 갈아야 한다.
- 그 결과 `verify_shotmarks.py`(FAIL 45, 전엔 40) · `verify_shots.js B4`(거울 2건) 는 통과시키지 못했다. 거울 레포(`payhug-investor-glossary`)는 `sync_glossary.sh` 가 push 까지 하므로 돌리지 않았다.
- `verify_crossscreen.py` 의 glossary 3건 · `verify_docnums.py` 위반 24 는 문서 페이지 대상의 기존 FAIL 그대로.
- `prep_fig.py apply`·`measure`·Figma 재임포트는 하지 않았다(지시 순서에 없음).
- `검산_투자자어드민_20260901.xlsx`(생성기 폴더 안 내부 검산 통합문서)는 재생성만 했고 「미확정」 표식·「대표 DM」 인용 셀은 그대로 두었다 — 투자자에게 나가는 `assets/xlsx` 가 아니다. `audit_xlsx_check.py` 는 그 표식을 기대하므로 손대지 않았다.
- 커밋·push 없음. `payhug-admin-web`·`payhug-merchant-web`·`/Users/semi/Desktop/01_PayHug/` 는 읽지도 않았다.
