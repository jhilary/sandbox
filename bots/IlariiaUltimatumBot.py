from env import switch_card, Guess, Card, FirstTurnInRound
from .Bot import Bot
from itertools import zip_longest


def _list_sequence(list1, list2):
    sequence = []
    for event1, event2 in zip_longest(list1, list2):
        sequence.append(event1)
        sequence.append(event2)
    return sequence


class IlariiaUltimatumBot(Bot):

    def __init__(self, learning_time: int, debug: bool = False):
        super(IlariiaUltimatumBot, self).__init__(debug)
        self.counter = 0
        self.learning_time = learning_time
        self.historic_base = {}

        self.my_card = None
        self.my = []
        self.opponent = []

    def _reset(self) -> None:
        self.my_card = None
        self.my = []
        self.opponent = []

    def _basic_strategy(self) -> int:
        if self.observation[2] == Guess.AWAITING_FOR_GUESS:
            return switch_card(self.my_card)
        return switch_card(self.observation[2])

    def _historic_base_strategy(self) -> int:

        sequence = _list_sequence(self.my, self.opponent)

        choose_red = tuple([self.observation[2]] + sequence + [Card.RED])
        choose_black = tuple([self.observation[2]] + sequence + [Card.BLACK])

        m_red, c_red = self.historic_base.get(choose_red, (0, 1))
        m_black, c_black = self.historic_base.get(choose_black, (0, 1))

        if m_red / c_red > m_black/c_black:
            return Card.RED
        else:
            return Card.BLACK

    def _act(self) -> int:
        self.counter += 1
        if self.counter > self.learning_time:
            return self._historic_base_strategy()
        else:
            return self._basic_strategy()

    def _observe(self) -> None:
        if self.observation[0] == FirstTurnInRound.YES:
            sequence = _list_sequence(self.my, self.opponent)
            i = 0
            while i < len(sequence):
                key = tuple([self.my_card] + sequence[: (i + 1)])
                if key not in self.historic_base:
                    new_value = (self.reward, 1)
                else:
                    new_value = (self.historic_base[key][0] + self.reward, self.historic_base[key][1] + 1)
                self.historic_base[key] = new_value
                i += 2
            self._reset()
        self.my_card = self.observation[1]
        self.opponent.append(self.observation[2])

