import asyncio
from collections.abc import AsyncIterator

import pytest

from private_quant_terminal.data.streaming.broker_stream import (
    BrokerStreamProvider,
)
from private_quant_terminal.models.market_depth import MarketDepth
from private_quant_terminal.models.quote import Quote
from private_quant_terminal.models.tick import Tick


def test_broker_stream_provider_is_abstract() -> None:
    """BrokerStreamProvider itself cannot be instantiated."""
    with pytest.raises(TypeError):
        BrokerStreamProvider()


def test_incomplete_broker_stream_provider_is_abstract() -> None:
    """A subclass missing abstract methods cannot be instantiated."""

    class IncompleteProvider(BrokerStreamProvider):
        async def connect(self) -> None:
            return None

    with pytest.raises(TypeError):
        IncompleteProvider()


def test_complete_broker_stream_provider_can_be_instantiated() -> None:
    """A subclass implementing every abstract method can be instantiated."""

    class CompleteProvider(BrokerStreamProvider):
        def __init__(self) -> None:
            self._connected = False

        async def connect(self) -> None:
            self._connected = True

        async def disconnect(self) -> None:
            self._connected = False

        def is_connected(self) -> bool:
            return self._connected

        async def subscribe_ticks(
            self,
            symbols: list[str],
        ) -> AsyncIterator[Tick]:
            if False:
                yield Tick

        async def subscribe_quotes(
            self,
            symbols: list[str],
        ) -> AsyncIterator[Quote]:
            if False:
                yield Quote

        async def subscribe_market_depth(
            self,
            symbols: list[str],
        ) -> AsyncIterator[MarketDepth]:
            if False:
                yield MarketDepth

    provider = CompleteProvider()

    assert isinstance(provider, BrokerStreamProvider)
    assert provider.is_connected() is False


def test_abstract_connect_body_raises_not_implemented() -> None:
    """Cover the default abstract connect method body."""

    async def run() -> None:
        with pytest.raises(NotImplementedError):
            await BrokerStreamProvider.connect(None)

    asyncio.run(run())


def test_abstract_disconnect_body_raises_not_implemented() -> None:
    """Cover the default abstract disconnect method body."""

    async def run() -> None:
        with pytest.raises(NotImplementedError):
            await BrokerStreamProvider.disconnect(None)

    asyncio.run(run())


def test_abstract_is_connected_body_raises_not_implemented() -> None:
    """Cover the default abstract is_connected method body."""

    with pytest.raises(NotImplementedError):
        BrokerStreamProvider.is_connected(None)


def test_abstract_subscribe_ticks_body_raises_not_implemented() -> None:
    """Cover the default abstract subscribe_ticks method body."""

    async def run() -> None:
        with pytest.raises(NotImplementedError):
            await BrokerStreamProvider.subscribe_ticks(None, ["TEST"])

    asyncio.run(run())


def test_abstract_subscribe_quotes_body_raises_not_implemented() -> None:
    """Cover the default abstract subscribe_quotes method body."""

    async def run() -> None:
        with pytest.raises(NotImplementedError):
            await BrokerStreamProvider.subscribe_quotes(None, ["TEST"])

    asyncio.run(run())


def test_abstract_subscribe_market_depth_body_raises_not_implemented() -> None:
    """Cover the default abstract subscribe_market_depth method body."""

    async def run() -> None:
        with pytest.raises(NotImplementedError):
            await BrokerStreamProvider.subscribe_market_depth(
                None,
                ["TEST"],
            )

    asyncio.run(run())