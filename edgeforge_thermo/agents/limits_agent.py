import json
from typing import List, Dict
from .types import Component, ComponentLimit

class LimitsAgent:
    """Agent 2: Component thermal limits specialist"""

    def __init__(self, limits_db_path: str = "data/limits_database.json"):
        self.db: Dict[str, dict] = json.load(open(limits_db_path))
        print(f"🤖 Limits Agent: Loaded {len(self.db)} component specs")

    def get_limits_for_bom(self, components: List[Component]) -> List[ComponentLimit]:
        """Match BOM components to thermal limits database"""
        limits: List[ComponentLimit] = []
        coverage = 0

        for comp in components:
            if comp.mpn in self.db:
                data = self.db[comp.mpn]
                limit = ComponentLimit(
                    mpn=comp.mpn,
                    max_temp_c=data["max_temp_c"],
                    max_ramp_rate_c_per_s=data["max_ramp_rate_c_per_s"],
                    min_soak_time_s=data["min_soak_time_s"],
                    min_time_above_liquidus_s=data["min_time_above_liquidus_s"],
                    notes=data.get("notes", ""),
                )
                limits.append(limit)
                coverage += 1

        cov_pct = (coverage / len(components)) * 100 if components else 0
        print(f"✅ Limits Agent: Matched {coverage}/{len(components)} components ({cov_pct:.0f}% coverage)")

        return limits

    def get_most_restrictive(self, limits: List[ComponentLimit]) -> ComponentLimit:
        """Find the most thermally sensitive component"""
        if not limits:
            raise ValueError("No component limits provided")

        most_restrictive = min(limits, key=lambda x: x.max_temp_c)
        print(
            f"🎯 Limits Agent: Most restrictive component is {most_restrictive.mpn} (Tmax={most_restrictive.max_temp_c}°C)"
        )
        return most_restrictive
