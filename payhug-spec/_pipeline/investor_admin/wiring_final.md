# 잔여 배선 · 허위 주장 정리 — 결과

대상 저장소 `/Users/semi/cursor/payhug-investor-admin` · 기준 2026-08-27 18:20
작업 트리 수정까지이며 **커밋·push 없음.** 다른 저장소는 건드리지 않았다.

지시서 `artifact_gap.md` §4 · 확정 결정 `request_register.md` · 요율 기준 `rate_apply_result.md`.
숫자(금액·비중·요율)는 손대지 않았다. 비중 합은 정정 라운드가 닫아 둔 `100.0%` 그대로다.

적용 스크립트
- 정적 화면 — `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/wire_final.py` (재실행 가능)
- 통합본 — `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/build_app.py` 수정 후 재생성

---

## §1 잔여 배선

### 1-1. `href="#"` 15건

지시서 §4-2 대상. 실측 15건 = 정적 14 + `app.html` 1.

| 대상 | 건수 | 처리 |
|---|---|---|
| 사이드바 로고 — `invest-assets*`(5) · `invest-profit*`(4) · `xls-*`(4) · `certificate`(1) | 14 | `href="#"` → `href="index.html"` |
| 사이드바 로고 — `app.html` | 1 | 현행 유지. 클릭 위임 `if(t.closest('.sidebar-logo a')){ e.preventDefault(); go('index'); }` 가 이미 랜딩으로 보낸다. `href` 를 채우면 SPA 밖으로 나가 오히려 화면을 벗어난다 |

잔여 `href="#"` **1건**(`app.html` 로고, 위 사유로 의도적 유지).

### 1-2. 지시서 §4-1 · §4-3 · 비밀번호 찾기

| # | 대상 | 전 | 후 |
|---|---|---|---|
| 1 | `certificate.html` `PDF 다운로드` | `<button class="btn btn-primary">` 무동작 | `<a … href="assets/docs/투자자산증명서_20260827.pdf" download>` |
| 2 | `app.html` `ACT['cert-pdf']` | 파일 없이 토스트 | 버튼을 `<a href download data-act="cert-pdf">` 로 바꾸고 `KEEP_DEFAULT` 에 등록해 브라우저가 실제로 내려받게 함 |
| 3 | `app.html` `ACT['aq-doc']` | `showInfo('… 이번 설계 범위 밖')` | `<a class="doc-link" href="assets/docs/계약서_서명대기_<MID>.pdf" target="_blank" rel="noopener">`. `SIGNQ` 에 `mid` 3건(`M2026-0001`·`-0002`·`-0004`) 추가 |
| 4 | `app.html` `ACT['ct-file']` | `showInfo('… 이번 설계 범위 밖')` | `<a class="file-link" href="assets/docs/재양도합의서_<MID>.pdf" target="_blank" rel="noopener">` · `CONTRACTS` 16행 전건 |
| 5 | `app.html` `ACT['ct-download']` | 상태만 바꾸고 파일 없음 | 선택 조합에 맞는 실물을 내려준 뒤 토스트. §2-2 참조 |
| 6 | `app.html:1041` 비밀번호 찾기 | `span.link-off` + 툴팁은 있었으나 `.link-off` CSS 가 통합본에 없어 흐린 색·`cursor:not-allowed` 가 적용되지 않음 | `build_app.py` CSS 블록에 `.login-links .link-off` 규칙 추가 — `login.html` 과 동일한 비활성 표시 |

`aq-doc`·`ct-file`·`cert-pdf` 의 대상 파일은 `assets/docs/` 에 이미 있는 실물이다(PDF 20 · zip 2, 총 22개).

### 1-3. 배선 링크 실측

`verify_links.py` — 루트 HTML 전량의 로컬 링크를 로컬 서버 `http://localhost:8901` 로 요청해 응답 바이트를 디스크 파일 크기와 대조.

| 항목 | 값 |
|---|---|
| 로컬 링크 고유 | 58개 / 참조 420건 |
| `assets/docs` | 고유 14개 · 참조 39건 |
| `assets/xlsx` | 고유 4개 · 참조 4건 |
| 판정 | **80건 전건 HTTP 200 · 바이트 일치 · FAIL 0** |

`app.html` 이 코드로 조립하는 경로(`CERT_PDF`·`CT_ZIP_ALL`·`CT_ZIP_SEL3`·`재양도합의서_<MID>`·`계약서_서명대기_<MID>`)는 문자열이라 정적 스캔에 안 잡히므로 같은 스크립트에서 파일 존재를 별도 대조한다.

