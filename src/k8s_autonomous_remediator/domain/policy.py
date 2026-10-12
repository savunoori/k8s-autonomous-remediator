from dataclasses import dataclass
from typing import ClassVar

from k8s_autonomous_remediator.domain.remediation import (
    RemediationActionType,
)

@dataclass(frozen=True, slots=True)
class RemediationPolicy:
    MANDATORY_PROTECTED_NAMESPACES: ClassVar[frozenset[str]] = frozenset({
        "kube-system",
        "kube-public",
        "kube-node-lease",
    })

    allowed_actions: frozenset[RemediationActionType]
    protected_namespaces: frozenset[str] = frozenset()
    max_remediation_attempts: int = 3

    def allows(
        self,
        action_type:RemediationActionType,
        namespace:str,
    ) -> bool:
        if action_type not in self.allowed_actions:
         return False

        effective_protected_namespaces = (
            self.MANDATORY_PROTECTED_NAMESPACES
            | self.protected_namespaces
         )

        if namespace in effective_protected_namespaces:
            return False

        return True
