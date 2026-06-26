/* @ds-bundle: {"format":3,"namespace":"PayHugDesignSystem_81d4f2","components":[{"name":"Avatar","sourcePath":"components/core/Avatar.jsx"},{"name":"Badge","sourcePath":"components/core/Badge.jsx"},{"name":"Button","sourcePath":"components/core/Button.jsx"},{"name":"Card","sourcePath":"components/core/Card.jsx"},{"name":"StatTile","sourcePath":"components/core/StatTile.jsx"},{"name":"SalesBreakdown","sourcePath":"components/data/SalesBreakdown.jsx"},{"name":"SalesCalendar","sourcePath":"components/data/SalesCalendar.jsx"},{"name":"AlertBanner","sourcePath":"components/feedback/AlertBanner.jsx"},{"name":"Checkbox","sourcePath":"components/forms/Checkbox.jsx"},{"name":"Input","sourcePath":"components/forms/Input.jsx"},{"name":"Select","sourcePath":"components/forms/Select.jsx"},{"name":"SegmentedTabs","sourcePath":"components/navigation/SegmentedTabs.jsx"},{"name":"SidebarNav","sourcePath":"components/navigation/SidebarNav.jsx"},{"name":"Tabs","sourcePath":"components/navigation/Tabs.jsx"}],"sourceHashes":{"components/core/Avatar.jsx":"56f7f2fd75b0","components/core/Badge.jsx":"79739a2f900c","components/core/Button.jsx":"a65a7314f18c","components/core/Card.jsx":"46e615a976ff","components/core/StatTile.jsx":"a4b99374955e","components/data/SalesBreakdown.jsx":"dcbe39c2e736","components/data/SalesCalendar.jsx":"e8c73007c41f","components/feedback/AlertBanner.jsx":"df7facc78fa3","components/forms/Checkbox.jsx":"469201f909c7","components/forms/Input.jsx":"e4b605f1ec10","components/forms/Select.jsx":"44eecd9d29ea","components/navigation/SegmentedTabs.jsx":"4a7202aa6a1d","components/navigation/SidebarNav.jsx":"45d67984a2b1","components/navigation/Tabs.jsx":"89594fd92134","ui_kits/admin_settlement/AdminApp.jsx":"cd8193760739","ui_kits/admin_settlement/data.js":"8f6fb4092aa3","ui_kits/payhug_app/PayhugApp.jsx":"2545ca4ab2eb","ui_kits/payhug_app/appData.js":"b46e897fb00e"},"inlinedExternals":[],"unexposedExports":[]} */

(() => {

const __ds_ns = (window.PayHugDesignSystem_81d4f2 = window.PayHugDesignSystem_81d4f2 || {});

const __ds_scope = {};

(__ds_ns.__errors = __ds_ns.__errors || []);

// components/core/Avatar.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * PayHug Avatar — circular user/merchant mark. Renders an image when `src`
 * is given, else initials on a soft brand fill.
 */
function Avatar({
  src = null,
  name = "",
  size = 40,
  tone = "green",
  // "green" | "navy" | "blue" | "neutral"
  square = false,
  style = {},
  ...rest
}) {
  const tones = {
    green: {
      bg: "var(--ph-green-tint)",
      fg: "var(--ph-green-700)"
    },
    navy: {
      bg: "#E9EDF7",
      fg: "var(--ph-navy)"
    },
    blue: {
      bg: "var(--ph-blue-tint)",
      fg: "var(--ph-blue-600)"
    },
    neutral: {
      bg: "var(--ph-gray-100)",
      fg: "var(--ph-gray-700)"
    }
  };
  const t = tones[tone] || tones.green;
  const initials = (name || "").trim().slice(0, 2).toUpperCase();
  return /*#__PURE__*/React.createElement("div", _extends({
    style: {
      width: size,
      height: size,
      borderRadius: square ? "var(--r-lg)" : "50%",
      background: src ? "#fff" : t.bg,
      color: t.fg,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      overflow: "hidden",
      flex: "none",
      fontFamily: "var(--font-sans)",
      fontWeight: 700,
      fontSize: Math.round(size * 0.38),
      ...style
    }
  }, rest), src ? /*#__PURE__*/React.createElement("img", {
    src: src,
    alt: name,
    style: {
      width: "100%",
      height: "100%",
      objectFit: "cover"
    }
  }) : initials);
}
Object.assign(__ds_scope, { Avatar });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Avatar.jsx", error: String((e && e.message) || e) }); }

// components/core/Badge.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * PayHug Badge / status pill.
 * Used for payment channels (카드 / 배달 / 쿠팡이츠) and settlement
 * states (매입완료 / 이체완료 / 예정일 경과 …). Default style is `soft`
 * (tinted fill + colored text), matching the admin tables.
 */
const TONES = {
  blue: {
    fg: "var(--ph-blue-600)",
    bg: "var(--ph-blue-tint)",
    solidBg: "var(--ph-blue-600)"
  },
  card: {
    fg: "var(--ph-blue-600)",
    bg: "var(--ph-blue-tint)",
    solidBg: "var(--ph-blue-600)"
  },
  success: {
    fg: "var(--ph-success-600)",
    bg: "var(--ph-mint-tint)",
    solidBg: "var(--ph-mint)"
  },
  mint: {
    fg: "var(--ph-success-600)",
    bg: "var(--ph-mint-tint)",
    solidBg: "var(--ph-mint)"
  },
  green: {
    fg: "var(--ph-green-700)",
    bg: "var(--ph-green-tint)",
    solidBg: "var(--ph-green)"
  },
  danger: {
    fg: "var(--ph-danger-600)",
    bg: "var(--ph-danger-tint)",
    solidBg: "var(--ph-danger)"
  },
  warning: {
    fg: "var(--ph-warning-700)",
    bg: "var(--ph-warning-tint)",
    solidBg: "var(--ph-warning)"
  },
  amber: {
    fg: "#8A6D00",
    bg: "var(--ph-amber-tint)",
    solidBg: "var(--ph-amber)"
  },
  navy: {
    fg: "var(--ph-navy)",
    bg: "#E9EDF7",
    solidBg: "var(--ph-navy)"
  },
  neutral: {
    fg: "var(--ph-gray-700)",
    bg: "var(--ph-gray-100)",
    solidBg: "var(--ph-gray-500)"
  }
};
const SIZES = {
  sm: {
    fontSize: 11,
    padding: "2px 7px",
    radius: "var(--r-sm)",
    dot: 5
  },
  md: {
    fontSize: 13,
    padding: "4px 10px",
    radius: "var(--r-sm)",
    dot: 6
  }
};
function Badge({
  children,
  tone = "neutral",
  variant = "soft",
  // "soft" | "solid" | "outline"
  size = "md",
  dot = false,
  style = {},
  ...rest
}) {
  const t = TONES[tone] || TONES.neutral;
  const s = SIZES[size] || SIZES.md;
  let css;
  if (variant === "solid") {
    css = {
      background: t.solidBg,
      color: tone === "green" || tone === "amber" ? "var(--ph-forest)" : "#fff",
      border: "none"
    };
  } else if (variant === "outline") {
    css = {
      background: "transparent",
      color: t.fg,
      border: `1px solid ${t.fg}`
    };
  } else {
    css = {
      background: t.bg,
      color: t.fg,
      border: "none"
    };
  }
  return /*#__PURE__*/React.createElement("span", _extends({
    style: {
      display: "inline-flex",
      alignItems: "center",
      gap: 5,
      fontFamily: "var(--font-sans)",
      fontSize: s.fontSize,
      fontWeight: 700,
      lineHeight: 1.3,
      padding: s.padding,
      borderRadius: s.radius,
      whiteSpace: "nowrap",
      ...css,
      ...style
    }
  }, rest), dot && /*#__PURE__*/React.createElement("span", {
    style: {
      width: s.dot,
      height: s.dot,
      borderRadius: "50%",
      background: "currentColor",
      flex: "none"
    }
  }), children);
}
Object.assign(__ds_scope, { Badge });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Badge.jsx", error: String((e && e.message) || e) }); }

// components/core/Button.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * PayHug Button.
 * Brand-primary = bright green (forest text). UI-primary action = blue.
 */
const SIZES = {
  sm: {
    height: 32,
    padding: "0 12px",
    fontSize: 13,
    radius: "var(--r-md)",
    gap: 6
  },
  md: {
    height: 42,
    padding: "0 18px",
    fontSize: 15,
    radius: "var(--r-lg)",
    gap: 8
  },
  lg: {
    height: 50,
    padding: "0 24px",
    fontSize: 16,
    radius: "var(--r-lg)",
    gap: 8
  }
};
const VARIANTS = {
  primary: {
    background: "var(--ph-green)",
    color: "var(--ph-forest)",
    border: "none",
    hover: "var(--ph-green-600)"
  },
  action: {
    background: "var(--ph-blue-600)",
    color: "#fff",
    border: "none",
    hover: "var(--ph-blue-700)"
  },
  forest: {
    background: "var(--ph-forest)",
    color: "#fff",
    border: "none",
    hover: "var(--ph-forest-700)"
  },
  secondary: {
    background: "#fff",
    color: "var(--ph-ink)",
    border: "1px solid var(--border-strong)",
    hover: "var(--ph-gray-50)"
  },
  ghost: {
    background: "transparent",
    color: "var(--ph-gray-700)",
    border: "1px solid transparent",
    hover: "var(--ph-gray-100)"
  },
  danger: {
    background: "var(--ph-danger)",
    color: "#fff",
    border: "none",
    hover: "var(--ph-danger-600)"
  }
};
function Button({
  children,
  variant = "primary",
  size = "md",
  disabled = false,
  block = false,
  iconLeft = null,
  iconRight = null,
  style = {},
  ...rest
}) {
  const s = SIZES[size] || SIZES.md;
  const v = VARIANTS[variant] || VARIANTS.primary;
  const [hover, setHover] = React.useState(false);
  return /*#__PURE__*/React.createElement("button", _extends({
    type: "button",
    disabled: disabled,
    onMouseEnter: () => setHover(true),
    onMouseLeave: () => setHover(false),
    style: {
      display: block ? "flex" : "inline-flex",
      width: block ? "100%" : "auto",
      alignItems: "center",
      justifyContent: "center",
      gap: s.gap,
      height: s.height,
      padding: s.padding,
      fontFamily: "var(--font-sans)",
      fontSize: s.fontSize,
      fontWeight: 700,
      lineHeight: 1,
      whiteSpace: "nowrap",
      borderRadius: s.radius,
      background: disabled ? "var(--ph-gray-100)" : hover ? v.hover : v.background,
      color: disabled ? "var(--ph-gray-400)" : v.color,
      border: disabled ? "1px solid var(--ph-gray-200)" : v.border,
      cursor: disabled ? "not-allowed" : "pointer",
      transition: "background var(--dur) var(--ease), transform var(--dur-fast) var(--ease)",
      transform: hover && !disabled ? "translateY(-1px)" : "none",
      boxSizing: "border-box",
      ...style
    }
  }, rest), iconLeft, children, iconRight);
}
Object.assign(__ds_scope, { Button });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Button.jsx", error: String((e && e.message) || e) }); }

// components/core/Card.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * PayHug Card — the base white surface. Soft low shadow, 16px radius.
 * Use `tone` for the tinted summary cards (수수료 / 내 수익 / 입금액).
 */
const TONES = {
  default: {
    background: "#fff",
    border: "1px solid var(--border-default)"
  },
  plain: {
    background: "#fff",
    border: "none"
  },
  danger: {
    background: "var(--ph-danger-tint)",
    border: "none"
  },
  success: {
    background: "var(--ph-success-tint)",
    border: "none"
  },
  warning: {
    background: "var(--ph-warning-tint)",
    border: "none"
  },
  blue: {
    background: "var(--ph-blue-tint)",
    border: "none"
  },
  green: {
    background: "var(--ph-green-tint)",
    border: "none"
  }
};
function Card({
  children,
  tone = "default",
  pad = 20,
  radius = "var(--r-xl)",
  shadow = true,
  style = {},
  ...rest
}) {
  const t = TONES[tone] || TONES.default;
  return /*#__PURE__*/React.createElement("div", _extends({
    style: {
      background: t.background,
      border: t.border,
      borderRadius: radius,
      padding: pad,
      boxShadow: shadow && tone === "default" ? "var(--sh-card)" : "none",
      boxSizing: "border-box",
      ...style
    }
  }, rest), children);
}
Object.assign(__ds_scope, { Card });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Card.jsx", error: String((e && e.message) || e) }); }

// components/core/StatTile.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * PayHug StatTile — label + big numeric value, used in the dashboard /
 * settlement summary headers (총 매출 · 수수료 · 내 수익 …).
 * Value renders in Inter tabular figures.
 */
const VALUE_COLORS = {
  default: "var(--ph-ink)",
  pos: "var(--ph-success)",
  neg: "var(--ph-danger)",
  blue: "var(--ph-blue-600)",
  warning: "var(--ph-warning-700)"
};
function StatTile({
  label,
  value,
  unit = "",
  sub = null,
  tone = "default",
  align = "left",
  size = "lg",
  // "md" | "lg"
  style = {},
  ...rest
}) {
  const valueSize = size === "lg" ? 30 : 22;
  return /*#__PURE__*/React.createElement("div", _extends({
    style: {
      display: "flex",
      flexDirection: "column",
      gap: 6,
      alignItems: align === "right" ? "flex-end" : "flex-start",
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: 14,
      fontWeight: 500,
      color: "var(--text-secondary)"
    }
  }, label), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "baseline",
      gap: 4
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "ph-num",
    style: {
      fontFamily: "var(--font-num)",
      fontSize: valueSize,
      fontWeight: 700,
      letterSpacing: "-0.01em",
      lineHeight: 1.1,
      color: VALUE_COLORS[tone] || VALUE_COLORS.default,
      fontVariantNumeric: "tabular-nums lining-nums"
    }
  }, value), unit && /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: 15,
      fontWeight: 500,
      color: "var(--text-secondary)"
    }
  }, unit)), sub != null && /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: 12.5,
      fontWeight: 500,
      color: "var(--text-muted)"
    }
  }, sub));
}
Object.assign(__ds_scope, { StatTile });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/StatTile.jsx", error: String((e && e.message) || e) }); }

// components/data/SalesBreakdown.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * PayHug SalesBreakdown — the sectioned per-issuer money list shared by the
 * "미리 받은 돈" and "매출 내역" detail screens. Each section (카드 / 배달앱 /
 * 페이허그·선정산 제외) has a bold header row + per-issuer rows; rows may carry a
 * blue/gray sub-row (선정산 제외액) and be clickable to a per-issuer detail.
 * Auto-layout: pure flex column, no fixed heights.
 */
const won = n => typeof n === "number" ? n.toLocaleString("ko-KR") + "원" : n;
function Amount({
  children,
  color = "var(--text-primary)",
  size = 16,
  weight = 700
}) {
  return /*#__PURE__*/React.createElement("span", {
    className: "ph-num",
    style: {
      fontFamily: "var(--font-num)",
      fontVariantNumeric: "tabular-nums lining-nums",
      fontSize: size,
      fontWeight: weight,
      color,
      whiteSpace: "nowrap",
      flex: "none"
    }
  }, children);
}
function Row({
  row,
  onClick
}) {
  const [hover, setHover] = React.useState(false);
  const clickable = !!onClick;
  const zero = row.zero || row.amount === 0 || row.amount === "0원";
  return /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    onClick: onClick,
    onMouseEnter: () => setHover(true),
    onMouseLeave: () => setHover(false),
    style: {
      display: "flex",
      alignItems: "center",
      gap: 8,
      padding: "11px 8px",
      borderRadius: "var(--r-md)",
      cursor: clickable ? "pointer" : "default",
      background: clickable && hover ? "var(--ph-gray-50)" : "transparent",
      transition: "background var(--dur-fast) var(--ease)"
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 16,
      fontWeight: 500,
      color: zero ? "var(--text-muted)" : "var(--text-primary)"
    }
  }, row.issuer), row.count != null && /*#__PURE__*/React.createElement("span", {
    className: "ph-num",
    style: {
      fontSize: 13,
      color: "var(--text-muted)",
      fontFamily: "var(--font-num)"
    }
  }, row.count), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1
    }
  }), /*#__PURE__*/React.createElement(Amount, {
    color: zero ? "var(--text-muted)" : "var(--text-primary)",
    weight: zero ? 500 : 700
  }, won(row.amount)), clickable && /*#__PURE__*/React.createElement("svg", {
    width: "18",
    height: "18",
    viewBox: "0 0 24 24",
    fill: "none",
    style: {
      color: "var(--ph-gray-400)"
    }
  }, /*#__PURE__*/React.createElement("path", {
    d: "M9 6l6 6-6 6",
    stroke: "currentColor",
    strokeWidth: "1.8",
    strokeLinecap: "round",
    strokeLinejoin: "round"
  }))), row.sub && /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: 8,
      padding: "2px 8px 9px 22px"
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 14.5,
      fontWeight: 500,
      color: row.sub.tone === "blue" ? "var(--ph-blue-600)" : "var(--text-secondary)"
    }
  }, "\u3134 ", row.sub.label), row.sub.count != null && /*#__PURE__*/React.createElement("span", {
    className: "ph-num",
    style: {
      fontSize: 13,
      color: row.sub.tone === "blue" ? "var(--ph-blue)" : "var(--text-muted)",
      fontFamily: "var(--font-num)"
    }
  }, row.sub.count), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1
    }
  }), /*#__PURE__*/React.createElement(Amount, {
    color: row.sub.tone === "blue" ? "var(--ph-blue-600)" : "var(--text-secondary)",
    size: 15
  }, won(row.sub.amount))));
}
function SalesBreakdown({
  sections = [],
  footer = null,
  onRowClick,
  onFooterClick,
  style = {},
  ...rest
}) {
  return /*#__PURE__*/React.createElement("div", _extends({
    style: {
      display: "flex",
      flexDirection: "column",
      fontFamily: "var(--font-sans)",
      ...style
    }
  }, rest), sections.map((sec, si) => /*#__PURE__*/React.createElement("div", {
    key: si,
    style: {
      borderTop: si > 0 ? "1px solid var(--border-hairline)" : "none",
      paddingTop: si > 0 ? 12 : 0,
      marginTop: si > 0 ? 8 : 0
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: 8,
      padding: "6px 8px 10px"
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 18,
      fontWeight: 700,
      color: "var(--text-primary)"
    }
  }, sec.label), sec.count != null && /*#__PURE__*/React.createElement("span", {
    className: "ph-num",
    style: {
      fontSize: 13,
      color: "var(--text-muted)",
      fontFamily: "var(--font-num)"
    }
  }, sec.count), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1
    }
  }), /*#__PURE__*/React.createElement(Amount, {
    size: 18
  }, won(sec.amount))), sec.rows.map((r, ri) => /*#__PURE__*/React.createElement(Row, {
    key: ri,
    row: r,
    onClick: onRowClick && r.key ? () => onRowClick(r.key, sec) : null
  })))), footer && /*#__PURE__*/React.createElement("div", {
    style: {
      borderTop: "1px solid var(--border-default)",
      paddingTop: 12,
      marginTop: 8
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      padding: "6px 8px 8px"
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 18,
      fontWeight: 700,
      color: "var(--text-primary)"
    }
  }, footer.label), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1
    }
  }), /*#__PURE__*/React.createElement(Amount, {
    size: 18,
    color: typeof footer.amount === "number" && footer.amount < 0 ? "var(--text-money-neg)" : "var(--text-primary)"
  }, won(footer.amount))), (footer.rows || []).map((r, ri) => /*#__PURE__*/React.createElement("div", {
    key: ri,
    onClick: r.link && onFooterClick ? () => onFooterClick(ri) : null,
    style: {
      display: "flex",
      alignItems: "center",
      gap: 6,
      padding: "9px 8px",
      cursor: r.link && onFooterClick ? "pointer" : "default"
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 15,
      color: "var(--text-secondary)"
    }
  }, r.label), r.help && /*#__PURE__*/React.createElement("span", {
    style: {
      width: 16,
      height: 16,
      borderRadius: "50%",
      border: "1px solid var(--ph-gray-300)",
      color: "var(--ph-gray-400)",
      fontSize: 11,
      display: "inline-flex",
      alignItems: "center",
      justifyContent: "center"
    }
  }, "?"), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1
    }
  }), /*#__PURE__*/React.createElement(Amount, {
    size: 15,
    weight: r.link ? 700 : 500,
    color: r.link ? "var(--ph-blue-600)" : "var(--text-secondary)"
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      textDecoration: r.link ? "underline" : "none"
    }
  }, won(r.amount)))))));
}
Object.assign(__ds_scope, { SalesBreakdown });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/data/SalesBreakdown.jsx", error: String((e && e.message) || e) }); }

