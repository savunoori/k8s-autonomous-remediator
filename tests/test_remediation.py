from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from k8s_autonomous_remediator.domain.remediation import (
    RemediationAction,
    RemediationActionStatus,
    RemediationActionType,
)

def test_remediation_Action_creation():
    action_id = uuid4()
    incident_id = uuid4()

    action = RemediationAction(
        action_id=action_id,
        incident_id=incident_id,
        action_type=RemediationActionType.ROLLBACK_DEPLOYMENT,
        workload_name="payment-api",
        namespace="production",
        status=RemediationActionStatus.PENDING,
    )

    assert action.action_id == action_id
    assert action.incident_id == incident_id
    assert action.action_type == RemediationActionType.ROLLBACK_DEPLOYMENT
    assert action,workload_name == "payment-api"
    assert action.namespace == "production"
    assert action.status == RemediationActionStatus.PENDING

def test_remediation_acton_caanot_be_modifeied():
    action = RemediationAction(
        action_id=uuid4(),
        incident_id=uuid4(),
        action_type=RemediationActionType.RESTART_ROLLOUT,
        workload_name="payment-api",
        namespace="production",
        status=RemediationActionStatus.PENDING,
    )

    with pytest.raises(FrozenInstanceError):
        action.status = RemediationActionStatus.APPROVED