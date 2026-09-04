# 5단계 — 화면 옛 표기 → 확정 용어 · 재생성

## 하지 않은 것 · 지시와 다르게 한 것

| 항목 | 내용 |
|---|---|
| `verify_sim.js` 미실행 | `sim_facts.py:52` 단언에 막힙니다. `build_app.py:2066` `SIM_DEFAULT.to = '@@ASOF@@'` 는 `2026-08-27`, `build_sim_static.py:48` `FROM, TO = LG.WEEK` 는 `2026-08-26`. 시뮬 기본 종료일 결정은 이 작업 밖입니다 |
| 시연본 미재생성 | `~/cursor/payhug-investor-prototype/index.html` · `demo/` 는 지시 목록 밖이고 `sync_prototype.sh` 는 push 까지 합니다. 그래서 `verify_shortfall.py` [0]·[5] 와 `verify_batch_symbols.py` `[proto]` 4건이 FAIL 입니다 (시연본은 기간도 `08-21~27` 구판) |
| 주석 2곳 삭제 | `build_app.py` 옛 1298-1299 · `sync_assets_static.py` 옛 184-185 — 제거한 「표기 d 미확정」 배지의 근거만 적은 줄이라 함께 지웠습니다. `sync_assets_static.py` 의 쓰임 없어진 `PEND_BADGE`·`PEND_ROW` 상수와 `pend` 인자도 같이 뺐습니다 |
| 검증기 메시지 문구 갱신 | 라벨 이름이 든 판정 문구(`verify_final_terms.py` I7·I9·I11·I20·I21·I24, `verify_batch_symbols.py`, `verify_sim.js` [10]) 를 새 라벨로 맞췄습니다 |
| 검증기 2종의 기간 종속 수정 | `verify_crossscreen.py` 의 xlsx 파일명 하드코딩(`_2026-08-21_2026-08-27`, 파일 없음)을 `build_xlsx.PRESETS` 파생으로, `sim_facts.py:48` 을 `@@WKFROM@@`·`@@ASOF@@` 토큰 치환 후 판독으로 바꿨습니다. 둘 다 이 작업 전부터 깨져 있던 자리이며 라벨 검사까지 가기 위해 손댔습니다 |
| `sim_facts.json` 구판 잔존 | `sim_facts.py` 가 단언에서 멈춰 쓰지 못합니다. `Ty수익율` 1 · `W금융일수` 12 그대로입니다 |

## (가) 고친 파일

