import streamlit as st
from openai import OpenAI
import datetime
import re
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image, NextPageTemplate
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
import datetime
import re
import os
import uuid
from reportlab.platypus import Frame, PageTemplate, BaseDocTemplate, PageBreak
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image, NextPageTemplate
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import datetime
import ssl
import logging
import json
import os
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
import re
import tempfile
from PIL import Image as PILImage
import io
from typing import Optional, Dict, Any

# Constants
# Long Description
long_description = """
KerjayaKu is an AI-powered portal designed to help fresh graduates and young professionals strategically navigate their career development journey. By integrating cutting-edge artificial intelligence, KerjayaKu assesses your education profile, aspirations, personality traits, current skillset, and problem-solving abilities, along with social-emotional learning skills. It then delivers personalized insights to help you stay competitive in today’s dynamic job market.

### Key Features of KerjayaKu

1. **Gap Identification**  
   KerjayaKu evaluates your existing skills and compares them to the competencies required for your desired career path. By identifying gaps in technical, soft, and strategic skills, the platform provides a clear roadmap for improvement.  

2. **Reskilling and Upskilling Recommendations**  
   Based on AI-driven analytics, KerjayaKu suggests relevant courses, certifications, and training programs that align with your career goals. This ensures you are continually learning skills that are in demand and future-proof.

3. **Portfolio Building**  
   The portal guides you in building a robust professional portfolio, highlighting projects, experiences, and skills that showcase your readiness for your dream roles. This feature enhances your ability to stand out in competitive job applications.

4. **Employer Expectations**  
   KerjayaKu pinpoints value-added competencies that employers look for in specific roles. You’ll receive tailored suggestions to develop qualities like leadership, critical thinking, adaptability, and innovation.

5. **Strategic Career Direction**  
   Through personality and aspiration mapping, the platform ensures your career development plan aligns with both your passions and the market’s needs, empowering you to pursue jobs where you’ll thrive.

### Why It Matters for Young Professionals  
Fresh graduates often struggle to transition from academia to the workforce due to a lack of clarity in skill requirements and strategic career planning. KerjayaKu bridges this gap by offering personalized, actionable insights to help you reskill, upskill, and showcase your abilities effectively. With its AI-driven precision, the portal provides a roadmap to build confidence, enhance employability, and unlock opportunities tailored to your goals.

KerjayaKu equips you not just for a job, but for a career that aligns with your aspirations and the future of work.
"""
EDUCATION_LEVELS = [
    "No formal education",
    "Primary school",
    "Secondary school / High school",
    "Diploma",
    "Bachelor's degree",
    "Master's degree",
    "Doctorate (PhD)",
    "Professional qualification (e.g., ACCA)"
]

FIELDS_OF_STUDY = [
    "Arts and Humanities",
    "Business and Management",
    "Engineering and Technology",
    "Computer Science / IT",
    "Health and Medicine",
    "Natural Sciences",
    "Social Sciences",
    "Law",
    "Education",
    "Others"
]

LANGUAGES = [
    "Arabic", "Bengali", "Burmese", "Czech", "Danish", "Dutch", "English",
    "Filipino/Tagalog", "Finnish", "French", "German", "Greek", "Hebrew",
    "Hindi", "Hungarian", "Indonesian/Malay", "Italian", "Japanese",
    "Kannada", "Korean", "Mandarin Chinese", "Marathi", "Nepali",
    "Norwegian", "Persian (Farsi)", "Polish", "Portuguese", "Punjabi",
    "Russian", "Sinhala", "Spanish", "Swahili", "Swedish", "Tamil",
    "Telugu", "Thai", "Turkish", "Ukrainian", "Urdu", "Vietnamese",
    "Others"
]

COUNTRIES = [
    "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda",
    "Argentina", "Armenia", "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain",
    "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan",
    "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria",
    "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada",
    "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros",
    "Congo", "Costa Rica", "Croatia", "Cuba", "Cyprus", "Czech Republic", "Denmark",
    "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador",
    "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji",
    "Finland", "France", "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Greece",
    "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras",
    "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", "Israel",
    "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati",
    "Korea, North", "Korea, South", "Kuwait", "Kyrgyzstan", "Laos", "Latvia",
    "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania",
    "Luxembourg", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta",
    "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova",
    "Monaco", "Mongolia", "Montenegro", "Morocco", "Mozambique", "Myanmar", "Namibia",
    "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria",
    "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Palestine", "Panama",
    "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal",
    "Qatar", "Romania", "Russia", "Rwanda", "Saint Kitts and Nevis", "Saint Lucia",
    "Saint Vincent and the Grenadines", "Samoa", "San Marino", "Sao Tome and Principe",
    "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore",
    "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan",
    "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria",
    "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Timor-Leste", "Togo", "Tonga",
    "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan", "Tuvalu", "Uganda",
    "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay",
    "Uzbekistan", "Vanuatu", "Vatican City", "Venezuela", "Vietnam", "Yemen",
    "Zambia", "Zimbabwe"
]

def create_custom_styles():
    base_styles = getSampleStyleSheet()
    
    try:
        pdfmetrics.registerFont(TTFont('Lato', 'fonts/Lato-Regular.ttf'))
        pdfmetrics.registerFont(TTFont('Lato-Bold', 'fonts/Lato-Bold.ttf'))
        pdfmetrics.registerFont(TTFont('Lato-Italic', 'fonts/Lato-Italic.ttf'))
        pdfmetrics.registerFont(TTFont('Lato-BoldItalic', 'fonts/Lato-BoldItalic.ttf'))
        base_font = 'Lato'
        bold_font = 'Lato-Bold'
    except:
        base_font = 'Helvetica'
        bold_font = 'Helvetica-Bold'

    custom_styles = {}
    
    # Normal style (both capitalized and lowercase versions)
    custom_styles['Normal'] = ParagraphStyle(
        'Normal',
        parent=base_styles['Normal'],
        fontSize=10,
        leading=12,
        fontName=base_font,
        alignment=TA_JUSTIFY
    )
    
    custom_styles['normal'] = custom_styles['Normal']  # Add lowercase version
    
    # TOC style
    custom_styles['TOCEntry'] = ParagraphStyle(
        'TOCEntry',
        parent=base_styles['Normal'],
        fontSize=12,
        leading=16,
        leftIndent=20,
        fontName=base_font,
        alignment=TA_JUSTIFY
    )
    
    custom_styles['toc'] = custom_styles['TOCEntry']  # Add lowercase version
    
    # Title style
    custom_styles['title'] = ParagraphStyle(
        'CustomTitle',
        parent=custom_styles['Normal'],  # Changed parent to our custom Normal
        fontSize=24,
        textColor=colors.HexColor('#2B6CB0'),
        alignment=TA_CENTER,
        spaceAfter=30,
        fontName=bold_font,
        leading=28.8
    )
    
    # Heading style
    custom_styles['heading'] = ParagraphStyle(
        'CustomHeading',
        parent=custom_styles['Normal'],  # Changed parent to our custom Normal
        fontSize=26,
        textColor=colors.HexColor('#1a1a1a'),
        spaceBefore=20,
        spaceAfter=15,
        fontName=bold_font,
        leading=40.5,
        alignment=TA_JUSTIFY
    )
    
    # Subheading style
    custom_styles['subheading'] = ParagraphStyle(
        'CustomSubheading',
        parent=custom_styles['Normal'],  # Changed parent to our custom Normal
        fontSize=12,
        textColor=colors.HexColor('#4A5568'),
        spaceBefore=15,
        spaceAfter=10,
        fontName=bold_font,
        leading=18.2,
        alignment=TA_JUSTIFY
    )
    
    # Content style
    custom_styles['content'] = ParagraphStyle(
        'CustomContent',
        parent=custom_styles['Normal'],  # Changed parent to our custom Normal
        fontSize=10,
        textColor=colors.HexColor('#1a1a1a'),
        alignment=TA_JUSTIFY,
        spaceBefore=6,
        spaceAfter=6,
        fontName=base_font,
        leading=15.4
    )
    
    # Bullet style
    custom_styles['bullet'] = ParagraphStyle(
        'CustomBullet',
        parent=custom_styles['Normal'],  # Changed parent to our custom Normal
        fontSize=10,
        textColor=colors.HexColor('#1a1a1a'),
        leftIndent=20,
        firstLineIndent=0,
        fontName=base_font,
        leading=15.4,
        alignment=TA_JUSTIFY
    )
    
    # Add any additional required style variations
    custom_styles['BodyText'] = custom_styles['Normal']
    custom_styles['bodytext'] = custom_styles['Normal']
    
    return custom_styles
