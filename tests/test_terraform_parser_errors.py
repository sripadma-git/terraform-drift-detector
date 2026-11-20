import json
import tempfile
import unittest
from pathlib import Path

from python.terraform_parser import TerraformPlanParser


class TestTerraformParserErrors(unittest.TestCase):

    def test_missing_file_raises_error(self):
        parser = TerraformPlanParser(
            "tests/fixtures/file-does-not-exist.json"
        )

        with self.assertRaises(FileNotFoundError):
            parser.load()

    def test_invalid_json_raises_error(self):

        with tempfile.TemporaryDirectory() as temp_dir:

            file_path = Path(temp_dir) / "invalid.json"

            file_path.write_text(
                "{invalid json",
                encoding="utf-8",
            )

            parser = TerraformPlanParser(file_path)

            with self.assertRaises(json.JSONDecodeError):
                parser.load()


if __name__ == "__main__":
    unittest.main()