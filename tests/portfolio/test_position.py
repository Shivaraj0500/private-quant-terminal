from dataclasses import FrozenInstanceError

import pytest

from private_quant_terminal.portfolio.position import Position


class TestPosition:
    def test_creates_position(self) -> None:
        position = Position(
            symbol="NIFTY",
            quantity=10,
            average_price=25000.0,
        )

        assert position.symbol == "NIFTY"
        assert position.quantity == 10
        assert position.average_price == 25000.0

    def test_position_is_immutable(self) -> None:
        position = Position(
            symbol="NIFTY",
            quantity=10,
            average_price=25000.0,
        )

        with pytest.raises(FrozenInstanceError):
            position.quantity = 20
