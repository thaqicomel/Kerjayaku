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
    Create enhanced custom styles for the PDF document with improved typography
    """
    styles = getSampleStyleSheet()
    
    # Define modern color scheme
    custom_colors = {
        'primary': colors.HexColor('#1a1a1a'),      # Main text
        'secondary': colors.HexColor('#4A5568'),    # Secondary text
        'accent': colors.HexColor('#2B6CB0'),       # Titles and headings
        'background': colors.HexColor('#F7FAFC'),   # Background elements
        'divider': colors.HexColor('#E2E8F0')       # Lines and dividers
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
        'bullet': ParagraphStyle(
            'BulletPoint',
            parent=styles['Normal'],
            fontSize=11,
            leftIndent=20,
            bulletIndent=12,
            spaceBefore=3,
            spaceAfter=3,
            fontName='Helvetica',
            leading=16
        )
    }

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


def process_section_content(content, styles, elements):
    """
    Process section content with enhanced markdown cleaning
    """
    paragraphs = []
    current_paragraph = []
    
    # Split content into lines and process
    lines = content.strip().split('\n')
    for line in lines:
        # Apply thorough cleaning to each line
        clean_line = clean_text(line)
        if not clean_line:
            continue
            
        # Check if this is a bullet point
        if clean_line.startswith('•'):
            # If we were building a paragraph, add it now
            if current_paragraph:
                paragraphs.append((' '.join(current_paragraph), False))
                current_paragraph = []
            # Add bullet point
            paragraphs.append((clean_line, True))
        else:
            # Check if this might be a section header
            if len(clean_line) < 50 and clean_line.endswith(':'):
                if current_paragraph:
                    paragraphs.append((' '.join(current_paragraph), False))
                    current_paragraph = []
                paragraphs.append((clean_line, 'header'))
            else:
                current_paragraph.append(clean_line)
    
    # Add any remaining paragraph
    if current_paragraph:
        paragraphs.append((' '.join(current_paragraph), False))
    
    # Create styled elements with cleaned text
    for text, is_bullet in paragraphs:
        if is_bullet == 'header':
            elements.extend([
                Spacer(1, 12),
                Paragraph(clean_text(text), styles['subheading']),
                Spacer(1, 6)
            ])
        elif is_bullet:
            elements.append(Paragraph(clean_text(text), styles['bullet']))
        else:
            elements.extend([
                Paragraph(clean_text(text), styles['content']),
                Spacer(1, 8)
            ])

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
def create_front_page(styles, personal_info):
    """Create the front page of the report."""
    elements = []
    
    # Logo placement
    if all(os.path.exists(logo) for logo in ["kerjayaku.jpg", "finb.jpg"]):
        elements.append(Table(
            [[Image("kerjayaku.jpg", width=2*inch, height=2*inch),
              Image("finb.jpg", width=1.5*inch, height=0.5*inch)]],
            colWidths=[2.5*inch, 3*inch, 2*inch],
            style=TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ])
        ))
    
    elements.extend([
        Spacer(1, inch),
        Paragraph("Career Analysis Report", styles['title']),
        Paragraph(f"for {personal_info['name']}", styles['heading']),
        Spacer(1, 0.5*inch),
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
        ),
        PageBreak()
    ])
    return elements

def generate_pdf(analysis1, analysis2, personal_info, work_experience):
    """Generate a PDF report with enhanced text cleaning"""
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
    
    # Front Page
    elements.extend(create_front_page(styles, personal_info))
    
    # Experience Section
    elements.append(Paragraph("Professional Experience", styles['heading']))
    for exp_type, details in work_experience.items():
        if details.get('description'):
            elements.extend([
                Paragraph(clean_text(details['title']), styles['subheading']),
                # Only add period if it exists
                *(
                    [Paragraph(f"Period: {details['period']}", styles['content'])]
                    if 'period' in details and details['period']
                    else []
                ),
                Paragraph(clean_text(details['description']), styles['content']),
                Spacer(1, 0.2*inch)
            ])
    elements.append(PageBreak())
    
    # Analysis Sections
    elements.append(Paragraph("Initial Assessment", styles['heading']))
    for para in clean_text(analysis1).split('\n\n'):
        if para.strip():
            elements.append(Paragraph(clean_text(para), styles['content']))
    elements.append(PageBreak())
    
    elements.append(Paragraph("Career Recommendations", styles['heading']))
    for para in clean_text(analysis2).split('\n\n'):
        if para.strip():
            if para.startswith(('•', '-')):
                elements.append(Paragraph(f"• {clean_text(para.lstrip('•- '))}", styles['bullet']))
            else:
                elements.append(Paragraph(clean_text(para), styles['content']))
    
    # Build PDF
    doc.build(elements, onFirstPage=create_header_footer, onLaterPages=create_header_footer)
    buffer.seek(0)
    return buffer
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

    if not st.session_state.show_language_form:
        with st.form("basic_info"):
            full_name = st.text_input("Full name", help="Required field")
            age = st.number_input("Age", min_value=13, max_value=65, value=20)
            education = st.selectbox("Highest level of education completed", EDUCATION_LEVELS, help="Required field")
            
            major_selection = st.selectbox("Field of study/major", FIELDS_OF_STUDY)
            major = st.text_input("Please specify your field of study") if major_selection == "Others" else major_selection
            
            languages = st.multiselect("Select languages", LANGUAGES)
            
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
        
        st.subheader("Set Language Proficiencies")
        language_proficiencies = {}
        
        for lang in st.session_state.temp_basic_info["selected_languages"]:
            if lang == "Others":
                custom_lang = st.text_input("Specify other language")
                if custom_lang:
                    proficiency = st.select_slider(
                        f"Proficiency in {custom_lang}",
                        options=["Beginner", "Intermediate", "Advanced", "Native/Fluent"],
                        key=f"lang_other_{custom_lang}"
                    )
                    language_proficiencies[custom_lang] = proficiency
            else:
                proficiency = st.select_slider(
                    f"Proficiency in {lang}",
                    options=["Beginner", "Intermediate", "Advanced", "Native/Fluent"],
                    key=f"lang_{lang}"
                )
                language_proficiencies[lang] = proficiency

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Back"):
                st.session_state.show_language_form = False
                st.rerun()
        with col2:
            if st.button("Next"):
                complete_data = st.session_state.temp_basic_info.copy()
                complete_data["languages"] = language_proficiencies
                return complete_data
    
    return None

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

Provide a detailed analysis of the above findings in 350 words with real examples or references and an additional analysis on:

1) based on the profile of the person given earlier, and the career aspirations given, what are the required skills and competencies that are needed for this person  to have? Explain in 350 words with examples and highlight any potential discrepancies.

2) based on the profile of the person given earlier, and the career aspirations given, what are the required personality or attributes that are needed for this person  to have? Explain in 350 words with examples and highlight any potential discrepancies. """

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
1. Summarize key characteristics in 350 words
2. Identify key strengths and advantages"""

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
    
    Provide a detailed {'assessment' if is_initial else 'set of recommendations'} in 350 words."""
    
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
                                st.session_state.user_data.get('work_experience', {})  # Remove the career_aspiration argument
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

if __name__ == "__main__":
    main()
