from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from private_quant_terminal.data.identity import DatasetIdentity
from private_quant_terminal.research.repository import (
    ResearchRunRepository,
)
from private_quant_terminal.research.run import (
    ResearchParameters,
    ResearchRun,
    ResearchRunStatus,
    canonical_parameters_json,
    parameters_hash,
)
from private_quant_terminal.strategy.ir import StrategyVersion


@dataclass(frozen=True)
class ResearchRunCreationResult:
    """Result of creating a research run."""

    run: ResearchRun


class ResearchRunService:
    """Create immutable research runs from immutable inputs."""

    def __init__(
        self,
        repository: ResearchRunRepository,
    ) -> None:
        self._repository = repository

    def create_run(
        self,
        strategy_version: StrategyVersion,
        dataset: DatasetIdentity,
        parameters: ResearchParameters,
        run_id: str | None = None,
    ) -> ResearchRunCreationResult:
        """Create and persist a reproducible research run."""

        if (
            strategy_version.specification.timeframe.value
            != dataset.timeframe
        ):
            raise ValueError(
                "Strategy timeframe does not match dataset timeframe."
            )

        if dataset.symbol not in strategy_version.specification.instruments:
            raise ValueError(
                "Dataset symbol is not supported by the strategy."
            )

        canonical_json = canonical_parameters_json(parameters)

        run = ResearchRun(
            run_id=run_id or str(uuid4()),
            strategy_id=strategy_version.strategy_id,
            strategy_version=strategy_version.version,
            strategy_hash=_strategy_hash(strategy_version),
            dataset_hash=dataset.dataset_hash,
            symbol=dataset.symbol,
            timeframe=dataset.timeframe,
            start_time=dataset.start_time,
            end_time=dataset.end_time,
            parameters_json=canonical_json,
            parameters_hash=parameters_hash(parameters),
            status=ResearchRunStatus.CREATED,
            created_at=datetime.now(UTC),
        )

        self._repository.save(run)

        return ResearchRunCreationResult(run=run)


def _strategy_hash(strategy_version: StrategyVersion) -> str:
    """Return the canonical hash of a strategy version."""

    from private_quant_terminal.strategy.canonical import (
        strategy_hash,
    )

    return strategy_hash(strategy_version.specification)
