# 투자자 어드민 UI 재현 충실도 검증

대조 축 — 기준(진실) `payhug-admin-web`(실 운영 어드민) ↔ 중간 문서 `DESIGN_REF.md` ↔ 재현본 `payhug-investor-admin/assets/base.css` + 화면 HTML.

---

## §0 판독 시각 · 방법

| 항목 | 값 |
|---|---|
| 판독 시각 | **2026-08-27 17:25 ~ 17:50 KST** |
| 기준 레포 | `/Users/semi/cursor/payhug-admin-web` @ `f79997b` (2026-08-25, `Merge branch 'develop' into feature/PAYHUG-203`) |
| 기준 스택 | Next.js 16.1.6 · React 19.2.0 · **tailwindcss 4.2.1**(`node_modules/tailwindcss/theme.css` 직접 판독) |
| 재현본 | `/Users/semi/cursor/payhug-investor-admin` — `assets/base.css` **588행 / 88,843바이트 / mtime 2026-08-27 15:08**, 화면 HTML 41개 |
| 중간 문서 | `/Users/semi/cursor/payhug-investor-admin/DESIGN_REF.md` — **13,239바이트 / mtime 2026-08-27 13:46** |

재현본 레포는 타 조가 동시 작업 중이라 `README.md`·화면 HTML 다수가 미커밋 상태다. 본 검증이 근거로 삼은 `assets/base.css`·`DESIGN_REF.md`는 판독 시작(17:25)과 종료(17:50) 시점의 mtime·바이트 수가 동일해, 판독 중 변경되지 않았음을 확인했다. 화면 HTML은 위 시각 스냅샷 기준이며 이후 변경분은 반영되지 않는다.

### 원본 어드민 실행 여부 — 부분 실행

`npm run dev`로 `http://localhost:3001` 기동 성공(Turbopack, Ready 686ms). `/login`은 실물 렌더되나 **백엔드 부재로 인증 이후 화면(대시보드·정산현황·가맹점관리)은 열리지 않는다**. 따라서 두 경로를 병용했다.

1. **토큰·유틸리티 실측** — 원본 dev 서버가 서빙하는 컴파일 CSS 번들
   `http://localhost:3001/_next/static/chunks/%5Broot-of-the-server%5D__57c617e4._.css` (466,992바이트, @font-face 497개 포함)을 그대로 링크한 프로브 페이지를 별도 오리진(127.0.0.1:8903)에 띄우고, **원본 소스의 클래스 문자열을 글자 그대로 옮겨 붙인 요소** 104개의 computed style을 headless Chrome 151.0.7922.174(`--headless=new`, 창 미표시)로 추출.
   근거: `@theme inline` 지시자 때문에 브랜드 토큰이 `:root` 변수로 방출되지 않고 유틸리티에 인라인되므로, 변수 조회가 아니라 유틸리티 적용 후 computed 값을 읽는 방식이 유일하게 정확하다.
2. **폰트 판정** — 원본 `/login` 실물 페이지에서 직접 측정(아래 §3-1).

재현본은 가동 중인 `http://localhost:8901`의 실 페이지 5종(`invest-assets.html`, `assets/components.html`, `acquisition--confirm.html`, `contracts--downloaded.html`, `login.html`)에서 computed style을 추출.

### 색차 판정 방법

Tailwind v4 팔레트는 `oklch()`로 정의되고 Chrome은 computed 값을 `lab()`으로 직렬화한다. 눈대중을 배제하기 위해 각 색을 1×1 캔버스에 `globalCompositeOperation:'copy'`로 실제 페인트해 sRGB 바이트를 확정한 뒤 **CIEDE2000**으로 비교했다.

| 판정 | 기준 |
|---|---|
| 일치 | ΔE2000 < 0.5 · 알파차 < 0.01 |
| 근사 | ΔE2000 < 1.5 |
| 불일치 | ΔE2000 ≥ 1.5 (JND 초과, 나란히 두면 구분됨) |

### 규율 준수

`payhug-admin-web`은 읽기만 했다. dev 서버 기동으로 gitignore 대상 `.next/` 외 변경 없음, 커밋·푸시 없음. 재현본 레포는 읽기만 했고 **HTML·CSS 수정 0건**. 산출물은 본 문서 1개.

---

## §1 DESIGN_REF 주장 검증 (1단)

검증 **92건** — 개별 주장 89건 + 시맨틱 팔레트 46토큰 일괄 1건 + 문서 누락 2건.

**일치 77 · 근사 1 · 부분 불일치 3 · 부분 3 · 불일치 3 · 근거 오기 2 · 근거 없음 1 · 누락 2**.

### 1-1. 브랜드 토큰 (주장 근거 `app/globals.css:3-27, 29-35`)

근거 행 번호 정확. `@theme inline`(3~27행)·`:root`(29~35행) 모두 확인.

| 주장 토큰 | 주장값 | 원본 실제 | 판정 |
|---|---|---|---|
| `--primary` / `primary-400` | `#7FE141` | `--color-primary`·`--color-primary-400` = `#7FE141` (globals.css:4,9) | 일치(이름 표기 부정확) |
| `--primary-50` | `#f4fdf0` | :5 동일 | 일치 |
| `--primary-100` | `#e5facf` | :6 동일 | 일치 |
| `--primary-200` | `#cef4a7` | :7 동일 | 일치 |
| `--primary-300` | `#b0eb75` | :8 동일 | 일치 |
| `--primary-500` | `#65c826` | :10 동일 | 일치 |
| `--primary-600` | `#4da119` | :11 동일 | 일치 |
| `--primary-700` | `#3a7a15` | :12 동일 | 일치 |
| `--primary-800` | `#29570e` | :13 동일 | 일치 |
| `--primary-900` / `--navy` | `#163300` | :14, :18 동일 | 일치 |
| `--secondary` | `#7e8299` | :16 동일 | 일치 |
| 사이드바 배경 `#1B2537` (`AdminLayout.tsx:409,427`) | `#1B2537` | :409 모바일 상단바, :427 aside — 둘 다 `bg-[#1B2537]` | 일치 |

> **이름 표기 부정확**: `@theme` 안의 실제 변수명은 `--color-primary-*`이고 `:root`의 `--primary`는 별개 선언이다. 값은 같아 재현에 영향 없으나, 문서만 보고 `var(--primary)`를 어드민 코드에서 찾으면 못 찾는다.

### 1-2. 그림자 (주장 근거 `app/globals.css:22-24`)

