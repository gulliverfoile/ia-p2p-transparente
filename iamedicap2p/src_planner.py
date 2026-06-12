import random
import numpy as np
from typing import Dict, Tuple, List

class RolloutPlanner:
    def __init__(self, actions: List[str], depth: int = 4, n_rollouts: int = 30,
                 epsilon: float = 0.2, novelty_bonus_weight: float = 0.5):
        self.actions = actions
        self.depth = depth
        self.n_rollouts = n_rollouts
        self.epsilon = epsilon
        self.novelty_bonus_weight = novelty_bonus_weight

    def plan(self, state_repr: str, model, ethics, memory, extra_margin: float = 0.0) -> Tuple[str, float, Dict[str, float]]:
        best_action = None
        best_score = -1e9
        action_scores = {}

        for action in self.actions:
            scores = []
            for _ in range(self.n_rollouts):
                score = self._rollout(state_repr, action, model, memory)