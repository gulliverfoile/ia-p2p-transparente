class EthicalModule:
    def __init__(self, min_safe_margin: float = 2.0, hazard_penalty: float = -5.0,
                 dynamic_margin: bool = True, uncertainty_factor: bool = True):
        self.min_safe_margin = min_safe_margin
        self.hazard_penalty = hazard_penalty
        self.dynamic_margin = dynamic_margin
        self.uncertainty_factor = uncertainty_factor
        self.base_margin = min_safe_margin

    def is_allowed(self, action: str, predicted_reward: float, hazard_risk: float,
                   extra_margin: float = 0.0, uncertainty: float = 0.0) -> bool:
        expected_harm = hazard_risk * abs(self.hazard_penalty)
        if self.uncertainty_factor:
            expected_harm *= (1.0 + uncertainty)
        margin = self.base_margin + extra_margin
        return (predicted_reward - expected_harm) >= margin

    def get_current_margin(self) -> float:
        return self.base_margin

    def set_base_margin(self, margin: float):
        self.base_margin = margin