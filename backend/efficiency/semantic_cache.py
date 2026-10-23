import time
import hashlib
from typing import Dict, Any, Optional, Tuple, List

class SemanticCacheEntry:
    def __init__(self, key: str, prompt: str, response: Dict[str, Any], tokens_saved: int, ttl: int = 3600):
        self.key = key
        self.prompt = prompt
        self.response = response
        self.tokens_saved = tokens_saved
        self.created_at = time.time()
        self.expires_at = self.created_at + ttl
        self.hit_count = 0

class SemanticCache:
    def __init__(self, similarity_threshold: float = 0.88, ttl_seconds: int = 3600):
        self.cache: Dict[str, SemanticCacheEntry] = {}
        self.similarity_threshold = similarity_threshold
        self.ttl_seconds = ttl_seconds
        self.total_queries = 0
        self.cache_hits = 0
        self.total_tokens_saved = 0

    def _hash_key(self, text: str) -> str:
        return hashlib.sha256(text.strip().lower().encode("utf-8")).hexdigest()

    def _tokenize(self, text: str) -> set:
        words = text.lower().replace("\n", " ").split()
        tokens = set(w for w in words if len(w) > 2)
        # Also include character 3-grams for stem/plural invariance
        trigrams = set()
        for w in words:
            if len(w) >= 3:
                for i in range(len(w) - 2):
                    trigrams.add(w[i:i+3])
        return tokens.union(trigrams)

    def _jaccard_similarity(self, tokens1: set, tokens2: set) -> float:
        if not tokens1 or not tokens2:
            return 0.0
        intersection = len(tokens1.intersection(tokens2))
        union = len(tokens1.union(tokens2))
        return intersection / union if union > 0 else 0.0

    def get(self, prompt: str) -> Tuple[Optional[Dict[str, Any]], Optional[str], float]:
        """
        Check cache for exact match or high semantic similarity.
        Returns (response, match_type, similarity_score).
        """
        self.total_queries += 1
        now = time.time()

        # 1. Exact match via SHA256 key
        exact_key = self._hash_key(prompt)
        if exact_key in self.cache:
            entry = self.cache[exact_key]
            if now < entry.expires_at:
                entry.hit_count += 1
                self.cache_hits += 1
                self.total_tokens_saved += entry.tokens_saved
                return entry.response, "EXACT_HASH_HIT", 1.0
            else:
                del self.cache[exact_key]

        # 2. Semantic token similarity
        prompt_tokens = self._tokenize(prompt)
        best_match: Optional[SemanticCacheEntry] = None
        highest_sim = 0.0

        for entry in list(self.cache.values()):
            if now >= entry.expires_at:
                continue
            sim = self._jaccard_similarity(prompt_tokens, self._tokenize(entry.prompt))
            if sim > highest_sim:
                highest_sim = sim
                best_match = entry

        if best_match and highest_sim >= self.similarity_threshold:
            best_match.hit_count += 1
            self.cache_hits += 1
            self.total_tokens_saved += best_match.tokens_saved
            return best_match.response, "SEMANTIC_SIMILARITY_HIT", round(highest_sim, 3)

        return None, None, 0.0

    def set(self, prompt: str, response: Dict[str, Any], tokens_saved: int):
        key = self._hash_key(prompt)
        self.cache[key] = SemanticCacheEntry(
            key=key,
            prompt=prompt,
            response=response,
            tokens_saved=tokens_saved,
            ttl=self.ttl_seconds
        )

    def get_metrics(self) -> Dict[str, Any]:
        hit_ratio = (self.cache_hits / self.total_queries) if self.total_queries > 0 else 0.0
        return {
            "total_queries": self.total_queries,
            "cache_hits": self.cache_hits,
            "cache_misses": self.total_queries - self.cache_hits,
            "hit_ratio_percent": round(hit_ratio * 100, 2),
            "cached_entries_count": len(self.cache),
            "total_tokens_saved": self.total_tokens_saved
        }

semantic_cache = SemanticCache()