| 절대경로 | 건수 | 무엇 |
|---|---|---|
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/build_app.py` | 38 | `POP_S` 문면·`pend:1` 제거 · `popTh` 의 「표기 d」 행·배지 분기 제거 · `popTh('가중평균 금융일수')`·`popTh('입금부족률')` ×2 · `tyTh` 앵커·`⑤가중평균 금융일수` · 투자자산 카드 앵커 `예상 연환산수익률`·`할인율 × 365 ÷ 가중평균 금융일수`·부제 · 자산 구분·가맹점별 `예상 연환산수익률` 열 · 증명서 th 3 · 수익 카드 `연환산수익률` ×2 · 툴팁 `PD`·`기간 가중평균 금융일수`·`관찰된 값`·`PY<sub>a</sub>` ×2 · 일별 th ×2 · 시뮬 요약 카드·현황표 · 엑셀 미리보기 머리글 3행·현황 행 2 |
| `…/sync_assets_static.py` | 5 | 카드 spec `예상 연환산수익률`/`가중평균 금융일수 %s일 기준` · `POP` 튜플 · `pop_th` pend 제거 · `pop_heads` |
| `…/sync_profit_static.py` | 8 | `TIP4` 3 · `TY_TH` 2 · `TIP5` · `put_ty_th` 정규식·assert |
| `…/build_sim_static.py` | 11 | `TY_TH` 2 · `TY4_DM` · 요약 카드·부제 · 현황표 th 3 · 수익 현황 카드·툴팁 3 · 일별 th |
| `…/build_xlsx.py` | 6 | `put_header` 3 · 각주 · 현황 시트 7·8행 |
| `…/build_docs.py` | 1 | 증명서 PDF 가맹점별 표 머리 3칸 |
| `/Users/semi/cursor/payhug-investor-admin/invest-assets.html` · `--download` · `--cert-confirm` · `--empty` | 각 10 | 카드 라벨·부제 · 앵커 2 · 입금부족률 앵커+문면 2 · 「표기 d」행·배지 2 · `예상 연환산수익률` th 2 |
| `…/invest-profit.html` · `--weekly` · `--monthly` · `--empty` | 각 8 | 카드 라벨 · 툴팁 4 · 일별 th 2 · `⑤가중평균 금융일수` |
| `…/invest-sim.html` | 0 | 대상 문자열 없음 (사이드바 동기화만 통과) |
| `…/invest-sim--result.html` | 11 | 요약 카드·부제 · 현황표 th 3 · 수익 현황 카드·툴팁 4 · 일별 th 2 |
| `…/certificate.html` | 3 | th 3 |
| `…/xls-assets-status.html` · `xls-assets-merchant.html` | 각 1 | 머리글 3칸 |
| `…/xls-profit-status.html` | 2 | 7·8행 `연환산수익률 (…)` |
| `…/xls-profit-daily.html` | 1 | 머리글 2칸 |
| `…/verify_crossscreen.py` | 9 | `POP_TIP`·`POP_WANT`·`PEND_TH`(배지 없음 판정)·`POP_S` 재료·`popTh` 건수 · xlsx 파일명 `BX.PRESETS` 파생 |
| `…/verify_final_terms.py` | 7 | I7·I8·I9·I11·I20·I21·I24 |
| `…/verify_shortfall.py` | 11 | `POP_S_TEXT`·변조 문면 · 앵커 판독 4 · 파일 훑기 · head index 3 |
| `…/verify_batch_symbols.py` | 1 | 주간 카드 라벨 |
| `…/verify_sim.js` | 3 | `card`·`stat` 라벨 · [10] 문구 |
| `…/sim_facts.py` | 3 | `cardTySub` · assert · 토큰 치환 |

재생성된 산출물: `app.html` · `invest-sim.html` · `invest-sim--result.html` · `assets/xlsx/*.xlsx` 14 · `xls-*.html` 파일바 4 · `assets/docs/투자자산증명서_20260827.pdf` · `_fig/` 33화면+assets (git 64건, xlsx 개명분 포함). 자산·수익 낱장 8종은 sync 가 `same` 으로 판정했습니다.

## (나) 재생성 · 검증 실행 결과

| 스크립트 | 종료코드 | 마지막 줄 |
|---|---|---|
| `python3 build_app.py` | 0 | `screens in doc: 16` |
| `python3 sync_assets_static.py` | 0 | `contracts--all.html same` (11 낱장 전부 same) |
| `python3 sync_profit_static.py` | 0 | `invest-profit--weekly.html 행 4 · 카드 4주 2026-08-03 ~ 2026-08-26 · 합계 622,381,520` |
| `python3 build_sim_static.py` | 0 | `W 3.13 · Ty 12.84% · 비중합 100.0 · 상환액=PSA+PSM True` |
| `python3 build_xlsx.py` | 0 | `동기화 xls-profit-daily.html 일별투자수익_2026-08-20_2026-08-26.xlsx · 5.7 KB · 2026-09-04 18:10` |
| `python3 build_docs.py` | 0 | `총 1건 → /Users/semi/cursor/payhug-investor-admin/assets/docs` |
| `python3 prep_fig.py sync` | 0 | `동기화 33화면 · 원본 HEAD 1693bd3 (워킹트리 변경분 포함)` · `패치 sheet.css text-overflow:ellipsis 2곳 제거` |
| `python3 verify_crossscreen.py` | 1 | PASS 56 · FAIL 6 — 라벨 검사(`popTh` ×2 · 모집단 툴팁 4낱장 · 배지 없음) 전건 PASS. FAIL = `xls-profit-daily 7행`·`xls-profit-status 카드`·`app.html 일별 원장 7행`(`08-21` 구판 vs 원장 `08-20`; `xls-profit-*` 표 본문은 재생성 체인에 생성기가 없음, 마지막 기록 `apply_duration.py:193`) + 용어 해설 3(문서) |
| `python3 verify_final_terms.py` | 0 | `판정 136건 · PASS 136 · FAIL 0` |
| `python3 verify_batch_symbols.py` | 1 | `검사 145건 · FAIL 5건` — 라벨 FAIL 0 (`화면 4.13` 판독됨). `[proto]` 4 + `엑셀 되짚은 주간 ④ 3.99 ≠ 화면 4.13`(검산 엑셀 구판) |
| `python3 verify_shortfall.py` | 1 | `검사 60건 · FAIL 2건` — 둘 다 드라이버 중단 `Error: proto 현황표에 입금부족률 툴팁 앵커가 없다`. app 대상은 앵커 통과 |
| `python3 sim_facts.py` | 1 | `AssertionError: ('2026-08-20', '2026-08-27', '2026-08-20', '2026-08-26')` |
| `node verify_sim.js` | 미실행 | 위 단언에 종속 |

## (다) 잔존 grep — `S입금부족율|W금융일수|Ty수익율|PwD|실적치|PY<sub>MR|d-20|D-20`

| 범위 | 건수 | 남긴 이유 |
|---|---|---|
| 루트 낱장 `invest-*` 10 · `certificate` · `xls-*` 4 | 0 | — |
| `_fig/*.html` 33 | 0 | — |
| `app.html` JS 주석 | 20 | 1297 · 1483 · 1485 · 1845 · 1873 · 2400 · 2405-2407 · 2427-2430 · 2457 · 2580 · 2598 — 화면에 안 보이는 주석 |
| `app.html` 코드 변수 | 6 | 2648 · 2650(2) · 2672(2) · 2905 `PwD` — 변수명 |
| `app.html:2300` | 1 | `대표 DM 16:27 · 365 ÷ W금융일수 = 1년 회전수` — 원문 인용 행 |
| `표기 d` | 0 (화면) | `steps-all.html` 1건은 문서 화면, 범위 밖 |

숫자 불변: 낱장 15종 전·후 동일 · `app.html` 은 지운 주석·`pend:1` 안 숫자 6개(`15` `15` `0831` `0831.` `4` `1`)만 빠짐 · `xls-*.html` 4종은 `build_xlsx.py` 가 찍는 파일바 생성일시 `2026-09-03 20:02 → 2026-09-04 18:10` 만 다름. 스냅샷 `…/scratchpad/before/` · `…/scratchpad/after/`.
