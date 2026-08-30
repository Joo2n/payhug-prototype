# 착수 불가 3건 재판정

`feasibility.md` §4가 E등급(착수 불가)으로 잡았던 3건을 재판정한다. 조사는 `payhug-admin-web` 읽기뿐이고 그 레포는 무변경이다.

---

## 1. E-2 실측 — 미지급금 · 과지급금

### 1-1. 정의

| 용어 | 정의 |
|---|---|
| **미지급금** | 선정산으로 가맹점에 지급해야 하는데 아직 못 준 금액 |
| **과지급금** | 가맹점에 더 나간 금액 |

### 1-2. 미지급금 — **A (값이 그대로 있음)**

미정산 누락(Missed Settlements) 도메인이 그대로 이 값이다.

| 집계 단위 | 필드 | 파일:라인 |
|---|---|---|
| 전체 합 | `MissedSettlementsData.totalAmount` | `types/settlement.ts:651` |
| 가맹점별 합 | `MissedSettlementMerchant.totalNetPayoutAmt` | `types/settlement.ts:645` |
| 날짜별 합 | `MissedSettlementDateEntry.netPayoutAmt` | `types/settlement.ts:635` |
| 건별 | `MissedTransaction.netPayoutAmt` | `types/settlement.ts:624` |
| 조회 | `GET /admin/settlement/missed-settlements` | `hooks/useSettlementOverview.ts:349` |

**화면 라벨**

| 라벨 | 파일:라인 |
|---|---|
| `미지급 {금액}원` | `app/settlement/overview/PreSettlementTab.tsx:1269` |
| 엑셀 `미정산누락` 시트 헤더 `미지급액` | `app/settlement/overview/PreSettlementTab.tsx:385` |
| 배너 제목 `미정산 누락 추적` | `app/settlement/overview/PreSettlementTab.tsx:1180` |

**의미가 그것임을 못박는 근거** — 화면 배너가 정의문을 직접 달고 있다.

> `PreSettlementTab.tsx:1197` — "정산 배치가 완료된 날짜에 뒤늦게 도착하여 선정산 처리가 누락된 건입니다. 이틀 이상 지난 건은 선정산이 아니라 카드/배달 수수료만 제외한 순지급액 전액을 그대로 이체합니다."

해소 액션 버튼도 `바로이체`(`:1214`)·`이미지급(기록만)`(`:1221`) 두 갈래라 **아직 지급되지 않은 상태**임이 확인된다. 훅 쪽 에러 문구도 이 도메인을 "미지급"으로 부른다(`hooks/useSettlementOverview.ts:387`·`:407`).

**혼동 주의** — 같은 낱말의 다른 값이 하나 있다. 플랫폼 환급 상태 배지 `미지급`(`lib/settlementLabels.ts:68` `REFUND.NONE`)은 배민·쿠팡이츠 환급분이 아직 반영 안 된 **상태값**이지 금액이 아니다. 광고비 등 플랫폼 조정의 `outstandingAmount`(`types/settlement.ts:494`)도 엑셀 `플랫폼환급` 시트에서 `미지급액` 헤더를 쓰지만(`PreSettlementTab.tsx:367`) 같은 필드가 `플랫폼차감` 시트에서는 `미회수액`으로 나온다(`:349`). 선정산 본체의 미지급금과 다른 축이다.

### 1-3. 과지급금 — **B (계산 필요)**

`과지급`·`과지급금`·`초과지급`·`overpaid`·`overpayment` 문자열은 레포 전체 **0건**이다. 발생 원인 두 갈래가 각각 필드로 실재하고, 합산해야 이 값이 나온다.

