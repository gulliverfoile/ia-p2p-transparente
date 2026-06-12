import hashlib
import numpy as np
from collections import deque
from typing import List, Tuple, Optional

class TinyVectorizer:
    def __init__(self, dim: int = 128):
        self.dim = dim

    def embed(self, text: str) -> np.ndarray: