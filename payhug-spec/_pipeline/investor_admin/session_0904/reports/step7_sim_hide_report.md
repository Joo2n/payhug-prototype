# 7단계 — 시연본에서 투자 시뮬레이션 제외

## 하지 않은 것

| 항목 | 상태 | 까닭 |
|---|---|---|
| 시연본 저장소(`payhug-investor-prototype`) 쓰기·push | 하지 않음 | 지시 범위 밖 — 배포 단계에서 다른 사람이 `sync_prototype.sh` 로 돌립니다. 그 저장소의 `index.html` 은 지금도 `invest-sim` 24건이 있는 옛 판입니다. `git status` 의 `M index.html` 은 9/2 01:51 의 미커밋 동기화분(마지막 커밋 8/31)이라 이 작업과 무관합니다 |
| 통합본·낱장·`build_app.py`·`build_sim_static.py`·원장 수정 | 하지 않음 | 읽기만 했습니다 |
| 검사기 5종(`verify_proto.js` 등) 수정 | 하지 않음 | (다) 목록만 냈습니다 — 다음 조 |
| 게이트의 Ty 툴팁 검사 2건 FAIL 정리 | 하지 않음 | 시뮬 제거와 무관한 원본 툴팁 구성 변경입니다(아래 「부기」). 시뮬 항목 밖이라 손대지 않았습니다 |

## (가) 고친 자리

### `/Users/semi/cursor/payhug-investor-admin/scripts/sync_prototype.py`

| 줄 | 무엇 |
|---|---|
| 14 | 머리 docstring 「끊는 통로」에 투자 시뮬레이션 항목 |
| 30–31 | `SIM_BANNED` — 잔존 검사 정규식 6개 (`invest-sim` · `시뮬` · `simRun` · `simBond` · `\bSIM(?:\b|_)` · `\bsim-`) |
| 78–177 | `drop_sim(s)` 함수 — 아래 a~j |
| 81–86 | a) 사이드바 `<a class="nav-item" data-menu="invest-sim">…</a>` 제거 |
| 88–99 | b) `<!-- ═ 투자 시뮬레이션 ═ -->` 머리 주석부터 `<section data-screen="invest-sim">…</section>` 까지 제거 (머리 주석과 섹션 사이에 다른 `<section` 이 없을 때만 주석부터) |
| 101–109 | c) 전용 CSS — `/* ── 투자 시뮬레이션 ─` 부터 다음 `/* ── ` 블록 또는 `</style>` 앞까지 |
| 111–127 | d) 레지스터 — `DERIVE['invest-sim']` 한 줄 · `SEED['invest-sim']` 블록(괄호 균형 절단) · `STATE_META` 중첩 객체 · `MENU_OF`·`SCREEN_LABEL`·`FILE2SCREEN`·`STATEFILE` 문자열 대응 4건 · `SCREEN_ORDER` 원소 |
| 129–139 | e) JS 본문 — `/* ───────── 투자 시뮬레이션 ─` 부터 다음 `/* ───────── ` 블록 앞까지 (SIM 상태·산식·`simRun`·`simBond`·`RENDER`·`clearSimTimer`·입력 취급 전부). 끝을 못 찾으면 `fail` |
| 141–149 | f) `ACT['sim-add'·'sim-del'·'sim-run']` — `/* 투자 시뮬레이션 */` 부터 `/* ═══ 이벤트 바인딩 ═══ */` 앞까지 |
| 151–154 | g) `change`·`input` 바인딩의 `sim-var`·`sim-scale`·`sim-row` 분기 6줄 |
| 156–159 | h) `go()` 의 `clearSimTimer();` 호출 |
| 161–164 | i) 원장 `DAILY` 주석(app.html:1324)의 뒷문장 「— 투자 시뮬레이션 simBond 와 같은 앵커라 …」 → 「수수료 앵커는 순지급액이다(D-31).」 |
| 166–175 | j) `hashchange` — `readHash()` 가 닿는 화면을 못 찾으면 `go('invest-assets','default')`. 첫 진입은 원본 `init` 이 이미 투자 자산으로 보냅니다 |
| 220–221 | `transform()` 4) 단계에서 `drop_sim(s)` 호출 — 갤러리·`index` 레지스터 제거(1~3) 뒤, 로고·해시 링크 변환(5~7) 앞 |
| 223·238·250·262 | 단계 번호 4→5, 5→6, 6→7, 7→8 |
| 288–291 | `gate()` — `SIM_BANNED` 잔존 검사. 1건이라도 걸리면 `fail` → `index.html` 을 쓰지 않고 종료코드 1 |
| 293 | 통과 메시지에 「시뮬레이션 0」 |

