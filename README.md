# Binance Futures Testnet Trading Bot (Simplified)

A small Python CLI application that places **MARKET** and **LIMIT** orders on **Binance Futures Testnet (USDT-M)**.

## Features

- Place `MARKET` and `LIMIT` orders
- Supports both `BUY` and `SELL`
- CLI arguments with validation
- Clear terminal output for request and response summary
- Structured code with separate API/client, service logic, validation, and logging modules
- Logs API requests, responses, and errors to file
- Handles invalid input, API errors, and network failures
- Bonus: `--mock` mode for local/demo runs without credentials

## Project Structure

```text
.
├── bot/
│   ├── __init__.py
│   ├── client.py
│   ├── logging_config.py
│   ├── orders.py
│   └── validators.py
├── cli.py
├── logs/
│   ├── market_order.log
│   └── limit_order.log
├── requirements.txt
└── README.md
```

## Prerequisites

- Python 3.9+
- Binance Futures Testnet account
- Testnet API credentials
- Base URL: `https://testnet.binancefuture.com`

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Export credentials (for real API calls):

```bash
export BINANCE_API_KEY="your_testnet_api_key"
export BINANCE_API_SECRET="your_testnet_api_secret"
```

## Usage

### MARKET order

```bash
python cli.py \
  --symbol BTCUSDT \
  --side BUY \
  --order-type MARKET \
  --quantity 0.001
```

### LIMIT order

```bash
python cli.py \
  --symbol BTCUSDT \
  --side SELL \
  --order-type LIMIT \
  --quantity 0.001 \
  --price 75000
```

### Mock mode (no API credentials required)

```bash
python cli.py \
  --symbol BTCUSDT \
  --side BUY \
  --order-type MARKET \
  --quantity 0.001 \
  --mock
```

You can also set custom log output path:

```bash
python cli.py ... --log-file logs/custom.log
```

## Output

The CLI prints:

- Order request summary
- Order response details:
  - `orderId`
  - `status`
  - `executedQty`
  - `avgPrice` (if available)
- Success/failure message

## Logging

- Default log file: `logs/trading_bot.log`
- Includes order requests, responses, and errors with timestamps and log levels.

Included sample logs:

- `logs/market_order.log` (MARKET order)
- `logs/limit_order.log` (LIMIT order)

## Assumptions

- Symbols are validated with basic formatting rules (`BTCUSDT` style), while exact symbol validity is verified by Binance API.
- Quantity and price precision/step-size constraints are enforced by Binance exchange filters (not pre-fetched in this simplified version).
- LIMIT orders are submitted with `timeInForce=GTC`.
- `avgPrice` may be `0`/empty for non-filled orders.
