from .base import Strategy


class StrategyRegistry:
    def __init__(self) -> None:
        self._strategies: dict[str, Strategy] = {}

    def register(self, strategy: Strategy) -> None:
        if strategy.name in self._strategies:
            raise ValueError(
                f"Strategy already registered: {strategy.name}"
            )

        self._strategies[strategy.name] = strategy

    def get(self, name: str) -> Strategy:
        try:
            return self._strategies[name]
        except KeyError:
            raise KeyError(f"Unknown strategy: {name}") from None

    def __contains__(self, name: object) -> bool:
        if not isinstance(name, str):
            return False

        return name in self._strategies

    def names(self) -> list[str]:
        return list(self._strategies.keys())