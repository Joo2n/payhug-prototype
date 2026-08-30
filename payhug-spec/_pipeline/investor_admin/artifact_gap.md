# 실물 공백 점검 — 투자자 어드민

대상 레포 `/Users/semi/cursor/payhug-investor-admin/` · 기준 2026-08-27 17:45
점검 범위 루트 HTML 38개 + `assets/` 하위 전량.

판정 기준 — **화면이 "실물을 준다"고 말하는 컨트롤**을 전수로 세고, 그 실물이 디스크에 있는지
로컬 서버(`http://localhost:8901`) 응답으로 실측한다. 라벨·아이콘·안내문이 파일·문서·외부 시스템·
검증 결과를 약속하면 전부 대상이다.

---

## §1 전수 점검표

컨트롤 **217건 · 14개 유형**. `실물` 열은 실측 결과다.

| # | 유형 | 화면 | 건수 | 약속하는 실물 | 실물 | 처리 |
|---|---|---|---|---|---|---|
| 1 | 사이드바 로고 링크 | 화면 33개 | 33 | 홈 이동 | 없음 (`href="#"`) | 18건 `index.html` 배선 · 15건 §4 |
| 2 | 계약서 파일 링크 `재양도합의서_M2026-00NN.pdf` | `contracts` `--all` `--downloaded` | 24 | 재양도합의서 원본 PDF | 없음 (`href="#"`) | **PDF 16종 생성 · 24건 배선** |
| 3 | `계약서 보기` | `acquisition` `--confirm` `--signing` `--done` | 12 | 서명 대상 계약서 원문 | 10건 없음 · 2건은 `contracts.html`로 이동 | **PDF 3종 생성 · 10건 배선** |
| 4 | `선택 문서 다운로드` | `contracts` ×3 (+`--empty` 1) | 4 | 재양도합의서 파일 + 서명검증 회신전문 묶음 | 없음 (`<button>` 무동작) | **zip 2종 생성 · 3건 배선** · `--empty` 제외(§5) |
| 5 | `비밀번호 찾기` | `login` `app` | 2 | 비밀번호 재설정 화면 | 화면 자체가 없음 (D-2 범위 밖) | `login` 비활성+툴팁 · `app`은 재빌드로 승계됨 |
| 6 | `엑셀 다운로드` | `invest-assets*` `invest-profit*` | 13 | 엑셀 미리보기 화면 | 있음 — `xls-*.html` 4종 | 유지 |
| 7 | `엑셀 파일 내려받기` | `xls-*` ×4 | 4 | `.xlsx` 실물 | 있음 — `assets/xlsx/` 4종, 바이트 일치 | 유지 |
| 8 | `증명서 다운로드` | `invest-assets*` ×5 | 5 | 발급 확인 모달 | 있음 — `invest-assets--cert-confirm.html` | 유지 |
| 9 | 모달 `발급` | `invest-assets--cert-confirm` | 1 | 증명서 화면 | 있음 — `certificate.html` | 유지 |
| 10 | `PDF 다운로드` | `certificate` | 1 | 투자자산 증명서 전자문서 | 없음 (`<button>` 무동작) | **PDF 생성 · 배선은 §4** |
| 11 | `We-bank 바로가기` / 모달 `이동` | `coocon` `--confirm` `app` | 5 | 쿠콘 We-bank 외부 시스템 | 스토리보드 슬라이드10 삽입 이미지(`image6.png`) 주소창에 `https://www.we-bank.co.kr/main_00100.act`가 경로까지 축자로 찍혀 있다 | 스토리보드가 지정한 목적지 그대로 유지 |
| 12 | 가맹점 행 클릭(`.clickable`) | `merchants*` | 18 | 가맹점 상세 화면 | 목적지 없음. 정적 화면은 안내도 없음 | §4 — 커서 제거 또는 안내 |
| 13 | `app.html` 액션 핸들러 | `app` | 6 | 파일·화면 | `xls-get`만 실물 · `cert-pdf` `ct-download`는 **파일 없이 성공 토스트** | §4 |
| 14 | 아카이브 파일 링크 | `archive` | 89 | 로컬 원본 파일 | 로컬 서버 2개(8901·8902) 가동 시에만 유효 | §5 — 의도된 작업용 페이지 |

### 1-1. `href="#"` 분해 재확인 — 기존 집계 정정

