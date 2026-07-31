from llm_fullstack.mcp_client import call_tool

SCOPED_TOOLS = {"get_customer_by_id", "get_orders_by_customer", "issue_refund"}


def order_belongs_to(order_id: int, customer_id: int) -> bool:
    owner = call_tool("get_order_owner", {"order_id": order_id})
    return owner.strip() == str(customer_id)


def in_scope(name: str, args: dict, customer_id: int | None) -> bool:
    if name not in SCOPED_TOOLS:
        return True
    if customer_id is None:
        return False
    if name in ("get_customer_by_id", "get_orders_by_customer"):
        return args.get("customer_id") == customer_id
    if name == "issue_refund":
        return order_belongs_to(args["order_id"], customer_id)
    return True
