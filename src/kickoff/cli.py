"""Command line: `kickoff run`, plus the individual steps `extract`, `plan` and `report`."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

import anthropic

from .documents import load_document
from .export import write_jira_csv, write_json
from .extract import extract_contract
from .llm import DEFAULT_EFFORT, DEFAULT_MODEL, Claude, LLMError
from .models import ContractExtract, ProjectPlan
from .plan import build_plan, check_plan, load_playbook
from .report import render_report
from .schedule import schedule_plan
from .traceability import Match, trace_extract


def _iso(value: str) -> date | None:
    try:
        return date.fromisoformat(value) if value else None
    except ValueError:
        return None


def _claude(args) -> Claude:
    return Claude(model=args.model, effort=args.effort)


def do_extract(args, document: str) -> ContractExtract:
    print(f"Reading {args.contract} with {args.model}…")
    extract = extract_contract(document, _claude(args))
    trace = trace_extract(extract, document)
    write_json(Path(args.out) / "extract.json", extract)
    bad = [t for t in trace if t.match is not Match.VERIFIED]
    print(f"  {len(extract.requirements)} requirements, {len(extract.customer_dependencies)} customer dependencies, "
          f"{len(extract.risks)} risks ({sum(r.severity.value == 'high' for r in extract.risks)} high)")
    print(f"  {len(trace) - len(bad)}/{len(trace)} quotes verified against the contract")
    return extract


def do_plan(args, extract: ContractExtract, playbook) -> tuple[ProjectPlan, object, int]:
    print("Building the plan…")
    plan, check, repairs = build_plan(extract, playbook, _claude(args))
    write_json(Path(args.out) / "plan.json", plan)
    tickets = sum(len(e.tickets) for e in plan.epics)
    print(f"  {len(plan.epics)} epics, {tickets} tickets; {len(check.errors)} errors after {repairs} repair round(s)")
    return plan, check, repairs


def do_report(args, document: str, extract: ContractExtract, plan: ProjectPlan, playbook, check=None, repairs=0) -> None:
    out = Path(args.out)
    check = check or check_plan(plan, extract, playbook)
    start = _iso(args.start) if args.start else (_iso(extract.effective_date) or date.today())
    schedule = schedule_plan(plan, start, playbook.holidays, _iso(extract.go_live_date))
    trace = trace_extract(extract, document)
    write_json(out / "traceability.json", [t.__dict__ for t in trace])
    write_jira_csv(out / "jira-import.csv", plan, schedule, extract)
    (out / "kickoff-brief.md").write_text(render_report(extract, plan, schedule, check, trace, playbook, repairs), encoding="utf-8")
    days = schedule.days_vs_contract
    status = "no contract date" if days is None else (f"{days} business days early" if days >= 0 else f"{-days} business days LATE")
    print(f"Projected go-live {schedule.go_live:%d %b %Y} ({status})")
    print(f"Wrote {out / 'kickoff-brief.md'} and {out / 'jira-import.csv'}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="kickoff", description="Turn a signed contract into a kickoff brief, plan and Jira tickets.")
    sub = parser.add_subparsers(dest="command", required=True)

    def common(p, needs_model=True):
        p.add_argument("contract", help="Contract or SOW (.md, .txt or .pdf)")
        p.add_argument("--out", required=True, help="Output folder")
        p.add_argument("--playbook", help="Delivery playbook TOML (defaults to the built-in SaaS playbook)")
        p.add_argument("--start", help="Project start date YYYY-MM-DD (defaults to the contract's effective date)")
        if needs_model:
            p.add_argument("--model", default=DEFAULT_MODEL)
            p.add_argument("--effort", default=DEFAULT_EFFORT, choices=["low", "medium", "high", "xhigh", "max"])

    common(sub.add_parser("run", help="Extract, plan and report in one go"))
    common(sub.add_parser("extract", help="Only read the contract into extract.json"))
    p = sub.add_parser("plan", help="Plan from an existing extract.json")
    common(p)
    r = sub.add_parser("report", help="Rebuild the brief and Jira CSV from saved JSON, without calling Claude")
    common(r, needs_model=False)
    args = parser.parse_args(argv)

    try:
        document = load_document(args.contract)
        playbook = load_playbook(args.playbook)
        out = Path(args.out)
        if args.command == "extract":
            do_extract(args, document)
        elif args.command == "run":
            extract = do_extract(args, document)
            plan, check, repairs = do_plan(args, extract, playbook)
            do_report(args, document, extract, plan, playbook, check, repairs)
        elif args.command == "plan":
            extract = ContractExtract.model_validate_json((out / "extract.json").read_text(encoding="utf-8"))
            plan, check, repairs = do_plan(args, extract, playbook)
            do_report(args, document, extract, plan, playbook, check, repairs)
        else:
            extract = ContractExtract.model_validate_json((out / "extract.json").read_text(encoding="utf-8"))
            plan = ProjectPlan.model_validate_json((out / "plan.json").read_text(encoding="utf-8"))
            do_report(args, document, extract, plan, playbook)
    except (ValueError, FileNotFoundError, LLMError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except anthropic.AuthenticationError:
        print("Error: the Anthropic API key was rejected. Check ANTHROPIC_API_KEY.", file=sys.stderr)
        return 2
    except anthropic.APIError as e:
        print(f"Error from the Anthropic API: {e}", file=sys.stderr)
        return 2
    except TypeError as e:
        if "authentication method" not in str(e):
            raise
        print("Error: no Anthropic credentials found. Set ANTHROPIC_API_KEY or run `ant auth login`.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
