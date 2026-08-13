# PayHug 화면설계·기능명세·IA 진행 상태

> **이어쓰기 문서.** 다음 세션은 이 파일만 보면 이어서 진행 가능. (worktree = `~/cursor/payhug` 전용)
> 최종 업데이트: **2026-08-13**

## 2026-08-13 세션 — 변경이력체 정화 + 정책서 3차 재제작(위계·표·계산식)

배경: 사용자 반려 2건 — ① 정산 3장(2705~2707) 키노트가 "무엇을 고쳤는지"(변경이력체)로 작성됨 ② 정책서(IFX 3783:906)가 위계 없는 통짜 불릿 + 화면 나열 수준. 산출물·데이터 = `_pipeline/enhance_202608/round2/`.

1. **원인**: 지난 현행화 교정 129건 중 52건이 이력체·영문 식별자·적용 지시문 노출("(기존 문장 유지 후 추가)"까지 시트에 박힘). 정산 3장은 신구 대조 문서(settle.md)를 원고로 써서 오염. → 교훈 메모리 `feedback_no_changelog_descriptions` 저장.
2. **화면설계서(서준 파일) 정화**: 정산 3장 전면 재작성(원고 `round2/settle3_rewrite.md`, 골드 스탠더드 = newsheets/admin_content.md 스타일) + 구판 20시트 오염 51건 교체(`fix_oldsheets.json`, 노드ID 재구성으로 무효→텍스트 매치 재특정) + 신규 8장·스왑 2장 보수 25건(이력체 15·Note 8·Date 2·모달 키노트 2) + '우리가게클릭비' 잔존 라벨 4노드 → '플랫폼 차감'. QA: 전 항목 PASS(원고 문자 단위 일치·이력체 0·표본 23건 반영 확인). 감사 전문 = `round2/audit_settle3.md`·`audit_new10.md`, 로그 = `apply_report_sheets.md`·`qa_sheets.md`.
3. **정책서 3차 재제작(IFX 3783:906)**: 재조판 규격 `round2/format_recipe4.md`(예시 EUK 5:17·회수 A4 해부 → 절 표준 흐름 [기능 개요→정책→계산식+예시→케이스→화면 기준→미확정], 타이포·들여쓰기 4단·네이티브 표·케이스 박스·EQ/EX 의무·원고 DSL). 원고 3부(`dsl_A/B/C.md`, 검산 EX 22개) → 신판 A4 **28장**(3998:2~4008:79) 조판 → QA 28장 PASS(DSL 누출 0·산식 21개 검산 일치) → 구판 13장 삭제·신판 그리드 재배치·탭 캡처 6장 재연결(꺾쇠 18건 갱신, 3940:17·31 보류)·섹션 4500×8500 트림. 슬라이드 2·Flow 2 유지. 로그 = `build_report4.md`·`qa_policy.md`·`final_apply.md`.
4. **운영 원칙 재확인**: 시트·정책서 본문은 현재 상태 서술만(이력은 커밋·파이프라인 md), diff 문서 원고화 시 재서술 필수, 적용 전 이력체 스캔 필수.

## 2026-08-12 세션 — 화면설계서 전수 현행화 + 누락 보강 + 정책 문서화

산출물·데이터 = `_pipeline/enhance_202608/` (discovery/ 코드 인벤토리 2종·capture_urls, audit2/ 감사 4종+placeholder, newsheets/ 신규 시트 콘텐츠, newdocs/ PH 문서 원고·형식 레시피).

