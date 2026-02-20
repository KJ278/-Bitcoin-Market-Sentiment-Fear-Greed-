# Bitcoin Market Sentiment vs Trader Behavior (Fear/Greed)

This project is now built around your sample sentiment format:
- `timestamp` (Unix seconds)
- `value` (index value)
- `classification` (Fear / Extreme Fear / Neutral / Greed / Extreme Greed)
- `date` (YYYY-MM-DD)

and a trade file containing trader-level PnL activity.

## Files

- `analysis.py` — Reproducible analysis pipeline.
- `data/sentiment.csv` — Example sentiment file in your shown format.
- `data/trades.csv` — Example trades file.
- `outputs/` — Generated report, tables, and charts.

## Required trade columns

At minimum, the trade file must include:
- one date/timestamp column: `date` or `timestamp`
- one PnL column: `pnl` (or `profit`, `realized_pnl`, `net_pnl`)

Recommended columns for full analysis:
- `trader_id`
- `side` (`long`/`short` or buy/sell aliases)
- `trade_size`
- `leverage`

## Run

```bash
python analysis.py
```

Or with custom files:

```bash
python analysis.py --sentiment path/to/sentiment.csv --trades path/to/trades.csv --outdir outputs
```

## Deliverables generated

- `outputs/report.md` (methodology + insights + strategy ideas)
- `outputs/daily_metrics.csv`
- `outputs/fear_vs_greed_comparison.csv`
- `outputs/segment_summary.csv`
- `outputs/pnl_by_sentiment.svg`
- `outputs/winrate_by_sentiment.svg`
