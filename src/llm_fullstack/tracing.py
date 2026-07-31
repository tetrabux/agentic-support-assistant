import json
import uuid
from pathlib import Path

TRACES_DIR = Path(__file__).resolve().parents[2] / "traces"


def new_run_id() -> str:
    return str(uuid.uuid4().hex[:12])


def write_trace(run_id: str, trace: list[dict]) -> None:
    TRACES_DIR.mkdir(exist_ok=True)
    trace_file = TRACES_DIR / f"{run_id}.jsonl"
    with open(trace_file, "w") as f:
        json.dump(trace, f, indent=2)
    return None
