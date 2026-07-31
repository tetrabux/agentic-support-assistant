from langgraph.types import interrupt

GATED_TOOLS = {"issue_refund"}


def requires_approval(tool_name: str) -> bool:
    return tool_name in GATED_TOOLS


def request_approval(tool_name: str, args: dict) -> bool:
    decision = interrupt({"tool": tool_name, "args": args})
    return decision == "approve"
