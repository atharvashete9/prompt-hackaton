import os
from typing import Dict, Any

class Config:
    PROJECT_NAME = "AegisOps AI"
    VERSION = "2.4.0-enterprise"
    ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 8080))
    
    # Google Gemini & Cloud Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "aegisops-resilience-prod")
    BIGQUERY_DATASET = os.getenv("BIGQUERY_DATASET", "aegisops_telemetry_audit")
    BIGQUERY_TABLE = os.getenv("BIGQUERY_TABLE", "agent_decisions_v1")
    
    # Security Configuration
    CANARY_TOKEN = "AEGIS-SEC-VERIFY-9924-X"
    PROMPT_INJECTION_THRESHOLD = 0.65  # Threat score threshold 0.0 - 1.0
    ENABLE_STRICT_RBAC = True
    MAX_PROMPT_LENGTH = 8192
    
    # Efficiency & Cache Configuration
    SEMANTIC_CACHE_ENABLED = True
    CACHE_SIMILARITY_THRESHOLD = 0.88
    CACHE_TTL_SECONDS = 3600
    COST_PER_1K_INPUT_TOKENS = 0.00015  # Gemini 2.5 Flash rate
    COST_PER_1K_OUTPUT_TOKENS = 0.00060
    ESTIMATED_CO2_GRAMS_PER_1K_TOKENS = 0.025  # Grams of CO2 equivalent
    
    # Telemetry Simulation Defaults
    STREAM_INTERVAL_SECONDS = 2.5
    ANOMALY_TRIGGER_INTERVAL = 15

config = Config()
