import random
from enum import IntEnum

from gym import Env
from gym.spaces import Discrete, MultiDiscrete


class Guess(IntEnum):
    AWAITING_FOR_GUESS = 0
    RED = 1
    BLACK = 2


class Card(IntEnum):
    RED = 0
    BLACK = 1


class CardsGuessing(Env):
    # noinspection PyTypeChecker
    action_space = Discrete(len(list(Card)))
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
        self._opponent_said: Card = None
        self._opponent_card = random.choice(Card)
        self._player_passed = False
        self._player_said: Card = None
        self._player_card = random.choice(Card)

    def _get_round_rewards(self):
        player_correct = self._opponent_card == self._player_said
        opponent_correct = self._player_card == self._opponent_said
        bank = (self._opponent_money - self._opponent_current_money) + \
               (self._player_money - self._player_current_money)
        if player_correct and opponent_correct:
            value = bank / 2
            p_value = self._player_current_money + value - self._player_money
            o_value = self._opponent_current_money + value - self._opponent_money
            assert p_value + p_value == 0.0, (p_value, o_value)
        elif player_correct and not opponent_correct:
            p_value = self._player_current_money + bank - self._player_money
            o_value = self._opponent_current_money - self._opponent_money
        elif not player_correct and opponent_correct:
            p_value = self.current_money[self.player1] - self.starting_money[self.player1]
            p2_value = self.current_money[self.player2] + self.bank - self.starting_money[self.player2]
        else:
            self.info("Both player guessed wrong")
            p1_value, p2_value = 0.0, 0.0

    def _step(self, action: int):
        if self._player_said is None:
            self._player_said = action
            self._player_current_money -= 10
        elif self._player_said != action:
            self._player_said = Card(action)
            self._player_current_money -= 10
        else:
            self._player_passed = True

        # if self._player_passed and self._opponent_passed:



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
