import random


def bootstrap_ci(values: list[float], n_resamples: int = 1000, confidence: float = 0.95, seed: int = 0) -> tuple[float, float]:
    rng = random.Random(seed)
    resamples = []

    for _ in range(n_resamples):
        sample = [rng.choice(values) for _ in range(len(values))]
        sample_mean = sum(sample) / len(sample)
        resamples.append(sample_mean)
    
    resamples_sorted = sorted(resamples)
    alpha = (1-confidence)/2

    return resamples_sorted[int(alpha * n_resamples)], resamples_sorted[int((1 - alpha) * n_resamples) - 1]
