from dataclasses import FrozenInstanceError

import pytest

from private_quant_terminal.risk.result import RiskResult


class TestRiskResult:
    def test_creates_approved_result(self) -> None:
        result = RiskResult(approved=True)

        assert result.approved is True
        assert result.reason is None

    def test_creates_rejected_result_with_reason(self) -> None:
        result = RiskResult(
            approved=False,
            reason="Order quantity exceeds configured limit",
        )

        assert result.approved is False
        assert result.reason == "Order quantity exceeds configured limit"

    def test_rejects_approved_result_with_reason(self) -> None:
        with pytest.raises(
            ValueError,
            match="approved risk results cannot include a rejection reason",
        ):
            RiskResult(
                approved=True,
                reason="This should not exist",
            )

    @pytest.mark.parametrize(
        "reason",
        [
            None,
            "",
        ],
    )
    def test_rejects_rejected_result_without_reason(
        self,
        reason: str | None,
    ) -> None:
        with pytest.raises(
            ValueError,
            match="rejected risk results must include a reason",
        ):
            RiskResult(
                approved=False,
                reason=reason,
            )

    def test_risk_result_is_immutable(self) -> None:
        result = RiskResult(approved=True)

        with pytest.raises(FrozenInstanceError):
            result.approved = False