| 갈래 | 필드 | 파일:라인 | 화면 라벨 |
|---|---|---|---|
| 선정산 후 취소 환수 | `AdjustmentCategory = "CANCEL_CLAWBACK"` | `types/settlement.ts:525` | `취소 환수` — `PreSettlementTab.tsx:108` |
| 〃 금액 | `AdjustmentCategorySummary.pendingAmount` (분류 필터 필요) | `types/settlement.ts:533` | 화면은 **건수만** 쓴다 — `app/settlement/overview/page.tsx:728` |
| 〃 일별 발생액 | `AdjustmentDailyTrend.clawbackAmt` | `types/settlement.ts:549` | `취소환수` — `app/settlement/overview/page.tsx:746` |
| 현장결제 중복 수령 | `offlinePendingTotal` | `hooks/usePurchaseLedger.ts:108` | `미회수(다음 배치)` — `app/sales/[bizNo]/page.tsx:729` |

생성 규칙은 수기 매출 입력 모달이 그대로 적어 둔다.

> `components/sales/ManualSalesModal.tsx:181` — "음수 금액은 매입취소로 처리되며, 정산 완료 건은 환수(CANCEL_CLAWBACK)가 생성됩니다."

현장결제 쪽도 화면 안내가 성격을 밝힌다 — "현장결제 미회수 {금액}원은 다음 정산 배치에서 회수 예정입니다"(`app/sales/[bizNo]/page.tsx:794`). 가맹점이 현금을 직접 받았는데 선정산도 나가 같은 돈이 두 번 나간 경우다.

**B로 두는 이유** — 두 갈래를 합치는 식이 없고, 취소 환수의 금액은 화면에 안 뜬다(건수만). 추정으로 A로 올리지 않는다.

### 1-4. ⚠ `미회수 이월(carryForward)`을 과지급금으로 쓰지 않는다

이름이 가까워 붙이기 쉬우나 다른 축이다.

| 필드 | 파일:라인 |
|---|---|
| `PreSettlementOverview.carryForwardTotal` | `types/settlement.ts:290` |
| `PreSettlementMerchant.carryForwardAmt` | `types/settlement.ts:390` |
| `carryForwardAmount` (배치 단위) | `hooks/useSettlementOverview.ts:69` |

> `app/settlements/[id]/fee-adjustments/page.tsx:239-241` — "미회수 이월: 당일 이체액으로 차액을 전부 회수하지 못해 다음 날로 이월된 금액"

`02_TERMS_AND_STATUS.md` §4가 `과지급`(발생 원인·최초 금액)과 `미회수금`(현재 남아 있는 회수 잔액)을 갈라 두었고, 이 필드는 **뒤쪽**이다. 과지급금 산정에 끌어다 쓰면 같은 돈을 두 번 세게 된다. CLAUDE.md 원칙 2의 6대 개념 분리는 이 지점에서 그대로 유지된다.

### 1-5. 6대 개념과 같은가 — **같다. 확정**

| 축 | `02_TERMS_AND_STATUS.md` | 대표 정의서 | 판정 |
|---|---|---|---|
| **미지급금** | §2 — "원래 가맹점에게 지급해야 했으나 실제 지급되지 않은 금액". 방향 = 페이허그 → 가맹점 | 선정산으로 가맹점에 지급해야 하는데 못 준 금액 | **같다** |
| **과지급** | §4 — "PayHug가 가맹점에게 실제 지급해야 할 금액보다 더 지급한 발생 금액" | 가맹점에 더 나간 금액 | **같다** |

**종전 서술을 정정한다.** `feasibility.md` §4·`value_lineage.md` §1-3·`glossary` 카드 29·30은 정의문이 없다는 이유로 산식 위치에서 방향을 **플랫폼 → 락계좌 입금 부족**으로 역산하고, 6대 개념과 다른 개념이라며 **제7의 축으로 격리**했다. 그 역산이 틀렸다. 격리는 해제하고 같은 개념으로 확정한다.

산식도 이 정의로 성립한다 — 투자자가 산 채권 중 가맹점에 아직 지급되지 않았거나 더 지급된 몫만큼 상환액·투자수익이 조정되는 구조다.