1. **최신 코드 기준 확보**: `gh repo clone`으로 admin(develop 9e2741b, 08-10)·merchant(e083af8, 08-08) 신선본. 시트 작성 시점(어드민 07.21/가맹점 07.28) 이후 변경 파일 특정(admin 23·merchant 5).
2. **디스크립션 전수 감사·교정(Figma 303:173)**: 감사 4팀 → H/M 교정 **어드민 129노드(전부 Apple SD→Noto 재구성 레시피, 오버플로 58건 폭 고정)** + 가맹점 33노드(Arimo 직접 수정) + 화면 라벨 22건(광고비→플랫폼 차감 12, 락계좌 상태칩 이상→불일치·스킵→검증 필요+색 9, 안내문 1) + **placeholder 심화 행 19노드 복원**(RESIGN·TRANSFER·WEEKDAY·SALES_DT_OLD·PARTNER) + ST_MA_DELIV 키노트 '환급액 그룹' 신규 행. 구판 정산 시트 4장(1665/1592/1667/1695)에 빨간 '신판 참조' 배지. L(줄번호 밀림 ~67건)은 의도적 보류.
3. **누락 화면 보강(신규 시트 8장, 섹션 2759:2883)**: AD_P_HOME·AD_P_SETTLE(총판 시점 2) / AD_MERCHANT_DT_CONTRACTRESET·BIZEDIT / AD_SALES_DT_ADD_RESULT / MC_CONTRACT_SIGN_GATE·BIZ_TYPEFIX / ST_MA_DELIV_REFUND. 화면은 **로컬 실행 캡처 파이프라인**으로 추출: scratchpad `run-admin`/`run-merchant`(목데이터 이식+`?__devuser=` 인증시드+`/__preview/*` 하네스, MOCK_API=1, 3001/3000) → capture.js 태그 + **헤드리스 크롬**(`--headless=new` + 해시 URL, 창 안 띄움 — 사용자 데스크톱 방해 금지 요청) → generate_figma_design 폴링. 미승인 대시보드 2시트(2152/2154)는 화면 제자리 스왑.
4. **PH_화면설계서(IFX) 정산 정책 문서**: 사용자 요청으로 IFX `3783:890` "[정책] 정산" 페이지에 3388:367 형식(A4 정책 프레임)으로 정산 3화면+정산현황·원장 문서 제작 — 원고 `newdocs/settle3_content.md`·`settle_rest_content.md`, 형식 `format_recipe.md`(Apple SD 로드 불가→Noto Black/Bold 신규 생성). ※ 종전 "IFX 안 건드림" 제약은 이 페이지에 한해 사용자 지시로 해제.
5. **발견 사항**: 정산 현황은 6탭(차액 정산·이체 내역·VOC 포함), 총판(참여자) 분기는 별도 레이아웃 없이 userType 가림, `/settlements/[id]/fee-adjustments`는 고아 라우트+404 링크 결함, 계약 초기화 버튼 isAdmin 가드 부재 의심, 플랫폼 '환급액'과 6대 개념 '환급' 매핑 미확정(07 등재 후보).

## 지금 어디까지 됐나

| 트랙 | 상태 | 산출물 |
|---|---|---|
| **A. 기능명세서(어드민)** | ✅ 완료 | `spec/기능명세서_어드민.html` — 법조항식(도메인장→화면절→기능조 번호+브레드크럼+계층네비+검색/권한·화면 필터+FAB). 12도메인·40화면·207기능. |
| **B. 화면설계서 심화(어드민)** | ✅ 117/117 | `spec/design_plus/*.html` — 기존 화면+콜아웃 아래 "정책·계산로직·데이터출처" 심화 섹션 추가. 개발용어 정리됨. 잘렸던 AD_SETTLE·AD_SETTLE_MISSED 전체높이 재캡처+마커 완료. |
| **C. Figma 반영** | ✅ 117/117 | 심화본 전체를 `Tcf69tIciGxmlqCIuRb0iI` node `303:173`에 임포트 완료. 기존 얕은 프레임 117 + 고아 13 삭제, 메뉴(A-01~A-11) 그리드 재배치·라벨 11. **현재 노드 매핑 = `_pipeline/figma_map_deep.json`**(AD_ page_id→심화 node). 검증: AD_SALES·AD_MERCHANT_DT(8215px) 심화 밴드까지 정상. |
| **D. IA 개편** | ⬜ 미착수 | 코드우선·기획자 문체로 IA 상세 재작성 예정. **사용자 결정: 이후 한도 보면서 진행.** |

## 남은 작업 (우선순위)

1. ✅ 완료 — 잘린 캡처 2개 재촬영, scrape 재추출·병합. deepdive_content = **117화면 전체**.
2. ✅ 완료 — **트랙 C: Figma 117화면 임포트**. (아래 재개법 참고)
3. **트랙 D: IA 개편** — 코드우선 상세 재작성. 사용자 결정: 이후 한도 보면서. 토큰 ~1–2M.
4. (선택) AD_SETTLE_MISSED 캡처는 배너 '접힘' 상태 전체페이지 — 펼침 필요 시 devClick 재촬영.

## Figma 재임포트 방법 (트랙 C 재현/보수용)

