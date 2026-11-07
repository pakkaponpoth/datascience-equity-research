"""
AHP factor weights for the SETscout stock ranking.

Reads the experts' pairwise judgments (data/judgments.csv), builds one
pairwise comparison matrix per expert and investor profile, and computes:
  - factor weights (principal eigenvector, by power iteration)
  - lambda max, consistency index (CI) and consistency ratio (CR)
  - a group matrix (element-wise geometric mean across experts)

Results are printed and saved to results/factor_weights.csv.
This reproduces the numbers in excel/AHP_Factor_Weights_SET.xlsx.

Usage:
    pip install -r requirements.txt
    python ahp.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

FACTORS = ["Growth", "Momentum", "Quality", "Health"]
PROFILES = ["Conservative", "Balanced", "Aggressive"]
RANDOM_INDEX = {3: 0.58, 4: 0.90, 5: 1.12}  # Saaty's random consistency index
CR_THRESHOLD = 0.10

BASE = Path(__file__).parent


def build_matrix(judgments: pd.DataFrame) -> np.ndarray:
    """Turn six pairwise judgments into a reciprocal 4x4 comparison matrix."""
    idx = {f: i for i, f in enumerate(FACTORS)}
    a = np.ones((len(FACTORS), len(FACTORS)))
    for _, row in judgments.iterrows():
        i, j = idx[row["first_factor"]], idx[row["second_factor"]]
        v = float(row["value_first_over_second"])
        a[i, j] = v
        a[j, i] = 1.0 / v
    return a


def eigen_weights(a: np.ndarray, tol: float = 1e-12, max_iter: int = 1000) -> np.ndarray:
    """Principal eigenvector by power iteration, normalised to sum to 1."""
    w = np.full(a.shape[0], 1.0 / a.shape[0])
    for _ in range(max_iter):
        w_new = a @ w
        w_new /= w_new.sum()
        if np.max(np.abs(w_new - w)) < tol:
            return w_new
        w = w_new
    return w


def consistency(a: np.ndarray, w: np.ndarray) -> tuple[float, float, float]:
    """Return (lambda_max, CI, CR) for a comparison matrix and its weights."""
    n = a.shape[0]
    lambda_max = float(np.mean((a @ w) / w))
    ci = (lambda_max - n) / (n - 1)
    cr = ci / RANDOM_INDEX[n]
    return lambda_max, ci, cr


def summarise(source: str, profile: str, a: np.ndarray) -> dict:
    w = eigen_weights(a)
    lambda_max, ci, cr = consistency(a, w)
    return {
        "source": source,
        "profile": profile,
        **{f: round(float(x), 4) for f, x in zip(FACTORS, w)},
        "lambda_max": round(lambda_max, 4),
        "CI": round(ci, 4),
        "CR": round(cr, 4),
        "consistent": cr <= CR_THRESHOLD,
    }


def main() -> None:
    df = pd.read_csv(BASE / "data" / "judgments.csv")
    experts = list(dict.fromkeys(df["expert"]))
    rows = []

    for expert in experts:
        for profile in PROFILES:
            sub = df[(df["expert"] == expert) & (df["profile"] == profile)]
            rows.append(summarise(expert, profile, build_matrix(sub)))

    # Group judgment: element-wise geometric mean of the experts' matrices
    for profile in PROFILES:
        mats = [
            build_matrix(df[(df["expert"] == e) & (df["profile"] == profile)])
            for e in experts
        ]
        group = np.exp(np.mean([np.log(m) for m in mats], axis=0))
        rows.append(summarise("Group geometric mean", profile, group))

    out = pd.DataFrame(rows)
    (BASE / "results").mkdir(exist_ok=True)
    out.to_csv(BASE / "results" / "factor_weights.csv", index=False)

    pd.set_option("display.width", 140)
    print(out.to_string(index=False))
    print(f"\nA matrix is acceptably consistent when CR <= {CR_THRESHOLD}.")
    print("Saved to results/factor_weights.csv")


if __name__ == "__main__":
    main()
