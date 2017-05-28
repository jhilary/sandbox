from env import Card
from .IlariiaUltimatumBot import IlariiaUltimatumBot


class IlariiaRandomUltimatumBot(IlariiaUltimatumBot):
    def _basic_strategy(self) -> Card:
        return self.env.action_space.sample()
