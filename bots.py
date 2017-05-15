from abc import ABCMeta, abstractmethod
from gym import Env
from env import Card, Guess, FirstTurnInRound
from storage import list_sequence


class Bot(object):
    __metaclass__ = ABCMeta

    @property
    def name(self) -> str:
        return self.__class__.__name__

    def __init__(self, debug: bool = False):
        self.env = None
        self.observation = None
        self.reward = 0
        self.done = False
        self.info = {}
        self.action = None
        self.debug = debug

    def set_env(self, env: Env) -> None:
        self.env = env

    def __repr__(self):
        return f"Name: { self.name } Action: { self.action };\nObservation: { self.observation }\n" \
               f"Reward: { self.reward };\nDone: { self.done }\nInfo: { self.info }\n"

    @abstractmethod
    def _observe(self) -> None:
        raise NotImplementedError()

    def observe(self, observation: object, reward: float, done: bool, info: dict):
        self.observation = observation
        self.reward = reward
        self.done = done
        self.info = info
        self._observe()
        if self.debug:
            print(self)

    @abstractmethod
    def _act(self) -> object:
        raise NotImplementedError()

    def act(self) -> object:
        self.action = self._act()
        return self.action

    def run(self, episodes: int = 1000) -> None:
        for i_episode in range(episodes):
            counter = 0
            initial_state = self.env.reset()
            self.observe(*initial_state)
            while True:
                counter += 1
                self.env.render()
                action = self.act()
                state = self.env.step(action)
                self.observe(*state)
                if self.done:
                    self.env.render()
                    print(f"Episode { i_episode } finished after { counter } timesteps")
                    break


class BaselineBot(Bot):
    def _act(self) -> object:
        return self.env.action_space.sample()

    def _observe(self) -> None:
        pass


class SmarterBaselineBot(Bot):

    def _act(self) -> object:
        return switch_card(self.observation[1])

    def _observe(self) -> None:
        pass


class BlackBot(Bot):

    def _act(self) -> object:
        return Card.BLACK

    def _observe(self) -> None:
        pass


def switch_card(value: int) -> int:
    if value == Card.RED:
        return Card.BLACK
    return Card.RED


class IlariiaB1V1(Bot):

    def _act(self) -> int:
        if self.observation[2] == Guess.AWAITING_FOR_GUESS:
            return switch_card(self.observation[1])
        return switch_card(self.observation[2])

    def _observe(self):
        pass


class IlariiaUltimatum(Bot):

    def __init__(self, learning_time: int, debug: bool = False):
        super(IlariiaUltimatum, self).__init__(debug)
        self.counter = 0
        self.learning_time = learning_time
        self.historic_base = {}
        self.my = []
        self.opponent = []

    def _reset(self) -> None:
        self.my = []
        self.opponent = []

    def _basic_strategy(self) -> int:
        if self.observation[2] == Guess.AWAITING_FOR_GUESS:
            return switch_card(self.observation[1])
        return switch_card(self.observation[2])

    def _historic_base_strategy(self) -> int:

        sequence = list_sequence(self.my, self.opponent)

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
            self._reset()
        self.opponent.append(self.observation[2])
        if self.done:
            sequence = list_sequence(self.my, self.opponent)
            i = 0
            while i < len(sequence):
                key = tuple([self.observation[1]] + sequence[: (i + 1)])
                if key not in self.historic_base:
                    new_value = (self.reward, 1)
                else:
                    new_value = (self.historic_base[key][0] + self.reward, self.historic_base[key][1] + 1)
                self.historic_base[key] = new_value
                i += 2


class IlariiaRandomUltimatum(IlariiaUltimatum):
    def _basic_strategy(self) -> Card:
        return self.env.actions_space.sample()

from collections import namedtuple
import random
from itertools import product

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


class MishaBotV2(Bot):

    def _act(self) -> object:
        if self.observation[2] == Guess.AWAITING_FOR_GUESS:
            return random.choice([Card.BLACK, Card.RED])
        elif self.observation[0] == FirstTurnInRound.YES:
            return switch_card(self.observation[2])
        else:
            return self.action

    def _observe(self) -> None:
        pass


