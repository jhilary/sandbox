import random
from enum import IntEnum

from gym import Env
from gym.spaces import Discrete


class Action(IntEnum):
    SAY_RED = 0
    SAY_BLACK = 1


class Observation(IntEnum):
    AWAITING_FOR_GUESS = 0
    SAID_RED = 1
    SAID_BLACK = 2


class CardsGuessing(Env):
    action_space = Discrete(Action)

    observation_space = Discrete(3)
    AWAITING_FOR_GUESS = 0
    SAID_RED = 1
    SAID_BLACK = 2

    def __init__(self, starting_money, opponent):
        self._opponent = opponent
        self._start_anew()
        self._player_money = starting_money
        self._opponent_money = starting_money
        self._player_current_money = starting_money
        self._opponent_current_money = starting_money
        opponent.set_env(self)

    def _start_anew(self):
        self._opponent_passed = False
        self._opponent_said: Action = None
        self._opponent_card = None

        self._player_passed = False
        self._player_said: Action = None
        self._player_card = None

    def _step(self, action: int):
        if self._player_said is None:
            self._player_said = action
            self._player_current_money -= 10
        elif self._player_said != action:
            self._player_said = Action(action)
            self._player_current_money -= 10
        else:
            self._player_passed = True

        self._opponent_current_money -= 10
        opponent_action = self._opponent

    def _reset(self):
        self._opponent_said = None
        self._opponent_passed = None
        self._player_said = None
        starting_state = Observation.AWAITING_FOR_GUESS, 0, False, {}
        if random.random() < 0.5:
            return starting_state
        else:
            self._opponent.observe(starting_state)
            action = self._opponent.act()
            self._opponent_current_money -= 10
            self._opponent_said = action
            return action, 0, False, {}

    def _seed(self, seed=None):
        random.seed(seed)
