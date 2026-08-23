import pytest

from private_quant_terminal.data.providers.broker_base import (
    BrokerMarketDataProvider,
)


class IncompleteBrokerMarketDataProvider(BrokerMarketDataProvider):
    def get_quote(self, symbol: str):
        raise NotImplementedError


class CompleteBrokerMarketDataProvider(BrokerMarketDataProvider):
    def get_quote(self, symbol: str):
        raise NotImplementedError

    def get_market_depth(self, symbol: str):
        raise NotImplementedError

    def stream_ticks(self, symbols: list[str]) -> None:
        return None


def test_broker_market_data_provider_is_abstract() -> None:
    with pytest.raises(TypeError):
        BrokerMarketDataProvider()


def test_incomplete_broker_market_data_provider_is_abstract() -> None:
    with pytest.raises(TypeError):
        IncompleteBrokerMarketDataProvider()


def test_complete_broker_market_data_provider_can_be_instantiated() -> None:
    provider = CompleteBrokerMarketDataProvider()

    assert isinstance(provider, BrokerMarketDataProvider)


def test_abstract_get_quote_body_raises_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        BrokerMarketDataProvider.get_quote(None, "TEST")


def test_abstract_get_market_depth_body_raises_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        BrokerMarketDataProvider.get_market_depth(None, "TEST")


def test_abstract_stream_ticks_body_raises_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        BrokerMarketDataProvider.stream_ticks(None, ["TEST"])