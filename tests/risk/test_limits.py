import pytest

from private_quant_terminal.risk.limits import RiskLimits


class TestRiskLimits:
    def test_creates_valid_risk_limits(self) -> None:
        limits = RiskLimits(
            max_position_quantity=100,
            max_order_quantity=50,
            max_open_positions=10,
            max_daily_loss=10000.0,
        )

        assert limits.max_position_quantity == 100
        assert limits.max_order_quantity == 50
        assert limits.max_open_positions == 10
        assert limits.max_daily_loss == 10000.0

    @pytest.mark.parametrize(
        ("field", "value", "message"),
        [
            (
                "max_position_quantity",
                0,
                "max_position_quantity must be greater than zero",
            ),
            (
                "max_order_quantity",
                0,
                "max_order_quantity must be greater than zero",
            ),
            (
                "max_open_positions",
                0,
                "max_open_positions must be greater than zero",
            ),
            (
                "max_daily_loss",
                0.0,
                "max_daily_loss must be greater than zero",
            ),
        ],
    )
    def test_rejects_zero_limits(
        self,
        field: str,
        value: float,
        message: str,
    ) -> None:
        values = {
            "max_position_quantity": 100,
            "max_order_quantity": 50,
            "max_open_positions": 10,
            "max_daily_loss": 10000.0,
        }

        values[field] = value

        with pytest.raises(ValueError, match=message):
            RiskLimits(**values)

    @pytest.mark.parametrize(
        ("field", "value", "message"),
        [
            (
                "max_position_quantity",
                -1,
                "max_position_quantity must be greater than zero",
            ),
            (
                "max_order_quantity",
                -1,
                "max_order_quantity must be greater than zero",
            ),
            (
                "max_open_positions",
                -1,
                "max_open_positions must be greater than zero",
            ),
            (
                "max_daily_loss",
                -1.0,
                "max_daily_loss must be greater than zero",
            ),
        ],
    )
    def test_rejects_negative_limits(
        self,
        field: str,
        value: float,
        message: str,
    ) -> None:
        values = {
            "max_position_quantity": 100,
            "max_order_quantity": 50,
            "max_open_positions": 10,
            "max_daily_loss": 10000.0,
        }

        values[field] = value

        with pytest.raises(ValueError, match=message):
            RiskLimits(**values)

    def test_risk_limits_are_immutable(self) -> None:
        limits = RiskLimits(
            max_position_quantity=100,
            max_order_quantity=50,
            max_open_positions=10,
            max_daily_loss=10000.0,
        )

        with pytest.raises(Exception) as error:
            limits.max_order_quantity = 200

        assert type(error.value).__name__ == "FrozenInstanceError"
