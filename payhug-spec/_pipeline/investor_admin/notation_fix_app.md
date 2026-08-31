# 아래첨자 표기 · 「만기」 교정 — build_app 계열

대상 파일 `build_app.py` `build_ops.py` `build_sigtext.py` `sync_assets_static.py`
`daily_ledger.py`(주석·독스트링) `platform_duration.py`(주석), 그리고 화면 짝인 `build_sim_static.py` 1줄.
산출 반영처 `/Users/semi/cursor/payhug-investor-admin` · `/Users/semi/cursor/payhug-investor-prototype`.

---

## 1. 전수 조사 결과 — 화면과 주석의 갈림

헤드리스 크롬으로 `app.html` 33개 상태쌍 · 시연본 32개 상태쌍의 `textContent` 를 전량 훑어
16개 토큰(`만기` · `Ai` `Di` `SLi` `SAi` `Api` `Dpi` · `BD-1i` `AD-1i` `MD-1i` `DD-1i` ·
`SBD-1` `SAD-1` `SMD-1` `SMRD-1` `SDD-1`)을 셌다.

| 토큰 | 교체 전 화면 렌더 | 교체 전 주석·소스 | 판정 |
|---|---|---|---|
| `만기` | **4건** (invest-sim 채권별 산출 표 `구분` 칸) | build_app.py 6 · daily_ledger.py 8 · platform_duration.py 10 · build_sim_static.py 1 | 화면 우선 처리 |
| `Ai` `Di` `Mi` `Bi` | **0건** | build_app.py JS 주석 3줄 · daily_ledger.py 22줄 · platform_duration.py 5줄 | 화면 렌더 없음 |
| `SLi` `SAi` `Api` `Dpi` `BD-1i` `AD-1i` `MD-1i` `DD-1i` `SBD-1` `SAD-1` `SMD-1` `SMRD-1` `SDD-1` | **0건** | daily_ledger.py · platform_duration.py 주석만 | 화면 렌더 없음 |

`app.html` 원문 검색으로 잡히던 `Di` 7건은 `pwHasDisallowed` 함수명 부분일치다. 기호가 아니다.

---

## 2. 파일별 교체 건수

### build_app.py — 10줄 (화면 1 · 주석 9)

| # | 자리 | 화면/주석 | 교체 |
|---|---|---|---|
| 1 | `b.kind = '만기'` (simRun) | **화면** | `'기간 내'` — 표 `구분` 칸 4행 |
| 2 | `투자 수익 (기간 안에 만기가 도래한 채권)` | 주석 | `정산예정일이 기간 안에 든 채권` |
| 3 | `플랫폼별 만기 = round(DURATION)` | 주석 | `플랫폼별 금융일수` |
| 4 | `그 행의 만기는 입력한 날짜대로` | 주석 | `그 행의 금융일수는` |
| 5 | `만기 4행(5~8)` | 주석 | `기간 내 4행(5~8)` |
| 6 | `이 화면의 만기는 채권 1건짜리 정수` | 주석 | `이 화면의 금융일수는` |
| 7 | `정수 만기 위에서 3.04` | 주석 | `정수 금융일수 위에서` |
| 8 | `옆 칸 금액(미회수 Σ Ai)` | 주석 | `Σ A<sub>i</sub>` |
| 9 | 산식 출처 줄 | 주석 | 아래 §3 |
| 10 | `채권 1건 — Ai · Di … 투자수익 Mi · 상환액 Bi` | 주석 | `A<sub>i</sub> · D<sub>i</sub> … M<sub>D−1,&thinsp;i</sub> · B<sub>D−1,&thinsp;i</sub>` |

`만기` 7건(화면 1 · 주석 6) · 아래첨자 3줄(기호 9개).

### build_sim_static.py — 1줄 (화면)

`b['kind'] = '만기'` → `'기간 내'`. 정적 낱장 `invest-sim--result.html` 의 같은 표 4행.
통합본과 낱장이 갈리면 `verify_sim.js` 의 `낱장 = 통합본` 대조가 깨진다.

### daily_ledger.py — 8건 (전건 주석·독스트링)

| 지금 | 바꾼 것 |
|---|---|
| `가맹점의 평균만기라 W 와 같은 만기를 쓴다` | `가맹점의 w금융일수라 W 와 같은 금융일수를 쓴다` |
| `만기 1~13일이 섞이면` | `금융일수 1~13일이 섞이면` |
| `묶음에서 만기 차이가 드러나지` | `금융일수 차이가` |
| `만기 최대치만큼 앞서 시작한다` | `금융일수 최대치만큼` |
| `틸트만큼 만기가 길거나 짧아진다` | `금융일수가 길거나` |
| `(가맹점, 플랫폼, 만기 버킷, 선정산일)` | `금융일수 버킷` |
| `플랫폼별 평균만기 실측 2.0~6.2일` | `플랫폼별 w금융일수 실측` |
| `정수 만기 버킷 2~7일` | `정수 금융일수 버킷` |

