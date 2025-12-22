import os
import time
import requests
import google.generativeai as genai
import logging
import json
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Config
logger = logging.getLogger(__name__)
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

def search_candidates_core(skill, experience, location="remote", limit=5):
    """
    Orchestrates scraping + Advanced Gemini Parsing
    """
    # 1. Scrape PostJobFree (Lightweight Source)
    base_url = "https://www.postjobfree.com/resumes"
    params = {
        "q": f"{skill} {experience} years",
        "l": location,
        "radius": 25
    }
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        resp = requests.get(base_url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        content = soup.find('div', class_='snippetPadding') or soup.find('body')
        # Get raw text but keep some structure
        raw_text = content.get_text(" | ", strip=True)[:12000] 
        
    except Exception as e:
        logger.error(f"Scrape failed: {e}")
        return {"error": "Failed to retrieve data from source."}

    # 2. Advanced AI Parsing (Your Logic + Retry Safety)
    # We use 'gemini-2.0-flash' as you requested for speed and JSON mode
    model = genai.GenerativeModel('gemini-2.0-flash', 
        generation_config={"response_mime_type": "application/json"}
    )

    prompt = f"""
    You are an expert Technical Recruiter. Analyze the following raw resume search results.
    Extract exactly {limit} best-fit candidates for the role of: {skill} ({experience}+ years exp).
    
    Return a JSON object with a key "candidates" containing a list. 
    Each candidate object must have:
    - "name": Generate a realistic placeholder name if hidden (e.g., "Senior Java Dev").
    - "match_score": A number 0-100 based on keyword match.
    - "current_job_title": Their refined job title.
    - "location": City/Country.
    - "experience_years": Number (estimate if needed).
    - "skills": Array of top 3-4 relevant skills.
    - "summary": A punchy 1-sentence marketing summary of this candidate.

    Raw Data:
    {raw_text}
    """

    for attempt in range(3):
        try:
            response = model.generate_content(prompt)
            # Parse the JSON response
            data = json.loads(response.text)
            
            # handle cases where AI returns list directly vs dict
            candidates = data.get('candidates', data) if isinstance(data, dict) else data
            
            return {"status": "success", "data": candidates}

        except Exception as e:
            if "429" in str(e):
                time.sleep(2 ** (attempt + 1)) # Exponential backoff
            else:
                logger.error(f"GenAI Error: {e}")
                return {"error": str(e)}

    return {"error": "AI Service busy. Please try again."}