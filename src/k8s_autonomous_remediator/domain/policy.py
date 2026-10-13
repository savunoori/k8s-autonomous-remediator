from dataclasses import dataclass
from typing import ClassVar
from datetime import datetime, timedelta

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
    approval_required_actions: frozenset[RemediationActionType] = frozenset({
        RemediationActionType.ROLLBACK_DEPLOYMENT,
    })

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

    def allows_cooldown(
        self,
        last_attempt_at: datetime | None,
        current_time: datetime,
    ) -> bool:
        if current_time.tzinfo is None or current_time.utcoffset() is None:
            raise ValueError("current_time must be timezone-aware")

        if last_attempt_at is None:
            return True
        if (
            last_attempt_at.tzinfo is None 
            or last_attempt_at.utcoffset() is None
        ):
            raise ValueError("last_attempt_at must be timezone-aware")
        if last_attempt_at > current_time:
            raise ValueError("last_attempt_at cannot be in the future")

        next_allowed_time = last_attempt_at + timedelta(
            seconds=self.cooldown_seconds
        )

        return current_time >= next_allowed_time

    def requires_approval(
        self,
        action_type: RemediationActionType,
    ) -> bool:
        return action_type in self.approval_required_actions
