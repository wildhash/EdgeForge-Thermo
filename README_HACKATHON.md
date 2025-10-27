# 🔥 EdgeForge-Thermo

**Multi-agent AI that prevents $100K PCB failures by auto-generating perfect reflow profiles**

## The Problem
PCB manufacturers waste millions annually on failed boards due to incorrect reflow profiles. Engineers manually create profiles, risking component damage from thermal stress.

## Our Solution
EdgeForge-Thermo is a **multi-agent system** where specialized AI agents collaborate to:
1. Parse your BOM
2. Match component thermal limits
3. Design optimal temperature curves
4. Verify all constraints
5. Generate production-ready profiles

## Multi-Agent Architecture (Track 1)
Each agent is autonomous with clear expertise:
- **BOM Parser Agent**: Component identification specialist
- **Limits Agent**: Thermal constraint expert  
- **Planner Agent**: Profile optimization architect
- **Verifier Agent**: Quality assurance validator
- **Presenter Agent**: Data visualization specialist

Agents coordinate through typed interfaces (Pydantic) and make independent decisions.

## Quick Start
```bash
pip install -r requirements.txt

# Run with new orchestrator (mega prompt version)
python -m edgeforge.orchestrator

# Or run with legacy interface
python -m edgeforge.main

# Open report/index.html or output/reflow_report.html
```

## Demo Output
- Interactive temperature/time chart with phase annotations
- Validation report with constraint checks
- Production-ready profile for your oven
- Component-specific thermal limits (MPN-based)

## Features

### 🔧 Multi-Agent Architecture
- **BOM Parser Agent**: Parses CSV BOM files with pandas support
- **Limits Agent**: Maintains MPN-specific thermal database (6+ components)
- **Planner Agent**: Generates optimized temperature/time curves
- **Verifier Agent**: Validates profiles against thermal limits
- **Presenter Agent**: Creates matplotlib charts and HTML reports

### 📊 Intelligent Profile Generation
- Respects component thermal limits (max temperature, ramp rates)
- Optimizes time above liquidus (TAL) for proper solder joint formation
- Generates complete 5-stage reflow profile: Preheat → Soak → Ramp → Peak → Cool
- Validates against strictest component requirements
- MPN-based limits for precise control

### 📈 Professional Output
- Interactive matplotlib temperature/time charts
- Comprehensive HTML report with validation status, BOM, and profile details
- Visual indicators for liquidus temperature and thermal limits
- Component-specific limits table

## Data Formats

### BOM CSV Format (New)
```csv
designator,mpn,package,qty,thermal_mass,component_type
U1,STM32F405RGT6,LQFP-64,1,high,IC
C1,GRM188R71C105KA12D,0603,15,low,Capacitor
R1,RC0603FR-0710KL,0603,25,low,Resistor
```

### BOM CSV Format (Legacy)
```csv
Designator,PartNumber,Type,Quantity
U1,STM32F103C8T6,IC,1
C1,100nF-X7R-0805,Capacitor,1
R1,10K-0805,Resistor,2
```

### Solder Paste JSON Format
```json
{
  "paste_name": "SAC305",
  "liquidus_temp_c": 217.0,
  "recommended_peak_c": [235.0, 250.0],
  "preheat_target_c": 150.0,
  "soak_range_c": [150.0, 180.0],
  "soak_duration_s": [60, 120],
  "time_above_liquidus_s": [45, 90],
  "max_ramp_rate_c_per_s": 3.0,
  "cooling_rate_c_per_s": [2.0, 4.0]
}
```

## Component Limits Database

The system includes thermal specifications for:
- **STM32F405RGT6**: MCU - Max 260°C, sensitive to thermal shock
- **LM358DR**: Op-amp - Max 260°C
- **GRM188R71C105KA12D**: Ceramic cap - Max 245°C, crack sensitive
- **GRM31CR61E226KE15L**: Ceramic cap - Max 245°C
- **RC0603FR-0710KL**: Thick film resistor - Max 275°C
- **WE-PD_744043330**: Power inductor - Max 260°C, high thermal mass

## Profile Stages

1. **Preheat** (25°C → 150°C): Gradual warming to activate flux
2. **Soak** (150°C → 180°C): Slow ramp for flux activation and thermal equilibration
3. **Ramp** (180°C → Liquidus): Controlled ramp to liquidus temperature
4. **Peak** (Liquidus → Peak → Liquidus): Actual soldering phase with controlled TAL
5. **Cool** (Liquidus → 100°C): Controlled cool-down to prevent thermal shock

## Architecture

EdgeForge uses Pydantic models for type-safe data handling:
- `Component`: BOM component with thermal mass classification
- `ComponentLimit`: MPN-specific thermal constraints
- `ThermalLimits`: Type-based thermal constraints (legacy)
- `PasteProfile`: Detailed solder paste specifications
- `ReflowStep`: Individual profile stage with phase identification
- `ReflowProfile`: Complete profile with interpolation support
- `ValidationResult`: Validation outcome with violations/warnings
- `AgentContext`: Shared state between agents

## Usage Examples

### Using the Orchestrator (Recommended)
```python
from edgeforge.orchestrator import Orchestrator

orchestrator = Orchestrator()
report_path = orchestrator.run(bom_path="data/sample_bom.csv")
```

### Using Individual Agents
```python
from edgeforge import (
    BOMParserAgent, LimitsAgent, PlannerAgent,
    VerifierAgent, PresenterAgent
)

# Parse BOM
bom_parser = BOMParserAgent()
components = bom_parser.parse_bom("data/sample_bom.csv")

# Get thermal limits
limits_agent = LimitsAgent()
component_limits = limits_agent.get_limits_for_bom(components)
most_restrictive = limits_agent.get_most_restrictive(component_limits)

# Generate profile
planner = PlannerAgent()
profile = planner.plan(component_limits)

# Verify profile
verifier = VerifierAgent()
validation = verifier.verify(profile, component_limits, planner.paste_profile)

# Generate outputs
presenter = PresenterAgent(output_dir="report")
chart_path = presenter.generate_chart(profile, component_limits)
report_path = presenter.generate_report(profile, components, component_limits, validation)
```

## Testing

Run the test suite:
```bash
python tests/test_agents.py
```

Tests cover:
- BOM parsing (both formats)
- MPN-based limits matching
- Profile generation
- Validation
- Temperature interpolation

## Impact

- Prevents component damage ($50-500K per board failure)
- Reduces profile development time from hours to seconds
- Scalable to any BOM size or component database
- Production-ready profiles for immediate use

## Built for Hackathon Track 1: Multi-Agent Systems

Demonstrates real-world collective intelligence in PCB manufacturing. Each agent:
- Has autonomous decision-making capabilities
- Communicates through well-defined typed interfaces
- Contributes specialized domain expertise
- Coordinates with other agents to achieve the overall goal

The orchestrator provides thin coordination, delegating all business logic to specialized agents.

## License

MIT

## Contributing

Contributions welcome! The multi-agent architecture makes it easy to:
- Add new component types to the thermal database
- Implement alternative profile generation strategies
- Create additional output formats
- Enhance validation rules

---

**EdgeForge-Thermo** - Because your $100K PCB deserves the perfect reflow profile! 🔥