---

## §2 허위 주장 정리

원칙 — 실물을 주거나, 주지 않는다고 말하거나. 화면이 자기 동작·산출물에 대해 하는 단정만 고쳤고, 표에 실린 예시 데이터 값은 건드리지 않았다.

### 2-1. 증명서 PDF 토스트

| | 내용 |
|---|---|
| 전 | `ACT['cert-pdf'] = function(){ showToast('투자자산 증명서 PDF 내려받기 완료', null, 3200); };` — 파일이 나가지 않음 |
| 후 | 버튼이 `assets/docs/투자자산증명서_20260827.pdf` 를 실제로 내려주고, 토스트가 그 파일명을 그대로 부른다 |
| 근거 | 문서 실물이 `build_docs.py` 산출물로 이미 있었다(372,443 B, 2면). 배선만 없던 상태 |

### 2-2. 재양도합의서 묶음 다운로드

| | 내용 |
|---|---|
| 전 | 상태만 바뀌고 파일 없음. 토스트 `재양도합의서 N건 내려받기 완료` + 부제 `각 문서에 서명 검증 회신전문 포함.` |
| 후 | 선택 조합에 맞는 실물을 내려준 뒤 토스트가 **내려간 것을 그대로 부른다** |

전달 규칙 — `assets/docs/` 에 실재하는 파일만 쓴다.

| 선택 | 내려주는 것 | 토스트 |
|---|---|---|
| 전체 16건 | `재양도합의서_전체16건_20260827.zip` | `…zip 내려받기 완료` · `재양도합의서 16건 묶음.` |
| `M2026-0001`·`-0004`·`-0006` (기본 상태 3건) | `재양도합의서_선택3건_20260827.zip` | `…zip 내려받기 완료` · `재양도합의서 3건 묶음.` |
| 그 밖의 임의 조합 | 선택된 MID의 개별 PDF를 순차 전달 | `재양도합의서 N건 내려받기 완료` · `개별 PDF N개.` |

정적 zip 2종으로는 가변 조합을 만들 수 없어 임의 조합은 개별 PDF로 내려준다(지시서 §4-3 (b)안). 토스트가 부르는 수와 실제로 나간 파일 수가 항상 같다.

**부제 `각 문서에 서명 검증 회신전문 포함.` 는 삭제했다.** `build_docs.py` 산출물을 열어 확인한 결과 zip 안 `README.txt` 가 `담기지 않은 것 — 서명값, 그리고 인증서 발행기관의 서명 검증 회신전문` 이라고 적고 있다. 화면 부제와 실물이 정면으로 어긋났다. 새 부제는 `서명 검증 회신전문 미포함 — 형식·전달 경로 확인 대상.`

토스트는 사용자가 버튼을 누른 경로뿐 아니라 **상태 진입(해시 딥링크·상태 전환 독)** 경로에서도 뜬다. 어느 쪽이든 파일이 나가도록 전달 지점을 `syncToast` 한 곳으로 모으고, 같은 상태 안에서 표를 다시 그릴 때 중복 전달되지 않게 `toastServed` 로 잠갔다. `invest-assets/download` 상태의 엑셀 토스트도 같은 방식으로 실물을 동반하게 했다.

### 2-3. 서명 검증 회신전문 표현

실물·형식·전달 경로가 모두 없다(`capability_manuscript.md` §4-15 — 회신전문 형식(xml·txt·pdf)과 묶음 다운로드 API 미정의). 형식을 지어내지 않고, 존재를 단정하는 표현만 `확인 대상` 으로 낮췄다.

