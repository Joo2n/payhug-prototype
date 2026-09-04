#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""투자자 어드민 화면이 약속하는 실물 문서(PDF) 생성기.

산출 — payhug-investor-admin/assets/docs/
  투자자산증명서_YYYYMMDD.pdf     certificate.html 전자문서의 실물

계약서·전자서명 결과는 텍스트다(D-12·D-27). 그쪽 산출은 build_sigtext.py 소관이며
계약서 원문은 contract_text.py 한 곳에서 온다.

값은 전부 화면에서 긁어온다. 지어내지 않는다.
  가맹점 원장   merchants*.html (없는 MID 는 _pipeline/investor_admin/roster16_model.py 로 보충)
  자산 명세     certificate.html (가맹점별 투자자산 표 · 합계 · 서명값)
다른 조가 화면 수치를 고치면 이 스크립트를 다시 돌려 문서를 맞춘다.
"""

import html
import os
import re
import shutil
import subprocess
import sys
import tempfile

REPO = "/Users/semi/cursor/payhug-investor-admin"
PIPE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(REPO, "assets", "docs")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

ISSUER = "㈜페이허그"


# ══════════════════════════════════════════════════════════════════
#  화면 판독
# ══════════════════════════════════════════════════════════════════

def screen(name):
    with open(os.path.join(REPO, name), encoding="utf-8") as f:
        return f.read()


def strip(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()


def cells(tr):
    return [strip(c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)]


def read_merchants():
    """가맹점 원장 — MID → (상호, 사업자번호, 대표자, 업종, 종목)."""
    led = {}
    for f in sorted(os.listdir(REPO)):
        if not re.match(r"merchants(--[a-z-]+)?\.html$", f):
            continue
        for tr in re.findall(r'<tr class="clickable">(.*?)</tr>', screen(f), re.S):
            c = cells(tr)
            if len(c) >= 6 and re.match(r"M\d{4}-\d{4}$", c[0]):
                led[c[0]] = (c[1], c[2], c[3], c[4], c[5])

    # 화면에 아직 행이 없는 MID 는 로스터 모델에서 보충
    sys.path.insert(0, PIPE)
    try:
        from roster16_model import ROSTER
    except Exception:
        ROSTER = []
    for name, _amt, _w, _s, mid, biz, ceo, sector, item, _signed in ROSTER:
        led.setdefault(mid, (name, biz, ceo, sector, item))
    return led


def read_certificate(ledger):
    """투자자산 증명서 화면 — 메타·표·합계·서명값."""
    s = screen("certificate.html")
    by_name = {v[0]: k for k, v in ledger.items()}

    meta = dict(re.findall(r'<span class="k">([^<]+)</span>(?:<span[^>]*>)?([^<]+)', s))
    investor = next((v.strip() for k, v in meta.items() if "투자자" in k), "—")
    made = next((v.strip() for k, v in meta.items() if "작성일자" in k), "—")

    tbl = re.search(r'<table class="doc-tbl">(.*?)</table>', s, re.S).group(1)
    rows, total = [], None
    for tr in re.findall(r"<tr>(.*?)</tr>", tbl, re.S):
        c = cells(tr)
        if len(c) != 6 or c[0] in ("가맹점",):
            continue
        if c[0] == "합계":
            total = c[1:]
            continue
        rows.append((by_name.get(c[0], "—"), c[0], c[1], c[2], c[3], c[4], c[5]))

    sig = re.search(r'<(?:div|span) class="sig-value">([^<]+)</(?:div|span)>', s)
    return dict(investor=investor, made=made, rows=rows, total=total,
                sig=sig.group(1).strip() if sig else "—")


# ══════════════════════════════════════════════════════════════════
#  조판
# ══════════════════════════════════════════════════════════════════

CSS = """
@page { size: A4; margin: 14mm 18mm 16mm; }
* { box-sizing: border-box; }
body {
  margin: 0; font-family: "Apple SD Gothic Neo", "Noto Sans KR", "Malgun Gothic", sans-serif;
  font-size: 10pt; line-height: 1.62; color: #1a1f2b; -webkit-print-color-adjust: exact;
}
/* 견본 머리띠 — thead 러닝 헤더로 매 페이지 반복 */
table.doc { width: 100%; border-collapse: collapse; }
table.doc > thead > tr > th { padding: 0 0 6mm; border: 0; font-weight: 400; }
table.doc > tbody > tr > td { padding: 0; border: 0; }
.stamp {
  background: #FDF3D6; border: 1px solid #E7C86A; color: #6B5310;
  padding: 1.6mm 0; font-size: 7.5pt; letter-spacing: 0.06em; text-align: center;
}
.wm {
  position: fixed; top: 40%; left: 0; right: 0; text-align: center;
  font-size: 52pt; font-weight: 700; color: rgba(27,37,55,0.07);
  letter-spacing: 0.2em; transform: rotate(-24deg); z-index: 0;
}
.sheet { position: relative; z-index: 1; }
h1 { font-size: 17pt; text-align: center; letter-spacing: 0.1em; margin: 0 0 3mm; font-weight: 700; }
.docno { text-align: center; font-size: 8.5pt; color: #6B7280; margin: 0 0 7mm;
  font-variant-numeric: tabular-nums; }
