# 검증기 명부

전부 `_pipeline/investor_admin/` 에서 실행. 대상 저장소는 각 파일 머리말에 적혀 있다.

## 기대값 원천

검증기에 숫자를 손으로 적지 않는다. 기대값은 모델이 낸다.

| 원천 | 내는 것 | 읽는 검증기 |
|---|---|---|
| `daily_ledger.py` → `ledger_facts.json` | 투자실행액·순현금·투자자산·W·Ty·S·로스터 명단·원장 구간·W 범위 가드(`wBound`)·채권 Di 범위 가드(`diBound`)·일별 행값(`tyByDate` = 날짜 → [W, Ty, 투자실행금, 투자수익, 상환액, 채권매입수수료, 부족액 차감]) | `verify_identity` · `verify_proto` · `verify_period` · `verify_app` · `verify_rows` · `verify_sync_chain` · `verify_deployed` · `verify_sim` · `verify_0828` |
| `sim_facts.py` (`build_app.py` 씨앗 8행·`SIM_DEFAULT`·`SIM_DUR` 을 읽고 `build_sim_static.py` 의 산식을 그대로 부른다) | 투자 시뮬레이션 시나리오 8종의 화면 표기값 | `verify_sim` (`python3 sim_facts.py --json` 을 그 자리에서 돌려 받는다 — 파일이 낡을 자리가 없다) |
| `roster16_model.py` · `platform_duration.py` | 로스터 원장·플랫폼별 만기 실측 | `verify_crossscreen` |

로스터 곳수는 `ledger_facts.json` 의 `merchants` 길이 하나에서 나온다. 검증기에 `16` 을 적지 않는다.

| 검증기 | 대상 | 보는 것 |
|---|---|---|
| `verify_0828.py` | `payhug-investor-admin` 배포 HTML 전량(루트 + `assets/*.html`) · `assets/docs/*.pdf` | 8/28 미팅 결론 32항목. 화면 텍스트에 `<script>` 안 문자열 리터럴을 포함한다 |
| `verify_0828_negative.py` | 위 검증기 자신 | 음성 시험 — 네 범위(`<script>` 문자열 · `assets/*.html` · PDF 본문 · 명단 밖 낱장)에 위반 16가지를 심어 전부 FAIL 로 잡히는지 |
| `verify_app.js` | `payhug-investor-admin/app.html` | 죽은 컨트롤·상태 도달·레이아웃·콘솔·모달 닫힘 경로(D-40) |
| `verify_proto.js` | `payhug-investor-prototype/index.html` | 시연본 전건 — 메뉴·상태·다운로드 실물·바깥 통로·모달 닫힘 경로(D-40, 배경·본문·ESC 로 안 닫힘 + X·닫기가 실제로 닫음) |
| `verify_sync_chain.js` | 원본 ↔ 시연본 | 변환 손실 |
| `verify_rows.js` | 표 | 행·순번·선택 |
| `verify_toast.js` | 다운로드 | 토스트 문구 ↔ 실물 바이트 (엑셀 14종 · 프리셋 6조합 포함) |
| `verify_links.py` | 링크·자산 | 전건 200 |
| `verify_crossscreen.py` | 화면 간 | 숫자 일치 · 수익 현황 카드 ↔ 같은 기간 엑셀 실물 |
| `verify_identity.js` | 산식 | 항등식 |
| `verify_period.js` | 기간 필터 | 기간·집계 단위 조작 · 낱장/미리보기 엑셀 링크가 그 기간 파일인지 |
| `verify_password.js` | 비밀번호 화면 | 실물 대조 |
| `verify_sim.js` | 투자 시뮬레이션 | 입력 → 산출 |
| `verify_glossary.js` | 용어 해설 | 앵커 도달·가로 넘침·본문 링크 대상·기호 검색·목차 |
| `verify_glossary5.js` | 용어 카드 | 5필드·캡처 마커·라이트박스·구버전 링크(전 HTML) |
| `verify_shotmarks.py` | 캡처 | 마커 |
| `verify_feasibility.js` | 구현 가능성 문서 | 근거 인용 |
| `verify_deployed.py` | 배포 3주소 | 익명 수신 바이트로 표식 대조 |
| `gate_prototype.js` · `gate_glossary.js` | 배포 게이트 | push 전 차단 |
| `sync_counts.py --check` | 문서 개수 표기 | `counts.py` 파일 실측 + 문서 자신의 판정 행 실측(구현 가능성 5표 · 화면별 기능 명세 §3) ↔ 손으로 쓰는 문서 + `README.md` 재생성분(어긋나면 종료코드 1) |
| `sync_profit_static.py` | 투자 수익 낱장 5종 | 검색 카드·표를 다시 찍고 카드↔표 기간 일치를 assert |
| `sync_assets_static.py --check` | 투자자산 낱장 3종 · 증명서 · 투자자산 엑셀 미리보기 2종 · 가맹점 낱장 2종(기본·검색 적용) · 계약기록 낱장 2종 | 요약 카드 4장·현황표 3행·로스터 표·계약기록 표·검색 적용 표·시트 행·페이지네이션·건수를 `roster16_model` 에서 다시 그려 낱장과 바이트 대조(어긋나면 종료코드 1). 자리는 `summary-label` · `<thead>` 첫 칸 · `c-head` 행으로 잡고 못 잡으면 AssertionError — 값을 locator 로 쓰지 않아 0건 치환이 성공으로 보이지 않는다 |
| `build_readme.py --check` | `README.md` | 개수·화면 목록이 실측과 같은지 (`sync_counts.py --check` 가 함께 돈다) |

