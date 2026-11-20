import logging
import subprocess
from pathlib import Path

from python.terraform_parser import TerraformPlanParser
from python.drift_detector import DriftDetector
from python.rules.risk_engine import RiskEngine
from python.report_generator import ReportGenerator
from python.html_report_generator import HTMLReportGenerator
from python.notifications import SlackNotifier


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

TERRAFORM_DIR = PROJECT_ROOT / "terraform"
REPORTS_DIR = PROJECT_ROOT / "reports"

PLAN_FILE = REPORTS_DIR / "automated-drift.tfplan"
PLAN_JSON_FILE = REPORTS_DIR / "automated-plan.json"


# ============================================================
# LOGGING CONFIGURATION
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("drift-automation")


# ============================================================
# COMMAND EXECUTION
# ============================================================

def run_command(command: list[str], cwd: Path) -> str:
    """Execute a command and return its standard output."""

    logger.info("Executing: %s", " ".join(command))

    result = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )

    if result.stderr.strip():
        logger.info(result.stderr.strip())

    return result.stdout


# ============================================================
# TERRAFORM PLAN GENERATION
# ============================================================

def generate_terraform_plan() -> None:
    """Generate a refresh-only Terraform plan."""

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("Generating Terraform refresh-only plan")

    run_command(
        [
            "terraform",
            "plan",
            "-refresh-only",
            "-input=false",
            "-out",
            str(PLAN_FILE),
        ],
        cwd=TERRAFORM_DIR,
    )

    logger.info("Terraform plan generated successfully")


# ============================================================
# PLAN JSON EXPORT
# ============================================================

def export_plan_json() -> None:
    """Convert the binary Terraform plan into JSON."""

    logger.info("Exporting Terraform plan to JSON")

    plan_json = run_command(
        [
            "terraform",
            "show",
            "-json",
            str(PLAN_FILE),
        ],
        cwd=TERRAFORM_DIR,
    )

    PLAN_JSON_FILE.write_text(
        plan_json,
        encoding="utf-8",
    )

    logger.info("Plan JSON saved: %s", PLAN_JSON_FILE)


# ============================================================
# DRIFT ANALYSIS
# ============================================================

def analyze_plan() -> list[dict]:
    """Analyze Terraform drift and generate reports."""

    logger.info("Analyzing Terraform plan")

    parser = TerraformPlanParser(PLAN_JSON_FILE)

    resource_drift = parser.get_resource_drift()

    detector = DriftDetector(resource_drift)

    findings = detector.analyze()

    # Apply risk scoring and recommendations
    risk_engine = RiskEngine()

    enhanced_findings = [
        risk_engine.analyze(finding)
        for finding in findings
    ]

    # Generate JSON report
    json_reporter = ReportGenerator(REPORTS_DIR)

    json_reporter.generate_json(
        enhanced_findings,
    )

    # Generate HTML dashboard
    html_reporter = HTMLReportGenerator(REPORTS_DIR)

    html_reporter.generate(
        enhanced_findings,
    )

    logger.info(
        "Analysis completed. Drifted resources: %d",
        len(enhanced_findings),
    )

    return enhanced_findings


# ============================================================
# SLACK NOTIFICATION
# ============================================================

def send_slack_notification(findings: list[dict]) -> None:
    """Send a Slack alert when drift is detected."""

    if not findings:
        logger.info("No drift detected. Slack alert skipped.")
        return

    logger.info("Drift detected. Sending Slack notification.")

    notifier = SlackNotifier()

    success = notifier.send(findings)

    if success:
        logger.info("Slack notification delivered successfully")
    else:
        logger.warning(
            "Slack notification was not delivered. "
            "Drift reports are still available."
        )


# ============================================================
# DISPLAY RESULTS
# ============================================================

def display_summary(findings: list[dict]) -> None:
    """Display drift analysis results in the terminal."""

    print("\n" + "=" * 60)
    print("DRIFT DETECTION SUMMARY")
    print("=" * 60)

    print(f"Drifted resources: {len(findings)}")

    print(f"JSON report : {REPORTS_DIR / 'drift-report.json'}")
    print(f"HTML report : {REPORTS_DIR / 'drift-report.html'}")

    if not findings:
        print("\nNo infrastructure drift detected.")
        logger.info("No drift detected")

        return

    print("\nDrift detected!")

    for finding in findings:
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


# ============================================================
# AUTOMATION WORKFLOW
# ============================================================

def main() -> int:
    """Run the complete automated drift detection workflow."""

    try:
        logger.info("=" * 60)
        logger.info("TERRAFORM DRIFT DETECTION AUTOMATION")
        logger.info("=" * 60)

        # Step 1: Generate Terraform plan
        generate_terraform_plan()

        # Step 2: Export plan as JSON
        export_plan_json()

        # Step 3: Analyze drift and generate reports
        findings = analyze_plan()

        # Step 4: Send Slack notification if drift exists
        send_slack_notification(findings)

        # Step 5: Display summary
        display_summary(findings)

        logger.info("Automation completed successfully")

        return 0

    except subprocess.CalledProcessError as exc:
        logger.error(
            "Command failed with exit code %s",
            exc.returncode,
        )

        if exc.stdout:
            logger.error("STDOUT:\n%s", exc.stdout)

        if exc.stderr:
            logger.error("STDERR:\n%s", exc.stderr)

        return 1

    except Exception:
        logger.exception(
            "Automated drift detection failed"
        )

        return 1


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    raise SystemExit(main())