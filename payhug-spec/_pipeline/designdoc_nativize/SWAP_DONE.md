# 화면설계서 래스터→네이티브 스왑 — 완료 기록

**완료: 2026-08-09.** 페이지 `303:173` "[페이허그_어드민] 화면설계"의 화면설계서 시트들에 박혀 있던 **캡처 이미지(래스터)를 수정 가능한 네이티브 피그마 요소로 전량 교체**. in-place(같은 프레임·위치·배열), 보라색 마커·영역선·키노트 전부 보존.

## 결과
- **스왑 성공 208/208, 실패 0.** (파일럿 1584·1591 + 배치 16개 206개)
- 소스 = "[페이허그_어드민] 추출" 페이지의 프론트 추출 네이티브 노드(`srcnode`). 매핑 = `sheet_to_source.json`(각 시트 `img` 노드 = 캡처 슬롯, `srcnode` = 원본 화면).
- **제외 1건**: `1836:2` MC_CONTRACT_TERMS_AGREE = 이미지 없음(손그림 네이티브) → 스왑 대상 아님, 약관 교정은 별도 완료.

## 프로그래밍 검증(통과)
- 원본 img 노드 208개 전부 제거됨(`origImgsStillExisting: 0`).
- 네이티브 "Screen (…)" 노드 정확히 208개 존재.
- 잔여 "Image (…)" 1213개 = 화면 **내부 로고 자산**(PayHug·배민·쿠팡이츠·요기요·카드사 등) — 실제 UI 서브이미지라 정상. 화면 단위 캡처 잔여 0.

## 스왑 레시피(재현용)
페이지 전환은 doc 페이지 1회. 각 잡:
1. `imgNode = getNodeByIdAsync(img)`, `src = getNodeByIdAsync(srcnode)` (cross-page 조회 OK, 추출 페이지로 전환 안 해도 됨).
2. 부모/인덱스/x·y/width 기록 → `clone = src.clone()`.
3. **폰트 리매핑**: 클론 내 모든 TEXT의 `getStyledTextSegments(['fontName'])` 순회, `loadFontAsync` 실패 폰트(예 Menlo 미설치)는 `setRangeFontName`으로 Noto Sans KR Regular 치환(이미 폴백 렌더라 시각 중립). rescale 전에 해야 rescale이 폰트 로드 요구로 실패 안 함.
4. `clone.rescale(targetW/clone.width)` (targetW=1250 균일).
5. `parent.insertChild(idx, clone)` → `layoutPositioning='ABSOLUTE'` → `clone.x/y` 복원 → 이름 "Image→Screen" → `imgNode.remove()`.

함정: 자동레이아웃 부모에선 clone이 페이지로 튕길 수 있음 → insertChild + ABSOLUTE로 강제. 스크립트는 per-job try/catch라 부분 실패해도 나머지 진행.

## 배치 파일
`swap_remaining.json`(206), `swap_batches.json`(16배치), `verify_imgids.json`(208 검증용).
