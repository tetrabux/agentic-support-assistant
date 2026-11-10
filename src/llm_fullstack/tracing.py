import json
import logging
import time
import uuid
from pathlib import Path

TRACES_DIR = Path(__file__).resolve().parents[2] / "traces"

logger = logging.getLogger("llm_fullstack")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def new_run_id() -> str:
    return str(uuid.uuid4().hex[:12])


def timed_completion(client, **kwargs):
    start = time.perf_counter()
    resp = client.chat.completions.create(**kwargs)
    latency_ms = round((time.perf_counter() - start) * 1000)
    usage = resp.usage
    return resp, {
        "latency_ms": latency_ms,
        "prompt_tokens": usage.prompt_tokens if usage else None,
        "completion_tokens": usage.completion_tokens if usage else None,
    }


def write_trace(run_id: str, trace: list[dict]) -> None:
    TRACES_DIR.mkdir(exist_ok=True)
    trace_file = TRACES_DIR / f"{run_id}.jsonl"
    with open(trace_file, "a") as f:
        for entry in trace:
            f.write(json.dumps({"trace_id": run_id, **entry}) + "\n")


def log_turn(run_id: str, trace: list[dict], status: str, thread_id: str | None = None, customer_id: int | None = None) -> None:
    model_calls = [c for e in trace for c in e.get("model_calls", [])]
    logger.info(json.dumps({
        "event": "turn",
        "trace_id": run_id,
        "thread_id": thread_id,
        "status": status,
        "customer_id": customer_id,
        "steps": [e.get("specialist") for e in trace],
        "tool_calls": [c["tool"] for e in trace for c in e.get("tool_calls", [])],
        "model_calls": len(model_calls),
        "latency_ms": sum(c["latency_ms"] for c in model_calls),
        "prompt_tokens": sum(c["prompt_tokens"] or 0 for c in model_calls),
        "completion_tokens": sum(c["completion_tokens"] or 0 for c in model_calls),
        "denied_out_of_scope": sum(len(e.get("denied_out_of_scope", [])) for e in trace),
        "injection_flags": sum(1 for e in trace if e.get("injection_suspected")),
    }))
