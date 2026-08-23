from private_quant_terminal.models.instrument import (
    Instrument,
    InstrumentType,
)
from private_quant_terminal.models.trading import (
    Order,
    OrderStatus,
    Position,
    Side,
)
import pytest


def create_instrument() -> Instrument:
    return Instrument(
        symbol="NIFTY",
        exchange="NSE",
        instrument_type=InstrumentType.INDEX,
    )


class TestTradingEnums:
    def test_side_values(self) -> None:
        assert Side.BUY.value == "BUY"
        assert Side.SELL.value == "SELL"

    def test_order_status_values(self) -> None:
        assert OrderStatus.PENDING.value == "PENDING"
        assert OrderStatus.FILLED.value == "FILLED"
        assert OrderStatus.PARTIALLY_FILLED.value == "PARTIALLY_FILLED"
        assert OrderStatus.CANCELLED.value == "CANCELLED"
        assert OrderStatus.REJECTED.value == "REJECTED"


class TestOrder:
    def test_creates_market_order_with_default_status(self) -> None:
        instrument = create_instrument()

        order = Order(
            order_id="ORD-001",
            instrument=instrument,
            side=Side.BUY,
            quantity=10,
        )

        assert order.order_id == "ORD-001"
        assert order.instrument == instrument
        assert order.side == Side.BUY
        assert order.quantity == 10
        assert order.price is None
        assert order.status == OrderStatus.PENDING

    def test_creates_limit_order(self) -> None:
        order = Order(
            order_id="ORD-002",
            instrument=create_instrument(),
            side=Side.SELL,
            quantity=5,
            price=250.50,
            status=OrderStatus.FILLED,
        )

        assert order.side == Side.SELL
        assert order.quantity == 5
        assert order.price == 250.50
        assert order.status == OrderStatus.FILLED

    def test_allows_order_status_values(self) -> None:
        instrument = create_instrument()

        for status in OrderStatus:
            order = Order(
                order_id=f"ORD-{status.value}",
                instrument=instrument,
                side=Side.BUY,
                quantity=1,
                status=status,
            )

            assert order.status == status

    def test_rejects_zero_quantity(self) -> None:
        with pytest.raises(
            ValueError,
            match="quantity must be greater than zero",
        ):
            Order(
                order_id="ORD-003",
                instrument=create_instrument(),
                side=Side.BUY,
                quantity=0,
            )

    def test_rejects_negative_quantity(self) -> None:
        with pytest.raises(
            ValueError,
            match="quantity must be greater than zero",
        ):
            Order(
                order_id="ORD-004",
                instrument=create_instrument(),
                side=Side.SELL,
                quantity=-5,
            )

    def test_rejects_zero_price(self) -> None:
        with pytest.raises(
            ValueError,
            match="price must be greater than zero",
        ):
            Order(
                order_id="ORD-005",
                instrument=create_instrument(),
                side=Side.BUY,
                quantity=10,
                price=0.0,
            )

    def test_rejects_negative_price(self) -> None:
        with pytest.raises(
            ValueError,
            match="price must be greater than zero",
        ):
            Order(
                order_id="ORD-006",
                instrument=create_instrument(),
                side=Side.BUY,
                quantity=10,
                price=-100.0,
            )

    def test_order_is_mutable(self) -> None:
        order = Order(
            order_id="ORD-007",
            instrument=create_instrument(),
            side=Side.BUY,
            quantity=10,
        )

        order.quantity = 20
        order.status = OrderStatus.FILLED
        order.price = 150.0

        assert order.quantity == 20
        assert order.status == OrderStatus.FILLED
        assert order.price == 150.0


class TestPosition:
    def test_creates_position_with_defaults(self) -> None:
        instrument = create_instrument()

        position = Position(
            instrument=instrument,
        )

        assert position.instrument == instrument
        assert position.quantity == 0
        assert position.average_price == 0.0
        assert position.market_value == 0.0

    def test_creates_position_with_values(self) -> None:
        position = Position(
            instrument=create_instrument(),
            quantity=25,
            average_price=100.0,
        )

        assert position.quantity == 25
        assert position.average_price == 100.0
        assert position.market_value == 2500.0

    def test_calculates_negative_market_value_for_short_position(self) -> None:
        position = Position(
            instrument=create_instrument(),
            quantity=-10,
            average_price=200.0,
        )

        assert position.market_value == -2000.0

    def test_allows_zero_average_price(self) -> None:
        position = Position(
            instrument=create_instrument(),
            quantity=10,
            average_price=0.0,
        )

        assert position.average_price == 0.0
        assert position.market_value == 0.0

    def test_rejects_negative_average_price(self) -> None:
        with pytest.raises(
            ValueError,
            match="average_price cannot be negative",
        ):
            Position(
                instrument=create_instrument(),
                quantity=10,
                average_price=-1.0,
            )

    def test_position_is_mutable(self) -> None:
        position = Position(
            instrument=create_instrument(),
            quantity=10,
            average_price=100.0,
        )

        position.quantity = 20
        position.average_price = 150.0

        assert position.quantity == 20
        assert position.average_price == 150.0
        assert position.market_value == 3000.0