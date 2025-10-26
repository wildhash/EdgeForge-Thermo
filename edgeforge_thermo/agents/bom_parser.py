import pandas as pd
from typing import List
from .types import Component, ThermalMass

class BOMParserAgent:
    """Agent 1: BOM parsing specialist"""

    def parse(self, filepath: str) -> List[Component]:
        """Parse BOM CSV into structured components"""
        print(f"🤖 BOM Parser Agent: Reading {filepath}")

        df = pd.read_csv(filepath)
        components: List[Component] = []

        for idx, row in df.iterrows():
            try:
                comp = Component(
                    designator=str(row["designator"]),
                    mpn=str(row["mpn"]),
                    package=str(row["package"]),
                    qty=int(row["qty"]),
                    thermal_mass=ThermalMass(row.get("thermal_mass", "medium")),
                    component_type=str(row.get("component_type", "Unknown")),
                )
                components.append(comp)
            except Exception as e:
                print(f"⚠️  Warning: Skipping row {idx}: {e}")

        print(f"✅ BOM Parser Agent: Parsed {len(components)} components")
        return components
