from casino import *


class BaselinePlayer(Player):
    def __init__(self, name):
        self._name = name
        self._my_card = None

    def make_first_bid(self) -> str:
        return random.choice([RED, BLACK])

    def make_response_bid(self, opponents_bid: Card) -> Card:
        return self.make_first_bid()

    def make_first_action(self, opponents_bid: Card) -> Action:
        return random.choice([PASS, CHANGE])

    def make_response_action(self, opponents_action: Action) -> Action:
        return random.choice([PASS, CHANGE])

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
        if self._my_card == RED:
            return BLACK
        else:
            return RED

    def make_first_action(self, opponents_bid: Card) -> Action:
        return PASS

    def deal(self, card: Card) -> None:
        self._my_card = card

    @property
    def name(self) -> str:
        return self._name

    def make_response_action(self, opponents_action: Action) -> Action:
        return PASS

    def make_response_bid(self, opponents_bid: Card) -> Card:
        return self.make_first_bid()

    def notify_about_last_action(self, opponents_action: Optional[Action]) -> None:
        pass

    def notify_about_value(self, value) -> None:
        pass


def main():
    p1 = SmarterBaseline("Misha")
    p2 = BaselinePlayer("Lara")
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
