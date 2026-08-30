import pytest

from private_quant_terminal.strategy.positions_state import (
    PositionStateSnapshot,
)
from private_quant_terminal.strategy.states import PositionState


def test_position_state_snapshot() -> None:
    snapshot = PositionStateSnapshot(
        group_id="entry",
        state=PositionState.OPEN,
        entry_count=1,
        exit_count=0,
    )

    assert snapshot.group_id == "entry"
    assert snapshot.state is PositionState.OPEN
    assert snapshot.entry_count == 1


def test_position_state_requires_group() -> None:
    with pytest.raises(
        ValueError,
        match="must not be empty",
    ):
        PositionStateSnapshot(
            group_id=" ",
            state=PositionState.FLAT,
        )


def test_position_state_rejects_negative_counts() -> None:
    with pytest.raises(
        ValueError,
        match="entry_count cannot be negative",
    ):
        PositionStateSnapshot(
            group_id="entry",
            state=PositionState.OPEN,
            entry_count=-1,
        )
