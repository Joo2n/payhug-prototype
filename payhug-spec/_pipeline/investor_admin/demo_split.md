# 시연용 프로토타입 분리 배포

제3자에게 링크 하나만 건네면 조작 가능한 프로토타입만 열리고, 용어 해설·문의서·구현가능성·아카이브·순차확인으로 가는 통로가 없는 상태를 만든 구성이다.

같은 저장소의 하위 폴더로 나누면 상위 경로를 직접 치는 것으로 나머지가 전부 드러난다. 그래서 **저장소를 물리적으로 분리**했다. 시연본 저장소에는 문제의 문서들이 링크가 없는 정도가 아니라 **파일 자체가 없다**.

---

## §1 저장소 구성

| 항목 | 값 |
|---|---|
| GitHub | https://github.com/Joo2n/payhug-investor-prototype — **public** |
| Vercel 프로젝트 | `payhug-investor-prototype` / `prj_7YUUDe3mxtArwSDV2Zi98H4zBatk` |
| Vercel 팀 | `joons-projects-9eb5ca31` / `team_zdYdgJva9XOk3DknIDQBLnuB` |
| 공개 주소 | https://payhug-investor-prototype.vercel.app/ |
| 로컬 | `/Users/semi/cursor/payhug-investor-prototype` |
| framework | 없음(정적). buildCommand·installCommand·outputDirectory 전부 미지정 |
| 파일 | **30건 · 13.3 MB** |

### 이름

기존 규칙은 저장소 `payhug-{역할}-web-demo` · Vercel 프로젝트 `payhug-{역할}-demo`다. 이번에는 저장소와 프로젝트를 `payhug-investor-prototype` 하나로 맞췄다. 근거 둘.

- `payhug-investor-demo`는 이미 `payhug-investor-admin`(화면 설계 전체)에 붙어 있다. 같은 이름을 쓸 수 없다.
- 이 산출물은 화면 설계 전체가 아니라 통합 프로토타입 한 벌이다. `-prototype`이 내용과 일치한다.

### 파일 목록 (원격 트리 실측 `git/trees/main?recursive=1` = 30 blob)

| 경로 | 건수 | 비고 |
|---|---|---|
| `index.html` | 1 | 진입점. `app.html`을 변환해 찍어 낸 사본 |
| `README.md` | 1 | 시연용이라는 것 · 주소 · index.html 직접 수정 금지 |
| `assets/base.css` `assets/sheet.css` | 2 | 별도 저장소라 상위 참조가 불가능해 복사 |
| `assets/xlsx/*.xlsx` | 4 | 엑셀 버튼이 실제로 내려주는 파일 |
| `assets/docs/*.pdf` | 20 | 증명서 1 · 계약서 서명대기 3 · 재양도합의서 16 |
| `assets/docs/*.zip` | 2 | 재양도합의서 전체 16건 · 선택 3건 |

자산은 손으로 고르지 않는다. `scripts/sync_prototype.py`가 산출물 문서에서 `XLSX` 표·`CONTRACTS`·`SIGNQ`·`CERT_PDF`·`CT_ZIP_*`·`<link rel=stylesheet>`를 역산해 목록을 만든다. 참조가 0건인 파일은 목록에 오르지 않으므로 복사되지 않는다. `logo-icon.png`(로고는 `base.css`의 data URI로 그린다)·`template.html`·`components.html`이 그렇게 빠졌다.

### 담지 않은 것

`glossary` `capability` `feasibility` `inquiry` `archive` `review` 6종, 랜딩 `index`, 정적 화면 낱장 34종, `xls-*.html` 4종, `DESIGN_REF.md`, `_pipeline` 산출물 일체. 원본 저장소에만 있다.

경로 직접 조회 실측 — 전부 404다.

```
glossary.html 404 · capability.html 404 · feasibility.html 404 · inquiry.html 404
archive.html 404 · review.html 404 · app.html 404 · invest-assets.html 404
DESIGN_REF.md 404 · assets/ 404
```

---

## §2 끊은 통로

`index.html`은 손으로 고친 결과물이 아니라 `app.html`에서 변환해 찍어 낸 것이다. 아래 처리는 동기화할 때마다 처음부터 다시 적용된다.

