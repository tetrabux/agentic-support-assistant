from openai import OpenAI
from langgraph.graph import END
from llm_fullstack.config import settings

client = OpenAI(base_url=settings.model_service_url, api_key=settings.model_api_key)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_docs",
            "description": "Search the product manual and error-code wiki for troubleshooting or policy information.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "manage_account",
            "description": "Handle a customer account action: look up a customer or their orders, or issue a refund for an order.",
            "parameters": {
                "type": "object",
                "properties": {"request": {"type": "string"}},
                "required": ["request"],
            },
        },
    },
]


def _tools_for(state):
    messages = state["messages"]
    if len(messages) >= 2 and messages[-1].get("role") == "tool":
        prior_calls = messages[-2].get("tool_calls") or []
        if prior_calls and prior_calls[0]["function"]["name"] == "search_docs":
            return [TOOLS[0]]
    return TOOLS


def supervisor_node(state):
    resp = client.chat.completions.create(
        model=settings.model_name,
        messages=state["messages"],
        tools=_tools_for(state),
    )
    result = resp.choices[0].message.model_dump(exclude_none=True)
    tool_calls = result.get("tool_calls") or []
    decision = (
        f"called {tool_calls[0]['function']['name']}"
        if tool_calls
        else "answered directly"
    )
    return {
        "messages": [result],
        "step_count": state["step_count"] + 1,
        "trace": [{"specialist": "supervisor", "decision": decision}],
    }


def route_supervisor(state) -> str:
    message = state["messages"][-1]
    if state["step_count"] >= settings.agent_step_cap:
        return END
    elif "tool_calls" in message and message["tool_calls"]:
        return "rag" if message["tool_calls"][0]["function"]["name"] == "search_docs" else "actions"
    else:
        return END
    
