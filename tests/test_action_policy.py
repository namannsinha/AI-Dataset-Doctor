from app.core.action_policy import ActionPolicy
from app.models import Action


def test_policy_returns_configured_action():

    policy = ActionPolicy(
        analyzer_actions={
            "corruption": Action.QUARANTINE,
            "duplicate": Action.FLAG,
        }
    )

    assert (
        policy.get_action("corruption")
        == Action.QUARANTINE
    )

    assert (
        policy.get_action("duplicate")
        == Action.FLAG
    )


def test_policy_uses_default_action():

    policy = ActionPolicy(
        default_action=Action.FLAG,
        analyzer_actions={
            "corruption": Action.QUARANTINE,
        }
    )

    assert (
        policy.get_action("blur")
        == Action.FLAG
    )


def test_policy_can_ignore_analyzer():

    policy = ActionPolicy(
        analyzer_actions={
            "resolution": Action.IGNORE,
        }
    )

    assert (
        policy.get_action("resolution")
        == Action.IGNORE
    )