기존 집계는 **70건 = 로고 33 · 계약서 PDF 24 · 계약서 보기 12 · 비밀번호 찾기 1**.
실측 결과 **69건**이고 분해도 두 항목이 다르다.

| 항목 | 기존 | 실측 | 확인 근거 |
|---|---|---|---|
| 로고 | 33 | **33** | 일치. `login.html`에는 사이드바가 없어 로고 링크도 없다 |
| 계약서 PDF | 24 | **24** | 일치. 3개 파일 × 8행 |
| 계약서 보기 | 12 | **10** | `acquisition--done.html`은 3건 중 2건이 이미 `contracts.html`로 배선돼 있어 `#`는 1건뿐 |
| 비밀번호 찾기 | 1 | **2** | `login.html` 외에 `app.html:1041`에도 같은 링크가 있다 |
| **합계** | 70 | **69** | |

### 1-2. 엑셀 밖의 "오해한 것" — 유형을 넓혀 본 결과

엑셀과 같은 구조(화면은 실물을 말하는데 뒤가 빔)로 판정된 것.

- **파일 없이 성공을 주장하는 토스트** — 가장 위험한 유형.
  `app.html` `ACT['cert-pdf']`는 `투자자산 증명서 PDF 내려받기 완료`를,
  `ACT['ct-download']`는 `재양도합의서 N건 내려받기 완료 · 각 문서에 서명 검증 회신전문 포함.`을
  띄우지만 어느 쪽도 파일을 내려주지 않는다. 같은 파일의 `xls-get`은 실제 `<a download>`를 함께 걸어
  토스트가 사실이므로, 세 핸들러가 같은 어투로 서로 다른 사실성을 갖는다.
- **서명 검증 회신전문** — 계약기록 표의 `검증 완료` 배지와 하단 안내문
  `서명 검증 회신전문이 함께 제공됨`이 존재를 단언하지만 실물·형식·전달 경로가 모두 없다.
  회신전문 형식(xml·txt·pdf)과 묶음 다운로드 API는 미정의(`capability_manuscript.md §4-15`).
- **증명서 서명값** — `certificate.html`의 `sig-value`
  (`kd568w7sg9apt86ag6ejg8atu73aat8tag8ata6agje8s7`)와 `서명 검증: 인증서 발행기관 검증 회신 완료`
  배지는 검증된 전자서명처럼 읽히지만 검증 가능한 값이 아니다.
- **가맹점 상세 이동** — `merchants*`의 행이 `cursor:pointer`로 상세 화면을 암시하나 목적지가 없다.
  `app.html`은 `가맹점 상세 화면은 이번 설계 범위 밖`이라고 밝히지만 정적 화면 4개는 아무 말도 없다.
- **표 건수와 실제 행 수 불일치** — `contracts*`·`merchants*`가 `총 16건`과 2페이지 버튼을 내걸지만
  마크업에 있는 행은 8개뿐이고 2페이지 데이터가 없다. 로스터 16건 확장이 진행 중인 다른 조의 작업 경계다.
- **외부 시스템 이동** — We-bank URL의 근거는 스토리보드 슬라이드10 삽입 이미지다. 브라우저 주소창에
  `https://www.we-bank.co.kr/main_00100.act`가 경로까지 축자로 찍혀 있어, 화면이 인쇄한 주소는
  스토리보드가 지정한 목적지다. 슬라이드 텍스트 프레임만 읽으면 이 근거가 보이지 않는다.

---

## §2 생성한 실물

`/Users/semi/cursor/payhug-investor-admin/assets/docs/` — **22개 파일**(PDF 20 · zip 2).
생성기 `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/build_docs.py`.

### 2-1. 목록

| 파일 | 면수 | 내용 | 대응 컨트롤 |
|---|---|---|---|
| `재양도합의서_M2026-0001.pdf` ~ `M2026-0016.pdf` (16) | 3면 | 정산금채권 재양도 합의서 — 당사자표·제1~9조·서명란 | 계약기록 파일 링크 |
| `계약서_서명대기_M2026-0001.pdf` `-0002` `-0004` (3) | 4면 | 서명 대기본. 제1부 양수도 계약서 요지 + 제2부 재양도 합의서(서명 대상) | 정산채권 양수 `계약서 보기` |
| `투자자산증명서_20260827.pdf` (1) | 2면 | 가맹점별 투자자산 16행 + 합계 + 서명·검증란 | `certificate.html` `PDF 다운로드` |
| `재양도합의서_선택3건_20260827.zip` | — | `M2026-0001` `-0004` `-0006` PDF + `README.txt` | `contracts.html` `선택 문서 다운로드` |
| `재양도합의서_전체16건_20260827.zip` | — | 16개 PDF + `README.txt` | `--all` `--downloaded` `선택 문서 다운로드 (16)` |