- **자산**: `spec/design_fig/*.html`(117개) = `design_plus` + capture.js 재주입. 브라우저 자체완결본은 `design_plus`, **Figma 전송용은 반드시 `design_fig`**.
- **서버**: `python3 -m http.server 8899 --directory <repo>/payhug-spec/spec` (nohup 권장 — 중간에 죽으면 이후 임포트 실패). `figcap.sh`가 `/design_fig/<page>.html` 로드.
- **임포트 워크플로우**: `_pipeline/wf_figma_import2.js`(1차, 동시~10) · `wf_figma_retry.js`(실패분 재시도, **동시 3 + captureId 한도초과 자동 재발급 + 폴링 24회**). args는 문자열로 와도 파싱함.
  - ⚠️ **Figma MCP 한도**: 10 동시 임포트는 rate limit(Full seat) 걸림 → 대량은 청크 3~4로. 1차 116개 중 52 실패(대부분 한도) → 재시도로 52/52 복구.
  - 결과 node_id는 저널(`subagents/workflows/<run>/journal.jsonl`)에서 `ok&&node_id`로 병합. → `figma_map_deep.json`.
- **정리·재배치**: `gen_delete_shallow.js`/직접 use_figma로 (얕은 AD `figma_map_shallow`의 AD_ 117 + 고아=node≥1584 & KEEP 미포함) 삭제 → `gen_reposition_deep.js`→`reposition_code_deep.js`→use_figma(`return` 필수).
- **비용 실측(참고)**: 임포트 3.34M + 재시도 1.54M + 정리/검증 ≈ **약 5M 토큰**. 사전 "1.5–2.5M" 추정보다 큼(원인 = 폴링 루프·에이전트 168개의 도구스키마/오케스트레이션 오버헤드. DOM은 Figma로 직접 전송돼 컨텍스트 미경유하나 그 외가 누적).

## 재개 방법 (파이프라인)

- **모든 스크립트·데이터 = `payhug-spec/_pipeline/`** 에 영구 복사됨.
  - 데이터: `deepdive_content.json`(116화면 심화) · `spec_content.json`(기능명세 207) · `screen_manifest.json`(208화면 메타) · `figma_map.json`(page_id→node_id) · `screens_all_config.json`(어드민 심화 대상+파일번들).
  - 렌더: `render_deepdive.js`(design/HTML+심화 append+캡처 base64→design_plus) · `render_spec.js`(기능명세 법조항식).
  - 워크플로우: `wf_deepdive_all.js`(베이스2패스/변형1패스) · `wf_spec.js` · `wf_tag.js`(화면·권한 태깅) · `wf_figma_import.js`.
  - 캡처: `shot_png.sh`(헤드리스 PNG) · `figcap.sh`(Figma 전송).
- ⚠️ **스크립트 내 CONTENT/OUT 경로가 옛 세션 scratchpad를 가리킴** → 재실행 시 `_pipeline/`의 json으로 repoint 필요.
- 렌더 예: `deepdive_content.json` 수정 → `node render_deepdive.js`(경로 조정 후) → `spec/design_plus/*.html` 갱신.

## 핵심 원칙·제약 (짧게)

- **작성 플로우 = 코드 정독→기능 전량추출→기획자 문체 번역→검증 에이전트**. md 재포맷 금지, 코드우선.
- 심화는 **추가만**(기존 콜아웃 삭제 없음). 개발용어(함수·route·DB·상태상수·내부라벨상수 MARGIN 등) 금지→한글.
- **확정/가설/확인필요** 표기. 서버 전용(최종 산술·스크래핑 스케줄·수수료율 C1·지급캘린더 C2·예상차액 C4)은 확인필요.
- 6대 개념(미지급금·선정산제외금액·바로이체·과지급·미회수금·환급) 분리. 어드민 '매출 회수'(락계좌→모계좌 스윕)≠정책 '회수'(과지급).
- 프론트 레포: 어드민 `01_payhug-admin-web-main`(:3001, MOCK_API). 가맹점 `02_payhug-merchant-web-main`(:3000)은 사용자가 직접(IFX Figma) — **건드리지 않음**.
- Figma 타깃 = `Tcf69tIciGxmlqCIuRb0iI` `303:173`(내 그리드). 사용자 IFX(`IFX4GRC60ibOVCWNrd6VQt`)는 절대 안 건드림.

## 결정 대기

- **트랙 D(IA 개편)만 남음.** 사용자 결정: 이후 주간 한도 보면서 진행. 착수 시 화면설계·기능명세와 같은 코드우선·기획자 문체.
