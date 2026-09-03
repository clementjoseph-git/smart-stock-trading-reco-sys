
---

## 📂 `docs/prompts/portfolio.md`

```markdown
# Portfolio Prompt

## Input
- Expected returns array
- Covariance matrix

## Processing
- Portfolio optimization (Mean‑Variance, MPT).
- Compute weights, expected return, risk.

## Output
```json
{
  "weights": [float, float, ...],
  "expected_return": float,
  "risk": float
}
