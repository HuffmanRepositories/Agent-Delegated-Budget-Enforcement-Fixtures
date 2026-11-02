import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("semantic_validator", ROOT / "scripts" / "validate_semantics.py")
semantic = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(semantic)


class BudgetSemanticValidatorTests(unittest.TestCase):
    def test_all_draft_fixtures_have_consistent_references_and_accounting(self):
        errors, count = semantic.validate_all()
        self.assertEqual(errors, [])
        self.assertEqual(count, 12)

    def test_unknown_actor_in_event_is_rejected(self):
        fixture = {
            "budget": {"unit": "credits", "limit": 10},
            "actors": [{"id": "parent", "role": "parent"}],
            "events": [{"type": "reserve", "actor_id": "missing", "amount": 1}],
            "expected_invariants": ["capacity stays bounded"],
            "failure_mode": "unknown actor"
        }
        errors = semantic.validate_data(fixture)
        self.assertTrue(any("unknown actor" in error for error in errors))

    def test_parent_cycle_is_rejected(self):
        fixture = {
            "budget": {"unit": "credits", "limit": 10},
            "actors": [{"id": "a", "parent_id": "b"}, {"id": "b", "parent_id": "a"}],
            "events": [{"type": "reserve", "actor_id": "a", "amount": 1}],
            "expected_invariants": ["bounded"],
            "failure_mode": "cycle"
        }
        errors = semantic.validate_data(fixture)
        self.assertTrue(any("cycle" in error for error in errors))

    def test_actual_cannot_exceed_reservation(self):
        fixture = {
            "budget": {"unit": "credits", "limit": 10},
            "actors": [{"id": "p"}, {"id": "c", "parent_id": "p"}],
            "events": [
                {"type": "reserve", "actor_id": "c", "amount": 3},
                {"type": "settle", "actor_id": "c", "reserved": 3, "actual": 4}
            ],
            "expected_invariants": ["settlement is bounded"],
            "failure_mode": "over-settlement"
        }
        errors = semantic.validate_data(fixture)
        self.assertTrue(any("actual usage exceeds reserved" in error for error in errors))

    def test_duplicate_release_is_rejected(self):
        fixture = {
            "budget": {"unit": "credits", "limit": 10},
            "actors": [{"id": "p"}, {"id": "c", "parent_id": "p"}],
            "events": [
                {"type": "reserve", "actor_id": "c", "amount": 4},
                {"type": "release", "actor_id": "c", "amount": 4},
                {"type": "release", "actor_id": "p", "target_id": "c", "amount": 1}
            ],
            "expected_invariants": ["release only once"],
            "failure_mode": "duplicate release"
        }
        errors = semantic.validate_data(fixture)
        self.assertTrue(any("release" in error and "exceeds remaining" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
