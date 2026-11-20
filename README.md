# Terraform Drift Detector

A Python-based AWS infrastructure drift detection tool that analyzes Terraform plan JSON, identifies configuration drift, assigns risk scores, generates reports, and sends Slack notifications.

## Features

- Detect infrastructure drift using Terraform plan JSON
- Compare expected and actual resource attributes
- Identify changed attributes recursively
- Risk scoring and classification:
  - LOW
  - MEDIUM
  - HIGH
  - CRITICAL
- JSON drift reports
- Interactive HTML drift dashboard
- Slack notifications for detected drift
- Automated refresh-only Terraform plan workflow
- Unit tests for drift detection, risk scoring, parsing, and notifications
- GitHub Actions CI pipeline

## Architecture

```text
Terraform Infrastructure
        |
        v
Terraform Refresh-Only Plan
        |
        v
Terraform Plan JSON
        |
        v
Drift Detection Engine
        |
        v
Risk Scoring Engine
        |
        +------> JSON Report
        |
        +------> HTML Dashboard
        |
        +------> Slack Notification
```

## Tech Stack

- Terraform
- AWS
- Python 3
- GitHub Actions
- Slack Webhooks

## Risk Classification

| Risk Score | Classification |
|---:|---|
| 0–29 | LOW |
| 30–59 | MEDIUM |
| 60–79 | HIGH |
| 80–100 | CRITICAL |

Risk scores are heuristic indicators designed for this project and are not official AWS security ratings.

## Project Structure

```text
terraform-drift-detector/
├── .github/
│   └── workflows/
│       └── ci.yml
├── python/
│   ├── automation.py
│   ├── drift_detector.py
│   ├── terraform_parser.py
│   ├── risk_engine.py
│   ├── report_generator.py
│   ├── html_report_generator.py
│   └── notifications.py
├── terraform/
│   ├── main.tf
│   ├── providers.tf
│   ├── variables.tf
│   └── outputs.tf
├── tests/
│   ├── fixtures/
│   └── test_*.py
├── reports/
├── requirements.txt
└── README.md
```

## Requirements

- Python 3
- Terraform
- AWS CLI
- Configured AWS credentials with appropriate permissions
- AWS infrastructure managed by Terraform

## Running Tests

```bash
python -m unittest discover -s tests -v
```

## Safety

This project is designed to **detect and report drift**, not automatically remediate it.

- Uses Terraform refresh-only planning for drift analysis.
- Does not automatically apply infrastructure changes.
- Does not automatically destroy resources.
- Generated reports, Terraform state, and plan files should not be committed.
- AWS credentials and Slack webhook URLs must be stored securely.

## CI

GitHub Actions runs the Python unit test suite on pushes and pull requests targeting `main` or `master`.

## Disclaimer

This project is intended for learning, testing, and demonstration purposes. Review all findings and Terraform plans before taking action on real infrastructure.
