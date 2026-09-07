# 투자 자산 정적 낱장 4벌 「예상 연환산 수익률」 툴팁

## 하지 않은 것

| 항목 | 상태 | 근거 |
|---|---|---|
| `capture_shots.js` 재촬영 | 하지 않음 | `verify_shots.js` B2·B3·C1 `invest-assets.html` FAIL. 툴팁 앵커의 점선 밑줄(`base.css:494` `.tooltip .tip-anchor { border-bottom: 1px dotted }`)이 카드 라벨·열머리 2곳에 그려져 재현 캡처가 저장본과 **1.587%**(120,120 / 7,568,640 픽셀) 다릅니다. 「툴팁은 hover 라 정적 캡처 불변」 전제는 패널에만 맞고 앵커 밑줄에는 맞지 않습니다. 재촬영은 거울 저장소(`payhug-investor-glossary`)·`build_glossary.py` 까지 닿는 캡처 조 소관(`verifiers.md:176-179`)이라 손대지 않았습니다 |
| `prep_fig.py:66` 주석 「요약카드 툴팁 앵커는 통합본에만 있다」 | 미수정 | 이 문장은 이제 투자실행액 카드에만 맞습니다. 동작(`TIP['invest-assets--tip-yield'] = (None, …)` 동결본 사용)은 그대로 정상이라 범위 밖으로 두었습니다. 확인 필요 |
| 시뮬레이션 결과의 「예상 연환산 수익률」 카드·열머리 (`build_app.py` `simResultHtml` · `build_sim_static.py:225·249`) | 맨 라벨 그대로 | 지시 범위가 투자 자산 낱장 4벌·통합본 투자 자산 화면이라 손대지 않았습니다 |
| `verify_crossscreen.py` 에 Yr 툴팁 검사 항목 | 추가하지 않음 | 지시는 기존 POP 검사 실행. 재생성 시 보호는 `sync_assets_static.py` 의 `assert`(카드 1·열머리 2) 가 맡습니다 |
| 배포·push·Figma·증명서·원장·원고·CSS | 없음 | — |

## (가) 고친 자리

| 파일:줄 | 무엇 |
|---|---|
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/build_app.py:1305-1310` | `YR_TIP_HEAD`(`Y<sub>r</sub> · 예상 연환산 수익률 · r × 365 ÷ D`) · `YR_TIP_ROW`(`연환산` 행) 상수와 `yrTh()` — `popTh()` 와 같은 꼴의 `<th class="num">` 툴팁 |
| `build_app.py:1767` | 투자자산 요약 카드 툴팁의 머리글·`연환산` 행이 `YR_TIP_HEAD + YR_TIP_ROW` 를 씁니다. 카드와 열머리가 한 문자열을 공유합니다 |
| `build_app.py:1779-1780` | 현황표 열머리 `popTh('입금부족률', POP_S) + yrTh()` |
| `build_app.py:1808-1809` | 가맹점별 표 열머리 `IA_HEAD` 에 `yrTh()` |
| `/Users/semi/cursor/payhug/payhug-spec/_pipeline/investor_admin/sync_assets_static.py:41` | `roster16_model` 에서 `RPCT`(할인율 `0.11`) 를 읽습니다. 툴팁의 r 값은 낱장에 손으로 적지 않습니다 |
| `sync_assets_static.py:193-205` | `th_pat(label)` — 맨 라벨이든 툴팁이 붙은 것이든 `<th class="num">` 하나를 통째로 잡는 패턴. `pop_heads` 가 이것을 씁니다 |
| `sync_assets_static.py:208-250` | `# ── 2-2) 예상 연환산 수익률 툴팁` 절. `YR_LABEL`·`YR_HEAD`·`YR_ROW`·`YR_PLAIN`·`YR_CARD_TIP`, `yr_card_tip(w, ty_)`(카드 툴팁 전문 · `w is None` 이면 `집계 대상 없음`), `yr_card_strip`(툴팁을 맨 라벨로 되돌림), `yr_card`(**assert 1건**), `yr_th`, `yr_heads`(**assert 2건**) |
| `sync_assets_static.py:429-434` | `build_assets` — `summary_cards(yr_card_strip(s))` → `yr_card(s, W_ROW, TY_ROW)` → `pop_heads` → `yr_heads` → 현황표·로스터 표 |
| `sync_assets_static.py:461-464` | `build_assets_empty` — `yr_card(…, None, '0.00')` + `pop_heads` + `yr_heads`. 통합본 빈 상태(`wv === null` → `집계 대상 없음` · `fx(0, 2)` → `0.00`) 와 같은 분기 |
| `sync_assets_static.py:572` | `PLAN` 의 `invest-assets--empty.html` 이 `build_assets_empty` 를 씁니다 |