### `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/gate_prototype.js`

| 줄 | 무엇 |
|---|---|
| 27–30 | `PROTO_DROPPED = ['index','invest-sim']` · `SIM_TRACE` 정규식 (변환기 `SIM_BANNED` 와 같은 목록) |
| 103–107 | 원본 `app.html` 실측에 화면별 상태 수 `per` · 사이드바 메뉴 목록 `nav` 추가 |
| 186–206 | 검사 「투자 시뮬레이션 없음」 — 메뉴·`<section>`·`SCREEN_ORDER`·`STATE_META`·`MENU_OF`·`FILE2SCREEN`·`STATEFILE`·전역 함수(`simRun`·`SIM`·`clearSimTimer`)·`outerHTML` 문자열 전부 0건, 사이드바 = 원본 메뉴 목록 − `invest-sim` (순서까지 일치) |
| 208–221 | 검사 「invest-sim 해시 진입 → 투자 자산」 — `about:blank` 경유 `#invest-sim/result` 첫 진입과, 계약기록 화면에서 `location.hash='#invest-sim'` 둘 다 `view=invest-assets` · `hash=#invest-assets` |
| 424–447 | 화면·상태 수 검사 — 「원본 − index 1화면·상태 동수」에서 「원본 − `PROTO_DROPPED` 화면 · 그 화면에 달린 상태」로. 기대값은 원본 실측 `per` 에서 계산 |

메뉴 수를 숫자로 박은 검사는 원래 없습니다(게이트 138~139줄 주석). 메뉴 7 은 「원본 8 − 1」로 실측 대조합니다.

## (나) 임시 변환 결과

임시 저장소 `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/proto_dry/` (`git init`). 원본 `app.html` 은 2026-09-04 22:12 판(다른 조 수정분 포함)으로 재확인했습니다.

| 확인 | 결과 |
|---|---|
| `--check-only` (대상 `payhug-investor-prototype`) | 종료코드 0 · ok 31건 · warn 0 · 쓰지 않음 |
| 실제 변환 (대상 `proto_dry`) | `index.html` 214,054 → 180,268 bytes · 자산 18건 역산 복사 |
| `index.html` 문자열 | `invest-sim` **0** · `시뮬` **0** · `simRun` **0** · `simBond` **0** · `SIM` **0** · `sim-` **0** |
| 인라인 스크립트 문법 | `node --check` 통과 |
| 사이드바 메뉴 | **7** — 투자 자산 · 투자 수익 · 가맹점 · 정산채권 양수 · 계약기록 · 쿠콘 관리 현금 · 비밀번호 변경 (라벨 원문 그대로) |
| 화면 `<section>` | 13 — 원본 15 에서 `index`·`invest-sim` 2건 제외 · 상태 17 (원본 18 − `invest-sim/result`) |

헤드리스 크롬으로 해시 진입(`about:blank` → `index.html#…`):

| 해시 | 선 화면 | 섹션 높이 |
|---|---|---|
| `#invest-assets` | 투자 자산 | 1276 |
| `#invest-profit` | 투자 수익 | 1244 |
| `#merchants` | 가맹점 | 693 |
| `#acquisition-list` | 정산채권 양수 | 503 |
| `#contracts` | 계약기록 | 658 |
| `#password` | 비밀번호 변경 | 565 |
| `#invest-sim` · `#invest-sim/result` · `#invest-sim.html` | 투자 자산 (해시 `#invest-assets` 로 정리) | 1276 |
| 계약기록에서 `location.hash='#invest-sim'` | 투자 자산 | — |

콘솔 오류 **0** (위 진입 전건 · 게이트 전 구간).

게이트 `DST_REPO=proto_dry node gate_prototype.js` — 시뮬 관련 항목 전부 PASS:

| 항목 | 판정 |
|---|---|
| 원본 app.html 실측 15화면 · 상태 18 | PASS |
| 화면 전건 렌더 13화면 · 상태 17 | PASS |
| 사이드바 메뉴 7 (SPA 6 · 쿠콘 1 외부링크) | PASS |
| 투자 시뮬레이션 없음 (메뉴 7 = 원본 8 − 1) | PASS |
| invest-sim 해시 진입 → 투자 자산 (첫 진입 · 화면 안 이동) | PASS |
| 형제 링크 0 · 금칙 문자열 0 · 외부 호스트 허용 밖 0 | PASS |
| 엑셀 도달 경로 14종 · 실물 수신 14건 바이트 일치 | PASS |
| 가로 오버플로 0 · 비중 합 100.0% · 투자실행금 일치 · 원장=롤업 | PASS |
| Ty수익율 ④⑤ = 원장 weekTy·weekTyAsset | PASS |
| 콘솔 에러 0 | PASS |
| 화면·상태 = 원본 − index·invest-sim | PASS |
| Ty수익율 ⑤ = ④ × PA/(PA+PEC) 되짚기 · 툴팁 PA·PEC = 원장 | **FAIL 2건 — 시뮬 무관(부기)** |

