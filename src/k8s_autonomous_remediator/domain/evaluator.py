from dataclasses import dataclass
from k8s_autonomous_remediator.domain.decision import (
    RemediationDecision,
    RemediationDecisionStatus,
)
from k8s_autonomous_remediator.domain.policy import RemediationPolicy
from k8s_autonomous_remediator.domain.remediation import RemediationActionType
from datetime import datetime

@dataclass(frozen=True, slots=True)
class RemediationEvaluator:
    policy: RemediationPolicy

    def evaluate(
        self,
        action_type: RemediationActionType,
        namespace: str,
        attempts_made: int,
        last_attempt_at: datetime | None = None,
        current_time: datetime | None = None,
    ) -> RemediationDecision:
        if not self.policy.allows(action_type, namespace):
            return RemediationDecision(
                status=RemediationDecisionStatus.BLOCKED,
                reason="Action is not allowed by remediation policy",
            )
        if current_time is None:
            raise ValueError("current_time is required for cooldown evaluation")

        if not self.policy.allows_cooldown(last_attempt_at, current_time):
            return RemediationDecision(
                status= RemediationDecisionStatus.BLOCKED,
                reason="Remediation cooldown period has not elapsed",
            )

        if not self.policy.allows_retry(attempts_made):
            return RemediationDecision(
                status=RemediationDecisionStatus.BLOCKED,
                reason="Maximum remediation attempts exceeded",
            )
            
        if self.policy.requires_approval(action_type):
            return RemediationDecision(
                status=RemediationDecisionStatus.REQUIRES_APPROVAL,
                reason= "Remediation action requires human approval",
            )

        return RemediationDecision(
            status=RemediationDecisionStatus.ALLOWED,
            reason="Action, namespace, retry, and cooldown checks passed",
        )