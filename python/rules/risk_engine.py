
from typing import Any


ATTRIBUTE_RISK = {
    # Security and network risks
    "ingress": 40,
    "egress": 35,
    "security_groups": 40,
    "vpc_security_group_ids": 40,
    "iam_instance_profile": 40,
    "public_ip": 35,
    "associate_public_ip_address": 35,
    "encrypted": 40,

    # Availability and infrastructure risks
    "instance_type": 20,
    "subnet_id": 25,
    "availability_zone": 20,
    "ami": 25,

    # Cost-related risks
    "volume_size": 15,

    # Metadata changes
    "tags": 5,
    "ManagedBy": 5,
    "Name": 5,
    "Project": 5,
}


RESOURCE_RISK_MULTIPLIERS = {
    "aws_security_group": 1.5,
    "aws_iam_policy": 1.5,
    "aws_iam_role": 1.5,
    "aws_instance": 1.0,
    "aws_s3_bucket": 1.2,
    "aws_ebs_volume": 1.0,
}


class RiskEngine:
    """
    Calculates risk scores for Terraform drift findings.

    Risk scores are project-defined heuristics and are not
    official AWS security ratings.
    """

    def calculate_score(
        self,
        changed_attributes: list[str],
        resource_type: str = "unknown",
    ) -> int:
        """
        Calculate a risk score from 0 to 100.

        Scores are additive and adjusted by a resource multiplier.
        """

        score = 0

        for attribute in changed_attributes:
            leaf = attribute.split(".")[-1]
            leaf = leaf.split("[")[0]

            score += ATTRIBUTE_RISK.get(leaf, 10)

        multiplier = RESOURCE_RISK_MULTIPLIERS.get(
            resource_type,
            1.0,
        )

        score = int(score * multiplier)

        return min(score, 100)

    def classify_risk(self, score: int) -> str:
        """Convert a numeric score into a risk category."""

        if score >= 80:
            return "CRITICAL"

        if score >= 60:
            return "HIGH"

        if score >= 30:
            return "MEDIUM"

        return "LOW"

    def recommend(
        self,
        finding: dict[str, Any],
    ) -> list[str]:
        """Generate recommendations for detected drift."""

        attributes = finding.get(
            "changed_attributes",
            [],
        )

        recommendations = []

        for attribute in attributes:
            leaf = attribute.split(".")[-1]
            leaf = leaf.split("[")[0]

            if leaf in {
                "ingress",
                "egress",
                "security_groups",
                "vpc_security_group_ids",
            }:
                recommendations.append(
                    "Review network access rules and verify "
                    "that the change does not expose services "
                    "or allow unauthorized traffic."
                )

            elif leaf in {
                "iam_instance_profile",
                "iam_role",
            }:
                recommendations.append(
                    "Review IAM permissions and verify that "
                    "the resource follows least privilege."
                )

            elif leaf in {
                "public_ip",
                "associate_public_ip_address",
            }:
                recommendations.append(
                    "Verify whether public network exposure "
                    "is intentional."
                )

            elif leaf == "encrypted":
                recommendations.append(
                    "Verify encryption settings and confirm "
                    "the correct encryption key is being used."
                )

            elif leaf in {
                "instance_type",
                "volume_size",
                "ami",
                "subnet_id",
                "availability_zone",
            }:
                recommendations.append(
                    "Review infrastructure sizing, availability, "
                    "compatibility, and potential cost impact."
                )

            elif leaf in {
                "tags",
                "ManagedBy",
                "Name",
                "Project",
            }:
                recommendations.append(
                    "Verify resource metadata and ensure tags "
                    "match the expected Terraform configuration."
                )

            else:
                recommendations.append(
                    f"Review the changed attribute '{attribute}' "
                    "and compare it against the intended "
                    "Terraform configuration."
                )

        if not recommendations:
            recommendations.append(
                "No specific recommendation available. "
                "Review the resource manually."
            )

        return sorted(set(recommendations))

    def analyze(
        self,
        finding: dict[str, Any],
    ) -> dict[str, Any]:
        """Enrich a drift finding with risk information."""

        attributes = finding.get(
            "changed_attributes",
            [],
        )

        resource_type = finding.get(
            "resource_type",
            "unknown",
        )

        score = self.calculate_score(
            attributes,
            resource_type,
        )

        risk_level = self.classify_risk(
            score,
        )

        recommendations = self.recommend(
            finding,
        )

        finding["risk_score"] = score
        finding["risk_level"] = risk_level
        finding["recommendations"] = recommendations

        return finding
