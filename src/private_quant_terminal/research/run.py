import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class ResearchRunStatus(str, Enum):
    """Lifecycle state of a research run."""

    CREATED = "CREATED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass(frozen=True)
class ResearchParameters:
    """Deterministic parameters supplied to a research run."""

    values: dict[str, Any]


@dataclass(frozen=True)
class ResearchRun:
    """Immutable identity and metadata of one research run."""

    run_id: str
    strategy_id: str
    strategy_version: int
    strategy_hash: str
    dataset_hash: str
    symbol: str
    timeframe: str
    start_time: datetime
    end_time: datetime
    parameters_json: str
    parameters_hash: str
    status: ResearchRunStatus
    created_at: datetime


def canonical_parameters_json(
    parameters: ResearchParameters,
) -> str:
    """Serialize research parameters deterministically."""

    return json.dumps(
        parameters.values,
        sort_keys=True,
        separators=(",", ":"),
    )


def parameters_hash(
    parameters: ResearchParameters,
) -> str:
    """Return the SHA-256 identity of research parameters."""

    payload = canonical_parameters_json(parameters)

    return hashlib.sha256(
        payload.encode("utf-8")
    ).hexdigest()
