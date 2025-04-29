import streamlit as st
import pandas as pd
from datetime import datetime
import base64
from fpdf import FPDF
import tempfile
import os
from ai_model import get_sections_and_analysis, generate_fir_structure

# Load the dataset
df = pd.read_csv('fir_sections.csv')

def create_pdf(fir_content, sections, analysis):
    """Create a PDF document with FIR content, relevant sections, and analysis"""
    pdf = FPDF()
    
    # Configure PDF
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "FIRST INFORMATION REPORT (FIR)", ln=True, align="C")
    pdf.line(10, 22, 200, 22)
    pdf.ln(5)
    
    # FIR Content - process text to handle special characters
    pdf.set_font("Arial", "", 12)
    
    # Process and clean the text to avoid encoding issues
    clean_content = fir_content.replace('"', '"').replace('"', '"').replace("'", "'").replace("'", "'")
    
    # Split the content by lines and add to PDF
    lines = clean_content.split('\n')
    for line in lines:
        if line.strip():
            if ":" in line:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    pdf.set_font("Arial", "B", 12)
                    pdf.cell(60, 10, parts[0].strip() + ":", 0, 0)
                    pdf.set_font("Arial", "", 12)
                    pdf.multi_cell(0, 10, parts[1].strip())
                else:
                    pdf.multi_cell(0, 10, line)
            else:
                if line.strip().isupper():
                    pdf.set_font("Arial", "B", 14)
                    pdf.ln(5)
                    pdf.cell(0, 10, line.strip(), ln=True)
                    pdf.ln(2)
                else:
                    pdf.set_font("Arial", "", 12)
                    pdf.multi_cell(0, 10, line)
    
    # Relevant Sections - with sanitized text
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "RELEVANT SECTIONS", ln=True)
    pdf.line(10, 22, 200, 22)
    pdf.ln(5)
    
    pdf.set_font("Arial", "", 12)
    for section, description in sections.items():
        # Clean text to avoid encoding issues
        clean_section = str(section).encode('latin-1', 'replace').decode('latin-1')
        clean_desc = str(description).encode('latin-1', 'replace').decode('latin-1')
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Section: {clean_section}", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 10, clean_desc)
        pdf.ln(5)
    
    # Case Analysis - with sanitized text
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "CASE ANALYSIS", ln=True)
    pdf.line(10, 22, 200, 22)
    pdf.ln(5)
    
    # Clean analysis text to avoid encoding issues
    clean_analysis = str(analysis).encode('latin-1', 'replace').decode('latin-1')
    
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, clean_analysis)
    
    return pdf

def get_download_link(pdf, filename="FIR_Report.pdf"):
    """Generate a download link for the PDF file"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            pdf.output(tmp.name)
            with open(tmp.name, "rb") as f:
                pdf_data = f.read()
        
        b64_pdf = base64.b64encode(pdf_data).decode('utf-8')
        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{filename}" class="download-button">Download FIR as PDF</a>'
        return href
    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")
        return ""

def get_css():
    """Return the CSS for styling the app"""
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
    
    .stApp {
        background-color: #f0f4f8;
    }
    
    .main-container {
        background-image:url("https://img.freepik.com/free-photo/still-life-with-scales-justice_23-2149776012.jpg");
        background-color: rgba(255, 255, 255, 0.97);
        border-radius: 15px;
        padding: 30px;
        margin: 20px auto;
        max-width: 1200px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
    }
    
    .header {
        text-align: center;
        margin-bottom: 25px;
        color: #000000;
        border-bottom: 3px solid #000000;
        padding-bottom: 15px;
    }
    
    .header h1 {
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        font-size: 2.2rem;
        margin-bottom: 0;
        color: #000000;
    }
    
    .stButton>button {
        background-color: #1e3a8a;
        color: white !important;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.7rem 1.5rem;
        border: none;
        transition: all 0.3s ease;
        width: 100%;
        font-size: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .stTextInput>div>div>input, 
    .stTextArea>div>div>textarea, 
    .stDateInput>div>div>input, 
    .stTimeInput>div>div>input {
        background-color: #f9f9f9;
        border: 1px solid #ccd0d5;
        border-radius: 8px;
        padding: 12px;
        font-size: 1rem;
        color: #000000 !important;
    }
    
    ::placeholder {
        color: #777777 !important;
        opacity: 0.8 !important;
        font-weight: 400;
    }
    
    .stTextInput label, 
    .stTextArea label, 
    .stDateInput label, 
    .stTimeInput label {
        color: #000000 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    
    h1, h2, h3 {
        color: #000000 !important;
        font-weight: 700;
        font-family: 'Poppins', sans-serif;
    }
    
    p, div, label, span {
        font-family: 'Poppins', sans-serif;
        color: #000000 !important;
    }
    
    .section-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 25px;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #000000;
    }
    
    .analysis-card {
        background-color: #f0f4f8;
        border-radius: 10px;
        padding: 25px;
        margin-top: 25px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #000000;
    }
    
    .download-button {
        display: inline-block;
        background-color: #1e3a8a;
        color: white !important;
        font-weight: 600;
        text-align: center;
        padding: 14px 28px;
        text-decoration: none;
        border-radius: 8px;
        margin-top: 25px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        font-size: 1.1rem;
    }
    
    .form-section {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 25px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.08);
        border: 1px solid #e2e8f0;
    }
    
    .form-section-title {
        color: #000000;
        font-size: 1.3rem;
        margin-bottom: 20px;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 10px;
        font-weight: 600;
        font-family: 'Poppins', sans-serif;
    }
    
    .streamlit-expanderHeader {
        background-color: #f0f4f8 !important;
        border-radius: 8px !important;
        padding: 10px 15px !important;
        font-weight: 600 !important;
        color: #000000 !important;
    }
    
    .stAlert {
        background-color: #fff3cd !important;
        color: #856404 !important;
        border-left: 5px solid #ffc107 !important;
        padding: 15px !important;
        border-radius: 8px !important;
        margin: 20px 0 !important;
    }
    </style>
    """

