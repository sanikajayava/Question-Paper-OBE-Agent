import time

class DeepResearchAgent:
    def __init__(self):
        self.name = "Lab 9: Deep Research Agent"

    def search(self, topic):
        print(f"  [Loop 1: Search] Searching databases for '{topic}' syllabus topics...")
        time.sleep(1)
        return [f"Source A: {topic} Unit 1 concepts", f"Source B: {topic} Unit 2 advanced topics"]

    def extract(self, sources):
        print(f"  [Loop 2: Extract] Extracting key facts from {len(sources)} sources...")
        time.sleep(1)
        return ["Fact 1: Requires 15 marks weightage.", "Fact 2: Bloom's Level L3 required."]

    def compare(self, facts):
        print(f"  [Loop 3: Compare] Checking for syllabus contradictions...")
        time.sleep(1)
        return "No contradictions found. Aligned with KLE Tech 2026 syllabus."

    def synthesize(self, facts, comparison):
        print(f"  [Loop 4: Synthesize] Generating research briefing...")
        time.sleep(1)
        return f"BRIEFING REPORT:\n  - {facts[0]}\n  - {facts[1]}\n  - Status: {comparison}"

    def run(self, topic):
        print(f"\n[{self.name}] Starting research on: {topic}")
        sources = self.search(topic)
        facts = self.extract(sources)
        comparison = self.compare(facts)
        report = self.synthesize(facts, comparison)
        print(f"\n✅ [{self.name}] Research Complete.\n{report}")

if __name__ == "__main__":
    agent = DeepResearchAgent()
    agent.run("Cloud Computing ISA1")