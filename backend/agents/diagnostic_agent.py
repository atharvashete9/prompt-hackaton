import json
from typing import Dict, Any
from backend.agents.gemini_client import gemini_client

class DiagnosticAgent:
    NAME = "DiagnosticAgent"

    SYSTEM_INSTRUCTION = (
        "You are the Lead Diagnostic Agent for AegisOps AI, an autonomous critical infrastructure sentinel. "
        "Your task is to analyze telemetry deltas and incident logs, identify causal root causes, "
        "estimate blast radius, and calculate diagnostic confidence. "
        "Format your output strictly with structured diagnosis, root cause, severity, blast radius, and confidence."
    )

    def analyze(self, telemetry_data: Dict[str, Any], context_notes: str = "") -> Dict[str, Any]:
        prompt = (
            f"Active Domain: {telemetry_data.get('domain', 'Infrastructure')}\n"
            f"Scenario: {telemetry_data.get('scenario')}\n"
            f"Status: {telemetry_data.get('status')}\n"
            f"Anomaly Type: {telemetry_data.get('anomaly_type')}\n"
            f"Raw Sensor Metrics: {json.dumps(telemetry_data.get('metrics', {}))}\n"
            f"Operator Notes: {context_notes}"
        )

        llm_response = gemini_client.generate_agent_response(
            system_instruction=self.SYSTEM_INSTRUCTION,
            user_prompt=prompt,
            agent_role="Diagnostic"
        )

        return {
            "agent": self.NAME,
            "status": "COMPLETED",
            "model_used": llm_response.get("model"),
            "source": llm_response.get("source"),
            "diagnosis": llm_response.get("structured_data", {}).get("diagnosis", "Telemetry Ingest Completed"),
            "root_cause": llm_response.get("structured_data", {}).get("root_cause", "Nominal operational envelope"),
            "severity": llm_response.get("structured_data", {}).get("severity", "LOW"),
            "blast_radius": llm_response.get("structured_data", {}).get("blast_radius", "Zero localized impact"),
            "confidence_score": llm_response.get("structured_data", {}).get("confidence_score", 0.95),
            "input_tokens": llm_response.get("input_tokens", 0),
            "output_tokens": llm_response.get("output_tokens", 0),
            "latency_ms": llm_response.get("latency_ms", 0.0),
            "raw_payload": llm_response.get("structured_data", {})
        }

diagnostic_agent = DiagnosticAgent()
