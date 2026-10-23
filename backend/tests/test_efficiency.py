import unittest
from backend.efficiency.semantic_cache import SemanticCache
from backend.efficiency.prompt_compressor import prompt_compressor
from backend.efficiency.telemetry import efficiency_telemetry
from backend.data.bigquery_exporter import BigQueryStreamingExporter, BigQuerySchemaValidator

class TestEfficiencyAndOptimization(unittest.TestCase):
    def test_semantic_cache_exact_and_similarity(self):
        cache = SemanticCache(similarity_threshold=0.80)
        
        prompt1 = "Inspect temperature fluctuations in freezer unit 04"
        response_data = {"status": "RESOLVED", "action": "compressor_cycle"}
        
        # Initial miss
        hit, match_type, score = cache.get(prompt1)
        self.assertIsNone(hit)
        
        # Populate cache
        cache.set(prompt1, response_data, tokens_saved=420)
        
        # Exact match
        hit, match_type, score = cache.get(prompt1)
        self.assertIsNotNone(hit)
        self.assertEqual(match_type, "EXACT_HASH_HIT")
        self.assertEqual(score, 1.0)
        
        # Semantic similarity match
        prompt2 = "Inspect temperature fluctuation in freezer unit 04"
        hit2, match_type2, score2 = cache.get(prompt2)
        self.assertIsNotNone(hit2)
        self.assertIn("SIMILARITY", match_type2)
        self.assertGreaterEqual(score2, 0.80)
        
        # Verify metrics
        metrics = cache.get_metrics()
        self.assertEqual(metrics["cache_hits"], 2)
        self.assertEqual(metrics["total_tokens_saved"], 840)

    def test_prompt_compressor(self):
        verbose_telemetry = (
            "Sensor reading:    temperature=-72.4C    \n\n\n"
            "ts=1729665000000   timestamp=1729665000\n"
            '{"status": "active",  "mode": "cooling",  "load": 82}'
        )
        compressed, stats = prompt_compressor.compress(verbose_telemetry)
        
        self.assertLess(len(compressed), len(verbose_telemetry))
        self.assertGreater(stats["reduction_ratio_pct"], 15.0)
        self.assertNotIn("   ", compressed)

    def test_bigquery_exporter_and_schema_validation(self):
        exporter = BigQueryStreamingExporter()
        valid_row = {
            "event_id": "TEST-EVENT-01",
            "timestamp": "2026-10-23T12:00:00Z",
            "domain": "Healthcare Cold-Chain",
            "agent_name": "DiagnosticAgent",
            "action_type": "TEST_ACTION",
            "block_hash": "a" * 64,
            "gcp_project": "test-project"
        }
        self.assertTrue(BigQuerySchemaValidator.validate_row(valid_row))
        
        invalid_row = {
            "event_id": "TEST-MISSING-HASH"
            # Missing required keys
        }
        self.assertFalse(BigQuerySchemaValidator.validate_row(invalid_row))

        # Test streaming buffer and flush
        for i in range(6):
            exporter.buffer_record(
                event_id=f"EVT-{i}",
                domain="Renewable Power Grid",
                agent_name="TestAgent",
                action_type="TEST_TICK",
                threat_score=0.0,
                tokens_used=100,
                latency_ms=25.0,
                decision_payload={"step": i},
                block_hash=f"{i:064x}"
            )
        
        self.assertGreater(exporter.total_rows_exported, 0)

    def test_telemetry_latency_percentiles(self):
        telemetry = efficiency_telemetry
        telemetry.record_request(latency_ms=15.0, input_tokens=100, output_tokens=150, tokens_saved=300)
        telemetry.record_request(latency_ms=45.0, input_tokens=200, output_tokens=250, tokens_saved=400)
        
        stats = telemetry.get_stats()
        self.assertIn("latency", stats)
        self.assertIn("p50_ms", stats["latency"])
        self.assertIn("p95_ms", stats["latency"])
        self.assertIn("p99_ms", stats["latency"])
        self.assertGreater(stats["tokens"]["tokens_saved_by_cache"], 0)
        self.assertGreaterEqual(stats["financial_and_eco"]["co2_avoided_grams"], 0.0)

if __name__ == "__main__":
    unittest.main()
