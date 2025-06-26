import pandas as pd
import numpy as np

def get_coin_metadata() -> dict:
    return {
        "targets": [
            {"symbol": "LDO", "timeframe": "1H"},
            {"symbol": "BONK", "timeframe": "1H"},
            {"symbol": "DOGE", "timeframe": "1H"},
        ],
        "anchors": [
            {"symbol": "BTC", "timeframe": "4H"},
            {"symbol": "ETH", "timeframe": "4H"},
            {"symbol": "SOL", "timeframe": "4H"},
            {"symbol": "BNB", "timeframe": "4H"},
            {"symbol": "XRP", "timeframe": "4H"},
        ]
    }

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / (avg_loss + 1e-9)
    return 100 - (100 / (1 + rs))

def generate_signals(anchor_df: pd.DataFrame, target_df: pd.DataFrame) -> pd.DataFrame:
    results = []
    metadata = get_coin_metadata()

    anchors = [a["symbol"] for a in metadata["anchors"]]
    targets = metadata["targets"]

    for target in targets:
        symbol = target["symbol"]
        tf = target["timeframe"]
        close_col = f"close_{symbol}_{tf}"
        if close_col not in target_df:
            continue

        df = target_df[["timestamp", close_col]].copy()
        df.rename(columns={close_col: "close"}, inplace=True)
        df["ema200"] = df["close"].ewm(span=200).mean()
        df["rsi"] = calculate_rsi(df["close"])
        df["return"] = df["close"].pct_change()
        df["volatility"] = df["return"].rolling(10).std().fillna(0.01)
        df["signal"] = "HOLD"
        df["position_size"] = 0.0

        # Add anchor returns
        for a in anchors:
            col = f"close_{a}_4H"
            if col in anchor_df:
                df[f"{a}_ret"] = anchor_df[col].pct_change().fillna(0)

        in_position = False
        entry_price = 0
        cooldown = 0

        signals = []
        sizes = []

        for i in range(len(df)):
            row = df.iloc[i]

            # Anchor score: how many anchors pumped >2%
            anchor_pumps = sum([
                row.get(f"{a}_ret", 0) > 0.02 for a in anchors
            ])

            trend_ok = row["close"] > row["ema200"]
            rsi_ok = row["rsi"] > 50
            price = row["close"]
            vol = row["volatility"]

            # Cooldown logic
            if cooldown > 0:
                cooldown -= 1
                signals.append("HOLD")
                sizes.append(0.0)
                continue

            # Entry condition
            if not in_position and price > 0 and trend_ok and rsi_ok and anchor_pumps >= 3:
                signals.append("BUY")
                sizes.append(min(1.0, max(0.2, 0.05 / (vol + 1e-9))))
                in_position = True
                entry_price = price
                continue

            # Exit condition
            if in_position and price > 0 and entry_price > 0:
                change = (price - entry_price) / entry_price
                if change > 0.05 or change < -0.03:
                    signals.append("SELL")
                    sizes.append(0.0)
                    in_position = False
                    entry_price = 0
                    cooldown = 20  # wait 20 candles
                    continue
                else:
                    signals.append("HOLD")
                    sizes.append(min(1.0, max(0.2, 0.05 / (vol + 1e-9))))
                    continue

            # Default
            signals.append("HOLD")
            sizes.append(0.0)

        result = pd.DataFrame({
            "timestamp": df["timestamp"],
            "symbol": symbol,
            "signal": signals,
            "position_size": sizes
        })

        results.append(result)

    return pd.concat(results, ignore_index=True)
