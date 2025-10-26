"""Limits Agent - Provides thermal limits for different component types."""
from typing import Dict, Optional
from edgeforge.models import ThermalLimits


class LimitsAgent:
    """Agent responsible for maintaining thermal limit database."""
    
    def __init__(self):
        """Initialize with hardcoded thermal limits for common components."""
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
    
    def get_limits(self, component_type: str) -> Optional[ThermalLimits]:
        """Get thermal limits for a component type."""
        return self.thermal_db.get(component_type)
    
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
