#!/usr/bin/env python3
"""
EdgeForge Demo Script - Interactive demonstration of the PCB reflow optimizer
"""
from edgeforge import EdgeForge

def main():
    print("=" * 70)
    print("  EdgeForge PCB Reflow Optimizer - Demo")
    print("=" * 70)
    print("\nThis demo will:")
    print("  1. Parse a sample BOM with STM32, capacitors, resistors, etc.")
    print("  2. Load SAC305 solder paste specifications")
    print("  3. Generate an optimized reflow profile")
    print("  4. Validate thermal constraints")
    print("  5. Create visual outputs")
    print("\n" + "-" * 70)
    
    input("\nPress Enter to start the optimization...")
    
    # Run the optimizer
    forge = EdgeForge()
    profile, validation = forge.optimize_reflow_profile(
        bom_csv_path="data/demo_bom.csv",
        paste_json_path="data/sac305_paste.json",
        output_dir="output"
    )
    
    # Summary
    print("\n" + "=" * 70)
    print("  Summary")
    print("=" * 70)
    print(f"\n✓ Profile Status: {'VALID ✓' if validation.valid else 'INVALID ✗'}")
    print(f"✓ Total Time: {profile.total_time:.1f}s ({profile.total_time/60:.1f} minutes)")
    print(f"✓ Peak Temperature: {max(s.end_temp for s in profile.steps):.1f}°C")
    print(f"✓ Time Above Liquidus: {profile.time_above_liquidus:.1f}s")
    print(f"✓ Profile Stages: {len(profile.steps)}")
    
    if validation.warnings:
        print(f"\n⚠️  Warnings: {len(validation.warnings)}")
    
    print("\n📂 Output files created:")
    print("   • output/reflow_profile.png - Temperature/time chart")
    print("   • output/reflow_report.html - Comprehensive HTML report")
    
    print("\n" + "=" * 70)
    print("  Demo complete! Open the HTML report to see detailed results.")
    print("=" * 70)

if __name__ == "__main__":
    main()
