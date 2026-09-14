"""
AgentOps Observatory - High-Throughput Load Tester (Phase 12+)
Benchmarks async ingestion throughput (events/sec) and latency percentiles (p50, p95, p99).
"""

import asyncio
import time
from uuid import uuid4
from backend.app.models.db import init_db
from backend.app.services.storage import IngestionService


async def run_load_test(num_events: int = 1000):
    print(f"Starting High-Throughput Ingestion Benchmark ({num_events} events)...")
    await init_db()
    ingestion = IngestionService()

    latencies = []
    start_all = time.time()

    for i in range(num_events):
        t0 = time.time()
        ev = {
            "event_id": f"load-bench-{uuid4().hex[:12]}",
            "run_id": f"run-bench-{i % 50}",
            "source": "agent",
            "actor": "load-tester",
            "tool_or_model_name": "search_web",
            "tool_name": "search_web",
            "arguments_redacted": {"q": f"benchmark item {i}"},
            "duration_ms": 10.0,
            "status": "success"
        }
        await ingestion.ingest_event(ev)
        latencies.append((time.time() - t0) * 1000.0)

    total_time = time.time() - start_all
    throughput = num_events / total_time

    latencies.sort()
    p50 = latencies[int(len(latencies) * 0.50)]
    p95 = latencies[int(len(latencies) * 0.95)]
    p99 = latencies[int(len(latencies) * 0.99)]

    print("=" * 60)
    print(f"Total Events Ingested:    {num_events}")
    print(f"Total Execution Time:     {total_time:.2f} s")
    print(f"Throughput:               {throughput:.1f} events/sec")
    print(f"Latency (p50):            {p50:.2f} ms")
    print(f"Latency (p95):            {p95:.2f} ms")
    print(f"Latency (p99):            {p99:.2f} ms")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_load_test(1000))
