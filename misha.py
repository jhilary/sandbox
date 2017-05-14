from collections import namedtuple
from itertools import product
import random
from pprint import pprint

from casino import Player, Card

RoundHistory = namedtuple("RoundHistory", "my_card opp_said_card changed opp_card")


class MishaBotV1(Player):
    def __init__(self, apriori=10):
        self._my_card: Card = None
        self._my_said_card: Card = None
        self._op_said_card: Card = None
        self._op_changed_card: bool = None
        self._apriori = apriori
        self.marginal_counters = self._init_counters(apriori)
        self._number_of_rounds = len(self.marginal_counters) * apriori

    @staticmethod
    def _init_counters(apriori):
        mycard = [Card.RED, Card.BLACK]
        opsaid = [Card.RED, Card.BLACK]
        changed = [True, False]
        opcard = [Card.RED, Card.BLACK]
        return {RoundHistory(*i): apriori for i in product(mycard, opsaid, changed, opcard)}

    @property
    def name(self) -> str:
        return self.__class__.__name__

    def take_card(self, card: Card) -> None:
        self._my_card = card

    def win(self, value) -> None:
        pass

    def would_change_card(self) -> bool:
        # return False
        if self._op_said_card != self._my_card:
            return False

        current_prob = self._p_opcard_cond_all(self._my_said_card)
        alt_prob = self._p_opcard_cond_all(self._invert_card(self._my_said_card))
        if alt_prob > current_prob:
            # print("Changing card. New prob is %s, old prob is %s" % (alt_prob, current_prob))
            # print("Current state: mycard %s, opsaid %s, changed %s, my_said_card: %s" % (self._my_card,
            #                                                                              self._op_said_card,
            #                                                                              self._op_changed_card,
            #                                                                              self._my_said_card))
            self._my_said_card = self._invert_card(self._my_said_card)
            return True
        else:
            return False

    def say_card(self) -> Card:
        if self._op_said_card is None:
            self._my_said_card = random.choice([Card.BLACK, Card.RED])
        else:
            p_opcard_red_cond_all = self._p_opcard_cond_all(Card.RED)
            self._my_said_card = Card.RED if random.random() < p_opcard_red_cond_all else Card.BLACK
            # p_opcard_black_cond_all = self._p_opcard_cond_all(Card.BLACK)
            # self._my_said_card = Card.RED if p_opcard_red_cond_all > p_opcard_black_cond_all else Card.BLACK
        return self._my_said_card

    def _p_opcard_cond_all(self, opcard):
        p_all_marg = self._marg_p(mycard=self._my_card, opsaid=self._op_said_card, changed=self._op_changed_card)
        p_all_cond_opcard = self._cond_p(opcard=opcard, mycard=self._my_card,
                                         opsaid=self._op_said_card, changed=self._op_changed_card)
        p_opcard_cond_all = 0.5 * p_all_cond_opcard / p_all_marg
        return p_opcard_cond_all

    def _marg_p(self, mycard=None, opsaid=None, changed=None, opcard=None):
        mycard = [Card.RED, Card.BLACK] if mycard is None else [mycard]
        opsaid = [Card.RED, Card.BLACK] if opsaid is None else [opsaid]
        changed = [True, False] if changed is None else [changed]
        opcard = [Card.RED, Card.BLACK] if opcard is None else [opcard]
        counter = sum(self.marginal_counters[RoundHistory(*i)] for i in product(mycard, opsaid, changed, opcard))
        return counter / self._number_of_rounds

    def _cond_p(self, opcard, mycard, opsaid=None, changed=None):
        opsaid = [Card.RED, Card.BLACK] if opsaid is None else [opsaid]
        changed = [True, False] if changed is None else [changed]
        mycard = [mycard]
        total = sum(self.marginal_counters[RoundHistory(*i)] for i in product([Card.RED, Card.BLACK],
                                                                              [Card.RED, Card.BLACK],
                                                                              [True, False],
                                                                              [opcard]))
        count = sum(self.marginal_counters[RoundHistory(*i)] for i in product(mycard, opsaid, changed, [opcard]))
        return count / total

    def end_round(self) -> None:
        self._op_said_card = None
        self._op_changed_card = None
        self._my_card = None
        self._my_said_card = None

    def opponent_card(self, card) -> None:
        changed = False if self._op_changed_card is None else self._op_changed_card
        history = RoundHistory(self._my_card, self._op_said_card, changed, card)
        self.marginal_counters[history] += 1
        self._number_of_rounds += 1

    def opponent_change_card(self, is_changed: bool) -> None:
        if is_changed:
            self._op_changed_card = True
            self._op_said_card = self._invert_card(self._op_said_card)

    def opponent_said_card(self, card: Card) -> None:
        self._op_said_card = card

    @staticmethod
    def _invert_card(card: Card):
        if card == Card.RED:
            return Card.BLACK
        else:
            return Card.RED


class MishaBotV2(Player):
    def __init__(self):
        self._op_said_card = None
        self._my_card = None

    def win(self, value) -> None:
        pass

    def opponent_card(self, card) -> None:
        pass

    def would_change_card(self) -> bool:
        return False

    def say_card(self) -> Card:
        if self._op_said_card is not None:
            return self._invert_card(self._op_said_card)
        else:
            return random.choice([Card.BLACK, Card.RED])

    def take_card(self, card: Card) -> None:
        self._my_card = card

    @property
    def name(self) -> str:
        return self.__class__.__name__

    def end_round(self) -> None:
        self._op_said_card = None

    def opponent_change_card(self, is_changed: bool) -> None:
        pass

    def opponent_said_card(self, card: Card) -> None:
        self._op_said_card = card

    @staticmethod
    def _invert_card(card: Card):
        if card == Card.RED:
            return Card.BLACK
        else:
            return Card.RED
