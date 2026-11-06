import { useState } from "react";
import { quantAPI } from "../api/client";
import {
  Activity,
  TrendingUp,
  TrendingDown,
  RefreshCw,
  Sparkles,
  ShieldAlert,
} from "lucide-react";

export const SignalsWorkspace = () => {
  const [symbols, setSymbols] = useState("FPT.VN, TCB.VN");
  const [signals, setSignals] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleGenerateSignals = async () => {
    setLoading(true);
    setError(null);

    try {
      const symList = symbols
        .split(",")
        .map((s) => s.trim().toUpperCase())
        .filter(Boolean);

      const res = await quantAPI.generateTradePlans(symList, 500);
      setSignals(res.data?.signals || []);
    } catch (err) {
      console.error("Error generating signals:", err);
      const msg =
        err.response?.data?.detail ||
        err.message ||
        "Lỗi kết nối Backend hoặc chưa có dữ liệu. Vui lòng kiểm tra lại!";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Control Panel */}
      <section className="relative overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/90 p-6 shadow-2xl backdrop-blur-md">
        <div className="mb-4 flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
          <div>
            <h2 className="flex items-center gap-2 text-xl font-bold tracking-tight text-white">
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-sky-500/20 text-sky-400 border border-sky-500/30">
                <RefreshCw size={18} />
              </span>
              Bảng Điều Khiển Quét Tín Hiệu & Kế Hoạch Lệnh
            </h2>
            <p className="mt-1 text-xs text-slate-400">
              Đồng bộ dữ liệu thị trường và phân tích tín hiệu thời gian thực theo mô hình định lượng.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400 flex items-center gap-1">
              <Sparkles size={13} className="text-amber-400" /> Gợi ý:
            </span>
            {["FPT.VN", "TCB.VN"].map((sym) => (
              <button
                key={sym}
                type="button"
                onClick={() => setSymbols(sym)}
                className="rounded-md border border-slate-700 bg-slate-800 px-2.5 py-1 text-xs font-mono text-slate-300 hover:text-white transition"
              >
                {sym}
              </button>
            ))}
          </div>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row">
          <input
            type="text"
            value={symbols}
            onChange={(e) => setSymbols(e.target.value)}
            placeholder="Nhập mã chứng khoán cách nhau bằng dấu phẩy (VD: FPT.VN, TCB.VN)"
            className="min-w-0 flex-1 rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm font-mono text-slate-100 outline-none transition focus:border-sky-500"
          />

          <button
            onClick={handleGenerateSignals}
            disabled={loading || !symbols.trim()}
            className="flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-sky-500 to-sky-400 px-6 py-3 font-semibold text-slate-950 shadow-lg shadow-sky-500/25 transition hover:from-sky-400 hover:to-sky-300 disabled:cursor-not-allowed disabled:opacity-50 text-sm"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            {loading ? "Đang phân tích..." : "Quét Tín Hiệu"}
          </button>
        </div>

        {error && (
          <div className="mt-4 flex items-center gap-3 rounded-xl border border-red-500/30 bg-red-950/40 p-4 text-xs text-red-200">
            <ShieldAlert size={18} className="shrink-0 text-red-400" />
            <span>{error}</span>
          </div>
        )}
      </section>

      {/* Signals Grid */}
      <section className="space-y-4">
        <h3 className="text-base font-bold text-white flex items-center gap-2">
          <Activity size={18} className="text-sky-400" />
          <span>Khuyến Nghị Tín Hiệu & Kế Hoạch Vị Thế</span>
          {signals.length > 0 && (
            <span className="rounded-full bg-slate-800 px-2.5 py-0.5 font-mono text-xs text-sky-400 border border-slate-700">
              {signals.length} khuyến nghị
            </span>
          )}
        </h3>

        {signals.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-slate-800 bg-slate-900/40 px-6 py-12 text-center backdrop-blur-sm">
            <Activity className="mx-auto mb-3 h-10 w-10 text-slate-600" />
            <p className="text-sm font-medium text-slate-400">
              Chưa có tín hiệu nào. Nhấn "Quét Tín Hiệu" để phân tích danh mục.
            </p>
            <p className="mt-1 text-xs text-slate-500">
              Hệ thống tự động đồng bộ kết quả này với Telegram Bot vào lúc 23:00 hàng ngày.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
            {signals.map((sig, idx) => (
              <article
                key={`${sig.symbol}-${idx}`}
                className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl backdrop-blur-md transition hover:border-slate-700"
              >
                {/* Signal Header */}
                <div className="mb-4 flex items-center justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <span className="text-xl font-bold font-mono text-white">
                      {sig.symbol}
                    </span>
                  </div>

                  <span
                    className={`inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs font-bold ${
                      sig.action === "BUY"
                        ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                        : sig.action === "SELL"
                        ? "bg-rose-500/15 text-rose-400 border border-rose-500/30"
                        : "bg-amber-500/15 text-amber-400 border border-amber-500/30"
                    }`}
                  >
                    {sig.action === "BUY" ? (
                      <TrendingUp size={14} />
                    ) : sig.action === "SELL" ? (
                      <TrendingDown size={14} />
                    ) : null}
                    {sig.action}
                  </span>
                </div>

                {/* Confidence Bar */}
                <div className="mb-4">
                  <div className="mb-1.5 flex justify-between text-xs">
                    <span className="text-slate-400">Độ tin cậy thuật toán:</span>
                    <span className="font-mono font-bold text-sky-400">
                      {(sig.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-slate-800">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-sky-500 to-indigo-500 transition-all duration-500"
                      style={{
                        width: `${Math.min(100, Math.max(0, sig.confidence * 100))}%`,
                      }}
                    />
                  </div>
                </div>

                {/* Reasoning */}
                <div className="mb-4 rounded-xl border border-slate-800/80 bg-slate-950/70 p-3.5">
                  <p className="mb-1 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                    Lý do phân tích
                  </p>
                  <p className="text-xs leading-relaxed text-slate-300">
                    {sig.reasoning}
                  </p>
                </div>

                {/* Trade Plan */}
                {sig.trade_plan ? (
                  <div>
                    <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
                      Kế Hoạch Khớp Lệnh Chi Tiết
                    </h4>
                    <div className="grid grid-cols-2 gap-2.5 font-mono text-xs">
                      <div className="rounded-xl border border-slate-800 bg-slate-950/80 p-3">
                        <span className="text-[10px] text-slate-400 uppercase">Giá Vào (Entry)</span>
                        <p className="mt-1 font-bold text-sky-400">
                          {Number(sig.trade_plan.entry_price).toLocaleString()}
                        </p>
                      </div>
                      <div className="rounded-xl border border-slate-800 bg-slate-950/80 p-3">
                        <span className="text-[10px] text-slate-400 uppercase">Dừng Lỗ (Stop Loss)</span>
                        <p className="mt-1 font-bold text-rose-400">
                          {Number(sig.trade_plan.stop_loss).toLocaleString()}
                        </p>
                      </div>
                      <div className="rounded-xl border border-slate-800 bg-slate-950/80 p-3">
                        <span className="text-[10px] text-slate-400 uppercase">Chốt Lời (Take Profit)</span>
                        <p className="mt-1 font-bold text-emerald-400">
                          {Number(sig.trade_plan.take_profit).toLocaleString()}
                        </p>
                      </div>
                      <div className="rounded-xl border border-slate-800 bg-slate-950/80 p-3">
                        <span className="text-[10px] text-slate-400 uppercase">Quy Mô Vị Thế</span>
                        <p className="mt-1 font-bold text-white">
                          {Number(sig.trade_plan.position_size).toLocaleString()} CP
                        </p>
                      </div>
                    </div>
                  </div>
                ) : (
                  <p className="text-xs italic text-slate-500">
                    Không có kế hoạch lệnh mở vị thế cho tín hiệu {sig.action}.
                  </p>
                )}
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
};

export default SignalsWorkspace;
