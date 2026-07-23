# PayHug 화면설계·기능명세·IA 진행 상태

> **이어쓰기 문서.** 다음 세션은 이 파일만 보면 이어서 진행 가능. (worktree = `~/cursor/payhug` 전용)
> 최종 업데이트: **2026-07-23**

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