### 2-2. 견본 표기

- 매 페이지 상단에 머리띠 `견본 · 제안서 시연용 — 계약 효력 없음 · 실제 서명·인증 미포함`.
  `<thead>` 러닝 헤더로 넣어 20개 PDF 전 페이지(총 62면)에 반복됨을 콘텐츠 스트림에서 실측 확인.
- 지면 중앙에 대각선 워터마크 `견본`.
- 서명란은 점선 빈칸 + `견본 — 서명 없음` / `서명 대기`. 실인감·서명 이미지·실존 인물 서명 없음.
- 하단 고지에 계약 효력·증명력 없음과 서명값·회신전문 미포함을 명시.
- zip 안 `README.txt`에 담긴 것/담기지 않은 것/효력을 분리 기재.

### 2-3. 값 출처

문서에 들어간 수치는 전부 화면에서 읽어온다. 생성기가 빌드할 때마다 화면을 다시 파싱하므로
다른 조가 화면 수치를 고치면 재실행만으로 문서가 따라간다.

| 항목 | 출처 |
|---|---|
| 가맹점 상호·사업자번호·대표자·업종·종목 | `merchants*.html` 원장 행. 화면에 행이 없는 `M2026-0009`~`-0016`은 `_pipeline/investor_admin/roster16_model.py` `ROSTER` |
| 서명일 | `contracts*.html` 표 5열 |
| 계약 생성일·서명 대기 대상 | `acquisition.html` `sign-row` |
| 투자자명·작성일자·자산 명세·합계·서명값 | `certificate.html` `doc-tbl`·`sig-value` |
| 조항 본문 | `payhug-spec/analysis/archive_02_계약약관.md` §2.3(양수도 계약서)·§2.4(재양도 합의서). 조문 근거를 조항마다 병기 |
| 문서명 상충 표기 | `capability_manuscript.md` §4-6 — `SB s15`는 양수도 계약서, `SB s16`은 재양도합의서. 계약 골격상 투자자 서명 대상은 **재양도 합의서** |

**요율 정정 조와의 관계** — `rate_fix_map.json`의 `no_change` 목록에 `certificate.html`·`contracts*.html`·
`acquisition*.html`·`merchants*.html`이 모두 들어 있어, 생성 문서가 읽는 화면은 요율 정정 대상이 아니다.
투자 금액·수익 수치가 들어가는 자리는 증명서 표 한 곳뿐이고 그 값은 `certificate.html`을 그대로 옮긴다.
`corrected` 값을 별도로 대입해야 하는 자리는 없다.

**요율 자체는 채택하지 않음** — 계약서 제8조 수수료표의 채권매입수수료율은 원 계약서와 같이 `_______ %`
공란으로 두었다(C1 미확정). 확정된 이체수수료 300원(VAT 별도, 제17조)만 기재. 증명서의
W금융일수·S입금부족율·Ty수익율에는 `예시값` 표기를 붙였다.

---

## §3 배선 결과

배선 스크립트 `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/wire_docs.py`
(계약기록 `선택 문서 다운로드` 3건은 이후 별도 패치).

| 대상 | 건수 | 교체 | 화면 |
|---|---|---|---|
| 계약서 파일 링크 | 24 | `href="#"` → `assets/docs/재양도합의서_<MID>.pdf` (`target="_blank"`) | `contracts` `--all` `--downloaded` |
| 계약서 보기 | 10 | `href="#"` → `assets/docs/계약서_서명대기_<MID>.pdf` | `acquisition` `--confirm` `--signing` `--done` |
| 선택 문서 다운로드 | 3 | `<button>` → `<a href="assets/docs/…zip" download>` (클래스·내용 유지) | `contracts` `--all` `--downloaded` |
| 로고 | 18 | `href="#"` → `index.html` | `acquisition*` `contracts*` `coocon*` `merchants*` `password*` |
| 비밀번호 찾기 | 1 | `<a href="#">` → `<span class="link-off" aria-disabled="true" title="…">` + 흐린 색·`cursor:not-allowed` | `login` |
| **합계** | **56** | | |

