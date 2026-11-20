
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any


class ReportGenerator:

    def __init__(
        self,
        output_dir: str | Path = "reports",
    ):

        self.output_dir = Path(output_dir)

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def generate_json(
        self,
        findings: list[dict[str, Any]],
    ) -> Path:

        risk_summary = {
            "critical": sum(
                f.get("risk_level") == "CRITICAL"
                for f in findings
            ),
            "high": sum(
                f.get("risk_level") == "HIGH"
                for f in findings
            ),
            "medium": sum(
                f.get("risk_level") == "MEDIUM"
                for f in findings
            ),
            "low": sum(
                f.get("risk_level") == "LOW"
                for f in findings
            ),
        }

        severity_summary = {
            "high": sum(
                f.get("severity") == "HIGH"
                for f in findings
            ),
            "medium": sum(
                f.get("severity") == "MEDIUM"
                for f in findings
            ),
            "low": sum(
                f.get("severity") == "LOW"
                for f in findings
            ),
        }

        report = {
            "generated_at": datetime.now(
                timezone.utc
            ).isoformat(),

            "tool": "Terraform Drift Detector",

            "summary": {
                "total_drifted_resources": len(
                    findings
                ),
                "severity": severity_summary,
                "risk": risk_summary,
            },

            "findings": findings,
        }

        output_file = (
            self.output_dir / "drift-report.json"
        )

        output_file.write_text(
            json.dumps(
                report,
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )

        return output_file
