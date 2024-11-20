import streamlit as st
import datetime
from openai import OpenAI
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
    "No formal education", "Primary school", "Secondary school / High school",
    "Diploma", "Bachelor's degree", "Master's degree", "Doctorate (PhD)",
    "Professional qualification (e.g., ACCA)"
]

FIELDS_OF_STUDY = [
    "Arts and Humanities", "Business and Management", 
    "Engineering and Technology", "Computer Science / IT",
    "Health and Medicine", "Natural Sciences", "Social Sciences",
    "Law", "Education", "Others"
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
##PDF
def create_custom_styles():
    """
    Create enhanced custom styles including all required styles
    """
    styles = getSampleStyleSheet()
    
    # Define modern color scheme
    custom_colors = {
        'primary': colors.HexColor('#1a1a1a'),      # Main text
        'secondary': colors.HexColor('#4A5568'),    # Secondary text
        'accent': colors.HexColor('#2B6CB0'),       # Titles and headings
        'background': colors.HexColor('#F7FAFC'),   # Background elements
        'divider': colors.HexColor('#E2E8F0'),      # Lines and dividers
        'bullet': colors.HexColor('#3182CE'),       # Bullet points
        'highlight_bg': colors.HexColor('#EBF8FF'), # Highlight box background
        'highlight_border': colors.HexColor('#90CDF4') # Highlight box border
    }
    
    return {
        'title': ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            textColor=custom_colors['accent'],
            spaceAfter=30,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ),
        'heading': ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=custom_colors['primary'],
            spaceBefore=20,
            spaceAfter=10,
            fontName='Helvetica-Bold',
            leading=22
        ),
        'subheading': ParagraphStyle(
            'CustomSubheading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=custom_colors['secondary'],
            spaceBefore=15,
            spaceAfter=8,
            fontName='Helvetica-Bold',
            leading=18
        ),
        'content': ParagraphStyle(
            'CustomContent',
            parent=styles['Normal'],
            fontSize=11,
            textColor=custom_colors['primary'],
            alignment=TA_JUSTIFY,
            spaceBefore=6,
            spaceAfter=6,
            fontName='Helvetica',
            leading=16,
            firstLineIndent=20
        ),
        'bullet_main': ParagraphStyle(
            'BulletMain',
            parent=styles['Normal'],
            fontSize=11,
            textColor=custom_colors['primary'],
            leftIndent=30,
            bulletIndent=15,
            spaceBefore=6,
            spaceAfter=6,
            fontName='Helvetica-Bold',
            leading=16,
            bulletColor=custom_colors['bullet']
        ),
        'bullet_sub': ParagraphStyle(
            'BulletSub',
            parent=styles['Normal'],
            fontSize=11,
            textColor=custom_colors['secondary'],
            leftIndent=45,
            bulletIndent=30,
            spaceBefore=3,
            spaceAfter=3,
            fontName='Helvetica',
            leading=14
        ),
        'bullet_subsub': ParagraphStyle(
            'BulletSubSub',
            parent=styles['Normal'],
            fontSize=11,
            textColor=custom_colors['secondary'],
            leftIndent=60,
            bulletIndent=45,
            spaceBefore=2,
            spaceAfter=2,
            fontName='Helvetica',
            leading=14
        ),
        'highlight': ParagraphStyle(
            'HighlightContent',
            parent=styles['Normal'],
            fontSize=11,
            textColor=custom_colors['primary'],
            alignment=TA_LEFT,
            spaceBefore=0,
            spaceAfter=0,
            fontName='Helvetica',
            leading=16
        ),
        'point_title': ParagraphStyle(
            'PointTitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=custom_colors['accent'],
            fontName='Helvetica-Bold',
            leading=16
        ),
        'toc_title': ParagraphStyle(
            'TOCTitle',
            parent=styles['Title'],
            fontSize=18,
            textColor=custom_colors['accent'],
            spaceAfter=20,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ),
        'toc_entry': ParagraphStyle(
            'TOCEntry',
            parent=styles['Normal'],
            fontSize=12,
            textColor=custom_colors['primary'],
            fontName='Helvetica',
            leading=16,
            spaceBefore=6,
            spaceAfter=6
        ),
        'toc_entry_level2': ParagraphStyle(
            'TOCEntryLevel2',
            parent=styles['Normal'],
            fontSize=11,
            textColor=custom_colors['secondary'],
            fontName='Helvetica',
            leading=14,
            leftIndent=20,
            spaceBefore=4,
            spaceAfter=4
        )
    }

