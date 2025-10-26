"""Verifier Agent - Validates reflow profiles against thermal limits."""
from typing import List
from edgeforge.models import (
    ReflowProfile, ThermalLimits, ValidationResult,
    ComponentLimit, PasteProfile
)


class VerifierAgent:
    """Agent responsible for validating reflow profiles."""
    
    def verify(
        self,
        profile: ReflowProfile,
        limits: List[ComponentLimit],
        paste: PasteProfile
    ) -> ValidationResult:
        """Validate profile against all constraints."""
        print("🔍 Verifier Agent: Checking constraints...")
        
        violations = []
        warnings = []
        
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
                warnings.append(f"Soak duration {soak_step.duration_s}s may be too short (min {min_soak}s)")
        
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
                "max_ramp_rate": max(s.ramp_rate_c_per_s for s in profile.steps) if profile.steps else 0
            }
        )
    
    def verify_profile(
        self,
        profile: ReflowProfile,
        limits: ThermalLimits
    ) -> ValidationResult:
        """
        Verify that a reflow profile respects all thermal limits (legacy method).
        
        Checks:
        - Maximum temperature not exceeded
        - Ramp rates within limits
        - Time above liquidus within acceptable range
        """
        violations = []
        warnings = []
        
        # Check each step
        for i, step in enumerate(profile.steps):
            step_name = f"{getattr(step, 'phase', f'step_{i+1}')}"
            
            # Get temperatures
            start_temp = getattr(step, 'start_temp_c', getattr(step, 'start_temp', 0))
            end_temp = getattr(step, 'end_temp_c', getattr(step, 'end_temp', 0))
            
            # Check maximum temperature
            max_step_temp = max(start_temp, end_temp)
            if max_step_temp > limits.max_temp:
                violations.append(
                    f"{step_name}: Temperature {max_step_temp}°C exceeds limit {limits.max_temp}°C"
                )
            
            # Get ramp rate
            ramp_rate = getattr(step, 'ramp_rate_c_per_s', getattr(step, 'ramp_rate', 0))
            
            # Check ramp rates
            if ramp_rate > 0:  # Heating
                if ramp_rate > limits.max_ramp_up:
                    violations.append(
                        f"{step_name}: Ramp up rate {ramp_rate:.2f}°C/s exceeds limit {limits.max_ramp_up}°C/s"
                    )
                elif ramp_rate > limits.max_ramp_up * 0.95:
                    warnings.append(
                        f"{step_name}: Ramp up rate {ramp_rate:.2f}°C/s is close to limit {limits.max_ramp_up}°C/s"
                    )
            elif ramp_rate < 0:  # Cooling
                if abs(ramp_rate) > limits.max_ramp_down:
                    violations.append(
                        f"{step_name}: Cool down rate {abs(ramp_rate):.2f}°C/s exceeds limit {limits.max_ramp_down}°C/s"
                    )
                elif abs(ramp_rate) > limits.max_ramp_down * 0.95:
                    warnings.append(
                        f"{step_name}: Cool down rate {abs(ramp_rate):.2f}°C/s is close to limit {limits.max_ramp_down}°C/s"
                    )
        
        # Check time above liquidus
        tal = profile.time_above_liquidus
        if tal < limits.min_time_above_liquidus:
            violations.append(
                f"Time above liquidus {tal:.1f}s is below minimum {limits.min_time_above_liquidus}s"
            )
        elif tal > limits.max_time_above_liquidus:
            violations.append(
                f"Time above liquidus {tal:.1f}s exceeds maximum {limits.max_time_above_liquidus}s"
            )
        elif tal < limits.min_time_above_liquidus * 1.1:
            warnings.append(
                f"Time above liquidus {tal:.1f}s is close to minimum {limits.min_time_above_liquidus}s"
            )
        elif tal > limits.max_time_above_liquidus * 0.9:
            warnings.append(
                f"Time above liquidus {tal:.1f}s is close to maximum {limits.max_time_above_liquidus}s"
            )
        
        result = ValidationResult(
            passed=len(violations) == 0,
            violations=violations,
            warnings=warnings,
            metrics={}
        )
        
        return result