// components/data/SalesCalendar.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * PayHug SalesCalendar — the mobile app's monthly sales calendar.
 * Each in-month day shows two sales figures: 카드 (amber) and 배달앱 (green).
 * The selected day gets a bright-green circle. Sundays are red, Saturdays blue.
 * Self-contained defaults render January 2026 (the source design).
 */
const DOW = ["일", "월", "화", "수", "목", "금", "토"];
const DEMO_DAYS = {
  1: {
    card: 162300,
    delivery: 118500
  },
  2: {
    card: 148700
  },
  3: {
    card: 171200,
    delivery: 96300
  },
  4: {
    card: 139500,
    delivery: 124700
  },
  5: {
    card: 158900
  },
  6: {
    card: 144800,
    delivery: 87600
  },
  7: {
    card: 176400,
    delivery: 132400
  },
  8: {
    card: 151600,
    delivery: 109800
  },
  9: {
    card: 133200,
    delivery: 103200
  },
  10: {
    card: 168500,
    delivery: 121500
  },
  11: {
    card: 142300,
    delivery: 94700
  },
  12: {
    card: 159700,
    delivery: 115300
  },
  13: {
    card: 147900,
    delivery: 98900
  },
  14: {
    card: 143500,
    delivery: 114500
  }
};
const fmt = n => n == null ? null : n.toLocaleString("ko-KR");
function SalesCalendar({
  year = 2026,
  month = 1,
  // 1-indexed
  monthLabel = "월 매출",
  total = "3,465,900원",
  legend = [{
    label: "카드",
    count: "21건",
    amount: "2,148,500원",
    color: "var(--ch-card)"
  }, {
    label: "배달앱",
    count: "47건",
    amount: "1,317,400원",
    color: "var(--ch-delivery)"
  }],
  days = DEMO_DAYS,
  selected = 15,
  onSelectDay,
  style = {},
  ...rest
}) {
  const startDow = new Date(year, month - 1, 1).getDay();
  const daysInMonth = new Date(year, month, 0).getDate();
  const prevDays = new Date(year, month - 1, 0).getDate();
  const cells = [];
  for (let i = 0; i < 42; i++) {
    const dn = i - startDow + 1;
    if (dn < 1) cells.push({
      d: prevDays + dn,
      out: true
    });else if (dn > daysInMonth) cells.push({
      d: dn - daysInMonth,
      out: true
    });else cells.push({
      d: dn,
      out: false
    });
  }
  const rows = cells.slice(35).every(c => c.out) ? 5 : 6;
  return /*#__PURE__*/React.createElement("div", _extends({
    style: {
      background: "#fff",
      borderRadius: 20,
      boxShadow: "0 1px 20px rgba(0,0,0,0.12)",
      padding: "24px 22px",
      fontFamily: "var(--font-sans)",
      boxSizing: "border-box",
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      marginBottom: 16
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 22,
      fontWeight: 700,
      color: "var(--text-primary)"
    }
  }, monthLabel), /*#__PURE__*/React.createElement("span", {
    className: "ph-num",
    style: {
      fontFamily: "var(--font-num)",
      fontSize: 22,
      fontWeight: 700,
      color: "var(--text-primary)",
      fontVariantNumeric: "tabular-nums"
    }
  }, total)), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: 8,
      marginBottom: 18
    }
  }, legend.map((lg, i) => /*#__PURE__*/React.createElement("div", {
    key: i,
    style: {
      display: "flex",
      alignItems: "center",
      gap: 14
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      width: 14,
      height: 14,
      borderRadius: "50%",
      background: lg.color,
      flex: "none"
    }
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 16,
      color: "var(--text-secondary)",
      minWidth: 56
    }
  }, lg.label), /*#__PURE__*/React.createElement("span", {
    className: "ph-num",
    style: {
      fontSize: 15,
      color: "var(--text-muted)",
      fontFamily: "var(--font-num)"
    }
  }, lg.count), /*#__PURE__*/React.createElement("span", {
    className: "ph-num",
    style: {
      marginLeft: "auto",
      fontSize: 16,
      fontWeight: 700,
      color: "var(--text-primary)",
      fontFamily: "var(--font-num)",
      fontVariantNumeric: "tabular-nums"
    }
  }, lg.amount)))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "repeat(7,1fr)",
      borderTop: "1px solid var(--border-hairline)"
    }
  }, DOW.map((d, i) => /*#__PURE__*/React.createElement("div", {
    key: d,
    style: {
      textAlign: "center",
      padding: "12px 0",
      fontSize: 15,
      fontWeight: 700,
      color: i === 0 ? "var(--ph-danger)" : i === 6 ? "var(--ph-blue)" : "var(--text-primary)"
    }
  }, d))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "repeat(7,1fr)"
    }
  }, cells.slice(0, rows * 7).map((c, i) => {
    const dow = i % 7;
    const data = !c.out ? days[c.d] : null;
    const isSel = !c.out && c.d === selected;
    const numColor = c.out ? "var(--ph-gray-300)" : isSel ? "var(--ph-forest)" : dow === 0 ? "var(--ph-danger)" : dow === 6 ? "var(--ph-blue)" : "var(--text-primary)";
    return /*#__PURE__*/React.createElement("div", {
      key: i,
      onClick: () => !c.out && onSelectDay && onSelectDay(c.d),
      style: {
        borderTop: "1px solid var(--border-hairline)",
        minHeight: 82,
        padding: "10px 4px 8px",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 4,
        cursor: c.out ? "default" : "pointer"
      }
    }, /*#__PURE__*/React.createElement("span", {
      className: "ph-num",
      style: {
        fontFamily: "var(--font-num)",
        fontSize: 17,
        fontWeight: isSel ? 700 : 500,
        color: numColor,
        width: 30,
        height: 30,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        borderRadius: "50%",
        background: isSel ? "var(--ph-green)" : "transparent"
      }
    }, c.d), data && /*#__PURE__*/React.createElement("div", {
      style: {
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 1
      }
    }, data.card != null && /*#__PURE__*/React.createElement("span", {
      className: "ph-num",
      style: {
        fontSize: 12.5,
        fontWeight: 600,
        color: "var(--ch-card)",
        fontFamily: "var(--font-num)"
      }
    }, fmt(data.card)), data.delivery != null && /*#__PURE__*/React.createElement("span", {
      className: "ph-num",
      style: {
        fontSize: 12.5,
        fontWeight: 600,
        color: "var(--ch-delivery)",
        fontFamily: "var(--font-num)"
      }
    }, fmt(data.delivery))));
  })));
}
Object.assign(__ds_scope, { SalesCalendar });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/data/SalesCalendar.jsx", error: String((e && e.message) || e) }); }

// components/feedback/AlertBanner.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * PayHug AlertBanner — the framed notice used in admin (e.g. 미정산 누락 추적).
 * Colored border + soft tinted fill, a leading icon, title, optional trailing
 * content (amount/chip) and collapsible body.
 */
const TONES = {
  danger: {
    border: "var(--ph-danger)",
    fill: "var(--ph-danger-tint)",
    fg: "var(--ph-danger-600)"
  },
  warning: {
    border: "var(--ph-warning)",
    fill: "var(--ph-warning-tint)",
    fg: "var(--ph-warning-700)"
  },
  info: {
    border: "var(--ph-blue)",
    fill: "var(--ph-blue-tint)",
    fg: "var(--ph-blue-700)"
  },
  success: {
    border: "var(--ph-mint)",
    fill: "var(--ph-mint-tint)",
    fg: "var(--ph-success-600)"
  }
};
const ICONS = {
  danger: "M12 3l9 16H3zM12 10v4M12 16.5v.5",
  warning: "M12 3l9 16H3zM12 10v4M12 16.5v.5",
  info: "M12 8h.01M11 12h1v5h1",
  success: "M5 12l4 4 10-10"
};
function AlertBanner({
  tone = "danger",
  title,
  trailing = null,
  children = null,
  collapsible = false,
  defaultOpen = true,
  style = {},
  ...rest
}) {
  const t = TONES[tone] || TONES.danger;
  const [open, setOpen] = React.useState(defaultOpen);
  return /*#__PURE__*/React.createElement("div", _extends({
    style: {
      border: `1.5px solid ${t.border}`,
      background: t.fill,
      borderRadius: "var(--r-xl)",
      padding: "14px 18px",
      fontFamily: "var(--font-sans)",
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement("div", {
    onClick: () => collapsible && setOpen(o => !o),
    style: {
      display: "flex",
      alignItems: "center",
      gap: 12,
      cursor: collapsible ? "pointer" : "default"
    }
  }, /*#__PURE__*/React.createElement("svg", {
    width: "22",
    height: "22",
    viewBox: "0 0 24 24",
    fill: "none",
    style: {
      flex: "none"
    }
  }, /*#__PURE__*/React.createElement("path", {
    d: ICONS[tone],
    stroke: t.fg,
    strokeWidth: "1.8",
    strokeLinecap: "round",
    strokeLinejoin: "round"
  })), /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 17,
      fontWeight: 700,
      color: t.fg
    }
  }, title), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1
    }
  }), trailing, collapsible && /*#__PURE__*/React.createElement("svg", {
    width: "20",
    height: "20",
    viewBox: "0 0 24 24",
    fill: "none",
    style: {
      transition: "transform var(--dur) var(--ease)",
      transform: open ? "rotate(180deg)" : "none"
    }
  }, /*#__PURE__*/React.createElement("path", {
    d: "M6 9l6 6 6-6",
    stroke: t.fg,
    strokeWidth: "1.8",
    strokeLinecap: "round",
    strokeLinejoin: "round"
  }))), children && open && /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 10,
      fontSize: 14,
      lineHeight: 1.6,
      color: t.fg,
      opacity: 0.92
    }
  }, children));
}
Object.assign(__ds_scope, { AlertBanner });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/feedback/AlertBanner.jsx", error: String((e && e.message) || e) }); }

// components/forms/Checkbox.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * PayHug Checkbox — used for bulk-select rows in the admin settlement tables.
 * Checked fill = blue action color.
 */
function Checkbox({
  checked = false,
  onChange,
  label = null,
  disabled = false,
  size = 18,
  style = {},
  ...rest
}) {
  return /*#__PURE__*/React.createElement("label", _extends({
    style: {
      display: "inline-flex",
      alignItems: "center",
      gap: 8,
      cursor: disabled ? "not-allowed" : "pointer",
      fontFamily: "var(--font-sans)",
      userSelect: "none",
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement("span", {
    onClick: () => !disabled && onChange && onChange(!checked),
    style: {
      width: size,
      height: size,
      borderRadius: 5,
      flex: "none",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      background: checked ? "var(--ph-blue-600)" : "#fff",
      border: `1.5px solid ${checked ? "var(--ph-blue-600)" : "var(--border-strong)"}`,
      transition: "background var(--dur-fast) var(--ease), border-color var(--dur-fast) var(--ease)",
      opacity: disabled ? 0.5 : 1
    }
  }, checked && /*#__PURE__*/React.createElement("svg", {
    width: size * 0.62,
    height: size * 0.62,
    viewBox: "0 0 16 16",
    fill: "none"
  }, /*#__PURE__*/React.createElement("path", {
    d: "M3 8.5l3.2 3.2L13 5",
    stroke: "#fff",
    strokeWidth: "2.2",
    strokeLinecap: "round",
    strokeLinejoin: "round"
  }))), label && /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 14,
      color: "var(--text-primary)"
    }
  }, label));
}
Object.assign(__ds_scope, { Checkbox });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Checkbox.jsx", error: String((e && e.message) || e) }); }

// components/forms/Input.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * PayHug Input — text field with optional label, leading/trailing adornment,
 * and error state. Blue focus ring matches the dashboard.
 */
function Input({
  label = null,
  hint = null,
  error = null,
  prefix = null,
  suffix = null,
  size = "md",
  // "sm" | "md"
  disabled = false,
  style = {},
  inputStyle = {},
  ...rest
}) {
  const [focus, setFocus] = React.useState(false);
  const h = size === "sm" ? 36 : 44;
  const borderColor = error ? "var(--ph-danger)" : focus ? "var(--border-focus)" : "var(--border-strong)";
  return /*#__PURE__*/React.createElement("label", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: 7,
      fontFamily: "var(--font-sans)",
      ...style
    }
  }, label && /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 13,
      fontWeight: 700,
      color: "var(--text-primary)"
    }
  }, label), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: 8,
      height: h,
      padding: "0 14px",
      background: disabled ? "var(--ph-gray-100)" : "#fff",
      border: `1.5px solid ${borderColor}`,
      borderRadius: "var(--r-md)",
      boxShadow: focus && !error ? "var(--sh-focus)" : "none",
      transition: "border-color var(--dur) var(--ease), box-shadow var(--dur) var(--ease)",
      boxSizing: "border-box"
    }
  }, prefix && /*#__PURE__*/React.createElement("span", {
    style: {
      color: "var(--text-secondary)",
      fontSize: 14,
      display: "inline-flex"
    }
  }, prefix), /*#__PURE__*/React.createElement("input", _extends({
    disabled: disabled,
    onFocus: () => setFocus(true),
    onBlur: () => setFocus(false),
    style: {
      flex: 1,
      minWidth: 0,
      border: "none",
      outline: "none",
      background: "transparent",
      fontFamily: "var(--font-sans)",
      fontSize: size === "sm" ? 14 : 15,
      color: "var(--text-primary)",
      ...inputStyle
    }
  }, rest)), suffix && /*#__PURE__*/React.createElement("span", {
    style: {
      color: "var(--text-secondary)",
      fontSize: 14,
      display: "inline-flex"
    }
  }, suffix)), (error || hint) && /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 12,
      color: error ? "var(--ph-danger)" : "var(--text-secondary)"
    }
  }, error || hint));
}
Object.assign(__ds_scope, { Input });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Input.jsx", error: String((e && e.message) || e) }); }

// components/forms/Select.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * PayHug Select — native dropdown styled to match Input, with a chevron.
 */