새 주석은 `sync_assets_static.py:208` 절 머리 한 줄(`# ── 2-2) 예상 연환산 수익률 툴팁`)뿐입니다. 파일의 `2-1)` 절 표기와 같은 꼴입니다.

### 재생성 산출물

| 파일 | 바뀐 줄 |
|---|---|
| `/Users/semi/cursor/payhug-investor-admin/app.html` | `YR_TIP_HEAD`·`YR_TIP_ROW`·`yrTh()` 정의(1870-1875) · 카드(2318) · 현황표(2330-2331) · 가맹점별 표(2359-2360). 그 밖의 diff 0 |
| `/Users/semi/cursor/payhug-investor-admin/invest-assets.html` | 133(카드) · 158(현황표 열머리) · 220(가맹점별 열머리) 3줄. 값·라벨 diff 0 |
| `/Users/semi/cursor/payhug-investor-admin/invest-assets--download.html` | 143 · 168 · 230 3줄. 값·라벨 diff 0 |
| `/Users/semi/cursor/payhug-investor-admin/invest-assets--cert-confirm.html` | 149 · 174 · 236 3줄. 값·라벨 diff 0 |
| `/Users/semi/cursor/payhug-investor-admin/invest-assets--empty.html` | 134 · 159 · 196 3줄. 값·라벨 diff 0 |

`git status`(payhug-investor-admin): 위 5개 파일만 `M`. 다른 파일 변경 없음.

## (나) 재생성·게이트·검사기 결과

| 단계 | 명령 | 결과 |
|---|---|---|
| 통합본 재생성 | `python3 build_app.py` | `app.html 245640 bytes / 3966 lines` |
| 낱장 재생성 | `python3 sync_assets_static.py` | 투자자산 낱장 4벌 `changed`, 나머지 7벌 `same` |
| 손편집 낱장 = 생성기 출력 | `python3 sync_assets_static.py --check` | **11 / 11 OK · 어긋난 낱장 0** (바이트 일치) |
| Figma 스테이징 | `python3 prep_fig.py sync` | 24화면 + freeze 대상 13 · 원본 HEAD e019d5a(워킹트리 변경분 포함) |
| 상태 프레임 동결 | `python3 prep_fig.py freeze` | 13개 생성. `invest-assets--tip-yield` 「예상 연환산 수익률」 패널 열림 정상 |
| 시연본 임시 변환 | `sync_prototype.py --dst …/scratchpad/proto_dry` | 통로 검사 통과 · 자산 역산 18건 · `index.html 214601 → 168053 bytes` |
| 시연본 게이트 | `DST_REPO=…/proto_dry node gate_prototype.js` | **게이트 통과** — 링크 208 · 엑셀 14종 바이트 일치 · 가로 오버플로 0 · 비중 합 100.0% · 콘솔 에러 0 · 9화면 · 상태 17 |
| 화면 간 정합 | `python3 verify_crossscreen.py` | 63건 · 불일치 3. **POP 검사 전건 PASS**(낱장 4벌 열머리 모집단 툴팁 · 미확정 배지 없음 · app.html 재료·popTh 2곳). 불일치 3건은 전부 용어 해설(`glossary.html`) 항목 — 「허용 블록 밖 대출 어휘(만기)」 「허용 블록 밖 duration」 「duration 허용 블록 = 1곳」. `glossary.html` 은 이번 변경과 무관하고 미수정(`git status` 에 없음) |
| 캡처 봉인 | `node verify_shots.js` | 64건 · **FAIL 5**. 아래 표 |

