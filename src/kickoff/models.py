"""Data shapes for what is read out of a contract and the plan built from it.

The models double as the JSON schemas Claude must answer in, so field descriptions are
written as instructions to the model as well as documentation.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------- contract extraction

class Category(StrEnum):
    PROJECT_MANAGEMENT = "project_management"
    DISCOVERY = "discovery"
    CONFIGURATION = "configuration"
    INTEGRATION = "integration"
    DATA_MIGRATION = "data_migration"
    SECURITY = "security"
    REPORTING = "reporting"
    TRAINING = "training"
    TESTING = "testing"
    GO_LIVE = "go_live"
    SUPPORT = "support"
    OTHER = "other"


class Severity(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RiskType(StrEnum):
    AMBIGUOUS_SCOPE = "ambiguous_scope"
    CONTRADICTION = "contradiction"
    MISSING_ACCEPTANCE_CRITERIA = "missing_acceptance_criteria"
    UNQUANTIFIED = "unquantified"
    CUSTOMER_DEPENDENCY = "customer_dependency"
    TIMELINE = "timeline"
    COMMERCIAL = "commercial"


class Source(Strict):
    section: str = Field(description="Clause number as written in the contract, e.g. '2.4'. Empty string if unnumbered.")
    quote: str = Field(description="Exact words copied from the contract that support this item. Copy verbatim, do not paraphrase.")


class Requirement(Strict):
    id: str = Field(description="Stable id like R01, R02 in contract order.")
    category: Category
    title: str = Field(description="Short name, under 8 words.")
    description: str = Field(description="What the vendor must deliver, in plain language.")
    acceptance_criteria: list[str] = Field(description="Testable conditions for this to count as done. Use numbers stated in the contract. Empty if the contract gives none.")
    source: Source


class CustomerDependency(Strict):
    id: str = Field(description="Stable id like C01.")
    description: str
    due: str = Field(description="When it is due, as the contract states it, e.g. 'within 5 business days of kickoff'.")
    blocks: list[str] = Field(description="Ids of requirements that cannot finish until this is done.")
    source: Source


class Milestone(Strict):
    name: str
    date: str = Field(description="ISO date (YYYY-MM-DD) if the contract states one, else empty string.")
    source: Source


class PaymentTerm(Strict):
    trigger: str = Field(description="The event that triggers the invoice, e.g. 'completion of UAT'.")
    percent: float = Field(description="Percent of the total fee, 0-100. 0 if stated only as an amount.")
    amount: float = Field(description="Amount in the contract currency if computable, else 0.")
    source: Source


class Risk(Strict):
    id: str = Field(description="Stable id like K01.")
    type: RiskType
    severity: Severity
    description: str = Field(description="What could go wrong and why, in one or two sentences.")
    recommendation: str = Field(description="What the implementation lead should do about it, starting with a verb.")
    source: Source


class ContractExtract(Strict):
    vendor: str
    customer: str
    effective_date: str = Field(description="ISO date if stated, else empty string.")
    go_live_date: str = Field(description="Contractual or target go-live date as ISO, else empty string.")
    total_fee: float = Field(description="Total implementation fee, 0 if not stated.")
    currency: str
    requirements: list[Requirement]
    customer_dependencies: list[CustomerDependency]
    milestones: list[Milestone]
    out_of_scope: list[Source] = Field(description="Each exclusion, one per item, with its clause.")
    payment_terms: list[PaymentTerm]
    risks: list[Risk]


# ---------------------------------------------------------------- plan generation

class Role(StrEnum):
    IMPLEMENTATION_LEAD = "implementation_lead"
    SOLUTIONS_CONSULTANT = "solutions_consultant"
    INTEGRATION_ENGINEER = "integration_engineer"
    DATA_SPECIALIST = "data_specialist"
    TRAINER = "trainer"
    SUPPORT_ENGINEER = "support_engineer"
    CUSTOMER = "customer"


class Ticket(Strict):
    id: str = Field(description="Stable id like T001, unique across the plan.")
    title: str = Field(description="Imperative, under 10 words, e.g. 'Configure approval workflows for US entity'.")
    description: str
    acceptance_criteria: list[str] = Field(description="Testable conditions. Reuse the requirement's criteria where they apply.")
    role: Role = Field(description="Who does the work. Use 'customer' for customer-owned tasks.")
    estimate_hours: float = Field(description="Realistic effort in hours for the assigned role. 0 only for customer waiting time.")
    duration_days: int = Field(description="Business days this takes on the calendar, including waiting on others. At least 1.")
    depends_on: list[str] = Field(description="Ids of tickets that must finish before this one can start.")
    requirement_ids: list[str] = Field(description="Requirement or customer-dependency ids this ticket delivers. Empty only for standard project tasks.")


class Epic(Strict):
    id: str = Field(description="Stable id like E01.")
    phase: str = Field(description="One of the playbook phase names, exactly as given.")
    title: str
    goal: str = Field(description="One sentence: what is true when this epic is done.")
    tickets: list[Ticket]


class ProjectPlan(Strict):
    epics: list[Epic]
    assumptions: list[str] = Field(description="Planning assumptions not stated in the contract, so they can be confirmed with the customer.")
