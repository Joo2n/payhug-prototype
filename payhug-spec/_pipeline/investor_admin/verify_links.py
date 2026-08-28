#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""배선 링크 전건 실측 — 로컬 서버가 실제 파일을 돌려주는지 HTTP 200 + 바이트 일치로 확인.

대상 — 루트 HTML 전량의 로컬 href (외부 URL·앵커·mailto 제외).
비교 — 응답 본문 바이트 == 디스크 파일 바이트.
"""

import io
import os
import re
import sys
import urllib.parse
import urllib.request

REPO = "/Users/semi/cursor/payhug-investor-admin"
BASE = "http://localhost:8901/"
SKIP_FILES = set()                     # 전 파일 검사. archive.html 도 레포 상대 경로만 걸므로 제외하지 않는다

HREF = re.compile(r'(?<![-\w])(?:href|src)="([^"]+)"')   # data-src= 같은 접두 속성을 잡지 않는다

rows, fails = [], 0


def chk(name, ok, detail=""):
    global fails
    if not ok:
        fails += 1
    rows.append((name, ok, detail))


def html_files():
    """검사 대상 = 루트 HTML + assets/ HTML. assets/ 안의 파일도 배포에서 주소로 열린다."""
    out = [f for f in sorted(os.listdir(REPO)) if f.endswith(".html") and f not in SKIP_FILES]
    out += ["assets/" + f for f in sorted(os.listdir(os.path.join(REPO, "assets")))
            if f.endswith(".html")]
    return out


BASE_TAG = re.compile(r'<base[^>]*href="([^"]+)"[^>]*>')

targets = {}
for f in html_files():
    s = io.open(os.path.join(REPO, f), encoding="utf-8").read()
    # 배포 주소 기준으로 푼다 — 링크는 그 파일이 놓인 자리에서 상대다.
    # <base href> 가 있으면 그것이 기준이다(assets/template.html 이 ../ 로 루트를 가리킨다).
    bm = BASE_TAG.search(s)
    root = os.path.dirname(f)
    if bm:
        root = os.path.normpath(os.path.join(root, bm.group(1)))
        root = "" if root == "." else root
    for h in HREF.findall(BASE_TAG.sub(" ", s)):     # <base> 는 링크가 아니라 기준이다
        if h.startswith(("http://", "https://", "#", "mailto:", "data:", "//")):
            continue
        if "'+" in h or '"+' in h or "' +" in h or '" +' in h:   # JS 문자열 조립 — 아래 동적 대조에서 본다
            continue
        rel = os.path.normpath(os.path.join(root, h)) if root else h
        if rel.startswith(".."):
            chk("%s → %s" % (f, h), False, "레포 밖으로 나간다")
            continue
        targets.setdefault(rel, []).append(f)

print("로컬 링크 고유 %d개 / 참조 %d건" % (len(targets), sum(len(v) for v in targets.values())))

# G-7 — 배포본에서 죽는 주소 0건. 로컬 서버 주소는 링크가 될 수 없다.
_local = []
for f in sorted(os.listdir(REPO)):
    if not f.endswith(".html"):
        continue
    for h in HREF.findall(io.open(os.path.join(REPO, f), encoding="utf-8").read()):
        if "localhost" in h or "127.0.0.1" in h:
            _local.append("%s → %s" % (f, h))
chk("로컬 서버 주소 링크 0건", not _local, ", ".join(_local[:5]) or "없음")

for h in sorted(targets):
    disk = os.path.join(REPO, urllib.parse.unquote(h))
    where = "%s (참조 %d건)" % (h, len(targets[h]))
    if not os.path.exists(disk):
        chk(where, False, "디스크에 파일 없음")
        continue
    url = BASE + urllib.parse.quote(urllib.parse.unquote(h))
    try:
        r = urllib.request.urlopen(url, timeout=20)
        body = r.read()
        code = r.getcode()
    except Exception as e:                                    # noqa: BLE001
        chk(where, False, "요청 실패 %s" % e)
        continue
    want = os.path.getsize(disk)
    ok = (code == 200 and len(body) == want)
    chk(where, ok, "%d · %dB / 디스크 %dB" % (code, len(body), want))

doc_refs = [h for h in targets if h.startswith("assets/docs/")]
xls_refs = [h for h in targets if h.startswith("assets/xlsx/")]
print("  assets/docs 고유 %d개 · 참조 %d건" % (len(doc_refs), sum(len(targets[h]) for h in doc_refs)))
print("  assets/xlsx 고유 %d개 · 참조 %d건" % (len(xls_refs), sum(len(targets[h]) for h in xls_refs)))

# app.html 이 코드로 만들어 내려주는 파일명도 실물 대조
APP = io.open(os.path.join(REPO, "app.html"), encoding="utf-8").read()
for var in ["CERT_PDF", "CT_SIG_ALL", "CT_SIG_SEL3"]:
    m = re.search(r"var %s\s*=\s*'([^']+)'" % var, APP)
    name = m.group(1) if m else None
    p = os.path.join(REPO, "assets/docs", name) if name else None
    chk("app.html %s → %s" % (var, name), bool(name) and os.path.exists(p))
# 계약기록 행이 거는 것은 전자서명 결과 텍스트다(대표 미팅 2026-08-28 M-2). 실물 = build_sigtext.py
for i in range(1, 17):
    mid = "M2026-%04d" % i
    chk("app.html ct-file %s" % mid, os.path.exists(os.path.join(REPO, "assets/docs", "전자서명결과_%s.txt" % mid)))
# 계약서보기가 여는 원문은 가맹점과 무관한 한 벌이다(당사자 공란)
m = re.search(r"var CONTRACT_TXT\s*=\s*'([^']+)'", APP)
chk("app.html CONTRACT_TXT → %s" % (m.group(1) if m else None),
    bool(m) and os.path.exists(os.path.join(REPO, "assets/docs", m.group(1))))

print("\n== 링크 실측 %d건 · FAIL %d ==" % (len(rows), fails))
for name, ok, detail in rows:
    if not ok:
        print("  FAIL " + name + "  " + detail)
if not fails:
    print("  전건 200 · 바이트 일치")
sys.exit(1 if fails else 0)
