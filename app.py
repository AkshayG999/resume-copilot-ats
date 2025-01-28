import streamlit as st
from io import StringIO
import PyPDF2
import openai
import requests
from bs4 import BeautifulSoup
from datetime import date
from fpdf import FPDF, XPos, YPos  # Add XPos, YPos import
import io
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get API key from environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return None

def parse_resume_text(text):
    try:
        # Use OpenAI to extract structured information from resume
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a resume parser. Extract and format the information exactly as requested."},
                {"role": "user", "content": f"""Please extract and format the following information from this resume:

Full Name:
[Extract full name]

Contact Information:
[Extract email, phone, location]

Technical Skills:
- [Skill 1]
- [Skill 2]
- [Skill 3]
- [Skill 4]
- ...

Notable Projects/Achievements (top 3):
- [Project 1]
- [Project 2]
- [Project 3]

Resume text:
{text}"""}
            ]
        )
        
        parsed_info = response.choices[0].message.content.strip()
        
        # Initialize default values
        name = "Unknown Name"
        contact = "No contact information provided"
        skills = []
        projects = []
        
        # Parse sections more robustly
        sections = parsed_info.split('\n\n')
        for section in sections:
            section = section.strip()
            if section.startswith('Full Name:'):
                name = section.replace('Full Name:', '').strip()
            elif section.startswith('Contact Information:'):
                contact = section.replace('Contact Information:', '').strip()
            elif section.startswith('Technical Skills'):
                skills = [s.strip().replace('- ', '') for s in section.split('\n')[1:] if s.strip()]
            elif section.startswith('Notable Projects'):
                projects = [p.strip().replace('- ', '') for p in section.split('\n')[1:] if p.strip()]
        
        # Ensure we have at least some default values
        if not skills:
            skills = ["Technical skill not found"]
        if not projects:
            projects = ["Project details not found"]
        
        # Create the structured output
        return {
            'name': name or "Unknown Name",
            'contact': contact or "No contact information provided",
            'skills': skills[:4],  # Keep top 4 skills
            'projects': projects[:3]  # Keep top 3 projects
        }
        
    except Exception as e:
        st.error(f"Error parsing resume: {str(e)}")
        st.write("Debug info:", parsed_info)  # Add debug information
        # Return default information instead of None
        return {
            'name': "Unknown Name",
            'contact': "No contact information provided",
            'skills': ["Technical skill not specified"],
            'projects': ["Project details not specified"]
        }

def extract_candidate_info(resume_path=None, uploaded_file=None):
    # Default candidate info as fallback
    default_info = {
        'name': "Akshay Gaikwad",
        'contact': "Pune, Maharashtra, India\n+919370638163\nakshay.ag544@gmail.com",
        'skills': [
            "Strong proficiency in Python and JavaScript",
            "Experience with distributed systems and cloud services (AWS, Azure, GCP)",
            "Proven track record of implementing efficient, scalable solutions",
            "Experience with CI/CD processes and containerization using Docker"
        ],
        'projects': [
            "AI-driven healthcare platform that improved patient care outcomes by 25%",
            "MyCarePilot app (50,000+ monthly users, 99.99% uptime)",
            "Police van tracking system reducing response times by 30%"
        ]
    }
    
    if uploaded_file is not None:
        # Extract text from uploaded PDF
        resume_text = extract_text_from_pdf(uploaded_file)
        if resume_text:
            # Parse the extracted text
            parsed_info = parse_resume_text(resume_text)
            if parsed_info:
                return parsed_info
    
    # Fallback to default resume if no upload or parsing failed
    return default_info

