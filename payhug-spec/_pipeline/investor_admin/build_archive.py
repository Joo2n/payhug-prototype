#!/usr/bin/env python3
# 투자자 어드민 작업물 아카이브 생성기 — 실행할 때마다 현재 상태로 갱신
import os, re, html, datetime, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import counts

REPO = "/Users/semi/cursor/payhug-investor-admin"
PIPE = "/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin"
OUT  = os.path.join(REPO, "archive.html")
# 레포 파일은 상대 경로 — 서버 없이도, Pages 에서도 열린다.
# 파이프라인 파일은 배포본에 없다. 링크를 걸면 전건 죽은 링크가 되므로 경로 문자열로만 싣는다(G-7).
REPO_URL, PIPE_URL = "", None
# 배포 호스트가 내주지 않는 파일 — 링크를 걸면 로컬에선 열리고 배포에선 404 다.
# Vercel 정적 배포는 README.md 를 산출물에서 뺀다(실측: /README.md 404 · /DESIGN_REF.md 200).
# 그래서 README.md 는 링크 없이 경로 문자열로만 싣는다.
NO_SERVE = {"README.md"}
# 배포 = git 이 추적하는 것만 나간다. 추적 밖 파일은 로컬에 있어도 배포에서 죽는다.
TRACKED = set(subprocess.run(["git", "-C", REPO, "-c", "core.quotepath=false", "ls-files"],
                             capture_output=True, text=True).stdout.split("\n"))

