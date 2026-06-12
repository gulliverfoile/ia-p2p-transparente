from typing import Dict, Callable, List
from collections import defaultdict
import threading
import time

class EventBus:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._subscribers = defaultdict(list)