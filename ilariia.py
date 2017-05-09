from storage import Storage, StorageRow
from casino import Player, Card


class IlariiaPlayer(Player):
    def __init__(self):
        self.storage = Storage()
        self.my = []
        self.opponent = []
        self.my_card = None
        self.op_card = None
        self.is_me_first = False
        self.value = 0

    def reset(self):
        self.storage.save(StorageRow(
            self.my,
            self.opponent,
            self.my_card,
            self.op_card,
            self.is_me_first,
            self.value
        ))
        self.my_card = None
        self.op_card = None
        self.my = []
        self.opponent = []
        self.is_me_first = False
        self.value = 0

    def __repr__(self):
        return "(State) My card:%s; Opponent card:%s; My turns: %s; Opponent turns: %s; IsMeFirst:%s; Value:%s\n" % \
               (self.my_card,
                self.op_card,
                ", ".join(card.name for card in self.my),
                ", ".join(card.name for card in self.opponent),
                self.is_me_first,
                self.value)

    def take_card(self, card: Card) -> None:
        self.my_card = card

    def win(self, value) -> None:
        self.value = value

    def end_round(self):
        self.reset()

    def say_card(self) -> Card:
        if not self.opponent:
            self.is_me_first = True

        new_card = self._make_decision()
        self.my.append(new_card)
        return new_card

    def opponent_said_card(self, card: Card) -> None:
        self.opponent.append(card)

    def would_change_card(self) -> bool:
        card = self._make_decision()
        if card != self.my[-1]:
            self.my.append(card)
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

    def opponent_changed_card(self):
        self.opponent_said_card(self._change_card(self.opponent[-1]))

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


if __name__ == "__main__":
    player = B1V1()

    player.take_card(Card.RED)
    card = player.say_card()
    player.opponent_said_card(Card.BLACK)
    decision = player.would_change_card()
    player.opponent_card(Card.BLACK)
    print(player)
    player.end_round()
    print(player.storage.print_game(0))