def create_highlight_box(text, styles, include_number=None):
    """Create highlighted box for key content with optional numbering"""
    # Default background and border colors from styles
    bg_color = colors.HexColor('#EBF8FF')  # Light blue background
    border_color = colors.HexColor('#90CDF4')  # Blue border
    
    content = text
    if include_number is not None:
        content = f"Point {include_number}: {text}"
    
    return Table(
        [[Paragraph(clean_text(content), styles['highlight'])]],
        colWidths=[7*inch],
        style=TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), bg_color),
            ('BOX', (0, 0), (-1, -1), 1, border_color),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ])
    )
def process_section_content(content, styles, elements):
    """
    Process section content with enhanced bullet points and highlight boxes
    """
    paragraphs = []
    current_paragraph = []
    bullet_level = 0
    current_point_number = None
    
    # Split content into lines and process
    lines = content.strip().split('\n')
    for i, line in enumerate(lines):
        clean_line = clean_text(line)
        if not clean_line:
            continue
            
        # Check for numbered points (1., 2., etc. at start of line)
        if re.match(r'^\d+\.', clean_line):
            # If we were building a paragraph, add it now
            if current_paragraph:
                paragraphs.append((' '.join(current_paragraph), 'normal', None))
                current_paragraph = []
            
            # Extract point number and content
            point_num = int(clean_line.split('.')[0])
            point_content = clean_line[clean_line.find('.')+1:].strip()
            
            # Add as a highlighted point
            paragraphs.append((point_content, 'highlight', point_num))
            current_point_number = point_num
            
        # Check for sub-bullets under the main points
        elif clean_line.startswith(('•', '-', '*')) or re.match(r'^\s+[•\-\*]', clean_line):
            if current_paragraph:
                paragraphs.append((' '.join(current_paragraph), 'normal', None))
                current_paragraph = []
            
            # Determine indentation level
            indent_level = len(line) - len(line.lstrip())
            if indent_level > 8:
                bullet_level = 2  # Sub-sub bullet
            elif indent_level > 4:
                bullet_level = 1  # Sub bullet
            else:
                bullet_level = 0  # Main bullet
            
            # Format bullet point
            text = clean_line.lstrip('•-* ')
            bullet_text = f"• {text}"
            paragraphs.append((bullet_text, f'bullet_{bullet_level}', None))
            
        else:
            # Reset point number for non-point content
            if not line.strip().endswith(':'):  # Don't reset for section headers
                current_point_number = None
            current_paragraph.append(clean_line)
    
    # Add any remaining paragraph
    if current_paragraph:
        paragraphs.append((' '.join(current_paragraph), 'normal', None))
    
    # Create styled elements
    for text, style_type, point_num in paragraphs:
        if style_type == 'highlight':
            elements.extend([
                Spacer(1, 12),
                create_highlight_box(text, styles, point_num),
                Spacer(1, 12)
            ])
        elif style_type.startswith('bullet_'):
            level = int(style_type.split('_')[1])
            style_name = ['bullet_main', 'bullet_sub', 'bullet_subsub'][level]
            elements.append(Paragraph(clean_text(text), styles[style_name]))
        else:
            if len(text) > 50:  # Only add as content if it's a substantial paragraph
                elements.extend([
                    Paragraph(clean_text(text), styles['content']),
                    Spacer(1, 8)
                ])
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

