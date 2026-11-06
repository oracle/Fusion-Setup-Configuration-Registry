"""Canonical Fusion opt-in prerequisites for the Fusion ABO workflow.

The task uses these feature codes only for authoritative state reads and for
the scoped handoff to the shared FSM opt-in writer. The writer resolves the
current valid choice short name immediately before an approved update.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FusionAboPrerequisite:
    """A required Fusion feature with stable API and user-facing identities."""

    feature_code: str
    display_name: str


FUSION_ABO_PREREQUISITES = (
    FusionAboPrerequisite("ORA_FOM_ASSET_BASED_ORDERING", "Asset-Based Ordering"),
    FusionAboPrerequisite(
        "ORA_ENABLE_UNIFIED_ORACLE_CPQ_IN_FUSION", "Unified Oracle CPQ in Fusion"
    ),
    FusionAboPrerequisite(
        "ORA_FOM_OSS_INTEGRATION_SUBSCRIPTIONS",
        "Integrate Order Management with Subscription Management to Process Subscriptions",
    ),
    FusionAboPrerequisite(
        "ORA_FOM_OSS_INTEGRATION_COVERAGES",
        "Integrate Order Management with Subscription Management to Process Coverages",
    ),
)

CPQ_ABO_PREREQUISITE_FEATURE_CODES = tuple(
    prerequisite.feature_code for prerequisite in FUSION_ABO_PREREQUISITES[:2]
)
SUBSCRIPTION_COVERAGE_PREREQUISITE_FEATURE_CODES = tuple(
    prerequisite.feature_code for prerequisite in FUSION_ABO_PREREQUISITES[2:]
)
FUSION_ABO_PREREQUISITE_FEATURE_CODES = (
    CPQ_ABO_PREREQUISITE_FEATURE_CODES
    + SUBSCRIPTION_COVERAGE_PREREQUISITE_FEATURE_CODES
)
