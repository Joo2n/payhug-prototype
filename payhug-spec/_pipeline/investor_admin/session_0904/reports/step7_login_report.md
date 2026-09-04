# 7단계 · 로그인 화면 실물 정합 보고

## 하지 않은 것 · 지시와 다르게 한 것

| 구분 | 내용 | 근거 |
|---|---|---|
| 하지 않음 | `archive.html` 재생성. `login.html` 행의 크기·시각(`3 KB` · `08-28 22:40`)이 옛 값으로 남아 있음 | `build_archive.py` 는 전 파일 행을 다시 쓰므로 다른 화면 diff 가 생깁니다. 판단 필요 |
| 하지 않음 | 검사기·생성기(`build_demo.py` 포함) 수정 | 지시 범위 밖. (마) 에 목록만 |
| 하지 않음 | 실물 레포 수정 | `payhug-admin-web` `git status --short` 0건. 캡처용 dev 서버(`:3001`)를 띄웠다 내렸으며 `.next/`(gitignore) 캐시만 갱신됨 |
| 범위 넓힘 | 문구·필드·버튼·푸터·레이아웃 외에 **배경 장식 원 3개**와 **버튼 활성 조건(두 칸 모두 입력 시 켜짐)** 도 실물대로 옮김 | `page.tsx:98-102` 장식, `:27`·`:161-166` 활성 조건. 초기 화면이 회색 버튼이라 이것을 빼면 캡처 비교가 어긋납니다. 되돌리려면 `login.html:38,92-98` · `build_app.py:2988-2991,3354-3364` 를 지우면 됩니다 |
| 유지 | `Admin` · `휴대전화번호` 는 지우지 않음 | 실물에 있음. `page.tsx:110` `PayHug <span>Admin</span>` · `:132` `휴대전화번호 또는 사업자번호` |

## (가) 실물 대 프로토타입 문구

| 자리 | 실물 (`payhug-admin-web/app/login/page.tsx`) | 옛 프로토타입 (`login.html` HEAD `f9f17dd`) | 새 프로토타입 (`login.html` · `app.html` 로그인 섹션) | 판정 |
|---|---|---|---|---|
| 제목 | `PayHug Admin` (`:110`, Admin 은 `text-primary`) | `PayHug Admin` (Admin 은 `--primary-600`) + 로고 마크 48px | `PayHug Admin` (Admin 은 `--primary`), 로고 마크 없음 | 일치 |
| 부제 | `관리자 로그인` (`:112`) | `투자자 어드민` | `관리자 로그인` | 일치 |
| 1번 필드 라벨 | `아이디` (`:119`) | `사업자등록번호 또는 휴대전화번호` | `아이디` | 일치 |
| 1번 플레이스홀더 | `휴대전화번호 또는 사업자번호` (`:132`) | `'-' 없이 숫자만 입력` | `휴대전화번호 또는 사업자번호` | 일치 |
| 1번 아이콘 | 사람 아이콘 (`:123-125`) | 없음 | 같은 path | 일치 |
| 2번 필드 라벨 | `비밀번호` (`:140`) | `비밀번호` | `비밀번호` | 일치 |
| 2번 플레이스홀더 | `비밀번호` (`:153`) | `비밀번호 입력` | `비밀번호` | 일치 |
| 2번 아이콘 | 자물쇠 아이콘 (`:144-146`) | 없음 | 같은 path | 일치 |
| 버튼 | `로그인` (`:174`) · 두 칸 비면 `bg-gray-300` (`:161-166`) | `로그인` · 항상 초록 | `로그인` · 두 칸 비면 `--gray-300`, 채우면 `--primary` | 일치 |
| 안내 | `안내:` 굵게 + ` 이 페이지는 관리자 전용입니다.` amber 상자 + 경고 아이콘 (`:180-189`) | 없음 | 같은 문구·아이콘 (`.notice.notice-amber`) | 일치 |
| 비밀번호 찾기 | 없음 | `비밀번호 찾기` (비활성 링크) | 없음 | 일치 |
| 푸터 | `© 2026 PayHug. All rights reserved.` (`:194`) | 없음 | 같은 문구, 카드 밖 | 일치 |
| 금지어 | — | `투자자` 1 · `사업자등록번호` 1 · `비밀번호 찾기` 1 | `투자자` 0 · `사업자등록번호` 0 · `비밀번호 찾기` 0 · `Admin` 1(제목) · `휴대전화번호` 1(플레이스홀더) | 실물과 같음 |

`app.html` 로그인 섹션(`app.html:1084`)의 보이는 텍스트 추출값: `PayHug` · `Admin` · `관리자 로그인` · `아이디` · `비밀번호` · `로그인` · `안내:` · `이 페이지는 관리자 전용입니다.` · `© 2026 PayHug. All rights reserved.` / 플레이스홀더 `휴대전화번호 또는 사업자번호` · `비밀번호`. `login.html` 과 동일합니다.

