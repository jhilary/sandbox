from collections import namedtuple
from itertools import zip_longest


def list_sequence(list1, list2):
    sequence = []
    for event1, event2 in zip_longest(list1, list2):
        sequence.append(event1)
        sequence.append(event2)
    return sequence


class StorageRow(namedtuple("StorageRow", ["my", "opponent", "my_card", "opponent_card", "value"])):
    @property
    def sequence(self):
        return list_sequence(self.my, self.opponent)

    def __repr__(self):
        result = ""
        for i, event in enumerate(self.sequence):
            result += ("I: %s\n" if i%2 == 0 else "O: %s\n") % event

        result += "My guess: %s(%s)\n" % (self.my[-1], self.opponent_card)
        result += "Opponent guess: %s(%s)\n" % (self.opponent[-1], self.my_card)
        result += "Value: %r\n" % self.value
        return result


class Storage(object):
    def __init__(self):
        self.result = []

    def _repr_game(self, i):
        return "Storage round %r:\n" % i + repr(self.result[i]) + "\n"

    def __repr__(self):
        storage_str = "Storage:\n\n"
        for i in range(len(self.result)):
            storage_str += self._repr_game(i)
        return storage_str

    def __iter__(self):
        return iter(self.result)

    def print(self):
        return repr(self)

    def print_game(self, game_id):
        return self._repr_game(game_id)

    def save(self, value):
        self.result.append(value)
