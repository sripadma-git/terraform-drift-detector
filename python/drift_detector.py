
from typing import Any


HIGH_RISK_ATTRIBUTES = {
    "ingress",
    "egress",
    "security_groups",
    "vpc_security_group_ids",
    "iam_instance_profile",
    "public_ip",
    "associate_public_ip_address",
    "encrypted",
}

MEDIUM_RISK_ATTRIBUTES = {
    "instance_type",
    "volume_size",
    "ami",
    "subnet_id",
    "availability_zone",
}


def find_differences(
    before: Any,
    after: Any,
    prefix: str = "",
) -> list[str]:
    differences = []

    # Ignore null versus empty tag maps
    if prefix.endswith(".tags") or prefix.endswith(".tags_all"):
        if before is None and after == {}:
            return []
        if after is None and before == {}:
            return []

    if isinstance(before, dict) and isinstance(after, dict):
        all_keys = set(before.keys()) | set(after.keys())

        for key in sorted(all_keys):
            path = f"{prefix}.{key}" if prefix else key

            differences.extend(
                find_differences(
                    before.get(key),
                    after.get(key),
                    path,
                )
            )

    elif isinstance(before, list) and isinstance(after, list):
        if len(before) != len(after):
            differences.append(prefix)
        else:
            for index, (left, right) in enumerate(zip(before, after)):
                path = f"{prefix}[{index}]"

                differences.extend(
                    find_differences(left, right, path)
                )

    elif before != after:
        differences.append(prefix)

    return differences


def normalize_attributes(
    changed_attributes: list[str],
) -> list[str]:
    """
    Normalize duplicate Terraform attributes.

    tags_all is a computed representation of tags.
    We keep tags as the canonical representation.
    """

    normalized = set()

    for attribute in changed_attributes:
        attribute = attribute.replace("tags_all.", "tags.")
        normalized.add(attribute)

    return sorted(normalized)


def classify_severity(
    changed_attributes: list[str],
) -> str:
    attributes = set(changed_attributes)

    leaf_attributes = {
        path.split(".")[-1].split("[")[0]
        for path in attributes
    }

    if leaf_attributes & HIGH_RISK_ATTRIBUTES:
        return "HIGH"

    if leaf_attributes & MEDIUM_RISK_ATTRIBUTES:
        return "MEDIUM"

    return "LOW"


class DriftDetector:

    def __init__(
        self,
        resource_drift: list[dict[str, Any]],
    ):
        self.resource_drift = resource_drift

    def analyze(self) -> list[dict[str, Any]]:
        findings = []

        for resource in self.resource_drift:
            change = resource.get("change", {})

            before = change.get("before") or {}
            after = change.get("after") or {}

            raw_attributes = find_differences(
                before,
                after,
            )

            changed_attributes = normalize_attributes(
                raw_attributes
            )

            severity = classify_severity(
                changed_attributes
            )

            finding = {
                "resource_address": resource.get(
                    "address",
                    "unknown",
                ),
                "resource_type": resource.get(
                    "type",
                    "unknown",
                ),
                "actions": change.get(
                    "actions",
                    [],
                ),
                "changed_attributes": changed_attributes,
                "severity": severity,
                "before": before,
                "after": after,
            }

            findings.append(finding)

        return findings
