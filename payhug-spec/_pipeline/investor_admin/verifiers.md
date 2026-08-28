# 검증기 명부

전부 `_pipeline/investor_admin/` 에서 실행. 대상 저장소는 각 파일 머리말에 적혀 있다.

| 검증기 | 대상 | 보는 것 |
|---|---|---|
| `verify_0828.py` | `payhug-investor-admin` 정적 HTML | 8/28 미팅 결론 26항목 |
| `verify_app.js` | `payhug-investor-admin/app.html` | 죽은 컨트롤·상태 도달·레이아웃·콘솔 |
| `verify_proto.js` | `payhug-investor-prototype/index.html` | 시연본 전건 — 메뉴·상태·다운로드 실물·바깥 통로 |
| `verify_sync_chain.js` | 원본 ↔ 시연본 | 변환 손실 |
| `verify_rows.js` | 표 | 행·순번·선택 |
| `verify_toast.js` | 다운로드 | 토스트 문구 ↔ 실물 바이트 |
| `verify_links.py` | 링크·자산 | 전건 200 |
| `verify_crossscreen.py` | 화면 간 | 숫자 일치 |
| `verify_identity.js` | 산식 | 항등식 |
| `verify_period.js` | 기간 필터 | 기간·집계 단위 조작 |
| `verify_password.js` | 비밀번호 화면 | 실물 대조 |
| `verify_sim.js` | 투자 시뮬레이션 | 입력 → 산출 |
| `verify_glossary.js` | 용어 해설 | 앵커 도달·가로 넘침·본문 링크 대상·기호 검색·목차 |
| `verify_glossary5.js` | 용어 카드 | 5필드·캡처 마커·라이트박스·구버전 링크(전 HTML) |
| `verify_shotmarks.py` | 캡처 | 마커 |
| `verify_feasibility.js` | 구현 가능성 문서 | 근거 인용 |
| `verify_deployed.py` | 배포 3주소 | 익명 수신 바이트로 표식 대조 |
| `gate_prototype.js` · `gate_glossary.js` | 배포 게이트 | push 전 차단 |
| `sync_counts.py --check` | 문서 개수 표기 | `counts.py` 실측 ↔ 손으로 쓰는 문서 + `README.md` 재생성분(어긋나면 종료코드 1) |
| `sync_profit_static.py` | 투자 수익 낱장 5종 | 검색 카드·표를 다시 찍고 카드↔표 기간 일치를 assert |
| `build_readme.py --check` | `README.md` | 개수·화면 목록이 실측과 같은지 (`sync_counts.py --check` 가 함께 돈다) |

## 폐지

| 검증기 | 폐지일 | 사유 |
|---|---|---|
| `verify_demo.js` (+ `verify_demo_result.json`) | 2026-08-28 | 대상 파일 `payhug-investor-admin/demo/index.html` 이 없다. 시연본이 `payhug-investor-prototype` 저장소로 분리되면서 `demo/` 자체가 사라져 실행 자체가 불가. 역할은 `verify_proto.js`(시연본 전건)와 `verify_sync_chain.js`(원본 ↔ 시연본 변환 손실)가 이미 대신한다 — 검사 공백 없음 |
