import math
from typing import Any


class RiskSignalService:
    @staticmethod
    def generate_signal(
        probability_up: float,
        rsi: float | None,
        close_price: float,
        sma20: float | None,
    ) -> dict[str, Any]:
        """Quyết định hành động BUY / SELL / HOLD dựa trên xác suất ML và bối cảnh kỹ thuật."""
        action = "HOLD"
        reasoning = []

        # Quy tắc sinh tín hiệu BUY
        if probability_up >= 0.60:
            if rsi is not None and rsi > 70:
                action = "HOLD"
                reasoning.append("Xác suất tăng cao nhưng RSI ở vùng quá mua (>70).")
            elif sma20 is not None and close_price < sma20:
                action = "HOLD"
                reasoning.append("Xác suất tăng nhưng giá nằm dưới SMA20 (Xu hướng ngắn hạn yếu).")
            else:
                action = "BUY"
                reasoning.append(f"Mô hình ML dự đoán xác suất tăng {probability_up * 100:.1f}%.")

        # Quy tắc sinh tín hiệu SELL
        elif probability_up <= 0.40:
            action = "SELL"
            reasoning.append(
                f"Mô hình ML dự đoán xác suất giảm/đi ngang (Tăng chỉ {probability_up * 100:.1f}%)."
            )

        # Quy tắc sinh tín hiệu HOLD
        else:
            reasoning.append(f"Tín hiệu trung tính (Xác suất tăng {probability_up * 100:.1f}%).")

        return {
            "action": action,
            "confidence": round(
                probability_up if action == "BUY" else (1.0 - probability_up),
                4,
            ),
            "reasoning": " ".join(reasoning),
        }

    @staticmethod
    def calculate_trade_plan(
        symbol: str,
        entry_price: float,
        atr14: float | None,
        account_risk_limit: float = 500.0,
        risk_reward_target: float = 2.0,
    ) -> dict[str, Any] | None:
        """Tính toán kế hoạch giao dịch chi tiết:
        Entry, Stop Loss, Take Profit và Position Size.
        """
        if entry_price <= 0:
            return None

        # Sử dụng 2 * ATR(14) để đặt Stop Loss theo biến động thực tế
        atr_val = atr14 if atr14 is not None and atr14 > 0 else entry_price * 0.025

        stop_loss_distance = 2.0 * atr_val
        stop_loss = max(
            round(entry_price - stop_loss_distance, 2),
            0.1,
        )

        risk_per_share = entry_price - stop_loss

        if risk_per_share <= 0:
            return None

        # Take Profit dựa trên tỷ lệ Risk/Reward (mặc định 1:2)
        take_profit = round(
            entry_price + (risk_per_share * risk_reward_target),
            2,
        )

        # Position Size = Hạn mức rủi ro / Rủi ro trên mỗi cổ phiếu
        position_size = math.floor(account_risk_limit / risk_per_share)

        return {
            "symbol": symbol,
            "entry_price": round(entry_price, 2),
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "position_size": position_size,
            "risk_reward_ratio": risk_reward_target,
            "status": "PENDING",
        }
