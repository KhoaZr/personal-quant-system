import { useState, useEffect, useCallback } from "react";
import { BacktestWorkspace } from "./components/BacktestWorkspace";
import { SignalsWorkspace } from "./components/SignalsWorkspace";
import {
  Activity,
  BarChart3,
  RefreshCw,
  CheckCircle,
  ShieldAlert,
} from "lucide-react";

export const App = () => {
  const [activeTab, setActiveTab] = useState("backtest");
  const [backendStatus, setBackendStatus] = useState("Checking...");
  const [isCheckingStatus, setIsCheckingStatus] = useState(false);

  const checkHealth = useCallback(async () => {
    setIsCheckingStatus(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/health");
      if (!res.ok) throw new Error("Health check failed");
      const data = await res.json();
      setBackendStatus(data.status === "healthy" ? "Online" : "Degraded");
    } catch {
      setBackendStatus("Offline");
    } finally {
      setIsCheckingStatus(false);
    }
  }, []);

  useEffect(() => {
    let isMounted = true;
    const fetchHealth = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/health");
        if (!res.ok) throw new Error("Health check failed");
        const data = await res.json();
        if (isMounted) {
          setBackendStatus(data.status === "healthy" ? "Online" : "Degraded");
        }
      } catch {
        if (isMounted) setBackendStatus("Offline");
      }
    };

    fetchHealth();
    const interval = setInterval(fetchHealth, 30000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <div className="min-h-screen bg-[#070b14] text-slate-100 flex flex-col font-sans selection:bg-indigo-500 selection:text-white">
      {/* HEADER ĐIỀU HƯỚNG QUANTUM TERMINAL */}
      <header className="sticky top-0 z-50 border-b border-slate-800/80 bg-[#0b0f19]/90 px-6 py-3.5 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl flex-col justify-between gap-4 md:flex-row md:items-center">
          {/* Logo & Subtitle */}
          <div className="flex items-center gap-3">
            <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-sky-400 shadow-md shadow-indigo-500/20">
              <Activity className="h-5 w-5 text-white" />
              <span className="absolute -top-0.5 -right-0.5 flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500" />
              </span>
            </div>

            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-base font-extrabold tracking-wide text-white">
                  PERSONAL QUANT SYSTEM
                </h1>
                <span className="rounded bg-indigo-500/10 px-2 py-0.5 text-[10px] font-mono font-bold text-indigo-400 border border-indigo-500/20">
                  v2.0
                </span>
              </div>
              <p className="text-[11px] text-slate-400">
                Nền tảng Nghiên Cứu Định Lượng &amp; Kiểm Thử Chiến Lược Tự Động
              </p>
            </div>
          </div>

          {/* Tab Navigation Center */}
          <div className="flex items-center rounded-xl border border-slate-800 bg-slate-900/90 p-1 shadow-inner">
            <button
              type="button"
              onClick={() => setActiveTab("backtest")}
              className={`flex items-center gap-2 rounded-lg px-4 py-2 text-xs font-semibold transition ${
                activeTab === "backtest"
                  ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                  : "text-slate-400 hover:text-white hover:bg-slate-800/50"
              }`}
            >
              <BarChart3 size={15} />
              <span>Kiểm Thử Chiến Lược (Backtest)</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("signals")}
              className={`flex items-center gap-2 rounded-lg px-4 py-2 text-xs font-semibold transition ${
                activeTab === "signals"
                  ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                  : "text-slate-400 hover:text-white hover:bg-slate-800/50"
              }`}
            >
              <RefreshCw size={15} />
              <span>Tín Hiệu &amp; Daily Pipeline</span>
            </button>
          </div>

          {/* Backend Status Indicator */}
          <div className="flex items-center gap-2.5">
            <button
              type="button"
              onClick={checkHealth}
              title="Nhấn để kiểm tra lại kết nối"
              className="flex items-center gap-2 rounded-xl border border-slate-800 bg-slate-900/80 px-3 py-1.5 text-xs transition hover:border-slate-700 hover:bg-slate-800"
            >
              {backendStatus === "Online" ? (
                <CheckCircle className="h-4 w-4 text-emerald-400" />
              ) : (
                <ShieldAlert className="h-4 w-4 text-amber-400" />
              )}
              <span className="text-slate-400">API:</span>
              <span
                className={`font-semibold font-mono ${
                  backendStatus === "Online"
                    ? "text-emerald-400"
                    : "text-amber-400"
                }`}
              >
                {backendStatus}
              </span>
              <RefreshCw
                size={12}
                className={`text-slate-500 ml-0.5 ${
                  isCheckingStatus ? "animate-spin" : ""
                }`}
              />
            </button>
          </div>
        </div>
      </header>

      {/* VÙNG NỘI DUNG CHÍNH */}
      <main className="flex-1 p-6 max-w-7xl mx-auto w-full">
        {activeTab === "backtest" && <BacktestWorkspace />}
        {activeTab === "signals" && <SignalsWorkspace />}
      </main>

      {/* FOOTER */}
      <footer className="border-t border-slate-800/80 bg-slate-950/60 py-4 px-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>
            Personal Quant System &copy; 2026 • Closed-Loop Quantitative Research &amp; Decision-Support
          </span>
          <span className="text-[11px] text-slate-600">
            Engine: FastAPI • Database: PostgreSQL • Frontend: React + Recharts
          </span>
        </div>
      </footer>
    </div>
  );
};

export default App;
