import math
from typing import Any

import pandas as pd
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models.stock import StockPrice, TechnicalIndicator
from app.schemas.backtest import (
    BacktestRequest,
    BacktestResponse,
    BacktestTradeLog,
    EquityPoint,
)


class BacktestService:
    @staticmethod
    def run_backtest(
        db: Session,
        request: BacktestRequest,
    ) -> BacktestResponse:
        symbol = request.symbol.upper()

        # 1. Trích xuất dữ liệu giá và chỉ báo kỹ thuật từ CSDL
        filters = [StockPrice.symbol == symbol]

        if request.start_date:
            filters.append(StockPrice.date >= request.start_date)

        if request.end_date:
            filters.append(StockPrice.date <= request.end_date)

        stmt_prices = (
            select(StockPrice)
            .where(and_(*filters))
            .order_by(StockPrice.date.asc())
        )

        prices: list[StockPrice] = list(db.scalars(stmt_prices).all())

        if len(prices) < 30:
            raise ValueError(
                f"Không đủ dữ liệu giá lịch sử cho mã {symbol} "
                "để chạy backtest (cần ít nhất 30 phiên)."
            )

        # Lấy chỉ báo kỹ thuật tương ứng
        date_list = [p.date for p in prices]

        stmt_ind = select(TechnicalIndicator).where(
            and_(
                TechnicalIndicator.symbol == symbol,
                TechnicalIndicator.date.in_(date_list),
            )
        )

        indicators = {
            ind.date: ind for ind in db.scalars(stmt_ind).all()
        }

        # 2. Chuẩn bị biến trạng thái mô phỏng
        cash = request.initial_capital
        position_shares = 0
        entry_price = 0.0
        entry_date = None
        current_sl = 0.0
        current_tp = 0.0

        trades: list[BacktestTradeLog] = []
        equity_series: list[dict[str, Any]] = []

        total_costs_rate = request.fee_rate + request.slippage

        # 3. Duyệt dữ liệu từng phiên (Bar-by-bar)
        for p in prices:
            current_date = p.date
            close_p = float(p.close)
            high_p = float(p.high)
            low_p = float(p.low)

            ind = indicators.get(current_date)

            rsi = (
                float(ind.rsi14)
                if ind and ind.rsi14 is not None
                else None
            )

            sma20 = (
                float(ind.sma20)
                if ind and ind.sma20 is not None
                else None
            )

            atr = (
                float(ind.atr14)
                if ind and ind.atr14 is not None
                else close_p * 0.02
            )

            # --- A. Kiểm tra điều kiện đóng vị thế nếu đang giữ hàng ---
            if position_shares > 0:
                exit_triggered = False
                exit_price = 0.0
                exit_reason = ""

                # Chạm Stop Loss
                if low_p <= current_sl:
                    exit_triggered = True
                    exit_price = min(close_p, current_sl) * (
                        1 - request.slippage
                    )
                    exit_reason = "STOP_LOSS"

                # Chạm Take Profit
                elif high_p >= current_tp:
                    exit_triggered = True
                    exit_price = max(close_p, current_tp) * (
                        1 - request.slippage
                    )
                    exit_reason = "TAKE_PROFIT"

                # RSI quá mua cực đại (> 80)
                # hoặc tín hiệu kỹ thuật đảo chiều
                elif rsi and rsi >= 80:
                    exit_triggered = True
                    exit_price = close_p * (1 - request.slippage)
                    exit_reason = "RSI_OVERBOUGHT"

                if exit_triggered:
                    proceeds = (
                        position_shares
                        * exit_price
                        * (1 - request.fee_rate)
                    )   
                    net_pnl = proceeds - (
                        position_shares
                        * entry_price
                        * (1 + total_costs_rate)
                    )

                    return_pct = (
                        net_pnl / (position_shares * entry_price)
                    ) * 100

                    cash += proceeds

                    trades.append(
                        BacktestTradeLog(
                            entry_date=entry_date,
                            exit_date=current_date,
                            action="BUY",
                            entry_price=round(entry_price, 2),
                            exit_price=round(exit_price, 2),
                            shares=position_shares,
                            pnl=round(net_pnl, 2),
                            return_pct=round(return_pct, 2),
                            exit_reason=exit_reason,
                        )
                    )

                    position_shares = 0
                    entry_price = 0.0
                    entry_date = None

            # --- B. Kiểm tra điều kiện mở vị thế mới nếu đang cầm tiền mặt ---
            elif (
                position_shares == 0
                and rsi is not None
                and sma20 is not None
            ):
                # Giả lập tín hiệu kết hợp:
                # Xu hướng giá trên SMA20 và RSI thoát vùng quá bán
                # hoặc động lực tốt (35 <= RSI <= 65)
                is_uptrend = close_p > sma20
                rsi_valid = 35.0 <= rsi <= 65.0

                if is_uptrend and rsi_valid:
                    actual_entry = close_p * (1 + request.slippage)

                    stop_loss = max(
                        0.1,
                        actual_entry - 2.0 * atr,
                    )

                    risk_per_share = actual_entry - stop_loss

                    if risk_per_share > 0:
                        account_risk_amount = (
                            cash * request.risk_per_trade
                        )

                        desired_shares = int(
                            account_risk_amount / risk_per_share
                        )

                        # Đảm bảo không mua vượt quá 95%
                        # số tiền mặt hiện có
                        max_affordable_shares = int(
                            (cash * 0.95)
                            / (actual_entry * (1 + request.fee_rate))
                        )

                        shares_to_buy = min(
                            desired_shares,
                            max_affordable_shares,
                        )

                        if shares_to_buy > 0:
                            cost = (
                                shares_to_buy
                                * actual_entry
                                * (1 + request.fee_rate)
                            )

                            cash -= cost
                            position_shares = shares_to_buy
                            entry_price = actual_entry
                            entry_date = current_date

                            current_sl = stop_loss
                            current_tp = (
                                actual_entry + (risk_per_share * 2.0)
                            )

                            # Tỷ lệ Risk/Reward = 1:2

            # Ghi nhận giá trị tài sản ròng (Equity) tại cuối ngày
            current_portfolio_value = (
                cash + (position_shares * close_p)
            )

            equity_series.append(
                {
                    "date": current_date,
                    "equity": current_portfolio_value,
                }
            )

        # Đóng vị thế cưỡng bức ở phiên cuối nếu còn giữ hàng
        if position_shares > 0:
            final_p = float(prices[-1].close) * (
                1 - request.slippage
            )

            proceeds = (
                position_shares
                * final_p
                * (1 - request.fee_rate)
            )

            net_pnl = proceeds - (
                position_shares
                * entry_price
                * (1 + total_costs_rate)
            )

            cash += proceeds

            trades.append(
                BacktestTradeLog(
                    entry_date=entry_date,
                    exit_date=prices[-1].date,
                    action="BUY",
                    entry_price=round(entry_price, 2),
                    exit_price=round(final_p, 2),
                    shares=position_shares,
                    pnl=round(net_pnl, 2),
                    return_pct=round(
                        (net_pnl / (position_shares * entry_price)) * 100,
                        2,
                    ),
                    exit_reason="END_OF_DATA",
                )
            )

            equity_series[-1]["equity"] = cash

        # 4. Tính toán các chỉ số thống kê hiệu năng
        df_equity = pd.DataFrame(equity_series)

        df_equity["peak"] = df_equity["equity"].cummax()

        df_equity["drawdown"] = (
            df_equity["equity"] - df_equity["peak"]
        ) / df_equity["peak"]

        max_drawdown = float(df_equity["drawdown"].min()) * 100

        final_equity = float(df_equity["equity"].iloc[-1])

        total_return_pct = (
            (final_equity - request.initial_capital)
            / request.initial_capital
        ) * 100

        # Annualized Return (CAGR)
        num_days = (prices[-1].date - prices[0].date).days
        years = max(num_days / 365.25, 0.1)

        annualized_return_pct = (
            (
                (final_equity / request.initial_capital)
                ** (1.0 / years)
            )
            - 1.0
        ) * 100

        # Daily Returns để tính Sharpe & Sortino
        df_equity["daily_return"] = (
            df_equity["equity"].pct_change().fillna(0.0)
        )

        daily_std = df_equity["daily_return"].std()

        sharpe_ratio = 0.0

        if daily_std > 0:
            sharpe_ratio = float(
                (
                    df_equity["daily_return"].mean() / daily_std
                ) * math.sqrt(252)
            )

        downside_returns = df_equity["daily_return"][
            df_equity["daily_return"] < 0
        ]

        downside_std = downside_returns.std()

        sortino_ratio = 0.0

        if downside_std and downside_std > 0:
            sortino_ratio = float(
                (
                    df_equity["daily_return"].mean() / downside_std
                ) * math.sqrt(252)
            )

        # 5. Thống kê lệnh
        total_trades = len(trades)

        winning_trades = sum(
            1 for t in trades if t.pnl > 0
        )

        losing_trades = sum(
            1 for t in trades if t.pnl <= 0
        )

        win_rate = (
            (winning_trades / total_trades * 100)
            if total_trades > 0
            else 0.0
        )

        gross_profits = sum(
            t.pnl for t in trades if t.pnl > 0
        )

        gross_losses = abs(
            sum(t.pnl for t in trades if t.pnl < 0)
        )

        profit_factor = (
            round(gross_profits / gross_losses, 2)
            if gross_losses > 0
            else (99.0 if gross_profits > 0 else 0.0)
        )

        equity_curve = [
            EquityPoint(
                date=row["date"],
                equity=round(row["equity"], 2),
                drawdown_pct=round(row["drawdown"] * 100, 2),
            )
            for _, row in df_equity.iterrows()
        ]

        return BacktestResponse(
            symbol=symbol,
            initial_capital=round(request.initial_capital, 2),
            final_equity=round(final_equity, 2),
            total_return_pct=round(total_return_pct, 2),
            annualized_return_pct=round(annualized_return_pct, 2),
            sharpe_ratio=round(sharpe_ratio, 2),
            sortino_ratio=round(sortino_ratio, 2),
            max_drawdown_pct=round(max_drawdown, 2),
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate_pct=round(win_rate, 2),
            profit_factor=profit_factor,
            trades=trades,
            equity_curve=equity_curve,
        )