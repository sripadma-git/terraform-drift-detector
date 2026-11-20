
import html
from pathlib import Path
from datetime import datetime, timezone
from typing import Any


class HTMLReportGenerator:
    """Generate a standalone HTML dashboard for Terraform drift."""

    def __init__(self, output_dir: str | Path = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _escape(value: Any) -> str:
        return html.escape(str(value), quote=True)

    def generate(self, findings: list[dict[str, Any]]) -> Path:
        total = len(findings)

        critical = sum(
            f.get("risk_level") == "CRITICAL" for f in findings
        )
        high = sum(
            f.get("risk_level") == "HIGH" for f in findings
        )
        medium = sum(
            f.get("risk_level") == "MEDIUM" for f in findings
        )
        low = sum(
            f.get("risk_level") == "LOW" for f in findings
        )

        cards = f"""
        <div class="metrics">
            <div class="metric">
                <div class="metric-label">Drifted Resources</div>
                <div class="metric-value">{total}</div>
            </div>
            <div class="metric critical">
                <div class="metric-label">Critical</div>
                <div class="metric-value">{critical}</div>
            </div>
            <div class="metric high">
                <div class="metric-label">High</div>
                <div class="metric-value">{high}</div>
            </div>
            <div class="metric medium">
                <div class="metric-label">Medium</div>
                <div class="metric-value">{medium}</div>
            </div>
            <div class="metric low">
                <div class="metric-label">Low</div>
                <div class="metric-value">{low}</div>
            </div>
        </div>
        """

        finding_cards = []

        for finding in findings:
            address = self._escape(
                finding.get("resource_address", "unknown")
            )
            resource_type = self._escape(
                finding.get("resource_type", "unknown")
            )
            risk_level = self._escape(
                finding.get("risk_level", "UNKNOWN")
            )
            risk_score = finding.get("risk_score", 0)
            severity = self._escape(
                finding.get("severity", "UNKNOWN")
            )

            attributes = finding.get("changed_attributes", [])
            recommendations = finding.get("recommendations", [])
            actions = finding.get("actions", [])

            attributes_html = "".join(
                f"<li>{self._escape(attribute)}</li>"
                for attribute in attributes
            )

            recommendations_html = "".join(
                f"<li>{self._escape(recommendation)}</li>"
                for recommendation in recommendations
            )

            actions_html = ", ".join(
                self._escape(action) for action in actions
            )

            before = finding.get("before", {})
            after = finding.get("after", {})

            before_tags = before.get("tags", {})
            after_tags = after.get("tags", {})

            before_tags_html = "".join(
                f"<li><strong>{self._escape(k)}</strong>: "
                f"{self._escape(v)}</li>"
                for k, v in (before_tags or {}).items()
            )

            after_tags_html = "".join(
                f"<li><strong>{self._escape(k)}</strong>: "
                f"{self._escape(v)}</li>"
                for k, v in (after_tags or {}).items()
            )

            finding_cards.append(f"""
            <section class="finding">
                <div class="finding-header">
                    <div>
                        <h2>{address}</h2>
                        <p class="resource-type">{resource_type}</p>
                    </div>
                    <span class="badge {risk_level.lower()}">
                        {risk_level}
                    </span>
                </div>

                <div class="risk-info">
                    <div>
                        <span class="small-label">Risk score</span>
                        <strong>{risk_score}/100</strong>
                    </div>
                    <div>
                        <span class="small-label">Severity</span>
                        <strong>{severity}</strong>
                    </div>
                    <div>
                        <span class="small-label">Terraform actions</span>
                        <strong>{actions_html or "N/A"}</strong>
                    </div>
                </div>

                <div class="detail-grid">
                    <div class="detail-box">
                        <h3>Changed Attributes</h3>
                        <ul>{attributes_html or "<li>None</li>"}</ul>
                    </div>

                    <div class="detail-box">
                        <h3>Recommendations</h3>
                        <ul>{recommendations_html or "<li>Review manually</li>"}</ul>
                    </div>

                    <div class="detail-box">
                        <h3>Before — Terraform Expected</h3>
                        <ul>{before_tags_html or "<li>No tags available</li>"}</ul>
                    </div>

                    <div class="detail-box">
                        <h3>After — Current AWS</h3>
                        <ul>{after_tags_html or "<li>No tags available</li>"}</ul>
                    </div>
                </div>
            </section>
            """)

        findings_html = "".join(finding_cards)

        if not findings_html:
            findings_html = """
            <section class="empty-state">
                <h2>No Drift Detected</h2>
                <p>Your infrastructure matches the detected Terraform state.</p>
            </section>
            """

        generated_at = datetime.now(timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S UTC"
        )

        document = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Terraform Drift Detector</title>

<style>
* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    font-family: Arial, Helvetica, sans-serif;
    background: #0b1120;
    color: #e5e7eb;
}}

