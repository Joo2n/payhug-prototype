# 투자자 어드민 배포본 QA — 2026-09-07

대상: 전체본 `https://payhug-investor-demo.vercel.app/` (`Joo2n/payhug-investor-admin` main `9972f0b`) · 시연본 `https://payhug-investor-prototype.vercel.app/` (`Joo2n/payhug-investor-prototype` main `4535135`)
방법: 헤드리스 크롬 + CDP 실제 마우스·키보드 이벤트 (뷰포트 1440×1000, `Emulation.setDeviceMetricsOverride`). 파일 수정 0건.
스크립트·결과: `scratchpad/demo_qa.js` `proto_qa.js` `style_qa.js` `pw_qa.js` `date_qa.js` `date2_qa.js` `date3_qa.js` `parse_dl.py` `compare_ledger.py` → `step11_*_result.json` · 캡처 175장 `scratchpad/step11_qa_live/` · 내려받은 실물 `scratchpad/step11_dl/{demo,proto}/`
「우리」 줄번호는 배포본 원문 기준(`step11_src/demo_app.html` = 전체본 app.html, `step11_src/proto_index.html` = 시연본 index.html). 로컬 `/Users/semi/cursor/payhug-investor-admin/app.html` 은 전체본과 줄이 같습니다.

## 결론

1. 판정 항목 1·2·4·5·7 은 전부 통과입니다. 금칙어 10종·「수익 산정 기준」 4종·「기준일」「보유채권」「연환산수익률」「투자자산 대비」 는 DOM 텍스트·속성·툴팁·엑셀 4종·PDF 본문 어디에도 0건, 콘솔 오류 0, 가로 스크롤 0, 카드·표·합계·월별·주별 값은 `ledger_facts.json` 과 전건 일치(값 대조 77건 통과)입니다.
2. 항목 3 툴팁 12곳(투자 자산 8 · 투자 수익 4)은 실제 호버로 전부 떴고 잘림·겹침·뷰포트 밖 0건입니다. 다만 일별 표 열머리 「투자실행금」 툴팁 본문이 「⑥ 의 ③ / 번호 / 상단 현황의 기간 전체 숫자 · **칸 미지목**」 이라 대표 회의 미결 사항이 투자자 화면에 그대로 노출됩니다(두 배포본 공통). 이것이 최상위 결함입니다.
3. 항목 6 시연본은 사이드바 7메뉴·화면 9·상태 17 이 전부 실제 클릭으로 도달했고, 「투자 시뮬레이션」 메뉴 0, 갤러리·엑셀 미리보기·시뮬레이션 해시 8종은 모두 투자 자산으로 되돌아가며, 로그인 화면은 `app/login/page.tsx` 와 문구·색·비활성 규칙·Enter 제출까지 같습니다.
4. 실제 프론트와 어긋나는 것 중 고칠 것은 날짜 칸 키보드 입력(대조군은 `2025-01-07` 이 되는데 우리 화면은 빈 값이 되고 원장 180일 전체가 조회됨), 증명서 제목 3종 불일치와 PDF 에만 있는 「견본」 띠, h1 옆 상태 배지(실제 프론트 0건)입니다.
5. 다운로드는 엑셀 4종·PDF 1종이 실제 파일로 도착했고(CDP `Browser.downloadProgress` completed 6건), 엑셀 머리행 서식은 `lib/excel.ts` 와 같으나 제목행·빈 행·틀고정이 더 붙어 있습니다.

## 결함 (심각도 순)

