# 7단계 검증기 — ⑤ 산식 교체 · 툴팁 용어명 · 시연본 축소 · 로그인 실물화 반영 · 전종 실행

실행 위치 `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/` · 실행 2026-09-04 · 로그 `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/step7v/vlogs/` · 수정 전 사본 `…/step7v/before/`

## 하지 않은 것 · 지시와 다르게 한 것

| 구분 | 내용 |
|---|---|
| 하지 않음 | `gate_prototype.js` · `scripts/sync_prototype.py` — 열지 않았고 돌리지 않았습니다 |
| 하지 않음 | 산출물·생성기·원장·시연본 저장소·`roster16_apply.py` 수정 |
| 하지 않음 | `build_glossary.py` 재생성 — 재촬영 절차의 마지막 단계인데 `glossary_manuscript.md` 의 `[[shot: …]]` 앵커 13건이 옛 라벨(`th:W금융일수` · `th:S입금부족율#0` · `th:TY수익율` · `div:Ty수익율#0`)이라 `!! 앵커 못 찾음` 으로 멎습니다(파일을 쓰기 전에 멎어 `glossary.html` 은 그대로). 원고 소관이라 손대지 않았고 (다) 에 적었습니다 |
| 하지 않음 | 기간 이동(기대 기준일 08-27 ↔ 화면 종료일 08-26) 검사기 6종의 날짜 기대값 — 어느 쪽이 정답인지 결정(D-번호)이 없어 옮기지 않았습니다. (다) 분류 |
| 하지 않음 | `verify_sim.js` 실행 확인 — `sim_facts.py:52` 단언(통합본 시뮬 종료일 08-27 ≠ 낱장 08-26)에서 멎어 못 돕니다. `sim_facts.py`·`verify_sim.js` 의 (가) 수정은 정규식 추출만 따로 확인했습니다(`PEND5_ROW` → `미확정대표 확인 대기` · `PEND_ROW` → `미확정대표 재전달 대기`) |
| 범위 넓힘 | 거울 저장소 `payhug-investor-glossary/assets/shots/*.webp` 5장에 새 캡처 복사(커밋·push 없음). `verify_shots.js` B4·`gate_glossary.js` 가 거울 바이트를 판정하므로 봉인 갱신에 따라옵니다. 그 저장소는 이미 같은 파일이 미커밋 수정 상태였습니다 |
| 범위 넓힘 | `capture_shots.js` · `verify_shots.js` 에 웹폰트 적재 대기·판정 추가. 재촬영 1회차가 Google Fonts CSS 가 닿기 전에 찍혀 문서가 37px 길어진 채 봉인될 뻔했습니다(아래 (라)) |
| 범위 넓힘 | `verify_rows.js` 첫 실행이 `psz is not defined` 로 죽고 재실행에서 35/35 — 고정 900ms 대기가 `app.html`(245KB) 초기화와 경주한 것이라 앱 전역이 잡힐 때까지 기다리게 했습니다 |
| 범위 넓힘 | `request_register.md` 「G-1 예외 — 제품 UI 원문」 표에 로그인 안내 문구 1행. `verify_0828.py` 가 「등재된 문구만 예외」라 검사기와 레지스터를 함께 맞췄습니다 |
| 검사 이관 | `verify_proto.js` 9)-(4) 엑셀 미리보기 대조는 시연본에 `xls-*` 화면이 없어 볼 자리가 없습니다. 지우지 않고 `verify_app.js` 9) 로 옮겨 원본 `app.html` 에서 봅니다 |
| 미실행 | `verify_0828_negative.py` 는 종료코드 0 만 확인(요약 줄 없음) |

## (가) 고친 검사기

경로는 `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/` 아래입니다. 판정을 느슨하게 한 자리는 없고, 근거는 각 줄의 주석에 있습니다.

### ⑤ 산식 교체 (`daily_ledger.TY5_EXPR = 'ty4 * ad / tot'` · facts `weekAD`·`fullAD`·`adByDate`)

