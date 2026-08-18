# 시트 조립 계획 (sheet-applier용) — Figma 쓰기 직렬

## 공통
- 파일: Tcf69tIciGxmlqCIuRb0iI. 대상 페이지: **2807:2212** ([페이허그_어드민] 회원관리, 빈 캔버스).
- 템플릿: **2103:2** (Document, 1922×16004) — clone → 대상 페이지에 appendChild → 위치 지정.
- 배치: 순번 i(0~8) 기준 **x = i×2200, y = 0**. 순서 = AD_MEMBER, AD_MEMBER_ADD, AD_MEMBER_ADD_TOP, AD_MEMBER_EDIT, AD_MEMBER_PROFILE, AD_MEMBER_CHAIN, AD_MEMBER_EXCEPT, AD_MEMBER_GNB, AD_MERCHANT_FEE2.
- 시트 이름: `<page_id> — <page_title>` 로 rename.
- 원고: `manuscripts/<page_id>.md`. 화면 노드: `import_map.json` (m1~m9 ↔ 시트 1~9 순서 일치).

## 텍스트 슬롯 (템플릿 136슬롯 — clone 직후 findAll 텍스트 덤프로 실물 대조 후 기입)
- 1=Page(page_title) / 3=Page ID / 7=Date(26.08.19) / 11=Flow / 24=메모(Note)
- 키노트 8쌍: 이름=29+3k, 설명=30+3k (k=0..7)
- 54=키노트 요약
- 심화 상태 pill 13개: 63/68/73/82/85/92/101/106/115/120/125/130/135
  - pill 색: 확정=녹(0.039,0.561,0.357) / 확인필요=회(0.420,0.447,0.502) / 가설=앰버(0.706,0.325,0.035) / 신규=남(0.294,0.278,0.839), 텍스트 백색
- 심화 제목·설명·근거 슬롯은 pill 인접 인덱스 — 덤프에서 그룹 헤더([데이터 출처]/[계산·판단 로직]/[설정·연결]/[정책·주의])와 행 구조 확인 후 기입.
- Writer 슬롯이 있으면 `이서준`. 하단 풋터 메타바도 동일 기입(있는 경우).

## 화면부 삽입
- import_map의 목업 노드를 clone → 시트 화면 크롭 컨테이너에 삽입.
- **rescale = 1250/원폭** (1920 → 0.6510). 컨테이너 높이 FIXED 유지, hug 오확대 금지.
- 목업 세로가 길면 컨테이너 높이를 목업 스케일 후 높이에 맞춰 명시적으로 설정(고정값), 형제 밴드 y 재적층.

## 마커
- 템플릿 인덱스 15~22 = 숫자 마커 8개(숫자 텍스트의 부모 원형) → 키노트 1~8 대응 화면 위치로 이동, **최상위 재부착**(가림 금지).
- 화면에 없는 항목(정책성 키노트)의 마커는 우측 키노트 행 옆 여백에.

## 폰트·오버플로
- Apple SD 폴백 시: 스타일 복사→Noto Sans KR 신규→같은 인덱스 재구성.
- 폭 초과: textAutoResize=HEIGHT + 폭 고정 캡. 키노트 표 재적층 후 시트 높이 hug 갱신.

## 검수 기록
- 시트별 완료 시 `figma_apply.md`에 append: page_id · 시트 node_id · 화면 노드 · 마커 8 · 특이사항.
