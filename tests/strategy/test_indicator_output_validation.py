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
from private_quant_terminal.strategy.expressions import (
    indicator,
)
from private_quant_terminal.strategy.indicator_registry import (
    IndicatorRegistry,
)
from private_quant_terminal.strategy.indicator_specs import (
    IndicatorOutputSpec,
    IndicatorSpec,
)


def candles(count: int = 30) -> list[Candle]:
    start = datetime(2026, 8, 30, 9, 15, tzinfo=UTC)

    return [
        Candle(
            timestamp=start + timedelta(minutes=index),
            open=100.0 + index,
            high=101.0 + index,
            low=99.0 + index,
            close=100.0 + index,
            volume=1000.0 + index,
        )
        for index in range(count)
    ]


def engine() -> CanonicalIndicatorEngine:
    registry = IndicatorRegistry()

    for spec in builtin_indicator_specs().values():
        registry.register_spec(spec)

    registry.register_provider(BuiltinStrategyIndicatorProvider())

    return CanonicalIndicatorEngine(registry)


def test_default_value_output_remains_compatible() -> None:
    result = engine().calculate(
        indicator(
            "SMA",
            parameters={"period": 5},
        ),
        candles(),
    )

    assert result.output("value").latest() is not None


def test_requested_output_must_exist_in_spec() -> None:
    expression = indicator(
        "SMA",
        parameters={"period": 5},
        output="upper",
    )

    with pytest.raises(
        ValueError,
        match="Unknown indicator output",
    ):
        engine().calculate(
            expression,
            candles(),
        )


def test_output_matching_is_case_insensitive() -> None:
    expression = indicator(
        "SMA",
        parameters={"period": 5},
        output="VALUE",
    )

    result = engine().calculate(
        expression,
        candles(),
    )

    assert result.output("value").latest() is not None


def test_builtin_specs_have_declared_output_names() -> None:
    specs = builtin_indicator_specs()

    for spec in specs.values():
        output_names = {output.name.lower() for output in spec.outputs}

        assert output_names

    assert {output.name.lower() for output in specs["SMA"].outputs} == {"value"}

    assert {output.name.lower() for output in specs["BBANDS"].outputs} == {
        "upper",
        "middle",
        "lower",
    }


def test_indicator_output_spec_normalizes_name() -> None:
    output = IndicatorOutputSpec(
        name="  Upper  ",
    )

    assert output.name == "Upper"


def test_multi_output_spec_can_be_represented() -> None:
    spec = IndicatorSpec(
        id="TEST_MULTI",
        version="1.0.0",
        name="Test Multi Output",
        category="TEST",
        description="Test multi-output indicator.",
        parameters=(),
        outputs=(
            IndicatorOutputSpec("upper"),
            IndicatorOutputSpec("middle"),
            IndicatorOutputSpec("lower"),
        ),
        warmup=0,
        provider="builtin_strategy",
    )

    names = tuple(output.name for output in spec.outputs)

    assert names == (
        "upper",
        "middle",
        "lower",
    )
