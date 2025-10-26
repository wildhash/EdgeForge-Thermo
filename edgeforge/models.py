"""Pydantic models for EdgeForge PCB reflow optimizer."""
from typing import List, Optional
from pydantic import BaseModel, Field


class Component(BaseModel):
    """Component from BOM."""
    designator: str = Field(..., description="Component designator (e.g., U1, C1)")
    part_number: str = Field(..., description="Part number")
    component_type: str = Field(..., description="Component type (e.g., IC, capacitor, resistor)")
    quantity: int = Field(default=1, ge=1)


class ThermalLimits(BaseModel):
    """Thermal limits for a component type."""
    component_type: str
    max_temp: float = Field(..., description="Maximum temperature in °C")
    max_ramp_up: float = Field(..., description="Maximum ramp up rate in °C/s")
    max_ramp_down: float = Field(..., description="Maximum ramp down rate in °C/s")
    min_time_above_liquidus: float = Field(..., description="Minimum time above liquidus in seconds")
    max_time_above_liquidus: float = Field(..., description="Maximum time above liquidus in seconds")


class SolderPaste(BaseModel):
    """Solder paste specifications."""
    name: str
    alloy: str
    liquidus_temp: float = Field(..., description="Liquidus temperature in °C")
    peak_temp_range: tuple[float, float] = Field(..., description="Peak temperature range (min, max) in °C")


class ProfileStep(BaseModel):
    """A step in the reflow profile."""
    name: str = Field(..., description="Step name (preheat, soak, ramp, peak, cool)")
    start_temp: float = Field(..., description="Starting temperature in °C")
    end_temp: float = Field(..., description="Ending temperature in °C")
    duration: float = Field(..., description="Duration in seconds")
    ramp_rate: float = Field(..., description="Ramp rate in °C/s")


class ReflowProfile(BaseModel):
    """Complete reflow profile."""
    paste: SolderPaste
    steps: List[ProfileStep]
    total_time: float = Field(..., description="Total profile time in seconds")
    time_above_liquidus: float = Field(..., description="Time above liquidus in seconds")


class ValidationResult(BaseModel):
    """Result of profile validation."""
    valid: bool
    violations: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
