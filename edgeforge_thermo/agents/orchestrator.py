from pathlib import Path
from .bom_parser import BOMParserAgent
from .limits_agent import LimitsAgent
from .planner import PlannerAgent
from .verifier import VerifierAgent
from .presenter import PresenterAgent
from .types import AgentContext

class Orchestrator:
    """Thin coordination layer - delegates all work to agents"""

    def __init__(self):
        print("🎯 EdgeForge-Thermo Multi-Agent System Starting...\n")
        self.context = AgentContext()

        # Initialize agents
        self.bom_parser = BOMParserAgent()
        self.limits_agent = LimitsAgent()
        self.planner = PlannerAgent()
        self.verifier = VerifierAgent()
        self.presenter = PresenterAgent()

    def run(self, bom_path: str = "data/sample_bom.csv") -> str:
        """Execute multi-agent workflow"""

        # Agent 1: Parse BOM
        self.context.bom_components = self.bom_parser.parse(bom_path)
        print()

        # Agent 2: Get component limits
        self.context.component_limits = self.limits_agent.get_limits_for_bom(
            self.context.bom_components
        )
        if self.context.component_limits:
            self.limits_agent.get_most_restrictive(self.context.component_limits)
        print()

        # Agent 3: Plan profile
        self.context.paste_profile = self.planner.paste
        self.context.proposed_profile = self.planner.plan(self.context.component_limits)
        print()

        # Agent 4: Verify constraints
        self.context.validation = self.verifier.verify(
            self.context.proposed_profile, self.context.component_limits, self.context.paste_profile
        )
        print()

        # Agent 5: Generate report
        report_path = self.presenter.generate_report(
            self.context.proposed_profile, self.context.validation
        )
        print()
        print(f"🎉 SUCCESS! Open: {Path(report_path).absolute()}")

        return report_path

def main():
    orchestrator = Orchestrator()
    orchestrator.run()

if __name__ == "__main__":
    main()
