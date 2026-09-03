import hashlib
import json
from dataclasses import asdict

from private_quant_terminal.strategy.ir import StrategyDefinition, StrategyIR


def canonical_strategy_dict(
    strategy: StrategyDefinition | StrategyIR,
) -> dict[str, object]:
    """Return the strategy as a deterministic, JSON-compatible mapping."""

    return asdict(strategy)


def canonical_strategy_json(
    strategy: StrategyDefinition | StrategyIR,
) -> str:
    """Return deterministic JSON for a strategy definition."""

    return json.dumps(
        canonical_strategy_dict(strategy),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def strategy_hash(strategy: StrategyDefinition | StrategyIR) -> str:
    """Return the SHA-256 identity of a strategy definition."""

    payload = canonical_strategy_json(strategy).encode("utf-8")

    return hashlib.sha256(payload).hexdigest()
