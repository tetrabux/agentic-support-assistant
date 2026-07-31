import uuid

from fastapi import FastAPI, Depends
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from pydantic import BaseModel

from llm_fullstack.api.auth import get_identity
from llm_fullstack.supervisor.graph import build_graph
from llm_fullstack.guardrails.consistency import enforce_reply_consistency

app = FastAPI()
checkpointer = InMemorySaver()
graph = build_graph(checkpointer=checkpointer)


class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None


class ResumeRequest(BaseModel):
    decision: str


@app.post("/chat")
def chat(req: ChatRequest, identity: dict = Depends(get_identity)):
    thread_id = req.thread_id or uuid.uuid4().hex[:12]
    config = {
        "configurable": {"thread_id": thread_id},
    }

    initial_state = {
        "messages": [{"role": "user", "content": req.message}],
        "step_count": 0,
        "trace": [],
        "next_specialist": "",
        "customer_id": identity.get("customer_id"),
    }

    result = graph.invoke(initial_state, config)
    
    if "__interrupt__" in result:
        return {"status": "pending_approval", "thread_id": thread_id, "pending": result["__interrupt__"][0].value}
    else:
        result = enforce_reply_consistency(result)
        return {"status": "done", "thread_id": thread_id, "answer": result["messages"][-1]["content"]}



@app.post("/chat/{thread_id}/resume")
def resume(thread_id: str, req: ResumeRequest, identity: dict = Depends(get_identity)):
    config = {"configurable": {"thread_id": thread_id}}
    result = graph.invoke(Command(resume=req.decision), config)
    result = enforce_reply_consistency(result)

    return {"status": "done", "thread_id": thread_id, "answer": result["messages"][-1]["content"]}
