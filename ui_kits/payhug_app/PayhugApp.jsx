// PayHug app — responsive web layout (수정.fig 기준).
// 메인(잇잇 · 미리받는돈 · 6월총매출[매출/비용/수익 탭 + 접이식 달력]) →
// 총매출액(날짜별) → 카드/배달앱 상세 → 단건 / 미매입 내역 / 계좌 입금 내역.
// Exposes window.PHPayhugApp.
(function () {
  const { SalesBreakdown, Badge } = window.PayHugDesignSystem_2ffe20;
  const D = window.PHAPP;
  const won = (n) => (typeof n === "number" ? n.toLocaleString("ko-KR") + "원" : n);
  const wonN = (n) => (typeof n === "number" ? n.toLocaleString("ko-KR") : n);

  const C_TOTAL = "var(--ph-ink)";
  const C_CARD = "var(--ph-blue-600)";
  const C_DELIV = "var(--ph-success-600)";

  const Ic = (d, c = "currentColor") => <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d={d} stroke={c} strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" /></svg>;
  const BACK = "M15 6l-6 6 6 6", PREV = "M14 6l-6 6 6 6", NEXT = "M10 6l6 6-6 6", CH_R = "M9 6l6 6-6 6", CH_D = "M6 9l6 6 6-6", CH_U = "M6 15l6-6 6 6";

  const Money = ({ children, c = "var(--text-primary)", s = 16, w = 700 }) => (
    <span className="ph-num" style={{ fontFamily: "var(--font-num)", fontVariantNumeric: "tabular-nums lining-nums", fontSize: s, fontWeight: w, color: c, whiteSpace: "nowrap", flex: "none" }}>{children}</span>
  );
  const Card = ({ children, style, onClick }) => (
    <div onClick={onClick} style={{ background: "#fff", borderRadius: 20, boxShadow: "0 1px 16px rgba(0,0,0,0.10)", boxSizing: "border-box", ...style }}>{children}</div>
  );
  const detailCard = { background: "#fff", borderRadius: 20, boxShadow: "0 1px 16px rgba(0,0,0,0.10)", overflow: "hidden" };
  const pad = { padding: "0 20px 24px" };

  function CardHeader({ title, onBack }) {
    return (
      <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "16px 18px 10px" }}>
        {onBack && <span onClick={onBack} style={{ cursor: "pointer", display: "inline-flex", color: "var(--text-primary)", marginLeft: -6 }}>{Ic(BACK)}</span>}
        <span style={{ fontSize: 19, fontWeight: 700 }}>{title}</span>
      </div>
    );
  }
  function DateNav({ label, sub }) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 24, padding: "8px 0 6px" }}>
        <span style={{ color: "var(--ph-gray-400)", display: "inline-flex" }}>{Ic(PREV)}</span>
        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: 16, fontWeight: 700 }}>{label}</div>
          {sub && <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 2 }}>{sub}</div>}
        </div>
        <span style={{ color: "var(--ph-gray-400)", display: "inline-flex" }}>{Ic(NEXT)}</span>
      </div>
    );
  }
  function KV({ k, sub, v, bold, color, indent }) {
    return (
      <div style={{ display: "flex", alignItems: "center", padding: "11px 0", paddingLeft: indent ? 16 : 0,
        borderLeft: indent ? "1.5px solid var(--border-default)" : "none", marginLeft: indent ? 4 : 0 }}>
        <span style={{ fontSize: indent ? 14.5 : 16, fontWeight: bold ? 700 : 500, color: indent ? "var(--text-secondary)" : "var(--text-primary)" }}>{k}</span>
        {sub != null && <span className="ph-num" style={{ fontSize: 13, color: "var(--text-muted)", marginLeft: 8, fontFamily: "var(--font-num)" }}>{sub}</span>}
        <div style={{ flex: 1 }} />
        <Money s={indent ? 14.5 : 16} w={bold ? 700 : 600} c={color || (indent ? "var(--text-secondary)" : "var(--text-primary)")}>{typeof v === "number" ? won(v) : v}</Money>
      </div>
    );
  }
  function HiliteRow({ label, count, amount, tone }) {
    const blue = tone === "blue";
    const bg = blue ? "var(--ph-blue-tint)" : "#FDF1F0";
    const fg = blue ? "var(--ph-blue-600)" : "#D75751";
    return (
      <div style={{ display: "flex", alignItems: "center", gap: 8, background: bg, borderRadius: 12, padding: "12px 14px", margin: "4px 0" }}>
        <span style={{ fontSize: 15, fontWeight: 700, color: fg }}>{label}</span>
        {count != null && <span className="ph-num" style={{ fontSize: 12.5, color: fg, opacity: 0.8, fontFamily: "var(--font-num)" }}>{count}건</span>}
        <div style={{ flex: 1 }} />
        <Money s={16} c={fg}>+{wonN(amount)}원</Money>
      </div>
    );
  }
  function GreenNote({ children }) {
    return <div style={{ background: "var(--ph-green-tint)", color: "var(--ph-forest)", borderRadius: 14, padding: "16px 18px", fontSize: 14, lineHeight: 1.6, whiteSpace: "pre-line" }}>{children}</div>;
  }
  function GreenButton({ children, onClick }) {
    return <button onClick={onClick} style={{ width: "100%", height: 56, border: "none", borderRadius: 16, background: "var(--ph-green)", color: "var(--ph-forest)", fontFamily: "var(--font-sans)", fontSize: 17, fontWeight: 700, cursor: "pointer" }}>{children}</button>;
  }
  function Tag({ done }) {
    return (
      <span style={{ fontSize: 12, fontWeight: 700, padding: "3px 8px", borderRadius: 6,
        background: done ? "#E9F8FF" : "#FDF1F0", color: done ? "var(--ph-blue-600)" : "#D75751" }}>
        {done ? "매입 완료" : "미매입"}
      </span>
    );
  }

  const DOW = ["일", "월", "화", "수", "목", "금", "토"];
  const fmt = (n) => (n == null ? null : n.toLocaleString("ko-KR"));
  const dayLabel = (day) => {
    const cal = D.salesCalendar;
    const w = DOW[new Date(cal.year, cal.month - 1, day).getDay()];
    return `26년 6월 ${day}일 (${w})`;
  };
  const TABS = [
    { key: "sales", label: "매출", monthKey: "sales", title: "6월 총 매출", screen: "totalsales",
      legend: [["총 매출액", C_TOTAL], ["카드", C_CARD], ["배달앱", C_DELIV]] },
    { key: "cost", label: "비용", monthKey: "cost", title: "6월 총 비용", screen: "costdetail",
      legend: [["총 비용", C_TOTAL], ["카드 비용", C_CARD], ["배달앱 비용", C_DELIV]] },
    { key: "profit", label: "수익", monthKey: "profit", title: "6월 총 수익", screen: "profitdetail",
      legend: [["총 수익", C_TOTAL], ["카드 수익", C_CARD], ["배달앱 수익", C_DELIV]] },
  ];
  function dayValues(tab, x) {
    if (!x) return [];
    const m = D.dayMetrics(x);
    if (tab === "sales") return [[m.sales, C_TOTAL], [m.cardSales, C_CARD], [m.delivSales, C_DELIV]];
    if (tab === "cost") return [[m.cost, C_TOTAL], [m.cardCost, C_CARD], [m.delivCost, C_DELIV]];
    return [[m.profit, C_TOTAL], [m.cardProfit, C_CARD], [m.delivProfit, C_DELIV]];
  }

  function MonthSalesCard({ push }) {
    const cal = D.salesCalendar;
    const [tab, setTab] = React.useState("sales");
    const [open, setOpen] = React.useState(false);
    const t = TABS.find((x) => x.key === tab);

    const startDow = new Date(cal.year, cal.month - 1, 1).getDay();
    const daysInMonth = new Date(cal.year, cal.month, 0).getDate();
    const prevDays = new Date(cal.year, cal.month - 1, 0).getDate();
    const cells = [];
    for (let i = 0; i < 42; i++) {
      const dn = i - startDow + 1;
      if (dn < 1) cells.push({ d: prevDays + dn, out: true });
      else if (dn > daysInMonth) cells.push({ d: dn - daysInMonth, out: true });
      else cells.push({ d: dn, out: false });
    }
    const todayRow = Math.floor((startDow + cal.today - 1) / 7);
    const fullRows = Math.ceil((startDow + daysInMonth) / 7);
    const view = open ? cells.slice(0, fullRows * 7) : cells.slice(todayRow * 7, todayRow * 7 + 7);

    return (
      <Card style={{ padding: "26px 22px 8px" }}>
        <div onClick={() => push({ name: t.screen, day: cal.today })} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", cursor: "pointer" }}>
          <span style={{ fontSize: 20, fontWeight: 700 }}>{t.title}</span>
          <span style={{ color: "var(--ph-gray-400)" }}>{Ic(CH_R)}</span>
        </div>
        <div style={{ marginTop: 10 }}><Money s={28} c="var(--text-secondary)">{wonN(cal.monthly[t.monthKey])}원</Money></div>

        <div style={{ display: "flex", gap: 8, marginTop: 18 }}>
          {TABS.map((x) => {
            const on = x.key === tab;
            return (
              <button key={x.key} onClick={() => setTab(x.key)} style={{ border: "none", cursor: "pointer",
                padding: "8px 18px", borderRadius: 9, fontFamily: "var(--font-sans)", fontSize: 14, fontWeight: 700,
                background: on ? "var(--ph-blue-600)" : "var(--ph-gray-100)", color: on ? "#fff" : "var(--text-secondary)" }}>{x.label}</button>
            );
          })}
        </div>

        <div style={{ display: "flex", flexWrap: "wrap", gap: "8px 22px", background: "var(--ph-gray-50)", borderRadius: 14, padding: "14px 18px", marginTop: 14 }}>
          {t.legend.map(([lb, cc]) => (
            <div key={lb} style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span style={{ width: 14, height: 14, borderRadius: 4, background: cc, flex: "none" }} />
              <span style={{ fontSize: 13, color: "var(--text-secondary)" }}>{lb}</span>
            </div>
          ))}
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(7,1fr)", marginTop: 16 }}>
          {DOW.map((d) => <div key={d} style={{ textAlign: "left", paddingLeft: 6, fontSize: 13, color: "var(--text-secondary)", paddingBottom: 8 }}>{d}</div>)}
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(7,1fr)", borderTop: "1px solid var(--ph-gray-200)" }}>
          {view.map((cell, i) => {
            const data = !cell.out && cell.d <= cal.today ? cal.days[cell.d] : null;
            const isToday = !cell.out && cell.d === cal.today;
            const vals = dayValues(tab, data);
            return (
              <div key={i} onClick={() => data && push({ name: t.screen, day: cell.d })}
                style={{ borderTop: "1px solid var(--ph-gray-100)", minHeight: 62, padding: "8px 3px 10px 6px",
                  display: "flex", flexDirection: "column", alignItems: "flex-start", gap: 5, cursor: data ? "pointer" : "default" }}>
                <span className="ph-num" style={{ fontFamily: "var(--font-num)", fontSize: 13, fontWeight: 500,
                  color: cell.out ? "var(--ph-gray-300)" : "var(--text-secondary)",
                  width: 24, height: 24, display: "flex", alignItems: "center", justifyContent: "center",
                  borderRadius: "50%", background: isToday ? "var(--ph-gray-200)" : "transparent" }}>{cell.d}</span>
                {vals.length > 0 && (
                  <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-start", lineHeight: 1.25, width: "100%" }}>
                    {vals.map(([v, cc], k) => (v ? <span key={k} className="ph-num" style={{ fontSize: 10.5, fontWeight: 600, color: cc, fontFamily: "var(--font-num)" }}>{fmt(v)}</span> : null))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
        <div onClick={() => setOpen((o) => !o)} style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 4, padding: "14px 0 12px", cursor: "pointer", color: "var(--ph-gray-700)" }}>
          <span style={{ fontSize: 14, fontWeight: 500 }}>{open ? "달력 접기" : "달력 펼치기"}</span>
          {Ic(open ? CH_U : CH_D, "var(--ph-gray-500)")}
        </div>
      </Card>
    );
  }

  function Main({ push }) {
    const p = D.premoney;
    return (
      <div data-screen-label="메인" style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        <Card style={{ padding: "20px 22px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <span style={{ fontSize: 18, fontWeight: 700 }}>{D.store.name}</span>
            <Badge tone="success" size="sm">{D.store.status}</Badge>
            <div style={{ flex: 1 }} />
            <span style={{ color: "var(--ph-ink)" }}>{Ic(CH_D)}</span>
          </div>
          <div className="ph-num" style={{ fontSize: 13.5, color: "var(--text-secondary)", fontFamily: "var(--font-num)", marginTop: 8 }}>{D.store.biz}</div>
        </Card>

        <Card style={{ padding: "24px 24px 22px" }}>
          <div style={{ fontSize: 13.5, color: "var(--text-secondary)" }}>{p.dateLabel} · 오늘</div>
          <div onClick={() => push({ name: "premoney" })} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", cursor: "pointer", marginTop: 10 }}>
            <span style={{ fontSize: 21, fontWeight: 700 }}>미리 받는 돈</span>
            <span style={{ color: "var(--ph-gray-400)" }}>{Ic(CH_R)}</span>
          </div>
          <div style={{ marginTop: 12 }}><Money s={30} c="var(--ph-blue-600)">{wonN(p.total)}원</Money></div>
          <div style={{ marginTop: 14, fontSize: 17, fontWeight: 700, color: "rgba(126,130,153,0.75)" }}>어제 매출액 {won(p.yesterdaySales)}</div>
          <button onClick={() => push({ name: "deposits" })} style={{ width: "100%", height: 54, marginTop: 22, border: "none", borderRadius: 16, background: "var(--ph-gray-100)", color: "var(--text-secondary)", fontFamily: "var(--font-sans)", fontSize: 15, fontWeight: 600, cursor: "pointer" }}>계좌 입금 내역보기</button>
        </Card>

        <MonthSalesCard push={push} />
      </div>
    );
  }

  function Premoney({ push, pop }) {
    const p = D.premoney;
    const sections = [
      { label: "카드", amount: p.cardsTotal, rows: p.cards.map((c) => ({ key: c.key, issuer: c.name, count: c.count + "건", amount: c.amount, zero: c.amount === 0 })) },
      { label: "배달앱", amount: p.platformsTotal, rows: p.platforms.map((c) => ({ key: c.key, issuer: c.name, count: c.count + "건", amount: c.amount, zero: c.amount === 0 })) },
    ];
    const footer = { label: "페이허그", amount: p.payhug.total, rows: [
      { label: "예상 지급 차액", amount: p.payhug.expectedDiff, link: true, help: true },
      { label: "전산 수수료", amount: "면제" },
    ]};
    const onRow = (key) => (p.cards.some((c) => c.key === key) ? push({ name: "card", key }) : push({ name: "platform", key }));
    return (
      <div data-screen-label="미리 받는 돈" style={detailCard}>
        <CardHeader title="미리 받는 돈" onBack={pop} />
        <DateNav label={p.dateLabel} sub={p.reflectedAt} />
        <div style={{ textAlign: "center", padding: "8px 0 8px" }}><Money s={30} c="var(--ph-blue-600)">{wonN(p.total)}원</Money></div>
        <div style={pad}>
          <div style={{ background: "var(--ph-gray-100)", borderRadius: 12, padding: "12px 16px", fontSize: 14, color: "var(--text-secondary)", margin: "6px 0 14px" }}>어제 매출액 {won(p.yesterdaySales)}</div>
          <SalesBreakdown sections={sections} footer={footer} onRowClick={onRow} onFooterClick={() => push({ name: "diff" })} />
        </div>
      </div>
    );
  }

  function TotalSales({ params, push, pop }) {
    const ts = D.totalSales;
    const cal = D.salesCalendar;
    const day = params.day || cal.today;
    const dd = cal.days[day];
    const dayTotal = dd ? dd.cardSales + dd.delivSales : ts.total;
    const dateLabel = dayLabel(day);
    const sections = [
      { label: "카드", amount: ts.cardsTotal, rows: ts.cards.map((c) => ({ key: c.key, issuer: c.name, count: c.count + "건", amount: c.amount, zero: c.amount === 0 })) },
      { label: "배달앱", amount: ts.platformsTotal, rows: ts.platforms.map((c) => ({ key: c.key, issuer: c.name, count: c.count + "건", amount: c.amount, zero: c.amount === 0 })) },
    ];
    const onRow = (key) => (ts.cards.some((c) => c.key === key) ? push({ name: "card", key }) : push({ name: "platform", key }));
    return (
      <div data-screen-label="총 매출액" style={detailCard}>
        <CardHeader title="총 매출액" onBack={pop} />
        <DateNav label={dateLabel} sub={ts.reflectedAt} />
        <div style={{ textAlign: "center", padding: "8px 0 4px" }}><Money s={32} c="var(--ph-blue-600)">{wonN(dayTotal)}원</Money></div>
        <div style={{ textAlign: "center", fontSize: 13, color: "var(--text-muted)", paddingBottom: 12 }}>매입기준 매출</div>
        <div style={pad}>
          <div onClick={() => push({ name: "excluded" })} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", background: "var(--ph-gray-100)", borderRadius: 16, padding: "16px 20px", cursor: "pointer", marginBottom: 8 }}>
            <span style={{ fontSize: 15, fontWeight: 500, color: "var(--text-secondary)" }}>선정산 제외액 {won(ts.excludedTotal)}</span>
            <span style={{ color: "var(--ph-gray-400)" }}>{Ic(CH_R)}</span>
          </div>
          <SalesBreakdown sections={sections} onRowClick={onRow} />
          <div style={{ marginTop: 20 }}><GreenButton onClick={() => push({ name: "unpurchased" })}>미매입 내역 보러가기</GreenButton></div>
        </div>
      </div>
    );
  }

  function Unpurchased({ pop }) {
    const u = D.unpurchased;
    return (
      <div data-screen-label="미매입 내역" style={detailCard}>
        <CardHeader title="미매입 내역" onBack={pop} />
        <div style={{ ...pad, paddingTop: 4 }}>
          <div className="ph-num" style={{ fontSize: 13.5, color: "var(--text-secondary)", fontFamily: "var(--font-num)" }}>{u.date}</div>
          <div style={{ margin: "6px 0 16px" }}><Money s={32}>{wonN(u.total)}원</Money></div>
          <GreenNote>{u.note}</GreenNote>
          <div style={{ marginTop: 8 }}>
            {u.rows.map((r, i) => (
              <div key={i} style={{ display: "flex", alignItems: "flex-start", padding: "16px 0", borderBottom: "1px solid var(--border-hairline)" }}>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div className="ph-num" style={{ fontSize: 13, color: "var(--text-muted)", fontFamily: "var(--font-num)" }}>{r.date}</div>
                  <div style={{ fontSize: 17, fontWeight: 700, marginTop: 4 }}>{r.issuer}</div>
                </div>
                <div style={{ textAlign: "right" }}>
                  <div className="ph-num" style={{ fontSize: 12.5, color: "var(--text-muted)", fontFamily: "var(--font-num)" }}>승인번호 {r.apprv}</div>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "flex-end", gap: 8, marginTop: 6 }}>
                    <Tag done={r.status === "done"} />
                    <Money s={17}>{won(r.amount)}</Money>
                  </div>
                </div>
              </div>
            ))}
          </div>
          <div style={{ marginTop: 22 }}><GreenButton>내역 더 불러오기</GreenButton></div>
        </div>
      </div>
    );
  }

  function CardScreen({ params, pop, push }) {
    const { card, txns, summary } = D.cardTxns(params.key);
    return (
      <div data-screen-label={card.name} style={detailCard}>
        <CardHeader title={card.name} onBack={pop} />
        <DateNav label={D.totalSales.dateLabel} sub={D.UPDATE} />
        <div style={{ padding: "8px 20px 12px" }}>
          <KV k="어제 매출액" v={summary.yesterdaySales} />
          <KV k="차감액" v={summary.fee} bold />
          <KV k="카드 수수료" v={summary.fee} indent />
          {summary.addPurchase && <HiliteRow label="추가 매입" count={summary.addPurchase.count} amount={summary.addPurchase.amount} tone="blue" />}
          <div style={{ borderTop: "1px solid var(--border-default)", marginTop: 8 }} />
          <KV k="미리 받는 돈" v={summary.premoney} bold color="var(--ph-blue-600)" />
        </div>
        <div style={{ height: 8, background: "var(--ph-gray-100)" }} />
        <div style={{ padding: "16px 20px 24px" }}>
          <div style={{ fontSize: 16, fontWeight: 700, marginBottom: 6 }}>어제 카드 내역</div>
          {txns.map((t, i) => (
            <div key={i} onClick={() => push({ name: "txn", key: params.key, idx: i })} style={{ display: "flex", alignItems: "center", padding: "14px 0", borderBottom: "1px solid var(--border-hairline)", cursor: "pointer" }}>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 15, fontWeight: 600 }}>{card.name}</div>
                <div className="ph-num" style={{ fontSize: 12.5, color: "var(--text-muted)", fontFamily: "var(--font-num)" }}>{D.totalSales.dateLabel.replace(/26년 6월 (\d+)일.*/, "2026.06.$1")} · {t.time}</div>
              </div>
              <div style={{ textAlign: "right" }}>
                <Money s={16}>{won(t.net)}</Money>
                <div style={{ fontSize: 12.5, color: "var(--text-muted)" }}>{t.payType}</div>
              </div>
            </div>
          ))}
          <div style={{ marginTop: 22 }}><GreenButton>내역 더 불러오기</GreenButton></div>
        </div>
      </div>
    );
  }

  function TxnScreen({ params, pop }) {
    const { card, txns } = D.cardTxns(params.key);
    const t = txns[params.idx] || txns[0];
    const dnum = D.totalSales.dateLabel.replace(/26년 6월 (\d+)일.*/, "$1");
    return (
      <div data-screen-label={`${card.name} 단건`} style={detailCard}>
        <CardHeader title={`${card.name} 내역`} onBack={pop} />
        <div style={{ ...pad, paddingTop: 4 }}>
          <div className="ph-num" style={{ fontSize: 13, color: "var(--text-muted)", fontFamily: "var(--font-num)" }}>2026.06.{dnum} · {t.time}</div>
          <div style={{ margin: "6px 0 18px" }}><Money s={30}>{won(t.net)}</Money></div>
          <KV k="승인번호" v={<span className="ph-num" style={{ fontFamily: "var(--font-num)" }}>{t.apprv}</span>} />
          <KV k="결제수단" v={t.payType} />
          <KV k="어제 매출액" v={t.sales} />
          <KV k="차감액" v={t.fee} bold />
          <KV k="카드 수수료" v={t.fee} indent />
          <div style={{ borderTop: "1px solid var(--border-default)", marginTop: 8 }} />
          <KV k="미리 받는 돈" v={t.net} bold color="var(--ph-blue-600)" />
        </div>
      </div>
    );
  }

  function PlatformScreen({ params, pop, push }) {
    const pf = D.platformDetail[params.key];
    return (
      <div data-screen-label={pf.name} style={detailCard}>
        <CardHeader title={pf.name} onBack={pop} />
        <DateNav label={D.totalSales.dateLabel} sub={D.UPDATE} />
        <div style={{ padding: "8px 20px 12px" }}>
          <KV k="어제 매출액" v={pf.yesterdaySales} />
          <KV k="차감액" v={pf.deductTotal} bold />
          {pf.deducts.map((d, i) => <KV key={i} k={d[0]} v={d[1]} indent />)}
          {pf.excluded && <HiliteRow label="선정산 제외 금액" count={pf.excluded.count} amount={pf.excluded.amount} tone="coral" />}
          <div style={{ borderTop: "1px solid var(--border-default)", marginTop: 8 }} />
          <KV k="미리 받는 돈" v={pf.premoney} bold color="var(--ph-blue-600)" />
        </div>
        <div style={{ height: 8, background: "var(--ph-gray-100)" }} />
        <div style={{ padding: "16px 20px 24px" }}>
          <div style={{ fontSize: 16, fontWeight: 700, marginBottom: 6 }}>어제 주문 내역</div>
          {pf.orders.length === 0 && <div style={{ padding: 32, textAlign: "center", color: "var(--text-muted)" }}>주문 내역이 없어요</div>}
          {pf.orders.map((o, i) => (
            <div key={i} onClick={() => push({ name: "order", key: params.key, idx: i })} style={{ display: "flex", alignItems: "center", padding: "14px 0", borderBottom: "1px solid var(--border-hairline)", cursor: "pointer" }}>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 15, fontWeight: 500 }}>{o.shop}</div>
                <div className="ph-num" style={{ fontSize: 12.5, color: "var(--text-muted)", fontFamily: "var(--font-num)" }}>{o.date} · {o.time}</div>
              </div>
              <div style={{ textAlign: "right" }}>
                <Money s={16} c={o.amount < 0 ? "var(--text-money-neg)" : "var(--text-primary)"}>{(o.amount >= 0 ? "+" : "") + wonN(o.amount)}원</Money>
                <div style={{ fontSize: 12, color: "var(--text-muted)" }}>{o.pay}</div>
              </div>
            </div>
          ))}
          <div style={{ marginTop: 22 }}><GreenButton>내역 더 불러오기</GreenButton></div>
        </div>
      </div>
    );
  }

  function OrderScreen({ pop }) {
    const o = D.orderDetail;
    return (
      <div data-screen-label={`${o.name} 주문`} style={detailCard}>
        <CardHeader title={`${o.name} 내역`} onBack={pop} />
        <div style={{ ...pad, paddingTop: 4 }}>
          <div className="ph-num" style={{ fontSize: 13, color: "var(--text-muted)", fontFamily: "var(--font-num)" }}>{o.date} · {o.time}</div>
          <div style={{ margin: "6px 0 18px" }}><Money s={30} c="var(--ph-blue-600)">{(o.amount >= 0 ? "+" : "") + wonN(o.amount)}원</Money></div>
          <KV k="주문번호" v={<span className="ph-num" style={{ fontFamily: "var(--font-num)" }}>{o.orderNo}</span>} />
          <KV k="결제수단" v={o.pay} />
          <KV k="어제 매출액" v={o.yesterdaySales} />
          <KV k="차감액" v={o.deductTotal} bold />
          {o.deducts.map((d, i) => <KV key={i} k={d[0]} v={d[1]} indent />)}
          <div style={{ borderTop: "1px solid var(--border-default)", marginTop: 8 }} />
          <KV k="미리 받는 돈" v={o.premoney} bold color="var(--ph-blue-600)" />
          <div style={{ marginTop: 18 }}><GreenNote>{o.note}</GreenNote></div>
        </div>
      </div>
    );
  }

  function DiffScreen({ pop }) {
    const e = D.expectedDiff;
    return (
      <div data-screen-label="예상 지급 차액" style={detailCard}>
        <CardHeader title="예상 지급 차액" onBack={pop} />
        <div style={{ ...pad, paddingTop: 4 }}>
          <div className="ph-num" style={{ fontSize: 13, color: "var(--text-muted)", fontFamily: "var(--font-num)" }}>{e.dateLabel}</div>
          <div style={{ margin: "6px 0 14px" }}><Money s={30}>{wonN(e.total)}원</Money></div>
          <GreenNote>{e.note}</GreenNote>
          <div style={{ marginTop: 16 }}>
            {e.rows.map((r, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", padding: "14px 0", borderBottom: "1px solid var(--border-hairline)" }}>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div className="ph-num" style={{ fontSize: 13, color: "var(--text-muted)", fontFamily: "var(--font-num)" }}>{r.date}</div>
                  <div style={{ fontSize: 15, fontWeight: 600 }}>{r.issuer}</div>
                </div>
                <div style={{ textAlign: "right" }}>
                  <div className="ph-num" style={{ fontSize: 12.5, color: "var(--text-muted)", fontFamily: "var(--font-num)" }}>{r.no}</div>
                  <Money s={16} c={r.amount < 0 ? "var(--text-money-neg)" : "var(--ph-success-600)"}>{(r.amount >= 0 ? "+" : "") + wonN(r.amount)}원</Money>
                </div>
              </div>
            ))}
          </div>
          <div style={{ marginTop: 20 }}><GreenButton>내역 더 불러오기</GreenButton></div>
        </div>
      </div>
    );
  }

  function DepositsScreen({ pop }) {
    const d = D.deposits;
    return (
      <div data-screen-label="계좌 입금 내역" style={detailCard}>
        <CardHeader title="계좌 입금 내역" onBack={pop} />
        <div style={{ ...pad, paddingTop: 0 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12, padding: "4px 0 16px" }}>
            <div style={{ width: 40, height: 40, borderRadius: 10, background: "var(--ph-gray-100)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 20 }}>🏦</div>
            <div><div style={{ fontSize: 15, fontWeight: 700 }}>{d.bank}</div><div className="ph-num" style={{ fontSize: 13, color: "var(--text-muted)", fontFamily: "var(--font-num)" }}>{d.account}</div></div>
          </div>
          {d.rows.map((r, i) => (
            <div key={i} style={{ display: "flex", alignItems: "center", padding: "14px 0", borderBottom: "1px solid var(--border-hairline)" }}>
              <div style={{ width: 44, flex: "none" }}><span className="ph-num" style={{ fontSize: 14, fontWeight: 700, color: "var(--text-secondary)", fontFamily: "var(--font-num)" }}>{r.date}</span></div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 15, fontWeight: 600 }}>페이허그</div>
                <div className="ph-num" style={{ fontSize: 12.5, color: "var(--text-muted)", fontFamily: "var(--font-num)" }}>{r.time}</div>
              </div>
              <div style={{ textAlign: "right" }}>
                <Money s={16}>{won(r.amount)}</Money>
                <div style={{ marginTop: 3 }}>
                  {r.kind === "premoney" ? <Badge tone="green" size="sm">미리 받는 돈</Badge> : <Badge tone="blue" size="sm">선정산 제외액</Badge>}
                </div>
              </div>
            </div>
          ))}
          <div style={{ marginTop: 22 }}><GreenButton>내역 더 불러오기</GreenButton></div>
        </div>
      </div>
    );
  }

  function CostDetail({ params, pop }) {
    const cal = D.salesCalendar;
    const day = params.day || cal.today;
    const m = D.dayMetrics(cal.days[day]) || D.dayMetrics(cal.days[cal.today]);
    return (
      <div data-screen-label="총 비용" style={detailCard}>
        <CardHeader title="총 비용" onBack={pop} />
        <DateNav label={dayLabel(day)} sub={D.UPDATE} />
        <div style={{ textAlign: "center", padding: "8px 0 4px" }}><Money s={32} c="var(--ph-ink)">{wonN(m.cost)}원</Money></div>
        <div style={{ textAlign: "center", fontSize: 13, color: "var(--text-muted)", paddingBottom: 12 }}>카드·배달앱 수수료와 광고비 등 지출</div>
        <div style={pad}>
          <KV k="카드 수수료" v={m.cardFee} />
          <KV k="배달앱 수수료" v={m.delivFee} />
          <KV k="광고비" v={m.adFee} />
          <div style={{ borderTop: "1px solid var(--border-default)", marginTop: 8 }} />
          <KV k="총 비용" v={m.cost} bold />
        </div>
      </div>
    );
  }

  function ProfitDetail({ params, pop }) {
    const cal = D.salesCalendar;
    const day = params.day || cal.today;
    const m = D.dayMetrics(cal.days[day]) || D.dayMetrics(cal.days[cal.today]);
    return (
      <div data-screen-label="총 수익" style={detailCard}>
        <CardHeader title="총 수익" onBack={pop} />
        <DateNav label={dayLabel(day)} sub={D.UPDATE} />
        <div style={{ textAlign: "center", padding: "8px 0 4px" }}><Money s={32} c="var(--ph-success-600)">{wonN(m.profit)}원</Money></div>
        <div style={{ textAlign: "center", fontSize: 13, color: "var(--text-muted)", paddingBottom: 12 }}>총 매출에서 총 비용을 끌 금액이에요</div>
        <div style={pad}>
          <KV k="카드 수익" v={m.cardProfit} bold color="var(--ph-blue-600)" />
          <KV k="카드 매출" v={m.cardSales} indent />
          <KV k="카드 수수료" v={-m.cardFee} indent />
          <KV k="배달앱 수익" v={m.delivProfit} bold color="var(--ph-success-600)" />
          <KV k="배달앱 매출" v={m.delivSales} indent />
          <KV k="배달앱 수수료" v={-m.delivFee} indent />
          <KV k="광고비" v={-m.adFee} indent />
          <div style={{ borderTop: "1px solid var(--border-default)", marginTop: 8 }} />
          <KV k="총 수익" v={m.profit} bold />
        </div>
      </div>
    );
  }

  function Excluded({ push, pop }) {
    const e = D.excludedDetail;
    return (
      <div data-screen-label="선정산 제외액" style={detailCard}>
        <CardHeader title="선정산 제외액" onBack={pop} />
        <div style={{ ...pad, paddingTop: 4 }}>
          <div className="ph-num" style={{ fontSize: 13.5, color: "var(--text-secondary)", fontFamily: "var(--font-num)" }}>{e.date}</div>
          <div style={{ margin: "6px 0 16px" }}><Money s={32}>{wonN(e.total)}원</Money></div>
          <GreenNote>{e.note}</GreenNote>
          <div style={{ marginTop: 16 }}>
            {e.reasons.map((r, i) => (
              <div key={i} onClick={() => push({ name: r.key })} style={{ display: "flex", alignItems: "center", gap: 12, background: "var(--ph-gray-100)", borderRadius: 16, padding: "16px 18px", cursor: "pointer", marginBottom: 8 }}>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: "flex", alignItems: "baseline", gap: 8 }}>
                    <span style={{ fontSize: 16, fontWeight: 700 }}>{r.label}</span>
                    <span className="ph-num" style={{ fontSize: 12.5, color: "var(--text-muted)", fontFamily: "var(--font-num)" }}>{r.count}건</span>
                  </div>
                  <div style={{ fontSize: 13, color: "var(--text-secondary)", marginTop: 2 }}>{r.desc}</div>
                </div>
                <Money s={17}>{won(r.amount)}</Money>
                <span style={{ color: "var(--ph-gray-400)", display: "inline-flex" }}>{Ic(CH_R)}</span>
              </div>
            ))}
          </div>
          <div style={{ marginTop: 8 }}>
            {e.rows.map((r, i) => (
              <div key={i} style={{ display: "flex", alignItems: "flex-start", padding: "14px 0", borderBottom: "1px solid var(--border-hairline)" }}>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div className="ph-num" style={{ fontSize: 13, color: "var(--text-muted)", fontFamily: "var(--font-num)" }}>{r.date}</div>
                  <div style={{ fontSize: 16, fontWeight: 700, marginTop: 4 }}>{r.issuer}</div>
                </div>
                <div style={{ textAlign: "right" }}>
                  <span style={{ fontSize: 12, color: "var(--text-secondary)", background: "var(--ph-gray-100)", borderRadius: 6, padding: "3px 8px" }}>{r.reason}</span>
                  <div style={{ marginTop: 8 }}><Money s={16}>{won(r.amount)}</Money></div>
                </div>
              </div>
            ))}
          </div>
          <div style={{ marginTop: 22 }}><GreenButton onClick={() => push({ name: "unpurchased" })}>미매입 내역 보러가기</GreenButton></div>
        </div>
      </div>
    );
  }

  const SCREENS = { main: Main, premoney: Premoney, totalsales: TotalSales, costdetail: CostDetail,
    profitdetail: ProfitDetail, unpurchased: Unpurchased, excluded: Excluded,
    card: CardScreen, txn: TxnScreen, platform: PlatformScreen, order: OrderScreen, diff: DiffScreen, deposits: DepositsScreen };

  function Logo() {
    return (
      <span style={{ fontFamily: "var(--font-sans)", fontWeight: 700, fontSize: 22, letterSpacing: "-0.01em", lineHeight: 1 }}>
        <span style={{ color: "var(--ph-ink)" }}>Pay</span><span style={{ color: "var(--ph-green-700)" }}>hug</span>
      </span>
    );
  }

  function PayhugApp() {
    const [stack, setStack] = React.useState([{ name: "main" }]);
    const cur = stack[stack.length - 1];
    const push = (s) => setStack((st) => [...st, s]);
    const pop = () => setStack((st) => (st.length > 1 ? st.slice(0, -1) : st));
    const Screen = SCREENS[cur.name] || Main;
    return (
      <div style={{ minHeight: "100vh", background: "rgb(250,249,250)", display: "flex", flexDirection: "column", fontFamily: "var(--font-sans)" }}>
        <header style={{ background: "#fff", borderBottom: "1px solid var(--border-hairline)", padding: "0 28px", height: 64, display: "flex", alignItems: "center", flex: "none" }}>
          <Logo />
        </header>
        <main style={{ flex: 1, display: "flex", justifyContent: "center", padding: "24px 16px 56px" }}>
          <div style={{ width: "100%", maxWidth: 440 }}>
            <Screen params={cur} push={push} pop={pop} />
          </div>
        </main>
      </div>
    );
  }

  window.PHPayhugApp = PayhugApp;
})();
