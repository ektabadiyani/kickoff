"""Step 3: put the plan on a calendar and test it against the contract's go-live date.

Uses the critical path method: each ticket starts as soon as everything it depends on is
finished. That gives the earliest achievable dates if people are available when needed,
so a plan that misses the contract date here will certainly miss it in practice.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from graphlib import TopologicalSorter

from .models import Epic, ProjectPlan, Ticket


class WorkCalendar:
    """Business days from a start date, skipping weekends and holidays. Day 0 is the
    first business day on or after the start date."""

    def __init__(self, start: date, holidays: frozenset[date] = frozenset()):
        self.holidays = holidays
        self.days: list[date] = []
        current = start
        while not self._working(current):
            current += timedelta(days=1)
        self.start = current

    def _working(self, d: date) -> bool:
        return d.weekday() < 5 and d not in self.holidays

    def date(self, index: int) -> date:
        if not self.days:
            self.days.append(self.start)
        while len(self.days) <= index:
            nxt = self.days[-1] + timedelta(days=1)
            while not self._working(nxt):
                nxt += timedelta(days=1)
            self.days.append(nxt)
        return self.days[index]

    def index(self, d: date) -> int:
        """Business days from the start up to (not including) date d."""
        i = 0
        while self.date(i) < d:
            i += 1
        return i


@dataclass(frozen=True)
class ScheduledTicket:
    ticket: Ticket
    epic: Epic
    early_start: int   # business-day index
    early_finish: int  # exclusive
    slack: int         # business days it can slip without delaying the end of the project
    start: date
    finish: date       # last working day of the ticket

    @property
    def critical(self) -> bool:
        return self.slack == 0


@dataclass(frozen=True)
class Schedule:
    items: list[ScheduledTicket]
    start: date
    end: date
    go_live: date
    go_live_ticket: str
    contract_go_live: date | None
    path_to_go_live: list[ScheduledTicket]   # the chain of tickets that sets the go-live date

    @property
    def days_vs_contract(self) -> int | None:
        """Business days of buffer before the contract go-live (negative means late)."""
        if not self.contract_go_live:
            return None
        cal = self._calendar
        return cal.index(self.contract_go_live) - cal.index(self.go_live)

    @property
    def feasible(self) -> bool | None:
        days = self.days_vs_contract
        return None if days is None else days >= 0

    _calendar: WorkCalendar | None = field(default=None, repr=False, compare=False)  # set by schedule_plan


def schedule_plan(
    plan: ProjectPlan,
    start: date,
    holidays: frozenset[date] = frozenset(),
    contract_go_live: date | None = None,
    go_live_phase: str = "Launch",
) -> Schedule:
    epic_of = {t.id: e for e in plan.epics for t in e.tickets}
    tickets = {t.id: t for e in plan.epics for t in e.tickets}
    deps = {tid: [d for d in t.depends_on if d in tickets and d != tid] for tid, t in tickets.items()}
    order = list(TopologicalSorter(deps).static_order())  # raises CycleError on a loop

    early_start, early_finish = {}, {}
    for tid in order:
        early_start[tid] = max((early_finish[d] for d in deps[tid]), default=0)
        early_finish[tid] = early_start[tid] + max(1, tickets[tid].duration_days)

    project_end = max(early_finish.values())
    successors: dict[str, list[str]] = {tid: [] for tid in tickets}
    for tid, ds in deps.items():
        for d in ds:
            successors[d].append(tid)
    late_finish = {}
    for tid in reversed(order):
        late_finish[tid] = min((late_finish[s] - max(1, tickets[s].duration_days) for s in successors[tid]), default=project_end)

    cal = WorkCalendar(start, holidays)
    items = {
        tid: ScheduledTicket(
            ticket=tickets[tid], epic=epic_of[tid],
            early_start=early_start[tid], early_finish=early_finish[tid],
            slack=late_finish[tid] - early_finish[tid],
            start=cal.date(early_start[tid]), finish=cal.date(early_finish[tid] - 1),
        )
        for tid in order
    }

    launch = [i for i in items.values() if i.epic.phase == go_live_phase]
    candidates = launch or [i for i in items.values() if i.epic.phase != "Hypercare"] or list(items.values())
    go_live_item = max(candidates, key=lambda i: (i.early_finish, i.ticket.id))

    # Walk back from go-live through the predecessor that finishes last at each step.
    path = [go_live_item]
    while deps[path[-1].ticket.id]:
        driver = max((items[d] for d in deps[path[-1].ticket.id]), key=lambda i: i.early_finish)
        path.append(driver)
    path.reverse()

    ordered = sorted(items.values(), key=lambda i: (i.early_start, i.ticket.id))
    schedule = Schedule(
        items=ordered, start=cal.start, end=cal.date(project_end - 1),
        go_live=go_live_item.finish, go_live_ticket=go_live_item.ticket.id,
        contract_go_live=contract_go_live, path_to_go_live=path,
    )
    object.__setattr__(schedule, "_calendar", cal)
    return schedule
