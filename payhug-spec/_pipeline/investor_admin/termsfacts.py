#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""용어정의서 원고가 쓰는 숫자를 원장 한 곳에서 읽는다.

termsdoc_seed.json 은 숫자를 손으로 적지 않고 `{{키}}` 로 적는다. 워드판
(build_termsdoc.py) 과 HTML 편집판(build_termsedit.py) 이 원고를 읽을 때 이
표를 끼워 넣으므로, 원장이 바뀌면 재생성만으로 값이 따라온다.

원천
  ledger_facts.json             daily_ledger.py 가 낸 화면 값
  verify_shortfall_result.json  표본 합 Σ L_i · Σ A_i

대표 원문 인용 자리(quote)는 손대지 않는다. 모르는 이름이 남으면 멈춘다.
"""
import copy
import io
import json
import os
import re
from datetime import date, timedelta
from decimal import Decimal as D, ROUND_HALF_UP

PIPE = os.path.dirname(os.path.abspath(__file__))
FACTS = os.path.join(PIPE, "ledger_facts.json")
SHORT = os.path.join(PIPE, "verify_shortfall_result.json")

TOKEN = re.compile(r"\{\{([A-Za-z][A-Za-z0-9_]*)\}\}")
SKIP_KEYS = ("quote",)


def _n(x):
    return "{:,}".format(int(x))


def _d(s):
    return date(*[int(v) for v in str(s).split("-")])


def tokens(path=None, short=None):
    """이름 → 넣을 글자. 값은 전부 원장에서 온다."""
    f = json.load(io.open(path or FACTS, encoding="utf-8"))
    asof = f["ledgerSpan"][1]
    row = f["tyByDate"][asof]
    total = D(f["total"])
    share = lambda v: str(
        (D(v) / total * 100).quantize(D("0.1"), rounding=ROUND_HALF_UP))
    week_from = _d(asof) - timedelta(days=int(f["weekDays"]) - 1)

    t = {
        "exec": _n(f["exec"]),
        "cash": _n(f["cash"]),
        "total": _n(f["total"]),
        "rate": f["rate"],
        "execPct": str(100 - D(f["rate"])),
        # 100만원 한 건을 예로 든 자리 — 할인율이 바뀌면 두 값이 함께 따라온다
        "millFee": _n(D(1000000) * D(f["rate"]) / 100),
        "millNet": _n(D(1000000) * (1 - D(f["rate"]) / 100)),
        "execShare": share(f["exec"]),
        "cashShare": share(f["cash"]),
        "w": f["w"],
        "wRaw": f["wRaw"],
        "ty": f["ty"],
        "s": f["s"],
        "sRaw": f["sRaw"],
        "receivables": _n(f["receivables"]),
        "openRecv": _n(f["openReceivables"]),
        "sampleRecv": _n(f["sampleReceivables"]),
        "sampleFrom": f["sampleSpan"][0],
        "sampleTo": f["sampleSpan"][1],
        "merchants": str(len(f["merchants"])),
        "ledgerDays": _n(f["ledgerDays"]),
        "ledgerFrom": f["ledgerSpan"][0],
        "ledgerTo": f["ledgerSpan"][1],
        "asof": asof,
        "diFrom": str(f["diRange"][0]),
        "diTo": str(f["diRange"][1]),
        "weekDays": str(f["weekDays"]),
        "weekFrom": week_from.isoformat(),
        "weekTo": asof,
        "weekExec": _n(f["weekExec"]),
        "weekProfit": _n(f["weekProfit"]),
        "weekRepay": _n(f["weekRepay"]),
        "weekPsc": _n(f["weekPsc"]),
        "weekW": f["weekW"],
        "weekWRaw": f["weekWRaw"],
        "weekTy": f["weekTy"],
        "weekTyAsset": f["weekTyAsset"],
        "dayW": row[0],
        "dayTy": row[1],
        "dayExec": _n(row[2]),
        "dayProfit": _n(row[3]),
        "dayRepay": _n(row[4]),
        "dayWRaw": f["w6ByDate"][asof],
    }

    sp = short or SHORT
    if os.path.exists(sp):
        so = json.load(io.open(sp, encoding="utf-8"))
        sos = ((so.get("delta") or {}).get("sum_over_sum") or {})
        if sos.get("SL") is not None:
            t["sampleL"] = _n(sos["SL"])
        if sos.get("SA") is not None:
            t["sampleA"] = _n(sos["SA"])
    return t


def fill(text, tk):
    def one(m):
        k = m.group(1)
        if k not in tk:
            raise KeyError("원장에 없는 이름 — {{%s}}" % k)
        return str(tk[k])
    return TOKEN.sub(one, text)


def resolve(seed, tk=None):
    """원고 한 벌을 받아 값을 끼운 새 벌을 낸다. 인용 자리는 그대로 둔다."""
    tk = tk or tokens()
    out = copy.deepcopy(seed)

    def walk(o):
        if isinstance(o, dict):
            return dict((k, o[k] if k in SKIP_KEYS else walk(o[k])) for k in o)
        if isinstance(o, list):
            return [walk(v) for v in o]
        if isinstance(o, str):
            return fill(o, tk)
        return o

    out = walk(out)
    sc = out.get("scale")
    if isinstance(sc, dict):
        f = json.load(io.open(FACTS, encoding="utf-8"))
        sc["투자실행액"] = f["exec"]
        sc["순현금"] = f["cash"]
        sc["가맹점수"] = len(f["merchants"])
        sc["할인율"] = float(D(f["rate"]) / 100)
    if "asof" in out:
        out["asof"] = tk["asof"]
    return out


if __name__ == "__main__":
    for k, v in tokens().items():
        print("%-14s %s" % (k, v))