| # | 대상 | 처리 | 근거 |
|---|---|---|---|
| 1 | 랜딩 갤러리 화면 `data-screen="index"` | `<section>`·`RENDER['index']`·`GALLERY` 배열·전용 CSS 35줄 제거 | 화면 목록 카드가 있는 뷰. 시연 대상이 아니다 |
| 2 | 화면 레지스터 6곳의 `index` 키 | `MENU_OF`·`STANDALONE`·`STATE_META`·`SCREEN_LABEL`·`SCREEN_ORDER`·`FILE2SCREEN`에서 제거 | 도크 화면 목록에도 뜨지 않게 |
| 3 | 사이드바 로고 → 랜딩 이동 | 핸들러 `if(t.closest('.sidebar-logo a')) go('index')` 삭제. `<a href="index.html" data-nav="invest-assets">`로 교체 | 자기 자신 안의 메인 화면(투자 자산)으로만 간다. 죽은 컨트롤을 만들지 않기 위해 비활성이 아니라 홈 이동으로 살렸다 |
| 4 | 형제 문서 상대링크 15건 | `href="<파일>.html"` → `href="#<화면>"`. `FILE2SCREEN`·`STATEFILE` 표를 문서에서 파싱해 대응시킨다 | 존재하지 않는 형제 파일을 부르지 않는다. 가운데 클릭·새 탭으로도 문서를 못 벗어난다 |
| 5 | 해시 클릭 처리 | 클릭 핸들러의 `#` 분기 첫머리에 `if(SEC(tg[0])){ go(tg[0], tg[1]); return; }` 삽입 | #4로 바뀐 링크가 안내 토스트 대신 실제로 화면을 넘기게 |
| 6 | 머리말 주석 | 개별 HTML 34개 언급을 지우고 시연본 설명으로 교체 | 없는 파일을 가리키지 않게 |

### 문자열 잔존 — 0건

`glossary` `capability` `feasibility` `inquiry` `archive` `review` 대소문자 무시 검색 0건. `랜딩` `갤러리` `문의서` 0건. `'index'`·`"index"` 0건. 형제 문서 상대링크 0건.

### 남긴 외부 링크 — 1건

쿠콘 `https://www.we-bank.co.kr/main_00100.act` (`target=_blank`, 이동 확인 모달 경유). 다른 산출물로 가는 통로가 아니라 원본 어드민에도 있는 화면 기능이라 그대로 둔다. 폰트 2건(`fonts.googleapis.com`·`fonts.gstatic.com`)이 함께 허용 목록에 있다.

---

## §3 검증

창을 띄우지 않는다(`--headless=new`). 대상은 화면 지적 12건이 반영된 최종 `app.html`(FAB 제거·임의 안내 문구 정리·용어 안내 제거·페이지네이션 정렬·서명 버튼 위치 교정·조회 필터 정리)에서 찍어 낸 배포본이다.

- `gate_prototype.js` — 동기화 때마다 도는 게이트. 화면 이동을 `go()`로 몰아 버튼 구성이 바뀌어도 흔들리지 않는다
- `verify_proto.js` — 클릭 시퀀스까지 재현하는 깊은 검증. 필요할 때만 수동

### 게이트 (로컬 · 배포 URL 양쪽 동일 결과)

| 항목 | 결과 |
|---|---|
| 화면 13 · 상태 18 전건 렌더 | PASS (높이 200px 이상 · `data-state` 일치) |
| 사이드바 메뉴 7 클릭 전환 | PASS (`body[data-active]` 일치 · 사이드바 유지) |
| 로고 → 자기 자신 메인 | PASS (`href=index.html` · 클릭 후 `view=invest-assets`) |
| 형제 문서 링크 | **0건** |
| 금칙 문자열 링크 | **0건** |
| 허용 밖 외부 호스트 | **0건** (링크 총 282 = 해시 211 · 자산 39 · 외부 `www.we-bank.co.kr`) |
| 엑셀 4종 실물 | PASS — 5,960 / 6,743 / 5,727 / 6,098 B, 전건 원본 바이트 일치 |
| 가로 오버플로 | 0 |
| 콘솔 에러 | 0 |
| 비중 합 | 100.0% |
| 투자실행금 화면 간 일치 | 1,523,100,000 |
| 일별 원장 = 월별 롤업 | 35,307,250 = 35,307,250 |
| 투자자산 대비 Ty수익율 ⑤ | 2.24% |

