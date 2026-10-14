from unittest.mock import patch
import pytest

from k8s_autonomous_remediator.infrastructure.kubernetes.config import (
    load_kubernetes_config,
)

def test_load_kubernetes_config_uses_local_kubeconfig():
    with patch(
        "k8s_autonomous_remediator.infrastructure.kubernetes.config.config.load_kube_config"
    ) as mock_load_kube_config:
        load_kubernetes_config(in_cluster=False)

        mock_load_kube_config.assert_called_once_with()

def test_load_kubernetes_Config_uses_incluster_Config():
    with patch(
        "k8s_autonomous_remediator.infrastructure.kubernetes.config.config.load_incluster_config"
    ) as mock_incluster:
        with patch(
            "k8s_autonomous_remediator.infrastructure.kubernetes.config.config.load_kube_config"
        ) as mock_local:
            load_kubernetes_config(in_cluster=True)

            mock_incluster.assert_called_once_with()
            mock_local.assert_not_called()

def test_load_kubernetes_config_propagates_authentication_error():
    with patch(
        "k8s_autonomous_remediator.infrastructure.kubernetes.config.config.load_kube_config"
    ) as mock_load_config:
        mock_load_config.side_effect = RuntimeError(
            "Kubernetes authentication failed"
        )

        with pytest.raises(
            RuntimeError,
            match="Kubernetes authentication failed",
        ):
            load_kubernetes_config(in_cluster=False)

def test_load_kubernetes_config_propagates_incluster_Error():
    with patch(
        "k8s_autonomous_remediator.infrastructure.kubernetes.config.config.load_incluster_config"
    ) as mock_incluster:

        mock_incluster.side_effect = RuntimeError(
            "In-cluster authentication failed"
        )
        
        with pytest.raises(
            RuntimeError,
            match="In-cluster authentication failed",
        ):
            load_kubernetes_config(in_cluster=True)