**로고 목적지를 `index.html`로 정한 근거** — ①`README.md`가 `index.html`을 정적 화면 세트의 랜딩·진입점으로
규정한다. ②개별 HTML은 "Figma 네이티브 임포트용 정적 원본(1파일=1프레임)"이고 `app.html`은 별개의
조작형 프로토타입이라, 정적 프레임에서 프로토타입으로 넘어가면 산출물 종류가 바뀐다.
③`app.html` 자신의 로고 핸들러가 `go('index')`이고 그 `index` 뷰의 이름이 `랜딩 갤러리`다 —
통합본이 이미 로고→랜딩으로 동작하고 있어 정적 화면도 같은 목적지가 맞는다.

**비밀번호 찾기를 비활성으로 둔 근거** — 재설정 화면 자체가 이번 설계안 범위 밖(D-2)이라 이동시킬 대상이
없다. 툴팁 문구 `비밀번호 찾기 화면은 이번 설계(안) 범위 밖(D-2). 발급·재설정은 페이허그 담당자 문의.`

**We-bank** — 슬라이드10 이미지 주소창의 주소를 그대로 쓴다. 화면·모달·`app.html`의 5개 지점이 동일 문자열이다.

### 3-1. 실측 검증

로컬 서버 `http://localhost:8901`로 배선된 링크 전량을 요청해 응답 확인.

- 실물 링크 **41건 / 고유 파일 17개** (`assets/docs` 13 = PDF 11 + zip 2, `assets/xlsx` 4) — 전건 `200`.
- PDF는 매직바이트 `%PDF-`, zip은 `PK` 확인. 응답 바이트 수가 디스크 파일 크기와 전건 일치.
- zip 2종 `testzip()` 무결성 OK, 파일명 UTF-8 플래그 설정 확인(한글 파일명 정상).
- 잔여 `href="#"` **15건** — 전부 §4 대상 파일.
- PDF 20개 전 페이지에 견본 머리띠가 그려졌는지 콘텐츠 스트림에서 확인 — 62/62면 일치.
- 한글 렌더링 — `Apple SD Gothic Neo` 적용, 래스터화 검수에서 깨짐 없음.

---

## §4 잔여 배선 지시서

요율 정정 조 작업이 끝난 뒤 적용한다. 형식 — `파일:위치:현재값:교체값`.

### 4-1. 증명서 PDF 다운로드 (실물 있음, 배선만 남음)

```
certificate.html : "PDF 다운로드" 버튼 (파일 끝 aside.cert-aside 안, 현재 <button class="btn btn-primary" style="width:100%">)
  현재값 : <button class="btn btn-primary" style="width:100%">
  교체값 : <a class="btn btn-primary" style="width:100%" href="assets/docs/투자자산증명서_20260827.pdf" download>
  닫는태그: </button> → </a>
```

### 4-2. 로고 15건 (실물 있음, 배선만 남음)

아래 파일의 `<div class="sidebar-logo">` 바로 다음 줄.

```
invest-assets.html / invest-assets--page2.html / invest-assets--download.html /
invest-assets--cert-confirm.html / invest-assets--empty.html /
invest-profit.html / invest-profit--monthly.html / invest-profit--datepicker.html /
invest-profit--empty.html /
xls-assets-status.html / xls-assets-merchant.html / xls-profit-status.html / xls-profit-daily.html /
certificate.html
  현재값 : <a href="#">
  교체값 : <a href="index.html">

app.html : 437행
  현재값 : <a href="#">
  교체값 : 그대로 둔다 — 2300행 핸들러 `if(t.closest('.sidebar-logo a')){ e.preventDefault(); go('index'); }`
           가 이미 랜딩으로 보낸다. SPA 내부 이동이라 href 교체는 오히려 페이지를 벗어나게 만든다.
```

### 4-3. `app.html` — 파일 없이 성공을 주장하는 토스트

`app.html`은 `build_app.py`가 생성한다. **원본은 `build_app.py`이므로 거기서 고치고 재빌드한다.**

