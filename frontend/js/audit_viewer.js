/**
 * Cryptographic SHA-256 Audit Ledger Explorer
 */

const AuditViewer = (function () {
  let isTampered = false;
  let tamperedIndex = 1;

  async function loadChain() {
    try {
      const res = await fetch("/api/security/audit/chain?limit=40");
      const data = await res.json();
      renderStatus(data.verification);
      renderBlocks(data.blocks);
    } catch (err) {
      console.error("Failed to load audit ledger:", err);
    }
  }

  function renderStatus(verification) {
    const badge = document.getElementById("ledgerStatusBadge");
    const text = document.getElementById("ledgerStatusText");
    const stats = document.getElementById("ledgerStatsText");
    const restoreBtn = document.getElementById("restoreTamperBtn");
    const tamperBtn = document.getElementById("tamperTestBtn");

    if (!badge || !text) return;

    if (verification.valid) {
      badge.className = "audit-status-badge valid";
      text.innerText = "Cryptographically Verified (SHA-256)";
      if (stats) stats.innerText = `Total Blocks: ${verification.total_blocks} | Root-of-Trust: Active`;
      if (restoreBtn) restoreBtn.style.display = "none";
      if (tamperBtn) tamperBtn.style.display = "inline-flex";
      isTampered = false;
    } else {
      badge.className = "audit-status-badge invalid";
      text.innerText = `CRITICAL ALERT: ${verification.error}`;
      if (stats) stats.innerText = `Breach Detected at Block #${verification.corrupted_block_index}`;
      if (restoreBtn) restoreBtn.style.display = "inline-flex";
      if (tamperBtn) tamperBtn.style.display = "none";
      isTampered = true;
    }
  }

  function renderBlocks(blocks) {
    const container = document.getElementById("ledgerBlocksList");
    if (!container) return;

    container.innerHTML = "";

    // Show latest first
    const reversed = [...blocks].reverse();

    reversed.forEach((b) => {
      const card = document.createElement("div");
      card.className = `audit-block-card ${isTampered && b.index === tamperedIndex ? "tampered" : ""}`;
      
      card.innerHTML = `
        <div class="block-header-row">
          <div style="display: flex; align-items: center; gap: 8px;">
            <span class="block-index-badge">Block #${b.index}</span>
            <span style="font-weight: 700; color: #fff;">${b.agent_name}</span>
            <span class="badge badge-info" style="font-size: 10px;">${b.action_type}</span>
          </div>
          <span style="font-family: var(--font-mono); font-size: 11px; color: var(--text-muted);">${b.iso_time}</span>
        </div>

        <div style="font-size: 12px; color: var(--text-secondary); margin: 4px 0;">
          <strong>Summary:</strong> ${b.output_summary}
        </div>

        <div class="block-hash-row">
          <span class="hash-label">Block Hash:</span>
          <span class="hash-value">${b.block_hash}</span>
        </div>
        <div class="block-hash-row">
          <span class="hash-label">Prev Hash:</span>
          <span class="hash-value" style="color: var(--text-muted);">${b.previous_hash}</span>
        </div>
      `;

      container.appendChild(card);
    });
  }

  async function simulateTampering() {
    try {
      const res = await fetch("/api/security/audit/tamper-test", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          block_index: 1,
          forged_output: "FORGED_MALICIOUS_LOG: Attacker modified historical temperature record"
        })
      });
      const data = await res.json();
      tamperedIndex = 1;
      await loadChain();
    } catch (err) {
      console.error("Tamper simulation failed:", err);
    }
  }

  async function restoreBlock() {
    try {
      await fetch("/api/security/audit/restore", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ block_index: 1, forged_output: "" })
      });
      await loadChain();
    } catch (err) {
      console.error("Restore failed:", err);
    }
  }

  return {
    init: function () {
      loadChain();
      const verifyBtn = document.getElementById("verifyLedgerBtn");
      const tamperBtn = document.getElementById("tamperTestBtn");
      const restoreBtn = document.getElementById("restoreTamperBtn");

      if (verifyBtn) verifyBtn.addEventListener("click", loadChain);
      if (tamperBtn) tamperBtn.addEventListener("click", simulateTampering);
      if (restoreBtn) restoreBtn.addEventListener("click", restoreBlock);
    },
    refresh: loadChain
  };
})();