## (나) 고친 자리

### `/Users/semi/cursor/payhug-investor-admin/login.html`

| 줄 (새) | 옛 | 새 | 실물 근거 |
|---|---|---|---|
| 13-17 | `.login-wrap` 회색 바탕 · column · padding 40/16 | 초록 그라데이션(`primary-700→600→500`, oklab) · `overflow:hidden` · padding 0 | `page.tsx:96` |
| 18-21 | 없음 | `.login-glow` 흐린 원 3개 (320·320·384px, blur 64px) | `page.tsx:98-102` |
| 22 | 없음 | `.login-box` max-width 448px · margin 0 16px · z-index 10 | `page.tsx:104` `max-w-md mx-4` |
| 23-26 | `.login-card` max 400px · padding 36/32/28 | 흰 95% · backdrop blur 24px · radius 24px · padding 32px · shadow-2xl · border 0 | `page.tsx:106` |
| 27-30 | 로고 마크 48px + 22px 워드마크, 부제 13px | `h1` 30px/36px bold tracking -0.025em, `em` 은 `--primary`, 부제 16px/24px mt 8px, 머리 mb 32px | `page.tsx:108-113` |
| 31-35 | 라벨 13px 600 · 입력 padding 11/16 흰 바탕 | 라벨 14px 500 mb 8px · 입력 padding 14/16/14/48 · 16px/24px · `.search-input-wrap` 아이콘 20px | `page.tsx:118-134` |
| 36-38 | 버튼 padding 12 | padding 14 · 16px · `--shadow-button` · hover shadow-lg · `aria-disabled` 시 `--gray-300` | `page.tsx:162-166` |
| 39-41 | `.login-links`·`.link-off` | `.login-card .notice` padding 16 · gap 12 · amber-800 · 아이콘 20px amber-500 | `page.tsx:180-189` |
| 42 | 없음 | `.login-foot` 14px/20px 흰 60% mt 24px | `page.tsx:193` |
| 55-56 | `<span class="logo-mark">` + `<span class="wordmark">` · `투자자 어드민` | `<h1 class="wordmark">PayHug <em>Admin</em></h1>` · `관리자 로그인` | `page.tsx:109-112` |
| 60-63 | `사업자등록번호 또는 휴대전화번호` · `'-' 없이 숫자만 입력` | `아이디` · 사람 아이콘 · `휴대전화번호 또는 사업자번호` | `page.tsx:119,124,132` |
| 67-70 | `비밀번호` · `비밀번호 입력` | `비밀번호` · 자물쇠 아이콘 · `비밀번호` | `page.tsx:140,145,153` |
| 74 | `<a class="btn btn-primary login-submit" href="invest-assets.html">로그인</a>` | 같음 (문자열 유지. `build_demo.py:90` 이 이 문자열을 찾음) | `page.tsx:174` |
| 76-78 | `비밀번호 찾기` | `.notice.notice-amber` + 경고 아이콘 + `<strong>안내:</strong> 이 페이지는 관리자 전용입니다.` | `page.tsx:180-189` |
| 81 | 없음 | `<p class="login-foot">© 2026 PayHug. All rights reserved.</p>` | `page.tsx:193-195` |
| 86-107 | Enter → 무조건 제출 | 두 칸 모두 차야 `aria-disabled=false` · Enter 도 그때만 제출 | `page.tsx:27,88-92,161` |

### `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/build_app.py`

| 줄 (새) | 옛 | 새 |
|---|---|---|
| 407-437 | 로그인 CSS 19줄 (`login.html` 옛 스타일과 같은 내용) | `login.html:13-42` 와 같은 CSS 31줄 |
| 2988-2991 | `RENDER['login'] = function(){};` | 화면 진입 시 두 칸 값으로 `aria-disabled` 를 정함 |
| 3302-3308 | Enter → `sb.click()` | Enter → `loginValid()` 일 때만 `sb.click()` |
| 3354-3364 | (없음) `input` 리스너는 `[data-act]` 만 봄 | `loginValid()` 정의 · `[data-login]` 입력마다 `aria-disabled` 갱신 |

로그인 카드 HTML 은 `build_app.py:53-54` 가 `login.html` 에서 `cut()` 으로 그대로 옮기므로 별도 수정 없이 따라옵니다. 생성기에 직접 박힌 로그인 문구는 없습니다(`build_app.py:2970` 갤러리 설명 `사업자번호·휴대전화 로그인` 은 랜딩 목록의 한 줄로, 로그인 화면 밖입니다).

## (다) 재생성 결과

