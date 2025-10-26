"""BOM Parser Agent - Parses CSV BOM files into component models."""
import csv
from pathlib import Path
from typing import List
from edgeforge.models import Component


class BOMParserAgent:
    """Agent responsible for parsing BOM CSV files."""
    
    def parse_bom(self, csv_path: str) -> List[Component]:
        """
        Parse a BOM CSV file into a list of components.
        
        Expected CSV format:
        Designator,PartNumber,Type,Quantity
        """
        components = []
        
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                component = Component(
                    designator=row['Designator'],
                    part_number=row['PartNumber'],
                    component_type=row['Type'],
                    quantity=int(row.get('Quantity', 1))
                )
                components.append(component)
        
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