.container {{
    max-width: 1200px;
    margin: auto;
    padding: 32px 24px;
}}

.header {{
    margin-bottom: 32px;
}}

.header h1 {{
    font-size: 30px;
    margin: 0 0 10px;
}}

.header p {{
    color: #9ca3af;
    margin: 0;
}}

.metrics {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 16px;
    margin-bottom: 32px;
}}

.metric {{
    background: #151e30;
    border: 1px solid #263449;
    padding: 22px;
    border-radius: 12px;
}}

.metric-label {{
    color: #9ca3af;
    font-size: 13px;
}}

.metric-value {{
    font-size: 30px;
    font-weight: bold;
    margin-top: 10px;
}}

.critical .metric-value {{
    color: #f87171;
}}

.high .metric-value {{
    color: #fb923c;
}}

.medium .metric-value {{
    color: #facc15;
}}

.low .metric-value {{
    color: #4ade80;
}}

.finding {{
    background: #151e30;
    border: 1px solid #263449;
    border-radius: 14px;
    padding: 24px;
    margin-bottom: 20px;
}}

.finding-header {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 16px;
}}

.finding-header h2 {{
    font-size: 20px;
    margin: 0;
    word-break: break-word;
}}

.resource-type {{
    color: #9ca3af;
    margin-top: 8px;
}}

.badge {{
    padding: 8px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: bold;
}}

.badge.critical {{
    background: #451a1a;
    color: #f87171;
}}

.badge.high {{
    background: #452816;
    color: #fb923c;
}}

.badge.medium {{
    background: #443714;
    color: #facc15;
}}

.badge.low {{
    background: #163a2a;
    color: #4ade80;
}}

.risk-info {{
    display: flex;
    flex-wrap: wrap;
    gap: 32px;
    padding: 20px 0;
    margin: 16px 0;
    border-top: 1px solid #263449;
    border-bottom: 1px solid #263449;
}}

.risk-info div {{
    display: flex;
    flex-direction: column;
    gap: 6px;
}}

.small-label {{
    color: #9ca3af;
    font-size: 12px;
}}

.risk-info strong {{
    font-size: 16px;
}}

.detail-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 16px;
}}

.detail-box {{
    background: #0b1120;
    border-radius: 10px;
    padding: 18px;
    overflow-wrap: anywhere;
}}

.detail-box h3 {{
    font-size: 15px;
    margin-top: 0;
}}

.detail-box ul {{
    padding-left: 20px;
    margin-bottom: 0;
}}

.detail-box li {{
    color: #cbd5e1;
    margin-bottom: 8px;
}}

.empty-state {{
    background: #153324;
    border: 1px solid #24543a;
    border-radius: 12px;
    padding: 32px;
    text-align: center;
}}

.footer {{
    color: #6b7280;
    text-align: center;
    margin-top: 40px;
    font-size: 12px;
}}

@media (max-width: 600px) {{
    .container {{
        padding: 20px 14px;
    }}

    .finding {{
        padding: 16px;
    }}

    .risk-info {{
        gap: 16px;
    }}
}}
</style>
</head>

<body>
<div class="container">

    <header class="header">
        <h1>Terraform Drift Detector</h1>
        <p>Infrastructure drift analysis and risk assessment dashboard</p>
        <p>Generated: {generated_at}</p>
    </header>

    {cards}

    <h2>Drift Findings</h2>

    {findings_html}

    <footer class="footer">
        Generated automatically by Terraform Drift Detector
    </footer>

</div>
</body>
</html>
"""

        output_file = self.output_dir / "drift-report.html"

        output_file.write_text(
            document,
            encoding="utf-8",
        )

        return output_file
