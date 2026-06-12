from typing import Dict

class ReputationManager:
    def __init__(self, initial: float = 0.5, update_rate: float = 0.1, exclusion_threshold: float = 0.2):
        self.reputations: Dict[str, float] = {}
        self.initial = initial
        self.update_rate = update_rate
        self.exclusion_threshold = exclusion_threshold
        self.excluded: set = set()

    def get_reputation(self, peer_id: str) -> float:
        if peer_id in self.excluded:
            return 0.0