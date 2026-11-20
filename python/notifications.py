import json
import logging
import os
import urllib.request
import urllib.error

logger = logging.getLogger("drift-automation")


class SlackNotifier:
    def __init__(self, webhook_url: str | None = None):
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")

    def format_message(self, findings: list[dict]) -> dict:
        if not findings:
            return {
                "text": "Terraform Drift Detector: No drift detected."
            }

        lines = [
            "*Terraform Infrastructure Drift Detected*",
            f"*Drifted resources:* {len(findings)}",
            "",
        ]

        for finding in findings:
            resource = finding.get("resource_address", "Unknown resource")
            risk_level = finding.get("risk_level", "UNKNOWN")
            risk_score = finding.get("risk_score", "N/A")
            severity = finding.get("severity", "UNKNOWN")
            attributes = finding.get("changed_attributes", [])

            lines.extend([
                f"*Resource:* `{resource}`",
                f"*Risk:* {risk_level} ({risk_score}/100)",
                f"*Severity:* {severity}",
                f"*Changed attributes:* {', '.join(attributes)}",
                "",
            ])

        return {"text": "\n".join(lines)}

    def send(self, findings: list[dict]) -> bool:
        if not self.webhook_url:
            logger.warning("Slack webhook not configured. Alert skipped.")
            return False

        payload = self.format_message(findings)
        data = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            self.webhook_url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                if response.status == 200:
                    logger.info("Slack notification sent successfully")
                    return True

                logger.error("Slack returned HTTP status %s", response.status)
                return False

        except urllib.error.HTTPError as exc:
            logger.error("Slack HTTP error: %s", exc.code)

        except urllib.error.URLError as exc:
            logger.error("Slack connection failed: %s", exc.reason)

        except TimeoutError:
            logger.error("Slack notification timed out")

        return False