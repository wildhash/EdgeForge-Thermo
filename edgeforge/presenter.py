"""Presenter Agent - Generates visualizations and reports."""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import List
from edgeforge.models import ReflowProfile, Component, ThermalLimits, ValidationResult


class PresenterAgent:
    """Agent responsible for generating charts and reports."""
    
    def __init__(self, output_dir: str = "output"):
        """Initialize presenter with output directory."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_chart(
        self,
        profile: ReflowProfile,
        limits: ThermalLimits,
        filename: str = "reflow_profile.png"
    ) -> str:
        """
        Generate an interactive matplotlib chart of the reflow profile.
        
        Returns the path to the saved chart.
        """
        # Generate time series data from profile steps
        time_points = [0]
        temp_points = [profile.steps[0].start_temp]
        
        cumulative_time = 0
        for step in profile.steps:
            cumulative_time += step.duration
            time_points.append(cumulative_time)
            temp_points.append(step.end_temp)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # Plot temperature profile
        ax.plot(time_points, temp_points, 'b-', linewidth=2, label='Temperature Profile')
        
        # Add liquidus line
        liquidus = profile.paste.liquidus_temp
        ax.axhline(y=liquidus, color='r', linestyle='--', linewidth=1.5, 
                   label=f'Liquidus ({liquidus}°C)')
        
        # Add max temp line
        ax.axhline(y=limits.max_temp, color='orange', linestyle='--', linewidth=1.5,
                   label=f'Max Temp Limit ({limits.max_temp}°C)')
        
        # Shade regions
        cumulative_time = 0
        colors = ['lightblue', 'lightgreen', 'lightyellow', 'lightcoral', 'lightgray']
        
        for i, step in enumerate(profile.steps):
            start_time = cumulative_time
            end_time = cumulative_time + step.duration
            
            # Get temperature range for this step
            temp_range = [step.start_temp, step.end_temp]
            
            ax.axvspan(start_time, end_time, alpha=0.2, color=colors[i % len(colors)])
            
            # Add step label
            mid_time = (start_time + end_time) / 2
            mid_temp = (step.start_temp + step.end_temp) / 2
            ax.text(mid_time, mid_temp, step.name, 
                   horizontalalignment='center', fontsize=9, fontweight='bold')
            
            cumulative_time = end_time
        
        # Labels and formatting
        ax.set_xlabel('Time (seconds)', fontsize=12)
        ax.set_ylabel('Temperature (°C)', fontsize=12)
        ax.set_title(f'Reflow Profile - {profile.paste.name} ({profile.paste.alloy})', 
                     fontsize=14, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Save figure
        output_path = self.output_dir / filename
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def generate_report(
        self,
        profile: ReflowProfile,
        components: List[Component],
        limits: ThermalLimits,
        validation: ValidationResult,
        filename: str = "reflow_report.html"
    ) -> str:
        """
        Generate an HTML report with profile details.
        
        Returns the path to the saved report.
        """
        # Build HTML content
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>EdgeForge Reflow Profile Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .section {{
            background-color: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{ margin: 0; }}
        h2 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}
        th, td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .valid {{ color: green; font-weight: bold; }}
        .invalid {{ color: red; font-weight: bold; }}
        .warning {{ color: orange; }}
        .violation {{ color: red; }}
        ul {{ list-style-type: none; padding-left: 0; }}
        li {{ padding: 5px 0; }}
        .chart {{ text-align: center; margin: 20px 0; }}
        .chart img {{ max-width: 100%; height: auto; border: 1px solid #ddd; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔥 EdgeForge Reflow Profile Report</h1>
        <p>Multi-Agent PCB Reflow Optimizer</p>
    </div>
    
    <div class="section">
        <h2>Validation Status</h2>
        <p class="{'valid' if validation.valid else 'invalid'}">
            {'✓ Profile is VALID - All thermal limits respected' if validation.valid else '✗ Profile has VIOLATIONS - See details below'}
        </p>
        
        {f'''
        <h3>Violations:</h3>
        <ul>
            {''.join(f'<li class="violation">❌ {v}</li>' for v in validation.violations)}
        </ul>
        ''' if validation.violations else ''}
        
        {f'''
        <h3>Warnings:</h3>
        <ul>
            {''.join(f'<li class="warning">⚠️ {w}</li>' for w in validation.warnings)}
        </ul>
        ''' if validation.warnings else ''}
    </div>
    
    <div class="section">
        <h2>Solder Paste Specifications</h2>
        <table>
            <tr><th>Property</th><th>Value</th></tr>
            <tr><td>Name</td><td>{profile.paste.name}</td></tr>
            <tr><td>Alloy</td><td>{profile.paste.alloy}</td></tr>
            <tr><td>Liquidus Temperature</td><td>{profile.paste.liquidus_temp}°C</td></tr>
            <tr><td>Peak Temperature Range</td><td>{profile.paste.peak_temp_range[0]}°C - {profile.paste.peak_temp_range[1]}°C</td></tr>
        </table>
    </div>
    
    <div class="section">
        <h2>Thermal Limits (Strictest)</h2>
        <table>
            <tr><th>Parameter</th><th>Limit</th></tr>
            <tr><td>Maximum Temperature</td><td>{limits.max_temp}°C</td></tr>
            <tr><td>Max Ramp Up Rate</td><td>{limits.max_ramp_up}°C/s</td></tr>
            <tr><td>Max Ramp Down Rate</td><td>{limits.max_ramp_down}°C/s</td></tr>
            <tr><td>Min Time Above Liquidus</td><td>{limits.min_time_above_liquidus}s</td></tr>
            <tr><td>Max Time Above Liquidus</td><td>{limits.max_time_above_liquidus}s</td></tr>
        </table>
    </div>
    
    <div class="section">
        <h2>Profile Steps</h2>
        <table>
            <tr>
                <th>Step</th>
                <th>Start Temp</th>
                <th>End Temp</th>
                <th>Duration</th>
                <th>Ramp Rate</th>
            </tr>
            {''.join(f'''
            <tr>
                <td>{step.name}</td>
                <td>{step.start_temp:.1f}°C</td>
                <td>{step.end_temp:.1f}°C</td>
                <td>{step.duration:.1f}s</td>
                <td>{step.ramp_rate:.2f}°C/s</td>
            </tr>
            ''' for step in profile.steps)}
        </table>
        <p><strong>Total Time:</strong> {profile.total_time:.1f}s ({profile.total_time/60:.1f} minutes)</p>
        <p><strong>Time Above Liquidus:</strong> {profile.time_above_liquidus:.1f}s</p>
    </div>
    
    <div class="section">
        <h2>Bill of Materials</h2>
        <table>
            <tr>
                <th>Designator</th>
                <th>Part Number</th>
                <th>Type</th>
                <th>Quantity</th>
            </tr>
            {''.join(f'''
            <tr>
                <td>{comp.designator}</td>
                <td>{comp.part_number}</td>
                <td>{comp.component_type}</td>
                <td>{comp.quantity}</td>
            </tr>
            ''' for comp in components)}
        </table>
    </div>
    
    <div class="section">
        <h2>Temperature Profile Chart</h2>
        <div class="chart">
            <img src="reflow_profile.png" alt="Reflow Profile Chart">
        </div>
    </div>
    
    <div class="section">
        <p style="text-align: center; color: #7f8c8d; font-size: 0.9em;">
            Generated by EdgeForge Multi-Agent PCB Reflow Optimizer
        </p>
    </div>
</body>
</html>
"""
        
        # Save report
        output_path = self.output_dir / filename
        with open(output_path, 'w') as f:
            f.write(html)
        
        return str(output_path)
