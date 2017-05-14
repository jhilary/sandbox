import random
from enum import IntEnum

from gym import Env
from gym.spaces import Discrete, MultiDiscrete


class Action(IntEnum):
    SAY_RED = 0
    SAY_BLACK = 1


class Guess(IntEnum):
    AWAITING_FOR_GUESS = 0
    SAID_RED = 1
    SAID_BLACK = 2


class Card(IntEnum):
    RED = 0
    BLACK = 1


class CardsGuessing(Env):
    # noinspection PyTypeChecker
    action_space = Discrete(len(list(Action)))
    # noinspection PyTypeChecker
    observation_space = MultiDiscrete([[0, 1], [0, 2]])  # Card x Guess

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
        self._opponent_card = Action(random.choice([0, 1]))

        self._player_passed = False
        self._player_said: Action = None
        self._player_card = Action(random.choice([0, 1]))

    def _get_round_rewards(self):
        player_correct = self._opponent_card == self._player_said
        opponent_correct = self._player_card == self._opponent_said
        bank = (self._opponent_money - self._opponent_current_money) + \
               (self._player_money - self._player_current_money)
        # if player_correct and opponent_correct:
        #     value = bank / 2
        #     p_value = self._player_current_money + value - self._player_money
        #     o_value = self.current_money[self.player2] + value - self.starting_money[self.player2]
        #     assert p1_value + p2_value == 0.0, (p1_value, p2_value)

    def _step(self, action: int):
        if self._player_said is None:
            self._player_said = action
            self._player_current_money -= 10
        elif self._player_said != action:
            self._player_said = Action(action)
            self._player_current_money -= 10
        else:
            self._player_passed = True

        if self._player_passed and self._opponent_passed:



        self._opponent_current_money -= 10
        opponent_action = self._opponent

    def _reset(self):
        self._opponent_said = None
        self._opponent_passed = None
        self._player_said = None
        starting_state = Guess.AWAITING_FOR_GUESS, 0, False, {}
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