| 주장 토큰 | 주장값 | 원본 실제 | 판정 |
|---|---|---|---|
| `--shadow-card` | `0 1px 20px 0 rgba(0,0,0,0.08)` | globals.css:22 동일 | 일치 |
| `--shadow-card-hover` | `0 10px 40px -10px rgba(127,225,65,0.15)` | :23 동일 | 일치 |
| `--shadow-button` | `0 4px 14px 0 rgba(127,225,65,0.39)` | :24 동일 | 일치 |
| 툴팁·토스트 `shadow-lg` | `0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -4px rgba(0,0,0,0.1)` | `theme.css:410` 동일 | 일치 |
| 모달 `shadow-xl` (`ConfirmDialog.tsx:55`) | `0 20px 25px -5px …, 0 8px 10px -6px …` | `theme.css:411` 동일, :55에 `shadow-xl` 존재 | 일치 |
| **토글 활성 `shadow-sm`** (`settlement/overview/page.tsx:276`) | `0 1px 2px 0 rgba(0,0,0,0.05)` | **`0 1px 3px 0 rgb(0 0 0/.1), 0 1px 2px -1px rgb(0 0 0/.1)`** (`theme.css:408`) | **불일치** |

> 주장값은 Tailwind **v3**의 `shadow-sm`이자 v4의 `shadow-xs`(`theme.css:407`)다. v4에서 그림자 계단이 한 칸씩 밀렸는데 그 변경이 반영되지 않았다. 인용한 `:276`에 `shadow-sm`이 있다는 사실은 맞다.

### 1-3. 시맨틱 팔레트 — 전량 v3 hex, 원본은 v4 oklch

주장표는 "원본은 v4 oklch, 아래는 동치 hex"라 적었으나 실제로는 **Tailwind v3 hex**다. v4는 oklch로 팔레트를 다시 뽑아 동치가 아니다. 46개 토큰 실측 결과.

| 계열 | 근사(ΔE<1.5) | 불일치(ΔE≥1.5) | 최대 편차 |
|---|---|---|---|
| gray 50~900 (10) | 10 | 0 | gray-400 ΔE 1.07 |
| emerald 50~800 (8) | 8 | 1(500 ΔE1.57·600 ΔE1.65 제외 시) | emerald-600 `#009966`→`#059669` ΔE **1.65** |
| red 50~800 (8) | 2 | 6 | red-600 `#e7000b`→`#dc2626` ΔE **3.86** |
| amber 50~700 (5) | 3 | 2 | amber-400 `#ffb900`→`#fbbf24` ΔE **2.55** |
| blue 100·700 (2) | 1 | 1 | blue-700 `#1447e6`→`#1d4ed8` ΔE **2.64** |
| violet 50~700 (4) | 3 | 1 | violet-700 `#7008e7`→`#6d28d9` ΔE **2.57** |
| green 100·500·800 (3) | 1 | 2 | green-500 `#00c950`→`#22c55e` ΔE **2.38** |

ΔE 상위 12건(원본 → 재현본 주장): red-600 `#e7000b`→`#dc2626` 3.86 · red-700 `#c10007`→`#b91c1c` 3.29 · **amber-600 `#e17100`→`#d97706` 3.02** · **amber-500 `#fe9a00`→`#f59e0b` 2.92** · red-500 `#fb2c36`→`#ef4444` 2.81 · blue-700 `#1447e6`→`#1d4ed8` 2.64 · violet-700 `#7008e7`→`#6d28d9` 2.57 · amber-400 `#ffb900`→`#fbbf24` 2.55 · red-400 `#ff6467`→`#f87171` 2.52 · green-500 `#00c950`→`#22c55e` 2.38 · amber-700 `#bb4d00`→`#b45309` 2.29 · red-800 `#9f0712`→`#991b1b` 2.03. 이어서 amber-800 `#973c00`→`#92400e` 1.79 · emerald-600 1.65 · emerald-500 1.57 · emerald-300 `#5ee9b5`→`#6ee7b7` 1.47.

**판정: 부분 불일치** — 무채색 10건은 근사, 채도 높은 15건은 불일치.

### 1-4. 폰트 (§2)

| 주장 | 원본 실제 | 판정 |
|---|---|---|
| `Noto_Sans_KR` next/font, weights 400/500/600/700 — `app/layout.tsx:6-10` | `layout.tsx:6-10` 정확. 단 `subsets:["latin"]`(:8)이 문서에 미기재 | 일치(보완 필요) |
| 본문 스택 `"Noto Sans KR", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif` — `globals.css:26,40` | :26 `--font-sans`, :40 `body{font-family:…}` 모두 동일 | 일치 |
| 숫자 = `font-mono` + 우측정렬, 일부만 `tabular-nums`(account-balance) | `font-mono` 21개 파일 사용, `tabular-nums`는 `account-balance`·`manage:503`·`merchants/[id]:2184`만 | 일치 |
| 타이포 8행 px 환산 (3xl 30/36 · 2xl 24/32 · xl 20/28 · lg 18/28 · sm 14/20 · xs 12/16 · 11px · 10px) | `theme.css:347-360` 전 행 일치. `text-[11px]`·`text-[10px]`은 line-height 미지정 → html의 1.5 상속 = 16.5px·15px | 일치 |

> `subsets:["latin"]`은 **프리로드 대상만** 제한한다. 컴파일 번들에는 한글 unicode-range를 가진 @font-face 497개가 그대로 실려 있으므로(원본 CSS 번들 직접 확인) 한글이 시스템 폰트로 떨어지지 않는다. 폰트 결함 아님 — 실측은 §3-1.

### 1-5. 레이아웃·사이드바 (§3·§4)

| 주장 | 원본 실제 | 판정 |
|---|---|---|
| 사이드바 폭 240px(접힘 72px) — `AdminLayout.tsx:428` | `:428 w-[72px]/w-[240px]` | 일치 |
| 콘텐츠 `margin-left:240px` — `:582` | `:582 md:ml-[240px]` | 일치 |
| 콘텐츠 패딩 32px(p-8) — 근거를 `:582`로 병기 | `:582`는 마진. 패딩 근거는 `app/page.tsx:40`·`manage/page.tsx:187`의 `p-4 md:p-8` | 근거 오기 |
| 페이지 배경 gray-50 — `:400` | `:400 min-h-screen flex bg-gray-50` | 일치 |
| 페이지 헤더 24/700 gray-900 + 부제 14 secondary + 아래 24px — `manage:189-193` | `mb-6` / `text-2xl font-bold text-gray-900` / `text-secondary text-sm mt-1` | 일치 |
| 로고 영역 h64 px20 하단보더 white/10 — `:433` | `h-16 flex items-center px-5 border-b border-white/10 shrink-0` | 일치 |
| 로고 아이콘 32px r8 + 워드마크 18/700, 강조 `#7FE141` — `:444-448` | `w-8 h-8 rounded-lg` / `text-lg font-bold` / `text-primary-400` | 일치 |
| 내비 패딩 16 12 — `:454` | `flex-1 py-4 px-3` | 일치 |
| 그룹 라벨 11/600 uppercase .05em gray-500, 쉐브론 12px, 활성 `#7FE141` — `:486-501` | `text-[11px] font-semibold uppercase tracking-wider` / `w-3 h-3` / `text-primary-400 : text-gray-500` | 일치 |
| 그룹 간격 16px, 항목 간격 2px — `:477`·`:507` | `space-y-4` / `space-y-0.5` | 일치 |
| 메뉴 항목 gap12 p8/12 r8 14/500 기본 gray-400 — `:515-519` | `gap-3 px-3 py-2 rounded-lg` + `:526 text-sm font-medium`, `text-gray-400` | 일치 |
| 항목 hover white/5 + 흰 텍스트 — `:518` | 동일 | 일치 |
| 항목 활성 `bg-primary text-white` — `:517` | 동일 | 일치 |
| 메뉴 아이콘 16px stroke 1.8 — `:37` | `w-4 h-4` + `strokeWidth={1.8}` | 일치 |
| 프로필 상단보더 white/10, p12, 아바타 36px `primary/20` + 아이콘 `#7FE141` — `:556-561` | `border-t border-white/10 p-3` / `w-9 h-9 bg-primary/20 rounded-full` / `w-4 h-4 text-primary-400` | 일치 |
| 이름 14/500 흰색 truncate / 로그아웃 12px gray-500 hover gray-300 — `:565-570` | 동일 | 일치 |

