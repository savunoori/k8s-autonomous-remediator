from dataclasses import dataclass, replace
from enum import Enum
from uuid import UUID

class RemediationActionType(str,Enum):
    RESTART_ROLLOUT = "restart_rollout"
    SCALE_DEPLOYMENT = "scale_deployment"
    ROLLBACK_DEPLOYMENT = "rollback_deployment"

class RemediationActionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    EXECUTING = "executing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REJECTED = "rejected"

@dataclass(frozen=True, slots=True)
class RemediationAction:
    action_id: UUID
    incident_id: UUID
    action_type: RemediationActionType
    workload_name:str
    namespace:str
    status: RemediationActionStatus

    def transition_to(
        self,
        new_status: RemediationActionStatus,
    ) -> "RemediationAction":
        allowed_transitions = {
            RemediationActionStatus.PENDING: {
                RemediationActionStatus.APPROVED,
                RemediationActionStatus.REJECTED,
            },
            RemediationActionStatus.APPROVED: {
                RemediationActionStatus.EXECUTING,
            },
            RemediationActionStatus.EXECUTING: {
                RemediationActionStatus.SUCCEEDED,
                RemediationActionStatus.FAILED,
            },
            RemediationActionStatus.SUCCEEDED: set(),
            RemediationActionStatus.FAILED: set(),
            RemediationActionStatus.REJECTED: set(),
        }

        if new_status not in allowed_transitions[self.status]:
            raise ValueError(
                f"Invalid remediation action transition: "
                f"{self.status.value} -> {new_status.value}"
            )

        return replace(self, status=new_status)