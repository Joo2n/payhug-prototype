# agentpack_report — Claude Code 에이전트·커맨드 팩 생성 기록 (26.08.15)

PayHug 문서 작업 규칙(CLAUDE.md 절대 원칙, PROGRESS 08-12·08-13 세션, round2 규격·로그·QA, newsheets 골드 스탠더드)을 재사용 가능한 에이전트 정의 8종 + 슬래시 커맨드(스킬) 4종으로 성문화했다. 생성 위치 = `~/cursor/payhug/.claude/`. 파일 생성만 수행(Figma 무접촉).

## 생성 파일 12개

### A. 에이전트 8종 — `.claude/agents/`

| 파일 | 역할 | Figma | 핵심 내재화 규칙 |
|---|---|---|---|
| `policy-analyst.md` | 자료→결정/방향/액션/미결 추출, 정책서 9문서·01~07 매핑, 용어 대조 | 읽기 전용(도구 없음) | C1·C2·C4 채택 판단 금지, 계약↔운영 매핑 금지, 확인필요 승격 조건 |
| `policy-writer.md` | format_recipe4 §3.7 DSL 원고 작성·증분 | 없음 | 절 표준 흐름 6구획, EQ마다 EX 사전 검산+검산표, 42줄·PAGEBREAK, C1/C2/C4 고정 문구 3종, 부호 무색 |
| `policy-typesetter.md` | DSL→IFX 3783:906 A4 조판 | 쓰기(직렬) | Noto Sans KR 타이포 체계, 2-pass reflow, 표·박스·인라인 빨강 규격, DSL 누출 0 자가 스캔, 그리드 44,240/637×900, 섹션 밖 금지 |
| `sheet-auditor.md` | 서준 파일 시트 텍스트 감사 — OK설명체/변경이력체/빈약/영문노출 4판정(취지 기반) | 읽기 전용 | 레이어 이름 판정 금지(스테일), 텍스트 앞 30자 병기(재특정 대비), 재작성 취지 열 |
| `sheet-writer.md` | 키노트 8쌍+심화 13행(3/3/2/5) 원고 — admin_content.md 스키마 | 없음 | 코드 외 근거 없음+HEAD 명기, 상태 4종, 현재 상태 서술만, 영문은 근거 열만 |
| `sheet-applier.md` | 서준 파일 직렬 적용 | 쓰기(직렬) | 노드 재특정(정규화 텍스트 매치), pill 4종 실측 색값, Apple SD 재구성 레시피(스타일 복사→Noto 신규→같은 인덱스), 폭 캡, 크롭 컨테이너 오확대 사고 방지, 마커 최상위 |
| `screen-capturer.md` | run-* 사본→헤드리스 크롬→generate_figma_design→clone·리매핑·rescale(1250/w) | 쓰기(추출 후처리) | `--headless=new`+해시 URL 창 금지, MOCK_API=1·`?__devuser=`·`/__preview/*`, 동시 3~4 청크, 원본 레포 무수정 |
| `doc-qa.md` | 원고 대조 PASS/FAIL — 텍스트 일치·이력체 0·DSL 누출 0·산식 검산·레이아웃 | 읽기 전용 | design context 실 문자값 기준, DSL 마커 16종 스캔 목록, 끝 y ≤ 780, FAIL 시 재작업 지시 가능 형식 |

### B. 커맨드(스킬) 4종 — `.claude/skills/`

| 파일 | 사용법 | 오케스트레이션 |
|---|---|---|
| `policy-sync/SKILL.md` | `/policy-sync <자료 경로>` | analyst(병렬)→영향 매핑→writer(병렬)→typesetter(직렬)→doc-qa→07 동기화·zip 재생성·PROGRESS→기획 레포 커밋. FAIL 재작업 1회 한도 |
| `sheet-update/SKILL.md` | `/sheet-update` | gh clone(읽기만)→기준 커밋 diff→auditor(병렬)→writer(병렬)→applier(직렬)→신규 화면은 /screen-add 위임→doc-qa→새 기준 커밋 기록 |
| `screen-add/SKILL.md` | `/screen-add <화면 경로·상태>` | capturer→템플릿 2103:2 clone+136슬롯 인덱스 맵(1/3/7/11/24, 키노트 29+3k·30+3k, 54, pill 63~135 13개, 마커 15~22)→마커 배치→doc-qa→맵 파일 등재 |
| `qa-report/SKILL.md` | `/qa-report [라운드 경로]` | 스크린샷 수집·sips 리사이즈→전/후·판정표 HTML(artifact-design 선로드, base64 임베드)→Artifact 게시(같은 경로 재게시)→게시 기록 |

## 공통 규율 (12개 파일 전부에 동일 수록)

1. 본문은 현재 상태만 — 변경이력체 금지, 적용 전 이력체 스캔
2. 순한글 — 영문 식별자는 근거 열·SRC 줄만
3. C1·C2·C4 값 단정 금지(고정 문구 인용), 6대 개념·회수 3갈래 혼용 금지
4. Figma 쓰기 단일 세션 직렬, 범위 = 서준 Tcf69tIciGxmlqCIuRb0iI(303:173 계열) / IFX 3783:890(섹션 3783:906) 한정, 캡처는 헤드리스만
5. 데스크톱 아카이브·프론트 원본 레포 무수정(클론 읽기만), 커밋은 기획 레포만
6. 산출물은 `_pipeline/enhance_YYYYMM/roundN/` 파일 보존, 에이전트 최종 응답 5줄 요약

## 규칙 원천 (성문화 근거)

- `CLAUDE.md` — 절대 원칙 7·미확정 3대·작업 방식
- `payhug-spec/PROGRESS.md` — 08-12(캡처 파이프라인·재구성 레시피)·08-13(정화 규율·정책서 3차) 세션 블록
- `round2/format_recipe4.md` — 조판 규격·DSL / `round2/settle3_rewrite.md`·`newsheets/admin_content.md` — 시트 원고 스키마(3/3/2/5)
- `round2/apply_report_sheets.md`·`final_apply.md` — 적용 규약(pill 색값·노드 재특정·폰트 레시피·크롭 사고·그리드·꺾쇠 재연결)
- `round2/qa_sheets.md`·`qa_policy.md` — QA 항목(실 문자값 대조·DSL 스캔·검산·레이어 이름 판정 금지)

## 사용법 요약

- 에이전트는 Agent 도구의 subagent_type으로 직접 지정 가능(예: policy-analyst), 커맨드는 `/policy-sync` 등 슬래시로 호출.
- 커맨드가 오케스트레이션 순서·병렬/직렬 경계·재작업 한도까지 지정하므로, 세션은 커맨드 1회 호출로 라운드 전체를 재현한다.
