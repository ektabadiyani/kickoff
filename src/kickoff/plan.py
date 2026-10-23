"""Step 2: turn the extracted contract into epics and tickets, then check the result.

Generation is done by Claude; checking is deterministic. If the checks find structural
errors (a requirement with no ticket, a dependency loop, a ticket depending on one that
doesn't exist), the errors are sent back to Claude for one repair attempt.
"""

from __future__ import annotations

import json
import tomllib
from dataclasses import dataclass, field
from datetime import date
from importlib import resources
from pathlib import Path

from .llm import Claude
from .models import ContractExtract, ProjectPlan, Role


@dataclass(frozen=True)
class Phase:
    name: str
    purpose: str
    standard_tasks: tuple[str, ...]


@dataclass(frozen=True)
class Playbook:
    name: str
    hours_per_day: float
    holidays: frozenset[date]
    role_cost: dict[str, float]
    phases: tuple[Phase, ...]

    @property
    def phase_names(self) -> list[str]:
        return [p.name for p in self.phases]


def load_playbook(path: str | Path | None = None) -> Playbook:
    if path is None:
        text = resources.files("kickoff").joinpath("playbooks/saas-implementation.toml").read_text(encoding="utf-8")
    else:
        text = Path(path).read_text(encoding="utf-8")
    data = tomllib.loads(text)
    unknown = set(data.get("roles", {})) - {r.value for r in Role}
    if unknown:
        raise ValueError(f"Unknown roles in playbook: {sorted(unknown)}. Allowed: {[r.value for r in Role]}")
    return Playbook(
        name=data.get("name", "Playbook"),
        hours_per_day=float(data.get("hours_per_day", 6)),
        holidays=frozenset(date.fromisoformat(d) if isinstance(d, str) else d for d in data.get("holidays", [])),
        role_cost={k: float(v) for k, v in data.get("roles", {}).items()},
        phases=tuple(Phase(p["name"], p.get("purpose", ""), tuple(p.get("standard_tasks", []))) for p in data["phases"]),
    )


# ---------------------------------------------------------------- checks

@dataclass(frozen=True)
class Issue:
    severity: str   # "error" blocks scheduling or breaks traceability; "warning" is worth a look
    message: str


@dataclass
class PlanCheck:
    issues: list[Issue] = field(default_factory=list)

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == "error"]

    def add(self, severity: str, message: str) -> None:
        self.issues.append(Issue(severity, message))


def find_cycle(edges: dict[str, list[str]]) -> list[str] | None:
    """Return one dependency cycle as a list of ids, or None."""
    state: dict[str, int] = {}  # 1 = on the current path, 2 = fully explored
    path: list[str] = []

    def visit(node: str) -> list[str] | None:
        state[node] = 1
        path.append(node)
        for nxt in edges.get(node, []):
            if state.get(nxt) == 1:
                return path[path.index(nxt):] + [nxt]
            if nxt not in state and (cycle := visit(nxt)):
                return cycle
        path.pop()
        state[node] = 2
        return None

    for node in edges:
        if node not in state and (cycle := visit(node)):
            return cycle
    return None


def check_plan(plan: ProjectPlan, extract: ContractExtract, playbook: Playbook) -> PlanCheck:
    check = PlanCheck()
    tickets = [t for e in plan.epics for t in e.tickets]
    ids = [t.id for t in tickets]
    known = set(ids)

    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        check.add("error", f"Duplicate ticket ids: {', '.join(duplicates)}")
    for epic in plan.epics:
        if epic.phase not in playbook.phase_names:
            check.add("error", f"Epic {epic.id} uses unknown phase '{epic.phase}'")
    for t in tickets:
        missing = [d for d in t.depends_on if d not in known]
        if missing:
            check.add("error", f"{t.id} depends on tickets that don't exist: {', '.join(missing)}")
        if t.id in t.depends_on:
            check.add("error", f"{t.id} depends on itself")
        if t.duration_days < 1:
            check.add("error", f"{t.id} has a duration under 1 business day")
        if t.role != Role.CUSTOMER and t.estimate_hours <= 0:
            check.add("warning", f"{t.id} has no effort estimate")

    cycle = find_cycle({t.id: [d for d in t.depends_on if d in known] for t in tickets})
    if cycle:
        check.add("error", "Dependency loop: " + " → ".join(cycle))

    covered = {r for t in tickets for r in t.requirement_ids}
    for r in extract.requirements:
        if r.id not in covered:
            check.add("error", f"Requirement {r.id} ({r.title}, §{r.source.section}) has no ticket")
    for c in extract.customer_dependencies:
        if c.id not in covered:
            check.add("error", f"Customer dependency {c.id} ({c.description[:60]}) has no ticket")
    valid_refs = {r.id for r in extract.requirements} | {c.id for c in extract.customer_dependencies}
    for t in tickets:
        unknown = [r for r in t.requirement_ids if r not in valid_refs]
        if unknown:
            check.add("warning", f"{t.id} cites requirement ids that don't exist: {', '.join(unknown)}")
    return check


