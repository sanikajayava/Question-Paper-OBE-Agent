import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.retrieval_tool import RetrievalTool
from tools.analysis_tool import AnalysisTool
from tools.validation_tool import ValidationTool
from tools.generation_tool import GenerationTool

print("=" * 60)
print("  TESTING ALL 4 TOOLS")
print("=" * 60)

print("\n[Tool 1: Retrieval]")
rt = RetrievalTool()
cloud_qs = rt.query("Cloud Computing", "ESA", "Oct 2025 - Feb 2026")
genai_qs = rt.query("Gen AI", "ESA", "Oct 2025 - Feb 2026")
print(f"  Cloud ESA 2026: {len(cloud_qs)} questions")
print(f"  Gen AI ESA 2026: {len(genai_qs)} questions")
print(f"  DB stats: {rt.get_stats()}")

print("\n[Tool 2: Analysis]")
at = AnalysisTool()
bloom = at.analyze_bloom(cloud_qs)
print(f"  Bloom distribution: {bloom}")

print("\n[Tool 3: Validation]")
vt = ValidationTool()
if cloud_qs:
    ok, msg = vt.check_length(cloud_qs[0]["question_text"])
    print(f"  Length check: {ok} ({msg})")

print("\n[Tool 4: Generation]")
gt = GenerationTool()
if cloud_qs:
    formatted = gt.format_question(cloud_qs[0]["question_text"], 10)
    print(f"  Formatted: {formatted[:120]}...")
    print(f"  Marks for 5 qs of 100: {gt.calculate_marks(100, 5)}")

print("\n✅ All 4 tools working!")