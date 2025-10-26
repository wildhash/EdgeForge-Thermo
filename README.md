# EdgeForge-Thermo

EdgeForge-Thermo: Multi-agent AI that reads your PCB BOM and auto-generates the perfect reflow oven profile—agents coordinate to respect component thermal limits, optimize energy, and prevent $100K board failures.

## Features

🔧 **Multi-Agent Architecture**:
- **BOM Parser Agent**: Parses CSV BOM files into component models
- **Limits Agent**: Maintains hardcoded thermal database for 5+ component types (ICs, capacitors, resistors, inductors, connectors)
- **Planner Agent**: Generates optimized temperature/time curves with all reflow stages (preheat, soak, ramp, peak, TAL, cool)
- **Verifier Agent**: Validates profiles against thermal limits (max temp, ramp rates, time above liquidus)
- **Presenter Agent**: Creates matplotlib charts and HTML reports

📊 **Intelligent Profile Generation**:
- Respects component thermal limits (max temperature, ramp rates)
- Optimizes time above liquidus (TAL) for proper solder joint formation
- Generates complete 5-stage reflow profile: Preheat → Soak → Ramp → Peak → Cool
- Validates against strictest component requirements

📈 **Professional Output**:
- Interactive matplotlib temperature/time charts with shaded regions
- Comprehensive HTML report with validation status, BOM, and profile details
- Visual indicators for liquidus temperature and thermal limits

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

Run the demo with included sample data:

```bash
python -m edgeforge.main
```

This will:
1. Parse the demo BOM (STM32, capacitors, resistors, etc.)
2. Load SAC305 solder paste specifications
3. Generate an optimized reflow profile
4. Validate against thermal limits
5. Create chart and HTML report in `output/` directory

## Usage

### Using the Main Orchestrator

```python
from edgeforge import EdgeForge

# Create optimizer instance
forge = EdgeForge()

# Run optimization
profile, validation = forge.optimize_reflow_profile(
    bom_csv_path="data/demo_bom.csv",
    paste_json_path="data/sac305_paste.json",
    output_dir="output"
)
```

### Using Individual Agents

```python
from edgeforge import (
    BOMParserAgent, LimitsAgent, PlannerAgent,
    VerifierAgent, PresenterAgent, SolderPaste
)

# Parse BOM
bom_parser = BOMParserAgent()
components = bom_parser.parse_bom("data/demo_bom.csv")

# Get thermal limits
limits_agent = LimitsAgent()
component_types = [c.component_type for c in components]
limits = limits_agent.get_strictest_limits(component_types)

# Generate profile
planner = PlannerAgent()
paste = SolderPaste(
    name="SAC305",
    alloy="Sn96.5/Ag3.0/Cu0.5",
    liquidus_temp=217.0,
    peak_temp_range=(240.0, 250.0)
)
profile = planner.generate_profile(paste, limits)

# Verify profile
verifier = VerifierAgent()
validation = verifier.verify_profile(profile, limits)

# Generate outputs
presenter = PresenterAgent(output_dir="output")
chart_path = presenter.generate_chart(profile, limits)
report_path = presenter.generate_report(profile, components, limits, validation)
```

## Data Formats

### BOM CSV Format

```csv
Designator,PartNumber,Type,Quantity
U1,STM32F103C8T6,IC,1
C1,100nF-X7R-0805,Capacitor,1
R1,10K-0805,Resistor,2
```

### Solder Paste JSON Format

```json
{
  "name": "SAC305 Solder Paste",
  "alloy": "Sn96.5/Ag3.0/Cu0.5",
  "liquidus_temp": 217.0,
  "peak_temp_range": [240.0, 250.0]
}
```

## Supported Component Types

The Limits Agent includes thermal specifications for:
- **IC**: Max 260°C, 3.0°C/s ramp up, 4.0°C/s ramp down
- **Capacitor**: Max 245°C, 2.5°C/s ramp up, 3.5°C/s ramp down
- **Resistor**: Max 270°C, 4.0°C/s ramp up, 5.0°C/s ramp down
- **Inductor**: Max 250°C, 3.0°C/s ramp up, 4.0°C/s ramp down
- **Connector**: Max 240°C, 2.0°C/s ramp up, 3.0°C/s ramp down

## Profile Stages

1. **Preheat** (25°C → 150°C): Gradual warming to activate flux
2. **Soak** (150°C → 180°C): Slow ramp for flux activation and thermal equilibration
3. **Ramp** (180°C → Liquidus): Controlled ramp to liquidus temperature
4. **Peak** (Liquidus → Peak → Liquidus): Actual soldering phase with controlled TAL
5. **Cool** (Liquidus → 100°C): Controlled cool-down to prevent thermal shock

## Output

The optimizer generates:
- **reflow_profile.png**: Temperature vs. time chart with stage annotations
- **reflow_report.html**: Comprehensive report with validation, specs, BOM, and embedded chart

## Example Output

![Reflow Profile Report](https://github.com/user-attachments/assets/0ac61c40-b3e0-4205-9cab-2ad65f9d78c4)

## Architecture

EdgeForge uses Pydantic models for type-safe data handling:
- `Component`: BOM component representation
- `ThermalLimits`: Thermal constraints for components
- `SolderPaste`: Paste specifications
- `ProfileStep`: Individual profile stage
- `ReflowProfile`: Complete profile with all steps
- `ValidationResult`: Validation outcome with violations/warnings

## License

MIT

## Contributing

Contributions welcome! The multi-agent architecture makes it easy to:
- Add new component types to the thermal database
- Implement alternative profile generation strategies
- Create additional output formats
- Enhance validation rules

---

**EdgeForge** - Because your $100K PCB deserves the perfect reflow profile! 🔥
