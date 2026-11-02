# Synthetic Hierarchical Budget Ledger

This experimental model uses SQLite transactions to test a shared parent/child budget ledger. It models reservations and committed usage against each account in the ancestry, so sibling reservations are serialized and bounded by the shared parent capacity.

Run:
```bash
python -m unittest discover -s tests -v
python scripts/validate_fixtures.py
python scripts/validate_semantics.py
```

Tests cover concurrent sibling reservation, idempotent reserve/replay, nested account cap, actual-usage settlement, release/refund of reserved capacity, revoked ancestor denial, and actual usage exceeding remaining budget.

## Limits
This is a local synthetic ledger—not production billing, provider usage metering, or proof of runtime enforcement. It does not test distributed multi-host transactions, external provider calls, price/unit conversion, time-window rollover, delayed usage after cancellation, ledger replication, crash recovery beyond SQLite transaction rollback, or account authentication. Monetary precision should use integer minor units or explicit decimal semantics, not binary floats. Unit/currency mismatches must be rejected by a real system.
