# Bitcoin Market Sentiment vs Trader Behavior (Fear/Greed)

This repository contains a reproducible script-based analysis for:
1. Data preparation and alignment (daily level),
2. Fear vs Greed performance/behavior comparison,
3. Trader segmentation and actionable strategy rules.

## Repository contents

- `analysis.py` — End-to-end analysis script (stdlib-only Python).
- `data/sentiment.csv` — Sentiment dataset used by the script.
- `data/trades.csv` — Trader-level trades dataset used by the script.
- `outputs/` — Generated tables, charts, and write-up.

## Setup

No external packages are required.

```bash
python --version
python analysis.py
```

## How to run

```bash
python analysis.py
```

After running, inspect:
- `outputs/report.md` (short write-up)
- `outputs/daily_metrics.csv`
- `outputs/fear_vs_greed_comparison.csv`
- `outputs/segment_summary.csv`
- `outputs/pnl_by_sentiment.svg`
- `outputs/winrate_by_sentiment.svg`

## Deliverable summary (1-page equivalent)

See `outputs/report.md` for:
- methodology,
- evidence-backed insights,
- strategy recommendations.
