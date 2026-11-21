"""
QUESTION PAPER OBE AGENT - MASTER DEMONSTRATION
=============================================
Team 6 | Agentic AI Labs 1-10

This script demonstrates the complete lab progression:
  PART 1: LAB 1-6 - Skills, Tools, Memory, Audit Logs
  PART 2: LAB 6/14 - Question Paper Multi-Agent System
  PART 3: LAB 7 - Agentic Node Graph
  PART 4: LAB 8 - Parallel Swarm
  PART 5: LAB 9 - Deep Research Agent
  PART 6: LAB 10 - Cloud Operations Agent
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from runtime.openclaw_runtime import OpenClawRuntime
from agent.lab7_node_graph_agent import NodeGraphAgent
from agent.lab8_parallel_swarm_agent import ParallelSwarmAgent
from agent.lab9_deep_research_agent import DeepResearchAgent
from agent.lab10_cloud_ops_agent import CloudOpsAgent

def show_header(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def main():
    # PART 1
    show_header("PART 1: LAB 1-6 - SKILLS, TOOLS, MEMORY, AUDIT LOGS")
    runtime = OpenClawRuntime()
    result = runtime.execute("Generate a 50-mark blueprint for Agentic AI.")
    print(f"âœ… Lab 1-6 Status: {result['status']} (Audit events: {len(result['audit_log'])})")

    # PART 2
    show_header("PART 2: LAB 6/14 - QUESTION PAPER MULTI-AGENT SYSTEM")
    print("Running 5-Agent Pipeline for Cloud Computing...")
    try:
        runtime.execute_multi_agent(
            subject="Cloud Computing", exam_type="ESA",
            target_batch="Oct 2025 - Feb 2026",
            lesson_plan_path="data/lesson_plans/Cloud_Computing_LP.pdf"
        )
    except Exception as e:
        print(f"âŒ ERROR: {e}")

    # PART 3
    show_header("PART 3: LAB 7 - AGENTIC NODE GRAPH")
    NodeGraphAgent().run_graph("Build a new Campus App for students")

    # PART 4
    show_header("PART 4: LAB 8 - PARALLEL SWARM")
    ParallelSwarmAgent().run_swarm()

    # PART 5
    show_header("PART 5: LAB 9 - DEEP RESEARCH AGENT")
    DeepResearchAgent().run("Generative AI in Education")

    # PART 6
    show_header("PART 6: LAB 10 - CLOUD OPERATIONS AGENT")
    CloudOpsAgent().run()

    # SUMMARY
    show_header("ðŸŽ‰ FULL LAB 1-10 DEMONSTRATION COMPLETE ðŸŽ‰")
    print("""
âœ… Lab 1-6: Foundations & Memory
âœ… Lab 6/14: Question Paper Capstone
âœ… Lab 7: Node Graph
âœ… Lab 8: Parallel Swarm
âœ… Lab 9: Deep Research Loop
âœ… Lab 10: Cloud Operations

ðŸ“ Check the output/ folder for generated JSON papers.
    """)

if __name__ == "__main__":
    main()