```
build_app.py : 1962행  ACT['cert-pdf']
  현재값 : ACT['cert-pdf']  = function(){ showToast('투자자산 증명서 PDF 내려받기 완료', null, 3200); };
  교체값 : ACT['cert-pdf']  = function(){
             var a = document.createElement('a');
             a.href = 'assets/docs/투자자산증명서_20260827.pdf';
             a.download = '투자자산증명서_20260827.pdf';
             document.body.appendChild(a); a.click(); a.remove();
             showToast('투자자산증명서_20260827.pdf 내려받기 완료', null, 3200);
           };
  주의   : 증명서 화면의 버튼 마크업(546행 부근 · 843~857행 모달과 무관)에 data-act="cert-pdf"가
           걸려 있는지 확인할 것. 없으면 xls-get 처럼 <a href download data-act> 형태로 바꾸는 편이 낫다.

build_app.py : 2083~2087행  ACT['ct-download']
  현재값 : 상태만 바꾸고 파일을 주지 않는다. 이어서 1589행이
           showToast('재양도합의서 ' + ctSelCount() + '건 내려받기 완료', '각 문서에 서명 검증 회신전문 포함.')
           를 띄운다 — 회신전문은 실물이 없으므로 이 부제는 사실이 아니다.
  교체값 : 선택 건수에 맞는 묶음을 실제로 내려준 뒤 토스트를 띄운다.
           전체 선택 → assets/docs/재양도합의서_전체16건_20260827.zip
           부분 선택 → 정적 zip 2종으로는 임의 조합을 못 만든다. 아래 둘 중 하나를 택한다.
             (a) 전체 묶음을 내려주고 토스트를 '재양도합의서 전체 16건 내려받기 완료'로 고정
             (b) 선택된 MID 별로 개별 PDF를 순차 내려받기
  1589행 부제 : '각 문서에 서명 검증 회신전문 포함.' → '서명 검증 회신전문은 형식·전달 경로 미정의(§4-15).'

build_app.py : 2069행  ACT['aq-doc']  — 이제 실물이 있다
  현재값 : ACT['aq-doc'] = function(el){ showInfo('계약서 원문 미리보기는 이번 설계 범위 밖. 대상 ' + SIGNQ[parseInt(el.dataset.i, 10)].name); };
  교체값 : ACT['aq-doc'] = function(el){
             var mid = SIGNQ[parseInt(el.dataset.i, 10)].mid;
             window.open('assets/docs/계약서_서명대기_' + mid + '.pdf', '_blank');
           };
  전제   : SIGNQ 항목에 mid 필드가 있어야 한다. 없으면 name → mid 대조표를 붙인다.
           현재 대상 3건 = 김성호떡볶이 본점 M2026-0001 · 달빛곱창 홍대점 M2026-0002 · 바다마루 횟집 M2026-0004

build_app.py : 2088행  ACT['ct-file']  — 이제 실물이 있다
  현재값 : ACT['ct-file'] = function(el){ showInfo('재양도합의서 원문 파일은 이번 설계 범위 밖. 대상 ' + el.dataset.mid); };
  교체값 : ACT['ct-file'] = function(el){
             window.open('assets/docs/재양도합의서_' + el.dataset.mid + '.pdf', '_blank');
           };
```

### 4-4. 가맹점 행 클릭 (실물 없음 — 문구·표현 정리)

```
merchants.html / merchants--filtered.html / merchants--filter-open.html : <tr class="clickable">
  현재값 : cursor:pointer 로 상세 화면을 암시하나 목적지가 없다. 정적 화면에는 안내도 없다.
  교체값 : 아래 둘 중 하나.
           (a) clickable 클래스를 떼어 커서 암시를 없앤다
           (b) app.html 과 같은 안내('가맹점 상세 화면은 이번 설계 범위 밖')를 표 하단 주석으로 붙인다
  판단 근거 : 상세 화면 신설 여부가 결정되기 전에는 (b)가 안전하다.
```

### 4-5. 16건 로스터 확장 시 (다른 조 진행 중)

`contracts*`·`merchants*`가 `총 16건`·2페이지 버튼을 내걸었으나 마크업 행은 8개다.
2페이지 행이 들어오면 새 행의 파일 링크가 다시 `href="#"`가 된다.

