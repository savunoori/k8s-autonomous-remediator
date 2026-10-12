from dataclasses import dataclass

from k8s_autonomous_remediator.domain.remediation import (
    RemediationActionType,
)

@dataclass(frozen=True, slots=True)
class RemediationPolicy:
    allowed_actions: frozenset[RemediationActionType]
    protected_namespaces: frozenset[str] = frozenset({
        "kube-system",
        "kube-public",
        "kube-node-lease",
    })

    def allows(
        self, 
        action_type: RemediationActionType,
        namespace: str,
    ) -> bool:
        if action_type not in self.allowed_actions:
            return False
        if namespace in self.protected_namespaces:
            return False
        return True

