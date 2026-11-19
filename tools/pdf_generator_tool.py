from fpdf import FPDF
import os
import re

class PDFGeneratorTool:
    def generate(self, final_paper, output_filename):
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()
        pdf.set_margins(10, 10, 10)
        
        exam_type = final_paper.get('exam_type', 'ISA')
        
        # --- KLE TECH HEADER ---
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 8, "KLE Technological University", ln=True, align='C')
        pdf.set_font("Arial", 'I', 9)
        pdf.cell(0, 5, "School of Computer Science and Engineering (Artificial Intelligence)", ln=True, align='C')
        pdf.ln(2)
        
        # --- TABLE 1: COURSE DETAILS ---
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(190, 8, f"Model Question Paper for {exam_type} Examination", border=1, ln=True, align='C')
        
        subject = str(final_paper.get('subject', 'Unknown')).encode('latin-1', 'ignore').decode('latin-1')
        course_code = str(final_paper.get('course_code', 'Auto')).encode('latin-1', 'ignore').decode('latin-1')
        
        pdf.cell(45, 8, f"Course Code: {course_code}", border=1, align='L')
        pdf.cell(145, 8, f"Course Title: {subject}", border=1, ln=True, align='L')
        
        pdf.cell(45, 8, f"Duration: {final_paper.get('duration', '2 Hours')}", border=1, align='L')
        pdf.cell(145, 8, f"Max. Marks: {final_paper.get('total_marks', 30)}", border=1, ln=True, align='L')
        
        pdf.set_font("Arial", '', 8)
        pdf.cell(45, 10, "Note:", border=1, align='C')
        pdf.multi_cell(145, 10, final_paper.get('instructions', ''), border=1, align='L')
        
        pdf.ln(4)

        # --- TABLE 2: QUESTIONS ---
        pdf.set_font("Arial", 'B', 8)
        col_widths = (10, 110, 12, 12, 12, 12, 22)
        
        with pdf.table(col_widths=col_widths, text_align="CENTER", line_height=6) as table:
            header = table.row()
            header.cell("Q.No")
            header.cell("Questions")
            header.cell("Marks")
            header.cell("CO")
            header.cell("BL")
            header.cell("PO")
            header.cell("PI Code")

            co_to_bl = {"CO1": "L1", "CO2": "L2", "CO3": "L3", "CO4": "L4", "CO5": "L5"}
            po_to_pi = {"PO1": "2.1.3", "PO2": "2.4.2", "PO3": "2.1.2", "PO4": "3.1.3"} 

            pdf.set_font("Arial", '', 8)
            
            for section in final_paper.get("sections", []):
                if not section["questions"]:
                    continue

                # ONLY print UNIT Header if it's an ESA paper
                if exam_type == "ESA":
                    row = table.row()
                    row.cell(f"UNIT-{section['unit'].replace('Unit ', '')}", colspan=7, align="LEFT")

                for main_q in section["questions"]:
                    for q in main_q["sub_questions"]:
                        row = table.row()
                        q_num = q.get('q_no', '?')
                        
                        raw_text = re.sub(r'[^\x00-\x7F]+', '', q.get('text', '')) 
                        q_text = re.sub(r'\s+', ' ', raw_text).strip()
                        
                        q_marks = str(q.get('marks', 0))
                        q_co = q.get('CO', '?').replace('CO', '')
                        q_bl = co_to_bl.get("CO"+q_co, 'L2')
                        
                        po_raw = q.get('PO', '?')
                        q_po = po_raw.split(',')[0].strip().replace('PO', '') if po_raw else '?'
                        q_pi = po_to_pi.get("PO"+q_po, "2.1.3")
                        
                        row.cell(q_num)
                        row.cell(q_text, align="LEFT") 
                        row.cell(q_marks)
                        row.cell(q_co)
                        row.cell(q_bl)
                        row.cell(q_po)
                        row.cell(q_pi)

        pdf.ln(5)
        pdf.set_font("Arial", 'I', 8)
        pdf.cell(0, 10, "*** End of Question Paper ***", align='C')

        os.makedirs("output", exist_ok=True)
        pdf.output(output_filename)
        print(f"📄 PDF Generated successfully: {output_filename}")