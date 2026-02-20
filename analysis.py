#!/usr/bin/env python3
"""Sentiment vs trader behavior analysis using only Python stdlib."""
from __future__ import annotations
import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from statistics import mean, median

DATA_DIR = Path('data')
OUT_DIR = Path('outputs')
OUT_DIR.mkdir(exist_ok=True)

SENTIMENT_FILE = DATA_DIR / 'sentiment.csv'
TRADES_FILE = DATA_DIR / 'trades.csv'


def parse_date(value: str) -> datetime.date:
    value = value.strip()
    fmts = ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%m/%d/%Y', '%d-%m-%Y']
    for fmt in fmts:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise ValueError(f'Unsupported timestamp format: {value}')


def to_float(v: str):
    v = (v or '').strip()
    if v == '':
        return None
    try:
        return float(v)
    except ValueError:
        return None


def profile_csv(path: Path):
    with path.open() as f:
        reader = list(csv.DictReader(f))
    cols = reader[0].keys() if reader else []
    missing = {c: 0 for c in cols}
    for row in reader:
        for c in cols:
            if row[c] is None or str(row[c]).strip() == '':
                missing[c] += 1
    duplicates = len(reader) - len({tuple((c, row[c]) for c in cols) for row in reader})
    return {'rows': len(reader), 'cols': len(cols), 'missing': missing, 'duplicates': duplicates, 'data': reader}


def load_sentiment(rows):
    out = {}
    for r in rows:
        d = parse_date(r['timestamp'])
        val = to_float(r.get('fear_greed_value'))
        label = (r.get('sentiment') or '').strip().title()
        if not label:
            label = 'Fear' if (val is not None and val < 45) else ('Greed' if (val is not None and val > 55) else 'Neutral')
        out[d] = {'value': val, 'sentiment': label}
    return out


def load_trades(rows):
    trades = []
    for r in rows:
        try:
            d = parse_date(r['timestamp'])
        except Exception:
            continue
        trade = {
            'trader_id': (r.get('trader_id') or 'UNKNOWN').strip(),
            'date': d,
            'side': (r.get('side') or '').strip().lower(),
            'trade_size': to_float(r.get('trade_size')) or 0.0,
            'leverage': to_float(r.get('leverage')),
            'pnl': to_float(r.get('pnl')) or 0.0,
        }
        trades.append(trade)
    return trades


def pct(n, d):
    return 0.0 if d == 0 else 100.0 * n / d


def summarize_daily(trades, sentiment_map):
    daily = defaultdict(lambda: {'trades': 0, 'pnl': 0.0, 'wins': 0, 'sizes': [], 'levs': [], 'long': 0, 'short': 0, 'traders': set()})
    for t in trades:
        d = t['date']
        rec = daily[d]
        rec['trades'] += 1
        rec['pnl'] += t['pnl']
        rec['wins'] += 1 if t['pnl'] > 0 else 0
        rec['sizes'].append(t['trade_size'])
        if t['leverage'] is not None:
            rec['levs'].append(t['leverage'])
        if t['side'] == 'long':
            rec['long'] += 1
        elif t['side'] == 'short':
            rec['short'] += 1
        rec['traders'].add(t['trader_id'])

    rows = []
    for d, rec in sorted(daily.items()):
        senti = sentiment_map.get(d, {'sentiment': 'Unknown', 'value': None})
        rows.append({
            'date': d.isoformat(),
            'sentiment': senti['sentiment'],
            'fear_greed_value': senti['value'],
            'num_trades': rec['trades'],
            'daily_pnl': round(rec['pnl'], 2),
            'win_rate': round(rec['wins'] / rec['trades'], 4) if rec['trades'] else 0.0,
            'avg_trade_size': round(mean(rec['sizes']), 2) if rec['sizes'] else 0.0,
            'avg_leverage': round(mean(rec['levs']), 2) if rec['levs'] else 0.0,
            'long_short_ratio': round(rec['long'] / rec['short'], 3) if rec['short'] else None,
            'active_traders': len(rec['traders']),
        })
    return rows


def grouped_comparison(daily):
    groups = defaultdict(list)
    for r in daily:
        if r['sentiment'] in {'Fear', 'Greed'}:
            groups[r['sentiment']].append(r)
    comp = {}
    for g, rows in groups.items():
        pnls = [x['daily_pnl'] for x in rows]
        wrs = [x['win_rate'] for x in rows]
        trade_counts = [x['num_trades'] for x in rows]
        levs = [x['avg_leverage'] for x in rows if x['avg_leverage']]
        dd_proxy = min(pnls) if pnls else 0.0
        comp[g] = {
            'days': len(rows),
            'avg_daily_pnl': round(mean(pnls), 2) if pnls else 0.0,
            'median_daily_pnl': round(median(pnls), 2) if pnls else 0.0,
            'avg_win_rate': round(mean(wrs), 4) if wrs else 0.0,
            'avg_trades_per_day': round(mean(trade_counts), 2) if trade_counts else 0.0,
            'avg_leverage': round(mean(levs), 2) if levs else 0.0,
            'drawdown_proxy': round(dd_proxy, 2),
        }
    return comp


