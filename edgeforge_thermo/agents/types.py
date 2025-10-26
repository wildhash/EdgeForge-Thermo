from pydantic import BaseModel, Field
from typing import List, Tuple, Literal
from enum import Enum

class ThermalMass(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Component(BaseModel):
    """BOM line item"""
    designator: str
    mpn: str
    package: str
    qty: int
    thermal_mass: ThermalMass
    component_type: str

    class Config:
        use_enum_values = True

class ComponentLimit(BaseModel):
    """Thermal constraints for a component"""
    mpn: str
    max_temp_c: float = Field(ge=200, le=300)
    max_ramp_rate_c_per_s: float = Field(ge=0.5, le=5.0)
    min_soak_time_s: int = Field(ge=30, le=180)
    min_time_above_liquidus_s: int = Field(ge=30, le=120)
    notes: str = ""

class PasteProfile(BaseModel):
    """Solder paste specifications"""
    paste_name: str
    liquidus_temp_c: float
    recommended_peak_c: Tuple[float, float]
    preheat_target_c: float
    soak_range_c: Tuple[float, float]
    soak_duration_s: Tuple[int, int]
    time_above_liquidus_s: Tuple[int, int]
    max_ramp_rate_c_per_s: float
    cooling_rate_c_per_s: Tuple[float, float]

class ReflowStep(BaseModel):
    """Single segment of reflow profile"""
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

class ReflowProfile(BaseModel):
    """Complete reflow profile"""
    profile_id: str
    steps: List[ReflowStep]
    peak_temp_c: float
    time_above_liquidus_s: int
    total_duration_s: int

    def get_temp_at_time(self, t: int) -> float:
        """Linear interpolation for any time point"""
        for step in self.steps:
            if step.start_time_s <= t <= step.end_time_s:
                progress = (t - step.start_time_s) / max(1, step.duration_s)
                return step.start_temp_c + progress * (step.end_temp_c - step.start_temp_c)
        return self.steps[-1].end_temp_c

class ValidationResult(BaseModel):
    """Verification output"""
    passed: bool
    violations: List[str] = []
    warnings: List[str] = []
    metrics: dict = {}

class AgentContext(BaseModel):
    """Shared state between agents"""
    bom_components: List[Component] = []
    component_limits: List[ComponentLimit] = []
    paste_profile: PasteProfile | None = None
    proposed_profile: ReflowProfile | None = None
    validation: ValidationResult | None = None
