from datetime import UTC, datetime, timedelta

import pytest

from private_quant_terminal.models import Candle
from private_quant_terminal.strategy.indicator_providers import (
    IndicatorProvider,
    IndicatorResult,
)
from private_quant_terminal.strategy.indicator_specs import (
    IndicatorOutputSpec,
    IndicatorParameterSpec,
    IndicatorParameterType,
    IndicatorSpec,
)
from private_quant_terminal.strategy.series import TimeSeries


def test_indicator_result_exposes_named_outputs() -> None:
    series = TimeSeries(
        timestamps=(datetime(2026, 8, 30, 9, 15, tzinfo=UTC),),
        values=(100.0,),
    )

    result = IndicatorResult({"value": series})

    assert result.output("value") is series


def test_unknown_output_is_rejected() -> None:
    series = TimeSeries(
        timestamps=(datetime(2026, 8, 30, 9, 15, tzinfo=UTC),),
        values=(100.0,),
    )

    result = IndicatorResult({"value": series})

    with pytest.raises(KeyError):
        result.output("missing")


def test_empty_result_is_rejected() -> None:
    with pytest.raises(ValueError):
        IndicatorResult({})


def test_provider_contract_can_be_implemented() -> None:
    class TestProvider(IndicatorProvider):
        @property
        def provider_id(self) -> str:
            return "test"

        def calculate(
            self,
            spec: IndicatorSpec,
            candles: list[Candle],
            parameters: dict[str, object],
        ) -> IndicatorResult:
            del parameters

            series = TimeSeries(
                timestamps=tuple(
                    candle.timestamp
                    for candle in candles
                ),
                values=tuple(
                    candle.close
                    for candle in candles
                ),
            )

            return IndicatorResult(
                {"value": series}
            )

    provider = TestProvider()

    spec = IndicatorSpec(
        id="TEST",
        version="1.0.0",
        name="Test",
        category="TEST",
        description="Test provider.",
        parameters=(
            IndicatorParameterSpec(
                name="period",
                parameter_type=IndicatorParameterType.INTEGER,
                default=1,
            ),
        ),
        outputs=(
            IndicatorOutputSpec("value"),
        ),
        warmup=0,
        provider="test",
    )

    candles = [
        Candle(
            timestamp=datetime(2026, 8, 30, 9, 15, tzinfo=UTC)
            + timedelta(minutes=index),
            open=100 + index,
            high=101 + index,
            low=99 + index,
            close=100 + index,
        )
        for index in range(3)
    ]

    result = provider.calculate(
        spec,
        candles,
        {"period": 1},
    )

    assert provider.provider_id == "test"
    assert result.output("value").latest() == 102
