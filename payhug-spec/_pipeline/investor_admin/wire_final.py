#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""잔여 배선 + 허위 주장 정리 — 정적 화면분.

app.html 은 build_app.py 가 생성하므로 여기서 손대지 않는다.
숫자(금액·비중·요율)는 건드리지 않는다. 건수 표기와 행 수를 맞추는 표시 구간 라벨만 붙인다.
"""

import io
import os

REPO = "/Users/semi/cursor/payhug-investor-admin"

LOGO_FILES = [
    "invest-assets.html", "invest-assets--page2.html", "invest-assets--download.html",
    "invest-assets--cert-confirm.html", "invest-assets--empty.html",
    "invest-profit.html", "invest-profit--monthly.html", "invest-profit--empty.html",
    "xls-assets-status.html", "xls-assets-merchant.html",
    "xls-profit-status.html", "xls-profit-daily.html",
    "certificate.html",
]
CONTRACT_FILES = ["contracts.html", "contracts--all.html", "contracts--downloaded.html",
                  "contracts--empty.html"]
MERCH_FILES = ["merchants.html", "merchants--filtered.html", "merchants--filter-open.html"]

FOOTNOTE_CSS = (
    "  .tbl-foot-note {\n"
    "    padding: 12px 20px; border-top: 1px solid var(--gray-100); background: var(--gray-50);\n"
    "    font-size: 12px; line-height: 18px; color: var(--gray-500);\n"
    "  }\n"
)
MC_NOTE = '<div class="tbl-foot-note">가맹점 상세 화면은 이번 설계(안) 범위 밖. 행 클릭 목적지 없음.</div>'

log = []


def rd(p):
    return io.open(os.path.join(REPO, p), encoding="utf-8").read()


def wr(p, s):
    io.open(os.path.join(REPO, p), "w", encoding="utf-8").write(s)


def sub(path, old, new, expect=1, tag=""):
    s = rd(path)
    n = s.count(old)
    if n == 0 and s.count(new) == expect:          # 이미 적용됨 — 재실행 허용
        log.append((path, expect, tag + " (기적용)"))
        return
    assert n == expect, "%s: %r %d건 (기대 %d)" % (path, old[:56], n, expect)
    wr(path, s.replace(old, new))
    log.append((path, expect, tag))


# ── 1. 로고 14건 ───────────────────────────────────────────────────
for f in LOGO_FILES:
    sub(f, '<div class="sidebar-logo">\n      <a href="#">',
           '<div class="sidebar-logo">\n      <a href="index.html">', 1, "로고 → index.html")

# ── 2. 증명서 PDF 다운로드 버튼 → 실물 링크 ────────────────────────
sub("certificate.html",
    '<button class="btn btn-primary" style="width:100%">',
    '<a class="btn btn-primary" style="width:100%" '
    'href="assets/docs/투자자산증명서_20260827.pdf" download="투자자산증명서_20260827.pdf">',
    1, "PDF 다운로드 배선")
sub("certificate.html", "            PDF 다운로드\n          </button>",
    "            PDF 다운로드\n          </a>", 1, "닫는 태그")

# ── 3. 증명서 서명값 — 검증 결과 단정 제거 ─────────────────────────
sub("certificate.html",
    '<span class="badge badge-green">서명 검증: 인증서 발행기관 검증 회신 완료</span>',
    '<span class="badge badge-gray">서명값 표시 — 검증 결과 미표기(확인 대상)</span>',
    1, "서명 검증 배지")
sub("certificate.html",
    '<p class="issue-note">전자문서에는 ㈜페이허그 인증서 서명값과 인증서 발행기관의 '
    '서명 검증 회신전문이 함께 포함됨.</p>',
    '<p class="issue-note">전자문서에 ㈜페이허그 인증서 서명값을 표시함. '
    '인증서 발행기관 검증 회신전문은 형식·전달 경로 미정의 — 확인 대상.</p>',
    1, "발급 안내문")

# ── 4. 증명서 발급 모달 안내문 ─────────────────────────────────────
sub("invest-assets--cert-confirm.html",
    '발급 문서에는 ㈜페이허그 인증서 서명값과 인증서 발행기관의 검증 회신전문이 포함됨.',
    '발급 문서에 ㈜페이허그 인증서 서명값을 표시함. 인증서 발행기관 검증 회신전문은 확인 대상.',
    1, "발급 모달 안내문")

# ── 5. 계약기록 표 하단 안내 — 회신전문 단정 제거 ──────────────────
for f in CONTRACT_FILES:
    sub(f,
        '<div class="tbl-foot-note">다운로드 시 선택한 각 가맹점의 재양도합의서 파일과 '
        '서명 검증 회신전문이 함께 제공됨.</div>',
        '<div class="tbl-foot-note">다운로드 시 선택한 각 가맹점의 재양도합의서 파일이 제공됨. '
        '서명 검증 회신전문은 형식·전달 경로 미정의 — 확인 대상.</div>',
        1, "표 하단 안내문")

# ── 6. 다운로드 완료 토스트 — 실제로 내려가는 파일에 맞춘다 ────────
sub("contracts--downloaded.html",
    '<p class="t-main">재양도합의서 8건 내려받기 완료</p>\n'
    '    <p class="t-sub">각 문서에 서명 검증 회신전문 포함.</p>',
    '<p class="t-main">재양도합의서_전체16건_20260827.zip 내려받기 완료</p>\n'
    '    <p class="t-sub">재양도합의서 16건 묶음. 서명 검증 회신전문 미포함 — 형식·전달 경로 확인 대상.</p>',
    1, "다운로드 토스트")

# ── 7. 가맹점 행 — 클릭 가능 표시 제거 + 사유 안내 ─────────────────
for f in MERCH_FILES:
    s = rd(f)
    n = s.count('<tr class="clickable">')
    if n == 0 and MC_NOTE in s:
        log.append((f, 0, "clickable 제거 + 상세 부재 안내 (기적용)"))
        continue
    assert n > 0, f
    s = s.replace('<tr class="clickable">', '<tr>')
    anchor = '      </div>\n      <div class="pagination"'
    assert s.count(anchor) == 1, "%s: pagination 앵커 %d건" % (f, s.count(anchor))
    s = s.replace(anchor, '      </div>\n      ' + MC_NOTE + '\n      <div class="pagination"')
    if ".tbl-foot-note" not in s:
        if "</style>" in s:
            assert s.count("</style>") == 1
            s = s.replace("</style>", FOOTNOTE_CSS + "</style>")
        else:
            assert s.count("</head>") == 1
            s = s.replace("</head>", "<style>\n" + FOOTNOTE_CSS + "</style>\n</head>")
    wr(f, s)
    log.append((f, n, "clickable 제거 + 상세 부재 안내"))

# ── 8. 총 건수 ↔ 화면에 그려진 행 수 — 표시 구간 병기 ──────────────
RANGE = ' · 표시 <b class="mono">1–8</b>'
sub("contracts.html",
    '총 <b class="mono">16</b>건 · 선택 <b class="mono">3</b>건',
    '총 <b class="mono">16</b>건' + RANGE + ' · 선택 <b class="mono">3</b>건', 1, "표시 구간")
for f in ["contracts--all.html", "contracts--downloaded.html"]:
    sub(f, '<span class="tbl-count">총 <b class="mono">16</b>건</span>',
           '<span class="tbl-count">총 <b class="mono">16</b>건' + RANGE + '</span>', 1, "표시 구간")
for f in ["merchants.html", "merchants--filter-open.html"]:
    sub(f, '총 <b class="mono">16</b>건</span>',
           '총 <b class="mono">16</b>건' + RANGE + '</span>', 1, "표시 구간")

# ── 9. 업종 옵션 — 원장에 실재하는 값만 남긴다 ─────────────────────
#    운영 어드민에 업종 필터가 없어(admin app/manage/page.tsx:223-255 ·
#    services/merchantService.ts:199-205) 가져올 코드 목록이 없다.
#    원장 16건의 업종은 `음식점업` 하나뿐이라 나머지 3개는 근거가 없다.
GHOST = "<option>도소매업</option><option>서비스업</option><option>기타</option>"
for f in ["merchants.html", "merchants--filtered.html", "merchants--empty.html"]:
    sub(f, GHOST, "", 1, "업종 옵션 정리 (5 → 2)")

DD_OLD = """            <div class="dd-trigger">
              <span>전체</span>
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
            </div>
            <div class="dd-menu">
              <div class="dd-opt">전체</div>
              <div class="dd-opt hover">음식점업 <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg></div>
              <div class="dd-opt">도소매업</div>
              <div class="dd-opt">서비스업</div>
              <div class="dd-opt">기타</div>
            </div>"""
DD_NEW = """            <div class="dd-trigger" role="combobox" tabindex="0" aria-haspopup="listbox" aria-expanded="true" aria-controls="mc-dd-list" aria-label="업종">
              <span>전체</span>
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
            </div>
            <div class="dd-menu" id="mc-dd-list" role="listbox" aria-label="업종">
              <div class="dd-opt" role="option" aria-selected="false" tabindex="-1">전체</div>
              <div class="dd-opt hover" role="option" aria-selected="true" tabindex="0">음식점업 <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg></div>
            </div>"""
sub("merchants--filter-open.html", DD_OLD, DD_NEW, 1, "업종 드롭다운 — 옵션 정리 + 보조기술 노출")

# ── 10. 정렬 머리글 — 키보드 도달 ──────────────────────────────────
#    정적 프레임에는 data-act 가 없어 정렬이 동작하지 않는다. 통합본과 표기를 맞춘다.

# ── 결과 ───────────────────────────────────────────────────────────
total = sum(n for _, n, _ in log)
for p, n, what in log:
    print("%3d건  %-34s %s" % (n, p, what))
print("\n적용 합계 %d건" % total)

rest = 0
for f in sorted(os.listdir(REPO)):
    if f.endswith(".html"):
        c = rd(f).count('href="#"')
        if c:
            print('잔여 href="#"  %2d건  %s' % (c, f))
            rest += c
print("잔여 합계 %d건" % rest)

