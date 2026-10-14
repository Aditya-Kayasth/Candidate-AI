import requests
from bs4 import BeautifulSoup
import logging
import time
import os
import json
from api.utils.gemini_parser import parse_resume_html

try:
    from curl_cffi import requests as cffi_requests
    HAS_CURL_CFFI = True
except ImportError:
    HAS_CURL_CFFI = False

logger = logging.getLogger(__name__)

SAMPLE_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'sample_response.json')

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

def get_cached_candidates(params):
    """
    Returns cached profiles from sample_response.json when PostJobFree blocks requests.
    Filters and sorts based on requested skill, experience, and limit.
    """
    try:
        if os.path.exists(SAMPLE_FILE_PATH):
            with open(SAMPLE_FILE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                candidates = data.get('candidates', [])

                skill = str(params.get('all_words') or params.get('skill') or '').lower().strip()
                target_exp = None
                try:
                    if params.get('experience'):
                        target_exp = float(params.get('experience'))
                except (ValueError, TypeError):
                    target_exp = None

                filtered = []
                for c in candidates:
                    match_skill = True
                    if skill:
                        cand_skills = [str(s).lower() for s in c.get('skills', [])]
                        title = str(c.get('current_job_title') or '').lower()
                        summary = str(c.get('summary') or '').lower()
                        match_skill = any(skill in s for s in cand_skills) or (skill in title) or (skill in summary)

                    if match_skill:
                        filtered.append(c)

                # If matching skill candidates found, use them; otherwise use full pool
                res = filtered if filtered else candidates

                # Sort by experience proximity if requested
                if target_exp is not None:
                    res = sorted(res, key=lambda c: abs(float(c.get('experience_years') or 0) - target_exp))

                limit = int(params.get('limit') or 10)
                print(f"[INFO] Returning {min(len(res), limit)} cached candidate profile(s) for showcase.")
                return res[:limit]
    except Exception as e:
        logger.error(f"Error loading cached candidates: {e}")
    return []

def fetch_resume_details(url):
    try:
        if HAS_CURL_CFFI:
            try:
                resp = cffi_requests.get(url, impersonate='chrome124', timeout=10)
                if resp.status_code == 200:
                    return resp.text
            except Exception:
                pass
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
    limit = int(params.get('limit', 10))

    search_url = f"https://www.postjobfree.com/resumes?q={full_query}&l={location}&radius={radius}&r={limit}"
    print(f"\n[INFO] Searching URL: {search_url}")

    try:
        response_text = None
        status_code = None

        if HAS_CURL_CFFI:
            try:
                resp = cffi_requests.get(search_url, impersonate='chrome124', timeout=10)
                status_code = resp.status_code
                if status_code == 200:
                    response_text = resp.text
            except Exception as e:
                logger.warning(f"curl_cffi error: {e}")

        if not response_text:
            response = requests.get(url=search_url, headers=HEADERS, timeout=10)
            status_code = response.status_code
            if status_code == 200:
                response_text = response.text

        if status_code != 200 or not response_text:
            print(f"[WARNING] PostJobFree returned HTTP {status_code}. Using cached results.")
            return get_cached_candidates(params)

        soup = BeautifulSoup(response_text, 'html.parser')
        resume_links = []
        for link in soup.find_all('a'):
            href = link.get('href', '')
            if '/resume/' in href and not href.endswith('/resume/'):
                full_url = "https://www.postjobfree.com" + href
                resume_links.append(full_url)

        print(f"[INFO] Found {len(resume_links)} links.")

        if not resume_links:
            print("[WARNING] No resume links found. Using cached results.")
            return get_cached_candidates(params)

        for i, url in enumerate(resume_links):
            if len(candidates) >= limit:
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

        if len(candidates) < limit:
            print(f"[INFO] Supplementing {len(candidates)} extracted candidate(s) with cached profiles for full showcase.")
            cached = get_cached_candidates(params)
            existing_names = {c.get('name') for c in candidates}
            for c in cached:
                if len(candidates) >= limit:
                    break
                if c.get('name') not in existing_names:
                    candidates.append(c)

    except Exception as e:
        logger.error(f"Scraper Error: {e}")
        print(f"[ERROR] {e} - using cached results")
        return get_cached_candidates(params)

    return candidates