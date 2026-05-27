document.addEventListener("DOMContentLoaded", () => {
    // State Variables
    let allSymptoms = [];
    const selectedSymptoms = new Set();
    let currentFocusedIndex = -1;
    let activeMode = "checklist"; // "checklist" or "nlp"

    // DOM Elements
    const symptomInput = document.getElementById("symptom-input");
    const autocompleteList = document.getElementById("autocomplete-list");
    const activeTagsContainer = document.getElementById("active-tags");
    const tagsCountBadge = document.getElementById("tags-count");
    const btnPredict = document.getElementById("btn-predict");
    const btnReset = document.getElementById("btn-reset");
    
    // Hybrid Consult Switcher DOM Elements
    const modeButtons = document.querySelectorAll(".mode-btn");
    const panelChecklist = document.getElementById("panel-checklist");
    const panelNlp = document.getElementById("panel-nlp");
    const nlpInput = document.getElementById("nlp-input");
    const charWarning = document.getElementById("char-warning");
    const modeDesc = document.getElementById("mode-desc");
    
    // Diagnostic Card Views
    const reportCard = document.getElementById("report-card");
    const welcomeView = document.getElementById("output-welcome");
    const loaderView = document.getElementById("output-loader");
    const reportView = document.getElementById("output-report");
    
    // Diagnosis Data Renderers
    const predictedDiseaseElem = document.getElementById("predicted-disease");
    const diseaseDescElem = document.getElementById("disease-desc");
    const precautionsList = document.getElementById("disease-precautions");
    const medicationsList = document.getElementById("disease-medications");
    const dietList = document.getElementById("disease-diet");
    const workoutList = document.getElementById("disease-workout");
    
    // Tabs Navigation
    const tabButtons = document.querySelectorAll(".tab-btn");
    const tabPanes = document.querySelectorAll(".tab-pane");

    /* ==========================================================================
       INITIALIZATION & DATA FETCHING
       ========================================================================== */
    async function fetchSymptoms() {
        try {
            const response = await fetch("/api/symptoms");
            if (!response.ok) throw new Error("Failed to load symptoms database");
            allSymptoms = await response.json();
            console.log(`Loaded ${allSymptoms.length} symptoms successfully.`);
        } catch (error) {
            console.error("Error loading symptoms:", error);
            showErrorState("Could not connect to backend server. Please ensure Flask app is running.");
        }
    }

    fetchSymptoms();

    /* ==========================================================================
       AUTOCOMPLETE DROPDOWN LOGIC
       ========================================================================== */
    symptomInput.addEventListener("input", () => {
        const query = symptomInput.value.toLowerCase().trim();
        closeDropdown();

        if (!query) return;

        // Filter symptoms that match the search query and are not already selected
        const matches = allSymptoms.filter(symptom => 
            symptom.toLowerCase().includes(query) && !selectedSymptoms.has(symptom)
        ).slice(0, 8); // Limit to top 8 results

        if (matches.length > 0) {
            renderDropdown(matches);
        }
    });

    // Keyboard navigation within autocomplete dropdown
    symptomInput.addEventListener("keydown", (e) => {
        const items = autocompleteList.getElementsByClassName("autocomplete-item");
        if (items.length === 0) return;

        if (e.key === "ArrowDown") {
            e.preventDefault();
            currentFocusedIndex = (currentFocusedIndex + 1) % items.length;
            setActiveDropdownItem(items);
        } else if (e.key === "ArrowUp") {
            e.preventDefault();
            currentFocusedIndex = (currentFocusedIndex - 1 + items.length) % items.length;
            setActiveDropdownItem(items);
        } else if (e.key === "Enter") {
            e.preventDefault();
            if (currentFocusedIndex > -1 && currentFocusedIndex < items.length) {
                items[currentFocusedIndex].click();
            } else if (items.length > 0) {
                items[0].click(); // Default select the first match
            }
        } else if (e.key === "Escape") {
            closeDropdown();
        }
    });

    function renderDropdown(matches) {
        autocompleteList.innerHTML = "";
        currentFocusedIndex = -1;

        matches.forEach(match => {
            const item = document.createElement("div");
            item.className = "autocomplete-item";
            
            // Highlight matching text portion
            const query = symptomInput.value.trim();
            const index = match.toLowerCase().indexOf(query.toLowerCase());
            if (index !== -1) {
                const before = match.substring(0, index);
                const highlight = match.substring(index, index + query.length);
                const after = match.substring(index + query.length);
                item.innerHTML = `${before}<strong>${highlight}</strong>${after}`;
            } else {
                item.textContent = match;
            }

            // Click listener
            item.addEventListener("click", () => {
                addSymptomTag(match);
                symptomInput.value = "";
                closeDropdown();
                symptomInput.focus();
            });

            autocompleteList.appendChild(item);
        });

        autocompleteList.classList.remove("hidden");
    }

    function setActiveDropdownItem(items) {
        // Remove active class from all items
        Array.from(items).forEach(item => item.classList.remove("selected-keyboard"));
        
        if (currentFocusedIndex > -1) {
            const activeItem = items[currentFocusedIndex];
            activeItem.classList.add("selected-keyboard");
            // Scroll dropdown if item is out of view
            activeItem.scrollIntoView({ block: "nearest" });
        }
    }

    function closeDropdown() {
        autocompleteList.innerHTML = "";
        autocompleteList.classList.add("hidden");
        currentFocusedIndex = -1;
    }

    // Close dropdown when clicking outside
    document.addEventListener("click", (e) => {
        if (e.target !== symptomInput && e.target !== autocompleteList) {
            closeDropdown();
        }
    });

    /* ==========================================================================
       TAG MANAGEMENT
       ========================================================================== */
    function addSymptomTag(symptom) {
        if (selectedSymptoms.has(symptom)) return;

        selectedSymptoms.add(symptom);
        renderTags();
        updatePredictButtonState();
    }

    function removeSymptomTag(symptom) {
        selectedSymptoms.delete(symptom);
        renderTags();
        updatePredictButtonState();
    }

    function renderTags() {
        // Clear container
        activeTagsContainer.innerHTML = "";
        
        const count = selectedSymptoms.size;
        tagsCountBadge.textContent = count;

        if (count === 0) {
            const placeholder = document.createElement("p");
            placeholder.className = "no-tags-placeholder";
            placeholder.textContent = "No symptoms selected yet. Type above to add.";
            activeTagsContainer.appendChild(placeholder);
            return;
        }

        selectedSymptoms.forEach(symptom => {
            const tag = document.createElement("span");
            tag.className = "tag";
            tag.textContent = symptom;

            const removeBtn = document.createElement("span");
            removeBtn.className = "tag-remove";
            removeBtn.innerHTML = "&times;";
            removeBtn.addEventListener("click", (e) => {
                e.stopPropagation();
                removeSymptomTag(symptom);
            });

            tag.appendChild(removeBtn);
            activeTagsContainer.appendChild(tag);
        });
    }

    /* ==========================================================================
       HYBRID MODE SWITCHER LOGIC
       ========================================================================== */
    modeButtons.forEach(button => {
        button.addEventListener("click", () => {
            const mode = button.getAttribute("data-mode");
            if (activeMode === mode) return;

            activeMode = mode;
            
            // Toggle active classes on mode buttons
            modeButtons.forEach(btn => btn.classList.remove("active"));
            button.classList.add("active");

            // Toggle panels visibility
            if (mode === "checklist") {
                panelChecklist.classList.remove("hidden");
                panelNlp.classList.add("hidden");
                modeDesc.textContent = "Search and select one or more symptoms below to compile a diagnosis report.";
            } else {
                panelChecklist.classList.add("hidden");
                panelNlp.classList.remove("hidden");
                modeDesc.textContent = "Describe your physical symptoms in your own words to execute Clinical AI transformer diagnostic models.";
            }

            updatePredictButtonState();
        });
    });

    nlpInput.addEventListener("input", () => {
        updatePredictButtonState();
    });

    function updatePredictButtonState() {
        if (activeMode === "checklist") {
            btnPredict.disabled = selectedSymptoms.size === 0;
        } else {
            const textLength = nlpInput.value.trim().length;
            const isValid = textLength >= 10;
            btnPredict.disabled = !isValid;
            
            if (isValid) {
                charWarning.textContent = "Detailed description provided. Ready to analyse.";
                charWarning.classList.add("valid");
            } else {
                charWarning.textContent = `Please enter a detailed description of minimum 10 characters (${textLength}/10).`;
                charWarning.classList.remove("valid");
            }
        }
    }

    /* ==========================================================================
       TABS NAVIGATION
       ========================================================================== */
    tabButtons.forEach(button => {
        button.addEventListener("click", () => {
            const targetTab = button.getAttribute("data-tab");

            // Deactivate all buttons & panes
            tabButtons.forEach(btn => btn.classList.remove("active"));
            tabPanes.forEach(pane => pane.classList.remove("active"));

            // Activate current
            button.classList.add("active");
            document.getElementById(targetTab).classList.add("active");
        });
    });

    function resetTabs() {
        tabButtons.forEach(btn => btn.classList.remove("active"));
        tabPanes.forEach(pane => pane.classList.remove("active"));

        // Default back to Overview (first tab)
        tabButtons[0].classList.add("active");
        tabPanes[0].classList.add("active");
    }

    /* ==========================================================================
       SUBMISSION & DIAGNOSIS FLOW
       ========================================================================== */
    btnPredict.addEventListener("click", async () => {
        let body = {};
        let endpoint = "";

        if (activeMode === "checklist") {
            if (selectedSymptoms.size === 0) return;
            body = { symptoms: Array.from(selectedSymptoms) };
            endpoint = "/api/predict";
        } else {
            const text = nlpInput.value.trim();
            if (text.length < 10) return;
            body = { description: text };
            endpoint = "/api/predict_nlp";
        }

        // Update view states
        reportCard.classList.remove("disabled-state");
        welcomeView.classList.add("hidden");
        loaderView.classList.remove("hidden");
        reportView.classList.add("hidden");
        btnPredict.disabled = true;

        try {
            const response = await fetch(endpoint, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(body)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || "An error occurred during diagnosis.");
            }

            // Successfully received diagnosis
            renderDiagnostics(result);
        } catch (error) {
            console.error("Prediction Error:", error);
            showErrorState(error.message);
        } finally {
            btnPredict.disabled = false;
            updatePredictButtonState();
        }
    });

    // Differential List Selector Element
    const differentialList = document.getElementById("differential-list");

    function renderDiagnostics(data) {
        // Hide loader, show report content
        loaderView.classList.add("hidden");
        reportView.classList.remove("hidden");
        
        const diffs = data.differential_diagnoses || [];
        if (diffs.length === 0) {
            showErrorState("No diagnostic categories returned from backend classifier.");
            return;
        }

        // Render the Differential Diagnosis items
        differentialList.innerHTML = "";
        
        diffs.forEach((diff, idx) => {
            const item = document.createElement("div");
            item.className = "diff-item";
            if (idx === 0) item.classList.add("active");

            item.innerHTML = `
                <div class="diff-info">
                    <span class="diff-name">${diff.disease}</span>
                    <span class="diff-percent">${diff.probability}% Match</span>
                </div>
                <div class="progress-track">
                    <div class="progress-fill" style="width: 0%"></div>
                </div>
            `;

            // Trigger progress bar load transition in next frame
            setTimeout(() => {
                const fill = item.querySelector(".progress-fill");
                if (fill) fill.style.width = `${diff.probability}%`;
            }, 50);

            // Add click listener to swap detail views instantly
            item.addEventListener("click", () => {
                // Remove active classes
                const allItems = differentialList.querySelectorAll(".diff-item");
                Array.from(allItems).forEach(i => i.classList.remove("active"));
                
                // Set active class
                item.classList.add("active");
                
                // Swap view details
                showReportDetails(diff.disease, diff.details);
            });

            differentialList.appendChild(item);
        });

        // Initialize display with the primary diagnosis (index 0)
        showReportDetails(diffs[0].disease, diffs[0].details);

        // Store full result for download handlers
        storeReportData(data);

        // ── Trigger Live Health Intelligence fetch ──────────────────────────
        if (typeof window.fetchHealthIntel === "function") {
            window.fetchHealthIntel(diffs[0].disease);
        }
    }

    function showReportDetails(diseaseName, details) {
        resetTabs();

        // 1. Diagnosis Banner Title
        predictedDiseaseElem.textContent = diseaseName;

        // 2. Overview Tab
        diseaseDescElem.textContent = details.description || "No description available.";

        // 3. Precautions Tab
        precautionsList.innerHTML = "";
        if (details.precautions && details.precautions.length > 0) {
            details.precautions.forEach(p => {
                const li = document.createElement("li");
                li.textContent = p;
                precautionsList.appendChild(li);
            });
        } else {
            precautionsList.innerHTML = "<li>No specific precaution guidelines found.</li>";
        }

        // 4. Medications Tab
        medicationsList.innerHTML = "";
        if (details.medications && details.medications.length > 0) {
            details.medications.forEach(m => {
                const li = document.createElement("li");
                li.textContent = m;
                medicationsList.appendChild(li);
            });
        } else {
            medicationsList.innerHTML = "<li>No specialized medication listed.</li>";
        }

        // 5. Diets Tab
        dietList.innerHTML = "";
        if (details.diets && details.diets.length > 0) {
            details.diets.forEach(d => {
                const li = document.createElement("li");
                li.textContent = d;
                dietList.appendChild(li);
            });
        } else {
            dietList.innerHTML = "<li>No specific dietary guidelines listed.</li>";
        }

        // 6. Recovery Tips Tab
        workoutList.innerHTML = "";
        if (details.workouts && details.workouts.length > 0) {
            details.workouts.forEach(w => {
                const li = document.createElement("li");
                li.textContent = w;
                workoutList.appendChild(li);
            });
        } else {
            workoutList.innerHTML = "<li>No specific workout or physical recovery tips listed.</li>";
        }
    }

    function showErrorState(message) {
        loaderView.classList.add("hidden");
        reportView.classList.add("hidden");
        welcomeView.classList.remove("hidden");
        reportCard.classList.add("disabled-state");
        
        alert(`⚠️ Diagnosis Error:\n${message}`);
    }

    // Download Button Elements
    const btnDownloadPdf = document.getElementById("btn-download-pdf");
    const btnDownloadTxt = document.getElementById("btn-download-txt");

    // Store last rendered report data for download
    let lastReportData = null;

    /* ==========================================================================
       RESET STATE
       ========================================================================== */
    btnReset.addEventListener("click", () => {
        // Clear search & tags
        symptomInput.value = "";
        selectedSymptoms.clear();
        renderTags();
        updatePredictButtonState();
        closeDropdown();

        // Clear NLP textarea
        nlpInput.value = "";

        // Clear output views
        reportView.classList.add("hidden");
        loaderView.classList.add("hidden");
        welcomeView.classList.remove("hidden");
        reportCard.classList.add("disabled-state");
        differentialList.innerHTML = "";

        // Clear report data
        lastReportData = null;
    });

    /* ==========================================================================
       REPORT DATA STORAGE (called after renderDiagnostics)
       ========================================================================== */
    function storeReportData(data) {
        lastReportData = data;
    }

    /* ==========================================================================
       DOWNLOAD HANDLERS
       ========================================================================== */

    // --- Text Download ---
    btnDownloadTxt.addEventListener("click", () => {
        if (!lastReportData) return;
        const diffs = lastReportData.differential_diagnoses || [];
        const ts = new Date().toLocaleString();
        let lines = [];

        lines.push("╔══════════════════════════════════════════════════════╗");
        lines.push("║     PMRS - AI Medical Diagnostic Report              ║");
        lines.push("║     Developed by Vipin Kumar Singh                   ║");
        lines.push("╚══════════════════════════════════════════════════════╝");
        lines.push(`Generated: ${ts}`);
        lines.push("DISCLAIMER: For educational/demo purposes only. Consult a doctor.");
        lines.push("━".repeat(56));
        lines.push("");

        diffs.forEach((diff, idx) => {
            lines.push(`[${idx + 1}] ${diff.disease.toUpperCase()} — ${diff.probability}% Match`);
            lines.push("─".repeat(56));

            const d = diff.details;
            lines.push("OVERVIEW:");
            lines.push(`  ${d.description || "N/A"}`);
            lines.push("");

            lines.push("PRECAUTIONS:");
            if (d.precautions && d.precautions.length > 0) {
                d.precautions.forEach(p => lines.push(`  • ${p}`));
            } else { lines.push("  • No precautions listed."); }
            lines.push("");

            lines.push("MEDICATIONS:");
            if (d.medications && d.medications.length > 0) {
                d.medications.forEach(m => lines.push(`  • ${m}`));
            } else { lines.push("  • No medications listed."); }
            lines.push("");

            lines.push("DIETARY RECOMMENDATIONS:");
            if (d.diets && d.diets.length > 0) {
                d.diets.forEach(di => lines.push(`  • ${di}`));
            } else { lines.push("  • No dietary guidelines listed."); }
            lines.push("");

            lines.push("RECOVERY & WORKOUT TIPS:");
            if (d.workouts && d.workouts.length > 0) {
                d.workouts.forEach(w => lines.push(`  • ${w}`));
            } else { lines.push("  • No recovery tips listed."); }
            lines.push("");
            lines.push("━".repeat(56));
            lines.push("");
        });

        const blob = new Blob([lines.join("\n")], { type: "text/plain;charset=utf-8" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        const safeName = (diffs[0]?.disease || "Report").replace(/\s+/g, "_");
        a.download = `PMRS_Report_${safeName}.txt`;
        a.click();
        URL.revokeObjectURL(url);
    });

    // --- PDF Download (Print-to-PDF via hidden styled window) ---
    btnDownloadPdf.addEventListener("click", () => {
        if (!lastReportData) return;
        const diffs = lastReportData.differential_diagnoses || [];
        const ts = new Date().toLocaleString();

        const sections = diffs.map((diff, idx) => {
            const d = diff.details;
            const prec = d.precautions?.length ? d.precautions.map(p => `<li>${p}</li>`).join("") : "<li>No precautions listed.</li>";
            const meds = d.medications?.length ? d.medications.map(m => `<li>${m}</li>`).join("") : "<li>No medications listed.</li>";
            const diet = d.diets?.length ? d.diets.map(di => `<li>${di}</li>`).join("") : "<li>No dietary guidelines listed.</li>";
            const work = d.workouts?.length ? d.workouts.map(w => `<li>${w}</li>`).join("") : "<li>No recovery tips listed.</li>";

            const barWidth = Math.min(diff.probability, 100);
            return `
            <div class="report-block ${idx === 0 ? 'primary' : ''}">
                <div class="block-header">
                    <div>
                        <span class="rank">#${idx + 1} ${idx === 0 ? "Primary Diagnosis" : "Differential"}</span>
                        <h2>${diff.disease}</h2>
                    </div>
                    <div class="prob-box">${diff.probability}%<span>Match</span></div>
                </div>
                <div class="prob-bar"><div style="width:${barWidth}%"></div></div>
                <div class="section"><h3>Overview</h3><p>${d.description || "N/A"}</p></div>
                <div class="two-col">
                    <div class="section"><h3>Precautions</h3><ul>${prec}</ul></div>
                    <div class="section"><h3>Medications</h3><ul>${meds}</ul></div>
                </div>
                <div class="two-col">
                    <div class="section"><h3>Diet</h3><ul>${diet}</ul></div>
                    <div class="section"><h3>Recovery Tips</h3><ul>${work}</ul></div>
                </div>
            </div>`;
        }).join("");

        const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>PMRS Diagnostic Report</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family:'Plus Jakarta Sans',sans-serif; background:#f8f9fc; color:#1a1c30; padding:2rem; font-size:13px; }
  .cover { background:linear-gradient(135deg,#3730a3 0%,#1d4ed8 100%); color:#fff; border-radius:14px; padding:2.5rem 2rem; margin-bottom:2rem; display:flex; justify-content:space-between; align-items:flex-end; }
  .cover h1 { font-size:2rem; font-weight:700; letter-spacing:-0.5px; }
  .cover p { font-size:0.85rem; opacity:0.8; margin-top:0.3rem; }
  .cover .meta { text-align:right; font-size:0.8rem; opacity:0.85; }
  .disclaimer { background:#fef3c7; border:1px solid #fcd34d; border-radius:8px; padding:0.75rem 1rem; font-size:0.78rem; color:#92400e; margin-bottom:1.5rem; }
  .report-block { background:#fff; border-radius:12px; padding:1.75rem; margin-bottom:1.5rem; box-shadow:0 2px 12px rgba(0,0,0,0.07); border-left:5px solid #c7d2fe; }
  .report-block.primary { border-left-color:#4f46e5; }
  .block-header { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:1rem; }
  .rank { font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:1px; color:#6366f1; }
  h2 { font-size:1.4rem; font-weight:700; color:#111827; margin-top:0.2rem; }
  .prob-box { background:#eef2ff; border-radius:10px; padding:0.5rem 0.9rem; text-align:center; font-size:1.5rem; font-weight:700; color:#4f46e5; min-width:70px; }
  .prob-box span { display:block; font-size:0.7rem; color:#6b7280; font-weight:500; }
  .prob-bar { height:7px; background:#e5e7eb; border-radius:10px; overflow:hidden; margin-bottom:1.25rem; }
  .prob-bar div { height:100%; background:linear-gradient(90deg,#4f46e5,#14b8a6); border-radius:10px; }
  .section { margin-bottom:1rem; }
  h3 { font-size:0.8rem; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; color:#6b7280; border-left:3px solid #14b8a6; padding-left:0.5rem; margin-bottom:0.6rem; }
  p { font-size:0.9rem; color:#374151; line-height:1.6; }
  ul { list-style:none; display:flex; flex-direction:column; gap:0.3rem; }
  li { font-size:0.88rem; color:#374151; padding:0.45rem 0.75rem; background:#f9fafb; border-radius:6px; border-left:3px solid #e5e7eb; }
  .two-col { display:grid; grid-template-columns:1fr 1fr; gap:1rem; }
  .footer { text-align:center; margin-top:2rem; font-size:0.75rem; color:#9ca3af; }
  @media print { body{padding:0.5rem} .report-block{break-inside:avoid} }
</style>
</head>
<body>
  <div class="cover">
    <div>
      <h1>PMRS Diagnostic Report</h1>
      <p>AI Medical Diagnostics &amp; Recommendations</p>
    </div>
    <div class="meta">
      <div>Generated: ${ts}</div>
      <div style="margin-top:0.3rem">Developer: <strong>Vipin Kumar Singh</strong></div>
    </div>
  </div>
  <div class="disclaimer">⚠️ <strong>Disclaimer:</strong> This report is generated by a machine learning classifier for educational/demo purposes only. Do not use for actual medical diagnoses. Always consult a qualified healthcare professional.</div>
  ${sections}
  <div class="footer">© 2026 PMRS — Designed and Developed by Vipin Kumar Singh</div>
</body>
</html>`;

        const win = window.open("", "_blank", "width=900,height=700");
        win.document.write(html);
        win.document.close();
        win.focus();
        setTimeout(() => { win.print(); }, 600);
    });

    // ── Live Health Intelligence Panel (BigQuery) ──────────────────────────

    const intelPanel   = document.getElementById("intel-panel");
    const intelToggle  = document.getElementById("intel-toggle");
    const intelBody    = document.getElementById("intel-body");
    const intelLoader  = document.getElementById("intel-loader");
    const intelUnconf  = document.getElementById("intel-unconfigured");
    const intelErr     = document.getElementById("intel-error");
    const intelData    = document.getElementById("intel-data");

    let intelCollapsed = false;

    /** Toggle expand/collapse of the intel panel body */
    function setupIntelToggle() {
        if (!intelToggle || !intelBody) return;
        intelToggle.addEventListener("click", (e) => {
            e.stopPropagation();
            intelCollapsed = !intelCollapsed;
            intelBody.classList.toggle("collapsed", intelCollapsed);
            intelToggle.classList.toggle("collapsed", intelCollapsed);
        });
        // Also toggle on header click
        const header = intelToggle.closest(".intel-header");
        if (header) {
            header.addEventListener("click", (e) => {
                if (e.target === intelToggle || intelToggle.contains(e.target)) return;
                intelCollapsed = !intelCollapsed;
                intelBody.classList.toggle("collapsed", intelCollapsed);
                intelToggle.classList.toggle("collapsed", intelCollapsed);
            });
        }
    }

    /** Format large numbers with commas */
    function fmtNum(n) {
        if (n == null) return "N/A";
        return Number(n).toLocaleString("en-IN");
    }

    /** Show one state, hide others inside intel-body */
    function showIntelState(state) {
        intelLoader.classList.add("hidden");
        intelUnconf.classList.add("hidden");
        intelErr.classList.add("hidden");
        intelData.classList.add("hidden");
        if (state === "loader") intelLoader.classList.remove("hidden");
        else if (state === "unconfigured") intelUnconf.classList.remove("hidden");
        else if (state === "error") intelErr.classList.remove("hidden");
        else if (state === "data") intelData.classList.remove("hidden");
    }

    /** Render the BigQuery data into the panel */
    function renderIntelData(payload) {
        const covid       = payload.covid_data;
        const wb          = payload.world_bank_data;
        const isDemo      = payload.demo === true;
        const diseaseName = (payload.disease || "Disease").replace(/^\w/, c => c.toUpperCase());

        // ── Update panel badge: Reference Data vs Live ──
        const badge = document.querySelector(".intel-badge");
        if (badge) {
            if (isDemo) {
                badge.textContent       = "REFERENCE DATA";
                badge.style.color       = "hsl(38,80%,65%)";
                badge.style.borderColor = "rgba(251,191,36,0.3)";
                badge.style.background  = "rgba(251,191,36,0.08)";
            } else {
                badge.textContent       = "🟢 LIVE · GOOGLE BIGQUERY";
                badge.style.color       = "";
                badge.style.borderColor = "";
                badge.style.background  = "";
            }
        }

        // ── Dynamic section labels based on disease ──
        const burdenText = document.getElementById("intel-burden-text");
        if (burdenText) {
            const src = covid?.source || "";
            burdenText.textContent = `Global ${diseaseName} Burden — ${src.replace(" (Demo Data)", "")}`;
        }
        const countriesText = document.getElementById("intel-countries-text");
        if (countriesText) {
            countriesText.textContent = `Top 5 Countries Affected by ${diseaseName}`;
        }

        // ── Stat Cards ──
        const statsRow = document.getElementById("intel-stats-row");
        if (statsRow && covid) {
            const totalLabel = isDemo ? "Global Prevalence (Est.)" : "Global Cumulative Cases";
            const newLabel   = isDemo ? "Annual New Cases (Est.)"  : "New Cases (Last 30 Days)";
            statsRow.innerHTML = `
                <div class="intel-stat-card">
                    <span class="stat-value">${fmtNum(covid.global_total)}</span>
                    <span class="stat-label">${totalLabel}</span>
                </div>
                <div class="intel-stat-card">
                    <span class="stat-value">${fmtNum(covid.global_new_30d)}</span>
                    <span class="stat-label">${newLabel}</span>
                </div>
                <div class="intel-stat-card">
                    <span class="stat-value">${covid.top_countries ? covid.top_countries.length : 0}</span>
                    <span class="stat-label">Top Countries Tracked</span>
                </div>
            `;
        }

        // ── Top Countries ──
        const countriesEl = document.getElementById("intel-countries");
        if (countriesEl && covid && covid.top_countries) {
            countriesEl.innerHTML = covid.top_countries.map((c, i) => `
                <div class="intel-country-row">
                    <span class="country-rank">#${i + 1}</span>
                    <span class="country-name">${c.country || "Unknown"}</span>
                    <span class="country-total">${fmtNum(c.total)} cases</span>
                </div>
            `).join("");
        }

        // ── World Bank Indicators ──
        const indicatorsEl = document.getElementById("intel-indicators");
        if (indicatorsEl && wb && wb.indicators) {
            if (wb.indicators.length === 0) {
                indicatorsEl.innerHTML = `<p style="font-size:0.8rem;color:var(--text-muted)">No health indicator data available.</p>`;
            } else {
                indicatorsEl.innerHTML = wb.indicators.map(ind => `
                    <div class="intel-indicator-row">
                        <span class="indicator-name">${ind.indicator}</span>
                        <span class="indicator-value">${ind.value != null ? ind.value : "N/A"}</span>
                        <span class="indicator-year">(${ind.year})</span>
                    </div>
                `).join("");
            }
        }

        // ── Note + Source attribution ──
        const sourceEl = document.getElementById("intel-source-label");
        if (sourceEl) {
            const note    = covid?.note ? `<em>${covid.note}</em>` : "";
            const srcTag  = isDemo
                ? "Reference data — WHO / IDF / World Bank"
                : `Live data — ${[covid?.source, wb?.source].filter(Boolean).join(" · ")}`;
            sourceEl.innerHTML = [note, srcTag].filter(Boolean).join(" &nbsp;·&nbsp; ");
        }

        showIntelState("data");
    }

    /** Fetch live intel for a given disease name */
    async function fetchHealthIntel(diseaseName) {
        if (!intelPanel) return;
        intelPanel.style.display = "block";

        // Reset & show loader
        showIntelState("loader");

        try {
            const encoded = encodeURIComponent(diseaseName.toLowerCase());
            const res = await fetch(`/api/health_intelligence/${encoded}`);
            const json = await res.json();

            if (json.status === "unconfigured") {
                document.getElementById("intel-notice-msg").textContent = json.message || "GCP credentials not configured.";
                showIntelState("unconfigured");
                return;
            }

            if (json.status === "error") {
                document.getElementById("intel-error-msg").textContent = json.message || "Unknown error occurred.";
                showIntelState("error");
                return;
            }

            if (json.status === "ok") {
                renderIntelData(json);
            }
        } catch (err) {
            document.getElementById("intel-error-msg").textContent = `Network error: ${err.message}`;
            showIntelState("error");
        }
    }

    // Expose globally so renderDiagnostics can call it directly
    window.fetchHealthIntel = fetchHealthIntel;

    // Initially hide the intel panel — shown only after a diagnosis
    if (intelPanel) intelPanel.style.display = "none";

    setupIntelToggle();

});
