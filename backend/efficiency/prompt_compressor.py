import re
import json
from typing import Dict, Any, Tuple

class PromptCompressor:
    """
    Compresses telemetry and conversational context to minimize token consumption
    while preserving vital semantic anchors and numerical values.
    """
    @staticmethod
    def compress(text: str) -> Tuple[str, Dict[str, Any]]:
        original_length = len(text)
        if not text:
            return "", {"original_chars": 0, "compressed_chars": 0, "reduction_ratio_pct": 0.0}

        # 1. Normalize excessive whitespace and blank lines
        compressed = re.sub(r"[ \t]+", " ", text)
        compressed = re.sub(r"\n\s*\n+", "\n", compressed)

        # 2. Compress repetitive key-value logs
        compressed = re.sub(r"(timestamp|ts)=\d{10,13}", "", compressed)

        # 3. Compact JSON blocks if present
        def json_compact(match):
            try:
                obj = json.loads(match.group(0))
                return json.dumps(obj, separators=(",", ":"))
            except Exception:
                return match.group(0)

        compressed = re.sub(r"\{[^{}]*\}", json_compact, compressed)

        compressed_length = len(compressed)
        ratio = round((1.0 - (compressed_length / original_length)) * 100, 2) if original_length > 0 else 0.0

        return compressed.strip(), {
            "original_chars": original_length,
            "compressed_chars": compressed_length,
            "reduction_ratio_pct": max(ratio, 0.0),
            "tokens_saved_estimate": max(int((original_length - compressed_length) / 4), 0)
        }

prompt_compressor = PromptCompressor()
