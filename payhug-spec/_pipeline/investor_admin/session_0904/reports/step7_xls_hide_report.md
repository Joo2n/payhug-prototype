# 7단계 — 시연본에서 엑셀 미리보기 4종 제외

## 하지 않은 것

| 항목 | 상태 | 까닭 |
|---|---|---|
| 시연본 저장소(`payhug-investor-prototype`) 쓰기·push | 하지 않음 | 지시 범위 밖. 그 저장소의 `index.html`·`README.md`(「화면 13개·상태 18개」)는 옛 판 그대로입니다 |
| 통합본 `app.html`·낱장 `xls-*.html`·`build_app.py`·원장 수정 | 하지 않음 | 읽기만 했습니다. 다른 조가 로그인 카드를 고치는 중이라 `app.html` 은 2026-09-04 22:14 판(245,015 B)으로 읽었습니다 |
| 검사기 5종(`verify_proto.js` 등) 수정 | 하지 않음 | (다) 목록만 냈습니다 |
| `assets/sheet.css` 링크 제거 | 하지 않음 | `.back-link` 가 `sheet.css` 에만 정의돼 있고 증명서 화면(`app.html:644`)이 씁니다. 링크를 빼면 증명서의 「투자 자산」 뒤로가기가 맨 글자가 됩니다. 시연본에 `sheet.css` 는 남고, 잔존 검사는 시트 DOM 클래스·함수명만 봅니다 |
| 게이트 Ty 툴팁 FAIL 2건 | 하지 않음 | 앞 조 부기와 같은 원인(`app.html` 툴팁에 `PA` 행 없음). 미리보기 제거와 무관합니다 |

## 앞 조와 다르게 한 것

| 항목 | 내용 |
|---|---|
| `hashchange` | 새로 손대지 않았습니다. `#xls-*` 해시는 `readHash()` 가 `null` 을 내고, 앞 조가 넣은 분기(`drop_sim` j)와 `go()` 자체의 폴백(`app.html:2157 if(!SEC(screen)) screen = 'invest-assets'`)이 투자 자산으로 보냅니다. 실측은 (나) 표 |
| 「미리보기로 가는 링크」 | 통합본에 투자 자산·투자 수익 화면에서 미리보기 뷰로 가는 링크(`data-nav="xls-…"`·`href="#xls-…"`·`go('xls-…')`)는 0건입니다(`app.html` 전문 검색). 미리보기 뷰는 해시·`FILE2SCREEN`(`xls-*.html`)·랜딩 갤러리로만 닿았고, 그 셋을 다 끊었습니다. 「엑셀 다운로드」 버튼은 원래부터 `ACT['xls-open'] → pullFile → a[download]` 직행(`app.html:3563-3580`)이라 손대지 않았습니다 |

## (가) 고친 자리

### `/Users/semi/cursor/payhug-investor-admin/scripts/sync_prototype.py`

| 줄 | 무엇 |
|---|---|
| 15 | 머리 docstring 「끊는 통로」에 엑셀 미리보기 항목 |
| 33–37 | `XLS_BANNED` — 잔존 검사 정규식 10개: `xls-assets-status` · `xls-assets-merchant` · `xls-profit` · `\bsheet-(?:frame\|tabs\|scroll\|tab)\b` · `class="sheet"` · `\b(?:sheetRow\|sheetData\|sheetName\|renderXls)\b` · `data-mount="(?:filebar\|sheettabs\|sheet)"` · `\bfile-bar\b` · `xls-get` · `미리보기 화면` |
| 185–244 | `drop_xls_preview(s)` 함수 — 아래 a~e |
| 190–195 | a) `<section data-screen="xls-…">…</section>` 4건 제거 |
| 197–212 | b) `XLSX` 레지스터 — 파일 없이 미리보기 화면만 가리키던 `'profit-status'`·`'profit-daily'` 2건 제거 · 14건의 `screen:` 필드 제거(`file`·`size`·`made`·`sheet`·`from` 은 그대로) · 머리 주석(`app.html:1717`)과 `xlsKey` 주석(`:1739`)의 미리보기 문장 제거. `var XLSX = {` 블록 안에서만 치환 |
| 214–222 | c) 레지스터 — `MENU_OF`·`SCREEN_LABEL`·`FILE2SCREEN` 문자열 대응 12건(말미 무쉼표 1건 별도 패턴) · `STATE_META` 4건 · `SCREEN_ORDER` 4건. 패턴은 `'xls-(?:assets\|profit)-…'` 로 한정 |
| 224–234 | d) 시트 JS — `/* ───────── 엑셀 미리보기 4종 ───────── */` 부터 마지막 `RENDER['xls-…']` 줄까지(`sheetRow`·`sheetData`·`sheetName`·`renderXls`·`RENDER` 4건). 그 사이에 다른 블록 머리가 끼면 `fail` |
| 236–243 | e) 파일바 「엑셀 파일 내려받기」 핸들러 `ACT['xls-get']`(괄호 균형 절단) · `KEEP_DEFAULT` 의 `'xls-get'` |
| 291–292 | `transform()` 5) 단계에서 `drop_xls_preview(s)` 호출 — `drop_sim` 뒤, 로고·해시 링크 변환 앞 |
| 294 · 309 · 321 · 333 | 단계 번호 5→6, 6→7, 7→8, 8→9 |
| 363–366 | `gate()` — `XLS_BANNED` 잔존 검사. 1건이라도 걸리면 `fail` → `index.html` 을 쓰지 않고 종료코드 1 |
| 368 | 통과 메시지에 「엑셀 미리보기 0」 |

