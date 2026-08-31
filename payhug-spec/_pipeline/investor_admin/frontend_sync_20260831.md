# 프론트 레포 최신화 — 2026-08-31

두 레포 모두 `origin/develop` 에 detached HEAD 로 붙어 있다. 워킹트리는 최신화 전후 모두 깨끗했고, 쓰기 동작은 `git fetch --all --prune` 과 fast-forward pull 뿐이었다.

| 레포 | 최신화 전 HEAD | 최신화 후 HEAD | 새 커밋 수 | 워킹트리 상태 | 정산 로직 변경 |
|---|---|---|---|---|---|
| payhug-admin-web | `f79997b` | `4f58fd3` | 4 | 깨끗 (전·후 모두) | 없음 (신규 화면용 계산 모듈만 추가) |
| payhug-merchant-web | `3f74cd0` | `3f74cd0` | 0 | 깨끗 (전·후 모두) | 없음 |

- admin: `git pull --ff-only origin develop` 로 `f79997b..4f58fd3` fast-forward. 9개 파일 +1747 / −10.
- merchant: `origin/develop` 이 움직이지 않아 pull 불필요. 페치에서 갱신된 것은 미병합 feature 브랜치뿐이다.

## admin 신규 커밋 4건

| 커밋 | 제목 |
|---|---|
| `20a60ab` | feat: PAYHUG-225 모 계좌 화면 선정산 미리보기 (#17) |
| `e3a1a45` | fix: 바이패스 테스트 |
| `36259d1` | fix: 바이패스 |
| `4f58fd3` | fix: 바이패스 |

## 정산 현황 화면 — 변경 없음

`app/settlement/overview/` (page.tsx · PreSettlementTab · BatchDetailTab · TransferRecordsTab · TaxInvoiceTab · VocExportTab) 은 이번 4커밋에서 **단 한 파일도 바뀌지 않았다.**

산식이 들어 있는 파일도 그대로다.

| 파일 | 이번 범위 변경 | 마지막 변경 커밋 (이번 범위 밖) |
|---|---|---|
| `lib/settlementLedger.ts` | 없음 | `580423e` 정산 상세 엑셀 다운로드 개선 |
| `lib/settlementLabels.ts` | 없음 | `2da6b9d` 차액 조정 환급 분류·플랫폼 조정 상태 배지 정합 (#16) |
| `lib/platformSettlementConstants.ts` | 없음 | — |
| `lib/format.ts` | 없음 | — |
| `components/settlement/*` | 없음 | — |

**순지급액 · 선정산 대상액 · 선정산 수수료 · 선정산 지급액 · 선정산 제외액 — 다섯 값의 계산은 모두 그대로다.** 정산 현황 세 탭(선정산 결과 · 정산 상세 · 차액 정산)의 화면·산식 어느 쪽도 이번 최신화로 달라지지 않았다.

## 새로 붙은 것 — 정산 현황이 아닌 다른 화면

정산 현황을 건드리진 않았지만 선정산 금액을 다루는 코드가 두 군데 늘었다. 참고용으로 남긴다.

### 1. `20a60ab` — 모 계좌 화면(`/account-balance`) 선정산 미리보기

`app/account-balance/page.tsx` 는 정산 현황이 아니라 **모 계좌 잔액 화면**이다. 여기에 "선정산 미리보기" 카드가 붙었다.

신규 파일 `lib/payoutShortfall.ts` (61줄) — 계산은 뺄셈 한 번이다.

```
여유·부족 = 출금 가능액(wdrwCanAmt) − 예상 지급액(estimatedPayoutAmount)
```

- 0 이상이면 `예상 여유금액`(+), 음수면 `예상 부족금액`(−)
- 재원을 **총잔액이 아니라 출금 가능액**으로 잡았다. 출금 불가액은 실제로 이체할 수 없다는 이유
- 잔액과 예상액이 **같은 조회 세대(generation)** 에서 온 값일 때만 결합한다. 한쪽만 새로 오면 정산 전후 값이 섞여 이미 나간 돈을 다시 부족액으로 계산하게 되므로, 세대가 어긋나면 금액을 그리지 않고 `—` 로 둔다
- 테스트 `lib/payoutShortfall.test.ts` (135줄) 신설, `package.json` 에 `test` 스크립트(`tsx --test`)와 `tsx` devDependency 추가

`services/settlementService.ts` +35줄 — 순수 추가다. 기존 함수·타입은 손대지 않았다.

- 신규 타입 `PayoutEstimate`, 신규 함수 `fetchPayoutEstimate(targetDate?)` → `GET /admin/settlement/payout-estimate`
- 코드 주석이 명시하는 성격: **수집 데이터(UPL) 기반 읽기 전용 근사**이며 권위 산식은 서버(`SettlementAdminService.estimatePayout`)에 있다. 모계좌 자금 준비용, ADMIN/PAYHUG 전용

`PayoutEstimate` 필드 중 정책 대조에 걸리는 대목:

| 필드 | 주석이 밝힌 성격 |
|---|---|
| `estimatedMarginFee` · `estimatedSystemFee` · `estimatedTransferFee` | 지급액에서 실제 차감되는 금액. **수수료 면제 가맹점은 0으로 잡히는데 실제 정산은 면제여도 수수료 원장을 만들므로 정산 화면의 수수료 값과 다를 수 있다** |
| `estimatedSalesAmount` | 주말·장애일에 실제 정산이 넣는 평균매출 기반 금액. 지급액에 **이미 포함**돼 있다 |
| `feeAdjustmentAmount` | 미적용 차액의 반영 순액 (환급 +, 차감 −) |
| `debtRecoveryAmount` | 부채회수(상계, 이체 생략) 분 — 지급액에 **미포함** |
| `excludedTxCount` | 미활성/미승인/회수전용/카드사/플랫폼/룰미배정/순지급액 0 이하/가맹점 지급액 0 이하로 빠진 건수 합. 부채회수 가맹점 거래 건수는 `txCount` 에도 여기에도 없어 **둘의 합은 대상일 총 건수가 아니다** |
| `targetDate` / `settlementDate` | 정산은 T+1, `settlementDate` 11:30 실행. 화면 문구는 "매일 11:30 및 18:00" |

즉 이 미리보기의 수수료·건수는 정산 현황 화면 값과 **의도적으로 다를 수 있는 별도 근사값**이다. 정산 현황의 확정 산식으로 읽으면 안 된다.

### 2. `e3a1a45` · `36259d1` · `4f58fd3` — 바이패스 대상 조회 화면 신설

`app/settlement/bypass/page.tsx` (835줄) 신규. `components/AdminLayout.tsx` 좌측 메뉴에 `바이패스 대상 조회` 항목, `components/TabContent.tsx` 에 라우트 등록.

- 서버 응답을 그리기만 하는 조회 화면이다. 클라이언트 산식은 없다
- 응답에 `netPayoutAmt`(순지급액) 컬럼이 있으나 서버가 준 값을 표에 출력할 뿐이다
- `excludedByDirectPayout` — **바로이체 소관 건은 바이패스 집계에서 제외**한다고 화면에 명시
- 카드 매출은 `excludedSources`(제외 카드사) 목록을 별도 표기

## merchant 레포 — 미병합 브랜치

`origin/develop` 은 그대로지만, 페치로 아래 브랜치가 갱신·신설됐다. 아직 develop 에 들어오지 않아 이번 HEAD 에는 반영되지 않았다.

| 브랜치 | develop 대비 |
|---|---|
| `origin/feature/PAYHUG-226-ad-settlement-dates` (신규) | 1 커밋 앞섬 |
| `origin/feature/excluded-payout-delivery-manual-transfer` (갱신) | 6 커밋 앞섬 |

admin 쪽에도 같은 이름의 `feature/excluded-payout-delivery-manual-transfer` 를 포함해 미병합 브랜치 5개가 새로 보인다 (`feature/bm-adjustment-order-date-split`, `feature/bypass`, `feature/bypass2`, `feature/excluded-payout-delivery-manual-transfer`, `feature/pre-settlement-residual-reason`). 이름으로 보아 선정산 제외액·차액 정산에 닿을 작업이 진행 중이다.
