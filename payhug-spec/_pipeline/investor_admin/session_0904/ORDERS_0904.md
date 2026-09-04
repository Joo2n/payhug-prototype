# 지시 목록 — 2026-09-04 세션

사용자(이서준)가 이 세션에서 시킨 것 전량. 순서는 시킨 순. 상태는 추적 조가 산출물로 판정한다.

| # | 지시 (사용자 말) | 대상 | 산출물·판정 근거 | 상태 |
|---|---|---|---|---|
| A | UI 프론트에서 용어 수정할 게 있으면 수정 | 화면 라벨·툴팁·엑셀 머리글·증명서의 옛 표기(`S입금부족율`·`W금융일수`·`Ty수익율`·`PwD`·`PY_MR`·`실적치`·`d-20 ~ d-11`) → 확정 용어 | `payhug-investor-admin/*.html`·`assets/xlsx`·`assets/docs`·`_fig/` · `reports/step5_*` | |
| B | 프로토타입이랑 전체 페이지 깃도 안 교체됐다 → 배포 | 전체본 `Joo2n/payhug-investor-admin` main push(Vercel) · 시연본 `sync_prototype.sh`(변환·게이트·push) | 배포 주소 실물 확인 | |
| C | PY 등 툴팁의 기호마다 용어명·산식까지 쓰고 UI 배포된 것 모조리 수정 | ④⑤ 툴팁 12건 + 카드 툴팁 2건에 `PMR`·`PY_a`·`PA`·`PEC`·`EC` 용어명 | `reports/step6_tooltip_report.md` · 산출 16 HTML | |
| D | ⑤ 를 `Σ( A_i × D_i ) + PEC` 로 검증해 문제없으면 워드·HTML 확정본 | 기호정리표 아티팩트·워드·HTML + `final_terms.json` | `~/Downloads/payhug_용어정의서/1차 최종/투자자어드민 기호정리표_V1.0.docx/html` (사용자가 20260904_2155 판을 이 이름으로 통일) · 레포 사본 `session_0904/artifact/` · `reports/step6_doc_*`·`step7_notation_report.md` · 검증 3건 `verify/xv_*` | |
| E | 산식 검증·시뮬레이션·설명 아티팩트는 추후 할 수 있게 정리, 깃 저장 + 로컬 넥스트세션 md | `session_0904/` 폴더 · `NEXT_SESSION.md` · payhug 레포 커밋 | 파일 존재·커밋 | |
| F | UI 고칠 게 적으면 Figma 와 그것부터, 용어정의는 그 다음 | 작업 순서 | 보고 순서 | |
| G | 표기 통일 — `PD` 분모 `Σ A_i`, 개념 행(D·MR·A·M·B·L) 산식, `P` 와 `Σ` 를 한 규칙으로, `PY_t` 를 `Σ( A_i × D_i )` 꼴 | 기호정리표 3벌 + 원고 | `reports/step7_notation_report.md` | |
| H | 니 방식이 맞다 → 용어표·docs·UI 수정 진행 | ⑤ 산식 원장·화면·엑셀·검산 엑셀 교체 (2.32% → 3.30%), 배지 「미확정」 유지·「대표 확인 대기」 | `reports/step7_ty5_report.md` · `ledger_facts.json` · 화면·xlsx | |
| I | Figma 는 프로토타입 화면만. 화면 갤러리(index)·쿠콘 상세(coocon) 만들지 말라. 두 번 지웠는데 매번 생김 | `prep_fig.py` IMPORT · `figma_map_investor.json` · Figma 3066:328 에서 `3341:2` 삭제, 갤러리는 이미 없음 | Figma 직계 프레임 목록 | |
| J | 검증 에이전트 2개 교차검증 — Vercel 배포 실물 확인·지시대로 고쳤는지·Figma 는 말한 프레임만·용어 기호 정리 지시대로. QA·검증 병렬 | 배포 후 | 교차검증 보고 2건 | |
| K | 시뮬레이션 메뉴는 프로토타입(시연본)·Figma 에서 숨김, 통합본(나만 보는)에만 유지, 코드에서도 프로토타입은 지움 | `sync_prototype.py`·`gate_prototype.js` · Figma `3376:2`·`3378:2` 삭제 · IMPORT·맵 제외 | `reports/step7_sim_hide_report.md` · 시연본 index.html 에 `invest-sim` 0건 | |
| L | 엑셀은 다운로드 바로 되는데 미리보기 화면은 실물에 없다 → 남기지 말고 현행화 | 시연본에서 엑셀 미리보기 뷰 제거(다운로드 버튼은 실물 xlsx 유지) · Figma `3370:2`·`3372:2`·`3375:2`·`3377:2` 삭제 · IMPORT·맵 제외. 통합본·낱장은 시뮬과 같이 유지 | 시연본 index.html 에 `xls-` 뷰 0건 | |
| M | 로그인 화면이 기존 프론트와 다르면(「투자자 어드민」 등 붙인 것) UI 되돌리고 Figma 프레임 삭제 | 실물 `payhug-admin-web/app/login/page.tsx` 기준으로 `login.html`·통합본 로그인 카드 되돌림 · Figma `3371:2` 삭제 · IMPORT·맵 제외 | 대조 표 | |
| N | 여기까지 시킨 것 확인·리스트업·진행 추적 에이전트 | 이 파일 + proto-orders 중간·최종 판정 | `reports/orders_mid.md`·`orders_final.md` | |
| O | 완료되면 한 번에 답 | 최종 보고 | | |

## 손대지 않는 것 (사용자·프로젝트 규칙)
- 사이드바 메뉴 **라벨** (항목 제거는 K 로 시연본에서만)
- 대표 원문 인용 (`quote`·`<pre class="calc quote">`·`<q>`·「대표 DM」 행)
- `payhug-admin-web`·`payhug-merchant-web` 는 읽기만
- `payhug-io` 조직 저장소에 push 금지. 세 저장소 모두 `Joo2n` 개인
- 통합본(`app.html`)·낱장의 시뮬레이션·엑셀 미리보기는 유지 (통합본 전용)
