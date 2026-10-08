// ==========================================================================
// ResumeX Pro — Interactive Frontend Engine & Dashboard Logic
// ==========================================================================

const analyzeForm = document.getElementById("analyzeForm");
const resultArea = document.getElementById("resultArea");
const resultPlaceholder = document.getElementById("resultPlaceholder");
const chartContainer = document.getElementById("chartContainer");
const chartCanvas = document.getElementById("skillsChart");

const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("resumeInput");
const fileInfoBox = document.getElementById("fileInfoBox");
const fileNameText = document.getElementById("fileNameText");
const fileSizeText = document.getElementById("fileSizeText");
const removeFileBtn = document.getElementById("removeFileBtn");

const submitBtn = document.getElementById("analyzeSubmitBtn");
const jobDescriptionInput = document.getElementById("jobDescriptionInput");

let skillsChart = null;

// --------------------------------------------------------------------------
// Quick Job Role Presets
// --------------------------------------------------------------------------
const jobPresets = {
    python: `Looking for a Python Backend Developer with strong experience in Python (Core & OOP), Django, Flask, and RESTful APIs. Experience with MySQL or PostgreSQL database design, query optimization, and Git version control. Knowledge of caching, Docker, and Linux environments is a plus.`,
    fullstack: `Hiring a Full-Stack Engineer proficient in React.js, JavaScript (ES6+), HTML5, CSS3, Tailwind CSS, and Python (Flask or Django). Candidate should be comfortable with REST APIs, component-based architectures, responsive web design, and Git workflow.`,
    ml: `Seeking a Junior Machine Learning / AI Engineer with solid Python programming, Scikit-learn, Pandas, NumPy, and Natural Language Processing (NLP) fundamentals including TF-IDF, text preprocessing, and predictive model evaluation metrics.`
};

function fillJobPreset(type) {
    if (jobDescriptionInput && jobPresets[type]) {
        jobDescriptionInput.value = jobPresets[type];
        jobDescriptionInput.focus();
    }
}

// --------------------------------------------------------------------------
// Drag & Drop File Upload Handling
// --------------------------------------------------------------------------
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

function updateFileDisplay(file) {
    if (file) {
        if (file.type !== "application/pdf" && !file.name.endsWith(".pdf")) {
            alert("Only PDF files are supported!");
            fileInput.value = "";
            return;
        }
        fileNameText.textContent = file.name;
        fileSizeText.textContent = formatFileSize(file.size);
        fileInfoBox.style.display = "flex";
        dropZone.style.display = "none";
    }
}

if (dropZone && fileInput) {
    dropZone.addEventListener("click", () => fileInput.click());

    fileInput.addEventListener("change", () => {
        if (fileInput.files.length > 0) {
            updateFileDisplay(fileInput.files[0]);
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
            fileInput.files = files;
            updateFileDisplay(files[0]);
        }
    });
}

if (removeFileBtn) {
    removeFileBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        fileInput.value = "";
        fileInfoBox.style.display = "none";
        dropZone.style.display = "block";
    });
}

// --------------------------------------------------------------------------
// Status Color Helper
// --------------------------------------------------------------------------
function getScoreBadge(score) {
    if (score >= 85) return { class: "pill-success", text: "Strong Match", icon: "fa-circle-check" };
    if (score >= 50) return { class: "pill-warning", text: "Potential Match", icon: "fa-triangle-exclamation" };
    return { class: "pill-danger", text: "Needs Optimization", icon: "fa-circle-xmark" };
}

