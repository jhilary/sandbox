import random
from typing import Optional

from casino import Player, Card, Action


class Inteleaving(Player):
    def __init__(self, name: str, *strategies: Player):
        self._name = name
        self._strategies = strategies
        self._current_strategy: Player = random.choice(self._strategies)

    def notify_about_value(self, value) -> None:
        self._current_strategy.notify_about_value(value)

    def make_first_action(self, opponents_bid: Card) -> Action:
        return self._current_strategy.make_first_action(opponents_bid)

    def make_first_bid(self) -> Card:
        return self._current_strategy.make_first_bid()

    def deal(self, card: Card) -> None:
        self._current_strategy: Player = random.choice(self._strategies)
        self._current_strategy.deal(card)

    @property
    def name(self) -> str:
        return self._name

    def notify_about_last_action(self, opponents_action: Optional[Action]) -> None:
        self._current_strategy.notify_about_last_action(opponents_action)

    def make_response_action(self, opponents_action: Action) -> Action:
        return self._current_strategy.make_response_action(opponents_action)

    def make_response_bid(self, opponents_bid: Card) -> Card:
        return self._current_strategy.make_response_bid(opponents_bid)
