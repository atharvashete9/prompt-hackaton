import hashlib
import json
import time
from typing import List, Dict, Any, Optional

class AuditBlock:
    def __init__(
        self,
        index: int,
        timestamp: float,
        agent_name: str,
        action_type: str,
        input_summary: str,
        output_summary: str,
        threat_score: float,
        tokens_used: int,
        previous_hash: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.index = index
        self.timestamp = timestamp
        self.agent_name = agent_name
        self.action_type = action_type
        self.input_summary = input_summary
        self.output_summary = output_summary
        self.threat_score = round(threat_score, 4)
        self.tokens_used = tokens_used
        self.previous_hash = previous_hash
        self.metadata = metadata or {}
        self.block_hash = self.compute_hash()

    def compute_hash(self) -> str:
        payload = {
            "index": self.index,
            "timestamp": self.timestamp,
            "agent_name": self.agent_name,
            "action_type": self.action_type,
            "input_summary": self.input_summary,
            "output_summary": self.output_summary,
            "threat_score": self.threat_score,
            "tokens_used": self.tokens_used,
            "previous_hash": self.previous_hash,
            "metadata": self.metadata
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "iso_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(self.timestamp)),
            "agent_name": self.agent_name,
            "action_type": self.action_type,
            "input_summary": self.input_summary,
            "output_summary": self.output_summary,
            "threat_score": self.threat_score,
            "tokens_used": self.tokens_used,
            "previous_hash": self.previous_hash,
            "block_hash": self.block_hash,
            "metadata": self.metadata
        }

class CryptographicAuditLedger:
    def __init__(self):
        self.chain: List[AuditBlock] = []
        self._create_genesis_block()

    def _create_genesis_block(self):
        genesis = AuditBlock(
            index=0,
            timestamp=time.time(),
            agent_name="SystemGenesis",
            action_type="LEDGER_INITIALIZE",
            input_summary="System initialization and root-of-trust setup",
            output_summary="Genesis block verified. Zero-Trust Audit Ledger operational.",
            threat_score=0.0,
            tokens_used=0,
            previous_hash="0" * 64,
            metadata={"version": "2.4.0", "algorithm": "SHA-256", "authority": "AegisOps-Root-CA"}
        )
        self.chain.append(genesis)

    @property
    def latest_block(self) -> AuditBlock:
        return self.chain[-1]

    def record_event(
        self,
        agent_name: str,
        action_type: str,
        input_summary: str,
        output_summary: str,
        threat_score: float = 0.0,
        tokens_used: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditBlock:
        new_block = AuditBlock(
            index=len(self.chain),
            timestamp=time.time(),
            agent_name=agent_name,
            action_type=action_type,
            input_summary=input_summary,
            output_summary=output_summary,
            threat_score=threat_score,
            tokens_used=tokens_used,
            previous_hash=self.latest_block.block_hash,
            metadata=metadata
        )
        self.chain.append(new_block)
        return new_block

    def verify_chain(self) -> Dict[str, Any]:
        """
        Cryptographically verifies the entire ledger from genesis.
        Returns verification status, block count, and any corrupted block index.
        """
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            prev = self.chain[i - 1]

            # 1. Verify previous hash pointer
            if current.previous_hash != prev.block_hash:
                return {
                    "valid": False,
                    "error": f"Hash chain broken at block {i}: previous_hash does not match parent block hash",
                    "corrupted_block_index": i
                }

            # 2. Recalculate and verify block hash
            recomputed = current.compute_hash()
            if current.block_hash != recomputed:
                return {
                    "valid": False,
                    "error": f"Tampering detected at block {i}: block hash mismatch",
                    "corrupted_block_index": i
                }

        return {
            "valid": True,
            "total_blocks": len(self.chain),
            "latest_hash": self.latest_block.block_hash,
            "verified_at": time.time(),
            "status": "CRYPTOGRAPHICALLY_VERIFIED"
        }

    def tamper_test_simulate(self, block_index: int, fake_output: str) -> bool:
        """Helper to simulate an adversary altering historical logs (for demo verification)."""
        if 0 <= block_index < len(self.chain):
            if not hasattr(self, "_tamper_backups"):
                self._tamper_backups = {}
            if block_index not in self._tamper_backups:
                self._tamper_backups[block_index] = self.chain[block_index].output_summary
            self.chain[block_index].output_summary = fake_output
            return True
        return False

    def restore_block(self, block_index: int):
        """Restores original text and re-computes correct hash."""
        if hasattr(self, "_tamper_backups") and block_index in self._tamper_backups:
            self.chain[block_index].output_summary = self._tamper_backups[block_index]
            del self._tamper_backups[block_index]
        if 0 <= block_index < len(self.chain):
            self.chain[block_index].block_hash = self.chain[block_index].compute_hash()

    def get_recent(self, limit: int = 50) -> List[Dict[str, Any]]:
        return [b.to_dict() for b in self.chain[-limit:]]

# Singleton instance
audit_ledger = CryptographicAuditLedger()
