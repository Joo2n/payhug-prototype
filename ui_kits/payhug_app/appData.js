// PayHug app — data (수정.fig 기준). today = 2026-06-24 (수). 최종 업데이트 06/24 11:30.
// 6/25 이후 = 0원(데이터 없음). 매출/비용/수익 월별 달력 + 미매입 내역.
// Exposes window.PHAPP.
(function () {
  const store = { name: "잇잇", status: "승인완료", biz: "616-28-53422" };
  const UPDATE = "최종 업데이트 2026년 06월 24일 11:30";

  // 미리 받는 돈 (오늘 6/24, 어제 6/23 매출 기준)
  const premoney = {
    dateLabel: "26년 6월 24일 (수)", today: true, reflectedAt: UPDATE,
    total: 488086, yesterdaySales: 818800,
    cards: [
      { key: "kb",      name: "KB카드",    count: 6, amount: 102366 },
      { key: "nh",      name: "농협NH카드", count: 3, amount: 41283 },
      { key: "lotte",   name: "롯데카드",   count: 0, amount: 0 },
      { key: "bc",      name: "비씨카드",   count: 3, amount: 50193 },
      { key: "woori",   name: "우리카드",   count: 0, amount: 0 },
      { key: "hana",    name: "하나카드",   count: 1, amount: 15246 },
      { key: "shinhan", name: "신한카드",   count: 2, amount: 20691 },
      { key: "samsung", name: "삼성카드",   count: 0, amount: 0 },
      { key: "hyundai", name: "현대카드",   count: 1, amount: 24156 },
    ],
    cardsTotal: 253935,
    platforms: [
      { key: "baemin",  name: "배달의 민족", count: 11, amount: 255514 },
      { key: "coupang", name: "쿠팡이츠",   count: 8,  amount: 56628 },
      { key: "yogiyo",  name: "요기요",     count: 1,  amount: 26752 },
    ],
    platformsTotal: 338894,
    payhug: { total: -104743, expectedDiff: -104743 },
  };

  // 총 매출액 (달력 날짜 클릭 시 = 어제/특정일 매출 상세). 선정산 제외액 = 미매입 합.
  const totalSales = {
    dateLabel: "26년 6월 23일 (화)", reflectedAt: UPDATE,
    total: 818800, excludedTotal: 83641,
    cards: premoney.cards, cardsTotal: premoney.cardsTotal,
    platforms: premoney.platforms, platformsTotal: premoney.platformsTotal,
  };

  // 미매입 내역 (카드 승인 후 카드사 매입 대기). 매입완료되면 총 매출에 가산. (status: done | pending)
  const unpurchased = {
    date: "2026.06.16", total: 83641,
    note: "카드 승인 이후 아직 카드사에서 매입 처리되지 않은 내역입니다.",
    rows: [
      { date: "2026.06.14", issuer: "삼성카드", apprv: "98231264", amount: 13796, status: "done" },
      { date: "2026.06.13", issuer: "삼성카드", apprv: "60702295", amount: 22232, status: "pending" },
      { date: "2026.06.06", issuer: "하나카드", apprv: "00283649", amount: 21212, status: "pending" },
      { date: "2026.06.06", issuer: "삼성카드", apprv: "14921793", amount: 26401, status: "pending" },
    ],
  };

  // 선정산 제외액 내역 (= 이번 선정산에서 빠진 금액). 미매입 내역과는 별개 화면.
  const excludedDetail = {
    date: "2026.06.16", total: 83641,
    note: "이번 선정산에서 제외된 금액이에요.\n아직 카드 매입이 완료되지 않아 빠졌고, 매입이 확인되면 다음 선정산 금액에 자동으로 포함돼요.",
    reasons: [
      { key: "unpurchased", label: "미매입", desc: "카드 매입 대기", count: 4, amount: 83641 },
    ],
    rows: unpurchased.rows.map((r) => ({ date: r.date, issuer: r.issuer, reason: "카드 매입 대기", amount: r.amount })),
  };

  const PAY_METHOD = "신용";
  const cardExtra = { kb: { count: 1, amount: 2739 }, samsung: { count: 1, amount: 13796 } };
  function cardTxns(key) {
    const c = premoney.cards.find((x) => x.key === key);
    if (!c || c.count === 0) return { card: c, txns: [], summary: null };
    const per = Math.round(c.amount / c.count);
    const txns = [];
    let salesSum = 0, feeSum = 0;
    for (let i = 0; i < c.count; i++) {
      const net = i === c.count - 1 ? c.amount - per * (c.count - 1) : per;
      const sales = Math.round(net / 0.99);
      const fee = -(sales - net);
      salesSum += sales; feeSum += fee;
      txns.push({ apprv: String(20000000 + ((i + 3) * 1300457) % 79999999), time: `1${i}:0${i}`,
        sales, fee, net, payType: i % 2 === 0 ? "신용" : "체크" });
    }
    const add = cardExtra[key] || null;
    const summary = { yesterdaySales: salesSum, fee: feeSum, premoney: c.amount, addPurchase: add };
    return { card: c, txns, summary };
  }

  const platformDetail = {
    baemin: {
      name: "배달의 민족", yesterdaySales: 397300, deductTotal: -141786,
      deducts: [["배달의 민족 차감액", -110698], ["광고비", -31088, "help"], ["페이허그 수수료", "면제"]],
      excluded: { count: 1, amount: 2889 }, premoney: 255514,
      orders: [
        { shop: "잇잇", date: "2026.06.23", time: "13:47", amount: 13443, pay: "바로결제" },
        { shop: "국밥보스 제육대장 시청점", date: "2026.06.23", time: "13:23", amount: 8156, pay: "바로결제" },
        { shop: "국밥보스 제육대장 시청점", date: "2026.06.23", time: "11:31", amount: -898, pay: "만나서 결제" },
        { shop: "Boss 짬뽕 직화제육 시청점", date: "2026.06.23", time: "11:12", amount: 7274, pay: "바로결제" },
        { shop: "Boss 짬뽕 직화제육 시청점", date: "2026.06.23", time: "10:31", amount: 7714, pay: "바로결제" },
        { shop: "Boss 짬뽕 직화제육 시청점", date: "2026.06.23", time: "10:24", amount: 7852, pay: "바로결제" },
      ],
    },
    coupang: { name: "쿠팡이츠", yesterdaySales: 61200, deductTotal: -4572,
      deducts: [["쿠팡이츠 차감액", -4572], ["페이허그 수수료", "면제"]], excluded: null, premoney: 56628, orders: [] },
    yogiyo: { name: "요기요", yesterdaySales: 28900, deductTotal: -2148,
      deducts: [["요기요 차감액", -2148], ["페이허그 수수료", "면제"]], excluded: null, premoney: 26752, orders: [] },
  };

  const orderDetail = {
    name: "배달의 민족", date: "2026.06.23", time: "11:31", amount: -898, orderNo: "B2DR004ZYJ",
    pay: "만나서 결제", yesterdaySales: "(14,900원)", deductTotal: -898,
    deducts: [["배달의 민족 차감액", -898], ["페이허그 수수료", "면제"]], premoney: -898,
    note: "[만나서 결제]는 배달의 민족 선정산 대상이 아니며 매출액에서 제외돼요\n[배민원 주문]의 매출액은 고객의 배달팁이 제외된 금액이에요",
  };

  const expectedDiff = {
    dateLabel: "2026.06.24 반영", total: -104743,
    note: "선정산은 예상 카드 수수료율을 기준으로 지급돼요.\n실제 정산 후 발생한 차액은 다음 선정산 금액에 자동으로 반영돼요.",
    rows: [
      { date: "2026.06.22", issuer: "비씨카드",   no: "승인번호 71864578", amount: 52 },
      { date: "2026.06.22", issuer: "비씨카드",   no: "승인번호 75903426", amount: 85 },
      { date: "2026.06.22", issuer: "하나카드",   no: "승인번호 21804005", amount: 10 },
      { date: "2026.06.22", issuer: "하나카드",   no: "승인번호 27800203", amount: 28 },
      { date: "2026.06.22", issuer: "배달의 민족", no: "주문번호 T2DQ00008CVO", amount: -5100 },
      { date: "2026.06.22", issuer: "배달의 민족", no: "주문번호 T2DQ0000B20S", amount: -5617 },
      { date: "2026.06.20", issuer: "배달의 민족", no: "주문번호 B2DQ004BI9", amount: 2138 },
    ],
  };

  const deposits = {
    bank: "하나은행", account: "62291002003804",
    rows: [
      { date: "6.24", time: "11:30", amount: 488086, kind: "premoney" },
      { date: "6.23", time: "11:30", amount: 766796, kind: "premoney" },
      { date: "",     time: "14:30", amount: 83641,  kind: "excluded" },
      { date: "6.22", time: "11:30", amount: 460958, kind: "premoney" },
      { date: "6.21", time: "11:30", amount: 533110, kind: "premoney" },
      { date: "6.20", time: "11:30", amount: 587,    kind: "premoney" },
      { date: "6.19", time: "11:30", amount: 771333, kind: "premoney" },
    ],
  };

  const calDays = {};
  for (let d = 1; d <= 24; d++) {
    const k = (d * 2654435761) >>> 0;
    const f = (n) => (((k >>> n) & 0x3ff) / 0x3ff);
    let cardSales = 90000 + Math.round((f(2) * 130000) / 100) * 100;
    let delivSales = d % 6 === 0 ? Math.round((40000 + f(7) * 55000) / 100) * 100
                                 : 70000 + Math.round((f(11) * 160000) / 100) * 100;
    if (d === 23) { cardSales = 480000; delivSales = 338800; }
    const cardFee = Math.round(cardSales * 0.011 / 10) * 10;
    const delivFee = delivSales ? Math.round(delivSales * 0.12 / 10) * 10 : 0;
    const adFee = delivSales ? Math.round(delivSales * 0.05 / 10) * 10 : 0;
    calDays[d] = { cardSales, delivSales, cardFee, delivFee, adFee };
  }
  const sum = (sel) => Object.values(calDays).reduce((a, x) => a + sel(x), 0);

  function dayMetrics(x) {
    if (!x) return null;
    const cardCost = x.cardFee;
    const delivCost = x.delivFee + x.adFee;
    const cardProfit = x.cardSales - cardCost;
    const delivProfit = x.delivSales - delivCost;
    return {
      cardSales: x.cardSales, delivSales: x.delivSales, sales: x.cardSales + x.delivSales,
      cardFee: x.cardFee, delivFee: x.delivFee, adFee: x.adFee,
      cardCost, delivCost, cost: cardCost + delivCost,
      cardProfit, delivProfit, profit: cardProfit + delivProfit,
    };
  }

  const monthly = {
    cardSales: sum((x) => x.cardSales), delivSales: sum((x) => x.delivSales),
    cardFee: sum((x) => x.cardFee), delivFee: sum((x) => x.delivFee), adFee: sum((x) => x.adFee),
  };
  monthly.sales = monthly.cardSales + monthly.delivSales;
  monthly.cardCost = monthly.cardFee;
  monthly.delivCost = monthly.delivFee + monthly.adFee;
  monthly.cost = monthly.cardCost + monthly.delivCost;
  monthly.cardProfit = monthly.cardSales - monthly.cardCost;
  monthly.delivProfit = monthly.delivSales - monthly.delivCost;
  monthly.profit = monthly.cardProfit + monthly.delivProfit;

  const salesCalendar = { year: 2026, month: 6, today: 24, label: "2026년 6월", days: calDays, monthly };

  window.PHAPP = { store, premoney, totalSales, unpurchased, excludedDetail, platformDetail, orderDetail,
    cardTxns, PAY_METHOD, expectedDiff, deposits, salesCalendar, dayMetrics, UPDATE };
})();
