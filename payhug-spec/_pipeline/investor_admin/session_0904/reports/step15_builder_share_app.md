# step15 — 통합본(원본)에 「투자자 공유 정리」 적용 (2026-09-09)

정리 대상은 투자 자산 요약 카드 「투자실행액」「순현금」 아래 줄, 투자 자산 현황 표의 「비중」「보관」 두 열, 투자 시뮬레이션 결과 화면의 같은 자리, 「투자자산 현황」 엑셀·미리보기의 같은 두 열입니다. 생성기·검증기만 고치고 산출 HTML 은 재생성으로 맞췄습니다. git commit·push 는 하지 않았습니다.

## 지시 밖에서 바꾼 것 · 못 한 것

| 구분 | 내용 | 까닭 |
|---|---|---|
| 순서를 바꿈 | 재생성을 `build_xlsx.py` → `build_app.py` → `sync_assets_static.py` → `build_sim_static.py` 순으로 돌렸습니다 (지시는 `build_app.py` 가 먼저) | `build_app.py` 가 `assets/xlsx/*` 의 크기·생성일시를 읽어 `app.html` 의 엑셀 등록부(`size:`·`made:`)에 박습니다(`build_app.py:3476`). 엑셀을 뒤에 만들면 `app.html` 이 옛 크기(5.6 KB)를 적습니다 |
| 지시 밖 재생성 | `python3 sim_facts.py` 를 추가로 돌려 `sim_facts.json` 을 새 구조로 맞췄습니다 | `sim_facts.py` 에서 `share0`·`share1`·`shareSum` 을 걷어 냈으므로 파일도 같은 상태여야 합니다 (`verify_sim.js` 는 `--json` 으로 매번 새로 받지만 저장본도 함께 갱신) |
| 지시 밖 검증기 | `verify_identity.js` 를 함께 고쳤습니다 (지시 목록에 없음) | 현황 표 6·7번째 칸(`st[0][5]`·`c[6]`)에서 비중을 읽어 합 100 을 검사하던 자리 3곳이 새 구조에서 FAIL 이 되므로, 열 5·빈 셀을 검사하도록 바꿨습니다 |
| 그대로 둔 것 | `app.html` 엑셀 미리보기 시트의 격자(A~G 7칸, `cols` 폭 8개)와 낱장 `xls-assets-status.html` 의 `<colgroup>`·`col-head` | `renderXls()` 가 A~G 를 고정으로 그리고 2열짜리 `투자수익 현황` 시트도 같은 격자를 씁니다. 투자자산 현황은 5열이라 F·G 가 빈 셀(`c-empty`)입니다. 폭을 바꾸는 것은 결정된 것이 아니라 손대지 않았습니다 |
| 못 한 것 | 용어 해설(`glossary_manuscript.md:1092·1096·1129·1434·1501`)의 「보관 ㈜쿠콘」 표기·`anchor: th:보관` 2곳과 캡처 재촬영(`capture_shots.js` → `build_glossary.py`) | 지시 범위(통합본·낱장·엑셀·검증기) 밖입니다. 현황 표에 「보관」 열이 없어졌으므로 다음 캡처 재촬영 때 앵커가 잡히지 않습니다 — 원고 정리가 먼저 필요합니다 |
| 못 한 것 | `gate_prototype.js`·`bash sync_prototype.sh --dry-run` | 시연본 변환기(`scripts/sync_prototype.py`, 작업 트리에 사용자 수정분 있음)를 거치는 검사라 돌리지 않았습니다. 변환기 쪽은 사용자가 맡습니다 |
| 손대지 않음 | `prep_fig.py` `share()` · `roster16_apply.py` · `payhug-admin-web`·`payhug-merchant-web` · 메뉴 라벨 · 툴팁 8곳 · 가맹점별 표·엑셀 「비중」 열 · `<title>` · 「㈜테스트인베스트」 | 지시대로 |

## 고친 파일과 자리

### 생성기 (`/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/`)