다운로드 버튼 유지 — `ACT['xls-open']`·`pullFile`·`xlsBusy`·`syncToast`(다운로드 완료 상태)·`IA.downloaded` 는 건드리지 않았습니다. 자산 역산 `wanted_assets()` 는 `file:'…xlsx'` 를 세므로 14벌이 계속 복사됩니다(실측 아래).

### `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/gate_prototype.js`

| 줄 | 무엇 |
|---|---|
| 27–28 | `PROTO_DROPPED = ['index','invest-sim','xls-assets-status','xls-assets-merchant','xls-profit-status','xls-profit-daily']` |
| 31–33 | `XLS_TRACE` 정규식 (변환기 `XLS_BANNED` 와 같은 목록) |
| 110–111 | 원본 `app.html` 실측에 `XLSX` 파일 목록 `xls`(파일이 있는 키만) 추가 |
| 227–254 | 검사 「엑셀 미리보기 없음」 — `section[data-screen^="xls-"]`·시트·파일바 DOM 0, `SCREEN_ORDER`·`STATE_META`·`MENU_OF`·`SCREEN_LABEL`·`RENDER`·`FILE2SCREEN`·`STATEFILE` 에 xls 뷰 0, 전역 함수 `renderXls`·`sheetData`·`sheetRow`·`sheetName` 미정의, `ACT['xls-get']`·`KEEP_DEFAULT` 의 `xls-get` 없음, `XLSX` 전건이 `file` 을 갖고 `screen` 이 xls 뷰를 가리키지 않음, `outerHTML` 문자열 0건 |
| 256–275 | 검사 「엑셀 다운로드 = 실물 xlsx 직행」 — `XLSX` 파일 목록이 원본 실측과 같고(순서까지) 전건이 `REPO/assets/xlsx/` 에 실재, `pullFile` 이 `a.download` 를 쓰고 `ACT['xls-open']` 이 `'assets/xlsx/'` 를 부름, `[data-act="xls-open"]` 버튼 4개가 기본 상태에서 파일에 닿음. 실제 수신·바이트 일치는 기존 5) 가 봅니다 |
| 277–292 | 검사 「xls-* 해시 진입 → 투자 자산」 — `about:blank` 경유 첫 진입 4종과, 투자 수익 화면에서 `location.hash='#xls-assets-status'` 모두 `view=invest-assets` · `state=default` · `hash=#invest-assets` |
| 336 | 5) 주석에서 「미리보기 화면을 가리키는 키」 문구 제거 |
| 506 | 화면·상태 수 검사의 `dropWant` 를 원본 `SCREEN_ORDER` 순서로 뽑음 — 앞서는 `PROTO_DROPPED` 순서라 빠진 화면 목록(원본 순서)과 JSON 비교가 어긋났습니다 |

## (나) 임시 변환 결과

임시 저장소 `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/proto_dry/` 에 다시 변환. 원본 `app.html` 은 2026-09-04 22:14 판.

