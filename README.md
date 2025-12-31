
# Candidate AI

**Candidate AI** is an intelligent resume search engine and parsing platform. It automates candidate sourcing by scraping public profiles from **PostJobFree**, extracting unstructured data using **Google Gemini 2.5 Flash**, and presenting it in a structured, actionable format for recruiters.

---

### Key Features

* **Gen AI Parsing:** Uses **Google Gemini 2.5 Flash** to intelligently extract skills, experience, education, and summaries from raw HTML resumes.
* **Real-time Scraping:** Fetches live candidate data dynamically from PostJobFree without relying on stale databases.
* **Filtering:** Search by **Skill** and **Years of Experience** with smart query construction.
* **Rate Limiting:** Implements sequential processing with auto-throttling to respect API rate limits and ensure stability.
* **Modern UI:** A professional dark-themed dashboard featuring:
    * **Expandable Candidate Cards:** Horizontal tabs with "Quick View" summaries.
    * **Dedicated Detail Page:** A clean, formatted profile view with session-based data storage.

---

### Tech Stack

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.0-092E20?style=for-the-badge&logo=django&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-2.5%20Flash-8E75B2?style=for-the-badge&logo=google&logoColor=white)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-Scraping-BC2F2F?style=for-the-badge)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

---

### Local Installation

Follow these steps to set up the project locally.

#### 1. Clone the repository
```bash
git clone [https://gitlab.com/yourusername/candidate-scout-ai.git](https://gitlab.com/yourusername/candidate-scout-ai.git)
cd candidate-scout-ai

```

#### 2. Set up virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate

```

#### 3. Install dependencies

```bash
pip install -r requirements.txt

```

#### 4. Configure Environment Variables

Create a `.env` file in the root directory and add your Google Gemini API key:

```ini
GEMINI_API_KEY=your_google_api_key_here

```

#### 5. Run the server

```bash
python manage.py runserver

```

The application will be available at `http://127.0.0.1:8000`.

---

### API Usage

You can also use the backend API directly for integration.

**Endpoint:** `POST /api/candidates/search`

**Request Body:**

```json
{
  "all_words": "Java Developer",
  "experience": 3,
  "location": "India",
  "radius": 50
}

```

**Response:**

```json
{
  "status": "success",
  "count": 10,
  "candidates": [
    {
      "name": "Rahul V.",
      "current_job_title": "Senior Java Engineer",
      "experience_years": 5,
      "skills": ["Java", "Spring Boot", "Microservices"],
      "location": "Bangalore, India",
      "resume_url": "[https://postjobfree.com/](https://postjobfree.com/)..."
    }
  ]
}

```

---

### Future Roadmap

* **Proxy Rotation:** Integrate `curl_cffi` to bypass advanced anti-bot protections.
* **Multi-Source Search:** Expand scraping to include other open resume databases.
* **Resume Download:** Add functionality to generate PDF summaries of parsed profiles.

---

### License

[MIT License](https://www.google.com/search?q=LICENSE)
