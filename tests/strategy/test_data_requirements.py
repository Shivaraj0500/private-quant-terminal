import pytest

from private_quant_terminal.data.providers.memory import InMemoryMarketDataProvider

from private_quant_terminal.strategy import (
    DataField,
    DataRequirement,
)


def test_data_requirement_normalizes_canonical_fields() -> None:
    requirement = DataRequirement(
        symbol=" reliance ",
        timeframe=" 5M ",
        fields=("open", "close"),
        lookback=50,
        purpose=" indicator ",
    )

    assert requirement.symbol == "RELIANCE"
    assert requirement.timeframe == "5m"
    assert requirement.fields == (
        DataField.OPEN,
        DataField.CLOSE,
    )
    assert requirement.lookback == 50
    assert requirement.purpose == "INDICATOR"


def test_data_requirement_defaults_to_ohlcv() -> None:
    requirement = DataRequirement(
        symbol="NIFTY",
        timeframe="5m",
    )

    assert requirement.fields == (
        DataField.OPEN,
        DataField.HIGH,
        DataField.LOW,
        DataField.CLOSE,
        DataField.VOLUME,
    )
    assert requirement.lookback == 1
    assert requirement.purpose == "MARKET_DATA"


@pytest.mark.parametrize(
    "kwargs",
    (
        {"symbol": "", "timeframe": "5m"},
        {"symbol": "NIFTY", "timeframe": ""},
        {"symbol": "NIFTY", "timeframe": "5m", "lookback": 0},
        {"symbol": "NIFTY", "timeframe": "5m", "fields": ()},
    ),
)
def test_data_requirement_rejects_invalid_values(
    kwargs: dict[str, object],
) -> None:
    with pytest.raises(ValueError):
        DataRequirement(**kwargs)


def test_data_requirement_rejects_duplicate_fields() -> None:
    with pytest.raises(ValueError, match="fields must be unique"):
        DataRequirement(
            symbol="NIFTY",
            timeframe="5m",
            fields=(DataField.CLOSE, DataField.CLOSE),
        )


def test_strategy_ir_accepts_data_requirements() -> None:
    from private_quant_terminal.strategy import (
        StrategyIR,
        StrategyStatus,
        StrategyTimeframe,
    )

    requirement = DataRequirement(
        symbol="NIFTY",
        timeframe="5m",
        fields=(DataField.CLOSE,),
        lookback=200,
        purpose="INDICATOR",
    )

    strategy = StrategyIR(
        strategy_id="data-requirement-test",
        name="Data Requirement Test",
        description="Verify data requirements are part of the IR.",
        version=1,
        status=StrategyStatus.DRAFT,
        instruments=("NIFTY",),
        timeframe=StrategyTimeframe.FIVE_MINUTES,
        data_requirements=(requirement,),
    )

    assert strategy.data_requirements == (requirement,)


def test_strategy_ir_rejects_duplicate_data_requirements() -> None:
    from private_quant_terminal.strategy import (
        StrategyIR,
        StrategyStatus,
        StrategyTimeframe,
    )

    requirement = DataRequirement(
        symbol="NIFTY",
        timeframe="5m",
        fields=(DataField.CLOSE,),
    )

    with pytest.raises(
        ValueError,
        match="Strategy data requirements must be unique",
    ):
        StrategyIR(
            strategy_id="data-requirement-duplicate",
            name="Duplicate Data Requirement",
            description="Verify duplicate requirements are rejected.",
            version=1,
            status=StrategyStatus.DRAFT,
            instruments=("NIFTY",),
            timeframe=StrategyTimeframe.FIVE_MINUTES,
            data_requirements=(requirement, requirement),
        )


def _make_candles(count: int):
    from datetime import datetime, timedelta

    from private_quant_terminal.models.candle import Candle

    return [
        Candle(
            timestamp=datetime(2026, 1, 1) + timedelta(minutes=5 * index),
            open=100.0 + index,
            high=101.0 + index,
            low=99.0 + index,
            close=100.5 + index,
            volume=1000.0,
        )
        for index in range(count)
    ]


def test_data_availability_reports_available_when_lookback_is_satisfied() -> None:
    from private_quant_terminal.strategy import (
        DataAvailabilityChecker,
        DataAvailabilityStatus,
    )

    provider = InMemoryMarketDataProvider()
    provider.add_candles("NIFTY", "5m", _make_candles(50))

    requirement = DataRequirement(
        symbol="NIFTY",
        timeframe="5m",
        fields=(DataField.CLOSE,),
        lookback=20,
    )

    result = DataAvailabilityChecker(provider).check_requirement(requirement)

    assert result.status is DataAvailabilityStatus.AVAILABLE
    assert result.required_candles == 20
    assert result.available_candles == 20


def test_data_availability_reports_insufficient_history() -> None:
    from private_quant_terminal.strategy import (
        DataAvailabilityChecker,
        DataAvailabilityStatus,
    )

    provider = InMemoryMarketDataProvider()
    provider.add_candles("NIFTY", "5m", _make_candles(10))

    requirement = DataRequirement(
        symbol="NIFTY",
        timeframe="5m",
        fields=(DataField.CLOSE,),
        lookback=20,
    )

    result = DataAvailabilityChecker(provider).check_requirement(requirement)

    assert result.status is DataAvailabilityStatus.INSUFFICIENT_HISTORY
    assert result.required_candles == 20
    assert result.available_candles == 10


def test_data_availability_reports_unavailable_when_provider_fails() -> None:
    from private_quant_terminal.strategy import (
        DataAvailabilityChecker,
        DataAvailabilityStatus,
    )

    class FailingProvider:
        def get_candles(
            self,
            symbol: str,
            timeframe: str,
            limit: int,
        ):
            raise LookupError("No data available for symbol.")

    requirement = DataRequirement(
        symbol="NIFTY",
        timeframe="5m",
        lookback=20,
    )

    result = DataAvailabilityChecker(FailingProvider()).check_requirement(
        requirement
    )

    assert result.status is DataAvailabilityStatus.UNAVAILABLE
    assert result.required_candles == 20
    assert result.available_candles == 0
    assert result.message == "No data available for symbol."

def test_data_availability_checks_all_strategy_requirements():
    from private_quant_terminal.strategy import (
        DataAvailabilityChecker,
        DataAvailabilityStatus,
        DataRequirement,
        StrategyIR,
        StrategyStatus,
        StrategyTimeframe,
    )

    provider = InMemoryMarketDataProvider()

    provider.add_candles(
        "AAPL",
        "5m",
        _make_candles(50),
    )
    provider.add_candles(
        "MSFT",
        "15m",
        _make_candles(10),
    )

    strategy = StrategyIR(
        strategy_id="data-availability-test",
        name="Data Availability Test",
        description="Verify all strategy data requirements are checked.",
        version=1,
        status=StrategyStatus.DRAFT,
        instruments=("AAPL", "MSFT"),
        timeframe=StrategyTimeframe.FIVE_MINUTES,
        data_requirements=(
            DataRequirement(
                symbol="AAPL",
                timeframe="5m",
                lookback=20,
            ),
            DataRequirement(
                symbol="MSFT",
                timeframe="15m",
                lookback=20,
            ),
        ),
    )

    results = DataAvailabilityChecker(provider).check_strategy(strategy)

    assert len(results) == 2
    assert results[0].status is DataAvailabilityStatus.AVAILABLE
    assert results[0].available_candles == 20
    assert results[1].status is DataAvailabilityStatus.INSUFFICIENT_HISTORY
    assert results[1].available_candles == 10