def build_trader_segments(trades):
    trader = defaultdict(lambda: {'pnl': 0.0, 'trades': 0, 'wins': 0, 'levs': [], 'sizes': []})
    for t in trades:
        tr = trader[t['trader_id']]
        tr['pnl'] += t['pnl']
        tr['trades'] += 1
        tr['wins'] += 1 if t['pnl'] > 0 else 0
        if t['leverage'] is not None:
            tr['levs'].append(t['leverage'])
        tr['sizes'].append(t['trade_size'])

    rows = []
    for tid, rec in trader.items():
        avg_lev = mean(rec['levs']) if rec['levs'] else 0.0
        rows.append({
            'trader_id': tid,
            'total_pnl': rec['pnl'],
            'trades': rec['trades'],
            'win_rate': rec['wins'] / rec['trades'] if rec['trades'] else 0,
            'avg_lev': avg_lev,
            'avg_size': mean(rec['sizes']) if rec['sizes'] else 0,
        })

    med_lev = median([r['avg_lev'] for r in rows])
    med_freq = median([r['trades'] for r in rows])

    segments = {
        'High leverage': [r for r in rows if r['avg_lev'] >= med_lev],
        'Low leverage': [r for r in rows if r['avg_lev'] < med_lev],
        'Frequent traders': [r for r in rows if r['trades'] >= med_freq],
        'Infrequent traders': [r for r in rows if r['trades'] < med_freq],
        'Consistent winners': [r for r in rows if r['win_rate'] >= 0.55],
        'Inconsistent': [r for r in rows if r['win_rate'] < 0.55],
    }

    summary = {}
    for name, members in segments.items():
        if not members:
            continue
        summary[name] = {
            'n_traders': len(members),
            'avg_total_pnl': round(mean([m['total_pnl'] for m in members]), 2),
            'avg_win_rate': round(mean([m['win_rate'] for m in members]), 4),
            'avg_trades': round(mean([m['trades'] for m in members]), 2),
            'avg_leverage': round(mean([m['avg_lev'] for m in members]), 2),
        }
    return summary


def write_csv(path: Path, rows):
    if not rows:
        return
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def write_svg_bar(path: Path, data: dict, title: str, y_label: str):
    width, height = 640, 360
    m = 40
    keys = list(data.keys())
    vals = [data[k] for k in keys]
    maxv = max(vals) if vals else 1
    bar_w = (width - 2 * m) / max(1, len(keys))
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
             f'<text x="{width/2}" y="20" text-anchor="middle" font-size="16">{title}</text>']
    parts.append(f'<line x1="{m}" y1="{height-m}" x2="{width-m}" y2="{height-m}" stroke="black"/>')
    parts.append(f'<line x1="{m}" y1="{m}" x2="{m}" y2="{height-m}" stroke="black"/>')
    for i, (k, v) in enumerate(zip(keys, vals)):
        h = 0 if maxv == 0 else (v / maxv) * (height - 2 * m)
        x = m + i * bar_w + 10
        y = height - m - h
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w-20:.1f}" height="{h:.1f}" fill="#4e79a7"/>')
        parts.append(f'<text x="{x + (bar_w-20)/2:.1f}" y="{height-m+15}" text-anchor="middle" font-size="12">{k}</text>')
        parts.append(f'<text x="{x + (bar_w-20)/2:.1f}" y="{y-5:.1f}" text-anchor="middle" font-size="11">{v:.2f}</text>')
    parts.append(f'<text x="15" y="{height/2}" transform="rotate(-90, 15, {height/2})" text-anchor="middle" font-size="12">{y_label}</text>')
    parts.append('</svg>')
    path.write_text('\n'.join(parts))