## 캡처 동결 범위

캡처 이미지(`assets/shots/*.webp`) · 좌표(`shot_rects.json` 의 `x`·`y`·`w`·`h`) · 앵커 `text` 는 동결한다. `glossary_manuscript.md` 의 `[[shot: … ]]` 줄에서 이미지 경로·좌표 지정은 손대지 않는다.

캡션은 이미지 밖 텍스트라 동결 대상이 아니다. 현행 화면값과 어긋나면 갱신한다. 갱신은 `build_glossary.py` 의 `CAP_FIX` 표 한 곳에서만 하고, `verify_shotmarks.py` 가 그 표를 불러 앵커 `text` 에도 똑같이 걸어 대조한다 — 양쪽에 같은 변환을 걸 뿐이라 캡션↔앵커 대조는 완전일치 그대로다. 표를 거치지 않고 캡션만 고치면 그 자리에서 FAIL 로 걸린다.

## 판정하는 것 / 출력만 하는 것

검사처럼 보이는데 값을 찍기만 하고 통과·실패를 안 가르는 자리가 있으면, 읽는 사람은 검사되고 있다고 믿는다.
그래서 검증기마다 두 칸을 갈라 적는다. **오른쪽 칸에 있는 것은 지금 아무도 판정하지 않는다.**
오른쪽 칸으로 보내려면 "왜 판정할 수 없는지" 를 함께 적는다 — 이유 없이 옮기면 검사를 끄는 것과 같다.

