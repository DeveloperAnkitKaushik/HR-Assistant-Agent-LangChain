"""
Google Sheets Integration for HR Assistant
Saves candidate data and results to Google Sheets
"""

import gspread
from google.auth import default
import os
from datetime import datetime
import json
import streamlit as st

class GoogleSheetsManager:
    """Manages Google Sheets operations for HR data"""
    
    def __init__(self, sheet_id=None):
        """Initialize Google Sheets connection"""
        self.sheet_id = sheet_id or os.getenv("GOOGLE_SHEET_ID", "")
        self.gc = None
        self.sheet = None
        self._connect()
    
    def _connect(self):
        """Connect to Google Sheets"""
        try:
            # Try service account first (for deployment)
            if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                self.gc = gspread.service_account()
            else:
                # Use API key for simple authentication
                self.gc = gspread.service_account_from_dict({
                    "type": "service_account",
                    "project_id": os.getenv("GOOGLE_PROJECT_ID", ""),
                    "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID", ""),
                    "private_key": os.getenv("GOOGLE_PRIVATE_KEY", "").replace('\\n', '\n'),
                    "client_email": os.getenv("GOOGLE_CLIENT_EMAIL", ""),
                    "client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{os.getenv('GOOGLE_CLIENT_EMAIL', '')}"
                })
            
            if self.sheet_id:
                spreadsheet = self.gc.open_by_key(self.sheet_id)
                
                # Try to get the "candidates - langchain" sheet, create if it doesn't exist
                try:
                    self.sheet = spreadsheet.worksheet("candidates - langchain")
                except:
                    # Create new sheet with the desired name
                    self.sheet = spreadsheet.add_worksheet(title="candidates - langchain", rows="1000", cols="20")
                
                self._setup_headers()
                
        except Exception as e:
            st.warning(f"⚠️ Google Sheets connection failed: {str(e)}")
            self.gc = None
            self.sheet = None
    
    def _setup_headers(self):
        """Setup headers for the Google Sheet"""
        headers = [
            "Timestamp", "Candidate Name", "Email", "Phone", 
            "Experience (Years)", "Overall Score", "Recommendation",
            "Matching Skills", "Missing Skills", "Education",
            "Job Title", "Analysis Summary", "Interview Questions"
        ]
        
        try:
            # Check if headers exist
            existing_headers = self.sheet.row_values(1)
            if not existing_headers or existing_headers != headers:
                self.sheet.clear()
                self.sheet.append_row(headers)
        except Exception as e:
            st.warning(f"⚠️ Could not setup headers: {str(e)}")
    
    def save_candidate_data(self, results, job_requirements=""):
        """Save candidate assessment results to Google Sheets"""
        if not self.sheet:
            return False
        
        try:
            parsed_resume = results.get('parsed_resume', {})
            analysis = results.get('analysis', {})
            hr_report = results.get('hr_report', {})
            
            # Extract job title from job requirements
            job_title = "N/A"
            if "Job Title" in job_requirements:
                lines = job_requirements.split('\n')
                for line in lines:
                    if "Job Title" in line:
                        job_title = line.split(':')[-1].strip().replace('*', '')
                        break
            
            # Handle education field properly (convert complex objects to strings)
            education_text = "N/A"
            education_data = parsed_resume.get('education', [])
            if education_data:
                if isinstance(education_data, list):
                    # If it's a list of education objects
                    education_parts = []
                    for edu in education_data:
                        if isinstance(edu, dict):
                            degree = edu.get('degree', '')
                            institution = edu.get('institution', '')
                            education_parts.append(f"{degree} from {institution}".strip())
                        else:
                            education_parts.append(str(edu))
                    education_text = ' | '.join(education_parts)
                elif isinstance(education_data, dict):
                    # If it's a single education object
                    degree = education_data.get('degree', '')
                    institution = education_data.get('institution', '')
                    education_text = f"{degree} from {institution}".strip()
                else:
                    # If it's a simple string
                    education_text = str(education_data)
            
            # Prepare row data
            row_data = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Timestamp
                parsed_resume.get('name', 'N/A'),              # Candidate Name
                parsed_resume.get('email', 'N/A'),             # Email
                parsed_resume.get('phone', 'N/A'),             # Phone
                str(parsed_resume.get('experience_years', 'N/A')), # Experience
                str(results.get('score', 0)),                  # Overall Score
                results.get('recommendation', 'UNKNOWN'),      # Recommendation
                ', '.join(analysis.get('skill_matches', [])),  # Matching Skills
                ', '.join(analysis.get('missing_skills', [])), # Missing Skills
                education_text,                                # Education
                job_title,                                     # Job Title
                analysis.get('analysis_summary', 'N/A'),       # Analysis Summary
                ' | '.join(hr_report.get('interview_questions', [])) # Interview Questions
            ]
            
            # Append to sheet
            self.sheet.append_row(row_data)
            
            return True
            
        except Exception as e:
            st.error(f"❌ Failed to save to Google Sheets: {str(e)}")
            return False
    
    def get_candidates_summary(self):
        """Get summary statistics from Google Sheets"""
        if not self.sheet:
            return None
        
        try:
            all_records = self.sheet.get_all_records()
            if not all_records:
                return None
            
            total_candidates = len(all_records)
            approved = len([r for r in all_records if r.get('Recommendation') == 'PROCEED'])
            rejected = total_candidates - approved
            
            return {
                'total_candidates': total_candidates,
                'approved': approved,
                'rejected': rejected,
                'approval_rate': round((approved / total_candidates) * 100, 1) if total_candidates > 0 else 0
            }
        except Exception as e:
            st.warning(f"⚠️ Could not fetch summary: {str(e)}")
            return None
    
    def is_connected(self):
        """Check if Google Sheets is connected"""
        return self.sheet is not None 