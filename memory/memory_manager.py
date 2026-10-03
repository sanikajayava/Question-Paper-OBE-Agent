import json
from pathlib import Path


class MemoryManager:
    """
    Memory manager for retrieving past question papers
    using tags.
    """

    def __init__(self):
        self.file_path = Path(__file__).parent / "past_papers.json"

    def load_past_papers(self):
        """Load past papers from memory storage."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                return json.load(file)

        except FileNotFoundError:
            return []

        except json.JSONDecodeError:
            return []

    def retrieve_by_tag(self, tag):
        """Retrieve past papers matching a tag."""
        papers = self.load_past_papers()
        matches = []

        for paper in papers:
            if tag.lower() in [item.lower() for item in paper.get("tags", [])]:
                matches.append(paper)

        return matches

if __name__ == "__main__":
    memory = MemoryManager()

    results = memory.retrieve_by_tag("agents")

    print("===== MEMORY RETRIEVAL =====")
    print("Matching past papers:", len(results))

    for paper in results:
        print(f"{paper['paper_id']} - {paper['year']}")