| 절대경로:줄 | 옛 | 새 |
|---|---|---|
| `verify_app.js:968-976` · `verify_sim.js:773-781` | `ty5body: /ty4 \* psa \/ tot/` 1건 · `hard5` 옛 꼴 3종 | `/ty4 \* ad \/ tot/` 1건 · `hard5` = 옛 `psa` 꼴 4종 + 새 인라인 꼴 `TY4 * AD / (AD + PEC)` · `ty4 * ad / (ad + psc)` · `ad + psc) ? ty4` 3종 (전부 0건이어야) |
| `verify_identity.js:122-124, 137-146` | `ledgerAgg` 가 exec·profit·repay·W 만 합산 | `ADBD = FACTS.adByDate` · `ad` 합산 |
| `verify_identity.js:157-166` | `ty5 = r6(ty4 × ex ÷ (ex + psc))` | `ty5 = r6(ty4 × ad ÷ (ad + psc))` |
| `verify_identity.js:201-206` | `tyAssetWant(ty4, psa, rs)` = `r2(ty4 × psa ÷ (psa + psc))` | `adOfLabels(rs)` · `tyAssetWant(ty4, rs)` = `r2(ty4 × ad ÷ (ad + psc))` |
| `verify_identity.js:363-401` | 배율 `PSA/(PSA+PSC)` · `wantK = exec/(exec+psc)` | 배율 `AD/(AD+PEC)` · `wantK = ad/(ad+psc)` (기본 기간 0.799031) |
| `verify_proto.js:804-806, 826-833` · `verify_app.js:863-865, 886-890` | 툴팁 `'PA' + psa + '원'` · `'PEC' + psc + '원'` | `'PA기간 투자실행금 · ' + psa + '원'`(④ 툴팁) · `'PEC기간 순현금 · ' + psc + '원'` · `'Σ( Ai × Di )' + weekAD + '원'`(⑤ 툴팁) |
| `verify_docnums.py:66-77, 83-84, 93, 97, 113` | `ratio = pa/(pa+pec)` · 못 `PA+PEC`·`PA비중` | `ratio = ad/(ad+pec)` · 못 `AD+PEC`·`AD비중` · 금액 못에 `weekAD`·`fullAD` |
| `verify_steps_all.py:196-198` | `ty_asset(o4, pa, weekPsc)` | `ty_asset(o4, D(F['weekAD']), weekPsc)` |
| `audit_xlsx_check.py:541-549` | facts 대조 26항 | + `주간 Σ(Ai x Di)`=`weekAD` · `전 구간 Σ(Ai x Di)`=`fullAD` (행은 라벨로 잡아 밀림 무관) |
| `audit_xlsx_check.py:969-1000, 1030-1050` | 「PA·PEC 를 함께 문 수식 셀 하나뿐」(`기간집계!B5`+`B15`) · 「`PA + PEC` 문자열」 뜻풀이 1줄 예외 | 「Σ(Ai x Di)·PEC 를 함께 문 수식 셀 하나뿐」(`B9`+`B15`) + **옛 식 `B5`+`B15` 셀 0건** + 새 문면 `Σ(Ai x Di) + PEC` 는 뜻풀이 1줄·⑤ 칸 행의 출처 셀뿐 + **옛 문면 `PA + PEC` 0건** |
| `verify_final_terms.py:766-769` I26 | 툴팁에 `PA`·`PEC` 값 | 툴팁에 `SAD`(Σ Ai×Di 556,626,436)·`PEC` 값 · 제목 「Σ( A_i × D_i ) · PEC 를 그대로 댄다」 |
| `verify_crossscreen.py:180-182` | `_DAILY_RE` 가 `ty:…}` 로 끝나는 행만 읽음 → `ad` 필드가 붙은 새 원장 0행 | `(?:, ad:\d+)?` 허용 |
| `verify_crossscreen.py:193-194` | (없음) | 「일별 원장 DAILY 0건 아님」 — 파서가 못 읽으면 `⊂ 범위` 검사들이 빈 채로 통과하던 구멍 |
| `sim_facts.py:194-202, 304` | `pendRow` 하나 | `pend5Row`(⑤ 「대표 확인 대기」) 추가 · 두 문면이 같으면 단언 실패 |
| `verify_sim.js:620-647, 891-896` | ⑤·⑥·낱장 전부 `pendRow` | ⑤ 는 `pend5Row` 포함 + `pendRow` 불포함 · ⑥ 열머리는 `pendRow`(`tyThText`) 그대로 |

### 시연본 축소 (`PROTO_DROPPED` 6건 · 사이드바 7)