```
재양도합의서 PDF M2026-0009 ~ M2026-0016 8종은 이미 생성돼 있다(assets/docs/).
새 행 배선 : href="#" → assets/docs/재양도합의서_<MID>.pdf  (target="_blank" rel="noopener")
전체 묶음  : assets/docs/재양도합의서_전체16건_20260827.zip 이 16건을 이미 담고 있어 교체 불필요.
증명서     : certificate.html 표가 바뀌면 build_docs.py 를 다시 돌린다 — 표를 실시간으로 읽어 반영한다.
```

### 4-6. 재생성 절차

화면 수치가 바뀐 뒤에는 아래 한 줄로 문서 22개를 다시 만든다. 배선은 파일명이 같아 그대로 유지된다.

```
python3 /Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/build_docs.py
```

증명서 파일명은 `certificate.html`의 작성일자를 따른다. 기준일이 바뀌면 파일명도 바뀌므로
§4-1 배선 경로를 함께 고친다.

---

## §5 실물을 만들지 않기로 한 것과 사유

| 대상 | 사유 |
|---|---|
| **서명 검증 회신전문** | 형식(xml·txt·pdf)도 전달 경로(단건/zip)도 미정의(`capability_manuscript.md §4-15`). 형식을 지어내면 그 자체가 새 사실 주장이 된다. zip `README.txt`에 미포함 사실과 사유를 적어 공백을 드러내는 쪽을 택했다 |
| **전자서명값·인증서 검증 회신** | 실제 인증서 서명을 만들 수 없고 만들어서도 안 된다. 견본 PDF는 서명란을 빈칸으로 두고 `견본 — 서명 없음`으로 표기했다. 증명서 PDF의 서명값은 화면 표시 문자열을 그대로 옮기되 `견본 — 실제 서명값이 아니며 검증할 수 없다`를 붙였다 |
| **We-bank 이동 URL** | 별도로 만들 실물이 없다. 주소 자체는 스토리보드 슬라이드10 삽입 이미지 주소창에 축자로 있어 근거가 있고, 목적지는 페이허그 밖 외부 콘솔이다 |
| **비밀번호 재설정 화면** | 화면 자체가 D-2로 범위 밖. 화면을 새로 만드는 것은 이 작업의 범위가 아니다. 비활성 + 사유 툴팁으로 처리 |
| **가맹점 상세 화면** | 같은 이유. 상세 화면 신설 여부가 미결이라 목적지를 만들면 범위를 임의로 넓히게 된다. §4-4에 표현 정리 지시만 남겼다 |
| `contracts--empty.html` **선택 문서 다운로드** | 총 0건·선택 0건 상태이고 버튼도 `disabled`다. 내려줄 대상이 없는 것이 정상 동작이라 배선하지 않았다 |
| **계약서 양수 금액** | 정산채권 양수 화면이 가맹점명·계약 생성일 2개 필드만 노출하고 금액을 표시하지 않는다. 화면에 없는 값을 문서에 넣지 않았다 — 견본에는 `미확정 — 화면에 표시되지 않음`으로 적었다 |
| **채권매입수수료율** | C1 미확정. 원 계약서도 가맹점별 기입 공란이다. `_______ %`로 두고 어느 후보값도 넣지 않았다 |
| `archive.html`의 로컬 링크 89건 | `build_archive.py` 산출물로, 로컬 서버 2개를 띄우고 쓰는 작업용 추적 페이지다. 배포 대상이 아니고 페이지 상단에 전제 조건이 이미 적혀 있다 |
| **부분 선택 묶음 zip** | 체크박스 조합이 가변이라 정적 파일로는 임의 조합을 만들 수 없다. 화면이 명시한 두 조합(선택 3건 · 전체 16건)만 만들고 나머지는 §4-3에 런타임 처리 지시로 남겼다 |

---

## 부록 — 건드리지 않은 파일

`invest-assets*.html` · `invest-profit*.html` · `xls-*.html` · `app.html` · `build_app.py` ·
`assets/xlsx/` · `certificate.html` — 요율 정정 조 작업 범위. 읽기만 했고 쓰지 않았다.
`certificate.html`은 문서 실물만 만들어 두고 HTML 배선은 §4-1에 지시로 남겼다.

작업 중 다른 조가 `contracts*`·`merchants*`의 총건수를 8 → 16으로, `certificate.html` 표를
8행 → 16행으로 바꾸는 것이 관측됐다. 생성기는 화면을 실시간으로 읽으므로 16건 기준으로 산출됐다.