**계약 용어와의 매핑은 미확정 유지.** 재양도합의서의 `미정산금`·`과정산금`은 "정산주체(플랫폼)별 초과·부족 입금"이라 주체가 플랫폼이다. 근거 없이 잇지 않는다(CLAUDE.md 원칙 7).

### 1-6. 검색 범위 — 0건인 키워드

`payhug-admin-web` 전체(`node_modules`·`.next` 제외), `*.ts` `*.tsx` `*.js` `*.jsx` `*.json` `*.md` 대상.

- 영문 0건 — `unpaid` `unpaidAmt` `unpaidAmount` `UNPAID` `overpaid` `overpaidAmt` `OVERPAID` `overPay` `overpayment` `excess` `excessAmt` `arrears` `shortage` `deficit` `notPaid` `pendingPay` `unsettled` `overSettled` `HOLD`
- 한글 0건 — `미지급금` `과지급` `과지급금` `초과지급` `미상환` `미수금` `채권잔액` `과다`
- 상태 enum에 `UNPAID`·`OVERPAID` 없음 — `PreSettlementTxStatus`(`types/settlement.ts:450-456`)는 `PRE_SETTLED` `PENDING` `DIRECT_TRANSFER` `RECORD_ONLY` `DEDUCTED` `NOT_TARGET` 6종

---

## 2. 등급 재산정

### 2-1. 판정 변경 3건

| ID | 항목 | 종전 | 변경 | 근거 |
|---|---|---|---|---|
| **E-1** | 채권매입수수료의 기준금액·요율 | E 착수 불가 | **B 계산만 추가** | 요율은 계약별로 달라지는 파라미터다. 값이 DB `PolicyRate.rateBps`에서 내려오고 어드민 요율 설정에서 계약별로 정해진다(`app/settlement/policies/page.tsx:166`). 코드에 리터럴이 없는 것은 결함이 아니라 정상이고, 계약서 요율 칸 공란도 같은 이유다. 투자자 몫인지 통 전체인지는 요율 행의 `targetRole`로 이미 갈린다(`:108`·`:120`) |
| **E-2** | 미지급금 · 과지급금의 정의 | E 착수 불가 | **미지급금 A · 과지급금 B** | §1 |
| **E-3** | ⑥ 지표의 `③` | E 착수 불가 | **B 계산만 추가** | `marker_legend.md`가 스토리보드 캡처 2장의 번호 마커로 대응을 전건 복원했다. `③` = 일별표 `투자실행금`. 산식 `⑥ = (투자수익 ÷ 투자실행금) × 365 ÷ w금융일수`. ④와는 동명이의가 아니라 집계 단위 차이(기간 전체 / 하루치) |

### 2-2. 등급이 바뀐 판정 행 3건

| 구분 | 항목 | 종전 | 변경 |
|---|---|---|---|
| 용어 29 | 미지급금 | E | **A** |
| 용어 30 | 과지급금 | E | **B** |
| 용어 49 | ⑥ 일별 투자실행금액 대비 ty수익율 | E | **B** |

E-1은 그 자체로 등급을 받은 행이 아니라 다른 행의 선행이었다(`유동화투자자의 할인율` B · `채권매입수수료` A). 선행 칸의 `E-1` 참조를 걷어 냈다.

### 2-3. 분포

| 등급 | 종전 | 변경 | 용어 50 | 화면 14 | 상태 19 | 기능 35 | 산출물 6 |
|---|---|---|---|---|---|---|---|
| **A** | 38 | **39** | 10 | 2 | 12 | 15 | 0 |
| **B** | 35 | **37** | 25 | 1 | 2 | 9 | 0 |
| **C** | 35 | 35 | 10 | 9 | 4 | 7 | 5 |
| **D** | 11 | 11 | 4 | 1 | 1 | 4 | 1 |
| **E** | 3 | **0** | 0 | 0 | 0 | 0 | 0 |
| 확인불가 | 1 | 1 | 1 | 0 | 0 | 0 | 0 |
| 해당없음 | 1 | 1 | 0 | 1 | 0 | 0 | 0 |
| **합계** | 124 | 124 | 50 | 14 | 19 | 35 | 6 |

