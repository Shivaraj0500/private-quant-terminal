from datetime import datetime, timezone

import pytest

from private_quant_terminal.models.instrument import Instrument, InstrumentType
from private_quant_terminal.research.simulation import (
    ResearchAccountingEngine,
    ResearchFill,
    ResearchFillSide,
    ResearchLegPosition,
)


def make_instrument() -> Instrument:
    return Instrument(
        symbol="TEST",
        exchange="TEST",
        instrument_type=InstrumentType.EQUITY,
    )


def make_fill(
    *,
    side: ResearchFillSide,
    quantity: float,
    price: float,
    cost: float = 0.0,
) -> ResearchFill:
    return ResearchFill(
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
        group_id="group-1",
        instrument=make_instrument(),
        side=side,
        quantity=quantity,
        price=price,
        transaction_cost=cost,
    )


def test_buy_creates_long_position():
    engine = ResearchAccountingEngine()

    result = engine.apply_fill(
        None,
        make_fill(
            side=ResearchFillSide.BUY,
            quantity=10,
            price=100,
        ),
    )

    assert result.position is not None
    assert result.position.quantity == 10
    assert result.position.average_price == 100
    assert result.realized_pnl == 0
    assert result.transaction_cost == 0


def test_multiple_buys_use_weighted_average_price():
    engine = ResearchAccountingEngine()

    first = engine.apply_fill(
        None,
        make_fill(
            side=ResearchFillSide.BUY,
            quantity=10,
            price=100,
        ),
    )

    second = engine.apply_fill(
        first.position,
        make_fill(
            side=ResearchFillSide.BUY,
            quantity=10,
            price=110,
        ),
    )

    assert second.position is not None
    assert second.position.quantity == 20
    assert second.position.average_price == 105


def test_partial_sell_realizes_long_pnl():
    engine = ResearchAccountingEngine()

    opened = engine.apply_fill(
        None,
        make_fill(
            side=ResearchFillSide.BUY,
            quantity=10,
            price=100,
        ),
    )

    closed = engine.apply_fill(
        opened.position,
        make_fill(
            side=ResearchFillSide.SELL,
            quantity=4,
            price=115,
        ),
    )

    assert closed.position is not None
    assert closed.position.quantity == 6
    assert closed.position.average_price == 100
    assert closed.realized_pnl == 60


def test_full_sell_closes_long_position():
    engine = ResearchAccountingEngine()

    opened = engine.apply_fill(
        None,
        make_fill(
            side=ResearchFillSide.BUY,
            quantity=10,
            price=100,
        ),
    )

    closed = engine.apply_fill(
        opened.position,
        make_fill(
            side=ResearchFillSide.SELL,
            quantity=10,
            price=120,
        ),
    )

    assert closed.position is None
    assert closed.realized_pnl == 200


def test_sell_opens_short_position():
    engine = ResearchAccountingEngine()

    result = engine.apply_fill(
        None,
        make_fill(
            side=ResearchFillSide.SELL,
            quantity=10,
            price=100,
        ),
    )

    assert result.position is not None
    assert result.position.quantity == -10
    assert result.position.average_price == 100
    assert result.realized_pnl == 0


def test_multiple_sells_use_weighted_average_short_price():
    engine = ResearchAccountingEngine()

    first = engine.apply_fill(
        None,
        make_fill(
            side=ResearchFillSide.SELL,
            quantity=10,
            price=100,
        ),
    )

    second = engine.apply_fill(
        first.position,
        make_fill(
            side=ResearchFillSide.SELL,
            quantity=10,
            price=110,
        ),
    )

    assert second.position is not None
    assert second.position.quantity == -20
    assert second.position.average_price == 105


