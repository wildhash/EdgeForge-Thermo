"""EdgeForge package initialization."""
from edgeforge.models import (
    Component,
    ThermalLimits,
    SolderPaste,
    ProfileStep,
    ReflowProfile,
    ValidationResult,
)
from edgeforge.bom_parser import BOMParserAgent
from edgeforge.limits_agent import LimitsAgent
from edgeforge.planner import PlannerAgent
from edgeforge.verifier import VerifierAgent
from edgeforge.presenter import PresenterAgent
from edgeforge.main import EdgeForge

__version__ = "1.0.0"

__all__ = [
    "Component",
    "ThermalLimits",
    "SolderPaste",
    "ProfileStep",
    "ReflowProfile",
    "ValidationResult",
    "BOMParserAgent",
    "LimitsAgent",
    "PlannerAgent",
    "VerifierAgent",
    "PresenterAgent",
    "EdgeForge",
]
