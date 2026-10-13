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

@pytest.mark.parametrize(
    "invalid_attempts",
    [
        0,
        -1,
        -5,
        2.5,
        True,
        "three",
    ],
)
def test_policy_rejected_invalid_retry_limits(invalid_attempts):
    with pytest.raises(
        ValueError,
        match="max_remediation_attempts must be a positive integer",
    ):
        RemediationPolicy(
            allowed_actions=frozenset({
                RemediationActionType.RESTART_ROLLOUT,
            }),
            max_remediation_attempts=invalid_attempts,
        )

@pytest.mark.parametrize(
    "valid_attempts",
    [
        1,
        3,
        5,
        10,
    ],
)
def test_policy_accepts_valid_retry_limits(valid_attempts):
    policy = RemediationPolicy(
        allowed_actions=frozenset({
            RemediationActionType.RESTART_ROLLOUT,
        }),
        max_remediation_attempts=valid_attempts,
    )

    assert policy.max_remediation_attempts == valid_attempts

@pytest.mark.parametrize(
    "attempts_made, expected",
    [
        (0, True),
        (1, True),
        (2, True),
        (3, False),
        (4, False),
        (10, False),
    ],
)
def test_policy_enforces_retry_limits(attempts_made , expected):
    policy = RemediationPolicy(
        allowed_actions=frozenset({
            RemediationActionType.RESTART_ROLLOUT,
        }),
        max_remediation_attempts=3,
    )

    result = policy.allows_retry(
        attempts_made=attempts_made
    )

    assert result is expected

@pytest.mark.parametrize(
    "invalid_attempts",
    [
        -1,
        -5,
        2.5,
        True,
        "three",
    ],
)
def test_policy_rejects_invalid_attempt_counts(invalid_attempts):
    policy = RemediationPolicy(
        allowed_actions= frozenset({
            RemediationActionType.RESTART_ROLLOUT,
        }),
    )

    with pytest.raises(
        ValueError,
        match="attempts_made must be a non-negative integer",
    ):
        policy.allows_retry(
            attempts_made=invalid_attempts,
        )

@pytest.mark.parametrize(
    "invalid_cooldown",
    [
        -1,
        -300,
        -2.5,
        True,
        "300",
    ],
)
def test_polic_rejects_invalid_cooldown(invalid_cooldown):
    with pytest.raises(
        ValueError,
        match="cooldown_seconds must be a non-negative integer",
    ):
        RemediationPolicy(
            allowed_actions=frozenset({
                RemediationActionType.RESTART_ROLLOUT,
            }),
            cooldown_seconds=invalid_cooldown,
        )

@pytest.mark.parametrize(
    "valid_cooldown",
    [
        0,
        60,
        300,
        600,
    ],
)
def test_policy_accepts_valid_cooldown(valid_cooldown):
    policy = RemediationPolicy(
        allowed_actions=frozenset({
            RemediationActionType.RESTART_ROLLOUT,
        }),
        cooldown_seconds=valid_cooldown,
    )

    assert policy.cooldown_seconds == valid_cooldown