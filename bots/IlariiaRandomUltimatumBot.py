from ..env import Card
from .IlariiaUltimatumBot import IlariiaUltimatumBot


class IlariiaRandomUltimatumBot(IlariiaUltimatumBot):
    def _basic_strategy(self) -> Card:
        return self.env.actions_space.sample()
