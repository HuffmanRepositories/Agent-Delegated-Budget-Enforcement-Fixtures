# Agent Delegated Budget Enforcement: Bounded Resource Use

**Author:** Robert Huffman  
**Status:** Research whitepaper, version 0.1

## Abstract

P14 is a synthetic fixture corpus for examining hierarchical resource budgets when agents delegate work to child agents. It focuses on allocation, reservation, settlement, and aggregate constraints rather than defining a production budget manager.

## Problem statement

Delegated systems can oversubscribe budgets through concurrent child reservations, nested allocations, stale accounting, late completion, or inconsistent units and windows. A parent may believe it has bounded total spend while child activity exceeds the intended limit.

## Approach

P14 captures concurrent reservations, nested allocation expansion, reserve/actual settlement, duplicate refunds, child work after parent exhaustion, lost updates, mixed units, rollups, cancellation and late completion, budget-window resets, revocation, and sibling overcommit. Each case describes the accounting invariant under review.

## How to use P14

Read [START-HERE.md](START-HERE.md), [docs/taxonomy.md](docs/taxonomy.md), [docs/fixture-format.md](docs/fixture-format.md), and [docs/review-checklist.md](docs/review-checklist.md). Inspect cases in [fixtures/](fixtures/). Run python scripts/validate_fixtures.py, python scripts/validate_semantics.py, and python -m unittest discover -s tests -v.

## Boundaries

P14 is not a budget manager, billing service, pricing catalog, usage interchange protocol, or production enforcement engine. Passing validators does not prove financial accuracy, concurrency safety, or runtime enforcement.

## Outlook

A robust budget system should make units, windows, reservation lifecycles, settlement, refunds, and delegation rollups explicit. The corpus is a review aid for these invariants, not a substitute for implementation testing.

— Robert Huffman