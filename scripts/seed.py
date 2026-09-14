"""
AgentOps Observatory - Database Seeder Script
Populates the observatory with rich historical and live telemetry:
- Normal multi-agent RAG runs
- MCP tool calls (filesystem, weather, github, database)
- n8n automated workflow executions
- Detected policy violations and security incidents
- Redaction audit events
- Cost, carbon, and latency metrics
"""

import asyncio
from evaluation.generator import FixtureGenerator
from backend.app.models.db import init_db
from backend.app.services.storage import IngestionService


async def seed_database():
    print("Initializing database and seeding telemetry...")
    await init_db()
    ingestion = IngestionService()
    fixtures = FixtureGenerator.generate_all_fixtures()

    total_seeded = 0
    for category, runs in fixtures.items():
        print(f"Seeding {len(runs)} runs for category '{category}'...")
        for run_obj in runs:
            for ev in run_obj["events"]:
                await ingestion.ingest_event(ev)
                total_seeded += 1

    print(f"\nSeeding complete! Successfully ingested {total_seeded} events across {sum(len(r) for r in fixtures.values())} runs.")


if __name__ == "__main__":
    asyncio.run(seed_database())
