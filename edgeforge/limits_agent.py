"""Limits Agent - Provides thermal limits for different component types and MPNs."""
import json
from pathlib import Path
from typing import Dict, Optional, List
from edgeforge.models import ThermalLimits, ComponentLimit, Component


class LimitsAgent:
    """Agent responsible for maintaining thermal limit database."""
    
    def __init__(self, limits_db_path: Optional[str] = None):
        """Initialize with hardcoded thermal limits for common components."""
        # Type-based limits (legacy)
        self.thermal_db: Dict[str, ThermalLimits] = {
            'IC': ThermalLimits(
                component_type='IC',
                max_temp=260.0,
                max_ramp_up=3.0,
                max_ramp_down=4.0,
                min_time_above_liquidus=60.0,
                max_time_above_liquidus=120.0
            ),
            'Capacitor': ThermalLimits(
                component_type='Capacitor',
                max_temp=245.0,
                max_ramp_up=2.5,
                max_ramp_down=3.5,
                min_time_above_liquidus=60.0,
                max_time_above_liquidus=100.0
            ),
            'Resistor': ThermalLimits(
                component_type='Resistor',
                max_temp=270.0,
                max_ramp_up=4.0,
                max_ramp_down=5.0,
                min_time_above_liquidus=60.0,
                max_time_above_liquidus=120.0
            ),
            'Inductor': ThermalLimits(
                component_type='Inductor',
                max_temp=250.0,
                max_ramp_up=3.0,
                max_ramp_down=4.0,
                min_time_above_liquidus=60.0,
                max_time_above_liquidus=110.0
            ),
            'Connector': ThermalLimits(
                component_type='Connector',
                max_temp=240.0,
                max_ramp_up=2.0,
                max_ramp_down=3.0,
                min_time_above_liquidus=60.0,
                max_time_above_liquidus=100.0
            )
        }
        
        # MPN-based limits database (new)
        self.mpn_db: Dict[str, dict] = {}
        if limits_db_path is None:
            limits_db_path = "data/limits_database.json"
        
        try:
            with open(limits_db_path, 'r') as f:
                self.mpn_db = json.load(f)
            print(f"🤖 Limits Agent: Loaded {len(self.mpn_db)} component specs from database")
        except FileNotFoundError:
            print(f"⚠️  Limits Agent: MPN database not found at {limits_db_path}, using type-based limits only")
    
    def get_limits(self, component_type: str) -> Optional[ThermalLimits]:
        """Get thermal limits for a component type."""
        return self.thermal_db.get(component_type)
    
    def get_limits_for_bom(self, components: List[Component]) -> List[ComponentLimit]:
        """Match BOM components to thermal limits database."""
        limits = []
        coverage = 0
        
        for comp in components:
            if comp.mpn in self.mpn_db:
                data = self.mpn_db[comp.mpn]
                limit = ComponentLimit(
                    mpn=comp.mpn,
                    max_temp_c=data["max_temp_c"],
                    max_ramp_rate_c_per_s=data["max_ramp_rate_c_per_s"],
                    min_soak_time_s=data["min_soak_time_s"],
                    min_time_above_liquidus_s=data["min_time_above_liquidus_s"],
                    notes=data.get("notes", "")
                )
                limits.append(limit)
                coverage += 1
        
        cov_pct = (coverage / len(components)) * 100 if components else 0
        print(f"✅ Limits Agent: Matched {coverage}/{len(components)} components ({cov_pct:.0f}% coverage)")
        
        return limits
    
    def get_most_restrictive(self, limits: List[ComponentLimit]) -> ComponentLimit:
        """Find the most thermally sensitive component."""
        if not limits:
            raise ValueError("No component limits provided")
        
        most_restrictive = min(limits, key=lambda x: x.max_temp_c)
        print(f"🎯 Limits Agent: Most restrictive component is {most_restrictive.mpn} "
              f"(Tmax={most_restrictive.max_temp_c}°C)")
        return most_restrictive
    
    def get_strictest_limits(self, component_types: list[str]) -> ThermalLimits:
        """
        Get the strictest thermal limits across multiple component types.
        This ensures the profile respects all components.
        """
        limits_list = [self.get_limits(ct) for ct in component_types if self.get_limits(ct)]
        
        if not limits_list:
            # Default conservative limits
            return ThermalLimits(
                component_type='Default',
                max_temp=240.0,
                max_ramp_up=2.0,
                max_ramp_down=3.0,
                min_time_above_liquidus=60.0,
                max_time_above_liquidus=100.0
            )
        
        # Take the most conservative limit for each parameter
        return ThermalLimits(
            component_type='Combined',
            max_temp=min(l.max_temp for l in limits_list),
            max_ramp_up=min(l.max_ramp_up for l in limits_list),
            max_ramp_down=min(l.max_ramp_down for l in limits_list),
            min_time_above_liquidus=max(l.min_time_above_liquidus for l in limits_list),
            max_time_above_liquidus=min(l.max_time_above_liquidus for l in limits_list)
        )
