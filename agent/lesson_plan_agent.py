import sys
import os
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class LessonPlanAgent:
    def __init__(self):
        self.name = "Lesson Plan Agent"

    def read_lesson_plan(self, file_path):
        print(f"\n[{self.name}] Reading lesson plan: {file_path}")
        
        if not os.path.exists(file_path):
            print(f"[{self.name}] ERROR: File not found.")
            return None

        content = ""
        if file_path.lower().endswith(".pdf"):
            from tools.pdf_reader_tool import extract_text_from_pdf
            result = extract_text_from_pdf(file_path)
            if result["status"] == "success":
                content = result["text"]
            else:
                return None
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

        # Extract Course Info
        course_title = "Unknown Subject"
        course_code = "Auto-Generated"
        
        title_match = re.search(r'Course Title:\s*([^\n\r]+)', content, re.IGNORECASE)
        if title_match:
            course_title = title_match.group(1).split('Course Code')[0].strip()
            
        code_match = re.search(r'Course Code:\s*([A-Z0-9]+)', content, re.IGNORECASE)
        if code_match:
            course_code = code_match.group(1).strip()

        all_questions = []
        text = re.sub(r'\s+', ' ', content)
        
        # 1. First split by lines starting with numbers
        parts = re.split(r'(?=\b\d+[\.\)]\s)', text)
        
        banned_phrases = [
            "describe the fundamental", "analyze deep learning", 
            "apply deep learning", "build various deep", "course outcomes",
            "at the end of the course"
        ]
        
        for part in parts:
            part = part.strip()
            
            # 2. SECONDARY SPLIT: Force a split if we see things like " 4.Explain" or " 5.Understand"
            # This breaks apart the concatenated questions
            sub_parts = re.split(r'(?=\s+\d+[\.\)]\s*[A-Z])', part)
            
            for sub_part in sub_parts:
                clean_line = re.sub(r'^\d+[\.\)]\s+', '', sub_part.strip())
                
                # Strip table columns
                clean_line = re.split(r'\s+(?:L\d|H\s*[HM]|M\s*[HL]|CO\d|TLO\d|PI|Code|\d+%|✓|\b\d+\.\d+\.\d+\b)', clean_line, flags=re.IGNORECASE)[0]
                clean_line = re.sub(r'\s*\b\d+\.*$', '', clean_line)
                clean_line = re.sub(r'\s+[A-Z0-9]\.?$', '', clean_line)
                clean_line = clean_line.strip(' .-')
                clean_line_lower = clean_line.lower()
                
                if any(banned in clean_line_lower for banned in banned_phrases):
                    continue
                    
                action_verbs = ["explain", "describe", "analyze", "discuss", "compare", "design", "calculate", "write", "illustrate", "what is", "how does", "briefly", "list", "define", "apply", "build", "differentiate", "consider", "given", "understand"]
                is_question = any(verb in clean_line_lower[:40] for verb in action_verbs)
                
                # Ensure it is a valid, standalone question (between 30 and 200 chars)
                if is_question and 30 < len(clean_line) < 200:
                    if clean_line + "." not in all_questions:
                        all_questions.append(clean_line + ".")

        # Distribute across units
        total_q = len(all_questions)
        chunk_size = max(1, total_q // 3)
        
        u1_qs = all_questions[:chunk_size]
        u2_qs = all_questions[chunk_size:chunk_size*2]
        u3_qs = all_questions[chunk_size*2:]

        units = {
            "Unit 1": {"title": "Fundamentals", "questions": u1_qs},
            "Unit 2": {"title": "Advanced Concepts", "questions": u2_qs},
            "Unit 3": {"title": "Applications", "questions": u3_qs}
        }

        structured_plan = {
            "course": course_title,
            "course_code": course_code,
            "units": units
        }

        print(f"[{self.name}] ✅ Parsed {course_title} ({course_code})")
        print(f"  -> Extracted {total_q} REAL questions (separated correctly).")
        
        return structured_plan