# Function to extract job details from a URL or manual inputs
def extract_job_details(job_url=None, manual_company=None, manual_position=None):
    # Initialize default values
    company_name = manual_company or "Unknown Company"
    position = manual_position or "Unknown Position"
    job_description = "No job description available."
    
    # Only try to fetch from URL if provided and no manual inputs
    if job_url and not (manual_company and manual_position):
        try:
            response = requests.get(job_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try to extract meta tags, with fallbacks
            if not manual_company:
                meta_company = soup.find('meta', {'property': 'og:site_name'})
                if meta_company and meta_company.get('content'):
                    company_name = meta_company['content']
            
            if not manual_position:
                meta_title = soup.find('meta', {'property': 'og:title'})
                if meta_title and meta_title.get('content'):
                    position = meta_title['content']
                
            meta_desc = soup.find('meta', {'property': 'og:description'})
            if meta_desc and meta_desc.get('content'):
                job_description = meta_desc['content']
                
        except Exception as e:
            st.error(f"Error fetching job details: {str(e)}")
    
    # Use OpenAI to analyze job description
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a professional cover letter writer. Create unique, specific content without placeholder text."},
                {"role": "user", "content": f"""Create two detailed paragraphs for a cover letter about a {position} role at {company_name}:
                1. Technical qualifications and role alignment (focus on specific skills and experience needed)
                2. Company-specific interest and culture fit (focus on company's industry impact and innovation)
                
                Context: {job_description}
                
                Important: Do not include any placeholder text like [Your Name] or [Company Address]. Write complete, specific paragraphs."""}
            ],
            max_tokens=250
        )
        
        analysis = response.choices[0].message.content.strip()
        try:
            alignment, why_company = analysis.split('\n\n', 1)
        except ValueError:
            alignment = analysis
            why_company = "The company offers exciting opportunities for growth and innovation."
            
    except Exception as e:
        st.error(f"Error generating job analysis: {str(e)}")
        alignment = "The role requires strong technical skills and problem-solving abilities."
        why_company = "The company offers exciting opportunities for growth and innovation."
    
    return company_name, position, alignment, why_company

def format_address(contact_info):
    """Format contact information into proper address blocks"""
    lines = []
    if isinstance(contact_info, str):
        info = {}
        for line in contact_info.split('\n'):
            if '@' in line:
                info['email'] = line.strip()
            elif any(char.isdigit() for char in line):
                if '@' not in line:  # Avoid adding email as phone
                    info['phone'] = line.strip()
            else:
                info['location'] = line.strip()
    else:
        info = contact_info
    
    return {
        'email': info.get('email', ''),
        'phone': info.get('phone', ''),
        'location': info.get('location', '')
    }

# Function to generate the cover letter
def generate_cover_letter(company_name, position, hiring_manager, alignment, why_company, candidate_info, letter_type="standard"):
    """Generate cover letter with specified length and style"""
    company_name = company_name.strip()
    position = position.strip()
    current_date = date.today().strftime("%B %d, %Y")
    contact_info = format_address(candidate_info['contact'])
    
    # Template configurations for different letter types
    templates = {
        "brief": {
            "skills_count": 4,
            "intro": f"I am writing to express my interest in the {position} position at {company_name}. With proven expertise in software development and a track record of delivering impactful solutions,",
            "skills_intro": "Key technical skills:",
            "closing": "I would welcome the opportunity to discuss how my skills align with your needs."
        },
        "standard": {
            "skills_count": 5,
            "intro": f"I am writing to express my strong interest in the {position} position at {company_name}. With a solid foundation in software development and a proven track record of developing scalable applications,",
            "skills_intro": "My key technical competencies include:",
            "closing": "I am eager to bring my collaborative approach and technical excellence to your team."
        },
        "detailed": {
            "skills_count": 6,
            "intro": f"I am writing to express my strong interest in the {position} position at {company_name}. As a software developer with demonstrated expertise in building scalable applications and innovative solutions,",
            "skills_intro": "My comprehensive technical skill set includes:",
            "closing": "I am eager to bring my collaborative approach, strong problem-solving abilities, and dedication to technical excellence to your engineering team."
        }
    }
    
    template = templates.get(letter_type, templates["standard"])
    
    # Format skills based on letter type
    skills = candidate_info['skills'][:template["skills_count"]]
    skills_list = '\n'.join(f"  - {skill}" for skill in skills)
    
    # Get most relevant project
    relevant_project = candidate_info['projects'][0] if candidate_info['projects'] else "various technical projects"
    
    # Generate letter content based on type
    letter_content = f"""{candidate_info['name']}
{contact_info['location']}
{contact_info['phone']}
{contact_info['email']}

{current_date}

{hiring_manager if hiring_manager else 'Hiring Manager'}
{company_name}
{position} Division

Dear {hiring_manager if hiring_manager else 'Hiring Manager'},

{template["intro"]} I am confident in my ability to contribute effectively to your innovative team.

{alignment if letter_type != "brief" else alignment.split('.')[0] + '.'}\n
{"" if letter_type == "brief" else why_company}
{template["skills_intro"]}
{skills_list}

{"" if letter_type == "brief" else f"These skills, combined with my experience in {relevant_project}, demonstrate my ability to deliver impactful solutions that drive business value. "}
{template["closing"]}

Thank you for considering my application.

Best regards,
{candidate_info['name']}

"""

    return letter_content

