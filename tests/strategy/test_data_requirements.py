import pytest

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
