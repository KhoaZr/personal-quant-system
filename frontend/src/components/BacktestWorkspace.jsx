import { useState, useMemo } from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceLine,
} from "recharts";
import {
  Play,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  Activity,
  Award,
  Target,
  DollarSign,
  Wallet,
  Download,
  Search,
  Filter,
  RotateCcw,
  Sparkles,
  Layers,
  ShieldAlert,
} from "lucide-react";
import {
  runBacktest,
  DEFAULT_BACKTEST_PARAMS,
  formatCurrency,
  formatCompactCurrency,
  formatPercent,
  exportTradesToCSV,
} from "../services/backtestService";

const QUICK_SYMBOLS = ["FPT.VN", "TCB.VN", "VIC.VN", "VNM.VN", "HPG.VN", "MWG.VN", "SSI.VN"];

export const BacktestWorkspace = () => {
  const [params, setParams] = useState({ ...DEFAULT_BACKTEST_PARAMS });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  // Bộ lọc nhật ký lệnh
  const [tradeFilter, setTradeFilter] = useState("ALL"); // ALL, WIN, LOSS, TAKE_PROFIT, STOP_LOSS
  const [tradeSearch, setTradeSearch] = useState("");
  const [chartView, setChartView] = useState("DUAL"); // DUAL, EQUITY_ONLY, DRAWDOWN_ONLY

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const data = await runBacktest(params);
      setResult(data);
    } catch (err) {
      console.error("Backtest execution error:", err);
      const msg =
        err.response?.data?.detail ||
        err.message ||
        "Có lỗi xảy ra khi thực hiện kiểm thử chiến lược định lượng.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleResetParams = () => {
    setParams({ ...DEFAULT_BACKTEST_PARAMS });
  };

  const handleQuickSymbol = (sym) => {
    setParams((prev) => ({ ...prev, symbol: sym }));
  };

  // Lọc danh sách lệnh theo tìm kiếm và tab phân loại
  const filteredTrades = useMemo(() => {
    if (!result || !result.trades) return [];

    return result.trades.filter((t) => {
      // Bộ lọc theo kết quả/lý do
      if (tradeFilter === "WIN" && t.pnl <= 0) return false;
      if (tradeFilter === "LOSS" && t.pnl > 0) return false;
      if (tradeFilter === "TAKE_PROFIT" && t.exit_reason !== "TAKE_PROFIT") return false;
      if (tradeFilter === "STOP_LOSS" && t.exit_reason !== "STOP_LOSS") return false;

      // Bộ lọc theo từ khóa tìm kiếm (ngày vào, ngày ra, lý do đóng)
      if (tradeSearch.trim()) {
        const query = tradeSearch.toLowerCase().trim();
        const matchDate =
          t.entry_date?.toLowerCase().includes(query) ||
          t.exit_date?.toLowerCase().includes(query);
        const matchReason = t.exit_reason?.toLowerCase().includes(query);
        if (!matchDate && !matchReason) return false;
      }

      return true;
    });
  }, [result, tradeFilter, tradeSearch]);

  // Thống kê nhanh các lệnh sau khi lọc
  const filteredStats = useMemo(() => {
    if (!filteredTrades.length) return null;
    const wins = filteredTrades.filter((t) => t.pnl > 0);
    const losses = filteredTrades.filter((t) => t.pnl < 0);
    const totalPnl = filteredTrades.reduce((sum, t) => sum + t.pnl, 0);
    const avgPnl = totalPnl / filteredTrades.length;
    const maxWin = wins.length ? Math.max(...wins.map((t) => t.pnl)) : 0;
    const maxLoss = losses.length ? Math.min(...losses.map((t) => t.pnl)) : 0;

    return {
      count: filteredTrades.length,
      winRate: ((wins.length / filteredTrades.length) * 100).toFixed(1),
      avgPnl,
      maxWin,
      maxLoss,
      totalPnl,
    };
  }, [filteredTrades]);

  // Tính số ngày nắm giữ của lệnh
  const calcHoldingDays = (entryDate, exitDate) => {
    if (!entryDate || !exitDate) return "-";
    const start = new Date(entryDate);
    const end = new Date(exitDate);
    const diffTime = Math.abs(end - start);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return `${diffDays} ngày`;
  };

  return (
    <div className="space-y-6">
      {/* 1. CONTROL PANEL - BẢNG ĐIỀU KHIỂN & CẤU HÌNH THAM SỐ CHIẾN LƯỢC */}
      <section className="relative overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/90 p-6 shadow-2xl backdrop-blur-md">
        {/* Ambient Top Glow */}
        <div className="pointer-events-none absolute -top-24 left-1/4 h-48 w-96 rounded-full bg-indigo-500/10 blur-3xl" />

        <div className="mb-6 flex flex-col justify-between gap-4 md:flex-row md:items-center">
          <div>
            <div className="flex items-center gap-2">
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600/20 text-indigo-400 border border-indigo-500/30">
                <Activity size={18} />
              </span>
              <h2 className="text-xl font-bold tracking-tight text-white">
                Cấu Hình Chiến Lược Backtest
              </h2>
              <span className="rounded-full bg-indigo-500/10 px-2.5 py-0.5 text-xs font-semibold text-indigo-300 border border-indigo-500/20">
                RSI + SMA20 + ATR Engine
              </span>
            </div>
            <p className="mt-1 text-xs text-slate-400">
              Kiểm thử quy tắc giao dịch định lượng, quản trị rủi ro trên quy mô vốn và chi phí thực tế.
            </p>
          </div>

          {/* Quick Symbol Chips */}
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-xs text-slate-400 mr-1 flex items-center gap-1">
              <Sparkles size={13} className="text-amber-400" /> Mã mẫu:
            </span>
            {QUICK_SYMBOLS.map((sym) => (
              <button
                key={sym}
                type="button"
                onClick={() => handleQuickSymbol(sym)}
                className={`rounded-md px-2.5 py-1 text-xs font-mono font-medium transition ${
                  params.symbol === sym
                    ? "bg-indigo-600 text-white shadow-sm ring-1 ring-indigo-400"
                    : "bg-slate-800/80 text-slate-300 hover:bg-slate-700 hover:text-white border border-slate-700/60"
                }`}
              >
                {sym}
              </button>
            ))}
          </div>
        </div>

        {/* Form nhập tham số */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6">
            {/* Mã Cổ Phiếu */}
            <div>
              <label className="block text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
                MÃ CỔ PHIẾU
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={params.symbol}
                  onChange={(e) =>
                    setParams({ ...params, symbol: e.target.value.toUpperCase() })
                  }
                  placeholder="VD: FPT.VN"
                  className="w-full rounded-xl border border-slate-700 bg-slate-950/80 px-3.5 py-2.5 font-mono text-sm font-semibold text-white uppercase placeholder-slate-600 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                  required
                />
              </div>
            </div>

            {/* Vốn Ban Đầu */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                  VỐN BAN ĐẦU (VND)
                </label>
                <span className="text-[10px] font-mono text-indigo-400">
                  {formatCompactCurrency(params.initial_capital)}
                </span>
              </div>
              <input
                type="number"
                value={params.initial_capital}
                onChange={(e) =>
                  setParams({ ...params, initial_capital: Number(e.target.value) })
                }
                step="5000000"
                min="1000000"
                className="w-full rounded-xl border border-slate-700 bg-slate-950/80 px-3.5 py-2.5 text-sm text-white font-mono outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                required
              />
            </div>

            {/* Hạn Mức Rủi Ro / Lệnh */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                  RỦI RO / LỆNH
                </label>
                <span className="text-[10px] font-mono text-sky-400">
                  {(params.risk_per_trade * 100).toFixed(1)}% Vốn
                </span>
              </div>
              <input
                type="number"
                value={params.risk_per_trade}
                onChange={(e) =>
                  setParams({ ...params, risk_per_trade: Number(e.target.value) })
                }
                step="0.005"
                min="0.005"
                max="0.2"
                className="w-full rounded-xl border border-slate-700 bg-slate-950/80 px-3.5 py-2.5 text-sm text-white font-mono outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                required
              />
            </div>

            {/* Phí Giao Dịch */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                  PHÍ GD (MỖI CHIỀU)
                </label>
                <span className="text-[10px] font-mono text-emerald-400">
                  {(params.fee_rate * 100).toFixed(2)}%
                </span>
              </div>
              <input
                type="number"
                value={params.fee_rate}
                onChange={(e) =>
                  setParams({ ...params, fee_rate: Number(e.target.value) })
                }
                step="0.0005"
                min="0"
                max="0.02"
                className="w-full rounded-xl border border-slate-700 bg-slate-950/80 px-3.5 py-2.5 text-sm text-white font-mono outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                required
              />
            </div>

            {/* Độ Trượt Giá */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                  TRƯỢT GIÁ (SLIPPAGE)
                </label>
                <span className="text-[10px] font-mono text-amber-400">
                  {(params.slippage * 100).toFixed(2)}%
                </span>
              </div>
              <input
                type="number"
                value={params.slippage}
                onChange={(e) =>
                  setParams({ ...params, slippage: Number(e.target.value) })
                }
                step="0.0005"
                min="0"
                max="0.05"
                className="w-full rounded-xl border border-slate-700 bg-slate-950/80 px-3.5 py-2.5 text-sm text-white font-mono outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                required
              />
            </div>

            {/* Nút Thực Thi */}
            <div className="flex items-end gap-2">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-500 px-4 py-2.5 font-semibold text-white shadow-lg shadow-indigo-600/30 transition hover:from-indigo-500 hover:to-indigo-400 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50 flex items-center justify-center gap-2 text-sm"
              >
                {loading ? (
                  <>
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                    <span>Đang tính...</span>
                  </>
                ) : (
                  <>
                    <Play size={16} fill="white" />
                    <span>Chạy Backtest</span>
                  </>
                )}
              </button>

              <button
                type="button"
                onClick={handleResetParams}
                title="Khôi phục mặc định"
                className="rounded-xl border border-slate-700 bg-slate-800 p-2.5 text-slate-400 transition hover:bg-slate-700 hover:text-white"
              >
                <RotateCcw size={16} />
              </button>
            </div>
          </div>

          {/* Dải thời gian tùy chọn (Start Date / End Date) */}
          <div className="flex flex-wrap items-center gap-3 pt-2 text-xs text-slate-400 border-t border-slate-800/80">
            <span className="font-medium text-slate-300">Khung thời gian (Tùy chọn):</span>
            <div className="flex items-center gap-2">
              <span className="text-[11px]">Từ:</span>
              <input
                type="date"
                value={params.start_date || ""}
                onChange={(e) => setParams({ ...params, start_date: e.target.value })}
                className="rounded-lg border border-slate-700 bg-slate-950 px-2.5 py-1 text-slate-200 outline-none focus:border-indigo-500"
              />
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[11px]">Đến:</span>
              <input
                type="date"
                value={params.end_date || ""}
                onChange={(e) => setParams({ ...params, end_date: e.target.value })}
                className="rounded-lg border border-slate-700 bg-slate-950 px-2.5 py-1 text-slate-200 outline-none focus:border-indigo-500"
              />
            </div>
            {(params.start_date || params.end_date) && (
              <button
                type="button"
                onClick={() => setParams({ ...params, start_date: "", end_date: "" })}
                className="text-xs text-indigo-400 hover:text-indigo-300 underline"
              >
                Dùng toàn bộ lịch sử
              </button>
            )}
          </div>
        </form>

        {/* Thông báo lỗi nếu có */}
        {error && (
          <div className="mt-5 flex items-start gap-3 rounded-xl border border-red-500/30 bg-red-950/40 p-4 text-sm text-red-200">
            <ShieldAlert size={20} className="shrink-0 text-red-400 mt-0.5" />
            <div className="flex-1">
              <p className="font-semibold text-red-300">Không thể thực thi kiểm thử:</p>
              <p className="mt-0.5 text-xs text-red-200/90">{error}</p>
              <p className="mt-2 text-[11px] text-red-400">
                Gợi ý: Hãy thử chọn các mã cổ phiếu đã có dữ liệu sẵn trong database như{" "}
                <button
                  type="button"
                  onClick={() => handleQuickSymbol("FPT.VN")}
                  className="font-bold underline"
                >
                  FPT.VN
                </button>{" "}
                hoặc{" "}
                <button
                  type="button"
                  onClick={() => handleQuickSymbol("TCB.VN")}
                  className="font-bold underline"
                >
                  TCB.VN
                </button>
                , hoặc thu thập thêm giá từ Daily Pipeline.
              </p>
            </div>
          </div>
        )}
      </section>

      {/* 2. KHU VỰC KẾT QUẢ KIỂM THỬ */}
      {result ? (
        <div className="space-y-6">
          {/* HÀNG THẺ CHỈ SỐ QUANT HIỆU NĂNG CAO (6 KPI CARDS) */}
          <section className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
            {/* 1. Tổng Lợi Nhuận */}
            <div className="group relative overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/80 p-4 transition hover:border-slate-700 hover:shadow-lg">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span className="font-medium">TỔNG LỢI NHUẬN</span>
                {result.total_return_pct >= 0 ? (
                  <TrendingUp size={16} className="text-emerald-400" />
                ) : (
                  <TrendingDown size={16} className="text-rose-400" />
                )}
              </div>
              <p
                className={`mt-2 font-mono text-2xl font-bold tracking-tight ${
                  result.total_return_pct >= 0 ? "text-emerald-400" : "text-rose-400"
                }`}
              >
                {formatPercent(result.total_return_pct)}
              </p>
              <div className="mt-1 flex items-center justify-between text-[11px]">
                <span className="text-slate-500">CAGR:</span>
                <span
                  className={`font-semibold ${
                    result.annualized_return_pct >= 0 ? "text-emerald-400" : "text-rose-400"
                  }`}
                >
                  {formatPercent(result.annualized_return_pct)}/năm
                </span>
              </div>
            </div>

            {/* 2. Sharpe Ratio */}
            <div className="group relative overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/80 p-4 transition hover:border-slate-700 hover:shadow-lg">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span className="font-medium">SHARPE RATIO</span>
                <Award size={16} className="text-indigo-400" />
              </div>
              <p className="mt-2 font-mono text-2xl font-bold tracking-tight text-white">
                {result.sharpe_ratio}
              </p>
              <div className="mt-1 flex items-center justify-between text-[11px]">
                <span className="text-slate-500">Sortino:</span>
                <span className="font-semibold text-slate-300">{result.sortino_ratio}</span>
              </div>
            </div>

            {/* 3. Max Drawdown */}
            <div className="group relative overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/80 p-4 transition hover:border-slate-700 hover:shadow-lg">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span className="font-medium">MAX DRAWDOWN</span>
                <AlertTriangle size={16} className="text-rose-400" />
              </div>
              <p className="mt-2 font-mono text-2xl font-bold tracking-tight text-rose-400">
                {result.max_drawdown_pct}%
              </p>
              <div className="mt-1 flex items-center justify-between text-[11px]">
                <span className="text-slate-500">Mức sụt tối đa:</span>
                <span className="text-rose-300 font-medium">Đỉnh - Đáy</span>
              </div>
            </div>

            {/* 4. Win Rate */}
            <div className="group relative overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/80 p-4 transition hover:border-slate-700 hover:shadow-lg">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span className="font-medium">TỶ LỆ THẮNG</span>
                <Target size={16} className="text-sky-400" />
              </div>
              <p className="mt-2 font-mono text-2xl font-bold tracking-tight text-sky-400">
                {result.win_rate_pct}%
              </p>
              <div className="mt-1 flex items-center justify-between text-[11px]">
                <span className="text-emerald-400 font-medium">{result.winning_trades} Thắng</span>
                <span className="text-slate-600">/</span>
                <span className="text-rose-400 font-medium">{result.losing_trades} Thua</span>
              </div>
            </div>

            {/* 5. Profit Factor */}
            <div className="group relative overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/80 p-4 transition hover:border-slate-700 hover:shadow-lg">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span className="font-medium">PROFIT FACTOR</span>
                <DollarSign size={16} className="text-amber-400" />
              </div>
              <p className="mt-2 font-mono text-2xl font-bold tracking-tight text-amber-400">
                {result.profit_factor}
              </p>
              <div className="mt-1 flex items-center justify-between text-[11px]">
                <span className="text-slate-500">Tổng Lãi / Lỗ:</span>
                <span className="font-semibold text-slate-300">
                  {result.profit_factor >= 1.5 ? "Chiến lược Tốt" : "Trung bình"}
                </span>
              </div>
            </div>

            {/* 6. Vốn Cuối Cùng */}
            <div className="group relative overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/80 p-4 transition hover:border-slate-700 hover:shadow-lg">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span className="font-medium">VỐN CUỐI CÙNG</span>
                <Wallet size={16} className="text-indigo-400" />
              </div>
              <p className="mt-2 font-mono text-xl font-bold tracking-tight text-white truncate">
                {formatCompactCurrency(result.final_equity)}
              </p>
              <div className="mt-1 flex items-center justify-between text-[11px]">
                <span className="text-slate-500">Vốn gốc:</span>
                <span className="text-slate-300 font-mono">
                  {formatCompactCurrency(result.initial_capital)}
                </span>
              </div>
            </div>
          </section>

          {/* 3. BIỂU ĐỒ TRỰC QUAN ĐƯỜNG CONG VỐN VÀ DRAWDOWN */}
          <section className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl backdrop-blur-md">
            {/* Chart Toolbar */}
            <div className="mb-6 flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Layers size={18} className="text-indigo-400" />
                  Đồ Thị Tăng Trưởng Tài Sản & Mức Độ Sụt Giảm
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Mã: <span className="font-mono text-indigo-300 font-semibold">{result.symbol}</span>{" "}
                  • Số điểm dữ liệu:{" "}
                  <span className="font-mono text-slate-200">
                    {result.equity_curve?.length || 0} phiên
                  </span>
                </p>
              </div>

              {/* View Switcher Tabs */}
              <div className="flex items-center rounded-xl border border-slate-800 bg-slate-950 p-1">
                <button
                  type="button"
                  onClick={() => setChartView("DUAL")}
                  className={`rounded-lg px-3 py-1.5 text-xs font-medium transition ${
                    chartView === "DUAL"
                      ? "bg-indigo-600 text-white shadow-sm"
                      : "text-slate-400 hover:text-white"
                  }`}
                >
                  Kết Hợp (Song Song)
                </button>
                <button
                  type="button"
                  onClick={() => setChartView("EQUITY_ONLY")}
                  className={`rounded-lg px-3 py-1.5 text-xs font-medium transition ${
                    chartView === "EQUITY_ONLY"
                      ? "bg-indigo-600 text-white shadow-sm"
                      : "text-slate-400 hover:text-white"
                  }`}
                >
                  Chỉ Đường Vốn
                </button>
                <button
                  type="button"
                  onClick={() => setChartView("DRAWDOWN_ONLY")}
                  className={`rounded-lg px-3 py-1.5 text-xs font-medium transition ${
                    chartView === "DRAWDOWN_ONLY"
                      ? "bg-indigo-600 text-white shadow-sm"
                      : "text-slate-400 hover:text-white"
                  }`}
                >
                  Chỉ Drawdown
                </button>
              </div>
            </div>

            {/* Grid Charts */}
            <div
              className={`grid gap-6 ${
                chartView === "DUAL" ? "grid-cols-1 lg:grid-cols-2" : "grid-cols-1"
              }`}
            >
              {/* Biểu đồ Equity Curve */}
              {(chartView === "DUAL" || chartView === "EQUITY_ONLY") && (
                <div className="rounded-xl border border-slate-800/80 bg-slate-950/60 p-4">
                  <div className="mb-3 flex items-center justify-between">
                    <span className="flex items-center gap-1.5 text-xs font-semibold text-emerald-400">
                      <TrendingUp size={15} /> Đường Cong Tăng Trưởng Vốn (Equity Curve)
                    </span>
                    <span className="text-[11px] font-mono text-slate-400">
                      Gốc: {formatCurrency(result.initial_capital)}
                    </span>
                  </div>

                  <div className={chartView === "EQUITY_ONLY" ? "h-80 w-full" : "h-72 w-full"}>
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart
                        data={result.equity_curve}
                        margin={{ top: 10, right: 15, left: 0, bottom: 0 }}
                      >
                        <defs>
                          <linearGradient id="equityGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#10b981" stopOpacity={0.35} />
                            <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                        <XAxis
                          dataKey="date"
                          stroke="#64748b"
                          tick={{ fontSize: 11 }}
                          tickLine={false}
                        />
                        <YAxis
                          stroke="#64748b"
                          tick={{ fontSize: 11 }}
                          tickLine={false}
                          domain={["dataMin - 1000000", "dataMax + 1000000"]}
                          tickFormatter={(val) => `${(val / 1_000_000).toFixed(0)}tr`}
                        />
                        <Tooltip
                          content={({ active, payload }) => {
                            if (active && payload && payload.length) {
                              const d = payload[0].payload;
                              const pnlVsStart =
                                ((d.equity - result.initial_capital) / result.initial_capital) * 100;
                              return (
                                <div className="rounded-xl border border-slate-700 bg-slate-900/95 p-3 shadow-xl backdrop-blur-md">
                                  <p className="text-xs font-medium text-slate-400">{d.date}</p>
                                  <p className="mt-1 font-mono text-sm font-bold text-white">
                                    {formatCurrency(d.equity)}
                                  </p>
                                  <p
                                    className={`mt-0.5 text-xs font-semibold ${
                                      pnlVsStart >= 0 ? "text-emerald-400" : "text-rose-400"
                                    }`}
                                  >
                                    Hiệu suất: {formatPercent(pnlVsStart)}
                                  </p>
                                  <p className="text-[11px] text-rose-300/80">
                                    Drawdown: {d.drawdown_pct}%
                                  </p>
                                </div>
                              );
                            }
                            return null;
                          }}
                        />
                        <ReferenceLine
                          y={result.initial_capital}
                          stroke="#475569"
                          strokeDasharray="4 4"
                          label={{
                            value: "Vốn ban đầu",
                            fill: "#94a3b8",
                            fontSize: 10,
                            position: "insideTopRight",
                          }}
                        />
                        <Area
                          type="monotone"
                          dataKey="equity"
                          stroke="#10b981"
                          strokeWidth={2.5}
                          fill="url(#equityGradient)"
                          isAnimationActive={true}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}

              {/* Biểu đồ Drawdown */}
              {(chartView === "DUAL" || chartView === "DRAWDOWN_ONLY") && (
                <div className="rounded-xl border border-slate-800/80 bg-slate-950/60 p-4">
                  <div className="mb-3 flex items-center justify-between">
                    <span className="flex items-center gap-1.5 text-xs font-semibold text-rose-400">
                      <AlertTriangle size={15} /> Mức Sụt Giảm Vốn (Drawdown %)
                    </span>
                    <span className="text-[11px] font-mono text-rose-400 font-semibold">
                      MDD: {result.max_drawdown_pct}%
                    </span>
                  </div>

                  <div className={chartView === "DRAWDOWN_ONLY" ? "h-80 w-full" : "h-72 w-full"}>
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart
                        data={result.equity_curve}
                        margin={{ top: 10, right: 15, left: 0, bottom: 0 }}
                      >
                        <defs>
                          <linearGradient id="drawdownGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.4} />
                            <stop offset="95%" stopColor="#f43f5e" stopOpacity={0.02} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                        <XAxis
                          dataKey="date"
                          stroke="#64748b"
                          tick={{ fontSize: 11 }}
                          tickLine={false}
                        />
                        <YAxis
                          stroke="#64748b"
                          tick={{ fontSize: 11 }}
                          tickLine={false}
                          tickFormatter={(val) => `${val}%`}
                        />
                        <Tooltip
                          content={({ active, payload }) => {
                            if (active && payload && payload.length) {
                              const d = payload[0].payload;
                              return (
                                <div className="rounded-xl border border-slate-700 bg-slate-900/95 p-3 shadow-xl backdrop-blur-md">
                                  <p className="text-xs font-medium text-slate-400">{d.date}</p>
                                  <p className="mt-1 font-mono text-sm font-bold text-rose-400">
                                    Drawdown: {d.drawdown_pct}%
                                  </p>
                                  <p className="text-[11px] text-slate-300">
                                    Vốn: {formatCurrency(d.equity)}
                                  </p>
                                </div>
                              );
                            }
                            return null;
                          }}
                        />
                        <Area
                          type="monotone"
                          dataKey="drawdown_pct"
                          stroke="#f43f5e"
                          strokeWidth={2}
                          fill="url(#drawdownGradient)"
                          isAnimationActive={true}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}
            </div>
          </section>

          {/* 4. BẢNG NHẬT KÝ LỆNH CHI TIẾT (TRADE LOG TABLE) */}
          <section className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl backdrop-blur-md">
            {/* Header và Bộ Lọc */}
            <div className="mb-5 flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <span>Nhật Ký Khớp Lệnh Giả Lập</span>
                  <span className="rounded-full bg-slate-800 px-2.5 py-0.5 font-mono text-xs text-indigo-400 border border-slate-700">
                    {result.trades?.length || 0} lệnh
                  </span>
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Theo dõi từng vị thế mua/bán, tỷ lệ lợi nhuận và nguyên nhân kích hoạt đóng lệnh.
                </p>
              </div>

              {/* Thanh Công Cụ & Xuất File */}
              <div className="flex flex-wrap items-center gap-2.5">
                {/* Ô tìm kiếm nhanh */}
                <div className="relative">
                  <Search
                    size={14}
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
                  />
                  <input
                    type="text"
                    placeholder="Tìm theo ngày, lý do..."
                    value={tradeSearch}
                    onChange={(e) => setTradeSearch(e.target.value)}
                    className="w-44 rounded-xl border border-slate-700 bg-slate-950 py-1.5 pl-8 pr-3 text-xs text-white placeholder-slate-500 outline-none transition focus:border-indigo-500 sm:w-56"
                  />
                </div>

                {/* Nút Xuất CSV */}
                <button
                  type="button"
                  onClick={() => exportTradesToCSV(result.trades, result.symbol)}
                  disabled={!result.trades || result.trades.length === 0}
                  className="flex items-center gap-1.5 rounded-xl border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs font-medium text-slate-200 transition hover:bg-slate-700 hover:text-white disabled:cursor-not-allowed disabled:opacity-40"
                >
                  <Download size={14} /> Xuất CSV
                </button>
              </div>
            </div>

            {/* Filter Pills */}
            <div className="mb-4 flex flex-wrap items-center gap-2">
              <span className="text-xs text-slate-400 flex items-center gap-1 mr-1">
                <Filter size={13} /> Lọc:
              </span>
              {[
                { id: "ALL", label: `Tất cả (${result.trades?.length || 0})` },
                { id: "WIN", label: `Lãi (${result.winning_trades})`, color: "text-emerald-400" },
                { id: "LOSS", label: `Lỗ (${result.losing_trades})`, color: "text-rose-400" },
                { id: "TAKE_PROFIT", label: "Take Profit" },
                { id: "STOP_LOSS", label: "Stop Loss" },
              ].map((f) => (
                <button
                  key={f.id}
                  type="button"
                  onClick={() => setTradeFilter(f.id)}
                  className={`rounded-lg px-2.5 py-1 text-xs font-medium transition ${
                    tradeFilter === f.id
                      ? "bg-indigo-600 text-white shadow-sm"
                      : "bg-slate-800/60 text-slate-400 hover:bg-slate-800 hover:text-white border border-slate-700/50"
                  }`}
                >
                  <span className={tradeFilter !== f.id && f.color ? f.color : ""}>
                    {f.label}
                  </span>
                </button>
              ))}
            </div>

            {/* Thống kê nhanh danh sách đã lọc */}
            {filteredStats && (
              <div className="mb-4 grid grid-cols-2 gap-2 rounded-xl bg-slate-950/70 p-3 sm:grid-cols-4 text-xs font-mono border border-slate-800">
                <div>
                  <span className="text-slate-500">Hiển thị: </span>
                  <span className="text-white font-semibold">{filteredStats.count} lệnh</span>
                </div>
                <div>
                  <span className="text-slate-500">Lợi nhuận TB: </span>
                  <span
                    className={`font-semibold ${
                      filteredStats.avgPnl >= 0 ? "text-emerald-400" : "text-rose-400"
                    }`}
                  >
                    {filteredStats.avgPnl >= 0 ? "+" : ""}
                    {formatCurrency(filteredStats.avgPnl)}
                  </span>
                </div>
                <div>
                  <span className="text-slate-500">Thắng lớn nhất: </span>
                  <span className="text-emerald-400 font-semibold">
                    +{formatCurrency(filteredStats.maxWin)}
                  </span>
                </div>
                <div>
                  <span className="text-slate-500">Thua lớn nhất: </span>
                  <span className="text-rose-400 font-semibold">
                    {formatCurrency(filteredStats.maxLoss)}
                  </span>
                </div>
              </div>
            )}

            {/* Bảng Dữ Liệu */}
            <div className="overflow-hidden rounded-xl border border-slate-800">
              <div className="overflow-x-auto max-h-96">
                <table className="w-full text-left text-xs">
                  <thead className="sticky top-0 bg-slate-950/95 text-[11px] uppercase tracking-wider text-slate-400 border-b border-slate-800 backdrop-blur-sm">
                    <tr>
                      <th className="py-3 px-3.5 font-semibold">#</th>
                      <th className="py-3 px-3.5 font-semibold">Ngày Vào</th>
                      <th className="py-3 px-3.5 font-semibold">Ngày Ra</th>
                      <th className="py-3 px-3.5 font-semibold">Thời Gian Giữ</th>
                      <th className="py-3 px-3.5 font-semibold">Vị Thế</th>
                      <th className="py-3 px-3.5 font-semibold text-right">Giá Vào</th>
                      <th className="py-3 px-3.5 font-semibold text-right">Giá Ra</th>
                      <th className="py-3 px-3.5 font-semibold text-right">Khối Lượng</th>
                      <th className="py-3 px-3.5 font-semibold text-right">Lãi / Lỗ Ròng</th>
                      <th className="py-3 px-3.5 font-semibold text-right">% Lợi Nhuận</th>
                      <th className="py-3 px-3.5 font-semibold text-center">Lý Do Đóng</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/70 font-mono text-slate-300">
                    {filteredTrades.length === 0 ? (
                      <tr>
                        <td colSpan={11} className="py-8 text-center text-slate-500 font-sans">
                          Không tìm thấy lệnh nào phù hợp với bộ lọc hiện tại.
                        </td>
                      </tr>
                    ) : (
                      filteredTrades.map((t, index) => {
                        const isWin = t.pnl > 0;
                        const isBreakeven = t.pnl === 0;

                        return (
                          <tr
                            key={index}
                            className="transition hover:bg-slate-800/40"
                          >
                            <td className="py-2.5 px-3.5 text-slate-500">{index + 1}</td>
                            <td className="py-2.5 px-3.5 text-slate-200">{t.entry_date}</td>
                            <td className="py-2.5 px-3.5 text-slate-200">{t.exit_date}</td>
                            <td className="py-2.5 px-3.5 text-slate-400 font-sans">
                              {calcHoldingDays(t.entry_date, t.exit_date)}
                            </td>
                            <td className="py-2.5 px-3.5">
                              <span className="rounded bg-emerald-500/10 px-2 py-0.5 text-[10px] font-bold text-emerald-400 border border-emerald-500/20">
                                {t.action || "BUY"}
                              </span>
                            </td>
                            <td className="py-2.5 px-3.5 text-right font-medium text-slate-300">
                              {Number(t.entry_price).toLocaleString()}
                            </td>
                            <td className="py-2.5 px-3.5 text-right font-medium text-slate-300">
                              {Number(t.exit_price).toLocaleString()}
                            </td>
                            <td className="py-2.5 px-3.5 text-right text-slate-300">
                              {Number(t.shares).toLocaleString()} CP
                            </td>
                            <td
                              className={`py-2.5 px-3.5 text-right font-bold ${
                                isWin
                                  ? "text-emerald-400"
                                  : isBreakeven
                                  ? "text-slate-400"
                                  : "text-rose-400"
                              }`}
                            >
                              {isWin ? `+${formatCurrency(t.pnl)}` : formatCurrency(t.pnl)}
                            </td>
                            <td
                              className={`py-2.5 px-3.5 text-right font-bold ${
                                isWin
                                  ? "text-emerald-400"
                                  : isBreakeven
                                  ? "text-slate-400"
                                  : "text-rose-400"
                              }`}
                            >
                              {formatPercent(t.return_pct)}
                            </td>
                            <td className="py-2.5 px-3.5 text-center">
                              <span
                                className={`inline-block rounded-md px-2 py-0.5 text-[10px] font-semibold tracking-wider font-sans ${
                                  t.exit_reason === "TAKE_PROFIT"
                                    ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/20"
                                    : t.exit_reason === "STOP_LOSS"
                                    ? "bg-rose-500/15 text-rose-400 border border-rose-500/20"
                                    : t.exit_reason === "RSI_OVERBOUGHT"
                                    ? "bg-purple-500/15 text-purple-300 border border-purple-500/20"
                                    : "bg-slate-800 text-slate-400 border border-slate-700"
                                }`}
                              >
                                {t.exit_reason}
                              </span>
                            </td>
                          </tr>
                        );
                      })
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </section>
        </div>
      ) : (
        /* Trạng thái chào đón trước khi chạy */
        <section className="rounded-2xl border border-dashed border-slate-800 bg-slate-900/40 p-12 text-center backdrop-blur-sm">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-indigo-600/10 text-indigo-400 border border-indigo-500/20 mb-4 shadow-inner">
            <Activity size={32} />
          </div>
          <h3 className="text-lg font-bold text-white">Sẵn Sàng Khởi Chạy Backtest Định Lượng</h3>
          <p className="mx-auto mt-2 max-w-xl text-xs text-slate-400 leading-relaxed">
            Hệ thống sẽ quét chuỗi dữ liệu giá lịch sử, tính toán chỉ báo kỹ thuật RSI, SMA20, ATR14
            và mô phỏng phân bổ quy mô vị thế theo quy tắc quản trị rủi ro cố định (Fixed Fractional Risk).
          </p>
          <div className="mt-6 flex flex-wrap justify-center gap-3">
            <button
              type="button"
              onClick={() => {
                handleQuickSymbol("FPT.VN");
                handleSubmit();
              }}
              className="rounded-xl bg-indigo-600 px-5 py-2.5 text-xs font-semibold text-white shadow-lg shadow-indigo-600/25 transition hover:bg-indigo-500 flex items-center gap-2"
            >
              <Play size={14} fill="white" /> Chạy thử ngay với FPT.VN
            </button>
            <button
              type="button"
              onClick={() => {
                handleQuickSymbol("TCB.VN");
                handleSubmit();
              }}
              className="rounded-xl border border-slate-700 bg-slate-800 px-5 py-2.5 text-xs font-semibold text-slate-200 transition hover:bg-slate-700 hover:text-white flex items-center gap-2"
            >
              <Play size={14} /> Chạy thử với TCB.VN
            </button>
          </div>
        </section>
      )}
    </div>
  );
};

export default BacktestWorkspace;
