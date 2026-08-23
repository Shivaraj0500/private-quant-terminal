import pytest

from private_quant_terminal.data.streaming.base import LiveMarketDataProvider


class TestLiveMarketDataProvider:
    def test_provider_is_abstract(self) -> None:
        with pytest.raises(TypeError):
            LiveMarketDataProvider()

    def test_subscribe_ticks_body_raises_not_implemented(self) -> None:
        with pytest.raises(NotImplementedError):
            LiveMarketDataProvider.subscribe_ticks(
                None,
                ["NIFTY"],
            )

    def test_subscribe_quotes_body_raises_not_implemented(self) -> None:
        with pytest.raises(NotImplementedError):
            LiveMarketDataProvider.subscribe_quotes(
                None,
                ["NIFTY"],
            )

    def test_subscribe_market_depth_body_raises_not_implemented(self) -> None:
        with pytest.raises(NotImplementedError):
            LiveMarketDataProvider.subscribe_market_depth(
                None,
                ["NIFTY"],
            )