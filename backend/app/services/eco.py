"""
AgentOps Observatory - Eco-Compute & Carbon Offset Calculator (Phase 7+)
Computes tree-seedling absorption equivalence, datacenter water usage effectiveness (WUE),
and generates Green Compute Sustainability scores for corporate ESG reporting.
"""

from typing import Dict
from pydantic import BaseModel


class EcoSustainabilityReport(BaseModel):
    total_energy_kwh: float
    total_carbon_gco2eq: float
    trees_seedlings_equivalent: float
    water_liters_evaporated: float
    eco_rating: str
    renewable_energy_percent: float


class EcoComputeEngine:
    # A mature tree absorbs approximately 21,770 grams of CO2 per year (~59.6 gCO2/day)
    CO2_GRAMS_PER_TREE_DAY: float = 59.64

    # Datacenters consume ~1.8 liters of water per kWh for direct evaporative cooling
    LITERS_WATER_PER_KWH: float = 1.80

    @classmethod
    def calculate_sustainability_metrics(
        cls,
        total_energy_kwh: float,
        total_carbon_gco2eq: float,
        renewable_percent: float = 85.0
    ) -> EcoSustainabilityReport:
        # Effective carbon after renewable credit
        net_carbon = total_carbon_gco2eq * (1.0 - (renewable_percent / 100.0) * 0.7)
        trees_needed_days = net_carbon / cls.CO2_GRAMS_PER_TREE_DAY
        trees_annual_seedlings = round(trees_needed_days / 365.0, 4)
        water_evaporated = round(total_energy_kwh * cls.LITERS_WATER_PER_KWH, 3)

        if total_carbon_gco2eq < 100:
            rating = "A+ (Ultra Low Emissions)"
        elif total_carbon_gco2eq < 1000:
            rating = "A (Clean Efficient Compute)"
        elif total_carbon_gco2eq < 10000:
            rating = "B (Standard Datacenter)"
        else:
            rating = "C (High Energy Consumption)"

        return EcoSustainabilityReport(
            total_energy_kwh=round(total_energy_kwh, 6),
            total_carbon_gco2eq=round(total_carbon_gco2eq, 4),
            trees_seedlings_equivalent=trees_annual_seedlings,
            water_liters_evaporated=water_evaporated,
            eco_rating=rating,
            renewable_energy_percent=renewable_percent
        )
