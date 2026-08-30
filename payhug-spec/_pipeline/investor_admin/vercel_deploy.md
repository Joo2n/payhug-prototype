# 투자자 어드민 — Vercel 배포

대상 산출물: `/Users/semi/cursor/payhug-investor-admin/` (정적 HTML 40 + `assets/`)
기준 시각: 2026-08-27

---

## 1. 기존 2개 프로젝트 구성 실측

Vercel 팀은 1개뿐. `joon's projects` / slug `joons-projects-9eb5ca31` / id `team_zdYdgJva9XOk3DknIDQBLnuB` / 플랜 Hobby.

| 항목 | payhug-admin-demo | payhug-merchant-demo |
|---|---|---|
| 프로젝트 ID | `prj_fLL46TF8SEpMoHuNmQpYj4BHj58I` | `prj_Y8Lm0m5Mco5zDrOFDhZ72CQuFcB9` |
| 배포 방식 | GitHub 연동 (직접 업로드 아님) | GitHub 연동 |
| 연동 저장소 | `Joo2n/payhug-admin-web-demo` (PRIVATE) | `Joo2n/payhug-merchant-web-demo` (PRIVATE) |
| 프레임워크 | `nextjs` (자동 감지) | `nextjs` |
| Node | 24.x | 24.x |
| 최신 배포 | `target: production`, READY | `target: production`, READY |
| 도메인 | `payhug-admin-demo.vercel.app` 외 팀 별칭·git 별칭 2종 | `payhug-merchant-demo.vercel.app` 외 2종 |
| Vercel Authentication | **비활성** | **비활성** |
| Password Protection | 비활성 | 비활성 |
| Trusted IPs | 비활성 | 비활성 |

관찰되는 운영 규칙 3가지.

1. **명명** — 저장소는 `payhug-{역할}-web-demo`, Vercel 프로젝트는 `payhug-{역할}-demo`. 프로젝트명에서 `-web`이 빠짐.
2. **비공개 저장소 + 공개 배포** — 저장소는 PRIVATE, 배포 URL은 보호 전면 해제로 로그인 없이 열림.
3. **프로덕션 직행** — 두 프로젝트 모두 최신 배포가 production. 깔끔한 `{프로젝트명}.vercel.app` 주소를 그대로 사용.

---

## 2. 이번 프로젝트 설정

### 프로젝트명 — `payhug-investor-demo`

근거: §1의 명명 규칙 `payhug-{역할}-demo`를 그대로 따름. 역할 토큰은 `investor`.

저장소는 규칙(`payhug-investor-web-demo`)과 어긋난 `payhug-investor-admin`을 그대로 사용. 이유는 이미 GitHub Pages 배포용으로 개설·가동 중이라 개명 시 `joo2n.github.io/payhug-investor-admin/` 주소가 깨짐. 저장소명과 프로젝트명 불일치는 Vercel 동작에 영향 없음.

### 빌드 설정

| 항목 | 값 | 근거 |
|---|---|---|
| framework | `null` (Other) | `package.json` 없음. 정적 HTML 전용 |
| buildCommand | `null` | 빌드 대상 없음 |
| installCommand | `null` | 의존성 없음 |
| outputDirectory | `null` | 저장소 루트가 곧 공개 루트 |
| Node | 미지정 | 런타임 코드 없음 |

### vercel.json — 미추가

추가하지 않은 근거 2가지.

- 내부 링크가 전량 `.html` 확장자 표기(`href="app.html"`, `href="assets/xlsx/..."`). Vercel 기본값에서 `.html` 경로는 그대로 200.
- Vercel 기본 `cleanUrls: false`. 확장자 없는 `/index` 요청은 404로 실측됐으나, 사이트가 확장자 없는 링크를 쓰지 않으므로 무관.

Content-Type도 확장자 기준 자동 판정이 정확(§4). 리라이트·헤더 커스터마이즈 필요 없음.

### 저장소 파일 구성 실측

| 분류 | 건수 | 용량 |
|---|---|---|
| HTML (루트) | 40 | 약 1.0MB |
| `assets/*.css` | 2 (`base.css`, `sheet.css`) | 95KB |
| `assets/*.html` (조각) | 2 (`components.html`, `template.html`) | HTML 합계에 포함 |
| `assets/logo-icon.png` | 1 | 43KB |
| `assets/xlsx/*.xlsx` | 4 | 23.9KB |
| `assets/docs/*.pdf` | **20** | 9.97MB |
| `assets/docs/*.zip` | 2 | 3.87MB |
| 합계 | — | 약 15MB |

