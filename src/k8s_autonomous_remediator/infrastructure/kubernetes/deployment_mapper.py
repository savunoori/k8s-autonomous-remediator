from kubernetes.client import V1Deployment

from k8s_autonomous_remediator.domain.deployment_health import (
    DeploymentHealth,
)

class DeploymentHealthMapper:
    @staticmethod
    def from_kubernetes(deployment: V1Deployment) -> DeploymentHealth:
        return DeploymentHealth(
            name=deployment.metadata.name,
            namespace=deployment.metadata.namespace,
            desired_replicas=deployment.spec.replicas,
            ready_replicas=deployment.status.ready_replicas,
            available_replicas=deployment.status.available_replicas,
        )