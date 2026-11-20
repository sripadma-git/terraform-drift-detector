import unittest
from python.notifications import SlackNotifier


class TestSlackNotifier(unittest.TestCase):

    def test_no_drift_message(self):
        notifier = SlackNotifier(webhook_url="https://example.com/webhook")
        message = notifier.format_message([])

        self.assertIn("No drift detected", message["text"])

    def test_drift_message_contains_resource(self):
        notifier = SlackNotifier(webhook_url="https://example.com/webhook")

        findings = [{
            "resource_address": "aws_instance.drift_detector",
            "risk_level": "LOW",
            "risk_score": 5,
            "severity": "LOW",
            "changed_attributes": ["tags.ManagedBy"],
        }]

        message = notifier.format_message(findings)

        self.assertIn("aws_instance.drift_detector", message["text"])
        self.assertIn("tags.ManagedBy", message["text"])
        self.assertIn("5/100", message["text"])


if __name__ == "__main__":
    unittest.main()
