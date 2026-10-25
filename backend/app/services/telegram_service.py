import logging
import os
from typing import Any, cast

import requests

logger = logging.getLogger(__name__)


class TelegramService:
    @staticmethod
    def send_message(text_message: str) -> bool:
        """Gửi thông báo văn bản (hỗ trợ định dạng HTML) qua Telegram Bot API."""
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")

        if not bot_token or not chat_id:
            logger.warning(
                "Telegram Bot Token hoặc Chat ID chưa được cấu hình trong .env. Bỏ qua thông báo."
            )
            return False

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

        payload = {
            "chat_id": chat_id,
            "text": text_message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }

        try:
            response = requests.post(
                url,
                json=cast(dict[str, Any], payload),
                timeout=10,
            )
            response.raise_for_status()
            res_data = response.json()

            if res_data.get("ok"):
                logger.info("Đã gửi báo cáo qua Telegram thành công!")
                return True

            logger.error("Gửi Telegram thất bại: %s", res_data)
            return False

        except (requests.RequestException, ValueError):
            logger.exception("Lỗi kết nối hoặc xử lý phản hồi Telegram API")
            return False

    @staticmethod
    def format_pipeline_summary(summary: dict[str, Any]) -> str:
        """Định dạng kết quả Daily Pipeline thành bản tin HTML trực quan."""
        lines: list[str] = []

        timestamp = str(summary.get("timestamp", "N/A"))[:19]
        duration = summary.get("duration_seconds", 0)
        symbols = summary.get("symbols_processed", [])
        signals = summary.get("signals_generated", [])
        errors = summary.get("errors", [])

        lines.append("🚀 <b>PERSONAL QUANT SYSTEM — BÁO CÁO HÀNG NGÀY</b>")
        lines.append(f"⏰ <b>Thời gian:</b> <code>{timestamp}</code>")
        lines.append(f"⏱️ <b>Thời gian xử lý:</b> {duration}s")
        lines.append(f"📊 <b>Cổ phiếu quét:</b> {', '.join(symbols) or 'Không có'}")

        lines.append("\n🎯 <b>KẾT QUẢ TÍN HIỆU &amp; KHUYẾN NGHỊ:</b>")

        if not signals:
            lines.append("<i>Không có tín hiệu mới.</i>")
        else:
            for sig in signals:
                symbol = sig.get("symbol", "N/A")
                action = sig.get("action", "N/A")
                confidence = float(sig.get("confidence", 0)) * 100

                if action == "BUY":
                    icon = "🟢"
                elif action == "SELL":
                    icon = "🔴"
                else:
                    icon = "🟡"

                lines.append(
                    f"\n{icon} <b>{symbol}</b>: <b>{action}</b> (Độ tin cậy: {confidence:.1f}%)"
                )

                plan = sig.get("trade_plan")

                if plan:
                    entry_price = plan.get("entry_price")
                    stop_loss = plan.get("stop_loss")
                    take_profit = plan.get("take_profit")
                    position_size = plan.get("position_size")

                    if entry_price is not None:
                        lines.append(f" • <b>Entry:</b> <code>{float(entry_price):,.0f}</code>")

                    if stop_loss is not None:
                        lines.append(f" • <b>Stop Loss:</b> <code>{float(stop_loss):,.0f}</code>")

                    if take_profit is not None:
                        lines.append(
                            f" • <b>Take Profit:</b> <code>{float(take_profit):,.0f}</code>"
                        )

                    if position_size is not None:
                        lines.append(f" • <b>Khối lượng:</b> <code>{position_size} CP</code>")

        if errors:
            lines.append("\n⚠️ <b>CẢNH BÁO LỖI:</b>")

            for error in errors:
                # Escape ký tự đặc biệt để tránh lỗi định dạng HTML.
                safe_error = (
                    str(error).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                )
                lines.append(f"• <code>{safe_error}</code>")

        return "\n".join(lines)
