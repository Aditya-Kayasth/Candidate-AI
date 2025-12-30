import requests
from bs4 import BeautifulSoup
import logging
import time
from api.utils.gemini_parser import parse_resume_html

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_resume_details(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            return resp.text
    except Exception as e:
        logger.warning(f"Failed to fetch {url}: {e}")
        return None
    return None

def search_and_process(params):
    candidates = []
    
    query_parts = []
    
    if params.get('all_words'):
        query_parts.append(params['all_words'])
    
    if params.get('experience'):
        query_parts.append(f"{params['experience']} years")

    full_query = " ".join(query_parts)
    
    location = params.get('location', 'India')
    radius = params.get('radius', '50')
    limit = params.get('limit', 10)

    search_url = f"https://www.postjobfree.com/resumes?q={full_query}&l={location}&radius={radius}&r={limit}"
    print(f"\n[INFO] Searching URL: {search_url}")

    try:
        response = requests.get(url=search_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser') 

        resume_links = []
        for link in soup.find_all('a'):
            href = link.get('href', '')
            if '/resume/' in href and not href.endswith('/resume/'):
                full_url = "https://www.postjobfree.com" + href
                resume_links.append(full_url)

        print(f"[INFO] Found {len(resume_links)} links.")

        for i, url in enumerate(resume_links):
            if len(candidates) >= int(limit):
                break

            print(f"[INFO] Processing {i+1}/{len(resume_links)}: {url}")
            
            content = fetch_resume_details(url)

            if content:
                ai_data = parse_resume_html(content) 

                if ai_data:
                    ai_data['source'] = "PostJobFree"
                    ai_data['resume_url'] = url
                    
                    if not ai_data.get('skills'):
                        ai_data['skills'] = [params.get('all_words', 'N/A')]
                    
                    candidates.append(ai_data)
                    print(f"   Extracted: {ai_data.get('name', 'Unknown')}")
                else:
                    print("   Extraction Failed")

            time.sleep(4) 

    except Exception as e:
        logger.error(f"Scraper Error: {e}")
        print(f"[ERROR] {e}")

    return candidates