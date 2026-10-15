from kubernetes import client

class KubernetesDeploymentClient:
    def __init__(self) -> None:
        self.apps_api = client.AppsV1Api()

    def list_deployments(self, namespace:str):
        return self.apps_api.list_namespaced_deployment(
            namespace=namespace
        )
    def get_deployment(self, name:str, namespace:str):
        return self.apps_api.read_namespaced_deployment(
            name=name,
            namespace=namespace,
        )