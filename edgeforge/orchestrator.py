"""EdgeForge Orchestrator - Coordinates all agents (mega prompt version)."""
from pathlib import Path
from edgeforge.bom_parser import BOMParserAgent
from edgeforge.limits_agent import LimitsAgent
from edgeforge.planner import PlannerAgent
from edgeforge.verifier import VerifierAgent
from edgeforge.presenter import PresenterAgent
from edgeforge.models import AgentContext


class Orchestrator:
    """Thin coordination layer - delegates all work to agents."""
    
    def __init__(self):
        """Initialize all agents."""
        print("🎯 EdgeForge-Thermo Multi-Agent System Starting...\n")
        self.context = AgentContext()
        
        # Initialize agents
        self.bom_parser = BOMParserAgent()
        self.limits_agent = LimitsAgent()
        self.planner = PlannerAgent()
        self.verifier = VerifierAgent()
        self.presenter = PresenterAgent()
    
    def run(self, bom_path: str = "data/sample_bom.csv", output_dir: str = "report") -> str:
        """Execute multi-agent workflow."""
        
        # Agent 1: Parse BOM
        self.context.bom_components = self.bom_parser.parse_bom(bom_path)
        print()
        
        # Agent 2: Get component limits
        self.context.component_limits = self.limits_agent.get_limits_for_bom(
            self.context.bom_components
        )
        if self.context.component_limits:
            self.limits_agent.get_most_restrictive(self.context.component_limits)
        print()
        
        # Agent 3: Plan profile
        self.context.paste_profile = self.planner.paste_profile
        self.context.proposed_profile = self.planner.plan(self.context.component_limits)
        print()
        
        # Agent 4: Verify constraints
        self.context.validation = self.verifier.verify(
            self.context.proposed_profile,
            self.context.component_limits,
            self.context.paste_profile
        )
        print()
        
        # Agent 5: Generate report
        self.presenter.output_dir = Path(output_dir)
        self.presenter.output_dir.mkdir(parents=True, exist_ok=True)
        
        report_path = self.presenter.generate_report(
            self.context.proposed_profile,
            self.context.bom_components,
            self.context.component_limits,
            self.context.validation
        )
        print()
        print(f"🎉 SUCCESS! Open: {Path(report_path).absolute()}")
        
        return report_path


def main():
    """Main entry point for orchestrator."""
    orchestrator = Orchestrator()
    orchestrator.run()


if __name__ == "__main__":
    main()
