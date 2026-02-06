from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os
import datetime
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def generate_chart(data, disease_type):
    """
    Generates a bar chart comparing patient values to approximate normal upper limits.
    Returns a BytesIO object containing the chart image.
    """
    # Define approx upper limits
    limits = {
        "glucose": 140, "bloodpressure": 120, "bmi": 25, "cholesterol": 200, "trestbps": 120,
        "thalach": 150, "age": 80, "insulin": 100, "skin_thickness": 30, "pregnancies": 5
    }
    
    # Filter numeric data
    labels = []
    values = []
    norms = []
    
    for key, info in data.items():
        k = key.lower().replace(" ", "")
        val = info.get("value", 0)
        
        # Skip non-visual or categorical fields if needed (like sex, pointers)
        if k in ["sex", "cp", "fbs", "restecg", "exang", "slope", "ca", "thal", "diabetespedigreefunction", "dpf"]:
            continue
            
        limit = 0
        # Find matching limit
        for lk, lv in limits.items():
            if lk in k:
                limit = lv
                break
        if limit == 0: limit = 100 # default scale
        
        labels.append(key[:10]) # truncate
        values.append(val)
        norms.append(limit)
        
    if not labels:
        return None

    # Plot
    fig, ax = plt.subplots(figsize=(6, 3))
    x = np.arange(len(labels))
    width = 0.35
    
    rects1 = ax.bar(x - width/2, values, width, label='Patient', color='#8884d8')
    rects2 = ax.bar(x + width/2, norms, width, label='Normal Limit', color='#82ca9d')

    ax.set_ylabel('Value')
    ax.set_title('Health Metrics vs Normal Limits')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.legend()
    
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    plt.close(fig)
    buf.seek(0)
    return buf

def generate_pdf_report(patient_data, prediction_result, risk_level, clinical_summary, disease_type, patient_name="Guest Patient", gender="N/A"):
    """
    Generates a strict MedPro PDF report.
    patient_data: dict of { feature: { value, source } }
    """
    
    reports_dir = "generated_reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    filename = f"MedPro_Report_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    filepath = os.path.join(reports_dir, filename)
    
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # --- 1. Header (Logo & Branding) ---
    logo_path = os.path.join("static", "logo.png")
    if os.path.exists(logo_path):
        logo_img = RLImage(logo_path, width=0.8*inch, height=0.8*inch)
        logo_img.hAlign = 'LEFT'
        
        # Create a table for header to align logo and text
        header_text = [
            [logo_img, Paragraph("<b>MedPro AI Healthcare System</b><br/><font size='10' color='grey'>Hospital: AI Generated Partner Hospital | Date: " + datetime.datetime.now().strftime('%Y-%m-%d') + "</font>", styles['Normal'])]
        ]
        head_table = Table(header_text, colWidths=[1*inch, 5*inch])
        head_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (1,0), (1,0), 20),
        ]))
        story.append(head_table)
    else:
        header_style = ParagraphStyle('Header', parent=styles['Normal'], fontSize=10, textColor=colors.gray)
        story.append(Paragraph("<b>MedPro AI Healthcare System</b>", ParagraphStyle('BName', parent=header_style, fontSize=14, textColor=colors.darkblue)))
        story.append(Paragraph(f"Hospital: AI Generated Partner Hospital | Date: {datetime.datetime.now().strftime('%Y-%m-%d')}", header_style))
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("________________________________________________________________________", styles['Normal']))
    story.append(Spacer(1, 20))
    
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=28, textColor=colors.darkblue, alignment=1, spaceAfter=20)
    story.append(Paragraph(f"Medical Health Report: {disease_type.capitalize()}", title_style))

    # --- 2. Patient Details ---
    age = patient_data.get("Age", {}).get("value") or patient_data.get("age", {}).get("value", "N/A")
    sex_display = gender
    if gender in [1, "1"]: sex_display = "Male"
    elif gender in [0, "0"]: sex_display = "Female"
    
    p_data = [
        ["Patient Details", ""],
        ["Name:", f"{patient_name}"],
        ["Age:", f"{age}"],
        ["Sex:", f"{sex_display}"],
        ["Report ID:", f"MP-{datetime.datetime.now().strftime('%H%M%S')}"]
    ]
    t = Table(p_data, colWidths=[2*inch, 4*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), colors.aliceblue),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('FONTSIZE', (0,0), (-1,-1), 11),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 25))

    # --- 3. Medical Data Table ---
    story.append(Paragraph("Clinical Data Analysis", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    # Table Header
    obs_data = [["Parameter", "Patient Value", "Source", "Status"]]
    
    for key, info in patient_data.items():
        val = info.get("value", 0)
        src = info.get("source", "Unknown")
        
        # Determine Status (Simple logic)
        status = "Normal"
        # Simple thresholds for coloring
        v = float(val)
        k = key.lower()
        if "glucose" in k and v > 140: status = "High"
        elif "bp" in k and v > 130: status = "High"
        elif "chol" in k and v > 240: status = "High"
        elif "bmi" in k and v > 25: status = "Overweight"
        
        obs_data.append([key, str(val), src, status])

    t2 = Table(obs_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.grey),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t2)
    story.append(Spacer(1, 25))

    # --- 4. AI Assessment ---
    story.append(Paragraph("AI Assessment & Prediction", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    risk_color = "green"
    if risk_level == "High": risk_color = "red"
    elif risk_level == "Moderate": risk_color = "orange"
    
    story.append(Paragraph(f"Prediction Model Result: <font color='{risk_color}'><b>{prediction_result}</b></font>", styles['Normal']))
    story.append(Paragraph(f"Risk Level: <font color='{risk_color}'><b>{risk_level}</b></font>", styles['Normal']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>Clinical Summary:</b> {clinical_summary}", styles['Normal']))
    story.append(Spacer(1, 25))

    # --- 5. Visual Section (Charts) ---
    story.append(Paragraph("Visual Health Metrics", styles['Heading2']))
    story.append(Spacer(1, 10))
    chart_buf = generate_chart(patient_data, disease_type)
    if chart_buf:
        img = RLImage(chart_buf, width=6*inch, height=3*inch)
        story.append(img)
    story.append(Spacer(1, 25))

    # --- 6. Recommendations ---
    story.append(Paragraph("Recommendations", styles['Heading2']))
    story.append(Spacer(1, 10))
    recs = [
        "• Consult the suggested specialist department immediately.",
        "• Maintain a healthy diet and regular exercise routine.",
        "• Monitor vital signs regularly."
    ]
    if disease_type == "diabetes":
        recs.append("• Specific: Monitor blood glucose levels pre/post meals.")
    elif disease_type == "heart":
        recs.append("• Specific: Monitor blood pressure and cholesterol.")
        
    for r in recs:
        story.append(Paragraph(r, styles['Normal']))
        
    story.append(Spacer(1, 40))
    
    # --- 7. Footer ---
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, textColor=colors.gray, alignment=1)
    story.append(Paragraph("________________________________________________________________________", styles['Normal']))
    story.append(Spacer(1, 5))
    story.append(Paragraph("Generated by MedPro AI Healthcare | Disclaimer: This is an AI-assisted report and not a final diagnosis.", footer_style))

    doc.build(story)
    return filepath
