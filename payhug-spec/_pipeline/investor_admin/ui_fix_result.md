# 투자자 어드민 UI 정정 결과

대상 파일 — `/Users/semi/cursor/payhug-investor-admin/assets/base.css` · `/Users/semi/cursor/payhug-investor-admin/DESIGN_REF.md` 2건.
지시서 `ui_fidelity.md` §5 우선순위 목록 기준. 화면 HTML·`assets/docs/`·빌드 스크립트는 타 조 작업 범위라 미변경(§4에 지시서로 분리).
커밋·푸시 없음. `payhug-admin-web`은 읽기 전용 참조(`node_modules/tailwindcss/theme.css` · 컴포넌트 소스).

| 항목 | 값 |
|---|---|
| 작업 시각 | 2026-08-27 17:55 ~ 18:35 KST |
| 색 판정 | Tailwind v4 `oklch()` → sRGB 변환(채널 클리핑) 후 CIEDE2000 |
| 변환 검증 | `ui_fidelity.md`가 headless Chrome 페인트로 실측한 sRGB 29건과 **전건 바이트 일치** — 변환기 신뢰 확보 |
| 판정 기준 | 일치 ΔE<0.5 · 근사 ΔE<1.5 · 불일치 ΔE≥1.5 (`ui_fidelity.md` §0 계승) |
| `base.css` | 588행 → 597행, 실변경 69행 |
| `DESIGN_REF.md` | 187행 → 203행, 실변경 76행 |

---

## §1 시맨틱 팔레트 정정

### 1-1. 근거

`payhug-admin-web/node_modules/tailwindcss/theme.css`(4.2.1)의 `--color-*` `oklch()` 정의가 원본 팔레트의 유일한 출처다.
`DESIGN_REF`가 "원본은 v4 oklch, 아래는 동치 hex"라 적은 표는 실제로 **Tailwind v3 hex**이며 v4와 동치가 아니다.
v4는 팔레트를 oklch 기준으로 다시 뽑아 무채색은 미세 이동, 채도 계열은 순색 방향으로 크게 이동한다.

Chrome은 sRGB 색역을 벗어나는 oklch를 채널 클리핑으로 페인트한다. CSS Color 4 색역 매핑(크로마 축소) 결과와는
29건 중 13건이 어긋나며, 실측값과 일치하는 쪽은 **클리핑**이다. 본 정정은 클리핑 결과를 채택한다.

### 1-2. 토큰별 전/후

24건 정정 · 7건 신설 · 13건 유지. 전 44건.