DESC = {
 "index.html":"랜딩 — 전 화면 목록 진입점","app.html":"통합 프로토타입 — 메뉴·버튼이 실제 동작하는 단일 HTML",
 "glossary.html":"계산식 용어 정의 — 화면 기준 매핑표 27행·용어 카드 50건(화면 용어 28·내부 용어 22)·정의 요청 26문항","capability.html":"투자자 뷰·기능 — 할 수 있는 것과 보여줄 수 있는 것",
 "archive.html":"이 페이지 — 작업물 추적","login.html":"로그인",
 "terms-edit.html":"용어 정의서 편집판 — 대표 정의 45항·그 자리에서 고쳐 저장",
 "final-terms.html":"용어·기호 정리 — 기존 표기 → 바뀐 기호",
 "calc.html":"계산식 하나씩 — 변수 정의 → 산식 → 대입 → 결과",
 "steps-all.html":"화면 칸별 중간 계산 — 투자 자산·투자 수익 두 화면의 값",
 "ceo-questions.html":"대표님 확인 문항 — 답을 적어 저장",
 "inquiry.html":"대표 확인 요청 — 문항 5건·문항별 평문 복사 + 개발·백엔드 부록",
 "ceo_definitions.md":"대표 정의 원문 — 계산식 용어","ceo_impact.md":"대표 정의 기준 산출물 영향 분석 — 27건",
 "ceo_inquiry.md":"대표 확인 요청 원고 — 문항 5건 + 개발·백엔드 부록","value_lineage.md":"값 계보 추적 — 용어별 소재·신설 목록·이름 충돌표",
 "term_mapping.md":"화면 기준 용어 매핑 — 매핑표 27행·층위 28/22·개명 15건·대표 정의 전수 대조",
 "verify_glossary.js":"용어 문서 헤드리스 검증기 — 앵커·오버플로·층위 필터·기호 검색",
 "invest-assets.html":"투자 자산 — 현황·가맹점별 표·산식 카드","certificate.html":"투자자산 증명서 — 미리보기·서명 검증",
 "invest-profit.html":"투자 수익 — 기간 검색·일별 표","coocon.html":"쿠콘 관리 현금 — 메뉴에서 We-bank 로 바로 이동",
 "invest-sim.html":"투자 시뮬레이션 — 기준 변수 6·정산금채권 8행 입력·실행 전",
 "invest-sim--result.html":"투자 시뮬레이션 · 실행 결과 — 투자 요약·채권별 산출·현황·수익 현황·일별 투자수익",
 "simulation_design.md":"투자 시뮬레이션 설계 — 입력 8종·결과 5블록·산식 의존 그래프·논리 5건",
 "build_sim_static.py":"투자 시뮬레이션 낱장 생성기 — 낱장 2종 + 사이드바 8메뉴 동기화",
 "verify_sim.js":"투자 시뮬레이션 검증기 — 기본값 실행·입력 변동·음수 수익·기간 밖 제외·행 추가삭제·버튼 비활성",
 "verify_sim_result.json":"투자 시뮬레이션 검증 결과",
 "invest-profit--weekly.html":"투자 수익 · 주별 — 집계 단위 주별 · 프리셋 4주(2026-08-03~08-27) · 4행",
 "invest-profit--monthly.html":"투자 수익 · 월별 — 집계 단위 월별 · 프리셋 6개월(2026-03-01~08-27) · 6행",
 "invest-profit--empty.html":"투자 수익 · 결과 없음 — 원장에 없는 기간(2026-02-01~02-07) 조회",
 "period_design.md":"투자 수익 기간 필터 설계 — 두 축 분리·집계 단위 스냅·프리셋 묶음",
 "ty_bucket_fix.md":"버킷 Ty수익율 산식 정정 — 일자별 ty 가중평균 → SMR x 365 / SD",
 "verify_period.js":"기간·집계 단위 조작 검증기","verify_period_result.json":"기간·집계 검증 결과",
 "fix_period.py":"기간 필터 재설계 패치기","sync_profit_static.py":"투자 수익 낱장 5종 동기화기",
 "sync_assets_static.py":"투자자산 낱장 4종·증명서·투자자산 엑셀 미리보기 2종·가맹점·계약기록 건수 재생성기 — 요약 카드·현황표·로스터 표를 라벨과 열머리로 잡아 모델에서 다시 그린다. --check 는 쓰지 않고 어긋난 낱장만 보고",
 "merchants.html":"가맹점 — 목록·필터","acquisition.html":"정산채권 양수 — 목록","contracts.html":"계약기록 — 문서 보관함",
 "password.html":"비밀번호 변경",
 "request_register.md":"요청 레지스터 — 확정 결정·요청 항목·게이트·루프 절차 (누락 판정 기준)",
 "glossary_manuscript.md":"용어 원고 — 매핑표 27행 + 카드 50건","capability_manuscript.md":"투자자 뷰·기능 원고",
 "new_screens_manuscript.md":"PPT 밖 추가 화면 원고 14건","screen_inventory.md":"화면 전수 인벤토리·결함 20건",
 "storyboard_coverage.md":"스토리보드 대비 커버리지 대조","figma_audit_8.md":"Figma 기존 8장 검수",
 "figma_import_plan.md":"Figma 임포트 계획 — 33프레임·11청크","deploy_verify.md":"배포 경로 실측 검증",
 "verify_loop1.md":"1차 검증 루프 — 29항목 판정","verify_loop2.md":"2차 검증 루프",
 "rate_recalc.md":"요율 배분 재계산·검산","rate_fix_map.json":"요율 정정값 맵",
 "rate_apply_result.md":"요율 정정 적용·로스터 통일 결과 — 검산·재검증 전문",
 "roster16_model.py":"로스터 모델 — 요율·가중평균·비중 잔차 산출",
 "roster16_apply.py":"폐기 — 대체: sync_assets_static.py. 옛 값 문자열을 locator 로 쓰던 정적 HTML·xlsx 적용기",
 "roster16_apply.log":"적용 로그 — roster16_apply.py 폐기 시점의 마지막 실행 기록",
 "patch_build_app.py":"통합본 생성기 데이터셋·산식 패치기",
 "verify_identity.js":"통합본 항등식 검증기 — 조작 후 재검산","verify_identity_result.json":"항등식 검증 결과",
 "verify_crossscreen.py":"화면 간 정합 대조기 — 정적 HTML↔app.html↔xlsx",
 "verify_app.js":"통합본 헤드리스 검증기","verify_run.log":"통합본 검증 실행 로그",
 "build_app.py":"통합본 생성기",
 "app_spec.json":"통합본 제작 사양","sync_app_spec.py":"통합본 사양 개수 동기화기 — _meta.counts 를 사양 배열·저장소 실측으로 덮는다","app_build_notes.md":"통합본 조립 지침","app_build_result.md":"통합본 제작 결과·검증",
 "DESIGN_REF.md":"디자인 실측 레퍼런스","README.md":"레포 안내",
 "review.html":"순차 확인 — 무엇을 어느 순서로 볼지 단계별 항목",
 "glossary-legacy.html":"용어 해설 구버전 — 만기 10~13일·ty 3.57% 시절의 동결 스냅샷. 대표 정의(만기 2.0~6.2일)와 뿌리부터 어긋나 배포에서 뺐다. 파이프라인에만 둔다",
 "feasibility.html":"구현 가능성 검토 — 화면·데이터 항목별 실현 조건. 착수 불가 0건",
 "feasibility.md":"구현 가능성 검토 원고 — 등급 A38·B36·C37·D11·E0",
 "base.css":"공용 스타일 — 실측 디자인 토큰(사이드바 #1B2537 · primary #7FE141)",
 "sheet.css":"엑셀 미리보기 전용 스타일 — xls-*.html · app.html 로드",
 "template.html":"화면 스켈레톤 — 사이드바·헤더 슬라이스 원본. 사이드바 메뉴 8개 실측이 여기서 나온다",
 "components.html":"컴포넌트 갤러리 — 버튼·배지·표·토스트 견본. 화면 제작용 스니펫 원본, 배포 대상 아님",
 "logo-icon.png":"로고 원본 이미지. 화면 렌더는 base.css data URI 사용",
 "build_index.py":"랜딩 생성기 — 화면·상태 카드 전량 등재",
 "build_archive.py":"이 아카이브 생성기 — 실행 시점 파일 목록·작업 목록 갱신",
 "build_xlsx.py":"엑셀 %d종 생성기 — 화면 표와 같은 값·서식" % counts.C['xlsx'],
 "build_docs.py":"투자자산 증명서 PDF 생성기",
 "build_sigtext.py":"계약서 원문 텍스트 생성기",
 "contract_text.py":"계약서 원문 — 화면·다운로드 텍스트의 단일 원본",
 "wire_docs.py":"문서 링크 연결기 — 화면 버튼 ↔ assets/docs 실물",
 "wire_final.py":"화면 간 링크·진입점 최종 연결기",
 "wiring_final.md":"링크 연결 결과 대조표",
 "prep_fig.py":"Figma 임포트용 캡처 전처리기",
 "figcap_ia.sh":"Figma 캡처 스크립트 — 1240px·87px 보정 적용본",
 "probe_current.js":"현행 화면 DOM 탐침기",
 "rate_recalc.py":"요율 배분 재계산기","rate_recalc.log":"요율 재계산 실행 로그",
 "rate_fix_map_gen.py":"요율 정정값 맵 생성기","rate_fix_verify.py":"요율 정정 검산기",
 "verify_links.py":"링크·바이트 일치 검증기 — 다운로드 버튼 ↔ 실파일",
 "verify_app_result.json":"통합본 검증 결과",
 "verify_toast.js":"토스트 실물 검증기 — 실제 노출 여부·문구",
 "verify_toast_result.json":"토스트 검증 결과",
 "verify_feasibility.js":"구현 가능성 문서 검증기","verify_feasibility_result.json":"구현 가능성 검증 결과",
 "figma_import_targets.json":"Figma 임포트 대상 프레임 목록",
 "figma_map_investor.json":"Figma 프레임 ↔ 로컬 파일 대응표",
 "figma_import_result.md":"Figma 임포트 결과·미해소 항목",
 "marker_legend.md":"대표 정의 번호 마커 ③④⑤⑥ 대응 풀이",
 "grade_revision.md":"착수 불가 3건 재판정 — E-1·E-2·E-3 등급 재산정과 실측 근거",
 "behavior_parity.md":"원본 어드민 동작 대조 — 클릭·입력 실측",
 "behavior_fix.md":"동작 정정 대상·적용 범위",
 "ui_fidelity.md":"UI 실측 대조 — 토큰·간격·타이포",
 "ui_fix_result.md":"UI 정정 결과",
 "fabrication_audit.md":"근거 없는 서술 감사 — 지어낸 값·단정 적발",
 "modal_audit.md":"모달 닫힘 경로 조사 — 오버레이·본문 클릭·ESC 실측과 원본 대조",
 "fabrication_fix.md":"근거 없는 서술 교정 결과",
 "artifact_gap.md":"산출물 공백 목록 — 요청 대비 미제작분",
 "vercel_deploy.md":"Vercel 프리뷰 경로·MIME 점검",
 "ceo_definitions.docx":"대표 정의 원문 문서본",
 "todo.json":"작업 목록 원장 — 아카이브 작업 표의 원천",
 "gate_fix.md":"게이트 미달 5건 해소 결과 — 집계·예시 고지·구값·링크·문체 + 토스트 정정, 재검증 5종",
 "daily_ledger.py":"채권 원장 — 화면·엑셀 숫자의 단일 원천. 채권 20,944건 생성·미회수 합 고정·일별 롤업",
 "ledger_facts.json":"채권 원장 사실값 — 검증기가 읽는 기준 수치",
 "sim_facts.py":"투자 시뮬레이션 기대값 산출기 — build_app.py 씨앗을 읽어 verify_sim.js 기대값을 낸다",
 "sim_facts.json":"투자 시뮬레이션 기대값 — 시나리오 8종의 화면 표기값",
 "platform_duration.py":"플랫폼별 만기·미지급률·과지급률 실측값",
 "apply_duration.py":"플랫폼 만기 실측값 적용기 — 원장·화면·원고 일괄 갱신",
 "build_glossary.py":"용어 해설 생성기 — 원고 → 카드 50건·캡처 오버레이",
 "read_finaledit.py":"용어기호정리 편집판 HTML 을 원고 꼴로 되읽어 final_terms.json 과 견준다. 차이 목록만 내고 원고에 쓰지 않는다",
 "read_wordedit.py":"워드에서 고친 용어기호정리를 원고 꼴로 되읽어 final_terms.json 과 견준다. 차이 목록만 내고 원고에 쓰지 않는다",
 "termsfacts.py":"용어정의서 원고의 {{키}} 자리에 넣을 숫자를 원장 한 곳에서 읽어 온다. 워드판·HTML 편집판이 함께 쓴다",
 "verify_banned.py":"금지 낱말·어투 기계 검사 — dm_0901/banned_words.md 목록을 읽어 워드·엑셀·화면·원고를 훑는다. 대표 원문 인용·기존 표기 칸·화면 라벨·미확정 표시는 가려낸다",
 "restructure_glossary.py":"용어 원고 재구성기 — 서술 절 → 카드 5필드",
 "glossary_restructure.md":"용어 해설 재구성 설계 — 카드 구조·부록 분리 기준",
 "capture_shots.js":"용어 해설용 화면 캡처기 — 정적 낱장 헤드리스 촬영",
 "shot_rects.json":"캡처 좌표 실측값 — 용어별 강조 상자 위치",
 "verify_shotmarks.py":"캡처 마커 검증기 — 좌표가 실제 칸을 가리키는지",
 "verify_shotmarks_result.json":"캡처 마커 검증 결과",
 "symbol_inventory.json":"대표 정의 원문 기호 추출 목록",
 "symbol_glossary.json":"기호 사전 데이터 — 기호별 이름·산식·쓰임",
 "symbol_glossary.md":"기호 사전 원고 — 부록 A 원천",
 "verify_glossary5.js":"용어 카드 5필드 검증기 — 필드 누락·구버전 링크·표제어 대조",
 "verify_glossary5_result.json":"용어 카드 검증 결과",
 "build_demo.py":"시연본 분리 생성기 — 통합본에서 바깥 통로를 걷어 낸 판",
 "demo_split.md":"시연본 분리 설계 — 저장소 분리·통로 차단 기준",
 "gate_prototype.js":"시연본 배포 게이트 — push 전 차단 검사",
 "gate_glossary.js":"용어 해설 배포 게이트 — push 전 차단 검사",
 "sync_prototype.sh":"시연본 배포 동기화 절차 — 빌드·게이트·push·배포 실측",
 "sync_glossary.sh":"용어 해설 배포 동기화 절차 — 빌드·게이트·push·배포 실측",
 "verify_proto.js":"시연본 검증기 — 메뉴·상태·다운로드 실물·바깥 통로",
 "verify_proto_result.json":"시연본 검증 결과",
 "verify_sync_chain.js":"원본 ↔ 시연본 변환 손실 검증기",
 "verify_sync_chain_result.json":"변환 손실 검증 결과",
 "verify_deployed.py":"배포 3주소 실측 검증기 — 익명 수신 바이트 대조",
 "verify_deployed_result.json":"배포 실측 검증 결과",
 "verify_password.js":"비밀번호 화면 검증기 — 원본 훅 동작 대조",
 "verify_password_result.json":"비밀번호 화면 검증 결과",
 "verify_rows.js":"표 행 검증기 — 행수·순번·선택 상태",
 "verify_rows_result.json":"표 행 검증 결과",
 "verify_0828.py":"8/28 미팅 결론 26항목 기계 검사기",
 "verify_0828_result.json":"8/28 미팅 결론 검사 결과",
 "verifiers.md":"검증기 명부 — 대상·검사 범위·폐지 이력",
 "meeting_20260828.md":"대표 미팅 기록 2026-08-28 — 결론 원문",
 "parity_audit_0828.md":"실제 프론트 대조 감사 — 화면·요소·판정·근거",
 "screen_fix7.md":"화면 정정 7건 — 대상·적용 범위·재검증",
 "term_box_unify.md":"용어 블록 통일 — 화면 라벨과 용어 해설 표제어 대조",
 "monthly_fix.md":"월별 표 재설계 — 원장 롤업으로 단일화",
 "figma_reimport.md":"Figma 재임포트 — 대상 프레임·교체 결과",
 "figma_reimport2.md":"Figma 재임포트 2차 — 델타 프레임 교체 결과",
 "figma_plan_0828.md":"Figma 임포트 계획 2026-08-28 — 프레임 배치·측정값",
 "figma_ops_0828.json":"Figma 임포트 조작 목록 — 프레임별 노드 작업",
 "fig_meas.json":"Figma 스테이징 기하 실측 — value 칸 좌표",
 "fig_heights.json":"Figma 프레임 높이 산출값",
 "run_import_0828.sh":"Figma 임포트 실행 절차 — 전처리·측정·캡처 일괄",
 "build_ops.py":"Figma 조작 목록 생성기",
 "fix12_gen.py":"통합본 정정 12건 패치기",
 "fix12_static.py":"정적 낱장 정정 12건 패치기",
 "fix_meeting0828.py":"미팅 결론 적용 패치기",
 "fix_round2.py":"폐기 — 대체: sync_assets_static.py(투자자산 표·건수) · contract_text.py(계약서 원문). 입력 낱장 contracts--downloaded.html 이 없어 실행 자체가 불가",
 "fix_rows.py":"표 행 정정 패치기",
 "probe_nums.js":"화면 숫자 탐침기 — 렌더 값 수집",
 "probe_cert.js":"증명서 화면 탐침기 — 렌더 값 수집",
 "counts.py":"메뉴·화면·상태·엑셀 개수 실측 — 문서에 적는 개수의 단일 원천",
 "TODO_0831.md":"할 일 판 — 4차 미팅(2026-09-01) 대비",
 "alias_table.py":"기존 표기 → 바뀐 기호 대조표 — 원천은 final_terms.json 의 vars[].alias 한 곳",
 "ceo_definitions.sha256":"대표 정의 원문 잠금 해시 — ceo_definitions.md 변조 감지",
 "chrome_dl.js":"헤드리스 크롬 내려받기 차단 — 검증기가 다운로드 링크를 눌러도 사용자 폴더에 안 쌓이게",
 "exec_amount_structures.md":"투자실행액 구조 판정 — 정의서 산식 4개·구조 3개·실측 대조",
 "final_terms.json":"용어·기호 정리 원고 — 워드·HTML 두 생성기의 단일 원천",
 "frontend_settlement_cards.md":"어드민 선정산 결과 요약 카드 8개 — 프론트 코드 실사",
 "settlement_cards_measured.json":"선정산 결과 요약 카드 실측값 — 검증기가 읽는 기준 수치",
 "frontend_sync_20260831.md":"프론트 레포 최신화 기록 — 두 레포 HEAD·정산 로직 변경 여부",
 "notation_fix_app.md":"표기 교정 — 아래첨자·「만기」, build_app 계열",
 "notation_fix_glossary.md":"표기 교정 — 아래첨자·「만기」·Duration, 용어 계통",
 "notation_fix_xlsx.md":"표기 교정 — 아래첨자·「만기」·조어 약칭, 검산 엑셀",
 "questions_final_0831.md":"대표 확인 문항 통합본 — 3차 미팅(2026-08-31)",
 "questions_triage.md":"확인 문항 28건 — 누가 답하는가",
 "read_ceoq.py":"대표님 확인 문항 답 추출기 — 저장된 판에서 답만 뽑는다",
 "screen_vs_register_0831.md":"어드민 정산 현황 화면 대 정책 레지스터 대조",
 "subscript.py":"아래첨자 조판 한 곳 — 원고 마크다운 규약을 화면 표기로",
 "symbol_notation_audit.md":"기호 표기·조어 감사 — 읽기 전용, 파일 수정 0건",
 "testcase_table.py":"테스트 케이스 절 — 계산에 넣는 값 → 채권 한 건 풀이 → 하루 합계 → 조회기간 합계 → 화면 표시값 대조",
 "counts.json":"개수 실측값 — 생성기·동기화기가 읽는 기준 수치",
 "sync_counts.py":"개수 표기 동기화기 — 생성기 없는 문서의 개수를 실측으로 덮는다",
 "rescale_decision.md":"예시 데이터 규모 재설계 결정안 — 대표 실측 만기 도수·플랫폼 구성비 채택, 투자자산 1억·로스터 9곳·W 2.75일 재산출과 파급·적용처",
 "terms_briefing_0831.md":"대표 용어·산식 검증 브리핑 — 정산주기와 금융일수 구분, 정의서 1·2번 이미지와 기간 집계 산식 전 항목 원문 대조, 확인 문항 29건",
 "audit_xlsx_check.py":"검산 통합문서 독립 검증기 — 셀 수식을 직접 파싱·계산해 생성기와 코드를 공유하지 않고 값을 낸다",
 "build_audit_xlsx.py":"검산 통합문서 생성기 — 정산주기 실측 도수·구성비, 재설계 결정안 로스터, 대표 정의서 산식, 플랫폼 요율을 읽어 입력·플랫폼·가맹점·채권·일별·기간집계·화면대조·산식 8시트를 전부 엑셀 수식으로 조립. 채권 한 건의 금융일수는 2025년 365일 실측 수열의 연속 슬라이스이고, 미회수 Σ Ai 와 전체 가중평균 금융일수는 정수 해로 목표값에 맞춘다. 스위치 4개(W 모집단·표기 자릿수·가맹점 수·산출 방향)에 따라 화면 표시값이 갈린다",
 "검산_투자자어드민_20260901.xlsx":"검산 통합문서 — 채권 한 건에서 화면 표시값까지 중간 매개변수와 중간 산식을 전부 편 대조용. 값이 아니라 수식으로 들어가 있어 입력 시트를 바꾸면 아래가 따라 움직인다. 미팅 작업용이라 화면 다운로드 대상이 아니다",
}
def desc(fn):
    if fn in DESC: return DESC[fn]
    m=re.match(r'^([a-z-]+)--(.+)\.html$',fn)
    if m: return f"{DESC.get(m.group(1)+'.html','화면').split(' —')[0]} · 상태: {m.group(2)}"
    if fn.startswith("xls-"): return "엑셀 산출물 서식 — Figma 임포트 전용, 화면 흐름 진입점 아님"
    if fn.endswith(".xlsx"): return "엑셀 파일 — 다운로드 버튼 연결 대상"
    if fn.startswith("투자자산증명서_"): return "투자자산 증명서 견본 — certificate.html 의 PDF 다운로드 대상"
    if fn == "정산금채권_재양도_합의서.txt": return "계약서보기의 계약서 원문 열기 대상"
    if fn.endswith("_result.json"): return "검증 결과 — " + fn[:-12].replace("verify_", "") + " 실행 산출"
    if fn.startswith("verify_") and fn.endswith((".js", ".py")): return "검증기 — " + fn[7:-3].replace("_", " ")
    if fn.startswith("build_") and fn.endswith(".py"): return "생성기 — " + fn[6:-3].replace("_", " ")
    # 조각·원고는 짝이 되는 배포 낱장이 뜻을 들고 있다 — 여기서 두 벌로 적지 않는다.
    if fn.endswith(".fragment.html"):
        _s = fn[:-14].replace("_", "-") + ".html"
        return DESC.get(_s, "문서").split(" —")[0] + " — 아티팩트 게시용 조각"
    if fn.endswith("_seed.json"): return "원고 — " + fn[:-10].replace("_", " ") + " 생성기 입력"
    return ""