def test_partial_buy_covers_short_and_realizes_pnl():
    engine = ResearchAccountingEngine()

    opened = engine.apply_fill(
        None,
        make_fill(
            side=ResearchFillSide.SELL,
            quantity=10,
            price=100,
        ),
    )

    covered = engine.apply_fill(
        opened.position,
        make_fill(
            side=ResearchFillSide.BUY,
            quantity=4,
            price=90,
        ),
    )

    assert covered.position is not None
    assert covered.position.quantity == -6
    assert covered.position.average_price == 100
    assert covered.realized_pnl == 40


def test_full_buy_cover_closes_short_position():
    engine = ResearchAccountingEngine()

    opened = engine.apply_fill(
        None,
        make_fill(
            side=ResearchFillSide.SELL,
            quantity=10,
            price=100,
        ),
    )

    covered = engine.apply_fill(
        opened.position,
        make_fill(
            side=ResearchFillSide.BUY,
            quantity=10,
            price=80,
        ),
    )

    assert covered.position is None
    assert covered.realized_pnl == 200


def test_long_to_short_reversal_realizes_long_pnl():
    engine = ResearchAccountingEngine()

    opened = engine.apply_fill(
        None,
        make_fill(
            side=ResearchFillSide.BUY,
            quantity=5,
            price=100,
        ),
    )

    reversed_position = engine.apply_fill(
        opened.position,
        make_fill(
            side=ResearchFillSide.SELL,
            quantity=8,
            price=110,
        ),
    )

    assert reversed_position.position is not None
    assert reversed_position.position.quantity == -3
    assert reversed_position.position.average_price == 110
    assert reversed_position.realized_pnl == 50


def test_short_to_long_reversal_realizes_short_pnl():
    engine = ResearchAccountingEngine()

    opened = engine.apply_fill(
        None,
        make_fill(
            side=ResearchFillSide.SELL,
            quantity=5,
            price=100,
        ),
    )

    reversed_position = engine.apply_fill(
        opened.position,
        make_fill(
            side=ResearchFillSide.BUY,
            quantity=8,
            price=90,
        ),
    )

    assert reversed_position.position is not None
    assert reversed_position.position.quantity == 3
    assert reversed_position.position.average_price == 90
    assert reversed_position.realized_pnl == 50


def test_mark_to_market_calculates_long_and_short_pnl():
    engine = ResearchAccountingEngine()

    long_position = ResearchLegPosition(
        group_id="group-1",
        instrument=make_instrument(),
        quantity=10,
        average_price=100,
    )

    short_position = ResearchLegPosition(
        group_id="group-1",
        instrument=make_instrument(),
        quantity=-10,
        average_price=100,
    )

    assert engine.mark_to_market(long_position, 120) == 200
    assert engine.mark_to_market(long_position, 90) == -100
    assert engine.mark_to_market(short_position, 80) == 200
    assert engine.mark_to_market(short_position, 120) == -200


def test_transaction_cost_is_preserved():
    engine = ResearchAccountingEngine()

    result = engine.apply_fill(
        None,
        make_fill(
            side=ResearchFillSide.BUY,
            quantity=10,
            price=100,
            cost=2.5,
        ),
    )

    assert result.transaction_cost == 2.5


def test_sell_without_position_opens_short():
    engine = ResearchAccountingEngine()

    result = engine.apply_fill(
        None,
        make_fill(
            side=ResearchFillSide.SELL,
            quantity=1,
            price=100,
        ),
    )

    assert result.position is not None
    assert result.position.quantity == -1
    assert result.position.average_price == 100
    assert result.realized_pnl == 0


def test_buy_cannot_exceed_short_position_without_reversal_logic():
    engine = ResearchAccountingEngine()

    opened = engine.apply_fill(
        None,
        make_fill(
            side=ResearchFillSide.SELL,
            quantity=5,
            price=100,
        ),
    )

    result = engine.apply_fill(
        opened.position,
        make_fill(
            side=ResearchFillSide.BUY,
            quantity=8,
            price=90,
        ),
    )

    assert result.position is not None
    assert result.position.quantity == 3
    assert result.position.average_price == 90
    assert result.realized_pnl == 50
