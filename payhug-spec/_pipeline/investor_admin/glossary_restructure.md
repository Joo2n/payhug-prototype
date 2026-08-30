# 용어 문서 재조판 — 5필드 카드 구조

투자자 어드민 용어 문서를 서술 중심에서 **용어 1건 = 카드 1개** 구조로 옮긴 결과다.
원고는 `_pipeline/investor_admin/glossary_manuscript.md`, 산출물은 `payhug-investor-admin/glossary.html` 이고 둘 다 같은 구조를 쓴다.

| 무엇 | 어디 |
|---|---|
| 원고 | `_pipeline/investor_admin/glossary_manuscript.md` (4,036행 · 205KB) |
| 원고 재조판기 | `_pipeline/investor_admin/restructure_glossary.py` |
| HTML 생성기 | `_pipeline/investor_admin/build_glossary.py` |
| 산출물 | `payhug-investor-admin/glossary.html` (413KB) |
| 구버전 | `payhug-investor-admin/glossary-legacy.html` (307KB) |
| 기호 원천 | `_pipeline/investor_admin/symbol_glossary.json` (기호 28 · 연산자 4) |
| 화면 좌표 원천 | `_pipeline/investor_admin/shot_rects.json` (14화면 · 689항목) |
| 캡처기 | `_pipeline/investor_admin/capture_shots.js` |
| 검증기 | `_pipeline/investor_admin/verify_glossary5.js` |

---

## 1. 새 구조 · 목차

### 목차가 용어 목록이다

종전 목차는 `0 화면에서 본 이름으로 찾기 / 1 전체 그림 / 2 그림 가운데가 비어 있다 / 3 읽는 순서 / 4 용어 카드 50건 / 5 화면 역방향 색인 / 6 이름 충돌 / 7 새로 만들어야 하는 것 / 8 물어야 할 것` 이었다. 아홉 항목 중 용어를 가리키는 것은 하나뿐이라 정작 용어를 찾을 수 없었다.

지금 목차는 **용어 50건 목록**이다. 왼쪽 고정 목차가 단계별로 묶인 용어 이름 50개이고, 이름 옆에 그 용어의 변수 기호가 붙는다. 본문 맨 앞에도 같은 50건이 `용어명 · 변수 · 화면 · 한 줄 뜻` 다섯 열의 표로 한 번 더 있다.

### 문서 뼈대

| 자리 | 내용 |
|---|---|
| 머리말 | 근거 7행 · 할인율 `0.11% 예정` 경고 |
| 카드 한 장에 무엇이 들어 있나 | 5필드 규격 · 값의 출처 다섯 갈래 · 계산 예시에 쓰는 숫자 한 벌 |
| 용어 50건 — 목차 | 표 50행 |
| 1~7단계 | 카드 50건 |
| 부록 A~G | 서술 |

단계별 카드 수는 1단계 8 · 2단계 4 · 3단계 3 · 4단계 13 · 5단계 6 · 6단계 7 · 7단계 9로 50건이다.

---

## 2. 카드 5필드 규격

카드 하나에 다섯이 같은 순서로 온다. HTML 에서 각 필드는 `data-field` 속성을 달고 있어 기계로 셀 수 있다.

| # | 필드 | `data-field` | 내용 |
|---|---|---|---|
| 1 | 용어명 | `term` | 화면에서 보는 이름이 먼저. 대표 정의서 표기가 다르면 `화면 표기` 칩으로 병기. 계통이 갈리면 `(어느 계통 · 어느 집계 단위)` |
| 2 | 변수 | `var` | 원문 기호와 한국어 이름. 단위 · 뜻 · 산식 · 글자 유래 · 이름을 붙인 근거. 기호가 없으면 `기호 없음` |
| 3 | 계산식 | `calc` | 원문 산식 그대로 → 기호를 그 자리에서 우리말로 풀이 → 숫자 한 벌로 단계별 계산 |
| 4 | 화면 | `screen` | 화면 캡처 + 위치 상자 + 라이트박스 확대 |
| 5 | 관련 용어 | `rel` | `재료`(이 용어를 만드는 것) · `쓰이는 곳`(이 용어를 재료로 쓰는 것). 이름은 카드 앵커 링크 |

카드 머리에는 한 줄 뜻이 리드로 붙고, 층위(`화면 용어` 28 / `계산 재료` 22) 칩이 달린다.
다섯 아래에 **값의 출처**와 **기획할 때 정해야 할 것**이 `<details>` 로 접혀 있다.

### 변수 칸이 지키는 것

