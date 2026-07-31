from langgraph.graph import StateGraph, END

from llm_fullstack.supervisor.state import State
from llm_fullstack.supervisor.nodes import supervisor_node, route_supervisor
from llm_fullstack.specialists.rag_specialist import rag_specialist_node
from llm_fullstack.specialists.actions_specialist import actions_specialist_node


def build_graph(checkpointer=None):
    workflow = StateGraph(State)

    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("rag", rag_specialist_node)
    workflow.add_node("actions", actions_specialist_node)

    workflow.add_edge("rag", "supervisor")
    workflow.add_edge("actions", "supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {"rag": "rag", "actions": "actions", END: END},
    )
    workflow.set_entry_point("supervisor")

    if checkpointer:
        return workflow.compile(checkpointer=checkpointer)
    return workflow.compile()
