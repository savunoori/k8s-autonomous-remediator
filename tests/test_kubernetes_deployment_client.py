from unittest.mock import MagicMock

from k8s_autonomous_remediator.infrastructure.kubernetes.deployment_client import (
    KubernetesDeploymentClient,
)

def test_list_deployments_calls_kubernetes_api():
    mock_api = MagicMock()

    deployment_client = KubernetesDeploymentClient()
    deployment_client.apps_api = mock_api

    deployment_client.list_deployments(namespace="default")

    mock_api.list_namespaced_deployment.assert_called_once_with(
        namespace="default"
    )

def test_get_deployment_calls_kubernetes_api():
    mock_api = MagicMock()

    deployment_client = KubernetesDeploymentClient()
    deployment_client.apps_api = mock_api

    deployment_client.get_deployment(
        name="payment-service",
        namespace="production",
    )

    mock_api.read_namespaced_deployment.assert_called_once_with(
        name="payment-service",
        namespace="production",
    )