### 깊은 검증 (배포 URL 대상 · PASS 62 · FAIL 0 · SKIP 1)

| 항목 | 결과 |
|---|---|
| 메뉴 7 — 클릭 · 활성 배경색 `rgb(127,225,65)` · 그룹 라벨 | 7/7 PASS |
| 상태 18 — 실제 클릭 시퀀스 도달 | 18/18 PASS |
| 엑셀 4 — 중간 화면 없이 즉시 · 바이트 일치 | 4/4 PASS |
| 증명서 PDF | PASS 372,443 B |
| 재양도합의서 전체 16건 zip | PASS 3,260,815 B |
| 레이아웃 31조합 (모달·서명 액션바 포함) | 31/31 PASS |
| 죽은 컨트롤 | **0 / 검사 132건** |
| 키보드·보조기술 미도달 컨트롤 | 0 |
| 콘솔 에러 | 0 |
| 정렬·필터 값 변화 11항 | **SKIP** — 조회 필터 개편으로 `어제` 프리셋이 사라져 이 검증 대본의 셀렉터가 맞지 않는다. 남은 프리셋은 `week`·`month`. 시연본 분리와 무관한, 원본 화면 개편 사안이다 |

FAB(화면·상태 이동 도크)가 사라졌으므로 두 상태(`invest-assets/empty`·`contracts/empty`)는 해시 딥링크로 닿게 대본을 고쳤다. 서명 액션바는 고정 푸터에서 정산채권 양수 화면 안으로 들어왔으므로 판정 기준을 `hidden` 속성에서 실제 표시 여부로 바꿨다.

### 숫자가 안 움직였다는 근거

문자열 대조보다 강한 근거를 썼다. `app.html`과 `index.html`의 `<script>` 구간을 통째로 비교하면 차이가 레지스터 6줄·링크 2줄·갤러리 블록 제거·해시 분기 1줄뿐이다. **데이터 배열과 계산 함수는 한 글자도 다르지 않다.** 자산 파일은 바이트 단위로 같다.

---

## §4 배포 URL 실측

| 주소 | 상태 |
|---|---|
| https://payhug-investor-prototype.vercel.app/ | **200** `text/html` 162,666 B |
| https://payhug-investor-prototype.vercel.app/index.html | 200 (같은 문서) |
| https://payhug-investor-prototype.vercel.app/assets/base.css | 200 `text/css` 89,853 B |

- 최신 배포 `dpl_B6LUTx64v2rGfwXSiXKUQesjQTT5` 이후 동기화 커밋으로 재배포. `target: production`, READY
- 별칭 3종 — `payhug-investor-prototype.vercel.app` · `-joons-projects-9eb5ca31` · `-git-main-joons-projects-9eb5ca31`
- **Vercel Authentication 꺼짐** — 인증 없는 `curl`이 200과 실제 본문을 받는다(SSO가 켜져 있으면 401 인증 페이지가 온다). `create_git_project`로 만든 새 프로젝트는 처음부터 꺼진 상태다
- 로그인 요구·비밀번호 보호·Trusted IPs 전부 없음

GitHub Pages는 이 저장소에 켜지 않았다. Vercel 하나로 끝내고 주소를 하나만 남긴다.

---

## §5 자동화 구성

저장소가 둘로 갈리면 자동 반영이 되지 않는다. `payhug-investor-admin/app.html`을 고쳐도 시연본은 그대로다. 사람이 기억해서 옮기는 구조를 없애기 위해 **원본 저장소의 GitHub Actions가 시연본을 갱신**하게 묶었다.

```
app.html 수정 → main push → (Actions) 변환·통로 차단·검사 → 시연본 저장소 push → Vercel 자동 배포
```

### 워크플로

| 항목 | 값 |
|---|---|
| 파일 | `payhug-investor-admin/.github/workflows/sync-prototype.yml` |
| 이름 | 시연용 프로토타입 동기화 (`gh workflow list` 에 `active`, id `344348742`) |
| 트리거 | `main` push 중 `app.html` · `assets/**` · `scripts/sync_prototype.py` · 워크플로 자신이 바뀐 경우 + 수동 `workflow_dispatch` |
| 동시 실행 | `concurrency: sync-prototype` — 겹쳐 돌지 않는다 |
| 권한 | 원본 저장소는 `contents: read`. 쓰기는 시연본 저장소에만, 시크릿 토큰으로 |

