"""Pydantic models for EdgeForge PCB reflow optimizer."""
from typing import List, Optional, Tuple, Literal
from pydantic import BaseModel, Field
from enum import Enum


class ThermalMass(str, Enum):
    """Thermal mass classification for components."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Component(BaseModel):
    """Component from BOM."""
    designator: str = Field(..., description="Component designator (e.g., U1, C1)")
    mpn: str = Field(..., description="Manufacturer part number")
    package: str = Field(..., description="Package type (e.g., LQFP-64, 0603)")
    qty: int = Field(default=1, ge=1)
    thermal_mass: ThermalMass = Field(default=ThermalMass.MEDIUM, description="Thermal mass category")
    component_type: str = Field(..., description="Component type (e.g., IC, Capacitor, Resistor)")
    
    # Backward compatibility aliases
    @property
    def part_number(self) -> str:
        return self.mpn
    
    @property
    def quantity(self) -> int:
        return self.qty
    
    class Config:
        use_enum_values = True


class ComponentLimit(BaseModel):
    """Thermal constraints for a specific component MPN."""
    mpn: str
    max_temp_c: float = Field(ge=200, le=300, description="Maximum temperature in °C")
    max_ramp_rate_c_per_s: float = Field(ge=0.5, le=5.0, description="Maximum ramp rate in °C/s")
    min_soak_time_s: int = Field(ge=30, le=180, description="Minimum soak time in seconds")
    min_time_above_liquidus_s: int = Field(ge=30, le=120, description="Minimum time above liquidus in seconds")
    notes: str = ""


class ThermalLimits(BaseModel):
    """Thermal limits for a component type (legacy support)."""
    component_type: str
    max_temp: float = Field(..., description="Maximum temperature in °C")
    max_ramp_up: float = Field(..., description="Maximum ramp up rate in °C/s")
    max_ramp_down: float = Field(..., description="Maximum ramp down rate in °C/s")
    min_time_above_liquidus: float = Field(..., description="Minimum time above liquidus in seconds")
    max_time_above_liquidus: float = Field(..., description="Maximum time above liquidus in seconds")


class PasteProfile(BaseModel):
    """Solder paste specifications with detailed constraints."""
    paste_name: str
    liquidus_temp_c: float
    recommended_peak_c: Tuple[float, float]
    preheat_target_c: float
    soak_range_c: Tuple[float, float]
    soak_duration_s: Tuple[int, int]
    time_above_liquidus_s: Tuple[int, int]
    max_ramp_rate_c_per_s: float
    cooling_rate_c_per_s: Tuple[float, float]


class SolderPaste(BaseModel):
    """Solder paste specifications (legacy support)."""
    name: str
    alloy: str
    liquidus_temp: float = Field(..., description="Liquidus temperature in °C")
    peak_temp_range: tuple[float, float] = Field(..., description="Peak temperature range (min, max) in °C")


class ReflowStep(BaseModel):
    """Single segment of reflow profile."""
    phase: Literal["preheat", "soak", "ramp_to_peak", "reflow", "cooling"]
    start_time_s: int
    end_time_s: int
    start_temp_c: float
    end_temp_c: float
    
    @property
    def duration_s(self) -> int:
        return self.end_time_s - self.start_time_s
    
    @property
    def ramp_rate_c_per_s(self) -> float:
        if self.duration_s == 0:
            return 0.0
        return abs(self.end_temp_c - self.start_temp_c) / self.duration_s


class ProfileStep(BaseModel):
    """A step in the reflow profile (legacy support)."""
    name: str = Field(..., description="Step name (preheat, soak, ramp, peak, cool)")
    start_temp: float = Field(..., description="Starting temperature in °C")
    end_temp: float = Field(..., description="Ending temperature in °C")
    duration: float = Field(..., description="Duration in seconds")
    ramp_rate: float = Field(..., description="Ramp rate in °C/s")


class ReflowProfile(BaseModel):
    """Complete reflow profile."""
    profile_id: str
    steps: List[ReflowStep]
    peak_temp_c: float
    time_above_liquidus_s: int
    total_duration_s: int
    
    def get_temp_at_time(self, t: int) -> float:
        """Linear interpolation for any time point."""
        for step in self.steps:
            if step.start_time_s <= t <= step.end_time_s:
                progress = (t - step.start_time_s) / max(1, step.duration_s)
                return step.start_temp_c + progress * (step.end_temp_c - step.start_temp_c)
        return self.steps[-1].end_temp_c if self.steps else 25.0
    
    # Legacy support
    @property
    def total_time(self) -> float:
        return float(self.total_duration_s)
    
    @property
    def time_above_liquidus(self) -> float:
        return float(self.time_above_liquidus_s)


class ValidationResult(BaseModel):
    """Result of profile validation."""
    passed: bool
    violations: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    metrics: dict = Field(default_factory=dict)
    
    # Legacy support
    @property
    def valid(self) -> bool:
        return self.passed


class AgentContext(BaseModel):
    """Shared state between agents."""
    bom_components: List[Component] = []
    component_limits: List[ComponentLimit] = []
    paste_profile: Optional[PasteProfile] = None
    proposed_profile: Optional[ReflowProfile] = None
    validation: Optional[ValidationResult] = None