| 절대경로:줄 | 옛 | 새 |
|---|---|---|
| `verify_proto.js:162-163` | 상태 도달 `['invest-sim','result', …]` | 제거 |
| `verify_proto.js:425, 696, 732, 777` | 죽은 컨트롤·레이아웃·탈출·오버플로 목록에 `invest-sim` 2상태 · `xls-*` 4화면 | 제거 |
| `verify_proto.js:872-877` | 9)-(4) `xls-profit-daily`·`xls-profit-status`·`xls-assets-status` 대조 | `verify_app.js` 9) 로 이관 · 9)-(6) 「시연본에 `xls-*`·`invest-sim` 화면 없음」 판정 추가 |
| `verify_app.js:853-953` | (없음) | 9) 숫자 불변 17건 — `verify_proto.js` 9) 의 (1)~(5) 전부를 원본 `app.html` 에서 판정 |
| `verify_sync_chain.js:71-75` | `PROTO_DROPPED = ['index']` | `['index','invest-sim','xls-assets-status','xls-assets-merchant','xls-profit-status','xls-profit-daily']` |
| `verify_sync_chain.js:83-85, 330-331, 394-399` | 시연 사이드바 = 정본 8 | `PROTO_MENUS` = 정본 `navList` − 제거 메뉴 · 목록까지 일치 요구 · 통합 배포본은 8 그대로 |
| `verify_sync_chain.js:435-437, 455` | 실클릭 루프가 기대 곳수만큼 | 실제 걸린 메뉴 전건(`max(navMenus, PROTO_MENUS)`) |
| `verify_batch_symbols.py:477-492` | 드라이버가 app·proto 양쪽에서 시뮬 3회 | app 만 · proto 는 `simAbsent`(섹션·메뉴·전역 함수) 수집 |
| `verify_batch_symbols.py:938-944, 1276-1280` | 3절·5-e `for key in ('app','proto')` | `('app',)` + 「[proto] 투자 시뮬레이션 화면·메뉴·전역 함수 없음」 1건 판정 |

### 로그인 실물화 · 실행 안정

| 절대경로:줄 | 옛 | 새 |
|---|---|---|
| `verify_0828.py:264-266` | `UI_ORIG` 16종 | + `('이 페이지는 관리자 전용입니다.', 'payhug-admin-web/app/login/page.tsx:186')` |
| `request_register.md:211` | G-1 예외 표 8행 | + 로그인 안내 상자 1행 (같은 출처) |
| `verify_rows.js:48-60` | `goto` = navigate + 900ms | `go`·`psz`·`section.screen` 이 잡힐 때까지 최대 8초 폴링 |

### 캡처 봉인

| 절대경로:줄 | 옛 | 새 |
|---|---|---|
| `capture_shots.js:279-293, 309, 383, 416` | `fonts.ready` + 800ms | Noto Sans KR `FontFace.status === 'loaded'` 최대 12초 대기 · 봉인에 `fontLoaded` 기록 · 미적재면 그 화면 실패 |
| `verify_shots.js:94-97, 228-242, 266-268, 284-285` | B 4건 · C 2건/장 · D 8건 | + B5 봉인 시점 웹폰트 적재 · C0 재현 시점 웹폰트 적재 · D4b 자기시험 (53 → 64건) |
| `verifiers.md` | — | 「⑤ 산식 교체 · 툴팁 용어명 · 시연본 축소로 기준을 옮긴 자리 (2026-09-04)」 절 · 판정 표 곳수(`verify_app` 123 · `verify_proto` 119 · `verify_shots` 64 · `verify_batch_symbols` 129) · 기대값 원천 표 `fontLoaded` |

## (나) 실행 결과

41건 실행 · 종료코드 0 = 24건 · 1 = 17건. 분류 — (가) 이번 변경 · 기대값 갱신으로 닫음 / (나) 시연본 재생성 전 / (다) 이전부터 깨진 것 / (라) 산출물 오류.

