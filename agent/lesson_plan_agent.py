import sys
import os
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class LessonPlanAgent:
    def __init__(self):
        self.name = "Lesson Plan Agent"

    def read_lesson_plan(self, file_path):
        """
        Reads a lesson plan text file and extracts units and topics.
        """
        print(f"\n[{self.name}] Reading lesson plan: {file_path}")
        
        if not os.path.exists(file_path):
            print(f"[{self.name}] ERROR: File not found.")
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract course and semester
        course_match = re.search(r'COURSE:\s*(.+)', content, re.IGNORECASE)
        semester_match = re.search(r'SEMESTER:\s*(.+)', content, re.IGNORECASE)
        
        course = course_match.group(1).strip() if course_match else "Unknown"
        semester = semester_match.group(1).strip() if semester_match else "Unknown"

        # Extract units and topics
        units = {}
        current_unit = None

        for line in content.split("\n"):
            line = line.strip()
            if not line:
                continue
            
            # Match lines like "UNIT 1: ..." or "UNIT-I: ..."
            unit_match = re.match(r'UNIT[\s\-]*([0-9IVX]+)[:\-]?\s*(.*)', line, re.IGNORECASE)
            if unit_match:
                current_unit = f"Unit {unit_match.group(1)}"
                units[current_unit] = {
                    "title": unit_match.group(2).strip(),
                    "topics": []
                }
            elif current_unit and (line.startswith("-") or line.startswith("*")):
                topic = line.lstrip("-* ").strip()
                if topic:
                    units[current_unit]["topics"].append(topic)

        structured_plan = {
            "course": course,
            "semester": semester,
            "units": units,
            "total_units": len(units),
            "total_topics": sum(len(u["topics"]) for u in units.values())
        }

        print(f"[{self.name}] ✅ Lesson plan parsed.")
        print(f"  -> Course: {structured_plan['course']}")
        print(f"  -> Total Units: {structured_plan['total_units']}")
        print(f"  -> Total Topics: {structured_plan['total_topics']}")
        
        return structured_plan

# --- TESTING THE AGENT ---
if __name__ == "__main__":
    agent = LessonPlanAgent()
    plan = agent.read_lesson_plan("data/lesson_plans/Cloud_Computing_Lesson_Plan.txt")
    
    if plan:
        print("\n--- EXTRACTED UNITS & TOPICS ---")
        for unit_name, unit_data in plan["units"].items():
            print(f"\n{unit_name}: {unit_data['title']}")
            for topic in unit_data["topics"]:
                print(f"  - {topic}")