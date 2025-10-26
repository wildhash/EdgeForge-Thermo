# 🔥 EdgeForge-Thermo

**Multi-agent AI that prevents $100K PCB failures by auto-generating perfect reflow profiles**

## The Problem
PCB manufacturers waste millions annually on failed boards due to incorrect reflow profiles. Engineers manually create profiles, risking component damage from thermal stress.

## Our Solution
EdgeForge-Thermo is a **multi-agent system** where specialized AI agents collaborate to:
1. Parse your BOM
2. Match component thermal limits
3. Design optimal temperature curves
4. Verify all constraints
5. Generate production-ready profiles

## Multi-Agent Architecture (Track 1)
Each agent is autonomous with clear expertise:
- **BOM Parser Agent**: Component identification specialist
- **Limits Agent**: Thermal constraint expert
- **Planner Agent**: Profile optimization architect  
- **Verifier Agent**: Quality assurance validator
- **Presenter Agent**: Data visualization specialist

Agents coordinate through typed interfaces (Pydantic) and make independent decisions.

## Quick Start
```bash
pip install -r requirements.txt
python -m agents.orchestrator
# Open report/index.html
```

## Demo Output
- Interactive temperature/time chart
- Validation report with constraint checks
- Production-ready profile for your oven

## Impact
- Prevents component damage ($50-500K per board failure)
- Reduces profile development time from hours to seconds
- Scalable to any BOM size or component database

## Built for Hackathon Track 1: Multi-Agent Systems
Demonstrates real-world collective intelligence in PCB manufacturing.
