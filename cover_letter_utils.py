from datetime import date

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

{alignment if letter_type != "brief" else alignment.split('.')[0] + '.'}

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