| 토큰 | 전 | 후 | ΔE 전 | ΔE 후 | 처리 |
|---|---|---|---|---|---|
| `--emerald-300` | (신설) | #5ee9b5 | — | 0.00 | 신설 |
| `--red-400` | (신설) | #ff6467 | — | 0.00 | 신설 |
| `--red-800` | (신설) | #9f0712 | — | 0.00 | 신설 |
| `--amber-500` | (신설) | #fe9a00 | — | 0.00 | 신설 |
| `--amber-800` | (신설) | #973c00 | — | 0.00 | 신설 |
| `--violet-50` | (신설) | #f5f3ff | — | 0.00 | 신설 |
| `--violet-200` | (신설) | #ddd6ff | — | 0.00 | 신설 |
| `--red-600` | #dc2626 | #e7000b | 3.86 | 0.00 | 정정 |
| `--red-700` | #b91c1c | #c10007 | 3.29 | 0.00 | 정정 |
| `--amber-600` | #d97706 | #e17100 | 3.02 | 0.00 | 정정 |
| `--red-500` | #ef4444 | #fb2c36 | 2.81 | 0.00 | 정정 |
| `--blue-700` | #1d4ed8 | #1447e6 | 2.64 | 0.00 | 정정 |
| `--violet-700` | #6d28d9 | #7008e7 | 2.57 | 0.00 | 정정 |
| `--amber-400` | #fbbf24 | #ffb900 | 2.55 | 0.00 | 정정 |
| `--green-500` | #22c55e | #00c950 | 2.38 | 0.00 | 정정 |
| `--amber-700` | #b45309 | #bb4d00 | 2.29 | 0.00 | 정정 |
| `--emerald-600` | #059669 | #009966 | 1.65 | 0.00 | 정정 |
| `--emerald-500` | #10b981 | #00bc7d | 1.57 | 0.00 | 정정 |
| `--green-800` | #166534 | #016630 | 1.43 | 0.00 | 정정 |
| `--emerald-700` | #047857 | #007a55 | 1.28 | 0.00 | 정정 |
| `--gray-400` | #9ca3af | #99a1af | 1.07 | 0.00 | 정정 |
| `--gray-800` | #1f2937 | #1e2939 | 1.00 | 0.00 | 정정 |
| `--teal-700` | #0f766e | #00786f | 0.92 | 0.00 | 정정 |
| `--gray-600` | #4b5563 | #4a5565 | 0.90 | 0.00 | 정정 |
| `--gray-700` | #374151 | #364153 | 0.89 | 0.00 | 정정 |
| `--gray-500` | #6b7280 | #6a7282 | 0.87 | 0.00 | 정정 |
| `--amber-200` | #fde68a | #fee685 | 0.78 | 0.00 | 정정 |
| `--emerald-800` | #065f46 | #006045 | 0.75 | 0.00 | 정정 |
| `--emerald-200` | #a7f3d0 | #a4f4cf | 0.69 | 0.00 | 정정 |
| `--gray-900` | #111827 | #101828 | 0.52 | 0.00 | 정정 |
| `--gray-300` | #d1d5db | #d1d5dc | 0.50 | 0.00 | 정정 |
| `--red-200` | #fecaca | #fecaca | 0.48 | 0.48 | 유지 |
| `--red-100` | #fee2e2 | #fee2e2 | 0.32 | 0.32 | 유지 |
| `--amber-100` | #fef3c7 | #fef3c7 | 0.26 | 0.26 | 유지 |
| `--emerald-100` | #d1fae5 | #d1fae5 | 0.24 | 0.24 | 유지 |
| `--gray-50` | #f9fafb | #f9fafb | 0.00 | 0.00 | 유지 |
| `--gray-100` | #f3f4f6 | #f3f4f6 | 0.00 | 0.00 | 유지 |
| `--gray-200` | #e5e7eb | #e5e7eb | 0.00 | 0.00 | 유지 |
| `--emerald-50` | #ecfdf5 | #ecfdf5 | 0.00 | 0.00 | 유지 |
| `--red-50` | #fef2f2 | #fef2f2 | 0.00 | 0.00 | 유지 |
| `--amber-50` | #fffbeb | #fffbeb | 0.00 | 0.00 | 유지 |
| `--blue-100` | #dbeafe | #dbeafe | 0.00 | 0.00 | 유지 |
| `--violet-100` | #ede9fe | #ede9fe | 0.00 | 0.00 | 유지 |
| `--green-100` | #dcfce7 | #dcfce7 | 0.00 | 0.00 | 유지 |

### 1-3. 유지 판정 4건

`--red-100`(0.32) · `--red-200`(0.48) · `--amber-100`(0.26) · `--emerald-100`(0.24)은 v3·v4 차이가
판정표의 **일치 구간(ΔE<0.5)** 안에 들어 v3 값을 유지한다. 나머지 9건(`--gray-50/100/200`, `--emerald-50`,
`--red-50`, `--amber-50`, `--blue-100`, `--violet-100`, `--green-100`)은 v3·v4 값이 바이트 단위로 같다.
유지 사유는 `base.css` `:root` 주석과 `DESIGN_REF` §1에 명기.

### 1-4. 신설 7건

`ui_fidelity.md` §5 P1 #4'·#4''의 토큰 미경유 hex를 토큰 경유로 바꾸는 데 필요한 토큰.

