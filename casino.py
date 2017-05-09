import random
from abc import ABCMeta, abstractmethod
from typing import Dict
from enum import Enum


class Card(Enum):
    RED = "RED"
    BLACK = "BLACK"


class Action(Enum):
    PASS = "PASS"
    CHANGE = "CHANGE"


class Player(object):
    __metaclass__ = ABCMeta

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def take_card(self, card: Card) -> None:
        raise NotImplementedError()

    @abstractmethod
    def say_card(self) -> Card:
        raise NotImplementedError()

    @abstractmethod
    def opponent_said_card(self, card: Card) -> None:
        raise NotImplementedError()

    @abstractmethod
    def would_change_card(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def opponent_changed_card(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    def end_round(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    def opponent_card(self, card) -> None:
        raise NotImplementedError()

    @abstractmethod
    def win(self, value) -> None:
        raise NotImplementedError()


class GameRound(object):
    CARDS = [Card.RED, Card.RED, Card.BLACK, Card.BLACK]

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
        self.player1.take_card(card1)
        print("%s got card %s" % (self.player1.name, card1.name))
        self.player2.take_card(card2)
        print("%s got card %s" % (self.player2.name, card2.name))

        self.bank += 20
        self.current_money[self.player1] -= 10
        self.current_money[self.player2] -= 10
        self.bids: Dict[Player, Card] = {}

        self.bids[self.player1] = self.player1.say_card()
        self.player2.opponent_said_card(self.bids[self.player1])
        self.bids[self.player2] = self.player2.say_card()
        self.player1.opponent_said_card(self.bids[self.player2])

        print("%s made first bid %s. Its money: %s. Bank: %s" % (self.player1.name, self.bids[player1].name,
                                                                        self.current_money[player1],
                                                                        self.bank))
        print("%s made first bid %s. Its money: %s. Bank: %s" % (self.player2.name, self.bids[player2].name,
                                                                        self.current_money[player2],
                                                                        self.bank))

    def play(self) -> (int, int):
        value1, value2 = self._run_game(self.player1, self.player2)
        return value1, value2

    def _run_game(self, player1: Player, player2: Player):
        action = self._make_action(player1, player2)

        if action == Action.PASS:
            self._make_action(player2, player1)
            p1_value, p2_value = self._resolve()

            player1.opponent_card(self.cards[player2])
            player2.opponent_card(self.cards[player1])

            player1.win(p1_value)
            player2.win(p2_value)

            player1.end_round()
            player2.end_round()

            return p1_value, p2_value
        else:
            return self._run_game(player2, player1)

    def _make_action(self, player: Player, opponent: Player) -> Action:
        if self.current_money[player] < 10:
            player_action = Action.PASS
        else:
            player_action = Action.CHANGE if player.would_change_card() else Action.PASS
            if player_action == Action.CHANGE:
                opponent.opponent_changed_card()
                self.current_money[player] -= 10
                self.bank += 10
                self.bids[player] = Card.RED if self.bids[player] == Card.BLACK else Card.BLACK

        print("%s made action %s. Its bid now %s. Its money: %s. Bank: %s" % (player.name,
                                                                                     player_action.name,
                                                                                     self.bids[player].name,
                                                                                     self.current_money[player],
                                                                                     self.bank))
        return player_action

    def _resolve(self) -> (int, int):
        p1_correct = self.bids[self.player1] == self.cards[self.player2]
        p2_correct = self.bids[self.player2] == self.cards[self.player1]
        print("%s had %s and %s had %s" % (self.player1.name, self.cards[self.player1].name,
                                           self.player2.name, self.cards[self.player2].name))
        if p1_correct and p2_correct:
            value = self.bank / 2
            p1_value = self.current_money[self.player1] + value - self.starting_money[self.player1]
            p2_value = self.current_money[self.player2] + value - self.starting_money[self.player2]
            assert p1_value + p2_value == 0, (p1_value, p2_value)
            print("Both player guessed right")
        elif p1_correct and not p2_correct:
            print("%s guessed right and %s guessed wrong" % (self.player1.name, self.player2.name))
            p1_value = self.current_money[self.player1] + self.bank - self.starting_money[self.player1]
            p2_value = self.current_money[self.player2] - self.starting_money[self.player2]
        elif not p1_correct and p2_correct:
            print("%s guessed right and %s guessed wrong" % (self.player2.name, self.player1.name))
            p1_value = self.current_money[self.player1] - self.starting_money[self.player1]
            p2_value = self.current_money[self.player2] + self.bank - self.starting_money[self.player2]
        else:
            print("Both player guessed wrong")
            p1_value, p2_value = 0, 0
        assert p1_value + p2_value == 0, (p1_value, p2_value)
        return p1_value, p2_value


class Game(object):
    def __init__(self, player1: Player, money1: int, player2: Player, money2: int, rounds: int):
        self.player1 = player1
        self.player2 = player2
        self.current_money = {player1: money1, player2: money2}
        self.rounds = rounds

    def run(self) -> Player:
        for i in range(self.rounds):
            print("Round %s\n" %i)
            if i % 2 == 0:
                first_player, second_player = self.player1, self.player2
            else:
                first_player, second_player = self.player2, self.player1
            print("Before round %s %s have %s and %s have %s" % (i + 1,
                                                                               self.player1.name,
                                                                               self.current_money[self.player1],
                                                                               self.player2.name,
                                                                               self.current_money[self.player2]))
            gameround = GameRound(first_player, self.current_money[first_player],
                                  second_player, self.current_money[second_player])
            value1, value2 = gameround.play()
            print("%s won %s and %s won %s" % (first_player.name, value1, second_player.name, value2))
            self.current_money[first_player] += value1
            assert self.current_money[first_player] >= 0
            self.current_money[second_player] += value2
            assert self.current_money[second_player] >= 0
            print("After %s rounds %s got %s and %s got %s\n" % (i + 1,
                                                               self.player1.name,
                                                               self.current_money[self.player1],
                                                               self.player2.name,
                                                               self.current_money[self.player2]))
            if self.current_money[self.player1] < 10:
                print("Game result:\n")
                print("After %s rounds player %s run out of money AND TOTALLY LOST\n" % (i + 1, self.player1.name))
                return self.player2
            if self.current_money[self.player2] < 10:
                print("Game result:\n")
                print("After %s rounds player %s run out of money AND TOTALLY LOST\n" % (i + 1, self.player2.name))
                return self.player1
