import re
from typing import Dict, Any, Tuple, List

class PIIMasker:
    def __init__(self):
        self.rules = [
            (r"\b\d{3}-\d{2}-\d{4}\b", "[REDACTED_SSN]", "SSN"),
            (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[REDACTED_EMAIL]", "EMAIL"),
            (r"\b(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})\b", "[REDACTED_PHONE]", "PHONE"),
            (r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b", "[REDACTED_CREDIT_CARD]", "CREDIT_CARD"),
            (r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b", "[REDACTED_IP]", "IP_ADDRESS"),
            (r"\b(?:MRN|PATIENT-ID|HCID)[:#\s]+[A-Z0-9-]{6,12}\b", "[REDACTED_PATIENT_MRN]", "HEALTHCARE_MRN")
        ]

    def mask(self, text: str) -> Tuple[str, List[Dict[str, Any]]]:
        redacted_text = text
        redactions = []

        for pattern, placeholder, pii_type in self.rules:
            matches = list(re.finditer(pattern, redacted_text, re.IGNORECASE))
            if matches:
                # Iterate in reverse to preserve span offsets
                for match in reversed(matches):
                    val = match.group(0)
                    start, end = match.span()
                    redacted_text = redacted_text[:start] + placeholder + redacted_text[end:]
                    redactions.append({
                        "type": pii_type,
                        "placeholder": placeholder,
                        "length": len(val)
                    })

        return redacted_text, redactions

pii_masker = PIIMasker()