| 토큰 | 값 | 신설 사유 |
|---|---|---|
| `--red-400` | `#ff6467` | 원본 툴팁 앵커 점선이 `border-red-400`(`PreSettlementTab.tsx:713`). 재현본이 `--red-500`으로 대체 중이라 단계 자체가 어긋남 |
| `--red-800` | `#9f0712` | error 토스트 텍스트(`Toast.tsx:29-33` red-100/500/800) — `base.css:493` 원시 hex |
| `--amber-500` | `#fe9a00` | warning 모달 아이콘(`ConfirmDialog` amber-50/500) — `:518` 원시 hex |
| `--amber-800` | `#973c00` | amber 지표 카드 값 — `:224` 원시 hex |
| `--emerald-300` | `#5ee9b5` | 툴팁 안내문(`PreSettlementTab:756 text-emerald-300`) — `:480` 원시 hex |
| `--violet-50` | `#f5f3ff` | 대기 안내 배너 배경 — `:578` 원시 hex |
| `--violet-200` | `#ddd6ff` | 대기 안내 배너 보더 — `:578` 원시 hex |

### 1-5. 브랜드 토큰

`--primary` 10단계 · `--secondary` · `--navy` 계열 · `--sidebar-bg #1B2537`은 `globals.css` 원문과 문자 단위 동일해 미변경.

---

## §2 시급 4건 처리

| # | 위치 | 전 | 후 | 근거 |
|---|---|---|---|---|
| 1 | `base.css:388` `.toggle-btn.active` | `box-shadow: 0 1px 2px 0 rgba(0,0,0,0.05)` | `0 1px 3px 0 rgba(0,0,0,0.1), 0 1px 2px -1px rgba(0,0,0,0.1)` | `theme.css:408` `--shadow-sm`. 종전 값은 v4 `--shadow-xs`(:407) |
| 2 | `:229` `.summary-card.amber .summary-value` | `#92400e` | `var(--amber-800)` `#973c00` | 토큰 경유 + v4 정렬 (ΔE 1.79) |
| 2 | `:487` `.tip-panel .tip-green` | `#6ee7b7` | `var(--emerald-300)` `#5ee9b5` | ΔE 1.47 |
| 2 | `:500` `.toast-error` color | `#991b1b` | `var(--red-800)` `#9f0712` | ΔE 2.03 |
| 2 | `:525` `.modal-icon.warning` color | `#f59e0b` | `var(--amber-500)` `#fe9a00` | ΔE 2.92 |
| 2 | `:585` `.notice-violet` | `#f5f3ff` / `#ddd6fe` | `var(--violet-50)` / `var(--violet-200)` `#ddd6ff` | violet-50 ΔE 0.00 · violet-200 ΔE 0.28 |
| 3 | `:471` `.tooltip .tip-anchor.red` | `border-bottom-color: var(--red-500)` | `var(--red-400)` | 원본 `PreSettlementTab.tsx:713 border-red-400` |
| 4 | `:445-446` `.formula-term .t-label` | `line-height: 15px` | `16.5px` | 원본 `text-[11px]`은 line-height 미지정 → html 1.5 상속 |
| 4 | `:473-477` `.tooltip .tip-panel` | `line-height: 15px` | `16.5px` | 동일 |

`base.css` 본문(`:root` 밖)에 남은 원시 hex는 `#171717`(foreground) · 스크롤바 3색(`#f1f5f9`·`#cbd5e1`·`#94a3b8`)뿐이며
모두 `globals.css`와 문자 단위 동일. 그 외 팔레트 hex는 0건.

---

## §3 잔여 항목 판정

`ui_fidelity.md` §2-3 D1~D21 · §5 P2 #6~#15 전건.

### 3-1. 고침 (7건)

