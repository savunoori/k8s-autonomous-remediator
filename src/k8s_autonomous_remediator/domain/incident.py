from dataclasses import dataclass
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
