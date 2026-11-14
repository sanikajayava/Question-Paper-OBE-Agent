import time

class DeepResearchAgent:
    def __init__(self):
        self.name = "Lab 9: Deep Research Agent"

    def search(self, topic):
        print(f"  [Loop 1: Search] Searching databases for '{topic}'...")
        time.sleep(0.5)
        return ["Source A: GenAI is growing fast.", "Source B: GenAI has ethical risks."]

    def extract(self, sources):
        print(f"  [Loop 2: Extract] Extracting facts from {len(sources)} sources...")
        time.sleep(0.5)
        return ["Fact 1: High growth rate.", "Fact 2: Ethical concerns exist."]

    def compare(self, facts):
        print(f"  [Loop 3: Compare] Checking for contradictions...")
        time.sleep(0.5)
        return "No contradictions found."

    def synthesize(self, facts, comparison):
        print(f"  [Loop 4: Synthesize] Generating briefing...")
        time.sleep(0.5)
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
    agent.run("Generative AI in Education")