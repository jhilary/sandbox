from random import random
from env import switch_card, Guess, Card, FirstTurnInRound
from .Bot import Bot


class MishaBotV2(Bot):

    def _act(self) -> object:
        if self.observation[2] == Guess.AWAITING_FOR_GUESS:
            return random.choice([Card.BLACK, Card.RED])
        elif self.observation[0] == FirstTurnInRound.YES:
            return switch_card(self.observation[2])
        else:
            return self.action

    def _observe(self) -> None:
        pass
