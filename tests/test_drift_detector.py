
import unittest

from python.drift_detector import (
    DriftDetector,
    classify_severity,
    find_differences,
)


class TestFindDifferences(unittest.TestCase):

    def test_detects_tag_change(self):
        before = {"tags": {"ManagedBy": "Terraform"}}
        after = {"tags": {"ManagedBy": "Manual"}}

        result = find_differences(before, after)

        self.assertIn("tags.ManagedBy", result)

    def test_detects_nested_difference(self):
        before = {
            "root_block_device": {
                "volume_size": 8,
                "encrypted": True,
            }
        }

        after = {
            "root_block_device": {
                "volume_size": 16,
                "encrypted": True,
            }
        }

        result = find_differences(before, after)

        self.assertEqual(result, ["root_block_device.volume_size"])

    def test_no_differences(self):
        data = {"instance_type": "t3.micro", "encrypted": True}

        self.assertEqual(find_differences(data, data), [])


class TestSeverityClassification(unittest.TestCase):

    def test_high_severity(self):
        self.assertEqual(
            classify_severity(["security_groups"]),
            "HIGH",
        )

    def test_medium_severity(self):
        self.assertEqual(
            classify_severity(["instance_type"]),
            "MEDIUM",
        )

    def test_low_severity(self):
        self.assertEqual(
            classify_severity(["tags.ManagedBy"]),
            "LOW",
        )


class TestDriftDetector(unittest.TestCase):

    def test_analyzes_resource_drift(self):
        drift = [
            {
                "address": "aws_instance.example",
                "type": "aws_instance",
                "change": {
                    "actions": ["update"],
                    "before": {
                        "tags": {
                            "ManagedBy": "Terraform",
                        }
                    },
                    "after": {
                        "tags": {
                            "ManagedBy": "Manual",
                        }
                    },
                },
            }
        ]

        detector = DriftDetector(drift)
        findings = detector.analyze()

        self.assertEqual(len(findings), 1)
        self.assertEqual(
            findings[0]["resource_address"],
            "aws_instance.example",
        )
        self.assertIn(
            "tags.ManagedBy",
            findings[0]["changed_attributes"],
        )
        self.assertEqual(findings[0]["severity"], "LOW")


if __name__ == "__main__":
    unittest.main()
