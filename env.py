import sys
import random
from itertools import zip_longest
from io import StringIO
from enum import IntEnum
from typing import Dict, List
import logging

from gym import Env
from gym.spaces import Discrete, MultiDiscrete

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


# return {
#     "names": ("Player", "Opponent"),
#     "cards": (None, None) if not finished else (real_cards[cls._player], real_cards[cls._opponent]),
#     "wins": (wins[cls._player], wins[cls._opponent]),
#     "rewards": rewards,
#     "money": (current_money[cls._player], current_money[cls._opponent]),
#     "bank": bank,
#     "end": finished,
#     "steps": steps
# }


class CardsGuessing(Env):
    _player = Player.PLAYER
    _opponent = Player.OPPONENT
    _all_players = [_player, _opponent]

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
        self._wins = {p: 0 for p in self._all_players}
        self._steps: Dict[Player, List[Card]] = []
        opponent.set_env(self)

    def _start_new_round(self, player_money: int, opponent_money: int):
        player_card, opp_card = random.sample([Card.RED, Card.RED, Card.BLACK, Card.BLACK], 2)
        self._card: Dict[Player, Card] = {self._player: player_card, self._opponent: opp_card}
        self._money = {self._player: player_money, self._opponent: opponent_money}
        self._steps = {p: [] for p in self._all_players}
        self._starting_player: Player = random.choice(self._all_players)

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
        current_money = self._current_money
        player_spent = self._money[self._player] - current_money[self._player]
        opponent_spent = self._money[self._opponent] - current_money[self._opponent]
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

    @staticmethod
    def _money_spent(steps) -> int:
        return 10 * sum(s1 == s2 for s1, s2 in zip_longest(steps, steps[1:]))

    @property
    def _current_money(self) -> Dict[Player, int]:
        spent = {p: self._money_spent(self._steps[p]) for p in self._all_players}
        return {p: self._money[p] - spent[p] for p in self._all_players}

    @staticmethod
    def _current_guess(steps) -> Guess:
        return Guess(steps[-1]) if len(steps) > 0 else Guess.AWAITING_FOR_GUESS

    @property
    def _said(self) -> Dict[Player, Guess]:
        return {p: self._current_guess(self._steps[p]) for p in self._all_players}

    def _step(self, action: int):
        assert not self._is_done()
        action = Card(action)
        self._steps[self._player].append(action)

        passed = self._passed

        if not passed[self._player] and not passed[self._opponent]:
            self._make_opponents_turn(reward=0.0, first_turn=False, done=False)
            return self._get_observation(self._player), 0.0, False, {}
        elif not passed[self._player] and passed[self._opponent]:
            return self._get_observation(self._player), 0.0, False, {}
        elif passed[self._player] and not passed[self._opponent]:
            self._make_opponents_turn(reward=0.0, first_turn=False, done=False)
            return self._finish_round()
        else:
            return self._finish_round()

    def _make_opponents_turn(self, reward: float, first_turn: bool, done: bool, previous_cards=None):
        opp_state = self._get_observation(self._opponent, first_turn, previous_cards), reward, done, {}
        self._opponent_agent.observe(*opp_state)
        opp_action = Card(self._opponent_agent.act())
        self._steps[self._opponent].append(opp_action)

    def _get_observation(self, player: Player, first_turn=False, previous_cards=None):
        if previous_cards is None:
            previous_cards = {p: Guess.AWAITING_FOR_GUESS for p in self._all_players}
        opponent = self._get_other_player(player)
        return FirstTurnInRound(int(first_turn)), self._card[player], self._said[opponent], previous_cards[player]

    def _get_other_player(self, player):
        return self._player if player == self._opponent else self._opponent

    @property
    def _passed(self) -> Dict[Player, bool]:
        passed = {self._player: False, self._opponent: False}
        current_money = self._current_money
        for p in self._all_players:
            if current_money[p] < 10:
                passed[p] = True

            if len(self._steps[p]) >= 2 and self._steps[p][-1] == self._steps[p][-2]:
                passed[p] = True

        passed_due_to_other = {p: passed[o] and len(self._steps[p]) == len(self._steps[o]) for p, o
                               in ((p, self._get_other_player(p)) for p in self._all_players)}

        return {p: passed[p] or passed_due_to_other[p] for p in self._all_players}

    def _is_done(self):
        return any(self._money[p] < 10 for p in self._all_players)

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
            if self._starting_player == self._player:
                player_obs = self._get_observation(self._player, first_turn=True, previous_cards=prev_cards)
                return player_obs, player_reward, False, {}
            else:
                self._make_opponents_turn(opponent_reward, first_turn=True, done=done, previous_cards=prev_cards)
                player_obs = self._get_observation(self._player, first_turn=True, previous_cards=prev_cards)
                return player_obs, player_reward, False, {}

    def _reset(self):
        self._start_new_round(self._starting_money, self._starting_money)
        rewards = {p: 0 for p in self._all_players}
        previous_cards = {p: Guess.AWAITING_FOR_GUESS for p in self._all_players}
        return self._make_first_turn_in_round(rewards, previous_cards)

    def _render(self, mode='human', close=False):
        if close:
            return

        outfile = StringIO() if mode == 'ansi' else sys.stdout

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
        # return {
        #     "names": ("Player", "Opponent"),
        #     "wins": (0, 0),
        #     "rewards": (0, 0),
        #     "money": (100, 100),
        #     "bank": 0,
        #     "end": False,
        #     "steps": [({"type": "wait | pass | card", "card": None, "money": 100},
        #                {"type": "card", "card": "RED", "money": 90})]
        # }

    def _seed(self, seed=None):
        random.seed(seed)
