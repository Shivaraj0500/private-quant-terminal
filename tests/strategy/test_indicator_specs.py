import pytest

from private_quant_terminal.strategy.indicator_specs import (
    IndicatorOutputSpec,
    IndicatorParameterSpec,
    IndicatorParameterType,
    IndicatorSpec,
)


def ema_spec() -> IndicatorSpec:
    return IndicatorSpec(
        id="EMA",
        version="1.0.0",
        name="Exponential Moving Average",
        category="TREND",
        description="Exponential moving average.",
        parameters=(
            IndicatorParameterSpec(
                name="period",
                parameter_type=IndicatorParameterType.INTEGER,
                required=False,
                default=20,
                minimum=1,
            ),
        ),
        outputs=(
            IndicatorOutputSpec(
                name="value",
                description="EMA value.",
            ),
        ),
        warmup=19,
        provider="builtin",
    )


def test_indicator_spec_has_stable_identity() -> None:
    assert ema_spec().identity == "EMA@1.0.0"


def test_indicator_parameter_validates_integer_range() -> None:
    parameter = IndicatorParameterSpec(
        name="period",
        parameter_type=IndicatorParameterType.INTEGER,
        minimum=1,
    )

    parameter.validate(10)

    with pytest.raises(ValueError):
        parameter.validate(0)


def test_enum_parameter_requires_valid_choice() -> None:
    parameter = IndicatorParameterSpec(
        name="source",
        parameter_type=IndicatorParameterType.ENUM,
        choices=("close", "open"),
    )

    parameter.validate("close")

    with pytest.raises(ValueError):
        parameter.validate("volume")


def test_required_parameter_cannot_have_default() -> None:
    with pytest.raises(ValueError):
        IndicatorParameterSpec(
            name="period",
            parameter_type=IndicatorParameterType.INTEGER,
            required=True,
            default=14,
        )


def test_spec_rejects_duplicate_outputs() -> None:
    with pytest.raises(ValueError):
        IndicatorSpec(
            id="TEST",
            version="1.0.0",
            name="Test",
            category="TEST",
            description="Test",
            parameters=(),
            outputs=(
                IndicatorOutputSpec("value"),
                IndicatorOutputSpec("value"),
            ),
            warmup=0,
            provider="builtin",
        )


def test_spec_applies_defaults_and_rejects_unknown_parameters() -> None:
    spec = ema_spec()

    assert spec.validate_parameters({}) == {"period": 20}

    with pytest.raises(ValueError):
        spec.validate_parameters({"unknown": 10})


def test_aliases_are_normalized() -> None:
    spec = IndicatorSpec(
        id="macd",
        version="1.0.0",
        name="MACD",
        category="MOMENTUM",
        description="Moving average convergence divergence.",
        parameters=(),
        outputs=(
            IndicatorOutputSpec("line"),
            IndicatorOutputSpec("signal"),
            IndicatorOutputSpec("histogram"),
        ),
        warmup=26,
        provider="builtin",
        aliases=(" macd_line ", "MacD"),
    )

    assert spec.id == "MACD"
    assert spec.aliases == ("MACD_LINE", "MACD")