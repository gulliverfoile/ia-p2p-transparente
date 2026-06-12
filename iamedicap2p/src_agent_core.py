import os
import pickle
import json
import time
import random
import numpy as np
from typing import Dict, Optional
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from src.event_bus import EventBus
from src.audit_service import AuditService
from src.world_model import TabularWorldModel
from src.ethical_module import EthicalModule
from src.memory import EpisodicMemory
from src.planner import RolloutPlanner
from src.reputation import ReputationManager
from src.p2p_network import P2PNetwork
from src.environment import Environment
from src.utils import setup_logger

class PrudentialAgent:
    def __init__(self, agent_id: str, config: Dict, env: Environment, data_dir: str = "./data"):
        self.agent_id = agent_id
        self.config = config
        self.env = env