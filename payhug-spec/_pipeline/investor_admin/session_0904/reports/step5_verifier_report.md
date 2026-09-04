# 5단계 검증기 — 라벨 확정 반영 · 전종 실행

실행 위치 `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/` · 실행 시각 2026-09-04 · 로그 `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/vlogs/`

## 하지 않은 것 · 지시와 다르게 한 것

| 항목 | 내용 |
|---|---|
| `verify_sim.js` 재실행 불가 | `sim_facts.py:52` 단언 `('2026-08-20','2026-08-27') ≠ ('2026-08-20','2026-08-26')` 에서 멈춥니다. 시뮬 종료일 ASOF/WEEK 불일치는 이 작업 밖입니다. 대신 `verify_sim.js` 의 `HELPERS` 를 그대로 빌린 탐침(`…/scratchpad/sim_stat_probe.js`)으로 고친 키가 화면에서 잡히는지만 확인했습니다 — `stat('연환산수익률')` 값 있음 · `stat('Ty수익율')` null · `card('예상 연환산수익률')` = `13.21% / 가중평균 금융일수 3.04일 기준` · 종료코드 0 |
| `verify_steps_all.py` D 판정 결과 미기록 | H 절에서 `KeyError: '2026-08-27'` 로 중단되어 결과 JSON 이 안 써집니다(steps_all.json 이 08-27 행을 참조 · 원장 `tyByDate` 는 08-26 까지). D 절은 같은 로직을 복제해 셈했습니다 — `SCREEN_LABEL` 갱신 전 `ours 0 · label 59`, 갱신 후 `ours 59 · label 0` 이므로 실행이 되면 「우리 서술에 폐기 기호 0건」이 59건으로 FAIL 입니다 |
| `banned_words.md` 대체어 중 `w금융일수` · `ty수익율` | 지시가 `S입금부족율` 하나라 그대로 뒀습니다. 같은 행의 나머지 둘도 화면 확정 라벨(`가중평균 금융일수` · `연환산수익률`)로 옮길지는 **확인 필요** 입니다 |
| 문서를 보는 검사기의 옛 표기 키 | 용어 해설·steps-all·검산 엑셀·대표 원문·`symbol_glossary.json` 을 대조하는 키는 그 문서가 아직 옛 체계라 손대지 않았습니다(아래 「남긴 자리」 표) |
| `verify_links.py` 실행 방식 | 머리말대로 로컬 서버가 필요해 `python3 -m http.server 8901` 을 띄우고 돌린 뒤 내렸습니다 |
| 기간 이동으로 낡은 검사기 기준 | `verify_app.js:543-544, 577` (`mTo==='2026-08-27'` · `d1===3`) · `verify_toast.js:114, 116` (`_2026-08-21_2026-08-27.xlsx` 파일명) 은 날짜를 손으로 적은 자리입니다. 라벨과 무관하고 지시가 (나) 로 분류해 손대지 말라 했으므로 그대로 두고 아래 표에 자리만 적었습니다 |

## (가) 고친 검사기

| 절대경로:줄 | 옛 | 새 |
|---|---|---|
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_sim.js:395` | `window.__S.stat('Ty수익율')` | `window.__S.stat('연환산수익률')` |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_sim.js:471` | `window.__S.stat('Ty수익율')` | `window.__S.stat('연환산수익률')` |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_proto.js:882` | `xps['Ty수익율 (투자실행금액 대비)']` | `xps['연환산수익률 (투자실행금액 대비)']` |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_proto.js:883` | `xps['Ty수익율 (투자자산 대비)']` | `xps['연환산수익률 (투자자산 대비)']` |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_steps_all.py:51` (근거 주석 48–50) | `SCREEN_LABEL = ('S입금부족율', 'W금융일수', 'Ty수익율', 'w금융일수', 'ty수익율')` | `SCREEN_LABEL = ('입금부족률', '가중평균 금융일수', '연환산수익률')` |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/dm_0901/banned_words.md:23` | 대체어 `S입금부족율` | 대체어 `입금부족률` (근거 칸에 「화면 확정 라벨(2026-09-04)」 병기) |