| # | 화면 | 요소 | 실제 프론트 / 원장 | 우리 | 판정 | 근거 (파일:줄) |
|---|---|---|---|---|---|---|
| 1 | 투자 수익 (전체본·시연본·낱장 4종) | 일별 표 열머리 「투자실행금」 툴팁 | 대표 정의서 번호 ③ 은 「상단 현황의 기간 전체 숫자」까지만 좁혀졌고 칸 미지목 — 회의 기록(2026-08-31 00:59:21)이 소스 주석에 있음 | 툴팁 본문 `⑥ 의 ③` + 행 「번호 · 상단 현황의 기간 전체 숫자 · 칸 미지목」 이 투자자에게 보임. 옆 열머리 「연환산 수익률」 툴팁도 `(④ ÷ ③) × 365 ÷ ⑤` 와 「번호 · 일별 표 열 ③투자실행금 ④투자 수익 ⑤가중평균 금융일수」 로 대표 정의서 번호 체계를 그대로 노출 | **내부 표시 노출** (금칙어 목록엔 없으나 「확인 대기」와 같은 부류) | 우리 `demo_app.html:1780-1784` `proto_index.html:1563-1567` `invest-profit.html:199,202` `invest-profit--weekly.html:205` `--monthly.html:205` `--empty.html:205` · 캡처 `demo_app_invest-profit_tip3_투자실행금.png` `proto_invest-profit_tip3_투자실행금.png` · 대응표 `_pipeline/investor_admin/marker_legend.md` |
| 2 | 투자 수익 (시연본·전체본) | 시작일·종료일 날짜 칸 키보드 입력 | 맨 `<input type=date>` 에 `2025`→→`01`→`07` 을 치면 `2025-01-07` (대조군 실측). 원본 `DateRangeFilter.tsx:116,122` 는 React 제어 입력이며 조회는 「조회」 버튼에서만 실행 | 같은 키 순서를 치면 시작일 값이 `""` 이 되고 그 즉시 원장 180일 전체가 표에 실림(「직접입력 ~ 2026-08-27」, 토스트 「조회 결과 180건 · ~ 2026-08-27」). 원인은 세그먼트를 칠 때마다 오는 `change` 가 `refresh()` 를 부르고 `fi.value = PF.from` 으로 값을 되써서 편집 중인 세그먼트가 초기화되는 구조. 빈 시작일을 하한 없음으로 다루는 것도 함께 | **불일치** | 우리 `proto_index.html:2897-2908`(change→refresh) `:2151-2152`(값 되쓰기) · 전체본 `demo_app.html:3720` `:2376-2377` · 실측 `step11_date3_result.json` control=`2025-01-07`, protoEsc=`{"v":"","pf":"","rows":180}`, protoFocusOnly 동일 · 캡처 `proto_37e_from-typed-esc.png` |
| 3 | 투자 수익 (시연본·전체본) | 날짜 칸 숫자 부분 클릭 | 원본은 `showPicker()` 0건 — 숫자 부분을 누르면 세그먼트에 캐럿이 가서 바로 타이핑 | 어디를 눌러도 달력이 뜨고, 달력이 떠 있는 동안 키 입력은 달력이 먹음(→ 키 `→` 가 날짜를 08-21→08-22 로 옮김). 소스가 「이 산출물만 다르다」고 적어 둔 의도된 차이지만 #2 와 겹쳐 키보드 입력 경로가 둘 다 막힘 | **불일치 (의도된 차이, 재검토)** | 우리 `proto_index.html:2689-2696` · 실측 protoNoEsc=`{"v":"2026-08-22"}` |
| 4 | 증명서 (전체본·시연본) + PDF | 문서 제목·「견본」 띠 | — (실제 프론트에 없는 신규 화면) | 한 문서에 제목이 셋: 화면 h1 「가맹점별 투자자산 증명서」, 화면 문서 제목 「투자자산 현황」, PDF 제목·메타 「투자자산 증명서 (견본)」. PDF 에만 머리띠 「견본 · 제안서 시연용 — 계약 효력 없음 · 실제 서명·인증 미포함」 4곳, 워터마크 「견본」, 2쪽 「서명 검증 — 인증서 발행기관 검증 회신전문 미첨부」, 서명값 아래 「견본 — 실제 서명값이 아니다.」 가 있고 화면에는 이 문구가 0건 | **불일치(자체) · 확인 필요** (시연본에서 투자자에게 「견본」 PDF 를 내려주는 것이 의도인지) | 우리 `certificate.html:6,155,164` · PDF `step11_dl/demo/투자자산증명서_20260827.pdf` 본문(`step11_dl_parsed.json`) · 생성기 `_pipeline/investor_admin/build_docs.py:108,169-171` · 캡처 `demo_app_certificate_full.png` `proto_25_certificate.png` |
| 5 | 시연본 전 화면 | h1 옆 상태 배지 (「엑셀 다운로드 완료」「증명서 발급 확인」「주별」「월별」「검색 적용」「결과 없음」「계약서보기」「서명 확인」「서명 진행」「서명 완료」「전체 선택」「문서 없음」「규칙 미충족」「확인값 불일치」「변경 완료」) | `AdminLayout.tsx`·각 page 의 h1 옆에 상태 배지 0건 | 상태 전이마다 h1 안에 `.badge.state-badge` 를 넣음. 시연본에서도 그대로 노출되며 「규칙 미충족」은 `.badge-amber`(항목 1 의 배지 0 규칙에 걸림) | **임의생성** (스토리보드 상태 표식 장치가 시연본에 남음) | 우리 `proto_index.html:1423-1461`(STATE_META) `:1830`(h1 주입) · 실측 `step11_proto_result.json` steps[*].stateMark · 캡처 `proto_71_password_weak.png` `proto_22_invest-assets_download.png` |
| 6 | 엑셀 4종 | 워크북 형식 | `lib/excel.ts:23-29` — 1행이 머리행(채움 `FF6366F1`·흰 굵은 글씨 11·가운데), 제목행 없음, 틀고정 없음. `app/sales/[bizNo]/page.tsx:274-285` 도 같음 | 1행 제목(`투자자산 현황 — 2026-08-27 / ㈜테스트인베스트`, 병합·13pt 굵게), 2행 빈 행, 3행 머리행(서식은 원본과 동일), 틀고정 `A4`. 백분율은 `0.00%` 셀 서식(원본은 숫자 `#,##0` 만) | **불일치 (개선 후보 — 근거 없음)** | 우리 `_pipeline/investor_admin/build_xlsx.py:47,84,89,167` · 실측 `step11_dl_parsed.json` |
| 7 | 전 화면 | 토스트 | `Toast.tsx:42-51` — 아이콘 없이 문구 + (duration 0 일 때만) X 버튼 | 문구 앞에 체크 원 아이콘(svg) 고정 삽입. 위치·색·패딩·3초 소멸은 원본과 동일(상단 24px·중앙·`green-100/500/800`·`primary-100/500/800`) | **불일치 (아이콘 임의 추가)** | 우리 `proto_index.html:1862-1864` `demo_app.html:2087` · 실측 `step11_style_result.json` toastInner |
| 8 | 투자 수익 | 날짜 input `min`/`max` | `DateRangeFilter.tsx:116` 시작일 `max={dateTo}` · `:122` 종료일 `min={dateFrom}` — 달력에서 역전 범위를 고를 수 없음 | 두 속성 없음(`null`). 역전 시 검색 버튼 비활성 + 붉은 인라인 문구로 막음(원본은 `alert`) | **불일치 (부분 개선)** | 우리 `proto_index.html:556,561` · 실측 dateInputs min/max null · 캡처 `proto_36_invest-profit_bad-range.png` |
| 9 | 투자 수익 표 ↔ 투자 자산 표 | 「가중평균 금융일수」 열 값 표기 | 원장 `w` 는 일수 | 투자 자산 두 표는 `3.04일`·`3.02일`(단위 있음), 투자 수익 일별·주별·월별 표는 `3.06`·`2.93`(단위 없음), 합계 행 `3.11 가중평균` | **불일치(자체)** | 우리 `demo_app.html:2205`(자산 표 `+'일'`) · 실측 `compare_ledger.py` 15건이 단위 차이로만 어긋남 |
| 10 | 투자 자산 카드 툴팁 | 「예상 연환산 수익률」 카드 패널 마지막 행 | 다른 4개 툴팁은 「연환산」 | 이 패널만 「연 환산 13.21%」(띄어쓰기) | **불일치(자체)** | 우리 `demo_app.html:2191` `proto_index.html:1966` `invest-assets.html:133` |
| 11 | 가맹점 · 가맹점별 투자자산 · 계약기록 | 「보기 10개/20개/50개」 셀렉트 | 어드민 목록은 페이지 크기 고정(`LockAccountDeposits.tsx:109 PAGE_SIZE = 20`), 셀렉트 0건. 스토리보드에도 없음(`storyboard_coverage.md:290` 은 행 수만 언급) | 세 표 머리에 셀렉트 노출 | **임의생성 · 확인 필요** | 우리 `proto_index.html:1696` `demo_app.html:1885` |
| 12 | 계약기록 (시연본·전체본) | 진입 직후 선택 상태 | — | 첫 진입에 「초록치킨 서초점·김밥나라·골목냉면」 3건이 이미 체크되어 「3건 선택」「선택 문서 다운로드 (3)」 로 시작 | **임의생성 (표본 시드)** | 우리 `proto_index.html:1657-1658`(`CT_SEL0`) · 실측 `step11_date2_result.json` ctBefore |
| 13 | 가맹점 | 행 클릭 | `app/manage/page.tsx:291` 행에 `cursor-pointer` + 상세 이동 | 행 클릭 무반응(호버 gray-50 만). 투자자용 상세 화면 정의가 없으면 정상 | **누락 · 확인 필요** | 실측 `proto_qa.js` 47단계 · `step11_style_result.json` mcRowClickable |
| 14 | 비밀번호 변경 | 변경 완료 후 | `merchant-web app/my-info/change-password/page.tsx:54,59` — 토스트 후 1.5초 뒤 로그아웃·로그인 이동 | 토스트 문구 동일, 세 칸 비움, 이동 없음(소스에 「옮기지 않았다」 명시) | **불일치 (의도된 차이)** | 우리 `proto_index.html:2818-2820` · 실측 pwDone/pwAfter(`step11_date3_result.json`) |
| 15 | 로그인 (시연본) | 제출 요소 | `page.tsx:159-161` `<button disabled>` | `<a class="login-submit" aria-disabled="true" href="#invest-assets">` — 색·커서·pointer-events 로 같은 동작 | **불일치 (마크업만)** | 우리 `proto_index.html:782` `:355` |
| 16 | 전체본 낱장 `invest-sim.html` | 「시뮬레이션 실행」「+ 채권 추가」「삭제」 | — | 핸들러 없는 정적 버튼(클릭 후 URL·본문 불변). `app.html#invest-sim` 은 추가 32→36행·삭제·실행→`#invest-sim/result` 전이 정상 | **낱장 죽은 버튼** | 우리 `demo_invest-sim.html:197,214` · 실측 `step11_style_result.json` sim, `step11_date3_result.json` sim* |
| 17 | 전체본 낱장 | favicon | 시연본은 `<link rel="icon" href="data:,">` | 전체본 낱장(`invest-assets.html`·`login.html`)에서 `/favicon.ico` 404 콘솔 로그 | **하** | 실측 `step11_demo_result.json` console |

