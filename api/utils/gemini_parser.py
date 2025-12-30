import google.generativeai as genai
import json
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

def parse_resume_html(html_content):
    try:
        model = genai.GenerativeModel('gemini-2.5-flash', 
            generation_config={"response_mime_type": "application/json"}
        )

        prompt = f"""
        You are a Resume Parser. Analyze the following HTML content of a candidate profile.
        Extract these specific details into a valid JSON object. 
        
        Rules:
        - If a field is missing, use null.
        - "skills": Extract a list of technical skills.
        - "experience_years": Estimate the total years as a number (e.g., 5).
        - "current_company": The most recent company they worked for.
        - "education_summary": A short string like "B.Tech in CS from IIT Delhi".
        
        JSON Structure needed:
        {{
            "name": "Candidate Name",
            "location": "City, Country",
            "current_job_title": "Job Title",
            "current_company": "Company Name",
            "skills": ["Skill1", "Skill2"],
            "experience_years": 5,
            "education_summary": "Degree details",
            "summary": "Brief professional summary"
        }}

        HTML Content:
        {html_content[:15000]} 
        """

        response = model.generate_content(prompt)
        return json.loads(response.text)

    except Exception as e:
        logger.error(f"GenAI Error: {e}")
        return None