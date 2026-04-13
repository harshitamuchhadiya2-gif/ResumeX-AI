const analyzeForm = document.getElementById("analyzeForm");
const resultArea = document.getElementById("resultArea");
const chartCanvas = document.getElementById("skillsChart");

const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("resumeInput");
const fileNameDisplay = document.getElementById("fileName");

let skillsChart = null;
let pieChart = null;


// -----------------------------
// Drag & Drop
// -----------------------------
if (dropZone) {

    dropZone.addEventListener("click", () => fileInput.click());

    fileInput.addEventListener("change", () => {
        if (fileInput.files.length > 0) {
            fileNameDisplay.textContent = "Selected: " + fileInput.files[0].name;
        }
    });

    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.classList.add("dragover");
    });

    dropZone.addEventListener("dragleave", () => {
        dropZone.classList.remove("dragover");
    });

    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.classList.remove("dragover");

        const files = e.dataTransfer.files;

        if (files.length > 0) {
            if (files[0].type !== "application/pdf") {
                alert("Only PDF files are allowed!");
                return;
            }

            fileInput.files = files;
            fileNameDisplay.textContent = "Selected: " + files[0].name;
        }
    });
}


// -----------------------------
// Status Color Logic
// -----------------------------
function getStatusClass(score) {
    if (score >= 85) return "status-green";
    if (score >= 50) return "status-yellow";
    return "status-red";
}


// -----------------------------
// Submit Form
// -----------------------------
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

            // -----------------------------
            // RESULT UI
            // -----------------------------
            resultArea.innerHTML = `

                <!-- Application Recommendation -->
                <div class="result-section glass-card application-box">
                    <h2>Application Recommendation</h2>

                    <p><strong>Status:</strong> 
                        <span class="status-highlight ${getStatusClass(data.match_score)}">
                            ${data.application_status || "Not Available"}
                        </span>
                    </p>

                    <p><strong>ATS Readiness:</strong> ${data.ats_readiness || "N/A"}</p>

                    <p><strong>Insight:</strong> ${data.highlight_message || ""}</p>

                    <p>${data.application_message || ""}</p>

                    <p><strong>Final Verdict:</strong> ${
                        data.match_score >= 85 ? "Strong Candidate" :
                        data.match_score >= 50 ? "Potential Candidate" :
                        "Needs Improvement"
                    }</p>
                </div>


                <!-- SCORE WITH DOUGHNUT -->
                <div class="score-box glass-card">

                    <div class="score-left">
                        <canvas id="scorePieChart"></canvas>
                        <div class="score-text">${data.match_score || 0}%</div>
                    </div>

                    <div class="score-right">
                        <h3>${data.match_level || "No Match Level"}</h3>
                        <p><strong>Keyword Overlap:</strong> ${data.keyword_overlap || 0}</p>
                        <p><strong>Resume Words:</strong> ${data.resume_word_count || 0}</p>
                        <p><strong>Job Words:</strong> ${data.job_word_count || 0}</p>
                    </div>

                </div>


                <!-- Education -->
                <div class="result-section">
                    <h3>Detected Education</h3>
                    <div class="tags-wrap">
                        ${
                            data.education_list?.length
                                ? data.education_list.map(e => `<span class="tag-pill success">${e}</span>`).join("")
                                : `<span class="tag-pill">No education detected</span>`
                        }
                    </div>
                </div>


                <!-- Resume Skills -->
                <div class="result-section">
                    <h3>Matched Resume Skills</h3>
                    <div class="tags-wrap">
                        ${
                            data.resume_skills?.length
                                ? data.resume_skills.map(s => `<span class="tag-pill success">${s}</span>`).join("")
                                : `<span class="tag-pill">No skills found</span>`
                        }
                    </div>
                </div>


                <!-- Job Skills -->
                <div class="result-section">
                    <h3>Job Required Skills</h3>
                    <div class="tags-wrap">
                        ${
                            data.job_skills?.length
                                ? data.job_skills.map(s => `<span class="tag-pill">${s}</span>`).join("")
                                : `<span class="tag-pill">No job skills found</span>`
                        }
                    </div>
                </div>


                <!-- Missing Skills -->
                <div class="result-section">
                    <h3>Missing Skills</h3>
                    <div class="tags-wrap">
                        ${
                            data.missing_skills?.length
                                ? data.missing_skills.map(s => `<span class="tag-pill danger">${s}</span>`).join("")
                                : `<span class="tag-pill success">No major missing skills 🎉</span>`
                        }
                    </div>
                </div>


                <!-- AI Feedback -->
                <div class="result-section">
                    <h3>AI Resume Improvement Suggestions</h3>
                    <ul class="suggestion-list">
                        ${
                            data.ai_feedback?.length
                                ? data.ai_feedback.map(i => `<li>${i}</li>`).join("")
                                : `<li>No AI feedback available.</li>`
                        }
                    </ul>
                </div>


                <!-- General Suggestions -->
                <div class="result-section">
                    <h3>General Suggestions</h3>
                    <ul class="suggestion-list">
                        ${
                            data.suggestions?.length
                                ? data.suggestions.map(i => `<li>${i}</li>`).join("")
                                : `<li>No suggestions available.</li>`
                        }
                    </ul>
                </div>


                <!-- Recommended Jobs -->
                <div class="result-section">
                    <h3>Recommended Job Roles</h3>
                    <div class="tags-wrap">
                        ${
                            data.recommended_jobs?.length
                                ? data.recommended_jobs.map(j => `<span class="tag-pill success">${j}</span>`).join("")
                                : `<span class="tag-pill">No recommended jobs found</span>`
                        }
                    </div>
                </div>
            `;

            // Render charts
            renderChart(data.chart_data);
            renderPieChart(data.match_score);

        } catch (error) {
            console.error("Analyze Error:", error);
            resultArea.innerHTML = `<p class="flash danger">Something went wrong. Please try again.</p>`;
        }
    });
}


// -----------------------------
// BAR CHART
// -----------------------------
function renderChart(chartData) {
    if (!chartCanvas || !chartData) return;

    if (skillsChart) {
        skillsChart.destroy();
    }

    skillsChart = new Chart(chartCanvas, {
        type: "bar",
        data: {
            labels: chartData.labels || [],
            datasets: [{
                label: "Skill Analysis",
                data: chartData.values || [],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: { color: "white" }
                }
            },
            scales: {
                x: { ticks: { color: "white" } },
                y: {
                    ticks: { color: "white" },
                    beginAtZero: true
                }
            }
        }
    });
}


// -----------------------------
// DOUGHNUT SCORE CHART
// -----------------------------
function renderPieChart(score) {
    const ctx = document.getElementById("scorePieChart");
    if (!ctx) return;

    if (pieChart) {
        pieChart.destroy();
    }

    let color;
    if (score >= 85) color = "#00ffae";
    else if (score >= 50) color = "#facc15";
    else color = "#ff4d4d";

    pieChart = new Chart(ctx, {
        type: "doughnut",
        data: {
            datasets: [{
                data: [score, 100 - score],
                backgroundColor: [color, "rgba(255,255,255,0.08)"],
                borderWidth: 0
            }]
        },
        options: {
            cutout: "70%",
            plugins: {
                legend: { display: false }
            }
        }
    });
}
