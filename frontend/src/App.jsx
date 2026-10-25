
import React, { useState, useEffect } from "react";
import { quantAPI } from "./api/client";
import {
  Activity,
  TrendingUp,
  TrendingDown,
  ShieldAlert,
  CheckCircle,
  RefreshCw,
} from "lucide-react";

export default function App() {
  const [symbols, setSymbols] = useState("FPT.VN, VIC.VN");
  const [signals, setSignals] = useState([]);
  const [loading, setLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState("Checking...");

  // Kiểm tra trạng thái Backend
  useEffect(() => {
    fetch("http://127.0.0.1:8000/health")
      .then((res) => {
        if (!res.ok) {
          throw new Error("Backend health check failed");
        }
        return res.json();
      })
      .then((data) => {
        setBackendStatus(
          data.status === "healthy" ? "Online" : "Offline"
        );
      })
      .catch(() => {
        setBackendStatus("Offline");
      });
  }, []);

  // Tạo tín hiệu giao dịch
  const handleGenerateSignals = async () => {
    setLoading(true);

    try {
      const symList = symbols
        .split(",")
        .map((symbol) => symbol.trim().toUpperCase())
        .filter(Boolean);

      const res = await quantAPI.generateTradePlans(
        symList,
        500
      );

      setSignals(res.data.signals || []);
    } catch (err) {
      console.error("Error generating signals:", err);
      alert(
        "Lỗi kết nối Backend hoặc chưa có dữ liệu. Vui lòng kiểm tra lại!"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-brand-dark text-slate-100">
      {/* Header */}
      <header className="border-b border-brand-border bg-brand-card px-6 py-5">
        <div className="mx-auto flex max-w-7xl flex-col justify-between gap-4 md:flex-row md:items-center">
          <div>
            <h1 className="flex items-center gap-3 text-2xl font-bold">
              <Activity className="h-7 w-7 text-brand-accent" />
              Personal Quant System
            </h1>

            <p className="mt-1 text-sm text-slate-400">
              Closed-Loop Quantitative Research &amp;
              Decision-Support
            </p>
          </div>

          <div className="flex items-center gap-2 text-sm">
            {backendStatus === "Online" ? (
              <CheckCircle className="h-5 w-5 text-emerald-400" />
            ) : (
              <ShieldAlert className="h-5 w-5 text-amber-400" />
            )}

            <span className="text-slate-400">
              Backend Status:
            </span>

            <span
              className={
                backendStatus === "Online"
                  ? "font-semibold text-emerald-400"
                  : "font-semibold text-amber-400"
              }
            >
              {backendStatus}
            </span>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl space-y-8 px-6 py-8">
        {/* Control Panel */}
        <section className="rounded-xl border border-brand-border bg-brand-card p-6">
          <h2 className="mb-5 text-xl font-semibold">
            Bảng điều khiển quét tín hiệu
          </h2>

          <div className="flex flex-col gap-4 md:flex-row">
            <input
              type="text"
              value={symbols}
              onChange={(e) => setSymbols(e.target.value)}
              placeholder="Nhập mã chứng khoán (VD: FPT.VN, VIC.VN)"
              className="min-w-0 flex-1 rounded-lg border border-brand-border bg-brand-dark px-4 py-3 text-slate-100 outline-none transition focus:border-brand-accent"
            />

            <button
              onClick={handleGenerateSignals}
              disabled={loading || !symbols.trim()}
              className="flex items-center justify-center gap-2 rounded-lg bg-sky-500 px-6 py-3 font-semibold text-slate-950 transition hover:bg-sky-400 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <RefreshCw
                className={`h-5 w-5 ${
                  loading ? "animate-spin" : ""
                }`}
              />

              {loading ? "Đang phân tích..." : "Quét Tín hiệu"}
            </button>
          </div>
        </section>

        {/* Signals Grid */}
        <section>
          <h2 className="mb-5 text-xl font-semibold">
            Khuyến nghị Tín hiệu &amp; Kế hoạch Lệnh
          </h2>

          {signals.length === 0 ? (
            <div className="rounded-xl border border-dashed border-brand-border bg-brand-card/50 px-6 py-12 text-center">
              <Activity className="mx-auto mb-3 h-10 w-10 text-slate-500" />

              <p className="text-slate-400">
                Chưa có tín hiệu nào. Nhấn "Quét Tín hiệu"
                để phân tích danh mục.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
              {signals.map((sig, idx) => (
                <article
                  key={`${sig.symbol}-${idx}`}
                  className="rounded-xl border border-brand-border bg-brand-card p-6 transition hover:border-slate-500"
                >
                  {/* Signal Header */}
                  <div className="mb-5 flex items-center justify-between gap-3">
                    <h3 className="text-xl font-bold">
                      {sig.symbol}
                    </h3>

                    <span
                      className={`rounded-full px-3 py-1 text-sm font-bold ${
                        sig.action === "BUY"
                          ? "bg-emerald-500/15 text-emerald-400"
                          : sig.action === "SELL"
                            ? "bg-rose-500/15 text-rose-400"
                            : "bg-amber-500/15 text-amber-400"
                      }`}
                    >
                      {sig.action === "BUY" ? (
                        <TrendingUp className="mr-1 inline h-4 w-4" />
                      ) : sig.action === "SELL" ? (
                        <TrendingDown className="mr-1 inline h-4 w-4" />
                      ) : null}

                      {sig.action}
                    </span>
                  </div>

                  {/* Confidence */}
                  <div className="mb-4">
                    <div className="mb-2 flex justify-between text-sm">
                      <span className="text-slate-400">
                        Độ tự tin
                      </span>

                      <span className="font-semibold text-brand-accent">
                        {(sig.confidence * 100).toFixed(1)}%
                      </span>
                    </div>

                    <div className="h-2 overflow-hidden rounded-full bg-slate-700">
                      <div
                        className="h-full rounded-full bg-sky-400 transition-all"
                        style={{
                          width: `${Math.min(
                            100,
                            Math.max(0, sig.confidence * 100)
                          )}%`,
                        }}
                      />
                    </div>
                  </div>

                  {/* Reasoning */}
                  <div className="mb-5 rounded-lg bg-brand-dark p-4">
                    <p className="mb-1 text-sm font-semibold text-slate-300">
                      Lý do phân tích
                    </p>

                    <p className="text-sm leading-6 text-slate-400">
                      {sig.reasoning}
                    </p>
                  </div>

                  {/* Trade Plan */}
                  {sig.trade_plan ? (
                    <div>
                      <h4 className="mb-4 font-semibold text-slate-200">
                        Chi tiết Kế hoạch Lệnh
                      </h4>

                      <div className="grid grid-cols-2 gap-3">
                        <div className="rounded-lg border border-brand-border p-3">
                          <p className="text-xs text-slate-400">
                            Entry
                          </p>

                          <p className="mt-1 font-semibold text-sky-400">
                            {sig.trade_plan.entry_price.toLocaleString()}
                          </p>
                        </div>

                        <div className="rounded-lg border border-brand-border p-3">
                          <p className="text-xs text-slate-400">
                            Stop Loss
                          </p>

                          <p className="mt-1 font-semibold text-rose-400">
                            {sig.trade_plan.stop_loss.toLocaleString()}
                          </p>
                        </div>

                        <div className="rounded-lg border border-brand-border p-3">
                          <p className="text-xs text-slate-400">
                            Take Profit
                          </p>

                          <p className="mt-1 font-semibold text-emerald-400">
                            {sig.trade_plan.take_profit.toLocaleString()}
                          </p>
                        </div>

                        <div className="rounded-lg border border-brand-border p-3">
                          <p className="text-xs text-slate-400">
                            Vị thế
                          </p>

                          <p className="mt-1 font-semibold text-slate-100">
                            {sig.trade_plan.position_size.toLocaleString()} CP
                          </p>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <p className="text-sm italic text-slate-500">
                      Không có kế hoạch lệnh mở vị thế cho tín hiệu{" "}
                      {sig.action}.
                    </p>
                  )}
                </article>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
