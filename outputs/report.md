# Bitcoin Market Sentiment vs Trader Behavior

## Methodology
- Loaded sentiment and trade datasets, profiled rows/columns/missing values/duplicates, and parsed timestamps to daily grain.
- Aligned trades with same-day sentiment labels and computed daily metrics: PnL, win rate, average size, leverage, trade count, and long/short ratio.
- Compared Fear vs Greed periods and created trader segments (high vs low leverage, frequent vs infrequent, consistent vs inconsistent winners).

## Part A — Data Preparation
- Sentiment dataset: **122 rows**, **3 columns**, duplicates=1, missing={'timestamp': 0, 'fear_greed_value': 0, 'sentiment': 0}.
- Trades dataset: **11754 rows**, **6 columns**, duplicates=1, missing={'trader_id': 0, 'timestamp': 0, 'side': 0, 'trade_size': 0, 'leverage': 1, 'pnl': 0}.
- Timestamps converted to date and joined by date (daily level).

## Part B — Evidence-based Analysis
### Fear vs Greed comparison

| Metric | Fear | Greed |
|---|---:|---:|
| Days | 61 | 46 |
| Avg daily PnL | -37.24 | 53.04 |
| Avg win rate | 0.3656 | 0.6725 |
| Drawdown proxy (worst day PnL) | -69.85 | 21.14 |
| Avg trades/day | 96.57 | 96.93 |
| Avg leverage | 3.39 | 3.47 |

### Segment summary

| Segment | # Traders | Avg total PnL | Avg win rate | Avg trades | Avg leverage |
|---|---:|---:|---:|---:|---:|
| High leverage | 40 | 6.85 | 0.5041 | 144.43 | 3.56 |
| Low leverage | 40 | 0.51 | 0.4943 | 149.43 | 3.3 |
| Frequent traders | 43 | 3.21 | 0.4973 | 159.42 | 3.43 |
| Infrequent traders | 37 | 4.22 | 0.5013 | 132.41 | 3.43 |
| Consistent winners | 11 | 26.38 | 0.5847 | 142.09 | 3.51 |
| Inconsistent | 69 | 0.06 | 0.4855 | 147.7 | 3.42 |

### Key insights (3)
- Greed days showed stronger profitability than Fear days (avg daily PnL 53.04 vs -37.24) and higher win rate (67.25% vs 36.56%).
- Risk was asymmetric: Fear days had a deeper drawdown proxy (-69.85) than Greed days (21.14).
- Behavior shifted mildly by sentiment: trades/day and leverage differed (Fear 96.57 trades/day, lev 3.39; Greed 96.93 trades/day, lev 3.47).

## Part C — Actionable Output
1. **Fear-day defensive rule:** For high-leverage and inconsistent traders, cap leverage near the low-leverage segment average and reduce trade frequency until sentiment exits Fear.
2. **Greed-day selective aggression:** Allow slightly higher trade frequency for consistent winners, while keeping position sizing constant to avoid oversized downside tails.

## Artifacts
- `outputs/daily_metrics.csv`
- `outputs/fear_vs_greed_comparison.csv`
- `outputs/segment_summary.csv`
- `outputs/pnl_by_sentiment.svg`
- `outputs/winrate_by_sentiment.svg`