| 항목 | 결과 |
|---|---|
| `python3 build_app.py` | `app.html 245015 bytes / 3966 lines` · `screens in doc: 16` |
| `python3 prep_fig.py sync` | `동기화 24화면 · 원본 HEAD 1693bd3 (워킹트리 변경분 포함)`. `_fig` 에 로그인 프레임은 원래 없음(`prep_fig.py:29`) |
| 변경 범위 | 수정 전 생성기 + HEAD `login.html` 로 만든 `app_old.html` 과 새 `app.html` 의 `diff` 123줄. `login` 이 들어가지 않은 줄을 골라내도 전부 로그인 CSS·카드·스크립트 조각. **다른 화면·숫자·라벨 diff 0** |
| 정적 낱장 | `login.html` 1장만 변경. `index.html` 의 로그인 카드 설명(`사업자번호·휴대전화 로그인 폼`)은 그대로 |

git HEAD 대비 `app.html` diff 에는 `BASE_DATE 2026-08-26`·가맹점 `ty` 값 등 다른 조의 미커밋 변경분이 함께 보입니다. 위 표의 판정은 HEAD 가 아니라 수정 직전 생성기 산출물과 견준 것입니다.

## (라) 캡처·판정

| 파일 | 내용 |
|---|---|
| `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/step7_login_real.png` | 실물 `http://localhost:3001/login` 1440×900 |
| `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/step7_login.png` | 프로토타입 `login.html` 1440×900 |
| `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/step7_login_side.png` | 두 장 나란히 (왼쪽 실물 · 오른쪽 프로토타입) |
| `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/step7_login_diffmask.png` | 채널 차 40 초과 픽셀 마스크 |

| 판정 항목 | 값 |
|---|---|
| 픽셀 차 8 초과 | **0 / 1,296,000 (0.00%)** |
| 픽셀 차 40 초과 | **0** |
| 카드 폭·위치 | 둘 다 x 497~943 · y 179~678 |
| 버튼 초기 상태 | 둘 다 회색(`gray-300`) |
| 글꼴 | 실물 next/font Noto Sans KR · 프로토타입 Google Fonts Noto Sans KR. 캡처상 차이 없음 |

동작 확인(헤드리스, 같은 출처 하네스): `app.html` 초기 `aria-disabled=true` → 한 칸 입력 `true` → 두 칸 입력 `false` → Enter·클릭 모두 `invest-assets` 로 이동. `login.html` 도 같고 빈 상태 Enter 는 그 자리에 머뭅니다.

## (마) 검사기 갱신 목록

로그인 문구를 기대하는 검사기는 없습니다. 로그인을 언급하는 자리는 아래이며 전부 화면 목록·문자열 앵커라 갱신 대상이 아닙니다.

| 파일:줄 | 내용 | 영향 |
|---|---|---|
| `verify_app.js:383,739` | 화면 목록 `['login','default']` | 없음 |
| `verify_proto.js:433,705,742,786` | 화면 목록 `['login','default']` | 없음 |
| `build_demo.py:43` | `RENDER['login']` 문자열 위치 | 유지됨 |
| `build_demo.py:90-92` | `<a class="btn btn-primary login-submit" href="invest-assets.html">` 치환 | 문자열 유지됨 |
| `build_index.py:53` · `build_app.py:2970` | 랜딩 갤러리 설명 `사업자번호·휴대전화 로그인` | 로그인 화면 밖 |

검사기 실행 결과

| 검사기 | 결과 | 로그인 관련 |
|---|---|---|
| `verify_app.js` (새 `app.html`) | 판정 101 · PASS 98 · FAIL 3 · 콘솔 에러 0 · 죽은 컨트롤 0/112 · 미도달 컨트롤 0 | `login/default PASS h=1113` |
| `verify_app.js` (수정 전 `app_old.html`, 같은 검사기 사본) | 판정 101 · PASS 98 · FAIL 3 · 죽은 컨트롤 0/113 | FAIL 3건이 새 결과와 동일: `R.data[4]` 기간 합계 재계산 · `R.data[6]` 날짜 입력 · `R.tyWire[0]` ⑤ 정의. 로그인과 무관한 기존 상태 |
| `verify_proto.js` (정적 낱장) | 판정 135 · PASS 122 · FAIL 13 · 콘솔 에러 0 · 죽은 컨트롤 0 | FAIL 13건 전부 `R.numbers.items[3~17]` 투자 수익 ④⑤·W·Ty·엑셀 값. 로그인 화면 항목 없음 |

죽은 컨트롤 검사 건수가 113→112 인 것은 로그인 버튼이 초기 `aria-disabled=true` 라 검사 풀에서 빠지기 때문입니다(`verify_app.js:405`). 실제 이동은 위 (라) 하네스로 확인했습니다.
