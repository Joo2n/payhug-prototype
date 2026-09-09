# 지시 이행 검사 — 2026-09-09 두 번째 라운드(통합본 투자자 공유 정리)

검사 시각 2026-09-09 14:5x · 검사자 proto-orders · 파일 수정 0건(이 보고서만). 직전 라운드 판정은 `orders_0909.md`(시연본만).
근거는 전부 산출물 실측입니다. 보고서·대화 문장은 근거로 쓰지 않았고, 보고서 수치를 인용한 자리는 「보고서 값」이라 적었습니다.

## 요약

| 판정 | 건수 | 항목 |
|---|---|---|
| **됨** | **6** | A 통합본 원본 · B 시뮬 결과·미리보기 · C 엑셀 · D 생성기·검증기 · E 전체본 배포 · F 시연본 재동기화(경위 있음) |
| **일부** | **2** | G Figma(맵·근거 됨, 실물 확인 불가) · I 기록(NEXT_SESSION 재개 명령 순서 미반영) |
| **안 됨** | **1** | H 「한 번에 보고」 — 자발적 중간 보고 6건 |
| 확인 불가 | 1 (G 안) | Figma 파일 실물 — 도구 없음 |

## 사용자 지시별 판정

| 지시 | 언제 | 몇 번 | 판정 | 근거 |
|---|---|---|---|---|
| 끝나면 한 번에 말해·보고해 (중간 보고 0) | 9/8 07:55 · 9/8 09:40 · 어시스턴트 약속 9/9 14:05 | **사용자 2회 + 약속 1회** | **안 됨** | 세션 기록 idx 22872(14:04 KST 「통합도 고쳐야 하는데」) 이후 사용자 발언 0건인데 어시스턴트 텍스트 8건 = 질문 답 1(14:05, 483자) · API 오류 1(14:34) · **자발적 중간 보고 6**: 14:07(133자) · 14:11(122자, 「지시 추적 10건 이행·1건 안 지킴」 결과 포함) · 14:29(58자) · 14:29(96자) · 14:41(74자) · 14:50(65자, 「QA 21건·결함 0」 결과 포함). 마감 보고는 이 검사 뒤 예정 |
| 그 외에 임의로 수정하지 않도록 | 9/8 07:55 | 1 | **일부** | 지시 밖 변경 5건이 있고 사용자에게는 미고지(빌더 보고·NEXT_SESSION 에만): `verify_identity.js`(지시 목록에 이름 없음, `2e919a2` 28줄) · `python3 sim_facts.py` 재실행(`sim_facts.json`) · 주석 커밋 `d9af5a7`(`scripts/sync_prototype.py` 2줄) · xlsx 13파일 −1 B(docProps 시각) · `xls-assets-merchant/profit-daily/profit-status.html` 생성일시 각 2줄. 화면 값·문구 변화는 0(툴팁 10줄·사이드바 블록 458-521 · 제목 · 첫 화면 `d7ce377` 과 동일) |
| 통합본도 고쳐라 — 카드 아래 비중·보관 줄 · 현황 표 두 열 · 엑셀 두 열 | 9/9 14:04 (04:24 「쿠콘 보관 80% 등등 빼」의 통합본 적용) | 1 | 됨 | `app.html` `보관 ㈜`·`<th>보관</th>`·`keeper` 0 (남은 「보관」 1곳은 1134행 「서명값은 계약기록에 보관」, 다른 뜻) · 현황 표 머리 `app.html:2192-2193` 5열 · `d7ce377` 에 있던 2185·2188·2198·2208행 문구 없음 · 낱장 4(`invest-assets*.html`) 0 · `투자자산현황_2026-08-27_2026-08-27.xlsx` 5,603 B 머리 A3~E3 5열, 보관·비중·페이허그·쿠콘 0 |
| 통합본에만 있는 시뮬 결과 카드·표 · 엑셀 미리보기 시트 | 9/9 14:05 (어시스턴트가 범위로 밝힘) | 1 | 됨 | `app.html` `R.SH` 0 · 시뮬 결과 현황 표 th 5 (`app.html` 2732-2733행 부근) · 미리보기 `assets-status` 머리 `app.html:3264-3265` 5열 + `null,null` · `invest-sim--result.html:339` th 5 · `xls-assets-status.html:134` 머리 5열 · `verify_sim_result.json` baseline.statusHead 5열 |
| 그 상태를 프로토타입(시연본)으로 바로 이어가기 | 9/9 14:04 | 1 | 됨 | `payhug-investor-prototype` HEAD `7ba7f26` = origin/main · 배포 `/` sha256 `87441f4a…` = 로컬 `index.html` · `<title>PayHug 투자자 어드민</title>` · 배포본 `보관 ㈜`·`<th>보관</th>`·`keeper` 0 · xlsx 5,603 B |
| 배포도 바로 | 9/9 04:32(1라운드) → 이 라운드 어시스턴트 순서에 포함 | 1 | 됨 | 전체본 `app.html` md5 `0d4813ea…` 로컬=배포 · `invest-assets.html` `6d9d0c09…` 동일 · 배포 xlsx 5,603 B md5 `c88b9a2f…` 동일 · 배포 `보관 ㈜` 0. 관리 레포 origin/main = `d9af5a7`(배포 HTML 은 `7493d89` 와 동일 — `d9af5a7` 은 변환기 주석 2줄만) |
| 피그마 수정도 이어가기 | 9/9 04:32 | 1 | 일부 | 맵 `figma_map_investor.json` `source_commit`=`7493d89`·`prev_source_commit`=`d7ce377`·`source_commit_note_0909` 에 「재임포트 없음」 근거 기재. 근거 실측: `_fig/invest-assets.html`·`--download`·`--cert-confirm`·`--empty` 와 원본 낱장의 태그 제거 텍스트 차이 = 각 1줄 「투자 시뮬레이션」(사이드바 메뉴)뿐 · `_fig` 4장 `보관 ㈜` 0. **Figma 파일 실물은 확인 불가**(이 검사자에게 Figma 도구 없음). 맵의 옛 `source_commit_note`·`source_commit_state`·`staging_copy_note` 는 아직 `d7ce377` 기준 문장이라 새 주석과 혼재 |
| 내가 말한 대로 고쳤는지 검증·QA 에이전트로 확인 | 9/8 07:55 · 09:40 | 2 | 됨 | `step15_qa_share_app.md:96` PASS 21 · FAIL 0(배포본 CDP 실측) · `verify_sim_result.json` 93/93 · `verify_identity_result.json` 18/18 · `verify_app_result.json` menus 9·states 18·downloads 15·dead 0·console 0·실패 플래그 0 · `verify_proto_result.json` menus 8·states 16·dead 0·console 0 · `verify_crossscreen.py` 직접 실행 65건 PASS 62 · FAIL 3(용어 해설 duration·대출 어휘, 이전부터) |

