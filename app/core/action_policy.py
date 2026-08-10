from app.models import Action


class ActionPolicy:

    def __init__(
        self,
        default_action: Action = Action.FLAG,
        analyzer_actions: dict[str, Action] | None = None,
    ):
        self.default_action = default_action

        self.analyzer_actions = (
            analyzer_actions or {}
        )

    def get_action(
        self,
        analyzer_name: str,
    ) -> Action:

        return self.analyzer_actions.get(
            analyzer_name,
            self.default_action,
        )