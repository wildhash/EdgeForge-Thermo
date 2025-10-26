"""Planner Agent - Generates optimized reflow profiles."""
from edgeforge.models import SolderPaste, ThermalLimits, ProfileStep, ReflowProfile


class PlannerAgent:
    """Agent responsible for generating reflow profiles."""
    
    def generate_profile(
        self,
        paste: SolderPaste,
        limits: ThermalLimits
    ) -> ReflowProfile:
        """
        Generate an optimized reflow profile based on paste specs and thermal limits.
        
        Typical reflow stages:
        1. Preheat: 25°C -> 150°C (ramp up gradually)
        2. Soak: 150°C -> 180°C (slow ramp, activate flux)
        3. Ramp to Peak: 180°C -> liquidus temp (controlled ramp)
        4. Peak: Above liquidus to peak temp (where actual soldering happens)
        5. Cool: Peak -> safe handling temp (controlled cool down)
        """
        steps = []
        
        # Starting temperature
        ambient_temp = 25.0
        
        # Calculate safe peak temperature (below component max and within paste range)
        peak_temp = min(
            paste.peak_temp_range[1],
            limits.max_temp - 5.0  # 5°C safety margin
        )
        
        # Ensure peak is at least at paste minimum
        peak_temp = max(peak_temp, paste.peak_temp_range[0])
        
        # Stage 1: Preheat (25°C -> 150°C)
        preheat_start = ambient_temp
        preheat_end = 150.0
        preheat_ramp = min(limits.max_ramp_up * 0.8, 2.0)  # Conservative ramp
        preheat_duration = (preheat_end - preheat_start) / preheat_ramp
        
        steps.append(ProfileStep(
            name='Preheat',
            start_temp=preheat_start,
            end_temp=preheat_end,
            duration=preheat_duration,
            ramp_rate=preheat_ramp
        ))
        
        # Stage 2: Soak (150°C -> 180°C)
        soak_start = preheat_end
        soak_end = 180.0
        soak_ramp = 0.5  # Slow ramp for flux activation
        soak_duration = (soak_end - soak_start) / soak_ramp
        
        steps.append(ProfileStep(
            name='Soak',
            start_temp=soak_start,
            end_temp=soak_end,
            duration=soak_duration,
            ramp_rate=soak_ramp
        ))
        
        # Stage 3: Ramp to liquidus (180°C -> liquidus)
        ramp_start = soak_end
        ramp_end = paste.liquidus_temp
        ramp_rate = min(limits.max_ramp_up * 0.9, 2.5)  # Near max safe ramp
        ramp_duration = (ramp_end - ramp_start) / ramp_rate
        
        steps.append(ProfileStep(
            name='Ramp',
            start_temp=ramp_start,
            end_temp=ramp_end,
            duration=ramp_duration,
            ramp_rate=ramp_rate
        ))
        
        # Stage 4: Peak (liquidus -> peak temp -> liquidus)
        # Time above liquidus must be within limits
        tal_target = (limits.min_time_above_liquidus + limits.max_time_above_liquidus) / 2
        
        # Ramp up to peak
        peak_ramp_up = (peak_temp - paste.liquidus_temp) / ramp_rate
        
        # Hold at peak briefly
        peak_hold = 10.0
        
        # Ramp down from peak to liquidus
        cool_ramp_rate = min(limits.max_ramp_down * 0.9, 3.0)
        peak_ramp_down = (peak_temp - paste.liquidus_temp) / cool_ramp_rate
        
        # Adjust hold time to meet TAL requirements
        tal_from_ramps = peak_ramp_up + peak_ramp_down
        additional_hold = max(0, limits.min_time_above_liquidus - tal_from_ramps - peak_hold)
        peak_hold += additional_hold
        
        # Total peak duration
        peak_duration = peak_ramp_up + peak_hold + peak_ramp_down
        
        steps.append(ProfileStep(
            name='Peak',
            start_temp=paste.liquidus_temp,
            end_temp=peak_temp,
            duration=peak_duration,
            ramp_rate=ramp_rate  # Average ramp rate
        ))
        
        # Stage 5: Cool down (peak -> 100°C)
        cool_start = paste.liquidus_temp
        cool_end = 100.0
        cool_rate = min(limits.max_ramp_down * 0.8, 3.0)
        cool_duration = (cool_start - cool_end) / cool_rate
        
        steps.append(ProfileStep(
            name='Cool',
            start_temp=cool_start,
            end_temp=cool_end,
            duration=cool_duration,
            ramp_rate=-cool_rate
        ))
        
        # Calculate totals
        total_time = sum(step.duration for step in steps)
        
        # TAL calculation (approximate)
        tal = peak_duration + (ramp_duration * 0.5)  # Half of ramp to liquidus contributes
        
        profile = ReflowProfile(
            paste=paste,
            steps=steps,
            total_time=total_time,
            time_above_liquidus=tal
        )
        
        return profile
