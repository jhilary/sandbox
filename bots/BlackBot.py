from .Bot import Bot
from ..env import Card


class BlackBot(Bot):

    def _act(self) -> object:
        return Card.BLACK

    def _observe(self) -> None:
        pass