| 항목 | 위치 | 전 → 후 | 근거 |
|---|---|---|---|
| D12 / P2 #8 필터 탭 카운트 | `:401` `.filter-tab .count` | line-height 상속(20px) → `16px` | 원본 `text-xs` 고정 16px |
| D10 / P2 #15 산식 연산자 | `:460` `.formula-op` | line-height 27px → `28px` | 원본 `text-lg` 28px |
| D11 / P2 #14 모달 라벨 | `:553` `.modal-body label` | line-height 21px → `20px` | 원본 `text-sm` 20px |
| D14 / P2 #11 표 헤더 자간 | `:249` `.tbl th` → `:280` `.tbl.wide th` | `letter-spacing:.05em` 상시 → 넓은 표 전용 | 원본은 `manage:265`만 `tracking-wider`, `PreSettlementTab:669`에는 없음 |
| D15 / P2 #12 인풋 본문색 | `:354` `.input` · `:368` `.search-input` | `var(--gray-900)` / 미지정(→`#000`) → 양쪽 `inherit` | 원본 preflight `color:inherit` + `--foreground #171717`. computed 실측 `rgb(23,23,23)` 확인 |
| D17 / P2 #13 모달 blur | `:511` `.modal-backdrop.blur` | `blur(4px)` → `blur(8px)` | v4 `--blur-sm` 8px(`theme.css:477`). 사용 화면 0건이라 렌더 영향 없음 |
| P3 #26 `.tbl.wide` 미사용 | `:278-281` | 주석에 미사용 사실·부착 규칙 명기 | 넓은 표 신규 작성 시 규격 분기 방지 |

### 3-2. 안 고침 (7건)

| 항목 | 사유 |
|---|---|
| D13 / P2 #10 `.filter-tab.active` 보더 | 원본은 활성 탭 보더를 빼 활성·비활성 폭이 2px 어긋난다. 재현본은 보더를 유지해 탭 크기가 고정된다. 어느 쪽이 옳은지 판단이 갈려 미변경 — 의도적 이탈로 `DESIGN_REF` §16에 등재 |
| D19 폰트 스택 | 원본에만 있는 `Noto Sans KR Fallback`은 next/font가 생성하는 메트릭 오버라이드다. 목업에서 재생성 불가하며 로드 후 렌더 결과는 동일(한글 실폭 양쪽 766.0px). `DESIGN_REF` §2에 사실만 등재 |
| D21 / P3 #17 `.badge.sm` | 원본에 2종 병존 — `manage:299`(700 · blue-50/blue-600), `PreSettlementTab:698`(500 · cyan-50/cyan-700). 어느 쪽이 표준인지 미확정이라 재현본 단일 규격 유지. 2종 모두 `DESIGN_REF` §7에 병기 |
| D20 상단 탭바 | 재현 여부 결정 대기 사안(§4-3). 구현 없이 `DESIGN_REF` §3·§16에 사실만 등재 |
| D18 body 배경 | 원본은 레이아웃 루트가 gray-50을 덮어 실효 결과가 같다. 변경 시 오히려 차이 발생 |
| `tabular-nums` 병용 | 모노스페이스에서 자릿폭 영향이 없어 렌더 동일. `DESIGN_REF` §16에 의도적 이탈로 등재 |
| 화면 인라인 규격 이탈 | `base.css` 밖의 화면 HTML 사안이라 §4 지시서로 분리 |

### 3-3. 판정 요약

`ui_fidelity.md`가 든 불일치 14건 중 팔레트 전이분(D2·D3·D4·D6·D7·D8)은 §1에서, 규격분(D1·D9·D12·D16·D17)은 §2·§3-1에서 해소.
남은 D13·D18·D19·D20·D21은 전부 결정 대기 또는 실효 동일 사유로 유지.

---

## §4 화면 HTML 지시서 (타 조 파일)

`base.css` 정정만으로는 닿지 않는 항목. **본 작업에서 미변경**이며, 배선 작업 조가 판단·적용할 대상.

### 4-1. 규격 정렬 — 적용 권고

