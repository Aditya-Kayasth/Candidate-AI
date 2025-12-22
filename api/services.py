import os
import time
import requests
import google.generativeai as genai
import logging
from bs4 import BeautifulSoup
import json

# Config
logger = logging.getLogger(__name__)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def search_candidates_core(skill, experience, location="remote", limit=5):
    """
    Scrapes PJF and uses Gemini to structure data. 
    Handles 429 Rate Limits and Threading safely.
    """

    # 1. Scrape Source (PostJobFree)
    base_url = "https://www.postjobfree.com/resumes"
    params = {
        "q": f"{skill} {experience} years",
        "l": location,
        "radius": 25
    }

    try:
        # User-Agent header is critical for scraping
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        resp = requests.get(base_url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()

        # Lightweight parse
        soup = BeautifulSoup(resp.text, 'html.parser')
        # Extract main content area only
        content = soup.find('div', class_='snippetPadding') or soup.find('body')
        raw_text = content.get_text(strip=True)[:8000] # Truncate for API limits

    except Exception as e:
        logger.error(f"Scrape failed: {e}")
        return {"error": "Failed to retrieve candidate data from source."}

    # 2. AI Parsing with Retry (Backoff)
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"""
    Act as a recruiter. Extract {limit} candidates from this raw text.
    Return ONLY a raw JSON list. No markdown formatting.
    Fields: name (or "Candidate"), title, location, years_exp (int), match_score (0-100), summary.

    Raw Text:
    {raw_text}
    """

    for attempt in range(3):
        try:
            # Generate
            response = model.generate_content(prompt)
            # Clean generic markdown if present
            clean_json = response.text.replace('```json', '').replace('```', '').strip()
            return {"status": "success", "data": clean_json}

        except Exception as e:
            if "429" in str(e):
                wait = 2 ** (attempt + 1)
                logger.warning(f"Gemini 429. Retrying in {wait}s...")
                time.sleep(wait)
            else:
                logger.error(f"AI Error: {e}")
                return {"error": str(e)}

    return {"error": "AI Service busy. Please try again."}