/**
 * Agent Graph Visualization Component
 * Renders the multi-agent hivemind topology and live consensus state.
 */

const AgentGraph = (function () {
  const defaultNodes = [
    { id: "guard", label: "Zero-Trust Guard Agent", role: "Shield & PII Sanitizer", icon: "🛡️", state: "idle" },
    { id: "compressor", label: "Context & Prompt Compressor", role: "Token Optimizer", icon: "⚡", state: "idle" },
    { id: "diagnostic", label: "Diagnostic Agent (Gemini)", role: "Causal Reasoning Engine", icon: "🧠", state: "idle" },
    { id: "remediation", label: "Remediation Agent", role: "Mitigation & Blast Radius", icon: "🔧", state: "idle" },
    { id: "verifier", label: "Verifier / Critic Agent", role: "Safety & Compliance Audit", icon: "⚖️", state: "idle" },
    { id: "ledger", label: "Cryptographic SHA-256 Ledger", role: "Tamper-Evident Trail", icon: "⛓️", state: "success" },
    { id: "bigquery", label: "Google BigQuery Streaming", role: "Enterprise Analytics", icon: "☁️", state: "success" }
  ];

  function renderGraph(containerId, activeStates = {}) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = "";

    defaultNodes.forEach((node, index) => {
      const state = activeStates[node.id] || node.state || "idle";
      
      const nodeEl = document.createElement("div");
      nodeEl.className = `graph-node state-${state}`;
      nodeEl.id = `node-${node.id}`;

      let badgeClass = "badge-nominal";
      let badgeText = "IDLE";
      if (state === "active") {
        badgeClass = "badge-secure";
        badgeText = "PROCESSING";
      } else if (state === "success") {
        badgeClass = "badge-nominal";
        badgeText = "VERIFIED";
      } else if (state === "blocked") {
        badgeClass = "badge-critical";
        badgeText = "INTERCEPTED";
      }

      nodeEl.innerHTML = `
        <div class="node-left">
          <div class="node-icon-box">${node.icon}</div>
          <div class="node-info">
            <div class="node-title">${node.label}</div>
            <div class="node-role">${node.role}</div>
          </div>
        </div>
        <div class="node-right">
          <span class="node-badge ${badgeClass}">${badgeText}</span>
        </div>
      `;

      container.appendChild(nodeEl);

      // Render connector link between nodes except last
      if (index < defaultNodes.length - 1) {
        const linkEl = document.createElement("div");
        linkEl.className = `graph-link ${state === "active" || state === "success" ? "active-flow" : ""}`;
        container.appendChild(linkEl);
      }
    });
  }

  function setExecutionAnimation(containerId, isSuccess = true) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (!isSuccess) {
      renderGraph(containerId, { guard: "blocked", compressor: "idle", diagnostic: "idle", remediation: "idle", verifier: "idle", ledger: "success", bigquery: "idle" });
      return;
    }

    // Success sequence animation
    renderGraph(containerId, {
      guard: "success",
      compressor: "success",
      diagnostic: "success",
      remediation: "success",
      verifier: "success",
      ledger: "success",
      bigquery: "success"
    });
  }

  return {
    init: function (containerId) {
      renderGraph(containerId);
    },
    update: setExecutionAnimation
  };
})();