- 기호가 붙은 카드 **22건**, 원문에 기호가 없어 `기호 없음` 인 카드 **28건**. 기호를 지어내지 않는다.
- 한국어 이름은 `원문 명명` 12건과 `문서 명명` 16건을 칩으로 갈라 표시한다. 문서가 붙인 이름은 `이름을 붙인 근거`가 함께 나온다.
- **영문 약자 12글자는 전건 `원문에 근거 없음`.** `A`를 Amount로, `P`를 Period로 읽는 식의 추측은 넣지 않고, 원문에서 관찰되는 쓰임만 적는다.
- `Ai` 카드는 화면 `투자실행금`과 **같은 개념이고 단위만 다르다**는 것(채권 1건 대 합계)을 본문에 적고, `헷갈리는 쌍` 으로 `Ai ↔ SA(D-1) · PSA` 를 붙였다. 헷갈리는 쌍 7건이 해당 카드마다 걸린다.
- 문서 약칭 `SB` `SA` `SM` `SMR` `SD` 는 원문에 없는 표기라 `다르게 쓰는 표기` 행에 alias 로 표시한다.
- `③④⑤⑥` 을 쓰는 카드 3건에는 **원문이 참조한 이미지가 없어 확정 불가**라는 단서가 붙는다.
- 기호는 `#sym-*` 앵커로 부록 A 기호 사전에 연결된다.

---

## 3. 이미지 생성 방식 · 용량

### 캡처

`capture_shots.js` — 로컬 정적 서버 + `--headless=new` + CDP. 창을 띄우지 않는다.

| 항목 | 값 |
|---|---|
| 뷰포트 | 폭 1440 · `Emulation.setDeviceMetricsOverride` |
| 배율 | `deviceScaleFactor 2` |
| 포맷 | webp · quality 70 (`Page.captureScreenshot` 직수신) |
| 범위 | `captureBeyondViewport` + 문서 전체 clip |
| 대기 | `document.fonts.ready` 후 추가 여유 |

`sips` 는 webp 쓰기를 못 해서 CDP 로 직접 webp 를 받는다. 화면 14종을 찍고 **용어 50건이 그 14장을 나눠 쓴다** — 용어마다 새로 찍지 않고 위치 상자만 다르다.

| 화면 | 용량 | 화면 | 용량 |
|---|---|---|---|
| invest-assets | 140KB | certificate | 144KB |
| invest-assets--page2 | 139KB | xls-profit-status | 79KB |
| invest-assets--cert-confirm | 124KB | xls-profit-daily | 108KB |
| invest-profit | 112KB | xls-assets-status | 82KB |
| invest-profit--monthly | 109KB | xls-assets-merchant | 139KB |
| merchants | 88KB | acquisition | 50KB |
| contracts | 83KB | coocon | 54KB |

**총 1,486,338B = 1.42MB / 예산 5MB.** 여유가 커서 화질을 깎지 않았다.

### 위치 표시 — 이미지에 굽지 않는다

좌표는 `shot_rects.json` 에 CSS 픽셀로 들어 있고(문서 좌상단 기준), 생성기가 `docW`·`docH` 로 나눠 **퍼센트**로 바꿔 CSS 로 얹는다. 화면이 바뀌면 `capture_shots.js` 를 다시 돌려 좌표만 갱신하면 되고 이미지를 다시 그릴 필요가 없다.

카드에서 앵커를 가리키는 규칙은 `restructure_glossary.py` 의 `META` 표에 카드별로 손으로 적혀 있다 — `tag:text#nth` 꼴이다. 예: `th:W금융일수#0` 은 현황표의 첫 `W금융일수` 열머리다.

상자는 두 가지다.

| 종류 | 뜻 | 표시 |
|---|---|---|
| `direct` | 그 자리에 그 값이 실제로 뜬다 | 초록 실선 · `이 자리` |
| `indirect` | 화면에 안 뜨고 그 자리 뒤에 숨는 재료다 | 주황 파선 · `재료 — 이 자리 뒤에 숨는다` |

카드 안에서는 260px 창에 상자 주변만 잘라 보여 준다. 세로 위치는 순수 JS 가 상자 중심을 창 가운데로 맞추되 이미지 위아래를 넘지 않게 가둔다.

### 라이트박스

외부 라이브러리 없이 순수 JS 다.

- 캡처를 누르면 열린다 (`.crop` 버튼)
- `Esc` 로 닫힌다
- 배경을 눌러도 닫힌다
- `실제 크기` 단추로 1:1 과 화면 맞춤을 오간다
- 확대 화면에도 **같은 위치 상자**가 같은 퍼센트로 얹힌다
- 닫으면 눌렀던 캡처로 초점이 돌아온다