| 위치 | 전 | 후 |
|---|---|---|
| `contracts` `--all` `--downloaded` `--empty` · `app.html` 표 하단 | 다운로드 시 … 재양도합의서 파일과 서명 검증 회신전문이 함께 제공됨. | 다운로드 시 … 재양도합의서 파일이 제공됨. 서명 검증 회신전문은 형식·전달 경로 미정의 — 확인 대상. |
| `contracts--downloaded` 토스트 | `재양도합의서 8건 내려받기 완료` / `각 문서에 서명 검증 회신전문 포함.` | `재양도합의서_전체16건_20260827.zip 내려받기 완료` / `재양도합의서 16건 묶음. 서명 검증 회신전문 미포함 — 형식·전달 경로 확인 대상.` |
| `certificate` · `app.html` 발급 안내 | 전자문서에는 … 서명값과 인증서 발행기관의 서명 검증 회신전문이 함께 포함됨. | 전자문서에 … 서명값을 표시함. 인증서 발행기관 검증 회신전문은 형식·전달 경로 미정의 — 확인 대상. |
| `invest-assets--cert-confirm` · `app.html` 발급 모달 | 발급 문서에는 … 검증 회신전문이 포함됨. | 발급 문서에 … 서명값을 표시함. 인증서 발행기관 검증 회신전문은 확인 대상. |
| `acquisition--signing` · `app.html` 서명 단계 3 | 인증서 발행기관 검증 회신전문 수신 전. | 인증서 발행기관 검증 회신 대기. |
| `acquisition--done` · `app.html` 완료 안내 | 서명값과 인증서 발행기관의 검증 회신전문이 계약기록에 보관됨. | 서명값은 계약기록에 보관됨. 인증서 발행기관 검증 회신전문의 형식·보관 경로는 확인 대상. |
| `capability.html` 비교표 `문서 산출` | 엑셀 4종 + 투자자산 증명서(전자서명·검증회신전문 포함) + 재양도합의서 원본·검증회신전문 | 엑셀 4종 + 투자자산 증명서(전자서명값 표시) + 재양도합의서 원본. 검증회신전문 동봉은 확인 대상 |

`contracts--downloaded` 토스트의 `8건` → `16건` 은 숫자 정정이 아니라 **같은 화면 안의 모순 해소**다. 그 화면은 이미 `총 16건` · `16건 선택` · 버튼 `선택 문서 다운로드 (16)` 이고 링크도 전체 16건 zip인데 토스트만 8건으로 남아 있었다.

`capability.html` 의 확인 질문 항목(§4-8 전자서명·인증서 연동 부재, §4-15 계약문서 일괄 다운로드 경로 없음)과 노출 항목표는 스토리보드 요구를 출처와 함께 적은 것이라 그대로 뒀다.

### 2-4. 증명서 서명값 `검증 완료`

| | 내용 |
|---|---|
| 전 | `<span class="badge badge-green">서명 검증: 인증서 발행기관 검증 회신 완료</span>` — `sig-value` 문자열 바로 아래에서 검증이 끝났다고 단정 |
| 후 | `<span class="badge badge-gray">서명값 표시 — 검증 결과 미표기(확인 대상)</span>` |
| 대상 | `certificate.html` · `app.html` 증명서 화면 |

근거 — ① 인증서 서명 모듈이 운영 코드에 없다(`capability_manuscript.md` §4-8, `capability.html` 데이터 미존재 판정). ② 화면의 `sig-value` 는 `SB s6` 예시 문자열을 옮긴 것이라 검증할 수 있는 값이 아니다. ③ `build_docs.py` 가 만든 증명서 PDF 자체가 서명값 칸에 `견본 — 실제 서명값이 아니며 검증할 수 없다`, 서명 검증 칸에 `견본 문서 — 인증서 발행기관 검증 회신전문 미첨부` 라고 적는다. 화면만 검증 완료라고 말하고 있었다.

**서명값 문자열은 지우지 않았다.** 표시까지는 사실이고, 없앨 근거도 없다. 초록 배지(성공)에서 회색 배지(중립)로 내린 것도 검증 결과를 색으로도 단정하지 않기 위해서다.

계약기록 표 `검증` 열의 행별 `검증 완료` 배지는 **손대지 않았다.** 그 열은 계약 건별 상태를 담는 데이터 칸이고, 표의 다른 예시 값(MID·가맹점명·서명일)과 같은 층위다. 화면이 자기 동작에 대해 하는 단정이 아니라 원장 값의 예시라서 정리 대상과 구분했다. 이 열을 실제로 어떻게 채울지는 §5에 확인 질문으로 남겼다.

### 2-5. 가맹점 행 클릭

목적지가 될 상세 화면이 없다(`request_register.md` D-2 범위 밖).

| | 내용 |
|---|---|
| 전 | `<tr class="clickable">` — `cursor:pointer` 와 hover 배경으로 상세 이동을 암시. 정적 화면에는 안내조차 없었다 |
| 후 | 정적 3개 파일(`merchants` 8행 · `--filtered` 2행 · `--filter-open` 8행) `clickable` 제거 · 통합본은 `tr.clickable[data-act="mc-row"]` → 평범한 `<tr>` 로 바꾸고 `ACT['mc-row']` 삭제. 표 하단에 `가맹점 상세 화면은 이번 설계(안) 범위 밖. 행 클릭 목적지 없음.` |

