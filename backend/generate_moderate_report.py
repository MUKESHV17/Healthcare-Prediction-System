from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def create_moderate_risk_report():
    file_path = "Moderate_Risk_Diabetes_Report.pdf"
    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter

    # Header
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.darkblue)
    c.drawCentredString(width / 2, height - 50, "MEDI-LAB DIAGNOSTICS")
    
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, height - 70, "Comprehensive Health Screening Report")
    
    # Patient Details
    c.line(50, height - 90, width - 50, height - 90)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 120, "Patient Name: Jane Doe")
    c.drawString(50, height - 140, "Age: 45")
    c.drawString(50, height - 160, "Sex: Female")
    c.drawString(300, height - 120, "Date: 05 Feb 2026")
    c.drawString(300, height - 140, "Ref Dr: Dr. A. Smith")
    
    c.line(50, height - 180, width - 50, height - 180)

    # Values chosen for Moderate Risk (Probability ~40-75%)
    # High enough to be concerning but not extreme
    metrics = [
        ("Test Parameter", "Observed Value", "Reference Range"),
        ("Fasting Glucose", "135 mg/dL", "70-100 mg/dL"),  # Pre-diabetic range
        ("Blood Pressure", "135/85 mmHg", "120/80 mmHg"), # Pre-hypertension
        ("BMI (Body Mass Index)", "29.5 kg/m2", "18.5-24.9 kg/m2"), # Overweight
        ("Insulin", "160 mu U/ml", "15-276 mu U/ml"),     # Elevated
        ("Skin Thickness", "30 mm", "10-50 mm"),
        ("Pregnancies", "2", "N/A"),
        ("Diabetes Pedigree Function", "0.65", "< 0.5 Low Risk") # Moderate genetic risk
    ]

    y = height - 220
    
    # Table Header
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, metrics[0][0])
    c.drawString(250, y, metrics[0][1])
    c.drawString(450, y, metrics[0][2])
    y -= 20
    c.line(50, y + 15, width - 50, y + 15)
    
    # Table Rows
    c.setFont("Helvetica", 11)
    for param, value, ref in metrics[1:]:
        y -= 25
        c.drawString(50, y, param)
        c.drawString(250, y, value)
        c.drawString(450, y, ref)

    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(width / 2, 50, "This is a computer-generated report for testing purposes.")
    
    c.save()
    print(f"✅ Generated report: {file_path}")

if __name__ == "__main__":
    create_moderate_risk_report()
