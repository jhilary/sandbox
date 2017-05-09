from collections import namedtuple
from itertools import zip_longest


class StorageRow(namedtuple("StorageRow", ["my", "opponent", "my_card", "opponent_card", "is_me_first", "value"])):
    def __repr__(self):
        result = ""
        if self.is_me_first:
            for event1, event2 in zip_longest(self.my, self.opponent):
                result += "I: %s\n" % event1
                result += "O: %s\n" % event2
        else:
            for event1, event2 in zip_longest(self.opponent, self.my):
                result += "O: %s\n" % event1
                result += "I: %s\n" % event2
        result += "My guess: %s(%s)\n" % (self.my[-1], self.opponent_card)
        result += "Opponent guess: %s(%s)\n" % (self.opponent[-1], self.my_card)
        result += "Value: %r\n" % self.value
        return result


class Storage(object):
    def __init__(self):
        self.result = []

    def _repr_game(self, i):
        return "Game %r:\n" % i + repr(self.result[i]) + "\n"

    def __repr__(self):
        storage_str = "Storage:\n\n"
        for i in range(len(self.result)):
            storage_str += self._repr_game(i)
        return storage_str

    def print(self):
        return repr(self)

    def print_game(self, game_id):
        return self._repr_game(game_id)

    def save(self, value):
        self.result.append(value)
