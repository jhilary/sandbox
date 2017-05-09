import random

from casino import Player, Card


class Inteleaving(Player):
    def __init__(self, name: str, *strategies: Player):
        self._name = name
        self._strategies = strategies
        self._current_strategy: Player = random.choice(self._strategies)

    def win(self, value) -> None:
        self._current_strategy.win(value)

    def would_change_card(self) -> bool:
        return self._current_strategy.would_change_card()

    def say_card(self) -> Card:
        return self._current_strategy.say_card()

    def take_card(self, card: Card) -> None:
        self._current_strategy: Player = random.choice(self._strategies)
        self._current_strategy.take_card(card)

    @property
    def name(self) -> str:
        return self._name

    def opponent_changed_card(self, is_changed: bool) -> None:
        self._current_strategy.opponent_change_card(is_changed)

    def opponent_said_card(self, card: Card) -> None:
        self._current_strategy.opponent_said_card(card)

    def opponent_card(self, card: Card) -> None:
        self._current_strategy.opponent_card(card)

    def end_round(self) -> None:
        pass
