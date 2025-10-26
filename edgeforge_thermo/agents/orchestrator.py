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
        """
        Create an Orchestrator instance that sets up a shared AgentContext and the five agent components used by the workflow.
        
        Initializes:
        - self.context: shared AgentContext for passing data between agents.
        - self.bom_parser: BOMParserAgent for parsing bill-of-materials.
        - self.limits_agent: LimitsAgent for retrieving and computing component limits.
        - self.planner: PlannerAgent for generating proposed profiles (exposes `paste` as paste profile).
        - self.verifier: VerifierAgent for validating proposed profiles against limits and paste profile.
        - self.presenter: PresenterAgent for generating final reports.
        
        Also prints a startup banner to stdout.
        """
        print("🎯 EdgeForge-Thermo Multi-Agent System Starting...\n")
        self.context = AgentContext()

        # Initialize agents
        self.bom_parser = BOMParserAgent()
        self.limits_agent = LimitsAgent()
        self.planner = PlannerAgent()
        self.verifier = VerifierAgent()
        self.presenter = PresenterAgent()

    def run(self, bom_path: str = "data/sample_bom.csv") -> str:
        """
        Run the five-stage multi-agent pipeline to produce a report from a BOM.
        
        Executes: (1) parse the BOM at bom_path and store components in self.context, (2) retrieve component limits and compute the most restrictive limits if available, (3) set the planner paste profile and generate a proposed profile, (4) verify the proposed profile against limits and paste profile, and (5) generate a report and return its path. The method updates self.context with results from each stage.
        
        Parameters:
            bom_path (str): Filesystem path to the BOM CSV to parse.
        
        Returns:
            report_path (str): Filesystem path to the generated report.
        """

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
    """
    Create an Orchestrator instance and execute the multi-agent workflow.
    
    Instantiates the Orchestrator and runs its pipeline, which parses a BOM, computes limits, generates a plan, verifies it, and produces a report.
    """
    orchestrator = Orchestrator()
    orchestrator.run()

if __name__ == "__main__":
    main()