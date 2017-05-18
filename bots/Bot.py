from abc import ABCMeta, abstractmethod
from gym import Env


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
        return f"Name: { self.name };\nAction: { self.action };\nObservation: { self.observation }\n" \
               f"Reward: { self.reward };\nDone: { self.done }\nInfo: { self.info }\n"

    @abstractmethod
    def _observe(self) -> None:
        raise NotImplementedError()

    def observe(self, observation: object, reward: float, done: bool, info: dict):
        self.observation = observation
        self.reward = reward
        self.done = done
        self.info = info
        if self.debug:
            print(self)
        self._observe()

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