function Select({
  label = null,
  options = [],
  // [{value, label}] or string[]
  value,
  onChange,
  size = "md",
  disabled = false,
  placeholder = null,
  style = {},
  ...rest
}) {
  const [focus, setFocus] = React.useState(false);
  const h = size === "sm" ? 36 : 44;
  const norm = options.map(o => typeof o === "string" ? {
    value: o,
    label: o
  } : o);
  return /*#__PURE__*/React.createElement("label", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: 7,
      fontFamily: "var(--font-sans)",
      ...style
    }
  }, label && /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 13,
      fontWeight: 700,
      color: "var(--text-primary)"
    }
  }, label), /*#__PURE__*/React.createElement("div", {
    style: {
      position: "relative",
      height: h,
      border: `1.5px solid ${focus ? "var(--border-focus)" : "var(--border-strong)"}`,
      borderRadius: "var(--r-md)",
      background: disabled ? "var(--ph-gray-100)" : "#fff",
      boxShadow: focus ? "var(--sh-focus)" : "none",
      transition: "border-color var(--dur) var(--ease), box-shadow var(--dur) var(--ease)",
      boxSizing: "border-box"
    }
  }, /*#__PURE__*/React.createElement("select", _extends({
    value: value,
    onChange: onChange,
    disabled: disabled,
    onFocus: () => setFocus(true),
    onBlur: () => setFocus(false),
    style: {
      appearance: "none",
      WebkitAppearance: "none",
      width: "100%",
      height: "100%",
      border: "none",
      outline: "none",
      background: "transparent",
      padding: "0 38px 0 14px",
      fontFamily: "var(--font-sans)",
      fontSize: size === "sm" ? 14 : 15,
      color: value ? "var(--text-primary)" : "var(--text-muted)",
      cursor: disabled ? "not-allowed" : "pointer"
    }
  }, rest), placeholder && /*#__PURE__*/React.createElement("option", {
    value: ""
  }, placeholder), norm.map(o => /*#__PURE__*/React.createElement("option", {
    key: o.value,
    value: o.value
  }, o.label))), /*#__PURE__*/React.createElement("svg", {
    width: "16",
    height: "16",
    viewBox: "0 0 16 16",
    fill: "none",
    style: {
      position: "absolute",
      right: 12,
      top: "50%",
      transform: "translateY(-50%)",
      pointerEvents: "none"
    }
  }, /*#__PURE__*/React.createElement("path", {
    d: "M4 6l4 4 4-4",
    stroke: "var(--ph-gray-500)",
    strokeWidth: "1.6",
    strokeLinecap: "round",
    strokeLinejoin: "round"
  }))));
}
Object.assign(__ds_scope, { Select });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Select.jsx", error: String((e && e.message) || e) }); }

// components/navigation/SegmentedTabs.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * PayHug SegmentedTabs — channel/period filter pills.
 * The active pill is a solid blue (or green) fill; the rest are quiet text.
 * Mirrors the dashboard's 전체 / 카드 / 배달의민족 / 요기요 / 쿠팡이츠 filter.
 */
function SegmentedTabs({
  items = [],
  // string[] or [{value,label}]
  value,
  onChange,
  accent = "blue",
  // "blue" | "green"
  size = "md",
  style = {},
  ...rest
}) {
  const norm = items.map(i => typeof i === "string" ? {
    value: i,
    label: i
  } : i);
  const h = size === "sm" ? 32 : 38;
  const activeBg = accent === "green" ? "var(--ph-green)" : "var(--ph-blue-600)";
  const activeFg = accent === "green" ? "var(--ph-forest)" : "#fff";
  return /*#__PURE__*/React.createElement("div", _extends({
    style: {
      display: "flex",
      alignItems: "center",
      gap: 6,
      flexWrap: "wrap",
      ...style
    }
  }, rest), norm.map(it => {
    const active = it.value === value;
    return /*#__PURE__*/React.createElement("button", {
      key: it.value,
      type: "button",
      onClick: () => onChange && onChange(it.value),
      style: {
        height: h,
        padding: "0 16px",
        borderRadius: "var(--r-pill)",
        border: "none",
        cursor: "pointer",
        fontFamily: "var(--font-sans)",
        fontSize: size === "sm" ? 13 : 14,
        fontWeight: 700,
        background: active ? activeBg : "transparent",
        color: active ? activeFg : "var(--text-secondary)",
        transition: "background var(--dur) var(--ease), color var(--dur) var(--ease)",
        whiteSpace: "nowrap"
      }
    }, it.label);
  }));
}
Object.assign(__ds_scope, { SegmentedTabs });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/navigation/SegmentedTabs.jsx", error: String((e && e.message) || e) }); }

// components/navigation/SidebarNav.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * PayHug SidebarNav — the admin left navigation on the dark forest-navy rail.
 * Grouped items with captions; the active item is a bright-green fill with
 * forest text. Each item takes an `icon` ReactNode (channel-agnostic).
 */
function SidebarNav({
  groups = [],
  // [{caption?, items:[{value,label,icon?,badge?}]}]
  value,
  onChange,
  style = {},
  ...rest
}) {
  return /*#__PURE__*/React.createElement("nav", _extends({
    style: {
      display: "flex",
      flexDirection: "column",
      gap: 22,
      ...style
    }
  }, rest), groups.map((g, gi) => /*#__PURE__*/React.createElement("div", {
    key: gi,
    style: {
      display: "flex",
      flexDirection: "column",
      gap: 4
    }
  }, g.caption && /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      padding: "0 12px 6px",
      fontFamily: "var(--font-sans)",
      fontSize: 13,
      fontWeight: 700,
      color: g.captionTone === "green" ? "var(--ph-green)" : "var(--ph-side-muted)",
      letterSpacing: "0.01em"
    }
  }, /*#__PURE__*/React.createElement("span", null, g.caption)), g.items.map(it => /*#__PURE__*/React.createElement(NavItem, {
    key: it.value,
    item: it,
    active: it.value === value,
    onClick: () => onChange && onChange(it.value)
  })))));
}
function NavItem({
  item,
  active,
  onClick
}) {
  const [hover, setHover] = React.useState(false);
  return /*#__PURE__*/React.createElement("button", {
    type: "button",
    onClick: onClick,
    onMouseEnter: () => setHover(true),
    onMouseLeave: () => setHover(false),
    style: {
      display: "flex",
      alignItems: "center",
      gap: 12,
      width: "100%",
      height: 46,
      padding: "0 14px",
      border: "none",
      cursor: "pointer",
      textAlign: "left",
      borderRadius: "var(--r-lg)",
      background: active ? "var(--ph-green)" : hover ? "var(--ph-side-bg-2)" : "transparent",
      color: active ? "var(--ph-forest)" : "var(--ph-side-text)",
      fontFamily: "var(--font-sans)",
      fontSize: 15,
      fontWeight: active ? 700 : 500,
      transition: "background var(--dur) var(--ease), color var(--dur) var(--ease)"
    }
  }, item.icon && /*#__PURE__*/React.createElement("span", {
    style: {
      display: "inline-flex",
      width: 20,
      height: 20,
      flex: "none",
      alignItems: "center",
      justifyContent: "center"
    }
  }, item.icon), /*#__PURE__*/React.createElement("span", {
    style: {
      flex: 1,
      whiteSpace: "nowrap",
      overflow: "hidden",
      textOverflow: "ellipsis"
    }
  }, item.label), item.badge != null && /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 11,
      fontWeight: 700,
      padding: "1px 7px",
      borderRadius: "var(--r-pill)",
      background: active ? "rgba(22,51,0,0.15)" : "var(--ph-danger)",
      color: active ? "var(--ph-forest)" : "#fff"
    }
  }, item.badge));
}
Object.assign(__ds_scope, { SidebarNav });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/navigation/SidebarNav.jsx", error: String((e && e.message) || e) }); }

// components/navigation/Tabs.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * PayHug Tabs — workspace/section tabs with an underline indicator
 * (active label = ink, indicator = brand green). Used in the admin top bar
 * (홈 · 가맹점 관리 · 정산 현황 …). Tabs may be closable.
 */
function Tabs({
  items = [],
  // [{value,label,closable?}]
  value,
  onChange,
  onClose,
  style = {},
  ...rest
}) {
  const norm = items.map(i => typeof i === "string" ? {
    value: i,
    label: i
  } : i);
  return /*#__PURE__*/React.createElement("div", _extends({
    style: {
      display: "flex",
      alignItems: "stretch",
      gap: 4,
      borderBottom: "1px solid var(--border-default)",
      ...style
    }
  }, rest), norm.map(it => {
    const active = it.value === value;
    return /*#__PURE__*/React.createElement("div", {
      key: it.value,
      onClick: () => onChange && onChange(it.value),
      style: {
        display: "inline-flex",
        alignItems: "center",
        gap: 8,
        padding: "12px 18px",
        cursor: "pointer",
        fontFamily: "var(--font-sans)",
        fontSize: 15,
        fontWeight: active ? 700 : 500,
        color: active ? "var(--text-primary)" : "var(--text-secondary)",
        borderBottom: `2.5px solid ${active ? "var(--ph-green-600)" : "transparent"}`,
        marginBottom: -1,
        transition: "color var(--dur) var(--ease), border-color var(--dur) var(--ease)",
        whiteSpace: "nowrap"
      }
    }, it.label, it.closable && /*#__PURE__*/React.createElement("span", {
      onClick: e => {
        e.stopPropagation();
        onClose && onClose(it.value);
      },
      style: {
        display: "inline-flex",
        color: "var(--ph-gray-400)",
        fontSize: 16,
        lineHeight: 1,
        padding: 2
      }
    }, "\xD7"));
  }));
}
Object.assign(__ds_scope, { Tabs });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/navigation/Tabs.jsx", error: String((e && e.message) || e) }); }

