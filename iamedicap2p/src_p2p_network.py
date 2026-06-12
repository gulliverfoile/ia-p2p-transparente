import socket
import threading
import pickle
import time
import random
import json
from typing import Dict, Tuple, Callable, Optional
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

class P2PNetwork:
    def __init__(self, agent_id: str, host: str = 'localhost', port: int = 0,
                 network_sim_config: Optional[Dict] = None, merge_weight: float = 0.5):
        self.agent_id = agent_id
        self.host = host
        self.port = port
        self.merge_weight = merge_weight
        self.sock = None
        self.running = False
        self.peers: Dict[str, Tuple[str, int, bytes]] = {}
        self.incoming_queue = []