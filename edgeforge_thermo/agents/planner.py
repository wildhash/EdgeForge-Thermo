import json
from typing import List
from .types import PasteProfile, ComponentLimit, ReflowProfile, ReflowStep

class PlannerAgent:
    """Agent 3: Reflow profile architect"""

    def __init__(self, paste_path: str = "data/paste_profile.json"):
        """
        Initialize the PlannerAgent and load a paste profile from a JSON file.
        
        Loads the JSON file at `paste_path`, constructs a PasteProfile from its contents,
        assigns it to `self.paste`, and prints a message indicating which paste profile was loaded.
        
        Parameters:
            paste_path (str): Path to the JSON file containing the paste profile. Defaults to "data/paste_profile.json".
        """
        self.paste = PasteProfile(**json.load(open(paste_path)))
        print(f"🤖 Planner Agent: Loaded {self.paste.paste_name} paste profile")

    def plan(self, limits: List[ComponentLimit]) -> ReflowProfile:
        """
        Create an optimized reflow profile that respects the paste recommendations and any provided component temperature limits.
        
        When component limits are provided, the peak temperature is chosen to honor the most restrictive max temperature with a 5°C safety margin and constrained to the paste's recommended peak range; when no limits are provided, the paste's recommended peak midpoint is used. The returned profile contains a sequence of timed phases (preheat, soak, ramp_to_peak, reflow, cooling), the selected peak temperature, the time above liquidus, and the total profile duration.
        
        Parameters:
            limits (List[ComponentLimit]): Component-specific temperature limits used to constrain the peak temperature. If empty, paste recommendations are used.
        
        Returns:
            ReflowProfile: A profile object with fields:
                - profile_id: identifier for the generated profile
                - steps: ordered list of ReflowStep phases with start/end times and temperatures
                - peak_temp_c: selected peak temperature in °C
                - time_above_liquidus_s: duration in seconds above liquidus
                - total_duration_s: total profile duration in seconds
        """
        print("🧠 Planner Agent: Computing optimal profile...")

        # Determine safe peak temp (most restrictive component - 5°C safety margin)
        if limits:
            max_allowed = min(l.max_temp_c for l in limits)
            safe_peak = min(max_allowed - 5, self.paste.recommended_peak_c[1])
            peak_temp = max(self.paste.recommended_peak_c[0], safe_peak)
        else:
            peak_temp = sum(self.paste.recommended_peak_c) / 2

        print(f"   Peak temp: {peak_temp}°C")

        # Build profile steps
        steps: List[ReflowStep] = []
        current_time = 0

        # Phase 1: Preheat (25°C → 150°C)
        preheat_duration = int((self.paste.preheat_target_c - 25) / 1.5)  # ~1.5°C/s
        steps.append(
            ReflowStep(
                phase="preheat",
                start_time_s=current_time,
                end_time_s=current_time + preheat_duration,
                start_temp_c=25.0,
                end_temp_c=self.paste.preheat_target_c,
            )
        )
        current_time += preheat_duration

        # Phase 2: Soak (150°C → 170°C, hold 60-90s)
        soak_target = sum(self.paste.soak_range_c) / 2
        soak_duration = int(sum(self.paste.soak_duration_s) / 2)
        steps.append(
            ReflowStep(
                phase="soak",
                start_time_s=current_time,
                end_time_s=current_time + soak_duration,
                start_temp_c=self.paste.preheat_target_c,
                end_temp_c=soak_target,
            )
        )
        current_time += soak_duration

        # Phase 3: Ramp to Peak (170°C → peak, ~2-3°C/s)
        ramp_duration = int((peak_temp - soak_target) / 2.5)
        steps.append(
            ReflowStep(
                phase="ramp_to_peak",
                start_time_s=current_time,
                end_time_s=current_time + ramp_duration,
                start_temp_c=soak_target,
                end_temp_c=peak_temp,
            )
        )
        current_time += ramp_duration

        # Phase 4: Reflow (hold at peak, time above liquidus)
        tal_duration = int(sum(self.paste.time_above_liquidus_s) / 2)
        steps.append(
            ReflowStep(
                phase="reflow",
                start_time_s=current_time,
                end_time_s=current_time + tal_duration,
                start_temp_c=peak_temp,
                end_temp_c=peak_temp - 5,  # Slight drop
            )
        )
        current_time += tal_duration

        # Phase 5: Cooling (peak → 100°C)
        cooling_rate = sum(self.paste.cooling_rate_c_per_s) / 2
        cooling_duration = int((peak_temp - 100) / cooling_rate)
        steps.append(
            ReflowStep(
                phase="cooling",
                start_time_s=current_time,
                end_time_s=current_time + cooling_duration,
                start_temp_c=steps[-1].end_temp_c,
                end_temp_c=100.0,
            )
        )
        current_time += cooling_duration

        profile = ReflowProfile(
            profile_id="optimized_v1",
            steps=steps,
            peak_temp_c=peak_temp,
            time_above_liquidus_s=tal_duration,
            total_duration_s=current_time,
        )

        print(
            f"✅ Planner Agent: Profile generated ({current_time}s total, peak={peak_temp}°C)"
        )
        return profile