"""CLI entry point for placing Binance Futures testnet orders."""

from __future__ import annotations

import argparse
import os
import sys

from bot.client import BinanceApiError, BinanceFuturesClient, MockBinanceFuturesClient
from bot.logging_config import setup_logger
from bot.orders import OrderRequest, OrderService
from bot.validators import ValidationError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Place MARKET/LIMIT orders on Binance Futures Testnet (USDT-M)."
    )
    parser.add_argument("--symbol", required=True, help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("--side", required=True, help="BUY or SELL")
    parser.add_argument("--order-type", required=True, help="MARKET or LIMIT")
    parser.add_argument("--quantity", required=True, help="Order quantity")
    parser.add_argument("--price", help="Required for LIMIT orders")
    parser.add_argument(
        "--log-file",
        default="logs/trading_bot.log",
        help="Path to log file (default: logs/trading_bot.log)",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock API responses instead of real Binance API calls",
    )
    return parser.parse_args()


def build_client(use_mock: bool):
    if use_mock:
        return MockBinanceFuturesClient()

    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    if not api_key or not api_secret:
        raise ValidationError(
            "BINANCE_API_KEY and BINANCE_API_SECRET environment variables are required"
        )

    return BinanceFuturesClient(api_key=api_key, api_secret=api_secret)


def print_summary(request: OrderRequest, response: dict) -> None:
    print("\n=== Order Request Summary ===")
    print(f"Symbol     : {request.symbol}")
    print(f"Side       : {request.side}")
    print(f"Type       : {request.order_type}")
    print(f"Quantity   : {request.quantity}")
    if request.price:
        print(f"Price      : {request.price}")

    print("\n=== Order Response ===")
    print(f"Order ID   : {response.get('orderId', 'N/A')}")
    print(f"Status     : {response.get('status', 'N/A')}")
    print(f"ExecutedQty: {response.get('executedQty', 'N/A')}")
    print(f"Avg Price  : {response.get('avgPrice', 'N/A')}")


def main() -> int:
    args = parse_args()
    logger = setup_logger(args.log_file)

    request = OrderRequest(
        symbol=args.symbol,
        side=args.side,
        order_type=args.order_type,
        quantity=args.quantity,
        price=args.price,
    )

    try:
        client = build_client(args.mock)
        service = OrderService(client=client, logger=logger)
        response = service.place_order(request)
    except ValidationError as exc:
        logger.error("Validation failed: %s", exc)
        print(f"\n❌ Validation error: {exc}")
        return 1
    except BinanceApiError as exc:
        logger.error("API call failed: %s", exc)
        print(f"\n❌ API error: {exc}")
        return 2
    except Exception as exc:
        logger.exception("Unhandled application error")
        print(f"\n❌ Unexpected error: {exc}")
        return 3

    print_summary(request, response)
    print("\n✅ Order submitted successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