---

## 4. 부록으로 옮긴 것

서술 여섯 절은 내용을 그대로 둔 채 뒤로 갔다. 종전 §3 `읽는 순서`와 §5 `화면 역방향 색인`은 카드 구조가 역할을 흡수해 없앴다 — 읽는 순서는 카드 규격 절의 한 줄로, 화면별 색인은 카드마다 붙은 화면 필드와 부록 D 로 대체된다.

| 종전 | 지금 | 처리 |
|---|---|---|
| 1 전체 그림 | 부록 B | 그대로 |
| 2 그림 가운데가 비어 있다 | 부록 C | 그대로 |
| 0 화면에서 본 이름으로 찾기 | 부록 D | 그대로 |
| 6 이름 충돌 | 부록 E | 그대로 |
| 7 새로 만들어야 하는 것 | 부록 F | 그대로 |
| 8 물어야 할 것 | 부록 G | 그대로 |
| 3 읽는 순서 | — | 카드 규격 절 한 줄로 흡수 |
| 5 화면 역방향 색인 | — | 카드 화면 필드가 흡수 |

**부록 A 기호 사전은 신설이다.** 기호 28건을 단위·뜻·원문 근거·명명 출처로 펴고, 연산자 4건 · 표기 정본 · 헷갈리는 쌍 7건을 함께 담는다. 카드 변수 칸의 기호가 여기로 연결된다.

---

## 5. 검증

`verify_glossary5.js` — 로컬 서버 + `--headless=new`. 창을 띄우지 않는다.

| 항목 | 기준 | 실측 |
|---|---|---|
| 카드 수 | 원고와 일치 | **50 / 50** |
| 5필드 누락 | 0건 | **0건** (카드마다 `term`·`var`·`calc`·`screen`·`rel` 전건) |
| 이미지 로드 | 전건 | **50 / 50** (`naturalWidth>0`) |
| 위치 상자 | 창 밖 0 · 0크기 0 | **0 / 0** |
| 라이트박스 | 열림·Esc·배경·재열림 | **전건 동작** |
| 앵커 도달 | 끊김 0 | **779건 중 0건 끊김** |
| 가로 오버플로 | 1440·1280·1024·768 에서 0 | **전건 0** |
| 콘솔 에러 | 0 | **0** |
| 검색 | 거르고 되돌아옴 | 동작 |
| 구버전 | 제목·안내 띠·최신본 링크 | 전건 확인 |

용량 — `glossary.html` **413KB**, 이미지 **1.42MB**, 합계 약 1.83MB.

### 표본으로 눈으로 본 것

`투자 실행액` 카드는 `invest-assets.html` 현황표의 `투자실행액` 칸에 초록 상자가 정확히 얹힌다. `PSC` 카드는 기호 표(단위·뜻·산식·글자 유래·이름 근거)가 펴지고 `Σ`·`EC` 로 가는 링크가 걸린다.

### 함께 잡아 고친 것

**표기 정본 5곳** — `symbol_glossary.md` §5-1 이 원고에서 특정한 자리다. 원문 인용 자리는 손대지 않았고 문서가 스스로 서술한 자리만 맞췄다.

| 자리 | 종전 | 지금 |
|---|---|---|
| 전체 그림 · 잔액 계통 | `Σ(Ai·Di) / Σ Ai` | `(Σ Ai x Di) / Σ Ai` |
| 전체 그림 · 유량 계통 | `Σ(Ai·Di) / Σ Ai` | `(Σ A(D-1)i x D(D-1)i) / Σ A(D-1)i` |
| 전체 그림 · 기간 집계 | `Σ(Api·Dpi) / PSA` | `(Σ Api x Dpi) / PSA` |
| w금융일수 카드 기호 풀이 | `Σ Ai × Di` | `Σ Ai x Di` |
| w금융일수(하루치) 풀어 쓴 식 | `Σ(A(D-1)i × D(D-1)i) ÷ …` | `(Σ A(D-1)i x D(D-1)i) / …` |

유량 계통 한 줄은 곱셈 기호만이 아니라 **기호 자체가 틀려 있었다** — 하루치 `SD` 식에 범위가 다른 `Ai`·`Di` 가 들어가 있었고 원문은 `AD-1i`·`DD-1i` 다.

