"""Write the plan as a Jira CSV import and as JSON."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from .models import ContractExtract, ProjectPlan
from .schedule import Schedule

JIRA_COLUMNS = ["Issue Id", "Parent Id", "Issue Type", "Summary", "Description",
                "Labels", "Labels", "Original Estimate", "Start date", "Due date"]


def _label(text: str) -> str:
    return text.lower().replace(" ", "-")


def write_jira_csv(path: str | Path, plan: ProjectPlan, schedule: Schedule, extract: ContractExtract) -> None:
    """Jira's CSV importer links stories to epics through the numeric Issue Id / Parent Id
    columns. Map "Labels" twice so each ticket gets both a phase and a role label."""
    by_id = {i.ticket.id: i for i in schedule.items}
    sources = {r.id: r.source.section for r in extract.requirements}
    sources |= {c.id: c.source.section for c in extract.customer_dependencies}
    numeric = {}
    rows = []
    next_id = 1
    for epic in plan.epics:
        numeric[epic.id] = next_id
        dates = [by_id[t.id] for t in epic.tickets if t.id in by_id]
        start = min(d.start for d in dates).isoformat() if dates else ""
        due = max(d.finish for d in dates).isoformat() if dates else ""
        rows.append([next_id, "", "Epic", f"{epic.id} · {epic.title}", f"{epic.goal}\n\nPhase: {epic.phase}",
                     _label(epic.phase), "", "", start, due])
        next_id += 1
        for t in epic.tickets:
            numeric[t.id] = next_id
            next_id += 1
    for epic in plan.epics:
        for t in epic.tickets:
            item = by_id[t.id]
            lines = [t.description, ""]
            if t.acceptance_criteria:
                lines += ["Acceptance criteria:"] + [f"- {c}" for c in t.acceptance_criteria] + [""]
            if t.depends_on:
                lines.append("Blocked by: " + ", ".join(t.depends_on))
            if t.requirement_ids:
                refs = [f"{r} (§{sources[r]})" if sources.get(r) else r for r in t.requirement_ids]
                lines.append("Contract: " + ", ".join(refs))
            lines.append(f"Plan id: {t.id}{' · on the critical path' if item.critical else ''}")
            rows.append([numeric[t.id], numeric[epic.id], "Task", f"{t.id} · {t.title}", "\n".join(lines),
                         _label(epic.phase), _label(t.role.value), int(round(t.estimate_hours * 3600)),
                         item.start.isoformat(), item.finish.isoformat()])
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(JIRA_COLUMNS)
        writer.writerows(rows)


def write_json(path: str | Path, data) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if hasattr(data, "model_dump_json"):
        path.write_text(data.model_dump_json(indent=2), encoding="utf-8")
    else:
        path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
