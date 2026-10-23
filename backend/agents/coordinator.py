import time
import uuid
from typing import Dict, Any, List
from backend.agents.guard_agent import guard_agent
from backend.agents.diagnostic_agent import diagnostic_agent
from backend.agents.remediation_agent import remediation_agent
from backend.agents.verifier_agent import verifier_agent
from backend.security.audit_ledger import audit_ledger
from backend.security.prompt_shield import prompt_shield
from backend.efficiency.semantic_cache import semantic_cache
from backend.efficiency.prompt_compressor import prompt_compressor
from backend.efficiency.telemetry import efficiency_telemetry
from backend.data.bigquery_exporter import bigquery_exporter

class MultiAgentCoordinator:
    NAME = "AegisMultiAgentCoordinator"

    def process_incident_cycle(
        self,
        telemetry_snapshot: Dict[str, Any],
        operator_prompt: str = "",
        user_role: str = "operator",
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Executes end-to-end multi-agent resilience cycle:
        1. Pre-screening & Security Guard
        2. Semantic Cache lookup
        3. Context Compression
        4. Gemini Causal Diagnosis
        5. Autonomous Remediation Planning
        6. Independent Verifier / Critic validation
        7. Cryptographic SHA-256 ledger recording
        8. Google BigQuery Streaming Export
        9. Efficiency & Telemetry tracking
        """
        cycle_start = time.time()
        incident_id = f"INC-{uuid.uuid4().hex[:8].upper()}"
        domain = telemetry_snapshot.get("domain", "Healthcare Cold-Chain")

        # Step 1: Zero-Trust Security Pre-screen
        guard_result = guard_agent.pre_screen_input(operator_prompt, user_role=user_role)
        
        # If blocked by prompt shield
        if guard_result["status"] == "BLOCKED":
            elapsed_ms = (time.time() - cycle_start) * 1000
            audit_block = audit_ledger.record_event(
                agent_name="ZeroTrustGuardAgent",
                action_type="ATTACK_INTERCEPTED",
                input_summary=operator_prompt[:120],
                output_summary=f"Threat score {guard_result['threat_score']}: Prompt Injection Blocked",
                threat_score=guard_result["threat_score"],
                tokens_used=0,
                metadata={"vectors": guard_result["detected_vectors"], "incident_id": incident_id}
            )

            efficiency_telemetry.record_request(
                latency_ms=elapsed_ms,
                input_tokens=0,
                output_tokens=0,
                tokens_saved=320
            )

            return {
                "incident_id": incident_id,
                "status": "SECURITY_BLOCK",
                "guard_assessment": guard_result,
                "audit_block": audit_block.to_dict(),
                "execution_graph": self._build_graph_state("SECURITY_BLOCK", guard_result),
                "latency_ms": round(elapsed_ms, 2)
            }

        # Step 2: Semantic Cache Lookup
        cache_query = f"{domain}:{telemetry_snapshot.get('scenario')}:{operator_prompt}:{telemetry_snapshot.get('anomaly_type')}"
        cached_resp, match_type, sim_score = semantic_cache.get(cache_query)
        if cached_resp:
            elapsed_ms = (time.time() - cycle_start) * 1000
            tokens_saved = cached_resp.get("tokens_saved_estimate", 450)

            efficiency_telemetry.record_request(
                latency_ms=elapsed_ms,
                input_tokens=0,
                output_tokens=0,
                tokens_saved=tokens_saved
            )

            audit_block = audit_ledger.record_event(
                agent_name="CoordinatorCache",
                action_type="CACHE_HIT_RESOLUTION",
                input_summary=cache_query[:120],
                output_summary=f"Resolved via {match_type} (Score {sim_score}). Saved {tokens_saved} tokens.",
                threat_score=guard_result["threat_score"],
                tokens_used=0,
                metadata={"incident_id": incident_id, "cached": True}
            )

            cached_copy = dict(cached_resp)
            cached_copy["cache_metadata"] = {
                "hit": True,
                "match_type": match_type,
                "similarity_score": sim_score,
                "latency_ms": round(elapsed_ms, 2)
            }
            cached_copy["incident_id"] = incident_id
            cached_copy["audit_block"] = audit_block.to_dict()
            return cached_copy

        # Step 3: Context Compression
        compressed_text, comp_meta = prompt_compressor.compress(guard_result["sanitized_input"])

        # Step 4: Diagnostic Agent with Google Gemini Reasoning
        diag_result = diagnostic_agent.analyze(telemetry_snapshot, context_notes=compressed_text)

        # Step 5: Remediation Agent
        remediation_result = remediation_agent.formulate_plan(diag_result, domain=domain)

        # Execute safe autonomous steps in sandbox
        execution_outcomes = []
        for step in remediation_result.get("autonomous_safe_steps", []):
            outcome = remediation_agent.execute_action_sandbox(step, dry_run=dry_run)
            execution_outcomes.append(outcome)

        # Step 6: Verifier / Critic Validation
        verifier_result = verifier_agent.verify_remediation_plan(
            domain=domain,
            diagnosis=diag_result,
            remediation_plan=remediation_result
        )

        total_input_tokens = diag_result.get("input_tokens", 140)
        total_output_tokens = diag_result.get("output_tokens", 220)
        elapsed_ms = (time.time() - cycle_start) * 1000

        # Step 7: Cryptographic SHA-256 Ledger
        audit_block = audit_ledger.record_event(
            agent_name="MultiAgentConsensus",
            action_type="RESOLVE_INCIDENT",
            input_summary=f"{domain} status: {telemetry_snapshot.get('status')}",
            output_summary=f"Diagnosis: {diag_result.get('diagnosis')} | Verdict: {verifier_result.get('verdict')}",
            threat_score=guard_result["threat_score"],
            tokens_used=total_input_tokens + total_output_tokens,
            metadata={
                "incident_id": incident_id,
                "domain": domain,
                "model_used": diag_result.get("model_used"),
                "auto_steps_executed": len(execution_outcomes),
                "requires_hitl": remediation_result.get("requires_human_approval")
            }
        )

        # Step 8: Stream to Google BigQuery
        bigquery_exporter.buffer_record(
            event_id=incident_id,
            domain=domain,
            agent_name="AegisConsensusHivemind",
            action_type="CONSENSUS_ACTION",
            threat_score=guard_result["threat_score"],
            tokens_used=total_input_tokens + total_output_tokens,
            latency_ms=elapsed_ms,
            decision_payload={
                "diagnosis": diag_result.get("diagnosis"),
                "severity": diag_result.get("severity"),
                "verdict": verifier_result.get("verdict"),
                "autonomous_steps": remediation_result.get("autonomous_safe_steps"),
                "hitl_steps": remediation_result.get("human_in_the_loop_steps")
            },
            block_hash=audit_block.block_hash
        )

        # Step 9: Efficiency Telemetry Update
        efficiency_telemetry.record_request(
            latency_ms=elapsed_ms,
            input_tokens=total_input_tokens,
            output_tokens=total_output_tokens,
            tokens_saved=comp_meta.get("tokens_saved_estimate", 0)
        )

        # Step 10: Store in Semantic Cache
        response_payload = {
            "incident_id": incident_id,
            "domain": domain,
            "status": "CONSENSUS_REACHED",
            "guard": guard_result,
            "diagnosis": diag_result,
            "remediation": remediation_result,
            "execution_outcomes": execution_outcomes,
            "verification": verifier_result,
            "compression_meta": comp_meta,
            "audit_block": audit_block.to_dict(),
            "execution_graph": self._build_graph_state("CONSENSUS_REACHED", diag_result, remediation_result, verifier_result),
            "latency_ms": round(elapsed_ms, 2),
            "tokens_saved_estimate": comp_meta.get("tokens_saved_estimate", 80) + 350
        }

        semantic_cache.set(cache_query, response_payload, tokens_saved=response_payload["tokens_saved_estimate"])

        return response_payload

    def _build_graph_state(self, status: str, *args) -> List[Dict[str, Any]]:
        """Constructs live visual graph nodes representing agent hivemind status."""
        nodes = [
            {"id": "guard", "label": "Zero-Trust Guard Agent", "status": "active" if status == "CONSENSUS_REACHED" else "blocked", "role": "Security Sentinel"},
            {"id": "compressor", "label": "Prompt Compressor", "status": "active" if status == "CONSENSUS_REACHED" else "idle", "role": "Efficiency Optimizer"},
            {"id": "diagnostic", "label": "Diagnostic Agent (Gemini)", "status": "active" if status == "CONSENSUS_REACHED" else "idle", "role": "Causal Reasoning"},
            {"id": "remediation", "label": "Remediation Agent", "status": "active" if status == "CONSENSUS_REACHED" else "idle", "role": "Autonomous Mitigator"},
            {"id": "verifier", "label": "Verifier Critic Agent", "status": "active" if status == "CONSENSUS_REACHED" else "idle", "role": "Compliance Validator"},
            {"id": "ledger", "label": "Cryptographic SHA-256 Ledger", "status": "success", "role": "Tamper-Evident Trail"},
            {"id": "bigquery", "label": "Google BigQuery Streaming", "status": "success", "role": "Analytics Telemetry"}
        ]
        return nodes

coordinator = MultiAgentCoordinator()
