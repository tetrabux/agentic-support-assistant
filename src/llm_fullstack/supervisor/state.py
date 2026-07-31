from typing import Annotated, TypedDict
import operator

class State(TypedDict):
    messages: Annotated[list[dict], operator.add]
    next_specialist: str
    step_count: int
    trace: Annotated[list[dict], operator.add]
    customer_id: int | None
    
