import os
import json
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from PIL import Image, ImageDraw, ImageFont

def generate_samples(output_dir="sample_documents"):
    os.makedirs(output_dir, exist_ok=True)
    styles = getSampleStyleSheet()

    # Colors
    NAVY = colors.HexColor('#0f172a')
    INDIGO = colors.HexColor('#4338ca')
    BORDER_COLOR = colors.HexColor('#cbd5e1')
    LIGHT_BG = colors.HexColor('#f8fafc')

    # Typography
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, leading=22, alignment=1, textColor=NAVY)
    sub_title = ParagraphStyle('DocSub', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=14, alignment=1, textColor=INDIGO)
    body_style = ParagraphStyle('DocBody', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=13, textColor=NAVY)
    bold_body = ParagraphStyle('DocBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=13, textColor=NAVY)

    # ----------------------------------------------------
    # 1. VALID MARKSHEET (Rohan Sharma)
    # ----------------------------------------------------
    valid_pdf_path = os.path.join(output_dir, "valid_marksheet.pdf")
    doc1 = SimpleDocTemplate(valid_pdf_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story1 = []

    story1.append(Paragraph("DELHI TECHNOLOGICAL INSTITUTE", title_style))
    story1.append(Paragraph("AFFILIATED TO STATE TECHNICAL UNIVERSITY • ESTD 1988", sub_title))
    story1.append(Spacer(1, 8))
    story1.append(HRFlowable(width="100%", thickness=1.5, color=INDIGO, spaceBefore=2, spaceAfter=12))

    story1.append(Paragraph("<b>ACADEMIC MARKSHEET & GRADE CARD</b>", ParagraphStyle('CenterHead', parent=bold_body, alignment=1, fontSize=12)))
    story1.append(Spacer(1, 10))

    # Student Info Table
    info_data = [
        [Paragraph("<b>Candidate Name:</b>", bold_body), Paragraph("Rohan Sharma", body_style),
         Paragraph("<b>Roll Number:</b>", bold_body), Paragraph("2021-CS-104", body_style)],
        [Paragraph("<b>Course / Branch:</b>", bold_body), Paragraph("Bachelor of Technology in Computer Science", body_style),
         Paragraph("<b>Academic Year:</b>", bold_body), Paragraph("2020-2024", body_style)],
        [Paragraph("<b>Institute:</b>", bold_body), Paragraph("Delhi Technological Institute", body_style),
         Paragraph("<b>Certificate No:</b>", bold_body), Paragraph("CR-889210", body_style)]
    ]
    t_info = Table(info_data, colWidths=[110, 190, 100, 140])
    t_info.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story1.append(t_info)
    story1.append(Spacer(1, 14))

    # Subjects Table
    subjects = [
        ["Paper / Subject Name", "Max Marks", "Marks Obtained", "Grade"],
        ["Data Structures", "100", "85", "A"],
        ["Operating Systems", "100", "78", "B+"],
        ["Computer Networks", "100", "82", "A"],
        ["Database Systems", "100", "80", "A"],
        ["Software Engineering", "100", "75", "B+"],
        ["Artificial Intelligence", "100", "80", "A"]
    ]
    t_subj = Table([[Paragraph(f"<b>{c}</b>" if r == 0 else c, body_style) for c in row] for r, row in enumerate(subjects)], colWidths=[240, 100, 120, 80])
    t_subj.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), LIGHT_BG),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story1.append(t_subj)
    story1.append(Spacer(1, 12))

    # Summary Row
    summary_data = [
        [
            Paragraph("<b>Total Marks: 480 / 600</b>", bold_body),
            Paragraph("<b>Percentage: 80.0%</b>", bold_body),
            Paragraph("<b>Result: PASS</b>", bold_body),
            Paragraph("<b>Division: First Class with Distinction</b>", bold_body)
        ]
    ]
    t_sum = Table(summary_data, colWidths=[140, 120, 100, 180])
    t_sum.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story1.append(t_sum)
    story1.append(Spacer(1, 16))

    # Footer with Signatory and Embedded QR code
    qr_payload = json.dumps({
        "student_name": "Rohan Sharma",
        "roll_number": "2021-CS-104",
        "certificate_number": "CR-889210",
        "institution": "Delhi Technological Institute"
    })
    qr_widget = QrCodeWidget(qr_payload)
    qr_widget.barWidth = 65
    qr_widget.barHeight = 65
    d_qr = Drawing(75, 75)
    d_qr.add(qr_widget)

    footer_table = Table([
        [
            d_qr,
            Paragraph("<b>Date of Issue:</b> 15/06/2024<br/><font size=7 color='#64748b'>Scan QR code to verify credential authenticity.</font>", body_style),
            Paragraph("<b>Dr. S. K. Malhotra</b><br/>Controller of Examinations<br/>Delhi Technological Institute", ParagraphStyle('SignRight', parent=body_style, alignment=2))
        ]
    ], colWidths=[90, 250, 200])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story1.append(footer_table)

    doc1.build(story1)

    # ----------------------------------------------------
    # 2. TAMPERED MARKSHEET (Forged Marks & Mismatched Total)
    # ----------------------------------------------------
    tampered_pdf_path = os.path.join(output_dir, "tampered_marksheet.pdf")
    doc2 = SimpleDocTemplate(tampered_pdf_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story2 = []

    story2.append(Paragraph("DELHI TECHNOLOGICAL INSTITUTE", title_style))
    story2.append(Paragraph("AFFILIATED TO STATE TECHNICAL UNIVERSITY • ESTD 1988", sub_title))
    story2.append(Spacer(1, 8))
    story2.append(HRFlowable(width="100%", thickness=1.5, color=INDIGO, spaceBefore=2, spaceAfter=12))

    story2.append(Paragraph("<b>ACADEMIC MARKSHEET & GRADE CARD</b>", ParagraphStyle('CenterHead2', parent=bold_body, alignment=1, fontSize=12)))
    story2.append(Spacer(1, 10))

    story2.append(t_info)
    story2.append(Spacer(1, 14))

    # Subjects sum to 480
    story2.append(t_subj)
    story2.append(Spacer(1, 12))

    # Forged Total Marks 560 instead of 480, and Percentage 93.3% instead of 80.0%
    forged_summary = [
        [
            Paragraph("<b>Total Marks: 560 / 600</b>", bold_body),
            Paragraph("<b>Percentage: 93.3%</b>", bold_body),
            Paragraph("<b>Result: PASS</b>", bold_body),
            Paragraph("<b>Division: First Class with Distinction</b>", bold_body)
        ]
    ]
    t_forged = Table(forged_summary, colWidths=[140, 120, 100, 180])
    t_forged.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story2.append(t_forged)
    story2.append(Spacer(1, 16))
    story2.append(footer_table)

    doc2.build(story2)

    # ----------------------------------------------------
    # 3. SAMPLE CERTIFICATE (Ananya Verma)
    # ----------------------------------------------------
    cert_pdf_path = os.path.join(output_dir, "sample_certificate.pdf")
    doc3 = SimpleDocTemplate(cert_pdf_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story3 = []

    story3.append(Paragraph("NATIONAL INSTITUTE OF ENGINEERING", title_style))
    story3.append(Paragraph("AUTONOMOUS DECLARED INSTITUTION OF HIGHER EDUCATION", sub_title))
    story3.append(Spacer(1, 16))
    story3.append(Paragraph("<b>PROVISIONAL DEGREE CERTIFICATE</b>", ParagraphStyle('CertHead', parent=bold_body, alignment=1, fontSize=15, textColor=INDIGO)))
    story3.append(Spacer(1, 20))

    cert_text = (
        "This is to certify that <b>Ananya Verma</b> bearing Registration Number <b>2022-EC-205</b> "
        "has successfully completed the prescribed curriculum and passed the examination for the "
        "degree of <b>Bachelor of Engineering in Electronics</b> from National Institute of Engineering "
        "in the academic year <b>2021-2025</b> with <b>First Class with Distinction</b>."
    )
    story3.append(Paragraph(cert_text, ParagraphStyle('CertBody', parent=body_style, fontSize=11, leading=18, alignment=4)))
    story3.append(Spacer(1, 25))

    cert_meta = [
        [
            Paragraph("<b>Certificate No:</b> CR-991024", body_style),
            Paragraph("<b>Date of Issue:</b> 20/05/2025", body_style),
            Paragraph("<b>Registrar</b><br/>National Institute of Engineering", ParagraphStyle('RegSign', parent=body_style, alignment=2))
        ]
    ]
    t_cm = Table(cert_meta, colWidths=[180, 180, 180])
    story3.append(t_cm)

    doc3.build(story3)

    print("Sample test documents successfully generated in:", output_dir)

if __name__ == "__main__":
    generate_samples()
