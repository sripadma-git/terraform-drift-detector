import argparse
import logging
from pathlib import Path

from python.terraform_parser import TerraformPlanParser
from python.drift_detector import DriftDetector
from python.rules.risk_engine import RiskEngine
from python.report_generator import ReportGenerator
from python.html_report_generator import HTMLReportGenerator


# ============================================================
# LOGGING CONFIGURATION
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("drift-detector")


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"


# ============================================================
# DRIFT ANALYSIS
# ============================================================

def analyze_plan(plan_file: Path) -> list[dict]:
    """Analyze Terraform plan JSON and generate reports."""

    logger.info("Starting Terraform drift analysis")
    logger.info("Plan file: %s", plan_file)

    # Step 1: Parse Terraform plan JSON
    parser = TerraformPlanParser(plan_file)

    resource_drift = parser.get_resource_drift()

    logger.info(
        "Terraform drift entries found: %d",
        len(resource_drift),
    )

    # Step 2: Detect drift
    detector = DriftDetector(resource_drift)

    findings = detector.analyze()

    # Step 3: Apply risk scoring and recommendations
    risk_engine = RiskEngine()

    enhanced_findings = [
        risk_engine.analyze(finding)
        for finding in findings
    ]

    # Step 4: Generate JSON report
    json_reporter = ReportGenerator(REPORTS_DIR)

    json_reporter.generate_json(
        enhanced_findings,
    )

    # Step 5: Generate HTML dashboard
    html_reporter = HTMLReportGenerator(REPORTS_DIR)

    html_reporter.generate(
        enhanced_findings,
    )

    # Step 6: Display summary
    print("\n" + "=" * 60)
    print("TERRAFORM DRIFT ANALYSIS")
    print("=" * 60)

    print(f"Drifted resources: {len(enhanced_findings)}")

    if not enhanced_findings:
        print("\nNo infrastructure drift detected.")

    else:
        print("\nDrift detected!")

        for finding in enhanced_findings:
            print("\n" + "-" * 60)

            print(
                f"Resource      : "
                f"{finding.get('resource_address')}"
            )

            print(
                f"Resource type : "
                f"{finding.get('resource_type')}"
            )

            print(
                f"Severity     : "
                f"{finding.get('severity')}"
            )

            print(
                f"Risk score   : "
                f"{finding.get('risk_score')}/100"
            )

            print(
                f"Risk level   : "
                f"{finding.get('risk_level')}"
            )

            print("\nChanged attributes:")

            for attribute in finding.get(
                "changed_attributes", []
            ):
                print(f"  - {attribute}")

            print("\nRecommendations:")

            for recommendation in finding.get(
                "recommendations", []
            ):
                print(f"  - {recommendation}")

    print("\nReports generated:")
    print(f"JSON : {REPORTS_DIR / 'drift-report.json'}")
    print(f"HTML : {REPORTS_DIR / 'drift-report.html'}")

    logger.info(
        "Analysis completed. Drifted resources: %d",
        len(enhanced_findings),
    )

    return enhanced_findings


# ============================================================
# CLI ENTRY POINT
# ============================================================

def main() -> int:
    """CLI entry point for manual Terraform plan analysis."""

    parser = argparse.ArgumentParser(
        description="Terraform Infrastructure Drift Detector"
    )

    parser.add_argument(
        "--plan",
        required=True,
        help="Path to Terraform plan JSON file",
    )

    args = parser.parse_args()

    plan_file = Path(args.plan)

    if not plan_file.is_absolute():
        plan_file = PROJECT_ROOT / plan_file

    try:
        analyze_plan(plan_file)
        return 0

    except FileNotFoundError as exc:
        logger.error("%s", exc)
        return 1

    except Exception:
        logger.exception("Drift analysis failed")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())