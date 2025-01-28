import openai
import streamlit as st
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get API key from environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

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
- so on...

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
            'skills': skills[:4],  
            # Return all skills found, with a minimum of 1 skill
            'skills': skills if len(skills) > 0 else ["Technical skill not found"],
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

