import json

import httpx

from llm_fullstack.config import settings


def search(query: str, k: int = 5, source: str | None = None) -> list[dict]:
    try:
        resp = httpx.post(f"{settings.rag_service_url}/search", json={
            "query": query,
            "mode": "hybrid_rerank",
            "k": k,
            "source": source,
        })
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"RAG service error: {e}")
        return []


def rag_specialist_node(state):
    tool_call = state["messages"][-1]["tool_calls"][0]
    args = json.loads(tool_call["function"]["arguments"])
    query = args["query"]

    results = search(query)

    context = "\n\n".join(r["text"] for r in results)
    content = f"[retrieved, untrusted]\n{context}" if results else "No relevant documents found."

    return {
        "messages": [{
            "role": "tool",
            "tool_call_id": tool_call["id"],
            "content": content,
        }],
        "trace": [{
            "specialist": "rag",
            "query": query,
            "n_results": len(results),
            "sources": [r["source"] for r in results],
        }],
    }