// ui_kits/admin_settlement/AdminApp.jsx
try { (() => {
// PayHug Admin — 정산 현황 screen. Exposes window.PHAdminApp.
(function () {
  const {
    SidebarNav,
    Tabs,
    AlertBanner,
    Badge,
    Card,
    Checkbox,
    Button,
    Avatar
  } = window.PayHugDesignSystem_81d4f2;
  const {
    merchants,
    details,
    missing,
    summary,
    CH_LABEL,
    CH_TONE
  } = window.PHADMIN;
  const won = n => n == null ? "–" : n.toLocaleString("ko-KR");
  const Num = ({
    children,
    color,
    weight = 500,
    size = 14
  }) => /*#__PURE__*/React.createElement("span", {
    className: "ph-num",
    style: {
      fontFamily: "var(--font-num)",
      fontVariantNumeric: "tabular-nums lining-nums",
      fontWeight: weight,
      fontSize: size,
      color: color || "var(--text-primary)"
    }
  }, children);
  const Ic = d => /*#__PURE__*/React.createElement("svg", {
    width: "20",
    height: "20",
    viewBox: "0 0 24 24",
    fill: "none"
  }, /*#__PURE__*/React.createElement("path", {
    d: d,
    stroke: "currentColor",
    strokeWidth: "1.7",
    strokeLinecap: "round",
    strokeLinejoin: "round"
  }));
  const I = {
    home: "M3 11l9-7 9 7M5 10v10h14V10",
    store: "M4 9l1-5h14l1 5M5 9v11h14V9M4 9h16",
    chart: "M4 20V10M10 20V4M16 20v-7M22 20H2",
    chat: "M4 5h16v11H8l-4 4z",
    settle: "M3 6h18v12H3zM3 10h18M7 14h4",
    box: "M3 7l9-4 9 4-9 4zM3 7v10l9 4 9-4V7",
    flask: "M9 3h6M10 3v6l-5 9a2 2 0 002 3h10a2 2 0 002-3l-5-9V3",
    wallet: "M3 7h15a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2zM17 13h.01",
    users: "M16 19v-2a4 4 0 00-8 0v2M12 11a3 3 0 100-6 3 3 0 000 6",
    doc: "M7 3h7l4 4v14H7zM14 3v4h4",
    clock: "M12 7v5l3 2M12 21a9 9 0 100-18 9 9 0 000 18",
    term: "M5 7l4 4-4 4M12 16h7",
    refresh: "M4 12a8 8 0 0114-5l2 2M20 12a8 8 0 01-14 5l-2-2M18 4v5h-5M6 20v-5h5"
  };
  const tdR = {
    padding: "16px",
    textAlign: "right",
    whiteSpace: "nowrap"
  };
  function SumCell({
    label,
    value,
    note,
    accent,
    plain,
    big
  }) {
    return /*#__PURE__*/React.createElement("div", {
      style: {
        display: "flex",
        flexDirection: "column",
        gap: 4
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        fontSize: 13,
        color: "var(--text-secondary)"
      }
    }, label, note && /*#__PURE__*/React.createElement("span", {
      style: {
        fontSize: 11,
        color: "var(--text-muted)",
        marginLeft: 4
      }
    }, "(", note, ")")), /*#__PURE__*/React.createElement(Num, {
      size: big ? 22 : 19,
      weight: 700,
      color: accent || (plain ? "var(--text-secondary)" : "var(--text-primary)")
    }, value));
  }
  const NAV_GROUPS = [{
    items: [{
      value: "home",
      label: "홈",
      icon: Ic(I.home)
    }, {
      value: "merch",
      label: "가맹점 관리",
      icon: Ic(I.store)
    }, {
      value: "sales",
      label: "매출 조회",
      icon: Ic(I.chart)
    }, {
      value: "qna",
      label: "1:1 문의",
      icon: Ic(I.chat),
      badge: "3"
    }]
  }, {
    caption: "정산",
    captionTone: "green",
    items: [{
      value: "settle",
      label: "정산 현황",
      icon: Ic(I.settle)
    }, {
      value: "product",
      label: "정산 상품관리",
      icon: Ic(I.box)
    }, {
      value: "sim",
      label: "정산 시뮬레이션",
      icon: Ic(I.flask)
    }, {
      value: "balance",
      label: "모 계좌 잔액 조회",
      icon: Ic(I.wallet)
    }]
  }, {
    caption: "관리자",
    items: [{
      value: "members",
      label: "회원 관리",
      icon: Ic(I.users)
    }, {
      value: "terms",
      label: "약관 관리",
      icon: Ic(I.doc)
    }, {
      value: "log",
      label: "활동 로그",
      icon: Ic(I.clock)
    }, {
      value: "ai",
      label: "AI 모니터링 어시스턴트",
      icon: Ic(I.term)
    }, {
      value: "collect",
      label: "매출 데이터 수집",
      icon: Ic(I.refresh)
    }]
  }];
  function MissingPanel() {
    return /*#__PURE__*/React.createElement(Card, {
      pad: 0,
      style: {
        overflow: "hidden"
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "16px 20px",
        borderBottom: "1px solid var(--border-hairline)"
      }
    }, /*#__PURE__*/React.createElement(Checkbox, {
      checked: false,
      onChange: () => {},
      label: /*#__PURE__*/React.createElement("span", {
        style: {
          fontWeight: 600
        }
      }, "\uC804\uCCB4 \uC120\uD0DD ", /*#__PURE__*/React.createElement("span", {
        style: {
          color: "var(--text-secondary)",
          fontWeight: 400
        }
      }, "\uC120\uD0DD 0\uAC74 \xB7 0\uC6D0"))
    }), /*#__PURE__*/React.createElement("div", {
      style: {
        display: "flex",
        gap: 8
      }
    }, /*#__PURE__*/React.createElement(Button, {
      variant: "secondary",
      size: "sm"
    }, "\uBBF8\uB9AC\uBCF4\uAE30"), /*#__PURE__*/React.createElement(Button, {
      variant: "primary",
      size: "sm"
    }, "\uBC14\uB85C\uC774\uCCB4"), /*#__PURE__*/React.createElement(Button, {
      variant: "ghost",
      size: "sm"
    }, "\uC774\uBBF8\uC9C0\uAE09(\uAE30\uB85D\uB9CC)"))), /*#__PURE__*/React.createElement("div", {
      style: {
        padding: "14px 20px 18px",
        background: "var(--ph-danger-tint)"
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        marginBottom: 10
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        display: "flex",
        alignItems: "center",
        gap: 8
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        fontWeight: 700,
        fontSize: 16
      }
    }, missing.merchant), /*#__PURE__*/React.createElement(Badge, {
      tone: "card",
      size: "sm"
    }, missing.code), /*#__PURE__*/React.createElement(Num, {
      color: "var(--text-secondary)",
      size: 13
    }, missing.biz)), /*#__PURE__*/React.createElement(Num, {
      size: 17,
      weight: 700,
      color: "var(--ph-danger-600)"
    }, won(missing.total), "\uC6D0 (", missing.count, "\uAC74)")), missing.groups.map((g, gi) => /*#__PURE__*/React.createElement("div", {
      key: gi,
      style: {
        background: "#fff",
        borderRadius: "var(--r-lg)",
        padding: "12px 16px",
        marginBottom: 8
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        marginBottom: g.items.length ? 8 : 0
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        display: "flex",
        alignItems: "center",
        gap: 10
      }
    }, /*#__PURE__*/React.createElement(Num, {
      weight: 700,
      size: 15
    }, g.date), /*#__PURE__*/React.createElement("span", {
      style: {
        fontSize: 13,
        color: "var(--text-secondary)"
      }
    }, g.count, "\uAC74"), /*#__PURE__*/React.createElement(Badge, {
      tone: "danger",
      size: "sm"
    }, g.tag)), /*#__PURE__*/React.createElement("div", {
      style: {
        fontSize: 13,
        color: "var(--text-secondary)"
      }
    }, "\uB9E4\uCD9C ", /*#__PURE__*/React.createElement(Num, null, won(g.sales)), "\u3000\uBBF8\uC9C0\uAE09 ", /*#__PURE__*/React.createElement(Num, {
      weight: 700,
      color: "var(--ph-danger-600)"
    }, won(g.unpaid), "\uC6D0"))), g.items.map((it, ii) => /*#__PURE__*/React.createElement("div", {
      key: ii,
      style: {
        display: "flex",
        alignItems: "center",
        gap: 12,
        padding: "7px 0",
        borderTop: "1px solid var(--border-hairline)"
      }
    }, /*#__PURE__*/React.createElement(Checkbox, {
      checked: false,
      onChange: () => {}
    }), /*#__PURE__*/React.createElement(Badge, {
      tone: "card",
      size: "sm"
    }, "\uCE74\uB4DC"), /*#__PURE__*/React.createElement(Num, {
      color: "var(--text-primary)"
    }, it.apprv), /*#__PURE__*/React.createElement("span", {
      style: {
        fontSize: 14
      }
    }, it.co), /*#__PURE__*/React.createElement("span", {
      style: {
        fontSize: 13,
        color: "var(--text-secondary)"
      }
    }, "\uC785\uAE08\uC608\uC815 ", /*#__PURE__*/React.createElement(Num, {
      color: "var(--text-secondary)"
    }, it.due)), /*#__PURE__*/React.createElement(Badge, {
      tone: "amber",
      size: "sm"
    }, "\uC608\uC815\uC77C \uACBD\uACFC"), /*#__PURE__*/React.createElement("div", {
      style: {
        flex: 1
      }
    }), /*#__PURE__*/React.createElement(Num, {
      weight: 700,
      color: "var(--ph-danger-600)"
    }, won(it.amt), "\uC6D0")))))));
  }
  function MerchantTable() {
    const heads = ["가맹점", "카드 매출", "배달 매출", "수수료", "순지급액", "선정산 수수료", "오프라인차감", "차액", "선정산 지급액", "상태"];
    return /*#__PURE__*/React.createElement(Card, {
      pad: 0,
      style: {
        overflow: "hidden"
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        display: "flex",
        alignItems: "center",
        gap: 32,
        padding: "20px 24px",
        flexWrap: "wrap",
        borderBottom: "1px solid var(--border-hairline)"
      }
    }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
      style: {
        display: "flex",
        alignItems: "baseline",
        gap: 8
      }
    }, /*#__PURE__*/React.createElement(Num, {
      size: 26,
      weight: 700
    }, summary.settleDate), /*#__PURE__*/React.createElement("span", {
      style: {
        fontSize: 18,
        fontWeight: 700
      }
    }, "\uC815\uC0B0")), /*#__PURE__*/React.createElement("div", {
      style: {
        fontSize: 13,
        color: "var(--text-secondary)"
      }
    }, /*#__PURE__*/React.createElement(Num, {
      color: "var(--text-secondary)",
      size: 13
    }, summary.salesBase), " \uB9E4\uCD9C \uAE30\uC900")), /*#__PURE__*/React.createElement(SumCell, {
      label: `${summary.merchants}개 가맹점`,
      value: `${summary.count}건`,
      plain: true
    }), /*#__PURE__*/React.createElement(SumCell, {
      label: "\uB9E4\uCD9C",
      value: won(summary.sales)
    }), /*#__PURE__*/React.createElement(SumCell, {
      label: "\uC218\uC218\uB8CC",
      value: won(summary.fee)
    }), /*#__PURE__*/React.createElement(SumCell, {
      label: "\uC120\uC815\uC0B0\uC218\uC218\uB8CC",
      value: won(summary.preFee),
      note: summary.preFeeNote,
      accent: "var(--ph-success-600)"
    }), /*#__PURE__*/React.createElement(SumCell, {
      label: "\uC624\uD504\uB77C\uC778\uCC28\uAC10",
      value: won(summary.offline),
      accent: "var(--ph-danger-600)"
    }), /*#__PURE__*/React.createElement(SumCell, {
      label: "\uC120\uC815\uC0B0",
      value: `${won(summary.payout)}원`,
      accent: "var(--ph-blue-700)",
      big: true
    })), /*#__PURE__*/React.createElement("div", {
      style: {
        overflowX: "auto"
      }
    }, /*#__PURE__*/React.createElement("table", {
      style: {
        width: "100%",
        borderCollapse: "collapse",
        fontSize: 14,
        minWidth: 1100
      }
    }, /*#__PURE__*/React.createElement("thead", null, /*#__PURE__*/React.createElement("tr", {
      style: {
        color: "var(--text-secondary)",
        fontSize: 13
      }
    }, heads.map((h, i) => /*#__PURE__*/React.createElement("th", {
      key: h,
      style: {
        textAlign: i === 0 ? "left" : i === 9 ? "center" : "right",
        fontWeight: 500,
        padding: "12px 16px",
        borderBottom: "1px solid var(--border-hairline)",
        whiteSpace: "nowrap"
      }
    }, h)))), /*#__PURE__*/React.createElement("tbody", null, merchants.map((m, i) => /*#__PURE__*/React.createElement("tr", {
      key: i,
      style: {
        borderBottom: "1px solid var(--border-hairline)"
      }
    }, /*#__PURE__*/React.createElement("td", {
      style: {
        padding: "16px"
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        display: "flex",
        alignItems: "center",
        gap: 8
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        fontWeight: 700,
        fontSize: 15
      }
    }, m.name), /*#__PURE__*/React.createElement(Badge, {
      tone: "card",
      size: "sm"
    }, m.code)), /*#__PURE__*/React.createElement(Num, {
      color: "var(--text-secondary)",
      size: 12
    }, m.biz)), /*#__PURE__*/React.createElement("td", {
      style: tdR
    }, /*#__PURE__*/React.createElement(Num, {
      weight: 600
    }, won(m.cardSales))), /*#__PURE__*/React.createElement("td", {
      style: tdR
    }, /*#__PURE__*/React.createElement(Num, {
      weight: 600
    }, won(m.deliverySales))), /*#__PURE__*/React.createElement("td", {
      style: tdR
    }, /*#__PURE__*/React.createElement(Num, null, won(m.fee))), /*#__PURE__*/React.createElement("td", {
      style: tdR
    }, /*#__PURE__*/React.createElement(Num, {
      weight: 600
    }, won(m.net))), /*#__PURE__*/React.createElement("td", {
      style: tdR
    }, /*#__PURE__*/React.createElement(Num, {
      color: "var(--ph-success-600)"
    }, won(m.preFee))), /*#__PURE__*/React.createElement("td", {
      style: tdR
    }, /*#__PURE__*/React.createElement(Num, {
      color: m.offline ? "var(--ph-danger-600)" : "var(--text-muted)"
    }, m.offline == null ? "–" : won(m.offline))), /*#__PURE__*/React.createElement("td", {
      style: tdR
    }, /*#__PURE__*/React.createElement(Num, {
      color: "var(--ph-success-600)",
      weight: 600
    }, "+", won(m.diff))), /*#__PURE__*/React.createElement("td", {
      style: tdR
    }, /*#__PURE__*/React.createElement(Num, {
      size: 17,
      weight: 700
    }, won(m.payout), "\uC6D0"), /*#__PURE__*/React.createElement("div", {
      style: {
        fontSize: 11.5,
        color: "var(--ph-warning-700)"
      }
    }, "UPL\uAE30\uC900 ", won(m.uplBase), " (\uCC28\uC774 +", won(m.uplDiff), ")")), /*#__PURE__*/React.createElement("td", {
      style: {
        padding: "16px",
        textAlign: "center"
      }
    }, /*#__PURE__*/React.createElement(Badge, {
      tone: "success"
    }, "\uC774\uCCB4\uC644\uB8CC"))))))));
  }
  function DetailTable() {
    const heads = ["매출원", "승인번호/주문번호", "카드사/앱", "매출액", "수수료", "수수료유형", "순지급액", "매입상태", "차액"];
    return /*#__PURE__*/React.createElement(Card, {
      pad: 0,
      style: {
        overflow: "hidden"
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        padding: "16px 20px",
        fontWeight: 700,
        fontSize: 15,
        borderBottom: "1px solid var(--border-hairline)"
      }
    }, "\uAC74\uBCC4 \uB9E4\uCD9C \uC0C1\uC138 ", /*#__PURE__*/React.createElement("span", {
      style: {
        color: "var(--text-secondary)",
        fontWeight: 500
      }
    }, "(", summary.detailCount, "\uAC74)")), /*#__PURE__*/React.createElement("div", {
      style: {
        overflowX: "auto"
      }
    }, /*#__PURE__*/React.createElement("table", {
      style: {
        width: "100%",
        borderCollapse: "collapse",
        fontSize: 14,
        minWidth: 920
      }
    }, /*#__PURE__*/React.createElement("thead", null, /*#__PURE__*/React.createElement("tr", {
      style: {
        color: "var(--text-secondary)",
        fontSize: 13
      }
    }, heads.map((h, i) => /*#__PURE__*/React.createElement("th", {
      key: h,
      style: {
        textAlign: i >= 3 && i !== 5 && i !== 7 ? "right" : i === 5 || i === 7 ? "center" : "left",
        fontWeight: 500,
        padding: "11px 16px",
        borderBottom: "1px solid var(--border-hairline)",
        whiteSpace: "nowrap"
      }
    }, h)))), /*#__PURE__*/React.createElement("tbody", null, details.map((d, i) => /*#__PURE__*/React.createElement("tr", {
      key: i,
      style: {
        borderBottom: "1px solid var(--border-hairline)"
      }
    }, /*#__PURE__*/React.createElement("td", {
      style: {
        padding: "12px 16px"
      }
    }, /*#__PURE__*/React.createElement(Badge, {
      tone: CH_TONE[d.ch],
      size: "sm"
    }, CH_LABEL[d.ch])), /*#__PURE__*/React.createElement("td", {
      style: {
        padding: "12px 16px"
      }
    }, /*#__PURE__*/React.createElement(Num, {
      color: "var(--text-primary)"
    }, d.apprv)), /*#__PURE__*/React.createElement("td", {
      style: {
        padding: "12px 16px"
      }
    }, d.co), /*#__PURE__*/React.createElement("td", {
      style: tdR
    }, /*#__PURE__*/React.createElement(Num, {
      weight: 600
    }, won(d.amt))), /*#__PURE__*/React.createElement("td", {
      style: tdR
    }, /*#__PURE__*/React.createElement(Num, {
      color: "var(--text-secondary)"
    }, won(d.fee))), /*#__PURE__*/React.createElement("td", {
      style: {
        padding: "12px 16px",
        textAlign: "center"
      }
    }, /*#__PURE__*/React.createElement(Badge, {
      tone: "mint",
      size: "sm"
    }, d.type)), /*#__PURE__*/React.createElement("td", {
      style: tdR
    }, /*#__PURE__*/React.createElement(Num, {
      weight: 600
    }, won(d.net))), /*#__PURE__*/React.createElement("td", {
      style: {
        padding: "12px 16px",
        textAlign: "center"
      }
    }, /*#__PURE__*/React.createElement(Badge, {
      tone: "success",
      size: "sm"
    }, "\uB9E4\uC785\uC644\uB8CC")), /*#__PURE__*/React.createElement("td", {
      style: tdR
    }, /*#__PURE__*/React.createElement(Num, {
      color: d.diff ? "var(--ph-success-600)" : "var(--text-muted)",
      weight: 600
    }, d.diff == null ? "–" : "+" + won(d.diff)))))))));
  }
  function AdminApp() {
    const [view, setView] = React.useState("settle");
    const [tab, setTab] = React.useState("settle");
    const [open] = React.useState(true);
    return /*#__PURE__*/React.createElement("div", {
      style: {
        display: "flex",
        minHeight: "100vh",
        fontFamily: "var(--font-sans)",
        color: "var(--text-primary)"
      }
    }, /*#__PURE__*/React.createElement("aside", {
      style: {
        width: 264,
        flex: "none",
        background: "var(--ph-side-bg)",
        padding: "20px 16px",
        display: "flex",
        flexDirection: "column",
        position: "sticky",
        top: 0,
        height: "100vh",
        boxSizing: "border-box"
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        display: "flex",
        alignItems: "center",
        gap: 10,
        padding: "0 6px",
        marginBottom: 26
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        width: 36,
        height: 36,
        borderRadius: 9,
        background: "var(--ph-green)",
        color: "var(--ph-forest)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontWeight: 900,
        fontSize: 19
      }
    }, "P"), /*#__PURE__*/React.createElement("span", {
      style: {
        color: "#fff",
        fontWeight: 800,
        fontSize: 18
      }
    }, "PayHug Admin")), /*#__PURE__*/React.createElement("div", {
      style: {
        flex: 1,
        overflowY: "auto"
      }
    }, /*#__PURE__*/React.createElement(SidebarNav, {
      value: view,
      onChange: setView,
      groups: NAV_GROUPS
    })), /*#__PURE__*/React.createElement("div", {
      style: {
        display: "flex",
        alignItems: "center",
        gap: 10,
        padding: "14px 8px 4px",
        borderTop: "1px solid var(--ph-side-bg-2)",
        marginTop: 10
      }
    }, /*#__PURE__*/React.createElement(Avatar, {
      name: "\uAD00",
      tone: "green",
      size: 36
    }), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
      style: {
        color: "#fff",
        fontWeight: 700,
        fontSize: 14
      }
    }, "\uAD00\uB9AC\uC790"), /*#__PURE__*/React.createElement("div", {
      style: {
        color: "var(--ph-side-muted)",
        fontSize: 12
      }
    }, "\uB85C\uADF8\uC544\uC6C3")))), /*#__PURE__*/React.createElement("main", {
      style: {
        flex: 1,
        minWidth: 0,
        background: "var(--bg-page)"
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        background: "#fff",
        padding: "0 28px",
        borderBottom: "1px solid var(--border-default)"
      }
    }, /*#__PURE__*/React.createElement(Tabs, {
      value: tab,
      onChange: setTab,
      onClose: () => {},
      items: [{
        value: "home",
        label: "홈"
      }, {
        value: "merch",
        label: "가맹점 관리"
      }, {
        value: "settle",
        label: "정산 현황",
        closable: true
      }]
    })), /*#__PURE__*/React.createElement("div", {
      style: {
        padding: "24px 28px 60px",
        display: "flex",
        flexDirection: "column",
        gap: 20,
        maxWidth: 1320
      }
    }, /*#__PURE__*/React.createElement(AlertBanner, {
      tone: "danger",
      title: "\uBBF8\uC815\uC0B0 \uB204\uB77D \uCD94\uC801",
      collapsible: true,
      defaultOpen: open,
      trailing: /*#__PURE__*/React.createElement("div", {
        style: {
          display: "flex",
          alignItems: "center",
          gap: 12
        }
      }, /*#__PURE__*/React.createElement(Badge, {
        tone: "danger"
      }, missing.count > 0 ? `1개 가맹점 · ${missing.count}건` : "없음"), /*#__PURE__*/React.createElement(Num, {
        size: 19,
        weight: 700,
        color: "var(--ph-danger-600)"
      }, won(missing.total), "\uC6D0"))
    }, "\uC815\uC0B0 \uBC30\uCE58\uAC00 \uC644\uB8CC\uB41C \uB0A0\uC9DC\uC5D0 \uB4A4\uB2A6\uAC8C \uB3C4\uCC29\uD558\uC5EC \uC120\uC815\uC0B0 \uCC98\uB9AC\uAC00 \uB204\uB77D\uB41C \uAC74\uC785\uB2C8\uB2E4. \uC774\uD2C0 \uC774\uC0C1 \uC9C0\uB09C \uAC74\uC740 \uC120\uC815\uC0B0\uC774 \uC544\uB2C8\uB77C \uCE74\uB4DC/\uBC30\uB2EC \uC218\uC218\uB8CC\uB9CC \uC81C\uC678\uD55C \uC21C\uC9C0\uAE09\uC561 \uC804\uC561\uC744 \uADF8\uB300\uB85C \uC774\uCCB4\uD569\uB2C8\uB2E4. \uC785\uAE08\uC608\uC815\uC77C \uACBD\uACFC \uC5EC\uBD80\uB294 \uCC38\uACE0\uC6A9 \uCD94\uC815\uC774\uBA70, \uC2E4\uC81C \uC785\uAE08 \uD655\uC778\uC740 \uBCC4\uB3C4\uB85C \uD310\uB2E8\uD574\uC57C \uD569\uB2C8\uB2E4."), /*#__PURE__*/React.createElement(MissingPanel, null), /*#__PURE__*/React.createElement(MerchantTable, null), /*#__PURE__*/React.createElement(DetailTable, null))));
  }
  window.PHAdminApp = AdminApp;
})();
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/admin_settlement/AdminApp.jsx", error: String((e && e.message) || e) }); }

