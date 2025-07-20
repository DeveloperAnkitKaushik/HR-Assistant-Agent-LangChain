"""
LangChain HR Assistant Multi-Agent System
Implements 3 agents: Resume Parser, Job Analyzer, HR Report Generator
"""

import os
import json
import datetime
from typing import Dict, Any, List
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class HRAssistantAgents:
    """Multi-agent system for HR recruitment automation using LangChain"""
    
    def __init__(self):
        """Initialize the multi-agent system with free models"""
        
        # Use free models
        self.gemini_model = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.3,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            convert_system_message_to_human=True  # Fix for SystemMessage support
        )
        
        # Backup OpenAI model (if available)
        try:
            if os.getenv("OPENAI_API_KEY"):
                self.openai_model = ChatOpenAI(
                    model="gpt-3.5-turbo",
                    temperature=0.3,
                    openai_api_key=os.getenv("OPENAI_API_KEY")
                )
            else:
                self.openai_model = self.gemini_model  # Fallback to Gemini
        except:
            self.openai_model = self.gemini_model  # Fallback to Gemini
        
        # Initialize custom tools
        self.custom_tools = self._create_custom_tools()
        
    def _create_custom_tools(self) -> List[Tool]:
        """Create custom tools for the agents"""
        
        def generate_interview_email(input_data: str) -> str:
            """Generate personalized interview invitation email"""
            try:
                # Parse input (expecting JSON string)
                data = json.loads(input_data) if isinstance(input_data, str) else input_data
                
                candidate_name = data.get("candidate_name", "Candidate")
                candidate_email = data.get("candidate_email", "candidate@email.com")
                skills = data.get("skills", "Python, AI")
                score = data.get("score", 70)
                
                current_date = datetime.datetime.now().strftime("%B %d, %Y")
                
                email_template = f"""
Subject: Interview Invitation - HR Position

Dear {candidate_name},

Thank you for your interest in joining our team! Based on your resume review, we are impressed with your skills in {skills} and your overall qualification score of {score}/100.

We would like to invite you for an interview. Please choose one of the following time slots:

🗓️ **Available Slots:**
- Monday, {current_date} at 10:00 AM
- Tuesday, {current_date} at 2:00 PM  
- Wednesday, {current_date} at 11:00 AM

Please reply to this email ({candidate_email}) with your preferred time slot.

**Interview Details:**
- Duration: 45 minutes
- Format: Video call (link will be shared)
- Focus areas: Technical skills, experience, cultural fit

We look forward to speaking with you!

Best regards,
HR Team
Company Name
"""
                return email_template.strip()
                
            except Exception as e:
                return f"Error generating email: {str(e)}"
        
        email_tool = Tool(
            name="generate_interview_email",
            description="Generate personalized interview invitation email. Input should be JSON with candidate_name, candidate_email, skills, and score.",
            func=generate_interview_email
        )
        
        return [email_tool]
    
    def resume_parser_agent(self, resume_text: str) -> Dict[str, Any]:
        """
        Agent 1: Resume Parser
        Extracts and structures resume data
        """
        
        # Combine system and user message for Gemini compatibility
        combined_prompt = """You are a Resume Parser Agent. Your job is to extract and structure resume information into JSON format.

Extract the following information from the resume:
- name
- email  
- phone
- experience_years (estimate from work history)
- skills (list of technical skills)
- education (degree and institution)
- work_experience (list of job titles and companies)
- certifications (if any)

Return ONLY a valid JSON object without any markdown formatting or code blocks.

Resume to parse:
""" + resume_text
        
        try:
            response = self.gemini_model.invoke([HumanMessage(content=combined_prompt)])
            result = response.content.strip()
            
            # Clean up response (remove markdown if present)
            if result.startswith("```json"):
                result = result.replace("```json", "").replace("```", "").strip()
            
            # Validate JSON
            parsed_data = json.loads(result)
            return {"success": True, "data": parsed_data}
            
        except Exception as e:
            return {
                "success": False, 
                "error": f"Resume parsing failed: {str(e)}",
                "data": {}
            }
    
    def job_analyzer_agent(self, parsed_resume: Dict, job_requirements: str) -> Dict[str, Any]:
        """
        Agent 2: Job Analyzer  
        Compares resume with job requirements and scores candidate
        """
        
        resume_summary = json.dumps(parsed_resume, indent=2)
        
        # Combine system and user message for Gemini compatibility
        combined_prompt = f"""You are a Job Analyzer Agent. Compare the candidate's resume with job requirements and provide a detailed analysis.

Your tasks:
1. Analyze skill matches between resume and job requirements
2. Calculate an overall score (0-100) based on:
   - Skill alignment (40%)
   - Experience relevance (30%) 
   - Education fit (20%)
   - Certifications bonus (10%)
3. Provide recommendations

If the score is below 70, recommend rejection.
If 70 or above, recommend proceeding with interview.

Return ONLY a valid JSON object with:
- overall_score (number)
- skill_matches (list)
- missing_skills (list)  
- recommendation (PROCEED/REJECT)
- analysis_summary (string)

Resume Data:
{resume_summary}

Job Requirements:
{job_requirements}

Analyze and score this candidate."""
        
        try:
            response = self.gemini_model.invoke([HumanMessage(content=combined_prompt)])
            result = response.content.strip()
            
            # Clean up response
            if result.startswith("```json"):
                result = result.replace("```json", "").replace("```", "").strip()
            
            analysis = json.loads(result)
            return {"success": True, "data": analysis}
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Job analysis failed: {str(e)}",
                "data": {"overall_score": 0, "recommendation": "REJECT"}
            }
    
    def hr_report_generator_agent(self, parsed_resume: Dict, analysis: Dict) -> Dict[str, Any]:
        """
        Agent 3: HR Report Generator
        Creates final report and interview questions, uses email tool
        """
        
        # Simplify by generating email template directly
        try:
            # Generate email template using our custom function
            email_data = {
                "candidate_name": parsed_resume.get('name', 'Candidate'),
                "candidate_email": parsed_resume.get('email', 'candidate@email.com'),
                "skills": ', '.join(parsed_resume.get('skills', ['Python'])[:3]),
                "score": analysis.get('overall_score', 70)
            }
            
            # Use the email generation function directly
            email_template = self._generate_email_template(email_data)
            
            # Generate interview questions using Gemini
            combined_prompt = f"""You are an HR Report Generator Agent. Create interview questions based on the candidate analysis.

Resume Data: {json.dumps(parsed_resume, indent=2)}
Analysis Data: {json.dumps(analysis, indent=2)}

Generate exactly 5 relevant interview questions based on the candidate's background and the job requirements.

Return ONLY a valid JSON object with:
- formatted_resume (the resume data)
- analysis_summary (the analysis data)
- interview_questions (list of exactly 5 strings)

Do not include any markdown formatting."""

            response = self.gemini_model.invoke([HumanMessage(content=combined_prompt)])
            result = response.content.strip()
            
            # Clean up response
            if result.startswith("```json"):
                result = result.replace("```json", "").replace("```", "").strip()
            
            report_data = json.loads(result)
            
            # Add the email template
            report_data["interview_email_template"] = email_template
            
            return {"success": True, "data": report_data}
            
        except Exception as e:
            # Fallback: Create report manually
            fallback_report = {
                "formatted_resume": parsed_resume,
                "analysis_summary": analysis,
                "interview_questions": [
                    "Tell us about your experience with the technologies mentioned in your resume.",
                    "How do you stay updated with the latest trends in your field?",
                    "Describe a challenging project you worked on and how you overcame obstacles.",
                    "What interests you most about this role and our company?",
                    "Where do you see yourself in the next 3-5 years?"
                ],
                "interview_email_template": self._generate_email_template({
                    "candidate_name": parsed_resume.get('name', 'Candidate'),
                    "candidate_email": parsed_resume.get('email', 'candidate@email.com'),
                    "skills": ', '.join(parsed_resume.get('skills', ['Python'])[:3]),
                    "score": analysis.get('overall_score', 70)
                })
            }
            
            return {
                "success": True, 
                "data": fallback_report,
                "warning": f"AI generation failed, using fallback: {str(e)}"
            }
    
    def _generate_email_template(self, data: Dict) -> str:
        """Generate email template directly without LangChain tools"""
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        
        return f"""Subject: Interview Invitation - HR Position

Dear {data.get('candidate_name', 'Candidate')},

Thank you for your interest in joining our team! Based on your resume review, we are impressed with your skills in {data.get('skills', 'your technical skills')} and your overall qualification score of {data.get('score', 70)}/100.

We would like to invite you for an interview. Please choose one of the following time slots:

🗓️ **Available Slots:**
- Monday, {current_date} at 10:00 AM
- Tuesday, {current_date} at 2:00 PM  
- Wednesday, {current_date} at 11:00 AM

Please reply to this email ({data.get('candidate_email', 'candidate@email.com')}) with your preferred time slot.

**Interview Details:**
- Duration: 45 minutes
- Format: Video call (link will be shared)
- Focus areas: Technical skills, experience, cultural fit

We look forward to speaking with you!

Best regards,
HR Team
Company Name"""
    
    def process_candidate(self, resume_text: str, job_requirements: str) -> Dict[str, Any]:
        """
        Main workflow: Process candidate through all 3 agents
        """
        
        # Agent 1: Parse Resume
        print("🔍 Step 1: Parsing resume...")
        resume_result = self.resume_parser_agent(resume_text)
        
        if not resume_result["success"]:
            return {"error": "Resume parsing failed", "details": resume_result}
        
        parsed_resume = resume_result["data"]
        
        # Agent 2: Analyze Job Fit
        print("📊 Step 2: Analyzing job fit...")
        analysis_result = self.job_analyzer_agent(parsed_resume, job_requirements)
        
        if not analysis_result["success"]:
            return {"error": "Job analysis failed", "details": analysis_result}
        
        analysis = analysis_result["data"]
        
        # Check score threshold
        score = analysis.get("overall_score", 0)
        if score < 70:
            return {
                "recommendation": "REJECT",
                "score": score,
                "reason": "Score below threshold (70)",
                "parsed_resume": parsed_resume,
                "analysis": analysis
            }
        
        # Agent 3: Generate HR Report
        print("📄 Step 3: Generating HR report...")
        report_result = self.hr_report_generator_agent(parsed_resume, analysis)
        
        return {
            "recommendation": "PROCEED",
            "score": score,
            "parsed_resume": parsed_resume,
            "analysis": analysis,
            "hr_report": report_result["data"] if report_result["success"] else {},
            "success": True
        } 