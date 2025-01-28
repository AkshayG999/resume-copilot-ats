
# Cover Letter Generator

An AI-powered tool that generates customized cover letters based on your resume and job details. Built with Python and Streamlit, it uses OpenAI's GPT-3.5 to create professional, tailored cover letters.

## Features

- PDF resume parsing
- Job posting URL analysis
- Multiple cover letter styles (Brief, Standard, Detailed)
- PDF output with professional formatting
- Automatic contact information formatting
- Custom hiring manager addressing

## Setup

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Create a `.env` file in the project root with your OpenAI API key:
```bash
OPENAI_API_KEY=your_api_key_here
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run cover_letter_generator.py
```

2. Upload your resume (PDF format) or use the default template
3. Enter the company name and position
4. (Optional) Add the job posting URL and hiring manager's name
5. Select your preferred letter style
6. Click "Generate Cover Letter"
7. Review and download the PDF

## Dependencies

- Python 3.8+
- Streamlit
- OpenAI
- PyPDF2
- FPDF2
- python-dotenv
- beautifulsoup4
- requests

## License

MIT License