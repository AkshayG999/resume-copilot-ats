import requests
from bs4 import BeautifulSoup
import streamlit as st
import openai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get API key from environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

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

