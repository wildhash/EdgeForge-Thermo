"""Planner Agent - Generates optimized reflow profiles."""
import json
from typing import List, Optional
from edgeforge.models import (
    SolderPaste, ThermalLimits, ProfileStep, ReflowProfile,
    PasteProfile, ComponentLimit, ReflowStep
)


class PlannerAgent:
    """Agent responsible for generating reflow profiles."""
    
    def __init__(self, paste_path: Optional[str] = None):
        """Initialize planner agent."""
        self.paste_profile: Optional[PasteProfile] = None
        
        if paste_path is None:
            paste_path = "data/paste_profile.json"
        
        try:
            with open(paste_path, 'r') as f:
                data = json.load(f)
            self.paste_profile = PasteProfile(**data)
            print(f"🤖 Planner Agent: Loaded {self.paste_profile.paste_name} paste profile")
        except FileNotFoundError:
            print(f"⚠️  Planner Agent: Paste profile not found at {paste_path}")
    
    def plan(self, limits: List[ComponentLimit]) -> ReflowProfile:
        """Generate optimal reflow profile respecting all constraints."""
        if not self.paste_profile:
            raise ValueError("No paste profile loaded")
        
        print("🧠 Planner Agent: Computing optimal profile...")
        
        paste = self.paste_profile
        
        # Determine safe peak temp (most restrictive component - 5°C safety margin)
        if limits:
            max_allowed = min(l.max_temp_c for l in limits)
            safe_peak = min(max_allowed - 5, paste.recommended_peak_c[1])
            peak_temp = max(paste.recommended_peak_c[0], safe_peak)
        else:
            peak_temp = sum(paste.recommended_peak_c) / 2
        
        print(f"   Peak temp: {peak_temp}°C")
        
        # Build profile steps
        steps = []
        current_time = 0
        
        # Phase 1: Preheat (25°C → 150°C)
        preheat_duration = int((paste.preheat_target_c - 25) / 1.5)  # ~1.5°C/s
        steps.append(ReflowStep(
            phase="preheat",
            start_time_s=current_time,
            end_time_s=current_time + preheat_duration,
            start_temp_c=25.0,
            end_temp_c=paste.preheat_target_c
        ))
        current_time += preheat_duration
        
        # Phase 2: Soak (150°C → 170°C, hold 60-90s)
        soak_target = sum(paste.soak_range_c) / 2
        soak_duration = int(sum(paste.soak_duration_s) / 2)
        steps.append(ReflowStep(
            phase="soak",
            start_time_s=current_time,
            end_time_s=current_time + soak_duration,
            start_temp_c=paste.preheat_target_c,
            end_temp_c=soak_target
        ))
        current_time += soak_duration
        
        # Phase 3: Ramp to Peak (170°C → peak, ~2-3°C/s)
        ramp_duration = int((peak_temp - soak_target) / 2.5)
        steps.append(ReflowStep(
            phase="ramp_to_peak",
            start_time_s=current_time,
            end_time_s=current_time + ramp_duration,
            start_temp_c=soak_target,
            end_temp_c=peak_temp
        ))
        current_time += ramp_duration
        
        # Phase 4: Reflow (hold at peak, time above liquidus)
        tal_duration = int(sum(paste.time_above_liquidus_s) / 2)
        steps.append(ReflowStep(
            phase="reflow",
            start_time_s=current_time,
            end_time_s=current_time + tal_duration,
            start_temp_c=peak_temp,
            end_temp_c=peak_temp - 5  # Slight drop
        ))
        current_time += tal_duration
        
        # Phase 5: Cooling (peak → 100°C)
        cooling_rate = sum(paste.cooling_rate_c_per_s) / 2
        cooling_duration = int((peak_temp - 100) / cooling_rate)
        steps.append(ReflowStep(
            phase="cooling",
            start_time_s=current_time,
            end_time_s=current_time + cooling_duration,
            start_temp_c=steps[-1].end_temp_c,
            end_temp_c=100.0
        ))
        current_time += cooling_duration
        
        profile = ReflowProfile(
            profile_id="optimized_v1",
            steps=steps,
            peak_temp_c=peak_temp,
            time_above_liquidus_s=tal_duration,
            total_duration_s=current_time
        )
        
        print(f"✅ Planner Agent: Profile generated ({current_time}s total, peak={peak_temp}°C)")
        return profile
    
    def generate_profile(
        self,
        paste: SolderPaste,
        limits: ThermalLimits
    ) -> ReflowProfile:
        """
        Generate an optimized reflow profile based on paste specs and thermal limits (legacy method).
        
        Typical reflow stages:
        1. Preheat: 25°C -> 150°C (ramp up gradually)
        2. Soak: 150°C -> 180°C (slow ramp, activate flux)
        3. Ramp to Peak: 180°C -> liquidus temp (controlled ramp)
        4. Peak: Above liquidus to peak temp (where actual soldering happens)
        5. Cool: Peak -> safe handling temp (controlled cool down)
        """
        # Starting temperature
        ambient_temp = 25.0
        
        # Calculate safe peak temperature (below component max and within paste range)
        peak_temp = min(
            paste.peak_temp_range[1],
            limits.max_temp - 5.0  # 5°C safety margin
        )
        
        # Ensure peak is at least at paste minimum
        peak_temp = max(peak_temp, paste.peak_temp_range[0])
        
        # Build profile steps (new format)
        steps = []
        current_time = 0
        
        # Stage 1: Preheat (25°C -> 150°C)
        preheat_start = ambient_temp
        preheat_end = 150.0
        preheat_ramp = min(limits.max_ramp_up * 0.8, 2.0)  # Conservative ramp
        preheat_duration = int((preheat_end - preheat_start) / preheat_ramp)
        
        steps.append(ReflowStep(
            phase='preheat',
            start_time_s=current_time,
            end_time_s=current_time + preheat_duration,
            start_temp_c=preheat_start,
            end_temp_c=preheat_end
        ))
        current_time += preheat_duration
        
        # Stage 2: Soak (150°C -> 180°C)
        soak_start = preheat_end
        soak_end = 180.0
        soak_ramp = 0.5  # Slow ramp for flux activation
        soak_duration = int((soak_end - soak_start) / soak_ramp)
        
        steps.append(ReflowStep(
            phase='soak',
            start_time_s=current_time,
            end_time_s=current_time + soak_duration,
            start_temp_c=soak_start,
            end_temp_c=soak_end
        ))
        current_time += soak_duration
        
        # Stage 3: Ramp to liquidus (180°C -> liquidus)
        ramp_start = soak_end
        ramp_end = paste.liquidus_temp
        ramp_rate = min(limits.max_ramp_up * 0.9, 2.5)  # Near max safe ramp
        ramp_duration = int((ramp_end - ramp_start) / ramp_rate)
        
        steps.append(ReflowStep(
            phase='ramp_to_peak',
            start_time_s=current_time,
            end_time_s=current_time + ramp_duration,
            start_temp_c=ramp_start,
            end_temp_c=ramp_end
        ))
        current_time += ramp_duration
        
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
        peak_duration = int(peak_ramp_up + peak_hold + peak_ramp_down)
        
        steps.append(ReflowStep(
            phase='reflow',
            start_time_s=current_time,
            end_time_s=current_time + peak_duration,
            start_temp_c=paste.liquidus_temp,
            end_temp_c=peak_temp
        ))
        current_time += peak_duration
        
        # Stage 5: Cool down (peak -> 100°C)
        cool_start = paste.liquidus_temp
        cool_end = 100.0
        cool_rate = min(limits.max_ramp_down * 0.8, 3.0)
        cool_duration = int((cool_start - cool_end) / cool_rate)
        
        steps.append(ReflowStep(
            phase='cooling',
            start_time_s=current_time,
            end_time_s=current_time + cool_duration,
            start_temp_c=cool_start,
            end_temp_c=cool_end
        ))
        current_time += cool_duration
        
        # TAL calculation (approximate)
        tal = int(peak_duration + (ramp_duration * 0.5))  # Half of ramp to liquidus contributes
        
        profile = ReflowProfile(
            profile_id="legacy_v1",
            steps=steps,
            peak_temp_c=peak_temp,
            time_above_liquidus_s=tal,
            total_duration_s=current_time
        )
        
        return profile
