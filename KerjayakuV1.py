import streamlit as st
import datetime
from openai import OpenAI
import json
import os

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
    st.header("Work Experience")
    
    exp_sections = {
        "internships": {
            "title": "Internships, part-time, or freelance work",
            "placeholder": "Describe your role and responsibilities"
        },
        "volunteer": {
            "title": "Volunteer or extracurricular activities",
            "placeholder": "Describe your activities and roles"
        },
        "achievements": {
            "title": "Professional achievements or awards",
            "placeholder": "List your achievements and awards"
        },
        "projects": {
            "title": "Key projects completed and roles undertaken",
            "placeholder": "Describe your projects and responsibilities"
        }
    }

    with st.form("work_experience"):
        experiences = {}
        
        for section_id, section_info in exp_sections.items():
            st.subheader(section_info["title"])
            
            description = st.text_area(
                "Description",
                key=f"desc_{section_id}",
                placeholder=section_info['placeholder']
            )
            
            date_col1, date_col2 = st.columns(2)
            with date_col1:
                start_date = st.date_input(
                    "Start Date",
                    key=f"start_{section_id}",
                    min_value=datetime.date(2000, 1, 1)
                )
            with date_col2:
                end_date = st.date_input(
                    "End Date",
                    key=f"end_{section_id}",
                    min_value=start_date
                )
            
            st.markdown("---")
            
            if description:
                experiences[section_id] = {
                    "title": section_info["title"],
                    "description": description,
                    "period": f"{start_date.strftime('%m/%Y')} - {end_date.strftime('%m/%Y')}"
                }

        if st.form_submit_button("Next"):
            if not experiences:
                st.error("Please fill in at least one experience section")
                return None
            return experiences
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

def main():
    initialize_session_state()
    render_header()
    
    api_key = st.text_input("OpenAI API Key", type="password")
    if not api_key:
        st.info("Please add your OpenAI API key to continue.", icon="🗝️")
        return
    
    st.write("## KerjayaKu: AI-Driven Career Guidance for a Strategic Future")

    st.markdown(long_description)

    
    personal_info = render_personal_info()
    if personal_info:
        st.session_state.user_data['personal_info'] = personal_info
        st.session_state.show_work = True
    
    if st.session_state.show_work:
        work_exp = render_work_experience()
        if work_exp:
            st.session_state.user_data['work_experience'] = work_exp
            with st.expander("📊 Initial Analysis", expanded=True):
                analysis1 = get_ai_analysis1(st.session_state.user_data, api_key)
                if analysis1:
                    st.markdown("#### Personal Profile Overview")
                    st.markdown(analysis1)
            st.session_state.show_aspirations = True
    
    if st.session_state.show_aspirations:
        career_aspirations = render_career_aspirations()
        if career_aspirations:
            st.session_state.user_data['career_aspirations'] = career_aspirations
            st.session_state.show_analysis = True
            
            with st.expander("📊 Final Career Analysis", expanded=True):
                analysis2 = get_ai_analysis2(st.session_state.user_data, api_key)
                if analysis2:
                    st.markdown("#### Career Recommendations")
                    st.markdown(analysis2)
if __name__ == "__main__":
    main()