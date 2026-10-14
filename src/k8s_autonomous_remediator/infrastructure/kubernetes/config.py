from kubernetes import config

def load_kubernetes_config(in_cluster: bool = False) -> None:
    if in_cluster:
        config.load_incluster_config()
    else:
        config.load_kube_config()