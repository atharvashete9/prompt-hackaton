from typing import Dict, Any, Tuple
from backend.security.prompt_shield import prompt_shield
from backend.security.pii_masker import pii_masker
from backend.security.rbac import rbac

class ZeroTrustGuardAgent:
    NAME = "ZeroTrustGuardAgent"

    def pre_screen_input(self, user_prompt: str, user_role: str = "operator") -> Dict[str, Any]:
        """
        Executes zero-trust pre-screening:
        1. Prompt injection & jailbreak detection
        2. PII detection and redaction
        3. Role-based permission verification
        """
        # Step 1: Prompt Shield analysis
        shield_result = prompt_shield.inspect(user_prompt)

        # Step 2: PII Redaction
        sanitized_text, redactions = pii_masker.mask(user_prompt)
        sanitized_text = prompt_shield.sanitize(sanitized_text)

        # Step 3: RBAC check
        has_permission = rbac.check_permission(user_role, "view_telemetry_and_audits")

        status = "PASSED"
        if not shield_result["safe"]:
            status = "BLOCKED" if shield_result["action"] == "REJECT" else "QUARANTINED"

        return {
            "agent": self.NAME,
            "status": status,
            "threat_score": shield_result["threat_score"],
            "action": shield_result["action"],
            "detected_vectors": shield_result["detected_vectors"],
            "sanitized_input": sanitized_text,
            "pii_redactions": redactions,
            "rbac_verified": has_permission,
            "canary_intact": shield_result.get("canary_verified", True)
        }

guard_agent = ZeroTrustGuardAgent()