def generate_pdf(analysis1, analysis2, personal_info, work_experience):
    """Generate PDF with enhanced formatting and highlight boxes"""
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
    
    # Front Page with user photo
    elements.extend(create_front_page(styles, personal_info))
    elements.append(PageBreak())
    
    # Experience Section with highlight boxes for each experience type
    elements.append(Paragraph("Professional Experience", styles['heading']))
    for exp_type, details in work_experience.items():
        if details.get('description'):
            elements.extend([
                Paragraph(clean_text(details['title']), styles['subheading']),
                create_highlight_box(clean_text(details['description']), styles),
                Spacer(1, 0.2*inch)
            ])
    elements.append(PageBreak())
    
    # Analysis Sections with highlight boxes for key points
    elements.append(Paragraph("Initial Assessment", styles['heading']))
    process_section_content(analysis1, styles, elements)
    elements.append(PageBreak())
    
    elements.append(Paragraph("Career Recommendations", styles['heading']))
    process_section_content(analysis2, styles, elements)

    elements.extend(create_contact_page(styles))
    
    # Build PDF
    doc.build(elements, onFirstPage=create_header_footer, onLaterPages=create_header_footer)
    
    # Cleanup temporary image file after PDF is generated
    if 'temp_image_path' in st.session_state:
        try:
            import os
            if os.path.exists(st.session_state['temp_image_path']):
                os.remove(st.session_state['temp_image_path'])
            del st.session_state['temp_image_path']
        except Exception as e:
            print(f"Error cleaning up temporary file: {str(e)}")
    
    buffer.seek(0)
    return buffer
def clean_text(text):
    """Clean text by thoroughly removing markdown formatting"""
    if not text:
        return ""
    # First pass - remove markdown headers and formatting
    text = text.replace('### ', '')  # Add space to avoid partial replacements
    text = text.replace('###', '')
    text = text.replace('## ', '')
    text = text.replace('##', '')
    text = text.replace('# ', '')
    text = text.replace('#', '')
    
    # Remove list markers and formatting
    text = text.replace('- ', '')
    text = text.replace('**', '')
    text = text.replace('*', '')
    text = text.replace('`', '')
    text = text.replace('_', ' ')
    
    # Clean up multiple periods
    text = text.replace('....', '.')
    text = text.replace('...', '.')
    text = text.replace('..', '.')
    
    # Normalize spaces
    text = ' '.join(text.split())
    return text.strip()
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
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 'personal'
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    if 'language_proficiencies' not in st.session_state:
        st.session_state.language_proficiencies = {}
    if 'show_work' not in st.session_state:
        st.session_state.show_work = False
    if 'show_aspirations' not in st.session_state:
        st.session_state.show_aspirations = False
    if 'show_analysis' not in st.session_state:
        st.session_state.show_analysis = False

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

