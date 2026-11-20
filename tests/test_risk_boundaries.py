import unittest

from python.rules.risk_engine import RiskEngine


class TestRiskBoundaries(unittest.TestCase):

    def setUp(self):
        self.engine = RiskEngine()

    def test_low_risk_boundary(self):
        self.assertEqual(self.engine.classify_risk(29), "LOW")

    def test_medium_risk_lower_boundary(self):
        self.assertEqual(self.engine.classify_risk(30), "MEDIUM")

    def test_medium_risk_upper_boundary(self):
        self.assertEqual(self.engine.classify_risk(59), "MEDIUM")

    def test_high_risk_lower_boundary(self):
        self.assertEqual(self.engine.classify_risk(60), "HIGH")

    def test_high_risk_upper_boundary(self):
        self.assertEqual(self.engine.classify_risk(79), "HIGH")

    def test_critical_risk_boundary(self):
        self.assertEqual(self.engine.classify_risk(80), "CRITICAL")

    def test_maximum_score(self):
        self.assertEqual(self.engine.classify_risk(100), "CRITICAL")


if __name__ == "__main__":
    unittest.main()