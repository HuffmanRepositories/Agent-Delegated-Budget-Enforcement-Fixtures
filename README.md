# Agent Delegated Budget Enforcement Fixtures

[Start here](START-HERE.md) · [Whitepaper](WHITEPAPER.md) · [AI agent guidance](AGENTS.md)


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
python scripts/validate_semantics.py
```

## Experimental budget-ledger harness

The [synthetic SQLite ledger](docs/synthetic-budget-ledger.md) tests concurrent reservations, hierarchical caps, idempotent reservation, settlement, release, revocation, and over-limit actual usage. It is a local model—not a production budget controller or provider billing integration.

## Fixture format

See [docs/fixture-format.md](docs/fixture-format.md), [template](docs/fixture-template.json), and [fixture status](docs/fixture-status.md).

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/review-checklist.md](docs/review-checklist.md). Keep fixtures synthetic and describe expected behavior as a reviewable invariant, not a universal implementation prescription.

## License

MIT. See [LICENSE](LICENSE).

## Ecosystem directory

This project is part of the [HuffmanRepositories public ecosystem](https://github.com/HuffmanRepositories/Huffman-Ecosystem-Root). Use the directory for project routing, human and AI onboarding, shared terminology, governance, and related workstreams. This repository's own README and specifications remain authoritative for its scope, maturity, and validation status.
