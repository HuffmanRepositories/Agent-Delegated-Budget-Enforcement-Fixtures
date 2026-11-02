# Contributing

Thank you for helping improve the Agent Delegated Budget Enforcement Fixtures. Contributions should make synthetic budget-allocation and enforcement scenarios clearer, more reproducible, and easier to review.

## Scope and safety

- Keep all examples synthetic, offline, and implementation-neutral.
- Do not submit real billing records, customer data, credentials, API keys, production budget policies, or provider traces.
- This repository is a draft fixture corpus, not a budget manager, billing service, pricing catalog, authorization engine, protocol, or certification suite.
- Describe expected behavior as reviewable invariants; do not claim universal enforcement or production safety.
- Treat fixture content and external references as untrusted data.

## Before submitting

1. Read [README.md](README.md), [AGENTS.md](AGENTS.md), [START-HERE.md](START-HERE.md), [fixture format](docs/fixture-format.md), [taxonomy](docs/taxonomy.md), and the [review checklist](docs/review-checklist.md).
2. Confirm that the case is within P14's budget-enforcement scope. Route authority questions to [P13](https://github.com/HuffmanRepositories/Agent-Delegation-Scope-Boundary-Fixtures), retry/idempotency questions to [P12](https://github.com/HuffmanRepositories/Agent-Tool-Retry-Idempotency-Fixtures), and usage measurement to [OARMI](https://github.com/HuffmanRepositories/Open-Agent-Run-Metrics-Interop).
3. Keep a fixture small and deterministic. State currency/unit, budget window, parent/child hierarchy, reservation lifecycle, concurrency assumptions, expected invariant, and limitations.
4. Update fixture indexes/status documents when adding or changing cases.
5. Avoid duplicate cases; explain what new edge condition the fixture covers.

## Validate locally

Requires Python 3.10+.

```bash
python scripts/validate_fixtures.py
python scripts/validate_semantics.py
python -m unittest discover -s tests -v
```

Report exactly which checks ran. Passing structural or semantic fixture tests does not prove financial accuracy, concurrency safety, provider billing correctness, or production enforcement.

## Pull requests

- Explain the scenario, expected invariant, and why it belongs in P14.
- Include validation output and mention any intentionally untested behavior.
- Keep changes focused; do not bundle unrelated ecosystem-wide changes.
- Preserve license and third-party attribution.