## 확인 항목 A~J

| 항목 | 판정 | 실측 |
|---|---|---|
| A 통합본 원본 | 됨 | `git log`: `d9af5a7`(14:49 주석) ← `7493d89`(14:27 정리) ← `3978be3` ← `d7ce377`. `git diff --stat d7ce377 7493d89` = 25파일 = `app.html`(82줄) · 낱장 5 · `xls-*.html` 4 · xlsx 14 · `scripts/sync_prototype.py` — 기대 목록과 일치. 제목 `app.html:6` 「통합 프로토타입」 · 첫 화면 `:943` 「화면 설계(안)」 · 「㈜테스트인베스트」 4곳(527·581·598 …) · `tip-panel` 포함 10줄 `d7ce377` 과 diff 0 · 가맹점별 표 「비중」 `:2221`(IA_HEAD)·`:2255`(증명서) 유지 · 사이드바 458-521 블록 diff 0, 라벨 8(투자 자산·투자 수익·투자 시뮬레이션·가맹점·정산채권 양수·계약기록·쿠콘 관리 현금·비밀번호 변경) |
| B 시뮬 결과·미리보기 | 됨 | 위 표 4행 |
| C 엑셀 | 됨 | `투자자산현황_…xlsx` 5,603 B · sheet1 A1 「투자자산 현황 — 2026-08-27 / ㈜테스트인베스트」 · 3행 A~E 「자산 구분·금액 (원)·가중평균 금융일수·입금부족률·예상 연환산 수익률」 · 금칙어 0. `가맹점별투자자산_…xlsx` 6,108 B F3 「비중」 유지 |
| D 생성기·검증기 | 됨 | `build_app.py` keeper 0(보관 1 = 계약기록 문구) · `sync_assets_static.py` 정리 정규식·5열 단언(:120·:170·:196·:209·:440·:451) · `build_sim_static.py` 보관 0 · `build_xlsx.py:261` 5열 · `sim_facts.py` share0/1/Sum 없음 · `verify_sim.js`·`verify_identity.js:284·442`·`verify_crossscreen.py:64` 5열 검사. 재생성=현재본 여부: `build_app.py` 는 돌리지 않음(덮어씀). 빌더 보고 `app.html` 235,191 B = 실측 235,191 B(줄 수 보고 3,813 · `wc -l` 3,812 — 끝 개행 계산 차이, 추정) · 배포 md5 일치 |
| E 전체본 배포 | 됨 | 위 표 6행 |
| F 시연본 재동기화 | 됨 · 경위 | `git diff --stat 7a369bd 7ba7f26` = xlsx 14(13은 −1 B, 자산현황 5658→5603) + `index.html` 46줄. `index.html` 차이 내용: 등록부 `made` 14건 시각(2026-09-07 13:35 → 09-09 14:18, size 「5.5 KB」 그대로) · 데이터 행 `keeper:` 필드 2줄 삭제 · `aRatio/rExec/rCash` 변수·문자열 이음 등 코드 모양 7쌍 — 기대(등록부 시각·엑셀·xlsx)보다 범위가 넓지만 화면 결과는 같음(배포 게이트 통과). 로그: `sync_proto_0909c.log`(14:27) = `bash: sync_prototype.sh: No such file or directory` EXIT=127, 아무것도 안 함 · `sync_proto_0909d.log`(14:30) = 1~4단계(변환·게이트·push `7a369bd..7ba7f26`·배포 반영 3회차) 완료 → 5단계 배포 URL 게이트 PASS 5 뒤 `ReferenceError: go is not defined`(`gate_prototype.js:55`) EXIT=1 · 어시스턴트 재실행(세션 기록 idx 23041/23042, 14:37~14:40 KST) `node gate_prototype.js --url=https://payhug-investor-prototype.vercel.app/` → `grep -c PASS` 43 · 「게이트 통과 — 바깥으로 나가는 통로 0건」 |
| G Figma | 일부 | 위 표 7행 |
| H 한 번에 보고 | 안 됨 | 위 표 1행 |
| I QA·기록 | 일부 | `step15_builder_share_app.md`(14:25) 순서 변경·지시 밖 2건·못 한 것 기재 · `step15_qa_share_app.md:96` PASS 21 · FAIL 0 · `NEXT_SESSION.md:38` 전체본 `7493d89`·시연본 `7ba7f26` · `:61` N 행 「적용 완료」+남은 것. **미반영**: `NEXT_SESSION.md:68-71` 재개 명령이 `build_app.py` → … → `build_xlsx.py` 순서 그대로(빌더가 `build_xlsx` 선행이 필요하다고 보고한 순서와 다름) · HEAD `d9af5a7` 언급 없음(내용상 영향 없음) |
| J 다르게 처리 | 아래 표 | |

