import requests
from bs4 import BeautifulSoup
import concurrent.futures
import logging
import time
from api.utils.gemini_parser import parse_resume_html

logger = logging.getLogger(__name__)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"}

def fetch_resume_details(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            return resp.text
    except Exception:
        return None
    return None

def search_and_process(skill, exp, limit):
    candidates = []
    search_url = f"https://www.postjobfree.com/resumes?q={skill}&n=&t={skill}&d={exp}&l=India&radius=100&r={limit}"
    
    print(f"[INFO] Searching: {search_url}")

    try:
        response = requests.get(url=search_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser') 

        resume_links = []
        for link in soup.find_all('a'):
            href = link.get('href', '')
            if '/resume/' in href and not href.endswith('/resume/'):
                full_url = "https://www.postjobfree.com" + href
                resume_links.append(full_url)

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            thread_dict = {
                executor.submit(fetch_resume_details, url): url for url in resume_links
            }

            for future in concurrent.futures.as_completed(thread_dict):
                current_url = thread_dict[future]
                content = future.result()

                if content:
                    print(f"[INFO] Processing: {current_url}")
                    time.sleep(4)
                    ai_data = parse_resume_html(content)

                    if ai_data:
                        ai_data['source'] = "PostJobFree"
                        ai_data['resume_url'] = current_url
                        
                        if not ai_data.get('skills'):
                            ai_data['skills'] = [skill]
                        
                        candidates.append(ai_data)

    except Exception as e:
        logger.error(f"Scraper Error: {e}")

    return candidates