def clean_text(text):
    """Clean and format text by removing HTML tags and normalizing line breaks"""
    if not text:
        return ""
    
    # Remove HTML tags while preserving line breaks
    text = re.sub(r'<br\s*/?>', '\n', text)  # Convert <br> to newlines
    text = re.sub(r'<para>', '', text)        # Remove <para> tags
    text = re.sub(r'</para>', '', text)       # Remove </para> tags
    text = re.sub(r'<[^>]+>', '', text)       # Remove any other HTML tags
    
    # Remove style tags
    text = re.sub(r'<userStyle>.*?</userStyle>', '', text)
    
    # Remove Markdown formatting while preserving structure
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
    text = re.sub(r'_(.*?)_', r'\1', text)        # Underscore
    
    # Improve spacing around punctuation
    text = re.sub(r':(?!\s)', ': ', text)         # Add space after colons
    text = re.sub(r'\s+([.,;!?])', r'\1', text)   # Remove space before punctuation
    text = re.sub(r'([.,;!?])(?!\s)', r'\1 ', text)  # Add space after punctuation
    
    # Handle multiple newlines
    text = re.sub(r'\n\s*\n', '\n\n', text)  # Normalize multiple newlines to double
    text = text.replace('\r\n', '\n')         # Normalize Windows line endings
    
    # Handle bullet points and dashes
    lines = text.split('\n')
    processed_lines = []
    for line in lines:
        line = line.strip()
        if line.startswith(('-', '•', '*')):
            line = '• ' + line[1:].strip()  # Normalize bullet points
        processed_lines.append(line)
    
    text = '\n'.join(processed_lines)
    
    return text.strip()

def process_content(content, styles, elements):
    """Process content with improved handling of lists and formatting"""
    if not content:
        return
    
    # Clean the content first
    content = clean_text(content)
    
    # Split content into sections
    sections = content.split('\n')
    current_paragraph = []
    
    i = 0
    while i < len(sections):
        line = sections[i].strip()
        
        # Skip empty lines
        if not line:
            if current_paragraph:
                para_text = ' '.join(current_paragraph)
                elements.append(Paragraph(para_text, styles['content']))
                elements.append(Spacer(1, 0.1*inch))
                current_paragraph = []
            i += 1
            continue
        
        # Handle headings
        if line.startswith('###') and not line.startswith('####'):
            if current_paragraph:
                para_text = ' '.join(current_paragraph)
                elements.append(Paragraph(para_text, styles['content']))
                current_paragraph = []
            
            heading_text = line.replace('###', '').strip()
            elements.append(Spacer(1, 0.3*inch))
            elements.append(Paragraph(heading_text, styles['subheading']))
            elements.append(Spacer(1, 0.15*inch))
            
        elif line.startswith('####'):
            if current_paragraph:
                para_text = ' '.join(current_paragraph)
                elements.append(Paragraph(para_text, styles['content']))
                current_paragraph = []
            
            subheading_text = line.replace('####', '').strip()
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph(subheading_text, styles['subheading']))
            elements.append(Spacer(1, 0.1*inch))
            
        # Handle bullet points
        elif line.startswith('•'):
            if current_paragraph:
                para_text = ' '.join(current_paragraph)
                elements.append(Paragraph(para_text, styles['content']))
                current_paragraph = []
            
            bullet_text = line[1:].strip()
            elements.append(Paragraph(bullet_text, styles['bullet']))
            
        # Handle tables
        elif '|' in line:
            if current_paragraph:
                para_text = ' '.join(current_paragraph)
                elements.append(Paragraph(para_text, styles['content']))
                current_paragraph = []
            
            # Collect table lines
            table_lines = [line]
            while i + 1 < len(sections) and '|' in sections[i + 1]:
                i += 1
                table_lines.append(sections[i].strip())
            
            # Process table
            if table_lines:
                process_table_content(table_lines, styles, elements)
                
        else:
            # Handle bold text and normal content
            processed_line = line
            if '**' in processed_line:
                processed_line = re.sub(r'\*\*(.*?)\*\*', lambda m: f'<b>{m.group(1)}</b>', processed_line)
            
            current_paragraph.append(processed_line)
        
        i += 1
    
    # Handle any remaining paragraph content
    if current_paragraph:
        para_text = ' '.join(current_paragraph)
        elements.append(Paragraph(para_text, styles['content']))
        elements.append(Spacer(1, 0.1*inch))
def create_formatted_table(table_data, styles):
    """Create a professionally formatted table with consistent styling"""
    # Ensure all rows have the same number of columns
    max_cols = max(len(row) for row in table_data)
    table_data = [row + [''] * (max_cols - len(row)) for row in table_data]
    
    # Calculate dynamic column widths based on content length
    total_width = 6.5 * inch
    col_widths = []
    
    if max_cols > 1:
        # Calculate max content length for each column
        col_lengths = [0] * max_cols
        for row in table_data:
            for i, cell in enumerate(row):
                content_length = len(str(cell))
                col_lengths[i] = max(col_lengths[i], content_length)
                
        # Distribute widths proportionally based on content length
        total_length = sum(col_lengths)
        for length in col_lengths:
            width = max((length / total_length) * total_width, inch)  # Minimum 1 inch
            col_widths.append(width)
            
        # Adjust widths to fit page
        scale = total_width / sum(col_widths)
        col_widths = [w * scale for w in col_widths]
    else:
        col_widths = [total_width]
    
    # Create table with calculated widths
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    # Define table style commands
    style_commands = [
        # Header styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E5E7EB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1F2937')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 15),
        ('TOPPADDING', (0, 0), (-1, 0), 15),
        
        # Content styling
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#374151')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 12),
        
        # Grid styling
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#2B6CB0')),
        
        # Alignment
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Cell padding
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]
    
    # Apply style commands
    table.setStyle(TableStyle(style_commands))
    
    # Apply word wrapping
    wrapped_data = []
    for i, row in enumerate(table_data):
        wrapped_row = []
        for cell in row:
            if isinstance(cell, (str, int, float)):
                # Use content style for all cells except headers
                style = styles['subheading'] if i == 0 else styles['content']
                wrapped_cell = Paragraph(str(cell), style)
            else:
                wrapped_cell = cell
            wrapped_row.append(wrapped_cell)
        wrapped_data.append(wrapped_row)
    
    # Create final table with wrapped data
    final_table = Table(wrapped_data, colWidths=col_widths, repeatRows=1)
    final_table.setStyle(TableStyle(style_commands))
    
    return final_table

def create_highlight_box(text, styles):
    """Create a highlighted box with improved styling"""
    content = Paragraph(f"• {text}", styles['content'])
    
    table = Table(
        [[content]],
        colWidths=[6*inch],
        style=TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.white),
            ('BORDER', (0,0), (-1,-1), 1, colors.black),
            ('PADDING', (0,0), (-1,-1), 15),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('BOX', (0,0), (-1,-1), 2, colors.HexColor('#E2E8F0')),
            ('BOTTOMPADDING', (0,0), (-1,-1), 18),
            ('TOPPADDING', (0,0), (-1,-1), 18),
        ])
    )
    
    return table

