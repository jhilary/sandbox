from env import switch_card
from .Bot import Bot


class SmarterBaselineBot(Bot):

    def _act(self) -> object:
        return switch_card(self.observation[1])

    def _observe(self) -> None:
        pass
