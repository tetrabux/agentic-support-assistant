import json

from openai import OpenAI

from llm_fullstack.config import settings
from llm_fullstack.mcp_client import call_tool
from llm_fullstack.guardrails.hitl import requires_approval, request_approval
from llm_fullstack.guardrails.consistency import build_refund_reply
from llm_fullstack.guardrails.tenant_scope import in_scope

client = OpenAI(base_url=settings.model_service_url, api_key=settings.model_api_key)

ACTIONS_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_customer_by_id",
            "description": "Get the information of a specific customer.",
            "parameters": {
                "type": "object",
                "properties": {"customer_id": {"type": "integer"}},
                "required": ["customer_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_orders_by_customer",
            "description": "Get the orders placed by a specific customer.",
            "parameters": {
                "type": "object",
                "properties": {"customer_id": {"type": "integer"}},
                "required": ["customer_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "issue_refund",
            "description": "Issue the refund to the customer of a specific order.",
            "parameters": {
                "type": "object",
                "properties": {"order_id": {"type": "integer"}},
                "required": ["order_id"],
            },
        },
    },
]

MAX_ACTION_STEPS = 5


def actions_specialist_node(state):
    original_tool_call = state["messages"][-1]["tool_calls"][0]
    request = json.loads(original_tool_call["function"]["arguments"])["request"]
    customer_id = state.get("customer_id")

    messages = [{"role": "user", "content": request}]
    final_content = "Could not complete the request."
    tool_calls_made = []
    last_refund_result = None
    denied_out_of_scope = []

    for step in range(MAX_ACTION_STEPS):
        resp = client.chat.completions.create(
            model=settings.model_name,
            messages=messages,
            tools=ACTIONS_TOOLS,
        )
        message = resp.choices[0].message

        if not message.tool_calls:
            final_content = message.content
            break

            

        messages.append(message.model_dump(exclude_none=True))

        for tool_call in message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            if not in_scope(name, args, customer_id):
                denial = f"{name} denied: outside the authenticated customer's scope."
                if name == "issue_refund":
                    last_refund_result = denial
                denied_out_of_scope.append({"tool": name, "args": args})
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": denial,
                })
                continue

            if requires_approval(name):
                if not request_approval(name, args):
                    denial = "Approval denied."
                    if name == "issue_refund":
                        last_refund_result = denial
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": denial,
                    })
                    continue


            result = call_tool(name, args)
            tool_calls_made.append({"tool": name, "args": args})

            if name == "issue_refund":
                last_refund_result = result

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })

        final_content = message.content or final_content

    if last_refund_result is not None:
        final_content = build_refund_reply(last_refund_result)

    trace_entry = {"specialist": "actions", "request": request, "tool_calls": tool_calls_made}
    if last_refund_result is not None:
        trace_entry["refund_result"] = last_refund_result
    if denied_out_of_scope:
        trace_entry["denied_out_of_scope"] = denied_out_of_scope

    return {
        "messages": [{
            "role": "tool",
            "tool_call_id": original_tool_call["id"],
            "content": final_content,
        }],
        "trace": [trace_entry],
    }