클릭 암시를 없애는 것과 사유를 밝히는 것을 함께 했다. `merchants--empty.html` 은 표 행 자체가 없어 대상이 아니다.

### 2-6. 표 건수 16 vs 화면 행 8

로스터는 16건 확정(`rate_apply_result.md` §3). 페이지 크기가 8이라 1쪽에 8행이 그려지는 것은 정상 동작인데, 화면이 `총 16건` 만 적고 지금 몇 행을 보여주는지는 말하지 않아 건수와 행 수가 어긋나 보였다.

| | 내용 |
|---|---|
| 후 | 총 건수 옆에 표시 구간을 병기 — `총 16건 · 표시 1–8` |
| 대상 | 정적 `contracts` `--all` `--downloaded` · `merchants` `--filter-open` (총 건수 > 페이지 크기인 화면만) |
| 통합본 | `rangeLabel(cur, pages, total)` 를 `RENDER['contracts']` · `RENDER['merchants']` 에 적용. 2쪽으로 넘기면 `표시 9–16` 으로 따라간다. 1쪽뿐이면 표기하지 않는다 |

**숫자는 움직이지 않았다.** 총 건수·행 데이터·금액·비중을 전혀 건드리지 않고 표시 구간 문구만 덧붙였다. 통합본은 원래부터 16행을 두 쪽에 나눠 그리고 있었고, 정적 프레임은 1쪽 단면이라 8행이 맞는다.

---

## §3 재검증

전 검증기 창 없이(`--headless=new`) 실행.

| 검증기 | 기준 | 결과 |
|---|---|---|
| `verify_app.js` | 70 PASS / 0 FAIL · 죽은 버튼 0 · 콘솔 에러 0 | **71 PASS / 0 FAIL** · 죽은 컨트롤 **0 / 검사 215건** · 콘솔 에러 **0** |
| `verify_identity.js` | 항등식 14건 PASS · 비중 합 100.0% | **14건 PASS / FAIL 0** · 비중 합 **100.0%** · 콘솔 에러 0 |
| `verify_crossscreen.py` | 정적 ↔ `app.html` ↔ `.xlsx` 23건 일치 | **23건 · 불일치 0** |
| `verify_links.py` (신규) | 배선 링크 전건 HTTP 200 + 바이트 일치 | **80건 · FAIL 0** |
| `verify_toast.js` (신규) | 토스트가 주장하는 일이 실제로 일어나는지 | **10건 · FAIL 0** · 콘솔 에러 0 |

### 3-1. `verify_app.js` 70 → 71 의 내역

판정 논리는 그대로 두고 **검사 항목 1건을 더했다.** 기존 70건은 전건 PASS 를 유지한다.

| 묶음 | 기준 | 지금 |
|---|---|---|
| 메뉴 7 | 7 PASS | 7 PASS |
| 상태 20 | 20 PASS | 20 PASS |
| 다운로드 4 | 4 PASS | 4 PASS |
| 값 변화 5 | 5 PASS | **6 PASS** (§6에서 고친 업종 드롭다운 검사 1건 추가) |
| 레이아웃 34 | 34 PASS | 34 PASS |
| **합** | **70** | **71** |

### 3-2. 토스트 실물 대조 10건

`verify_toast.js` — `app.html` 안의 `완료` 주장 문구 4개를 소스에서 전수로 뽑고, 그 문구가 뜨는 경로 10가지를 실제로 밟아 파일이 내려왔는지 바이트로 대조.

| 경로 | 토스트 | 내려온 파일 |
|---|---|---|
| `xls-get` ×4 | `<파일명> 내려받기 완료` | xlsx 4종 · 바이트 일치 |
| `cert-pdf` | `투자자산증명서_20260827.pdf 내려받기 완료` | 372,443 B 일치 |
| `ct-download` 기본 3건 | `재양도합의서_선택3건_20260827.zip 내려받기 완료` | 608,829 B 일치 |
| `ct-download` 전체 16건 | `재양도합의서_전체16건_20260827.zip 내려받기 완료` | 3,257,835 B 일치 |
| `ct-download` 임의 2건 | `재양도합의서 2건 내려받기 완료 · 개별 PDF 2개.` | PDF 2개 · 각 바이트 일치 |
| 상태 진입 `#contracts/downloaded` | 전체 16건 zip | 일치 |
| 상태 진입 `#invest-assets/download` | 가맹점별 투자자산 xlsx | 일치 |

