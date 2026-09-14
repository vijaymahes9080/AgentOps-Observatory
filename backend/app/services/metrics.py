"""
AgentOps Observatory - Cost, Latency, and Energy Engine (Phase 7)
Computes multi-dimensional operational metrics:
- Latency (measured)
- Token counts (measured/estimated)
- Financial cost in USD (estimated based on standard rate cards)
- Energy in kWh (estimated based on GPU inference power profiles)
- Carbon footprint in gCO2eq (estimated with regional PUE & grid intensity)
"""

from typing import Dict, Optional, Tuple
from backend.app.schemas.events import CostEstimate, EnergyEstimate, MetricLabel


class MetricsEngine:
    """
    Precision calculation engine for cost, latency, energy, and emissions.
    Labels all estimations and simulated values clearly.
    """

    # Price per 1,000,000 tokens (USD)
    # [Prompt / 1M tokens, Completion / 1M tokens]
    MODEL_PRICING: Dict[str, Tuple[float, float]] = {
        # OpenAI
        "gpt-4o": (5.00, 15.00),
        "gpt-4o-mini": (0.15, 0.60),
        "gpt-4-turbo": (10.00, 30.00),
        "gpt-3.5-turbo": (0.50, 1.50),
        # Anthropic
        "claude-3-5-sonnet": (3.00, 15.00),
        "claude-3-opus": (15.00, 75.00),
        "claude-3-haiku": (0.25, 1.25),
        # Google
        "gemini-1.5-pro": (3.50, 10.50),
        "gemini-1.5-flash": (0.35, 1.05),
        # Local / Open Source (Ollama / vLLM / HuggingFace)
        "llama-3-70b": (0.00, 0.00),
        "llama-3-8b": (0.00, 0.00),
        "mistral-7b": (0.00, 0.00),
        "qwen-2.5": (0.00, 0.00),
        "default": (2.00, 6.00)
    }

    # kWh per 1,000 tokens (based on typical modern datacenter accelerator power consumption)
    ENERGY_KWH_PER_1K_TOKENS: float = 0.00035

    # Power usage effectiveness (PUE) factor
    DEFAULT_PUE: float = 1.25

    # Global average grid carbon intensity (gCO2eq / kWh)
    DEFAULT_CARBON_INTENSITY: float = 390.0

    @classmethod
    def calculate_cost(
        cls,
        model_name: str,
        prompt_tokens: int,
        completion_tokens: int,
        is_simulated: bool = False
    ) -> CostEstimate:
        """Calculate USD cost based on token counts and model pricing."""
        norm_name = (model_name or "default").lower().replace(":", "-").replace("/", "-")
        matched_pricing = None
        for key, rates in cls.MODEL_PRICING.items():
            if key in norm_name:
                matched_pricing = rates
                break

        if not matched_pricing:
            matched_pricing = cls.MODEL_PRICING["default"]

        prompt_cost = (prompt_tokens / 1_000_000.0) * matched_pricing[0]
        completion_cost = (completion_tokens / 1_000_000.0) * matched_pricing[1]
        total_cost = round(prompt_cost + completion_cost, 6)

        return CostEstimate(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            estimated_cost_usd=total_cost,
            model=model_name,
            currency="USD",
            label=MetricLabel.SIMULATED if is_simulated else MetricLabel.ESTIMATED
        )

    @classmethod
    def calculate_energy_and_carbon(
        cls,
        total_tokens: int,
        duration_ms: float = 0.0,
        pue: Optional[float] = None,
        grid_carbon_intensity: Optional[float] = None,
        is_simulated: bool = False
    ) -> EnergyEstimate:
        """
        Estimate kWh electrical consumption and grams of CO2 equivalent emissions.
        """
        eff_pue = pue or cls.DEFAULT_PUE
        eff_intensity = grid_carbon_intensity or cls.DEFAULT_CARBON_INTENSITY

        # Token-based compute energy
        base_energy_kwh = (total_tokens / 1000.0) * cls.ENERGY_KWH_PER_1K_TOKENS

        # If tokens are 0 but duration exists (e.g. tool execution or GPU idle), compute from duration:
        if base_energy_kwh == 0 and duration_ms > 0:
            # Assume ~250W server power consumption
            base_energy_kwh = (250.0 / 1000.0) * (duration_ms / 3_600_000.0)

        total_energy_kwh = round(base_energy_kwh * eff_pue, 8)
        carbon_gco2eq = round(total_energy_kwh * eff_intensity, 6)

        return EnergyEstimate(
            energy_kwh=total_energy_kwh,
            carbon_gco2eq=carbon_gco2eq,
            pue=eff_pue,
            grid_carbon_intensity=eff_intensity,
            label=MetricLabel.SIMULATED if is_simulated else MetricLabel.ESTIMATED
        )
