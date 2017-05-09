import random
from storage import Storage, StorageRow, list_sequence
from casino import Player, Card
from collections import defaultdict


class IlariiaPlayer(Player):
    def __init__(self):
        self.storage = Storage()
        self.my = []
        self.opponent = []
        self.my_card = None
        self.op_card = None
        self.value = 0

    def reset(self):
        self.storage.save(StorageRow(
            self.my,
            self.opponent,
            self.my_card,
            self.op_card,
            self.value
        ))
        self.my_card = None
        self.op_card = None
        self.my = []
        self.opponent = []
        self.value = 0

    def __repr__(self):
        return "(State)\nMy card: %s;\nOpponent card: %s;\n" \
               "My turns: %s;\nOpponent turns: %s;\n" \
               "Value: %s\n" % \
               (self.my_card.name if self.my_card else self.my_card,
                self.op_card.name if self.op_card else self.op_card,
                ", ".join(card.name for card in self.my),
                ", ".join(card.name for card in self.opponent),
                self.value)

    def take_card(self, card: Card) -> None:
        self.my_card = card

    def win(self, value) -> None:
        self.value = value

    def end_round(self):
        self.reset()

    def say_card(self) -> Card:
        new_card = self._make_decision()
        self.my.append(new_card)
        return new_card

    def opponent_said_card(self, card: Card) -> None:
        if not self.my:
            self.my.append(None)
        self.opponent.append(card)

    def would_change_card(self) -> bool:
        card = self._make_decision()
        self.my.append(card)
        if card != self.my[-1]:
            return True
        else:
            return False

    def opponent_card(self, card: Card) -> None:
        self.op_card = card

    def _change_card(self, old_card):
        if old_card == Card.BLACK:
            return Card.RED
        else:
            return Card.BLACK

    def opponent_change_card(self, is_changed: bool) -> None:
        if is_changed:
            self.opponent_said_card(self._change_card(self.opponent[-1]))
        else:
            self.opponent_said_card(self.opponent[-1])

    def _make_decision(self) -> Card:
        raise NotImplementedError()


class B1V1(IlariiaPlayer):

    @property
    def name(self) -> str:
        return "IlariiaB1V1"

    def _make_decision(self) -> Card:
        if self.opponent:
            if len(self.opponent) > 1:
                if self.opponent[-1] == self.opponent[-2]:
                    return self.my[-1]

            if self.opponent[-1] == Card.BLACK:
                return Card.RED
            if self.opponent[-1] == Card.RED:
                return Card.BLACK

        if self.my_card == Card.BLACK:
            return Card.RED
        if self.my_card == Card.RED:
            return Card.BLACK

        assert False, "Cannot be reached"


class B1V2(IlariiaPlayer):
    def __init__(self, learning_time):
        super(B1V2, self).__init__()
        self.counter = 0
        self.learning_time = learning_time
        self.historic_base = None

    @property
    def name(self) -> str:
        return "IlariiaUltimatum"

    def _learn_strategy(self):
        if self.opponent:
            if len(self.opponent) > 1:
                if self.opponent[-1] == self.opponent[-2]:
                    return self.my[-1]

            if self.opponent[-1] == Card.BLACK:
                return Card.RED
            if self.opponent[-1] == Card.RED:
                return Card.BLACK

        if self.my_card == Card.BLACK:
            return Card.RED
        if self.my_card == Card.RED:
            return Card.BLACK

        assert False, "Cannot be reached"

    def _historic_base_strategy(self):

        if self.historic_base is None:
            self.historic_base = self._generate_historic_base()

        sequence = list_sequence(self.my, self.opponent)
        choose_red = tuple(sequence + [Card.RED])
        choose_black = tuple(sequence + [Card.BLACK])

        if self.historic_base[choose_red] > self.historic_base[choose_black]:
            return Card.RED
        else:
            return Card.BLACK

    def _make_decision(self) -> Card:
        self.counter += 1
        if self.counter > self.learning_time:
            return self._historic_base_strategy()
        else:
            return self._learn_strategy()

    def _generate_historic_base(self):

        strategy = defaultdict(int)
        for r in self.storage:
            i = 0
            while i <= len(r.sequence):
                strategy[tuple(r.sequence[: (i+1)])] += r.value
                i += 2

        return strategy


class B1V3(B1V2):
    @property
    def name(self) -> str:
        return "IlariiaRandomUltimatum"

    def _learn_strategy(self):
        return random.choice([Card.RED, Card.BLACK])


if __name__ == "__main__":
    player = B1V2(100)

    player.take_card(Card.RED)
    player.opponent_said_card(Card.BLACK)
    card = player.say_card()
    player.opponent_change_card(True)
    decision = player.would_change_card()
    player.opponent_card(Card.BLACK)
    print(player)
    player.end_round()
    print(player.storage.print_game(0))
