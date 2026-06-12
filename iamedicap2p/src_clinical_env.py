"""
Entorno clínico con memoria de flujo temporal (ventana deslizante).
Cada observación guarda un historial de los últimos N pasos (síntomas y pruebas)
para que el agente pueda detectar tendencias (ej. fiebre creciente).
"""

import random
import numpy as np
from collections import deque
from typing import Dict, List, Any, Tuple
from src.environment import Environment

class ClinicalEnvironment(Environment):
    def __init__(self, config: Dict, seed: int = None, history_window: int = 3):
        """
        Args:
            config: diccionario con 'diseases', 'rewards', 'max_steps_per_episode'
            seed: semilla para reproducibilidad
            history_window: número de pasos anteriores a incluir en la representación
        """
        self.config = config
        self.diseases = config['diseases']
        self.rewards = config['rewards']