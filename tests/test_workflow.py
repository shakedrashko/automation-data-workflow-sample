import csv
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from workflow import run, transform


class WorkflowTests(unittest.TestCase):
    def test_sample_preserves_rows_and_flags_ambiguity(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp:
            summary = run(root / "sample_input.csv", Path(temp))
            with (Path(temp) / "cleaned.csv").open(encoding="utf-8", newline="") as stream:
                rows = list(csv.DictReader(stream))
            with (Path(temp) / "review_flags.csv").open(encoding="utf-8", newline="") as stream:
                flags = list(csv.DictReader(stream))
        self.assertEqual(summary["source_rows"], 8)
        self.assertEqual(summary["output_rows"], 8)
        self.assertEqual(rows[1]["name"], "Bright Studio")
        self.assertEqual({(x["record_id"], x["reason"]) for x in flags}, {
            ("R-005", "Possible duplicate"), ("R-006", "Unknown category")
        })

    def test_missing_value_fails_instead_of_dropping_a_row(self):
        with self.assertRaisesRegex(ValueError, "missing values"):
            transform([{"record_id": "R-001"}])


if __name__ == "__main__":
    unittest.main()

