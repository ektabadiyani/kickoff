"""The kickoff brief: one Markdown document an implementation lead can take into kickoff
and a services leader can read in five minutes."""

from __future__ import annotations

from collections import defaultdict

from .models import ContractExtract, ProjectPlan, Severity
from .plan import PlanCheck, Playbook
from .schedule import Schedule
from .traceability import Match, TraceResult

SEVERITY_ORDER = {Severity.HIGH: 0, Severity.MEDIUM: 1, Severity.LOW: 2}


def _money(value: float, currency: str) -> str:
    symbol = {"USD": "$", "CAD": "CA$", "EUR": "€", "GBP": "£"}.get(currency.upper(), "")
    return f"{symbol}{value:,.0f}" if symbol else f"{value:,.0f} {currency}"


def _cell(text: str) -> str:
    return " ".join(text.split()).replace("|", "\\|")


def _n(count: int, word: str) -> str:
    return f"{count} {word}{'' if count == 1 else 's'}"


def _d(d) -> str:
    return d.strftime("%a %d %b %Y")


def render_report(
    extract: ContractExtract,
    plan: ProjectPlan,
    schedule: Schedule,
    check: PlanCheck,
    trace: list[TraceResult],
    playbook: Playbook,
    repairs: int = 0,
) -> str:
    tickets = [t for e in plan.epics for t in e.tickets]
    by_ticket = {i.ticket.id: i for i in schedule.items}
    hours_by_role: dict[str, float] = defaultdict(float)
    for t in tickets:
        hours_by_role[t.role.value] += t.estimate_hours
    cost = sum(h * playbook.role_cost.get(role, 0) for role, h in hours_by_role.items())
    vendor_hours = sum(h for role, h in hours_by_role.items() if role != "customer")
    margin = (extract.total_fee - cost) / extract.total_fee if extract.total_fee else None
    risks = sorted(extract.risks, key=lambda r: (SEVERITY_ORDER[r.severity], r.id))
    high = [r for r in risks if r.severity is Severity.HIGH]
    unverified = [t for t in trace if t.match is not Match.VERIFIED]

    out = [f"# Kickoff brief: {extract.customer}", ""]
    out += [f"{extract.vendor} implementation for {extract.customer}. Generated from the signed contract; "
            "every requirement links back to the clause it came from.", ""]

    # --- headline
    days = schedule.days_vs_contract
    if days is None:
        verdict = f"Projected go-live **{_d(schedule.go_live)}**. The contract states no go-live date."
    elif days >= 0:
        verdict = (f"Projected go-live **{_d(schedule.go_live)}**, {days} business days before the contract date "
                   f"of {_d(schedule.contract_go_live)}.")
    else:
        verdict = (f"**At risk:** projected go-live is **{_d(schedule.go_live)}**, {-days} business days after the "
                   f"contract date of {_d(schedule.contract_go_live)}, even if every task starts as early as possible.")
    out += ["## Headline", "", f"- {verdict}"]
    out.append(f"- **{_n(len(high), 'high-severity contract risk')}** to resolve at kickoff (of {len(risks)} found).")
    out.append(f"- **{len(plan.epics)} epics, {len(tickets)} tickets**, {vendor_hours:,.0f} delivery hours "
               f"(plus {hours_by_role.get('customer', 0):,.0f} customer hours).")
    if extract.total_fee:
        out.append(f"- **Estimated delivery cost {_money(cost, extract.currency)}** against a fee of "
                   f"{_money(extract.total_fee, extract.currency)}: projected services margin **{margin:.0%}**.")
    out.append(f"- **Traceability:** {len(trace) - len(unverified)} of {len(trace)} contract references verified "
               "word for word against the document." + (f" {len(unverified)} need a look (see the end)." if unverified else ""))
    out.append("")

    # --- risks
    out += ["## Contract risks to resolve at kickoff", "", "| | Risk | Clause | Recommendation |", "|---|---|---|---|"]
    for r in risks:
        out.append(f"| {r.severity.value.upper()} · {r.type.value.replace('_', ' ')} | {_cell(r.description)} | "
                   f"§{r.source.section} | {_cell(r.recommendation)} |")
    if not risks:
        out.append("| | None found | | |")

    # --- timeline
    out += ["", "## Timeline", "", "| Phase | Start | Finish | Tickets |", "|---|---|---|---|"]
    phases: dict[str, list] = defaultdict(list)
    for item in schedule.items:
        phases[item.epic.phase].append(item)
    for phase in playbook.phase_names:
        if phase in phases:
            items = phases[phase]
            out.append(f"| {phase} | {_d(min(i.start for i in items))} | {_d(max(i.finish for i in items))} | {len(items)} |")
    out += ["", "**What sets the go-live date.** Delay any of these and go-live moves by the same amount:", ""]
    for item in schedule.path_to_go_live:
        who = "customer" if item.ticket.role.value == "customer" else item.ticket.role.value.replace("_", " ")
        out.append(f"1. {item.ticket.id} {item.ticket.title} ({who}, {_n(item.ticket.duration_days, 'day')}, "
                   f"{item.start:%d %b}–{item.finish:%d %b})")
    customer_on_path = [i for i in schedule.path_to_go_live if i.ticket.role.value == "customer"]
    if customer_on_path:
        n = len(customer_on_path)
        out += ["", f"{n} of these {'is a customer task' if n == 1 else 'are customer tasks'}. "
                "Agree owners and dates for them at kickoff."]

    # --- customer dependencies
    out += ["", "## Customer responsibilities", "", "| Id | What | Due (contract) | Planned finish | Clause |", "|---|---|---|---|---|"]
    for c in extract.customer_dependencies:
        finishes = [by_ticket[t.id].finish for t in tickets if c.id in t.requirement_ids and t.id in by_ticket]
        planned = _d(max(finishes)) if finishes else "not planned"
        out.append(f"| {c.id} | {_cell(c.description)} | {_cell(c.due)} | {planned} | §{c.source.section} |")

    # --- effort
    out += ["", "## Effort and cost", "", "| Role | Hours | Cost |", "|---|---|---|"]
    for role, hours in sorted(hours_by_role.items(), key=lambda kv: -kv[1]):
        out.append(f"| {role.replace('_', ' ')} | {hours:,.0f} | {_money(hours * playbook.role_cost.get(role, 0), extract.currency)} |")
    out.append(f"| **Total** | **{sum(hours_by_role.values()):,.0f}** | **{_money(cost, extract.currency)}** |")
    if extract.payment_terms:
        out += ["", "Payment milestones:", ""]
        for p in extract.payment_terms:
            amount = p.amount or extract.total_fee * p.percent / 100
            out.append(f"- {p.percent:.0f}% ({_money(amount, extract.currency)}) on {p.trigger} (§{p.source.section})")

    # --- traceability
    tickets_for: dict[str, list[str]] = defaultdict(list)
    for t in tickets:
        for r in t.requirement_ids:
            tickets_for[r].append(t.id)
    match_of = {t.item_id: t.match for t in trace}
    out += ["", "## Requirements traceability", "",
            "| Id | Requirement | Clause | Quote check | Tickets |", "|---|---|---|---|---|"]
    for r in extract.requirements:
        out.append(f"| {r.id} | {_cell(r.title)} | §{r.source.section} | {match_of.get(r.id, Match.NOT_FOUND).value} | "
                   f"{', '.join(tickets_for.get(r.id, [])) or '**none**'} |")

    out += ["", "## Out of scope", ""]
    out += [f"- {_cell(x.quote)} (§{x.section})" for x in extract.out_of_scope] or ["- None stated."]
    out += ["", "## Assumptions to confirm with the customer", ""]
    out += [f"- {a}" for a in plan.assumptions] or ["- None."]

    # --- quality
    out += ["", "## Plan quality checks", ""]
    out.append(f"- Automated checks: {len(check.errors)} errors, {len(check.issues) - len(check.errors)} warnings"
               + (f" after {repairs} repair round(s)." if repairs else "."))
    out += [f"- {i.severity.upper()}: {i.message}" for i in check.issues]
    if unverified:
        out += ["", "Contract references that did not match the document word for word:", "",
                "| Item | Kind | Clause | Match | Quote |", "|---|---|---|---|---|"]
        out += [f"| {t.item_id} | {t.kind} | §{t.section} | {t.match.value} ({t.similarity:.0%}) | {_cell(t.quote)} |" for t in unverified]
    out += ["", "## Method", "",
            "- Requirements, dependencies and risks were extracted from the contract by Claude, with a verbatim quote "
            "for each. Every quote was then matched against the document by code, not by the model.",
            "- The plan was generated against the delivery playbook and checked automatically for coverage (every "
            "requirement has a ticket), missing or circular dependencies, and unknown phases.",
            "- Dates use the critical path method over business days, skipping weekends and the playbook's holidays. "
            "They assume people are available when each task can start, so they are the earliest achievable dates.",
            f"- Cost uses the playbook's loaded hourly rates ({playbook.name}).", ""]
    return "\n".join(out)