### 상위 결함 고치는 법

- **#1** 「투자실행금」 열머리 툴팁은 다른 열머리처럼 정의만 남깁니다(예: `PA · 기간 투자실행금 · Σ Ai`). 「⑥ 의 ③」「번호」「칸 미지목」 행과 「연환산 수익률」 툴팁의 「번호 · 일별 표 열 ③④⑤」 행을 지우고 산식은 기호로 씁니다(`PMR × 365 ÷ PD` 꼴, 현황 ④ 툴팁과 같은 문법). 대표 정의서 번호 대응은 `marker_legend.md` 에만 둡니다. 낱장 4종·app.html·시연본 index.html 6곳 동일.
- **#2** `change` 에서 `refresh()` 를 부르지 않고 `PF.from/to` 만 갱신한 뒤 표는 「검색」에서만 다시 그립니다(원본 `DateRangeFilter` 와 같은 순서). `fi.value = PF.from` 되쓰기는 값이 다를 때만, 그리고 포커스가 그 칸에 없을 때만 합니다. 빈 시작일은 조회 불가(검색 비활성)로 둡니다.
- **#3** `showPicker()` 를 아이콘 클릭으로 한정하거나 제거합니다(원본 0건).
- **#4** 화면 문서 제목·h1·PDF 제목을 하나로 맞춥니다. 「견본」 띠·「실제 서명값이 아니다」는 시연본 PDF 에서 빼거나, 화면에도 같은 표시를 두어 둘이 같게 합니다.
- **#5** 시연본 빌드에서 `STATE_META` 라벨을 비우거나 `[data-state-mark]` 주입을 끕니다(`proto_index.html:1830`).

