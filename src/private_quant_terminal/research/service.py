from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from private_quant_terminal.data.identity import (
    DatasetIdentity,
    candle_dataset_hash,
)
from private_quant_terminal.models import Candle
from private_quant_terminal.research.execution import (
    ResearchExecutionRequest,
    ResearchExecutionResult,
)
from private_quant_terminal.research.executor import ResearchExecutor
from private_quant_terminal.research.integrity import (
    ResearchIntegrityAnalyzer,
    ResearchIntegrityReport,
    ResearchIntegrityStatus,
)
from private_quant_terminal.research.intelligence import (
    ResearchIntelligenceAnalyzer,
    ResearchIntelligenceReport,
)
from private_quant_terminal.research.performance import (
    ResearchPerformanceAnalyzer,
    ResearchPerformanceReport,
)
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
from private_quant_terminal.strategy.canonical import strategy_hash
from private_quant_terminal.strategy.ir import StrategyVersion


@dataclass(frozen=True)
class ResearchRunCreationResult:
    """Result of creating a research run."""

    run: ResearchRun


@dataclass(frozen=True)
class ResearchAnalysisResult:
    """Complete result of executing and analyzing a research run."""

    run: ResearchRun
    execution: ResearchExecutionResult
    performance: ResearchPerformanceReport
    integrity: ResearchIntegrityReport
    intelligence: ResearchIntelligenceReport


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

    def execute_run(
        self,
        run: ResearchRun,
        strategy_version: StrategyVersion,
        candles: tuple[Candle, ...],
        initial_equity: float,
    ) -> ResearchAnalysisResult:
        """Execute and analyze a research run deterministically."""

        if run.strategy_id != strategy_version.strategy_id:
            raise ValueError(
                "strategy identity does not match research run"
            )

        if run.strategy_version != strategy_version.version:
            raise ValueError(
                "strategy version does not match research run"
            )

        if run.strategy_hash != strategy_hash(
            strategy_version.specification
        ):
            raise ValueError(
                "strategy hash does not match research run"
            )

        if not candles:
            raise ValueError(
                "research execution requires at least one candle"
            )

        actual_dataset_hash = candle_dataset_hash(list(candles))

        if run.dataset_hash != actual_dataset_hash:
            raise ValueError(
                "dataset hash does not match research run"
            )

        persisted_run = self._repository.get(run.run_id)

        should_update_lifecycle = (
            persisted_run.status is ResearchRunStatus.CREATED
        )

        if should_update_lifecycle:
            self._repository.update_status(
                run.run_id,
                ResearchRunStatus.RUNNING,
            )
        elif persisted_run.status is not ResearchRunStatus.COMPLETED:
            raise ValueError(
                "Research run is not executable from status: "
                f"{persisted_run.status.value}"
            )

        try:
            execution = ResearchExecutor(
                initial_equity=initial_equity,
            ).execute(
                ResearchExecutionRequest(
                    run=run,
                    strategy_version=strategy_version,
                    candles=candles,
                )
            )

            integrity = ResearchIntegrityAnalyzer().analyze(
                execution
            )

            if integrity.status is ResearchIntegrityStatus.FAIL:
                raise ValueError(
                    "research execution failed integrity validation"
                )

            performance = ResearchPerformanceAnalyzer().analyze(
                execution
            )
            intelligence = ResearchIntelligenceAnalyzer().analyze(
                performance=performance,
                integrity=integrity,
            )

        except Exception:
            self._repository.update_status(
                run.run_id,
                ResearchRunStatus.FAILED,
            )
            raise

        self._repository.save_result(
            execution=execution,
            performance=performance,
            integrity=integrity,
            intelligence=intelligence,
        )

        if should_update_lifecycle:
            self._repository.update_status(
                run.run_id,
                ResearchRunStatus.COMPLETED,
            )

        completed_run = self._repository.get(run.run_id)

        return ResearchAnalysisResult(
            run=completed_run,
            execution=execution,
            performance=performance,
            integrity=integrity,
            intelligence=intelligence,
        )


def _strategy_hash(strategy_version: StrategyVersion) -> str:
    """Return the canonical hash of a strategy version."""

    from private_quant_terminal.strategy.canonical import (
        strategy_hash,
    )

    return strategy_hash(strategy_version.specification)