def render_personal_info():
    st.header("Personal Information")
    
    if not hasattr(st.session_state, 'show_language_form'):
        st.session_state.show_language_form = False
    if not hasattr(st.session_state, 'temp_basic_info'):
        st.session_state.temp_basic_info = {}
    if not hasattr(st.session_state, 'user_image'):
        st.session_state.user_image = None
    if not hasattr(st.session_state, 'photo_option'):
        st.session_state.photo_option = "Upload a photo"

    if not st.session_state.show_language_form:
        # Camera input at the top level, outside any forms
        photo_option = st.radio("Choose how to add your photo:", 
                              ["Upload a photo", "Take a photo"], 
                              horizontal=True,
                              key="photo_choice")
        
        if photo_option == "Take a photo":
            st.info("Please allow camera access when prompted by your browser.")
            try:
                camera_photo = st.camera_input(
                    "Take your photo",
                    key="camera_input",
                    help="If camera doesn't open, please check your browser permissions"
                )
                if camera_photo is not None:
                    st.session_state.user_image = camera_photo.read()
                    st.success("Photo captured successfully!")
                    st.image(st.session_state.user_image, caption="Captured photo", width=200)
            except Exception as e:
                st.error(f"Error accessing camera: {str(e)}")
                st.info("Please make sure to:")
                st.markdown("""
                    1. Allow camera access in your browser
                    2. Use a supported browser (Chrome, Firefox, or Edge)
                    3. Access the app through HTTPS if running remotely
                """)
        
        # Clear photo button with unique key
        if st.session_state.user_image:
            if st.button("Clear current photo", key="clear_photo_button_1"):
                st.session_state.user_image = None
                st.info("Photo cleared. You can upload or take a new one.")
                st.rerun()

        # Personal Information Form
        with st.form("personal_info_form"):
            st.subheader("Profile Photo")
            
            # File uploader inside form
            if photo_option == "Upload a photo":
                uploaded_file = st.file_uploader("Upload your profile photo", 
                                               type=['jpg', 'jpeg', 'png'])
                if uploaded_file is not None:
                    st.session_state.user_image = uploaded_file.read()
                    st.success("Photo uploaded successfully!")
                    st.image(st.session_state.user_image, width=200)
            
            # Show current photo if available
            elif st.session_state.user_image:
                st.image(st.session_state.user_image, caption="Current photo", width=200)
            
            # Personal Details
            st.subheader("Personal Details")
            col1, col2 = st.columns(2)
            
            with col1:
                full_name = st.text_input("Full name", help="Required field")
                education = st.selectbox("Highest level of education completed", 
                                       EDUCATION_LEVELS, 
                                       help="Required field")
                major_selection = st.selectbox("Field of study/major", FIELDS_OF_STUDY)
            
            with col2:
                age = st.number_input("Age", min_value=13, max_value=65, value=20)
                if major_selection == "Others":
                    major = st.text_input("Please specify your field of study")
                else:
                    major = major_selection
            
            languages = st.multiselect("Select languages", LANGUAGES)
            
            # Submit button without key argument
            submitted_basic = st.form_submit_button("Continue to Language Proficiency")
            
            if submitted_basic:
                if not full_name or not education:
                    st.error("Please fill in all required fields")
                    return None
                if not languages:
                    st.error("Please select at least one language")
                    return None
                
                st.session_state.temp_basic_info = {
                    "name": full_name,
                    "age": age,
                    "education": education,
                    "major": major,
                    "selected_languages": languages
                }
                st.session_state.show_language_form = True
                st.rerun()
    else:
        st.write("### Basic Information")
        st.write(f"Name: {st.session_state.temp_basic_info['name']}")
        st.write(f"Education: {st.session_state.temp_basic_info['education']}")
        
        # Display current photo if available
        if st.session_state.user_image:
            st.image(st.session_state.user_image, caption="Your Profile Photo", width=200)
        
        st.subheader("Set Language Proficiencies")
        language_proficiencies = {}
        
        # Language Proficiency Form
        with st.form("language_form"):
            for lang in st.session_state.temp_basic_info["selected_languages"]:
                if lang == "Others":
                    custom_lang = st.text_input("Specify other language")
                    if custom_lang:
                        proficiency = st.select_slider(
                            f"Proficiency in {custom_lang}",
                            options=["Beginner", "Intermediate", "Advanced", "Native/Fluent"]
                        )
                        language_proficiencies[custom_lang] = proficiency
                else:
                    proficiency = st.select_slider(
                        f"Proficiency in {lang}",
                        options=["Beginner", "Intermediate", "Advanced", "Native/Fluent"]
                    )
                    language_proficiencies[lang] = proficiency

            # Form submit buttons without key arguments
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Back"):
                    st.session_state.show_language_form = False
                    st.rerun()
            with col2:
                if st.form_submit_button("Next"):
                    complete_data = st.session_state.temp_basic_info.copy()
                    complete_data["languages"] = language_proficiencies
                    return complete_data
    
    return None
