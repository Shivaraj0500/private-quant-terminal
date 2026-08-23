from .base import Broker


class BrokerRegistry:
    def __init__(self) -> None:
        self._brokers: dict[str, Broker] = {}

    def register(self, name: str, broker: Broker) -> None:
        if name in self._brokers:
            raise ValueError(
                f"Broker already registered: {name}"
            )

        self._brokers[name] = broker

    def get(self, name: str) -> Broker:
        try:
            return self._brokers[name]
        except KeyError as exc:
            raise KeyError(
                f"Broker not found: {name}"
            ) from exc

    def names(self) -> list[str]:
        return list(self._brokers.keys())

    def __contains__(self, name: str) -> bool:
        return name in self._brokers