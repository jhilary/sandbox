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

    def tell_result(self, value: int) -> None:
        self._my_card = None

    def deal(self, card: str) -> None:
        self._my_card = card

    @property
    def name(self) -> str:
        return self._name


def main():
    p1 = BaselinePlayer("Misha")
    p2 = BaselinePlayer("Lara")
    game = Game(p1, 100, p2, 100, rounds=1000)
    game.run()


if __name__ == "__main__":
    main()
