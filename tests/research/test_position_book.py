from datetime import datetime, timezone

from private_quant_terminal.models.instrument import Instrument, InstrumentType
from private_quant_terminal.research.position_book import ResearchPositionBook
from private_quant_terminal.research.simulation import (
    ResearchFill,
    ResearchFillSide,
)


TIMESTAMP = datetime(2026, 9, 1, 10, 0, tzinfo=timezone.utc)


def make_instrument(symbol: str) -> Instrument:
    return Instrument(
        symbol=symbol,
        exchange="NSE",
        instrument_type=InstrumentType.EQUITY,
    )


def make_fill(
    *,
    group_id: str,
    symbol: str,
    side: ResearchFillSide,
    quantity: float,
    price: float,
    transaction_cost: float = 0.0,
) -> ResearchFill:
    return ResearchFill(
        timestamp=TIMESTAMP,
        group_id=group_id,
        instrument=make_instrument(symbol),
        side=side,
        quantity=quantity,
        price=price,
        transaction_cost=transaction_cost,
    )


def test_opens_one_leg() -> None:
    book = ResearchPositionBook()

    result = book.apply_fill(
        make_fill(
            group_id="STRATEGY-1",
            symbol="NIFTY",
            side=ResearchFillSide.BUY,
            quantity=10,
            price=100,
        )
    )

    assert result.position is not None
    assert result.position.quantity == 10
    assert result.position.average_price == 100
    assert book.open_position_count() == 1
    assert book.realized_pnl() == 0
    assert book.transaction_cost() == 0


def test_multiple_legs_can_coexist_in_one_group() -> None:
    book = ResearchPositionBook()

    book.apply_fill(
        make_fill(
            group_id="STRADDLE-1",
            symbol="BANKNIFTY-CALL",
            side=ResearchFillSide.SELL,
            quantity=1,
            price=100,
        )
    )

    book.apply_fill(
        make_fill(
            group_id="STRADDLE-1",
            symbol="BANKNIFTY-PUT",
            side=ResearchFillSide.SELL,
            quantity=1,
            price=120,
        )
    )

    positions = book.positions_for_group("STRADDLE-1")

    assert len(positions) == 2
    assert {position.instrument.symbol for position in positions} == {
        "BANKNIFTY-CALL",
        "BANKNIFTY-PUT",
    }

    assert all(position.quantity == -1 for position in positions)


def test_different_groups_are_isolated() -> None:
    book = ResearchPositionBook()

    book.apply_fill(
        make_fill(
            group_id="STRATEGY-1",
            symbol="NIFTY",
            side=ResearchFillSide.BUY,
            quantity=1,
            price=100,
        )
    )

    book.apply_fill(
        make_fill(
            group_id="STRATEGY-2",
            symbol="NIFTY",
            side=ResearchFillSide.BUY,
            quantity=2,
            price=200,
        )
    )

    assert len(book.positions_for_group("STRATEGY-1")) == 1
    assert len(book.positions_for_group("STRATEGY-2")) == 1

    assert book.positions_for_group("STRATEGY-1")[0].quantity == 1
    assert book.positions_for_group("STRATEGY-2")[0].quantity == 2


def test_same_leg_uses_existing_accounting_state() -> None:
    book = ResearchPositionBook()

    book.apply_fill(
        make_fill(
            group_id="STRATEGY-1",
            symbol="NIFTY",
            side=ResearchFillSide.BUY,
            quantity=10,
            price=100,
        )
    )

    result = book.apply_fill(
        make_fill(
            group_id="STRATEGY-1",
            symbol="NIFTY",
            side=ResearchFillSide.BUY,
            quantity=10,
            price=120,
        )
    )

    assert result.position is not None
    assert result.position.quantity == 20
    assert result.position.average_price == 110


def test_closing_one_leg_does_not_remove_other_legs() -> None:
    book = ResearchPositionBook()

    call = make_fill(
        group_id="STRADDLE-1",
        symbol="BANKNIFTY-CALL",
        side=ResearchFillSide.SELL,
        quantity=1,
        price=100,
    )
    put = make_fill(
        group_id="STRADDLE-1",
        symbol="BANKNIFTY-PUT",
        side=ResearchFillSide.SELL,
        quantity=1,
        price=120,
    )

    book.apply_fill(call)
    book.apply_fill(put)

    book.apply_fill(
        make_fill(
            group_id="STRADDLE-1",
            symbol="BANKNIFTY-CALL",
            side=ResearchFillSide.BUY,
            quantity=1,
            price=80,
        )
    )

    positions = book.positions_for_group("STRADDLE-1")

    assert len(positions) == 1
    assert positions[0].instrument.symbol == "BANKNIFTY-PUT"
    assert positions[0].quantity == -1


def test_realized_pnl_aggregates_across_multiple_legs() -> None:
    book = ResearchPositionBook()

    book.apply_fill(
        make_fill(
            group_id="STRADDLE-1",
            symbol="BANKNIFTY-CALL",
            side=ResearchFillSide.SELL,
            quantity=1,
            price=100,
        )
    )

    book.apply_fill(
        make_fill(
            group_id="STRADDLE-1",
            symbol="BANKNIFTY-PUT",
            side=ResearchFillSide.SELL,
            quantity=1,
            price=120,
        )
    )

    book.apply_fill(
        make_fill(
            group_id="STRADDLE-1",
            symbol="BANKNIFTY-CALL",
            side=ResearchFillSide.BUY,
            quantity=1,
            price=80,
        )
    )

    book.apply_fill(
        make_fill(
            group_id="STRADDLE-1",
            symbol="BANKNIFTY-PUT",
            side=ResearchFillSide.BUY,
            quantity=1,
            price=100,
        )
    )

    assert book.realized_pnl() == 40
    assert book.open_position_count() == 0


def test_transaction_costs_aggregate_across_legs() -> None:
    book = ResearchPositionBook()

    book.apply_fill(
        make_fill(
            group_id="STRADDLE-1",
            symbol="BANKNIFTY-CALL",
            side=ResearchFillSide.SELL,
            quantity=1,
            price=100,
            transaction_cost=2.5,
        )
    )

    book.apply_fill(
        make_fill(
            group_id="STRADDLE-1",
            symbol="BANKNIFTY-PUT",
            side=ResearchFillSide.SELL,
            quantity=1,
            price=120,
            transaction_cost=3.5,
        )
    )

    assert book.transaction_cost() == 6.0


def test_get_position_returns_exact_group_and_instrument_leg() -> None:
    book = ResearchPositionBook()
    instrument = make_instrument("NIFTY")

    book.apply_fill(
        ResearchFill(
            timestamp=TIMESTAMP,
            group_id="STRATEGY-1",
            instrument=instrument,
            side=ResearchFillSide.BUY,
            quantity=1,
            price=100,
        )
    )

    position = book.get_position("STRATEGY-1", instrument)

    assert position is not None
    assert position.instrument.identifier == instrument.identifier

    assert book.get_position("STRATEGY-2", instrument) is None


def test_clear_resets_positions_and_totals() -> None:
    book = ResearchPositionBook()

    book.apply_fill(
        make_fill(
            group_id="STRATEGY-1",
            symbol="NIFTY",
            side=ResearchFillSide.BUY,
            quantity=1,
            price=100,
            transaction_cost=5,
        )
    )

    book.clear()

    assert book.positions() == ()
    assert book.open_position_count() == 0
    assert book.realized_pnl() == 0
    assert book.transaction_cost() == 0
