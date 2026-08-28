
from private_quant_terminal.research import (
    ResearchParameters,
    ResearchRunStatus,
    canonical_parameters_json,
    parameters_hash,
)


def test_parameters_are_canonicalized() -> None:
    first = ResearchParameters(
        values={
            "lookback": 20,
            "risk": 0.02,
        }
    )

    second = ResearchParameters(
        values={
            "risk": 0.02,
            "lookback": 20,
        }
    )

    assert canonical_parameters_json(first) == canonical_parameters_json(
        second
    )


def test_parameter_hash_is_deterministic() -> None:
    parameters = ResearchParameters(
        values={
            "lookback": 20,
            "risk": 0.02,
        }
    )

    assert parameters_hash(parameters) == parameters_hash(parameters)
    assert len(parameters_hash(parameters)) == 64


def test_parameter_hash_changes_when_parameters_change() -> None:
    first = ResearchParameters(
        values={"lookback": 20}
    )

    second = ResearchParameters(
        values={"lookback": 21}
    )

    assert parameters_hash(first) != parameters_hash(second)


def test_research_status_is_created_initially() -> None:
    assert ResearchRunStatus.CREATED.value == "CREATED"