def create_front_page(styles, personal_info):
    """Create the front page of the report with user photo."""
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
            
            # Create a row with photo and personal info side by side
            info_table = Table(
                [["Education:", personal_info['education']],
                 ["Field of Study:", personal_info['major']],
                 ["Languages:", ", ".join(f"{lang} ({level})" for lang, level in personal_info['languages'].items())]],
                colWidths=[1.5*inch, 3.5*inch],
                style=TableStyle([
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
                    ('PADDING', (0, 0), (-1, -1), 6),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ])
            )
            
            # Create a table with photo on left and info on right
            combined_table = Table(
                [[Image(temp_path, width=1.5*inch, height=1.5*inch), info_table]],
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
                Table(
                    [["Education:", personal_info['education']],
                     ["Field of Study:", personal_info['major']],
                     ["Languages:", ", ".join(f"{lang} ({level})" for lang, level in personal_info['languages'].items())]],
                    colWidths=[2*inch, 4*inch],
                    style=TableStyle([
                        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
                        ('PADDING', (0, 0), (-1, -1), 6)
                    ])
                )
            ])
    else:
        # Layout without photo
        elements.extend([
            Spacer(1, 0.3*inch),
            Paragraph(f"for {personal_info['name']}", styles['heading']),
            Spacer(1, 0.3*inch),
            Table(
                [["Education:", personal_info['education']],
                 ["Field of Study:", personal_info['major']],
                 ["Languages:", ", ".join(f"{lang} ({level})" for lang, level in personal_info['languages'].items())]],
                colWidths=[2*inch, 4*inch],
                style=TableStyle([
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
                    ('PADDING', (0, 0), (-1, -1), 6)
                ])
            )
        ])
    
    if temp_path:
        st.session_state['temp_image_path'] = temp_path
        
    return elements
def render_work_experience():
    """Render the work experience form."""
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
            
            # if description:  # Only show dates if description is provided
            #     col1, col2 = st.columns(2)
            #     with col1:
            #         start_date = st.date_input(
            #             "Start Date",
            #             key=f"start_{section_id}",
            #             min_value=datetime.date(2000, 1, 1)
            #         )
            #     with col2:
            #         end_date = st.date_input(
            #             "End Date",
            #             key=f"end_{section_id}",
            #             min_value=start_date
            #         )
                
            #     experiences[section_id] = {
            #         "title": section_info["title"],
            #         "description": description,
            #         "period": f"{start_date.strftime('%m/%Y')} - {end_date.strftime('%m/%Y')}"
            #     }
            
            st.markdown("---")
            if description:
                experiences[section_id] = {
                    "title": section_info["title"],
                    "description": description,
                    # "period": f"{start_date.strftime('%m/%Y')} - {end_date.strftime('%m/%Y')}"
                }           
        
        if st.form_submit_button("Continue"):
            return experiences or {"general": {"title": "Experience", "description": "No specific experience provided."}}
    return None
