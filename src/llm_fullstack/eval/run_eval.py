from llm_fullstack.eval import task_success, retrieval_metrics, safety_injection, safety_isolation, safety_tenant_isolation
from llm_fullstack.eval.regression import save_results


def run_all() -> dict:
    task = task_success.run_all()
    retrieval = retrieval_metrics.run_all()
    injection = safety_injection.run_all()
    isolation = safety_isolation.run_all()
    tenant = safety_tenant_isolation.run_all()

    return {
        "pass_rate": task["pass_rate"],
        "ci": task["ci"],
        "task_results": task["results"],
        "system_faults": task["system_faults"],
        "wording_faults": task["wording_faults"],
        "recall_at_k": retrieval["recall_at_k"],
        "recall_ci": retrieval["recall_ci"],
        "precision_at_k": retrieval["precision_at_k"],
        "precision_ci": retrieval["precision_ci"],
        "block_rate": injection["block_rate"],
        "block_rate_ci": injection["block_rate_ci"],
        "agent_tool_isolation_pass_rate": isolation["agent_tool_isolation_pass_rate"],
        "agent_tool_isolation_ci": isolation["agent_tool_isolation_ci"],
        "tenant_block_rate": tenant["tenant_block_rate"],
        "tenant_block_rate_ci": tenant["tenant_block_rate_ci"],
    }


def main():
    results = run_all()
    save_results(results)

    print(f"task success:        {results['pass_rate']:.2f}  CI {results['ci']}  (system faults: {results['system_faults']}, wording faults: {results['wording_faults']})")
    print(f"retrieval recall:    {results['recall_at_k']:.2f}  CI {results['recall_ci']}")
    print(f"retrieval precision: {results['precision_at_k']:.2f}  CI {results['precision_ci']}")
    print(f"injection block:     {results['block_rate']:.2f}  CI {results['block_rate_ci']}")
    print(f"agent tool isolation:{results['agent_tool_isolation_pass_rate']:.2f}  CI {results['agent_tool_isolation_ci']}")
    print(f"tenant isolation:    {results['tenant_block_rate']:.2f}  CI {results['tenant_block_rate_ci']}")


if __name__ == "__main__":
    main()
