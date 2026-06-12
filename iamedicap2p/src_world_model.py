from collections import defaultdict, Counter
from typing import Dict, Tuple, Optional
import pickle
import os

class TabularWorldModel:
    def __init__(self, max_states: int = 10000):
        self.transitions = defaultdict(lambda: defaultdict(int))
        self.rewards = defaultdict(lambda: defaultdict(list))
        self.state_counts = Counter()
        self.max_states = max_states
        self.version = 0

    def observe(self, state: str, action: str, next_state: str, reward: float):
        self.transitions[(state, action)][next_state] += 1
        self.rewards[(state, action)].append(reward)
        self.state_counts[next_state] += 1
        if len(self.state_counts) > self.max_states:
            self._prune()

    def _prune(self):
        if len(self.state_counts) <= self.max_states:
            return
        to_remove = set()
        sorted_states = sorted(self.state_counts.items(), key=lambda x: x[1])
        for state, _ in sorted_states[:len(self.state_counts) - self.max_states]: