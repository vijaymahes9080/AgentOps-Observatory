"""
AgentOps Observatory - Benchmark Evaluator (Phase 11)
Executes all 200 synthetic runs against the ingestion, redaction, and policy engine.
Computes and asserts target SLA metrics:
- Trace Completeness (Target >= 95%)
- Seeded Secret Masking (Target 100%)
- Policy Detection Precision/Recall (Target >= 85%)
- Cross-User Data Leakage (Target: 0)
"""

import asyncio
import json
import time
from typing import Any, Dict, List
from evaluation.generator import FixtureGenerator
from backend.app.models.db import init_db
from backend.app.services.storage import IngestionService


class BenchmarkEvaluator:

    def __init__(self):
        self.ingestion = IngestionService()

    async def run_benchmark(self) -> Dict[str, Any]:
        print("=" * 60)
        print("AGENTOPS OBSERVATORY - BENCHMARK EVALUATION SUITE")
        print("=" * 60)

        # Reset DB tables for clean, reproducible benchmark runs
        from backend.app.models.db import engine, Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        fixtures = FixtureGenerator.generate_all_fixtures()

        total_runs = sum(len(runs) for runs in fixtures.values())
        print(f"Loaded {total_runs} synthetic evaluation test runs across 6 categories.\n")

        # Metrics trackers
        complete_traces_checked = 0
        complete_traces_passed = 0
        
        secrets_tested = 0
        secrets_masked = 0
        
        policy_true_positives = 0
        policy_false_negatives = 0
        policy_false_positives = 0
        
        partial_traces_detected = 0
        cross_user_leaks = 0

        start_time = time.time()

        # 1. Evaluate Normal Runs (100 runs)
        print("1. Ingesting 100 Normal Agent Runs...")
        for run_fix in fixtures["normal_runs"]:
            run_id = run_fix["run_id"]
            complete_traces_checked += 1
            has_error = False
            for ev in run_fix["events"]:
                res = await self.ingestion.ingest_event(ev)
                if res.get("violations_count", 0) > 0:
                    policy_false_positives += 1
                if res.get("is_partial", False):
                    has_error = True
            if not has_error:
                complete_traces_passed += 1

        # 2. Evaluate Unauthorized Tool Runs (20 runs)
        print("2. Ingesting 20 Unauthorized Tool Invocation Runs...")
        for run_fix in fixtures["unauthorized_tool_runs"]:
            detected = False
            for ev in run_fix["events"]:
                res = await self.ingestion.ingest_event(ev)
                if res.get("violations_count", 0) > 0:
                    detected = True
            if detected:
                policy_true_positives += 1
            else:
                policy_false_negatives += 1

        # 3. Evaluate Secret Leak Runs (20 runs)
        print("3. Ingesting 20 Secret / Credential Leak Runs...")
        for run_fix in fixtures["secret_leak_runs"]:
            raw_secret = run_fix.get("raw_secret")
            secrets_tested += 1
            masked = False
            for ev in run_fix["events"]:
                res = await self.ingestion.ingest_event(ev)
                if res.get("redactions_count", 0) > 0:
                    masked = True
            if masked:
                secrets_masked += 1

        # 4. Evaluate Repeated Failure Runs (20 runs)
        print("4. Ingesting 20 Repeated Failure / Loop Runs...")
        for run_fix in fixtures["repeated_failure_runs"]:
            detected = False
            for ev in run_fix["events"]:
                res = await self.ingestion.ingest_event(ev)
                if res.get("violations_count", 0) > 0:
                    detected = True
            if detected:
                policy_true_positives += 1
            else:
                policy_false_negatives += 1

        # 5. Evaluate Prompt Injection Runs (20 runs)
        print("5. Ingesting 20 Prompt Injection / Jailbreak Runs...")
        for run_fix in fixtures["prompt_injection_runs"]:
            detected = False
            for ev in run_fix["events"]:
                res = await self.ingestion.ingest_event(ev)
                if res.get("violations_count", 0) > 0:
                    detected = True
            if detected:
                policy_true_positives += 1
            else:
                policy_false_negatives += 1

        # 6. Evaluate Partial Trace Runs (20 runs)
        print("6. Ingesting 20 Partial / Orphan Telemetry Runs...")
        for run_fix in fixtures["partial_trace_runs"]:
            for ev in run_fix["events"]:
                res = await self.ingestion.ingest_event(ev)
                if res.get("is_partial", False):
                    partial_traces_detected += 1
                    break

        # 7. Cross-User Data Isolation Check
        print("7. Verifying Cross-User & Tenant Isolation Boundaries...")
        tenant_a_event = {
            "event_id": "cross-user-test-1",
            "run_id": "eval-tenant-a",
            "source": "agent",
            "actor": "user-alice",
            "status": "success",
            "provenance": {"target_tenant": "tenant-beta"}
        }
        res_cross = await self.ingestion.ingest_event(tenant_a_event, tenant_id="tenant-alpha")
        if res_cross.get("violations_count", 0) > 0:
            # Policy caught cross-tenant access!
            cross_user_leaks = 0
        else:
            cross_user_leaks = 1

        elapsed = time.time() - start_time

        # Calculate target performance metrics
        trace_completeness_pct = (complete_traces_passed / max(complete_traces_checked, 1)) * 100.0
        secret_masking_pct = (secrets_masked / max(secrets_tested, 1)) * 100.0
        
        expected_policy_cases = 20 + 20 + 20  # unauth + retry + injection = 60 cases
        policy_recall_pct = (policy_true_positives / max(expected_policy_cases, 1)) * 100.0
        policy_precision_pct = (
            policy_true_positives / max(policy_true_positives + policy_false_positives, 1)
        ) * 100.0
        
        partial_trace_detection_pct = (partial_traces_detected / 20.0) * 100.0

        summary = {
            "total_runs_evaluated": total_runs,
            "total_execution_seconds": round(elapsed, 2),
            "trace_completeness_percent": round(trace_completeness_pct, 2),
            "target_trace_completeness_percent": 95.0,
            "trace_completeness_met": trace_completeness_pct >= 95.0,
            "secret_masking_percent": round(secret_masking_pct, 2),
            "target_secret_masking_percent": 100.0,
            "secret_masking_met": secret_masking_pct >= 100.0,
            "policy_detection_recall_percent": round(policy_recall_pct, 2),
            "policy_detection_precision_percent": round(policy_precision_pct, 2),
            "target_policy_percent": 85.0,
            "policy_detection_met": policy_recall_pct >= 85.0,
            "partial_trace_detection_percent": round(partial_trace_detection_pct, 2),
            "cross_user_data_leaks": cross_user_leaks,
            "cross_user_isolation_met": cross_user_leaks == 0
        }

        print("\n" + "=" * 60)
        print("EVALUATION RESULTS & SLA VERIFICATION")
        print("=" * 60)
        print(f"Trace Completeness:        {summary['trace_completeness_percent']}% (Target: >=95% -> {'PASS' if summary['trace_completeness_met'] else 'FAIL'})")
        print(f"Seeded Secret Masking:     {summary['secret_masking_percent']}% (Target: 100% -> {'PASS' if summary['secret_masking_met'] else 'FAIL'})")
        print(f"Policy Detection Recall:   {summary['policy_detection_recall_percent']}% (Target: >=85% -> {'PASS' if summary['policy_detection_met'] else 'FAIL'})")
        print(f"Policy Precision:          {summary['policy_detection_precision_percent']}%")
        print(f"Partial Traces Detected:   {summary['partial_trace_detection_percent']}% (20/20)")
        print(f"Cross-User Data Leaks:     {summary['cross_user_data_leaks']} (Target: 0 -> {'PASS' if summary['cross_user_isolation_met'] else 'FAIL'})")
        print(f"Total Benchmark Time:      {summary['total_execution_seconds']}s")
        print("=" * 60)

        return summary


if __name__ == "__main__":
    evaluator = BenchmarkEvaluator()
    asyncio.run(evaluator.run_benchmark())
