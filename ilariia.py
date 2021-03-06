import random
from storage import Storage, StorageRow, list_sequence
from casino import Player, Card


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
                ", ".join(card.name if card else "None" for card in self.my) ,
                ", ".join(card.name if card else "None" for card in self.opponent),
                self.value)

    def take_card(self, card: Card) -> None:
        self.my_card = card

    def win(self, value) -> None:
        self.value = value

    def end_round(self) -> None:
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
        old_card = self.my[-1]
        new_card = self._make_decision()
        self.my.append(new_card)
        return new_card != old_card

    def opponent_card(self, card: Card) -> None:
        self.op_card = card

    def opponent_change_card(self, is_changed: bool) -> None:
        if is_changed:
            self.opponent_said_card(self.switch_card(self.opponent[-1]))
        else:
            self.opponent_said_card(self.opponent[-1])

    @staticmethod
    def switch_card(old_card) -> Card:
        if old_card == Card.BLACK:
            return Card.RED
        else:
            return Card.BLACK

    def _make_decision(self) -> Card:
        raise NotImplementedError()


class BlackBot(IlariiaPlayer):

    @property
    def name(self) -> str:
        return "BlackBot"

    def _make_decision(self) -> Card:
        return Card.BLACK


class B1V1(IlariiaPlayer):

    @property
    def name(self) -> str:
        return "IlariiaB1V1"

    def _make_decision(self) -> Card:
        if self.opponent:
            return self.switch_card(self.opponent[-1])
        return self.switch_card(self.my_card)


class B1V2(IlariiaPlayer):
    def __init__(self, learning_time):
        super(B1V2, self).__init__()
        self.counter = 0
        self.learning_time = learning_time
        self.historic_base = {}

    @property
    def name(self) -> str:
        return "IlariiaUltimatum"

    def _learn_strategy(self) -> Card:
        if self.opponent:
            return self.switch_card(self.opponent[-1])
        return self.switch_card(self.my_card)

    def _historic_base_strategy(self) -> Card:

        sequence = list_sequence(self.my, self.opponent)

        choose_red = tuple([self.my_card] + sequence + [Card.RED])
        choose_black = tuple([self.my_card] + sequence + [Card.BLACK])

        M_red, C_red = self.historic_base.get(choose_red, (0, 1))
        M_black, C_black = self.historic_base.get(choose_black, (0, 1))

        if M_red / C_red > M_black/C_black:
            return Card.RED
        else:
            return Card.BLACK

    def _make_decision(self) -> Card:
        self.counter += 1
        if self.counter > self.learning_time:
            return self._historic_base_strategy()
        else:
            return self._learn_strategy()

    def win(self, value) -> None:
        self.value = value
        sequence = list_sequence(self.my, self.opponent)
        i = 0
        while i < len(sequence):
            key = tuple([self.my_card] + sequence[: (i + 1)])
            if key not in self.historic_base:
                new_value = (value, 1)
            else:
                new_value = (self.historic_base[key][0] + value, self.historic_base[key][1] + 1)
            self.historic_base[key] = new_value
            i += 2


class B1V3(B1V2):
    @property
    def name(self) -> str:
        return "IlariiaRandomUltimatum"

    def _learn_strategy(self) -> Card:
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