## 다르게 처리한 것

| 무엇 | 지시 | 실제 | 왜 | 고지 여부 |
|---|---|---|---|---|
| 재생성 순서 | `build_app.py` → `sync_assets_static.py` → `build_sim_static.py` → `build_xlsx.py`(빌더 프롬프트) | `build_xlsx.py` → `build_app.py` → … | `app.html` 등록부가 xlsx 크기·생성 시각을 박으므로 엑셀이 먼저 있어야 함(빌더 보고 :9) | 빌더 보고에만 · 사용자 미고지 · NEXT_SESSION 재개 명령은 옛 순서 |
| `verify_identity.js` 수정 | 검증기 목록에 이름 없음(「등」) | `2e919a2` 28줄 — 현황 표 비중 합 검사 → 열 5·비중·보관 없음 검사 | 비중 열이 없어져 옛 검사가 깨짐(빌더 보고 :11) | 빌더 보고에만 |
| `sim_facts.py` 재실행 | 파일 수정은 목록 안, 실행은 지시 없음 | `python3 sim_facts.py` → `sim_facts.json` share 항목 제거 | 낱장·검증기가 읽는 사실값 동기화(빌더 보고 :10) | 빌더 보고에만 |
| 통합본 탭 제목 | — | 「PayHug Admin — 통합 프로토타입」 그대로, 시연본만 변경 | 검토용 이름 | 어시스턴트 답 14:05 에서 고지(「다르게 원하시면 말씀해 주십시오」) |
| 용어 해설 원고·캡처 | — (어시스턴트 범위 밖) | `glossary_manuscript.md:1092·1096·1129·1434·1501` 「보관 ㈜쿠콘」·`anchor: th:보관` 그대로 · 캡처 `assets/shots/invest-assets.webp`(9/8 18:09, 정리 전 화면 — 「비중 80.0% · 보관 ㈜페이허그」·비중·보관 열 보임) · **전체본 배포 `glossary.html` 「보관 ㈜」 5곳 · `terms-edit.html` 1곳(둘 다 로컬=배포 md5 동일), 배포 첫 화면 `index.html:140·147` doc-card 로 한 번에 닿음** | 캡처 재촬영·원고 정리를 F·G 항목과 묶어 뒤로 둠(NEXT_SESSION N 행) | 사용자 미고지(NEXT_SESSION·빌더 보고 :13 에만) |
| 부산물 | — | xlsx 13파일 −1 B(docProps 생성 시각) · `xls-assets-merchant/profit-daily/profit-status.html` 「생성일시」 각 2줄 | `openpyxl` 재저장·`sync_preview` | 빌더 보고 :115-116 · QA :21 |
| 주석 커밋 `d9af5a7` | — | `scripts/sync_prototype.py` 주석·docstring 2줄(「시연본에만」 → 「원본에도 같은 정리, 이중 안전장치」) | 변환기 설명이 사실과 어긋남 | 없음 |
| 시연본 `index.html` 코드 차이 | 등록부 시각·엑셀만 | keeper 필드·죽은 비중 변수·문자열 이음 7쌍도 바뀜 | 원본이 정리된 뒤 변환기 정규식이 걷어낼 대상이 없어져 코드 모양이 달라짐 | 없음(결과 화면 동일) |