| 검사기 | PASS / FAIL | 분류 | 원인 한 줄 |
|---|---|---|---|
| `sim_facts.py` | 단언 실패 | 다 | `SIM_DEFAULT.to`(08-27) ≠ `build_sim_static.TO`(08-26) — 통합본·낱장 시뮬 기간 갈림 |
| `verify_0828.py` | 32 / 0 | 가 | 로그인 안내 문구 `…전용입니다.` 가 22·26 G-1 에 걸림 → 제품 UI 원문 등재로 닫음 |
| `verify_0828_negative.py` | 종료 0 | — | — |
| `verify_banned.py` | 금지 낱말 161 | 다 | `capability.html`·`capability_manuscript.md` 「확인필요」 158 · `final_terms.json` 「낱건」 3 — 라운드 무관 |
| `verify_banned.py --self` | 19 / 0 | — | — |
| `verify_batch_symbols.py` | 125 / 4 | 나 | `[proto]` 행값·합계 3건(08-21~27 구판) · `[proto] 시뮬 없음`(구판에 시뮬 있음) |
| `verify_ceo_quotes.py` | 64 / 0 | — | — |
| `verify_crossscreen.py` | 59 / 4 | 가+다 | `ad` 필드로 원장 0행 → 파서 갱신으로 닫음(가). 남은 4: 기본 기간 7행(기대 08-21~27 리터럴 ↔ 원장 08-20~26 · 다) · 용어 해설 duration 3건(문서 옛 체계 · 다) |
| `verify_cycle_xlsx.py` | PASS | — | — |
| `verify_docnums.py` | 대조값 통과 5 · 위반 70 | 다 | 문서의 `PwD 3.107588`·`3.99%`·`0.562460` 등 — 기간 이동·옛 ⑤ 시절 값 |
| `verify_final_terms.py` | **137 / 0** | 가 | I26 을 `Σ( A_i × D_i )` 로 → 137/137 |
| `verify_finaledit.py` | 34 / 12 | 다 | 원고 `final_terms.json`(36항) 이 산출 `용어기호정리_편집판_20260902_2345.html`(29항) 보다 새것 — 미재생성 |
| `verify_links.py` | 73 / 12 | 다 | `archive.html` 이 `*_2026-08-27.xlsx` 12건 참조 · 실물은 `_08-26` |
| `verify_settlement_cards.py` | 81 / 4 | 다 | 명부가 「종료코드 1 이 정상」으로 못 박은 어드민 화면·코드 결함 4건 |
| `verify_shortfall.py` | 58 / 2 (드라이버 중단으로 60건만 판정) | 나 | `[0]·[5]` 드라이버 중단 — proto 현황표에 `입금부족률` 툴팁 앵커 없음(구판 `S입금부족율`). 시연본이 재생성되면 82건 전건이 돈다 |
| `verify_shotmarks.py` | 11 / 39 | 다 | 캡처는 현행인데 `glossary.html` 의 `data-mark` 가 옛 좌표 — `build_glossary.py` 가 원고 앵커 13건(옛 라벨)에서 멎어 재생성 불가 |
| `verify_steps_all.py` | 중단 `KeyError '2026-08-27'` | 다 | `steps_all.json` 이 08-27 행 참조 · 원장은 08-26 까지 |
| `verify_termsedit.py` | 48 / 0 | — | — |
| `audit_xlsx_check.py` (기본 · `all`) | 종료 0 · 전체 통과 true | 가 | `all` 의 ⑤ 단일 원천 절 「기호 사전 줄 1」이 옛 문면 `PA + PEC` 기준이라 false → 새 문면 기준·옛 문면 0건으로 닫음 |
| `sync_counts.py --check` | 불일치 0 / 규칙 66 | — | — |
| `sync_assets_static.py --check` | 종료 0 | — | — |
| `build_readme.py --check` | 종료 0 | — | — |
| `verify_app.js` | 121 / 2 | 다 | `기간·granularity` 월별 종료 `08-26` ↔ 기대 `08-27`(:544) · `날짜 입력` 08-25 부터 2행 ↔ 기대 3행(:577). 새 9) 숫자 불변 17건·⑤ 배선 전건 PASS |
| `verify_proto.js` | 106 / 13 | 나 | 시연본 구판 12건(④ 3.99 ↔ 4.13 · ⑤ 2.25 ↔ 3.30 · 툴팁 옛 문면 · 08-27 행 · 월별 08 4.57) + 「`xls-*`·`invest-sim` 없음」 1건. 1회차의 `profit-status/12주 → null 0B` 는 재실행에서 PASS(내려받기 타이밍) |
| `verify_rows.js` | 35 / 0 | 가 | 1회차 `psz is not defined`(초기화 경주) → 대기 조건으로 닫음 · 2회 연속 35/35 |
| `verify_toast.js` | 23 / 2 | 다 | 토스트 `_2026-08-20_2026-08-26.xlsx` ↔ 기대 `_08-21_08-27`(:114, :116) |
| `verify_identity.js` | 17 / 1 | 다 | 「카드 5값 = 표 합계」 월별·복귀 끝 `08-26` ↔ 기대 `08-27`. ⑤ 항등식·AD 배율 절 PASS |
| `verify_period.js` | 14 / 26 | 다 | 전건 기준일 `08-27` 기대 ↔ 화면 `08-26` |
| `verify_password.js` | 75 / 0 | — | — |
| `verify_sim.js` | 미실행 | 다 | `sim_facts.py` 단언에 종속 |
| `verify_glossary.js` · `verify_glossary5.js` · `verify_feasibility.js` | PASS | — | 용어 해설 옛 체계 그대로 통과(검색어 `W금융일수`·`PwD` 가 문서에 아직 있음) |
| `verify_weighting.js` | PASS | — | — |
| `verify_termsedit_page.js` · `verify_page_common.js` | 17 / 0 · 17 / 0 | — | — |
| `verify_shots.js` | **64 / 0** | 라(봉인) | 재촬영·봉인 갱신 뒤 B·C 전건 |
| `gate_glossary.js` | 통과 | 라(봉인) | 배포본 webp = 봉인 · `verify_shots` 0 · 화면이 부른 바이트 = 봉인 |
| `verify_sync_chain.js` | 동기화 안 됨 5 | 나 | 시연 사이드바 8 ↔ 기대 7 · 시연·배포 `ledgerDays 180 ≠ 179`·`profitSum` · 시연 총 건수 없음 · 용어 본문 길이 89,277 ↔ 84,124 |
| `verify_deployed.py` | 8 / 0 | — | 배포된 구판에도 표식이 있어 통과 |