| 파일 | 자리 | 현재 상태 |
|---|---|---|
| `build_app.py` | `:1734` | `RENDER['invest-assets']` — `mRatio` 만 계산 (`aRatio`·`rExec`·`rCash` 없음) |
| 〃 | `:1747` · `:1749` | 요약 카드 「투자실행액」「순현금」 — `summary-value` 로 카드가 닫힘, `summary-sub` 없음 |
| 〃 | `:1758-1759` | 현황 표 열머리 5 (`자산 구분 · 금액 (원) · 가중평균 금융일수 · 입금부족률 · 예상 연환산 수익률`) · 빈 행 `emptyRow(5, …)` |
| 〃 | `:1767` · `:1771` | 현황 표 행·합계 행 — 5칸 |
| 〃 | `:2097` · `:2125` | `simRun()` — `TOT` 다음에 `SH` 계산 없음 · `SIM.result` 에 `SH` 없음 |
| 〃 | `:2284` · `:2286` | 시뮬레이션 결과 요약 카드 「투자실행액」「순현금」 — `summary-sub` 없음 |
| 〃 | `:2314` · `:2317` · `:2320` · `:2323` | 시뮬레이션 현황 표 — 열머리 5 · 행 3건 5칸 |
| 〃 | `:2813` | `sheetData()` — `xRatio` 만 계산 (`sRatio` 없음) |
| 〃 | `:2816-2823` | 엑셀 미리보기 `assets-status` — 제목 `span:5` + 빈 셀 2 · 머리글 5 + 빈 셀 2 · 각 행 5칸 + 빈 셀 2 · 합계 행 같음 |
| 〃 | `:3450` · `:3452` | `_AST` (→ `ASSET_ROWS`) — `keeper:` 필드 없음 |
| `sync_assets_static.py` | `:112-121` | `CARD` 정규식이 `summary-sub` 없는 카드도 잡음 · `SUB`·`KEEP`·`SHARE_SUB`·`NO_SUB` |
| 〃 | `:124-131` `card_spec()` | 「투자자산」 `KEEP`(산식 라벨 그대로) · 「투자실행액」「순현금」 `None`(보조줄 없음) · 「예상 연환산 수익률」 값 |
| 〃 | `:134-141` `share_cards()` | 「비중 … · 보관 ㈜…」 줄을 걷고 두 카드에 보조줄이 없음을 단언 |
| 〃 | `:144-166` `summary_cards()` | 보조줄 `None` 이면 없음을 단언, `KEEP` 이면 그대로, 문자열이면 치환 |
| 〃 | `:170-171` · `:174-187` | `STATUS_TH`·`STATUS_COLS = 5` · `status_rows()` 3행 5칸 |
| 〃 | `:190-204` `status_head()` | 「자산 구분」 표 열머리에서 `비중`·`보관` 두 `<th>` 를 걷고 `colspan="7"` → `5`, 열머리 5 단언 |
| 〃 | `:207-211` `share_check()` | 낱장 전체에 `보관 ㈜`·`㈜쿠콘`·`<th>보관</th>`·`c-head">보관` 0 단언 |
| 〃 | `:438-452` `xls_status_head()` | 시트 제목 병합 5열 + 빈 셀 2 · 머리글 5 + 빈 셀 2 (이미 그 꼴이면 그대로) |
| 〃 | `:455-465` `xls_status_make()` | 시트 3행 — 5칸 + 빈 셀 2 |
| 〃 | `:493-512` `build_assets()` · `:528-533` `build_assets_empty()` · `:644` PLAN | `share_cards` → … → `status_head` → `status_table` → `share_check` / 빈 낱장도 같은 순서 / `xls-assets-status.html` 은 `xls_status_head` → `sheet` → `share_check` |
| 〃 | 머리 주석 `:8-14` | 자리 잡기 목록에 현황표 열 5·시트 5열 명시 |
| `build_sim_static.py` | `:83` · `:106` | `run()` — `SH` 계산·반환 없음, `ratios()` 함수 없음 |
| 〃 | `:193-198` | 결과 요약 카드 「투자실행액」「순현금」 — `summary-sub` 없음 |
| 〃 | `:223-234` | 현황 표 — 열머리 5 · 행 3건 5칸 |
| 〃 | `:348` | 실행 출력에서 「비중합」 항목 없음 |
| `build_xlsx.py` | `:30-32` | `EXEC_SHARE`·`CASH_SHARE` import 없음 |
| 〃 | `:257-267` `build_assets_status()` | 열 5 · 폭 5개 `[18.5, 16.5, 12.5, 14.5, 11.5]` · 병합 1행 5열 · 머리글 5 · 4~6행 5칸 |
| `sim_facts.py` | `:118-123` `snap()` · `:324` | `share0`·`share1`·`shareSum` 없음 · 출력 줄에서 비중 항목 없음 |

### 검증기 (같은 폴더)

