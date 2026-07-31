from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from llm_fullstack.supervisor.graph import build_graph
from llm_fullstack.tracing import new_run_id, write_trace
from llm_fullstack.guardrails.consistency import enforce_reply_consistency


def main():
    run_id = new_run_id()
    graph = build_graph(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": run_id}}
    initial_state = {
        "messages": [{"role": "user", "content": "What does ERR_4231 error indicate?"}],
        "step_count": 0,
        "trace": [],
        "next_specialist": "",
        "customer_id": 1,
    }

    result = graph.invoke(initial_state, config)

    if "__interrupt__" in result:
        pending = result["__interrupt__"][0].value
        print(f"Approval needed: {pending}")
        decision = input("approve/reject: ").strip().lower()
        result = graph.invoke(Command(resume=decision), config)

    result = enforce_reply_consistency(result)
    write_trace(run_id, result["trace"])
    print(f'{result["messages"][-1]["content"]} + {run_id}')



if __name__ == "__main__":
    main()
