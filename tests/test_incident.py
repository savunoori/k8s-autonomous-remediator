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


def test_incident_allows_valid_status_transition():
    incident = Incident(
        incident_id=uuid4(),
        workload_name="payment-api",
        namespace="production",
        reason="HTTP 500 error rate exceeded 15%",
        severity=IncidentSeverity.HIGH,
        status=IncidentStatus.DETECTED,
        detected_at=datetime.now(timezone.utc),
    )

    updated_incident = incident.transition_to(
        IncidentStatus.INVESTIGATING
    )

    assert updated_incident.status == IncidentStatus.INVESTIGATING

    assert incident.status == IncidentStatus.DETECTED

    assert updated_incident.incident_id == incident.incident_id

def test_incident_rejects_invalid_status_transition():
    incident = Incident(
        incident_id=uuid4(),
        workload_name="payment-api",
        namespace="production",
        reason="HTTP 500 error rate exceeded 15%",
        severity=IncidentSeverity.HIGH,
        status=IncidentStatus.DETECTED,
        detected_at=datetime.now(timezone.utc),
    )

    with pytest.raises(
        ValueError,
        match="Invalid incident transition",
    ):
        incident.transition_to(IncidentStatus.RESOLVED)

@pytest.mark.parametrize(
    "current_status, new_status",
    [
        (IncidentStatus.DETECTED, IncidentStatus.INVESTIGATING),
        (IncidentStatus.INVESTIGATING, IncidentStatus.REMEDIATING),
        (IncidentStatus.INVESTIGATING, IncidentStatus.ESCALATED),
        (IncidentStatus.REMEDIATING, IncidentStatus.RESOLVED),
        (IncidentStatus.REMEDIATING, IncidentStatus.ESCALATED),
    ],
)

def test_incident_allows_supported_lifecycle_transitions(
    current_status,
    new_status,
):
    incident = Incident(
        incident_id=uuid4(),
        workload_name="payment-api",
        namespace="production",
        reason="HTTP 500 error rate exceeded threshold",
        severity=IncidentSeverity.HIGH,
        status=current_status,
        detected_at=datetime.now(timezone.utc),
    )

    updated_incident = incident.transition_to(new_status)
    
    assert updated_incident.status ==new_status
    assert incident.status == current_status
    assert updated_incident.incident_id == incident.incident_id

@pytest.mark.parametrize(
    "terminal_status",
    [
        IncidentStatus.RESOLVED,
        IncidentStatus.ESCALATED,
    ]
)

def test_incident_rejects_transitions_from_terminal_stated(
    terminal_status,
):
    incident =Incident(
        incident_id=uuid4(),
        workload_name="payment-api",
        namespace="production",
        reason="HTTP 500 error rate exceeded threshold",
        severity=IncidentSeverity.HIGH,
        status=terminal_status,
        detected_at=datetime.now(timezone.utc),
    )

    with pytest.raises(ValueError, match="Invalid incident transition"):
        incident.transition_to(IncidentStatus.INVESTIGATING)