| 검증기 | 판정한다 (종료코드에 들어감) | 판정하지 않고 출력만 — 그 이유 |
|---|---|---|
| `verify_0828.py` | 32항목 전건 — 32번은 `rd()` 가 빈 문자열로 삼킨 파일 0건 | — |
| `verify_app.js` | 99건 — `R` 안 `pass` 전수(메뉴·사이드바 구성·상태·값 변화·레이아웃·다운로드·모달·서명 딥링크) + 콘솔 에러 + 죽은 컨트롤 | `a11y` — 원본 어드민의 표 행 `tabIndex` 가 0건이라 「몇 건이어야 하는가」의 근거가 없다. `newtab` — 실물 도달은 `verify_links.py` 가 본다. `scanned`·`menuCount` 는 곳수 보고 |
| `verify_proto.js` | 135건 — `R` 안 `pass` 전수 + 바깥 통로 5종(형제 문서·금칙 문자열·외부 호스트·화면 문구·스캔 0건) + 모달 곳수 가드 + 콘솔 + 죽은 컨트롤 | `a11y`·`newtab` 위와 같음. `escape.dockOptions` — 도크가 지금 없다(「도크 없음」). `escape.asset`·`hash`·`total` 은 곳수 보고(0건만 판정) |
| `verify_sync_chain.js` | 라운드의 `checks` 전건. 사이드바는 곳수가 아니라 **메뉴마다** 판정 — 다른 화면에 세운 뒤 눌러 `body.dataset.active` 가 그 메뉴가 되는지. 외부 링크(`target=_blank`)만 제외 | `http` 응답 바이트·`age`·`cache` — 배포 캐시 상태라 기준값을 댈 수 없다 |
| `verify_rows.js` | 37건(행 호버·초점·순번 열·건수·잔존·계약기록 잠금 행) + 콘솔 | — |
| `verify_toast.js` | 25건(실물 바이트 대조 + 프리셋 밖 잠금 + `완료` 토스트 전건이 파일명을 대는가 = D-39) + 콘솔 | — |
| `verify_links.py` | 링크 전건 200·바이트 + 검사 대상 0건 아님 | `assets/docs`·`assets/xlsx` 참조 곳수 — 몇 건이어야 하는지 근거 없음 |
| `verify_crossscreen.py` | 48건 전건 `chk()` | — |
| `verify_identity.js` | 항등식 17건 + 콘솔 에러 (① 잔액=유량x만기 되살림 · 일별 행은 `tyByDate` 와 바이트 대조 · 비중 최대잉여법) | — |
| `verify_period.js` | 40건 + 뷰포트 1440×`VIEW_H` + 콘솔 에러 | — |
| `verify_password.js` | `checks` 75건(정적 대조·지어낸 문구 포함) | `steps`·`expected` — 재현 기록 |
| `verify_sim.js` | 59건(뷰포트 1440×1200 포함) | — |
| `verify_glossary.js` | 앵커·가로 넘침·본문 링크 대상·층위 칩 곳수·기호 검색 0건·목차·콘솔 | 검색에 걸리는 카드 수 — 내용이 늘면 같이 는다 |
| `verify_glossary5.js` | 카드 50·5필드·이미지·앵커·마커(크롭 밖·크기 0)·라이트박스(열림·재열림·이미지·마커 좌표·ESC)·검색·가로 넘침·구버전 잔존·콘솔 | `lightbox.backdropCloses` — 배경 클릭 닫힘은 화면이 약속한 적 없는 동작이라 기준을 댈 수 없다(닫기 버튼 라벨은 「닫기 (Esc)」 뿐) |
| `verify_shotmarks.py` | 마커 곳수·4자 일치·촬영-측정 동기·잉크·앵커 역산 | 잉크 최소·최대 비율 — 판정은 `INK_MIN` 만 |
| `verify_feasibility.js` | 곳수·등급·가로 넘침·표·필터·검색·문항·SVG·복사 버튼 라벨 곳수·클립보드 실물(첫·끝 문항) + 콘솔 | 클립보드 글자 수·줄 수 — 문항 본문이 바뀌면 같이 바뀐다 |
| `verify_deployed.py` | 화면 문구 표식·쿠콘 구버전 잔재 | `commentNotes`·`rawBan` — D-22 가 지운 것은 **화면 고지**다. 주석은 화면에 안 뜨므로 FAIL 로 세지 않고, 0 이 아니면 찍어 둔다(화면 고지를 주석으로 옮겨 검사를 피하는 것을 눈에 보이게) |
| `gate_prototype.js` · `gate_glossary.js` | `check()` 전건 | 링크·자산 참조 총 곳수 |
| `sync_counts.py --check` · `sync_assets_static.py --check` · `build_readme.py --check` | 실측 ↔ 문서 전건 | — |

### 로스터 9건 재생성으로 기준을 옮긴 자리 (2026-08-30)

| 검증기 | 옛 기준 | 새 기준 | 사유 |
|---|---|---|---|
| `verify_identity.js` | 일별 행 수익 = 투자실행금에서 되짚은 수수료(±1.5원) | `tyByDate` 의 투자실행금·투자수익·상환액과 바이트 대조 + 수익 ≤ 되짚은 수수료 | 대표 정의서 [2번 이미지] `MD-1i` 의 부족액 차감이 들어가 되짚기가 성립하지 않는다 |
| `verify_identity.js` | 항등식 ① 삭제 | 되살림(허용 오차 2.0%) | W 모집단이 대상정산금채권 전체로 돌아가 성립한다 |
| `verify_proto.js` | `tyByW` — W 하나에 Ty 하나 | `tyByDate` — 날짜마다 W·Ty | 같은 사유. Ty 가 W 만의 함수가 아니다 |
| `verify_rows.js` | 계약기록 2쪽 순번 11–16 | 1쪽 전건 1:1 + 쪽 버튼 0개 | 9건이 기본 보기 10건 안에 들어가 2쪽이 없다 |
| `verify_rows.js`·`verify_toast.js` | 계약기록 10행 | `min(10, 로스터 곳수)` | 곳수를 검증기에 적지 않는다 |
| `verify_app.js`·`verify_proto.js` | 가맹점 검색어 `곱창` 결과 2건 | 원장 명단에서 센 `MC_HITS` | 왕십리곱창타운이 로스터에서 빠졌다 |
| `verify_app.js`·`verify_proto.js` | 상태 `invest-assets/page2` | 없음 | 낱장·상태 폐기 |
| `verify_crossscreen.py` | 1p+2p 로스터 합치기 · 엑셀 합계 행 20 | 1p 전건 · `4 + 로스터 곳수` 행 | 같은 사유 |
| `verify_identity.js` | 시트 본문 `slice(3, 19)` · 합계 `all[19]` | `slice(3, 3+NR)` · `all[3+NR]` | 같은 사유 |
| `verify_crossscreen.py` | 용어 출처 `조현준 슬랙 2026-08-28` | `정산주기.xlsx` | 만기 출처가 슬랙 축약값에서 365일 도수분포로 바뀌었다 |
| W 표기 | 소수 1자리 | 소수 2자리 | `40.15 ÷ 2.75 = 14.60` 이 화면 두 칸으로 되짚어진다 |