**영문 약자 추정 6곳 제거** — `A`=Amount, `w`=weighted, `S`=Sample, `L`=Lack/Loss, `EC`=End Cash, `P`=Period. 전부 원문에 근거가 없어 `원문에 근거 없음` + 관찰되는 쓰임으로 바꿨다.

**캡처로 드러난 현행 화면 사실 2건** — 원 판단은 지우지 않고 실측 관찰을 덧붙였다.

| 카드 | 원고가 적은 것 | 2026-08-28 캡처 실측 |
|---|---|---|
| `정산예정일` | 현재 열 이름은 `입금일자` | 이미 `정산예정일` 로 적용돼 있다 |
| `효력기간` | `contracts.html` 에 `서명일` 열은 있다 | 열은 `MID` `가맹점` `재양도합의서` `검증` 넷뿐이고 `서명일` 도 없다 |

### 손대지 않은 것

숫자 · 산식 · 판정은 위 표기 정본 5곳 외에 바뀐 것이 없다. 할인율 `0.11% 예정` 단서, C1·C2·C4 미확정, 6대 개념 분리 모두 그대로다. 산식 안의 `×` 가 남은 자리는 `symbol_glossary.md` §5-1 이 어긋난 자리로 지목하지 않은 곳이라 건드리지 않았다.

---

## 6. 배포 — 통합 레포

| 파일 | 상태 |
|---|---|
| `glossary.html` | 재조판본. 제목 `투자자 어드민 용어 해설` |
| `glossary-legacy.html` | 구버전 보존. 제목 `용어 구버전 — 투자자 어드민` · 상단 띠에서 최신본으로 연결. 본문 내용은 그대로 |
| `index.html` | 문서 카드 4장 — `용어 해설`(최신 표시) · `용어 구버전` · 기능·데이터 명세 · 작업물 아카이브 |
| `review.html` | 순차 확인 12단계 — `용어 해설 — 여기부터 읽으면 된다` 와 `용어 구버전 — 비교용` 이 나란히 |
| `assets/shots/*.webp` | 화면 14종 캡처 보관함. 카드가 부르는 것은 5종이다 |
| `scripts/sync_glossary.py` | 단독 배포본 변환기 |

배포 주소 — 용어 해설 `https://payhug-investor-demo.vercel.app/glossary.html` · 구버전 `https://payhug-investor-demo.vercel.app/glossary-legacy.html`. 둘 다 200 실측이고 새 구조가 그대로 올라가 있다(카드 50 · 5필드 전건 · 이미지 50 전건 로드 · 앵커 779 전건 도달 · 콘솔 0).

`index.html` 은 `build_index.py` 산출물이라 생성기와 산출물을 함께 고쳤다.

### 커밋에 섞여 들어간 것 — 확인 필요

재조판 커밋 `efe85b4` 는 의도한 6종(`glossary.html` · `glossary-legacy.html` · `index.html` · `review.html` · `assets/shots/` 14장) 외에 **다른 조가 작업 중이던 파일 12종이 함께 들어갔다** — `app.html` · `assets/base.css` · `README.md` · `contracts*.html` 4종 · `acquisition*.html` 4종 · `merchants.html`.

스테이징은 6종만 했는데 커밋 사이에 인덱스에 다른 파일이 올라와 있었다. 훅도 `commit.all` 설정도 없다. 같은 저장소에서 동시에 도는 다른 작업이 `git add -A` 계열을 돌린 것으로 보인다.

**되돌리지 않았다.** 이력 재작성·force push 는 금지돼 있고, 그 조의 최신 작업물을 지우게 된다. 배포 실측으로 깨진 곳이 없는지 확인했다 — `app.html` · `contracts.html` · `merchants.html` · `acquisition.html` 전건 200, `app.html` 콘솔 에러 0, 가로 오버플로 0.

그 조에 알려야 할 것은 **작업 중이던 변경이 예정보다 일찍 `main` 에 올라가 배포됐다**는 사실이다. 되돌릴지 그대로 갈지는 그쪽 판단이다.

---

## 7. 용어 해설 단독 배포

팀원 공유용으로 용어 해설만 담는 별도 주소를 둔다. 통합 레포에도 그대로 남아 있어 구버전과 견줘 볼 수 있다.

| 무엇 | 주소 |
|---|---|
| **용어 해설 (단독 배포)** | **https://payhug-investor-glossary.vercel.app/** |
| 용어 해설 (통합본 안) | https://payhug-investor-demo.vercel.app/glossary.html |
| **용어 구버전** | **https://payhug-investor-demo.vercel.app/glossary-legacy.html** |
| 저장소 | `Joo2n/payhug-investor-glossary` (private) |
| Vercel 프로젝트 | `prj_Di7TnN5I2WwDgEH3x2qw0vkvQNbg` · 팀 `joons-projects-9eb5ca31` |

