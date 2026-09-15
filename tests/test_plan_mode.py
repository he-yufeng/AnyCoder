"""Plan mode: the approval gate for mutating tool calls."""

import sys

from anycoder.agent import _MUTATING_TOOLS, Agent
from anycoder.config import Config


def _agent(plan: bool) -> Agent:
    return Agent(Config(plan_mode=plan))


def _call(name: str, **kwargs) -> dict:
    return {"id": f"call_{name}", "name": name, "arguments": kwargs}


def test_gate_is_inert_when_plan_mode_off():
    agent = _agent(plan=False)
    calls = [_call("edit_file", file_path="a.py", old_text="x", new_text="y")]
    assert agent._gate_tool_calls(calls) == calls


def test_read_only_tools_pass_ungated_in_plan_mode():
    agent = _agent(plan=True)
    calls = [_call("read_file", file_path="a.py"), _call("grep", pattern="foo")]
    assert agent._gate_tool_calls(calls) == calls


def test_non_tty_auto_approves_with_a_notice():
    # pytest's stdin is not a tty, so this is the default automation path
    agent = _agent(plan=True)
    calls = [_call("write_file", file_path="a.py", content="x")]
    assert agent._gate_tool_calls(calls) == calls


def test_declined_mutating_calls_get_a_synthetic_result(monkeypatch):
    agent = _agent(plan=True)
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr("anycoder.agent.Prompt.ask", lambda *a, **k: "n")

    calls = [
        _call("read_file", file_path="a.py"),
        _call("edit_file", file_path="a.py", old_text="x", new_text="y"),
        _call("bash", command="rm -rf build/"),
    ]
    approved = agent._gate_tool_calls(calls)

    # read-only work still runs; every mutating call is answered in place
    assert [c["name"] for c in approved] == ["read_file"]
    tool_results = [m for m in agent.ctx.messages if m.get("role") == "tool"]
    assert len(tool_results) == 2
    assert {r["tool_call_id"] for r in tool_results} == {"call_edit_file", "call_bash"}
    assert all("declined by user" in r["content"] for r in tool_results)


def test_approved_calls_all_run(monkeypatch):
    agent = _agent(plan=True)
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr("anycoder.agent.Prompt.ask", lambda *a, **k: "y")

    calls = [_call("edit_file", file_path="a.py", old_text="x", new_text="y")]
    assert agent._gate_tool_calls(calls) == calls
    assert not [m for m in agent.ctx.messages if m.get("role") == "tool"]


def test_mutating_set_matches_the_tool_registry():
    from anycoder.tools import TOOL_MAP

    assert _MUTATING_TOOLS <= set(TOOL_MAP)
