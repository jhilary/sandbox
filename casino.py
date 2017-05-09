import random
from collections import namedtuple
from abc import ABCMeta, abstractmethod
from typing import Dict, Optional

Card = namedtuple("Card", "color")
RED = Card("RED")
BLACK = Card("BLACK")

Action = namedtuple("Action", "name")
PASS = Action("PASS")
CHANGE = Action("CHANGE")


class Player(object):
    __metaclass__ = ABCMeta

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def deal(self, card: str) -> None:
        raise NotImplementedError()

    @abstractmethod
    def tell_result(self, value: int) -> None:
        raise NotImplementedError()

    @abstractmethod
    def make_first_bid(self) -> Card:
        raise NotImplementedError()

    @abstractmethod
    def make_response_bid(self, opponents_bid: Card) -> Card:
        raise NotImplementedError()

    @abstractmethod
    def make_first_action(self, opponents_bid: Card) -> Action:
        raise NotImplementedError()

    @abstractmethod
    def make_response_action(self, opponents_action: Action) -> Action:
        raise NotImplementedError()

    @abstractmethod
    def notify_about_last_action(self, opponents_action: Optional[Action]) -> None:
        raise NotImplementedError()

    @abstractmethod
    def notify_about_value(self, value) -> None:
        raise NotImplementedError()


class GameRound(object):
    CARDS = [RED, RED, BLACK, BLACK]

    def __init__(self, player1: Player, money1: int, player2: Player, money2: int):
        assert money1 >= 10, money1
        assert money2 >= 10, money2
        self.player1 = player1
        self.player2 = player2
        self.starting_money = {player1: money1, player2: money2}
        self.current_money = {player1: money1, player2: money2}
        self.bank: int = 0
        self.last_action: Action = None

        card1, card2 = random.sample(self.CARDS, 2)
        self.cards: Dict[Player, Card] = {self.player1: card1, self.player2: card2}
        self.player1.deal(card1)
        print("Player %s got card %s" % (self.player1.name, card1.color))
        self.player2.deal(card2)
        print("Player %s got card %s" % (self.player2.name, card2.color))

        self.bank += 20
        self.current_money[self.player1] -= 10
        self.current_money[self.player2] -= 10
        self.bids: Dict[Player, Card] = {self.player1: self.player1.make_first_bid()}
        self.bids[self.player2] = self.player1.make_response_bid(self.bids[self.player1])

        print("Player %s made first bid %s. Its money: %s. Bank: %s" % (self.player1.name, self.bids[player1].color,
                                                                        self.current_money[player1],
                                                                        self.bank))
        print("Player %s made first bid %s. Its money: %s. Bank: %s" % (self.player2.name, self.bids[player2].color,
                                                                        self.current_money[player2],
                                                                        self.bank))

    def play(self) -> (int, int):
        value1, value2 = self._run_game(self.player1, self.player2)
        self.player1.tell_result(value1)
        self.player2.tell_result(value2)
        return value1, value2

    def _run_game(self, player1: Player, player2: Player):
        action = self._make_action(player1, player2)
        if action == PASS:
            self._make_action(player2, player1)
            player1.notify_about_last_action(self.last_action)
            player2.notify_about_last_action(None)
            p1_value, p2_value = self._resolve()
            self.player1.notify_about_value(p1_value)
            self.player1.notify_about_value(p2_value)
            return p1_value, p2_value
        else:
            return self._run_game(player2, player1)

    def _make_action(self, player: Player, opponent: Player) -> Action:
        if self.current_money[player] < 10:
            self.last_action = PASS
        else:
            if self.last_action is None:
                self.last_action = player.make_first_action(self.bids[opponent])
            else:
                self.last_action = player.make_response_action(self.last_action)
            if self.last_action == CHANGE:
                self.current_money[player] -= 10
                self.bank += 10
                self.bids[player] = RED if self.bids[player] == BLACK else BLACK
        print("Player %s made action %s. Its bid now %s. Its money: %s. Bank: %s" % (player.name,
                                                                                     self.last_action.name,
                                                                                     self.bids[player].color,
                                                                                     self.current_money[player],
                                                                                     self.bank))
        return self.last_action

    def _resolve(self) -> (int, int):
        p1_correct = self.bids[self.player1] == self.cards[self.player1]
        p2_correct = self.bids[self.player2] == self.cards[self.player2]
        print("%s had %s and %s had %s" % (self.player1.name, self.bids[self.player1].color,
                                           self.player2.name, self.bids[self.player2].color))
        if p1_correct and p2_correct:
            value = self.bank / 2
            p1_value = self.current_money[self.player1] + value - self.starting_money[self.player1]
            p2_value = self.current_money[self.player2] + value - self.starting_money[self.player2]
            assert p1_value + p2_value == 0, (p1_value, p2_value)
            print("Both player guessed right")
        elif p1_correct and not p2_correct:
            print("Player %s guessed right and player %s guessed wrong" % (self.player1.name, self.player2.name))
            p1_value, p2_value = self.bank / 2, -self.bank / 2
        elif not p1_correct and p2_correct:
            print("Player %s guessed right and player %s guessed wrong" % (self.player2.name, self.player2.name))
            p1_value, p2_value = -self.bank / 2, self.bank / 2
        else:
            print("Both player guessed wrong")
            p1_value, p2_value = 0, 0
        return p1_value, p2_value


class Game(object):
    def __init__(self, player1: Player, money1: int, player2: Player, money2: int, rounds: int):
        self.player1 = player1
        self.player2 = player2
        self.current_money = {player1: money1, player2: money2}
        self.rounds = rounds

    def run(self):
        for i in range(self.rounds):
            if i % 2 == 0:
                first_player, second_player = self.player1, self.player2
            else:
                first_player, second_player = self.player2, self.player1
            print("Before round %s player %s have %s and player %s have %s" % (i + 1,
                                                                               self.player1.name,
                                                                               self.current_money[self.player1],
                                                                               self.player2.name,
                                                                               self.current_money[self.player2]))
            gameround = GameRound(first_player, self.current_money[first_player],
                                  second_player, self.current_money[second_player])
            value1, value2 = gameround.play()
            print("Player %s won %s and player %s won %s" % (first_player.name, value1, second_player.name, value2))
            self.current_money[first_player] += value1
            assert self.current_money[first_player] >= 0
            self.current_money[second_player] += value2
            assert self.current_money[second_player] >= 0
            print("After %s rounds %s got %s and %s got %s" % (i + 1,
                                                               self.player1.name,
                                                               self.current_money[self.player1],
                                                               self.player2.name,
                                                               self.current_money[self.player2]))
            if self.current_money[self.player1] < 10:
                print("Player %s run out of money AND TOTALLY LOST" % self.player1.name)
                break
            if self.current_money[self.player2] < 10:
                print("Player %s run out of money AND TOTALLY LOST" % self.player2.name)
                break
