from dataclasses import dataclass, replace
from datetime import UTC, datetime

from private_quant_terminal.strategy.enums import StrategyStatus
from private_quant_terminal.strategy.ir import (
    StrategyDefinition,
    StrategyVersion,
)
from private_quant_terminal.strategy.repository import (
    StrategyVersionRepository,
)
from private_quant_terminal.strategy.validation import (
    StrategyValidationResult,
    validate_strategy,
)


@dataclass(frozen=True)
class StrategyCreationResult:
    """Result of creating and validating a strategy version."""

    version: StrategyVersion
    validation: StrategyValidationResult


class StrategyLifecycleService:
    """Coordinate strategy validation, versioning, and persistence."""

    def __init__(
        self,
        repository: StrategyVersionRepository,
    ) -> None:
        self._repository = repository

    def create_version(
        self,
        strategy: StrategyDefinition,
    ) -> StrategyCreationResult:
        """Validate and persist a new immutable strategy version."""

        validation = validate_strategy(strategy)

        if not validation.valid:
            raise ValueError(
                "Cannot create strategy version: "
                + "; ".join(
                    f"{issue.field}: {issue.message}"
                    for issue in validation.issues
                )
            )

        validated_strategy = replace(
            strategy,
            status=StrategyStatus.VALIDATED,
        )

        version_number = self._repository.next_version(
            validated_strategy.strategy_id
        )

        version = StrategyVersion(
            strategy_id=validated_strategy.strategy_id,
            version=version_number,
            specification=validated_strategy,
            created_at=datetime.now(UTC),
        )

        self._repository.save(version)

        return StrategyCreationResult(
            version=version,
            validation=validation,
        )
