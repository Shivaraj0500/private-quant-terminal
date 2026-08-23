from dataclasses import FrozenInstanceError

import pytest

from private_quant_terminal.models.market_depth import (
    MarketDepth,
    MarketDepthLevel,
)


class TestMarketDepthLevel:
    def test_creates_level_with_all_fields(self) -> None:
        level = MarketDepthLevel(
            price=100.50,
            quantity=250.0,
            orders=5,
        )

        assert level.price == 100.50
        assert level.quantity == 250.0
        assert level.orders == 5

    def test_orders_defaults_to_none(self) -> None:
        level = MarketDepthLevel(
            price=100.50,
            quantity=250.0,
        )

        assert level.orders is None

    def test_allows_zero_values(self) -> None:
        level = MarketDepthLevel(
            price=0.0,
            quantity=0.0,
            orders=0,
        )

        assert level.price == 0.0
        assert level.quantity == 0.0
        assert level.orders == 0

    def test_market_depth_level_is_immutable(self) -> None:
        level = MarketDepthLevel(
            price=100.0,
            quantity=50.0,
            orders=2,
        )

        with pytest.raises(FrozenInstanceError):
            level.price = 101.0


class TestMarketDepth:
    def test_creates_market_depth_with_bids_and_asks(self) -> None:
        bid = MarketDepthLevel(
            price=100.0,
            quantity=200.0,
            orders=3,
        )

        ask = MarketDepthLevel(
            price=101.0,
            quantity=150.0,
            orders=2,
        )

        depth = MarketDepth(
            symbol="NIFTY",
            exchange="NSE",
            bids=(bid,),
            asks=(ask,),
        )

        assert depth.symbol == "NIFTY"
        assert depth.exchange == "NSE"
        assert depth.bids == (bid,)
        assert depth.asks == (ask,)

    def test_allows_multiple_bid_and_ask_levels(self) -> None:
        bids = (
            MarketDepthLevel(
                price=100.0,
                quantity=200.0,
            ),
            MarketDepthLevel(
                price=99.5,
                quantity=300.0,
            ),
        )

        asks = (
            MarketDepthLevel(
                price=100.5,
                quantity=150.0,
            ),
            MarketDepthLevel(
                price=101.0,
                quantity=250.0,
            ),
        )

        depth = MarketDepth(
            symbol="BANKNIFTY",
            exchange="NSE",
            bids=bids,
            asks=asks,
        )

        assert len(depth.bids) == 2
        assert len(depth.asks) == 2
        assert depth.bids[0].price == 100.0
        assert depth.bids[1].price == 99.5
        assert depth.asks[0].price == 100.5
        assert depth.asks[1].price == 101.0

    def test_allows_empty_market_depth(self) -> None:
        depth = MarketDepth(
            symbol="RELIANCE",
            exchange="NSE",
            bids=(),
            asks=(),
        )

        assert depth.bids == ()
        assert depth.asks == ()

    def test_market_depth_is_immutable(self) -> None:
        depth = MarketDepth(
            symbol="NIFTY",
            exchange="NSE",
            bids=(),
            asks=(),
        )

        with pytest.raises(FrozenInstanceError):
            depth.symbol = "BANKNIFTY"

    def test_market_depth_levels_are_immutable_inside_depth(self) -> None:
        bid = MarketDepthLevel(
            price=100.0,
            quantity=200.0,
            orders=3,
        )

        depth = MarketDepth(
            symbol="NIFTY",
            exchange="NSE",
            bids=(bid,),
            asks=(),
        )

        with pytest.raises(FrozenInstanceError):
            depth.bids[0].quantity = 500.0