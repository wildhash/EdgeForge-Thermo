import matplotlib.pyplot as plt
from pathlib import Path
from .types import ReflowProfile, ValidationResult

class PresenterAgent:
    """Agent 5: Visualization and reporting"""

    def generate_report(
        self, profile: ReflowProfile, validation: ValidationResult, output_dir: str = "report"
    ) -> str:
        """Create HTML report with profile visualization"""
        print("📊 Presenter Agent: Generating report...")

        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Generate profile chart
        self._create_chart(profile, f"{output_dir}/profile.png")

        # Generate HTML report
        html = self._create_html(profile, validation)
        html_path = f"{output_dir}/index.html"
        Path(html_path).write_text(html)

        print(f"✅ Presenter Agent: Report saved to {html_path}")
        return html_path

    def _create_chart(self, profile: ReflowProfile, output_path: str):
        """Generate temperature vs time chart"""
        times = []
        temps = []

        for step in profile.steps:
            times.extend([step.start_time_s, step.end_time_s])
            temps.extend([step.start_temp_c, step.end_temp_c])

        plt.figure(figsize=(12, 6))
        plt.plot(times, temps, linewidth=2, color="#e74c3c")
        plt.axhline(y=217, color="orange", linestyle="--", label="Liquidus (217°C)")
        plt.axhline(
            y=profile.peak_temp_c, color="red", linestyle="--", label=f"Peak ({profile.peak_temp_c}°C)"
        )

        # Shade phases
        for step in profile.steps:
            plt.axvspan(
                step.start_time_s,
                step.end_time_s,
                alpha=0.1,
                label=step.phase if step == profile.steps[0] else "",
            )

        plt.xlabel("Time (seconds)", fontsize=12)
        plt.ylabel("Temperature (°C)", fontsize=12)
        plt.title("EdgeForge-Thermo Optimized Reflow Profile", fontsize=14, fontweight="bold")
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        plt.close()

    def _create_html(self, profile: ReflowProfile, validation: ValidationResult) -> str:
        """Generate HTML report"""
        status_emoji = "✅" if validation.passed else "❌"
        status_color = "green" if validation.passed else "red"

        steps_html = ""
        for step in profile.steps:
            steps_html += f"""
            <tr>
                <td>{step.phase}</td>
                <td>{step.start_time_s}s - {step.end_time_s}s ({step.duration_s}s)</td>
                <td>{step.start_temp_c:.1f}°C → {step.end_temp_c:.1f}°C</td>
                <td>{step.ramp_rate_c_per_s:.2f}°C/s</td>
            </tr>
            """

        violations_html = "<br>".join(validation.violations) if validation.violations else "None"
        warnings_html = "<br>".join(validation.warnings) if validation.warnings else "None"

        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>EdgeForge-Thermo Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; 
                     border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        .status {{ font-size: 24px; color: {status_color}; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background: #34495e; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        tr:hover {{ background: #f9f9f9; }}
        .metric {{ display: inline-block; margin: 10px 20px; }}
        .metric-value {{ font-size: 28px; color: #e74c3c; font-weight: bold; }}
        .metric-label {{ color: #7f8c8d; font-size: 14px; }}
        img {{ max-width: 100%; margin: 20px 0; border: 1px solid #ddd; }}
        .violations {{ color: #e74c3c; }}
        .warnings {{ color: #f39c12; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔥 EdgeForge-Thermo Reflow Profile</h1>
        <p class="status">{status_emoji} Validation Status: {"PASSED" if validation.passed else "FAILED"}</p>
        
        <h2>📊 Key Metrics</h2>
        <div>
            <div class="metric">
                <div class="metric-value">{profile.peak_temp_c:.1f}°C</div>
                <div class="metric-label">Peak Temperature</div>
            </div>
            <div class="metric">
                <div class="metric-value">{profile.time_above_liquidus_s}s</div>
                <div class="metric-label">Time Above Liquidus</div>
            </div>
            <div class="metric">
                <div class="metric-value">{profile.total_duration_s}s</div>
                <div class="metric-label">Total Duration</div>
            </div>
        </div>
        
        <h2>📈 Profile Chart</h2>
        <img src="profile.png" alt="Reflow Profile">
        
        <h2>📋 Profile Steps</h2>
        <table>
            <tr>
                <th>Phase</th>
                <th>Time Window</th>
                <th>Temperature Range</th>
                <th>Ramp Rate</th>
            </tr>
            {steps_html}
        </table>
        
        <h2>🔍 Validation Results</h2>
        <p><strong class="violations">Violations:</strong> {violations_html}</p>
        <p><strong class="warnings">Warnings:</strong> {warnings_html}</p>
        
        <hr>
        <p style="text-align: center; color: #7f8c8d;">
            Generated by EdgeForge-Thermo Multi-Agent System
        </p>
    </div>
</body>
</html>
        """
