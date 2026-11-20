import unittest

from python.drift_detector import DriftDetector


class TestMultipleDrift(unittest.TestCase):

    def test_multiple_drifted_resources_are_detected(self):

        drift = [
            {
                "address": "aws_instance.web",
                "type": "aws_instance",
                "change": {
                    "before": {
                        "tags": {"ManagedBy": "Terraform"}
                    },
                    "after": {
                        "tags": {"ManagedBy": "Manual"}
                    }
                }
            },
            {
                "address": "aws_security_group.web",
                "type": "aws_security_group",
                "change": {
                    "before": {
                        "ingress": [{"from_port": 443}]
                    },
                    "after": {
                        "ingress": [{"from_port": 22}]
                    }
                }
            }
        ]

        detector = DriftDetector(drift)
        findings = detector.analyze()

        self.assertEqual(len(findings), 2)


if __name__ == "__main__":
    unittest.main()