경로 필터를 둔 이유 — 이 저장소는 화면 낱장·설명 문서 커밋이 잦다. 시연본과 무관한 커밋마다 도는 것은 낭비다. 시연본 결과물에 실제로 영향을 주는 파일은 `app.html`과 `assets/` 둘뿐이다.

변환 로직은 YAML에 박지 않았다. `payhug-investor-admin/scripts/sync_prototype.py` 한 파일이 갖고, 워크플로는 그것을 부른다. 로컬에서 같은 명령을 돌려 같은 결과를 얻을 수 있다.

### 단계와 실패 조건

| 단계 | 하는 일 | 실패하면 |
|---|---|---|
| 1 토큰 확인 | 시크릿 `PROTOTYPE_SYNC_TOKEN` 존재 확인 | 등록 경로를 annotation 으로 찍고 **즉시 실패**. 조용히 넘어가지 않는다 |
| 2~3 체크아웃 | 원본 + 시연본 저장소(`prototype/`) | 토큰 권한 부족 시 실패 |
| 4 변환 | `scripts/sync_prototype.py --dst prototype` — 갤러리 제거·로고 고정·형제 링크 해시 전환·자산 역산 복사 | 차단 처리를 걸 자리를 못 찾으면 **`index.html`을 쓰지 않고** 실패 |
| 5 통로 잔존 검사 | 산출된 `index.html`을 스크립트와 무관하게 다시 훑는다 | 금칙 문자열·형제 문서 상대링크·허용 밖 외부 호스트가 **1건이라도 있으면 실패**. push하지 않는다 |
| 6 반영 | 시연본 저장소 커밋·push (바뀐 것 없으면 커밋하지 않는다) | push 실패 시 워크플로 실패 |
| 7 배포 확인 | 배포 주소 본문의 sha256이 산출물과 같아질 때까지 최장 10분 | 지연은 warning (배포는 Vercel 몫) |

5단계 검사 항목 — `glossary` `capability` `feasibility` `inquiry` `archive` `review` `랜딩` `갤러리` `문의서` 문자열, `#`·`assets/`·`index.html`·절대주소가 아닌 `href`, 허용 목록(`fonts.googleapis.com` `fonts.gstatic.com` `www.we-bank.co.kr`) 밖의 외부 호스트.

이 검사가 헛돌지 않는지 확인했다. 산출된 `index.html`에 `<a href="glossary.html">용어</a>`와 `<a href="https://evil.example.com/x">`를 일부러 끼워 넣고 같은 검사를 돌리면 금칙 문자열 1건·형제 문서 상대링크 1건·허용 밖 외부 호스트 1건을 모두 집어내고 종료코드 1로 끝난다. 원본 그대로는 0건으로 통과한다.

### 사용자가 할 1회 작업 — 토큰 등록

`GITHUB_TOKEN`은 자기 저장소 밖으로 쓸 수 없다. 다른 저장소에 push하려면 개인 토큰이 필요하고, **토큰 발급과 등록은 계정 소유자만 할 수 있다.** 아래 한 번만 하면 이후로는 손댈 일이 없다.

**1) 토큰 만들기**

https://github.com/settings/personal-access-tokens/new (Settings → Developer settings → Personal access tokens → **Fine-grained tokens** → Generate new token)

| 칸 | 넣을 값 |
|---|---|
| Token name | `payhug-prototype-sync` |
| Expiration | 원하는 기간 (만료되면 자동화가 멈추므로 길게) |
| Resource owner | `Joo2n` |
| Repository access | **Only select repositories** → `payhug-investor-prototype` **하나만** |
| Permissions → Repository permissions | **Contents: Read and write** — 이것 하나면 된다 |

Generate 후 화면에 뜨는 `github_pat_…` 값을 복사한다. 그 화면을 벗어나면 다시 볼 수 없다.

**2) 시크릿으로 넣기**

https://github.com/Joo2n/payhug-investor-admin/settings/secrets/actions → **New repository secret**

| 칸 | 넣을 값 |
|---|---|
| Name | `PROTOTYPE_SYNC_TOKEN` |
| Secret | 위에서 복사한 토큰 |

**3) 도는지 보기**

https://github.com/Joo2n/payhug-investor-admin/actions/workflows/sync-prototype.yml → **Run workflow** → main. 초록이면 끝이다. 이후 `app.html`이 바뀔 때마다 저절로 돈다.

