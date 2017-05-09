import random
from typing import Dict

from casino import Player, Card, Game
from utils import Inteleaving
from ilariia import B1V1


class BaselinePlayer(Player):
    def __init__(self, name):
        self._name = name
        self._my_card = None

    def say_card(self) -> Card:
        return random.choice([Card.RED, Card.BLACK])

    def opponent_said_card(self, opponents_bid: Card) -> None:
        return None

    def would_change_card(self) -> bool:
        return random.choice([True, False])

    def opponent_changed_card(self) -> None:
        pass

    def win(self, value):
        pass

    def end_round(self):
        pass

    def take_card(self, card: Card) -> None:
        self._my_card = card

    def opponent_card(self, card: Card) -> None:
        pass

    @property
    def name(self) -> str:
        return self._name


class SmarterBaseline(Player):
    def __init__(self, name):
        self._name = name
        self._my_card = None
        self._opponent_card = None

    @property
    def name(self) -> str:
        return self._name

    def take_card(self, card: Card) -> None:
        self._my_card = card

    def say_card(self) -> Card:
        if self._my_card == Card.RED:
            return Card.BLACK
        else:
            return Card.RED

    def opponent_said_card(self, opponents_bid: Card) -> None:
        self._opponent_card = opponents_bid

    def would_change_card(self) -> bool:
        return False

    def opponent_changed_card(self) -> None:
        self._opponent_card = Card.BLACK if self._opponent_card == Card.RED else Card.RED

    def win(self, value: int) -> None:
        pass

    def opponent_card(self, card: Card) -> None:
        pass

    def end_round(self) -> None:
        pass


def main():
    p11 = SmarterBaseline("Misha-smarter")
    p12 = BaselinePlayer("Misha-base")
    p1 = Inteleaving("Misha", p11, p12)
    p2 = B1V1()
    winners: Dict[Player, int] = {p1: 0, p2: 0}
    games = 100
    for i in range(games):
        game = Game(p1, 100, p2, 100, rounds=1000)
        winner = game.run()
        if winner is not None:
            winners[winner] += 1
    print("After %s games player %s won %s times and player %s won %s times" % (games,
                                                                                p1.name, winners[p1],
                                                                                p2.name, winners[p2]))


if __name__ == "__main__":
    main()