### 새 검사가 실제로 잡는지

| 검사 | 확인 |
|---|---|
| `verify_app.js` 9) Σ( Ai × Di ) 툴팁 행 | 원본 `app.html` 에서 `Σ( Ai × Di )556,626,436원` 일치 · 시연본(옛 툴팁)에서는 `없음` 으로 FAIL |
| `verify_proto.js` 9)-(6) | 구판 시연본에서 `invest-sim,xls-assets-status,…` 5화면을 그대로 댐 |
| `audit_xlsx_check.py all` 옛 식·옛 문면 0건 | 검산 xlsx 20260901 판에서 `입력!C19` 하나 · 옛 식 0 · 옛 문면 0 |
| `verify_crossscreen.py` DAILY 0건 아님 | 파서 갱신 전 원장 0행 상태에서 FAIL 이었을 자리 |
| `verify_shots.js` D4b | 봉인에 `fontLoaded:false` 를 심으면 B5 가 잡음 |

## (다) 빌더가 손볼 것

| 자리 | 무엇 | 걸리는 검사기 |
|---|---|---|
| `glossary_manuscript.md` `[[shot: …]]` 앵커 13건 (314·492·1192·1299·1376·1822·1901·2013·2345·2415·2480·2759·3109행) | `th:W금융일수`(5) · `th:S입금부족율#0`(3) · `th:TY수익율`·`#0`(4) · `div:Ty수익율#0`(1) 이 현행 라벨(`가중평균 금융일수` · `입금부족률` · `연환산수익률`)과 안 맞아 `build_glossary.py` 가 멎음. 고치고 재생성하면 `glossary.html` 좌표가 새 캡처를 따라옴 | `verify_shotmarks.py` 39 |
| `build_app.py` `SIM_DEFAULT.to = @@ASOF@@`(08-27) ↔ `build_sim_static.TO`(08-26) | 통합본 시뮬 기본 기간과 낱장 `invest-sim--result.html` 기간이 갈림 | `sim_facts.py` · `verify_sim.js` |
| 기준일 `ASOF 08-27` ↔ 원장 끝 `08-26` · `BASE_DATE 2026-08-26` | 프리셋·월별 종료일·xlsx 파일명·`steps_all.json` 08-27 행이 한쪽씩 갈림. 어느 날짜가 정답인지 결정이 나면 검사기 6종(`verify_app` :544·:577 · `verify_toast` :114·:116 · `verify_period` · `verify_identity` 카드↔표 · `verify_crossscreen` :192 · `verify_steps_all`)을 한 번에 옮김 | 위 검사기 |
| `archive.html` (`build_archive.py`) | xlsx 개명분(`_08-27` → `_08-26`) 미반영 · `login.html` 행 크기·시각 옛 값 | `verify_links.py` 12 |
| `용어기호정리_편집판_*.html` (`build_finaledit.py`·`build_final.py`) | 원고 `final_terms.json` 36항보다 뒤처짐 | `verify_finaledit.py` 12 |
| 용어 해설·`steps-all.html`·`calc.html`·`final-terms.html` 문서 | 옛 체계(`W금융일수` 24 · `ty수익율` 93 · `PwD 3.107588` · `( PA + PEC )` 잔존) | `verify_docnums.py` 70 · `verify_crossscreen.py` 3 · `verify_glossary*.js` 검색어 |
| 시연본 `payhug-investor-prototype` | 재생성 대기(다른 조) | `verify_proto.js` 13 · `verify_batch_symbols.py` 4 · `verify_shortfall.py` 2 · `verify_sync_chain.js` 5 |

