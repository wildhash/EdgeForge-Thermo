import json
from typing import List, Dict
from .types import Component, ComponentLimit

class LimitsAgent:
    """Agent 2: Component thermal limits specialist"""

    def __init__(self, limits_db_path: str = "data/limits_database.json"):
        """
        Create a LimitsAgent and load the component limits database from the specified JSON file.
        
        Parameters:
            limits_db_path (str): Filesystem path to a JSON file containing component limit specifications (default: "data/limits_database.json").
        
        Description:
            Loads the JSON file into self.db as a mapping from component MPN to its limit data and prints a one-line summary indicating how many component specs were loaded.
        """
        self.db: Dict[str, dict] = json.load(open(limits_db_path))
        print(f"🤖 Limits Agent: Loaded {len(self.db)} component specs")

    def get_limits_for_bom(self, components: List[Component]) -> List[ComponentLimit]:
        """
        Match BOM components to entries in the loaded thermal limits database.
        
        Parameters:
        	components (List[Component]): Bill of materials components to match by MPN.
        
        Returns:
        	List[ComponentLimit]: ComponentLimit objects for components whose MPN was found in the database.
        """
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
        """
        Identify the most thermally restrictive component from a list of component limits.
        
        Parameters:
            limits (List[ComponentLimit]): Component limit records to evaluate.
        
        Returns:
            ComponentLimit: The component limit with the lowest `max_temp_c`.
        
        Raises:
            ValueError: If `limits` is empty.
        """
        if not limits:
            raise ValueError("No component limits provided")

        most_restrictive = min(limits, key=lambda x: x.max_temp_c)
        print(
            f"🎯 Limits Agent: Most restrictive component is {most_restrictive.mpn} (Tmax={most_restrictive.max_temp_c}°C)"
        )
        return most_restrictive