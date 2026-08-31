from __future__ import annotations

from private_quant_terminal.strategy.indicator_specs import (
    IndicatorOutputSpec,
    IndicatorParameterSpec,
    IndicatorParameterType,
    IndicatorSpec,
)


def _period(
    default: int,
) -> IndicatorParameterSpec:
    return IndicatorParameterSpec(
        name="period",
        parameter_type=IndicatorParameterType.INTEGER,
        required=False,
        default=default,
        minimum=1,
    )


def _single_output() -> tuple[IndicatorOutputSpec, ...]:
    return (
        IndicatorOutputSpec(
            name="value",
            description="Primary numerical indicator value.",
        ),
    )


def builtin_indicator_specs() -> dict[str, IndicatorSpec]:
    """Return the canonical specifications for built-in indicators."""

    specs = (
        IndicatorSpec(
            id="SMA",
            name="Simple Moving Average",
            version="1.0.0",
            category="TREND",
            description="Simple moving average of the selected price series.",
            parameters=(_period(14),),
            outputs=_single_output(),
            warmup=0,
            provider="builtin_strategy",
            deterministic=True,
        ),
        IndicatorSpec(
            id="EMA",
            name="Exponential Moving Average",
            version="1.0.0",
            category="TREND",
            description="Exponential moving average of the selected price series.",
            parameters=(_period(14),),
            outputs=_single_output(),
            warmup=0,
            provider="builtin_strategy",
            deterministic=True,
        ),
        IndicatorSpec(
            id="RSI",
            name="Relative Strength Index",
            version="1.0.0",
            category="MOMENTUM",
            description="Relative Strength Index using the strategy engine implementation.",
            parameters=(_period(14),),
            outputs=_single_output(),
            warmup=0,
            provider="builtin_strategy",
            deterministic=True,
        ),
        IndicatorSpec(
            id="ATR",
            name="Average True Range",
            version="1.0.0",
            category="VOLATILITY",
            description="Historical Average True Range used by the strategy engine.",
            parameters=(_period(14),),
            outputs=_single_output(),
            warmup=0,
            provider="builtin_strategy",
            deterministic=True,
        ),
        IndicatorSpec(
            id="BBANDS",
            name="Bollinger Bands",
            version="1.0.0",
            category="VOLATILITY",
            description="Bollinger Bands calculated from the selected price series.",
            parameters=(
                _period(20),
                IndicatorParameterSpec(
                    name="deviation",
                    parameter_type=IndicatorParameterType.FLOAT,
                    required=False,
                    default=2.0,
                    minimum=0.000001,
                ),
            ),
            outputs=(
                IndicatorOutputSpec(
                    name="upper",
                    description="Upper Bollinger Band.",
                ),
                IndicatorOutputSpec(
                    name="middle",
                    description="Middle Bollinger Band.",
                ),
                IndicatorOutputSpec(
                    name="lower",
                    description="Lower Bollinger Band.",
                ),
            ),
            warmup=0,
            provider="talib",
            deterministic=True,
        ),
        IndicatorSpec(
            id="SUPERTREND",
            name="Supertrend",
            version="1.0.0",
            category="TREND",
            description="Supertrend trend-following indicator.",
            parameters=(
                _period(10),
                IndicatorParameterSpec(
                    name="multiplier",
                    parameter_type=IndicatorParameterType.FLOAT,
                    required=False,
                    default=2.0,
                    minimum=0.000001,
                ),
            ),
            outputs=_single_output(),
            warmup=0,
            provider="builtin_strategy",
            deterministic=True,
        ),
        IndicatorSpec(
            id="MOMENTUM",
            name="Momentum",
            version="1.0.0",
            category="MOMENTUM",
            description="Difference between the latest value and the value N periods ago.",
            parameters=(_period(1),),
            outputs=_single_output(),
            warmup=0,
            provider="builtin_strategy",
            deterministic=True,
        ),
        IndicatorSpec(
            id="ROC",
            name="Rate of Change",
            version="1.0.0",
            category="MOMENTUM",
            description="Percentage rate of change over the selected period.",
            parameters=(_period(1),),
            outputs=_single_output(),
            warmup=0,
            provider="builtin_strategy",
            deterministic=True,
        ),
        IndicatorSpec(
            id="VOLUME_SMA",
            name="Volume Simple Moving Average",
            version="1.0.0",
            category="VOLUME",
            description="Simple moving average of volume.",
            parameters=(_period(20),),
            outputs=_single_output(),
            warmup=0,
            provider="builtin_strategy",
            deterministic=True,
        ),
        IndicatorSpec(
            id="RELATIVE_VOLUME",
            name="Relative Volume",
            version="1.0.0",
            category="VOLUME",
            description="Current volume relative to the average previous volume.",
            parameters=(_period(20),),
            outputs=_single_output(),
            warmup=0,
            provider="builtin_strategy",
            deterministic=True,
        ),
        IndicatorSpec(
            id="OBV",
            name="On-Balance Volume",
            version="1.0.0",
            category="VOLUME",
            description="Cumulative On-Balance Volume.",
            parameters=(),
            outputs=_single_output(),
            warmup=0,
            provider="builtin_strategy",
            deterministic=True,
        ),
    )

    return {spec.id: spec for spec in specs}
