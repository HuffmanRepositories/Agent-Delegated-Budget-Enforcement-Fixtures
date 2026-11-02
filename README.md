# Agent Delegated Budget Enforcement Fixtures

An implementation-neutral collection of **synthetic JSON fixtures** for reviewing hierarchical budget allocation and enforcement when agents delegate work to child agents.

The focus is budget **reservation and enforcement semantics**: concurrent child allocations, nested limits, refunds/releases, revocation, and parent-level aggregate constraints. This repository does not define a budget protocol or implement a budget manager.

## Status

- Fixtures: draft, synthetic, human review required
- Validator: structural/schema-light checks only
- CI: configured; passing runs are reported only after verification
- No claim of completeness, novelty, conformance, or production safety

## Scope

Included:
- Parent/child budget allocation and concurrent reservation cases
- Explicit units and budget-window semantics
- Expected invariant statements for reviewers

Excluded:
- Runtime, SDK, middleware, gateway, or budget manager
- Pricing catalog, billing product, usage metric interchange (see [OARMI](https://github.com/HuffmanRepositories/Open-Agent-Run-Metrics-Interop))
- Generic retry/idempotency suite (see [P12](https://github.com/HuffmanRepositories/Agent-Tool-Retry-Idempotency-Fixtures))
- Benchmark, certification, or protocol

## Quick start

```bash
python -m unittest discover -s tests -v
python scripts/validate_fixtures.py
```

## Fixture format

See [docs/fixture-format.md](docs/fixture-format.md), [template](docs/fixture-template.json), and [fixture status](docs/fixture-status.md).

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/review-checklist.md](docs/review-checklist.md). Keep fixtures synthetic and describe expected behavior as a reviewable invariant, not a universal implementation prescription.

## License

MIT. See [LICENSE](LICENSE).