토큰을 넣기 전까지 워크플로는 1단계에서 빨간불로 멈춘다 — 실측 확인됨(run `33145392700`, 5초, annotation `PROTOTYPE_SYNC_TOKEN 없음`). 잘못된 결과가 배포되는 경로는 없다.

트리거가 실제로 걸리는 것도 확인됐다. 화면 지적 12건을 담은 `app.html` 커밋(`0b12238`)이 올라가자 워크플로가 저절로 돌았고, 토큰이 없어 1단계에서 멈췄다. 토큰이 있었다면 그 push 하나로 시연본까지 갔을 자리다 — 이번에는 같은 결과를 수동 경로로 올렸다.

### 그 사이 공백

시크릿 등록 전에는 자동화가 돌지 않는다. 그동안은 같은 변환기를 부르는 `_pipeline/investor_admin/sync_prototype.sh`로 반영한다(빌드 → 헤드리스 게이트 → push → 배포 실측, 검사 실패 시 push 중단). 현재 배포본은 이 경로로 올렸다.

### 관련 파일

| 파일 | 용도 |
|---|---|
| `payhug-investor-admin/.github/workflows/sync-prototype.yml` | 자동화 본체 |
| `payhug-investor-admin/scripts/sync_prototype.py` | 변환기. 자동화·수동 양쪽이 같은 파일을 쓴다 |
| `_pipeline/investor_admin/gate_prototype.js` | 헤드리스 게이트(화면·상태·링크·다운로드·숫자). 로컬·배포 URL 양쪽 |
| `_pipeline/investor_admin/sync_prototype.sh` | 공백 기간용 수동 경로 |
| `_pipeline/investor_admin/verify_proto.js` · `verify_proto_result.json` | 깊은 검증(클릭 시퀀스·죽은 컨트롤·레이아웃 31조합) |

### 원본 저장소 정리

`payhug-investor-admin`의 기존 산출물은 건드리지 않았다. 중간에 만들었던 `demo/` 폴더는 커밋 전에 지웠고 작업 트리에도 없다(`git ls-files demo/` = 0). 다른 조가 고치는 중인 `glossary.html`·`glossary_manuscript.md`는 손대지 않았고, push 충돌 1회는 `git pull --rebase --autostash`로 풀었다 — force push 없음. 추가한 것은 `scripts/sync_prototype.py`와 `.github/workflows/sync-prototype.yml` 둘뿐이다.

---

## §6 미해소

| # | 사안 | 상태 |
|---|---|---|
| 1 | 일별 투자수익의 `0.110000%` | **표기 자체가 없다.** 화면은 `0.11%`로 그리고, `일별투자수익_2026-08-21_2026-08-27.xlsx`도 셀 값 `0.11` · 서식 `0.0`이다. 소수 6자리 표기는 이 산출물 어디에도 없다. 엑셀 파일은 원본과 바이트가 같으므로 이 저장소가 바꾼 값은 아니다. 요구한 자릿수가 맞다면 원본 `build_app.py`·`build_xlsx.py` 쪽 사안이다 |
| 2 | 투자자산 증명서 화면의 `본 지면은 화면 설계(안) 시연용 견본` 문구 | 남겼다. 다른 문서로 가는 링크가 아니라 발급 효력이 없다는 고지다. 지우면 견본임을 알리는 문구가 사라진다 — 지울지 여부는 판단 필요 |
| 3 | 정렬·필터 깊은 검증 대본 | 조회 필터 개편으로 `어제` 프리셋이 사라져 `verify_proto.js`의 값 변화 11항이 돌지 않는다(SKIP). 게이트는 전항 통과. 이 대본을 새 필터 구성에 맞춰 다시 쓸지 여부는 판단 필요 — 시연본 분리와 무관한 원본 화면 사안이다 |
| 4 | 요율·수수료율 | `analysis/00_종합.md` C1 미확정 그대로. 화면의 `(예시)` 표기 유지 |
| 5 | 시연본 저장소 공개 범위 | public이라 주소를 아는 사람은 누구나 연다. 링크를 받은 사람만 보게 하려면 Vercel Password Protection(유료 플랜)이나 저장소 private + Vercel Authentication 조합이 필요하다 — 현재는 열려 있다 |