def scan(root, sub=""):
    d=os.path.join(root,sub); out=[]
    if not os.path.isdir(d): return out
    for fn in sorted(os.listdir(d)):
        p=os.path.join(d,fn)
        if fn.startswith(".") or os.path.isdir(p): continue
        st=os.stat(p)
        out.append({"fn":fn,"rel":(sub+"/" if sub else "")+fn,"abs":p,"size":st.st_size,
                    "mt":datetime.datetime.fromtimestamp(st.st_mtime).strftime("%m-%d %H:%M"),"desc":desc(fn)})
    return out
def kb(n): return f"{n/1024:.0f} KB" if n>=1024 else f"{n} B"
def rows(items, base):
    r=[]
    for i in items:
        fn=html.escape(i["fn"])
        if base is None or i["rel"] in NO_SERVE:
            cell=f'<span class="nl">{fn}</span>'
        else:
            cell=f'<a href="{(base+"/" if base else "")+html.escape(i["rel"])}" target="_blank">{fn}</a>'
        r.append(f'<tr><td class="fn">{cell}</td>'
                 f'<td class="ds">{html.escape(i["desc"])}</td><td class="sz">{kb(i["size"])}</td>'
                 f'<td class="mt">{i["mt"]}</td><td class="pa">{html.escape(i["abs"])}</td></tr>')
    return "\n".join(r)