### 1-6. 카드·테이블·뱃지 (§5·§6·§7)

| 주장 | 원본 실제 | 판정 |
|---|---|---|
| 기본 카드 `#fff` r16 p24 shadow-card 보더 gray-100 — `page.tsx:55` | 동일 | 일치 |
| 지표 카드 p20 — `page.tsx:477`·`PreSettlementTab.tsx:874` | `rounded-2xl p-5 shadow-card border` | 일치 |
| 지표 구성 라벨 12/600 gray-500 → 값 20/700 mono(원 14/400 좌2) → 서브 12 gray-400 상4 — `:879-883` | 동일(라벨 `mb-2`=8px는 미기재) | 일치 |
| 강조 카드 emerald-50 + 보더 emerald-200 + 값 emerald-800 — `page.tsx:227-232` | 동일(`iconBg emerald-500`·`labelColor emerald-700` 미기재) | 일치 |
| 부호값 양수 primary-700 / 음수 red-700 / 0 gray-400 — `:867-871` | `signedTone==='cost'`면 **반전**(양수 red-700, 음수 primary-700) | 부분 불일치 |
| 카드 그리드 gap-4 — `page.tsx:185` | `grid grid-cols-2 lg:grid-cols-6 gap-4` | 일치 |
| 테이블 래퍼 카드 + overflow hidden/내부 auto — `manage:260-261` | 동일 | 일치 |
| 본문 14px — `PreSettlementTab.tsx:666` | `w-full text-sm` | 일치 |
| 헤더 gray-50 · 12/16 · 12/600 gray-500 uppercase **tracking .05em** — `:667-678`, `manage:264-274` | `manage:265`는 `tracking-wider` 있음, **`PreSettlementTab:669`는 없음** | 부분 불일치 |
| 바디 셀 12/16(넓은 표 16/20) gray-700 — `:703`, `manage:294` | `px-4 py-3` / `px-5 py-4` | 일치 |
| 행 구분선 `divide-gray-50` — `:681` | 동일 | 일치 |
| 행 hover gray-50 · 클릭형 `primary-50/30` — `:691`, `manage:291` | `manage:291 hover:bg-primary-50/30` 맞음. **`:691`은 hover가 아니라 확장 행 `bg-primary-50/50`** | 근거 오기 |
| 숫자 셀 우측정렬 + font-mono(+tabular-nums) — `:703` | `text-right font-mono`, `tabular-nums` 없음(문서 §2에 예외 명시됨) | 일치 |
| 강조 값 순지급액 500/gray-900 · 최종 700/gray-900+원 · 수수료 amber-700 · 차감 red-600/600 — `:706,731,770` | `:706`·`:770`·`:731`·`:713` 모두 확인 | 일치 |
| 가맹점 셀 이름 600 gray-900 + 사업자번호 12 gray-400 mono — `:696-701` | 동일 | 일치 |
| 빈 상태 py 64px 중앙 secondary — `manage:279-283` | `px-5 py-16 text-center text-secondary` | 일치 |
| 뱃지 표준 4/10 r9999 12/500 — `manage:318`, `:808` | 동일 | 일치 |
| 뱃지 색 매핑 7종 — `:36-50, 101-110` | 7종 모두 일치. **미기재 2종**: `NOT_TARGET` 미대상 `gray-100/gray-400`(:49), `DEDUCTED` 선정산차감 `red-100/red-700`(:48) | 부분 |
| **소형 pill 2/6 r4 10px/700** — `:698`, `manage:299` | `manage:299`는 `font-bold`(700) 맞음. **`PreSettlementTab:698`은 `font-medium`(500)** + `bg-cyan-50 text-cyan-700` | **불일치** |
| 소형 pill 색 | `cyan-50/cyan-700`(:698), `blue-50/blue-600`(manage:299) — 둘 다 §1 팔레트 미등재 | **근거 없음** |

### 1-7. 버튼·필터·토글·페이지네이션 (§8·§9·§10)

| 주장 | 원본 실제 | 판정 |
|---|---|---|
| primary 8/20 `#7FE141` 흰 14/600 r8 → h36, hover primary-600 — `DateRangeFilter.tsx:129` | 동일(computed 실측 h36 확인) | 일치 |
| outline 8/16 흰 보더 gray-200 gray-600 14/500 — `:133` | 동일 | 일치 |
| 엑셀 8/12 emerald-600 흰 12/500 r8 아이콘 16 stroke2 gap6, hover emerald-700 — `ExcelDownloadButton.tsx:15-19` | 동일 | 일치 |
| disabled gray-300 not-allowed — `:129` | 동일 | 일치 |
| 모달 풋터 세로 10px r12 flex-1 — `manage:417-424` | `flex-1 py-2.5 … rounded-xl` | 일치 |
| 필터 카드 카드+p16, 하단 24 — `DateRangeFilter.tsx:90` | 동일 | 일치 |
| 프리셋 칩 4/10 r6 12/500 gray-50/gray-200, 활성 primary — `:100-104` | 동일(칩 간격 `gap-1.5`=6px 미기재) | 일치 |
| date 인풋 8/12 gray-50 gray-200 r8 14px, focus primary + `rgba(127,225,65,.2)` 2px — `:117` | `focus:ring-2 focus:ring-primary/20 focus:border-primary` | 일치 |
| 인풋 라벨 12 secondary 아래4 — `:115` | `block text-xs text-secondary mb-1` | 일치 |
| 키워드 검색 12/16+좌48 r12, 돋보기 20px gray-400 — `manage:246-255` | `pl-12 pr-4 py-3 … rounded-xl` + `left-4 w-5 h-5 text-gray-400` | 일치 |
| 세그먼트 토글 gray-100 r8 p4 gap4 / 버튼 8/16 r6 14/500 / 활성 흰+gray-900+shadow-sm — `overview/page.tsx:271-278` | 동일(shadow-sm **값**은 1-2 참조) | 일치 |
| 상태 필터 탭 8/16 r8, 활성 primary 흰, 카운트 12(활성 white/70·비활성 gray-400) — `manage:224-240` | 동일. **비활성 탭이 `bg-white` + `border-gray-200` 보유** 사실 미기재 | 부분 |
| 페이지네이션 컨테이너 14/20 상단보더 gray-100 중앙 gap4 / 번호 32²  r8 12/500 / 화살표 6/12 + 16px, disabled 0.4 — `activity-logs:338-359` | 전 항목 일치 | 일치 |

