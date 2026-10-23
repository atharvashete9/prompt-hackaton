import time
import random
from typing import Dict, Any, List

class TelemetryGenerator:
    def __init__(self):
        self.current_scenario = "healthcare_coldchain"
        self.anomaly_active = False
        self.anomaly_type = None
        self.sequence_number = 0

        # Base baseline states
        self.state_coldchain = {
            "facility_id": "VAX-HUB-NORTH-7",
            "freezer_temp_c": -72.4,
            "target_temp_c": -70.0,
            "ambient_temp_c": 21.5,
            "backup_battery_pct": 98.4,
            "grid_power_voltage": 240.2,
            "compressor_pressure_psi": 142.1,
            "door_sealed": True,
            "vial_inventory_count": 18450,
            "risk_index": 0.04
        }

        self.state_grid = {
            "substation_id": "SUB-RENEWABLE-SOLAR-09",
            "grid_frequency_hz": 60.01,
            "inverter_efficiency_pct": 96.8,
            "transformer_temp_c": 54.2,
            "battery_storage_mwh": 14.8,
            "line_load_pct": 68.2,
            "scada_integrity_status": "SECURE",
            "risk_index": 0.02
        }

        self.state_cloud = {
            "cluster_id": "GCP-RUN-CLUSTER-US-CENTRAL",
            "requests_per_sec": 3850,
            "p95_latency_ms": 34.2,
            "error_rate_pct": 0.01,
            "cpu_utilization_pct": 52.4,
            "token_budget_remaining": 894000,
            "firewall_drop_count": 14,
            "risk_index": 0.03
        }

    def set_scenario(self, scenario_name: str):
        if scenario_name in ["healthcare_coldchain", "smart_grid", "cloud_infra"]:
            self.current_scenario = scenario_name
            self.anomaly_active = False
            self.anomaly_type = None

    def trigger_anomaly(self, anomaly_type: str = "THERMAL_FAILURE"):
        self.anomaly_active = True
        self.anomaly_type = anomaly_type

    def clear_anomaly(self):
        self.anomaly_active = False
        self.anomaly_type = None

    def generate_next_tick(self) -> Dict[str, Any]:
        self.sequence_number += 1
        ts = time.time()

        if self.current_scenario == "healthcare_coldchain":
            if self.anomaly_active:
                # Critical thermal rise in freezer
                self.state_coldchain["freezer_temp_c"] = round(min(self.state_coldchain["freezer_temp_c"] + random.uniform(1.2, 2.5), -38.0), 1)
                self.state_coldchain["compressor_pressure_psi"] = round(max(self.state_coldchain["compressor_pressure_psi"] - 6.5, 30.0), 1)
                self.state_coldchain["risk_index"] = round(min(self.state_coldchain["risk_index"] + 0.15, 0.96), 2)
                if self.anomaly_type == "POWER_OUTAGE":
                    self.state_coldchain["grid_power_voltage"] = 0.0
                    self.state_coldchain["backup_battery_pct"] = max(self.state_coldchain["backup_battery_pct"] - 1.5, 12.0)
            else:
                # Regulate gently back to safe state
                if self.state_coldchain["freezer_temp_c"] > -70.0:
                    self.state_coldchain["freezer_temp_c"] = round(max(self.state_coldchain["freezer_temp_c"] - 1.8, -72.0), 1)
                else:
                    self.state_coldchain["freezer_temp_c"] = round(-71.5 + random.uniform(-0.5, 0.5), 1)
                self.state_coldchain["compressor_pressure_psi"] = round(140.0 + random.uniform(-2.0, 2.0), 1)
                self.state_coldchain["grid_power_voltage"] = round(240.0 + random.uniform(-1.0, 1.0), 1)
                self.state_coldchain["risk_index"] = round(max(self.state_coldchain["risk_index"] - 0.08, 0.03), 2)

            return {
                "sequence": self.sequence_number,
                "timestamp": ts,
                "domain": "Healthcare Cold-Chain",
                "scenario": self.current_scenario,
                "anomaly_active": self.anomaly_active,
                "anomaly_type": self.anomaly_type,
                "metrics": dict(self.state_coldchain),
                "status": "CRITICAL" if self.state_coldchain["risk_index"] > 0.70 else ("WARNING" if self.state_coldchain["risk_index"] > 0.35 else "NOMINAL")
            }

        elif self.current_scenario == "smart_grid":
            if self.anomaly_active:
                self.state_grid["grid_frequency_hz"] = round(max(self.state_grid["grid_frequency_hz"] - random.uniform(0.12, 0.25), 58.7), 2)
                self.state_grid["transformer_temp_c"] = round(min(self.state_grid["transformer_temp_c"] + random.uniform(2.0, 4.0), 98.0), 1)
                self.state_grid["risk_index"] = round(min(self.state_grid["risk_index"] + 0.16, 0.98), 2)
            else:
                if self.state_grid["grid_frequency_hz"] < 59.95:
                    self.state_grid["grid_frequency_hz"] = round(min(self.state_grid["grid_frequency_hz"] + 0.15, 60.00), 2)
                else:
                    self.state_grid["grid_frequency_hz"] = round(60.00 + random.uniform(-0.02, 0.02), 2)
                self.state_grid["transformer_temp_c"] = round(54.0 + random.uniform(-1.0, 1.0), 1)
                self.state_grid["risk_index"] = round(max(self.state_grid["risk_index"] - 0.09, 0.02), 2)

            return {
                "sequence": self.sequence_number,
                "timestamp": ts,
                "domain": "Renewable Power Grid",
                "scenario": self.current_scenario,
                "anomaly_active": self.anomaly_active,
                "anomaly_type": self.anomaly_type,
                "metrics": dict(self.state_grid),
                "status": "CRITICAL" if self.state_grid["risk_index"] > 0.70 else ("WARNING" if self.state_grid["risk_index"] > 0.35 else "NOMINAL")
            }

        else: # cloud_infra
            if self.anomaly_active:
                self.state_cloud["requests_per_sec"] += random.randint(1500, 3500)
                self.state_cloud["p95_latency_ms"] = round(min(self.state_cloud["p95_latency_ms"] + 120.0, 850.0), 1)
                self.state_cloud["error_rate_pct"] = round(min(self.state_cloud["error_rate_pct"] + 2.5, 18.4), 2)
                self.state_cloud["risk_index"] = round(min(self.state_cloud["risk_index"] + 0.18, 0.99), 2)
            else:
                self.state_cloud["requests_per_sec"] = random.randint(3200, 4100)
                self.state_cloud["p95_latency_ms"] = round(32.0 + random.uniform(-3.0, 5.0), 1)
                self.state_cloud["error_rate_pct"] = round(0.01 + random.uniform(0.0, 0.02), 2)
                self.state_cloud["risk_index"] = round(max(self.state_cloud["risk_index"] - 0.10, 0.03), 2)

            return {
                "sequence": self.sequence_number,
                "timestamp": ts,
                "domain": "Cloud Infrastructure",
                "scenario": self.current_scenario,
                "anomaly_active": self.anomaly_active,
                "anomaly_type": self.anomaly_type,
                "metrics": dict(self.state_cloud),
                "status": "CRITICAL" if self.state_cloud["risk_index"] > 0.70 else ("WARNING" if self.state_cloud["risk_index"] > 0.35 else "NOMINAL")
            }

telemetry_stream = TelemetryGenerator()
