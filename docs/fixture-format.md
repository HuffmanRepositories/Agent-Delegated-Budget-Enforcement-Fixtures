# Fixture format

Each fixture is a JSON object with these fields:

- `id`: stable kebab-case identifier
- `title`: short scenario name
- `category`: review category
- `status`: currently `draft`
- `synthetic`: must be `true`
- `description`: scenario context
- `budget`: explicit budget unit, amount, scope, and window
- `actors`: synthetic parent/child actors and roles
- `events`: ordered or concurrent allocation/usage events
- `expected_invariants`: statements a reviewer should evaluate
- `failure_mode`: potential violation
- `notes`: optional caveats

Amounts and units are illustrative only. They do not represent prices or real workloads. Fixtures are not executable semantics; ordering/concurrency is described in the scenario. An expected invariant is a review target, not a claim that every system must implement one particular reservation strategy.