### platform_duration.py — 10건 (주석 8 · `__main__` 터미널 출력 2)

| 지금 | 바꾼 것 |
|---|---|
| `플랫폼별 평균만기(Duration)와 …` (모듈 독스트링 표제) | `플랫폼별 평균 금융일수(Duration)` |
| `금융 일반 용어로 \`Duration\`(가중평균만기)이다` | `금융 일반 용어로 \`Duration\` 이다` |
| `이 구성으로 낸 가중평균만기 = 3.039607…일` | `이 구성으로 낸 w금융일수 =` |
| `이 구성으로 낸 가중평균만기 2.750406…일` | `이 구성으로 낸 w금융일수` |
| `플랫폼 평균만기가 소수인 것은 건별 정수 만기가` | `평균 금융일수가 소수인 것은 건별 정수 금융일수가` |
| `평균만기는 손으로 적지 않고` | `평균 금융일수는` |
| `플랫폼 구성비 → 가중평균만기(Duration)` (duration 독스트링) | `→ w금융일수(Duration)` |
| `금액 실측 구성의 가중평균만기 — 데이터의 기준값` | `금액 실측 구성의 w금융일수` |
| `print(… 평균만기 %s일)` | `평균 금융일수 %s일` — 터미널 출력 |
| `print(금액 실측 구성의 가중평균만기 = %s일 …)` | `w금융일수 = %s일` — 터미널 출력 |

두 낱말을 갈라 쓴다. 플랫폼 한 곳의 값(`DURATION[k]`)은 도수 가중이라 **평균 금융일수**,
플랫폼 구성비로 합친 값(`MEASURED_W` · `duration()`)은 금액 가중이라 **w금융일수**다.
합친 값까지 「평균 금융일수」로 쓰면 `verify_weighting.js` 가 지키는 금액 가중 / 건수 가중의 갈림이 흐려진다.

### build_ops.py · build_sigtext.py · sync_assets_static.py — 0건

`만기` 0 · 기호 0. 손댈 자리가 없다.

---

## 3. 산식 출처 줄 — [1번] / [2번] 대조

교체 전 (`app.html:2296`)

```
산식 출처 — 대표 정의서 [1번 이미지] Ai·Di·W·Ty·S · [2번 이미지] Mi·Bi·PSA·PSM·PSD·PSMR·PSC.
```

교체 후

```
산식 출처 — 대표 정의서 [1번 이미지] A<sub>i</sub>·D<sub>i</sub>·w·ty·S · [2번 이미지] M<sub>D−1,&thinsp;i</sub>·B<sub>D−1,&thinsp;i</sub>·PSA·PSM·PSD·PSMR·PSC.
```

`ceo_definitions.md` 를 [1번 이미지] / [2번 이미지] 두 절로 갈라 토큰별 출현 수를 센 결과.

| 토큰 | [1번] | [2번] |
|---|---|---|
| `Ai` `Di` `SLi` `SAi` `S입금부족율` | 5 / 2 / 2 / 2 / 1 | 0 |
| `w금융일수` | 2 | 2 |
| `ty수익율` | 1 | 5 |
| `MD-1i` `BD-1i` | 0 | 3 / 2 |
| `PSA` `PSM` `PSD` `PSMR` `PSC` `Api` `Dpi` `EC` | 0 | 5 / 4 / 2 / 2 / 2 / 2 / 2 / 2 |
| `Mi` `Bi` | **0** | **0** |

- 기존 줄의 `PSA·PSM·PSD·PSMR·PSC` → [2번] 귀속이 맞다. 검산 결과 유지.
- `Mi` `Bi` → 원문 0건. `symbol_glossary.json` 28항목에도 없다. 원문 표기 `MD-1i` `BD-1i` 로 되돌렸다.
- `W` `Ty` → 대문자는 화면 라벨 표기다. 이 줄은 원문을 가리키는 자리라
  `symbol_glossary.json` `notation_canon` 「w · ty 대소문자」에 따라 소문자로 내렸다.
- `w금융일수`는 [1번]·[2번] 양쪽에 있으나 정의가 서는 자리는 [1번]이라 그대로 [1번]에 둔다.

---

## 4. 조어로 남긴 자리 · 조어가 아니었던 자리