| 확인 | 결과 |
|---|---|
| `--check-only` (대상 `payhug-investor-prototype`) | 종료코드 0 · ok 41건 · warn 0 · 쓰지 않음 |
| 실제 변환 (대상 `proto_dry`) | `index.html` 214,185 → 167,894 자(191,943 B) · 자산 18건 역산 복사(xlsx 14 · docs 2 · css 2) |
| 변환 로그 (엑셀 미리보기 단계) | `<section>` 4 · XLSX 미리보기 자리 2 · `screen` 필드 14 · 주석 2 · 문자열 대응 11+1 · `STATE_META` 4 · `SCREEN_ORDER` 4 · 시트 JS 1블록 · `ACT['xls-get']` 1 · `KEEP_DEFAULT` 1 |
| `index.html` 문자열 | `xls-assets-status` **0** · `xls-assets-merchant` **0** · `xls-profit` **0** · `sheet-frame`·`sheet-tabs`·`sheet-scroll`·`class="sheet"` **0** · `sheetRow`·`sheetData`·`sheetName`·`renderXls` **0** · `file-bar`·`filebar`·`sheettabs` **0** · `xls-get` **0** · `미리보기` **0** · `invest-sim`·`시뮬` **0** |
| `assets/sheet.css` 링크 | 1건 유지(12행) — `.back-link` 용 |
| 인라인 스크립트 문법 | `node --check` 통과 |
| `XLSX` 레지스터 | 14건 전건 `file` 보유 · `screen` 필드 없음 |
| `SCREEN_ORDER` | `login · invest-assets · certificate · invest-profit · merchants · acquisition-list · contracts · coocon · password` (9) |
| `FILE2SCREEN` | 9건 — `xls-*.html` 0 |
| `KEEP_DEFAULT` | `cert-pdf · aq-chk · ct-chk · ct-all · aq-file · ct-doc · pf-date` |
| 사이드바 메뉴 | **7** — 투자 자산 · 투자 수익 · 가맹점 · 정산채권 양수 · 계약기록 · 쿠콘 관리 현금 · 비밀번호 변경 |
| 화면 `<section>` | 9 — 원본 15 에서 `index`·`invest-sim`·xls 4 제외 · 상태 17 |
| 「엑셀 다운로드」 버튼 `[data-act="xls-open"]` | 4 |

헤드리스 크롬 해시 진입(`about:blank` → `index.html#…`) — `hash_open_xls.js`:

| 해시 | 선 화면 | 섹션 높이 | 정리된 해시 |
|---|---|---|---|
| `#invest-assets` | 투자 자산 | 1276 | `#invest-assets` |
| `#invest-profit` | 투자 수익 | 1244 | `#invest-profit` |
| `#merchants` | 가맹점 | 693 | `#merchants` |
| `#acquisition-list` | 정산채권 양수 | 503 | `#acquisition-list` |
| `#contracts` | 계약기록 | 658 | `#contracts` |
| `#password` | 비밀번호 변경 | 565 | `#password` |
| `#xls-assets-status` · `#xls-assets-merchant` · `#xls-profit-status` · `#xls-profit-daily` · `#xls-profit-status.html` · `#invest-sim` | 투자 자산 | 1276 | `#invest-assets` |
| 투자 수익에서 `location.hash='#xls-assets-merchant'` | 투자 자산 | — | `#invest-assets` |

콘솔 오류 **0**.

「엑셀 다운로드」 버튼 4개 실측 — `dl_probe.js` (헤드리스 크롬, 내려받기 폴더 감시):

| 버튼 | 내려온 파일 | 바이트(수신/원본) | 누른 뒤 화면·상태 | 버튼 라벨 | 토스트 |
|---|---|---|---|---|---|
| 투자 자산 › 현황 | `투자자산현황_2026-08-27_2026-08-27.xlsx` | 5,737 / 5,737 | `invest-assets/default` | 엑셀 다운로드 | `… 내려받기 완료` |
| 투자 자산 › 가맹점별 투자자산 | `가맹점별투자자산_2026-08-27_2026-08-27.xlsx` | 6,117 / 6,117 | `invest-assets/download` (`#invest-assets/download`) | **다운로드 완료** (`is-done`) | `… 내려받기 완료` |
| 투자 수익 › 수익 현황 | `투자수익현황_2026-08-20_2026-08-26.xlsx` | 5,471 / 5,471 | `invest-profit/default` | 엑셀 다운로드 | `… 내려받기 완료` |
| 투자 수익 › 일별 투자수익 | `일별투자수익_2026-08-20_2026-08-26.xlsx` | 5,876 / 5,876 | `invest-profit/default` | 엑셀 다운로드 | `… 내려받기 완료` |

누르는 동안 라벨은 4건 모두 「다운로드 중...」, 화면 이동 없음.

음성 확인 — 시트 JS 머리 주석을 바꿔 제거가 안 되게 한 사본(`neg_xls/app.html`)으로 변환: `FAIL 엑셀 미리보기 잔존` 6건 → 종료코드 **1**, `dst/` 에 파일 0.

게이트 `DST_REPO=proto_dry node gate_prototype.js` — `gate_dry_xls.log`:

