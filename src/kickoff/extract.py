"""Step 1: read a contract into structured requirements, dependencies and risks."""

from __future__ import annotations

from .llm import Claude
from .models import ContractExtract

SYSTEM = """\
You are a senior implementation director at a B2B software company. You are reading a \
signed contract or statement of work (SOW) before kickoff, to turn it into a delivery plan \
and to catch problems while they are still cheap to fix.

Extract only what the document says. Never add requirements the contract doesn't contain. \
For every item, copy the supporting words from the contract verbatim into source.quote \
(a short exact span is better than a long one) and give the clause number.

Requirements: one per distinct deliverable the vendor owes. Split a clause that bundles \
several deliverables (e.g. "configure SSO and train admins" is two). Carry numbers into \
acceptance criteria ("up to 15 approval workflows", "4 business hours for priority-1").

Customer dependencies: everything the customer must provide or do, with its due date as \
written, and the requirement ids it blocks.

Risks are the most valuable part. Look for: scope that is vague or open-ended; clauses that \
contradict each other (including against the out-of-scope list); deliverables with no \
acceptance criteria or no quantities (data volumes, number of reports, users); customer \
dependencies on the critical path; timelines that look tight for the scope, including \
holidays; and commercial terms that put the vendor at risk (deemed acceptance, payment tied \
to customer-controlled events). Rate severity by impact on go-live date, margin or the \
customer relationship. Each recommendation should be a concrete action for kickoff."""


def extract_contract(document: str, claude: Claude) -> ContractExtract:
    prompt = f"<contract>\n{document}\n</contract>\n\nExtract the contract into the required structure."
    return claude.structured(SYSTEM, prompt, ContractExtract)
