document.getElementById('searchForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const btn = document.getElementById('searchBtn');
    const status = document.getElementById('statusBar');
    const container = document.getElementById('resultsGrid');
    const countLabel = document.getElementById('resultCount');

    const payload = {
        all_words: document.getElementById('skill').value,
        experience: document.getElementById('experience').value,
        location: "India",
        radius: "50"
    };

    btn.disabled = true;
    btn.innerText = "PARSING CANDIDATES...";
    status.innerText = "Processing request...";
    container.innerHTML = ''; 
    countLabel.innerText = "Searching...";

    try {
        const response = await fetch('/api/candidates/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        btn.disabled = false;
        btn.innerText = "SEARCH PROFILES";
        
        if (data.status === 'success') {
            const candidates = data.candidates || [];
            countLabel.innerText = `${candidates.length} Profiles Found`;
            status.innerText = "Extraction Complete.";

            if (candidates.length === 0) {
                container.innerHTML = '<div style="color:#666">No candidates found matching criteria.</div>';
                return;
            }

            candidates.forEach(cand => {
                const skillsHtml = (cand.skills || []).slice(0, 4).map(s => 
                    `<span class="skill-tag">${s}</span>`
                ).join('');

                const card = document.createElement('div');
                card.className = 'card';
                card.innerHTML = `
                    <div class="card-header">
                        <div class="card-title">${cand.name || 'Hidden Candidate'}</div>
                        <div class="card-exp">${cand.experience_years || 'N/A'} Yrs</div>
                    </div>
                    <div class="card-meta">
                        ${cand.current_job_title || 'No Title'} • ${cand.location || 'India'}
                    </div>
                    <div class="card-skills">
                        ${skillsHtml}
                    </div>
                    <div class="card-summary">
                        ${cand.summary || 'No summary available.'}
                    </div>
                    <div class="card-actions">
                        <a href="${cand.resume_url}" target="_blank" class="btn-link">CONTACT CANDIDATE</a>
                    </div>
                `;
                container.appendChild(card);
            });
        } else {
            status.innerText = "Error: " + (data.error || "Unknown error");
            countLabel.innerText = "Search Failed";
        }

    } catch (error) {
        console.error(error);
        btn.disabled = false;
        btn.innerText = "SEARCH PROFILES";
        status.innerText = "Network Error.";
        countLabel.innerText = "Connection Failed";
    }
});