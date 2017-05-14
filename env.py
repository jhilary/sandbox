import random

from gym import Env
from gym.spaces import Discrete


class CardsGuessing(Env):
    action_space = Discrete(2)
    observation_space = Discrete(2)

    def __init__(self, opponent):
        self._opponent = opponent
        self._round = 0

    def _step(self, action):
        pass

    def _reset(self):
        self._round

    def _seed(self, seed=None):
        random.seed(seed)
