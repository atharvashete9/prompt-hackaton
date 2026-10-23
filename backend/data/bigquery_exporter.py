import json
import time
from typing import Dict, Any, List
from backend.config import config

class BigQuerySchemaValidator:
    SCHEMA = [
        {"name": "event_id", "type": "STRING", "mode": "REQUIRED"},
        {"name": "timestamp", "type": "TIMESTAMP", "mode": "REQUIRED"},
        {"name": "domain", "type": "STRING", "mode": "REQUIRED"},
        {"name": "agent_name", "type": "STRING", "mode": "REQUIRED"},
        {"name": "action_type", "type": "STRING", "mode": "REQUIRED"},
        {"name": "threat_score", "type": "FLOAT", "mode": "NULLABLE"},
        {"name": "tokens_used", "type": "INTEGER", "mode": "NULLABLE"},
        {"name": "latency_ms", "type": "FLOAT", "mode": "NULLABLE"},
        {"name": "decision_payload", "type": "JSON", "mode": "REQUIRED"},
        {"name": "block_hash", "type": "STRING", "mode": "REQUIRED"},
        {"name": "gcp_project", "type": "STRING", "mode": "REQUIRED"}
    ]

    @classmethod
    def validate_row(cls, row: Dict[str, Any]) -> bool:
        required_keys = ["event_id", "timestamp", "domain", "agent_name", "action_type", "block_hash"]
        for key in required_keys:
            if key not in row or row[key] is None:
                return False
        return True

class BigQueryStreamingExporter:
    def __init__(self):
        self.project_id = config.GOOGLE_CLOUD_PROJECT
        self.dataset_id = config.BIGQUERY_DATASET
        self.table_id = config.BIGQUERY_TABLE
        self.buffer: List[Dict[str, Any]] = []
        self.total_rows_exported = 0
        self.last_flush_time = time.time()

    def buffer_record(
        self,
        event_id: str,
        domain: str,
        agent_name: str,
        action_type: str,
        threat_score: float,
        tokens_used: int,
        latency_ms: float,
        decision_payload: Dict[str, Any],
        block_hash: str
    ):
        iso_timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        row = {
            "event_id": event_id,
            "timestamp": iso_timestamp,
            "domain": domain,
            "agent_name": agent_name,
            "action_type": action_type,
            "threat_score": threat_score,
            "tokens_used": tokens_used,
            "latency_ms": latency_ms,
            "decision_payload": decision_payload,
            "block_hash": block_hash,
            "gcp_project": self.project_id
        }

        if BigQuerySchemaValidator.validate_row(row):
            self.buffer.append(row)
            if len(self.buffer) >= 5:
                self.flush_stream()

    def flush_stream(self) -> Dict[str, Any]:
        """Flushes the buffer as a BigQuery streaming insert payload."""
        rows_to_export = list(self.buffer)
        count = len(rows_to_export)
        self.buffer.clear()
        self.total_rows_exported += count
        self.last_flush_time = time.time()

        return {
            "status": "STREAMED_TO_BIGQUERY",
            "rows_flushed": count,
            "total_flushed_lifetime": self.total_rows_exported,
            "destination": f"{self.project_id}.{self.dataset_id}.{self.table_id}",
            "schema_columns": len(BigQuerySchemaValidator.SCHEMA)
        }

    def export_all_jsonl(self) -> str:
        """Exports buffered & current dataset in BigQuery-compatible JSON Lines format."""
        return "\n".join(json.dumps(row) for row in self.buffer)

    def get_status(self) -> Dict[str, Any]:
        return {
            "project_id": self.project_id,
            "dataset_id": self.dataset_id,
            "table_id": self.table_id,
            "buffered_rows": len(self.buffer),
            "total_streamed_rows": self.total_rows_exported,
            "last_flush_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(self.last_flush_time)),
            "schema": BigQuerySchemaValidator.SCHEMA
        }

bigquery_exporter = BigQueryStreamingExporter()
