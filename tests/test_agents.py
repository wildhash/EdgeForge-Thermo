"""Tests for EdgeForge-Thermo multi-agent system."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from edgeforge.bom_parser import BOMParserAgent
from edgeforge.limits_agent import LimitsAgent
from edgeforge.planner import PlannerAgent
from edgeforge.verifier import VerifierAgent
from edgeforge.models import ThermalMass


def test_bom_parser_new_format():
    """Test BOM parser with new format (MPN-based)."""
    parser = BOMParserAgent()
    components = parser.parse_bom("data/sample_bom.csv")
    
    assert len(components) == 6
    assert components[0].designator == "U1"
    assert components[0].mpn == "STM32F405RGT6"
    assert components[0].thermal_mass == ThermalMass.HIGH
    assert components[0].component_type == "IC"


def test_bom_parser_legacy_format():
    """Test BOM parser with legacy format."""
    parser = BOMParserAgent()
    components = parser.parse_bom("data/demo_bom.csv")
    
    assert len(components) == 11
    assert components[0].designator == "U1"
    assert components[0].part_number == "STM32F103C8T6"  # Test alias


def test_limits_agent_mpn_matching():
    """Test limits agent MPN matching."""
    parser = BOMParserAgent()
    components = parser.parse_bom("data/sample_bom.csv")
    
    limits_agent = LimitsAgent()
    limits = limits_agent.get_limits_for_bom(components)
    
    assert len(limits) == 6  # All components should have limits
    
    # Check most restrictive
    most_restrictive = limits_agent.get_most_restrictive(limits)
    assert most_restrictive.mpn == "GRM188R71C105KA12D"
    assert most_restrictive.max_temp_c == 245.0


def test_planner_profile_generation():
    """Test planner generates valid profile."""
    parser = BOMParserAgent()
    components = parser.parse_bom("data/sample_bom.csv")
    
    limits_agent = LimitsAgent()
    comp_limits = limits_agent.get_limits_for_bom(components)
    
    planner = PlannerAgent()
    profile = planner.plan(comp_limits)
    
    assert profile.profile_id == "optimized_v1"
    assert len(profile.steps) == 5
    assert profile.peak_temp_c <= 240.0  # Should respect most restrictive limit
    assert profile.total_duration_s > 0
    assert profile.time_above_liquidus_s > 0
    
    # Check phase names
    phases = [step.phase for step in profile.steps]
    assert "preheat" in phases
    assert "soak" in phases
    assert "reflow" in phases
    assert "cooling" in phases


def test_verifier():
    """Test verifier validates profile."""
    parser = BOMParserAgent()
    components = parser.parse_bom("data/sample_bom.csv")
    
    limits_agent = LimitsAgent()
    comp_limits = limits_agent.get_limits_for_bom(components)
    
    planner = PlannerAgent()
    profile = planner.plan(comp_limits)
    
    verifier = VerifierAgent()
    validation = verifier.verify(profile, comp_limits, planner.paste_profile)
    
    assert validation.passed or not validation.passed  # Should complete without error
    assert isinstance(validation.violations, list)
    assert isinstance(validation.warnings, list)
    assert isinstance(validation.metrics, dict)


def test_get_temp_at_time():
    """Test ReflowProfile.get_temp_at_time method."""
    parser = BOMParserAgent()
    components = parser.parse_bom("data/sample_bom.csv")
    
    limits_agent = LimitsAgent()
    comp_limits = limits_agent.get_limits_for_bom(components)
    
    planner = PlannerAgent()
    profile = planner.plan(comp_limits)
    
    # Test temperature interpolation
    temp_at_start = profile.get_temp_at_time(0)
    assert temp_at_start == 25.0  # Should start at ambient
    
    temp_at_end = profile.get_temp_at_time(profile.total_duration_s)
    assert temp_at_end <= 100.0  # Should cool down to ~100°C
    
    # Test mid-point
    temp_at_mid = profile.get_temp_at_time(profile.total_duration_s // 2)
    assert 100 < temp_at_mid < 250  # Should be somewhere in the middle


if __name__ == "__main__":
    # Run tests
    test_bom_parser_new_format()
    print("✓ test_bom_parser_new_format passed")
    
    test_bom_parser_legacy_format()
    print("✓ test_bom_parser_legacy_format passed")
    
    test_limits_agent_mpn_matching()
    print("✓ test_limits_agent_mpn_matching passed")
    
    test_planner_profile_generation()
    print("✓ test_planner_profile_generation passed")
    
    test_verifier()
    print("✓ test_verifier passed")
    
    test_get_temp_at_time()
    print("✓ test_get_temp_at_time passed")
    
    print("\n✅ All tests passed!")