A+B = 76건(61%). **막는 것은 외부 의존 11건뿐이다.**

### 2-4. 미확정 유지

- **C1 수수료율** — 요율 값 자체는 채택하지 않는다. 화면 숫자는 `예시값` 표기를 유지한다. 값이 미확정인 것과 구현이 막히는 것은 별개다.
- **C2 지급 캘린더 · C4 예상 지급 차액** — 그대로 미확정.
- **6대 개념 분리** — 미지급금·과지급은 대표 정의와 같은 것으로 확정했으나, 나머지 넷과의 병합은 0건이고 `미회수금`(`carryForward*`)을 `과지급`에 붙이지 않는 구분도 유지한다.
- **계약 용어(`과정산금`·`미정산금`) 매핑** — 미확정.

---

## 3. 갱신 문서

### 3-1. 레포 `/Users/semi/cursor/payhug-investor-admin/`

| 파일 | 무엇 |
|---|---|
| `feasibility.html` | 결론 배너(`막는 것은 없다`) · E등급 칸 0건 · 등급 분포 막대·범례·칩 · 순서도에서 0층 E 밴드 제거 및 viewBox 690→548 · §4를 재판정 카드 3장으로 교체 · 판정 행 3건 등급 변경 · 선행 칸 E 참조 제거 · 착수 순서 6단계 재구성 |
| `glossary.html` | 카드 29·30 전면 교체(정의·출처 표·경고 방향 전환) · 출처 배지 `확인필요`→`기존 어드민에 있음` · 필터 칩·출처 표 집계(admin 7→9, check 3→1) · §2 못 만드는 것 표 · §6-2 이름 대조표 2행 · §7-4를 해소 3건으로 교체 · §8 Q-1·Q-2·Q-8을 닫힘으로 · `.ok-inline` 스타일 신설 |
| `inquiry.html` | 문항 7→4건(Q-1·Q-2·Q-4 제거, 나머지 재정렬) · 인사말·힌트·복사 `ORDER` 배열 · §2 꼬리말·N-2 행 · §6 축소 + §7 신설(사내 대조로 닫은 3건) · 평문 복사 블록 동기화 |
| `capability.html` | 6대 개념 주석 · 노출 주의 3번(S입금부족율) · §7-18 배경·영향·주의 — `제7의 축` 서술을 파생 지표로 정정 |
| `review.html` | 문의서 단계 노트·확인 항목 · 아직 열려 있는 것 노트 |
| `archive.html` | 생성기 재실행 산출 |

### 3-2. 파이프라인 `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/`

| 파일 | 무엇 |
|---|---|
| `feasibility.md` | HTML과 동일 범위 + §9 D-07 문항 현행화 · §10 6대 개념 항목 정정 |
| `glossary_manuscript.md` | 카드 미지급금·과지급금 전면 교체 · 못 만드는 것 표 · 이름 대조표 2행 |
| `ceo_inquiry.md` | 문항 7→4건 재정렬 · 인사말 · §2 꼬리말·N-2 행 · §6 축소 + §7 신설 · 회신 대응표 |
| `value_lineage.md` | §1-3 전면 교체(판정 `다른 개념`→`같은 개념`) · §3-4 착수 불가→해소 · 계층도 2곳 · 이름 충돌표 2행 · 요약표 2행 |
| `capability_manuscript.md` | 6대 개념 주석 · 노출 주의 3번 · §7-18 배경·영향·주의 |
| `verify_feasibility.js` | 기대 분포 `{A:39, B:37, C:35, D:11, U:1, N:1}` + E 0건 단언 추가 |
| `build_archive.py` | `inquiry`·`ceo_inquiry`·`feasibility` 설명 현행화 · `grade_revision.md` 등재 |
| `grade_revision.md` | 이 문서 |

