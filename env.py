import random
from enum import IntEnum
from typing import Dict

from gym import Env
from gym.spaces import Discrete, MultiDiscrete


class Guess(IntEnum):
    AWAITING_FOR_GUESS = 0
    RED = 1
    BLACK = 2


class Card(IntEnum):
    RED = 0
    BLACK = 1


class Player(object):
    pass


class CardsGuessing(Env):
    _player = Player()
    _opponent = Player()
    
    # noinspection PyTypeChecker
    action_space = Discrete(len(list(Card)))
    # noinspection PyTypeChecker
    observation_space = MultiDiscrete([[0, 1], [0, 2]])  # Card x Guess

    def __init__(self, starting_money, opponent):
        self._opponent_agent = opponent
        self._start_new_round(starting_money, starting_money)
        opponent.set_env(self)

    def _start_new_round(self, player_money, opponent_money):
        self._passed: Dict[Player, bool] = {self._player: False, self._opponent: False}
        self._said: Dict[Player, Guess] = {self._player: Guess.AWAITING_FOR_GUESS,
                                           self._opponent: Guess.AWAITING_FOR_GUESS}
        self._card: Dict[Player, Card] = {self._player: random.choice(Card), self._opponent: random.choice(Card)}
        self._money = {self._player: player_money, self._opponent: opponent_money}
        self._current_money = {self._player: player_money, self._opponent: opponent_money}

    def _finish_round(self):
        player_reward, opponent_reward = self._get_round_rewards()
        player_money = self._money[self._player] + player_reward
        opponent_money = self._money[self._opponent] + opponent_reward
        self._start_new_round(player_money, opponent_money)
        return self._make_first_turn_in_round(player_reward, opponent_reward)

    def _get_round_rewards(self):
        player_correct = self._card[self._opponent] == self._said[self._player]
        opponent_correct = self._card[self._player] == self._said[self._opponent]
        bank = (self._money[self._opponent] - self._current_money[self._opponent]) + \
               (self._money[self._player] - self._current_money[self._player])
        if player_correct and opponent_correct:
            value = bank / 2
            player_reward = self._current_money[self._player] + value - self._money[self._player]
            opponent_reward = self._current_money[self._opponent] + value - self._money[self._opponent]
        elif player_correct and not opponent_correct:
            player_reward = self._current_money[self._player] + bank - self._money[self._player]
            opponent_reward = self._current_money[self._opponent] - self._money[self._opponent]
        elif not player_correct and opponent_correct:
            player_reward = self._current_money[self._player] - self._money[self._player]
            opponent_reward = self._current_money[self._opponent] + bank - self._money[self._opponent]
        else:
            player_reward, opponent_reward = 0.0, 0.0
        assert player_reward + opponent_reward == 0.0, (player_reward, opponent_reward)
        return player_reward, opponent_reward
    
    def _step(self, action: int):
        action = Card(action)
        self._process_action(self._player, action)

        if not self._passed[self._player] and not self._passed[self._opponent]:
            self._make_opponents_turn()
            return self._get_observation(self._player), 0, False, {}
        elif self._passed[self._player] and not self._passed[self._opponent]:
            self._make_opponents_turn()
            return self._finish_round()
        else:
            return self._finish_round()

    def _make_opponents_turn(self):
        opp_state = self._get_observation(self._opponent), 0, self._is_done(), {}
        self._opponent_agent.observe(opp_state)
        opp_action = self._opponent_agent.act()
        self._process_action(self._opponent, opp_action)

    def _get_observation(self, player: Player):
        opponent = self._player if player == self._opponent else self._opponent
        return self._card[player], self._said[opponent]

    def _process_action(self, player: Player, action: Card):
        if self._said[player] is None:
            self._said[player] = action
            self._current_money[player] -= 10
        elif self._said[player] != action:
            self._said[player] = Card(action)
            self._current_money[player] -= 10
        else:
            self._passed[player] = True

        if self._current_money[player] < 10:
            self._passed[player] = True

    def _is_done(self):
        return self._money[self._player] < 10 or self._money[self._opponent] < 10

    def _make_first_turn_in_round(self, player_reward, opponent_reward):
        if random.random() < 0.5:
            return self._get_observation(self._player), player_reward, self._is_done(), {}
        else:
            self._make_opponents_turn()
            return self._get_observation(self._player), opponent_reward, self._is_done(), {}

    def _reset(self):
        return self._make_first_turn_in_round(player_reward=0, opponent_reward=0)

    def _seed(self, seed=None):
        random.seed(seed)
