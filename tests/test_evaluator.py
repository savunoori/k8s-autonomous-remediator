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
    )

    assert decision.status is RemediationDecisionStatus.ALLOWED
    assert decision.reason == "Action and namespace checks passed"

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
    )

    assert decision.status is RemediationDecisionStatus.BLOCKED
    assert decision.reason == "Action is not allowed by remediation policy"