## 사용자에게 먼저 밝힐 것

1. 「한 번에 보고」를 어겼습니다 — 14:04 이후 자발적 중간 보고 6건(그중 2건은 결과 수치 포함).
2. 전체본 배포 안의 용어 해설(`glossary.html` 5곳 · `terms-edit.html` 1곳)과 캡처 `assets/shots/invest-assets.webp` 는 「보관 ㈜」가 남은 정리 전 화면이고, 배포 첫 화면 `index.html` 에서 한 번에 열립니다. 어시스턴트 범위 설명(14:05)에 이 제외가 없었습니다.
3. 지시 밖 변경: `verify_identity.js` 수정 · `sim_facts.py` 재실행 · 주석 커밋 `d9af5a7` · xlsx 13파일 −1 B · 미리보기 3장 생성일시.
4. 재생성 순서가 `build_xlsx` → `build_app` 로 바뀌었고, `NEXT_SESSION.md` 재개 명령(68-71행)은 옛 순서 그대로입니다.
5. Figma 파일 실물은 이 검사에서 확인하지 못했습니다(맵·`_fig` 텍스트 비교로만 「재임포트 불필요」 확인).
6. 시연본 동기화는 스크립트 경로 착오 1회(EXIT=127) 뒤 두 번째 실행에서 push·배포까지 끝났으나 배포 URL 게이트가 스크립트 오류(`go is not defined`)로 중단됐고, 수동 재실행으로 43 PASS 를 받았습니다. 게이트 스크립트 오류 자체는 고치지 않은 상태입니다.
