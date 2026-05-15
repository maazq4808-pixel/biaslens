from fpdf import FPDF

def clean_text(text):
    lines = text.split("\n")
    lines = [line for line in lines if not line.startswith("#")]
    text = "\n".join(lines)
    text = text.replace("\u2014", "-")
    text = text.replace("\u2013", "-")
    text = text.replace("\u2018", "'")
    text = text.replace("\u2019", "'")
    text = text.replace("\u201c", '"')
    text = text.replace("\u201d", '"')
    text = text.replace("\u2022", "-")
    text = text.encode("latin-1", "replace").decode("latin-1")
    return text.strip()

def generate_report(all_findings):
    pdf =  FPDF()
    pdf.add_page()
    pdf.set_font("Arial","B", 24)
    pdf.cell(200,15,"Biaslens- Bias Report", ln= True, align = "C")
    demographic_cols= set(f["demographic_col"] for f in all_findings)
    for col in demographic_cols:
        pdf.add_page()
        pdf.image(f"chart_{col}.png", x= 10, w=180)
        pdf.ln(10)
        for finding in all_findings:
            if finding["demographic_col"] == col:
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, f"{finding['group']} ({finding['demographic_col']})", ln=True)
                pdf.set_font("Arial", "", 12)
                pdf.multi_cell(0, 10, clean_text(finding["explanation"]))
                pdf.ln(5)
    pdf.output("report.pdf")