h2 { font-size: 11pt; margin: 7mm 0 2.5mm; padding-bottom: 1.5mm;
  border-bottom: 1.4px solid #1B2537; font-weight: 700; }
h3 { font-size: 10pt; margin: 4.5mm 0 1.5mm; font-weight: 700; color: #1B2537; }
p { margin: 0 0 2.4mm; }
.sheet table { width: 100%; border-collapse: collapse; margin: 2mm 0 3mm; font-size: 9pt; }
.sheet th, .sheet td { border: 1px solid #C9CFDA; padding: 2mm 2.4mm; vertical-align: top; }
.sheet th { background: #F2F4F8; word-break: keep-all; font-weight: 600; text-align: left; }
.sheet td.n, .sheet th.n { text-align: right; font-variant-numeric: tabular-nums; }
.sheet td.c, .sheet th.c { text-align: center; }
.sheet tr.tot td { background: #F7F8FB; font-weight: 700; }
.k { width: 30mm; background: #F2F4F8; font-weight: 600; }
ol { margin: 0 0 2.4mm; padding-left: 6.5mm; }
li { margin-bottom: 1.4mm; }
.note {
  background: #F7F8FB; border: 1px solid #D8DEE8; border-left: 3px solid #6B7280;
  padding: 2.6mm 3mm; font-size: 8.5pt; color: #414A5C; margin: 3mm 0;
}
.note b { color: #1B2537; }
.warn { border-left-color: #C9922A; background: #FDF9EF; }
.src { font-size: 8pt; color: #6B7280; margin: 1.5mm 0 0; }
.sign-area { margin-top: 8mm; page-break-inside: avoid; }
.sign-box {
  border: 1px solid #C9CFDA; padding: 3mm 3.5mm; margin-bottom: 2.5mm;
  display: flex; align-items: flex-end; gap: 4mm;
}
.sign-box .role { width: 26mm; font-size: 8.5pt; color: #6B7280; font-weight: 600; }
.sign-box .who { flex: 1; font-size: 9.5pt; }
.sign-box .who small { display: block; color: #6B7280; font-size: 8pt; margin-top: 0.6mm; }
.sign-box .slot {
  width: 34mm; height: 13mm; border: 1px dashed #B6BECC; border-radius: 2px;
  display: flex; align-items: center; justify-content: center;
  font-size: 7.5pt; color: #9AA3B2;
}
.foot { margin-top: 7mm; border-top: 1px solid #D8DEE8; padding-top: 2.5mm;
  font-size: 7.5pt; color: #6B7280; }
.mono { font-variant-numeric: tabular-nums; }
.pb { page-break-before: always; }
"""


def page(title, body):
    return (
        "<!doctype html><html lang=\"ko\"><head><meta charset=\"utf-8\">"
        f"<title>{html.escape(title)}</title><style>{CSS}</style></head><body>"
        "<div class=\"wm\">견본</div>"
        "<table class=\"doc\"><thead><tr><th><div class=\"stamp\">"
        "견본 · 제안서 시연용 — 계약 효력 없음 · 실제 서명·인증 미포함"
        "</div></th></tr></thead><tbody><tr><td>"
        f"<div class=\"sheet\">{body}</div>"
        "</td></tr></tbody></table></body></html>"
    )


def foot(base_date):
    return f"<div class=\"foot\">기준일 {base_date} · {ISSUER}</div>"


def build_certificate(cert):
    rows = "".join(
        f"<tr><td>{html.escape(n)}<br><small class=\"src\">{mid}</small></td>"
        f"<td class=\"n\">{amt}</td><td class=\"n\">{w}</td>"
        f"<td class=\"n\">{s}</td><td class=\"n\">{ty}</td><td class=\"n\">{sh}</td></tr>"
        for mid, n, amt, w, s, ty, sh in cert["rows"]
    )
    t = cert["total"]
    # 합계는 tbody 마지막 행. tfoot 은 Chrome 인쇄에서 페이지마다 반복돼
    # 그 페이지까지의 소계로 오독된다.
    total_row = ("<tr class=\"tot\"><td>합계</td>"
                 + "".join(f"<td class=\"n\">{v}</td>" for v in t) + "</tr>") if t else ""
    return page("투자자산 증명서 (견본)", f"""
<h1>투자자산 증명서</h1>
<p class="docno">가맹점별 투자자산 · 기준일 {cert['made']} · 대상 가맹점 {len(cert['rows'])}개</p>

<table>
  <colgroup><col style="width:32mm"><col><col style="width:32mm"><col></colgroup>
  <tbody>
    <tr><td class="k">투자자</td><td>{html.escape(cert['investor'])}</td>
        <td class="k">작성자</td><td>{ISSUER}</td></tr>
    <tr><td class="k">작성일자</td><td class="mono">{cert['made']}</td>
        <td class="k">대상 가맹점</td><td>{len(cert['rows'])}개</td></tr>
  </tbody>
</table>

<h2>가맹점별 투자자산</h2>
<table>
  <colgroup><col><col style="width:32mm"><col style="width:22mm"><col style="width:24mm">
    <col style="width:22mm"><col style="width:18mm"></colgroup>
  <thead><tr><th>가맹점</th><th class="n">투자실행액 (원)</th><th class="n">가중평균 금융일수</th>
    <th class="n">입금부족률</th><th class="n">예상 연환산수익률</th><th class="n">비중</th></tr></thead>
  <tbody>{rows}{total_row}</tbody>
</table>
<h2>서명 및 검증</h2>
<p>발급 문서에는 {ISSUER} 인증서 서명값과 인증서 발행기관의 서명 검증 회신전문이 함께 포함된다.</p>
<table>
  <colgroup><col style="width:36mm"><col></colgroup>
  <tbody>
    <tr><td class="k">작성자</td><td>{ISSUER}</td></tr>
    <tr><td class="k">서명값</td><td><span class="mono" style="font-size:8pt">{html.escape(cert['sig'])}</span>
      <br><small class="src">견본 — 실제 서명값이 아니다.</small></td></tr>
    <tr><td class="k">서명 검증</td><td>견본 문서 — 인증서 발행기관 검증 회신전문 미첨부</td></tr>
  </tbody>
</table>

{foot(cert['made'])}
""")


# ══════════════════════════════════════════════════════════════════

def render(name, doc, tmpdir):
    src = os.path.join(tmpdir, name + ".html")
    with open(src, "w", encoding="utf-8") as f:
        f.write(doc)
    dst = os.path.join(OUT, name + ".pdf")
    subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
         "--virtual-time-budget=4000", f"--print-to-pdf={dst}", "file://" + src],
        check=True, capture_output=True,
    )
    return dst


def main():
    ledger = read_merchants()
    cert = read_certificate(ledger)
    investor = cert["investor"]
    base = cert["made"]

    print(f"판독 — 가맹점 {len(ledger)} · "
          f"증명서 행 {len(cert['rows'])} · 투자자 {investor}")
    missing = [m for m, _n, _a, _w, _s, _t, _h in cert["rows"] if m == "—"]
    if missing:
        print(f"  ! 증명서 표에 MID 미대조 {len(missing)}건")

    os.makedirs(OUT, exist_ok=True)
    tmpdir = tempfile.mkdtemp(prefix="phdocs-")
    made = []
    try:
        made.append(render(f"투자자산증명서_{base.replace('-', '')}",
                           build_certificate(cert), tmpdir))
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    for p in made:
        print(f"{os.path.getsize(p):>9,}  {os.path.basename(p)}")
    print(f"\n총 {len(made)}건 → {OUT}")


if __name__ == "__main__":
    main()
