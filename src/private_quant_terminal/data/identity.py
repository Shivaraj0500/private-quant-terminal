import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from private_quant_terminal.data.validators import validate_candles
from private_quant_terminal.models import Candle


@dataclass(frozen=True)
class DatasetIdentity:
    """Immutable identity of a deterministic candle dataset."""

    symbol: str
    timeframe: str
    start_time: datetime
    end_time: datetime
    candle_count: int
    dataset_hash: str


def _canonical_candle(candle: Candle) -> dict[str, Any]:
    """Return the canonical representation of one candle."""

    return {
        "timestamp": candle.timestamp.isoformat(),
        "open": candle.open,
        "high": candle.high,
        "low": candle.low,
        "close": candle.close,
        "volume": candle.volume,
    }


def canonical_candle_json(candles: list[Candle]) -> str:
    """Serialize candles deterministically for identity hashing."""

    validate_candles(candles)

    payload = [_canonical_candle(candle) for candle in candles]

    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    )


def candle_dataset_hash(candles: list[Candle]) -> str:
    """Return the SHA-256 identity of a candle dataset."""

    canonical_json = canonical_candle_json(candles)

    return hashlib.sha256(
        canonical_json.encode("utf-8")
    ).hexdigest()


def create_dataset_identity(
    symbol: str,
    timeframe: str,
    candles: list[Candle],
) -> DatasetIdentity:
    """Create an immutable deterministic dataset identity."""

    if not symbol:
        raise ValueError("symbol cannot be empty")

    if not timeframe:
        raise ValueError("timeframe cannot be empty")

    validate_candles(candles)

    return DatasetIdentity(
        symbol=symbol,
        timeframe=timeframe,
        start_time=candles[0].timestamp,
        end_time=candles[-1].timestamp,
        candle_count=len(candles),
        dataset_hash=candle_dataset_hash(candles),
    )