# ---------------------------------------------------------------- generation

SYSTEM = """\
You are a senior implementation director building the delivery plan for a signed contract. \
You will receive the requirements, customer dependencies, exclusions and risks already \
extracted from the contract, plus the company's delivery playbook.

Build epics and tickets that a delivery team could load into Jira tomorrow:
- Use the playbook phases, in order, as the epics' phases. A phase may have more than one \
epic (e.g. one integration epic per system). Skip a phase only if nothing in the contract needs it.
- Include the playbook's standard tasks where they apply, adapted to this customer.
- Every requirement id and every customer-dependency id must appear in the requirement_ids \
of at least one ticket. Customer dependencies become tickets with role "customer".
- Never plan work the exclusions rule out. Where a risk calls for an action at kickoff \
(clarify scope, raise a change order, confirm a date), add a ticket for it.
- Split work per entity, system or deliverable when the contract counts them.
- Dependencies must reflect real sequencing and must not loop. A customer task blocks the \
vendor tasks that need its output.
- Estimates are effort hours for one person in the given role. Duration is elapsed business \
days, including waiting time, and is never less than effort / 6 hours.
- Ticket ids are T001, T002, ... in plan order. Epic ids are E01, E02, ...
- List any planning assumption the contract doesn't settle (data volumes, number of users, \
environments) so it can be confirmed at kickoff. Don't put calendar dates or timing in \
assumptions or tickets: a scheduler computes all dates from your durations and dependencies."""


def _prompt(extract: ContractExtract, playbook: Playbook) -> str:
    contract = extract.model_dump(mode="json", include={
        "customer", "go_live_date", "requirements", "customer_dependencies", "out_of_scope", "risks", "milestones"})
    phases = [{"name": p.name, "purpose": p.purpose, "standard_tasks": list(p.standard_tasks)} for p in playbook.phases]
    roles = [r.value for r in Role]
    return (
        f"<contract_extract>\n{json.dumps(contract, indent=1)}\n</contract_extract>\n\n"
        f"<playbook_phases>\n{json.dumps(phases, indent=1)}\n</playbook_phases>\n\n"
        f"Allowed roles: {', '.join(roles)}.\n\nBuild the project plan."
    )


def build_plan(
    extract: ContractExtract, playbook: Playbook, claude: Claude, max_repairs: int = 1
) -> tuple[ProjectPlan, PlanCheck, int]:
    """Returns the plan, its check results, and how many repair rounds were used."""
    prompt = _prompt(extract, playbook)
    plan = claude.structured(SYSTEM, prompt, ProjectPlan)
    check = check_plan(plan, extract, playbook)
    repairs = 0
    while check.errors and repairs < max_repairs:
        repairs += 1
        problems = "\n".join(f"- {i.message}" for i in check.errors)
        repair_prompt = (
            f"{prompt}\n\nA previous draft of the plan failed these checks:\n{problems}\n\n"
            f"<previous_draft>\n{plan.model_dump_json(indent=1)}\n</previous_draft>\n\n"
            "Return the complete corrected plan. Keep everything that was fine; fix only what the checks list."
        )
        plan = claude.structured(SYSTEM, repair_prompt, ProjectPlan)
        check = check_plan(plan, extract, playbook)
    return plan, check, repairs
