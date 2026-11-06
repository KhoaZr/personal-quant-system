import apiClient from "../api/client";

export const DEFAULT_BACKTEST_PARAMS = {
  symbol: "FPT.VN",
  start_date: "",
  end_date: "",
  initial_capital: 100000000,
  risk_per_trade: 0.02,
  fee_rate: 0.0015,
  slippage: 0.001,
};

/**
 * Gọi API thực thi kiểm thử chiến lược định lượng.
 * @param {Object} params Tham số cấu hình backtest
 * @returns {Promise<Object>} Kết quả phân tích backtest
 */
export const runBacktest = async (params) => {
  // Chuẩn hóa payload: bỏ start_date / end_date nếu rỗng
  const payload = {
    symbol: params.symbol.trim().toUpperCase(),
    initial_capital: Number(params.initial_capital),
    fee_rate: Number(params.fee_rate),
    slippage: Number(params.slippage),
    risk_per_trade: Number(params.risk_per_trade),
  };

  if (params.start_date) {
    payload.start_date = params.start_date;
  }
  if (params.end_date) {
    payload.end_date = params.end_date;
  }

  const response = await apiClient.post("/backtest/run", payload);
  return response.data;
};

/**
 * Định dạng tiền tệ VND đầy đủ
 */
export const formatCurrency = (val) => {
  if (val === null || val === undefined || isNaN(val)) return "0 ₫";
  return new Intl.NumberFormat("vi-VN", {
    style: "currency",
    currency: "VND",
    maximumFractionDigits: 0,
  }).format(val);
};

/**
 * Định dạng tiền tệ gọn gàng (triệu / tỷ)
 */
export const formatCompactCurrency = (val) => {
  if (val === null || val === undefined || isNaN(val)) return "0";
  const abs = Math.abs(val);
  if (abs >= 1_000_000_000) {
    return `${(val / 1_000_000_000).toFixed(2)} tỷ`;
  }
  if (abs >= 1_000_000) {
    return `${(val / 1_000_000).toFixed(1)} tr`;
  }
  return Number(val).toLocaleString("vi-VN");
};

/**
 * Định dạng tỷ lệ phần trăm
 */
export const formatPercent = (val, showSign = true) => {
  if (val === null || val === undefined || isNaN(val)) return "0.00%";
  const num = Number(val);
  const formatted = `${num >= 0 && showSign ? "+" : ""}${num.toFixed(2)}%`;
  return formatted;
};

/**
 * Xuất danh sách nhật ký lệnh ra file CSV tải về trình duyệt
 */
export const exportTradesToCSV = (trades, symbol = "BACKTEST") => {
  if (!trades || trades.length === 0) return;

  const headers = [
    "Ma_CP",
    "Ngay_Mua",
    "Ngay_Ban",
    "Loai_Lenh",
    "Gia_Vao",
    "Gia_Ra",
    "Khoi_Luong",
    "Lai_Lo_VND",
    "Phan_Tram_Loi_Nhuan",
    "Ly_Do_Dong",
  ];

  const rows = trades.map((t) => [
    symbol,
    t.entry_date,
    t.exit_date,
    t.action,
    t.entry_price,
    t.exit_price,
    t.shares,
    t.pnl,
    `${t.return_pct}%`,
    t.exit_reason,
  ]);

  const csvContent =
    "data:text/csv;charset=utf-8,\uFEFF" +
    [headers.join(","), ...rows.map((e) => e.join(","))].join("\n");

  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute(
    "download",
    `trade_log_${symbol}_${new Date().toISOString().slice(0, 10)}.csv`
  );
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};
