from datetime import UTC, datetime

import pytest

from private_quant_terminal.persistence import Database
from private_quant_terminal.research import (
    ResearchParameters,
    ResearchRun,
    ResearchRunRepository,
    ResearchRunStatus,
    canonical_parameters_json,
    parameters_hash,
)


def make_run(run_id: str = "run-1") -> ResearchRun:
    parameters = ResearchParameters(
        values={
            "lookback": 20,
            "risk": 0.02,
        }
    )

    return ResearchRun(
        run_id=run_id,
        strategy_id="strategy-1",
        strategy_version=1,
        strategy_hash="a" * 64,
        dataset_hash="b" * 64,
        symbol="RELIANCE",
        timeframe="1h",
        start_time=datetime(2026, 1, 1, tzinfo=UTC),
        end_time=datetime(2026, 1, 2, tzinfo=UTC),
        parameters_json=canonical_parameters_json(parameters),
        parameters_hash=parameters_hash(parameters),
        status=ResearchRunStatus.CREATED,
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


def test_save_and_get_round_trip(tmp_path) -> None:
    repository = ResearchRunRepository(
        Database(tmp_path / "research.db")
    )

    run = make_run()

    repository.save(run)

    assert repository.get(run.run_id) == run


def test_save_same_run_is_idempotent(tmp_path) -> None:
    repository = ResearchRunRepository(
        Database(tmp_path / "research.db")
    )

    run = make_run()

    repository.save(run)
    repository.save(run)

    assert repository.get(run.run_id) == run


def test_save_rejects_same_run_with_different_identity(tmp_path) -> None:
    repository = ResearchRunRepository(
        Database(tmp_path / "research.db")
    )

    first = make_run()

    second = ResearchRun(
        run_id=first.run_id,
        strategy_id=first.strategy_id,
        strategy_version=first.strategy_version,
        strategy_hash=first.strategy_hash,
        dataset_hash="c" * 64,
        symbol=first.symbol,
        timeframe=first.timeframe,
        start_time=first.start_time,
        end_time=first.end_time,
        parameters_json=first.parameters_json,
        parameters_hash=first.parameters_hash,
        status=first.status,
        created_at=first.created_at,
    )

    repository.save(first)

    with pytest.raises(
        ValueError,
        match="Research run identity is immutable",
    ):
        repository.save(second)


def test_unknown_run_raises(tmp_path) -> None:
    repository = ResearchRunRepository(
        Database(tmp_path / "research.db")
    )

    with pytest.raises(
        KeyError,
        match="Unknown research run",
    ):
        repository.get("missing")
