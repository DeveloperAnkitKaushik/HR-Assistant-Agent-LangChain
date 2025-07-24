"""
HR Assistant Agent - Streamlit Frontend
Beautiful UI for multi-agent recruitment automation with Google Sheets integration
"""

import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
from agents import HRAssistantAgents
from pdf_processor import process_uploaded_file
from google_sheets import GoogleSheetsManager
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="HR Assistant Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .agent-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
    }
    
    .success-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
    }
    
    .warning-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize session state variables"""
    if 'processing_complete' not in st.session_state:
        st.session_state.processing_complete = False
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'sheets_manager' not in st.session_state:
        st.session_state.sheets_manager = GoogleSheetsManager()

def create_score_gauge(score):
    """Create a beautiful gauge chart for candidate score"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Candidate Score"},
        delta = {'reference': 70},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 70], 'color': "yellow"},
                {'range': [70, 100], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 70
            }
        }
    ))
    fig.update_layout(height=300)
    return fig

def main():
    """Main Streamlit application"""
    init_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🤖 HR Assistant Agent</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">AI-Powered Recruitment Automation with LangChain</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # API Keys status (Hidden from users, using environment variables)
        google_api_key = os.getenv("GOOGLE_API_KEY", "")
        
        if google_api_key:
            st.success("✅ Google API Key: Configured")
        else:
            st.error("❌ Google API Key: Not configured")
        
        # Google Sheets status
        sheets_manager = st.session_state.sheets_manager
        if sheets_manager.is_connected():
            st.success("✅ Google Sheets: Connected")
            
            # Show summary if available
            summary = sheets_manager.get_candidates_summary()
            if summary:
                st.markdown("### 📊 Candidates Summary")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total", summary['total_candidates'])
                    st.metric("Approved", summary['approved'])
                with col2:
                    st.metric("Rejected", summary['rejected'])
                    st.metric("Approval Rate", f"{summary['approval_rate']}%")
        else:
            st.warning("⚠️ Google Sheets: Not connected")
        
        st.markdown("---")
        
        # Configuration Help
        st.subheader("🔑 Configuration")
        st.info("""
        **Required Environment Variables:**
        - `GOOGLE_API_KEY`: Your Google AI API key
        - `GOOGLE_SHEET_ID`: Your Google Sheet ID
        - Google Service Account credentials
        
        **For deployment platforms:**
        - **Streamlit Cloud**: Add in app settings
        - **Heroku**: Use config vars
        - **Railway**: Use environment variables
        """)
        
        st.markdown("---")
        
        # About
        st.subheader("ℹ️ About")
        st.info("""
        **Multi-Agent Architecture:**
        
        🔍 **Agent 1**: Resume Parser  
        📊 **Agent 2**: Job Analyzer  
        📄 **Agent 3**: HR Report Generator
        📝 **Google Sheets**: Auto-save results
        
        **Model**: Gemini 2.0 Flash (Free)
        """)
        
        # Demo data
        if st.button("📝 Load Demo Job Requirements"):
            st.session_state.demo_job = """**Job Title**: AI/ML Engineer

**Requirements**:
- 3+ years Python development experience
- Machine Learning frameworks (TensorFlow, PyTorch, Scikit-learn)
- Experience with AI/LLM applications
- Cloud platforms (AWS, GCP, Azure)
- Data processing and analysis
- Bachelor's degree in Computer Science or related field

**Nice to Have**:
- LangChain experience
- Streamlit/FastAPI development
- Docker/Kubernetes
- Research publications"""
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="agent-card"><h3>📄 Resume Upload</h3></div>', unsafe_allow_html=True)
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload Resume",
            type=['pdf', 'docx', 'txt'],
            help="Upload candidate's resume in PDF, DOCX, or TXT format"
        )
        
        # Extract text from file
        resume_text = ""
        if uploaded_file:
            with st.spinner("📖 Extracting text from resume..."):
                resume_text = process_uploaded_file(uploaded_file)
            
            if resume_text and not resume_text.startswith("Error"):
                st.success(f"✅ Successfully extracted {len(resume_text)} characters")
                with st.expander("📋 View Extracted Text"):
                    st.text_area("Resume Content", resume_text, height=200)
            else:
                st.error(f"❌ {resume_text}")
        
        # Manual text input (alternative)
        st.markdown("**Or paste resume text directly:**")
        manual_resume = st.text_area(
            "Resume Text",
            height=150,
            placeholder="Paste resume content here..."
        )
        
        # Use extracted text or manual input
        final_resume_text = resume_text if resume_text and not resume_text.startswith("Error") else manual_resume
    
    with col2:
        st.markdown('<div class="agent-card"><h3>💼 Job Requirements</h3></div>', unsafe_allow_html=True)
        
        # Load demo data if available
        default_job = st.session_state.get('demo_job', '')
        
        job_requirements = st.text_area(
            "Job Requirements",
            value=default_job,
            height=400,
            placeholder="Enter the job description and requirements..."
        )
    
    # Process button
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Process Candidate", type="primary", use_container_width=True):
            if not final_resume_text.strip():
                st.error("❌ Please upload a resume or enter resume text")
            elif not job_requirements.strip():
                st.error("❌ Please enter job requirements")
            elif not google_api_key:
                st.error("❌ Google API Key not configured. Please set GOOGLE_API_KEY environment variable.")
            else:
                process_candidate(final_resume_text, job_requirements)
    
    # Results display
    if st.session_state.processing_complete and st.session_state.results:
        display_results(st.session_state.results, job_requirements)