### QA 결함 교정으로 기준을 옮긴 자리 (2026-08-30)

엑셀이 프리셋 조합마다 갈리고(6조합 x 2 = 12벌), 프리셋 종료일이 기준일에서 끊기고,
계약기록의 전자서명 결과가 서명 대기 큐에서 갈리면서 옛 기대값이 무효가 됐다.

| 검증기 | 옛 기준 | 새 기준 | 사유 |
|---|---|---|---|
| `verify_app.js`·`verify_proto.js`·`verify_toast.js` | 엑셀 8건 · 파일명을 손으로 적음 | 화면의 `PRESET_RANGE` 를 읽어 6조합 x 2벌을 돌고, 파일명이 그 프리셋의 `_시작일_종료일.xlsx` 를 달았는지까지 판정 | 프리셋이 늘면 검증기가 저절로 따라온다. 기간을 적어 두면 다시 낡는다 |
| `verify_app.js`·`verify_proto.js` | (없음) | 직접입력 기간에서 두 버튼 `disabled` · `cursor:not-allowed` · 토스트 0 · 떨어진 파일 0 | 실물 없는 기간에 `완료` 토스트가 뜨면 그것이 곧 거짓말이다(D-39) |
| `verify_period.js` | 주별 전환 08-17~08-30 · 주 라벨 월~일 고정 · 4주 08-03~08-30 · 6개월 …08-31 | 주별 전환 = 4주 프리셋 08-03~08-27 · 기준일에서 끊긴 주는 라벨도 그 날짜까지 · 프리셋 종료일 전부 기준일 | 프리셋이 원장보다 앞서 나가지 않는다. 마지막 버킷이 빈 날짜를 이고 있으면 급락으로 읽힌다 |
| `verify_period.js` | 단위 전환 = 기간 유지(프리셋 포함) | 프리셋을 보고 있으면 새 단위의 같은 자리 프리셋으로, 직접 고른 기간은 그대로 유지 | 탭을 눌렀다고 직접입력으로 떨어지지 않는다. 두 축 원칙은 직접입력 기간에서 따로 본다 |
| `verify_period.js` | (없음) | 직접입력에서 미리보기 파일바 회색(`is-off`) · 이름 `-` · 내려받기가 `BUTTON[disabled]` · `a[download]` 0 | 파일바와 시트가 다른 기간을 말하던 자리 |
| `verify_identity.js` | 카드↔표 대조 구간에 프리셋(일주일·금월) 사용 | 네 구간 전부 직접입력(하루·8일·26일·5개월) | 프리셋에서 단위를 바꾸면 기간이 통째로 갈려 「같은 기간」 전제가 깨진다 |
| `verify_identity.js` | (없음) | 비중 최대잉여법 — 합 100.0 · 각 행 잔차 < 0.1pp | 잔차를 최대 금액 행에 몰면 그 행만 눈금 4개(0.2pp) 밀린다 |
| `verify_app.js` | (없음) | 딥링크 `#acquisition-list/signing` — 닫는 버튼 0 · 1.5초 뒤 `done` | 씨앗이 상태만 놓고 타이머를 안 걸면 그 주소로 들어온 사람은 갇힌다 |
| `verify_rows.js`·`verify_toast.js`·`verify_app.js`·`verify_proto.js` | 계약기록 클릭 가능 행 = 로스터 곳수 | `ctSignedCount(CONTRACTS)` — 화면이 세는 수 + 잠긴 체크박스 곳수 합이 총 행 | 서명 대기 큐에 남은 가맹점은 내려받을 문서가 없다 |
| `verify_crossscreen.py` | (없음) | 열머리 모집단 툴팁 — 낱장 4종은 마크업, 통합본은 `POP_W`·`POP_S` 재료. 건수는 `ledger_facts` | W·S·금액 세 칸의 모집단이 서로 다르다는 사실을 화면에서 되짚게 한다 |
| `gate_prototype.js` | 화면·상태만 돌며 엑셀 도달 경로 수집 | 화면·상태 + 프리셋 칩까지 돌고, `file` 없는 레지스터 키는 대상에서 뺌 | 상태만 돌면 12벌 중 절반이 「도달 경로 없음」으로 남는다 |
| `verify_toast.js`·`verify_proto.js`·`gate_prototype.js` | 화면 세우기와 클릭을 한 틱에 몰아 실행 | 한 번에 하나씩(120ms 간격) | 한 틱에 해시가 두 번 갱신되면 마지막 해시가 상태를 다시 심어, 방금 누른 프리셋이 아니라 그 상태의 씨앗 기간이 잡힌다 |

