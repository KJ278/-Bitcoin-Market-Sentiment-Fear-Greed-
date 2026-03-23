"""Order placement service layer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .client import BinanceApiError
from .validators import (
    validate_order_type,
    validate_positive_decimal,
    validate_price_for_limit,
    validate_side,
    validate_symbol,
)


@dataclass
class OrderRequest:
    symbol: str
    side: str
    order_type: str
    quantity: str
    price: str | None = None


class OrderService:
    def __init__(self, client: Any, logger: Any):
        self.client = client
        self.logger = logger

    def validate(self, request: OrderRequest) -> OrderRequest:
        symbol = validate_symbol(request.symbol)
        side = validate_side(request.side)
        order_type = validate_order_type(request.order_type)
        quantity = validate_positive_decimal(request.quantity, "quantity")
        price = validate_price_for_limit(order_type, request.price)

        return OrderRequest(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
        )

    def place_order(self, request: OrderRequest) -> dict[str, Any]:
        validated = self.validate(request)

        params: dict[str, Any] = {
            "symbol": validated.symbol,
            "side": validated.side,
            "type": validated.order_type,
            "quantity": validated.quantity,
            "newOrderRespType": "RESULT",
        }

        if validated.order_type == "LIMIT":
            params["price"] = validated.price
            params["timeInForce"] = "GTC"

        self.logger.info("Placing order request: %s", params)

        try:
            response = self.client.create_order(params)
        except BinanceApiError:
            self.logger.exception("Binance API error while placing order")
            raise
        except Exception:
            self.logger.exception("Unexpected error while placing order")
            raise

        self.logger.info("Order response: %s", response)
        return response
