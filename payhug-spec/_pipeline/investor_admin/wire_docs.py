#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""화면의 href="#" 를 실물 경로로 배선한다.

대상 — 수정 가능 범위만. invest-*·xls-*·app.html·certificate.html 은 손대지 않는다.
  계약서 PDF   24건  contracts.html / --all / --downloaded
  계약서 보기  10건  acquisition.html / --confirm / --signing / --done
  로고         18건  수정 가능 파일의 사이드바 로고 → index.html
  비밀번호찾기  1건  login.html → 비활성 + 사유 툴팁
"""

import os
import re

REPO = "/Users/semi/cursor/payhug-investor-admin"

CONTRACT_FILES = ["contracts.html", "contracts--all.html"]
ACQ_FILES = ["acquisition.html", "acquisition--confirm.html",
             "acquisition--signing.html", "acquisition--done.html"]
LOGO_FILES = ACQ_FILES + CONTRACT_FILES + [
    "contracts--empty.html", "coocon.html", "coocon--confirm.html",
    "merchants.html", "merchants--empty.html", "merchants--filtered.html",
    "merchants--filter-open.html",
    "password.html", "password--done.html", "password--error.html", "password--weak.html",
]

# 정산채권 양수 화면의 서명 대기 3건 — 목록 순서대로
PENDING_ORDER = ["M2026-0001", "M2026-0002", "M2026-0004"]

LOGO_OLD = '<div class="sidebar-logo">\n      <a href="#">'
LOGO_NEW = '<div class="sidebar-logo">\n      <a href="index.html">'

PW_OLD = '<div class="login-links"><a href="#">비밀번호 찾기</a></div>'
PW_NEW = (
    '<div class="login-links">'
    '<span class="link-off" role="link" aria-disabled="true" '
    'title="비밀번호 찾기 화면은 이번 설계(안) 범위 밖(D-2). 발급·재설정은 페이허그 담당자 문의.">'
    '비밀번호 찾기</span></div>'
)
PW_CSS_ANCHOR = (
    "  .login-links a:hover { color: var(--gray-700); text-decoration: underline; }"
)
PW_CSS_ADD = (
    "\n  .login-links .link-off { font-size: 12px; line-height: 16px; color: var(--gray-300);"
    " text-decoration: none; cursor: not-allowed; }"
)


def read(p):
    with open(os.path.join(REPO, p), encoding="utf-8") as f:
        return f.read()


def write(p, s):
    with open(os.path.join(REPO, p), "w", encoding="utf-8") as f:
        f.write(s)


log = []


def patch(path, old, new, expect):
    s = read(path)
    n = s.count(old)
    assert n == expect, f"{path}: '{old[:40]}...' {n}건 (기대 {expect})"
    write(path, s.replace(old, new))
    log.append((path, expect, new[:60]))


# ── 1. 계약서 PDF 24건 ─────────────────────────────────────────────
for f in CONTRACT_FILES:
    s = read(f)
    cnt = 0
    for i in range(1, 9):
        mid = f"M2026-{i:04d}"
        old = f'<a class="file-link" href="#">재양도합의서_{mid}.pdf</a>'
        new = (f'<a class="file-link" href="assets/docs/재양도합의서_{mid}.pdf" '
               f'target="_blank" rel="noopener">재양도합의서_{mid}.pdf</a>')
        assert s.count(old) == 1, f"{f}: {mid} {s.count(old)}건"
        s = s.replace(old, new)
        cnt += 1
    write(f, s)
    log.append((f, cnt, "계약서 PDF"))

# ── 2. 계약서 보기 10건 ────────────────────────────────────────────
DOC_OLD = '<a class="doc-link" href="#">계약서 보기</a>'
for f in ACQ_FILES:
    s = read(f)
    hits = s.count(DOC_OLD)
    if f == "acquisition--done.html":
        assert hits == 1, f"{f}: {hits}건"
        order = ["M2026-0004"]          # 남은 서명 대기 1건 = 바다마루 횟집
    else:
        assert hits == 3, f"{f}: {hits}건"
        order = PENDING_ORDER
    for mid in order:
        new = (f'<a class="doc-link" href="assets/docs/계약서_서명대기_{mid}.pdf" '
               f'target="_blank" rel="noopener">계약서 보기</a>')
        s = s.replace(DOC_OLD, new, 1)
    write(f, s)
    log.append((f, hits, "계약서 보기"))

# ── 3. 로고 18건 ───────────────────────────────────────────────────
for f in LOGO_FILES:
    patch(f, LOGO_OLD, LOGO_NEW, 1)

# ── 4. 비밀번호 찾기 1건 ───────────────────────────────────────────
s = read("login.html")
assert s.count(PW_CSS_ANCHOR) == 1 and s.count(PW_OLD) == 1
s = s.replace(PW_CSS_ANCHOR, PW_CSS_ANCHOR + PW_CSS_ADD).replace(PW_OLD, PW_NEW)
write("login.html", s)
log.append(("login.html", 1, "비밀번호 찾기 비활성"))

# ── 결과 ───────────────────────────────────────────────────────────
total = sum(n for _, n, _ in log)
for p, n, what in log:
    print(f"{n:>3}건  {p:<32} {what}")
print(f"\n배선 합계 {total}건")

rest = 0
for f in sorted(os.listdir(REPO)):
    if f.endswith(".html"):
        c = read(f).count('href="#"')
        if c:
            print(f"잔여 href=\"#\"  {c:>2}건  {f}")
            rest += c
print(f"잔여 합계 {rest}건")