### verify_shots.js FAIL 5건

| 판정 | 대상 | 원인 | 이번 변경과의 관계 |
|---|---|---|---|
| B2 원본 HTML sha256 = 봉인 | `invest-assets.html` | 8bd0d059… vs 봉인 1736d106… | 이번 변경(낱장 3줄) |
| B3 이미지가 화면보다 나중 | `invest-assets.html` | 촬영 02:38 < 화면 수정 03:11 | 이번 변경 |
| C1 재현 바이트 = 저장본 | `invest-assets.html` | 어긋난 픽셀 120,120 / 7,568,640 (1.587%) | 이번 변경 — 앵커 점선 밑줄 3곳이 캡처에 실림 |
| B4 거울 이미지 = 원본 이미지 | `invest-assets.html` | efa99cfa… vs eb277ff9… | 무관 — 두 저장소의 webp 모두 미수정 |
| B4 거울 이미지 = 원본 이미지 | `invest-profit.html` | 82de1ce5… vs 732ae73c… | 무관 — 같은 이유 |

## (다) DOM 확인

헤드리스 Chrome(CDP, `scratchpad/dom_check.js`)으로 낱장 4벌을 열어 `.tip-anchor` 텍스트가 「예상 연환산 수익률」인 툴팁의 `.tip-panel` 을 읽었습니다.

| 낱장 | 툴팁 곳수 | 카드 패널 행 | 현황표 열머리(5열) 패널 행 | 가맹점별 열머리(5열) 패널 행 | 카드 값 | 기본 상태 패널 숨김 |
|---|---|---|---|---|---|---|
| `invest-assets.html` | 3 | `연환산` · `r \| 계약된 할인율 · 0.11%` · `D \| 가중평균 금융일수 · 3.04일` · `연 환산 \| 13.21%` · `일 환산 \| 미확정` · `대표 DM 16:27` · `대표 DM 16:45` | `연환산` 1행 | `연환산` 1행 | 13.21% | display:none |
| `invest-assets--download.html` | 3 | 위와 같음 | `연환산` 1행 | `연환산` 1행 | 13.21% | display:none |
| `invest-assets--cert-confirm.html` | 3 | 위와 같음 | `연환산` 1행 | `연환산` 1행 | 13.21% | display:none |
| `invest-assets--empty.html` | 3 | `연환산` · `r \| 계약된 할인율 · 0.11%` · `D \| 가중평균 금융일수 · 집계 대상 없음` · `연 환산 \| 0.00%` · `일 환산 \| 미확정` · `대표 DM 16:27` · `대표 DM 16:45` | `연환산` 1행 | `연환산` 1행 | 0.00% | display:none |

머리글은 4벌 12곳 모두 `Yr · 예상 연환산 수익률 · r × 365 ÷ D`.

### 통합본과 마크업 바이트 대조

| 대조 | 결과 |
|---|---|
| 카드 툴팁 마크업 — 낱장 3벌(기본·download·cert-confirm) vs 통합본 동결 DOM(`_fig/invest-assets--tip-yield.html`, `id="fig-tip"` 제외) | **일치** |
| 카드 툴팁 마크업 — `--empty` vs 통합본 `go('invest-assets','empty')` 동결 DOM(`freeze_app.js`) | **일치** |
| 열머리 툴팁 마크업 — 낱장 4벌 × 2곳 vs 통합본 동결 DOM 2곳 | **일치** (8곳 전부 같은 문자열) |

## 임시 파일 (scratchpad)

| 경로 | 용도 |
|---|---|
| `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/before/` | 수정 전 낱장 4벌·app.html 사본 (diff 근거) |
| `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/dom_check.js` | (다) DOM 추출 스크립트 |
| `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/proto_dry/` | 시연본 임시 변환 결과 (게이트 대상) |
| `/private/tmp/claude-501/-Users-semi-cursor-payhug/9aed3429-fc00-4785-9abd-c254e437cf03/scratchpad/app_empty.json` | 통합본 빈 상태 동결 DOM |
