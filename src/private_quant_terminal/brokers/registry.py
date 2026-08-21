from .base import Broker


class BrokerRegistry:
    def __init__(self) -> None:
        self._brokers: dict[str, Broker] = {}

    def register(self, broker: Broker) -> None:
        self._brokers[broker.name] = broker

    def get(self, name: str) -> Broker:
        return self._brokers[name]