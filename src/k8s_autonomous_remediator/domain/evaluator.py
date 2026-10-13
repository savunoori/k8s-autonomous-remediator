from dataclasses import dataclass
from k8s_autonomous_remediator.domain.decision import (
    RemediationDecision,
    RemediationDecisionStatus,
)
from k8s_autonomous_remediator.domain.policy import RemediationPolicy
from k8s_autonomous_remediator.domain.remediation import RemediationActionType

@dataclass(frozen=True, slots=True)
class RemediationEvaluator:
    policy: RemediationPolicy

    def evaluate(
        self,
        action_type: RemediationActionType,
        namespace: str,
    ) -> RemediationDecision:
        if not self.policy.allows(action_type, namespace):
            return RemediationDecision(
                status=RemediationDecisionStatus.BLOCKED,
                reason="Action is not allowed by remediation policy",
            )

        return RemediationDecision(
            status=RemediationDecisionStatus.ALLOWED,
            reason="Action and namespace checks passed",
        )