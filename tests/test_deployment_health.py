from dataclasses import FrozenInstanceError

import pytest
from k8s_autonomous_remediator.domain.deployment_health import(
    DeploymentHealth,
    DeploymentHealthStatus,
)

def test_deployment_health_stores_replicas_information():
    health = DeploymentHealth(
        name="payment-service",
        namespace="production",
        desired_replicas=3,
        ready_replicas=2,
        available_replicas=2,
    )

    assert health.name == "payment-service"
    assert health.namespace == "production"
    assert health.desired_replicas == 3
    assert health.ready_replicas == 2
    assert health.available_replicas == 2

def test_deployment_health_is_immutable():
    health = DeploymentHealth(
        name= "payment-service",
        namespace="production",
        desired_replicas=3,
        ready_replicas=2,
        available_replicas=2,
    )

    with pytest.raises(FrozenInstanceError):
        health.ready_replicas = 3

@pytest.mark.parametrize(
    "desired, ready, available, expected_status",
    [
        (3, 3, 3, DeploymentHealthStatus.HEALTHY),
        (3, 2, 2, DeploymentHealthStatus.DEGRADED),
        (3, 0, 0, DeploymentHealthStatus.UNAVAILABLE),
        (0, 0, 0, DeploymentHealthStatus.SCALED_DOWN),
        (3, 4, 3, DeploymentHealthStatus.UNKNOWN),
        (3, 2, 3, DeploymentHealthStatus.UNKNOWN),
        (3, None, None, DeploymentHealthStatus.UNKNOWN),
    ]
)
def test_deployment_health_classification(
    desired,
    ready,
    available,
    expected_status,
):
    health = DeploymentHealth(
        name="payment-service",
        namespace="production",
        desired_replicas=desired,
        ready_replicas=ready,
        available_replicas=available,
    )

    assert health.status == expected_status