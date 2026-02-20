#!/usr/bin/env python3
"""Fear/Greed sentiment vs trader behavior analysis.

Designed to work with sentiment data shaped like:
- timestamp (unix seconds)
- value
- classification
- date

and trade data with common field aliases for trader, side, size, leverage, and pnl.
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from statistics import mean, median


def normalize_key(name: str) -> str:
    return ''.join(ch.lower() for ch in name if ch.isalnum())


def parse_date(value: str):
    raw = (value or '').strip()
    if not raw:
        return None

    if raw.isdigit():
        iv = int(raw)
        if iv > 10_000_000_000:  # ms
            iv //= 1000
        try:
            return datetime.utcfromtimestamp(iv).date()
        except Exception:
            pass

    for fmt in ('%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%m/%d/%Y', '%d-%m-%Y', '%Y/%m/%d'):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(raw.replace('Z', '+00:00')).date()
    except Exception:
        return None


def to_float(value: str):
    raw = (value or '').strip().replace(',', '')
    if raw == '':
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def profile_rows(rows, headers):
    missing = {h: 0 for h in headers}
    for row in rows:
        for h in headers:
            if (row.get(h) or '').strip() == '':
                missing[h] += 1
    duplicates = len(rows) - len({tuple((h, row.get(h, '')) for h in headers) for row in rows})
    return {'rows': len(rows), 'cols': len(headers), 'missing': missing, 'duplicates': duplicates}


def read_csv(path: Path):
    with path.open(newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        headers = reader.fieldnames or []
    return rows, headers


def find_col(headers, aliases, required=False):
    normalized = {normalize_key(h): h for h in headers}
    for alias in aliases:
        if alias in normalized:
            return normalized[alias]
    if required:
        raise ValueError(f'Missing required column. Expected one of aliases: {aliases}. Found: {headers}')
    return None


def load_sentiment(path: Path):
    rows, headers = read_csv(path)
    date_col = find_col(headers, ['date', 'day'])
    ts_col = find_col(headers, ['timestamp', 'time', 'datetime'])
    value_col = find_col(headers, ['value', 'feargreedvalue', 'indexvalue'])
    cls_col = find_col(headers, ['classification', 'sentiment', 'label'])

    data = {}
    for row in rows:
        d = parse_date(row.get(date_col, '')) if date_col else None
        if d is None and ts_col:
            d = parse_date(row.get(ts_col, ''))
        if d is None:
            continue

        val = to_float(row.get(value_col, '')) if value_col else None
        cls = (row.get(cls_col, '') or '').strip()
        if not cls:
            cls = 'Fear' if (val is not None and val < 45) else ('Greed' if (val is not None and val > 55) else 'Neutral')

        cls = cls.title()
        if cls == 'Extreme Fear':
            cls = 'Fear'
        elif cls == 'Extreme Greed':
            cls = 'Greed'

        data[d] = {'value': val, 'sentiment': cls}

    return rows, headers, data


def load_trades(path: Path):
    rows, headers = read_csv(path)
    date_col = find_col(headers, ['date', 'day'])
    ts_col = find_col(headers, ['timestamp', 'time', 'datetime', 'opentime'], required=not date_col)
    trader_col = find_col(headers, ['traderid', 'account', 'accountid', 'uid', 'user'])
    side_col = find_col(headers, ['side', 'direction', 'position', 'longshort'])
    size_col = find_col(headers, ['tradesize', 'size', 'qty', 'quantity', 'notional'])
    lev_col = find_col(headers, ['leverage', 'lev', 'marginmultiple'])
    pnl_col = find_col(headers, ['pnl', 'realizedpnl', 'profit', 'netpnl'], required=True)

    trades = []
    for row in rows:
        d = parse_date(row.get(date_col, '')) if date_col else None
        if d is None and ts_col:
            d = parse_date(row.get(ts_col, ''))
        if d is None:
            continue

        side = (row.get(side_col, '') if side_col else '').strip().lower()
        if side in ('buy', 'bull', 'longs'):
            side = 'long'
        if side in ('sell', 'bear', 'shorts'):
            side = 'short'

        trades.append(
            {
                'date': d,
                'trader_id': (row.get(trader_col, '') if trader_col else '').strip() or 'UNKNOWN',
                'side': side,
                'trade_size': to_float(row.get(size_col, '')) if size_col else 0.0,
                'leverage': to_float(row.get(lev_col, '')) if lev_col else None,
                'pnl': to_float(row.get(pnl_col, '')) or 0.0,
            }
        )

    return rows, headers, trades


def summarize_daily(trades, sentiment_map):
    agg = defaultdict(lambda: {'pnl': 0.0, 'wins': 0, 'trades': 0, 'sizes': [], 'levs': [], 'long': 0, 'short': 0, 'traders': set()})
    for t in trades:
        rec = agg[t['date']]
        rec['pnl'] += t['pnl']
        rec['wins'] += 1 if t['pnl'] > 0 else 0
        rec['trades'] += 1
        if t['trade_size'] is not None:
            rec['sizes'].append(t['trade_size'])
        if t['leverage'] is not None:
            rec['levs'].append(t['leverage'])
        if t['side'] == 'long':
            rec['long'] += 1
        elif t['side'] == 'short':
            rec['short'] += 1
        rec['traders'].add(t['trader_id'])

    out = []
    for d in sorted(agg.keys()):
        rec = agg[d]
        s = sentiment_map.get(d, {'sentiment': 'Unknown', 'value': None})
        out.append(
            {
                'date': d.isoformat(),
                'sentiment': s['sentiment'],
                'fear_greed_value': s['value'],
                'num_trades': rec['trades'],
                'daily_pnl': round(rec['pnl'], 2),
                'win_rate': round(rec['wins'] / rec['trades'], 4) if rec['trades'] else 0.0,
                'avg_trade_size': round(mean(rec['sizes']), 2) if rec['sizes'] else 0.0,
                'avg_leverage': round(mean(rec['levs']), 2) if rec['levs'] else 0.0,
                'long_short_ratio': round(rec['long'] / rec['short'], 3) if rec['short'] else None,
                'active_traders': len(rec['traders']),
            }
        )
    return out


def compare_fear_greed(daily_rows):
    grouped = defaultdict(list)
    for r in daily_rows:
        if r['sentiment'] in ('Fear', 'Greed'):
            grouped[r['sentiment']].append(r)

    summary = {}
    for k, rows in grouped.items():
        pnls = [r['daily_pnl'] for r in rows]
        win = [r['win_rate'] for r in rows]
        trades = [r['num_trades'] for r in rows]
        levs = [r['avg_leverage'] for r in rows if r['avg_leverage']]

        cum = 0.0
        peak = 0.0
        dd = 0.0
        for p in pnls:
            cum += p
            peak = max(peak, cum)
            dd = min(dd, cum - peak)

        summary[k] = {
            'days': len(rows),
            'avg_daily_pnl': round(mean(pnls), 2) if pnls else 0.0,
            'median_daily_pnl': round(median(pnls), 2) if pnls else 0.0,
            'avg_win_rate': round(mean(win), 4) if win else 0.0,
            'avg_trades_per_day': round(mean(trades), 2) if trades else 0.0,
            'avg_leverage': round(mean(levs), 2) if levs else 0.0,
            'drawdown_proxy': round(dd, 2),
        }
    return summary


def segment_traders(trades):
    per = defaultdict(lambda: {'pnl': 0.0, 'wins': 0, 'trades': 0, 'lev': [], 'size': []})
    for t in trades:
        p = per[t['trader_id']]
        p['pnl'] += t['pnl']
        p['wins'] += 1 if t['pnl'] > 0 else 0
        p['trades'] += 1
        if t['leverage'] is not None:
            p['lev'].append(t['leverage'])
        if t['trade_size'] is not None:
            p['size'].append(t['trade_size'])

    rows = []
    for trader_id, p in per.items():
        rows.append(
            {
                'trader_id': trader_id,
                'total_pnl': p['pnl'],
                'trades': p['trades'],
                'win_rate': p['wins'] / p['trades'] if p['trades'] else 0.0,
                'avg_leverage': mean(p['lev']) if p['lev'] else 0.0,
                'avg_trade_size': mean(p['size']) if p['size'] else 0.0,
            }
        )

    med_lev = median([r['avg_leverage'] for r in rows]) if rows else 0.0
    med_freq = median([r['trades'] for r in rows]) if rows else 0.0

    segments = {
        'High leverage': [r for r in rows if r['avg_leverage'] >= med_lev],
        'Low leverage': [r for r in rows if r['avg_leverage'] < med_lev],
        'Frequent traders': [r for r in rows if r['trades'] >= med_freq],
        'Infrequent traders': [r for r in rows if r['trades'] < med_freq],
        'Consistent winners': [r for r in rows if r['win_rate'] >= 0.55],
        'Inconsistent': [r for r in rows if r['win_rate'] < 0.55],
    }

    out = {}
    for name, members in segments.items():
        if not members:
            continue
        out[name] = {
            'n_traders': len(members),
            'avg_total_pnl': round(mean([m['total_pnl'] for m in members]), 2),
            'avg_win_rate': round(mean([m['win_rate'] for m in members]), 4),
            'avg_trades': round(mean([m['trades'] for m in members]), 2),
            'avg_leverage': round(mean([m['avg_leverage'] for m in members]), 2),
        }
    return out


def write_csv(path: Path, rows):
    if not rows:
        return
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_svg_bar(path: Path, data: dict, title: str, y_label: str):
    width, height, margin = 700, 380, 45
    keys = list(data.keys())
    vals = [data[k] for k in keys]
    if not vals:
        vals = [0]
    min_v, max_v = min(vals), max(vals)
    span = max(max_v - min_v, 1.0)

    bar_w = (width - 2 * margin) / max(1, len(keys))
    zero_y = height - margin - ((0 - min_v) / span) * (height - 2 * margin)

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">']
    parts.append(f'<text x="{width/2}" y="24" text-anchor="middle" font-size="16">{title}</text>')
    parts.append(f'<line x1="{margin}" y1="{height-margin}" x2="{width-margin}" y2="{height-margin}" stroke="black"/>')
    parts.append(f'<line x1="{margin}" y1="{margin}" x2="{margin}" y2="{height-margin}" stroke="black"/>')
    parts.append(f'<line x1="{margin}" y1="{zero_y:.1f}" x2="{width-margin}" y2="{zero_y:.1f}" stroke="#888" stroke-dasharray="4 3"/>')

    for i, (k, v) in enumerate(zip(keys, vals)):
        x = margin + i * bar_w + 10
        y_v = height - margin - ((v - min_v) / span) * (height - 2 * margin)
        y0 = zero_y
        rect_y = min(y0, y_v)
        rect_h = max(1.0, abs(y_v - y0))
        color = '#4e79a7' if v >= 0 else '#e15759'
        parts.append(f'<rect x="{x:.1f}" y="{rect_y:.1f}" width="{bar_w-20:.1f}" height="{rect_h:.1f}" fill="{color}"/>')
        parts.append(f'<text x="{x + (bar_w-20)/2:.1f}" y="{height-margin+18}" text-anchor="middle" font-size="12">{k}</text>')
        parts.append(f'<text x="{x + (bar_w-20)/2:.1f}" y="{rect_y-6:.1f}" text-anchor="middle" font-size="11">{v:.2f}</text>')

    parts.append(f'<text x="14" y="{height/2}" transform="rotate(-90, 14, {height/2})" text-anchor="middle" font-size="12">{y_label}</text>')
    parts.append('</svg>')
    path.write_text('\n'.join(parts))


def build_report(out_dir: Path, sent_profile, trade_profile, comp, seg):
    fear = comp.get('Fear', {})
    greed = comp.get('Greed', {})

    lines = [
        '# Bitcoin Market Sentiment vs Trader Behavior',
        '',
        '## Methodology',
        '- Load and profile sentiment/trade CSV files (rows, columns, missing values, duplicates).',
        '- Normalize timestamps to daily dates and align trade records with same-day sentiment.',
        '- Compute daily metrics, compare Fear vs Greed periods, and build trader segments.',
        '',
        '## Part A — Data preparation',
        f"- Sentiment: rows={sent_profile['rows']}, cols={sent_profile['cols']}, duplicates={sent_profile['duplicates']}, missing={sent_profile['missing']}",
        f"- Trades: rows={trade_profile['rows']}, cols={trade_profile['cols']}, duplicates={trade_profile['duplicates']}, missing={trade_profile['missing']}",
        '- Timestamp fields converted/aligned at daily level.',
        '',
        '## Part B — Analysis',
        '### Fear vs Greed',
        '',
        '| Metric | Fear | Greed |',
        '|---|---:|---:|',
        f"| Days | {fear.get('days', 0)} | {greed.get('days', 0)} |",
        f"| Avg daily PnL | {fear.get('avg_daily_pnl', 0)} | {greed.get('avg_daily_pnl', 0)} |",
        f"| Avg win rate | {fear.get('avg_win_rate', 0)} | {greed.get('avg_win_rate', 0)} |",
        f"| Drawdown proxy | {fear.get('drawdown_proxy', 0)} | {greed.get('drawdown_proxy', 0)} |",
        f"| Avg trades/day | {fear.get('avg_trades_per_day', 0)} | {greed.get('avg_trades_per_day', 0)} |",
        f"| Avg leverage | {fear.get('avg_leverage', 0)} | {greed.get('avg_leverage', 0)} |",
        '',
        '### Segments',
        '',
        '| Segment | # Traders | Avg total PnL | Avg win rate | Avg trades | Avg leverage |',
        '|---|---:|---:|---:|---:|---:|',
    ]

    for k, v in seg.items():
        lines.append(f"| {k} | {v['n_traders']} | {v['avg_total_pnl']} | {v['avg_win_rate']} | {v['avg_trades']} | {v['avg_leverage']} |")

    lines.extend(
        [
            '',
            '### Key insights',
            f"- Performance differs by sentiment: Fear avg PnL={fear.get('avg_daily_pnl',0)} vs Greed avg PnL={greed.get('avg_daily_pnl',0)}.",
            f"- Risk profile differs: drawdown proxy Fear={fear.get('drawdown_proxy',0)} vs Greed={greed.get('drawdown_proxy',0)}.",
            f"- Behavior shifts: avg trades/day and leverage differ between Fear and Greed regimes.",
            '',
            '## Part C — Actionable output',
            '1. During Fear days, reduce leverage and position size for high-leverage/inconsistent segments.',
            '2. During Greed days, allow higher trade frequency only for consistent winners while keeping risk caps fixed.',
        ]
    )

    (out_dir / 'report.md').write_text('\n'.join(lines))


def main():
    parser = argparse.ArgumentParser(description='Fear/Greed trader behavior analysis')
    parser.add_argument('--sentiment', default='data/sentiment.csv', help='Path to sentiment CSV')
    parser.add_argument('--trades', default='data/trades.csv', help='Path to trades CSV')
    parser.add_argument('--outdir', default='outputs', help='Output directory')
    args = parser.parse_args()

    out_dir = Path(args.outdir)
    out_dir.mkdir(parents=True, exist_ok=True)

    sent_rows, sent_headers, sentiment = load_sentiment(Path(args.sentiment))
    trade_rows, trade_headers, trades = load_trades(Path(args.trades))

    sent_profile = profile_rows(sent_rows, sent_headers)
    trade_profile = profile_rows(trade_rows, trade_headers)

    daily = summarize_daily(trades, sentiment)
    comp = compare_fear_greed(daily)
    seg = segment_traders(trades)

    write_csv(out_dir / 'daily_metrics.csv', daily)
    write_csv(out_dir / 'fear_vs_greed_comparison.csv', [{'sentiment': k, **v} for k, v in comp.items()])
    write_csv(out_dir / 'segment_summary.csv', [{'segment': k, **v} for k, v in seg.items()])
    write_svg_bar(out_dir / 'pnl_by_sentiment.svg', {k: v['avg_daily_pnl'] for k, v in comp.items()}, 'Average Daily PnL by Sentiment', 'PnL')
    write_svg_bar(out_dir / 'winrate_by_sentiment.svg', {k: 100 * v['avg_win_rate'] for k, v in comp.items()}, 'Win Rate by Sentiment', 'Win rate %')
    build_report(out_dir, sent_profile, trade_profile, comp, seg)

    print('Analysis complete.')
    print(f'Sentiment records: {len(sentiment)} | Trades: {len(trades)} | Output dir: {out_dir}')


if __name__ == '__main__':
    main()