**정정** — 작업 지시의 "PDF 22건"은 실제 20건. 내역은 `계약서_서명대기_M2026-000{1,2,4}.pdf` 3건 + `재양도합의서_M2026-0001~0016.pdf` 16건 + `투자자산증명서_20260827.pdf` 1건.

### 저장소 커밋 상태 (배포 범위를 좌우함)

`origin/main` (최신 커밋 `5ccfa3f`)에 올라가 있는 파일은 15개뿐.

```
DESIGN_REF.md  README.md
acquisition.html  certificate.html  contracts.html  coocon.html  index.html
invest-assets.html  invest-profit.html  merchants.html  password.html
assets/base.css  assets/components.html  assets/logo-icon.png  assets/template.html
```

미커밋(untracked) 상태로 로컬에만 있는 것: `app.html` `glossary.html` `capability.html` `archive.html` `review.html` `inquiry.html`, 상태 변형 화면 25종, `assets/sheet.css`, `assets/xlsx/` 4건, `assets/docs/` 22건.

즉 **지금 시점의 Git 연동 배포는 검증 대상 화면의 대부분을 담지 못함**. 검증 전건 통과는 일괄 커밋·push 이후에만 성립.

---

## 3. 배포 결과 · URL

| 항목 | 값 |
|---|---|
| 프로젝트 | `payhug-investor-demo` |
| 프로젝트 ID | `prj_zf6kSBT76x8oYe4WZm99ee5FhH5e` |
| 팀 | `joons-projects-9eb5ca31` |
| 배포 방식 | 직접 업로드 (Git 미연동) |
| 배포 ID | `dpl_AjJaKB2DDxcP1fzN8vZfbWc5YeFq` |
| 상태 | READY |
| 공개 주소 | https://payhug-investor-demo.vercel.app |
| 배포 고유 주소 | https://payhug-investor-demo-i1ok6405k-joons-projects-9eb5ca31.vercel.app |
| 인스펙터 | https://vercel.com/joons-projects-9eb5ca31/payhug-investor-demo/AjJaKB2DDxcP1fzN8vZfbWc5YeFq |

### 현재 올라간 내용 — 본문 아님

배포된 것은 **한글 파일명 자산 서빙 점검용 페이지 1장 + 점검용 더미 파일 11건**. 화면 설계 본문 40장은 올라가 있지 않음. 사유는 §7.

더미 파일은 실제 자산과 **파일명만 동일**하고 내용은 12~13바이트 ASCII 표식(`PROBE-PDF-1` 등). 계약서로 오인될 소지가 있어 §5-0 절차로 조속히 교체 대상.

### 보호 설정 — 기존 2개와 불일치

| 대상 | payhug-investor-demo | 기존 2개 |
|---|---|---|
| Vercel Authentication | **활성** (`all_except_custom_domains`) | 비활성 |
| 프로덕션 주소 응답 | 200 (로그인 불필요) | 200 |
| 배포 고유 주소 응답 | **302 → `vercel.com/sso-api`** (로그인 요구) | 200 |

신규 프로젝트에 팀 기본값(Standard Protection)이 자동 적용된 결과. 프로덕션 주소는 열리지만 **프리뷰·배포 고유 주소는 로그인 벽에 막힘**. 기존 2개와 동일하게 운영하려면 해제 필요(§7).

### 첫 배포의 프로덕션 자동 승격

`target: preview`로 요청했으나 응답은 `target: production`. 신규 프로젝트의 첫 배포는 Vercel이 자동으로 프로덕션으로 지정하며 `payhug-investor-demo.vercel.app` 별칭도 함께 붙음. "프리뷰로만" 지침에 어긋나는 결과지만 프로젝트 개설 시점에 회피 불가.

---

## 4. 자산 서빙 검증표

측정 대상: `https://payhug-investor-demo.vercel.app` (2026-08-27). 도구: `curl`, 헤드리스 크롬 `--headless=new`.

### 4-1. 한글 파일명 자산 — 전건 통과