`완료`라고 말하면서 아무 일도 일어나지 않는 경로는 남아 있지 않다.

### 3-3. 아카이브

`python3 build_archive.py` 로 `archive.html` 재생성 완료.

---

## §4 근거가 없어 만들지 않은 것

| 대상 | 사유 |
|---|---|
| **서명 검증 회신전문** | 형식(xml·txt·pdf)도 전달 경로(단건/zip)도 미정의(`capability_manuscript.md` §4-15). 형식을 정하는 순간 그 자체가 새 사실 주장이 된다. 실물을 만들지 않고 화면 표현을 `확인 대상` 으로 낮췄다 |
| **전자서명 검증 로직·검증 결과** | 인증서 서명 모듈이 운영 코드에 없다(§4-8). 검증할 수 없는 문자열에 검증 결과를 붙이지 않는다. 서명값 표시까지만 남겼다 |
| **가맹점 상세 화면** | D-2 범위 밖. 목적지를 새로 만들면 범위를 임의로 넓히게 된다. 클릭 암시를 없애고 사유를 표에 적었다 |
| **비밀번호 재설정 화면** | 같은 이유. 비활성 + 사유 툴팁으로 두고 통합본에도 같은 표시가 나오도록 CSS만 맞췄다 |
| **We-bank 이동 URL** | 근거 없는 임의 추가로 분류된 상태. 살아 있는 주소라는 사실이 채택 근거가 되지 않는다. 넣지도 바꾸지도 않았다 |
| **업종 코드 목록** | 운영 어드민에 업종 필터 자체가 없고(`app/manage/page.tsx:223-255`, `services/merchantService.ts:199-205`) 업종 코드 상수도 없다. 가져올 목록이 없어 원장에 실재하는 값만 남겼다. §6-2 |
| **부분 선택 묶음 zip** | 체크박스 조합이 가변이라 정적 파일로 못 만든다. 화면이 명시한 두 조합만 zip 으로 두고 나머지는 개별 PDF 전달로 처리했다 |
| **채권매입수수료율** | C1 미확정. 견본 계약서는 원 계약서와 같이 `_______ %` 공란, 증명서 지표에는 `예시값` 표기 유지 |
| **계약기록 `검증` 열의 실제 판정 로직** | 검증 회신 자체가 미정의라 판정 규칙을 만들 수 없다. 예시 데이터로 두고 §5에 질문으로 남겼다 |

---

## §5 남은 확인 질문

| # | 질문 | 배경 |
|---|---|---|
| 5-1 | 서명 검증 회신전문의 **형식**(xml·txt·pdf)과 **전달 경로**(단건 첨부 / zip 동봉 / 별도 API)를 무엇으로 정합니까? | 화면 6곳이 회신전문을 말하는데 실물·형식·경로가 전무. 현재는 전부 `확인 대상` 표기 |
| 5-2 | 계약기록 표 `검증` 열은 **무엇을 근거로** `검증 완료`/미완료를 판정합니까? 회신전문 수신 여부입니까, 별도 상태값입니까? | 현재는 전 행 `검증 완료` 예시값. 판정 규칙이 서면 데이터 정의로 옮긴다 |
| 5-3 | 투자자산 증명서의 **전자서명 벤더·방식**을 정하고 나면 증명서 화면의 서명 표시를 어디까지 노출합니까? | 서명값 표시까지만 남기고 검증 결과 단정을 뺀 상태 |
| 5-4 | 가맹점 **상세 화면**을 신설합니까? 신설하면 목록 행 클릭이 진입점이 됩니까? | 현재는 클릭 암시를 없애고 범위 밖임을 표에 적어 둔 상태 |
| 5-5 | We-bank 이동 대상 **URL**을 무엇으로 확정합니까? | 임의 URL 채택 금지 상태 유지 |
| 5-6 | 가맹점 화면의 **업종 필터를 유지**합니까? | 스토리보드 `SB s14` 는 요구하나 운영 어드민에는 필터도, 목록 API 파라미터도, 업종 코드 목록도 없다(`capability_manuscript.md` §275 `확인필요`). 유지한다면 코드 목록의 출처가 필요하다 |
| 5-7 | 업종 필터 UI 를 **네이티브 `<select>` 로 바꿉니까?** | §6-2 참조. 운영 어드민은 커스텀 드롭다운을 쓰지 않는다. 바꾸면 `merchants--filter-open`(필터 열림) 상태 화면이 보여 줄 대상을 잃는다 |
| 5-8 | 비밀번호 **재설정 화면**을 이번 범위에 넣습니까? | 넣지 않으면 현재의 비활성 + 툴팁이 최종 |

