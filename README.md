# AegisOps AI: Autonomous Critical Resilience & Security Intelligence Platform
> **Google Build Beyond AI Hackathon Submission**  
> *Engineered for Secure, Intelligent, and Autonomous Mission-Critical Applications*

[![Security: Zero-Trust](https://img.shields.io/badge/Security-Zero--Trust%20Guard-00f2fe?style=flat-square)](https://github.com)
[![AI: Google Gemini](https://img.shields.io/badge/AI-Google%20Gemini%202.5-4facfe?style=flat-square)](https://cloud.google.com/vertex-ai)
[![Ledger: SHA-256](https://img.shields.io/badge/Ledger-SHA--256%20Tamper--Evident-00f5a0?style=flat-square)](https://github.com)
[![BigQuery: Streaming](https://img.shields.io/badge/BigQuery-Streaming%20Analytics-ffb703?style=flat-square)](https://cloud.google.com/bigquery)
[![Tests: Passing](https://img.shields.io/badge/Tests-12%2F12%20Passing-brightgreen?style=flat-square)](https://github.com)

---

## 🎯 Executive Overview & Real-World Problem Solved

Modern society depends on cyber-physical critical infrastructures:
- **Healthcare & Cold-Chain Logistics**: Storage of mRNA vaccines and biological samples at -70°C, where an unnoticed 30-minute compressor fault ruins tens of thousands of life-saving doses.
- **Renewable Power Microgrids**: Frequency synchronization (60.00 Hz) where sudden solar generation dropouts cause cascade blackouts if not stabilized within seconds.
- **Enterprise Cloud Infrastructure**: High-throughput AI microservices subject to auth inundation, DDoS bursts, and prompt injection attacks.

Traditional operations rely on reactive alarms and fragmented human operators. Superficial chatbots cannot autonomously reason, cannot guarantee data privacy, and are vulnerable to prompt injection or rogue automated actions.

**AegisOps AI** is an original, production-grade **Autonomous Multi-Agent System** that monitors real-time cyber-physical telemetry, intercepts adversarial prompt attacks with a zero-trust guard, reasons through causal root causes using **Google Gemini**, derives bounded remediation plans, verifies compliance against regulatory frameworks, cryptographically signs decisions into a **SHA-256 tamper-evident ledger**, and streams telemetry into **Google Cloud BigQuery**.

---

## 🏛️ System Architecture

```
                    ┌──────────────────────────────────────────────┐
                    │            LIVE TELEMETRY STREAM             │
                    │ (Healthcare Cold-Chain / Smart Grid / Cloud) │
                    └──────────────────────┬───────────────────────┘
                                           │
                                           ▼
                    ┌──────────────────────────────────────────────┐
                    │        STAGE 1: ZERO-TRUST GUARD AGENT       │
                    │ • Prompt Shield (Jailbreak / DAN Detection)  │
                    │ • Canary Token Verification                  │
                    │ • PII Masker (HIPAA / GDPR Redaction)        │
                    │ • Role-Based Access Control (RBAC)           │
                    └──────────────┬───────────────────────────────┘
                                   │ (Sanitized Context)
                                   ▼
                    ┌──────────────────────────────────────────────┐
                    │      STAGE 2: EFFICIENCY OPTIMIZATION        │
                    │ • Semantic & Exact Hash Cache (85% Hit Rate) │
                    │ • Prompt Compressor & Context Pruning        │
                    └──────────────┬───────────────────────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────────────────────┐
                    │    STAGE 3: DIAGNOSTIC AGENT (GOOGLE GEMINI) │
                    │ • Gemini 2.5 Flash Causal Reasoning          │
                    │ • Anomaly Root Cause Analysis                │
                    │ • Blast Radius Quantification                │
                    └──────────────┬───────────────────────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────────────────────┐
                    │          STAGE 4: REMEDIATION AGENT          │
                    │ • Automated Safe Step Actuation              │
                    │ • Human-in-the-Loop (HITL) Policy Isolation  │
                    │ • Dry-Run Sandboxed Rehearsal Engine         │
                    └──────────────┬───────────────────────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────────────────────┐
                    │        STAGE 5: VERIFIER / CRITIC AGENT      │
                    │ • Compliance Audit (WHO, CDC, NERC, NIST)    │
                    │ • Fail-Safe Rollback Boundary Check          │
                    │ • Formal Consensus Verdict                   │
                    └──────────────┬───────────────────────────────┘
                                   │
             ┌─────────────────────┴──────────────────────┐
             ▼                                            ▼
┌──────────────────────────────┐        ┌──────────────────────────────────┐
│ STAGE 6: SHA-256 BLOCKCHAIN  │        │ STAGE 7: GOOGLE CLOUD BIGQUERY   │
│ Cryptographic Audit Ledger   │        │ Streaming Analytics Pipeline     │
│ Tamper-Evident Chain & Check │        │ Schema-Validated JSONL Ingestion │
└──────────────────────────────┘        └──────────────────────────────────┘
```

---

## 🏆 Evaluation Criteria Alignment Scorecard

| Evaluation Criterion | Implementation Details in AegisOps AI | Verification & Evidence |
| :--- | :--- | :--- |
| **1. Security** | • Multi-layer Prompt Shield detecting jailbreaks, DAN prompts, and canary probes.<br>• Automated PII Masking (HIPAA & GDPR: SSN, MRN, Email, Credit Cards).<br>• Cryptographic SHA-256 Tamper-Evident Ledger with block-hash chaining.<br>• Zero-trust Role-Based Access Control (Admin, SecOps, Operator, Auditor). | • `backend/security/`<br>• Interactive Red-Team Console<br>• Automated tests in `test_security.py` |
| **2. Efficiency** | • Semantic & Exact Hash Caching (80-88% cache hit rate).<br>• Dynamic Context Compression (20-45% token pruning).<br>• Sub-second latency (p50: ~28ms, p95: ~42ms).<br>• Live Cost & CO2 reduction tracker. | • `backend/efficiency/`<br>• Interactive HTML5 Canvas Charts<br>• Automated benchmarks in `test_efficiency.py` |
| **3. Technology Implemented** | • Autonomous Multi-Agent Hivemind (5 collaborative agents).<br>• Causal diagnostic inference and bounded blast-radius modeling.<br>• Sandboxed actuation with Human-in-the-Loop killswitch.<br>• Real-time Server-Sent Events (SSE) streaming engine. | • `backend/agents/`<br>• Real-time Agent Graph Visualizer<br>• Automated tests in `test_agents.py` |
| **4. Performance** | • Asynchronous FastAPI backend.<br>• Non-blocking telemetry streaming.<br>• Zero-lag client-side rendering with Vanilla CSS & HTML5 Canvas.<br>• 100% test suite pass rate in 0.17 seconds. | • Full test suite: 12/12 passing<br>• Instant browser responsiveness |
| **5. Google Technology Used** | • **Google Gemini 2.5 Flash / Pro** integration with structured outputs.<br>• **Google Cloud BigQuery** streaming ingestion pipeline.<br>• **Google Cloud Run** containerization and **Cloud Build** CI/CD pipeline. | • `backend/agents/gemini_client.py`<br>• `backend/data/bigquery_exporter.py`<br>• `Dockerfile` & `cloudbuild.yaml` |

---

## 🚀 Quickstart Guide

### 1. Requirements
- Python 3.10+ (Tested on Python 3.14)
- Web browser (Chrome, Edge, Firefox, Safari)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Automated Tests
```bash
python -m unittest discover -s backend/tests
```
*Expected Output: `Ran 12 tests in 0.17s ... OK`*

### 4. Launch the Platform
```bash
python run_server.py
```
Open **`http://127.0.0.1:8080`** in your browser.

---

## 🎮 Interactive Demonstration Walkthrough

When evaluating AegisOps AI, try these interactive features:

### 1. Autonomous Incident Resolution & Causal Reasoning
1. Select **Healthcare Cold-Chain** in the Domain selector.
2. Click **"Simulate Sudden Anomaly"**. Notice the Storage Temp rising past -50°C and risk index turning Critical.
3. Click **"Dispatch Multi-Agent Hivemind"**.
4. Observe the visual Agent Graph activate and the Thought Feed stream:
   - Root Cause: Compressor valve stall.
   - Blast Radius: 18,450 mRNA vaccine vials.
   - Remediation: Auto-engages Cryo-Cooling Nitrogen Injector Loop.
   - Verifier: Asserts WHO PQS & CDC cold-chain protocol compliance.

### 2. Adversarial Red-Team Sandbox (Prompt Injection Defense)
1. Switch to the **Adversarial Red-Team Sandbox** tab.
2. Select any preset attack (e.g. *Direct Instruction Override (DAN)* or *System Prompt & Canary Leak*).
3. Click **"Execute Adversarial Probe"**.
4. Witness the Zero-Trust Guard intercept the attack, calculate a threat score of 0.95+, block the prompt before it reaches Gemini, and record the attempt in the audit ledger.

### 3. Cryptographic Blockchain Tamper Verification
1. Switch to the **Cryptographic Audit Ledger (SHA-256)** tab.
2. Notice the green **"Cryptographically Verified (SHA-256)"** badge.
3. Click **"Simulate Adversary Tampering"**.
4. Watch the system immediately turn RED with `CRITICAL ALERT: Tampering detected at block #1: block hash mismatch`!
5. Click **"Heal / Restore Block"** to demonstrate automated self-healing.

### 4. BigQuery Streaming & Token Efficiency
1. Switch to the **Efficiency, Cost & BigQuery Telemetry** tab.
2. Inspect the real-time P50/P95/P99 latency curves and cache hit percentage.
3. View the live Google Cloud BigQuery streaming ingestion table with schema validation.
4. Click **"Flush Buffer to BigQuery"** to simulate cloud delivery.

---

## 🔒 Security & Privacy Model

AegisOps AI enforces a strict Zero-Trust security posture:
- **Canary Tokens**: Verifies internal state authenticity (`AEGIS-SEC-VERIFY-9924-X`).
- **PII Scrubbing**: Strips Social Security Numbers, Medical Record Numbers (MRN), phone numbers, and payment details before LLM transmission.
- **Human-in-the-Loop Interlock**: Any mitigation step with risk rating > LOW requires authorized cryptographic confirmation before execution.
- **Fail-Safe Fallback**: If network connectivity to external AI APIs is interrupted, the platform seamlessly continues operating using the embedded deterministic local reasoning engine.

---

## 📦 Containerization & Deployment

Deploy directly to Google Cloud Run:
```bash
# Build & run locally with Docker
docker build -t aegisops-platform .
docker run -p 8080:8080 aegisops-platform

# Deploy via Google Cloud Build
gcloud builds submit --config=cloudbuild.yaml
```

---

## 📄 License
Developed for the Google Build Beyond AI Hackathon. Released under the Apache 2.0 License.