def main():
    st.set_page_config(
        page_title="FIR Assistant", 
        page_icon="🚨", 
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Apply CSS styling
    st.markdown(get_css(), unsafe_allow_html=True)
    
    # Main container
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Header
    st.markdown('<div class="header"><h1>🚨 FIR Assistant – Indian Police Report Generator</h1></div>', unsafe_allow_html=True)

    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    
    if 'fir_data' not in st.session_state:
        st.session_state.fir_data = None

    # Home Page
    if st.session_state.page == 'home':
        st.markdown("""
        <div style="text-align: center; padding: 20px; background-color: #f0f4f8; border-radius: 10px; margin-bottom: 30px;">
            <h2 style="color: #000000; margin-bottom: 15px;">Welcome to the FIR Assistant</h2>
            <p style="font-size: 1.1rem; margin-bottom: 20px; color: #000000;">This tool helps police officers and legal professionals in creating structured First Information Reports (FIRs) with relevant legal sections.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            if st.button("📝 Start New FIR"):
                st.session_state.page = 'query'
                st.experimental_rerun()

    # Query Form Page
    elif st.session_state.page == 'query':
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<div class="form-section-title">📅 Incident Details</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            date_of_incident = st.date_input("Date of Incident", datetime.now())
            place_of_occurrence = st.text_input("Place of Occurrence", placeholder="Enter exact location of crime")
        with col2:
            time_of_incident = st.time_input("Time of Incident", datetime.now().time())
            nature_of_offense = st.text_input("Nature of the Offense", placeholder="e.g., Theft, Assault, etc.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<div class="form-section-title">👤 Complainant Details</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            complainant_name = st.text_input("Complainant Name", placeholder="Full name of the person filing the complaint")
            complainant_address = st.text_area("Complainant Address", placeholder="Complete residential address", height=100)
        with col2:
            complainant_contact = st.text_input("Complainant Contact", placeholder="Mobile number or other contact information")
            complainant_id = st.text_input("ID Proof Details", placeholder="Aadhar/PAN/Voter ID number (optional)")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<div class="form-section-title">🕵️ Accused Details (if known)</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            accused_name = st.text_input("Accused Name", placeholder="Name of the suspect (if known)")
            accused_address = st.text_input("Accused Address", placeholder="Address of the suspect (if known)")
        with col2:
            accused_description = st.text_area("Accused Description", placeholder="Physical description, identifying marks, etc.", height=100)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<div class="form-section-title">📝 Case Description</div>', unsafe_allow_html=True)
        case_description = st.text_area(
            "Enter the detailed facts of the case:",
            placeholder="Provide detailed facts of the incident",
            height=200
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔍 Generate FIR"):
                if case_description:
                    with st.spinner("Generating FIR... This may take a moment."):
                        user_inputs = f"""
                        Date of Incident: {date_of_incident}
                        Time of Incident: {time_of_incident}
                        Place of Occurrence: {place_of_occurrence}
                        Nature of Offense: {nature_of_offense}
                        Complainant Name: {complainant_name}
                        Complainant Contact: {complainant_contact}
                        Complainant Address: {complainant_address}
                        Complainant ID: {complainant_id}
                        Accused Name: {accused_name}
                        Accused Address: {accused_address}
                        Accused Description: {accused_description}
                        """

                        sections, analysis = get_sections_and_analysis(case_description)
                        fir_structure = generate_fir_structure(case_description, sections, user_inputs)
                        
                        # Store the generated data
                        st.session_state.fir_data = {
                            'fir_structure': fir_structure,
                            'sections': sections,
                            'analysis': analysis
                        }
                        
                        st.session_state.page = 'result'
                        st.experimental_rerun()
                else:
                    st.warning("Please enter a case description.")
        with col2:
            if st.button("🏠 Back to Home"):
                st.session_state.page = 'home'
                st.experimental_rerun()
    
    # Results Page
    elif st.session_state.page == 'result' and st.session_state.fir_data:
        data = st.session_state.fir_data
        
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.header("📄 Generated FIR")
        st.markdown(f'<div style="line-height: 1.6; font-size: 1.05rem; color: #000000;">{data["fir_structure"].replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Create PDF and download button
        try:
            pdf = create_pdf(data['fir_structure'], data['sections'], data['analysis'])
            st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
            st.markdown(get_download_link(pdf), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Unable to generate PDF: {str(e)}")
        
        with st.expander("📚 Relevant Sections", expanded=False):
            for section, description in data['sections'].items():
                st.markdown(f'<div class="section-card"><h3 style="color: #000000;">Section: {section}</h3><p style="font-size: 1.05rem; line-height: 1.5; color: #000000;">{description}</p></div>', unsafe_allow_html=True)
        
        with st.expander("🔎 Case Analysis", expanded=False):
            st.markdown(f'<div class="analysis-card"><div style="font-size: 1.05rem; line-height: 1.6; color: #000000;">{data["analysis"]}</div></div>', unsafe_allow_html=True)
        
        st.markdown('<div style="margin-top: 30px;">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 Create New FIR"):
                st.session_state.page = 'query'
                st.experimental_rerun()
        with col2:
            if st.button("🏠 Return to Home"):
                st.session_state.page = 'home'
                st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Close main container
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()