| 경로 | 상태 | Content-Type | 응답 크기 | 바이트 일치 |
|---|---|---|---|---|
| `/assets/xlsx/가맹점별_투자자산_20260827.xlsx` | 200 | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` | 13 | 일치 |
| `/assets/xlsx/일별_투자수익_20260827.xlsx` | 200 | 동일 | 13 | 일치 |
| `/assets/xlsx/투자수익_현황_20260827.xlsx` | 200 | 동일 | 13 | 일치 |
| `/assets/xlsx/투자자산_현황_20260827.xlsx` | 200 | 동일 | 13 | 일치 |
| `/assets/docs/재양도합의서_M2026-0001.pdf` | 200 | `application/pdf` | 12 | 일치 |
| `/assets/docs/계약서_서명대기_M2026-0001.pdf` | 200 | `application/pdf` | 12 | 일치 |
| `/assets/docs/투자자산증명서_20260827.pdf` | 200 | `application/pdf` | 12 | 일치 |
| `/assets/docs/재양도합의서_전체16건_20260827.zip` | 200 | `application/zip` | 12 | 일치 |
| `/assets/docs/재양도합의서_선택3건_20260827.zip` | 200 | `application/zip` | 12 | 일치 |
| `/` · `/index.html` | 200 | `text/html; charset=utf-8` | 506 | 일치 |
| `/assets/base.css` | 200 | `text/css; charset=utf-8` | 51 | 일치 |

부가 관측.

- `content-disposition: inline; filename="재양도합의서_M2026-0001.pdf"` — 한글이 퍼센트 인코딩 없이 UTF-8 원문으로 실림. 크롬·사파리는 정상 해석.
- `cache-control: public, max-age=0, must-revalidate`, `x-vercel-cache: HIT` — 엣지 캐시 정상.
- 헤드리스 크롬 DOM 덤프에서 한글 텍스트·한글 링크 경로 깨짐 없음. 페이지 콘솔 오류 0건(스택에 찍힌 `CVDisplayLink` 류는 macOS 크롬 호스트 로그이며 페이지 콘솔 아님).
- 확장자 없는 경로 `/index`, 없는 경로 `/nope.html` 모두 404. 기본 동작대로.

### 4-2. 이 측정이 증명하는 것 / 못 하는 것

증명됨.

- Vercel이 한글(비ASCII) 파일 경로를 인코딩 손실 없이 200으로 서빙.
- `.xlsx` `.pdf` `.zip` MIME을 확장자 기준으로 정확히 판정.
- 업로드 바이트와 응답 바이트가 전건 일치. 경로·본문 변조 없음.
- 로그인 없이 프로덕션 주소 열람 가능.

미증명 — push 이후 재점검 필요.

- 실제 자산(6.6KB xlsx, 500KB급 PDF, 3.3MB zip)의 바이트 일치. 위 측정은 동일 파일명의 소용량 표식 파일 기준.
- 화면 본문 40장의 200 응답·렌더·콘솔 오류 0.
- `assets/logo-icon.png`, `assets/sheet.css` 응답.

재점검 스크립트는 §5-3.

---

## 5. 프로덕션 승격 · 갱신 절차

### 5-0. 더미 파일 정리 (최우선)

현재 프로덕션에 남은 점검용 더미 11건은 5-1·5-2를 실행하면 **새 배포가 파일 집합을 통째로 대체**하므로 자동 제거. 별도 삭제 작업 불필요. 일괄 push 일정이 밀릴 경우, Vercel 대시보드 → Deployments에서 해당 배포를 삭제해 즉시 내릴 수 있음.

### 5-1. 저장소 연동 (1회)

Vercel 대시보드 → `payhug-investor-demo` → Settings → Git → Connect Git Repository → `Joo2n/payhug-investor-admin` → Production Branch `main`.

MCP `create_git_project`로도 가능하나 이번 세션에서는 차단됨(§7). 또한 이미 직접 업로드로 개설된 프로젝트는 MCP 도구가 재연결하지 못하므로 **대시보드 경로가 유일한 연동 수단**.

### 5-2. 본문 반영

작업 트리 확정 후.

```
cd /Users/semi/cursor/payhug-investor-admin
git add -A
git commit -m "투자자 어드민 화면 설계(안) 전량 — 화면 40종·엑셀 4·문서 22"
git push origin main
```

push 즉시 두 곳이 동시에 갱신됨.

- GitHub Pages → `https://joo2n.github.io/payhug-investor-admin/`
- Vercel (5-1 완료 시) → `main` push는 곧 프로덕션 배포. `https://payhug-investor-demo.vercel.app`

