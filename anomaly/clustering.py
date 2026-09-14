"""
AgentOps Observatory - Semantic Trace Clustering & Behavioral Drift Engine (Phase 8+)
Computes vector embeddings and cosine similarity across agent run intents to detect subtle behavioral drift.
"""

import math
from collections import Counter
from typing import Any, Dict, List, Tuple


class SemanticClusteringEngine:
    """Lightweight deterministic vector clustering for agent run intent baselining."""

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return [w.lower() for w in text.split() if len(w) > 2]

    @classmethod
    def compute_similarity(cls, prompt_a: str, prompt_b: str) -> float:
        """Compute cosine similarity between two prompt text bags."""
        tokens_a = cls._tokenize(prompt_a)
        tokens_b = cls._tokenize(prompt_b)

        if not tokens_a or not tokens_b:
            return 0.0

        vec_a = Counter(tokens_a)
        vec_b = Counter(tokens_b)

        all_keys = set(vec_a.keys()).union(set(vec_b.keys()))

        dot_product = sum(vec_a[k] * vec_b[k] for k in all_keys)
        mag_a = math.sqrt(sum(v ** 2 for v in vec_a.values()))
        mag_b = math.sqrt(sum(v ** 2 for v in vec_b.values()))

        if mag_a == 0 or mag_b == 0:
            return 0.0

        return round(dot_product / (mag_a * mag_b), 4)

    @classmethod
    def detect_intent_drift(
        cls,
        current_prompt: str,
        baseline_cluster: List[str],
        threshold: float = 0.25
    ) -> Dict[str, Any]:
        """Flags whether current prompt significantly diverges from historical baseline."""
        if not baseline_cluster:
            return {"is_drift": False, "average_similarity": 1.0}

        similarities = [cls.compute_similarity(current_prompt, base) for base in baseline_cluster]
        avg_sim = sum(similarities) / len(similarities)

        is_drift = avg_sim < threshold
        return {
            "is_drift": is_drift,
            "average_similarity": round(avg_sim, 4),
            "threshold": threshold,
            "rationale": "High behavioral divergence from approved agent baseline." if is_drift else "Within baseline tolerance."
        }
