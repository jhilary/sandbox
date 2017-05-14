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
        return "Action: %s;\nObservation: %s\nReward: %s;\nDone: %s\nInfo: %s\n" % \
               (self.action, self.observation, self.reward, self.done, self.info)

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
            self.observe(*self.env.reset())
            while True:
                counter += 1
                self.env.render()
                self.observe(*self.env.step(self.act()))
                if self.done:
                    print("Episode {} finished after {} timesteps".format(i_episode, counter))
                    break


class BaselineBot(Bot):

    def _act(self) -> object:
        return self.env.actions_space.sample()

    def _observe(self) -> None:
        pass


class SmarterBaselineBot(Bot):

    def _act(self) -> object:
        if self.action is not None:
            return self.action
        if self.observation[2] == Guess.AWAITING_FOR_GUESS:
            return switch_card(self.observation[1])
        return switch_card(self.observation[2])

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

        M_red, C_red = self.historic_base.get(choose_red, (0, 1))
        M_black, C_black = self.historic_base.get(choose_black, (0, 1))

        if M_red / C_red > M_black/C_black:
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
