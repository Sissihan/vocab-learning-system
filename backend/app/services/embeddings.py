"""Word embedding utilities for semantic similarity."""
import hashlib
import json
import logging
from typing import List

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from app.config import settings

logger = logging.getLogger(__name__)


def _hash_seed(text: str) -> int:
    return int(hashlib.md5(text.encode()).hexdigest(), 16) % (2**32)


def generate_embedding(word: str, meaning: str = "") -> List[float]:
    """Deterministic pseudo-embedding from word+meaning for demo."""
    rng = np.random.default_rng(_hash_seed(word + meaning))
    vec = rng.standard_normal(settings.embedding_dim)
    vec = vec / (np.linalg.norm(vec) + 1e-8)
    return vec.tolist()


def parse_embedding(embedding_json: str) -> np.ndarray:
    data = json.loads(embedding_json) if embedding_json else []
    if not data:
        return np.zeros(settings.embedding_dim)
    return np.array(data, dtype=float)


def semantic_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Cosine similarity S_sim in [0, 1] mapped from [-1,1]."""
    if vec_a.size == 0 or vec_b.size == 0:
        return 0.0
    sim = float(cosine_similarity([vec_a], [vec_b])[0][0])
    return max(0.0, min(1.0, (sim + 1) / 2))
