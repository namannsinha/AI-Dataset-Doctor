from app.models import Action


def test_action_values():

    assert Action.FLAG.value == "flag"
    assert Action.QUARANTINE.value == "quarantine"
    assert Action.IGNORE.value == "ignore"