## (라) 캡처 봉인 결과

| 항목 | 값 |
|---|---|
| 촬영 | `node capture_shots.js`(`--headless=new`) · dsf 2 · quality 70 · 1440×1200 · Google Chrome 152.0.7977.77 · `2026-09-04T13:36:04Z` |
| 문서 높이 | `invest-assets` 1316 · `invest-profit` 1271 · `merchants`·`contracts`·`coocon` 1200 |
| 바뀐 그림 | `invest-assets.webp`(1cea1cd2 → efa99cfa · 127,558B) · `invest-profit.webp`(0c0ab8d7 → 82de1ce5 · 111,574B). 나머지 3장은 화면이 안 바뀌어 sha256 동일 |
| 봉인 | `shot_rects.json` `capture.files[*]` 5건 `fontLoaded: true` |
| 거울 | `payhug-investor-glossary/assets/shots/*.webp` 5장 = 원본 바이트 (미커밋) |
| `verify_shots.js` | 64 / 0 — A 13 · B 25 · C 16 · D 9 · E 1 |
| `gate_glossary.js` | 통과 — 배포본 webp = 봉인 · 화면이 부른 바이트 = 봉인 |
| `verify_shotmarks.py` | 11 / 39 — 캡처가 아니라 `glossary.html` 좌표가 옛것((다) 첫 행) |
| 1회차 사고 | 같은 명령의 첫 촬영이 `invest-assets` 1353 · `invest-profit` 1308 으로 37px 길게 찍혔고 `verify_shots` C1·C2 가 잡았습니다. `fonts.ready` 가 Google Fonts CSS 도착 전에 풀려 대체 글꼴로 「수익 산정 기준」 블록이 한 줄 더 접힌 것입니다. 2회차부터 1316 · 1271 로 재현 대조와 일치했고, 3회차(폰트 대기 반영)로 봉인했습니다 |

## 만들거나 고친 파일

| 절대경로 | 무엇 |
|---|---|
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_app.js` | ⑤ 정의 정규식 · 9) 숫자 불변 17건 이관 |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_sim.js` | ⑤ 정의 정규식 · [10] ⑤ `pend5Row` |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_identity.js` | AD 합산 · ⑤ 기대식 · 배율 |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_proto.js` | 툴팁 3행 · 제거 화면 목록 · 9)-(6) |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_sync_chain.js` | `PROTO_DROPPED` · `PROTO_MENUS` |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_batch_symbols.py` | proto 시뮬 제외 · 없음 판정 |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_docnums.py` | AD 비중 · 못 |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_steps_all.py` | `ty_asset` 인자 |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/audit_xlsx_check.py` | facts 대조 2행 · ⑤ 칸 수식·문면 |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_final_terms.py` | I26 |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_crossscreen.py` | DAILY 파서 · 0건 가드 |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_0828.py` | G-1 예외 1건 |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_rows.js` | `goto` 대기 |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/sim_facts.py` | `pend5Row` |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/capture_shots.js` | 웹폰트 대기 · 봉인 `fontLoaded` |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_shots.js` | B5 · C0 · D4b |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verifiers.md` | 2026-09-04 절 · 곳수 · 원천 표 |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/request_register.md` | G-1 예외 표 1행 |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/shot_rects.json` | 촬영 봉인 갱신 |
| `/Users/semi/cursor/payhug-investor-admin/assets/shots/invest-assets.webp` · `invest-profit.webp` | 재촬영 (나머지 3장은 바이트 동일) |
| `/Users/semi/cursor/payhug-investor-glossary/assets/shots/*.webp` 5장 | 원본과 같은 바이트로 복사 (미커밋) |
| `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/step7v/run_all.sh` | 전종 실행기(`gate_prototype.js` 제외 · `verify_links` 용 8901 서버 포함) |
| `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/step7v/vlogs/` | 검사기별 로그 · `_summary.tsv` · `audit_xlsx_check_all.log` · `verify_proto_rerun.log` · `capture3.log` |
| `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/step7v/before/` | 수정 전 검사기 16종 · `glossary.html` · 옛 캡처 5장 · 옛 `shot_rects.json` |

검사기 실행이 갱신한 `*_result.json` 은 각 검사기의 정해진 출력 자리(`_pipeline/investor_admin/verify_*_result.json`)에 남아 있습니다.