// --------------------------------------------------------------------------
// Form Submit & Analysis
// --------------------------------------------------------------------------
if (analyzeForm) {
    analyzeForm.addEventListener("submit", async function (e) {
        e.preventDefault();

        if (!fileInput.files || fileInput.files.length === 0) {
            alert("Please select or drop a PDF resume first!");
            return;
        }

        const formData = new FormData(analyzeForm);

        // Loading state
        const btnText = submitBtn.querySelector(".btn-text");
        const btnSpinner = submitBtn.querySelector(".btn-spinner");
        submitBtn.disabled = true;
        btnText.classList.add("hidden");
        btnSpinner.classList.remove("hidden");

        resultPlaceholder.classList.add("hidden");
        resultArea.classList.remove("hidden");
        resultArea.innerHTML = `
            <div style="text-align: center; padding: 40px 20px;">
                <i class="fa-solid fa-spinner fa-spin" style="font-size: 36px; color: #38bdf8; margin-bottom: 16px;"></i>
                <h3 style="color: white; font-size: 17px; margin-bottom: 6px;">Extracting Text & Running NLP Vectorizer...</h3>
                <p style="color: #94a3b8; font-size: 13px;">Analyzing skill overlap, education, and ATS cosine similarity.</p>
            </div>
        `;

        try {
            const response = await fetch("/analyze", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (data.error) {
                resultArea.innerHTML = `
                    <div class="flash-toast flash-danger" style="margin: 20px 0;">
                        <i class="fa-solid fa-circle-exclamation"></i>
                        <span>${data.error}</span>
                    </div>
                `;
                return;
            }

            const badge = getScoreBadge(data.match_score || 0);

            // ------------------------------------------------------------------
            // Render Modern Intelligence Dashboard
            // ------------------------------------------------------------------
            resultArea.innerHTML = `
                <!-- Main Score & ATS Verdict Card -->
                <div class="mockup-card" style="margin-bottom: 24px; background: rgba(10, 15, 29, 0.95); border: 1px solid rgba(59, 130, 246, 0.3);">
                    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px;">
                        <div style="display: flex; align-items: center; gap: 20px;">
                            <div class="score-circle" style="width: 100px; height: 100px;">
                                <span class="score-value" style="font-size: 26px;">${data.match_score || 0}%</span>
                                <span class="score-text">ATS MATCH</span>
                            </div>
                            <div>
                                <span class="pill ${badge.class}" style="font-size: 12px; margin-bottom: 6px;">
                                    <i class="fa-solid ${badge.icon}"></i> ${badge.text}
                                </span>
                                <h3 style="color: white; font-size: 18px; margin: 4px 0;">${data.match_level || "Evaluated Match"}</h3>
                                <p style="color: #94a3b8; font-size: 12.5px;">${data.highlight_message || "Analysis complete against target job requirements."}</p>
                            </div>
                        </div>

                        <div>
                            <a href="/download-report" class="btn btn-primary btn-sm">
                                <i class="fa-solid fa-download"></i> Download Report
                            </a>
                        </div>
                    </div>

                    <!-- Key Statistics 4-Pillar Grid -->
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; margin-top: 20px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.08);">
                        <div style="background: rgba(15,23,42,0.8); padding: 10px; border-radius: 8px; text-align: center;">
                            <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase;">Keyword Overlap</div>
                            <div style="font-size: 18px; font-weight: 800; color: #38bdf8; font-family: var(--font-mono);">${data.keyword_overlap || 0}</div>
                        </div>
                        <div style="background: rgba(15,23,42,0.8); padding: 10px; border-radius: 8px; text-align: center;">
                            <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase;">Resume Words</div>
                            <div style="font-size: 18px; font-weight: 800; color: #a855f7; font-family: var(--font-mono);">${data.resume_word_count || 0}</div>
                        </div>
                        <div style="background: rgba(15,23,42,0.8); padding: 10px; border-radius: 8px; text-align: center;">
                            <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase;">Job Words</div>
                            <div style="font-size: 18px; font-weight: 800; color: #60a5fa; font-family: var(--font-mono);">${data.job_word_count || 0}</div>
                        </div>
                        <div style="background: rgba(15,23,42,0.8); padding: 10px; border-radius: 8px; text-align: center;">
                            <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase;">ATS Readiness</div>
                            <div style="font-size: 14px; font-weight: 700; color: #34d399; margin-top: 3px;">${data.ats_readiness || "Good"}</div>
                        </div>
                    </div>
                </div>

                <!-- Detected Education -->
                <div style="margin-bottom: 20px;">
                    <div class="mockup-section-title">
                        <i class="fa-solid fa-graduation-cap text-primary"></i> Detected Education & Qualifications
                    </div>
                    <div class="pill-group">
                        ${
                            data.education_list && data.education_list.length > 0
                                ? data.education_list.map(e => `<span class="pill pill-primary"><i class="fa-solid fa-check mr-1"></i> ${e}</span>`).join("")
                                : `<span class="pill" style="color: #94a3b8;">No standard degree keywords detected</span>`
                        }
                    </div>
                </div>

                <!-- Matched Skills -->
                <div style="margin-bottom: 20px;">
                    <div class="mockup-section-title">
                        <i class="fa-solid fa-circle-check text-success"></i> Matched Competencies (${data.resume_skills?.length || 0})
                    </div>
                    <div class="pill-group">
                        ${
                            data.resume_skills && data.resume_skills.length > 0
                                ? data.resume_skills.map(s => `<span class="pill pill-success">${s}</span>`).join("")
                                : `<span class="pill pill-warning">No skills detected in resume</span>`
                        }
                    </div>
                </div>

                <!-- Missing Skills -->
                <div style="margin-bottom: 24px;">
                    <div class="mockup-section-title">
                        <i class="fa-solid fa-triangle-exclamation text-warning"></i> Missing Skills Gap (${data.missing_skills?.length || 0})
                    </div>
                    <div class="pill-group">
                        ${
                            data.missing_skills && data.missing_skills.length > 0
                                ? data.missing_skills.map(s => `<span class="pill pill-danger"><i class="fa-solid fa-plus mr-1"></i> ${s}</span>`).join("")
                                : `<span class="pill pill-success">🎉 No critical skill gaps found!</span>`
                        }
                    </div>
                </div>

                <!-- AI Recommendations Checklist -->
                <div style="background: rgba(10, 15, 29, 0.7); border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin-bottom: 24px;">
                    <div class="mockup-section-title" style="color: #60a5fa; margin-bottom: 12px;">
                        <i class="fa-solid fa-lightbulb"></i> Actionable AI Resume Recommendations
                    </div>
                    <ul class="mockup-checklist" style="font-size: 13px; line-height: 1.7;">
                        ${
                            data.ai_feedback && data.ai_feedback.length > 0
                                ? data.ai_feedback.map(item => `<li><i class="fa-solid fa-arrow-right" style="color: #38bdf8;"></i> ${item}</li>`).join("")
                                : `<li>Maintain clear action verbs and quantifiable results in your experience section.</li>`
                        }
                    </ul>
                </div>
            `;

            // ------------------------------------------------------------------
            // Render Chart.js Visualization
            // ------------------------------------------------------------------
            if (chartCanvas && data.chart_data) {
                chartContainer.classList.remove("hidden");

                if (skillsChart) {
                    skillsChart.destroy();
                }

                skillsChart = new Chart(chartCanvas, {
                    type: "bar",
                    data: {
                        labels: data.chart_data.labels || ["Matched Skills", "Missing Skills", "Job Required"],
                        datasets: [{
                            label: "Skill Count Breakdown",
                            data: data.chart_data.values || [data.resume_skills?.length || 0, data.missing_skills?.length || 0, data.job_skills?.length || 0],
                            backgroundColor: [
                                "rgba(16, 185, 129, 0.75)",
                                "rgba(239, 68, 68, 0.75)",
                                "rgba(59, 130, 246, 0.75)"
                            ],
                            borderColor: [
                                "#10b981",
                                "#ef4444",
                                "#3b82f6"
                            ],
                            borderWidth: 1.5,
                            borderRadius: 6
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { display: false }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: { color: "#94a3b8", stepSize: 1 },
                                grid: { color: "rgba(255, 255, 255, 0.06)" }
                            },
                            x: {
                                ticks: { color: "#94a3b8" },
                                grid: { display: false }
                            }
                        }
                    }
                });
            }

        } catch (error) {
            console.error(error);
            resultArea.innerHTML = `
                <div class="flash-toast flash-danger">
                    <i class="fa-solid fa-circle-exclamation"></i>
                    <span>An error occurred while analyzing the resume. Please check your network and try again.</span>
                </div>
            `;
        } finally {
            submitBtn.disabled = false;
            btnText.classList.remove("hidden");
            btnSpinner.classList.add("hidden");
        }
    });
}
