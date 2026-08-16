from httpx import request
from app.services.metrics_service import get_metrics_service
from app.models.conversation import Conversation

class DashboardService:
    def __init__(self):
        self.metrics = get_metrics_service()

    def get_dashboard(self):
        stats = self.metrics.get_stats()

        request_stats = {
            "total_requests": stats["requests"],
            "total_llm_calls": stats["llm_calls"],
            "avg_response_time_ms": round(stats["avg_response_time"] * 1000, 2),
            "avg_llm_time_ms": round(stats["avg_llm_time"] * 1000, 2),
            "prompt_tokens": stats["prompt_tokens"],
            "completion_tokens": stats["completion_tokens"],
            "total_tokens": stats["total_tokens"],
            "avg_tokens_per_request": (
                round(stats["total_tokens"] / stats["requests"], 2)
                if stats["requests"] else 0
            ),
            "llm_calls_per_request": (
                round(stats["llm_calls"] / stats['requests'], 2)
                if stats["requests"] else 0
            )
        }

        provider_stats = {}
        for provider, data in stats["providers"].items():
            requests = data["requests"]
            failures = data["failures"]
            success = requests - failures
            provider_stats[provider] = {
                "requests": requests,
                "successes": success,
                "failures": failures,
                "success_rate": (
                    round(success / requests *100, 2)
                    if requests else 100
                ),
                "failure_rate": (
                    round(failures / requests *100, 2)
                    if requests else 0
                ),
                "avg_latency_ms": round(data["avg_latency"] * 1000, 2)
            }

        cache_stats = {}
        for cache_name, data in stats["caches"].items():
            hits = data["hits"]
            misses = data["misses"]
            total = hits + misses

            cache_stats[cache_name] = {
                "hits": hits,
                "misses": misses,
                "requests": total,
                "hit_rate": round(
                    data["hit_rate"]*100, 2
                ),
                "miss_rate": round(
                    (100 - data["hit_rate"] *100), 2
                ),
                "status": (
                    "Excellent" if data["hit_rate"] >= 0.90
                    else "Good"
                    if data["hit_rate"] >= 0.70
                    else "Needs Improvement"
                )

            }
        

        retrieval_stats = {
            "avg_chroma_ms": round(
                stats["retrieval"]["avg_chroma_time"] * 1000, 2
            ),
            "avg_bm25_ms": round(
                stats["retrieval"]["avg_bm25_time"] * 1000, 2
            ),
            "avg_reranker_ms": round(
                stats["retrieval"]["avg_reranker_time"] * 1000, 2
            ),
            "avg_hybrid_ms": round(
                stats["retrieval"]["avg_hybrid_time"] * 1000, 2
            ),
            "avg_chunks": round(
                stats["retrieval"]["avg_chunks"], 2
            )
        }

        conversation_stats = {
            "avg_conversation_turns": round(
                stats["conversation"]["avg_conversation_turns"], 2
            ),
            "memory_hits": stats["conversation"]["memory_hits"],
            "summary_hits": stats["conversation"]["summary_hits"],
            "avg_prompt_size": round(
                stats["conversation"]["avg_prompt_size"], 2
            ),
            "memory_usage": (
                "Enabled"
                if stats["conversation"]["memory_hits"] >0
                else "Unused"
            ),
            "summary_usage": (
                "Enabled"
                if stats["conversation"]["summary_hits"] > 0
                else "Unused"
            )
        }

        overall_cache_requests = 0
        overall_cache_hits = 0

        for cache in stats["caches"].values():
            overall_cache_hits += cache["hits"]
            overall_cache_requests += (
                cache["hits"] + cache["misses"]
            )
        
        overall_cache_hit_rate = (
            round(overall_cache_hits / overall_cache_requests *100, 2)
            if overall_cache_requests else 0
        )
        
        summary = {
            "status": "Healthy",
            "requests": stats["requests"],
            "providers": len(stats["providers"]),
            "caches": len(stats["caches"]),
            "avg_response_ms": round(stats["avg_response_time"]*1000, 2),
            "cache_hit_rate": overall_cache_hit_rate,
            "total_tokens": stats["total_tokens"],
            "provider_failures": sum(
                provider["failures"]
                for provider in stats["providers"].values()
            ),
            "retrieval_enabled": True,
            "memory_ennabled": True
        }


        return {
            "requests": request_stats,
            "providers": provider_stats,
            "caches": cache_stats,
            "retrieval": retrieval_stats,
            "conversation": conversation_stats,
            "summary": summary,
        }


_dashboard = None

def get_dashboard_service():
    global _dashboard
    if _dashboard is None:
        _dashboard = DashboardService()

    return _dashboard