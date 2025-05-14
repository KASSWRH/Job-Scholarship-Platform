import os
import io
import re
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_RIGHT, TA_LEFT, TA_CENTER

# Register fonts for Arabic support
try:
    pdfmetrics.registerFont(TTFont('Arabic', 'static/fonts/NotoSansArabic-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('ArabicBold', 'static/fonts/NotoSansArabic-Bold.ttf'))
except:
    # Fallback if the font file doesn't exist
    pass

def get_cv_template_content(template, data, rtl=False):
    """Generate CV content based on template and user data."""
    styles = getSampleStyleSheet()
    
    # Define RTL style if needed
    if rtl:
        styles.add(ParagraphStyle(
            name='RTL',
            fontName='Arabic',
            alignment=TA_RIGHT,
            fontSize=12,
            leading=14
        ))
        styles.add(ParagraphStyle(
            name='RTLHeading',
            fontName='ArabicBold',
            alignment=TA_RIGHT,
            fontSize=16,
            leading=18,
            spaceAfter=10
        ))
        text_style = styles['RTL']
        heading_style = styles['RTLHeading']
    else:
        styles.add(ParagraphStyle(
            name='Heading',
            fontName='Helvetica-Bold',
            fontSize=16,
            leading=18,
            spaceAfter=10
        ))
        text_style = styles['Normal']
        heading_style = styles['Heading']
    
    # Basic user information
    content = []
    
    # Name and contact info header
    name = data.get('name', '')
    email = data.get('email', '')
    phone = data.get('phone', '')
    content.append(Paragraph(name, heading_style))
    content.append(Paragraph(f"{email} | {phone}", text_style))
    content.append(Spacer(1, 12))
    
    # Professional Summary
    content.append(Paragraph("Professional Summary", heading_style))
    summary = data.get('summary', '')
    content.append(Paragraph(summary, text_style))
    content.append(Spacer(1, 12))
    
    # Education
    content.append(Paragraph("Education", heading_style))
    education = data.get('education', '')
    content.append(Paragraph(education, text_style))
    content.append(Spacer(1, 12))
    
    # Work Experience
    content.append(Paragraph("Work Experience", heading_style))
    experience = data.get('experience', '')
    content.append(Paragraph(experience, text_style))
    content.append(Spacer(1, 12))
    
    # Skills
    content.append(Paragraph("Skills", heading_style))
    skills = data.get('skills', '')
    content.append(Paragraph(skills, text_style))
    content.append(Spacer(1, 12))
    
    return content

def get_cover_letter_template_content(template, data, rtl=False):
    """Generate cover letter content based on template and user data."""
    styles = getSampleStyleSheet()
    
    # Define RTL style if needed
    if rtl:
        styles.add(ParagraphStyle(
            name='RTL',
            fontName='Arabic',
            alignment=TA_RIGHT,
            fontSize=12,
            leading=14
        ))
        styles.add(ParagraphStyle(
            name='RTLHeading',
            fontName='ArabicBold',
            alignment=TA_RIGHT,
            fontSize=16,
            leading=18,
            spaceAfter=10
        ))
        text_style = styles['RTL']
        heading_style = styles['RTLHeading']
    else:
        text_style = styles['Normal']
        heading_style = styles['Heading1']
    
    # Basic content
    content = []
    
    # Sender information
    name = data.get('name', '')
    email = data.get('email', '')
    phone = data.get('phone', '')
    date = datetime.now().strftime("%B %d, %Y")
    
    # Add sender info
    content.append(Paragraph(name, text_style))
    content.append(Paragraph(email, text_style))
    content.append(Paragraph(phone, text_style))
    content.append(Paragraph(date, text_style))
    content.append(Spacer(1, 12))
    
    # Recipient information
    company = data.get('company', '')
    position = data.get('position', '')
    
    # Add recipient info
    content.append(Paragraph(f"RE: Application for {position} position at {company}", heading_style))
    content.append(Spacer(1, 12))
    
    # Greeting
    content.append(Paragraph("Dear Hiring Manager,", text_style))
    content.append(Spacer(1, 12))
    
    # Body paragraphs
    introduction = data.get('introduction', '')
    body = data.get('body', '')
    conclusion = data.get('conclusion', '')
    
    content.append(Paragraph(introduction, text_style))
    content.append(Spacer(1, 6))
    content.append(Paragraph(body, text_style))
    content.append(Spacer(1, 6))
    content.append(Paragraph(conclusion, text_style))
    content.append(Spacer(1, 12))
    
    # Closing
    content.append(Paragraph("Sincerely,", text_style))
    content.append(Spacer(1, 24))
    content.append(Paragraph(name, text_style))
    
    return content

def generate_cv(user, template, data, upload_folder):
    """Generate a CV PDF document using the provided template and data."""
    # Generate a unique filename
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f"cv_{user.id}_{timestamp}.pdf"
    file_path = os.path.join(upload_folder, filename)
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Determine if RTL is needed
    rtl = template.is_arabic
    
    # Get the content
    content = get_cv_template_content(template, data, rtl)
    
    # Build the document
    doc.build(content)
    
    return filename

def generate_cover_letter(user, template, data, upload_folder):
    """Generate a cover letter PDF document using the provided template and data."""
    # Generate a unique filename
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f"cover_letter_{user.id}_{timestamp}.pdf"
    file_path = os.path.join(upload_folder, filename)
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Determine if RTL is needed
    rtl = template.is_arabic
    
    # Get the content
    content = get_cover_letter_template_content(template, data, rtl)
    
    # Build the document
    doc.build(content)
    
    return filename