| # | 대상 | 현재 | 권고 | 사유 |
|---|---|---|---|---|
| H1 | `acquisition.html` · `acquisition--confirm.html` · `acquisition--done.html` · `acquisition--signing.html` 각 1건 | `style="padding:16px 24px; border-bottom:1px solid var(--gray-100)"` | `class="modal-header"` 사용 | `.modal-header`가 이미 동일 규격. 클래스 미사용 상태라 규격이 두 곳에서 관리됨 |
| H2 | `password--weak.html` 1건 · `index.html` 3건 | `border-radius:10px` | `8px` 또는 `12px` | 어드민 radius 계단(4/6/8/12/16)에 10px 없음 |
| H3 | `invest-profit.html` · `invest-profit--monthly.html` · `invest-profit--empty.html` · `invest-profit--datepicker.html` 각 1건 | `font-size:16px; line-height:28px; font-weight:700` | `16px/24px`(text-base) 또는 `18px/28px`(text-lg) | 16/28은 두 격자의 혼합. `.modal-title`이 16/24, `.modal-header h3`가 18/28 |

### 4-2. 규격 승격 판단 — 결정 필요

| # | 대상 | 현재 | 선택지 |
|---|---|---|---|
| H4 | `acquisition*.html` 4건 대형 CTA | `padding:12px 40px; font-size:16px; border-radius:12px` | (가) 투자자 화면 전용 규격으로 확정하고 `.btn-lg`로 `base.css` 승격 (나) 어드민 primary 규격(8/20 · 14/600 · r8)으로 축소 |
| H5 | `login.html` · `password*.html` 4건 폼 제출 버튼 | `width:100%; padding:12px 0; border-radius:12px` | (가) `.btn-block`으로 승격 (나) 모달 풋터 규격(10px 0 · r12)에 맞춤 |

승격 결정 시 `base.css`에 클래스를 추가하는 작업은 본 조로 넘길 것.

### 4-3. 결정 대기 — 구현 금지

| # | 사안 | 내용 |
|---|---|---|
| H6 | 상단 40px 탭바 | 원본은 `TabContext.tsx:89 isTabMode:true` · `AdminLayout.tsx:585 <TabBar/>`로 탭바를 제공한다. 단 `TabBar.tsx:8`이 `tabs.length <= 1`이면 `null`을 반환하므로 **탭이 2개 이상 열렸을 때만** 40px 크롬이 붙는다(`ui_fidelity.md` §1-9의 "상시 렌더" 서술은 이 조건을 누락). 투자자 어드민에 다중 탭 작업 개념이 필요한지 미결 — 결론 전까지 미구현 |

### 4-4. 저위험 — 선택 적용

| # | 대상 | 내용 |
|---|---|---|
| H7 | `archive.html` 11건 · `capability.html` 1건 | v3 팔레트 원시 hex(`#6b7280`·`#b45309`·`#111827`·`#374151`·`#9ca3af`·`#b91c1c`·`#ddd6fe`)가 남아 v4로 정렬된 화면과 색이 갈린다. 배포 화면이 아닌 메타 문서라 결함 취급은 하지 않되, 손댈 때 `var(--*)`로 전환 권고 |

화면 산출물(`app.html` 포함 배포 대상 전량)의 v3 팔레트 원시 hex는 **0건** — 색은 전량 `var(--*)` 참조라 `base.css` 정정이 그대로 전파된다.

---

## §5 DESIGN_REF 교정 내역

`ui_fidelity.md` §1이 든 불일치 3 · 근거 오기 2 · 근거 없음 1 · 문서 누락 2 전건 + 부분 불일치·부분 판정분.

