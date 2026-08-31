from datetime import UTC, datetime, timedelta

import pytest

from private_quant_terminal.models import Candle
from private_quant_terminal.strategy.builtin_indicator_provider import (
    BuiltinStrategyIndicatorProvider,
)
from private_quant_terminal.strategy.builtin_indicator_specs import (
    builtin_indicator_specs,
)
from private_quant_terminal.strategy.canonical_indicator_engine import (
    CanonicalIndicatorEngine,
)
from private_quant_terminal.strategy.expressions import indicator
from private_quant_terminal.strategy.indicator_registry import (
    IndicatorRegistry,
)
from private_quant_terminal.strategy.talib_indicator_provider import (
    TALibIndicatorProvider,
)


def candles(count: int = 60) -> list[Candle]:
    start = datetime(2026, 8, 30, 9, 15, tzinfo=UTC)

    return [
        Candle(
            timestamp=start + timedelta(minutes=index),
            open=100.0 + index,
            high=101.0 + index,
            low=99.0 + index,
            close=100.0 + index + (index % 3) * 0.25,
            volume=1000.0 + index * 25.0,
        )
        for index in range(count)
    ]


def engine() -> CanonicalIndicatorEngine:
    registry = IndicatorRegistry()

    for spec in builtin_indicator_specs().values():
        registry.register_spec(spec)

    registry.register_provider(TALibIndicatorProvider())

    registry.register_provider(BuiltinStrategyIndicatorProvider())

    return CanonicalIndicatorEngine(registry)


def test_stoch_spec_is_canonical_multi_output() -> None:
    spec = builtin_indicator_specs()["STOCH"]

    assert spec.id == "STOCH"
    assert spec.provider == "talib"

    assert {output.name for output in spec.outputs} == {
        "slowk",
        "slowd",
    }

    parameters = {parameter.name: parameter for parameter in spec.parameters}

    assert parameters["fastk_period"].default == 5
    assert parameters["slowk_period"].default == 3
    assert parameters["slowk_matype"].default == 0
    assert parameters["slowd_period"].default == 3
    assert parameters["slowd_matype"].default == 0


@pytest.mark.parametrize(
    "output",
    [
        "slowk",
        "slowd",
    ],
)
def test_stoch_outputs_are_available(
    output: str,
) -> None:
    result = engine().calculate(
        indicator(
            "STOCH",
            output=output,
        ),
        candles(),
    )

    series = result.output(output)

    assert series.timestamps == tuple(candle.timestamp for candle in candles())

    assert any(value is not None for value in series.values)


def test_stoch_requires_explicit_output() -> None:
    expression = indicator("STOCH")

    with pytest.raises(
        ValueError,
        match="Unknown indicator output",
    ):
        engine().calculate(
            expression,
            candles(),
        )


def test_stoch_unknown_output_is_rejected() -> None:
    expression = indicator(
        "STOCH",
        output="value",
    )

    with pytest.raises(
        ValueError,
        match="Unknown indicator output",
    ):
        engine().calculate(
            expression,
            candles(),
        )


@pytest.mark.parametrize(
    "parameters",
    [
        {"fastk_period": 0},
        {"slowk_period": 0},
        {"slowd_period": 0},
        {"fastk_period": 5.5},
        {"slowk_period": 3.5},
        {"slowd_period": 3.5},
    ],
)
def test_stoch_rejects_invalid_periods(
    parameters: dict[str, float],
) -> None:
    with pytest.raises(ValueError):
        engine().calculate(
            indicator(
                "STOCH",
                parameters=parameters,
                output="slowk",
            ),
            candles(),
        )


def test_stoch_rejects_fastk_less_than_one() -> None:
    with pytest.raises(ValueError):
        engine().calculate(
            indicator(
                "STOCH",
                parameters={"fastk_period": 0},
                output="slowk",
            ),
            candles(),
        )


def test_stoch_provider_supports_stoch() -> None:
    spec = builtin_indicator_specs()["STOCH"]

    assert TALibIndicatorProvider().supports(spec) is True
