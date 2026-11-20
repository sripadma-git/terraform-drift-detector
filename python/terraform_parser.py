
import json
from pathlib import Path
from typing import Any


class TerraformPlanParser:
    """Load and extract drift information from Terraform plan JSON."""

    def __init__(self, plan_file: str | Path):
        self.plan_file = Path(plan_file)

    def load(self) -> dict[str, Any]:
        """Load Terraform plan JSON from disk."""
        if not self.plan_file.exists():
            raise FileNotFoundError(f"Terraform plan file not found: {self.plan_file}")

        with self.plan_file.open("r", encoding="utf-8") as file:
            return json.load(file)

    def get_resource_drift(self) -> list[dict[str, Any]]:
        """Return resources explicitly listed in Terraform resource_drift."""
        plan = self.load()
        return plan.get("resource_drift", [])

    def get_resource_changes(self) -> list[dict[str, Any]]:
        """Return planned resource changes separately from drift."""
        plan = self.load()
        return plan.get("resource_changes", [])

    def get_metadata(self) -> dict[str, Any]:
        """Extract basic Terraform plan metadata."""
        plan = self.load()
        return {
            "terraform_version": plan.get("terraform_version"),
            "format_version": plan.get("format_version"),
        }
