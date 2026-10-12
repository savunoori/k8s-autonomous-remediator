import pytest

from k8s_autonomous_remediator.domain.policy import RemediationPolicy
from k8s_autonomous_remediator.domain.remediation import RemediationActionType

@pytest.mark.parametrize(
    "action_type, expected",
    [
        (RemediationActionType.RESTART_ROLLOUT, True),
        (RemediationActionType.ROLLBACK_DEPLOYMENT, True),
        (RemediationActionType.SCALE_DEPLOYMENT, False),
    ],
)

def test_policy_evaluates_allowed_actions(action_type, expected):
    policy = RemediationPolicy(
        allowed_actions=frozenset({
            RemediationActionType.RESTART_ROLLOUT,
            RemediationActionType.ROLLBACK_DEPLOYMENT,
        })
    )
    result = policy.allows(action_type, namespace="production")

    assert result is expected

def test_policy_denies_all_actions_when_allowlist_is_empty():
    policy = RemediationPolicy(
        allowed_actions=frozenset()
    )

    for action_type in RemediationActionType:
        assert policy.allows(action_type, namespace="production") is False

@pytest.mark.parametrize(
    "namespace, expected",
    [
        ("kube-system", False),
        ("kube-public", False),
        ("kube-node-lease", False),
        ("production", True),
        ("staging", True),
    ],
)

def test_policy_enforces_protected_namespaces(
    namespace,
    expected,
):
    policy = RemediationPolicy(
        allowed_actions=frozenset({
            RemediationActionType.RESTART_ROLLOUT,
        })
   )

    result = policy.allows(
        action_type=RemediationActionType.RESTART_ROLLOUT,
        namespace=namespace,
   )

    assert result is expected

def test_policy_supports_custom_protected_namespaces():
    policy = RemediationPolicy(
        allowed_actions=frozenset({
            RemediationActionType.ROLLBACK_DEPLOYMENT,
        }),
        protected_namespaces=frozenset({
            "finance-critical",
            "kube-system",
            "kube-public",
            "kube-node-lease",
        })
    )

    result = policy.allows(
        action_type=RemediationActionType.ROLLBACK_DEPLOYMENT,
        namespace="finance-critical",
    )
    assert result is False

@pytest.mark.parametrize(
    "namespace",
    [
        "kube-system",
        "kube-public",
        "kube-node-lease",
    ],
)
def test_mandatory_namespaces_remain_protected(
    namespace,
):
    policy = RemediationPolicy(
        allowed_actions=frozenset({
            RemediationActionType.RESTART_ROLLOUT,
        }),
        protected_namespaces=frozenset(),
    )

    result=policy.allows(
        action_type=RemediationActionType.RESTART_ROLLOUT,
        namespace=namespace,
    )

    assert result is False

def test_custom_namespaces_preserve_mandatory_protection():
    policy = RemediationPolicy(
        allowed_actions=frozenset({
            RemediationActionType.ROLLBACK_DEPLOYMENT,
        }),
        protected_namespaces=frozenset({
            "finance-critical",
        }),
    )

    for namespace in (
        "finance-critical",
        "kube-system",
        "kube-public",
        "kube-node-lease",
    ):
        assert policy.allows(
            action_type=RemediationActionType.ROLLBACK_DEPLOYMENT,
            namespace=namespace,
        ) is False