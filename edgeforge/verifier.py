"""Verifier Agent - Validates reflow profiles against thermal limits."""
from edgeforge.models import ReflowProfile, ThermalLimits, ValidationResult


class VerifierAgent:
    """Agent responsible for validating reflow profiles."""
    
    def verify_profile(
        self,
        profile: ReflowProfile,
        limits: ThermalLimits
    ) -> ValidationResult:
        """
        Verify that a reflow profile respects all thermal limits.
        
        Checks:
        - Maximum temperature not exceeded
        - Ramp rates within limits
        - Time above liquidus within acceptable range
        """
        violations = []
        warnings = []
        
        # Check each step
        for i, step in enumerate(profile.steps):
            step_name = f"{step.name} (step {i+1})"
            
            # Check maximum temperature
            max_step_temp = max(step.start_temp, step.end_temp)
            if max_step_temp > limits.max_temp:
                violations.append(
                    f"{step_name}: Temperature {max_step_temp}°C exceeds limit {limits.max_temp}°C"
                )
            
            # Check ramp rates
            if step.ramp_rate > 0:  # Heating
                if step.ramp_rate > limits.max_ramp_up:
                    violations.append(
                        f"{step_name}: Ramp up rate {step.ramp_rate:.2f}°C/s exceeds limit {limits.max_ramp_up}°C/s"
                    )
                elif step.ramp_rate > limits.max_ramp_up * 0.95:
                    warnings.append(
                        f"{step_name}: Ramp up rate {step.ramp_rate:.2f}°C/s is close to limit {limits.max_ramp_up}°C/s"
                    )
            elif step.ramp_rate < 0:  # Cooling
                if abs(step.ramp_rate) > limits.max_ramp_down:
                    violations.append(
                        f"{step_name}: Cool down rate {abs(step.ramp_rate):.2f}°C/s exceeds limit {limits.max_ramp_down}°C/s"
                    )
                elif abs(step.ramp_rate) > limits.max_ramp_down * 0.95:
                    warnings.append(
                        f"{step_name}: Cool down rate {abs(step.ramp_rate):.2f}°C/s is close to limit {limits.max_ramp_down}°C/s"
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
            valid=len(violations) == 0,
            violations=violations,
            warnings=warnings
        )
        
        return result
