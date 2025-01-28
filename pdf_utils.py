import PyPDF2
import streamlit as st
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem

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

def _sanitize_text(text):
    """Replace Unicode characters with their closest ASCII equivalents"""
    replacements = {
        '"': '"',
        '"': '"',
        ''': "'",
        ''': "'",
        '–': '-',
        '—': '-',
        '•': '-',
        '…': '...',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

def convert_to_pdf(cover_letter):
    """Convert cover letter text to PDF format using reportlab"""
    if not cover_letter:
        st.error("No content provided for PDF conversion")
        return None

    try:
        # Create buffer and PDF document
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        # Get styles
        styles = getSampleStyleSheet()
        
        # Create custom styles
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading1'],
            fontSize=14,
            spaceAfter=12
        )
        
        contact_style = ParagraphStyle(
            'ContactInfo',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=6
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=12
        )
        
        bullet_style = ParagraphStyle(
            'CustomBullet',
            parent=styles['Normal'],
            fontSize=11,
            leftIndent=20,
            spaceAfter=6
        )

        # Build document content
        story = []
        lines = _sanitize_text(cover_letter).split('\n')
        current_bullets = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                story.append(Spacer(1, 12))
                continue

            if i == 0:  # Name
                story.append(Paragraph(line, header_style))
            elif i < 4:  # Contact info
                if line.startswith('-'):
                    story.append(Paragraph(line[2:].strip(), contact_style))
                else:
                    story.append(Paragraph(line, contact_style))
            elif i < 9:  # Date and address
                story.append(Paragraph(line, normal_style))
            else:  # Main content
                if line.startswith('-'):
                    current_bullets.append(ListItem(Paragraph(line[1:].strip(), bullet_style)))
                else:
                    # Add any pending bullet points
                    if current_bullets:
                        story.append(ListFlowable(
                            current_bullets,
                            bulletType='bullet',
                            start='•'
                        ))
                        current_bullets = []
                        story.append(Spacer(1, 6))
                    
                    story.append(Paragraph(line, normal_style))

        # Add any remaining bullet points
        if current_bullets:
            story.append(ListFlowable(
                current_bullets,
                bulletType='bullet',
                start='•'
            ))

        # Build PDF
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes

    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")
        return None
