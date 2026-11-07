# AHP Factor Weights for SETScout

How much should each factor count in SETScout's stock score, for each type of investor?
This folder answers that with the **Analytic Hierarchy Process (AHP)**, using survey answers
from finance experts, and checks whether those answers are logically consistent before using them.

## Factors

| Factor | Proxy used |
|---|---|
| Growth | Return on equity (ROE) |
| Momentum | 6-month return |
| Quality | Low volatility |
| Health | Maximum drawdown (MDD) |

## Method

1. **Survey.** Each expert compared every pair of factors (6 pairs) on Saaty's 1–9 scale,
   separately for three investor profiles: Conservative, Balanced and Aggressive (18 questions per expert).
2. **Comparison matrix.** Each set of 6 answers becomes a 4×4 reciprocal matrix
   (if Growth is 3× as important as Momentum, Momentum is 1/3 as important as Growth).
3. **Weights.** The factor weights are the matrix's principal eigenvector, found by power iteration
   and normalised to sum to 1.
4. **Consistency check.** λmax → consistency index CI = (λmax − n)/(n − 1) → consistency ratio
   CR = CI / RI (RI = 0.90 for n = 4). Judgments are accepted only if **CR ≤ 0.10**.
5. **Group view.** The experts' matrices are also combined by element-wise geometric mean, for reference.

## Results

| Profile | Growth | Momentum | Quality | Health | CR |
|---|---|---|---|---|---|
| Conservative | 0.118 | 0.055 | 0.262 | 0.565 | 0.043 ✓ |
| Balanced | 0.208 | 0.096 | 0.208 | 0.487 | 0.057 ✓ |
| Aggressive | 0.249 | 0.560 | 0.095 | 0.095 | 0.016 ✓ |

These are the **recommended weights (Expert 1)**. The pattern makes sense: conservative investors
weight downside protection (Health) most, while aggressive investors weight Momentum most.

**Why Expert 2 is excluded:** Expert 2 answered "7" on all 18 questions and picked the same winner in
every profile, so the answers don't separate the profiles and contradict themselves (CR = 0.38, far above 0.10).
The group geometric mean is shown in `results/factor_weights.csv` for reference only, because it is
valid only when every expert is individually consistent.

## Files

| Path | What it is |
|---|---|
| `ahp.py` | Reproduces every weight and consistency figure from the raw survey answers |
| `data/judgments.csv` | The 36 pairwise judgments (2 experts × 3 profiles × 6 pairs) |
| `results/factor_weights.csv` | Output: weights, λmax, CI, CR for each expert/profile |
| `excel/AHP_Factor_Weights_SET.xlsx` | Original Excel workbook with the step-by-step calculation |

## Run it

```bash
pip install numpy pandas
python ahp.py
```

## Limitations

- Only two expert responses were collected, and one failed the consistency test.
  More experts are needed before these weights are treated as robust.
- Each factor uses a single proxy (for example, ROE for Growth). Other proxies could change the ranking.

Educational data science project, not investment advice.