| # | 절 | 교정 |
|---|---|---|
| 1 | 머리말 | "색상은 Tailwind 표준 hex"라는 서술 제거. 시맨틱 팔레트가 v4 `theme.css` oklch 변환값이며 v3 hex와 동치가 아님(최대 ΔE 3.86)을 색 표기 규칙으로 명시. 실측 소스에 커밋 `f79997b`·스택 버전 병기 |
| 2 | §1 브랜드 토큰 | `@theme inline`의 실제 변수명이 `--color-primary-*`이고 `:root`의 `--primary`는 별개 선언임을 병기. `@theme inline` 때문에 브랜드 토큰이 `:root`로 방출되지 않는 사실 추가 |
| 3 | §1 그림자 | 토글 활성 `shadow-sm`을 v4 값으로 교체. `shadow-2xl` 행 신설. v3→v4 그림자 계단 이동과 `blur-sm` 8px 사실 추가 |
| 4 | §1 시맨틱 팔레트 | 표 전체를 v4 값으로 교체. 계열별 사용 단계를 실사용 기준으로 확장(red-400/800 · amber-500/800 · emerald-300 · violet-50/200 등). green·teal·cyan·orange·blue-50/600 행 신설. 유지 4종의 사유 명기 |
| 5 | §2 폰트 | `subsets:["latin"]`이 프리로드만 제한하고 한글 `@font-face` 497개가 번들에 포함된다는 사실 추가. 실폭 실측치(766.0px)와 `Noto Sans KR Fallback`의 성격 병기 |
| 6 | §3 레이아웃 | 콘텐츠 패딩 근거를 `AdminLayout.tsx:582`(마진) → `app/page.tsx:40`·`manage/page.tsx:187`로 정정. **상단 탭바 행 신설** — 40px 규격과 "탭 2개 이상일 때만 렌더" 조건, 근거 3파일 |
| 7 | §5 카드 | 부호값 색에 `signedTone==='cost'` 반전 병기 |
| 8 | §6 테이블 | 헤더 `tracking .05em`이 넓은 표 전용임을 명시. 행 hover 근거에서 `PreSettlementTab.tsx:691` 제거(확장 행 배경이며 hover 아님) → `manage:291` 단독 |
| 9 | §7 뱃지 | 미기재 2종 추가(`NOT_TARGET` gray-100/gray-400 · `DEDUCTED` red-100/red-700). 소형 pill을 원본 2종으로 분리 기재하고 재현본 단일 규격이 미결임을 병기 |
| 10 | §12 툴팁 | 앵커 `inline` → `inline-block`(:1019). 점선 톤 hex 병기. 패널 배경 `#111827` → `#101828`. `text-[11px]`·`text-[10px]`의 상속 line-height(16.5px·15px) 추가 |
| 11 | §13 토스트 | success·error hex를 v4 값으로 교체 |
| 12 | §14 모달 | 폼 모달 백드롭 blur 4px → 8px. 컨테이너 `shadow-2xl`·인풋 패딩 10/16 추가. `manage:373` orange 틴트 헤더가 개별 변형이며 공통 규격이 아님을 명시 |
| 13 | §4 사이드바 | 그룹 라벨·메뉴 항목·로그아웃의 v3 hex를 v4로 교체하고 토큰명 병기 |
| 14 | §8 버튼 | 엑셀 버튼 emerald-600/700 hex를 v4로 교체 |
| 15 | §16 신설 | 재현본 의도적 이탈·미채택 6건 등재 — 상단 탭바(결정 대기) · 대시보드 웰컴 그라디언트 · 필터 탭 보더 · `tabular-nums` 병용 · `.tbl.wide` 미사용 · 대형 CTA와 radius 10px. 기존 §16은 §17로 이동 |

문체 — `~입니다`·`~습니다` 종결 0건. 변경 경위 서술 없이 현재 상태만 기술.

---

## §6 검증 결과

전 항목 headless Chrome 151.0.7922.174(`--headless=new`, 창 미표시) + 로컬 `http://localhost:8901`.

### 6-1. ΔE 재계산

| 구간 | 정정 전 | 정정 후 |
|---|---|---|
| ΔE ≥ 1.5 (불일치) | 11 | **0** |
| 0.5 ≤ ΔE < 1.5 (근사) | 13 | **0** |
| ΔE < 0.5 (일치) | 13 | **44** |
| 최대 ΔE | **3.86** (`--red-600`) | **0.48** (`--red-200`, 유지 판정분) |

### 6-2. CSS 유효성

| 검사 | 결과 |
|---|---|
| Chrome CSSOM 파싱(`document.styleSheets`) | 규칙 224개 · 선언 2,246개 · **선언이 전부 탈락한 규칙 0건** |
| 중괄호 균형 | 0 |
| 미정의 변수 참조 | **0건** (선언 65 · 사용 56) |
| `:root` 밖 팔레트 원시 hex | **0건** (잔여 4건은 `globals.css` 원문과 동일한 foreground·스크롤바) |

