from __future__ import annotations

from types import MappingProxyType

from private_quant_terminal.strategy.indicator_providers import (
    IndicatorProvider,
)
from private_quant_terminal.strategy.indicator_specs import (
    IndicatorSpec,
)


class IndicatorRegistry:
    """Deterministic registry for canonical indicator specifications
    and calculation providers.
    """

    def __init__(self) -> None:
        self._specs: dict[str, IndicatorSpec] = {}
        self._aliases: dict[str, str] = {}
        self._providers: dict[str, IndicatorProvider] = {}

    @staticmethod
    def _normalize(value: str) -> str:
        normalized = value.strip().upper()

        if not normalized:
            raise ValueError("Registry key cannot be empty.")

        return normalized

    @staticmethod
    def _provider_key(value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Provider ID cannot be empty.")

        return value.lower()

    def register_spec(self, spec: IndicatorSpec) -> None:
        indicator_id = self._normalize(spec.id)

        if indicator_id in self._specs:
            raise ValueError(
                f"Indicator {indicator_id} is already registered."
            )

        if indicator_id in self._aliases:
            raise ValueError(
                f"Indicator key {indicator_id} is already registered "
                "as an alias."
            )

        aliases = [
            self._normalize(alias)
            for alias in spec.aliases
        ]

        if indicator_id in aliases:
            raise ValueError(
                f"Indicator {indicator_id} cannot alias itself."
            )

        for alias in aliases:
            if (
                alias in self._specs
                or alias in self._aliases
            ):
                raise ValueError(
                    f"Indicator alias {alias} is already registered."
                )

        self._specs[indicator_id] = spec

        for alias in aliases:
            self._aliases[alias] = indicator_id

    def register_provider(
        self,
        provider: IndicatorProvider,
    ) -> None:
        provider_id = self._provider_key(
            provider.provider_id
        )

        if provider_id in self._providers:
            raise ValueError(
                f"Indicator provider {provider.provider_id} "
                "is already registered."
            )

        self._providers[provider_id] = provider

    def resolve_spec(
        self,
        indicator_id: str,
    ) -> IndicatorSpec:
        key = self._normalize(indicator_id)

        canonical_id = self._aliases.get(
            key,
            key,
        )

        try:
            return self._specs[canonical_id]
        except KeyError as exc:
            raise KeyError(
                f"Unknown indicator: {indicator_id}"
            ) from exc

    def resolve_provider(
        self,
        provider_id: str,
    ) -> IndicatorProvider:
        key = self._provider_key(provider_id)

        try:
            return self._providers[key]
        except KeyError as exc:
            raise KeyError(
                f"Unknown indicator provider: {provider_id}"
            ) from exc

    def resolve_provider_for(
        self,
        spec: IndicatorSpec,
    ) -> IndicatorProvider:
        provider_key = self._provider_key(
            spec.provider
        )

        provider = self._providers.get(provider_key)

        if provider is None:
            raise ValueError(
                f"No provider registered for indicator "
                f"{spec.id}: {spec.provider}"
            )

        if (
            provider.provider_id.strip().lower()
            != spec.provider.strip().lower()
        ):
            raise ValueError(
                f"No compatible provider registered for "
                f"indicator {spec.id}"
            )

        return provider

    def specs(self) -> MappingProxyType:
        return MappingProxyType(
            dict(self._specs)
        )

    def providers(self) -> MappingProxyType:
        return MappingProxyType(
            dict(self._providers)
        )
