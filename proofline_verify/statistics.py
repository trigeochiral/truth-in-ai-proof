"""
Statistical tests for the Proofline evaluation protocol.

- DeLong AUC comparison (DeLong et al. 1988) [verify]
- Bootstrap CI for AUC (Efron 1979) [verify]
- McNemar test for paired binary classifiers
- Expected Calibration Error (Guo et al. 2017) [verify]

Every function has a single docstring paragraph naming the paper it
implements so any auditor can trace the arithmetic back to the source.
"""
from __future__ import annotations
import numpy as np
from scipy import stats

# ── DeLong AUC comparison ─────────────────────────────────────────────────
def delong_auc_test(y_true: np.ndarray,
                    scores_a: np.ndarray,
                    scores_b: np.ndarray) -> dict:
    """
    Compare two ROC curves computed on the same y_true.
    Implements DeLong, DeLong & Clarke-Pearson (1988), 'Comparing the
    areas under two or more correlated receiver operating characteristic
    curves: a nonparametric approach', Biometrics 44(3):837-845.
    Returns {auc_a, auc_b, delta, z_stat, p_value} where p_value is
    two-tailed and null hypothesis is auc_a == auc_b.
    """
    y_true = np.asarray(y_true).astype(int)
    pos = y_true == 1
    neg = ~pos
    n_pos = pos.sum(); n_neg = neg.sum()

    def _auc_and_variance(scores):
        s_pos = scores[pos]; s_neg = scores[neg]
        # midrank via scipy
        from scipy.stats import rankdata
        r_all = rankdata(scores)
        r_pos = r_all[pos]
        auc = (r_pos.sum() - n_pos*(n_pos+1)/2) / (n_pos * n_neg)
        # structural components (Sun & Xu 2014 simplification)
        v01 = np.array([(scores[neg] < s).sum() + 0.5*(scores[neg] == s).sum() for s in s_pos]) / n_neg
        v10 = np.array([(scores[pos] > s).sum() + 0.5*(scores[pos] == s).sum() for s in s_neg]) / n_pos
        s01 = v01.var(ddof=1) / n_pos
        s10 = v10.var(ddof=1) / n_neg
        return auc, s01 + s10, v01, v10

    a_a, var_a, v01_a, v10_a = _auc_and_variance(scores_a)
    a_b, var_b, v01_b, v10_b = _auc_and_variance(scores_b)
    # covariance
    cov = (np.cov(v01_a, v01_b, ddof=1)[0,1] / n_pos +
           np.cov(v10_a, v10_b, ddof=1)[0,1] / n_neg)
    delta = a_a - a_b
    se = np.sqrt(var_a + var_b - 2*cov)
    if se < 1e-12:
        return {"auc_a": float(a_a), "auc_b": float(a_b), "delta": float(delta),
                "z_stat": 0.0, "p_value": 1.0}
    z = delta / se
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    return {"auc_a": float(a_a), "auc_b": float(a_b), "delta": float(delta),
            "z_stat": float(z), "p_value": float(p)}


# ── Bootstrap CI for AUC ──────────────────────────────────────────────────
def bootstrap_auc_ci(y_true: np.ndarray, scores: np.ndarray,
                     n_boot: int = 1000, alpha: float = 0.05,
                     seed: int = 42) -> dict:
    """
    Percentile bootstrap CI for AUC-ROC.
    Efron 1979: 'Bootstrap methods: Another look at the jackknife',
    Annals of Statistics 7(1):1-26. n_boot resamples with replacement
    of the sample indices; the interval is the [alpha/2, 1-alpha/2]
    quantile of the resampled AUCs.
    """
    from sklearn.metrics import roc_auc_score
    rng = np.random.default_rng(seed)
    n = len(y_true)
    aucs = np.zeros(n_boot)
    for b in range(n_boot):
        idx = rng.integers(0, n, size=n)
        if len(np.unique(y_true[idx])) < 2:  # degenerate — resample
            aucs[b] = np.nan; continue
        aucs[b] = roc_auc_score(y_true[idx], scores[idx])
    aucs = aucs[~np.isnan(aucs)]
    lo = float(np.quantile(aucs, alpha/2))
    hi = float(np.quantile(aucs, 1 - alpha/2))
    return {"auc": float(roc_auc_score(y_true, scores)),
            "ci_lo": lo, "ci_hi": hi, "n_boot": len(aucs),
            "alpha": alpha}


# ── McNemar's test for paired binary classifiers ──────────────────────────
def mcnemar_test(y_true: np.ndarray,
                 pred_a: np.ndarray, pred_b: np.ndarray) -> dict:
    """
    McNemar's paired binary test at a fixed operating point.
    Returns discordant counts b, c and the exact/binomial two-tailed p-value.
    """
    y_true = np.asarray(y_true).astype(int)
    a_correct = (pred_a == y_true)
    b_correct = (pred_b == y_true)
    b_only = int((a_correct & ~b_correct).sum())   # A right, B wrong
    c_only = int((~a_correct & b_correct).sum())   # B right, A wrong
    n = b_only + c_only
    if n == 0:
        return {"b_only": b_only, "c_only": c_only, "p_value": 1.0}
    # exact binomial
    p = 2 * stats.binom.cdf(min(b_only, c_only), n, 0.5)
    return {"b_only": b_only, "c_only": c_only, "p_value": float(min(p, 1.0))}


# ── Expected Calibration Error ────────────────────────────────────────────
def expected_calibration_error(y_true: np.ndarray, scores: np.ndarray,
                               n_bins: int = 15) -> dict:
    """
    Guo, Pleiss, Sun, Weinberger 2017, 'On Calibration of Modern Neural Networks', ICML.
    Bins predictions by predicted probability, measures weighted absolute
    gap between mean-confidence and mean-accuracy per bin.
    """
    y_true = np.asarray(y_true).astype(int)
    bins = np.linspace(0, 1, n_bins + 1)
    ece = 0.0; n = len(y_true)
    per_bin = []
    for i in range(n_bins):
        lo, hi = bins[i], bins[i+1]
        m = (scores >= lo) & (scores < hi if i < n_bins - 1 else scores <= hi)
        cnt = int(m.sum())
        if cnt == 0:
            per_bin.append({"bin": [float(lo), float(hi)], "n": 0}); continue
        acc = float(y_true[m].mean())
        conf = float(scores[m].mean())
        ece += (cnt / n) * abs(acc - conf)
        per_bin.append({"bin": [float(lo), float(hi)], "n": cnt,
                        "accuracy": acc, "confidence": conf})
    return {"ece": float(ece), "n_bins": n_bins, "per_bin": per_bin}
