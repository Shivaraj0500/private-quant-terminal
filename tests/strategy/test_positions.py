import pytest

from private_quant_terminal.strategy.options import (
    OptionQuantity,
    OptionSelector,
    OptionType,
    StrikeSelection,
)
from private_quant_terminal.strategy.positions import (
    LegAction,
    LegInstrumentType,
    PositionGroup,
    StrategyLeg,
)


def atm_call() -> OptionSelector:
    return OptionSelector(
        underlying="BANKNIFTY",
        option_type=OptionType.CALL,
        strike_selection=StrikeSelection.ATM,
    )


def atm_put() -> OptionSelector:
    return OptionSelector(
        underlying="BANKNIFTY",
        option_type=OptionType.PUT,
        strike_selection=StrikeSelection.ATM,
    )


def test_buy_option_leg() -> None:
    leg = StrategyLeg(
        action=LegAction.BUY,
        instrument_type=LegInstrumentType.OPTION,
        option=atm_call(),
        quantity=OptionQuantity(1),
    )

    assert leg.action is LegAction.BUY
    assert leg.instrument_type is LegInstrumentType.OPTION
    assert leg.option == atm_call()


def test_sell_option_leg() -> None:
    leg = StrategyLeg(
        action=LegAction.SELL,
        instrument_type=LegInstrumentType.OPTION,
        option=atm_put(),
        quantity=OptionQuantity(1),
    )

    assert leg.action is LegAction.SELL
    assert leg.option == atm_put()


def test_short_atm_straddle_has_two_legs() -> None:
    group = PositionGroup(
        group_id="short-atm-straddle",
        name="Short ATM Straddle",
        legs=(
            StrategyLeg(
                action=LegAction.SELL,
                instrument_type=LegInstrumentType.OPTION,
                option=atm_call(),
                quantity=OptionQuantity(1),
            ),
            StrategyLeg(
                action=LegAction.SELL,
                instrument_type=LegInstrumentType.OPTION,
                option=atm_put(),
                quantity=OptionQuantity(1),
            ),
        ),
    )

    assert len(group.legs) == 2
    assert all(
        leg.action is LegAction.SELL
        for leg in group.legs
    )


def test_option_leg_requires_selector() -> None:
    with pytest.raises(
        ValueError,
        match="OPTION legs require an option selector",
    ):
        StrategyLeg(
            action=LegAction.BUY,
            instrument_type=LegInstrumentType.OPTION,
        )


def test_equity_leg_requires_symbol() -> None:
    with pytest.raises(
        ValueError,
        match="Non-option legs require a symbol",
    ):
        StrategyLeg(
            action=LegAction.BUY,
            instrument_type=LegInstrumentType.EQUITY,
        )


def test_position_group_requires_leg() -> None:
    with pytest.raises(
        ValueError,
        match="at least one leg",
    ):
        PositionGroup(
            group_id="empty",
            name="Empty",
            legs=(),
        )
