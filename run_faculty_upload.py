import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.coordinator import QuestionPaperCoordinator
from tools.retrieval_tool import RetrievalTool

def main():
    print("\n" + "="*60)
    print("  🎓 FACULTY QUESTION PAPER GENERATION SYSTEM")
    print("="*60)

    # 1. Ask for Lesson Plan File (Supports PDF and TXT)
    print("Available Lesson Plans in data/lesson_plans/:")
    lp_dir = "data/lesson_plans"
    available_files = []
    
    if os.path.exists(lp_dir):
        for f in os.listdir(lp_dir):
            if f.lower().endswith(".txt") or f.lower().endswith(".pdf"):
                print(f"  - {f}")
                available_files.append(f)
    
    while True:
        user_input = input("\n👉 Enter the Lesson Plan filename (e.g., Deep_Learning_LP.pdf): ").strip()
        
        # Check exact match first
        if user_input in available_files:
            lesson_plan_file = user_input
            break
            
        # Check if user forgot the extension
        matched_file = None
        for f in available_files:
            if f.lower().startswith(user_input.lower()):
                matched_file = f
                break
                
        if matched_file:
            lesson_plan_file = matched_file
            print(f"🔍 Auto-detected file: {lesson_plan_file}")
            break
            
        print("❌ File not found. Please try again.")

    lesson_plan_path = os.path.join(lp_dir, lesson_plan_file)

    # 2. Extract a clean subject name from the filename
    subject = lesson_plan_file.replace("_LP.pdf", "").replace("_Lesson_Plan.txt", "").replace("_", " ")

    # 3. Ask for Exam Type
    print("\n👉 Select Exam Type:")
    print("  1. ISA1")
    print("  2. ISA2")
    print("  3. ESA")
    exam_choice = input("Enter choice (1/2/3): ").strip()
    
    if exam_choice == "1":
        exam_type = "ISA1"
    elif exam_choice == "2":
        exam_type = "ISA2"
    elif exam_choice == "3":
        exam_type = "ESA"
    else:
        print("❌ Invalid choice. Exiting.")
        return

    # 4. Dynamically Find the Batch
    tool = RetrievalTool()
    target_batch = tool.get_available_batch(subject, exam_type)
    
    if not target_batch:
        print(f"\n❌ ERROR: No past papers found for {subject} - {exam_type} in the database.")
        print("Please ensure the database has been built properly.")
        return
        
    print(f"\n🔍 Found available batch for {exam_type}: {target_batch}")

    # 5. Ask for Total Marks
    while True:
        try:
            total_marks = int(input(f"\n👉 Enter Total Marks for {exam_type}: "))
            if total_marks > 0:
                break
        except ValueError:
            pass
        print("❌ Please enter a valid number.")

    # 6. Execute the Coordinator Workflow
    print(f"\n🚀 Generating {exam_type} Paper for {subject} ({total_marks} Marks)...")
    print("-" * 40)
    
    coordinator = QuestionPaperCoordinator()
    coordinator.run_workflow(
        subject=subject,
        exam_type=exam_type,
        target_batch=target_batch,
        lesson_plan_path=lesson_plan_path,
        total_marks=total_marks
    )

if __name__ == "__main__":
    main()