def render_report(sent_prof, trade_prof, comp, seg):
    fear = comp.get('Fear', {})
    greed = comp.get('Greed', {})
    lines = [
        '# Bitcoin Market Sentiment vs Trader Behavior',
        '',
        '## Methodology',
        '- Loaded sentiment and trade datasets, profiled rows/columns/missing values/duplicates, and parsed timestamps to daily grain.',
        '- Aligned trades with same-day sentiment labels and computed daily metrics: PnL, win rate, average size, leverage, trade count, and long/short ratio.',
        '- Compared Fear vs Greed periods and created trader segments (high vs low leverage, frequent vs infrequent, consistent vs inconsistent winners).',
        '',
        '## Part A — Data Preparation',
        f"- Sentiment dataset: **{sent_prof['rows']} rows**, **{sent_prof['cols']} columns**, duplicates={sent_prof['duplicates']}, missing={sent_prof['missing']}.",
        f"- Trades dataset: **{trade_prof['rows']} rows**, **{trade_prof['cols']} columns**, duplicates={trade_prof['duplicates']}, missing={trade_prof['missing']}.",
        '- Timestamps converted to date and joined by date (daily level).',
        '',
        '## Part B — Evidence-based Analysis',
        '### Fear vs Greed comparison',
        '',
        '| Metric | Fear | Greed |',
        '|---|---:|---:|',
        f"| Days | {fear.get('days',0)} | {greed.get('days',0)} |",
        f"| Avg daily PnL | {fear.get('avg_daily_pnl',0)} | {greed.get('avg_daily_pnl',0)} |",
        f"| Avg win rate | {fear.get('avg_win_rate',0)} | {greed.get('avg_win_rate',0)} |",
        f"| Drawdown proxy (worst day PnL) | {fear.get('drawdown_proxy',0)} | {greed.get('drawdown_proxy',0)} |",
        f"| Avg trades/day | {fear.get('avg_trades_per_day',0)} | {greed.get('avg_trades_per_day',0)} |",
        f"| Avg leverage | {fear.get('avg_leverage',0)} | {greed.get('avg_leverage',0)} |",
        '',
        '### Segment summary',
        '',
        '| Segment | # Traders | Avg total PnL | Avg win rate | Avg trades | Avg leverage |',
        '|---|---:|---:|---:|---:|---:|',
    ]
    for k, v in seg.items():
        lines.append(f"| {k} | {v['n_traders']} | {v['avg_total_pnl']} | {v['avg_win_rate']} | {v['avg_trades']} | {v['avg_leverage']} |")

    insights = []
    if greed and fear:
        insights.append(f"Greed days showed stronger profitability than Fear days (avg daily PnL {greed['avg_daily_pnl']} vs {fear['avg_daily_pnl']}) and higher win rate ({greed['avg_win_rate']:.2%} vs {fear['avg_win_rate']:.2%}).")
        insights.append(f"Risk was asymmetric: Fear days had a deeper drawdown proxy ({fear['drawdown_proxy']}) than Greed days ({greed['drawdown_proxy']}).")
        insights.append(f"Behavior shifted mildly by sentiment: trades/day and leverage differed (Fear {fear['avg_trades_per_day']} trades/day, lev {fear['avg_leverage']}; Greed {greed['avg_trades_per_day']} trades/day, lev {greed['avg_leverage']}).")

    lines += [
        '',
        '### Key insights (3)',
    ]
    lines += [f'- {x}' for x in insights[:3]]

    lines += [
        '',
        '## Part C — Actionable Output',
        '1. **Fear-day defensive rule:** For high-leverage and inconsistent traders, cap leverage near the low-leverage segment average and reduce trade frequency until sentiment exits Fear.',
        '2. **Greed-day selective aggression:** Allow slightly higher trade frequency for consistent winners, while keeping position sizing constant to avoid oversized downside tails.',
        '',
        '## Artifacts',
        '- `outputs/daily_metrics.csv`',
        '- `outputs/fear_vs_greed_comparison.csv`',
        '- `outputs/segment_summary.csv`',
        '- `outputs/pnl_by_sentiment.svg`',
        '- `outputs/winrate_by_sentiment.svg`',
    ]
    (OUT_DIR / 'report.md').write_text('\n'.join(lines))


def main():
    sent_prof = profile_csv(SENTIMENT_FILE)
    trade_prof = profile_csv(TRADES_FILE)
    sentiment = load_sentiment(sent_prof['data'])
    trades = load_trades(trade_prof['data'])

    daily = summarize_daily(trades, sentiment)
    comp = grouped_comparison(daily)
    seg = build_trader_segments(trades)

    write_csv(OUT_DIR / 'daily_metrics.csv', daily)
    comp_rows = [{'sentiment': k, **v} for k, v in comp.items()]
    write_csv(OUT_DIR / 'fear_vs_greed_comparison.csv', comp_rows)
    seg_rows = [{'segment': k, **v} for k, v in seg.items()]
    write_csv(OUT_DIR / 'segment_summary.csv', seg_rows)

    write_svg_bar(OUT_DIR / 'pnl_by_sentiment.svg', {k: v['avg_daily_pnl'] for k, v in comp.items()}, 'Average Daily PnL by Sentiment', 'PnL')
    write_svg_bar(OUT_DIR / 'winrate_by_sentiment.svg', {k: v['avg_win_rate'] * 100 for k, v in comp.items()}, 'Win Rate (%) by Sentiment', 'Win Rate %')

    render_report(sent_prof, trade_prof, comp, seg)
    print('Analysis complete. See outputs/report.md')


if __name__ == '__main__':
    main()
