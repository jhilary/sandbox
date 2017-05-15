import random
from enum import IntEnum
from typing import Dict

from gym import Env
from gym.spaces import Discrete, MultiDiscrete


class FirstTurnInRound(IntEnum):
    NO = 0
    YES = 1


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

    metadata = {'render.modes': ['human']}
    
    # noinspection PyTypeChecker
    action_space = Discrete(len(list(Card)))
    # noinspection PyTypeChecker
    observation_space = MultiDiscrete([[0, 1], [0, 1], [0, 2]])  # FirstTurnInRound x Card x Guess

    def __init__(self, starting_money, opponent):
        self._opponent_agent = opponent
        self._starting_money = starting_money
        self._start_new_round(starting_money, starting_money)
        self._wins = {self._player: 0, self._opponent: 0}
        opponent.set_env(self)

    def _start_new_round(self, player_money: int, opponent_money: int):
        self._passed: Dict[Player, bool] = {self._player: False, self._opponent: False}
        self._said: Dict[Player, Guess] = {self._player: Guess.AWAITING_FOR_GUESS,
                                           self._opponent: Guess.AWAITING_FOR_GUESS}
        # noinspection PyTypeChecker
        self._card: Dict[Player, Card] = {self._player: random.choice(list(Card)),
                                          self._opponent: random.choice(list(Card))}
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

        player_spent = self._money[self._player] - self._current_money[self._player]
        opponent_spent = self._money[self._opponent] - self._current_money[self._opponent]
        bank = player_spent + opponent_spent

        if player_correct and opponent_correct:
            value = bank / 2
            p_value = value
            o_value = value
            self._wins[self._player] += 1
            self._wins[self._opponent] += 1
        elif player_correct and not opponent_correct:
            p_value = bank
            o_value = 0.0
            self._wins[self._player] += 1
        elif not player_correct and opponent_correct:
            p_value = 0.0
            o_value = bank
            self._wins[self._opponent] += 1
        else:
            p_value = player_spent
            o_value = opponent_spent
        player_reward = p_value - player_spent
        opponent_reward = o_value - opponent_spent
        assert player_reward + opponent_reward == 0.0, (player_reward, opponent_reward)
        return player_reward, opponent_reward
    
    def _step(self, action: int):
        assert not self._is_done()
        action = Card(action)
        self._process_action(self._player, action)

        if not self._passed[self._player] and not self._passed[self._opponent]:
            self._make_opponents_turn(reward=0.0, first_turn=False, done=False)
            return self._get_observation(self._player), 0.0, False, {}
        elif not self._passed[self._player] and self._passed[self._opponent]:
            return self._get_observation(self._player), 0.0, False, {}
        elif self._passed[self._player] and not self._passed[self._opponent]:
            self._make_opponents_turn(reward=0.0, first_turn=False, done=False)
            return self._finish_round()
        else:
            return self._finish_round()

    def _make_opponents_turn(self, reward: float, first_turn: bool, done: bool):
        opp_state = self._get_observation(self._opponent, first_turn), reward, done, {}
        self._opponent_agent.observe(*opp_state)
        opp_action = Card(self._opponent_agent.act())
        self._process_action(self._opponent, opp_action)

    def _get_observation(self, player: Player, first_turn=False):
        opponent = self._get_other_player(player)
        return FirstTurnInRound(int(first_turn)), self._card[player], self._said[opponent]

    def _get_other_player(self, player):
        return self._player if player == self._opponent else self._opponent

    def _process_action(self, player: Player, action: Card):
        if self._said[player] == Guess.AWAITING_FOR_GUESS and self._current_money[player] >= 10:
            self._said[player] = action
            self._current_money[player] -= 10.0
        elif self._said[player] != action:
            self._said[player] = action
            self._current_money[player] -= 10.0
        else:
            self._passed[player] = True

        if self._current_money[player] < 10 or self._passed[self._get_other_player(player)]:
            self._passed[player] = True

    def _is_done(self):
        done = self._money[self._player] < 10 or self._money[self._opponent] < 10
        return done

    def _make_first_turn_in_round(self, player_reward, opponent_reward):
        done = self._is_done()
        if done:
            opp_state = self._get_observation(self._opponent, first_turn=True), opponent_reward, True, {}
            self._opponent_agent.observe(*opp_state)
            return self._get_observation(self._player, first_turn=True), player_reward, True, {}
        else:
            assert self._money[self._player] >= 0
            assert self._money[self._opponent] >= 0
            if random.random() < 0.5:
                return self._get_observation(self._player, first_turn=True), player_reward, False, {}
            else:
                self._make_opponents_turn(opponent_reward, first_turn=True, done=done)
                return self._get_observation(self._player, first_turn=True), player_reward, False, {}

    def _reset(self):
        self._start_new_round(self._starting_money, self._starting_money)
        return self._make_first_turn_in_round(player_reward=0.0, opponent_reward=0.0)

    def _render(self, mode='human', close=False):
        print(f"""Player's wins: {self._wins[self._player]}, Opp's wins: {self._wins[self._opponent]}
Player's card: {self._card[self._player].name}, Opp's card: {self._card[self._opponent].name}
Player's money: {self._money[self._player]}, Opp's money: {self._money[self._opponent]}
Player's guess: {self._said[self._player].name}, Opp's guess: {self._said[self._opponent].name},
Player's current money: {self._current_money[self._player]}, Opp's current money: {self._current_money[self._opponent]}
Player passed: {self._passed[self._player]}, Opp passed: {self._passed[self._opponent]}
""")

    def _seed(self, seed=None):
        random.seed(seed)