| 낱말 | 판정 | 근거 |
|---|---|---|
| `기간 내` | **조어 아님** | `symbol_glossary.json` 이 `Api` 를 「**기간 내** 채권 1건분 투자실행금」으로 등록. 원문 [2번] 「정산예정일이 위 선택한 기간에 해당하는」과 같은 모집단이다 |
| `미회수` | 조어 아님 | 원문 [1번] 「회수되지 않은 순지급액」 |
| `기간 밖` | 손대지 않음 | 교체 전부터 있던 라벨. `기간 내`의 짝이다 |
| `만기 도래` | **조어 — 남아 있다** | 검산 엑셀 `채권` 시트 열머리. `build_audit_xlsx.py`(엑셀 조) 소관이라 손대지 않았다. §7 |
| `가중평균만기` | 조어 — 남아 있다 | `glossary.html` 3건. 「Duration」의 한국어 대역으로 용어 해설에만 서는 말이고, `verify_crossscreen.py:224` · `verify_sync_chain.js:57` · `verify_deployed.py:46` 세 검증기가 그 존재를 기준으로 잡고 있다. 글로서리 조 소관. §7 |

---

## 5. 아래첨자를 `.py` 에 넣지 않은 이유

`<sub>` 는 HTML 로 나가는 글자에만 넣었다. `daily_ledger.py` · `platform_duration.py` 의
`Ai` `Di` `SLi` `SAi` `MD-1i` `BD-1i` 27줄은 그대로 뒀다.

- `symbol_glossary.json` `notation_canon` 「아래첨자 표기」 —
  canonical 은 `원문은 SAD-1 · AD-1i 처럼 평문으로 붙여 쓴다`. `Ai` `Di` `SLi` `SAi` 는
  사전의 `symbol` 필드 그 자체이고, `MD-1i` `BD-1i` 는 별칭 `(원문 평문 표기)` 로 등록돼 있다.
- `.py` 소스는 렌더되지 않는다. `<sub>` 를 넣으면 아래첨자가 아니라 글자 `<sub>` 가 남는다.
- 새 표기(`M_{D−1,i}` 같은 것)를 만들면 사전에 없는 변종이 하나 더 생긴다.

`build_app.py` 의 세 줄은 `.py` 지만 그 문자열이 `app.html` 안 JS 주석으로 그대로 나가므로
HTML 쪽 규약을 적용했다.

---

## 6. 렌더 확인

헤드리스 크롬 1440×1200, `app.html` · 시연본 `index.html` 양쪽.

| 항목 | app.html | 시연본 index.html |
|---|---|---|
| 화면 렌더 `만기` | 0건 | 0건 |
| 화면 렌더 평문 기호 15종 | 0건 | 0건 |
| 시뮬레이션 `구분` 칸 | 미회수 ×4 · **기간 내 ×4** | 미회수 ×4 · **기간 내 ×4** |
| 채권별 산출 표 행 높이 | 15행 전건 45px (분포 1종) | 15행 전건 45px |
| 가로 오버플로 | 0px | 0px |
| DOM `<sub>` 요소 | 0개 | 0개 |
| 콘솔 에러 | 0건 | 0건 |

`<sub>` 가 DOM 에 0개라 줄 높이가 흔들릴 자리가 없다.
`sub{font-size:.72em;line-height:0}` 규칙은 넣지 않았다 — 이 화면에 쓰이지 않는 죽은 규칙이 된다.
`<sub>` 를 실제로 그리는 화면(글로서리)에서 그 조가 붙일 자리다.

정적 낱장 `invest-sim--result.html` 도 `<td>기간 내</td>` 4행 · `만기` 0건.

---

## 7. 검증기

### 기준을 함께 갱신한 것 2건

라벨을 문자열로 잡던 자리다. 갱신하지 않으면 대상 0건이 되어 「0건 아님」 검사가 FAIL 로 잡힌다.
기대값을 낮추지 않고 찾는 문자열만 새 라벨로 옮겼다.

| 검증기 | 자리 | 교체 |
|---|---|---|
| `verify_sim.js` | `B.bondKinds.filter(k => k === '만기')` 외 판정문 5개 | `=== '기간 내'` |
| `verify_batch_symbols.py:815` | `sim['bonds']['body'] if b[1] == '만기'` | `== '기간 내'` · 검사명도 `기간 내 채권 0건 아님` |

### 실행 결과

| 검증기 | 결과 |
|---|---|
| `verify_batch_symbols.py` | 검사 144 · **FAIL 0** (교체 전 FAIL 1 → 0) |
| `verify_weighting.js` | 판정 23 · FAIL 0 |
| `verify_crossscreen.py` | FAIL 0 (exit 0) |
| `verify_identity.js` | 항등식 17 · FAIL 0 · 콘솔 0 |
| `verify_sim.js` | 59 / 59 ALL PASS |
| `verify_app.js` | 판정 99 · FAIL 0 · 콘솔 0 · 죽은 컨트롤 0 |
| `verify_proto.js` | 판정 135 · FAIL 0 · 콘솔 0 · 죽은 컨트롤 0 |
| `verify_period.js` | 40 · FAIL 0 |
| `verify_rows.js` | 35 · FAIL 0 |
| `verify_toast.js` | 25 · FAIL 0 |
| `verify_password.js` | exit 0 |
| `verify_feasibility.js` | 판정 PASS |
| `verify_sync_chain.js` | 라운드 1 전건 통과 |
| `verify_glossary.js` · `verify_glossary5.js` | PASS |
| `gate_prototype.js` · `gate_glossary.js` | 게이트 통과 · 통로 0건 |
| `verify_0828.py` | 32 · FAIL 0 |
| `verify_0828_negative.py` | 복원 후 FAIL 없음 |
| `verify_shotmarks.py` | 50 · FAIL 0 |
| `verify_links.py` | 74 · FAIL 0 (`localhost:8901` 로 레포를 띄운 상태에서 실행) |
| `verify_cycle_xlsx.py` | PASS |
| `verify_deployed.py` | 배포 실측 8 · FAIL 0 |

