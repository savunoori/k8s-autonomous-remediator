from dataclasses import FrozenInstanceError

import pytest

from k8s_autonomous_remediator.domain.decision import (
    RemediationDecision,
    RemediationDecisionStatus,
)

@pytest.mark.parametrize(
    "status",
    [
        RemediationDecisionStatus.ALLOWED,
        RemediationDecisionStatus.BLOCKED,
        RemediationDecisionStatus.REQUIRES_APPROVAL,
    ],
)
def test_remediation_decision_stores_status_and_reason(status):
    decision = RemediationDecision(
        status=status,
        reason="Policy evaluation completed",
    )

    assert decision.status is status
    assert decision.reason == "Policy evaluation completed"

def test_remediation_decision_is_immutable():
    decision = RemediationDecision(
        status=RemediationDecisionStatus.BLOCKED,
        reason="Namespace is protected",
    )

    with pytest.raises(FrozenInstanceError):
        decision.reason = "Action allowed"