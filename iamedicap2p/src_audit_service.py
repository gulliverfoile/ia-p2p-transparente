import sqlite3
import json
import hashlib
from datetime import datetime
from typing import Dict, Optional
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from src.event_bus import EventBus

class AuditService:
    def __init__(self, agent_id: str, db_path: str, private_key: Ed25519PrivateKey):
        self.agent_id = agent_id
        self.db_path = db_path
        self.private_key = private_key
        self.last_hash = self._load_last_hash()
        self._init_db()
        bus = EventBus()