### 1-8. 산식·툴팁·토스트·모달·안내 (§11~§16)

| 주장 | 원본 실제 | 판정 |
|---|---|---|
| 산식 카드 r16 shadow-card 틴트(일치 emerald-50/40 + emerald-200) — `account-balance:527-530` | 동일 | 일치 |
| 산식 헤드 12/24 하단보더 `black/5` + 상태 pill — `:532-545` | `px-5 md:px-6 py-3 border-b border-black/5`(데스크톱 24px) | 일치 |
| 수식 행 flex wrap gap12 p16/24 — `:555` | `px-5 md:px-6 py-4 gap-x-3 gap-y-3` | 일치 |
| Term 라벨 11 secondary max-200 truncate → 값 tabular-nums 600(강조700) gray-800, 원 12/400 op.7 → sub 10 gray-400, 톤 4종 — `:638-665` | `:654,657,658,660,662` 전량 일치 | 일치 |
| Op `= + −` gray-300 18/300 좌우2 — `:609-611` | `text-gray-300 text-lg font-light px-0.5` | 일치 |
| 툴팁 앵커 **inline** + cursor:help, 점선 밑줄 red-400/amber-400 — `:713,796,1019` | `:1019`는 **`inline-block`** | 근사 |
| 툴팁 패널 224/256 gray-900 흰 11/400 r8 p10 shadow-lg — `:1034` | 동일(`w-56`/`w-64`, `:1000`의 224/256 상수와 짝) | 일치 |
| 툴팁 분해행 양끝정렬 · 합계행 상단 gray-700 · 안내 emerald-300 — `:744-763` | `:753 border-t border-gray-700`, `:756 text-emerald-300` | 일치 |
| 토스트 fixed top24 중앙, 12/20 r8 1px shadow-lg 500 — `Toast.tsx:29-43` | `:42 fixed top-6 left-1/2`, `:43 px-5 py-3 rounded-lg border shadow-lg`, `:44 font-medium` | 일치 |
| 토스트 색 success green-100/500/800 · error red · info primary — `:29-33` | 동일(hex는 1-3 참조) | 일치 |
| 모달 백드롭 `black/40` — `ConfirmDialog:54` | 동일 | 일치 |
| 확인형 r16 max-w-sm(384) p24 shadow-xl / 아이콘 40 원형 3톤 / 제목 16/700 / 설명 14 gray-500 / 우측정렬 — `:53-77` | `:55,56,61,62,63` 전량 일치 | 일치 |
| **폼형 백드롭 `black/60` + blur 4px** — `manage:370` | `bg-black/60 backdrop-blur-sm` — v4 `--blur-sm`은 **8px**(`theme.css:477`), 4px는 `--blur-xs` | **불일치** |
| 폼형 max-w-md(448) / 헤더 16-24 하단보더 / 바디 24 gap16 / 라벨 14/600 gray-700 / 인풋 r12 gray-300 / 풋터 16-24 gray-50 flex-1 — `manage:369-427` | 치수 전량 일치. **헤더가 `bg-orange-50 border-orange-200` 틴트**·**컨테이너가 `shadow-2xl`**·**인풋 패딩 10/16**은 미기재 | 부분 |
| 배너 12/16 r12 1px 14px — violet(page.tsx:237)·red(manage:212) | 동일 | 일치 |
| 스크롤바 6px, 트랙 `#f1f5f9`, 썸 `#cbd5e1` r3 — `globals.css:51-63` | 행 번호까지 정확 | 일치 |
| radius 변환표 4/6/8/12/16/9999 | `theme.css:397-403` 일치 | 일치 |
| 아이콘 관례 메뉴·셀 16, 카드 헤더 20, 배지 컨테이너 32~40 | `page.tsx:58-59` 등에서 확인 | 일치 |

### 1-9. DESIGN_REF 누락 2건

