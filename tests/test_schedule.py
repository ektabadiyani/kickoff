from datetime import date

import pytest

from kickoff.schedule import WorkCalendar, schedule_plan

HOLIDAYS = frozenset({date(2026, 11, 26), date(2026, 11, 27)})


def test_calendar_skips_weekends_and_holidays():
    cal = WorkCalendar(date(2026, 11, 21), HOLIDAYS)  # a Saturday
    assert cal.start == date(2026, 11, 23)             # Monday
    assert cal.date(2) == date(2026, 11, 25)           # Wednesday
    assert cal.date(3) == date(2026, 11, 30)           # Thanksgiving Thu/Fri and the weekend skipped
    assert cal.index(date(2026, 11, 30)) == 3


def test_critical_path_and_go_live(plan):
    s = schedule_plan(plan, date(2026, 11, 2), contract_go_live=date(2026, 12, 31))
    by_id = {i.ticket.id: i for i in s.items}
    # T001 (1 day) -> T002 customer (5) -> T003 (10) -> T005 go-live (1) = 17 business days
    assert by_id["T005"].early_finish == 17
    assert s.go_live_ticket == "T005"
    assert s.go_live == date(2026, 11, 24)
    assert [i.ticket.id for i in s.path_to_go_live] == ["T001", "T002", "T003", "T005"]
    assert by_id["T004"].slack == 13 and not by_id["T004"].critical
    assert by_id["T003"].critical
    assert s.feasible and s.days_vs_contract > 0


def test_late_plan_reports_negative_buffer(plan):
    s = schedule_plan(plan, date(2026, 11, 2), contract_go_live=date(2026, 11, 20))
    assert s.days_vs_contract == -2 and s.feasible is False


def test_dependency_loop_is_rejected(plan):
    plan.epics[0].tickets[0].depends_on.append("T005")
    with pytest.raises(ValueError):  # graphlib.CycleError is a ValueError
        schedule_plan(plan, date(2026, 11, 2))
