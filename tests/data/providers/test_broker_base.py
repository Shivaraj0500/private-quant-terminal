import pytest

from private_quant_terminal.data.providers.broker_base import BrokerMarketDataProvider
from private_quant_terminal.models.market_depth import MarketDepth
from private_quant_terminal.models.quote import Quote


def test_broker_market_data_provider_is_abstract() -> None:
    with pytest.raises(TypeError):
        BrokerMarketDataProvider()


def test_incomplete_broker_market_data_provider_is_abstract() -> None:
    class IncompleteProvider(BrokerMarketDataProvider):
        def get_quote(self, symbol: str) -> Quote:
            raise NotImplementedError

    with pytest.raises(TypeError):
        IncompleteProvider()


def test_complete_broker_market_data_provider_can_be_instantiated() -> None:
    class CompleteProvider(BrokerMarketDataProvider):
        def get_quote(self, symbol: str) -> Quote:
            raise NotImplementedError

        def get_market_depth(self, symbol: str) -> MarketDepth:
            raise NotImplementedError

        def stream_ticks(self, symbols: list[str]) -> None:
            pass

    provider = CompleteProvider()

    assert isinstance(provider, BrokerMarketDataProvider)