| 파일 | 자리 | 검사 내용 |
|---|---|---|
| `verify_sim.js` | `:328` · `:339-344` | 현황 표 열머리 5 글자 그대로 · 3행 각 5칸 (`st[n].length === 5`) |
| 〃 | `:347-351` | 요약 카드 4장 — 「투자실행액」「순현금」 `sub === ''` |
| 〃 | `:396-399` | 순현금 2억 시나리오 — 순현금·투자자산 이동 + 현황 표 칸 `5,5,5` |
| 〃 | `:727-731` | 투자자산 규모·유휴 비율 시나리오 — 비중 칸 비교 없음, 합계 칸 5 |
| `verify_identity.js` | `:252-262` | 투자자산 항등식 — `stCols === '5,5,5'` |
| 〃 | `:281-286` | 비중 최대잉여법 — 가맹점별 표만 검사, 현황 표는 열머리 5·「비중/보관」 없음 |
| 〃 | `:435-447` | 엑셀 미리보기 현황 — 머리글 5 글자 그대로 · F·G 빈 셀 · 3행 꼬리 빈 셀 |
| `verify_crossscreen.py` | `:64-76` | 엑셀 실물 — 3행 머리글 `[…5개, None, None]` · 4행 F·G `None` · 5·6행 F·G `None` · 2행 아래 `㈜` 문자열 0 |

### 산출물 (`/Users/semi/cursor/payhug-investor-admin/`)

| 파일 | 자리 | 현재 상태 |
|---|---|---|
| `app.html` | `:1181-1182` | `ASSET_ROWS` 2행 — `keeper` 없음 |
| 〃 | `:1590-1605` | 엑셀 등록부 `size:'5.5 KB'`(투자자산현황) · `made:'2026-09-09 14:18'`(14파일) |
| 〃 | `:2169` · `:2182` · `:2184` · `:2193-2194` · `:2202` · `:2206` | 투자 자산 카드 2장 보조줄 없음 · 현황 표 열 5 · 빈 행 colspan 5 |
| 〃 | `:2530` · `:2558` · `:2717` · `:2719` · `:2747-2756` | 시뮬레이션 — `SH` 없음 · 카드 2장 보조줄 없음 · 현황 표 열 5 |
| 〃 | `:3244-3257` | 엑셀 미리보기 투자자산 현황 — 5열 + 빈 셀 2 |
| `invest-assets.html` | `:123-129` · `:152-158` · 현황 3행 | 카드 2장 보조줄 없음 · 열머리 5 · 행 5칸 |
| `invest-assets--download.html` | `:133-139` · `:162-168` · 현황 3행 | 같음 |
| `invest-assets--cert-confirm.html` | `:139-145` · `:168-174` · 현황 3행 | 같음 |
| `invest-assets--empty.html` | `:124-130` · `:153-159` · `:162` | 카드 2장 보조줄 없음 · 열머리 5 · `colspan="5"` |
| `invest-sim--result.html` | `:299-305` · `:339-342` | 카드 2장 보조줄 없음 · 현황 표 열 5 · 행 5칸 |
| `xls-assets-status.html` | `:108-109` · `:132-136` | 파일바 `5.5 KB`·`2026-09-09 14:18` · 제목 병합 5열 + 빈 셀 2 · 머리글 5 + 빈 셀 2 · 3행 5칸 + 빈 셀 2 |
| `assets/xlsx/투자자산현황_2026-08-27_2026-08-27.xlsx` | 5,603 B | 5열 · 「비중」「보관」「㈜쿠콘」「㈜페이허그」 0 |

## 재생성·검증 결과

| 순서 | 명령 | 결과 |
|---|---|---|
| 1 | `python3 build_xlsx.py` | 14파일 생성 · 미리보기 4종 파일바 동기화 (투자자산현황 5.5 KB) |
| 2 | `python3 build_app.py` | `app.html` 235,191 bytes / 3,813 lines · screens 16 |
| 3 | `python3 sync_assets_static.py` | `invest-assets` 4낱장 · `xls-assets-status.html` changed, 나머지 6 same · `--check` 재실행 11/11 OK(멱등) |
| 4 | `python3 build_sim_static.py` | `invest-sim.html`·`invest-sim--result.html` 기록 · W 3.04 · Ty 13.21% |
| 5 | `python3 sim_facts.py` | `sim_facts.json` 갱신 |
| 6 | `grep -c "보관 ㈜\|<th>보관</th>\|keeper" app.html invest-assets*.html invest-sim--result.html xls-assets-status.html` | 7파일 전부 **0** |
| 7 | `unzip -p …투자자산현황….xlsx \| grep -o "비중\|보관\|㈜쿠콘\|㈜페이허그" \| wc -l` | **0** |
| 8 | 헤드리스 Chrome DOM 확인 (`app.html#invest-assets` · `#invest-assets/empty` · `#xls-assets-status` · `#invest-sim/result`) | 카드 보조줄 = 「투자실행액 + 순현금」「가중평균 금융일수 … 기준」 2건만 · 현황 표 th 5 · 행 5칸 · 빈 행 colspan 5 · 시트 머리글 5 + F·G 빈 셀 · 시뮬 현황 th 5 · 「보관 ㈜」 0 |