def process_candidate(resume_text, job_requirements):
    """Process candidate through the multi-agent system"""
    try:
        # Initialize HR agent
        with st.spinner("🤖 Initializing HR Assistant..."):
            hr_agent = HRAssistantAgents()
        
        # Process candidate
        with st.spinner("🔄 Processing candidate through multi-agent system..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Resume parsing
            status_text.text("🔍 Step 1: Parsing resume...")
            progress_bar.progress(33)
            
            # Step 2: Job analysis
            status_text.text("📊 Step 2: Analyzing job fit...")
            progress_bar.progress(66)
            
            # Step 3: Generate report
            status_text.text("📄 Step 3: Generating HR report...")
            progress_bar.progress(100)
            
            # Process
            results = hr_agent.process_candidate(resume_text, job_requirements)
            
            # Clear progress
            progress_bar.empty()
            status_text.empty()
            
            # Store results
            st.session_state.results = results
            st.session_state.processing_complete = True
            
            # Save to Google Sheets
            sheets_manager = st.session_state.sheets_manager
            if sheets_manager.is_connected():
                with st.spinner("💾 Saving to Google Sheets..."):
                    if sheets_manager.save_candidate_data(results, job_requirements):
                        st.success("✅ Processing complete! Data saved to Google Sheets.")
                    else:
                        st.success("✅ Processing complete! (Google Sheets save failed)")
            else:
                st.success("✅ Processing complete!")
                st.info("💡 Connect Google Sheets to auto-save results")
            
    except Exception as e:
        st.error(f"❌ Error processing candidate: {str(e)}")

def display_results(results, job_requirements=""):
    """Display processing results with beautiful visualizations"""
    st.markdown("---")
    st.markdown('<h2 style="text-align: center;">📊 Processing Results</h2>', unsafe_allow_html=True)
    
    # Recommendation banner
    score = results.get('score', 0)
    recommendation = results.get('recommendation', 'UNKNOWN')
    
    if recommendation == 'PROCEED':
        st.markdown(f'<div class="success-card"><h3>✅ RECOMMENDATION: PROCEED WITH INTERVIEW</h3><p>Candidate Score: {score}/100</p></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="warning-card"><h3>❌ RECOMMENDATION: REJECT CANDIDATE</h3><p>Candidate Score: {score}/100 (Below threshold)</p></div>', unsafe_allow_html=True)
    
    # Results tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📄 Parsed Resume", "🔍 Analysis", "📧 HR Report"])
    
    with tab1:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.plotly_chart(create_score_gauge(score), use_container_width=True)
        
        with col2:
            # Key metrics
            parsed_resume = results.get('parsed_resume', {})
            analysis = results.get('analysis', {})
            
            st.subheader("📋 Quick Summary")
            st.write(f"**Name:** {parsed_resume.get('name', 'N/A')}")
            st.write(f"**Experience:** {parsed_resume.get('experience_years', 'N/A')} years")
            st.write(f"**Score:** {score}/100")
            st.write(f"**Recommendation:** {recommendation}")
            
            if analysis:
                skill_matches = len(analysis.get('skill_matches', []))
                missing_skills = len(analysis.get('missing_skills', []))
                st.write(f"**Skills Match:** {skill_matches} matched, {missing_skills} missing")
    
    with tab2:
        parsed_resume = results.get('parsed_resume', {})
        if parsed_resume:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("👤 Personal Information")
                st.write(f"**Name:** {parsed_resume.get('name', 'N/A')}")
                st.write(f"**Email:** {parsed_resume.get('email', 'N/A')}")
                st.write(f"**Phone:** {parsed_resume.get('phone', 'N/A')}")
                st.write(f"**Experience:** {parsed_resume.get('experience_years', 'N/A')} years")
                
                st.subheader("🎓 Education")
                education = parsed_resume.get('education', 'N/A')
                st.write(education)
            
            with col2:
                st.subheader("💼 Work Experience")
                work_exp = parsed_resume.get('work_experience', [])
                for i, job in enumerate(work_exp):
                    st.write(f"{i+1}. {job}")
                
                st.subheader("🛠️ Skills")
                skills = parsed_resume.get('skills', [])
                if skills:
                    st.write(", ".join(skills))
                else:
                    st.write("No skills listed")
    
    with tab3:
        analysis = results.get('analysis', {})
        if analysis:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("✅ Matching Skills")
                skill_matches = analysis.get('skill_matches', [])
                for skill in skill_matches:
                    st.success(f"✅ {skill}")
                
                st.subheader("❌ Missing Skills")
                missing_skills = analysis.get('missing_skills', [])
                for skill in missing_skills:
                    st.error(f"❌ {skill}")
            
            with col2:
                st.subheader("📝 Analysis Summary")
                summary = analysis.get('analysis_summary', 'No summary available')
                st.write(summary)
                
                st.subheader("🎯 Score Breakdown")
                st.write(f"**Overall Score:** {analysis.get('overall_score', 0)}/100")
    
    with tab4:
        hr_report = results.get('hr_report', {})
        if hr_report:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("❓ Interview Questions")
                questions = hr_report.get('interview_questions', [])
                for i, question in enumerate(questions):
                    st.write(f"{i+1}. {question}")
            
            with col2:
                st.subheader("📧 Interview Email Template")
                email_template = hr_report.get('interview_email_template', 'Email template not generated')
                st.text_area("Email Template", email_template, height=300)
        else:
            st.info("HR Report not generated (candidate rejected or error occurred)")
    
    # Download and Google Sheets link
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        # Convert results to JSON for download
        results_json = json.dumps(results, indent=2)
        st.download_button(
            label="📥 Download Results (JSON)",
            data=results_json,
            file_name=f"hr_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col3:
        # Google Sheets link
        sheets_manager = st.session_state.sheets_manager
        if sheets_manager.is_connected() and sheets_manager.sheet_id:
            sheet_url = f"https://docs.google.com/spreadsheets/d/{sheets_manager.sheet_id}"
            st.link_button(
                label="📊 View Google Sheets",
                url=sheet_url,
                use_container_width=True
            )

if __name__ == "__main__":
    main() 