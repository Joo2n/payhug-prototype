# PayHug Prototype

페이허그 서비스 UI 프로토타입 모음. Claude Design에서 작업한 디자인을 GitHub Pages로 배포해 팀/외부에 공유합니다.

**라이브 URL:** https://joo2n.github.io/payhug-prototype/

---

## 화면 목록

### 1. 페이허그 앱 (기존)
**URL:** https://joo2n.github.io/payhug-prototype/ui_kits/payhug_app/

가맹점주 모바일 앱 — 미리 받는 돈(선정산)·매출 관리 흐름

| 화면 | 설명 |
|------|------|
| 메인 | 미리 받는 돈 금액 + 6월 총 매출 달력 카드 |
| 미리 받는 돈 | 카드·배달앱별 선정산 내역, 날짜 이동 |
| 총 매출액 | 날짜별 카드·배달앱 매출 브레이크다운 |
| 카드사 상세 | KB·농협·비씨 등 카드사별 건별 내역 |
| 배달앱 상세 | 배민·쿠팡이츠·요기요 차감액·주문 목록 |
| 단건 거래 | 카드 승인건 상세 (승인번호·수수료·미리받는돈) |
| 주문 상세 | 배달앱 단건 주문 상세 |
| 미매입 내역 | 카드사 매입 대기 중인 건 목록 |
| 선정산 제외액 | 이번 선정산에서 빠진 금액 상세 |
| 예상 지급 차액 | 실제 정산 후 발생한 차액 내역 |
| 계좌 입금 내역 | 하나은행 입금 타임라인 |

---

### 2. 캐시노트 통합 (Claude Design)
**URL:** https://joo2n.github.io/payhug-prototype/ui_kits/cashnote/

페이허그 앱 기반 + 매출관리 장부(매출/비용/수익 상세) 화면 추가

| 화면 | 설명 |
|------|------|
| 메인 | 미리 받는 돈 + 매출관리 달력 (매출/비용/수익 탭) |
| 미리 받는 돈 | (동일) |
| 총 매출액 | (동일) |
| **매출관리 상세** | 매출관리/미리받는돈 전환 드롭다운, 기간 선택(일·월·범위) |
| **총 비용** | 카드수수료·배달앱수수료·광고비 브레이크다운 |
| **수수료 상세** | 카드별/배달앱별 수수료 분배 내역 |
| **총 수익** | 매출 − 비용 = 수익 카드·배달앱 분리 표시 |
| 선정산 제외액 | (동일) |
| 미매입 내역 | (동일) |
| 계좌 입금 내역 | (동일, 하나은행 로고 포함) |

---

### 3. 매출관리 — 캐시노트 웹 (Claude Design, 최신)
**URL:** https://joo2n.github.io/payhug-prototype/ui_kits/sales_management/

`매출관리.dc.html` 마지막 버전. 캐시노트 매출관리를 반응형 웹 레이아웃으로 재구성 (PayHug 헤더 + 440px 카드 컬럼)

| 화면 | 설명 |
|------|------|
| 메인 | 잇잇 가맹점 + 미리 받는 돈 + 매출관리(매출/비용/수익 탭) 접이식 달력 |
| 총 매출액 | 날짜별 카드·배달앱 매출 브레이크다운 |
| 카드/배달앱 상세 | 카드사·배달앱별 건별 내역 |
| 단건 거래 / 주문 상세 | 카드 승인건 · 배달앱 주문 상세 |
| 미매입 내역 | 카드 매입 대기 건 목록 |
| 선정산 제외액 / 예상 지급 차액 | 제외 사유·차액 상세 |
| 계좌 입금 내역 | 하나은행 입금 타임라인 |

> 새 디자인 시스템 번들(`PayHugDesignSystem_81d4f2`) 사용 — `SalesBreakdown`, `Badge` 등

---

## 기술 스택

- **React 18** (CDN), **Babel Standalone** (JSX 인라인 변환)
- **디자인 시스템:** `_ds_bundle.js` (PayHugDesignSystem_2ffe20 네임스페이스)
- **디자인 토큰:** `tokens/colors.css`, `fonts.css`, `typography.css`, `spacing.css`
- **빌드 없음** — 정적 HTML 단일 파일, GitHub Pages 직접 서빙

---

## 레포 구조

```
payhug-prototype/
├── ui_kits/
│   ├── payhug_app/index.html     # 페이허그 앱 (전체 인라인)
│   ├── cashnote/index.html       # 캐시노트 통합 (전체 인라인)
│   └── sales_management/         # 매출관리 — 캐시노트 웹 (최신)
│       ├── index.html            # 앱 인라인 (text/babel)
│       ├── _ds_bundle.js         # DS 번들 (_81d4f2 네임스페이스)
│       ├── styles.css, tokens/   # 디자인 토큰
│       └── assets/bank-hana.png
├── assets/
│   ├── bank-hana.png             # 하나은행 로고
│   ├── avatar-default.png        # 기본 아바타
│   └── store-thumb.png           # 가게 썸네일
├── tokens/
│   ├── colors.css
│   ├── fonts.css
│   ├── typography.css
│   └── spacing.css
├── _ds_bundle.js                 # 디자인 시스템 컴포넌트 번들
├── styles.css                    # 토큰 임포트 진입점
├── index.html                    # 루트 → payhug_app 리다이렉트
└── .nojekyll                     # Jekyll 비활성화 (필수)
```

---

## 배포 방식

Claude Design MCP → 로컬 레포 → `git push` → GitHub Pages 자동 배포

**주의사항:**
- `.nojekyll` 없으면 `_ds_bundle.js` 404 발생
- `.jsx` 외부 로드 불가 → `<script type="text/babel">` 인라인 필수
- 이미지는 `render_preview` serve_url → `curl` 로 직접 다운로드

---

변경 이력은 커밋 메시지로 관리합니다 → `git log --oneline`