Vercel Authentication · 비밀번호 보호 · Trusted IP 전부 꺼져 있다. 저장소는 private, 배포 주소만 public 이다.

### 레포 구성

담는 것은 이것뿐이다. 총 **1.00 MB**.

```
index.html            glossary.html 을 변환한 것 (413KB)
assets/base.css
assets/logo-icon.png
assets/shots/*.webp   5종 — 문서가 실제로 부르는 것만
README.md
.gitignore
```

캡처는 화면 14종을 찍어 통합 레포 `assets/shots/` 에 보관함으로 두고, **배포본에는 문서가 실제로 부르는 5종만** 넣는다(`invest-assets` · `invest-profit` · `merchants` · `contracts` · `coocon`). 나머지 9종은 어느 카드도 부르지 않아 배포본에서 뺐다 — 830KB 가 줄었다. 뒤에 카드가 그 화면을 부르면 동기화가 알아서 딸려 보낸다.

### 바깥 링크 제거

원본에서 바깥으로 나가는 실제 앵커는 상단 우측 `.tb-alt` 안의 둘뿐이다 — `glossary-legacy.html` 과 `index.html`. 단독본에는 그 문서들이 없으므로 `.tb-alt` 블록과 그 CSS 규칙 3개를 들어낸다. 원본 대비 diff 는 15줄이다.

본문의 `invest-assets.html` 같은 화면 이름 표기는 링크가 아니라 내용이라 그대로 둔다(170건 보존). 그래서 금칙 검사는 문자열 전체가 아니라 **`href`·`action` 속성 안만** 본다.

### 배포 실측

| 항목 | 결과 |
|---|---|
| `/` · `/index.html` | 200 · 422,527B |
| `assets/base.css` · 캡처 5종 | 200 전건 |
| `app.html` `capability.html` `feasibility.html` `inquiry.html` `archive.html` `review.html` `glossary.html` `glossary-legacy.html` `merchants.html` | **전건 404** |
| 부르지 않는 캡처 (`certificate.webp` 등) | 404 |
| 카드 · 이미지 · 앵커 · 콘솔 | 50건 · 50개 전건 로드 · 779개 전건 도달 · 0 |
| **바깥 링크** | **0건** (문자열·DOM 양쪽) |
| 라이트박스 · 가로 오버플로 | 동작 · 0 |

### 동기화

```
bash payhug-spec/_pipeline/investor_admin/sync_glossary.sh [--dry-run]
```

| 단계 | 하는 일 |
|---|---|
| 1 | `glossary.html` → 변환 → 용어 레포 `index.html`. 통로 검사에 걸리면 **파일을 쓰지 않고** 종료코드 1 |
| 2 | `gate_glossary.js` 로컬 게이트 — 걸리면 push 로 넘어가지 않는다 |
| 3 | 변경이 있을 때만 commit · push (3회 재시도, `pull --rebase`, force 금지) |
| 4 | 배포 반영 대기 — 로컬 `index.html` 과 배포 응답의 sha256 대조 |
| 5 | 배포 URL 실측 게이트 |

`--dry-run` 은 2단계까지만 돈다. 변경이 없으면 조용히 끝난다.

| 파일 | 역할 |
|---|---|
| `_pipeline/investor_admin/sync_glossary.sh` | 드라이버 |
| `payhug-investor-admin/scripts/sync_glossary.py` | 변환기·문자열 게이트·자산 거울 |
| `_pipeline/investor_admin/gate_glossary.js` | 헤드리스 게이트 (문자열 + DOM) |

변환기를 원본 레포 `scripts/` 에 둔 것은 시연본 `sync_prototype.py` 와 같은 자리다. 시연본과 공용 모듈로 묶지는 않았다 — 시연본 변환기는 `app.html` 의 SPA 구조 전용(갤러리 섹션 절단 · `RENDER['index']` 괄호 균형 · 해시 딥링크 치환)이라 정적 문서인 용어판과 겹치는 로직이 사실상 없고, 억지로 묶으면 잘 돌고 있는 시연본을 고쳐야 한다. 구조·명명·게이트 방식만 그대로 본떴다.

원본을 고친 뒤 이 스크립트를 돌린다. 용어 레포의 `index.html` 을 직접 고치면 다음 동기화에서 덮인다.