---

## §6 죽은 컨트롤 재검사

### 6-1. 검사 범위를 넓힌 내용

기존 `verify_app.js` 의 죽은 버튼 검사는 후보를 `button, a[href], [data-act], input[type=checkbox], tr.clickable, .dd-opt, select` **선택자 목록**으로 뽑았다. 태그를 열거하는 방식이라 목록에 없는 형태는 통째로 빠질 수 있다. 후보 선정을 **`클릭 가능해 보이는가`** 로 바꿨다.

후보 조건(하나라도 해당하면 컨트롤)
- 네이티브 — `button` · `select` · `a[href]` · `input[type=checkbox|date]`
- 위임 — `[data-act]` · `[data-nav]` · `[onclick]`
- 시맨틱 — `role` 이 `button`·`link`·`option`·`tab`·`menuitem`
- 포커스 — `tabindex` 가 `-1` 이 아닌 것
- 관용 클래스 — `.clickable` · `.dd-trigger` · `.dd-opt`
- **계산된 `cursor: pointer`** — 태그·클래스와 무관하게 클릭을 약속하는 시각 신호

버튼 안의 `span`·`svg` 가 중복으로 잡히지 않도록 **조상 중 컨트롤이 있으면 제외**해 가장 바깥 것만 센다.

판정 신호도 늘렸다. 클릭 전후로 아래 중 하나라도 달라져야 산 것으로 본다.
`body.innerHTML` 해시 · 문서 길이 · `location.hash` · 열린 모달 id · 토스트 표시 여부 · **토스트 문구** · **표 `tbody` 행 수** · **문서 전체 요소 수** · **포커스 위치**

제외 규칙 하나를 더했다 — `aria-disabled="true"`. 사유를 밝히고 꺼 둔 컨트롤(비밀번호 찾기)은 아무 일도 안 하는 것이 정상 동작이라 죽은 것과 구분한다.

### 6-2. 색출 결과

30개 화면·상태 조합을 다시 훑었다.

| 회차 | 검사 | 죽은 컨트롤 | 키보드·보조기술 미도달 |
|---|---|---|---|
| 넓히기 전 | (선택자 목록) | 0 | 검사 안 함 |
| 넓힌 뒤 1회차 | 219건 | 1 | **84** |
| 고친 뒤 | 215건 | **0** | **0** |

**클릭 동작이 죽은 것은 없었다.** 1회차의 1건은 `login` 의 `비밀번호 찾기`(`span.link-off`, `aria-disabled="true"`) 로, 사유 툴팁을 달고 의도적으로 꺼 둔 것이다. 검사기에 `aria-disabled` 제외 규칙을 넣어 정상 판정으로 돌렸다.

실제로 나온 결함은 **키보드·보조기술로 닿을 수 없는 컨트롤 84건**이었다. `div`·`th` 로 만들어 마우스로는 눌리지만 `role`·`tabindex` 가 없어 접근성 트리에 안 잡히고 키보드로도 못 누른다. 업종 드롭다운이 브라우저 조작에서 "눌러도 아무것도 안 열린다"로 관측된 것이 이 결함이다 — 클릭 자체는 되지만 접근성 트리로 접근하면 컨트롤이 보이지 않는다.

| 종류 | 건수 | 전 | 후 |
|---|---|---|---|
| 정렬 머리글 `th[data-act=sort]` | 70 | `<th class="sortable" data-act="sort">` | `role="columnheader"` · `tabindex="0"` · `aria-sort="ascending\|descending\|none"` · `aria-label="<열> 기준 정렬"` 추가. `Enter`·`Space` 로 정렬되고, 표를 다시 그린 뒤에도 같은 머리글로 포커스가 돌아온다 |
| 업종 드롭다운 트리거 `div.dd-trigger` | 4 | 속성 없는 `div` | `role="combobox"` · `tabindex="0"` · `aria-haspopup="listbox"` · `aria-expanded`(열림 상태에 따라 갱신) · `aria-controls="mc-dd-list"` · `aria-label="업종"` |
| 업종 드롭다운 옵션 `div.dd-opt` | 4 | 속성 없는 `div` | 목록에 `role="listbox"`, 항목에 `role="option"` · `aria-selected` · `tabindex`(선택 항목만 `0`) |
| 뒤로가기 링크 `a.back-link` | 5 | `href` 없는 `<a>` | `href="<대상>.html"` 부여. `data-nav` 위임은 그대로라 SPA 내부 이동은 유지되고, 링크로서 포커스·키보드가 산다 |
| 계약서 보기(서명 완료 행) `a.doc-link` | 1 | `href` 없는 `<a>` | `href="contracts.html"` 부여 |

