REFUND_SUCCESS_MARKER = "refunded."


def refund_succeeded(tool_result: str) -> bool:
    return tool_result.strip().endswith(REFUND_SUCCESS_MARKER)


def build_refund_reply(tool_result: str) -> str:
    if refund_succeeded(tool_result):
        return f"Refund confirmed. {tool_result}"
    return f"Refund not issued. {tool_result}"


def enforce_reply_consistency(result: dict) -> dict:
    for entry in reversed(result.get("trace", [])):
        if entry.get("specialist") == "actions" and "refund_result" in entry:
            result["messages"][-1]["content"] = build_refund_reply(entry["refund_result"])
            break
    return result
