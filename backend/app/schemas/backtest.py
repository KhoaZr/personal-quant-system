from datetime import date

from pydantic import BaseModel, Field


class BacktestRequest(BaseModel):
    symbol: str = Field(
        ...,
        example="FPT.VN",
        description="Mã cổ phiếu cần kiểm thử",
    )
    start_date: date | None = Field(
        None,
        description="Ngày bắt đầu (mặc định lấy từ đầu lịch sử)",
    )
    end_date: date | None = Field(
        None,
        description="Ngày kết thúc",
    )
    initial_capital: float = Field(
        100_000_000.0,
        description="Vốn ban đầu (VND)",
    )
    fee_rate: float = Field(
        0.0015,
        description="Phí giao dịch mỗi chiều (mặc định 0.15%)",
    )
    slippage: float = Field(
        0.001,
        description="Độ trượt giá ước lượng (mặc định 0.1%)",
    )
    risk_per_trade: float = Field(
        0.02,
        description="Tỷ lệ rủi ro tối đa mỗi lệnh trên tổng vốn (mặc định 2%)",
    )


class BacktestTradeLog(BaseModel):
    entry_date: date
    exit_date: date
    action: str  # BUY
    entry_price: float
    exit_price: float
    shares: int
    pnl: float
    return_pct: float
    exit_reason: str  # TAKE_PROFIT, STOP_LOSS, SIGNAL_EXIT, END_OF_DATA


class EquityPoint(BaseModel):
    date: date
    equity: float
    drawdown_pct: float


class BacktestResponse(BaseModel):
    symbol: str
    initial_capital: float
    final_equity: float
    total_return_pct: float
    annualized_return_pct: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown_pct: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate_pct: float
    profit_factor: float
    trades: list[BacktestTradeLog]
    equity_curve: list[EquityPoint]