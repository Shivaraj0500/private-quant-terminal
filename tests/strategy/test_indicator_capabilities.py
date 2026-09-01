
from private_quant_terminal.strategy.builtin_indicator_provider import (
    BuiltinStrategyIndicatorProvider,
)
from private_quant_terminal.strategy.builtin_indicator_specs import (
    builtin_indicator_specs,
)
from private_quant_terminal.strategy.talib_indicator_provider import (
    TALibIndicatorProvider,
)


def test_builtin_provider_declares_supported_indicators() -> None:
    provider = BuiltinStrategyIndicatorProvider()

    specs = builtin_indicator_specs()

    assert provider.supports(specs["SMA"])
    assert provider.supports(specs["EMA"])
    assert provider.supports(specs["RSI"])
    assert provider.supports(specs["ATR"])
    assert provider.supports(specs["SUPERTREND"])
    assert provider.supports(specs["MOMENTUM"])
    assert provider.supports(specs["ROC"])
    assert provider.supports(specs["VOLUME_SMA"])
    assert provider.supports(specs["RELATIVE_VOLUME"])
    assert provider.supports(specs["OBV"])


def test_talib_provider_declares_only_supported_indicators() -> None:
    provider = TALibIndicatorProvider()

    specs = builtin_indicator_specs()

    assert provider.supports(specs["SMA"])
    assert provider.supports(specs["EMA"])
    assert provider.supports(specs["RSI"])
    assert provider.supports(specs["ATR"])
    assert provider.supports(specs["MOMENTUM"])
    assert provider.supports(specs["ROC"])
    assert provider.supports(specs["OBV"])

    assert not provider.supports(specs["SUPERTREND"])
    assert not provider.supports(specs["VOLUME_SMA"])
    assert not provider.supports(specs["RELATIVE_VOLUME"])


def test_provider_capability_rejects_wrong_provider_identity() -> None:
    provider = TALibIndicatorProvider()

    spec = builtin_indicator_specs()["SMA"]

    assert provider.supports(spec) is True


def test_capability_is_based_on_indicator_identity() -> None:
    provider = TALibIndicatorProvider()

    spec = builtin_indicator_specs()["SMA"]

    assert provider.supports(spec) is True


def test_unknown_indicator_is_not_supported() -> None:
    provider = TALibIndicatorProvider()

    class UnknownSpec:
        id = "DOES_NOT_EXIST"

    assert provider.supports(UnknownSpec()) is False