`verify_batch_symbols.py` 항목 4 「[2번] 축 기호 표기가 전부 symbol_glossary.json 에 등록돼 있음」

- 교체 전 : `미등록 표기 {'Mi': ['app.html', '시연본 index.html', '검산 엑셀 채권 시트'], 'Bi': [같음]}`
- 교체 후 : `미등록 표기 {}`

엑셀 쪽은 같은 시간대에 엑셀 조가 열머리를 `투자수익 MD-1i` · `상환액 BD-1i` 로 바꿔 두었다.
화면 2곳은 이 작업이 맡았다. 세 곳이 다 채워져 FAIL 이 0 이 됐다.

### 이 작업과 무관하게 FAIL 인 것 3건

| 검증기 | 상태 | 성격 |
|---|---|---|
| `verify_settlement_cards.py` | FAIL 4 | 교체 전 저장된 `verify_settlement_cards_result.json` 도 `fail: 4`. 실제 프론트 정산 카드 산식 대조라 이 파일들과 닿지 않는다 |
| `rate_fix_verify.py` | 실행 불가 | `invest-assets--page2.html` 을 읽는데 그 낱장이 레포에 없다. 폐기된 화면을 가리키는 옛 검증기 |
| `verify_demo.js` | 파일 없음 | `verifiers.md` 목록에만 있고 실물이 없다 |

---

## 8. 레포 커밋

푸시하지 않았다. 두 레포 다 `origin/main` 대비 `ahead 1`.

| 레포 | 커밋 | 담은 파일 |
|---|---|---|
| `/Users/semi/cursor/payhug-investor-admin` | `f08c98a` | `app.html` · `invest-sim--result.html` |
| `/Users/semi/cursor/payhug-investor-prototype` | `c110ad9` | `index.html` |

같은 시각 작업 트리에 있던 `glossary.html` 변경은 글로서리 조 것이라 스테이징에서 뺐다.

---

## 9. 넘길 것

| 자리 | 파일 | 조 | 내용 |
|---|---|---|---|
| `capability.html` 2줄 | `capability_manuscript.md` | 원고 조 | `구간 안이면 만기(투자 수익)로 갈린다` · `행은 만기 채권의 서로 다른 정산예정일에만 선다` — 화면 라벨이 `기간 내` 로 바뀌어 원고가 화면과 어긋난다 |
| `capability.html` 2줄 | 같음 | 같음 | `투자 시뮬레이션 플랫폼별 만기` · `플랫폼별 평균 만기 실측` — `platform_duration.py` 는 `평균 금융일수` 로 맞췄다 |
| `archive.html` 4줄 | `build_archive.py` | 아카이브 조 | 파일 설명 `플랫폼 만기 실측값 적용기` · `플랫폼별 만기·미지급률·과지급률 실측 상수` 등 |
| 검산 엑셀 `채권` 시트 | `build_audit_xlsx.py` | 엑셀 조 | 열머리 `만기 도래` — 화면의 `기간 내` 와 같은 모집단인데 낱말이 갈린다 |
| `glossary.html` 3줄 | `glossary_manuscript.md` | 글로서리 조 | `가중평균만기`. 지우면 `verify_crossscreen.py:224` · `verify_sync_chain.js:57` · `verify_deployed.py:46` 세 검증기가 FAIL 이 된다. 낱말과 기준을 같이 옮겨야 한다 |
| `symbol_glossary.json` | 같음 | 같음 | `A(D-1)i` 의 한국어 이름이 「**전일자 만기 채권** 1건분 투자실행금」이다. 원문은 「정산예정일이 전일자(D-1)인」 |
| `sim_facts.py:52 · 160` | — | — | 주석 `플랫폼 만기` 2건. 산출값에 영향 없어 남겨 뒀다 |
| `verify_identity.js` 5줄 | — | — | Little's Law 설명 주석의 `잔액 = 유량 x 만기`. 금융 일반 용어를 빌려 쓰는 자리라 판단을 넘긴다 |
