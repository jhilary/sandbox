from .Bot import Bot


class BaselineBot(Bot):
    def _act(self) -> object:
        return self.env.action_space.sample()

    def _observe(self) -> None:
        pass
