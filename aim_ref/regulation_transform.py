"""Helpers to apply 2026 regulation multipliers to feature matrices."""

from __future__ import annotations

from typing import Dict

import pandas as pd

REGULATION_MULTIPLIERS: Dict[str, Dict[str, float]] = {
    "hybrid_power": {
        "power_ratio": 3.33  # 100% hybrid power (up from 30%)
    },
    "boost_mode": {
        "power_ratio": 1.25,              # Boost button power increase
        "fuel_efficiency_rating": 1.05,   # Improved energy recovery
        "overtake_power_boost": 1.15,     # Extra 0.5MJ for overtake mode
        "ers_deployment_flexibility": 1.4 # Deploy anywhere vs fixed DRS zones
    },
    "chassis": {
        "weight_ratio": 0.962  # 768kg (down from 798kg)
    },
    "tyres": {
        "tire_grip_ratio": 0.94  # Reduced grip with new compounds
    },
    "fuel": {
        "fuel_flow_ratio": 0.75,         # Lower flow rate
        "fuel_efficiency_rating": 1.15   # Better efficiency
    }
}


def apply_2026_regulations(features: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of the features with 2026 multipliers applied."""

    updated = features.copy()

    for multipliers in REGULATION_MULTIPLIERS.values():
        for column, multiplier in multipliers.items():
            if column in updated.columns:
                updated[column] = updated[column] * multiplier

    return updated


__all__ = ["apply_2026_regulations", "REGULATION_MULTIPLIERS"]