// ui_kits/admin_settlement/data.js
try { (() => {
// PayHug Admin — 정산 현황 mock data. Exposes window.PHADMIN.
(function () {
  const merchants = [{
    name: "고짬뽕",
    code: "A5500000",
    biz: "4154101368",
    cardSales: 499000,
    deliverySales: 0,
    fee: 9840,
    net: 489160,
    preFee: 5251,
    offline: null,
    diff: 1333,
    payout: 485082,
    uplBase: 483909,
    uplDiff: 1173,
    status: "done"
  }, {
    name: "잇잇",
    code: "K7000000",
    biz: "6162853422",
    cardSales: 358700,
    deliverySales: 438500,
    fee: 154527,
    net: 642673,
    preFee: 4219,
    offline: -1638,
    diff: 6448,
    payout: 639338,
    uplBase: 638454,
    uplDiff: 884,
    status: "done"
  }];
  const details = [{
    ch: "card",
    apprv: "58190779",
    co: "롯데카드",
    amt: 10900,
    fee: 109,
    type: "실제",
    net: 10791,
    state: "done",
    diff: 112
  }, {
    ch: "coupang",
    apprv: "1P88T8",
    co: "쿠팡이츠",
    amt: 15000,
    fee: 7983,
    type: "실제",
    net: 7017,
    state: "done",
    diff: null
  }, {
    ch: "card",
    apprv: "41038021",
    co: "농협NH카드",
    amt: 13900,
    fee: 139,
    type: "실제",
    net: 13761,
    state: "done",
    diff: 135
  }, {
    ch: "card",
    apprv: "30019385",
    co: "KB카드",
    amt: 18900,
    fee: 189,
    type: "실제",
    net: 18711,
    state: "done",
    diff: 166
  }, {
    ch: "card",
    apprv: "01800900",
    co: "하나카드",
    amt: 27300,
    fee: 0,
    type: "실제",
    net: 27300,
    state: "done",
    diff: null
  }, {
    ch: "baemin",
    apprv: "T2D8000120MV",
    co: "배달의민족",
    amt: 38500,
    fee: 7874,
    type: "실제",
    net: 30626,
    state: "done",
    diff: null
  }, {
    ch: "baemin",
    apprv: "T2D80000YA05",
    co: "배달의민족",
    amt: 22000,
    fee: 5914,
    type: "실제",
    net: 16086,
    state: "done",
    diff: null
  }, {
    ch: "card",
    apprv: "83556006",
    co: "우리카드",
    amt: 10900,
    fee: 109,
    type: "실제",
    net: 10791,
    state: "done",
    diff: 107
  }];

  // 미정산 누락 추적
  const missing = {
    total: 83641,
    count: 4,
    merchant: "잇잇",
    code: "K7000000",
    biz: "6162853422",
    groups: [{
      date: "2026-06-14",
      count: 1,
      tag: "해당일 정산완료 - 누락",
      sales: 13900,
      unpaid: 13796,
      items: [{
        apprv: "98231264",
        co: "삼성카드",
        due: "2026-06-16",
        amt: 13796
      }]
    }, {
      date: "2026-06-13",
      count: 1,
      tag: "해당일 정산완료 - 누락",
      sales: 22400,
      unpaid: 22232,
      items: [{
        apprv: "60702295",
        co: "삼성카드",
        due: "2026-06-15",
        amt: 22232
      }]
    }, {
      date: "2026-06-06",
      count: 2,
      tag: "해당일 정산완료 - 누락",
      sales: 48400,
      unpaid: 47613,
      items: [{
        apprv: "00283649",
        co: "하나카드",
        due: "2026-06-09",
        amt: 21212
      }, {
        apprv: "14921793",
        co: "삼성카드",
        due: "2026-06-08",
        amt: 26401
      }]
    }]
  };
  const summary = {
    settleDate: "2026-05-28",
    salesBase: "2026-05-27",
    merchants: 4,
    count: 87,
    sales: 1838900,
    fee: 166216,
    preFee: 11413,
    preFeeNote: "매입9,144+시스템1,221+이체990+차액58",
    offline: -1638,
    payout: 1663158,
    detailCount: 44
  };
  const CH_LABEL = {
    card: "카드",
    baemin: "배민",
    yogiyo: "요기요",
    coupang: "쿠팡이츠"
  };
  const CH_TONE = {
    card: "card",
    baemin: "warning",
    yogiyo: "navy",
    coupang: "danger"
  };
  window.PHADMIN = {
    merchants,
    details,
    missing,
    summary,
    CH_LABEL,
    CH_TONE
  };
})();
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/admin_settlement/data.js", error: String((e && e.message) || e) }); }

// ui_kits/payhug_app/PayhugApp.jsx
try { (() => {
// PayHug app — responsive web layout (수정.fig 기준).
// 메인(잇잇 · 미리받는돈 · 6월총매출[매출/비용/수익 탭 + 접이식 달력]) →
// 총매출액(날짜별) → 카드/배달앱 상세 → 단건 / 미매입 내역 / 계좌 입금 내역.
// Exposes window.PHPayhugApp.
(function () {
  const {
    SalesBreakdown,
    Badge
  } = window.PayHugDesignSystem_81d4f2;
  const D = window.PHAPP;
  const won = n => typeof n === "number" ? n.toLocaleString("ko-KR") + "원" : n;
  const wonN = n => typeof n === "number" ? n.toLocaleString("ko-KR") : n;
  const C_TOTAL = "var(--ph-ink)";
  const C_CARD = "var(--ph-blue-600)";
  const C_DELIV = "var(--ph-success-600)";
  const Ic = (d, c = "currentColor") => /*#__PURE__*/React.createElement("svg", {
    width: "24",
    height: "24",
    viewBox: "0 0 24 24",
    fill: "none"
  }, /*#__PURE__*/React.createElement("path", {
    d: d,
    stroke: c,
    strokeWidth: "1.9",
    strokeLinecap: "round",
    strokeLinejoin: "round"
  }));
  const BACK = "M15 6l-6 6 6 6",
    PREV = "M14 6l-6 6 6 6",
    NEXT = "M10 6l6 6-6 6",
    CH_R = "M9 6l6 6-6 6",
    CH_D = "M6 9l6 6 6-6",
    CH_U = "M6 15l6-6 6 6";
  const Money = ({
    children,
    c = "var(--text-primary)",
    s = 16,
    w = 700
  }) => /*#__PURE__*/React.createElement("span", {
    className: "ph-num",
    style: {
      fontFamily: "var(--font-num)",
      fontVariantNumeric: "tabular-nums lining-nums",
      fontSize: s,
      fontWeight: w,
      color: c,
      whiteSpace: "nowrap",
      flex: "none"
    }
  }, children);
  const Card = ({
    children,
    style,
    onClick
  }) => /*#__PURE__*/React.createElement("div", {
    onClick: onClick,
    style: {
      background: "#fff",
      borderRadius: 20,
      boxShadow: "0 1px 16px rgba(0,0,0,0.10)",
      boxSizing: "border-box",
      ...style
    }
  }, children);
  const detailCard = {
    background: "#fff",
    borderRadius: 20,
    boxShadow: "0 1px 16px rgba(0,0,0,0.10)",
    overflow: "hidden"
  };
  const pad = {
    padding: "0 20px 24px"
  };
  function CardHeader({
    title,
    onBack
  }) {
    return /*#__PURE__*/React.createElement("div", {
      style: {
        display: "flex",
        alignItems: "center",
        gap: 6,
        padding: "16px 18px 10px"
      }
    }, onBack && /*#__PURE__*/React.createElement("span", {
      onClick: onBack,
      style: {
        cursor: "pointer",
        display: "inline-flex",
        color: "var(--text-primary)",
        marginLeft: -6
      }
    }, Ic(BACK)), /*#__PURE__*/React.createElement("span", {
      style: {
        fontSize: 19,
        fontWeight: 700
      }
    }, title));
  }
  function DateNav({
    label,
    sub
  }) {
    return /*#__PURE__*/React.createElement("div", {
      style: {
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        gap: 24,
        padding: "8px 0 6px"
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        color: "var(--ph-gray-400)",
        display: "inline-flex"
      }
    }, Ic(PREV)), /*#__PURE__*/React.createElement("div", {
      style: {
        textAlign: "center"
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        fontSize: 16,
        fontWeight: 700
      }
    }, label), sub && /*#__PURE__*/React.createElement("div", {
      style: {
        fontSize: 12,
        color: "var(--text-muted)",
        marginTop: 2
      }
    }, sub)), /*#__PURE__*/React.createElement("span", {
      style: {
        color: "var(--ph-gray-400)",
        display: "inline-flex"
      }
    }, Ic(NEXT)));
  }
  function KV({
    k,
    sub,
    v,
    bold,
    color,
    indent
  }) {
    return /*#__PURE__*/React.createElement("div", {
      style: {
        display: "flex",
        alignItems: "center",
        padding: "11px 0",
        paddingLeft: indent ? 16 : 0,
        borderLeft: indent ? "1.5px solid var(--border-default)" : "none",
        marginLeft: indent ? 4 : 0
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        fontSize: indent ? 14.5 : 16,
        fontWeight: bold ? 700 : 500,
        color: indent ? "var(--text-secondary)" : "var(--text-primary)"
      }
    }, k), sub != null && /*#__PURE__*/React.createElement("span", {
      className: "ph-num",
      style: {
        fontSize: 13,
        color: "var(--text-muted)",
        marginLeft: 8,
        fontFamily: "var(--font-num)"
      }
    }, sub), /*#__PURE__*/React.createElement("div", {
      style: {
        flex: 1
      }
    }), /*#__PURE__*/React.createElement(Money, {
      s: indent ? 14.5 : 16,
      w: bold ? 700 : 600,
      c: color || (indent ? "var(--text-secondary)" : "var(--text-primary)")
    }, typeof v === "number" ? won(v) : v));
  }
  function HiliteRow({
    label,
    count,
    amount,
    tone
  }) {
    const blue = tone === "blue";
    const bg = blue ? "var(--ph-blue-tint)" : "#FDF1F0";
    const fg = blue ? "var(--ph-blue-600)" : "#D75751";
    return /*#__PURE__*/React.createElement("div", {
      style: {
        display: "flex",
        alignItems: "center",
        gap: 8,
        background: bg,
        borderRadius: 12,
        padding: "12px 14px",
        margin: "4px 0"
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        fontSize: 15,
        fontWeight: 700,
        color: fg
      }
    }, label), count != null && /*#__PURE__*/React.createElement("span", {
      className: "ph-num",
      style: {
        fontSize: 12.5,
        color: fg,
        opacity: 0.8,
        fontFamily: "var(--font-num)"
      }
    }, count, "\uAC74"), /*#__PURE__*/React.createElement("div", {
      style: {
        flex: 1
      }
    }), /*#__PURE__*/React.createElement(Money, {
      s: 16,
      c: fg
    }, "+", wonN(amount), "\uC6D0"));
  }
  function GreenNote({
    children
  }) {
    return /*#__PURE__*/React.createElement("div", {
      style: {
        background: "var(--ph-green-tint)",
        color: "var(--ph-forest)",
        borderRadius: 14,
        padding: "16px 18px",
        fontSize: 14,
        lineHeight: 1.6,
        whiteSpace: "pre-line"
      }
    }, children);
  }
  function GreenButton({
    children,
    onClick
  }) {
    return /*#__PURE__*/React.createElement("button", {
      onClick: onClick,
      style: {
        width: "100%",
        height: 56,
        border: "none",
        borderRadius: 16,
        background: "var(--ph-green)",
        color: "var(--ph-forest)",
        fontFamily: "var(--font-sans)",
        fontSize: 17,
        fontWeight: 700,
        cursor: "pointer"
      }
    }, children);
  }
  function Tag({
    done
  }) {
    return /*#__PURE__*/React.createElement("span", {
      style: {
        fontSize: 12,
        fontWeight: 700,
        padding: "3px 8px",
        borderRadius: 6,
        background: done ? "#E9F8FF" : "#FDF1F0",
        color: done ? "var(--ph-blue-600)" : "#D75751"
      }
    }, done ? "매입 완료" : "미매입");
  }
  const DOW = ["일", "월", "화", "수", "목", "금", "토"];
  const fmt = n => n == null ? null : n.toLocaleString("ko-KR");
  const dayLabel = day => {
    const cal = D.salesCalendar;
    const w = DOW[new Date(cal.year, cal.month - 1, day).getDay()];
    return `26년 6월 ${day}일 (${w})`;
  };
  const TABS = [{
    key: "sales",
    label: "매출",
    monthKey: "sales",
    title: "6월 총 매출",
    screen: "totalsales",
    legend: [["총 매출액", C_TOTAL], ["카드", C_CARD], ["배달앱", C_DELIV]]
  }, {
    key: "cost",
    label: "비용",
    monthKey: "cost",
    title: "6월 총 비용",
    screen: "costdetail",
    legend: [["총 비용", C_TOTAL], ["카드 비용", C_CARD], ["배달앱 비용", C_DELIV]]
  }, {
    key: "profit",
    label: "수익",
    monthKey: "profit",
    title: "6월 총 수익",
    screen: "profitdetail",
    legend: [["총 수익", C_TOTAL], ["카드 수익", C_CARD], ["배달앱 수익", C_DELIV]]
  }];
  function dayValues(tab, x) {
    if (!x) return [];
    const m = D.dayMetrics(x);
    if (tab === "sales") return [[m.sales, C_TOTAL], [m.cardSales, C_CARD], [m.delivSales, C_DELIV]];
    if (tab === "cost") return [[m.cost, C_TOTAL], [m.cardCost, C_CARD], [m.delivCost, C_DELIV]];
    return [[m.profit, C_TOTAL], [m.cardProfit, C_CARD], [m.delivProfit, C_DELIV]];
  }
  function MonthSalesCard({
    push
  }) {
    const cal = D.salesCalendar;
    const [tab, setTab] = React.useState("sales");
    const [open, setOpen] = React.useState(false);
    const t = TABS.find(x => x.key === tab);
    const startDow = new Date(cal.year, cal.month - 1, 1).getDay();
    const daysInMonth = new Date(cal.year, cal.month, 0).getDate();
    const prevDays = new Date(cal.year, cal.month - 1, 0).getDate();
    const cells = [];
    for (let i = 0; i < 42; i++) {
      const dn = i - startDow + 1;
      if (dn < 1) cells.push({
        d: prevDays + dn,
        out: true
      });else if (dn > daysInMonth) cells.push({
        d: dn - daysInMonth,
        out: true
      });else cells.push({
        d: dn,
        out: false
      });
    }
    const todayRow = Math.floor((startDow + cal.today - 1) / 7);
    const fullRows = Math.ceil((startDow + daysInMonth) / 7);
    const view = open ? cells.slice(0, fullRows * 7) : cells.slice(todayRow * 7, todayRow * 7 + 7);
    return /*#__PURE__*/React.createElement(Card, {
      style: {
        padding: "26px 22px 8px"
      }
    }, /*#__PURE__*/React.createElement("div", {
      onClick: () => push({
        name: t.screen,
        day: cal.today
      }),
      style: {
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        cursor: "pointer"
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        fontSize: 20,
        fontWeight: 700
      }
    }, t.title), /*#__PURE__*/React.createElement("span", {
      style: {
        color: "var(--ph-gray-400)"
      }
    }, Ic(CH_R))), /*#__PURE__*/React.createElement("div", {
      style: {
        marginTop: 10
      }
    }, /*#__PURE__*/React.createElement(Money, {
      s: 28,
      c: "var(--text-secondary)"
    }, wonN(cal.monthly[t.monthKey]), "\uC6D0")), /*#__PURE__*/React.createElement("div", {
      style: {
        display: "flex",
        gap: 8,
        marginTop: 18
      }
    }, TABS.map(x => {
      const on = x.key === tab;
      return /*#__PURE__*/React.createElement("button", {
        key: x.key,
        onClick: () => setTab(x.key),
        style: {
          border: "none",
          cursor: "pointer",
          padding: "8px 18px",
          borderRadius: 9,
          fontFamily: "var(--font-sans)",
          fontSize: 14,
          fontWeight: 700,
          background: on ? "var(--ph-blue-600)" : "var(--ph-gray-100)",
          color: on ? "#fff" : "var(--text-secondary)"
        }
      }, x.label);
    })), /*#__PURE__*/React.createElement("div", {
      style: {
        display: "flex",
        flexWrap: "wrap",
        gap: "8px 22px",
        background: "var(--ph-gray-50)",
        borderRadius: 14,
        padding: "14px 18px",
        marginTop: 14
      }
    }, t.legend.map(([lb, cc]) => /*#__PURE__*/React.createElement("div", {
      key: lb,
      style: {
        display: "flex",
        alignItems: "center",
        gap: 8
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        width: 14,
        height: 14,
        borderRadius: 4,
        background: cc,
        flex: "none"
      }
    }), /*#__PURE__*/React.createElement("span", {
      style: {
        fontSize: 13,
        color: "var(--text-secondary)"
      }
    }, lb)))), /*#__PURE__*/React.createElement("div", {
      style: {
        display: "grid",
        gridTemplateColumns: "repeat(7,1fr)",
        marginTop: 16
      }
    }, DOW.map(d => /*#__PURE__*/React.createElement("div", {
      key: d,
      style: {
        textAlign: "left",
        paddingLeft: 6,
        fontSize: 13,
        color: "var(--text-secondary)",
        paddingBottom: 8
      }
    }, d))), /*#__PURE__*/React.createElement("div", {
      style: {
        display: "grid",
        gridTemplateColumns: "repeat(7,1fr)",
        borderTop: "1px solid var(--ph-gray-200)"
      }
    }, view.map((cell, i) => {
      const data = !cell.out && cell.d <= cal.today ? cal.days[cell.d] : null;
      const isToday = !cell.out && cell.d === cal.today;
      const vals = dayValues(tab, data);
      return /*#__PURE__*/React.createElement("div", {
        key: i,
        onClick: () => data && push({
          name: t.screen,
          day: cell.d
        }),
        style: {
          borderTop: "1px solid var(--ph-gray-100)",
          minHeight: 62,
          padding: "8px 3px 10px 6px",
          display: "flex",
          flexDirection: "column",
          alignItems: "flex-start",
          gap: 5,
          cursor: data ? "pointer" : "default"
        }
      }, /*#__PURE__*/React.createElement("span", {
        className: "ph-num",
        style: {
          fontFamily: "var(--font-num)",
          fontSize: 13,
          fontWeight: 500,
          color: cell.out ? "var(--ph-gray-300)" : "var(--text-secondary)",
          width: 24,
          height: 24,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          borderRadius: "50%",
          background: isToday ? "var(--ph-gray-200)" : "transparent"
        }
      }, cell.d), vals.length > 0 && /*#__PURE__*/React.createElement("div", {
        style: {
          display: "flex",
          flexDirection: "column",
          alignItems: "flex-start",
          lineHeight: 1.25,
          width: "100%"
        }
      }, vals.map(([v, cc], k) => v ? /*#__PURE__*/React.createElement("span", {
        key: k,
        className: "ph-num",
        style: {
          fontSize: 10.5,
          fontWeight: 600,
          color: cc,
          fontFamily: "var(--font-num)"
        }
      }, fmt(v)) : null)));
    })), /*#__PURE__*/React.createElement("div", {
      onClick: () => setOpen(o => !o),
      style: {
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        gap: 4,
        padding: "14px 0 12px",
        cursor: "pointer",
        color: "var(--ph-gray-700)"
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        fontSize: 14,
        fontWeight: 500
      }
    }, open ? "달력 접기" : "달력 펼치기"), Ic(open ? CH_U : CH_D, "var(--ph-gray-500)")));
  }
  function Main({
    push
  }) {
    const p = D.premoney;
    return /*#__PURE__*/React.createElement("div", {
      "data-screen-label": "\uBA54\uC778",
      style: {
        display: "flex",
        flexDirection: "column",
        gap: 16
      }
    }, /*#__PURE__*/React.createElement(Card, {
      style: {
        padding: "20px 22px"
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        display: "flex",
        alignItems: "center",
        gap: 12
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        fontSize: 18,
        fontWeight: 700
      }
    }, D.store.name), /*#__PURE__*/React.createElement(Badge, {
      tone: "success",
      size: "sm"
    }, D.store.status), /*#__PURE__*/React.createElement("div", {
      style: {
        flex: 1
      }
    }), /*#__PURE__*/React.createElement("span", {
      style: {
        color: "var(--ph-ink)"
      }
    }, Ic(CH_D))), /*#__PURE__*/React.createElement("div", {
      className: "ph-num",
      style: {
        fontSize: 13.5,
        color: "var(--text-secondary)",
        fontFamily: "var(--font-num)",
        marginTop: 8
      }
    }, D.store.biz)), /*#__PURE__*/React.createElement(Card, {
      style: {
        padding: "24px 24px 22px"
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        fontSize: 13.5,
        color: "var(--text-secondary)"
      }
    }, p.dateLabel, " \xB7 \uC624\uB298"), /*#__PURE__*/React.createElement("div", {
      onClick: () => push({
        name: "premoney"
      }),
      style: {
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        cursor: "pointer",
        marginTop: 10
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        fontSize: 21,
        fontWeight: 700
      }
    }, "\uBBF8\uB9AC \uBC1B\uB294 \uB3C8"), /*#__PURE__*/React.createElement("span", {
      style: {
        color: "var(--ph-gray-400)"
      }
    }, Ic(CH_R))), /*#__PURE__*/React.createElement("div", {
      style: {
        marginTop: 12
      }
    }, /*#__PURE__*/React.createElement(Money, {
      s: 30,
      c: "var(--ph-blue-600)"
    }, wonN(p.total), "\uC6D0")), /*#__PURE__*/React.createElement("div", {
      style: {
        marginTop: 14,
        fontSize: 17,
        fontWeight: 700,
        color: "rgba(126,130,153,0.75)"
      }
    }, "\uC5B4\uC81C \uB9E4\uCD9C\uC561 ", won(p.yesterdaySales)), /*#__PURE__*/React.createElement("button", {
      onClick: () => push({
        name: "deposits"
      }),
      style: {
        width: "100%",
        height: 54,
        marginTop: 22,
        border: "none",
        borderRadius: 16,
        background: "var(--ph-gray-100)",
        color: "var(--text-secondary)",
        fontFamily: "var(--font-sans)",
        fontSize: 15,
        fontWeight: 600,
        cursor: "pointer"
      }
    }, "\uACC4\uC88C \uC785\uAE08 \uB0B4\uC5ED\uBCF4\uAE30")), /*#__PURE__*/React.createElement(MonthSalesCard, {
      push: push
    }));
  }
  function Premoney({
    push,
    pop
  }) {
    const p = D.premoney;
    const sections = [{
      label: "카드",
      amount: p.cardsTotal,
      rows: p.cards.map(c => ({
        key: c.key,
        issuer: c.name,
        count: c.count + "건",
        amount: c.amount,
        zero: c.amount === 0
      }))
    }, {
      label: "배달앱",
      amount: p.platformsTotal,
      rows: p.platforms.map(c => ({
        key: c.key,
        issuer: c.name,
        count: c.count + "건",
        amount: c.amount,
        zero: c.amount === 0
      }))
    }];
    const footer = {
      label: "페이허그",
      amount: p.payhug.total,
      rows: [{
        label: "예상 지급 차액",
        amount: p.payhug.expectedDiff,
        link: true,
        help: true
      }, {
        label: "전산 수수료",
        amount: "면제"
      }]
    };
    const onRow = key => p.cards.some(c => c.key === key) ? push({
      name: "card",
      key
    }) : push({
      name: "platform",
      key
    });
    return /*#__PURE__*/React.createElement("div", {
      "data-screen-label": "\uBBF8\uB9AC \uBC1B\uB294 \uB3C8",
      style: detailCard
    }, /*#__PURE__*/React.createElement(CardHeader, {
      title: "\uBBF8\uB9AC \uBC1B\uB294 \uB3C8",
      onBack: pop
    }), /*#__PURE__*/React.createElement(DateNav, {
      label: p.dateLabel,
      sub: p.reflectedAt
    }), /*#__PURE__*/React.createElement("div", {
      style: {
        textAlign: "center",
        padding: "8px 0 8px"
      }
    }, /*#__PURE__*/React.createElement(Money, {
      s: 30,
      c: "var(--ph-blue-600)"
    }, wonN(p.total), "\uC6D0")), /*#__PURE__*/React.createElement("div", {
      style: pad
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        background: "var(--ph-gray-100)",
        borderRadius: 12,
        padding: "12px 16px",
        fontSize: 14,
        color: "var(--text-secondary)",
        margin: "6px 0 14px"
      }
    }, "\uC5B4\uC81C \uB9E4\uCD9C\uC561 ", won(p.yesterdaySales)), /*#__PURE__*/React.createElement(SalesBreakdown, {
      sections: sections,
      footer: footer,
      onRowClick: onRow,
      onFooterClick: () => push({
        name: "diff"
      })
    })));
  }
  function TotalSales({
    params,
    push,
    pop
  }) {
    const ts = D.totalSales;
    const cal = D.salesCalendar;
    const day = params.day || cal.today;
    const dd = cal.days[day];
    const dayTotal = dd ? dd.cardSales + dd.delivSales : ts.total;
    const dateLabel = dayLabel(day);
    const sections = [{
      label: "카드",
      amount: ts.cardsTotal,
      rows: ts.cards.map(c => ({
        key: c.key,
        issuer: c.name,
        count: c.count + "건",
        amount: c.amount,
        zero: c.amount === 0
      }))
    }, {
      label: "배달앱",
      amount: ts.platformsTotal,
      rows: ts.platforms.map(c => ({
        key: c.key,
        issuer: c.name,
        count: c.count + "건",
        amount: c.amount,
        zero: c.amount === 0
      }))
    }];
    const onRow = key => ts.cards.some(c => c.key === key) ? push({
      name: "card",
      key
    }) : push({
      name: "platform",
      key
    });
    return /*#__PURE__*/React.createElement("div", {
      "data-screen-label": "\uCD1D \uB9E4\uCD9C\uC561",
      style: detailCard
    }, /*#__PURE__*/React.createElement(CardHeader, {
      title: "\uCD1D \uB9E4\uCD9C\uC561",
      onBack: pop
    }), /*#__PURE__*/React.createElement(DateNav, {
      label: dateLabel,
      sub: ts.reflectedAt
    }), /*#__PURE__*/React.createElement("div", {
      style: {
        textAlign: "center",
        padding: "8px 0 4px"
      }
    }, /*#__PURE__*/React.createElement(Money, {
      s: 32,
      c: "var(--ph-blue-600)"
    }, wonN(dayTotal), "\uC6D0")), /*#__PURE__*/React.createElement("div", {
      style: {
        textAlign: "center",
        fontSize: 13,
        color: "var(--text-muted)",
        paddingBottom: 12
      }
    }, "\uB9E4\uC785\uAE30\uC900 \uB9E4\uCD9C"), /*#__PURE__*/React.createElement("div", {
      style: pad
    }, /*#__PURE__*/React.createElement("div", {
      onClick: () => push({
        name: "excluded"
      }),
      style: {
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        background: "var(--ph-gray-100)",
        borderRadius: 16,
        padding: "16px 20px",
        cursor: "pointer",
        marginBottom: 8
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        fontSize: 15,
        fontWeight: 500,
        color: "var(--text-secondary)"
      }
    }, "\uC120\uC815\uC0B0 \uC81C\uC678\uC561 ", won(ts.excludedTotal)), /*#__PURE__*/React.createElement("span", {
      style: {
        color: "var(--ph-gray-400)"
      }
    }, Ic(CH_R))), /*#__PURE__*/React.createElement(SalesBreakdown, {
      sections: sections,
      onRowClick: onRow
    }), /*#__PURE__*/React.createElement("div", {
      style: {
        marginTop: 20
      }
    }, /*#__PURE__*/React.createElement(GreenButton, {
      onClick: () => push({
        name: "unpurchased"
      })
    }, "\uBBF8\uB9E4\uC785 \uB0B4\uC5ED \uBCF4\uB7EC\uAC00\uAE30"))));
  }
  function Unpurchased({
    pop
  }) {
    const u = D.unpurchased;
    return /*#__PURE__*/React.createElement("div", {
      "data-screen-label": "\uBBF8\uB9E4\uC785 \uB0B4\uC5ED",
      style: detailCard
    }, /*#__PURE__*/React.createElement(CardHeader, {
      title: "\uBBF8\uB9E4\uC785 \uB0B4\uC5ED",
      onBack: pop
    }), /*#__PURE__*/React.createElement("div", {
      style: {
        ...pad,
        paddingTop: 4
      }
    }, /*#__PURE__*/React.createElement("div", {
      className: "ph-num",
      style: {
        fontSize: 13.5,
        color: "var(--text-secondary)",
        fontFamily: "var(--font-num)"
      }
    }, u.date), /*#__PURE__*/React.createElement("div", {
      style: {
        margin: "6px 0 16px"
      }
    }, /*#__PURE__*/React.createElement(Money, {
      s: 32
    }, wonN(u.total), "\uC6D0")), /*#__PURE__*/React.createElement(GreenNote, null, u.note), /*#__PURE__*/React.createElement("div", {
      style: {
        marginTop: 8
      }
    }, u.rows.map((r, i) => /*#__PURE__*/React.createElement("div", {
      key: i,
      style: {
        display: "flex",
        alignItems: "flex-start",
        padding: "16px 0",
        borderBottom: "1px solid var(--border-hairline)"
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        flex: 1,
        minWidth: 0
      }
    }, /*#__PURE__*/React.createElement("div", {
      className: "ph-num",
      style: {
        fontSize: 13,
        color: "var(--text-muted)",
        fontFamily: "var(--font-num)"
      }
    }, r.date), /*#__PURE__*/React.createElement("div", {
      style: {
        fontSize: 17,
        fontWeight: 700,
        marginTop: 4
      }
    }, r.issuer)), /*#__PURE__*/React.createElement("div", {
      style: {
        textAlign: "right"
      }
    }, /*#__PURE__*/React.createElement("div", {
      className: "ph-num",
      style: {
        fontSize: 12.5,
        color: "var(--text-muted)",
        fontFamily: "var(--font-num)"
      }
    }, "\uC2B9\uC778\uBC88\uD638 ", r.apprv), /*#__PURE__*/React.createElement("div", {
      style: {
        display: "flex",
        alignItems: "center",
        justifyContent: "flex-end",
        gap: 8,
        marginTop: 6
      }
    }, /*#__PURE__*/React.createElement(Tag, {
      done: r.status === "done"
    }), /*#__PURE__*/React.createElement(Money, {
      s: 17
    }, won(r.amount))))))), /*#__PURE__*/React.createElement("div", {
      style: {
        marginTop: 22
      }
    }, /*#__PURE__*/React.createElement(GreenButton, null, "\uB0B4\uC5ED \uB354 \uBD88\uB7EC\uC624\uAE30"))));
  }
  function CardScreen({
    params,
    pop,
    push
  }) {
    const {
      card,
      txns,
      summary
    } = D.cardTxns(params.key);
    return /*#__PURE__*/React.createElement("div", {
      "data-screen-label": card.name,
      style: detailCard
    }, /*#__PURE__*/React.createElement(CardHeader, {
      title: card.name,
      onBack: pop
    }), /*#__PURE__*/React.createElement(DateNav, {
      label: D.totalSales.dateLabel,
      sub: D.UPDATE
    }), /*#__PURE__*/React.createElement("div", {
      style: {
        padding: "8px 20px 12px"
      }
    }, /*#__PURE__*/React.createElement(KV, {
      k: "\uC5B4\uC81C \uB9E4\uCD9C\uC561",
      v: summary.yesterdaySales
    }), /*#__PURE__*/React.createElement(KV, {
      k: "\uCC28\uAC10\uC561",
      v: summary.fee,
      bold: true
    }), /*#__PURE__*/React.createElement(KV, {
      k: "\uCE74\uB4DC \uC218\uC218\uB8CC",
      v: summary.fee,
      indent: true
    }), summary.addPurchase && /*#__PURE__*/React.createElement(HiliteRow, {
      label: "\uCD94\uAC00 \uB9E4\uC785",
      count: summary.addPurchase.count,
      amount: summary.addPurchase.amount,
      tone: "blue"
    }), /*#__PURE__*/React.createElement("div", {
      style: {
        borderTop: "1px solid var(--border-default)",
        marginTop: 8
      }
    }), /*#__PURE__*/React.createElement(KV, {
      k: "\uBBF8\uB9AC \uBC1B\uB294 \uB3C8",
      v: summary.premoney,
      bold: true,
      color: "var(--ph-blue-600)"
    })), /*#__PURE__*/React.createElement("div", {
      style: {
        height: 8,
        background: "var(--ph-gray-100)"
      }
    }), /*#__PURE__*/React.createElement("div", {
      style: {
        padding: "16px 20px 24px"
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        fontSize: 16,
        fontWeight: 700,
        marginBottom: 6
      }
    }, "\uC5B4\uC81C \uCE74\uB4DC \uB0B4\uC5ED"), txns.map((t, i) => /*#__PURE__*/React.createElement("div", {
      key: i,
      onClick: () => push({
        name: "txn",
        key: params.key,
        idx: i
      }),
      style: {
        display: "flex",
        alignItems: "center",
        padding: "14px 0",
        borderBottom: "1px solid var(--border-hairline)",
        cursor: "pointer"
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        flex: 1,
        minWidth: 0
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        fontSize: 15,
        fontWeight: 600
      }
    }, card.name), /*#__PURE__*/React.createElement("div", {
      className: "ph-num",
      style: {
        fontSize: 12.5,
        color: "var(--text-muted)",
        fontFamily: "var(--font-num)"
      }
    }, D.totalSales.dateLabel.replace(/26년 6월 (\d+)일.*/, "2026.06.$1"), " \xB7 ", t.time)), /*#__PURE__*/React.createElement("div", {
      style: {
        textAlign: "right"
      }
    }, /*#__PURE__*/React.createElement(Money, {
      s: 16
    }, won(t.net)), /*#__PURE__*/React.createElement("div", {
      style: {
        fontSize: 12.5,
        color: "var(--text-muted)"
      }
    }, t.payType)))), /*#__PURE__*/React.createElement("div", {
      style: {
        marginTop: 22
      }
    }, /*#__PURE__*/React.createElement(GreenButton, null, "\uB0B4\uC5ED \uB354 \uBD88\uB7EC\uC624\uAE30"))));
  }
  function TxnScreen({
    params,
    pop
  }) {
    const {
      card,
      txns
    } = D.cardTxns(params.key);
    const t = txns[params.idx] || txns[0];
    const dnum = D.totalSales.dateLabel.replace(/26년 6월 (\d+)일.*/, "$1");
    return /*#__PURE__*/React.createElement("div", {
      "data-screen-label": `${card.name} 단건`,
      style: detailCard
    }, /*#__PURE__*/React.createElement(CardHeader, {
      title: `${card.name} 내역`,
      onBack: pop
    }), /*#__PURE__*/React.createElement("div", {
      style: {
        ...pad,
        paddingTop: 4
      }
    }, /*#__PURE__*/React.createElement("div", {
      className: "ph-num",
      style: {
        fontSize: 13,
        color: "var(--text-muted)",
        fontFamily: "var(--font-num)"
      }
    }, "2026.06.", dnum, " \xB7 ", t.time), /*#__PURE__*/React.createElement("div", {
      style: {
        margin: "6px 0 18px"
      }
    }, /*#__PURE__*/React.createElement(Money, {
      s: 30
    }, won(t.net))), /*#__PURE__*/React.createElement(KV, {
      k: "\uC2B9\uC778\uBC88\uD638",
      v: /*#__PURE__*/React.createElement("span", {
        className: "ph-num",
        style: {
          fontFamily: "var(--font-num)"
        }
      }, t.apprv)
    }), /*#__PURE__*/React.createElement(KV, {
      k: "\uACB0\uC81C\uC218\uB2E8",
      v: t.payType
    }), /*#__PURE__*/React.createElement(KV, {
      k: "\uC5B4\uC81C \uB9E4\uCD9C\uC561",
      v: t.sales
    }), /*#__PURE__*/React.createElement(KV, {
      k: "\uCC28\uAC10\uC561",
      v: t.fee,
      bold: true
    }), /*#__PURE__*/React.createElement(KV, {
      k: "\uCE74\uB4DC \uC218\uC218\uB8CC",
      v: t.fee,
      indent: true
    }), /*#__PURE__*/React.createElement("div", {
      style: {
        borderTop: "1px solid var(--border-default)",
        marginTop: 8
      }
    }), /*#__PURE__*/React.createElement(KV, {
      k: "\uBBF8\uB9AC \uBC1B\uB294 \uB3C8",
      v: t.net,
      bold: true,
      color: "var(--ph-blue-600)"
    })));
  }
  function PlatformScreen({
    params,
    pop,
    push
  }) {
    const pf = D.platformDetail[params.key];
    return /*#__PURE__*/React.createElement("div", {
      "data-screen-label": pf.name,
      style: detailCard
    }, /*#__PURE__*/React.createElement(CardHeader, {
      title: pf.name,
      onBack: pop
    }), /*#__PURE__*/React.createElement(DateNav, {
      label: D.totalSales.dateLabel,
      sub: D.UPDATE
    }), /*#__PURE__*/React.createElement("div", {
      style: {
        padding: "8px 20px 12px"
      }
    }, /*#__PURE__*/React.createElement(KV, {
      k: "\uC5B4\uC81C \uB9E4\uCD9C\uC561",
      v: pf.yesterdaySales
    }), /*#__PURE__*/React.createElement(KV, {
      k: "\uCC28\uAC10\uC561",
      v: pf.deductTotal,
      bold: true
    }), pf.deducts.map((d, i) => /*#__PURE__*/React.createElement(KV, {
      key: i,
      k: d[0],
      v: d[1],
      indent: true
    })), pf.excluded && /*#__PURE__*/React.createElement(HiliteRow, {
      label: "\uC120\uC815\uC0B0 \uC81C\uC678 \uAE08\uC561",
      count: pf.excluded.count,
      amount: pf.excluded.amount,
      tone: "coral"
    }), /*#__PURE__*/React.createElement("div", {
      style: {
        borderTop: "1px solid var(--border-default)",
        marginTop: 8
      }
    }), /*#__PURE__*/React.createElement(KV, {
      k: "\uBBF8\uB9AC \uBC1B\uB294 \uB3C8",
      v: pf.premoney,
      bold: true,
      color: "var(--ph-blue-600)"
    })), /*#__PURE__*/React.createElement("div", {
      style: {
        height: 8,
        background: "var(--ph-gray-100)"
      }
    }), /*#__PURE__*/React.createElement("div", {
      style: {
        padding: "16px 20px 24px"
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        fontSize: 16,
        fontWeight: 700,
        marginBottom: 6
      }
    }, "\uC5B4\uC81C \uC8FC\uBB38 \uB0B4\uC5ED"), pf.orders.length === 0 && /*#__PURE__*/React.createElement("div", {
      style: {
        padding: 32,
        textAlign: "center",
        color: "var(--text-muted)"
      }
    }, "\uC8FC\uBB38 \uB0B4\uC5ED\uC774 \uC5C6\uC5B4\uC694"), pf.orders.map((o, i) => /*#__PURE__*/React.createElement("div", {
      key: i,
      onClick: () => push({
        name: "order",
        key: params.key,
        idx: i
      }),
      style: {
        display: "flex",
        alignItems: "center",
        padding: "14px 0",
        borderBottom: "1px solid var(--border-hairline)",
        cursor: "pointer"
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        flex: 1,
        minWidth: 0
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        fontSize: 15,
        fontWeight: 500
      }
    }, o.shop), /*#__PURE__*/React.createElement("div", {
      className: "ph-num",
      style: {
        fontSize: 12.5,
        color: "var(--text-muted)",
        fontFamily: "var(--font-num)"
      }
    }, o.date, " \xB7 ", o.time)), /*#__PURE__*/React.createElement("div", {
      style: {
        textAlign: "right"
      }
    }, /*#__PURE__*/React.createElement(Money, {
      s: 16,
      c: o.amount < 0 ? "var(--text-money-neg)" : "var(--text-primary)"
    }, (o.amount >= 0 ? "+" : "") + wonN(o.amount), "\uC6D0"), /*#__PURE__*/React.createElement("div", {
      style: {
        fontSize: 12,
        color: "var(--text-muted)"
      }
    }, o.pay)))), /*#__PURE__*/React.createElement("div", {
      style: {
        marginTop: 22
      }
    }, /*#__PURE__*/React.createElement(GreenButton, null, "\uB0B4\uC5ED \uB354 \uBD88\uB7EC\uC624\uAE30"))));
  }
  function OrderScreen({
    pop
  }) {
    const o = D.orderDetail;
    return /*#__PURE__*/React.createElement("div", {
      "data-screen-label": `${o.name} 주문`,
      style: detailCard
    }, /*#__PURE__*/React.createElement(CardHeader, {
      title: `${o.name} 내역`,
      onBack: pop
    }), /*#__PURE__*/React.createElement("div", {
      style: {
        ...pad,
        paddingTop: 4
      }
    }, /*#__PURE__*/React.createElement("div", {
      className: "ph-num",
      style: {
        fontSize: 13,
        color: "var(--text-muted)",
        fontFamily: "var(--font-num)"
      }
    }, o.date, " \xB7 ", o.time), /*#__PURE__*/React.createElement("div", {
      style: {
        margin: "6px 0 18px"
      }
    }, /*#__PURE__*/React.createElement(Money, {
      s: 30,
      c: "var(--ph-blue-600)"
    }, (o.amount >= 0 ? "+" : "") + wonN(o.amount), "\uC6D0")), /*#__PURE__*/React.createElement(KV, {
      k: "\uC8FC\uBB38\uBC88\uD638",
      v: /*#__PURE__*/React.createElement("span", {
        className: "ph-num",
        style: {
          fontFamily: "var(--font-num)"
        }
      }, o.orderNo)
    }), /*#__PURE__*/React.createElement(KV, {
      k: "\uACB0\uC81C\uC218\uB2E8",
      v: o.pay
    }), /*#__PURE__*/React.createElement(KV, {
      k: "\uC5B4\uC81C \uB9E4\uCD9C\uC561",
      v: o.yesterdaySales
    }), /*#__PURE__*/React.createElement(KV, {
      k: "\uCC28\uAC10\uC561",
      v: o.deductTotal,
      bold: true
    }), o.deducts.map((d, i) => /*#__PURE__*/React.createElement(KV, {
      key: i,
      k: d[0],
      v: d[1],
      indent: true
    })), /*#__PURE__*/React.createElement("div", {
      style: {
        borderTop: "1px solid var(--border-default)",
        marginTop: 8
      }
    }), /*#__PURE__*/React.createElement(KV, {
      k: "\uBBF8\uB9AC \uBC1B\uB294 \uB3C8",
      v: o.premoney,
      bold: true,
      color: "var(--ph-blue-600)"
    }), /*#__PURE__*/React.createElement("div", {
      style: {
        marginTop: 18
      }
    }, /*#__PURE__*/React.createElement(GreenNote, null, o.note))));
  }
  function DiffScreen({
    pop
  }) {
    const e = D.expectedDiff;
    return /*#__PURE__*/React.createElement("div", {
      "data-screen-label": "\uC608\uC0C1 \uC9C0\uAE09 \uCC28\uC561",
      style: detailCard
    }, /*#__PURE__*/React.createElement(CardHeader, {
      title: "\uC608\uC0C1 \uC9C0\uAE09 \uCC28\uC561",
      onBack: pop
    }), /*#__PURE__*/React.createElement("div", {
      style: {
        ...pad,
        paddingTop: 4
      }
    }, /*#__PURE__*/React.createElement("div", {
      className: "ph-num",
      style: {
        fontSize: 13,
        color: "var(--text-muted)",
        fontFamily: "var(--font-num)"
      }
    }, e.dateLabel), /*#__PURE__*/React.createElement("div", {
      style: {
        margin: "6px 0 14px"
      }
    }, /*#__PURE__*/React.createElement(Money, {
      s: 30
    }, wonN(e.total), "\uC6D0")), /*#__PURE__*/React.createElement(GreenNote, null, e.note), /*#__PURE__*/React.createElement("div", {
      style: {
        marginTop: 16
      }
    }, e.rows.map((r, i) => /*#__PURE__*/React.createElement("div", {
      key: i,
      style: {
        display: "flex",
        alignItems: "center",
        padding: "14px 0",
        borderBottom: "1px solid var(--border-hairline)"
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        flex: 1,
        minWidth: 0
      }
    }, /*#__PURE__*/React.createElement("div", {
      className: "ph-num",
      style: {
        fontSize: 13,
        color: "var(--text-muted)",
        fontFamily: "var(--font-num)"
      }
    }, r.date), /*#__PURE__*/React.createElement("div", {
      style: {
        fontSize: 15,
        fontWeight: 600
      }
    }, r.issuer)), /*#__PURE__*/React.createElement("div", {
      style: {
        textAlign: "right"
      }
    }, /*#__PURE__*/React.createElement("div", {
      className: "ph-num",
      style: {
        fontSize: 12.5,
        color: "var(--text-muted)",
        fontFamily: "var(--font-num)"
      }
    }, r.no), /*#__PURE__*/React.createElement(Money, {
      s: 16,
      c: r.amount < 0 ? "var(--text-money-neg)" : "var(--ph-success-600)"
    }, (r.amount >= 0 ? "+" : "") + wonN(r.amount), "\uC6D0"))))), /*#__PURE__*/React.createElement("div", {
      style: {
        marginTop: 20
      }
    }, /*#__PURE__*/React.createElement(GreenButton, null, "\uB0B4\uC5ED \uB354 \uBD88\uB7EC\uC624\uAE30"))));
  }
  function DepositsScreen({
    pop
  }) {
    const d = D.deposits;
    return /*#__PURE__*/React.createElement("div", {
      "data-screen-label": "\uACC4\uC88C \uC785\uAE08 \uB0B4\uC5ED",
      style: detailCard
    }, /*#__PURE__*/React.createElement(CardHeader, {
      title: "\uACC4\uC88C \uC785\uAE08 \uB0B4\uC5ED",
      onBack: pop
    }), /*#__PURE__*/React.createElement("div", {
      style: {
        ...pad,
        paddingTop: 0
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        display: "flex",
        alignItems: "center",
        gap: 12,
        padding: "4px 0 16px"
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        width: 40,
        height: 40,
        borderRadius: 10,
        overflow: "hidden",
        background: "#fff",
        border: "1px solid var(--border-hairline)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        flex: "none"
      }
    }, /*#__PURE__*/React.createElement("img", {
      src: "../../assets/bank-hana.png",
      alt: "\uD558\uB098\uC740\uD589",
      style: {
        width: "100%",
        height: "100%",
        objectFit: "contain"
      }
    })), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
      style: {
        fontSize: 15,
        fontWeight: 700
      }
    }, d.bank), /*#__PURE__*/React.createElement("div", {
      className: "ph-num",
      style: {
        fontSize: 13,
        color: "var(--text-muted)",
        fontFamily: "var(--font-num)"
      }
    }, d.account))), d.rows.map((r, i) => /*#__PURE__*/React.createElement("div", {
      key: i,
      style: {
        display: "flex",
        alignItems: "center",
        padding: "14px 0",
        borderBottom: "1px solid var(--border-hairline)"
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        width: 44,
        flex: "none"
      }
    }, /*#__PURE__*/React.createElement("span", {
      className: "ph-num",
      style: {
        fontSize: 14,
        fontWeight: 700,
        color: "var(--text-secondary)",
        fontFamily: "var(--font-num)"
      }
    }, r.date)), /*#__PURE__*/React.createElement("div", {
      style: {
        flex: 1
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        fontSize: 15,
        fontWeight: 600
      }
    }, "\uD398\uC774\uD5C8\uADF8"), /*#__PURE__*/React.createElement("div", {
      className: "ph-num",
      style: {
        fontSize: 12.5,
        color: "var(--text-muted)",
        fontFamily: "var(--font-num)"
      }
    }, r.time)), /*#__PURE__*/React.createElement("div", {
      style: {
        textAlign: "right"
      }
    }, /*#__PURE__*/React.createElement(Money, {
      s: 16
    }, won(r.amount)), /*#__PURE__*/React.createElement("div", {
      style: {
        marginTop: 3
      }
    }, r.kind === "premoney" ? /*#__PURE__*/React.createElement(Badge, {
      tone: "green",
      size: "sm"
    }, "\uBBF8\uB9AC \uBC1B\uB294 \uB3C8") : /*#__PURE__*/React.createElement(Badge, {
      tone: "blue",
      size: "sm"
    }, "\uC120\uC815\uC0B0 \uC81C\uC678\uC561"))))), /*#__PURE__*/React.createElement("div", {
      style: {
        marginTop: 22
      }
    }, /*#__PURE__*/React.createElement(GreenButton, null, "\uB0B4\uC5ED \uB354 \uBD88\uB7EC\uC624\uAE30"))));
  }
  function CostDetail({
    params,
    pop
  }) {
    const cal = D.salesCalendar;
    const day = params.day || cal.today;
    const m = D.dayMetrics(cal.days[day]) || D.dayMetrics(cal.days[cal.today]);
    return /*#__PURE__*/React.createElement("div", {
      "data-screen-label": "\uCD1D \uBE44\uC6A9",
      style: detailCard
    }, /*#__PURE__*/React.createElement(CardHeader, {
      title: "\uCD1D \uBE44\uC6A9",
      onBack: pop
    }), /*#__PURE__*/React.createElement(DateNav, {
      label: dayLabel(day),
      sub: D.UPDATE
    }), /*#__PURE__*/React.createElement("div", {
      style: {
        textAlign: "center",
        padding: "8px 0 4px"
      }
    }, /*#__PURE__*/React.createElement(Money, {
      s: 32,
      c: "var(--ph-ink)"
    }, wonN(m.cost), "\uC6D0")), /*#__PURE__*/React.createElement("div", {
      style: {
        textAlign: "center",
        fontSize: 13,
        color: "var(--text-muted)",
        paddingBottom: 12
      }
    }, "\uCE74\uB4DC\xB7\uBC30\uB2EC\uC571 \uC218\uC218\uB8CC\uC640 \uAD11\uACE0\uBE44 \uB4F1 \uC9C0\uCD9C"), /*#__PURE__*/React.createElement("div", {
      style: pad
    }, /*#__PURE__*/React.createElement(KV, {
      k: "\uCE74\uB4DC \uC218\uC218\uB8CC",
      v: m.cardFee
    }), /*#__PURE__*/React.createElement(KV, {
      k: "\uBC30\uB2EC\uC571 \uC218\uC218\uB8CC",
      v: m.delivFee
    }), /*#__PURE__*/React.createElement(KV, {
      k: "\uAD11\uACE0\uBE44",
      v: m.adFee
    }), /*#__PURE__*/React.createElement("div", {
      style: {
        borderTop: "1px solid var(--border-default)",
        marginTop: 8
      }
    }), /*#__PURE__*/React.createElement(KV, {
      k: "\uCD1D \uBE44\uC6A9",
      v: m.cost,
      bold: true
    })));
  }
  function ProfitDetail({
    params,
    pop
  }) {
    const cal = D.salesCalendar;
    const day = params.day || cal.today;
    const m = D.dayMetrics(cal.days[day]) || D.dayMetrics(cal.days[cal.today]);
    return /*#__PURE__*/React.createElement("div", {
      "data-screen-label": "\uCD1D \uC218\uC775",
      style: detailCard
    }, /*#__PURE__*/React.createElement(CardHeader, {
      title: "\uCD1D \uC218\uC775",
      onBack: pop
    }), /*#__PURE__*/React.createElement(DateNav, {
      label: dayLabel(day),
      sub: D.UPDATE
    }), /*#__PURE__*/React.createElement("div", {
      style: {
        textAlign: "center",
        padding: "8px 0 4px"
      }
    }, /*#__PURE__*/React.createElement(Money, {
      s: 32,
      c: "var(--ph-success-600)"
    }, wonN(m.profit), "\uC6D0")), /*#__PURE__*/React.createElement("div", {
      style: {
        textAlign: "center",
        fontSize: 13,
        color: "var(--text-muted)",
        paddingBottom: 12
      }
    }, "\uCD1D \uB9E4\uCD9C\uC5D0\uC11C \uCD1D \uBE44\uC6A9\uC744 \uB04C \uAE08\uC561\uC774\uC5D0\uC694"), /*#__PURE__*/React.createElement("div", {
      style: pad
    }, /*#__PURE__*/React.createElement(KV, {
      k: "\uCE74\uB4DC \uC218\uC775",
      v: m.cardProfit,
      bold: true,
      color: "var(--ph-blue-600)"
    }), /*#__PURE__*/React.createElement(KV, {
      k: "\uCE74\uB4DC \uB9E4\uCD9C",
      v: m.cardSales,
      indent: true
    }), /*#__PURE__*/React.createElement(KV, {
      k: "\uCE74\uB4DC \uC218\uC218\uB8CC",
      v: -m.cardFee,
      indent: true
    }), /*#__PURE__*/React.createElement(KV, {
      k: "\uBC30\uB2EC\uC571 \uC218\uC775",
      v: m.delivProfit,
      bold: true,
      color: "var(--ph-success-600)"
    }), /*#__PURE__*/React.createElement(KV, {
      k: "\uBC30\uB2EC\uC571 \uB9E4\uCD9C",
      v: m.delivSales,
      indent: true
    }), /*#__PURE__*/React.createElement(KV, {
      k: "\uBC30\uB2EC\uC571 \uC218\uC218\uB8CC",
      v: -m.delivFee,
      indent: true
    }), /*#__PURE__*/React.createElement(KV, {
      k: "\uAD11\uACE0\uBE44",
      v: -m.adFee,
      indent: true
    }), /*#__PURE__*/React.createElement("div", {
      style: {
        borderTop: "1px solid var(--border-default)",
        marginTop: 8
      }
    }), /*#__PURE__*/React.createElement(KV, {
      k: "\uCD1D \uC218\uC775",
      v: m.profit,
      bold: true
    })));
  }
  function Excluded({
    push,
    pop
  }) {
    const e = D.excludedDetail;
    return /*#__PURE__*/React.createElement("div", {
      "data-screen-label": "\uC120\uC815\uC0B0 \uC81C\uC678\uC561",
      style: detailCard
    }, /*#__PURE__*/React.createElement(CardHeader, {
      title: "\uC120\uC815\uC0B0 \uC81C\uC678\uC561",
      onBack: pop
    }), /*#__PURE__*/React.createElement("div", {
      style: {
        ...pad,
        paddingTop: 4
      }
    }, /*#__PURE__*/React.createElement("div", {
      className: "ph-num",
      style: {
        fontSize: 13.5,
        color: "var(--text-secondary)",
        fontFamily: "var(--font-num)"
      }
    }, e.date), /*#__PURE__*/React.createElement("div", {
      style: {
        margin: "6px 0 16px"
      }
    }, /*#__PURE__*/React.createElement(Money, {
      s: 32
    }, wonN(e.total), "\uC6D0")), /*#__PURE__*/React.createElement(GreenNote, null, e.note), /*#__PURE__*/React.createElement("div", {
      style: {
        marginTop: 16
      }
    }, e.reasons.map((r, i) => /*#__PURE__*/React.createElement("div", {
      key: i,
      onClick: () => push({
        name: r.key
      }),
      style: {
        display: "flex",
        alignItems: "center",
        gap: 12,
        background: "var(--ph-gray-100)",
        borderRadius: 16,
        padding: "16px 18px",
        cursor: "pointer",
        marginBottom: 8
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        flex: 1,
        minWidth: 0
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        display: "flex",
        alignItems: "baseline",
        gap: 8
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        fontSize: 16,
        fontWeight: 700
      }
    }, r.label), /*#__PURE__*/React.createElement("span", {
      className: "ph-num",
      style: {
        fontSize: 12.5,
        color: "var(--text-muted)",
        fontFamily: "var(--font-num)"
      }
    }, r.count, "\uAC74")), /*#__PURE__*/React.createElement("div", {
      style: {
        fontSize: 13,
        color: "var(--text-secondary)",
        marginTop: 2
      }
    }, r.desc)), /*#__PURE__*/React.createElement(Money, {
      s: 17
    }, won(r.amount)), /*#__PURE__*/React.createElement("span", {
      style: {
        color: "var(--ph-gray-400)",
        display: "inline-flex"
      }
    }, Ic(CH_R))))), /*#__PURE__*/React.createElement("div", {
      style: {
        marginTop: 8
      }
    }, e.rows.map((r, i) => /*#__PURE__*/React.createElement("div", {
      key: i,
      style: {
        display: "flex",
        alignItems: "flex-start",
        padding: "14px 0",
        borderBottom: "1px solid var(--border-hairline)"
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        flex: 1,
        minWidth: 0
      }
    }, /*#__PURE__*/React.createElement("div", {
      className: "ph-num",
      style: {
        fontSize: 13,
        color: "var(--text-muted)",
        fontFamily: "var(--font-num)"
      }
    }, r.date), /*#__PURE__*/React.createElement("div", {
      style: {
        fontSize: 16,
        fontWeight: 700,
        marginTop: 4
      }
    }, r.issuer)), /*#__PURE__*/React.createElement("div", {
      style: {
        textAlign: "right"
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        fontSize: 12,
        color: "var(--text-secondary)",
        background: "var(--ph-gray-100)",
        borderRadius: 6,
        padding: "3px 8px"
      }
    }, r.reason), /*#__PURE__*/React.createElement("div", {
      style: {
        marginTop: 8
      }
    }, /*#__PURE__*/React.createElement(Money, {
      s: 16
    }, won(r.amount))))))), /*#__PURE__*/React.createElement("div", {
      style: {
        marginTop: 22
      }
    }, /*#__PURE__*/React.createElement(GreenButton, {
      onClick: () => push({
        name: "unpurchased"
      })
    }, "\uBBF8\uB9E4\uC785 \uB0B4\uC5ED \uBCF4\uB7EC\uAC00\uAE30"))));
  }
  const SCREENS = {
    main: Main,
    premoney: Premoney,
    totalsales: TotalSales,
    costdetail: CostDetail,
    profitdetail: ProfitDetail,
    unpurchased: Unpurchased,
    excluded: Excluded,
    card: CardScreen,
    txn: TxnScreen,
    platform: PlatformScreen,
    order: OrderScreen,
    diff: DiffScreen,
    deposits: DepositsScreen
  };
  function Logo() {
    return /*#__PURE__*/React.createElement("span", {
      style: {
        fontFamily: "var(--font-sans)",
        fontWeight: 700,
        fontSize: 22,
        letterSpacing: "-0.01em",
        lineHeight: 1
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        color: "var(--ph-ink)"
      }
    }, "Pay"), /*#__PURE__*/React.createElement("span", {
      style: {
        color: "var(--ph-green-700)"
      }
    }, "hug"));
  }
  function PayhugApp() {
    const [stack, setStack] = React.useState([{
      name: "main"
    }]);
    const cur = stack[stack.length - 1];
    const push = s => setStack(st => [...st, s]);
    const pop = () => setStack(st => st.length > 1 ? st.slice(0, -1) : st);
    const Screen = SCREENS[cur.name] || Main;
    return /*#__PURE__*/React.createElement("div", {
      style: {
        minHeight: "100vh",
        background: "rgb(250,249,250)",
        display: "flex",
        flexDirection: "column",
        fontFamily: "var(--font-sans)"
      }
    }, /*#__PURE__*/React.createElement("header", {
      style: {
        background: "#fff",
        borderBottom: "1px solid var(--border-hairline)",
        padding: "0 28px",
        height: 64,
        display: "flex",
        alignItems: "center",
        flex: "none"
      }
    }, /*#__PURE__*/React.createElement(Logo, null)), /*#__PURE__*/React.createElement("main", {
      style: {
        flex: 1,
        display: "flex",
        justifyContent: "center",
        padding: "24px 16px 56px"
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        width: "100%",
        maxWidth: 440
      }
    }, /*#__PURE__*/React.createElement(Screen, {
      params: cur,
      push: push,
      pop: pop
    }))));
  }
  window.PHPayhugApp = PayhugApp;
})();
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/payhug_app/PayhugApp.jsx", error: String((e && e.message) || e) }); }

