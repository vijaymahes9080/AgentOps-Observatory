"""
AgentOps Observatory - Intelligent Model Router & Cost Optimizer (Phase 7+)
Analyzes LLM prompts, complexity scores, and token volumes to recommend optimal model routing
(e.g. suggesting GPT-4o-mini or Haiku for deterministic queries to save up to 85% in inference costs).
"""

import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class OptimizationRecommendation(BaseModel):
    current_model: str
    recommended_model: str
    complexity_score: float  # 0.0 to 1.0
    estimated_savings_percent: float
    rationale: str
    is_safe_to_downgrade: bool


class CostOptimizer:
    """Evaluates prompt tasks and computes model routing optimization suggestions."""

    COMPLEX_PATTERNS = [
        re.compile(r"\b(?:prove|mathematical|formal proof|calculus|differential)\b", re.IGNORECASE),
        re.compile(r"\b(?:architect|refactor system|distributed consensus|concurrency bug)\b", re.IGNORECASE),
        re.compile(r"\b(?:write a compiler|write an interpreter|binary exploitation)\b", re.IGNORECASE),
    ]

    SIMPLE_PATTERNS = [
        re.compile(r"\b(?:summarize|format as json|extract email|translate to|fix typo)\b", re.IGNORECASE),
        re.compile(r"\b(?:classify sentiment|extract entities|yes or no|true or false)\b", re.IGNORECASE),
    ]

    @classmethod
    def evaluate_routing(
        cls,
        prompt: str,
        current_model: str,
        prompt_tokens: int = 0
    ) -> OptimizationRecommendation:
        norm_model = current_model.lower()

        # Check if already using lightweight or free model
        if any(m in norm_model for m in ["mini", "haiku", "flash", "llama-3-8b"]):
            return OptimizationRecommendation(
                current_model=current_model,
                recommended_model=current_model,
                complexity_score=0.3,
                estimated_savings_percent=0.0,
                rationale="Model is already on an efficient lightweight tier.",
                is_safe_to_downgrade=False
            )

        # Check complexity
        is_complex = any(p.search(prompt) for p in cls.COMPLEX_PATTERNS)
        is_simple = any(p.search(prompt) for p in cls.SIMPLE_PATTERNS)

        if is_complex or prompt_tokens > 8000:
            return OptimizationRecommendation(
                current_model=current_model,
                recommended_model=current_model,
                complexity_score=0.9,
                estimated_savings_percent=0.0,
                rationale="Prompt requires frontier reasoning and large context capacity.",
                is_safe_to_downgrade=False
            )

        # Suggest downgrade
        if "gpt-4" in norm_model:
            rec_model = "gpt-4o-mini"
            savings = 88.0
        elif "claude" in norm_model:
            rec_model = "claude-3-5-haiku"
            savings = 82.0
        elif "gemini" in norm_model:
            rec_model = "gemini-1.5-flash"
            savings = 85.0
        else:
            rec_model = "llama-3-8b (local)"
            savings = 100.0

        return OptimizationRecommendation(
            current_model=current_model,
            recommended_model=rec_model,
            complexity_score=0.25 if is_simple else 0.5,
            estimated_savings_percent=savings,
            rationale=f"Task exhibits moderate complexity suitable for {rec_model}, reducing cost by ~{savings}%.",
            is_safe_to_downgrade=True
        )
