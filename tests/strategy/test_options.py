import pytest

from private_quant_terminal.strategy.options import (
    ExpirySelection,
    OptionQuantity,
    OptionSelector,
    OptionType,
    StrikeSelection,
)


def test_atm_call_selector() -> None:
    selector = OptionSelector(
        underlying="banknifty",
        option_type=OptionType.CALL,
        strike_selection=StrikeSelection.ATM,
    )

    assert selector.underlying == "BANKNIFTY"
    assert selector.option_type is OptionType.CALL
    assert selector.strike_selection is StrikeSelection.ATM
    assert selector.expiry_selection is ExpirySelection.CURRENT_WEEK


def test_put_selector_can_be_sold() -> None:
    selector = OptionSelector(
        underlying="BANKNIFTY",
        option_type=OptionType.PUT,
        strike_selection=StrikeSelection.ATM,
    )

    assert selector.option_type is OptionType.PUT


def test_exact_strike_requires_strike() -> None:
    with pytest.raises(
        ValueError,
        match="EXACT strike selection requires a strike",
    ):
        OptionSelector(
            underlying="BANKNIFTY",
            option_type=OptionType.CALL,
            strike_selection=StrikeSelection.EXACT,
        )


def test_offset_requires_offset() -> None:
    with pytest.raises(
        ValueError,
        match="OFFSET strike selection requires a strike offset",
    ):
        OptionSelector(
            underlying="BANKNIFTY",
            option_type=OptionType.CALL,
            strike_selection=StrikeSelection.OFFSET,
        )


def test_exact_expiry_requires_expiry() -> None:
    with pytest.raises(
        ValueError,
        match="EXACT expiry selection requires an expiry",
    ):
        OptionSelector(
            underlying="BANKNIFTY",
            option_type=OptionType.CALL,
            strike_selection=StrikeSelection.ATM,
            expiry_selection=ExpirySelection.EXACT,
        )


def test_option_quantity_defaults_to_lots() -> None:
    quantity = OptionQuantity(2)

    assert quantity.value == 2
    assert quantity.unit == "LOTS"


def test_option_quantity_rejects_zero() -> None:
    with pytest.raises(
        ValueError,
        match="greater than zero",
    ):
        OptionQuantity(0)
