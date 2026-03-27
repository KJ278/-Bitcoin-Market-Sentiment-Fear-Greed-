# Bitcoin Market Sentiment vs Trader Behavior (Fear/Greed)

This project is configured so you can use **your own files** from a folder named:

- `fear_greed_index/`

## 1) Put your data in `fear_greed_index/`

Add two CSV files in that folder:

- a **sentiment** CSV (example schema you shared):
  - `timestamp` (Unix seconds) or `date`
  - `value`
  - `classification` (Fear / Extreme Fear / Neutral / Greed / Extreme Greed)
- a **trades** CSV:
  - required: date/timestamp + pnl
  - recommended: trader_id, side, trade_size, leverage

> File names can vary. The script will auto-detect sentiment/trades files by filename hints.

## 2) Run

```bash
python analysis.py
```

Default behavior:
- input folder: `fear_greed_index/`
- output folder: `outputs/`

## 3) Optional explicit file paths

```bash
python analysis.py \
  --sentiment fear_greed_index/my_sentiment.csv \
  --trades fear_greed_index/my_trades.csv \
  --outdir outputs
```

You can also change the input folder root:

```bash
python analysis.py --input-dir fear_greed_index --outdir outputs
```

## Generated deliverables

- `outputs/report.md` (methodology + insights + strategy ideas)
- `outputs/daily_metrics.csv`
- `outputs/fear_vs_greed_comparison.csv`
- `outputs/segment_summary.csv`
- `outputs/pnl_by_sentiment.svg`
- `outputs/winrate_by_sentiment.svg`

## Current repo examples

- `fear_greed_index/sentiment.csv`
- `fear_greed_index/trades.csv`
