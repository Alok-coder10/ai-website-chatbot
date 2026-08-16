from time import perf_counter

class MetricsService:

    def __init__(self):
        self.reset()

    def reset(self):
        self.total_requests = 0
        self.total_llm_calls = 0

        self.total_response_time = 0.0
        self.total_llm_time = 0.0

        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0

        self.provider_stats = {}

        self.cache_stats = {}

        self.retrieval_stats = {
            "chroma_time": 0.0,
            "bm25_time": 0.0,
            "reranker_time": 0.0,
            "hybrid_time": 0.0,
            "retrieved_chunks": 0,
            "requests": 0,
        }

        self.conversation_stats = {
            "conversation_turns": 0,
            "memory_hits": 0,
            "summary_hits": 0,
            "prompt_characters": 0,
            "requests": 0,
        }

    def add_conversation_turns(self, count: int):
        self.conversation_stats["conversation_turns"] += count
    
    def add_memory_hit(self):
        self.conversation_stats["memory_hits"] += 1

    def add_summary_hit(self):
        self.conversation_stats["summary_hits"] += 1

    def add_prompt_size(self, size: int):
        self.conversation_stats["prompt_characters"] += size
        self.conversation_stats["requests"] += 1
    
    def add_retrieval_metrics(
        self, name: str, value: float
    ):
        self.retrieval_stats[name] += value

    def add_retrieved_chunks(self, count: int):
        self.retrieval_stats["retrieved_chunks"] += count
        self.retrieval_stats["requests"] += 1


    def request_started(self):
        self.total_requests += 1
        return perf_counter()

    def request_finished(self, start):
        elapsed = perf_counter() - start
        self.total_response_time += elapsed
        return elapsed

    def llm_started(self):
        self.total_llm_calls += 1
        return perf_counter()

    def llm_finished(self, start):
        elapsed = perf_counter() - start
        self.total_llm_time += elapsed
        return elapsed

    def get_stats(self):
        conversation = {
            "avg_conversation_turns": (
                self.conversation_stats["conversation_turns"] /
                self.conversation_stats["requests"]
                if self.conversation_stats["requests"] else 0
            ),
            "memory_hits": self.conversation_stats["memory_hits"],
            "summary_hits": self.conversation_stats["summary_hits"],
            "avg_prompt_size": (
                self.conversation_stats["prompt_characters"] /
                self.conversation_stats["requests"]
                if self.conversation_stats["requests"] else 0
            )
        }


        retrieval= {
            "avg_chroma_time": (
                self.retrieval_stats["chroma_time"] /
                self.retrieval_stats["requests"]
                if self.retrieval_stats["requests"] else 0
            ),
            "avg_bm25_time": (
                self.retrieval_stats["bm25_time"] /
                self.retrieval_stats["requests"]
                if self.retrieval_stats["requests"] else 0
            ),
            "avg_reranker_time": (
                self.retrieval_stats["reranker_time"] /
                self.retrieval_stats["requests"]
                if self.retrieval_stats["requests"] else 0
            ),
            "avg_hybrid_time": (
                self.retrieval_stats["hybrid_time"] /
                self.retrieval_stats["requests"]
                if self.retrieval_stats["requests"] else 0
            ),
            "avg_chunks": (
                self.retrieval_stats["retrieved_chunks"] /
                self.retrieval_stats["requests"]
                if self.retrieval_stats["requests"] else 0
            ),
        }

        
        caches = {}
        for name, data in self.cache_stats.items():

            hits = data["hits"]
            misses = data["misses"]
            total = hits + misses

            caches[name] = {
                "hits": hits,
                "misses": misses,
                "hit_rate": (
                    hits / total
                    if total
                    else 0
                )
            }


        providers = {}
        for name, data in self.provider_stats.items():

            requests = data["requests"]
            providers[name] = {
                "requests": requests,
                "failures": data["failures"],
                "avg_latency": (
                    data["latency"] / requests
                    if requests
                    else 0
                ),
            }

        return {
            "requests": self.total_requests,
            "llm_calls": self.total_llm_calls,
            "avg_response_time": (
                self.total_response_time / self.total_requests
                if self.total_requests
                else 0
            ),
            "avg_llm_time": (
                self.total_llm_time / self.total_llm_calls
                if self.total_llm_calls
                else 0
            ),
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "providers": providers,
            "caches": caches,
            "retrieval": retrieval,
            "conversation": conversation
        }


    def add_token_usage(self, usage: dict):
        self.prompt_tokens += usage.get(
            "prompt_tokens", 0
        )
        self.completion_tokens += usage.get(
            "completion_tokens", 0
        )
        self.total_tokens += usage.get(
            "total_tokens", 0
        )

    def provider_started(self, provider: str):
        if provider not in self.provider_stats:
            self.provider_stats[provider] = {
                "requests": 0,
                "failures": 0,
                "latency": 0.0
            }
        
        self.provider_stats[provider]["requests"] += 1
        
        return perf_counter()

    
    def provider_finished(
        self, provider: str, start_time: float
    ):
        elapsed = perf_counter() - start_time
        self.provider_stats[provider]["latency"] += elapsed

        return elapsed

    def provider_failed(self, provider: str):
        if provider not in self.provider_stats:
            self.provider_stats[provider] = {
                "requests": 0,
                "failures": 0,
                "latency": 0.0
            }

        self.provider_stats[provider]["failures"] += 1

    def cache_access(
        self, cache_name: str, hit: bool
    ):
        if cache_name not in self.cache_stats:
            self.cache_stats[cache_name] = {
                "hits": 0,
                "misses": 0
            }
        
        if hit:
            self.cache_stats[cache_name]["hits"] += 1
        else:
            self.cache_stats[cache_name]["misses"] += 1
    

_metrics_service = None


def get_metrics_service():
    global _metrics_service

    if _metrics_service is None:
        _metrics_service = MetricsService()

    return _metrics_service