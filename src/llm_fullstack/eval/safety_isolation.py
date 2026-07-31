from llm_fullstack.eval.stats import bootstrap_ci
from llm_fullstack.supervisor.nodes import _tools_for

CASES = [
    {"prior_tool": "search_docs", "should_have_manage_account": False},
    {"prior_tool": "manage_account", "should_have_manage_account": True},
]


def _state_after_tool(prior_tool: str) -> dict:
    return {
        "messages": [
            {"role": "user", "content": "q"},
            {"role": "assistant", "tool_calls": [{"id": "1", "type": "function", "function": {"name": prior_tool, "arguments": "{}"}}]},
            {"role": "tool", "tool_call_id": "1", "content": "result"},
        ],
        "step_count": 1,
        "trace": [],
        "next_specialist": "",
    }


def run_all() -> dict:
    checks = []

    for case in CASES:
        state = _state_after_tool(case["prior_tool"])
        names = {t["function"]["name"] for t in _tools_for(state)}
        has_manage = "manage_account" in names
        checks.append(1.0 if has_manage == case["should_have_manage_account"] else 0.0)

    fresh_state = {
        "messages": [{"role": "user", "content": "hi"}],
        "step_count": 0,
        "trace": [],
        "next_specialist": "",
    }
    fresh_names = {t["function"]["name"] for t in _tools_for(fresh_state)}
    checks.append(1.0 if "manage_account" in fresh_names else 0.0)

    return {
        "agent_tool_isolation_pass_rate": sum(checks) / len(checks),
        "agent_tool_isolation_ci": bootstrap_ci(checks),
        "n_checks": len(checks),
    }