키보드 조작을 `keydown` 위임으로 붙였다.
- 트리거 — `Enter`·`Space`·`ArrowDown` 으로 열고, 열리면 선택된 옵션으로 포커스가 옮겨간다. `Escape` 로 닫고 트리거로 복귀
- 옵션 — `ArrowUp`·`ArrowDown` 이동, `Enter`·`Space` 선택, `Escape` 취소. 고르면 포커스가 트리거로 돌아온다
- 정렬 머리글 — `Enter`·`Space` 로 정렬

접근성 트리 실측 — `Accessibility.getFullAXTree` 에서 `combobox:업종` · `columnheader:업종 기준 정렬` 노드가 잡힌다. 고치기 전에는 없던 노드다.

### 6-3. 업종 옵션 — 데이터에 없는 값 3개 제거

| | 내용 |
|---|---|
| 전 | `SECTORS = ['전체','음식점업','도소매업','서비스업','기타']` (통합본) · 정적 5개 |
| 후 | 원장에서 파생 — `['전체'] + MERCHANTS 의 고유 업종` = `['전체','음식점업']` |

근거 — ① 원장 16건의 업종은 전부 `음식점업` 이다. `도소매업`·`서비스업`·`기타` 를 고르면 항상 0건이 나온다. ② 운영 어드민에는 업종 필터가 없고 업종 코드 상수도 없어(`app/manage/page.tsx:223-255` 상태 탭만 존재, `services/merchantService.ts:199-205` 필터 파라미터는 `status`·`fromDate`·`toDate` 뿐) 가져올 목록이 없다. ③ `screen_inventory.md` M-7 이 이미 옵션 세트 불일치를 결함으로 등재해 뒀다.

통합본은 상수를 지우고 `MERCHANTS` 에서 뽑도록 바꿨다. 원장이 늘어 다른 업종이 들어오면 옵션이 따라 는다. 정적 `merchants` `--filtered` `--empty` `--filter-open` 도 같은 2개로 맞췄다.

### 6-4. 필터 적용 시 비중

**비중은 영향을 받지 않는다.** 가맹점 화면 표의 열은 `가맹점ID`·`가맹점명`·`사업자번호`·`대표자`·`업종`·`종목`·`채권매입업체ID` 7개로 금액도 비중도 없다. 비중은 투자 자산 화면(`invest-assets`)의 별도 표에 있고 가맹점 필터의 영향권 밖이다.

재검증에서 비중 합은 `100.0%` 그대로다 — `verify_app.js` selfcheck `ratioSum: 100`, `verify_identity.js` 항등식 14건 전건 PASS(정렬·기간·페이지 조작 뒤에도 `ratioSum 100`).

업종 필터 자체는 조건 칩 · 초기화 · 검색어 조합까지 정상 동작한다. 다만 원장이 단일 업종이라 **업종만으로는 행이 줄지 않는다.** 행이 줄어드는 모습은 `--filtered`(업종 + 검색어 `곱창` → 2행)·`--empty`(업종 + 검색어 `라멘` → 0건)에서 확인된다. 행을 줄여 보이려고 없는 업종의 가맹점을 지어내지 않았다.

### 6-5. 커스텀 드롭다운을 유지한 근거와 미결

운영 어드민 원본 코드 조사 결과.

