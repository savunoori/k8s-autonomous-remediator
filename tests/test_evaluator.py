import pytest

from k8s_autonomous_remediator.domain.decision import (
    RemediationDecisionStatus,
)
from k8s_autonomous_remediator.domain.evaluator import (
    RemediationEvaluator,
)
from k8s_autonomous_remediator.domain.policy import (
    RemediationPolicy,
)
from k8s_autonomous_remediator.domain.remediation import (
    RemediationActionType
)

from datetime import datetime, timezone, timedelta


def test_evaluator_allows_permitted_action():
    policy = RemediationPolicy(
        allowed_actions=frozenset({
            RemediationActionType.RESTART_ROLLOUT,
        }),
    )

    evaluator = RemediationEvaluator(policy=policy)

    decision = evaluator.evaluate(
        action_type=RemediationActionType.RESTART_ROLLOUT,
        namespace="production",
        attempts_made=0,
        current_time=datetime(2026, 10, 14, 12, 0, tzinfo=timezone.utc),
    )

    assert decision.status is RemediationDecisionStatus.ALLOWED
    assert decision.reason == (
        "Action, namespace, retry, and cooldown checks passed"
    )

@pytest.mark.parametrize(
    "action_type, namespace, protected_namespaces",
    [
        (
            RemediationActionType.ROLLBACK_DEPLOYMENT,
            "production",
            frozenset(),
        ),
        (
            RemediationActionType.RESTART_ROLLOUT,
            "kube-system",
            frozenset(),
        ),
        (
            RemediationActionType.RESTART_ROLLOUT,
            "payments",
            frozenset({"payments"}),
        ),
    ],
)
def test_evaluator_blocks_unsafe_actions(
    action_type,
    namespace,
    protected_namespaces,
):
    policy = RemediationPolicy(
        allowed_actions=frozenset({
            RemediationActionType.RESTART_ROLLOUT,
        }),
        protected_namespaces=protected_namespaces,
    )

    evaluator = RemediationEvaluator(policy=policy)

    decision = evaluator.evaluate(
        action_type=action_type,
        namespace=namespace,
        attempts_made=0,
        current_time=datetime(2026, 10, 14, 12, 0, tzinfo=timezone.utc),
    )

    assert decision.status is RemediationDecisionStatus.BLOCKED
    assert decision.reason == "Action is not allowed by remediation policy"

@pytest.mark.parametrize(
    "attempts_made, expected_status",
    [
        (0, RemediationDecisionStatus.ALLOWED),
        (1, RemediationDecisionStatus.ALLOWED),
        (2, RemediationDecisionStatus.ALLOWED),
        (3, RemediationDecisionStatus.BLOCKED),
        (4, RemediationDecisionStatus.BLOCKED),
    ],
)
def test_evaluator_enforces_retry_limit(
    attempts_made,
    expected_status,
):
    policy = RemediationPolicy(
        allowed_actions=frozenset({
            RemediationActionType.RESTART_ROLLOUT,
        }),
        max_remediation_attempts=3,
    )

@pytest.mark.parametrize(
    "seconds_elapsed, expected_status",
    [
        (0, RemediationDecisionStatus.BLOCKED),
        (30, RemediationDecisionStatus.BLOCKED),
        (299, RemediationDecisionStatus.BLOCKED),
        (300, RemediationDecisionStatus.ALLOWED),
        (600, RemediationDecisionStatus.ALLOWED),
    ]
)
def test_evaluator_enforces_cooldown(
    seconds_elapsed,
    expected_status,
):
    policy = RemediationPolicy(
        allowed_actions=frozenset({
            RemediationActionType.RESTART_ROLLOUT,
        }),
        cooldown_seconds=300,
    )

    evaluator = RemediationEvaluator(policy=policy)

    last_attempt_at = datetime(
        2026, 10, 14, 12, 0, tzinfo=timezone.utc
    )

    current_time = last_attempt_at +timedelta(
        seconds=seconds_elapsed
    )

    decision = evaluator.evaluate(
        action_type=RemediationActionType.RESTART_ROLLOUT,
        namespace="production",
        attempts_made=0,
        last_attempt_at=last_attempt_at,
        current_time=current_time,
    )

    assert decision.status is expected_status

@pytest.mark.parametrize(
    "action_type, expected_status",
    [
        (
            RemediationActionType.RESTART_ROLLOUT,
            RemediationDecisionStatus.ALLOWED,
        ),
        (
            RemediationActionType.ROLLBACK_DEPLOYMENT,
            RemediationDecisionStatus.REQUIRES_APPROVAL,
        ),
        (
            RemediationActionType.SCALE_DEPLOYMENT,
            RemediationDecisionStatus.REQUIRES_APPROVAL,
        ),
    ],
)
def test_evaluator_requires_human_approval(
    action_type,
    expected_status,
):
    policy = RemediationPolicy(
        allowed_actions=frozenset({
            RemediationActionType.RESTART_ROLLOUT,
            RemediationActionType.ROLLBACK_DEPLOYMENT,
            RemediationActionType.SCALE_DEPLOYMENT
        }),
        approval_required_actions=frozenset({
            RemediationActionType.ROLLBACK_DEPLOYMENT,
            RemediationActionType.SCALE_DEPLOYMENT,
        }),
    )

    evaluator = RemediationEvaluator(policy=policy)

    decision = evaluator.evaluate(
        action_type=action_type,
        namespace="production",
        attempts_made=0,
        current_time=datetime(
            2026, 10, 14, 12, 0, tzinfo=timezone.utc
        ),
    )

    assert decision.status is expected_status

@pytest.mark.parametrize(
    "namespace, attempts_made, seconds_elapsed",
    [
        ("kube-system", 0, 300),
        ("production", 3, 300),
        ("production", 1, 30),
    ],
)
def test_evaluator_blocks_unsafe_Actions_before_approval(
    namespace,
    attempts_made,
    seconds_elapsed,
):
    policy = RemediationPolicy(
        allowed_actions=frozenset({
            RemediationActionType.ROLLBACK_DEPLOYMENT,
        }),
        max_remediation_attempts=3,
        cooldown_seconds=300,
    )
    evaluator = RemediationEvaluator(policy=policy)

    last_attempt_at = datetime(
        2026, 10, 14, 12, 0, tzinfo=timezone.utc
    )

    current_time = last_attempt_at + timedelta(
        seconds=seconds_elapsed
    )

    decision = evaluator.evaluate(
        action_type=RemediationActionType.ROLLBACK_DEPLOYMENT,
        namespace=namespace,
        attempts_made=attempts_made,
        last_attempt_at=last_attempt_at,
        current_time=current_time,
    )

    assert decision.status is RemediationDecisionStatus.BLOCKED

def test_evaluator_requires_attempt_count():
    policy = RemediationPolicy(
        allowed_actions=frozenset({
            RemediationActionType.RESTART_ROLLOUT,
        }),
    )

    evaluator = RemediationEvaluator(policy=policy)

    with pytest.raises(TypeError):
        evaluator.evaluate(
            action_type=RemediationActionType.RESTART_ROLLOUT,
            namespace="production",
            current_time=datetime(
                2026, 10, 14, 12,0, tzinfo=timezone.utc
            ),
        )