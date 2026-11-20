import unittest

from python.drift_detector import DriftDetector


class TestNoDrift(unittest.TestCase):

    def test_empty_drift_returns_no_findings(self):
        detector = DriftDetector([])
        findings = detector.analyze()

        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()