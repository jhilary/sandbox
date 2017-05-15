from collections import namedtuple
import random
from itertools import product

from ..env import switch_card, Card, FirstTurnInRound, Guess
from .Bot import Bot


RoundHistory = namedtuple("RoundHistory", "my_card opp_said_card changed opp_card")


class MishaBotV1(Bot):

    def __init__(self, apriori=10, debug=False):
        super(MishaBotV1, self).__init__(debug)
        self._apriori = apriori

        # Storage
        self.marginal_counters = self._init_counters(apriori)
        self._number_of_rounds = len(self.marginal_counters) * apriori

        # Round state
        self._op_previous_guess: Card = None
        self._op_changed_guess = False

    def _observe(self) -> None:
        if self.observation[0] == FirstTurnInRound.YES:
            self._reset()

        if self.observation[2] != Guess.AWAITING_FOR_GUESS:
            if self._op_previous_card is None:
                self._op_previous_card = self.observation[2]
            elif self._op_previous_card != self.observation[2]:
                self._op_changed_guess = True

    def _act(self) -> object:
        if self.observation[0] == FirstTurnInRound.YES:
            if self.observation[2] == Guess.AWAITING_FOR_GUESS:
                return random.choice([Card.BLACK, Card.RED])
            else:
                if random.random() < self._p_opcard_cond_all(Card.RED):
                    return Card.RED
                else:
                    return Card.BLACK
        else:
            if self.observation[2] != self.observation[1]:
                return self.action
            else:
                current_prob = self._p_opcard_cond_all(self.action)
                alt_prob = self._p_opcard_cond_all(switch_card(self.action))

                if alt_prob > current_prob:
                    return switch_card(self.action)
                else:
                    return self.action

    @staticmethod
    def _init_counters(apriori):
        mycard = [Card.RED, Card.BLACK]
        opsaid = [Card.RED, Card.BLACK]
        changed = [True, False]
        opcard = [Card.RED, Card.BLACK]
        return { RoundHistory(*i): apriori for i in product(mycard, opsaid, changed, opcard) }

    def _p_opcard_cond_all(self, opcard):
        mycard = self.observation[1]
        opsaid = self.observation[2]
        changed = self._op_changed_guess
        p_all_marg = self._marg_p(mycard=mycard, opsaid=opsaid, changed=changed)
        p_all_cond_opcard = self._cond_p(opcard=opcard, mycard=mycard, opsaid=opsaid, changed=changed)
        p_opcard_cond_all = 0.5 * p_all_cond_opcard / p_all_marg
        return p_opcard_cond_all

    def _marg_p(self, mycard=None, opsaid=None, changed=None, opcard=None):
        mycard = [mycard]
        opsaid = [Card.RED, Card.BLACK] if opsaid == Guess.AWAITING_FOR_GUESS else [opsaid]
        changed = [True, False] if changed is None else [changed]
        opcard = [Card.RED, Card.BLACK] if opcard is None else [opcard]
        counter = sum(self.marginal_counters[RoundHistory(*i)] for i in product(mycard, opsaid, changed, opcard))
        return counter / self._number_of_rounds

    def _cond_p(self, opcard, mycard, opsaid=None, changed=None):
        opsaid = [Card.RED, Card.BLACK] if opsaid == Guess.AWAITING_FOR_GUESS else [opsaid]
        changed = [True, False] if changed is None else [changed]
        mycard = [mycard]
        total = sum(self.marginal_counters[RoundHistory(*i)] for i in product([Card.RED, Card.BLACK],
                                                                              [Card.RED, Card.BLACK],
                                                                              [True, False],
                                                                              [opcard]))
        count = sum(self.marginal_counters[RoundHistory(*i)] for i in product(mycard, opsaid, changed, [opcard]))
        return count / total

    def _reset(self) -> None:
        self._op_previous_guess = None
        self._op_changed_guess = False
