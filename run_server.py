import os
import sys
import socket
import uvicorn
from backend.config import config

def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0

def find_available_port(start_port: int = 8080) -> int:
    port = start_port
    while is_port_in_use(port):
        port += 1
    return port

if __name__ == "__main__":
    target_port = config.PORT
    if is_port_in_use(target_port):
        target_port = find_available_port(target_port)

    print("=" * 70)
    print("   AEGISOPS AI: AUTONOMOUS CRITICAL RESILIENCE SENTINEL")
    print("   Engineered for Google Build Beyond AI Hackathon")
    print("=" * 70)
    print(f" • Dashboard URL:        http://{config.HOST}:{target_port}")
    print(f" • Health Probe:         http://{config.HOST}:{target_port}/healthz")
    print(f" • Metrics Stream:       http://{config.HOST}:{target_port}/metrics")
    print(f" • BigQuery Destination: {config.GOOGLE_CLOUD_PROJECT}.{config.BIGQUERY_DATASET}")
    print("=" * 70)
    print("Starting Uvicorn Server...\n")

    uvicorn.run("backend.app:app", host=config.HOST, port=target_port, reload=False)
