import streamlit as st
from pdf_utils import extract_text_from_pdf, convert_to_pdf
from openai_utils import parse_resume_text, analyze_resume_ats, optimize_resume
from job_utils import extract_job_details
from cover_letter_utils import generate_cover_letter
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
                "brief": "Brief (Concise)",
                "standard": "Standard (Professional)",
                "detailed": "Detailed (Comprehensive)"
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

            # print(cover_letter)
            # Convert to PDF and add download button
            pdf_bytes = convert_to_pdf(cover_letter)
            st.download_button(
                label="Download Cover Letter as PDF",
                data=pdf_bytes,
                file_name=f"{pos.replace(' ', '_')}_{company.replace(' ', '_')}_Cover_Letter.pdf",
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

