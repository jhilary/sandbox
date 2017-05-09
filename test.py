import random
from typing import Optional

from casino import Player, Card, Action, Game


class BaselinePlayer(Player):
    def __init__(self, name):
        self._name = name
        self._my_card = None

    def make_first_bid(self) -> Card:
        return random.choice([Card.RED, Card.BLACK])

    def make_response_bid(self, opponents_bid: Card) -> Card:
        return self.make_first_bid()

    def make_first_action(self, opponents_bid: Card) -> Action:
        return random.choice([Action.PASS, Action.CHANGE])

    def make_response_action(self, opponents_action: Action) -> Action:
        return random.choice([Action.PASS, Action.CHANGE])

    def notify_about_last_action(self, opponents_action: Optional[Action]):
        pass

    def notify_about_value(self, value):
        pass

    def deal(self, card: Card) -> None:
        self._my_card = card

    @property
    def name(self) -> str:
        return self._name


class SmarterBaseline(Player):
    def __init__(self, name):
        self._name = name
        self._my_card = None

    def make_first_bid(self) -> Card:
        if self._my_card == Card.RED:
            return Card.BLACK
        else:
            return Card.RED

    def make_first_action(self, opponents_bid: Card) -> Action:
        return Action.PASS

    def deal(self, card: Card) -> None:
        self._my_card = card

    @property
    def name(self) -> str:
        return self._name

    def make_response_action(self, opponents_action: Action) -> Action:
        return Action.PASS

    def make_response_bid(self, opponents_bid: Card) -> Card:
        return self.make_first_bid()

    def notify_about_last_action(self, opponents_action: Optional[Action]) -> None:
        pass

    def notify_about_value(self, value) -> None:
        pass


def main():
    p1 = SmarterBaseline("Misha")
    p2 = BaselinePlayer("Lara")
    game = Game(p1, 100, p2, 100, rounds=1000)
    game.run()


if __name__ == "__main__":
    main()