### 6-3. computed style 확인

`assets/components.html` 23개 셀렉터 실측 — 전건 목표값 일치.

`badge-green #007a55` · `badge-red #c10007` · `badge-amber #bb4d00` · `badge-blue #1447e6` · `badge-violet #7008e7` ·
`toast-success` 보더 `#00c950`/텍스트 `#016630` · `toast-error` 보더 `#fb2c36`/텍스트 `#9f0712` · `notice-violet #7008e7` ·
`btn-excel #009966` · `toggle-btn.active` v4 shadow-sm · `tbl th letter-spacing normal` · `t-label`·`tip-panel` 16.5px ·
`filter-tab .count` 16px · `formula-op` 28px · `modal-body label` 20px · `input`·`search-input` `rgb(23,23,23)` ·
`modal-icon.warning #fe9a00` · `summary-card.amber #973c00` · `tip-green #5ee9b5`.

### 6-4. 렌더 확인

1440px 뷰포트에서 화면 35개 전수 — **가로 오버플로 0건**(`scrollWidth == clientWidth == 1440`).

`invest-profit--datepicker.html`의 `.filter-field` 내부 오버플로 1건은 절대배치 데이트피커 팝오버 때문이며,
정정 전 `base.css`를 CDP로 주입해 같은 화면을 재측정한 결과 동일하게 재현 — **선행 상태이며 본 정정과 무관**.
페이지 높이는 산식 카드가 있는 화면에서 +2px(11px 라벨 line-height 15→16.5px 반영분).

육안 확인 — `invest-assets` · `merchants` · `contracts--downloaded`(토스트) · `assets/components.html`(뱃지 8종 · 토스트 3종 · 툴팁 · 표 차감 표시 · 배너).
뱃지 8종 전부 판독 가능, success 토스트 3종 정상, 표의 차감값(`−1,200,000`)이 `--red-600 #e7000b`로 표시, 대기 배너 violet 틴트 정상.

### 6-5. 대비 확인

색 정정이 가독성을 낮추지 않는지 WCAG 대비비로 검산 — 19쌍 전건에서 등급 변동 없음. 최대 증감 ±0.18.

| 쌍 | 전 | 후 |
|---|---|---|
| `badge-green` | 4.84 | 4.73 (AA) |
| `badge-violet` | 5.98 | 6.15 (AA) |
| `toast-error` | 6.80 | 6.84 (AA) |
| `btn-danger`(흰 텍스트) | 4.83 | 4.77 (AA) |
| `btn-excel`(흰 텍스트) | 3.77 | 3.65 (AA-large, 12px/500 · 정정 전과 동일 등급) |
| 표 차감값 `td.red` | 4.83 | 4.77 (AA) |

### 6-6. 범위 준수

`app.html` · `certificate.html` · `contracts*.html` · `acquisition*.html` · `merchants*.html` · `assets/docs/` ·
`_pipeline/investor_admin/build_app.py` · `build_docs.py` · `wire_docs.py` 변경 0건.
타 조 검증기 미실행. 커밋·푸시 없음. `payhug-admin-web` 변경 0건(읽기만).

---

## 부록 — 재현 절차

```
# v4 팔레트 추출 + ΔE 계산 (변환기는 ui_fidelity.md 실측 29건으로 검증됨)
node theme.js     # theme.css oklch → sRGB hex
node cmp.js       # base.css :root ↔ v4 ΔE2000

# headless Chrome (창 미표시)
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --remote-debugging-port=9344 \
  --user-data-dir=<scratch>/fix/prof about:blank

node cdp.js       "http://localhost:8901/assets/components.html" probe_after.js 9344   # computed 23종
node fix/cdp1440.js "http://localhost:8901/<화면>" ov.js                                # 1440px 오버플로
node cw.js        # 대비비 전/후
```

작업 산출물(변환기·프로브·전후 캡처·`base.css`/`DESIGN_REF.md` 정정 전 사본)은
`/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/fix/`
에 있으며 세션 종료 시 소멸한다.
