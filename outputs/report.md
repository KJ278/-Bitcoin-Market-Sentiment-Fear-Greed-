# Bitcoin Market Sentiment vs Trader Behavior

- Source files: sentiment=fear_greed_index/sentiment.csv | trades=fear_greed_index/trades.csv

## Methodology
- Load and profile sentiment/trade CSV files (rows, columns, missing values, duplicates).
- Normalize timestamps to daily dates and align trade records with same-day sentiment.
- Compute daily metrics, compare Fear vs Greed periods, and build trader segments.

## Part A — Data preparation
- Sentiment: rows=25, cols=4, duplicates=0, missing={'timestamp': 0, 'value': 0, 'classification': 0, 'date': 0}
- Trades: rows=899, cols=6, duplicates=1, missing={'trader_id': 0, 'timestamp': 0, 'side': 0, 'trade_size': 0, 'leverage': 1, 'pnl': 0}
- Timestamp fields converted/aligned at daily level.

## Part B — Analysis
### Fear vs Greed

| Metric | Fear | Greed |
|---|---:|---:|
| Days | 16 | 7 |
| Avg daily PnL | -333.05 | 803.88 |
| Avg win rate | 0.3266 | 0.8244 |
| Drawdown proxy | -5328.74 | 0.0 |
| Avg trades/day | 35.31 | 35 |
| Avg leverage | 5.52 | 5.84 |

### Segments

| Segment | # Traders | Avg total PnL | Avg win rate | Avg trades | Avg leverage |
|---|---:|---:|---:|---:|---:|
| High leverage | 10 | -13.25 | 0.4523 | 45.1 | 5.88 |
| Low leverage | 10 | 41.07 | 0.4847 | 44.8 | 5.31 |
| Frequent traders | 10 | -20.92 | 0.4736 | 50.4 | 5.55 |
| Infrequent traders | 10 | 48.74 | 0.4634 | 39.5 | 5.64 |
| Consistent winners | 1 | 325.81 | 0.6111 | 36 | 5.28 |
| Inconsistent | 19 | -2.5 | 0.461 | 45.42 | 5.61 |

### Key insights
- Performance differs by sentiment: Fear avg PnL=-333.05 vs Greed avg PnL=803.88.
- Risk profile differs: drawdown proxy Fear=-5328.74 vs Greed=0.0.
- Behavior shifts: average trades/day and leverage are not identical across sentiment regimes.

## Part C — Actionable output
1. During Fear days, reduce leverage and position size for high-leverage/inconsistent segments.
2. During Greed days, allow higher trade frequency only for consistent winners while keeping risk caps fixed.