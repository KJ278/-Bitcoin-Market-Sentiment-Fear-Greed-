"""Validation helpers for order input."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

VALID_SIDES = {"BUY", "SELL"}
VALID_TYPES = {"MARKET", "LIMIT"}


class ValidationError(ValueError):
    """Raised when user input is invalid."""


def validate_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not symbol or not symbol.isalnum() or len(symbol) < 6:
        raise ValidationError("symbol must be alphanumeric and look like BTCUSDT")
    return symbol


def validate_side(side: str) -> str:
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValidationError(f"side must be one of: {', '.join(sorted(VALID_SIDES))}")
    return side


def validate_order_type(order_type: str) -> str:
    order_type = order_type.strip().upper()
    if order_type not in VALID_TYPES:
        raise ValidationError(f"order_type must be one of: {', '.join(sorted(VALID_TYPES))}")
    return order_type


def validate_positive_decimal(value: str, field_name: str) -> str:
    try:
        parsed = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValidationError(f"{field_name} must be a valid number") from exc

    if parsed <= 0:
        raise ValidationError(f"{field_name} must be greater than zero")
    return format(parsed.normalize(), "f")


def validate_price_for_limit(order_type: str, price: str | None) -> str | None:
    if order_type == "LIMIT":
        if price is None:
            raise ValidationError("price is required when order_type is LIMIT")
        return validate_positive_decimal(price, "price")

    if price is not None:
        raise ValidationError("price is only allowed when order_type is LIMIT")

    return None
