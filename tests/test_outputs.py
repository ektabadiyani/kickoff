import csv
from datetime import date

from kickoff.export import write_jira_csv
from kickoff.plan import check_plan, load_playbook
from kickoff.report import render_report
from kickoff.schedule import schedule_plan
from kickoff.traceability import trace_extract


def test_jira_csv_links_tasks_to_epics(tmp_path, plan, extract):
    s = schedule_plan(plan, date(2026, 11, 2))
    path = tmp_path / "jira.csv"
    write_jira_csv(path, plan, s, extract)
    with open(path, newline="") as f:
        rows = list(csv.reader(f))
    header, body = rows[0], rows[1:]
    assert header.count("Labels") == 2
    epics = {r[0]: r for r in body if r[2] == "Epic"}
    tasks = [r for r in body if r[2] == "Task"]
    assert len(epics) == 4 and len(tasks) == 6
    assert all(t[1] in epics for t in tasks)
    t003 = next(t for t in tasks if t[3].startswith("T003"))
    assert "R01 (§2.4)" in t003[4] and t003[7] == str(60 * 3600)


def test_report_has_the_key_sections(plan, extract, document):
    playbook = load_playbook()
    s = schedule_plan(plan, date(2026, 11, 2), playbook.holidays, date(2027, 1, 15))
    report = render_report(extract, plan, s, check_plan(plan, extract, playbook), trace_extract(extract, document), playbook)
    for heading in ["## Headline", "## Contract risks to resolve at kickoff", "## Timeline",
                    "## Customer responsibilities", "## Effort and cost", "## Requirements traceability"]:
        assert heading in report
    assert "business days before the contract date" in report
    assert "| R01 | NetSuite integration | §2.4 | verified | T003 |" in report
    assert "1 of these is a customer task" in report