| 검증기 | 판정 | 비고 |
|---|---|---|
| `node verify_app.js` | **123 / 123 PASS** · 콘솔 에러 0 · 죽은 컨트롤 0 | |
| `node verify_proto.js` | **118 / 118 PASS** · 콘솔 에러 0 · 죽은 컨트롤 0 | |
| `node verify_sim.js` | **93 / 93 PASS** | 새 검사 「현황 · 열머리 5」「행 (칸 5)」「카드 아래 줄 없음」 포함 |
| `node verify_identity.js` | **18 / 18 PASS** · 콘솔 에러 0 | 새 검사 「현황 표 칸 5」「엑셀 현황 5열」 포함 |
| `python3 verify_crossscreen.py` | 65건 · **PASS 62 · FAIL 3** | FAIL 3 = 용어 해설 duration 허용 블록·대출 어휘 (이전부터 FAIL 이던 문서 페이지 항목 G, 그대로) · 엑셀 4검사(머리글 5열 · 투자실행액 행 · 순현금·합계 · ㈜ 0) PASS |
| `python3 verify_final_terms.py` | **302 / 302 PASS** | |
| `python3 verify_0828.py` | **32 / 32 PASS** | |

## diff 요약 (`git -C /Users/semi/cursor/payhug-investor-admin diff --stat`)

| 파일 | 바뀐 줄 | 위 1~5 범위인가 |
|---|---|---|
| `app.html` | 82 (+37 −45) | 1·2·3·4·5 전부 해당 + **엑셀 등록부 `made:` 14건·`size:` 1건** (`:1590-1605`, 재생성 부산물) |
| `invest-assets.html` · `--download` · `--cert-confirm` | 각 −10 | 1·2 (카드 줄 2 · 열머리 2 · 행 꼬리 6) |
| `invest-assets--empty.html` | 6 (+1 −5) | 1·2 (카드 줄 2 · 열머리 2 · colspan 7→5) |
| `invest-sim--result.html` | 10 (+4 −6) | 3 |
| `xls-assets-status.html` | 14 (+7 −7) | 4 + 파일바 크기·생성일시 |
| `assets/xlsx/투자자산현황_2026-08-27_2026-08-27.xlsx` | 5,727 → 5,603 B | 4 |
| `assets/xlsx/*.xlsx` 나머지 13파일 | 각 −1 B | **지시 밖 부산물** — `openpyxl` 재저장으로 문서 속성의 생성 시각만 바뀜(값·서식 동일) |
| `xls-assets-merchant.html` · `xls-profit-daily.html` · `xls-profit-status.html` | 각 2 | **지시 밖 부산물** — 파일바 `생성일시` (`build_xlsx.sync_preview`) |
| `scripts/sync_prototype.py` | 34 | 작업 시작 전부터 있던 사용자 수정분 — 손대지 않음 |

파이프라인 폴더(`payhug-spec/_pipeline/investor_admin/`)에서 이 작업으로 바뀐 파일: `build_app.py` · `sync_assets_static.py` · `build_sim_static.py` · `build_xlsx.py` · `sim_facts.py` · `sim_facts.json` · `verify_sim.js` · `verify_identity.js` · `verify_crossscreen.py` · 검증기 실행 결과 `verify_app_result.json` · `verify_proto_result.json` · `verify_sim_result.json` · `verify_identity_result.json`. 같은 폴더의 `NEXT_SESSION.md` · `prep_fig.py` · `figma_ops_0828.json` · `session_0904/qa/figma_0909/*` 수정분은 이 작업과 무관합니다.

임시 파일: `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/builder_share_0909/` (패치 스크립트 4종 · 검증 로그 · DOM 덤프).