## (다) 시연본을 보는 검사기 — 시뮬을 기대하는 자리 (수정은 다음 조)

| 파일:줄 | 무엇 | 필요한 방향 |
|---|---|---|
| `verify_proto.js:162-165` | 상태 도달 경로 `['invest-sim','result', [nav invest-sim → click sim-go → wait]]` | 항목 제거 |
| `verify_proto.js:427` | 활성 표식 점검 `TARGETS` 의 `['invest-sim','default'],['invest-sim','result']` | 제거 |
| `verify_proto.js:699` | 6) 레이아웃 점검 `T` 의 같은 2건 | 제거 |
| `verify_proto.js:736` | 7) 탈출 통로 점검 `TARGETS` 의 같은 2건 | 제거 |
| `verify_proto.js:781` | 8) 가로 오버플로 `T` 의 같은 2건 | 제거 |
| `verify_sync_chain.js:71` | `PROTO_DROPPED = ['index']` — C 시연 화면·상태 구성 대조 기준 | `'invest-sim'` 추가 |
| `verify_sync_chain.js:80·325·388` | `SIDEBAR_MENUS` 를 정본 `app.html` 실측(8)으로 채워 시연본과 동수 요구 | 시연본 기대 = 정본 − 1 |
| `verify_batch_symbols.py:393-428` | 드라이버 `readSim()`·`runSim()` — `section[data-screen="invest-sim"]` 에서 표를 읽음 | proto 대상에서 호출 제외 |
| `verify_batch_symbols.py:478-484` | 드라이버가 app·proto 두 대상 모두에서 `#invest-sim` 진입 후 씨앗·클램프 2회 실행 (`waitFor` 가 시연본에서 시간 초과) | `t.key == 'app'` 일 때만 |
| `verify_batch_symbols.py:932-946` | 3절 `for key in ('app','proto')` — `simSeed` 의 채권별 산출·일별 합계 PSD 검사 | proto 제외 |
| `verify_batch_symbols.py:1266-1298` | 5-e `for key in ('app','proto')` — `simClampNeg`·`simClampPos`·`simSeed` 클램프 검사 | proto 제외 |
| `verify_batch_symbols.py:1117` | 시연본 `index.html` 에서 `[2번 이미지]` 기호 주석을 훑음 — 시뮬 블록의 주석이라 시연본에서는 0건 | 기대 없음 · 영향 없음(추정) |
| `verify_deployed.py` | 시뮬 기대 없음 (`NEED_APP`·`BAN_APP` 에 시뮬 문자열 없음) | — |
| `verify_shortfall.py` | 시뮬 기대 없음 (proto 는 `입금부족률` 툴팁 파일 훑기·크롬 조작만) | — |

## 부기 — 게이트 FAIL 2건은 시뮬 제거와 무관

| 근거 | 내용 |
|---|---|
| 게이트가 찾는 것 | 투자 수익 「투자자산 대비」 칸 툴팁의 `PA` 행 (`gate_prototype.js` Ty 되짚기·툴팁 대조) |
| 원본 `app.html:2527-2528` | 그 칸의 툴팁 행은 `PYa` · `Σ( Ai × Di )` · `PEC` · `EC` — `PA` 행이 없음 |
| 시연본과 원본 대조 | 투자 수익 툴팁 코드 35줄(app.html 2506~2540)이 시연본 `index.html` 에 전건 그대로 있음 — 변환기는 이 자리를 건드리지 않음 |
| 판정 | 원본 툴팁 구성 변경(「⑤ 단일 원천 · ⑥ 배선」 커밋 이후)에 게이트 Ty 검사가 뒤처진 것. 그 항목 담당 조 몫 |

## 파일

| 경로 | 무엇 |
|---|---|
| `/Users/semi/cursor/payhug-investor-admin/scripts/sync_prototype.py` | 변환기 — 시뮬레이션 제거 단계·잔존 검사 |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/gate_prototype.js` | 게이트 — 시뮬 없음·해시 진입·화면 수 기준 |
| `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/proto_dry/index.html` | 임시 변환 결과 (시연본 저장소에는 쓰지 않음) |
| `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/gate_dry.log` | 게이트 실행 로그 |
| `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/hash_open.js` | 해시 진입 헤드리스 확인 스크립트 |
