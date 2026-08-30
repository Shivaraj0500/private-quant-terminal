import json
from datetime import datetime

from private_quant_terminal.persistence import Database
from private_quant_terminal.strategy.canonical import (
    canonical_strategy_json,
    strategy_hash,
)
from private_quant_terminal.strategy.enums import (
    ConditionOperator,
    OrderType,
    PositionSizingMethod,
    StopLossType,
    StrategyStatus,
    StrategyTimeframe,
    TakeProfitType,
)
from private_quant_terminal.strategy.ir import (
    ExecutionAssumptions,
    PositionSizing,
    StopLoss,
    StrategyCondition,
    StrategyDefinition,
    StrategyVersion,
    TakeProfit,
)


class StrategyVersionRepository:
    """Persist immutable strategy versions."""

    def __init__(self, database: Database) -> None:
        self._database = database
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        with self._database.transaction() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS strategy_versions (
                    strategy_id TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    specification_json TEXT NOT NULL,
                    specification_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (strategy_id, version)
                )
                """
            )

    def save(self, version: StrategyVersion) -> None:
        """Persist a strategy version exactly once."""

        specification = version.specification
        specification_json = canonical_strategy_json(specification)
        specification_hash = strategy_hash(specification)

        with self._database.transaction() as connection:
            existing = connection.execute(
                """
                SELECT specification_hash
                FROM strategy_versions
                WHERE strategy_id = ?
                  AND version = ?
                """,
                (version.strategy_id, version.version),
            ).fetchone()

            if existing is not None:
                if existing["specification_hash"] != specification_hash:
                    raise ValueError(
                        "Strategy versions are immutable: "
                        f"{version.strategy_id} v{version.version} "
                        "already exists with a different specification."
                    )

                return

            connection.execute(
                """
                INSERT INTO strategy_versions (
                    strategy_id,
                    version,
                    specification_json,
                    specification_hash,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    version.strategy_id,
                    version.version,
                    specification_json,
                    specification_hash,
                    version.created_at.isoformat(),
                ),
            )

    def get(
        self,
        strategy_id: str,
        version: int,
    ) -> StrategyVersion:
        """Retrieve one strategy version."""

        with self._database.connect() as connection:
            row = connection.execute(
                """
                SELECT
                    strategy_id,
                    version,
                    specification_json,
                    created_at
                FROM strategy_versions
                WHERE strategy_id = ?
                  AND version = ?
                """,
                (strategy_id, version),
            ).fetchone()

        if row is None:
            raise KeyError(
                f"Unknown strategy version: {strategy_id} v{version}"
            )

        specification = _strategy_from_json(
            row["specification_json"]
        )

        return StrategyVersion(
            strategy_id=row["strategy_id"],
            version=row["version"],
            specification=specification,
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def list_all(self) -> list[StrategyVersion]:
        """Return all persisted strategy versions."""

        with self._database.connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    strategy_id,
                    version,
                    specification_json,
                    created_at
                FROM strategy_versions
                ORDER BY strategy_id, version
                """
            ).fetchall()

        return [
            StrategyVersion(
                strategy_id=row["strategy_id"],
                version=row["version"],
                specification=_strategy_from_json(
                    row["specification_json"]
                ),
                created_at=datetime.fromisoformat(
                    row["created_at"]
                ),
            )
            for row in rows
        ]

    def next_version(self, strategy_id: str) -> int:
        """Return the next available version number."""

        with self._database.connect() as connection:
            row = connection.execute(
                """
                SELECT COALESCE(MAX(version), 0) + 1 AS next_version
                FROM strategy_versions
                WHERE strategy_id = ?
                """,
                (strategy_id,),
            ).fetchone()

        return int(row["next_version"])

    def list_latest(self) -> list[StrategyVersion]:
        """Return the latest version of every persisted strategy."""

        with self._database.connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    strategy_id,
                    version,
                    specification_json,
                    created_at
                FROM strategy_versions
                WHERE version = (
                    SELECT MAX(sv2.version)
                    FROM strategy_versions sv2
                    WHERE sv2.strategy_id = strategy_versions.strategy_id
                )
                ORDER BY created_at DESC
                """
            ).fetchall()

        return [
            StrategyVersion(
                strategy_id=row["strategy_id"],
                version=row["version"],
                specification=_strategy_from_json(
                    row["specification_json"]
                ),
                created_at=datetime.fromisoformat(
                    row["created_at"]
                ),
            )
            for row in rows
        ]

def _strategy_from_json(payload: str) -> StrategyDefinition:
    """Reconstruct a strategy definition from canonical JSON."""

    data = json.loads(payload)

    return StrategyDefinition(
        strategy_id=data["strategy_id"],
        name=data["name"],
        description=data["description"],
        instruments=tuple(data["instruments"]),
        timeframe=StrategyTimeframe(data["timeframe"]),
        entry_conditions=tuple(
            StrategyCondition(
                indicator=condition["indicator"],
                operator=ConditionOperator(condition["operator"]),
                value=condition["value"],
            )
            for condition in data["entry_conditions"]
        ),
        exit_conditions=tuple(
            StrategyCondition(
                indicator=condition["indicator"],
                operator=ConditionOperator(condition["operator"]),
                value=condition["value"],
            )
            for condition in data["exit_conditions"]
        ),
        position_sizing=PositionSizing(
            method=PositionSizingMethod(
                data["position_sizing"]["method"]
            ),
            value=data["position_sizing"]["value"],
        ),
        stop_loss=StopLoss(
            type=StopLossType(data["stop_loss"]["type"]),
            value=data["stop_loss"]["value"],
        ),
        take_profit=TakeProfit(
            type=TakeProfitType(data["take_profit"]["type"]),
            value=data["take_profit"]["value"],
        ),
        execution=ExecutionAssumptions(
            order_type=OrderType(data["execution"]["order_type"]),
            slippage_bps=data["execution"]["slippage_bps"],
            transaction_cost_bps=data["execution"][
                "transaction_cost_bps"
            ],
        ),
        status=StrategyStatus(data["status"]),
    )