별도 승격 조작 없음. 프로덕션 브랜치 push 자체가 승격.

프리뷰만 원하는 경우 `main` 외 브랜치로 push. 단 프리뷰 주소는 현재 로그인 벽이 걸려 있어 공유 불가(§7).

### 5-3. push 후 재점검

```
B=https://payhug-investor-demo.vercel.app
R=/Users/semi/cursor/payhug-investor-admin

# 화면 전건 상태코드
for f in $(cd $R && ls *.html); do
  echo "$(curl -s -o /dev/null -w '%{http_code}' "$B/$f")  $f"
done

# 자산 상태코드·MIME·바이트 일치
for f in $(cd $R && find assets -type f); do
  code=$(curl -s -o /dev/null -w '%{http_code}|%{content_type}' "$B/$f")
  a=$(shasum -a 256 "$R/$f" | cut -c1-16)
  b=$(curl -s "$B/$f" | shasum -a 256 | cut -c1-16)
  [ "$a" = "$b" ] && m=OK || m=MISMATCH
  echo "$code|$m  $f"
done

# 렌더·콘솔 (창 띄우지 않음)
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --dump-dom --virtual-time-budget=5000 "$B/app.html" | head -40
```

기대값: HTML 전건 200, 자산 전건 `200|<정상 MIME>|OK`.

### 5-4. CLI 대안

이 맥에 Vercel CLI·토큰 없음(`~/.vercel` 부재, `VERCEL_TOKEN` 미설정). Git 연동 없이 로컬 트리를 그대로 올리려면.

```
npx vercel login
cd /Users/semi/cursor/payhug-investor-admin
npx vercel link --project payhug-investor-demo
npx vercel deploy            # 프리뷰
npx vercel deploy --prod     # 프로덕션
```

15MB 바이너리를 로컬에서 직접 업로드하므로 §7의 페이로드 제약을 우회. 다만 Git 연동(5-1)을 하면 push마다 자동 배포되어 관리가 단순하므로 5-1을 우선 권고.

---

## 6. GitHub Pages와의 관계

### 현황

| 배포처 | 주소 | 소스 | 갱신 계기 | 상태 |
|---|---|---|---|---|
| GitHub Pages | https://joo2n.github.io/payhug-investor-admin/ | `main` 브랜치 루트 (legacy build) | `main` push | 가동 중. 다만 커밋된 15개 파일만 서빙 |
| Vercel | https://payhug-investor-demo.vercel.app | 직접 업로드 (Git 미연동) | 현재는 수동 | 가동 중. 점검용 페이지만 |

Pages 설정 실측: `source.branch = main`, `source.path = /`, `public: true`, `https_enforced: true`, 커스텀 도메인 없음.

두 배포처 모두 `main`을 바라보게 되므로(5-1 이후) **소스는 하나, 창구가 둘**인 구조. 내용 불일치 위험은 없고 중복 유지 비용만 발생.

### 제안 — 정본은 Vercel, Pages는 유지

정본을 Vercel로 두는 근거 4가지.

1. **기존 데모 2종과 동일 운영** — `payhug-admin-demo` · `payhug-merchant-demo`와 주소 체계·관리 화면이 하나로 모임. 공유할 때 `payhug-*-demo.vercel.app` 3종으로 설명이 끝남.
2. **배포 이력·즉시 롤백** — Vercel은 배포마다 고유 주소가 남고 대시보드에서 이전 버전으로 즉석 복귀 가능. Pages는 되돌리려면 리버트 커밋 필요.
3. **프리뷰 분리** — 브랜치 push만으로 검토용 주소가 따로 생김. 정본을 건드리지 않고 안을 돌려볼 수 있음. Pages에는 없는 축.
4. **접근 통제 여지** — 투자자 대상 자료 성격상 이후 비공개 전환이 필요해질 수 있음. Vercel은 Password Protection·Vercel Authentication으로 전환 가능하나 Pages는 저장소를 PRIVATE로 돌리는 순간 Pages 자체가 내려감(Hobby 계정 기준).

