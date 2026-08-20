# 회원관리 상태 매트릭스 델타 라운드 v3 — 신규·변경 9상태 캡처·임포트 로그 (2026-08-20)

- 파일: Tcf69tIciGxmlqCIuRb0iI / 임포트 페이지: 2822:2294 ([정산_정책 백업])
- 소스: `~/cursor/payhug-member-redesign/v2.html` (커밋 8906a1c, 58상태) → `gen_proto_fig.js`로 `proto_fig/index.html` 재생성(capture.js 주입, 142KB)
- 서버: http://localhost:8902/index.html?state=<id> — 기존 프로세스(PID 46063, python3 http.server 8902, proto_fig) 재사용. 파일 md5 일치 확인.
- 방식: 캡처 전 9상태 전부 헤드리스(`--headless=new` + `--timeout` 강제 덤프)로 `STATE:<id>:READY` 타이틀 검증 → captureId 발급 → `figcap_state.sh` 헤드리스 제출(동시 4 청크) → 폴링. 브라우저 창 0회.

| state | url | captureId | node_id | w×h | 비고 |
|---|---|---|---|---|---|
| E5 | ?state=E5 | 34b9594c-3816-4655-ab8f-77be59338243 | 3001:2 | 1922×1918 | STATE:E5:READY |
| I1 | ?state=I1 | 2cc7b9a2-dd16-4a4e-a17b-51a99f49e8c8 | 3002:2 | 1922×1641 | STATE:I1:READY |
| I2 | ?state=I2 | 9698c9e1-81a5-4b48-9f4e-1fbd89040c83 | 3004:2 | 1922×1513 | STATE:I2:READY |
| I3 | ?state=I3 | 4a5f2100-d85c-4af4-bee4-4dcb375d0808 | 3005:2 | 1922×1513 | STATE:I3:READY |
| I4 | ?state=I4 | 76b6c4a2-39dc-45d4-8884-c474f3b44b78 | 3003:2 | 1922×1513 | STATE:I4:READY |
| I5 | ?state=I5 | 0facdf0b-9b00-469c-9796-25c1517d0756 | 3007:2 | 1922×1513 | STATE:I5:READY |
| I6 | ?state=I6 | 235fdc66-40a0-4054-ade0-c301d98ba8c7 | 3008:2 | 1922×1626 | STATE:I6:READY |
| D6 | ?state=D6 | 02414989-b1f8-43bf-96a6-e74b19f2ffda | 3010:2 | 1922×1627 | 재발급분. 초기 9934cae7-57af-4410-8cf6-96af24921d6e 폴링 15회(약 14분) processing 정체 → 폐기·재캡처(재발급 후 2폴 완료). 폐기분 지연 완료 여부는 검증 단계에서 확인·정리 |
| D7 | ?state=D7 | 4938afe2-9241-4bd3-99b0-1916cf125d38 | 3006:2 | 1922×1627 | STATE:D7:READY |

## 결과 요약
- 9/9 성공. 실패 0, 재시도 1(D6 — captureId 재발급 1회, 위 표 비고).
- 전 프레임 폭 1922. D6·D7 신판 높이 1627(배지 변경 반영), 구판(2961:2/2962:2)은 1535 — 매트릭스 반영 단계에서 교체.
- 노드ID 3001:2~3008:2 + 3010:2 (3009 결번 — D6 폐기 captureId 몫). 프레임명 STATE:<id>:READY 전수 일치.
- 배치: 보관 페이지 2822:2294, x=33107~48803, y=0, 40px 간격 가로 나열. 이동·조립은 2단계(assembly_v3) 몫.
- 맵: `state_import_map_v3.json` (9건 — id/node_id/width/height/page/x/y).
