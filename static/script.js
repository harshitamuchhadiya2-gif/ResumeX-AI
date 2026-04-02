const analyzeForm = document.getElementById("analyzeForm");
const resultArea = document.getElementById("resultArea");
const chartCanvas = document.getElementById("skillsChart");

let skillsChart = null;

if (analyzeForm) {
    analyzeForm.addEventListener("submit", async function (e) {
        e.preventDefault();

        const formData = new FormData(analyzeForm);

        resultArea.innerHTML = `<p class="loading">Analyzing resume, please wait...</p>`;

        try {
            const response = await fetch("/analyze", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (data.error) {
                resultArea.innerHTML = `<p class="flash danger">${data.error}</p>`;
                return;
            }

            resultArea.innerHTML = `
                <div class="score-box">
                    <div class="score-ring">${data.match_score}%</div>
                    <div>
                        <h3>${data.match_level}</h3>
                        <p><strong>Keyword Overlap:</strong> ${data.keyword_overlap}</p>
                        <p><strong>Resume Words:</strong> ${data.resume_word_count}</p>
                        <p><strong>Job Description Words:</strong> ${data.job_word_count}</p>
                    </div>
                </div>

                <div class="result-section">
                    <h3>Matched Resume Skills</h3>
                    <div class="tags-wrap">
                        ${data.resume_skills.map(skill => `<span class="tag-pill success">${skill}</span>`).join("")}
                    </div>
                </div>

                <div class="result-section">
                    <h3>Job Required Skills</h3>
                    <div class="tags-wrap">
                        ${data.job_skills.map(skill => `<span class="tag-pill">${skill}</span>`).join("")}
                    </div>
                </div>

                <div class="result-section">
                    <h3>Missing Skills</h3>
                    <div class="tags-wrap">
                        ${data.missing_skills.length
                            ? data.missing_skills.map(skill => `<span class="tag-pill danger">${skill}</span>`).join("")
                            : `<span class="tag-pill success">No major missing skills 🎉</span>`
                        }
                    </div>
                </div>

                <div class="result-section">
                    <h3>AI Resume Improvement Suggestions</h3>
                    <ul class="suggestion-list">
                        ${data.ai_feedback.map(item => `<li>${item}</li>`).join("")}
                    </ul>
                </div>

                <div class="result-section">
                    <h3>General Suggestions</h3>
                    <ul class="suggestion-list">
                        ${data.suggestions.map(item => `<li>${item}</li>`).join("")}
                    </ul>
                </div>

                <div class="result-section">
                    <h3>Recommended Job Roles</h3>
                    <div class="tags-wrap">
                        ${data.recommended_jobs.map(job => `<span class="tag-pill success">${job}</span>`).join("")}
                    </div>
                </div>
            `;

            renderChart(data.chart_data);

        } catch (error) {
            resultArea.innerHTML = `<p class="flash danger">Something went wrong. Please try again.</p>`;
        }
    });
}

function renderChart(chartData) {
    if (!chartCanvas) return;

    if (skillsChart) {
        skillsChart.destroy();
    }

    skillsChart = new Chart(chartCanvas, {
        type: "bar",
        data: {
            labels: chartData.labels,
            datasets: [{
                label: "Skill Analysis",
                data: chartData.values,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: {
                        color: "white"
                    }
                }
            },
            scales: {
                x: {
                    ticks: { color: "white" }
                },
                y: {
                    ticks: { color: "white" },
                    beginAtZero: true
                }
            }
        }
    });
}


