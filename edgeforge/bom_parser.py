"""BOM Parser Agent - Parses CSV BOM files into component models."""
import csv
import pandas as pd
from pathlib import Path
from typing import List
from edgeforge.models import Component, ThermalMass


class BOMParserAgent:
    """Agent responsible for parsing BOM CSV files."""
    
    def parse_bom(self, csv_path: str) -> List[Component]:
        """
        Parse a BOM CSV file into a list of components.
        
        Expected CSV format:
        Designator,PartNumber,Type,Quantity (legacy)
        OR
        designator,mpn,package,qty,thermal_mass,component_type (new format)
        """
        print(f"🤖 BOM Parser Agent: Reading {csv_path}")
        
        # Try pandas first for new format
        try:
            df = pd.read_csv(csv_path)
            
            # Check if it's the new format
            if 'mpn' in df.columns:
                return self._parse_new_format(df)
            elif 'PartNumber' in df.columns:
                return self._parse_legacy_format_pandas(df)
        except Exception as e:
            print(f"⚠️  Pandas parsing failed, trying CSV: {e}")
        
        # Fallback to legacy CSV parsing
        return self._parse_legacy_format_csv(csv_path)
    
    def _parse_new_format(self, df: pd.DataFrame) -> List[Component]:
        """Parse new format with mpn, thermal_mass, etc."""
        components = []
        
        for idx, row in df.iterrows():
            try:
                comp = Component(
                    designator=str(row["designator"]),
                    mpn=str(row["mpn"]),
                    package=str(row["package"]),
                    qty=int(row["qty"]),
                    thermal_mass=ThermalMass(row.get("thermal_mass", "medium")),
                    component_type=str(row.get("component_type", "Unknown"))
                )
                components.append(comp)
            except Exception as e:
                print(f"⚠️  Warning: Skipping row {idx}: {e}")
        
        print(f"✅ BOM Parser Agent: Parsed {len(components)} components")
        return components
    
    def _parse_legacy_format_pandas(self, df: pd.DataFrame) -> List[Component]:
        """Parse legacy format with PartNumber."""
        components = []
        
        for idx, row in df.iterrows():
            try:
                comp = Component(
                    designator=str(row["Designator"]),
                    mpn=str(row["PartNumber"]),
                    package=row.get("Package", "Unknown"),
                    qty=int(row.get("Quantity", 1)),
                    thermal_mass=ThermalMass.MEDIUM,
                    component_type=str(row["Type"])
                )
                components.append(comp)
            except Exception as e:
                print(f"⚠️  Warning: Skipping row {idx}: {e}")
        
        print(f"✅ BOM Parser Agent: Parsed {len(components)} components (legacy format)")
        return components
    
    def _parse_legacy_format_csv(self, csv_path: str) -> List[Component]:
        """Parse legacy format using CSV reader."""
        components = []
        
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                component = Component(
                    designator=row['Designator'],
                    mpn=row['PartNumber'],
                    package=row.get('Package', 'Unknown'),
                    component_type=row['Type'],
                    qty=int(row.get('Quantity', 1)),
                    thermal_mass=ThermalMass.MEDIUM
                )
                components.append(component)
        
        print(f"✅ BOM Parser Agent: Parsed {len(components)} components (legacy CSV)")
        return components
    
    def summarize_bom(self, components: List[Component]) -> dict:
        """Generate a summary of the BOM."""
        summary = {
            'total_components': len(components),
            'types': {}
        }
        
        for comp in components:
            if comp.component_type not in summary['types']:
                summary['types'][comp.component_type] = 0
            summary['types'][comp.component_type] += comp.quantity
        
        return summary
