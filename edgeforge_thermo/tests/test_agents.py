import os
from agents.orchestrator import Orchestrator

def test_pipeline_runs(tmp_path):
    # Ensure report directory goes to temp
    orch = Orchestrator()
    report_path = orch.run(bom_path="data/sample_bom.csv")
    assert os.path.exists(report_path)
    assert report_path.endswith("index.html")