def process_table_content(lines, styles, elements):
    """Process table content with improved header handling"""
    table_data = []
    header_processed = False
    
    for line in lines:
        if '-|-' in line:  # Skip separator lines
            continue
            
        cells = [cell.strip() for cell in line.split('|')]
        cells = [cell for cell in cells if cell]
        
        if cells:
            # Handle cells with bold markers
            cells = [re.sub(r'\*\*(.*?)\*\*', r'\1', cell) for cell in cells]
            
            # Create paragraphs with appropriate styles
            if not header_processed:
                cells = [Paragraph(str(cell), styles['subheading']) for cell in cells]
                header_processed = True
            else:
                cells = [Paragraph(str(cell), styles['content']) for cell in cells]
                
            table_data.append(cells)
    
    if table_data:
        elements.append(Spacer(1, 0.2*inch))
        table = create_formatted_table(table_data, styles)
        elements.append(table)
        elements.append(Spacer(1, 0.2*inch))

def create_kerjayaku_info_page(styles):
    """Create the KerjayaKu information page"""
    elements = []
    
    # Title
    elements.append(Paragraph("KerjayaKu: AI-Driven Career Guidance for a Strategic Future", styles['heading']))
    elements.append(Spacer(1, 0.5*inch))
    
    # Introduction
    intro_text = """KerjayaKu is an AI-powered portal designed to help fresh graduates and young professionals strategically navigate their career development journey. By integrating cutting-edge artificial intelligence, KerjayaKu assesses your education profile, aspirations, personality traits, current skillset, and problem-solving abilities, along with social-emotional learning skills. It then delivers personalized insights to help you stay competitive in today's dynamic job market."""
    elements.append(Paragraph(intro_text, styles['content']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Key Features Section
    elements.append(Paragraph("Key Features of KerjayaKu", styles['subheading']))
    
    # Feature 1
    elements.append(Paragraph("1. Gap Identification", styles['point_title']))
    feature1_text = """KerjayaKu evaluates your existing skills and compares them to the competencies required for your desired career path. By identifying gaps in technical, soft, and strategic skills, the platform provides a clear roadmap for improvement."""
    elements.append(Paragraph(feature1_text, styles['content']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Feature 2
    elements.append(Paragraph("2. Reskilling and Upskilling Recommendations", styles['point_title']))
    feature2_text = """Based on AI-driven analytics, KerjayaKu suggests relevant courses, certifications, and training programs that align with your career goals. This ensures you are continually learning skills that are in demand and future-proof."""
    elements.append(Paragraph(feature2_text, styles['content']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Feature 3
    elements.append(Paragraph("3. Portfolio Building", styles['point_title']))
    feature3_text = """The portal guides you in building a robust professional portfolio, highlighting projects, experiences, and skills that showcase your readiness for your dream roles. This feature enhances your ability to stand out in competitive job applications."""
    elements.append(Paragraph(feature3_text, styles['content']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Feature 4
    elements.append(Paragraph("4. Employer Expectations", styles['point_title']))
    feature4_text = """KerjayaKu pinpoints value-added competencies that employers look for in specific roles. You'll receive tailored suggestions to develop qualities like leadership, critical thinking, adaptability, and innovation."""
    elements.append(Paragraph(feature4_text, styles['content']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Feature 5
    elements.append(Paragraph("5. Strategic Career Direction", styles['point_title']))
    feature5_text = """Through personality and aspiration mapping, the platform ensures your career development plan aligns with both your passions and the market's needs, empowering you to pursue jobs where you'll thrive."""
    elements.append(Paragraph(feature5_text, styles['content']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Why It Matters Section
    elements.append(Paragraph("Why It Matters for Young Professionals", styles['subheading']))
    why_text = """Fresh graduates often struggle to transition from academia to the workforce due to a lack of clarity in skill requirements and strategic career planning. KerjayaKu bridges this gap by offering personalized, actionable insights to help you reskill, upskill, and showcase your abilities effectively. With its AI-driven precision, the portal provides a roadmap to build confidence, enhance employability, and unlock opportunities tailored to your goals."""
    elements.append(Paragraph(why_text, styles['content']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Conclusion
    conclusion_text = """KerjayaKu equips you not just for a job, but for a career that aligns with your aspirations and the future of work."""
    elements.append(Paragraph(conclusion_text, styles['content']))
    
    return elements
def create_contact_page(styles):
    """Create a beautifully designed contact page with fixed sizing."""
    elements = []
    
    # Add a page break before contact page
    elements.append(PageBreak())
    
    # Create a colored background header
    elements.append(
        Table(
            [[Paragraph("Get in Touch", styles['heading'])]], 
            colWidths=[7*inch],
            style=TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F0F9FF')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
                ('TOPPADDING', (0, 0), (-1, -1), 20),
                ('LEFTPADDING', (0, 0), (-1, -1), 30),
            ])
        )
    )
    elements.append(Spacer(1, 0.3*inch))

    # Profile photo
    if os.path.exists("mizah.jpg"):
        description_style = ParagraphStyle(
            'ImageDescription',
            parent=styles['content'],
            fontSize=10,
            textColor=colors.HexColor('#1a1a1a'),
            alignment=TA_LEFT,
            leading=14
        )
        
        description_text = Paragraph("""KerjayaKu: AI-Driven Career Guidance for a Strategic Future<br/>
            KerjayaKu is an AI-powered portal designed to help fresh graduates and young professionals strategically navigate their career development journey. 
            By integrating cutting-edge artificial intelligence, KerjayaKu assesses your education profile, aspirations, personality traits, current skillset, 
            and problem-solving abilities, along with social-emotional learning skills. It then delivers personalized insights to help you stay competitive 
            in today's dynamic job market.""", description_style)

        elements.append(
            Table(
                [
                    [Image("mizah.jpg", width=1*inch, height=1*inch), ""],  # Image row
                    [description_text, ""]  # Description row below image
                ],
                colWidths=[1.5*inch, 5.5*inch],
                style=TableStyle([
                    ('ALIGN', (0, 0), (0, 0), 'LEFT'),  # Align image to left
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('TOPPADDING', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                    ('LEFTPADDING', (0, 0), (-1, -1), 15),
                    ('SPAN', (0, 1), (1, 1)),  # Span description across both columns
                ])
            )
        )
        elements.append(Spacer(1, 0.3*inch))

    # Contact information table
    contact_table_data = [
        # Label Cell, Value Cell
        [Paragraph("Address:", styles['content']),
         Paragraph("Centre for AI Innovation (CEAI) @Kuala Lumpur,\nc/o MyFinB (M) Sdn Bhd,\nLevel 13A, Menara Tokio Marine,\n189 Jalan Tun Razak, Hampshire Park,\n50450 Kuala Lumpur, Malaysia", styles['content'])],
        
        [Paragraph("Tel:", styles['content']),
         Paragraph("+601117695760", styles['content'])],
        
        [Paragraph("Email:", styles['content']),
         Paragraph('<link href="mailto:hamizah@ceaiglobal.com"><font color="#2563EB">hamizah@ceaiglobal.com</font></link>', styles['content'])],
        
        [Paragraph("Website:", styles['content']),
         Paragraph('<link href="https://www.google.com/maps"><font color="#2563EB">www.ceaiglobal.com</font></link>', styles['content'])]
    ]

    # Create the contact information table
    contact_table = Table(
        contact_table_data,
        colWidths=[1.5*inch, 5.8*inch],
        style=TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FFFFFF')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2B6CB0')),  # Blue color for labels
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ])
    )
    
    elements.append(contact_table)
    
    # Footer
    elements.extend([
        Spacer(1, 0.5*inch),
        Table(
            [[Paragraph("Thank you for your interest!", 
                       ParagraphStyle(
                           'ThankYou',
                           parent=styles['subheading'],
                           alignment=TA_CENTER,
                           textColor=colors.HexColor('#2B6CB0')
                       ))]],
            colWidths=[7*inch],
            style=TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F0F9FF')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
                ('TOPPADDING', (0, 0), (-1, -1), 15),
            ])
        ),
        # Spacer(1, 0.2*inch),
        # Table(
        #     [[Paragraph("© 2024 Centre for AI Innovation. All rights reserved.", 
        #                ParagraphStyle(
        #                    'Footer',
        #                    parent=styles['content'],
        #                    alignment=TA_CENTER,
        #                    textColor=colors.HexColor('#666666'),
        #                    fontSize=8
        #                ))]],
        #     colWidths=[7*inch],
        #     style=TableStyle([
        #         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        #     ])
        # )
    ])
    
    return elements

def generate_pdf(summary,personality, analysis2, personal_info):
    """Generate PDF with enhanced formatting and highlight boxes."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=1.5*inch,
        bottomMargin=inch
    )
    
    styles = create_custom_styles()
    elements = []

    # Check for None and provide fallback
    summary=summary
    personality = personality
    analysis2 = analysis2 or "No recommendations available."
    personal_info = personal_info or {"name": "Unknown"}

    # Front Page
    elements.extend(create_front_page(styles, personal_info))
    elements.append(PageBreak())

    # Initial Assessment Section
    elements.append(Paragraph("Profile Summary", styles['heading']))
    process_content(summary, styles, elements)
    elements.append(PageBreak())
        
    elements.append(Paragraph("Personality Assessment", styles['heading']))
    process_content(personality, styles, elements)
    elements.append(PageBreak())

    elements.append(Paragraph("Comprehensive Analysis", styles['heading']))
    process_content(analysis2, styles, elements)
    elements.append(PageBreak())


    # Contact Page
    elements.extend(create_contact_page(styles))
    
    # Build PDF
    doc.build(elements, onFirstPage=create_header_footer, onLaterPages=create_header_footer)
    
    buffer.seek(0)
    return buffer

def create_dynamic_toc(elements, styles, content_sections):
    """Create dynamic table of contents with enhanced styling"""
    elements.append(Table([['']], colWidths=[7*inch], rowHeights=[2],
        style=TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.HexColor('#2B6CB0')),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
        ])
    ))
    
    elements.append(Paragraph("Table of Contents", styles['toc_title']))
    elements.append(Spacer(1, 30))
    
    current_page = 2  # Start after front page
    toc_entries = []
    
    # Executive Summary (always starts on page 3)
    toc_entries.append(("Executive Summary", 3))
    current_page = 4  # Next section starts after executive summary
    
    # Business Areas (each on new page)
    if content_sections.get('business_areas'):
        toc_entries.append(("Selected Business Areas", current_page))
        current_page += 1
        for area in content_sections['business_areas']:
            toc_entries.append((f"    {area}", current_page))
            current_page += 2  # Each area gets its own page + spacing
    
    # Generate TOC entries with dot leaders
    for title, page in toc_entries:
        if title.startswith("    "):
            # Indent sub-entries
            title = title.strip()
            elements.append(
                Paragraph(
                    f"{title} {'.' * (60 - len(title))} {page}",
                    styles['toc_entry_level2']
                )
            )
        else:
            elements.append(
                Paragraph(
                    f"{title} {'.' * (60 - len(title))} {page}",
                    styles['toc_entry']
                )
            )
        elements.append(Spacer(1, 12))
    
    elements.append(Table([['']], colWidths=[7*inch], rowHeights=[2],
        style=TableStyle([
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#2B6CB0')),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
        ])
    ))
    
    elements.append(PageBreak())
    return current_page

def create_header_footer(canvas, doc):
    """Add header and footer to each page."""
    canvas.saveState()
    if doc.page > 1:
        # Header
        if os.path.exists("finb.jpg"):
            canvas.drawImage("finb.jpg", 
                           doc.width + doc.rightMargin - 1.5*inch, 
                           doc.height + doc.topMargin - 0.75*inch,
                           width=1.3*inch,
                           height=0.5*inch)
        
        canvas.setFont('Helvetica-Bold', 10)
        canvas.drawString(doc.leftMargin, doc.height + doc.topMargin - 0.4*inch, 
                         "Career Analysis Report")
        
        # Footer
        canvas.setFont('Helvetica', 9)
        canvas.drawString(doc.leftMargin, 0.5*inch, 
                         f"Generated on {datetime.datetime.now().strftime('%B %d, %Y')}")
        canvas.drawRightString(doc.width + doc.rightMargin, 0.5*inch, 
                             f"Page {doc.page}")
    canvas.restoreState()

def initialize_session_state():
    """Initialize all required keys in session state."""
    if "work_experience" not in st.session_state:
        st.session_state["work_experience"] = {}
    if "personal_info" not in st.session_state:
        st.session_state["personal_info"] = {}
    if "career_aspirations" not in st.session_state:
        st.session_state["career_aspirations"] = {}
    if "personality_assessment" not in st.session_state:
        st.session_state["personality_assessment"] = None
    if "final_analysis" not in st.session_state:
        st.session_state["final_analysis"] = None
    if "current_step" not in st.session_state:
        st.session_state["current_step"] = 0
    if "user_image" not in st.session_state:
        st.session_state.user_image = None
    if "photo_source" not in st.session_state:
        st.session_state.photo_source = "upload"


def render_header():
    """Render application header"""
    col1, col2 = st.columns([3, 1])
    with col1:
        logo_path = "kerjayaku.jpg"
        if os.path.exists(logo_path):
            st.image(logo_path, width=150)
    with col2:
        logo_path = "finb.jpg"
        if os.path.exists(logo_path):
            st.image(logo_path, width=250)

def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Validate phone number format."""
    # Allows for international format with optional +, spaces, and hyphens
    pattern = r'^\+?[\d\s-]{8,}$'
    return bool(re.match(pattern, phone))

def render_personal_info():
    """Render enhanced personal information form"""
    st.header("Personal Information")
    
    if not hasattr(st.session_state, 'show_language_form'):
        st.session_state.show_language_form = False
    if not hasattr(st.session_state, 'temp_basic_info'):
        st.session_state.temp_basic_info = {}
    if not hasattr(st.session_state, 'user_image'):
        st.session_state.user_image = None
        
    # Initialize experience lists in session state
    for exp_type in ['internships', 'volunteer', 'achievements', 'projects']:
        if exp_type not in st.session_state:
            st.session_state[exp_type] = []
    
    if not st.session_state.show_language_form:
        with st.form("personal_info_form"):
            # Photo Upload Section
            st.subheader("📸 Profile Photo")
            photo_option = st.radio("Choose how to add your photo:", 
                                  ["Upload a photo", "Take a photo"], 
                                  horizontal=True)
            
            if photo_option == "Take a photo":
                st.info("Please allow camera access when prompted by your browser.")
                camera_photo = st.camera_input("Take your photo")
                if camera_photo:
                    st.session_state.user_image = camera_photo.read()
            else:
                uploaded_file = st.file_uploader("Upload your profile photo", 
                                               type=['jpg', 'jpeg', 'png'])
                if uploaded_file:
                    st.session_state.user_image = uploaded_file.read()

            # Basic Information Section
            st.subheader("👤 Basic Information")
            col1, col2 = st.columns(2)
            
            with col1:
                full_name = st.text_input("Full Name*", help="Enter your legal full name")
                email = st.text_input("Email Address*", help="Enter a valid email address")
                linkedin_url = st.text_input("LinkedIn Profile URL (Optional)", 
                                           help="e.g., https://www.linkedin.com/in/username")
            
            with col2:
                phone = st.text_input("Phone Number*", help="Include country code (e.g., +60123456789)")
                country = st.selectbox("Country of Residence*", COUNTRIES)

            # Experience Section
            st.subheader("💼 Experience")
            
            # Internships Form
            st.write("Internships, Part-time, or Freelance Work")
            internship_desc = st.text_input("Description", key="new_internship_desc")
            col_int1, col_int2 = st.columns(2)
            with col_int1:
                internship_start = st.date_input("Start Date", key="new_internship_start")
            with col_int2:
                internship_end = st.date_input("End Date", key="new_internship_end")
            
            add_internship = st.form_submit_button("Add Internship")
            if add_internship and internship_desc:
                st.session_state.internships.append({
                    "description": internship_desc,
                    "start_date": internship_start.strftime("%B %Y"),
                    "end_date": internship_end.strftime("%B %Y")
                })
                st.rerun()

            # Display internships
            for idx, internship in enumerate(st.session_state.internships):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.text(internship["description"])
                with col2:
                    st.text(f"{internship['start_date']} - {internship['end_date']}")
                remove_internship = st.form_submit_button(f"Remove Internship {idx + 1}")
                if remove_internship:
                    st.session_state.internships.pop(idx)
                    st.rerun()
                st.markdown("---")

            # Volunteer activities
            st.write("Volunteer or Extracurricular Activities")
            volunteer_desc = st.text_input("Description", key="new_volunteer_desc")
            col_vol1, col_vol2 = st.columns(2)
            with col_vol1:
                volunteer_start = st.date_input("Start Date", key="new_volunteer_start")
            with col_vol2:
                volunteer_end = st.date_input("End Date", key="new_volunteer_end")
            
            add_volunteer = st.form_submit_button("Add Volunteer Activity")
            if add_volunteer and volunteer_desc:
                st.session_state.volunteer.append({
                    "description": volunteer_desc,
                    "start_date": volunteer_start.strftime("%B %Y"),
                    "end_date": volunteer_end.strftime("%B %Y")
                })
                st.rerun()

            # Display volunteer activities
            for idx, volunteer in enumerate(st.session_state.volunteer):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.text(volunteer["description"])
                with col2:
                    st.text(f"{volunteer['start_date']} - {volunteer['end_date']}")
                remove_volunteer = st.form_submit_button(f"Remove Volunteer Activity {idx + 1}")
                if remove_volunteer:
                    st.session_state.volunteer.pop(idx)
                    st.rerun()
                st.markdown("---")

            # Professional Achievements/Rewards Section
            st.write("Professional Achievements and Rewards")
            achievement_desc = st.text_input("Description", key="new_achievement_desc")
            col_ach1, col_ach2 = st.columns(2)
            with col_ach1:
                achievement_start = st.date_input("Start Date", key="new_achievement_start")
            with col_ach2:
                achievement_end = st.date_input("End Date", key="new_achievement_end")

            add_achievement = st.form_submit_button("Add Achievement")
            if add_achievement and achievement_desc:
                st.session_state.achievements.append({
                    "description": achievement_desc,
                    "start_date": achievement_start.strftime("%B %Y"),
                    "end_date": achievement_end.strftime("%B %Y")
                })
                st.rerun()

            # Display achievements
            for idx, achievement in enumerate(st.session_state.achievements):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.text(achievement["description"])
                with col2:
                    st.text(f"{achievement['start_date']} - {achievement['end_date']}")
                remove_achievement = st.form_submit_button(f"Remove Achievement {idx + 1}")
                if remove_achievement:
                    st.session_state.achievements.pop(idx)
                    st.rerun()
                st.markdown("---")

            # Key Projects Section
            st.write("Key Projects and Roles")
            project_desc = st.text_input("Description", key="new_project_desc")
            col_proj1, col_proj2 = st.columns(2)
            with col_proj1:
                project_start = st.date_input("Start Date", key="new_project_start")
            with col_proj2:
                project_end = st.date_input("End Date", key="new_project_end")

            add_project = st.form_submit_button("Add Project")
            if add_project and project_desc:
                st.session_state.projects.append({
                    "description": project_desc,
                    "start_date": project_start.strftime("%B %Y"),
                    "end_date": project_end.strftime("%B %Y")
                })
                st.rerun()

            # Display projects
            for idx, project in enumerate(st.session_state.projects):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.text(project["description"])
                with col2:
                    st.text(f"{project['start_date']} - {project['end_date']}")
                remove_project = st.form_submit_button(f"Remove Project {idx + 1}")
                if remove_project:
                    st.session_state.projects.pop(idx)
                    st.rerun()
                st.markdown("---")
            # Language Selection Section
            st.subheader("🌐 Language Selection")
            languages = st.multiselect("Select Languages*", LANGUAGES,
                                     help="Select all languages you can communicate in")

            # Continue to Language Proficiency button
            submitted = st.form_submit_button("Continue to Language Proficiency")
            
            if submitted:
                if not languages:
                    st.error("Please select at least one language")
                    return None
                    
                # Store the data and move to language form
                experience_data = {
                    "internships": st.session_state.internships,
                    "volunteer": st.session_state.volunteer
                }
                
                personal_info = {
                    "name": full_name,
                    "email": email,
                    "phone": phone,
                    "linkedin_url": linkedin_url if linkedin_url else "Not provided",
                    "country": country,
                    "experience": experience_data,
                    "selected_languages": languages
                }
                
                st.session_state.temp_basic_info = personal_info
                st.session_state.show_language_form = True
                st.rerun()

    else:
        # Language proficiency form
        with st.form("language_form"):
            st.write("### Basic Information")
            st.write(f"Name: {st.session_state.temp_basic_info['name']}")
            st.write(f"Email: {st.session_state.temp_basic_info['email']}")
            
            if st.session_state.user_image:
                st.image(st.session_state.user_image, caption="Profile Photo", width=200)
            
            # Language Proficiency Section
            st.subheader("🌐 Set Language Proficiencies")
            language_proficiencies = {}
            
            for lang in st.session_state.temp_basic_info["selected_languages"]:
                proficiency = st.select_slider(
                    f"Proficiency in {lang}",
                    options=["Beginner", "Intermediate", "Advanced", "Native/Fluent"]
                )
                language_proficiencies[lang] = proficiency
            
            # Back and Submit buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Back"):
                    st.session_state.show_language_form = False
                    st.rerun()
            with col2:
                if st.form_submit_button("Submit"):
                    complete_data = st.session_state.temp_basic_info.copy()
                    complete_data["languages"] = language_proficiencies
                    return complete_data
    
    return None
def validate_form_data(
    full_name, email, phone, gender, languages, consent, current_status, status_details
):
    """
    Validate the personal information form data.
    """
    # Validate required fields
    if not full_name:
        st.error("Full name is required.")
        return False
    if not email or not validate_email(email):
        st.error("A valid email address is required.")
        return False
    if not phone or not validate_phone(phone):
        st.error("A valid phone number is required.")
        return False
    if gender == "Select Gender":
        st.error("Please select a gender.")
        return False
    if not languages:
        st.error("Please select at least one language.")
        return False
    if not consent:
        st.error("You must agree to the consent checkbox to proceed.")
        return False

    # Validate current status details
    if current_status == "Working":
        if not status_details.get("job_title"):
            st.error("Please provide your job title.")
            return False
        if not status_details.get("employment_type"):
            st.error("Please specify your employment type.")
            return False
    elif current_status == "Studying":
        if not status_details.get("field_of_study"):
            st.error("Please provide your field of study.")
            return False
        if not status_details.get("institution_name"):
            st.error("Please provide your institution name.")
            return False

    return True

def render_personality_assessment():
    """Render personality assessment questions and process with GPT"""
    st.header("Personality Assessment")
    
    with st.form("personality_assessment_form"):
        # Define all questions and options in a structured format
        assessment_sections = {
            "Self-Reflection and Behavior": {
                "q1": {
                    "question": "How do you typically handle unexpected challenges?",
                    "options": [
                        "I adapt quickly and focus on finding solutions",
                        "I analyze the situation thoroughly before acting",
                        "I rely on others for support or advice",
                        "I feel overwhelmed but try to push through"
                    ]
                },
                "q2": {
                    "question": "When working in a team, how do you contribute?",
                    "options": [
                        "I take charge and lead the group",
                        "I provide insights and ideas from the background",
                        "I ensure everyone stays on track and organized",
                        "I prefer to follow instructions and support the team"
                    ]
                },
                "q3": {
                    "question": "How do you react to constructive criticism?",
                    "options": [
                        "I welcome it and use it to improve",
                        "I analyze the feedback to see if it aligns with my views",
                        "I feel uncomfortable but try to work on it",
                        "I tend to take it personally and avoid similar situations"
                    ]
                },
                "q4": {
                    "question": "What motivates you the most at work?",
                    "options": [
                        "Achieving goals and recognition",
                        "Learning and developing new skills",
                        "Collaborating with others",
                        "Stability and security"
                    ]
                },
                "q5": {
                    "question": "How do you approach decision-making?",
                    "options": [
                        "I make quick decisions and trust my instincts",
                        "I gather all available information before deciding",
                        "I consult others and value their opinions",
                        "I avoid making decisions if possible"
                    ]
                }
            }
        }

        # Collect responses
        responses = {}
        
        # Display questions by section
        for section_name, questions in assessment_sections.items():
            st.subheader(section_name)
            for q_id, q_data in questions.items():
                response = st.radio(
                    q_data["question"],
                    q_data["options"],
                    key=q_id
                )
                responses[q_id] = {
                    "question": q_data["question"],
                    "answer": response
                }

        submitted = st.form_submit_button("Submit Assessment")
        if submitted:
            # Format the response for GPT
            formatted_responses = {
                "sections": {
                    section_name: {
                        q_id: {
                            "question": q_info["question"],
                            "answer": responses[q_id]["answer"]
                        }
                        for q_id, q_info in questions.items()
                    }
                    for section_name, questions in assessment_sections.items()
                }
            }

            # Add personal_info to the call
            with st.spinner("Analyzing your personality profile..."):
                analysis = analyze_personality_with_gpt(
                    formatted_responses,
                    st.session_state.personal_info,  # Pass personal_info from session state
                    st.session_state.openai_api_key
                )
                if analysis:
                    return {
                        'responses': formatted_responses,
                        'analysis': analysis
                    }
    
    return None

def analyze_personality_with_gpt(responses, personal_info, api_key):
    """
    Analyze personality assessment responses with GPT, incorporating personal profile
    """
    client = OpenAI(api_key=api_key)

    # Ensure all expected sections exist, even if empty
    sections = {
        "Self-Reflection and Behavior": responses['sections'].get("Self-Reflection and Behavior", {}),
        "Social Interaction and Communication": responses['sections'].get("Social Interaction and Communication", {}),
        "Work Preferences and Adaptability": responses['sections'].get("Work Preferences and Adaptability", {})
    }

    # Check for 'dob' and calculate age or provide a fallback
    dob = personal_info.get('dob', None)
    age = calculate_age(dob) if dob else "Unknown"

    prompt = f"""As a career psychologist, analyze these personality assessment responses alongside the individual's profile in 800 words and create a summary table in the end:

PERSONAL PROFILE:
- Name: {personal_info.get('name', 'N/A')}
- Age: {age} years
- Education: {personal_info.get('education', 'N/A')} in {personal_info.get('major', 'N/A')}
{format_status_details(personal_info.get('status_details', {}), personal_info.get('current_status', 'N/A'))}
- Experience Level: {personal_info.get('experience', 'N/A')}
- Languages: {format_languages(personal_info.get('languages', {}))}

PERSONALITY ASSESSMENT RESPONSES:
1. Self-Reflection and Behavior:
{json.dumps(sections["Self-Reflection and Behavior"], indent=2)}

2. Social Interaction and Communication:
{json.dumps(sections["Social Interaction and Communication"], indent=2)}

3. Work Preferences and Adaptability:
{json.dumps(sections["Work Preferences and Adaptability"], indent=2)}

Please provide a comprehensive analysis..."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error in personality analysis: {str(e)}")
        return None

def calculate_age(dob_str):
    """Calculate age from date of birth string"""
    dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d").date()
    today = datetime.date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def format_status_details(details, status):
    """Format status details based on current status"""
    if status == "Working":
        return f"  • Job Title: {details.get('job_title', 'N/A')}\n  • Employment Type: {details.get('employment_type', 'N/A')}"
    elif status == "Studying":
        return f"  • Field of Study: {details.get('field_of_study', 'N/A')}\n  • Institution: {details.get('institution_name', 'N/A')}"
    return "  • No additional details provided"

def format_languages(languages):
    """Format language proficiencies"""
    return ", ".join([f"{lang} ({level})" for lang, level in languages.items()])
def create_front_page(styles, personal_info):
    """Create the front page of the report with user photo and additional details."""
    import os
    import tempfile
    from PIL import Image as PILImage
    import io
    
    elements = []
    temp_path = None
    
    # Logo placement - reduced spacing and size
    if all(os.path.exists(logo) for logo in ["kerjayaku.jpg", "finb.jpg"]):
        elements.append(Table(
            [[Image("kerjayaku.jpg", width=1.5*inch, height=1.5*inch),
              Image("finb.jpg", width=1.2*inch, height=0.4*inch)]],
            colWidths=[2*inch, 3*inch, 2*inch],
            style=TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ])
        ))
    
    elements.extend([
        Spacer(1, 0.3*inch),  # Reduced spacing
        Paragraph("Career Analysis Report", styles['title']),
    ])

    # Add user photo if available - with smaller dimensions
    if hasattr(st.session_state, 'user_image') and st.session_state.user_image:
        try:
            # Save image to a fixed location
            temp_path = "user_profile_temp.jpg"
            
            # Convert bytes to PIL Image and save as JPEG
            image = PILImage.open(io.BytesIO(st.session_state.user_image))
            
            # Ensure image is in RGB mode
            if image.mode != 'RGB':
                image = image.convert('RGB')
                
            # Save the image
            image.save(temp_path, 'JPEG')
            
            # Create a table with photo on left and personal info on right
            photo = Image(temp_path, width=1.5*inch, height=1.5*inch)
            personal_details = Table(
                [
                    ["Name:", personal_info.get('name', 'Not provided')],
                    ["Email:", personal_info.get('email', 'Not provided')],
                    ["Phone:", personal_info.get('phone', 'Not provided')],
                    ["Country:", personal_info.get('country', 'Not provided')],
                    ["Languages:", ", ".join(f"{lang} ({level})" for lang, level in personal_info.get('languages', {}).items())],
                ],
                colWidths=[1.5*inch, 4.5*inch],
                style=TableStyle([
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
                    ('PADDING', (0, 0), (-1, -1), 6),
                ])
            )
            
            combined_table = Table(
                [[photo, personal_details]],
                colWidths=[2*inch, 5*inch],
                style=TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 12),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                    ('TOPPADDING', (0, 0), (-1, -1), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ])
            )
            
            elements.extend([
                Spacer(1, 0.3*inch),
                Paragraph(f"for {personal_info['name']}", styles['heading']),
                Spacer(1, 0.3*inch),
                combined_table
            ])
            
        except Exception as e:
            st.error(f"Error processing user image: {str(e)}")
            print(f"Error details: {str(e)}")
            
            # Fallback layout without photo
            elements.extend([
                Spacer(1, 0.3*inch),
                Paragraph(f"for {personal_info['name']}", styles['heading']),
                Spacer(1, 0.3*inch),
                create_personal_details_table(personal_info, styles)
            ])
    else:
        # Layout without photo
        elements.extend([
            Spacer(1, 0.3*inch),
            Paragraph(f"for {personal_info['name']}", styles['heading']),
            Spacer(1, 0.3*inch),
            create_personal_details_table(personal_info, styles)
        ])
    
    if temp_path:
        st.session_state['temp_image_path'] = temp_path
        
    return elements


def create_personal_details_table(personal_info, styles):
    """Helper function to create a table for personal details."""
    return Table(
        [
            ["Name:", personal_info.get('name', 'Not provided')],
            ["Email:", personal_info.get('email', 'Not provided')],
            ["Phone:", personal_info.get('phone', 'Not provided')],
            ["Country:", personal_info.get('country', 'Not provided')],
            ["Languages:", ", ".join(f"{lang} ({level})" for lang, level in personal_info.get('languages', {}).items())],
        ],
        colWidths=[1.5*inch, 4.5*inch],
        style=TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('PADDING', (0, 0), (-1, -1), 6),
        ])
    )


def render_work_experience():
    """Render the work experience form with date ranges."""
    st.header("Work Experience")
    exp_sections = {
        "internships": {
            "title": "Internships and Work Experience",
            "placeholder": "Describe your roles and responsibilities"
        },
        "projects": {
            "title": "Key Projects",
            "placeholder": "Describe significant projects you've worked on"
        },
        "achievements": {
            "title": "Achievements",
            "placeholder": "List notable achievements and awards"
        }
    }
    
    with st.form("work_experience"):
        experiences = {}
        for section_id, section_info in exp_sections.items():
            st.subheader(section_info["title"])
            description = st.text_area(
                "Description",
                key=f"desc_{section_id}",
                placeholder=section_info["placeholder"]
            )
            
            if description:
                # Date range columns
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input(
                        "Start Date",
                        key=f"start_{section_id}",
                        min_value=datetime.date(2000, 1, 1)
                    )
                with col2:
                    end_date = st.date_input(
                        "End Date",
                        key=f"end_{section_id}",
                        min_value=start_date
                    )

                # Current status checkbox
                is_current = st.checkbox("This is my current role/activity", key=f"current_{section_id}")
                
                experiences[section_id] = {
                    "title": section_info["title"],
                    "description": description,
                    "start_date": start_date.strftime("%Y-%m"),
                    "end_date": "Present" if is_current else end_date.strftime("%Y-%m"),
                    "is_current": is_current
                }
            
            st.markdown("---")
        
        if st.form_submit_button("Continue"):
            return experiences or {"general": {"title": "Experience", "description": "No specific experience provided."}}
    return None
def render_career_aspirations():
    """Render the Career Aspirations form and store data."""
    st.header("Career Aspirations")

    # Define sections and their options
    sections = {
        "career_goals": {
            "title": "Career Goals",
            "options": [
                "I want to secure my first job in a relevant field.",
                "I aim to transition into a new industry or role.",
                "I want to enhance my technical or professional skills.",
                "I aspire to take on leadership roles in my career.",
                "I plan to start my own business or pursue entrepreneurship.",
                "I aim to become a subject matter expert in my field.",
                "I want to achieve financial stability and career growth.",
                "I aspire to contribute to impactful projects or social causes."
            ]
        },
        "industries": {
            "title": "Industries or Sectors of Interest",
            "options": [
                "Technology and IT services",
                "Healthcare or biotechnology",
                "Education and training",
                "Finance and banking",
                "Manufacturing and engineering",
                "Sustainability and renewable energy",
                "Creative arts and media",
                "Government, public services, or non-profits"
            ]
        },
        "roles": {
            "title": "Preferred Roles or Job Titles",
            "options": [
                "Software developer or data scientist",
                "Project manager or team lead",
                "Marketing, sales, or branding",
                "Business analyst or consultant",
                "Graphic designer or content creator",
                "Human resources or talent management",
                "Research, academia, or innovation"
            ]
        },
        "locations": {
            "title": "Desired Work Location",
            "options": [
                "I prefer working in my hometown or current city.",
                "I am open to relocating nationally for the right opportunity.",
                "I am eager to explore international opportunities.",
                "I prefer remote or hybrid work arrangements.",
                "I want to work in a specific country or region (e.g., USA, Europe)."
            ]
        },
        "interest": {
            "title": "Best Describe(s) Your Desired Roles",
            "options": [
                "I want to pursue entrepreneurship and build my own business.",
                "I prefer freelancing to maintain flexibility and independence.",
                "I am interested in corporate roles to gain structured experience.",
                "I want to combine freelance and corporate roles for variety.",
                "I am open to all paths and will decide based on opportunities."
            ]
        },
        "target": {
            "title": "Best Describe(s) Your Preferred Employers",
            "options": [
                "I aspire to work for globally renowned companies (e.g., Google, Microsoft).",
                "I want to join startups with innovative cultures.",
                "I aim to work for established companies in my region.",
                "I want to work with companies known for social impact and sustainability.",
                "I aspire to join industry leaders in my field of interest.",
                "I am open to exploring companies aligned with my values and skills."
            ]
        }
    }

    temp_aspirations = {}
    with st.form("career_aspirations_form"):
        # Render form sections
        for key, section in sections.items():
            st.subheader(section["title"])
            selected = st.multiselect(
                section["title"],
                section["options"],
                key=f"{key}_multiselect"
            )
            other = st.text_input(f"Other {section['title'].lower()} (optional)", key=f"other_{key}")
            temp_aspirations[key] = selected + ([other] if other else [])

        # Handle form submission
        if st.form_submit_button("Submit"):
            if not any(temp_aspirations.values()):
                st.error("Please fill in at least one section.")
                return None

            # Update session state only after submission
            if "career_aspirations" not in st.session_state:
                st.session_state["career_aspirations"] = {}

            st.session_state["career_aspirations"].update(temp_aspirations)
            st.success("Career aspirations saved successfully!")
            return temp_aspirations

    return None


def get_ai_analysis2(user_data, api_key):
    client = OpenAI(api_key=api_key)

    # Extract user details for more personalized examples
    name = user_data["personal_info"].get("name", "the user")
    age = user_data["personal_info"].get("age", "unknown age")
    education = user_data["personal_info"].get("education", "no education data")
    work_experience = user_data.get("work_experience", {})
    career_aspirations = user_data.get("career_aspirations", {})
    personality_assessment = user_data.get("personality_assessment", {})
    preferred_roles = career_aspirations.get("roles", [])
    target_industries = career_aspirations.get("industries", [])
    preferred_locations = career_aspirations.get("locations", [])
    current_skills = user_data["personal_info"].get("skills", "not specified")
    language_proficiency = user_data["personal_info"].get("languages", {})

    # Build a specific and detailed prompt
    prompt = f"""
    You are a career advisor tasked with providing personalized career guidance for {name}. Here is the detailed profile:

    ### Personal Profile:
    - Name: {name}
    - Age: {age}
    - Education: {education}
    - Current Skills: {current_skills}
    - Language Proficiency: {', '.join([f"{lang} ({level})" for lang, level in language_proficiency.items()])}

    ### Work Experience:
    {json.dumps(work_experience, indent=2)}

    ### Career Aspirations:
    - Preferred Roles: {', '.join(preferred_roles) if preferred_roles else 'Not specified'}
    - Target Industries: {', '.join(target_industries) if target_industries else 'Not specified'}
    - Preferred Locations: {', '.join(preferred_locations) if preferred_locations else 'Not specified'}

    ### Personality Assessment:
    {json.dumps(personality_assessment, indent=2)}

    ### Analysis Instructions:
    1. **Comprehensive Profile Analysis**:
        - Analyze {name}'s background, work experience, personality, and aspirations.
        - Highlight specific strengths, advantages, and current gaps.
        - Use real-world examples to showcase how these traits can align with their aspirations.

    2. **Skill and Competency Recommendations**:
        - Identify exactly 5 critical skills or competencies that {name} needs to succeed in their preferred roles ({', '.join(preferred_roles)}).
        - Explain how these skills can bridge any current gaps based on their work experience and aspirations.
        - Provide long, detailed real-world examples or use cases for each skill.

    3. **Personality and Attributes Recommendations**:
        - Highlight exactly 5 personality traits or attributes {name} needs to develop or enhance for success in the target industries ({', '.join(target_industries)}).
        - Include detailed examples of situations where these traits are critical and explain potential gaps {name} might face.
        - Use a conversational and engaging tone, tailored to inspire action.

    Provide actionable recommendations in each section and ensure the guidance aligns with {name}'s unique goals and background in 1650 words and must be put in a paragph and create a summary table.
    """

    # API call to OpenAI
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error getting AI analysis: {str(e)}")
        return None
    

    
def get_ai_analysis1(user_data, api_key):
    client = OpenAI(api_key=api_key)
    
    prompt = f"""As a career advisor,  provide initial assessment and predict likely personality:

Profile:
{json.dumps(user_data, indent=2)}

Provide structured analysis covering:
1. Summarize key characteristics in 500 words
2. Identify key strengths and advantages. Do it in 5 points(numbering) with example
3. make a summary table for his characteristicss"""

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error getting AI analysis: {str(e)}")
        return None
def get_ai_analysis(user_data, api_key, is_initial=True):
    """Get AI-generated analysis using OpenAI API."""
    client = OpenAI(api_key=api_key)
    
    prompt = f"""{'Initial assessment' if is_initial else 'Career recommendations'} for:
    {json.dumps(user_data, indent=2)}
    
    Provide a detailed {'assessment' if is_initial else 'set of recommendations'} in 1500 words."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error getting AI analysis: {str(e)}")
        return None
def main():
    """Main application function with enhanced current status handling"""
    st.set_page_config(page_title="KerjayaKu", page_icon="📊", layout="wide")
    
    initialize_session_state()
    render_header()

    # API Key handling
    if 'openai_api_key' not in st.session_state:
        st.session_state.openai_api_key = ''
    
    with st.sidebar:
        st.title("Settings")
        api_key_input = st.text_input("Secret Key", type="password", value=st.session_state.openai_api_key)
        if api_key_input:
            st.session_state.openai_api_key = api_key_input
        if not st.session_state.openai_api_key:
            st.warning("Please enter your Secret key to continue.")
            return

    st.title("KerjayaKu - AI-Powered Career Development Portal")

    # Step 1: Personal Information with Enhanced Current Status
    with st.container():
        st.write("## Step 1: Personal Information")
        if st.session_state.current_step == 0:
            col1, col2 = st.columns(2)
            with col1:
                personal_info = render_personal_info()
                if personal_info:
                    # Validate current status details
                    if personal_info.get('current_status') == "Working":
                        if not personal_info.get('status_details', {}).get('job_title'):
                            st.error("Please enter your job title")
                            return
                    elif personal_info.get('current_status') == "Studying":
                        if not (personal_info.get('status_details', {}).get('field_of_study') 
                               and personal_info.get('status_details', {}).get('institution_name')):
                            st.error("Please complete all study details")
                            return
                    
                    st.session_state["personal_info"] = personal_info
                    
                    # Generate GPT-enhanced personal info summary
                    with st.spinner("Processing personal information summary..."):
                        summary = generate_personal_info_summary_with_gpt(personal_info, st.session_state.openai_api_key)
                        st.session_state["personal_info_summary"] = summary
                    
                    st.session_state.current_step = 1
                    st.success("Personal information submitted successfully!")
                    st.rerun()
            
            with col2:
                st.info("""
                📌 Note:
                - All fields marked with * are required
                - Please provide accurate information for better analysis
                - Make sure to complete all relevant fields based on your current status
                """)
        
        elif "personal_info" in st.session_state:
            st.success("✓ Personal Information Completed")
            with st.expander("Review Personal Information"):
                display_personal_info(st.session_state["personal_info"])
                st.markdown(st.session_state["personal_info_summary"])

    # Step 2: Personality Assessment
    if st.session_state.current_step >= 1:
        with st.container():
            st.write("## Step 2: Personality Assessment")
            if st.session_state.current_step == 1:
                personality_data = render_personality_assessment()
                if personality_data:
                    st.session_state["personality_assessment"] = personality_data
                    st.session_state.current_step = 2
                    st.success("Personality assessment completed!")
                    st.rerun()
            elif "personality_assessment" in st.session_state:
                st.success("✓ Personality Assessment Completed")
                with st.expander("View Personality Analysis"):
                    st.markdown(st.session_state["personality_assessment"]["analysis"])


    # Step 3: Career Aspirations
    if st.session_state.current_step >= 2:
        with st.container():
            st.write("## Step 3: Career Aspirations")
            if st.session_state.current_step == 2:
                career_aspirations = render_career_aspirations()
                if career_aspirations:
                    st.session_state["career_aspirations"] = career_aspirations
                    
                    # Combine all data for analysis
                    analysis_data = {
                        "personal_info": st.session_state["personal_info"],
                        "personality_assessment": st.session_state["personality_assessment"],
                        "career_aspirations": career_aspirations
                    }
                    
                    with st.spinner("Generating comprehensive career analysis..."):
                        final_analysis = get_ai_analysis2(analysis_data, st.session_state.openai_api_key)
                        st.session_state["final_analysis"] = final_analysis
                        st.session_state.current_step = 3
                        st.success("Career analysis completed!")
                        st.rerun()
            
            elif "career_aspirations" in st.session_state:
                st.success("✓ Career Aspirations Completed")
                with st.expander("View Career Analysis"):
                    st.markdown(st.session_state["final_analysis"])

    # Final Report Generation
    if st.session_state.current_step == 3:
        st.write("## Final Report")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write("### Review Your Information")
            tabs = st.tabs(["Personal Info", "Personality", "Aspirations"])
            
            with tabs[0]:
                st.write(st.session_state["personal_info_summary"])  # Display GPT-enhanced summary
            with tabs[1]:
                st.markdown(st.session_state["personality_assessment"]["analysis"])
            with tabs[2]:
                st.markdown(st.session_state["final_analysis"])

        with col2:
            st.write("### Generate Report")
            if st.button("📄 Generate Complete Report", type="primary"):
                try:
                    with st.spinner("Generating your career analysis report..."):
                        pdf_buffer = generate_pdf(
                            st.session_state["personal_info_summary"],
                            st.session_state["personality_assessment"]["analysis"],
                            st.session_state["final_analysis"],
                            st.session_state["personal_info"]
                        )
                        
                        st.success("Report generated successfully!")
                        st.download_button(
                            "📥 Download Career Analysis Report",
                            data=pdf_buffer,
                            file_name=f"career_analysis_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                            mime="application/pdf"
                        )
                except Exception as e:
                    st.error(f"Error generating report: {str(e)}")
                    st.info("Please try again or contact support if the issue persists.")

def generate_personal_info_summary_with_gpt(personal_info, api_key):
    """
    Generate a professional summary of personal information using GPT.
    """
    client = OpenAI(api_key=api_key)
    
    # Prepare the prompt
    prompt = f"""
    You are a career advisor tasked with summarizing the personal information of an individual for a career analysis report. Here's the profile:
    
    ### Personal Information:
    - Name: {personal_info.get('name', 'N/A')}
    - Email: {personal_info.get('email', 'N/A')}
    - Phone: {personal_info.get('phone', 'N/A')}
    - Country of Residence: {personal_info.get('country', 'N/A')}
    
    {"- Job Title: " + personal_info.get('status_details', {}).get('job_title', 'N/A') if personal_info.get('current_status') == "Working" else ""}
    {"- Employment Type: " + personal_info.get('status_details', {}).get('employment_type', 'N/A') if personal_info.get('current_status') == "Working" else ""}
    {"- Field of Study: " + personal_info.get('status_details', {}).get('field_of_study', 'N/A') if personal_info.get('current_status') == "Studying" else ""}
    {"- Institution: " + personal_info.get('status_details', {}).get('institution_name', 'N/A') if personal_info.get('current_status') == "Studying" else ""}
    
    ### Language Proficiency:
    {', '.join([f"{lang} ({level})" for lang, level in personal_info.get('languages', {}).items()])}
    
    Please create a professional and concise summary of this information in 800 words.
    """
    
    try:
        # Call GPT API
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        # Return GPT's response
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Error generating summary: {str(e)}"

def display_personal_info(info):
    """Helper function to display personal information"""
    st.write(f"**Name:** {info.get('name')}")
    st.write(f"**Email:** {info.get('email')}")
    # st.write(f"**Current Status:** {info.get('current_status')}")
    
    # Display status-specific details
    status_details = info.get('status_details', {})
    if info.get('current_status') == "Working":
        st.write(f"**Job Title:** {status_details.get('job_title')}")
        st.write(f"**Employment Type:** {status_details.get('employment_type')}")
    elif info.get('current_status') == "Studying":
        st.write(f"**Field of Study:** {status_details.get('field_of_study')}")
        st.write(f"**Institution:** {status_details.get('institution_name')}")

def display_work_experience(experience):
    """Helper function to display work experience"""
    for exp_type, details in experience.items():
        st.subheader(details.get('title', ''))
        st.write(f"**Period:** {details.get('start_date')} - {details.get('end_date')}")
        st.write(details.get('description', ''))
        st.markdown("---")

if __name__ == "__main__":
    main()