def render_career_aspirations():
    st.header("Career Aspirations")
    
    with st.form("career_aspirations"):
        aspirations = {}
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
                "title": "Industries or sectors of interest",
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
                "title": "Preferred roles or job titles",
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
            "locations":{
                "title": "Desired work location",
                "options": [
                    "I prefer working in my hometown or current city.",
                    "I am open to relocating nationally for the right opportunity.",
                    "I am eager to explore international opportunities.",
                    "I prefer remote or hybrid work arrangements.",
                    "I want to work in a specific country or region (e.g., USA, Europe)."
                ]
            },
            "Interest":{
                "title": "Best describe(s) your desired roles",
                "options": [
                    "I want to pursue entrepreneurship and build my own business.",
                    "I prefer freelancing to maintain flexibility and independence.",
                    "I am interested in corporate roles to gain structured experience.",
                    "I want to combine freelance and corporate roles for variety.",
                    "I am open to all paths and will decide based on opportunities."
                ]
            },
            "Target":{
                "title": "Best describe(s) your preferred employers",
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

        for key, section in sections.items():
            st.subheader(section["title"])
            selected = st.multiselect(
                section["title"],
                section["options"],
                key=key
            )
            other = st.text_input(f"Other {section['title'].lower()} (optional)", key=f"other_{key}")
            aspirations[key] = selected + ([other] if other else [])

        if st.form_submit_button("Submit"):
            if not any(aspirations.values()):
                st.error("Please fill in at least one section")
                return None
            return aspirations
    return None

def get_ai_analysis2(user_data, api_key):
    client = OpenAI(api_key=api_key)
    
    prompt = f"""As a career advisor, analyze this profile and provide specific recommendations:

Profile:
{json.dumps(user_data, indent=2)}

Provide a detailed analysis of the above findings in 1000 words with real examples or references and an additional analysis on:

1) based on the profile of the person given earlier, and the career aspirations given, what are the required skills and competencies that are needed for this person  to have? Explain in 700 words with real world examples and highlight any potential discrepancies.Do it in exactly 5 points(numbering) with long examples

2) based on the profile of the person given earlier, and the career aspirations given, what are the required personality or attributes that are needed for this person  to have? Explain in 700 words with real world examples and highlight any potential discrepancies.Do it in exactly 5 points points(numbering) with long examples """

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
2. Identify key strengths and advantages. Do it in 5 points(numbering) with example"""

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
    """Main application function."""
    st.set_page_config(page_title="Career Analysis", page_icon="📊", layout="wide")
    
    initialize_session_state()
    render_header()
    
    # Initialize analysis variables
    if 'analysis1' not in st.session_state:
        st.session_state.analysis1 = None
    if 'analysis2' not in st.session_state:
        st.session_state.analysis2 = None
    
    # API Key input in sidebar
    with st.sidebar:
        st.title("Settings")
        api_key = st.text_input("OpenAI API Key", type="password")
        
        if not api_key:
            st.warning("Please enter your OpenAI API key to continue.")
            return
    
    # Main flow
    personal_info = render_personal_info()
    if personal_info:
        st.session_state.user_data['personal_info'] = personal_info
        st.session_state.show_work = True
    
    if st.session_state.show_work:
        work_exp = render_work_experience()
        if work_exp:
            st.session_state.user_data['work_experience'] = work_exp
            with st.expander("📊 Initial Analysis", expanded=True):
                st.session_state.analysis1 = get_ai_analysis1(st.session_state.user_data, api_key)
                if st.session_state.analysis1:
                    st.markdown("#### Personal Profile Overview")
                    st.markdown(st.session_state.analysis1)
            st.session_state.show_aspirations = True
    
    if st.session_state.show_aspirations:
        career_aspirations = render_career_aspirations()
        if career_aspirations:
            st.session_state.user_data['career_aspirations'] = career_aspirations
            st.session_state.show_analysis = True
            
            with st.expander("📊 Final Career Analysis", expanded=True):
                st.session_state.analysis2 = get_ai_analysis2(st.session_state.user_data, api_key)
                if st.session_state.analysis2:
                    st.markdown("#### Career Recommendations")
                    st.markdown(st.session_state.analysis2)
                    
                    # Generate PDF only if both analyses are available
                    if st.session_state.analysis1 and st.session_state.analysis2:
                        try:
                            pdf_buffer = generate_pdf(
                                st.session_state.analysis1,
                                st.session_state.analysis2,
                                st.session_state.user_data['personal_info'],
                                st.session_state.user_data.get('work_experience', {})
                            )
                            
                            # Download button
                            st.download_button(
                                "📥 Download Career Analysis Report",
                                data=pdf_buffer,
                                file_name=f"career_analysis_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                mime="application/pdf",
                                help="Click to download your personalized career analysis report"
                            )
                        except Exception as e:
                            st.error(f"Error generating PDF: {str(e)}")
                            print(f"Detailed error: {str(e)}")  # Add detailed error logging

if __name__ == "__main__":
    main()
