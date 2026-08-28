from datetime import datetime

from private_quant_terminal.persistence import Database
from private_quant_terminal.research.run import (
    ResearchRun,
    ResearchRunStatus,
)


class ResearchRunRepository:
    """Persist immutable research runs."""

    def __init__(self, database: Database) -> None:
        self._database = database
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        with self._database.transaction() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS research_runs (
                    run_id TEXT PRIMARY KEY,
                    strategy_id TEXT NOT NULL,
                    strategy_version INTEGER NOT NULL,
                    strategy_hash TEXT NOT NULL,
                    dataset_hash TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    parameters_json TEXT NOT NULL,
                    parameters_hash TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    def save(self, run: ResearchRun) -> None:
        """Persist a research run exactly once."""

        with self._database.transaction() as connection:
            existing = connection.execute(
                """
                SELECT
                    strategy_hash,
                    dataset_hash,
                    parameters_hash
                FROM research_runs
                WHERE run_id = ?
                """,
                (run.run_id,),
            ).fetchone()

            if existing is not None:
                if (
                    existing["strategy_hash"] != run.strategy_hash
                    or existing["dataset_hash"] != run.dataset_hash
                    or existing["parameters_hash"]
                    != run.parameters_hash
                ):
                    raise ValueError(
                        "Research run identity is immutable: "
                        f"{run.run_id} already exists with "
                        "different inputs."
                    )

                return

            connection.execute(
                """
                INSERT INTO research_runs (
                    run_id,
                    strategy_id,
                    strategy_version,
                    strategy_hash,
                    dataset_hash,
                    symbol,
                    timeframe,
                    start_time,
                    end_time,
                    parameters_json,
                    parameters_hash,
                    status,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run.run_id,
                    run.strategy_id,
                    run.strategy_version,
                    run.strategy_hash,
                    run.dataset_hash,
                    run.symbol,
                    run.timeframe,
                    run.start_time.isoformat(),
                    run.end_time.isoformat(),
                    run.parameters_json,
                    run.parameters_hash,
                    run.status.value,
                    run.created_at.isoformat(),
                ),
            )

    def get(self, run_id: str) -> ResearchRun:
        """Retrieve one research run."""

        with self._database.connect() as connection:
            row = connection.execute(
                """
                SELECT
                    run_id,
                    strategy_id,
                    strategy_version,
                    strategy_hash,
                    dataset_hash,
                    symbol,
                    timeframe,
                    start_time,
                    end_time,
                    parameters_json,
                    parameters_hash,
                    status,
                    created_at
                FROM research_runs
                WHERE run_id = ?
                """,
                (run_id,),
            ).fetchone()

        if row is None:
            raise KeyError(f"Unknown research run: {run_id}")

        return ResearchRun(
            run_id=row["run_id"],
            strategy_id=row["strategy_id"],
            strategy_version=row["strategy_version"],
            strategy_hash=row["strategy_hash"],
            dataset_hash=row["dataset_hash"],
            symbol=row["symbol"],
            timeframe=row["timeframe"],
            start_time=datetime.fromisoformat(row["start_time"]),
            end_time=datetime.fromisoformat(row["end_time"]),
            parameters_json=row["parameters_json"],
            parameters_hash=row["parameters_hash"],
            status=ResearchRunStatus(row["status"]),
            created_at=datetime.fromisoformat(row["created_at"]),
        )
