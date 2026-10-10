from dataclasses import dataclass, replace
from datetime import datetime
from enum import Enum
from uuid import UUID

class IncidentSeverity(str,Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IncidentStatus(str, Enum):
    DETECTED = "detected"
    INVESTIGATING = "investigating"
    REMEDIATING = "remediating"
    RESOLVED = "resolved"
    ESCALATED = "escalated"

@dataclass(frozen=True,slots=True)
class Incident:
    incident_id: UUID
    workload_name: str
    namespace: str
    reason: str
    severity: IncidentSeverity
    status: IncidentStatus
    detected_at: datetime

    def transition_to(self, new_status: IncidentStatus) -> "Incident":
        allowed_transitions = {
            IncidentStatus.DETECTED: {
                IncidentStatus.INVESTIGATING,
            },
            IncidentStatus.INVESTIGATING: {
                IncidentStatus.REMEDIATING,
                IncidentStatus.ESCALATED,
            },
            IncidentStatus.REMEDIATING: {
                IncidentStatus.RESOLVED,
                IncidentStatus.ESCALATED,
            },
            IncidentStatus.RESOLVED: set(),
            IncidentStatus.ESCALATED: set(),
        }

        if new_status not in allowed_transitions[self.status]:
            raise ValueError(
                f"Invalid incident transition: "
                f"{self.status.value} -> {new_status.value}"
            )
        return replace(self, status=new_status)