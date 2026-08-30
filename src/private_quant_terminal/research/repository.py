import json
from dataclasses import asdict, is_dataclass
from datetime import datetime

from private_quant_terminal.persistence import Database
from private_quant_terminal.research.execution import (
    ResearchExecutionEvent,
    ResearchExecutionEventType,
    ResearchEquityPoint,
    ResearchExecutionResult,
    ResearchTrade,
)
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

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS research_run_results (
                    run_id TEXT PRIMARY KEY,
                    events_json TEXT NOT NULL,
                    trades_json TEXT NOT NULL,
                    equity_curve_json TEXT NOT NULL,
                    final_equity REAL NOT NULL,
                    performance_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (run_id)
                        REFERENCES research_runs(run_id)
                        ON DELETE CASCADE
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

    def save_result(
        self,
        execution: ResearchExecutionResult,
        performance: object,
    ) -> None:
        """Persist the immutable result of a completed research run."""

        events = [
            {
                "timestamp": event.timestamp.isoformat(),
                "event_type": event.event_type.value,
                "symbol": event.symbol,
                "price": event.price,
                "quantity": event.quantity,
            }
            for event in execution.events
        ]

        trades = [
            {
                "symbol": trade.symbol,
                "entry_time": trade.entry_time.isoformat(),
                "exit_time": trade.exit_time.isoformat(),
                "entry_price": trade.entry_price,
                "exit_price": trade.exit_price,
                "quantity": trade.quantity,
                "gross_pnl": trade.gross_pnl,
                "transaction_cost": trade.transaction_cost,
                "net_pnl": trade.net_pnl,
            }
            for trade in execution.trades
        ]

        equity_curve = [
            {
                "timestamp": point.timestamp.isoformat(),
                "equity": point.equity,
            }
            for point in execution.equity_curve
        ]

        performance_payload = _json_safe(performance)

        with self._database.transaction() as connection:
            existing = connection.execute(
                """
                SELECT run_id
                FROM research_run_results
                WHERE run_id = ?
                """,
                (execution.run_id,),
            ).fetchone()

            if existing is not None:
                return

            connection.execute(
                """
                INSERT INTO research_run_results (
                    run_id,
                    events_json,
                    trades_json,
                    equity_curve_json,
                    final_equity,
                    performance_json,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    execution.run_id,
                    json.dumps(events, separators=(",", ":")),
                    json.dumps(trades, separators=(",", ":")),
                    json.dumps(equity_curve, separators=(",", ":")),
                    execution.final_equity,
                    json.dumps(
                        performance_payload,
                        separators=(",", ":"),
                    ),
                    datetime.now().isoformat(),
                ),
            )

    def get_result(
        self,
        run_id: str,
    ) -> tuple[ResearchExecutionResult, dict]:
        """Retrieve persisted execution evidence and performance payload."""

        with self._database.connect() as connection:
            row = connection.execute(
                """
                SELECT
                    run_id,
                    events_json,
                    trades_json,
                    equity_curve_json,
                    final_equity,
                    performance_json
                FROM research_run_results
                WHERE run_id = ?
                """,
                (run_id,),
            ).fetchone()

        if row is None:
            raise KeyError(
                f"No research result stored for run: {run_id}"
            )

        events = tuple(
            ResearchExecutionEvent(
                timestamp=datetime.fromisoformat(item["timestamp"]),
                event_type=ResearchExecutionEventType(
                    item["event_type"]
                ),
                symbol=item["symbol"],
                price=float(item["price"]),
                quantity=float(item["quantity"]),
            )
            for item in json.loads(row["events_json"])
        )

        trades = tuple(
            ResearchTrade(
                symbol=item["symbol"],
                entry_time=datetime.fromisoformat(item["entry_time"]),
                exit_time=datetime.fromisoformat(item["exit_time"]),
                entry_price=float(item["entry_price"]),
                exit_price=float(item["exit_price"]),
                quantity=float(item["quantity"]),
                gross_pnl=float(item["gross_pnl"]),
                transaction_cost=float(item["transaction_cost"]),
                net_pnl=float(item["net_pnl"]),
            )
            for item in json.loads(row["trades_json"])
        )

        equity_curve = tuple(
            ResearchEquityPoint(
                timestamp=datetime.fromisoformat(item["timestamp"]),
                equity=float(item["equity"]),
            )
            for item in json.loads(row["equity_curve_json"])
        )

        execution = ResearchExecutionResult(
            run_id=row["run_id"],
            events=events,
            trades=trades,
            equity_curve=equity_curve,
            final_equity=float(row["final_equity"]),
        )

        return execution, json.loads(row["performance_json"])

    def update_status(
        self,
        run_id: str,
        status: ResearchRunStatus,
    ) -> None:
        """Transition a research run through its lifecycle."""

        allowed_transitions = {
            ResearchRunStatus.CREATED: {
                ResearchRunStatus.RUNNING,
            },
            ResearchRunStatus.RUNNING: {
                ResearchRunStatus.COMPLETED,
                ResearchRunStatus.FAILED,
            },
        }

        with self._database.transaction() as connection:
            row = connection.execute(
                """
                SELECT status
                FROM research_runs
                WHERE run_id = ?
                """,
                (run_id,),
            ).fetchone()

            if row is None:
                raise KeyError(
                    f"Unknown research run: {run_id}"
                )

            current_status = ResearchRunStatus(row["status"])

            if status not in allowed_transitions.get(
                current_status,
                set(),
            ):
                raise ValueError(
                    "Invalid research run status transition: "
                    f"{current_status.value} -> {status.value}"
                )

            connection.execute(
                """
                UPDATE research_runs
                SET status = ?
                WHERE run_id = ?
                """,
                (status.value, run_id),
            )

    def list(self) -> tuple[ResearchRun, ...]:
        """Retrieve persisted research runs newest first."""

        with self._database.connect() as connection:
            rows = connection.execute(
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
                ORDER BY created_at DESC, run_id DESC
                """
            ).fetchall()

        return tuple(
            ResearchRun(
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
            for row in rows
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


def _json_safe(value):
    """Convert dataclasses/enums/tuples into JSON-compatible values."""

    if is_dataclass(value):
        return _json_safe(asdict(value))

    if isinstance(value, dict):
        return {
            str(key): _json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]

    if hasattr(value, "value"):
        return value.value

    return value
