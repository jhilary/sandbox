from casino import Player, Card


class MishaBotV1(Player):
    def __init__(self, apriori=10):
        self._my_card: Card = None
        self._op_card: Card = None
        self._number_of_rounds = apriori * 4
        self.counters = {(Card.RED, Card.RED): apriori,
                         (Card.RED, Card.BLACK): apriori,
                         (Card.BLACK, Card.RED): apriori,
                         (Card.BLACK, Card.BLACK): apriori}

    def win(self, value) -> None:
        pass

    def opponent_card(self, card) -> None:
        self.counters[(self._my_card, card)] += 1

    def would_change_card(self) -> bool:
        return False

    def say_card(self) -> Card:
        inverted = self._invert_card(self._my_card)
        prob1 = self.counters[(self._my_card, self._my_card)] / self._number_of_rounds
        prob2 = self.counters[(self._my_card, inverted)] / self._number_of_rounds
        if prob1 >= prob2:
            return self._my_card
        else:
            return inverted

    def take_card(self, card: Card) -> None:
        self._my_card = card

    @property
    def name(self) -> str:
        return self.__class__.__name__

    def end_round(self) -> None:
        self._number_of_rounds += 1

    def opponent_changed_card(self) -> None:
        self._op_card = self._invert_card(self._op_card)

    def opponent_said_card(self, card: Card) -> None:
        pass

    @staticmethod
    def _invert_card(card: Card):
        if card == Card.RED:
            return Card.BLACK
        else:
            return Card.RED
