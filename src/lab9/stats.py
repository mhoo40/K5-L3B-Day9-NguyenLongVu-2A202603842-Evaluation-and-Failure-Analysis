"""Statistics students implement (M2 judge calibration, M4 paired bootstrap).

Rules: a judge is a classifier -- measure it like one. A higher mean is not
"better" until the paired CI of the difference excludes 0.
Reference values to self-check are in tests/test_lab9_stats.py.
"""

from __future__ import annotations

from collections.abc import Sequence

POS = "FAIL"   # the judge's job is to FIND failures, so FAIL is the positive class


def confusion(human: Sequence[str], judge: Sequence[str]) -> dict[str, int]:
    """tp/fp/fn/tn with FAIL as positive."""
    # TODO M2
    tp = sum(1 for h, j in zip(human, judge) if h == POS and j == POS)
    fp = sum(1 for h, j in zip(human, judge) if h != POS and j == POS)
    fn = sum(1 for h, j in zip(human, judge) if h == POS and j != POS)
    tn = sum(1 for h, j in zip(human, judge) if h != POS and j != POS)
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn}


def precision_recall(human: Sequence[str], judge: Sequence[str]) -> tuple[float, float]:
    # TODO M2: precision = tp/(tp+fp), recall = tp/(tp+fn); return 0.0 when the denominator is 0
    conf = confusion(human, judge)
    tp = conf["tp"]
    fp = conf["fp"]
    fn = conf["fn"]
    tn = conf["tn"]
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    return precision, recall


def cohen_kappa(human: Sequence[str], judge: Sequence[str]) -> float:
    """kappa = (p_o - p_e) / (1 - p_e). Raise ValueError when undefined (p_e == 1):
    a constant judge has no signal and must FAIL calibration, not pass on a technicality."""
    # TODO M2
    p_o = sum(1 for h, j in zip(human, judge) if h == j) / len(human)
    p_e = ((sum(1 for h in human if h == POS) / len(human)) * (sum(1 for j in judge if j == POS) / len(judge))) + \
          ((sum(1 for h in human if h != POS) / len(human)) * (sum(1 for j in judge if j != POS) / len(judge)))
    if p_e == 1:
        raise ValueError("Cohen's kappa is undefined when p_e == 1")
    kappa = (p_o - p_e) / (1 - p_e)
    return kappa


def rogan_gladen(observed_rate: float, sensitivity: float, specificity: float) -> float:
    """Correct an observed failure rate for judge error; clip to [0, 1]."""
    # TODO M2: (p_obs + spec - 1) / (sens + spec - 1)
    denom = sensitivity + specificity - 1.0
    if denom <= 0:
        raise ValueError("sensitivity + specificity must be > 1")
    theta = (observed_rate + specificity - 1.0) / denom
    return max(0.0, min(1.0, theta))


def paired_bootstrap(a: Sequence[float], b: Sequence[float], *, n_resamples: int = 1000,
                     rng: int = 2027, confidence: float = 0.95) -> tuple[float, float, float]:
    """a[i], b[i] = per-item mean over seeds, SAME items, SAME order.
    Return (mean(a)-mean(b), lo, hi) with scipy.stats.bootstrap(paired=True, method="percentile",
    rng=numpy.random.default_rng(rng)). If a == b everywhere return (0.0, 0.0, 0.0)."""
    # TODO M4
    import numpy as np
    import scipy.stats as stats
    a_arr = np.asarray(a, dtype=float)
    b_arr = np.asarray(b, dtype=float)

    if np.array_equal(a_arr, b_arr):
        return (0.0, 0.0, 0.0)

    diff = float(np.mean(a_arr) - np.mean(b_arr))

    res = stats.bootstrap(
        data=(a_arr, b_arr),
        statistic=lambda x, y, axis=-1: np.mean(x, axis=axis) - np.mean(y, axis=axis),
        paired=True,
        method="percentile",
        n_resamples=n_resamples,
        confidence_level=confidence,
        rng=np.random.default_rng(rng),
    )
    return (diff, float(res.confidence_interval.low), float(res.confidence_interval.high))
    


def pass_at_k(n: int, c: int, k: int) -> float:
    """Probability that AT LEAST ONE of k trials drawn from n (c of them passing) passes.
    Unbiased estimator (Chen et al. 2021): 1 - C(n-c, k) / C(n, k). Raise ValueError if k > n."""
    # TODO M6
    if k > n:
        raise ValueError("k cannot be greater than n")
    
    from math import comb
    return 1 - comb(n - c, k) / comb(n, k)


def pass_hat_k(n: int, c: int, k: int) -> float:
    """pass^k (tau-bench, Yao et al. 2024): probability that ALL k trials drawn from n pass.
    Unbiased estimator: C(c, k) / C(n, k). Raise ValueError if k > n.
    pass^k <= pass@1 <= pass@k; a reliable agent keeps pass^k close to pass@1."""
    # TODO M6
    if k > n:
            raise ValueError("k cannot be greater than n")
    
    from math import comb
    return comb(c, k) / comb(n, k)