**무접촉** — `payhug-admin-web`(읽기만) · `payhug-merchant-web` · Figma · `app.html` · 화면 HTML · 엑셀 · PDF. **숫자는 바꾸지 않았다.** 판정과 서술만 바뀐다.

---

## 4. 제거한 문의 문항

| 종전 | 제목 | 무엇으로 닫혔나 |
|---|---|---|
| **Q-1** | 정의서가 가리키는 이미지 2장을 받을 수 있습니까 | `marker_legend.md`의 번호 마커 대응표. 이미지 재송부 없이 산식 적용 가능하고, ④·⑥ 동명 문제도 집계 단위 차이로 해소 |
| **Q-2** | 0.11%가 할인율입니까 채권매입수수료율입니까, 채권매입수수료는 투자자 몫만입니까 | 요율은 계약별 파라미터로 어드민 요율 설정에서 읽어 온다. 투자자 몫 여부는 `targetRole`로 갈린다. 요율 **값**은 C1 미확정 유지 |
| **Q-4** | `미지급금`·`과지급금`의 정의문을 주실 수 있습니까 | §1 실측. 어드민에 이미 있는 개념이고 6대 개념과 같은 것 |

**제거 3건 · 남은 4건.** 번호를 재정렬했다.

| 새 번호 | 종전 | 제목 |
|---|---|---|
| Q-1 | Q-3 | 투자자산 대비 Ty수익율은 어느 값이 맞습니까 |
| Q-2 | Q-5 | 가맹점별 투자자산 표의 `비중` 열을 어떻게 합니까 |
| Q-3 | Q-6 | 조달이자형(연 12%) 산식 카드를 계속 둡니까 |
| Q-4 | Q-7 | 화면의 0.11% 표기를 `예시`에서 `예정`으로 올립니까 |

남은 4건은 전부 표기·선택 문제라 개발 착수를 막지 않는다. 닫힌 3건의 현행 구조는 부록 §7에 남겼다.

---

## 5. 재검증

창을 띄우지 않는다(`--headless=new`).

| 검증기 | 기준 | 실측 | 판정 |
|---|---|---|---|
| `verify_app.js` | 72 PASS / 0 FAIL · 죽은 컨트롤 0 · states 18 | PASS 72 · 죽은 컨트롤 0/검사 134 · 키보드 미도달 0 · 콘솔 0 · `states:18` `screens:14` `contracts:16` | 유지 |
| `verify_identity.js` | 14 PASS · 비중 합 100.0% · ⑤ 2.24% | 항등식 14건 · FAIL 0 · 콘솔 0 · `ratioSum:100` · `cardTyAsset:2.24` | 유지 |
| `verify_crossscreen.py` | 23건 일치 | 화면 간 정합 23건 · 불일치 0 | 유지 |
| `verify_links.py` | 200 · 바이트 일치 | 링크 실측 80건 · FAIL 0 · 전건 200 · 바이트 일치 (고유 58 / 참조 512) | 유지 |
| `verify_toast.js` | 실물 동반 | 전건 PASS · FAIL 0 · 콘솔 0. zip·PDF·xlsx 바이트 일치 | 유지 |
| `verify_feasibility.js` | 124건 · E 0건 | 124건 · `{A:39, B:37, C:35, D:11, U:1, N:1}` · 가로 오버플로 0(4폭) · 표 7개 전부 `.scroll` 안 · 개발문의 32 · 순서도 940×548 · 콘솔 0 · **판정 PASS** | 기대치 갱신 |

### 5-1. 숫자 불변 확인

화면 숫자는 하나도 바뀌지 않았다.

| 값 | 실측 |
|---|---|
| 가맹점별 투자금액 합 | 1,523,100,000 |
| 투자자산 | 1,628,400,000 |
| 비중 합 | 100.0% |
| 일별 투자수익 합(7일) | 1,375,880 |
| 월별 투자수익 합 | 35,307,250 |
| ⑤ 투자자산 대비 Ty수익율 | 2.24% |