import json as _j
_td=_j.load(open(os.path.join(PIPE,"todo.json")))
_SL={"done":("완료","#4da119","#f4fdf0"),"run":("진행중","#b45309","#fffbeb"),"wait":("대기","#6b7280","#f9fafb"),"ask":("결정 대기","#b91c1c","#fef2f2")}
_dn=sum(1 for t in _td if t["s"]=="done"); _rn=sum(1 for t in _td if t["s"]=="run")
_tr="".join(f'<tr class="td-{t["s"]}"><td class="no">{t["n"]}</td>'
  f'<td class="st"><span style="color:{_SL[t["s"]][1]};background:{_SL[t["s"]][2]}">{_SL[t["s"]][0]}</span></td>'
  f'<td class="tk">{html.escape(t["t"])}</td><td class="ou">{html.escape(t["o"])}</td></tr>' for t in _td)
TODO=(f'<section id="todo"><h2>작업 목록 <span class="cnt">{_dn}/{len(_td)} 완료</span></h2>'
 f'<div class="pbar"><i style="width:{_dn/len(_td)*100:.0f}%"></i></div>'
 f'<div class="tw"><table><thead><tr><th>#</th><th>상태</th><th>작업</th><th>산출</th></tr></thead>'
 f'<tbody>{_tr}</tbody></table></div></section>')

