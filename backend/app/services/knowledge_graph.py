"""Morphological knowledge graph operations."""
import logging
from collections import deque
from typing import Dict, List, Optional, Set, Tuple

from sqlalchemy.orm import Session

from app.models import Root, RootWord, Vocabulary, WordSemanticLink

logger = logging.getLogger(__name__)


class KnowledgeGraphService:
    """Build and query root-word semantic graph."""

    def __init__(self, db: Session):
        self.db = db
        self._adjacency: Dict[int, List[Tuple[int, float, str]]] = {}
        self._root_to_words: Dict[int, List[int]] = {}

    def build(self) -> None:
        """Load graph edges from database."""
        self._adjacency.clear()
        self._root_to_words.clear()

        for rw in self.db.query(RootWord).all():
            self._add_edge(rw.root_id, rw.word_id, 1.0, "morph")
            self._root_to_words.setdefault(rw.root_id, []).append(rw.word_id)

        for vocab in self.db.query(Vocabulary).filter(Vocabulary.root_id.isnot(None)).all():
            self._add_edge(vocab.root_id, vocab.id, 0.9, "primary")
            self._root_to_words.setdefault(vocab.root_id, []).append(vocab.id)

        for link in self.db.query(WordSemanticLink).all():
            self._add_edge(link.word_id1, link.word_id2, link.similarity_score, "semantic")
            self._add_edge(link.word_id2, link.word_id1, link.similarity_score, "semantic")

    def _add_edge(self, a: int, b: int, weight: float, edge_type: str) -> None:
        self._adjacency.setdefault(a, []).append((b, weight, edge_type))
        self._adjacency.setdefault(b, []).append((a, weight, edge_type))

    def shortest_path_strength(self, source_id: int, target_id: int) -> float:
        """
        Compute morphological association via inverse shortest path length.
        Returns R_sim in [0, 1].
        """
        if source_id == target_id:
            return 1.0

        visited: Set[int] = {source_id}
        queue: deque = deque([(source_id, 1.0)])
        best = 0.0

        while queue:
            node, dist = queue.popleft()
            if dist > 5:
                continue
            for neighbor, weight, edge_type in self._adjacency.get(node, []):
                if neighbor in visited:
                    continue
                morph_bonus = 1.2 if edge_type in ("morph", "primary") else 0.8
                new_dist = dist + (1.0 / max(weight, 0.1)) / morph_bonus
                if neighbor == target_id:
                    best = max(best, 1.0 / new_dist)
                visited.add(neighbor)
                queue.append((neighbor, new_dist))

        return min(best, 1.0)

    def get_root_network(self, root_id: int) -> dict:
        """Return nodes and edges for word planet visualization."""
        words = self.db.query(Vocabulary).filter(Vocabulary.root_id == root_id).all()
        root = self.db.query(Root).filter(Root.id == root_id).first()
        if not root:
            return {"nodes": [], "edges": []}

        nodes = [{"id": f"root-{root.id}", "label": root.root, "type": "root", "meaning": root.meaning}]
        edges = []

        for w in words:
            nodes.append({
                "id": f"word-{w.id}",
                "label": w.word,
                "type": "word",
                "meaning": w.meaning,
                "difficulty": w.difficulty,
            })
            edges.append({
                "source": f"root-{root.id}",
                "target": f"word-{w.id}",
                "relation": "derived",
            })

        word_ids = [w.id for w in words]
        links = (
            self.db.query(WordSemanticLink)
            .filter(
                WordSemanticLink.word_id1.in_(word_ids),
                WordSemanticLink.word_id2.in_(word_ids),
            )
            .all()
        )
        for link in links:
            edges.append({
                "source": f"word-{link.word_id1}",
                "target": f"word-{link.word_id2}",
                "relation": "semantic",
                "weight": link.similarity_score,
            })

        return {"nodes": nodes, "edges": edges, "root": {"id": root.id, "root": root.root, "meaning": root.meaning}}
