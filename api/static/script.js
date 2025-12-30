const sidebar = document.getElementById('searchPanel');
const toggleBtn = document.getElementById('sidebarToggle');
let isCollapsed = false;

toggleBtn.innerHTML = "◀";

toggleBtn.addEventListener('click', () => {
    isCollapsed = !isCollapsed;
    sidebar.classList.toggle('collapsed');
    toggleBtn.innerHTML = isCollapsed ? "▶" : "◀";
});

document.getElementById('searchForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const progressBar = document.getElementById('progressBar');
    const progressContainer = document.getElementById('progressContainer');
    const status = document.getElementById('statusBar');
    const container = document.getElementById('resultsGrid');
    
    container.innerHTML = '';
    progressContainer.style.display = 'block';
    progressBar.style.width = '0%';
    progressBar.classList.add('loading');
    status.innerText = "Initializing Search Agents...";

    const payload = {
        all_words: document.getElementById('skill').value,
        experience: document.getElementById('experience').value,
        location: "India",
        radius: "50"
    };

    try {
        let progress = 10;
        const interval = setInterval(() => {
            progress += Math.random() * 10;
            if (progress > 90) progress = 90;
            if(progress < 30) status.innerText = "Scraping PostJobFree...";
            else if(progress < 60) status.innerText = "Analyzing Resume HTML...";
            else status.innerText = "Extracting Skills & Experience...";
        }, 800);

        const response = await fetch('/api/candidates/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        clearInterval(interval);

        progressBar.classList.remove('loading');
        progressBar.style.width = '100%';
        
        if (data.status === 'success') {
            status.innerText = `Done. Found ${data.candidates.length} profiles.`;
            document.getElementById('resultCount').innerText = `${data.candidates.length} Results`;
            
            data.candidates.forEach(cand => {
                 const card = document.createElement('div');
                 card.className = 'card';
                 card.innerHTML = `
                    <div class="card-header">
                        <div class="card-main-info">
                            <div>
                                <span class="card-title">${cand.name || 'Hidden Candidate'}</span>
                                <span class="badge">${cand.experience_years || 'N/A'} Yrs Exp</span>
                            </div>
                            <div class="card-meta">
                                <span>${cand.current_job_title || 'No Title'}</span>
                                <span>•</span>
                                <span>${cand.location || 'India'}</span>
                            </div>
                        </div>
                    </div>
                    <div class="card-skills">
                        ${(cand.skills || []).slice(0, 5).map(s => `<span class="skill-tag">${s}</span>`).join('')}
                    </div>
                    <button class="toggle-details-btn" onclick="this.parentElement.querySelector('.card-summary').classList.toggle('expanded'); this.parentElement.querySelector('.card-actions').style.display = this.parentElement.querySelector('.card-summary').classList.contains('expanded') ? 'block' : 'none'; this.innerText = this.innerText.includes('Show') ? 'Show Less ▴' : 'Show Details ▾'">Show Details ▾</button>
                    <div class="card-summary">
                        <p><strong>Summary:</strong> ${cand.summary || 'No summary available.'}</p>
                        <p style="margin-top:10px; color: #888;"><strong>Education:</strong> ${cand.education_summary || 'N/A'}</p>
                    </div>
                    <div class="card-actions">
                        <button onclick='viewCandidateDetail(${JSON.stringify(cand).replace(/'/g, "&#39;")})' class="btn-link">VIEW FULL DETAIL</button>
                    </div>
                 `;
                 container.appendChild(card);
            });

        } else {
            status.innerText = "Error: " + data.error;
            progressBar.style.backgroundColor = "red";
        }

    } catch (error) {
        console.error(error);
        status.innerText = "Connection Failed.";
    }
});

function viewCandidateDetail(candidateData) {

    sessionStorage.setItem('selectedCandidate', JSON.stringify(candidateData));

    window.location.href = '/candidate/detail';
}