| 확인 항목 | 결과 |
|---|---|
| 커스텀 드롭다운 컴포넌트 | **0건.** `components/` 에 Dropdown·Select·Listbox·Combobox 파일 없음. `package.json` 에 headlessui·radix·react-select 등 UI 라이브러리 없음 |
| 셀렉트형 입력 | **전부 네이티브 `<select>`** (33곳). 이 중 목록 필터 바에서 쓰는 것은 4곳 — `app/settlement/overview/page.tsx:364`(에이전시) · `app/scraping-incidents/page.tsx:227`(플랫폼)·`:239`(상태) · `app/activity-logs/page.tsx:219`(이벤트 유형) |
| 세 번째 유형 | 가맹점 목록·정산 목록의 주 필터는 `<select>` 가 아니라 **버튼 칩·탭 그룹**(`app/manage/page.tsx:225-241`, `app/settlement/overview/page.tsx:377-412`·`:435-465`) |
| 업종 필터 | **존재하지 않음.** `businessTypeMain`·`businessItemMain` 은 가맹점 상세의 읽기 전용 표시(`app/merchants/[id]/page.tsx:1048-1049`)와 파트너 프로필의 텍스트 입력(`app/partners/page.tsx:362-363`)뿐 |
| 접근성 속성 | 사실상 전무 — 전 저장소에서 `tabIndex` 0건, `aria-expanded`·`aria-haspopup`·`role="listbox"`·`role="option"`·`role="combobox"` 각 0건. 존재하는 것은 `role` 1곳·`aria-label` 1곳·`aria-pressed` 1곳 |

운영 어드민이 커스텀 드롭다운을 쓰지 않으므로 "그쪽 구현을 따르라"의 조건은 성립하지 않는다. 그렇다고 네이티브 `<select>` 로 통일하는 것도 안전하지 않다 — `merchants--filter-open`(업종 셀렉트 열림)은 확정 상태 화면 25종에 든 항목(`request_register.md` S)이고, 네이티브 `<select>` 의 팝업은 DOM 으로 그릴 수 없어 그 상태 화면이 보여 줄 대상을 잃는다.

그래서 **커스텀 구조는 유지하되 접근성 결함만 고쳤다.** 어느 쪽으로 통일할지는 상태 화면 존폐가 걸린 결정이라 §5-7 에 질문으로 남겼다. 옵션 값은 어느 쪽을 택하든 §6-3 대로 원장 파생이 맞는다.

---

## 부록 A — 손댄 파일

| 경로 | 내용 |
|---|---|
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/wire_final.py` | 정적 화면 배선·문구 정리 스크립트(신규, 재실행 가능) |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_links.py` | 배선 링크 실측 검증기(신규) |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_toast.js` | 토스트 실물 대조 검증기(신규) |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/verify_app.js` | 죽은 컨트롤 검사 범위·판정 신호 확장 + 업종 드롭다운 검사 1건 추가 |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/build_app.py` | 통합본 생성기 — 배선·문구·접근성·업종 옵션 |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/capability.html` | 비교표 `문서 산출` 셀 1개 |
| `/Users/semi/cursor/payhug-investor-admin/app.html` | `build_app.py` 재생성 산출물 |
| `/Users/semi/cursor/payhug-investor-admin/archive.html` | `build_archive.py` 재생성 산출물 |
| `/Users/semi/cursor/payhug-investor-admin/certificate.html` | 로고 · PDF 다운로드 배선 · 서명 배지 · 발급 안내문 |
| `/Users/semi/cursor/payhug-investor-admin/contracts.html` `--all` `--downloaded` `--empty` | 표 하단 안내문 · 표시 구간 · 다운로드 토스트 |
| `/Users/semi/cursor/payhug-investor-admin/merchants.html` `--filtered` `--filter-open` `--empty` | 행 클릭 표시 · 상세 부재 안내 · 표시 구간 · 업종 옵션 · 드롭다운 접근성 |
| `/Users/semi/cursor/payhug-investor-admin/acquisition--signing.html` `acquisition--done.html` | 회신전문 표현 |
| `/Users/semi/cursor/payhug-investor-admin/invest-assets*.html` `invest-profit*.html` `xls-*.html` | 사이드바 로고 |
| `/Users/semi/cursor/payhug-investor-admin/invest-assets--cert-confirm.html` | 발급 모달 안내문 |
| `/Users/semi/cursor/payhug-investor-admin/capability.html` | 비교표 `문서 산출` 셀 1개 |

## 부록 B — 작업 중 관측

작업 도중 `18:09` 에 다른 프로세스가 `review.html` 을 새로 만들고 `18:13` 에 `archive.html` 을 재기록했다. 두 파일 모두 이번 작업의 대상이 아니고 배선·문구·숫자와 겹치지 않는다. `archive.html` 은 마지막에 `build_archive.py` 로 다시 생성했다. `review.html` 은 손대지 않았다 — `verify_links.py` 의 링크 스캔 대상에는 포함돼 있고, 그 안의 JS 조립 경로는 정적 대조에서 제외된다.