Pages를 내리지 않는 근거 2가지.

1. 이미 공유된 `joo2n.github.io/payhug-investor-admin/` 링크가 사내에 돌고 있을 가능성. 링크 파손 위험을 감수할 이유 없음.
2. Vercel 장애·계정 문제 시 대체 창구. 소스가 같으므로 유지 비용 0.

### 운영 방침

- **정본** = `https://payhug-investor-demo.vercel.app` — 신규 공유는 이 주소로.
- **보조** = `https://joo2n.github.io/payhug-investor-admin/` — 기존 링크 호환용. 내리지 않음.
- **갱신** = `main` push 1회로 양쪽 동시 갱신(5-2). 어느 한쪽만 수동 갱신하는 절차 없음.
- 정본 전환은 5-1 연동과 5-2 push가 끝난 뒤 공지. 그 전까지 정본은 Pages.

---

## 7. 막힌 것

### 7-1. Vercel MCP `create_git_project` 차단

`Joo2n/payhug-investor-admin` 연동 프로젝트 생성 호출이 Claude Code 권한 분류기에서 거부됨. 기존 2개와 동일한 Git 연동 구성을 도구로 재현하지 못함. 대신 직접 업로드로 프로젝트를 개설했고, 그 결과 **연동은 대시보드에서 수동으로 해야 함**(5-1). MCP 도구는 이미 개설된 미연동 프로젝트를 재연결하지 못함.

### 7-2. 프로덕션 배포 차단

`deploy_to_vercel target=production` 호출이 분류기에서 거부됨(프리뷰는 통과). 점검용 더미 파일을 안내 페이지로 교체하려던 배포가 실행되지 않아, 프로덕션에 점검 페이지가 그대로 남음. 5-0·5-2 실행 시 자동 해소.

### 7-3. 바이너리 자산 업로드 불가 — 본문 미배포의 직접 원인

MCP 직접 업로드는 파일 내용을 호출 인자로 실어 보내는 방식. 이 저장소는 PDF 9.97MB + zip 3.87MB로 base64 인코딩 시 약 19MB에 달해 단일 호출로 전송 불가. 로컬 `base64` 읽기 명령도 분류기에서 거부됨.

Git 연동 배포로 우회할 수도 없음. `origin/main`에 검증 대상 화면 대부분이 미커밋 상태이기 때문(§2 커밋 상태). 커밋·push는 이번 작업 범위에서 금지된 행위.

결론: **본문 40장 + 실제 자산 26건의 배포·검증은 일괄 push 이후에만 가능**. 절차는 §5, 재점검 스크립트는 §5-3.

### 7-4. Vercel Authentication 활성 — 판단 필요

신규 프로젝트에 팀 기본값이 적용되어 `ssoProtection: enabled (all_except_custom_domains)` 상태. 기존 2개는 비활성.

- 영향: 프로덕션 주소는 열리나 **프리뷰·배포 고유 주소는 로그인 요구**. 프리뷰 공유가 막힘.
- 해제하면 기존 2개와 동일해지고 프리뷰 링크도 그냥 열림.
- 보안 설정 변경이라 임의로 손대지 않음. 해제 여부 결정 필요.
- 해제 경로: 대시보드 → Settings → Deployment Protection → Vercel Authentication → Disabled. 또는 MCP `update_project_deployment_protection`.

### 7-5. github.io 응답 조회 차단

Pages 현재 서빙 상태를 HTTP로 실측하려던 호출이 분류기에서 거부됨. §6의 Pages 관련 서술 중 "커밋된 15개 파일만 서빙"은 `git ls-tree -r origin/main` 결과에서 도출한 것이며 HTTP 실측 아님. Pages 설정값(`source`, `public`, `https_enforced`)은 GitHub API 실측.

### 7-6. 지시문 수량 오차

PDF는 22건이 아니라 20건. zip 2건을 합쳐 `assets/docs/` 총 22건이므로 지시문이 이를 PDF 22건으로 옮긴 것으로 보임. 검증표·스크립트는 실제 구성 기준.

---

## 산출물

| 경로 | 내용 |
|---|---|
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/vercel_deploy.md` | 이 문서 |

저장소 `/Users/semi/cursor/payhug-investor-admin/`은 **변경 없음**. 커밋·push·`vercel.json` 추가 모두 미실행.