// ui_kits/payhug_app/appData.js
try { (() => {
// PayHug app — data (수정.fig 기준). today = 2026-06-24 (수). 최종 업데이트 06/24 11:30.
// 6/25 이후 = 0원(데이터 없음). 매출/비용/수익 월별 달력 + 미매입 내역.
// Exposes window.PHAPP.
(function () {
  const store = {
    name: "잇잇",
    status: "승인완료",
    biz: "616-28-53422"
  };
  const UPDATE = "최종 업데이트 2026년 06월 24일 11:30";

  // 미리 받는 돈 (오늘 6/24, 어제 6/23 매출 기준)
  const premoney = {
    dateLabel: "26년 6월 24일 (수)",
    today: true,
    reflectedAt: UPDATE,
    total: 488086,
    yesterdaySales: 818800,
    cards: [{
      key: "kb",
      name: "KB카드",
      count: 6,
      amount: 102366
    }, {
      key: "nh",
      name: "농협NH카드",
      count: 3,
      amount: 41283
    }, {
      key: "lotte",
      name: "롯데카드",
      count: 0,
      amount: 0
    }, {
      key: "bc",
      name: "비씨카드",
      count: 3,
      amount: 50193
    }, {
      key: "woori",
      name: "우리카드",
      count: 0,
      amount: 0
    }, {
      key: "hana",
      name: "하나카드",
      count: 1,
      amount: 15246
    }, {
      key: "shinhan",
      name: "신한카드",
      count: 2,
      amount: 20691
    }, {
      key: "samsung",
      name: "삼성카드",
      count: 0,
      amount: 0
    }, {
      key: "hyundai",
      name: "현대카드",
      count: 1,
      amount: 24156
    }],
    cardsTotal: 253935,
    platforms: [{
      key: "baemin",
      name: "배달의 민족",
      count: 11,
      amount: 255514
    }, {
      key: "coupang",
      name: "쿠팡이츠",
      count: 8,
      amount: 56628
    }, {
      key: "yogiyo",
      name: "요기요",
      count: 1,
      amount: 26752
    }],
    platformsTotal: 338894,
    payhug: {
      total: -104743,
      expectedDiff: -104743
    }
  };

  // 총 매출액 (달력 날짜 클릭 시 = 어제/특정일 매출 상세). 선정산 제외액 = 미매입 합.
  const totalSales = {
    dateLabel: "26년 6월 23일 (화)",
    reflectedAt: UPDATE,
    total: 818800,
    excludedTotal: 83641,
    cards: premoney.cards,
    cardsTotal: premoney.cardsTotal,
    platforms: premoney.platforms,
    platformsTotal: premoney.platformsTotal
  };

  // 미매입 내역 (카드 승인 후 카드사 매입 대기). 매입완료되면 총 매출에 가산. (status: done | pending)
  const unpurchased = {
    date: "2026.06.16",
    total: 83641,
    note: "카드 승인 이후 아직 카드사에서 매입 처리되지 않은 내역입니다.",
    rows: [{
      date: "2026.06.14",
      issuer: "삼성카드",
      apprv: "98231264",
      amount: 13796,
      status: "done"
    }, {
      date: "2026.06.13",
      issuer: "삼성카드",
      apprv: "60702295",
      amount: 22232,
      status: "pending"
    }, {
      date: "2026.06.06",
      issuer: "하나카드",
      apprv: "00283649",
      amount: 21212,
      status: "pending"
    }, {
      date: "2026.06.06",
      issuer: "삼성카드",
      apprv: "14921793",
      amount: 26401,
      status: "pending"
    }]
  };

  // 선정산 제외액 내역 (= 이번 선정산에서 빠진 금액). 미매입 내역과는 별개 화면.
  const excludedDetail = {
    date: "2026.06.16",
    total: 83641,
    note: "이번 선정산에서 제외된 금액이에요.\n아직 카드 매입이 완료되지 않아 빠졌고, 매입이 확인되면 다음 선정산 금액에 자동으로 포함돼요.",
    reasons: [{
      key: "unpurchased",
      label: "미매입",
      desc: "카드 매입 대기",
      count: 4,
      amount: 83641
    }],
    rows: unpurchased.rows.map(r => ({
      date: r.date,
      issuer: r.issuer,
      reason: "카드 매입 대기",
      amount: r.amount
    }))
  };
  const PAY_METHOD = "신용";
  const cardExtra = {
    kb: {
      count: 1,
      amount: 2739
    },
    samsung: {
      count: 1,
      amount: 13796
    }
  };
  function cardTxns(key) {
    const c = premoney.cards.find(x => x.key === key);
    if (!c || c.count === 0) return {
      card: c,
      txns: [],
      summary: null
    };
    const per = Math.round(c.amount / c.count);
    const txns = [];
    let salesSum = 0,
      feeSum = 0;
    for (let i = 0; i < c.count; i++) {
      const net = i === c.count - 1 ? c.amount - per * (c.count - 1) : per;
      const sales = Math.round(net / 0.99);
      const fee = -(sales - net);
      salesSum += sales;
      feeSum += fee;
      txns.push({
        apprv: String(20000000 + (i + 3) * 1300457 % 79999999),
        time: `1${i}:0${i}`,
        sales,
        fee,
        net,
        payType: i % 2 === 0 ? "신용" : "체크"
      });
    }
    const add = cardExtra[key] || null;
    const summary = {
      yesterdaySales: salesSum,
      fee: feeSum,
      premoney: c.amount,
      addPurchase: add
    };
    return {
      card: c,
      txns,
      summary
    };
  }
  const platformDetail = {
    baemin: {
      name: "배달의 민족",
      yesterdaySales: 397300,
      deductTotal: -141786,
      deducts: [["배달의 민족 차감액", -110698], ["광고비", -31088, "help"], ["페이허그 수수료", "면제"]],
      excluded: {
        count: 1,
        amount: 2889
      },
      premoney: 255514,
      orders: [{
        shop: "잇잇",
        date: "2026.06.23",
        time: "13:47",
        amount: 13443,
        pay: "바로결제"
      }, {
        shop: "국밥보스 제육대장 시청점",
        date: "2026.06.23",
        time: "13:23",
        amount: 8156,
        pay: "바로결제"
      }, {
        shop: "국밥보스 제육대장 시청점",
        date: "2026.06.23",
        time: "11:31",
        amount: -898,
        pay: "만나서 결제"
      }, {
        shop: "Boss 짬뽕 직화제육 시청점",
        date: "2026.06.23",
        time: "11:12",
        amount: 7274,
        pay: "바로결제"
      }, {
        shop: "Boss 짬뽕 직화제육 시청점",
        date: "2026.06.23",
        time: "10:31",
        amount: 7714,
        pay: "바로결제"
      }, {
        shop: "Boss 짬뽕 직화제육 시청점",
        date: "2026.06.23",
        time: "10:24",
        amount: 7852,
        pay: "바로결제"
      }]
    },
    coupang: {
      name: "쿠팡이츠",
      yesterdaySales: 61200,
      deductTotal: -4572,
      deducts: [["쿠팡이츠 차감액", -4572], ["페이허그 수수료", "면제"]],
      excluded: null,
      premoney: 56628,
      orders: []
    },
    yogiyo: {
      name: "요기요",
      yesterdaySales: 28900,
      deductTotal: -2148,
      deducts: [["요기요 차감액", -2148], ["페이허그 수수료", "면제"]],
      excluded: null,
      premoney: 26752,
      orders: []
    }
  };
  const orderDetail = {
    name: "배달의 민족",
    date: "2026.06.23",
    time: "11:31",
    amount: -898,
    orderNo: "B2DR004ZYJ",
    pay: "만나서 결제",
    yesterdaySales: "(14,900원)",
    deductTotal: -898,
    deducts: [["배달의 민족 차감액", -898], ["페이허그 수수료", "면제"]],
    premoney: -898,
    note: "[만나서 결제]는 배달의 민족 선정산 대상이 아니며 매출액에서 제외돼요\n[배민원 주문]의 매출액은 고객의 배달팁이 제외된 금액이에요"
  };
  const expectedDiff = {
    dateLabel: "2026.06.24 반영",
    total: -104743,
    note: "선정산은 예상 카드 수수료율을 기준으로 지급돼요.\n실제 정산 후 발생한 차액은 다음 선정산 금액에 자동으로 반영돼요.",
    rows: [{
      date: "2026.06.22",
      issuer: "비씨카드",
      no: "승인번호 71864578",
      amount: 52
    }, {
      date: "2026.06.22",
      issuer: "비씨카드",
      no: "승인번호 75903426",
      amount: 85
    }, {
      date: "2026.06.22",
      issuer: "하나카드",
      no: "승인번호 21804005",
      amount: 10
    }, {
      date: "2026.06.22",
      issuer: "하나카드",
      no: "승인번호 27800203",
      amount: 28
    }, {
      date: "2026.06.22",
      issuer: "배달의 민족",
      no: "주문번호 T2DQ00008CVO",
      amount: -5100
    }, {
      date: "2026.06.22",
      issuer: "배달의 민족",
      no: "주문번호 T2DQ0000B20S",
      amount: -5617
    }, {
      date: "2026.06.20",
      issuer: "배달의 민족",
      no: "주문번호 B2DQ004BI9",
      amount: 2138
    }]
  };
  const deposits = {
    bank: "하나은행",
    account: "62291002003804",
    rows: [{
      date: "6.24",
      time: "11:30",
      amount: 488086,
      kind: "premoney"
    }, {
      date: "6.23",
      time: "11:30",
      amount: 766796,
      kind: "premoney"
    }, {
      date: "",
      time: "14:30",
      amount: 83641,
      kind: "excluded"
    }, {
      date: "6.22",
      time: "11:30",
      amount: 460958,
      kind: "premoney"
    }, {
      date: "6.21",
      time: "11:30",
      amount: 533110,
      kind: "premoney"
    }, {
      date: "6.20",
      time: "11:30",
      amount: 587,
      kind: "premoney"
    }, {
      date: "6.19",
      time: "11:30",
      amount: 771333,
      kind: "premoney"
    }]
  };
  const calDays = {};
  for (let d = 1; d <= 24; d++) {
    const k = d * 2654435761 >>> 0;
    const f = n => (k >>> n & 0x3ff) / 0x3ff;
    let cardSales = 90000 + Math.round(f(2) * 130000 / 100) * 100;
    let delivSales = d % 6 === 0 ? Math.round((40000 + f(7) * 55000) / 100) * 100 : 70000 + Math.round(f(11) * 160000 / 100) * 100;
    if (d === 23) {
      cardSales = 480000;
      delivSales = 338800;
    }
    const cardFee = Math.round(cardSales * 0.011 / 10) * 10;
    const delivFee = delivSales ? Math.round(delivSales * 0.12 / 10) * 10 : 0;
    const adFee = delivSales ? Math.round(delivSales * 0.05 / 10) * 10 : 0;
    calDays[d] = {
      cardSales,
      delivSales,
      cardFee,
      delivFee,
      adFee
    };
  }
  const sum = sel => Object.values(calDays).reduce((a, x) => a + sel(x), 0);
  function dayMetrics(x) {
    if (!x) return null;
    const cardCost = x.cardFee;
    const delivCost = x.delivFee + x.adFee;
    const cardProfit = x.cardSales - cardCost;
    const delivProfit = x.delivSales - delivCost;
    return {
      cardSales: x.cardSales,
      delivSales: x.delivSales,
      sales: x.cardSales + x.delivSales,
      cardFee: x.cardFee,
      delivFee: x.delivFee,
      adFee: x.adFee,
      cardCost,
      delivCost,
      cost: cardCost + delivCost,
      cardProfit,
      delivProfit,
      profit: cardProfit + delivProfit
    };
  }
  const monthly = {
    cardSales: sum(x => x.cardSales),
    delivSales: sum(x => x.delivSales),
    cardFee: sum(x => x.cardFee),
    delivFee: sum(x => x.delivFee),
    adFee: sum(x => x.adFee)
  };
  monthly.sales = monthly.cardSales + monthly.delivSales;
  monthly.cardCost = monthly.cardFee;
  monthly.delivCost = monthly.delivFee + monthly.adFee;
  monthly.cost = monthly.cardCost + monthly.delivCost;
  monthly.cardProfit = monthly.cardSales - monthly.cardCost;
  monthly.delivProfit = monthly.delivSales - monthly.delivCost;
  monthly.profit = monthly.cardProfit + monthly.delivProfit;
  const salesCalendar = {
    year: 2026,
    month: 6,
    today: 24,
    label: "2026년 6월",
    days: calDays,
    monthly
  };
  window.PHAPP = {
    store,
    premoney,
    totalSales,
    unpurchased,
    excludedDetail,
    platformDetail,
    orderDetail,
    cardTxns,
    PAY_METHOD,
    expectedDiff,
    deposits,
    salesCalendar,
    dayMetrics,
    UPDATE
  };
})();
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/payhug_app/appData.js", error: String((e && e.message) || e) }); }

__ds_ns.Avatar = __ds_scope.Avatar;

__ds_ns.Badge = __ds_scope.Badge;

__ds_ns.Button = __ds_scope.Button;

__ds_ns.Card = __ds_scope.Card;

__ds_ns.StatTile = __ds_scope.StatTile;

__ds_ns.SalesBreakdown = __ds_scope.SalesBreakdown;

__ds_ns.SalesCalendar = __ds_scope.SalesCalendar;

__ds_ns.AlertBanner = __ds_scope.AlertBanner;

__ds_ns.Checkbox = __ds_scope.Checkbox;

__ds_ns.Input = __ds_scope.Input;

__ds_ns.Select = __ds_scope.Select;

__ds_ns.SegmentedTabs = __ds_scope.SegmentedTabs;

__ds_ns.SidebarNav = __ds_scope.SidebarNav;

__ds_ns.Tabs = __ds_scope.Tabs;

})();