### 이 표가 없어서 새던 것 (2026-08-30)

| 자리 | 무엇이 샜나 |
|---|---|
| `verify_glossary.js` | 6종을 재고 `process.exit(0)` 무조건. 어느 값도 판정 안 함 |
| `verify_glossary5.js` | `process.exit(0)` 무조건. 자기 출력에 `legacyVerdict:'FAIL'` 을 찍으면서 종료코드에 안 넣음. 마커·라이트박스·가로 넘침은 게이트도 안 봄 |
| `verify_identity.js` · `verify_period.js` | 콘솔 에러를 걷어 찍고 종료코드에서 뺌 |
| `verify_period.js` · `verify_sim.js` | macOS 87px 보정 뒤 뷰포트를 재 놓고 판정 안 함 |
| `verify_toast.js` | `완료` 토스트 문구를 전수 수집해 찍기만 함 |
| `verify_proto.js` | 바깥 통로를 전 화면·상태에서 훑어 곳수만 찍음 |
| `verify_app.js` · `verify_proto.js` | 사이드바 메뉴 곳수를 재고 판정 안 함 (메뉴가 통째로 사라져도 통과) |
| `verify_feasibility.js` | 클립보드를 실제로 읽어 놓고 판정 안 함 |
| `verify_app.js` | `localStorage` 접근 예외를 `0` 으로 삼켜 `storageUsed===0` 이 통과 |
| `verify_proto.js` | 쿠콘 메뉴 검사가 `if(kc)` 로 감싸여 메뉴가 없으면 건너뜀 |
| `verify_0828.py` | `rd()` 가 없는 파일을 `''` 로 돌려줘 「금칙어 0건」류가 저절로 통과 |
| `verify_links.py` | 검사 대상이 0건이면 루프가 안 돌아 FAIL 0 으로 통과 |
| `verify_sync_chain.js` | 사이드바 `navMoved >= 메뉴수 - 1` — 곳수로 하나를 봐줘 진짜 죽은 메뉴가 숨음 |

## 종료코드

전 검증기가 FAIL 1건 이상이면 종료코드 1 로 끝난다. `verify_app.js` · `verify_proto.js` 는 R 안에서 `pass` 를 가진 항목을 전수로 훑어 세고, 콘솔 에러·죽은 컨트롤을 더한다 — 섹션 이름을 손으로 적지 않아 검사를 새로 넣어도 저절로 종료코드에 들어온다. `pass!==true` 는 전부 실패로 센다(try/catch 가 낸 `pass:null` 도 실패다).

## 폐지

| 검증기 | 폐지일 | 사유 |
|---|---|---|
| `rate_fix_verify.py` | 2026-08-30 | `rate_fix_map.json` 의 locator 74건이 대상 파일에서 전건 사라졌다(0건 매칭 뒤 예외로 종료). 할인율 정정 라운드(2026-08-29) 당시의 낱장 문자열이라 D-31 로 원장·낱장이 다시 찍히면서 무효가 됐다. 같은 재검산은 `verify_crossscreen.py`(정적 HTML·app.html·xlsx 3중 대조)와 `verify_identity.js`(항등식)가 덮는다 — 검사 공백 없음 |
| `verify_demo.js` (+ `verify_demo_result.json`) | 2026-08-28 | 대상 파일 `payhug-investor-admin/demo/index.html` 이 없다. 시연본이 `payhug-investor-prototype` 저장소로 분리되면서 `demo/` 자체가 사라져 실행 자체가 불가. 역할은 `verify_proto.js`(시연본 전건)와 `verify_sync_chain.js`(원본 ↔ 시연본 변환 손실)가 이미 대신한다 — 검사 공백 없음 |