| 항목 | 판정 |
|---|---|
| 원본 app.html 실측 15화면 · 상태 18 | PASS |
| 화면 전건 렌더 9화면 · 상태 17 | PASS |
| 사이드바 메뉴 7 (SPA 6 · 쿠콘 1 외부링크) | PASS |
| 투자 시뮬레이션 없음 (메뉴 7 = 원본 8 − 1) · invest-sim 해시 진입 → 투자 자산 | PASS |
| **엑셀 미리보기 없음 (뷰 4종 · 레지스터 · 시트 JS · 파일바 · 문자열)** | **PASS** |
| **엑셀 다운로드 = 실물 xlsx 직행 (레지스터 14건 = 원본 14 · 자산 실재 · 버튼 4)** | **PASS** |
| **xls-* 해시 진입 → 투자 자산 (첫 진입 4종 · 화면 안 이동)** | **PASS** |
| 형제 링크 0 · 금칙 문자열 0 · 외부 호스트 허용 밖 0 (링크 208 — 해시 156 · 자산 2) | PASS |
| 엑셀 도달 경로 14종 · 실물 수신 14건 바이트 일치 | PASS |
| 가로 오버플로 0 · 비중 합 100.0% · 투자실행금 일치 · 원장 = 롤업 | PASS |
| Ty수익율 ④ ⑤ = 원장 weekTy · weekTyAsset | PASS |
| 콘솔 에러 0 | PASS |
| **화면·상태 = 원본 − index·xls 4·invest-sim (9화면 · 상태 17)** | **PASS** |
| Ty수익율 ⑤ = ④ × PA/(PA+PEC) 되짚기 · 툴팁 PA·PEC = 원장 | **FAIL 2건 — 앞 조 부기와 동일(툴팁에 `PA` 행 없음) · 미리보기 무관** |

## (다) 시연본을 보는 검사기 — 미리보기를 기대하는 자리 (수정은 다음 조)

| 파일:줄 | 무엇 | 필요한 방향 |
|---|---|---|
| `verify_proto.js:432-433` | 활성 표식 점검 `TARGETS` 의 `['xls-assets-status','default']` 외 3건 | 4건 제거 — `go('xls-…')` 는 이제 투자 자산으로 떨어져 화면 불일치로 판정됨 |
| `verify_proto.js:704-705` | 6) 레이아웃 점검 `T` 의 같은 4건 | 제거 |
| `verify_proto.js:741-742` | 7) 탈출 통로 점검 `TARGETS` 의 같은 4건 | 제거 |
| `verify_proto.js:785` | 8) 가로 오버플로 `T` 의 같은 4건 | 제거 |
| `verify_proto.js:804` | 9) 숫자 불변 주석 — 「xls-profit-status 를 더한다」 | 문구 정리 |
| `verify_proto.js:871-889` | 9)-(4) 엑셀 서식 미리보기 — `go('xls-profit-daily')`·`SECQ('xls-profit-daily','table tr')`·`xls-profit-status`·`xls-assets-status` 표를 읽어 원장과 대조 | 시연본 대상에서 블록 제거. 같은 대조는 통합본 `verify_app.js`·`verify_identity.js:413-431`·`verify_period.js:384-443` 이 계속 봄 |
| `verify_proto.js:296` | 3) 엑셀 — 「화면이 미리보기로 넘어가지 않는다」 판정 | 그대로 — 이번 상태와 일치 |
| `verify_sync_chain.js:71` | `PROTO_DROPPED = ['index']` — C 시연 화면·상태 구성 대조 기준(`:369·376`) | `'invest-sim'` 과 xls 4종 추가(게이트와 같은 목록) |
| `verify_sync_chain.js:80·325` | `SIDEBAR_MENUS` 정본 실측(8) | 앞 조 목록과 같음 — 시연본 기대 = 정본 − 1 |
| `verify_batch_symbols.py` · `verify_shortfall.py` · `verify_deployed.py` | xls 뷰·시트 함수 기대 없음(`xls-`·`renderXls`·`sheetData` 0건) | — |
| `payhug-investor-prototype/README.md:3` | 「화면 13개·상태 18개」 | 동기화 때 9·17 로(시연본 저장소 쓰기는 다음 단계) |

## 파일

| 경로 | 무엇 |
|---|---|
| `/Users/semi/cursor/payhug-investor-admin/scripts/sync_prototype.py` | 변환기 — 엑셀 미리보기 제거 단계 `drop_xls_preview()`·`XLS_BANNED` 잔존 검사 |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/gate_prototype.js` | 게이트 — 미리보기 없음·다운로드 직행·xls 해시 진입·화면 수 기준 |
| `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/proto_dry/index.html` | 임시 변환 결과 (시연본 저장소에는 쓰지 않음) |
| `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/gate_dry_xls.log` | 게이트 실행 로그 |
| `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/hash_open_xls.js` | 해시 진입 헤드리스 확인 스크립트(xls 4종 포함) |
| `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/dl_probe.js` | 다운로드 버튼 4개 실측 스크립트 |
| `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/neg_xls/` | 잔존 검사 음성 확인용 사본 |
