import json
from pathlib import Path

RESULTS_PATH = Path(__file__).parent / "results.json"
BASELINE_PATH = Path(__file__).parent / "baseline.json"

HARD_GATE_METRICS = ["recall_at_k", "precision_at_k", "agent_tool_isolation_pass_rate", "block_rate", "tenant_block_rate"]


def save_results(results: dict, path: Path = RESULTS_PATH) -> None:
    with open(path, "w") as f:
        json.dump(results, f, indent=2)


def load_results(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def check_regression(baseline: dict, current: dict) -> list[str]:
    regressions = []

    for metric in HARD_GATE_METRICS:
        if metric in baseline and metric in current and current[metric] < baseline[metric]:
            regressions.append(f"{metric}: {baseline[metric]:.3f} -> {current[metric]:.3f}")

    baseline_pass_rate = baseline.get("pass_rate")
    current_pass_rate = current.get("pass_rate")
    current_ci = current.get("ci")
    if baseline_pass_rate is not None and current_ci is not None:
        if current_pass_rate < baseline_pass_rate and current_ci[1] < baseline_pass_rate:
            regressions.append(f"pass_rate: {baseline_pass_rate:.3f} -> {current_pass_rate:.3f} (outside CI)")

    return regressions


def run_regression(baseline_path: Path = BASELINE_PATH, current_path: Path = RESULTS_PATH) -> list[str]:
    baseline = load_results(baseline_path)
    current = load_results(current_path)
    regressions = check_regression(baseline, current)

    if regressions:
        print("=== REGRESSIONS DETECTED ===")
        for r in regressions:
            print(r)
    else:
        print("No regressions detected.")

    return regressions
