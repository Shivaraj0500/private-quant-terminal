import pytest

from private_quant_terminal.strategy.indicator_warmup import (
    canonical_warmup,
)


@pytest.mark.parametrize(
    ("indicator_id", "parameters", "expected"),
    [
        ("SMA", {"period": 5}, 4),
        ("EMA", {"period": 5}, 4),
        ("RSI", {"period": 5}, 5),
        ("ATR", {"period": 5}, 4),
        ("SUPERTREND", {"period": 5}, 4),
        ("MOMENTUM", {"period": 5}, 5),
        ("ROC", {"period": 5}, 5),
        ("VOLUME_SMA", {"period": 5}, 4),
        ("RELATIVE_VOLUME", {"period": 5}, 5),
        ("OBV", {}, 0),
    ],
)
def test_canonical_warmup(
    indicator_id: str,
    parameters: dict[str, float],
    expected: int,
) -> None:
    assert (
        canonical_warmup(
            indicator_id,
            parameters,
        )
        == expected
    )


def test_warmup_is_parameter_aware() -> None:
    assert canonical_warmup("SMA", {"period": 5}) == 4
    assert canonical_warmup("SMA", {"period": 20}) == 19

    assert canonical_warmup("RSI", {"period": 5}) == 5
    assert canonical_warmup("RSI", {"period": 14}) == 14


def test_indicator_id_is_case_insensitive() -> None:
    assert canonical_warmup("sma", {"period": 5}) == 4
    assert canonical_warmup("Ema", {"period": 5}) == 4


def test_missing_period_is_rejected() -> None:
    with pytest.raises(ValueError, match="period"):
        canonical_warmup("SMA", {})


def test_invalid_period_is_rejected() -> None:
    with pytest.raises(ValueError, match="period"):
        canonical_warmup("SMA", {"period": 0})


def test_unknown_indicator_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unknown indicator"):
        canonical_warmup("DOES_NOT_EXIST", {"period": 5})


@pytest.mark.parametrize(
    ("output_name", "expected"),
    [
        ("macd", 25),
        ("signal", 33),
        ("histogram", 33),
    ],
)
def test_macd_warmup_is_output_aware(
    output_name: str,
    expected: int,
) -> None:
    assert (
        canonical_warmup(
            "MACD",
            {
                "fastperiod": 12,
                "slowperiod": 26,
                "signalperiod": 9,
            },
            output_name,
        )
        == expected
    )


def test_macd_warmup_uses_parameters() -> None:
    assert (
        canonical_warmup(
            "MACD",
            {
                "fastperiod": 5,
                "slowperiod": 10,
                "signalperiod": 3,
            },
            "macd",
        )
        == 9
    )

    assert (
        canonical_warmup(
            "MACD",
            {
                "fastperiod": 5,
                "slowperiod": 10,
                "signalperiod": 3,
            },
            "signal",
        )
        == 11
    )


def test_macd_invalid_period_relationship_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="fastperiod",
    ):
        canonical_warmup(
            "MACD",
            {
                "fastperiod": 26,
                "slowperiod": 26,
                "signalperiod": 9,
            },
            "macd",
        )
