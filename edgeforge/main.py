"""EdgeForge Main Orchestrator - Coordinates all agents."""
import json
from pathlib import Path
from edgeforge.models import SolderPaste
from edgeforge.bom_parser import BOMParserAgent
from edgeforge.limits_agent import LimitsAgent
from edgeforge.planner import PlannerAgent
from edgeforge.verifier import VerifierAgent
from edgeforge.presenter import PresenterAgent


class EdgeForge:
    """Main orchestrator for the multi-agent PCB reflow optimizer."""
    
    def __init__(self):
        """Initialize all agents."""
        self.bom_parser = BOMParserAgent()
        self.limits_agent = LimitsAgent()
        self.planner = PlannerAgent()
        self.verifier = VerifierAgent()
        self.presenter = PresenterAgent()
    
    def optimize_reflow_profile(
        self,
        bom_csv_path: str,
        paste_json_path: str,
        output_dir: str = "output"
    ):
        """
        Run the complete optimization process.
        
        Args:
            bom_csv_path: Path to BOM CSV file
            paste_json_path: Path to solder paste JSON file
            output_dir: Directory for output files
        """
        print("🔧 EdgeForge PCB Reflow Optimizer")
        print("=" * 60)
        
        # Step 1: Parse BOM
        print("\n📋 Step 1: Parsing BOM...")
        components = self.bom_parser.parse_bom(bom_csv_path)
        summary = self.bom_parser.summarize_bom(components)
        print(f"   Found {summary['total_components']} components")
        for comp_type, count in summary['types'].items():
            print(f"   - {comp_type}: {count}")
        
        # Step 2: Get thermal limits
        print("\n🌡️  Step 2: Retrieving thermal limits...")
        component_types = list(set(comp.component_type for comp in components))
        limits = self.limits_agent.get_strictest_limits(component_types)
        print(f"   Max temperature: {limits.max_temp}°C")
        print(f"   Max ramp up: {limits.max_ramp_up}°C/s")
        print(f"   Max ramp down: {limits.max_ramp_down}°C/s")
        print(f"   TAL range: {limits.min_time_above_liquidus}-{limits.max_time_above_liquidus}s")
        
        # Step 3: Load paste specifications
        print("\n🧪 Step 3: Loading solder paste specs...")
        with open(paste_json_path, 'r') as f:
            paste_data = json.load(f)
        paste = SolderPaste(**paste_data)
        print(f"   Paste: {paste.name}")
        print(f"   Alloy: {paste.alloy}")
        print(f"   Liquidus: {paste.liquidus_temp}°C")
        print(f"   Peak range: {paste.peak_temp_range[0]}-{paste.peak_temp_range[1]}°C")
        
        # Step 4: Generate profile
        print("\n📊 Step 4: Generating optimized profile...")
        profile = self.planner.generate_profile(paste, limits)
        print(f"   Profile generated with {len(profile.steps)} steps")
        print(f"   Total time: {profile.total_time:.1f}s ({profile.total_time/60:.1f} min)")
        print(f"   Time above liquidus: {profile.time_above_liquidus:.1f}s")
        
        # Step 5: Verify profile
        print("\n✅ Step 5: Verifying profile...")
        validation = self.verifier.verify_profile(profile, limits)
        if validation.valid:
            print("   ✓ Profile is VALID - all thermal limits respected!")
        else:
            print("   ✗ Profile has VIOLATIONS:")
            for violation in validation.violations:
                print(f"      - {violation}")
        
        if validation.warnings:
            print("   ⚠️  Warnings:")
            for warning in validation.warnings:
                print(f"      - {warning}")
        
        # Step 6: Generate outputs
        print("\n📈 Step 6: Generating outputs...")
        self.presenter.output_dir = Path(output_dir)
        self.presenter.output_dir.mkdir(exist_ok=True)
        
        chart_path = self.presenter.generate_chart(profile, limits)
        print(f"   Chart saved to: {chart_path}")
        
        report_path = self.presenter.generate_report(
            profile, components, limits, validation
        )
        print(f"   Report saved to: {report_path}")
        
        print("\n" + "=" * 60)
        print("✨ Optimization complete!")
        print(f"📂 Results available in: {output_dir}/")
        
        return profile, validation


def main():
    """Main entry point."""
    # Create EdgeForge instance
    forge = EdgeForge()
    
    # Run optimization with demo data
    profile, validation = forge.optimize_reflow_profile(
        bom_csv_path="data/demo_bom.csv",
        paste_json_path="data/sac305_paste.json",
        output_dir="output"
    )
    
    # Print profile steps
    print("\n📋 Profile Steps:")
    print("-" * 80)
    print(f"{'Step':<12} {'Start':<10} {'End':<10} {'Duration':<12} {'Ramp Rate':<12}")
    print("-" * 80)
    for step in profile.steps:
        # Handle both ReflowStep and ProfileStep
        name = getattr(step, 'phase', getattr(step, 'name', 'unknown'))
        start_temp = getattr(step, 'start_temp_c', getattr(step, 'start_temp', 0))
        end_temp = getattr(step, 'end_temp_c', getattr(step, 'end_temp', 0))
        duration = getattr(step, 'duration_s', getattr(step, 'duration', 0))
        ramp_rate = getattr(step, 'ramp_rate_c_per_s', getattr(step, 'ramp_rate', 0))
        
        print(f"{name:<12} {start_temp:>6.1f}°C  {end_temp:>6.1f}°C  "
              f"{duration:>8.1f}s    {ramp_rate:>8.2f}°C/s")
    print("-" * 80)


if __name__ == "__main__":
    main()