| 누락 | 원본 근거 | 영향 |
|---|---|---|
| **상단 탭바** — 어드민은 `TabContext.tsx:89`에서 `isTabMode: true`를 상시 제공하고 `AdminLayout.tsx:585`가 `<TabBar/>`를 렌더한다. 탭바는 `h-10`(40px) `bg-white` `border-b border-gray-200` `px-2`, 탭 라벨 12/500 + 하단 2px 인디케이터(`TabBar.tsx:11,17`) | 콘텐츠 상단에 40px 크롬이 항상 붙음. 재현본에는 없음 |
| **대시보드 웰컴 그라디언트** — `page.tsx:42 bg-gradient-to-r from-primary-700 to-primary-500` r16 p32 mb32 | `.gradient-primary`(#7FE141→#163300)와 다른 조합. 재현본 무영향(대시보드 미재현) |

---

## §2 재현 검증 (2단)

`base.css`·화면 HTML이 DESIGN_REF 값을 그대로 옮겼는가. 검증 **89건** — 토큰 선언 7건 + computed style 무차이 확인 61건 + 편차 21건.

**일치 69 · 근사 8 · 불일치 10 · 확인불가 2**.

### 2-1. 토큰 선언

| 항목 | base.css | 판정 |
|---|---|---|
| `--primary` ~ `--primary-900`, `--secondary`, `--navy*` (base.css:12-26) | DESIGN_REF·원본과 문자 단위 동일 | 일치 |
| `--sidebar-bg: #1B2537` (:27) | 동일 | 일치 |
| `--shadow-card` / `-hover` / `-button` (:29-31) | 동일 | 일치 |
| Tailwind 팔레트 46종 (:34-46) | **DESIGN_REF의 v3 hex를 그대로 복사** → §1-3의 편차가 그대로 전이 | 불일치(전이) |
| `--font-sans` (:48) | 원본 스택과 동일(단 `BlinkMacSystemFont` 위치까지 동일) | 일치 |
| `--font-mono` (:49) | Tailwind v4 기본 `--font-mono`와 문자 단위 동일(원본 computed로 확인) | 일치 |
| 스크롤바 (:70-73) | `globals.css:51-66`과 동일 | 일치 |

### 2-2. computed style 대조 — 일치 확인분

사이드바(폭 240 · 로고 h64/px20 · 내비 16/12 · 그룹 라벨 11/600/0.55px/uppercase · 그룹 16px·항목 2px 간격 · 항목 gap12 p8/12 r8 14/500 · 활성 `#7fe141`+흰 · 아바타 36px `rgba(127,225,65,.2)` · 이름 14/500 · 로그아웃 12px) · 콘텐츠(ml240 p32) · 페이지 헤더(24/32/700, 14/20 secondary, mb24) · 카드(r16 p24 shadow-card 보더 `#f3f4f6`) · 지표 카드(p20, 라벨 12/16/600 mb8, 값 20/28/700, 원 14/400 ml2, 서브 12/16 mt4) · 그리드 gap16 · 테이블(래퍼 r16 shadow-card · th 12/16 12/600 gray-500 uppercase · td 12/16 14/20 · 구분선 `#f9fafb` · 클릭행 hover `rgba(244,253,240,.3)`) · 뱃지(4/10 r9999 12/16/500) · 버튼(primary 8/20 r8 14/600 `#7fe141` / outline 8/16 보더 `#e5e7eb` / 엑셀 8/12 12/16/500 gap6) · 필터(카드 p16 mb24 · 칩 4/10 r6 12/16/500 `#f9fafb`/`#e5e7eb` · 활성 `#7fe141` 3면 일치 · date 인풋 8/12 r8 · 라벨 12 `#7e8299` mb4 · 검색 12/16/12/48 r12) · 토글(gray-100 r8 p4 gap4 mb16 · 버튼 8/16 r6 14/500) · 필터 탭(8/16 r8 14/500, 활성 `#7fe141`+흰) · 페이지네이션(14/20 상단보더 `#f3f4f6` gap4 · 번호 32² r8 12/500 · 화살표 6/12 · disabled .4) · 모달(백드롭 `rgba(0,0,0,.4)` · r16 · shadow-xl `0 20px 25px -5px …` · max-w 384/448 · 제목 16/24/700 mb4 · 설명 14/20 mb24 · 풋터 16/24 `#f9fafb` gap12 · 풋터 버튼 flex-1 10/0 r12) · 토스트(12/20 r8 1px shadow-lg gap12) · 툴팁(224/256 r8 p10 shadow-lg) · 산식(카드 r16 · 헤드 12/24 `rgba(0,0,0,.05)` · 행 16/24 gap12 · 라벨 11 secondary max200 · 값 tabular-nums 600/강조700 gray-800 · 원 12/400 op.7 ml2 · sub 10 gray-400 mt2 · Op gray-300 18/300 좌우2) · 안내 배너(12/16 r12 1px 14/20) · terms-note(gray-50/gray-200 r12 16/20 12/18 gray-500).

### 2-3. computed style 대조 — 편차

| # | 요소 | 속성 | 원본 | 재현본 | 판정 |
|---|---|---|---|---|---|
| D1 | `.toggle-btn.active` | box-shadow | `0 1px 3px 0 rgba(0,0,0,.1), 0 1px 2px -1px rgba(0,0,0,.1)` | `0 1px 2px 0 rgba(0,0,0,.05)` | **불일치** |
| D2 | `.toast-success` | border-color | `#00c950` | `#22c55e` | **불일치** ΔE 2.38 |
| D3 | `.toast-success` | color | `#016630` | `#166534` | 근사 ΔE 1.43 |
| D4 | `.toast-error` | color / border | `#9f0712` / `#fb2c36` | `#991b1b` / `#ef4444` | **불일치** ΔE 2.03 / 2.81 |
| D5 | `.toast-info` | 3색 전부 | `#29570e`/`#e5facf`/`#65c826` | 동일 | 일치(브랜드 토큰) |
| D6 | `.notice-violet` | color | `#7008e7` | `#6d28d9` | **불일치** ΔE 2.57 |
| D7 | `.btn-excel` | background | `#009966` | `#059669` | **불일치** ΔE 1.65 |
| D8 | `.badge-green` | color | `#007a55` | `#047857` | 근사 ΔE 1.28 |
| D9 | `.tip-panel` / `.formula-term .t-label` | line-height | 16.5px(11px × html 1.5) | 15px | **불일치**(높이 −1.5px) |
| D10 | `.formula-op` | line-height | 28px(`text-lg`) | 27px(18 × 1.5) | 근사 |
| D11 | `.modal-body label` | line-height | 20px(`text-sm`) | 21px(14 × 1.5) | 근사 |
| D12 | `.filter-tab .count` | line-height | 16px(`text-xs`) | 20px(부모 상속) | **불일치** |
| D13 | `.filter-tab.active` | border | 없음(활성 탭만 보더 제거) | `1px solid #7fe141` | 근사(폭·높이 +2px) |
| D14 | `.tbl th` | letter-spacing | 좁은 표 없음 / 넓은 표 0.6px | 항상 0.6px | 근사 |
| D15 | `.input` / `.search-input` | color | `#171717`(preflight `color:inherit`) | `#111827` / `#000000` | 근사 |
| D16 | `.tip-anchor.red` | border-bottom-color | `border-red-400` `#ff6467` | `var(--red-500)` `#ef4444` | **불일치**(단계 자체가 다름) |
| D17 | `.modal-backdrop.blur` | backdrop-filter | `blur(8px)` | `blur(4px)` | 불일치(사용처 0 — 사문) |
| D18 | body 배경 | background | `#ffffff`(레이아웃 루트가 gray-50 덮음) | `#f9fafb` | 일치(실효) |
| D19 | 폰트 스택 | font-family | `"Noto Sans KR", "Noto Sans KR Fallback", -apple-system, …` | `"Noto Sans KR", -apple-system, …` | 근사(§3-1) |
| D20 | 상단 탭바 | — | `h-10` 흰 배경 + `border-b gray-200` 상시 | 없음 | 확인불가(범위 결정 사안) |
| D21 | `.badge.sm` | font-weight / 색 | `manage:299` 700 `blue-50/blue-600` · `PreSettlementTab:698` 500 `cyan-50/cyan-700` | 700 + `.badge-*` 색 상속 | 확인불가(원본 2종 병존) |

> D2·D4·D6·D7·D8은 §1-3에서 확정한 v3↔v4 팔레트 편차가 그대로 나타난 것이다. base.css 자체의 실수가 아니라 DESIGN_REF를 충실히 따른 결과다.

### 2-4. 재현본 고유 규격 (원본 미대응 — 결함 아님)

| 요소 | 내용 |
|---|---|
| `.terms-note` (base.css:560-566) | 투자자 화면 신규 규격. DESIGN_REF §15에 명시. 값 4건 문서와 일치 |
| `.sidebar-profile .type-badge` (:182-186) | 투자자 유형 표시. 어드민 프로필 영역에 대응 없음. 1/6 r4 10/700 `rgba(127,225,65,.2)`/primary-400 |
| `.formula-grid` / `.formula-caption` (:455-456) | 산식 카드 2열 배치. 어드민은 단일 열 |
| `.tbl.wide` (:274-275) | 정의만 있고 **사용 화면 0건** — 사문 |

---

## §3 중점 7항목 판정표

| # | 항목 | 판정 | 근거 |
|---|---|---|---|
| 1 | **폰트** | **일치** | 아래 §3-1 |
| 2 | 색 — 브랜드 토큰 | **일치** | `--primary` 10단계·`--secondary`·`#1B2537` 전량 문자 단위 동일. computed `rgb(127,225,65)` 양쪽 동일 |
| 2' | 색 — 시맨틱 팔레트 | **불일치** | v3 hex ↔ v4 oklch. 46토큰 중 채도 계열 12건 ΔE 1.5~3.86. 최악 red-600 3.86 |
| 3 | 간격·치수 | **일치** | 사이드바 240 · 콘텐츠 ml240/p32 · 카드 p24/지표 p20 · 표 12-16(넓은 표 14-20/16-20) · 버튼 h36 · 로고 h64. computed 전량 동일. **단 헤더는 원본에 40px 탭바가 있고 재현본에 없음 → 확인 필요** |
| 4 | 그림자·모서리 | **부분 불일치** | `--shadow-card`·`shadow-lg`·`shadow-xl`·radius 전량 일치. **`shadow-sm` 1건 불일치**(D1), `backdrop-blur` 1건 불일치(D17, 사문) |
| 5 | 컴포넌트 구조 | **근사** | 표·버튼·뱃지·모달·토스트·페이지네이션·필터 드롭다운 모두 원본 컴포넌트와 동일 구조·동일 상태 표현. 편차는 D12~D16의 소규모 5건 |
| 6 | 사이드바 표현 | **일치** | 배경 `#1B2537` · 그룹 라벨 11/600/0.05em/gray-500·활성 primary-400 · 항목 gap12 p8/12 r8 14/500 gray-400 · hover white/5 · **활성 `bg-primary` + 흰 텍스트** · 아이콘 16px · 프로필 36px 아바타. 메뉴 7종 구성은 확정 사항이라 대조 제외 |
| 7 | 하드코딩 이탈 | **근사(양호)** | 화면 산출물 29개 `<style>`+`style=` 전수에서 **원시 hex 0건**, 색은 전량 `var(--*)`. 인라인 178건은 전부 레이아웃 조정. 잔여는 `base.css` 본문의 토큰 미경유 hex 5건과 격자 밖 타이포 소수. §4 참조 |

### §3-1 폰트 판정 근거 (실측)

| 측정 | 원본 `localhost:3001/login` | 재현본 `localhost:8901/login.html` |
|---|---|---|
| body font-family | `"Noto Sans KR", "Noto Sans KR Fallback", -apple-system, "system-ui", "Segoe UI", Roboto, sans-serif` | `"Noto Sans KR", -apple-system, "system-ui", "Segoe UI", Roboto, sans-serif` |
| 로드된 @font-face 수 | 501 | 496 |
| `document.fonts.check('14px "Noto Sans KR"')` | true | true |
| `…check('700 14px "Noto Sans KR"')` | true | true |
| 한글 문자열 실폭 100px 기준 — 상속 스택 | **766.0px** | **766.0px** |
| 같은 문자열 — `"Noto Sans KR"` 강제 | 766.0px | 766.0px |
| 같은 문자열 — `-apple-system` 강제 | 704.7px | 704.7px |
| 같은 문자열 — `Arial` 강제 | 738.3px | 738.3px |

상속 스택 실폭이 Noto 강제값과 소수점까지 동일하고 시스템 폰트값과 61.3px 차이가 난다. **원본·재현본 모두 한글을 Noto Sans KR로 실제 렌더한다.** `subsets:["latin"]`은 프리로드 대상만 제한하며 한글 unicode-range @font-face 497개가 번들에 그대로 실려 있음을 원본 CSS 번들에서 직접 확인했다. 재현본의 Google Fonts `<link>` 방식은 원본과 렌더 결과가 같다. **어드민 폰트 결함 없음, 재현본 `Noto Sans KR` 채택 타당.**

차이는 next/font가 주입하는 메트릭 오버라이드 폴백 `Noto Sans KR Fallback`(`local(Arial)`, ascent 110.73% / descent 27.49% / size-adjust 104.76%) 1개뿐이다. 웹폰트 로드 전 레이아웃 시프트를 줄이는 장치이며, 로드 후 렌더에는 영향이 없다.

**숫자 표기** — 원본은 `font-mono`만 쓰고 `tabular-nums`는 `account-balance` 계열에만 붙인다. 재현본은 `.mono`·`.tbl td.num`·`.summary-value`·`.formula-term .t-value` 전부에 `font-variant-numeric: tabular-nums`를 병용한다. `font-mono` 스택은 양쪽 모두 `ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace`로 동일. 모노스페이스 폰트에서 tabular-nums는 자릿폭에 영향이 없어 렌더 결과 동일 — **의도된 이탈이며 DESIGN_REF §2에 명시됨**.

---

## §4 하드코딩 이탈 목록

### 4-1. 색 — 화면 HTML 이탈 0건 / `base.css` 잔여 5건

화면 산출물 29개(`app.html` 포함, 메타 문서 `index/capability/glossary/archive` 제외)의 `<style>` 블록 + `style=` 속성 전수 스캔:

| 구분 | 원시 hex | `rgb()`/`rgba()` 직접값 | 미등록 색 |
|---|---|---|---|
| 화면 산출물 29개 | **0** | 0 | **0** |
| 메타 문서 4개 | 62 | — | 5 (`#7c4a03` `#7c4a09` `#f7f8fa` `#fafbfc` `#fafdf8` — `archive.html` 55건, `capability.html` 3건, `glossary.html` 1건) |

화면 HTML의 색은 전부 `var(--*)` 참조. 메타 문서는 배포 화면이 아니므로 결함 취급하지 않는다.

단 **`base.css` 본문(`:root` 밖)에 토큰을 거치지 않은 팔레트 hex 5건**이 남아 있다 — `:224 #92400e`(amber-800) · `:480 #6ee7b7`(emerald-300) · `:493 #991b1b`(red-800) · `:518 #f59e0b`(amber-500) · `:578 #f5f3ff`·`#ddd6fe`(violet-50/200). 팔레트를 v4로 정렬해도 이 5건은 따로 고쳐야 한다(§5 P1 #4'). `:56 #171717`(foreground)과 `:71-73` 스크롤바 3색은 원본 `globals.css`와 문자 단위 동일해 문제 없다.

### 4-2. 인라인 `style=` 속성 — 총 178건, 전부 레이아웃 조정

빈도 상위: `margin:0`(14) · `flex:1; min-width:0`(13) · `width:100%`(7) · `padding:0; overflow:hidden`(5) · `padding:16px 24px; border-bottom:1px solid var(--gray-100)`(5) · `width:180px`(5) · 열 폭 지정 `width:NNNpx`(약 30). 색 지정은 전부 토큰 참조.

주목 대상 4건:

| 값 | 파일 | 성격 |
|---|---|---|
| `padding:12px 40px; font-size:16px; border-radius:12px` ×5 | `acquisition--*` 계열 대형 CTA | 어드민 버튼 규격(14/600, r8, 8/20) 밖. 화면 전용 대형 버튼 |
| `font-size:16px; line-height:28px; font-weight:700` ×4 | 모달·문서 제목 | `text-base`(16/24)도 `text-lg`(18/28)도 아닌 혼합 |
| `width:100%; padding:12px 0; border-radius:12px` ×4 | 폼 제출 버튼 | 모달 풋터 버튼(10/0 r12)과 상이 |
| `padding:16px 24px; border-bottom:1px solid var(--gray-100)` ×5 | 모달 헤더 대체 | `.modal-header`가 이미 동일 규격 — 클래스 미사용 |

### 4-3. 타이포 격자 이탈

| 값 | 건수 | 위치 |
|---|---|---|
| `font-size:13px` | 25 | `app.html`(12) `certificate.html`(3) `login.html`(2) `contracts--downloaded.html` `contracts--empty.html` `coocon--confirm.html` `invest-assets--cert-confirm.html` `invest-profit--datepicker.html` `assets/sheet.css`(2) — **어드민도 `text-[13px]` 2건 사용, 격자 이탈 아님** |
| `font-size:15px` / `line-height:22px` | 4 / 13 | `app.html` `certificate.html` `contracts--downloaded.html` — 토스트 2행 변형·증명서 서명란 |
| `font-size:22px` / `line-height:30px` | 2 | `login.html`·`app.html` 로그인 워드마크 |
| `font-size:26px` / `line-height:34px` | 1 | `app.html` 프로토타입 랜딩 hero (화면 아님) |
| `line-height:19px` | 1 | `app.html` 프로토타입 카드 설명 (화면 아님) |
| `border-radius:10px` | 3 | `app.html`(2) `password--weak.html`(1) — 어드민 radius 계단(4/6/8/12/16)에 없음 |

`font-size:9px`~`11px`는 어드민이 `text-[9px]` 40건·`text-[11px]` 69건·`text-[10px]` 181건을 쓰므로 이탈 아님.

### 4-4. 클래스 미사용

`.tbl.wide`(base.css:274-275) 정의만 있고 사용 화면 0건. 재현본 표는 전부 좁은 규격(12/16)만 쓴다. 어드민의 가맹점관리 표(14/20·16/20)에 대응하는 화면이 없으므로 현재로선 무해하나, 넓은 표를 새로 그릴 때 이 클래스를 안 붙이면 규격이 갈린다.

---

## §5 고쳐야 할 것 — 우선순위

### P1 — 문서 오류가 코드로 전이된 건 (DESIGN_REF와 base.css를 함께 고쳐야 함)

| # | 파일:위치 | 현재값 | 교체값 | 사유 |
|---|---|---|---|---|
| 1 | `DESIGN_REF.md` §1 그림자표 "토글 활성(shadow-sm)" 행 | `0 1px 2px 0 rgba(0,0,0,0.05)` | `0 1px 3px 0 rgba(0,0,0,0.1), 0 1px 2px -1px rgba(0,0,0,0.1)` | Tailwind v4 `--shadow-sm`(theme.css:408). 주장값은 v4 `--shadow-xs` |
| 2 | `assets/base.css:382` `.toggle-btn.active` | `box-shadow: 0 1px 2px 0 rgba(0,0,0,0.05)` | `box-shadow: 0 1px 3px 0 rgba(0,0,0,0.1), 0 1px 2px -1px rgba(0,0,0,0.1)` | 1과 동반 |
| 3 | `DESIGN_REF.md` §1 시맨틱 팔레트 표 전체 | Tailwind v3 hex 46종 | v4 oklch 환산 hex로 교체(아래 4·5의 값) | "원본은 v4 oklch, 아래는 동치 hex"라는 서술이 사실과 다름 |
| 4 | `assets/base.css:37-46` 채도 계열 토큰 | `--emerald-500 #10b981` `--emerald-600 #059669` (:38) · `--red-500 #ef4444` `--red-600 #dc2626` `--red-700 #b91c1c` (:40) · `--amber-400 #fbbf24` `--amber-600 #d97706` `--amber-700 #b45309` (:42) · `--blue-700 #1d4ed8` (:43) · `--violet-700 #6d28d9` (:44) · `--teal-700 #0f766e` (:45) · `--green-500 #22c55e` `--green-800 #166534` (:46) | `#00bc7d` `#009966` · `#fb2c36` `#e7000b` `#c10007` · `#ffb900` `#e17100` `#bb4d00` · `#1447e6` · `#7008e7` · `#00786f` · `#00c950` `#016630` | ΔE 1.43~3.86. 뱃지·토스트·차감 표시 등 상태 색이 나란히 놓이면 구분됨 |
| 4' | `assets/base.css` 토큰 미경유 hex 5건 | `:224 #92400e`(amber-800) · `:480 #6ee7b7`(emerald-300) · `:493 #991b1b`(red-800) · `:518 #f59e0b`(amber-500) · `:578 #f5f3ff`·`#ddd6fe`(violet-50/200) | `#973c00` · `#5ee9b5` · `#9f0712` · `#fe9a00` · `#f5f3ff`·`#ddd6ff` | 토큰을 거치지 않아 4를 고쳐도 남는다. ΔE — amber-500 2.92 · amber-800 1.79 · emerald-300 1.47 · red-800 2.03 · violet-200 0.28 |
| 4'' | `assets/base.css:39-40` 미정의 토큰 | `--red-400` 없음(툴팁 앵커가 `--red-500`으로 대체 중, P2 #9와 연동) | `--red-400: #ff6467` 추가 | 원본이 `border-red-400`을 쓴다 |
| 5 | `assets/base.css:34-36` 무채색 토큰 | `--gray-300 #d1d5db` `--gray-400 #9ca3af` `--gray-500 #6b7280` (:35) · `--gray-600 #4b5563` `--gray-700 #374151` `--gray-800 #1f2937` `--gray-900 #111827` (:36) | `#d1d5dc` `#99a1af` `#6a7282` · `#4a5565` `#364153` `#1e2939` `#101828` | ΔE ≤1.07(근사). 4와 함께 처리하면 팔레트가 v4로 정렬됨. `--gray-50/100/200`은 v3·v4 동일(ΔE 0)이라 유지 |

### P2 — 재현본 단독 편차

| # | 파일:위치 | 현재값 | 교체값 | 사유 |
|---|---|---|---|---|
| 6 | `assets/base.css:470` `.tooltip .tip-panel` | `line-height: 15px` | `line-height: 16.5px` (또는 `line-height: 1.5`) | 원본 `text-[11px]`은 line-height 미지정 → html 1.5 상속 = 16.5px. 툴팁 행 높이가 줄당 1.5px 좁음 |
| 7 | `assets/base.css:439` `.formula-term .t-label` | `line-height: 15px` | `line-height: 16.5px` | 6과 동일 사유 |
| 8 | `assets/base.css:394` `.filter-tab .count` | 상속(20px) | `line-height: 16px` 추가 | 원본 `text-xs`는 16px 고정 |
| 9 | `assets/base.css:464` `.tooltip .tip-anchor.red` | `border-bottom-color: var(--red-500)` | `border-bottom-color: var(--red-400)` = `#ff6467` (4'' 선행) | 원본 `PreSettlementTab.tsx:713`은 `border-red-400`. 단계 자체가 다름 |
| 10 | `assets/base.css:393` `.filter-tab.active` | `border-color: var(--primary)` 유지 | 보더 제거 또는 유지 결정 | 원본은 활성 탭에서 보더를 뺀다(`manage:231`). 현행은 활성/비활성 폭이 같아 흔들림이 없으므로 **의도적 개선이면 DESIGN_REF에 기록** |
| 11 | `assets/base.css:244` `.tbl th` | `letter-spacing: 0.05em` 상시 | 좁은 표는 제거, `.tbl.wide th`(:274)에만 유지 | 원본은 넓은 표(`manage:265`)만 `tracking-wider`, 좁은 표(`PreSettlementTab:669`)는 없음 |
| 12 | `assets/base.css:345` `.input` · `:359` `.search-input` | `color: var(--gray-900)` / 미지정(→`#000`) | 양쪽 `color: #171717` | 원본은 preflight `color: inherit` + `--foreground #171717`. 인풋 본문 색이 미세하게 진함 |
| 13 | `assets/base.css:504` `.modal-backdrop.blur` | `backdrop-filter: blur(4px)` | `blur(8px)` | v4 `backdrop-blur-sm`은 8px. **사용 화면 0건이라 사문** — 제거해도 무방 |
| 14 | `assets/base.css:546` `.modal-body label` | `font-size: 14px`(line-height 미지정 → 21px) | `line-height: 20px` 추가 | 원본 `text-sm`은 20px |
| 15 | `assets/base.css:453` `.formula-op` | `font-size: 18px`(→27px) | `line-height: 28px` 추가 | 원본 `text-lg`는 28px |

### P3 — 문서 보완 (코드 변경 없음)

| # | 파일:위치 | 조치 |
|---|---|---|
| 16 | `DESIGN_REF.md` §6 "행 hover" 행 | 근거에서 `PreSettlementTab.tsx:691` 삭제. `:691`은 확장 행 `bg-primary-50/50`이고 hover는 `hover:bg-gray-50`. `primary-50/30`의 근거는 `manage:291` 단독 |
| 17 | `DESIGN_REF.md` §7 소형 pill 행 | `manage:299` = 700 `blue-50/blue-600`, `PreSettlementTab:698` = 500 `cyan-50/cyan-700`으로 분리 기재. §1 팔레트에 cyan-50/700·blue-50/600 추가 |
| 18 | `DESIGN_REF.md` §6 테이블 헤더 행 | `tracking .05em`은 넓은 표 전용임을 명시 |
| 19 | `DESIGN_REF.md` §3 콘텐츠 패딩 행 | 근거를 `AdminLayout.tsx:582`(마진) → `app/page.tsx:40`·`manage/page.tsx:187`로 정정 |
| 20 | `DESIGN_REF.md` §1 브랜드 토큰 표 | 변수명을 `--color-primary-*`(@theme)로 정정. `:root`의 `--primary`는 별도 선언임을 병기 |
| 21 | `DESIGN_REF.md` §2 폰트 | `subsets:["latin"]`(layout.tsx:8)과 "프리로드만 제한, 한글 @font-face 497개는 번들에 포함" 사실 추가 |
| 22 | `DESIGN_REF.md` §14 폼형 모달 | 헤더 `bg-orange-50 border-orange-200` 틴트 · 컨테이너 `shadow-2xl` · 인풋 패딩 10/16 추가. 백드롭 blur를 4px → 8px 정정 |
| 23 | `DESIGN_REF.md` §5 부호값 색 | `signedTone==='cost'`에서 반전됨을 병기(`PreSettlementTab.tsx:867-868`) |
| 24 | `DESIGN_REF.md` §12 툴팁 앵커 | `inline` → `inline-block`(`:1019`) |
| 25 | `DESIGN_REF.md` §7 뱃지 색 매핑 | 미기재 2종 추가 — `NOT_TARGET` 미대상 `gray-100/gray-400`(:49), `DEDUCTED` 선정산차감 `red-100/red-700`(:48) |
| 26 | `assets/base.css:274-275` `.tbl.wide` | 사용처 0건. 넓은 표 화면이 생길 때까지 유지하되 미사용임을 주석에 명기 |

### P4 — 정책 확인 필요 (수정 대상 아님)

| # | 사안 | 내용 |
|---|---|---|
| 27 | **상단 탭바 부재** | 운영 어드민은 `TabContext.tsx:89`의 `isTabMode: true`로 모든 화면에 40px 탭바(`TabBar.tsx:11`)를 상시 렌더한다. 투자자 어드민에는 없다. 투자자용에 다중 탭 작업 개념이 필요한지 결정 필요. 불필요로 결론 나면 DESIGN_REF에 "탭바 미채택" 근거를 남길 것 |
| 28 | 인라인 대형 CTA 4종 (§4-2) | `padding:12px 40px; font-size:16px`, `width:100%; padding:12px 0` 등은 어드민 버튼 규격 밖. 투자자 화면 전용 규격으로 확정할지, `.btn-lg`·`.btn-block`으로 base.css에 승격할지 결정 |
| 29 | `border-radius:10px` 3건 | 어드민 계단(4/6/8/12/16)에 없음. 8px 또는 12px로 정렬 권고 |

---

## 부록 — 재현 절차

```
# 원본 어드민 (읽기 전용, .next 외 변경 없음)
cd /Users/semi/cursor/payhug-admin-web && npm run dev          # :3001

# 헤드리스 크롬 (창 미표시)
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --remote-debugging-port=9333 \
  --user-data-dir=<scratch>/cprofile --disable-web-security about:blank

# 프로브 (CDP Runtime.evaluate → computed style JSON)
node cdp.js "http://127.0.0.1:8903/probe.html" harness/probe.js   # 원본 유틸리티 104종
node cdp.js "http://localhost:8901/assets/components.html" p2.js  # 재현본 45종
node cdp.js "http://localhost:3001/login" pfont2.js               # 폰트 실측
```

작업 산출물(프로브 스크립트·JSON·색차 계산기)은
`/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/`
에 있으며 세션 종료 시 소멸한다.
