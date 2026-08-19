# PayHug 화면설계·기능명세·IA 진행 상태

> **이어쓰기 문서.** 다음 세션은 이 파일만 보면 이어서 진행 가능. (worktree = `~/cursor/payhug` 전용)
> 최종 업데이트: **2026-08-19**

## 2026-08-19 세션 — 회원관리 계약 체인 TO-BE 화면설계 (신규 페이지 2807:2212)

산출물 = `_pipeline/member_redesign/`. 근거 = 개편안 v2(`source_v2.txt`, 정산상품 제거·관계 요율) + v1 대조. 사용자 결정: ① 요율 UI = **세트 전체**(채권매입·시스템이용료·이체수수료+VAT+납부·수취를 관계 Edge에) ② 범위 = 제거 영향까지 9장.

1. **에이전트 팀 파이프라인**: 분석·원고·목업 3조 병렬 → Figma 임포트 1조 → 조립 3조 직렬(3장씩) → doc-qa → 보수 1조. 총 9에이전트.
2. **코드 분석**(`code_analysis.md`): 회원관리 뼈대 전부 재사용 가능, 유형 규칙·관계 모델은 신규(프론트에 relation 모델 전무). 정산상품 참조 = 화면 4곳+API 3계열, 제거 영향 a화면5/b서버8/c이행4. **정책 확인 필요 12건**(P2 투자자·페이허그 배분 자리, P5 파트너 위치, 정산 실행 게이트 대체 기준, 추천코드 체인 시작점 등).
3. **원고 9장**(`manuscripts/`): 키노트 8쌍+심화 13행(3/3/2/5)×9, 심화 117행 = 확인필요 47·신규 41·확정 19·가설 10. C1 전 시트 '예시' 고정.
4. **목업 9종**(`mockups/m1~m9.html`): 자체완결 HTML, 실코드 Tailwind 값 역산(사이드바 #1B2537·primary #7FE141/#4da119), TO-BE 사이드바(정산 상품관리 없음), 요율 칩은 전부 연결선(Edge) 표기. **프론트 반영 시 마크업 기준** — 프론트 레포는 커밋 금지 규율이라 브랜치 대신 목업 채택.
5. **Figma 시트 9장**: 페이지 `2807:2212`, 템플릿 2103:2 clone, x피치 2200. 노드 = AD_MEMBER 2839:2 / ADD 2847:2 / ADD_TOP 2849:2 / EDIT 2853:2 / PROFILE 2860:2 / CHAIN 2862:2 / EXCEPT 2866:2 / GNB 2873:2 / MERCHANT_FEE2 2875:2 (`sheets_map.json`). 원본 임포트 = 2829:2~2837:2([정산_정책 백업] 페이지 2822:2294 — 이동 보류). **AS-IS 현행 manifest에는 미등재**(TO-BE 제안이므로 오염 방지).
6. **QA**(`qa.md`): 6 PASS/3 FAIL → 보수(제목 랩 3·CHAIN 심화11행 재서술·칩 예시 병기 2) 후 해소. 조립 요령 축적 = 슬롯 실물 재특정·목업 폰트 전량 Noto 재구성·"원본 페이지에서 재구성 후 이동"·FILL 칩 연쇄 수축 주의(`figma_apply.md`).
7. **리포트 뷰**: Artifact "회원관리 계약 체인 설계" — 목업↔시트 갤러리+분석+QA. 빌더 = `build_report.py`(이미지 = 세션 scratchpad).
8. **결정 라운드(08-19)**: 사용자 답변 + 회의록 이미지 2장(8.14 원장/계약 구조) 반영 — **확정 15**(P5 상위 없음 선택=최상위 자동 판별, P2 투자자=선택적 병렬 참여, P4 다우=제휴사·직계약(채권매입 없음), 이체수수료 전 건 300원 고정, 계정 자동 생성 규칙: 아이디=기업 코드 4자+순번·비밀번호=휴대폰 뒤 4자리·추천코드=난수, 폭포수/병렬 배분 구분 등)·유력 2·미결 7. 레지스터 = `decisions_0819.md`. 미결 9문항은 결정 콘솔 Artifact(제출 버튼으로 저장하는 방식)로 수집.
9. **인터랙티브 프로토타입**(개인 비공개 레포 `Joo2n/payhug-member-redesign`, 로컬 `~/cursor/payhug-member-redesign`): `index.html` = 계약 위치 라디오판(46상태 하네스, 비교용 보존) / `v2.html` = 정책 반영판(자동 판별·계정 자동 생성·이체료 고정·다우 직계약·투자자 병렬, 51상태 하네스·셀프테스트 20/20). 팀 공유용 구조 설명서 = `회원관리_계약체인_구조서.html`(v3, 이전 버전 스냅샷 `구조서_버전/`).
10. **상태 매트릭스(Figma)**: 카탈로그 51상태(`states_catalog.md`, Flow A 등록 7·B 상위선택 10·C 요율 6·D 프로필 7·E 검증 4·F 예외 6·G 노출 위치 비교 6·H 병렬 배분 5) → `?state=` 하네스 헤드리스 캡처 임포트 v1 46·v2 51(`state_import_map*.json`) → 회원관리 페이지(2807:2212) y=4200부터 **54장 조립**(본편 v2 51 + Flow B 뒤 "비교안 — 계약 위치 라디오" v1 3) + 헤더 밴드 9·라벨 108(`assembly_v2_result.md`). doc-qa 전수 **PASS 6 / FAIL 0**(`qa_matrix_v2.md`). 보관 페이지(2822:2294) 미사용 v1 상태 43장 삭제·목업 원본 9장 보존(`cleanup_v1_log.md`).
11. **미결**: ① 결정 콘솔 9문항 제출 대기 — 수신 즉시 v2 프로토·시트 9장·구조서·`decisions_0819.md` 동기화 ② 시트 9장에 P5 자동 판별·계정 자동 생성·이체료 고정 반영 갱신 ③ 07_OPEN_QUESTIONS 등재 검토 ④ 결정 후 서버 API 스펙(관계 CRUD·체인 조회·요율 검증) 초안.

## 2026-08-15~16 세션 — 8/15 회의 반영 · 용어 출처 증명 · 클러스터 재편 · 에이전트 팩

산출물 = `_pipeline/enhance_202608/round3/`. **자동화 커맨드 신설** = `.claude/agents/`(8종) + `.claude/skills/`(`/policy-sync` `/sheet-update` `/screen-add` `/qa-report`) → [[project_payhug_agent_pack]].

1. **8/15 회의 반영**(`meeting_changes.md`, 근거=Gemini 회의록 전사): 결정 15·방향 8·액션 16·미결 10 추출→장절 매핑. 핵심 = ① 선정산 시작일 이전 거래의 플랫폼 차감·환급은 지급액 미가감(개발 반영 완료)+'조정 금액' 전면 비노출 ② 이미지급 = 기록용 수동 이체 → 바로이체의 일종(선정산 제외 포함·가맹점엔 실제 이체일 기준 노출), 회수 기능 도입 후 버튼 제거·태그 유지 ③ 배민·쿠팡이츠 제외 건 리스트 연동(프론트 미반영·티켓)·리스트=지급일/툴팁=거래일.
2. **용어 출처 전수 증명**(`term_provenance.md`, 사용자 질문 "정산 차액·잔차 어디서 나왔냐"): 112용어 → 화면 표기 83·코드 내부 8·스펙 문서 10·**작성 정의 14**. 질문 13종 전부 화면 근거 확인(잔차=제외액 카드 보조문구, 검증 차이=지급액 하단 줄). **'정산 차액'은 정책서에 없던 용어**이고 화면 '정산차액'은 플랫폼 조정 항목 → 용어장에 구분 행. 작성 정의 14종은 전부 화면 문구로 치환(장부→원장, 출금전용계좌→락계좌 등 81곳).
3. **클러스터 재편**(`regroup_plan.md`→`final_apply_r3.md`): 6클러스터(0 읽는 순서/A 개념·용어/B 실행·결과/C 차액/D 배분·원장/E 이체·대사) 다크 헤더 밴드, 87노드 재배치, 화면 첨삭 13장(라벨 카드+빨간 박스 15+꺾쇠 10), **Flow 2장 수정 11건**(시작일 분기·바로이체—기록형 재라벨·회수 점선 노드 등). 섹션 4500×14560.
4. **재조판**(`dsl_delta.md`→`build_report5.md`): 치환·회의 결정이 9문서 전부에 닿아 **28면 전면 재조판→29면**(자동 분할 1), 구판 28면 삭제, 넘침 0.
5. **재조판 QA**(`qa_r3.md`→`qa_r3_final.md`, Figma 읽기 전용 3개 조 병렬): 원 결함 23건(빨강 규율 4·위상 2·참조 4·치환 11·형식 2) 중 **21 해소·2 부분**, 회귀 0(6밴드 좌표·섹션 크기 무변동, 신규 겹침 0). 감사 범위를 Flow 2장으로 넓히며 선존 미보고 3건 + 회귀 성격 1건이 드러나 잔여·신규는 `fix_r3_round2.json` 9건으로 처리 중. 결함 23건 중 14건이 조판 실수가 아닌 **원고 누락**이어서 원고(`dsl_delta.md` 18곳 — 치환 범위 선언·죽은 상호참조 제거·확정/미확정 줄 분리)와 규격서(`round2/format_recipe4.md` §3.10 주변 자산 동기화 규칙 신설, 판정 단위를 자산이 아닌 지면으로 규정)를 먼저 고쳐 재발 방지. 정책 판단이 서야 고칠 수 있는 5건은 `07_OPEN_QUESTIONS.md` §7로 이관.
6. **미결**: 서비스 정책서 초안 폴더(`~/Desktop/01_PayHug/02_정책/01_서비스 정책서/초안`)가 macOS 권한으로 접근 불가 → 사용자 복사 대기(용어 일원화 대조 G5 보류).

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
