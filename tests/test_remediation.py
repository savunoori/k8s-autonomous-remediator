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

@pytest.mark.parametrize(
    "current_status, next_status",
    [
        (RemediationActionStatus.PENDING, RemediationActionStatus.APPROVED),
        (RemediationActionStatus.PENDING, RemediationActionStatus.REJECTED),
        (RemediationActionStatus.APPROVED, RemediationActionStatus.EXECUTING),
        (RemediationActionStatus.EXECUTING, RemediationActionStatus.SUCCEEDED),
        (RemediationActionStatus.EXECUTING, RemediationActionStatus.FAILED),
    ],
)
def test_remediation_allows_valid_status_transitions(
    current_status,
    next_status,
):
    action = RemediationAction(
        action_id=uuid4(),
        incident_id=uuid4(),
        action_type=RemediationActionType.ROLLBACK_DEPLOYMENT,
        workload_name="payment-api",
        namespace="production",
        status=current_status,
    )

    updated_action = action.transition_to(next_status)

    assert updated_action.status == next_status
    assert action.status == current_status
    assert updated_action.action_id == action.action_id
    assert updated_action.incident_id == action.incident_id

@pytest.mark.parametrize(
    "current_status, next_status",
    [
        (RemediationActionStatus.PENDING, RemediationActionStatus.EXECUTING),
        (RemediationActionStatus.APPROVED, RemediationActionStatus.SUCCEEDED),
        (RemediationActionStatus.REJECTED, RemediationActionStatus.EXECUTING),
        (RemediationActionStatus.SUCCEEDED, RemediationActionStatus.EXECUTING),
        (RemediationActionStatus.FAILED, RemediationActionStatus.APPROVED),
    ],
)
def test_remediation_rejects_invalid_status_transitions(
    current_status,
    next_status,
):
    action =RemediationAction(
        action_id=uuid4(),
        incident_id=uuid4(),
        action_type=RemediationActionType.ROLLBACK_DEPLOYMENT,
        workload_name="payment-api",
        namespace="production",
        status=current_status,
   )

    with pytest.raises(
        ValueError,
        match ="Invalid remediation action transition",
    ):
        action.transition_to(next_status)
