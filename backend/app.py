import os
import json
import asyncio
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.config import config
from backend.agents.coordinator import coordinator
from backend.agents.gemini_client import gemini_client
from backend.data.telemetry_stream import telemetry_stream
from backend.data.bigquery_exporter import bigquery_exporter
from backend.security.audit_ledger import audit_ledger
from backend.security.prompt_shield import prompt_shield
from backend.security.rbac import rbac
from backend.efficiency.semantic_cache import semantic_cache
from backend.efficiency.telemetry import efficiency_telemetry

app = FastAPI(
    title=config.PROJECT_NAME,
    version=config.VERSION,
    description="Autonomous Mission-Critical Resilience & Security Intelligence Platform"
)

# Enable CORS for local dev / cross-origin inspection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Request Models
class TriggerIncidentRequest(BaseModel):
    prompt: Optional[str] = ""
    scenario: Optional[str] = None
    role: Optional[str] = "operator"
    dry_run: Optional[bool] = True

class ScenarioRequest(BaseModel):
    scenario: str

class AnomalyRequest(BaseModel):
    anomaly_type: str = "THERMAL_FAILURE"

class RedTeamRequest(BaseModel):
    prompt: str
    role: Optional[str] = "secops"

class TamperTestRequest(BaseModel):
    block_index: int
    forged_output: str

class GeminiKeyRequest(BaseModel):
    api_key: str

# ----------------- Health & Metrics -----------------
@app.get("/healthz")
def healthz():
    verification = audit_ledger.verify_chain()
    return {
        "status": "HEALTHY",
        "service": config.PROJECT_NAME,
        "version": config.VERSION,
        "gcp_project": config.GOOGLE_CLOUD_PROJECT,
        "audit_chain_valid": verification["valid"],
        "gemini_live_connected": bool(gemini_client.api_key)
    }

@app.get("/metrics")
def metrics():
    stats = efficiency_telemetry.get_stats()
    cache_meta = semantic_cache.get_metrics()
    return {
        "efficiency": stats,
        "cache": cache_meta,
        "bigquery_streamed_rows": bigquery_exporter.total_rows_exported,
        "ledger_blocks": len(audit_ledger.chain)
    }

# ----------------- Telemetry Endpoints -----------------
@app.get("/api/telemetry/tick")
def get_tick():
    return telemetry_stream.generate_next_tick()

@app.post("/api/telemetry/scenario")
def set_scenario(req: ScenarioRequest):
    telemetry_stream.set_scenario(req.scenario)
    return {"status": "SUCCESS", "current_scenario": telemetry_stream.current_scenario}

@app.post("/api/telemetry/anomaly")
def inject_anomaly(req: AnomalyRequest):
    telemetry_stream.trigger_anomaly(req.anomaly_type)
    return {"status": "ANOMALY_TRIGGERED", "anomaly_type": req.anomaly_type}

@app.post("/api/telemetry/resolve")
def resolve_anomaly():
    telemetry_stream.clear_anomaly()
    return {"status": "NOMINAL_RESTORED"}

# ----------------- Real-Time SSE Stream -----------------
@app.get("/api/telemetry/stream")
async def sse_telemetry_stream():
    """Server-Sent Events streaming live sensor ticks to frontend."""
    async def event_generator():
        while True:
            tick_data = telemetry_stream.generate_next_tick()
            payload = json.dumps(tick_data)
            yield f"data: {payload}\n\n"
            await asyncio.sleep(config.STREAM_INTERVAL_SECONDS)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# ----------------- Autonomous Agent Dispatch -----------------
@app.post("/api/agent/trigger")
def trigger_agent(req: TriggerIncidentRequest):
    if req.scenario:
        telemetry_stream.set_scenario(req.scenario)
    
    current_tick = telemetry_stream.generate_next_tick()
    result = coordinator.process_incident_cycle(
        telemetry_snapshot=current_tick,
        operator_prompt=req.prompt or "",
        user_role=req.role or "operator",
        dry_run=req.dry_run if req.dry_run is not None else True
    )
    return result

# ----------------- Security & Red-Team Console -----------------
@app.post("/api/security/redteam")
def run_redteam_test(req: RedTeamRequest):
    """Interactive Red-Team prompt injection and jailbreak evaluator."""
    assessment = prompt_shield.inspect(req.prompt)
    
    # Record red-team probe in audit log
    audit_block = audit_ledger.record_event(
        agent_name="RedTeamProbeTester",
        action_type="REDTEAM_PROBE_EVALUATION",
        input_summary=req.prompt[:100],
        output_summary=f"Threat Score: {assessment['threat_score']} - Action: {assessment['action']}",
        threat_score=assessment["threat_score"],
        tokens_used=0,
        metadata={"detected_vectors": assessment["detected_vectors"]}
    )

    return {
        "prompt": req.prompt,
        "assessment": assessment,
        "audit_block": audit_block.to_dict()
    }

# ----------------- Cryptographic Audit Ledger -----------------
@app.get("/api/security/audit/chain")
def get_audit_chain(limit: int = 50):
    verification = audit_ledger.verify_chain()
    return {
        "verification": verification,
        "blocks": audit_ledger.get_recent(limit=limit)
    }

@app.post("/api/security/audit/tamper-test")
def tamper_test(req: TamperTestRequest):
    success = audit_ledger.tamper_test_simulate(req.block_index, req.forged_output)
    verification = audit_ledger.verify_chain()
    return {
        "tampering_simulated": success,
        "block_index": req.block_index,
        "verification_result": verification
    }

@app.post("/api/security/audit/restore")
def restore_block(req: TamperTestRequest):
    audit_ledger.restore_block(req.block_index)
    verification = audit_ledger.verify_chain()
    return {
        "restored": True,
        "verification_result": verification
    }

# ----------------- Efficiency & BigQuery -----------------
@app.get("/api/efficiency/stats")
def get_efficiency_stats():
    return {
        "telemetry": efficiency_telemetry.get_stats(),
        "cache": semantic_cache.get_metrics()
    }

@app.get("/api/bigquery/status")
def get_bigquery_status():
    return bigquery_exporter.get_status()

@app.post("/api/bigquery/flush")
def flush_bigquery():
    return bigquery_exporter.flush_stream()

@app.post("/api/config/gemini-key")
def set_gemini_key(req: GeminiKeyRequest):
    gemini_client.set_api_key(req.api_key)
    return {
        "status": "UPDATED",
        "configured": bool(gemini_client.api_key),
        "model": gemini_client.model
    }

# ----------------- Frontend Static Files -----------------
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/", response_class=HTMLResponse)
    def serve_index():
        index_file = os.path.join(frontend_dir, "index.html")
        if os.path.exists(index_file):
            with open(index_file, "r", encoding="utf-8") as f:
                return f.read()
        return "<h1>AegisOps AI Backend Running</h1>"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host=config.HOST, port=config.PORT, reload=True)
