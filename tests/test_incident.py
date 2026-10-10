from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from uuid import uuid4
import pytest

from k8s_autonomous_remediator.domain.incident import (
    Incident,
    IncidentSeverity,
    IncidentStatus,         
)

def test_incident_creation():
    incident_id = uuid4()
    detected_at = datetime.now(timezone.utc)

    incident = Incident(
        incident_id=incident_id,
        workload_name="payment-api",
        namespace="production",
        reason="High 500 erroor rate exceeded 15%",
        severity=IncidentSeverity.HIGH,
        status=IncidentStatus.DETECTED,
        detected_at=detected_at,
    )

    assert incident.incident_id == incident_id
    assert incident.workload_name == "payment-api"
    assert incident.namespace == "production"
    assert incident.severity == IncidentSeverity.HIGH
    assert incident.status == IncidentStatus.DETECTED
    assert incident.detected_at == detected_at

def test_incident_cannot_be_modified():
    incident = Incident(
        incident_id=uuid4(),
        workload_name="payment-api",
        namespace="production",
        reason="High HTTP 500 error rate",
        severity=IncidentSeverity.HIGH,
        status=IncidentStatus.DETECTED,
        detected_at=datetime.now(timezone.utc),
    )

    with pytest.raises(FrozenInstanceError):
        incident.status = IncidentStatus.RESOLVED