import pytest
from backend.app.core.security import compute_event_hash


def test_append_only_hash_chain_integrity():
    genesis = "0" * 64
    chain = [genesis]

    events = [
        {"action": "EVENT_INGEST", "event_id": f"ev-{i}", "index": i}
        for i in range(500)
    ]

    for ev in events:
        prev = chain[-1]
        current = compute_event_hash(prev, ev)
        chain.append(current)

    # Verify chain length
    assert len(chain) == 501

    # Verify recomputation matches perfectly
    for i in range(len(events)):
        prev_hash = chain[i]
        expected_hash = compute_event_hash(prev_hash, events[i])
        assert chain[i + 1] == expected_hash

    # Verify tampering invalidates downstream
    tampered_event = dict(events[100])
    tampered_event["action"] = "UNAUTHORIZED_MODIFICATION"
    tampered_hash = compute_event_hash(chain[100], tampered_event)
    assert tampered_hash != chain[101]
