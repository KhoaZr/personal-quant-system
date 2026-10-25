
import axios from "axios";

const apiClient = axios.create({
  baseURL: "http://127.0.0.1:8000/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
});

export const quantAPI = {
  // Lấy danh sách cổ phiếu
  getStocks: () => apiClient.get("/stocks/"),

  // Thu thập dữ liệu giá cổ phiếu
  collectPrices: (symbols, period = "1mo") =>
    apiClient.post("/stocks/collect", {
      symbols,
      period,
    }),

  // Tính toán các chỉ báo kỹ thuật
  calculateIndicators: (symbols) =>
    apiClient.post("/indicators/calculate", {
      symbols,
    }),

  // Dự đoán tín hiệu
  predictSignals: (symbols) =>
    apiClient.post("/predictions/predict", {
      symbols,
    }),

  // Tạo tín hiệu và kế hoạch giao dịch
  generateTradePlans: (symbols, account_risk_limit = 500) =>
    apiClient.post("/trades/generate-signals", {
      symbols,
      account_risk_limit,
    }),

  // Lấy danh sách giao dịch giả lập đang mở
  getOpenPaperTrades: () =>
    apiClient.get("/paper-trades/open-trades"),

  // Mở giao dịch giả lập
  openPaperTrade: (tradeData) =>
    apiClient.post("/paper-trades/open", tradeData),

  // Đóng giao dịch giả lập
  closePaperTrade: (tradeData) =>
    apiClient.post("/paper-trades/close", tradeData),
};

export default apiClient;
