from ..env import switch_card, Guess
from .Bot import Bot


class IlariiaB1V1Bot(Bot):

    def _act(self) -> int:
        if self.observation[2] == Guess.AWAITING_FOR_GUESS:
            return switch_card(self.observation[1])
        return switch_card(self.observation[2])

    def _observe(self):
        pass