def convert_to_pdf(cover_letter):
    """Convert cover letter text to PDF format"""
    # Create PDF with larger margins
    pdf = FPDF(format='Letter')
    pdf.add_page()
    pdf.set_margins(left=25, top=25, right=25)
    pdf.set_auto_page_break(auto=True, margin=25)
    
    # Use Helvetica instead of Arial (core font)
    pdf.set_font("Helvetica", size=11)
    
    # Split the cover letter into lines
    lines = cover_letter.split('\n')
    
    # Add content to PDF with proper spacing
    for i, line in enumerate(lines):
        if line.strip() == '':  # Add spacing for empty lines
            pdf.ln(5)
        else:
            # Format header (name) differently
            if i == 0:  # First line (name)
                pdf.set_font("Helvetica", "B", 14)
                pdf.cell(0, 10, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_font("Helvetica", size=11)
            # Format contact info
            elif i < 4:  # Next few lines (contact info)
                pdf.cell(0, 6, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            # Format date and address block
            elif i < 9:  # Date and address block
                pdf.cell(0, 6, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            # Format main content
            else:
                # Handle bullet points (now using hyphen)
                if line.strip().startswith('-'):
                    pdf.ln(2)
                    # Add extra indentation for bullet points
                    pdf.cell(10)  # Indent
                    pdf.multi_cell(0, 6, line)
                else:
                    pdf.multi_cell(0, 6, line)
                    if not line.strip().startswith('Dear'):  # Add paragraph spacing
                        pdf.ln(2)
    
    # Get PDF as bytes
    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    return pdf_output.getvalue()

def analyze_resume_ats(resume_text, job_description):
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an ATS optimization expert. Analyze resume compatibility with job requirements."},
                {"role": "user", "content": f"""Analyze this resume against the job description and provide JSON formatted output with:
                1. ats_score: number between 0-100
                2. missing_keywords: array of important missing keywords
                3. skills_to_highlight: array of existing skills to emphasize
                4. improvement_suggestions: array of specific suggestions
                5. key_job_requirements: array of critical job requirements

                Resume:
                {resume_text}

                Job Description:
                {job_description}"""}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error analyzing resume: {str(e)}")
        return None

def optimize_resume(resume_text, job_description, ats_analysis):
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert resume writer. Optimize resumes for ATS compatibility."},
                {"role": "user", "content": f"""Optimize this resume based on the ATS analysis and job description.
                Use these specific insights to improve the resume:

                ATS Analysis:
                {ats_analysis}

                Focus on:
                1. Incorporating missing keywords naturally
                2. Emphasizing suggested skills to highlight
                3. Implementing the specific improvement suggestions
                4. Addressing key job requirements
                5. Maintaining a clear, ATS-friendly format

                Original Resume:
                {resume_text}

                Job Description:
                {job_description}"""}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error optimizing resume: {str(e)}")
        return None

# Streamlit UI
def main():
    st.title("Cover Letter & Resume Generator")
    
    tab1, tab2 = st.tabs(["Cover Letter Generator", "Resume Optimizer"])
    
    with tab1:
        st.write("Fill in the details below to generate a customized cover letter.")

        # File uploader for resume
        uploaded_file = st.file_uploader("Upload your resume (PDF)", type=['pdf'])
        
        # Extract candidate information
        if uploaded_file:
            candidate_info = extract_candidate_info(uploaded_file=uploaded_file)
            st.success("Resume uploaded and processed successfully!")
        else:
            resume_path = "/Users/apple/Desktop/Nirmitee/MyProjects/cover_letter_generator/AKSHAY GAIKWAD - Resume.pdf"
            candidate_info = extract_candidate_info(resume_path=resume_path)
            st.info("Using default resume template. Upload your resume for personalized content.")

        # Input fields in the UI
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("Company Name *", 
                                        placeholder="Enter company name")
            hiring_manager = st.text_input("Hiring Manager Name (optional)", 
                                        placeholder="Leave empty for 'Hiring Manager'")
        with col2:
            position = st.text_input("Position *", 
                                    placeholder="Enter position/role")
            job_url = st.text_input("Job URL (optional)", 
                                    placeholder="Enter the job posting URL")
        
        # Add letter type selection
        letter_type = st.selectbox(
            "Select Cover Letter Style",
            ["brief", "standard", "detailed"],
            format_func=lambda x: {
                "brief": "Brief (Concise, ~200 words)",
                "standard": "Standard (Professional, ~350 words)",
                "detailed": "Detailed (Comprehensive, ~500 words)"
            }[x]
        )

        # Generate and download the cover letter
        if st.button("Generate Cover Letter"):
            if not company_name or not position:
                st.error("Company Name and Position are required fields.")
                return
                
            company, pos, alignment, why_company = extract_job_details(
                job_url, company_name, position
            )
            cover_letter = generate_cover_letter(
                company, pos, hiring_manager, alignment, 
                why_company, candidate_info, letter_type
            )
            
            # Display the generated cover letter
            st.subheader("Generated Cover Letter")
            st.text_area("Cover Letter", cover_letter, height=400)

            # Convert to PDF and add download button
            pdf_bytes = convert_to_pdf(cover_letter)
            st.download_button(
                label="Download Cover Letter as PDF",
                data=pdf_bytes,
                file_name=f"{company.replace(' ', '_')}_Cover_Letter.pdf",
                mime="application/pdf"
            )

    with tab2:
        st.header("Resume ATS Optimizer")
        
        resume_file = st.file_uploader("Upload your current resume (PDF)", type=['pdf'], key="resume_upload")
        job_desc = st.text_area("Paste the job description", height=200)
        
        if resume_file and job_desc:
            resume_text = extract_text_from_pdf(resume_file)
            
            if resume_text:
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("1. Analyze Resume"):
                        with st.spinner("Analyzing resume..."):
                            analysis = analyze_resume_ats(resume_text, job_desc)
                            if analysis:
                                st.session_state.ats_analysis = analysis
                                st.subheader("ATS Analysis")
                                st.write(analysis)
                                st.info("👆 Review the analysis above, then click 'Optimize Resume' to improve your resume based on these insights.")
                
                with col2:
                    if st.button("2. Optimize Resume", disabled='ats_analysis' not in st.session_state):
                        with st.spinner("Optimizing resume based on ATS analysis..."):
                            optimized_resume = optimize_resume(resume_text, job_desc, st.session_state.ats_analysis)
                            if optimized_resume:
                                st.subheader("Optimized Resume")
                                st.text_area("Optimized Content", optimized_resume, height=400)
                                
                                # Convert optimized resume to PDF
                                pdf_bytes = convert_to_pdf(optimized_resume)
                                st.download_button(
                                    label="Download Optimized Resume as PDF",
                                    data=pdf_bytes,
                                    file_name="optimized_resume.pdf",
                                    mime="application/pdf"
                                )

if __name__ == "__main__":
    main()