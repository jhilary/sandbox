from collections import Counter

from casino import Player, Card
import random


class State(object):
    """
    Actual color of the card does not matter. So the state space can be reduced
    """
    KEEP = 0
    CHANGE = 1
    OPPONENT_SAID_MY = 2
    OPPONENT_SAID_NOT_MY = 3

    def __init__(self, prev_state=None):
        """
        We want to init from previous state to form trajectory
        state_1 -> state_2 -> current_state
        :param prev_state:
        """
        self._prev_state = prev_state
        self.event_sequence = []
        if prev_state:
            self.event_sequence += prev_state.event_sequence

    def make_tuple(self):
        """
        Used for hashing
        :return:
        """
        return tuple(self.event_sequence)

    def add_event(self, event):
        self.event_sequence.append(event)

    def get_prev(self):
        """
        Method aimed for backtracking update of action values
        """
        return self._prev_state


def reverse_card(card):
    if card == Card.BLACK:
        return Card.RED
    return Card.BLACK


class CoolSarsaPlayer(Player):
    def __init__(self, discount=0.9, alpha=0.1, explorer_spirit_level=0.05):
        self._q_table = Counter()   # table contains values for state - action pairs
        self._explorer_spirit = explorer_spirit_level  # chance of executing random policy
        self._discount = discount  # we favor quick winning to long one
        self._alpha = alpha  # value update rate

        self._my_card = None
        self._opponent_card = None
        self._state = State()
        self._action_sequence = []

    @property
    def name(self) -> str:
        return "SARSA (actually not sarsa)"
        # Sarsa uses some current policy, we use greedy, so it is trajectory based Q-learning

    def _get_action_value(self, action):
        return self._q_table[self._state.make_tuple() + (action,)]  # Q(s, a) -> value

    def _act(self):
        # Select action which has highest value in current state
        greedy_action = max((self._get_action_value(action), action) for action in (State.KEEP, State.CHANGE))[1]

        # Execute random policy with some chance
        if random.random() > self._explorer_spirit:
            action = greedy_action
        else:
            action = random.choice((State.KEEP, State.CHANGE))

        # Go to next state
        self._state = State(self._state)
        self._state.add_event(action)
        self._action_sequence.append(action)

        return action

    @property
    def _not_my_card(self):
        return reverse_card(self._my_card)

    def take_card(self, card: Card) -> None:
        # do nothing
        self._my_card = card

    def say_card(self) -> Card:
        action = self._act()
        if action == State.KEEP:
            return self._my_card
        return self._not_my_card

    def _remember_opponent_action(self):
        if self._opponent_card == self._my_card:
            self._state.add_event(State.OPPONENT_SAID_MY)
        else:
            self._state.add_event(State.OPPONENT_SAID_NOT_MY)

    def opponent_said_card(self, card: Card) -> None:
        self._opponent_card = card
        self._remember_opponent_action()

    def would_change_card(self) -> bool:
        return self._act() == State.KEEP

    def opponent_change_card(self, is_changed: bool) -> None:
        # construct state
        if is_changed:
            self._opponent_card = reverse_card(self._opponent_card)
        self._remember_opponent_action()

    def end_round(self) -> None:
        self._my_card = None
        self._opponent_card = None
        self._state = State()
        self._action_sequence = []

    def opponent_card(self, card) -> None:
        # does not really matter because we infer this information from value of winnings
        pass

    def win(self, value) -> None:
        # update q-table with sampled trajectory
        state = self._state
        current_val = value
        for action in self._action_sequence[::-1]:
            state = state.get_prev()
            q_table_entry = state.make_tuple() + (action,)
            self._q_table[q_table_entry] = (1.0 - self._alpha) * self._q_table[q_table_entry] + self._alpha * current_val
            current_val *= self._discount
