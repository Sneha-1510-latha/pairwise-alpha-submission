# 🧠 Smart Crypto Strategy: EMA, RSI, Anchor Momentum, Volatility Sizing

This strategy is built for the **PairWise Alpha Round 2** challenge and designed to be:

- ✅ Fully deterministic  
- ✅ Realistic (no future data)  
- ✅ Risk-aware  
- ✅ Competitive under real-world constraints  

---

## 🚀 Strategy Summary

We trade **LDO**, **BONK**, and **DOGE** using predictive movements in **BTC**, **ETH**, **SOL**, **BNB**, and **XRP** as anchors. The logic is:

1. **Entry Trigger**:
   - Target price is above **EMA200** (uptrend)
   - Target **RSI > 50** (momentum confirmation)
   - **At least 3 anchor coins** pumped >2% in the last 4H candle

2. **Exit Trigger**:
   - Profit target: +5% OR
   - Stop loss: -3%

3. **Risk Control**:
   - Cooldown of **20 candles** after a loss
   - Position size = `min(1.0, max(0.2, 0.05 / volatility))`

---

## 🧮 `get_coin_metadata()`

```python
{
  "targets": [
    {"symbol": "LDO", "timeframe": "1H"},
    {"symbol": "BONK", "timeframe": "1H"},
    {"symbol": "DOGE", "timeframe": "1H"}
  ],
  "anchors": [
    {"symbol": "BTC", "timeframe": "4H"},
    {"symbol": "ETH", "timeframe": "4H"},
    {"symbol": "SOL", "timeframe": "4H"},
    {"symbol": "BNB", "timeframe": "4H"},
    {"symbol": "XRP", "timeframe": "4H"}
  ]
}

📊 Position Sizing
Calculated dynamically using volatility:

python
Copy code
position_size = min(1.0, max(0.2, 0.05 / volatility))
Increases exposure when market is calm

Reduces exposure when volatility is high


🧠 Indicators Used

| Indicator      | Purpose                   |
| -------------- | ------------------------- |
| EMA200         | Trend detection (uptrend) |
| RSI (14)       | Momentum confirmation     |
| Anchor Returns | Market context            |
🔒 Risk Management
Cooldown of 20 candles after a stop-loss exit

Strategy trades only when:

Uptrend (EMA200)

RSI > 50

Anchor momentum is strong

No lookahead, no randomness — safe for forward evaluation

✅ Submission Ready
✅ Passed Lunor validator

✅ At least 16+ BUY-SELL pairs per symbol

✅ Deterministic (no randomness, no leakage)

✅ Uses only pandas + numpy

✅ <90s runtime

💡 Potential Future Enhancements
Multi-timeframe confirmation: 1H + 4H

Adaptive TP/SL based on volatility

Historical Sharpe-weighted allocation per target

Cross-anchor sentiment scoring for higher precision