근거는 각 줄의 주석에 「라벨 확정 2026-09-04」로 적었습니다. 검사를 지우거나 조건을 낮춘 자리는 없습니다. `verify_steps_all.py` 는 옛 라벨을 「화면 라벨」로 봐주던 예외가 사라져 검사가 더 엄격해집니다.

빌더가 앞서 고친 검사기(`verify_crossscreen.py` · `verify_final_terms.py` · `verify_shortfall.py` · `verify_batch_symbols.py` · `verify_sim.js` 나머지 · `sim_facts.py`)는 그대로 두고 실행만 했습니다.

### 옛 표기를 남긴 자리와 이유

| 절대경로:줄 | 남긴 문자열 | 이유 |
|---|---|---|
| `…/verify_ceo_quotes.py:247-251` | `'선정산일이 d-20 ~ d-11'` | 대상이 `glossary_manuscript.md` · `glossary.html`(용어 해설 문서)입니다. 문서의 소문자 d 표기 규칙 검사이며 화면 툴팁 문언이 아닙니다. 용어 해설이 아직 옛 체계(`d-20 ~ d-11` 5건)라 PASS 입니다 |
| `…/verify_glossary.js:93` | 검색어 `'W금융일수'` · `'ty수익율'` | 용어 해설 검색 기능 검사입니다. 문서에 `W금융일수` 24 · `ty수익율` 93 · `연환산수익률` 0 · `입금부족률` 0 이라 지금 바꾸면 문서 재생성 전까지 검색 0건으로 FAIL 입니다 |
| `…/verify_glossary5.js:100, 169` | 검색어 `'PwD'` | 같은 이유 (`PwD` 31건) |
| `…/verify_shortfall.py:74` | `RATIO_SENTENCE = 'S입금부족율 = Σ SLi / Σ SAi'` | 대표 정의서 원문 인용 문장입니다 |
| `…/verify_shortfall.py:581` | `'S입금부족율(%)'` | 검산 엑셀(`~/Downloads/payhug_검산엑셀`, 수정 금지 대상) 기간집계 시트의 행 라벨입니다 |
| `…/audit_xlsx_check.py` 전건 (`pm['S입금부족율(%)']` · `'W금융일수 raw'` · `'Ty수익율(%)'` · `FORBID_SKIP` 등) | 검산 엑셀 셀 라벨 | 대상이 검산 엑셀 20260901 판입니다. 화면 라벨을 보는 자리가 아닙니다 |
| `…/verify_batch_symbols.py:1000, 1043-1047` | `W금융일수` ↔ `w금융일수` 별칭 접기 | `symbol_glossary.json` 이 등록한 별칭의 실재를 판정하는 자리입니다. 그 JSON 은 이번 대상이 아닙니다 |
| `…/verify_docnums.py:91, 99` | 내부 키 `'365/PwD'` · `'ty@PwD'` | 검사기 안에서만 쓰는 사전 키입니다 |
| `…/verify_banned.py:541` | 자기시험 문장 `S입금부족율` | 「대체어 자리는 조용한가」 시험입니다. `S` 단독 규칙은 칸 전체가 `S` 일 때만 잡으므로 대체어 갱신 뒤에도 19/19 통과합니다 |
| `…/verify_0828_negative.py:118` | 심는 문장 `W금융일수는 예시값이다.` | 29번 항목(예시값 고지) 음성 시험의 재료이며 라벨 검사가 아닙니다 |
| 주석·판정 이름 (`verify_final_terms.py:878` · `gate_prototype.js:366-376` · `verify_identity.js` · `verify_crossscreen.py:262-270` 등) | `Ty수익율` · `W금융일수` | 지시대로 문면만 남긴 자리입니다 |

## (나) 실행 결과

41건 실행 · 종료코드 0 = 21건 · 1 = 20건 (`verify_links.py` 는 로컬 서버를 띄운 재실행 결과 기준).