### 5-2. 정적 무결성

| 파일 | div 열림/닫힘 | article | section | 중복 id |
|---|---|---|---|---|
| `glossary.html` | 1416 / 1416 | 50 / 50 | 8 / 8 | 0 |
| `capability.html` | 628 / 628 | 15 / 15 | 9 / 9 | 0 |
| `feasibility.html` | 140 / 140 | — | 7 / 7 | 0 |
| `inquiry.html` | 15 / 15 | — | 4 / 4 | 0 |
| `review.html` | 9 / 9 | — | — | 0 |

`inquiry.html` 복사 배열 `ORDER = ['intro','q1','q2','q3','q4']` 전건이 대응 `src-*` 블록을 갖고, `data-copy` 6개 전부 대상이 실재한다.

`glossary.html` 용어 카드 50건의 `data-src` 실집계 `{admin:9, design:3, new:36, check:1, track:1}`가 필터 칩 표기와 일치한다.

---

## 6. 배포 확인

### 6-1. 커밋

| 항목 | 값 |
|---|---|
| 레포 | `Joo2n/payhug-investor-admin` |
| 브랜치 | `main` |
| commit SHA | `5cfb51c86fc08ab6d83bcb9e479877dc8f1917ee` |
| 제목 | 착수 불가 0건 — 종전 E등급 3건 재판정 반영 |
| 규모 | 6파일 · +237 / −354 |
| `origin/main` | 같은 SHA — push 완료 |

파이프라인 원고(`payhug-spec/_pipeline/investor_admin/`)는 `payhug` 레포 워킹트리에 둔다. 그 레포는 다른 브랜치(`payhug-spec-deepdive-figma`)에서 무관한 작업이 진행 중이라 이번 커밋 범위에 넣지 않았다.

### 6-2. GitHub Pages

| 항목 | 값 |
|---|---|
| 빌드 상태 | `built` |
| 빌드 커밋 | `5cfb51c86fc08ab6d83bcb9e479877dc8f1917ee` — push한 SHA와 일치 |
| 완료 시각 | 2026-08-27T13:00:37Z |

### 6-3. 라이브 응답 — 캐시 버스터 부착 실측

`https://joo2n.github.io/payhug-investor-admin/<파일>?cb=<epoch>`

| 파일 | 응답 | 크기 | 로컬 대조 |
|---|---|---|---|
| `feasibility.html` | 200 | 114,129 B | 바이트 일치 |
| `glossary.html` | 200 | 278,312 B | 바이트 일치 |
| `inquiry.html` | 200 | 43,117 B | 바이트 일치 |
| `capability.html` | 200 | 166,359 B | 바이트 일치 |
| `review.html` | 200 | 14,598 B | 바이트 일치 |
| `archive.html` | 200 | 63,228 B | 바이트 일치 |
| `index.html` | 200 | 23,588 B | 바이트 일치 |

### 6-4. 라이브 본문 확인

| 확인 대상 | 실측 |
|---|---|
| `feasibility.html` 결론 | `막는 것은 없다` |
| 〃 E등급 칸 | `0건 · E등급` |
| 〃 등급 막대 | `A 39` · `B 37` |
| 〃 필터 칩 | `E 착수 불가 0` |
| `inquiry.html` 문항 | `Q-1.` `Q-2.` `Q-3.` `Q-4.` — 4건 |
| `glossary.html` 카드 29·30 | `data-src="admin"` (종전 `check`) |

### 6-5. 순서도 렌더

`feasibility.html` 순서도 SVG를 단독 추출해 헤드리스로 렌더했다. 0층 E 밴드가 빠지고 1층~5층·옆줄이 잘림 없이 들어간다. 좌표 실측 — 도형 y 범위 14~503, viewBox 높이 548.
