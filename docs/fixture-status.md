# Fixture status

All cases below are **synthetic draft fixtures**. They are intended for semantic review, not as an implementation conformance suite.

| ID | Scenario | Category | Status |
|---|---|---|---|
| DBEF-001 | Concurrent children reserve shared remaining capacity | concurrent-reservation | draft |
| DBEF-002 | Nested child delegation expands beyond parent allocation | nested-allocation | draft |
| DBEF-003 | Reservation exceeds actual usage; settlement releases remainder | reservation-settlement | draft |
| DBEF-004 | Reservation release/refund is lost or duplicated | release-refund | draft |
| DBEF-005 | Child continues after parent budget exhaustion | revocation-exhaustion | draft |
| DBEF-006 | Concurrent updates lose aggregate usage | accounting-race | draft |
| DBEF-007 | Token and money limits are silently mixed | unit-scope | draft |
| DBEF-008 | Child usage is omitted or double-counted in parent roll-up | roll-up | draft |
| DBEF-009 | Cancellation and late child completion conflict | lifecycle | draft |
| DBEF-010 | Child crosses budget-window reset boundary | window-boundary | draft |
| DBEF-011 | Child grant is revoked while a reservation is pending | revocation-exhaustion | draft |
| DBEF-012 | Sibling allocations are independently valid but jointly oversubscribe | concurrent-reservation | draft |

Validator checks JSON structure and required fields only; it does not evaluate budget correctness.
