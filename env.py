import sys
import random
from io import StringIO
from enum import IntEnum
from typing import Dict

from gym import Env
from gym.spaces import Discrete, MultiDiscrete

import logging
logging.disable(logging.WARNING)


class FirstTurnInRound(IntEnum):
    NO = 0
    YES = 1


# order is important as we are comparing Guess to Card directly
class Guess(IntEnum):
    RED = 0
    BLACK = 1
    AWAITING_FOR_GUESS = 2


class Card(IntEnum):
    RED = 0
    BLACK = 1


class Player(IntEnum):
    PLAYER = 0
    OPPONENT = 1


def switch_card(value: int) -> int:
    if value == Card.RED:
        return Card.BLACK
    return Card.RED


class CardsGuessing(Env):
    _player = Player.PLAYER
    _opponent = Player.OPPONENT

    metadata = {'render.modes': ['human', 'ansi']}

    # noinspection PyTypeChecker
    action_space = Discrete(len(list(Card)))
    # noinspection PyTypeChecker
    observation_space = MultiDiscrete([[0, 1], [0, 1], [0, 2], [0, 2]])  # FirstTurnInRound x Card x Guess x Guess

    def __init__(self, starting_money, opponent):
        super(CardsGuessing, self).__init__()
        self._opponent_agent = opponent
        self._starting_money = starting_money
        self._start_new_round(starting_money, starting_money)
        self._wins = {self._player: 0, self._opponent: 0}
        opponent.set_env(self)

    def _start_new_round(self, player_money: int, opponent_money: int):
        self._passed: Dict[Player, bool] = {self._player: False, self._opponent: False}
        self._said: Dict[Player, Guess] = {self._player: Guess.AWAITING_FOR_GUESS,
                                           self._opponent: Guess.AWAITING_FOR_GUESS}
        player_card, opp_card = random.sample([Card.RED, Card.RED, Card.BLACK, Card.BLACK], 2)
        self._card: Dict[Player, Card] = {self._player: player_card, self._opponent: opp_card}
        self._money = {self._player: player_money, self._opponent: opponent_money}
        self._current_money = {self._player: player_money, self._opponent: opponent_money}

    def _finish_round(self):
        rewards = self._get_round_rewards()
        # print(f"--== Player's guess {self._said[self._player]} VS real {self._card[self._opponent]}")
        # print(f"--== Opps's guess {self._said[self._opponent]} VS real {self._card[self._player]}")
        # print(f"--== Player's reward {rewards[self._player]}, Opp's reward {rewards[self._opponent]} ==--\n")
        player_money = self._money[self._player] + rewards[self._player]
        opponent_money = self._money[self._opponent] + rewards[self._opponent]
        if player_money < 10:
            self._wins[self._opponent] += 1
        if opponent_money < 10:
            self._wins[self._player] += 1
        previous_cards = {self._player: Guess(self._card[self._opponent]),
                          self._opponent: Guess(self._card[self._player])}
        self._start_new_round(player_money, opponent_money)
        return self._make_first_turn_in_round(rewards, previous_cards)

    def _get_round_rewards(self) -> Dict[Player, int]:
        player_correct = self._card[self._opponent] == self._said[self._player]
        opponent_correct = self._card[self._player] == self._said[self._opponent]

        player_spent = self._money[self._player] - self._current_money[self._player]
        opponent_spent = self._money[self._opponent] - self._current_money[self._opponent]
        bank = player_spent + opponent_spent

        if player_correct and opponent_correct:
            value = bank / 2
            p_value = value
            o_value = value
        elif player_correct and not opponent_correct:
            p_value = bank
            o_value = 0.0
        elif not player_correct and opponent_correct:
            p_value = 0.0
            o_value = bank
        else:
            p_value = player_spent
            o_value = opponent_spent
        player_reward = p_value - player_spent
        opponent_reward = o_value - opponent_spent
        assert player_reward + opponent_reward == 0.0, (player_reward, opponent_reward)
        return {self._player: player_reward, self._opponent: opponent_reward}

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

    def _make_opponents_turn(self, reward: float, first_turn: bool, done: bool, previous_cards=None):
        opp_state = self._get_observation(self._opponent, first_turn, previous_cards), reward, done, {}
        self._opponent_agent.observe(*opp_state)
        opp_action = Card(self._opponent_agent.act())
        self._process_action(self._opponent, opp_action)

    def _get_observation(self, player: Player, first_turn=False, previous_cards=None):
        if previous_cards is None:
            previous_cards = {self._player: Guess.AWAITING_FOR_GUESS, self._opponent: Guess.AWAITING_FOR_GUESS}
        opponent = self._get_other_player(player)
        return FirstTurnInRound(int(first_turn)), self._card[player], self._said[opponent], previous_cards[player]

    def _get_other_player(self, player):
        return self._player if player == self._opponent else self._opponent

    def _process_action(self, player: Player, action: Card):
        guess = Guess.RED if action == Card.RED else Guess.BLACK
        if self._said[player] == Guess.AWAITING_FOR_GUESS:
            self._said[player] = guess
            self._current_money[player] -= 10.0
        elif self._said[player] != guess:
            self._said[player] = guess
            self._current_money[player] -= 10.0
        else:
            self._passed[player] = True

        if self._current_money[player] < 10 or self._passed[self._get_other_player(player)]:
            self._passed[player] = True

    def _is_done(self):
        done = self._money[self._player] < 10 or self._money[self._opponent] < 10
        return done

    def _make_first_turn_in_round(self, rewards, prev_cards):
        player_reward = rewards[self._player]
        opponent_reward = rewards[self._opponent]
        done = self._is_done()
        if done:
            assert Guess.AWAITING_FOR_GUESS not in prev_cards.values(), prev_cards
            opp_obs = self._get_observation(self._opponent, first_turn=True, previous_cards=prev_cards)
            opp_state = opp_obs, opponent_reward, True, {}
            self._opponent_agent.observe(*opp_state)
            player_obs = self._get_observation(self._player, first_turn=True, previous_cards=prev_cards)
            return player_obs, player_reward, True, {}
        else:
            assert self._money[self._player] >= 0
            assert self._money[self._opponent] >= 0
            if random.random() < 0.5:
                player_obs = self._get_observation(self._player, first_turn=True, previous_cards=prev_cards)
                return player_obs, player_reward, False, {}
            else:
                self._make_opponents_turn(opponent_reward, first_turn=True, done=done, previous_cards=prev_cards)
                player_obs = self._get_observation(self._player, first_turn=True, previous_cards=prev_cards)
                return player_obs, player_reward, False, {}

    def _reset(self):
        self._start_new_round(self._starting_money, self._starting_money)
        rewards = {self._player: 0, self._opponent: 0}
        previous_cards = {self._player: Guess.AWAITING_FOR_GUESS, self._opponent: Guess.AWAITING_FOR_GUESS}
        return self._make_first_turn_in_round(rewards, previous_cards)

    def _render(self, mode='human', close=False):
        if close:
            return
        # state = {
        #     "names": ("Player", "Computer"),
        #     "wins": (0, 0),
        #     "rewards": (10, 00),
        #     "money": (100, 100),
        #     "bank": 0,
        #     "end": False,
        #     "steps": [({"type": "card", "card": "R", "money": 100}, {"type": "card", "card": "B", "money": 90})]
        # }

        outfile = StringIO() if mode == 'ansi' else sys.stdout
