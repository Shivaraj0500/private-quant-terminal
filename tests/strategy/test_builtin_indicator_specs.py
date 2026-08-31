from private_quant_terminal.strategy.builtin_indicator_specs import (
    builtin_indicator_specs,
)
from private_quant_terminal.strategy.indicator_specs import (
    IndicatorParameterType,
)


def test_builtin_catalog_contains_core_indicators() -> None:
    specs = builtin_indicator_specs()

    expected = {
        "SMA",
        "EMA",
        "RSI",
        "ATR",
        "BBANDS",
        "MACD",
        "SUPERTREND",
        "MOMENTUM",
        "ROC",
        "VOLUME_SMA",
        "RELATIVE_VOLUME",
        "OBV",
    }

    assert set(specs) == expected


def test_sma_spec() -> None:
    spec = builtin_indicator_specs()["SMA"]

    assert spec.id == "SMA"
    assert spec.version == "1.0.0"
    assert spec.category == "TREND"
    assert spec.outputs[0].name == "value"

    period = spec.parameter("period")

    assert period.parameter_type is IndicatorParameterType.INTEGER
    assert period.default == 14
    assert period.minimum == 1


def test_ema_spec() -> None:
    spec = builtin_indicator_specs()["EMA"]

    assert spec.category == "TREND"
    assert spec.parameter("period").default == 14


def test_rsi_spec() -> None:
    spec = builtin_indicator_specs()["RSI"]

    assert spec.category == "MOMENTUM"
    assert spec.parameter("period").default == 14


def test_atr_spec() -> None:
    spec = builtin_indicator_specs()["ATR"]

    assert spec.category == "VOLATILITY"
    assert spec.parameter("period").default == 14


def test_supertrend_spec() -> None:
    spec = builtin_indicator_specs()["SUPERTREND"]

    assert spec.category == "TREND"
    assert spec.parameter("period").default == 10
    assert spec.parameter("multiplier").default == 2.0


def test_momentum_and_roc_specs() -> None:
    specs = builtin_indicator_specs()

    assert specs["MOMENTUM"].category == "MOMENTUM"
    assert specs["ROC"].category == "MOMENTUM"

    assert specs["MOMENTUM"].parameter("period").default == 1
    assert specs["ROC"].parameter("period").default == 1


def test_volume_specs() -> None:
    specs = builtin_indicator_specs()

    assert specs["VOLUME_SMA"].category == "VOLUME"
    assert specs["RELATIVE_VOLUME"].category == "VOLUME"
    assert specs["OBV"].category == "VOLUME"

    assert specs["VOLUME_SMA"].parameter("period").default == 20
    assert specs["RELATIVE_VOLUME"].parameter("period").default == 20


def test_all_builtin_specs_are_deterministic() -> None:
    specs = builtin_indicator_specs()

    assert all(spec.deterministic for spec in specs.values())


def test_all_builtin_specs_have_declared_outputs() -> None:
    specs = builtin_indicator_specs()

    assert all(spec.outputs for spec in specs.values())

    assert tuple(output.name for output in specs["BBANDS"].outputs) == (
        "upper",
        "middle",
        "lower",
    )
