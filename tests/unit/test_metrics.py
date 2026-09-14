import pytest
from backend.app.services.metrics import MetricsEngine


def test_calculate_cost():
    cost = MetricsEngine.calculate_cost("gpt-4o", prompt_tokens=1000, completion_tokens=2000)
    assert cost.total_tokens == 3000
    assert cost.estimated_cost_usd > 0.0
    assert cost.currency == "USD"


def test_calculate_local_model_cost_free():
    cost = MetricsEngine.calculate_cost("llama-3-70b", prompt_tokens=5000, completion_tokens=5000)
    assert cost.estimated_cost_usd == 0.0


def test_calculate_energy_and_carbon():
    energy = MetricsEngine.calculate_energy_and_carbon(total_tokens=10000, duration_ms=2500)
    assert energy.energy_kwh > 0.0
    assert energy.carbon_gco2eq > 0.0
    assert energy.pue == 1.25
