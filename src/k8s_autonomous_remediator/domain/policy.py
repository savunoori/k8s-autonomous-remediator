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
    cooldown_seconds: int = 300

    def __post_init__(self) -> None:
        if (
            type(self.max_remediation_attempts) is not int
            or self.max_remediation_attempts < 1
        ):
            raise ValueError(
                "max_remediation_attempts must be a positive integer"
            )
        if (
            type(self.cooldown_seconds) is not int
            or self.cooldown_seconds < 0
        ):
            raise ValueError(
                "cooldown_seconds must be a non-negative integer"
            )

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

    def allows_retry(self, attempts_made: int) -> bool:
        if type(attempts_made)  is not int or attempts_made < 0:
            raise ValueError(
                "attempts_made must be a non-negative integer"
            )
        return attempts_made < self.max_remediation_attempts
