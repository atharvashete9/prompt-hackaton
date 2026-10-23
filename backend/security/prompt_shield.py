import re
import base64
from typing import Dict, List, Any, Tuple
from backend.config import config

class PromptShield:
    def __init__(self):
        # Known jailbreak and prompt injection signatures
        self.attack_patterns = [
            (r"ignore\s+(?:all\s+)?(?:previous|prior)\s+(?:instructions|rules|guidelines)", "DIRECT_INSTRUCTION_OVERRIDE", 0.95),
            (r"you\s+are\s+(?:now\s+)?(?:DAN|unrestricted|jailbroken|godmode|root)", "ROLE_USURPATION_JAILBREAK", 0.95),
            (r"(?:disregard|forget)\s+(?:all\s+)?safety\s+(?:protocols|checks|filters)", "SAFETY_BYPASS_ATTEMPT", 0.90),
            (r"(?:reveal|print|output|display)\s+(?:system\s+prompt|initial\s+prompt|developer\s+instructions)", "SYSTEM_PROMPT_LEAK_ATTEMPT", 0.85),
            (r"base64\s*(?:decode|eval|exec)", "OBFUSCATED_PAYLOAD_EXECUTION", 0.80),
            (r"i\s+am\s+(?:the\s+)?(?:lead\s+developer|root\s+administrator|system\s+operator|ceo)\b", "AUTHORITY_IMPERSONATION", 0.75),
            (r"(?:curl|wget|nc|bash|sh|powershell|cmd\.exe)\s+-[a-zA-Z]", "SHELL_INJECTION_PATTERN", 0.90),
            (r"bypass\s+(?:rbac|auth|permission|approval|killswitch)", "SECURITY_CONTROL_EVASION", 0.90),
            (r"simulate\s+(?:unauthorized|illegal|destructive)\s+override", "ADVERSARIAL_SIMULATION", 0.70),
            (r"<\s*script\b[^>]*>.*?<\s*/\s*script\s*>", "XSS_SCRIPT_INJECTION", 0.85)
        ]

    def decode_obfuscated_strings(self, text: str) -> List[str]:
        """Detect and decode potential base64 embedded payloads for deep inspection."""
        decoded_snippets = []
        # Find potential base64 blocks (min 16 chars)
        b64_candidates = re.findall(r"[A-Za-z0-9+/]{16,}={0,2}", text)
        for cand in b64_candidates:
            try:
                dec = base64.b64decode(cand, validate=True).decode("utf-8", errors="ignore")
                if len(dec) > 4 and any(c.isalnum() for c in dec):
                    decoded_snippets.append(dec)
            except Exception:
                continue
        return decoded_snippets

    def inspect(self, prompt: str) -> Dict[str, Any]:
        """
        Multi-layered inspection of input prompt:
        - Length validation
        - Regex heuristic signatures
        - Embedded payload decoding & analysis
        - Canary token check
        - Comprehensive risk calculation
        """
        if not prompt or not prompt.strip():
            return {
                "safe": True,
                "threat_score": 0.0,
                "action": "ALLOW",
                "detected_vectors": [],
                "reason": "Empty prompt passed"
            }

        detected_vectors = []
        max_threat_score = 0.0

        # 1. Length check
        if len(prompt) > config.MAX_PROMPT_LENGTH:
            detected_vectors.append({
                "vector": "BUFFER_OVERFLOW_RISK",
                "score": 0.75,
                "detail": f"Prompt length ({len(prompt)}) exceeds security limit ({config.MAX_PROMPT_LENGTH})"
            })
            max_threat_score = max(max_threat_score, 0.75)

        # 2. Canary Token Check
        # If user is asking for the canary token or trying to verify it illegitimately
        if config.CANARY_TOKEN.lower() in prompt.lower():
            detected_vectors.append({
                "vector": "CANARY_TOKEN_EXTRACTION",
                "score": 0.99,
                "detail": "Adversarial probe detected querying internal canary signature"
            })
            max_threat_score = max(max_threat_score, 0.99)

        # 3. Direct Pattern Matching
        normalized_prompt = prompt.lower()
        for pattern, vector_name, score in self.attack_patterns:
            if re.search(pattern, normalized_prompt, re.IGNORECASE):
                detected_vectors.append({
                    "vector": vector_name,
                    "score": score,
                    "detail": f"Pattern matched: {pattern}"
                })
                max_threat_score = max(max_threat_score, score)

        # 4. Obfuscation & Base64 Inspection
        decoded_payloads = self.decode_obfuscated_strings(prompt)
        for dec in decoded_payloads:
            for pattern, vector_name, score in self.attack_patterns:
                if re.search(pattern, dec, re.IGNORECASE):
                    detected_vectors.append({
                        "vector": f"OBFUSCATED_{vector_name}",
                        "score": min(score + 0.05, 1.0),
                        "detail": f"Hidden base64 payload contained: {pattern}"
                    })
                    max_threat_score = max(max_threat_score, min(score + 0.05, 1.0))

        # Decision Logic
        is_safe = max_threat_score < config.PROMPT_INJECTION_THRESHOLD
        action = "ALLOW" if is_safe else ("QUARANTINE" if max_threat_score < 0.85 else "REJECT")

        return {
            "safe": is_safe,
            "threat_score": round(max_threat_score, 3),
            "action": action,
            "detected_vectors": detected_vectors,
            "canary_verified": True,
            "reason": "Passed security filters" if is_safe else f"High risk detected: {len(detected_vectors)} attack vectors triggered"
        }

    def sanitize(self, text: str) -> str:
        """Sanitizes text by stripping harmful control characters and delimiter manipulation."""
        # Strip null bytes and non-printable control chars except standard newlines/tabs
        sanitized = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)
        return sanitized

prompt_shield = PromptShield()