## DOM 만 보면 결함이나 실제로는 정상

| # | 화면 | DOM 관찰 | 실제 동작 · 근거 |
|---|---|---|---|
| 1 | 투자 자산·투자 수익 | `.badge-amber` 7개(「서명 대기」) 가 DOM 에 있음 | 숨겨진 `section[data-screen=acquisition-list]`·`contracts`·모달 안의 도메인 상태 배지. 대상 화면에서 가시 0건 (`step11_demo_result.json` pages[*].badgeAmber visible=false) |
| 2 | 투자 자산 | 다운로드 뒤 h1 텍스트가 「투자 자산 엑셀 다운로드 완료」 | h1 안에 상태 배지가 들어가는 구조(#5). 제목 문구 자체는 「투자 자산」 |
| 3 | 계약기록 | 「선택 문서 다운로드 (n)」·행별 「문서 다운로드」 6개가 항상 `disabled`, 핸들러 `function(){}` | 결정 D-39(전자서명 형식 확정 전까지 계약서 다운로드 차단) — `request_register.md:314`, `proto_index.html:2779,2782` |
| 4 | 정산채권 양수 | 행(`[data-act=aq-row]`)에 `role`·`tabindex` 없음, 행 포커스 후 Space 무반응 | 원본 어드민 레포 전체 `tabIndex` 0건·`role="checkbox"` 0건이라 행은 키보드 대상이 아님. 행 안 체크박스는 Space(`key:" "`)로 토글됨(실측 aqChkSpace `[true,false,false]`). 행 클릭·「전체 선택」「선택 해제」 정상 |
| 5 | 가맹점 | 열머리 8개 클릭해도 순서 불변, `aria-sort` 없음 | 원본 `app/manage/page.tsx` 도 정렬 없음(레포 `aria-sort`·`sortBy` 0건) |
| 6 | 가맹점 | 업종 셀렉트 옵션이 「전체·음식점업」 둘뿐 | 8곳 로스터가 전부 음식점업이라 옵션이 로스터에서 파생됨. change 이벤트로 필터 동작 확인(`proto_45_merchants_sector.png`) |
| 7 | 가맹점·계약기록·가맹점별 투자자산 | 페이지 버튼 0개, 「총 8건」만 | 8행 ≤ 페이지 크기 10. 원본도 `totalPages > 1` 일 때만 페이지네이션(`LockAccountDeposits.tsx:432`) |
| 8 | 투자 수익 | 역전 범위에서 `alert` 없음 | 원본은 버튼 자체를 `disabled`(`DateRangeFilter.tsx:128`)라 alert 경로가 눌리지 않음. 우리는 같은 비활성 + 인라인 문구 |
| 9 | 쿠콘 관리 현금 | 사이드바 클릭으로는 화면이 안 바뀜 | `target=_blank` 외부 링크(원본 없는 신규 메뉴). `#coocon` 해시로는 「We-bank 바로가기」 화면이 뜸 |
| 10 | 전체본 | 재실행 시 다운로드 목록이 `["downloads.html"]`·`[]` | 같은 이름 파일을 덮어써 새 파일 검출이 안 된 것. CDP `Browser.downloadProgress` completed 6건, mtime 갱신 확인 |
| 11 | 시연본 | 토스트 목록에 「㈜테스트인베스트 로그아웃」 | 판독 셀렉터 `.info` 가 사이드바 프로필을 잡은 것 |
| 12 | 투자 자산 | 「투자실행액」 카드 툴팁이 카드 값(80,000,000)을 덮음 | 원본 `HoverTooltip` 도 앵커 우측 정렬(`PreSettlementTab.tsx:1006`)이라 같은 자리. 겹침 판정(패널 위 elementFromPoint)은 0건 |
| 13 | 시연본 로그인 | `<form>` 없음 | 원본 `page.tsx` 도 `<form>` 없이 `onKeyDown` Enter 제출(`:89-92`) |
| 14 | 전체본 `index.html` 갤러리 | 「대표 확인 요청」「대표님 확인 문항」 링크 | 전체본 갤러리(내부용). 시연본에서 갤러리·용어 해설·엑셀 미리보기로 가는 링크 0건, 해당 파일 404 |

## 판정 항목별 실측

### 1. 내부 검토 표시 (DOM 텍스트·속성·툴팁 패널)

- 검사 낱말: 미확정·대표 확인 대기·대표 재전달·대표 DM·관찰된 값·항등식·부족액 0·일 환산·예시·확인 대기 → 전체본 22개 페이지 상태·시연본 72단계 전부 **0건**(script/style 제외 텍스트 노드 + `title/placeholder/aria-label/alt` + 툴팁 패널 내부).
- `.badge-amber` 가시: 투자 자산·투자 수익·증명서·엑셀 미리보기 **0**. 정산채권 양수·계약기록 「서명 대기」(도메인 상태), 비밀번호 변경 weak 상태 「규칙 미충족」(상태 배지, 결함 #5).
- 「칸 미지목」(결함 #1)은 검사 낱말 밖이지만 같은 부류.

### 2. 「수익 산정 기준」 구역

- 「수익 산정 기준」「수수료 배분형」「조달이자형」「연 12%」 **0건**.
- 투자 자산 세로 배치: page-header(32~64) → 카드(88~204) → 현황 표(228~470) → 가맹점별 표(494~1015), 블록 간격 전부 **24px**, `<hr>` 0, main padding-bottom 32px, 문서 높이 1071. 빈 자리·이중 구분선 없음(`demo_app_invest-assets_full.png`).

### 3. 툴팁 (실제 호버, 두 배포본 동일 텍스트)

모두 `display:none → block → none`, 패널 폭 256px, 뷰포트 안, 조상 클리핑 0, 덮임 0, 텍스트 잘림 0.

| 화면 | 앵커 | 패널 행 |
|---|---|---|
| 투자 자산 카드 | 투자실행액 | `Σ Ai · 투자 실행액 · Ai = 순지급액i × (1 − r) 의 합` / `r 계약된 할인율 · 0.11%` |
| 투자 자산 카드 | 예상 연환산 수익률 | `Yr · 예상 연환산 수익률 · r × 365 ÷ D` / `연환산 일부 기간의 수익률이 1년간 계속된다는 가정하에 예상되는 연간 수익률` / `r 계약된 할인율 · 0.11%` / `D 가중평균 금융일수 · 3.04일` / `연 환산 13.21%` |
| 현황표·가맹점별 열머리 | 가중평균 금융일수 | `보유 채권 전체 (회수된 것 포함)` / `채권 건수 61,760건` |
| 현황표·가맹점별 열머리 | 입금부족률 | `선정산일이 오늘 기준 20일 전 ~ 11일 전인 표본` / `채권 건수 3,200건` |
| 현황표·가맹점별 열머리 | 예상 연환산 수익률 | `YR · 예상 연환산 수익률 · R × 365 ÷ D` / `연환산 …` |
| 투자 수익 ④ | 투자실행금액 대비 | `PYa · 투자실행금액 대비 연환산 수익률 · PMR × 365 ÷ PD` / `연환산 …` / `PMR 기간 투자수익율 · PM ÷ PA = 0.033992%` / `PM 기간 투자수익 · 61,175원` / `PA 기간 투자실행금 · 179,970,919원` / `PD 기간 가중평균 금융일수 · 3.11일` |
| 투자 수익 ⑤ | 투자 자산 대비 | `PYt · 투자 자산 대비 연환산 수익률 · PM × 365 ÷ ( Σ( Ai × Di ) + PEC )` / `연환산 …` / `PYa 투자실행금액 대비 연환산 수익률 · 3.99%` / `Σ( Ai × Di ) 559,275,516원` / `PEC 기간 순현금 · 140,000,000원` / `EC 순현금 · 20,000,000원 × 7일` |
| 일별 표 열머리 | 투자실행금 | `⑥ 의 ③` / `번호 상단 현황의 기간 전체 숫자 · 칸 미지목` ← 결함 #1 |
| 일별 표 열머리 | 연환산 수익률 | `(④ ÷ ③) × 365 ÷ ⑤` / `번호 일별 표 열 ③투자실행금 ④투자 수익 ⑤가중평균 금융일수` / `행 정산예정일이 그 날짜인 보유 채권` ← 결함 #1 |

주별·월별 전환 뒤 ④⑤ 툴팁 값도 화면 값과 같음(주별 4주: PMR 0.038323%·PM 248,681·PA 648,903,503·PD 3.03·Σ 1,965,572,846·PEC 500,000,000·EC ×25일 / 월별 3개월: 0.038118%·875,417·2,296,624,838·3.03·6,964,794,977·1,760,000,000·×88일). 캡처 `demo_app_invest-*_tip*.png` `proto_invest-*_tip*.png` 36장.

### 4. 값 (원장 `ledger_facts.json` 대조)

| 항목 | 화면 | 원장 | 판정 |
|---|---|---|---|
| 카드 | 100,000,000 / 80,000,000 / 20,000,000 / 13.21% · 3.04일 | total/exec/cash/ty/w | 일치 |
| 현황표 투자실행액 행 | 80,000,000 · 3.04일 · 0.07% · 13.21% · 80.0% · ㈜페이허그 | exec·w·s·ty | 일치 |
| 가맹점별 8행 | 이름·금액·W·S·Ty | merchants[0..7] | 8행 전부 일치 |
| 투자 수익 기본 | 일주일 2026-08-21 ~ 08-27 · ④ 3.99% · ⑤ 3.19% | weekFrom/To·weekTy·weekTyAsset | 일치 |
| 일별 7행 | 상환액·투자실행금·투자수익·W·Ty | tyByDate | 35셀 일치 |
| 합계 | 180,032,111 / 179,970,919 / 61,175 / 3.11 / 3.99% | weekRepay/weekExec/weekProfit/weekW/weekTy | 일치 |
| 월별 3개월 3행 | 2026-06·07·08 투자실행금·W·Ty·투자수익·상환액 | monthExec·monthTy·tyByDate 합 | 15셀 일치 |
| 월별 6개월 합계 | 4,700,503,303 / 1,787,417 / 3.03 / 4.57% · ⑤ 3.65% | fullExec/fullProfit/fullW/fullTy/fullTyAsset | 일치 |
| 주별 4주 4행 | 월~일 버킷 합·W=r6(ΣAD/Σexec)·Ty=r6(r6(pf/ex·100)·365/W) | tyByDate·adByDate 롤업 | 20셀 일치 |
| 프리셋 6종 | 일주일 7행·금월 27행·4주 4행·12주 12행·3개월 3행·6개월 6행, 활성 표시 `aria-pressed` | period_design.md 표 | 일치 |

「기준일」「보유채권」「연환산수익률」「투자자산 대비」 0건. 검사 92건 중 15건은 판독기가 「일」 단위를 기대한 차이(결함 #9)이고 값은 같습니다(`step11_ledger_compare.json`).

### 5. 다운로드 (실제 클릭 → 파일 도착)

| 버튼 | 파일 | 크기 | 내용 검사 |
|---|---|---|---|
| 투자 자산 › 현황 엑셀 다운로드 | 투자자산현황_2026-08-27_2026-08-27.xlsx | 5,727 B | 시트 「투자자산 현황」 6행, 금칙어 0 |
| 투자 자산 › 가맹점별 엑셀 다운로드 | 가맹점별투자자산_2026-08-27_2026-08-27.xlsx | 6,109 B | 12행(8곳+합계), 금칙어 0, 상태 `download` 전이·토스트 |
| 투자 수익 › 현황 엑셀 다운로드 | 투자수익현황_2026-08-21_2026-08-27.xlsx | 5,466 B | 항목/값 5행(④ 0.0399 ⑤ 0.0319), 금칙어 0 |
| 투자 수익 › 일별 엑셀 다운로드 | 일별투자수익_2026-08-21_2026-08-27.xlsx | 5,873 B | 7행+합계, 금칙어 0 |
| 증명서 › PDF 다운로드 | 투자자산증명서_20260827.pdf | 245,291 B | A4 2쪽, 본문 금칙어 0, 「견본」 띠(결함 #4) |

버튼 350ms 「다운로드 중…」 스피너 후 「<파일명> 내려받기 완료」 토스트, 3초 소멸. 시연본도 같은 3파일 도착.

### 6. 시연본

- 사이드바: 투자(투자 자산·투자 수익) / 가맹점(가맹점·정산채권 양수·계약기록) / 관리(쿠콘 관리 현금 ↗·비밀번호 변경) = 7. 「투자 시뮬레이션」 **0**. 그룹 머리 접힘 동작, 활성 메뉴 `rgb(127,225,65)`, 폭 240·배경 `#1B2537` 는 `AdminLayout.tsx:435-439,520-528` 과 일치.
- 화면 9 도달: login(`#login`·로그아웃 클릭) · invest-assets · certificate(모달 → 발급) · invest-profit · merchants · acquisition-list · contracts · coocon(`#coocon`) · password.
- 상태 17 도달: invest-assets download/cert-confirm/empty · invest-profit weekly/monthly/empty · merchants filtered/empty · acquisition-list doc/confirm/signing/done · contracts all/empty · password weak/error/done — 전부 실제 클릭·타이핑(빈 상태 3종은 해시 진입, `merchants/empty` 는 검색어로도 도달).
- 진입 차단: `#xls-assets-status` `#xls-profit-status` `#invest-sim` `#invest-sim/result` `#glossary` `#index` `#invest-sim.html` `#xls-assets-status.html` → 모두 `invest-assets/default`. `login.html` `app.html` `xls-*.html` `invest-sim.html` `glossary.html` 은 404.
- 로그인 대조(`app/login/page.tsx`): 배경 `primary-700→600→500` 대각선 그라데이션(:96) · 카드 448px·둥글기 24·흰색 95%(:106) · 「PayHug Admin」 30px 굵게 + 「관리자 로그인」(:109-112) · 라벨 「아이디」「비밀번호」, placeholder 「휴대전화번호 또는 사업자번호」「비밀번호」, 아이콘(:118-155) · 비활성 버튼 `gray-300` `not-allowed`(:161-166), 두 칸 채우면 활성, Enter 제출(:27,:89-92) · 안내 「안내: 이 페이지는 관리자 전용입니다.」 amber(:180-188) · 「© 2026 PayHug. All rights reserved.」(:194) — 전부 일치. 차이는 결함 #15 마크업뿐.
- 그 밖에 실제 프론트와 대조해 일치한 것: 열머리(`text-xs font-semibold text-gray-500 uppercase`, `PreSettlementTab.tsx:669`), 엑셀 버튼 `emerald-600`(`ExcelDownloadButton.tsx:15`), 프리셋 활성 `bg-primary text-white` + `aria-pressed`(`DateRangeFilter.tsx:96-107`), 역전 범위 검색 비활성(`:128`), 검색·초기화 문구, 툴팁 패널(`bg-gray-900 text-[11px] rounded-lg p-2.5 w-64`, `PreSettlementTab.tsx:1035`), 비밀번호 규칙·문구 9종(`merchant-web lib/passwordPolicy.ts:11-20`)과 placeholder 3종(`change-password/page.tsx:111,118,130`), 성공 토스트 문구(`:54`).

### 7. 콘솔·가로 스크롤

- 콘솔: 시연본 72단계 0건, 전체본 0건(단 낱장 `invest-assets.html`·`login.html` 의 favicon 404 로그 1건씩, 결함 #17).
- 가로 스크롤: 전 페이지 `scrollWidth ≤ clientWidth`, 뷰포트 밖 요소 0.

## 캡처 색인 (`scratchpad/step11_qa_live/`, 175장)

- 전체본: `demo_app_invest-assets_full.png` `…_tip1~8` `…_download-state` `…_cert-confirm` `demo_app_certificate_full.png` `demo_app_invest-profit_full.png` `…_weekly_full` `…_monthly_full` `…_tip1~4`(기본·주별·월별) `demo_app_invest-sim_result_full.png` `demo_single_*_full.png`(낱장 13종) `demo_single_invest-*_tip*.png`
- 시연본: `proto_00_entry` `proto_01_login` `proto_01_login_filled` `proto_10_menu_*`(6) `proto_11_coocon_hash` `proto_20~28`(투자 자산·증명서) `proto_30~39`(투자 수익) `proto_31_invest-profit_<단위>_<프리셋>`(6) `proto_40~47`(가맹점) `proto_50~58`(정산채권 양수) `proto_60~65`(계약기록) `proto_70~74`(비밀번호) `proto_74b_password_done` `proto_95_logout` `proto_96_logo-click` `proto_invest-*_tip*.png` `proto_36b/37b~e`(날짜 입력) `proto_61b_contracts_two-selected`
- 스타일 대조: `demo_style_*.png` `proto_style_*.png`
