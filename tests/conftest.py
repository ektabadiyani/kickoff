"""Hand-written fixtures shaped like Claude's output for the sample SOW, so tests run offline."""

from pathlib import Path

import pytest

from kickoff.models import (ContractExtract, CustomerDependency, Epic, Milestone, PaymentTerm, ProjectPlan,
                            Requirement, Risk, Source, Ticket)

SAMPLE = Path(__file__).resolve().parent.parent / "data" / "sample" / "sow-harbor-logistics.md"


@pytest.fixture
def document() -> str:
    return SAMPLE.read_text(encoding="utf-8")


@pytest.fixture
def extract() -> ContractExtract:
    return ContractExtract(
        vendor="Ledgerline, Inc.", customer="Harbor Logistics Group, LLC",
        effective_date="2026-11-02", go_live_date="2027-01-15", total_fee=48000, currency="USD",
        requirements=[
            Requirement(id="R01", category="integration", title="NetSuite integration",
                        description="Sync vendors, POs, GL accounts and bills with NetSuite.",
                        acceptance_criteria=["Payment status posts back to NetSuite"],
                        source=Source(section="2.4", quote="The NetSuite integration will sync vendors, purchase orders, GL accounts and approved bills")),
            Requirement(id="R02", category="security", title="Okta SSO",
                        description="Configure SAML SSO with Okta.", acceptance_criteria=[],
                        source=Source(section="2.8", quote="configure SAML single sign-on with the Customer's identity provider (Okta)")),
        ],
        customer_dependencies=[
            CustomerDependency(id="C01", description="Provide NetSuite sandbox access",
                               due="within five (5) business days of kickoff", blocks=["R01"],
                               source=Source(section="4.2", quote="The Customer will provide NetSuite sandbox access")),
        ],
        milestones=[Milestone(name="Go-live", date="2027-01-15",
                              source=Source(section="3.1", quote="go-live for all three entities on January 15, 2027"))],
        out_of_scope=[Source(section="6", quote="on-site services")],
        payment_terms=[PaymentTerm(trigger="go-live", percent=30, amount=14400,
                                   source=Source(section="8.1", quote="30% on go-live"))],
        risks=[Risk(id="K01", type="contradiction", severity="high",
                    description="2.4 allows 'any other systems' but section 6 excludes them.",
                    recommendation="Confirm in writing that only NetSuite and Okta are in scope.",
                    source=Source(section="2.4", quote="any other systems as reasonably required by the Customer"))],
    )


def ticket(tid, role="integration_engineer", hours=12.0, days=2, deps=(), reqs=()):
    return Ticket(id=tid, title=f"Task {tid}", description="d", acceptance_criteria=["done"], role=role,
                  estimate_hours=hours, duration_days=days, depends_on=list(deps), requirement_ids=list(reqs))


@pytest.fixture
def plan() -> ProjectPlan:
    return ProjectPlan(
        epics=[
            Epic(id="E01", phase="Initiate", title="Kickoff", goal="Project mobilised",
                 tickets=[ticket("T001", "implementation_lead", 6, 1)]),
            Epic(id="E02", phase="Integrate", title="NetSuite", goal="NetSuite connected",
                 tickets=[ticket("T002", "customer", 0, 5, ["T001"], ["C01"]),
                          ticket("T003", "integration_engineer", 60, 10, ["T002"], ["R01"]),
                          ticket("T004", "solutions_consultant", 8, 2, ["T001"], ["R02"])]),
            Epic(id="E03", phase="Launch", title="Go-live", goal="Live",
                 tickets=[ticket("T005", "implementation_lead", 6, 1, ["T003", "T004"])]),
            Epic(id="E04", phase="Hypercare", title="Hypercare", goal="Stable",
                 tickets=[ticket("T006", "support_engineer", 40, 20, ["T005"])]),
        ],
        assumptions=["One NetSuite sandbox is available."],
    )
