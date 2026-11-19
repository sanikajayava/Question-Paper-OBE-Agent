import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.analysis_tool import AnalysisTool

class BloomTaxonomyAgent:
    def __init__(self):
        self.name = "Bloom's Taxonomy Agent"
        self.tool = AnalysisTool()

    def analyze(self, questions):
        print(f"\n[{self.name}] Analyzing cognitive levels (L1 to L6)...")
        
        # AGENT CALLS TOOL
        bloom_distribution = self.tool.analyze_bloom(questions)
        
        # Find the dominant level
        dominant_level = max(bloom_distribution, key=bloom_distribution.get)
        
        print(f"[{self.name}] ✅ Analysis Complete.")
        print(f"  -> Distribution: {bloom_distribution}")
        print(f"  -> Dominant Level: {dominant_level}")
        
        return {
            "bloom_distribution": bloom_distribution,
            "dominant_level": dominant_level
        }