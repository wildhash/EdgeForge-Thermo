from typing import List
from .types import ReflowProfile, ComponentLimit, PasteProfile, ValidationResult

class VerifierAgent:
    """Agent 4: Quality assurance and constraint validation"""

    def verify(
        self,
        profile: ReflowProfile,
        limits: List[ComponentLimit],
        paste: PasteProfile,
    ) -> ValidationResult:
        """
        Validate a reflow profile against component and paste constraints.
        
        Checks the profile for peak temperature violations, excessive ramp rates, insufficient time above liquidus (TAL), and short soak duration; aggregates violations and warnings and returns pass/fail status with summary metrics.
        
        Parameters:
        	profile (ReflowProfile): The reflow heating profile to validate.
        	limits (List[ComponentLimit]): Component-specific constraints to check (e.g., max temps, max ramp rates, min soak times).
        	paste (PasteProfile): Paste-specific constraints used for TAL comparison.
        
        Returns:
        	ValidationResult: Result object containing:
        		- passed (bool): `true` if no violations were found, `false` otherwise.
        		- violations (List[str]): Fatal constraint breach messages.
        		- warnings (List[str]): Non-fatal advisory messages.
        		- metrics (dict): Summary metrics with keys `peak_temp_c`, `tal_s`, `total_duration_s`, and `max_ramp_rate`.
        """
        print("🔍 Verifier Agent: Checking constraints...")

        violations: List[str] = []
        warnings: List[str] = []

        # Check peak temperature
        for limit in limits:
            if profile.peak_temp_c > limit.max_temp_c:
                violations.append(
                    f"Peak {profile.peak_temp_c}°C exceeds {limit.mpn} max {limit.max_temp_c}°C"
                )

        # Check ramp rates
        for step in profile.steps:
            rate = step.ramp_rate_c_per_s
            for limit in limits:
                if rate > limit.max_ramp_rate_c_per_s:
                    warnings.append(
                        f"{step.phase}: {rate:.2f}°C/s exceeds {limit.mpn} max {limit.max_ramp_rate_c_per_s}°C/s"
                    )

        # Check time above liquidus
        if profile.time_above_liquidus_s < paste.time_above_liquidus_s[0]:
            violations.append(
                f"TAL {profile.time_above_liquidus_s}s below minimum {paste.time_above_liquidus_s[0]}s"
            )

        # Check soak phase
        soak_step = next((s for s in profile.steps if s.phase == "soak"), None)
        if soak_step and limits:
            min_soak = min(l.min_soak_time_s for l in limits)
            if soak_step.duration_s < min_soak:
                warnings.append(
                    f"Soak duration {soak_step.duration_s}s may be too short (min {min_soak}s)"
                )

        passed = len(violations) == 0
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} Verifier Agent: {len(violations)} violations, {len(warnings)} warnings")

        return ValidationResult(
            passed=passed,
            violations=violations,
            warnings=warnings,
            metrics={
                "peak_temp_c": profile.peak_temp_c,
                "tal_s": profile.time_above_liquidus_s,
                "total_duration_s": profile.total_duration_s,
                "max_ramp_rate": max(s.ramp_rate_c_per_s for s in profile.steps),
            },
        )