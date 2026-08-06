import logging
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def _flatten_multiindex_columns(df: pd.DataFrame) -> pd.DataFrame:
    """If DataFrame has MultiIndex columns (e.g. from yfinance), flatten them.
    Join levels with underscore and strip whitespace.
    """
    if isinstance(df.columns, pd.MultiIndex):
        new_cols = []
        for col in df.columns:
            parts = [str(p).strip() for p in col if (p is not None and p != "")]
            new_cols.append("_".join(parts))
        df = df.copy()
        df.columns = new_cols
    return df


def process_stock_data(df: pd.DataFrame, symbol: str) -> pd.DataFrame:
    """Clean and normalize a stock price DataFrame for insertion into Postgres.

    Steps implemented per specification:
    - Flatten MultiIndex columns
    - Normalize column names to lower_snake_case expected: date, open, high, low,
      close, adj_close, volume
    - Ensure `date` is a column in YYYY-MM-DD format
    - Assign and normalize `symbol` (uppercase)
    - Drop duplicate (symbol, date) keeping last
    - Drop rows with NaN in price columns, fill missing volume with 0
    - Remove invalid/non-positive prices and negative volume
    - Remove logical anomalies (high < low or high < close)
    - Ensure `adj_close` exists (fill from close)
    - Add `created_at` timestamp
    - Strictly cast dtypes and return only the 9 required columns in order

    Returns cleaned DataFrame.
    """
    try:
        original_count = len(df)

        # Flatten columns if MultiIndex
        df = _flatten_multiindex_columns(df)

        # If index is datetime-like and contains dates, reset to column
        if not isinstance(df.index, pd.RangeIndex):
            try:
                # keep index if it's a meaningful date index
                df = df.reset_index()
            except Exception:
                df = df.copy()

        # Normalize column names
        df = df.rename(columns={c: str(c).lower().strip().replace(" ", "_") for c in df.columns})

        # Common variants mapping
        col_map = {
            "adj close": "adj_close",
            "adj_close": "adj_close",
            "adjusted_close": "adj_close",
            "close": "close",
            "open": "open",
            "high": "high",
            "low": "low",
            "volume": "volume",
            "date": "date",
        }

        # Apply fuzzy mapping for columns that may include ticker prefixes like 'AAPL_close'
        mapped = {}
        for c in df.columns:
            lc = c.lower()
            if lc in col_map:
                mapped[c] = col_map[lc]
            else:
                # try to match by suffix
                for key in ["open", "high", "low", "close", "adj_close", "volume", "date"]:
                    if lc.endswith("_" + key) or lc == key or key in lc:
                        mapped[c] = key
                        break

        df = df.rename(columns=mapped)

        # Ensure date column exists
        if "date" not in df.columns:
            # try common index name
            if "index" in df.columns:
                df = df.rename(columns={"index": "date"})
            else:
                raise ValueError("No date column or index found in dataframe")

        # Convert date to datetime and format YYYY-MM-DD (string ISO date)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")

        # Assign symbol column and normalize to upper-case
        df["symbol"] = symbol.upper()

        # Reorder columns to bring symbol and date to front for operations
        cols = [c for c in df.columns if c not in ("symbol", "date")]
        df = df[["symbol", "date"] + cols]

        # Drop duplicate primary keys
        before_dups = len(df)
        df = df.drop_duplicates(subset=["symbol", "date"], keep="last")
        dropped_dups = before_dups - len(df)

        # Ensure price columns exist; if missing create as NaN
        for price_col in ["open", "high", "low", "close", "adj_close"]:
            if price_col not in df.columns:
                df[price_col] = np.nan

        # Drop rows where any critical price is NaN
        before_nans = len(df)
        df = df.dropna(subset=["open", "high", "low", "close"], how="any")
        dropped_nans = before_nans - len(df)

        # Fill missing volume with 0
        if "volume" not in df.columns:
            df["volume"] = 0
        df["volume"] = df["volume"].fillna(0)

        # Convert numeric columns to numeric coercing errors to NaN
        for c in ["open", "high", "low", "close", "adj_close", "volume"]:
            if c in ("volume",):
                df[c] = pd.to_numeric(df[c], errors="coerce")
            else:
                df[c] = pd.to_numeric(df[c], errors="coerce")

        # Remove rows with non-positive prices or negative volume
        before_invalids = len(df)
        cond_valid = (
            (df["open"] > 0)
            & (df["high"] > 0)
            & (df["low"] > 0)
            & (df["close"] > 0)
            & (df["volume"] >= 0)
        )
        df = df[cond_valid]
        dropped_invalids = before_invalids - len(df)

        # Price logic checks: high >= low and high >= close
        before_logic = len(df)
        cond_logic = (df["high"] >= df["low"]) & (df["high"] >= df["close"]) & (df["low"] <= df["close"].fillna(df["low"]))
        df = df[cond_logic]
        dropped_logic = before_logic - len(df)

        # Ensure adj_close filled from close when missing or NaN
        df["adj_close"] = df["adj_close"].fillna(df["close"])

        # Add created_at timestamp
        df["created_at"] = pd.Timestamp.now()

        # Strict casting
        df["symbol"] = df["symbol"].astype(str)
        # Keep date as ISO YYYY-MM-DD string
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
        df[["open", "high", "low", "close", "adj_close"]] = df[["open", "high", "low", "close", "adj_close"]].astype(float)
        df["volume"] = df["volume"].fillna(0).astype("int64")
        df["created_at"] = pd.to_datetime(df["created_at"]) 

        # Sort by date ascending
        df = df.sort_values(by="date", ascending=True)

        # Final column ordering
        final_cols = ["symbol", "date", "open", "high", "low", "close", "adj_close", "volume", "created_at"]
        # Ensure all final cols exist
        for c in final_cols:
            if c not in df.columns:
                df[c] = np.nan if c != "volume" else 0

        result = df[final_cols].copy()

        logger.info(
            "process_stock_data: rows before=%d, after=%d, dropped_duplicates=%d, dropped_nans=%d, dropped_invalids=%d, dropped_logic=%d",
            original_count,
            len(result),
            dropped_dups,
            dropped_nans,
            dropped_invalids,
            dropped_logic,
        )

        return result

    except Exception as e:
        logger.exception("Error processing stock data for %s: %s", symbol, e)
        raise


def process_csv_file(input_csv: str, output_csv: str, symbol: str) -> pd.DataFrame:
    """Read raw CSV, process with `process_stock_data`, and write cleaned CSV.

    Returns the cleaned DataFrame.
    """
    try:
        df = pd.read_csv(input_csv)
    except Exception as e:
        logger.exception("Failed to read input CSV %s: %s", input_csv, e)
        raise

    cleaned = process_stock_data(df, symbol)

    try:
        cleaned.to_csv(output_csv, index=False)
        logger.info("Wrote cleaned CSV to %s (rows=%d)", output_csv, len(cleaned))
    except Exception as e:
        logger.exception("Failed to write cleaned CSV to %s: %s", output_csv, e)
        raise

    return cleaned


__all__ = ["process_stock_data", "process_csv_file"]
