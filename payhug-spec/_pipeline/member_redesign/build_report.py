#!/usr/bin/env python3
# 회원관리 계약 체인 설계 리포트 빌더 — mockshots/sheetshots base64 임베드
import base64, os, sys
SP='/private/tmp/claude-501/-Users-semi-cursor-payhug/1ac085d1-d765-4e8c-98f1-012bcafd2c37/scratchpad'
OUT=os.path.join(SP,'member_chain_report.html')
def b64(p):
    return 'data:image/png;base64,'+base64.b64encode(open(p,'rb').read()).decode()
M=lambda n: b64(f'{SP}/mockshots/{n}.png')
S=lambda n: b64(f'{SP}/sheetshots/{n}.png')
SHEETS=[
 dict(pid='AD_MEMBER',t='회원 관리 목록',node='2839:2',mock='m1_list',shot='s1_AD_MEMBER',
  d="기존 11컬럼을 유지하면서 '상위 회원'을 '직속 상위'로 바꾸고, '직속 계약 수수료율'(대표값=채권매입, 예시)과 '계약 구조 보기 ›' 컬럼을 더한 목록. 사이드바는 정산 상품관리가 없는 TO-BE 메뉴."),
 dict(pid='AD_MEMBER_ADD',t='회원 등록 (계약 관계)',node='2847:2',mock='m2_add_sales',shot='s2_AD_MEMBER_ADD',
  d="유형을 고르면 직속 상위 유형이 자동 결정되고, 해당 유형만 검색되는 상위 선택 → 관계 요율 세트(채권매입·시스템이용료·이체수수료 + VAT + 납부·수취) 입력 → 연결선에 요율이 붙는 계약 구조 미리보기까지 한 모달에서 완결."),
 dict(pid='AD_MEMBER_ADD_TOP',t='회원 등록 (최상위·파트너 위치)',node='2849:2',mock='m3_add_top',shot='s3_AD_MEMBER_ADD_TOP',
  d="파트너 유형에 '계약 위치' 라디오가 붙는 두 상태 — 상위파트너를 고르면 계약 관계 섹션이 잠기고 최상위로 등록, 하위파트너를 고르면 상위파트너 검색과 요율 입력이 열린다. 페이허그와의 계약율 필요 여부는 확인 필요."),
 dict(pid='AD_MEMBER_EDIT',t='회원 수정 (관계 변경)',node='2853:2',mock='m4_edit',shot='s4_AD_MEMBER_EDIT',
  d="직속 상위·요율 세트 변경 영역과 \"변경 시 기존 관계는 종료 처리되고 새 이력이 생성됩니다\" 안내. 이력 정책(종료 처리 vs 덮어쓰기)은 확인 필요로 명기 — 현행 코드는 이력 없는 덮어쓰기."),
 dict(pid='AD_MEMBER_PROFILE',t='회원 프로필 (직속 계약)',node='2860:2',mock='m5_profile',shot='s5_AD_MEMBER_PROFILE',
  d="회원 정보 아래 [직속 계약 관계] 블록 — 직속 상위·상위 유형·적용일과 요율 세트 표(VAT·납부·수취 포함), [전체 구조 보기 ›] 진입."),
 dict(pid='AD_MEMBER_CHAIN',t='계약 구조 조회',node='2862:2',mock='m6_chain',shot='s6_AD_MEMBER_CHAIN',
  d="페이허그부터 영업까지 세로 체인 — 요율은 노드가 아니라 연결선 칩에 표시(Edge 원칙). 하단 관계 테이블에 상위/하위/관계/요율 세트/적용일. 페이허그↔상위파트너 구간 요율은 확인 필요 칩."),
 dict(pid='AD_MEMBER_EXCEPT',t='등록 예외 상태',node='2866:2',mock='m7_except',shot='s7_AD_MEMBER_EXCEPT',
  d="4패널 — ① 비활성 회원은 검색에서 선택 불가 ② 순환 구조 등록 차단 에러 ③ 중간 단계 생략(skip-level) 확인 다이얼로그 ④ 기존 직속 상위 계약 존재 안내. ③④의 허용 정책은 확인 필요."),
 dict(pid='AD_MEMBER_GNB',t='메뉴 구성',node='2873:2',mock='m8_gnb',shot='s8_AD_MEMBER_GNB',
  d="정산 상품관리가 없는 TO-BE 사이드바 — 정산 그룹은 정산 현황·정산 시뮬레이션 2메뉴. 우측에 총판(참여자) 시점 메뉴를 나란히 배치. 시뮬레이션 요율 원천의 전환은 확인 필요."),
 dict(pid='AD_MERCHANT_FEE2',t='가맹점 상세 수수료 연결',node='2875:2',mock='m9_merchant_fee',shot='s9_AD_MERCHANT_FEE2',
  d="정산상품 배정 대신 '적용 계약 체인' 카드 — 담당 영업의 체인과 요율을 가로로 표시. 거래 유형별(카드/배달) 차등과 정산 실행 활성화 게이트의 대체 기준은 확인 필요."),
]
CONFIRM=[
 "파트너 상·하위 판별 — 회원 데이터에 구분 없음, '계약 위치' 선택 단계 신설 여부 (P5)",
 "투자자·페이허그 채권매입 배분의 자리 — 체인 연결선에 없음 (P2)",
 "거래 유형(카드/배달)별 요율 차등의 관계 모델 표현 (P3)",
 "다우 트랙의 체인 표현 — 상위영업/하위영업 관계·수수료의 행선지 (P4)",
 "정산 계산 요율 원천 전환·기존 상품 데이터 이행 (P6)",
 "최상위(상위파트너) 등록 시 페이허그와의 계약율 필요 여부",
 "관계 변경 이력 정책 — 종료 처리+새 이력 생성 채택 여부 (현행은 덮어쓰기)",
 "순환·중간 단계 생략·다중 상위의 서버 검증 규칙",
 "정산 실행 활성화 게이트의 대체 기준 (현행은 상품 배정 존재가 전제)",
 "추천코드→체인 시작점 규칙의 명문화",
 "비활성 상위의 기존 하위 관계·정산 지속 여부",
 "선정산 응답의 상품 요율 필드 거취 — 관계 전환 시 재정의 또는 폐기",
]
gal=''
for i,s in enumerate(SHEETS,1):
    gal+=f'''<article class="sheet">
  <header class="sheet-h"><span class="sheet-no">{i}</span><code class="sheet-pid">{s['pid']}</code><h3>{s['t']}</h3><code class="sheet-node">{s['node']}</code></header>
  <p class="sheet-d">{s['d']}</p>
  <div class="imgs"><figure><img src="{M(s['mock'])}" alt="{s['t']} 목업" loading="lazy"><figcaption>화면 목업 (브라우저 뷰)</figcaption></figure>
  <figure class="fig-sheet"><img src="{S(s['shot'])}" alt="{s['t']} 시트" loading="lazy"><figcaption>Figma 화면설계 시트</figcaption></figure></div>
</article>'''
conf=''.join(f'<li>{c}</li>' for c in CONFIRM)
html=f'''<title>회원관리 계약 체인 설계</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{{--bg:#f7f9f6;--surface:#ffffff;--ink:#1a222c;--sub:#5a6672;--line:#e2e8e1;--navy:#1b2537;--navy-ink:#eef3ee;--acc:#4da119;--acc-ink:#2f6b0d;--chip:#eaf6de;--warn:#b45309;--warn-bg:#fdf3e4;--pass:#0a8f5b;--pass-bg:#e6f6ef;--hold:#6b7280;--hold-bg:#eef0f2;--mono:"IBM Plex Mono",Consolas,monospace}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#0f151d;--surface:#161f2b;--ink:#e7ecef;--sub:#9aa7b1;--line:#26313d;--navy:#121a26;--navy-ink:#e7ecef;--acc:#8fe24c;--acc-ink:#a5e972;--chip:#1e3016;--warn:#e2a04a;--warn-bg:#31261442;--pass:#43c98d;--pass-bg:#12301f;--hold:#96a0aa;--hold-bg:#222b34}}}}
:root[data-theme="dark"]{{--bg:#0f151d;--surface:#161f2b;--ink:#e7ecef;--sub:#9aa7b1;--line:#26313d;--navy:#121a26;--navy-ink:#e7ecef;--acc:#8fe24c;--acc-ink:#a5e972;--chip:#1e3016;--warn:#e2a04a;--warn-bg:#31261442;--pass:#43c98d;--pass-bg:#12301f;--hold:#96a0aa;--hold-bg:#222b34}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font-family:"IBM Plex Sans KR","Apple SD Gothic Neo","Noto Sans KR",sans-serif;line-height:1.7;font-size:15px}}
.wrap{{max-width:1100px;margin:0 auto;padding:0 28px 96px}}
.hero{{background:var(--navy);color:var(--navy-ink);border-radius:0 0 22px 22px;padding:44px 40px 38px;margin:0 -28px 36px}}
.hero .kicker{{font-size:12px;font-weight:700;letter-spacing:.14em;color:var(--acc);text-transform:uppercase}}
.hero h1{{margin:10px 0 10px;font-size:32px;line-height:1.3;text-wrap:balance;letter-spacing:-.01em}}
.hero p{{margin:0;max-width:760px;color:#c3ccd6;font-size:15px}}
:root[data-theme="dark"] .hero p{{color:var(--sub)}}
.stats{{display:flex;flex-wrap:wrap;gap:10px;margin-top:24px}}
.stat{{background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.12);border-radius:12px;padding:10px 16px;min-width:118px}}
.stat b{{display:block;font-size:22px;font-family:var(--mono);color:var(--acc)}}
.stat span{{font-size:12px;color:#aeb9c4}}
h2{{font-size:21px;margin:56px 0 6px;letter-spacing:-.01em}}
h2 .no{{color:var(--acc);font-family:var(--mono);font-size:15px;margin-right:8px}}
.sect-sub{{color:var(--sub);margin:0 0 20px;font-size:14px}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px}}
.card{{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:18px 20px}}
.card h4{{margin:0 0 6px;font-size:15px}}
.card p{{margin:0;color:var(--sub);font-size:13.5px}}
.tag{{display:inline-block;font-size:11px;font-weight:700;padding:2px 9px;border-radius:999px;margin-bottom:8px}}
.tag.acc{{background:var(--chip);color:var(--acc-ink)}}
.tag.hold{{background:var(--hold-bg);color:var(--hold)}}
.sheet{{background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:24px 26px;margin:18px 0}}
.sheet-h{{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap}}
.sheet-no{{display:inline-grid;place-items:center;width:26px;height:26px;border-radius:8px;background:var(--acc);color:#fff;font-weight:700;font-size:13px;align-self:center}}
:root[data-theme="dark"] .sheet-no{{color:#10240a}}
.sheet-pid{{font-family:var(--mono);font-size:13px;color:var(--acc-ink);background:var(--chip);padding:2px 8px;border-radius:6px}}
.sheet-h h3{{margin:0;font-size:17px}}
.sheet-node{{font-family:var(--mono);font-size:12px;color:var(--sub);margin-left:auto}}
.sheet-d{{color:var(--sub);font-size:13.5px;margin:8px 0 16px;max-width:900px}}
.imgs{{display:grid;grid-template-columns:1.45fr 1fr;gap:14px}}
.imgs figure{{margin:0}}
.imgs img{{width:100%;max-width:100%;height:auto;border:1px solid var(--line);border-radius:10px;display:block;background:#fff}}
.imgs figcaption{{font-size:12px;color:var(--sub);margin-top:6px;letter-spacing:.02em}}
@media (max-width:760px){{.imgs{{grid-template-columns:1fr}}}}
table{{width:100%;border-collapse:collapse;font-size:13.5px;background:var(--surface);border:1px solid var(--line);border-radius:12px;overflow:hidden}}
.tbl-wrap{{overflow-x:auto;border-radius:12px}}
th,td{{border-bottom:1px solid var(--line);padding:9px 13px;text-align:left;vertical-align:top}}
th{{background:var(--hold-bg);color:var(--sub);font-size:12px;letter-spacing:.04em}}
tr:last-child td{{border-bottom:0}}
td.num,th.num{{font-family:var(--mono);font-variant-numeric:tabular-nums}}
.pill{{display:inline-block;font-size:11px;font-weight:700;padding:1px 8px;border-radius:999px}}
.pill.pass{{background:var(--pass-bg);color:var(--pass)}}
.pill.fix{{background:var(--warn-bg);color:var(--warn)}}
ol.conf{{margin:0;padding-left:22px;display:grid;gap:6px;font-size:13.5px;color:var(--sub)}}
ol.conf li::marker{{color:var(--acc);font-weight:700}}
.note{{border-left:3px solid var(--acc);background:var(--surface);border-radius:0 10px 10px 0;padding:12px 16px;font-size:13.5px;color:var(--sub);margin:14px 0}}
code{{font-family:var(--mono);font-size:.92em}}
a{{color:var(--acc-ink)}}
.next{{display:grid;gap:8px;font-size:14px}}
.next div{{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:10px 16px}}
</style>
<div class="wrap">
<header class="hero">
  <div class="kicker">PayHug Admin · 화면설계 라운드 · 2026.08.19</div>
  <h1>회원관리 계약 체인 설계</h1>
  <p>정산상품이라는 중간 개념 없이, 회원 간 직속 상위 관계(Edge)에 계약 수수료율 세트를 싣는 회원관리 TO-BE. 개편안 v2를 실제 어드민 코드와 대조해 목업 9종을 만들고, Figma 화면설계 시트 9장으로 조판했다.</p>
  <div class="stats">
    <div class="stat"><b>9</b><span>Figma 시트</span></div>
    <div class="stat"><b>9</b><span>화면 목업</span></div>
    <div class="stat"><b>117</b><span>심화 행 (확인필요 47)</span></div>
    <div class="stat"><b>12</b><span>정책 확인 필요</span></div>
    <div class="stat"><b>9/9</b><span>QA PASS (보수 3 반영)</span></div>
  </div>
</header>

<h2><span class="no">1</span>채택 구조</h2>
<p class="sect-sub">개편안 v2 + 확정된 설계 결정 2건.</p>
<div class="cards">
  <div class="card"><span class="tag acc">원칙</span><h4>직속 상위 하나만 선택</h4><p>유형을 고르면 직속 상위 유형이 자동 결정되고(영업→영업조직→하위파트너→상위파트너→최상위), 사용자는 그 유형의 회원 1명만 검색해 고른다. 전체 체인은 상위 참조를 따라 시스템이 조합.</p></div>
  <div class="card"><span class="tag acc">결정 ①</span><h4>요율은 관계(Edge)에, 세트 전체로</h4><p>채권매입·시스템이용료·이체수수료 + VAT 방식 + 납부(대납)·수취 주체까지 현행 정산상품의 요율 구조를 관계 1건에 그대로 싣는다. 모든 숫자는 예시 표기(수수료율 실값 미확정).</p></div>
  <div class="card"><span class="tag acc">결정 ②</span><h4>제거 영향까지 9장</h4><p>회원관리 코어 6장에 더해 메뉴 구성·가맹점 상세 수수료 연결·등록 예외 상태까지 — 정산 상품관리가 사라진 뒤의 자리를 화면으로 답한다.</p></div>
</div>

<h2><span class="no">2</span>화면 갤러리 — 목업 ↔ Figma 시트</h2>
<p class="sect-sub">좌측 = 실제 어드민 디자인 언어로 만든 화면 목업(자체완결 HTML, 브라우저에서 열람 가능). 우측 = 페이지 <code>2807:2212</code>에 조판된 화면설계 시트(메타바 + 마커 + 키노트 8쌍 + 심화 13행).</p>
{gal}

<h2><span class="no">3</span>코드 분석 — 무엇을 재사용하고 무엇이 새로 필요한가</h2>
<p class="sect-sub">payhug-admin-web(main 5f9297e) 읽기 전용 분석. 전문 = <code>_pipeline/member_redesign/code_analysis.md</code></p>
<div class="cards">
  <div class="card"><span class="tag acc">재사용</span><h4>회원관리 뼈대 전부</h4><p>목록·등록/수정 모달·프로필·직속 상위 필드(parentUserId)·유형별 조회 API가 이미 있다 — TO-BE는 이 골격 위에 계약 관계 섹션을 얹는 구조.</p></div>
  <div class="card"><span class="tag hold">신규</span><h4>유형 규칙 · 관계 모델</h4><p>상위 후보 필터는 "활성+자기 제외"뿐이라 유형→상위 규칙은 신규. 관계에 요율을 담을 모델·API는 프론트 기준 전무 — 회원계약관계 신설이 전제.</p></div>
  <div class="card"><span class="tag hold">전제</span><h4>정산 계산의 요율 원천 전환</h4><p>정산상품 참조 지점 = 화면 4곳 + API 3계열. 화면만 바꿔도 되는 5건 / 서버 전환이 전제인 8건 / 데이터 이행 4건으로 분류됨.</p></div>
</div>
<h2 style="font-size:17px;margin-top:34px"><span class="no">3.1</span>정책 확인 필요 12건</h2>
<p class="sect-sub">화면에는 전부 '확인 필요'로 명기됨 — 개발 착수 전 결정 대상.</p>
<ol class="conf">{conf}</ol>

<h2><span class="no">4</span>QA 판정</h2>
<p class="sect-sub">읽기 전용 검수(doc-qa) — 원고 대 실물 전수 대조 + 좌표 기계 검증 + 육안 23장. 전문 = <code>qa.md</code></p>
<div class="tbl-wrap"><table>
<thead><tr><th>항목</th><th>결과</th><th>비고</th></tr></thead>
<tbody>
<tr><td>원고 대 실물 텍스트 일치 (전수)</td><td><span class="pill pass">PASS</span></td><td>9시트 × 메타·키노트 8쌍·심화 13행 문자 단위 일치</td></tr>
<tr><td>변경이력체 0 · 순한글 · DSL 누출 0</td><td><span class="pill pass">PASS</span></td><td>위반 0 — 인용 UI 문구·근거줄 영문만 예외</td></tr>
<tr><td>심화 pill 규격 (상태 4종 × 색)</td><td><span class="pill pass">PASS</span></td><td>117개 전수, 원고와 상태 수 일치</td></tr>
<tr><td>마커 8개 노출·가림 없음</td><td><span class="pill pass">PASS</span></td><td>72개 전수 — 화면 밖 정책 항목은 키노트 여백 배치</td></tr>
<tr><td>수수료율 예시 병기 (값 단정 0)</td><td><span class="pill pass">PASS</span></td><td>요율 표기 전건 '(예시)' — 실값 미확정 유지</td></tr>
<tr><td>레이아웃 (크롭·겹침·오확대)</td><td><span class="pill fix">보수 완료</span></td><td>키노트 제목 랩 미적용 3건(단일 유형) → 랩·재적층으로 해소, 재검 통과</td></tr>
</tbody>
</table></div>
<div class="note">보수 내역: 제목 랩 3건 + 계약 구조 시트의 심화 서술 1건(페이허그 노드 표시와 정합) + 미리보기 칩 2건 '(예시)' 병기 강화.</div>

<h2><span class="no">5</span>산출물 위치 · 다음 단계</h2>
<div class="cards" style="margin-bottom:20px">
  <div class="card"><h4>Figma</h4><p>서준 작업 공간 → 페이지 <b>[페이허그_어드민] 회원관리</b> (<code>2807:2212</code>) — 시트 9장, x 피치 2200. 원본 목업 노드는 <code>2829:2~2837:2</code>.</p></div>
  <div class="card"><h4>레포</h4><p><code>payhug-spec/_pipeline/member_redesign/</code> — 명세(spec.md)·원고 9건·목업 9건·코드 분석·조립/QA 로그·시트 맵.</p></div>
  <div class="card"><h4>목업 열람</h4><p><code>member_redesign/mockups/m1~m9.html</code> — 자체완결이라 브라우저로 바로 열림. 프론트 반영 시 이 목업이 마크업 기준.</p></div>
</div>
<div class="next">
  <div><b>①</b> 정책 확인 12건 중 P2(투자자·페이허그 배분)·P5(파트너 위치)·이력 정책부터 결정 — 화면 구조가 걸린 순서.</div>
  <div><b>②</b> 결정되면 서버 API 스펙(관계 CRUD·체인 조회·요율 검증) 초안 작성 → 프론트 목킹 구현.</div>
  <div><b>③</b> 미확정 항목의 07_OPEN_QUESTIONS 등재 여부 검토.</div>
</div>
</div>'''
open(OUT,'w',encoding='utf-8').write(html)
print(OUT, round(os.path.getsize(OUT)/1048576,2),'MB')
