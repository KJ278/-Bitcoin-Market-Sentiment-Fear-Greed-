"""HTTP client wrapper for Binance Futures Testnet."""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class BinanceApiError(Exception):
    """Raised when Binance returns an API-level error."""


@dataclass
class BinanceFuturesClient:
    api_key: str
    api_secret: str
    base_url: str = "https://testnet.binancefuture.com"
    timeout_seconds: int = 10

    def _sign_query(self, params: dict[str, Any]) -> str:
        query = urlencode(params, doseq=True)
        signature = hmac.new(
            self.api_secret.encode("utf-8"), query.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        return f"{query}&signature={signature}"

    def create_order(self, params: dict[str, Any]) -> dict[str, Any]:
        endpoint = "/fapi/v1/order"
        params = {**params, "timestamp": int(time.time() * 1000)}
        signed_query = self._sign_query(params)

        headers = {"X-MBX-APIKEY": self.api_key}
        url = f"{self.base_url}{endpoint}?{signed_query}"

        req = Request(url=url, headers=headers, method="POST")

        try:
            with urlopen(req, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
                payload = json.loads(raw)
                return payload
        except HTTPError as exc:
            raw = exc.read().decode("utf-8") if exc.fp else ""
            try:
                payload = json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                payload = {}
            message = payload.get("msg", raw or "Unknown Binance API error")
            code = payload.get("code", "N/A")
            raise BinanceApiError(f"Binance error {code}: {message}") from exc
        except URLError as exc:
            raise BinanceApiError(f"Network error while calling Binance: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise BinanceApiError("Binance returned a non-JSON response") from exc


class MockBinanceFuturesClient:
    """Mock client for local testing without API credentials."""

    def create_order(self, params: dict[str, Any]) -> dict[str, Any]:
        order_type = params.get("type", "MARKET")
        is_market = order_type == "MARKET"
        price = "0" if is_market else str(params.get("price", "0"))

        return {
            "clientOrderId": "mock-order-123",
            "cumQty": str(params.get("quantity")),
            "cumQuote": "0",
            "executedQty": str(params.get("quantity")) if is_market else "0",
            "orderId": 123456789,
            "avgPrice": price if not is_market else "64000.00",
            "origQty": str(params.get("quantity")),
            "price": price,
            "reduceOnly": False,
            "side": params.get("side"),
            "positionSide": "BOTH",
            "status": "FILLED" if is_market else "NEW",
            "stopPrice": "0",
            "closePosition": False,
            "symbol": params.get("symbol"),
            "timeInForce": params.get("timeInForce", "GTC"),
            "type": order_type,
            "updateTime": int(time.time() * 1000),
            "workingType": "CONTRACT_PRICE",
            "priceProtect": False,
        }
