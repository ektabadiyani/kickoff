import json
from types import SimpleNamespace

import pytest

from kickoff.llm import Claude, LLMError
from kickoff.models import ProjectPlan
from kickoff.plan import build_plan, check_plan, find_cycle, load_playbook


@pytest.fixture
def playbook():
    return load_playbook()


def test_default_playbook_loads(playbook):
    assert playbook.phase_names[0] == "Initiate" and playbook.phase_names[-1] == "Hypercare"
    assert playbook.role_cost["integration_engineer"] > 0


def test_clean_plan_has_no_errors(plan, extract, playbook):
    assert check_plan(plan, extract, playbook).errors == []


def test_check_catches_coverage_gaps_and_bad_dependencies(plan, extract, playbook):
    plan.epics[1].tickets[2].requirement_ids = []          # R02 loses its only ticket
    plan.epics[2].tickets[0].depends_on.append("T999")     # dependency on a ticket that doesn't exist
    plan.epics[0].phase = "Kickoff"                        # not a playbook phase
    messages = [i.message for i in check_plan(plan, extract, playbook).errors]
    assert any("R02" in m and "no ticket" in m for m in messages)
    assert any("T999" in m for m in messages)
    assert any("unknown phase" in m for m in messages)


def test_find_cycle():
    assert find_cycle({"a": ["b"], "b": ["c"], "c": ["a"]}) == ["a", "b", "c", "a"]
    assert find_cycle({"a": ["b"], "b": []}) is None


class FakeClaude(Claude):
    def __init__(self, plans):
        self.plans = list(plans)
        self.prompts = []

    def structured(self, system, prompt, schema, max_tokens=64000):
        self.prompts.append(prompt)
        return self.plans.pop(0)


def test_build_plan_sends_errors_back_for_one_repair(plan, extract, playbook):
    broken = plan.model_copy(deep=True)
    broken.epics[1].tickets[2].requirement_ids = []
    claude = FakeClaude([broken, plan])
    result, check, repairs = build_plan(extract, playbook, claude)
    assert repairs == 1 and check.errors == [] and result is plan
    assert "R02" in claude.prompts[1] and "previous_draft" in claude.prompts[1]


def test_build_plan_stops_after_max_repairs(plan, extract, playbook):
    broken = plan.model_copy(deep=True)
    broken.epics[1].tickets[2].requirement_ids = []
    _, check, repairs = build_plan(extract, playbook, FakeClaude([broken, broken]), max_repairs=1)
    assert repairs == 1 and check.errors


# --- the Claude wrapper, with a fake SDK client

class FakeStream:
    def __init__(self, message):
        self.message = message

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def get_final_message(self):
        return self.message


def fake_client(text, stop_reason="end_turn"):
    message = SimpleNamespace(stop_reason=stop_reason, content=[SimpleNamespace(type="text", text=text)])
    calls = []

    def stream(**kwargs):
        calls.append(kwargs)
        return FakeStream(message)

    return SimpleNamespace(beta=SimpleNamespace(messages=SimpleNamespace(stream=stream))), calls


def test_structured_validates_and_sends_schema(plan):
    client, calls = fake_client(plan.model_dump_json())
    result = Claude(client=client).structured("sys", "prompt", ProjectPlan)
    assert result == plan
    call = calls[0]
    assert call["model"] == "claude-opus-5-5"
    assert call["output_config"]["effort"] == "high"
    assert call["output_config"]["format"]["schema"]["additionalProperties"] is False
    assert call["fallbacks"] == "default"


@pytest.mark.parametrize("text,stop,expected", [
    ("", "refusal", "declined"),
    ("{}", "max_tokens", "output limit"),
    (json.dumps({"epics": "nope"}), "end_turn", "didn't match"),
])
def test_structured_raises_clear_errors(text, stop, expected):
    client, _ = fake_client(text, stop)
    with pytest.raises(LLMError, match=expected):
        Claude(client=client).structured("sys", "prompt", ProjectPlan)
