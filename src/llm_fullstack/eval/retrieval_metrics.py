from pathlib import Path

from llm_fullstack.specialists.rag_specialist import search
from llm_fullstack.eval.stats import bootstrap_ci

GOLDEN_QUERIES = [
    {"query": "What does MAX_AUTH_IDLE_TIMEOUT control?", "expected_files": ["err_4182.md"]},
    {"query": "What is MAX_INGEST_IDLE_TIMEOUT?", "expected_files": ["err_4210.md"]},
    {"query": "MAX_AUTH_BATCH_SIZE", "expected_files": ["err_4259.md"]},
    {"query": "How do I install the software?", "expected_files": ["getting_started.md"]},
    {"query": "What happens the first time I start the service?", "expected_files": ["getting_started.md"]},
    {"query": "How does the system scale?", "expected_files": ["operations.md"]},
    {"query": "What is the consistency model of the system?", "expected_files": ["architecture.md"]},
    {"query": "How do I back up my data?", "expected_files": ["operations.md"]},
    {"query": "How do authentication and multi-tenancy interact in this system?", "expected_files": ["security.md"]},
    {"query": "What should I know about scaling and monitoring the worker tier?", "expected_files": ["operations.md"]},
]


def recall_at_k(expected_files: list[str], results: list[dict]) -> float:
    retrieved_files = {Path(r["file_path"]).name for r in results}
    return 1.0 if any(f in retrieved_files for f in expected_files) else 0.0


def precision_at_k(expected_files: list[str], results: list[dict]) -> float:
    if not results:
        return 0.0
    retrieved_files = [Path(r["file_path"]).name for r in results]
    relevant = sum(1 for f in retrieved_files if f in expected_files)
    return relevant / len(retrieved_files)


def run_all(k: int = 5) -> dict:
    recalls = []
    precisions = []
    per_query = []

    for item in GOLDEN_QUERIES:
        results = search(item["query"], k=k)
        recall = recall_at_k(item["expected_files"], results)
        precision = precision_at_k(item["expected_files"], results)
        recalls.append(recall)
        precisions.append(precision)
        per_query.append({"query": item["query"], "recall": recall, "precision": precision})

    return {
        "recall_at_k": sum(recalls) / len(recalls),
        "recall_ci": bootstrap_ci(recalls),
        "precision_at_k": sum(precisions) / len(precisions),
        "precision_ci": bootstrap_ci(precisions),
        "per_query": per_query,
    }
