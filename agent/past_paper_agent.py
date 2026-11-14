import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.analysis_tool import AnalysisTool

class PastPaperAnalysisAgent:
    def __init__(self):
        self.name = "Past Paper Analysis Agent"
        self.tool = AnalysisTool()  # <-- AGENT USES TOOL

    def analyze(self, questions):
        print(f"\n[{self.name}] Using AnalysisTool on {len(questions)} questions...")
        
        if not questions:
            return {"error": "No questions to analyze."}

        # AGENT CALLS TOOL - Bloom's L1-L6
        bloom = self.tool.analyze_bloom(questions)
        
        # AGENT CALLS TOOL - Topic frequency
        keywords = [
            "docker", "kubernetes", "microservice", "serverless", "virtualization", 
            "ansible", "puppet", "chef", "leaf-spine", "isolation", "container",
            "cloud", "network", "security", "scaling", "cnn", "rnn", "lstm",
            "transformer", "attention", "gan", "diffusion", "prompt", "bert", "gpt",
            "soc", "siem", "firewall", "malware", "forensics", "cia"
        ]
        top_topics = self.tool.analyze_topics(questions, keywords)[:5]

        dominant_level = max(bloom, key=bloom.get)
        
        report = {
            "total_questions_analyzed": len(questions),
            "top_topics": top_topics,
            "bloom_distribution": bloom,
            "dominant_bloom_level": dominant_level,
            "pattern_summary": f"Paper focuses on {', '.join([t[0] for t in top_topics[:3]])}. "
                               f"Dominant Bloom level: {dominant_level}."
        }

        print(f"[{self.name}] Analysis complete via tool.")
        return report