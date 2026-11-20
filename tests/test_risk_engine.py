
import unittest

from python.rules.risk_engine import RiskEngine


class TestRiskEngine(unittest.TestCase):

    def setUp(self):
        self.engine = RiskEngine()

    def test_low_risk_tag_change(self):
        score = self.engine.calculate_score(
            ["tags.ManagedBy"],
            "aws_instance",
        )

        self.assertEqual(score, 5)

    def test_high_risk_encryption_change(self):
        score = self.engine.calculate_score(
            ["root_block_device[0].encrypted"],
            "aws_instance",
        )

        self.assertEqual(score, 40)

    def test_security_group_multiplier(self):
        score = self.engine.calculate_score(
            ["ingress"],
            "aws_security_group",
        )

        self.assertEqual(score, 60)

    def test_score_capped_at_100(self):
        score = self.engine.calculate_score(
            [
                "ingress",
                "egress",
                "encrypted",
                "public_ip",
            ],
            "aws_instance",
        )

        self.assertEqual(score, 100)

    def test_critical_risk_classification(self):
        self.assertEqual(
            self.engine.classify_risk(85),
            "CRITICAL",
        )

    def test_high_risk_classification(self):
        self.assertEqual(
            self.engine.classify_risk(65),
            "HIGH",
        )

    def test_medium_risk_classification(self):
        self.assertEqual(
            self.engine.classify_risk(40),
            "MEDIUM",
        )

    def test_low_risk_classification(self):
        self.assertEqual(
            self.engine.classify_risk(10),
            "LOW",
        )

    def test_recommendation_for_tag_change(self):
        finding = {
            "resource_type": "aws_instance",
            "changed_attributes": ["tags.ManagedBy"],
        }

        recommendations = self.engine.recommend(finding)

        self.assertTrue(
            any("metadata" in r.lower() or "tag" in r.lower()
                for r in recommendations)
        )


if __name__ == "__main__":
    unittest.main()
