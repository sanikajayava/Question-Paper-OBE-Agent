
from fpdf import FPDF
import os
import re


class ValuationTool:
    """
    Generates a Scheme of Valuation PDF
    using the final question paper JSON.
    """

    def clean_text(self, text):
        """Clean text for standard Arial PDF font."""
        text = str(text)
        text = text.encode("latin-1", "ignore").decode("latin-1")
        return re.sub(r"\s+", " ", text).strip()

    def write_text(self, pdf, text, height=6):
        """
        Safely write multiline text using the full
        available page width.
        """
        width = pdf.w - pdf.l_margin - pdf.r_margin

        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(
            w=width,
            h=height,
            text=self.clean_text(text)
        )

    def generate(self, final_paper, output_filename):

        pdf = FPDF(orientation="P", unit="mm", format="A4")

        pdf.set_margins(15, 15, 15)
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        subject = self.clean_text(
            final_paper.get("subject", "Unknown")
        )

        course_code = self.clean_text(
            final_paper.get("course_code", "Auto")
        )

        exam_type = self.clean_text(
            final_paper.get("exam_type", "ISA")
        )

        # ------------------------------------------------
        # HEADER
        # ------------------------------------------------

        pdf.set_font("Arial", "B", 14)
        pdf.cell(
            0, 8,
            "KLE Technological University",
            ln=True,
            align="C"
        )

        pdf.set_font("Arial", "B", 12)
        pdf.cell(
            0, 7,
            "SCHEME OF VALUATION",
            ln=True,
            align="C"
        )

        pdf.set_font("Arial", "", 9)
        pdf.cell(
            0, 6,
            "School of Computer Science and Engineering (Artificial Intelligence)",
            ln=True,
            align="C"
        )

        pdf.ln(5)

        # ------------------------------------------------
        # COURSE DETAILS
        # ------------------------------------------------

        pdf.set_font("Arial", "B", 10)

        self.write_text(pdf, f"Subject: {subject}")
        self.write_text(pdf, f"Course Code: {course_code}")
        self.write_text(pdf, f"Examination: {exam_type}")
        self.write_text(
            pdf,
            f"Maximum Marks: {final_paper.get('total_marks', 0)}"
        )

        pdf.ln(5)

        # ------------------------------------------------
        # QUESTION-WISE MARKING SCHEME
        # ------------------------------------------------

        pdf.set_font("Arial", "B", 11)
        self.write_text(pdf, "Question-wise Marking Scheme", 8)

        for section in final_paper.get("sections", []):

            questions = section.get("questions", [])

            if not questions:
                continue

            pdf.ln(3)

            pdf.set_font("Arial", "B", 10)

            unit_name = section.get("unit", "Questions")
            self.write_text(pdf, unit_name, 7)

            for main_q in questions:

                for q in main_q.get("sub_questions", []):

                    q_no = self.clean_text(q.get("q_no", "?"))
                    question = self.clean_text(q.get("text", ""))
                    marks = float(q.get("marks", 0))

                    # Question heading
                    pdf.set_font("Arial", "B", 9)

                    self.write_text(
                        pdf,
                        f"Question {q_no} ({marks:g} Marks)",
                        6
                    )

                    # Question text
                    pdf.set_font("Arial", "", 9)

                    self.write_text(pdf, question, 6)

                    # Marking criteria
                    pdf.set_font("Arial", "I", 9)

                    self.write_text(
                        pdf,
                        "Suggested Evaluation Criteria:",
                        6
                    )

                    pdf.set_font("Arial", "", 9)

                    # Generic marking rubric
                    if marks <= 0:
                        criteria = []

                    elif marks <= 2:
                        criteria = [
                            ("Correct concept / definition", marks)
                        ]

                    elif marks <= 5:
                        criteria = [
                            ("Correct concept / definition", 1),
                            ("Explanation of key points", marks - 1)
                        ]

                    else:
                        criteria = [
                            ("Introduction / basic concept", 2),
                            (
                                "Explanation of important points",
                                marks * 0.5
                            ),
                            (
                                "Examples / application / conclusion",
                                marks - 2 - marks * 0.5
                            )
                        ]

                    for criterion, allocated_marks in criteria:

                        if allocated_marks > 0:

                            self.write_text(
                                pdf,
                                f"- {criterion}: {allocated_marks:g} marks",
                                5
                            )

                    pdf.ln(4)

        # ------------------------------------------------
        # FOOTER
        # ------------------------------------------------

        pdf.ln(5)

        pdf.set_font("Arial", "I", 9)

        pdf.cell(
            0, 8,
            "*** End of Scheme of Valuation ***",
            align="C"
        )

        # ------------------------------------------------
        # SAVE PDF
        # ------------------------------------------------

        output_dir = os.path.dirname(output_filename)

        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        pdf.output(output_filename)

        print(
            f"Scheme of Valuation generated successfully: "
            f"{output_filename}"
        )
