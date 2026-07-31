from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from llm_fullstack.eval.tasks import TASKS
from llm_fullstack.eval.stats import bootstrap_ci
from llm_fullstack.supervisor.graph import build_graph
from llm_fullstack.guardrails.consistency import enforce_reply_consistency


def classify_failure(task: dict, trace: list[dict]) -> str:
    actions_entries = [t for t in trace if t.get("specialist") == "actions"]
    rag_entries = [t for t in trace if t.get("specialist") == "rag"]

    if task["type"] == "actions" and task.get("expects_interrupt"):
        refund_result = actions_entries[-1].get("refund_result") if actions_entries else None
        if refund_result is None:
            return "system"
        succeeded = refund_result.strip().endswith("refunded.")
        expected_success = task.get("resume") == "approve"
        system_ok = succeeded == expected_success
        return "wording" if system_ok else "system"

    if task["type"] == "actions":
        entry = actions_entries[-1] if actions_entries else None
        system_ok = bool(entry) and entry.get("tool_calls") and not entry.get("denied_out_of_scope")
        return "wording" if system_ok else "system"

    if task["type"] == "rag":
        system_ok = any(e.get("n_results", 0) > 0 for e in rag_entries)
        return "wording" if system_ok else "system"

    return "system"


def run_task(task: dict) -> dict:
    graph = build_graph(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": task["id"]}}
    initial_state = {
        "messages": [{"role": "user", "content": task["query"]}],
        "step_count": 0,
        "trace": [],
        "next_specialist": "",
        "customer_id": task.get("customer_id"),
    }
    result = graph.invoke(initial_state, config)

    if "__interrupt__" in result:
        command = Command(resume=task.get("resume","approve"))
        result = graph.invoke(command, config)

    result = enforce_reply_consistency(result)
    content = result["messages"][-1]["content"].lower()
    passed = any(kw.lower() in content for kw in task["expect_any"])

    out = {"id": task["id"], "passed": passed, "content": content}
    if not passed:
        out["failure_reason"] = classify_failure(task, result["trace"])
    return out



def run_all() -> dict:
    result = [run_task(t) for t in TASKS]
    scores = [1.0 if r["passed"] else 0.0 for r in result]
    if len(scores) == 0:
        return{"error": "No tasks to evaluate"}
    ci = bootstrap_ci(scores)

    failures = [r for r in result if not r["passed"]]
    system_faults = sum(1 for r in failures if r["failure_reason"] == "system")
    wording_faults = sum(1 for r in failures if r["failure_reason"] == "wording")

    return {
        "pass_rate": sum(scores)/len(scores),
        "ci": ci,
        "results": result,
        "system_faults": system_faults,
        "wording_faults": wording_faults,
    }