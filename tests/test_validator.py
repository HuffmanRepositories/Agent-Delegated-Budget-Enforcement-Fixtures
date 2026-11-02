import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validator", ROOT / "scripts" / "validate_fixtures.py")
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)

class FixtureValidatorTests(unittest.TestCase):
    def test_all_fixture_files_are_structurally_valid(self):
        files = sorted((ROOT / "fixtures").glob("*.json"))
        self.assertEqual(len(files), 12)
        for path in files:
            with self.subTest(path=path.name):
                self.assertEqual(validator.validate(path), [])

    def test_validator_requires_synthetic_draft(self):
        import json
        import tempfile
        fixture = {
            "id": "DBEF-test", "title": "x", "category": "test", "status": "final",
            "synthetic": False, "description": "x", "budget": {"unit": "x"},
            "actors": [{"id": "p"}], "events": [{"type": "x"}],
            "expected_invariants": ["x"], "failure_mode": "x"
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", encoding="utf-8") as f:
            json.dump(fixture, f)
            f.flush()
            errors = validator.validate(Path(f.name))
        self.assertTrue(any("synthetic must be true" in e for e in errors))
        self.assertTrue(any("status must remain draft" in e for e in errors))

if __name__ == "__main__":
    unittest.main()
