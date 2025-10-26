import pandas as pd
from typing import List
from .types import Component, ThermalMass

class BOMParserAgent:
    """Agent 1: BOM parsing specialist"""

    def parse(self, filepath: str) -> List[Component]:
        """
        Parse a BOM CSV file into a list of Component objects.
        
        Expects the CSV to contain columns: "designator", "mpn", "package", and "qty".
        Optional columns:
        - "thermal_mass" (defaults to "medium")
        - "component_type" (defaults to "Unknown")
        
        Rows that fail to construct a Component are skipped and a warning is printed for each skipped row.
        
        Parameters:
            filepath (str): Path to the BOM CSV file.
        
        Returns:
            List[Component]: List of successfully parsed Component objects.
        """
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