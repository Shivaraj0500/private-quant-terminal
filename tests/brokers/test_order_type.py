from private_quant_terminal.brokers.order_type import OrderType


def test_order_type_market_exists() -> None:
    assert OrderType.MARKET.value == "MARKET"


def test_order_type_limit_exists() -> None:
    assert OrderType.LIMIT.value == "LIMIT"


def test_order_type_members_are_distinct() -> None:
    assert OrderType.MARKET != OrderType.LIMIT