| 검사기 | PASS / FAIL | FAIL 분류 | 원인 한 줄 |
|---|---|---|---|
| `sim_facts.py` | 단언 실패 | 나 | `SIM_DEFAULT.to='@@ASOF@@'`(08-27) ≠ `build_sim_static.TO`(WEEK 끝 08-26) |
| `verify_0828.py` | 32 / 0 | — | — |
| `verify_0828_negative.py` | 위반 16종 전건 검출 · 복원 후 FAIL 0 | — | — |
| `verify_banned.py` | 금지 낱말 161건 (종료 1) | 나 | `확인필요` 158 — `capability.html` 83건은 HEAD 와 같은 수 · `capability_manuscript.md` 75건 동일. `낱건` 3 — `final_terms.json`(09-03 20:13 판, 설명 문장 조). 라벨 무관 |
| `verify_banned.py --self` | 19 / 0 | — | 갱신한 목록으로 판별력 유지 |
| `verify_batch_symbols.py` | 140 / 5 | 나 | `[proto]` 4 — 시연본 미재생성(08-21~27 구판). `엑셀 되짚은 주간 ④ 3.99 ≠ 화면 4.13` — 검산 엑셀 구판 |
| `verify_ceo_quotes.py` | 64 / 0 | — | — |
| `verify_crossscreen.py` | 56 / 6 | 나 | `xls-profit-daily 7행` · `xls-profit-status 카드` · `app.html 일별 원장 7행` — 08-21 구판 ↔ 원장 08-20 (표 본문 생성기 없음). 용어 해설 duration 3건 — 문서 옛 체계. 라벨 검사(`popTh` 2 · 모집단 툴팁 4낱장 · 배지 없음) 전건 PASS |
| `verify_cycle_xlsx.py` | PASS | — | — |
| `verify_docnums.py` | 13문서 · 대조값 통과 5 · 위반 76 | 나 | 문서의 `PwD 3.107588` · `365÷PwD 117.454437` 등이 원장 `weekWRaw 3.093802` 와 다름 — 기간 이동 전 값 |
| `verify_final_terms.py` | 136 / 0 | — | I7·I8·I9·I11·I20·I21·I24 새 라벨 통과 |
| `verify_finaledit.py` | 34 / 12 | 나 | 원고 `final_terms.json`(09-03 20:13 · 36항 · `연환산수익률` 4건) 이 산출 `용어기호정리_편집판_20260902_2345.html`(29항) 보다 새것 — `build_finaledit.py`·`build_final.py` 미실행. 이번 작업 전 상태 |
| `verify_links.py` | 73 / 12 | 나 | `archive.html` 이 `*_2026-08-27.xlsx` 12건을 참조 · 실물은 `*_2026-08-26.xlsx` (build_xlsx 개명분) — `build_archive.py` 미실행 |
| `verify_settlement_cards.py` | 81 / 4 | 나 | 명부가 「종료코드 1 이 정상」으로 못 박은 어드민 화면·코드 결함 4건(②·⑤·⑤'·types) |
| `verify_shortfall.py` | 58 / 2 | 가+나 | [0]·[5] 드라이버 중단 `proto 현황표에 입금부족률 툴팁 앵커가 없다` — 기대는 새 라벨(빌더 갱신), 시연본이 `S입금부족율` 구판. app 대상은 앵커 통과 |
| `verify_shotmarks.py` | 50 / 0 | — | — |
| `verify_steps_all.py` | 중단 (`KeyError '2026-08-27'`) | 나 | `steps_all.json` 이 08-27 행을 참조 · 원장은 08-26 까지. 실행되면 D 절 59건 FAIL — `steps_all.json` 의 `term`·`label` 이 `S입금부족율`·`w금융일수`·`ty수익율` 구판 |
| `verify_termsedit.py` | 48 / 0 | — | — |
| `audit_xlsx_check.py` | 종료 0 | — | 검산 엑셀 20260901 판 대조 |
| `sync_counts.py --check` | 규칙 66 · 불일치 0 | — | — |
| `sync_assets_static.py --check` | 어긋난 낱장 0 / 11 | — | — |
| `build_readme.py --check` | 일치 | — | — |
| `verify_app.js` | 99 / 2 | 나 | `기간·granularity 변경 시 합계 재계산` — 월별 종료 `2026-08-26`, 검사기 `mTo==='2026-08-27'`(:544). `날짜 입력이 조회 조건을 움직인다` — 08-25 부터 2행, 검사기 `d1===3`(:577). 종료일 ASOF↔LAST_DUE |
| `verify_proto.js` | 123 / 12 | 가+나 | 시연본 구판 10건(④ 3.99% ↔ 원장 4.13% · PA · 08-27 행 · 월별 08 4.62) + `엑셀 투자수익현황 ④⑤ 없음` 2건 — 새 키 `연환산수익률 (…)` ↔ 시연본 라벨 `Ty수익율 (…)`. 시연본 재생성 뒤 재판정 |
| `verify_rows.js` | 35 / 0 | — | — |
| `verify_toast.js` | 23 / 2 | 나 | `xls-get profit-status`·`profit-daily` — 토스트 `_2026-08-20_2026-08-26.xlsx`, 검사기 want `_2026-08-21_2026-08-27.xlsx`(:114, :116) |
| `verify_identity.js` | 17 / 1 | 나 | `카드 5값 = 표 합계` — 월별·복귀 기간 끝 `08-26`, 기대 `08-27` (행수 26↔27 · 148↔149) |
| `verify_period.js` | 14 / 26 | 나 | 전건 기준일 `08-27` 기대 ↔ 화면 종료일 `08-26` (프리셋·주 라벨·스냅·복귀) |
| `verify_password.js` | 75 / 0 | — | — |
| `verify_sim.js` | 미실행 | 나 | `sim_facts.py` 단언에 종속. 라벨 키는 탐침으로 확인(위 표) |
| `verify_glossary.js` | PASS | — | 용어 해설 옛 체계 그대로 통과 |
| `verify_glossary5.js` | PASS | — | 같음 |
| `verify_feasibility.js` | PASS | — | — |
| `verify_weighting.js` | 28 / 0 | — | 검산 엑셀 금지값 2건은 곳수만 보고 |
| `verify_termsedit_page.js` | 17 / 0 | — | — |
| `verify_page_common.js` | 17 / 0 | — | — |
| `verify_shots.js` | 46 / 7 | 다(파생) | `invest-assets.html` · `invest-profit.html` 이 촬영 봉인(09-01 17:24Z) 뒤 바뀜(09-04 09:09Z · 라벨 교체) — B2·B3 sha·mtime, C1·C2 재현 바이트(invest-assets 문서 높이 1320→1316 · 「표기 d」행 제거분). 고칠 자리는 봉인이 아니라 캡처 |
| `gate_prototype.js` | 실패 2 | 나 | `Ty수익율 ④⑤ = 원장` ④ 3.99/4.13 · ⑤ 2.25/2.32 · `PA 179,970,919/179,916,643` — 시연본 구판 |
| `gate_glossary.js` | 실패 1 | 다(파생) | `verify_shots.js` 종료코드 상속 |
| `verify_sync_chain.js` | 동기화 안 됨 4 | 나 | 시연·배포 `ledgerDays 180 ≠ 정본 179` · `ledgerProfitSum 1,787,417 ≠ 1,778,656` · 시연 가맹점별 총 건수 없음 · 용어 본문 길이 89,277↔84,124 — 시연본·배포본 미동기화 |
| `verify_deployed.py` | 8 / 0 | — | — |

### 새 라벨 자리 실측 (화면·엑셀·PDF)

| 산출물 | `예상 연환산수익률` | `연환산수익률`(전체) | `입금부족률` | `가중평균 금융일수` | `PD`·`기간 가중평균 금융일수`·`관찰된 값`·`PY<sub>a</sub>` | `표기 d` | 옛 라벨 |
|---|---|---|---|---|---|---|---|
| `invest-assets*.html` 4종 | 3 | 3 | 2 | 3 | — | 0 | 0 |
| `certificate.html` · `xls-assets-*.html` 2종 | 1 | 1 | 1 | 1 | — | 0 | 0 |
| `invest-profit*.html` 4종 | 0 | 2 | 0 | 3 | 2·1·1·1 | 0 | 0 |
| `invest-sim--result.html` | 2 | 4 | 1 | 5 | 2·1·1·1 | 0 | 0 |
| `xls-profit-status.html` · `xls-profit-daily.html` | 0 | 2 · 1 | 0 | 0 · 1 | — | 0 | 0 |
| `app.html` (주석 20 · 변수명 6 · DM 인용 1 제외) | 8 | 14 | 6 | 16 | 4·2·2·2 | 0 | 0 |
| `assets/xlsx/*.xlsx` 14 | 셀 새 라벨 2~3건씩 | | | | | | 0 |
| `assets/docs/투자자산증명서_20260827.pdf` | 1 | 1 | 1 | 1 | — | 0 | 0 |

## (다) 빌더가 손볼 것

| 자리 | 무엇 |
|---|---|
| `/Users/semi/cursor/payhug-investor-admin/assets/docs/투자자산증명서_20260827.pdf` 가맹점별 표 머리 (원천 `build_docs.py` 표 머리 3칸) | 새 라벨이 열 너비에 안 들어가 낱말 가운데서 꺾입니다 — PDF 본문 판독 `가중평균 금` / `융일수` · `예상 연환산` / `수익률`. 열 너비 또는 줄바꿈 위치 조정이 필요합니다 |

### 라벨 교체가 파생시킨 재생성 대상 (검사기가 아니라 산출물 쪽)

| 대상 | 검사기 | 무엇 |
|---|---|---|
| 캡처 `assets/shots/*.webp` (`capture_shots.js` → `build_glossary.py`) | `verify_shots.js` 7 · `gate_glossary.js` 1 | `invest-assets.html` · `invest-profit.html` 이 라벨 교체로 바뀌어 촬영 봉인과 어긋납니다 |
| `archive.html` (`build_archive.py`) | `verify_links.py` 12 | xlsx 파일명 `_08-27` → `_08-26` 개명분 미반영 |
| `meeting_0901/steps_all.json` · `steps-all.html` | `verify_steps_all.py` D 59건 | `term`·`label` 이 옛 라벨 |
| `glossary.html` · `glossary_manuscript.md` | `verify_glossary.js:93` · `verify_glossary5.js:100,169` · `verify_ceo_quotes.py:247-251` · `verify_crossscreen.py` 용어 해설 3 | 옛 라벨 `W금융일수` 24 · `ty수익율` 93 · `S입금부족율` 38 · `PwD` 31 · `d-20 ~ d-11` 5. 문서를 새 체계로 재생성하면 이 검색어·문장 기대값도 같이 갱신해야 합니다 |
| 시연본 `~/cursor/payhug-investor-prototype` | `verify_proto.js` 12 · `verify_batch_symbols.py` 4 · `verify_shortfall.py` 2 · `gate_prototype.js` 2 · `verify_sync_chain.js` 4 | 08-21~27 구판 · `Ty수익율`·`S입금부족율` 구판 |

## 만들거나 고친 파일

| 절대경로 | 무엇 |
|---|---|
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_sim.js` | 395 · 471 라벨 키 |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_proto.js` | 882 · 883 엑셀 행 키 |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_steps_all.py` | 48–51 `SCREEN_LABEL` |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/dm_0901/banned_words.md` | 23 대체어 |
| `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/run_all.sh` | 전종 순차 실행기 |
| `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/vlogs/` | 검사기별 로그 41개 · `_summary.tsv`(종료코드·소요) |
| `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/sim_stat_probe.js` | `verify_sim.js` 라벨 키 탐침 |
| `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/step5_verifier_report.md` | 이 보고서 |

검사기 실행이 갱신한 `*_result.json` 은 각 검사기의 정해진 출력 자리(`_pipeline/investor_admin/verify_*_result.json`)에 그대로 남아 있습니다.
