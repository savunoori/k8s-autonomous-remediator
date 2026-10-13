from enum import Enum
from dataclasses import dataclass

class RemediationDecisionStatus(str, Enum):
    ALLOWED= "allowed"
    BLOCKED = "blocked"
    REQUIRES_APPROVAL = "requires_approval"

@dataclass(frozen=True, slots=True)
class RemediationDecision:
    status: RemediationDecisionStatus
    reason: str