/**
 * AegisOps AI - Main Dashboard Application Controller
 */

document.addEventListener("DOMContentLoaded", () => {
  // Global State
  let currentScenario = "healthcare_coldchain";
  let userRole = "operator";
  let isDryRun = true;
  let eventSource = null;

  // Initialize UI Components
  AgentGraph.init("agentGraphCanvas");
  RedTeamConsole.init("redteamPresetsList", "redteamPromptInput");
  AuditViewer.init();
  PerformanceCharts.renderLatency("latencyCanvas", 28.4, 42.1, 48.0);
  PerformanceCharts.renderCache("cacheCanvas", 85, 12450);

  // Bind Event Listeners
  setupTabs();
  setupScenarioSelector();
  setupRoleSelector();
  setupDryRunToggle();
  setupGeminiModal();
  setupActionButtons();
  setupRedTeamExecution();
  setupBigQueryControls();

  // Start Real-Time Telemetry Stream
  startTelemetryStream();

  // Periodically refresh BigQuery table and efficiency stats
  loadBigQueryTable();
  setInterval(loadEfficiencyMetrics, 5000);

  /* ----------------- Tab Navigation ----------------- */
  function setupTabs() {
    const tabButtons = document.querySelectorAll(".tab-btn");
    tabButtons.forEach(btn => {
      btn.addEventListener("click", () => {
        tabButtons.forEach(b => b.classList.remove("active"));
        document.querySelectorAll(".tab-pane").forEach(pane => pane.classList.remove("active"));

        btn.classList.add("active");
        const targetId = btn.getAttribute("data-tab");
        const targetPane = document.getElementById(targetId);
        if (targetPane) targetPane.classList.add("active");

        // Re-render charts or ledger if tab clicked
        if (targetId === "tabEfficiency") {
          loadEfficiencyMetrics();
        } else if (targetId === "tabAudit") {
          AuditViewer.refresh();
        }
      });
    });
  }

  /* ----------------- Scenario & Role Selectors ----------------- */
  function setupScenarioSelector() {
    const select = document.getElementById("scenarioSelect");
    if (!select) return;

    select.addEventListener("change", async (e) => {
      currentScenario = e.target.value;
      try {
        await fetch("/api/telemetry/scenario", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ scenario: currentScenario })
        });
        showToast(`Switched scenario to: ${currentScenario}`, "info");
        updateScenarioLabels(currentScenario);
      } catch (err) {
        showToast("Failed to switch scenario", "danger");
      }
    });
  }

  function updateScenarioLabels(scenario) {
    const label = document.getElementById("kpiMetricLabel");
    if (!label) return;

    if (scenario === "healthcare_coldchain") {
      label.innerText = "Storage Temp (Core)";
    } else if (scenario === "smart_grid") {
      label.innerText = "Grid Frequency (Hz)";
    } else {
      label.innerText = "API Throughput (req/s)";
    }
  }

  function setupRoleSelector() {
    const select = document.getElementById("roleSelect");
    if (!select) return;

    select.addEventListener("change", (e) => {
      userRole = e.target.value;
      showToast(`Active Role updated to: ${userRole.toUpperCase()}`, "info");
    });
  }

  function setupDryRunToggle() {
    const btn = document.getElementById("dryRunToggleBtn");
    const label = document.getElementById("dryRunToggleLabel");
    if (!btn || !label) return;

    btn.addEventListener("click", () => {
      isDryRun = !isDryRun;
      if (isDryRun) {
        btn.classList.add("active");
        label.innerText = "Safe Sandbox (Dry-Run)";
        showToast("Dry-Run Sandbox Mode: Actuators simulate safely without hardware risk", "info");
      } else {
        btn.classList.remove("active");
        label.innerText = "Live Actuation Mode";
        showToast("Live Mode: Actuators will directly command target infrastructure", "warning");
      }
    });
  }

  /* ----------------- Action Strip Controls ----------------- */
  function setupActionButtons() {
    const anomalyBtn = document.getElementById("triggerAnomalyBtn");
    const clearBtn = document.getElementById("clearAnomalyBtn");
    const triggerBtn = document.getElementById("triggerResolutionBtn");

    if (anomalyBtn) {
      anomalyBtn.addEventListener("click", async () => {
        let type = "THERMAL_FAILURE";
        if (currentScenario === "smart_grid") type = "FREQUENCY_DROP";
        if (currentScenario === "cloud_infra") type = "DDOS_BURST";

        try {
          await fetch("/api/telemetry/anomaly", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ anomaly_type: type })
          });
          showToast(`Critical anomaly injected: ${type}! Telemetry spiking.`, "warning");
        } catch (err) {
          showToast("Failed to inject anomaly", "danger");
        }
      });
    }

    if (clearBtn) {
      clearBtn.addEventListener("click", async () => {
        try {
          await fetch("/api/telemetry/resolve", { method: "POST" });
          showToast("Anomaly resolved. Telemetry returning to nominal envelope.", "success");
        } catch (err) {
          showToast("Failed to restore baseline", "danger");
        }
      });
    }

    if (triggerBtn) {
      triggerBtn.addEventListener("click", executeMultiAgentResolution);
    }
  }

  /* ----------------- Multi-Agent Resolution Execution ----------------- */
  async function executeMultiAgentResolution() {
    const promptInput = document.getElementById("operatorPromptInput");
    const prompt = promptInput ? promptInput.value.trim() : "";
    const activeBadge = document.getElementById("activeAgentBadge");

    if (activeBadge) {
      activeBadge.innerText = "Hivemind Active...";
      activeBadge.className = "badge badge-warning";
    }

    showToast("Dispatching Multi-Agent Hivemind across Zero-Trust Guard, Gemini Reasoner & Verifier...", "info");

    try {
      const res = await fetch("/api/agent/trigger", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: prompt,
          scenario: currentScenario,
          role: userRole,
          dry_run: isDryRun
        })
      });

      const data = await res.json();
      handleAgentResolutionResponse(data);
    } catch (err) {
      showToast(`Agent dispatch error: ${err.message}`, "danger");
      if (activeBadge) activeBadge.innerText = "Error";
    }
  }

  function handleAgentResolutionResponse(data) {
    const activeBadge = document.getElementById("activeAgentBadge");
    const feedContent = document.getElementById("agentFeedContent");
    const placeholder = document.getElementById("feedPlaceholder");

    if (placeholder) placeholder.style.display = "none";

    // Update Agent Graph
    if (data.status === "SECURITY_BLOCK") {
      AgentGraph.update("agentGraphCanvas", false);
      if (activeBadge) {
        activeBadge.innerText = "Attack Blocked";
        activeBadge.className = "badge badge-critical";
      }
      showToast(`Adversarial threat intercepted! Threat score: ${data.guard_assessment.threat_score}`, "danger");
      renderSecurityBlockBubble(feedContent, data);
    } else {
      AgentGraph.update("agentGraphCanvas", true);
      if (activeBadge) {
        activeBadge.innerText = "Consensus Reached";
        activeBadge.className = "badge badge-nominal";
      }
      showToast(`Consensus established in ${data.latency_ms}ms. Verifier: ${data.verification.verdict}`, "success");
      renderConsensusBubble(feedContent, data);
    }

    // Refresh Audit Ledger & BigQuery Table
    AuditViewer.refresh();
    loadBigQueryTable();
    loadEfficiencyMetrics();
  }

  function renderSecurityBlockBubble(container, data) {
    const bubble = document.createElement("div");
    bubble.className = "feed-thought-bubble";
    bubble.style.borderLeftColor = "var(--red-critical)";

    bubble.innerHTML = `
      <div class="bubble-header">
        <span class="bubble-author" style="color: var(--red-critical);">🛡️ Zero-Trust Guard Agent (Shield Intercept)</span>
        <span class="bubble-timestamp">${new Date().toLocaleTimeString()}</span>
      </div>
      <div class="bubble-text">
        <strong>Security Alert:</strong> Adversarial injection quarantined before reaching Gemini reasoning models.
      </div>
      <div class="bubble-details-grid">
        <div><span class="detail-label">Threat Score:</span> <span class="detail-value" style="color: var(--red-critical);">${data.guard_assessment.threat_score}</span></div>
        <div><span class="detail-label">Action:</span> <span class="detail-value">${data.guard_assessment.action}</span></div>
        <div><span class="detail-label">Incident ID:</span> <span class="detail-value">${data.incident_id}</span></div>
        <div><span class="detail-label">SHA-256 Block:</span> <span class="detail-value">${data.audit_block.block_hash.slice(0, 16)}...</span></div>
      </div>
    `;

    container.prepend(bubble);
  }

  function renderConsensusBubble(container, data) {
    const bubble = document.createElement("div");
    bubble.className = "feed-thought-bubble";

    const autoStepsHtml = (data.remediation.autonomous_safe_steps || []).map(s => `
      <div class="step-item auto">
        <span>⚡ <strong>Step ${s.step}:</strong> ${s.action}</span>
        <span class="badge badge-nominal">Auto Actuated (${s.risk})</span>
      </div>
    `).join("");

    const hitlStepsHtml = (data.remediation.human_in_the_loop_steps || []).map(s => `
      <div class="step-item hitl">
        <span>⚠️ <strong>Step ${s.step}:</strong> ${s.action}</span>
        <span class="badge badge-warning">HITL Required (${s.risk})</span>
      </div>
    `).join("");

    bubble.innerHTML = `
      <div class="bubble-header">
        <span class="bubble-author">🧠 Causal Diagnosis & Consensus Plan [${data.domain}]</span>
        <span class="bubble-timestamp">${new Date().toLocaleTimeString()} (${data.latency_ms} ms)</span>
      </div>
      <div class="bubble-text">
        <strong>Diagnosis:</strong> ${data.diagnosis.diagnosis}<br>
        <strong>Root Cause:</strong> ${data.diagnosis.root_cause}<br>
        <strong>Blast Radius:</strong> ${data.diagnosis.blast_radius}
      </div>
      <div class="bubble-details-grid">
        <div><span class="detail-label">Confidence:</span> <span class="detail-value">${Math.round(data.diagnosis.confidence_score * 100)}%</span></div>
        <div><span class="detail-label">Verifier Verdict:</span> <span class="detail-value" style="color: var(--green-nominal);">${data.verification.verdict}</span></div>
        <div><span class="detail-label">Regulatory Standards:</span> <span class="detail-value">${data.verification.applicable_standards.join(", ")}</span></div>
        <div><span class="detail-label">Tokens Saved (Cache & Compression):</span> <span class="detail-value" style="color: var(--cyan-primary);">+${data.tokens_saved_estimate}</span></div>
      </div>
      <div class="steps-list">
        ${autoStepsHtml}
        ${hitlStepsHtml}
      </div>
    `;

    container.prepend(bubble);
  }

  /* ----------------- Real-Time SSE Telemetry ----------------- */
  function startTelemetryStream() {
    if (!!window.EventSource) {
      eventSource = new EventSource("/api/telemetry/stream");

      eventSource.onmessage = function (e) {
        try {
          const tick = JSON.parse(e.data);
          updateTelemetryUI(tick);
        } catch (err) {
          console.error("Error parsing telemetry tick:", err);
        }
      };

      eventSource.onerror = function () {
        // Fallback polling if SSE drops
        eventSource.close();
        setInterval(async () => {
          try {
            const res = await fetch("/api/telemetry/tick");
            const tick = await res.json();
            updateTelemetryUI(tick);
          } catch (e) {}
        }, 3000);
      };
    }
  }

  function updateTelemetryUI(tick) {
    const seq = document.getElementById("streamSequence");
    if (seq) seq.innerText = `Tick #${tick.sequence}`;

    const valEl = document.getElementById("kpiMetricValue");
    const badgeEl = document.getElementById("kpiMetricBadge");
    const subtextEl = document.getElementById("kpiMetricSubtext");
    const threatVal = document.getElementById("kpiThreatValue");
    const threatBar = document.getElementById("threatProgressBar");

    if (tick.scenario === "healthcare_coldchain") {
      const temp = tick.metrics.freezer_temp_c;
      if (valEl) valEl.innerText = `${temp}°C`;
      if (subtextEl) subtextEl.innerText = `Compressor: ${tick.metrics.compressor_pressure_psi} PSI | Bat: ${tick.metrics.backup_battery_pct}%`;
    } else if (tick.scenario === "smart_grid") {
      if (valEl) valEl.innerText = `${tick.metrics.grid_frequency_hz} Hz`;
      if (subtextEl) subtextEl.innerText = `Inverter: ${tick.metrics.inverter_efficiency_pct}% | Oil: ${tick.metrics.transformer_temp_c}°C`;
    } else {
      if (valEl) valEl.innerText = `${tick.metrics.requests_per_sec.toLocaleString()}`;
      if (subtextEl) subtextEl.innerText = `P95: ${tick.metrics.p95_latency_ms}ms | Errors: ${tick.metrics.error_rate_pct}%`;
    }

    if (badgeEl) {
      badgeEl.innerText = tick.status;
      badgeEl.className = `kpi-badge badge-${tick.status.toLowerCase()}`;
    }

    if (threatVal && tick.metrics.risk_index !== undefined) {
      threatVal.innerText = tick.metrics.risk_index;
      if (threatBar) {
        threatBar.style.width = `${Math.min(tick.metrics.risk_index * 100, 100)}%`;
        threatBar.className = `progress-bar-fill ${tick.metrics.risk_index > 0.6 ? "fill-danger" : "fill-green"}`;
      }
    }
  }

  /* ----------------- Efficiency & BigQuery ----------------- */
  async function loadEfficiencyMetrics() {
    try {
      const res = await fetch("/api/efficiency/stats");
      const data = await res.json();

      const tokensSavedEl = document.getElementById("kpiTokensSaved");
      const latencyValEl = document.getElementById("kpiLatencyValue");
      const cacheBadge = document.getElementById("kpiCacheBadge");

      const stats = data.telemetry;
      const cache = data.cache;

      if (tokensSavedEl) tokensSavedEl.innerText = stats.tokens.tokens_saved_by_cache.toLocaleString();
      if (latencyValEl) latencyValEl.innerText = `${stats.latency.p95_ms} ms`;
      if (cacheBadge) cacheBadge.innerText = `Cache: ${cache.hit_ratio_percent}% Hit`;

      PerformanceCharts.renderLatency("latencyCanvas", stats.latency.p50_ms, stats.latency.p95_ms, stats.latency.p99_ms);
      PerformanceCharts.renderCache("cacheCanvas", cache.hit_ratio_percent || 75, stats.tokens.tokens_saved_by_cache);
    } catch (err) {
      console.error("Efficiency stats fetch failed:", err);
    }
  }

  async function loadBigQueryTable() {
    try {
      const res = await fetch("/api/bigquery/status");
      const bq = await res.json();

      const countEl = document.getElementById("kpiStreamedCount");
      if (countEl) countEl.innerText = `Streaming Rows: ${bq.total_streamed_rows}`;

      // Also render some simulated BigQuery stream entries
      const tableBody = document.getElementById("bigqueryTableBody");
      if (!tableBody) return;

      const auditRes = await fetch("/api/security/audit/chain?limit=6");
      const auditData = await auditRes.json();

      tableBody.innerHTML = "";
      auditData.blocks.slice(-6).reverse().forEach(b => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td style="color: var(--cyan-primary);">EVT-${b.index}</td>
          <td>${b.iso_time}</td>
          <td>${b.metadata.domain || "Healthcare"}</td>
          <td>${b.agent_name}</td>
          <td><span class="badge badge-info">${b.action_type}</span></td>
          <td>28.4ms</td>
          <td>${b.tokens_used}</td>
          <td style="font-size: 11px;">${b.block_hash.slice(0, 18)}...</td>
          <td><span class="badge badge-nominal">GCP-INGEST-OK</span></td>
        `;
        tableBody.appendChild(tr);
      });
    } catch (err) {
      console.error("BigQuery table load failed:", err);
    }
  }

  function setupBigQueryControls() {
    const btn = document.getElementById("flushBigQueryBtn");
    if (!btn) return;

    btn.addEventListener("click", async () => {
      try {
        const res = await fetch("/api/bigquery/flush", { method: "POST" });
        const data = await res.json();
        showToast(`Flushed buffer to BigQuery! Destination: ${data.destination}`, "success");
        loadBigQueryTable();
      } catch (err) {
        showToast("BigQuery flush failed", "danger");
      }
    });
  }

  /* ----------------- Red-Team Console ----------------- */
  function setupRedTeamExecution() {
    const btn = document.getElementById("executeRedteamBtn");
    const input = document.getElementById("redteamPromptInput");

    if (btn && input) {
      btn.addEventListener("click", () => {
        const prompt = input.value.trim();
        if (!prompt) {
          showToast("Please enter or select an adversarial probe string first", "warning");
          return;
        }
        RedTeamConsole.execute(prompt, "redteamResultsContainer");
      });
    }
  }

  /* ----------------- Google Gemini Modal ----------------- */
  function setupGeminiModal() {
    const openBtn = document.getElementById("geminiConfigBtn");
    const modal = document.getElementById("geminiModal");
    const closeBtn = document.getElementById("closeGeminiModalBtn");
    const cancelBtn = document.getElementById("cancelGeminiModalBtn");
    const saveBtn = document.getElementById("saveGeminiKeyBtn");
    const input = document.getElementById("geminiApiKeyInput");

    if (openBtn && modal) {
      openBtn.addEventListener("click", () => modal.classList.add("open"));
    }

    const closeModal = () => modal.classList.remove("open");
    if (closeBtn) closeBtn.addEventListener("click", closeModal);
    if (cancelBtn) cancelBtn.addEventListener("click", closeModal);

    if (saveBtn && input) {
      saveBtn.addEventListener("click", async () => {
        const key = input.value.trim();
        try {
          await fetch("/api/config/gemini-key", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ api_key: key })
          });
          showToast(key ? "Google Gemini API Key configured and active!" : "Switched to Local Deterministic Reasoning Engine", "success");
          closeModal();
        } catch (err) {
          showToast("Failed to save Gemini key", "danger");
        }
      });
    }
  }

  /* ----------------- Toast Notifications ----------------- */
  function showToast(message, type = "info") {
    const container = document.getElementById("toastContainer");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.innerHTML = `
      <div class="toast-content" style="font-size: 13px; font-weight: 500;">${message}</div>
    `;

    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transition = "opacity 0.3s ease";
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }
});