root=[f for f in scan(REPO) if f["fn"].endswith(".html")]
docs=[f for f in root if f["fn"] in ("index.html","app.html","glossary.html",
      "terms-edit.html","final-terms.html","calc.html","steps-all.html","ceo-questions.html",
      "capability.html","feasibility.html","inquiry.html","review.html","archive.html")]
xls =[f for f in root if f["fn"].startswith("xls-")]
scr =[f for f in root if f not in docs and f not in xls]
base_scr=[f for f in scr if "--" not in f["fn"]]; st_scr=[f for f in scr if "--" in f["fn"]]
assets=scan(REPO,"assets"); xlsx=scan(REPO,"assets/xlsx"); pdocs=scan(REPO,"assets/docs")
meta=[f for f in scan(REPO) if f["fn"].endswith(".md")]
pipe=scan(PIPE)
gitn=subprocess.run(["git","-C",REPO,"status","--porcelain"],capture_output=True,text=True).stdout.strip()
gitn=len([l for l in gitn.split("\n") if l.strip()])
now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
SEC=[("통합·설명 문서",docs,REPO_URL),("기본 화면",base_scr,REPO_URL),("상태 화면",st_scr,REPO_URL),
     ("엑셀 산출물 서식 화면 (Figma 전용)",xls,REPO_URL),("엑셀 파일",xlsx,REPO_URL),
     ("계약·증명 문서",pdocs,REPO_URL),
     ("공용 자산",[a for a in assets if a["fn"]!="xlsx"],REPO_URL),("레포 문서",meta,REPO_URL),
     ("원고·분석·검증 (파이프라인)",pipe,PIPE_URL)]
