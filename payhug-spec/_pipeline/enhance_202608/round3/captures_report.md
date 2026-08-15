# round3 — 신규 추출 7장 캡처 리포트 (26.08.15)

regroup_plan ④ "신규 추출 7장"을 로컬 실행 사본(run-admin 3001 / run-merchant 3000, MOCK_API=1)에서
헤드리스 크롬(`--headless=new`, 창 미표시)으로 캡처 → `generate_figma_design` 네이티브 임포트.
**7/7 전량 성공.** 임포트 위치 = `IFX4GRC60ibOVCWNrd6VQt` 페이지 3783:890([정책] 정산) 직속,
**스테이징 영역 x=4967**(섹션 3783:906 x=-33 기준 +5000), y=-113부터 세로 스택(간격 200).

모든 URL은 임포트 전 헤드리스 DOM 마커 검증 통과(`discovery/verify_urls.sh` round3 블록 7건 추가, 덤프 = `discovery/dom/r3_n*.html`).

## 결과표

| 캡처 ID | URL·상태 | Figma 노드ID | 폭 | 특이사항 |
|---|---|---|---|---|
| CAP-N1 | `http://localhost:3001/settlement/overview?__devuser=PARTNER` — 총판 계정 정산 현황, 노출 탭 3종(선정산 결과·차액 정산·이체 내역)만. 내부 전용 3탭 비노출 DOM 확인 | **4106:2** (이름 `CAP_N1`) | 1574 (h 1257) | 하네스 불요. 1차 성공 |
| CAP-N2 | `http://localhost:3001/settlement/overview?__devuser=ADMIN&__open=missing` — 미정산 누락 배너 **펼침**: 액션 바(미리보기·바로이체·이미지급(기록만)) + 3단(가맹점 카드→날짜 묶음→건별 행, "해당일 정산완료 - 누락" 배지·입금예정 열 포함) | **4115:2** (이름 `CAP_N2`) | 1574 (h 3257) | 하네스 **추가**(`__open=missing`). 1차(4107:2, 뷰포트 1257)에서 3단이 클리핑 → **세로 3400 재캡처로 대체**, 1차분 삭제 |
| CAP-N3 | `http://localhost:3000/settlement/account/excluded?bizNo=1234567890&payoutId=5019&__devuser=1` — 가맹점 웹 선정산 제외액 내역: 안내 문구("매일 오전 11시 30분 정산이 완료된 후…") + 제외 거래 5행(카드 4·배민 1) | **4108:2** (이름 `CAP_N3`) | 1574 (h 1257) | 하네스 불요. 1차 성공. 제외 행 전부 프레임 내 확인 |
| CAP-N4 | `http://localhost:3001/settlements/12301/fee-adjustments?__devuser=ADMIN` — 고아 화면(주소 직접 입력): 통계 4카드(전체 건수·환급·추가 차감·순 차액) + '원래 선정산' 링크 열 | **4109:2** (이름 `CAP_N4`) | 1574 (h 1257) | id=12301은 devMockData fee-adjustments 목의 originalPayoutId 계열로 사전 확인. **사본 탭 셸(TabContent.tsx)에 이 라우트 매핑이 아예 없어 "페이지를 찾을 수 없습니다"가 뜸 → 캡처용 매핑을 사본에만 추가**(실서비스 탭 셸 미매핑 = 고아 화면 증거, 꺾쇠 문안에 활용 가능) |
| CAP-N5 | `http://localhost:3001/merchants/101/fee-adjustments?__devuser=ADMIN` — 가맹점(김성호떡볶이) 축 차액 이력: 상태 필터 + 통계 4카드(화면 재계산) | **4110:2** (이름 `CAP_N5`) | 1574 (h 1257) | 하네스 불요. 1차 성공 |
| CAP-N6 | `http://localhost:3001/settlement/overview?__devuser=ADMIN&__open=ledger` — 정산 상세 탭 + 첫 배치 자동 선택: 이해관계자 배분 요약 + 수수료 원장 상세(7열, 배분액 열 포함) 펼침 | **4116:2** (이름 `CAP_N6`) | 1574 (h 3457) | 하네스 **추가**(`__open=ledger` — 탭 시드 + 첫 배치 선택→배분·원장 조회). 1차(4111:2)에서 원장 상세(relY 1480)가 프레임(1257) 밖 → **세로 3600 재캡처로 대체**, 1차분 삭제 |
| CAP-N7 | `http://localhost:3001/settlement/simulation?__devuser=ADMIN&__run=1` — 정책 선택(1·2번 상품 시드) + 기본 거래 입력 + 시뮬레이션 자동 실행 결과: 정산 요약·건별 원장·이해관계자 배분 요약(재귀속 미적용) | **4112:2** (이름 `CAP_N7`) | 1574 (h 2458) | 하네스 **추가**(`__run=1` — regroup_plan "상태 시드 검토"의 채택안). 1차 성공, 이 페이지는 문서 흐름이라 전체 높이 캡처됨 |

## 스테이징 좌표 (페이지 3783:890 직속)

| 이름 | 노드ID | x | y | w×h |
|---|---|---|---|---|
| CAP_N1 | 4106:2 | 4967 | -113 | 1574×1257 |
| CAP_N2 | 4115:2 | 4967 | 1344 | 1574×3257 |
| CAP_N3 | 4108:2 | 4967 | 4801 | 1574×1257 |
| CAP_N4 | 4109:2 | 4967 | 6258 | 1574×1257 |
| CAP_N5 | 4110:2 | 4967 | 7715 | 1574×1257 |
| CAP_N6 | 4116:2 | 4967 | 9172 | 1574×3457 |
| CAP_N7 | 4112:2 | 4967 | 12829 | 1574×2458 |

- 폭은 캡처 표준 1574(capture_urls.md 규격). regroup_plan 슬롯의 "폭 1000/@0.6" 규격 맞춤(리스케일)은 조판 단계 몫 — 본 라운드는 이동·리네임 외 쓰기 안 함.
- 1차 캡처 중 클리핑으로 대체된 4107:2·4111:2(내 임포트)는 삭제함. 사용자 기존 노드는 일절 건드리지 않음.

## 실행 사본 수정 내역 (원본 레포 무변경, 쿼리 없으면 기존 동작 그대로)

run-admin:
1. `app/settlement/overview/PreSettlementTab.tsx` — `MissedSettlementsBanner`의 `expanded` 초기값을 `?__open=missing`으로 시드 (dashboard `__open=inquiry` 전례 패턴).
2. `app/settlement/overview/page.tsx` — `initialActiveTab()`에 `__open=ledger`→batch-detail 시드 + 배치 목록 로드 후 첫 배치 자동 선택 effect(`fetchPayouts`가 원장까지 연쇄 조회).
3. `app/settlement/simulation/page.tsx` — `?__run=1` 시 정책 2종 시드 + 시뮬레이션 1회 자동 실행(2-effect 패턴).
4. `components/TabContent.tsx` — `/settlements/{id}/fee-adjustments` 캡처용 탭 매핑 추가(위 N4 특이사항 참고 — 실서비스에는 이 매핑이 없음).

검증 스크립트: `discovery/verify_urls.sh` 말미 "round3" 블록(dump/check 7건). N4는 매핑 추가 전 1회 FAIL("페이지를 찾을 수 없습니다" + 홈 대시보드만 렌더) → 매핑 후 4마커 PASS.