#         outfile.write(
# """
#  {:s}
# |{:24s}Score{:24s}|
# |{:2s}{:>10s}{:10s}{:4d}:{:<4d}{:10s}{:10s}{:2s}|
# |{:53s}|
# |{:24s}Money{:24s}|
# |{:22s}{:4d}:{:<4d}{:22s}|
# |{:53s}|
# |{:23s}Bank: {:4<d}{:23s}|
# \n
# """
#                 .format("_"*53,
#                         "","",
#                         "", state["names"][0], "", state["wins"][0], state["wins"][1], "", state["names"][1], "",
#                         "",
#                         "","",
#                         "", state["money"][0], state["money"][1], "",
#                         "",
#                         "", state["bank"], ""))


        outfile.write(
            f"""
            Player's wins: {self._wins[self._player]}, Opp's wins: {self._wins[self._opponent]}
            Player's card: {self._card[self._player].name}, Opp's card: {self._card[self._opponent].name}
            Player's money: {self._money[self._player]}, Opp's money: {self._money[self._opponent]}
            Player's guess: {self._said[self._player].name}, Opp's guess: {self._said[self._opponent].name},
            Player's current money: {self._current_money[self._player]}, Opp's current money: {self._current_money[self._opponent]}
            Player passed: {self._passed[self._player]}, Opp passed: {self._passed[self._opponent]}
            \n"""
        )
        return outfile


    def _seed(self, seed=None):
        random.seed(seed)