body="".join(
 f'<section><h2>{html.escape(t)} <span class="cnt">{len(it)}</span></h2>'
 f'<div class="tw"><table><thead><tr><th>파일</th><th>설명</th><th>크기</th><th>수정</th><th>절대경로</th></tr></thead>'
 f'<tbody>{rows(it,b)}</tbody></table></div></section>' for t,it,b in SEC if it)
# G-7 — 설명 공란 0건. 새 파일이 들어오면 DESC 에 한 줄을 더할 때까지 여기서 걸린다.
_blank=[i["fn"] for _t,_it,_b in SEC for i in _it if not i["desc"]]
assert not _blank, "설명 공란 %d건: %s" % (len(_blank), ", ".join(_blank))

DOC = f'''<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>투자자 어드민 — 작업물 아카이브</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap" rel="stylesheet">
<style>
:root{{--bg:#f7f8fa;--card:#fff;--ln:#e5e7eb;--tx:#111827;--sub:#6b7280;--pri:#4da119;--pri50:#f4fdf0}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--tx);font-family:'Noto Sans KR',-apple-system,sans-serif;font-size:13px;line-height:1.6}}
.wrap{{max-width:1400px;margin:0 auto;padding:32px 24px 64px}}
h1{{font-size:22px;margin:0}}.sub{{color:var(--sub);margin:4px 0 0}}
.bar{{display:flex;gap:20px;flex-wrap:wrap;background:var(--card);border:1px solid var(--ln);border-radius:10px;padding:14px 18px;margin:20px 0 8px}}
.bar b{{color:var(--pri)}}
.note{{background:var(--pri50);border:1px solid #cef4a7;border-radius:8px;padding:10px 14px;margin-bottom:24px;font-size:12px}}
section{{margin-bottom:28px}}h2{{font-size:15px;margin:0 0 8px;display:flex;align-items:center;gap:8px}}
.cnt{{background:var(--pri50);color:var(--pri);border-radius:20px;padding:1px 9px;font-size:11px;font-weight:700}}
.tw{{overflow-x:auto;background:var(--card);border:1px solid var(--ln);border-radius:10px}}
table{{width:100%;border-collapse:collapse;min-width:900px}}
th{{text-align:left;font-size:11px;color:var(--sub);font-weight:500;padding:9px 12px;border-bottom:1px solid var(--ln);background:#fafbfc}}
td{{padding:8px 12px;border-bottom:1px solid #f3f4f6;vertical-align:top}}tr:last-child td{{border-bottom:none}}
tr:hover td{{background:#fafdf8}}
.fn a{{color:var(--pri);text-decoration:none;font-weight:500;font-family:ui-monospace,Menlo,monospace;font-size:12px}}
.fn a:hover{{text-decoration:underline}}.ds{{color:#374151}}
.fn .nl{{color:#6b7280;font-weight:500;font-family:ui-monospace,Menlo,monospace;font-size:12px}}
.sz,.mt{{color:var(--sub);font-size:11px;white-space:nowrap;font-variant-numeric:tabular-nums}}
.pa{{color:#9ca3af;font-size:10px;font-family:ui-monospace,monospace;word-break:break-all}}
.no{{color:var(--sub);font-size:11px;width:28px}}
.st span{{font-size:10px;font-weight:700;border-radius:20px;padding:2px 9px;white-space:nowrap}}
.tk{{font-weight:500}}.ou{{color:var(--sub);font-size:11px;font-family:ui-monospace,monospace}}
.td-done .tk{{color:var(--sub);font-weight:400}}
.pbar{{height:6px;background:var(--ln);border-radius:20px;overflow:hidden;margin:0 0 10px}}
.pbar i{{display:block;height:100%;background:var(--pri);border-radius:20px}}
</style></head><body><div class="wrap">
<h1>투자자 어드민 — 작업물 아카이브</h1>
<p class="sub">갱신 {now}</p>
<div class="bar"><span>화면 <b>{len(base_scr)+len(st_scr)+len(xls)}</b></span><span>엑셀 <b>{len(xlsx)}</b></span><span>계약·증명 문서 <b>{len(pdocs)}</b></span>
<span>설명 문서 <b>{len(docs)}</b></span><span>원고·분석 <b>{len(pipe)}</b></span><span>미커밋 <b>{gitn}</b></span></div>
<div class="note">원고·분석(파이프라인)은 레포 밖이라 링크 없이 경로만 싣는다.
&nbsp;·&nbsp; 갱신 <code>python3 {PIPE}/build_archive.py</code></div>
{TODO}\n{body}</div></body></html>'''

# G-7 — 죽은 링크 0건. 판정 기준은 로컬 파일 존재가 아니라 배포에서 열리는가다.
#   ① 로컬 서버 주소  ② 디스크에 없음  ③ git 추적 밖(배포에 안 나감)  ④ 호스트가 안 내주는 파일
_href = re.findall(r'<a[^>]+href="([^"]+)"', DOC)
_dead = []
for h in _href:
    if h.startswith(("#", "mailto:")):
        continue
    if h.startswith(("http://", "https://")):
        if "localhost" in h or "127.0.0.1" in h:
            _dead.append(h + " (로컬 서버)")
        continue
    rel = h.split("#")[0].split("?")[0]
    if not os.path.exists(os.path.join(REPO, rel)):
        _dead.append(rel + " (디스크 없음)")
    elif rel not in TRACKED:
        _dead.append(rel + " (git 추적 밖 — 배포에 안 나간다)")
    elif rel in NO_SERVE:
        _dead.append(rel + " (호스트 미서빙)")
assert not _dead, "죽은 링크 %d건: %s" % (len(_dead), ", ".join(sorted(set(_dead))[:10]))

open(OUT, "w").write(DOC)
print(f"생성: {OUT}  (링크 {len(_href)}건 · 죽은 링크 0건)")
